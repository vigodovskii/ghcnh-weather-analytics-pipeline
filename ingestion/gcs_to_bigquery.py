import io
import os
import numpy as np
import pandas as pd
from google.cloud import storage, bigquery

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "terraform-demo-488900")
BUCKET_NAME = os.environ["BUCKET_NAME"]
DATASET_ID = os.getenv("DATASET_ID", "weather_warehouse")
TABLE_ID = os.getenv("TABLE_ID", "weather_analytics")
YEAR = os.getenv("YEAR", "2025")
FILE_LIMIT = int(os.getenv("FILE_LIMIT", "1"))
ROW_LIMIT = int(os.getenv("ROW_LIMIT", "100"))

EXPECTED_COLUMNS = [
    "station", "date", "source", "latitude", "longitude", "elevation",
    "name", "report_type", "call_sign", "quality_control", "wnd", "cig",
    "vis", "tmp", "dew", "slp", "ga1", "ga2", "ga3", "ge1", "gf1",
    "ma1", "mw1", "mw2", "mw3", "oc1", "rem", "eqd"
]

FINAL_COLUMNS = [
    "station",
    "observation_timestamp",
    "observation_date",
    "source",
    "latitude",
    "longitude",
    "elevation",
    "name",
    "report_type",
    "quality_control",
    "tmp",
    "dew",
    "slp"
]


def transform_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [col.lower() for col in df.columns]

    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = None

    df["name"] = df["name"].astype(str).str.strip().str.title()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["source"] = pd.to_numeric(df["source"], errors="coerce")
    df["station"] = pd.to_numeric(df["station"], errors="coerce")

    for col in ["latitude", "longitude", "elevation"]:
        df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce")

    placeholders = ["9999", "+9999", "99999", "+99999", "9999,9", "99999,9", "+9999,9"]
    for col in ["tmp", "dew", "slp"]:
        df[col] = df[col].replace(placeholders, np.nan)
        df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
        df[col] = pd.to_numeric(
            df[col].str.extract(r"([+-]?\d+\.?\d*)")[0],
            errors="coerce"
        ) / 10

    df["observation_timestamp"] = df["date"]
    df["observation_date"] = pd.to_datetime(df["date"], errors="coerce").dt.date

    return df[FINAL_COLUMNS]


def load_from_gcs():
    storage_client = storage.Client(project=PROJECT_ID)
    bq_client = bigquery.Client(project=PROJECT_ID)

    blobs = list(storage_client.list_blobs(BUCKET_NAME, prefix=f"raw/{YEAR}/"))
    csv_blobs = [blob for blob in blobs if blob.name.endswith(".csv")][:FILE_LIMIT]

    if not csv_blobs:
        raise RuntimeError(f"No CSV files found in gs://{BUCKET_NAME}/raw/{YEAR}/")

    frames = []

    for blob in csv_blobs:
        print(f"Reading {blob.name}")
        data = blob.download_as_bytes()
        df = pd.read_csv(io.BytesIO(data), dtype=str, low_memory=False)

        if ROW_LIMIT > 0:
            df = df.head(ROW_LIMIT)

        frames.append(transform_dataframe(df))

    final_df = pd.concat(frames, ignore_index=True)

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    print(f"Loading {len(final_df)} rows into {table_ref}")

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="observation_date"
        ),
        clustering_fields=["station", "name"]
    )

    load_job = bq_client.load_table_from_dataframe(final_df, table_ref, job_config=job_config)
    load_job.result()

    query = f"SELECT COUNT(*) AS row_count FROM `{table_ref}`"
    result = list(bq_client.query(query).result())
    row_count = result[0].row_count if result else 0

    print(f"BigQuery row count: {row_count}")

    if row_count == 0:
        raise RuntimeError("Validation failed: table is empty")

    print("BigQuery load completed successfully.")


if __name__ == "__main__":
    load_from_gcs()

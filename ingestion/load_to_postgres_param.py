import pandas as pd
import os
from sqlalchemy import create_engine, text
import numpy as np

YEAR = os.getenv("YEAR", "2025")
DATA_DIR = os.getenv("DATA_DIR", f"data/raw/{YEAR}")
ROW_LIMIT = int(os.getenv("ROW_LIMIT", "100"))
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@postgres:5432/weather"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# List of expected columns for the PostgreSQL table (all lowercase)
expected_columns = [
    'station', 'date', 'source', 'latitude', 'longitude', 'elevation',
    'name', 'report_type', 'call_sign', 'quality_control', 'wnd', 'cig',
    'vis', 'tmp', 'dew', 'slp', 'ga1', 'ga2', 'ga3', 'ge1', 'gf1',
    'ma1', 'mw1', 'mw2', 'mw3', 'oc1', 'rem', 'eqd'
]

# SQL statement to create the table if it doesn't exist
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS weather_data (
    station BIGINT,
    date TIMESTAMP,
    source INT,
    latitude FLOAT,
    longitude FLOAT,
    elevation FLOAT,
    name TEXT,
    report_type TEXT,
    call_sign INT,
    quality_control TEXT,
    wnd TEXT,
    cig TEXT,
    vis TEXT,
    tmp FLOAT,
    dew FLOAT,
    slp FLOAT,
    ga1 TEXT,
    ga2 TEXT,
    ga3 TEXT,
    ge1 TEXT,
    gf1 TEXT,
    ma1 TEXT,
    mw1 TEXT,
    mw2 TEXT,
    mw3 TEXT,
    oc1 TEXT,
    rem TEXT,
    eqd TEXT
);
"""

# Create table if it doesn't exist
with engine.connect() as conn:
    conn.execute(text(create_table_sql))
    conn.commit()

if not os.path.exists(DATA_DIR):
    raise FileNotFoundError(f"Data directory does not exist: {DATA_DIR}")

# Loop through all CSV files in the directory and do transformations
for file in os.listdir(DATA_DIR):
    if file.endswith(".csv"):
        path = os.path.join(DATA_DIR, file)

        # Load CSV into a DataFrame
        df = pd.read_csv(path, dtype=str, low_memory=False)

        if ROW_LIMIT > 0:
            df = df.head(ROW_LIMIT)

        # Convert all column names to lowercase
        df.columns = [col.lower() for col in df.columns]

        # Fill missing expected columns with None
        for col in expected_columns:
            if col not in df.columns:
                df[col] = None

        # Normalize station names
        df['name'] = df['name'].astype(str).str.strip().str.title()

        # Convert columns to numeric types
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['source'] = pd.to_numeric(df['source'], errors='coerce')
        df['call_sign'] = pd.to_numeric(df['call_sign'], errors='coerce')
        df['station'] = pd.to_numeric(df['station'], errors='coerce')

        # Latitude, longitude, elevation: numeric, handle commas
        for col in ['latitude', 'longitude', 'elevation']:
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Replace placeholders and convert temperatures + slp
        placeholders = ['9999', '+9999', '99999', '+99999', '9999,9', '99999,9', '+9999,9']
        for col in ['tmp', 'dew', 'slp']:
            df[col] = df[col].replace(placeholders, np.nan)
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col].str.extract(r'([+-]?\d+\.?\d*)')[0], errors='coerce') / 10

        # Keep only expected columns
        df = df[expected_columns]

        # Dynamically add missing columns in PostgreSQL table
        with engine.connect() as conn:
            existing_cols = [row[0] for row in conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='weather_data';"
            ))]
            for col in expected_columns:
                if col not in existing_cols:
                    conn.execute(text(f'ALTER TABLE weather_data ADD COLUMN {col} TEXT;'))
            conn.commit()

        print(f"Loading file: {file} with columns: {df.columns.tolist()}")

        # Load DataFrame into PostgreSQL
        df.to_sql("weather_data", engine, if_exists="append", index=False)

print("All CSV files loaded into PostgreSQL!")
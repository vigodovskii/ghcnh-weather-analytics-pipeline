# ghcnh-weather-analytics-pipeline

End-to-end batch data engineering pipeline for NOAA Global Hourly weather station data.

---

## Project Goal

This project builds a reproducible batch pipeline that ingests raw weather observations,
stores them locally and in the cloud, applies transformations, and serves curated datasets
for downstream analytics and future flight delay analysis.

---

## Dataset

**Source:** NOAA / NCEI Global Hourly Weather Station Data

The dataset contains hourly weather observations from stations around the world, including
temperature, dew point, sea-level pressure, latitude, longitude, elevation, and other
weather-related attributes.

---

## Use Case

The target user is a climate, weather, or operations analyst who needs clean and structured
hourly weather data for downstream analysis.

Typical use cases include:

- Analyzing temperature and pressure patterns across stations and time
- Comparing weather conditions across locations
- Preparing analytical features for future flight delay analysis
- Storing weather observations in queryable local and cloud environments

---

## Stack

| Layer | Tool |
|---|---|
| Ingestion | Python |
| Local storage | PostgreSQL + pgAdmin |
| Containerization | Docker Compose |
| Orchestration | Kestra |
| Infrastructure as Code | Terraform |
| Data Lake | Google Cloud Storage |
| Data Warehouse | BigQuery |

---

## Architecture

```
NOAA NCEI Global Hourly Dataset
        │
        ├── Midterm (Local Pipeline)
        │   ├── Batch download with Python
        │   ├── Raw local storage
        │   ├── Transformation
        │   └── PostgreSQL (weather_data)
        │
        └── Final (Cloud Pipeline)
            ├── Terraform provisions:
            │   ├── GCS bucket
            │   └── BigQuery dataset
            ├── Kestra flow: NOAA → GCS
            └── Kestra flow: GCS → BigQuery
```

---

## Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd ghcnh-weather-analytics-pipeline
```

### 2. Start Docker containers

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

> For the final cloud pipeline, you also need:
> - a valid `credentials/service_account.json`
> - a local `terraform/terraform.tfvars`

### 3. Verify services are running

```bash
docker compose -f docker/docker-compose.yml ps
```

### 4. Open Kestra

| | |
|---|---|
| URL | http://localhost:8080/ui/ |
| Username | `admin@kestra.io` |
| Password | `Admin1234` |

### 5. Configure pgAdmin

| | |
|---|---|
| URL | http://localhost:8081 |
| Email | `admin@admin.com` |
| Password | `admin` |

Add a new server with these connection details:

| Field | Value |
|---|---|
| Host | `postgres` |
| Port | `5432` |
| Database | `weather` |
| Username | `postgres` |
| Password | `postgres` |

---

## Midterm: Local Pipeline

The midterm pipeline downloads NOAA weather data and loads it into local PostgreSQL.

### Flow

| | |
|---|---|
| Namespace | `weather.midterm` |
| Flow | `weather_local_ingestion` |

### What it does

1. Downloads NOAA weather CSV files in batch mode
2. Stores raw files locally
3. Applies data transformation logic
4. Loads transformed data into PostgreSQL
5. Validates that rows were inserted successfully

### Running the flow

In the Kestra UI, use these recommended test inputs to start small:

| Input | Value |
|---|---|
| `year` | `2025` |
| `file_limit` | `1` |
| `row_limit` | `10` |

### Verifying local data

Check row count:

```bash
docker exec -it weather_postgres psql -U postgres -d weather \
  -c "SELECT COUNT(*) FROM weather_data;"
```

Inspect sample rows:

```bash
docker exec -it weather_postgres psql -U postgres -d weather \
  -c "SELECT station, date, name, tmp, dew, slp FROM weather_data LIMIT 5;"
```

---

## Final: Cloud Pipeline

The final stage extends the project from local storage to Google Cloud.

### Prerequisite: Google Cloud Setup

Before running the final cloud pipeline, you must create a Google Cloud project in Google Cloud Platform.

### GCP Credentials

Place your Google Cloud service account key at:

```
credentials/service_account.json
```

> This file is gitignored and must never be committed.

> **Note:** The `bucket_name` and `project_id` values you use in the flows below are the same ones you set in `terraform.tfvars`.

---

### Terraform Infrastructure

Terraform provisions:

- A Google Cloud Storage bucket (data lake)
- A BigQuery dataset (data warehouse)

**Files:** `terraform/`
```bash
cd terraform
```

Create a local `terraform.tfvars` file (this file is gitignored and must not be committed):

```hcl
project_id  = "your-gcp-project-id"
region      = "europe-west6"
bucket_name = "your-unique-bucket-name"
dataset_id  = "weather_warehouse"
```

Run:

```bash
terraform init
terraform plan
terraform apply
```

### Final Flow 1: NOAA → GCS

| | |
|---|---|
| Namespace | `weather.final` |
| Flow | `weather_gcs_ingestion` |

**What it does:**

1. Downloads NOAA weather data in batch mode
2. Uploads raw CSV files to Google Cloud Storage
3. Validates that files exist in the bucket

**Recommended test inputs:**

| Input | Value |
|---|---|
| `year` | `2025` |
| `file_limit` | `1` |
| `max_workers` | `2` |
| `bucket_name` | your bucket name |

**Expected result:** Files appear in the bucket under `raw/2025/`, for example:

```
raw/2025/01001099999.csv
```

---

### Final Flow 2: GCS → BigQuery

| | |
|---|---|
| Namespace | `weather.final` |
| Flow | `weather_bq_transform` |

**What it does:**

1. Reads raw CSV files from GCS
2. Applies transformation logic in Python
3. Loads curated weather data into BigQuery
4. Validates that the analytics table contains rows

**Recommended test inputs:**

| Input | Value | Note |
|---|---|---|
| `year` | `2025` | |
| `file_limit` | `1` | Number of GCS files to process |
| `row_limit` | `100` | Rows per file — set to `0` for full load |
| `bucket_name` | your bucket name | Same value as in `terraform.tfvars` |
| `dataset_id` | `weather_warehouse` | |
| `table_id` | `weather_analytics` | |
| `project_id` | your GCP project ID | Same value as in `terraform.tfvars` |

**Expected result:** A BigQuery table is created at:

```
<project_id>.weather_warehouse.weather_analytics
```

---

## Data Transformation

The pipeline includes a transformation step applied before loading into both PostgreSQL and BigQuery.

### Transformations applied

| Transformation | Why |
|---|---|
| Column names → lowercase | Consistent SQL access across tools |
| Station names → Title Case | Human-readable for dashboards |
| Timestamp parsing | Enables time-range queries |
| Lat / lon / elevation → numeric | Geospatial filtering |
| Placeholder replacement (`9999`, `+9999` → `NULL`) | Prevents skewed aggregations |
| Temperature / pressure ÷ 10 | NOAA stores values as tenths of their unit |

### Why it is necessary

Raw NOAA files contain placeholder values, mixed formats, and raw string-based weather
fields that are not directly usable for analysis.

### How it supports the use case

The transformed data becomes queryable and suitable for downstream analytics, comparisons
across stations, and future feature engineering for weather-based operational analysis.

---

## BigQuery Design

| | |
|---|---|
| Dataset | `weather_warehouse` |
| Table | `weather_analytics` |
| Partitioned by | `observation_date` |
| Clustered by | `station`, `name` |

**Why:**

- Partitioning reduces bytes scanned for time-based queries
- Clustering improves performance for station-level filtering and aggregation

---

## Repository Structure

```
.
├── credentials/                    # GCP service account key (gitignored)
├── data/raw/2025/                  # Downloaded NOAA CSVs (gitignored)
├── docker/
│   ├── docker-compose.yml          # PostgreSQL + pgAdmin + Kestra
│   ├── Dockerfile.ingestion
│   └── Dockerfile.kestra
├── docs/
│   └── midterm_orchestration_plan.md
├── ingestion/
│   ├── download_weather_2025.py
│   ├── download_weather_param.py
│   ├── load_to_postgres.py
│   ├── load_to_postgres_param.py
│   ├── noaa_to_gcs.py
│   └── gcs_to_bigquery.py
├── orchestration/kestra/
│   ├── README.md
│   └── flows/
│       ├── main_weather.midterm.weather_local_ingestion.yml
│       ├── main_weather.final.weather_gcs_ingestion.yml
│       └── main_weather.final.weather_bq_transform.yml
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── provider.tf
│   ├── terraform.tfvars.example
│   └── .gitignore
├── tests/
├── requirements.txt
└── README.md
```

---

## Verification

### Local

- [ ] PostgreSQL contains rows in `weather_data`
- [ ] pgAdmin can query the local table
- [ ] Kestra execution for `weather_local_ingestion` completes successfully

### Cloud

- [ ] GCS bucket contains files under `raw/2025/`
- [ ] BigQuery dataset `weather_warehouse` exists
- [ ] BigQuery table `weather_analytics` exists and contains rows
- [ ] Kestra execution for `weather_gcs_ingestion` completes successfully
- [ ] Kestra execution for `weather_bq_transform` completes successfully

---

## Status

### Midterm

- [x] Dataset and Use Case
- [x] Ingestion Pipeline
- [x] Local Storage (PostgreSQL + pgAdmin)
- [x] Dockerized Environment
- [x] Data Transformation
- [x] Workflow Orchestration (Kestra)

### Final

- [x] Infrastructure as Code (Terraform) — GCS bucket + BigQuery dataset
- [x] Data Lake ingestion pipeline (NOAA → GCS, orchestrated)
- [x] Data Warehouse transformation pipeline (GCS → BigQuery, partitioned + clustered)
- [x] Repository documentation

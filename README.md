# ghcnh-weather-analytics-pipeline
End-to-end batch data engineering pipeline for NOAA global hourly weather station data.

## Project Goal
This project builds a reproducible batch pipeline that ingests raw weather observations, stores them locally and in the cloud, applies transformations, and serves curated analytics tables for downstream analysis.

## Dataset
NOAA / NCEI global hourly weather station data.

## Use Case
The target user is a climate or weather analyst who wants to analyze temperature, precipitation, wind, and pressure patterns across stations, countries, and time.

## Planned Stack
- Python
- PostgreSQL
- pgAdmin
- Docker Compose
- Kestra
- Terraform
- Google Cloud Storage
- BigQuery

## Quick Start
1. Clone the repository

2. Start Docker containers:
   ```bash
   docker compose -f docker/docker-compose.yml down
   rm -f data/database.mv.db data/database.trace.db
   docker compose -f docker/docker-compose.yml up -d --build
   ```

3. Check that the services are running:
   ```bash
   docker compose -f docker/docker-compose.yml ps
   ```

4. Open Kestra:
   - URL: `http://localhost:8080/ui/`
   - Username: `admin@kestra.io`
   - Password: `Admin1234`

5. Run the orchestration flow in Kestra:
   - Namespace: `weather.midterm`
   - Flow: `weather_local_ingestion`
   - Example input values:
     - `year = 2025`
     - `file_limit = 1`
     - `row_limit = 10`

6. Configure pgAdmin:
   - URL: `http://localhost:8081`
   - Email: `admin@admin.com`
   - Password: `admin`

   Create a new server with:
   - Host: `postgres`
   - Port: `5432`
   - Database: `weather`
   - Username: `postgres`
   - Password: `postgres`

7. Verify the data:
   
   From the terminal:
   ```bash
   docker exec -it weather_postgres psql -U postgres -d weather -c "SELECT COUNT(*) FROM weather_data;"
   ```
   
   Example:
   ```bash
   docker exec -it weather_postgres psql -U postgres -d weather -c "SELECT station, date, name, tmp, dew, slp FROM weather_data LIMIT 5;"
   ```

   Or using the **pgAdmin Query Tool**:
   ```sql
   SELECT COUNT(*) FROM weather_data;
   ```

   Example:
   ```sql
   SELECT station, date, name, tmp, dew, slp
   FROM weather_data
   LIMIT 5;
   ```


## Workflow Orchestration

This project uses **Kestra** as the workflow orchestrator for the midterm stage.

Implemented flow:
- Namespace: `weather.midterm`
- Flow: `weather_local_ingestion`

The flow performs:
1. batch download of NOAA weather files
2. loading transformed data into local PostgreSQL
3. validation that rows were inserted successfully

The flow supports:
- manual execution
- scheduled execution
- future runs
- missed schedule recovery / backfill behavior


## Data Transformation

The pipeline includes a transformation step before loading data into PostgreSQL.

Current transformations:
- convert column names to lowercase
- normalize station names
- parse timestamps
- convert latitude, longitude, and elevation to numeric values
- replace placeholder values in weather fields such as `tmp`, `dew`, and `slp`
- standardize selected raw weather values for querying

Why this transformation is necessary:
The raw NOAA files contain placeholder values, mixed formats, and raw string-based measurements that are not directly suitable for analysis.

How it supports the use case:
The target analyst needs structured and queryable weather observations across stations and time. These transformations make the data usable for filtering, comparison, and downstream analytics.

What problem it solves:
It converts raw operational weather files into a consistent local analytical dataset.



## Status

### Midterm
- Dataset and Use Case ✓
- Ingestion Pipeline ✓
- Local Storage ✓
- Docker Compose ✓
- Data Transformation ✓
- Workflow Orchestration with Kestra ✓

### Final Stage
- GCS data lake planned
- BigQuery warehouse planned
- Terraform planned

## Repository Structure
- `ingestion/`
- `orchestration/`
- `terraform/`
- `docs/`
- `tests/`

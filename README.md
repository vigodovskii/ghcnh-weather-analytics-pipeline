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
- Airflow or Kestra
- Terraform
- Google Cloud Storage
- BigQuery

## Quick Start
1. Clone the repository
2. Start Docker containers:
   - First, remove any old containers and volumes (clean start): docker compose -f docker/docker-compose.yml down -v
   - Build and start the containers: docker compose -f docker/docker-compose.yml up --build -d
   - The ingestion container will automatically:
        1. Run ingestion/download_weather_2025.py to download the NOAA CSV files.
        2. Run ingestion/load_to_postgres.py to load the data into PostgreSQL with transformations applied (placeholder values, numeric conversions, and normalized station names).
3. Configure PgAdmin:
   - Open your browser: http://localhost:8081
   - Login using: Email: admin@admin.com, Password: admin
   - Create a new Server: Name: weather_postgres, Hostname / IP:  postgres, Port: 5432, Maintenance DB: weather, Username: postgres, Password: postgres
4. Verify the data:
   - In PgAdmin, select the database "weather", right-click on the weather database and choose query tool. Run: SELECT * FROM weather_data LIMIT 10;
   - You should see the first rows of your ingested weather data.






## Planned Pipeline until midterm
1. Download raw weather files in batch from the NOAA dataset
2. Store raw data locally
3. Load raw data into staging tables in PostgreSQL
4. Transform raw observations into analytics-ready tables
5. Schedule the ingestion and transformation pipeline using a workflow orchestrator 

## Planned Pipeline after midterm
1. Upload raw and transformed data to Google Cloud Storage (GCS)
2. Load curated data from GCS into BigQuery for analytics
3. Provision cloud infrastructure using Terraform
4. Extend the workflow orchestrator to run the full cloud pipeline

## Repository Structure
- `ingestion/`
- `transformations/`
- `orchestration/`
- `terraform/`
- `postgres/`
- `docs/`
- `tests/`

## Status
- Ingestion Pipeline ✓
- Local Storage ✓
- Docker ✓
- Data Transformation ✓
- Workflow Orchestration


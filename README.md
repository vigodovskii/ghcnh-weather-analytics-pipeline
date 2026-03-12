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

## Planned Pipeline
1. Download raw weather files in batch
2. Store raw data locally
3. Load staging data into PostgreSQL
4. Transform raw observations into analytics-ready tables
5. Upload raw/curated data to GCS
6. Load transformed data into BigQuery
7. Schedule workflows with an orchestrator

## Repository Structure
- `ingestion/`
- `transformations/`
- `orchestration/`
- `terraform/`
- `postgres/`
- `docs/`
- `tests/`

## Status
Project setup phase.

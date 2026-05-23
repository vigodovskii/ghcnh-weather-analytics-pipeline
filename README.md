# ghcnh-weather-analytics-pipeline
End-to-end batch data engineering pipeline for preparing weather data to support flight delay analysis and prediction.

## Project Goal
The goal of this project is to process raw weather data and transform it into a clean and structured format.
This prepared data can then be used for analysis and machine learning models to help predict flight delays.

## Dataset
We use the NOAA / NCEI Global Hourly Weather Dataset (2025).

This dataset contains hourly weather observations from stations all around the world.
Because the full dataset is very large, we limited our project to the first 1000 files.

Each file includes weather data collected at specific weather stations over time.

## Use Case
The main user of this pipeline is an airline data analyst who needs reliable weather data for analysis. Raw weather data is often large and unstructured, making it difficult to use directly. This pipeline cleans and organizes the data so it can support analytics and machine learning models for predicting flight delays.

## Planned Stack
- Python
- PostgreSQL
- pgAdmin
- Docker Compose
- Kestra
- Terraform
- Google Cloud Storage
- BigQuery

## Quick Start Midterm
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


## Quick Start Final 
1. Install required tools:
   - Terraform
   - Google Cloud CLI
  
2. Create a Google Cloud Project:
   - Go to the Google Cloud Console: https://console.cloud.google.com/
   - Create a new project ("ghcnh-weather-pipeline")
   - Enable billing for the project

3. Authenticate with Google Cloud:
   ```bash
   gcloud auth application-default login
   ```

   ## Troubleshooting
   If the following Terraform authentication error appears:

   ```text
   Error: Attempted to load application default credentials since neither `credentials` nor `access_token` was set in the provider block.
   google: error getting credentials using GOOGLE_APPLICATION_CREDENTIALS environment variable
   ```
   
   remove the environment variable:
   ```bash
   Remove-Item Env:GOOGLE_APPLICATION_CREDENTIALS
   ```

   Then authenticate again with:
   ```bash
   gcloud auth application-default login
   ```
   

5. Navigate to Terraform directory:
   ```bash
   cd terraform
   ```

6. Initialize Terraform:
   ```bash
   terraform init
   ```

7. Create Terraform variables file:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

8. Update the variables in terraform.tfvars:
   ```hcl
   project_id  = "your-project-id"
   region      = "europe-west6"
   bucket_name = "your-bucket-name"
   dataset_id  = "your_dataset"
   ```
   We used:
   - bucket_name = "ghcnh-weather-data-lake"
   - dataset_id  = "weather_warehouse"

9. Preview Infrastracture changes:
   ```bash
   terraform plan
   ```

10. Apply infrastructure:
   ```bash
   terraform apply
   ```
11. confirm deployment

12. Verify Cloud Resources in Google Cloud Console
    - In the Google Cloud Console, check that the Cloud Storage bucket has been created and is visible in the selected project.
    - Also verify that the BigQuery dataset exists and is correctly displayed in the project.



## Status

### Midterm
- Dataset and Use Case ✓
- Ingestion Pipeline ✓
- Local Storage ✓
- Docker Compose ✓
- Data Transformation ✓
- Workflow Orchestration with Kestra ✓

### Final Stage
- Infrastructure as code (Terraform) ✓
- GCS data lake Ingestion Pipeline
- BigQuery warehouse Transformation Pipeline

## Repository Structure
- `ingestion/`
- `orchestration/`
- `terraform/`
- `docs/`
- `tests/`

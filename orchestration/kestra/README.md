# Midterm Orchestration

This folder contains the workflow orchestration setup for the midterm stage of the project.

## Goal
Run the batch pipeline from the NOAA data source into local PostgreSQL storage.

## Planned orchestration requirements
- scheduled batch runs
- manual triggering
- backfill support
- future runs

## Planned workflow
1. Download NOAA weather data
2. Load processed records into local PostgreSQL
3. Validate that data was loaded successfully
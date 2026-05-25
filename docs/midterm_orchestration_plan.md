# Midterm Orchestration Plan

## Requirement
For the midterm, the orchestration tool must run the workflow from the source into local storage.

## Current gap
The ingestion pipeline currently runs directly from Docker Compose and is not yet managed by an orchestration tool.

## Planned solution
We will add Kestra as the orchestration layer for the midterm.

## Planned workflow steps
1. Download batch weather data from NOAA
2. Load the data into local PostgreSQL
3. Run a simple validation query

## Required orchestration features
- scheduling
- backfills
- future runs
- manual execution for testing
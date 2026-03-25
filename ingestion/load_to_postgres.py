import pandas as pd
import os
from sqlalchemy import create_engine, text

# Directory where the raw NOAA CSV files are stored
DATA_DIR = "data/raw/2025"

# Create SQLAlchemy engine
engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/weather")

# List of expected columns for the PostgreSQL table
expected_columns = [
    'STATION', 'DATE', 'SOURCE', 'LATITUDE', 'LONGITUDE', 'ELEVATION',
    'NAME', 'REPORT_TYPE', 'CALL_SIGN', 'QUALITY_CONTROL', 'WND', 'CIG',
    'VIS', 'TMP', 'DEW', 'SLP', 'GA1', 'GA2', 'GA3', 'GE1', 'GF1',
    'MA1', 'MW1', 'MW2', 'MW3', 'OC1', 'REM', 'EQD'
]

# SQL statement to create the table if it doesn't exist
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS weather_data (
    STATION BIGINT,
    DATE TIMESTAMP,
    SOURCE INT,
    LATITUDE FLOAT,
    LONGITUDE FLOAT,
    ELEVATION FLOAT,
    NAME TEXT,
    REPORT_TYPE TEXT,
    CALL_SIGN INT,
    QUALITY_CONTROL TEXT,
    WND TEXT,
    CIG TEXT,
    VIS TEXT,
    TMP TEXT,
    DEW TEXT,
    SLP TEXT,
    GA1 TEXT,
    GA2 TEXT,
    GA3 TEXT,
    GE1 TEXT,
    GF1 TEXT,
    MA1 TEXT,
    MW1 TEXT,
    MW2 TEXT,
    MW3 TEXT,
    OC1 TEXT,
    REM TEXT,
    EQD TEXT
);
"""

# Create table if it doesn't exist
with engine.connect() as conn:
    conn.execute(text(create_table_sql))
    conn.commit()

# Loop through all CSV files in the directory
for file in os.listdir(DATA_DIR):
    if file.endswith(".csv"):
        path = os.path.join(DATA_DIR, file)
        
        # Load CSV into a DataFrame
        df = pd.read_csv(path)
        
        # Take only the first 100 rows for testing
        df = df.head(100)

        # Fill missing expected columns with None
        for col in expected_columns:
            if col not in df.columns:
                df[col] = None

        # Keep only expected columns in the correct order
        df = df[expected_columns]

        # Dynamically add missing columns in the table
        with engine.connect() as conn:
            existing_cols = [row[0] for row in conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='weather_data';"
            ))]
            for col in expected_columns:
                if col.lower() not in [c.lower() for c in existing_cols]:
                    # Add missing column as TEXT by default
                    conn.execute(text(f'ALTER TABLE weather_data ADD COLUMN "{col}" TEXT;'))
            conn.commit()

        print(f"Loading file: {file} with columns: {df.columns.tolist()}")

        # Load DataFrame into PostgreSQL
        df.to_sql("weather_data", engine, if_exists="append", index=False)

print("All CSV files loaded into PostgreSQL!")
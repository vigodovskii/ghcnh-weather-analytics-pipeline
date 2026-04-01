import requests
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

YEAR = os.getenv("YEAR", "2025")
FILE_LIMIT = int(os.getenv("FILE_LIMIT", "1000"))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "50"))

# Base URL for NOAA Global Hourly Dataset
BASE_URL = f"https://www.ncei.noaa.gov/data/global-hourly/access/{YEAR}/"

# Local directory to save the raw CSV files
OUTPUT_DIR = os.getenv("OUTPUT_DIR", f"data/raw/{YEAR}")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the HTML page containing the list of files
response = requests.get(BASE_URL)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

# Find all <a> tags (links) on the page
links = soup.find_all("a")

# Filter links that end with '.csv'
csv_files = [link.get("href") for link in links if link.get("href") and link.get("href").endswith(".csv")]

print(f"{len(csv_files)} files found for year {YEAR}")

# Limit to the first N CSV files if FILE_LIMIT > 0
if FILE_LIMIT > 0:
    csv_files = csv_files[:FILE_LIMIT]

print(f"Processing {len(csv_files)} files")

def download_file(file):
    file_url = BASE_URL + file
    file_path = os.path.join(OUTPUT_DIR, file)

    if os.path.exists(file_path):
        return f"Skipped {file}"

    try:
        r = requests.get(file_url, timeout=120)
        r.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(r.content)
        return f"Downloaded {file}"
    except Exception as e:
        return f"Failed {file}: {e}"

# Parallel download
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(download_file, file) for file in csv_files]
    for future in as_completed(futures):
        print(future.result())
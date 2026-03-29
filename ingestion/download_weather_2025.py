import requests
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Base URL for NOAA Global Hourly Dataset 2025
BASE_URL = "https://www.ncei.noaa.gov/data/global-hourly/access/2025/"

# Local directory to save the raw CSV files
OUTPUT_DIR = "data/raw/2025"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the HTML page containing the list of files
response = requests.get(BASE_URL)
soup = BeautifulSoup(response.text, "html.parser")

# Find all <a> tags (links) on the page
links = soup.find_all("a")

# Filter links that end with '.csv'
csv_files = [link.get("href") for link in links if link.get("href").endswith(".csv")]

print(f"{len(csv_files)} files found")

# Limit to the first 1000 CSV files
csv_files = csv_files[:1000]

def download_file(file):
    file_url = BASE_URL + file
    file_path = os.path.join(OUTPUT_DIR, file)
    
    if os.path.exists(file_path):
        return f"Skipped {file}"
    
    try:
        r = requests.get(file_url)
        r.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(r.content)
        return f"Downloaded {file}"
    except Exception as e:
        return f"Failed {file}: {e}"

# Parallel download with 50 Threads 
with ThreadPoolExecutor(max_workers=50) as executor:
    futures = [executor.submit(download_file, file) for file in csv_files]
    for future in as_completed(futures):
        print(future.result())
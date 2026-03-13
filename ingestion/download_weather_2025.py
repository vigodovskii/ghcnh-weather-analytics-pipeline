import requests
from bs4 import BeautifulSoup
import os

# Base URL for NOAA Global Hourly Dataset 2025
BASE_URL = "https://www.ncei.noaa.gov/data/global-hourly/access/2025/"

# Local directory to save the raw CSV files
OUTPUT_DIR = "../data/raw/2025"

# Make sure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the HTML page containing the list of files
response = requests.get(BASE_URL)
soup = BeautifulSoup(response.text, "html.parser")

# Find all <a> tags (links) on the page
links = soup.find_all("a")

# Filter links that end with '.csv'
csv_files = [link.get("href") for link in links if link.get("href").endswith(".csv")]

print(f"{len(csv_files)} files found")

# Limit to the first 500 CSV files (instead of 12'000+)
for file in csv_files[:500]:
    file_url = BASE_URL + file
    file_path = os.path.join(OUTPUT_DIR, file)

    # Skip file if it already exists locally
    if os.path.exists(file_path):
        continue

    # Download the CSV content
    r = requests.get(file_url)

    # Save the CSV file locally
    with open(file_path, "wb") as f:
        f.write(r.content)

    print(f"Downloaded {file}")
import requests
import time
from bs4 import BeautifulSoup
from google.cloud import storage
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Base URL for NOAA Global Hourly Dataset 2025
BASE_URL = "https://www.ncei.noaa.gov/data/global-hourly/access/2025/"

# GCS bucket name
BUCKET_NAME = "ghcnh-weather-data-lake"

# Shared requests session with connection pooling and retry logic
session = requests.Session()

retry = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504]
)

adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=retry)
session.mount("https://", adapter)

headers = {"Connection": "keep-alive"}


def get_csv_files(limit=1000):
    """Scrape the NOAA directory page and return a list of CSV filenames."""
    response = session.get(BASE_URL, timeout=30, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    csv_files = [
        link.get("href")
        for link in soup.find_all("a")
        if link.get("href") and link.get("href").endswith(".csv")
    ][:limit] 

    print(f"{len(csv_files)} files found")
    return csv_files


def process_file(file_name):
    """
    Download a single CSV from NOAA and upload it to GCS.
    """
    # Create a GCS client local to this thread 
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    file_url = BASE_URL + file_name

    try:
        # Download full file into memory
        r = session.get(file_url, timeout=60, headers=headers)

        if r.status_code == 200:
            blob = bucket.blob(f"raw/2025/{file_name}")

            # upload_from_string knows content-length → GCS uses fast multipart upload
            blob.upload_from_string(
                r.content,
                content_type="text/csv",
            )
            print(f"✓ {file_name}")

        else:
            print(f"✗ {file_name}: HTTP {r.status_code}")

    except Exception as e:
        print(f"✗ {file_name}: {e}")


def run_pipeline(files, max_workers=8):
    """
    Upload all files in parallel using a thread pool.
    """
    print(f"\nStarting upload: {len(files)} files | {max_workers} workers\n")
    start = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(process_file, files))

    elapsed = time.time() - start
    print(f"\nDone — {len(files)} files in {elapsed:.1f}s ({elapsed/len(files):.1f}s per file)")


# Main
csv_files = get_csv_files()

csv_files = csv_files[:1000]

run_pipeline(csv_files)

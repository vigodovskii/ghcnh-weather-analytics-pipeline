import os
import time
import requests
from bs4 import BeautifulSoup
from google.cloud import storage
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

YEAR        = os.environ.get("YEAR", "2025")
FILE_LIMIT  = int(os.environ.get("FILE_LIMIT", "1000"))
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", "8"))
BUCKET_NAME = os.environ["BUCKET_NAME"]

BASE_URL = f"https://www.ncei.noaa.gov/data/global-hourly/access/{YEAR}/"

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=retry)
session.mount("https://", adapter)
headers = {"Connection": "keep-alive"}


def get_csv_files(limit):
    response = session.get(BASE_URL, timeout=30, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    csv_files = [
        link.get("href")
        for link in soup.find_all("a")
        if link.get("href") and link.get("href").endswith(".csv")
    ][:limit]
    print(f"{len(csv_files)} files found")
    return csv_files


def process_file(file_name):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    file_url = BASE_URL + file_name
    try:
        r = session.get(file_url, timeout=60, headers=headers)
        if r.status_code == 200:
            blob = bucket.blob(f"raw/{YEAR}/{file_name}")
            blob.upload_from_string(r.content, content_type="text/csv")
            print(f"Uploaded {file_name}")
        else:
            print(f"Failed {file_name}: HTTP {r.status_code}")
    except Exception as e:
        print(f"Failed {file_name}: {e}")


def run_pipeline(files, max_workers):
    print(f"\nStarting upload: {len(files)} files | {max_workers} workers\n")
    start = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(process_file, files))
    elapsed = time.time() - start
    print(f"\nDone — {len(files)} files in {elapsed:.1f}s")


csv_files = get_csv_files(FILE_LIMIT)
run_pipeline(csv_files, MAX_WORKERS)

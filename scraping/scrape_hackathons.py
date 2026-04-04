import json
import logging
from pathlib import Path
import requests
from tqdm import tqdm
import pandas as pd

BASE_URL = "https://devpost.com/api/hackathons?status[]=ended&order_by=deadline"
TOTAL_HACKATHONS = 12509
PER_PAGE = 9
MAX_PAGE = TOTAL_HACKATHONS // PER_PAGE + 1

DATA_ROOT = Path("../data")
OUTPUT_FILE = Path(DATA_ROOT / "hackathons.txt")
CSV_OUTPUT_FILE = Path(DATA_ROOT / "hackathons.csv")
LOG_FILE = Path("scrape.log")

CHUNK_ROOT = Path(DATA_ROOT / "inputs")
if not CHUNK_ROOT.exists():
    CHUNK_ROOT.mkdir()

logger = logging.getLogger(__name__)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

def scrape_hackathons():
    with open(OUTPUT_FILE, "w") as output_file:
        for page_index in tqdm(range(1, MAX_PAGE + 1), total=MAX_PAGE, desc="Scraping"):
            response = requests.get(f"{BASE_URL}&page={page_index}")
            if response.status_code != 200:
                logger.error(f"Failed to fetch page {page_index}")
                return

            output_file.write(response.text + "\n")

def compile_csv():
    data_rows = []

    with open(OUTPUT_FILE, "r") as input_file:
        for line in input_file:
            hackathon_object = json.loads(line)
            for hackathon in hackathon_object["hackathons"]:
                # Submission year must be before 2025 because recent hackathons might not
                # have posted their winners
                date_string =hackathon["submission_period_dates"]
                year_val = int(date_string[-4:])
                assert 2009 <= year_val <= 2026 # Sanity check
                if year_val > 2025:
                    continue

                # Skip hackathons with less than 30 participants
                if hackathon["registrations_count"] < 30:
                    continue

                # Process hackathon
                fields = [
                    "id",
                    "title",
                    "url",
                    "submission_period_dates",
                    "themes",
                    "registrations_count"
                ]
                transformed_object = {
                    field: hackathon[field]
                    for field in fields
                }
                data_rows.append(transformed_object)


    df = pd.DataFrame(data_rows)
    df.to_csv(CSV_OUTPUT_FILE, index=False)

def chunk_df():
    df = pd.read_csv(CSV_OUTPUT_FILE)
    chunk_size = 1000
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i + chunk_size]
        chunk.to_csv(CHUNK_ROOT / f"hackathon_{i // chunk_size}.csv", index=False)

if __name__ == '__main__':
    # scrape_hackathons()
    compile_csv()
    chunk_df()

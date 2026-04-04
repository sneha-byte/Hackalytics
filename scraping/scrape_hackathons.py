import logging
from pathlib import Path
import requests
from tqdm import tqdm

BASE_URL = "https://devpost.com/api/hackathons?status[]=ended&order_by=deadline"
TOTAL_HACKATHONS = 12509
PER_PAGE = 9
MAX_PAGE = TOTAL_HACKATHONS // PER_PAGE + 1

OUTPUT_FILE = Path("../data/hackathons.txt")
LOG_FILE = Path("scrape.log")

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

if __name__ == '__main__':
    scrape_hackathons()

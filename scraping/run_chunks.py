import subprocess
from pathlib import Path
import sys

if __name__ == "__main__":
    start_idx, end_idx = map(int, sys.argv[1:])
    if end_idx <= start_idx:
        raise ValueError("End index must be greater than start index")

    data_root = Path("../data")
    input_root = data_root / Path("inputs")
    output_root = data_root / Path("outputs")
    crawl_data_root = data_root / Path("crawl_data")

    for i in range(start_idx, end_idx):
        input_file = input_root / f"hackathon_{i}.csv"
        output_file = output_root / f"project-output-{i}.csv"
        job_dir = crawl_data_root / f"job-{i}"

        subprocess.run([
            "scrapy",
            "crawl",
            "ProjectSpider",
            "-O",
            output_file,
            "-a",
            f"dataset={input_file}",
            "-s",
            f"JOBDIR={job_dir}"
        ])

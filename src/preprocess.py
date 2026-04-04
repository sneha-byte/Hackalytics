import nltk
import pandas as pd
import re
from pathlib import Path
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

# Get English stopwords and tokenize
stop_words = set(stopwords.words('english'))

# BASE_DIR = project root folder
# If this file is in src/preprocess.py, parent.parent goes up to the main project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# File paths
HACKATHONS_PATH = BASE_DIR / "data" / "processed" / "processed_hackathons.csv"
PROJECTS_PATH = BASE_DIR / "data" / "raw" / "projects.csv"
PROCESSED_PROJECTS_PATH = BASE_DIR / "data" / "processed" / "processed_projects.csv"
WORD_COUNTS_PATH = BASE_DIR / "data" / "processed" / "word_counts_by_year.csv"

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "our", "your",
    "was", "were", "are", "have", "has", "had", "can", "will", "not", "but",
    "project", "projects", "app", "using", "used", "build", "built", "user",
    "users", "team", "hackathon", "solution", "platform", "make", "made", "in"
    "one", "two", "many", "would", "could", "should", "also", "like", "get", "got",
    "use", "you", "their", "one", "more", "you", "di"
}

MIN_WORD_COUNT = 6

# clean raw text and turn everything lc remove links and punchuation and spaces
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# load hackathons and projects and take year from hackathon start and merge it into project using id
# creates processed projects csv with cleaned text and year
def build_processed_projects():
    hackathons = pd.read_csv(HACKATHONS_PATH)
    projects = pd.read_csv(PROJECTS_PATH)
    # Turn submission_start into datetime values
    hackathons["submission_start"] = pd.to_datetime(
        hackathons["submission_start"], errors="coerce"
    )
    # Pull out just the year
    hackathons["year"] = hackathons["submission_start"].dt.year

    # Keep only id and year so we can merge year into the projects table
    # Rename hackathon id column to match projects table key
    hackathon_years = hackathons[["id", "year"]].copy()
    hackathon_years = hackathon_years.rename(columns={"id": "hackathon_id"})

    # Merge year into projects using hackathon_id
    projects = projects.merge(hackathon_years, on="hackathon_id", how="left")

    # Make one text column:
    # use description first, and if that is missing, use full-description
    projects["text"] = projects["description"].fillna(
        projects["full-description"]
    ).fillna("")

    # Create a cleaned text version for word counting
    projects["clean_text"] = projects["text"].apply(clean_text)

    # Save the full cleaned projects dataset
    projects.to_csv(PROCESSED_PROJECTS_PATH, index=False)

    return projects

# make dataset with year word and count
def generate_word_counts_csv(df):
    rows = []

    # Loop through each unique year in the dataframe
    for year in sorted(df["year"].dropna().unique()):
        # Keep only projects from one year
        year_df = df[df["year"] == year]

        # Join all cleaned text from that year into one big string and split it into words
        text = " ".join(year_df["clean_text"].fillna(""))
        words = text.split()

        # Count how many times each word appears
        counts = Counter(words)

        # Remove stopwords and very short words
        filtered = {
            word: count
            for word, count in counts.items()
            if word not in STOPWORDS and word not in stop_words and len(word) > 2
        }

        # Save every filtered word for that year
        for word, count in filtered.items():
            if count >= MIN_WORD_COUNT:
                rows.append({
                    "year": int(year),
                    "word": word,
                    "count": count
                })

    # Turn the list of rows into a dataframe
    result = pd.DataFrame(rows)
    # Save to CSV
    result.to_csv(WORD_COUNTS_PATH, index=False)

# pipeline: build processed projects and then build word counts
def main():
    projects = build_processed_projects()
    generate_word_counts_csv(projects)

    print(f"Saved processed projects to: {PROCESSED_PROJECTS_PATH}")
    print(f"Saved yearly word counts to: {WORD_COUNTS_PATH}")

if __name__ == "__main__":
    main()
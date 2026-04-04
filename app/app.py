import sys
from pathlib import Path

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="Hackathon Project Trends Dashboard",
    layout="wide"
)

# Find project root so file paths work reliably
BASE_DIR = Path(__file__).resolve().parent.parent
WORD_CLOUD_PATH = BASE_DIR / "data" / "processed" / "word_counts_by_year.csv"
st.set_page_config(layout="wide")
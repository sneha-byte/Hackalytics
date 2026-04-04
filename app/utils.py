from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

WORD_CLOUD_PATH = DATA_DIR / "word_counts_by_year.csv"
TOOLS_PATH = DATA_DIR / "tool_counts_by_year.csv"
LOCATIONS_PATH = DATA_DIR / "hackathon_locations_cleaned.csv"
HACKATHONS_PATH = DATA_DIR / "processed_hackathons.csv"
PROJECTS_PATH = DATA_DIR / "processed_projects.csv"

@st.cache_data
def load_word_counts():
    return pd.read_csv(WORD_CLOUD_PATH)

@st.cache_data
def load_tool_counts():
    return pd.read_csv(TOOLS_PATH)

@st.cache_data
def load_locations():
    return pd.read_csv(LOCATIONS_PATH)

@st.cache_data
def load_hackathons():
    return pd.read_csv(HACKATHONS_PATH)

@st.cache_data
def load_projects():
    return pd.read_csv(PROJECTS_PATH)
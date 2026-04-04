from pathlib import Path
import pandas as pd
import streamlit as st
import ast

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

WORD_CLOUD_PATH = DATA_DIR / "word_counts_by_year.csv"
TOOLS_PATH = DATA_DIR / "tool_counts_by_year.csv"
LOCATIONS_PATH = DATA_DIR / "hackathon_locations_cleaned.csv"
HACKATHONS_PATH = DATA_DIR / "processed_hackathons.csv"
PROJECTS_PATH = DATA_DIR / "processed_projects.csv"

MIN_YEAR = 2009
MAX_YEAR = 2025

@st.cache_data
def load_word_counts():
    df = pd.read_csv(WORD_CLOUD_PATH)
    return df

@st.cache_data
def load_tool_counts():
    df = pd.read_csv(TOOLS_PATH)
    return df

@st.cache_data
def load_locations():
    df = pd.read_csv(LOCATIONS_PATH)
    return df

@st.cache_data
def load_hackathons():
    df = pd.read_csv(HACKATHONS_PATH)
    if "submission_start" in df.columns:
        df["submission_start"] = pd.to_datetime(df["submission_start"], errors="coerce")
        df["year"] = df["submission_start"].dt.year
    return df

@st.cache_data
def load_projects():
    df = pd.read_csv(PROJECTS_PATH)
    return df

def get_selected_year():
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = MAX_YEAR

    st.sidebar.header("Year Filter")
    st.session_state.selected_year = st.sidebar.slider(
        "Select year",
        min_value=MIN_YEAR,
        max_value=MAX_YEAR,
        value=st.session_state.selected_year,
        step=1,
    )
    return st.session_state.selected_year

def parse_themes(theme_value):
    if pd.isna(theme_value):
        return []

    text = str(theme_value).strip()

    if not text:
        return []

    try:
        parsed = ast.literal_eval(text)

        if isinstance(parsed, list):
            names = []
            for item in parsed:
                if isinstance(item, dict) and "name" in item:
                    names.append(str(item["name"]).strip())
                else:
                    names.append(str(item).strip())
            return [x for x in names if x]
    except Exception:
        pass

    return [x.strip() for x in text.split(",") if x.strip()]
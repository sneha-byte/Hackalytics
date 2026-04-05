from collections import defaultdict
from pathlib import Path
import ast

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from wordcloud import WordCloud

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"

PROCESSED_HACKATHONS_PATH = DATA_DIR / "processed_hackathons.csv"
PROJECTS_PATH = DATA_DIR / "projects.csv"
THEME_TREND_PATH = DATA_DIR / "theme_trend.csv"
TOOL_TREND_PATH = DATA_DIR / "tool_trend.csv"
WORD_CLOUD_PATH = DATA_DIR / "word_cloud_output.csv"
LOCATION_TREND_PATH = DATA_DIR / "location_trend.csv"
LOCATIONS_PATH = DATA_DIR / "locations.csv"

MIN_YEAR = 2009
MAX_YEAR = 2025


def init_page():
    st.set_page_config(
        page_title="Hackalytics",
        page_icon="🏆",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_global_css()

    if "selected_year" not in st.session_state:
        st.session_state["selected_year"] = MAX_YEAR


def apply_global_css():
    st.markdown(
        """
        <style>
        div[data-testid="stMetric"] {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 14px 16px;
        }

        div[data-testid="stSlider"] label p {
            font-size: 1.05rem !important;
            font-weight: 700 !important;
        }

        div[data-baseweb="slider"] > div > div {
            height: 8px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(show_home_message=False):
    with st.sidebar:
        st.title("Hackalytics")
        st.caption("Hackathon trend explorer")

        if show_home_message:
            st.info("Home shows overall trends across all years.")
            st.write(f"Data range: **{MIN_YEAR}–{MAX_YEAR}**")
            return None

        year = st.slider(
            "Select year",
            min_value=MIN_YEAR,
            max_value=MAX_YEAR,
            key="selected_year",
            help="This selected year stays the same across the other pages.",
        )
        st.caption(f"Currently viewing **{year}**")
        return year


@st.cache_data
def load_processed_hackathons():
    return pd.read_csv(PROCESSED_HACKATHONS_PATH)

@st.cache_data
def load_projects():
    return pd.read_csv(PROJECTS_PATH)

@st.cache_data
def load_trend_file(file_path):
    df = pd.read_csv(file_path)
    df["period"] = pd.to_datetime(df["period"], errors="coerce")
    df["year"] = df["period"].dt.year
    return df


@st.cache_data
def load_locations():
    return pd.read_csv(LOCATIONS_PATH)

def filter_year(df, year):
    if "year" not in df.columns:
        return df.iloc[0:0].copy()
    return df[df["year"] == year].copy()


def top_n(df, group_col, value_col="count", n=10):
    if df.empty or group_col not in df.columns:
        return pd.DataFrame(columns=[group_col, value_col])

    if value_col not in df.columns:
        df = df.copy()
        df[value_col] = 1

    return (
        df.groupby(group_col, as_index=False)[value_col]
        .sum()
        .sort_values(value_col, ascending=False)
        .head(n)
    )

@st.cache_data
def build_home_metrics():
    hackathons = load_processed_hackathons()
    projects = load_projects()
    theme_trend = load_trend_file(THEME_TREND_PATH)
    tool_trend = load_trend_file(TOOL_TREND_PATH)
    location_trend = load_trend_file(LOCATION_TREND_PATH)

    all_theme_names = theme_trend["theme"].unique()
    unique_tools = len(tool_trend["tool"].unique())

    total_hackathons = len(hackathons)
    total_projects = len(projects)
    unique_themes = len(all_theme_names)

    location_counts = defaultdict(int)
    for _, row in location_trend.iterrows():
        location = row["location"]
        location_counts[location] += row["count"]
    location_counts.pop("Online", None)
    location_counts = dict(sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    location_df = pd.DataFrame([
        {"location": location, "count": count}
        for location, count in location_counts.items()
    ])

    return {
        "total_hackathons": total_hackathons,
        "total_projects": total_projects,
        "unique_themes": unique_themes,
        "unique_tools": unique_tools,
        "top_locations": location_df,
    }


def make_wordcloud_figure(word_df, year):
    fig, ax = plt.subplots(figsize=(10, 4.8))

    if word_df.empty:
        ax.text(0.5, 0.5, f"No word cloud data for {year}", ha="center", va="center", fontsize=16)
        ax.axis("off")
        return fig

    frequencies = dict(zip(word_df["word"], word_df["count"]))

    wc = WordCloud(
        width=1200,
        height=550,
        background_color="white",
        collocations=False,
        max_words=80,
    ).generate_from_frequencies(frequencies)

    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    return fig

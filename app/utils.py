from collections import defaultdict
from pathlib import Path
import pandas as pd
import streamlit as st
import pydeck as pdk

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"

PROCESSED_HACKATHONS_PATH = DATA_DIR / "processed_hackathons.csv"
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
            background: light-dark(#f8fafc, #0e1117);
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

        default_year = st.session_state.get("selected_year", MAX_YEAR)
        year = st.slider(
            "Select year",
            min_value=MIN_YEAR,
            max_value=MAX_YEAR,
            value=default_year,
            key="selected_year",
            help="This selected year stays the same across the other pages.",
        )
        return year


@st.cache_data
def load_processed_hackathons():
    return pd.read_csv(PROCESSED_HACKATHONS_PATH)

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
    theme_trend = load_trend_file(THEME_TREND_PATH)
    tool_trend = load_trend_file(TOOL_TREND_PATH)
    location_trend = load_trend_file(LOCATION_TREND_PATH)

    all_theme_names = theme_trend["theme"].unique()
    unique_tools = len(tool_trend["tool"].unique())

    total_hackathons = len(hackathons)
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
        "total_projects": 147760,
        "unique_themes": unique_themes,
        "unique_tools": unique_tools,
        "top_locations": location_df,
    }

def render_map(df, tooltip):
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[longitude, latitude]",
        get_radius="radius",
        get_fill_color=[255, 99, 132, 180],
        get_line_color=[255, 255, 255, 200],
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_min_pixels=4,
        radius_max_pixels=40,
        line_width_min_pixels=1,
    )

    view_state = pdk.ViewState(
        latitude=20,
        longitude=0,
        zoom=1.2,
        pitch=0,
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="road",
        ),
        use_container_width=True,
    )

def parse_coordinates(coord):
    try:
        if pd.isna(coord):
            return None, None

        coord = str(coord).strip().strip("(").strip(")")
        lat_str, lon_str = coord.split(",")

        latitude = float(lat_str.strip())
        longitude = float(lon_str.strip())

        return latitude, longitude
    except Exception:
        return None, None

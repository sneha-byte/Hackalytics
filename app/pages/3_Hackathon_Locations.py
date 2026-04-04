from pathlib import Path
import re
import pandas as pd
import streamlit as st
import pydeck as pdk


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "processed_hackathons.csv"

st.set_page_config(
    page_title="Hackathon Locations",
    layout="wide",
)

st.title("Hackathon Locations")
st.subheader("Where are hackathons being held?")


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


def extract_year(date_text):
    try:
        if pd.isna(date_text):
            return None

        text = str(date_text).strip()

        matches = re.findall(r"(20\d{2}|19\d{2})", text)
        if matches:
            return int(matches[-1])

        return None
    except Exception:
        return None


@st.cache_data
def load_hackathon_data():
    df = pd.read_csv(DATA_PATH)

    # Extract year
    df["year"] = df["submission_period_dates"].apply(extract_year)

    # Parse coordinates
    df[["latitude", "longitude"]] = df["coordinate"].apply(
        lambda x: pd.Series(parse_coordinates(x))
    )

    # Clean columns safely
    df["title"] = df["title"].fillna("Unknown Hackathon")

    if "geo_location" not in df.columns:
        df["geo_location"] = "Unknown"
    else:
        df["geo_location"] = df["geo_location"].fillna("Unknown")

    if "locality" not in df.columns:
        df["locality"] = ""
    else:
        df["locality"] = df["locality"].fillna("")

    if "registrations_count" not in df.columns:
        df["registrations_count"] = 0
    else:
        df["registrations_count"] = pd.to_numeric(
            df["registrations_count"], errors="coerce"
        ).fillna(0)

    if "url" not in df.columns:
        df["url"] = ""

    # Keep valid rows
    df = df.dropna(subset=["latitude", "longitude", "year"]).copy()
    df["year"] = df["year"].astype(int)

    return df


df = load_hackathon_data()

# Slider
min_year = int(df["year"].min())
max_year = int(df["year"].max())
default_year = st.session_state.get("selected_year", max_year)

year = st.sidebar.slider(
    "Select Year",
    min_value=min_year,
    max_value=max_year,
    value=default_year,
    step=1,
)

st.session_state["selected_year"] = year

year_df = df[df["year"] == year].copy()

if year_df.empty:
    st.warning(f"No location data found for {year}.")
    st.stop()

year_df = year_df.drop_duplicates(
    subset=["title", "latitude", "longitude"]
).copy()

# Radius for map bubbles
year_df["radius"] = year_df["registrations_count"].clip(lower=20)
year_df["radius"] = year_df["radius"].apply(
    lambda x: max(20000, min(x * 800, 120000))
)

# Top 5 locations for selected year
top_locations = (
    year_df.groupby("geo_location")
    .size()
    .reset_index(name="count")
    .sort_values(["count", "geo_location"], ascending=[False, True])
    .head(5)
)

view_state = pdk.ViewState(
    latitude=year_df["latitude"].mean(),
    longitude=year_df["longitude"].mean(),
    zoom=1.2,
    pitch=0,
)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=year_df,
    get_position="[longitude, latitude]",
    get_radius="radius",
    get_fill_color=[255, 99, 132, 180],
    get_line_color=[255, 255, 255, 200],
    pickable=True,
    opacity=0.8,
    stroked=True,
    filled=True,
    line_width_min_pixels=1,
)

tooltip = {
    "html": """
        <b>{title}</b><br/>
        Year: {year}<br/>
        Location: {geo_location}<br/>
        Locality: {locality}<br/>
        Registrations: {registrations_count}
    """,
    "style": {
        "backgroundColor": "white",
        "color": "black"
    },
}

# Layout: map on left, top 5 on right
left_col, right_col = st.columns([3, 1])

with left_col:
    st.pydeck_chart(
        pdk.Deck(
            map_style="dark",
            initial_view_state=view_state,
            layers=[layer],
            tooltip=tooltip,
        ),
        use_container_width=True,
        height=600,
    )

with right_col:
    st.subheader(f"Top 5 Locations in {year}")

    clean_df = year_df[
            year_df["locality"].notna() & (year_df["locality"].str.strip() != "")
        ].copy()

    top_locations = (
        clean_df.groupby("locality")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(5)
    )

    for row in top_locations.itertuples(index=False):
        st.markdown(f"- **{row.locality}** ({row.count})")

st.subheader(f"Locations in {year}")

display_df = year_df[
    ["title", "geo_location", "locality", "registrations_count", "url"]
].sort_values("registrations_count", ascending=False)

st.dataframe(display_df, use_container_width=True)
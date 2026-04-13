import math
from pathlib import Path
import pandas as pd
import streamlit as st
from utils import init_page, render_map, render_sidebar, parse_coordinates
import plotly.express as px

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "processed_hackathons.csv"

st.set_page_config(
    page_title="Hackathon Locations",
    layout="wide",
)
init_page()

st.title("Hackathon Locations")

@st.cache_data
def load_hackathon_data():
    df = pd.read_csv(DATA_PATH)
    df["submission_start"] = pd.to_datetime(df["submission_start"], errors="coerce")
    df["year"] = df["submission_start"].dt.year

    online_percentage_map = {}
    for year, group in df.groupby("year"):
        online_percentage_map[year] = (group["geo_location"] == "Online").mean()

    df[["latitude", "longitude"]] = df["coordinate"].apply(
        lambda x: pd.Series(parse_coordinates(x))
    )

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

    df_filtered = df.dropna(subset=["latitude", "longitude", "year"]).copy()
    df_filtered["year"] = df["year"].astype(int)

    return df_filtered, online_percentage_map, df


def build_top_locations_with_change(df, year):
    current_df = df[df["year"] == year].copy()
    previous_df = df[df["year"] == year - 1].copy()

    current_df = current_df[
        current_df["locality"].notna() & (current_df["locality"].str.strip() != "")
    ].copy()
    previous_df = previous_df[
        previous_df["locality"].notna() & (previous_df["locality"].str.strip() != "")
    ].copy()

    current_counts = (
        current_df.groupby("locality")
        .size()
        .reset_index(name="count")
    )

    previous_counts = (
        previous_df.groupby("locality")
        .size()
        .reset_index(name="prev_count")
    )

    merged = current_counts.merge(previous_counts, on="locality", how="left")
    merged["prev_count"] = merged["prev_count"].fillna(0).astype(int)
    merged["change"] = merged["count"] - merged["prev_count"]

    merged = merged.sort_values(
        ["count", "locality"], ascending=[False, True]
    ).head(5)

    return merged


df, percentages, df_non_filtered = load_hackathon_data()

# Slider
year = render_sidebar()

year_df = df[df["year"] == year].copy()

year_df = year_df.drop_duplicates(
    subset=["title", "latitude", "longitude"]
).copy()

year_df["radius"] = year_df["registrations_count"].clip(lower=20)
year_df["radius"] = year_df["radius"].apply(
    lambda x: math.log(x) * 15000
)

top_locations = build_top_locations_with_change(df, year)

left, right = st.columns([0.7, 0.3], gap="medium")
with left:
    st.subheader(f"Locations Map in {year}")

    if year_df.empty:
        st.warning(f"No location data found for {year}.")
    else:
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
                "color": "black",
            },
        }
        render_map(year_df, tooltip)

with right:
    st.subheader(f"Online vs In-person Locations in {year}")
    online_pct = percentages.get(year, 0) * 100
    other_pct = 100 - online_pct

    # Data
    labels = ["Online", "In-person"]
    sizes = [online_pct, other_pct]

    pie_df = pd.DataFrame({"label": labels, "size": sizes})
    # Plot
    fig = px.pie(
        pie_df,
        values="size",
        names="label",
    )
    st.plotly_chart(fig)

with st.container():
    st.markdown(f"### Top 5 Locations in {year}")

    if top_locations.empty:
        st.info("No locality data available for this year.")
    else:
        columns = st.columns(min(len(top_locations), 5))
        for column, row in zip(columns, top_locations.itertuples(index=False)):
            with column:
                st.metric(row.locality, row.count, delta=row.change)


st.subheader(f"Locations in {year}")
df_non_filtered = df_non_filtered[df_non_filtered["year"] == year].copy()
display_df = df_non_filtered[
    ["title", "geo_location", "locality", "registrations_count", "url"]
].sort_values("registrations_count", ascending=False)

st.dataframe(display_df)
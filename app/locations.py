import pandas as pd
import streamlit as st
import pydeck as pdk
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
HACKATHONS_PATH = BASE_DIR / "data" / "processed" / "processed_hackathons.csv"
LOCATIONS_OUTPUT_PATH = BASE_DIR / "data" / "processed" / "hackathon_locations_cleaned.csv"

# convert coordinate string into lat = 2 and long = 9
def parse_coordinates(coord):
    try:
        if pd.isna(coord):
            return None, None

        # Make sure it is a string and remove parentheses/spaces
        coord = str(coord).strip().strip("(").strip(")")

        # Split into two parts using the comma
        lat_str, lon_str = coord.split(",")

        # Convert text into numbers
        latitude = float(lat_str.strip())
        longitude = float(lon_str.strip())

        return latitude, longitude

    except Exception:
        return None, None


# clean location data and make location file with location lat and long
def build_location_data():
    # Load hackathons data
    df = pd.read_csv(HACKATHONS_PATH)

    # Rename geo_location to location
    df = df.rename(columns={"geo_location": "location"})
    # Clean location text if missing fill with unknown, verify str and strip
    df["location"] = df["location"].fillna("Unknown").astype(str).str.strip()
    # take coordinate and apply parse coordinate to it and convert to series and then assign to lat and long
    df[["latitude", "longitude"]] = df["coordinate"].apply(lambda x: pd.Series(parse_coordinates(x)))
    # Remove rows without usable coordinates
    df = df.dropna(subset=["latitude", "longitude"]).copy()
    # remove online events
    df = df[df["location"].str.lower() != "online"]

    # Save cleaned output
    df.to_csv(LOCATIONS_OUTPUT_PATH, index=False)
    print(f"Saved cleaned location data to: {LOCATIONS_OUTPUT_PATH}")


# load clean location file and cache it
@st.cache_data
def load_location_data():
    df = pd.read_csv(LOCATIONS_OUTPUT_PATH)
    return df


# group hackathons by location so theres one point for each location
def get_location_counts_for_map():
    df = load_location_data()

    # groups rows with same location and coord and counts how many rows are in that group
    grouped = (
        df.groupby(["location", "latitude", "longitude"])
        .size()
        .reset_index(name="count")
    )

    # Sort biggest counts first
    grouped = grouped.sort_values("count", ascending=False).reset_index(drop=True)
    return grouped

# render map using pydeck with circle size based on hackathon concentration
def render_location_map():
    map_df = get_location_counts_for_map()

    if map_df.empty:
        st.warning("No location data available for the map.")
        return

    st.subheader("Hackathon Locations Map")

    # Scatterplot layer draws circles on the map
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[longitude, latitude]",
        get_radius="count * 20000",
        get_fill_color=[255, 75, 75, 180],
        pickable=True,
        auto_highlight=True,
    )

    # Center the map  around the average of all points
    view_state = pdk.ViewState(
        latitude=map_df["latitude"].mean(),
        longitude=map_df["longitude"].mean(),
        zoom=2,
        pitch=0,
    )

    # Create the deck map
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{location}\nHackathons: {count}"}
    )
    # Show the map in Streamlit
    st.pydeck_chart(deck, width='stretch')
    st.dataframe(map_df, width='stretch')
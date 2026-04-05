import streamlit as st
from pathlib import Path
import pandas as pd
import pydeck as pdk
from matplotlib import pyplot as plt
from utils import init_page, render_sidebar, build_home_metrics, THEME_TREND_PATH, load_trend_file, TOOL_TREND_PATH

init_page()
render_sidebar(show_home_message=True)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "processed_hackathons.csv"

st.title('Hackalytics')
st.write("Overall dashboard across all years. Use the other pages to explore one year at a time.")

metrics = build_home_metrics()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Hackathons", f"{metrics['total_hackathons']:,}")
c2.metric("Total Projects", f"{metrics['total_projects']:,}")
c3.metric("Unique Themes", f"{metrics['unique_themes']:,}")
c4.metric("Unique Tools", f"{metrics['unique_tools']:,}")

st.divider()

def plot_top(trend_file, column_name, default_selection=None):
    trend_df = load_trend_file(trend_file)

    all_options = trend_df[column_name].unique().tolist()
    options = st.multiselect("Select keywords", all_options, default=default_selection or all_options[:5])

    trend_df = trend_df[trend_df[column_name].isin(options)]

    top = trend_df.groupby(column_name)["count"].sum().sort_values(ascending=False).index.tolist()
    df_top = trend_df[trend_df[column_name].isin(top)]

    df_top["period"] = df_top["period"].dt.year
    pivot = df_top.pivot(index="period", columns=column_name, values="count").fillna(0)

    # --- Step 3: Plot with Matplotlib ---
    fig, ax = plt.subplots(figsize=(10, 6))

    for tool in pivot.columns:
        ax.plot(pivot.index, pivot[tool], label=tool)

    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    ax.set_xlim(2008, 2026)
    ax.set_title(f"Usage of {column_name.title()} Over Time")
    ax.legend()
    ax.grid(True)

    # Show in Streamlit
    st.pyplot(fig)

with st.container():
    st.subheader("What problems have hackers been focused on?")
    plot_top(
        THEME_TREND_PATH,
        "theme",
        ["COVID-19", "Social Good", "Beginner Friendly", "Open Ended", "Machine Learning/AI", "Gaming"]
    )

with st.container():
    st.subheader("What tools have hackers been using?")
    plot_top(TOOL_TREND_PATH, "tool", ["python", "javascript", "html", "web", "ios", "gemini"])


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


@st.cache_data
def load_map_data():
    df = pd.read_csv(DATA_PATH)

    # turn "(lat, lon)" into separate numeric columns
    df[["latitude", "longitude"]] = df["coordinate"].apply(
        lambda x: pd.Series(parse_coordinates(x))
    )

    if "locality" in df.columns:
        df["location_label"] = df["locality"].fillna("Unknown")
    elif "geo_location" in df.columns:
        df["location_label"] = df["geo_location"].fillna("Unknown")
    else:
        df["location_label"] = "Unknown"

    df = df.dropna(subset=["latitude", "longitude"]).copy()

    # group same locations together so circle size reflects number of hackathons there
    map_df = (
        df.groupby(["location_label", "latitude", "longitude"])
        .size()
        .reset_index(name="count")
    )

    # circle size
    map_df["radius"] = map_df["count"] * 20000

    return map_df


with st.container():
    st.subheader("Where are hackathons being held?")

    map_df = load_map_data()

    st.caption("Each circle represents a hackathon location. Bigger circles mean more hackathons were held there.")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[longitude, latitude]",
        get_radius="radius",
        get_fill_color=[255, 99, 132, 180],
        get_line_color=[255, 255, 255, 200],
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_min_pixels=4,
        radius_max_pixels=45,
        line_width_min_pixels=1,
    )

    view_state = pdk.ViewState(
        latitude=20,
        longitude=0,
        zoom=1.2,
        pitch=0,
    )

    tooltip = {
        "html": "<b>{location_label}</b><br/>Hackathons: {count}",
        "style": {
            "backgroundColor": "rgba(0, 0, 0, 0.75)",
            "color": "white",
        },
    }

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="road",
        ),
        use_container_width=True,
    )
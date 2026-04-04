import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import (
    init_page,
    render_sidebar,
    load_location_trend,
    filter_year,
    top_n,
)

init_page()
year = render_sidebar()

st.title("Hackathon Locations")
st.caption('Answers: "Where are hackathons being held?"')

location_df = load_location_trend()
location_year = filter_year(location_df, year)

if "location" in location_year.columns:
    location_year = location_year[
        ~location_year["location"].fillna("").str.strip().str.lower().eq("online")
    ].copy()

top_locations_df = top_n(location_year, "location", "count", 15)

col1, col2 = st.columns([1.2, 0.8])

with col1:
    st.subheader(f"Top locations in {year}")
    if top_locations_df.empty:
        st.warning(f"No location data found for {year}.")
    else:
        st.bar_chart(top_locations_df.set_index("location"))

with col2:
    st.subheader("Takeaway")
    if top_locations_df.empty:
        st.info("No location trend data is available for this year.")
    else:
        top_locations = top_locations_df["location"].head(5).tolist()
        st.markdown(
            f"""
            In **{year}**, hackathons were most commonly held in:

            1. **{top_locations[0]}**
            2. **{top_locations[1]}**
            3. **{top_locations[2]}**
            4. **{top_locations[3]}**
            5. **{top_locations[4]}**
            """
        )

st.divider()
st.subheader("Location detail table")
st.dataframe(top_locations_df, use_container_width=True, hide_index=True)
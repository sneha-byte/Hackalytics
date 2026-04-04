import streamlit as st
from utils import init_page, render_sidebar, build_home_metrics

init_page()
render_sidebar(show_home_message=True)

st.markdown('<div class="main-title">Hackalytics</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Overall dashboard across all years. Use the other pages to explore one year at a time.</div>',
    unsafe_allow_html=True,
)

metrics = build_home_metrics()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Hackathons", f"{metrics['total_hackathons']:,}")
c2.metric("Total Projects", f"{metrics['total_projects']:,}")
c3.metric("Unique Themes", f"{metrics['unique_themes']:,}")
c4.metric("Unique Tools", f"{metrics['unique_tools']:,}")
c5.metric("Unique Locations", f"{metrics['unique_locations']:,}")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("What problems have hackers been focused on?")
    if not metrics["top_themes"].empty:
        st.bar_chart(metrics["top_themes"].set_index("theme"))
    else:
        st.info("No theme data found.")

    st.subheader("What tools have hackers been using?")
    if not metrics["top_tools"].empty:
        st.bar_chart(metrics["top_tools"].set_index("tool"))
    else:
        st.info("No tool data found.")

with right:
    st.subheader("Where are hackathons being held?")
    if not metrics["top_locations"].empty:
        st.bar_chart(metrics["top_locations"].set_index("location"))
    else:
        st.info("No location data found.")

st.divider()
st.info(
    "The three analysis pages share one year slider using Streamlit session state, "
    "so when you switch pages the selected year stays the same."
)

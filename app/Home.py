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

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Hackathons", f"{metrics['total_hackathons']:,}")
c2.metric("Total Projects", f"{metrics['total_projects']:,}")
c3.metric("Unique Themes", f"{metrics['unique_themes']:,}")
c4.metric("Unique Tools", f"{metrics['unique_tools']:,}")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("What problems have hackers been focused on?")
    st.bar_chart(metrics["top_themes"], x="theme", y="count", horizontal=True, sort=True)

    st.subheader("What tools have hackers been using?")
    st.bar_chart(metrics["top_tools"], x="tool", y="count", horizontal=True, sort=True)

with right:
    st.subheader("Where are hackathons being held?")
    st.bar_chart(metrics["top_locations"], x="location", y="count", horizontal=True, sort=True)

st.divider()
st.info(
    "The three analysis pages share one year slider using Streamlit session state, "
    "so when you switch pages the selected year stays the same."
)

import streamlit as st

st.set_page_config(
    page_title="Hackathon Trends Dashboard",
    page_icon="🏆",
    layout="wide",
)

st.title("🏆 Hackathon Trends Dashboard")
st.markdown("""
Welcome to the dashboard exploring trends in hackathon projects and events.

Use the sidebar to navigate between pages:

- **Themes + Word Cloud** → What problems have hackers been focused on?
- **Tool Trends** → What tools have hackers been using?
- **Hackathon Locations** → Where are hackathons being held?
""")
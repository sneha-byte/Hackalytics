import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import word_cloud as wc
import matplotlib.pyplot as plt
from io import BytesIO

st.title("Themes and Word Cloud Analysis")

st.markdown("""
Explore the most common themes and keywords from hackathon projects over different years.
""")


def show_word_cloud():
    # Load data to get available years
    try:
        df = pd.read_csv("data/processed/processed_projects.csv")

        available_years = sorted(df['year'].unique())
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'data/processed/processed_projects.csv' exists.")
        available_years = []

    if available_years:
        selected_year = st.selectbox(
            "Select Year:",
            available_years
        )

        if st.button("Generate Word Cloud", type="primary"):
            with st.spinner("Generating word cloud..."):
                try:
                    # Generate the word cloud and get the figure
                    fig = wc.generate_word_cloud(selected_year, df)

                    # Display in streamlit
                    st.pyplot(fig)

                    # Add download button
                    buf = BytesIO()
                    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
                    buf.seek(0)

                    st.download_button(
                        label="Download Word Cloud",
                        data=buf,
                        file_name=f"wordcloud_{selected_year}.png",
                        mime="image/png",
                        help="Download the word cloud as a PNG image"
                    )

                except Exception as e:
                    st.error(f" Error generating word cloud: {str(e)}")
                    st.info("Make sure you have the required data and dependencies installed.")

    else:
        st.warning("No data available. Please check your data processing pipeline.")


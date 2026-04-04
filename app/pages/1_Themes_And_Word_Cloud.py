import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import load_theme_trend, load_word_cloud, make_wordcloud_figure

import matplotlib.pyplot as plt
from io import BytesIO

st.title("Themes and Word Cloud Analysis")

st.markdown("""
Explore the most common themes and keywords from hackathon projects over different years.
""")


def show_word_cloud():
    # Load data to get available years
    # fix file paths and columns for this function
    try:
        df = load_word_cloud()

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
                    fig = make_wordcloud_figure(df, selected_year)

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

    
def show_theme_trends():
    try: 
        df = load_theme_trend()
        available_years = sorted(df['year'].unique())

        start_year = st.selectbox(
            "Select Year for Theme Trends:",
            available_years
        )
        end_year = st.selectbox(
            "Select End Year for Theme Trends:",
            available_years,
            index=len(available_years)-1
        )

        if st.button("Show Theme Trends", type="primary"):
            st.subheader(f"Theme Trends for {start_year} to {end_year}")
            year_df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
            
            # Find top 10 most common themes across the entire time period
            top_themes = year_df.groupby('theme')['count'].sum().nlargest(10).index.tolist()
            
            # Filter to only those top themes
            trend_df = year_df[year_df['theme'].isin(top_themes)]

            # Create line chart
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plot each theme as a separate line
            for theme in top_themes:
                theme_data = trend_df[trend_df['theme'] == theme].sort_values('year')
                ax.plot(theme_data['year'], theme_data['count'], marker='o', label=theme)
            
            ax.set_xlabel('Year')
            ax.set_ylabel('Count')
            ax.set_title(f"Top 10 Theme Trends from {start_year} to {end_year}")
            ax.legend(loc='best', fontsize=9)
            ax.grid(True, alpha=0.3)

            st.pyplot(fig)
        
        
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'data/theme_trend.csv' exists.")
        return
    
if __name__ == "__main__":
    show_theme_trends()
    show_word_cloud()

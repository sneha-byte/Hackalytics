from pathlib import Path
from utils import (init_page, MIN_YEAR, MAX_YEAR, render_sidebar,
                   load_trend_file, THEME_TREND_PATH, filter_year, top_n)
import streamlit as st

st.set_page_config(
    page_title="Themes and Word Cloud",
    layout="wide",
)

st.title("Hackathon Themes and Word Cloud")
st.subheader("What problems have hackers been focused on?")

BASE_DIR = Path(__file__).resolve().parents[2]
WORD_CLOUD_DIR = BASE_DIR / "data" / "word_clouds"

def get_wordcloud_image_path(year: int) -> Path:
    return WORD_CLOUD_DIR / f"word_cloud_{year}.png"


theme_df = load_trend_file(THEME_TREND_PATH)
init_page()

year = render_sidebar()
theme_year = filter_year(theme_df, year)

theme_year = theme_year[theme_year["theme"] != ""].copy()

group_col_name = "theme"
value_col_name = "count"
top_themes_df = top_n(theme_year, group_col_name, value_col_name, n=10)
top_themes_df = top_themes_df[top_themes_df["count"] > 0].copy()

wordcloud_image_path = get_wordcloud_image_path(year)

st.subheader(f"{year} Overview")

metric_col1, metric_col2 = st.columns(2)

with metric_col1:
    st.metric("Themes with non-zero count", int((theme_year["count"] > 0).sum()))

with metric_col2:
    st.metric("Total theme mentions", int(theme_year["count"].sum()))

col1, col2 = st.columns([1.1, 1])

with col1:
    st.markdown("### Theme Chart")
    st.bar_chart(top_themes_df, x="theme", y="count", use_container_width=True, sort=False, horizontal=True)

with col2:
    st.markdown("### Word Cloud")
    if wordcloud_image_path.exists():
        st.image(str(wordcloud_image_path), use_container_width=True)
    else:
        st.info(f"No word cloud image found for {year}")

with st.container():
    st.subheader("Takeaway")
    st.write(f"In **{year}**, hackers were solving the following types of projects:")

    top5_themes = top_themes_df.head(5)
    if not top5_themes.empty:
        columns = st.columns(min(len(top5_themes), 5))
        for column, theme_name in zip(columns, top5_themes["theme"].tolist()):
            with column:
                current_count = top5_themes.loc[top5_themes["theme"] == theme_name, "count"].iloc[0]
                try:
                    prev_value = theme_df[(theme_df["year"] == year - 1) & (theme_df["theme"] == theme_name)]["count"].iloc[0]
                except:
                    prev_value = current_count
                st.metric(theme_name, current_count, delta=current_count - prev_value)

with st.expander("Preview filtered theme data"):
    st.dataframe(theme_year, use_container_width=True)

with st.expander("Preview top themes used in chart"):
    st.dataframe(top_themes_df, use_container_width=True)

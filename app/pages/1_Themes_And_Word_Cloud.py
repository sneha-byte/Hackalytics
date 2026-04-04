import streamlit as st
from app.utils import (
    init_page,
    render_sidebar,
    load_tool_trend,
    filter_year,
    top_n, load_theme_trend, load_word_cloud,
)

init_page()
year = render_sidebar()

st.title("Themes and Word Cloud")
st.caption('Answers: "What problems have hackers been focused on?"')

theme_df = load_theme_trend()
word_df = load_word_cloud()

theme_year = filter_year(theme_df, year)
word_year = filter_year(word_df, year)

top_themes_df = top_n(theme_year, "theme", "count", 12)

col1, col2 = st.columns([1.15, 1])

with col1:
    st.subheader(f"Top themes in {year}")
    if top_themes_df.empty:
        st.warning(f"No theme data found for {year}.")
    else:
        st.bar_chart(top_themes_df.set_index("theme"))

        top_list = top_themes_df["theme"].head(3).tolist()
        if len(top_list) >= 3:
            st.markdown(
                f"**Answer:** In **{year}**, hackers were mostly focused on "
                f"**{top_list[0]}**, **{top_list[1]}**, and **{top_list[2]}**."
            )

with col2:
    st.subheader(f"Word cloud for {year}")
    fig = make_wordcloud_figure(word_year, year)
    st.pyplot(fig, clear_figure=True)

st.divider()
st.subheader("Theme detail table")
st.dataframe(top_themes_df, use_container_width=True, hide_index=True)
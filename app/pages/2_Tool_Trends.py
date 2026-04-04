import streamlit as st
from app.utils import (
    init_page,
    render_sidebar,
    load_theme_trend,
    load_word_cloud,
    filter_year,
    top_n,
    make_wordcloud_figure,
)

init_page()
year = render_sidebar()

st.title("Tool Trends")
st.caption('Answers: "What tools have hackers been using?"')

tool_df = load_tool_trend()
tool_year = filter_year(tool_df, year)
top_tools_df = top_n(tool_year, "tool", "count", 15)

col1, col2 = st.columns([1.2, 0.8])

with col1:
    st.subheader(f"Most used tools in {year}")
    if top_tools_df.empty:
        st.warning(f"No tool data found for {year}.")
    else:
        st.bar_chart(top_tools_df.set_index("tool"))

with col2:
    st.subheader("Takeaway")
    if top_tools_df.empty:
        st.info("No tool trend data is available for this year.")
    else:
        top_tools = top_tools_df["tool"].head(5).tolist()
        st.markdown(
            f"""
            In **{year}**, the most common tools were:

            1. **{top_tools[0]}**
            2. **{top_tools[1]}**
            3. **{top_tools[2]}**
            4. **{top_tools[3]}**
            5. **{top_tools[4]}**
            """
        )

st.divider()
st.subheader("Tool detail table")
st.dataframe(top_tools_df, use_container_width=True, hide_index=True)
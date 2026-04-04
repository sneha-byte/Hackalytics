import streamlit as st
from utils import (
    init_page,
    render_sidebar,
    load_theme_trend,
    load_word_cloud,
    filter_year,
    top_n,
    make_wordcloud_figure,
    load_tool_trend
)

init_page()

# Slider
min_year = 2009
max_year = 2025
default_year = st.session_state.get("selected_year", max_year)

year = st.sidebar.slider(
    "Select Year",
    min_value=min_year,
    max_value=max_year,
    value=default_year,
    step=1,
)

st.session_state["selected_year"] = year

st.title("Tool Trends")
st.write("What tools have hackers been using?")

tool_df = load_tool_trend()
tool_year = filter_year(tool_df, year)
top_tools_df = top_n(tool_year, "tool", "count", 10)
top_tools_df.sort_values("count", ascending=False)

with st.container():
    st.subheader(f"Most used tools in {year}")
    if top_tools_df.empty:
        st.warning(f"No tool data found for {year}.")
    else:
        st.bar_chart(top_tools_df, x="tool", y="count", use_container_width=True, sort=False)

with st.container():
    st.subheader("Takeaway")
    st.write(f"In **{year}**, hackers were using the following tools:")

    top5_tools = top_tools_df.head(5)
    columns = st.columns(min(len(top5_tools), 5))
    for column, tool_name in zip(columns, top5_tools["tool"].tolist()):
        with column:
            current_count = top5_tools.loc[top5_tools["tool"] == tool_name, "count"].iloc[0]
            try:
                prev_value = tool_df[(tool_df["year"] == year - 1) & (tool_df["tool"] == tool_name)]["count"].iloc[0]
            except:
                prev_value = current_count
            st.metric(tool_name, current_count, delta=current_count - prev_value)

st.divider()
st.subheader("Tool detail table")
st.dataframe(top_tools_df, use_container_width=True, hide_index=True)
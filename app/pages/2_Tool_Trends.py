import pandas as pd
import streamlit as st
from utils import (
    init_page,
    render_sidebar,
    filter_year,
    top_n,
    load_trend_file,
    TOOL_TREND_PATH,
    MAX_YEAR,
    MIN_YEAR,
)
from matplotlib import pyplot as plt

init_page()

# Slider
year = render_sidebar()

st.title("Tool Trends")
st.write("What tools have hackers been using?")

tool_df = load_trend_file(TOOL_TREND_PATH)
tool_year = filter_year(tool_df, year)
top_tools_df = top_n(tool_year, "tool", "count", 9)
top_tools_df.sort_values("count", ascending=False)

left, right = st.columns(2)
with left:
    st.subheader(f"Most used tools in {year}")
    if top_tools_df.empty:
        st.warning(f"No tool data found for {year}.")
    else:
        st.bar_chart(top_tools_df, x="tool", y="count", use_container_width=True, sort=False)

with right:
    st.subheader("Tool usage pie chart")

    top_tool_names = top_tools_df["tool"].tolist()
    others_count = 0
    for _, row in tool_year.iterrows():
        if row["tool"] not in top_tool_names:
            others_count += row["count"]

    all_tools = pd.concat([
        top_tools_df,
        pd.DataFrame([{"tool": "Others", "count": others_count}])
    ])

    # Create figure
    fig, ax = plt.subplots()

    ax.pie(
        all_tools["count"],
        labels=all_tools["tool"],
        autopct="%1.1f%%",
        startangle=90
    )

    ax.axis("equal")

    # Show in Streamlit
    st.pyplot(fig)

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
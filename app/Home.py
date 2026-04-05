import datetime

import streamlit as st
from matplotlib import pyplot as plt
from utils import init_page, render_sidebar, build_home_metrics, THEME_TREND_PATH, load_trend_file, TOOL_TREND_PATH

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

def plot_top(trend_file, column_name):
    trend_df = load_trend_file(trend_file)

    all_options = trend_df[column_name].unique().tolist()
    options = st.multiselect("Select keywords", all_options, default=all_options[:3])

    trend_df = trend_df[trend_df[column_name].isin(options)]

    top = trend_df.groupby(column_name)["count"].sum().sort_values(ascending=False).index.tolist()
    df_top = trend_df[trend_df[column_name].isin(top)]

    df_top["period"] = df_top["period"].dt.year
    pivot = df_top.pivot(index="period", columns=column_name, values="count").fillna(0)

    # --- Step 3: Plot with Matplotlib ---
    fig, ax = plt.subplots(figsize=(10, 6))

    for tool in pivot.columns:
        ax.plot(pivot.index, pivot[tool], label=tool)

    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    ax.set_xlim(2008, 2026)
    ax.set_title(f"Usage of {column_name} Over Time")
    ax.legend()
    ax.grid(True)

    # Show in Streamlit
    st.pyplot(fig)

with st.container():
    st.subheader("What problems have hackers been focused on?")
    plot_top(THEME_TREND_PATH, "theme")

with st.container():
    st.subheader("What tools have hackers been using?")
    plot_top(TOOL_TREND_PATH, "tool")

with st.container():
    st.subheader("Where are hackathons being held?")
    st.bar_chart(metrics["top_locations"], x="location", y="count", horizontal=True, sort=False)

st.divider()
st.info(
    "The three analysis pages share one year slider using Streamlit session state, "
    "so when you switch pages the selected year stays the same."
)

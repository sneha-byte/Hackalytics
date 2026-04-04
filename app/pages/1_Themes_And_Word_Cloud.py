from pathlib import Path
from utils import init_page
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Themes and Word Cloud",
    layout="wide",
)

st.title("Hackathon Themes and Word Cloud")
st.subheader("What problems have hackers been focused on?")

BASE_DIR = Path(__file__).resolve().parents[2]
THEME_TREND_PATH = BASE_DIR / "data" / "theme_trend.csv"

# folder where your png files live
# example filenames:
# word_cloud_2009.png
# word_cloud_2010.png
WORD_CLOUD_DIR = BASE_DIR / "data" / "word_clouds"


@st.cache_data
def load_theme_trend():
    df = pd.read_csv(THEME_TREND_PATH)

    df["period"] = pd.to_datetime(df["period"], errors="coerce")
    df["year"] = df["period"].dt.year

    df["theme"] = df["theme"].fillna("").astype(str).str.strip()
    df["count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0)

    return df


def filter_year(df: pd.DataFrame, year: int) -> pd.DataFrame:
    if "year" not in df.columns:
        return df.copy()
    return df[df["year"] == year].copy()


def top_n(df: pd.DataFrame, group_col: str, value_col: str, n: int = 10) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[group_col, value_col])

    return (
        df.groupby(group_col, as_index=False)[value_col]
        .sum()
        .sort_values(value_col, ascending=False)
        .head(n)
    )


def make_theme_chart(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 7))

    if df.empty or df[value_col_name].sum() == 0:
        ax.text(
            0.5,
            0.5,
            "No non-zero theme data available for this year",
            ha="center",
            va="center",
            fontsize=14,
            transform=ax.transAxes,
        )
        ax.axis("off")
        return fig

    df = df.sort_values(value_col_name, ascending=True).copy()

    df[group_col_name] = df[group_col_name].apply(
        lambda x: x if len(str(x)) <= 28 else str(x)[:28] + "..."
    )

    bars = ax.barh(df[group_col_name], df[value_col_name])

    ax.set_title("Top Hackathon Themes", fontsize=17, weight="bold", pad=12)
    ax.set_xlabel("Count", fontsize=12)
    ax.set_ylabel("")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.3)

    ax.tick_params(axis="y", labelsize=11)
    ax.tick_params(axis="x", labelsize=10)

    max_val = df[value_col_name].max()
    offset = max(1, max_val * 0.01)

    for bar, value in zip(bars, df[value_col_name]):
        ax.text(
            bar.get_width() + offset,
            bar.get_y() + bar.get_height() / 2,
            f"{int(value)}",
            va="center",
            fontsize=10,
        )

    plt.tight_layout()
    return fig


def get_wordcloud_image_path(year: int) -> Path:
    return WORD_CLOUD_DIR / f"word_cloud_{year}.png"


theme_df = load_theme_trend()
init_page()

available_years = sorted(theme_df["year"].dropna().astype(int).tolist())

if available_years:
    min_year = int(min(available_years))
    max_year = int(max(available_years))
else:
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
    theme_fig = make_theme_chart(top_themes_df)
    st.pyplot(theme_fig, use_container_width=True)

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

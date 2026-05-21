import streamlit as st
import pandas as pd
from src.parsers import load_anki, load_duolingo, merge_sources
from src.stats import overall_retention, retention_by_language, streak_stats, weekly_averages, compare_languages, activity_heatmap_data
from src.charts import progress_line, language_bar, github_heatmap, accuracy_over_time

st.set_page_config(page_title="LinguaStats", layout="wide")


@st.cache_data
def get_data():
    anki = load_anki("data/anki_sample.csv")
    duo = load_duolingo("data/duolingo_sample.json")
    df = merge_sources(anki, duo)
    return df


df = get_data()

st.title("LinguaStats")
st.caption("прогресс по языкам из Anki + Duolingo")

with st.sidebar:
    st.header("filters")
    langs = sorted(df["language"].unique())
    lang_choice = st.selectbox("language", ["All"] + list(langs))
    min_d = df["date"].min().date()
    max_d = df["date"].max().date()
    date_range = st.date_input("date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    sources = st.multiselect("source", ["anki", "duolingo"], default=["anki", "duolingo"])

filtered = df.copy()
if lang_choice != "All":
    filtered = filtered[filtered["language"] == lang_choice]
if isinstance(date_range, tuple) and len(date_range) == 2:
    filtered = filtered[(filtered["date"] >= pd.Timestamp(date_range[0])) & (filtered["date"] <= pd.Timestamp(date_range[1]))]
filtered = filtered[filtered["source"].isin(sources)]

tab1, tab2, tab3, tab4 = st.tabs(["overview", "progress", "comparison", "heatmap"])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    total_min = filtered["duration_min"].sum()
    total_items = filtered["items"].sum()
    avg_acc = filtered["accuracy"].mean() if len(filtered) else 0
    total_xp = filtered["xp_earned"].sum()

    c1.metric("total time (min)", f"{total_min:,.0f}")
    c2.metric("items / cards", f"{total_items:,.0f}")
    c3.metric("avg accuracy", f"{avg_acc:.1%}" if avg_acc else "—")
    c4.metric("xp earned", f"{total_xp:,.0f}")

    st.subheader("streak")
    sl = lang_choice if lang_choice != "All" else None
    s = streak_stats(filtered, sl)
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("current streak", s["current_streak"])
    sc2.metric("longest streak", s["longest_streak"])
    sc3.metric("active days", s["active_days"])

    st.subheader("recent activity")
    st.dataframe(filtered.sort_values("date", ascending=False).head(15), use_container_width=True)

with tab2:
    sl = lang_choice if lang_choice != "All" else None
    weekly = weekly_averages(filtered, sl)
    if len(weekly):
        st.plotly_chart(progress_line(weekly, "items", "items per week"), use_container_width=True)
        st.plotly_chart(progress_line(weekly, "duration", "minutes per week"), use_container_width=True)
        if filtered["xp_earned"].sum() > 0:
            st.plotly_chart(progress_line(weekly, "xp", "xp per week"), use_container_width=True)
    else:
        st.info("no data for this filter")

with tab3:
    cmp = compare_languages(filtered)
    st.dataframe(cmp, use_container_width=True)
    if len(cmp):
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(language_bar(cmp, "total_minutes"), use_container_width=True)
        with col2:
            st.plotly_chart(language_bar(cmp, "total_items"), use_container_width=True)
        st.plotly_chart(accuracy_over_time(filtered), use_container_width=True)

with tab4:
    sl = lang_choice if lang_choice != "All" else None
    daily = activity_heatmap_data(filtered, sl)
    st.plotly_chart(github_heatmap(daily, f"activity — {lang_choice}"), use_container_width=True)
    st.caption("каждая ячейка = день, цвет = суммарное время занятий")

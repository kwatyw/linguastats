import pandas as pd
import numpy as np


def overall_retention(df):
    sub = df[df["source"] == "anki"]
    if len(sub) == 0:
        return 0.0
    return float(sub["accuracy"].mean())


def retention_by_language(df):
    sub = df[df["source"] == "anki"]
    res = sub.groupby("language")["accuracy"].mean().sort_values(ascending=False)
    return res


def streak_stats(df, lang=None):
    if lang:
        df = df[df["language"] == lang]
    days = sorted(df["date"].dt.date.unique())
    if not days:
        return {"current_streak": 0, "longest_streak": 0, "active_days": 0}

    longest = 1
    current = 1
    for i in range(1, len(days)):
        if (days[i] - days[i-1]).days == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1

    last_day = days[-1]
    today = pd.Timestamp.today().date()
    if (today - last_day).days > 1:
        current_active = 0
    else:
        current_active = current

    return {"current_streak": current_active, "longest_streak": longest, "active_days": len(days)}


def weekly_averages(df, lang=None):
    if lang:
        df = df[df["language"] == lang]
    tmp = df.copy()
    tmp["week"] = tmp["date"].dt.to_period("W").dt.start_time
    grouped = tmp.groupby("week").agg(
        items=("items", "sum"),
        duration=("duration_min", "sum"),
        accuracy=("accuracy", "mean"),
        xp=("xp_earned", "sum"),
    ).reset_index()
    return grouped


def compare_languages(df):
    res = df.groupby("language").agg(
        total_items=("items", "sum"),
        total_minutes=("duration_min", "sum"),
        avg_accuracy=("accuracy", "mean"),
        total_xp=("xp_earned", "sum"),
        active_days=("date", lambda x: x.dt.date.nunique()),
    ).round(2)
    res = res.sort_values("total_minutes", ascending=False)
    return res


def activity_heatmap_data(df, lang=None):
    if lang:
        df = df[df["language"] == lang]
    tmp = df.copy()
    tmp["d"] = tmp["date"].dt.date
    daily = tmp.groupby("d")["duration_min"].sum().reset_index()
    daily["d"] = pd.to_datetime(daily["d"])
    daily["weekday"] = daily["d"].dt.dayofweek
    daily["week"] = daily["d"].dt.isocalendar().week
    return daily

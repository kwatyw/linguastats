import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def progress_line(weekly_df, metric="items", title=None):
    fig = px.line(weekly_df, x="week", y=metric, markers=True, title=title or f"{metric} per week")
    fig.update_layout(height=350, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def language_bar(compare_df, metric="total_minutes"):
    tmp = compare_df.reset_index()
    fig = px.bar(tmp, x="language", y=metric, color="language", title=f"{metric} by language")
    fig.update_layout(height=350, showlegend=False, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def github_heatmap(daily_df, title="activity heatmap"):
    if len(daily_df) == 0:
        fig = go.Figure()
        fig.update_layout(title="no data")
        return fig

    daily_df = daily_df.copy()
    daily_df["d"] = pd.to_datetime(daily_df["d"])
    start = daily_df["d"].min()
    end = daily_df["d"].max()
    all_days = pd.date_range(start, end)
    full = pd.DataFrame({"d": all_days})
    full = full.merge(daily_df, on="d", how="left").fillna(0)
    full["weekday"] = full["d"].dt.dayofweek
    full["week_idx"] = ((full["d"] - start).dt.days // 7).astype(int)

    pivot = full.pivot_table(index="weekday", columns="week_idx", values="duration_min", fill_value=0)

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f"w{i}" for i in pivot.columns],
        y=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        colorscale="Greens",
        showscale=True,
        hovertemplate="%{y} %{x}<br>%{z:.0f} min<extra></extra>",
    ))
    fig.update_layout(title=title, height=300, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def accuracy_over_time(df, lang=None):
    tmp = df.copy()
    if lang:
        tmp = tmp[tmp["language"] == lang]
    tmp["week"] = tmp["date"].dt.to_period("W").dt.start_time
    g = tmp.groupby(["week", "language"])["accuracy"].mean().reset_index()
    fig = px.line(g, x="week", y="accuracy", color="language", markers=True, title="weekly accuracy")
    fig.update_layout(height=350, yaxis_tickformat=".0%", margin=dict(l=10, r=10, t=40, b=10))
    return fig

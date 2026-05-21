import pandas as pd
import json


def load_anki(path):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df["accuracy"] = df["correct"] / df["cards_reviewed"]
    df["source"] = "anki"
    out = df.rename(columns={
        "cards_reviewed": "items",
        "time_spent_min": "duration_min",
    })
    cols = ["date", "language", "source", "items", "accuracy", "duration_min", "deck_name"]
    return out[cols]


def load_duolingo(path):
    with open(path) as f:
        raw = json.load(f)

    rows = []
    for lang, info in raw["languages"].items():
        for s in info["sessions"]:
            rows.append({
                "date": s["date"],
                "language": lang,
                "source": "duolingo",
                "items": s["lessons_completed"],
                "accuracy": s["accuracy"],
                "duration_min": s["duration_min"],
                "xp_earned": s["xp_earned"],
            })
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def merge_sources(anki_df, duo_df):
    a = anki_df.copy()
    a["xp_earned"] = 0
    common = ["date", "language", "source", "items", "accuracy", "duration_min", "xp_earned"]
    df = pd.concat([a[common], duo_df[common]], ignore_index=True)
    df = df.sort_values("date").reset_index(drop=True)
    return df

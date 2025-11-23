# app/utils.py

import pandas as pd
from app.constants import SUBJECT_LABELS


def compute_basic_statistics(df: pd.DataFrame, subject: str) -> dict:
    """
    Tra ve cac thong ke co ban cho mot mon.
    """
    if subject not in df.columns:
        return {}

    series = df[subject].dropna()
    if series.empty:
        return {}

    stats = {
        "mean": float(series.mean()),
        "median": float(series.median()),
        "min": float(series.min()),
        "max": float(series.max()),
        "count": int(series.count()),
    }
    return stats


def format_stat_value(value: float, decimals: int = 2) -> str:
    return f"{value:.{decimals}f}"


def get_subject_label(subject: str) -> str:
    return SUBJECT_LABELS.get(subject, subject)

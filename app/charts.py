# app/charts.py

import pandas as pd
import plotly.express as px

from app.constants import SUBJECT_LABELS, DEFAULT_SUBJECT_ORDER, COMBINATIONS, COMBINATION_LABELS



def get_subject_label(subject: str) -> str:
    return SUBJECT_LABELS.get(subject, subject)


def create_histogram(df: pd.DataFrame, subject: str):
    label = get_subject_label(subject)
    fig = px.histogram(
        df,
        x=subject,
        nbins=40,
        title=f"Phân bố điểm môn {label}",
        labels={subject: f"Điểm môn {label}"},
        marginal="box",
    )
    fig.update_layout(
        xaxis_title=f"Điểm môn {label}",
        yaxis_title="T",
    )
    return fig


def create_boxplot_all_subjects(df: pd.DataFrame):
    """
    Boxplot so sanh cac mon.
    """
    cols = [c for c in DEFAULT_SUBJECT_ORDER if c in df.columns]
    if not cols:
        return None

    long_df = df[cols].melt(var_name="mon", value_name="diem")
    long_df["ten_mon"] = long_df["mon"].map(SUBJECT_LABELS)

    fig = px.box(
        long_df,
        x="ten_mon",
        y="diem",
        title="So sánh phân bố điểm giữa các môn",
        labels={"ten_mon": "Môn học", "diem": "Điểm"},
    )
    return fig


def create_bar_mean_by_province(stats_df: pd.DataFrame, subject: str, years: list[int]):
    """
    Bieu do cot diem trung binh theo tinh thanh.
    Su dung bang thong ke da tong hop san.
    """
    label = get_subject_label(subject)

    subset = stats_df[
        (stats_df["mon"] == subject)
        & (stats_df["nam"].isin(years))
    ].copy()

    if subset.empty:
        return None

    # Neu chon nhieu nam, lay trung binh diem trung binh
    group = (
        subset.groupby("tinh_thanh", dropna=False)["mean"]
        .mean()
        .reset_index()
        .sort_values("mean", ascending=False)
    )

    fig = px.bar(
        group,
        x="tinh_thanh",
        y="mean",
        title=f"Điểm trung bình môn{label} theo tỉnh thành",
        labels={"tinh_thanh": "Tỉnh thành", "mean": "Điểm trung bình"},
    )
    fig.update_layout(xaxis_tickangle=60)
    return fig


def create_scatter_for_combination(df: pd.DataFrame, combination_code: str):
    """
    Scatter 2D hoac 3D cho mot khoi to hop.
    Neu khoi co 2 mon thi ve scatter 2D, neu co 3 mon thi ve scatter 3D.
    """
    subjects = COMBINATIONS.get(combination_code)
    if not subjects:
        return None

    exist_subjects = [s for s in subjects if s in df.columns]
    if len(exist_subjects) < 2:
        return None

    labels = {s: get_subject_label(s) for s in exist_subjects}

    if len(exist_subjects) == 2:
        s1, s2 = exist_subjects
        fig = px.scatter(
            df,
            x=s1,
            y=s2,
            title=f"Biểu đồ điểm khối {combination_code}",
            labels={
                s1: f"Điểm {labels[s1]}",
                s2: f"Điểm {labels[s2]}",
            },
            opacity=0.6,
        )
        return fig

    if len(exist_subjects) >= 3:
        s1, s2, s3 = exist_subjects[:3]
        fig = px.scatter_3d(
            df,
            x=s1,
            y=s2,
            z=s3,
            title=f"Biểu đồ điểm khối {combination_code}",
            labels={
                s1: f"Điểm {labels[s1]}",
                s2: f"Điểm {labels[s2]}",
                s3: f"Điểm {labels[s3]}",
            },
            opacity=0.6,
        )
        return fig

    return None

# -*- coding: utf-8 -*-
# app/charts.py

import pandas as pd
import plotly.express as px

from app.constants import SUBJECT_LABELS, DEFAULT_SUBJECT_ORDER, COMBINATIONS, COMBINATION_LABELS


def get_subject_label(subject: str) -> str:
    return SUBJECT_LABELS.get(subject, subject)


def create_histogram(df: pd.DataFrame, subject: str):
    """
    Biểu đồ phân bố điểm theo một môn. Trục Y hiển thị Số thí sinh.
    Tooltip tiếng Việt.
    """
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
        yaxis_title="Số thí sinh",
    )
    # Việt hóa tooltip
    fig.update_traces(
        hovertemplate="Điểm %{x}<br>Số thí sinh = %{y:,}<extra></extra>"
    )
    return fig


def create_boxplot_all_subjects(df: pd.DataFrame):
    """
    Boxplot so sánh phân bố điểm giữa các môn.
    Tooltip tiếng Việt: Q1, Trung vị, Q3, Cận dưới, Cận trên.
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

    # Việt hóa tooltip boxplot
    fig.update_traces(
        selector=dict(type="box"),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Q1: %{q1:.2f}<br>"
            "Trung vị: %{median:.2f}<br>"
            "Q3: %{q3:.2f}<br>"
            "Cận dưới: %{lowerfence:.2f}<br>"
            "Cận trên: %{upperfence:.2f}"
            "<extra></extra>"
        ),
    )
    return fig


def create_bar_mean_by_province(stats_df: pd.DataFrame, subject: str, years: list[int]):
    """
    Biểu đồ cột điểm trung bình theo tỉnh/thành.
    Dùng bảng thống kê đã tổng hợp sẵn.
    """
    label = get_subject_label(subject)

    subset = stats_df[
        (stats_df["mon"] == subject) & (stats_df["nam"].isin(years))
    ].copy()
    if subset.empty:
        return None

    # Nếu chọn nhiều năm, lấy trung bình của "điểm trung bình"
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
        title=f"Điểm trung bình môn {label} theo tỉnh/thành",
        labels={"tinh_thanh": "Tỉnh/thành", "mean": "Điểm trung bình"},
    )
    fig.update_layout(xaxis_tickangle=60)
    # Tooltip tiếng Việt
    fig.update_traces(
        hovertemplate="Tỉnh/thành: %{x}<br>Điểm trung bình: %{y:.2f}<extra></extra>"
    )
    return fig


def create_scatter_for_combination(df: pd.DataFrame, combination_code: str):
    """
    Scatter 2D hoặc 3D cho một khối tổ hợp.
    Nếu khối có 2 môn thì vẽ scatter 2D, nếu có 3 môn thì vẽ scatter 3D.
    Tooltip tiếng Việt.
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
        fig.update_traces(
            hovertemplate=f"Điểm {labels[s1]}: "+"%{x:.2f}<br>"
                          f"Điểm {labels[s2]}: "+"%{y:.2f}<extra></extra>"
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
        fig.update_traces(
            hovertemplate=f"Điểm {labels[s1]}: "+"%{x:.2f}<br>"
                          f"Điểm {labels[s2]}: "+"%{y:.2f}<br>"
                          f"Điểm {labels[s3]}: "+"%{z:.2f}<extra></extra>"
        )
        return fig

    return None


def create_scatter_clusters(df: pd.DataFrame, subjects: list[str], cluster_col: str = "cum"):
    """
    Vẽ scatter tô màu theo cụm. Hỗ trợ 2D (2 môn) hoặc 3D (3 môn).
    Tooltip tiếng Việt, hiển thị nhãn cụm.
    """
    labs = {s: SUBJECT_LABELS.get(s, s) for s in subjects}
    title = "Phân cụm KMeans theo tổ hợp"

    if len(subjects) == 2:
        x, y = subjects
        fig = px.scatter(
            df,
            x=x, y=y,
            color=df[cluster_col].astype(str),
            labels={x: labs[x], y: labs[y], "color": "Cụm"},
            title=title,
            opacity=0.7,
        )
        fig.update_traces(
            hovertemplate="Cụm: %{marker.color}<br>"
                          f"{labs[x]}: "+"%{x:.2f}<br>"
                          f"{labs[y]}: "+"%{y:.2f}<extra></extra>"
        )
        return fig

    if len(subjects) >= 3:
        x, y, z = subjects[:3]
        fig = px.scatter_3d(
            df,
            x=x, y=y, z=z,
            color=df[cluster_col].astype(str),
            labels={x: labs[x], y: labs[y], z: labs[z], "color": "Cụm"},
            title=title,
            opacity=0.7,
        )
        fig.update_traces(
            hovertemplate="Cụm: %{marker.color}<br>"
                          f"{labs[x]}: "+"%{x:.2f}<br>"
                          f"{labs[y]}: "+"%{y:.2f}<br>"
                          f"{labs[z]}: "+"%{z:.2f}<extra></extra>"
        )
        return fig

    return None

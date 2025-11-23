# app/data_access.py

from typing import List, Optional, Tuple

import pandas as pd
import streamlit as st

from etl.config import MAIN_DATA_FILE, AGG_SUBJECT_PROVINCE_FILE
from app.constants import DEFAULT_SUBJECT_ORDER

@st.cache_data
def load_main_dataset() -> pd.DataFrame:
    """
    Doc du lieu diem thi da xu ly tu file Parquet.
    """
    if not MAIN_DATA_FILE.exists():
        raise RuntimeError(
            f"Khong tim thay file {MAIN_DATA_FILE}. Hay chay ETL truoc khi chay ung dung."
        )
    df = pd.read_parquet(MAIN_DATA_FILE)
    return df


@st.cache_data
def load_agg_subject_province() -> pd.DataFrame:
    """
    Doc bang thong ke diem tung mon theo tinh va nam tu file Parquet.
    """
    if not AGG_SUBJECT_PROVINCE_FILE.exists():
        raise RuntimeError(
            f"Khong tim thay file {AGG_SUBJECT_PROVINCE_FILE}. Hay chay ETL de tao thong ke."
        )
    df = pd.read_parquet(AGG_SUBJECT_PROVINCE_FILE)
    return df


def get_filter_options(df: pd.DataFrame) -> Tuple[List[int], List[str]]:
    years = sorted(df["nam"].dropna().unique().tolist())
    provinces = (
        df["tinh_thanh"]
        .dropna()
        .drop_duplicates()
        .sort_values()
        .tolist()
    )
    return years, provinces


def filter_main_dataset(
    df: pd.DataFrame,
    years: List[int],
    provinces: Optional[List[str]] = None,
) -> pd.DataFrame:
    filtered = df[df["nam"].isin(years)]
    if provinces:
        filtered = filtered[filtered["tinh_thanh"].isin(provinces)]
    return filtered


def sample_for_plotting(df: pd.DataFrame, max_rows: int = 100_000) -> pd.DataFrame:
    """
    Lay mau du lieu neu so dong qua lon de tranh lam cham giao dien.
    """
    if len(df) <= max_rows:
        return df
    return df.sample(n=max_rows, random_state=42)

# etl/build_aggregates.py

import pandas as pd

from .config import SUBJECT_COLUMNS, AGG_SUBJECT_PROVINCE_FILE, PROCESSED_DIR, MAIN_DATA_FILE


def load_main_data() -> pd.DataFrame:
    if not MAIN_DATA_FILE.exists():
        raise RuntimeError(
            f"Không tìm thấy file {MAIN_DATA_FILE}. Hãy chạy preprocess.build_all_years trước."
        )
    return pd.read_parquet(MAIN_DATA_FILE)


def build_subject_stats_by_province(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tao bang thong ke diem tung mon theo nam va tinh_thanh.
    """
    frames = []

    for mon in SUBJECT_COLUMNS:
        if mon not in df.columns:
            continue

        group = (
            df.groupby(["nam", "tinh_thanh"], dropna=False)[mon]
            .agg(["mean", "median", "min", "max", "count"])
            .reset_index()
        )
        group["mon"] = mon
        frames.append(group)

    if not frames:
        raise RuntimeError("Không có môn học nào để thống kê.")

    result = pd.concat(frames, ignore_index=True)
    return result


def run_build_aggregates():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df_all = load_main_data()
    stats_df = build_subject_stats_by_province(df_all)

    print(f"Lưu thống kê môn học theo tỉnh và năm vào {AGG_SUBJECT_PROVINCE_FILE}")
    stats_df.to_parquet(AGG_SUBJECT_PROVINCE_FILE, index=False)

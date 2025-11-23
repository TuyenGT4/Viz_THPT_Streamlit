# etl/preprocess.py

import pandas as pd
from pathlib import Path
from typing import Dict

from .config import RAW_FILES, SUBJECT_COLUMNS, COMBINATION_DEFINITIONS, PROCESSED_DIR, MAIN_DATA_FILE
from .province_mapping import extract_ma_tinh_from_sbd, get_tinh_thanh_from_sbd


def ensure_processed_dir():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_raw_year(path: Path, year: int) -> pd.DataFrame:
    """
    Đọc dữ liệu thô cho một năm.

    Dataset có thể có các cột như:
    sbd, toan, ngu_van, ngoai_ngu, vat_li, hoa_hoc, sinh_hoc,
    lich_su, dia_li, gdcd, ma_ngoai_ngu.
    """

    # Đọc file CSV (nếu dùng utf-8-sig thì thêm encoding vào)
    df = pd.read_csv(path, dtype=str)

#    chuẩn hóa tên cột (tránh lỗi do ký tự ẩn, viết hoa, khoảng trắng)
    # Ví dụ: " SBD " -> "sbd", "NGU VAN" -> "ngu_van"
    normalized_cols = []
    for c in df.columns:
        c_norm = (
            str(c)
            .strip()           # bỏ khoảng trắng đầu/cuối
            .replace("\ufeff", "")  # bỏ BOM nếu có
            .lower()           # chuyển thường
            .replace(" ", "_") # đổi khoảng trắng thành _
        )
        normalized_cols.append(c_norm)

    df.columns = normalized_cols

    # mapping tên cột đã chuẩn hóa -> tên cột chuẩn dùng trong hệ thống
    raw_to_standard_lower: Dict[str, str] = {
        "sbd": "sbd",
        "so_bao_danh": "sbd",
        "sobd": "sbd",
        "so_bd": "sbd",

        # Các môn
        "toan": "toan",
        "ngu_van": "van",
        "nguvan": "van",
        "ngoai_ngu": "anh",
        "ngoaingu": "anh",
        "vat_li": "ly",
        "vatli": "ly",
        "hoa_hoc": "hoa",
        "hoahoc": "hoa",
        "sinh_hoc": "sinh",
        "sinhhoc": "sinh",
        "lich_su": "su",
        "lichsu": "su",
        "dia_li": "dia",
        "diali": "dia",
        "gdcd": "gdcd",

        # Mã ngoại ngữ
        "ma_ngoai_ngu": "ma_ngoai_ngu",
        "mangoaingu": "ma_ngoai_ngu",
    }

    new_columns = {}
    for col in df.columns:
        if col in raw_to_standard_lower:
            new_columns[col] = raw_to_standard_lower[col]

    df = df.rename(columns=new_columns)

    # Đảm bảo có cột số báo danh chuẩn "sbd"
    if "sbd" not in df.columns:
        raise ValueError(
            f"File {path} không có cột số báo danh sau khi chuẩn hóa. "
            f"Các cột hiện có: {list(df.columns)}"
        )

    # Giữ lại các cột cần thiết: sbd, các môn và mã ngoại ngữ (nếu có)
    extra_cols = []
    if "ma_ngoai_ngu" in df.columns:
        extra_cols.append("ma_ngoai_ngu")

    from .config import SUBJECT_COLUMNS  # tránh import vòng nếu bạn đặt trên đầu file

    keep_cols = ["sbd"] + [c for c in SUBJECT_COLUMNS if c in df.columns] + extra_cols
    df = df[keep_cols]

    # Chuyển cột điểm sang float
    for col in SUBJECT_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", "."),
                errors="coerce",
            )

    # Loại bỏ điểm không hợp lệ (<0 hoặc >10)
    for col in SUBJECT_COLUMNS:
        if col in df.columns:
            df.loc[(df[col] < 0) | (df[col] > 10), col] = pd.NA

    # Thêm cột năm
    df["nam"] = year

    # Mã tỉnh và tên tỉnh từ số báo danh
    from .province_mapping import extract_ma_tinh_from_sbd, get_tinh_thanh_from_sbd

    df["ma_tinh"] = df["sbd"].apply(extract_ma_tinh_from_sbd)
    df["tinh_thanh"] = df["sbd"].apply(get_tinh_thanh_from_sbd)

    # Tính tổng điểm các khối
    from .config import COMBINATION_DEFINITIONS

    for code, subjects in COMBINATION_DEFINITIONS.items():
        exist_subjects = [s for s in subjects if s in df.columns]
        if not exist_subjects:
            continue
        df[f"tong_{code}"] = df[exist_subjects].sum(axis=1, skipna=False)

    # Tính điểm trung bình trên các môn có dữ liệu
    available_subjects = [c for c in SUBJECT_COLUMNS if c in df.columns]
    if available_subjects:
        df["diem_trung_binh"] = df[available_subjects].mean(axis=1, skipna=True)

    return df

def build_all_years() -> pd.DataFrame:
    ensure_processed_dir()
    all_dfs = []

    for year, path in RAW_FILES.items():
        if not path.exists():
            print(f"Cảnh báo: không tìm thấy file {path}, bỏ qua năm {year}")
            continue
        print(f"Xử lý dữ liệu năm {year} từ {path}")
        df_year = load_raw_year(path, year)
        all_dfs.append(df_year)

    if not all_dfs:
        raise RuntimeError("Không có dữ liệu nào được xử lý. Kiểm tra lại các file CSV.")

    df_all = pd.concat(all_dfs, ignore_index=True)

    print(f"Lưu dữ liệu tổng hợp vào {MAIN_DATA_FILE}")
    df_all.to_parquet(MAIN_DATA_FILE, index=False)

    return df_all

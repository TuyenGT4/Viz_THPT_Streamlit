# etl/config.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = BASE_DIR / "data_raw"
PROCESSED_DIR = BASE_DIR / "data_processed"

RAW_FILES = {
    2020: RAW_DIR / "thpt2020.csv",
    2021: RAW_DIR / "thpt2021.csv",
    2022: RAW_DIR / "thpt2022.csv",
    2023: RAW_DIR / "thpt2023.csv",
    2024: RAW_DIR / "thpt2024.csv",
}

# Danh sách môn với tên cột chuẩn hóa trong dữ liệu đã xử lý
SUBJECT_COLUMNS = [
    "toan",
    "van",
    "anh",
    "ly",
    "hoa",
    "sinh",
    "su",
    "dia",
    "gdcd",
]

# Định nghĩa các tổ hợp xét tuyển phổ biến
COMBINATION_DEFINITIONS = {
    "A00": ["toan", "ly", "hoa"],
    "A01": ["toan", "ly", "anh"],
    "B00": ["toan", "hoa", "sinh"],
    "C00": ["van", "su", "dia"],
    "D01": ["toan", "van", "anh"],
}

MAIN_DATA_FILE = PROCESSED_DIR / "diem_thpt_2020_2024.parquet"
AGG_SUBJECT_PROVINCE_FILE = PROCESSED_DIR / "thong_ke_mon_tinh_nam.parquet"

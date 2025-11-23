# app/constants.py

from etl.config import SUBJECT_COLUMNS, COMBINATION_DEFINITIONS

# Nhan tieng Viet cho cac mon
SUBJECT_LABELS = {
    "toan": "Toán",
    "van": "Ngữ văn",
    "anh": "Ngoại ngữ",
    "ly": "Vật lý",
    "hoa": "Hóa học",
    "sinh": "Sinh học",
    "su": "Lịch sử",
    "dia": "Địa lí",
    "gdcd": "Giáo dục công dân",
}

DEFAULT_SUBJECT_ORDER = [s for s in SUBJECT_COLUMNS if s in SUBJECT_LABELS]

COMBINATIONS = COMBINATION_DEFINITIONS

COMBINATION_LABELS = {
    "A00": "Khoi A00 Toan Ly Hoa",
    "A01": "Khoi A01 Toan Ly Anh",
    "B00": "Khoi B00 Toan Hoa Sinh",
    "C00": "Khoi C00 Van Su Dia",
    "D01": "Khoi D01 Toan Van Anh",
}

# etl/run_all.py

from .preprocess import build_all_years
from .build_aggregates import run_build_aggregates


def main():
    print("Bắt đầu xử lý dữ liệu điểm thi THPT Quốc Gia 202-2024")
    df_all = build_all_years()
    print(f"Đã xử lý xong {len(df_all)} bản ghi.")
    run_build_aggregates()
    print("Hoàn thành toàn bộ quy trình ETL.")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
# app/clustering.py

import pandas as pd
from typing import List, Tuple
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def kmeans_cluster(
    df: pd.DataFrame,
    subjects: List[str],
    n_clusters: int = 4,
    sample_size: int = 50000,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Chạy KMeans trên các cột 'subjects'. Trả về:
    - df_out: bản sao df có thêm cột 'cum' (nhãn cụm)
    - centers_df: tọa độ tâm cụm ở hệ gốc (đã inverse scale) để tham khảo
    """
    # Chỉ lấy các cột cần thiết và loại NA trên các môn
    use_cols = [c for c in subjects if c in df.columns]
    if len(use_cols) < 2:
        raise ValueError("Cần ít nhất hai môn để phân cụm.")

    work = df[use_cols].dropna().copy()
    if work.empty:
        raise ValueError("Không có dữ liệu hợp lệ để phân cụm.")

    # Lấy mẫu để tránh quá nặng
    if len(work) > sample_size:
        work = work.sample(n=sample_size, random_state=random_state)

    # Chuẩn hóa
    scaler = StandardScaler()
    X = scaler.fit_transform(work[use_cols].values)

    # KMeans
    km = KMeans(n_clusters=n_clusters, n_init=10, random_state=random_state)
    labels = km.fit_predict(X)

    # Gắn nhãn vào bản ghi tương ứng
    work = work.assign(cum=labels)

    # Tính tâm cụm theo thang đo gốc để đọc dễ hơn
    centers = scaler.inverse_transform(km.cluster_centers_)
    centers_df = pd.DataFrame(centers, columns=use_cols)
    centers_df["cum"] = range(n_clusters)

    # Gộp lại với df gốc để còn dùng các cột khác nếu cần
    df_out = df.merge(work[use_cols + ["cum"]], how="inner", on=use_cols)

    return df_out, centers_df

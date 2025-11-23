# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

from app.constants import (
    DEFAULT_SUBJECT_ORDER,
    SUBJECT_LABELS,
    COMBINATIONS,
    COMBINATION_LABELS,
)
from app.data_access import (
    load_main_dataset,
    load_agg_subject_province,
    get_filter_options,
    filter_main_dataset,
    sample_for_plotting,
)
from app.charts import (
    create_histogram,
    create_boxplot_all_subjects,
    create_bar_mean_by_province,
    create_scatter_for_combination,
    create_scatter_clusters,
)
from app.clustering import kmeans_cluster
from app.utils import compute_basic_statistics, format_stat_value, get_subject_label


def _init_selected_years(years: list[int]) -> list[int]:
    """Ưu tiên đọc từ URL (?years=2024 hoặc 2023,2024). Nếu không có thì chọn năm mới nhất."""
    latest_year = max(years) if years else None
    raw = st.query_params.get("years", "")
    try:
        from_url = [int(x) for x in raw.split(",") if x] if raw else []
    except Exception:
        from_url = []

    chosen = [y for y in from_url if y in years]
    if chosen:
        return chosen
    return [latest_year] if latest_year else []


def _persist_selected_years_to_url(selected_years: list[int]) -> None:
    """Ghi lựa chọn năm hiện tại lên URL để khi refresh vẫn giữ."""
    if selected_years:
        st.query_params["years"] = ",".join(map(str, selected_years))
    else:
        if "years" in st.query_params:
            del st.query_params["years"]


def main():
    st.set_page_config(
        page_title="Phân tích điểm thi THPT quốc gia",
        layout="wide",
    )

    st.title("Phân tích và trực quan hóa điểm thi THPT quốc gia 2020–2024")

    # Tải dữ liệu
    df = load_main_dataset()
    stats_df = load_agg_subject_province()
    years, provinces = get_filter_options(df)

    # Khởi tạo năm lần đầu: đọc từ URL, nếu không có thì chọn năm mới nhất
    if "selected_years" not in st.session_state:
        st.session_state["selected_years"] = _init_selected_years(years)

    # Sidebar bộ lọc
    with st.sidebar:
        st.header("Bộ lọc")

        # CHỌN NĂM: không đặt default để tránh cảnh báo.
        st.multiselect(
            "Chọn năm",
            options=years,
            key="selected_years",
            help="Lần đầu mặc định chọn năm mới nhất. Sau khi đổi sẽ được giữ khi refresh.",
        )
        _persist_selected_years_to_url(st.session_state["selected_years"])

        selected_provinces = st.multiselect(
            "Chọn tỉnh/thành",
            options=provinces,
            default=[],
            help="Để trống nếu muốn xem tất cả tỉnh/thành.",
        )

        subject_options = DEFAULT_SUBJECT_ORDER
        default_subject = subject_options[0] if subject_options else None

        selected_subject = st.selectbox(
            "Chọn môn",
            options=subject_options,
            index=0 if default_subject else 0,
            format_func=lambda x: SUBJECT_LABELS.get(x, x),
        )

        combination_codes = list(COMBINATIONS.keys())
        selected_combination = st.selectbox(
            "Chọn tổ hợp xét tuyển",
            options=combination_codes,
            format_func=lambda x: COMBINATION_LABELS.get(x, x),
        )

    if not st.session_state["selected_years"]:
        st.warning("Hãy chọn ít nhất một năm trong bộ lọc.")
        return

    # Lọc dữ liệu chính
    filtered_df = filter_main_dataset(
        df,
        years=st.session_state["selected_years"],
        provinces=selected_provinces,
    )

    if filtered_df.empty:
        st.warning("Không có bản ghi nào phù hợp với bộ lọc hiện tại.")
        return

    # Lấy mẫu dữ liệu phục vụ vẽ biểu đồ
    plot_df = sample_for_plotting(filtered_df)

    # Thống kê cơ bản
    st.subheader("Tổng quan dữ liệu")

    col1, col2, col3, col4 = st.columns(4)
    subject_label = get_subject_label(selected_subject)
    stats = compute_basic_statistics(filtered_df, selected_subject)

    if stats:
        col1.metric("Điểm trung bình", format_stat_value(stats["mean"]))
        col2.metric("Trung vị", format_stat_value(stats["median"]))
        col3.metric("Điểm thấp nhất", format_stat_value(stats["min"]))
        col4.metric("Điểm cao nhất", format_stat_value(stats["max"]))
    else:
        st.info("Không có dữ liệu điểm hợp lệ cho môn được chọn.")

    st.markdown(f"Dữ liệu hiện tại có {len(filtered_df)} thí sinh sau khi áp dụng bộ lọc.")

    # Tabs phân tích (giữ nguyên Tab 5 của bạn)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Phân bố điểm theo môn",
            "So sánh giữa các môn",
            "Theo tỉnh/thành",
            "Tổ hợp xét tuyển",
            "Phân cụm",
        ]
    )

    # Tab 1: Phân bố điểm theo môn
    with tab1:
        st.subheader(f"Phân bố điểm môn {subject_label}")
        fig_hist = create_histogram(plot_df, selected_subject)
        st.plotly_chart(fig_hist, use_container_width=True)

    # Tab 2: So sánh giữa các môn
    with tab2:
        st.subheader("So sánh phân bố điểm giữa các môn")
        fig_box = create_boxplot_all_subjects(plot_df)
        if fig_box is not None:
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("Không đủ dữ liệu các môn để vẽ biểu đồ.")

    # Tab 3: Theo tỉnh/thành
    with tab3:
        st.subheader(f"Điểm trung bình môn {subject_label} theo tỉnh/thành")
        fig_bar = create_bar_mean_by_province(
            stats_df=stats_df,
            subject=selected_subject,
            years=st.session_state["selected_years"],
        )
        if fig_bar is not None:
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Không có dữ liệu thống kê theo tỉnh/thành cho môn được chọn.")

    # Tab 4: Tổ hợp xét tuyển
    with tab4:
        st.subheader(f"Biểu đồ điểm tổ hợp {selected_combination}")
        fig_scatter = create_scatter_for_combination(plot_df, selected_combination)
        if fig_scatter is not None:
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Không đủ môn thành phần hoặc không đủ dữ liệu để vẽ biểu đồ tổ hợp.")

    # Tab 5: Phân cụm KMeans
    with tab5:
        st.subheader("Phân cụm KMeans theo tổ hợp đang chọn")

        subjects = COMBINATIONS.get(selected_combination, [])
        exist_subjects = [s for s in subjects if s in filtered_df.columns]

        if len(exist_subjects) < 2:
            st.info("Cần ít nhất hai môn trong tổ hợp để phân cụm.")
        else:
            n_clusters = st.number_input("Số cụm", min_value=2, max_value=10, value=4, step=1)
            sample_size = st.number_input(
                "Số mẫu tối đa để phân cụm", min_value=1000, max_value=200000, value=50000, step=1000
            )

            try:
                clustered_df, centers_df = kmeans_cluster(
                    plot_df,
                    subjects=exist_subjects,
                    n_clusters=int(n_clusters),
                    sample_size=int(sample_size),
                )
                fig_c = create_scatter_clusters(clustered_df, exist_subjects, cluster_col="cum")
                if fig_c is not None:
                    st.plotly_chart(fig_c, use_container_width=True)

                counts = clustered_df["cum"].value_counts().sort_index()
                st.write("Số lượng trong từng cụm:")
                st.table(pd.DataFrame({"Cụm": counts.index, "Số thí sinh": counts.values}))

                st.write("Tọa độ tâm cụm (theo thang điểm gốc):")
                show_centers = centers_df.rename(columns={c: SUBJECT_LABELS.get(c, c) for c in centers_df.columns})
                st.table(show_centers)
            except Exception as e:
                st.warning(f"Không thể phân cụm: {e}")


if __name__ == "__main__":
    main()

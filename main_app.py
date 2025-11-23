# -*- coding: utf-8 -*-
import streamlit as st

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
)
from app.utils import compute_basic_statistics, format_stat_value, get_subject_label


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

    # Sidebar bộ lọc
    with st.sidebar:
        st.header("Bộ lọc")

        selected_years = st.multiselect(
            "Chọn năm",
            options=years,
            default=years,
        )

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

    if not selected_years:
        st.warning("Hãy chọn ít nhất một năm trong bộ lọc.")
        return

    # Lọc dữ liệu chính
    filtered_df = filter_main_dataset(df, years=selected_years, provinces=selected_provinces)

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

    st.markdown(
        f"Dữ liệu hiện tại có {len(filtered_df)} thí sinh sau khi áp dụng bộ lọc."
    )

    # Tabs phân tích
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Phân bố điểm theo môn",
            "So sánh giữa các môn",
            "Theo tỉnh/thành",
            "Tổ hợp xét tuyển",
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
            years=selected_years,
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
            st.info(
                "Không đủ môn thành phần hoặc không đủ dữ liệu để vẽ biểu đồ tổ hợp."
            )


if __name__ == "__main__":
    main()

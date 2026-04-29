import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
from config import (
    MAJOR_NAMES,
    get_features,
    get_display_names,
    DEFAULT_KHTN,
    DEFAULT_KHXH,
    NGANH_HOC_DESCRIPTION,
    get_majors,
)
from hybrid_fusion import (
    get_hybrid_ranking, load_ml_model
)

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cấu hình Streamlit
st.set_page_config(
    page_title="Hybrid Suggest Career System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tối ưu
st.markdown("""
<style>
    .main { padding: 1rem 0; }
    .metric-card { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
    }
    .app-header {
        background: linear-gradient(135deg, rgba(102,126,234,.25) 0%, rgba(118,75,162,.25) 100%);
        border: 1px solid rgba(118,75,162,.25);
        border-radius: 12px;
        padding: 1.25rem 1.25rem;
        margin-bottom: 0.75rem;
    }
    .app-subheader {
        color: rgba(255,255,255,.95);
        font-size: 0.95rem;
        margin-top: 0.25rem;
    }
    .section-title {
        font-weight: 700;
        letter-spacing: 0.2px;
    }
    .pill {
        display: inline-block;
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        background: rgba(102,126,234,.15);
        border: 1px solid rgba(102,126,234,.25);
        margin-right: .4rem;
        margin-top: .2rem;
        font-size: .85rem;
    }
</style>
""", unsafe_allow_html=True)

# --- STREAMLIT CACHE OPTIMIZATIONS ---
@st.cache_resource
def get_model(block: str):
    """Cache Random Forest model theo khối."""
    return load_ml_model(block)

# --- INITIALIZE SESSION STATE & VARIABLES ---
if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_block_label" not in st.session_state:
    st.session_state.selected_block_label = "KHTN"

# Khởi tạo các button variables
analyze_btn = False
check_all_btn = False

# Khởi tạo map điểm (được tạo động theo khối ở sidebar)
scores_map = {}

# --- HEADER ---
col1, col2 = st.columns([0.9, 0.1])
with col1:
    st.title(" Hybrid Suggest Career System")
    st.markdown("*Hệ thống gợi ý ngành học lai*")

with col2:
    if st.button("Home", help="Quay lại trang chủ", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

st.divider()

# --- SIDEBAR: INPUT SCORES ---
with st.sidebar:
    st.header("Nhập thông tin")
    st.radio(
        "Chọn khối",
        ["KHTN", "KHXH"],
        key="selected_block_label",
        horizontal=True,
    )
    block = 'khtn' if st.session_state.selected_block_label == 'KHTN' else 'khxh'
    
    # Nếu ở trang home, hiển thị nút bắt đầu
    if st.session_state.page == "home":
        if st.button("Bắt đầu phân tích", use_container_width=True, key="start_btn"):
            st.session_state.page = "analyze"
            st.rerun()
        
        st.info("""
        **Tính năng:**
        - Dự đoán ngành học phù hợp
        - Phân tích chi tiết điểm số
        - So sánh các ngành trong khối (KHTN: 5 ngành, KHXH: 4 ngành)
        - Khuyến nghị dựa trên AI
        """)
    
    else:  # Trang phân tích
        st.subheader("Điểm số các môn (0-10)")
        feature_names = get_features(block)
        display_map = get_display_names(block)
        defaults = DEFAULT_KHTN if block == 'khtn' else DEFAULT_KHXH

        col1, col2 = st.columns(2)
        for idx, feat in enumerate(feature_names):
            slider_col = col1 if idx % 2 == 0 else col2
            with slider_col:
                scores_map[feat] = st.slider(
                    display_map[feat],
                    0.0,
                    10.0,
                    float(defaults[feat]),
                    step=0.25,
                    key=f"{block}_{feat}",
                )
        
        st.divider()
        
        # Button phân tích
        col1, col2 = st.columns(2)
        with col1:
            analyze_btn = st.button("Phân tích", use_container_width=True)
        with col2:
            check_all_btn = st.button("Xem tất cả ngành", use_container_width=True)

# --- MAIN CONTENT ---
if st.session_state.page == "home":
    # === TRANG CHỦ (HOME PAGE) ===
    st.markdown("""
    <div class="app-header">
        <div class="section-title" style="font-size:1.6rem; color: rgba(255,255,255,.98)">Hybrid Suggest Career System</div>
        <div class="app-subheader">Kết hợp luật chuyên gia (KBS) + mô hình ML để gợi ý ngành phù hợp theo khối xét tuyển.</div>
        <div style="margin-top:.65rem">
            <span class="pill">KHTN • 6 môn • 5 ngành</span>
            <span class="pill">KHXH • 6 môn • 4 ngành</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Thông tin hệ thống
    
    st.divider()
    
    def build_major_df(block: str) -> pd.DataFrame:
        rows = []
        for major_idx in get_majors(block):
            info = NGANH_HOC_DESCRIPTION[int(major_idx)]
            rows.append(
                {
                    "Ngành": info["name"],
                    "Ưu tiên": ", ".join(info.get("keywords", [])),
                    "Mô tả": info.get("description", ""),
                }
            )
        return pd.DataFrame(rows)

    st.subheader("Các ngành theo khối xét tuyển")
    col_khtn, col_khxh = st.columns(2)
    with col_khtn:
        st.markdown("#### KHTN")
        st.dataframe(build_major_df("khtn"), use_container_width=True, hide_index=True)
    with col_khxh:
        st.markdown("#### KHXH")
        st.dataframe(build_major_df("khxh"), use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Hướng dẫn
    st.subheader("Cách Sử Dụng")
    st.markdown("""
    ### Bước 1: Bắt đầu
    Nhấn nút **"Bắt đầu phân tích"** ở sidebar
    
    ### Bước 2: Nhập Điểm Số
    Điều chỉnh thanh slider cho 6 môn học:
    - KHTN: Toán, Văn, Anh, Lý, Hóa, Sinh
    - KHXH: Toán, Văn, Anh, Sử, Địa, GDCD
    
    ### Bước 3: Phân Tích
    Chọn:
    - **Phân tích**: Xem kết quả chi tiết cho một ngành
    - **Xem tất cả ngành**: So sánh các ngành trong khối đang chọn
    
    ### Bước 4: Xem Kết Quả
    Nhận được:
    - Điểm khuyến nghị
    - Bảng phân tích
    - Biểu đồ so sánh
    """)
    
    st.divider()
    
    # Công nghệ
    

elif st.session_state.page == "analyze":
    # === TRANG PHÂN TÍCH (ANALYSIS PAGE) ===
    if analyze_btn:
        feature_names = get_features(block)
        display_map = get_display_names(block)
        user_scores = [scores_map[feat] for feat in feature_names]
        
        # Validate model
        model = get_model(block)
        if model is None:
            st.error("Lỗi: Không thể tải mô hình ML. Vui lòng chạy train_model.py trước!")
            st.stop()
        
        # Lấy xếp hạng tất cả ngành và tìm ngành phù hợp nhất
        all_rankings = get_hybrid_ranking(user_scores, block=block, model=model)
        best_major = all_rankings[0]
        
        score = best_major['hybrid_score']
        explanation = best_major['explanation']
        ml_score = best_major['ml_score']
        major_name = best_major['major']
        
        # Tab 1: Kết quả chính
        tab1, tab2, tab3 = st.tabs(["Kết quả chính", "Phân tích chi tiết", "So sánh ngành"])
        
        with tab1:
            st.header("Kết quả Phân Tích")
            
            if score is not None:
                # "Top pick" card
                level = "Rất phù hợp" if score >= 75 else "Khá phù hợp" if score >= 50 else "Không phù hợp"
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div style="font-size:1.05rem; font-weight:700">Ngành đề xuất: {major_name}</div>
                        <div class="app-subheader" style="color: rgba(255,255,255,.98); margin-top:.35rem">
                            Hybrid Score: <b>{score:.1f}%</b> • {level}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.divider()

                # Hiển thị các metrics chính (reuse best_major từ all_rankings)
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Ngành được chọn", major_name)
                
                with col2:
                    color_hybrid = "Good" if score >= 75 else "Fair" if score >= 50 else "Low"
                    st.metric("Hybrid Score", f"{score:.1f}%", delta=color_hybrid)
                
                with col3:
                    ml_score_display = f"{ml_score:.1f}%" if ml_score is not None else "N/A"
                    st.metric("ML Score", ml_score_display)
                
                with col4:
                    st.metric("KBS Score", f"{best_major['kbs_score']:.1f}%")
                
                with col5:
                    st.metric("Mức độ khuyến nghị", level)
                
                st.divider()
                
                # Giải thích chi tiết
                st.subheader("Giải thích chi tiết")
                st.info(explanation)
            else:
                st.error("Có lỗi xảy ra trong quá trình phân tích. Vui lòng thử lại!")
        
        with tab2:
            st.header("Phân Tích Chi Tiết")
            
            # Radar Chart điểm các môn
            subjects = [display_map[feat] for feat in feature_names]
            df_radar = pd.DataFrame({
                'Điểm': user_scores,
                'Môn': subjects
            })
            
            fig_radar = px.line_polar(
                df_radar,
                r='Điểm',
                theta='Môn',
                line_close=True,
                title="Radar Chart Điểm Số Các Môn",
                markers=True
            )
            fig_radar.update_traces(fill='toself')
            fig_radar.update_layout(height=500)
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # Bảng thống kê
            st.subheader("Bảng Thống Kê")
            stats_df = pd.DataFrame({
                'Môn học': subjects,
                'Điểm': user_scores,
                'Xếp hạng': [
                    'Rất tốt' if s >= 8 else 'Tốt' if s >= 6 else 'Bình thường' if s >= 4 else 'Cần cải thiện'
                    for s in user_scores
                ]
            })
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
        with tab3:
            st.header("So Sánh Các Ngành")
            
            # Reuse all_rankings (đã tính ở trên, không gọi lại)
            hybrid_rankings = all_rankings
            ranking_df = pd.DataFrame(hybrid_rankings)
            
            # Biểu đồ so sánh (Hybrid, ML, KBS)
            st.subheader("Biểu đồ So Sánh - Hybrid vs ML vs KBS")
            fig_hybrid_compare = go.Figure(data=[
                go.Bar(name='Hybrid Score', x=ranking_df['major'], y=ranking_df['hybrid_score'], marker_color='indianred'),
                go.Bar(name='ML Score', x=ranking_df['major'], y=ranking_df['ml_score'], marker_color='lightsalmon'),
                go.Bar(name='KBS Score', x=ranking_df['major'], y=ranking_df['kbs_score'], marker_color='lightgreen')
            ])
            fig_hybrid_compare.update_layout(
                barmode='group',
                title='Xếp hạng các ngành: Hybrid vs ML vs KBS',
                xaxis_title='Ngành học',
                yaxis_title='Điểm (%)',
                height=400,
                hovermode='x unified'
            )
            fig_hybrid_compare.update_xaxes(tickangle=-25)
            st.plotly_chart(fig_hybrid_compare, use_container_width=True)
            
            st.divider()
            
            # Bảng chi tiết
            st.subheader("Chi tiết Xếp Hạng - HYBRID")
            st.caption("Hybrid = 60% ML + 40% KBS - Đây là kết quả được khuyên dùng")
            
            # Tạo bảng so sánh
            comparison_data = []
            for idx, result in enumerate(hybrid_rankings, 1):
                comparison_data.append({
                    'Rank': idx,
                    'Ngành': result['major'],
                    'Hybrid': f"{result['hybrid_score']:.1f}%",
                    'ML Score': f"{result['ml_score']:.1f}%" if result['ml_score'] is not None else "N/A",
                    'KBS Score': f"{result['kbs_score']:.1f}%",
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Chi tiết từng ngành
            st.subheader("Chi Tiết Từng Ngành")
            for idx, result in enumerate(hybrid_rankings, 1):
                ml_score_display = f"{result['ml_score']:.1f}%" if result['ml_score'] is not None else "N/A"
                with st.expander(f"#{idx} {result['major']} - Hybrid: {result['hybrid_score']:.1f}% | ML: {ml_score_display} | KBS: {result['kbs_score']:.1f}%"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Hybrid Score", f"{result['hybrid_score']:.1f}%")
                    with col2:
                        st.metric("ML Score", f"{result['ml_score']:.1f}%" if result['ml_score'] is not None else "N/A")
                    with col3:
                        st.metric("KBS Score", f"{result['kbs_score']:.1f}%")
                    st.info(result['explanation'])
        
    elif check_all_btn:
        st.header("Xếp Hạng Tất Cả Ngành")
        
        feature_names = get_features(block)
        user_scores = [scores_map[feat] for feat in feature_names]
        
        # Validate model
        model = get_model(block)
        if model is None:
            st.error("Lỗi: Không thể tải mô hình ML!")
            st.stop()
        
        # Lấy xếp hạng hybrid tất cả ngành
        hybrid_rankings = get_hybrid_ranking(user_scores, block=block, model=model)
        
        # Hiển thị tất cả ngành từ trên xuống
        for idx, result in enumerate(hybrid_rankings, 1):
            hs = result['hybrid_score']
            level = "Rất phù hợp" if hs >= 75 else "Khá phù hợp" if hs >= 50 else "Không phù hợp"
            ml_display = f"{result['ml_score']:.1f}%" if result['ml_score'] is not None else "N/A"
            
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([0.3, 1.5, 0.8, 0.8, 0.8])
                with col1:
                    st.markdown(f"### #{idx}")
                with col2:
                    st.markdown(f"### {result['major']}")
                with col3:
                    st.metric("Hybrid", f"{hs:.1f}%")
                with col4:
                    st.metric("ML", ml_display)
                with col5:
                    st.metric("KBS", f"{result['kbs_score']:.1f}%")
                
                st.caption(f"Mức độ: **{level}**")
                st.divider()
    
    else:
        # Khi đang ở trang phân tích nhưng chưa nhấn nút
        st.info("Nhập điểm số các môn rồi nhấn **Phân tích** hoặc **Xem tất cả ngành** để bắt đầu!")

# --- FOOTER ---
st.divider()
st.markdown("""

""", unsafe_allow_html=True)
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
from hybrid_engine import (
    get_hybrid_advice, get_all_majors_ranking, NGANH_HOC_MAP
)
from hybrid_fusion import (
    calculate_hybrid_score, get_hybrid_ranking, load_ml_model
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
</style>
""", unsafe_allow_html=True)

# --- STREAMLIT CACHE OPTIMIZATIONS ---
@st.cache_resource
def get_model():
    """Cache mô hình ML"""
    from hybrid_engine import load_model
    return load_model()

@st.cache_resource
def get_hybrid_model():
    """Cache Random Forest model cho hybrid_fusion"""
    return load_ml_model()

# --- INITIALIZE SESSION STATE & VARIABLES ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# Khởi tạo các button variables
analyze_btn = False
check_all_btn = False

# Khởi tạo input scores
s_toan = 8
s_ly = 7
s_hoa = 6
s_sinh = 7
s_van = 5
s_anh = 8
s_lich_su = 6
s_dia_ly = 6
s_tin = 9

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
    
    # Nếu ở trang home, hiển thị nút bắt đầu
    if st.session_state.page == "home":
        if st.button("Bắt đầu phân tích", use_container_width=True, key="start_btn"):
            st.session_state.page = "analyze"
            st.rerun()
        
        st.info("""
        **Tính năng:**
        - Dự đoán ngành học phù hợp
        - Phân tích chi tiết điểm số
        - So sánh 8 ngành khác nhau
        - Khuyến nghị dựa trên AI
        """)
    
    else:  # Trang phân tích
        st.subheader("Điểm số các môn (0-10)")
        col1, col2 = st.columns(2)
        
        with col1:
            s_toan = st.slider("Toán", 0, 10, 8, key="toan")
            s_ly = st.slider("Lý", 0, 10, 7, key="ly")
            s_hoa = st.slider("Hóa", 0, 10, 6, key="hoa")
            s_sinh = st.slider("Sinh", 0, 10, 7, key="sinh")
            s_van = st.slider("Văn", 0, 10, 5, key="van")
        
        with col2:
            s_anh = st.slider("Anh", 0, 10, 8, key="anh")
            s_lich_su = st.slider("Lịch sử", 0, 10, 6, key="lich_su")
            s_dia_ly = st.slider("Địa lý", 0, 10, 6, key="dia_ly")
            s_tin = st.slider("Tin học", 0, 10, 9, key="tin")
        
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
    # Hệ Thống Gợi ý Ngành Học Thông Minh
    
    Với công nghệ AI hiện đại, chúng tôi giúp bạn tìm ra ngành học phù hợp nhất 
    dựa trên điểm số và khả năng của bạn.
    """)
    
    # Thông tin hệ thống
    
    st.divider()
    
    # Hiển thị thông tin ngành
    st.subheader("Các Ngành Học Được Hỗ Trợ")
    major_info = pd.DataFrame([
        {"Ngành": "IT - Công nghệ thông tin", "Ưu tiên": "Toán, Lý, Tin học", "Mô tả": "Phát triển phần mềm, AI, An ninh"},
        {"Ngành": "Kinh tế - Kinh doanh", "Ưu tiên": "Toán, Anh, Văn", "Mô tả": "Quản lý, Kế toán, Tiếp thị"},
        {"Ngành": "Y khoa - Sức khỏe", "Ưu tiên": "Sinh, Hóa, Lý", "Mô tả": "Bác sĩ, Điều dưỡng, Dược sĩ"},
        {"Ngành": "Kỹ thuật - Xây dựng", "Ưu tiên": "Toán, Lý, Tin", "Mô tả": "Xây dựng, Cơ khí, Điện"},
        {"Ngành": "Nông - Lâm - Ngư", "Ưu tiên": "Sinh, Địa lý, Hóa", "Mô tả": "Nông nghiệp, Lâm nghiệp"},
        {"Ngành": "Sư phạm - Giáo dục", "Ưu tiên": "Văn, Anh, Lịch sử", "Mô tả": "Dạy học, Quản lý giáo dục"},
        {"Ngành": "Luật pháp", "Ưu tiên": "Lịch sử, Văn, Anh", "Mô tả": "Luật sư, Công tố viên"},
        {"Ngành": "Du lịch - Khách sạn", "Ưu tiên": "Địa lý, Anh, Văn", "Mô tả": "Hướng dẫn, Quản lý khách sạn"},
    ])
    st.dataframe(major_info, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Hướng dẫn
    st.subheader("Cách Sử Dụng")
    st.markdown("""
    ### Bước 1: Bắt đầu
    Nhấn nút **"Bắt đầu phân tích"** ở sidebar
    
    ### Bước 2: Nhập Điểm Số
    Điều chỉnh thanh slider cho 9 môn học:
    - Toán, Lý, Hóa, Sinh
    - Văn, Anh, Lịch sử, Địa lý, Tin học
    
    ### Bước 3: Phân Tích
    Chọn:
    - **Phân tích**: Xem kết quả chi tiết cho một ngành
    - **Xem tất cả ngành**: So sánh tất cả 8 ngành
    
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
        user_scores = [s_toan, s_ly, s_hoa, s_sinh, s_van, s_anh, s_lich_su, s_dia_ly, s_tin]
        
        # Validate model
        model = get_model()
        if model is None:
            st.error("Lỗi: Không thể tải mô hình ML. Vui lòng chạy train_model.py trước!")
            st.stop()
        
        # Lấy xếp hạng tất cả ngành và tìm ngành phù hợp nhất (sử dụng interest cố định 5.0)
        all_rankings = get_all_majors_ranking(user_scores)
        best_major = max(all_rankings, key=lambda x: (x['score'], x.get('relevance_score', 0)))
        
        score = best_major['score']
        explanation = best_major['explanation']
        ml_score = best_major['ml_score']
        major_name = best_major['major']
        
        # Tìm index của ngành được chọn từ hybrid_fusion
        from hybrid_fusion import MAJOR_NAMES
        try:
            best_major_index = MAJOR_NAMES.index(major_name)
        except ValueError:
            best_major_index = 0  # Fallback to IT if not found
        
        # Tab 1: Kết quả chính
        tab1, tab2, tab3 = st.tabs(["Kết quả chính", "Phân tích chi tiết", "So sánh ngành"])
        
        with tab1:
            st.header("Kết quả Phân Tích")
            
            if score is not None:
                # === BƯỚC 1: TÍNH HYBRID SCORE ===
                model = get_hybrid_model()
                hybrid_result = calculate_hybrid_score(user_scores, major_index=best_major_index, model=model)
                
                # Hiển thị các metrics chính
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Ngành được chọn", major_name)
                
                with col2:
                    color_hybrid = "Good" if hybrid_result['hybrid_score'] >= 75 else "Fair" if hybrid_result['hybrid_score'] >= 50 else "Low"
                    st.metric("Hybrid Score", f"{hybrid_result['hybrid_score']:.1f}%", delta=color_hybrid)
                
                with col3:
                    ml_score_display = f"{hybrid_result['ml_score']:.1f}%" if hybrid_result['ml_score'] is not None else "N/A"
                    st.metric("ML Score", ml_score_display)
                
                with col4:
                    st.metric("KBS Score", f"{hybrid_result['kbs_score']:.1f}%")
                
                with col5:
                    hs = hybrid_result['hybrid_score']
                    level = "Rất phù hợp" if hs >= 75 else "Khá phù hợp" if hs >= 50 else "Không phù hợp"
                    st.metric("Mức độ khuyến nghị", level)
                
                st.divider()
                
                # Giải thích chi tiết
                st.subheader("Giải thích chi tiết")
                st.info(hybrid_result['explanation'])
            else:
                st.error("Có lỗi xảy ra trong quá trình phân tích. Vui lòng thử lại!")
        
        with tab2:
            st.header("Phân Tích Chi Tiết")
            
            # Radar Chart điểm các môn
            df_radar = pd.DataFrame({
                'Điểm': user_scores,
                'Môn': ['Toán', 'Lý', 'Hóa', 'Sinh', 'Văn', 'Anh', 'Lịch sử', 'Địa lý', 'Tin học']
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
                'Môn học': ['Toán', 'Lý', 'Hóa', 'Sinh', 'Văn', 'Anh', 'Lịch sử', 'Địa lý', 'Tin học'],
                'Điểm': user_scores,
                'Xếp hạng': [
                    'Rất tốt' if s >= 8 else 'Tốt' if s >= 6 else 'Bình thường' if s >= 4 else 'Cần cải thiện'
                    for s in user_scores
                ]
            })
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
        with tab3:
            st.header("So Sánh Các Ngành")
            
            # === BƯỚC 2: TÍNH HYBRID RANKING CHO TẤT CẢ NGÀNH ===
            model = get_hybrid_model()
            hybrid_rankings = get_hybrid_ranking(user_scores, model=model)
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
            st.plotly_chart(fig_hybrid_compare, use_container_width=True)
            
            st.divider()
            
            # Lấy ranking từ hybrid_engine (cũ) để so sánh
            rankings = get_all_majors_ranking(user_scores)
            
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
        st.header("Top 4 Ngành Phù Hợp Nhất")
        
        user_scores = [s_toan, s_ly, s_hoa, s_sinh, s_van, s_anh, s_lich_su, s_dia_ly, s_tin]
        
        # Validate model
        model = get_model()
        if model is None:
            st.error("Lỗi: Không thể tải mô hình ML!")
            st.stop()
        
        # Lấy xếp hạng tất cả ngành
        rankings = get_all_majors_ranking(user_scores)
        
        # Sắp xếp theo score giảm dần và lấy top 4
        top_4 = sorted(rankings, key=lambda x: (x['score'], x.get('relevance_score', 0)), reverse=True)[:4]
        
        # Hiển thị top 4 ngành từ trên xuống
        for idx, result in enumerate(top_4, 1):
            medal = ['#1', '#2', '#3', '#4'][idx-1]
            with st.container():
                col1, col2, col3 = st.columns([0.5, 2, 1])
                with col1:
                    st.markdown(f"# {medal}")
                with col2:
                    st.markdown(f"### {result['major']}")
                with col3:
                    st.markdown(f"### {result['score']:.1f}%")
                
                st.info(result['explanation'])
                st.divider()
    
    else:
        # Khi đang ở trang phân tích nhưng chưa nhấn nút
        st.info("Nhập điểm số các môn rồi nhấn **Phân tích** hoặc **Xem tất cả ngành** để bắt đầu!")

# --- FOOTER ---
st.divider()
st.markdown("""

""", unsafe_allow_html=True)
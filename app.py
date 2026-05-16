import streamlit as st
import pandas as pd
import plotly.express as px
import logging

from config import (
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

    /* Hide slider min/max labels (e.g. 0.00 / 10.00) */
    div[data-testid="stSlider"] [data-testid="stTickBarMin"],
    div[data-testid="stSlider"] [data-testid="stTickBarMax"] {
        display: none !important;
    }
    /* Fallbacks for other Streamlit/BaseWeb versions */
    div[data-testid="stSlider"] [data-testid="stTickBar"] {
        display: none !important;
    }
    /* Often the min/max labels sit in the element right after the baseweb slider */
    div[data-testid="stSlider"] div[data-baseweb="slider"] + div {
        display: none !important;
    }
    /* Another common layout: last child under slider root is the label row */
    div[data-testid="stSlider"] > div:has(div[data-baseweb="slider"]) > div:last-child {
        display: none !important;
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
        - Dự đoán ngành học phù hợp (hybrid ML + KBS)
        - Phân tích chi tiết điểm số (radar + bảng môn)
        - Giải thích và chuỗi suy luận KBS cho ngành đề xuất
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
        
        analyze_btn = st.button("Phân tích", use_container_width=True)

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
    Nhấn **Phân tích** để xem ngành đề xuất, điểm hybrid / ML / KBS và giải thích.
    
    ### Bước 4: Xem Kết Quả
    Nhận được:
    - Điểm khuyến nghị và mức độ phù hợp
    - Tab phân tích chi tiết (radar, bảng môn)
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
        
        # Lấy xếp hạng tất cả ngành và lấy top 4 ngành phù hợp nhất
        all_rankings = get_hybrid_ranking(user_scores, block=block, model=model)
        top_majors = all_rankings[:4]  # KHTN: 4/5, KHXH: 4/4
        best_major = top_majors[0]

        score = best_major['hybrid_score']
        explanation = best_major['explanation']
        ml_score = best_major['ml_score']
        major_name = best_major['major']

        def _level(s: float) -> str:
            return "Rất phù hợp" if s >= 75 else "Khá phù hợp" if s >= 50 else "Không phù hợp"

        def _fmt_ml_cell(m: dict) -> str:
            """ml_score = xác suất RF thô × 100."""
            ms = m.get("ml_score")
            return "N/A" if ms is None else f"{ms:.1f}%"

        tab1, tab2 = st.tabs(["Kết quả chính", "Phân tích chi tiết"])

        with tab1:
            st.header("Kết quả Phân Tích")

            if score is not None:
                # "Top pick" card (ngành #1)
                level = _level(score)
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

                # Hiển thị các metrics chính cho ngành top-1
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Ngành được chọn", major_name)
                with col2:
                    color_hybrid = "Good" if score >= 75 else "Fair" if score >= 50 else "Low"
                    st.metric(
                        "Hybrid Score",
                        f"{score:.1f}%",
                        delta=color_hybrid,
                        delta_color="off",
                    )
                with col3:
                    ml_score_display = f"{ml_score:.1f}%" if ml_score is not None else "N/A"
                    st.metric("ML Score", ml_score_display)
                with col4:
                    st.metric("KBS Score", f"{best_major['kbs_score']:.1f}%")
                with col5:
                    st.metric("Mức độ khuyến nghị", level)
                st.divider()

                # === TOP 4 ngành phù hợp nhất ===
                st.subheader(f"Top {len(top_majors)} ngành phù hợp nhất")
                summary_df = pd.DataFrame(
                    [
                        {
                            "Hạng": f"#{i + 1}",
                            "Ngành": m["major"],
                            "Hybrid": f"{m['hybrid_score']:.1f}%",
                            "ML": _fmt_ml_cell(m),
                            "KBS": f"{m['kbs_score']:.1f}%",
                            "Mức độ": _level(m["hybrid_score"]),
                        }
                        for i, m in enumerate(top_majors)
                    ]
                )
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
                st.caption(
                    "Cột **ML**: xác suất RF thô (`predict_proba`) × 100 — tổng các ngành trong khối = 100%."
                )

                st.divider()

                # Giải thích chi tiết cho ngành #1
                st.subheader("Giải thích chi tiết — Ngành #1")
                st.info(explanation)
                rc = best_major.get("reasoning_chain") or []
                if rc:
                    st.markdown("**Chuỗi suy luận KBS (theo ngành đề xuất)**")
                    for step in rc:
                        st.markdown(f"- {step}")

                # Giải thích cho ngành #2 đến #4 (ẩn trong expander)
                if len(top_majors) > 1:
                    st.markdown("##### Giải thích các ngành xếp sau")
                    for i, m in enumerate(top_majors[1:], start=2):
                        with st.expander(
                            f"#{i} — {m['major']} • Hybrid {m['hybrid_score']:.1f}% • "
                            f"{_level(m['hybrid_score'])}"
                        ):
                            cA, cB, cC = st.columns(3)
                            with cA:
                                st.metric("Hybrid", f"{m['hybrid_score']:.1f}%")
                            with cB:
                                st.metric(
                                    "ML",
                                    f"{m['ml_score']:.1f}%"
                                    if m.get("ml_score") is not None
                                    else "N/A",
                                )
                            with cC:
                                st.metric("KBS", f"{m['kbs_score']:.1f}%")
                            st.info(m.get("explanation", ""))
                            rc_i = m.get("reasoning_chain") or []
                            if rc_i:
                                st.markdown("**Chuỗi suy luận KBS**")
                                for step in rc_i:
                                    st.markdown(f"- {step}")
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
    
    else:
        # Khi đang ở trang phân tích nhưng chưa nhấn nút
        st.info("Nhập điểm số các môn rồi nhấn **Phân tích** để xem kết quả.")

# --- FOOTER ---
st.divider()
st.markdown("""

""", unsafe_allow_html=True)
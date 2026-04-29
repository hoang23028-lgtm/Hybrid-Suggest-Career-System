"""
Tệp cấu hình chung cho Hệ thống AI Gợi ý Ngành Học
Phiên bản 3.0: Kiến trúc 2 khối (KHTN/KHXH), không Tin học
"""

# ============================================================================
# MÔ HÌNH MACHINE LEARNING
# ============================================================================
MODEL_PATH_KHTN = 'rf_model_khtn.pkl'
MODEL_PATH_KHXH = 'rf_model_khxh.pkl'
RANDOM_STATE = 42
TEST_SIZE = 0.2  # 80/20 split

# Random Forest hyperparameters
RF_PARAMS = {
    'n_estimators': 100,
    'max_depth': 15,
    'min_samples_split': 10,
    'min_samples_leaf': 5,
    'random_state': RANDOM_STATE,
    'n_jobs': -1,
}

# ============================================================================
# DỮ LIỆU
# ============================================================================
RAW_DATA_PATH = 'diem_thi_thpt_2024.csv'  # Dữ liệu gốc THPT 2024
DATA_PATH_KHTN = 'data_khtn.csv'           # Dữ liệu KHTN đã xử lý
DATA_PATH_KHXH = 'data_khxh.csv'           # Dữ liệu KHXH đã xử lý

# Ánh xạ cột: dữ liệu gốc → tên nội bộ
RAW_COLUMN_MAP = {
    'toan': 'toan',
    'ngu_van': 'van',
    'ngoai_ngu': 'anh',
    'vat_li': 'ly',
    'hoa_hoc': 'hoa',
    'sinh_hoc': 'sinh',
    'lich_su': 'lich_su',
    'dia_li': 'dia_ly',
    'gdcd': 'gdcd',
}

# ============================================================================
# ĐẶC TRƯNG (FEATURES) THEO KHỐI
# ============================================================================
# 3 môn bắt buộc + 3 môn tự chọn = 6 features/khối
SHARED_FEATURES = ['toan', 'van', 'anh']

KHTN_FEATURES = ['toan', 'van', 'anh', 'ly', 'hoa', 'sinh']
KHXH_FEATURES = ['toan', 'van', 'anh', 'lich_su', 'dia_ly', 'gdcd']

KHTN_DISPLAY = {
    'toan': 'Toán', 'van': 'Văn', 'anh': 'Anh',
    'ly': 'Lý', 'hoa': 'Hóa', 'sinh': 'Sinh'
}
KHXH_DISPLAY = {
    'toan': 'Toán', 'van': 'Văn', 'anh': 'Anh',
    'lich_su': 'Lịch sử', 'dia_ly': 'Địa lý', 'gdcd': 'GDCD'
}

def get_features(block):
    """Trả về danh sách features theo khối"""
    return KHTN_FEATURES if block == 'khtn' else KHXH_FEATURES

def get_display_names(block):
    """Trả về tên hiển thị theo khối"""
    return KHTN_DISPLAY if block == 'khtn' else KHXH_DISPLAY

def get_model_path(block):
    """Trả về đường dẫn model theo khối"""
    return MODEL_PATH_KHTN if block == 'khtn' else MODEL_PATH_KHXH

def get_data_path(block):
    """Trả về đường dẫn dữ liệu theo khối"""
    return DATA_PATH_KHTN if block == 'khtn' else DATA_PATH_KHXH

# ============================================================================
# NGÀNH HỌC (CLASSES)
# ============================================================================
NGANH_HOC_MAP = {
    0: "IT - Công nghệ thông tin",
    1: "Kinh tế - Kinh doanh",
    2: "Y khoa - Sức khỏe",
    3: "Kỹ thuật - Xây dựng",
    4: "Nông - Lâm - Ngư",
    5: "Sư phạm - Giáo dục",
    6: "Luật pháp",
    7: "Du lịch - Khách sạn"
}

MAJOR_NAMES = ['IT', 'Kinh tế', 'Y khoa', 'Kỹ thuật',
               'Nông-Lâm-Ngư', 'Sư phạm', 'Luật', 'Du lịch']

# Ngành theo khối
KHTN_MAJORS = [0, 1, 2, 3, 4]   # IT, Kinh tế, Y khoa, Kỹ thuật, Nông-Lâm
KHXH_MAJORS = [1, 5, 6, 7]       # Kinh tế, Sư phạm, Luật, Du lịch

KHTN_MAJOR_NAMES = [MAJOR_NAMES[i] for i in KHTN_MAJORS]
KHXH_MAJOR_NAMES = [MAJOR_NAMES[i] for i in KHXH_MAJORS]

def get_majors(block):
    """Trả về danh sách index ngành theo khối"""
    return KHTN_MAJORS if block == 'khtn' else KHXH_MAJORS

def get_major_names(block):
    """Trả về danh sách tên ngành theo khối"""
    return KHTN_MAJOR_NAMES if block == 'khtn' else KHXH_MAJOR_NAMES

# Mô tả chi tiết cho mỗi ngành
NGANH_HOC_DESCRIPTION = {
    0: {
        'name': 'IT - Công nghệ thông tin',
        'block': 'khtn',
        'keywords': ['Toán', 'Lý'],
        'description': 'Phát triển phần mềm, lập trình, AI, an ninh mạng'
    },
    1: {
        'name': 'Kinh tế - Kinh doanh',
        'block': 'both',
        'keywords': ['Toán', 'Anh', 'Văn'],
        'description': 'Quản lý doanh nghiệp, kế toán, tiếp thị'
    },
    2: {
        'name': 'Y khoa - Sức khỏe',
        'block': 'khtn',
        'keywords': ['Sinh', 'Hóa', 'Lý'],
        'description': 'Bác sĩ, điều dưỡng, dược sĩ, nha sĩ'
    },
    3: {
        'name': 'Kỹ thuật - Xây dựng',
        'block': 'khtn',
        'keywords': ['Toán', 'Lý', 'Hóa'],
        'description': 'Xây dựng, cơ khí, điện, dân dụng'
    },
    4: {
        'name': 'Nông - Lâm - Ngư',
        'block': 'khtn',
        'keywords': ['Sinh', 'Hóa'],
        'description': 'Nông nghiệp, lâm nghiệp, nuôi trồng thủy sản'
    },
    5: {
        'name': 'Sư phạm - Giáo dục',
        'block': 'khxh',
        'keywords': ['Văn', 'Anh', 'Lịch sử'],
        'description': 'Dạy học, quản lý giáo dục, phát triển nhân lực'
    },
    6: {
        'name': 'Luật pháp',
        'block': 'khxh',
        'keywords': ['GDCD', 'Lịch sử', 'Văn'],
        'description': 'Luật sư, công tố viên, cảnh sát'
    },
    7: {
        'name': 'Du lịch - Khách sạn',
        'block': 'khxh',
        'keywords': ['Địa lý', 'Anh', 'Văn'],
        'description': 'Hướng dẫn du lịch, quản lý khách sạn, sự kiện'
    }
}

# ============================================================================
# NGƯỠNG QUYẾT ĐỊNH
# ============================================================================
ADVICE_THRESHOLDS = {
    'high': 75,
    'medium': 50,
    'low': 0
}

# ============================================================================
# VALIDATION & CONSTRAINTS
# ============================================================================
SCORE_MIN = 0
SCORE_MAX = 10
SCORE_DECIMALS = 1

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'app.log'

# ============================================================================
# STREAMLIT CONFIG
# ============================================================================
STREAMLIT_CONFIG = {
    'page_title': 'Hybrid Suggest Career System',
    'page_icon': '',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# ============================================================================
# DEFAULT VALUES (DEMO)
# ============================================================================
DEFAULT_KHTN = {
    'toan': 8, 'van': 5, 'anh': 7,
    'ly': 7, 'hoa': 6, 'sinh': 6
}
DEFAULT_KHXH = {
    'toan': 7, 'van': 8, 'anh': 7,
    'lich_su': 7, 'dia_ly': 6, 'gdcd': 7
}

# ============================================================================
# CROSS-VALIDATION
# ============================================================================
CV_FOLDS = 5
CV_SEED = 42

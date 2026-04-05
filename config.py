"""
Tệp cấu hình chung cho Hệ thống AI Gợi ý Ngành Học
"""

# ============================================================================
# MÔ HÌNH MACHINE LEARNING
# ============================================================================
MODEL_PATH = 'rf_model.pkl'
RANDOM_STATE = 42
TEST_SIZE = 0.2  # 80/20 split

# Random Forest hyperparameters
RF_PARAMS = {
    'n_estimators': 100,      # Số lượng cây quyết định
    'max_depth': 15,          # Độ sâu cây tối đa
    'min_samples_split': 10,  # Số mẫu tối thiểu để split
    'min_samples_leaf': 5,    # Số mẫu tối thiểu tại leaf
    'random_state': RANDOM_STATE,
    'n_jobs': -1,             # Sử dụng tất cả CPU cores
}

# ============================================================================
# DỮ LIỆU
# ============================================================================
DATA_PATH = 'data_tuyensinh_balanced.csv'  # Sử dụng dữ liệu cân bằng
NUM_SAMPLES = 117280  # Số lượng mẫu dữ liệu (cân bằng)

# Các đặc trưng (Features)
FEATURE_NAMES = ['toan', 'ly', 'hoa', 'sinh', 'van', 'anh', 'lich_su', 'dia_ly', 'tin_hoc']
FEATURE_DISPLAY_NAMES = {
    'toan': ' Toán',
    'ly': ' Lý',
    'hoa': ' Hóa',
    'sinh': ' Sinh',
    'van': ' Văn',
    'anh': ' Anh',
    'lich_su': ' Lịch sử',
    'dia_ly': ' Địa lý',
    'tin_hoc': ' Tin học'
}

NUM_FEATURES = len(FEATURE_NAMES)

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

NUM_CLASSES = len(NGANH_HOC_MAP)

# Mô tả chi tiết cho mỗi ngành
NGANH_HOC_DESCRIPTION = {
    0: {
        'name': 'IT - Công nghệ thông tin',
        'emoji': '💻',
        'keywords': ['Toán', 'Tin học', 'Lý'],
        'description': 'Phát triển phần mềm, lập trình, AI, an ninh mạng'
    },
    1: {
        'name': 'Kinh tế - Kinh doanh',
        'emoji': '💼',
        'keywords': ['Toán', 'Anh', 'Văn'],
        'description': 'Quản lý doanh nghiệp, kế toán, tiếp thị'
    },
    2: {
        'name': 'Y khoa - Sức khỏe',
        'emoji': '⚕️',
        'keywords': ['Sinh', 'Hóa', 'Lý'],
        'description': 'Bác sĩ, điều dưỡng, dược sĩ, nha sĩ'
    },
    3: {
        'name': 'Kỹ thuật - Xây dựng',
        'emoji': '🏗️',
        'keywords': ['Toán', 'Lý', 'Tin'],
        'description': 'Xây dựng, cơ khí, điện, dân dụng'
    },
    4: {
        'name': 'Nông - Lâm - Ngư',
        'emoji': '🌾',
        'keywords': ['Sinh', 'Địa lý', 'Hóa'],
        'description': 'Nông nghiệp, lâm nghiệp, nuôi trồng thủy sản'
    },
    5: {
        'name': 'Sư phạm - Giáo dục',
        'emoji': '👨‍🏫',
        'keywords': ['Văn', 'Anh', 'Lịch sử'],
        'description': 'Dạy học, quản lý giáo dục, phát triển nhân lực'
    },
    6: {
        'name': 'Luật pháp',
        'emoji': '⚖️',
        'keywords': ['Lịch sử', 'Văn', 'Anh'],
        'description': 'Luật sư, công tố viên, cảnh sát'
    },
    7: {
        'name': 'Du lịch - Khách sạn',
        'emoji': '✈️',
        'keywords': ['Địa lý', 'Anh', 'Văn'],
        'description': 'Hướng dẫn du lịch, quản lý khách sạn, sự kiện'
    }
}

# ============================================================================
# FUZZY LOGIC SYSTEM
# ============================================================================
# Ngưỡng Membership Functions
FUZZY_ML_INPUT_RANGE = (0, 11)
FUZZY_INTEREST_RANGE = (0, 11)
FUZZY_ADVICE_RANGE = (0, 101)

# Ngưỡng quyết định
ADVICE_THRESHOLDS = {
    'high': 75,      # Rất phù hợp
    'medium': 50,    # Khá phù hợp
    'low': 0         # Không quá phù hợp
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
    'page_title': '🎓 Hybrid Suggest Career System',
    'page_icon': '🎓',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# ============================================================================
# DEFAULT VALUES (DEMO)
# ============================================================================
DEFAULT_VALUES = {
    'toan': 8,
    'ly': 7,
    'hoa': 6,
    'sinh': 7,
    'van': 5,
    'anh': 8,
    'lich_su': 6,
    'dia_ly': 6,
    'tin_hoc': 9
}

# ============================================================================
# CROSS-VALIDATION
# ============================================================================
CV_FOLDS = 5
CV_SEED = 42

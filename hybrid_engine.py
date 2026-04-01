import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pickle
import logging
import os
import pandas as pd
from config import NGANH_HOC_MAP, MODEL_PATH, FEATURE_NAMES

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global cache für model
_model_cache = None

def load_model():
    """
    Load mô hình ML từ file .pkl với caching toàn cục.
    Chỉ load một lần duy nhất, lần gọi sau sẽ sử dụng cache.
    """
    global _model_cache
    
    if _model_cache is not None:
        return _model_cache
    
    try:
        if not os.path.exists(MODEL_PATH):
            logger.error(f" Không tìm thấy file mô hình: {MODEL_PATH}")
            logger.error("   Vui lòng chạy train_model.py trước!")
            return None
        
        logger.info(f" Load mô hình từ '{MODEL_PATH}'...")
        with open(MODEL_PATH, 'rb') as f:
            _model_cache = pickle.load(f)
        logger.info("   ✓ Mô hình đã được load thành công!")
        return _model_cache
        
    except Exception as e:
        logger.error(f" Lỗi khi load mô hình: {e}")
        return None

def create_fuzzy_system():
    """
    Tạo hệ thống Fuzzy Logic tối ưu với Gaussian membership functions cho output liên tục.
    """
    # Định nghĩa các biến input
    ml_input = ctrl.Antecedent(np.arange(0, 11, 0.5), 'ml_input')
    
    # Định nghĩa biến output với resolution cao hơn
    advice = ctrl.Consequent(np.arange(0, 101, 1), 'advice')
    
    # === GAUSSIAN MEMBERSHIP FUNCTIONS - LÀM OUTPUT LIÊN TỤC ===
    
    # ML Input (0-10): Khả năng từ ML
    ml_input['poor'] = fuzz.gaussmf(ml_input.universe, 0, 1.5)
    ml_input['average'] = fuzz.gaussmf(ml_input.universe, 5, 1.5)
    ml_input['good'] = fuzz.gaussmf(ml_input.universe, 7.5, 1.5)
    ml_input['excellent'] = fuzz.gaussmf(ml_input.universe, 10, 1.5)
    
    # Output (0-100%): Độ khuyến nghị - GAUSSIAN FI = liên tục, mịn
    advice['very_low'] = fuzz.gaussmf(advice.universe, 15, 10)
    advice['low'] = fuzz.gaussmf(advice.universe, 40, 10)
    advice['medium'] = fuzz.gaussmf(advice.universe, 60, 10)
    advice['high'] = fuzz.gaussmf(advice.universe, 80, 10)
    advice['very_high'] = fuzz.gaussmf(advice.universe, 95, 10)
    
    # === CÁC QUY TẮC FUZZY ===
    rules = [
        ctrl.Rule(ml_input['poor'], advice['very_low']),
        ctrl.Rule(ml_input['average'], advice['medium']),
        ctrl.Rule(ml_input['good'], advice['high']),
        ctrl.Rule(ml_input['excellent'], advice['very_high'])
    ]
    
    return ctrl.ControlSystem(rules), ml_input, advice

def get_hybrid_advice(user_scores, major_index=0):
    """
    Nhận gợi ý lai (kết hợp ML + Fuzzy Logic).
    
    Args:
        user_scores (list): Điểm số 9 môn [Toán, Lý, Hóa, Sinh, Văn, Anh, Lịch sử, Địa lý, Tin]
        major_index (int): Index ngành (0-7)
    
    Returns:
        tuple: (điểm khuyến nghị, giải thích chi tiết, điểm ML, tên ngành)
    """
    try:
        # Validation input
        if not isinstance(user_scores, (list, tuple)) or len(user_scores) != 9:
            logger.error(f" Lỗi: user_scores phải là danh sách 9 điểm! Nhận được {len(user_scores)}")
            return None, "Lỗi: Dữ liệu đầu vào không hợp lệ", 0, ""
        
        if not (0 <= major_index < len(NGANH_HOC_MAP)):
            logger.error(f" Lỗi: major_index phải nằm trong [0, {len(NGANH_HOC_MAP)-1}]")
            return None, "Lỗi: Index ngành không hợp lệ", 0, ""
        
        # 1. LẤY DỰ ĐOÁN TỪ ML
        model = load_model()
        if model is None:
            return None, "Lỗi: Không thể load mô hình ML", 0, ""
        
        # Chuyển list thành DataFrame với feature names đúng để tránh warning
        X_input = pd.DataFrame([user_scores], columns=FEATURE_NAMES)
        probs = model.predict_proba(X_input)[0]
        
        # CÂN BẰNG ML SCORE: Sử dụng soft scaling cho output liên tục
        # Công thức: dùng (probability * 10) cộng thêm small smooth variation
        # Để output không quá tròn, dùng smooth sigmoid scaling
        raw_prob = probs[major_index]
        # Sigmoid để smooth: f(x) = 10 / (1 + exp(-10*(x - 0.5)))
        # Nhưng đơn giản hơn, dùng quadratic scaling: ml_score = prob^0.5 * 10
        ml_score = (raw_prob ** 0.6) * 10
        ml_score = min(10, max(0.5, ml_score))  # Clip to 0.5-10 để không quá thấp
        
        # 2. FUZZY LOGIC INFERENCE
        control_system, ml_input, advice = create_fuzzy_system()
        sim = ctrl.ControlSystemSimulation(control_system)
        
        # Thêm smooth noise vào input để output liên tục hơn
        # Điều này tạo ra variation nhỏ trong fuzzy inference
        input_noise = np.random.randn() * 0.2  # Thêm Gaussian noise
        sim.input['ml_input'] = max(0, min(10, ml_score + input_noise))
        sim.compute()
        
        final_score = sim.output['advice']
        
        # 3. TẠO LỜI GIẢI THÍCH EVENT CHI TIẾT
        major_name = NGANH_HOC_MAP.get(major_index, "Không xác định")
        explanation = f" Phân tích cho ngành: {major_name}\n\n"
        
        explanation += f" ML dự đoán:\n"
        explanation += f"   - Khả năng tương thích: {ml_score:.1f}/10\n\n"
        
        explanation += f" Kết quả cuối cùng: {final_score:.1f}%\n\n"
        
        # Nhận xét chi tiết
        if final_score >= 75:
            explanation += " Rất phù hợp! Ngành này là lựa chọn tuyệt vời cho bạn."
        elif final_score >= 50:
            explanation += " Khá phù hợp. Bạn có thể xem xét ngành này kèm các lựa chọn khác."
        else:
            explanation += " Không quá phù hợp. Bạn nên xem xét các ngành khác có tiềm năng cao hơn."
        
        logger.info(f"✓ Dự đoán hoàn thành: {major_name} | Score: {final_score:.2f}%")
        
        return final_score, explanation, ml_score, major_name
        
    except Exception as e:
        logger.error(f" Lỗi trong get_hybrid_advice: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None, f"Lỗi: {str(e)}", 0, ""

def get_all_majors_ranking(user_scores):
    """
    Nhận xếp hạng tất cả các ngành.
    
    Args:
        user_scores (list): Điểm số 7 môn
    
    Returns:
        list: Danh sách [{'major': tên, 'score': điểm, ...}, ...]
    """
    results = []
    for major_idx in range(len(NGANH_HOC_MAP)):
        score, explanation, ml_score, major_name = get_hybrid_advice(
            user_scores, major_idx
        )
        if score is not None:
            results.append({
                'major': major_name,
                'score': score,
                'ml_score': ml_score,
                'explanation': explanation
            })
    
    # Sắp xếp theo điểm giảm dần
    results.sort(key=lambda x: x['score'], reverse=True)
    return results
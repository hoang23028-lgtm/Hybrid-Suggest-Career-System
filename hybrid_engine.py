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

# Import hybrid_fusion functions nếu có
try:
    from hybrid_fusion import (
        calculate_hybrid_score, 
        get_hybrid_ranking
    )
    HYBRID_FUSION_AVAILABLE = True
    logger.info("✓ hybrid_fusion module đã được load thành công!")
except ImportError:
    HYBRID_FUSION_AVAILABLE = False
    logger.warning("⚠ Không thể import hybrid_fusion. Sẽ sử dụng fuzzy logic cũ.")

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
    
    try:
        # Validation input
        if not isinstance(user_scores, (list, tuple)) or len(user_scores) != 9:
            logger.error(f" Chú ý: user_scores phải là danh sách 9 điểm! Nhận được {len(user_scores)}")
            return None, "Lỗi: Dữ liệu đầu vào không hợp lệ", 0, ""
        
        if not (0 <= major_index < len(NGANH_HOC_MAP)):
            logger.error(f" Chú ý: major_index phải nằm trong [0, {len(NGANH_HOC_MAP)-1}]")
            return None, "Lỗi: Index ngành không hợp lệ", 0, ""
        
        major_name = NGANH_HOC_MAP.get(major_index, "Không xác định")
        
        # ===== CÁCH 1: Nếu có hybrid_fusion module (ưu tiên) =====
        if HYBRID_FUSION_AVAILABLE:
            try:
                model = load_model()
                if model is None:
                    logger.warning(f"⚠ Không thể load mô hình ML, sẽ sử dụng fuzzy logic")
                else:
                    hybrid_result = calculate_hybrid_score(user_scores, major_index, model=model)
                    
                    # Chuyển đổi format output để tương thích với signature cũ
                    final_score = hybrid_result['hybrid_score']  # 0-100%
                    ml_score = hybrid_result['ml_score']  # 0-10 scale
                    
                    # Format giải thích chi tiết
                    explanation = f"Phân tích lai (Hybrid) cho ngành: {major_name}\n\n"
                    explanation += f"Kết quả phân tích:\n"
                    explanation += f"   • Điểm Hybrid : {final_score:.1f}%\n"
                    explanation += f"   • ML Score: {hybrid_result['ml_score']:.1f}/10 ({hybrid_result['ml_score']*10:.1f}%)\n"
                    explanation += f"   • KBS Score: {hybrid_result['kbs_score']:.1f}%\n\n"
                    
                    explanation += f"Công thức: Hybrid = 0.6×ML + 0.4×KBS\n"
                    explanation += f"   = 0.6×{hybrid_result['ml_score']*10:.1f}% + 0.4×{hybrid_result['kbs_score']:.1f}%\n\n"
                    
                    explanation += f"Chi tiết: {hybrid_result['explanation']}\n\n"
                    
                    # Nhận xét chi tiết dựa trên điểm
                    if final_score >= 75:
                        explanation += "Rất phù hợp! Ngành này là lựa chọn tuyệt vời cho bạn."
                    elif final_score >= 50:
                        explanation += "Khá phù hợp. Bạn có thể xem xét ngành này kèm các lựa chọn khác."
                    else:
                        explanation += "Không quá phù hợp. Bạn nên xem xét các ngành khác có tiềm năng cao hơn."
                    
                    logger.info(f"✓ Dự đoán Hybrid hoàn thành: {major_name} | Score: {final_score:.2f}%")
                    
                    return final_score, explanation, ml_score, major_name
                    
            except Exception as e:
                logger.warning(f"⚠ Lỗi sử dụng hybrid_fusion: {e}. Fallback sang fuzzy logic.")
                # Tiếp tục xử lý với fuzzy logic bên dưới
        
        # ===== CÁCH 2: Fallback sang Fuzzy Logic (cách cũ) =====
        logger.info(f"ℹ Sử dụng Fuzzy Logic cho {major_name}")
        
        model = load_model()
        if model is None:
            return None, "Lỗi: Không thể load mô hình ML", 0, ""
        
        # Chuyển list thành DataFrame với feature names đúng
        X_input = pd.DataFrame([user_scores], columns=FEATURE_NAMES)
        probs = model.predict_proba(X_input)[0]
        
        # Tính ML score: dùng quadratic scaling
        raw_prob = probs[major_index]
        ml_score = (raw_prob ** 0.6) * 10
        ml_score = min(10, max(0.5, ml_score))  # Clip to 0.5-10
        
        # Fuzzy Logic inference
        control_system, ml_input, advice = create_fuzzy_system()
        sim = ctrl.ControlSystemSimulation(control_system)
        
        # Thêm smooth noise vào input
        input_noise = np.random.randn() * 0.2
        sim.input['ml_input'] = max(0, min(10, ml_score + input_noise))
        sim.compute()
        
        final_score = sim.output['advice']
        
        # Tạo lời giải thích
        explanation = f"Phân tích Fuzzy Logic cho ngành: {major_name}\n\n"
        explanation += f"Kết quả phân tích:\n"
        explanation += f"   • Điểm cuối cùng: {final_score:.1f}%\n"
        explanation += f"   • ML dự đoán: {ml_score:.1f}/10\n\n"
        
        # Nhận xét chi tiết
        if final_score >= 75:
            explanation += "Rất phù hợp! Ngành này là lựa chọn tuyệt vời cho bạn."
        elif final_score >= 50:
            explanation += "Khá phù hợp. Bạn có thể xem xét ngành này kèm các lựa chọn khác."
        else:
            explanation += "Không quá phù hợp. Bạn nên xem xét các ngành khác có tiềm năng cao hơn."
        
        logger.info(f"✓ Dự đoán Fuzzy hoàn thành: {major_name} | Score: {final_score:.2f}%")
        
        return final_score, explanation, ml_score, major_name
        
    except Exception as e:
        logger.error(f" Lỗi trong get_hybrid_advice: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None, f"Lỗi: {str(e)}", 0, ""

def get_all_majors_ranking(user_scores):
    
    try:
        # ===== CÁCH 1: Nếu có hybrid_fusion module (ưu tiên) =====
        if HYBRID_FUSION_AVAILABLE:
            try:
                model = load_model()
                if model is not None:
                    rankings = get_hybrid_ranking(user_scores, model=model)
                    
                    # Chuyển đổi format output từ hybrid_fusion
                    results = []
                    for idx, ranking in enumerate(rankings):
                        results.append({
                            'major': ranking['major'],
                            'score': ranking['hybrid_score'],  # 0-100%
                            'ml_score': ranking['ml_score'],  # 0-10
                            'kbs_score': ranking['kbs_score'],  # 0-100%
                            'relevance_score': ranking.get('relevance_score', 0),  # Tie-breaking
                            'explanation': f"Hybrid: {ranking['hybrid_score']:.1f}% (ML: {ranking['ml_score']*10:.1f}% + KBS: {ranking['kbs_score']:.1f}%)",
                            'rank': idx + 1,
                            'hybrid_result': ranking  # Chi tiết đầy đủ từ hybrid_fusion
                        })
                    
                    logger.info(f"✓ Xếp hạng Hybrid hoàn thành: {len(results)} ngành")
                    return results
                else:
                    logger.warning("⚠ Không thể load model, fallback sang cách cũ")
                    
            except Exception as e:
                logger.warning(f"⚠ Lỗi sử dụng hybrid_fusion: {e}. Fallback sang cách cũ.")
        
        # ===== CÁCH 2: Fallback - dùng get_hybrid_advice lần lượt (cách cũ) =====
        logger.info("ℹ Sử dụng phương pháp cũ để xếp hạng các ngành")
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
                    'explanation': explanation,
                    'rank': major_idx + 1
                })
        
        # Sắp xếp theo điểm giảm dần, tie-break by relevance_score
        results.sort(key=lambda x: (x['score'], x.get('relevance_score', 0)), reverse=True)
        
        # Cập nhật rank sau khi sắp xếp
        for idx, item in enumerate(results):
            item['rank'] = idx + 1
        
        logger.info(f"✓ Xếp hạng cũ hoàn thành: {len(results)} ngành")
        return results
        
    except Exception as e:
        logger.error(f" Lỗi trong get_all_majors_ranking: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []
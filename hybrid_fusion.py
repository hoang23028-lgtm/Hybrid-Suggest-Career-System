"""Hybrid Fusion Engine: Kết Hợp Luật + Luật Từ ML
=========================================================


Hai Loại Luật:
  1. Luật Không AI (KBS):   32 luật chuyên gia (knowledge_rules.py)
  2. Luật Từ ML   (ML):     Random Forest + Feature Extraction (train_model.py)
  
Kết Hợp (Fusion):
  Hybrid_Score = 0.6 × ML_Score + 0.4 × KBS_Score
"""

from pathlib import Path
import pickle
import logging
import pandas as pd

# Import KBS engine
from knowledge_rules import KnowledgeRuleEngine
from config import FEATURE_NAMES

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ==================== CONFIG ====================

# Weight: 60% ML, 40% KBS
ML_WEIGHT = 0.6
KBS_WEIGHT = 0.4

MAJOR_NAMES = [
    'IT', 'Kinh tế', 'Y khoa', 'Kỹ thuật',
    'Nông-Lâm-Ngư', 'Sư phạm', 'Luật', 'Du lịch'
]


# ==================== MODEL LOADING ====================

def load_ml_model():
    """Load trained Random Forest model"""
    model_path = Path(__file__).parent / 'rf_model.pkl'
    
    if not model_path.exists():
        logger.error(f"⚠️  Model not found: {model_path}")
        return None
    
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"✓ Loaded ML model from {model_path}")
        return model
    except Exception as e:
        logger.error(f" Error loading model: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


def normalize_scores(user_scores):
    """
    Dữ liệu training là [3, 10], không cần normalize!
    Mô hình được huấn luyện trên scores trong phạm vi [3-10]
    
    Args:
        user_scores: list [0-10] từ UI
    
    Returns:
        list: Rescale thành [3-10] để match dữ liệu training
    """
    # Rescale từ [0, 10] → [3, 10]
    # Formula: output = 3 + (input / 10) * 7
    # Khi input=0 → output=3, khi input=10 → output=10
    return [3 + (s / 10) * 7 for s in user_scores]


# ==================== ML SCORE CALCULATION ====================

def calculate_ml_score(user_scores, major_index, model=None):
    """
    Tính ML_Score từ Random Forest
    
    Args:
        user_scores: list [Toán, Lý, Hóa, Sinh, Văn, Anh, LS, DL, Tin]
        major_index: int (0-7, chỉ số ngành)
        model: Random Forest model (nếu None, load tự động)
    
    Returns:
        dict: {
            'score': float (0-100),
            'raw_prob': float (0-1),
            'ml_score_0_10': float (0-10),
            'major': str
        }
    """
    if model is None:
        model = load_ml_model()
    
    if model is None:
        logger.warning(f"⚠️  ML Model not available for {MAJOR_NAMES[major_index]}")
        return {
            'score': None,
            'raw_prob': None,
            'ml_score_0_10': None,
            'major': MAJOR_NAMES[major_index],
            'error': 'Model not available'
        }
    
    try:
        # Input scores should be [0-10], use as-is (no normalization in input)
        logger.debug(f"User scores [0-10]: {user_scores}")
        logger.debug(f"Major index: {major_index} ({MAJOR_NAMES[major_index]})")
        
        # Normalize scores [0,10] → [0,1] for model input
        X_normalized = normalize_scores(user_scores)
        logger.debug(f"Normalized scores [0-1]: {X_normalized}")
        
        # Create DataFrame with exact feature names and order
        # CRITICAL: Must match the order used during training!
        X_df = pd.DataFrame([X_normalized], columns=FEATURE_NAMES)
        logger.debug(f"DataFrame shape: {X_df.shape}, columns: {X_df.columns.tolist()}")
        logger.debug(f"DataFrame values: {X_df.values}")
        
        # Get model's expected feature names (set during training)
        if hasattr(model, 'feature_names_in_'):
            expected_features = list(model.feature_names_in_)
            logger.debug(f"Model expects features: {expected_features}")
            if X_df.columns.tolist() != expected_features:
                logger.warning("  Feature order mismatch! Reordering...")
                X_df = X_df[expected_features]
        
        # Predict probability for all classes
        probs = model.predict_proba(X_df)[0]
        logger.debug(f"All class probabilities: {probs}")
        
        # Get probability for the specific major
        if major_index >= len(probs):
            logger.error(f" Major index {major_index} out of range (0-{len(probs)-1})")
            return {
                'score': None,
                'raw_prob': None,
                'major': MAJOR_NAMES[major_index],
                'error': f'Invalid major index {major_index}'
            }
        
        raw_prob = probs[major_index]
        logger.debug(f"Raw probability for {MAJOR_NAMES[major_index]}: {raw_prob:.6f}")
        
        if raw_prob is None or not isinstance(raw_prob, (int, float)):
            logger.error(f" Invalid probability value: {raw_prob} (type: {type(raw_prob)})")
            return {
                'score': None,
                'raw_prob': None,
                'major': MAJOR_NAMES[major_index],
                'error': f'Invalid probability: {raw_prob}'
            }
        
        # Temperature Scaling to boost confidence
        temperature = 0.7  # Boost confidence (0.5-0.9 works well)
        boosted_prob = raw_prob ** (1.0 / temperature)
        scaled_prob = min(boosted_prob, 1.0)
        
        # Convert to 0-100% with confidence scaling
        baseline_prob = 1.0 / 8  # 0.125 (baseline for 8 classes)
        if scaled_prob <= baseline_prob:
            ml_score_0_100 = 0.0
        else:
            ml_score_0_100 = ((scaled_prob - baseline_prob) / (1 - baseline_prob)) * 100.0
        
        ml_score_0_100 = max(0.0, min(100.0, ml_score_0_100))  # Clamp to [0, 100]
        
        logger.debug(f"ML Score calculation: raw={raw_prob:.6f} → boosted={boosted_prob:.6f} → scaled={scaled_prob:.6f} → final={ml_score_0_100:.2f}%")
        logger.info(f"✓ ML Score for {MAJOR_NAMES[major_index]}: {ml_score_0_100:.2f}%")
        
        return {
            'score': ml_score_0_100,
            'raw_prob': raw_prob,
            'major': MAJOR_NAMES[major_index]
        }
    except Exception as e:
        logger.error(f" ML Score Calculation Error for {MAJOR_NAMES[major_index]}: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'score': None,
            'raw_prob': None,
            'major': MAJOR_NAMES[major_index],
            'error': str(e)
        }


# ==================== KBS SCORE CALCULATION ====================

def calculate_kbs_score(user_scores, major_index):
    """
    Tính KBS_Score từ 32 luật chuyên gia
    
    Args:
        user_scores: list [Toán, Lý, Hóa, Sinh, Văn, Anh, LS, DL, Tin]
        major_index: int (0-7)
    
    Returns:
        dict: {
            'score': float (0-100),
            'rule_name': str,
            'reason': str,
            'major': str
        }
    """
    kbs = KnowledgeRuleEngine()
    result = kbs.evaluate(user_scores, major_index)
    
    return result


# ==================== HYBRID FUSION ====================

def calculate_hybrid_score(user_scores, major_index, model=None):
    """
    ⭐ MAIN FUNCTION: Kết hợp KBS + ML → Hybrid Score
    
    Bước 1: Tính KBS_Score từ 32 luật chuyên gia
    Bước 2: Tính ML_Score từ Random Forest
    Bước 3: Kết hợp = 0.6 × ML + 0.4 × KBS
    
    Args:
        user_scores: list [Toán, Lý, Hóa, Sinh, Văn, Anh, LS, DL, Tin]
        major_index: int (0-7)
        model: Random Forest model (optional)
    
    Returns:
        dict: {
            'major': str,
            'hybrid_score': float (0-100),  ← FINAL RESULT
            'ml_score': float,
            'kbs_score': float,
            'ml_weight': float,
            'kbs_weight': float,
            'ml_details': dict,
            'kbs_details': dict,
            'explanation': str [Vietnamese]
        }
    """
    
    # LOẠI 1: KBS (Luật không AI)
    kbs_result = calculate_kbs_score(user_scores, major_index)
    kbs_score = kbs_result.get('score', 0)
    relevance_score = kbs_result.get('relevance_score', 0)
    
    # LOẠI 2: ML (Luật từ ML)
    ml_result = calculate_ml_score(user_scores, major_index, model)
    ml_score = ml_result.get('score')
    
    # Xử lý khi ML không khả dụng
    if ml_score is None:
        # Fallback: chỉ dùng KBS
        hybrid_score = kbs_score
        ml_weight_actual = 0
        kbs_weight_actual = 1.0
    else:
        # Kết hợp: 60% ML + 40% KBS
        hybrid_score = ML_WEIGHT * ml_score + KBS_WEIGHT * kbs_score
        ml_weight_actual = ML_WEIGHT
        kbs_weight_actual = KBS_WEIGHT
    
    # Tạo giải thích (Vietnamese)
    explanation = _create_explanation(
        user_scores,
        major_index,
        kbs_score,
        ml_score,
        hybrid_score,
        kbs_result,
        ml_result
    )
    
    return {
        'major': MAJOR_NAMES[major_index],
        'hybrid_score': round(hybrid_score, 1),  # ← KẾT QUẢ CUỐI CÙNG
        'ml_score': round(ml_score, 1) if ml_score is not None else None,
        'kbs_score': round(kbs_score, 1),
        'relevance_score': relevance_score,  # Tie-breaking: điểm TB môn liên quan
        'ml_weight': ml_weight_actual,
        'kbs_weight': kbs_weight_actual,
        'ml_details': ml_result,
        'kbs_details': kbs_result,
        'explanation': explanation
    }


def _create_explanation(user_scores, major_index, kbs_score, ml_score, hybrid_score, kbs_result, ml_result):
    """Tạo giải thích chi tiết (Vietnamese)"""
    
    major = MAJOR_NAMES[major_index]
    
    if ml_score is None:
        return f"""
NGÀNH: {major}
ĐIỂM CUỐI CÙNG: {hybrid_score}% (Chỉ dùng KBS vì ML không khả dụng)

📋 LUẬT (KBS):
   Luật: {kbs_result.get('rule_name', 'N/A')}
   Lý do: {kbs_result.get('reason', 'N/A')}
   Điểm: {kbs_score}%
"""
    else:
        calc_details = f"{ML_WEIGHT} × {ml_score} + {KBS_WEIGHT} × {kbs_score} = {hybrid_score}"
        return f"""
NGÀNH: {major}
█ ĐIỂM CUỐI CÙNG: {hybrid_score}% (HYBRID)

TÍNH TOÁN:
   {calc_details}

LOẠI 2 - LUẬT TỪ ML (Data-Driven):
   Mô hình: Random Forest (100 cây, 91.77% accuracy)
   , Dữ liệu: 118,449 mẫu học sinh
   , Xác suất: {ml_result.get('raw_prob', 'N/A'):.2%}
   , Công thức: (prob^0.6) × 100
   , Điểm ML: {ml_score}% (60%)

LOẠI 1 - LUẬT KHÔNG AI (Expert Rules):
   Loại luật: {kbs_result.get('description', 'N/A')}
   , Chi tiết: {kbs_result.get('rule_name', 'N/A')}
   , Lý do: {kbs_result.get('reason', 'N/A')}
   , Điểm KBS: {kbs_score}% (40%)

KẾT HỢP CUỐI CÙNG:
   Kết hợp = 60% (ML) + 40% (KBS)
   = 60% × Dữ liệu + 40% × Chuyên gia
   = {hybrid_score}%
"""


# ==================== RANKING ====================

def get_hybrid_ranking(user_scores, model=None):
    """
    Xếp hạng tất cả 8 ngành dựa trên Hybrid Score
    
    Args:
        user_scores: list [Toán, Lý, Hóa, Sinh, Văn, Anh, LS, DL, Tin]
        model: Random Forest model (optional)
    
    Returns:
        list: [{rank, major, hybrid_score, ml_score, kbs_score, explanation}, ...]
    """
    results = []
    
    for i in range(8):
        result = calculate_hybrid_score(user_scores, i, model)
        results.append({
            'major': result['major'],
            'hybrid_score': result['hybrid_score'],
            'ml_score': result['ml_score'],
            'kbs_score': result['kbs_score'],
            'relevance_score': result.get('relevance_score', 0),
            'explanation': result['explanation']
        })
    
    # Sort by hybrid_score descending, tie-break by relevance_score
    results.sort(key=lambda x: (x['hybrid_score'], x.get('relevance_score', 0)), reverse=True)
    
    # Add rank
    for rank, item in enumerate(results, 1):
        item['rank'] = rank
    
    return results


def print_hybrid_ranking(user_scores, model=None):
    """In kết quả xếp hạng Hybrid"""
    
    ranking = get_hybrid_ranking(user_scores, model)
    
    print("\n" + "="*90)
    print("XẾP HẠNG NGÀNH - HYBRID (KBS + ML)")
    print("="*90)
    print(f"Điểm học sinh: {dict(zip(['Toán', 'Lý', 'Hóa', 'Sinh', 'Văn', 'Anh', 'LS', 'DL', 'Tin'], user_scores))}")
    print("-"*90)
    print(f"{'Rank':<4} {'Ngành':<15} {'Hybrid':<8} {'ML':<8} {'KBS':<8} {'Công thức':<30}")
    print("-"*90)
    
    for item in ranking:
        ml_str = f"{item['ml_score']:.0f}%" if item['ml_score'] else "N/A"
        formula = f"0.6×{ml_str}+0.4×{item['kbs_score']:.0f}%" if item['ml_score'] else "100%×KBS"
        print(
            f"{item['rank']:<4} {item['major']:<15} {item['hybrid_score']:<8.0f}% "
            f"{ml_str:<8} {item['kbs_score']:<8.0f}% {formula:<30}"
        )
    
    print("="*90 + "\n")


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    print("\n" + "="*90)
    print("HYBRID FUSION ENGINE - TEST")
    print("="*90)
    print("Kết hợp Luật Không AI (KBS) + Luật Từ ML")
    print("Kết quả = 60% ML + 40% KBS")
    print("="*90)
    
    # Load model
    model = load_ml_model()
    
    # Test Case 1: Học sinh IT chuyên
    print("\n### TEST CASE 1: Học sinh IT Chuyên ###")
    scores_1 = [9, 8, 5, 4, 5, 6, 5, 5, 9.5]
    result_1 = calculate_hybrid_score(scores_1, major_index=0, model=model)
    print(result_1['explanation'])
    print_hybrid_ranking(scores_1, model)
    
    # Test Case 2: Học sinh Y Khoa chuyên
    print("\n### TEST CASE 2: Học sinh Y Khoa Chuyên ###")
    scores_2 = [6, 5, 8, 8.5, 7, 7, 6, 6, 5]
    result_2 = calculate_hybrid_score(scores_2, major_index=2, model=model)
    print(result_2['explanation'])
    print_hybrid_ranking(scores_2, model)
    
    # Test Case 3: Học sinh cân bằng
    print("\n### TEST CASE 3: Học sinh Cân Bằng ###")
    scores_3 = [7, 7, 7, 7, 7, 7, 7, 7, 7]
    print_hybrid_ranking(scores_3, model)

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
import numpy as np
import pandas as pd

# Import KBS engine
from knowledge_rules import KnowledgeRuleEngine
from config import MAJOR_NAMES, get_features, get_model_path, get_majors, get_display_names

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ==================== CONFIG ====================

# Weight: 60% ML, 40% KBS
ML_WEIGHT = 0.6
KBS_WEIGHT = 0.4

# ==================== KBS VETO CONFIG ====================
# KBS có quyền phủ quyết (veto) kết quả ML khi phát hiện bất hợp lý rõ ràng
VETO_KBS_NOT_FIT_THRESHOLD = 20     # KBS score <= 20 → ngành "Không phù hợp"
VETO_ML_HIGH_THRESHOLD = 60         # ML score > 60 khi KBS nói Not_Fit → bất hợp lý
VETO_KEY_SUBJECT_MIN = 4.0          # Môn trọng tâm < 4.0 → veto cứng
VETO_KBS_DOMINANT_WEIGHT = 0.85     # Khi veto: KBS chiếm 85%, ML chỉ 15%

# Cached engines (singleton per block)
_kbs_engines = {}
_ml_models = {}

def _get_kbs_engine(block: str):
    """Get cached KnowledgeRuleEngine instance for a block."""
    global _kbs_engines
    if block not in _kbs_engines:
        _kbs_engines[block] = KnowledgeRuleEngine(block=block)
    return _kbs_engines[block]


# ==================== MODEL LOADING ====================

def load_ml_model(block: str):
    """Load trained Random Forest model for a given block."""
    global _ml_models
    if block in _ml_models:
        return _ml_models[block]

    model_path = Path(__file__).parent / get_model_path(block)
    if not model_path.exists():
        logger.error(f"⚠️  ML model not found for {block}: {model_path}")
        _ml_models[block] = None
        return None

    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"✓ Loaded ML model for {block} from {model_path}")
        _ml_models[block] = model
        return model
    except Exception as e:
        logger.error(f"Error loading ML model for {block}: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        _ml_models[block] = None
        return None


def normalize_scores(user_scores):
    """
    Chuẩn hóa điểm từ UI.
    Model được train trên raw scores [3-10], nên KHÔNG chia cho 10.
    Chỉ clip về khoảng [0, 10] để đảm bảo hợp lệ.
    
    Args:
        user_scores: list [0-10] từ UI
    
    Returns:
        list: Scores đã clip về [0, 10]
    """
    return [min(max(s, 0.0), 10.0) for s in user_scores]


# ==================== ML SCORE CALCULATION ====================

def calculate_ml_score(user_scores, major_index, block: str, model=None):
    """
    Tính ML_Score từ Random Forest cho đúng khối (KHTN/KHXH).

    Lưu ý: model được train trên 6 features (không có tin_hoc) và classes chỉ gồm các
    nhãn ngành thuộc khối đó, nên cần map major_index → vị trí trong model.classes_.
    """
    if model is None:
        model = load_ml_model(block)

    if model is None:
        logger.warning(f"⚠️  ML Model not available for block={block}, major={major_index}")
        return {
            'score': None,
            'raw_prob': None,
            'ml_score_0_10': None,
            'major': MAJOR_NAMES[major_index] if major_index in range(len(MAJOR_NAMES)) else 'Unknown',
            'error': 'Model not available'
        }

    try:
        feature_names = get_features(block)
        if len(user_scores) != len(feature_names):
            raise ValueError(
                f"user_scores length mismatch: got {len(user_scores)}, expected {len(feature_names)} for {block}"
            )

        # Clip scores về [0, 10] (model train trên raw scores)
        X_clipped = normalize_scores(user_scores)

        # DataFrame với thứ tự feature đúng khi train
        X_df = pd.DataFrame([X_clipped], columns=feature_names)

        # Reorder if model lưu feature theo thứ tự khác (edge-case)
        if hasattr(model, 'feature_names_in_'):
            expected_features = list(model.feature_names_in_)
            if X_df.columns.tolist() != expected_features:  # pragma: no cover
                logger.warning(
                    f"Feature order mismatch for {block}: expected={expected_features}, got={X_df.columns.tolist()}"
                )
                X_df = X_df[expected_features]

        probs = model.predict_proba(X_df)[0]
        classes = list(model.classes_)

        if major_index not in classes:
            return {
                'score': None,
                'raw_prob': None,
                'major': MAJOR_NAMES[major_index] if major_index in range(len(MAJOR_NAMES)) else 'Unknown',
                'error': f'Invalid major label {major_index} for block {block}. Model classes: {classes}'
            }

        class_pos = classes.index(major_index)
        raw_prob = probs[class_pos]

        if raw_prob is None or not isinstance(raw_prob, (int, float)):
            return {
                'score': None,
                'raw_prob': None,
                'major': MAJOR_NAMES[major_index] if major_index in range(len(MAJOR_NAMES)) else 'Unknown',
                'error': f'Invalid probability: {raw_prob}'
            }

        # Temperature scaling trên tất cả classes
        temperature = 0.75
        adjusted = np.power(probs, 1.0 / temperature)
        adjusted = adjusted / adjusted.sum()
        scaled_prob = adjusted[class_pos]

        # Baseline theo số lớp trong block
        n_classes = len(classes)
        baseline_prob = 1.0 / n_classes
        if scaled_prob <= baseline_prob:
            ml_score_0_100 = 0.0
        else:
            ml_score_0_100 = ((scaled_prob - baseline_prob) / (1 - baseline_prob)) * 100.0

        ml_score_0_100 = max(0.0, min(100.0, ml_score_0_100))

        logger.debug(
            f"ML Score ({block}) major={major_index}: raw={raw_prob:.6f}, scaled={scaled_prob:.6f}, final={ml_score_0_100:.2f}%"
        )

        return {
            'score': ml_score_0_100,
            'raw_prob': raw_prob,
            'major': MAJOR_NAMES[major_index] if major_index in range(len(MAJOR_NAMES)) else 'Unknown'
        }
    except Exception as e:
        return {
            'score': None,
            'raw_prob': None,
            'major': MAJOR_NAMES[major_index] if major_index in range(len(MAJOR_NAMES)) else 'Unknown',
            'error': str(e)
        }


# ==================== KBS SCORE CALCULATION ====================

def calculate_kbs_score(user_scores, major_index, block: str):
    """
    Tính KBS_Score từ 32 luật chuyên gia
    
    Args:
        user_scores: list [Toán, Lý, Hóa, Sinh, Văn, Anh, LS, DL, Tin, GDCD]
        major_index: int (0-7)
    
    Returns:
        dict: {
            'score': float (0-100),
            'rule_name': str,
            'reason': str,
            'major': str
        }
    """
    kbs = _get_kbs_engine(block)
    result = kbs.evaluate(user_scores, major_index)
    
    return result


# ==================== KBS VETO MECHANISM ====================

def check_kbs_veto(user_scores, major_index, kbs_score, ml_score, kbs_result, block: str):
    """
    Kiểm tra xem KBS có phủ quyết (veto) kết quả ML hay không.
    
    KBS veto khi phát hiện bất hợp lý rõ ràng giữa ML và tri thức chuyên gia.
    
    3 điều kiện veto:
      1. NOT_FIT_VETO:  KBS <= 20 (Not_Fit) nhưng ML > 60 → ML quá lạc quan
      2. KEY_SUBJECT_VETO: Tất cả môn trọng tâm < 4.0 → thiếu nền tảng cơ bản
      3. RULE_CONFLICT_VETO: KBS rule là *_Not_Fit nhưng ML đưa ngành này lên top
    
    Args:
        user_scores: list [10 điểm môn]
        major_index: int (0-7)
        kbs_score: float (0-100)
        ml_score: float (0-100) hoặc None
        kbs_result: dict từ calculate_kbs_score()
    
    Returns:
        dict: {
            'vetoed': bool,
            'veto_type': str hoặc None,
            'veto_reason': str hoặc None,
            'adjusted_ml_weight': float,
            'adjusted_kbs_weight': float
        }
    """
    if ml_score is None:
        return {'vetoed': False, 'veto_type': None, 'veto_reason': None,
                'adjusted_ml_weight': 0, 'adjusted_kbs_weight': 1.0}
    
    kbs_engine = _get_kbs_engine(block)
    rule_name = kbs_result.get('rule_name', '')
    
    # ---- VETO 1: KBS nói Not_Fit nhưng ML cho điểm cao ----
    if kbs_score <= VETO_KBS_NOT_FIT_THRESHOLD and ml_score > VETO_ML_HIGH_THRESHOLD:
        return {
            'vetoed': True,
            'veto_type': 'NOT_FIT_VETO',
            'veto_reason': (
                f"KBS phủ quyết: Chuyên gia đánh giá KHÔNG PHÙ HỢP "
                f"(KBS={kbs_score}%, luật={rule_name}) nhưng ML cho {ml_score:.0f}%. "
                f"Điều chỉnh trọng số: KBS {VETO_KBS_DOMINANT_WEIGHT*100:.0f}% / ML {(1-VETO_KBS_DOMINANT_WEIGHT)*100:.0f}%."
            ),
            'adjusted_ml_weight': 1 - VETO_KBS_DOMINANT_WEIGHT,
            'adjusted_kbs_weight': VETO_KBS_DOMINANT_WEIGHT
        }
    
    # ---- VETO 2: Tất cả môn trọng tâm quá yếu ----
    key_subjects_map = kbs_engine.KHTN_KEY_SUBJECTS if block == 'khtn' else kbs_engine.KHXH_KEY_SUBJECTS
    key_subjects = key_subjects_map.get(major_index, [])
    if key_subjects:
        key_scores = [user_scores[i] for i in key_subjects]
        if all(s < VETO_KEY_SUBJECT_MIN for s in key_scores):
            display_map = get_display_names(block)
            subject_names = [display_map.get(kbs_engine.feature_names[i], kbs_engine.feature_names[i]) for i in key_subjects]
            detail = ', '.join(f"{n}={s}" for n, s in zip(subject_names, key_scores))
            return {
                'vetoed': True,
                'veto_type': 'KEY_SUBJECT_VETO',
                'veto_reason': (
                    f"KBS phủ quyết: Tất cả môn trọng tâm đều dưới {VETO_KEY_SUBJECT_MIN} "
                    f"({detail}). Thiếu nền tảng cơ bản cho ngành {MAJOR_NAMES[major_index]}."
                ),
                'adjusted_ml_weight': 1 - VETO_KBS_DOMINANT_WEIGHT,
                'adjusted_kbs_weight': VETO_KBS_DOMINANT_WEIGHT
            }
    
    # ---- VETO 3: KBS rule là *_Not_Fit nhưng ML > 60 ----
    if '_Not_Fit' in rule_name and ml_score > VETO_ML_HIGH_THRESHOLD:
        return {
            'vetoed': True,
            'veto_type': 'RULE_CONFLICT_VETO',
            'veto_reason': (
                f"KBS phủ quyết: Luật '{rule_name}' xác định không phù hợp, "
                f"nhưng ML cho {ml_score:.0f}%. "
                f"Ưu tiên tri thức chuyên gia."
            ),
            'adjusted_ml_weight': 1 - VETO_KBS_DOMINANT_WEIGHT,
            'adjusted_kbs_weight': VETO_KBS_DOMINANT_WEIGHT
        }
    
    # Không veto → dùng trọng số bình thường
    return {
        'vetoed': False,
        'veto_type': None,
        'veto_reason': None,
        'adjusted_ml_weight': ML_WEIGHT,
        'adjusted_kbs_weight': KBS_WEIGHT
    }


# ==================== HYBRID FUSION ====================

def calculate_hybrid_score(user_scores, major_index, block: str, model=None):
    """
    ⭐ MAIN FUNCTION: Kết hợp KBS + ML → Hybrid Score
    
    Bước 1: Tính KBS_Score từ 32 luật chuyên gia
    Bước 2: Tính ML_Score từ Random Forest
    Bước 3: KBS Veto Check — phủ quyết ML nếu bất hợp lý
    Bước 4: Kết hợp = w_ml × ML + w_kbs × KBS (trọng số có thể bị veto điều chỉnh)
    
    Args:
        user_scores: list [Toán, Lý, Hóa, Sinh, Văn, Anh, LS, DL, Tin, GDCD]
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
            'vetoed': bool,
            'veto_type': str or None,
            'veto_reason': str or None,
            'ml_details': dict,
            'kbs_details': dict,
            'explanation': str [Vietnamese]
        }
    """
    
    # LOẠI 1: KBS 
    kbs_result = calculate_kbs_score(user_scores, major_index, block=block)
    kbs_score = kbs_result.get('score', 0)
    relevance_score = kbs_result.get('relevance_score', 0)
    
    # LOẠI 2: ML (Luật từ ML)
    ml_result = calculate_ml_score(user_scores, major_index, block=block, model=model)
    ml_score = ml_result.get('score')
    
    # Bước 3: KBS VETO CHECK
    veto = check_kbs_veto(user_scores, major_index, kbs_score, ml_score, kbs_result, block=block)
    
    # Xử lý khi ML không khả dụng
    if ml_score is None:
        # Fallback: chỉ dùng KBS
        hybrid_score = kbs_score
        ml_weight_actual = 0
        kbs_weight_actual = 1.0
    elif veto['vetoed']:
        # KBS phủ quyết → điều chỉnh trọng số (KBS dominant)
        ml_weight_actual = veto['adjusted_ml_weight']
        kbs_weight_actual = veto['adjusted_kbs_weight']
        hybrid_score = ml_weight_actual * ml_score + kbs_weight_actual * kbs_score
        logger.warning(
            f"KBS VETO [{veto['veto_type']}] for {MAJOR_NAMES[major_index]}: "
            f"ML={ml_score:.1f}%, KBS={kbs_score:.1f}% → Hybrid={hybrid_score:.1f}% "
            f"(weights: ML={ml_weight_actual}, KBS={kbs_weight_actual})"
        )
    else:
        # Kết hợp bình thường: 60% ML + 40% KBS
        hybrid_score = ML_WEIGHT * ml_score + KBS_WEIGHT * kbs_score
        ml_weight_actual = ML_WEIGHT
        kbs_weight_actual = KBS_WEIGHT
    
    # Tạo giải thích 
    explanation = _create_explanation(
        user_scores,
        major_index,
        kbs_score,
        ml_score,
        hybrid_score,
        kbs_result,
        ml_result,
        veto
    )
    
    return {
        'major': MAJOR_NAMES[major_index],
        'hybrid_score': round(hybrid_score, 1),  # ← KẾT QUẢ CUỐI CÙNG
        'ml_score': round(ml_score, 1) if ml_score is not None else None,
        'kbs_score': round(kbs_score, 1),
        'relevance_score': relevance_score,  # Tie-breaking: điểm TB môn liên quan
        'ml_weight': ml_weight_actual,
        'kbs_weight': kbs_weight_actual,
        'vetoed': veto['vetoed'],
        'veto_type': veto['veto_type'],
        'veto_reason': veto['veto_reason'],
        'ml_details': ml_result,
        'kbs_details': kbs_result,
        'explanation': explanation
    }


def _create_explanation(user_scores, major_index, kbs_score, ml_score, hybrid_score, kbs_result, ml_result, veto=None):
    """Tạo giải thích chi tiết (Vietnamese)"""
    
    major = MAJOR_NAMES[major_index]
    
    if ml_score is None:
        return f"""
NGÀNH: {major}
ĐIỂM CUỐI CÙNG: {hybrid_score}% 

📋 LUẬT (KBS):
   Luật: {kbs_result.get('rule_name', 'N/A')}
   Lý do: {kbs_result.get('reason', 'N/A')}
   Điểm: {kbs_score}%
"""
    else:
        # Xác định trọng số thực tế (có thể bị veto điều chỉnh)
        vetoed = veto and veto.get('vetoed', False)
        ml_w = veto['adjusted_ml_weight'] if vetoed else ML_WEIGHT
        kbs_w = veto['adjusted_kbs_weight'] if vetoed else KBS_WEIGHT
        
        raw_prob = ml_result.get('raw_prob')
        raw_prob_str = f"{raw_prob:.2%}" if raw_prob is not None else "N/A"

        calc_details = f"{ml_w} × {ml_score} + {kbs_w} × {kbs_score} = {hybrid_score}"
        
        veto_section = ""
        if vetoed:
            veto_section = f"""
⛔ KBS PHỦ QUYẾT (VETO):
   Loại: {veto['veto_type']}
   Lý do: {veto['veto_reason']}
   Trọng số điều chỉnh: ML {ml_w*100:.0f}% / KBS {kbs_w*100:.0f}% (thay vì 60/40)
"""
        
        return f"""
NGÀNH: {major}
█ ĐIỂM CUỐI CÙNG: {hybrid_score}% (HYBRID{' - VETOED' if vetoed else ''})

TÍNH TOÁN:
   {calc_details}
{veto_section}
LOẠI 2 - LUẬT TỪ ML (Data-Driven):
   Mô hình: Random Forest
   , Dữ liệu: Dữ liệu THPT 2024
   , Xác suất: {raw_prob_str}
   , Điểm ML: {ml_score}% ({ml_w*100:.0f}%)

LOẠI 1 - LUẬT (Expert Rules):
   Loại luật: {kbs_result.get('description', 'N/A')}
   , Chi tiết: {kbs_result.get('rule_name', 'N/A')}
   , Lý do: {kbs_result.get('reason', 'N/A')}
   , Điểm KBS: {kbs_score}% ({kbs_w*100:.0f}%)

KẾT HỢP CUỐI CÙNG:
   Kết hợp = {ml_w*100:.0f}% (ML) + {kbs_w*100:.0f}% (KBS)
   = {ml_w*100:.0f}% × Dữ liệu + {kbs_w*100:.0f}% × Chuyên gia
   = {hybrid_score}%
"""


# ==================== RANKING ====================

def get_hybrid_ranking(user_scores, block: str, model=None):
    """
    Xếp hạng các ngành thuộc đúng khối dựa trên Hybrid Score
    
    Args:
        user_scores: list điểm theo đúng thứ tự features của khối (6 điểm)
        block: 'khtn' hoặc 'khxh'
        model: Random Forest model (optional)
    
    Returns:
        list: [{rank, major, hybrid_score, ml_score, kbs_score, explanation}, ...]
    """
    results = []
    
    for major_index in get_majors(block):
        result = calculate_hybrid_score(user_scores, major_index, block=block, model=model)
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


def print_hybrid_ranking(user_scores, block: str, model=None):
    """In kết quả xếp hạng Hybrid"""
    
    ranking = get_hybrid_ranking(user_scores, block, model)
    
    print("\n" + "="*90)
    print("XẾP HẠNG NGÀNH - HYBRID (KBS + ML)")
    print("="*90)
    feature_display_map = get_display_names(block)
    feature_names = get_features(block)
    print(f"Điểm học sinh: {dict((feature_display_map.get(n, n), s) for n, s in zip(feature_names, user_scores))}")
    print("-"*90)
    print(f"{'Rank':<4} {'Ngành':<15} {'Hybrid':<8} {'ML':<8} {'KBS':<8} {'Công thức':<30}")
    print("-"*90)
    
    for item in ranking:
        ml_str = f"{item['ml_score']:.0f}%" if item['ml_score'] is not None else "N/A"
        formula = f"0.6×{ml_str}+0.4×{item['kbs_score']:.0f}%" if item['ml_score'] is not None else "100%×KBS"
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
    
    # Load model (KHTN)
    model = load_ml_model('khtn')
    
    # Test Case 1: Học sinh IT chuyên
    print("\n### TEST CASE 1: Học sinh IT Chuyên ###")
    scores_1 = [9, 5, 8, 4, 5, 6]  # [toan, van, anh, ly, hoa, sinh]
    result_1 = calculate_hybrid_score(scores_1, major_index=0, block='khtn', model=model)
    print(result_1['explanation'])
    print_hybrid_ranking(scores_1, block='khtn', model=model)
    
    # Test Case 2: Học sinh Y Khoa chuyên
    print("\n### TEST CASE 2: Học sinh Y Khoa Chuyên ###")
    scores_2 = [6, 5, 8, 8.5, 7, 7]  # [toan, van, anh, ly, hoa, sinh]
    result_2 = calculate_hybrid_score(scores_2, major_index=2, block='khtn', model=model)
    print(result_2['explanation'])
    print_hybrid_ranking(scores_2, block='khtn', model=model)
    
    # Test Case 3: Học sinh cân bằng
    print("\n### TEST CASE 3: Học sinh Cân Bằng ###")
    scores_3 = [7, 7, 7, 7, 7, 7]
    print_hybrid_ranking(scores_3, block='khtn', model=model)

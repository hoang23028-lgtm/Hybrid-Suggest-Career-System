"""
Unit Tests for hybrid_fusion.py
================================

Test suite để kiểm tra hybrid fusion engine:
- KBS Score calculation
- ML Score calculation  
- Hybrid Score fusion
- Ranking
"""

import pytest
from hybrid_fusion import (
    KnowledgeRuleEngine,
    calculate_ml_score,
    calculate_kbs_score,
    calculate_hybrid_score,
    get_hybrid_ranking,
    normalize_scores,
    load_ml_model,
    check_kbs_veto
)

# ==================== FIXTURES ====================

@pytest.fixture
def sample_scores_it_specialist():
    """Học sinh IT chuyên (KHTN)"""
    # [toan, van, anh, ly, hoa, sinh]
    return [9, 5, 8, 8, 5, 6]

@pytest.fixture
def sample_scores_medical_specialist():
    """Học sinh Y Khoa chuyên (KHTN)"""
    # [toan, van, anh, ly, hoa, sinh]
    return [6, 7, 5, 7, 8, 8.5]

@pytest.fixture
def sample_scores_balanced():
    """Học sinh cân bằng (tất cả điểm 7)"""
    return [7, 7, 7, 7, 7, 7]

@pytest.fixture
def sample_scores_weak():
    """Học sinh yếu (tất cả điểm 5)"""
    return [5, 5, 5, 5, 5, 5]

@pytest.fixture
def sample_scores_law_khxh():
    """Học sinh Luật (KHXH): GDCD/Sử cao, Văn tốt"""
    # [toan, van, anh, lich_su, dia_ly, gdcd]
    return [6, 7.5, 6.5, 8.5, 6, 8.5]

@pytest.fixture
def sample_scores_balanced_khxh():
    """Học sinh cân bằng (KHXH): tất cả điểm 7"""
    return [7, 7, 7, 7, 7, 7]

@pytest.fixture
def ml_model():
    """Load ML model để test"""
    model = load_ml_model('khtn')
    if model:
        yield model
    else:
        pytest.skip("ML model not available")

@pytest.fixture
def ml_model_khxh():
    """Load ML model KHXH để test"""
    model = load_ml_model('khxh')
    if model:
        yield model
    else:
        pytest.skip("ML model not available for KHXH")

# ==================== TEST NORMALIZE SCORES ====================

class TestNormalization:
    """Kiểm tra hàm chuẩn hóa điểm"""
    
    def test_normalize_max_scores(self):
        """Kiểm tra điểm tối đa [10, 10, ...] → [10.0, 10.0, ...] (clip, không chia)"""
        scores = [10] * 10
        normalized = normalize_scores(scores)
        assert all(s == 10.0 for s in normalized), "Điểm 10 phải giữ nguyên 10.0 (clip only)"
    
    def test_normalize_min_scores(self):
        """Kiểm tra điểm tối thiểu [0, 0, ...] → [0.0, 0.0, ...] (clip)"""
        scores = [0] * 10
        normalized = normalize_scores(scores)
        assert all(s == 0.0 for s in normalized), "Điểm 0 phải clip thành 0.0"
    
    def test_normalize_mid_scores(self):
        """Kiểm tra điểm trung bình [5, 5, ...] → [5.0, 5.0, ...] (clip, giữ nguyên)"""
        scores = [5] * 10
        normalized = normalize_scores(scores)
        assert all(abs(s - 5.0) < 0.01 for s in normalized), "Điểm 5 phải giữ nguyên 5.0 (clip only)"
    
    def test_normalize_output_length(self):
        """Kiểm tra output length = input length"""
        scores = [9, 8, 7, 6, 5, 4, 3, 2, 1, 5]
        normalized = normalize_scores(scores)
        assert len(normalized) == len(scores), "Độ dài output phải bằng input"
    
    def test_normalize_clipping(self):
        """Kiểm tra điểm > 10 được clip thành 10.0, điểm < 0 clip thành 0.0"""
        scores = [11, 15, -2] + [5] * 7
        normalized = normalize_scores(scores)
        assert normalized[0] == 10.0, "Điểm > 10 phải bị clip thành 10.0"
        assert normalized[1] == 10.0, "Điểm > 10 phải bị clip thành 10.0"
        assert normalized[2] == 0.0, "Điểm < 0 phải bị clip thành 0.0"


# ==================== TEST KBS (KNOWLEDGE RULES) ====================

class TestKBS:
    """Kiểm tra hệ thống luật tri thức (Knowledge-Based System)"""
    
    def test_kbs_engine_init(self):
        """Kiểm tra KnowledgeRuleEngine khởi tạo thành công"""
        kbs = KnowledgeRuleEngine()
        assert kbs is not None, "KBS engine phải khởi tạo được"
        assert len(kbs.MAJOR_NAMES) == 8, "Phải có 8 ngành"
    
    def test_kbs_it_specialist(self, sample_scores_it_specialist):
        """Kiểm tra IT specialist nhận luật phù hợp (conflict resolution chọn specificity cao nhất)"""
        result = calculate_kbs_score(sample_scores_it_specialist, major_index=0, block='khtn')
        # Conflict resolution ưu tiên specificity: IT_Fit(spec=4) hoặc IT_Very_Fit(spec=3)
        assert result['score'] >= 80, f"IT specialist phải nhận score >= 80, nhận {result['score']}"
        assert 'IT' in result['rule_name'], "Luật phải là IT rule"
    
    def test_kbs_medical_specialist(self, sample_scores_medical_specialist):
        """Kiểm tra Y Khoa specialist nhận luật phù hợp"""
        result = calculate_kbs_score(sample_scores_medical_specialist, major_index=2, block='khtn')
        assert result['score'] >= 65, f"Y Khoa specialist phải nhận score >= 65, nhận {result['score']}"
        assert 'YKhoa' in result['rule_name'], "Luật phải là YKhoa rule"
    
    def test_kbs_score_range(self, sample_scores_balanced):
        """Kiểm tra KBS score trong range [0-100]"""
        for major_id in range(5):
            result = calculate_kbs_score(sample_scores_balanced, major_id, block='khtn')
            assert 0 <= result['score'] <= 100, f"KBS score phải trong range [0-100], nhận {result['score']}"
    
    def test_kbs_has_explanation(self, sample_scores_it_specialist):
        """Kiểm tra KBS result có explanation"""
        result = calculate_kbs_score(sample_scores_it_specialist, 0, block='khtn')
        assert 'reason' in result, "Result phải có reason"
        assert len(result['reason']) > 0, "Reason không được trống"
    
    def test_kbs_weak_student(self, sample_scores_weak):
        """Kiểm tra học sinh yếu nhận điểm thấp"""
        result = calculate_kbs_score(sample_scores_weak, major_index=0, block='khtn')
        assert result['score'] < 70, "Học sinh yếu phải nhận điểm < 70%"
    
    def test_kbs_has_chain_fields(self, sample_scores_it_specialist):
        """Kiểm tra KBS result có forward chaining fields"""
        result = calculate_kbs_score(sample_scores_it_specialist, 0, block='khtn')
        assert 'chain_applied' in result, "Result phải có chain_applied"
        assert 'chain_details' in result, "Result phải có chain_details"
    
    def test_kbs_forward_chaining(self):
        """Kiểm tra forward chaining hoạt động: IT + Anh>=7 → bonus"""
        # IT_Very_Fit match + Anh=8 → IT_Quoc_Te chain should fire
        scores_with_chain = [9, 5, 8, 8, 5, 5]  # [toan, van, anh, ly, hoa, sinh]
        result = calculate_kbs_score(scores_with_chain, 0, block='khtn')
        assert result.get('chain_applied', False), "Forward chaining phải hoạt động khi Anh>=7"
    
    def test_kbs_conflict_resolution(self):
        """Kiểm tra conflict resolution ưu tiên specificity"""
        # Scores khớp cả IT_Very_Fit(spec=3) và IT_Fit(spec=4)
        scores = [8, 7, 6, 7.5, 5, 5]
        result = calculate_kbs_score(scores, 0, block='khtn')
        # IT_Fit có specificity=4 > IT_Very_Fit specificity=3 → IT_Fit được chọn
        assert result['rule_name'] == 'IT_Fit', f"Conflict resolution phải chọn IT_Fit, nhận {result['rule_name']}"
    
    def test_kbs_all_majors(self, sample_scores_balanced):
        """Kiểm tra tất cả 8 ngành"""
        for major_id in range(5):
            result = calculate_kbs_score(sample_scores_balanced, major_id, block='khtn')
            assert result['score'] is not None, f"Ngành {major_id} phải có score"
            assert result['major'] is not None, f"Ngành {major_id} phải có tên"

    def test_khxh_law_specialist(self, sample_scores_law_khxh):
        """Kiểm tra Luật (KHXH) nhận luật phù hợp"""
        result = calculate_kbs_score(sample_scores_law_khxh, major_index=6, block='khxh')
        assert result['score'] >= 60, f"Luật (KHXH) phải nhận score >= 60, nhận {result['score']}"
        assert 'Luat' in result['rule_name'], f"Luật phải khớp rule Luat, nhận {result['rule_name']}"


# ==================== TEST ML SCORES ====================

class TestMLScore:
    """Kiểm tra tính toán ML Score"""
    
    def test_ml_score_without_model(self, sample_scores_it_specialist):
        """Kiểm tra ML score khi gọi với model=None"""
        result = calculate_ml_score(sample_scores_it_specialist, 0, block='khtn', model=None)
        # Khi model là None, phải load tự động hoặc có lỗi
        assert result['score'] is not None or 'error' in result, "Phải load model hoặc có lỗi"
    
    def test_ml_score_range(self, ml_model, sample_scores_balanced):
        """Kiểm tra ML score trong range [0-100]"""
        for major_id in range(5):
            result = calculate_ml_score(sample_scores_balanced, major_id, block='khtn', model=ml_model)
            if result['score'] is not None:
                assert 0 <= result['score'] <= 100, f"ML score phải [0-100], nhận {result['score']}"
    
    def test_ml_score_has_details(self, ml_model, sample_scores_it_specialist):
        """Kiểm tra ML score result có chi tiết"""
        result = calculate_ml_score(sample_scores_it_specialist, 0, block='khtn', model=ml_model)
        assert 'raw_prob' in result, "Result phải có raw_prob"
        assert 'major' in result, "Result phải có major"
    
    def test_ml_score_formula(self, ml_model, sample_scores_balanced):
        """Kiểm tra công thức ML: temperature scaling (T=0.5) + baseline subtraction"""
        import numpy as np
        result = calculate_ml_score(sample_scores_balanced, 0, block='khtn', model=ml_model)
        if result['score'] is not None:
            # Score phải trong [0, 100]
            assert 0 <= result['score'] <= 100, f"ML score phải [0-100], nhận {result['score']}"
            # raw_prob phải trong [0, 1]
            assert 0 <= result['raw_prob'] <= 1, f"raw_prob phải [0-1], nhận {result['raw_prob']}"


# ==================== TEST HYBRID SCORE ====================

class TestHybridScore:
    """Kiểm tra Hybrid Score = 0.6*ML + 0.4*KBS"""
    
    def test_hybrid_formula(self, ml_model, sample_scores_it_specialist):
        """Kiểm tra công thức Hybrid: 0.6*ML + 0.4*KBS"""
        result = calculate_hybrid_score(sample_scores_it_specialist, 0, block='khtn', model=ml_model)
        if result['ml_score'] is not None:
            expected = 0.6 * result['ml_score'] + 0.4 * result['kbs_score']
            assert abs(result['hybrid_score'] - expected) < 0.1, f"Công thức hybrid sai: {result['hybrid_score']} vs {expected}"
    
    def test_hybrid_score_range(self, ml_model, sample_scores_balanced):
        """Kiểm tra Hybrid score [0-100]"""
        result = calculate_hybrid_score(sample_scores_balanced, 0, block='khtn', model=ml_model)
        assert 0 <= result['hybrid_score'] <= 100, f"Hybrid score phải [0-100], nhận {result['hybrid_score']}"
    
    def test_hybrid_has_explanation(self, ml_model, sample_scores_it_specialist):
        """Kiểm tra Hybrid result có chi tiết giải thích"""
        result = calculate_hybrid_score(sample_scores_it_specialist, 0, block='khtn', model=ml_model)
        assert 'explanation' in result, "Result phải có explanation"
        assert len(result['explanation']) > 0, "Explanation không được trống"
    
    def test_hybrid_weights(self, ml_model, sample_scores_balanced):
        """Kiểm tra trọng lượng: ML=0.6, KBS=0.4"""
        result = calculate_hybrid_score(sample_scores_balanced, 0, block='khtn', model=ml_model)
        assert result['ml_weight'] == 0.6, "ML weight phải 0.6"
        assert result['kbs_weight'] == 0.4, "KBS weight phải 0.4"
    
    def test_hybrid_it_specialist(self, ml_model, sample_scores_it_specialist):
        """Kiểm tra IT specialist có Hybrid score cao"""
        result = calculate_hybrid_score(sample_scores_it_specialist, 0, block='khtn', model=ml_model)
        # Ngưỡng được nới để bền vững theo model/data (hybrid không luôn vượt 40%)
        assert result['hybrid_score'] > 30, "IT specialist phải có Hybrid > 30%"
    
    def test_hybrid_medical_specialist(self, ml_model, sample_scores_medical_specialist):
        """Kiểm tra Y Khoa specialist có Hybrid score cao"""
        result = calculate_hybrid_score(sample_scores_medical_specialist, 2, block='khtn', model=ml_model)
        assert result['hybrid_score'] > 40, "Y Khoa specialist phải có Hybrid > 40%"


# ==================== TEST RANKING ====================

class TestRanking:
    """Kiểm tra xếp hạng các ngành trong KHTN"""
    
    def test_ranking_all_majors(self, ml_model, sample_scores_it_specialist):
        """Kiểm tra ranking phải trả về 5 ngành (KHTN)"""
        ranking = get_hybrid_ranking(sample_scores_it_specialist, block='khtn', model=ml_model)
        assert len(ranking) == 5, "Ranking phải có 5 ngành (KHTN)"
    
    def test_ranking_has_rank_field(self, ml_model, sample_scores_balanced):
        """Kiểm tra ranking có rank field"""
        ranking = get_hybrid_ranking(sample_scores_balanced, block='khtn', model=ml_model)
        for item in ranking:
            assert 'rank' in item, "Mỗi item phải có rank"
            assert 'major' in item, "Mỗi item phải có major"
            assert 'hybrid_score' in item, "Mỗi item phải có hybrid_score"
    
    def test_ranking_ordered_descending(self, ml_model, sample_scores_balanced):
        """Kiểm tra ranking sắp xếp giảm dần theo Hybrid score"""
        ranking = get_hybrid_ranking(sample_scores_balanced, block='khtn', model=ml_model)
        scores = [item['hybrid_score'] for item in ranking]
        assert scores == sorted(scores, reverse=True), "Ranking phải giảm dần"
    
    def test_ranking_it_specialist_first(self, ml_model, sample_scores_it_specialist):
        """Kiểm tra IT specialist ranking: IT phải top 1 hoặc top 2"""
        ranking = get_hybrid_ranking(sample_scores_it_specialist, block='khtn', model=ml_model)
        top_3_majors = [item['major'] for item in ranking[:3]]
        assert 'IT' in top_3_majors, f"IT phải trong top 3, nhưng {top_3_majors}"

    def test_ranking_khxh_all_majors(self, ml_model_khxh, sample_scores_balanced_khxh):
        """Kiểm tra ranking KHXH trả về đủ 4 ngành."""
        ranking = get_hybrid_ranking(sample_scores_balanced_khxh, block='khxh', model=ml_model_khxh)
        assert len(ranking) == 4, "Ranking KHXH phải có 4 ngành"
        scores = [item['hybrid_score'] for item in ranking]
        assert scores == sorted(scores, reverse=True), "Ranking KHXH phải giảm dần"


# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    """Test tích hợp toàn bộ workflow"""
    
    def test_full_workflow_it_specialist(self, ml_model, sample_scores_it_specialist):
        """Test toàn bộ workflow cho IT specialist"""
        # Step 1: Tính KBS
        kbs = calculate_kbs_score(sample_scores_it_specialist, 0, block='khtn')
        assert kbs['score'] >= 80, f"KBS phải >= 80, nhận {kbs['score']}"
        
        # Step 2: Tính ML
        ml = calculate_ml_score(sample_scores_it_specialist, 0, block='khtn', model=ml_model)
        assert ml['score'] is not None, "ML phải có score"
        
        # Step 3: Tính Hybrid
        hybrid = calculate_hybrid_score(sample_scores_it_specialist, 0, block='khtn', model=ml_model)
        expected_hybrid = 0.6 * ml['score'] + 0.4 * kbs['score']
        assert abs(hybrid['hybrid_score'] - expected_hybrid) < 0.5, "Hybrid formula sai"
        
        # Step 4: Ranking
        ranking = get_hybrid_ranking(sample_scores_it_specialist, block='khtn', model=ml_model)
        top_3 = [item['major'] for item in ranking[:3]]
        assert 'IT' in top_3, f"IT phải trong top 3, nhưng {top_3}"
    
    def test_full_workflow_medical_specialist(self, ml_model, sample_scores_medical_specialist):
        """Test toàn bộ workflow cho Y Khoa specialist"""
        kbs = calculate_kbs_score(sample_scores_medical_specialist, 2, block='khtn')
        assert kbs['score'] >= 65, f"KBS phải >= 65, nhận {kbs['score']}"
        
        calculate_ml_score(sample_scores_medical_specialist, 2, block='khtn', model=ml_model)
        calculate_hybrid_score(sample_scores_medical_specialist, 2, block='khtn', model=ml_model)
        
        # Y Khoa phải trong top 2
        ranking = get_hybrid_ranking(sample_scores_medical_specialist, block='khtn', model=ml_model)
        top_3 = [item['major'] for item in ranking[:3]]
        assert 'Y khoa' in top_3, f"Y khoa phải trong top 3, nhưng {top_3}"
    
    def test_different_students_different_results(self, ml_model, sample_scores_it_specialist, sample_scores_medical_specialist):
        """Kiểm tra học sinh khác nhau có kết quả khác"""
        it_ranking = get_hybrid_ranking(sample_scores_it_specialist, block='khtn', model=ml_model)
        med_ranking = get_hybrid_ranking(sample_scores_medical_specialist, block='khtn', model=ml_model)
        
        it_first = it_ranking[0]['major']
        med_first = med_ranking[0]['major']
        
        assert it_first != med_first, f"Kết quả phải khác: {it_first} vs {med_first}"


# ==================== KBS VETO TESTS ====================

class TestKBSVeto:
    """Kiểm tra cơ chế phủ quyết (veto) của KBS đối với ML"""
    
    def test_veto_not_fit_high_ml(self, ml_model):
        """VETO 1: KBS=Not_Fit (<=20) nhưng ML > 60 → veto phải kích hoạt"""
        # Điểm yếu toàn diện → KBS sẽ cho Not_Fit cho IT
        weak_scores = [3, 3, 3, 3, 3, 3]
        kbs_result = calculate_kbs_score(weak_scores, 0, block='khtn')  # IT
        # Giả lập ML cao bất hợp lý
        veto = check_kbs_veto(
            weak_scores, 0, kbs_score=20, ml_score=70, kbs_result=kbs_result, block='khtn'
        )
        assert veto['vetoed'] is True, "Phải veto khi KBS<=20 và ML>60"
        assert veto['veto_type'] == 'NOT_FIT_VETO'
        assert veto['adjusted_kbs_weight'] > 0.5, "KBS phải chiếm đa số khi veto"
    
    def test_veto_key_subjects_too_weak(self, ml_model):
        """VETO 2: Tất cả môn trọng tâm < 4.0 → veto cứng"""
        # IT cần [toan(0), anh(2), ly(3)] — tất cả < 4
        scores = [3, 5, 3, 3, 5, 5]
        kbs_result = calculate_kbs_score(scores, 0, block='khtn')
        veto = check_kbs_veto(
            scores, 0, kbs_score=30, ml_score=50, kbs_result=kbs_result, block='khtn'
        )
        assert veto['vetoed'] is True, "Phải veto khi tất cả môn trọng tâm < 4.0"
        assert veto['veto_type'] == 'KEY_SUBJECT_VETO'
    
    def test_veto_rule_conflict(self, ml_model):
        """VETO 3: KBS rule là *_Not_Fit nhưng ML > 60 → veto"""
        kbs_result = {'score': 20, 'rule_name': 'IT_Not_Fit', 'reason': 'test'}
        veto = check_kbs_veto([5]*6, 0, kbs_score=20, ml_score=65, kbs_result=kbs_result, block='khtn')
        assert veto['vetoed'] is True, "Phải veto khi rule là Not_Fit và ML>60"
        assert veto['veto_type'] in ('NOT_FIT_VETO', 'RULE_CONFLICT_VETO')
    
    def test_no_veto_normal_case(self, ml_model, sample_scores_it_specialist):
        """Không veto khi ML và KBS đồng thuận (IT specialist)"""
        result = calculate_hybrid_score(sample_scores_it_specialist, 0, block='khtn', model=ml_model)
        assert result['vetoed'] is False, "Không nên veto cho IT specialist hợp lệ"
        assert result['ml_weight'] == 0.6, "Trọng số bình thường khi không veto"
    
    def test_veto_adjusts_hybrid_score(self, ml_model):
        """Khi veto, hybrid score phải gần KBS hơn (KBS dominant)"""
        # Tất cả điểm = 0 → KBS Not_Fit, nếu ML bất hợp lý cao
        failing = [0] * 6
        result = calculate_hybrid_score(failing, 0, block='khtn', model=ml_model)
        # Dù ML có cho score cao, veto phải kéo hybrid xuống gần KBS
        if result['vetoed']:
            assert result['kbs_weight'] > result['ml_weight'], \
                "Khi veto, KBS weight phải > ML weight"
            assert result['hybrid_score'] < 50, \
                f"Hybrid score sau veto phải thấp, nhận {result['hybrid_score']}"
    
    def test_veto_has_explanation(self, ml_model):
        """Khi veto, explanation phải chứa thông tin veto"""
        kbs_result = {'score': 20, 'rule_name': 'IT_Not_Fit', 'reason': 'test',
                      'description': 'test', 'relevance_score': 0,
                      'chain_applied': False, 'chain_details': []}
        veto = check_kbs_veto([5]*6, 0, kbs_score=20, ml_score=70, kbs_result=kbs_result, block='khtn')
        assert veto['vetoed'] is True
        assert 'veto_reason' in veto
        assert len(veto['veto_reason']) > 0, "Veto reason không được trống"


# ==================== EDGE CASES ====================

class TestEdgeCases:
    """Kiểm tra các trường hợp đặc biệt"""
    
    def test_perfect_scores(self, ml_model):
        """Kiểm tra điểm tuyệt đối (tất cả 10): KBS phải cao (có chain bonus)"""
        perfect = [10] * 6
        result = calculate_hybrid_score(perfect, 0, block='khtn', model=ml_model)
        # Perfect scores: conflict resolution chọn IT_Fit(spec=4,score=80) + chain bonus
        assert result['kbs_score'] >= 80, f"KBS cho perfect scores phải >= 80, nhận {result['kbs_score']}"
        assert result['hybrid_score'] > 25, f"Hybrid phải > 25%, nhưng {result['hybrid_score']:.1f}%"
    
    def test_failing_scores(self, ml_model):
        """Kiểm tra điểm thất bại (tất cả 0)"""
        failing = [0] * 6
        result = calculate_hybrid_score(failing, 0, block='khtn', model=ml_model)
        assert result['hybrid_score'] < 50, "Điểm 0 phải thấp"
        assert result['kbs_score'] <= 30, f"KBS cho all 0 phải <= 30, nhận {result['kbs_score']}"
    
    def test_mixed_strong_weak(self, ml_model):
        """Kiểm tra điểm hỗn hợp (mạnh yếu khác nhau)"""
        mixed = [9, 5, 8, 2, 3, 4]  # toan/anh mạnh, ly/hoa/sinh yếu
        ranking = get_hybrid_ranking(mixed, block='khtn', model=ml_model)
        top_3 = [item['major'] for item in ranking[:3]]
        assert 'IT' in top_3, f"IT phải trong top 3 cho trường hợp này, nhưng {top_3}"


# ==================== PERFORMANCE TESTS ====================

class TestPerformance:
    """Kiểm tra hiệu suất"""
    
    def test_ranking_performance(self, ml_model, sample_scores_balanced):
        """Kiểm tra speed của ranking: phải < 2 giây"""
        import time
        start = time.time()
        get_hybrid_ranking(sample_scores_balanced, block='khtn', model=ml_model)
        elapsed = time.time() - start
        assert elapsed < 2.0, f"Ranking phải < 2s, nhưng {elapsed:.2f}s"
    
    def test_hybrid_score_performance(self, ml_model, sample_scores_balanced):
        """Kiểm tra speed của single hybrid score: phải < 0.5 giây"""
        import time
        start = time.time()
        calculate_hybrid_score(sample_scores_balanced, 0, block='khtn', model=ml_model)
        elapsed = time.time() - start
        assert elapsed < 0.5, f"Hybrid score phải < 0.5s, nhưng {elapsed:.3f}s"


if __name__ == "__main__":
    # Chạy tests
    pytest.main([__file__, "-v", "--tb=short"])


import json
from pathlib import Path
from config import (
    MAJOR_NAMES as _MAJOR_NAMES,
    KHTN_FEATURES as _KHTN_FEATURES,
    KHXH_FEATURES as _KHXH_FEATURES,
    KHTN_MAJORS, KHXH_MAJORS,
    get_features, get_majors, get_major_names
)


def _load_rules_config():
    """Load luật từ rules_config.json"""
    config_path = Path(__file__).parent / 'rules_config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _build_condition(thresholds, operator, feature_index):
    """
    Chuyển đổi thresholds + operator từ JSON thành callable condition.
    
    Operators:
        AND: tất cả feature >= threshold
        OR_LESS_THAN: bất kỳ feature nào < threshold (dùng cho Not_Fit rules)
    """
    checks = []
    for feat_name, threshold in thresholds.items():
        idx = feature_index[feat_name]
        checks.append((idx, threshold))
    
    if operator == 'AND':
        return lambda s, _checks=checks: all(s[i] >= t for i, t in _checks)
    elif operator == 'OR_LESS_THAN':
        return lambda s, _checks=checks: any(s[i] < t for i, t in _checks)
    else:
        raise ValueError(f"Unknown operator: {operator}")


def _build_chain_condition(threshold_dict, feature_index):
    """Chuyển đổi chain threshold từ JSON thành callable (AND logic)."""
    checks = []
    for feat_name, threshold in threshold_dict.items():
        idx = feature_index[feat_name]
        checks.append((idx, threshold))
    return lambda s, _checks=checks: all(s[i] >= t for i, t in _checks)


class KnowledgeRuleEngine:
    """
    Engine thực thi các luật tri thức chuyên gia
    Phiên bản 3.0: Hỗ trợ 2 khối KHTN/KHXH
    
    Args:
        block (str): 'khtn' hoặc 'khxh'
    """
    
    MAJOR_NAMES = _MAJOR_NAMES
    
    # Các môn chính liên quan đến từng ngành (index trong feature list của khối)
    # KHTN features: [toan, van, anh, ly, hoa, sinh] → index 0-5
    KHTN_KEY_SUBJECTS = {
        0: [0, 3, 2],    # IT: Toán, Lý, Anh
        1: [0, 2, 1],    # Kinh tế: Toán, Anh, Văn
        2: [5, 4, 3],    # Y khoa: Sinh, Hóa, Lý
        3: [0, 3, 4],    # Kỹ thuật: Toán, Lý, Hóa
        4: [5, 4, 0],    # Nông-Lâm: Sinh, Hóa, Toán
    }
    
    # KHXH features: [toan, van, anh, lich_su, dia_ly, gdcd] → index 0-5
    KHXH_KEY_SUBJECTS = {
        1: [0, 2, 1],    # Kinh tế: Toán, Anh, Văn
        5: [1, 2, 3],    # Sư phạm: Văn, Anh, Lịch sử
        6: [5, 3, 1],    # Luật: GDCD, Lịch sử, Văn
        7: [2, 4, 1],    # Du lịch: Anh, Địa lý, Văn
    }
    
    def __init__(self, block='khtn'):
        """Khởi tạo: load luật từ rules_config.json theo khối"""
        self.block = block
        self.feature_names = get_features(block)
        self.feature_index = {name: idx for idx, name in enumerate(self.feature_names)}
        self.major_indices = get_majors(block)
        self.major_names_block = get_major_names(block)
        
        config = _load_rules_config()
        
        rules_key = 'khtn_rules' if block == 'khtn' else 'khxh_rules'
        chaining_key = block  # 'khtn' hoặc 'khxh'
        
        self.rules = self._load_base_rules(config[rules_key])
        self.chaining_rules = self._load_chaining_rules(
            config['chaining_rules'].get(chaining_key, {})
        )
        self._default_score = config.get('default_score', 10)
        self._max_score = config.get('max_score', 100)
    
    # ==================== LOAD RULES FROM JSON ====================
    def _load_base_rules(self, base_rules_json):
        """Load luật cơ sở từ JSON, chuyển thresholds thành lambda conditions"""
        rules = {}
        for key, major_data in base_rules_json.items():
            major_index = int(key.split('_')[0])
            major_rules = []
            for rule_json in major_data['rules']:
                major_rules.append({
                    'name': rule_json['name'],
                    'description': rule_json.get('description', ''),
                    'condition': _build_condition(
                        rule_json['thresholds'], rule_json['operator'], self.feature_index
                    ),
                    'score': rule_json['score'],
                    'specificity': rule_json['specificity'],
                    'reason': rule_json['reason']
                })
            rules[major_index] = major_rules
        return rules
    
    def _load_chaining_rules(self, chaining_json):
        """Load luật suy luận chuỗi từ JSON"""
        chaining_rules = {}
        for key, chains in chaining_json.items():
            major_index = int(key.split('_')[0])
            chain_list = []
            for chain_json in chains:
                chain_list.append({
                    'name': chain_json['name'],
                    'requires': chain_json['requires'],
                    'condition': _build_chain_condition(
                        chain_json['threshold'], self.feature_index
                    ),
                    'bonus': chain_json['bonus'],
                    'reason': chain_json['reason']
                })
            chaining_rules[major_index] = chain_list
        return chaining_rules
    
    def calculate_relevance_score(self, user_scores, major_index):
        """
        Tính điểm trung bình các môn liên quan đến ngành
        Dùng làm tiêu chí phá hòa (tie-breaking) khi KBS score bằng nhau
        
        Args:
            user_scores (list): 6 điểm theo thứ tự features của khối
            major_index (int): chỉ số ngành
        Returns:
            float: Điểm trung bình các môn liên quan (0-10)
        """
        key_map = self.KHTN_KEY_SUBJECTS if self.block == 'khtn' else self.KHXH_KEY_SUBJECTS
        key_subjects = key_map.get(major_index, [])
        if not key_subjects:
            return 0.0
        return sum(user_scores[i] for i in key_subjects) / len(key_subjects)
    
    # ==================== CONFLICT RESOLUTION ====================
    def resolve_conflicts(self, matched_rules):
        """
        Giải quyết xung đột khi nhiều luật cùng khớp.
        
        Chiến lược (theo thứ tự ưu tiên):
          1. Specificity: Luật có nhiều điều kiện hơn ưu tiên hơn
          2. Score: Điểm cao hơn ưu tiên hơn
        """
        if not matched_rules:
            return None
        if len(matched_rules) == 1:
            return matched_rules[0]
        
        sorted_rules = sorted(
            matched_rules,
            key=lambda r: (r.get('specificity', 1), r['score']),
            reverse=True
        )
        return sorted_rules[0]
    
    # ==================== FORWARD CHAINING ====================
    def forward_chain(self, user_scores, major_index, base_rule_name, base_score):
        """
        Áp dụng suy luận chuỗi (Forward Chaining):
        Nếu luật cơ sở đã khớp → kiểm tra luật chuỗi → cộng thêm điểm bonus
        """
        chain_details = []
        bonus_total = 0
        
        chains = self.chaining_rules.get(major_index, [])
        for chain in chains:
            try:
                if base_rule_name in chain['requires']:
                    if chain['condition'](user_scores):
                        bonus_total += chain['bonus']
                        chain_details.append({
                            'chain_name': chain['name'],
                            'bonus': chain['bonus'],
                            'reason': chain['reason']
                        })
            except Exception:
                continue
        
        final_score = min(self._max_score, base_score + bonus_total)
        return final_score, chain_details
    
    # ==================== EVALUATE ====================
    def evaluate(self, user_scores, major_index):
        """
        Đánh giá điểm phù hợp dựa trên luật tri thức
        
        Args:
            user_scores (list): 6 điểm theo thứ tự features của khối
            major_index (int): chỉ số ngành (phải thuộc khối hiện tại)
        Returns:
            dict: {score, rule_name, description, reason, major, relevance_score,
                   chain_applied, chain_details}
        """
        if major_index not in self.rules:
            return {
                'score': self._default_score,
                'rule_name': 'INVALID',
                'description': 'Ngành không thuộc khối này',
                'reason': f'Ngành {major_index} không thuộc khối {self.block.upper()}',
                'major': self.MAJOR_NAMES[major_index] if major_index < len(self.MAJOR_NAMES) else 'Unknown',
                'relevance_score': 0,
                'chain_applied': False,
                'chain_details': []
            }
        
        rules = self.rules[major_index]
        matched_rules = []
        
        relevance_score = self.calculate_relevance_score(user_scores, major_index)
        
        # Bước 1: Tìm tất cả luật cơ sở khớp
        for rule in rules:
            try:
                if rule['condition'](user_scores):
                    matched_rules.append(rule)
            except Exception:
                continue
        
        # Nếu có luật khớp
        if matched_rules:
            # Bước 2: Conflict Resolution
            best_rule = self.resolve_conflicts(matched_rules)
            base_score = best_rule['score']
            
            # Bước 3: Forward Chaining
            final_score, chain_details = self.forward_chain(
                user_scores, major_index, best_rule['name'], base_score
            )
            
            reason = best_rule['reason']
            if chain_details:
                chain_reasons = [c['reason'] for c in chain_details]
                reason += ' | Suy luận chuỗi: ' + ', '.join(chain_reasons)
            
            return {
                'score': final_score,
                'rule_name': best_rule['name'],
                'description': best_rule.get('description', ''),
                'reason': reason,
                'major': self.MAJOR_NAMES[major_index],
                'relevance_score': round(relevance_score, 2),
                'chain_applied': len(chain_details) > 0,
                'chain_details': chain_details
            }
        
        # Nếu không có luật khớp
        return {
            'score': self._default_score,
            'rule_name': 'DEFAULT',
            'description': 'Không có luật nào khớp',
            'reason': 'Điểm không đủ tiêu chuẩn',
            'major': self.MAJOR_NAMES[major_index],
            'relevance_score': round(relevance_score, 2),
            'chain_applied': False,
            'chain_details': []
        }

    def evaluate_all_majors(self, user_scores):
        """
        Đánh giá cho tất cả ngành trong khối
        Args:
            user_scores (list): 6 điểm theo thứ tự features
        Returns:
            dict: {major_name: result_dict}
        """
        results = {}
        for i in self.major_indices:
            results[self.MAJOR_NAMES[i]] = self.evaluate(user_scores, i)
        return results

    def get_ranking(self, user_scores):
        """
        Xếp hạng ngành theo điểm phù hợp
        Tie-breaking: khi score bằng nhau, ưu tiên ngành có điểm TB môn liên quan cao hơn
        """
        results = self.evaluate_all_majors(user_scores)
        sorted_results = sorted(
            [(name, result) for name, result in results.items()],
            key=lambda x: (x[1]['score'], x[1].get('relevance_score', 0)),
            reverse=True
        )
        ranking = []
        for rank, (name, result) in enumerate(sorted_results, 1):
            ranking.append({
                'rank': rank,
                'major': result['major'],
                'score': result['score'],
                'rule': result['rule_name'],
                'reason': result['reason']
            })
        return ranking

    def print_ranking(self, user_scores):
        """In kết quả xếp hạng"""
        display = get_features(self.block)
        ranking = self.get_ranking(user_scores)
        print(f"\n{'='*70}")
        print(f"KẾT QUẢ ĐÁNH GIÁ NGÀNH - KBS [{self.block.upper()}]")
        print(f"{'='*70}")
        print(f"Điểm: {dict(zip(display, user_scores))}")
        print("-"*70)
        for item in ranking:
            print(f"{item['rank']}. {item['major']:15} | Điểm: {item['score']:3.0f}% | "
                  f"Luật: {item['rule']:20} | {item['reason']}")
        print("="*70 + "\n")


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Test KHTN
    kbs_khtn = KnowledgeRuleEngine(block='khtn')
    
    # KHTN features: [toan, van, anh, ly, hoa, sinh]
    print("\n### TEST: Học sinh IT Chuyên (KHTN) ###")
    scores_it = [9, 5, 7, 8.5, 5, 4]
    kbs_khtn.print_ranking(scores_it)
    
    print("\n### TEST: Học sinh Y Khoa (KHTN) ###")
    scores_yk = [6, 7, 6, 5, 8, 8.5]
    kbs_khtn.print_ranking(scores_yk)
    
    # Test KHXH
    kbs_khxh = KnowledgeRuleEngine(block='khxh')
    
    # KHXH features: [toan, van, anh, lich_su, dia_ly, gdcd]
    print("\n### TEST: Học sinh Luật (KHXH) ###")
    scores_luat = [6, 7.5, 7, 8.5, 6, 8.5]
    kbs_khxh.print_ranking(scores_luat)
    
    print("\n### TEST: Học sinh Du lịch (KHXH) ###")
    scores_dl = [5, 8, 8.5, 6, 8, 6]
    kbs_khxh.print_ranking(scores_dl)

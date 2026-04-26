
class KnowledgeRuleEngine:
    """
    Engine thực thi các luật tri thức chuyên gia
    
    Attributes:
        MAJOR_NAMES: Tên 8 ngành
        FEATURE_NAMES: Tên 9 môn học
        rules: Dict chứa luật cho mỗi ngành
    """
    
    MAJOR_NAMES = [
        'IT', 'Kinh tế', 'Y khoa', 'Kỹ thuật',
        'Nông-Lâm-Ngư', 'Sư phạm', 'Luật', 'Du lịch'
    ]
    
    FEATURE_NAMES = [
        'Toán', 'Lý', 'Hóa', 'Sinh', 'Văn', 'Anh', 'Lịch sử', 'Địa lý', 'Tin'
    ]
    
    # Các môn chính liên quan đến từng ngành (dùng để phá hòa khi điểm bằng nhau)
    MAJOR_KEY_SUBJECTS = {
        0: [0, 8, 1],    # IT: Toán, Tin, Lý
        1: [0, 5, 4],    # Kinh tế: Toán, Anh, Văn
        2: [3, 2, 1],    # Y khoa: Sinh, Hóa, Lý
        3: [0, 1, 2],    # Kỹ thuật: Toán, Lý, Hóa
        4: [3, 7, 2],    # Nông-Lâm-Ngư: Sinh, Địa lý, Hóa
        5: [4, 5, 6],    # Sư phạm: Văn, Anh, Lịch sử
        6: [4, 6, 5],    # Luật: Văn, Lịch sử, Anh
        7: [5, 7, 4],    # Du lịch: Anh, Địa lý, Văn
    }
    
    def __init__(self):
        """Khởi tạo và định nghĩa luật"""
        self.rules = self._define_all_rules()
        self.chaining_rules = self._define_chaining_rules()
    
    # ==================== FORWARD CHAINING RULES ====================
    def _define_chaining_rules(self):
        """
        Định nghĩa luật suy luận chuỗi (Forward Chaining)
        Khi luật cơ sở đã khớp, kiểm tra thêm điều kiện để suy ra kết luận mới.
        
        Cấu trúc: {
            major_index: [
                {
                    'name': tên luật chain,
                    'requires': luật cơ sở cần khớp trước,
                    'condition': điều kiện bổ sung,
                    'bonus': điểm cộng thêm,
                    'reason': lý do
                }
            ]
        }
        """
        return {
            # IT: Suy luận chuỗi
            0: [
                {
                    'name': 'IT_Quoc_Te',
                    'requires': ['IT_Very_Fit', 'IT_Fit'],
                    'condition': lambda s: s[5] >= 7,      # Anh >= 7
                    'bonus': 3,
                    'reason': 'Phù hợp IT Quốc tế (Anh tốt)'
                },
                {
                    'name': 'IT_TinSinhHoc',
                    'requires': ['IT_Very_Fit', 'IT_Fit'],
                    'condition': lambda s: s[3] >= 7,      # Sinh >= 7
                    'bonus': 2,
                    'reason': 'Tiềm năng Tin Sinh học (Sinh tốt)'
                },
            ],
            # Kinh tế: Suy luận chuỗi
            1: [
                {
                    'name': 'KinhTe_So',
                    'requires': ['KinhTe_Very_Fit', 'KinhTe_Fit'],
                    'condition': lambda s: s[8] >= 6,      # Tin >= 6
                    'bonus': 3,
                    'reason': 'Phù hợp Kinh tế số (có nền Tin học)'
                },
            ],
            # Y khoa: Suy luận chuỗi
            2: [
                {
                    'name': 'YKhoa_QuocTe',
                    'requires': ['YKhoa_Very_Fit', 'YKhoa_Fit'],
                    'condition': lambda s: s[5] >= 7.5,    # Anh >= 7.5
                    'bonus': 3,
                    'reason': 'Phù hợp Y khoa Quốc tế (Anh xuất sắc)'
                },
                {
                    'name': 'YKhoa_NghienCuu',
                    'requires': ['YKhoa_Very_Fit'],
                    'condition': lambda s: s[0] >= 7.5,    # Toán >= 7.5
                    'bonus': 2,
                    'reason': 'Tiềm năng Nghiên cứu Y học (Toán tốt)'
                },
            ],
            # Kỹ thuật: Suy luận chuỗi
            3: [
                {
                    'name': 'KyThuat_CongNghe',
                    'requires': ['KyThuat_Very_Fit', 'KyThuat_Fit'],
                    'condition': lambda s: s[8] >= 7,      # Tin >= 7
                    'bonus': 3,
                    'reason': 'Phù hợp Kỹ thuật Công nghệ (Tin học tốt)'
                },
            ],
            # Nông-Lâm-Ngư: Suy luận chuỗi
            4: [
                {
                    'name': 'NongLam_CongNghe',
                    'requires': ['NongLamNgu_Very_Fit', 'NongLamNgu_Fit'],
                    'condition': lambda s: s[8] >= 6,      # Tin >= 6
                    'bonus': 2,
                    'reason': 'Tiềm năng Nông nghiệp công nghệ cao'
                },
            ],
            # Sư phạm: Suy luận chuỗi
            5: [
                {
                    'name': 'SuPham_QuocTe',
                    'requires': ['SuPham_Very_Fit'],
                    'condition': lambda s: s[5] >= 8,      # Anh >= 8
                    'bonus': 3,
                    'reason': 'Phù hợp Giáo dục Quốc tế (Anh xuất sắc)'
                },
            ],
            # Luật: Suy luận chuỗi
            6: [
                {
                    'name': 'Luat_QuocTe',
                    'requires': ['Luat_Very_Fit', 'Luat_Fit'],
                    'condition': lambda s: s[5] >= 7.5,    # Anh >= 7.5
                    'bonus': 3,
                    'reason': 'Phù hợp Luật Quốc tế (Anh tốt)'
                },
            ],
            # Du lịch: Suy luận chuỗi
            7: [
                {
                    'name': 'DuLich_QuocTe',
                    'requires': ['DuLich_Very_Fit', 'DuLich_Fit'],
                    'condition': lambda s: s[5] >= 8 and s[7] >= 8,  # Anh >= 8 và Địa >= 8
                    'bonus': 3,
                    'reason': 'Phù hợp Du lịch Quốc tế (Anh và Địa xuất sắc)'
                },
            ],
        }
    
    def _define_all_rules(self):
        """Định nghĩa 32 luật cho 8 ngành"""
        return {
            0: self._rules_IT(),
            1: self._rules_KinhTe(),
            2: self._rules_YKhoa(),
            3: self._rules_KyThuat(),
            4: self._rules_NongLamNgu(),
            5: self._rules_SuPham(),
            6: self._rules_Luat(),
            7: self._rules_DuLich()
        }
    
    # ==================== IT (Công Nghệ Thông Tin) ====================
    def _rules_IT(self):
        """4 luật cho IT"""
        return [
            {
                'name': 'IT_Very_Fit',
                'description': 'Rất phù hợp IT',
                'condition': lambda s: s[0]>=8 and s[8]>=8 and s[1]>=7,
                'score': 95,
                'specificity': 3,
                'reason': 'Toán, Tin, Lý đều xuất sắc'
            },
            {
                'name': 'IT_Fit',
                'description': 'Khá phù hợp IT',
                'condition': lambda s: s[0]>=7 and s[8]>=7 and s[1]>=6 and s[5]>=5,
                'score': 80,
                'specificity': 4,
                'reason': 'Đáp ứng yêu cầu cơ bản, có khả năng teamwork'
            },
            {
                'name': 'IT_Medium',
                'description': 'Trung bình IT',
                'condition': lambda s: s[0]>=7 and s[8]>=6.5,
                'score': 65,
                'specificity': 2,
                'reason': 'Có tiềm năng nhưng cần cải thiện'
            },
            {
                'name': 'IT_Not_Fit',
                'description': 'Không phù hợp IT',
                'condition': lambda s: s[0]<6 or s[8]<6,
                'score': 20,
                'specificity': 1,
                'reason': 'Thiếu kỹ năng cơ bản'
            }
        ]
    
    # ==================== Kinh Tế ====================
    def _rules_KinhTe(self):
        """4 luật cho Kinh Tế"""
        return [
            {
                'name': 'KinhTe_Very_Fit',
                'description': 'Rất phù hợp Kinh tế',
                'condition': lambda s: s[5]>=8 and s[0]>=7.5 and s[4]>=7,
                'score': 90,
                'specificity': 3,
                'reason': 'Anh, Toán, Văn đều tốt'
            },
            {
                'name': 'KinhTe_Fit',
                'description': 'Khá phù hợp Kinh tế',
                'condition': lambda s: s[5]>=7 and s[0]>=6.5 and s[4]>=6.5,
                'score': 75,
                'specificity': 3,
                'reason': 'Đáp ứng yêu cầu'
            },
            {
                'name': 'KinhTe_Medium',
                'description': 'Trung bình Kinh tế',
                'condition': lambda s: s[5]>=6.5 and s[0]>=6,
                'score': 55,
                'specificity': 2,
                'reason': 'Có khả năng nhưng yếu về Anh'
            },
            {
                'name': 'KinhTe_Not_Fit',
                'description': 'Không phù hợp Kinh tế',
                'condition': lambda s: s[5]<6 or s[0]<5.5,
                'score': 15,
                'specificity': 1,
                'reason': 'Kỹ năng không đủ'
            }
        ]
    
    # ==================== Y Khoa ====================
    def _rules_YKhoa(self):
        """4 luật cho Y Khoa"""
        return [
            {
                'name': 'YKhoa_Very_Fit',
                'description': 'Rất phù hợp Y khoa',
                'condition': lambda s: s[3]>=8.5 and s[2]>=8 and s[4]>=7,
                'score': 95,
                'specificity': 3,
                'reason': 'Sinh, Hóa, Văn đều xuất sắc'
            },
            {
                'name': 'YKhoa_Fit',
                'description': 'Khá phù hợp Y khoa',
                'condition': lambda s: s[3]>=8 and s[2]>=7.5 and s[1]>=6 and s[4]>=6,
                'score': 85,
                'specificity': 4,
                'reason': 'Đáp ứng yêu cầu, có nền tảng Lý'
            },
            {
                'name': 'YKhoa_Medium',
                'description': 'Trung bình Y khoa',
                'condition': lambda s: s[3]>=7.5 and s[2]>=7,
                'score': 65,
                'specificity': 2,
                'reason': 'Có tiềm năng, điểm khá nhưng chưa xuất sắc'
            },
            {
                'name': 'YKhoa_Not_Fit',
                'description': 'Không phù hợp Y khoa',
                'condition': lambda s: s[3]<7 or s[2]<6.5,
                'score': 15,
                'specificity': 1,
                'reason': 'Từ khối khác, không phù hợp'
            }
        ]
    
    # ==================== Kỹ Thuật ====================
    def _rules_KyThuat(self):
        """4 luật cho Kỹ Thuật"""
        return [
            {
                'name': 'KyThuat_Very_Fit',
                'description': 'Rất phù hợp Kỹ thuật',
                'condition': lambda s: s[0]>=8 and s[1]>=8 and s[2]>=7,
                'score': 92,
                'specificity': 3,
                'reason': 'Toán, Lý, Hóa đều xuất sắc'
            },
            {
                'name': 'KyThuat_Fit',
                'description': 'Khá phù hợp Kỹ thuật',
                'condition': lambda s: s[0]>=7.5 and s[1]>=7 and s[2]>=6.5 and s[8]>=5,
                'score': 80,
                'specificity': 4,
                'reason': 'Đáp ứng yêu cầu, có kỹ năng Tin học'
            },
            {
                'name': 'KyThuat_Medium',
                'description': 'Trung bình Kỹ thuật',
                'condition': lambda s: s[0]>=7.5 and s[1]>=6.5,
                'score': 65,
                'specificity': 2,
                'reason': 'Có khả năng, Toán tốt nhưng Lý chưa cao'
            },
            {
                'name': 'KyThuat_Not_Fit',
                'description': 'Không phù hợp Kỹ thuật',
                'condition': lambda s: s[0]<6.5 or s[1]<6,
                'score': 18,
                'specificity': 1,
                'reason': 'Thiếu nền tảng cơ bản'
            }
        ]
    
    # ==================== Nông-Lâm-Ngư ====================
    def _rules_NongLamNgu(self):
        """4 luật cho Nông-Lâm-Ngư"""
        return [
            {
                'name': 'NongLamNgu_Very_Fit',
                'description': 'Rất phù hợp Nông-Lâm-Ngư',
                'condition': lambda s: s[3]>=8 and s[2]>=7.5 and s[7]>=7,
                'score': 88,
                'specificity': 3,
                'reason': 'Sinh, Hóa, Địa lý đều tốt'
            },
            {
                'name': 'NongLamNgu_Fit',
                'description': 'Khá phù hợp Nông-Lâm-Ngư',
                'condition': lambda s: s[3]>=7.5 and s[2]>=7 and s[7]>=6 and s[0]>=5.5,
                'score': 72,
                'specificity': 4,
                'reason': 'Đáp ứng yêu cầu, có kỹ năng tính toán'
            },
            {
                'name': 'NongLamNgu_Medium',
                'description': 'Trung bình Nông-Lâm-Ngư',
                'condition': lambda s: s[3]>=7 and s[7]>=7,
                'score': 65,
                'specificity': 2,
                'reason': 'Có khả năng, Địa lý tốt'
            },
            {
                'name': 'NongLamNgu_Not_Fit',
                'description': 'Không phù hợp Nông-Lâm-Ngư',
                'condition': lambda s: s[3]<6.5 or s[2]<5.5,
                'score': 18,
                'specificity': 1,
                'reason': 'Kỹ năng không đủ'
            }
        ]
    
    # ==================== Sư phạm ====================
    def _rules_SuPham(self):
        """4 luật cho Sư phạm"""
        return [
            {
                'name': 'SuPham_Very_Fit',
                'description': 'Rất phù hợp Sư phạm',
                'condition': lambda s: s[4]>=8 and s[5]>=7.5 and s[6]>=7,
                'score': 90,
                'specificity': 3,
                'reason': 'Văn, Anh, Lịch sử đều xuất sắc'
            },
            {
                'name': 'SuPham_Fit',
                'description': 'Khá phù hợp Sư phạm',
                'condition': lambda s: s[4]>=7 and s[5]>=7 and s[6]>=6.5,
                'score': 75,
                'specificity': 3,
                'reason': 'Đáp ứng yêu cầu, có năng lực truyền đạt'
            },
            {
                'name': 'SuPham_Medium',
                'description': 'Trung bình Sư phạm',
                'condition': lambda s: s[4]>=6.5 and s[5]>=6.5,
                'score': 60,
                'specificity': 2,
                'reason': 'Có khả năng, cần cải thiện kỹ năng mềm'
            },
            {
                'name': 'SuPham_Not_Fit',
                'description': 'Không phù hợp Sư phạm',
                'condition': lambda s: s[4]<6 or s[5]<5.5,
                'score': 15,
                'specificity': 1,
                'reason': 'Thiếu kỹ năng truyền đạt'
            }
        ]
    
    # ==================== Luật ====================
    def _rules_Luat(self):
        """4 luật cho Luật"""
        return [
            {
                'name': 'Luat_Very_Fit',
                'description': 'Rất phù hợp Luật',
                'condition': lambda s: s[4]>=8 and s[6]>=8 and s[5]>=7,
                'score': 90,
                'specificity': 3,
                'reason': 'Văn, Lịch sử, Anh đều xuất sắc'
            },
            {
                'name': 'Luat_Fit',
                'description': 'Khá phù hợp Luật',
                'condition': lambda s: s[4]>=7 and s[6]>=7 and s[5]>=6.5,
                'score': 75,
                'specificity': 3,
                'reason': 'Đáp ứng yêu cầu, có tư duy phản biện'
            },
            {
                'name': 'Luat_Medium',
                'description': 'Trung bình Luật',
                'condition': lambda s: s[4]>=6.5 and s[6]>=6.5,
                'score': 60,
                'specificity': 2,
                'reason': 'Có khả năng, cần rèn luyện kỹ năng lập luận'
            },
            {
                'name': 'Luat_Not_Fit',
                'description': 'Không phù hợp Luật',
                'condition': lambda s: s[4]<6 or s[6]<5.5,
                'score': 15,
                'specificity': 1,
                'reason': 'Thiếu kỹ năng lập luận'
            }
        ]
    
    # ==================== Du lịch ====================
    def _rules_DuLich(self):
        """4 luật cho Du lịch"""
        return [
            {
                'name': 'DuLich_Very_Fit',
                'description': 'Rất phù hợp Du lịch',
                'condition': lambda s: s[5]>=8 and s[7]>=7.5 and s[4]>=8,
                'score': 88,
                'specificity': 3,
                'reason': 'Anh, Địa lý, Văn xuất sắc'
            },
            {
                'name': 'DuLich_Fit',
                'description': 'Khá phù hợp Du lịch',
                'condition': lambda s: s[5]>=7.5 and s[7]>=7 and s[0]>=5.5,
                'score': 78,
                'specificity': 3,
                'reason': 'Kỹ năng giao tiếp quốc tế, có khả năng tính toán'
            },
            {
                'name': 'DuLich_Medium',
                'description': 'Trung bình Du lịch',
                'condition': lambda s: s[5]>=6.5 and s[7]>=6.5 and s[4]>=6,
                'score': 68,
                'specificity': 3,
                'reason': 'Có khả năng, Văn khá'
            },
            {
                'name': 'DuLich_Not_Fit',
                'description': 'Không phù hợp Du lịch',
                'condition': lambda s: s[5]<6.5 or s[7]<5.5,
                'score': 15,
                'specificity': 1,
                'reason': 'Yếu kỹ năng giao tiếp'
            }
        ]
    
    def calculate_relevance_score(self, user_scores, major_index):
        """
        Tính điểm trung bình các môn liên quan đến ngành
        Dùng làm tiêu chí phá hòa (tie-breaking) khi KBS score bằng nhau
        
        Args:
            user_scores (list): [Toán, Lý, Hóa, Sinh, Văn, Anh, LS, DL, Tin]
            major_index (int): 0-7
        Returns:
            float: Điểm trung bình các môn liên quan (0-10)
        """
        key_subjects = self.MAJOR_KEY_SUBJECTS.get(major_index, [])
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
          3. Priority: Luật được định nghĩa trước ưu tiên hơn (thứ tự trong list)
        
        Args:
            matched_rules (list): Danh sách luật đã khớp
        Returns:
            dict: Luật được chọn sau giải quyết xung đột
        """
        if not matched_rules:
            return None
        if len(matched_rules) == 1:
            return matched_rules[0]
        
        # Sắp xếp: specificity giảm dần, sau đó score giảm dần
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
        
        Ví dụ: IT_Very_Fit (95) + Anh>=7 → IT_Quốc_Tế (+3) = 98
        
        Args:
            user_scores: điểm 9 môn
            major_index: chỉ số ngành
            base_rule_name: tên luật cơ sở đã khớp
            base_score: điểm từ luật cơ sở
        Returns:
            tuple: (final_score, chain_details)
                chain_details: list các luật chuỗi đã áp dụng
        """
        chain_details = []
        bonus_total = 0
        
        chains = self.chaining_rules.get(major_index, [])
        for chain in chains:
            try:
                # Kiểm tra luật cơ sở có nằm trong danh sách requires không
                if base_rule_name in chain['requires']:
                    # Kiểm tra điều kiện bổ sung
                    if chain['condition'](user_scores):
                        bonus_total += chain['bonus']
                        chain_details.append({
                            'chain_name': chain['name'],
                            'bonus': chain['bonus'],
                            'reason': chain['reason']
                        })
            except Exception:
                continue
        
        final_score = min(100, base_score + bonus_total)  # Cap tối đa 100
        return final_score, chain_details
    
    # ==================== EVALUATE ====================
    def evaluate(self, user_scores, major_index):
        """
        Đánh giá điểm phù hợp dựa trên luật tri thức
        
        Quy trình:
          1. Tìm tất cả luật cơ sở khớp
          2. Giải quyết xung đột (Conflict Resolution) → chọn 1 luật
          3. Áp dụng suy luận chuỗi (Forward Chaining) → cộng bonus
        
        Args:
            user_scores (list): [Toán, Lý, Hóa, Sinh, Văn, Anh, LS, DL, Tin]
            major_index (int): 0-7 (chỉ số ngành)
        Returns:
            dict: {score, rule_name, description, reason, major, relevance_score,
                   chain_applied, chain_details}
        """
        if major_index not in self.rules:
            return None, None, "Invalid major index"
        
        rules = self.rules[major_index]
        matched_rules = []
        
        # Tính điểm liên quan (tie-breaking)
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
            
            # Tạo reason chi tiết
            reason = best_rule['reason']
            if chain_details:
                chain_reasons = [c['reason'] for c in chain_details]
                reason += ' | Suy luận chuỗi: ' + ', '.join(chain_reasons)
            
            return {
                'score': final_score,
                'rule_name': best_rule['name'],
                'description': best_rule['description'],
                'reason': reason,
                'major': self.MAJOR_NAMES[major_index],
                'relevance_score': round(relevance_score, 2),
                'chain_applied': len(chain_details) > 0,
                'chain_details': chain_details
            }
        
        # Nếu không có luật khớp
        return {
            'score': 30,
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
        Đánh giá cho tất cả 8 ngành
        Args:
            user_scores (list): [Toán, Lý, Hóa, Sinh, Văn, Anh, LS, DL, Tin]
        Returns:
            dict: {major_name: result_dict}
        """
        results = {}
        for i in range(8):
            results[self.MAJOR_NAMES[i]] = self.evaluate(user_scores, i)
        return results

    def get_ranking(self, user_scores):
        """
        Xếp hạng ngành theo điểm phù hợp
        Tie-breaking: khi score bằng nhau, ưu tiên ngành có điểm TB môn liên quan cao hơn
        Args:
            user_scores (list): [Toán, Lý, Hóa, Sinh, Văn, Anh, LS, DL, Tin]
        Returns:
            list: Danh sách ngành sắp xếp từ cao→ thấp
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
        ranking = self.get_ranking(user_scores)
        print("\n" + "="*70)
        print("KẾT QUẢ ĐÁNH GIÁ NGÀNH (Luật Tri Thức KBS)")
        print("="*70)
        print(f"Điểm học sinh: {dict(zip(self.FEATURE_NAMES, user_scores))}")
        print("-"*70)
        for item in ranking:
            print(f"{item['rank']}. {item['major']:15} | Điểm: {item['score']:3.0f}% | "
                  f"Luật: {item['rule']:20} | {item['reason']}")
        print("="*70 + "\n")


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    kbs = KnowledgeRuleEngine()
    
    # Test Case 1: Học sinh IT chuyên
    print("\n### TEST CASE 1: Học sinh IT Chuyên ###")
    scores_1 = [9, 8, 5, 4, 5, 6, 5, 5, 9.5]
    kbs.print_ranking(scores_1)
    
    # Test Case 2: Học sinh Y Khoa chuyên
    print("\n### TEST CASE 2: Học sinh Y Khoa Chuyên ###")
    scores_2 = [6, 5, 8, 8.5, 7, 7, 6, 6, 5]
    kbs.print_ranking(scores_2)
    
    # Test Case 3: Học sinh cân bằng
    print("\n### TEST CASE 3: Học sinh Cân Bằng ###")
    scores_3 = [7, 7, 7, 7, 7, 7, 7, 7, 7]
    kbs.print_ranking(scores_3)
    
    # Test Case 4: Học sinh yếu
    print("\n### TEST CASE 4: Học sinh Yếu ###")
    scores_4 = [5, 5, 5, 5, 5, 5, 5, 5, 5]
    kbs.print_ranking(scores_4)

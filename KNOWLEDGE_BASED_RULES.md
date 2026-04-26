# 32 Luật Tri Thức Chuyên Gia (KBS - Knowledge-Based System) v2.0

**Hệ thống 32 luật cơ sở + 10 luật chuỗi + Conflict Resolution**  
**4 Luật × 8 Ngành = 32 Luật + Forward Chaining + Specificity**

---

## I. Khái Niệm

**Luật Tri Thức Độc Lập = Luật Chuyên Gia (Expert Rules)**

```
Định nghĩa: Các luật được xây dựng từ:
   Kiến thức giáo viên/chuyên gia
   Kinh nghiệm thực tế
   Phân tích yêu cầu của ngành
   KHÔNG phụ thuộc vào dữ liệu ML

Ví dụ:
  "Một học sinh phù hợp với IT nếu:"
  ├─ Toán học tốt (≥7/10)
  ├─ Kỹ năng lập trình tốt (Tin ≥7/10)
  ├─ Có tư duy logic (Lý ≥6/10)
  └─ (Đây là KIẾN THỨC, không phải từ mô hình)
```

---

## II. Cấu Trúc Mỗi Luật (Rule Structure)

```python
{
    'name': 'IT_Very_Fit',              # Tên luật
    'description': 'Rất phù hợp IT',    # Mô tả
    'condition': lambda s: s[0]>=8 and s[8]>=8 and s[1]>=7,  # Điều kiện
    'score': 95,                        # Điểm nếu điều kiện đúng (0-100%)
    'specificity': 3,                   # Số điều kiện (độ đặc hiệu) - MỚI v2.0
    'reason': 'Toán, Tin, Lý đều xuất sắc'  # Giải thích
}
```

---

## III. CƠ CHẾ

### A. Forward Chaining (Suy Luận Chuỗi)

Khi luật cơ sở khớp VÀ điều kiện phụ thỏa mãn → cộng điểm bonus.

| Ngành | Luật Chuỗi | Yêu Cầu | Điều Kiện Phụ | Bonus |
|-------|-----------|---------|-------------|-------|
| IT | IT_Quoc_Te | IT_Very_Fit hoặc IT_Fit | Anh≥7 | +3 |
| IT | IT_TinSinhHoc | IT_Very_Fit hoặc IT_Fit | Sinh≥7 | +2 |
| Kinh Tế | KinhTe_So | KinhTe_Very_Fit hoặc Fit | Tin≥6 | +3 |
| Y Khoa | YKhoa_QuocTe | YKhoa_Very_Fit hoặc Fit | Anh≥7.5 | +3 |
| Y Khoa | YKhoa_NghienCuu | YKhoa_Very_Fit hoặc Fit | Toán≥7.5 | +2 |
| Kỹ Thuật | KyThuat_CongNghe | KyThuat_Very_Fit hoặc Fit | Tin≥7 | +3 |
| Nông-Lâm | NongLam_CongNghe | NLN_Very_Fit hoặc Fit | Tin≥6 | +2 |
| Sư Phạm | SuPham_QuocTe | SP_Very_Fit hoặc Fit | Anh≥8 | +3 |
| Luật | Luat_QuocTe | Luat_Very_Fit hoặc Fit | Anh≥7.5 | +3 |
| Du Lịch | DuLich_QuocTe | DL_Very_Fit hoặc Fit | Anh≥8 AND ĐL≥8 | +3 |

### B. Conflict Resolution (Giải Quyết Xung Đột)

Khi nhiều luật cùng khớp cho 1 ngành:
1. **Ưu tiên specificity** (luật có nhiều điều kiện hơn)
2. Sau đó **ưu tiên score** (luật có điểm cao hơn)

Ví dụ:
```
Học sinh: Toán=8, Lý=7, Tin=8, Anh=6
→ IT_Very_Fit khớp (spec=3, score=95)
→ IT_Fit khớp (spec=4, score=80)
→ Chọn IT_Fit (spec=4 > spec=3) → score=80
```

### C. Specificity (Độ Đặc Hiệu)

| Specificity | Số Điều Kiện | Ví Dụ |
|-------------|--------------|--------|
| 1 | 1 điều kiện | Not_Fit (luật loại trừ) |
| 2 | 2 điều kiện | Medium |
| 3 | 3 điều kiện | Very_Fit, Fit |
| 4 | 4 điều kiện | Fit mở rộng (được ưu tiên) |

### D. Cấu Hình Ngoài (rules_config.json)

Metadata của luật được tách ra `rules_config.json` để dễ bảo trì:
- Thresholds, scores, specificity
- Chaining rules
- Conflict resolution strategy
- Không cần sửa code khi điều chỉnh tham số

---

## IV. 32 Luật Chi Tiết

### Quy Ước Ký Hiệu Môn Học (Indices)
```
s[0] = Toán        s[1] = Lý          s[2] = Hóa
s[3] = Sinh        s[4] = Văn         s[5] = Anh
s[6] = Lịch sử     s[7] = Địa lý      s[8] = Tin học
```

---

### **NGÀNH 0: IT (Công Nghệ Thông Tin)**

| # | Luật | Điều Kiện | Điểm | Spec | Lý Do |
|---|------|-----------|------|------|-------|
| 1 | IT_Very_Fit | Toán≥8 AND Tin≥8 AND Lý≥7 | **95** | 3 | Toán, Tin, Lý đều xuất sắc |
| 2 | IT_Fit | Toán≥7 AND Tin≥7 AND Lý≥6 AND Anh≥5 | **80** | 4 | Đáp ứng cơ bản + teamwork |
| 3 | IT_Medium | Toán≥7 AND Tin≥6.5 | **65** | 2 | Có tiềm năng, cần cải thiện |
| 4 | IT_Not_Fit | Toán<6 OR Tin<6 | **20** | 1 | Thiếu kỹ năng cơ bản |

**Chaining:** IT_Quoc_Te (+3, Anh≥7) | IT_TinSinhHoc (+2, Sinh≥7)

---

### **NGÀNH 1: Kinh Tế (Kinh Doanh)**

| # | Luật | Điều Kiện | Điểm | Spec | Lý Do |
|---|------|-----------|------|------|-------|
| 1 | KinhTe_Very_Fit | Anh≥8 AND Toán≥7.5 AND Văn≥7 | **90** | 3 | Anh, Toán, Văn đều tốt |
| 2 | KinhTe_Fit | Anh≥7 AND Toán≥6.5 AND Văn≥6.5 | **75** | 3 | Đáp ứng yêu cầu |
| 3 | KinhTe_Medium | Anh≥6.5 AND Toán≥6 | **55** | 2 | Có khả năng nhưng yếu Anh |
| 4 | KinhTe_Not_Fit | Anh<6 OR Toán<5.5 | **15** | 1 | Kỹ năng không đủ |

**Chaining:** KinhTe_So (+3, Tin≥6)

---

### **NGÀNH 2: Y Khoa (Sức Khỏe)**

| # | Luật | Điều Kiện | Điểm | Spec | Lý Do |
|---|------|-----------|------|------|-------|
| 1 | YKhoa_Very_Fit | Sinh≥8.5 AND Hóa≥8 AND Văn≥7 | **95** | 3 | Sinh, Hóa, Văn đều xuất sắc |
| 2 | YKhoa_Fit | Sinh≥8 AND Hóa≥7.5 AND Lý≥6 AND Văn≥6 | **85** | 4 | Đáp ứng + nền tảng Lý |
| 3 | YKhoa_Medium | Sinh≥7.5 AND Hóa≥7 | **65** | 2 | Tiềm năng, điểm khá |
| 4 | YKhoa_Not_Fit | Sinh<7 OR Hóa<6.5 | **15** | 1 | Khối khác, không phù hợp |

**Chaining:** YKhoa_QuocTe (+3, Anh≥7.5) | YKhoa_NghienCuu (+2, Toán≥7.5)

---

### **NGÀNH 3: Kỹ Thuật (Xây Dựng)**

| # | Luật | Điều Kiện | Điểm | Spec | Lý Do |
|---|------|-----------|------|------|-------|
| 1 | KyThuat_Very_Fit | Toán≥8 AND Lý≥8 AND Hóa≥7 | **92** | 3 | Toán, Lý, Hóa xuất sắc |
| 2 | KyThuat_Fit | Toán≥7.5 AND Lý≥7 AND Hóa≥6.5 AND Tin≥5 | **80** | 4 | Đáp ứng + Tin học |
| 3 | KyThuat_Medium | Toán≥7.5 AND Lý≥6.5 | **65** | 2 | Toán tốt, Lý chưa cao |
| 4 | KyThuat_Not_Fit | Toán<6.5 OR Lý<6 | **18** | 1 | Thiếu nền tảng |

**Chaining:** KyThuat_CongNghe (+3, Tin≥7)

---

### **NGÀNH 4: Nông-Lâm-Ngư**

| # | Luật | Điều Kiện | Điểm | Spec | Lý Do |
|---|------|-----------|------|------|-------|
| 1 | NongLamNgu_Very_Fit | Sinh≥8 AND Hóa≥7.5 AND ĐL≥7 | **88** | 3 | Sinh, Hóa, Địa lý tốt |
| 2 | NongLamNgu_Fit | Sinh≥7.5 AND Hóa≥7 AND ĐL≥6 AND Toán≥5.5 | **72** | 4 | Đáp ứng + tính toán |
| 3 | NongLamNgu_Medium | Sinh≥7 AND ĐL≥7 | **65** | 2 | Địa lý tốt |
| 4 | NongLamNgu_Not_Fit | Sinh<6.5 OR Hóa<5.5 | **18** | 1 | Kỹ năng không đủ |

**Chaining:** NongLam_CongNghe (+2, Tin≥6)

---

### **NGÀNH 5: Sư Phạm (Giáo Dục)**

| # | Luật | Điều Kiện | Điểm | Spec | Lý Do |
|---|------|-----------|------|------|-------|
| 1 | SuPham_Very_Fit | Văn≥8 AND Anh≥7.5 AND LS≥7 | **90** | 3 | Văn, Anh, LS xuất sắc |
| 2 | SuPham_Fit | Văn≥7 AND Anh≥7 AND LS≥6.5 | **75** | 3 | Đáp ứng + truyền đạt |
| 3 | SuPham_Medium | Văn≥6.5 AND Anh≥6.5 | **60** | 2 | Cần cải thiện kỹ năng mềm |
| 4 | SuPham_Not_Fit | Văn<6 OR Anh<5.5 | **15** | 1 | Thiếu kỹ năng truyền đạt |

**Chaining:** SuPham_QuocTe (+3, Anh≥8)

---

### **NGÀNH 6: Luật Pháp**

| # | Luật | Điều Kiện | Điểm | Spec | Lý Do |
|---|------|-----------|------|------|-------|
| 1 | Luat_Very_Fit | Văn≥8 AND LS≥8 AND Anh≥7 | **90** | 3 | Văn, LS, Anh xuất sắc |
| 2 | Luat_Fit | Văn≥7 AND LS≥7 AND Anh≥6.5 | **75** | 3 | Đáp ứng + phản biện |
| 3 | Luat_Medium | Văn≥6.5 AND LS≥6.5 | **60** | 2 | Kỹ năng lập luận |
| 4 | Luat_Not_Fit | Văn<6 OR LS<5.5 | **15** | 1 | Thiếu kỹ năng lập luận |

**Chaining:** Luat_QuocTe (+3, Anh≥7.5)

---

### **NGÀNH 7: Du Lịch (Khách Sạn)**

| # | Luật | Điều Kiện | Điểm | Spec | Lý Do |
|---|------|-----------|------|------|-------|
| 1 | DuLich_Very_Fit | Anh≥8 AND ĐL≥7.5 AND Văn≥8 | **88** | 3 | Anh, ĐL, Văn xuất sắc |
| 2 | DuLich_Fit | Anh≥7.5 AND ĐL≥7 AND Toán≥5.5 | **78** | 3 | Giao tiếp + tính toán |
| 3 | DuLich_Medium | Anh≥6.5 AND ĐL≥6.5 AND Văn≥6 | **68** | 3 | Anh khá, Văn tốt |
| 4 | DuLich_Not_Fit | Anh<6.5 OR ĐL<5.5 | **15** | 1 | Yếu giao tiếp |

**Chaining:** DuLich_QuocTe (+3, Anh≥8 AND ĐL≥8)

---

## V. Mức Phân Loại & Điểm

| Mức | Điểm | Spec | Mô Tả |
|-----|------|------|-------|
| **Very Fit** | 88-95 | 3 | Rất phù hợp (điều kiện khắt khe) |
| **Fit** | 72-85 | 3-4 | Khá phù hợp (đáp ứng cơ bản, được ưu tiên nếu spec=4) |
| **Medium** | 55-68 | 2 | Trung bình (có tiềm năng) |
| **Not Fit** | 15-20 | 1 | Không phù hợp (thiếu kỹ năng) |

---

## VI. Quy Trình Đánh Giá KBS

```python
1. TÌM TẤT CẢ LUẬT KHỚP:
   FOR EACH RULE IN MAJOR_RULES:
     IF rule_condition(user_scores) == TRUE:
       ADD RULE TO matched_rules[]
     ENDIF
   ENDFOR

2. CONFLICT RESOLUTION (GIẢI QUYẾT XUNG ĐỘT):
   IF len(matched_rules) > 1:
     SORT matched_rules BY specificity DESC, THEN BY score DESC
     best_rule = matched_rules[0]  ← Luật cụ thể nhất
   ELIF len(matched_rules) == 1:
     best_rule = matched_rules[0]
   ELSE:
     RETURN DEFAULT_SCORE (30%)
   ENDIF

3. FORWARD CHAINING (SUY LUẬN CHUỖI):
   FOR EACH CHAIN_RULE IN CHAINING_RULES:
     IF best_rule.name IN chain_rule.requires:
       IF chain_threshold(user_scores) == TRUE:
         best_rule.score += chain_rule.bonus
         LOG chain_details
       ENDIF
     ENDIF
   ENDFOR

4. RETURN: score, rule_name, reason, chain_applied, chain_details
```

**Ví dụ (v2.0):** Học sinh IT có Anh tốt
```
Điểm: Toán=8.5, Tin=9, Lý=7.2, Anh=8, Sinh=3

Bước 1 - Tìm luật khớp:
✓ Very_Fit:  Toán≥8 ✓ AND Tin≥8 ✓ AND Lý≥7 ✓  → KHỚP (score=95, spec=3)
✓ Fit:       Toán≥7 ✓ AND Tin≥7 ✓ AND Lý≥6 ✓ AND Anh≥5 ✓ → KHỚP (score=80, spec=4)
✓ Medium:    Toán≥7 ✓ AND Tin≥6.5 ✓ → KHỚP (score=65, spec=2)

Bước 2 - Conflict Resolution:
Matched: [Fit(spec=4), Very_Fit(spec=3), Medium(spec=2)]
→ CHỌN: IT_Fit (spec=4 > spec=3) → score=80

Bước 3 - Forward Chaining:
IT_Quoc_Te: IT_Fit ∈ requires ✓ AND Anh(8)≥7 ✓ → +3 bonus
→ SCORE CUỐI: 80 + 3 = 83
→ Chain: "Phù hợp IT Quốc tế (Anh tốt)"
```

---

## VII. Feature Importance trong KBS

**Các môn học quan trọng nhất cho mỗi ngành:**

| Ngành | Top 3 Môn | Tầm Quan Trọng |
|-------|----------|---|
| IT | Toán, Tin, Lý | Rất cao (57%) |
| Kinh tế | Toán, Anh, Văn | Cao (43%) |
| Y khoa | Sinh, Hóa, Lý | Rất cao (57%) |
| Kỹ thuật | Toán, Lý, Hóa | Rất cao (59%) |
| Nông-Lâm-Ngư | Sinh, Địa lý, Hóa | Cao (47%) |
| Sư phạm | Văn, Anh, Lịch sử | Cao (47%) |
| Luật | Văn, Lịch sử, Anh | Cao (46%) |
| Du lịch | Anh, Địa lý, Văn | Cao (42%) |

---


---

##  Cách Triển Khai Luật Tri Thức

### Phương Pháp 1: Luật Đơn Giản (Simple Rule Engine)

```python
# File: knowledge_rules.py

class KnowledgeRuleEngine:
    """
    Hệ thống luật tri thức độc lập (không dùng ML)
    """
    
    def __init__(self):
        self.rules = self._define_rules()
    
    def _define_rules(self):
        """Định nghĩa luật cho 8 ngành"""
        return {
            0: self._rules_IT(),          # IT
            1: self._rules_KinhTe(),      # Kinh Tế
            2: self._rules_YKhoa(),       # Y Khoa
            3: self._rules_KyThuat(),     # Kỹ Thuật
            4: self._rules_NongLamNgu(),  # Nông-Lâm-Ngư
            5: self._rules_SuPham(),      # Sư Phạm
            6: self._rules_Luat(),        # Luật
            7: self._rules_DuLich()       # Du Lịch
        }
    
    def _rules_IT(self):
        """Luật cho IT"""
        return [
            {
                'name': 'IT_Very_Fit',
                'condition': lambda s: s[0]>=8 and s[8]>=8 and s[1]>=7,  # Toán, Tin, Lý
                'score': 95
            },
            {
                'name': 'IT_Fit',
                'condition': lambda s: s[0]>=7 and s[8]>=7 and s[1]>=6,
                'score': 80
            },
            {
                'name': 'IT_Medium',
                'condition': lambda s: s[0]>=6.5 and s[8]>=6.5,
                'score': 60
            },
            {
                'name': 'IT_Not_Fit',
                'condition': lambda s: s[0]<6 or s[8]<6,
                'score': 20
            }
        ]
    
    def _rules_YKhoa(self):
        """Luật cho Y Khoa"""
        return [
            {
                'name': 'YK_Very_Fit',
                'condition': lambda s: s[3]>=8.5 and s[2]>=8 and s[4]>=7,  # Sinh, Hóa, Văn
                'score': 95
            },
            {
                'name': 'YK_Fit',
                'condition': lambda s: s[3]>=8 and s[2]>=7.5 and s[4]>=6,
                'score': 85
            },
            {
                'name': 'YK_Medium',
                'condition': lambda s: s[3]>=7 and s[2]>=6.5,
                'score': 50
            },
            {
                'name': 'YK_Not_Fit',
                'condition': lambda s: s[3]<7 or s[2]<6.5,
                'score': 15
            }
        ]
    
    def _rules_KyThuat(self):
        """Luật cho Kỹ Thuật"""
        return [
            {
                'name': 'KT_Very_Fit',
                'condition': lambda s: s[0]>=8 and s[1]>=8 and s[2]>=7,
                'score': 92
            },
            {
                'name': 'KT_Fit',
                'condition': lambda s: s[0]>=7.5 and s[1]>=7 and s[2]>=6,
                'score': 80
            },
            {
                'name': 'KT_Medium',
                'condition': lambda s: s[0]>=7 and s[1]>=6.5,
                'score': 55
            },
            {
                'name': 'KT_Not_Fit',
                'condition': lambda s: s[0]<6.5 or s[1]<6,
                'score': 18
            }
        ]
    
    # ... (tương tự cho các ngành khác)
    
    def evaluate(self, user_scores, major_index):
        """
        Đánh giá điểm cho ngành dựa trên luật tri thức
        
        Args:
            user_scores: [Toán, Lý, Hóa, Sinh, Văn, Anh, LS, DL, Tin]
            major_index: 0-7 (chỉ số ngành)
        
        Returns:
            score (0-100%): Điểm phù hợp
        """
        if major_index not in self.rules:
            return None
        
        rules = self.rules[major_index]
        
        # Áp dụng luật theo thứ tự: từ cụ thể đến tổng quát
        for rule in rules:
            if rule['condition'](user_scores):
                return rule['score']
        
        # Default nếu không có luật nào khớp
        return 30  # Điểm thấp mặc định
```

### Phương Pháp 2: Luật Mở Rộng (Extended Rules)

```python
def _rules_Kinh_Te(self):
    """Luật cho Kinh Tế - Mở rộng"""
    return [
        {
            'name': 'KinhTe_Very_Fit',
            'conditions': [
                ('Anh', '>=', 8),
                ('Toan', '>=', 7.5),
                ('Van', '>=', 7)
            ],
            'logic': 'AND',  # Tất cả điều kiện đều đúng
            'score': 90
        },
        {
            'name': 'KinhTe_Fit',
            'conditions': [
                ('Anh', '>=', 7),
                ('Toan', '>=', 6.5)
            ],
            'logic': 'AND',
            'score': 75
        }
    ]
```

### Phương Pháp 3: Tích Hợp Vào Hệ Thống Hiện Tại

```python
# File: hybrid_engine.py (Cập nhật)

from knowledge_rules import KnowledgeRuleEngine

def get_hybrid_advice(user_scores, major_index=0):
    """
    Kết hợp 2 loại luật:
    1. Luật tri thức độc lập (KBS)
    2. Luật từ ML (nếu dùng)
    """
    
    # LOẠI 1: LUẬT TRI THỨC
    kbs_engine = KnowledgeRuleEngine()
    kbs_score = kbs_engine.evaluate(user_scores, major_index)
    
    # LOẠI 2: LUẬT TỪ ML (Optional)
    model = load_model()
    if model is not None:
        probs = model.predict_proba(X_input)[0]
        raw_prob = probs[major_index]
        ml_score = (raw_prob ** 0.6) * 10 * 10  # Chuyển thành %
    else:
        ml_score = None
    
    # KẾT HỢP (Tuỳ chọn)
    if ml_score is not None:
        # Hybrid 60% ML + 40% KBS
        hybrid_score = 0.6 * ml_score + 0.4 * kbs_score
    else:
        # Chỉ dùng KBS
        hybrid_score = kbs_score
    
    return hybrid_score, kbs_score, ml_score
```

---



##  Giai Đoạn Triển Khai

### Giai Đoạn 1: Xây Dựng Luật

```python
# 1. Định nghĩa luật cho 8 ngành
knowledge_rules.py:
├─ _rules_IT()
├─ _rules_KinhTe()
├─ _rules_YKhoa()
├─ _rules_KyThuat()
├─ _rules_NongLamNgu()
├─ _rules_SuPham()
├─ _rules_Luat()
└─ _rules_DuLich()
```

### Giai Đoạn 2: Kiểm Tra Luật

```python
# 2. Test luật với dữ liệu
test_knowledge_rules.py:
├─ Test IT với học sinh kỹ thuật cao
├─ Test Y Khoa với học sinh khoa học cao
├─ Test Kinh Tế với học sinh Anh cao
└─ Xác minh điểm phù hợp
```

### Giai Đoạn 3: Tích Hợp Vào App

```python
# 3. Thêm vào Streamlit UI
app.py:
├─ Toggle: "Chỉ dùng KBS" vs "Hybrid"
├─ Hiển thị cả KBS_Score và ML_Score
└─ Giải thích từ luật chuyên gia
```

---

##  Ví Dụ Thực Tế

### Case 1: Học Sinh IT Chuyên

```
Điểm: Toán 9, Lý 8, Hóa 5, Sinh 4, Văn 5, Anh 8, LS 5, DL 5, Tin 9.5

Áp dụng LUẬT KBS cho IT:
├─ Bước 1: Tìm luật khớp
│  ✓ IT_Very_Fit: Toán(9)≥8 ✓ AND Tin(9.5)≥8 ✓ AND Lý(8)≥7 ✓ (spec=3, 95)
│  ✓ IT_Fit: Toán(9)≥7 ✓ AND Tin(9.5)≥7 ✓ AND Lý(8)≥6 ✓ AND Anh(8)≥5 ✓ (spec=4, 80)
│  ✓ IT_Medium: Toán(9)≥7 ✓ AND Tin(9.5)≥6.5 ✓ (spec=2, 65)
│
├─ Bước 2: Conflict Resolution
│  Matched: [IT_Fit(spec=4), IT_Very_Fit(spec=3), IT_Medium(spec=2)]
│  → CHỌN: IT_Fit (spec=4 > spec=3) → score=80
│
└─ Bước 3: Forward Chaining
   IT_Quoc_Te: IT_Fit ∈ requires ✓ AND Anh(8)≥7 ✓ → +3
   → SCORE CUỐI: 80 + 3 = 83 ("Phù hợp IT Quốc tế")

RANKING KBS:
1. IT: 83% (IT_Fit + IT_Quoc_Te chain)
2. Kỹ Thuật: ~83% (KyThuat_Fit + KyThuat_CongNghe chain)
3. Khác: 15-30%
```

### Case 2: Học Sinh Y Khoa Chuyên

```
Điểm: Toán 6, Lý 5, Hóa 8, Sinh 8.5, Văn 7, Anh 7, LS 6, DL 6, Tin 5

Áp dụng LUẬT KBS:
├─ Y Khoa: Sinh(8.5)>=8.5  AND Hóa(8)>=8  AND Văn(7)>=7 
│   Luật YK_Very_Fit khớp
│   KBS_Score = 95%
│
├─ IT: Toán(6)<6  OR Tin(5)<6 
│   Luật IT_Not_Fit khớp
│   KBS_Score = 20%
│
└─ Kỹ Thuật: Toán(6)<6.5 
    Luật KT_Not_Fit khớp
    KBS_Score = 18%

RANKING KBS:
1. Y Khoa: 95%  Rất phù hợp
2. Sư Phạm: 70% (tùy luật)
3. Du Lịch: 65% (tùy luật)
```

---

##  Cách Cập Nhật Luật 

### Quy Trình Cập Nhật

```python
Bước 1: Chạy evaluate_kbs.py → kiểm tra KBS hiện tại
Bước 2: Chạy experiments.py → phân tích ML vs KBS
Bước 3: Sửa rules_config.json (thresholds, scores, chaining)
Bước 4: Cập nhật knowledge_rules.py cho phù hợp
Bước 5: Chạy lại evaluate_kbs.py → verify
```

### Cách 1: Sửa rules_config.json (Ưu tiên)

```json
// Thay đổi threshold trong rules_config.json:
"thresholds": {"sinh": 8.2, "hoa": 7.5, "van": 6.5}
// Không cần sửa code!
```

### Cách 2: Sửa knowledge_rules.py (nếu cần logic mới)

```python
# TRƯỚC:
condition=lambda s: s[3]>=8 and s[2]>=7.5 and s[4]>=6
# SAU:
condition=lambda s: s[3]>=8.2 and s[2]>=7.5 and s[4]>=6.5
```


# Luật tri thức chuyên gia (KBS) 

**Hệ thống luật theo khối trong `rules_config.json` (JSON) + Conflict Resolution + Forward chaining (bonus) + Specificity**

---

## I. Tổng Quan Kiến Trúc KBS v3.0



```


v3.0 :
- Luật theo ngành trong `rules_config.json` (`khtn_rules`, `khxh_rules`)
- 2 khối (KHTN: 5 ngành, KHXH: 4 ngành), 6 môn/khối (không dùng Tin học)
- **Forward chaining:** `chaining_rules` trong JSON → `forward_chain()` sau khi chọn luật nền
- `_build_condition()` biên dịch JSON → callable
```

---

## II. Cấu Trúc Luật JSON (rules_config.json)

### 2.1 Format Cơ Bản

```json
{
  "version": "3.0",
  "khtn_rules": {
    "0_IT": {
      "major_name": "IT",
      "rules": [
        {
          "name": "IT_Very_Fit",
          "thresholds": {"toan": 8, "ly": 7.5, "anh": 6},
          "operator": "AND",
          "score": 95,
          "specificity": 3,
          "reason": "Toán, Lý xuất sắc, Anh khá"
        },
        ...
      ]
    },
    ...
  },
  "khxh_rules": { ... }
}
```

### 2.2 Giải Thích Mỗi Field

| Field | Ý Nghĩa | Ví Dụ |
|-------|---------|-------|
| `name` | Tên luật | `IT_Very_Fit`, `YKhoa_Medium` |
| `thresholds` | Dict (môn: ngưỡng) | `{"toan": 8, "ly": 7.5}` |
| `operator` | AND hoặc OR_LESS_THAN | AND: tất cả ≥ threshold |
| `score` | Điểm nếu khớp (0-100) | 95 (rất phù hợp), 20 (không phù hợp) |
| `specificity` | Độ đặc hiệu (số điều kiện) | 3, 4, 2, 1 |
| `reason` | Giải thích bằng Tiếng Việt | "Toán, Lý, Anh đều xuất sắc" |

---

## III. Cơ Chế Hoạt Động

### 3.1 Quy Trình Matching

```
User Input (6 môn) → [điểm môn]
    ↓
Duyệt qua ~20 luật trong rules_config.json
    ↓
Kiểm tra điều kiện (AND / OR_LESS_THAN)
    ↓
Luật khớp? → Thêm vào danh sách candidates
    ↓
Conflict Resolution:
  - Ưu tiên luật có specificity cao nhất
  - Nếu bằng → ưu tiên score cao nhất
  - → Chọn 1 luật winner
    ↓
Output: (rule_name, score, reason)
```

### 3.2 Conflict Resolution

**Ưu tiên:**
1. **Specificity cao nhất** (số điều kiện nhiều)
2. Sau đó **score cao nhất**

**Ví dụ:**
```
Học sinh: Toan=8.5, Ly=8, Anh=5.5, Van=6.5

Khớp:
  ✓ IT_Very_Fit: spec=3, score=95 (Toan≥8, Ly≥7.5, Anh≥6)
  ✓ IT_Fit: spec=4, score=80 (Toan≥7, Ly≥6.5, Hoa≥5, Anh≥5)
  ✗ IT_Medium: không khớp (Anh < 6)

→ Chọn IT_Fit (spec=4 > spec=3 của Very_Fit)
→ Điểm KBS: 80
```

### 3.3 Operators

| Operator | Ý Nghĩa | Ví Dụ |
|----------|---------|--------|
| `AND` | **TẤT CẢ** điều kiện đúng | `Toan≥8 AND Ly≥7.5` |
| `OR_LESS_THAN` | **BẤT KỲ** điều kiện sai | `Toan<6 OR Ly<5.5` (Not_Fit rule) |

---

## IV. Luật chi tiết theo khối (ví dụ cấu trúc)

### A. KHTN (Khối Học Tự Nhiên)

#### 1. IT (Công nghệ Thông tin)

```json
"0_IT": {
  "major_name": "IT",
  "rules": [
    {
      "name": "IT_Very_Fit",
      "thresholds": {"toan": 8, "ly": 7.5, "anh": 6},
      "operator": "AND",
      "score": 95,
      "specificity": 3,
      "reason": "Toán, Lý xuất sắc"
    },
    {
      "name": "IT_Fit",
      "thresholds": {"toan": 7, "ly": 6.5, "hoa": 5, "anh": 5},
      "operator": "AND",
      "score": 80,
      "specificity": 4,
      "reason": "Nền tảng tốt"
    },
    {
      "name": "IT_Medium",
      "thresholds": {"toan": 7, "ly": 6},
      "operator": "AND",
      "score": 65,
      "specificity": 2,
      "reason": "Có tiềm năng, cần cải thiện"
    },
    {
      "name": "IT_Not_Fit",
      "thresholds": {"toan": 6, "ly": 5.5},
      "operator": "OR_LESS_THAN",
      "score": 20,
      "specificity": 1,
      "reason": "Thiếu kỹ năng cơ bản"
    }
  ]
}
```

#### 2. Y khoa (Sức Khỏe)

```json
"2_YKhoa": {
  "major_name": "Y khoa",
  "rules": [
    {
      "name": "YKhoa_Very_Fit",
      "thresholds": {"sinh": 8.5, "hoa": 8, "ly": 7},
      "operator": "AND",
      "score": 95,
      "specificity": 3,
      "reason": "Sinh, Hóa, Lý đều xuất sắc"
    },
    {
      "name": "YKhoa_Fit",
      "thresholds": {"sinh": 8, "hoa": 7.5, "ly": 6, "van": 6},
      "operator": "AND",
      "score": 85,
      "specificity": 4,
      "reason": "Đáp ứng yêu cầu, nền tảng Lý tốt"
    },
    {
      "name": "YKhoa_Medium",
      "thresholds": {"sinh": 7.5, "hoa": 7},
      "operator": "AND",
      "score": 65,
      "specificity": 2,
      "reason": "Có khả năng nhưng cần cải thiện"
    },
    {
      "name": "YKhoa_Not_Fit",
      "thresholds": {"sinh": 6.5, "hoa": 6},
      "operator": "OR_LESS_THAN",
      "score": 20,
      "specificity": 1,
      "reason": "Không đủ kỹ năng"
    }
  ]
}
```

#### 3. Kinh tế (Khối KHTN + KHXH)

```json
"1_KinhTe": {
  "major_name": "Kinh tế",
  "rules": [
    {
      "name": "KinhTe_Very_Fit",
      "thresholds": {"anh": 8, "toan": 7.5, "van": 7},
      "operator": "AND",
      "score": 90,
      "specificity": 3,
      "reason": "Anh, Toán, Văn đều tốt"
    },
    {
      "name": "KinhTe_Fit",
      "thresholds": {"anh": 7, "toan": 6.5, "van": 6.5},
      "operator": "AND",
      "score": 75,
      "specificity": 3,
      "reason": "Đáp ứng yêu cầu"
    },
    {
      "name": "KinhTe_Medium",
      "thresholds": {"anh": 6.5, "toan": 6},
      "operator": "AND",
      "score": 55,
      "specificity": 2,
      "reason": "Cơ bản nhưng cần cải Anh"
    },
    {
      "name": "KinhTe_Not_Fit",
      "thresholds": {"anh": 6, "toan": 5.5},
      "operator": "OR_LESS_THAN",
      "score": 15,
      "specificity": 1,
      "reason": "Kỹ năng không đủ"
    }
  ]
}
```

#### 4-5. Kỹ thuật & Nông-Lâm-Ngư

Tương tự, mỗi ngành có 4 luật (Very_Fit, Fit, Medium, Not_Fit)

### B. KHXH (Khối Học Xã Hội)

#### 1. Sư phạm (Giáo dục)

```json
"5_SuPham": {
  "major_name": "Sư phạm",
  "rules": [
    {
      "name": "SuPham_Very_Fit",
      "thresholds": {"van": 8, "anh": 7.5, "toan": 7},
      "operator": "AND",
      "score": 90,
      "specificity": 3,
      "reason": "Văn, Anh, Toán đều xuất sắc"
    },
    ...
  ]
}
```

#### 2. Luật pháp

```json
"6_Luat": {
  "major_name": "Luật pháp",
  "rules": [
    {
      "name": "Luat_Very_Fit",
      "thresholds": {"van": 8, "lich_su": 7.5, "anh": 7},
      "operator": "AND",
      "score": 92,
      "specificity": 3,
      "reason": "Văn, Lịch sử, Anh đều tốt"
    },
    ...
  ]
}
```

#### 3. Du lịch

```json
"7_DuLich": {
  "major_name": "Du lịch",
  "rules": [
    {
      "name": "DuLich_Very_Fit",
      "thresholds": {"anh": 8, "dia_ly": 7.5, "van": 7},
      "operator": "AND",
      "score": 88,
      "specificity": 3,
      "reason": "Anh, Địa lý, Văn xuất sắc"
    },
    ...
  ]
}
```

---

## V. Cách sử dụng KBS Engine

### 5.1 Khởi tạo và `evaluate`

```python
from knowledge_rules import KnowledgeRuleEngine
from config import get_majors

engine = KnowledgeRuleEngine(block="khtn")
student_scores = [8.5, 7.0, 6.5, 7.5, 6.0, 7.0]  # đúng thứ tự get_features("khtn")

for idx in get_majors("khtn"):
    r = engine.evaluate(student_scores, idx)
    print(r["major"], r["score"], r["rule_name"], r["reason"])

# Hoặc một lần cho cả khối:
all_results = engine.evaluate_all_majors(student_scores)
# dict: tên ngành → dict kết quả (score, rule_name, reason, chain_applied, ...)
```

### 5.2 Xếp hạng chỉ KBS

```python
ranking = engine.get_ranking(student_scores)
# list các dict: rank, major, score, rule, reason, ...
```

---

## VI. Ưu Điểm & Hạn Chế

### Ưu Điểm ✓

- **Dễ cập nhật:** Chỉ sửa `rules_config.json`, không cần code
- **Rõ ràng:** Mỗi luật có reason bằng Tiếng Việt
- **Flexible:** Thêm/bớt luật dễ dàng
- **Maintainable:** JSON-based dễ version control
- **Conflict Resolution:** Specificity + score tự động chọn luật tốt nhất

### Hạn Chế ⚠

- **Thresholds cứng:** Toán ≥ 8 = quyết định tuyệt đối (không soft)
- **Chưa được validate:** Luật chưa qua chuyên gia giáo dục thực tế
- **Không học từ dữ liệu:** KBS hoàn toàn dựa trên cảm tính
- **Forward chaining** đã có (bonus theo điều kiện chuỗi); có thể mở rộng thêm rule chain

---

## VII. Cải Tiến Có Thể

1. **Mở rộng chaining_rules:** Thêm chuỗi suy luận theo từng ngành
2. **Soft Thresholds:** Dùng fuzzy logic thay vì cứng (Toan ≥ 8 → degree 0.8)
3. **Validation Workshop:** Họp với 10-15 giáo viên chuyên gia
4. **Dynamic Thresholds:** Thresholds có thể thay đổi theo năm
5. **Explainability:** Chi tiết hơn (VD: "Cần cải Lý thêm 0.5 điểm")

---

## VIII. Tệp Liên Quan

| Tệp | Mục đích |
|-----|---------|
| `rules_config.json` | Cấu hình 20+ luật (JSON) |
| `knowledge_rules.py` | Engine: load JSON → evaluate / forward_chain |
| `hybrid_fusion.py` | Sử dụng KBS score + ML score |
| `config.py` | Thông tin ngành, features |

---

**Cập nhật lần cuối:** 30/04/2026  
**Phiên bản:** 3.0  
**Format:** JSON-based, dynamic thresholds

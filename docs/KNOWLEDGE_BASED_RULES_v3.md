# Luật tri thức chuyên gia (KBS) 

**Hệ thống luật theo khối trong `rules_config.json` (JSON) + Conflict Resolution + Forward chaining (bonus) + Specificity**

---

## I. Tổng Quan Kiến Trúc KBS 



```


v3.0 :
- Luật theo ngành trong `rules_config.json` (`khtn_rules`, `khxh_rules`)
- 2 khối (KHTN: 5 ngành, KHXH: 4 ngành), 6 môn/khối
- **Forward chaining:** `chaining_rules` trong JSON → `forward_chain()` sau khi chọn luật nền
- `_build_condition()` biên dịch JSON → callable
```

### Thống kê luật (`rules_config.json`, bản 3.0)

Số liệu dưới đây khớp với nội dung JSON hiện tại: mỗi **mục ngành** có 4 **luật nền** (Very_Fit / Fit / Medium / Not_Fit) và tối đa thêm các **luật chuỗi** trong `chaining_rules`.

| Phạm vi | Số ngành (key) | Luật nền | Luật chuỗi | Tổng định nghĩa |
|--------|-----------------|----------|------------|-----------------|
| **KHTN** (`khtn_rules`) | 5 (`0_IT` … `4_NongLamNgu`) | 5 × 4 = **20** | 5 × 2 = **10** | **30** |
| **KHXH** (`khxh_rules`) | 4 (`1_KinhTe`, `5_SuPham`, `6_Luat`, `7_DuLich`) | 4 × 4 = **16** | 4 × 2 = **8** | **24** |
| **Toàn tệp** | 9 mục ngành (Kinh tế khai báo riêng theo khối) | **36** | **18** | **54** |

**Luật nền theo toán tử:** mỗi ngành có 3 luật `AND` + 1 luật `OR_LESS_THAN` (Not_Fit) → **27** luật `AND` + **9** luật `OR_LESS_THAN` = **36**.

**Luật chuỗi:** mỗi ngành có **2** mục trong `chaining_rules` (bonus điểm khi đã khớp luật nền trong `requires` và thỏa thêm `threshold`). Tổng **18** luật chuỗi (KHTN 10 + KHXH 8).

**Chi tiết theo key ngành**

| Key | `major_name` | Luật nền | Luật chuỗi |
|-----|----------------|----------|------------|
| `0_IT` | IT | 4 | 2 |
| `1_KinhTe` (KHTN) | Kinh tế | 4 | 2 |
| `2_YKhoa` | Y khoa | 4 | 2 |
| `3_KyThuat` | Kỹ thuật | 4 | 2 |
| `4_NongLamNgu` | Nông-Lâm-Ngư | 4 | 2 |
| `1_KinhTe` (KHXH) | Kinh tế | 4 | 2 |
| `5_SuPham` | Sư phạm | 4 | 2 |
| `6_Luat` | Luật pháp | 4 | 2 |
| `7_DuLich` | Du lịch | 4 | 2 |

**Ghi chú khi chạy engine:** với một khối (`khtn` hoặc `khxh`), engine chỉ duyệt luật nền của các ngành thuộc khối đó (tối đa **20** hoặc **16** luật nền khi gọi `evaluate_all_majors`), cộng thêm luật chuỗi tương ứng từng ngành sau khi đã chọn luật nền thắng.

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
Duyệt luật nền của các ngành trong khối (tối đa 20 KHTN / 16 KHXH; xem mục Thống kê luật)
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
# dict: tên ngành → dict kết quả (score, rule_name, reason, chain_applied, reasoning_chain, ...)
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

### 6.1 Chuỗi suy luận theo từng ngành (`reasoning_chain`)

Mỗi lần gọi `evaluate(...)` hoặc `calculate_kbs_score` / hybrid, kết quả KBS có thêm **`reasoning_chain`**: `list[str]` — các bước tiếng Việt cố định:

1. **Bước 1:** Ngành + điểm các môn trọng tâm + điểm liên quan TB (tie-break).
2. **Bước 2:** Luật cơ sở được chọn sau giải quyết xung đột + điểm nền.
3. **Bước 3+:** Mỗi luật chuỗi (`chaining_rules`) kích hoạt được (bonus), hoặc thông báo không có chuỗi thỏa.
4. **Bước cuối:** Tổng kết điểm nền + bonus (trần `max_score`).

`get_ranking` và `get_hybrid_ranking` trả về `reasoning_chain` **cho mỗi ngành** trong kết quả xếp hạng. Trên UI Streamlit hiện tại, chuỗi được hiển thị ở tab **Kết quả chính** cho **ngành đề xuất** (top-1), mục **Chuỗi suy luận KBS (theo ngành đề xuất)**.

---

## VII. Cải Tiến Có Thể

1. ~~**Mở rộng chaining_rules:** Thêm chuỗi suy luận theo từng ngành~~ — Đã bổ sung thêm luật chuỗi trong `rules_config.json` và trường `reasoning_chain` trong engine
2. **Soft Thresholds:** Dùng fuzzy logic thay vì cứng (Toan ≥ 8 → degree 0.8)
3. **Validation Workshop:** Họp với 10-15 giáo viên chuyên gia
4. **Dynamic Thresholds:** Thresholds có thể thay đổi theo năm
5. **Explainability:** Chi tiết hơn (VD: "Cần cải Lý thêm 0.5 điểm")

---

## VIII. Tệp Liên Quan

| Tệp | Mục đích |
|-----|---------|
| `rules_config.json` | Luật KHTN/KHXH + `chaining_rules` (JSON) |
| `kbs/knowledge_rules.py` | Engine: load JSON → evaluate / forward_chain / `reasoning_chain` |
| `kbs/hybrid_fusion.py` | ML + KBS + VETO + ranking |
| `kbs/config.py` | Ngành, features, RF params, **VETO_***, đường dẫn dữ liệu/model |
| `scripts/tune_veto.py` | (Tuỳ chọn) quét lưới tham số VETO trên tập test |

---


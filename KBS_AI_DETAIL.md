

## Mục Lục


---

## 1. Tổng Quan Pipeline

```
┌──────────────┐    ┌──────────────┐    ┌──────────────────────────────┐
│ create_data  │───▶│ train_model  │───▶│         rf_model.pkl         │
│   .py        │    │    .py       │    │  (Random Forest đã train)    │
└──────────────┘    └──────────────┘    └─────────────┬────────────────┘
                                                      │
                                                      ▼
┌──────────────┐    ┌──────────────────────────────────────────────────┐
│  app.py      │───▶│           hybrid_fusion.py                      │
│  (Streamlit) │    │  ┌─────────────┐   ┌──────────────────────┐     │
│  9 điểm môn  │    │  │ ML Score    │   │ KBS Score            │     │
│              │    │  │ (RF model)  │   │ (knowledge_rules.py) │     │
│              │    │  └──────┬──────┘   └──────────┬───────────┘     │
│              │    │         │   0.6×ML + 0.4×KBS  │                 │
│              │    │         └────────┬─────────────┘                 │
│              │    │                  ▼                               │
│              │◀───│         Hybrid Score (0-100%)                    │
└──────────────┘    └──────────────────────────────────────────────────┘
```

---

## Bước 1: Tạo Dữ Liệu

**File:** `create_data.py`  
**Mục đích:** Tạo dataset tổng hợp để huấn luyện ML

### Đầu Vào

| Tham số | Giá trị | Nguồn |
|---------|---------|-------|
| `NUM_SAMPLES` | 117,280 | `config.py` |
| `FEATURE_NAMES` | 9 môn: toan, ly, hoa, sinh, van, anh, lich_su, dia_ly, tin_hoc | `config.py` |
| `LABEL_NOISE_RATE` | 0.08 (8%) | `config.py` |
| `FEATURE_NOISE_STD` | 0.3 | `config.py` |
| `RANDOM_STATE` | 42 | `config.py` |

### Quá Trình

```
1. Tạo 117,280 hàng, mỗi feature ~ Uniform(3, 10)
      ↓
2. Gán nhãn bằng assign_major(row):
   - IT:       Toán≥7.5 AND Tin≥7.5 AND (Toán+Tin+Lý)/3≥7  → 0
   - Kỹ thuật: Toán≥8 AND Lý≥8                              → 3
   - Y khoa:   Sinh≥7.5 AND Hóa≥7.5 AND Lý≥6               → 2
   - Nông-Lâm: Sinh≥7 AND ĐL≥7.5 AND Hóa≥6                 → 4
   - Luật:     LS≥7.5 AND Văn≥7                              → 6
   - Sư phạm:  Văn≥7 AND Anh≥7                               → 5
   - Kinh tế:  Toán≥6 AND Anh≥7 AND Văn≥5.5                 → 1
   - Du lịch:  ĐL≥6.5 AND Anh≥6.5 AND Văn≥6                 → 7
      ↓
3. Thêm Feature Noise: Gaussian(μ=0, σ=0.3) → clip [0, 10]
      ↓
4. Thêm Label Noise: 8% mẫu đổi nhãn ngẫu nhiên (0-7)
      ↓
5. Cân bằng các lớp (undersampling)
```

### Đầu Ra

| Output | Mô tả |
|--------|-------|
| `data_tuyensinh_balanced.csv` | 117,280 rows × 10 cols (9 features + 1 label), ~18.5 MB |

---

## Bước 2: Huấn Luyện ML

**File:** `train_model.py`  
**Mục đích:** Huấn luyện Random Forest Classifier

### Đầu Vào

| Tham số | Giá trị | Nguồn |
|---------|---------|-------|
| Dataset | `data_tuyensinh_balanced.csv` | Bước 1 |
| X (features) | 9 cột: toan, ly, hoa, sinh, van, anh, lich_su, dia_ly, tin_hoc | DataFrame |
| y (label) | cột `nganh_hoc` (0-7) | DataFrame |
| `TEST_SIZE` | 0.2 (80/20 split) | `config.py` |
| `RF_PARAMS` | n_estimators=100, max_depth=15, min_samples_split=10, min_samples_leaf=5 | `config.py` |

### Quá Trình

```
1. Load CSV → DataFrame (117,280 × 10)
      ↓
2. Tách X (9 features) và y (label)
      ↓
3. Train/Test split: 80% train (93,824) / 20% test (23,456)
      ↓
4. Khởi tạo RandomForestClassifier(**RF_PARAMS)
      ↓
5. model.fit(X_train, y_train)  → 100 cây quyết định song song
      ↓
6. Đánh giá:
   - accuracy_score(y_test, y_pred)         → ~75% (do noisy data)
   - classification_report()                → precision, recall, f1 per class
   - cross_val_score(5-fold)                → CV accuracy
   - feature_importances_                   → tầm quan trọng 9 features
      ↓
7. Lưu model bằng pickle
```

### Đầu Ra

| Output | Mô tả |
|--------|-------|
| `rf_model.pkl` | Random Forest model serialized (~95 MB) |
| Console log | Accuracy ~75%, CV scores, feature importance, confusion matrix |



---

## Bước 3: Người Dùng Nhập Điểm

**File:** `app.py` (Streamlit UI)  
**Mục đích:** Thu thập 9 điểm môn học từ người dùng

### Đầu Vào

| Input | Loại | Khoảng |
|-------|------|--------|
| 9 thanh trượt Streamlit | `st.slider` | 0.0 → 10.0 (step 0.5) |

### Quá Trình

```
Sidebar Streamlit:
├─ Toán:     st.slider(0, 10, default=8)
├─ Lý:       st.slider(0, 10, default=7)
├─ Hóa:      st.slider(0, 10, default=6)
├─ Sinh:     st.slider(0, 10, default=7)
├─ Văn:      st.slider(0, 10, default=5)
├─ Anh:      st.slider(0, 10, default=8)
├─ Lịch sử:  st.slider(0, 10, default=6)
├─ Địa lý:   st.slider(0, 10, default=6)
└─ Tin học:   st.slider(0, 10, default=9)
      ↓
user_scores = [Toán, Lý, Hóa, Sinh, Văn, Anh, LS, DL, Tin]
      ↓
Gọi hybrid_fusion.get_hybrid_ranking(user_scores)
```

### Đầu Ra

| Output | Giá trị |
|--------|---------|
| `user_scores` | `list[float]` — 9 phần tử, phạm vi [0, 10] |

---

## Bước 4: Tính ML Score

**File:** `hybrid_fusion.py` → hàm `calculate_ml_score()`  
**Mục đích:** Dự đoán xác suất ngành bằng Random Forest

### Đầu Vào

| Tham số | Kiểu | Ví dụ |
|---------|------|-------|
| `user_scores` | list[float] × 9 | `[9, 8, 5, 4, 5, 8, 5, 5, 9.5]` |
| `major_index` | int (0-7) | `0` (IT) |
| `model` | RandomForestClassifier | Loaded from `rf_model.pkl` |

### Quá Trình Chi Tiết

```
1. NORMALIZE: user_scores [0,10] → [3,10]
   Công thức: output = 3 + (input / 10) × 7
   Ví dụ: Toán=9 → 3 + (9/10) × 7 = 9.3
      ↓
2. TẠO DataFrame:
   X_df = pd.DataFrame([normalized], columns=FEATURE_NAMES)
   → DataFrame 1×9 với tên cột chính xác
      ↓
3. DỰ ĐOÁN:
   probs = model.predict_proba(X_df)[0]
   → mảng 8 phần tử [p_IT, p_KinhTe, p_YKhoa, ..., p_DuLich]
   Ví dụ: [0.61, 0.03, 0.02, 0.15, 0.01, 0.02, 0.01, 0.15]
      ↓
4. LẤY XÁC SUẤT cho ngành:
   raw_prob = probs[major_index]
   Ví dụ: probs[0] = 0.61 (IT)
      ↓
5. TEMPERATURE SCALING (tăng confidence):
   temperature = 0.7
   boosted_prob = raw_prob ^ (1/0.7) = 0.61^1.43 ≈ 0.49
   scaled_prob = min(boosted_prob, 1.0)
      ↓
6. CHUYỂN SANG %:
   baseline = 1/8 = 0.125
   ml_score = ((scaled_prob - baseline) / (1 - baseline)) × 100
   Ví dụ: ((0.49 - 0.125) / 0.875) × 100 ≈ 41.7%
      ↓
7. CLAMP: max(0, min(100, ml_score))
```

### Đầu Ra

```python
{
    'score': 41.7,           # ML Score (0-100%)
    'raw_prob': 0.61,        # Xác suất thô từ RF
    'major': 'IT'            # Tên ngành
}
```

---

## Bước 5: Tính KBS Score

**File:** `knowledge_rules.py` → class `KnowledgeRuleEngine` → method `evaluate()`  
**Mục đích:** Đánh giá bằng 32 luật chuyên gia + Forward Chaining + Conflict Resolution

### Đầu Vào

| Tham số | Kiểu | Ví dụ |
|---------|------|-------|
| `user_scores` | list[float] × 9 | `[9, 8, 5, 4, 5, 8, 5, 5, 9.5]` |
| `major_index` | int (0-7) | `0` (IT) |

### Quá Trình Chi Tiết — 3 Bước Con

#### Bước 5.1: Tìm Tất Cả Luật Khớp (Rule Matching)

```
Đầu vào: user_scores = [9, 8, 5, 4, 5, 8, 5, 5, 9.5], major_index = 0 (IT)

Duyệt 4 luật của IT:
┌─────────────────┬────────────────────────────────────────────┬───────┬──────┬────────┐
│ Luật            │ Điều kiện                                  │ Kết quả│ Score│ Spec   │
├─────────────────┼────────────────────────────────────────────┼───────┼──────┼────────┤
│ IT_Very_Fit     │ Toán(9)≥8 ✓ AND Tin(9.5)≥8 ✓ AND Lý(8)≥7 ✓│ KHỚP │  95  │   3    │
│ IT_Fit          │ Toán(9)≥7 ✓ AND Tin(9.5)≥7 ✓ AND Lý(8)≥6 ✓ AND Anh(8)≥5 ✓│ KHỚP │  80  │   4    │
│ IT_Medium       │ Toán(9)≥7 ✓ AND Tin(9.5)≥6.5 ✓            │ KHỚP │  65  │   2    │
│ IT_Not_Fit      │ Toán(9)<6 ✗ OR Tin(9.5)<6 ✗               │ KHÔNG │  20  │   1    │
└─────────────────┴────────────────────────────────────────────┴───────┴──────┴────────┘

Đầu ra: matched_rules = [IT_Very_Fit, IT_Fit, IT_Medium]
```

#### Bước 5.2: Conflict Resolution (Giải Quyết Xung Đột)

```
Đầu vào: matched_rules = [IT_Very_Fit(spec=3,score=95), IT_Fit(spec=4,score=80), IT_Medium(spec=2,score=65)]

Thuật toán:
  1. Sắp xếp theo specificity GIẢM DẦN
  2. Nếu spec bằng nhau → sắp xếp theo score GIẢM DẦN

Sắp xếp:
  IT_Fit     (spec=4, score=80)  ← ƯU TIÊN (spec cao nhất)
  IT_Very_Fit(spec=3, score=95)
  IT_Medium  (spec=2, score=65)

Đầu ra: best_rule = IT_Fit, base_score = 80
```

**Tại sao IT_Fit (80) thắng IT_Very_Fit (95)?**  
→ IT_Fit có **4 điều kiện** (spec=4) > IT_Very_Fit có **3 điều kiện** (spec=3).  
→ Luật cụ thể hơn được ưu tiên hơn, vì nó khớp chặt chẽ hơn với hồ sơ học sinh.

#### Bước 5.3: Forward Chaining (Suy Luận Chuỗi)

```
Đầu vào: best_rule = IT_Fit, base_score = 80, user_scores

Duyệt chaining_rules cho IT (major_index=0):
┌─────────────────┬─────────────────────────┬────────────────────────────┬───────┬────────┐
│ Chain Rule      │ Requires                │ Điều kiện phụ              │ Bonus │ Kết quả│
├─────────────────┼─────────────────────────┼────────────────────────────┼───────┼────────┤
│ IT_Quoc_Te      │ IT_Very_Fit, IT_Fit     │ Anh(8) ≥ 7 ✓              │  +3   │ ÁP DỤNG│
│ IT_TinSinhHoc   │ IT_Very_Fit, IT_Fit     │ Sinh(4) ≥ 7 ✗             │  +2   │ BỎ QUA │
└─────────────────┴─────────────────────────┴────────────────────────────┴───────┴────────┘

Tính: final_score = min(100, 80 + 3) = 83

Đầu ra:
  final_score = 83
  chain_details = [{'chain_name': 'IT_Quoc_Te', 'bonus': 3, 'reason': 'Phù hợp IT Quốc tế (Anh tốt)'}]
```

#### Bước 5.4: Tính Relevance Score (Phá Hòa)

```
Đầu vào: user_scores, major_index = 0 (IT)

MAJOR_KEY_SUBJECTS[0] = [0, 8, 1]  → Toán, Tin, Lý
relevance_score = (Toán + Tin + Lý) / 3 = (9 + 9.5 + 8) / 3 = 8.83

Đầu ra: relevance_score = 8.83
(Dùng để phá hòa khi hybrid_score bằng nhau giữa 2 ngành)
```

### Đầu Ra Tổng Hợp Bước 5

```python
{
    'score': 83,                      # KBS Score cuối cùng (0-100)
    'rule_name': 'IT_Fit',            # Luật cơ sở được chọn
    'description': 'Khá phù hợp IT', # Mô tả luật
    'reason': 'Đáp ứng yêu cầu cơ bản, có khả năng teamwork | Suy luận chuỗi: Phù hợp IT Quốc tế (Anh tốt)',
    'major': 'IT',                    # Tên ngành
    'relevance_score': 8.83,          # Điểm TB môn liên quan (tie-breaking)
    'chain_applied': True,            # Có forward chaining
    'chain_details': [                # Chi tiết chuỗi
        {'chain_name': 'IT_Quoc_Te', 'bonus': 3, 'reason': 'Phù hợp IT Quốc tế (Anh tốt)'}
    ]
}
```

---

## Bước 6: Kết Hợp Hybrid

**File:** `hybrid_fusion.py` → hàm `calculate_hybrid_score()`  
**Mục đích:** Kết hợp ML + KBS thành 1 điểm duy nhất

### Đầu Vào

| Tham số | Giá trị (ví dụ) |
|---------|-----------------|
| `ml_result` | `{'score': 41.7, 'raw_prob': 0.61, ...}` (từ Bước 4) |
| `kbs_result` | `{'score': 83, 'rule_name': 'IT_Fit', ...}` (từ Bước 5) |
| `ML_WEIGHT` | 0.6 |
| `KBS_WEIGHT` | 0.4 |

### Quá Trình

```
1. Lấy scores:
   ml_score  = 41.7  (từ Bước 4)
   kbs_score = 83    (từ Bước 5)
      ↓
2. Công thức Hybrid:
   hybrid_score = 0.6 × ml_score + 0.4 × kbs_score
                = 0.6 × 41.7    + 0.4 × 83
                = 25.02          + 33.2
                = 58.2%
      ↓
3. Tạo giải thích:
   "NGÀNH: IT
    ĐIỂM CUỐI CÙNG: 58.2% (HYBRID)
    TÍNH TOÁN: 0.6 × 41.7 + 0.4 × 83 = 58.2
    ML Score: 41.7% (60%)
    KBS Score: 83% (40%)"
```

**Fallback:** Nếu ML model không có (`ml_score = None`) → `hybrid_score = kbs_score` (100% KBS)

### Đầu Ra

```python
{
    'major': 'IT',
    'hybrid_score': 58.2,          # ← KẾT QUẢ CUỐI CÙNG
    'ml_score': 41.7,
    'kbs_score': 83,
    'relevance_score': 8.83,       # Tie-breaking
    'ml_weight': 0.6,
    'kbs_weight': 0.4,
    'ml_details': { ... },         # Dict đầy đủ từ Bước 4
    'kbs_details': { ... },        # Dict đầy đủ từ Bước 5
    'explanation': '...'           # Giải thích tiếng Việt
}
```

---

## Bước 7: Xếp Hạng & Hiển Thị

**File:** `hybrid_fusion.py` → `get_hybrid_ranking()` + `app.py`  
**Mục đích:** Tính Hybrid cho TẤT CẢ 8 ngành, sắp xếp, hiển thị

### Đầu Vào

| Tham số | Giá trị |
|---------|---------|
| `user_scores` | `[9, 8, 5, 4, 5, 8, 5, 5, 9.5]` |

### Quá Trình

```
1. FOR i = 0 → 7 (8 ngành):
     results[i] = calculate_hybrid_score(user_scores, i, model)
      ↓
2. Sắp xếp: results.sort(key=(hybrid_score, relevance_score), reverse=True)
      ↓
3. Gán rank: 1, 2, 3, ..., 8
      ↓
4. Hiển thị trên Streamlit:
   Tab 1: Kết quả chính (top 1 ngành, Hybrid Score, giải thích)
   Tab 2: Phân tích chi tiết (Radar chart 9 môn, ML vs KBS breakdown)
   Tab 3: So sánh 8 ngành (bar chart, bảng xếp hạng)
```

### Đầu Ra

```python
[
    {'rank': 1, 'major': 'IT',       'hybrid_score': 58.2, 'ml_score': 41.7, 'kbs_score': 83, ...},
    {'rank': 2, 'major': 'Kỹ thuật', 'hybrid_score': 55.1, 'ml_score': 38.4, 'kbs_score': 80, ...},
    {'rank': 3, 'major': 'Kinh tế',  'hybrid_score': 32.5, 'ml_score': 12.3, 'kbs_score': 63, ...},
    ...
    {'rank': 8, 'major': 'Y khoa',   'hybrid_score': 18.0, 'ml_score': 5.2,  'kbs_score': 37, ...},
]
```

---

## Sơ Đồ Luồng Dữ Liệu Tổng Hợp

```
╔══════════════════════════════════════════════════════════════════════════╗
║  NGƯỜI DÙNG NHẬP 9 ĐIỂM MÔN HỌC                                      ║
║  [Toán=9, Lý=8, Hóa=5, Sinh=4, Văn=5, Anh=8, LS=5, DL=5, Tin=9.5]  ║
╚═══════════════════════════╤══════════════════════════════════════════════╝
                            │
              ┌─────────────┴──────────────┐
              ▼                            ▼
  ╔═══════════════════╗        ╔════════════════════════════════════╗
  ║   ML BRANCH       ║        ║   KBS BRANCH                      ║
  ║                   ║        ║                                    ║
  ║ 1.Normalize [3,10]║        ║ 1. Rule Matching (32 luật)        ║
  ║ 2.RF predict_proba║        ║    → tìm tất cả luật khớp         ║
  ║ 3.Temperature     ║        ║                                    ║
  ║   scaling (T=0.7) ║        ║ 2. Conflict Resolution            ║
  ║ 4.Baseline adjust ║        ║    → chọn luật spec cao nhất      ║
  ║                   ║        ║                                    ║
  ║ → ML Score: 41.7% ║        ║ 3. Forward Chaining               ║
  ╚════════╤══════════╝        ║    → cộng bonus nếu đủ điều kiện  ║
           │                   ║                                    ║
           │                   ║ 4. Relevance Score (tie-break)     ║
           │                   ║                                    ║
           │                   ║ → KBS Score: 83%                   ║
           │                   ╚═══════════════╤════════════════════╝
           │                                   │
           └───────────────┬───────────────────┘
                           ▼
           ╔═══════════════════════════════╗
           ║   HYBRID FUSION              ║
           ║                              ║
           ║   0.6 × 41.7 + 0.4 × 83     ║
           ║   = 25.02 + 33.2             ║
           ║   = 58.2%                    ║
           ╚══════════════╤════════════════╝
                          ▼
           ╔═══════════════════════════════╗
           ║   LẶP CHO 8 NGÀNH           ║
           ║   → Sắp xếp theo hybrid_score║
           ║   → Tie-break: relevance     ║
           ╚══════════════╤════════════════╝
                          ▼
           ╔═══════════════════════════════╗
           ║   STREAMLIT UI               ║
           ║   Tab 1: Kết quả chính       ║
           ║   Tab 2: Radar + phân tích   ║
           ║   Tab 3: So sánh 8 ngành     ║
           ╚═══════════════════════════════╝
```

---

## Chi Tiết KBS Engine

### Kiến Trúc Class

```python
class KnowledgeRuleEngine:
    # Thuộc tính
    MAJOR_NAMES          # 8 ngành
    FEATURE_NAMES        # 9 môn
    MAJOR_KEY_SUBJECTS   # Môn chính mỗi ngành (tie-breaking)
    rules                # 32 luật cơ sở (4 × 8)
    chaining_rules       # 10 luật chuỗi

    # Phương thức chính
    evaluate(scores, major_index)        # Đánh giá 1 ngành (3 bước)
    evaluate_all_majors(scores)          # Đánh giá tất cả 8 ngành
    get_ranking(scores)                  # Xếp hạng 8 ngành

    # Phương thức nội bộ
    resolve_conflicts(matched_rules)     # Bước 2: Chọn luật tốt nhất
    forward_chain(scores, major, rule, score)  # Bước 3: Cộng bonus
    calculate_relevance_score(scores, major)   # Tie-breaking
```

### Cấu Trúc 1 Luật Cơ Sở

```python
{
    'name': 'IT_Fit',                                           # ID
    'description': 'Khá phù hợp IT',                           # Mô tả
    'condition': lambda s: s[0]>=7 and s[8]>=7 and s[1]>=6 and s[5]>=5,  # Hàm kiểm tra
    'score': 80,                                                # Điểm (0-100)
    'specificity': 4,                                           # Số điều kiện
    'reason': 'Đáp ứng yêu cầu cơ bản, có khả năng teamwork'  # Giải thích
}
```

### Cấu Trúc 1 Luật Chuỗi (Forward Chaining)

```python
{
    'name': 'IT_Quoc_Te',                        # ID chuỗi
    'requires': ['IT_Very_Fit', 'IT_Fit'],       # Luật cơ sở phải khớp trước
    'condition': lambda s: s[5] >= 7,            # Điều kiện bổ sung (Anh ≥ 7)
    'bonus': 3,                                  # Điểm cộng thêm
    'reason': 'Phù hợp IT Quốc tế (Anh tốt)'   # Giải thích
}
```

### Conflict Resolution — Thuật Toán

```python
def resolve_conflicts(matched_rules):
    sorted_rules = sorted(
        matched_rules,
        key=lambda r: (r['specificity'], r['score']),  # Ưu tiên: spec > score
        reverse=True  # Giảm dần
    )
    return sorted_rules[0]  # Luật cụ thể nhất
```

### Bảng Tổng Kết 32 Luật + 10 Chuỗi

| Ngành | Very_Fit | Fit | Medium | Not_Fit | Chaining |
|-------|----------|-----|--------|---------|----------|
| IT | 95 (sp3) | 80 (sp4) | 65 (sp2) | 20 (sp1) | IT_Quoc_Te(+3), IT_TinSinhHoc(+2) |
| Kinh tế | 90 (sp3) | 75 (sp3) | 55 (sp2) | 15 (sp1) | KinhTe_So(+3) |
| Y khoa | 95 (sp3) | 85 (sp4) | 65 (sp2) | 15 (sp1) | YKhoa_QuocTe(+3), YKhoa_NghienCuu(+2) |
| Kỹ thuật | 92 (sp3) | 80 (sp4) | 65 (sp2) | 18 (sp1) | KyThuat_CongNghe(+3) |
| Nông-Lâm | 88 (sp3) | 72 (sp4) | 65 (sp2) | 18 (sp1) | NongLam_CongNghe(+2) |
| Sư phạm | 90 (sp3) | 75 (sp3) | 60 (sp2) | 15 (sp1) | SuPham_QuocTe(+3) |
| Luật | 90 (sp3) | 75 (sp3) | 60 (sp2) | 15 (sp1) | Luat_QuocTe(+3) |
| Du lịch | 88 (sp3) | 78 (sp3) | 68 (sp3) | 15 (sp1) | DuLich_QuocTe(+3) |

---

## Chi Tiết AI / ML Engine

### Random Forest — Cách Hoạt Động

```
100 CÂY QUYẾT ĐỊNH (Decision Trees)
├─ Mỗi cây được train trên subsample ngẫu nhiên (bootstrap)
├─ Mỗi node split chọn subset features ngẫu nhiên
├─ max_depth = 15 (giới hạn độ sâu → chống overfitting)
├─ min_samples_split = 10, min_samples_leaf = 5
│
└─ Khi predict:
   ├─ Mỗi cây bỏ phiếu cho 1 trong 8 lớp
   ├─ predict_proba = tỷ lệ phiếu / 100
   │  Ví dụ: 61 cây chọn IT → probs[IT] = 0.61
   └─ Dùng probs[major_index] cho ML Score
```

### Temperature Scaling — Tại Sao?

```
Vấn đề: RF với 8 lớp → xác suất max thường chỉ 0.3-0.6 (thấp)
Giải pháp: Temperature T=0.7 → "làm sắc nét" phân phối

Trước:  [0.61, 0.15, 0.08, 0.06, 0.04, 0.03, 0.02, 0.01]
Sau:    [0.49, 0.08, 0.03, 0.02, 0.01, 0.01, 0.00, 0.00]
                ↑ Sự khác biệt rõ ràng hơn
```

### ML Score vs KBS Score — So Sánh

| Khía cạnh | ML Score | KBS Score |
|-----------|----------|-----------|
| **Nguồn** | Dữ liệu 117K mẫu | 32 luật chuyên gia |
| **Cách tính** | RF predict_proba + scaling | Rule matching + conflict resolution + chaining |
| **Ưu điểm** | Học pattern phức tạp từ data | Giải thích được, suy luận chuỗi |
| **Nhược điểm** | Bị ảnh hưởng bởi noise | Không linh hoạt với trường hợp ngoại lệ |
| **Khoảng** | 0-100% (thường 10-60%) | 15-98% (phụ thuộc luật + chaining) |
| **Trọng số** | 60% | 40% |
| **Vai trò trong Hybrid** | Pattern từ dữ liệu lớn | Kiến thức chuyên gia, bù noise |

---

## Ví Dụ Chạy Tay Từ Đầu Đến Cuối

### Input: Học sinh IT chuyên, Anh tốt

```
Toán=9, Lý=8, Hóa=5, Sinh=4, Văn=5, Anh=8, LS=5, DL=5, Tin=9.5
```

### Bước 4 — ML Score cho IT (major=0)

```
Normalize:  [9.3, 8.6, 6.5, 5.8, 6.5, 8.6, 6.5, 6.5, 9.65]
RF probs:   [0.61, 0.03, 0.02, 0.15, 0.01, 0.02, 0.01, 0.15]
raw_prob:   0.61
Boosted:    0.61^(1/0.7) = 0.61^1.43 ≈ 0.49
Baseline:   0.125
ML Score:   ((0.49 - 0.125) / 0.875) × 100 ≈ 41.7%
```

### Bước 5 — KBS Score cho IT (major=0)

```
5.1 Matching:  IT_Very_Fit(95,sp3) ✓, IT_Fit(80,sp4) ✓, IT_Medium(65,sp2) ✓
5.2 Conflict:  IT_Fit wins (spec=4 > spec=3) → base=80
5.3 Chaining:  IT_Quoc_Te (Anh=8≥7) → +3 → final=83
5.4 Relevance: (9+9.5+8)/3 = 8.83
→ KBS Score = 83%
```

### Bước 6 — Hybrid Score cho IT

```
Hybrid = 0.6 × 41.7 + 0.4 × 83
       = 25.02 + 33.2
       = 58.2%
```

### Bước 7 — Lặp cho 8 ngành → Xếp hạng

```
#  Ngành          Hybrid   ML      KBS     Giải thích
1. IT             58.2%    41.7%   83%     IT_Fit + IT_Quoc_Te chain
2. Kỹ thuật       ~55%    ~38%    ~83%    KyThuat_Fit + CongNghe chain
3. Kinh tế        ~33%    ~12%    ~63%    KinhTe_Medium
4. Du lịch        ~25%     ~8%    ~50%    DuLich_Not_Fit
5. Nông-Lâm       ~22%     ~5%    ~48%    NongLamNgu_Not_Fit
6. Sư phạm        ~20%     ~5%    ~45%    SuPham_Not_Fit
7. Luật            ~18%     ~3%    ~40%    Luat_Not_Fit
8. Y khoa          ~15%     ~2%    ~35%    YKhoa_Not_Fit

→ KẾT LUẬN: Ngành phù hợp nhất là IT (58.2%), runner-up Kỹ thuật (~55%)
```

---

## Mức Độ Khuyến Nghị

### Cách Xác Định

Mức độ khuyến nghị được tính từ **Hybrid Score** (kết quả cuối cùng = 60% ML + 40% KBS).  
Hệ thống chia thành **3 mức** dựa trên ngưỡng điểm:

### Bảng Phân Loại

| Mức | Hybrid Score | Nhãn UI | Ý nghĩa | Hành động khuyến nghị |
|-----|-------------|---------|---------|----------------------|
| **Rất phù hợp** | ≥ 75% | `Good` (xanh) | Ngành phù hợp tuyệt vời | Nên ưu tiên đăng ký ngành này |
| **Khá phù hợp** | 50% – 74% | `Fair` (vàng) | Có tiềm năng, chưa tối ưu | Xem xét kèm các ngành khác |
| **Không phù hợp** | < 50% | `Low` (đỏ) | Thiếu năng lực cốt lõi | Nên chọn ngành khác phù hợp hơn |



### Hybrid Score Được Tạo Từ Đâu?

```
Hybrid Score = 0.6 × ML Score + 0.4 × KBS Score
                 ↑                    ↑
         Random Forest           32 luật chuyên gia
         (học từ data)       (conflict resolution + chaining)
```

| Thành phần | Khoảng thực tế | Vai trò |
|-----------|----------------|---------|
| ML Score | 0–60% (thường 10–50%) | Pattern phức tạp từ 117K mẫu |
| KBS Score | 15–98% (phụ thuộc luật + chaining) | Kiến thức chuyên gia, giải thích được |
| Hybrid Score | 10–80% (phụ thuộc tổ hợp) | Kết quả cuối cùng, cân bằng cả hai |

---

## Chi Tiết Noise Trong Dữ Liệu Sinh (`create_data.py`)

### Tổng Quan

Dữ liệu được tạo **không phải rule-based thuần túy** mà cố tình thêm nhiễu (noise) để mô phỏng thực tế. Có **3 loại noise**:

### 1. Feature Noise (Nhiễu Điểm Số)

**File:** `create_data.py` → `apply_feature_noise()`  
**Config:** `FEATURE_NOISE_STD = 0.3` (trong `config.py`)

**Cơ chế:**
```
Với mỗi cột điểm (9 cột):
  noise = np.random.normal(0, 0.3, N)       # N(0, 0.3)
  điểm_mới = (điểm_gốc + noise).clip(3, 10) # Giữ trong [3, 10]
```

**Ý nghĩa:**
- Mô phỏng **sai số khi nhập điểm** hoặc **biến động tự nhiên** của học sinh
- Một học sinh Toán = 8.0 thực tế có thể dao động 7.4 – 8.6 (±2σ = ±0.6)
- Phân phối Gaussian → đa số nhiễu nhỏ, ít trường hợp nhiễu lớn

**Ví dụ cụ thể:**
```
Trước noise: Toán=8.0  Lý=7.5  Hóa=6.0  ...
Noise:       +0.2     -0.4     +0.1     ...
Sau noise:   Toán=8.2  Lý=7.1  Hóa=6.1  ...
```

**Tác động lên ML:**
- RF khó học chính xác ngưỡng (ví dụ "Toán≥7.5" trở thành fuzzy boundary)
- Accuracy giảm từ ~90% (clean data) xuống **~75%** (noisy data)
- Đây là **mong muốn** — tạo bài toán khó hơn để KBS bù đắp

### 2. Label Noise (Nhiễu Nhãn)

**File:** `create_data.py` → `apply_label_noise()`  
**Config:** `LABEL_NOISE_RATE = 0.08` (8%)

**Cơ chế:**
```
n_noisy = int(117280 × 0.08) = 9382 mẫu

Với mỗi mẫu được chọn ngẫu nhiên:
  nhãn_cũ = IT (ví dụ)
  nhãn_mới = random_choice([Kinh tế, Y khoa, Kỹ thuật, ...])  # Khác nhãn cũ
```

**Ý nghĩa thực tế:**
- Mô phỏng học sinh **chọn ngành không theo điểm mạnh**
- Ví dụ: Học sinh giỏi Toán+Tin nhưng **chọn Y khoa** vì đam mê
- 8% là tỷ lệ vừa phải — đủ tạo noise mà không phá hủy pattern

**Tác động:**
```
117,280 mẫu tổng
├─ 107,898 mẫu (92%): nhãn đúng theo quy luật assign_major()
└─   9,382 mẫu (8%):  nhãn ngẫu nhiên (noise)
```


### Quy Trình Sinh Dữ Liệu Đầy Đủ

```
Bước 1: Sinh 9 điểm ngẫu nhiên uniform [3, 10]
         ↓
Bước 2: Gán nhãn bằng assign_major() (17 rules)
         ↓ (lấy mẫu cân bằng 12.5% mỗi ngành)
Bước 3: Feature Noise → N(0, 0.3) rồi clip [3, 10]
         ↓
Bước 4: Label Noise → 8% mẫu đổi nhãn random
         ↓
Bước 5: Shuffle + Lưu CSV (117,280 mẫu)
```

### Tại Sao Cần Noise?

| Không có noise | Có noise |
|---------------|----------|
| RF accuracy ~90% | RF accuracy ~75% |
| ML đủ mạnh, KBS thừa | ML yếu, KBS bù đắp rõ rệt |
| Hybrid ≈ ML (vô nghĩa) | Hybrid > ML (có giá trị) |
| Không giống thực tế | Giống dữ liệu thực: sai số, ngoại lệ |

---

## Chi Tiết 32 Luật Cơ Sở (`knowledge_rules.py`)

### Cấu Trúc Mỗi Luật

```python
{
    'name': 'IT_Very_Fit',           # Tên định danh
    'description': 'Rất phù hợp IT', # Mô tả
    'condition': lambda s: s[0]>=8 and s[8]>=8 and s[1]>=7,  # Hàm kiểm tra
    'score': 95,                      # Điểm nếu khớp (0-100)
    'specificity': 3,                 # Số điều kiện (dùng cho conflict resolution)
    'reason': 'Toán, Tin, Lý đều xuất sắc'  # Giải thích
}
```

**Chỉ số môn học:** `s[0]=Toán, s[1]=Lý, s[2]=Hóa, s[3]=Sinh, s[4]=Văn, s[5]=Anh, s[6]=Lịch sử, s[7]=Địa lý, s[8]=Tin`

### Bảng Đầy Đủ 32 Luật (4 luật × 8 ngành)

#### IT - Công Nghệ Thông Tin (index=0)

| Luật | Điều kiện | Score | Spec | Reason |
|------|----------|-------|------|--------|
| **IT_Very_Fit** | Toán≥8 AND Tin≥8 AND Lý≥7 | 95 | 3 | Toán, Tin, Lý đều xuất sắc |
| **IT_Fit** | Toán≥7 AND Tin≥7 AND Lý≥6 AND Anh≥5 | 80 | 4 | Đáp ứng cơ bản, có teamwork |
| **IT_Medium** | Toán≥7 AND Tin≥6.5 | 65 | 2 | Tiềm năng, cần cải thiện |
| **IT_Not_Fit** | Toán<6 OR Tin<6 | 20 | 1 | Thiếu kỹ năng cơ bản |

#### Kinh Tế - Kinh Doanh (index=1)

| Luật | Điều kiện | Score | Spec | Reason |
|------|----------|-------|------|--------|
| **KinhTe_Very_Fit** | Anh≥8 AND Toán≥7.5 AND Văn≥7 | 90 | 3 | Anh, Toán, Văn đều tốt |
| **KinhTe_Fit** | Anh≥7 AND Toán≥6.5 AND Văn≥6.5 | 75 | 3 | Đáp ứng yêu cầu |
| **KinhTe_Medium** | Anh≥6.5 AND Toán≥6 | 55 | 2 | Có khả năng nhưng yếu Anh |
| **KinhTe_Not_Fit** | Anh<6 OR Toán<5.5 | 15 | 1 | Kỹ năng không đủ |

#### Y Khoa - Sức Khỏe (index=2)

| Luật | Điều kiện | Score | Spec | Reason |
|------|----------|-------|------|--------|
| **YKhoa_Very_Fit** | Sinh≥8.5 AND Hóa≥8 AND Văn≥7 | 95 | 3 | Sinh, Hóa, Văn xuất sắc |
| **YKhoa_Fit** | Sinh≥8 AND Hóa≥7.5 AND Lý≥6 AND Văn≥6 | 85 | 4 | Đáp ứng, có nền Lý |
| **YKhoa_Medium** | Sinh≥7.5 AND Hóa≥7 | 65 | 2 | Khá nhưng chưa xuất sắc |
| **YKhoa_Not_Fit** | Sinh<7 OR Hóa<6.5 | 15 | 1 | Từ khối khác |

#### Kỹ Thuật - Xây Dựng (index=3)

| Luật | Điều kiện | Score | Spec | Reason |
|------|----------|-------|------|--------|
| **KyThuat_Very_Fit** | Toán≥8 AND Lý≥8 AND Hóa≥7 | 92 | 3 | Toán, Lý, Hóa xuất sắc |
| **KyThuat_Fit** | Toán≥7.5 AND Lý≥7 AND Hóa≥6.5 AND Tin≥5 | 80 | 4 | Đáp ứng, có Tin học |
| **KyThuat_Medium** | Toán≥7.5 AND Lý≥6.5 | 65 | 2 | Toán tốt, Lý chưa cao |
| **KyThuat_Not_Fit** | Toán<6.5 OR Lý<6 | 18 | 1 | Thiếu nền tảng |

#### Nông-Lâm-Ngư (index=4)

| Luật | Điều kiện | Score | Spec | Reason |
|------|----------|-------|------|--------|
| **NongLamNgu_Very_Fit** | Sinh≥8 AND Hóa≥7.5 AND Địa≥7 | 88 | 3 | Sinh, Hóa, Địa tốt |
| **NongLamNgu_Fit** | Sinh≥7.5 AND Hóa≥7 AND Địa≥6 AND Toán≥5.5 | 72 | 4 | Đáp ứng, có tính toán |
| **NongLamNgu_Medium** | Sinh≥7 AND Địa≥7 | 65 | 2 | Địa lý tốt |
| **NongLamNgu_Not_Fit** | Sinh<6.5 OR Hóa<5.5 | 18 | 1 | Kỹ năng không đủ |

#### Sư Phạm - Giáo Dục (index=5)

| Luật | Điều kiện | Score | Spec | Reason |
|------|----------|-------|------|--------|
| **SuPham_Very_Fit** | Văn≥8 AND Anh≥7.5 AND Lịch sử≥7 | 90 | 3 | Văn, Anh, Lịch sử xuất sắc |
| **SuPham_Fit** | Văn≥7 AND Anh≥7 AND Lịch sử≥6.5 | 75 | 3 | Đáp ứng, có truyền đạt |
| **SuPham_Medium** | Văn≥6.5 AND Anh≥6.5 | 60 | 2 | Cần cải thiện kỹ năng mềm |
| **SuPham_Not_Fit** | Văn<6 OR Anh<5.5 | 15 | 1 | Thiếu kỹ năng truyền đạt |

#### Luật Pháp (index=6)

| Luật | Điều kiện | Score | Spec | Reason |
|------|----------|-------|------|--------|
| **Luat_Very_Fit** | Văn≥8 AND Lịch sử≥8 AND Anh≥7 | 90 | 3 | Văn, Lịch sử, Anh xuất sắc |
| **Luat_Fit** | Văn≥7 AND Lịch sử≥7 AND Anh≥6.5 | 75 | 3 | Đáp ứng, có phản biện |
| **Luat_Medium** | Văn≥6.5 AND Lịch sử≥6.5 | 60 | 2 | Cần rèn luyện lập luận |
| **Luat_Not_Fit** | Văn<6 OR Lịch sử<5.5 | 15 | 1 | Thiếu kỹ năng lập luận |

#### Du Lịch - Khách Sạn (index=7)

| Luật | Điều kiện | Score | Spec | Reason |
|------|----------|-------|------|--------|
| **DuLich_Very_Fit** | Anh≥8 AND Địa≥7.5 AND Văn≥8 | 88 | 3 | Anh, Địa, Văn xuất sắc |
| **DuLich_Fit** | Anh≥7.5 AND Địa≥7 AND Toán≥5.5 | 78 | 3 | Giao tiếp quốc tế, có tính toán |
| **DuLich_Medium** | Anh≥6.5 AND Địa≥6.5 AND Văn≥6 | 68 | 3 | Có khả năng, Văn khá |
| **DuLich_Not_Fit** | Anh<6.5 OR Địa<5.5 | 15 | 1 | Yếu giao tiếp |

### DEFAULT Rule

Khi **không có luật nào khớp** → trả về `score=30`, `rule_name='DEFAULT'`.

---

## Chi Tiết Conflict Resolution (Giải Quyết Xung Đột)

### Khi Nào Xảy Ra?

Khi nhiều luật cùng thỏa mãn điều kiện cho **một ngành**. Ví dụ với IT, học sinh có Toán=9, Tin=9.5, Lý=8, Anh=8:

```
Luật khớp:
├─ IT_Very_Fit: Toán(9)≥8 ✓  Tin(9.5)≥8 ✓  Lý(8)≥7 ✓   → 95% (spec=3)
├─ IT_Fit:      Toán(9)≥7 ✓  Tin(9.5)≥7 ✓  Lý(8)≥6 ✓  Anh(8)≥5 ✓ → 80% (spec=4)
└─ IT_Medium:   Toán(9)≥7 ✓  Tin(9.5)≥6.5 ✓  → 65% (spec=2)
```

→ 3 luật cùng khớp! Cần chọn 1.

### Thuật Toán Giải Quyết

```python
# resolve_conflicts() trong knowledge_rules.py
sorted_rules = sorted(
    matched_rules,
    key=lambda r: (r['specificity'], r['score']),  # tuple sort
    reverse=True  # giảm dần
)
return sorted_rules[0]  # Chọn luật đầu tiên
```

**Thứ tự ưu tiên:**
1. **Specificity** (số điều kiện) — ưu tiên cao nhất
2. **Score** (điểm số) — phá hòa khi specificity bằng nhau
3. **Position** (thứ tự định nghĩa) — fallback cuối cùng

### Ví Dụ Phân Tích

```
Sắp xếp theo (specificity, score) giảm dần:
├─ IT_Fit:       (4, 80) ← THẮNG (spec=4 cao nhất)
├─ IT_Very_Fit:  (3, 95)
└─ IT_Medium:    (2, 65)

Kết quả: IT_Fit được chọn → base_score = 80
```

**Tại sao ưu tiên specificity?**
- Luật có **nhiều điều kiện hơn** = mô tả **chính xác hơn** về học sinh
- IT_Fit (4 ĐK: Toán+Tin+Lý+Anh) mô tả cụ thể hơn IT_Very_Fit (3 ĐK: Toán+Tin+Lý)
- Luật cụ thể hơn luôn đáng tin hơn luật chung

### Trường Hợp Đặc Biệt

| Tình huống | Xử lý |
|-----------|-------|
| 0 luật khớp | Trả DEFAULT (score=30) |
| 1 luật khớp | Chọn luật đó (không cần resolution) |
| 2+ luật, spec khác | Chọn spec cao nhất |
| 2+ luật, spec bằng | Chọn score cao nhất |
| 2+ luật, spec+score bằng | Chọn luật được định nghĩa trước (stable sort) |

---

## Chi Tiết Forward Chaining (Suy Luận Chuỗi)

### Nguyên Lý

Forward chaining = **suy luận tiến**: từ luật cơ sở đã khớp → kiểm tra thêm điều kiện → cộng bonus.

```
NẾU (luật_cơ_sở đã khớp) VÀ (điều_kiện_bổ_sung thỏa) → base_score + bonus
```

### 10 Luật Forward Chaining

| # | Ngành | Tên Chain | Requires | Điều kiện thêm | Bonus | Lý do |
|---|-------|-----------|------------------------|----------------|-------|-------|
| 1 | IT | IT_Quoc_Te | IT_Very_Fit hoặc IT_Fit | Anh ≥ 7 | +3 | Phù hợp IT Quốc tế |
| 2 | IT | IT_TinSinhHoc | IT_Very_Fit hoặc IT_Fit | Sinh ≥ 7 | +2 | Tiềm năng Tin Sinh học |
| 3 | Kinh tế | KinhTe_So | KinhTe_Very_Fit hoặc KinhTe_Fit | Tin ≥ 6 | +3 | Kinh tế số |
| 4 | Y khoa | YKhoa_QuocTe | YKhoa_Very_Fit hoặc YKhoa_Fit | Anh ≥ 7.5 | +3 | Y khoa Quốc tế |
| 5 | Y khoa | YKhoa_NghienCuu | YKhoa_Very_Fit | Toán ≥ 7.5 | +2 | Nghiên cứu Y học |
| 6 | Kỹ thuật | KyThuat_CongNghe | KyThuat_Very_Fit hoặc KyThuat_Fit | Tin ≥ 7 | +3 | Kỹ thuật Công nghệ |
| 7 | Nông-Lâm-Ngư | NongLam_CongNghe | NongLamNgu_Very_Fit hoặc NongLamNgu_Fit | Tin ≥ 6 | +2 | Nông nghiệp công nghệ cao |
| 8 | Sư phạm | SuPham_QuocTe | SuPham_Very_Fit | Anh ≥ 8 | +3 | Giáo dục Quốc tế |
| 9 | Luật | Luat_QuocTe | Luat_Very_Fit hoặc Luat_Fit | Anh ≥ 7.5 | +3 | Luật Quốc tế |
| 10 | Du lịch | DuLich_QuocTe | DuLich_Very_Fit hoặc DuLich_Fit | Anh ≥ 8 AND Địa ≥ 8 | +3 | Du lịch Quốc tế |

### Thuật Toán

```python
# forward_chain() trong knowledge_rules.py
bonus_total = 0
for chain in chaining_rules[major_index]:
    if base_rule_name in chain['requires']:     # Luật cơ sở đã khớp?
        if chain['condition'](user_scores):      # Điều kiện thêm thỏa?
            bonus_total += chain['bonus']        # Cộng bonus

final_score = min(100, base_score + bonus_total)  # Cap tối đa 100
```

### Ví Dụ Đầy Đủ: IT với Anh tốt

```
Đầu vào: Toán=9, Lý=8, Tin=9.5, Anh=8, Sinh=4

Bước 1 - Rule Matching:
├─ IT_Very_Fit: Toán(9)≥8 ✓ Tin(9.5)≥8 ✓ Lý(8)≥7 ✓  → khớp (95, spec=3)
├─ IT_Fit:      Toán(9)≥7 ✓ Tin(9.5)≥7 ✓ Lý(8)≥6 ✓ Anh(8)≥5 ✓  → khớp (80, spec=4)
└─ IT_Medium:   Toán(9)≥7 ✓ Tin(9.5)≥6.5 ✓  → khớp (65, spec=2)

Bước 2 - Conflict Resolution:
└─ IT_Fit thắng (spec=4 > spec=3 > spec=2)
   → base_score = 80, base_rule = "IT_Fit"

Bước 3 - Forward Chaining:
├─ IT_Quoc_Te: requires=[IT_Very_Fit, IT_Fit] → IT_Fit ∈ requires ✓
│              condition: Anh(8) ≥ 7 ✓ → bonus +3
├─ IT_TinSinhHoc: requires=[IT_Very_Fit, IT_Fit] → IT_Fit ∈ requires ✓
│                 condition: Sinh(4) ≥ 7 ✗ → không áp dụng
└─ bonus_total = 3

Bước 4 - Tính điểm cuối:
└─ KBS_Score = min(100, 80 + 3) = 83%

Đầu ra:
├─ score: 83
├─ rule_name: "IT_Fit"
├─ reason: "Đáp ứng cơ bản, có teamwork | Suy luận chuỗi: Phù hợp IT Quốc tế (Anh tốt)"
├─ chain_applied: true
└─ chain_details: [{chain_name: "IT_Quoc_Te", bonus: 3, reason: "Phù hợp IT Quốc tế (Anh tốt)"}]
```

### Đặc Điểm Quan Trọng

| Đặc điểm | Chi tiết |
|----------|---------|
| **Nhiều chain cùng áp dụng** | Có thể cộng nhiều bonus (ví dụ IT: +3 Quốc tế + 2 Tin Sinh = +5) |
| **Cap 100** | `min(100, base + bonus)` — không vượt 100% |
| **Chỉ áp dụng cho luật cao** | `requires` thường là `Very_Fit` hoặc `Fit` — không áp dụng cho `Medium`/`Not_Fit` |
| **Thêm giá trị, không thay thế** | Chain không thay đổi luật cơ sở, chỉ cộng thêm |

### Quy Trình Evaluate Hoàn Chỉnh

```
evaluate(user_scores, major_index)
│
├─ 1. Duyệt 4 luật → tìm tất cả luật khớp (matched_rules)
│
├─ 2. Conflict Resolution:
│     └─ sort by (specificity DESC, score DESC) → chọn top 1
│
├─ 3. Forward Chaining:
│     └─ duyệt chaining_rules → cộng bonus nếu match
│
└─ 4. Return: {score, rule_name, description, reason, chain_details}
```

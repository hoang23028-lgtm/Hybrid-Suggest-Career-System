# Hướng Dẫn AI Chi Tiết - Hybrid KBS+ML System 

---

## 1. Tổng Quan Kiến Trúc

### 1.1 Sơ Đồ Hệ Thống

```
┌─────────────────────────────────────────────────────────┐
│                   STREAMLIT APP (app.py)                │
│         [Chọn Khối] → [Nhập 6 Điểm] → [Xem Kết Quả]   │
└─────────┬─────────────────────────────────────────────┘
          │
     [Input: 6 điểm]
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│              HYBRID FUSION ENGINE (`kbs/hybrid_fusion.py`)    │
│  ┌──────────────────┬─────────────────────────────┐     │
│  │  ML BRANCH       │   KBS BRANCH                │     │
│  │                  │                             │     │
│  │  Random Forest   │  JSON Rules                 │     │
│  │  rf_model_*.pkl  │  (rules_config.json)        │     │
│  │  predict_proba() │  KnowledgeRuleEngine        │     │
│  │  → [0.15, ...]   │  → [95, 75, 85, ...]        │     │
│  │  temp=0.75       │  + Conflict Resolution      │     │
│  │  → 0-100% score  │  + Specificity              │     │
│  │                  │                             │     │
│  │  Score ML: 65%   │  Score KBS: 80%             │     │
│  └────────┬─────────┴────────────┬────────────────┘     │
│           │                      │                       │
│           └──────────┬───────────┘                       │
│                      │                                   │
│            Fusion: 0.6×ML + 0.4×KBS                     │
│            = 0.6×65 + 0.4×80 = 71%                     │
│                      │                                   │
└──────────────────────┼──────────────────────────────────┘
                       │
                  [Output: Ranking + Explanation]
```

### 1.2 Kiến Trúc 2 Khối

```
                 Input (6 Điểm)
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
    KHTN Block               KHXH Block
    (5 Ngành)               (4 Ngành)
    Môn: Toan,Van,Anh       Môn: Toan,Van,Anh
         Ly,Hoa,Sinh            Lich Su,Dia Ly,GDCD
    
    Model: models/rf_model_khtn   Model: models/rf_model_khxh
    Rules: KHTN in JSON    Rules: KHXH in JSON
    
    Output: 5 Scores       Output: 4 Scores
    (IT, KT, Y, KT, NLN)  (KT, SP, LP, DL)
```

---

## 2. Pipeline Chi Tiết

### 2.1 Bước 1: Data Preprocessing (Streamlit App)

**Input:** Người dùng chọn khối + nhập 6 điểm

```python
# app.py (rút gọn)
from config import get_features, get_display_names  # (shim) → kbs/config.py

# UI: "KHTN" / "KHXH" → nội bộ dùng 'khtn' / 'khxh'
block = "khtn" if st.session_state.selected_block_label == "KHTN" else "khxh"
feature_names = get_features(block)
display_map = get_display_names(block)
user_scores = [st.slider(display_map.get(f, f), 0.0, 10.0, ...) for f in feature_names]
```

**Output:** `score_array = [8.5, 7.0, 6.5, 7.5, 6.0, 7.0]`

### 2.2 Bước 2: ML Branch (Random Forest)

**Input:** score_array (6 điểm)

```python
# kbs/hybrid_fusion.py → calculate_ml_score()

from hybrid_fusion import load_ml_model  # (shim) → kbs/hybrid_fusion.py

model = load_ml_model(block)

# predict_proba trên 1 hàng DataFrame đúng tên cột get_features(block)
probs = model.predict_proba(X_df)[0]
classes = list(model.classes_)  # chỉ nhãn ngành của khối đó
class_pos = classes.index(major_index)

# Temperature T=0.75: p' ∝ p^(1/T), chuẩn hóa lại
adjusted = np.power(probs, 1.0 / 0.75)
adjusted = adjusted / adjusted.sum()
scaled_prob = adjusted[class_pos]

# Baseline 1/n_classes; điểm ML 0–100 cho từng ngành (major_index)
baseline = 1.0 / len(classes)
ml_score = 0.0 if scaled_prob <= baseline else ((scaled_prob - baseline) / (1 - baseline)) * 100.0
```

**Công thức chi tiết:**

$$\text{ML\_Score}_i = \text{clip}\left(\frac{\text{proba}_i - \frac{1}{n}}{\frac{n-1}{n}} \times 100, 0, 100\right)$$

### 2.3 Bước 3: KBS Branch (Knowledge Rules)

**Input:** score_array (6 điểm)

```python
# kbs/knowledge_rules.py → KnowledgeRuleEngine.evaluate()

from knowledge_rules import KnowledgeRuleEngine  # (shim) → kbs/knowledge_rules.py
from config import get_majors

engine = KnowledgeRuleEngine(block="khtn")  # hoặc "khxh"
user_scores = [8.5, 7.0, 6.5, 7.5, 6.0, 7.0]  # đúng thứ tự get_features(block)

for major_index in get_majors("khtn"):
    r = engine.evaluate(user_scores, major_index)
    # r: score, rule_name, reason, relevance_score, chain_applied, chain_details, ...
```

### 2.4 Bước 4: Hybrid Fusion

**Input:** ml_scores (5 điểm), kbs_scores (5 điểm)

```python
# kbs/hybrid_fusion.py → calculate_hybrid_score() (mỗi ngành)
# Mặc định: hybrid = 0.6 * ml + 0.4 * kbs
# Nếu VETO: trọng số chuyển về ~0.15 ML + 0.85 KBS (xem check_kbs_veto)
hybrid_scores = 0.6 * ml_scores + 0.4 * kbs_scores

# Ví dụ:
# IT: 0.6 * 15 + 0.4 * 95 = 9 + 38 = 47%
# KT: 0.6 * 42 + 0.4 * 75 = 25.2 + 30 = 55.2%
# Y:  0.6 * 35 + 0.4 * 85 = 21 + 34 = 55%
# KyThuat: 0.6 * 25 + 0.4 * 80 = 15 + 32 = 47%
# NLN: 0.6 * 10 + 0.4 * 60 = 6 + 24 = 30%

# Sort & Rank
ranking = sorted(zip(major_names, hybrid_scores), 
                 key=lambda x: x[1], reverse=True)
# Output:
# 1. Kinh tế: 55.2%
# 2. Y khoa: 55%
# 3. IT: 47%
# 4. Kỹ thuật: 47%
# 5. Nông-Lâm: 30%
```

### 2.5 Bước 5: Explanation Generation

**Input:** score_array, ml_scores, kbs_scores, hybrid_scores

```python
# hybrid_fusion.py → _create_explanation()

explanation = {
    'top_major': 'Kinh tế',
    'top_score': 55.2,
    'ml_score': 42,
    'kbs_score': 75,
    'reasoning': {
        'ml': '42% từ ML: điểm Anh (7.0) tương đối, Toán (8.5) cao, Văn (7.0) cân bằng',
        'kbs': '75% từ KBS: Anh≥7, Toán≥6.5, Văn≥6.5 → Fit rule',
        'hybrid': 'Kết hợp: 60% ML (42) + 40% KBS (75) = 55.2%',
        'recommendation': 'Kinh tế là lựa chọn tốt. Cân nhắc Y khoa (55%) vì Sinh cao'
    }
}
```

---

## 3. Cơ Chế Thêm: VETO

### 3.1 Định Nghĩa VETO

KBS có quyền **phủ quyết** (veto) kết quả ML khi phát hiện bất hợp lý rõ ràng.

```python
# hybrid_fusion.py → VETO_CONFIG

VETO_KBS_NOT_FIT_THRESHOLD = 20      # KBS ≤ 20 → "Không phù hợp"
VETO_ML_HIGH_THRESHOLD = 60          # ML > 60 trong khi KBS ≤ 20 → bất hợp lý
VETO_KEY_SUBJECT_MIN = 4.0           # Môn chính < 4.0 → veto cứng
VETO_KBS_DOMINANT_WEIGHT = 0.85      # Khi veto: 85% KBS, 15% ML
```

### 3.2 Ví Dụ VETO

Môn **trọng tâm** để kiểm tra ngưỡng 4.0 được lấy theo khối và ngành trong `KnowledgeRuleEngine` (`KHTN_KEY_SUBJECTS` / `KHXH_KEY_SUBJECTS`).

```
Học sinh: Toán=3.5, Văn=8, Anh=8, Ly=2, Hóa=1.5, Sinh=2
Khối: KHTN

ML có thể vẫn cho xác suất cao ở một số ngành; KBS có thể trả Not_Fit (điểm thấp).

→ Nếu KBS ≤ 20, ML > 60 và có môn trọng tâm < 4.0 → VETO kích hoạt
→ Hybrid ≈ 0.15 × ML + 0.85 × KBS (thay vì 60/40)
```

---

## 4. Chi Tiết ML Model

### 4.1 Random Forest Config

```python
# config.py
RF_PARAMS = {
    'n_estimators': 100,        # 100 cây
    'max_depth': 15,            # Độ sâu tối đa
    'min_samples_split': 10,    # Tối thiểu split
    'min_samples_leaf': 5,      # Tối thiểu leaf
    'random_state': 42,         # Reproducible
    'n_jobs': -1,               # Parallel
}
```

### 4.2 Training Pipeline

```python
# scripts/train_model.py

# [1] Load data
data = pd.read_csv(get_data_path(block))
X = data[get_features(block)]  # 6 features
y = data["nganh_hoc"]          # nhãn ngành (theo NGANH_HOC_MAP)

# [2] Split 80/20
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# [3] Cross-validation 5-fold
from sklearn.model_selection import cross_val_score
scores = cross_val_score(rf, X_train, y_train, cv=5)
print(f"CV Accuracy: {scores.mean():.4f} +/- {scores.std():.4f}")

# [4] Train model
rf = RandomForestClassifier(**RF_PARAMS)
rf.fit(X_train, y_train)

# [5] Evaluate
y_pred = rf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Test Accuracy: {accuracy:.4f}")

# [6] Save model
pickle.dump(rf, open(get_model_path(block), 'wb'))
```

### 4.3 Feature Importance

```python
# experiments.py

# Sau khi train
importances = rf.feature_importances_
feature_names = get_features(block)

# Rank
ranked = sorted(zip(feature_names, importances), 
                key=lambda x: x[1], reverse=True)

# Output KHTN:
# 1. toan: 0.28
# 2. ly: 0.22
# 3. sinh: 0.18
# 4. hoa: 0.15
# 5. van: 0.12
# 6. anh: 0.05
```

---

## 5. Chi Tiết KBS Engine

### 5.1 Load Rules từ JSON

```python
# knowledge_rules.py

def _load_rules_config():
    """Load luật từ rules_config.json"""
    config_path = Path(__file__).parent / 'rules_config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load
rules_json = _load_rules_config()

# Khởi tạo lại
def _build_condition(thresholds, operator, feature_index):
    """JSON → lambda condition"""
    checks = []
    for feat_name, threshold in thresholds.items():
        idx = feature_index[feat_name]
        checks.append((idx, threshold))
    
    if operator == 'AND':
        return lambda s, _checks=checks: all(s[i] >= t for i, t in _checks)
    elif operator == 'OR_LESS_THAN':
        return lambda s, _checks=checks: any(s[i] < t for i, t in _checks)
```

### 5.2 Conflict Resolution

Trong `KnowledgeRuleEngine.resolve_conflicts()`, luật thắng là luật có **specificity** cao nhất, nếu hòa thì **score** cao hơn (dict từ JSON, có trường `condition` đã biên dịch).

---

## 6. Output Format

### 6.1 Kết quả `get_hybrid_ranking`

Hàm trả về **list** các dict (đã gán `rank` sau khi sort):

```python
[
  {
    "rank": 1,
    "major": "Kinh tế",
    "hybrid_score": 55.2,
    "ml_score": 42.0,
    "kbs_score": 75.0,
    "relevance_score": 7.2,
    "explanation": "..."  # chuỗi tiếng Việt, có thể ghi VETO
  },
  ...
]
```

Chi tiết veto / trọng số nằm trong từng lần gọi `calculate_hybrid_score` (trường `vetoed`, `ml_weight`, `kbs_weight` trong dict trả về).

### 6.2 Streamlit Display

```python
# app.py
st.metric("Ngành Gợi Ý", "Kinh tế", "55.2%")

# Expander: Chi tiết điểm
with st.expander("Xem chi tiết"):
    col1, col2 = st.columns(2)
    with col1:
        st.write("**ML Score:** 42%")
        st.write("Dựa trên: Random Forest 100 cây")
    with col2:
        st.write("**KBS Score:** 75%")
        st.write("Rule: KinhTe_Fit")

# Bar chart: Ranking
fig, ax = plt.subplots()
ax.barh(major_names, hybrid_scores)
st.pyplot(fig)
```

---

## 7. Error Handling & Logging

### 7.1 Chuẩn hóa đầu vào

`hybrid_fusion.normalize_scores()` **clip** từng điểm về `[0, 10]` (không chia 10). Độ dài list phải khớp `len(get_features(block))`; nếu sai, `calculate_ml_score` ném `ValueError`.

### 7.2 Logging

```python
# hybrid_fusion.py
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Log prediction
logger.info(f"Block: {block}, Scores: {score_array}, "
            f"Result: {major_name} ({hybrid_score:.1f}%)")

# Log error
logger.error(f"ML model not found: {model_path}")
```

---

## 8. Performance Monitoring

### 8.1 Metrics

```python
# monitoring.py

def log_prediction(user_scores, result, timestamp):
    """Log mỗi dự đoán"""
    # Lưu vào database/file
    # Fields: timestamp, scores, predicted_major, score, confidence
    pass

def calculate_satisfaction(actual_major, predicted_major):
    """
    Sau 1-2 năm, hỏi học sinh:
    "Bạn chọn ngành gì? Hài lòng không?"
    → Tính accuracy thực tế
    """
    pass
```

### 8.2 Metrics Theo Dõi

| Metric | Công Thức | Mục Tiêu |
|--------|-----------|---------|
| Accuracy | Predictions đúng / Tổng | ≥ 70% |
| Top-2 Accuracy | Ngành đúng trong top 2 | ≥ 85% |
| Confidence (ML) | Mean predict_proba | ≥ 60% |
| Confidence (KBS) | Mean rule score | ≥ 70% |
| User Satisfaction | Hỏi sau 1-2 năm | ≥ 75% |

---

## 9. Tệp Liên Quan & Responsibilities

| Tệp | Chức Năng |
|-----|----------|
| `app.py` | UI: Input + Output |
| `hybrid_fusion.py` | Engine: ML + KBS + Fusion + VETO |
| `knowledge_rules.py` | KBS: JSON → Predict |
| `scripts/train_model.py` | ML: Training pipeline |
| `config.py` | Settings, paths, features |
| `rules_config.json` | KBS rules (20+ luật) |
| `models/rf_model_khtn.pkl` | ML model (KHTN) |
| `models/rf_model_khxh.pkl` | ML model (KHXH) |
| `monitoring.py` | Logging & Performance |
| `experiments.py` | Testing & Tuning |

---

**Cập nhật:** 30/04/2026  
**Phiên bản:** 3.0  
**Tác giả:** Hybrid KBS-ML Team

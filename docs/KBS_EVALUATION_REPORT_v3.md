# Báo Cáo Đánh Giá Hệ Thống


---

## I. Tóm Tắt Đánh Giá

### Điểm Chung

| Tiêu Chí | Điểm | Ghi Chú |
|----------|------|--------|
| Kiến Trúc | 8.5/10 | Tách biệt rõ KHTN/KHXH, JSON-based |
| Dữ Liệu | 8/10 | THPT 2024; cỡ mẫu sau `scripts/create_data.py` phụ thuộc CSV (và pipeline tạo dữ liệu) |
| ML Model | 7.5/10 | Random Forest ổn định, chưa optimize |
| KBS Engine | 8.5/10 | Conflict resolution tốt, JSON-based dễ maintain |
| Hybrid Fusion | 8/10 | 70/30 ML–KBS (tuned `scripts/tune_weights.py`), VETO (`kbs/config.py` + `scripts/tune_veto.py`) |
| Deployment | 8/10 | Streamlit app sạch, UX tốt |
| Documentation | 8.5/10 | Tài liệu v3.0 chi tiết |
| **Điểm Chung** | **8.1/10** | **Hệ thống sản xuất ready** |

### Kết Luận


- Thêm monitoring & logging
- Validate rules với chuyên gia
- Plan A/B testing với thực tế
- Set up CI/CD pipeline

---

## II. Đánh Giá Chi Tiết

### A. Kiến Trúc & Thiết Kế —
**Điểm mạnh:**
- ✓ Kiến trúc 2 khối phản ánh cấu trúc thi tuyển thực tế THPT
- ✓ Tách rõ ML branch (data-driven) vs KBS branch (rule-based)
- ✓ JSON-based rules dễ cập nhật không cần code
- ✓ VETO mechanism bảo vệ output không hợp lý
- ✓ Feature lựa chọn phù hợp (6 môn per khối)
- ✓ Fallback to KBS nếu ML model lỗi
- ✓ Logging & monitoring framework sẵn sàng

**Điểm cần cải thiện:**
- ⚠ Chưa có database centralized (logging, predictions)
- ✓ `hybrid_fusion` cache model và `KnowledgeRuleEngine` theo khối (singleton đơn giản)
- ⚠ Một phần cấu hình vẫn trong Python (`kbs/config.py`); VETO đã tập trung tại đây, có script `scripts/tune_veto.py` hỗ trợ quét lưới
- ⚠ Batch inference chưa hỗ trợ (chỉ single input)

**Khuyến nghị:** batch inference có thể gom `predict_proba` trên ma trận `X` nếu sau này cần API hàng loạt (hiện Streamlit xử lý từng phiên).

---

### B. Dữ Liệu 

**Điểm mạnh:**
- ✓ Dữ liệu thực tế từ THPT 2024
- ✓ 2 khối độc lập, 6 features per khối hợp lý
- ✓ Phạm vi [0-10] chuẩn THPT
- ✓ Cấu trúc sạch (phạm vi, tên cột chuẩn)

**Điểm cần cải thiện:**
- ⚠ Chỉ 6 điểm môn (không có sở thích, năng lực khác)
- ⚠ Dữ liệu một năm (mở rộng khi có thêm file các năm)
- ⚠ Chưa validate với dữ liệu từ các nguồn khác

**Khuyến nghị:** chuẩn hóa pipeline ingest nhiều năm; phân tích phân bố và drift sau khi gom dữ liệu.

---

### C. Machine Learning

**Điểm mạnh:**
- ✓ Random Forest model ổn định
- ✓ Cross-validation 5-fold để tránh overfitting
- ✓ Temperature scaling (T=0.75) tối ưu
- ✓ Feature importance analysis
- ✓ Stratified split giữ tỉ lệ class

**Điểm cần cải thiện:**
- ⚠ Chỉ thử RF, chưa so sánh XGBoost/LightGBM/Neural Network
- ⚠ Hyperparameter không tune (hardcoded max_depth=15)
- ⚠ Model size ~178MB → có thể optimize
- ⚠ Baseline subtraction (1/n_classes) là hardcoded
- ⚠ Không có learning curve → không biết data đủ chưa
- ⚠ Accuracy thực tế chưa được validate (chỉ có THPT 2024)

**Khuyến nghị:**
```python
# Hyperparameter tuning
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [50, 100, 150],
    'max_depth': [10, 15, 20],
    'min_samples_split': [5, 10, 15],
}

grid_search = GridSearchCV(rf, param_grid, cv=5)
grid_search.fit(X_train, y_train)
print(f"Best params: {grid_search.best_params_}")

# So sánh models
models = {
    'RF': RandomForestClassifier(n_estimators=100),
    'XGB': XGBClassifier(n_estimators=100),
    'LightGBM': LGBMClassifier(n_estimators=100),
}

results = {}
for name, model in models.items():
    scores = cross_val_score(model, X_train, y_train, cv=5)
    results[name] = scores.mean()

print(results)  # So sánh accuracy
```

---

### D. Knowledge-Based System

**Điểm mạnh:**
- ✓ 32 luật/khối (JSON) hợp lý
- ✓ Conflict resolution rõ ràng (specificity + score)
- ✓ Rules dễ cập nhật không cần code
- ✓ Tie-breaking logic tự động
- ✓ Giải thích đầy đủ bằng Tiếng Việt

**Điểm cần cải thiện:**
- ⚠ Luật chưa được validate bởi giáo viên
- ⚠ Thresholds dựa trên cảm tính (Toan ≥ 8 = sự quyết định)
- ✓ **Forward chaining** (`chaining_rules` + `forward_chain`) và **`reasoning_chain`** trong KBS engine; cần tiếp tục validate nội dung luật với chuyên gia
- ⚠ Không có soft thresholds (fuzzy logic)
- ⚠ Không có dynamic thresholds (theo năm)

**Khuyến nghị:**
```json
{
  "validation_status": "pending",
  "validated_by": [],
  "validation_date": null,
  "feedback": []
}

// Thêm vào mỗi rule để track validation
```

```bash
# Workshop với 15 giáo viên (3 ngành × 5 người)
# Hỏi: "Thresholds này hợp lý không?"
# Collect feedback → cập nhật rules

python collect_expert_feedback.py
```

---

### E. Hybrid Fusion

**Điểm mạnh:**
- ✓ Weights **70/30** (mặc định `kbs/hybrid_fusion.py`, tuned bằng `scripts/tune_weights.py` trên 2000 mẫu test); legacy `scripts/legacy/experiments.py` có thử nhiều tỷ lệ
- ✓ VETO mechanism bảo vệ output rõ ràng
- ✓ Fallback to KBS khi ML fail
- ✓ Chuẩn hoá điểm môn clip [0, 10] trước khi đưa vào ML/KBS
- ✓ Explanation chi tiết

**Điểm cần cải thiện:**
- ⚠ Weights cố định 70/30 → có thể dynamic theo confidence (chưa triển khai)
- ⚠ Chưa có A/B testing thực tế người dùng (70/30 vs tỷ lệ khác)
- ⚠ Ranking có tie (VD: 55.2% và 55.0%) → tie-breaking cần rõ ràng

**Khuyến nghị:**
```python
# Dynamic weights dựa trên ML confidence
def get_adaptive_weights(ml_confidence: float) -> tuple:
    """
    Nếu ML confident cao → gia tăng ML weight
    Nếu ML không confident → gia tăng KBS weight
    """
    if ml_confidence > 0.8:
        return (0.7, 0.3)  # 70% ML, 30% KBS
    elif ml_confidence > 0.6:
        return (0.5, 0.5)  # 50% ML, 50% KBS
    else:
        return (0.4, 0.6)  # 40% ML, 60% KBS

# A/B test (gợi ý)
def ab_test(weights: tuple, test_data: pd.DataFrame):
    """So sánh 50/50 vs dynamic weights trên test data"""
    pass
```

---

### F. Deployment & UX

**Điểm mạnh:**
- ✓ Streamlit app sạch, dễ sử dụng
- ✓ Hai tab: **Kết quả chính**, **Phân tích chi tiết** (tập trung ngành đề xuất)
- ✓ Slider input intuitive
- ✓ Radar điểm môn (Plotly) trong tab phân tích chi tiết
- ✓ Error handling tốt

**Điểm cần cải thiện:**
- ⚠ Không có session management (user history)
- ⚠ Không có export kết quả (PDF/CSV)
- ⚠ Không có compare nhiều scenarios
- ⚠ Không có multi-language (chỉ Tiếng Việt)
- ⚠ Mobile responsive chưa được test

**Khuyến nghị:**
```python
# Session management
import streamlit as st

if 'predictions' not in st.session_state:
    st.session_state.predictions = []

# Save kết quả
def export_to_pdf():
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.cell(0, 10, "Kết Quả Gợi Ý Ngành Học", ln=True)
    # ... thêm nội dung
    pdf.output("result.pdf")
```

---

### G. Documentation 

**Điểm mạnh:**
- ✓ 5 file .md v3.0 chi tiết
- ✓ README.md cập nhật phiên bản
- ✓ `DATASET_v3.md` giải thích dữ liệu rõ
- ✓ `KNOWLEDGE_BASED_RULES_v3.md` mô tả JSON rules
- ✓ `KBS_AI_DETAIL_v3.md` pipeline chi tiết
- ✓ Docstring trong code

**Điểm cần cải thiện:**
- ⚠ Chưa có API documentation (OpenAPI/Swagger)
- ✓ README có mục khắc phục sự cố; có thể thêm runbook vận hành
- ⚠ Chưa có deployment instructions (Docker, cloud)
- ⚠ Chưa có architecture diagram (mermaid/plantuml)

**Khuyến nghị:**
```bash
# Thêm API docs
pip install fastapi uvicorn

# Tạo FastAPI wrapper
from fastapi import FastAPI

app = FastAPI(title="Hybrid KBS-ML API", version="3.0")

@app.post("/rank")
def rank(block: str, scores: List[float]):
    """Ví dụ: gọi get_hybrid_ranking từ hybrid_fusion"""
    from hybrid_fusion import get_hybrid_ranking, load_ml_model

    model = load_ml_model(block)
    return get_hybrid_ranking(scores, block=block, model=model)

# Docs tự động tại /docs
```

---

## III. Scoring Chi Tiết

| Thành Phần | Sub-tiêu chí | Điểm | Ghi Chú |
|-----------|-------------|------|--------|
| **Kiến Trúc** | Tách biệt rõ | 9/10 | 2 khối, JSON-based |
| | VETO mechanism | 8/10 | Tốt; tham số trong `kbs/config.py`, có `tune_veto.py` |
| | Error handling | 8/10 | Cơ bản nhưng đủ |
| **Dữ Liệu** | Kích thước | 7/10 | Phụ thuộc CSV; sau cân bằng theo khối |
| | Chất lượng | 8/10 | Thực tế THPT 2024 |
| | Features | 8/10 | 6 môn hợp lý |
| **ML** | Accuracy | 7/10 | Chưa know thực tế |
| | Model diversity | 6/10 | Chỉ RF, không XGB |
| | Hyperparameter | 6/10 | Hardcoded, không tune |
| | Feature analysis | 8/10 | Có feature importance |
| **KBS** | Luật | 8/10 | ~20/khối, JSON-based |
| | Conflict res | 9/10 | Specificity + score tốt |
| | Validation | 7/10 | Chưa expert review |
| | Giải thích | 9/10 | Chi tiết bằng Tiếng Việt |
| **Fusion** | Logic | 8/10 | 70/30 weights (tuned) + VETO hợp lý |
| | VETO | 8/10 | Bảo vệ output rõ ràng |
| **Deployment** | UX | 8/10 | Streamlit sạch |
| | Scalability | 7/10 | Single-instance, không cluster |
| | Monitoring | 7/10 | Basic logging |
| **Doc** | Completeness | 8/10 | v3.0 chi tiết |
| | Clarity | 9/10 | Tiếng Việt rõ ràng |

---

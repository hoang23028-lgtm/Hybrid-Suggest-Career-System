# Báo Cáo Đánh Giá Hệ Thống v3.0

**Ngày đánh giá:** 29/04/2026  
**Phiên bản:** 3.0 (Kiến Trúc 2 Khối KHTN/KHXH, JSON-based Rules)  
**Loại dự án:** Hybrid KBS + ML System

---

## I. Tóm Tắt Đánh Giá

### Điểm Chung

| Tiêu Chí | Điểm | Ghi Chú |
|----------|------|--------|
| Kiến Trúc | 8.5/10 | Tách biệt rõ KHTN/KHXH, JSON-based |
| Dữ Liệu | 8/10 | Dữ liệu thực tế THPT 2024, nhưng cỡ mẫu nhỏ |
| ML Model | 7.5/10 | Random Forest ổn định, chưa optimize |
| KBS Engine | 8.5/10 | Conflict resolution tốt, JSON-based dễ maintain |
| Hybrid Fusion | 8/10 | 60/40 weights, VETO mechanism |
| Deployment | 8/10 | Streamlit app sạch, UX tốt |
| Documentation | 8.5/10 | Tài liệu v3.0 chi tiết |
| **Điểm Chung** | **8.1/10** | **Hệ thống sản xuất ready** |

### Kết Luận

✅ **Sản Xuất Ready** với điều kiện:
- Thêm monitoring & logging
- Validate rules với chuyên gia
- Plan A/B testing với thực tế
- Set up CI/CD pipeline

---

## II. Đánh Giá Chi Tiết

### A. Kiến Trúc & Thiết Kế — ⭐ 8.5/10

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
- ⚠ Chưa có caching ML model (mỗi lần load pickle từ disk)
- ⚠ Config hard-coded trong Python, nên move vào `config.json`
- ⚠ Batch inference chưa hỗ trợ (chỉ single input)

**Khuyến nghị:**
```python
# Thêm caching
from functools import lru_cache

@lru_cache(maxsize=2)
def load_model(block: str):
    return pickle.load(open(get_model_path(block)))

# Batch inference
def predict_batch(scores_list: List[List[float]], block: str):
    """Dự đoán nhiều học sinh một lúc"""
    X = np.array(scores_list)
    return engine.predict(X)
```

---

### B. Dữ Liệu — ⭐ 8/10

**Điểm mạnh:**
- ✓ Dữ liệu thực tế từ THPT 2024
- ✓ 2 khối độc lập, 6 features per khối hợp lý
- ✓ Phạm vi [0-10] chuẩn THPT
- ✓ Cấu trúc sạch (phạm vi, tên cột chuẩn)

**Điểm cần cải thiện:**
- ⚠ Cỡ mẫu nhỏ: ~30K-50K/khối (so với 160K cũ)
- ⚠ Phân bố không đều: Kinh tế >> Nông-Lâm-Ngư
- ⚠ Chỉ 6 features (không có tư duy, kỹ năng, sở thích)
- ⚠ Dữ liệu tĩnh (chỉ 2024, cần cộng dồn multi-year)
- ⚠ Chưa validate với dữ liệu từ các trường khác

**Khuyến nghị:**
```bash
# Cộng dữ liệu 2022, 2023, 2024, 2025
python combine_multi_year_data.py --years 2022 2023 2024 2025

# Phân tích phân bố
python analyze_distribution.py

# Augmentation để cân bằng ngành
python balance_classes.py
```

---

### C. Machine Learning — ⭐ 7.5/10

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

### D. Knowledge-Based System — ⭐ 8.5/10

**Điểm mạnh:**
- ✓ ~20 luật/khối (JSON) hợp lý
- ✓ Conflict resolution rõ ràng (specificity + score)
- ✓ Rules dễ cập nhật không cần code
- ✓ Tie-breaking logic tự động
- ✓ Giải thích đầy đủ bằng Tiếng Việt

**Điểm cần cải thiện:**
- ⚠ Luật chưa được validate bởi 10+ giáo viên
- ⚠ Thresholds dựa trên cảm tính (Toan ≥ 8 = sự quyết định)
- ⚠ Không có Forward Chaining (luật chuỗi bonus)
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

### E. Hybrid Fusion — ⭐ 8/10

**Điểm mạnh:**
- ✓ Weights 60/40 được thử nghiệm (experiments.py)
- ✓ VETO mechanism bảo vệ output rõ ràng
- ✓ Fallback to KBS khi ML fail
- ✓ Normalize scores đúng (clip [0,100])
- ✓ Explanation chi tiết

**Điểm cần cải thiện:**
- ⚠ Weights cố định 60/40 → nên dynamic dựa trên confidence
- ⚠ VETO thresholds hardcoded → nên config
- ⚠ Không có A/B testing (60/40 vs 50/50 vs 70/30)
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
        return (0.6, 0.4)  # 60% ML, 40% KBS
    else:
        return (0.4, 0.6)  # 40% ML, 60% KBS

# A/B test
def ab_test(weights: tuple, test_data: pd.DataFrame):
    """So sánh 60/40 vs dynamic weights trên test data"""
    pass
```

---

### F. Deployment & UX — ⭐ 8/10

**Điểm mạnh:**
- ✓ Streamlit app sạch, dễ sử dụng
- ✓ 3 tabs: Kết quả, Phân tích, So sánh
- ✓ Slider input intuitive
- ✓ Bar chart ranking dễ hiểu
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

### G. Documentation — ⭐ 8.5/10

**Điểm mạnh:**
- ✓ 5 file .md v3.0 chi tiết
- ✓ README.md cập nhật phiên bản
- ✓ DATASET_v3.md giải thích dữ liệu rõ
- ✓ KNOWLEDGE_BASED_RULES_v3.md mô tả JSON rules
- ✓ KBS_AI_DETAIL_v3.md pipeline chi tiết
- ✓ Docstring trong code

**Điểm cần cải thiện:**
- ⚠ Chưa có API documentation (OpenAPI/Swagger)
- ⚠ Chưa có troubleshooting guide
- ⚠ Chưa có deployment instructions (Docker, cloud)
- ⚠ Chưa có architecture diagram (mermaid/plantuml)

**Khuyến nghị:**
```bash
# Thêm API docs
pip install fastapi uvicorn

# Tạo FastAPI wrapper
from fastapi import FastAPI

app = FastAPI(title="Hybrid KBS-ML API", version="3.0")

@app.post("/predict")
def predict(block: str, scores: List[float]):
    """Predict major từ scores"""
    engine = HybridFusionEngine(block=block)
    return engine.predict(scores)

# Docs tự động tại /docs
```

---

## III. Scoring Chi Tiết

| Thành Phần | Sub-tiêu chí | Điểm | Ghi Chú |
|-----------|-------------|------|--------|
| **Kiến Trúc** | Tách biệt rõ | 9/10 | 2 khối, JSON-based |
| | VETO mechanism | 8/10 | Tốt nhưng hardcoded |
| | Error handling | 8/10 | Cơ bản nhưng đủ |
| **Dữ Liệu** | Kích thước | 7/10 | 30-50K nhỏ hơn cũ |
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
| **Fusion** | Logic | 8/10 | 60/40 weights hợp lý |
| | VETO | 8/10 | Bảo vệ output rõ ràng |
| **Deployment** | UX | 8/10 | Streamlit sạch |
| | Scalability | 7/10 | Single-instance, không cluster |
| | Monitoring | 7/10 | Basic logging |
| **Doc** | Completeness | 8/10 | v3.0 chi tiết |
| | Clarity | 9/10 | Tiếng Việt rõ ràng |

---

## IV. Roadmap Cải Thiện

### Phase 1 (4-6 tuần) - MVP Enhancement

- [ ] Hyperparameter tuning (GridSearchCV)
- [ ] So sánh XGBoost vs LightGBM
- [ ] Workshop expert validation (15 giáo viên)
- [ ] Thêm A/B testing framework
- [ ] Setup monitoring dashboard

### Phase 2 (2-3 tháng) - Production Ready

- [ ] Cộng dữ liệu 2022-2025 (multi-year)
- [ ] FastAPI wrapper + OpenAPI docs
- [ ] Database logging (PostgreSQL)
- [ ] Docker containerization
- [ ] CI/CD pipeline (GitHub Actions)

### Phase 3 (3-6 tháng) - Advanced Features

- [ ] Fuzzy logic soft thresholds
- [ ] Forward Chaining rules
- [ ] Dynamic weights (adaptive)
- [ ] Batch inference API
- [ ] Mobile app (React Native)

---

## V. Risk Assessment

| Risk | Xác Suất | Tác Động | Giảm Thiểu |
|------|---------|----------|-----------|
| Dữ liệu cỡ mẫu nhỏ | Cao | Medium | Cộng multi-year data |
| Rules không validate | Cao | High | Workshop 15 experts |
| ML accuracy thực tế ≠ test | Medium | High | A/B test real users |
| VETO threshold sai | Medium | Medium | Feedback loop from users |
| Model drift theo thời gian | Medium | Medium | Retrain quarterly |

---

## VI. Kết Luận & Khuyến Cáo

### ✅ Kết Luận

Hệ thống v3.0 đạt **mức sản xuất ready** (8.1/10) với:
- Kiến trúc hybrid rõ ràng (ML + KBS + Fusion)
- JSON-based rules dễ maintain
- VETO mechanism bảo vệ output
- Documentation tốt v3.0

### ⚠ Điều Kiện Go-Live

1. **Validate Rules:** Workshop 15 giáo viên → sign-off
2. **Test A/B:** Real users (100 học sinh) → 30 ngày
3. **Monitoring:** Setup logging + alert dashboard
4. **Fallback Plan:** Manual review nếu confidence < 50%
5. **SLA:** Target accuracy ≥ 70%, satisfaction ≥ 75%

### 🚀 Ưu Tiên

1. **Ngắn hạn (2 tuần):** Expert validation workshop
2. **Trung hạn (1 tháng):** Hyperparameter tuning + A/B test
3. **Dài hạn (3-6 tháng):** Multi-year data + advanced features

---

**Đánh giá ngày:** 29/04/2026  
**Phiên bản:** 3.0  
**Trạng thái:** ✅ Recommend for Production (with conditions)  
**Reviewer:** Hybrid KBS-ML Team

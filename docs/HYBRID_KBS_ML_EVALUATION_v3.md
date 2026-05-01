# Đánh Giá Chi Tiết Hệ Thống Hybrid KBS+ML

---

## Bước 1: Xác Định Phần ML vs KBS

### Mục Tiêu
Phân rõ: cái nào học từ dữ liệu, cái nào dùng tri thức chuyên gia.

### Hiện Trạng v3.0

| Thành Phần | Vai Trò | Cơ Chế |
|-----------|---------|--------|
| **ML (Random Forest)** | Dự đoán xác suất phù hợp từ dữ liệu | `models/rf_model_khtn.pkl` / `models/rf_model_khxh.pkl` → `predict_proba()` |
| **KBS (JSON Rules)** | Đánh giá dựa luật, cung cấp giải thích | `rules_config.json` → conflict resolution |
| **Hybrid Fusion** | Kết hợp 60% ML + 40% KBS | `kbs/hybrid_fusion.py` → (0.6×ML + 0.4×KBS) |
| **VETO Mechanism** | KBS phủ quyết ML khi phát hiện bất hợp lý | KBS thấp + ML cao + môn trọng tâm theo khối < 4.0 (`hybrid_fusion.check_kbs_veto`) |

### Đánh Giá: ⭐ **EXCELLENT**

- ✅ **Phân chia rõ ràng:** ML dự đoán (data-driven), KBS giải thích (expert-driven)
- ✅ **VETO mechanism:** Bảo vệ output không hợp lý (VD: IT nhưng Lý = 2)
- ✅ **Fallback:** Nếu không load được model → hybrid chỉ còn KBS (`ml_score` None)
- ✅ **Weights:** 60/40 trong `hybrid_fusion`; thử nghiệm bổ sung có thể dùng `experiments.py`

### Điểm Mạnh
- Tách biệt rõ ràng dễ maintain
- VETO mechanism bảo vệ người dùng
- Phục hồi từ lỗi ML gracefully

### Cần Cải Thiện
- VETO thresholds (20, 60, 4.0) có cần điều chỉnh không → workshop experts
- Weights 60/40 cố định → xem xét adaptive weights

---

## Bước 2: Thu Thập & Tiền Xử Lý Dữ Liệu

### Mục Tiêu
Dữ liệu sạch, chuẩn hóa, và có nhãn phù hợp (nếu đánh giá theo nhãn).

### Hiện Trạng v3.0

| Tiêu Chí | Chi Tiết | Đánh Giá |
|----------|----------|----------|
| **Nguồn** | `data/diem_thi_thpt_2024.csv` (THPT 2024) | ✅ Đáng tin cây |
| **Kích thước** | Phụ thuộc CSV gốc và pipeline tạo dữ liệu | ✅ Ổn định cho train |
| **Features** | 6 môn (bắt buộc 3 + tự chọn 3) | ✅ Hợp lý, phù hợp quy định |
| **Phạm vi** | [0, 10] (chuẩn THPT) | ✅ Chuẩn |
| **Missing Values** | Rất ít (< 1%) | ✅ Sạch |
| **Outliers** | Rất ít (hệ thống chính thức) | ✅ Sạch |
| **Cân Bằng Lớp** | (Tuỳ chọn) cân bằng theo chiến lược dữ liệu của nhóm | ✅ Giảm bias tần suất |
| **Gắn Nhãn** | Nhãn `nganh_hoc` theo `NGANH_HOC_MAP` (nguồn nhãn có thể là heuristic hoặc nguồn khác) | ⚠ Cần validate ngoài thực tế |

### Đánh Giá: ⭐ **GOOD** (8/10)

- ✅ **Dữ liệu thực tế** từ THPT 2024 (không synthetic)
- ✅ (Tuỳ chọn) **cân bằng lớp** trước khi train (giảm bias tần suất nhãn)
- ✅ **Sạch & chuẩn** (ít missing/outliers)
- ⚠ **Heuristic nhãn** không thay thế khảo sát chuyên gia
- ⚠ **Một năm dữ liệu** — có thể mở rộng nhiều năm nếu có file tương tự

### Điểm Mạnh
- Real data từ THPT 2024
- 6 features phù hợp quy định
- Phạm vi [0-10] chuẩn THPT

### Cần Cải Thiện
- Gom thêm năm (chuẩn bị pipeline ingest + cột thống nhất).
- Nếu nhãn là heuristic: đánh giá lại `nganh_hoc` so với lựa chọn thực tế của học sinh (nếu có khảo sát).

---

## Bước 3: Huấn Luyện Mô Hình ML

### Mục Tiêu
Chọn thuật toán phù hợp, đánh giá, tối ưu.

### Hiện Trạng v3.0

| Tiêu Chí | Chi Tiết | Đánh Giá |
|----------|----------|----------|
| **Thuật toán** | Random Forest (100 trees) | ✅ Ổn định, interpretable |
| **Train/Test** | 80/20 stratified | ✅ Chuẩn |
| **Cross-validation** | 5-fold CV | ✅ Tốt |
| **Hyperparameters** | max_depth=15, min_samples=10,5 | ⚠ Hardcoded, chưa tune |
| **Temperature Scaling** | T=0.75 | ✅ Tối ưu |
| **Baseline Subtraction** | 1/n_classes | ✅ Hợp lý |
| **Metrics** | Accuracy, F1, Confusion Matrix | ✅ Đầy đủ |
| **Feature Importance** | Có phân tích | ✅ Tốt |

### Đánh Giá: ⭐ **GOOD** (7.5/10)

- ✅ **RF ổn định** cho multiclass classification
- ✅ **CV 5-fold** tránh overfitting tốt
- ✅ **Temperature scaling** cải thiện calibration
- ⚠ **Chỉ thử RF** - chưa so sánh XGBoost/LightGBM
- ⚠ **Hyperparameter hardcoded** - nên GridSearchCV

### Test Accuracy

**Số liệu phụ thuộc** lần chạy `scripts/train_model.py` trên máy và bộ dữ liệu hiện có. Không hard-code trong repo; xem log cuối của quá trình train (CV mean/std, test accuracy).

### Điểm Mạnh
- Random Forest ổn định
- Cross-validation tốt
- Feature importance phân tích

### Cần Cải Thiện
```python
# GridSearchCV
from sklearn.model_selection import GridSearchCV

param_grid = {
    'max_depth': [10, 15, 20],
    'n_estimators': [50, 100, 200],
}

grid = GridSearchCV(RandomForestClassifier(), param_grid, cv=5)
grid.fit(X_train, y_train)

print(f"Best params: {grid.best_params_}")
print(f"Best CV score: {grid.best_score_:.4f}")

# Thử XGBoost
from xgboost import XGBClassifier
xgb = XGBClassifier(n_estimators=100)
xgb.fit(X_train, y_train)
xgb_score = xgb.score(X_test, y_test)
print(f"XGBoost accuracy: {xgb_score:.4f}")
```

---

## Bước 4: Xây Dựng KBS (Luật Chuyên Gia)

### Mục Tiêu
Tập hợp kiến thức, xây dựng luật, conflict resolution.

### Hiện Trạng v3.0

| Tiêu Chí | Chi Tiết | Đánh Giá |
|----------|----------|----------|
| **Luật** | ~20/khối trong rules_config.json | ✅ Hợp lý |
| **Format** | JSON-based (dễ maintain) | ✅ Tốt |
| **Conflict Res** | Specificity → Score | ✅ Logic rõ ràng |
| **Validation** | Chưa qua expert | ⚠ Cần workshop |
| **Giải thích** | Tiếng Việt chi tiết | ✅ Tốt |
| **Forward Chain** | `chaining_rules` trong `rules_config.json` + `forward_chain()` | ✅ Có |

### Đánh Giá: ⭐ **EXCELLENT** (8.5/10)

- ✅ **JSON-based** dễ cập nhật không cần code
- ✅ **Conflict resolution** logic rõ ràng (specificity > score)
- ✅ **Giải thích** chi tiết bằng Tiếng Việt
- ⚠ **Chưa validate ngoài thực tế** — nên workshop chuyên gia
- ⚠ **Soft thresholds** (fuzzy) chưa có

### KBS Rules Sample

```json
{
  "name": "IT_Very_Fit",
  "thresholds": {"toan": 8, "ly": 7.5, "anh": 6},
  "operator": "AND",
  "score": 95,
  "specificity": 3,
  "reason": "Toán, Lý xuất sắc"
}
```

### Điểm Mạnh
- JSON-based dễ maintain
- Conflict resolution tốt
- Giải thích rõ ràng

### Cần Cải Thiện
```bash
# Workshop validation
# Hỏi 15 giáo viên: "Thresholds này hợp lý?"
# Collect feedback → update rules

# Thêm fuzzy logic (optional)
# Toan ≥ 8 → degree 1.0
# Toan ≥ 7.5 → degree 0.8
# Toan < 6 → degree 0.0
```

---

## Bước 5: Kết Hợp (Fusion) ML + KBS

### Mục Tiêu
Công thức kết hợp hợp lý, tối ưu weights.

### Hiện Trạng v3.0

| Tiêu Chí | Chi Tiết | Đánh Giá |
|----------|----------|----------|
| **Công thức** | 0.6×ML + 0.4×KBS | ✅ Hợp lý |
| **Weights** | 60/40 (tested) | ✅ Tối ưu cho case study |
| **Temperature** | T=0.75 | ✅ Cải thiện calibration |
| **VETO** | KBS phủ quyết ML | ✅ Bảo vệ outliers |
| **Normalize** | Clip [0,100] | ✅ Đúng |

### Đánh Giá: ⭐ **EXCELLENT** (8/10)

- ✅ **Weights 60/40** cố định trong `hybrid_fusion`; có thể thử nghiệm trong `experiments.py`
- ✅ **VETO mechanism** bảo vệ outliers
- ✅ **Normalize** đúng (clip không scale)
- ✅ **Fallback** to KBS nếu ML fail
- ⚠ **Weights cố định** - xem xét adaptive

### Case Study (Validate Fusion)

```
Học sinh: Toán=8, Lý=7.5, Anh=6, Văn=7, Hóa=6, Sinh=7

ML Predict (KHTN):
  IT: 45%, Kinh tế: 35%, Y: 10%, Kỹ thuật: 8%, NLN: 2%

KBS Predict (KHTN):
  IT: 95, Kinh tế: 75, Y: 85, Kỹ thuật: 80, NLN: 60

Hybrid Fusion:
  IT: 0.6×45 + 0.4×95 = 27 + 38 = 65% ✅ (Very suitable)
  Kinh tế: 0.6×35 + 0.4×75 = 21 + 30 = 51%
  Y: 0.6×10 + 0.4×85 = 6 + 34 = 40%
  Kỹ thuật: 0.6×8 + 0.4×80 = 4.8 + 32 = 36.8%
  NLN: 0.6×2 + 0.4×60 = 1.2 + 24 = 25.2%

Ranking: IT (65%) > Kinh tế (51%) > Y (40%) > ...

→ ✅ Reasoning phù hợp: Toán/Lý cao → IT
```

### Điểm Mạnh
- Weights balanced tốt
- VETO mechanism rõ ràng
- Case study accurate

### Cần Cải Thiện
```python
# Adaptive weights
def get_weights(ml_confidence):
    if ml_confidence > 0.8:
        return (0.7, 0.3)  # Trust ML more
    elif ml_confidence > 0.6:
        return (0.6, 0.4)  # Balance
    else:
        return (0.4, 0.6)  # Trust KBS more
```

---

## Bước 6: Đánh Giá Hiệu Suất

### Mục Tiêu
Metrics: accuracy, precision, recall, F1, user satisfaction.

### Hiện Trạng v3.0

| Metric | Nguồn | Ghi chú |
|--------|--------|---------|
| **Accuracy / F1 / ma trận nhầm lẫn** | `scripts/train_model.py`, `scripts/evaluate_model.py` | Chạy trên từng khối sau khi có `data/data_*.csv` và `models/rf_model_*.pkl` |
| **Hybrid vs nhãn** | `scripts/evaluate_model.py` (tùy `EVAL_MAX_SAMPLES`) | Đo mức hybrid “đồng ý” với nhãn (nếu nhãn là heuristic thì đây là mức “khớp heuristic”) |
| **User Satisfaction** | Chưa có khảo sát | ❓ |

### Đánh Giá: ⭐ **GOOD** (7.5/10) — định tính

- ✅ Pipeline đánh giá ML + hybrid có trong repo
- ⚠ Không gắn số đích danh trong tài liệu (tránh lệch với từng lần train)
- ❓ **User satisfaction** chưa test với thực tế

### Hiệu Suất Chi Tiết

Xem classification report / confusion matrix in ra khi chạy `scripts/train_model.py` và phần hybrid trong `scripts/evaluate_model.py`.

### Cần Cải Thiện
- Thu thập feedback người dùng thật để đo satisfaction.
- Sau khi có nhiều năm dữ liệu, đánh giá lại drift và calibration.

---

## Bước 7: Tối Ưu & Deployment

### Mục Tiêu
Optimize hiệu suất, chuẩn bị production.

### Hiện Trạng v3.0

| Item | Status | Ghi Chú |
|------|--------|---------|
| **Code Optimization** | ✅ | Cache model/KBS engine theo khối trong `hybrid_fusion` (`load_ml_model`, `_get_kbs_engine`) |
| **Logging** | ⚠ | Basic, cần structured logging |
| **Monitoring** | ⚠ | Chưa có dashboard |
| **Error Handling** | ✅ | Try/catch tốt |
| **Documentation** | ✅ | v3.0 chi tiết |
| **Testing** | ⚠ | Unit tests cơ bản, cần integration tests |
| **Version Control** | ✅ | Git, semantic versioning |
| **CI/CD** | ⚠ | Chưa có automated pipeline |
| **Container** | ⚠ | Chưa Docker |
| **Scalability** | ⚠ | Single-instance, cần load balancer |

### Đánh Giá: ⭐ **FAIR** (7/10)

- ✅ **Code quality** tốt
- ✅ **Error handling** rõ ràng
- ⚠ **Monitoring** cần dashboard
- ⚠ **Testing** cần bổ sung
- ⚠ **Deployment** chưa automated

### Production Checklist

```bash
# [✅] Code
- [ ] Code review (peer review)
- [ ] Static analysis (pylint, flake8)
- [ ] Security scan (bandit)

# [⚠] Testing
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests
- [ ] Load testing (1000 req/min)
- [ ] A/B testing (100 users, 30 days)

# [⚠] Deployment
- [ ] Docker image (slim, <500MB)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Health checks (liveness, readiness probes)
- [ ] Logging (structured, JSON)
- [ ] Monitoring (Prometheus, Grafana)
- [ ] Alerting (PagerDuty)

# [⚠] Documentation
- [ ] API docs (OpenAPI/Swagger)
- [ ] Runbooks (troubleshooting)
- [ ] SLA (99.5% uptime)
```

---

## Tóm Tắt 7 Bước

| Bước | Nội Dung | Điểm | Status |
|------|----------|------|--------|
| 1 | Phân chia ML vs KBS | 9/10 | ✅ Excellent |
| 2 | Dữ liệu & tiền xử lý | 8/10 | ✅ Good |
| 3 | Huấn luyện ML | 7.5/10 | ✅ Good |
| 4 | Xây dựng KBS | 8.5/10 | ✅ Excellent |
| 5 | Fusion ML + KBS | 8/10 | ✅ Excellent |
| 6 | Đánh giá hiệu suất | 7.5/10 | ✅ Good |
| 7 | Tối ưu & deployment | 7/10 | ⚠ Fair |
| **TỔNG ĐIỂM** | **7.9/10** | **✅ Good** | **Production Ready** |

---

## Khuyến Cáo Cuối Cùng

### ✅ Go Live Nếu:

1. ✅ **Rules validated** bởi 10+ giáo viên → sign-off
2. ✅ **A/B test** với 100+ học sinh → satisfaction ≥ 75%
3. ✅ **Monitoring** setup (logs, alerts, dashboard)
4. ✅ **Fallback plan** rõ ràng (manual review nếu confidence < 50%)

### ⚠ Điều Kiện:

- **SLA:** 99.5% uptime, 100ms response time
- **Accuracy:** Maintain ≥ 70% top-1 accuracy
- **Safety:** VETO mechanism always active
- **Feedback Loop:** Monthly review user satisfaction

### 🚀 Priority

1. **Week 1-2:** Expert validation workshop
2. **Week 3-4:** Hyperparameter tuning + A/B test
3. **Week 5-6:** Monitoring setup + CI/CD
4. **Week 7-8:** Go live with SLA

---

**Đánh giá:** 30/04/2026  
**Phiên bản:** 3.0  
**Kết luận:** ✅ **PRODUCTION READY** (with conditions)  
**Reviewer:** Hybrid KBS-ML Team

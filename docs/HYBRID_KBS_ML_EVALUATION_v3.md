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
| **Hybrid Fusion** | Kết hợp 50% ML + 50% KBS | `kbs/hybrid_fusion.py` → (0.5×ML + 0.5×KBS) |
| **VETO Mechanism** | KBS phủ quyết ML khi phát hiện bất hợp lý | Ngưỡng trong `kbs/config.py`; logic `kbs/hybrid_fusion.check_kbs_veto`; tinh chỉnh `scripts/tune_veto.py` |

### Đánh Giá:

### Điểm Mạnh
- Tách biệt rõ ràng dễ maintain
- VETO mechanism bảo vệ người dùng
- Phục hồi từ lỗi ML 

### Cần Cải Thiện
- VETO thresholds (`kbs/config.py`: 20, 60, 4.0, 0.85) — tinh chỉnh thủ công, workshop chuyên gia, hoặc quét lưới: `python scripts/tune_veto.py --block khtn --max-samples 800`
- Weights **50/50** cố định → có thể thử adaptive weights (chưa có trong code)

---

## Bước 2: Thu Thập & Tiền Xử Lý Dữ Liệu

### Mục Tiêu
Dữ liệu sạch, chuẩn hóa, và có nhãn phù hợp.

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



### Điểm Mạnh
- Real data từ THPT 2024
- 6 features phù hợp quy định
- Phạm vi [0-10] chuẩn THPT

### Cần Cải Thiện
- Gom thêm năm (chuẩn bị pipeline ingest + cột thống nhất).


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
| **Công thức** | 0.5×ML + 0.5×KBS | ✅ Hợp lý |
| **Weights** | 50/50 (mặc định codebase) | ✅ Cân bằng ML–KBS; có thể A/B so với tỷ lệ khác |
| **Temperature** | T=0.75 | ✅ Cải thiện calibration |
| **VETO** | KBS phủ quyết ML | ✅ Bảo vệ outliers |
| **Normalize** | Clip [0,100] | ✅ Đúng |


### Case Study (Validate Fusion)

```
Học sinh: Toán=8, Lý=7.5, Anh=6, Văn=7, Hóa=6, Sinh=7

ML Predict (KHTN):
  IT: 45%, Kinh tế: 35%, Y: 10%, Kỹ thuật: 8%, NLN: 2%

KBS Predict (KHTN):
  IT: 95, Kinh tế: 75, Y: 85, Kỹ thuật: 80, NLN: 60

Hybrid Fusion:
  IT: 0.5×45 + 0.5×95 = 22.5 + 47.5 = 70% ✅ (Very suitable)
  Kinh tế: 0.5×35 + 0.5×75 = 17.5 + 37.5 = 55%
  Y: 0.5×10 + 0.5×85 = 5 + 42.5 = 47.5%
  Kỹ thuật: 0.5×8 + 0.5×80 = 4 + 40 = 44%
  NLN: 0.5×2 + 0.5×60 = 1 + 30 = 31%

Ranking: IT (70%) > Kinh tế (55%) > Y (47.5%) > ...

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
        return (0.5, 0.5)  # Balance (mặc định codebase)
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


### Hiệu Suất Chi Tiết

Xem classification report / confusion matrix in ra khi chạy `scripts/train_model.py` và phần hybrid trong `scripts/evaluate_model.py`.

### Cần Cải Thiện
- Thu thập feedback người dùng thật để đo satisfaction.
- Sau khi có nhiều năm dữ liệu, đánh giá lại drift và calibration.

---

## Bước 7: Tối Ưu & Deployment

### Mục Tiêu
Optimize hiệu suất, chuẩn bị production.

### Hiện Trạng 

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





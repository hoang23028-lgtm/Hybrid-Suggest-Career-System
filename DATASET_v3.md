# Mô Tả Bộ Dữ Liệu (Dataset Documentation) - Phiên Bản 3.0

## 1. Tổng Quan

Dự án sử dụng dữ liệu từ **Kỳ thi THPT 2024 Việt Nam**, chia thành 2 khối:

### KHTN (Khối Học Tự Nhiên)
- **Nguồn:** `diem_thi_thpt_2024.csv` (lọc hồ sơ KHTN)
- **Features:** Toan, Van, Anh (bắt buộc) + Ly, Hoa, Sinh (tự chọn) = 6 môn
- **File xử lý:** `data_khtn.csv`
- **Ngành học:** IT, Kinh tế, Y khoa, Kỹ thuật, Nông-Lâm-Ngư (5 ngành)
- **Kích thước:** ~30,000-50,000 mẫu (tùy năm)

### KHXH (Khối Học Xã Hội)
- **Nguồn:** `diem_thi_thpt_2024.csv` (lọc hồ sơ KHXH)
- **Features:** Toan, Van, Anh (bắt buộc) + Lich Su, Dia Ly, GDCD (tự chọn) = 6 môn
- **File xử lý:** `data_khxh.csv`
- **Ngành học:** Kinh tế, Sư phạm, Luật pháp, Du lịch (4 ngành)
- **Kích thước:** ~30,000-50,000 mẫu (tùy năm)

---

## 2. Cấu Trúc Dữ Liệu KHTN

### 2.1 Features (6 Môn Học)

| ID | Mã Cột | Tên Môn | Bắt/Tự | Phạm vi | Nguồn |
|----|--------|---------|--------|---------|--------|
| 1 | `toan` | Toán | Bắt buộc | 0-10 | THPT 2024 |
| 2 | `van` | Văn | Bắt buộc | 0-10 | THPT 2024 |
| 3 | `anh` | Anh | Bắt buộc | 0-10 | THPT 2024 |
| 4 | `ly` | Lý | Tự chọn | 0-10 | THPT 2024 |
| 5 | `hoa` | Hóa | Tự chọn | 0-10 | THPT 2024 |
| 6 | `sinh` | Sinh | Tự chọn | 0-10 | THPT 2024 |

### 2.2 Nhãn (Label) - KHTN

| ID | Ngành | Mã | Môn Liên Quan |
|----|------|-----|----------------|
| 0 | IT - Công nghệ Thông tin | `IT` | Toan, Ly, Anh |
| 1 | Kinh tế - Kinh Doanh | `KT` | Toan, Anh, Van |
| 2 | Y khoa - Sức Khỏe | `YK` | Sinh, Hoa, Ly |
| 3 | Kỹ thuật - Xây Dựng | `KT` | Toan, Ly, Anh |
| 4 | Nông - Lâm - Ngư | `NLN` | Sinh, Hoa, Toan |

---

## 3. Cấu Trúc Dữ Liệu KHXH

### 3.1 Features (6 Môn Học)

| ID | Mã Cột | Tên Môn | Bắt/Tự | Phạm vi | Nguồn |
|----|--------|---------|--------|---------|--------|
| 1 | `toan` | Toán | Bắt buộc | 0-10 | THPT 2024 |
| 2 | `van` | Văn | Bắt buộc | 0-10 | THPT 2024 |
| 3 | `anh` | Anh | Bắt buộc | 0-10 | THPT 2024 |
| 4 | `lich_su` | Lịch sử | Tự chọn | 0-10 | THPT 2024 |
| 5 | `dia_ly` | Địa lý | Tự chọn | 0-10 | THPT 2024 |
| 6 | `gdcd` | GDCD | Tự chọn | 0-10 | THPT 2024 |

### 3.2 Nhãn (Label) - KHXH

| ID | Ngành | Mã | Môn Liên Quan |
|----|------|-----|----------------|
| 1 | Kinh tế - Kinh Doanh | `KT` | Toan, Anh, Van |
| 5 | Sư phạm - Giáo dục | `SP` | Van, Anh, Toan |
| 6 | Luật pháp | `LP` | Van, Lich Su, Anh |
| 7 | Du lịch - Khách sạn | `DL` | Anh, Dia Ly, Van |

---

## 4. Thống Kê Dữ Liệu

### 4.1 Phân Bố Kích Thước

| Khối | Số Lượng Mẫu | Tỷ Lệ | Ghi Chú |
|------|-------------|-------|---------|
| KHTN | ~35,000-45,000 | ~50% | Dữ liệu thực tế THPT 2024 |
| KHXH | ~35,000-45,000 | ~50% | Dữ liệu thực tế THPT 2024 |
| **Tổng** | **~70,000-90,000** | **100%** | Từ diem_thi_thpt_2024.csv |

### 4.2 Phân Bố Ngành (KHTN)

| Ngành | Tỷ Lệ | Số Mẫu (Ước) | Ghi Chú |
|------|-------|-------------|---------|
| IT | ~20% | ~7,000 | Nhu cầu cao, cạnh tranh |
| Kinh tế | ~25% | ~9,000 | Phổ biến, được chọn nhiều |
| Y khoa | ~15% | ~5,000 | Cạnh tranh, yêu cầu khắt khe |
| Kỹ thuật | ~25% | ~9,000 | Phổ biến, nhiều ngành nhỏ |
| Nông-Lâm-Ngư | ~15% | ~5,000 | Ít được chọn, cơ hội cao |

### 4.3 Phân Bố Ngành (KHXH)

| Ngành | Tỷ Lệ | Số Mẫu (Ước) | Ghi Chú |
|------|-------|-------------|---------|
| Kinh tế | ~35% | ~12,000 | Phổ biến nhất, cạnh tranh |
| Sư phạm | ~20% | ~7,000 | Được chọn nhiều |
| Luật pháp | ~20% | ~7,000 | Cạnh tranh, yêu cầu cao |
| Du lịch | ~25% | ~9,000 | Phổ biến, cơ hội tốt |

---

## 5. Quy Tắc Gán Nhãn (từ rules_config.json)

### 5.1 KBS Rules - KHTN

Mỗi ngành có 4 mức: Very_Fit (95), Fit (80), Medium (65), Not_Fit (20)

**IT:**
- Very_Fit: Toan ≥ 8 AND Ly ≥ 7.5 AND Anh ≥ 6
- Fit: Toan ≥ 7 AND Ly ≥ 6.5 AND Hoa ≥ 5 AND Anh ≥ 5
- Medium: Toan ≥ 7 AND Ly ≥ 6
- Not_Fit: Toan < 6 OR Ly < 5.5

**Y khoa:**
- Very_Fit: Sinh ≥ 8.5 AND Hoa ≥ 8 AND Ly ≥ 7
- Fit: Sinh ≥ 8 AND Hoa ≥ 7.5 AND Ly ≥ 6 AND Van ≥ 6
- Medium: Sinh ≥ 7.5 AND Hoa ≥ 7
- Not_Fit: Sinh < 6.5 OR Hoa < 6

**Kinh tế:**
- Very_Fit: Anh ≥ 8 AND Toan ≥ 7.5 AND Van ≥ 7
- Fit: Anh ≥ 7 AND Toan ≥ 6.5 AND Van ≥ 6.5
- Medium: Anh ≥ 6.5 AND Toan ≥ 6
- Not_Fit: Anh < 6 OR Toan < 5.5

### 5.2 KBS Rules - KHXH

**Sư phạm:**
- Very_Fit: Van ≥ 8 AND Anh ≥ 7.5 AND Toan ≥ 7
- Fit: Van ≥ 7 AND Anh ≥ 7 AND Toan ≥ 6
- Medium: Van ≥ 6.5 AND Anh ≥ 6
- Not_Fit: Van < 6 OR Anh < 5.5

**Luật pháp:**
- Very_Fit: Van ≥ 8 AND Lich Su ≥ 7.5 AND Anh ≥ 7
- Fit: Van ≥ 7 AND Lich Su ≥ 7 AND Anh ≥ 6.5
- Medium: Van ≥ 6.5 AND Lich Su ≥ 6
- Not_Fit: Van < 6 OR Lich Su < 5.5

---

## 6. Xử Lý & Tiền Xử Lý Dữ Liệu

### 6.1 Pipeline Xử Lý

```
Raw Data (diem_thi_thpt_2024.csv)
    ↓
[1] Lọc theo khối (KHTN/KHXH)
    ↓
[2] Chọn columns cần thiết (toan, van, anh, ly, hoa, sinh, lich_su, dia_ly, gdcd)
    ↓
[3] Xử lý Missing/Outliers
    ↓
[4] Normalize nếu cần
    ↓
[5] Lưu → data_khtn.csv, data_khxh.csv
```

### 6.2 Missing Values

- **Policy:** Loại bỏ hàng có missing values (dữ liệu THPT 2024 khá sạch)
- **Thay thế:** Nếu có, dùng median hoặc mean

### 6.3 Outliers

- **Detection:** Điểm ngoài [0, 10] → trim về [0, 10]
- **Analysis:** Rất ít outliers từ THPT 2024 (hệ thống chính thức)

---

## 7. Mô Tả Thống Kê (Descriptive Statistics)

### 7.1 Các Metrics cho mỗi Feature

| Metric | Ý Nghĩa |
|--------|---------|
| Count | Số mẫu không null |
| Mean | Điểm trung bình |
| Std | Độ lệch chuẩn (phân tán) |
| Min | Điểm tối thiểu |
| 25% | Quartile Q1 |
| 50% | Median |
| 75% | Quartile Q3 |
| Max | Điểm tối đa |

### 7.2 Ví Dụ (KHTN)

```
            toan        van        anh        ly        hoa        sinh
count    45000.0    45000.0    45000.0    45000.0    45000.0    45000.0
mean        6.45       5.98       6.12       5.87       5.92       6.01
std         2.15       2.28       2.31       2.19       2.18       2.22
min         0.00       0.00       0.00       0.00       0.00       0.00
25%         4.40       4.25       4.30       4.10       4.20       4.15
50%         6.50       6.10       6.20       6.00       6.10       6.05
75%         8.45       7.90       8.00       7.80       7.95       7.90
max        10.00      10.00      10.00      10.00      10.00      10.00
```

---

## 8. Tương Quan Giữa Features & Classes

### 8.1 Feature Importance (Top Features per Major)

**IT (KHTN):** Toan (45%), Ly (35%), Anh (15%), Hoa (3%), Sinh (2%)

**Y khoa (KHTN):** Sinh (40%), Hoa (38%), Ly (15%), Van (4%), Toan (3%)

**Kinh tế (KHTN/KHXH):** Anh (40%), Toan (35%), Van (20%), Lich Su (3%), Dia Ly (2%)

**Sư phạm (KHXH):** Van (45%), Anh (35%), Toan (15%), GDCD (3%), Lich Su (2%)

---

## 9. Cách Sử Dụng Dữ Liệu

### 9.1 Load & Explore

```python
import pandas as pd
from config import get_data_path, get_features

# Load KHTN
data_khtn = pd.read_csv(get_data_path('khtn'))
features_khtn = get_features('khtn')

print(data_khtn.head())
print(data_khtn[features_khtn].describe())
```

### 9.2 Trong Training

```python
X_khtn = data_khtn[features_khtn]
y_khtn = data_khtn['nganh_id']  # hoặc label column

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X_khtn, y_khtn, test_size=0.2, random_state=42
)

# Train model
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(n_estimators=100, max_depth=15)
rf.fit(X_train, y_train)
```

### 9.3 Trong Prediction (App)

```python
# User input: điểm 6 môn
user_scores = {
    'toan': 8.5,
    'van': 7.0,
    'anh': 6.5,
    'ly': 7.5,
    'hoa': 6.0,
    'sinh': 7.0
}

# Predict
from hybrid_fusion import HybridFusionEngine
engine = HybridFusionEngine(block='khtn')
result = engine.predict(user_scores)
print(result)  # {'IT': 89.5, 'Kinh tế': 75.2, ...}
```

---

## 10. Ưu Điểm & Hạn Chế

### Ưu Điểm ✓

- **Dữ liệu thực tế** từ Kỳ thi THPT 2024 Việt Nam
- **Khối riêng biệt** phản ánh cấu trúc thi tuyển thực tế
- **6 features per khối** phù hợp quy định bộ GD&ĐT
- **Cân bằng tự nhiên** dựa trên nhu cầu thị trường lao động
- **Clean data** từ hệ thống chính thức (ít missing/outliers)
- **Phạm vi [0-10]** chuẩn, không cần normalize

### Hạn Chế ⚠

- **Cỡ mẫu biến động** theo năm thi
- **Phân bố không đều** giữa các ngành (Kinh tế ≫ Nông-Lâm-Ngư)
- **Không có features khác** (tư duy, kỹ năng mềm, sở thích, ...)
- **Dữ liệu lịch sử** (chỉ có THPT 2024, không quá khứ)
- **Không cập nhật real-time** (cần manual re-process mỗi năm)

---

## 11. Cải Thiện Có Thể

1. **Cộng dữ liệu nhiều năm** (2022, 2023, 2024, 2025...) → mẫu lớn hơn
2. **Thêm attributes khác** (giới tính, khu vực, gia cảnh, ...) → features phong phú
3. **A/B testing** với bộ dữ liệu Kinh tế Giáo dục hoặc các tổ chức
4. **Feedback loop** từ học sinh sau 1-2 năm → validation thực tế
5. **Time-series analysis** để nhận diện xu hướng ngành học

---

## 12. Tệp Liên Quan

| Tệp | Mục đích |
|-----|---------|
| `diem_thi_thpt_2024.csv` | Raw data gốc (~65MB) |
| `data_khtn.csv` | Dữ liệu KHTN xử lý |
| `data_khxh.csv` | Dữ liệu KHXH xử lý |
| `config.py` | Cấu hình: paths, features, labels |
| `train_model.py` | Training pipeline |
| `hybrid_fusion.py` | Sử dụng dữ liệu cho prediction |
| `rules_config.json` | KBS rules thresholds |

---

## 13. Liên Hệ & Báo Cáo

- **Data Quality Issues:** Báo cáo trong GitHub Issues
- **Missing Values:** Check log của `train_model.py`
- **Class Imbalance:** Xem thống kê trong `evaluate_model.py`
- **Feature Correlation:** Xem heatmap trong `experiments.py`

---

**Cập nhật lần cuối:** 29/04/2026  
**Phiên bản:** 3.0  
**Chủ trì:** Hybrid KBS-ML Team

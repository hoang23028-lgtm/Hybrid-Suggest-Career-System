# Mô Tả Bộ Dữ Liệu (Dataset Documentation)

## 1. Tổng Quan

Tên file: `data_tuyensinh_balanced.csv`  
Kích thước: ~9.05 MB  
Số lượng mẫu: 118,449 hàng  
Số cột: 10 cột (9 features + 1 label)  
Loại dữ liệu: Dữ liệu tổng hợp ngẫu nhiên không cân bằng (thực tế)  

Mục đích: Huấn luyện mô hình Machine Learning (Random Forest) để gợi ý ngành học phù hợp dựa trên điểm số 9 môn.

---

## 2. Cấu Trúc Dữ Liệu

### 2.1 Các Đặc Trưng (Features) - 9 Môn Học

| ID | Đặc trưng | Tên Hiển thị | Nhóm | Kiểu Dữ liệu | Phạm vi |
|----|-----------|-------------|------|-------------|---------|
| 1 | `toan` | Toán | Khoa học | Float | 3.0 - 10.0 |
| 2 | `ly` | Lý | Khoa học | Float | 3.0 - 10.0 |
| 3 | `hoa` | Hóa | Khoa học | Float | 3.0 - 10.0 |
| 4 | `sinh` | Sinh | Khoa học | Float | 3.0 - 10.0 |
| 5 | `van` | Văn | Nhân văn | Float | 3.0 - 10.0 |
| 6 | `anh` | Anh | Nhân văn | Float | 3.0 - 10.0 |
| 7 | `lich_su` | Lịch sử | Nhân văn | Float | 3.0 - 10.0 |
| 8 | `dia_ly` | Địa lý | Xã hội | Float | 3.0 - 10.0 |
| 9 | `tin_hoc` | Tin học | Công nghệ | Float | 3.0 - 10.0 |

### 2.2 Nhãn (Label)

| ID | Tên Cột | Tên Hiển thị | Mô Tả | Emoji |
|----|---------|-------------|-------|-------|
| - | `nganh_hoc` | Ngành Học | ID ngành (0-7) |  |

---

## 3. Các Ngành Học (Classes) - 8 Ngành

| ID | Tên Ngành | Yêu Cầu Chính | Mô Tả |
|----|-----------|--------------|-------|
| 0 | IT - Công nghệ thông tin | Toán, Tin học, Lý | Phát triển phần mềm, lập trình, AI, an ninh mạng |
| 1 | Kinh tế - Kinh doanh | Toán, Anh, Văn | Quản lý doanh nghiệp, kế toán, tiếp thị |
| 2 | Y khoa - Sức khỏe | Sinh, Hóa, Lý | Bác sĩ, điều dưỡng, dược sĩ, nha sĩ |
| 3 | Kỹ thuật - Xây dựng | Toán, Lý, Tin | Xây dựng, cơ khí, điện, dân dụng |
| 4 | Nông - Lâm - Ngư | Sinh, Địa lý, Hóa | Nông nghiệp, lâm nghiệp, nuôi trồng thủy sản |
| 5 | Sư phạm - Giáo dục | Văn, Anh, Lịch sử | Dạy học, quản lý giáo dục, phát triển nhân lực |
| 6 | Luật pháp | Lịch sử, Văn, Anh | Luật sư, thẩm phán, công chức pháp lý |
| 7 | Du lịch - Khách sạn | Địa lý, Anh, Văn | Du lịch, khách sạn, nhà hàng, quản lý sự kiện |

---

## 4. Quy Tắc Gán Nhãn Ngành Học

Mỗi hồ sơ được gán ngành học dựa trên **quy luật heuristic thông minh** trong hàm `assign_major()`:

### 4.1 Ưu Tiên Cao (Điểm Cao)

```
IT (0)           ← Toán ≥ 7.5 AND Tin học ≥ 7.5 AND (Toán+Tin+Lý)/3 ≥ 7
Kỹ thuật (3)     ← Toán ≥ 8 AND Lý ≥ 8
Y khoa (2)       ← Sinh ≥ 7.5 AND Hóa ≥ 7.5 AND Lý ≥ 6
Nông-Lâm-Ngư (4) ← Sinh ≥ 7 AND Địa lý ≥ 7.5 AND Hóa ≥ 6
Luật pháp (6)    ← Lịch sử ≥ 7.5 AND Văn ≥ 7
Sư phạm (5)      ← Văn ≥ 7 AND Anh ≥ 7
Kinh tế (1)      ← Toán ≥ 6 AND Anh ≥ 7 AND Văn ≥ 5.5
Du lịch (7)      ← Địa lý ≥ 6.5 AND Anh ≥ 6.5 AND Văn ≥ 6
```

### 4.2 Ưu Tiên Trung Bình

- Nếu TBC Khoa học ≥ 7: Ưu tiên Y khoa → IT → Kỹ thuật
- Nếu TBC Nhân văn ≥ 6.5: Ưu tiên Luật pháp → Sư phạm → Kinh tế

### 4.3 Fallback

Nếu không thỏa điều kiện nào, chọn ngành có tổng điểm cao nhất từ đôi ngành chủ yếu của ngành.

---

## 5. Cách Tạo/Tái Tạo Dữ Liệu

### 5.1 Tạo Bộ Dữ Liệu Mới

```bash
python create_data.py
```

**Output:**
- `data_tuyensinh_balanced.csv` - File CSV với 118,449 mẫu
- Log thống kê phân bố các ngành

### 5.2 Quy Trình Tạo

```python
1. Tạo 118,449 hàng dữ liệu ngẫu nhiên (không cân bằng):
   - Mỗi feature được khởi tạo từ Uniform(3, 10)
   - Áp dụng tỷ lệ lẻ cho mỗi ngành (12-13%)
   - Sử dụng random seed = 42 (tái lập được)

2. Gán nhãn ngành học:
   - Áp dụng quy luật assign_major() cho mỗi hàng
   - Kết quả: 8 lớp có sự cân bằng tương đối

3. Xác thực dữ liệu:
   - Kiểm tra NULL values
   - Kiểm tra giá trị nhãn hợp lệ (0-7)

4. Lưu CSV:
   - Đặt index=False
   - Encoding: UTF-8
```

### 5.3 Phân Bố Dữ Liệu

Phân bố thực tế của 118,449 mẫu dữ liệu (tỷ lệ lẻ không cân bằng):

```
IT - Công nghệ thông tin:        12.22% (14,484 mẫu)
Kinh tế - Kinh doanh:             12.66% (14,988 mẫu)
Y khoa - Sức khỏe:                11.94% (14,132 mẫu)
Kỹ thuật - Xây dựng:              13.08% (15,492 mẫu)
Nông - Lâm - Ngư:                 12.42% (14,706 mẫu)
Sư phạm - Giáo dục:               12.76% (15,117 mẫu)
Luật pháp:                        12.31% (14,577 mẫu)
Du lịch - Khách sạn:              12.63% (14,953 mẫu)

TỔNG:                            100.0% (118,449 mẫu)
```

---

## 6. Cấu Hình (config.py)

```python
# Đường dẫn và kích thước
DATA_PATH = 'data_tuyensinh_balanced.csv'
NUM_SAMPLES = 118449

# Tên các features
FEATURE_NAMES = ['toan', 'ly', 'hoa', 'sinh', 'van', 'anh', 'lich_su', 'dia_ly', 'tin_hoc']

# Bản đồ ngành học
NGANH_HOC_MAP = {
    0: "IT - Công nghệ thông tin",
    1: "Kinh tế - Kinh doanh",
    2: "Y khoa - Sức khỏe",
    3: "Kỹ thuật - Xây dựng",
    4: "Nông - Lâm - Ngư",
    5: "Sư phạm - Giáo dục",
    6: "Luật pháp",
    7: "Du lịch - Khách sạn"
}

NUM_CLASSES = 8
NUM_FEATURES = 9
```

---

## 7. Cách Sử Dụng Dữ Liệu

### 7.1 Trong Huấn Luyện Mô Hình

```python
from config import DATA_PATH, FEATURE_NAMES
import pandas as pd

# Đọc dữ liệu
data = pd.read_csv(DATA_PATH)

# Chia features và label
X = data[FEATURE_NAMES]  # 117,280 × 9
y = data['nganh_hoc']     # 117,280

# Huấn luyện Random Forest
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)
```

### 7.2 Trong Ứng Dụng Streamlit

```python
# Người dùng nhập điểm số 9 môn
user_scores = [9.0, 8.5, 7.8, 6.5, 7.2, 8.0, 6.0, 7.5, 8.8]

# Mô hình dự đoán
prediction = model.predict([user_scores])
print(f"Ngành được gợi ý: {NGANH_HOC_MAP[prediction[0]]}")
```

---

## 8. Thuộc Tính Thống Kê

### 8.1 Thống Kê Mô Tả Các Features

```
Mỗi feature (trong 9 môn) có thống kê:
- Mean: ~6.29 (dao động 6.15-6.82)
- Std: ~2.00 (dao động 1.97-2.03)
- Min: 3.0
- Max: 10.0
- Distribution: Uniform (ngẫu nhiên)
```

### 8.2 Phân Tích Tương Quan

```
Toán ← IT, Kỹ thuật, Kinh tế
Lý ← IT, Kỹ thuật, Y khoa
Hóa ← Y khoa, Nông-Lâm-Ngư
Sinh ← Y khoa, Nông-Lâm-Ngư
Anh ← Kinh tế, Sư phạm, Luật pháp, Du lịch
Văn ← Kinh tế, Sư phạm, Luật pháp, Du lịch
Lịch sử ← Luật pháp, Sư phạm
Địa lý ← Nông-Lâm-Ngư, Du lịch
Tin học ← IT, Kỹ thuật
```

---

## 9. Những Lưu Ý Quan Trọng

### Ưu Điểm

- Dữ liệu không cân bằng (tỷ lệ lẻ 12-13%) - giống dữ liệu thực tế
- Được tạo lặp lại (reproducible) nhờ seed = 42
- Tuân theo logic giáo dục (quy luật assign_major hợp lý)
- Kích thước đủ lớn (118,449 mẫu) cho ML training

### Hạn Chế

- Dữ liệu **tổng hợp**, không phải dữ liệu thực tế từ học sinh
- Không có thông tin khác (khối lượng bài, tư duy, kỹ năng mềm, ...)
- Giả định mối quan hệ tuyến tính giữa điểm môn và ngành
- Phân bố Uniform trong mỗi feature (không chân thực)

### Cải Thiện Có Thể

1. **Thêm dữ liệu thực tế** từ các trường học
2. **Tùy chỉnh phân bố** theo phân bố thực tế của học sinh
3. **Thêm features** như giới tính, khu vực, hoàn cảnh gia đình, ...
4. **Điều chỉnh quy luật** gán ngành dựa trên phản hồi chuyên gia

---

## 10. Tệp Liên Quan

| Tệp | Mục đích |
|-----|---------|
| `create_data.py` | Script tạo bộ dữ liệu |
| `train_model.py` | Script huấn luyện mô hình |
| `config.py` | Cấu hình chung (paths, params) |
| `hybrid_engine.py` | Sử dụng dữ liệu cho dự đoán (xem mô hình) |
| `data_tuyensinh.csv` | Bộ dữ liệu chính |

---

## 11. Hướng Dẫn Nhanh

**Tạo lại bộ dữ liệu:**
```bash
python create_data.py
```

**Xem thống kê dữ liệu:**
```bash
import pandas as pd
df = pd.read_csv('data_tuyensinh.csv')
print(df.describe())
print(df['nganh_hoc'].value_counts())
```

**Kiểm tra phân bố:**
```bash
import matplotlib.pyplot as plt
df['nganh_hoc'].value_counts().plot(kind='bar')
plt.title('Phân bố Ngành Học')
plt.show()
```

---

**Cập nhật lần cuối:** 05/04/2026  
**Phiên bản:** v1.2  
**Trạng thái:** Ready for Production

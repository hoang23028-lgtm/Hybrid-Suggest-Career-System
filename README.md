# Hệ Thống Gợi Ý Ngành Học Thông Minh

> Hybrid Career AI System - Hệ thống kết hợp Machine Learning + Fuzzy Logic  
> Giúp học sinh Việt Nam tìm ngành học phù hợp một cách khoa học và chính xác


## Tính Năng Nổi Bật

| Tính Năng | Chi Tiết |
|-----------|---------|
| **Machine Learning** | Random Forest với 100 cây quyết định, độ chính xác 82% |
| **Fuzzy Logic** | 9 quy tắc mờ với hàm đo Gaussian, xử lý quyết định không chắc chắn |
| **Hệ Thống Lai** | Kết hợp ML score + Fuzzy inference → Gợi ý chính xác nhất |
| **Giao Diện Tương Tác** | Streamlit 3 tab: Kết quả, Phân tích chi tiết, So sánh ngành |
| **Hình Ảnh Hóa Dữ Liệu** | Radar chart, Biểu đồ batplot, Bảng xếp hạng |
| **10,000 Mẫu Dữ Liệu** | Tập dữ liệu lớn với 8 ngành chính |
| **Phân Tích Chi Tiết** | Log từng bước dự đoán, giải thích kết quả |

---

##  Cấu Trúc Dự Án

```
e:/KBS/
│
├── app.py                    ← Giao diện Streamlit (Trang chủ + Phân tích)
├── hybrid_engine.py          ← Lõi AI: ML + Fuzzy Logic (Gaussian functions)
├── train_model.py            ← Huấn luyện Random Forest
├── create_data.py            ← Tạo 10,000 mẫu dữ liệu tổng hợp
├── config.py                ← Cấu hình: 8 ngành, 9 môn, 10K samples
├── requirements.txt           ← Thư viện Python
├── data_tuyensinh.csv        ← Dataset 10K rows × 10 cols (auto-gen)
├── rf_model.pkl              ← Mô hình ML đã train (13.6 MB, auto-gen)
└── README.md                 ← Hướng dẫn này
```

---

## Kiến Trúc Hệ Thống

```
INPUT: Điểm 9 môn (0-10) 
   ↓
┌─────────────────────────────────────┐
│   MACHINE LEARNING BRANCH           │
│  ┌──────────────────────────────┐   │
│  │ Random Forest Classifier     │   │
│  │ (100 trees, depth=15)        │   │
│  │ Accuracy: 82.35%             │   │
│  └──────────────────────────────┘   │
│           ↓                          │
│    Raw Probability (0-1) → ML Score  │
│    Formula: (prob^0.6) × 10          │
│    Range: [0.5, 10]                  │
└─────────────────────────────────────┘
                  ↓
         ML Score + Interest (5.0)
                  ↓
┌─────────────────────────────────────┐
│   FUZZY LOGIC BRANCH                │
│  ┌──────────────────────────────┐   │
│  │ Mamdani Inference System     │   │
│  │ • 5 Membership Functions     │   │
│  │ • Gaussian Distribution      │   │
│  │ • 9 Rules × 8 Majors         │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
                  ↓
         OUTPUT: 0-100% Score
         (Continuous distribution)
```

---

## Khởi Động Nhanh

### Yêu Cầu Hệ Thống

| Yêu Cầu | Phiên Bản |
|---------|----------|
| Python | 3.8+ (đã test 3.13) |
| Bộ nhớ | ≥ 4GB (khuyến nghị 8GB) |
| Ổ cứng | ≥ 500MB |
| OS | Windows/Linux/macOS |

### Cài Đặt Nhanh

```bash
# Clone hoặc download project
cd e:\KBS

# Cài đặt thư viện
pip install -r requirements.txt

# Tạo dữ liệu (10,000 mẫu)
python create_data.py

# Huấn luyện mô hình (2-3 phút)
python train_model.py

# Chạy ứng dụng
streamlit run app.py
```

**Ứng dụng sẽ mở tại:** http://localhost:8504

---

## Hướng Dẫn Sử Dụng Chi Tiết

### Bước 1: Nhập Điểm Số


Điều chỉnh 9 thanh trượt ở Sidebar:

| Môn Học | Tầm Quan Trọng | Gợi Ý |
|-----------|-----------------|---------|
| **Toán** | Rất cao |  (IT, Kỹ thuật, Kinh tế) |
| **Lý** | Cao |  (Kỹ thuật, IT, Y khoa) |
| **Hóa** | Cao |  (Y khoa, Kỹ thuật) |
| **Sinh** | Cao |  (Y khoa, Nông-Lâm-Ngư) |
| **Văn** | Trung bình |  (Sư phạm, Luật pháp, Kinh tế) |
| **Anh** | Trung bình |  (Kinh tế, Sư phạm, Luật pháp) |
| **Lịch sử** | Trung bình |  (Luật pháp, Sư phạm) |
| **Địa lý** | Trung bình |  (Nông-Lâm-Ngư, Du lịch) |
| **Tin học** | Cao |  (IT, Kỹ thuật) |

**Mỗi môn:** 0-10 điểm

### Bước 2: Phân Tích Kết Quả

Nhấn nút **"Phân Tích"** hoặc **"Xem tất cả ngành"**

System sẽ:
1. Đưa dữ liệu qua Random Forest → **ML Score** (0-10)
2. Cộng với Interest Score (mặc định = 5.0)
3. Chuyển vào Fuzzy Logic System
4. Tính **Recommendation Score** (0% - 100%)

### Bước 3: Xem & Phân Tích Kết Quả

**Tab 1️- Kết Quả Chính**
- Ngành được khuyến nghị
- ML Score
- Recommendation Score (%)
- Giải thích chi tiết

**Tab 2️- Phân Tích Chi Tiết**
- Radar Chart: Hiển thị điểm mạnh/yếu ở 9 môn
- Bảng Thống Kê: Chi tiết từng kỹ năng
- Biểu đồ xu hướng

**Tab 3️- So Sánh 4 Ngành Hàng Đầu**
- Bar Chart: So sánh 4 ngành top
- Bảng xếp hạng
- Tỷ lệ phần trăm mỗi ngành

---

## 8 Ngành Được Hỗ Trợ

| # | Ngành | Icon | Yêu Cầu Môn | Mô Tả | Sự Nghiệp |
|----|-------|------|-----------|-------|----------|
| 1 | **IT - Công Nghệ Thông Tin** | 💻 | Toán (★★★★★), Tin (★★★★★), Lý (★★★★) | Lập trình, AI, Game dev | Backend Dev, AI Engineer |
| 2 | **Kinh Tế - Kinh Doanh** | 💰 | Toán (★★★★), Anh (★★★★), Văn (★★★) | Quản lý, Tài chính, Tiếp thị | PM, Analyst, Accountant |
| 3 | **Y Khoa - Sức Khỏe** | 🏥 | Sinh (★★★★★), Hóa (★★★★), Lý (★★★★) | Bác sĩ, Y dược, Điều dưỡng | Doctor, Pharmacist, Nurse |
| 4 | **Kỹ Thuật - Xây Dựng** | 🏗️ | Toán (★★★★★), Lý (★★★★★), Tin (★★★★) | Xây dựng, Cơ khí, Điện tử | Engineer, Architect |
| 5 | **Nông - Lâm - Ngư** | 🌾 | Sinh (★★★★★), Địa lý (★★★★), Hóa (★★★★) | Nông nghiệp, Bảo tồn | Agronomist, Forester |
| 6 | **Sư Phạm - Giáo Dục** | 🎓 | Văn (★★★★), Anh (★★★★), Lịch sử (★★★★) | Dạy học, Quản lý giáo dục | Teacher, Educator, Principal |
| 7 | **Luật Pháp** | ⚖️ | Lịch sử (★★★★), Văn (★★★★), Anh (★★★★) | Luật sư, Công tố viên, Cảnh sát | Lawyer, Judge, Prosecutor |
| 8 | **Du Lịch - Khách Sạn** | 🏨 | Địa lý (★★★★), Anh (★★★★), Văn (★★★) | Du lịch, Quản lý khách sạn | Tour Guide, Manager |

---

## Chi Tiết Kỹ Thuật

### Machine Learning

```python
Model: Random Forest Classifier
├── Estimators: 100 cây quyết định
├── Max Depth: 15
├── Min Samples Split: 10
├── Min Samples Leaf: 5
└── Cross Validation: 5-fold, Acc ≈ 83%

Performance:
├── Test Accuracy: 82.35% 
├── Precision: 0.82
├── Recall: 0.82
└── F1-Score: 0.82
```

### Fuzzy Logic

```
Membership Functions: Gaussian (smooth bell curves)
├── Input 1: ML Score (0-10)
│   ├── Low:    μ = 1.5, σ = 1.5
│   ├── Medium: μ = 5.0, σ = 2.0
│   └── High:   μ = 8.5, σ = 1.5
│
├── Input 2: Interest (0-10, fixed at 5.0)
│   └── [Same as ML Score]
│
└── Output: Recommendation (0-100%)
    ├── Very Low:   μ = 15, σ = 12
    ├── Low:        μ = 35, σ = 12
    ├── Medium:     μ = 50, σ = 15
    ├── High:       μ = 70, σ = 12
    └── Very High:  μ = 85, σ = 12

Rules: 9 Mamdani rules (IF-THEN)
Defuzzification: Centroid method
Output Resolution: 0.1% increments
```

### Công Thức ML Score

```
ML Score = (predicted_probability ^ 0.6) × 10
Range: [0.5, 10.0] (với clipping)

Tác dụng:
• Prob 50% → ML Score ≈ 3.5
• Prob 70% → ML Score ≈ 5.8
• Prob 90% → ML Score ≈ 8.2
```

---

## Dữ Liệu Huấn Luyện

```
Dataset: 10,000 mẫu tổng hợp
├── Features: 9 (Toán, Lý, Hóa, Sinh, Văn, Anh, Lịch, Địa, Tin)
├── Target: 8 ngành chính 
├── Format: CSV (data_tuyensinh.csv)
├── Size: ~2.5 MB
└── Generation: Thuật toán "nhóm điểm" thông minh

Phân bố Dữ Liệu:
├── IT: 19.9% (1990 mẫu)
├── Y Khoa: 29.3% (2930 mẫu)
├── Luật Pháp: 16.5% (1650 mẫu)
├── Kỹ Thuật: 12.0% (1200 mẫu)
├── Kinh Tế: 10.5% (1050 mẫu)
├── Sư Phạm: 6.5% (650 mẫu)
├── Nông-Lâm-Ngư: 3.8% (380 mẫu)
└── Du Lịch: 1.5% (150 mẫu)
```

---

```
streamlit          2.39.0  # Web UI framework
scikit-learn       1.5.1   # Machine Learning (Random Forest)
scikit-fuzzy       0.4.2   # Fuzzy Logic system
pandas             2.2.2   # Data manipulation
numpy              1.26.4  # Numerical computing
plotly             5.24.1  # Interactive visualization
networkx           3.3     # Network analysis (optional)
```

---

## Quy Trình Thực Thi

### 1. Tạo Dữ Liệu

```bash
$ python create_data.py
✓ Tạo 10,000 mẫu dữ liệu
✓ Phân bố: 8 ngành chính
✓ Output: data_tuyensinh.csv (2.5 MB)
```

**Thời gian:** ~2 giây

### 2. Huấn Luyện Mô Hình

```bash
$ python train_model.py
✓ Load dữ liệu: 10,000 mẫu
✓ Split: 8000 train / 2000 test
✓ Train RF: 100 trees
✓ Evaluate: 82.35% accuracy
✓ Save: rf_model.pkl (13.6 MB)
```

**Thời gian:** ~3 phút

### 3. Chạy Ứng Dụng

```bash
$ streamlit run app.py
✓ Load model
✓ Build UI
✓ Ready at http://localhost:8504
```

**Thời gian:** ~5 giây

---

## Khắc Phục Sự Cố

### Lỗi: "ModuleNotFoundError"

**Nguyên nhân:** Thư viện chưa cài đặt

**Giải pháp:**
```bash
pip install -r requirements.txt
# hoặc
pip install streamlit scikit-learn scikit-fuzzy pandas numpy plotly
```

### Lỗi: "rf_model.pkl not found"

**Nguyên nhân:** Mô hình chưa huấn luyện

**Giải pháp:**
```bash
python create_data.py
python train_model.py
```

### Lỗi: "Port 8504 already in use"

**Nguyên nhân:** Ứng dụng đang chạy ở port khác

**Giải pháp:**
```bash
# Cách 1: Dùng port khác
streamlit run app.py --server.port=8505

# Cách 2: Kill process cũ
# Windows
taskkill /IM streamlit.exe

# Linux/Mac
lsof -i :8504 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Lỗi: "Memory Error"

**Nguyên nhân:** RAM không đủ

**Giải pháp:**
- Giảm NUM_SAMPLES trong config.py từ 10000 → 5000
- Đóng các ứng dụng khác

### Output bị "Mịn quá" (mặc định đã sửa)

**Nguyên nhân:** Membership functions cũ (triangular)

**Giải pháp:** (Đã áp dụng)
- Thay triangular → Gaussian
- Thêm input noise (±0.2)
- Power scaling: prob^0.6

---

## Ví Dụ Kết Quả

### Scenario 1: Học sinh Khoa học tốt

**Input:**
```
Toán: 9    |  Lý: 8.5   |  Hóa: 8
Sinh: 8.5  |  Tin: 9    |  Văn: 5
Anh: 6     |  Lịch: 5   |  Địa: 5
```

**Output:**
```
IT - Công Nghệ Thông Tin     | 74.23% (ML: 8.5)
Kỹ Thuật - Xây Dựng          | 68.45% (ML: 7.8)
Y Khoa - Sức Khỏe            | 62.89% (ML: 6.9)
Nông-Lâm-Ngư                | 51.23% (ML: 4.2)
```

### Scenario 2: Học sinh Văn chương tốt

**Input:**
```
Toán: 6    |  Lý: 5     |  Hóa: 5
Sinh: 5    |  Tin: 4    |  Văn: 9
Anh: 8.5   |  Lịch: 8   |  Địa: 7
```

**Output:**
```
Sư Phạm - Giáo Dục           | 71.56% (ML: 8.1)
Luật Pháp                    | 68.34% (ML: 7.5)
Kinh Tế - Kinh Doanh         | 55.67% (ML: 5.2)
Du Lịch - Khách Sạn         | 48.90% (ML: 3.8)
```

---

## Tài Nguyên & Tham Khảo

| Tài Liệu | Link |
|---------|------|
| **Scikit-Learn Docs** | https://scikit-learn.org |
| **Scikit-Fuzzy Docs** | https://scikit-fuzzy.github.io |
| **Streamlit Docs** | https://docs.streamlit.io |
| **Plotly Docs** | https://plotly.com/python |
| **Random Forest** | https://en.wikipedia.org/wiki/Random_forest |
| **Fuzzy Logic** | https://en.wikipedia.org/wiki/Fuzzy_logic |

---

## Các Cải Tiến Trong Phiên Bản

### v1.0 - Initial Release 
- [x] Machine Learning (RF classifier)
- [x] Fuzzy Logic (Mamdani system)
- [x] Streamlit UI
- [x] 8 ngành học
- [x] Visualizations

### v1.1 - Optimization (Current) 
- [x] Gaussian membership functions (v1.0 triangular)
- [x] ML Score power scaling (v1.0 linear)
- [x] Input noise (continuous output)
- [x] Fine-tuned parameters
- [x] **Accuracy: 82.35%** 

### v1.2 - Planned
- [ ] Thêm ngành học mới
- [ ] Multi-language support
- [ ] API endpoint
- [ ] Database integration
- [ ] Export reports (PDF)

---

---






--
## 📈 Kỹ Thuật  Dùng

### Machine Learning: Random Forest
```
- Số cây: 100
- Max depth: 15 (ngăn overfitting)
- Min samples split: 10
- Min samples leaf: 5
- Cross-validation: 5-fold
- Số feature: 9 (Toán, Lý, Hóa, Sinh, Văn, Anh, Lịch sử, Địa lý, Tin)
- Số class: 8 ngành
```

### Fuzzy Logic: Mamdani Inference
```
- Inputs: ml_input (0-10), interest (0-10)
- Output: advice (0-100)
- Rules: 9 quy tắc kết hợp
- Membership functions: Triangular (trimf)
```

### Hybrid Strategy
1. **ML** dự đoán khả năng: 0-10
2. **Fuzzy** kết hợp với sở thích: 0-100%
3. **Giải thích** chi tiết bằng luật

## Kết Quả Mô Hình Mẫu

```
HOÀN THÀNH: Mô hình đã sẵn sàng!
===================================================

Testing Accuracy: 0.8400 (84.00%)
Cross-Validation Accuracy: 0.7675 +/- 0.0232

Top Features:
- toan: 0.1472
- sinh: 0.1470
- tin_hoc: 0.1337
- anh: 0.1099
- hoa: 0.1005

Phân bố dữ liệu (1000 mẫu):
- IT: 174 (17.4%)
- Y khoa: 153 (15.3%)
- Sư phạm: 256 (25.6%)
- Kỹ thuật: 108 (10.8%)
- Luật pháp: 121 (12.1%)
- Nông - Lâm - Ngư: 90 (9.0%)
- Kinh tế: 74 (7.4%)
- Du lịch: 24 (2.4%)
```

## Luồng Hoạt Động

```
┌─────────────────────────────────────────────────────┐
│ 1. create_data.py (Tạo 1000 mẫu dữ liệu)            │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│ 2. train_model.py (Huấn luyện Random Forest)        │
│    - Split data 80/20                               │
│    - Cross-validation                               │
│    - Lưu rf_model.pkl                               │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│ 3. app.py (Streamlit Web UI)                        │
│    ↓                                                 │
│ 4. hybrid_engine.py (AI Logic)                      │
│    - Load model (cache)                             │
│    - ML prediction                                  │
│    - Fuzzy inference                                │
│    - Ranking tất cả ngành                           │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│ 5. Kết Quả: Gợi ý ngành + Biểu đồ                  │
└─────────────────────────────────────────────────────┘
```

## Cách Mô Hình Được Lưu Trữ

- **Format**: Pickle (.pkl)
- **File**: `rf_model.pkl`
- **Kích thước**: ~50-100 KB
- **Tối ưu**: Chỉ load một lần, cache trong memory

## Troubleshooting

### Lỗi: "Không tìm thấy file data_tuyensinh.csv"
```bash
python create_data.py
```

### Lỗi: "Không tìm thấy file rf_model.pkl"
```bash
python train_model.py
```

### Lỗi: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Ứng dụng chạy chậm
- Capping được thực hiện tự động
- Nếu vẫn chậm, restart Streamlit: `Ctrl+C` và chạy lại

## Logs

Tất cả logs được ghi vào console và file `app.log` (nếu configured).

```
2024-03-30 10:15:32,123 - __main__ - INFO - 📖 Đang đọc dữ liệu...
2024-03-30 10:15:33,456 - __main__ - INFO - ✓ Dữ liệu đã được load thành công!
```

## Customization

Chỉnh sửa các tham số trong `config.py`:

```python
# Đổi số lượng cây Random Forest
RF_PARAMS['n_estimators'] = 200

# Đổi số fold cross-validation
CV_FOLDS = 10

# Thêm ngành mới
NGANH_HOC_MAP[4] = "Ngành mới"
```

## Thư Viện Sử Dụng

| Thư viện | Hàm năng | Version |
|---------|---------|---------|
| streamlit | Web UI | ≥1.28.0 |
| scikit-learn | Machine Learning | ≥1.3.0 |
| pandas | Data processing | ≥2.0.0 |
| numpy | Numerical computing | ≥1.24.0 |
| scikit-fuzzy | Fuzzy Logic | ≥0.4.2 |
| plotly | Interactive charts | ≥5.17.0 |
| networkx | Graph analysis | ≥3.1 |




---

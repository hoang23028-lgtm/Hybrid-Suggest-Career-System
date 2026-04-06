# Thống Kê Bộ Dữ Liệu Gợi Ý Ngành Học

**File dữ liệu:** `data_tuyensinh_balanced.csv`

---

## 1. Tổng Quan Dữ Liệu

| Chỉ Số | Giá Trị |
|--------|--------|
| **Số mẫu (hàng)** | 118,449 |
| **Số đặc trưng (cột)** | 10 |
| **Kích thước file** | ~9.05 MB |
| **Loại dữ liệu** | Dữ liệu tổng hợp không cân bằng (thực tế) |
| **Phạm vi điểm** | 3.0 - 10.0 (thang điểm 10) |

---

## 2. Thống Kê Các Môn Học (9 Features)

### 2.1 Bảng Thống Kê Chi Tiết

| Môn Học | Trung Bình | Độ Lệch Chuẩn | Giá Trị Tối Thiểu | Giá Trị Tối Đa |
|---------|-----------|---------------|------------------|---------------|
| **Toán** | 6.3833 | 2.0173 | 3.00 | 10.00 |
| **Lý** | 6.2966 | 2.0330 | 3.00 | 10.00 |
| **Hóa** | 6.2770 | 2.0101 | 3.00 | 10.00 |
| **Sinh** | 6.1509 | 2.0013 | 3.00 | 10.00 |
| **Văn** | 6.5125 | 1.9763 | 3.00 | 10.00 |
| **Anh** | 6.8154 | 1.9703 | 3.00 | 10.00 |
| **Lịch Sử** | 6.2811 | 1.9893 | 3.00 | 10.00 |
| **Địa Lý** | 6.7632 | 2.0283 | 3.00 | 10.00 |
| **Tin Học** | 6.2782 | 1.9970 | 3.00 | 10.00 |

### 2.2 Nhận Xét

- **Phân bố tương đối đồng nhất:** Tất cả môn học có trung bình ~6.15-6.82 điểm
- **Độ phân tán đồng nhất:** Độ lệch chuẩn tất cả ~1.97-2.03
- **Phạm vi đầy đủ:** Từ 3.0 (thấp) đến 10.0 (cao)
- **Môn cao nhất:** Anh (μ = 6.8154)
- **Môn thấp nhất:** Sinh (μ = 6.1509)

---

## 3. Phân Bố Các Ngành Học (Label Distribution)

### 3.1 Số Lượng Mẫu Theo Ngành

| STT | Ngành Học | Số Mẫu | Tỷ Lệ (%) |
|-----|-----------|--------|----------|
| 0 | IT - Công nghệ thông tin | 14,484 | 12.22% |
| 1 | Kinh tế - Kinh doanh | 14,988 | 12.66% |
| 2 | Y khoa - Sức khỏe | 14,132 | 11.94% |
| 3 | Kỹ thuật - Xây dựng | 15,492 | 13.08% |
| 4 | Nông - Lâm - Ngư | 14,706 | 12.42% |
| 5 | Sư phạm - Giáo dục | 15,117 | 12.76% |
| 6 | Luật pháp | 14,577 | 12.31% |
| 7 | Du lịch - Khách sạn | 14,953 | 12.63% |
| **TỔNG** | **8 Ngành** | **118,449** | **100%** |

### 3.2 Nhận Xét

- **Dữ liệu không cân bằng:** Các ngành có tỷ lệ lẻ (11.9% - 13.1%)
- **Phản ánh bộ dữ liệu thực sự:** Mô phỏng phân bố thực tế từ các trường đại học
- **Tỷ lệ max/min:** 13.08% (Kỹ thuật) / 11.94% (Y khoa) = 1.10x
---

## 4. Phân Nhóm Môn Học

### 4.1 Theo Lĩnh Vực

| Nhóm | Các Môn | Trung Bình Nhóm |
|-----|---------|-----------------|
| **Khoa Học Tự Nhiên** | Toán, Lý, Hóa, Sinh | 6.28 |
| **Nhân Văn** | Văn, Anh, Lịch Sử | 6.54 |
| **Công Nghệ** | Tin Học | 6.28 |
| **Xã Hội** | Địa Lý | 6.76 |

### 4.2 Phân Tích Theo Nhóm

- **Xã Hội** (Địa Lý) có trung bình cao nhất (6.76) → Học sinh có xu hướng tốt nhất trong lĩnh vực này
- **Nhân Văn** cao thứ hai (6.54) → Lĩnh vực được ưa chuộng
- **Khoa Học Tự Nhiên** thấp nhất (6.28) → Ngành này yêu cầu học sinh chuyên biệt hơn

---

## 5. Phân tích Độ Phân Tán (Variance Analysis)

### 5.1 Hệ Số Biến Thiên (Coefficient of Variation)

| Môn Học | CV (%) | Ý Nghĩa |
|---------|--------|---------|
| **Sinh** | 32.54% | Độ phân tán cao nhất |
| **Lý** | 32.29% | Phân tán cao |
| **Hóa** | 32.02% | Phân tán cao |
| **Tin Học** | 31.81% | Phân tán cao |
| **Lịch Sử** | 31.67% | Phân tán cao |
| **Toán** | 31.60% | Phân tán cao |
| **Văn** | 30.35% | Phân tán trung bình |
| **Địa Lý** | 29.99% | Phân tán trung bình |
| **Anh** | 28.91% | Phân tán vừa phải (thấp nhất) |

**Kết luận:**  
- Tất cả môn học có CV ~28-32%, cho thấy dữ liệu được sinh tạo với phân bố đồng nhất
- Không có môn nào có độ phân tán bất thường

---

## 6. Thống Kê Theo Các Nhóm Điểm

### 6.1 Phân Loại Học Lực (Giả Định)

Dựa trên trung bình của 9 môn:

| Mức Học Lực | Phạm Vi GPA | Mô Tả |
|------------|-----------|-------|
| **Yếu** | 3.0 - 4.5 | Cần cải thiện |
| **Trung Bình Dưới** | 4.5 - 5.5 | Đạt yêu cầu cơ bản |
| **Trung Bình** | 5.5 - 7.0 | Bình thường |
| **Trung Bình Trên** | 7.0 - 8.5 | Khá |
| **Xuất Sắc** | 8.5 - 10.0 | Giỏi |

---

## 7. Độ Cắt (Thresholds) Được Sử Dụng

### 7.1 Ngưỡng Chính cho Từng Ngành

| Ngành | Điều Kiện Chính | Mục Tiêu GPA |
|-------|-----------------|-------------|
| IT | Toán ≥ 7.5, Tin ≥ 7.5, (Toán+Tin+Lý)/3 ≥ 7 | ≥ 7.0 |
| Kỹ Thuật | Toán ≥ 8, Lý ≥ 8 | ≥ 8.0 |
| Y Khoa | Sinh ≥ 7.5, Hóa ≥ 7.5, Lý ≥ 6 | ≥ 7.0 |
| Nông-Lâm-Ngư | Sinh ≥ 7, Địa Lý ≥ 7.5, Hóa ≥ 6 | ≥ 7.0 |
| Luật Pháp | Lịch Sử ≥ 7.5, Văn ≥ 7 | ≥ 7.2 |
| Sư Phạm | Văn ≥ 7, Anh ≥ 7 | ≥ 7.0 |
| Kinh Tế | Toán ≥ 6, Anh ≥ 7, Văn ≥ 5.5 | ≥ 6.5 |
| Du Lịch | Địa Lý ≥ 6.5, Anh ≥ 6.5, Văn ≥ 6 | ≥ 6.5 |

---

## 8. Chất Lượng Dữ Liệu

### 8.1 Kiểm Tra

| Tiêu Chí | Kết Quả | Ghi Chú |
|---------|--------|--------|
| **Giá trị thiếu** | 0 | Dữ liệu hoàn toàn |
| **Giá trị ngoài phạm vi** | 0 | (3.0 - 10.0) |
| **Cân bằng lớp** | Không cân bằng | Tỷ lệ lẻ (11.9%-13.1%) |
| **Độ phân tán** | Tốt | CV ~32% đều |
| **Độc lập dữ liệu** | Tốt | Random seed = 42 |

### 8.2 Kết Luận

**Dữ liệu chất lượng cao (thực tế):**
- Không có lỗi hoặc giá trị thiếu
- Phân bố không cân bằng (giống dữ liệu thực sự từ các trường ĐH)
- Đủ mẫu cho huấn luyện (118K samples)
- Phù hợp cho các mô hình Machine Learning

---

## 9. Sử Dụng Dữ Liệu

### 9.1 Chia Tập Dữ Liệu

| Tập | Số Mẫu | Tỷ Lệ | Mục Đích |
|-----|--------|-------|---------|
| **Training** | 94,759 | 80% | Huấn luyện mô hình |
| **Testing** | 23,690 | 20% | Đánh giá hiệu suất |

### 9.2 Hiệu Suất Mô Hình (Cập Nhật)

| Mô Hình | Độ Chính Xác | Ghi Chú |
|---------|-------------|--------|
| **Random Forest** | 91.77% | 100 trees, depth=15 |
| **Cross-Validation** | 91.56% ± 0.20% | 5-fold CV |
| **Hybrid (ML+Fuzzy)** | ~91.5%* | Kết hợp fuzzy logic |

---

## 10. Tài Liệu Tham Khảo

- [DATASET.md](DATASET.md) - Mô tả chi tiết dữ liệu
- [README.md](README.md) - Hướng dẫn chính
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Hướng dẫn kỹ thuật
- [create_data.py](create_data.py) - Script tạo dữ liệu

---

**Ghi Chú:** File thống kê này được tạo tự động từ dữ liệu thực. Cập nhật sau mỗi lần tạo dữ liệu mới.

Kế Hoạch Phân Chia Công Việc - 2 Người, 3 Tuần

Dự án: Hệ Thống Gợi Ý Ngành Học Hybrid v1.2 (Bảo trì & Nâng cao)
Thời gian: 3 tuần (21 ngày)  
Nhân lực: 2 người  
Deadline: Ngày 25/04/2026

Cấu trúc hiện tại:
- app.py (Streamlit UI với 3 tabs)
- hybrid_engine.py (ML + Fuzzy Logic)
- config.py, train_model.py, create_data.py

---

Phân Công

| Hàng | Người | Trách Nhiệm |
|--------|-------|-----------|
| Hoàng | Backend/ML | Tối ưu ML, Hiệu suất, Các tính năng |
| Long | Frontend | Giao diện, Thiết kế responsive, Biểu đồ |

---

TUẦN 1: Tối ưu Code & Sửa Lỗi

### Hoàng (Backend/ML)
- [ ] **W1.A1** - Kiểm tra & Tái cấu trúc Code
  - [ ] Kiểm tra logic hybrid_engine.py
  - [ ] Thêm type hints & docstrings
  - [ ] Tối ưu imports
  - [ ] Thời gian: 1.5 ngày
  - [ ] Kết quả: Code sạch, tài liệu tốt
  
- [ ] W1.A2 - Kiểm tra Hiệu suất
  - [ ] Đo hiệu suất hybrid_engine
  - [ ] Kiểm tra với các input khác nhau
  - [ ] Kiểm tra sử dụng bộ nhớ
  - [ ] Thời gian: 1.5 ngày
  - [ ] Kết quả: Báo cáo, tối ưu
  
- [ ] W1.A3 - Nâng cao Tính năng
  - [ ] Xuất kết quả dạng JSON/CSV
  - [ ] Thêm điểm tin cậy
  - [ ] Thêm các test case mẫu
  - [ ] Thời gian: 2 ngày
  - [ ] Kết quả: Tính năng mới trong hybrid_engine

### Long (Frontend)
- [ ] W1.B1 - Kiểm tra Giao diện
  - [ ] Kiểm tra cấu trúc app.py
  - [ ] Kiểm tra style CSS
  - [ ] Kiểm tra trên màn hình khác nhau
  - [ ] Thời gian: 1 ngày
  - [ ] Kết quả: Danh sách cải thiện UX
  
- [ ] W1.B2 - Dọn dẹp Code & Type Hints
  - [ ] Thêm type hints cho các function app.py
  - [ ] Tối ưu components giao diện
  - [ ] Dọn dẹp CSS
  - [ ] Thời gian: 2 ngày
  - [ ] Kết quả: Code sạch, có tài liệu
  
- [ ] W1.B3 - Thiết kế Responsive
  - [ ] Mobile-first CSS
  - [ ] Grid layout responsive
  - [ ] Kiểm tra trên màn hình nhỏ
  - [ ] Thời gian: 1.5 ngày
  - [ ] Kết quả: Giao diện thân thiện với di động

### Điểm Kiểm tra (Cuối tuần 1 - Ngày 12/4)
- [ ] Tất cả code đã tái cấu trúc & có type hints
- [ ] Hiệu suất đã đo
- [ ] Giao diện responsive trên tất cả thiết bị
- [ ] Sửa lỗi hoàn tất

---

TUẦN 2: Tính năng & Biểu đồ

### Hoàng (Backend/ML)
- [ ] W2.A1 - Tính năng Nâng cao
  - [ ] Dự đoán multi-input (lưu kết quả tạm thời)
  - [ ] Chế độ so sánh (2 hồ sơ)
  - [ ] Thống kê về khuyến nghị
  - [ ] Thời gian: 2.5 ngày
  - [ ] Kết quả: Tính năng dự đoán mới
  
- [ ] W2.A2 - Kiểm tra & Đảm bảo Chất lượng
  - [ ] Unit tests cho hybrid_engine
  - [ ] Kiểm tra các trường hợp biên
  - [ ] Kiểm tra xác thực
  - [ ] Thời gian: 1.5 ngày
  - [ ] Kết quả: test_hybrid_engine.py

### Long (Frontend)
- [ ] W2.B1 - Biểu đồ Nâng cao
  - [ ] Cải thiện Radar Chart (màu sắc, tương tác)
  - [ ] Thêm biểu đồ tập nhiệt
  - [ ] Thêm biểu đồ tỷ lệ thành công
  - [ ] Thời gian: 2 ngày
  - [ ] Kết quả: Biểu đồ tốt hơn với Plotly
  
- [ ] W2.B2 - Cải thiện Giao diện
  - [ ] Thêm nút tắt sáng (dark mode)
  - [ ] Cải thiện loại màu
  - [ ] Thêm animations/transitions
  - [ ] Thông báo lỗi tốt hơn
  - [ ] Thời gian: 2 ngày
  - [ ] Kết quả: Giao diện nâng cao

### Điểm Kiểm tra (Cuối tuần 2 - Ngày 19/4)
- [ ] Tính năng mới hoạt động
- [ ] Biểu đồ nâng cao hoàn tất
- [ ] Unit tests đang chạy
- [ ] Chế độ tắt sáng đang hoạt động

---

TUẦN 3: Kiểm tra, Tài liệu & Triển khai

### Hoàng (Backend/ML)
- [ ] W3.A1 - Kiểm tra Tích hợp
  - [ ] Kiểm tra quy trình đầu cuối
  - [ ] Kiểm tra với dữ liệu thực tế
  - [ ] Hiệu suất dưới tải nặng
  - [ ] Thời gian: 1.5 ngày
  - [ ] Kết quả: Kết quả kiểm tra toàn diện
  
- [ ] W3.A2 - Tài liệu
  - [ ] Cập nhật README.md với các tính năng v1.2
  - [ ] Tạo CHANGELOG.md
  - [ ] Thêm ví dụ về mã
  - [ ] Thời gian: 1 ngày
  - [ ] Kết quả: Tài liệu đầy đủ

### Long (Frontend)
- [ ] W3.B1 - Kiểm tra Trên các Trình duyệt
  - [ ] Kiểm tra Chrome, Firefox, Safari, Edge
  - [ ] Kiểm tra trên các HĐH khác nhau (Windows, Mac, Linux)
  - [ ] Ghi chép khả năng tương thích
  - [ ] Thời gian: 1 ngày
  - [ ] Kết quả: Báo cáo khả năng tương thích
  
- [ ] W3.B2 - Tinh chỉnh Giao diện & Sửa Lỗi
  - [ ] Sửa các vấn đề giao diện còn lại
  - [ ] Tinh chỉnh UX cuối cùng
  - [ ] Tối ưu hóa hiệu suất
  - [ ] Thời gian: 1.5 ngày
  - [ ] Kết quả: Giao diện sản xuất

### Cả hai (Hoàng & Long)
- [ ] **W3.BOTH.1** - Kiểm tra Cuối cùng
  - [ ] Kiểm tra quy trình ứng dụng đầy đủ
  - [ ] Các kịch bản kiểm tra chấp nhận người dùng
  - [ ] Kiểm tra hiệu suất
  - [ ] Thời gian: 1 ngày
  - [ ] Kết quả: Báo cáo kiểm tra cuối cùng

- [ ] **W3.BOTH.2** - Triển khai
  - [ ] Commit & tag git cuối cùng
  - [ ] Tạo phát hành GitHub (v1.2)
  - [ ] Cập nhật chi tiết triển khai
  - [ ] Thời gian: 0.5 ngày
  - [ ] Kết quả: v1.2 ĐÃ PHÁT HÀNH

### Danh sách Kiểm tra Cuối cùng (Ngày 25/4)
- [ ] Tất cả code được commit & ghi chép
- [ ] Tất cả kiểm tra đang chạy
- [ ] Tương thích trên các trình duyệt
- [ ] Chế độ tắt sáng hoạt động
- [ ] Hiệu suất được tối ưu hóa
- [ ] README & CHANGELOG được cập nhật
- [ ] Phát hành GitHub được tạo
- [ ] v1.2 TRỰC TIẾP

---

## Công cụ & Tài nguyên

| Công cụ | Mục đích | Chủ sở hữu | Thiết lập vào |
|--------|---------|-----------|-----------|
| GitHub | Version control | Cả hai | W1 Ngày 1 |
| Pytest | Unit testing | A | W2 |
| Streamlit | Frontend | B | Đã có |
| Plotly | Visualizations | B | W2 |
| Docker | Optional deployment | A | W3 |

---

## Tóm Tắt Kết quả

**Hoàng (Backend/ML):**
- hybrid_engine.py đã được tối ưu hóa
- Các điểm chuẩn về hiệu suất
- Các tính năng dự đoán mới
- Kiểm tra đơn vị (>70% bảo phủ)
- Tài liệu đầy đủ

**Long (Frontend):**
- Thiết kế phản hồi (di động, máy tính bảng, máy tính để bàn)
- Nút chuyển đổi chế độ tắt sáng
- Trực quan hóa nâng cao
- Kiểm tra trên các trình duyệt
- Giao diện sản xuất

**Kết quả:**
- Phát hành v1.2 trên GitHub
- Codebase sạch, ghi chép đầy đủ
- Cải thiện hiệu suất
- UX tốt hơn trong ứng dụng Streamlit


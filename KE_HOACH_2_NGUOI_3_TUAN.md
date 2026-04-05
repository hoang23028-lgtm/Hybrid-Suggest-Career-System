Kế Hoạch Phân Chia Công Việc - 2 Người, 3 Tuần

Dự án: Hệ Thống Gợi Ý Ngành Học Hybrid v1.1  
Thời gian: 3 tuần (21 ngày)  
Nhân lực: 2 người  
Deadline: Ngày 25/04/2026

---

Phân Công

| Vai Trò | Người | Trách Nhiệm |
|--------|-------|-----------|
| Hoàng | Backend/ML | AI, API, Cơ sở dữ liệu |
| Long | Frontend | Giao diện, Triển khai, Tài liệu |

---

TUẦN 1: Chuẩn Bị & Triển Khai Cơ Bản

### Developer A - Hoàng (Backend/ML)
- [ ] **W1.A1** - Tối ưu hóa Mô hình ML
  - [ ] Thử nghiệm các siêu tham số khác nhau
  - [ ] Target: Nâng độ chính xác từ 82% → 85%
  - [ ] Thời gian: 3 ngày
  - [ ] Output: `train_model_v2.py`
  
- [ ] W1.A2 - Cải thiện Hệ thống Fuzzy
  - [ ] Điều chỉnh các hàm membership
  - [ ] Thêm điều chỉnh quy tắc động
  - [ ] Thời gian: 2 ngày
  - [ ] Output: `hybrid_engine_v2.py`
  
- [ ] W1.A3 - Thiết lập Cơ sở Dữ liệu
  - [ ] Thiết kế schema (SQLite/PostgreSQL)
  - [ ] Tạo lớp quản lý dữ liệu
  - [ ] Thời gian: 2 ngày
  - [ ] Output: `database.py`, file `.db`

### Developer B (Frontend)
- [ ] W1.B1 - Kiểm tra & Tối ưu Code
  - [ ] Kiểm tra phong cách code
  - [ ] Thêm type hints
  - [ ] Thời gian: 2 ngày
  - [ ] Output: `app_refactored.py`
  
- [ ] W1.B2 - Nâng cấp Giao diện Giai đoạn 1
  - [ ] Thêm Chế độ Tối (Dark Mode)
  - [ ] Cải thiện thiết kế đáp ứng
  - [ ] Thêm hiệu ứng chuyển động
  - [ ] Thời gian: 3 ngày
  - [ ] Output: `app.py` cập nhật CSS

### Điểm Đồng bộ (Cuối tuần 1)
- [ ] kiểm tra code
- [ ] Hợp nhất PR 
- [ ] Kiểm tra trên staging

---

TUẦN 2: Phát Triển & Tích Hợp Nâng cao

### Developer A (Backend/ML)
- [ ] W2.A1 - Thêm Bộ nhớ đệm & Tối ưu hóa
  - [ ] Triển khai Redis caching (nếu cần)
  - [ ] Tối ưu hóa hiệu suất query
  - [ ] Thời gian: 2 ngày
  - [ ] Output: `cache_layer.py`
  
- [ ] W2.A2 - Phát triển API (FastAPI)
  - [ ] Tạo API REST endpoints
  - [ ] Thêm xác thực (authentication)
  - [ ] Tài liệu API (Swagger)
  - [ ] Thời gian: 3 ngày
  - [ ] Output: `api.py`, `/api/docs`

- [ ] W2.A3 - Tính Năng Phân tích Dữ liệu
  - [ ] Quản lý hồ sơ học sinh
  - [ ] Lịch sử khuyến nghị
  - [ ] API thống kê & báo cáo
  - [ ] Thời gian: 2 ngày

### Developer B (Frontend)
- [ ] W2.B1 - Nâng cấp Ứng dụng Đa trang
  - [ ] Thêm trang mới: Lịch sử, Thống kê, Hồ sơ
  - [ ] Cải thiện điều hướng
  - [ ] Thời gian: 2 ngày
  - [ ] Output: Các trang mới trong `app.py`

- [ ] W2.B2 - Tối ưu hóa cho Thiết bị Di động
  - [ ] Kiểm tra trên thiết bị di động
  - [ ] Sửa vấn đề bố cục
  - [ ] Thêm tối ưu hóa di động
  - [ ] Thời gian: 2 ngày

- [ ] W2.B3 - Nâng cấp Hình ảnh hóa Dữ liệu
  - [ ] Thêm loại biểu đồ mới
  - [ ] Tính năng tương tác
  - [ ] Xuất ra PDF/Excel
  - [ ] Thời gian: 1 ngày

### Công việc Tích hợp 
- [ ] W2.SYNC - Tích hợp API
  - [ ] Long: Tích hợp API call vào Frontend
  - [ ] Hoàng: Kiểm tra & tối ưu endpoints
  - [ ] Thời gian: 1 ngày
  - [ ] Output: Luồng end-to-end hoạt động

---

TUẦN 3: Kiểm tra, Triển khai & Tài liệu

### 🧪 Kiểm tra (Song song)

#### Hoàng - Kiểm tra Backend
- [ ] W3.A1 - Unit Tests (ML & API)
  - [ ] Kiểm tra độ chính xác dự đoán ML
  - [ ] Kiểm tra API endpoints
  - [ ] Kiểm tra các trường hợp biên
  - [ ] Thời gian: 2 ngày
  - [ ] Output: `tests/test_ml.py`, `tests/test_api.py`
  - [ ] Target: 80%+ phủ code

- [ ] W3.A2 - Kiểm tra Hiệu suất
  - [ ] Load testing API
  - [ ] Benchmark mô hình ML
  - [ ] Phân tích bộ nhớ
  - [ ] Thời gian: 1 ngày
  - [ ] Output: `PERFORMANCE_REPORT.md`

#### Long - Kiểm tra Frontend
- [ ] W3.B1 - Kiểm tra Giao diện/UX
  - [ ] Kiểm tra trên các trình duyệt
  - [ ] Kiểm tra khả năng tiếp cận (WCAG)
  - [ ] Kiểm tra hiệu suất
  - [ ] Thời gian: 2 ngày
  - [ ] Output: Danh sách vấn đề, sửa chữa

- [ ] **W3.B2** - Sửa Lỗi & Hoàn thiện
  - [ ] Sửa các vấn đề được báo cáo
  - [ ] Điều chỉnh giao diện cuối cùng
  - [ ] Tối ưu hóa hiệu suất
  - [ ] Thời gian: 1 ngày

### 📚 Tài liệu (Cả hai)
- [ ] **W3.BOTH.1** - Viết Tài liệu
  - Developer A: Tài liệu API, Kiến trúc kỹ thuật
  - Developer B: Hướng dẫn người dùng, Hướng dẫn cài đặt
  - Thời gian: 2 ngày
  - Output: Tài liệu hoàn chỉnh trong `/docs`

- [ ] **W3.BOTH.2** - README & CHANGELOG
  - [ ] Cập nhật README.md
  - [ ] Tạo CHANGELOG.md
  - [ ] Thêm CONTRIBUTING.md
  - [ ] Thời gian: 1 ngày

### 🚀 Triển khai (Cả hai)
- [ ] **W3.BOTH.3** - Chuẩn bị Triển khai
  - Developer A: Thiết lập môi trường sản xuất, migrations
  - Developer B: Thiết lập CI/CD pipeline
  - Thời gian: 1 ngày

- [ ] **W3.BOTH.4** - Triển khai Cuối cùng
  - [ ] Triển khai lên sản xuất
  - [ ] Giám sát lỗi
  - [ ] Kiểm tra sản xuất
  - [ ] Thời gian: 1 ngày
  - [ ] Output: Ứng dụng hoạt động tại URL sản xuất

### 🎯 Danh sách Kiểm tra Cuối cùng (Ngày 21)
- [ ] Tất cả kiểm tra vượt
- [ ] Phủ code > 80%
- [ ] Tất cả PR đã hợp nhất
- [ ] Tài liệu hoàn chỉnh
- [ ] Server chạy mượt mà
- [ ] README được cập nhật
- [ ] GitHub releases được tạo
- [ ] Cuộc họp nhóm & ghi chú phát hành

---

## 📌 Phụ Thuộc Công việc & Điểm Tắc nghẽn

```
Tuần 1:
├── A1 (Tối ưu ML)
├── A2 (Hệ thống Fuzzy) → Phụ thuộc vào A1
├── A3 (Cơ sở dữ liệu)
├── B1 (Kiểm tra code) → Có thể bắt đầu bất kỳ lúc nào
└── B2 (Giao diện) → Có thể bắt đầu bất kỳ lúc nào

Tuần 2:
├── A1 (Bộ nhớ đệm) → Phụ thuộc vào W1.A3
├── A2 (API) → Phụ thuộc vào W1.A1, W1.A2
└── B1 (Đa trang) → Phụ thuộc vào A2 API endpoints
└── SYNC (Tích hợp API) → Phụ thuộc vào A2, B1

Tuần 3:
├── A1 (Test backend) → Phụ thuộc vào W2.A2
├── B1 (Test frontend) → Phụ thuộc vào W2.B2
└── BOTH.3, BOTH.4 → Tất cả kiểm tra phải vượt
```

---

## � Buổi Dev Mỗi Tuần

**Buổi 1:** Thứ 3, 10:00-12:00 (Review targets)
**Buổi 2:** Thứ 6, 14:00-16:00 (Sync & Demo)

## �🔄 Standup Hàng ngày (15 phút)

**Thời gian:** 10:00 sáng hàng ngày

```
Developer A:
- Tập trung hôm nay
- Vấn đề cản trở
- Kế hoạch ngày mai

Developer B:
- Tập trung hôm nay
- Vấn đề cản trở
- Kế hoạch ngày mai

Chung:
- Vấn đề đồng bộ
- Demo tính năng
```

---

## Chỉ Số Chất Lượng

| Chỉ Số | Mục Tiêu | Tuần |
|--------|----------|------|
| **Phủ Code** | 80%+ | W3 |
| **Độ Chính xác ML** | 85%+ | W1 |
| **Thời Gian Phản Hồi API** | <200ms | W3 |
| **Hiệu Suất UI** | LCP <2s | W3 |
| **Tài Liệu** | Hoàn chỉnh | W3 |

---

## 📦 Deliverables Theo Tuần

### Cuối Tuần 1
- [ ] Mô hình ML v2 (85% độ chính xác)
- [ ] Hệ thống Fuzzy cải thiện
- [ ] Schema cơ sở dữ liệu
- [ ] Code giao diện được tái cấu trúc
- [ ] Chế độ tối hoạt động

### Cuối Tuần 2
- [ ] FastAPI hoạt động
- [ ] Ứng dụng đa trang hoạt động
- [ ] Đáp ứng di động
- [ ] API tích hợp đầy đủ

### Cuối Tuần 3 (Cuối cùng)
- [ ] Triển khai sản xuất
- [ ] Tất cả kiểm tra vượt (>80% phủ)
- [ ] Tài liệu hoàn chỉnh
- [ ] GitHub release v2.0
- [ ] Hoạt động tại URL sản xuất

---

## 🛠️ Công cụ & Tài nguyên

| Công cụ | Mục đích | Chủ sở hữu | Thiết lập vào |
|--------|---------|-----------|-----------|
| GitHub | Kho mã | Cả hai | W1 Ngày 1 |
| Jira/Trello | Theo dõi công việc | Cả hai | W1 Ngày 1 |
| Docker | Containerization | A | W2 |
| PostgreSQL | Cơ sở dữ liệu | A | W1 |
| Pytest | Kiểm tra backend | A | W3 |
| Pytest-cov | Phủ code | A | W3 |
| Streamlit Cloud | Triển khai | B | W3 |
| GitHub Actions | CI/CD | B | W2 |

---

## 💰 Quản lý Rủi ro

| Rủi ro | Tác động | Giảm thiểu |
|--------|----------|-----------|
| Tối ưu ML không đạt 85% | Cao | Bắt đầu phân tích dự phòng Ngày 2 |
| Vấn đề migration DB | Cao | Kiểm tra trên staging trước, tạo rollback scripts |
| Độ trễ tích hợp API | Trung bình | Tạo mock endpoints sớm |
| Vấn đề responsive di động | Thấp | Sử dụng CSS frameworks (Tailwind) |
| Tài liệu không hoàn chỉnh | Thấp | Gán người kiểm tra tài liệu |

---

## 📞 Giao Tiếp

- **Standup Hàng ngày:** 10:00 sáng (15 phút)
- **Kiểm tra Kỹ thuật:** Thứ 4 3:00 chiều (30 phút)
- **Xem xét Sprint:** Thứ 6 4:00 chiều (1 giờ)
- **Khẩn cấp:** Slack real-time

---

## Tiêu chuẩn Thành Công

**Tuần 1 Thành Công:**
- Độ chính xác ML cải thiện đến 85%+
- Cơ sở dữ liệu hoạt động
- Giao diện được tái cấu trúc & chế độ tối sẵn sàng
- Không có vấn đề blockers

**Tuần 2 Thành Công:**
- Tất cả API endpoints hoạt động
- Frontend tích hợp đầy đủ
- Đáp ứng di động
- Kiểm tra hiệu suất vượt

**Tuần 3 Thành Công (CUỐI CÙNG):**
- **Triển khai lên sản xuất**
- Tất cả kiểm tra vượt (80%+ phủ)
- Tài liệu hoàn chỉnh
- Không có vấn đề đã biết
- Nhóm sẵn sàng cho sprint tiếp theo

---

**Lần cập nhật cuối cùng:** 2026-04-05  
**Trạng thái:** Sẵn sàng Thực hiện  
**Xem xét tiếp theo:** 2026-04-07 (Sau hoàn thành W1)

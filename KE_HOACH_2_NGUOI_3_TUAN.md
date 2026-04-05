Kế Hoạch Phân Chia Công Việc - 2 Người, 3 Tuần

Dự án: Hệ Thống Gợi Ý Ngành Học Hybrid v2.0 (Database + API + Multi-page UI)
Thời gian: 3 tuần (21 ngày)  
Nhân lực: 2 người  
Deadline: Ngày 25/04/2026

---

Phân Công

| Vai Trò | Người | Trách Nhiệm |
|--------|-------|-----------|
| Hoàng | Backend/ML | Database, API (FastAPI), Deployment |
| Long | Frontend | Multi-page UI (Streamlit), Responsive Design |

---

TUẦN 1: Chuẩn Bị & Thiết lập Database

### Hoàng (Backend/ML)
- [ ] **W1.A1** - Database Design & Implementation
  - [ ] Thiết kế schema SQLite (3 bảng: Profile, History, Stats)
  - [ ] Tạo `database.py` với CRUD operations
  - [ ] Thiết lập migrations
  - [ ] Thời gian: 3 ngày
  - [ ] Output: `database.py`, SQLite schema, sample queries
  - [ ] Bảng cần: students (profile), predictions (history), recommendations (stats)
  
- [ ] W1.A2 - API Scaffold & Core Setup
  - [ ] Khởi tạo FastAPI project
  - [ ] Setup project structure: routes, models, schemas
  - [ ] Tầng xác thực cơ bản
  - [ ] Thời gian: 2 ngày
  - [ ] Output: `api.py`, `models.py`, `schemas.py`

### Long (Frontend)
- [ ] W1.B1 - Code Review & Type Hints
  - [ ] Review `app.py` và hybrid_engine logic
  - [ ] Thêm type hints cho main functions
  - [ ] Tối ưu imports
  - [ ] Thời gian: 1 ngày
  - [ ] Output: `app.py` with type hints
  
- [ ] W1.B2 - Multi-page UI Scaffold
  - [ ] Tách UI thành 4 trang: Home, Analysis, History, Profile
  - [ ] Setup Streamlit multipage navigation
  - [ ] Tạo layout base và responsive CSS
  - [ ] Thời gian: 2 ngày
  - [ ] Output: pages/ folder với 4 files

### Điểm Đồng bộ (Cuối tuần 1 - Ngày 12/4)
- [ ] Database schema finalized & tested
- [ ] API project initialized & routes setup
- [ ] Multi-page structure ready
- [ ] All code committed & PR reviewed

---

TUẦN 2: Phát Triển API & Multi-page UI

### Hoàng (Backend/ML)
- [ ] W2.A1 - API Endpoints Implementation
  - [ ] POST /predict - Gợi ý sử dụng hybrid_engine
  - [ ] POST /profile - Lưu hồ sơ học sinh
  - [ ] GET /history - Lấy lịch sử dự đoán
  - [ ] GET /stats - Thống kê truy cập
  - [ ] Thời gian: 3 ngày
  - [ ] Output: 4 endpoints + Swagger docs
  - [ ] Mỗi endpoint kết nối với database & hybrid_engine
  
- [ ] W2.A2 - API Testing & Documentation
  - [ ] Unit tests cho mỗi endpoint
  - [ ] Integration tests
  - [ ] Tài liệu API (Swagger OpenAPI)
  - [ ] Thời gian: 2 ngày
  - [ ] Output: test files, `/api/docs`

### Long (Frontend)
- [ ] W2.B1 - Multi-page Pages Implementation
  - [ ] pages/home.py - Trang chính (dự đoán)
  - [ ] pages/analysis.py - Phân tích chi tiết
  - [ ] pages/history.py - Lịch sử dự đoán (gọi API GET /history)
  - [ ] pages/profile.py - Hồ sơ học sinh (gọi API POST /profile)
  - [ ] Thời gian: 3 ngày
  - [ ] Output: 4 trang UI hoàn chỉnh

- [ ] W2.B2 - API Integration & Responsive UI
  - [ ] Gọi API endpoints từ mỗi trang
  - [ ] Xử lý loading/error states
  - [ ] CSS responsive cho mobile
  - [ ] Thời gian: 2 ngày
  - [ ] Output: All pages connected to API

### Điểm Đồng bộ (Cuối tuần 2 - Ngày 19/4)
- [ ] API endpoints fully functional
- [ ] Multi-page UI connected to API
- [ ] Database storing predictions correctly
- [ ] End-to-end workflow tested

---

TUẦN 3: Testing, Documentation & Deployment

### Kiểm tra (Song song)

#### Hoàng - Backend Testing
- [ ] W3.A1 - Unit & Integration Tests
  - [ ] Test các API endpoints
  - [ ] Test database operations
  - [ ] Test hybrid_engine integration
  - [ ] Thời gian: 2 ngày
  - [ ] Output: `tests/test_api.py`, `tests/test_db.py`
  - [ ] Target: 70%+ code coverage

- [ ] W3.A2 - Performance & Deployment Prep
  - [ ] Performance testing
  - [ ] Environment setup (production)
  - [ ] Database migrations ready
  - [ ] Thời gian: 1 ngày
  - [ ] Output: Deployment checklist

#### Long - Frontend Testing
- [ ] W3.B1 - UI/UX Testing
  - [ ] Kiểm tra trên Chrome, Firefox, Safari
  - [ ] Kiểm tra responsive (desktop, tablet, mobile)
  - [ ] Kiểm tra UX flow
  - [ ] Thời gian: 1.5 ngày
  - [ ] Output: Bug report & fixes

- [ ] W3.B2 - Bug Fixes & Polish
  - [ ] Sửa lỗi giao diện
  - [ ] Tối ưu hóa hiệu suất
  - [ ] Polish UI/UX
  - [ ] Thời gian: 1.5 ngày

### Tài liệu (Cả hai)
- [ ] **W3.BOTH.1** - Update Documentation
  - [ ] Cập nhật README.md (v2.0 features)
  - [ ] Tạo API_DOCUMENTATION.md
  - [ ] Tạo DEPLOYMENT_GUIDE.md
  - [ ] Tạo CHANGELOG.md
  - [ ] Thời gian: 1.5 ngày

- [ ] **W3.BOTH.2** - Deployment Guide
  - [ ] Setup instructions
  - [ ] Environment variables
  - [ ] Database setup
  - [ ] Thời gian: 0.5 ngày

### Triển khai (Cả hai)
- [ ] **W3.BOTH.3** - Production Deployment
  - [ ] Deploy API (Heroku/Railway/Local)
  - [ ] Deploy Frontend (Streamlit Cloud/Heroku)
  - [ ] Setup database in production
  - [ ] Thời gian: 1 ngày

- [ ] **W3.BOTH.4** - Final Verification
  - [ ] Kiểm tra production environment
  - [ ] Monitor logs
  - [ ] Test production APIs
  - [ ] Thời gian: 0.5 ngày
  - [ ] Output: v2.0 LIVE

### Danh sách Kiểm tra Cuối cùng (Ngày 25/4)
- [ ] Database connected & working
- [ ] API endpoints tested (70%+ coverage)
- [ ] Multi-page UI functional
- [ ] API & Frontend deployed
- [ ] Documentation complete
- [ ] README v2.0 updated
- [ ] CHANGELOG.md created
- [ ] GitHub tag & release created


## Công cụ & Tài nguyên

| Công cụ | Mục đích | Chủ sở hữu | Thiết lập vào |
|--------|---------|-----------|-----------|
| GitHub | Kho mã | Cả hai | W1 Ngày 1 |
| Jira/Trello | Theo dõi công việc | Cả hai | W1 Ngày 1 |
| SQLite | Cơ sở dữ liệu | A | W1 |
| FastAPI | API framework | A | W2 |
| Pytest | Kiểm tra backend | A | W3 |
| Streamlit | Frontend | B | W1 |
| Docker | Optional containerization | A | W3 |
| Heroku/Railway | Deployment | A/B | W3 |

---


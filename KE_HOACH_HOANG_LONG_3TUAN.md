# Kế Hoạch Phân Chia Công Việc - HOÀNG & LONG - 3 Tuần

**Dự án:** Hệ Thống Gợi Ý Ngành Học Hybrid v1.1  
**Thời gian:** 3 tuần (21 ngày)  
**Nhân lực:** 2 người  
**Dev 1:** Hoàng (Backend/ML)  
**Dev 2:** Long (Frontend)  
**Deadline:** Ngày 25/04/2026

---

## 👥 Phân Công Cụ Thể

| Vai Trò | Tên | Trách Nhiệm |
|--------|-----|-----------|
| **Developer A** | **Hoàng** | ML optimization, API, Database, Backend |
| **Developer B** | **Long** | UI/UX, Frontend, Deployment, Documentation |

---

## Buổi Dev Mỗi Tuần

| Buổi | Thời gian | Nội dung |
|------|----------|---------|
| **Buổi 1** | Thứ 3, 10:00-12:00 | Review targets & problem-solving |
| **Buổi 2** | Thứ 6, 14:00-16:00 | Sync & Demo kết quả |
| **Standup** | Hàng ngày 10:00 | 15 phút daily sync |

---

## TUẦN 1: Chuẩn Bị & Triển Khai Cơ Bản

### 🔧 Hoàng (Backend/ML)

**Buổi 1 - Thứ 3 (W1.1):**
- [ ] **ML Model Optimization**
  - Phân tích hiệu suất cơ sở (82%)
  - Thử nghiệm hyperparameters
  - File: `train_model_v2.py`
  - **Target:** 85% accuracy
  - **Thời gian:** 1.5 ngày

**Buổi 2 - Thứ 6 (W1.2):**
- [ ] **Fuzzy System & Database**
  - Cải thiện hàm Gaussian
  - Thiết kế schema DB
  - File: `hybrid_engine_v2.py`, `database.py`
  - **Thời gian:** 1.5 ngày + 2 ngày
  - **Output:** ML v2, DB schema ready

### 🎨 Long (Frontend)

**Buổi 1 - Thứ 3 (W1.1):**
- [ ] **Code Review & Refactoring**
  - Kiểm tra phong cách code
  - Thêm type hints
  - File: `app_refactored.py`
  - **Thời gian:** 1.5 ngày

**Buổi 2 - Thứ 6 (W1.2):**
- [ ] **UI Enhancement**
  - Dark mode implementation
  - Responsive design
  - Smooth animations
  - **Thời gian:** 3 ngày
  - **Output:** Better UI/UX

### 📊 Tuần 1 Deliverables
- ✅ ML accuracy 85%
- ✅ Fuzzy system improved
- ✅ Database schema
- ✅ Code refactored
- ✅ Dark mode ready

---

## TUẦN 2: Phát Triển & Tích Hợp Nâng Cao

### 🔧 Hoàng (Backend/ML)

**Buổi 1 - Thứ 3 (W2.1):**
- [ ] **API Development Part 1**
  - Tạo REST endpoints (predict, history, stats)
  - Request validation
  - File: `api.py` (part 1)
  - **Thời gian:** 2 ngày

**Buổi 2 - Thứ 6 (W2.2):**
- [ ] **API Development Part 2 & Caching**
  - Hoàn thiện endpoints
  - Thêm caching layer
  - API documentation
  - File: `api.py` (complete), `cache.py`
  - **Thời gian:** 2 ngày + 1 ngày
  - **Output:** API fully working

### 🎨 Long (Frontend)

**Buổi 1 - Thứ 3 (W2.1):**
- [ ] **Multi-page App Development**
  - History page
  - Statistics page
  - Profile page
  - Navigation updates
  - **Thời gian:** 2 ngày

**Buổi 2 - Thứ 6 (W2.2):**
- [ ] **Mobile & API Integration**
  - Mobile responsiveness
  - API call integration
  - Loading/error states
  - **Thời gian:** 2 ngày + 2 ngày
  - **Output:** Frontend fully connected

### 📊 Tuần 2 Deliverables
- ✅ FastAPI working
- ✅ Multi-page app functional
- ✅ Mobile responsive
- ✅ API integrated end-to-end

---

## TUẦN 3: Testing, Deployment & Documentation

### 🔧 Hoàng (Backend/ML)

**Buổi 1 - Thứ 3 (W3.1):**
- [ ] **Backend Testing & Documentation**
  - Unit tests (test_ml.py, test_api.py)
  - Performance testing
  - Target: 80%+ coverage
  - File: `/tests/**`, `PERFORMANCE_REPORT.md`
  - **Thời gian:** 2 ngày

**Buổi 2 - Thứ 6 (W3.2):**
- [ ] **Documentation & Production Deployment**
  - Technical documentation
  - Deployment setup
  - Backend goes live
  - File: `/docs/technical.md`, deployment scripts
  - **Thời gian:** 2 ngày + 1 ngày
  - **Output:** Backend in production ✅

### 🎨 Long (Frontend)

**Buổi 1 - Thứ 3 (W3.1):**
- [ ] **Frontend Testing & Polish**
  - Cross-browser testing
  - Accessibility check
  - Bug fixes
  - **Thời gian:** 2 ngày

**Buổi 2 - Thứ 6 (W3.2):**
- [ ] **Documentation & Deployment**
  - User guide
  - README update
  - CI/CD setup
  - Frontend deployment
  - File: `/docs/user_guide.md`, README.md, CHANGELOG.md
  - **Thời gian:** 2 ngày + 2 ngày
  - **Output:** Frontend in production ✅

### 📊 Tuần 3 Deliverables
- ✅ All tests passing (80%+)
- ✅ Backend in production
- ✅ Frontend in production
- ✅ Documentation complete
- ✅ CHANGELOG created
- LIVE!

---

## 📊 Chi Tiết Công Việc Hàng Tuần

### TUẦN 1

| Ngày | Hoàng (Backend/ML) | Long (Frontend) |
|------|-------------------|-----------------|
| T2 | Setup, ML testing | Setup, code review |
| **T3** | **Buổi 1: ML 85%, DB schema** | **Buổi 1: Code refactor** |
| T4 | Fuzzy system, DB setup | UI enhancement |
| T5 | DB finalization | UI polish |
| **T6** | **Buổi 2: DB ready** | **Buổi 2: Dark mode ready** |
| T7 | Review & merge | Review & merge |

**Output:** ML v2, DB, Refactored UI ✅

### TUẦN 2

| Ngày | Hoàng (Backend/ML) | Long (Frontend) |
|------|-------------------|-----------------|
| T2 | API planning | Multi-page planning |
| **T3** | **Buổi 1: APIs endpoints** | **Buổi 1: History, Stats pages** |
| T4 | API testing | Mobile optimization |
| T5 | Caching, validation | API integration |
| **T6** | **Buổi 2: API complete** | **Buổi 2: Frontend-API connected** |
| T7 | Integration testing | UI testing |

**Output:** API working, UI integrated, Mobile ready ✅

### TUẦN 3

| Ngày | Hoàng (Backend/ML) | Long (Frontend) |
|------|-------------------|-----------------|
| T2 | Unit tests prep | UI tests prep |
| **T3** | **Buổi 1: Tests, perf report** | **Buổi 1: UI tests, fixes** |
| T4 | Tech docs | User guide, setup |
| T5 | Deploy setup | CI/CD setup |
| **T6** | **Buổi 2: Backend LIVE** | **Buổi 2: Frontend LIVE** |
| T7 | Final check | CHANGELOG, release |

**Output:** PRODUCTION LIVE

---

## 📞 Giao Tiếp & Meeting

### Hàng ngày
- **Daily Standup:** 10:00 (15 phút)
  - Hoàng: Hôm nay focus gì, vấn đề gì, ngày mai làm gì
  - Long: Hôm nay focus gì, vấn đề gì, ngày mai làm gì

### Hàng tuần
- **Buổi 1 - Thứ 3, 10:00-12:00 (Review & Planning)**
  - Hoàng: Báo cáo progress, blockers
  - Long: Báo cáo progress, blockers
  - Cả hai: Lên kế hoạch cho nửa tuần tiếp
  
- **Buổi 2 - Thứ 6, 14:00-16:00 (Demo & Sync)**
  - Demo tính năng mới
  - Code review
  - Merge PRs
  - Lên kế hoạch tuần tiếp

---

## ✅ Chỉ Số Chất Lượng

| Chỉ Số | Mục Tiêu | Tuần |
|--------|----------|------|
| **Accuracy ML** | 85%+ | W1 |
| **Phủ Code** | 80%+ | W3 |
| **API Response** | <200ms | W3 |
| **UI Performance** | LCP <2s | W3 |
| **Docs** | 100% | W3 |

---

## Success Criteria

### Tuần 1 ✅
- [ ] Hoàng: ML 85%, Database ready, Fuzzy improved
- [ ] Long: Code refactored, Dark mode working
- [ ] Status: On track ✓

### Tuần 2 ✅
- [ ] Hoàng: API fully functional, Caching working
- [ ] Long: Multi-page app, Mobile ready, API integrated
- [ ] Status: On track ✓

### Tuần 3 ✅ (FINAL)
- [ ] Hoàng: Tests passing (80%+), Backend LIVE
- [ ] Long: UI polished, Frontend LIVE, Docs complete
- [ ] Status: **PRODUCTION LIVE!**

---

## 📝 Status Report Template

**Tuần:** ___   
**Ngày:** ___

### Hoàng (Backend/ML)
- ✅ Hoàn thành: ___________
- ❌ Vấn đề: ___________
- 📍 Tiếp theo: ___________

### Long (Frontend)
- ✅ Hoàn thành: ___________
- ❌ Vấn đề: ___________
- 📍 Tiếp theo: ___________

### Chung
- Sync issues: ___________
- Ngày bộc lộ: ___________

---

**Trạng thái:** ✅ Sẵn sàng thực hiện  
**Ngày bắt đầu:** Thứ 2, 07/04/2026  
**Deadline:** Thứ 2, 25/04/2026  
**Buổi đầu:** Thứ 3, 08/04/2026 (10:00-12:00)

Kế Hoạch Phân Chia Công Việc - 2 Người, 3 Tuần

Dự án: Hệ Thống Gợi Ý Ngành Học Hybrid v1.2 (Maintenance & Enhancement)
Thời gian: 3 tuần (21 ngày)  
Nhân lực: 2 người  
Deadline: Ngày 25/04/2026

Cấu trúc hiện tại:
- app.py (Streamlit UI với 3 tabs)
- hybrid_engine.py (ML + Fuzzy Logic)
- config.py, train_model.py, create_data.py

---

Phân Công

| Vai Trò | Người | Trách Nhiệm |
|--------|-------|-----------|
| Hoàng | Backend/ML | ML optimization, Performance, Features |
| Long | Frontend | UI/UX, Responsive design, Visualization |

---

TUẦN 1: Code Optimization & Bug Fixes

### Hoàng (Backend/ML)
- [ ] **W1.A1** - Code Review & Refactoring
  - [ ] Review hybrid_engine.py logic
  - [ ] Add type hints & docstrings
  - [ ] Optimize imports
  - [ ] Thời gian: 1.5 ngày
  - [ ] Output: Clean code, better documentation
  
- [ ] W1.A2 - Performance Testing
  - [ ] Benchmark hybrid_engine performance
  - [ ] Test with different input ranges
  - [ ] Check memory usage
  - [ ] Thời gian: 1.5 ngày
  - [ ] Output: Performance report, optimizations
  
- [ ] W1.A3 - Feature Enhancement
  - [ ] Add export predictions as JSON/CSV
  - [ ] Add confidence scores
  - [ ] Add sample test cases
  - [ ] Thời gian: 2 ngày
  - [ ] Output: New features in hybrid_engine

### Long (Frontend)
- [ ] W1.B1 - UI/UX Review
  - [ ] Review app.py structure
  - [ ] Check CSS styling
  - [ ] Test on different screen sizes
  - [ ] Thời gian: 1 ngày
  - [ ] Output: UX improvement list
  
- [ ] W1.B2 - Code Cleanup & Type Hints
  - [ ] Add type hints to app.py functions
  - [ ] Optimize layout components
  - [ ] Clean up CSS
  - [ ] Thời gian: 2 ngày
  - [ ] Output: Clean, documented code
  
- [ ] W1.B3 - Responsive Design
  - [ ] Mobile-first CSS
  - [ ] Responsive grid layout
  - [ ] Test on tablet/mobile
  - [ ] Thời gian: 1.5 ngày
  - [ ] Output: Mobile-friendly UI

### Checkpoint (Cuối tuần 1 - Ngày 12/4)
- [ ] All code refactored & type-hinted
- [ ] Performance benchmarks done
- [ ] UI responsive on all devices
- [ ] Bug fixes completed

---

TUẦN 2: Features & Visualization

### Hoàng (Backend/ML)
- [ ] W2.A1 - Advanced Features
  - [ ] Multi-input predictions (save temporary results)
  - [ ] Add comparison mode (2 profiles)
  - [ ] Add statistics about recommendations
  - [ ] Thời gian: 2.5 ngày
  - [ ] Output: New prediction features
  
- [ ] W2.A2 - Testing & QA
  - [ ] Unit tests for hybrid_engine
  - [ ] Edge case testing
  - [ ] Validation tests
  - [ ] Thời gian: 1.5 ngày
  - [ ] Output: test_hybrid_engine.py

### Long (Frontend)
- [ ] W2.B1 - Advanced Visualizations
  - [ ] Improve Radar Chart (colors, interactivity)
  - [ ] Add heatmap for score distribution
  - [ ] Add success rate visualization
  - [ ] Thời gian: 2 ngày
  - [ ] Output: Better charts with Plotly
  
- [ ] W2.B2 - UI Enhancements
  - [ ] Add dark mode toggle
  - [ ] Improve color scheme
  - [ ] Add animations/transitions
  - [ ] Better error messages
  - [ ] Thời gian: 2 ngày
  - [ ] Output: Enhanced UI theme

### Checkpoint (Cuối tuần 2 - Ngày 19/4)
- [ ] New features working
- [ ] Advanced visualizations complete
- [ ] Unit tests passing
- [ ] Dark mode implemented

---

TUẦN 3: Testing, Documentation & Deployment

### Hoàng (Backend/ML)
- [ ] W3.A1 - Integration Testing
  - [ ] Test end-to-end workflows
  - [ ] Test with real-world data
  - [ ] Performance under load
  - [ ] Thời gian: 1.5 ngày
  - [ ] Output: Comprehensive test results
  
- [ ] W3.A2 - Documentation
  - [ ] Update README.md with v1.2 features
  - [ ] Create CHANGELOG.md
  - [ ] Add code examples
  - [ ] Thời gian: 1 ngày
  - [ ] Output: Complete documentation

### Long (Frontend)
- [ ] W3.B1 - Cross-browser Testing
  - [ ] Test Chrome, Firefox, Safari, Edge
  - [ ] Test on different OS (Windows, Mac, Linux)
  - [ ] Document compatibility
  - [ ] Thời gian: 1 ngày
  - [ ] Output: Compatibility report
  
- [ ] W3.B2 - UI Polish & Bug Fixes
  - [ ] Fix remaining UI issues
  - [ ] Final UX refinements
  - [ ] Performance optimization
  - [ ] Thời gian: 1.5 ngày
  - [ ] Output: Production-ready UI

### Both (Cả hai)
- [ ] **W3.BOTH.1** - Final Testing
  - [ ] Full app workflow testing
  - [ ] User acceptance testing scenarios
  - [ ] Performance check
  - [ ] Thời gian: 1 ngày
  - [ ] Output: Final test report

- [ ] **W3.BOTH.2** - Deployment
  - [ ] Final git commit & tag
  - [ ] Create GitHub release (v1.2)
  - [ ] Update deployment details
  - [ ] Thời gian: 0.5 ngày
  - [ ] Output: v1.2 RELEASED

### Final Checklist (Ngày 25/4)
- [ ] All code committed & documented
- [ ] All tests passing
- [ ] Cross-browser compatible
- [ ] Dark mode working
- [ ] Performance optimized
- [ ] README & CHANGELOG updated
- [ ] GitHub release created
- [ ] v1.2 LIVE

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

## Tóm Tắt Output

**Hoàng (Backend/ML):**
- Optimized hybrid_engine.py
- Performance benchmarks
- New prediction features
- Unit tests (70%+ coverage)
- Complete documentation

**Long (Frontend):**
- Responsive design (mobile, tablet, desktop)
- Dark mode toggle
- Advanced visualizations
- Cross-browser tested
- Production-ready UI

**Output:**
- v1.2 release on GitHub
- Clean, documented codebase
- Performance improvements
- Better UX in Streamlit app


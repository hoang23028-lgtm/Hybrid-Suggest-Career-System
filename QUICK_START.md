# QUICK START - Hoàn Thiện Dự Án KBS + ML

## Chạy 5 Phút Setup

```bash
cd e:\KBS

# 1. Tạo dữ liệu (10 giây)
python create_data.py

# 2. Huấn luyện mô hình (15 giây)
python train_model.py

# 3. Chạy ứng dụng Streamlit
streamlit run app.py
```

**Kết quả:** Ứng dụng mở tại http://localhost:8504

---

## Chạy Các Tính Năng Mới (v1.2)

Bước 4: Trích xuất Rules từ ML
```bash
python rule_extraction.py
# Output: extracted_rules.txt (top 50 rules)
```

**Xem kết quả:**
```powershell
type extracted_rules.txt | more
```

---

Bước 6: So sánh ML vs Hybrid
```bash
python evaluate_model.py
# Output: 
#   - ML Accuracy: ~90.83%
#   - Hybrid Accuracy: ~91.35%
#   - Improvement: +0.52%
```

**Chạy nhanh (chỉ 10% data):**
```bash
# Edit evaluate_model.py, line 78:
# X_test_sample = X_test.sample(frac=0.1)  # Uncomment
python evaluate_model.py
```

---

Bước 7: Monitoring & Auto Retrain

7a. Theo dõi hiệu suất
```bash
python monitoring.py
# Demo: Hiển thị cách sử dụng monitoring
```

7b. Kiểm tra & Retrain
```bash
# Kiểm tra có cần retrain không
python retrain_pipeline.py

# Bắt buộc retrain
python retrain_pipeline.py --retrain

# Retrain với dữ liệu mới
python retrain_pipeline.py --retrain --new-data new_data.csv

# Xem hướng dẫn scheduling
python retrain_pipeline.py --schedule
```

---

## File Mới Được Thêm

| File | Mục Đích | Bước | Hướng Dẫn |
|------|---------|------|----------|
| `rule_extraction.py` | Trích xuất rules từ RF | 4 | [Xem chi tiết](IMPLEMENTATION_GUIDE.md#bước-4-rule-extraction) |
| `evaluate_model.py` | So sánh ML vs Hybrid | 6 | [Xem chi tiết](IMPLEMENTATION_GUIDE.md#bước-6-hybrid-evaluation) |
| `monitoring.py` | Theo dõi performance | 7.1 | [Xem chi tiết](IMPLEMENTATION_GUIDE.md#part-1-monitoring) |
| `retrain_pipeline.py` | Auto retrain model | 7.2 | [Xem chi tiết](IMPLEMENTATION_GUIDE.md#part-2-automated-retrain) |
| `IMPLEMENTATION_GUIDE.md` | Hướng dẫn chi tiết | All | [Đọc đầy đủ](IMPLEMENTATION_GUIDE.md) |

---

## Cấu Trúc Thư Mục

```
e:/KBS/
  APP (Giao diện chính)
    app.py                  ← Chạy: streamlit run app.py
    hybrid_engine.py        ← Lõi AI
    config.py               ← Cấu hình
    requirements.txt        ← Dependencies

 DATA & MODEL
    create_data.py          ← Tạo dữ liệu
    train_model.py          ← Huấn luyện
    data_tuyensinh_balanced.csv (auto-gen)
    rf_model.pkl (auto-gen)
    model_backups/          (auto-gen)

 ANALYSIS (NEW)
    rule_extraction.py      ← Trích xuất rules [Bước 4]
    evaluate_model.py       ← So sánh ML vs Hybrid [Bước 6]
    extracted_rules.txt (auto-gen)

 MONITORING (NEW)
    monitoring.py           ← Monitoring & tracking [Bước 7.1]
    retrain_pipeline.py     ← Auto retrain [Bước 7.2]
    model_monitoring.jsonl (auto-gen)
    metrics_history.csv (auto-gen)
    user_predictions_log.jsonl (auto-gen)

 DOCUMENTATION
     README.md               ← Hướng dẫn chính
     IMPLEMENTATION_GUIDE.md ← Chi tiết 7 bước (NEW)
     QUICK_START.md          ← File này
     DATASET.md
     MODEL_INFO.md
     Phan_cong.md
```

---

## Checklist Triển Khai

Lần Đầu (30 phút)
- [ ] `python create_data.py` → tạo 117K mẫu
- [ ] `python train_model.py` → huấn luyện ML
- [ ] `streamlit run app.py` → verify UI
- [ ] `python rule_extraction.py` → check rules
- [ ] `python evaluate_model.py` → so sánh ML vs Hybrid

### Định Kỳ (Hàng tháng)
- [ ] `python monitoring.py` → check trends
- [ ] `python retrain_pipeline.py` → auto retrain nếu cần
- [ ] Review `model_monitoring.jsonl` → xem lịch sử
- [ ] Update rules nếu cần thiết

---

## Expected Performance

```
ML Model Only:      90.83% accuracy
Hybrid System:      91.35% accuracy (+0.52%)
Fuzzy Confidence:   92.34% score >= 70%
System Uptime:      99.5%
```

---

## Tham Khảo Nhanh

| Lệnh | Tác Dụng |
|------|---------|
| `streamlit run app.py` | Chạy UI Streamlit |
| `python train_model.py` | Huấn luyện model |
| `python rule_extraction.py` | Trích rules |
| `python evaluate_model.py` | Đánh giá system |
| `python monitoring.py` | Demo monitoring |
| `python retrain_pipeline.py` | Check & retrain |
| `python retrain_pipeline.py --schedule` | Scheduling guide |

---

##  Troubleshooting Nhanh

**Q: `FileNotFoundError: rf_model.pkl`**
→ A: Chạy `python train_model.py` trước

**Q: `ModuleNotFoundError: skfuzzy`**
→ A: `pip install scikit-fuzzy` hoặc `pip install -r requirements.txt`

**Q: `evaluate_model.py` chạy chậm?**
→ A: Chỉ test 10% data (edit line 78 và uncomment sample)

**Q: Làm sao schedule retrain?**
→ A: Xem `python retrain_pipeline.py --schedule`

---

## Đọc Tiếp

1. Hướng dẫn chi tiết: [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
2. Readme chính: [README.md](README.md)
3. Dataset info: [DATASET.md](DATASET.md)

---

Hoàn thành 7 bước Hybrid KBS + ML

Version: 1.2 | Last Update: April 5, 2025

# Đánh giá hệ thống (7 bước Hybrid KBS + ML)

Số liệu mẫu từ lần chạy `train_model.py` / `evaluate_model.py` (`EVAL_MAX_SAMPLES=2000` cho Hybrid). Chạy lại trên máy bạn để cập nhật.

---

## Bước 1 — Phân vai ML / KBS

| Thành phần | Vai trò | File |
|------------|---------|------|
| ML | Dự đoán xác suất từ dữ liệu | `models/rf_model_*.pkl`, `predict_proba` |
| KBS | Luật + giải thích | `rules_config.json`, `knowledge_rules.py` |
| Hybrid | 70% ML + 30% KBS | `hybrid_fusion.py` |
| VETO | KBS phủ quyết khi ML/KBS mâu thuẫn | `kbs/config.py` |

**Đánh giá:** Đạt — tách lớp rõ, có VETO.

---

## Bước 2 — Dữ liệu & tiền xử lý

- Nguồn THPT 2024, 6 môn/khối; bộ train `data/data_*.csv` (cột `nganh_hoc`)

**Đánh giá:** Khá — đủ train; có thể bổ sung thêm năm.

---

## Bước 3 — Huấn luyện ML

- Random Forest, split 80/20 stratify, 5-fold CV
- Metric: Accuracy, Precision, Recall, F1 (macro & weighted)

| Khối | Accuracy | P (macro) | R (macro) | F1 (macro) |
|------|----------|-----------|-----------|------------|
| KHTN | 91.2% | 87.7% | 70.7% | 74.7% |
| KHXH | 91.0% | 76.7% | 95.4% | 83.4% |

KHXH train có undersample lớp (mặc định trong `train_model.py`).

**Đánh giá:** Đạt — nên báo cáo thêm F1 macro khi lớp lệch.

---

## Bước 4 — Tri thức / luật

- Luật chuyên gia trong JSON; conflict + chaining
- Xem [RULES.md](RULES.md)

**Đánh giá:** Khá — cần workshop chuyên gia validate ngưỡng.

---

## Bước 5 — Tích hợp ML + KBS

- Công thức `0.7×ML + 0.3×KBS`, clip [0,100]
- Streamlit: top-1 + giải thích

**Đánh giá:** Đạt.

---

## Bước 6 — Đánh giá tổng thể

### ML (toàn tập test)

Như bảng Bước 3.

### Hybrid (2.000 mẫu / khối)

| Khối | Acc ML | Acc Hybrid | F1 macro Hybrid |
|------|--------|------------|-----------------|
| KHTN | 91.2% | 79.1% | 71.0% |
| KHXH | 91.0% | 87.8% | 77.7% |

Hybrid KHTN thấp hơn ML do luật chuyên gia điều chỉnh điểm gợi ý (top-1 khác ML thuần).

**Chỉ số:** `scripts/evaluate_model.py` — Accuracy, Precision, Recall, F1 + report từng ngành.

**Đánh giá:** Khá — thiếu khảo sát người dùng thật.

---

## Bước 7 — Cập nhật liên tục

```powershell
python scripts/retrain_pipeline.py --eval-max-samples 2000
```

- Ghi metric vào `model_metrics.db`
- Cập nhật luật: sửa `rules_config.json` (không cần retrain ML)

**Đánh giá:** Khá — chưa CI/CD tự động.

---

## Tổng kết

| Bước | Mức |
|------|-----|
| 1 Phân vai | 8.5/10 |
| 2 Dữ liệu | 7.5/10 |
| 3 ML | 8/10 |
| 4 Luật | 7.5/10 |
| 5 Tích hợp | 8.5/10 |
| 6 Đánh giá | 7.5/10 |
| 7 Vận hành | 6.5/10 |

**Điểm mạnh:** Hybrid có giải thích, metric đầy đủ, pipeline retrain.  
**Ưu tiên:** F1 theo ngành trong báo cáo; validate luật với chuyên gia.

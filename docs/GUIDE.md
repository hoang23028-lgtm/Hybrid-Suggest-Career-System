# Hướng dẫn dự án — Hybrid KBS + ML v3

## Kiến trúc tóm tắt

```
app.py (Streamlit) → hybrid_fusion.py
                         ├─ ML: rf_model_{khtn|khxh}.pkl → predict_proba × 100
                         ├─ KBS: rules_config.json → KnowledgeRuleEngine
                         └─ Hybrid = 0.7×ML + 0.3×KBS (+ VETO nếu mâu thuẫn)
```

| Khối | 6 môn | Ngành (mã) | Model |
|------|-------|------------|--------|
| **KHTN** | Toán, Văn, Anh, Lý, Hóa, Sinh | 0 IT, 1 KT, 2 Y khoa, 3 Kỹ thuật, 4 NLN | `models/rf_model_khtn.pkl` |
| **KHXH** | Toán, Văn, Anh, Sử, Địa, GDCD | 1 KT, 5 Sư phạm, 6 Luật, 7 Du lịch | `models/rf_model_khxh.pkl` |

Tham số VETO và đường dẫn: `kbs/config.py`. Luật JSON: `rules_config.json` (chi tiết: [RULES.md](RULES.md)).

---

## Cài đặt & chạy nhanh

```powershell
cd E:\KBS
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python scripts/create_data.py      # cần data/diem_thi_thpt_2024.csv
python scripts/train_model.py
streamlit run app.py               # http://localhost:8501
```

---

## Script CLI

| Script | Mục đích |
|--------|----------|
| `create_data.py` | CSV gốc → `data/data_khtn.csv`, `data/data_khxh.csv` |
| `train_model.py` | Huấn luyện 2 RF; in Accuracy, P/R/F1 |
| `evaluate_model.py` | So ML vs Hybrid trên tập test |
| `retrain_pipeline.py` | Train + eval + ghi `model_metrics.db` (mặc định không chạy lại create_data) |
| `tune_weights.py` | Quét tỉ lệ ML/KBS (tuỳ chọn) |
| `tune_veto.py` | Quét ngưỡng VETO (tuỳ chọn) |
| `rule_extraction.py` | Trích candidate rules từ cây RF → `extracted_rules/` (review, không auto-merge JSON) |

```powershell
# Đánh giá (Hybrid chậm — giới hạn mẫu)
$env:EVAL_MAX_SAMPLES = "2000"
python scripts/evaluate_model.py

# Retrain + DB
python scripts/retrain_pipeline.py --blocks khtn khxh --eval-max-samples 2000
python scripts/retrain_pipeline.py --create-data   # kèm tạo lại data

pytest -q test_hybrid_fusion.py test_label_assignment.py

# Trích xuất luật candidate từ ML (cần model .pkl)
python scripts/rule_extraction.py --block khtn --out-dir extracted_rules --top-k-total 30
python scripts/rule_extraction.py --block khxh --out-dir extracted_rules --top-k-total 30
```

---

## Dữ liệu

**Nguồn:** `data/diem_thi_thpt_2024.csv` (THPT 2024).

**Pipeline** (`create_data.py`):

1. Đổi tên cột (`RAW_COLUMN_MAP` trong `kbs/config.py`)
2. Lọc đủ 6 môn theo khối
3. Ghi cột `nganh_hoc` (mã ngành mục tiêu, theo `NGANH_HOC_MAP`)
4. Lưu `data/data_khtn.csv`, `data/data_khxh.csv`

**Cột huấn luyện:** 6 điểm môn + `nganh_hoc`.

---

## Module chính

| File | Vai trò |
|------|---------|
| `app.py` | UI Streamlit |
| `kbs/hybrid_fusion.py` | ML + KBS + fusion + ranking |
| `kbs/knowledge_rules.py` | Engine đọc JSON |
| `kbs/config.py` | Features, ngành, VETO, paths |
| `kbs/metrics_db.py` | SQLite metric sau retrain |

Shim gốc (`config.py`, `hybrid_fusion.py`, …) re-export từ `kbs/` cho `app.py`.

---

## Xử lý sự cố

| Triệu chứng | Xử lý |
|-------------|--------|
| Thiếu `data/data_*.csv` | `python scripts/create_data.py` |
| Thiếu `models/rf_model_*.pkl` | `python scripts/train_model.py` |
| `KeyError: 'nganh_hoc'` | Chạy lại `create_data.py` |
| Cổng 8501 bận | `streamlit run app.py --server.port 8502` |

---

Đánh giá 7 bước & số liệu mẫu: [EVALUATION.md](EVALUATION.md).

**Đánh giá mô hình : 
$env:EVAL_MAX_SAMPLES = "2000" 
python scripts/evaluate_model.py
**Retrain 
python scripts/retrain_pipeline.py --blocks khtn khxh --eval-max-samples 2000
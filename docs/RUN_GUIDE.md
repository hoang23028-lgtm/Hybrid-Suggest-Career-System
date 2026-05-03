# Hướng dẫn chạy dự án

Repo đã được tổ chức lại theo thư mục:
- `kbs/`: core logic (KBS/Hybrid/Config/Metrics)
- `scripts/`: CLI (data/train/eval/tune_veto/retrain/rule_extraction)
- `data/`: dữ liệu CSV
- `models/`: model `.pkl`
- `docs/`: tài liệu

---

## 1) Cài đặt môi trường (Windows / PowerShell)

```powershell
cd E:\KBS
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 2) Chạy nhanh (end-to-end)

Yêu cầu: có file `data/diem_thi_thpt_2024.csv`.

```powershell
cd E:\KBS

# (A) Tạo dữ liệu theo 2 khối (KHTN/KHXH)
python scripts/create_data.py

# (B) Train 2 model
python scripts/train_model.py

# (C) Chạy giao diện
streamlit run app.py
```

---

## 3) Các chức năng và cách chạy

### 3.1 UI gợi ý ngành (Streamlit)
- **File**: `app.py`
- **Chức năng**:
  - chọn khối `KHTN` / `KHXH`
  - nhập 6 điểm theo khối (slider động)
  - nhấn **Phân tích**: hiển thị **ngành đề xuất** (hybrid top-1), giải thích, **chuỗi suy luận KBS** (nếu có), và hai tab **Kết quả chính** / **Phân tích chi tiết** (radar + bảng môn)
  - (Không còn tab so sánh nhiều ngành hay nút xem danh sách tất cả ngành trên UI; ranking đầy đủ chỉ dùng nội bộ để chọn top-1.)

```powershell
streamlit run app.py
```

### 3.2 Tạo dữ liệu theo khối (data pipeline)
- **File**: `scripts/create_data.py`
- **Input**: `data/diem_thi_thpt_2024.csv`
- **Output**:
  - `data/data_khtn.csv`
  - `data/data_khxh.csv`
  - (Để train/eval ML) cần có cột nhãn `nganh_hoc` trong các file CSV này.

```powershell
python scripts/create_data.py
```

### 3.3 Huấn luyện mô hình (2 model theo khối)
- **File**: `scripts/train_model.py`
- **Input**: `data/data_khtn.csv`, `data/data_khxh.csv`
- **Output**: `models/rf_model_khtn.pkl`, `models/rf_model_khxh.pkl`

```powershell
python scripts/train_model.py
```

### 3.4 Đánh giá ML vs Hybrid (Bước 6)
- **File**: `scripts/evaluate_model.py`
- **Ghi chú**: phần Hybrid có thể chậm; có thể giới hạn số mẫu bằng biến môi trường `EVAL_MAX_SAMPLES`.

```powershell
$env:EVAL_MAX_SAMPLES=2000
python scripts/evaluate_model.py
```

### 3.5 Quét tham số VETO (tuỳ chọn)
- **File**: `scripts/tune_veto.py`
- **Tham số mặc định**: `kbs/config.py` (`VETO_KBS_NOT_FIT_THRESHOLD`, `VETO_ML_HIGH_THRESHOLD`, `VETO_KEY_SUBJECT_MIN`, `VETO_KBS_DOMINANT_WEIGHT`)
- **Mục đích**: lưới nhỏ trên tập test (cùng split như `evaluate_model`) để so sánh accuracy / F1 macro; in TOP combo gợi ý chép vào `kbs/config.py` sau khi kiểm chứng.

```powershell
python scripts/tune_veto.py --block khtn --max-samples 800
python scripts/tune_veto.py --block both --max-samples 500 --kbs-low 18,20,22 --ml-high 55,60,65
```

### 3.6 Rule extraction từ ML (Bước 4)
- **File**: `scripts/rule_extraction.py`
- **Mục tiêu**: xuất **candidate rules** để chuyên gia review (không auto-merge thẳng vào `rules_config.json`).
- **Output**: `extracted_rules/<block>_candidates.json`, `extracted_rules/<block>_review.md`

```powershell
python scripts/rule_extraction.py --block khtn --out-dir extracted_rules --min-confidence 0.6 --min-samples 50 --top-k-total 50 --top-k-per-class 10
python scripts/rule_extraction.py --block khxh --out-dir extracted_rules --min-confidence 0.6 --min-samples 50 --top-k-total 50 --top-k-per-class 10
```

### 3.7 Retrain pipeline + lưu metrics DB (Bước 7)
- **File**: `scripts/retrain_pipeline.py`
- **DB**: `model_metrics.db` (tables: `metrics`, `alerts`, `predictions`)
- **Ghi**: metrics ML & Hybrid + versioning (`git SHA`, `rules sha256`, `model sha256`) vào `details_json`

```powershell
# End-to-end (data + train + eval + persist DB)
python scripts/retrain_pipeline.py --blocks khtn khxh --eval-max-samples 2000

# Nếu chỉ evaluate + ghi DB (không chạy lại data/train)
python scripts/retrain_pipeline.py --blocks khtn --skip-data --skip-train --eval-max-samples 200

# Kèm rule extraction sau pipeline
python scripts/retrain_pipeline.py --blocks khtn khxh --extract-rules --rules-out-dir extracted_rules
```

### 3.8 Xem schema DB metrics
- **File**: `scripts/inspect_db.py`

```powershell
python scripts/inspect_db.py
```

---

## 4) “Core” nằm ở đâu?

- **Cấu hình (paths, features, majors, tham số VETO)**: `kbs/config.py`  
- **KBS engine (JSON rules + conflict + chaining + `reasoning_chain`)**: `kbs/knowledge_rules.py`  
- **Hybrid engine (ML+KBS+VETO+ranking)**: `kbs/hybrid_fusion.py`  
- **Metrics DB (insert/alerts/baseline degradation)**: `kbs/metrics_db.py`  
- **Rules config**: `rules_config.json`

---

## 5) Troubleshooting nhanh

- **Không có `data/data_khtn.csv` / `data/data_khxh.csv`**: chạy `python scripts/create_data.py`
- **Không có `models/rf_model_khtn.pkl` / `models/rf_model_khxh.pkl`**: chạy `python scripts/train_model.py`
- **Thiếu `data/diem_thi_thpt_2024.csv`**: đặt đúng tên file theo `kbs/config.py`
 - **Lỗi `KeyError: 'nganh_hoc'` khi train/eval**: đảm bảo `data/data_*.csv` có cột nhãn `nganh_hoc` (theo `kbs/config.py:NGANH_HOC_MAP`).


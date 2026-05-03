# Hệ thống gợi ý ngành học (Hybrid KBS + ML) — Phiên bản 3.0

Ứng dụng gợi ý ngành đại học dựa trên **điểm THPT**, kết hợp **Random Forest** (ML) và **luật chuyên gia** (KBS) trong `rules_config.json`.

## Kiến trúc 3.0 (hai khối, không Tin học)

| Khối | Môn nhập (6) | Số ngành gợi ý | Model |
|------|----------------|----------------|--------|
| **KHTN** | Toán, Văn, Anh, Lý, Hóa, Sinh | 5 | `models/rf_model_khtn.pkl` |
| **KHXH** | Toán, Văn, Anh, Sử, Địa, GDCD | 4 | `models/rf_model_khxh.pkl` |

- **Hybrid:** `Hybrid = 0.5 × ML + 0.5 × KBS` (có cơ chế **VETO** khi ML và KBS mâu thuẫn rõ rệt).
- **Dữ liệu huấn luyện:** `data/diem_thi_thpt_2024.csv` → lọc theo khối → `scripts/create_data.py` → `data/data_khtn.csv` / `data/data_khxh.csv` (cần có cột nhãn `nganh_hoc` để train/eval ML).
- **Giao diện:** `app.py` (Streamlit): chọn khối → slider 6 môn → **Phân tích** → ngành đề xuất (hybrid); hai tab **Kết quả chính** (metric, giải thích, chuỗi suy luận KBS) và **Phân tích chi tiết** (radar Plotly, bảng điểm). `get_hybrid_ranking` vẫn xếp hạng đủ ngành trong khối để chọn top-1 (không còn màn hình so sánh tất cả ngành trên UI).

## Cấu trúc thư mục (đã tổ chức lại)

```
e:/KBS/
  app.py                 # UI Streamlit
  config.py              # (shim) re-export từ kbs/config.py
  hybrid_fusion.py       # (shim) re-export từ kbs/hybrid_fusion.py
  knowledge_rules.py     # (shim) re-export từ kbs/knowledge_rules.py
  metrics_db.py          # (shim) re-export từ kbs/metrics_db.py
  monitoring.py          # (shim) re-export từ kbs/monitoring.py
  rules_config.json      # Luật KHTN / KHXH + chaining
  kbs/                   # Core package (config, KBS, hybrid, metrics)
  scripts/               # CLI: create_data/train/eval/tune_veto/retrain/rule_extraction
  docs/                  # Tài liệu v3
  data/                  # CSV datasets
  models/                # Model artifacts (.pkl)
  experiments.py         # Thử nghiệm (legacy, optional)
  test_hybrid_fusion.py  # Pytest
  requirements.txt
  README.md                # File này
  docs/DATASET_v3.md            # Mô tả dữ liệu & pipeline
  docs/KBS_AI_DETAIL_v3.md      # Luồng xử lý chi tiết
  docs/KNOWLEDGE_BASED_RULES_v3.md  # Luật JSON & KBS
  docs/HYBRID_KBS_ML_EVALUATION_v3.md # Đánh giá 7 bước (tổng quan)
  docs/KBS_EVALUATION_REPORT_v3.md    # Báo cáo đánh giá tổng hợp
  docs/RUN_GUIDE.md                   # Hướng dẫn chạy dự án (Windows / pipeline)
```

## Chạy nhanh

```bash
cd e:\KBS
pip install -r requirements.txt

# 1) Tạo dữ liệu đã lọc theo khối (cần file `data/diem_thi_thpt_2024.csv`)
python scripts/create_data.py

# 2) Huấn luyện hai model
python scripts/train_model.py

# 3) Giao diện
streamlit run app.py
```

Mặc định Streamlit: **http://localhost:8501** (hoặc cổng bạn chỉ định, ví dụ `--server.port 8501`).

## Luồng xử lý (tóm tắt)

1. Người dùng chọn **KHTN** hoặc **KHXH** và nhập **6 điểm** (0–10).
2. `hybrid_fusion.load_ml_model(block)` tải đúng `rf_model_{block}.pkl`.
3. Với mỗi ngành thuộc khối: `calculate_hybrid_score(scores, major_index, block=...)`  
   - ML: `predict_proba` trên 6 cột đúng thứ tự `config.get_features(block)`  
   - KBS: `KnowledgeRuleEngine(block).evaluate(...)`  
4. `get_hybrid_ranking(scores, block=...)` xếp hạng các ngành **của khối đó** (5 hoặc 4).

## Đánh giá / thử nghiệm

```bash
# Đánh giá ML vs hybrid (từng khối; có thể giới hạn mẫu hybrid bằng biến môi trường)
set EVAL_MAX_SAMPLES=2000
python scripts/evaluate_model.py

# (Tuỳ chọn) Quét tham số VETO trên tập test — xem `kbs/config.py` và `scripts/tune_veto.py`
python scripts/tune_veto.py --block khtn --max-samples 800

pytest -q test_hybrid_fusion.py
```

## Khắc phục sự cố thường gặp

| Lỗi / triệu chứng | Cách xử lý |
|-------------------|------------|
| Không tìm thấy `models/rf_model_khtn.pkl` / `models/rf_model_khxh.pkl` | Chạy `python scripts/train_model.py` sau khi đã có `data/data_khtn.csv` và `data/data_khxh.csv`. |
| Không có `data/data_khtn.csv` / `data/data_khxh.csv` | Chạy `python scripts/create_data.py` (cần `data/diem_thi_thpt_2024.csv`). |
| Lỗi `KeyError: 'nganh_hoc'` khi train/eval | Đảm bảo `data/data_*.csv` có cột nhãn `nganh_hoc` (theo `kbs/config.py:NGANH_HOC_MAP`). |
| Cổng Streamlit đã dùng | `streamlit run app.py --server.port 8502` |

## Tài liệu chi tiết (v3)

- [DATASET_v3.md](docs/DATASET_v3.md) — Nguồn dữ liệu, cột, pipeline dữ liệu
- [KBS_AI_DETAIL_v3.md](docs/KBS_AI_DETAIL_v3.md) — Luồng ML / KBS / hybrid theo `block`
- [KNOWLEDGE_BASED_RULES_v3.md](KNOWLEDGE_BASED_RULES_v3.md) — Cấu trúc `rules_config.json`
- [HYBRID_KBS_ML_EVALUATION_v3.md](HYBRID_KBS_ML_EVALUATION_v3.md) — Khung đánh giá 7 bước
- [KBS_EVALUATION_REPORT_v3.md](KBS_EVALUATION_REPORT_v3.md) — Báo cáo tổng hợp & roadmap
- [RUN_GUIDE.md](docs/RUN_GUIDE.md) — Cài đặt, chạy Streamlit, script CLI

---

**Cập nhật:** 03/05/2026 — Hybrid 50/50 ML+KBS, VETO trong `kbs/config.py`, `scripts/tune_veto.py`, chuỗi suy luận KBS (`reasoning_chain`); UI Streamlit gọn: 2 tab, không tab so sánh ngành / không nút xem tất cả ngành.

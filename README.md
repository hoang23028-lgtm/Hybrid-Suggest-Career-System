# Hệ thống gợi ý ngành học (Hybrid KBS + ML) v3

Gợi ý ngành ĐH từ **điểm THPT**: **Random Forest** + **luật chuyên gia** (`rules_config.json`), fusion **70% ML / 30% KBS**, có **VETO**.

| Khối | 6 môn | Ngành | Model |
|------|-------|-------|--------|
| KHTN | Toán, Văn, Anh, Lý, Hóa, Sinh | 5 | `models/rf_model_khtn.pkl` |
| KHXH | Toán, Văn, Anh, Sử, Địa, GDCD | 4 | `models/rf_model_khxh.pkl` |

## Chạy nhanh

```powershell
cd E:\KBS
pip install -r requirements.txt
python scripts/create_data.py    # cần data/diem_thi_thpt_2024.csv
python scripts/train_model.py
streamlit run app.py           # http://localhost:8501
```

```powershell
$env:EVAL_MAX_SAMPLES = "2000"
python scripts/evaluate_model.py
pytest -q
```

## Cấu trúc

```
app.py, rules_config.json
kbs/          # config, hybrid_fusion, knowledge_rules, …
scripts/      # create_data, train_model, evaluate_model, retrain_pipeline, tune_*
data/         # CSV
models/       # .pkl
docs/         # GUIDE.md, RULES.md, EVALUATION.md
```

## Tài liệu

| File | Nội dung |
|------|----------|
| [docs/GUIDE.md](docs/GUIDE.md) | Cài đặt, script, dữ liệu, module, sự cố |
| [docs/RULES.md](docs/RULES.md) | Luật JSON, conflict, chaining, VETO |
| [docs/EVALUATION.md](docs/EVALUATION.md) | Đánh giá 7 bước + metric mẫu |

## Sự cố nhanh

| Lỗi | Xử lý |
|-----|--------|
| Thiếu `data/data_*.csv` | `python scripts/create_data.py` |
| Thiếu model `.pkl` | `python scripts/train_model.py` |
| Cổng bận | `streamlit run app.py --server.port 8502` |

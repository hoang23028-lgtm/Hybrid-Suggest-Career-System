# Luật KBS (`rules_config.json`)

## Tổng quan

- **KHTN:** 5 ngành × (4 luật nền + 2 chaining) = 30 định nghĩa
- **KHXH:** 4 ngành × (4 luật nền + 2 chaining) = 24 định nghĩa
- Mỗi ngành có 3 luật `AND` (Very_Fit / Fit / Medium) + 1 `OR_LESS_THAN` (Not_Fit)

Engine: `kbs/knowledge_rules.py` — `KnowledgeRuleEngine(block).evaluate(scores, major_index)`.

---

## Cấu trúc JSON (rút gọn)

```json
{
  "version": "3.0",
  "khtn_rules": {
    "0_IT": {
      "major_name": "IT",
      "rules": [
        {
          "name": "IT_Very_Fit",
          "thresholds": {"toan": 8, "ly": 7.5, "anh": 6},
          "operator": "AND",
          "score": 95,
          "specificity": 3,
          "reason": "Toán, Lý xuất sắc, Anh khá"
        }
      ],
      "chaining_rules": [ ... ]
    }
  },
  "khxh_rules": { ... }
}
```

| Field | Ý nghĩa |
|-------|---------|
| `thresholds` | Ngưỡng từng môn |
| `operator` | `AND` hoặc `OR_LESS_THAN` |
| `score` | 0–100 khi khớp |
| `specificity` | Số điều kiện (ưu tiên khi conflict) |
| `reason` | Giải thích tiếng Việt |

---

## Luồng khớp luật

```
Điểm 6 môn → duyệt luật nền từng ngành trong khối
           → lọc luật thỏa điều kiện
           → conflict: specificity cao → score cao
           → forward_chain (bonus nếu có chaining_rules)
           → điểm KBS 0–100 + reasoning_chain
```

**Conflict resolution:** (1) specificity lớn hơn thắng; (2) hòa thì score cao hơn.

**Chaining:** Sau khi có luật nền thắng, kiểm tra `chaining_rules` (điều kiện `requires` + `threshold`) để cộng bonus.

---

## Tích hợp Hybrid

- KBS score: output `evaluate()` → thang 0–100
- Hybrid: `0.7 × ML + 0.3 × KBS` (`kbs/hybrid_fusion.py`)
- **VETO:** KBS rất thấp + ML cao + môn trọng tâm yếu → trọng số ~15% ML / 85% KBS (`VETO_*` trong `kbs/config.py`)

UI hiển thị `reasoning_chain` cho ngành đề xuất (top-1).

---

## Sửa luật

1. Chỉnh `rules_config.json` (ngưỡng, score, reason).
2. Không cần train lại ML.
3. Chạy lại app hoặc `pytest` hybrid/KBS.

Tinh VETO / tỉ lệ ML–KBS: `scripts/tune_veto.py`, `scripts/tune_weights.py`.

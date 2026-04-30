"""
Rule extraction (Step 4) for v3.

Mục tiêu: trích xuất các đường đi (path-to-leaf) từ RandomForest (scikit-learn)
để tạo **candidate rules** cho con người review trước khi đưa vào `rules_config.json`.

Lưu ý quan trọng:
- Decision tree dùng cả điều kiện `<=` và `>`; trong khi format KBS v3 dùng `AND` (>=)
  hoặc `OR_LESS_THAN` (<). Vì vậy script này **không auto-merge** trực tiếp vào KBS,
  mà xuất ra file review + JSON candidates.
"""

from __future__ import annotations

import argparse
import json
import logging
import pickle
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sklearn.tree import _tree

# Ensure repo root is importable when running `python scripts/...`
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from kbs.config import NGANH_HOC_MAP, get_features, get_majors, get_model_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

try:  # Windows terminals can default to a non-UTF8 codepage
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


@dataclass(frozen=True)
class CandidateRule:
    block: str
    predicted_class: int
    confidence: float
    samples: int
    conditions: list[tuple[str, str, float]]  # (feature, op, threshold)
    tree_index: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "block": self.block,
            "predicted_class": self.predicted_class,
            "predicted_label": NGANH_HOC_MAP.get(self.predicted_class, str(self.predicted_class)),
            "confidence": float(self.confidence),
            "samples": int(self.samples),
            "conditions": [
                {"feature": f, "op": op, "threshold": float(t)} for (f, op, t) in self.conditions
            ],
            "tree_index": int(self.tree_index),
        }


class RuleExtractorV3:
    def __init__(self, block: str, model, feature_names: list[str]):
        self.block = block
        self.model = model
        self.feature_names = feature_names

    def extract_tree_candidates(self, estimator, tree_index: int) -> list[CandidateRule]:
        tree_ = estimator.tree_
        feature_name = [
            self.feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
            for i in tree_.feature
        ]

        candidates: list[CandidateRule] = []

        def walk(node: int, path: list[tuple[str, str, float]]):
            if tree_.feature[node] != _tree.TREE_UNDEFINED:
                name = feature_name[node]
                threshold = float(tree_.threshold[node])

                # left: <= threshold
                walk(tree_.children_left[node], path + [(name, "<=", threshold)])
                # right: > threshold
                walk(tree_.children_right[node], path + [(name, ">", threshold)])
                return

            # NOTE: tree_.value stores (weighted) class counts; use sum(value) for confidence.
            samples = int(tree_.n_node_samples[node])
            value = tree_.value[node][0]  # shape (n_classes,)
            predicted_class_pos = int(value.argmax())
            denom = float(value.sum())
            confidence = float(value[predicted_class_pos] / denom) if denom > 0 else 0.0

            # Map position -> real label if estimator trained with non-0..k labels.
            classes = list(getattr(self.model, "classes_", []))
            if classes:
                predicted_label = int(classes[predicted_class_pos])
            else:
                predicted_label = predicted_class_pos

            candidates.append(
                CandidateRule(
                    block=self.block,
                    predicted_class=predicted_label,
                    confidence=confidence,
                    samples=samples,
                    conditions=path,
                    tree_index=tree_index,
                )
            )

        walk(0, [])
        return candidates

    def extract_all_candidates(self) -> list[CandidateRule]:
        logger.info(f"Trích xuất candidate rules từ RandomForest ({self.block})...")
        all_candidates: list[CandidateRule] = []
        for idx, tree in enumerate(self.model.estimators_):
            cands = self.extract_tree_candidates(tree, tree_index=idx)
            all_candidates.extend(cands)
        logger.info(
            f"✓ Tổng candidate rules: {len(all_candidates):,} (từ {len(self.model.estimators_)} cây)"
        )
        return all_candidates


def consolidate_candidates(
    candidates: list[CandidateRule],
    *,
    valid_labels: set[int],
    min_confidence: float,
    min_samples: int,
    top_k_total: int,
    top_k_per_class: int,
) -> list[CandidateRule]:
    filtered = [
        c
        for c in candidates
        if c.predicted_class in valid_labels and c.confidence >= min_confidence and c.samples >= min_samples
    ]
    filtered.sort(key=lambda r: (r.confidence, r.samples, len(r.conditions)), reverse=True)

    if top_k_per_class > 0:
        per_class: dict[int, list[CandidateRule]] = {}
        for c in filtered:
            per_class.setdefault(c.predicted_class, [])
            if len(per_class[c.predicted_class]) < top_k_per_class:
                per_class[c.predicted_class].append(c)
        merged = [c for cls in sorted(per_class) for c in per_class[cls]]
        merged.sort(key=lambda r: (r.confidence, r.samples), reverse=True)
        return merged[:top_k_total] if top_k_total > 0 else merged

    return filtered[:top_k_total] if top_k_total > 0 else filtered


def format_review_md(candidates: list[CandidateRule], block: str) -> str:
    lines: list[str] = []
    lines.append(f"# Candidate rules từ ML ({block.upper()})")
    lines.append("")
    lines.append("Các rule dưới đây được trích xuất từ các leaf trong RandomForest.")
    lines.append("Mục tiêu: dùng làm **gợi ý** để chuyên gia chỉnh thành luật KBS trong `rules_config.json`.")
    lines.append("")
    lines.append("## Lưu ý khi chuyển sang KBS JSON")
    lines.append("- Decision tree dùng cả `<=` và `>`; KBS v3 dùng `AND` (>=) hoặc `OR_LESS_THAN` (<).")
    lines.append("- Vì vậy: **không auto-import** trực tiếp; hãy chọn rule hợp lý và viết lại ngưỡng.")
    lines.append("")
    for i, c in enumerate(candidates, 1):
        lines.append(f"## Rule #{i} — {NGANH_HOC_MAP.get(c.predicted_class, c.predicted_class)}")
        lines.append(f"- **confidence**: {c.confidence:.2%}")
        lines.append(f"- **samples**: {c.samples}")
        lines.append(f"- **tree_index**: {c.tree_index}")
        lines.append("")
        lines.append("**Điều kiện (raw từ tree):**")
        for feat, op, thr in c.conditions:
            lines.append(f"- `{feat} {op} {thr:.3f}`")
        lines.append("")
        lines.append("**Gợi ý skeleton KBS (cần chỉnh thủ công):**")
        lines.append("```json")
        lines.append(
            json.dumps(
                {
                    "name": f"ML_Candidate_{i}",
                    "thresholds": {"<fill>": 0},
                    "operator": "AND",
                    "score": int(round(c.confidence * 100)),
                    "specificity": 0,
                    "reason": "Trích xuất từ ML (cần chuyên gia review)",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def load_model_for_block(block: str):
    repo_root = Path(__file__).parent.parent
    model_path = repo_root / get_model_path(block)
    if not model_path.exists():
        raise FileNotFoundError(f"Không tìm thấy model cho {block}: {model_path}")
    with open(model_path, "rb") as f:
        return pickle.load(f)


def main():
    parser = argparse.ArgumentParser(description="Extract candidate rules from RandomForest (v3, per block).")
    parser.add_argument("--block", choices=["khtn", "khxh"], required=True, help="Khối: khtn hoặc khxh")
    parser.add_argument("--out-dir", default="extracted_rules", help="Thư mục output")
    parser.add_argument("--min-confidence", type=float, default=0.6, help="Ngưỡng confidence tối thiểu")
    parser.add_argument("--min-samples", type=int, default=50, help="Ngưỡng số mẫu leaf tối thiểu")
    parser.add_argument("--top-k-total", type=int, default=50, help="Giới hạn tổng rule")
    parser.add_argument("--top-k-per-class", type=int, default=10, help="Giới hạn rule mỗi ngành (0=disable)")
    args = parser.parse_args()

    block = args.block
    repo_root = Path(__file__).parent.parent
    out_dir = repo_root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    model = load_model_for_block(block)
    feature_names = get_features(block)
    majors = set(get_majors(block))

    extractor = RuleExtractorV3(block=block, model=model, feature_names=feature_names)
    all_candidates = extractor.extract_all_candidates()

    top_candidates = consolidate_candidates(
        all_candidates,
        valid_labels=majors,
        min_confidence=args.min_confidence,
        min_samples=args.min_samples,
        top_k_total=args.top_k_total,
        top_k_per_class=args.top_k_per_class,
    )
    logger.info(f"✓ Sau lọc: {len(top_candidates):,} candidates")

    json_path = out_dir / f"{block}_candidates.json"
    md_path = out_dir / f"{block}_review.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in top_candidates], f, ensure_ascii=False, indent=2)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(format_review_md(top_candidates, block=block))

    logger.info(f"✓ Wrote: {json_path}")
    logger.info(f"✓ Wrote: {md_path}")


if __name__ == "__main__":
    main()

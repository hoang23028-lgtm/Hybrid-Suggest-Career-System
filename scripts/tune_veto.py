"""
Quét lưới tham số VETO (Hybrid KBS vs ML) trên tập test — cùng split stratify như evaluate_model.

Ghi đè tạm các biến trên module `kbs.hybrid_fusion` (không sửa file config) rồi khôi phục sau mỗi combo.

Ví dụ:
  python scripts/tune_veto.py --block khtn --max-samples 500
  python scripts/tune_veto.py --block both --max-samples 300 --kbs-low 18,20,22 --ml-high 55,60,65
"""

from __future__ import annotations

import argparse
import itertools
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from kbs import hybrid_fusion as hf  # noqa: E402
from kbs.config import (  # noqa: E402
    RANDOM_STATE,
    TEST_SIZE,
    VETO_PARAM_KEYS,
    get_data_path,
    get_features,
    get_majors,
)
from kbs.hybrid_fusion import calculate_hybrid_score, load_ml_model  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _parse_float_list(s: str) -> list[float]:
    return [float(x.strip()) for x in s.split(",") if x.strip()]


def _parse_int_list(s: str) -> list[int]:
    return [int(float(x.strip())) for x in s.split(",") if x.strip()]


def _snapshot_veto() -> dict[str, float | int]:
    return {k: getattr(hf, k) for k in VETO_PARAM_KEYS}


def _apply_veto(snapshot: dict[str, float | int], **overrides) -> None:
    for k in VETO_PARAM_KEYS:
        setattr(hf, k, overrides.get(k, snapshot[k]))


def _restore_veto(snapshot: dict[str, float | int]) -> None:
    for k, v in snapshot.items():
        setattr(hf, k, v)


def hybrid_argmax_accuracy(
    block: str,
    model,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    *,
    max_samples: int | None,
) -> tuple[float, float]:
    """Top-1 theo hybrid_score trên các ngành của khối; trả (accuracy, f1_macro)."""
    features = get_features(block)
    majors = get_majors(block)
    n = len(X_test)
    if max_samples is not None and max_samples > 0:
        n = min(n, max_samples)

    y_pred = []
    for idx in range(n):
        row = X_test.iloc[idx]
        user_scores = row[features].values.tolist()
        best_m, best_s = None, -1.0
        for major_label in majors:
            r = calculate_hybrid_score(user_scores, major_label, block=block, model=model)
            sc = r.get("hybrid_score", 0) or 0
            if sc > best_s:
                best_s = sc
                best_m = major_label
        y_pred.append(best_m)

    y_true = y_test.iloc[:n].values
    y_pred = np.array(y_pred)
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    return float(acc), float(f1)


def tune_block(
    block: str,
    *,
    max_samples: int | None,
    kbs_lows: list[int],
    ml_highs: list[int],
    key_mins: list[float],
    doms: list[float],
) -> list[dict]:
    # Giảm log VETO từng mẫu khi quét nhiều combo
    logging.getLogger("kbs.hybrid_fusion").setLevel(logging.ERROR)

    df = pd.read_csv(str(REPO_ROOT / get_data_path(block)))
    features = get_features(block)
    X = df[features]
    y = df["nganh_hoc"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    model = load_ml_model(block)
    if model is None:
        raise RuntimeError(f"Không load được model cho {block}")

    snap = _snapshot_veto()
    results: list[dict] = []
    try:
        for kbs_low, ml_high, key_min, dom in itertools.product(
            kbs_lows, ml_highs, key_mins, doms
        ):
            _apply_veto(
                snap,
                VETO_KBS_NOT_FIT_THRESHOLD=kbs_low,
                VETO_ML_HIGH_THRESHOLD=ml_high,
                VETO_KEY_SUBJECT_MIN=key_min,
                VETO_KBS_DOMINANT_WEIGHT=dom,
            )
            acc, f1 = hybrid_argmax_accuracy(
                block, model, X_test, y_test, max_samples=max_samples
            )
            results.append(
                {
                    "block": block,
                    "VETO_KBS_NOT_FIT_THRESHOLD": kbs_low,
                    "VETO_ML_HIGH_THRESHOLD": ml_high,
                    "VETO_KEY_SUBJECT_MIN": key_min,
                    "VETO_KBS_DOMINANT_WEIGHT": dom,
                    "accuracy": acc,
                    "f1_macro": f1,
                }
            )
    finally:
        _restore_veto(snap)

    return results


def main() -> None:
    p = argparse.ArgumentParser(description="Tune VETO thresholds on test split")
    p.add_argument("--block", choices=["khtn", "khxh", "both"], default="khtn")
    p.add_argument("--max-samples", type=int, default=500, help="0 = toàn bộ tập test")
    p.add_argument("--kbs-low", default="15,20,25", help="Danh sách VETO_KBS_NOT_FIT_THRESHOLD")
    p.add_argument("--ml-high", default="55,60,65", help="Danh sách VETO_ML_HIGH_THRESHOLD")
    p.add_argument("--key-min", default="3.5,4.0", help="Danh sách VETO_KEY_SUBJECT_MIN")
    p.add_argument("--dom", default="0.8,0.85,0.9", help="Danh sách VETO_KBS_DOMINANT_WEIGHT")
    args = p.parse_args()

    max_samples = args.max_samples if args.max_samples > 0 else None
    kbs_lows = _parse_int_list(args.kbs_low)
    ml_highs = _parse_int_list(args.ml_high)
    key_mins = _parse_float_list(args.key_min)
    doms = _parse_float_list(args.dom)

    blocks = ["khtn", "khxh"] if args.block == "both" else [args.block]
    all_rows: list[dict] = []
    for b in blocks:
        logger.info("Đang quét VETO cho khối %s (max_samples=%s)...", b.upper(), max_samples)
        rows = tune_block(
            b,
            max_samples=max_samples,
            kbs_lows=kbs_lows,
            ml_highs=ml_highs,
            key_mins=key_mins,
            doms=doms,
        )
        all_rows.extend(rows)

    # Sắp theo F1 rồi accuracy
    all_rows.sort(key=lambda r: (r["f1_macro"], r["accuracy"]), reverse=True)
    logger.info("\n%s", "=" * 80)
    logger.info("TOP 10 (theo F1 macro, rồi accuracy)")
    logger.info("%s", "=" * 80)
    hdr = (
        f"{'block':6} {'kbs≤':>5} {'ml>':>5} {'key':>5} {'dom':>5} "
        f"{'acc':>8} {'f1':>8}"
    )
    logger.info(hdr)
    logger.info("-" * len(hdr))
    for r in all_rows[:10]:
        logger.info(
            f"{r['block']:6} {r['VETO_KBS_NOT_FIT_THRESHOLD']:5d} {r['VETO_ML_HIGH_THRESHOLD']:5d} "
            f"{r['VETO_KEY_SUBJECT_MIN']:5.1f} {r['VETO_KBS_DOMINANT_WEIGHT']:5.2f} "
            f"{r['accuracy']:8.4f} {r['f1_macro']:8.4f}"
        )
    best = all_rows[0]
    logger.info("\nGợi ý chép vào kbs/config.py (kiểm chứng lại trên đủ mẫu + ý kiến chuyên gia):")
    logger.info(
        "  VETO_KBS_NOT_FIT_THRESHOLD = %s",
        int(best["VETO_KBS_NOT_FIT_THRESHOLD"]),
    )
    logger.info(
        "  VETO_ML_HIGH_THRESHOLD = %s",
        int(best["VETO_ML_HIGH_THRESHOLD"]),
    )
    logger.info(
        "  VETO_KEY_SUBJECT_MIN = %s",
        best["VETO_KEY_SUBJECT_MIN"],
    )
    logger.info(
        "  VETO_KBS_DOMINANT_WEIGHT = %s",
        best["VETO_KBS_DOMINANT_WEIGHT"],
    )


if __name__ == "__main__":
    main()

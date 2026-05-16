"""
Quét nhiều tỉ lệ ML / KBS cho Hybrid trên tập test.

Cách hoạt động:
  - Override `ML_WEIGHT` và `KBS_WEIGHT` trên module `kbs.hybrid_fusion`.
  - Với mỗi tỉ lệ, tính hybrid_score cho từng ngành trong khối, lấy top-1.
  - Đo accuracy / precision / recall / F1 (macro & weighted) so với nhãn `nganh_hoc`.
  - Dùng cùng split (TEST_SIZE, RANDOM_STATE, stratify) như `evaluate_model.py`.

VETO mặc định vẫn bật (giống production); dùng --no-veto để vô hiệu hoá nếu muốn
đánh giá ảnh hưởng "thuần" của tỉ lệ trọng số.

Ví dụ:
  python scripts/tune_weights.py --block khxh --max-samples 800
  python scripts/tune_weights.py --block both --max-samples 500 \\
    --weights "0,0.2,0.3,0.4,0.5,0.6,0.7,0.8,1"
  python scripts/tune_weights.py --block khtn --no-veto --max-samples 500
"""

from __future__ import annotations

import argparse
import logging
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from kbs import hybrid_fusion as hf  # noqa: E402
from kbs.config import (  # noqa: E402
    RANDOM_STATE,
    TEST_SIZE,
    get_data_path,
    get_features,
    get_majors,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _parse_float_list(s: str) -> list[float]:
    return [float(x.strip()) for x in s.split(",") if x.strip()]


def _predict_hybrid(
    block: str, model, X_test: pd.DataFrame, *, max_samples: int | None
) -> np.ndarray:
    features = get_features(block)
    majors = get_majors(block)
    n = len(X_test)
    if max_samples is not None and max_samples > 0:
        n = min(n, max_samples)

    y_pred: list[int] = []
    for idx in range(n):
        row = X_test.iloc[idx]
        user_scores = row[features].values.tolist()
        best_m, best_s = majors[0], -1.0
        for major_label in majors:
            r = hf.calculate_hybrid_score(user_scores, major_label, block=block, model=model)
            sc = r.get("hybrid_score", 0) or 0.0
            if sc > best_s:
                best_s = sc
                best_m = major_label
        y_pred.append(int(best_m))
    return np.asarray(y_pred)


def _metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "precision_w": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall_w": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1_w": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
    }


def _disable_veto() -> dict:
    """Đẩy các ngưỡng VETO ra ngoài khoảng có thể kích hoạt (KBS không bao giờ phủ quyết)."""
    snap = {
        "VETO_KBS_NOT_FIT_THRESHOLD": hf.VETO_KBS_NOT_FIT_THRESHOLD,
        "VETO_ML_HIGH_THRESHOLD": hf.VETO_ML_HIGH_THRESHOLD,
        "VETO_KEY_SUBJECT_MIN": hf.VETO_KEY_SUBJECT_MIN,
    }
    hf.VETO_KBS_NOT_FIT_THRESHOLD = -1
    hf.VETO_ML_HIGH_THRESHOLD = 101
    hf.VETO_KEY_SUBJECT_MIN = -1.0
    return snap


def _restore(snap: dict) -> None:
    for k, v in snap.items():
        setattr(hf, k, v)


def sweep_block(
    block: str,
    *,
    ml_weights: list[float],
    max_samples: int | None,
    no_veto: bool,
) -> list[dict]:
    logging.getLogger("kbs.hybrid_fusion").setLevel(logging.ERROR)

    df = pd.read_csv(str(REPO_ROOT / get_data_path(block)))
    features = get_features(block)
    X = df[features]
    y = df["nganh_hoc"]
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    model = hf.load_ml_model(block)
    if model is None:
        raise RuntimeError(f"Không load được model cho {block}")
    # Tránh cảnh báo joblib/sklearn 1.8 lặp hàng nghìn lần khi predict
    if hasattr(model, "set_params"):
        try:
            model.set_params(n_jobs=1)
        except ValueError:
            pass

    n = len(X_test)
    if max_samples is not None and max_samples > 0:
        n = min(n, max_samples)
    y_true = y_test.iloc[:n].values.astype(int)

    veto_snap = _disable_veto() if no_veto else None
    weight_snap = (hf.ML_WEIGHT, hf.KBS_WEIGHT)

    try:
        # ML thuần (đối chứng): chỉ chạy 1 lần
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            ml_pred = model.predict(X_test.iloc[:n])
        ml_metrics = _metrics(y_true, ml_pred.astype(int))
        ml_metrics.update({"ml_weight": None, "kbs_weight": None, "label": "ML only"})

        rows: list[dict] = [ml_metrics]
        for w_ml in ml_weights:
            w_kbs = 1.0 - w_ml
            hf.ML_WEIGHT = float(w_ml)
            hf.KBS_WEIGHT = float(w_kbs)
            y_pred = _predict_hybrid(block, model, X_test, max_samples=max_samples)
            m = _metrics(y_true, y_pred)
            m.update(
                {
                    "ml_weight": float(w_ml),
                    "kbs_weight": float(w_kbs),
                    "label": f"ML {w_ml:.2f} / KBS {w_kbs:.2f}",
                }
            )
            rows.append(m)
    finally:
        hf.ML_WEIGHT, hf.KBS_WEIGHT = weight_snap
        if veto_snap is not None:
            _restore(veto_snap)

    return rows


def _print_table(block: str, rows: list[dict], no_veto: bool) -> None:
    logger.info("\n" + "=" * 100)
    logger.info(
        "KHỐI %s — Quét tỉ lệ ML/KBS (VETO: %s)",
        block.upper(),
        "OFF" if no_veto else "ON",
    )
    logger.info("=" * 100)
    hdr = (
        f"{'Tỉ lệ':18} {'Acc':>8} {'P macro':>9} {'R macro':>9} {'F1 macro':>10} "
        f"{'P w':>8} {'R w':>8} {'F1 w':>8}"
    )
    logger.info(hdr)
    logger.info("-" * len(hdr))
    for r in rows:
        logger.info(
            f"{r['label']:18} {r['accuracy']:8.4f} {r['precision_macro']:9.4f} "
            f"{r['recall_macro']:9.4f} {r['f1_macro']:10.4f} "
            f"{r['precision_w']:8.4f} {r['recall_w']:8.4f} {r['f1_w']:8.4f}"
        )


def main() -> None:
    warnings.filterwarnings(
        "ignore",
        message=".*sklearn.utils.parallel.delayed.*",
        category=UserWarning,
    )
    try:
        from sklearn.exceptions import InconsistentVersionWarning

        warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
    except ImportError:
        pass

    p = argparse.ArgumentParser(description="Quét tỉ lệ ML/KBS cho Hybrid trên tập test")
    p.add_argument("--block", choices=["khtn", "khxh", "both"], default="both")
    p.add_argument("--max-samples", type=int, default=500, help="0 = toàn bộ tập test")
    p.add_argument(
        "--weights",
        default="0,0.3,0.5,0.7,1",
        help="Danh sách ML_WEIGHT (0-1); KBS_WEIGHT = 1 - ML_WEIGHT",
    )
    p.add_argument(
        "--no-veto",
        action="store_true",
        help="Tắt cơ chế VETO để đo ảnh hưởng 'thuần' của tỉ lệ trọng số",
    )
    args = p.parse_args()

    weights = [w for w in _parse_float_list(args.weights) if 0.0 <= w <= 1.0]
    max_samples = args.max_samples if args.max_samples > 0 else None
    blocks = ["khtn", "khxh"] if args.block == "both" else [args.block]

    all_rows: list[dict] = []
    for b in blocks:
        logger.info(
            "Đang quét tỉ lệ trên khối %s (max_samples=%s, weights=%s)...",
            b.upper(),
            max_samples,
            weights,
        )
        rows = sweep_block(
            b, ml_weights=weights, max_samples=max_samples, no_veto=args.no_veto
        )
        for r in rows:
            r["block"] = b
        _print_table(b, rows, no_veto=args.no_veto)
        all_rows.extend(rows)

    # Tổng kết: top 5 hybrid (loại ML-only) theo F1 macro
    hybrid_rows = [r for r in all_rows if r["ml_weight"] is not None]
    hybrid_rows.sort(key=lambda r: (r["f1_macro"], r["accuracy"]), reverse=True)
    logger.info("\n" + "=" * 100)
    logger.info("TOP 5 cấu hình HYBRID (mọi khối) theo F1 macro")
    logger.info("=" * 100)
    for r in hybrid_rows[:5]:
        logger.info(
            f"{r['block']:5} {r['label']:18} Acc={r['accuracy']:.4f}  "
            f"F1 macro={r['f1_macro']:.4f}  P macro={r['precision_macro']:.4f}  "
            f"R macro={r['recall_macro']:.4f}"
        )


if __name__ == "__main__":
    main()

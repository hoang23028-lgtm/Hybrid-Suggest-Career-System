"""
Huấn luyện mô hình Random Forest cho dự đoán ngành học
Train 2 model riêng cho KHTN và KHXH
"""

import argparse
import logging
import os
import pickle
import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score, train_test_split

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from kbs.classification_metrics import test_set_metrics
from kbs.config import (
    BALANCE_TRAIN_BLOCKS,
    CV_FOLDS,
    NGANH_HOC_MAP,
    RANDOM_STATE,
    TEST_SIZE,
    get_data_path,
    get_features,
    get_model_path,
    get_rf_params,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def undersample_train(X_train, y_train, seed=RANDOM_STATE):
    """Undersample tập train: mỗi lớp = min(count) mẫu."""
    counts = y_train.value_counts()
    min_count = int(counts.min())
    logger.info(f"   Cân bằng train: {len(counts)} lớp × {min_count:,} mẫu/lớp")
    sampled_idx = []
    for label in sorted(counts.index):
        idx = y_train[y_train == label].index
        sampled_idx.extend(
            pd.Series(idx).sample(n=min_count, random_state=seed).tolist()
        )
    X_bal = X_train.loc[sampled_idx]
    y_bal = y_train.loc[sampled_idx]
    perm = X_bal.sample(frac=1, random_state=seed).index
    return X_bal.loc[perm], y_bal.loc[perm]


def train_model(block, *, balance_train: bool | None = None):
    """Huấn luyện Random Forest Classifier cho 1 khối."""
    try:
        if balance_train is None:
            balance_train = block in BALANCE_TRAIN_BLOCKS

        data_path = str(REPO_ROOT / get_data_path(block))
        model_path = str(REPO_ROOT / get_model_path(block))
        feature_names = get_features(block)
        rf_params = get_rf_params(block)

        logger.info(f"\n{'=' * 60}")
        logger.info(f"HUẤN LUYỆN MODEL {block.upper()}")
        if balance_train:
            logger.info("   (train undersample theo lớp — cân bằng lớp thiểu số)")
        logger.info(f"{'=' * 60}")

        df = pd.read_csv(data_path)
        logger.info(f"Đọc dữ liệu: {data_path} ({len(df):,} mẫu)")

        X = df[feature_names]
        y = df["nganh_hoc"]

        dist = y.value_counts().sort_index()
        for label, cnt in dist.items():
            logger.info(f"   Phân bố: {label} = {cnt:,} ({100 * cnt / len(y):.1f}%)")

        logger.info(f"Chia dữ liệu: {int((1 - TEST_SIZE) * 100)}% train / {int(TEST_SIZE * 100)}% test")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )

        if balance_train:
            X_train, y_train = undersample_train(X_train, y_train)

        logger.info(f"   Training set (fit): {len(X_train):,}")
        logger.info(f"   Testing set (giữ phân bố gốc): {len(X_test):,}")

        logger.info(f"Huấn luyện Random Forest — params: {rf_params}")
        model = RandomForestClassifier(**rf_params)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        labels = sorted([int(v) for v in pd.unique(y)])
        m = test_set_metrics(y_test, y_pred, labels=labels)

        logger.info("\n   Chỉ số tập test:")
        logger.info(f"   Accuracy:           {m['accuracy']:.4f} ({m['accuracy'] * 100:.2f}%)")
        logger.info(f"   Balanced accuracy:  {m['balanced_accuracy']:.4f} ({m['balanced_accuracy'] * 100:.2f}%)")
        logger.info(f"   Precision (macro):  {m['precision']:.4f} ({m['precision'] * 100:.2f}%)")
        logger.info(f"   Recall (macro):     {m['recall']:.4f} ({m['recall'] * 100:.2f}%)")
        logger.info(f"   F1 (macro):           {m['f1']:.4f}")
        logger.info(
            f"   Precision (weighted): {m['precision_weighted']:.4f} "
            f"({m['precision_weighted'] * 100:.2f}%)"
        )
        logger.info(
            f"   Recall (weighted):    {m['recall_weighted']:.4f} "
            f"({m['recall_weighted'] * 100:.2f}%)"
        )
        logger.info(f"   F1 (weighted):        {m['f1_weighted']:.4f}")

        target_names = [NGANH_HOC_MAP[i] for i in labels]
        report = classification_report(
            y_test, y_pred, labels=labels, target_names=target_names, digits=4, zero_division=0
        )
        logger.info(f"\n   Classification Report (theo ngành):\n{report}")

        logger.info(f"Cross-validation ({CV_FOLDS}-fold trên tập train đã fit)...")
        cv_bal = cross_val_score(
            model, X_train, y_train, cv=CV_FOLDS, scoring="balanced_accuracy", n_jobs=-1
        )
        cv_f1 = cross_val_score(model, X_train, y_train, cv=CV_FOLDS, scoring="f1_macro", n_jobs=-1)
        logger.info(f"   CV balanced acc: {cv_bal.mean():.4f} (+/- {cv_bal.std():.4f})")
        logger.info(f"   CV F1 (macro):   {cv_f1.mean():.4f} (+/- {cv_f1.std():.4f})")

        logger.info("\nFeature Importance:")
        for name, imp in sorted(zip(feature_names, model.feature_importances_), key=lambda x: -x[1]):
            logger.info(f"   {name:10s}: {imp:.4f} {'#' * int(imp * 100)}")

        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        with open(model_path, "wb") as f:
            pickle.dump(model, f)

        logger.info(f"\n   TỔNG KẾT {block.upper()}:")
        logger.info(
            f"   Acc={m['accuracy']:.4f} | Bal-acc={m['balanced_accuracy']:.4f} | "
            f"P={m['precision']:.4f} R={m['recall']:.4f} F1={m['f1']:.4f} (macro)"
        )
        logger.info(f"   Model saved: {model_path}")

        return model, {
            "block": block,
            "test_accuracy": m["accuracy"],
            "test_balanced_accuracy": m["balanced_accuracy"],
            "test_precision": m["precision"],
            "test_recall": m["recall"],
            "test_f1": m["f1"],
            "test_precision_weighted": m["precision_weighted"],
            "test_recall_weighted": m["recall_weighted"],
            "test_f1_weighted": m["f1_weighted"],
            "cv_mean_balanced_accuracy": float(cv_bal.mean()),
            "cv_mean_f1_macro": float(cv_f1.mean()),
            "balance_train": balance_train,
        }

    except Exception as e:
        logger.error(f"Lỗi: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return None, {"block": block, "error": str(e), "test_accuracy": 0.0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-balance-train",
        action="store_true",
        help="Tắt undersample train (mặc định KHXH vẫn balance theo config)",
    )
    parser.add_argument(
        "--balance-train",
        choices=("khtn", "khxh", "both", "none"),
        default=os.getenv("TRAIN_BALANCE", "khxh"),
        help="Khối undersample train: mặc định khxh (env TRAIN_BALANCE)",
    )
    args = parser.parse_args()

    balance_map = {
        "none": frozenset(),
        "khtn": frozenset({"khtn"}),
        "khxh": frozenset({"khxh"}),
        "both": frozenset({"khtn", "khxh"}),
    }
    balance_blocks = balance_map.get(args.balance_train, frozenset({"khxh"}))
    if args.no_balance_train:
        balance_blocks = frozenset()

    logger.info("=" * 60)
    logger.info("BẮT ĐẦU HUẤN LUYỆN 2 MODEL")
    logger.info("=" * 60)

    _, m_khtn = train_model("khtn", balance_train="khtn" in balance_blocks)
    _, m_khxh = train_model("khxh", balance_train="khxh" in balance_blocks)

    logger.info(f"\n{'=' * 60}")
    logger.info("TỔNG KẾT CHUNG")
    logger.info(f"{'=' * 60}")
    for block, m in (("KHTN", m_khtn), ("KHXH", m_khxh)):
        logger.info(
            f"   {block}: acc={m.get('test_accuracy', 0):.4f} "
            f"P={m.get('test_precision', 0):.4f} R={m.get('test_recall', 0):.4f} "
            f"F1={m.get('test_f1', 0):.4f} (macro) | "
            f"F1_w={m.get('test_f1_weighted', 0):.4f}"
        )


if __name__ == "__main__":
    main()

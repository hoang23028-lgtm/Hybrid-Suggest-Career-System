"""Chỉ số phân loại đa lớp (dùng chung train / eval)."""

from __future__ import annotations

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)


def multiclass_prf(y_true, y_pred, *, labels=None) -> dict[str, float]:
    """
    Precision / recall / F1 cho phân loại đa lớp.

    - macro: trung bình không trọng số theo lớp (phản ánh lớp thiểu số).
    - weighted: trung bình có trọng số theo support (gần accuracy khi lớp lệch).
    """
    kw = {"average": "macro", "zero_division": 0}
    kw_w = {"average": "weighted", "zero_division": 0}
    if labels is not None:
        kw["labels"] = labels
        kw_w["labels"] = labels
    return {
        "precision": float(precision_score(y_true, y_pred, **kw)),
        "recall": float(recall_score(y_true, y_pred, **kw)),
        "f1": float(f1_score(y_true, y_pred, **kw)),
        "precision_weighted": float(precision_score(y_true, y_pred, **kw_w)),
        "recall_weighted": float(recall_score(y_true, y_pred, **kw_w)),
        "f1_weighted": float(f1_score(y_true, y_pred, **kw_w)),
    }


def test_set_metrics(y_true, y_pred, *, labels=None) -> dict[str, float]:
    """Gói accuracy + balanced accuracy + macro/weighted PRF."""
    out = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
    }
    out.update(multiclass_prf(y_true, y_pred, labels=labels))
    return out

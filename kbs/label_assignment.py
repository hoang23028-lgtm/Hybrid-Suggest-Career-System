"""Gán mã ngành mục tiêu (cột nganh_hoc) cho hồ sơ đủ 6 môn theo khối."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from .config import get_features, get_majors
from .knowledge_rules import KnowledgeRuleEngine

logger = logging.getLogger(__name__)

_BLOCK_REQUIRED = {
    'khtn': ['toan', 'van', 'anh', 'ly', 'hoa', 'sinh'],
    'khxh': ['toan', 'van', 'anh', 'lich_su', 'dia_ly', 'gdcd'],
}

_engines: dict[str, KnowledgeRuleEngine] = {}


def _get_engine(block: str) -> KnowledgeRuleEngine:
    if block not in _engines:
        _engines[block] = KnowledgeRuleEngine(block=block)
    return _engines[block]


def mask_complete_block(df: pd.DataFrame, block: str) -> pd.Series:
    """True nếu hàng có đủ điểm 6 môn của khối."""
    required = _BLOCK_REQUIRED[block]
    return df[required].notna().all(axis=1)


def assign_major_labels(df: pd.DataFrame, block: str, *, log_every: int = 50_000) -> pd.Series:
    """Trả về Series mã ngành (int) cùng index với df."""
    features = get_features(block)
    engine = _get_engine(block)
    n = len(df)
    labels = np.empty(n, dtype=np.int64)

    for i, row in enumerate(df[features].to_numpy(dtype=float, copy=False)):
        labels[i] = engine.predict_major_index(row.tolist())
        if log_every and (i + 1) % log_every == 0:
            logger.info(f"  [{block.upper()}] Đã xử lý {i + 1:,}/{n:,} mẫu")

    return pd.Series(labels, index=df.index, name='nganh_hoc')


def label_distribution(series: pd.Series, block: str) -> dict[int, int]:
    """Đếm nhãn theo major index."""
    valid = set(get_majors(block))
    vc = series.value_counts().sort_index()
    return {int(k): int(v) for k, v in vc.items() if int(k) in valid}

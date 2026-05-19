"""Ánh xạ tên ngành trong CSV gốc sang mã số nguyên (theo khối)."""

from __future__ import annotations

import pandas as pd

from .config import NGANH_HOC_MAP, get_majors

NAME_TO_MAJOR_ID = {name.strip(): idx for idx, name in NGANH_HOC_MAP.items()}


def map_raw_label_series(label_series: pd.Series, block: str) -> pd.Series:
    """Map chuỗi nhãn → mã ngành; NaN nếu không map được hoặc ngoài khối."""
    valid = set(get_majors(block))
    mapped = label_series.astype(str).str.strip().map(NAME_TO_MAJOR_ID)
    mapped = pd.to_numeric(mapped, errors="coerce")
    return mapped.where(mapped.isin(valid))

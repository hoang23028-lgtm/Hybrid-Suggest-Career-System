"""
Tiền xử lý dữ liệu THPT 2024 → data_khtn.csv / data_khxh.csv

1. Đọc diem_thi_thpt_2024.csv
2. Đổi tên cột
3. Lọc đủ 6 môn theo khối
4. Ghi cột nganh_hoc (ngành mục tiêu theo khối)
5. Lưu file train

Usage:
  python scripts/create_data.py
"""

import logging
import os
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from kbs.config import (
    RAW_DATA_PATH,
    RAW_COLUMN_MAP,
    DATA_PATH_KHTN,
    DATA_PATH_KHXH,
    KHTN_FEATURES,
    KHXH_FEATURES,
    NGANH_HOC_MAP,
    get_features,
    get_majors,
)
from kbs.label_assignment import assign_major_labels, label_distribution, mask_complete_block
from kbs.external_labels import map_raw_label_series

LABEL_COL = "nganh_hoc"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_and_rename(path):
    """Đọc CSV gốc và đổi tên cột."""
    logger.info(f"Đọc dữ liệu gốc: {path}")
    df = pd.read_csv(path)
    logger.info(f"  Tổng số hàng: {len(df):,}")
    return df.rename(columns=RAW_COLUMN_MAP)


def _log_label_distribution(filtered: pd.DataFrame, block: str) -> None:
    dist = label_distribution(filtered[LABEL_COL], block)
    for major_id, count in sorted(dist.items()):
        name = NGANH_HOC_MAP.get(major_id, "?")
        logger.info(f"    nganh_hoc={major_id} ({name}): {count:,}")
    missing = set(get_majors(block)) - set(dist.keys())
    if missing:
        logger.warning(
            f"  [{block.upper()}] Không có mẫu cho ngành: {sorted(missing)}"
        )


def filter_and_label_block(df: pd.DataFrame, block: str, label_source: str = "kbs") -> pd.DataFrame:
    """Lọc theo khối và ghi cột nganh_hoc."""
    if label_source not in ("raw", "kbs"):
        raise ValueError(f"label_source không hợp lệ: {label_source}")

    features = get_features(block)
    mask = mask_complete_block(df, block)
    n_block = int(mask.sum())
    logger.info(f"  [{block.upper()}] Có đủ 6 môn khối: {n_block:,} / {len(df):,}")

    if label_source == "raw":
        if LABEL_COL not in df.columns:
            raise ValueError(f"Thiếu cột {LABEL_COL} trong CSV gốc")
        out = df.loc[mask, features].copy()
        raw_mapped = map_raw_label_series(df.loc[mask, LABEL_COL], block)
        before = len(out)
        out[LABEL_COL] = raw_mapped
        out = out[out[LABEL_COL].notna()].copy()
        out[LABEL_COL] = out[LABEL_COL].astype(int)
        dropped = before - len(out)
        if dropped:
            logger.info(
                f"  [{block.upper()}] Loại {dropped:,} hàng (mã ngành trống / ngoài khối)"
            )
        logger.info(f"  [{block.upper()}] Hoàn tất: {len(out):,} mẫu")
        _log_label_distribution(out, block)
        return out

    filtered = df.loc[mask, features].copy()
    if filtered.empty:
        filtered[LABEL_COL] = pd.Series(dtype=int)
        return filtered

    logger.info(f"  [{block.upper()}] Ánh xạ cột nganh_hoc...")
    filtered[LABEL_COL] = assign_major_labels(filtered, block)
    _log_label_distribution(filtered, block)
    return filtered


def balance_data(df, label_col="nganh_hoc", valid_majors=None, seed=42):
    """Cân bằng dữ liệu bằng undersampling (tuỳ chọn, không gọi trong main)."""
    if valid_majors:
        df = df[df[label_col].isin(valid_majors)].copy()
    counts = df[label_col].value_counts()
    min_count = counts.min()
    balanced_parts = []
    for major in valid_majors:
        major_df = df[df[label_col] == major]
        if len(major_df) >= min_count:
            balanced_parts.append(major_df.sample(n=min_count, random_state=seed))
        else:
            balanced_parts.append(major_df.sample(n=min_count, random_state=seed, replace=True))
    return pd.concat(balanced_parts, ignore_index=True).sample(frac=1, random_state=seed).reset_index(drop=True)


def create_dataset(block: str, label_source: str = "kbs"):
    """Tạo bộ dữ liệu cho 1 khối."""
    logger.info(f"\n{'=' * 60}")
    logger.info(f"TẠO DỮ LIỆU {block.upper()}")
    logger.info(f"{'=' * 60}")

    df = load_and_rename(RAW_DATA_PATH)
    filtered = filter_and_label_block(df, block, label_source=label_source)

    output_path = DATA_PATH_KHTN if block == "khtn" else DATA_PATH_KHXH
    features = KHTN_FEATURES if block == "khtn" else KHXH_FEATURES

    logger.info("\n  Thống kê cuối cùng:")
    logger.info(f"  Shape: {filtered.shape}")
    for f in features:
        logger.info(
            f"    {f}: mean={filtered[f].mean():.2f}, std={filtered[f].std():.2f}, "
            f"min={filtered[f].min():.1f}, max={filtered[f].max():.1f}"
        )

    filtered.to_csv(output_path, index=False)
    logger.info(f"\n  Lưu: {output_path} ({len(filtered):,} mẫu)")
    return filtered


def main():
    # Chế độ raw chỉ qua biến môi trường (không hiển thị CLI công khai)
    label_source = os.getenv("LABEL_SOURCE", "kbs").strip().lower() or "kbs"
    if label_source not in ("raw", "kbs"):
        label_source = "kbs"

    logger.info("=" * 60)
    logger.info("TIỀN XỬ LÝ DỮ LIỆU THPT 2024")
    logger.info("=" * 60)

    df_khtn = create_dataset("khtn", label_source=label_source)
    df_khxh = create_dataset("khxh", label_source=label_source)

    logger.info(f"\n{'=' * 60}")
    logger.info("HOÀN TẤT")
    logger.info(f"{'=' * 60}")
    logger.info(f"  KHTN: {len(df_khtn):,} mẫu → {DATA_PATH_KHTN}")
    logger.info(f"  KHXH: {len(df_khxh):,} mẫu → {DATA_PATH_KHXH}")


if __name__ == "__main__":
    main()

"""
Tiền xử lý dữ liệu THPT 2024 → 2 bộ dữ liệu (KHTN + KHXH)

Quy trình:
  1. Đọc dữ liệu gốc diem_thi_thpt_2024.csv (~1M thí sinh)
  2. Đổi tên cột theo chuẩn nội bộ
  3. Lọc thí sinh KHTN (có Lý, Hóa, Sinh) và KHXH (có Sử, Địa, GDCD)
  4. Loại bỏ hàng thiếu dữ liệu ở môn bắt buộc (Toán, Văn, Anh)
  5. Lưu data_khtn.csv và data_khxh.csv (không gắn nhãn)
"""

import logging
import sys
from pathlib import Path
import pandas as pd
import numpy as np


REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from kbs.config import (
    RAW_DATA_PATH, RAW_COLUMN_MAP,
    DATA_PATH_KHTN, DATA_PATH_KHXH,
    KHTN_FEATURES, KHXH_FEATURES,
    RANDOM_STATE
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# XỬ LÝ CHÍNH
# ============================================================================
def load_and_rename(path):
    """Đọc CSV gốc và đổi tên cột"""
    logger.info(f"Đọc dữ liệu gốc: {path}")
    df = pd.read_csv(path)
    logger.info(f"  Tổng số hàng: {len(df):,}")
    logger.info(f"  Cột: {list(df.columns)}")
    
    # Đổi tên cột
    df = df.rename(columns=RAW_COLUMN_MAP)
    return df


def filter_block(df, block):
    """Lọc thí sinh theo khối thi"""
    if block == 'khtn':
        features = KHTN_FEATURES
        block_specific = ['ly', 'hoa', 'sinh']
    else:
        features = KHXH_FEATURES
        block_specific = ['lich_su', 'dia_ly', 'gdcd']
    
    # Lọc: phải có đủ 3 môn bắt buộc + 3 môn tự chọn
    required = ['toan', 'van', 'anh'] + block_specific
    mask = df[required].notna().all(axis=1)
    
    filtered = df[mask][features].copy()
    logger.info(f"  [{block.upper()}] Sau lọc: {len(filtered):,} thí sinh (từ {len(df):,})")
    
    return filtered


def balance_data(df, label_col='nganh_hoc', valid_majors=None, seed=42):
    """Cân bằng dữ liệu bằng undersampling"""
    if valid_majors:
        df = df[df[label_col].isin(valid_majors)].copy()
    
    counts = df[label_col].value_counts()
    logger.info(f"  Phân bố trước cân bằng:")
    for major, count in counts.items():
        logger.info(f"    Ngành {major}: {count:,}")
    
    min_count = counts.min()
    logger.info(f"  Cân bằng về: {min_count:,} mẫu/ngành")
    
    balanced_parts = []
    for major in valid_majors:
        major_df = df[df[label_col] == major]
        if len(major_df) >= min_count:
            balanced_parts.append(major_df.sample(n=min_count, random_state=seed))
        else:
            # Nếu thiếu: oversample
            balanced_parts.append(major_df.sample(n=min_count, random_state=seed, replace=True))
    
    result = pd.concat(balanced_parts, ignore_index=True)
    result = result.sample(frac=1, random_state=seed).reset_index(drop=True)  # Shuffle
    
    logger.info(f"  Tổng sau cân bằng: {len(result):,} ({len(valid_majors)} ngành × {min_count:,})")
    return result


def create_dataset(block):
    """Tạo bộ dữ liệu cho 1 khối"""
    logger.info(f"\n{'='*60}")
    logger.info(f"TẠO DỮ LIỆU {block.upper()}")
    logger.info(f"{'='*60}")
    
    # 1. Đọc dữ liệu gốc
    df = load_and_rename(RAW_DATA_PATH)
    
    # 2. Lọc theo khối
    filtered = filter_block(df, block)

    output_path = DATA_PATH_KHTN if block == 'khtn' else DATA_PATH_KHXH

    # 3. Thống kê
    logger.info(f"\n  Thống kê cuối cùng:")
    logger.info(f"  Shape: {filtered.shape}")
    features = KHTN_FEATURES if block == 'khtn' else KHXH_FEATURES
    for f in features:
        logger.info(
            f"    {f}: mean={filtered[f].mean():.2f}, std={filtered[f].std():.2f}, "
            f"min={filtered[f].min():.1f}, max={filtered[f].max():.1f}"
        )

    # 4. Lưu 
    filtered.to_csv(output_path, index=False)
    logger.info(f"\n  Lưu: {output_path} ({len(filtered):,} mẫu)")

    return filtered


def main():
    """Tạo 2 bộ dữ liệu"""
    logger.info("="*60)
    logger.info("TIỀN XỬ LÝ DỮ LIỆU THPT 2024")
    logger.info("="*60)
    
    df_khtn = create_dataset('khtn')
    df_khxh = create_dataset('khxh')
    
    logger.info(f"\n{'='*60}")
    logger.info("HOÀN TẤT")
    logger.info(f"{'='*60}")
    logger.info(f"  KHTN: {len(df_khtn):,} mẫu → {DATA_PATH_KHTN}")
    logger.info(f"  KHXH: {len(df_khxh):,} mẫu → {DATA_PATH_KHXH}")


if __name__ == "__main__":
    main()

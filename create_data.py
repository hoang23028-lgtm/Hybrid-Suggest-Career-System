"""
Tiền xử lý dữ liệu THPT 2024 → 2 bộ dữ liệu (KHTN + KHXH)

Quy trình:
  1. Đọc dữ liệu gốc diem_thi_thpt_2024.csv (~1M thí sinh)
  2. Đổi tên cột theo chuẩn nội bộ
  3. Lọc thí sinh KHTN (có Lý, Hóa, Sinh) và KHXH (có Sử, Địa, GDCD)
  4. Loại bỏ hàng thiếu dữ liệu ở môn bắt buộc (Toán, Văn, Anh)
  5. Gán nhãn ngành học bằng heuristic chuyên gia
  6. Cân bằng dữ liệu (undersampling về min class)
  7. Lưu data_khtn.csv và data_khxh.csv
"""

import logging
import pandas as pd
import numpy as np
from config import (
    RAW_DATA_PATH, RAW_COLUMN_MAP,
    DATA_PATH_KHTN, DATA_PATH_KHXH,
    KHTN_FEATURES, KHXH_FEATURES,
    KHTN_MAJORS, KHXH_MAJORS,
    RANDOM_STATE
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# GÁN NHÃN NGÀNH HỌC
# ============================================================================
def assign_major_khtn(row):
    """
    Gán ngành cho thí sinh KHTN dựa trên điểm số.
    Ưu tiên từ ngưỡng cao → thấp.
    
    Ngành: 0=IT, 1=Kinh tế, 2=Y khoa, 3=Kỹ thuật, 4=Nông-Lâm
    """
    toan, van, anh = row['toan'], row['van'], row['anh']
    ly, hoa, sinh = row['ly'], row['hoa'], row['sinh']
    
    scores = {}
    
    # Kỹ thuật: Toán mạnh + Lý mạnh
    if toan >= 8 and ly >= 8:
        scores[3] = toan + ly + hoa * 0.5
    
    # Y khoa: Sinh mạnh + Hóa mạnh
    if sinh >= 7.5 and hoa >= 7.5:
        scores[2] = sinh + hoa + ly * 0.5
    
    # IT: Toán mạnh + Lý khá
    if toan >= 7.5 and ly >= 7:
        scores[0] = toan + ly + anh * 0.3
    
    # Nông-Lâm: Sinh khá + Hóa khá
    if sinh >= 7 and hoa >= 7:
        scores[4] = sinh + hoa
    
    # Kinh tế: Toán + Anh
    if toan >= 6 and anh >= 7:
        scores[1] = toan + anh + van * 0.3
    
    if scores:
        return max(scores, key=scores.get)
    
    # Fallback: chọn ngành phù hợp nhất dựa trên tổ hợp điểm
    fallback = {
        0: toan * 0.5 + ly * 0.3 + anh * 0.2,
        1: toan * 0.3 + anh * 0.4 + van * 0.3,
        2: sinh * 0.4 + hoa * 0.4 + ly * 0.2,
        3: toan * 0.4 + ly * 0.4 + hoa * 0.2,
        4: sinh * 0.4 + hoa * 0.3 + toan * 0.3,
    }
    return max(fallback, key=fallback.get)


def assign_major_khxh(row):
    """
    Gán ngành cho thí sinh KHXH dựa trên điểm số.
    
    Ngành: 1=Kinh tế, 5=Sư phạm, 6=Luật, 7=Du lịch
    """
    toan, van, anh = row['toan'], row['van'], row['anh']
    lich_su, dia_ly, gdcd = row['lich_su'], row['dia_ly'], row['gdcd']
    
    scores = {}
    
    # Luật: GDCD + Sử mạnh
    if gdcd >= 7.5 and lich_su >= 7.5:
        scores[6] = gdcd + lich_su + van * 0.5
    
    # Sư phạm: Văn + Anh mạnh
    if van >= 7 and anh >= 7:
        scores[5] = van + anh + lich_su * 0.3
    
    # Du lịch: Địa + Anh khá
    if dia_ly >= 6.5 and anh >= 6.5:
        scores[7] = dia_ly + anh + van * 0.3
    
    # Kinh tế: Toán + Anh
    if toan >= 6 and anh >= 7:
        scores[1] = toan + anh + van * 0.3
    
    if scores:
        return max(scores, key=scores.get)
    
    # Fallback
    fallback = {
        1: toan * 0.3 + anh * 0.4 + van * 0.3,
        5: van * 0.4 + anh * 0.3 + lich_su * 0.3,
        6: gdcd * 0.4 + lich_su * 0.3 + van * 0.3,
        7: dia_ly * 0.3 + anh * 0.4 + van * 0.3,
    }
    return max(fallback, key=fallback.get)


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
    
    # 3. Gán nhãn ngành học
    logger.info(f"  Gán nhãn ngành học...")
    if block == 'khtn':
        filtered['nganh_hoc'] = filtered.apply(assign_major_khtn, axis=1)
        valid_majors = KHTN_MAJORS
        output_path = DATA_PATH_KHTN
    else:
        filtered['nganh_hoc'] = filtered.apply(assign_major_khxh, axis=1)
        valid_majors = KHXH_MAJORS
        output_path = DATA_PATH_KHXH
    
    # 4. Cân bằng
    balanced = balance_data(filtered, valid_majors=valid_majors, seed=RANDOM_STATE)
    
    # 5. Thống kê
    logger.info(f"\n  Thống kê cuối cùng:")
    logger.info(f"  Shape: {balanced.shape}")
    features = KHTN_FEATURES if block == 'khtn' else KHXH_FEATURES
    for f in features:
        logger.info(f"    {f}: mean={balanced[f].mean():.2f}, std={balanced[f].std():.2f}, "
                     f"min={balanced[f].min():.1f}, max={balanced[f].max():.1f}")
    
    logger.info(f"\n  Phân bố ngành:")
    for major, count in balanced['nganh_hoc'].value_counts().sort_index().items():
        logger.info(f"    Ngành {major}: {count:,} ({count/len(balanced)*100:.1f}%)")
    
    # 6. Lưu
    balanced.to_csv(output_path, index=False)
    logger.info(f"\n  Lưu: {output_path} ({len(balanced):,} mẫu)")
    
    return balanced


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

import pandas as pd
import numpy as np
import logging
import os
from config import FEATURE_NAMES, NGANH_HOC_MAP, NUM_SAMPLES, DATA_PATH

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def assign_major(row):
    """
    Gán ngành học dựa trên quy luật tối ưu cho 8 ngành.
    
    Ngành:
    0: IT - Công nghệ thông tin (Toán, Lý, Tin)
    1: Kinh tế - Kinh doanh (Toán, Anh, Văn)
    2: Y khoa - Sức khỏe (Sinh, Hóa, Lý)
    3: Kỹ thuật - Xây dựng (Toán, Lý, Tin)
    4: Nông - Lâm - Ngư (Sinh, Địa lý, Hóa)
    5: Sư phạm - Giáo dục (Văn, Anh, Lịch sử)
    6: Luật pháp (Lịch sử, Văn, Anh)
    7: Du lịch - Khách sạn (Địa lý, Anh, Văn)
    """
    toan = row['toan']
    ly = row['ly']
    hoa = row['hoa']
    sinh = row['sinh']
    van = row['van']
    anh = row['anh']
    lich_su = row['lich_su']
    dia_ly = row['dia_ly']
    tin_hoc = row['tin_hoc']
    
    # === CÁC NHÓM ĐIỂM TỔNG HỢP ===
    khoa_hoc = (toan + ly + hoa + sinh) / 4
    cong_nghe = (toan + ly + tin_hoc) / 3
    sinh_hoc = (sinh + hoa + ly) / 3
    nhan_van = (van + anh + lich_su) / 3
    kinh_te = (toan + anh) / 2
    du_lich = (dia_ly + anh + van) / 3
    
    # === QUYẾT ĐỊNH NGÀNH ===
    
    # 0: IT (Toán-Lý-Tin cao)
    if toan >= 7.5 and tin_hoc >= 7.5 and (toan + tin_hoc + ly) / 3 >= 7:
        return 0
    
    # 3: Kỹ thuật (Toán-Lý rất cao)
    elif toan >= 8 and ly >= 8:
        return 3
    
    # 2: Y khoa (Sinh-Hóa cao, Lý ok)
    elif sinh >= 7.5 and hoa >= 7.5 and ly >= 6:
        return 2
    
    # 4: Nông-Lâm-Ngư (Sinh-Địa lý cao, Hóa ok)
    elif sinh >= 7 and dia_ly >= 7.5 and hoa >= 6:
        return 4
    
    # Trường hợp khác trong khoa học tự nhiên
    elif khoa_hoc >= 7 and sinh >= 6.5:
        return 2  # Y khoa nếu sinh ok
    elif khoa_hoc >= 7 and tin_hoc >= 6:
        return 0  # IT nếu tin ok
    elif khoa_hoc >= 7.5:
        return 3  # Kỹ thuật nếu khoa học rất tốt
    
    # === NHÓM NHÂN VĂN ===
    
    # 6: Luật pháp (Lịch sử-Văn kao)
    elif lich_su >= 7.5 and van >= 7:
        return 6
    
    # 5: Sư phạm (Văn-Anh cao)
    elif van >= 7 and anh >= 7:
        return 5
    
    # 1: Kinh tế (Toán ok + Anh cao, có văn)
    elif toan >= 6 and anh >= 7 and van >= 5.5:
        return 1
    
    # 7: Du lịch (Địa lý-Anh-Văn ok)
    elif dia_ly >= 6.5 and anh >= 6.5 and van >= 6:
        return 7
    
    # === CÁC TRƯỜNG HỢP KHÁC ===
    elif khoa_hoc >= 6:
        # Có khoa học tự nhiên
        if sinh >= 5.5:
            return 2
        elif tin_hoc >= 5.5:
            return 0
        else:
            return 3
    
    elif nhan_van >= 6.5:
        # Có nhân văn
        if lich_su >= 6:
            return 6
        elif anh >= 6.5:
            return 5
        else:
            return 1
    
    else:
        # Fallback: dựa trên điểm cao nhất
        scores = {
            0: toan + tin_hoc,
            1: toan + anh,
            2: sinh + hoa,
            3: toan + ly,
            4: sinh + dia_ly,
            5: van + anh,
            6: lich_su + van,
            7: dia_ly + anh
        }
        return max(scores, key=scores.get)

def generate_synthetic_data(num_samples=NUM_SAMPLES, output_file=DATA_PATH, balance=False, class_ratios=None):
    """
    Tạo dữ liệu tổng hợp cho hệ thống AI gợi ý ngành học.
    
    Args:
        num_samples (int): Tổng số lượng mẫu dữ liệu cần tạo
        output_file (str): Tên file CSV output
        balance (bool): Nếu True, dữ liệu sẽ cân bằng hoàn hảo (12.5% mỗi ngành)
        class_ratios (list): Danh sách tỷ lệ (%) cho mỗi ngành, tổng = 100. 
                            Nếu None và balance=False, sẽ dùng tỷ lệ không cân bằng 12-13%
    
    Returns:
        pd.DataFrame: DataFrame chứa dữ liệu được tạo
    """
    # Xác định tỷ lệ cho mỗi ngành
    if balance:
        logger.info(f"Bắt đầu tạo {num_samples} mẫu dữ liệu tổng hợp CÂN BẰNG (12.5% mỗi ngành)...")
        # Cân bằng hoàn hảo: mỗi ngành 12.5%
        class_ratios = [12.5] * 8
    elif class_ratios is None:
        logger.info(f"Bắt đầu tạo {num_samples} mẫu dữ liệu tổng hợp KHÔNG CÂN BẰNG (tỷ lệ lẻ dữ liệu thực tế)...")
        # Tỷ lệ không cân bằng với số lẻ (giống dữ liệu thực tế)
        class_ratios = [12.35, 12.78, 12.05, 13.21, 12.54, 12.89, 12.43, 12.75]  # Tổng = 100%
    else:
        logger.info(f"Bắt đầu tạo {num_samples} mẫu dữ liệu tổng hợp với tỷ lệ tùy chỉnh...")
    
    np.random.seed(42)
    
    num_classes = len(NGANH_HOC_MAP)
    # Tính số mẫu cho mỗi ngành dựa trên tỷ lệ
    target_per_class = {i: int((class_ratios[i] / 100) * num_samples) for i in range(num_classes)}
    
    collected_data = []
    class_counts = {i: 0 for i in range(num_classes)}
    batch_size = 50000
    
    # Tính tổng mẫu cần thiết (có thể lệch do làm tròn)
    total_target = sum(target_per_class.values())
    
    while sum(class_counts.values()) < total_target:
        # Tạo batch dữ liệu ngẫu nhiên
        batch_df = pd.DataFrame({
            'toan': np.random.uniform(3, 10, batch_size),
            'ly': np.random.uniform(3, 10, batch_size),
            'hoa': np.random.uniform(3, 10, batch_size),
            'sinh': np.random.uniform(3, 10, batch_size),
            'van': np.random.uniform(3, 10, batch_size),
            'anh': np.random.uniform(3, 10, batch_size),
            'lich_su': np.random.uniform(3, 10, batch_size),
            'dia_ly': np.random.uniform(3, 10, batch_size),
            'tin_hoc': np.random.uniform(3, 10, batch_size)
        })
        
        # Gán nhãn cho batch
        batch_df['nganh_hoc'] = batch_df.apply(assign_major, axis=1)
        
        # Lọc và lấy số lượng mẫu cần thiết cho từng class
        for class_id in range(num_classes):
            if class_counts[class_id] < target_per_class[class_id]:
                needed = target_per_class[class_id] - class_counts[class_id]
                class_samples = batch_df[batch_df['nganh_hoc'] == class_id]
                
                samples_to_add = class_samples.head(needed)
                if not samples_to_add.empty:
                    collected_data.append(samples_to_add)
                    class_counts[class_id] += len(samples_to_add)
                    
        current_total = sum(class_counts.values())
        logger.info(f"Đã thu thập: {current_total}/{total_target} mẫu...")
            
    # Nối tất cả dữ liệu và xáo trộn (shuffle)
    data = pd.concat(collected_data, ignore_index=True)
    data = data.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Validation dữ liệu
    if data.isnull().sum().sum() > 0:
        logger.warning(" Phát hiện giá trị NULL trong dữ liệu!")
    
    if not all(val in NGANH_HOC_MAP for val in data['nganh_hoc'].unique()):
        logger.error(" Lỗi: Có giá trị nhãn không hợp lệ!")
        return None
    
    # Thống kê phân bố dữ liệu
    logger.info("\n Phân bố ngành học:")
    for major_id in sorted(NGANH_HOC_MAP.keys()):
        major_name = NGANH_HOC_MAP[major_id]
        count = (data['nganh_hoc'] == major_id).sum()
        percentage = (count / len(data)) * 100
        logger.info(f"  {major_name}: {count} mẫu ({percentage:.1f}%)")
    
    # Lưu dữ liệu
    try:
        data.to_csv(output_file, index=False)
        logger.info(f"\n Thành công: Dữ liệu đã được lưu tại '{output_file}'")
        logger.info(f"  Kích thước: {len(data)} hàng × {len(data.columns)} cột")
        logger.info(f"  Features: {FEATURE_NAMES}")
        return data
    except Exception as e:
        logger.error(f" Lỗi khi lưu file: {e}")
        return None

if __name__ == "__main__":
    import sys
    
    # Kiểm tra tham số dòng lệnh
    balance = "--balanced" in sys.argv or "--balance" in sys.argv
    
    if balance:
        generate_synthetic_data(balance=True)
    else:
        generate_synthetic_data(balance=False)
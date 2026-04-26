"""
Retrain Pipeline - Bước 7 (Phần 2)
Tự động retrain mô hình khi phát hiện suy giảm hiệu suất
"""

import os
import pickle
import logging
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from config import (
    DATA_PATH, MODEL_PATH, FEATURE_NAMES, NGANH_HOC_MAP, 
    RF_PARAMS, TEST_SIZE, CV_FOLDS
)
from monitoring import ModelMonitor, PredictionLogger

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASELINE_ACCURACY = 0.885  # Accuracy baseline (từ training gốc)
DEGRADATION_THRESHOLD = 0.02  # Trigger retrain nếu suy giảm > 2%
MODEL_BACKUP_DIR = 'model_backups'


class RetrainPipeline:
    """Quản lý việc retrain tự động"""
    
    def __init__(self):
        self.monitor = ModelMonitor()
        self.prediction_logger = PredictionLogger()
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Tạo thư mục backup nếu chưa có"""
        os.makedirs(MODEL_BACKUP_DIR, exist_ok=True)
    
    def should_retrain(self):
        """Kiểm tra xem có cần retrain hay không"""
        logger.info("\n" + "="*70)
        logger.info("🔍 KIỂM TRA NHU CẦU RETRAIN")
        logger.info("="*70)
        
        trend = self.monitor.get_performance_trend()
        
        if trend is None:
            logger.info("\n⚠️ Chưa có đủ lịch sử để quyết định")
            return False
        
        latest_ml_acc = trend['ml_accuracies'][-1]
        degradation = BASELINE_ACCURACY - latest_ml_acc
        
        logger.info(f"\n📊 Phân tích:")
        logger.info(f"   Baseline Accuracy: {BASELINE_ACCURACY:.4f}")
        logger.info(f"   Hiện tại: {latest_ml_acc:.4f}")
        logger.info(f"   Suy giảm: {degradation:+.4f}")
        logger.info(f"   Ngưỡng: {DEGRADATION_THRESHOLD:.4f}")
        
        if degradation > DEGRADATION_THRESHOLD:
            logger.warning(f"🔴 CẢNH BÁO: Suy giảm vượt ngưỡng ({degradation:.4f} > {DEGRADATION_THRESHOLD})")
            logger.warning(f"   → CẦN RETRAIN")
            return True
        else:
            logger.info(f"✅ Hiệu suất ổn định")
            return False
    
    def retrain_model(self, use_new_data=False, new_data_path=None):
        """Retrain mô hình"""
        logger.info("\n" + "="*70)
        logger.info("🔄 RETRAIN MÔ HÌNH")
        logger.info("="*70)
        
        try:
            # 1. Load dữ liệu
            logger.info("\n1️⃣  Load dữ liệu...")
            if use_new_data and new_data_path:
                data_path = new_data_path
                logger.info(f"   Sử dụng dữ liệu mới: {new_data_path}")
            else:
                data_path = DATA_PATH
                logger.info(f"   Sử dụng dữ liệu cũ: {data_path}")
            
            df = pd.read_csv(data_path)
            logger.info(f"   ✓ Load {len(df)} samples")
            
            # 2. Chuẩn bị dữ liệu
            logger.info("\n2️⃣  Chuẩn bị dữ liệu...")
            X = df[FEATURE_NAMES]
            y = df['nganh_hoc']
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=TEST_SIZE, random_state=42, stratify=y
            )
            logger.info(f"   Training: {len(X_train)}, Testing: {len(X_test)}")
            
            # 3. Backup mô hình cũ
            logger.info("\n3️⃣  Backup mô hình cũ...")
            if os.path.exists(MODEL_PATH):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(MODEL_BACKUP_DIR, f"rf_model_{timestamp}.pkl")
                os.rename(MODEL_PATH, backup_path)
                logger.info(f"   ✓ Backup: {backup_path}")
            
            # 4. Huấn luyện mô hình mới
            logger.info("\n4️⃣  Huấn luyện Random Forest...")
            model = RandomForestClassifier(**RF_PARAMS)
            model.fit(X_train, y_train)
            logger.info(f"   ✓ Huấn luyện xong")
            
            # 5. Đánh giá
            logger.info("\n5️⃣  Đánh giá mô hình...")
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"   Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=CV_FOLDS, scoring='accuracy', n_jobs=-1)
            logger.info(f"   Cross-val Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
            
            # 6. So sánh với baseline
            logger.info("\n6️⃣  So sánh với baseline...")
            diff = accuracy - BASELINE_ACCURACY
            logger.info(f"   Baseline: {BASELINE_ACCURACY:.4f}")
            logger.info(f"   Mới: {accuracy:.4f}")
            logger.info(f"   Thay đổi: {diff:+.4f} ({diff/BASELINE_ACCURACY*100:+.2f}%)")
            
            if accuracy >= BASELINE_ACCURACY * 0.95:  # Ít nhất 95% baseline
                logger.info("\n   ✅ Mô hình mới chấp nhận được")
                
                # 7. Lưu mô hình mới
                logger.info("\n7️⃣  Lưu mô hình mới...")
                with open(MODEL_PATH, 'wb') as f:
                    pickle.dump(model, f)
                logger.info(f"   ✓ Lưu: {MODEL_PATH}")
                
                # 8. Cập nhật baseline
                logger.info("\n8️⃣  Cập nhật baseline...")
                new_baseline = accuracy
                logger.info(f"   Baseline mới: {new_baseline:.4f}")
                
                logger.info("\n✅ RETRAIN HOÀN THÀNH THÀNH CÔNG")
                return True
            else:
                logger.warning("\n   ⚠️ Mô hình mới tệ hơn") 
                logger.warning("   → Khôi phục mô hình cũ")
                
                # Khôi phục mô hình cũ
                backup_files = sorted(os.listdir(MODEL_BACKUP_DIR), reverse=True)
                if backup_files:
                    latest_backup = os.path.join(MODEL_BACKUP_DIR, backup_files[0])
                    os.rename(latest_backup, MODEL_PATH)
                    logger.info(f"   ✓ Khôi phục: {latest_backup}")
                
                return False
        
        except Exception as e:
            logger.error(f"❌ Lỗi retrain: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def automated_retrain_check(self):
        """Kiểm tra tự động và retrain nếu cần"""
        logger.info("\n" + "="*70)
        logger.info("🤖 AUTOMATED RETRAIN CHECK")
        logger.info("="*70)
        
        should_retrain = self.should_retrain()
        
        if should_retrain:
            logger.warning("\n🔴 Có dấu hiệu suy giảm - bắt đầu retrain")
            success = self.retrain_model()
            
            if success:
                logger.info("\n✅ Hệ thống đã tự động cập nhật")
            else:
                logger.error("\n❌ Retrain thất bại - kiểm tra dữ liệu mới")
        else:
            logger.info("\n✅ Hệ thống ổn định - không cần retrain")
    
    def schedule_retrain(self, interval_days=30):
        """Hướng dẫn scheduling retrain định kỳ"""
        logger.info("\n" + "="*70)
        logger.info("📅 HƯ­ỚNG DẪN SCHEDULE RETRAIN")
        logger.info("="*70)
        
        logger.info(f"\nĐề xuất: Retrain mỗi {interval_days} ngày hoặc khi dữ liệu mới có.")
        
        logger.info("\n**Cách 1: Cron Job (Linux/Mac)**")
        logger.info(f"""
        0 0 */{interval_days} * * cd /path/to/kbs && python retrain_pipeline.py
        """)
        
        logger.info("\n**Cách 2: Windows Task Scheduler**")
        logger.info(f"""
        schtasks /create /tn "KBS_Retrain" /tr "python C:\\path\\to\\retrain_pipeline.py" /sc daily /mo {interval_days}
        """)
        
        logger.info("\n**Cách 3: Python APScheduler**")
        logger.info("""
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=retrain_pipeline, trigger="interval", days=30)
        scheduler.start()
        """)


# ============================================================================
# QUY TRÌNH CẬP NHẬT KBS RULES
# ============================================================================
"""
QUY TRÌNH CẬP NHẬT LUẬT CHUYÊN GIA (KBS Rules):

Khi nào cần cập nhật?
  1. Khi phát hiện KBS predict sai nhiều (thông qua monitoring)
  2. Khi có tri thức chuyên gia mới (ví dụ: ngành mới, tiêu chí mới)
  3. Khi ML-KBS disagreement rate > 40% (từ experiments.py)
  4. Khi nhận feedback từ người dùng

Cách cập nhật:
  Bước 1: Chạy evaluate_kbs.py để kiểm tra KBS hiện tại
      python evaluate_kbs.py
  
  Bước 2: Chạy experiments.py để phân tích ML vs KBS
      python experiments.py
  
  Bước 3: Sửa rules_config.json (thresholds, scores, chaining rules)
  
  Bước 4: Cập nhật knowledge_rules.py cho phù hợp
  
  Bước 5: Chạy lại evaluate_kbs.py để verify

Ai quyết định?
  - Chuyên gia giáo dục / tư vấn hướng nghiệp
  - Dựa trên kết quả monitoring và feedback người dùng
"""


def main():
    """Main retrain pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Retrain Pipeline')
    parser.add_argument('--check', action='store_true', help='Kiểm tra nhu cầu retrain')
    parser.add_argument('--retrain', action='store_true', help='Bắt buộc retrain')
    parser.add_argument('--new-data', type=str, help='Đường dẫn dữ liệu mới')
    parser.add_argument('--schedule', action='store_true', help='Hiển thị hướng dẫn scheduling')
    
    args = parser.parse_args()
    
    pipeline = RetrainPipeline()
    
    if args.schedule:
        pipeline.schedule_retrain()
    elif args.retrain:
        pipeline.retrain_model(use_new_data=bool(args.new_data), new_data_path=args.new_data)
    else:
        pipeline.automated_retrain_check()


if __name__ == "__main__":
    main()

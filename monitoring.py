"""
Monitoring & Performance Tracking - Bước 7 (Phần 1)
Theo dõi hiệu suất hệ thống theo thời gian và phát hiện độ suy giảm
"""

import json
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from config import NGANH_HOC_MAP

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MONITORING_FILE = 'model_monitoring.jsonl'
METRICS_HISTORY_FILE = 'metrics_history.csv'


class ModelMonitor:
    """Theo dõi hiệu suất mô hình theo thời gian"""
    
    def __init__(self, monitor_file=MONITORING_FILE):
        self.monitor_file = monitor_file
        self.history = []
        self._load_history()
    
    def _load_history(self):
        """Load lịch sử monitoring"""
        if Path(self.monitor_file).exists():
            with open(self.monitor_file, 'r', encoding='utf-8') as f:
                for line in f:
                    self.history.append(json.loads(line))
            logger.info(f"✓ Load {len(self.history)} bản ghi lịch sử")
    
    def record_evaluation(self, ml_metrics, hybrid_metrics, evaluation_date=None):
        """Ghi lại kết quả đánh giá"""
        if evaluation_date is None:
            evaluation_date = datetime.now().isoformat()
        
        record = {
            'timestamp': evaluation_date,
            'ml_accuracy': ml_metrics['accuracy'],
            'ml_precision': ml_metrics['precision'],
            'ml_recall': ml_metrics['recall'],
            'ml_f1': ml_metrics['f1'],
            'hybrid_accuracy': hybrid_metrics['accuracy'],
            'hybrid_precision': hybrid_metrics['precision'],
            'hybrid_recall': hybrid_metrics['recall'],
            'hybrid_f1': hybrid_metrics['f1'],
            'improvement_pct': (hybrid_metrics['accuracy'] - ml_metrics['accuracy']) * 100
        }
        
        self.history.append(record)
        self._save_record(record)
        
        logger.info(f"✓ Ghi lại đánh giá tại {evaluation_date}")
    
    def _save_record(self, record):
        """Lưu record vào file"""
        with open(self.monitor_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    def get_performance_trend(self):
        """Lấy xu hướng hiệu suất"""
        if len(self.history) < 2:
            logger.warning("⚠️ Chưa đủ dữ liệu lịch sử để phân tích xu hướng (cần >= 2 bản ghi)")
            return None
        
        logger.info("\n" + "="*70)
        logger.info("📊 XU HƯỚNG HIỆU SUẤT")
        logger.info("="*70)
        
        ml_acc = [h['ml_accuracy'] for h in self.history]
        hybrid_acc = [h['hybrid_accuracy'] for h in self.history]
        timestamps = [h['timestamp'] for h in self.history]
        
        logger.info(f"\n📈 ML Accuracy:")
        logger.info(f"   Đầu: {ml_acc[0]:.4f}")
        logger.info(f"   Hiện tại: {ml_acc[-1]:.4f}")
        logger.info(f"   Thay đổi: {ml_acc[-1] - ml_acc[0]:+.4f}")
        
        # Tính xu hướng (linear regression slope)
        x = np.arange(len(ml_acc))
        ml_slope = np.polyfit(x, ml_acc, 1)[0]
        logger.info(f"   Xu hướng: {ml_slope:+.6f}/evaluation")
        
        logger.info(f"\n📈 Hybrid Accuracy:")
        logger.info(f"   Đầu: {hybrid_acc[0]:.4f}")
        logger.info(f"   Hiện tại: {hybrid_acc[-1]:.4f}")
        logger.info(f"   Thay đổi: {hybrid_acc[-1] - hybrid_acc[0]:+.4f}")
        
        hybrid_slope = np.polyfit(x, hybrid_acc, 1)[0]
        logger.info(f"   Xu hướng: {hybrid_slope:+.6f}/evaluation")
        
        # Phát hiện suy giảm
        logger.info(f"\n⚠️  PHÁT HIỆN SỰ CỐ:")
        ml_degradation = (ml_acc[-1] - ml_acc[0]) * 100
        hybrid_degradation = (hybrid_acc[-1] - hybrid_acc[0]) * 100
        
        if ml_degradation < -2:
            logger.warning(f"   🔴 ML accuracy suy giảm {abs(ml_degradation):.2f}% - CẦN RETRAIN!")
        elif ml_degradation < 0:
            logger.warning(f"   🟡 ML accuracy giảm {abs(ml_degradation):.2f}%")
        else:
            logger.info(f"   ✅ ML accuracy tăng {ml_degradation:+.2f}%")
        
        if hybrid_degradation < -2:
            logger.warning(f"   🔴 Hybrid accuracy suy giảm {abs(hybrid_degradation):.2f}% - ĐIỀU CHỈNH RULES!")
        elif hybrid_degradation < 0:
            logger.warning(f"   🟡 Hybrid accuracy giảm {abs(hybrid_degradation):.2f}%")
        else:
            logger.info(f"   ✅ Hybrid accuracy tăng {hybrid_degradation:+.2f}%")
        
        return {
            'timestamps': timestamps,
            'ml_accuracies': ml_acc,
            'hybrid_accuracies': hybrid_acc,
            'ml_trend': ml_slope,
            'hybrid_trend': hybrid_slope
        }
    
    def export_to_csv(self):
        """Xuất lịch sử ra CSV"""
        if len(self.history) == 0:
            logger.warning("⚠️ Không có dữ liệu để xuất")
            return
        
        df = pd.DataFrame(self.history)
        df.to_csv(METRICS_HISTORY_FILE, index=False)
        logger.info(f"✓ Xuất lịch sử ra '{METRICS_HISTORY_FILE}'")


class PredictionLogger:
    """Ghi lại các dự đoán cá nhân để phân tích"""
    
    def __init__(self, log_file='user_predictions_log.jsonl'):
        self.log_file = log_file
    
    def log_prediction(self, user_id, scores, ml_prediction, hybrid_prediction, 
                      actual_major=None, feedback=None):
        """Ghi lại một dự đoán"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'scores': scores,
            'ml_prediction': NGANH_HOC_MAP.get(ml_prediction, "Unknown"),
            'hybrid_prediction': NGANH_HOC_MAP.get(hybrid_prediction, "Unknown"),
            'actual_major': NGANH_HOC_MAP.get(actual_major) if actual_major is not None else None,
            'feedback': feedback
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    def analyze_feedback(self):
        """Phân tích feedback từ users"""
        if not Path(self.log_file).exists():
            logger.warning("⚠️ Chưa có dữ liệu dự đoán")
            return
        
        records = []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                records.append(json.loads(line))
        
        if len(records) == 0:
            logger.warning("⚠️ Chưa có dữ liệu dự đoán")
            return
        
        logger.info("\n" + "="*70)
        logger.info("📝 PHÂN TÍCH USER FEEDBACK")
        logger.info("="*70)
        
        logger.info(f"\n📊 Tổng số dự đoán: {len(records)}")
        
        # Phân tích prediction match
        matches = 0
        for record in records:
            if record['ml_prediction'] == record['actual_major']:
                matches += 1
        
        if record['actual_major'] is not None:
            logger.info(f"Dự đoán chính xác: {matches}/{len(records)} ({matches/len(records)*100:.2f}%)")
        
        # Phân tích major distribution
        logger.info(f"\n📈 Phân phối ngành dự đoán:")
        predictions = [r['hybrid_prediction'] for r in records]
        for major, count in sorted([(x, predictions.count(x)) for x in set(predictions)], 
                                   key=lambda x: x[1], reverse=True):
            logger.info(f"   {major:25} {count:3d} ({count/len(records)*100:5.2f}%)")


def main():
    """Demo monitoring"""
    logger.info("🔄 Demo: Monitoring & Tracking")
    logger.info("="*70)
    
    monitor = ModelMonitor()
    
    # Demo record
    ml_metrics = {
        'accuracy': 0.886,
        'precision': 0.88,
        'recall': 0.88,
        'f1': 0.88
    }
    
    hybrid_metrics = {
        'accuracy': 0.892,
        'precision': 0.89,
        'recall': 0.89,
        'f1': 0.89
    }
    
    logger.info("\n✅ Monitoring system sẵn sàng!")
    logger.info("   - Sử dụng monitor.record_evaluation() để ghi lại kết quả đánh giá")
    logger.info("   - Sử dụng monitor.get_performance_trend() để phân tích xu hướng")
    logger.info("   - Sử dụng prediction_logger.log_prediction() để ghi lại dự đoán")


if __name__ == "__main__":
    main()

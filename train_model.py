import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle
import logging
import os
from config import FEATURE_NAMES, NGANH_HOC_MAP, MODEL_PATH, RF_PARAMS, TEST_SIZE, DATA_PATH, CV_FOLDS

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def train():
    """Huấn luyện mô hình Random Forest với evaluation và cross-validation"""
    try:
        # 1. Đọc dữ liệu từ file CSV
        logger.info("📖 Đang đọc dữ liệu từ 'data_tuyensinh.csv'...")
        df = pd.read_csv(DATA_PATH)
        logger.info(f"   Kích thước dữ liệu: {df.shape}")
        
        # Kiểm tra xem dữ liệu có hợp lệ không
        if df.empty:
            logger.error("Lỗi: File CSV trống!")
            return False
        
        # 2. Tách đặc trưng (X) và nhãn (y)
        X = df[FEATURE_NAMES]
        y = df['nganh_hoc']
        
        logger.info(f"   Các đặc trưng: {FEATURE_NAMES}")
        logger.info(f"   Số lượng mẫu: {len(X)}")
        logger.info(f"   Số lượng class: {len(y.unique())}")
        
        # 3. Chia dữ liệu training/testing
        logger.info(f"Chia dữ liệu: {int((1-TEST_SIZE)*100)}% training, {int(TEST_SIZE*100)}% testing...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=42, stratify=y
        )
        logger.info(f"   Training set: {len(X_train)} mẫu")
        logger.info(f"   Testing set: {len(X_test)} mẫu")
        
        # 4. Khởi tạo và huấn luyện Random Forest
        logger.info("Khởi tạo & huấn luyện Random Forest...")
        logger.info(f"   Hyperparameters: {RF_PARAMS}")
        model = RandomForestClassifier(**RF_PARAMS)
        model.fit(X_train, y_train)
        logger.info("   ✓ Huấn luyện xong!")
        
        # 5. Đánh giá mô hình trên test set
        logger.info("Đánh giá mô hình trên test set:")
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"   Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        
        logger.info("Chi tiết phân loại:")
        class_report = classification_report(y_test, y_pred, 
                                            target_names=list(NGANH_HOC_MAP.values()),
                                            digits=4)
        logger.info(f"\n{class_report}")
        
        # 6. Cross-validation
        logger.info(f"Cross-validation ({CV_FOLDS}-fold)...")
        cv_scores = cross_val_score(model, X_train, y_train, cv=CV_FOLDS, scoring='accuracy', n_jobs=-1)
        logger.info(f"   CV Scores: {[f'{s:.4f}' for s in cv_scores]}")
        logger.info(f"   Mean CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # 7. Feature Importance Analysis
        logger.info("Tầm quan trọng của các đặc trưng:")
        feature_importance = dict(zip(FEATURE_NAMES, model.feature_importances_))
        for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"   {feature:12s}: {importance:.4f} {'█' * int(importance * 50)}")
        
        # 8. Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        logger.info(f"Confusion Matrix:\n{cm}")
        
        # 9. Lưu mô hình
        logger.info(f"Lưu mô hình vào '{MODEL_PATH}'...")
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        file_size = os.path.getsize(MODEL_PATH) / 1024
        logger.info(f"   ✓ Lưu thành công! Kích thước: {file_size:.2f} KB")
        
        logger.info("\n" + "="*50)
        logger.info("HOÀN THÀNH: Mô hình đã sẵn sàng!")
        logger.info("="*50)
        return True
        
    except FileNotFoundError:
        logger.error(f"Lỗi: Không tìm thấy file '{DATA_PATH}'!")
        logger.error("   Vui lòng chạy create_data.py trước!")
        return False
    except Exception as e:
        logger.error(f"Có lỗi xảy ra: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    train()
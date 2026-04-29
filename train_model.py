"""
Huấn luyện mô hình Random Forest cho dự đoán ngành học
Phiên bản 3.0: Train 2 model riêng cho KHTN và KHXH
"""

import pickle
import logging
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from config import (
    NGANH_HOC_MAP, RF_PARAMS, TEST_SIZE, CV_FOLDS, RANDOM_STATE,
    get_data_path, get_model_path, get_features, get_majors, get_major_names
)

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def train_model(block):
    """Huấn luyện Random Forest Classifier cho 1 khối"""
    try:
        data_path = get_data_path(block)
        model_path = get_model_path(block)
        feature_names = get_features(block)
        major_indices = get_majors(block)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"HUẤN LUYỆN MODEL {block.upper()}")
        logger.info(f"{'='*60}")
        
        # 1. Đọc dữ liệu
        logger.info(f"Đọc dữ liệu: {data_path}")
        df = pd.read_csv(data_path)
        logger.info(f"   Số lượng mẫu: {len(df)}")
        
        # 2. Tách đặc trưng (X) và nhãn (y)
        X = df[feature_names]
        y = df['nganh_hoc']
        
        logger.info(f"   Các đặc trưng: {feature_names}")
        logger.info(f"   Số lượng mẫu: {len(X)}")
        logger.info(f"   Các ngành: {sorted(y.unique())} ({len(y.unique())} ngành)")
        
        # 3. Chia dữ liệu training/testing
        logger.info(f"Chia dữ liệu: {int((1-TEST_SIZE)*100)}% training, {int(TEST_SIZE*100)}% testing...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )
        
        logger.info(f"   Training set: {len(X_train)}")
        logger.info(f"   Testing set: {len(X_test)}")
        
        # 4. Huấn luyện mô hình
        logger.info(f"Huấn luyện Random Forest...")
        logger.info(f"   Params: {RF_PARAMS}")
        model = RandomForestClassifier(**RF_PARAMS)
        model.fit(X_train, y_train)
        
        # 5. Đánh giá
        logger.info(f"Đánh giá mô hình...")
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"\n   Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        
        # Classification Report
        target_names = [NGANH_HOC_MAP[i] for i in sorted(y.unique())]
        report = classification_report(y_test, y_pred, target_names=target_names)
        logger.info(f"\n   Classification Report:\n{report}")
        
        # Cross-validation
        logger.info(f"Cross-validation ({CV_FOLDS}-fold)...")
        cv_scores = cross_val_score(model, X_train, y_train, cv=CV_FOLDS, scoring='accuracy', n_jobs=-1)
        logger.info(f"   CV Scores: {cv_scores}")
        logger.info(f"   CV Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # 6. Phân tích Feature Importance
        logger.info(f"\nFeature Importance:")
        importances = model.feature_importances_
        for name, imp in sorted(zip(feature_names, importances), key=lambda x: -x[1]):
            bar = '#' * int(imp * 100)
            logger.info(f"   {name:10s}: {imp:.4f} {bar}")
        
        # 7. Lưu mô hình
        logger.info(f"\nLưu mô hình vào {model_path}...")
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(f"   Mô hình đã được lưu thành công!")
        logger.info(f"\n   TỔNG KẾT {block.upper()}:")
        logger.info(f"   Accuracy: {accuracy:.4f}")
        logger.info(f"   CV Mean: {cv_scores.mean():.4f}")
        logger.info(f"   Model saved: {model_path}")
        
        return model, accuracy
        
    except Exception as e:
        logger.error(f"Lỗi: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None, 0


def main():
    """Train cả 2 model"""
    logger.info("="*60)
    logger.info("BẮT ĐẦU HUẤN LUYỆN 2 MODEL")
    logger.info("="*60)
    
    model_khtn, acc_khtn = train_model('khtn')
    model_khxh, acc_khxh = train_model('khxh')
    
    logger.info(f"\n{'='*60}")
    logger.info(f"TỔNG KẾT CHUNG")
    logger.info(f"{'='*60}")
    logger.info(f"   KHTN Accuracy: {acc_khtn:.4f}")
    logger.info(f"   KHXH Accuracy: {acc_khxh:.4f}")


if __name__ == "__main__":
    main()
"""
Đánh giá Hệ Thống Lai - So sánh ML vs Hybrid (Bước 6)
Bước 6: Đánh giá hệ thống tổng thể - so sánh độ chính xác của ML vs Hybrid
"""

import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import logging
from config import DATA_PATH, NGANH_HOC_MAP, MODEL_PATH, FEATURE_NAMES
from hybrid_engine import get_hybrid_advice

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get MAJOR_NAMES from NGANH_HOC_MAP
MAJOR_NAMES = [NGANH_HOC_MAP[i] for i in range(len(NGANH_HOC_MAP))]


def evaluate_ml_only(model, X_test, y_test):
    """Đánh giá mô hình ML thuần"""
    logger.info("\n" + "="*70)
    logger.info("1️⃣  ĐÁNH GIÁ ML (RANDOM FOREST THUẦN)")
    logger.info("="*70)
    
    y_pred = model.predict(X_test)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision_macro = precision_score(y_test, y_pred, average='macro')
    recall_macro = recall_score(y_test, y_pred, average='macro')
    f1_macro = f1_score(y_test, y_pred, average='macro')
    
    logger.info("\n📊 Kết quả tổng hợp:")
    logger.info(f"   Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    logger.info(f"   Precision: {precision_macro:.4f} ({precision_macro*100:.2f}%)")
    logger.info(f"   Recall:    {recall_macro:.4f} ({recall_macro*100:.2f}%)")
    logger.info(f"   F1 Score:  {f1_macro:.4f}")
    
    logger.info("\n📈 Chi tiết theo ngành:")
    report = classification_report(y_test, y_pred, target_names=MAJOR_NAMES, digits=4, output_dict=True)
    print_classification_report(report, MAJOR_NAMES)
    
    return {
        'accuracy': accuracy,
        'precision': precision_macro,
        'recall': recall_macro,
        'f1': f1_macro,
        'y_pred': y_pred,
        'report': report
    }


def evaluate_hybrid_system(model, X_test, y_test):
    """Đánh giá hệ thống Hybrid (ML + KBS)"""
    logger.info("\n" + "="*70)
    logger.info("2️⃣  ĐÁNH GIÁ HYBRID SYSTEM (ML + KBS)")
    logger.info("="*70)
    
    y_pred_hybrid = []
    hybrid_scores = []
    
    logger.info(f"\n⏳ Đang dự đoán {len(X_test)} mẫu...")
    for idx, (i, row) in enumerate(X_test.iterrows()):
        if (idx + 1) % 1000 == 0:
            logger.info(f"   Tiến độ: {idx+1}/{len(X_test)}")
        
        scores = row.values.tolist()
        
        # Lấy xếp hạng từ hybrid
        rankings = []
        max_score = 0
        best_major = 0
        
        for major_idx in range(len(NGANH_HOC_MAP)):
            score, _, _, _ = get_hybrid_advice(scores, major_idx)
            if score is not None:
                rankings.append((major_idx, score))
                if score > max_score:
                    max_score = score
                    best_major = major_idx
        
        y_pred_hybrid.append(best_major)
        hybrid_scores.append(max_score)
    
    y_pred_hybrid = np.array(y_pred_hybrid)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred_hybrid)
    precision_macro = precision_score(y_test, y_pred_hybrid, average='macro')
    recall_macro = recall_score(y_test, y_pred_hybrid, average='macro')
    f1_macro = f1_score(y_test, y_pred_hybrid, average='macro')
    
    logger.info("\n📊 Kết quả tổng hợp:")
    logger.info(f"   Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    logger.info(f"   Precision: {precision_macro:.4f} ({precision_macro*100:.2f}%)")
    logger.info(f"   Recall:    {recall_macro:.4f} ({recall_macro*100:.2f}%)")
    logger.info(f"   F1 Score:  {f1_macro:.4f}")
    logger.info(f"   Avg Hybrid Score: {np.mean(hybrid_scores):.2f}%")
    
    logger.info("\n📈 Chi tiết theo ngành:")
    report = classification_report(y_test, y_pred_hybrid, target_names=MAJOR_NAMES, digits=4, output_dict=True)
    print_classification_report(report, MAJOR_NAMES)
    
    return {
        'accuracy': accuracy,
        'precision': precision_macro,
        'recall': recall_macro,
        'f1': f1_macro,
        'y_pred': y_pred_hybrid,
        'hybrid_scores': hybrid_scores,
        'report': report
    }


def print_classification_report(report, major_names):
    """In classification report theo ngành"""
    logger.info(f"{'Ngành':25} {'Precision':12} {'Recall':12} {'F1-Score':12} {'Support':10}")
    logger.info("-" * 70)
    for idx, major in enumerate(major_names):
        if str(idx) in report:
            metrics = report[str(idx)]
            logger.info(f"{major[:25]:25} {metrics['precision']:12.4f} {metrics['recall']:12.4f} {metrics['f1-score']:12.4f} {int(metrics['support']):10}")


def compare_ml_vs_hybrid(ml_results, hybrid_results):
    """So sánh ML vs Hybrid"""
    logger.info("\n" + "="*70)
    logger.info("3️⃣  SO SÁNH ML vs HYBRID SYSTEM")
    logger.info("="*70)
    
    logger.info(f"\n{'Metric':20} {'ML':15} {'Hybrid':15} {'Thay Đổi':15}")
    logger.info("-" * 70)
    
    metrics = ['accuracy', 'precision', 'recall', 'f1']
    improvements = {}
    
    for metric in metrics:
        ml_val = ml_results[metric]
        hybrid_val = hybrid_results[metric]
        change = hybrid_val - ml_val
        improvement_pct = (change / ml_val * 100) if ml_val != 0 else 0
        
        improvements[metric] = {'change': change, 'pct': improvement_pct}
        
        symbol = "📈" if change > 0 else "📉" if change < 0 else "="
        logger.info(f"{metric.upper():20} {ml_val:14.4f} {hybrid_val:14.4f} {symbol} {improvement_pct:+.2f}%")
    
    logger.info("-" * 70)
    
    avg_improvement = np.mean([v['pct'] for v in improvements.values()])
    logger.info(f"\n🎯 Cải thiện trung bình: {avg_improvement:+.2f}%")
    
    if avg_improvement > 0:
        logger.info("✅ Hybrid System cải thiện hiệu suất so với ML thuần!")
    elif avg_improvement < 0:
        logger.info("⚠️ ML thuần vẫn tốt hơn - cần điều chỉnh Fuzzy rules")
    else:
        logger.info("🔄 Hiệu suất tương đương")
    
    return improvements


def analyze_prediction_confidence(ml_preds, hybrid_scores, y_test):
    """Phân tích độ tin cậy của Hybrid System"""
    logger.info("\n" + "="*70)
    logger.info("4️⃣  PHÂN TÍCH ĐỘ TIN CẬY HYBRID SYSTEM")
    logger.info("="*70)
    
    correct_mask = ml_preds == y_test
    high_confidence = np.array(hybrid_scores) >= 70
    
    logger.info("\n📊 Thống kê:")
    logger.info(f"   Dự đoán đúng (ML): {correct_mask.sum()}/{len(y_test)} ({correct_mask.sum()/len(y_test)*100:.2f}%)")
    logger.info(f"   Hybrid score >= 70%: {high_confidence.sum()}/{len(hybrid_scores)} ({high_confidence.sum()/len(hybrid_scores)*100:.2f}%)")
    
    # Tỉ lệ dự đoán đúng khi Hybrid confidence cao
    correct_high_conf = (correct_mask & high_confidence).sum()
    if high_confidence.sum() > 0:
        accuracy_high_conf = correct_high_conf / high_confidence.sum()
        logger.info(f"   Độ chính xác khi Hybrid >= 70%: {accuracy_high_conf:.4f} ({accuracy_high_conf*100:.2f}%)")
    
    logger.info("\n📈 Phân phối Hybrid Scores:")
    for threshold in [50, 60, 70, 80, 90]:
        count = (np.array(hybrid_scores) >= threshold).sum()
        logger.info(f"   Score >= {threshold}%: {count:5d} ({count/len(hybrid_scores)*100:5.2f}%)")


def main():
    """Main evaluation function"""
    try:
        # 1. Load data
        logger.info("📖 Đang load dữ liệu...")
        df = pd.read_csv(DATA_PATH)
        logger.info(f"✓ Load thành công: {len(df)} samples")
        
        # Prepare features and target
        X = df[FEATURE_NAMES]
        y = df['nganh_hoc']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # 2. Load model
        logger.info("\n🔄 Đang load mô hình...")
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        logger.info("✓ Mô hình đã load")
        
        # 3. Evaluate ML
        ml_results = evaluate_ml_only(model, X_test, y_test)
        
        # 4. Evaluate Hybrid
        logger.info("\n⏳ Đánh giá Hybrid System - có thể mất 1-2 phút...")
        hybrid_results = evaluate_hybrid_system(model, X_test, y_test)
        
        # 5. Compare
        compare_ml_vs_hybrid(ml_results, hybrid_results)
        
        # 6. Analyze confidence
        analyze_prediction_confidence(ml_results['y_pred'], hybrid_results['hybrid_scores'], y_test.values)
        
        # 7. Summary
        logger.info("\n" + "="*70)
        logger.info("✅ ĐÁNH GIÁ HOÀN TẤT")
        logger.info("="*70)
        logger.info("\n📋 Khuyến nghị:")
        
        ml_acc = ml_results['accuracy']
        hybrid_acc = hybrid_results['accuracy']
        
        if hybrid_acc > ml_acc:
            logger.info(f"✅ Sử dụng Hybrid System - cải thiện {(hybrid_acc-ml_acc)*100:.2f}%")
        else:
            logger.info("⚠️ ML thuần vẫn tốt hơn - xem xét điều chỉnh KBS rules")
        
        logger.info("\nChi tiết lưu trong log")
        
    except Exception as e:
        logger.error(f"❌ Lỗi: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()

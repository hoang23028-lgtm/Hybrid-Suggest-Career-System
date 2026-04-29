"""
Đánh giá Hệ Thống Lai - So sánh ML vs Hybrid (Bước 6)
Bước 6: Đánh giá hệ thống tổng thể - so sánh độ chính xác của ML vs Hybrid
"""

import pickle
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import logging
from config import (
    TEST_SIZE,
    RANDOM_STATE,
    get_data_path,
    get_features,
    get_majors,
    NGANH_HOC_MAP,
    MAJOR_NAMES,
)
from hybrid_fusion import calculate_hybrid_score, load_ml_model

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# (Không load model ở cấp module để tránh lỗi khi API thay đổi.)


def evaluate_ml_only(block, model, X_test, y_test):
    """Đánh giá mô hình ML thuần cho 1 khối."""
    logger.info("\n" + "="*70)
    logger.info(f"1️⃣  ĐÁNH GIÁ ML (RANDOM FOREST THUẦN) - {block.upper()}")
    logger.info("="*70)

    y_pred = model.predict(X_test)

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision_macro = precision_score(y_test, y_pred, average='macro', zero_division=0)
    recall_macro = recall_score(y_test, y_pred, average='macro', zero_division=0)
    f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)

    logger.info("\n Kết quả tổng hợp:")
    logger.info(f"   Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    logger.info(f"   Precision: {precision_macro:.4f} ({precision_macro*100:.2f}%)")
    logger.info(f"   Recall:    {recall_macro:.4f} ({recall_macro*100:.2f}%)")
    logger.info(f"   F1 Score:  {f1_macro:.4f}")

    labels = sorted([int(v) for v in pd.unique(y_test)])
    target_names = [NGANH_HOC_MAP[int(i)] for i in labels]

    logger.info("\n📈 Chi tiết theo ngành:")
    report = classification_report(
        y_test, y_pred,
        labels=labels,
        target_names=target_names,
        digits=4,
        output_dict=True,
        zero_division=0,
    )
    print_classification_report(report, target_names, labels=labels)

    return {
        'accuracy': accuracy,
        'precision': precision_macro,
        'recall': recall_macro,
        'f1': f1_macro,
        'y_pred': y_pred,
        'report': report,
        'labels': labels,
    }


def evaluate_hybrid_system(block, model, X_test, y_test, max_samples=None):
    """Đánh giá hệ thống Hybrid (ML + KBS) cho 1 khối."""
    logger.info("\n" + "=" * 70)
    logger.info(f"2️⃣  ĐÁNH GIÁ HYBRID SYSTEM (ML + KBS) - {block.upper()}")
    logger.info("=" * 70)

    features = get_features(block)
    majors = get_majors(block)

    y_pred_hybrid = []
    hybrid_scores = []

    n_total = len(X_test)
    if max_samples is not None and max_samples > 0:
        n_total = min(n_total, max_samples)
        X_iter = X_test.iloc[:n_total]
        y_iter = y_test.iloc[:n_total]
    else:
        X_iter = X_test
        y_iter = y_test

    logger.info(f"\n⏳ Đang dự đoán {len(X_iter)} mẫu...")
    for idx, (_, row) in enumerate(X_iter.iterrows()):
        if (idx + 1) % 1000 == 0:
            logger.info(f"   Tiến độ: {idx+1}/{len(X_iter)}")

        user_scores = row[features].values.tolist()

        best_major = None
        best_score = -1.0
        for major_label in majors:
            result = calculate_hybrid_score(user_scores, major_label, block=block, model=model)
            score = result.get('hybrid_score', 0)
            if score > best_score:
                best_score = score
                best_major = major_label

        y_pred_hybrid.append(best_major)
        hybrid_scores.append(best_score)

    y_pred_hybrid = np.array(y_pred_hybrid)

    # Metrics
    accuracy = accuracy_score(y_iter, y_pred_hybrid)
    precision_macro = precision_score(y_iter, y_pred_hybrid, average='macro', zero_division=0)
    recall_macro = recall_score(y_iter, y_pred_hybrid, average='macro', zero_division=0)
    f1_macro = f1_score(y_iter, y_pred_hybrid, average='macro', zero_division=0)

    logger.info("\n📊 Kết quả tổng hợp:")
    logger.info(f"   Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    logger.info(f"   Precision: {precision_macro:.4f} ({precision_macro*100:.2f}%)")
    logger.info(f"   Recall:    {recall_macro:.4f} ({recall_macro*100:.2f}%)")
    logger.info(f"   F1 Score:  {f1_macro:.4f}")
    logger.info(f"   Avg Hybrid Score: {np.mean(hybrid_scores):.2f}%")

    labels = sorted([int(v) for v in pd.unique(y_iter)])
    target_names = [NGANH_HOC_MAP[int(i)] for i in labels]
    logger.info("\n Chi tiết theo ngành:")
    report = classification_report(
        y_iter, y_pred_hybrid,
        labels=labels,
        target_names=target_names,
        digits=4,
        output_dict=True,
        zero_division=0,
    )
    print_classification_report(report, target_names, labels=labels)

    return {
        'accuracy': accuracy,
        'precision': precision_macro,
        'recall': recall_macro,
        'f1': f1_macro,
        'y_pred': y_pred_hybrid,
        'hybrid_scores': hybrid_scores,
        'report': report,
        'labels': labels,
    }


def print_classification_report(report, major_names, labels=None):
    """In classification report theo ngành"""
    logger.info(f"{'Ngành':25} {'Precision':12} {'Recall':12} {'F1-Score':12} {'Support':10}")
    logger.info("-" * 70)
    if labels is None:
        for idx, major in enumerate(major_names):
            if str(idx) in report:
                metrics = report[str(idx)]
                logger.info(
                    f"{major[:25]:25} {metrics['precision']:12.4f} {metrics['recall']:12.4f} {metrics['f1-score']:12.4f} {int(metrics['support']):10}"
                )
    else:
        for label, major in zip(labels, major_names):
            key = str(label)
            if key in report:
                metrics = report[key]
                logger.info(
                    f"{major[:25]:25} {metrics['precision']:12.4f} {metrics['recall']:12.4f} {metrics['f1-score']:12.4f} {int(metrics['support']):10}"
                )


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
        logger.info(" Hybrid System cải thiện hiệu suất so với ML thuần!")
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
    """Main evaluation function (đánh giá theo từng khối)."""
    try:
        max_samples_env = os.getenv("EVAL_MAX_SAMPLES", "0").strip()
        max_samples = int(max_samples_env) if max_samples_env and int(max_samples_env) > 0 else None

        blocks = ["khtn", "khxh"]
        for block in blocks:
            logger.info("\n" + "=" * 80)
            logger.info(f"🚀 BẮT ĐẦU ĐÁNH GIÁ CHO KHỐI {block.upper()}")
            logger.info("=" * 80)

            logger.info("📖 Đang load dữ liệu...")
            df = pd.read_csv(get_data_path(block))
            logger.info(f"✓ Load thành công: {len(df):,} samples")

            features = get_features(block)
            X = df[features]
            y = df["nganh_hoc"]

            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=TEST_SIZE,
                random_state=RANDOM_STATE,
                stratify=y,
            )

            logger.info("\n🔄 Đang load mô hình...")
            model = load_ml_model(block)
            if model is None:
                logger.warning(f"⚠️  Không load được ML model cho {block}. Bỏ qua khối này.")
                continue
            logger.info("✓ Mô hình đã load")

            ml_results = evaluate_ml_only(block, model, X_test, y_test)

            logger.info("\n⏳ Đánh giá Hybrid System (có thể chậm)...")
            hybrid_results = evaluate_hybrid_system(
                block, model, X_test, y_test, max_samples=max_samples
            )

            compare_ml_vs_hybrid(ml_results, hybrid_results)
            analyze_prediction_confidence(
                ml_results["y_pred"],
                hybrid_results["hybrid_scores"],
                y_test.values,
            )

            ml_acc = ml_results["accuracy"]
            hybrid_acc = hybrid_results["accuracy"]
            logger.info("\n📋 Khuyến nghị:")
            if hybrid_acc > ml_acc:
                logger.info(
                    f"✅ Hybrid tốt hơn ML: cải thiện {(hybrid_acc - ml_acc) * 100:.2f}%"
                )
            else:
                logger.info("⚠️ ML thuần vẫn tốt hơn - xem xét tinh chỉnh KBS rules")

    except Exception as e:
        logger.error(f"❌ Lỗi: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()

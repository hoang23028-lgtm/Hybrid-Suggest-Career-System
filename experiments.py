"""
Thử nghiệm & Đánh giá toàn diện - Experiments
Bao gồm:
  1. Thử nghiệm tỷ lệ ML/KBS (tìm trọng số tối ưu)
  2. Hyperparameter tuning cho Random Forest
  3. So sánh ML rules vs Expert rules
"""

import pickle
import logging
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, f1_score
from config import DATA_PATH, FEATURE_NAMES, MODEL_PATH, RF_PARAMS, TEST_SIZE
from knowledge_rules import KnowledgeRuleEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# 1. THỬ NGHIỆM TỶ LỆ ML/KBS
# ============================================================================
def experiment_weight_ratios(X_test, y_test, model, sample_size=2000):
    """
    Thử nghiệm các tỷ lệ ML/KBS khác nhau để tìm trọng số tối ưu.
    
    Thử: 0/100, 10/90, 20/80, ..., 90/10, 100/0
    Đo accuracy trên tập test.
    """
    logger.info("\n" + "="*70)
    logger.info("1️⃣  THỬ NGHIỆM TỶ LỆ ML/KBS")
    logger.info("="*70)
    
    kbs_engine = KnowledgeRuleEngine()
    
    # Lấy mẫu nhỏ để tăng tốc
    if len(X_test) > sample_size:
        indices = np.random.choice(len(X_test), sample_size, replace=False)
        X_sample = X_test.iloc[indices]
        y_sample = y_test.iloc[indices]
    else:
        X_sample = X_test
        y_sample = y_test
    
    # Tính trước ML scores và KBS scores cho tất cả mẫu
    logger.info(f"Tính scores cho {len(X_sample)} mẫu...")
    all_ml_scores = []  # shape: (n_samples, 8)
    all_kbs_scores = []  # shape: (n_samples, 8)
    
    X_input = pd.DataFrame(X_sample.values, columns=FEATURE_NAMES)
    probs = model.predict_proba(X_input)
    
    for idx in range(len(X_sample)):
        row = X_sample.iloc[idx]
        scores = row.values.tolist()
        
        ml_row = []
        kbs_row = []
        for major_idx in range(8):
            # ML score
            raw_prob = probs[idx][major_idx]
            ml_score = (raw_prob ** 0.6) * 10 * 10  # Scale to 0-100
            ml_score = min(100, max(0, ml_score))
            ml_row.append(ml_score)
            
            # KBS score
            kbs_result = kbs_engine.evaluate(scores, major_idx)
            kbs_row.append(kbs_result['score'])
        
        all_ml_scores.append(ml_row)
        all_kbs_scores.append(kbs_row)
    
    all_ml_scores = np.array(all_ml_scores)
    all_kbs_scores = np.array(all_kbs_scores)
    
    # Thử các tỷ lệ
    ratios = [(ml_w / 10, 1 - ml_w / 10) for ml_w in range(0, 11)]
    results = []
    
    logger.info(f"\n{'ML%':>6} {'KBS%':>6} {'Accuracy':>10} {'F1':>10}")
    logger.info("-" * 40)
    
    for ml_weight, kbs_weight in ratios:
        hybrid_scores = ml_weight * all_ml_scores + kbs_weight * all_kbs_scores
        y_pred = np.argmax(hybrid_scores, axis=1)
        
        acc = accuracy_score(y_sample, y_pred)
        f1 = f1_score(y_sample, y_pred, average='macro')
        
        marker = " ◀ hiện tại" if abs(ml_weight - 0.6) < 0.01 else ""
        logger.info(f"{ml_weight*100:5.0f}% {kbs_weight*100:5.0f}% {acc:10.4f} {f1:10.4f}{marker}")
        
        results.append({
            'ml_weight': ml_weight,
            'kbs_weight': kbs_weight,
            'accuracy': acc,
            'f1': f1
        })
    
    # Tìm tỷ lệ tối ưu
    best = max(results, key=lambda x: x['accuracy'])
    logger.info(f"\n🏆 Tỷ lệ tối ưu: ML={best['ml_weight']*100:.0f}% / KBS={best['kbs_weight']*100:.0f}%")
    logger.info(f"   Accuracy: {best['accuracy']:.4f}, F1: {best['f1']:.4f}")
    
    current = next(r for r in results if abs(r['ml_weight'] - 0.6) < 0.01)
    diff = best['accuracy'] - current['accuracy']
    logger.info(f"   So với 60/40 hiện tại: {diff:+.4f} ({diff*100:+.2f}%)")
    
    return results


# ============================================================================
# 2. HYPERPARAMETER TUNING CHO RANDOM FOREST
# ============================================================================
def experiment_hyperparameter_tuning(X_train, y_train, sample_size=20000):
    """
    GridSearchCV cho Random Forest.
    """
    logger.info("\n" + "="*70)
    logger.info("2️⃣  HYPERPARAMETER TUNING (Random Forest)")
    logger.info("="*70)
    
    # Lấy mẫu nhỏ để tăng tốc GridSearch
    if len(X_train) > sample_size:
        indices = np.random.choice(len(X_train), sample_size, replace=False)
        X_sample = X_train.iloc[indices]
        y_sample = y_train.iloc[indices]
    else:
        X_sample = X_train
        y_sample = y_train
    
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [10, 15, 20, None],
        'min_samples_split': [2, 5, 10],
    }
    
    logger.info(f"Grid search trên {len(X_sample)} mẫu...")
    logger.info(f"Param grid: {param_grid}")
    
    grid_search = GridSearchCV(
        RandomForestClassifier(random_state=42, n_jobs=-1),
        param_grid,
        cv=3,
        scoring='accuracy',
        n_jobs=-1,
        verbose=0
    )
    
    grid_search.fit(X_sample, y_sample)
    
    logger.info(f"\n🏆 Best params: {grid_search.best_params_}")
    logger.info(f"   Best CV accuracy: {grid_search.best_score_:.4f}")
    
    # So sánh với params hiện tại
    logger.info(f"\n   Params hiện tại: {RF_PARAMS}")
    
    # Top 5 combinations
    logger.info(f"\n📊 Top 5 combinations:")
    results_df = pd.DataFrame(grid_search.cv_results_)
    top5 = results_df.nlargest(5, 'mean_test_score')[['params', 'mean_test_score', 'std_test_score']]
    for _, row in top5.iterrows():
        logger.info(f"   {row['params']} → {row['mean_test_score']:.4f} (+/- {row['std_test_score']:.4f})")
    
    return grid_search.best_params_, grid_search.best_score_


# ============================================================================
# 3. SO SÁNH ML RULES VS EXPERT RULES
# ============================================================================
def experiment_compare_ml_vs_expert_rules(X_test, y_test, model, sample_size=3000):
    """
    So sánh rules trích xuất từ ML với rules chuyên gia.
    Phân tích: khi nào ML đồng ý/bất đồng với KBS?
    """
    logger.info("\n" + "="*70)
    logger.info("3️⃣  SO SÁNH ML RULES vs EXPERT RULES")
    logger.info("="*70)
    
    kbs_engine = KnowledgeRuleEngine()
    
    if len(X_test) > sample_size:
        indices = np.random.choice(len(X_test), sample_size, replace=False)
        X_sample = X_test.iloc[indices]
        y_sample = y_test.iloc[indices]
    else:
        X_sample = X_test
        y_sample = y_test
    
    ml_preds = model.predict(X_sample)
    
    agree_count = 0
    disagree_count = 0
    ml_correct_kbs_wrong = 0
    kbs_correct_ml_wrong = 0
    both_correct = 0
    both_wrong = 0
    
    for idx in range(len(X_sample)):
        row = X_sample.iloc[idx]
        scores = row.values.tolist()
        true_label = y_sample.iloc[idx]
        ml_pred = ml_preds[idx]
        
        # KBS prediction: chọn ngành có score cao nhất
        kbs_results = kbs_engine.evaluate_all_majors(scores)
        kbs_pred = max(
            range(8),
            key=lambda i: kbs_results[kbs_engine.MAJOR_NAMES[i]]['score']
        )
        
        if ml_pred == kbs_pred:
            agree_count += 1
            if ml_pred == true_label:
                both_correct += 1
            else:
                both_wrong += 1
        else:
            disagree_count += 1
            if ml_pred == true_label:
                ml_correct_kbs_wrong += 1
            elif kbs_pred == true_label:
                kbs_correct_ml_wrong += 1
    
    total = len(X_sample)
    
    logger.info(f"\n📊 Kết quả trên {total} mẫu:")
    logger.info(f"   ML và KBS đồng ý:        {agree_count:5d} ({agree_count/total*100:5.1f}%)")
    logger.info(f"   ML và KBS bất đồng:       {disagree_count:5d} ({disagree_count/total*100:5.1f}%)")
    
    logger.info(f"\n   Khi đồng ý:")
    logger.info(f"     Cả hai đúng:            {both_correct:5d} ({both_correct/total*100:5.1f}%)")
    logger.info(f"     Cả hai sai:             {both_wrong:5d} ({both_wrong/total*100:5.1f}%)")
    
    logger.info(f"\n   Khi bất đồng:")
    logger.info(f"     ML đúng, KBS sai:       {ml_correct_kbs_wrong:5d} ({ml_correct_kbs_wrong/total*100:5.1f}%)")
    logger.info(f"     KBS đúng, ML sai:       {kbs_correct_ml_wrong:5d} ({kbs_correct_ml_wrong/total*100:5.1f}%)")
    
    # Tính accuracy riêng
    ml_acc = accuracy_score(y_sample, ml_preds)
    logger.info(f"\n   ML Accuracy:              {ml_acc:.4f}")
    
    # Nhận xét
    logger.info(f"\n💡 Nhận xét:")
    if ml_correct_kbs_wrong > kbs_correct_ml_wrong:
        logger.info(f"   ML tốt hơn KBS khi bất đồng → Nên dùng ML weight > KBS weight")
    else:
        logger.info(f"   KBS tốt hơn ML khi bất đồng → Nên tăng KBS weight")
    
    agreement_rate = agree_count / total
    logger.info(f"   Tỷ lệ đồng thuận: {agreement_rate*100:.1f}% → ", end="")
    if agreement_rate > 0.8:
        logger.info("Hai hệ thống rất nhất quán")
    elif agreement_rate > 0.6:
        logger.info("Hai hệ thống khá nhất quán")
    else:
        logger.info("Hai hệ thống khác biệt nhiều → Hybrid có giá trị bổ sung cao")
    
    return {
        'agree_rate': agreement_rate,
        'ml_accuracy': ml_acc,
        'ml_correct_kbs_wrong': ml_correct_kbs_wrong,
        'kbs_correct_ml_wrong': kbs_correct_ml_wrong
    }


# ============================================================================
# MAIN
# ============================================================================
def main():
    """Chạy tất cả thử nghiệm"""
    logger.info("="*70)
    logger.info("🔬 BẮT ĐẦU THỬ NGHIỆM TOÀN DIỆN")
    logger.info("="*70)
    
    # Load data
    logger.info("\n📖 Load dữ liệu...")
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_NAMES]
    y = df['nganh_hoc']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=42, stratify=y
    )
    logger.info(f"   Train: {len(X_train)}, Test: {len(X_test)}")
    
    # Load model
    logger.info("🔄 Load mô hình...")
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    
    # Experiment 1: Weight ratios
    weight_results = experiment_weight_ratios(X_test, y_test, model)
    
    # Experiment 2: Hyperparameter tuning
    best_params, best_score = experiment_hyperparameter_tuning(X_train, y_train)
    
    # Experiment 3: ML vs Expert rules
    comparison = experiment_compare_ml_vs_expert_rules(X_test, y_test, model)
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("✅ TẤT CẢ THỬ NGHIỆM HOÀN TẤT")
    logger.info("="*70)
    
    logger.info("\n📋 TÓM TẮT:")
    best_weight = max(weight_results, key=lambda x: x['accuracy'])
    logger.info(f"   1. Tỷ lệ tối ưu: ML={best_weight['ml_weight']*100:.0f}%/KBS={best_weight['kbs_weight']*100:.0f}%")
    logger.info(f"   2. Best RF params: {best_params} ({best_score:.4f})")
    logger.info(f"   3. ML-KBS agreement: {comparison['agree_rate']*100:.1f}%")


if __name__ == "__main__":
    main()

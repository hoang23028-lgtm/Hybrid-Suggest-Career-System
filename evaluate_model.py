import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from config import DATA_PATH, NGANH_HOC_MAP

# Get MAJOR_NAMES from NGANH_HOC_MAP
MAJOR_NAMES = [NGANH_HOC_MAP[i] for i in range(len(NGANH_HOC_MAP))]

# Load data
print("🔄 Đang load dữ liệu...")
df = pd.read_csv(DATA_PATH)
print(f"✓ Load thành công: {len(df)} samples")

# Prepare features and target
X = df.drop('nganh_hoc', axis=1)
y = df['nganh_hoc']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Load model
print("\n🔄 Đang load mô hình từ 'rf_model.pkl'...")
import sys
try:
    with open('rf_model.pkl', 'rb') as f:
        model = pickle.load(f)
    print("✓ Mô hình đã được load thành công!")
except Exception as e:
    print(f"❌ Lỗi load mô hình: {e}")
    print("⚠️ Đang retrain mô hình...")
    from sklearn.ensemble import RandomForestClassifier
    from config import RF_PARAMS
    model = RandomForestClassifier(**RF_PARAMS)
    model.fit(X_train, y_train)
    print("✓ Mô hình retrain thành công!")

# Predictions
y_pred = model.predict(X_test)

# Metrics
accuracy = accuracy_score(y_test, y_pred)
precision_macro = precision_score(y_test, y_pred, average='macro')
recall_macro = recall_score(y_test, y_pred, average='macro')
f1_macro = f1_score(y_test, y_pred, average='macro')

print("\n" + "="*70)
print("ĐÁNH GIÁ MÔ HÌNH")
print("="*70)
print(f"\nAccuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"Precision: {precision_macro:.4f} ({precision_macro*100:.2f}%)")
print(f"Recall:    {recall_macro:.4f} ({recall_macro*100:.2f}%)")
print(f"F1 Score:  {f1_macro:.4f}")

print("\n" + "-"*70)
print("CHI TIẾT THEO NGÀNH")
print("-"*70)
print(classification_report(y_test, y_pred, target_names=MAJOR_NAMES, digits=4))

# Feature importance
print("\n" + "-"*70)
print("MỨC ĐỘ QUAN TRỌNG CỦA CÁC FEATURE")
print("-"*70)
importances = model.feature_importances_
indices = np.argsort(importances)[::-1][:10]
for i, idx in enumerate(indices):
    print(f"{i+1}. {X.columns[idx]:15} - {importances[idx]:.4f} ({importances[idx]*100:.2f}%)")

print("\n" + "="*70)
print("✓ ĐÁNH GIÁ HOÀN THÀNH")
print("="*70)

"""
train.py — Script huấn luyện mô hình Machine Learning
=======================================================
Cách sử dụng:
    python ML/scripts/train.py
"""

import os
import sys
import yaml
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, classification_report,
                             mean_squared_error, r2_score)

# Thêm root vào path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# ============================================================
# CẤU HÌNH
# ============================================================
CONFIG = {
    'data_path': 'data/processed/data_processed.csv',
    'target_column': 'target',       # ← Thay tên cột mục tiêu
    'test_size': 0.2,
    'random_state': 42,
    'model_save_path': 'ML/models/',
    'task': 'classification',         # 'classification' hoặc 'regression'
}


# ============================================================
# HÀM TIỆN ÍCH
# ============================================================
def load_data(path: str, target_col: str):
    """Tải dữ liệu và tách features / target."""
    print(f"📂 Tải dữ liệu từ: {path}")
    df = pd.read_csv(path)
    X = df.drop(columns=[target_col])
    y = df[target_col]
    print(f"   Shape X: {X.shape}, Shape y: {y.shape}")
    return X, y


def get_model(task: str):
    """Trả về dict các mô hình theo loại task."""
    if task == 'classification':
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.linear_model import LogisticRegression
        return {
            'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
            'RandomForest':       RandomForestClassifier(n_estimators=100, random_state=42),
            'GradientBoosting':   GradientBoostingClassifier(n_estimators=100, random_state=42),
        }
    elif task == 'regression':
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        from sklearn.linear_model import LinearRegression, Ridge
        return {
            'LinearRegression':   LinearRegression(),
            'Ridge':              Ridge(alpha=1.0),
            'RandomForest':       RandomForestRegressor(n_estimators=100, random_state=42),
            'GradientBoosting':   GradientBoostingRegressor(n_estimators=100, random_state=42),
        }


def evaluate_model(model, X_test, y_test, task):
    """Đánh giá mô hình trên tập test."""
    y_pred = model.predict(X_test)
    if task == 'classification':
        score = accuracy_score(y_test, y_pred)
        print(f"   Accuracy: {score:.4f}")
        print(classification_report(y_test, y_pred))
    else:
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        score = r2
        print(f"   RMSE: {rmse:.4f} | R²: {r2:.4f}")
    return score


# ============================================================
# PIPELINE CHÍNH
# ============================================================
def main():
    print("=" * 60)
    print("🚀 BẮT ĐẦU HUẤN LUYỆN MÔ HÌNH")
    print(f"   Task: {CONFIG['task']}")
    print(f"   Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Tải dữ liệu
    X, y = load_data(CONFIG['data_path'], CONFIG['target_column'])

    # 2. Chia tập train / test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=CONFIG['test_size'],
        random_state=CONFIG['random_state']
    )
    print(f"\n📊 Train size: {X_train.shape[0]} | Test size: {X_test.shape[0]}")

    # 3. Huấn luyện và so sánh các mô hình
    models = get_model(CONFIG['task'])
    results = {}

    print("\n" + "=" * 60)
    print("🔄 HUẤN LUYỆN CÁC MÔ HÌNH")
    print("=" * 60)

    for name, model in models.items():
        print(f"\n▶ {name}")
        model.fit(X_train, y_train)
        score = evaluate_model(model, X_test, y_test, CONFIG['task'])
        results[name] = score

    # 4. Chọn mô hình tốt nhất
    best_name = max(results, key=results.get)
    best_model = models[best_name]
    print(f"\n🏆 Mô hình tốt nhất: {best_name} (Score: {results[best_name]:.4f})")

    # 5. Lưu mô hình
    os.makedirs(CONFIG['model_save_path'], exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_path = os.path.join(CONFIG['model_save_path'], f"{best_name}_{timestamp}.pkl")
    joblib.dump(best_model, save_path)
    print(f"\n💾 Đã lưu mô hình tại: {save_path}")

    # 6. Lưu kết quả
    results_df = pd.DataFrame(list(results.items()), columns=['Model', 'Score'])
    results_df = results_df.sort_values('Score', ascending=False)
    results_path = os.path.join(
        CONFIG['model_save_path'].replace('models', 'experiments'),
        f"results_{timestamp}.csv"
    )
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    results_df.to_csv(results_path, index=False)
    print(f"📋 Kết quả so sánh: {results_path}")
    print("\n✅ HOÀN THÀNH!")


if __name__ == '__main__':
    main()

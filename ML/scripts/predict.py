"""
predict.py — Script dự đoán với mô hình đã huấn luyện
=======================================================
Cách sử dụng:
    python ML/scripts/predict.py --model ML/models/model.pkl --input data/processed/new_data.csv
"""

import os
import sys
import joblib
import argparse
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def load_model(model_path: str):
    """Tải mô hình từ file."""
    print(f"📦 Tải mô hình từ: {model_path}")
    model = joblib.load(model_path)
    print(f"   Loại mô hình: {type(model).__name__}")
    return model


def load_input(input_path: str):
    """Tải dữ liệu đầu vào."""
    print(f"📂 Tải dữ liệu từ: {input_path}")
    df = pd.read_csv(input_path)
    print(f"   Shape: {df.shape}")
    return df


def predict(model, df: pd.DataFrame):
    """Dự đoán kết quả."""
    predictions = model.predict(df)
    return predictions


def main():
    parser = argparse.ArgumentParser(description='Dự đoán với mô hình ML')
    parser.add_argument('--model', type=str, required=True, help='Đường dẫn tới file model (.pkl)')
    parser.add_argument('--input', type=str, required=True, help='Đường dẫn tới file dữ liệu đầu vào')
    parser.add_argument('--output', type=str, default='report/outputs/', help='Thư mục lưu kết quả')
    args = parser.parse_args()

    print("=" * 60)
    print("🔮 DỰ ĐOÁN VỚI MÔ HÌNH ĐÃ HUẤN LUYỆN")
    print("=" * 60)

    model = load_model(args.model)
    df    = load_input(args.input)

    predictions = predict(model, df)

    # Lưu kết quả
    result_df = df.copy()
    result_df['prediction'] = predictions

    os.makedirs(args.output, exist_ok=True)
    timestamp  = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(args.output, f'predictions_{timestamp}.csv')
    result_df.to_csv(output_path, index=False)

    print(f"\n✅ Dự đoán hoàn thành!")
    print(f"   Số dòng: {len(predictions)}")
    print(f"   Kết quả lưu tại: {output_path}")


if __name__ == '__main__':
    main()

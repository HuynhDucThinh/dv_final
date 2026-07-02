# 📊 DV_Final — Data & Analytics Project

> Dự án phân tích dữ liệu và trực quan hóa tổng hợp.

---

## 📁 Cấu trúc thư mục

```
DV_Final/
│
├── data/
│   ├── raw/           # Dữ liệu gốc, chưa xử lý
│   └── processed/     # Dữ liệu đã được làm sạch & xử lý
│
├── notebook/          # Jupyter Notebooks phân tích EDA, khám phá dữ liệu
│
├── ML/                # Các mô hình Machine Learning
│   ├── models/        # File model đã train (.pkl, .joblib, ...)
│   ├── scripts/       # Script train, evaluate, predict
│   └── experiments/   # Log thí nghiệm, kết quả so sánh
│
├── powerBI/           # Báo cáo & dashboard Power BI (.pbix)
│
├── report/            # Báo cáo tổng hợp cuối cùng
│   ├── figures/       # Biểu đồ, hình ảnh export
│   └── outputs/       # File báo cáo (PDF, DOCX, HTML)
│
└── README.md
```

---

## 🚀 Hướng dẫn sử dụng

### 1. Cài đặt môi trường
```bash
pip install -r requirements.txt
```

### 2. Khám phá dữ liệu (EDA)
Mở các notebook trong thư mục `notebook/`.

### 3. Huấn luyện mô hình
```bash
python ML/scripts/train.py
```

### 4. Xem báo cáo
- Power BI: mở file `.pbix` trong thư mục `powerBI/`
- Báo cáo văn bản: xem thư mục `report/`

---

## 👤 Tác giả
- **Tên:** _(cập nhật)_
- **Ngày tạo:** 2026-07-02

# Power BI — Hướng dẫn sử dụng

## 📌 Mô tả
Thư mục này chứa các file Power BI (`.pbix`) và tài liệu liên quan.

## 📂 Nội dung
| File | Mô tả |
|------|-------|
| `overview_dashboard.pbix` | Dashboard tổng quan, KPIs chính |
| `detailed_analysis.pbix` | Phân tích chi tiết theo phân khúc |
| `powerbi_info.json` | Metadata mô tả cấu trúc các dashboard |

## 🔧 Cách sử dụng

### Bước 1: Mở file `.pbix`
- Cài đặt **Power BI Desktop** (miễn phí từ Microsoft Store)
- Double-click vào file `.pbix` để mở

### Bước 2: Cập nhật nguồn dữ liệu
1. Vào **Home → Transform Data → Data Source Settings**
2. Cập nhật đường dẫn trỏ đến thư mục `../data/processed/`

### Bước 3: Refresh dữ liệu
- Nhấn **Home → Refresh** để tải dữ liệu mới nhất

## 🎨 Màu sắc thương hiệu (Brand Colors)
```
Primary:   #1E3A5F  (Navy Blue)
Secondary: #2ECC71  (Emerald Green)
Accent:    #F39C12  (Amber)
Neutral:   #ECF0F1  (Light Gray)
```

## 📋 Checklist tạo Dashboard mới
- [ ] Kết nối đúng nguồn dữ liệu
- [ ] Đặt tên page rõ ràng
- [ ] Thêm tiêu đề và mô tả cho từng visual
- [ ] Thiết lập filter / slicer
- [ ] Kiểm tra responsive trên các màn hình khác nhau
- [ ] Export sang PDF để báo cáo

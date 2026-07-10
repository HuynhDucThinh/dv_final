# Kế hoạch thực hiện Tab 1: Bức Tranh Thị Trường (Jupyter Notebook)

Dựa trên yêu cầu từ `DASHBOARD_DESIGN.md` và tuân thủ tuyệt đối các quy định trong `writing_rules.md`, dưới đây là kế hoạch chi tiết triển khai "Tab 1 — Bức Tranh Thị Trường" dưới dạng một Jupyter Notebook. Do môi trường thực thi là Notebook, các bộ lọc (slicers) tương tác sẽ được lược bỏ, thay vào đó tập trung vào tính toán và trực quan hoá các biểu đồ tĩnh với chất lượng thẩm mỹ cao nhất theo quy tắc màu sắc (Dark Theme).

## 1. Môi trường và Dữ liệu

### Cell 1: Setup & Imports (Code)
*   **Mục tiêu:** Thiết lập môi trường, cấu hình hiển thị biểu đồ và nạp các thư viện cần thiết. Tất cả thư viện phải nằm gọn ở đây.
*   **Chi tiết kĩ thuật:**
    *   Import `pandas`, `numpy`, `matplotlib.pyplot`, `seaborn`, `squarify` (thư viện chuyên dụng vẽ Treemap).
    *   Định nghĩa hằng số màu sắc theo quy tắc Theme:
        *   `BG_COLOR = '#1A1A2E'` (Nền trang xanh đen đậm)
        *   `CARD_COLOR = '#16213E'` (Nền card/visual xanh đêm)
        *   `PRIMARY_COLOR = '#0F3460'` (Accent chính xanh đậm)
        *   `HIGHLIGHT_COLOR = '#E94560'` (Highlight đỏ cam nhấn)
        *   `TEXT_COLOR = '#FFFFFF'` (Text chính màu trắng)
        *   `POSITIVE_COLOR = '#00B894'` (Màu xanh lá tích cực)
        *   `WARNING_COLOR = '#FDCB6E'` (Màu vàng cảnh báo)
    *   Cấu hình `matplotlib` để loại bỏ đường viền (spines: top, right), tắt lưới (`axes.grid: False`), thiết lập font chữ rõ ràng, độ phân giải cao (`dpi=120`).
    *   Cấu hình `rcParams` để áp dụng màu nền `BG_COLOR` cho `figure`, `CARD_COLOR` cho `axes`, và `TEXT_COLOR` cho tất cả các nhãn (labels, ticks, title, legend).
    *   *Lưu ý:* Tuyệt đối không dùng `%matplotlib inline`.

### Cell 2: Load Processed Data (Code)
*   **Mục tiêu:** Nạp dữ liệu đã qua tiền xử lý từ thư mục `data/processed/`.
*   **Chi tiết kĩ thuật:**
    *   Đọc file `fact_car_listings.csv`.
    *   Merge với các file dimension cần thiết (như `dim_brand.csv`, `dim_body_type.csv`, `dim_condition.csv`, `dim_origin.csv`) thông qua các khóa ngoại `id_...` để lấy nhãn phân loại dạng text.

## 2. Tính toán KPIs

### Cell 3: Giới thiệu KPIs (Markdown)
*   **Nội dung:** Giải thích mục tiêu tính toán các chỉ số định lượng trọng yếu để phác họa nhanh quy mô của tập dữ liệu.

### Cell 4: Tính toán và In KPIs (Code)
*   **Mục tiêu:** Tính toán và in ra màn hình 4 KPI cốt lõi.
*   **Chi tiết kĩ thuật:**
    *   `total_listings`: Đếm tổng số lượng bản ghi (dự kiến ~33,849).
    *   `total_brands`: Đếm số lượng giá trị duy nhất (`nunique()`) của cột hãng xe (dự kiến ~91).
    *   `median_price`: Tính trung vị (`median()`) của cột giá xe.
    *   `top_manufacture_year` và `top_year_count`: Dùng `mode()` trên cột Năm sản xuất và tính tổng số lượng của năm đó.
    *   In kết quả bằng tiếng Việt, định dạng số dễ nhìn (dấu phẩy phân cách hàng nghìn).

### Cell 5: Nhận xét KPIs (Markdown)
*   **Nội dung:** Nêu bật quy mô của thị trường dựa trên các số liệu thực tế vừa in ra, giải thích việc sử dụng trung vị (median) thay vì trung bình (mean) để mô tả giá xe nhằm loại bỏ ảnh hưởng của xe siêu sang.

## 3. Trực quan hoá (Visualizations)

### Cell 6: Giới thiệu Treemap Hãng Xe (Markdown)
*   **Nội dung:** Dẫn dắt vào biểu đồ cơ cấu thị phần của Top 15 hãng xe phổ biến nhất.

### Cell 7: Treemap Top 15 Hãng Xe (Code)
*   **Mục tiêu:** Vẽ biểu đồ Treemap thể hiện tỷ trọng số lượng xe của từng hãng.
*   **Chi tiết kĩ thuật:** Lọc Top 15 hãng, dùng `squarify.plot`. Tùy chỉnh màu sắc dựa trên dải màu từ `PRIMARY_COLOR` (#0F3460), nhãn hiển thị bằng `TEXT_COLOR` (#FFFFFF) gồm tên hãng và tỷ lệ %. Đặt màu viền đồng nhất với `CARD_COLOR` để tách các ô. Dùng `plt.show()` ở cuối.

### Cell 8: Nhận xét Treemap (Markdown)
*   **Nội dung:** Đánh giá sự thống trị của các hãng xe Nhật, Hàn, Mỹ (Toyota, Hyundai, Ford,...) trên thị trường.

### Cell 9: Giới thiệu Bar Chart Dòng Xe (Markdown)
*   **Nội dung:** Đặt vấn đề về thị hiếu chọn kiểu dáng xe (Body Type) của người tiêu dùng.

### Cell 10: Bar Chart Dòng Xe Phổ Biến (Code)
*   **Mục tiêu:** Vẽ Bar Chart ngang đếm số lượng tin đăng theo Dòng xe.
*   **Chi tiết kĩ thuật:** Dùng `sns.barplot` dạng ngang (`orient='h'`). Tô màu các cột bằng `PRIMARY_COLOR` (#0F3460). Sắp xếp dữ liệu từ cao xuống thấp. Đưa nhãn số lượng (data labels) màu `TEXT_COLOR` vào cuối mỗi thanh bar. Đảm bảo nền biểu đồ là `CARD_COLOR`.

### Cell 11: Nhận xét Bar Chart (Markdown)
*   **Nội dung:** Nhận định về sự áp đảo của SUV và Sedan so với các phân khúc khác.

### Cell 12: Giới thiệu Donut Charts (Markdown)
*   **Nội dung:** Giải thích mục tiêu xem xét cán cân cung cầu giữa xe mới/cũ và xe lắp ráp/nhập khẩu.

### Cell 13: Donut Charts (Code)
*   **Mục tiêu:** Vẽ 2 Donut Chart song song (1 dòng, 2 cột).
*   **Chi tiết kĩ thuật:**
    *   Dùng `plt.pie` với tham số `wedgeprops=dict(width=0.4, edgecolor=CARD_COLOR)` để tạo lỗ trống ở giữa và chia viền.
    *   Chart 1: Tỷ lệ Tình trạng (Mới vs Đã dùng). Dùng màu `POSITIVE_COLOR` (#00B894) cho Xe Mới và `PRIMARY_COLOR` (#0F3460) cho Xe Đã dùng.
    *   Chart 2: Tỷ lệ Xuất xứ (Lắp ráp vs Nhập khẩu). Dùng màu `HIGHLIGHT_COLOR` (#E94560) cho Nhập khẩu và `PRIMARY_COLOR` cho Lắp ráp.
    *   Text nhãn tỷ lệ sử dụng màu `TEXT_COLOR`.

### Cell 14: Nhận xét Donut Charts (Markdown)
*   **Nội dung:** Trình bày chi tiết tỷ lệ 79.7% xe cũ so với 20.3% xe mới, và 58% xe lắp ráp so với 42% xe nhập khẩu.

### Cell 15: Giới thiệu Column Chart Năm Sản Xuất (Markdown)
*   **Nội dung:** Đặt vấn đề về độ tuổi của xe trên thị trường và sự bùng nổ của các hãng xe nội địa/xe điện (VinFast) trong những năm gần đây.

### Cell 16: Column Chart Năm Sản Xuất (Code)
*   **Mục tiêu:** Vẽ biểu đồ cột dọc thể hiện số lượng xe theo năm sản xuất, tập trung vào 15 năm gần nhất.
*   **Chi tiết kĩ thuật:**
    *   Dùng `sns.barplot` cột dọc.
    *   Để highlight giai đoạn bùng nổ của VinFast (từ 2019 đến nay), sử dụng màu nổi bật `HIGHLIGHT_COLOR` (#E94560) cho các thanh bar từ năm 2019 trở đi. Các năm trước đó dùng màu `PRIMARY_COLOR` (#0F3460).
    *   Thêm Text Annotation mũi tên chỉ vào vùng 2019-2023 với ghi chú "Giai đoạn VinFast bùng nổ" sử dụng màu `WARNING_COLOR` (#FDCB6E) hoặc `TEXT_COLOR` (#FFFFFF) để nổi bật trên nền tối.

### Cell 17: Nhận xét Column Chart (Markdown)
*   **Nội dung:** Đánh giá xu hướng tập trung giao dịch ở các đời xe 2021-2023 và tác động của thị trường xe điện/VinFast đến nguồn cung xe lướt.

## Design Layout

```text
┌──────────────────────────────────────────────────────────────────┐
│ KPI Row: Tổng tin 33,849 | 91 Hãng xe | Giá trung vị | Đời phổ biến │
├────────────────────────────┬─────────────────────────────────────┤
│                            │                                     │
│   Treemap                  │   Bar Chart                         │
│   Thị phần Top 15 Hãng xe  │   Dòng xe phổ biến                  │
│                            │                                     │
├────────────────────────────┼─────────────────────────────────────┤
│                            │                                     │
│   Donut Charts             │   Column Chart                      │
│   Tỷ lệ Mới/Cũ & Lắp ráp/  │   Số lượng xe theo                  │
│   Nhập khẩu                │   năm sản xuất (15 năm gần nhất)    │
│                            │                                     │
└────────────────────────────┴─────────────────────────────────────┘
```

Bố cục thiết kế 2×2 phân bổ đồng đều, mỗi biểu đồ chiếm một phần tư diện tích để tạo sự cân bằng trực quan. Hàng KPI chạy ngang ở vị trí trên cùng nhằm cung cấp ngay các thông số tổng quát làm bối cảnh phân tích về quy mô thị trường. Các biểu đồ phía trên (Treemap và Bar Chart ngang) giúp phác họa cấu trúc phân loại xe theo hãng và dòng xe, trong khi hai biểu đồ bên dưới (Donut Charts và Column Chart) đi sâu vào các yếu tố tình trạng, xuất xứ và xu hướng thay đổi qua các năm.

Toàn bộ nền thống nhất Dark Theme: `#1A1A2E` cho figure, `#16213E` cho từng ô đồ thị.

## Kỷ luật Tuân thủ (Kiểm tra chéo)

- Thiết kế Dark Theme được tuân thủ nghiêm ngặt ở nền, nhãn, trục và các thanh dữ liệu.
- Output, title, label 100% tiếng Việt.
- Comment code 100% tiếng Anh.
- Tên biến chuẩn `snake_case`.
- Không sử dụng ký tự phân cách ngang theo luật cấm.
- Nhận xét (Markdown) chỉ được chốt nội dung sau khi có biểu đồ thực tế. Nếu cần sinh sẵn khung, sẽ tuân thủ việc đánh dấu ghi chú vào Bảng Ghi chú ở mục 6 (writing_rules.md).

# 📊 DASHBOARD DESIGN GUIDE — THỊ TRƯỜNG XE Ô TÔ VIỆT NAM
### Nguồn dữ liệu: bonbanh.com | 33,849 tin đăng | Phân tích bằng Power BI

---

## 📋 MỤC LỤC

1. [Tổng quan kiến trúc dữ liệu](#1-tổng-quan-kiến-trúc-dữ-liệu)
2. [Quy tắc thiết kế chung](#2-quy-tắc-thiết-kế-chung)
3. [Tab 1 — Bức Tranh Thị Trường](#3-tab-1--bức-tranh-thị-trường)
4. [Tab 2 — Giải Mã Giá Xe](#4-tab-2--giải-mã-giá-xe)
5. [Tab 3 — Cuộc Chiến Xăng vs Điện](#5-tab-3--cuộc-chiến-xăng-vs-điện)
6. [Tab 4 — Chân Dung Người Mua](#6-tab-4--chân-dung-người-mua)
7. [Tab 5 — Góc Khuất Thị Trường](#7-tab-5--góc-khuất-thị-trường)
8. [Tổng hợp Slicers & Interactions](#8-tổng-hợp-slicers--interactions)
9. [DAX Measures cần tạo](#9-dax-measures-cần-tạo)

---

## 1. TỔNG QUAN KIẾN TRÚC DỮ LIỆU

### Mô hình Star Schema (đã xây dựng sẵn)

- **Fact Table:** `fact_car_listings` (33,849 dòng)
- **Dimension Tables:** 
  - `dim_brand` (91 hãng)
  - `dim_body_type` (11 dòng)
  - `dim_condition` (2: Mới/Cũ)
  - `dim_origin` (2: Nhập/Lắp)
  - `dim_fuel_type` (5 loại)
  - `dim_transmission` (5 loại)
  - `dim_drivetrain` (5 loại)
  - `dim_exterior_color` (18 màu)
  - `dim_interior_color` (18 màu)
  - `dim_grade` (613 phân khúc)

---

## 2. QUY TẮC THIẾT KẾ CHUNG

### Màu sắc chủ đạo (Theme)
- **Nền trang:** #1A1A2E (xanh đen đậm)
- **Nền card/visual:** #16213E (xanh đêm)
- **Accent chính:** #0F3460 (xanh đậm)
- **Highlight:** #E94560 (đỏ cam nhấn)
- **Text chính:** #FFFFFF (trắng)
- **Tích cực:** #00B894 (xanh lá)
- **Cảnh báo:** #FDCB6E (vàng)

### Nguyên tắc tương tác (Interactions)
- **Cross-filtering bật:** Tất cả visual trong cùng tab filter lẫn nhau khi click.
- **Drill-through:** Từ Tab 1 có thể drill sang Tab 2 (xem giá), Tab 3 (xem nhiên liệu).
- **Tooltips tùy chỉnh:** Mỗi visual có tooltip hiển thị thêm thông tin chi tiết.

---

## 3. TAB 1 — BỨC TRANH THỊ TRƯỜNG

**Mục tiêu:** Cái nhìn toàn cảnh thị trường.

### 📌 KPI Cards (hàng đầu trang)
1. **Tổng tin đăng:** 33,849
2. **Tổng hãng xe:** 91 hãng
3. **Giá trung vị:** 638 triệu VND
4. **Năm SX nhiều nhất:** 2023 (4,006 xe)

### 📊 Các Visual
1. **Treemap:** Top 15 Hãng Xe theo Số Lượng.
2. **Bar Chart ngang:** Dòng Xe (Body Type) Phổ Biến.
3. **Donut Chart:** Xe Mới (20.3%) vs Xe Cũ (79.7%).
4. **Donut Chart:** Xuất Xứ Xe (Lắp ráp 58% vs Nhập khẩu 42%).
5. **Column Chart:** Số Lượng Xe theo Năm SX (highlight giai đoạn bùng nổ của VinFast).

### 🎛️ Bộ lọc (Slicers)
- **Hãng xe:** Dropdown / Search.
- **Tình trạng:** Button (Xe mới / Xe đã dùng).
- **Khoảng năm SX:** Slider (Between).

---

## 4. TAB 2 — GIẢI MÃ GIÁ XE

**Mục tiêu:** Phân tích dải giá và yếu tố ảnh hưởng.

### 📌 KPI Cards
1. **Giá thấp nhất:** 18 triệu
2. **Giá trung vị:** 638 triệu
3. **80% xe bán dưới:** ~1,087 triệu
4. **Giá cao nhất:** 54,000 triệu

### 📊 Các Visual
1. **Histogram:** Phân Phối Giá Toàn Thị Trường (các nhóm giá <500tr, 500-800tr...).
2. **Bar Chart:** Giá Trung Vị theo Top 15 Hãng (Lexus cao nhất, Daewoo thấp nhất).
3. **Line Chart:** Giá Trung Vị theo Năm SX (So sánh giá trị xe theo thời gian).
4. **Clustered Bar:** Giá theo Xuất Xứ (Nhập khẩu đắt hơn Lắp ráp).
5. **Scatter Plot:** Km Đã Đi vs Giá (Xe Cũ). Trục X: Km, Trục Y: Giá.
6. **Box Plot:** Phân Phối Giá theo Dòng Xe.

### 🎛️ Bộ lọc (Slicers)
- **Khoảng giá:** Slider (Between 0 - 5,000 triệu).
- **Xuất xứ:** Button.
- **Hãng xe:** Dropdown.

---

## 5. TAB 3 — CUỘC CHIẾN XĂNG VS ĐIỆN

**Mục tiêu:** Sự tăng trưởng thần tốc của xe điện.

### 📌 KPI Cards
1. **Tổng Xe Điện:** 768 (2.3%)
2. **Thị phần xe điện 2025:** 19.79%
3. **Hãng xe điện số 1:** VinFast (89%)
4. **Tốc độ tăng trưởng xe điện:** 90x trong 4 năm.

### 📊 Các Visual
1. **Combo Chart (Bar + Line):** Thị Phần Xe Điện Theo Từng Năm (2020-2025). Cột là số lượng, Đường là % thị phần.
2. **100% Stacked Bar:** Cơ Cấu Nhiên Liệu theo Năm.
3. **Clustered Bar:** So Sánh Giá Theo Phân Khúc (Xăng vs Điện). Trực quan hóa giá xe điện rẻ hơn xe xăng.
4. **Donut:** Phân Bổ Dòng Xe trong Xe Điện (SUV 67%).
5. **Stacked Bar:** Tỷ Lệ Xe Mới/Cũ theo Loại Nhiên Liệu. Xe điện có tỷ lệ xe mới rất cao (44.5%).
6. **Box Plot:** Km Đã Đi: Xe Cũ Điện vs Xăng.

### 🎛️ Bộ lọc (Slicers)
- **Loại nhiên liệu:** Button (Xăng/Điện/Hybrid/Dầu).
- **Năm sản xuất:** Slider.
- **Tình trạng:** Button (Mới/Cũ).

---

## 6. TAB 4 — CHÂN DUNG NGƯỜI MUA

**Mục tiêu:** Thói quen mua sắm (Màu sắc, số chỗ, hộp số).

### 📌 KPI Cards
1. **Màu ngoại thất Top 1:** Trắng (33.5%)
2. **Màu nội thất Top 1:** Đen (42.7%)
3. **Hộp số Top 1:** Tự động (74.3%)
4. **Số chỗ Top 1:** 5 chỗ (68.8%)

### 📊 Các Visual
1. **Bar Chart Màu:** Màu Ngoại Thất Phổ Biến. Mỗi thanh được tô theo màu thực tế của xe.
2. **Bar Chart Màu:** Màu Nội Thất Phổ Biến.
3. **100% Stacked Bar:** Hộp Số theo Năm (Số tự động vs Số tay). Thể hiện xu hướng loại bỏ số tay.
4. **Donut:** Số Chỗ Ngồi (5 chỗ vs 7 chỗ).
5. **Matrix Heatmap:** Hãng × Màu Ngoại Thất. Xem hãng nào chuộng màu nào nhất.
6. **Line Chart:** Km Trung Bình của Xe Cũ theo Năm SX.

### 🎛️ Bộ lọc (Slicers)
- **Dòng xe:** Dropdown.
- **Khoảng giá:** Slider (Phân tích thói quen mua theo tầm giá).
- **Số chỗ ngồi:** Dropdown.

---

## 7. TAB 5 — GÓC KHUẤT THỊ TRƯỜNG

**Mục tiêu:** Những điều dữ liệu tiết lộ mà mắt thường không thấy (Outliers).

### 📌 KPI Cards
1. **Xe rẻ nhất:** 18 triệu (Kia Pride 1996)
2. **Xe đắt nhất:** 54,000 triệu (Ferrari SF90)
3. **Xe đi nhiều nhất:** 500,000 km
4. **Tăng trưởng nhanh nhất:** VinFast

### 📊 Các Visual
1. **Bar Chart:** Top 10 Xe Đắt Nhất.
2. **Bar Chart:** Top 10 Xe Rẻ Nhất.
3. **Line Chart:** Sự Trỗi Dậy và Suy Tàn của Các Hãng Xe. Highlight VinFast và BYD.
4. **Scatter Plot:** Bản Đồ Định Vị Thương Hiệu. Trục X: Giá trung vị, Trục Y: Số lượng xe bán.
5. **Histogram:** Phân Phối Km Xe Cũ. Đánh dấu các outlier 500,000 km.
6. **Thẻ Bí Mật (Text Card):** Trình bày các facts bất ngờ.

### 🎛️ Bộ lọc (Slicers)
- **Hãng xe:** Dropdown Multi.
- **Năm sản xuất:** Slider.
- **Khoảng giá:** Slider (để dễ dàng loại bỏ outlier).

---

## 8. TỔNG HỢP SLICERS & INTERACTIONS

Nên có một **Filter Pane** (thanh công cụ lọc) nằm gọn ở mép trái hoặc phải của Dashboard, áp dụng cho tất cả các trang (Global Filters).

**Các Filters chính cần có trong Filter Pane:**
- `Năm sản xuất` (Slider)
- `Tình trạng xe` (Mới/Cũ)
- `Hãng xe` (Dropdown)
- `Loại nhiên liệu` (Xăng/Dầu/Điện)
- `Khoảng giá` (Slider)

---

## 9. DAX MEASURES CẦN TẠO

Tạo một `Measure Table` riêng biệt để lưu tất cả các DAX. Dưới đây là các measure chính:

```dax
-- Đếm tổng số
Tổng tin đăng = COUNTROWS(fact_car_listings)

-- Phân tích giá
Giá trung vị = MEDIAN(fact_car_listings[Giá (triệu VND)])
Giá min = MIN(fact_car_listings[Giá (triệu VND)])
Giá max = MAX(fact_car_listings[Giá (triệu VND)])

-- Tỷ trọng
% Xe điện = DIVIDE(CALCULATE(COUNTROWS(fact_car_listings), dim_fuel_type[Loại nhiên liệu] = "Điện"), COUNTROWS(fact_car_listings))
% Xe mới = DIVIDE(CALCULATE(COUNTROWS(fact_car_listings), dim_condition[Tình trạng] = "Xe mới"), COUNTROWS(fact_car_listings))

-- Phân tích chênh lệch
Giá median Nhập khẩu = CALCULATE(MEDIAN(fact_car_listings[Giá (triệu VND)]), dim_origin[Xuất xứ] = "Nhập khẩu")
Giá median Lắp ráp = CALCULATE(MEDIAN(fact_car_listings[Giá (triệu VND)]), dim_origin[Xuất xứ] = "Lắp ráp trong nước")
Chênh lệch Nhập vs Lắp = [Giá median Nhập khẩu] - [Giá median Lắp ráp]
```

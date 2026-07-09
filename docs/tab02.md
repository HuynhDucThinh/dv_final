# Kế hoạch thực hiện Tab 2: Giải mã giá xe (Jupyter Notebook)

Dựa trên yêu cầu từ tài liệu thiết kế và tuân thủ các quy tắc viết báo cáo, dưới đây là kế hoạch chi tiết triển khai phần phân tích giá xe dưới dạng một Jupyter Notebook. Do đặc thù môi trường chạy tĩnh, các bộ lọc tương tác được lược bỏ, thay vào đó tập trung thể hiện bốn đồ thị chất lượng cao đồng bộ theo phong cách tối.

## 1. Môi trường và Dữ liệu

### Cell 1: Setup & Imports (Code)
*   Mục tiêu: Thiết lập môi trường và cấu hình các thuộc tính hiển thị đồ thị.
*   Chi tiết kĩ thuật:
    *   Nạp các thư viện pandas, numpy, matplotlib.pyplot và seaborn.
    *   Định nghĩa các hằng số màu sắc cho phong cách tối:
        *   `BG_COLOR = '#1A1A2E'` (màu nền chính của trang)
        *   `CARD_COLOR = '#16213E'` (màu nền của từng ô đồ thị)
        *   `PRIMARY_COLOR = '#0F3460'` (màu sắc chủ đạo cho dữ liệu)
        *   `HIGHLIGHT_COLOR = '#E94560'` (màu nhấn làm nổi bật thông tin)
        *   `TEXT_COLOR = '#FFFFFF'` (màu chữ chính)
        *   `POSITIVE_COLOR = '#00B894'` (màu xanh lá bổ trợ)
        *   `WARNING_COLOR = '#FDCB6E'` (màu vàng cảnh báo)
    *   Thiết lập plt.rcParams để áp dụng hình nền `BG_COLOR`, khung hiển thị `CARD_COLOR`, màu chữ `TEXT_COLOR` cho các nhãn, tiêu đề, hệ trục tọa độ và độ phân giải cao `dpi=120`.
    *   Loại bỏ các đường viền phía trên và phía bên phải của đồ thị để giao diện thoáng hơn.

### Cell 2: Load Processed Data (Code)
*   Mục tiêu: Đọc nguồn dữ liệu và thực hiện các phép liên kết cần thiết.
*   Chi tiết kĩ thuật:
    *   Đọc tệp tin dữ liệu `fact_car_listings.csv` từ thư mục đã xử lý.
    *   Liên kết với các bảng danh mục `dim_brand.csv`, `dim_body_type.csv`, `dim_condition.csv`, `dim_origin.csv` để lấy giá trị dạng chữ tương ứng cho hãng xe, dòng xe, tình trạng và xuất xứ.

## 2. Tính toán KPIs

### Cell 3: Giới thiệu KPIs (Markdown)
*   Nội dung: Trình bày mục tiêu đo lường dải giá xe để người đọc nắm bắt nhanh cấu trúc giá cả trên thị trường.

### Cell 4: Tính toán và In KPIs (Code)
*   Mục tiêu: Xác định các giá trị biên và giá trị trung vị của giá xe.
*   Chi tiết kĩ thuật:
    *   Tính giá xe thấp nhất bằng hàm `min()`.
    *   Tính giá xe trung vị bằng hàm `median()`.
    *   Xác định mức giá mà 80% số lượng xe trên thị trường nằm dưới ngưỡng đó bằng hàm `quantile()` với tham số `0.8`.
    *   Tính giá xe cao nhất bằng hàm `max()`.
    *   In ra các kết quả dưới dạng số nguyên có dấu phẩy phân cách hàng nghìn.

### Cell 5: Nhận xét KPIs (Markdown)
*   Nội dung: Nhận xét dải giá xe từ mức tối thiểu 18 triệu đồng của xe đời cũ đến mức tối đa 54,000 triệu đồng của xe siêu sang. Giá trị trung vị ở mức 638 triệu đồng và ngưỡng 80% xe dưới 1,087 triệu đồng cho thấy phần lớn thị trường là các xe phổ thông.

## 3. Trực quan hoá (Visualizations)

### Cell 6: Giới thiệu Histogram phân phối giá xe (Markdown)
*   Nội dung: Dẫn dắt người đọc tìm hiểu về sự phân bổ của các tin đăng theo từng tầm giá cụ thể.

### Cell 7: Histogram phân phối giá xe (Code)
*   Mục tiêu: Trực quan hóa cấu trúc phân bổ giá xe toàn thị trường.
*   Chi tiết kĩ thuật:
    *   Sử dụng hàm `pd.cut` để phân nhóm cột `Giá (triệu VND)` thành các khoảng: `< 500 triệu`, `500 đến 800 triệu`, `800 đến 1200 triệu`, `1.2 đến 2 tỷ`, `2 đến 5 tỷ`, `> 5 tỷ`.
    *   Dùng `plt.bar` vẽ biểu đồ cột dọc thể hiện số lượng tin đăng cho mỗi nhóm giá.
    *   Tô màu nhóm xe giá dưới 500 triệu (nhóm chiếm số lượng lớn nhất) bằng `HIGHLIGHT_COLOR` (#E94560), các nhóm còn lại dùng `PRIMARY_COLOR` (#0F3460).
    *   Hiển thị nhãn số lượng (`data labels`) dạng text màu `TEXT_COLOR` (#FFFFFF) ở đỉnh mỗi cột bằng `plt.text` với căn lề giữa (`ha='center'`).

### Cell 8: Nhận xét Histogram (Markdown)
*   Nội dung: Mô tả xu hướng phân bổ tập trung ở phân khúc xe giá rẻ dưới 500 triệu đồng. Số lượng tin đăng giảm dần khi mức giá tăng lên, thể hiện rõ quy luật cầu giảm ở các phân khúc giá cao.

### Cell 9: Giới thiệu Bar Chart giá xe theo hãng (Markdown)
*   Nội dung: Đặt câu hỏi về mức định giá trung vị của các hãng xe phổ biến nhất tại Việt Nam.

### Cell 10: Bar Chart giá xe theo hãng (Code)
*   Mục tiêu: So sánh giá xe trung vị giữa các hãng xe lớn có nhiều tin đăng nhất.
*   Chi tiết kĩ thuật:
    *   Lọc ra danh sách 15 hãng xe có tần suất xuất hiện cao nhất trong tập dữ liệu bằng `value_counts().head(15)`.
    *   Tính toán giá trung vị cho từng hãng xe này bằng `groupby('Hãng')['Giá (triệu VND)'].median()` và sắp xếp theo thứ tự giảm dần.
    *   Vẽ biểu đồ cột ngang bằng `plt.barh` hiển thị giá trung vị của các hãng.
    *   Tô màu `HIGHLIGHT_COLOR` (#E94560) cho Lexus để nhấn mạnh mức giá cao vượt trội và WARNING_COLOR cho Daewoo để biểu thị dòng xe giá rẻ nhất, các hãng còn lại dùng `PRIMARY_COLOR` (#0F3460).
    *   Dùng `plt.text` hiển thị giá trị trung vị màu `TEXT_COLOR` ở cuối mỗi thanh với căn lề trái (`ha='left'`).

### Cell 11: Nhận xét Bar Chart (Markdown)
*   Nội dung: Đánh giá sự phân hóa rõ nét giữa các hãng xe phổ thông và xe sang. Thương hiệu Lexus dẫn đầu về mức giá trị trung vị trong khi thương hiệu Daewoo ghi nhận giá trị thấp nhất.

### Cell 12: Giới thiệu Line Chart giá xe theo năm (Markdown)
*   Nội dung: Tìm hiểu mức độ biến động giá trị xe theo độ tuổi sản xuất của phương tiện.

### Cell 13: Line Chart giá xe theo năm (Code)
*   Mục tiêu: Thể hiện xu hướng biến đổi giá xe trung vị theo thời gian.
*   Chi tiết kĩ thuật:
    *   Lọc dữ liệu các xe sản xuất trong giai đoạn từ năm 2010 đến năm 2025.
    *   Tính giá xe trung vị theo từng năm sản xuất bằng `groupby('Năm sản xuất')['Giá (triệu VND)'].median()`.
    *   Vẽ biểu đồ đường bằng `plt.plot` với `marker='o'` màu `HIGHLIGHT_COLOR` (#E94560) và `linewidth=2`.
    *   Bật lưới tọa độ mờ bằng `plt.grid(True, linestyle='--', alpha=0.3, color=PRIMARY_COLOR)`.
    *   Hiển thị giá trị trung vị tại các mốc năm bằng `plt.text` màu `TEXT_COLOR` nằm phía trên điểm nút (`va='bottom'`).

### Cell 14: Nhận xét Line Chart (Markdown)
*   Nội dung: Giải thích sự suy giảm giá trị xe theo thời gian do yếu tố hao mòn tự nhiên. Mức giá xe tăng nhanh ở các đời xe gần đây từ năm 2020 đến năm 2025 do yếu tố công nghệ mới và chất lượng xe còn rất mới.

### Cell 15: Giới thiệu Scatter Plot km đi và giá bán xe cũ (Markdown)
*   Nội dung: Phân tích sự tác động của quãng đường di chuyển đến giá trị giao dịch của xe cũ.

### Cell 16: Scatter Plot km đi và giá bán xe cũ (Code)
*   Mục tiêu: Khám phá mối tương quan giữa số km đã đi và giá bán xe.
*   Chi tiết kĩ thuật:
    *   Lọc tập dữ liệu chỉ lấy các bản ghi xe đã qua sử dụng với điều kiện tình trạng là Xe đã dùng.
    *   Giới hạn vùng biểu diễn dưới 300,000 km di chuyển và mức giá dưới 4,000 triệu đồng để tránh các điểm dị biệt gây loãng biểu đồ.
    *   Dùng `plt.scatter` vẽ biểu đồ phân tán với độ trong suốt `alpha=0.3`, kích thước điểm `s=15`, màu điểm `PRIMARY_COLOR` (#0F3460).
    *   Tính toán hệ số hồi quy tuyến tính bằng `np.polyfit` và vẽ đường xu hướng bằng `plt.plot` màu `HIGHLIGHT_COLOR` (#E94560) để chỉ ra chiều hướng biến động.

### Cell 17: Nhận xét Scatter Plot (Markdown)
*   Nội dung: Nhận định mối quan hệ nghịch biến giữa số km đã đi và giá bán. Xe đi càng nhiều thì giá bán càng giảm, tuy nhiên độ phân tán rộng cho thấy mức giá còn phụ thuộc vào nhiều yếu tố khác như chất lượng bảo dưỡng hay thương hiệu xe.

## Kỷ luật Tuân thủ (Kiểm tra chéo)

- Thiết kế đồ thị đồng bộ theo phong cách tối với hệ màu được định nghĩa sẵn.
- Tiêu đề, nhãn trục và các câu thông báo đầu ra hoàn toàn sử dụng tiếng Việt.
- Các chú thích trong phần code được viết bằng tiếng Anh.
- Tên các biến số đặt theo định dạng snake_case rõ nghĩa.
- Không sử dụng ký tự gạch ngang làm dấu ngắt câu trong toàn bộ văn xuôi.

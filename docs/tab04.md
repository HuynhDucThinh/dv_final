# Tab 4 — Chân Dung Người Mua

## Mục tiêu phân tích

Tab này phân tích hành vi mua xe thông qua bốn góc nhìn: màu sắc được chọn, số chỗ ngồi cần thiết, loại hộp số ưa dùng, và quãng đường xe cũ đã đi trước khi sang tay. Khi nhìn bốn chỉ số này cùng nhau, hành vi người mua hiện ra khá nhất quán — và khác với hình ảnh thường thấy trong quảng cáo.

---

## KPI — Bốn tín hiệu hành vi

| Chỉ số | Giá trị | Ý nghĩa |
|---|---|---|
| Màu ngoại thất #1 | Trắng — 33.6% | 1/3 thị trường chọn màu an toàn nhất |
| Nội thất phổ biến #1 | Đen — 42.6% | Gần một nửa chọn màu thực dụng nhất |
| Hộp số #1 | Số tự động — 74.3% | 3/4 không muốn tự đạp côn |
| Số chỗ #1 | 5 chỗ — 68.8% | Gia đình hạt nhân làm chuẩn mực |

Bốn chỉ số này khá nhất quán với nhau: người mua chọn màu dễ bán lại (Trắng), nội thất dễ vệ sinh (Đen), hộp số không cần thao tác nhiều (Tự động), và xe đủ chỗ cho gia đình nhỏ (5 chỗ). Không có gì đặc biệt về sở thích cá nhân — đây là bộ lựa chọn tối ưu cho xe dùng hàng ngày ở đô thị.

---

## Biểu đồ 1 — Bar Chart: Bảng Màu Người Mua Việt Chọn

### Loại biểu đồ
Bar chart nằm ngang, mỗi thanh tô theo màu thực tế của xe. Đây là biểu đồ duy nhất trong toàn dashboard mà **màu của thanh chính là dữ liệu** — không cần legend, người đọc hiểu ngay.

### Màu sắc
Mỗi thanh dùng chính xác màu thực của xe:
Trắng `#F5F5F5` (viền `#CCCCCC`), Đen `#1A1A1A`, Đỏ `#CC2936`, Bạc `#C0C0C0`, Xanh `#1A5276`, Xám `#808080`, Nâu `#795548`, Vàng `#F9A825`, Cát `#D4B483`, Cam `#E67E22`.

### Dữ liệu thực

| Màu ngoại thất | Số xe | Tỷ lệ (%) |
|---|---|---|
| Trắng | 11,358 | 33.6% |
| Đen | 7,440 | 22.0% |
| Đỏ | 4,296 | 12.7% |
| Bạc | 2,939 | 8.7% |
| Xanh | 2,747 | 8.1% |
| Xám | 1,250 | 3.7% |
| Nâu | 862 | 2.5% |
| Vàng | 749 | 2.2% |
| Cát | 700 | 2.1% |
| Cam | 493 | 1.5% |

*Ghi chú: Loại "Không rõ" và "Nhiều màu" (134 xe, 0.4%) khỏi biểu đồ để so sánh trung thực.*

### Câu chuyện dữ liệu
Ba màu đầu tiên — Trắng, Đen, Đỏ — chiếm 68% tổng thị trường. Trắng dẫn đầu với 33.6%, tức cứ 3 xe bán ra thì có 1 xe trắng.

Trắng phổ biến có một lý do thực tế: xe màu trắng giữ giá tốt hơn khi bán lại, vì người mua xe cũ cũng hay chọn trắng. Vòng này cứ thế lặp lại. Dưới nắng Việt Nam, trắng cũng phản nhiệt tốt hơn các màu đậm — dù đây ít khi là lý do người ta kể ra khi mua xe.

Điểm đáng chú ý: Xanh xếp thứ 5 với 8.1%, cao hơn cả Xám (3.7%). Con số này chủ yếu đến từ VinFast — đội xe taxi Xanh SM và xe giao doanh nghiệp của VinFast kéo màu xanh tím lên vị trí không ai dự đoán. Nếu loại VinFast ra, thứ hạng màu xanh sẽ tụt xuống đáng kể.

---

## Biểu đồ 2 — Donut Chart: Người Mua Cần Bao Nhiêu Chỗ?

### Loại biểu đồ
Donut chart chia thành 4 phần theo số chỗ ngồi, với số liệu hiển thị trực tiếp trên từng phần (không dùng legend riêng). Phần giữa donut hiển thị tổng số mẫu: **33,848 xe**.

### Màu sắc
5 chỗ: `#00B894` (xanh lá — màu chủ đạo, chiếm ưu thế). 7 chỗ: `#0F3460` (xanh đậm). 8 chỗ: `#A29BFE` (tím nhạt). Còn lại: `#636E72` (xám).

### Dữ liệu thực

| Số chỗ ngồi | Số xe | Tỷ lệ (%) |
|---|---|---|
| 5 chỗ | 23,294 | 68.8% |
| 7 chỗ | 6,616 | 19.5% |
| 8 chỗ | 1,816 | 5.4% |
| Khác (2, 3, 4, 6 chỗ…) | 2,122 | 6.3% |

### Câu chuyện dữ liệu
5 chỗ chiếm 68.8% — phần lớn người mua là gia đình nhỏ ở đô thị, xe dùng để đi làm và đưa đón con là chính.

Số đáng chú ý là 7 chỗ chiếm 19.5%. Ở nhiều nước, xe 7 chỗ chỉ chiếm khoảng 10–12% thị trường. Tại Việt Nam tỷ lệ này gần gấp đôi, phản ánh nhu cầu chở cả gia đình lớn vào cuối tuần — Toyota Fortuner và Hyundai Santa Fe bán tốt ở Việt Nam một phần cũng vì lý do này.

8 chỗ (5.4%) chủ yếu là Van/Minivan phục vụ kinh doanh và đưa rước. Nhóm còn lại (6.3%) gồm xe 2–4 chỗ và các loại xe đặc thù — không đáng kể về quy mô.

---

## Biểu đồ 3 — 100% Stacked Bar: Số Tay Đang Biến Mất (2015–2023)

### Loại biểu đồ
100% Stacked Bar chart theo năm, chỉ hiển thị hai lớp: Số tự động và Số tay. Loại bỏ "Không rõ" khỏi tính toán tỷ lệ để so sánh trung thực. Thêm annotation mũi tên vào năm 2021.

### Màu sắc
Số tự động: `#0F3460` (xanh đậm). Số tay: `#E94560` (đỏ cam). Label trực tiếp trên thanh — không dùng legend tách biệt.

### Dữ liệu thực (chỉ tính xe có thông tin hộp số rõ ràng)

| Năm | Số tay | Số tự động | Tự động (%) | Số tay (%) |
|---|---|---|---|---|
| 2015 | 321 | 1,071 | 76.9% | **23.1%** |
| 2016 | 437 | 1,523 | 77.7% | 22.3% |
| 2017 | 361 | 1,445 | 80.0% | 20.0% |
| 2018 | 327 | 2,039 | 86.2% | 13.8% |
| 2019 | 377 | 2,533 | 87.0% | 13.0% |
| 2020 | 211 | 2,374 | 91.8% | 8.2% |
| **2021** | **109** | **2,642** | **96.0%** | **4.0%** ← đáy |
| 2022 | 239 | 3,496 | 93.6% | 6.4% |
| 2023 | 333 | 3,673 | 91.7% | 8.3% |

### Câu chuyện dữ liệu
Năm 2015, cứ 4 xe bán ra thì có 1 xe số tay (23.1%). Đến 2021, con số đó còn 4% — tức 1 trong 25 xe. Trong vòng 6 năm, số tay gần như biến mất khỏi thị trường phổ thông.

Giai đoạn giảm mạnh nhất là 2018–2021. Hai việc xảy ra đồng thời: VinFast ra mắt với toàn bộ lineup số tự động, và Toyota, Hyundai, Kia lần lượt ngừng bán phiên bản số tay ở phân khúc phổ thông. Cầu có thể vẫn còn nhưng cung đã hết — người mua không còn nhiều lựa chọn.

2022–2023 tỷ lệ số tay tăng nhẹ lại, từ 4% lên 6.4–8.3%. Nguyên nhân là lượng xe nhập khẩu cũ từ Nhật Bản và Châu Âu tăng sau COVID — nhiều xe trong số này là số tay, đặc biệt ở phân khúc giá thấp. Đây không phải xu hướng đảo chiều mà chỉ là tác động nhất thời của nguồn hàng nhập.

*Annotation năm 2021: "4% — 1 xe số tay trong 25 xe".*

---

## Biểu đồ 4 — Area Chart: KM Trung Vị Xe Cũ theo Năm Sản Xuất

### Loại biểu đồ
**Area Chart** — vẽ được trực tiếp trong Power BI bằng visual "Area chart" có sẵn (không cần custom visual). Trục X: năm sản xuất (2015–2022). Trục Y: km trung vị (đơn vị: nghìn km). Area fill tô dưới đường để nhấn mạnh độ chênh giữa các năm.

Đường tham chiếu ngang (chuẩn ~15,000 km/năm) thêm qua **Analytics Pane → Constant Line** trong Power BI — nhập giá trị tương ứng với năm gốc cần so sánh. Trong trường hợp này, dùng giá trị `45` (nghìn km) tương đương 3 năm × 15,000 km/năm làm mốc so sánh cho xe 2019.

### Màu sắc
Đường chính + area fill: `#00B894` (xanh lá), opacity area 15%. Marker tròn tại mỗi điểm năm. Đường tham chiếu: `#FDCB6E` (vàng đứt nét). Annotation điểm 2022: nhãn text màu `#FDCB6E`.

### Dữ liệu thực (xe đã qua sử dụng — trung vị km theo năm sản xuất)

| Năm SX | Trung vị KM (nghìn km) | KM/năm ước tính | Số xe cũ trong mẫu |
|---|---|---|---|
| 2015 | 64.0 | ~7,100 km/năm | 1,372 |
| 2016 | 60.0 | ~7,500 km/năm | 1,930 |
| 2017 | 57.0 | ~8,100 km/năm | 1,792 |
| 2018 | 48.0 | ~8,000 km/năm | 2,350 |
| 2019 | 38.0 | ~7,600 km/năm | 2,881 |
| 2020 | 27.0 | ~6,750 km/năm | 2,570 |
| 2021 | 16.9 | ~5,600 km/năm | 2,692 |
| 2022 | 8.0 | ~4,000 km/năm | 1,751 |

*Đường tham chiếu: mức trung bình Đông Nam Á ~10,000–12,000 km/năm. Mỹ ~25,000 km, EU ~13,000 km.*

### Câu chuyện dữ liệu
Xe sản xuất năm 2015, đến nay đã 9–10 năm, chỉ đi được 64,000 km — tức khoảng 7,000 km mỗi năm. Đây thấp hơn mức trung bình Đông Nam Á (10,000–12,000 km/năm) và thấp hơn nhiều so với Mỹ hay châu Âu. Lý do chủ yếu là xe ở Việt Nam phần lớn dùng trong nội thành, đường ngắn và hay tắc — người ta ngồi xe nhiều nhưng di chuyển ít.

Điểm cụ thể đáng nhìn là xe năm 2022 chỉ có 8,000 km khi rao bán — tức chủ xe bán sau chưa đầy 2 năm sử dụng, và xe gần như chưa hao mòn gì đáng kể về cơ học. Nhiều xe trong nhóm này vẫn còn trong thời hạn bảo hành nhà máy (thường 3–5 năm hoặc 100,000 km).

Kết hợp với số liệu từ Tab 3 — xe điện cũ có trung vị chỉ 16,000 km — thị trường xe cũ Việt Nam đang có một lượng xe chạy rất ít, bán sớm, ở tình trạng tốt. Câu hỏi đặt ra là tại sao người ta bán sớm như vậy: nâng cấp model mới, thay đổi nhu cầu, hay không hài lòng với xe — dữ liệu này không đủ để trả lời, nhưng đó là điều đáng theo dõi thêm.

*Annotation tại điểm 2022: "8,000 km — có thể còn bảo hành nhà máy."*

---

## Design Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  KPI: Trắng 33.6%  |  Đen nội thất 42.6%  |  Tự động 74.3%  |  5 chỗ 68.8%  │
├────────────────────────────────┬─────────────────────────────────────────┤
│                                │                                         │
│   Bar Chart (nằm ngang)        │   Donut Chart                           │
│   Màu Ngoại Thất Phổ Biến      │   Phân bổ Số Chỗ Ngồi                  │
│   [thanh = màu thực xe]        │   [5 chỗ 68.8% — phần lớn nhất]        │
│                                │   [số ở giữa = 33,848 xe]               │
│                                │                                         │
├────────────────────────────────┼─────────────────────────────────────────┤
│                                │                                         │
│   100% Stacked Bar             │   Area Chart                            │
│   Số Tay vs Tự Động            │   KM Trung Vị Xe Cũ                     │
│   2015–2023                    │   theo Năm Sản Xuất (2015–2022)         │
│   [annotation: 2021 = 4%]      │   [đường vàng: chuẩn ĐNA ~12k/năm]     │
│                                │   [annotation: 2022 = 8k km]            │
│                                │                                         │
└────────────────────────────────┴─────────────────────────────────────────┘
```

**Luồng đọc có chủ ý:** KPI đặt vấn đề → Bar Chart (màu gì?) → Donut (bao nhiêu chỗ?) → Stacked Bar (lái kiểu gì?) → Line Chart (lái bao nhiêu?). Bốn câu hỏi kế tiếp nhau từ *hình thức* đến *hành vi*, kể một câu chuyện liền mạch về người mua xe Việt Nam.

Biểu đồ trái trên (Bar Chart màu) nên rộng hơn một chút để 11 thanh màu có khoảng thở. Donut (phải trên) cần đủ lớn để phần nhỏ nhất (8 chỗ, 5.4%) vẫn có thể đọc được label. Stacked Bar (trái dưới) cần chiều rộng đủ cho 9 cột không chật chội — ưu tiên aspect ratio ngang.

Toàn bộ nền Dark Theme: `#1A1A2E` cho figure, `#16213E` cho từng ô đồ thị. Text trắng `#FFFFFF`. Annotation highlight `#FDCB6E`.

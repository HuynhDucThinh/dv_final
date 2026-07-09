# Tab 5 — Góc Khuất Thị Trường

## Mục tiêu phân tích

Tab này là phần kết thúc của câu chuyện dữ liệu. Bốn tab trước dựng lên bức tranh tổng quát — thị phần, giá cả, nhiên liệu, hành vi người mua. Tab này đi vào những góc mà bức tranh đó cố tình che lại: xe nào đắt bất thường, xe nào rẻ đến mức gây ngạc nhiên, hãng nào đang thực sự trỗi dậy hay thoái trào, và người bán xe nào đang rao những con số khiến người mua phải dừng lại đọc kỹ hơn. Đây không phải phân tích để tìm xu hướng — đây là phân tích để tìm ngoại lệ, và từ đó hiểu thêm về cách thị trường vận hành ở những phần ít được nhìn thấy nhất.

---

## KPI — Bốn con số mở đầu

| Chỉ số | Giá trị | Ghi chú |
|---|---|---|
| Xe đắt nhất trong dữ liệu | 54,000 triệu VND | Ferrari SF90 Stradale 2020 |
| Xe rẻ nhất trong dữ liệu | 18 triệu VND | Kia Pride Beta 1996 |
| Xe đi nhiều km nhất | 500,000 km | Đi gần bằng một vòng trái đất ×12 |
| Khoảng cách giá min–max | ×3,000 lần | Khoảng cách lớn nhất trong mọi loại hàng hóa thông thường |

Bốn con số đặt cạnh nhau tạo ra bối cảnh cho toàn bộ tab: đây là một thị trường mà cùng một từ "ô tô" được dùng để chỉ một chiếc xe 18 triệu và một siêu xe 54 tỷ đồng. Khoảng cách đó — 3,000 lần — không phải là bất thường nếu nhìn từ góc độ toàn cầu, nhưng chúng tồn tại cùng nhau trên cùng một nền tảng rao vặt tại Việt Nam. Đây là điều tab này cần khám phá.

---

## Biểu đồ 1 — Horizontal Bar Chart: Top 10 Xe Đắt Nhất và Top 10 Xe Rẻ Nhất

### Loại biểu đồ
Hai biểu đồ cột ngang đặt song song (side-by-side), mỗi bên thể hiện 10 dòng xe. Trái: xe đắt nhất. Phải: xe rẻ nhất. Bố cục gương nhau để tạo hiệu ứng tương phản trực quan.

### Màu sắc
Xe đắt nhất: thanh màu `#E94560` (đỏ cam), nhạt dần theo thứ hạng. Xe rẻ nhất: thanh màu `#00B894` (xanh lá), nhạt dần theo thứ hạng. Label giá trị màu `#FFFFFF`. Tên xe màu `#FDCB6E` (vàng) để phân biệt với nhãn số.

### Dữ liệu thực

**Top 10 xe đắt nhất (triệu VND):**

| Tên xe | Hãng | Giá (triệu VND) | Năm SX |
|---|---|---|---|
| Ferrari SF90 Stradale 4.0 V8 | Ferrari | 54,000 | 2020 |
| Rolls Royce Cullinan Black Badge | Rolls Royce | 46,000 | 2021 |
| Rolls Royce Cullinan Black Badge 6.75 V12 | Rolls Royce | 45,000 | 2022 |
| Rolls Royce Cullinan Black Badge 6.75 V12 | Rolls Royce | 45,000 | 2022 |
| Rolls Royce Ghost Series II EWB | Rolls Royce | 39,999 | 2021 |
| Rolls Royce Cullinan | Rolls Royce | 39,990 | 2022 |
| Rolls Royce Cullinan 6.75 V12 | Rolls Royce | 39,900 | 2018 |
| Rolls Royce Cullinan V12 | Rolls Royce | 39,000 | 2022 |
| Rolls Royce Ghost Series II EWB | Rolls Royce | 39,000 | 2021 |
| Rolls Royce Ghost Series II EWB | Rolls Royce | 39,000 | 2021 |

**Top 10 xe rẻ nhất (triệu VND):**

| Tên xe | Hãng | Giá (triệu VND) | Năm SX |
|---|---|---|---|
| Kia Pride Beta | Kia | 18 | 1996 |
| Mitsubishi L300 2.0 MT | Mitsubishi | 21 | 2000 |
| Nissan Sunny EX Saloon | Nissan | 25 | 1992 |
| Toyota Cressida | Toyota | 25 | trước 1990 |
| Mitsubishi L300 2.0 MT | Mitsubishi | 25 | 1999 |
| Daewoo Matiz 0.8 MT | Daewoo | 25 | 2003 |
| Kia Pride Beta | Kia | 27 | 2002 |
| Toyota Hiace Van 2.0 | Toyota | 28 | 2002 |
| Toyota Hiace 2.4 | Toyota | 28 | 2002 |
| Daewoo Matiz SE 0.8 MT | Daewoo | 28 | 2003 |

### Câu chuyện dữ liệu
Top 10 xe đắt nhất hầu như bị chiếm hoàn toàn bởi Rolls Royce — 9 trong 10 chiếc. Thực tế thú vị là Ferrari SF90 Stradale đứng đầu với 54 tỷ nhưng đây là siêu xe hybrid, không phải xe siêu sang theo nghĩa truyền thống. Điều đáng chú ý hơn là sự vắng mặt hoàn toàn của Lamborghini, Bentley, hay Porsche Taycan ở top này — những cái tên thường gắn với "đắt" trong trí tưởng tượng phổ biến nhưng thực ra vẫn thấp hơn mức ngưỡng Rolls Royce đang thiết lập tại đây.

Top 10 rẻ nhất là câu chuyện ngược lại: Kia Pride 1996 với 18 triệu — thấp hơn giá một chiếc điện thoại tầm trung. Đây là thế hệ xe nhỏ từ thập niên 90, nhiều chiếc vẫn đang lưu thông trên đường và xuất hiện trên nền tảng rao vặt như những hiện vật của một giai đoạn thị trường khác. Toyota và Mitsubishi chiếm phần lớn danh sách này với các mẫu van, minibus đời cũ — xe không đẹp nhưng vẫn chạy được, vẫn có người mua.

*Lưu ý khi triển khai:* Trong Power BI, hai biểu đồ này nên đặt trên cùng một hàng với trục Y là tên xe (ngắn gọn, ký hiệu bằng model thôi), trục X là giá tính theo tỷ VND (không phải triệu, để scale hợp lý). Biểu đồ bên trái nên có trục X đảo chiều (từ phải sang trái) để tạo hiệu ứng gương tự nhiên.

---

## Biểu đồ 2 — Multi-Line Chart: Cuộc Đua Thị Phần — Sự Trỗi Dậy và Biến Động của Các Hãng Xe (2018–2025)

### Loại biểu đồ
Line chart với nhiều đường, mỗi đường là một hãng xe lớn. Trục X: năm sản xuất (2018–2025). Trục Y: số lượng xe trong dữ liệu. Annotation dùng callout box nổi bật tại các điểm bùng nổ hoặc sụt giảm quan trọng.

### Màu sắc
VinFast/Vinfast: `#E94560` (đỏ cam — màu nhận diện thương hiệu). Toyota: `#FDCB6E` (vàng). Hyundai: `#00B894` (xanh lá). Kia: `#A29BFE` (tím). Ford: `#0F3460` (xanh đậm). Mazda: `#74B9FF` (xanh nhạt). Honda: `#636E72` (xám). Annotation text: `#FFFFFF`.

### Dữ liệu thực (số lượng xe theo năm sản xuất)

| Năm SX | Toyota | Hyundai | Ford | Kia | Mazda | VinFast* | Honda |
|---|---|---|---|---|---|---|---|
| 2018 | 365 | 337 | 227 | 219 | 309 | 0 | 150 |
| 2019 | 544 | 436 | 282 | 252 | 304 | 74 | 145 |
| 2020 | 430 | 427 | 194 | 245 | 240 | 127 | 99 |
| 2021 | 343 | 336 | 181 | 282 | 153 | 185 | 96 |
| 2022 | 496 | 557 | 140 | 379 | 185 | 260 | 68 |
| 2023 | 704 | 399 | **1,081** | 167 | 207 | 148 | 245 |
| 2024 | 150 | 196 | 181 | 180 | 165 | 140 | 59 |
| 2025 | 119 | 146 | 168 | 87 | 51 | **271** | 38 |

*VinFast và Vinfast được gộp để tính tổng (do lỗi nhất quán tên trong dữ liệu thô).*

### Câu chuyện dữ liệu
Biểu đồ này chứa ít nhất ba điểm dị thường cần annotation.

Điểm thứ nhất: Ford năm 2023 đạt 1,081 xe — gấp gần 8 lần so với 2022 (140 xe). Đây là con số bất thường nhất trong toàn bộ tập dữ liệu nếu nhìn theo chiều hãng × năm. Nguyên nhân có thể là đợt xả hàng tồn kho lớn, chương trình kích cầu sau tắc nghẽn chuỗi cung ứng hậu COVID, hoặc đơn giản là chiến dịch đăng rao hàng loạt của một hệ thống đại lý. Đây là điểm mà dashboard không thể trả lời dứt khoát — nhưng chính việc "không thể trả lời" đó mới là điều quan trọng cần chỉ ra.

Điểm thứ hai: VinFast (gộp cả Vinfast) đạt 271 xe năm 2025 — vượt qua tất cả các hãng truyền thống trong cùng năm đó (Toyota: 119, Hyundai: 146, Ford: 168). Đây là lần đầu tiên VinFast dẫn đầu về số lượng xe mới đăng ký trong năm. Kết hợp với dữ liệu từ Tab 3 (thị phần xe điện đạt 19.79% năm 2025), xu hướng này có tính nhất quán cao.

Điểm thứ ba: Toyota đạt đỉnh 544 xe năm 2019 rồi sụt liên tục đến 2021, phục hồi năm 2022–2023, sau đó lại giảm mạnh năm 2024–2025. Đây là vòng chu kỳ khá điển hình của một thương hiệu phổ thông ở giai đoạn cạnh tranh khốc liệt — không phải suy tàn, mà là đang chia sẻ thị phần với nhiều đối thủ hơn.

*Annotation cần có trong biểu đồ:*
- Mũi tên chỉ đỉnh Ford 2023: *"Ford: 1,081 — dị thường hay đột biến?"*
- Mũi tên chỉ VinFast 2025: *"VinFast lần đầu dẫn đầu (2025)"*
- Highlight vùng 2024–2025 bằng shading nhẹ để phân biệt xu hướng gần đây.

---

## Biểu đồ 3 — Bubble Chart / Scatter Plot: Bản Đồ Định Vị Thương Hiệu

### Loại biểu đồ
Bubble chart (scatter plot với kích thước bong bóng). Trục X: giá trung vị (triệu VND). Trục Y: số lượng xe trong dữ liệu. Kích thước bong bóng: số lượng xe (tỷ lệ thuận). Nhãn tên hãng đặt trực tiếp gần bong bóng. Chỉ bao gồm các hãng có từ 50 xe trở lên để tránh nhiễu.

### Màu sắc
Phân nhóm theo vùng định vị:
- Vùng phổ thông (giá <700tr, số lượng cao): `#0F3460` (xanh đậm)
- Vùng trung cao (700tr–2,000tr): `#A29BFE` (tím)
- Vùng cao cấp (>2,000tr): `#FDCB6E` (vàng)
- VinFast: `#E94560` (đỏ cam) để nổi bật riêng.

### Dữ liệu thực (các hãng có ≥50 xe, theo số lượng giảm dần)

| Hãng | Số lượng | Giá trung vị (tr VND) | Nhóm định vị |
|---|---|---|---|
| Toyota | 5,861 | 552 | Phổ thông |
| Hyundai | 3,897 | 528 | Phổ thông |
| Ford | 3,719 | 699 | Phổ thông–Trung |
| Mercedes Benz | 3,376 | 1,880 | Cao cấp |
| Kia | 3,258 | 465 | Phổ thông |
| Mazda | 2,447 | 598 | Phổ thông |
| Mitsubishi | 1,540 | 575 | Phổ thông |
| Honda | 1,322 | 565 | Phổ thông |
| Lexus | 1,023 | 3,190 | Siêu cao cấp |
| Chevrolet | 802 | 245 | Giá rẻ |
| VinFast | 794 | 680 | Phổ thông–Trung |
| BMW | 668 | 1,460 | Cao cấp |
| Nissan | 471 | 495 | Phổ thông |
| Suzuki | 427 | 455 | Phổ thông |
| Daewoo | 419 | 105 | Giá rẻ cũ |
| Peugeot | 391 | 870 | Trung–Cao |
| LandRover | 380 | 3,889 | Siêu cao cấp |
| Porsche | 379 | 4,150 | Siêu cao cấp |

### Câu chuyện dữ liệu
Biểu đồ này phân tách thị trường thành bốn tứ phần rõ ràng. Góc phải dưới — giá cao, số lượng ít — là Porsche (4,150 tr), Lexus (3,190 tr), LandRover (3,889 tr): thị trường sang trọng, ít người chơi nhưng doanh thu lớn theo đơn vị. Góc trái dưới — giá thấp, số lượng ít — là Daewoo (105 tr) và Chevrolet (245 tr): xe cũ đời xa, thị trường co lại tự nhiên theo thời gian.

Góc trái trên — giá vừa phải, số lượng lớn — là nơi Toyota, Hyundai, Kia, Mazda, Honda tranh nhau thị phần phổ thông. Đây là vùng cạnh tranh khốc liệt nhất và cũng là nơi VinFast đang chen vào với giá trung vị 680 triệu và 794 xe — cao hơn Kia (465 tr) nhưng thấp hơn Ford (699 tr) và đang tăng.

Điểm quan trọng nhất của biểu đồ này không phải là vị trí ai đứng ở đâu, mà là Mercedes Benz xuất hiện ở vùng trung–cao với số lượng 3,376 xe — cao hơn nhiều so với BMW (668 xe) hay Porsche (379 xe). Tại thị trường Việt Nam, Mercedes Benz không chỉ là xe sang, nó là xe phổ biến ở phân khúc cao cấp — một hiện tượng ít thấy ở các nước phát triển khác.

*Annotation gợi ý:* Vẽ bốn vùng phân cách bằng đường đứt nét màu `#636E72` và đánh nhãn góc: "Sang trọng", "Phổ thông", "Giá rẻ cũ", "Trung–Cao".

---

## Biểu đồ 4 — Histogram + KDE: Phân Phối Km Xe Cũ và Câu Hỏi về Xe "Chạy Gần Cả Triệu Km"

### Loại biểu đồ
Histogram (trục X: km đã đi, phân nhóm theo từng 20,000 km) kết hợp đường KDE (Kernel Density Estimate) phủ lên trên. Giới hạn hiển thị chính từ 0 đến 300,000 km để dữ liệu đủ đọc được. Thêm một thanh nhỏ nổi bật riêng đánh dấu nhóm >200,000 km với annotation số lượng.

### Màu sắc
Histogram bars: `#0F3460` (xanh đậm), highlight nhóm 0–20,000 km bằng `#00B894` (xanh lá) vì đây là nhóm lớn nhất. Đường KDE: `#E94560` (đỏ cam). Đường tham chiếu tại 30,000 km (trung vị): `#FDCB6E` (vàng đứt nét). Annotation text: `#FFFFFF`.

### Dữ liệu thực (26,722 xe đã qua sử dụng)

| Phân vị | Giá trị km |
|---|---|
| Trung vị (50%) | 30,000 km |
| Tứ phân vị dưới (25%) | 9,000 km |
| Tứ phân vị trên (75%) | 65,000 km |
| Ngưỡng 90% | 100,000 km |
| Ngưỡng 95% | 130,000 km |
| Ngưỡng 99% | 210,000 km |
| Max | 500,000 km |
| Số xe >200,000 km | 292 xe (1.1%) |

### Câu chuyện dữ liệu
Phân phối km của xe cũ Việt Nam lệch phải mạnh: phần lớn xe cũ được rao bán khi còn rất ít km. Nhóm 0–20,000 km là nhóm đông nhất trong tập xe đã qua sử dụng — tức người ta rao bán xe cũ khi xe còn gần như mới. Điều này khớp với quan sát ở Tab 4 về km trung vị theo năm sản xuất: xe mới 2–3 năm tuổi đã được rao bán ở mức 8,000–16,000 km.

Nhưng đuôi phân phối mới là điều đáng chú ý hơn: 292 xe có km >200,000 — tức 1.1% thị trường xe cũ. Trong số đó có những trường hợp đặc biệt như Toyota Land Cruiser II 1991 đã đi 370,000 km (vẫn được rao giá 465 triệu), Toyota Crown 1990 đi 370,000 km (185 triệu), và một chiếc Porsche Panamera 2014 đi 384,000 km vẫn được rao đến 2,500 triệu. Chiếc xe có km cao nhất trong tập là 500,000 km — khoảng cách bằng 12 lần đường xích đạo trái đất.

Hai câu hỏi mà biểu đồ này đặt ra: tại sao người ta bán xe sớm khi km còn rất thấp (phần phân phối bên trái), và những chiếc xe chạy 300,000–500,000 km vẫn xuất hiện trên thị trường nói lên điều gì về độ bền và thói quen bảo trì ở Việt Nam (phần đuôi phải)? Cả hai đều là "góc khuất" mà con số trung bình bình thường không thể tiết lộ.

*Annotation trong biểu đồ:*
- Đường tham chiếu vàng tại 30,000 km: *"Trung vị: 30,000 km"*
- Annotation tại vùng >200,000 km: *"292 xe — 1.1% thị trường"*
- Callout box nhỏ ngoài trục X: *"Max: 500,000 km (Xe trước 1990)"*

---

## Design Layout

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  KPI: Ferrari 54,000 tr  |  Kia Pride 18 tr  |  500,000 km max  |  ×3,000  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Horizontal Bar Chart (đôi — gương nhau)                                   │
│   Top 10 Xe Đắt Nhất           |    Top 10 Xe Rẻ Nhất                       │
│   [Rolls Royce chiếm 9/10]     |    [Kia/Daewoo/Toyota đời 90s]             │
│   [thanh màu đỏ cam]           |    [thanh màu xanh lá]                     │
│                                                                              │
├──────────────────────────────────────────┬───────────────────────────────────┤
│                                          │                                   │
│   Multi-Line Chart                       │   Bubble Chart                    │
│   Sự Trỗi Dậy và Biến Động Hãng Xe      │   Bản Đồ Định Vị Thương Hiệu     │
│   2018–2025                              │   Giá Trung Vị × Số Lượng        │
│   [annotation: Ford 2023 spike]          │   [4 vùng phân cách]              │
│   [annotation: VinFast dẫn đầu 2025]    │   [Mercedes nổi bật]              │
│                                          │                                   │
├──────────────────────────────────────────┴───────────────────────────────────┤
│                                                                              │
│   Histogram + KDE                                                            │
│   Phân Phối Km Xe Cũ (0 – 300,000 km)                                       │
│   [highlight nhóm 0–20k: đông nhất]  [annotation: 292 xe >200k]             │
│   [đường vàng tại trung vị 30,000 km]  [callout: max 500,000 km]            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

Bố cục tab này không đối xứng theo đúng nghĩa — và đó là có chủ ý. Biểu đồ đôi (gương nhau) ở phần trên chiếm toàn bộ chiều ngang để tạo ấn tượng mở đầu mạnh: sự tương phản giữa Rolls Royce 46 tỷ và Kia Pride 18 triệu. Hai biểu đồ giữa bố cục 1:1 — Line Chart và Bubble Chart — kể hai câu chuyện song song: diễn biến theo thời gian và vị thế hiện tại. Histogram ở đáy kéo dài toàn bộ chiều ngang để tối đa hóa không gian đọc phân phối km, vốn là dữ liệu có đuôi dài cần nhiều chỗ hiển thị.

Luồng đọc có chủ ý: KPI gây sốc → Biểu đồ đôi (câu hỏi về cực trị) → Line Chart (ai đang thắng theo thời gian?) → Bubble Chart (mỗi hãng thực sự đứng ở đâu?) → Histogram (người ta bán xe sau bao nhiêu km và những cái đuôi cực đoan ẩn chứa điều gì?). Năm biểu đồ, mỗi cái kể một phần câu chuyện về những thứ mà con số bình thường không nói ra được.

Toàn bộ nền Dark Theme: `#1A1A2E` cho figure, `#16213E` cho từng ô đồ thị. Annotation text `#FDCB6E` (vàng) để nổi bật trên nền tối mà không gây chói. Đường phân cách vùng trong Bubble Chart dùng `#636E72` đứt nét mờ để không cạnh tranh với dữ liệu chính.

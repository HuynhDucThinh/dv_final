# Tab 5 — Góc Khuất Thị Trường

## Mục tiêu phân tích

Tab này là phần kết thúc của câu chuyện dữ liệu. Bốn tab trước dựng lên bức tranh tổng quát — thị phần, giá cả, nhiên liệu, hành vi người mua. Tab này đi vào những góc mà bức tranh đó cố tình che lại: xe nào đắt bất thường, xe nào rẻ đến mức gây ngạc nhiên, hãng nào đang thực sự trỗi dậy hay thoái trào, và người bán xe nào đang rao những con số khiến người mua phải dừng lại đọc kỹ hơn. Đây không phải phân tích để tìm xu hướng — đây là phân tích để tìm ngoại lệ, và từ đó hiểu thêm về cách thị trường vận hành ở những phần ít được nhìn thấy nhất.

---

## KPI — Bốn tín hiệu dị thường

| Chỉ số | Giá trị | Ghi chú |
|---|---|---|
| Xe đắt nhất bị rao bán sau khi đã chạy >50,000 km | 12,980 triệu VND | Mercedes Benz G63 AMG 2021 — 129,000 km |
| Xe chạy nhiều km nhất còn được rao bán | 500,000 km | Tương đương 12 vòng quanh Trái Đất |
| Số hãng xe hiếm (≤5 xe trong toàn bộ dữ liệu) | 35 hãng / 91 hãng | 38% số hãng hầu như vô hình trên thị trường |
| Ford 2023 — đột biến bất thường | 1,081 xe (×7.7 so với 2022) | Không có lý giải rõ ràng từ dữ liệu |

Bốn con số này không phải những chỉ số tổng quát — chúng là những điểm gãy trong dữ liệu, nơi quy luật bình thường không còn áp dụng được. Một chiếc G63 AMG đã chạy 129,000 km vẫn được rao 13 tỷ đồng; 35 hãng xe xuất hiện trong dữ liệu nhưng không ai biết tên; Ford đột ngột rao 1,081 xe trong một năm rồi quay về mức 181 xe năm sau. Tab này đi tìm những điểm bất thường đó.

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

## Biểu đồ 3 — Diverging Bar Chart: Hãng Xe Nào Bán Được Cả Hai Thái Cực?

### Loại biểu đồ
Diverging bar chart nằm ngang: mỗi hãng có hai thanh xuất phát từ điểm trung tâm (giá trung vị của hãng đó), một thanh kéo sang trái thể hiện khoảng cách xuống giá thấp nhất, một thanh kéo sang phải thể hiện khoảng cách lên giá cao nhất. Điểm gốc của mỗi thanh là giá trung vị — không phải 0. Chỉ bao gồm các hãng có ≥20 xe trong dữ liệu để đảm bảo đủ đại diện.

*Lưu ý triển khai Power BI:* Dùng Custom Visual "Tornado Chart" hoặc "Grouped Bar" với hai measure [Khoảng giá xuống] và [Khoảng giá lên] tính từ median. Trong Notebook dùng `plt.barh` hai lần với dấu âm cho thanh trái.

### Màu sắc
Thanh xuống (giá thấp nhất so với median): `#0F3460` (xanh đậm). Thanh lên (giá cao nhất so với median): `#E94560` (đỏ cam). Điểm median: chấm tròn màu `#FDCB6E` (vàng). Nhãn tên hãng: `#FFFFFF`.

### Dữ liệu thực (Top 15 hãng có khoảng cách giá nội bộ lớn nhất, ≥20 xe)

| Hãng | Giá thấp nhất (tr) | Trung vị (tr) | Giá cao nhất (tr) | Khoảng cách (tr) |
|---|---|---|---|---|
| Rolls Royce | 6,900 | 18,500 | 46,000 | 39,100 |
| Bentley | 1,200 | 9,999 | 29,500 | 28,300 |
| Mercedes Benz | 49 | 1,880 | 23,300 | 23,251 |
| Maserati | 2,599 | 4,999 | 18,999 | 16,400 |
| LandRover | 650 | 3,889 | 16,941 | 16,291 |
| Porsche | 199 | 4,150 | 15,500 | 15,301 |
| Lexus | 150 | 3,190 | 14,200 | 14,050 |
| Toyota | 25 | 552 | 9,880 | 9,855 |
| Audi | 285 | 1,059 | 8,880 | 8,595 |
| BMW | 120 | 1,460 | 7,299 | 7,179 |
| Ford | 78 | 699 | 6,990 | 6,912 |
| Vinfast | 192 | 519 | 4,600 | 4,408 |
| Volvo | 1,260 | 2,274 | 4,890 | 3,630 |
| Peugeot | 405 | 870 | 4,000 | 3,595 |
| Isuzu | 95 | 590 | 3,500 | 3,405 |

### Câu chuyện dữ liệu
Biểu đồ này hỏi một câu khác với Tab 2: không phải hãng nào đắt hay rẻ, mà *hãng nào có biên độ dao động nội bộ lớn nhất* — tức cùng một thương hiệu nhưng bán được cả xe vài chục triệu lẫn xe vài tỷ. Đây là góc nhìn về độ đa dạng sản phẩm và khả năng phủ sóng phân khúc.

Mercedes Benz là trường hợp gây sốc nhất: giá thấp nhất là 49 triệu (xe đời 1990 cũ kỹ) và giá cao nhất là 23,300 triệu — biên độ 23,251 triệu. Một thương hiệu "xe sang" nhưng lại có chiếc rẻ hơn cả xe Kia mới. Cơ chế ở đây là thị trường xe cũ đời cũ: những chiếc Mercedes từ thập niên 90–2000 vẫn được rao bán với giá rất thấp, trong khi những chiếc AMG mới nhất đẩy trần lên rất cao.

Tương tự với Toyota: giá thấp nhất là 25 triệu (Toyota Cressida trước 1990), cao nhất là 9,880 triệu (Land Cruiser V8 đời mới) — biên độ gần 10 tỷ. Chỉ một thương hiệu nhưng phủ toàn bộ dải từ xe lịch sử đến SUV cao cấp.

Điểm đối lập thú vị: Vinfast có biên độ 4,408 triệu (192 đến 4,600 triệu) — tương đối hẹp so với Toyota hay Mercedes, nhưng đây lại là thương hiệu trẻ chỉ mới xuất hiện từ 2019. Biên độ hẹp phản ánh việc VinFast chưa có thị trường xe cũ đời cũ, và danh mục sản phẩm còn tập trung.

*Annotation:* Đánh dấu ba điểm đặc biệt bằng nhãn màu `#FDCB6E`: Mercedes (giá thấp nhất 49 tr), Toyota (giá thấp nhất 25 tr), Rolls Royce (giá cao nhất 46,000 tr).

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
│  KPI: G63 AMG 129k km → 13 tỷ  |  500,000 km max  |  35 hãng vô hình  |  Ford ×7.7  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Horizontal Bar Chart (đôi — gương nhau)                                   │
│   Top 10 Xe Đắt Nhất           |    Top 10 Xe Rẻ Nhất                       │
│   [Rolls Royce chiếm 9/10]     |    [Kia/Daewoo/Toyota đời 90s]             │
│   [thanh màu đỏ cam]           |    [thanh màu xanh lá]                     │
│                                                                              │
├──────────────────────────────────────────┬───────────────────────────────────┤
│                                          │                                   │
│   Multi-Line Chart                       │   Diverging Bar Chart             │
│   Sự Trỗi Dậy và Biến Động Hãng Xe      │   Biên Độ Giá Nội Bộ Theo Hãng   │
│   2018–2025                              │   [Giá thấp ← Median → Cao]       │
│   [annotation: Ford 2023 spike ×7.7]    │   [Mercedes 49 tr → 23,300 tr]    │
│   [annotation: VinFast dẫn đầu 2025]    │   [Toyota 25 tr → 9,880 tr]       │
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

Bố cục tab này không đối xứng theo đúng nghĩa — và đó là có chủ ý. Biểu đồ đôi (gương nhau) ở phần trên chiếm toàn bộ chiều ngang để tạo ấn tượng mở đầu mạnh: sự tương phản giữa Rolls Royce 46 tỷ và Kia Pride 18 triệu. Hai biểu đồ giữa bố cục 1:1 — Line Chart và Diverging Bar Chart — kể hai câu chuyện song song: diễn biến bất thường theo thời gian và biên độ dao động giá nội bộ từng hãng. Histogram ở đáy kéo dài toàn bộ chiều ngang để tối đa hóa không gian đọc phân phối km, vốn là dữ liệu có đuôi dài cần nhiều chỗ hiển thị.

Luồng đọc có chủ ý: KPI dị thường → Biểu đồ đôi (hai thái cực thị trường) → Line Chart (ai đang thắng và ai đang có đột biến?) → Diverging Bar Chart (cùng một hãng nhưng bán được bao nhiêu mức giá khác nhau?) → Histogram (người ta bán xe sau bao nhiêu km và những cái đuôi cực đoan ẩn chứa điều gì?). Năm biểu đồ, mỗi cái khai thác một khía cạnh dị thường mà bốn tab trước không đề cập.

Toàn bộ nền Dark Theme: `#1A1A2E` cho figure, `#16213E` cho từng ô đồ thị. Annotation text `#FDCB6E` (vàng) để nổi bật trên nền tối mà không gây chói. Thanh diverging dùng hai màu tương phản `#0F3460` và `#E94560` để người đọc phân biệt ngay hướng nào là "xuống đáy", hướng nào là "lên đỉnh".

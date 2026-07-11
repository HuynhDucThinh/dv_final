# Tab 5 — Góc Khuất Thị Trường

## Mục tiêu phân tích

Tab này là phần kết thúc của câu chuyện dữ liệu. Bốn tab trước dựng lên bức tranh tổng quát — thị phần, giá cả, nhiên liệu, hành vi người mua. Tab này đi vào những góc mà bức tranh đó cố tình che lại: xe nào đắt bất thường, xe nào rẻ đến mức gây ngạc nhiên, hãng nào đang thực sự trỗi dậy hay thoái trào, và cùng một thương hiệu nhưng có thể bán cả xe vài chục triệu lẫn xe vài chục tỷ. Đây không phải phân tích để tìm xu hướng — đây là phân tích để tìm ngoại lệ, và từ đó hiểu thêm về cách thị trường vận hành ở những phần ít được nhìn thấy nhất.

---

## KPI — Bốn tín hiệu dị thường

*(Đã vẽ xong trên Power BI — giữ nguyên, không thay đổi)*

| Chỉ số | Giá trị | Ghi chú |
|---|---|---|
| Xe đắt nhất bị rao bán sau khi đã chạy >50,000 km | 12,980 triệu VND | Mercedes Benz G63 AMG 2021 — 129,000 km |
| Xe chạy nhiều km nhất còn được rao bán | 500,000 km | Tương đương 12 vòng quanh Trái Đất |
| Số hãng xe hiếm (≤5 xe trong toàn bộ dữ liệu) | 33 hãng / 91 hãng | ~36% số hãng hầu như vô hình trên thị trường |
| Ford 2023 — đột biến bất thường | 1,081 xe (×7.7 so với 2022) | Không có lý giải rõ ràng từ dữ liệu |

Bốn con số này không phải những chỉ số tổng quát — chúng là những điểm gãy trong dữ liệu, nơi quy luật bình thường không còn áp dụng được. Một chiếc G63 AMG đã chạy 129,000 km vẫn được rao 13 tỷ đồng; 33 hãng xe xuất hiện trong dữ liệu nhưng không ai biết tên; Ford đột ngột rao 1,081 xe trong một năm rồi quay về mức 181 xe năm sau. Tab này đi tìm những điểm bất thường đó.

---

## Biểu đồ 1a — Horizontal Bar Chart: Top 8 Xe Rẻ Nhất

*(Đã vẽ xong trên Power BI — giữ nguyên nội dung, chỉ bổ sung câu chuyện dữ liệu)*

### Loại biểu đồ
Biểu đồ cột ngang (Horizontal Bar Chart) thể hiện 8 dòng xe rẻ nhất thị trường, sắp xếp từ rẻ nhất ở trên xuống. Trục X đo bằng tỷ VND để scale hợp lý với trục đối diện (xe đắt nhất).

### Màu sắc
Thanh màu `#00B894` (xanh lá), nhạt dần theo thứ hạng. Label giá trị màu `#FFFFFF`. Vị trí: Tầng 2, ô trái.

### Dữ liệu thực

| Tên xe | Hãng | Giá (tỷ VND) | Năm SX |
|---|---|---|---|
| Mitsubishi L300 2.0 MT | Mitsubishi | 0.021 | 2000 |
| Mitsubishi L300 2.0 MT | Mitsubishi | 0.025 | 1999 |
| Nissan Sunny EX Saloon | Nissan | 0.025 | 1992 |
| Toyota Cressida | Toyota | 0.025 | trước 1990 |
| Kia Pride Beta | Kia | 0.027 | 2002 |
| Mitsubishi Canter | Mitsubishi | 0.028 | 1993 |
| Toyota Hiace 2.4 | Toyota | 0.028 | 2002 |
| Toyota Hiace Van 2.0 | Toyota | 0.028 | 2002 |

*Ghi chú: Kia Pride Beta 1996 (18 triệu — thấp nhất tuyệt đối) không xuất hiện trong danh sách vì bản thực tế trên Power BI đã hiển thị theo thứ tự từ Mitsubishi L300 2000.*

### Câu chuyện dữ liệu
Kia Pride 1996 với 18 triệu — thấp hơn giá một chiếc điện thoại tầm trung. Đây là thế hệ xe nhỏ từ thập niên 90, nhiều chiếc vẫn đang lưu thông trên đường và xuất hiện trên nền tảng rao vặt như những hiện vật của một giai đoạn thị trường khác. Mitsubishi L300 và Toyota Hiace chiếm phần lớn danh sách này — xe tải van, minibus đời cũ từ 1990–2003, đã chạy hàng chục năm nhưng vẫn còn người mua vì nhu cầu vận chuyển hàng hóa giá thấp vẫn tồn tại.

---

## Biểu đồ 1b — Horizontal Bar Chart: Top 8 Xe Đắt Nhất

### Loại biểu đồ
Biểu đồ cột ngang (Horizontal Bar Chart) thể hiện 8 dòng xe đắt nhất thị trường, sắp xếp từ rẻ nhất ở trên xuống (tức đắt nhất ở đáy) để tạo hiệu ứng gương với Biểu đồ 1a. Trục X đo bằng tỷ VND.

*Lưu ý triển khai Power BI:* Đây là Tầng 2, ô phải — đặt cạnh Biểu đồ 1a. Hai biểu đồ nên dùng cùng chiều rộng cột để người đọc dễ so sánh trực quan. Dùng Clustered Bar hoặc Bar Chart thông thường, không cần trục X đảo chiều (khác với thiết kế "gương" kiểu diverging — vì Power BI hỗ trợ dễ hơn với hai chart riêng biệt).

### Màu sắc
Thanh màu `#E94560` (đỏ cam), nhạt dần theo thứ hạng từ dưới lên. Label giá trị màu `#FFFFFF`. Tên xe màu `#FDCB6E` (vàng) để phân biệt với nhãn số.

### Dữ liệu thực

| Tên xe | Hãng | Giá (tỷ VND) | Năm SX |
|---|---|---|---|
| Rolls Royce Ghost Series II EWB | Rolls Royce | 39.0 | 2021 |
| Rolls Royce Cullinan V12 | Rolls Royce | 39.0 | 2022 |
| Rolls Royce Cullinan 6.75 V12 | Rolls Royce | 39.9 | 2018 |
| Rolls Royce Cullinan | Rolls Royce | 39.99 | 2022 |
| Rolls Royce Ghost Series II EWB | Rolls Royce | 39.999 | 2021 |
| Rolls Royce Cullinan Black Badge 6.75 V12 | Rolls Royce | 45.0 | 2022 |
| Rolls Royce Cullinan Black Badge | Rolls Royce | 46.0 | 2021 |
| Ferrari SF90 Stradale 4.0 V8 | Ferrari | 54.0 | 2020 |

### Câu chuyện dữ liệu
Top 8 xe đắt nhất hầu như bị chiếm hoàn toàn bởi Rolls Royce — 7 trong 8 chiếc, với Ferrari SF90 Stradale là ngoại lệ duy nhất. Đây là siêu xe hybrid 1,000 mã lực, không phải xe siêu sang theo nghĩa truyền thống — sự có mặt của nó ở đỉnh bảng cho thấy hiệu suất thuần túy đôi khi còn đắt hơn cả sự sang trọng. Điều đáng chú ý hơn là sự vắng mặt hoàn toàn của Lamborghini, Bentley, hay Bugatti ở top này — những cái tên thường gắn với "đắt" trong trí tưởng tượng phổ biến nhưng thực ra vẫn thấp hơn mức ngưỡng Rolls Royce đang thiết lập tại đây.

Khi đặt hai biểu đồ cạnh nhau: một chiếc Mitsubishi L300 năm 2000 giá 21 triệu và một chiếc Rolls Royce Cullinan 46,000 triệu — chúng đều đang được rao trên cùng một trang web, trong cùng một bộ dữ liệu.

---

## Biểu đồ 2 — Multi-Line Chart: Cuộc Đua Thị Phần — Sự Trỗi Dậy và Biến Động của Các Hãng Xe (2018–2025)

### Loại biểu đồ
Line chart với nhiều đường, mỗi đường là một hãng xe lớn. Trục X: năm sản xuất (2018–2025). Trục Y: số lượng xe trong dữ liệu. Annotation dùng callout box nổi bật tại các điểm bùng nổ hoặc sụt giảm quan trọng.

*Lưu ý triển khai Power BI:* Tầng 3, ô trái. Dùng Line Chart chuẩn, mỗi hãng một màu, bật legend ở dưới để tiết kiệm chiều cao. Giới hạn 6–7 hãng lớn nhất, loại bỏ các hãng quá nhỏ để tránh rối. Thêm Text Box annotation tại điểm Ford 2023 và VinFast 2025 trực tiếp trên biểu đồ.

### Màu sắc
VinFast/Vinfast: `#E94560` (đỏ cam). Toyota: `#FDCB6E` (vàng). Hyundai: `#00B894` (xanh lá). Kia: `#A29BFE` (tím). Ford: `#74B9FF` (xanh nhạt, để nổi bật điểm spike 2023). Mazda: `#636E72` (xám). Annotation text: `#FFFFFF`.

### Dữ liệu thực (số lượng xe theo năm sản xuất)

| Năm SX | Toyota | Hyundai | Ford | Kia | Mazda | VinFast* |
|---|---|---|---|---|---|---|
| 2018 | 365 | 337 | 227 | 219 | 309 | 0 |
| 2019 | 544 | 436 | 282 | 252 | 304 | 74 |
| 2020 | 430 | 427 | 194 | 245 | 240 | 127 |
| 2021 | 343 | 336 | 181 | 282 | 153 | 185 |
| 2022 | 496 | 557 | 140 | 379 | 185 | 260 |
| 2023 | 704 | 399 | **1,081** | 167 | 207 | 148 |
| 2024 | 150 | 196 | 181 | 180 | 165 | 140 |
| 2025 | 119 | 146 | 168 | 87 | 51 | **271** |

*VinFast và Vinfast được gộp để tính tổng (do lỗi nhất quán tên trong dữ liệu thô).*

### Câu chuyện dữ liệu
Biểu đồ này chứa ít nhất ba điểm dị thường cần annotation.

Điểm thứ nhất: Ford năm 2023 đạt 1,081 xe — gấp gần 8 lần so với 2022 (140 xe). Đây là con số bất thường nhất trong toàn bộ tập dữ liệu nếu nhìn theo chiều hãng × năm. Khi xem thêm cơ cấu xe Ford 2023, phần lớn là SUV (546 xe) và bán tải/pickup (465 xe) — tức đây không phải một model duy nhất bùng nổ mà là cả dải sản phẩm được rao hàng loạt. Nguyên nhân có thể là đợt xả hàng tồn kho sau tắc nghẽn chuỗi cung ứng hậu COVID hoặc chiến dịch đại lý. Dashboard không thể trả lời dứt khoát — nhưng chính việc "không thể trả lời" đó mới là điều quan trọng cần chỉ ra.

Điểm thứ hai: VinFast (gộp cả Vinfast) đạt 271 xe năm 2025 — vượt qua tất cả các hãng truyền thống trong cùng năm (Toyota: 119, Hyundai: 146, Ford: 168). Đây là lần đầu tiên VinFast dẫn đầu về số lượng xe mới đăng ký trong năm. Kết hợp với dữ liệu từ Tab 3 (thị phần xe điện đạt 19.79% năm 2025), xu hướng này có tính nhất quán cao.

Điểm thứ ba: Toyota đạt đỉnh 544 xe năm 2019 rồi sụt liên tục đến 2021, phục hồi 2022–2023, rồi lại giảm mạnh 2024–2025 — vòng chu kỳ điển hình của thương hiệu phổ thông đang chia sẻ thị phần với nhiều đối thủ hơn, không phải đang suy tàn.

*Annotation cần có trong biểu đồ:*
- Mũi tên chỉ đỉnh Ford 2023: *"Ford 2023: 1,081 — bình thường hay đột biến?"*
- Mũi tên chỉ VinFast 2025: *"VinFast lần đầu dẫn đầu (2025)"*
- Vùng 2024–2025 có thể highlight nhẹ để phân biệt xu hướng gần đây với lịch sử.

---

## Biểu đồ 3 — Diverging Bar Chart: Hãng Xe Nào Bán Được Cả Hai Thái Cực?

### Loại biểu đồ
Diverging bar chart nằm ngang: mỗi hãng có hai thanh xuất phát từ điểm trung tâm là giá trung vị của hãng đó. Thanh trái thể hiện khoảng cách từ median xuống giá thấp nhất; thanh phải thể hiện khoảng cách từ median lên giá cao nhất. Gốc của mỗi thanh là giá trung vị, không phải 0. Chỉ bao gồm hãng có ≥20 xe trong dữ liệu.

*Lưu ý triển khai Power BI:* Tầng 3, ô phải. Dùng Custom Visual "Tornado Chart" (có sẵn trong AppSource, miễn phí) hoặc tạo Clustered Bar với hai measure tính từ median: `[Biên độ xuống] = Median - Min` và `[Biên độ lên] = Max - Median`. Trục X đo bằng tỷ VND. Giữ 10–12 hãng để tránh chật chội trong ô half-width. Sắp xếp từ biên độ lớn nhất ở trên.

### Màu sắc
Thanh trái (từ median xuống giá thấp nhất): `#0F3460` (xanh đậm). Thanh phải (từ median lên giá cao nhất): `#E94560` (đỏ cam). Điểm median: chấm tròn màu `#FDCB6E` (vàng). Nhãn tên hãng: `#FFFFFF`.

### Dữ liệu thực (Top 12 hãng có khoảng cách giá nội bộ lớn nhất, ≥20 xe)

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

### Câu chuyện dữ liệu
Biểu đồ này hỏi một câu khác với Tab 2: không phải hãng nào đắt hay rẻ, mà hãng nào có biên độ dao động nội bộ lớn nhất — tức cùng một thương hiệu nhưng bán được cả xe vài chục triệu lẫn xe vài tỷ. Đây là góc nhìn về độ đa dạng sản phẩm và khả năng phủ sóng phân khúc theo chiều dọc.

Mercedes Benz là trường hợp gây sốc nhất: giá thấp nhất là 49 triệu (xe đời 1990 cũ kỹ) và giá cao nhất là 23,300 triệu — biên độ 23,251 triệu. Một thương hiệu "xe sang" nhưng lại có chiếc rẻ hơn cả xe Kia mới. Cơ chế ở đây là thị trường xe cũ đời cũ: những chiếc Mercedes từ thập niên 90–2000 vẫn được rao bán với giá rất thấp, trong khi những chiếc AMG mới nhất đẩy trần lên rất cao.

Toyota tương tự: từ 25 triệu (Toyota Cressida trước 1990) đến 9,880 triệu (Land Cruiser V8 đời mới) — biên độ gần 10 tỷ. Chỉ một thương hiệu nhưng phủ toàn bộ dải từ xe lịch sử đến SUV cao cấp.

Điểm đối lập: Vinfast có biên độ 4,408 triệu (192 đến 4,600 triệu) — tương đối hẹp so với Toyota hay Mercedes. Đây là thương hiệu trẻ chỉ mới từ 2019, chưa có thị trường xe cũ đời cũ và danh mục sản phẩm còn tập trung. Biên độ hẹp không phải điểm yếu — nó phản ánh giai đoạn phát triển còn sớm.

*Annotation:* Đánh dấu ba điểm đặc biệt bằng nhãn màu `#FDCB6E`: Mercedes (giá thấp nhất 49 tr), Toyota (giá thấp nhất 25 tr), Rolls Royce (giá cao nhất 46,000 tr).

---

## Design Layout

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  KPI: G63 AMG 129k km → 13 tỷ  |  500,000 km max  |  33 hãng vô hình  |  Ford ×7.7 │
├──────────────────────────────────────┬───────────────────────────────────────┤
│                                      │                                       │
│   Bar Chart (nằm ngang) ✅           │   Bar Chart (nằm ngang)               │
│   Top 8 Xe Rẻ Nhất (Tỷ VND)         │   Top 8 Xe Đắt Nhất (Tỷ VND)         │
│   [màu xanh lá #00B894]              │   [màu đỏ cam #E94560]                │
│   [Mitsubishi L300 0.021 — đáy]      │   [Ferrari 54 — đỉnh]                │
│                                      │   [Rolls Royce 7/8 xe]                │
│                                      │                                       │
├──────────────────────────────────────┼───────────────────────────────────────┤
│                                      │                                       │
│   Multi-Line Chart                   │   Diverging Bar Chart                 │
│   Cuộc Đua Hãng Xe 2018–2025         │   Biên Độ Giá Nội Bộ Theo Hãng       │
│   [Ford 2023: đột biến ×7.7]         │   [Min ← Median → Max]               │
│   [VinFast dẫn đầu 2025: 271 xe]     │   [Mercedes: 49 tr → 23,300 tr]      │
│   [6 hãng, legend dưới biểu đồ]      │   [Toyota: 25 tr → 9,880 tr]         │
│                                      │                                       │
└──────────────────────────────────────┴───────────────────────────────────────┘
```

**Lý do chọn 4 biểu đồ này cho bố cục 3 tầng:**

Bốn biểu đồ tạo thành hai cặp đối xứng về mặt phân tích:

Tầng 2 là cặp tương phản trực tiếp: xe rẻ nhất vs xe đắt nhất của cùng một thị trường, đặt cạnh nhau để khoảng cách ×3,000 lần hiện ra ngay lập tức mà không cần một câu giải thích nào.

Tầng 3 là cặp tương phản theo chiều phân tích: Multi-Line Chart hỏi "ai đang thay đổi theo thời gian?" còn Diverging Bar Chart hỏi "mỗi hãng đang trải dài bao nhiêu về giá ở cùng một thời điểm?" — hai câu hỏi vuông góc nhau, cùng khai thác khía cạnh dị thường chưa có ở bốn tab trước.

Histogram km xe cũ bị loại khỏi thiết kế này vì: insight về km đã được khai thác ở Tab 4 (Area Chart km trung vị theo năm sản xuất), Histogram lệch phải cần full-width để đọc được phần đuôi dài, và không còn slot full-width nào sau khi đã giữ bố cục 2×2.

Toàn bộ nền Dark Theme: `#1A1A2E` cho figure, `#16213E` cho từng ô đồ thị. Annotation text `#FDCB6E` (vàng) để nổi bật trên nền tối. Thanh diverging dùng hai màu tương phản `#0F3460` và `#E94560` để người đọc phân biệt ngay hướng "xuống đáy" và "lên đỉnh".

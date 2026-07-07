# Quy tắc viết báo cáo và notebook

---

## Phần 1 — Báo cáo LaTeX (Report)

### 1. Trước khi viết

Đọc kĩ toàn bộ source code hiện tại trong dự án để nắm văn phong, cấu trúc, và cú pháp đang dùng. Mọi nội dung mới phải viết thống nhất với phần đã có, không được tự ý thay đổi phong cách trình bày.

---

### 2. Văn phong và giọng văn

- Viết đầy đủ, kĩ càng, chi tiết nhất có thể.
- Giọng văn phải tự nhiên như con người viết: dễ hiểu nhưng không sáo rỗng, không cứng nhắc.
- Tránh các từ ngữ màu mè kiểu AI như: *tuyệt đối, hoàn toàn, đáng kể, mạnh mẽ, vượt trội, hiệu quả cao, đặc biệt quan trọng,...*
- Học theo văn phong hiện tại trong bài hoặc cải thiện thêm nếu thấy phù hợp.

---

### 3. Các dấu hiệu AI cần tránh

Đây là những lỗi phổ biến nhất cần chú ý:

**In đậm sai chỗ.** Cấm in đậm cụm từ giữa dòng văn xuôi. Nếu cần nhấn mạnh thì dùng *in nghiêng*, không đụng đến in đậm.

**Viết hoa tùy tiện.** Cấm viết hoa bất kì từ nào giữa dòng mà không có lí do ngữ pháp rõ ràng, kể cả trong tiêu đề nếu không cần thiết.

**Viết song ngữ.** Cấm viết kiểu "thuật ngữ tiếng Anh (tiếng Việt)" hoặc "tiếng Việt (tiếng Anh)". Đây là dấu hiệu rõ nhất của văn AI. Ưu tiên dùng thuật ngữ tiếng Anh vì đã có bảng danh mục kí hiệu và thuật ngữ trong `main.tex`. Chỉ mở ngoặc giải thích khi thật sự cần thiết và không còn cách nào khác.

**Dấu gạch ngang.** Cấm dùng các kí tự `---`, `--`, `-` trong văn xuôi của báo cáo.

---

### 4. Thuật ngữ và kí hiệu

Sau mỗi lần gen nội dung, phải liệt kê riêng tất cả kí hiệu, chữ viết tắt và thuật ngữ mới xuất hiện trong đoạn vừa viết để bổ sung vào bảng danh mục trong `main.tex`. Không để thuật ngữ xuất hiện trong bài mà không có trong danh mục.

---

### 5. Hình ảnh và minh họa

- Chèn ảnh đầy đủ, đúng vị trí, trích nguồn đầy đủ theo chuẩn hiện tại đang dùng trong bài.
- Caption quá dài thì tách xuống phần ghi chú bên dưới theo cách hiện tại đang làm, không nhồi tất cả vào một dòng caption.

---

### 6. Hộp thông tin

Tham khảo và chèn các hộp InfoBox, NoteBox, WarningBox,... theo đúng cú pháp chuẩn đang định nghĩa trong bài. Phải đọc qua phần đã trình bày trước để hiểu cách dùng từng loại hộp trước khi áp dụng.

---

### 7. Bắt buộc sau mỗi lần gen nội dung

- Danh mục kí hiệu và thuật ngữ mới xuất hiện trong đoạn vừa viết.
- Danh sách tài liệu tham khảo đầy đủ, đúng chuẩn cho nội dung vừa tạo ra.

---
---

## Phần 2 — Jupyter Notebook

### 1. Trước khi viết

Đọc kĩ toàn bộ source code hiện tại trong dự án, bao gồm cả phần report lẫn các notebook đã có (nếu có), để đảm bảo nội dung mới viết ra thống nhất về cách đặt tên, cách trình bày và cấu trúc section.

---

### 2. Văn phong trong Markdown cell

Áp dụng toàn bộ quy tắc văn phong như phần report:

- Cấm in đậm giữa dòng văn xuôi, dùng *in nghiêng* nếu cần nhấn mạnh.
- Cấm viết hoa tùy tiện.
- Cấm viết song ngữ.
- Cấm dùng `---`, `--`, `-` (dấu gạch ngang) trong toàn bộ notebook.
- Tránh từ ngữ AI màu mè, sáo rỗng.

---

### 3. Cấu trúc notebook

- Mỗi section lớn phải có một Markdown cell giải thích rõ mục tiêu của phần đó trước khi bắt đầu chạy code. Không để code xuất hiện đột ngột mà không có ngữ cảnh.
- Sau mỗi biểu đồ hoặc kết quả phân tích phải có một Markdown cell nhận xét, giải thích ý nghĩa của kết quả. Không để biểu đồ trơ không có lời dẫn giải. *Cell nhận xét chỉ được viết sau khi đã có output thực tế từ việc chạy code, không được sinh sẵn nội dung nhận xét trước khi có kết quả.*
- Toàn bộ thư viện cần dùng phải được import tập trung ở cell đầu tiên của notebook. Cấm import rải rác ở giữa notebook.
- Không được để cell lỗi còn tồn tại trong notebook khi nộp bài.

---

### 4. Quy tắc viết code

- Output in ra màn hình (câu thông báo, nhãn, tiêu đề kết quả,...) phải bằng tiếng Việt.
- Comment trong code phải bằng tiếng Anh.
- Không dùng `%matplotlib inline`. Thay bằng `plt.show()` tường minh ở cuối mỗi block vẽ biểu đồ.
- Đặt tên biến bằng tiếng Anh, theo chuẩn snake_case, có nghĩa rõ ràng. Cấm dùng các tên vô nghĩa như `df1`, `df2`, `x1`, `temp`, `data2`,...

---

### 5. Biểu đồ (chart)

- Chart phải đẹp, có tiêu đề rõ ràng, màu sắc hài hòa và nhất quán xuyên suốt notebook.
- Chú thích (legend), nhãn trục (axis label) và tiêu đề không được đè lên nhau hay đè lên vùng vẽ của biểu đồ.
- Không vẽ trùng lắp thông tin: mỗi chart phải truyền đạt một góc nhìn hoặc một câu hỏi phân tích riêng biệt, không lặp lại nội dung của chart trước.
- Tên trục và tiêu đề chart phải rõ nghĩa, đúng ngữ cảnh phân tích, không để mặc định tên biến thô từ dataframe.

---

### 6. Ghi chú

Trường hợp người dùng yêu cầu sinh cell nhận xét trực tiếp khi chưa có output thực tế (bắt buộc phải sinh), agent phải ghi lại thông tin vào mục này để tiện theo dõi và chỉnh sửa sau:

| Thời điểm | File notebook | Cell | Lí do sinh trực tiếp | Cần kiểm tra lại |
|---|---|---|---|---|
| *(ví dụ: 2026-06-11)* | *(tên file .ipynb)* | *(tên/vị trí cell)* | *(người dùng yêu cầu)* | Có |

Quy tắc ghi chú:

- Ghi rõ tên file notebook và vị trí cell (tên section hoặc số thứ tự cell).
- Ghi rõ nội dung cell đã sinh và lí do phải sinh trực tiếp.
- Đánh dấu "Cần kiểm tra lại" để sau khi có output thực tế thì quay lại cập nhật nội dung cho chính xác.

---
---

## Phần 3 — Quy tắc sử dụng mô hình học máy (Machine Learning)

Phần này áp dụng khi đồ án có sử dụng mô hình học máy để hỗ trợ phân tích dữ liệu.

### 1. Lựa chọn mô hình

Việc chọn mô hình không được làm tùy tiện. Phải giải thích rõ lí do lựa chọn dựa trên đặc điểm của dữ liệu: kiểu dữ liệu (phân loại hay liên tục), phân phối, kích thước tập dữ liệu, và mục tiêu phân tích. Không được đưa dữ liệu vào chạy mà không có lập luận rõ ràng về tính phù hợp của mô hình với bài toán.

### 2. Đánh giá mô hình

Không được dựa vào accuracy đơn thuần để kết luận mô hình tốt. Phải chọn metric phù hợp với bài toán và giải thích rõ lí do lựa chọn metric đó. Ví dụ: với bài toán mất cân bằng nhãn thì precision, recall, F1-score hoặc AUC sẽ phù hợp hơn accuracy; với bài toán hồi quy thì RMSE hay MAE cần được giải thích tại sao chọn cái này thay vì cái kia.

### 3. Giải thích cơ chế hoạt động

Khi trình bày một mô hình cụ thể trong báo cáo, phải giải thích được cơ chế hoạt động của nó theo cách liên hệ với dữ liệu đang dùng. Ví dụ: với Decision Tree thì phải giải thích được cách thuật toán chia nhánh, tiêu chí chia (Gini hay entropy), và tại sao cây ra quyết định theo hướng đó. Không được chỉ đặt tên mô hình rồi báo kết quả.

### 4. Tinh chỉnh siêu tham số

Bắt buộc phải thể hiện quá trình thay đổi và đánh giá ít nhất một siêu tham số của mô hình (hyperparameter tuning). Phân tích sự thay đổi kết quả khi điều chỉnh tham số đó để chứng minh nhóm hiểu rõ mô hình, không phải chỉ chạy với giá trị mặc định.

---
---

## Phần 4 — Nguyên tắc thiết kế trực quan hóa dữ liệu (Visualization Design)

### 1. Chọn đúng biểu đồ

Việc chọn loại biểu đồ phù hợp với tính chất của dữ liệu là yêu cầu cốt lõi, ảnh hưởng trực tiếp đến điểm phân tích. Không được chọn biểu đồ theo cảm tính. Phải lập luận được tại sao dùng bar chart thay vì line chart, hay tại sao scatter plot phù hợp hơn heatmap cho câu hỏi phân tích cụ thể đó.

### 2. Dashboard phải có tính tương tác

Dashboard không được là tập hợp hình ảnh tĩnh cắt ghép lại. Phải sử dụng filter và slicer để người dùng có thể tương tác, lọc và khám phá dữ liệu theo các chiều khác nhau. Dashboard phải thiết kế như một storyboard dẫn dắt người đọc từ tổng quan đến chi tiết.

### 3. Không nhồi nhét thông tin

Mỗi dashboard hoặc trang báo cáo chỉ tập trung vào một chủ đề phân tích. Thông tin cần được chắt lọc, làm nổi bật đối tượng muốn nhấn mạnh thông qua màu sắc, và làm mờ hoặc lược bỏ các chi tiết phụ không liên quan đến câu hỏi phân tích chính.

### 4. Loại bỏ các yếu tố thừa

Cần xóa hoặc ẩn: đường lưới không cần thiết, viền thừa, chú thích tách rời xa biểu đồ. Chú giải (legend) nên được đặt sát vào đường biểu diễn hoặc thanh dữ liệu, không để người đọc phải dò mắt sang góc khác. Màu sắc phải nhất quán xuyên suốt toàn bộ dashboard.

### 5. Biểu đồ có nhiều đường hoặc danh mục

Khi dữ liệu có nhiều nhóm hoặc chuỗi thời gian chồng chéo, phải tách thành các chart con theo từng danh mục thay vì nhồi tất cả vào một biểu đồ duy nhất. Ưu tiên đọc được xu hướng rõ ràng hơn là thể hiện được nhiều thông tin trong một chỗ.

### 6. Xử lý dữ liệu thiếu (missing data)

Không được lờ đi dữ liệu thiếu. Phải chủ động xử lý (điền giá trị, loại bỏ hợp lí) hoặc báo cáo minh bạch giới hạn của dữ liệu trong phần trình bày. Biểu đồ vẽ từ dữ liệu có missing values chưa được xử lý mà không ghi chú là lỗi phân tích nghiêm trọng.

### 7. Trực quan hóa để kiểm chứng giả định

Các chỉ số thống kê như trung bình hay phương sai có thể giống nhau trên nhiều tập dữ liệu có bản chất hoàn toàn khác nhau (xem bộ dữ liệu Anscombe). Vì vậy, bắt buộc phải vẽ biểu đồ để quan sát phân phối thực tế của dữ liệu trước khi đưa ra bất kì kết luận thống kê nào. Không được kết luận chỉ dựa trên con số.

---
---

## Phần 5 — Kỹ năng báo cáo và giao tiếp dữ liệu

### 1. Báo cáo phải kể một câu chuyện

Báo cáo không phải là danh sách biểu đồ được liệt kê lần lượt. Phải có mục tiêu phân tích rõ ràng từ đầu, sau đó dẫn dắt người đọc từ tổng quan đến chi tiết theo một luồng logic nhất quán. Mỗi phần phân tích phải trả lời đúng câu hỏi đã đặt ra ở phần giới thiệu bài toán.

### 2. Tránh từ ngữ chung chung không có căn cứ

Không được dùng các nhận định chung chung không được chứng minh bằng dữ liệu, ví dụ như "nhóm này có xu hướng cao hơn" mà không kèm con số cụ thể, hoặc gộp nhóm dữ liệu theo tiêu chí địa lí (Bắc Mỹ, Nam Á,...) mà không có định nghĩa rõ ràng về cách phân nhóm đó trong dữ liệu.

### 3. Thiết kế phù hợp với đối tượng người đọc

Biểu đồ và cách trình bày phải phù hợp với đối tượng mục tiêu của báo cáo. Độ phức tạp của thuật ngữ kỹ thuật, mức độ chi tiết của số liệu và cách giải thích biểu đồ phải được điều chỉnh tương ứng với người đọc là ai (nhà quản lí, kỹ sư, hay người dùng phổ thông).

### 4. Nhận xét biểu đồ phải cụ thể

Sau mỗi biểu đồ, phần nhận xét phải chỉ ra được con số cụ thể, xu hướng rõ ràng, hoặc sự khác biệt đáng chú ý từ biểu đồ. Không được viết nhận xét theo kiểu mô tả lại hình dạng biểu đồ mà không có lời giải thích ý nghĩa thực sự đằng sau con số đó.

# Đồ Án Cuối Kỳ — Phân Tích & Trực Quan Hóa Thị Trường Ô Tô Việt Nam

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-Dashboard-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Next.js](https://img.shields.io/badge/Next.js-Web_AI-black?style=for-the-badge&logo=nextdotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge)

> **Đồ án cuối kỳ — Môn Trực quan hóa Dữ liệu (Data Visualization)**
>
> _Khoa Công nghệ Thông tin · Trường Đại học Khoa học Tự nhiên · ĐHQG-HCM · Tháng 7/2026_

---

## Mục lục

- [1. Thông tin nhóm](#1-thông-tin-nhóm)
- [2. Bài toán phân tích chung](#2-bài-toán-phân-tích-chung)
- [3. Mục tiêu phân tích từng thành viên](#3-mục-tiêu-phân-tích-từng-thành-viên)
- [4. Nguồn dữ liệu & Tiền xử lý](#4-nguồn-dữ-liệu--tiền-xử-lý)
- [5. Mô hình dữ liệu (Star Schema)](#5-mô-hình-dữ-liệu-star-schema)
- [6. Web AI — VietCar Chatbot](#6-web-ai--vietcar-chatbot)
- [7. Scraping Agent](#7-scraping-agent)
- [8. Cấu trúc dự án](#8-cấu-trúc-dự-án)
- [9. Hướng dẫn cài đặt & chạy](#9-hướng-dẫn-cài-đặt--chạy)
- [10. Kết luận chính](#10-kết-luận-chính)

---

## 1. Thông tin nhóm

| STT | Họ và tên          | Nhiệm vụ chính                                                                                       |
| :-: | :----------------- | :--------------------------------------------------------------------------------------------------- |
|  1  | Cao Tiến Thành     | EDA & Thiết kế Tab 1 (Bức tranh thị trường)                                                         |
|  2  | Phạm Ngọc Thanh    | Thiết kế Tab 2 (Giải mã giá xe)                                                                      |
|  3  | Huỳnh Đức Thịnh    | Thu thập dữ liệu (Scraping Agent) & Thiết kế Tab 3 (Cuộc chiến Xăng vs Điện) & Xây dựng Web AI     |
|  4  | Nguyễn Nhựt Thanh  | Tiền xử lý dữ liệu & Thiết kế Tab 4 (Chân dung người mua)                                          |
|  5  | Lê Hà Thanh Chương | Thiết kế Tab 5 (Góc khuất thị trường)                                                               |

> **Giảng viên hướng dẫn:** CN. Trần Huy Bân · CN. Võ Nhật Tân

---

## 2. Bài toán phân tích chung

> _"Thị trường ô tô Việt Nam đang vận động theo quy luật nào — và người mua xe thông minh cần biết gì trước khi xuống tiền?"_

Sử dụng **33.848 tin đăng xe ô tô** thu thập từ Bonbanh.com (2015–2025), dự án xây dựng hệ thống dashboard tương tác trên Power BI và Web AI chatbot nhằm trả lời câu hỏi trung tâm qua 5 khía cạnh:

1. Bức tranh tổng quan: hãng xe, phân khúc và giá trị thị trường
2. Quy luật định giá: yếu tố nào quyết định giá xe?
3. Cuộc chiến Xăng vs Điện: xu hướng đang thay đổi ra sao?
4. Chân dung người mua: thị hiếu và hành vi lựa chọn
5. Góc khuất thị trường: những điều ẩn sau số liệu

---

## 3. Mục tiêu phân tích từng thành viên

### Tab 1: Bức tranh thị trường ô tô Việt Nam (Cao Tiến Thành)

**Mục tiêu:** Phác họa toàn cảnh thị trường — hãng xe, phân khúc, phân bố giá và tình trạng nguồn gốc xe.

**KPI tổng quan:** 33.848 tin đăng · 91 hãng xe · Giá trung vị 638 triệu VNĐ · Đời xe phổ biến nhất: 2023

| Câu hỏi | Nội dung |
| :------ | :------- |
| CQ1 | Hãng xe nào chiếm tỷ trọng lớn nhất và cán cân thương hiệu Hàn–Nhật–Đức đang ở đâu? |
| CQ2 | Phân khúc xe nào (SUV, Sedan, Crossover…) đang dẫn dắt thị trường thứ cấp? |

**Phát hiện chính:** Toyota dẫn đầu với 5.861 tin (17,3%), SUV chiếm 36,3% — 2 dòng xe này cộng lại nắm giữ hơn một nửa thị phần. Xe cũ đã qua sử dụng chiếm 79,7%, xe lắp ráp trong nước chiếm 58%.

---

### Tab 2: Giải mã giá xe (Phạm Ngọc Thanh)

**Mục tiêu:** Xác định quy luật định giá — yếu tố nào tác động mạnh nhất đến giá xe?

**KPI tổng quan:** Giá trung vị 638 triệu · Giá trung bình 1.201 triệu · Rẻ nhất 18 triệu · Đắt nhất 54 tỷ

| Câu hỏi | Nội dung |
| :------ | :------- |
| CQ3 | Giá xe phân bố như thế nào theo hãng và theo phân khúc giá? |
| CQ4 | Độ khấu hao giá theo năm sản xuất và số km đã đi diễn ra theo quy luật nào? |

**Phát hiện chính:** Phân khúc 500 triệu–1 tỷ chiếm ~40% thị trường. Khoảng cách giữa giá trung vị (638 triệu) và trung bình (1.201 triệu) phản ánh ảnh hưởng mạnh của nhóm xe siêu sang đến thống kê.

---

### Tab 3: Cuộc chiến Xăng vs Điện (Huỳnh Đức Thịnh)

**Mục tiêu:** Đo lường tốc độ tăng trưởng xe điện và kiểm chứng các định kiến phổ biến về giá và hành vi người dùng.

**KPI tổng quan:** 768 xe điện · Thị phần 2025: 19,79% · VinFast chiếm 89% xe điện

| Câu hỏi | Nội dung |
| :------ | :------- |
| CQ5 | Xe điện chỉ chiếm 2,3% toàn bộ dữ liệu — tại sao gọi đây là "cuộc bứt phá", và điều gì đang âm thầm xảy ra song song? |
| CQ6 | Quan niệm phổ biến rằng xe điện đắt hơn và được giữ dùng lâu dài — dữ liệu thực tế có xác nhận điều này không? |

**Phát hiện chính:**
- Xe điện tăng từ 5 xe (2020) lên 272 xe (2025) — thị phần từ 0,21% lên 19,79%.
- Hybrid âm thầm tăng từ 1,7% lên 11,3% — làn sóng ít ai chú ý.
- Xe điện **rẻ hơn** xe xăng cùng phân khúc từ 13–28% (Hatchback: 239 tr vs 329 tr).
- 44,3% xe điện đăng bán là xe mới — gấp đôi xe xăng (20,8%) — người dùng bán lại sớm và ít km.

---

### Tab 4: Chân dung người mua (Nguyễn Nhựt Thanh)

**Mục tiêu:** Phân tích thị hiếu lựa chọn cấu hình xe và hành vi sử dụng xe của người tiêu dùng Việt Nam.

**KPI tổng quan:** Chọn màu trắng: 33,62% · Chọn số tự động: 82,05% · Chọn xe 5 chỗ: 68,82%

| Câu hỏi | Nội dung |
| :------ | :------- |
| CQ7 | Thị trường ô tô ngày càng đa dạng nhưng người mua Việt lại ngày càng giống nhau trong lựa chọn — đâu là lý do đằng sau sự đồng nhất bất thường này? |
| CQ8 | Điều gì xảy ra khi một thế hệ người mua đồng loạt chuyển sang số tự động và cũng đồng loạt bán xe sớm hơn? |

**Phát hiện chính:** Màu trắng và đen chiếm hơn 55% — phản ánh tâm lý ưu tiên giá trị bán lại. Số tự động tăng liên tục từ 2016 đến 2023, số sàn gần như biến mất ở dòng xe mới. Xe điện cũ khi bán lại chỉ đi ~16.000 km, so với 30.000 km của xe xăng.

---

### Tab 5: Góc khuất thị trường (Lê Hà Thanh Chương)

**Mục tiêu:** Phát hiện những điều bất thường và nghịch lý ẩn sau bộ dữ liệu.

**KPI tổng quan:** Xe chạy nhiều km nhất: 500.000 km · 33 hãng siêu hiếm · Chênh lệch giá Ferrari: 40,5 tỷ

| Câu hỏi | Nội dung |
| :------ | :------- |
| CQ9 | Phân khúc siêu sang có đặc điểm giao dịch nào khác biệt so với xe phổ thông? |
| CQ10 | Có những outlier dữ liệu nào có thể làm lệch kết quả phân tích nếu không xử lý đúng cách? |

---

## 4. Nguồn dữ liệu & Tiền xử lý

### Nguồn dữ liệu

- **Nền tảng:** Bonbanh.com — sàn giao dịch xe ô tô lớn nhất Việt Nam
- **Quy mô:** 33.848 tin đăng · 30 cột thông tin · Giai đoạn 2015–2025
- **Thu thập:** Tự động bằng Scraping Agent tự xây dựng (xem [Mục 7](#7-scraping-agent))

### Quy trình tiền xử lý (3 notebooks)

**Notebook 01 — Khám phá dữ liệu thô (`01_data_overview.ipynb`) — Huỳnh Đức Thịnh**
- Đọc 33.848 dòng × 30 cột, kiểm tra kiểu dữ liệu và tỷ lệ missing values.
- Phát hiện các cột số bị lưu dưới dạng chuỗi (giá: "500 triệu", km: "50.000 km").

**Notebook 02 — Tiền xử lý (`02_preprocessing.ipynb`) — Nguyễn Nhựt Thanh**
- Ép kiểu và chuẩn hóa: Giá (triệu VNĐ), Số km, Năm sản xuất.
- Lọc outlier: km ảo (> 999.999 km), giá bất hợp lý.
- Chuẩn hóa 802 biến thể loại nhiên liệu về 4 nhóm: Xăng, Dầu, Điện, Hybrid.
- Xuất `car_detail_processed.csv` (UTF-8 BOM, tương thích Power BI).

**Notebook 03 — EDA (`03_eda.ipynb`) — Cao Tiến Thành**
- Phân tích tương quan giữa Giá, Năm SX, Hãng và Loại nhiên liệu.
- Xuất `Dashboard.json` — nguồn dữ liệu cho Web AI chatbot.

---

## 5. Mô hình dữ liệu (Star Schema)

Bảng trung tâm `fact_car_listings` (33.848 dòng, khóa chính `id_tin_đăng`) liên kết với 8 bảng chiều qua quan hệ một-nhiều, chuẩn hóa 3NF.

| Bảng Dimension       | Mô tả                                           |
| :------------------- | :---------------------------------------------- |
| `dim_hang_xe`        | Hãng xe và nhóm thương hiệu                     |
| `dim_dong_xe`        | Kiểu dáng thân xe (SUV, Sedan, Crossover…)      |
| `dim_nhien_lieu`     | Loại nhiên liệu (Xăng, Dầu, Điện, Hybrid)      |
| `dim_hop_so`         | Hộp số (Tự động / Số sàn)                       |
| `dim_xuat_xu`        | Xuất xứ (Trong nước / Nhập khẩu)                |
| `dim_tinh_trang`     | Tình trạng xe (Mới / Cũ)                        |
| `dim_mau_sac`        | Màu ngoại thất                                  |
| `dim_so_cho_ngoi`    | Số chỗ ngồi                                     |

---

## 6. Web AI — VietCar Chatbot

**VietCar AI** là chatbot thông minh được xây dựng trên nền **Next.js + FastAPI**, tích hợp LLM để trả lời câu hỏi phân tích dữ liệu ô tô theo thời gian thực.

### 6.1 Kiến trúc 3 tầng trả lời

Hệ thống định tuyến câu hỏi qua 3 tầng theo thứ tự ưu tiên:

| Tầng | Tên | Tốc độ | Cơ chế | Loại câu hỏi |
| :--: | :-- | :-----: | :----- | :----------- |
| 1 | **Pre-warmed Cache** | ~0ms | Nội dung 5 tab được load sẵn vào RAM khi server khởi động | "Tab 3 cho thấy gì?" |
| 2 | **Auto Pandas Query** | ~1–2s | Tự động sinh và chạy code pandas trên DataFrame 33.848 dòng | "Tỷ lệ nhiên liệu xăng dầu điện?" |
| 3 | **Full LLM + Context** | ~5–10s | Gọi LLM (Groq/OpenAI/Google) với full system prompt + Dashboard.json + CSV schema | "Ngân sách 500 triệu mua xe điện nào?" |

### 6.2 Tính năng nổi bật

#### Sinh & thực thi code Python (Code Sandbox)
- AI tự động sinh code pandas/matplotlib phù hợp với câu hỏi phân tích.
- Code hiển thị dạng block với nút **▶ Thực thi** — người dùng xem trước rồi mới chạy.
- Kết quả trả về ngay trong cửa sổ chat: bảng Markdown + biểu đồ PNG (base64).
- Namespace Python được giữ nguyên trong suốt phiên — không cần load lại `df` mỗi lần.

#### Agent CRUD File với Approval Workflow (Human-in-the-Loop)
AI có khả năng tạo, sửa, xóa, đổi tên file trong project — nhưng **không tự ý thực thi**. Mọi thao tác phải qua modal xác nhận:

| Thao tác | Risk Level | Hành vi |
| :------- | :--------: | :------ |
| Đọc file | LOW | Tự động thực hiện |
| Tạo file mới | MEDIUM | Hiện modal → user Approve |
| Sửa file | HIGH | Hiện modal + diff trước/sau → user Approve |
| Xóa file | CRITICAL | Hiện modal cảnh báo → user Approve |
| Hoàn tác | — | Rollback về bản backup tự động |

**Thư mục được phép truy cập:** `data/`, `report/`, `ML/`, `docs/`, `notebook/`

#### Multi-provider LLM
Hỗ trợ chuyển đổi linh hoạt giữa các nhà cung cấp:

| Provider | Model | Đặc điểm |
| :------- | :---- | :-------- |
| Groq | llama-3.3-70b-versatile | Nhanh, miễn phí tier |
| OpenAI | gpt-4o-mini, gpt-4o | Chất lượng cao |
| Google | gemini-2.0-flash-lite | Cân bằng tốc độ/chất lượng |
| Ollama | llama3.2, qwen2.5 | Chạy local, không cần API key |

#### Scraping Agent tích hợp trong Chat
- Gõ URL xe bất kỳ → AI gọi `scrape_car_data(url=...)` → trả về JSON thông tin xe ngay trong chat.

#### Public API (cho ứng dụng bên ngoài)
- Endpoint JSON đồng bộ — dễ tích hợp với Power BI, Excel, n8n, Python script.

### 6.3 Hướng dẫn sử dụng Web AI

#### Khởi động

```bash
# Terminal 1 — Backend
cd web/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Frontend
cd web/frontend
npm run dev
```

Truy cập: **http://localhost:3000**

#### Các câu hỏi mẫu theo từng tính năng

**Tầng 1 — Xem Dashboard nhanh:**
```
Tab 1 thị trường ô tô cho thấy gì?
Tab 3 xe xăng và xe điện cho thấy gì?
```

**Tầng 2 — Thống kê thực tế từ CSV:**
```
Tỷ lệ phân bố các loại nhiên liệu xăng dầu điện?
Top 10 hãng xe có nhiều tin đăng nhất?
Giá trung bình xe Toyota so với Hyundai?
```

**Tầng 3 — Phân tích sâu, tư vấn:**
```
Ngân sách 500 triệu muốn mua xe điện, nên chọn hãng nào?
Tại sao xe điện lại rẻ hơn xe xăng trong khi nhiều người nghĩ ngược lại?
```

**Sinh biểu đồ:**
```
Vẽ biểu đồ so sánh giá xe điện và xe xăng theo dòng xe SUV, Crossover, Hatchback
Vẽ pie chart phân bố loại nhiên liệu trên thị trường
```

**CRUD File:**
```
Tạo file report/ket_luan.md với nội dung tóm tắt Tab 3
Sửa file report/ket_luan.md, thêm dòng kết luận về Hybrid
Chạy file report/test_chart.py
Hoàn tác thay đổi vừa rồi trong report/ket_luan.md
```

**Scraping:**
```
Thu thập thông tin xe tại https://bonbanh.com/xe-vinfast-vf8-...
```

**Public API:**
```bash
# Health check
curl http://localhost:8000/api/public/health

# Hỏi AI
curl -X POST http://localhost:8000/api/public/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Toyota co bao nhieu xe?\", \"model\": \"llama-3.3-70b-versatile\"}"
```

**Swagger UI:** http://localhost:8000/docs

---

## 7. Scraping Agent

Agent thu thập dữ liệu tự động từ các sàn ô tô trực tuyến, thiết kế 2 tầng:

| Tầng | Phương pháp | Tốc độ | Áp dụng cho |
| :--: | :---------- | :-----: | :---------- |
| 1 | **Direct Scraper** (BeautifulSoup) | Rất nhanh | bonbanh.com, oto.com.vn |
| 2 | **LLM Browser Agent** (browser-use) | Chậm hơn | Bất kỳ trang web nào |

### Sử dụng

```bash
cd scraping_agent

# Thu thập thông tin 1 xe từ bonbanh.com
python main.py "https://bonbanh.com/xe-toyota-camry-2023-..."

# Thu thập và lưu ra file JSON
python main.py "https://oto.com.vn/..." --output xe_info.json

# Dùng LLM provider cụ thể cho trang web lạ
python main.py "https://caranddriver.com/..." --llm groq

# Chạy ẩn (không hiện cửa sổ trình duyệt)
python main.py "https://..." --headless
```

### Cấu hình `.env`

```env
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
```

---

## 8. Cấu trúc dự án

```text
DV_Final/
├── data/
│   ├── raw/
│   │   └── fact_car_listings.csv    # Fact table gốc từ scraping (Star Schema)
│   └── processed/
│       ├── car_detail_processed.csv  # 33.848 dòng — bảng chính đã làm sạch
│       └── dim_*.csv                 # 8 bảng Dimension
├── docs/
│   └── Dashboard.json                # Insights dashboard — nguồn dữ liệu cho AI
├── notebook/
│   ├── 01_data_overview.ipynb
│   ├── 02_preprocessing.ipynb
│   └── 03_eda.ipynb
├── report/                           # Báo cáo LaTeX & biểu đồ
├── scraping_agent/
│   ├── main.py                       # CLI entry point
│   ├── scraper/
│   │   ├── dispatcher.py             # Điều phối URL → đúng scraper
│   │   ├── direct/                   # bonbanh.py, oto.py
│   │   └── agent.py                  # LLM browser agent
│   └── requirements.txt
└── web/
    ├── frontend/                     # Next.js — Chat UI
    │   ├── app/
    │   ├── components/chat/          # ChatInterface, ChatMessage, Sidebar...
    │   └── hooks/
    └── backend/                      # FastAPI
        └── app/
            ├── main.py               # App factory
            ├── api/
            │   ├── analysis_chat.py  # AI phân tích streaming (3 tầng)
            │   ├── execute.py        # Python code sandbox
            │   ├── file_operations.py # CRUD + Approval workflow
            │   └── public_api.py     # Public JSON API
            └── services/
                ├── data_context.py   # Inject Dashboard.json + CSV schema
                ├── file_manager.py   # File CRUD operations
                └── approval_workflow.py # Human-in-the-loop
```

---

## 9. Hướng dẫn cài đặt & chạy

### Yêu cầu hệ thống

- Python 3.10+
- Node.js 18+
- PostgreSQL (tùy chọn — dùng cho chat session storage)

### Cài đặt Backend

```bash
cd web/backend
pip install -r requirements.txt

# Cấu hình biến môi trường
cp web/.env.example web/.env
# Điền GROQ_API_KEY / OPENAI_API_KEY / GOOGLE_API_KEY vào .env

# Khởi động
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Cài đặt Frontend

```bash
cd web/frontend
npm install
npm run dev
```

### Cài đặt Scraping Agent

```bash
cd scraping_agent
pip install -r requirements.txt

# Cấu hình
cp .env .env.local
# Điền API keys
```

### Xem Dashboard Power BI

1. Cài đặt **Power BI Desktop** (phiên bản mới nhất).
2. Mở file `.pbix` trong thư mục `docs/`.
3. Nếu yêu cầu cập nhật nguồn dữ liệu, trỏ lại đường dẫn đến `data/processed/`.

---

## 10. Kết luận chính

**Câu trả lời cho câu hỏi trung tâm:** Thị trường ô tô Việt Nam đang trong giai đoạn chuyển đổi cơ cấu — xe điện tăng trưởng bùng nổ nhờ chiến lược giá thâm nhập, Hybrid lặng lẽ chiếm lĩnh, trong khi thị hiếu người mua hội tụ mạnh về nhóm xe thực dụng.

**Các phát hiện chính:**

- **Tab 1 (Thị trường):** Toyota chiếm 17,3% với 5.861 tin. SUV + Sedan kiểm soát 68% thị phần. 79,7% xe trên thị trường là xe cũ đã qua sử dụng.
- **Tab 2 (Giá xe):** Giá trung vị 638 triệu, nhưng trung bình bị kéo lên 1.201 triệu do nhóm siêu sang. Phân khúc 500 triệu–1 tỷ chiếm 40% thị trường.
- **Tab 3 (Xăng vs Điện):** Xe điện tăng từ 0,21% (2020) lên 19,79% (2025). Xe điện **rẻ hơn xe xăng 28%** ở phân khúc Hatchback. Hybrid âm thầm tăng từ 1,7% lên 11,3%.
- **Tab 4 (Người mua):** 82% chọn số tự động, 68,8% chọn xe 5 chỗ, 33,6% chọn màu trắng — phản ánh tâm lý thực dụng ưu tiên thanh khoản khi bán lại.
- **Tab 5 (Góc khuất):** Xe điện cũ chỉ đi ~16.000 km khi bán lại so với 30.000 km của xe xăng — vòng đời mua-bán nhanh tạo ra thị trường thứ cấp xe điện giá rẻ.

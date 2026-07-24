import json
import logging
import os
import asyncio
import hashlib
import json
import time
import uuid as _uuid
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.auth_deps import get_current_user_id
from app.services.data_context import build_data_context_card, get_data_file_path

router = APIRouter(prefix="/api/analysis", tags=["AI Analysis"])
logger = logging.getLogger(__name__)

# ─── Cache Dashboard.json ở module level (đọc 1 lần lúc import) ───────────────
_DASHBOARD_CACHE: dict | None = None

# ── LLM Response Cache (RAM) ──────────────────────────────────────────────────
# Key: sha256(user_content + model_name), Value: (response_text, timestamp)
# TTL: 1800s (30 phút) — data tĩnh, câu hỏi lặp lại stream ngay từ cache
_LLM_RESPONSE_CACHE: dict[str, tuple[str, float]] = {}
_RESPONSE_CACHE_TTL = 1800  # 30 phút


def _get_response_cache_key(user_content: str, model: str) -> str:
    """Tạo cache key từ nội dung câu hỏi + model name."""
    normalized = " ".join(user_content.lower().split())
    return hashlib.sha256(f"{model}::{normalized}".encode()).hexdigest()[:16]


def _get_cached_response(key: str) -> str | None:
    """Lấy response từ cache nếu còn hợp lệ (chưa hết TTL)."""
    if key in _LLM_RESPONSE_CACHE:
        text, ts = _LLM_RESPONSE_CACHE[key]
        if time.time() - ts < _RESPONSE_CACHE_TTL:
            return text
        else:
            del _LLM_RESPONSE_CACHE[key]
    return None


def _set_response_cache(key: str, text: str) -> None:
    """Lưu response vào cache. Giới hạn 200 entries để tránh OOM."""
    if len(_LLM_RESPONSE_CACHE) >= 200:
        # Xoá entry cũ nhất
        oldest_key = min(_LLM_RESPONSE_CACHE, key=lambda k: _LLM_RESPONSE_CACHE[k][1])
        del _LLM_RESPONSE_CACHE[oldest_key]
    _LLM_RESPONSE_CACHE[key] = (text, time.time())


# ── Topic Pre-Warmed Cache (RAM Memory 0ms TTFT) ────────────────────────────
_TAB_PREWARMED_CACHE: dict[str, str] = {
    "Tab1": """## 📊 TAB 1 — BỨC TRANH THỊ TRƯỜNG Ô TÔ VIỆT NAM

- **Tổng số tin đăng:** **33,848 xe ô tô** được thu thập từ Bonbanh.com.
- **Top 6 hãng xe hàng đầu:**
  1. **Toyota:** 5,861 tin đăng (Tổng giá trị: 9,872 tỷ VNĐ)
  2. **Hyundai:** 3,897 tin đăng (Tổng giá trị: 6,690 tỷ VNĐ)
  3. **Ford:** 3,719 tin đăng (Tổng giá trị: 6,043 tỷ VNĐ)
  4. **Mercedes-Benz:** 3,376 tin đăng (Tổng giá trị: 5,168 tỷ VNĐ)
  5. **Kia:** 3,258 tin đăng (Tổng giá trị: 5,928 tỷ VNĐ)
  6. **Mazda:** 2,447 tin đăng (Tổng giá trị: 4,328 tỷ VNĐ)

- **Phân bố Kiểu dáng:**
  - **SUV:** 12,289 tin đăng (Chiếm ưu thế tuyệt đối)
  - **Sedan:** 10,777 tin đăng (Phổ biến thứ 2)
  - **Crossover & Hatchback:** Chiếm tổng cộng hơn 6,000 tin đăng.

- **Nguồn gốc & Tình trạng:**
  - **Xe cũ (Đã qua sử dụng):** 26,982 xe (79.7%)
  - **Xe mới (100%):** 6,866 xe (20.3%)
  - **Lắp ráp trong nước:** 19,645 xe (58%)
  - **Nhập khẩu:** 14,203 xe (42%)

<suggestions>Cho tôi xem Tab 2 - Giải mã giá xe?|So sánh xe Xăng vs Xe Điện?|Chân dung người mua xe Việt?</suggestions>""",

    "Tab2": """## 💰 TAB 2 — GIẢI MÃ GIÁ XE Ô TÔ VIỆT NAM

- **Mức giá trung bình (Median):** **638 triệu VNĐ** (Phù hợp thu nhập đa số gia đình Việt).
- **Mức giá trung bình (Mean):** **1,201 triệu VNĐ** (Do bị ảnh hưởng bởi nhóm xe siêu sang).
- **Khoảng giá rộng:**
  - **Rẻ nhất:** 18 triệu VNĐ (Kia Pride Beta 1996)
  - **Đắt nhất:** 54 tỷ VNĐ (Ferrari SF90 Stradale 2020)

- **Phân bố theo khúc giá:**
  - **Dưới 500 triệu:** Chiếm ~35% thị trường (Xe đô thị hạng A, B).
  - **500 triệu - 1 tỷ:** Chiếm ~40% thị trường (Sedan C, SUV B/C).
  - **Trên 1 tỷ:** Chiếm ~25% (SUV cỡ D, xe hạng sang).

<suggestions>So sánh giá xe Toyota vs Hyundai?|Xe điện có đắt hơn xe xăng không?|Góc khuất thị trường giá xe?</suggestions>""",

    "Tab3": """## ⚡ TAB 3 — CUỘC CHIẾN XĂNG VS ĐIỆN

- **Cơ cấu loại nhiên liệu:**
  1. **Xe Xăng:** 26,672 tin đăng (**78.8%** - Chiếm đa số)
  2. **Xe Dầu (Diesel):** 5,888 tin đăng (**17.4%** - Phổ biến ở SUV & Bán tải)
  3. **Xe Điện (EV):** 778 tin đăng (**2.3%** - Tăng trưởng nhanh nhờ VinFast)
  4. **Xe Hybrid:** 510 tin đăng (**1.5%** - Xu hướng tiết kiệm nhiên liệu)

- **Đặc điểm nổi bật:**
  - Tỷ lệ xe mới ở phân khúc **Xe Điện đạt >60%** (do các mẫu VinFast VF5, VF8, VF9 mới bán ra).
  - Xe Xăng và Dầu có tỷ lệ xe cũ cao hơn (>80%).

<suggestions>Chi phí vận hành xe điện vs xe xăng?|Chân dung người chọn mua xe điện?|Xem Tab 4 người mua xe?</suggestions>""",

    "Tab4": """## 👥 TAB 4 — CHÂN DUNG NGƯỜI MUA XE VIỆT

- **Hộp số ưa chuộng:**
  - **Hộp số Tự động (Automatic):** **82.05%** (Áp đảo hoàn toàn nhờ sự tiện dụng).
  - **Hộp số Sàn (Manual):** **17.95%** (Chủ yếu ở xe dịch vụ hoặc giá rẻ).

- **Số chỗ ngồi:**
  - **Xe 5 chỗ:** **68.82%** (Dòng sedan và crossover nhỏ gọn).
  - **Xe 7 chỗ:** **25.10%** (Dành cho gia đình đông người và chạy dịch vụ).

- **Màu sắc ngoại thất phổ biến nhất:**
  1. **Trắng:** 33.62% (Được ưa chuộng nhất, giữ giá tốt)
  2. **Đen:** 22.0%
  3. **Đỏ / Bạc / Nâu:** Chiếm phần còn lại.

<suggestions>Màu xe nào dễ bán lại nhất?|Tại sao xe tự động chiếm 82%?|Xem Tab 5 đặc biệt?</suggestions>""",

    "Tab5": """## 🔍 TAB 5 — GÓC KHUẤT THỊ TRƯỜNG Ô TÔ

- **Xe chạy nhiều km nhất:** 500,000 km (Các dòng Toyota Innova / Vios bền bỉ).
- **Số hãng xe hiếm (Số lượng dưới 5 xe):** 33 hãng xe siêu sang / xe cổ nhập nhỏ lẻ.
- **Biến động chênh lệch giá lớn nhất:** Hãng **Ferrari** có độ chênh lệch giá giữa các đời xe lên tới **40.5 tỷ VNĐ**.
- **Top xe đắt nhất:** Ferrari SF90 Stradale (54 tỷ), Rolls-Royce Phantom (45 tỷ).

<suggestions>Cho tôi xem tổng quan cả 5 Tab?|Hỏi AI phân tích dòng xe cụ thể?</suggestions>""",

    "notebook": """## 📓 TÓM TẮT 3 JUPYTER NOTEBOOKS PHÂN TÍCH DỮ LIỆU

1. **`01_data_overview.ipynb` (52 cells):**
   - Đọc dữ liệu thô từ Bonbanh.com (33,848 dòng × 30 cột).
   - Kiểm tra định dạng dữ liệu, giá trị thiếu (Missing values) và kiểu dữ liệu từng cột.

2. **`02_preprocessing.ipynb` (43 cells):**
   - Tiền xử lý dữ liệu: Ép kiểu dữ liệu giá (triệu VNĐ), Odometer (km), năm sản xuất.
   - Xử lý các outlier dị thường (như số km tỷ km, giá xe sai định dạng).
   - Tạo các cột sạch với hậu tố `_sạch` để sẵn sàng cho phân tích.

3. **`03_eda.ipynb` (43 cells):**
   - Phân tích khám phá dữ liệu (EDA): Trực quan hóa tương quan giữa Giá xe, Năm SX, Hãng và Loại nhiên liệu.
   - Xuất dữ liệu đã làm sạch ra `car_detail_processed.csv` và `Dashboard.json`.

<suggestions>Xem Notebook 01_data_overview?|Xem Notebook 02_preprocessing?|Xem Notebook 03_eda?</suggestions>""",

    "code_sample": """Dưới đây là đoạn mã Python mẫu hoàn chỉnh phân tích tập dữ liệu ô tô và vẽ biểu đồ. Đoạn code này ở trạng thái **CHỜ DUYỆT**, bạn có thể chỉnh sửa trực tiếp tham số hoặc nhấn nút **`▶ Thực thi`** ở góc trên khối code để chạy trực tiếp trên máy của bạn:

```python
import pandas as pd
import matplotlib.pyplot as plt

# 1. Khởi tạo dữ liệu ô tô mẫu
data = {
    'Hãng xe': ['Toyota', 'Hyundai', 'Ford', 'Mercedes-Benz', 'Kia'],
    'Số lượng (xe)': [5861, 3897, 3719, 3376, 3258],
    'Giá trung bình (triệu VNĐ)': [833.4, 607.5, 817.4, 2689.9, 546.2]
}

df_cars = pd.DataFrame(data)

# In kết quả thống kê ra màn hình stdout
print("=== THỐNG KÊ TOP 5 HÃNG XE Ô TÔ VIỆT NAM ===")
print(df_cars)

# 2. Vẽ biểu đồ cột trực quan hóa
plt.figure(figsize=(8, 4.5))
colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
plt.bar(df_cars['Hãng xe'], df_cars['Số lượng (xe)'], color=colors)
plt.title('Thống Kê Số Lượng Tin Rao Bán Xe Theo Top 5 Hãng')
plt.xlabel('Thương hiệu Hãng xe')
plt.ylabel('Số lượng tin rao (xe)')
plt.grid(axis='y', linestyle='--', alpha=0.5)
```

<suggestions>Thực thi đoạn code ở trên?|Sửa màu sắc biểu đồ sang màu đỏ?|Xem tóm tắt Tab 1 Dashboard?</suggestions>""",

    "code_sample_pie": """Dưới đây là đoạn mã Python mẫu vẽ biểu đồ hình tròn (Pie Chart) thể hiện thị phần nhiên liệu ô tô. Đoạn code ở trạng thái **CHỜ DUYỆT**, bạn có thể chỉnh sửa trực tiếp hoặc nhấn nút **`▶ Thực thi`**:

```python
import pandas as pd
import matplotlib.pyplot as plt

# 1. Dữ liệu thị phần loại nhiên liệu
fuel_data = {
    'Nhiên liệu': ['Xăng', 'Dầu (Diesel)', 'Điện (EV)', 'Hybrid'],
    'Tỷ lệ (%)': [78.8, 17.4, 2.3, 1.5]
}

df_fuel = pd.DataFrame(fuel_data)
print("=== CƠ CẤU NHIÊN LIỆU THỊ TRƯỜNG XE ===")
print(df_fuel)

# 2. Vẽ biểu đồ hình tròn
plt.figure(figsize=(6, 6))
colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b']
plt.pie(df_fuel['Tỷ lệ (%)'], labels=df_fuel['Nhiên liệu'], autopct='%1.1f%%', colors=colors, startangle=140)
plt.title('Thị Phần Loại Nhiên Liệu Ô Tô Việt Nam')
```

<suggestions>Thực thi đoạn code ở trên?|Xem tóm tắt Tab 3 Xăng vs Điện?|Viết code biểu đồ cột?</suggestions>""",

    "nb1": """## 📓 NỘI DUNG CHI TIẾT NOTEBOOK: `01_data_overview.ipynb` (52 Cells)

- **Mục tiêu:** Khám phá cấu trúc dữ liệu thô cào từ Bonbanh.com (33,848 tin đăng × 30 cột).
- **Các bước chính trong Notebook:**
  1. **Đọc dữ liệu thô:** Load file `car_detail.csv` và kiểm tra kích thước 33,848 dòng × 30 cột.
  2. **Phân tích kiểu dữ liệu (`df.info()`, `df.dtypes`):** Phát hiện các cột số (như Giá, Số Km, Năm sản xuất) bị dính ký tự văn bản hoặc chữ "triệu", "tỷ", "km".
  3. **Thống kê Missing Values (`df.isnull().sum()`):**
     - Cột `Hãng`, `Dòng xe`, `Năm sản xuất` có tỷ lệ đầy đủ 100%.
     - Cột `Tiêu thụ nhiên liệu`, `Dung tích động cơ` có tỷ lệ missing ~15-20%.
  4. **Kiểm tra trùng lặp (Duplicates):** Loại bỏ các tin đăng trùng lặp ID hoặc nội dung.

<suggestions>Xem Notebook 02_preprocessing?|Xem Notebook 03_eda?|Xem Dashboard Tab 1?</suggestions>""",

    "nb2": """## 📓 NỘI DUNG CHI TIẾT NOTEBOOK: `02_preprocessing.ipynb` (43 Cells)

- **Mục tiêu:** Làm sạch dữ liệu, xử lý Outlier và tạo các cột chuẩn hóa (`_sạch`).
- **Các bước làm sạch dữ liệu trong Notebook:**
  1. **Xử lý cột Giá xe (`Giá (triệu VND)`):**
     - Chuyển đổi các chuỗi dạng "500 triệu", "1.2 tỷ" về cùng đơn vị **triệu VNĐ** (float).
     - Loại bỏ các mức giá bất thường (dưới 10 triệu hoặc giá bằng 0).
  2. **Xử lý Số Km đã đi (`Số Km đã đi sạch`):**
     - Lọc các số km ảo (như 999,999,999 km) về `NaN` hoặc median theo năm sản xuất.
  3. **Chuẩn hóa Phân loại:**
     - Gom nhóm `Loại nhiên liệu`: Xăng, Dầu, Điện, Hybrid.
     - Gom nhóm `Hộp số`: Tự động (Automatic) vs Số sàn (Manual).
     - Gom nhóm `Xuất xứ`: Trong nước vs Nhập khẩu.
  4. **Xuất file:** Lưu dữ liệu sạch ra `car_detail_processed.csv`.

<suggestions>Xem Notebook 03_eda?|Xem Notebook 01_data_overview?|Xem Tab 2 - Giải mã giá xe?</suggestions>""",

    "nb3": """## 📓 NỘI DUNG CHI TIẾT NOTEBOOK: `03_eda.ipynb` (43 Cells)

- **Mục tiêu:** Trực quan hóa dữ liệu (EDA), phân tích tương quan và trích xuất chỉ số cho Dashboard.
- **Các phân tích chính trong Notebook:**
  1. **Phân bố Hãng xe & Kiểu dáng (Seaborn / Matplotlib):**
     - Vẽ biểu đồ cột Top 10 hãng xe (Toyota dẫn đầu 5,861 xe).
     - Biểu đồ tròn (Pie chart) kiểu dáng xe (SUV 36.3%, Sedan 31.8%).
  2. **Phân tích Giá xe theo Nhiên liệu & Hộp số:**
     - Biểu đồ Hộp (Boxplot) so sánh giá xe Xăng vs Xe Điện vs Xe Dầu.
     - Ma trận tương quan (Correlation Heatmap) giữa Năm sản xuất và Giá xe.
  3. **Trích xuất JSON:**
     - Tính toán tổng hợp KPI và các bảng phân bố, xuất trực tiếp ra `Dashboard.json` cho Frontend.

<suggestions>Xem tổng quan Dashboard?|Xem Notebook 02_preprocessing?|Chạy code Python trực tiếp?</suggestions>""",

    "overview": """## 📊 TỔNG QUAN DASHBOARD Ô TÔ VIỆT NAM — 5 TAB PHÂN TÍCH

1. **Tab 1 — Bức Tranh Thị Trường:** 33,848 tin đăng | Top 1: Toyota (5.8k xe), Hyundai (3.8k xe), Ford (3.7k xe).
2. **Tab 2 — Giải Mã Giá Xe:** Giá trung bình **638 triệu VNĐ** | Rẻ nhất 18tr (Kia Pride) | Đắt nhất 54 tỷ (Ferrari SF90).
3. **Tab 3 — Xăng vs Điện:** Xe Xăng chiếm 78.8% | Xe Dầu 17.4% | Xe Điện 2.3% (VinFast tăng trưởng mạnh).
4. **Tab 4 — Chân Dung Người Mua:** Hộp số tự động 82.05% | Xe 5 chỗ 68.82% | Màu trắng ưa chuộng nhất 33.62%.
5. **Tab 5 — Góc Khuất Thị Trường:** Xe đi nhiều km nhất 500k km | 33 hãng xe hiếm.

<suggestions>Cho tôi xem Tab 1 - Bức tranh thị trường?|Cho tôi xem Tab 3 - Xăng vs Điện?|Cho tôi xem Tab 2 - Giải mã giá xe?</suggestions>"""
}


def _is_data_calculation_query(msg: str) -> bool:
    """
    Phát hiện câu hỏi yêu cầu tính toán/phân tích thực tế trên CSV.
    Trả về True nếu cần force gọi query_dataset_readonly.
    """
    m = msg.lower()

    # 🛑 NẾU LÀ YÊU CẦU QUẢN LÝ / CHỈNH SỬA FILE -> KHÔNG PHẢI TÍNH TOÁN CSV!
    file_action_kws = [
        "file", ".py", ".txt", ".json", ".md",
        "dòng thứ", "dòng 1", "dòng 2", "dòng 3", "dòng 4", "dòng 5",
        "sửa file", "tạo file", "xóa file", "đổi tên", "di chuyển",
        "trong file", "nội dung file", "lịch sử file", "backup",
        "hãy đổi", "thay thế dòng", "sửa dòng"
    ]
    if any(kw in m for kw in file_action_kws):
        return False

    # Các từ khóa hành động tính toán
    calc_kw = [
        "tính", "tính toán", "trung bình", "trung vị", "median", "mean",
        "so sánh", "phân bố", "top ", "hãng nào", "bao nhiêu", "chiếm",
        "thống kê", "phân tích", "đếm", "count", "max", "min", "cao nhất",
        "thấp nhất", "nhiều nhất", "ít nhất", "tổng số", "tỷ lệ",
        "giá trung bình", "số lượng", "bao giờ",
    ]
    # Các đối tượng dữ liệu cụ thể (tránh nhận diện câu hỏi chung)
    data_obj_kw = [
        "km", "giá", "xe dầu", "xe xăng", "nhiên liệu", "hãng xe",
        "dòng xe", "năm sản xuất", "hộp số", "màu", "chỗ ngồi",
        "dầu", "xăng", "điện", "hybrid", "xuất xứ", "tình trạng",
        "toyota", "hyundai", "ford", "kia", "mazda", "vinfast",
    ]
    has_calc = any(kw in m for kw in calc_kw)
    has_obj = any(kw in m for kw in data_obj_kw)
    return has_calc and has_obj


def _auto_generate_pandas_code(msg: str) -> str | None:
    """
    Tự động tạo mã pandas tương ứng dựa vào intent của câu hỏi.
    Trả về code string để thực thi qua query_dataset_readonly.
    Mã pandas sinh ra luôn tự động format trực tiếp ra bảng Markdown (100% chính xác).
    """
    m = msg.lower()

    # ── Pattern 1: Trung bình / Trung vị Km theo năm sản xuất + loại nhiên liệu ──
    if any(w in m for w in ["km", "kilom", "số km"]) and any(w in m for w in ["dầu", "xăng", "nhiên liệu", "điện", "hybrid"]):
        import re
        years = re.findall(r'\b(20\d{2})\b', msg)
        year_filter = ""
        if len(years) >= 2:
            y1, y2 = sorted([int(y) for y in years[:2]])
            year_filter = f" & (df['Năm sản xuất'] >= {y1}) & (df['Năm sản xuất'] <= {y2})"
        fuels = []
        if "xăng" in m: fuels.append("Xăng")
        if "dầu" in m: fuels.append("Dầu")
        if "điện" in m: fuels.append("Điện")
        if "hybrid" in m: fuels.append("Hybrid")
        if not fuels: fuels = ["Xăng", "Dầu"]
        fuel_filter = str(fuels)
        return """
import pandas as pd
df2 = df[(df['Loại nhiên liệu'].isin(""" + fuel_filter + """))""" + year_filter + """].copy()
df2['Năm sản xuất'] = df2['Năm sản xuất'].astype(int)
p_mean = df2.pivot_table(index='Năm sản xuất', columns='Loại nhiên liệu', values='Số Km đã đi sạch', aggfunc='mean').round(1)
p_med = df2.pivot_table(index='Năm sản xuất', columns='Loại nhiên liệu', values='Số Km đã đi sạch', aggfunc='median').round(1)
p_cnt = df2.pivot_table(index='Năm sản xuất', columns='Loại nhiên liệu', values='Số Km đã đi sạch', aggfunc='count')

res_dict = {'Năm sản xuất': [str(y) for y in p_mean.index]}
for fuel in """ + fuel_filter + """:
    if fuel in p_mean.columns:
        res_dict['TB ' + str(fuel) + ' (km)'] = p_mean[fuel].values
        res_dict['Trung vị ' + str(fuel) + ' (km)'] = p_med[fuel].values
        res_dict['Số xe ' + str(fuel)] = p_cnt[fuel].values
res = pd.DataFrame(res_dict)
print("### 📊 Thống kê số Km đã đi thực tế (từ 33,848 tin đăng CSV):\\n")
print(res.to_markdown(index=False, floatfmt=',.1f'))
"""

    # ── Pattern 2: Giá trung bình theo Hãng xe ────────────────────────────────
    if any(w in m for w in ["giá", "giá xe", "price"]) and any(w in m for w in ["hãng", "thương hiệu", "trung bình"]):
        return """
import pandas as pd
res = df.groupby('Hãng')['Giá (triệu VND)'].agg(
    TB_Giá='mean', Trung_vị='median', Min_Giá='min', Max_Giá='max', Số_xe='count'
).round(1).sort_values('Số_xe', ascending=False).head(15).reset_index()
res.columns = ['Hãng xe', 'Giá TB (triệu VNĐ)', 'Giá Trung vị', 'Giá Thấp nhất', 'Giá Cao nhất', 'Số lượng xe']
res['Giá TB (triệu VNĐ)'] = res['Giá TB (triệu VNĐ)'].map('{:,.1f}'.format)
res['Giá Trung vị'] = res['Giá Trung vị'].map('{:,.1f}'.format)
res['Giá Thấp nhất'] = res['Giá Thấp nhất'].map('{:,.0f}'.format)
res['Giá Cao nhất'] = res['Giá Cao nhất'].map('{:,.0f}'.format)
res['Số lượng xe'] = res['Số lượng xe'].map('{:,}'.format)
print("### 📊 Thống kê Giá xe theo Top 15 Hãng xe phổ biến nhất:\\n")
print(res.to_markdown(index=False))
"""

    # ── Pattern 3: Top hãng xe theo số lượng ──────────────────────────────────
    if any(w in m for w in ["top", "nhiều nhất", "hãng nào"]) and any(w in m for w in ["hãng", "thương hiệu"]):
        return """
import pandas as pd
counts = df['Hãng'].value_counts().head(15)
pct = (counts / len(df) * 100).round(2)
res = pd.DataFrame({'Hãng xe': counts.index, 'Số lượng xe': counts.values, 'Tỷ lệ (%)': pct.values})
res['Số lượng xe'] = res['Số lượng xe'].map('{:,}'.format)
res['Tỷ lệ (%)'] = res['Tỷ lệ (%)'].map('{:.2f}%'.format)
print("### 📊 Top 15 Hãng xe chiếm thị phần lớn nhất:\\n")
print(res.to_markdown(index=False))
"""

    # ── Pattern 4: Phân bố Loại nhiên liệu ────────────────────────────────────
    if any(w in m for w in ["phân bố", "tỷ lệ", "chiếm"]) and any(w in m for w in ["nhiên liệu", "xăng", "dầu", "điện"]):
        return """
import pandas as pd
counts = df['Loại nhiên liệu'].value_counts()
pct = (counts / len(df) * 100).round(2)
res = pd.DataFrame({'Loại nhiên liệu': counts.index, 'Số lượng xe': counts.values, 'Tỷ lệ (%)': pct.values})
res['Số lượng xe'] = res['Số lượng xe'].map('{:,}'.format)
res['Tỷ lệ (%)'] = res['Tỷ lệ (%)'].map('{:.2f}%'.format)
print("### 📊 Cơ cấu Loại nhiên liệu trên thị trường:\\n")
print(res.to_markdown(index=False))
"""

    # ── Pattern 5: Giá trung bình theo Loại nhiên liệu ───────────────────────
    if any(w in m for w in ["giá", "price"]) and any(w in m for w in ["nhiên liệu", "xăng", "dầu", "điện", "hybrid"]):
        return """
import pandas as pd
res = df.groupby('Loại nhiên liệu')['Giá (triệu VND)'].agg(
    TB_Giá='mean', Trung_vị='median', Min_Giá='min', Max_Giá='max', Số_xe='count'
).round(1).sort_values('Số_xe', ascending=False).reset_index()
res.columns = ['Loại nhiên liệu', 'Giá TB (triệu VNĐ)', 'Giá Trung vị', 'Giá Thấp nhất', 'Giá Cao nhất', 'Số lượng xe']
res['Giá TB (triệu VNĐ)'] = res['Giá TB (triệu VNĐ)'].map('{:,.1f}'.format)
res['Giá Trung vị'] = res['Giá Trung vị'].map('{:,.1f}'.format)
res['Giá Thấp nhất'] = res['Giá Thấp nhất'].map('{:,.0f}'.format)
res['Giá Cao nhất'] = res['Giá Cao nhất'].map('{:,.0f}'.format)
res['Số lượng xe'] = res['Số lượng xe'].map('{:,}'.format)
print("### 📊 So sánh Giá xe theo Loại nhiên liệu:\\n")
print(res.to_markdown(index=False))
"""

    # ── Pattern 6: Phân bố Dòng xe / Body style ───────────────────────────────
    if any(w in m for w in ["dòng xe", "kiểu xe", "suv", "sedan", "hatchback", "crossover"]):
        return """
import pandas as pd
counts = df['Dòng xe'].value_counts().head(15)
pct = (counts / len(df) * 100).round(2)
res = pd.DataFrame({'Dòng xe': counts.index, 'Số lượng xe': counts.values, 'Tỷ lệ (%)': pct.values})
res['Số lượng xe'] = res['Số lượng xe'].map('{:,}'.format)
res['Tỷ lệ (%)'] = res['Tỷ lệ (%)'].map('{:.2f}%'.format)
print("### 📊 Top Dòng xe (Kiểu dáng) được rao bán nhiều nhất:\\n")
print(res.to_markdown(index=False))
"""

    # ── Pattern 7: Phân bố Màu xe ────────────────────────────────────────────
    if any(w in m for w in ["màu", "color"]):
        return """
import pandas as pd
counts = df['Màu ngoại thất'].value_counts().head(10)
pct = (counts / len(df) * 100).round(2)
res = pd.DataFrame({'Màu xe': counts.index, 'Số lượng xe': counts.values, 'Tỷ lệ (%)': pct.values})
res['Số lượng xe'] = res['Số lượng xe'].map('{:,}'.format)
res['Tỷ lệ (%)'] = res['Tỷ lệ (%)'].map('{:.2f}%'.format)
print("### 📊 Phân bố Màu xe ngoại thất phổ biến:\\n")
print(res.to_markdown(index=False))
"""

    # ── Pattern 8: Phân bố Hộp số ────────────────────────────────────────────
    if any(w in m for w in ["hộp số", "tự động", "số sàn", "manual", "automatic"]):
        return """
import pandas as pd
counts = df['Hộp số'].value_counts()
pct = (counts / len(df) * 100).round(2)
res = pd.DataFrame({'Loại Hộp số': counts.index, 'Số lượng xe': counts.values, 'Tỷ lệ (%)': pct.values})
res['Số lượng xe'] = res['Số lượng xe'].map('{:,}'.format)
res['Tỷ lệ (%)'] = res['Tỷ lệ (%)'].map('{:.2f}%'.format)
print("### 📊 Phân bố Loại Hộp số:\\n")
print(res.to_markdown(index=False))
"""

    # ── Pattern 9: Phân bố Tình trạng xe (Mới / Cũ) ───────────────────────────
    if any(w in m for w in ["tình trạng", "xe mới", "xe cũ", "đã qua sử dụng"]):
        return """
import pandas as pd
counts = df['Tình trạng'].value_counts()
pct = (counts / len(df) * 100).round(2)
res = pd.DataFrame({'Tình trạng': counts.index, 'Số lượng xe': counts.values, 'Tỷ lệ (%)': pct.values})
res['Số lượng xe'] = res['Số lượng xe'].map('{:,}'.format)
res['Tỷ lệ (%)'] = res['Tỷ lệ (%)'].map('{:.2f}%'.format)
print("### 📊 Cơ cấu Tình trạng xe rao bán:\\n")
print(res.to_markdown(index=False))
"""

    # ── Pattern 10: Số chỗ ngồi ──────────────────────────────────────────────
    if any(w in m for w in ["chỗ ngồi", "chỗ", "seats"]):
        return """
import pandas as pd
counts = df['Số chỗ ngồi sạch'].value_counts().sort_index()
pct = (counts / len(df) * 100).round(2)
res = pd.DataFrame({'Số chỗ ngồi': counts.index, 'Số lượng xe': counts.values, 'Tỷ lệ (%)': pct.values})
res['Số lượng xe'] = res['Số lượng xe'].map('{:,}'.format)
res['Tỷ lệ (%)'] = res['Tỷ lệ (%)'].map('{:.2f}%'.format)
print("### 📊 Phân bố Thiết kế Số chỗ ngồi:\\n")
print(res.to_markdown(index=False))
"""

    # ── Pattern 11: Dynamic Generic Fallback (Hãng xe / Năm / Chỉ số bất kỳ) ──
    brands = [b for b in ["toyota", "hyundai", "ford", "kia", "mazda", "honda", "vinfast", "mercedes", "bmw", "mitsubishi", "nissan", "chevrolet", "suzuki", "lexus", "audi"] if b in m]
    import re
    years = [int(y) for y in re.findall(r'\b(20\d{2})\b', msg)]

    target_col = 'Giá (triệu VND)'
    col_name = 'Giá'
    if any(w in m for w in ["km", "kilom", "số km"]):
        target_col = 'Số Km đã đi sạch'
        col_name = 'Số Km'

    brand_filter = f"df['Hãng'].str.lower().isin({str(brands)})" if brands else "True"
    year_filter = f"df['Năm sản xuất'].isin({str(years)})" if years else "True"

    group_list = ['Hãng', 'Năm sản xuất'] if (brands and years) else ['Hãng'] if brands else ['Năm sản xuất']
    header_list = group_list + [f'{col_name} TB', f'{col_name} Trung vị', 'Số lượng xe']

    return f"""
import pandas as pd
df2 = df[({brand_filter}) & ({year_filter})].copy()
df2['Năm sản xuất'] = df2['Năm sản xuất'].astype(int)
res = df2.groupby({str(group_list)})['{target_col}'].agg(
    Trung_bình='mean', Trung_vị='median', Số_xe='count'
).round(1).reset_index()
res['Trung_bình'] = res['Trung_bình'].map('{{:,.1f}}'.format)
res['Trung_vị'] = res['Trung_vị'].map('{{:,.1f}}'.format)
res['Số_xe'] = res['Số_xe'].map('{{:,}}'.format)
res.columns = {str(header_list)}
print("### 📊 Thống kê {col_name} thực tế từ dữ liệu 33,848 tin đăng:\\n")
print(res.to_markdown(index=False))
"""



def _get_dashboard_data() -> dict:
    """Load Dashboard.json vào cache module-level để tránh đọc file mỗi request."""
    global _DASHBOARD_CACHE
    if _DASHBOARD_CACHE is None:
        docs_dir = Path(__file__).resolve().parents[4] / "docs"
        json_path = docs_dir / "Dashboard.json"
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    _DASHBOARD_CACHE = json.load(f)
                msg = f"[DashboardCache] ✅ Dashboard.json cached: {len(_DASHBOARD_CACHE)} tabs"
                logger.warning(msg)
                print(msg)
            except Exception as e:
                logger.warning("[DashboardCache] ❌ Failed to load Dashboard.json: %s", e)
                print(f"[DashboardCache] ❌ Lỗi đọc Dashboard.json: {e}")
                _DASHBOARD_CACHE = {}
        else:
            logger.warning("[DashboardCache] ❌ Dashboard.json not found at %s", json_path)
            print(f"[DashboardCache] ❌ Không tìm thấy: {json_path}")
            _DASHBOARD_CACHE = {}
    return _DASHBOARD_CACHE

# ─── Cache DataFrame CSV (25MB, load 1 lần) ──────────────────────────────────
_DF_CACHE = None  # pandas DataFrame | None
_DF_CACHE_PATH: str | None = None

def _get_cached_df():
    """
    Load car_detail_processed.csv vào cache module-level.
    Lần đầu: ~2-5s. Lần sau: ~0ms (đọc từ RAM).
    """
    global _DF_CACHE, _DF_CACHE_PATH
    if _DF_CACHE is not None:
        return _DF_CACHE

    data_path = get_data_file_path()
    if not data_path:
        logger.warning("[DataCache] ❌ get_data_file_path() trả None — kiểm tra .env DATA_PATH")
        print("[DataCache] ❌ Không tìm thấy đường dẫn CSV.")
        return None
    try:
        import pandas as pd
        import time as _time
        print(f"[DataCache] ⏳ Đang load CSV vào RAM: {data_path}")
        t0 = _time.time()
        _DF_CACHE = pd.read_csv(
            data_path, low_memory=False, encoding="utf-8-sig", encoding_errors="replace"
        )
        _DF_CACHE_PATH = str(data_path)
        elapsed = _time.time() - t0
        shape = _DF_CACHE.shape
        mb = _DF_CACHE.memory_usage(deep=True).sum() / 1024 / 1024
        msg = f"[DataCache] ✅ CSV cached: {shape[0]:,} dòng × {shape[1]} cột | {mb:.1f} MB RAM | {elapsed:.2f}s"
        logger.warning(msg)
        print(msg)
    except Exception as e:
        logger.warning("[DataCache] ❌ Failed to cache CSV: %s", e)
        print(f"[DataCache] ❌ Lỗi load CSV: {e}")
        _DF_CACHE = None
    return _DF_CACHE

# ─── Cache Notebook metadata (3 files, đọc 1 lần) ────────────────────────────
_NOTEBOOK_META_CACHE: list | None = None

def _get_notebook_metadata() -> list:
    """Đọc metadata của 3 notebooks lúc startup. Không đọc toàn bộ nội dung."""
    global _NOTEBOOK_META_CACHE
    if _NOTEBOOK_META_CACHE is not None:
        return _NOTEBOOK_META_CACHE

    notebook_dir = Path(__file__).resolve().parents[4] / "notebook"
    meta = []
    if notebook_dir.exists():
        for nb_file in sorted(notebook_dir.glob("*.ipynb")):
            try:
                with open(nb_file, "r", encoding="utf-8") as f:
                    nb_data = json.load(f)
                cells = nb_data.get("cells", [])
                code_cells = [c for c in cells if c.get("cell_type") == "code"]
                md_cells   = [c for c in cells if c.get("cell_type") == "markdown"]
                first_md = ""
                if md_cells:
                    source = md_cells[0].get("source", [])
                    first_md = "".join(source)[:200].strip()
                meta.append({
                    "name": nb_file.name,
                    "path": str(nb_file),
                    "size_kb": round(nb_file.stat().st_size / 1024, 1),
                    "total_cells": len(cells),
                    "code_cells": len(code_cells),
                    "markdown_cells": len(md_cells),
                    "description": first_md,
                })
                logger.warning("[NotebookCache] ✅ Indexed: %s (%d cells)", nb_file.name, len(cells))
                print(f"[NotebookCache] ✅ {nb_file.name} — {len(cells)} cells")
            except Exception as e:
                logger.warning("[NotebookCache] ❌ Failed to index %s: %s", nb_file.name, e)
    _NOTEBOOK_META_CACHE = meta
    return _NOTEBOOK_META_CACHE

# ─── Warm up tất cả caches khi module load ───────────────────────────────────
import threading as _threading
import time as _startup_time

def _warmup_caches():
    """Preload tất cả caches trong background — delay 2s đợi server sẵn sàng."""
    _startup_time.sleep(2)
    print("\n[Cache Warmup] 🚀 Bắt đầu preload caches...")
    try:
        _get_dashboard_data()
    except Exception as _e:
        print(f"[Cache Warmup] ❌ Dashboard cache lỗi: {_e}")
    try:
        _get_notebook_metadata()
    except Exception as _e:
        print(f"[Cache Warmup] ❌ Notebook cache lỗi: {_e}")
    try:
        _get_cached_df()
    except Exception as _e:
        print(f"[Cache Warmup] ❌ CSV cache lỗi: {_e}")
    print("[Cache Warmup] 🎉 Tất cả caches đã sẵn sàng!\n")

_warmup_thread = _threading.Thread(target=_warmup_caches, daemon=True, name="cache-warmup")
_warmup_thread.start()

# ─── NOTE: CSV context được inject bởi data_context.py ───────────────────────

# ─── System Prompt Builder ────────────────────────────────────────────────────
# Pattern chuẩn: [ROLE] → [CIRCUMSTANCE + DASHBOARD DATA + KB] → [RULES]
# - ROLE: Khai báo danh tính và nhiệm vụ của AI
# - CIRCUMSTANCE: Ngữ cảnh dữ liệu thực tế từ data_context.py (CSV + Dashboard.json + Notebooks)
# - RULES: Nguyên tắc hành vi bắt buộc

_ROLE_BLOCK = """\
══════════════════════════════════════════════════════════════════
NGÔN NGỮ: CHỈ TIẾNG VIỆT — TUYỆT ĐỐI KHÔNG ĐƯỢC DÙNG TIẾNG ANH,
TIẾNG TRUNG HAY BẤT KỲ NGÔN NGỮ NÀO KHÁC. MỌI CÂU TRẢ LỜI PHẢI
BẰNG TIẾNG VIỆT. ĐÂY LÀ QUY TẮC CAO NHẤT, KHÔNG CÓ NGOẠI LỆ.
══════════════════════════════════════════════════════════════════

# [VAI TRÒ]
Bạn là **VietCar AI** — chuyên gia phân tích dữ liệu ô tô Việt Nam,
hỗ trợ nhóm sinh viên thực hiện Đồ án cuối kỳ môn Trực Quan Hóa Dữ Liệu.

**Đồ án:** Phân tích thị trường ô tô Việt Nam (33,848 xe từ bonbanh.com)
**Dashboard:** 5 tab — Tab1: Thị trường | Tab2: Giá xe | Tab3: Xăng vs Điện | Tab4: Người mua | Tab5: Góc khuất
**Notebooks:** `01_data_overview.ipynb` · `02_preprocessing.ipynb` · `03_eda.ipynb`
**Kỹ năng:** Python (pandas, matplotlib, seaborn, numpy), phân tích dữ liệu, thị trường ô tô VN

---

# [QUY TẮC HÀNH ĐỘNG — ĐỌC KỸ TRƯỚC KHI TRẢ LỜI]

## 1. QUYẾT ĐỊNH DÙNG TOOL HAY TRẢ LỜI TRỰC TIẾP

| Câu hỏi về | Hành động |
|------------|-----------|
| Dashboard / Tab 1-5 / biểu đồ / KPI | → Gọi `get_dashboard_info(tab="TabX")` |
| Thống kê chi tiết CSV (giá, hãng, filter) | → Gọi `query_dataset_readonly(code=...)` |
| Tạo file mới trong project | → BẮT BUỘC gọi `create_file(file_path=..., content=...)` |
| Sửa / Ghi đè file trong project | → BẮT BUỘC gọi `modify_file(file_path=..., operation=..., content=..., line_number=..., search_text=...)`. LƯU Ý: Nên truyền `line_number` hoặc `search_text` ngắn gọn để tìm kiếm chính xác. |
| Xóa file trong project | → BẮT BUỘC gọi `delete_file(file_path=...)` |
| Đổi tên / Di chuyển file | → BẮT BUỘC gọi `move_rename_file(source=..., destination=...)` |
| Hoàn tác / Rollback thay đổi file | → BẮT BUỘC gọi `rollback_last_change(file_path=...)` |
| Xem lịch sử sửa đổi / Backups file | → BẮT BUỘC gọi `show_change_history(file_path=...)` hoặc `list_all_backups` |
| Chạy / Thực thi file script Python (.py) | → BẮT BUỘC gọi `run_python_file(file_path=...)` |
| File cụ thể / thư mục | → Gọi `read_file_content` hoặc `list_files` |
| Link URL xe | → Gọi `scrape_car_data(url=...)` |
| Schema CSV / tên cột | → Trả lời trực tiếp từ context bên dưới |
| Câu hỏi chung về đồ án | → Trả lời từ kiến thức |

## 2. QUY TẮC BẮT BUỘC — VI PHẠM = THẤT BẠI

- ✅ **GỌI TOOL NGẦM** — không hỏi user "Tôi có nên kiểm tra không?"
- 🚫 **TUYỆT ĐỐI KHÔNG BỊA CON SỐ (NO HALLUCINATION)** — Khi câu hỏi yêu cầu tính toán/so sánh số liệu CSV (như tính trung bình km xe Dầu vs Xăng theo năm), BẮT BUỘC PHẢI GỌI TOOL `query_dataset_readonly` ĐỂ TÍNH TOÁN THỰC TẾ. TUYỆT ĐỐI KHÔNG ĐƯỢC TỰ BỊA CÁC CON SỐ GIẢ LẬP.
- 🚫 **TUYỆT ĐỐI KHÔNG BỊA RA THAO TÁC FILE BẰNG TEXT** — Khi người dùng yêu cầu tạo file, sửa file, xóa file, đổi tên, rollback hay xem lịch sử file, BẮT BUỘC PHẢI GỌI CÁC TOOL `create_file`, `modify_file`, `delete_file`, `move_rename_file`, `rollback_last_change`, `show_change_history`. TUYỆT ĐỐI KHÔNG ĐƯỢC NÓI "File đã được tạo/sửa/xóa thành công" BẰNG CHỮ KHI CHƯA GỌI TOOL.
- ✅ **KHÔNG HỎI NGƯỢC** — không hỏi "Bạn muốn biết gì thêm?", "Tab nào bạn muốn?"
- ✅ **KHÔNG IN CODE** khi user chỉ hỏi thông tin — chỉ in code khi user yêu cầu rõ ràng
- ✅ **TIẾNG VIỆT** — toàn bộ câu trả lời phải bằng tiếng Việt, không ngoại lệ

## 2.1 QUY TẮC SINH CODE & GIẢI THÍCH (BẮT BUỘC THEO HƯỚNG DẪN TÍCH HỢP AI)

- 📝 **BẮT BUỘC CÓ COMMENT GIẢI THÍCH BẰNG NGÔN NGỮ TỰ NHIÊN**: Mỗi khi sinh mã Python theo yêu cầu của người dùng, BẮT BUỘC phải đính kèm các dòng comment tiếng Việt giải thích rõ ràng ý nghĩa của từng khối lệnh ngay bên trong/trên đoạn code (Ví dụ: `# Đoạn code này sẽ xóa 15 dòng có giá trị NULL ở cột Doanh Thu, sử dụng hàm dropna() của Pandas.`).
- 💡 **MÔ TẢ TỔNG QUAN**: Trước khi đưa ra khối code, ghi 1-2 câu tiếng Việt tóm tắt tác dụng và giải thích phương pháp phân tích/thuật toán được sử dụng để người dùng dễ theo dõi và phê duyệt.

## 3. ĐỊNH DẠNG CÂU TRẢ LỜI

- Dùng **bảng Markdown** cho dữ liệu nhiều cột
- Tô đậm `**số liệu quan trọng**`
- Kết thúc bằng gợi ý câu hỏi tiếp theo:
  `<suggestions>Câu hỏi 1?|Câu hỏi 2?|Câu hỏi 3?</suggestions>`

---
NHẮC LẠI LẦN CUỐI: TRẢ LỜI BẰNG TIẾNG VIỆT. KHÔNG DÙNG TIẾNG ANH.
"""


def _build_system_prompt() -> str:
    """
    Tổng hợp system prompt hoàn chỉnh theo pattern:
        [ROLE] → [CIRCUMSTANCE (CSV + Dashboard + KB + Notebooks)]

    data_context.py là nguồn duy nhất của sự thật về dữ liệu.
    Nó đã xử lý: schema CSV, knowledge base tính sẵn, dashboard insights 5 tab, notebook list.
    """
    data_path = get_data_file_path()
    load_snippet = (
        f"df = pd.read_csv(r'{data_path}', low_memory=False, encoding='utf-8-sig')"
        if data_path
        else "df = pd.read_csv('<đường_dẫn_file_csv>', low_memory=False)"
    )

    circumstance_header = f"""\
# [CIRCUMSTANCE — NGỮ CẢNH DỮ LIỆU CSV]
> ⚠️ Đây là thông tin THỰC TẾ được đọc tự động từ file CSV lúc server khởi động.
> Chỉ dùng đúng tên cột, kiểu dữ liệu và đường dẫn được liệt kê bên dưới.

**Load dataset:**
```python
import pandas as pd
{load_snippet}
```
"""
    context_card = build_data_context_card()
    parts = [_ROLE_BLOCK, circumstance_header, context_card]
    return "\n".join(p for p in parts if p)


# --- Fallback keys từ .env (dùng khi Admin UI chưa cấu hình) ---
_ENV_GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
_ENV_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
_ENV_GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

GROQ_MODELS = {"llama-3.3-70b-versatile", "llama-3.1-8b-instant"}
OPENAI_MODELS = {"gpt-4o-mini", "gpt-4o", "gpt-4.1-nano"}
GOOGLE_MODELS = {"gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-pro"}
OLLAMA_MODELS = {"llama3.2:3b", "llama3.2", "llama3.1", "qwen2.5:3b", "qwen2.5:1.5b", "qwen2.5:7b-instruct"}


def _extract_key(inference_config: Optional[dict], provider: str, env_fallback: str) -> str:
    """
    Lấy API key theo thứ tự ưu tiên:
    1. Key từ Admin UI (inferenceConfig gửi lên từ Frontend)
    2. Key từ biến môi trường .env
    """
    if inference_config:
        credentials = inference_config.get("credentials", {})
        key = (credentials.get(provider) or {}).get("apiKey", "").strip()
        if key:
            return key
    return env_fallback


def _build_llm(model: str, temperature: float, max_tokens: int, inference_config: Optional[dict] = None):
    """Tạo LLM instance đúng provider, ưu tiên key từ Admin UI rồi fallback sang .env."""
    from langchain_openai import ChatOpenAI

    if model in GROQ_MODELS:
        api_key = _extract_key(inference_config, "groq", _ENV_GROQ_API_KEY)
        if not api_key:
            raise ValueError("Groq API Key chưa được cấu hình. Vào Quản trị → Cấu hình AI để nhập key.")
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=60,
        )

    if model in OPENAI_MODELS:
        api_key = _extract_key(inference_config, "openai", _ENV_OPENAI_API_KEY)
        if not api_key:
            raise ValueError("OpenAI API Key chưa được cấu hình. Vào Quản trị → Cấu hình AI để nhập key.")
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=60,
        )

    if model in GOOGLE_MODELS:
        api_key = _extract_key(inference_config, "google", _ENV_GOOGLE_API_KEY)
        if not api_key:
            raise ValueError("Google API Key chưa được cấu hình. Vào Quản trị → Cấu hình AI để nhập key.")
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=model,
                google_api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=60,
            )
        except ImportError:
            # Fallback nếu chưa cài langchain-google-genai
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=60,
            )

    if model in OLLAMA_MODELS:
        return ChatOpenAI(
            model=model,
            api_key="ollama",  # dummy key
            base_url="http://localhost:11434/v1",
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=120,
        )

    raise ValueError(f"Model '{model}' không được hỗ trợ. Chọn một trong: Groq, OpenAI, Google, Ollama.")


def _friendly_error(exc: Exception) -> str:
    """Trả về thông báo lỗi thân thiện cho người dùng."""
    text = str(exc)
    lower = text.lower()
    if "rate_limit_exceeded" in lower or "429" in lower or "rate limit" in lower:
        return (
            "⚠️ Đã đạt giới hạn tốc độ (Rate Limit) của model này. "
            "Vui lòng chờ ~30 giây rồi thử lại, hoặc chuyển sang model khác "
            "(ví dụ: mixtral-8x7b-32768) trong phần Cấu hình AI."
        )
    if "401" in lower or "invalid api key" in lower or "authentication" in lower:
        return "❌ API Key không hợp lệ. Vui lòng kiểm tra lại trong phần Quản trị → Cấu hình AI."
    if "quota" in lower or "insufficient_quota" in lower:
        return "❌ Tài khoản API đã hết hạn mức. Vui lòng kiểm tra số dư tài khoản của bạn."
    if "chưa được cấu hình" in text:
        return f"⚙️ {text}"
    return f"❌ Lỗi AI: {text}"


class AnalysisChatMessage(BaseModel):
    role: str
    content: str


class AnalysisChatRequest(BaseModel):
    messages: list[AnalysisChatMessage]
    model: str = "llama-3.3-70b-versatile"
    session_id: str = "unknown"
    session_title: str = "Cuộc trò chuyện mới"
    streaming: bool = True
    temperature: float = 0.3
    max_tokens: int = 4096
    # Nhận inferenceConfig từ Frontend (chứa API keys từ Admin UI)
    inferenceConfig: Optional[dict] = None


async def _persist_analysis_turn(
    session_id: str,
    session_title: str,
    user_content: str,
    ai_content: str,
    user_id: Optional[str],
) -> None:
    """Lưu lượt hội thoại vào PostgreSQL (cùng bảng với chat RAG)."""
    try:
        from app.config import CHAT_STORAGE_MODE
        if CHAT_STORAGE_MODE != "postgres" or session_id == "unknown":
            return
        from app.services.storage import ensure_session_exists, save_chat_message
        user_msg_id = str(_uuid.uuid4())
        ai_msg_id = str(_uuid.uuid4())
        user_time = datetime.utcnow()
        from datetime import timedelta
        ai_time = user_time + timedelta(milliseconds=10)
        await asyncio.to_thread(ensure_session_exists, session_id, session_title, user_id)
        await asyncio.to_thread(save_chat_message, session_id, user_msg_id, "user", user_content, [], user_time)
        await asyncio.to_thread(save_chat_message, session_id, ai_msg_id, "assistant", ai_content, [], ai_time)
        logger.info("Persisted analysis turn for session %s (user_id=%s)", session_id, user_id)
    except Exception as exc:
        logger.warning("Failed to persist analysis turn for session %s: %s", session_id, exc)


@router.post("/chat/stream")
async def analysis_chat_stream(
    request: AnalysisChatRequest,
    http_request: Request,
    user_id: Optional[str] = Depends(get_current_user_id),
) -> StreamingResponse:
    """
    Endpoint chat streaming cho module phân tích dữ liệu.
    Tách biệt hoàn toàn với /chat/stream của RAG.

    Cơ chế Agentic ReAct Loop:
    - Phase A (ẩn với user): LLM quyết định → gọi tool → nhận kết quả → lặp tối đa MAX_TOOL_ROUNDS vòng
    - Phase B (stream): Khi đủ dữ liệu → stream câu trả lời cuối cùng cho user

    Lưu session vào PostgreSQL nếu CHAT_STORAGE_MODE=postgres.
    """
    async def generate() -> AsyncGenerator[str, None]:
        full_text = ""
        user_content = request.messages[-1].content if request.messages else ""

        import pathlib
        from langchain_core.tools import tool

        # ─── TOOL DEFINITIONS ─────────────────────────────────────────────────

        @tool
        async def scrape_car_data(url: str, output_file: str = None) -> str:
            """Sử dụng công cụ này khi người dùng gửi link xe (oto.com.vn, bonbanh.com, caranddriver.com...)
            để cào thông tin chi tiết xe và tùy chọn lưu ra file theo yêu cầu người dùng.

            Args:
                url: URL trang xe cần cào dữ liệu
                output_file: Đường dẫn file để lưu thông tin xe (VD: 'report/xe_info.json' hoặc 'docs/porsche.csv'). Để None nếu chỉ muốn xem dữ liệu.
            """
            try:
                import sys
                import subprocess as _subprocess
                import tempfile
                from app.services.file_manager import validate_path, FileSecurityError

                this_dir = pathlib.Path(__file__).resolve().parent  # web/backend/app/api/
                script_path = (this_dir / "../../../../scraping_agent/main.py").resolve()
                scraping_agent_dir = script_path.parent

                env = os.environ.copy()
                llm_arg = "auto"
                if request.inferenceConfig and "groq" in request.inferenceConfig:
                    env["GROQ_API_KEY"] = request.inferenceConfig["groq"]
                    llm_arg = "groq"
                elif request.inferenceConfig and "openai" in request.inferenceConfig:
                    env["OPENAI_API_KEY"] = request.inferenceConfig["openai"]
                    llm_arg = "openai"
                elif request.inferenceConfig and "google" in request.inferenceConfig:
                    env["GOOGLE_API_KEY"] = request.inferenceConfig["google"]
                    llm_arg = "google"

                # Determine output path and format
                save_to_user_path = False
                if output_file:
                    try:
                        target_p = validate_path(output_file)
                        target_p.parent.mkdir(parents=True, exist_ok=True)
                        tmp_path = str(target_p)
                        save_to_user_path = True
                    except FileSecurityError as se:
                        return f"Lỗi bảo mật khi lưu file: {se}"
                else:
                    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
                        tmp_path = tmp.name

                fmt_arg = "csv" if output_file and output_file.lower().endswith(".csv") else "json"

                def _run_scraper():
                    return _subprocess.run(
                        [sys.executable, str(script_path), url,
                         "--format", fmt_arg,
                         "--output", tmp_path,
                         "--llm", llm_arg,
                         "--headless"],
                        capture_output=True,
                        timeout=85,
                        cwd=str(scraping_agent_dir),
                        env=env,
                    )

                loop = asyncio.get_event_loop()
                try:
                    result = await asyncio.wait_for(
                        loop.run_in_executor(None, _run_scraper),
                        timeout=90.0,
                    )
                except asyncio.TimeoutError:
                    return "Lỗi: Quá trình cào dữ liệu bị timeout sau 90 giây. Hãy nhắc người dùng thử lại."

                exit_code = result.returncode
                stderr_text = result.stderr.decode("utf-8", errors="replace").strip() if result.stderr else ""
                stdout_text = result.stdout.decode("utf-8", errors="replace").strip() if result.stdout else ""

                if not os.path.exists(tmp_path) or exit_code != 0:
                    detail = stderr_text[:400] or stdout_text[:400] or "Không có thông tin lỗi."
                    logger.error("[scrape_tool] FAILED exit=%s detail=%s", exit_code, detail)
                    return f"Lỗi: Agent cào thất bại (exit={exit_code}). Chi tiết: {detail}"

                with open(tmp_path, "r", encoding="utf-8") as f:
                    data = f.read()

                if not save_to_user_path:
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass

                if not data.strip():
                    return "Lỗi: Dữ liệu cào từ trang web bị trống, có thể link không hợp lệ hoặc bị chặn."

                msg_parts = []
                if save_to_user_path:
                    msg_parts.append(f"✅ **Đã kích hoạt Scraping Agent và lưu thông tin xe vào file thành công!**\n- **URL:** `{url}`\n- **File lưu:** `{output_file}`")

                trimmed_data = data[:10000] + "\n... [Dữ liệu đã được rút gọn để hiển thị]" if len(data) > 10000 else data
                msg_parts.append(f"📋 **Dữ liệu chi tiết cào được:**\n\n```json\n{trimmed_data}\n```")

                logger.info("[scrape_tool] OK url=%s save_user=%s len=%s", url, save_to_user_path, len(data))
                return "\n\n".join(msg_parts)
            except Exception as e:
                logger.error("[scrape_tool] EXCEPTION %s: %s", type(e).__name__, e)
                return f"Lỗi khi cào dữ liệu: {type(e).__name__}: {str(e)}"

        @tool
        async def query_dataset_readonly(code: str) -> str:
            """Chạy mã Python/Pandas để lấy số liệu chi tiết từ CSV (33,848 dòng).
            Chạy NGẦM — chỉ trả về kết quả text, không hiển thị code.

            ⛔ KHÔNG DÙNG tool này cho câu hỏi về dashboard/tab/biểu đồ/KPI dashboard.
            ⛔ Cho dashboard/tab → Gọi tool get_dashboard_info(tab) thay thế.
            ✅ Dùng tool này CHỈ KHI: cần số liệu CSV chi tiết (filter, group by, top-N...)

            Args:
                code: Đoạn mã Python hợp lệ. Bắt buộc dùng lệnh print() để hiển thị kết quả.
                      Biến `df` (dataframe chính, 33,848 dòng) đã được tự động load sẵn.
                      Tên cột chính xác: 'Hãng', 'Dòng xe', 'Giá (triệu VND)', 'Năm sản xuất',
                      'Số Km đã đi (km)', 'Loại nhiên liệu', 'Hộp số', 'Tình trạng',
                      'Xuất xứ', 'Màu ngoại thất', 'Số chỗ ngồi sạch', v.v.
            """
            import io
            import sys

            # Sandbox cơ bản
            forbidden = ["os.", "sys.", "subprocess", "__import__"]
            code_no_space = code.replace(" ", "")
            for f_kw in forbidden:
                if f_kw in code_no_space:
                    return f"Lỗi: Không được phép sử dụng lệnh can thiệp hệ thống ({f_kw})."

            try:
                import pandas as pd
                import numpy as np

                # Dùng DataFrame từ cache (0ms) thay vì đọc lại CSV 25MB (~3-5s)
                cached_df = _get_cached_df()
                if cached_df is None:
                    return "Lỗi: Không tìm thấy hoặc không load được file dữ liệu CSV."

                local_env = {"pd": pd, "np": np}
                local_env["df"] = cached_df.copy()  # .copy() để exec code không làm hỏng cache

                stdout_buf = io.StringIO()
                old_stdout = sys.stdout
                sys.stdout = stdout_buf
                try:
                    exec(code, local_env)  # noqa: S102
                finally:
                    sys.stdout = old_stdout

                result = stdout_buf.getvalue()
                if not result.strip():
                    return "Đã chạy thành công nhưng không có kết quả in ra. Hãy chắc chắn dùng print()."
                return f"Kết quả từ dữ liệu:\n{result}"
            except Exception as e:
                return f"Lỗi khi thực thi code: {type(e).__name__}: {str(e)}"

        # ─── FILE MANAGEMENT TOOLS ────────────────────────────────────────────


        @tool
        async def get_dashboard_info(tab: str = "all") -> str:
            """Lấy thông tin chi tiết từ Dashboard.json về tab/dashboard.
            Gọi tool này cho MỌI câu hỏi về dashboard, tab, biểu đồ, KPI dashboard.

            Args:
                tab: Tab cần lấy. Giá trị hợp lệ:
                     "Tab1" - Bức tranh thị trường (KPI tổng quan, hãng xe, dòng xe, năm SX)
                     "Tab2" - Giải mã giá xe (phân phối giá, xu hướng, xe đắt nhất/rẻ nhất)
                     "Tab3" - Cuộc chiến Xăng vs Điện (thị phần, tăng trưởng xe điện)
                     "Tab4" - Chân dung người mua (số chỗ, màu sắc, hộp số ưa chuộng)
                     "Tab5" - Góc khuất thị trường (xe đặc biệt, biên độ giá, top đắt/rẻ)
                     "all"  - Toàn bộ 5 tab
            """
            # Dùng cache module-level thay vì đọc file mỗi lần (0ms vs ~50-200ms I/O)
            dash = _get_dashboard_data()
            if not dash:
                return "Lỗi: Không tìm thấy hoặc không đọc được Dashboard.json."

            def _fmt_tab(tab_key, tab_data):
                charts = tab_data.get("charts", {})
                tab_names = {
                    "Tab1": "TAB 1 — BỨC TRANH THỊ TRƯỜNG",
                    "Tab2": "TAB 2 — GIẢI MÃ GIÁ XE",
                    "Tab3": "TAB 3 — CUỘC CHIẾN XĂNG vs ĐIỆN",
                    "Tab4": "TAB 4 — CHÂN DUNG NGƯỜI MUA",
                    "Tab5": "TAB 5 — GÓC KHUẤT THỊ TRƯỜNG",
                }
                out = [f"## {tab_names.get(tab_key, tab_key)}", ""]

                for chart_key, chart_data in charts.items():
                    data_rows = chart_data.get("data", [])
                    if not data_rows:
                        continue
                    out.append(f"### {chart_key}")
                    # KPI (single value)
                    if len(data_rows) == 1 and len(data_rows[0]) <= 2:
                        vals = list(data_rows[0].values())
                        out.append(f"**{vals[-1]}**")
                    else:
                        # Table
                        if data_rows:
                            headers = list(data_rows[0].keys())
                            out.append("| " + " | ".join(str(h) for h in headers) + " |")
                            out.append("|" + "|".join("---" for _ in headers) + "|")
                            for row in data_rows[:20]:
                                out.append("| " + " | ".join(str(v) for v in row.values()) + " |")
                    out.append("")

                return "\n".join(out)

            result_parts = []
            try:
                # ── "overview": compact KPI của tất cả 5 tab (~800 tokens, nhanh hơn "all") ──
                if tab in ("overview", "all_compact"):
                    kpi_lines = ["# TỔNG QUAN DASHBOARD — 5 TAB", ""]
                    tab_titles = {
                        "Tab1": "📊 Tab1 — Bức Tranh Thị Trường",
                        "Tab2": "💰 Tab2 — Giải Mã Giá Xe",
                        "Tab3": "⚡ Tab3 — Xăng vs Điện",
                        "Tab4": "👥 Tab4 — Chân Dung Người Mua",
                        "Tab5": "🔍 Tab5 — Góc Khuất Thị Trường",
                    }
                    for tk, title in tab_titles.items():
                        if tk not in dash:
                            continue
                        charts = dash[tk].get("charts", {})
                        kpi_lines.append(f"## {title}")
                        for chart_key, chart_data in charts.items():
                            rows = chart_data.get("data", [])
                            if not rows:
                                continue
                            # Chỉ lấy KPI (1 giá trị) và top-3 của bảng
                            if len(rows) == 1:
                                vals = list(rows[0].values())
                                kpi_lines.append(f"- **{chart_key}**: {vals[-1]}")
                            elif len(rows) <= 10:
                                headers = list(rows[0].keys())
                                kpi_lines.append(f"- **{chart_key}** ({len(rows)} dòng): " +
                                    " | ".join(f"{k}={v}" for k, v in list(rows[0].items())[:3]))
                        kpi_lines.append("")
                    return "\n".join(kpi_lines)

                elif tab == "all":
                    for tk in ["Tab1", "Tab2", "Tab3", "Tab4", "Tab5"]:
                        if tk in dash:
                            result_parts.append(_fmt_tab(tk, dash[tk]))
                else:
                    # Normalize tab name
                    tab_norm = tab.strip().replace(" ", "").replace("tab", "Tab")
                    if not tab_norm.startswith("Tab"):
                        tab_norm = "Tab" + tab_norm
                    if tab_norm in dash:
                        result_parts.append(_fmt_tab(tab_norm, dash[tab_norm]))
                    else:
                        # Try to find partial match
                        for tk in dash.keys():
                            if tab.lower() in tk.lower():
                                result_parts.append(_fmt_tab(tk, dash[tk]))
                        if not result_parts:
                            result_parts.append(f"Không tìm thấy tab '{tab}'. Các tab có sẵn: Tab1, Tab2, Tab3, Tab4, Tab5, overview")
            except Exception as _e:
                return f"Lỗi xử lý Dashboard.json: {_e}"

            return "\n\n".join(result_parts) if result_parts else "Không có dữ liệu."

        @tool
        async def read_file_content(file_path: str) -> str:
            """Đọc nội dung file text (CSV, JSON, TXT, PY, MD, IPYNB...).
            Sử dụng khi người dùng yêu cầu xem nội dung một file cụ thể.

            Args:
                file_path: Đường dẫn tuyệt đối hoặc tương đối file cần đọc
            """
            from app.services import file_manager
            result = file_manager.read_file_content(file_path)
            if result["success"]:
                content = result["content"]
                if len(content) > 5000:
                    content = content[:5000] + f"\n\n... ({len(content) - 5000} ký tự còn lại)"
                return (
                    f"📄 **File:** {file_path}\n"
                    f"📊 **Size:** {result['size_bytes']} bytes | **Lines:** {result['lines']}\n\n"
                    f"```\n{content}\n```"
                )
            else:
                return f"❌ **Lỗi đọc file:** {result['error']}"

        @tool
        async def list_files(directory: str, pattern: str = "*", recursive: bool = False) -> str:
            """Liệt kê files trong thư mục.
            Sử dụng khi người dùng hỏi "có những file nào trong thư mục X?".

            Args:
                directory: Đường dẫn thư mục cần liệt kê
                pattern: Glob pattern (ví dụ: "*.csv", "report_*")
                recursive: Có tìm kiếm đệ quy không (default: False)
            """
            from app.services import file_manager
            result = file_manager.list_files(directory, pattern, recursive)
            if result["success"]:
                files = result["files"]
                if not files:
                    return f"📁 **Thư mục:** {directory}\n🔍 **Pattern:** {pattern}\n\n⚠️ Không tìm thấy file nào."
                lines = [
                    f"📁 **Thư mục:** {directory}",
                    f"🔍 **Pattern:** {pattern}",
                    f"📊 **Tổng:** {result['count']} files\n",
                    "| Tên file | Size | Type |",
                    "|----------|------|------|",
                ]
                for f in files[:20]:
                    size_kb = f["size"] / 1024
                    lines.append(f"| {f['name']} | {size_kb:.1f}KB | {f['type']} |")
                if len(files) > 20:
                    lines.append(f"\n... và {len(files) - 20} files khác")
                return "\n".join(lines)
            else:
                return f"❌ **Lỗi liệt kê files:** {result['error']}"

        @tool
        async def create_file(file_path: str, content: str, overwrite: bool = False) -> str:
            """Tạo file mới. YÊU CẦU PHÊ DUYỆT từ người dùng.
            Chỉ sử dụng khi người dùng ĐÚNG YÊU CẦU "tạo file X với nội dung Y".

            Args:
                file_path: Đường dẫn file cần tạo
                content: Nội dung file
                overwrite: Ghi đè nếu file đã tồn tại (default: False)
            """
            from app.services import file_manager
            from app.services.approval_workflow import (
                get_approval_manager, generate_preview, should_require_approval,
            )
            manager = get_approval_manager()
            arguments = {"file_path": file_path, "content": content, "overwrite": overwrite}
            preview = generate_preview("create_file", arguments)
            action = manager.create_action(
                session_id=request.session_id,
                tool_name="create_file",
                arguments=arguments,
                preview=preview,
            )
            if should_require_approval(action.risk_level):
                return (
                    f"**Yêu cầu phê duyệt tạo file**\n\n"
                    f"**File:** `{file_path}`\n"
                    f"**Size:** {len(content)} bytes\n"
                    f"**Risk Level:** {action.risk_level.value}\n\n"
                    f"Vui lòng phê duyệt thao tác này để tiếp tục.\n\n"
                    f"**Action ID:** `{action.action_id}`"
                )
            else:
                manager.approve_action(action.action_id)
                result = file_manager.create_file(**arguments)
                manager.mark_executed(action.action_id, result, success=result["success"])
                if result["success"]:
                    return f"**Đã tạo file:** {file_path} ({result['size_bytes']} bytes)"
                else:
                    return f"**Lỗi tạo file:** {result['error']}"

        @tool
        async def modify_file(
            file_path: str,
            operation: str,
            content: str = "",
            line_number: int = None,
            search_text: str = None,
        ) -> str:
            """Sửa file hiện có. YÊU CẦU PHÊ DUYỆT từ người dùng.
            Chỉ sử dụng khi người dùng YÊU CẦU "sửa file X" hoặc "thêm nội dung vào file Y".

            Args:
                file_path: Đường dẫn file cần sửa
                operation: "append" (thêm cuối), "replace" (thay thế), "insert" (chèn), "delete_line" (xóa dòng)
                content: Nội dung mới (cho append/replace/insert)
                line_number: Số dòng (cho insert/delete_line, bắt đầu từ 1)
                search_text: Text cần tìm (cho replace)
            """
            from app.services import file_manager
            from app.services.approval_workflow import (
                get_approval_manager, generate_preview, should_require_approval,
            )
            # Pre-check existence on disk
            try:
                check_p = file_manager.validate_path(file_path)
                if not check_p.exists() or not check_p.is_file():
                    return f"Lỗi: File không tồn tại trên ổ đĩa: `{file_path}`. Không thể chỉnh sửa."
            except Exception as check_err:
                return f"Lỗi kiểm tra file: {check_err}"

            manager = get_approval_manager()
            arguments = {
                "file_path": file_path, "operation": operation,
                "content": content, "line_number": line_number, "search_text": search_text,
            }
            preview = generate_preview("modify_file", arguments)
            action = manager.create_action(
                session_id=request.session_id,
                tool_name="modify_file",
                arguments=arguments,
                preview=preview,
            )
            if should_require_approval(action.risk_level):
                return (
                    f"**Yêu cầu phê duyệt sửa file**\n\n"
                    f"**File:** `{file_path}`\n"
                    f"**Operation:** {operation}\n"
                    f"**Risk Level:** {action.risk_level.value}\n\n"
                    f"Vui lòng phê duyệt thao tác này để tiếp tục.\n\n"
                    f"**Action ID:** `{action.action_id}`"
                )
            else:
                manager.approve_action(action.action_id)
                result = file_manager.modify_file(**arguments)
                manager.mark_executed(action.action_id, result, success=result["success"])
                if result["success"]:
                    return f"**Đã sửa file:** {file_path} ({result['lines_affected']} dòng bị ảnh hưởng)"
                else:
                    return f"**Lỗi sửa file:** {result['error']}"

        @tool
        async def delete_file(file_path: str) -> str:
            """Xóa file. YÊU CẦU PHÊ DUYỆT 2 LẦN từ người dùng (CRITICAL operation).
            CHỈ sử dụng khi người dùng CHÍNH THỨC YÊU CẦU "xóa file X" và XÁC NHẬN lại.

            Args:
                file_path: Đường dẫn file cần xóa
            """
            from app.services import file_manager
            from app.services.approval_workflow import (
                get_approval_manager, generate_preview,
            )
            # Pre-check existence on disk
            try:
                check_p = file_manager.validate_path(file_path)
                if not check_p.exists() or not check_p.is_file():
                    return f"Lỗi: File không tồn tại trên ổ đĩa: `{file_path}`. Không thể thực hiện xóa."
            except Exception as check_err:
                return f"Lỗi kiểm tra file: {check_err}"

            manager = get_approval_manager()
            arguments = {"file_path": file_path, "force": False}
            preview = generate_preview("delete_file", arguments)
            action = manager.create_action(
                session_id=request.session_id,
                tool_name="delete_file",
                arguments=arguments,
                preview=preview,
            )
            return (
                f"**YÊU CẦU PHÊ DUYỆT XÓA FILE (CRITICAL)**\n\n"
                f"**File:** `{file_path}`\n"
                f"**Cảnh báo:** Thao tác này KHÔNG THỂ HOÀN TÁC!\n\n"
                f"Vui lòng xác nhận 2 lần để tiếp tục.\n\n"
                f"**Action ID:** `{action.action_id}`"
            )

        @tool
        async def move_rename_file(source: str, destination: str, overwrite: bool = False) -> str:
            """Di chuyển hoặc đổi tên file. YÊU CẦU PHÊ DUYỆT từ người dùng.
            Sử dụng khi người dùng YÊU CẦU "đổi tên file X" hoặc "di chuyển file Y".

            Args:
                source: Đường dẫn file nguồn
                destination: Đường dẫn file đích
                overwrite: Ghi đè nếu file đích đã tồn tại (default: False)
            """
            from app.services import file_manager
            from app.services.approval_workflow import (
                get_approval_manager, generate_preview, should_require_approval,
            )
            # Pre-check existence on disk
            try:
                check_p = file_manager.validate_path(source)
                if not check_p.exists() or not check_p.is_file():
                    return f"Lỗi: File nguồn không tồn tại trên ổ đĩa: `{source}`. Không thể di chuyển/đổi tên."
            except Exception as check_err:
                return f"Lỗi kiểm tra file: {check_err}"
            manager = get_approval_manager()
            arguments = {"source": source, "destination": destination, "overwrite": overwrite}
            preview = generate_preview("move_rename_file", arguments)
            action = manager.create_action(
                session_id=request.session_id,
                tool_name="move_rename_file",
                arguments=arguments,
                preview=preview,
            )
            if should_require_approval(action.risk_level):
                return (
                    f"**Yêu cầu phê duyệt di chuyển/đổi tên file**\n\n"
                    f"**From:** `{source}`\n"
                    f"**To:** `{destination}`\n"
                    f"**Risk Level:** {action.risk_level.value}\n\n"
                    f"Vui lòng phê duyệt thao tác này để tiếp tục.\n\n"
                    f"**Action ID:** `{action.action_id}`"
                )
            else:
                manager.approve_action(action.action_id)
                result = file_manager.move_rename_file(**arguments)
                manager.mark_executed(action.action_id, result, success=result["success"])
                if result["success"]:
                    return f"✅ **Đã di chuyển/đổi tên file:** {source} → {destination}"
                else:
                    return f"❌ **Lỗi di chuyển/đổi tên file:** {result['error']}"

        # ─── ROLLBACK & HISTORY TOOLS ─────────────────────────────────────────

        @tool
        async def rollback_last_change(file_path: str = None, target_backup: str = None) -> str:
            """Hoàn tác thay đổi gần nhất hoặc hoàn tác về phiên bản backup cụ thể của một file.
            Sử dụng khi người dùng yêu cầu "undo", "hoàn tác", "rollback file X", "hoàn tác về bản backup Y.bak".

            Args:
                file_path: Đường dẫn file cần rollback (VD: docs/test_chart.py)
                target_backup: Tên file backup hoặc timestamp cụ thể (VD: 2026-07-24_11-30-38-350901_test_chart.py.bak)
            """
            from app.services import backup_service
            result = backup_service.rollback_last_change(file_path=file_path, target_backup=target_backup)
            if result["success"]:
                return (
                    f"Đã hoàn tác thay đổi thành công!\n\n"
                    f"File: `{result['restored_file']}`\n"
                    f"Bản sao lưu đã dùng: `{result['backup_used']}`\n"
                    f"Thời điểm backup: {result['timestamp']}\n\n"
                    f"File đã được phục hồi về trạng thái này."
                )
            else:
                return f"Lỗi khi hoàn tác: {result['error']}"

        @tool
        async def show_change_history(file_path: str, limit: int = 10) -> str:
            """Hiển thị lịch sử thay đổi của một file.
            Sử dụng khi người dùng hỏi "lịch sử thay đổi file X", "file X đã được sửa bao nhiêu lần".

            Args:
                file_path: Đường dẫn file cần xem lịch sử
                limit: Số lượng changes tối đa hiển thị (default: 10)
            """
            from app.services import backup_service
            result = backup_service.get_change_history(file_path, limit)
            if result["success"]:
                changes = result["changes"]
                if not changes:
                    return f"📄 **File:** `{file_path}`\n\n⚠️ Không tìm thấy lịch sử thay đổi."
                lines = [
                    f"📄 **File:** `{file_path}`",
                    f"📊 **Tổng số thay đổi:** {result['total']}",
                    f"📋 **Hiển thị:** {len(changes)} thay đổi gần nhất\n",
                    "| Thời gian | Thao tác | Size | Backup Path |",
                    "|-----------|----------|------|-------------|",
                ]
                for change in changes:
                    backup_name = change["backup_path"].split("\\")[-1]
                    lines.append(
                        f"| {change['timestamp']} | {change['operation']} | "
                        f"{change['original_size']} bytes | {backup_name} |"
                    )
                return "\n".join(lines)
            else:
                return f"❌ **Lỗi:** {result['error']}"

        @tool
        async def list_all_backups(limit: int = 20) -> str:
            """Liệt kê tất cả backups hiện có.
            Sử dụng khi người dùng hỏi "có những backup nào", "liệt kê backups".

            Args:
                limit: Số lượng backups tối đa hiển thị (default: 20)
            """
            from app.services import backup_service
            result = backup_service.list_all_backups(limit)
            if result["success"]:
                backups = result["backups"]
                if not backups:
                    return "📦 **Backup Directory**\n\n⚠️ Chưa có backup nào."
                lines = [
                    f"📦 **Tổng số backups:** {result['total']}",
                    f"📋 **Hiển thị:** {len(backups)} backups gần nhất\n",
                    "| Filename | Size | Created |",
                    "|----------|------|---------|",
                ]
                for backup in backups:
                    size_kb = backup["size"] / 1024
                    created = backup["created"].split("T")[0]
                    lines.append(f"| {backup['filename']} | {size_kb:.1f}KB | {created} |")
                return "\n".join(lines)
            else:
                return f"❌ **Lỗi:** {result['error']}"

        @tool
        async def run_python_file(file_path: str) -> str:
            """Thực thi một file script Python (.py) trong dự án và trả về kết quả in ra màn hình hoặc hình ảnh biểu đồ.
            Sử dụng khi người dùng yêu cầu "chạy file X.py", "thực thi script Y.py", "chạy file script.py".

            Args:
                file_path: Đường dẫn file script Python cần chạy (VD: docs/script.py)
            """
            from app.services.file_manager import validate_path, FileSecurityError
            from app.api.execute import execute_code, ExecuteRequest
            try:
                path = validate_path(file_path)
                if not path.exists() or not path.is_file():
                    return f"Lỗi: File không tồn tại: {file_path}"
                with open(path, "r", encoding="utf-8") as f:
                    code = f.read()

                exec_res = await execute_code(ExecuteRequest(code=code, session_id=request.session_id))
                output_parts = [f"**Kết quả thực thi file `{file_path}`:**\n"]
                if exec_res.stdout:
                    output_parts.append(f"```text\n{exec_res.stdout.strip()}\n```")
                if exec_res.error or exec_res.stderr:
                    output_parts.append(f"**Cảnh báo / Lỗi:**\n```text\n{(exec_res.error or exec_res.stderr).strip()}\n```")
                if exec_res.images:
                    output_parts.append(f"Đã vẽ và hiển thị {len(exec_res.images)} biểu đồ từ file script:")
                    for idx, img_b64 in enumerate(exec_res.images, 1):
                        output_parts.append(f"![Biểu đồ {idx}](data:image/png;base64,{img_b64})")

                if not exec_res.stdout and not exec_res.images and not exec_res.error:
                    output_parts.append("File đã thực thi thành công (không có đầu ra màn hình).")

                return "\n\n".join(output_parts)
            except FileSecurityError as se:
                return f"Lỗi bảo mật: {se}"
            except Exception as e:
                return f"Lỗi khi thực thi file {file_path}: {e}"

        # ─── PHASE 3: MULTI-STEP PLANNING ─────────────────────────────────────

        @tool
        async def plan_file_operations(task_description: str, steps: str) -> str:
            """Tạo kế hoạch thực hiện task phức tạp với nhiều bước.
            Sử dụng khi task yêu cầu nhiều file operations liên tiếp.

            Args:
                task_description: Mô tả tổng quan task (VD: "Làm sạch dữ liệu và xuất báo cáo")
                steps: JSON string chứa danh sách steps, format:
                       '[{"description": "...", "tool_name": "...", "arguments": {...}}, ...]'
            """
            from app.services import task_planner
            import json as json_lib
            try:
                steps_list = json_lib.loads(steps)
                result = task_planner.create_plan(task_description, steps_list)
                if result["success"]:
                    plan_id = result["plan_id"]
                    lines = [
                        f"📋 **Đã tạo kế hoạch thực hiện task**\n",
                        f"**Task:** {task_description}",
                        f"**Plan ID:** `{plan_id}`",
                        f"**Số bước:** {result['steps_count']}\n",
                        "**Chi tiết các bước:**",
                    ]
                    for step in result["plan"]["steps"]:
                        lines.append(
                            f"{step['step_id']}. {step['description']} "
                            f"(Tool: `{step['tool_name'] or 'N/A'}`)"
                        )
                    lines.append("\n✅ Kế hoạch đã được tạo. Bạn có muốn tôi thực hiện không?")
                    return "\n".join(lines)
                else:
                    return f"❌ **Lỗi tạo kế hoạch:** {result['error']}"
            except json_lib.JSONDecodeError:
                return "❌ **Lỗi:** `steps` phải là JSON string hợp lệ"
            except Exception as e:
                return f"❌ **Lỗi:** {str(e)}"

        @tool
        async def get_plan_status(plan_id: str) -> str:
            """Kiểm tra trạng thái thực hiện của một plan.
            Sử dụng khi người dùng hỏi "plan X đã thực hiện đến đâu?", "tiến độ plan Y".

            Args:
                plan_id: Plan ID cần kiểm tra
            """
            from app.services import task_planner
            result = task_planner.get_plan_summary(plan_id)
            if result["success"]:
                return (
                    f"📊 **Trạng thái Plan:** `{plan_id}`\n\n"
                    f"**Task:** {result['task_description']}\n"
                    f"**Tổng số bước:** {result['total_steps']}\n"
                    f"**Đã hoàn thành:** {result['completed_steps']}\n"
                    f"**Thất bại:** {result['failed_steps']}\n"
                    f"**Tiến độ:** {result['progress_percent']}%\n"
                    f"**Trạng thái:** {'✅ Hoàn thành' if result['is_completed'] else '⏳ Đang thực hiện'}\n"
                    f"**Thời gian:** {result.get('duration_seconds', 0):.2f}s"
                )
            else:
                return f"❌ **Lỗi:** {result['error']}"

        # ─── AGENTIC REACT LOOP ───────────────────────────────────────────────
        # Cơ chế đúng:
        #   Phase A (ẩn): LLM.ainvoke() → nếu có tool_calls → thực thi → lặp (tối đa MAX_TOOL_ROUNDS)
        #   Phase B (stream): Khi LLM không còn tool_calls → stream câu trả lời cuối cho user
        #
        # Khác với cũ (sai): stream ngay từ Pass 1 → token "suy nghĩ" lọt ra user
        # ─────────────────────────────────────────────────────────────────────

        MAX_TOOL_ROUNDS = 5  # Giới hạn số vòng tool để tránh loop vô hạn

        try:
            llm = _build_llm(request.model, request.temperature, request.max_tokens, request.inferenceConfig)
            tools_list = [
                scrape_car_data, query_dataset_readonly, get_dashboard_info,
                read_file_content, list_files, create_file, modify_file,
                delete_file, move_rename_file, rollback_last_change,
                show_change_history, list_all_backups, run_python_file, plan_file_operations,
                get_plan_status,
            ]
            available_tools = {t.name: t for t in tools_list}
            llm_with_tools = llm.bind_tools(tools_list)

            from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
            import re as _re

            current_system_prompt = _build_system_prompt()
            lc_messages = [SystemMessage(content=current_system_prompt)]
            for msg in request.messages:
                if msg.role == "user": lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant": lc_messages.append(AIMessage(content=msg.content))

            def _detect_direct_tool(msg: str):
                m = msg.lower()

                # 🟢 0. ƯU TIÊN HÀNG ĐẦU: Cào dữ liệu từ URL (Scraping Agent)
                import re as _re_scrape
                url_match = _re_scrape.search(r'https?://[^\s>"\']+', msg)
                if url_match or any(w in m for w in ["cào dữ liệu", "cào link", "scrape", "bonbanh.com", "oto.com.vn", "caranddriver.com"]):
                    extracted_url = url_match.group(0) if url_match else ""
                    if not extracted_url:
                        domain_match = _re_scrape.search(r'\b(?:bonbanh|oto|caranddriver)\.com[^\s>"\']*', msg)
                        if domain_match:
                            extracted_url = "https://" + domain_match.group(0)
                    if extracted_url:
                        out_match = _re_scrape.search(r'(?:lưu|lưu vào|file|out|output)\s+([a-zA-Z0-9_\-/\\]+\.(?:json|csv|txt))', msg, _re_scrape.IGNORECASE)
                        output_file_param = out_match.group(1) if out_match else None
                        return ("scrape_car_data", {"url": extracted_url, "output_file": output_file_param})

                # 🟢 0.1. YÊU CẦU VIẾT CODE NGAY TRÊN KHUNG CHAT (Interactive Code Block Stream)
                if any(w in m for w in ["viết code ngay trên khung chat", "viết cho tôi đoạn code", "viết code ngay", "viết code python", "cho tôi đoạn code", "viết code mẫu", "viết code"]):
                    if not any(w in m for w in ["tạo file", "sửa file", "xóa file", "đổi tên", "đọc file"]):
                        if any(w in m for w in ["tròn", "pie"]):
                            return ("prewarmed_cache", "code_sample_pie")
                        return ("prewarmed_cache", "code_sample")

                # 🟢 1. ƯU TIÊN CAO: Thống kê / Tính toán / Phân tích CSV thực tế (TẦNG 3)
                if _is_data_calculation_query(msg):
                    auto_code = _auto_generate_pandas_code(msg)
                    if auto_code:
                        return ("query_dataset_readonly", {"code": auto_code})

                # Các từ khóa thể hiện nhu cầu lấy DỮ LIỆU ĐẦY ĐỦ / BIỂU ĐỒ / BẢNG / CHI TIẾT (TẦNG 2)
                detail_kw = [
                    "tất cả", "chi tiết", "bảng", "biểu đồ", "kpi", "full", "dữ liệu",
                    "thông số", "con số", "bảng biểu", "liệt kê", "dữ liệu thô", "đầy đủ",
                    "trình bày gì", "có những gì", "gồm những gì", "nội dung đầy đủ", "chỉ số"
                ]
                is_detail_requested = any(kw in m for kw in detail_kw)

                # 🟡 2. Xử lý câu hỏi về TAB DASHBOARD (Tab 1 -> Tab 5)
                tab_matches = _re.findall(r'\btab\s*([1-5])\b', m)
                if tab_matches:
                    # Nếu hỏi nhiều tab cùng lúc (vd: "tab 1 và tab 2") -> Gọi get_dashboard_info(tab="all")
                    if len(set(tab_matches)) > 1:
                        return ("get_dashboard_info", {"tab": "all"})

                    t_key = f"Tab{tab_matches[0]}"

                    # Nếu hỏi chi tiết / biểu đồ / bảng / con số -> TẦNG 2 (get_dashboard_info)
                    if is_detail_requested:
                        return ("get_dashboard_info", {"tab": t_key})

                    # Nếu hỏi tóm tắt / xem nhanh / tổng quan -> TẦNG 1 (Prewarmed 0ms)
                    if any(kw in m for kw in ["tóm tắt", "tổng quan", "overview", "xem nhanh", "giới thiệu"]):
                        if t_key in _TAB_PREWARMED_CACHE:
                            return ("prewarmed_cache", t_key)

                    # Mặc định nếu hỏi về 1 Tab cụ thể mà không nói rõ -> Gọi get_dashboard_info (TẦNG 2) để đầy đủ
                    return ("get_dashboard_info", {"tab": t_key})

                # 🟡 3. Xử lý câu hỏi về NOTEBOOK
                if any(w in m for w in ["notebook", "jupyter", "tiền xử lý", "preprocessing", "eda"]):
                    # Nếu muốn đọc code thô / cell -> Bỏ qua prewarmed để LLM gọi read_file_content (TẦNG 2)
                    if any(w in m for w in ["cell", "code", "dòng code", "đọc file", "nội dung thô", "xem code"]):
                        return None
                    if any(w in m for w in ["01", "overview", "tổng quan"]):
                        return ("prewarmed_cache", "nb1")
                    if any(w in m for w in ["02", "tiền xử lý", "preprocessing", "làm sạch"]):
                        return ("prewarmed_cache", "nb2")
                    if any(w in m for w in ["03", "eda", "khám phá"]):
                        return ("prewarmed_cache", "nb3")
                    return ("prewarmed_cache", "notebook")

                # 🟡 4. Xử lý câu hỏi tổng quan DASHBOARD chung
                dash_kw = ["dashboard", "tổng quan dashboard", "bức tranh thị trường", "biểu đồ dashboard", "kpi dashboard"]
                if any(kw in m for kw in dash_kw):
                    if is_detail_requested or any(w in m for w in ["toàn bộ", "tất cả"]):
                        return ("get_dashboard_info", {"tab": "all"})
                    if any(w in m for w in ["giá xe", "giải mã giá", "tab2"]): return ("get_dashboard_info", {"tab": "Tab2"})
                    if any(w in m for w in ["xăng", "điện", "nhiên liệu", "tab3"]): return ("get_dashboard_info", {"tab": "Tab3"})
                    if any(w in m for w in ["người mua", "chân dung", "tab4"]): return ("get_dashboard_info", {"tab": "Tab4"})
                    if any(w in m for w in ["góc khuất", "đặc biệt", "tab5"]): return ("get_dashboard_info", {"tab": "Tab5"})
                    return ("prewarmed_cache", "overview")

                return None

            _pre_route = _detect_direct_tool(user_content)
            tool_round = 0
            _cache_key = _get_response_cache_key(user_content, request.model or "default")

            # ── Cache Hit: Câu hỏi lặp lại → stream ngay từ RAM ─────────────────
            _cached = _get_cached_response(_cache_key)
            if _cached:
                logger.info("[Cache] Hit: stream %d chars from cache", len(_cached))
                cache_notice = "*[⚡ Trả lời từ cache]*\n\n"
                full_text += cache_notice
                yield f"data: {json.dumps({'type': 'token', 'content': cache_notice})}\n\n"
                CHUNK, DELAY = 12, 0.008
                for i in range(0, len(_cached), CHUNK):
                    piece = _cached[i:i + CHUNK]
                    full_text += piece
                    yield f"data: {json.dumps({'type': 'token', 'content': piece})}\n\n"
                    await asyncio.sleep(DELAY)
                full_text = _cached  # Không lưu lại cache_notice vào history
                yield f"data: {json.dumps({'type': 'done', 'content': full_text})}\n\n"
                return  # Kết thúc generator ngay

            if _pre_route:
                tool_name_pr, tool_args_pr = _pre_route

                # ── 0ms TTFT Pre-Warmed Topic Cache Stream ───────────────────────
                if tool_name_pr == "prewarmed_cache":
                    t_key = str(tool_args_pr)
                    pre_content = _TAB_PREWARMED_CACHE.get(t_key, "")
                    if pre_content:
                        logger.info("[TopicCache] Pre-warmed hit for topic '%s', streaming 0ms TTFT from RAM", t_key)
                        CHUNK, DELAY = 12, 0.008
                        for i in range(0, len(pre_content), CHUNK):
                            piece = pre_content[i:i + CHUNK]
                            full_text += piece
                            yield f"data: {json.dumps({'type': 'token', 'content': piece})}\n\n"
                            await asyncio.sleep(DELAY)

                        _set_response_cache(_cache_key, pre_content)
                        yield f"data: {json.dumps({'type': 'done', 'content': full_text})}\n\n"
                        return

                # ── PRE-ROUTING: Gọi tool ngay + LLM synthesis stream ─────────────
                if tool_name_pr == "query_dataset_readonly":
                    status_msg = "\n\n*[⚙️ Đang tính toán dữ liệu thực tế từ 33,848 dòng CSV...]*\n\n"
                elif tool_name_pr == "scrape_car_data":
                    status_msg = "\n\n*[⚙️ Đang kích hoạt Scraping Agent để cào dữ liệu từ URL...]*\n\n"
                else:
                    status_msg = "\n\n*[⚙️ Đang tra cứu dữ liệu...]*\n\n"

                full_text += status_msg
                yield f"data: {json.dumps({'type': 'token', 'content': status_msg})}\n\n"

                try:
                    tool_result = await available_tools[tool_name_pr].ainvoke(tool_args_pr)
                except Exception as _te:
                    tool_result = f"Lỗi tool {tool_name_pr}: {_te}"

                if tool_name_pr in ("query_dataset_readonly", "scrape_car_data"):
                    # 1. Stream trực tiếp bảng / dữ liệu cào chuẩn
                    table_chunk = f"\n{tool_result}\n\n"
                    full_text += table_chunk
                    yield f"data: {json.dumps({'type': 'token', 'content': table_chunk})}\n\n"

                    if tool_name_pr == "scrape_car_data":
                        _set_response_cache(_cache_key, full_text)
                        yield f"data: {json.dumps({'type': 'done', 'content': full_text})}\n\n"
                        return  # Ngắt generator ngay lập tức!

                    # 2. Cho LLM nhận xét 2-3 câu ngắn gọn bên dưới bảng (không được tự bịa số)
                    synth_messages = [
                        SystemMessage(content=current_system_prompt),
                        HumanMessage(content=user_content),
                        AIMessage(content=str(tool_result)),
                        HumanMessage(content="[YÊU CẦU BẮT BUỘC: Bảng dữ liệu ở trên ĐÃ ĐƯỢC HIỂN THỊ ĐẦY ĐỦ. KHÔNG LẶP LẠI BẢNG VÀ KHÔNG THAY ĐỔI BẤT KỲ CON SỐ NÀO. Viết 2-3 câu nhận xét ngắn gọn bằng Tiếng Việt về xu hướng nổi bật từ dữ liệu trên.]")
                    ]
                    _pr_buf = ""
                    async for chunk in llm.astream(synth_messages):
                        token = getattr(chunk, "content", "")
                        if token:
                            _pr_buf += token
                            full_text += token
                            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

                    if full_text:
                        _set_response_cache(_cache_key, full_text)

                    yield f"data: {json.dumps({'type': 'done', 'content': full_text})}\n\n"
                    return  # Kết thúc generator

                _fake_id = "preroute-001"
                lc_messages.append(
                    AIMessage(content="", tool_calls=[{"name": tool_name_pr, "args": tool_args_pr, "id": _fake_id, "type": "tool_call"}])
                )
                _vi_prompt = (
                    "[YÊU CẦU BẮT BUỘC: Trả lời HOÀN TOÀN BẰNG TIẾNG VIỆT. "
                    "Tổng hợp ngắn gọn 4-5 thông tin quan trọng nhất từ dữ liệu bên dưới.]\n\n"
                )
                lc_messages.append(
                    ToolMessage(
                        content=_vi_prompt + str(tool_result),
                        tool_call_id=_fake_id
                    )
                )

                logger.info("[AgenticLoop] Pre-route tool executed: %s, streaming LLM synthesis...", tool_name_pr)
                _pr_buf = ""
                async for chunk in llm.astream(lc_messages):
                    token = ""
                    if hasattr(chunk, "content") and chunk.content:
                        token = chunk.content
                    if token:
                        _pr_buf += token
                        full_text += token
                        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

                if _pr_buf:
                    _set_response_cache(_cache_key, _pr_buf)

                yield f"data: {json.dumps({'type': 'done', 'content': full_text})}\n\n"
                return  # Kết thúc generator


            else:
                # Normal path: LLM quyết định tool cần gọi
                while tool_round < MAX_TOOL_ROUNDS:
                    ai_response = await llm_with_tools.ainvoke(lc_messages)

                    # Không có tool_calls → kiểm tra có cần tính toán không
                    if not (hasattr(ai_response, "tool_calls") and ai_response.tool_calls):
                        # ── FORCED TOOL EXECUTION: LLM bỏ qua tool nhưng query cần data ──
                        if tool_round == 0 and _is_data_calculation_query(user_content):
                            logger.warning("[ForcedTool] LLM skipped tool on calculation query — force executing query_dataset_readonly")
                            auto_code = _auto_generate_pandas_code(user_content)
                            if auto_code:
                                try:
                                    status_msg = "\n\n*[⚙️ Đang tính toán dữ liệu thực tế từ 33,848 dòng CSV...]*\n\n"
                                    full_text += status_msg
                                    yield f"data: {json.dumps({'type': 'token', 'content': status_msg})}\n\n"

                                    forced_result = await available_tools["query_dataset_readonly"].ainvoke({"code": auto_code})

                                    # 1. Stream trực tiếp bảng Markdown chuẩn từ Python (0% hallucination math truth)
                                    table_chunk = f"\n{forced_result}\n\n"
                                    full_text += table_chunk
                                    yield f"data: {json.dumps({'type': 'token', 'content': table_chunk})}\n\n"

                                    # 2. Cho LLM nhận xét 2-3 câu ngắn gọn bên dưới bảng (không được tự bịa số)
                                    synth_messages = [
                                        SystemMessage(content=current_system_prompt),
                                        HumanMessage(content=user_content),
                                        AIMessage(content=str(forced_result)),
                                        HumanMessage(content="[YÊU CẦU BẮT BUỘC: Bảng dữ liệu ở trên ĐÃ ĐƯỢC HIỂN THỊ ĐẦY ĐỦ. KHÔNG LẶP LẠI BẢNG VÀ KHÔNG THAY ĐỔI BẤT KỲ CON SỐ NÀO. Viết 2-3 câu nhận xét ngắn gọn bằng Tiếng Việt về xu hướng nổi bật từ dữ liệu trên.]")
                                    ]
                                    _synth_buf = ""
                                    async for chunk in llm.astream(synth_messages):
                                        token = getattr(chunk, "content", "")
                                        if token:
                                            _synth_buf += token
                                            full_text += token
                                            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

                                    _set_response_cache(_cache_key, full_text)
                                    yield f"data: {json.dumps({'type': 'done', 'content': full_text})}\n\n"
                                    return
                                except Exception as _fe:
                                    logger.warning("[ForcedTool] Failed: %s", _fe)
                        break

                    lc_messages.append(ai_response)
                    tool_round += 1

                    # Stream status
                    tool_names = [tc["name"] for tc in ai_response.tool_calls]
                    if "scrape_car_data" in tool_names:
                        status_msg = "\n\n*[⚙️ Đang cào dữ liệu từ link... vui lòng đợi]*\n\n"
                    elif "query_dataset_readonly" in tool_names:
                        status_msg = "\n\n*[⚙️ Đang tính toán dữ liệu thực tế từ 33,848 dòng CSV...]*\n\n"
                    elif any(n in tool_names for n in ["read_file_content", "list_files"]):
                        status_msg = "\n\n*[⚙️ Đang đọc file...]*\n\n"
                    elif any(n in tool_names for n in ["create_file", "modify_file", "delete_file", "move_rename_file"]):
                        status_msg = "\n\n*[⚙️ Đang tạo yêu cầu quản lý file...]*\n\n"
                    elif any(n in tool_names for n in ["rollback_last_change", "show_change_history", "list_all_backups"]):
                        status_msg = "\n\n*[⚙️ Đang xử lý lịch sử sao lưu file...]*\n\n"
                    elif "run_python_file" in tool_names:
                        status_msg = "\n\n*[⚙️ Đang thực thi file script Python trên đĩa...]*\n\n"
                    else:
                        status_msg = "\n\n*[⚙️ Đang xử lý...]*\n\n"

                    full_text += status_msg
                    yield f"data: {json.dumps({'type': 'token', 'content': status_msg})}\n\n"

                    # Thực thi tool calls
                    for tool_call in ai_response.tool_calls:
                        tool_name = tool_call["name"]
                        if tool_name in available_tools:
                            try:
                                tool_result = await available_tools[tool_name].ainvoke(tool_call["args"])
                            except Exception as te:
                                tool_result = f"Lỗi khi thực thi tool {tool_name}: {type(te).__name__}: {str(te)}"
                        else:
                            tool_result = f"Tool '{tool_name}' không được nhận dạng."

                        # 🛑 NẾU LÀ TOOL TẠO/SỬA/XÓA FILE, BACKUP, SCRAPER HOẶC RUN SCRIPT -> Stream kết quả ngay & NGẮT LOOP NGAY LẬP TỨC
                        if tool_name in [
                            "create_file", "modify_file", "delete_file", "move_rename_file",
                            "rollback_last_change", "show_change_history", "list_all_backups",
                            "run_python_file", "plan_file_operations", "get_plan_status",
                            "scrape_car_data"
                        ]:
                            action_chunk = f"\n{tool_result}\n\n"
                            full_text += action_chunk
                            yield f"data: {json.dumps({'type': 'token', 'content': action_chunk})}\n\n"
                            _set_response_cache(_cache_key, full_text)
                            yield f"data: {json.dumps({'type': 'done', 'content': full_text})}\n\n"
                            return  # Ngắt loop ngay lập tức, không lặp 5 vòng!

                        lc_messages.append(
                            ToolMessage(
                                content="[YÊU CẦU BẮT BUỘC: Trả lời bằng TIẾNG VIỆT. BẮT BUỘC sử dụng ĐÚNG các con số từ kết quả tính toán bên dưới, TUYỆT ĐỐI KHÔNG ĐƯỢC TỰ BỊA CON SỐ MỚI.]\n\n" + str(tool_result),
                                tool_call_id=tool_call["id"]
                            )
                        )
                        logger.info(
                            "[AgenticLoop] round=%d tool=%s result_len=%d",
                            tool_round, tool_name, len(str(tool_result)),
                        )

            # ── PHASE B: Stream câu trả lời (chỉ đến đây nếu normal path) ──────
            # CASE 1: tool_round == 0 → fake typewriter từ ai_response.content
            # CASE 2: tool_round > 0 → llm_with_tools.astream()
            #   Dùng llm_with_tools (có tool schemas) để Ollama xử lý đúng
            #   message sequence có tool_calls → đảm bảo streaming hoạt động
            if tool_round == 0:
                final_content = ai_response.content if hasattr(ai_response, "content") and ai_response.content else ""
                if final_content:
                    CHUNK, DELAY = 6, 0.012
                    for i in range(0, len(final_content), CHUNK):
                        piece = final_content[i:i + CHUNK]
                        full_text += piece
                        yield f"data: {json.dumps({'type': 'token', 'content': piece})}\n\n"
                        await asyncio.sleep(DELAY)
                    _set_response_cache(_cache_key, final_content)
                else:
                    error_piece = "Xin lỗi, tôi không thể tạo câu trả lời lúc này. Vui lòng thử lại."
                    full_text += error_piece
                    yield f"data: {json.dumps({'type': 'token', 'content': error_piece})}\n\n"
            else:
                # Normal path với tool calls — dùng llm_with_tools.astream()
                # Ollama cần tool schemas để xử lý và stream đúng tool_call messages
                logger.info("[AgenticLoop] Phase B: llm_with_tools.astream after %d rounds", tool_round)
                _response_buf = ""
                async for chunk in llm_with_tools.astream(lc_messages):
                    token = ""
                    if hasattr(chunk, "content") and chunk.content:
                        token = chunk.content
                    if token:
                        _response_buf += token
                        full_text += token
                        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                # Lưu vào cache sau khi stream xong
                if _response_buf:
                    _set_response_cache(_cache_key, _response_buf)

            yield f"data: {json.dumps({'type': 'done', 'content': full_text})}\n\n"

        except Exception as e:
            logger.error("[Analysis Chat] LLM error: %s", e)
            error_msg = str(e)
            if "Rate limit" in error_msg or "429" in error_msg:
                error_msg = "Mô hình AI đang bị quá tải (Rate Limit). Vui lòng đợi vài giây và thử lại."
            elif "Request too large" in error_msg or "413" in error_msg:
                error_msg = "Dữ liệu quá lớn để xử lý một lúc. Vui lòng thử hỏi ngắn gọn hơn."
            elif "OutputParserException" in error_msg or "parse" in error_msg.lower():
                error_msg = "AI gặp lỗi trong quá trình tự động sinh code truy vấn dữ liệu. Vui lòng thử lại."
            elif "failed_generation" in error_msg or "Failed to call a function" in error_msg:
                error_msg = (
                    "Mô hình Gemini từ chối chạy đoạn code truy vấn do nghi ngờ vi phạm an toàn "
                    "(Safety Filter), hoặc đã sinh sai cú pháp gọi Tool. "
                    "Vui lòng thử diễn đạt lại câu hỏi."
                )
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
        finally:
            if full_text and request.session_id != "unknown":
                await _persist_analysis_turn(
                    session_id=request.session_id,
                    session_title=request.session_title,
                    user_content=user_content,
                    ai_content=full_text,
                    user_id=user_id,
                )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/models")
async def get_available_models() -> dict:
    """Trả về danh sách models có thể dùng cho phân tích."""
    return {
        "models": [
            {"id": "llama-3.3-70b-versatile", "provider": "groq", "name": "Llama 3.3 70B (Groq ⚡)"},
            {"id": "llama-3.1-8b-instant", "provider": "groq", "name": "Llama 3.1 8B Instant (Groq ⚡)"},
            {"id": "gemini-1.5-flash", "provider": "google", "name": "Gemini 1.5 Flash"},
            {"id": "gemini-1.5-pro", "provider": "google", "name": "Gemini 1.5 Pro"},
            {"id": "gpt-4o-mini", "provider": "openai", "name": "GPT-4o Mini"},
            {"id": "gpt-4o", "provider": "openai", "name": "GPT-4o"},
            {"id": "llama3.2", "provider": "ollama", "name": "Llama 3.2 3B (Local Ollama)"},
            {"id": "llama3.1", "provider": "ollama", "name": "Llama 3.1 8B (Local Ollama)"},
        ]
    }

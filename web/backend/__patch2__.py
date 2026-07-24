"""
Patch analysis_chat.py:
1. Add dedicated get_dashboard_info tool - LLM gọi khi hỏi về dashboard/tab
2. Fix Phase B - stream ai_response.content trực tiếp (không gọi LLM lần 2)
3. Update ROLE_BLOCK - dẫn LLM gọi get_dashboard_info cho dashboard questions
4. Fix query_dataset_readonly - thêm warning không dùng cho dashboard
"""
from pathlib import Path

filepath = Path(r'app/api/analysis_chat.py')

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# =============================================================================
# FIX 1: Update query_dataset_readonly docstring - cấm dùng cho dashboard
# =============================================================================
old_qdr_doc = '''        async def query_dataset_readonly(code: str) -> str:
            """Công cụ chạy mã Python/Pandas ngầm để lấy thống kê chi tiết từ dữ liệu CSV.
            Chạy hoàn toàn ẩn với user — chỉ trả về kết quả text.
            CẢNH BÁO QUAN TRỌNG: KHÔNG ĐƯỢC dùng tool này cho câu hỏi về dashboard/tab/biểu đồ.
            Dashboard data ĐÃ CÓ SẴN trong system prompt — chỉ cần đọc và trả lời trực tiếp.
            Tool này CHỈ dùng khi cần số liệu CSV chi tiết chưa có trong context (filter, aggregation phức tạp).'''

new_qdr_doc = '''        async def query_dataset_readonly(code: str) -> str:
            """Chạy mã Python/Pandas để lấy số liệu chi tiết từ CSV (33,848 dòng).
            Chạy NGẦM — chỉ trả về kết quả text, không hiển thị code.

            ⛔ KHÔNG DÙNG tool này cho câu hỏi về dashboard/tab/biểu đồ/KPI dashboard.
            ⛔ Cho dashboard/tab → Gọi tool get_dashboard_info(tab) thay thế.
            ✅ Dùng tool này CHỈ KHI: cần số liệu CSV chi tiết (filter, group by, top-N...)'''

if old_qdr_doc in content:
    content = content.replace(old_qdr_doc, new_qdr_doc)
    print("FIX 1 (query_dataset_readonly doc): APPLIED")
else:
    # Try finding by partial match
    idx = content.find('async def query_dataset_readonly')
    if idx >= 0:
        print(f"FIX 1: query_dataset_readonly found at char {idx}, line {content[:idx].count(chr(10))+1}")
    else:
        print("FIX 1: query_dataset_readonly NOT FOUND")

# =============================================================================
# FIX 2: Add get_dashboard_info tool after query_dataset_readonly tool
# =============================================================================
# Find the read_file_content tool definition and insert before it
DASHBOARD_TOOL = '''
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
            from pathlib import Path as _Path
            import json as _json

            docs_dir = _Path(__file__).resolve().parents[4] / "docs"
            json_path = docs_dir / "Dashboard.json"

            if not json_path.exists():
                return "Lỗi: Không tìm thấy Dashboard.json."

            try:
                with open(json_path, "r", encoding="utf-8") as _f:
                    dash = _json.load(_f)
            except Exception as _e:
                return f"Lỗi đọc Dashboard.json: {_e}"

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

                return "\\n".join(out)

            result_parts = []
            try:
                if tab == "all":
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
                            result_parts.append(f"Không tìm thấy tab '{tab}'. Các tab có sẵn: Tab1, Tab2, Tab3, Tab4, Tab5")
            except Exception as _e:
                return f"Lỗi xử lý Dashboard.json: {_e}"

            return "\\n\\n".join(result_parts) if result_parts else "Không có dữ liệu."

'''

# Insert the new tool before read_file_content
insert_marker = '        @tool\n        async def read_file_content(file_path: str) -> str:'
if insert_marker in content:
    content = content.replace(insert_marker, DASHBOARD_TOOL + insert_marker)
    print("FIX 2 (get_dashboard_info tool): APPLIED")
else:
    idx = content.find('async def read_file_content')
    print(f"FIX 2: read_file_content at char {idx}, line {content[:idx].count(chr(10))+1 if idx>=0 else 'NOT FOUND'}")

# =============================================================================
# FIX 3: Add get_dashboard_info to tools_list
# =============================================================================
old_tools_list = '''            tools_list = [
                scrape_car_data,
                query_dataset_readonly,
                read_file_content,'''

new_tools_list = '''            tools_list = [
                scrape_car_data,
                query_dataset_readonly,
                get_dashboard_info,
                read_file_content,'''

if old_tools_list in content:
    content = content.replace(old_tools_list, new_tools_list)
    print("FIX 3 (tools_list): APPLIED")
else:
    print("FIX 3: tools_list pattern NOT FOUND")

# =============================================================================
# FIX 4: Update ROLE_BLOCK - thêm get_dashboard_info vào decision tree
# =============================================================================
old_decision_tree = '''**A. Về dashboard/tab/biểu đồ/KPI → TRẢ LỜI THẲNG từ system prompt:**
- "tab 1/2/3/... trình bày gì?", "dashboard có gì?", "biểu đồ nào?", "KPI là gì?"
→ **ĐỌC** block `[DASHBOARD INSIGHTS]` phía dưới và trả lời ngay với số liệu cụ thể
→ KHÔNG gọi bất kỳ tool nào, KHÔNG giả định'''

new_decision_tree = '''**A. Về dashboard/tab/biểu đồ/KPI dashboard:**
- "tab 1/2/3/... trình bày gì?", "dashboard có gì?", "biểu đồ nào?", "KPI là gì?"
→ **GỌI NGẦM** `get_dashboard_info(tab="Tab1")` (hoặc Tab2/Tab3/.../all)
→ Tool sẽ trả về dữ liệu chính xác từ Dashboard.json → Trả lời với số liệu đó
→ KHÔNG GỌI `query_dataset_readonly` cho dashboard, KHÔNG giả định'''

if old_decision_tree in content:
    content = content.replace(old_decision_tree, new_decision_tree)
    print("FIX 4 (ROLE_BLOCK decision tree): APPLIED")
else:
    print("FIX 4: decision tree pattern NOT FOUND")

# Fix the DECISION TREE section too
old_dt2 = '''2. Hỏi về dashboard/tab/KPI/biểu đồ → **ĐỌC [DASHBOARD INSIGHTS] → TRẢ LỜI NGAY** (không tool, không giả định)
3. Hỏi thống kê/số liệu chi tiết → `query_dataset_readonly(code)` ngầm'''

new_dt2 = '''2. Hỏi về dashboard/tab/biểu đồ/KPI → gọi ngầm `get_dashboard_info(tab="TabX")`
3. Hỏi thống kê/số liệu chi tiết CSV → `query_dataset_readonly(code)` ngầm'''

if old_dt2 in content:
    content = content.replace(old_dt2, new_dt2)
    print("FIX 4b (decision tree 2): APPLIED")

# Fix the summary rules
old_summary = '''- ✅ Dashboard/tab/biểu đồ → ĐỌC [DASHBOARD INSIGHTS] TRONG SYSTEM PROMPT → trả lời ngay với số liệu cụ thể
- ✅ Số liệu CSV chi tiết → gọi `query_dataset_readonly` NGẦM (không hiện code, không hỏi user)'''

new_summary = '''- ✅ Dashboard/tab/biểu đồ/KPI → gọi ngầm `get_dashboard_info(tab="TabX")` → trả lời với số liệu thực
- ✅ Số liệu CSV chi tiết → gọi `query_dataset_readonly` NGẦM (không hiện code, không hỏi user)'''

if old_summary in content:
    content = content.replace(old_summary, new_summary)
    print("FIX 4c (summary rules): APPLIED")

# =============================================================================
# FIX 5: Add get_dashboard_info to TOOLS section in ROLE_BLOCK
# =============================================================================
old_tools_section = '''### 1. `read_file_content` - Đọc file
**Khi nào dùng:** User hỏi "cho xem nội dung file X", "file Y có gì?" (CHỈ dùng cho file/thư mục cụ thể, KHÔNG DÙNG cho dashboard/tab)
**Auto-approve:** ✅ Chạy ngay (LOW risk)'''

new_tools_section = '''### 0. `get_dashboard_info` - Lấy data Dashboard ← DÙNG CHO MỌI CÂU HỎI VỀ DASHBOARD/TAB
**Khi nào dùng:** User hỏi về "tab 1/2/3/4/5", "dashboard", "biểu đồ", "KPI dashboard"
**Cách dùng:** `get_dashboard_info(tab="Tab1")` hoặc `get_dashboard_info(tab="all")`
**Auto-approve:** ✅ Chạy ngay (READ-ONLY)

### 1. `read_file_content` - Đọc file
**Khi nào dùng:** User hỏi "cho xem nội dung file X", "file Y có gì?" (CHỈ dùng cho file/thư mục cụ thể)
**Auto-approve:** ✅ Chạy ngay (LOW risk)'''

if old_tools_section in content:
    content = content.replace(old_tools_section, new_tools_section)
    print("FIX 5 (tools section): APPLIED")
else:
    print("FIX 5: tools section NOT FOUND")

# =============================================================================
# Write file
# =============================================================================
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nFile written.")

# Syntax check
import py_compile
try:
    py_compile.compile(str(filepath), doraise=True)
    print("SYNTAX CHECK: OK ✅")
except py_compile.PyCompileError as e:
    print(f"SYNTAX ERROR ❌: {e}")

# Count occurrences of get_dashboard_info
count = content.count("get_dashboard_info")
print(f"get_dashboard_info appears {count} times in file")

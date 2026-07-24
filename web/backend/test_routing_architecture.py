import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.api.analysis_chat import _is_data_calculation_query, _auto_generate_pandas_code, _TAB_PREWARMED_CACHE

def detect_direct_tool(msg: str):
    m = msg.lower()

    if _is_data_calculation_query(msg):
        auto_code = _auto_generate_pandas_code(msg)
        if auto_code:
            return ("query_dataset_readonly", {"code": auto_code})

    detail_kw = [
        "tất cả", "chi tiết", "bảng", "biểu đồ", "kpi", "full", "dữ liệu",
        "thông số", "con số", "bảng biểu", "liệt kê", "dữ liệu thô", "đầy đủ",
        "trình bày gì", "có những gì", "gồm những gì", "nội dung đầy đủ", "chỉ số"
    ]
    is_detail_requested = any(kw in m for kw in detail_kw)

    tab_matches = re.findall(r'\btab\s*([1-5])\b', m)
    if tab_matches:
        if len(set(tab_matches)) > 1:
            return ("get_dashboard_info", {"tab": "all"})

        t_key = f"Tab{tab_matches[0]}"

        if is_detail_requested:
            return ("get_dashboard_info", {"tab": t_key})

        if any(kw in m for kw in ["tóm tắt", "tổng quan", "overview", "xem nhanh", "giới thiệu"]):
            if t_key in _TAB_PREWARMED_CACHE:
                return ("prewarmed_cache", t_key)

        return ("get_dashboard_info", {"tab": t_key})

    return ("llm_react", None)


q = 'Tính trung bình số km xe Dầu đi được so với xe Xăng theo từng năm sản xuất từ 2018 đến 2023"'
res = detect_direct_tool(q)
print("Query:", q)
print("Tool target:", res[0])
print("Has auto-generated Python code:", "code" in res[1] and len(res[1]["code"]) > 50)

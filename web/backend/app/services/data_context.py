"""
Data Context Service — đọc dataset ô tô thực tế và sinh "Circumstance Card"
để inject vào system prompt của AI Analysis module.

Pattern: Role → Circumstance → Rules → Request
- Circumstance gồm 3 phần:
    1. Schema đầy đủ (tên cột, dtype, null%)
    2. Knowledge Base được tính sẵn từ CSV (thống kê thực tế)
    3. Dashboard pre-computed insights từ Dashboard.json
- Cache trong memory sau lần đọc đầu tiên để tránh I/O mỗi request
"""
from __future__ import annotations

import json
import logging
import os
import time
from functools import lru_cache
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ─── Đường dẫn ───────────────────────────────────────────────────────────────
_DATA_ROOT     = Path(__file__).resolve().parents[4] / "data"
_DOCS_ROOT     = Path(__file__).resolve().parents[4] / "docs"
PROCESSED_CSV  = _DATA_ROOT / "processed" / "car_detail_processed.csv"
RAW_CSV        = _DATA_ROOT / "raw"       / "car_detail.csv"
DASHBOARD_JSON = _DOCS_ROOT / "Dashboard.json"

# Cột phân tích chính (luôn giữ chính xác tên tiếng Việt)
_NUMERIC_COLS = [
    "Giá (triệu VND)",
    "Số Km đã đi (km)",
    "Năm sản xuất",
    "Dung tích động cơ (lít)",
    "Tiêu thụ nhiên liệu sạch",
    "Số chỗ ngồi sạch",
    "Số cửa sạch",
]
_CATEG_COLS = [
    "Hãng", "Dòng xe", "Tình trạng", "Xuất xứ",
    "Hộp số", "Loại nhiên liệu", "Dẫn động",
    "Màu ngoại thất", "Màu nội thất",
]


# ─── Builder chính ────────────────────────────────────────────────────────────

_context_cache = None
_context_cache_mtime = 0.0

def build_data_context_card() -> str:
    """
    Tổng hợp context card hoàn chỉnh:
    - Schema + thống kê CSV thực tế
    - Knowledge Base tính sẵn (để AI trả lời trực tiếp)
    - Dashboard insights từ Dashboard.json
    - Quy tắc tiền xử lý từ các notebooks

    Sử dụng cache dựa trên thời gian chỉnh sửa file (mtime) để luôn cập nhật dữ liệu mới nhất.
    """
    global _context_cache, _context_cache_mtime

    csv_path = PROCESSED_CSV if PROCESSED_CSV.exists() else (RAW_CSV if RAW_CSV.exists() else None)

    # Tính mtime mới nhất của toàn bộ folder processed và JSON
    current_mtime = 0.0
    try:
        if PROCESSED_CSV.parent.exists():
            for f in PROCESSED_CSV.parent.glob("*.csv"):
                current_mtime = max(current_mtime, os.path.getmtime(f))
        if DASHBOARD_JSON.exists():
            current_mtime = max(current_mtime, os.path.getmtime(DASHBOARD_JSON))
    except Exception:
        pass

    # Trả về cache nếu file không đổi
    if _context_cache is not None and current_mtime <= _context_cache_mtime and current_mtime > 0:
        return _context_cache
    try:
        import pandas as pd
    except ImportError:
        logger.warning("pandas chưa được cài — trả về context mặc định")
        return _fallback_context()

    csv_path = PROCESSED_CSV if PROCESSED_CSV.exists() else (RAW_CSV if RAW_CSV.exists() else None)
    if csv_path is None:
        logger.warning("Không tìm thấy file CSV dataset — dùng context mặc định")
        return _fallback_context()

    try:
        df = pd.read_csv(csv_path, low_memory=False)
        logger.info("DataContext: đọc %s — shape %s", csv_path.name, df.shape)
    except Exception as exc:
        logger.error("Lỗi đọc CSV: %s", exc)
        return _fallback_context()

    parts = [
        _build_preprocessing_rules(),
        _build_schema_section(df, csv_path),
        _build_all_tables_schema(),
        _build_knowledge_base(df),
        _build_dashboard_section(),
    ]
    _context_cache = "\n\n".join(p for p in parts if p)
    _context_cache_mtime = current_mtime
    return _context_cache


# ─── Section 1: Schema ───────────────────────────────────────────────────────

def _build_schema_section(df, csv_path: Path) -> str:
    n_rows, n_cols = df.shape
    lines = [
        "## DATASET ĐẦU VÀO",
        f"- **File:** `{csv_path.name}` (nguồn: bonbanh.com)",
        f"- **Kích thước:** {n_rows:,} dòng × {n_cols} cột",
        f"- **Đường dẫn đầy đủ:** `{csv_path.as_posix()}`",
        f"- **Load code:** `df = pd.read_csv(r'{csv_path}', low_memory=False)`",
        "",
        "## SCHEMA — TẤT CẢ CỘT",
        "```",
    ]
    null_pct = (df.isnull().sum() / n_rows * 100).round(1)
    for col in df.columns:
        dtype_str = str(df[col].dtype)
        null_str  = f"null={null_pct[col]:.1f}%" if null_pct[col] > 0 else "no null"
        lines.append(f"  {col!r:45s} dtype={dtype_str:10s}  {null_str}")
    lines.append("```")

    # Cột đã tiền xử lý
    clean_cols = [c for c in df.columns if "sạch" in c.lower()]
    if clean_cols:
        lines += [
            "",
            "## CỘT ĐÃ TIỀN XỬ LÝ (hậu tố 'sạch')",
            "Các cột này đã chuẩn hóa, xóa outlier — dùng trực tiếp cho phân tích:",
        ]
        for c in clean_cols:
            lines.append(f"  - `{c}`")

    # Cảnh báo null cao
    high_null = null_pct[null_pct > 10].sort_values(ascending=False)
    if not high_null.empty:
        lines += ["", "## CẢNH BÁO NULL CAO (>10%)"]
        for col, pct in high_null.items():
            lines.append(f"- `{col}`: **{pct:.1f}% null** → cần dropna() hoặc fillna() trước khi dùng")

    return "\n".join(lines)


# ─── Section 1.1: All Tables Schema ──────────────────────────────────────────

def _build_all_tables_schema() -> str:
    """Scan tất cả các bảng trong data/processed và liệt kê cấu trúc cột."""
    import pandas as pd
    lines = [
        "## CẤU TRÚC CÁC BẢNG DỮ LIỆU KHÁC (Dimension & Fact)",
        "Các bảng này nằm trong thư mục `d:/TU HOC/DV_Final/data/processed/`. Khi cần truy vấn, hãy dùng `pd.read_csv('đường_dẫn')`.",
        "```text",
    ]
    try:
        processed_dir = PROCESSED_CSV.parent
        for csv_file in sorted(processed_dir.glob("*.csv")):
            if csv_file.name == PROCESSED_CSV.name:
                continue # Đã có schema chi tiết ở trên
            
            try:
                # Đọc nhanh (chỉ lấy header)
                df_preview = pd.read_csv(csv_file, nrows=0)
                cols = ", ".join(df_preview.columns)
                lines.append(f"- {csv_file.name}: [{cols}]")
            except Exception:
                lines.append(f"- {csv_file.name}: (không thể đọc cột)")
        
        lines.append("```")
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Lỗi đọc thư mục processed: {e}")
        return ""


# ─── Section 1.5: Preprocessing Rules ────────────────────────────────────────

def _build_preprocessing_rules() -> str:
    # Lấy danh sách các file trong thư mục processed
    try:
        processed_dir = PROCESSED_CSV.parent
        files = [f.name for f in processed_dir.glob("*.csv")]
        files_str = "\n  - ".join(sorted(files))
    except Exception:
        files_str = "car_detail_processed.csv, fact_car_listings.csv, dim_brand.csv..."
        
    return f"""## QUY TẮC TIỀN XỬ LÝ & CẤU TRÚC THƯ MỤC DỮ LIỆU
> ⚠️ GIÚP AI TRẢ LỜI CÁC CÂU HỎI VỀ CÁCH DỮ LIỆU ĐƯỢC LÀM SẠCH VÀ LƯU TRỮ.
Dưới đây là các bước tiền xử lý đã được thực hiện trong Notebook:
- **Số Km đã đi**: Có nhiều dòng chứa giá trị ảo (vd: 4.2 tỷ km do lỗi tràn số). Các ngoại lệ này đã được chuyển thành NaN. Giá trị trung vị thực tế khoảng 20,000 km.
- **Tạo cột "sạch"**: Để khắc phục lỗi nhập liệu của người dùng, các cột mới được tạo để lọc giá trị hợp lý:
  - `Số cửa sạch`: Giới hạn từ 2 đến 6 cửa.
  - `Số chỗ ngồi sạch`: Giới hạn từ 2 đến 16 chỗ.
  - `Tiêu thụ nhiên liệu sạch`: Giới hạn từ 1 đến 30 L/100km.
- **Hệ thống nạp nhiên liệu**: Cột gốc chứa tới 802 biến thể cực kỳ hỗn loạn (sai chính tả, viết tắt...). Đã được chuẩn hóa/canonicalise lại.
- **Chuẩn hóa 3NF (Star Schema)**: Dữ liệu đã được tách thành bảng Fact và các bảng Dimension để giảm lặp dữ liệu, tối ưu cho Power BI và SQL. Mọi file xuất ra đều ở dạng UTF-8-SIG.
- **Thư mục lưu trữ**: Tất cả các bảng nằm trong thư mục `{PROCESSED_CSV.parent.as_posix()}`.
  Các file hiện có:
  - {files_str}"""


# ─── Section 2: Knowledge Base (tính sẵn từ CSV) ─────────────────────────────

def _build_knowledge_base(df) -> str:
    """
    Tính toán và đóng gói các số liệu thực tế quan trọng nhất.
    AI dùng trực tiếp để trả lời câu hỏi mà KHÔNG cần chạy code.
    """
    lines = ["## KNOWLEDGE BASE — SỐ LIỆU THỰC TẾ TÍNH SẴN"]
    lines.append("> AI sử dụng phần này để trả lời câu hỏi trực tiếp, không cần người dùng chạy code.")

    try:
        import pandas as pd
        import numpy as np

        # --- Thống kê cột số ---
        lines.append("\n### THỐNG KÊ CỘT SỐ")
        num_present = [c for c in _NUMERIC_COLS if c in df.columns]
        if num_present:
            desc = df[num_present].describe().round(2)
            lines.append("```")
            hdr = f"{'Cột':<38} {'min':>10} {'25%':>10} {'median':>10} {'mean':>10} {'75%':>10} {'max':>10}"
            lines.append(hdr)
            lines.append("-" * 105)
            for col in num_present:
                if col in desc.columns:
                    s = desc[col]
                    lines.append(
                        f"{col:<38} {s['min']:>10.1f} {s['25%']:>10.1f} "
                        f"{s['50%']:>10.1f} {s['mean']:>10.1f} {s['75%']:>10.1f} {s['max']:>10.1f}"
                    )
            lines.append("```")

        # --- Top hãng xe theo số lượng và giá trung vị ---
        if "Hãng" in df.columns and "Giá (triệu VND)" in df.columns:
            lines.append("\n### TOP HÃNG XE (theo số lượng tin đăng)")
            brand_stats = (
                df.groupby("Hãng")["Giá (triệu VND)"]
                .agg(so_luong="count", gia_trung_vi="median", gia_trung_binh="mean")
                .sort_values("so_luong", ascending=False)
                .head(20)
                .round(0)
            )
            lines.append("| Hãng | Số lượng | Giá trung vị (tr) | Giá trung bình (tr) |")
            lines.append("|------|----------|-------------------|---------------------|")
            for brand, row in brand_stats.iterrows():
                lines.append(f"| {brand} | {int(row.so_luong):,} | {int(row.gia_trung_vi):,} | {int(row.gia_trung_binh):,} |")

        # --- Phân loại theo dòng xe ---
        if "Dòng xe" in df.columns:
            lines.append("\n### PHÂN BỐ THEO DÒNG XE")
            dong_xe = df["Dòng xe"].value_counts().head(10)
            lines.append("| Dòng xe | Số lượng |")
            lines.append("|---------|----------|")
            for dong, cnt in dong_xe.items():
                lines.append(f"| {dong} | {cnt:,} |")

        # --- Loại nhiên liệu ---
        if "Loại nhiên liệu" in df.columns:
            lines.append("\n### PHÂN BỐ LOẠI NHIÊN LIỆU")
            nl = df["Loại nhiên liệu"].value_counts()
            lines.append("| Nhiên liệu | Số lượng | % |")
            lines.append("|------------|----------|---|")
            total = len(df)
            for nl_type, cnt in nl.items():
                pct = cnt / total * 100
                lines.append(f"| {nl_type} | {cnt:,} | {pct:.1f}% |")

        # --- Tình trạng và xuất xứ ---
        for col in ["Tình trạng", "Xuất xứ", "Hộp số"]:
            if col in df.columns:
                lines.append(f"\n### PHÂN BỐ {col.upper()}")
                vc = df[col].value_counts()
                lines.append(f"| {col} | Số lượng | % |")
                lines.append(f"|{'-'*len(col)}|----------|---|")
                for val, cnt in vc.items():
                    lines.append(f"| {val} | {cnt:,} | {cnt/len(df)*100:.1f}% |")

        # --- Màu ngoại thất phổ biến ---
        if "Màu ngoại thất" in df.columns:
            lines.append("\n### MÀU NGOẠI THẤT PHỔ BIẾN")
            mau = df["Màu ngoại thất"].value_counts().head(8)
            lines.append("| Màu | Số lượng | % |")
            lines.append("|-----|----------|---|")
            for mau_val, cnt in mau.items():
                lines.append(f"| {mau_val} | {cnt:,} | {cnt/len(df)*100:.1f}% |")

        # --- Xu hướng theo năm sản xuất ---
        if "Năm sản xuất" in df.columns and "Giá (triệu VND)" in df.columns:
            lines.append("\n### XU HƯỚNG GIÁ THEO NĂM SẢN XUẤT (2015-2025)")
            year_stats = (
                df[df["Năm sản xuất"] >= 2015]
                .groupby("Năm sản xuất")["Giá (triệu VND)"]
                .agg(so_luong="count", gia_median="median")
                .round(0)
            )
            lines.append("| Năm | Số lượng | Giá trung vị (tr) |")
            lines.append("|-----|----------|-------------------|")
            for year, row in year_stats.iterrows():
                lines.append(f"| {int(year)} | {int(row.so_luong):,} | {int(row.gia_median):,} |")

        # --- Phân loại giá ---
        if "Giá (triệu VND)" in df.columns:
            lines.append("\n### PHÂN LOẠI GIÁ XE")
            gia = df["Giá (triệu VND)"].dropna()
            buckets = [
                ("Dưới 200 tr",    gia < 200),
                ("200–500 tr",     (gia >= 200) & (gia < 500)),
                ("500–800 tr",     (gia >= 500) & (gia < 800)),
                ("800 tr – 1.2 tỷ", (gia >= 800) & (gia < 1200)),
                ("1.2–2 tỷ",       (gia >= 1200) & (gia < 2000)),
                ("2–5 tỷ",         (gia >= 2000) & (gia < 5000)),
                ("Trên 5 tỷ",      gia >= 5000),
            ]
            lines.append("| Phân loại | Số lượng | % |")
            lines.append("|-----------|----------|---|")
            for label, mask in buckets:
                cnt = mask.sum()
                lines.append(f"| {label} | {cnt:,} | {cnt/len(gia)*100:.1f}% |")

    except Exception as exc:
        logger.warning("Lỗi khi tính Knowledge Base: %s", exc)
        lines.append(f"_(Lỗi tính toán: {exc})_")

    return "\n".join(lines)


# ─── Section 3: Dashboard Insights ───────────────────────────────────────────

def _build_dashboard_section() -> str:
    """
    Đọc Dashboard.json và chuyển thành markdown tóm tắt tất cả 5 tab.
    Cho AI biết ngữ cảnh đầy đủ của dashboard đã được phân tích trước.
    """
    if not DASHBOARD_JSON.exists():
        logger.warning("Dashboard.json không tìm thấy: %s", DASHBOARD_JSON)
        return ""

    try:
        with open(DASHBOARD_JSON, "r", encoding="utf-8") as f:
            dash = json.load(f)
    except Exception as exc:
        logger.error("Lỗi đọc Dashboard.json: %s", exc)
        return ""

    lines = ["## DASHBOARD INSIGHTS — KẾT QUẢ PHÂN TÍCH THỰC TẾ"]
    lines.append("> Dữ liệu được tính sẵn từ Dashboard. AI dùng trực tiếp để trả lời.")

    # ── TAB 1: Thị trường ─────────────────────────────────────────────────────
    try:
        t1 = dash["Tab1"]["charts"]
        lines.append("\n### TAB 1 — THỊ TRƯỜNG TỔNG QUAN")
        lines.append(f"- Tổng tin đăng: **{t1['so_tin_dang']['data'][0]['Giá trị']:,}**")
        lines.append(f"- Số hãng xe: **{t1['so_hang_xe']['data'][0]['Giá trị']}**")
        lines.append(f"- Trung vị giá xe: **{t1['trung_vi_gia_xe_trieu_vnd']['data'][0]['Giá trị']:,} triệu VND**")
        lines.append(f"- Đời xe phổ biến nhất: **{t1['doi_xe_pho_bien_nhat']['data'][0]['Giá trị']}**")

        lines.append("\n**Hãng xe nhiều tin nhất:**")
        lines.append("| Hãng | Số tin đăng |")
        lines.append("|------|-------------|")
        for r in t1['cac_hang_xe_co_luong_tin_dang_cao_nhat']['data']:
            lines.append(f"| {r['Hãng']} | {r['Count of id_tin_đăng']:,} |")

        lines.append("\n**Tình trạng xe:**")
        for r in t1['co_cau_tin_dang_theo_tinh_trang_xe']['data']:
            lines.append(f"- {r['Tình trạng']}: **{r['Count of id_tin_đăng']:,} tin**")

        lines.append("\n**Xuất xứ:**")
        for r in t1['co_cau_tin_dang_theo_xuat_xu']['data']:
            lines.append(f"- {r['Xuất xứ']}: **{r['Count of id_tin_đăng']:,} tin**")

        lines.append("\n**Theo dòng xe:**")
        lines.append("| Dòng xe | Số lượng |")
        lines.append("|---------|----------|")
        for r in t1['so_luong_tin_dang_theo_dong_xe']['data']:
            lines.append(f"| {r['Dòng xe']} | {r['Số lượng']:,} |")

        lines.append("\n**Số lượng tin theo năm sản xuất (gần đây):**")
        lines.append("| Năm | Số lượng |")
        lines.append("|-----|----------|")
        for r in t1['so_luong_tin_dang_theo_nam_san_xuat']['data'][-10:]:
            lines.append(f"| {r['Năm sản xuất']} | {r['Số lượng']:,} |")
    except Exception as e:
        lines.append(f"_(Lỗi Tab1: {e})_")

    # ── TAB 2: Giá xe ─────────────────────────────────────────────────────────
    try:
        t2 = dash["Tab2"]["charts"]
        lines.append("\n### TAB 2 — GIẢI MÃ GIÁ XE")
        lines.append(f"- Giá xe đắt nhất: **{t2['gia_xe_dat_nhat_vnd']['data'][0]['Giá trị']/1e9:.0f} tỷ VND**")
        lines.append(f"- Giá xe rẻ nhất: **{t2['gia_xe_re_nhat_vnd']['data'][0]['Giá trị']/1e6:.0f} triệu VND**")

        lines.append("\n**Giá trung vị top hãng sang (VND):**")
        lines.append("| Hãng | Giá trung vị |")
        lines.append("|------|-------------|")
        for r in t2['gia_trung_vi_cua_top_8_hang_xe_hang_sang']['data']:
            vals = list(r.values())
            hang, gia = vals[0], vals[1]
            lines.append(f"| {hang} | {gia/1e9:.1f} tỷ |")

        lines.append("\n**Phân phối giá xe trên thị trường:**")
        lines.append("| Phân loại giá | Số tin đăng |")
        lines.append("|---------------|-------------|")
        for r in t2['phan_phoi_gia_xe_theo_so_tin_dang_tren_thi_truong']['data']:
            lines.append(f"| {r['Phân loại giá']} | {r['Count of id_tin_đăng']:,} |")

        lines.append("\n**Xu hướng giá theo năm SX (trung vị, VND):**")
        lines.append("| Năm | Giá trung vị |")
        lines.append("|-----|-------------|")
        for r in t2['xu_huong_gia_xe_theo_nam_san_xuat']['data'][-12:]:
            lines.append(f"| {r['Năm sản xuất']} | {r['Median of Giá (VND)']/1e6:.0f} triệu |")
    except Exception as e:
        lines.append(f"_(Lỗi Tab2: {e})_")

    # ── TAB 3: Xăng vs Điện ───────────────────────────────────────────────────
    try:
        t3 = dash["Tab3"]["charts"]
        lines.append("\n### TAB 3 — XĂNG vs ĐIỆN")
        for k, label in [
            ('quy_mo_xe_dien', 'Quy mô xe điện (số lượng)'),
            ('thi_phan_nam_2025', 'Thị phần xe điện năm 2025'),
            ('hang_dan_dau', 'Hãng dẫn đầu thị phần xe điện'),
        ]:
            d = t3[k]['data'][0]
            vals = list(d.values())
            lines.append(f"- {label}: **{vals[1]}**")

        lines.append("\n**So sánh giá trung vị Xe Điện vs Xăng (triệu VND):**")
        lines.append("| Dòng xe | Loại NL | Giá trung vị |")
        lines.append("|---------|---------|-------------|")
        for r in t3['so_sanh_gia_trung_vi_xe_dien_re_hon_xe_xang']['data']:
            lines.append(f"| {r['Dòng xe']} | {r['Loại nhiên liệu']} | {r['Giá trung vị']:,} |")

        lines.append("\n**Tăng trưởng xe điện 2020–2025:**")
        lines.append("| Năm | Số lượng XĐ | Thị phần |")
        lines.append("|-----|-------------|----------|")
        for r in t3['su_but_pha_cua_xe_dien_so_luong_voi_thi_phan_2020_2025']['data']:
            lines.append(f"| {r['Năm sản xuất']} | {r['Số lượng xe điện']:,} | {r['Thị phần (%)']} |")
    except Exception as e:
        lines.append(f"_(Lỗi Tab3: {e})_")

    # ── TAB 4: Chân dung người mua ────────────────────────────────────────────
    try:
        t4 = dash["Tab4"]["charts"]
        lines.append("\n### TAB 4 — CHÂN DUNG NGƯỜI MUA")
        for k, label in [
            ('chon_so_tu_dong', '% chọn số tự động'),
            ('chon_xe_5_cho', '% chọn xe 5 chỗ'),
            ('chon_mau_trang', '% chọn màu trắng'),
        ]:
            d = t4[k]['data'][0]
            vals = list(d.values())
            lines.append(f"- {label}: **{vals[1]}**")

        lines.append("\n**Nhu cầu số chỗ ngồi:**")
        lines.append("| Nhóm | Số xe |")
        lines.append("|------|-------|")
        for r in t4['phan_bo_nhu_cau_so_cho_ngoi_cua_gia_dinh_viet_khi_mua_xe']['data']:
            lines.append(f"| {r['Nhóm Chỗ Ngồi']} | {r['Tổng Số Xe']:,} |")

        lines.append("\n**Màu ngoại thất được ưa chuộng:**")
        lines.append("| Màu | Số xe |")
        lines.append("|-----|-------|")
        for r in t4['xu_huong_lua_chon_mau_ngoai_that_cua_nguoi_mua_xe_viet']['data']:
            lines.append(f"| {r['Màu ngoại thất']} | {r['Số Xe Màu Ngoại Thất']:,} |")
    except Exception as e:
        lines.append(f"_(Lỗi Tab4: {e})_")

    # ── TAB 5: Góc khuất thị trường ───────────────────────────────────────────
    try:
        t5 = dash["Tab5"]["charts"]
        lines.append("\n### TAB 5 — GÓC KHUẤT THỊ TRƯỜNG")
        for k, label in [
            ('xe_chay_nhieu_km_nhat', 'Xe chạy nhiều km nhất (km)'),
            ('so_hang_xe_hiem_5_xe', 'Số hãng xe hiếm (≤5 xe)'),
            ('luong_xe_ford_sx_2023', 'Lượng xe Ford SX 2023'),
            ('xe_50k_km_dat_nhat_tr_vnd', 'Xe >50k km đắt nhất (triệu VND)'),
        ]:
            d = t5[k]['data'][0]
            vals = list(d.values())
            lines.append(f"- {label}: **{vals[1]}**")

        lines.append("\n**Top 8 xe rẻ nhất (tỷ VND):**")
        lines.append("| Xe | Giá (tỷ) |")
        lines.append("|----|----------|")
        for r in t5['top_8_xe_re_nhat_ty_vnd']['data']:
            lines.append(f"| {r['Tên xe rút gọn']} | {r['Tab5_GiaTy_ReNhat']} |")

        lines.append("\n**Top 8 xe đắt nhất (tỷ VND):**")
        lines.append("| Xe | Giá (tỷ) |")
        lines.append("|----|----------|")
        for r in t5['top_8_xe_dat_nhat_ty_vnd']['data']:
            lines.append(f"| {r['Tên xe rút gọn']} | {r['Tab5_GiaTy_DatNhat']} |")
    except Exception as e:
        lines.append(f"_(Lỗi Tab5: {e})_")

    return "\n".join(lines)


# ─── Fallback ─────────────────────────────────────────────────────────────────

def _fallback_context() -> str:
    return """## DATASET ĐẦU VÀO
- File: car_detail_processed.csv (dữ liệu ô tô Việt Nam từ bonbanh.com)
- Các cột chính: 'Hãng', 'Dòng xe', 'Giá (triệu VND)', 'Năm sản xuất',
  'Số Km đã đi (km)', 'Loại nhiên liệu', 'Hộp số', 'Dẫn động',
  'Màu ngoại thất', 'Xuất xứ', 'Tình trạng'
- Lưu ý: Không tìm thấy file CSV — hãy yêu cầu người dùng xác nhận đường dẫn file.
"""


def get_data_file_path() -> Optional[str]:
    """Trả về đường dẫn tuyệt đối của file CSV chính."""
    if PROCESSED_CSV.exists():
        return str(PROCESSED_CSV)
    if RAW_CSV.exists():
        return str(RAW_CSV)
    return None

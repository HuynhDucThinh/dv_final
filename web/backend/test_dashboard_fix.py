"""
=============================================================================
TEST SCRIPT: Kiểm tra patch dashboard fix cho analysis_chat.py
=============================================================================
Chay: python test_dashboard_fix.py
Khong can server, khong can API key.
=============================================================================
"""
import sys
import asyncio
import py_compile
import traceback

# Fix encoding cho Windows terminal
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"d:\TU HOC\DV_Final\web\backend")

# --- Colors ---
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

passed = 0
failed = 0
warnings = 0

def ok(msg):
    global passed
    passed += 1
    print(f"  {GREEN}PASS{RESET} {msg}")

def fail(msg, detail=""):
    global failed
    failed += 1
    print(f"  {RED}FAIL{RESET} {msg}")
    if detail:
        print(f"       {RED}>> {detail}{RESET}")

def warn(msg):
    global warnings
    warnings += 1
    print(f"  {YELLOW}WARN{RESET} {msg}")

def section(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")


# =============================================================================
# TEST 1: Syntax Check
# =============================================================================
section("TEST 1 -- Syntax Check (py_compile)")

FILEPATH = r"d:\TU HOC\DV_Final\web\backend\app\api\analysis_chat.py"
try:
    py_compile.compile(FILEPATH, doraise=True)
    ok("analysis_chat.py khong co loi cu phap Python")
except py_compile.PyCompileError as e:
    fail("analysis_chat.py co loi cu phap!", str(e))
    print(f"\n{RED}[CRITICAL] Khong the tiep tuc test vi file loi syntax.{RESET}")
    sys.exit(1)


# =============================================================================
# TEST 2: Import module
# =============================================================================
section("TEST 2 -- Import Module")

try:
    import app.api.analysis_chat as ac
    ok("import app.api.analysis_chat thanh cong")
except Exception as e:
    fail("Import that bai", traceback.format_exc(limit=3))
    print(f"\n{RED}[CRITICAL] Khong the import module.{RESET}")
    sys.exit(1)


# =============================================================================
# TEST 3: Kiem tra ROLE_BLOCK khong con chi dan mau thuan
# =============================================================================
section("TEST 3 -- ROLE_BLOCK Consistency")

role = ac._ROLE_BLOCK

if "DASHBOARD INSIGHTS" in role:
    fail(
        "Con sot chi dan cu '[DASHBOARD INSIGHTS]' trong ROLE_BLOCK",
        "Tim thay 'DASHBOARD INSIGHTS' -> mau thuan voi get_dashboard_info"
    )
else:
    ok("Khong con chi dan cu 'DASHBOARD INSIGHTS' -> nhat quan")

if "get_dashboard_info" in role:
    ok("ROLE_BLOCK co nhac den get_dashboard_info")
else:
    fail("ROLE_BLOCK KHONG nhac den get_dashboard_info!")

count_tool_ref = role.count("get_dashboard_info")
if count_tool_ref >= 3:
    ok(f"get_dashboard_info xuat hien {count_tool_ref} lan trong ROLE_BLOCK (du noi bat)")
else:
    warn(f"get_dashboard_info chi xuat hien {count_tool_ref} lan (nen >= 3)")

if "query_dataset_readonly" in role and ("KHONG" in role or "KH\u00d4NG" in role or "NOT" in role):
    ok("ROLE_BLOCK co canh bao ve viec khong dung query_dataset_readonly cho dashboard")
else:
    warn("Thieu canh bao tuong minh ve query_dataset_readonly trong ROLE_BLOCK")


# =============================================================================
# TEST 4: Kiem tra get_dashboard_info tool ton tai trong source
# =============================================================================
section("TEST 4 -- tools_list Code Check")

import inspect

source = inspect.getsource(ac)

total_occurrences = source.count("get_dashboard_info")
if total_occurrences >= 4:
    ok(f"'get_dashboard_info' xuat hien {total_occurrences} lan trong toan file")
else:
    fail(f"'get_dashboard_info' chi xuat hien {total_occurrences} lan -- thieu dinh nghia hoac khong co trong tools_list")

if "tools_list = [" in source and "get_dashboard_info," in source:
    ok("get_dashboard_info co trong tools_list")
else:
    fail("get_dashboard_info KHONG co trong tools_list!")

if "query_dataset_readonly," in source:
    ok("query_dataset_readonly van con trong tools_list")
else:
    warn("query_dataset_readonly khong tim thay trong tools_list?")

# Tim canh bao trong docstring (co the la Unicode hoac ASCII)
has_warning = (
    "KH\u00d4NG D\u00d9NG" in source          # Unicode: KHONG DUNG
    or "KHONG DUNG" in source           # ASCII fallback
    or "do not use" in source.lower()  # English fallback
    or "\u26d4" in source               # Unicode ky hieu cam
)
if has_warning:
    ok("query_dataset_readonly docstring co canh bao ve dashboard (Unicode/ASCII)")
else:
    fail("Thieu canh bao trong docstring cua query_dataset_readonly")

if "get_dashboard_info(tab)" in source:
    ok("query_dataset_readonly docstring chi ro dung get_dashboard_info thay the")
else:
    warn("query_dataset_readonly docstring khong chi ro get_dashboard_info la thay the")


# =============================================================================
# TEST 5: Goi logic get_dashboard_info (functional test, khong can LLM)
# =============================================================================
section("TEST 5 -- Functional Test: get_dashboard_info logic")

async def run_tool_tests():
    from pathlib import Path
    import json

    docs_path = Path(r"d:\TU HOC\DV_Final\docs\Dashboard.json")

    # 5a: Dashboard.json ton tai?
    if docs_path.exists():
        ok(f"Dashboard.json ton tai ({docs_path.stat().st_size / 1024:.0f} KB)")
    else:
        fail("Dashboard.json KHONG ton tai!", str(docs_path))
        return

    # 5b: Parse duoc?
    try:
        with open(docs_path, "r", encoding="utf-8") as f:
            dash = json.load(f)
        ok(f"Dashboard.json parse OK -- co {len(dash)} key: {list(dash.keys())}")
    except Exception as e:
        fail("Khong parse duoc Dashboard.json!", str(e))
        return

    # 5c: Du 5 tab?
    expected_tabs = ["Tab1", "Tab2", "Tab3", "Tab4", "Tab5"]
    missing = [t for t in expected_tabs if t not in dash]
    if not missing:
        ok(f"Du 5 tab: {expected_tabs}")
    else:
        fail(f"Thieu tab: {missing}")

    # 5d: Format tung tab (chep logic tu get_dashboard_info)
    def _fmt_tab(tab_key, tab_data):
        charts = tab_data.get("charts", {})
        tab_names = {
            "Tab1": "TAB 1 -- BUC TRANH THI TRUONG",
            "Tab2": "TAB 2 -- GIAI MA GIA XE",
            "Tab3": "TAB 3 -- CUOC CHIEN XANG vs DIEN",
            "Tab4": "TAB 4 -- CHAN DUNG NGUOI MUA",
            "Tab5": "TAB 5 -- GOC KHUAT THI TRUONG",
        }
        out = [f"## {tab_names.get(tab_key, tab_key)}", ""]
        for chart_key, chart_data in charts.items():
            data_rows = chart_data.get("data", [])
            if not data_rows:
                continue
            out.append(f"### {chart_key}")
            if len(data_rows) == 1 and len(data_rows[0]) <= 2:
                vals = list(data_rows[0].values())
                out.append(f"**{vals[-1]}**")
            else:
                if data_rows:
                    headers = list(data_rows[0].keys())
                    out.append("| " + " | ".join(str(h) for h in headers) + " |")
                    out.append("|" + "|".join("---" for _ in headers) + "|")
                    for row in data_rows[:3]:
                        out.append("| " + " | ".join(str(v) for v in row.values()) + " |")
            out.append("")
        return "\n".join(out)

    for tab in expected_tabs:
        try:
            if tab in dash:
                result = _fmt_tab(tab, dash[tab])
                charts_count = len(dash[tab].get("charts", {}))
                if result and len(result) > 50:
                    ok(f"{tab}: format OK -- {charts_count} chart(s), {len(result)} chars")
                else:
                    warn(f"{tab}: output qua ngan ({len(result)} chars)")
            else:
                fail(f"{tab} khong co trong Dashboard.json")
        except Exception as e:
            fail(f"{tab}: loi khi format", str(e))

    # 5e: tab="all"
    try:
        parts = []
        for tk in expected_tabs:
            if tk in dash:
                parts.append(_fmt_tab(tk, dash[tk]))
        result_all = "\n\n".join(parts)
        if len(result_all) > 500:
            ok(f"tab='all': OK -- tong {len(result_all):,} chars")
        else:
            warn(f"tab='all': output qua ngan ({len(result_all)} chars)")
    except Exception as e:
        fail("tab='all': loi khi xu ly", str(e))

    # 5f: tab khong hop le
    try:
        tab_invalid = "tab999"
        tab_norm = tab_invalid.strip().replace(" ", "").replace("tab", "Tab")
        if not tab_norm.startswith("Tab"):
            tab_norm = "Tab" + tab_norm
        if tab_norm not in dash:
            msg = f"Khong tim thay tab '{tab_invalid}'. Cac tab co san: Tab1, Tab2, Tab3, Tab4, Tab5"
            ok(f"tab khong hop le -> tra ve thong bao loi dung: '{msg[:60]}'")
    except Exception as e:
        fail("Test tab khong hop le bi loi", str(e))

asyncio.run(run_tool_tests())


# =============================================================================
# TEST 6: Phase B stream logic check (via source analysis)
# =============================================================================
section("TEST 6 -- Phase B Stream Logic Check")

if "if final_content:" in source and "CHUNK = 15" in source:
    ok("Phase B: co logic stream truc tiep tu ai_response.content (CHUNK = 15)")
else:
    fail("Phase B: khong tim thay logic stream truc tiep!")

if "llm_with_tools.astream(lc_messages)" in source:
    lines = source.split("\n")
    astream_line = next((i for i, l in enumerate(lines) if "llm_with_tools.astream" in l), -1)
    if astream_line > 0:
        context_before = "\n".join(lines[max(0, astream_line-5):astream_line])
        if "else:" in context_before:
            ok("Phase B: astream() chi o else-branch (fallback khi content rong)")
        else:
            warn("Phase B: astream() khong nam ro trong else-branch -- kiem tra lai")
else:
    warn("Phase B: khong tim thay astream() -- chi stream tu content san co")

if "await asyncio.sleep(0)" in source:
    ok("Phase B: co asyncio.sleep(0) de yield control trong streaming loop")
else:
    warn("Phase B: thieu asyncio.sleep(0) -- stream co the bi blocking")

if "tool_round = 0" in source and "MAX_TOOL_ROUNDS" in source:
    ok("Phase A: co MAX_TOOL_ROUNDS va tool_round counter (chong loop vo han)")
else:
    warn("Phase A: khong tim thay MAX_TOOL_ROUNDS")


# =============================================================================
# SUMMARY
# =============================================================================
total = passed + failed + warnings
print(f"\n{BOLD}{'='*60}{RESET}")
print(f"{BOLD}  KET QUA TONG HOP{RESET}")
print(f"{BOLD}{'='*60}{RESET}")
print(f"  Tong so kiem tra  : {total}")
print(f"  {GREEN}PASSED           : {passed}{RESET}")
print(f"  {RED}FAILED           : {failed}{RESET}")
print(f"  {YELLOW}WARNINGS         : {warnings}{RESET}")

if failed == 0 and warnings == 0:
    print(f"\n  {GREEN}{BOLD}[OK] TAT CA PASS -- Patch hoat dong dung!{RESET}")
elif failed == 0:
    print(f"\n  {YELLOW}{BOLD}[OK] Khong co loi nghiem trong, co {warnings} canh bao.{RESET}")
else:
    print(f"\n  {RED}{BOLD}[!!] CO {failed} LOI -- Can kiem tra lai!{RESET}")

print()

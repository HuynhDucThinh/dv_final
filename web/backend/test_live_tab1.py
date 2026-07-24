"""
=============================================================================
LIVE API TEST: Hoi AI ve Tab 1 dashboard va kiem tra phan hoi
=============================================================================
Chay: python test_live_tab1.py
Yeu cau: backend dang chay tren localhost:8000
=============================================================================
"""
import sys
import httpx
import json
import asyncio
import re

sys.stdout.reconfigure(encoding="utf-8")

BACKEND_URL = "http://localhost:8000"
API_ENDPOINT = f"{BACKEND_URL}/api/analysis/chat/stream"

# Su dung Groq key tu .env
GROQ_API_KEY = "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"

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def section(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")

def ok(msg):
    print(f"  {GREEN}PASS{RESET} {msg}")

def fail(msg, detail=""):
    print(f"  {RED}FAIL{RESET} {msg}")
    if detail:
        print(f"       {RED}>> {detail}{RESET}")

def warn(msg):
    print(f"  {YELLOW}WARN{RESET} {msg}")

def info(msg):
    print(f"  {CYAN}INFO{RESET} {msg}")


async def test_tab1_query():
    section("STEP 1 -- Kiem tra backend co chay khong")

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{BACKEND_URL}/api/analysis/models")
            if r.status_code == 200:
                models = r.json().get("models", [])
                ok(f"Backend online -- co {len(models)} models kha dung")
                for m in models[:3]:
                    info(f"  Model: {m['id']} ({m['provider']})")
            else:
                fail(f"Backend tra ve HTTP {r.status_code}")
                return
    except Exception as e:
        fail("Khong ket noi duoc backend!", str(e))
        print(f"\n{RED}Backend chua chay? Chay: uvicorn app.main:app --reload{RESET}")
        return

    # ----------------------------------------------------------------
    section("STEP 2 -- Gui cau hoi ve Tab 1 cho AI (Groq Llama)")

    payload = {
        "messages": [
            {"role": "user", "content": "Tab 1 cua dashboard trinh bay gi? Cho toi biet cac KPI va so lieu chinh."}
        ],
        "model": "llama-3.3-70b-versatile",
        "session_id": "test-tab1-check",
        "session_title": "Test Tab 1",
        "temperature": 0.1,
        "max_tokens": 2048,
        "inferenceConfig": {
            "credentials": {
                "groq": {"apiKey": GROQ_API_KEY}
            }
        }
    }

    info(f"Endpoint : {API_ENDPOINT}")
    info(f"Model    : {payload['model']}")
    info(f"Question : {payload['messages'][0]['content']}")
    print()

    full_response = ""
    token_count = 0
    got_tool_status = False
    tool_names_seen = []
    error_received = None

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream("POST", API_ENDPOINT, json=payload) as response:
                if response.status_code != 200:
                    fail(f"HTTP {response.status_code}: {response.text[:200]}")
                    return

                ok(f"Ket noi thanh cong (HTTP {response.status_code}) -- dang nhan stream...")
                print()

                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    try:
                        data = json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue

                    dtype = data.get("type", "")

                    if dtype == "token":
                        content = data.get("content", "")
                        # Detect tool status messages
                        if "*[" in content and "]*" in content:
                            got_tool_status = True
                            # Extract tool name from status msg
                            m = re.search(r'\[.+?\]', content)
                            if m:
                                tool_names_seen.append(m.group(0))
                            sys.stdout.write(f"{YELLOW}{content}{RESET}")
                        else:
                            sys.stdout.write(content)
                        sys.stdout.flush()
                        full_response += content
                        token_count += 1

                    elif dtype == "done":
                        full_response = data.get("content", full_response)
                        print()  # newline after streaming

                    elif dtype == "error":
                        error_received = data.get("content", "Unknown error")
                        print(f"\n{RED}[ERROR from AI]: {error_received}{RESET}")

    except httpx.ReadTimeout:
        fail("Timeout sau 60 giay -- model qua cham hoac bi treo")
        return
    except Exception as e:
        fail("Loi ket noi", str(e))
        return

    # ----------------------------------------------------------------
    section("STEP 3 -- Phan tich noi dung phan hoi")

    if error_received:
        fail(f"AI tra ve loi: {error_received}")
        return

    if not full_response.strip():
        fail("AI tra ve phan hoi rong!")
        return

    resp_len = len(full_response)
    info(f"Do dai phan hoi: {resp_len} chars, {token_count} SSE events")

    # 3a: Co phan hoi du dai khong?
    if resp_len > 200:
        ok(f"Phan hoi du dai ({resp_len} chars)")
    elif resp_len > 50:
        warn(f"Phan hoi kha ngan ({resp_len} chars) -- co the AI chua lay du data")
    else:
        fail(f"Phan hoi qua ngan ({resp_len} chars)!")

    # 3b: Co goi tool get_dashboard_info khong? (qua status message)
    if got_tool_status:
        ok(f"AI da goi tool (hien thi status): {tool_names_seen}")
    else:
        warn("Khong thay tool status message -- AI co the tra loi truc tiep tu prompt (OK neu data co san)")

    # 3c: Co so lieu cu the khong? (khong bi gia dinh)
    # Kiem tra cac marker: so, %, "Tab 1", ten bieu do
    numeric_pattern = re.compile(r'\d[\d,\.]+')
    numbers_found = numeric_pattern.findall(full_response)
    if len(numbers_found) >= 3:
        ok(f"Phan hoi co {len(numbers_found)} so lieu cu the: {numbers_found[:8]}...")
    else:
        warn(f"Phan hoi co it so lieu ({len(numbers_found)} so) -- AI co the dang giai thich chung chung")

    # 3d: Co ke den Tab 1 / Buc tranh thi truong khong?
    kws_tab1 = ["tab 1", "tab1", "buc tranh", "thi truong", "kpi", "hang xe", "dong xe",
                "nam san xuat", "Tab 1", "Tab1", "KPI", "Toyota", "Honda", "Hyundai",
                "33,848", "33848", "tong so xe"]
    matched_kws = [kw for kw in kws_tab1 if kw.lower() in full_response.lower()]
    if len(matched_kws) >= 3:
        ok(f"Phan hoi co noi dung dung chu de Tab 1: {matched_kws[:5]}")
    elif len(matched_kws) >= 1:
        warn(f"Phan hoi co noi dung lien quan Tab 1 nhung chua ro rang: {matched_kws}")
    else:
        fail("Phan hoi KHONG co noi dung lien quan Tab 1! AI co the dang tra loi sai chu de.")

    # 3e: Co bi giai dinh khong? ("thong thuong", "co the", "gia su")
    assumption_phrases = [
        "thong thuong se", "co the gia su", "toi co the gia dinh",
        "chac han se co", "thong thuong bao gom", "co the la"
    ]
    assumptions = [p for p in assumption_phrases if p in full_response.lower()]
    if not assumptions:
        ok("Khong phat hien cau gia dinh (KHONG 'thong thuong se', 'co the gia su'...)")
    else:
        fail(f"Phat hien cau giai dinh: {assumptions}")

    # 3f: Co hoi nguoc lai nguoi dung khong?
    question_back = [
        "ban co the cung cap", "ban muon toi kiem tra",
        "ban co the mo ta", "toi can them thong tin"
    ]
    asked_back = [p for p in question_back if p in full_response.lower()]
    if not asked_back:
        ok("AI khong hoi nguoc lai nguoi dung")
    else:
        fail(f"AI hoi nguoc lai nguoi dung: {asked_back}")

    # ----------------------------------------------------------------
    section("STEP 4 -- Preview noi dung phan hoi")
    preview = full_response[:600].replace("\n", "\n  ")
    print(f"  {CYAN}--- Dau phan hoi (600 chars) ---{RESET}")
    print(f"  {preview}")
    if len(full_response) > 600:
        print(f"  {YELLOW}... [{len(full_response)-600} chars nua]{RESET}")

    # ----------------------------------------------------------------
    section("KIEM TRA HOAN TAT")
    print(f"\n{BOLD}  Neu tat ca PASS -> AI tra loi dung Tab 1 tu Dashboard.json{RESET}")
    print(f"{BOLD}  Neu co FAIL -> xem chi tiet o tren de debug{RESET}\n")


asyncio.run(test_tab1_query())

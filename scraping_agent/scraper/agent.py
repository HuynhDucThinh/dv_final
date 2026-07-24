"""
Core scraping agent — browser_use 0.13.6 compatible.

Dùng các LLM wrapper tích hợp sẵn của browser-use (ChatOpenAI, ChatGoogle, ChatGroq)
để tránh xung đột dependency với langchain-openai.
"""

import os
import json
import re
from datetime import datetime

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from browser_use import ActionResult, Agent, BrowserProfile, BrowserSession, Controller

load_dotenv()


# ---------------------------------------------------------------------------
# Wrapper: strip markdown code fences khỏi response của Groq/Llama
# ---------------------------------------------------------------------------

def make_groq_llm(model: str, base_url: str, api_key: str):
    """Tạo ChatOpenAI với dont_force_structured_output=True.
    Groq llama-3.3-70b-versatile trả về JSON bọc trong ```json...``` nên
    cần dùng dont_force_structured_output để browser-use không gửi json_schema
    (versatile không hỗ trợ strict json_schema), rồi strip markdown thủ công.
    """
    from browser_use.llm import ChatOpenAI
    import langchain_core.messages as lc_msgs

    class GroqChatOpenAI(ChatOpenAI):
        """Subclass ChatOpenAI, strip ```json ... ``` khỏi AIMessage content."""

        async def ainvoke(self, *args, **kwargs):
            result = await super().ainvoke(*args, **kwargs)
            if hasattr(result, 'content') and isinstance(result.content, str):
                result.content = _strip_code_fence(result.content)
            return result

        def invoke(self, *args, **kwargs):
            result = super().invoke(*args, **kwargs)
            if hasattr(result, 'content') and isinstance(result.content, str):
                result.content = _strip_code_fence(result.content)
            return result

    return GroqChatOpenAI(
        model=model,
        base_url=base_url,
        api_key=api_key,
        temperature=0.0,
        dont_force_structured_output=True,
    )


def _strip_code_fence(text: str) -> str:
    """Strip ```json ... ``` hoặc ``` ... ``` khỏi response text."""
    # Xóa ```json hoặc ``` ở đầu và cuối
    text = text.strip()
    match = re.match(r'^```(?:json)?\s*\n?(.*?)\n?```$', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text



# ---------------------------------------------------------------------------
# LLM factory — dùng browser_use.llm (tích hợp sẵn)
# ---------------------------------------------------------------------------


def get_llm(provider: str = 'auto'):
    """Return (primary_llm, fallback_llm | None)."""

    if provider == 'auto':
        if os.getenv('OPENAI_API_KEY'):
            provider = 'openai'
        elif os.getenv('GOOGLE_API_KEY'):
            provider = 'google'
        elif os.getenv('GROQ_API_KEY'):
            provider = 'groq'
        else:
            raise ValueError(
                'No API key found. Set one of these env vars:\n'
                '  OPENAI_API_KEY=...   (best quality)\n'
                '  GOOGLE_API_KEY=...   (good quality)\n'
                '  GROQ_API_KEY=...     (free, rate-limited)\n'
            )

    if provider == 'openai':
        from browser_use.llm import ChatOpenAI
        print('LLM: OpenAI GPT-4o-mini')
        primary = ChatOpenAI(model='gpt-4o-mini', temperature=0.0)
        fallback = None
        if os.getenv('GROQ_API_KEY'):
            fallback = make_groq_llm(
                model='llama-3.3-70b-versatile',
                base_url='https://api.groq.com/openai/v1',
                api_key=os.getenv('GROQ_API_KEY'),
            )
        return primary, fallback

    elif provider == 'google':
        from browser_use.llm import ChatGoogle
        print('LLM: Google Gemini 2.0 Flash')
        primary = ChatGoogle(model='gemini-2.0-flash', temperature=0.0)
        fallback = None
        if os.getenv('GROQ_API_KEY'):
            fallback = make_groq_llm(
                model='llama-3.3-70b-versatile',
                base_url='https://api.groq.com/openai/v1',
                api_key=os.getenv('GROQ_API_KEY'),
            )
        return primary, fallback

    elif provider == 'groq':
        from browser_use.llm import ChatGroq
        groq_key = os.getenv('GROQ_API_KEY')
        print('LLM: Groq llama-3.3-70b-versatile')
        primary = ChatGroq(
            model='llama-3.3-70b-versatile',
            api_key=groq_key,
            temperature=0.0,
        )
        fallback = None
        if os.getenv('GOOGLE_API_KEY'):
            from browser_use.llm import ChatGoogle
            fallback = ChatGoogle(model='gemini-2.0-flash', temperature=0.0)
        return primary, fallback

    else:
        raise ValueError(f'Unknown provider: {provider}. Choose: openai, google, groq')


# ---------------------------------------------------------------------------
# Task prompt — mô tả nhiệm vụ cho AI agent
# ---------------------------------------------------------------------------


def build_task(url: str) -> str:
    return f"""You are a car data extractor. Your job is to extract car information from a webpage.

The page has already been opened for you. URL: {url}

STEPS:
1. Close any popup, cookie banner, or modal overlay if present (click the X or dismiss button).
2. Scroll down slowly to read all information on the page.
3. Extract ALL available information about the car:
   - Car name / brand / model / year
   - Price (listed price, asking price, or market price)
   - Specifications: engine size, fuel type, transmission, mileage/odometer, color, condition (new/used)
   - Seller or dealer name and contact info if available
   - Any other notable details or description
4. Call the `extract_and_save_data` tool EXACTLY ONCE with all extracted information.
5. After calling the tool, you are DONE. Stop immediately.

RULES:
- Do NOT navigate to any other URL.
- Do NOT search for other pages or listings.
- If you cannot find certain information, write "N/A" for that field.
""".strip()


# ---------------------------------------------------------------------------
# Pydantic model cho action input
# ---------------------------------------------------------------------------


class CarDataInput(BaseModel):
    product_name: str = Field(
        description="Full car name including brand, model, year. Example: 'Land Rover Range Rover Sport 2022'"
    )
    price: str = Field(
        description="Price of the car. Example: '2.5 tỷ', '$45,000'. Write 'N/A' if not found."
    )
    specifications: str = Field(
        description="All specifications as plain text: engine, fuel, transmission, mileage/km, color, condition. One spec per line."
    )
    contact_info: str = Field(
        default="",
        description="Seller name, phone number, address or dealer info. Empty string if not found."
    )
    description: str = Field(
        default="",
        description="Additional description, condition notes, or any extra info from the page."
    )


# ---------------------------------------------------------------------------
# Main scraping coroutine
# ---------------------------------------------------------------------------


async def scrape_with_groq_direct(url: str, output_path: str, groq_key: str) -> int:
    """Dùng Playwright lấy HTML, rồi gọi Groq API trực tiếp — tránh json_schema issue."""
    from playwright.async_api import async_playwright
    from groq import Groq

    print('  [Groq Direct] Mở trình duyệt...')
    html_text = ''
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(3000)
            # Lấy text visible trên trang
            html_text = await page.evaluate('''() => {
                // Xóa script/style
                document.querySelectorAll("script,style,noscript").forEach(e => e.remove());
                return document.body.innerText.slice(0, 8000);
            }''')
        finally:
            await browser.close()

    if not html_text.strip():
        print('  [Groq Direct] Không lấy được nội dung trang')
        return 0

    print('  [Groq Direct] Gọi Groq API...')
    client = Groq(api_key=groq_key)
    prompt = f"""Extract car information from this webpage text and return JSON.

Webpage URL: {url}

Webpage content:
{html_text}

Return ONLY valid JSON with these fields:
{{
  "ten_xe": "full car name with brand, model, year",
  "gia": "price or price range (N/A if not found)",
  "thong_so_ky_thuat": "engine, fuel, transmission, etc. (one per line)",
  "lien_he": "seller/dealer info (empty if not found)",
  "mo_ta": "additional description or notes"
}}"""

    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[{'role': 'user', 'content': prompt}],
        response_format={'type': 'json_object'},
        temperature=0.0,
        max_tokens=1024,
    )

    raw = response.choices[0].message.content
    car_info = json.loads(raw)
    car_info['nguon'] = url
    car_info['thoi_gian'] = datetime.now().isoformat()

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump([car_info], f, ensure_ascii=False, indent=2)

    print(f"  [✓] Đã lưu: {car_info.get('ten_xe')} | {car_info.get('gia')}")
    return 1


async def scrape_reviews(
    url: str,
    output_path: str,
    fmt: str = 'json',
    max_reviews: int = 1,
    llm_provider: str = 'auto',
    headless: bool = False,
) -> int:
    """Trích xuất thông tin xe từ URL."""

    # Groq: dùng Playwright + Groq API trực tiếp (tránh json_schema issue)
    if llm_provider == 'groq' or (llm_provider == 'auto' and os.getenv('GROQ_API_KEY') and not os.getenv('OPENAI_API_KEY') and not os.getenv('GOOGLE_API_KEY')):
        groq_key = os.getenv('GROQ_API_KEY')
        try:
            return await scrape_with_groq_direct(url, output_path, groq_key)
        except Exception as e:
            print(f'\n  [Groq Direct] Lỗi: {e}')
            return 0

    # OpenAI / Google: dùng browser-use agent như cũ
    llm, fallback_llm = get_llm(llm_provider)

    controller = Controller()

    @controller.action(
        'Save all extracted car information to file. '
        'Call this ONCE after you have read the page and gathered all info.',
        param_model=CarDataInput,
    )
    async def extract_and_save_data(params: CarDataInput) -> ActionResult:
        car_info = {
            "ten_xe":             params.product_name,
            "gia":                params.price,
            "thong_so_ky_thuat": params.specifications,
            "lien_he":           params.contact_info,
            "mo_ta":             params.description,
            "nguon":             url,
            "thoi_gian":         datetime.now().isoformat(),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([car_info], f, ensure_ascii=False, indent=2)

        print(f"\n  [✓] Car data saved: {params.product_name} | {params.price}")
        return ActionResult(
            extracted_content='SUCCESS: Data saved.',
            is_done=True,
        )

    browser_profile = BrowserProfile(
        headless=headless,
        user_data_dir=None,
    )
    browser_session = BrowserSession(browser_profile=browser_profile)

    supports_vision = llm_provider in ('openai', 'google')

    agent_kwargs = dict(
        task=build_task(url),
        llm=llm,
        controller=controller,
        browser=browser_session,
        directly_open_url=url,
        max_actions_per_step=3,
        max_failures=6,
        max_history_items=20,
        use_vision=supports_vision,
    )

    if fallback_llm is not None:
        agent_kwargs['fallback_llm'] = fallback_llm

    agent = Agent(**agent_kwargs)

    saved_count = 0
    try:
        await agent.run(max_steps=25)
        if os.path.exists(output_path):
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data and len(data) > 0:
                    saved_count = 1
            except Exception:
                pass
    except KeyboardInterrupt:
        print('\nStopped by user.')
    except Exception as e:
        print(f'\nAgent error: {e}')
    finally:
        try:
            await browser_session.stop()
        except Exception:
            pass

    return saved_count

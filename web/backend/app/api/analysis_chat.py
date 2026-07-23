import json
import logging
import os
import asyncio
import uuid as _uuid
from datetime import datetime
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.auth_deps import get_current_user_id
from app.services.data_context import build_data_context_card, get_data_file_path

router = APIRouter(prefix="/api/analysis", tags=["AI Analysis"])
logger = logging.getLogger(__name__)

# ─── System Prompt Builder ────────────────────────────────────────────────────
# Pattern chuẩn: [ROLE] → [CIRCUMSTANCE] → [RULES]
# - ROLE: Khai báo danh tính và nhiệm vụ của AI
# - CIRCUMSTANCE: Ngữ cảnh dữ liệu thực tế (inject từ CSV lúc runtime)
# - RULES: Nguyên tắc hành vi bắt buộc

_ROLE_BLOCK = """\
# [ROLE — VAI TRÒ]
Bạn là một chuyên gia phân tích dữ liệu ô tô Việt Nam, hỗ trợ nhóm nghiên cứu \
tại một dự án học thuật. Bạn có kiến thức sâu về Python (pandas, matplotlib, seaborn, \
numpy, scikit-learn) và am hiểu thị trường ô tô Việt Nam.

NHIỆM VỤ CỐT LÕI:
- Trả lời câu hỏi TRỰC TIẼP bằng số liệu từ KNOWLEDGE BASE và DASHBOARD INSIGHTS trong [CIRCUMSTANCE].
- Nếu cần số liệu chi tiết hơn không có sẵn, đề xuất code READ-ONLY (chỉ đ## NGUYÊN TẮC HÀNH ĐỘNG (ĐỌC KỸ TRƯỚC KHI TRẢ LỜI)

**Bạn có 2 loại hành động, KHÔNG ĐƯỢC LẪN LỘN:**

### LOẠI 1 — GỌI TOOL NỘI BỘ (khi người dùng hỏi thông tin về dữ liệu)
**Nhận diện:** Người dùng hỏi thông tin từ dữ liệu. Ví dụ: "bảng X có bao nhiêu dòng?", "cột Y có giá trị gì?", "cho xem dòng 100", "đếm số xe Honda".
**Hành động:**
1. Gọi tool `query_dataset_readonly` (đây là tool nội bộ của hệ thống, KHÔNG phải hàm Python).
2. Trong tham số `code` của tool, viết code Python để truy vấn, ví dụ:
   ```
   import pandas as pd
   df = pd.read_csv('D:/TU HOC/DV_Final/data/processed/dim_origin.csv')
   print(df.shape)
   ```
3. Tool sẽ chạy ngầm và trả kết quả về cho bạn.
4. Bạn đọc kết quả đó rồi trả lời bằng ngôn ngữ tự nhiên cho người dùng.

**⛔ TUYỆT ĐỐI CẤM trong Loại 1:**
- In code ra màn hình dưới dạng ```python code block```
- Hỏi lại người dùng "Bạn có muốn tôi chạy không?"
- Hiển thị nút "Thực thi" (Chờ duyệt) cho người dùng

---

### LOẠI 2 — IN CODE RA MÀN HÌNH (khi người dùng yêu cầu viết code/sửa file/vẽ biểu đồ)
**Nhận diện:** Người dùng chủ động yêu cầu. Ví dụ: "hãy viết code...", "xóa dòng X", "lưu lại file", "vẽ biểu đồ", "sửa dữ liệu".
**Hành động:** In code ra trong markdown block ````python ... ``` ` để giao diện hiện nút "Thực thi" cho người dùng tự bấm.
**Luật khi sửa/lưu file:** Bắt buộc đủ 3 bước:
  1. `df = pd.read_csv('đường_dẫn_thực_tế')` — Đọc file gốc
  2. Xử lý dữ liệu (drop, fillna, filter...)
  3. `df.to_csv('đường_dẫn_thực_tế', index=False, encoding='utf-8-sig')` — Lưu đè (bắt buộc `utf-8-sig` để không lỗi tiếng Việt)

**⛔ TUYỆT ĐỐI CẤM trong Loại 2:**
- Tự gọi tool để lấy kết quả mà không hỏi ý kiến
- Tự ý lưu file mà không in code ra cho người dùng xem trước

---

## QUYỀN TRUY CẬP DỮ LIỆU
- Bạn CÓ QUYỀN truy cập TẤT CẢ các bảng trong `D:/TU HOC/DV_Final/data/processed/` (dim_origin.csv, dim_fuel_type.csv, fact_car_listings.csv...).
- KNOWLEDGE BASE phía dưới chứa thống kê của bảng chính — dùng nó khi câu hỏi không cần chi tiết dòng/cột cụ thể. Nếu cần chi tiết → Gọi tool (Loại 1).

## QUY TẮC GIAO TIẾP
- Luôn trả lời bằng tiếng Việt. Tô đậm (**) các số liệu quan trọng.
- Không bịa số liệu. Không vẽ biểu đồ trừ khi được yêu cầu.
- Nếu vẽ biểu đồ: lưu bằng `plt.savefig()` và in đường dẫn file.

## Quy tắc định dạng câu trả lời (PHONG CÁCH CHUYÊN NGHIỆP)
11. **CẤU TRÚC RÕ RÀNG**: Dùng markdown đầy đủ để chia nội dung:
    - `## Tiêu đề lớn` cho các mục chính (in đậm, cỡ lớn)
    - `### Tiêu đề nhỏ` cho các mục phụ
    - `---` để ngăn cách các phần nội dung lớn
    - `**số liệu**` để tô đậm tất cả số liệu, phần trăm, con số quan trọng
    - **BẢNG MARKDOWN**: Mọi dữ liệu có thể dạng bảng PHẢI dùng bảng markdown `| Cột | Cột |`:
      * So sánh nhiều hãng/dòng xe → bảng
      * Thống kê nhiều thuộc tính → bảng
      * Danh sách có 2+ thuộc tính liên quan → bảng
      * Key-value pairs nhiều dòng → bảng 2 cột "Thuộc tính | Giá trị"
      * KHÔNG liệt kê dạng `- **key**: value` khi có thể làm bảng
12. **ALERTS — CHỈ DÙNG KHI THỰC SỰ CẦN**: Không lạm dụng alerts màu sắc.
    - `> [!IMPORTANT] nội dung` → khung đỏ — CHỈ dùng cho kết luận hoặc cảnh báo CỰC KỲ quan trọng (1-2 lần/câu trả lời)
    - `> [!NOTE] nội dung` → khung xanh — chỉ dùng khi thực sự cần ghi chú đặc biệt
    - `> [!TIP] nội dung` → khung xanh lá — chỉ dùng cho gợi ý thực hành cụ thể
    - `> [!WARNING] nội dung` → khung vàng — chỉ dùng khi có rủi ro thực sự
    - **KHÔNG** dùng alert cho thông tin thông thường, tóm tắt hay bullet points bình thường
13. **GỢI Ý CÂU HỎI BẮT BUỘC**: Luôn kết thúc MỌI câu trả lời bằng tag:
    `<suggestions>Câu hỏi liên quan 1?|Câu hỏi liên quan 2?|Câu hỏi liên quan 3?</suggestions>`
    Mỗi câu hỏi phải liên quan đến chủ đề vừa trả lời, giúp người dùng khám phá thêm.
    Tag này phải đặt ở CUỐI CÙNG, sau tất cả nội dung khác.
"""


def _build_system_prompt() -> str:
    """
    Tổng hợp system prompt hoàn chỉnh theo pattern:
        [ROLE] → [CIRCUMSTANCE (data context thực tế)] → [RULES]

    Được gọi một lần khi module load, kết quả được cache.
    """
    data_path = get_data_file_path()
    load_snippet = (
        f"df = pd.read_csv(r'{data_path}', low_memory=False)"
        if data_path
        else "df = pd.read_csv('<đường_dẫn_file_csv>', low_memory=False)"
    )

    circumstance_header = f"""\
# [CIRCUMSTANCE — NGỮ CẢNH DỮ LIỆU THỰC TẾ]
> ⚠️ Đây là thông tin THỰC TẾ được đọc tự động từ file CSV lúc server khởi động.
> Chỉ dùng đúng tên cột, kiểu dữ liệu và đường dẫn được liệt kê bên dưới.

**Load dataset:**
```python
import pandas as pd
{load_snippet}
```
"""
    context_card = build_data_context_card()
    return "\n".join([_ROLE_BLOCK, circumstance_header, context_card, _RULES_BLOCK])


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
            api_key="ollama", # dummy key
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
    Lưu session vào PostgreSQL nếu CHAT_STORAGE_MODE=postgres.
    """
    async def generate() -> AsyncGenerator[str, None]:
        full_text = ""
        user_content = request.messages[-1].content if request.messages else ""
        
        import os
        from langchain_core.tools import tool
        import tempfile
        import pathlib

        @tool
        async def scrape_car_data(url: str) -> str:
            """Sử dụng công cụ này KHI VÀ CHỈ KHI người dùng gửi link xe (oto.com.vn, bonbanh.com, caranddriver.com...) 
            để cào thông tin chi tiết, giá cả và thông số kỹ thuật của xe đó. 
            Chỉ dùng khi người dùng yêu cầu phân tích một link cụ thể."""
            try:
                import sys
                import subprocess as _subprocess

                # Tìm đường dẫn scraping_agent/main.py từ vị trí file này
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

                # Tạo tmp file — đóng ngay vì Windows không cho process khác ghi vào file đang mở
                with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
                    tmp_path = tmp.name

                # Dùng run_in_executor + subprocess.run (sync) thay vì create_subprocess_exec
                # → tránh NotImplementedError trên Windows SelectorEventLoop của uvicorn
                def _run_scraper():
                    return _subprocess.run(
                        [sys.executable, str(script_path), url,
                         "--format", "json",
                         "--output", tmp_path,
                         "--llm", llm_arg],
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
                os.remove(tmp_path)

                if not data.strip():
                    return "Lỗi: File dữ liệu trống, có thể link không hợp lệ hoặc bị chặn."

                if len(data) > 15000:
                    data = data[:15000] + "\n... [Dữ liệu đã bị cắt bớt do quá dài]"

                logger.info("[scrape_tool] OK url=%s data_len=%s", url, len(data))
                return f"Dữ liệu cào được từ {url}:\n\n{data}"
            except Exception as e:
                logger.error("[scrape_tool] EXCEPTION %s: %s", type(e).__name__, e)
                return f"Lỗi khi cào dữ liệu: {type(e).__name__}: {str(e)}"

        @tool
        async def query_dataset_readonly(code: str) -> str:
            """Công cụ chạy mã Python/Pandas ngầm để lấy thống kê chi tiết từ dữ liệu.
            
            Args:
                code: Đoạn mã Python hợp lệ. Bắt buộc dùng lệnh print() để hiển thị kết quả. Biến `df` (dataframe chính) đã được tự động load sẵn.
            """
            import io
            import sys
            
            # Bảo mật cơ bản (Sandbox)
            forbidden = ["os.", "sys.", "subprocess", "__"]
            for f in forbidden:
                if f in code.replace(" ", ""):
                    return f"Lỗi: Không được phép sử dụng lệnh can thiệp hệ thống ({f})."
            
            try:
                import pandas as pd
                from app.services.data_context import get_data_file_path
                data_path = get_data_file_path()
                if not data_path:
                    return "Lỗi: Không tìm thấy file dữ liệu CSV."
                    
                local_env = {"pd": pd}
                local_env["df"] = pd.read_csv(data_path, low_memory=False)
                
                stdout_b = io.StringIO()
                old_stdout = sys.stdout
                sys.stdout = stdout_b
                try:
                    exec(code, local_env)
                finally:
                    sys.stdout = old_stdout
                    
                result = stdout_b.getvalue()
                if not result.strip():
                    return "Đã chạy thành công nhưng không có kết quả in ra. Hãy chắc chắn bạn đã dùng print() để hiển thị kết quả."
                return f"Kết quả từ dữ liệu:\n{result}"
            except Exception as e:
                return f"Lỗi khi thực thi code: {type(e).__name__}: {str(e)}"

        try:
            llm = _build_llm(request.model, request.temperature, request.max_tokens, request.inferenceConfig)
            llm_with_tools = llm.bind_tools([scrape_car_data, query_dataset_readonly])

            from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
            
            # Lấy System Prompt mới nhất (context động có kiểm tra cache mtime)
            current_system_prompt = _build_system_prompt()
            lc_messages = [SystemMessage(content=current_system_prompt)]
            
            for msg in request.messages:
                if msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            # Pass 1: Kiểm tra xem LLM có gọi tool không
            full_msg = None
            async for chunk in llm_with_tools.astream(lc_messages):
                if full_msg is None:
                    full_msg = chunk
                else:
                    full_msg += chunk

                token = chunk.content if hasattr(chunk, "content") else str(chunk)
                if token:
                    full_text += token
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            # Xử lý gọi Tool nếu có
            if full_msg and hasattr(full_msg, "tool_calls") and full_msg.tool_calls:
                lc_messages.append(full_msg)

                for tool_call in full_msg.tool_calls:
                    if tool_call["name"] == "scrape_car_data":
                        status_msg = f"\n\n*[Hệ thống: Đang tự động kích hoạt Agent cào dữ liệu từ link... Vui lòng đợi]*\n\n"
                    elif tool_call["name"] == "query_dataset_readonly":
                        status_msg = f"\n\n*[Hệ thống: Đang chạy ngầm truy vấn dữ liệu chi tiết... Vui lòng đợi]*\n\n"
                    else:
                        status_msg = f"\n\n*[Hệ thống: Đang thực thi công cụ... Vui lòng đợi]*\n\n"
                        
                    full_text += status_msg
                    yield f"data: {json.dumps({'type': 'token', 'content': status_msg})}\n\n"

                    if tool_call["name"] == "scrape_car_data":
                        tool_res = await scrape_car_data.ainvoke(tool_call["args"])
                    elif tool_call["name"] == "query_dataset_readonly":
                        tool_res = await query_dataset_readonly.ainvoke(tool_call["args"])
                    else:
                        tool_res = "Unknown tool."
                        
                    lc_messages.append(ToolMessage(content=tool_res, tool_call_id=tool_call["id"]))
                
                # Pass 2: Sinh câu trả lời cuối cùng sau khi có kết quả từ Tool
                async for chunk in llm_with_tools.astream(lc_messages):
                    token = chunk.content if hasattr(chunk, "content") else str(chunk)
                    if token:
                        full_text += token
                        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            yield f"data: {json.dumps({'type': 'done', 'content': full_text})}\n\n"

        except Exception as e:
            logger.error(f"[Analysis Chat] LLM error: {e}")
            error_msg = str(e)
            if "Rate limit" in error_msg or "429" in error_msg:
                error_msg = "Mô hình AI đang bị quá tải (Rate Limit). Vui lòng đợi vài giây và thử lại."
            elif "Request too large" in error_msg or "413" in error_msg:
                error_msg = "Dữ liệu quá lớn để xử lý một lúc. Vui lòng thử hỏi ngắn gọn hơn."
            elif "OutputParserException" in error_msg or "parse" in error_msg.lower():
                error_msg = "AI gặp lỗi trong quá trình tự động sinh code truy vấn dữ liệu. Vui lòng thử lại."
            elif "failed_generation" in error_msg or "Failed to call a function" in error_msg:
                error_msg = "Mô hình Gemini từ chối chạy đoạn code truy vấn do nghi ngờ vi phạm an toàn (Safety Filter), hoặc đã sinh sai cú pháp gọi Tool. Vui lòng thử diễn đạt lại câu hỏi."
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

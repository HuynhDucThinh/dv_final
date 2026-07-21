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

router = APIRouter(prefix="/api/analysis", tags=["AI Analysis"])
logger = logging.getLogger(__name__)

ANALYSIS_SYSTEM_PROMPT = """Bạn là một trợ lý AI chuyên phân tích dữ liệu ô tô Việt Nam.

NHIỆM VỤ:
- Giúp người dùng phân tích dữ liệu, đề xuất phương pháp và viết code Python.
- Khi viết code, bắt buộc phải giải thích rõ ràng bằng tiếng Việt ngay trong comment.

NGUYÊN TẮC BẮT BUỘC:
1. HIỂN THỊ CODE: Mỗi khi tạo code, phải hiển thị rõ ràng trong markdown code block (```python).
2. GIẢI THÍCH: Thêm comment tiếng Việt giải thích từng bước trong code.
3. KHÔNG TỰ Ý THỰC THI: Code chỉ là đề xuất — người dùng sẽ xem xét, chỉnh sửa và phê duyệt trước khi chạy.
4. KHÔNG THÊM SỐ LIỆU: Không tự ý tạo ra số liệu hay hình ảnh không có trong dữ liệu gốc.
5. GỢI Ý: Nếu người dùng chưa có ý tưởng, hãy đề xuất các phương pháp phân tích phù hợp để họ lựa chọn.

CẤU TRÚC DATASET (Dữ liệu ô tô Việt Nam):
- Các cột thường có: tên xe, hãng, giá, năm sản xuất, nhiên liệu, hộp số, màu sắc, tỉnh/thành
- Dữ liệu dạng CSV, đọc bằng: df = pd.read_csv('path/to/data.csv')

Luôn trả lời bằng tiếng Việt."""

# --- Fallback keys từ .env (dùng khi Admin UI chưa cấu hình) ---
_ENV_GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
_ENV_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
_ENV_GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

GROQ_MODELS = {"llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"}
OPENAI_MODELS = {"gpt-4o-mini", "gpt-4o", "gpt-4.1-nano"}
GOOGLE_MODELS = {"gemini-2.0-flash-lite", "gemini-2.5-flash", "gemini-3.1-flash-lite"}


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

    if model in GOOGLE_MODELS or model.startswith("gemini-"):
        api_key = _extract_key(inference_config, "google", _ENV_GOOGLE_API_KEY)
        if not api_key:
            raise ValueError("Google API Key chưa được cấu hình. Vào Quản trị → Cấu hình AI để nhập key.")
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=60,
        )

    raise ValueError(f"Model '{model}' không được hỗ trợ. Chọn một trong: Groq, OpenAI, Google.")


def _friendly_error(exc: Exception) -> str:
    """Trả về thông báo lỗi thân thiện cho người dùng."""
    text = str(exc)
    lower = text.lower()
    if "rate_limit_exceeded" in lower or "429" in lower or "rate limit" in lower:
        return (
            "⚠️ Đã đạt giới hạn tốc độ (Rate Limit) của model này. "
            "Vui lòng chờ ~30 giây rồi thử lại, hoặc chuyển sang model khác "
            "(ví dụ: mixtral-8x7b-32768 hoặc gemma2-9b-it) trong phần Cấu hình AI."
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
        try:
            llm = _build_llm(request.model, request.temperature, request.max_tokens, request.inferenceConfig)
            from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
            lc_messages = [SystemMessage(content=ANALYSIS_SYSTEM_PROMPT)]
            for msg in request.messages:
                if msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            async for chunk in llm.astream(lc_messages):
                token = chunk.content if hasattr(chunk, "content") else str(chunk)
                if token:
                    full_text += token
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            yield f"data: {json.dumps({'type': 'done', 'content': full_text})}\n\n"

        except Exception as e:
            logger.error("Analysis LLM error: %s", e)
            yield f"data: {json.dumps({'type': 'error', 'content': _friendly_error(e)})}\n\n"
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
            {"id": "gemma2-9b-it", "provider": "groq", "name": "Gemma 2 9B (Groq ⚡)"},
            {"id": "gemini-2.0-flash-lite", "provider": "google", "name": "Gemini 2.0 Flash-Lite"},
            {"id": "gemini-2.5-flash", "provider": "google", "name": "Gemini 2.5 Flash"},
            {"id": "gpt-4o-mini", "provider": "openai", "name": "GPT-4o Mini"},
            {"id": "gpt-4o", "provider": "openai", "name": "GPT-4o"},
        ]
    }

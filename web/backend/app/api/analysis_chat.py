"""
API Chat Phân tích dữ liệu — tách biệt với Legal Q&A.
Nhận yêu cầu phân tích, gọi LLM với system prompt phân tích dữ liệu,
trả về code Python kèm giải thích.

Sử dụng ChatOpenAI trực tiếp với provider-aware routing
để hỗ trợ Groq, OpenAI, Google mà không phụ thuộc vào get_llm() cũ.
"""
import json
import logging
import os
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

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

# --- Cấu hình provider ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

GROQ_MODELS = {"llama-3.3-70b-versatile", "gemma2-9b-it", "mixtral-8x7b-32768"}
OPENAI_MODELS = {"gpt-4o-mini", "gpt-4o", "gpt-4.1-nano"}
GOOGLE_MODELS = {"gemini-2.0-flash-lite", "gemini-2.5-flash", "gemini-3.1-flash-lite"}


def _build_llm(model: str, temperature: float, max_tokens: int):
    """Tạo LLM instance đúng provider dựa vào tên model."""
    from langchain_openai import ChatOpenAI

    if model in GROQ_MODELS:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY chưa được cấu hình trong file .env")
        return ChatOpenAI(
            model=model,
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=60,
        )

    if model in OPENAI_MODELS:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY chưa được cấu hình trong file .env")
        return ChatOpenAI(
            model=model,
            api_key=OPENAI_API_KEY,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=60,
        )

    if model in GOOGLE_MODELS or model.startswith("gemini-"):
        api_key = GOOGLE_API_KEY
        if not api_key:
            raise ValueError("GOOGLE_API_KEY chưa được cấu hình trong file .env")
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=60,
        )

    raise ValueError(f"Model '{model}' không được hỗ trợ. Chọn một trong: Groq, OpenAI, Google.")


class AnalysisChatMessage(BaseModel):
    role: str
    content: str


class AnalysisChatRequest(BaseModel):
    messages: list[AnalysisChatMessage]
    model: str = "llama-3.3-70b-versatile"
    session_id: str = "unknown"
    streaming: bool = True
    temperature: float = 0.3
    max_tokens: int = 4096


async def _stream_llm(request: AnalysisChatRequest) -> AsyncGenerator[str, None]:
    """Gọi LLM và stream kết quả theo định dạng SSE."""
    try:
        llm = _build_llm(request.model, request.temperature, request.max_tokens)

        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

        lc_messages = [SystemMessage(content=ANALYSIS_SYSTEM_PROMPT)]
        for msg in request.messages:
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))

        full_text = ""
        async for chunk in llm.astream(lc_messages):
            token = chunk.content if hasattr(chunk, "content") else str(chunk)
            if token:
                full_text += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'content': full_text})}\n\n"

    except Exception as e:
        logger.error("Analysis LLM error: %s", e)
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"


@router.post("/chat/stream")
async def analysis_chat_stream(request: AnalysisChatRequest) -> StreamingResponse:
    """
    Endpoint chat streaming cho module phân tích dữ liệu.
    Tách biệt hoàn toàn với /chat/stream của Legal Q&A.
    """
    return StreamingResponse(
        _stream_llm(request),
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
            {"id": "gemma2-9b-it", "provider": "groq", "name": "Gemma 2 9B (Groq ⚡)"},
            {"id": "mixtral-8x7b-32768", "provider": "groq", "name": "Mixtral 8x7B (Groq ⚡)"},
            {"id": "gemini-2.0-flash-lite", "provider": "google", "name": "Gemini 2.0 Flash-Lite"},
            {"id": "gemini-2.5-flash", "provider": "google", "name": "Gemini 2.5 Flash"},
            {"id": "gpt-4o-mini", "provider": "openai", "name": "GPT-4o Mini"},
            {"id": "gpt-4o", "provider": "openai", "name": "GPT-4o"},
        ]
    }

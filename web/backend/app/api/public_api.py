"""
public_api.py — Endpoint công khai cho ứng dụng bên ngoài sử dụng.

Cung cấp:
  POST /api/public/chat    — Hỏi AI, nhận JSON đồng bộ (không phải SSE stream)
  GET  /api/public/health  — Kiểm tra trạng thái

Bảo mật:
  Header X-API-Key bắt buộc nếu biến môi trường API_KEY được đặt trong .env.
  Nếu API_KEY không có trong .env → endpoint hoạt động tự do (dev mode).

Thiết kế:
  - Tái sử dụng _build_llm, _build_system_prompt từ analysis_chat.py
  - Không thay đổi bất kỳ file nào khác đang chạy đúng.
"""

from __future__ import annotations

import logging
import os
import uuid
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/public", tags=["Public API"])

# Đọc API key từ .env một lần lúc load module
_API_KEY = os.getenv("API_KEY", "").strip()


# ─── Request / Response schema ────────────────────────────────────────────────

class PublicChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    model: Optional[str] = "llama-3.3-70b-versatile"
    temperature: Optional[float] = 0.1
    max_tokens: Optional[int] = 2048


class PublicChatResponse(BaseModel):
    answer: str
    session_id: str
    status: str = "ok"


# ─── API Key helper ───────────────────────────────────────────────────────────

def _check_api_key(x_api_key: Optional[str]) -> None:
    """
    Kiểm tra API Key.
    - Nếu API_KEY không được cấu hình trong .env → bỏ qua (dev mode).
    - Nếu đã cấu hình → header X-API-Key phải khớp, nếu không → 401.
    """
    if not _API_KEY:
        return  # Dev mode: không cần key
    if x_api_key != _API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key không hợp lệ hoặc thiếu header X-API-Key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/chat",
    response_model=PublicChatResponse,
    summary="Hỏi AI — trả về JSON đồng bộ (dành cho ứng dụng bên ngoài)",
)
async def public_chat(
    request: PublicChatRequest,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
) -> PublicChatResponse:
    """
    Endpoint công khai để ứng dụng bên ngoài hỏi AI.

    Khác với `/api/analysis/chat/stream`:
    - Trả về **1 JSON duy nhất** sau khi có kết quả hoàn chỉnh (không phải SSE stream).
    - Dễ tích hợp với Power BI, Excel, Python script, n8n, v.v.

    **Ví dụ request:**
    ```json
    {
        "message": "Toyota có bao nhiêu xe?",
        "session_id": "my-app-001",
        "model": "llama-3.3-70b-versatile"
    }
    ```

    **Ví dụ response:**
    ```json
    {
        "answer": "Toyota có 5,861 xe, chiếm 17.3% thị trường...",
        "session_id": "my-app-001",
        "status": "ok"
    }
    ```
    """
    # Kiểm tra API Key
    _check_api_key(x_api_key)

    session_id = request.session_id or str(uuid.uuid4())

    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from app.api.analysis_chat import _build_llm, _build_system_prompt

        # Dùng model và temperature từ request, inference_config=None → fallback về .env
        llm = _build_llm(
            model=request.model or "llama-3.3-70b-versatile",
            temperature=request.temperature if request.temperature is not None else 0.1,
            max_tokens=request.max_tokens or 2048,
            inference_config=None,  # Dùng key từ .env
        )

        system_prompt = _build_system_prompt()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=request.message),
        ]

        # Thu thập toàn bộ stream thành 1 chuỗi hoàn chỉnh
        full_answer = ""
        async for chunk in llm.astream(messages):
            token = getattr(chunk, "content", "") or ""
            full_answer += token

        full_answer = full_answer.strip()
        if not full_answer:
            raise ValueError("LLM trả về chuỗi rỗng — kiểm tra API Key và model name.")

        return PublicChatResponse(
            answer=full_answer,
            session_id=session_id,
            status="ok",
        )

    except HTTPException:
        raise  # Giữ nguyên lỗi 401 auth
    except Exception as e:
        logger.error("[PublicAPI] Lỗi xử lý chat: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi xử lý yêu cầu: {str(e)}",
        )


@router.get("/health", summary="Kiểm tra trạng thái Public API")
async def public_health():
    """Kiểm tra nhanh endpoint public có hoạt động không."""
    return {
        "status": "ok",
        "api_key_required": bool(_API_KEY),
        "available_endpoints": [
            "POST /api/public/chat",
            "GET  /api/public/health",
        ],
        "docs": "http://localhost:8000/docs#/Public%20API",
    }

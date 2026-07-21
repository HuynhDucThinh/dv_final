"""
Auth dependencies cho FastAPI.
Hỗ trợ 2 phương thức xác thực:
  1. X-User-Id header (trusted internal) — từ Next.js server, đã verify bởi Better Auth
  2. Authorization: Bearer JWT — fallback cho direct API calls (nếu cần)
"""
from typing import Optional
from fastapi import Header, HTTPException
from app.utils.logging import setup_logger

logger = setup_logger("vietcar.auth")


async def get_current_user_id(
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
    authorization: Optional[str] = Header(default=None),
) -> Optional[str]:
    """
    FastAPI dependency — trả về user_id nếu request có thông tin auth hợp lệ.
    
    Ưu tiên:
      1. X-User-Id header (từ Next.js server proxy — đã xác thực bởi Better Auth)
      2. Authorization: Bearer JWT (fallback — verify bằng BETTER_AUTH_SECRET)
    
    Trả về None nếu không có auth (guest mode).
    """
    # 1. Trusted internal header từ Next.js server
    if x_user_id and x_user_id.strip():
        return x_user_id.strip()

    # 2. Fallback: JWT Bearer token (cho direct API calls)
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        if token:
            payload = _decode_jwt(token)
            if payload:
                return payload.get("sub")

    return None


async def require_user_id(
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
    authorization: Optional[str] = Header(default=None),
) -> str:
    """
    FastAPI dependency — yêu cầu bắt buộc phải đăng nhập.
    Dùng cho các endpoint chỉ dành cho authenticated users.
    """
    user_id = await get_current_user_id(x_user_id=x_user_id, authorization=authorization)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please sign in.",
        )
    return user_id


def _decode_jwt(token: str) -> Optional[dict]:
    """Decode và verify JWT token (fallback method)."""
    try:
        from jose import jwt
        from app.config import BETTER_AUTH_SECRET
        if not BETTER_AUTH_SECRET:
            return None
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        return payload
    except Exception as exc:
        logger.debug("JWT decode failed: %s", exc)
        return None

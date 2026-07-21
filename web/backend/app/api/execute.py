"""
API Thực thi code — nhận code đã được người dùng phê duyệt,
chạy exec() trong sandbox, trả về stdout + hình ảnh biểu đồ (base64).

NGUYÊN TẮC: Code chỉ được thực thi khi con người đã chấp thuận.
"""
import base64
import io
import sys
import traceback
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/analysis", tags=["AI Analysis"])


class ExecuteRequest(BaseModel):
    code: str
    session_id: str = "unknown"


class ExecuteResponse(BaseModel):
    success: bool
    stdout: str
    stderr: str
    images: list[str]  # Base64 PNG strings
    error: str | None = None


@router.post("/execute", response_model=ExecuteResponse)
async def execute_code(req: ExecuteRequest) -> ExecuteResponse:
    """
    Thực thi code Python đã được người dùng phê duyệt.
    Chỉ chạy trên môi trường local — không thực thi online.
    """
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    images: list[str] = []

    # Namespace sandbox với các thư viện phân tích dữ liệu
    namespace: dict[str, Any] = {}
    try:
        import pandas as pd
        import numpy as np
        namespace["pd"] = pd
        namespace["np"] = np
    except ImportError:
        pass

    # Cấu hình matplotlib để capture ảnh thay vì hiển thị cửa sổ
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        namespace["plt"] = plt
        namespace["matplotlib"] = matplotlib
    except ImportError:
        plt = None

    # Redirect stdout/stderr
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = stdout_buf
    sys.stderr = stderr_buf

    error_msg: str | None = None
    try:
        exec(req.code, namespace)  # noqa: S102

        # Thu thập tất cả figures đang mở
        if plt is not None:
            for fig_num in plt.get_fignums():
                fig = plt.figure(fig_num)
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
                buf.seek(0)
                images.append(base64.b64encode(buf.read()).decode("utf-8"))
                buf.close()
            plt.close("all")

    except Exception:
        error_msg = traceback.format_exc()
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    return ExecuteResponse(
        success=error_msg is None,
        stdout=stdout_buf.getvalue(),
        stderr=stderr_buf.getvalue(),
        images=images,
        error=error_msg,
    )

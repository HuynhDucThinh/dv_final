"""
API Thực thi code — nhận code đã được người dùng phê duyệt,
chạy exec() trong sandbox, trả về stdout + hình ảnh biểu đồ (base64).

NGUYÊN TẮC:
- Code chỉ được thực thi khi con người đã chấp thuận (human-in-the-loop).
- Namespace được giữ theo session: biến df và các biến khác tồn tại xuyên suốt
  một session chat — không cần load lại df ở mỗi bước phân tích tiếp theo.
- Mỗi lần thực thi tự động log vào analysis_logs.jsonl.
"""
import base64
import io
import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/analysis", tags=["AI Analysis"])

# ─── Persistent namespace per session ────────────────────────────────────────
# Key: session_id  →  Value: dict chứa các biến Python đang tồn tại trong session
# Mục đích: df, variables khác được giữ nguyên giữa các lần exec() trong cùng session.
_SESSION_NAMESPACES: dict[str, dict] = {}

# ─── Log file ──────────────────────────────────────────────────────────────
_LOGS_DIR = Path(__file__).resolve().parents[2] / "logs"
_LOGS_DIR.mkdir(exist_ok=True)
_EXEC_LOG_FILE = _LOGS_DIR / "analysis_logs.jsonl"


# ─── Models ────────────────────────────────────────────────────────────────
class ExecuteRequest(BaseModel):
    code: str
    session_id: str = "unknown"
    language: str = "python"


class ExecuteResponse(BaseModel):
    success: bool
    stdout: str
    stderr: str
    images: list[str]   # Base64 PNG strings
    error: str | None = None
    df_context: str = ""  # Snapshot trạng thái DataFrame sau thực thi — dùng để inject vào AI context


# ─── Helpers ───────────────────────────────────────────────────────────────

def _get_or_create_namespace(session_id: str) -> dict[str, Any]:
    """
    Lấy namespace hiện có của session hoặc tạo mới nếu chưa có.
    Namespace mới được pre-populate với pandas, numpy, matplotlib.
    """
    if session_id != "unknown" and session_id in _SESSION_NAMESPACES:
        return _SESSION_NAMESPACES[session_id]

    ns: dict[str, Any] = {}

    # Pre-populate thư viện phân tích dữ liệu
    try:
        import pandas as pd
        import numpy as np
        ns["pd"] = pd
        ns["np"] = np
        
        # Tự động load df mặc định để tránh lỗi NameError nếu AI viết code biến df trực tiếp
        from app.services.data_context import get_data_file_path, PROCESSED_CSV
        data_path = get_data_file_path() or str(PROCESSED_CSV)
        if data_path:
            try:
                from app.api.analysis_chat import _get_cached_df
                cached_df = _get_cached_df()
                if cached_df is not None:
                    ns["df"] = cached_df.copy()
            except Exception:
                pass

            if "df" not in ns:
                try:
                    ns["df"] = pd.read_csv(data_path, low_memory=False, encoding="utf-8-sig", encoding_errors="replace")
                except Exception:
                    try:
                        ns["df"] = pd.read_csv(data_path, low_memory=False, encoding="utf-8", encoding_errors="replace")
                    except Exception:
                        pass
            
    except ImportError:
        pass

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns
        ns["plt"] = plt
        ns["matplotlib"] = matplotlib
        ns["sns"] = sns
    except ImportError:
        pass

    try:
        from sklearn import preprocessing, metrics, model_selection
        ns["preprocessing"] = preprocessing
        ns["metrics"] = metrics
        ns["model_selection"] = model_selection
    except ImportError:
        pass

    if session_id != "unknown":
        _SESSION_NAMESPACES[session_id] = ns

    return ns


def _capture_df_context(namespace: dict[str, Any]) -> str:
    """
    Snapshot trạng thái DataFrame hiện tại từ namespace.
    Kết quả được inject vào hidden message gửi cho AI để AI biết
    trạng thái dữ liệu MỚI NHẤT sau khi user thực thi code.
    """
    if "df" not in namespace:
        return ""
    df = namespace["df"]
    if not hasattr(df, "shape"):
        return ""
    try:
        n_rows, n_cols = df.shape
        null_counts = df.isnull().sum()
        null_cols = null_counts[null_counts > 0]

        if null_cols.empty:
            null_str = "  (Không có cột null)"
        else:
            null_str = "\n".join(
                f"  - `{col}`: {cnt:,} null ({cnt / n_rows * 100:.1f}%)"
                for col, cnt in null_cols.items()
            )

        # Liệt kê tên cột và dtype
        dtype_lines = "\n".join(
            f"  - `{col}` ({dtype})" for col, dtype in df.dtypes.items()
        )

        return (
            f"[TRẠNG THÁI DATAFRAME SAU THỰC THI]\n"
            f"- Shape: {n_rows:,} dòng × {n_cols} cột\n"
            f"- Các cột:\n{dtype_lines}\n"
            f"- Cột còn null:\n{null_str}"
        )
    except Exception:
        try:
            return f"[DATAFRAME]: shape={df.shape}"
        except Exception:
            return ""


def _save_exec_log(
    session_id: str,
    code: str,
    stdout: str,
    stderr: str,
    images_count: int,
    error: str | None,
    df_context: str,
) -> None:
    """
    Tự động lưu log mỗi lần thực thi code.
    Tuân thủ yêu cầu 'API Logs bắt buộc' — lưu trữ mã nguồn + kết quả phân tích.
    """
    try:
        record = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "user_request": "[Code execution via InteractiveCodeBlock]",
            "code": code,
            "execution_result": stdout[:3000] if stdout else "",
            "stderr": stderr[:500] if stderr else "",
            "charts_count": images_count,
            "error": error[:500] if error else None,
            "df_context": df_context[:800] if df_context else "",
        }
        with _EXEC_LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass  # Log failure không ảnh hưởng response trả về user


# ─── Endpoint ──────────────────────────────────────────────────────────────

@router.post("/execute", response_model=ExecuteResponse)
async def execute_code(req: ExecuteRequest) -> ExecuteResponse:
    """
    Thực thi code Python đã được người dùng phê duyệt.

    - Namespace persistent theo session: biến (df, ...) giữ nguyên giữa các lần exec.
    - Sau thực thi: snapshot df_context và trả về — frontend dùng để inject vào AI history.
    - Tự động log vào analysis_logs.jsonl.
    """
    if req.language.lower() not in ("python", "py", "python3", ""):
        return ExecuteResponse(
            success=False,
            stdout="",
            stderr="",
            images=[],
            error=f"Chỉ hỗ trợ thực thi code Python. Ngôn ngữ '{req.language}' không được hỗ trợ.",
        )

    namespace = _get_or_create_namespace(req.session_id)

    def _run_code() -> tuple[str, str, list[str], str | None]:
        """Thực thi code trong thread pool để không block async event loop."""
        stdout_b = io.StringIO()
        stderr_b = io.StringIO()
        imgs: list[str] = []
        err: str | None = None

        old_stdout, old_stderr = sys.stdout, sys.stderr
        old_cwd = os.getcwd()
        project_root = Path(__file__).resolve().parents[4]

        sys.stdout = stdout_b
        sys.stderr = stderr_b

        # Tự động đảm bảo mọi lệnh to_csv() đều có encoding='utf-8-sig' để Excel không bị lỗi font tiếng Việt
        import pandas as pd
        _orig_to_csv = pd.DataFrame.to_csv
        def _safe_to_csv(self, *args, **kwargs):
            if "encoding" not in kwargs:
                kwargs["encoding"] = "utf-8-sig"
            return _orig_to_csv(self, *args, **kwargs)

        pd.DataFrame.to_csv = _safe_to_csv

        try:
            os.chdir(project_root)
            exec(req.code, namespace)  # noqa: S102

            # Thu thập tất cả figures đang mở
            plt = namespace.get("plt")
            if plt is not None:
                for fig_num in plt.get_fignums():
                    fig = plt.figure(fig_num)
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
                    buf.seek(0)
                    imgs.append(base64.b64encode(buf.read()).decode("utf-8"))
                    buf.close()
                plt.close("all")

        except Exception:
            err = traceback.format_exc()
        finally:
            pd.DataFrame.to_csv = _orig_to_csv
            os.chdir(old_cwd)
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        return stdout_b.getvalue(), stderr_b.getvalue(), imgs, err

    import asyncio
    loop = asyncio.get_event_loop()
    stdout_val, stderr_val, images, error_msg = await loop.run_in_executor(None, _run_code)

    # Snapshot df state SAU khi thực thi (chỉ khi thành công)
    df_context = _capture_df_context(namespace) if error_msg is None else ""

    # Tự động lưu log
    _save_exec_log(req.session_id, req.code, stdout_val, stderr_val, len(images), error_msg, df_context)

    return ExecuteResponse(
        success=error_msg is None,
        stdout=stdout_val,
        stderr=stderr_val,
        images=images,
        error=error_msg,
        df_context=df_context,
    )


@router.delete("/session/{session_id}", tags=["AI Analysis"])
async def clear_session_namespace(session_id: str) -> dict:
    """Xóa namespace của session (dùng khi bắt đầu chat mới để tránh rò rỉ bộ nhớ)."""
    removed = _SESSION_NAMESPACES.pop(session_id, None)
    return {"cleared": removed is not None, "session_id": session_id}

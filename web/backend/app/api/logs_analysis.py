"""
API Logs phân tích dữ liệu — lưu trữ tất cả yêu cầu, mã nguồn, kết quả.
Theo nguyên tắc "Lưu trữ" trong yêu cầu đồ án.
"""
import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Analysis Logs"])

# Thư mục lưu logs
LOGS_DIR = Path(__file__).resolve().parents[2] / "logs"
LOGS_DIR.mkdir(exist_ok=True)
ANALYSIS_LOG_FILE = LOGS_DIR / "analysis_logs.jsonl"


class AnalysisLogEntry(BaseModel):
    session_id: str
    timestamp: str = ""
    user_request: str
    ai_response: str = ""
    code: str = ""
    execution_result: str = ""
    charts_count: int = 0


class LogsResponse(BaseModel):
    entries: list[dict]
    total: int


@router.post("/log")
async def save_analysis_log(entry: AnalysisLogEntry) -> dict:
    """Lưu một bản ghi phân tích vào file JSONL."""
    if not entry.timestamp:
        entry.timestamp = datetime.now().isoformat()

    record = entry.model_dump()

    with ANALYSIS_LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {"status": "saved", "timestamp": entry.timestamp}


@router.get("/history", response_model=LogsResponse)
async def get_analysis_logs(session_id: str | None = None, limit: int = 50) -> LogsResponse:
    """Truy vấn lịch sử logs phân tích."""
    if not ANALYSIS_LOG_FILE.exists():
        return LogsResponse(entries=[], total=0)

    entries = []
    with ANALYSIS_LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if session_id is None or record.get("session_id") == session_id:
                    entries.append(record)
            except json.JSONDecodeError:
                continue

    # Lấy entries mới nhất
    entries = entries[-limit:]
    entries.reverse()

    return LogsResponse(entries=entries, total=len(entries))

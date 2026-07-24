"""
Pydantic Models cho File Operations API.

Models cho:
1. File operation requests (từ LLM tools)
2. Approval requests (từ Frontend)
3. API responses
"""
from typing import Optional, Literal, List
from pydantic import BaseModel, Field, field_validator


# ─── FILE OPERATION REQUESTS ─────────────────────────────────────────────────

class ReadFileRequest(BaseModel):
    """Request để đọc file."""
    file_path: str = Field(..., description="Đường dẫn file cần đọc")


class ListFilesRequest(BaseModel):
    """Request để liệt kê files trong thư mục."""
    directory: str = Field(..., description="Đường dẫn thư mục")
    pattern: str = Field(default="*", description="Glob pattern (vd: *.csv, report_*)")
    recursive: bool = Field(default=False, description="Tìm kiếm đệ quy")


class CreateFileRequest(BaseModel):
    """Request để tạo file mới."""
    file_path: str = Field(..., description="Đường dẫn file cần tạo")
    content: str = Field(..., description="Nội dung file")
    overwrite: bool = Field(default=False, description="Ghi đè nếu file đã tồn tại")


class ModifyFileRequest(BaseModel):
    """Request để sửa file."""
    file_path: str = Field(..., description="Đường dẫn file cần sửa")
    operation: Literal["append", "replace", "insert", "delete_line"] = Field(
        ...,
        description="Loại thao tác: append (thêm cuối), replace (thay thế), insert (chèn), delete_line (xóa dòng)"
    )
    content: Optional[str] = Field(default="", description="Nội dung mới (cho append/replace/insert)")
    line_number: Optional[int] = Field(default=None, description="Số dòng (cho insert/delete_line, bắt đầu từ 1)")
    search_text: Optional[str] = Field(default=None, description="Text cần tìm (cho replace)")
    
    @field_validator("line_number")
    @classmethod
    def validate_line_number(cls, v):
        if v is not None and v < 1:
            raise ValueError("line_number phải >= 1")
        return v


class DeleteFileRequest(BaseModel):
    """Request để xóa file."""
    file_path: str = Field(..., description="Đường dẫn file cần xóa")
    force: bool = Field(default=False, description="Bỏ qua cảnh báo (khi user đã xác nhận)")


class MoveRenameFileRequest(BaseModel):
    """Request để di chuyển/đổi tên file."""
    source: str = Field(..., description="Đường dẫn file nguồn")
    destination: str = Field(..., description="Đường dẫn file đích")
    overwrite: bool = Field(default=False, description="Ghi đè nếu file đích đã tồn tại")


# ─── APPROVAL WORKFLOW REQUESTS ──────────────────────────────────────────────

class ApprovalDecisionRequest(BaseModel):
    """Request từ Frontend để approve/reject action."""
    action_id: str = Field(..., description="ID của pending action")
    decision: Literal["approve", "reject"] = Field(..., description="Quyết định: approve hoặc reject")
    reason: Optional[str] = Field(default=None, description="Lý do (cho reject)")


class ExecuteApprovedActionRequest(BaseModel):
    """Request để thực thi action đã được approve."""
    action_id: str = Field(..., description="ID của action đã được approve")


# ─── API RESPONSES ───────────────────────────────────────────────────────────

class FileInfo(BaseModel):
    """Thông tin về một file."""
    name: str
    path: str
    size: int
    type: str


class ReadFileResponse(BaseModel):
    """Response khi đọc file thành công."""
    success: bool
    content: Optional[str] = None
    size_bytes: Optional[int] = None
    encoding: Optional[str] = None
    lines: Optional[int] = None
    error: Optional[str] = None


class ListFilesResponse(BaseModel):
    """Response khi list files thành công."""
    success: bool
    files: Optional[List[FileInfo]] = None
    count: Optional[int] = None
    error: Optional[str] = None


class CreateFileResponse(BaseModel):
    """Response khi tạo file thành công."""
    success: bool
    path: Optional[str] = None
    size_bytes: Optional[int] = None
    existed_before: Optional[bool] = None
    error: Optional[str] = None


class ModifyFileResponse(BaseModel):
    """Response khi sửa file thành công."""
    success: bool
    operation: Optional[str] = None
    lines_affected: Optional[int] = None
    new_size_bytes: Optional[int] = None
    error: Optional[str] = None


class DeleteFileResponse(BaseModel):
    """Response khi xóa file thành công."""
    success: bool
    path: Optional[str] = None
    size_deleted: Optional[int] = None
    error: Optional[str] = None


class MoveRenameFileResponse(BaseModel):
    """Response khi move/rename file thành công."""
    success: bool
    source: Optional[str] = None
    destination: Optional[str] = None
    size_bytes: Optional[int] = None
    error: Optional[str] = None


# ─── PENDING ACTION RESPONSE ─────────────────────────────────────────────────

class PendingActionResponse(BaseModel):
    """Response chứa thông tin về một pending action."""
    action_id: str
    session_id: str
    tool_name: str
    arguments: dict
    risk_level: str
    status: str
    preview: Optional[str] = None
    created_at: str
    approved_at: Optional[str] = None
    executed_at: Optional[str] = None
    error: Optional[str] = None
    result: Optional[dict] = None


class PendingActionsListResponse(BaseModel):
    """Response chứa danh sách pending actions."""
    actions: List[PendingActionResponse]
    count: int


class ApprovalDecisionResponse(BaseModel):
    """Response sau khi approve/reject action."""
    success: bool
    action_id: str
    decision: str
    status: str
    message: Optional[str] = None
    error: Optional[str] = None


class ExecuteActionResponse(BaseModel):
    """Response sau khi thực thi action."""
    success: bool
    action_id: str
    operation_result: dict
    message: Optional[str] = None
    error: Optional[str] = None

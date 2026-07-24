"""
Approval Workflow Service — Quản lý pending file operations.

Workflow:
1. AI gọi file operation tool
2. Tool tạo PendingAction với risk level
3. Nếu risk >= MEDIUM → Đưa vào queue chờ phê duyệt
4. Frontend hiển thị modal yêu cầu user approve/reject
5. User approve → Execute operation
6. User reject → Discard operation

Risk Levels:
- LOW: Read-only operations (auto-approve)
- MEDIUM: Create new file, append to file
- HIGH: Modify existing file, move/rename file
- CRITICAL: Delete file
"""
import uuid
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Literal
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ─── RISK CLASSIFICATION ─────────────────────────────────────────────────────

class RiskLevel(str, Enum):
    """Risk level cho file operations."""
    LOW = "low"           # Read-only - auto approve
    MEDIUM = "medium"     # Create new file
    HIGH = "high"         # Modify/move file
    CRITICAL = "critical" # Delete file


class ActionStatus(str, Enum):
    """Status của pending action."""
    PENDING = "pending"       # Chờ phê duyệt
    APPROVED = "approved"     # Đã được approve
    REJECTED = "rejected"     # Bị từ chối
    EXECUTED = "executed"     # Đã thực thi thành công
    FAILED = "failed"         # Thực thi thất bại


# ─── DATA MODELS ─────────────────────────────────────────────────────────────

@dataclass
class PendingAction:
    """Một file operation đang chờ phê duyệt."""
    
    action_id: str
    session_id: str
    tool_name: str  # "create_file", "modify_file", "delete_file", ...
    arguments: dict
    risk_level: RiskLevel
    status: ActionStatus = ActionStatus.PENDING
    preview: Optional[str] = None  # Preview content hoặc diff
    created_at: datetime = field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[dict] = None
    
    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            "action_id": self.action_id,
            "session_id": self.session_id,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "risk_level": self.risk_level.value,
            "status": self.status.value,
            "preview": self.preview,
            "created_at": self.created_at.isoformat(),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "error": self.error,
            "result": self.result,
        }


# ─── IN-MEMORY QUEUE ─────────────────────────────────────────────────────────

class ApprovalWorkflowManager:
    """
    Singleton quản lý pending actions trong memory.
    
    Note: Trong production nên dùng Redis hoặc DB để persist queue.
    """
    
    def __init__(self):
        self._actions: Dict[str, PendingAction] = {}
        self._session_actions: Dict[str, list[str]] = {}  # session_id -> [action_ids]
    
    def create_action(
        self,
        session_id: str,
        tool_name: str,
        arguments: dict,
        preview: Optional[str] = None,
    ) -> PendingAction:
        """
        Tạo pending action mới.
        
        Args:
            session_id: ID của chat session
            tool_name: Tên tool (create_file, modify_file, ...)
            arguments: Arguments của tool call
            preview: Preview nội dung (cho frontend hiển thị)
            
        Returns:
            PendingAction object
        """
        action_id = str(uuid.uuid4())
        
        # Determine risk level
        risk_level = self._classify_risk(tool_name, arguments)
        
        action = PendingAction(
            action_id=action_id,
            session_id=session_id,
            tool_name=tool_name,
            arguments=arguments,
            risk_level=risk_level,
            preview=preview,
        )
        
        self._actions[action_id] = action
        
        if session_id not in self._session_actions:
            self._session_actions[session_id] = []
        self._session_actions[session_id].append(action_id)
        
        logger.info(
            f"[approval] Created action {action_id}: {tool_name} "
            f"risk={risk_level.value} session={session_id}"
        )
        
        return action
    
    def _classify_risk(self, tool_name: str, arguments: dict) -> RiskLevel:
        """Phân loại risk level dựa trên tool và arguments."""
        
        # Read-only operations
        if tool_name in ["read_file_content", "list_files"]:
            return RiskLevel.LOW
        
        # Delete operations
        if tool_name == "delete_file":
            return RiskLevel.CRITICAL
        
        # Modify existing file
        if tool_name == "modify_file":
            return RiskLevel.HIGH
        
        # Move/rename
        if tool_name == "move_rename_file":
            return RiskLevel.HIGH
        
        # Create file
        if tool_name == "create_file":
            # Check if overwriting existing file
            if arguments.get("overwrite"):
                return RiskLevel.HIGH
            return RiskLevel.MEDIUM
        
        # Default: medium
        return RiskLevel.MEDIUM
    
    def get_action(self, action_id: str) -> Optional[PendingAction]:
        """Lấy action theo ID."""
        return self._actions.get(action_id)
    
    def get_pending_actions(
        self,
        session_id: Optional[str] = None,
        status: Optional[ActionStatus] = None
    ) -> list[PendingAction]:
        """
        Lấy danh sách pending actions.
        
        Args:
            session_id: Filter theo session (None = all sessions)
            status: Filter theo status (None = all statuses)
        """
        actions = self._actions.values()
        
        if session_id:
            action_ids = self._session_actions.get(session_id, [])
            actions = [self._actions[aid] for aid in action_ids if aid in self._actions]
        
        if status:
            actions = [a for a in actions if a.status == status]
        
        # Sort by created_at (newest first)
        return sorted(actions, key=lambda a: a.created_at, reverse=True)
    
    def approve_action(self, action_id: str) -> Optional[PendingAction]:
        """
        Phê duyệt action.
        
        Returns:
            PendingAction nếu thành công, None nếu không tìm thấy
        """
        action = self._actions.get(action_id)
        if not action:
            return None
        
        if action.status != ActionStatus.PENDING:
            logger.warning(
                f"[approval] Cannot approve action {action_id}: "
                f"status={action.status.value}"
            )
            return None
        
        action.status = ActionStatus.APPROVED
        action.approved_at = datetime.utcnow()
        
        logger.info(f"[approval] Approved action {action_id}: {action.tool_name}")
        
        return action
    
    def reject_action(self, action_id: str, reason: Optional[str] = None) -> Optional[PendingAction]:
        """
        Từ chối action.
        
        Returns:
            PendingAction nếu thành công, None nếu không tìm thấy
        """
        action = self._actions.get(action_id)
        if not action:
            return None
        
        if action.status != ActionStatus.PENDING:
            logger.warning(
                f"[approval] Cannot reject action {action_id}: "
                f"status={action.status.value}"
            )
            return None
        
        action.status = ActionStatus.REJECTED
        action.error = reason or "User rejected"
        
        logger.info(
            f"[approval] Rejected action {action_id}: {action.tool_name} "
            f"reason={reason}"
        )
        
        return action
    
    def mark_executed(
        self,
        action_id: str,
        result: dict,
        success: bool = True
    ) -> Optional[PendingAction]:
        """
        Đánh dấu action đã được thực thi.
        
        Args:
            action_id: ID của action
            result: Kết quả từ file operation
            success: True nếu thành công, False nếu lỗi
        """
        action = self._actions.get(action_id)
        if not action:
            return None
        
        if action.status != ActionStatus.APPROVED:
            logger.warning(
                f"[approval] Cannot mark action {action_id} as executed: "
                f"status={action.status.value}"
            )
            return None
        
        action.status = ActionStatus.EXECUTED if success else ActionStatus.FAILED
        action.executed_at = datetime.utcnow()
        action.result = result
        
        if not success:
            action.error = result.get("error", "Unknown error")
        
        logger.info(
            f"[approval] Marked action {action_id} as "
            f"{'executed' if success else 'failed'}"
        )
        
        return action
    
    def cleanup_old_actions(self, max_age_hours: int = 24) -> int:
        """
        Dọn dẹp các actions cũ.
        
        Args:
            max_age_hours: Xóa actions cũ hơn X giờ
            
        Returns:
            Số lượng actions đã xóa
        """
        from datetime import timedelta
        
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        old_action_ids = [
            aid for aid, action in self._actions.items()
            if action.created_at < cutoff and action.status in [
                ActionStatus.EXECUTED,
                ActionStatus.FAILED,
                ActionStatus.REJECTED
            ]
        ]
        
        for aid in old_action_ids:
            action = self._actions.pop(aid)
            
            # Remove from session index
            if action.session_id in self._session_actions:
                try:
                    self._session_actions[action.session_id].remove(aid)
                except ValueError:
                    pass
        
        logger.info(f"[approval] Cleaned up {len(old_action_ids)} old actions")
        
        return len(old_action_ids)
    
    def clear_session(self, session_id: str) -> int:
        """
        Xóa tất cả actions của một session.
        
        Returns:
            Số lượng actions đã xóa
        """
        action_ids = self._session_actions.get(session_id, [])
        
        for aid in action_ids:
            self._actions.pop(aid, None)
        
        self._session_actions.pop(session_id, None)
        
        logger.info(f"[approval] Cleared {len(action_ids)} actions for session {session_id}")
        
        return len(action_ids)


# ─── SINGLETON INSTANCE ──────────────────────────────────────────────────────

_manager: Optional[ApprovalWorkflowManager] = None


def get_approval_manager() -> ApprovalWorkflowManager:
    """Get singleton instance của approval manager."""
    global _manager
    if _manager is None:
        _manager = ApprovalWorkflowManager()
    return _manager


# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────

def should_require_approval(risk_level: RiskLevel) -> bool:
    """
    Check xem risk level có cần phê duyệt không.
    
    Policy:
    - LOW: Auto-approve
    - MEDIUM+: Require approval
    """
    return risk_level != RiskLevel.LOW


def generate_preview(tool_name: str, arguments: dict, max_lines: int = 20) -> str:
    """
    Sinh preview text cho frontend hiển thị.
    
    Args:
        tool_name: Tên tool
        arguments: Arguments của tool
        max_lines: Giới hạn số dòng hiển thị
        
    Returns:
        Preview text (markdown format)
    """
    if tool_name == "create_file":
        content = arguments.get("content", "")
        lines = content.split("\n")
        
        if len(lines) > max_lines:
            preview_lines = lines[:max_lines]
            preview = "\n".join(preview_lines)
            preview += f"\n\n... ({len(lines) - max_lines} dòng còn lại)"
        else:
            preview = content
        
        return f"```\n{preview}\n```"
    
    elif tool_name == "modify_file":
        operation = arguments.get("operation")
        content = arguments.get("content", "")
        line_number = arguments.get("line_number")
        search_text = arguments.get("search_text")
        
        parts = [f"**Operation:** `{operation}`"]
        
        if line_number:
            parts.append(f"**Line:** {line_number}")
        
        if search_text:
            parts.append(f"**Search:** `{search_text}`")
        
        if content:
            parts.append(f"**New content:**\n```\n{content[:500]}\n```")
        
        return "\n\n".join(parts)
    
    elif tool_name == "delete_file":
        file_path = arguments.get("file_path", "")
        return f"⚠️ **Xóa vĩnh viễn file:**\n`{file_path}`"
    
    elif tool_name == "move_rename_file":
        source = arguments.get("source", "")
        destination = arguments.get("destination", "")
        return f"**From:** `{source}`\n**To:** `{destination}`"
    
    else:
        return f"Arguments: {arguments}"

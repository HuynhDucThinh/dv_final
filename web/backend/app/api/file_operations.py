"""
File Operations API — Endpoints cho approval workflow.

Endpoints:
1. GET  /api/file-operations/pending          — Lấy danh sách pending actions
2. POST /api/file-operations/{action_id}/approve — Approve action
3. POST /api/file-operations/{action_id}/reject  — Reject action
4. POST /api/file-operations/{action_id}/execute — Execute approved action
5. DELETE /api/file-operations/session/{session_id} — Clear session actions

Note: File operations được gọi trực tiếp từ LLM tools (không qua API),
      chỉ có approval workflow cần REST API cho Frontend.
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.api.auth_deps import get_current_user_id
from app.models.file_operations import (
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ExecuteActionResponse,
    PendingActionsListResponse,
    PendingActionResponse,
)
from app.services.approval_workflow import (
    get_approval_manager,
    ActionStatus,
)
from app.services import file_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/file-operations", tags=["File Operations"])


# ─── GET PENDING ACTIONS ─────────────────────────────────────────────────────

@router.get("/pending", response_model=PendingActionsListResponse)
async def get_pending_actions(
    session_id: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[str] = Depends(get_current_user_id)
):
    """
    Lấy danh sách pending actions.
    
    Query params:
        session_id: Filter theo session (optional)
        status: Filter theo status (optional)
    """
    try:
        manager = get_approval_manager()
        
        # Parse status
        status_filter = None
        if status:
            try:
                status_filter = ActionStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status: {status}. Valid: pending, approved, rejected, executed, failed"
                )
        
        actions = manager.get_pending_actions(
            session_id=session_id,
            status=status_filter
        )
        
        return PendingActionsListResponse(
            actions=[
                PendingActionResponse(**action.to_dict())
                for action in actions
            ],
            count=len(actions)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pending actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── APPROVE ACTION ──────────────────────────────────────────────────────────

@router.post("/{action_id}/approve", response_model=ApprovalDecisionResponse)
async def approve_action(
    action_id: str,
    user_id: Optional[str] = Depends(get_current_user_id)
):
    """
    Phê duyệt một pending action.
    
    Path params:
        action_id: ID của action cần approve
    """
    try:
        manager = get_approval_manager()
        
        action = manager.get_action(action_id)
        if not action:
            raise HTTPException(
                status_code=404,
                detail=f"Action not found: {action_id}"
            )
        
        if action.status != ActionStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Action {action_id} is not pending (status={action.status.value})"
            )
        
        approved_action = manager.approve_action(action_id)
        if not approved_action:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to approve action {action_id}"
            )
        
        logger.info(
            f"[file_operations] Action {action_id} approved by user {user_id or 'anonymous'}"
        )
        
        return ApprovalDecisionResponse(
            success=True,
            action_id=action_id,
            decision="approve",
            status=approved_action.status.value,
            message=f"Action approved. Ready to execute."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving action {action_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── REJECT ACTION ───────────────────────────────────────────────────────────

@router.post("/{action_id}/reject", response_model=ApprovalDecisionResponse)
async def reject_action(
    action_id: str,
    request: ApprovalDecisionRequest,
    user_id: Optional[str] = Depends(get_current_user_id)
):
    """
    Từ chối một pending action.
    
    Path params:
        action_id: ID của action cần reject
        
    Body:
        reason: Lý do từ chối (optional)
    """
    try:
        manager = get_approval_manager()
        
        action = manager.get_action(action_id)
        if not action:
            raise HTTPException(
                status_code=404,
                detail=f"Action not found: {action_id}"
            )
        
        if action.status != ActionStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Action {action_id} is not pending (status={action.status.value})"
            )
        
        rejected_action = manager.reject_action(action_id, reason=request.reason)
        if not rejected_action:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to reject action {action_id}"
            )
        
        logger.info(
            f"[file_operations] Action {action_id} rejected by user {user_id or 'anonymous'}: "
            f"{request.reason or 'No reason provided'}"
        )
        
        return ApprovalDecisionResponse(
            success=True,
            action_id=action_id,
            decision="reject",
            status=rejected_action.status.value,
            message=f"Action rejected: {request.reason or 'User declined'}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting action {action_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── EXECUTE APPROVED ACTION ─────────────────────────────────────────────────

@router.post("/{action_id}/execute", response_model=ExecuteActionResponse)
async def execute_approved_action(
    action_id: str,
    user_id: Optional[str] = Depends(get_current_user_id)
):
    """
    Thực thi một action đã được approve.
    
    Path params:
        action_id: ID của action đã được approve
    """
    try:
        manager = get_approval_manager()
        
        action = manager.get_action(action_id)
        if not action:
            raise HTTPException(
                status_code=404,
                detail=f"Action not found: {action_id}"
            )
        
        if action.status != ActionStatus.APPROVED:
            raise HTTPException(
                status_code=400,
                detail=f"Action {action_id} is not approved (status={action.status.value})"
            )
        
        # Execute operation based on tool_name
        tool_name = action.tool_name
        arguments = action.arguments
        
        result = {}
        
        if tool_name == "read_file_content":
            result = file_manager.read_file_content(**arguments)
            
        elif tool_name == "list_files":
            result = file_manager.list_files(**arguments)
            
        elif tool_name == "create_file":
            result = file_manager.create_file(**arguments)
            
        elif tool_name == "modify_file":
            result = file_manager.modify_file(**arguments)
            
        elif tool_name == "delete_file":
            result = file_manager.delete_file(**arguments)
            
        elif tool_name == "move_rename_file":
            result = file_manager.move_rename_file(**arguments)
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown tool: {tool_name}"
            )
        
        # Mark as executed
        success = result.get("success", False)
        manager.mark_executed(action_id, result, success=success)
        
        logger.info(
            f"[file_operations] Action {action_id} executed: "
            f"tool={tool_name} success={success}"
        )
        
        return ExecuteActionResponse(
            success=success,
            action_id=action_id,
            operation_result=result,
            message="Operation executed successfully" if success else "Operation failed",
            error=result.get("error") if not success else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing action {action_id}: {e}")
        
        # Mark as failed
        try:
            manager = get_approval_manager()
            manager.mark_executed(action_id, {"error": str(e)}, success=False)
        except Exception:
            pass
        
        raise HTTPException(status_code=500, detail=str(e))


# ─── CLEAR SESSION ACTIONS ───────────────────────────────────────────────────

@router.delete("/session/{session_id}")
async def clear_session_actions(
    session_id: str,
    user_id: Optional[str] = Depends(get_current_user_id)
):
    """
    Xóa tất cả actions của một session.
    
    Path params:
        session_id: ID của session cần xóa actions
    """
    try:
        manager = get_approval_manager()
        
        count = manager.clear_session(session_id)
        
        logger.info(
            f"[file_operations] Cleared {count} actions for session {session_id}"
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "actions_cleared": count
        }
        
    except Exception as e:
        logger.error(f"Error clearing session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── CLEANUP OLD ACTIONS ─────────────────────────────────────────────────────

@router.post("/cleanup")
async def cleanup_old_actions(
    max_age_hours: int = 24,
    user_id: Optional[str] = Depends(get_current_user_id)
):
    """
    Dọn dẹp các actions cũ (admin endpoint).
    
    Query params:
        max_age_hours: Xóa actions cũ hơn X giờ (default: 24)
    """
    try:
        manager = get_approval_manager()
        
        count = manager.cleanup_old_actions(max_age_hours=max_age_hours)
        
        logger.info(f"[file_operations] Cleaned up {count} old actions")
        
        return {
            "success": True,
            "actions_cleaned": count,
            "max_age_hours": max_age_hours
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

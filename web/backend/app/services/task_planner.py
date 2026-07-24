"""
Task Planner Service — Multi-step planning và task decomposition.

Phase 3 Feature: Cho phép AI tự động phân tích task phức tạp thành các bước nhỏ.

Example:
    User: "Làm sạch dữ liệu và xuất 3 file báo cáo"
    AI tự động plan:
      1. Đọc file gốc
      2. Filter outliers
      3. Tạo file report_summary.csv
      4. Tạo file report_details.json
      5. Tạo file visualization.png
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

# ─── CONFIGURATION ───────────────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
PLANS_DIR = _PROJECT_ROOT / "ML" / "experiments"
PLANS_LOG = PLANS_DIR / "task_plans.jsonl"


# ─── DATA MODELS ─────────────────────────────────────────────────────────────

class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskStep:
    """A single step in task plan."""
    step_id: int
    description: str
    tool_name: Optional[str] = None
    arguments: Optional[Dict] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None
    duration_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass
class TaskPlan:
    """Complete task plan with multiple steps."""
    plan_id: str
    task_description: str
    steps: List[TaskStep]
    created_at: str
    completed_at: Optional[str] = None
    total_duration_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "plan_id": self.plan_id,
            "task_description": self.task_description,
            "steps": [step.to_dict() for step in self.steps],
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "total_duration_seconds": self.total_duration_seconds,
        }


# ─── IN-MEMORY STORAGE ───────────────────────────────────────────────────────

_ACTIVE_PLANS: Dict[str, TaskPlan] = {}


# ─── INITIALIZATION ──────────────────────────────────────────────────────────

def _ensure_plans_dir():
    """Ensure plans directory exists."""
    PLANS_DIR.mkdir(parents=True, exist_ok=True)


# ─── TASK PLANNING ───────────────────────────────────────────────────────────

def create_plan(task_description: str, steps: List[Dict]) -> dict:
    """
    Tạo task plan mới từ mô tả task.
    
    Args:
        task_description: Mô tả tổng quan của task
        steps: List of step dictionaries với format:
               {
                   "description": str,
                   "tool_name": Optional[str],
                   "arguments": Optional[Dict]
               }
    
    Returns:
        {
            "success": bool,
            "plan_id": str,
            "steps_count": int,
            "plan": dict,
            "error": Optional[str]
        }
    """
    try:
        _ensure_plans_dir()
        
        # Generate plan ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        plan_id = f"plan_{timestamp}"
        
        # Create TaskStep objects
        task_steps = []
        for i, step_dict in enumerate(steps, 1):
            task_step = TaskStep(
                step_id=i,
                description=step_dict.get("description", ""),
                tool_name=step_dict.get("tool_name"),
                arguments=step_dict.get("arguments"),
            )
            task_steps.append(task_step)
        
        # Create TaskPlan
        plan = TaskPlan(
            plan_id=plan_id,
            task_description=task_description,
            steps=task_steps,
            created_at=datetime.now().isoformat(),
        )
        
        # Store in memory
        _ACTIVE_PLANS[plan_id] = plan
        
        # Log to file
        with open(PLANS_LOG, "a", encoding="utf-8") as f:
            log_entry = {
                "timestamp": plan.created_at,
                "event": "plan_created",
                "plan_id": plan_id,
                "task_description": task_description,
                "steps_count": len(task_steps),
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        logger.info(
            f"[planner] Created plan {plan_id}: {task_description} "
            f"({len(task_steps)} steps)"
        )
        
        return {
            "success": True,
            "plan_id": plan_id,
            "steps_count": len(task_steps),
            "plan": plan.to_dict(),
        }
        
    except Exception as e:
        logger.error(f"[planner] Failed to create plan: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_plan(plan_id: str) -> Optional[dict]:
    """
    Lấy thông tin task plan.
    
    Args:
        plan_id: Plan ID
        
    Returns:
        Plan dictionary or None if not found
    """
    plan = _ACTIVE_PLANS.get(plan_id)
    if plan:
        return plan.to_dict()
    return None


def update_step_status(
    plan_id: str,
    step_id: int,
    status: TaskStatus,
    result: Optional[Dict] = None,
    error: Optional[str] = None,
    duration_seconds: Optional[float] = None,
) -> dict:
    """
    Cập nhật trạng thái của một step.
    
    Args:
        plan_id: Plan ID
        step_id: Step ID (1-indexed)
        status: New status
        result: Execution result
        error: Error message if failed
        duration_seconds: Execution duration
        
    Returns:
        {
            "success": bool,
            "step": dict,
            "error": Optional[str]
        }
    """
    try:
        plan = _ACTIVE_PLANS.get(plan_id)
        if not plan:
            return {
                "success": False,
                "error": f"Plan {plan_id} not found"
            }
        
        # Find step
        step = next((s for s in plan.steps if s.step_id == step_id), None)
        if not step:
            return {
                "success": False,
                "error": f"Step {step_id} not found in plan {plan_id}"
            }
        
        # Update step
        step.status = status
        if result:
            step.result = result
        if error:
            step.error = error
        if duration_seconds:
            step.duration_seconds = duration_seconds
        
        # Check if all steps completed
        all_done = all(
            s.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.SKIPPED]
            for s in plan.steps
        )
        
        if all_done and not plan.completed_at:
            plan.completed_at = datetime.now().isoformat()
            
            # Calculate total duration
            total = sum(s.duration_seconds or 0 for s in plan.steps)
            plan.total_duration_seconds = total
            
            logger.info(
                f"[planner] Plan {plan_id} completed in {total:.2f}s"
            )
        
        logger.info(
            f"[planner] Updated step {step_id} in plan {plan_id}: "
            f"{status.value}"
        )
        
        return {
            "success": True,
            "step": step.to_dict(),
        }
        
    except Exception as e:
        logger.error(f"[planner] Failed to update step: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def list_active_plans() -> dict:
    """
    Liệt kê tất cả active plans.
    
    Returns:
        {
            "success": bool,
            "plans": List[dict],
            "count": int
        }
    """
    try:
        plans_list = [plan.to_dict() for plan in _ACTIVE_PLANS.values()]
        
        # Sort by created_at (newest first)
        plans_list.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "success": True,
            "plans": plans_list,
            "count": len(plans_list),
        }
        
    except Exception as e:
        logger.error(f"[planner] Failed to list plans: {e}")
        return {
            "success": False,
            "error": str(e),
            "plans": [],
            "count": 0,
        }


def get_plan_summary(plan_id: str) -> dict:
    """
    Lấy summary của plan (progress, statistics).
    
    Args:
        plan_id: Plan ID
        
    Returns:
        {
            "success": bool,
            "plan_id": str,
            "task_description": str,
            "total_steps": int,
            "completed_steps": int,
            "failed_steps": int,
            "progress_percent": float,
            "is_completed": bool,
            "duration_seconds": Optional[float],
            "error": Optional[str]
        }
    """
    try:
        plan = _ACTIVE_PLANS.get(plan_id)
        if not plan:
            return {
                "success": False,
                "error": f"Plan {plan_id} not found"
            }
        
        total = len(plan.steps)
        completed = sum(1 for s in plan.steps if s.status == TaskStatus.COMPLETED)
        failed = sum(1 for s in plan.steps if s.status == TaskStatus.FAILED)
        progress = (completed / total * 100) if total > 0 else 0
        
        is_completed = all(
            s.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.SKIPPED]
            for s in plan.steps
        )
        
        return {
            "success": True,
            "plan_id": plan_id,
            "task_description": plan.task_description,
            "total_steps": total,
            "completed_steps": completed,
            "failed_steps": failed,
            "progress_percent": round(progress, 1),
            "is_completed": is_completed,
            "duration_seconds": plan.total_duration_seconds,
        }
        
    except Exception as e:
        logger.error(f"[planner] Failed to get plan summary: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def clear_plan(plan_id: str) -> dict:
    """
    Xóa plan khỏi memory.
    
    Args:
        plan_id: Plan ID
        
    Returns:
        {"success": bool, "error": Optional[str]}
    """
    try:
        if plan_id in _ACTIVE_PLANS:
            del _ACTIVE_PLANS[plan_id]
            logger.info(f"[planner] Cleared plan {plan_id}")
            return {"success": True}
        else:
            return {
                "success": False,
                "error": f"Plan {plan_id} not found"
            }
    except Exception as e:
        logger.error(f"[planner] Failed to clear plan: {e}")
        return {
            "success": False,
            "error": str(e)
        }

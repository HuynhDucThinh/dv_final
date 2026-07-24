"""
Parallel Executor Service — Execute multiple file operations concurrently.

Phase 3 Feature: Cho phép AI thực hiện nhiều thao tác file cùng lúc (nếu không conflict).

Example:
    # Tạo 3 file báo cáo cùng lúc
    await execute_parallel([
        {"tool": "create_file", "args": {"file_path": "report1.csv", ...}},
        {"tool": "create_file", "args": {"file_path": "report2.json", ...}},
        {"tool": "create_file", "args": {"file_path": "report3.md", ...}},
    ])
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


# ─── DATA MODELS ─────────────────────────────────────────────────────────────

@dataclass
class ParallelTask:
    """A single task in parallel execution."""
    task_id: str
    tool_name: str
    arguments: Dict[str, Any]
    depends_on: Optional[List[str]] = None  # Task IDs that must complete first
    
    
@dataclass
class ParallelResult:
    """Result of a parallel task execution."""
    task_id: str
    tool_name: str
    success: bool
    result: Optional[Dict] = None
    error: Optional[str] = None
    duration_seconds: Optional[float] = None


# ─── CONFLICT DETECTION ──────────────────────────────────────────────────────

def detect_file_conflicts(tasks: List[ParallelTask]) -> List[tuple]:
    """
    Phát hiện conflicts giữa các tasks (cùng thao tác trên 1 file).
    
    Args:
        tasks: List of parallel tasks
        
    Returns:
        List of (task_id1, task_id2) tuples that conflict
    """
    conflicts = []
    
    # Extract file paths from each task
    file_paths = {}
    for task in tasks:
        file_path = None
        
        # Get file_path from arguments
        if "file_path" in task.arguments:
            file_path = Path(task.arguments["file_path"]).resolve()
        elif "source" in task.arguments:  # For move_rename_file
            file_path = Path(task.arguments["source"]).resolve()
        
        if file_path:
            if file_path not in file_paths:
                file_paths[file_path] = []
            file_paths[file_path].append(task.task_id)
    
    # Check for conflicts (multiple tasks on same file)
    for path, task_ids in file_paths.items():
        if len(task_ids) > 1:
            # All pairs conflict with each other
            for i, task1 in enumerate(task_ids):
                for task2 in task_ids[i+1:]:
                    conflicts.append((task1, task2))
    
    return conflicts


def can_execute_parallel(tasks: List[ParallelTask]) -> dict:
    """
    Kiểm tra xem các tasks có thể thực hiện parallel hay không.
    
    Args:
        tasks: List of parallel tasks
        
    Returns:
        {
            "can_parallel": bool,
            "conflicts": List[tuple],
            "message": str
        }
    """
    if not tasks:
        return {
            "can_parallel": True,
            "conflicts": [],
            "message": "No tasks to execute"
        }
    
    conflicts = detect_file_conflicts(tasks)
    
    if conflicts:
        return {
            "can_parallel": False,
            "conflicts": conflicts,
            "message": f"Detected {len(conflicts)} file conflicts"
        }
    
    return {
        "can_parallel": True,
        "conflicts": [],
        "message": f"All {len(tasks)} tasks can execute in parallel"
    }


# ─── PARALLEL EXECUTION ──────────────────────────────────────────────────────

async def execute_task_async(
    task: ParallelTask,
    tool_map: Dict[str, Callable]
) -> ParallelResult:
    """
    Execute a single task asynchronously.
    
    Args:
        task: Task to execute
        tool_map: Dictionary mapping tool names to functions
        
    Returns:
        ParallelResult
    """
    start_time = datetime.now()
    
    try:
        # Get tool function
        tool_func = tool_map.get(task.tool_name)
        if not tool_func:
            return ParallelResult(
                task_id=task.task_id,
                tool_name=task.tool_name,
                success=False,
                error=f"Tool {task.tool_name} not found in tool_map",
            )
        
        # Execute tool (run in thread pool since most tools are sync)
        loop = asyncio.get_event_loop()
        
        # run_in_executor doesn't support kwargs, so use lambda
        result = await loop.run_in_executor(
            None, 
            lambda: tool_func(**task.arguments)
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return ParallelResult(
            task_id=task.task_id,
            tool_name=task.tool_name,
            success=result.get("success", False),
            result=result,
            duration_seconds=duration,
        )
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"[parallel] Task {task.task_id} failed: {e}")
        
        return ParallelResult(
            task_id=task.task_id,
            tool_name=task.tool_name,
            success=False,
            error=str(e),
            duration_seconds=duration,
        )


async def execute_parallel(
    tasks: List[ParallelTask],
    tool_map: Dict[str, Callable],
    check_conflicts: bool = True,
) -> dict:
    """
    Execute multiple tasks in parallel.
    
    Args:
        tasks: List of tasks to execute
        tool_map: Dictionary mapping tool names to functions
        check_conflicts: Whether to check for conflicts before execution
        
    Returns:
        {
            "success": bool,
            "results": List[ParallelResult],
            "total_duration_seconds": float,
            "conflicts_detected": bool,
            "conflicts": List[tuple],
            "error": Optional[str]
        }
    """
    try:
        start_time = datetime.now()
        
        # Check conflicts
        if check_conflicts:
            conflict_check = can_execute_parallel(tasks)
            if not conflict_check["can_parallel"]:
                logger.warning(
                    f"[parallel] Cannot execute parallel: "
                    f"{conflict_check['message']}"
                )
                return {
                    "success": False,
                    "results": [],
                    "total_duration_seconds": 0,
                    "conflicts_detected": True,
                    "conflicts": conflict_check["conflicts"],
                    "error": conflict_check["message"],
                }
        
        # Execute all tasks concurrently
        logger.info(f"[parallel] Executing {len(tasks)} tasks in parallel...")
        
        task_coroutines = [
            execute_task_async(task, tool_map)
            for task in tasks
        ]
        
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Process results
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"[parallel] Task raised exception: {result}")
                valid_results.append(ParallelResult(
                    task_id="unknown",
                    tool_name="unknown",
                    success=False,
                    error=str(result),
                ))
            else:
                valid_results.append(result)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # Count successes
        success_count = sum(1 for r in valid_results if r.success)
        
        logger.info(
            f"[parallel] Completed {len(tasks)} tasks in {duration:.2f}s "
            f"({success_count} succeeded, {len(tasks) - success_count} failed)"
        )
        
        return {
            "success": True,
            "results": valid_results,
            "total_duration_seconds": duration,
            "conflicts_detected": False,
            "conflicts": [],
        }
        
    except Exception as e:
        logger.error(f"[parallel] Parallel execution failed: {e}")
        return {
            "success": False,
            "results": [],
            "total_duration_seconds": 0,
            "conflicts_detected": False,
            "conflicts": [],
            "error": str(e),
        }


def execute_parallel_sync(
    tasks: List[ParallelTask],
    tool_map: Dict[str, Callable],
    check_conflicts: bool = True,
) -> dict:
    """
    Synchronous wrapper for execute_parallel (for non-async contexts).
    
    Args:
        tasks: List of tasks to execute
        tool_map: Dictionary mapping tool names to functions
        check_conflicts: Whether to check for conflicts
        
    Returns:
        Same as execute_parallel
    """
    try:
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run async function
        return loop.run_until_complete(
            execute_parallel(tasks, tool_map, check_conflicts)
        )
        
    except Exception as e:
        logger.error(f"[parallel] Sync execution failed: {e}")
        return {
            "success": False,
            "results": [],
            "total_duration_seconds": 0,
            "conflicts_detected": False,
            "conflicts": [],
            "error": str(e),
        }


# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────

def create_batch_tasks(
    tool_name: str,
    file_paths: List[str],
    common_args: Optional[Dict] = None,
) -> List[ParallelTask]:
    """
    Tạo batch tasks cho cùng một tool với nhiều files.
    
    Args:
        tool_name: Tool to execute
        file_paths: List of file paths
        common_args: Common arguments for all tasks
        
    Returns:
        List of ParallelTask
    """
    common_args = common_args or {}
    
    tasks = []
    for i, file_path in enumerate(file_paths):
        task = ParallelTask(
            task_id=f"batch_{i+1}",
            tool_name=tool_name,
            arguments={"file_path": file_path, **common_args},
        )
        tasks.append(task)
    
    return tasks

"""
Backup Service — Auto-backup files trước khi modify/delete và rollback mechanism.

Features:
1. Auto-backup trước mỗi thao tác nguy hiểm (modify/delete)
2. File versioning với timestamp
3. Rollback to previous version
4. Change history tracking
5. Auto-cleanup old backups

Backup Structure:
    backup/
    ├── 2025-01-23_14-30-15_dim_brand.csv.bak
    ├── 2025-01-23_14-32-08_report.md.bak
    └── rollback_log.jsonl
"""
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)

# ─── CONFIGURATION ───────────────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
BACKUP_DIR = _PROJECT_ROOT / "backup"
ROLLBACK_LOG = BACKUP_DIR / "rollback_log.jsonl"

# Auto-cleanup: Xóa backups cũ hơn N ngày
MAX_BACKUP_AGE_DAYS = 30

# Max backup files per file (giữ tối đa N versions)
MAX_VERSIONS_PER_FILE = 10


# ─── INITIALIZATION ──────────────────────────────────────────────────────────

def _ensure_backup_dir():
    """Ensure backup directory exists."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# ─── BACKUP OPERATIONS ───────────────────────────────────────────────────────

def create_backup(file_path: str, operation: str = "modify") -> dict:
    """
    Tạo backup của file trước khi modify/delete.
    
    Args:
        file_path: Đường dẫn file cần backup
        operation: Loại thao tác (modify, delete, move)
        
    Returns:
        {
            "success": bool,
            "backup_path": str,
            "original_size": int,
            "timestamp": str,
            "error": Optional[str]
        }
    """
    try:
        _ensure_backup_dir()
        
        source = Path(file_path)
        if not source.is_absolute():
            source = (_PROJECT_ROOT / source).resolve()
            
        if not source.exists():
            return {
                "success": False,
                "error": f"File không tồn tại: {file_path}"
            }
        
        # Generate backup filename with timestamp (including microseconds to avoid conflicts)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        backup_name = f"{timestamp}_{source.name}.bak"
        backup_path = BACKUP_DIR / backup_name
        
        # Copy file to backup
        shutil.copy2(source, backup_path)
        
        original_size = source.stat().st_size
        
        # Log to rollback log
        log_entry = {
            "timestamp": timestamp,
            "operation": operation,
            "original_path": str(source),
            "backup_path": str(backup_path),
            "original_size": original_size,
        }
        
        with open(ROLLBACK_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        logger.info(
            f"[backup] Created backup: {source.name} → {backup_name} "
            f"({original_size} bytes, operation={operation})"
        )
        
        return {
            "success": True,
            "backup_path": str(backup_path),
            "original_size": original_size,
            "timestamp": timestamp,
        }
        
    except Exception as e:
        logger.error(f"[backup] Failed to create backup for {file_path}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def rollback_last_change(file_path: Optional[str] = None, target_backup: Optional[str] = None) -> dict:
    """
    Hoàn tác thay đổi gần nhất hoặc hoàn tác về phiên bản backup cụ thể.
    
    Args:
        file_path: Đường dẫn file cần rollback
        target_backup: Tên file backup hoặc timestamp cụ thể (VD: 2026-07-24_11-30-38-350901_test_chart.py.bak)
        
    Returns:
        {
            "success": bool,
            "restored_file": str,
            "backup_used": str,
            "timestamp": str,
            "error": Optional[str]
        }
    """
    try:
        _ensure_backup_dir()
        
        if not ROLLBACK_LOG.exists():
            return {
                "success": False,
                "error": "Không tìm thấy lịch sử backup"
            }
        
        # Read rollback log
        with open(ROLLBACK_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if not lines:
            return {
                "success": False,
                "error": "Không có backup nào để rollback"
            }
        
        target_log = None
        
        # Search by specific target_backup filename or timestamp if provided
        if target_backup:
            clean_target = Path(target_backup).name
            for line in reversed(lines):
                entry = json.loads(line)
                b_path = Path(entry["backup_path"])
                if b_path.name == clean_target or clean_target in b_path.name or (entry.get("timestamp") and entry["timestamp"] in clean_target):
                    target_log = entry
                    break
            
            # If not in log, check if file exists directly in BACKUP_DIR
            if not target_log:
                direct_b_path = BACKUP_DIR / clean_target
                if direct_b_path.exists() and file_path:
                    source_p = Path(file_path)
                    if not source_p.is_absolute():
                        source_p = (_PROJECT_ROOT / source_p).resolve()
                    shutil.copy2(direct_b_path, source_p)
                    return {
                        "success": True,
                        "restored_file": str(source_p),
                        "backup_used": str(direct_b_path),
                        "timestamp": "Custom Backup",
                    }
        
        # Find last backup for specific file
        if not target_log and file_path:
            file_path_resolved = Path(file_path)
            if not file_path_resolved.is_absolute():
                file_path_resolved = (_PROJECT_ROOT / file_path_resolved).resolve()
            else:
                file_path_resolved = file_path_resolved.resolve()
            for line in reversed(lines):
                entry = json.loads(line)
                entry_path = Path(entry["original_path"]).resolve()
                if entry_path == file_path_resolved:
                    target_log = entry
                    break
        elif not target_log:
            # Get last backup
            target_log = json.loads(lines[-1])
        
        if not target_log:
            return {
                "success": False,
                "error": f"Không tìm thấy backup cho file: {file_path}"
            }
        
        backup_path = Path(target_log["backup_path"])
        original_path = Path(target_log["original_path"])
        
        if not backup_path.exists():
            return {
                "success": False,
                "error": f"Backup file không tồn tại: {backup_path}"
            }
        
        # Restore file
        original_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup_path, original_path)
        
        # Remove this entry from log to prevent re-rollback
        remaining_lines = [line for line in lines if json.loads(line) != target_log]
        with open(ROLLBACK_LOG, "w", encoding="utf-8") as f:
            f.writelines(remaining_lines)
        
        logger.info(
            f"[rollback] Restored {original_path.name} from backup "
            f"{backup_path.name} (timestamp={target_log['timestamp']})"
        )
        
        return {
            "success": True,
            "restored_file": str(original_path),
            "backup_used": str(backup_path),
            "timestamp": target_log["timestamp"],
        }
        
    except Exception as e:
        logger.error(f"[rollback] Failed to rollback: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_change_history(file_path: str, limit: int = 10) -> dict:
    """
    Lấy lịch sử thay đổi của một file.
    
    Args:
        file_path: Đường dẫn file
        limit: Số lượng changes tối đa trả về
        
    Returns:
        {
            "success": bool,
            "file": str,
            "changes": List[dict],
            "total": int,
            "error": Optional[str]
        }
    """
    try:
        _ensure_backup_dir()
        
        if not ROLLBACK_LOG.exists():
            return {
                "success": True,
                "file": file_path,
                "changes": [],
                "total": 0,
            }
        
        target_path = Path(file_path)
        if not target_path.is_absolute():
            target_path = (_PROJECT_ROOT / target_path).resolve()
        else:
            target_path = target_path.resolve()
        
        # Read and filter log
        changes = []
        with open(ROLLBACK_LOG, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                # Compare resolved paths to handle different path formats
                entry_path = Path(entry["original_path"]).resolve()
                if entry_path == target_path:
                    changes.append(entry)
        
        # Sort by timestamp (newest first)
        changes.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Limit results
        limited_changes = changes[:limit]
        
        logger.info(
            f"[history] Found {len(changes)} changes for {Path(file_path).name} "
            f"(returning {len(limited_changes)})"
        )
        
        return {
            "success": True,
            "file": file_path,
            "changes": limited_changes,
            "total": len(changes),
        }
        
    except Exception as e:
        logger.error(f"[history] Failed to get change history: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def list_all_backups(limit: int = 50) -> dict:
    """
    Liệt kê tất cả backups.
    
    Args:
        limit: Số lượng backups tối đa trả về
        
    Returns:
        {
            "success": bool,
            "backups": List[dict],
            "total": int,
            "error": Optional[str]
        }
    """
    try:
        _ensure_backup_dir()
        
        # Get all .bak files
        backup_files = list(BACKUP_DIR.glob("*.bak"))
        
        backups = []
        for backup_file in backup_files:
            stat = backup_file.stat()
            backups.append({
                "filename": backup_file.name,
                "path": str(backup_file),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            })
        
        # Sort by created time (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        limited = backups[:limit]
        
        return {
            "success": True,
            "backups": limited,
            "total": len(backups),
        }
        
    except Exception as e:
        logger.error(f"[list_backups] Failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def cleanup_old_backups(max_age_days: int = MAX_BACKUP_AGE_DAYS) -> dict:
    """
    Xóa các backups cũ hơn max_age_days.
    
    Args:
        max_age_days: Xóa backups cũ hơn N ngày
        
    Returns:
        {
            "success": bool,
            "deleted_count": int,
            "freed_bytes": int,
            "error": Optional[str]
        }
    """
    try:
        _ensure_backup_dir()
        
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=max_age_days)
        
        deleted_count = 0
        freed_bytes = 0
        
        for backup_file in BACKUP_DIR.glob("*.bak"):
            stat = backup_file.stat()
            created = datetime.fromtimestamp(stat.st_ctime)
            
            if created < cutoff:
                freed_bytes += stat.st_size
                backup_file.unlink()
                deleted_count += 1
        
        logger.info(
            f"[cleanup] Deleted {deleted_count} old backups "
            f"({freed_bytes / 1024 / 1024:.1f}MB freed)"
        )
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "freed_bytes": freed_bytes,
        }
        
    except Exception as e:
        logger.error(f"[cleanup] Failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def cleanup_excess_versions(max_versions: int = MAX_VERSIONS_PER_FILE) -> dict:
    """
    Giữ tối đa N versions cho mỗi file, xóa các versions cũ hơn.
    
    Args:
        max_versions: Số versions tối đa giữ lại cho mỗi file
        
    Returns:
        {
            "success": bool,
            "deleted_count": int,
            "freed_bytes": int,
            "error": Optional[str]
        }
    """
    try:
        _ensure_backup_dir()
        
        if not ROLLBACK_LOG.exists():
            return {
                "success": True,
                "deleted_count": 0,
                "freed_bytes": 0,
            }
        
        # Group backups by original file
        file_backups = {}
        with open(ROLLBACK_LOG, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                original = entry["original_path"]
                if original not in file_backups:
                    file_backups[original] = []
                file_backups[original].append(entry)
        
        deleted_count = 0
        freed_bytes = 0
        
        # For each file, keep only max_versions newest backups
        for original, backups in file_backups.items():
            if len(backups) <= max_versions:
                continue
            
            # Sort by timestamp (oldest first)
            backups.sort(key=lambda x: x["timestamp"])
            
            # Delete oldest backups
            to_delete = backups[:-max_versions]
            for entry in to_delete:
                backup_path = Path(entry["backup_path"])
                if backup_path.exists():
                    freed_bytes += backup_path.stat().st_size
                    backup_path.unlink()
                    deleted_count += 1
        
        logger.info(
            f"[cleanup_versions] Deleted {deleted_count} excess versions "
            f"({freed_bytes / 1024 / 1024:.1f}MB freed)"
        )
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "freed_bytes": freed_bytes,
        }
        
    except Exception as e:
        logger.error(f"[cleanup_versions] Failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

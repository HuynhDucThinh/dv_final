"""
File Manager Service — Core logic cho 6 file management operations.

Security Features:
- Path traversal protection
- Allowed directories whitelist
- Forbidden patterns blacklist
- File size limits
- Encoding detection

Operations:
1. read_file_content   — Đọc nội dung file text
2. list_files          — Liệt kê files trong thư mục
3. create_file         — Tạo file mới
4. modify_file         — Sửa file (append/replace/insert/delete_line)
5. delete_file         — Xóa file
6. move_rename_file    — Di chuyển/đổi tên file
"""
import os
import shutil
from pathlib import Path
from typing import Literal, Optional
import logging

logger = logging.getLogger(__name__)

# ─── SECURITY CONFIGURATION ──────────────────────────────────────────────────

# Thư mục được phép truy cập
_PROJECT_ROOT = Path(__file__).resolve().parents[4]  # d:/TU HOC/DV_Final

ALLOWED_DIRECTORIES = [
    _PROJECT_ROOT / "data",
    _PROJECT_ROOT / "report",
    _PROJECT_ROOT / "ML",
    _PROJECT_ROOT / "docs",
    _PROJECT_ROOT / "notebook",
]

# Patterns cấm tuyệt đối
FORBIDDEN_PATTERNS = [
    "*.env",           # API keys
    ".env.*",          # Environment files
    "*.git/*",         # Git internals
    "*password*",      # Password files
    "*secret*",        # Secret files
    "*.key",           # Private keys
    "*.pem",           # Certificates
    "*.exe",           # Executables
    "*.dll",           # Libraries
    "*.so",            # Shared objects
    "*.pyc",           # Python bytecode
    "__pycache__/*",   # Cache
]

# Giới hạn kích thước
MAX_FILE_READ_SIZE = 10 * 1024 * 1024     # 10MB
MAX_FILE_CREATE_SIZE = 50 * 1024 * 1024   # 50MB
MAX_MODIFY_LINES = 1000                    # Max lines per modify


# ─── SECURITY VALIDATORS ─────────────────────────────────────────────────────

class FileSecurityError(Exception):
    """Raised when file operation violates security policy."""
    pass


def validate_path(file_path: str) -> Path:
    """
    Validate path security.
    
    Raises:
        FileSecurityError: If path is invalid or forbidden
    """
    try:
        path_obj = Path(file_path)
        if not path_obj.is_absolute():
            path_obj = _PROJECT_ROOT / path_obj
        resolved = path_obj.resolve()
    except Exception as e:
        raise FileSecurityError(f"Invalid path: {e}")
    
    # Check allowed directories
    is_allowed = any(
        resolved == allowed_dir or resolved.is_relative_to(allowed_dir)
        for allowed_dir in ALLOWED_DIRECTORIES
    )
    
    if not is_allowed:
        allowed_str = ", ".join(str(d) for d in ALLOWED_DIRECTORIES)
        raise FileSecurityError(
            f"Path '{file_path}' is outside allowed directories. "
            f"Allowed: {allowed_str}"
        )
    
    # Check forbidden patterns
    path_str = str(resolved)
    for pattern in FORBIDDEN_PATTERNS:
        import fnmatch
        if fnmatch.fnmatch(path_str.lower(), pattern.lower()):
            raise FileSecurityError(
                f"Path matches forbidden pattern '{pattern}'"
            )
    
    return resolved


def validate_file_size(file_path: Path, max_size: int) -> None:
    """
    Validate file size.
    
    Raises:
        FileSecurityError: If file is too large
    """
    if file_path.exists():
        size = file_path.stat().st_size
        if size > max_size:
            raise FileSecurityError(
                f"File size ({size / 1024 / 1024:.1f}MB) exceeds limit "
                f"({max_size / 1024 / 1024:.1f}MB)"
            )


def detect_encoding(file_path: Path) -> str:
    """Detect file encoding (UTF-8, UTF-8-SIG, or CP1252)."""
    try:
        with open(file_path, "rb") as f:
            raw = f.read(4096)
        
        # Check BOM
        if raw.startswith(b'\xef\xbb\xbf'):
            return "utf-8-sig"
        
        # Try UTF-8
        try:
            raw.decode("utf-8")
            return "utf-8"
        except UnicodeDecodeError:
            pass
        
        # Fallback to Windows-1252
        return "cp1252"
    except Exception:
        return "utf-8"


# ─── FILE OPERATIONS ─────────────────────────────────────────────────────────

def read_file_content(file_path: str) -> dict:
    """
    Đọc nội dung file text.
    
    Args:
        file_path: Đường dẫn tuyệt đối hoặc tương đối từ project root
        
    Returns:
        {
            "success": bool,
            "content": str,
            "size_bytes": int,
            "encoding": str,
            "lines": int,
            "error": Optional[str]
        }
    """
    try:
        path = validate_path(file_path)
        
        if not path.exists():
            return {
                "success": False,
                "error": f"File không tồn tại: {file_path}"
            }
        
        if not path.is_file():
            return {
                "success": False,
                "error": f"Đường dẫn không phải là file: {file_path}"
            }
        
        validate_file_size(path, MAX_FILE_READ_SIZE)
        
        encoding = detect_encoding(path)
        
        with open(path, "r", encoding=encoding) as f:
            content = f.read()
        
        lines = content.count("\n") + 1
        
        logger.info(f"[read_file] OK: {file_path} ({len(content)} bytes, {lines} lines)")
        
        return {
            "success": True,
            "content": content,
            "size_bytes": len(content.encode(encoding)),
            "encoding": encoding,
            "lines": lines,
        }
        
    except FileSecurityError as e:
        logger.warning(f"[read_file] SECURITY: {e}")
        return {"success": False, "error": f"🔒 Security: {e}"}
    except Exception as e:
        logger.error(f"[read_file] ERROR: {e}")
        return {"success": False, "error": str(e)}


def list_files(directory: str, pattern: str = "*", recursive: bool = False) -> dict:
    """
    Liệt kê files trong thư mục.
    
    Args:
        directory: Đường dẫn thư mục
        pattern: Glob pattern (ví dụ: "*.csv", "report_*")
        recursive: Có tìm kiếm đệ quy không
        
    Returns:
        {
            "success": bool,
            "files": List[{"name": str, "path": str, "size": int, "type": str}],
            "count": int,
            "error": Optional[str]
        }
    """
    try:
        path = validate_path(directory)
        
        if not path.exists():
            return {
                "success": False,
                "error": f"Thư mục không tồn tại: {directory}"
            }
        
        if not path.is_dir():
            return {
                "success": False,
                "error": f"Đường dẫn không phải là thư mục: {directory}"
            }
        
        # Collect files
        glob_method = path.rglob if recursive else path.glob
        matched = list(glob_method(pattern))
        
        files = []
        for item in matched:
            if item.is_file():
                try:
                    size = item.stat().st_size
                    files.append({
                        "name": item.name,
                        "path": str(item),
                        "size": size,
                        "type": item.suffix or "no extension"
                    })
                except Exception:
                    pass
        
        # Sort by name
        files.sort(key=lambda x: x["name"])
        
        logger.info(f"[list_files] OK: {directory} pattern={pattern} found={len(files)}")
        
        return {
            "success": True,
            "files": files,
            "count": len(files),
        }
        
    except FileSecurityError as e:
        logger.warning(f"[list_files] SECURITY: {e}")
        return {"success": False, "error": f"🔒 Security: {e}"}
    except Exception as e:
        logger.error(f"[list_files] ERROR: {e}")
        return {"success": False, "error": str(e)}


def create_file(file_path: str, content: str, overwrite: bool = False) -> dict:
    """
    Tạo file mới.
    
    Args:
        file_path: Đường dẫn file cần tạo
        content: Nội dung file
        overwrite: Có ghi đè nếu file đã tồn tại không
        
    Returns:
        {
            "success": bool,
            "path": str,
            "size_bytes": int,
            "existed_before": bool,
            "error": Optional[str]
        }
    """
    try:
        path = validate_path(file_path)
        
        existed_before = path.exists()
        
        if existed_before and not overwrite:
            return {
                "success": False,
                "error": f"File đã tồn tại: {file_path}. Set overwrite=True để ghi đè."
            }
        
        # Validate content size
        content_bytes = content.encode("utf-8")
        if len(content_bytes) > MAX_FILE_CREATE_SIZE:
            return {
                "success": False,
                "error": f"Nội dung quá lớn ({len(content_bytes) / 1024 / 1024:.1f}MB). "
                         f"Giới hạn: {MAX_FILE_CREATE_SIZE / 1024 / 1024:.1f}MB"
            }
        
        # Create parent directory if not exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"[create_file] OK: {file_path} ({len(content_bytes)} bytes, overwrite={overwrite})")
        
        return {
            "success": True,
            "path": str(path),
            "size_bytes": len(content_bytes),
            "existed_before": existed_before,
        }
        
    except FileSecurityError as e:
        logger.warning(f"[create_file] SECURITY: {e}")
        return {"success": False, "error": f"🔒 Security: {e}"}
    except Exception as e:
        logger.error(f"[create_file] ERROR: {e}")
        return {"success": False, "error": str(e)}


def modify_file(
    file_path: str,
    operation: Literal["append", "replace", "insert", "delete_line"],
    content: str = "",
    line_number: Optional[int] = None,
    search_text: Optional[str] = None,
) -> dict:
    """
    Sửa file hiện có.
    
    Operations:
        - append: Thêm nội dung vào cuối file
        - replace: Thay thế search_text bằng content
        - insert: Chèn content vào dòng line_number
        - delete_line: Xóa dòng line_number
    
    Args:
        file_path: Đường dẫn file
        operation: Loại thao tác
        content: Nội dung mới (cho append/replace/insert)
        line_number: Số dòng (cho insert/delete_line, bắt đầu từ 1)
        search_text: Text cần tìm (cho replace)
        
    Returns:
        {
            "success": bool,
            "operation": str,
            "lines_affected": int,
            "new_size_bytes": int,
            "error": Optional[str]
        }
    """
    try:
        path = validate_path(file_path)
        
        if not path.exists():
            return {
                "success": False,
                "error": f"File không tồn tại: {file_path}"
            }
        
        validate_file_size(path, MAX_FILE_READ_SIZE)
        
        encoding = detect_encoding(path)
        
        with open(path, "r", encoding=encoding) as f:
            lines = f.readlines()
        
        if len(lines) > MAX_MODIFY_LINES:
            return {
                "success": False,
                "error": f"File quá lớn ({len(lines)} dòng). Giới hạn: {MAX_MODIFY_LINES} dòng."
            }
        
        lines_affected = 0
        
        # Auto-backup trước khi sửa file để ghi nhận lịch sử và hỗ trợ Rollback
        try:
            from app.services.backup_service import create_backup
            create_backup(str(path), operation=f"modify_{operation}")
        except Exception as _be:
            logger.warning(f"[modify_file] Backup warning: {_be}")

        # Execute operation
        if operation == "append":
            if lines and not lines[-1].endswith("\n"):
                lines[-1] += "\n"
            lines.append(content if content.endswith("\n") else content + "\n")
            lines_affected = 1
            
        elif operation in ("replace", "replace_line", "update"):
            if line_number is not None:
                if 1 <= line_number <= len(lines):
                    lines[line_number - 1] = content if content.endswith("\n") else content + "\n"
                    lines_affected = 1
                else:
                    return {
                        "success": False,
                        "error": f"line_number {line_number} out of range (1-{len(lines)})"
                    }
            elif search_text:
                import unicodedata
                clean_search = search_text.strip()
                nfc_search = unicodedata.normalize('NFC', clean_search)
                nfd_search = unicodedata.normalize('NFD', clean_search)
                
                new_lines = []
                for line in lines:
                    nfc_line = unicodedata.normalize('NFC', line)
                    nfd_line = unicodedata.normalize('NFD', line)
                    
                    if clean_search in line or nfc_search in nfc_line or nfd_search in nfd_line:
                        has_newline = line.endswith("\n") or line.endswith("\r")
                        if clean_search in line:
                            replaced = line.replace(clean_search, content.strip())
                        elif nfc_search in nfc_line:
                            replaced = nfc_line.replace(nfc_search, content.strip())
                        else:
                            replaced = nfd_line.replace(nfd_search, content.strip())
                        
                        if has_newline and not replaced.endswith("\n"):
                            replaced += "\n"
                        new_lines.append(replaced)
                        lines_affected += 1
                    else:
                        new_lines.append(line)
                
                if lines_affected == 0:
                    return {
                        "success": False,
                        "error": f"Không tìm thấy đoạn text '{clean_search}' trong file để thay thế. Vui lòng kiểm tra lại chính tả hoặc chọn thay thế theo số dòng (line_number)."
                    }
                lines = new_lines
            else:
                return {
                    "success": False,
                    "error": "Missing search_text or line_number for replace operation"
                }
            
        elif operation == "insert":
            if line_number is None:
                return {
                    "success": False,
                    "error": "Missing line_number for insert operation"
                }
            
            if line_number < 1 or line_number > len(lines) + 1:
                return {
                    "success": False,
                    "error": f"line_number {line_number} out of range (1-{len(lines) + 1})"
                }
            
            lines.insert(line_number - 1, content if content.endswith("\n") else content + "\n")
            lines_affected = 1
            
        elif operation == "delete_line":
            if line_number is None:
                return {
                    "success": False,
                    "error": "Missing line_number for delete_line operation"
                }
            
            if line_number < 1 or line_number > len(lines):
                return {
                    "success": False,
                    "error": f"line_number {line_number} out of range (1-{len(lines)})"
                }
            
            del lines[line_number - 1]
            lines_affected = 1
        
        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}"
            }
        
        # Write back (always use UTF-8 for consistency)
        new_content = "".join(lines)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        new_size = len(new_content.encode("utf-8"))
        
        logger.info(f"[modify_file] OK: {file_path} operation={operation} lines_affected={lines_affected}")
        
        return {
            "success": True,
            "operation": operation,
            "lines_affected": lines_affected,
            "new_size_bytes": new_size,
        }
        
    except FileSecurityError as e:
        logger.warning(f"[modify_file] SECURITY: {e}")
        return {"success": False, "error": f"🔒 Security: {e}"}
    except Exception as e:
        logger.error(f"[modify_file] ERROR: {e}")
        return {"success": False, "error": str(e)}


def delete_file(file_path: str, force: bool = False) -> dict:
    """
    Xóa file.
    
    Args:
        file_path: Đường dẫn file cần xóa
        force: Bỏ qua cảnh báo (dùng khi user đã xác nhận 2 lần)
        
    Returns:
        {
            "success": bool,
            "path": str,
            "size_deleted": int,
            "error": Optional[str]
        }
    """
    try:
        path = validate_path(file_path)
        
        if not path.exists():
            return {
                "success": False,
                "error": f"File không tồn tại: {file_path}"
            }
        
        if not path.is_file():
            return {
                "success": False,
                "error": f"Đường dẫn không phải là file: {file_path}"
            }
        
        size_deleted = path.stat().st_size
        
        # Auto-backup trước khi xóa file
        try:
            from app.services.backup_service import create_backup
            create_backup(str(path), operation="delete")
        except Exception as _be:
            logger.warning(f"[delete_file] Backup warning: {_be}")

        # Delete file
        path.unlink()
        
        logger.info(f"[delete_file] OK: {file_path} ({size_deleted} bytes deleted)")
        
        return {
            "success": True,
            "path": str(path),
            "size_deleted": size_deleted,
        }
        
    except FileSecurityError as e:
        logger.warning(f"[delete_file] SECURITY: {e}")
        return {"success": False, "error": f"🔒 Security: {e}"}
    except Exception as e:
        logger.error(f"[delete_file] ERROR: {e}")
        return {"success": False, "error": str(e)}


def move_rename_file(source: str, destination: str, overwrite: bool = False) -> dict:
    """
    Di chuyển hoặc đổi tên file.
    
    Args:
        source: Đường dẫn file nguồn
        destination: Đường dẫn file đích
        overwrite: Có ghi đè nếu file đích đã tồn tại không
        
    Returns:
        {
            "success": bool,
            "source": str,
            "destination": str,
            "size_bytes": int,
            "error": Optional[str]
        }
    """
    try:
        src_path = validate_path(source)
        dst_path = validate_path(destination)
        
        if not src_path.exists():
            return {
                "success": False,
                "error": f"File nguồn không tồn tại: {source}"
            }
        
        if not src_path.is_file():
            return {
                "success": False,
                "error": f"Nguồn không phải là file: {source}"
            }
        
        if dst_path.exists() and not overwrite:
            return {
                "success": False,
                "error": f"File đích đã tồn tại: {destination}. Set overwrite=True để ghi đè."
            }
        
        size_bytes = src_path.stat().st_size
        
        # Create destination directory if not exists
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Move/rename
        shutil.move(str(src_path), str(dst_path))
        
        logger.info(f"[move_rename_file] OK: {source} → {destination}")
        
        return {
            "success": True,
            "source": str(src_path),
            "destination": str(dst_path),
            "size_bytes": size_bytes,
        }
        
    except FileSecurityError as e:
        logger.warning(f"[move_rename_file] SECURITY: {e}")
        return {"success": False, "error": f"🔒 Security: {e}"}
    except Exception as e:
        logger.error(f"[move_rename_file] ERROR: {e}")
        return {"success": False, "error": str(e)}

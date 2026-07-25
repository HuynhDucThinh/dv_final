from __future__ import annotations
import json, logging, threading, time, zipfile
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

_PBIX_LAYOUT_SNAPSHOT = None
_PBIX_CHANGE_LOG = []
_PBIX_LAST_MTIME = 0.0
_MAX_LOG_ENTRIES = 20
_lock = threading.Lock()


def start(pbix_path):
    """
    Khoi dong Watchdog theo doi file .pbix.
    Goi 1 lan khi server khoi dong (tu _warmup_caches).
    Neu file khong ton tai -> ghi log warning va return im lang.
    """
    pbix_path = Path(pbix_path)
    if not pbix_path.exists():
        logger.warning("[PBIXWatcher] File .pbix khong ton tai: %s", pbix_path)
        print(f"[PBIXWatcher] Khong tim thay {pbix_path} -- bo qua watcher.")
        return
    _load_and_snapshot(pbix_path)
    t = threading.Thread(target=_run_watcher, args=(pbix_path,), daemon=True, name="pbix-watcher")
    t.start()
    print(f"[PBIXWatcher] OK Dang theo doi: {pbix_path}")
    logger.warning("[PBIXWatcher] Watchdog started for: %s", pbix_path)


def get_change_log():
    """Tra ve danh sach thay doi gan nhat. Thread-safe."""
    with _lock:
        return list(_PBIX_CHANGE_LOG)


def get_summary_for_context():
    """
    Tra ve chuoi markdown ve cac thay doi Power BI gan nhat.
    Tra ve chuoi rong neu chua co thay doi nao.
    """
    with _lock:
        if not _PBIX_CHANGE_LOG:
            return ""
        lines = ["### Power BI -- Thay Doi Gan Nhat:"]
        for entry in _PBIX_CHANGE_LOG[-5:]:
            lines.append("- " + entry["time"] + " | Trang: " + entry["page"])
            for chg in entry["changes"]:
                lines.append("  - " + chg)
        return "\n".join(lines)


def _run_watcher(pbix_path):
    """Chay Watchdog observer trong thread daemon."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class _PBIXHandler(FileSystemEventHandler):
            def on_modified(self, event):
                if not event.is_directory and Path(event.src_path).resolve() == pbix_path.resolve():
                    time.sleep(1.5)
                    _load_and_snapshot(pbix_path)

            def on_created(self, event):
                if not event.is_directory and Path(event.src_path).resolve() == pbix_path.resolve():
                    time.sleep(1.5)
                    _load_and_snapshot(pbix_path)

        observer = Observer()
        observer.schedule(_PBIXHandler(), path=str(pbix_path.parent), recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(5)
        finally:
            observer.stop()
            observer.join()
    except Exception as e:
        logger.warning("[PBIXWatcher] Loi watchdog: %s", e)
        print(f"[PBIXWatcher] Loi watchdog: {e} -- fallback sang mtime polling.")
        _run_mtime_fallback(pbix_path)


def _run_mtime_fallback(pbix_path):
    """Fallback: poll mtime moi 10s neu watchdog that bai."""
    global _PBIX_LAST_MTIME
    print("[PBIXWatcher] Chuyen sang mtime polling (moi 10s).")
    while True:
        try:
            if pbix_path.exists():
                mtime = pbix_path.stat().st_mtime
                if mtime != _PBIX_LAST_MTIME:
                    _load_and_snapshot(pbix_path)
        except Exception:
            pass
        time.sleep(10)


def _load_and_snapshot(pbix_path):
    """Doc Layout JSON tu .pbix, so sanh voi snapshot cu, ghi diff."""
    global _PBIX_LAYOUT_SNAPSHOT, _PBIX_LAST_MTIME
    try:
        if not pbix_path.exists():
            return
        current_mtime = pbix_path.stat().st_mtime
        new_layout = _parse_layout(pbix_path)
        if new_layout is None:
            return
        with _lock:
            old_layout = _PBIX_LAYOUT_SNAPSHOT
            _PBIX_LAST_MTIME = current_mtime
            if old_layout is None:
                _PBIX_LAYOUT_SNAPSHOT = new_layout
                pages = _extract_pages(new_layout)
                names = [p.get("displayName", p.get("name", "?")) for p in pages]
                print("[PBIXWatcher] Snapshot ban dau: " + str(len(pages)) + " trang -- " + str(names))
                return
            diffs = _diff_layout(old_layout, new_layout)
            _PBIX_LAYOUT_SNAPSHOT = new_layout
            if diffs:
                for diff in diffs:
                    _PBIX_CHANGE_LOG.append(diff)
                    print("[PBIXWatcher] " + diff["time"] + " | " + diff["page"] + ": " + ", ".join(diff["changes"]))
                if len(_PBIX_CHANGE_LOG) > _MAX_LOG_ENTRIES:
                    del _PBIX_CHANGE_LOG[:-_MAX_LOG_ENTRIES]
            else:
                print("[PBIXWatcher] File thay doi nhung khong phat hien khac biet chart.")
    except Exception as e:
        logger.warning("[PBIXWatcher] Loi doc/parse .pbix: %s", e)


def _parse_layout(pbix_path):
    """Giai file .pbix (ZIP) va doc Report/Layout JSON."""
    try:
        with zipfile.ZipFile(pbix_path, "r") as z:
            names = z.namelist()
            layout_name = next(
                (n for n in names if n in ("Report/Layout", "Report\\Layout") or n.endswith("Layout")),
                None
            )
            if layout_name is None:
                logger.warning("[PBIXWatcher] Khong tim thay Report/Layout trong .pbix")
                return None
            raw = z.read(layout_name)
            try:
                text = raw.decode("utf-16-le")
            except UnicodeDecodeError:
                text = raw.decode("utf-8", errors="replace")
            return json.loads(text)
    except zipfile.BadZipFile:
        logger.warning("[PBIXWatcher] File .pbix dang bi ghi (locked) -- bo qua.")
        return None
    except Exception as e:
        logger.warning("[PBIXWatcher] Loi parse layout: %s", e)
        return None


def _extract_pages(layout):
    return layout.get("sections", [])


def _diff_layout(old_layout, new_layout):
    """So sanh 2 Layout JSON, tra ve list diff entry."""
    diffs = []
    ts = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    old_pages = {p.get("name", ""): p for p in _extract_pages(old_layout)}
    new_pages = {p.get("name", ""): p for p in _extract_pages(new_layout)}

    for name in set(new_pages) - set(old_pages):
        display = new_pages[name].get("displayName", name)
        diffs.append({"time": ts, "page": display, "changes": ["[THEM] Trang moi duoc tao"]})

    for name in set(old_pages) - set(new_pages):
        display = old_pages[name].get("displayName", name)
        diffs.append({"time": ts, "page": display, "changes": ["[XOA] Trang bi xoa"]})

    for name in set(old_pages) & set(new_pages):
        op, np2 = old_pages[name], new_pages[name]
        display = np2.get("displayName", name)
        pc = []
        if op.get("displayName") != np2.get("displayName"):
            pc.append("[DOI TEN] '" + str(op.get("displayName")) + "' -> '" + str(np2.get("displayName")) + "'")
        ov = {v.get("name", ""): v for v in op.get("visualContainers", [])}
        nv = {v.get("name", ""): v for v in np2.get("visualContainers", [])}
        for vn in set(nv) - set(ov):
            vt = _get_visual_type(nv[vn])
            vtit = _get_visual_title(nv[vn])
            pc.append("[THEM] Visual moi - loai: " + vt + (" - tieu de: '" + vtit + "'" if vtit else ""))
        for vn in set(ov) - set(nv):
            vtit = _get_visual_title(ov[vn])
            pc.append("[XOA] Visual bi xoa" + (" - '" + vtit + "'" if vtit else ""))
        for vn in set(ov) & set(nv):
            pc.extend(_diff_visual(ov[vn], nv[vn]))
        if pc:
            diffs.append({"time": ts, "page": display, "changes": pc})
    return diffs


def _diff_visual(old_v, new_v):
    """So sanh 2 visual cung ten, tra ve list thay doi."""
    ch = []
    title = _get_visual_title(new_v) or _get_visual_title(old_v) or "visual"
    ot = _get_visual_type(old_v)
    nt = _get_visual_type(new_v)
    if ot != nt:
        ch.append("[SUA] '" + title + "' - kieu chart: " + ot + " -> " + nt)
    otit = _get_visual_title(old_v)
    ntit = _get_visual_title(new_v)
    if otit != ntit and (otit or ntit):
        ch.append("[SUA] Tieu de: '" + otit + "' -> '" + ntit + "'")
    for attr in ("x", "y", "width", "height"):
        if old_v.get(attr) != new_v.get(attr):
            ch.append("[SUA] '" + title + "' - vi tri/kich thuoc thay doi")
            break
    return ch


def _get_visual_type(visual):
    try:
        cfg = visual.get("config", "{}")
        c = json.loads(cfg) if isinstance(cfg, str) else cfg
        return c.get("singleVisual", {}).get("visualType", "unknown")
    except Exception:
        return "unknown"


def _get_visual_title(visual):
    try:
        cfg = visual.get("config", "{}")
        c = json.loads(cfg) if isinstance(cfg, str) else cfg
        tp = c.get("singleVisual", {}).get("vcObjects", {}).get("title", [{}])
        if tp:
            tv = tp[0].get("properties", {}).get("text", {})
            if "expr" in tv:
                return tv["expr"].get("Literal", {}).get("Value", "").strip("'\"")
        return ""
    except Exception:
        return ""

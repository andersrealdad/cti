"""
File-based IN/OUT store helpers for news, briefs, and debates.
All content lives in local folders (JSONL/Markdown). No external DB.
"""
from pathlib import Path
from typing import List, Dict
import shutil
import time

# Base folders
NEWS_IN = Path("data/news_in")
NEWS_OUT = Path("data/news_out")
BRIEFS_IN = Path("data/briefs_in")
BRIEFS_OUT = Path("data/briefs_out")
DEBATES_IN = Path("data/debates_in")
DEBATES_OUT = Path("data/debates_out")

ALL_FOLDERS = [
    NEWS_IN,
    NEWS_OUT,
    BRIEFS_IN,
    BRIEFS_OUT,
    DEBATES_IN,
    DEBATES_OUT,
]


def ensure_dirs():
    """Ensure base folders exist."""
    for folder in ALL_FOLDERS:
        folder.mkdir(parents=True, exist_ok=True)


def list_md(folder: Path) -> List[Dict]:
    """List markdown files with basic metadata."""
    if not folder.exists():
        return []
    items = []
    for path in sorted(folder.glob("*.md")):
        try:
            items.append(
                {
                    "name": path.name,
                    "path": path,
                    "mtime": path.stat().st_mtime,
                }
            )
        except Exception:
            continue
    return items


def read_md(path: Path) -> str:
    """Read markdown content; empty string if missing/error."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def write_md(folder: Path, filename: str, content: str) -> Path:
    """Write markdown content to folder/filename."""
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / filename
    target.write_text(content, encoding="utf-8")
    return target


def move_md(src: Path, dst_folder: Path) -> Path:
    """Move a markdown file into a destination folder (overwrite-safe)."""
    dst_folder.mkdir(parents=True, exist_ok=True)
    target = dst_folder / src.name
    shutil.move(str(src), str(target))
    return target


# Ensure folders exist on import
ensure_dirs()

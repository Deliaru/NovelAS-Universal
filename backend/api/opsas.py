"""
OpsasPlan REST API endpoints.

Manages operational plans under the project-root `OpsasPlan/` directory.
Plans are organized by category (song-release, cover-selection, etc.)
and named `YYYY-MM-DD_<slug>.md`.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["opsas"])

# Project root = parent of backend/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OPSAS_ROOT = PROJECT_ROOT / "OpsasPlan"

CATEGORIES = [
    "song-release",
    "cover-selection",
    "stream-planning",
    "weekly-schedule",
    "promo-pack",
    "campaign-design",
    "content-review",
]

CATEGORY_LABELS = {
    "song-release": "歌曲发布",
    "cover-selection": "翻唱选题",
    "stream-planning": "直播规划",
    "weekly-schedule": "周度排期",
    "promo-pack": "推广文案",
    "campaign-design": "活动策划",
    "content-review": "内容审查",
}

SAFE_NAME = re.compile(r"^[A-Za-z0-9_\-\.]+$")


def _ensure_category(category: str) -> Path:
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Unknown category: {category}")
    p = OPSAS_ROOT / category
    p.mkdir(parents=True, exist_ok=True)
    return p


def _ensure_safe_name(name: str) -> None:
    if not SAFE_NAME.match(name):
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not name.endswith(".md"):
        raise HTTPException(status_code=400, detail="Filename must end with .md")


class WritePlanRequest(BaseModel):
    content: str


class CreatePlanRequest(BaseModel):
    category: str
    title: str
    slug: str = ""
    tags: list[str] = []


@router.get("/opsas/categories")
async def list_categories():
    """List all plan categories with labels and counts."""
    result = []
    for cat in CATEGORIES:
        path = OPSAS_ROOT / cat
        count = 0
        if path.exists():
            count = sum(1 for p in path.iterdir() if p.is_file() and p.suffix == ".md")
        result.append({
            "category": cat,
            "label": CATEGORY_LABELS[cat],
            "count": count,
        })
    return result


@router.get("/opsas/plans")
async def list_plans(category: str | None = None):
    """List plan files, optionally filtered by category."""
    items = []
    categories = [category] if category else CATEGORIES
    for cat in categories:
        if cat not in CATEGORIES:
            continue
        path = OPSAS_ROOT / cat
        if not path.exists():
            continue
        for p in sorted(path.iterdir(), reverse=True):
            if not p.is_file() or p.suffix != ".md":
                continue
            stat = p.stat()
            items.append({
                "category": cat,
                "category_label": CATEGORY_LABELS[cat],
                "name": p.name,
                "path": f"{cat}/{p.name}",
                "size": stat.st_size,
                "mtime": stat.st_mtime,
            })
    items.sort(key=lambda x: x["name"], reverse=True)
    return items


@router.get("/opsas/plans/{category}/{name}")
async def read_plan(category: str, name: str):
    """Read a plan file."""
    _ensure_safe_name(name)
    base = _ensure_category(category)
    fp = base / name
    if not fp.exists():
        raise HTTPException(status_code=404, detail="Plan not found")
    return {
        "category": category,
        "name": name,
        "path": f"{category}/{name}",
        "content": fp.read_text(encoding="utf-8"),
    }


@router.put("/opsas/plans/{category}/{name}")
async def write_plan(category: str, name: str, request: WritePlanRequest):
    """Create or update a plan file."""
    _ensure_safe_name(name)
    base = _ensure_category(category)
    fp = base / name
    fp.write_text(request.content, encoding="utf-8")
    return {"status": "ok", "path": f"{category}/{name}"}


@router.delete("/opsas/plans/{category}/{name}")
async def delete_plan(category: str, name: str):
    """Delete a plan file."""
    _ensure_safe_name(name)
    base = _ensure_category(category)
    fp = base / name
    if not fp.exists():
        raise HTTPException(status_code=404, detail="Plan not found")
    fp.unlink()
    return {"status": "ok"}


@router.post("/opsas/plans")
async def create_plan(request: CreatePlanRequest):
    """Create a new empty plan with standard frontmatter."""
    if request.category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Unknown category: {request.category}")
    base = _ensure_category(request.category)
    today = date.today().isoformat()
    slug_part = re.sub(r"[^A-Za-z0-9\-]+", "-", request.title).strip("-").lower()[:40] or "plan"
    name = f"{today}_{slug_part}.md"
    fp = base / name
    n = 2
    while fp.exists():
        name = f"{today}_{slug_part}_{n}.md"
        fp = base / name
        n += 1
    tags_yaml = "[" + ", ".join(request.tags) + "]" if request.tags else "[]"
    content = (
        "---\n"
        f"category: {request.category}\n"
        f"title: {request.title}\n"
        f"slug: {request.slug}\n"
        f"created_at: {today}\n"
        f"plan_type: {request.category}\n"
        f"tags: {tags_yaml}\n"
        "---\n\n"
        f"# {request.title}\n\n"
    )
    fp.write_text(content, encoding="utf-8")
    return {"status": "ok", "category": request.category, "name": name, "path": f"{request.category}/{name}"}

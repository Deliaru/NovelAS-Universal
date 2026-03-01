"""
Pydantic models for the Propose-Commit patch system.
"""

from typing import Any

from pydantic import BaseModel, Field


class PendingPatch(BaseModel):
    """Internal model for a pending patch stored on disk."""

    patch_id: str
    lore_updates: list[dict[str, Any]]
    created_at: str

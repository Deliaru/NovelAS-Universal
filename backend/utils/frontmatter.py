"""
YAML frontmatter parser for Markdown files.
Handles reading and writing YAML frontmatter in lore/chapter files.
"""

from dataclasses import dataclass
from typing import Any

import yaml


@dataclass
class ParsedDocument:
    """A Markdown document with parsed frontmatter."""

    metadata: dict[str, Any]
    body: str


def parse_frontmatter(content: str) -> ParsedDocument:
    """
    Parse YAML frontmatter from a Markdown document.

    Expects format:
        ---
        key: value
        ---
        Body content here...
    """
    if not content.startswith("---"):
        return ParsedDocument(metadata={}, body=content)

    parts = content.split("---", 2)
    if len(parts) < 3:
        return ParsedDocument(metadata={}, body=content)

    try:
        metadata = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        metadata = {}

    body = parts[2].lstrip("\n")
    return ParsedDocument(metadata=metadata, body=body)


def build_frontmatter(metadata: dict[str, Any], body: str) -> str:
    """
    Build a Markdown document with YAML frontmatter.
    """
    if not metadata:
        return body

    yaml_str = yaml.dump(
        metadata,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    ).rstrip("\n")

    return f"---\n{yaml_str}\n---\n\n{body}"


# Standard frontmatter template for lore entries
LORE_FRONTMATTER_TEMPLATE = {
    "name": "",
    "category": "",
    "aliases": [],
    "first_appearance": "",
    "last_updated": "",
    "status": "active",
    "tags": [],
}

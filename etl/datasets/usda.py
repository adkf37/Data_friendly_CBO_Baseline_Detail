"""USDA Farm Programs hierarchy adapter."""

from __future__ import annotations


HIERARCHY_COLUMNS = ["table_title", "section", "subsection"]


def split_hierarchy(category_path: str, category: str) -> dict[str, str]:
    """Split a USDA breadcrumb into explicit hierarchy fields.

    ``category`` remains the leaf label and ``category_path`` remains the
    lossless representation. Additional intermediate nodes are retained in
    ``subsection`` using the same delimiter.
    """

    parts = [part.strip() for part in category_path.split(" / ") if part.strip()]
    if parts and parts[-1].casefold() == category.strip().casefold():
        ancestors = parts[:-1]
    else:
        ancestors = parts
    return {
        "table_title": ancestors[0] if ancestors else "",
        "section": ancestors[1] if len(ancestors) > 1 else "",
        "subsection": " / ".join(ancestors[2:]) if len(ancestors) > 2 else "",
    }


"""
execution/context_signals.py

Single source of truth for determining whether execution context is
actually available.

IMPORTANT INVARIANT
-------------------
Bucket presence DOES NOT imply usable context.

Example:
    open_website("github.com")

writes:

    context._buckets["web"] = ["Opened github.com"]

That is NOT retrieval.

Only a successful execution of the appropriate producer tool should
count as available context.

These helpers intentionally inspect execution history rather than
bucket presence for context types where this distinction matters.
"""

from typing import Any


def is_document_loaded(context: Any) -> bool:
    """
    Returns True only if a document has genuinely been loaded.
    """

    if context is None:
        return False

    buckets = getattr(context, "_buckets", None)

    if buckets and buckets.get("document"):
        return True

    history = getattr(context, "history", []) or []

    for entry in history:
        if isinstance(entry, dict):
            tool = entry.get("tool", "")
            result = str(entry.get("result", "")).strip()
        else:
            tool = getattr(entry, "tool", "")
            result = str(getattr(entry, "result", "")).strip()

        if tool != "load_document":
            continue

        if result.startswith("⚠️") or result.startswith("❌"):
            continue

        return True

    return False


def has_retrieved_content(context: Any) -> bool:
    """
    Returns True only after an actual web retrieval.

    open_website() should NEVER satisfy this condition.
    """

    if context is None:
        return False

    history = getattr(context, "history", []) or []

    for entry in history:
        if isinstance(entry, dict):
            tool = entry.get("tool", "")
            result = str(entry.get("result", "")).strip()
        else:
            tool = getattr(entry, "tool", "")
            result = str(getattr(entry, "result", "")).strip()

        if tool != "web_retriever":
            continue

        if result.startswith("⚠️") or result.startswith("❌"):
            continue

        if result:
            return True

    return False

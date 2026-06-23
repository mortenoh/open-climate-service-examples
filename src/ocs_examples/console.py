"""Tiny console-formatting helpers so the examples print consistent, readable output.

Deliberately dependency-free (plain ``print``) — the examples are meant to be copied
and run, and should not require a rich-text library to read.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel


def section(title: str) -> None:
    """Print a labelled section header."""
    line = "=" * len(title)
    print(f"\n{title}\n{line}")


def info(message: str) -> None:
    """Print an informational line."""
    print(message)


def warn(message: str) -> None:
    """Print a warning line, prefixed so it stands out in plain output."""
    print(f"!! {message}")


def dump(obj: Any, *, limit: int | None = None) -> None:
    """Pretty-print a JSON-serialisable object (or pydantic model) as indented JSON.

    Args:
        obj: A pydantic model, dict, list, or any JSON-serialisable value.
        limit: If set and ``obj`` is a list, only the first ``limit`` items are shown.
    """
    if isinstance(obj, BaseModel):
        obj = obj.model_dump(mode="json")
    if limit is not None and isinstance(obj, list):
        shown = obj[:limit]
        print(json.dumps(shown, indent=2, default=str))
        if len(obj) > limit:
            print(f"... ({len(obj) - limit} more)")
        return
    print(json.dumps(obj, indent=2, default=str))

"""Shared selected-agreement state for notebook widget workflows."""

from __future__ import annotations

from typing import Any

_SELECTED_AGREEMENT: dict[str, Any] | None = None


def set_selected_agreement(row: dict[str, Any]) -> None:
    """Store the selected agreement row for downstream notebook helpers."""
    global _SELECTED_AGREEMENT
    _SELECTED_AGREEMENT = dict(row)


def get_selected_agreement_state() -> dict[str, Any] | None:
    """Return the selected agreement row, if one has been stored."""
    return dict(_SELECTED_AGREEMENT) if _SELECTED_AGREEMENT else None

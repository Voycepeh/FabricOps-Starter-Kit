"""Shared data-agreement helpers used outside the legacy owner module."""

from __future__ import annotations

from typing import Any

from fabricops_kit import data_agreement as _legacy

AGREEMENT_EVIDENCE_TYPES = _legacy.AGREEMENT_EVIDENCE_TYPES
FIELD_LABELS = _legacy.FIELD_LABELS
_WIDGET_CONFIG_DEFAULTS = _legacy._WIDGET_CONFIG_DEFAULTS


def __getattr__(name: str) -> Any:
    """Return shared data-agreement attributes from the current legacy implementation."""
    return getattr(_legacy, name)

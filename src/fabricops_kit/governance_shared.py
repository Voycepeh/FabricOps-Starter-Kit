"""Shared governance helpers used outside the legacy governance module."""

from __future__ import annotations

from typing import Any

from fabricops_kit import governance_review as _legacy

CATALOGUE_TABLE = _legacy.CATALOGUE_TABLE
DQ_RULE_TYPES = _legacy.DQ_RULE_TYPES
ENRICHMENT_RULES_TABLE = _legacy.ENRICHMENT_RULES_TABLE
GUARDRAIL_RULES_TABLE = _legacy.GUARDRAIL_RULES_TABLE


def __getattr__(name: str) -> Any:
    """Return shared governance attributes from the current legacy implementation."""
    return getattr(_legacy, name)

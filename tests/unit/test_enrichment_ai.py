"""Regression tests for Data Contract AI enrichment helpers."""

from __future__ import annotations

import inspect

import pytest

from fabricops_kit.widgets.enrichment_shared import suggest_enrichment

pytestmark = pytest.mark.unit


def test_suggest_enrichment_is_description_only() -> None:
    """Description AI no longer requires or returns Classification advice."""
    prompts: list[str] = []

    result = suggest_enrichment(
        {"metadata_level": "column", "column_name": "CATEGORY"},
        description_prompt="Describe the selected column.",
        invoke=lambda prompt: prompts.append(prompt) or " Product category ",
    )

    assert result == {"Description": "Product category"}
    assert len(prompts) == 1
    assert "CATEGORY" in prompts[0]
    parameters = inspect.signature(suggest_enrichment).parameters
    assert "classification_prompt" not in parameters
    assert "classification_labels" not in parameters


def test_suggest_enrichment_requires_only_description_prompt() -> None:
    """A missing Description prompt fails clearly without Classification coupling."""
    with pytest.raises(ValueError, match="description prompt"):
        suggest_enrichment({}, description_prompt="", invoke=lambda _prompt: "unused")

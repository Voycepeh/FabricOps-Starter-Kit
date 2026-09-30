"""Tests for curated TEMPLATE_FLOW_DOCS validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import pytest

from scripts import generate_individual_function_reference_pages as generator


def _flow(template_path: str = "templates/notebooks/example.ipynb") -> dict[str, object]:
    """Return a minimal valid curated template-flow entry."""
    return {
        "notebook_key": "example",
        "notebook_label": "`example`",
        "segment_intro": "Curated example flow.",
        "segments": [{"title": "Curated step", "symbols": ["curated_function"]}],
        "template_path": template_path,
    }


def _write_notebook(root: Path, source: str) -> None:
    """Write a notebook containing one code cell."""
    path = root / "templates" / "notebooks" / "example.ipynb"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps({"cells": [{"cell_type": "code", "source": [source]}]}),
        encoding="utf-8",
    )


def test_curated_flow_allows_additional_direct_public_notebook_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Notebook calls outside curated flow metadata do not affect validation or rendering inputs."""
    _write_notebook(tmp_path, "curated_function()\nadditional_public_function()\n")
    monkeypatch.setattr(generator, "ROOT", tmp_path)
    flows = [_flow()]
    symbols = {"curated_function": object(), "additional_public_function": object()}

    generator._validate_template_flow_docs(flows, set(symbols))

    _, example_usage = generator._derive_template_usage_by_kind(flows, symbols)
    assert example_usage["curated_function"] == ["example"]
    assert example_usage["additional_public_function"] == []


def test_curated_flow_does_not_parse_notebook_call_expressions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Curated flow metadata remains usable even when notebook code is not parseable Python."""
    _write_notebook(tmp_path, "curated_function(\n")
    monkeypatch.setattr(generator, "ROOT", tmp_path)

    generator._validate_template_flow_docs([_flow()], {"curated_function"})


def test_curated_flow_rejects_unknown_public_symbols(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every curated symbol must remain part of the public API."""
    _write_notebook(tmp_path, "")
    monkeypatch.setattr(generator, "ROOT", tmp_path)

    with pytest.raises(RuntimeError, match="references unknown symbol: curated_function"):
        generator._validate_template_flow_docs([_flow()], {"different_function"})


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda flow: flow.pop("segment_intro"), "require a non-empty segment_intro"),
        (lambda flow: flow.update(segments=[]), "require a non-empty segments list"),
        (
            lambda flow: flow["segments"].append({"title": "Duplicate", "symbols": ["curated_function"]}),
            "contains duplicate symbol",
        ),
    ],
)
def test_curated_flow_structural_validation_remains_strict(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutate: Callable[[dict[str, object]], object],
    message: str,
) -> None:
    """Required fields, segments, and unique symbols remain validated."""
    _write_notebook(tmp_path, "")
    monkeypatch.setattr(generator, "ROOT", tmp_path)
    flow = _flow()
    mutate(flow)

    with pytest.raises(RuntimeError, match=message):
        generator._validate_template_flow_docs([flow], {"curated_function"})

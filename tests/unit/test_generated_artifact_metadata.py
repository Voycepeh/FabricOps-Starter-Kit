"""Tests for shared generated-artifact metadata helpers."""

from __future__ import annotations

from pathlib import Path

from scripts import generated_artifact_metadata as metadata


def test_sync_home_public_function_count_uses_generated_reference_count(tmp_path: Path) -> None:
    reference_index = tmp_path / "reference.md"
    reference_index.write_text(
        '<strong class="reference-kpi-value">28</strong>\n'
        '<span class="reference-kpi-title">Public functions</span>\n',
        encoding="utf-8",
    )
    home_index = tmp_path / "index.md"
    home_index.write_text(
        '<span><!-- FABRICOPS_PUBLIC_FUNCTION_COUNT --><strong>29</strong>'
        '<span> public callable functions</span><!-- /FABRICOPS_PUBLIC_FUNCTION_COUNT --></span>\n',
        encoding="utf-8",
    )

    count = metadata.sync_home_public_function_count(reference_index, home_index)

    assert count == 28
    assert (
        '<!-- FABRICOPS_PUBLIC_FUNCTION_COUNT --><strong>28</strong>'
        '<span> public callable functions</span><!-- /FABRICOPS_PUBLIC_FUNCTION_COUNT -->'
        in home_index.read_text(encoding="utf-8")
    )


def test_function_reference_metadata_update_triggers_home_count_sync(
    tmp_path: Path,
    monkeypatch,
) -> None:
    sync_calls: list[bool] = []
    monkeypatch.setattr(
        metadata,
        "sync_home_public_function_count",
        lambda: sync_calls.append(True) or 28,
    )

    metadata.update_generated_artifact_metadata(
        artifact_key=metadata.PUBLIC_FUNCTION_REFERENCE_ARTIFACT_KEY,
        label="Individual function reference pages",
        generator="scripts/generate_individual_function_reference_pages.py",
        output_path="docs/api/reference",
        metadata_path=tmp_path / "generated-artifacts.json",
    )

    assert sync_calls == [True]

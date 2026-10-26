"""Regression coverage for setup_notebook store-key resolution."""

from __future__ import annotations

import pytest

from fabricops_kit import FabricStore, FrameworkConfig, PathConfig, setup_notebook

pytestmark = pytest.mark.unit


def _config() -> FrameworkConfig:
    return FrameworkConfig(
        path_config=PathConfig(
            paths={
                "dev": {
                    "Bronze": FabricStore(
                        env="dev", workspace_id="workspace", item_id="bronze-id", kind="lakehouse"
                    ),
                    "Silver": FabricStore(
                        env="dev", workspace_id="workspace", item_id="silver-id", kind="lakehouse"
                    ),
                    "Gold": FabricStore(
                        env="dev", workspace_id="workspace", item_id="gold-id", kind="warehouse"
                    ),
                    "Metadata": FabricStore(
                        env="dev",
                        workspace_id="workspace",
                        item_id="metadata-id",
                        kind="lakehouse",
                        schema_enabled=True,
                        schema="governance",
                    ),
                }
            }
        )
    )


def test_setup_notebook_defaults_to_configured_store_keys() -> None:
    """Omitting required_targets should validate the stores declared for the environment."""
    context = setup_notebook(_config(), env="dev", local_fallback_name="00_env_config")

    assert list(context.paths) == ["Bronze", "Silver", "Gold", "Metadata"]
    assert all(store.key == key for key, store in context.paths.items())
    assert context.readiness_status == "ready"


def test_setup_notebook_readiness_does_not_require_optional_store_name() -> None:
    """Resolved stores pass readiness when no physical FabricStore.name is supplied."""
    context = setup_notebook(
        _config(), env="dev", required_targets=["Bronze", "Gold"], local_fallback_name="02_pipeline"
    )

    path_checks = {check.name: check for check in context.validation_results if check.name.startswith("path:")}
    assert path_checks["path:Bronze"].status == "pass"
    assert path_checks["path:Gold"].status == "pass"
    assert context.paths["Bronze"].name is None


def test_explicit_setup_summary_reports_failed_checks(capsys, monkeypatch) -> None:
    """Make startup warnings and failures visible even when the result is discarded."""
    from fabricops_kit.io import shared as io
    def unavailable():
        raise RuntimeError("No active Spark session")
    monkeypatch.setattr(io, "get_spark_session", unavailable)
    setup_notebook(_config(), env="dev", notebook_name="invalid_name", config_workspace_id="ignored-workspace")

    output = capsys.readouterr().out
    assert "Configuration: explicit configuration" in output
    assert "00_env_config" not in output
    assert "ignored-workspace" not in output
    assert "Environment: dev" in output
    assert "- Gold: Gold (warehouse;" in output
    assert "Readiness: ready" in output
    assert "notebook_naming" not in output
    assert "Notebook name does not match" not in output
    assert "- warn: spark_session:" in output


def test_setup_summary_handles_no_requested_targets(capsys) -> None:
    """Empty target selection should still show readiness and a useful summary."""
    setup_notebook(_config(), env="dev", required_targets=[], local_fallback_name="02_pipeline")

    output = capsys.readouterr().out
    assert "Targets:\n- None requested" in output
    assert "Readiness: ready" in output

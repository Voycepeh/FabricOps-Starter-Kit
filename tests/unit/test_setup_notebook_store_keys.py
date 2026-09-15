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
                    "bronze": FabricStore(
                        env="dev", workspace_id="workspace", item_id="bronze-id", kind="lakehouse"
                    ),
                    "silver": FabricStore(
                        env="dev", workspace_id="workspace", item_id="silver-id", kind="lakehouse"
                    ),
                    "gold": FabricStore(
                        env="dev", workspace_id="workspace", item_id="gold-id", kind="warehouse"
                    ),
                    "metadata": FabricStore(
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

    assert list(context.paths) == ["bronze", "silver", "gold", "metadata"]
    assert all(store.key == key for key, store in context.paths.items())
    assert context.readiness_status == "ready"


def test_setup_notebook_readiness_does_not_require_removed_store_name() -> None:
    """Resolved stores should pass readiness without the removed FabricStore.name field."""
    context = setup_notebook(
        _config(), env="dev", required_targets=["bronze", "gold"], local_fallback_name="02_pipeline"
    )

    path_checks = {check.name: check for check in context.validation_results if check.name.startswith("path:")}
    assert path_checks["path:bronze"].status == "pass"
    assert path_checks["path:gold"].status == "pass"
    assert not hasattr(context.paths["bronze"], "name")

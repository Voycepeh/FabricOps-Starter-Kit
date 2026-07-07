"""Tests for metadata catalogue browser widget helpers."""

from __future__ import annotations

import pytest

import fabricops_kit
from fabricops_kit.config.shared import FabricStore, FrameworkConfig, PathConfig
from fabricops_kit.widgets import widget_browse_metadata_catalogue as public_widget
from fabricops_kit.widgets.widget_browse_metadata_catalogue import (
    _catalogue_table_names_for_target,
    _configured_fabric_store_targets,
    _filter_metadata_catalogue,
)

pytestmark = pytest.mark.unit


def _config():
    return FrameworkConfig(
        path_config=PathConfig(
            paths={
                "dev": {
                    "product": FabricStore("dev", "ws", "prod-id", "dev_product", "lakehouse"),
                    "raw": FabricStore("dev", "ws", "raw-id", "dev_raw", "lakehouse"),
                    "metadata": FabricStore("dev", "ws", "meta-id", "dev_metadata", "lakehouse"),
                    "": object(),
                }
            }
        )
    )


def test_configured_fabric_store_targets_are_logical_sorted_and_deduplicated():
    """Verify configured targets use logical config keys rather than physical store names."""
    assert _configured_fabric_store_targets({"config": _config(), "env": "dev"}) == ["metadata", "product", "raw"]


def test_catalogue_table_names_are_limited_to_selected_store(spark_session):
    """Verify table options come from distinct names for the selected FabricStore target."""
    catalogue = spark_session.createDataFrame(
        [
            ("orders", "product"),
            ("orders", "product"),
            ("customers", "raw"),
            ("", "product"),
        ],
        "table_name string, fabric_store_target string",
    )

    assert _catalogue_table_names_for_target(catalogue, "product") == ["orders"]


def test_filter_metadata_catalogue_honors_table_agreement_precedence_and_missing_columns(spark_session):
    """Verify catalogue filtering uses store, table, and optional agreement columns."""
    catalogue = spark_session.createDataFrame(
        [
            ("orders", "product", "a1", "v1"),
            ("orders", "product", "a2", "v1"),
            ("orders", "raw", "a1", "v1"),
        ],
        "table_name string, fabric_store_target string, agreement_id string, contract_version string",
    )

    rows = _filter_metadata_catalogue(
        catalogue,
        fabric_store_target="product",
        table_name="orders",
        agreement_id="a2",
        contract_version="v1",
    ).collect()

    assert [row.agreement_id for row in rows] == ["a2"]
    assert _filter_metadata_catalogue(catalogue.drop("agreement_id"), fabric_store_target="product", table_name="missing").count() == 0


def test_widget_is_publicly_importable():
    """Verify metadata catalogue browser is exported at package root."""
    assert public_widget is not None
    assert fabricops_kit.widget_browse_metadata_catalogue is public_widget

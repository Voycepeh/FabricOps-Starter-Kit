"""Central Governance reads all Engineering evidence without changing workspace identity."""
from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

from tests.helpers import framework_config

pytestmark = pytest.mark.unit


def _central_config():
    config = framework_config()
    config.path_config.paths["prod"] = dict(config.path_config.paths["dev"])
    config.path_config.paths["governance"] = {
        "Metadata": config.path_config.paths["dev"]["Metadata"],
    }
    return config


def test_governance_catalogue_includes_all_engineering_observations(monkeypatch):
    contracts = importlib.import_module("fabricops_kit.data_contract.shared")
    config = _central_config()
    entries = [
        {"environment_name": "dev", "table_id": "shared", "metadata_level": "table",
         "table_name": "orders", "is_active": True},
        {"environment_name": "prod", "table_id": "shared", "metadata_level": "table",
         "table_name": "orders", "is_active": True},
        {"environment_name": "dev", "table_id": "shared", "column_id": "c1",
         "metadata_level": "column", "is_active": True},
        {"environment_name": "retired", "table_id": "old", "metadata_level": "table",
         "is_active": True},
    ]
    calls = []

    def read(table, **kwargs):
        calls.append(table)
        assert kwargs["context"]["env"] == "governance"
        return entries

    monkeypatch.setattr(contracts, "read_lakehouse_table", read)
    result = contracts.list_contract_governance_state(
        config=config, env="governance", spark_session=object(), include_contracts=False,
    )
    assert {(r["environment_name"], r["table_id"]) for r in result["tables"]} == {
        ("dev", "shared"), ("prod", "shared"),
    }
    assert result["contracts"] == []
    assert calls == ["METADATA_DATA_CATALOGUE"]


def test_governance_can_read_pipeline_runs_across_environments(monkeypatch):
    activation = importlib.import_module("fabricops_kit.activated_pipeline.shared")
    config = _central_config()
    rows = [{"environment_name": "dev", "run_id": "dev-run"},
            {"environment_name": "prod", "run_id": "prod-run"}]

    class FakeFrame:
        def filter(self, *_args, **_kwargs):
            raise AssertionError("The central record browser must not filter by environment.")

        def collect(self):
            return rows

    monkeypatch.setattr(activation, "read_lakehouse_table", lambda *args, **kwargs: FakeFrame())
    monkeypatch.setattr(activation, "validate_pipeline_run", lambda row: row)
    actual = activation.metadata_records(
        "METADATA_PIPELINE_RUN", context={"config": config, "env": "governance"},
        spark_session=object(), all_environments=True,
    )
    assert [r["environment_name"] for r in actual] == ["dev", "prod"]

    with pytest.raises(ValueError, match="central Governance context"):
        activation.metadata_records(
            "METADATA_PIPELINE_RUN", context={"config": config, "env": "dev"},
            spark_session=object(), all_environments=True,
        )

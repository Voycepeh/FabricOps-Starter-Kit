"""Inspect the single-row Registry MERGE and exact acknowledgement recovery."""
# ruff: noqa: D103
import copy
import re
import sys
from types import SimpleNamespace

import pytest

from fabricops_kit.activated_pipeline import shared as service
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types


@pytest.fixture
def delta_authority(monkeypatch):
    central = {"row": service.empty_pipeline_authority(), "after_commit": False, "before_commit": False}
    calls = []
    context = {"config": {}, "env": "DEV"}
    monkeypatch.setattr(service, "resolve_fabric_context", lambda context=None: ({}, "DEV", context))
    monkeypatch.setattr(service, "resolve_configured_lakehouse_table", lambda *a, **kw: ("Metadata", service.PIPELINE_AUTHORITY_TABLE, "engineering", "configured/authority"))
    monkeypatch.setattr(service, "build_runtime_audit_fields", lambda **kw: {})
    monkeypatch.setattr(service, "authority_records", lambda **kw: copy.deepcopy(central["row"]))
    class Merge:
        def alias(self, name): return self
        def merge(self, source, predicate):
            assert predicate == "target.authority_id = source.authority_id"
            self.row = source.row
            return self
        def whenMatchedUpdate(self, set):
            self.changes = set
            return self
        def execute(self):
            assert "snapshot_json" not in self.changes
            assert all(self.changes[key] == f"source.`{key}`" for key in ("approvals", "reservations", "registrations"))
            assert "raise_error('Stale Pipeline Registry authority; refresh')" in self.changes["token"]
            expected = re.search("target.token = '([^']*)'", self.changes["token"]).group(1)
            calls.append("merge")
            if central["before_commit"]: raise OSError("write failed")
            if expected != central["row"]["token"]: raise ValueError("Stale Pipeline Registry authority")
            central["row"] = copy.deepcopy(self.row)
            if central["after_commit"]: raise OSError("acknowledgement lost")
    class Frame:
        def __init__(self, rows): self.row = rows[0]
        def alias(self, name): return self
    spark = SimpleNamespace(sql=lambda statement: pytest.fail("runtime DDL is forbidden"),
                            createDataFrame=lambda rows, schema: Frame(rows))
    monkeypatch.setitem(sys.modules, "delta.tables", SimpleNamespace(DeltaTable=SimpleNamespace(forPath=lambda *_: Merge())))
    monkeypatch.setattr(service, "get_spark_session", lambda supplied=None, *_args, **_kwargs: spark)
    return context, central, calls


def test_existing_singleton_updates_atomically_and_stale_token_fails(delta_authority):
    context, central, calls = delta_authority
    proposed = {"environments": {}}
    service.environment_activation(proposed, "DEV")["revision"] = "release-one"
    service.commit_pipeline_authority(proposed, expected_token="initial", context=context)
    committed = copy.deepcopy(central["row"])
    assert committed["revisions"] == [{"environment_name": "DEV", "revision": "release-one"}]
    assert calls == ["merge"]
    with pytest.raises(ValueError, match="Stale"):
        service.commit_pipeline_authority({"environments": {}}, expected_token="initial", context=context)
    assert central["row"] == committed


def test_failure_exposes_no_partial_snapshot_and_lost_acknowledgement_is_confirmed(delta_authority):
    context, central, _calls = delta_authority
    proposed = {"environments": {}}
    service.environment_activation(proposed, "DEV")["revision"] = "release-one"
    original = copy.deepcopy(central["row"])
    central["before_commit"] = True
    with pytest.raises(OSError): service.commit_pipeline_authority(proposed, expected_token="initial", context=context)
    assert central["row"] == original
    central.update(before_commit=False, after_commit=True)
    result = service.commit_pipeline_authority(proposed, expected_token="initial", context=context)
    assert result == central["row"]["token"]

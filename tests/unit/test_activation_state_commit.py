"""Exercise the production Delta authority mutation and acknowledgement behavior."""
# ruff: noqa: D103
import copy
import json
import re
import sys
from types import SimpleNamespace

import pytest

from fabricops_kit.activated_pipeline import shared as service


@pytest.fixture
def delta_authority(monkeypatch):
    """Simulate Delta execution while inspecting the actual production MERGE expressions."""
    central = {"token": "initial", "state": json.loads(service.empty_activation_state()), "after_commit": False, "before_commit": False}
    calls = []
    context = {"config": {}, "env": "DEV"}
    monkeypatch.setattr(service, "resolve_fabric_context", lambda context=None: ({}, "DEV", context))
    monkeypatch.setattr(service, "resolve_configured_lakehouse_table", lambda *a, **kw: ("Metadata", service.ACTIVATION_STATE_TABLE, "governance", "configured/authority"))
    monkeypatch.setattr(service, "build_runtime_audit_fields", lambda **kw: {})
    monkeypatch.setattr(service, "read_activation_state", lambda **kw: (central["token"], copy.deepcopy(central["state"])))
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
            assert self.changes["snapshot_json"] == "source.snapshot_json"
            assert "raise_error('Stale activation revision; refresh')" in self.changes["token"]
            expected = re.search("target.token = '([^']*)'", self.changes["token"]).group(1)
            calls.append("merge")
            if central["before_commit"]: raise OSError("write failed")
            if expected != central["token"]: raise ValueError("Stale activation revision")
            central.update(token=self.row["token"], state=json.loads(self.row["snapshot_json"]))
            if central["after_commit"]: raise OSError("acknowledgement lost")
    class Frame:
        def __init__(self, rows): self.row = rows[0]
        def alias(self, name): return self
    spark = SimpleNamespace(sql=lambda statement: calls.append(statement),
                            createDataFrame=lambda rows, schema: Frame(rows))
    monkeypatch.setitem(sys.modules, "delta.tables", SimpleNamespace(DeltaTable=SimpleNamespace(forPath=lambda *_: Merge())))
    monkeypatch.setattr(service, "get_spark_session", lambda supplied=None: spark)
    return context, central, calls


def test_existing_singleton_updates_atomically_and_stale_token_fails(delta_authority):
    context, central, calls = delta_authority
    proposed = copy.deepcopy(central["state"])
    service.environment_activation(proposed, "DEV")["revision"] = "release-one"
    service.commit_activation_state(proposed, expected_token="initial", context=context)
    assert central["state"] == proposed
    assert "Serializable" in calls[0]
    with pytest.raises(ValueError, match="Stale"):
        service.commit_activation_state(json.loads(service.empty_activation_state()), expected_token="initial", context=context)
    assert central["state"] == proposed


def test_failure_exposes_no_partial_snapshot_and_lost_acknowledgement_is_confirmed(delta_authority):
    context, central, _calls = delta_authority
    proposed = copy.deepcopy(central["state"])
    service.environment_activation(proposed, "DEV")["revision"] = "release-one"
    central["before_commit"] = True
    with pytest.raises(OSError): service.commit_activation_state(proposed, expected_token="initial", context=context)
    assert central["state"] == json.loads(service.empty_activation_state())
    central.update(before_commit=False, after_commit=True)
    result = service.commit_activation_state(proposed, expected_token="initial", context=context)
    assert result == central["token"] and central["state"] == proposed

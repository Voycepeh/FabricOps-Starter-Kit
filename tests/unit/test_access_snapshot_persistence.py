"""Tests for configured OneLake snapshot persistence and Catalogue guards."""

import importlib
from pathlib import Path

import pytest


def test_shared_access_persistence_always_appends_to_metadata(monkeypatch):
    """Persist every scanner result through the same append-only metadata route."""
    shared = importlib.import_module("fabricops_kit.access_scanner.shared")
    writes = []

    monkeypatch.setattr(shared, "metadata_table_physical_schema", lambda config, table: "engineering")
    monkeypatch.setattr(
        shared,
        "write_lakehouse_table",
        lambda df, table, **kwargs: writes.append((df, table, kwargs)),
    )

    validated = []
    monkeypatch.setattr(shared, "_require_catalogue_assets", lambda df, **kwargs: validated.append((df, kwargs)))
    frame = object()
    shared.persist_access_rows(
        frame,
        config={"config": "value"},
        workspace_id="dev",
        context={"scope_workspace_id": "dev"},
        persist=True,
        transaction_id="snapshot",
    )

    assert validated[0][0] is frame
    assert len(writes) == 1
    assert writes[0][0] is frame
    assert writes[0][1] == "METADATA_DATA_ACCESS"
    assert writes[0][2]["store"] == "Metadata"
    assert writes[0][2]["schema"] == "engineering"
    assert writes[0][2]["mode"] == "append"
    assert writes[0][2]["options"] == {"txnAppId": "snapshot", "txnVersion": "0"}


@pytest.mark.parametrize("parent_count", [0, 1, 2])
def test_access_append_requires_one_physical_catalogue_parent(monkeypatch, spark_session, parent_count):
    """Reject missing or duplicate Catalogue parents before appending observations."""
    shared = importlib.import_module("fabricops_kit.access_scanner.shared")
    reader = importlib.import_module("fabricops_kit.io.read_lakehouse_table")
    fields = "asset_workspace_id string, table_id string, asset_type string"
    reference = ("physical", "orders", "TABLE")
    access = spark_session.createDataFrame([reference], fields)
    parents = spark_session.createDataFrame(
        [("other", "orders", "TABLE", True), ("physical", "orders", "FILE", True)]
        + [(*reference, True)] * parent_count,
        fields + ", is_active boolean",
    )
    writes = []
    monkeypatch.setattr(reader, "read_lakehouse_table", lambda *a, **kw: parents)
    monkeypatch.setattr(shared, "write_lakehouse_table", lambda *a, **kw: writes.append(a))
    context = dict(config={}, workspace_id="execution", context={}, persist=True, transaction_id="snapshot")
    if parent_count == 1:
        shared.persist_access_rows(access, **context)
        assert len(writes) == 1
    else:
        with pytest.raises(ValueError, match="requires exactly one active Catalogue asset"):
            shared.persist_access_rows(access, **context)
        assert not writes


def test_shared_access_persistence_can_be_disabled(monkeypatch):
    """Allow notebook authors to inspect a scan without writing metadata."""
    shared = importlib.import_module("fabricops_kit.access_scanner.shared")
    monkeypatch.setattr(
        shared,
        "write_lakehouse_table",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("write should not run")),
    )

    shared.persist_access_rows(
        object(),
        config={},
        workspace_id="dev",
        context={},
        persist=False,
        transaction_id="snapshot",
    )


def test_access_scanners_do_not_introduce_microsoft_graph_dependencies():
    """Keep access discovery on existing Fabric and SQL sources without Graph."""
    scanner_root = Path("src/fabricops_kit/access_scanner")
    source = "\n".join(path.read_text(encoding="utf-8").lower() for path in scanner_root.glob("*.py"))

    assert "graph.microsoft.com" not in source
    assert "groupmember.readbasic.all" not in source
    assert "directory.read.all" not in source
    assert "import msal" not in source

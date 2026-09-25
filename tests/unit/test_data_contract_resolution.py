"""Focused tests for runtime Data Contract resolution."""
# ruff: noqa: D101, D102, D103, D107

from __future__ import annotations

import json
import re
from types import SimpleNamespace

import pytest

from fabricops_kit.pipeline import shared

pytestmark = pytest.mark.unit


class RecordingFrame:
    """Small Spark-like frame that records filtering and collection order."""

    def __init__(self, rows, operations=None):
        self.rows = list(rows)
        self.operations = operations if operations is not None else []

    def filter(self, predicate):
        self.operations.append(("filter", predicate))
        rows = self.rows
        for column in ("table_id", "contract_id"):
            match = re.search(rf"`{column}` = '((?:''|[^'])*)'", predicate)
            if match:
                value = match.group(1).replace("''", "'")
                rows = [row for row in rows if str(row.get(column) or "") == value]
        version = re.search(r"`contract_version` = (-?\d+)", predicate)
        if version:
            rows = [row for row in rows if int(row.get("contract_version") or 0) == int(version.group(1))]
        if "`is_active` = TRUE" in predicate:
            rows = [row for row in rows if row.get("is_active") is True]
        return RecordingFrame(rows, self.operations)

    def limit(self, count):
        self.operations.append(("limit", count))
        return RecordingFrame(self.rows[:count], self.operations)

    def collect(self):
        self.operations.append(("collect", None))
        return [SimpleNamespace(**row) for row in self.rows]


def contract_row(
    *,
    contract_id="contract-a",
    contract_version=1,
    table_id="table-a",
    status="frozen",
    is_active=True,
):
    payload = {
        "contract": {"contract_id": contract_id, "contract_version": contract_version},
        "table": {"table_id": table_id},
    }
    return {
        "contract_id": contract_id,
        "contract_version": contract_version,
        "table_id": table_id,
        "status": status,
        "is_active": is_active,
        "agreement_id": "agreement-a",
        "agreement_version": "1",
        "contract_payload_json": json.dumps(payload),
    }


def install_contract_frame(monkeypatch, rows):
    frame = RecordingFrame(rows)
    monkeypatch.setattr(shared, "read_lakehouse_table", lambda *args, **kwargs: frame)
    monkeypatch.setattr(shared, "metadata_table_physical_schema", lambda *args, **kwargs: None)
    return frame


def test_active_contract_filters_and_limits_before_collect(monkeypatch):
    frame = install_contract_frame(
        monkeypatch,
        [contract_row(), contract_row(table_id="other-table", contract_id="contract-other")],
    )

    resolved = shared.resolve_active_data_contract(object(), "prod", "table-a")

    assert resolved["contract_id"] == "contract-a"
    assert frame.operations == [
        ("filter", "`table_id` = 'table-a' AND `is_active` = TRUE"),
        ("limit", 2),
        ("collect", None),
    ]


def test_multiple_active_contracts_still_raise_integrity_error(monkeypatch):
    frame = install_contract_frame(
        monkeypatch,
        [contract_row(), contract_row(contract_id="contract-b", contract_version=2)],
    )

    with pytest.raises(RuntimeError, match="multiple active versions"):
        shared.resolve_active_data_contract(object(), "prod", "table-a")

    assert ("limit", 2) in frame.operations


def test_optional_active_resolution_preserves_missing_and_inactive_behaviour(monkeypatch):
    frame = install_contract_frame(monkeypatch, [contract_row(table_id="other-table")])
    assert shared.resolve_active_data_contract(
        object(), "dev", "table-a", required=False
    ) is None
    assert frame.operations[-3:] == [
        ("filter", "`table_id` = 'table-a'"),
        ("limit", 1),
        ("collect", None),
    ]

    install_contract_frame(monkeypatch, [contract_row(status="frozen", is_active=False)])
    with pytest.raises(ValueError, match="No active Data Contract"):
        shared.resolve_active_data_contract(object(), "dev", "table-a", required=False)


def test_exact_contract_version_filters_and_limits_before_collect(monkeypatch):
    frame = install_contract_frame(
        monkeypatch,
        [
            contract_row(status="frozen", is_active=False),
            contract_row(contract_version=2, status="frozen", is_active=False),
            contract_row(contract_id="contract-b", status="frozen", is_active=False),
        ],
    )

    resolved = shared.resolve_data_contract_version(
        object(), "dev", "table-a", "contract-a", 1
    )

    assert resolved["contract_version"] == 1
    assert frame.operations == [
        ("filter", "`contract_id` = 'contract-a' AND `contract_version` = 1"),
        ("limit", 2),
        ("collect", None),
    ]


def test_duplicate_exact_contract_versions_still_raise(monkeypatch):
    frame = install_contract_frame(
        monkeypatch,
        [
            contract_row(status="frozen", is_active=False),
            contract_row(status="frozen", is_active=False),
        ],
    )

    with pytest.raises(RuntimeError, match="duplicate version rows"):
        shared.resolve_data_contract_version(
            object(), "dev", "table-a", "contract-a", 1
        )

    assert ("limit", 2) in frame.operations


def test_exact_contract_version_rejects_draft(monkeypatch):
    install_contract_frame(monkeypatch, [contract_row(status="draft", is_active=False)])

    with pytest.raises(ValueError, match="must be frozen"):
        shared.resolve_data_contract_version(
            object(), "dev", "table-a", "contract-a", 1
        )


@pytest.mark.parametrize(
    ("rows", "contract_id", "version", "table_id", "message"),
    [
        ([contract_row()], "missing", 1, "table-a", "does not exist"),
        ([contract_row()], "contract-a", 2, "table-a", "does not exist"),
        ([contract_row()], "contract-a", 1, "other-table", "does not belong"),
    ],
)
def test_exact_resolution_preserves_non_matching_errors(
    monkeypatch, rows, contract_id, version, table_id, message
):
    install_contract_frame(monkeypatch, rows)

    with pytest.raises(ValueError, match=message):
        shared.resolve_data_contract_version(
            object(), "dev", table_id, contract_id, version
        )

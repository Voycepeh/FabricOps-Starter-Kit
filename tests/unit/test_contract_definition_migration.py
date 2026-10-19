"""Payload-only definitions and conservative migration of retired side tables."""

from copy import deepcopy
import json
from types import SimpleNamespace

import pytest

from fabricops_kit.data_contract import migration
from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.pipeline import shared as runtime


def _payload(version=1):
    return {
        "contract": {"contract_id": "c", "contract_version": version, "status": "frozen"},
        "table": {"table_id": "orders", "columns": [{"column_id": "id", "column_name": "order_id", "data_type": "int"}], "processing": {"load_strategy": "overwrite"}},
        "enrichment": {"table": [], "columns": []}, "guardrails": [],
    }


def _contract(payload=None):
    payload = payload or _payload()
    return {
        "contract_id": "c", "contract_version": payload["contract"]["contract_version"],
        "table_id": "orders", "table_name": "orders", "environment_name": "dev",
        "status": payload["contract"]["status"], "is_active": True,
        "agreement_id": "a", "agreement_version": "1",
        "contract_payload_json": json.dumps(payload),
    }


def _enrichment(**changes):
    return {
        "contract_id": "c", "contract_version": 1, "environment_name": "dev",
        "enrichment_id": "description", "enrichment_level": "table", "column_id": "",
        "enrichment_type": "Description", "value": "Orders", **changes,
    }


def _rule(kind="schema", **changes):
    return {
        "guardrail_rule_id": kind, "guardrail_version": 1,
        "contract_id": "c", "contract_version": 1, "environment_name": "dev",
        "column_id": "id" if kind == "sensitive_data" else "",
        "guardrail_type": kind, "rule_id": kind, "rule_type": "uniqueness" if kind == "grain" else kind,
        "action": "Block" if kind in {"schema", "grain", "sensitive_data"} else "Warn",
        "is_active": True,
        "rule_parameters": {"columns": ["order_id"]} if kind == "grain" else {"scope": "column", "treatment": "remove"} if kind == "sensitive_data" else {},
        **changes,
    }


def _plan(rows=None, enrichment=None, guardrails=None):
    return migration.plan_contract_definition_migration(
        contract_rows=rows if rows is not None else [_contract()],
        enrichment_rows=enrichment or [], guardrail_rows=guardrails or [], environment_name="dev",
    )


def test_migration_creates_new_draft_and_repeated_snapshot_is_idempotent():
    """Only the new version contains migrated definitions; frozen bytes stay fixed."""
    frozen = _contract()
    before = deepcopy(frozen)
    side = [_enrichment(), _enrichment(enrichment_id="column-description", enrichment_level="column", column_id="id", value="Order identifier")]
    rules = [_rule(kind) for kind in contracts.GUARDRAIL_TYPES]
    report = _plan([frozen], side, rules)
    assert report["can_apply"] and not report["conflicts"]
    assert frozen == before
    draft = report["drafts"][0]
    assert draft["contract_version"] == 2
    assert draft["status"] == "draft" and draft["is_active"] is False
    assert draft["agreement_id"] is None and draft["agreement_version"] is None
    payload = json.loads(draft["contract_payload_json"])
    assert payload["enrichment"]["table"][0]["value"] == "Orders"
    assert payload["enrichment"]["columns"][0]["value"] == "Order identifier"
    assert all(row["contract_version"] == 2 for row in payload["guardrails"])
    repeated = _plan([frozen, draft], side, rules)
    assert repeated["can_apply"] and repeated["drafts"] == []
    assert repeated["already_migrated"] == ["c"]


def test_conflicts_report_exact_version_field_and_rule_without_drafts():
    """Neither a payload disagreement nor two conflicting side rows can be chosen."""
    payload = _payload()
    payload["guardrails"] = [_rule("freshness", rule_parameters={"max_lag_days": 2})]
    report = _plan([_contract(payload)], guardrails=[_rule("freshness", rule_parameters={"max_lag_days": 7})])
    assert not report["can_apply"] and not report["drafts"]
    assert report["conflicts"] == [{
        "contract_id": "c", "contract_version": 1, "rule": "freshness",
        "field": "rule_parameters.max_lag_days", "payload_value": 2, "side_table_value": 7,
    }]
    duplicate = _plan(enrichment=[_enrichment(), _enrichment(value="Different")])
    assert duplicate["conflicts"][0]["field"] == "value"
    assert not duplicate["drafts"]


@pytest.mark.parametrize("change", [
    {"guardrail_type": "unsupported"}, {"rule_parameters_json": "bad JSON"},
    {"rule_parameters_json": "[]"}, {"column_id": "unknown"}, {"table_id": "other"},
    {"is_active": "false"}, {"action": "Warn"},
])
def test_unrepresentable_guardrails_block_migration(change):
    """Migration reports malformed or incompatible definitions instead of dropping them."""
    report = _plan(guardrails=[_rule(**change)])
    assert not report["can_apply"] and not report["drafts"]
    assert report["conflicts"][0]["contract_version"] == 1


def test_orphans_open_drafts_and_conflicting_newer_payload_block():
    """No missing parent, in-progress draft, or newer changed definition is overwritten."""
    assert _plan(enrichment=[_enrichment(contract_version=9)])["conflicts"]
    draft = _contract({**_payload(2), "contract": {"contract_id": "c", "contract_version": 2, "status": "draft"}})
    assert _plan([_contract(), draft], [_enrichment()])["conflicts"][0]["field"] == "status"
    newer = _payload(2)
    newer["enrichment"]["table"] = [_enrichment(value="Newer governed description")]
    assert _plan([_contract(), _contract(newer)], [_enrichment()])["conflicts"][0]["field"] == "value"


def test_matching_existing_definitions_need_no_migration():
    """Different audit fields or duplicate row identities do not require another version."""
    payload = _payload()
    payload["enrichment"]["table"] = [_enrichment(enrichment_id="canonical-id")]
    assert _plan([_contract(payload)], [_enrichment(_activity_id="another")])["drafts"] == []
    assert _plan(enrichment=[_enrichment(environment_name="prod")])["drafts"] == []


def test_apply_requires_reviewed_snapshot_and_writes_only_contract_drafts(monkeypatch):
    """Dry-run, changed snapshots and conflicts produce no writes; retry appends nothing."""
    frozen = _contract()
    tables = {
        contracts.DATA_CONTRACT_TABLE: [frozen],
        "METADATA_ENRICHMENT": [_enrichment()], "METADATA_GUARDRAIL": [],
    }
    reads, writes = [], []

    def read(name, **kwargs):
        reads.append((name, kwargs))
        return deepcopy(tables[name])

    def write(frame, name, **kwargs):
        writes.append((name, kwargs))
        tables[name].extend(frame)

    monkeypatch.setattr(migration, "read_lakehouse_table", read)
    monkeypatch.setattr(migration, "write_lakehouse_table", write)
    monkeypatch.setattr(migration, "coerce_metadata_row_types", lambda _name, row: row)
    monkeypatch.setattr(migration, "build_runtime_audit_fields", lambda **_kwargs: {})
    spark = SimpleNamespace(createDataFrame=lambda rows, schema: rows)
    args = dict(config={"governance_metadata_schema": "approved"}, env="dev", spark_session=spark)
    report = migration.migrate_contract_definitions(**args)
    assert not writes and not report["applied"]
    assert all(kwargs["store"] == "Metadata" and kwargs["schema"] == "approved" for _, kwargs in reads)
    with pytest.raises(ValueError, match="paused"):
        migration.migrate_contract_definitions(**args, dry_run=False)
    with pytest.raises(ValueError, match="snapshot changed"):
        migration.migrate_contract_definitions(**args, dry_run=False, reviewed_snapshot="stale", authoring_paused=True)
    applied = migration.migrate_contract_definitions(**args, dry_run=False, reviewed_snapshot=report["snapshot_fingerprint"], authoring_paused=True)
    assert applied["applied"] and len(writes) == 1
    assert writes[0][0] == contracts.DATA_CONTRACT_TABLE and writes[0][1]["mode"] == "append"
    assert tables[contracts.DATA_CONTRACT_TABLE][0] == frozen
    repeated_apply = migration.migrate_contract_definitions(
        **args, dry_run=False, reviewed_snapshot=report["snapshot_fingerprint"], authoring_paused=True,
    )
    assert not repeated_apply["applied"] and len(writes) == 1
    retry = migration.migrate_contract_definitions(**args)
    assert not retry["drafts"] and retry["can_apply"]
    migration.migrate_contract_definitions(**args, dry_run=False, reviewed_snapshot=retry["snapshot_fingerprint"], authoring_paused=True)
    assert len(writes) == 1
    tables["METADATA_ENRICHMENT"].append(_enrichment(value="Conflicting"))
    conflict = migration.migrate_contract_definitions(**args)
    with pytest.raises(ValueError, match="Migration conflicts"):
        migration.migrate_contract_definitions(**args, dry_run=False, reviewed_snapshot=conflict["snapshot_fingerprint"], authoring_paused=True)
    assert len(writes) == 1


@pytest.mark.parametrize("kind", sorted(contracts.GUARDRAIL_TYPES))
def test_payload_roundtrip_retains_all_supported_rules_and_disabled_state(kind):
    """Authoring, freezing and runtime resolve one exact payload and skip disabled rules."""
    payload = _payload()
    payload["contract"]["status"] = "draft"
    payload["guardrails"] = [_rule(kind)]
    payload["enrichment"]["table"] = [_enrichment(enrichment_type="Grain", value="One row per order")]
    payload["enrichment"]["columns"] = [_enrichment(enrichment_level="column", column_id="id", enrichment_type="Classification", value="Public")]
    frozen = contracts.freeze_contract_record(draft=_contract(payload), audit={})
    saved = json.loads(frozen["contract_payload_json"])
    assert saved["enrichment"] == payload["enrichment"]
    assert saved["guardrails"] == payload["guardrails"]
    rows = runtime.contract_guardrail_rows(frozen, environment_name="dev", table_id="orders")
    assert rows[0]["guardrail_rule_id"] == kind
    saved["guardrails"][0]["is_active"] = False
    assert runtime.contract_guardrail_rows(_contract(saved), environment_name="dev", table_id="orders") == []


@pytest.mark.parametrize("field,value", [("enrichment", None), ("guardrails", None), ("guardrails", [{}])])
def test_missing_or_malformed_definitions_cannot_be_frozen(field, value):
    """Explicit empty collections are valid; malformed definitions fail before freeze."""
    payload = _payload()
    payload["contract"]["status"] = "draft"
    payload[field] = value
    with pytest.raises(ValueError):
        contracts.freeze_contract_record(draft=_contract(payload), audit={})


def test_new_draft_inherits_frozen_definitions_without_reading_side_tables(monkeypatch):
    """New draft creation deep-copies all definitions and rebinds only the new version."""
    identity = contracts.contract_lifecycle_id("orders", "dev")
    payload = _payload()
    payload["contract"]["contract_id"] = identity
    payload["enrichment"]["table"] = [_enrichment(contract_id=identity, enrichment_type="Grain", value="One row per order")]
    payload["enrichment"]["columns"] = [_enrichment(contract_id=identity, column_id="id", enrichment_level="column")]
    payload["guardrails"] = [_rule(kind, contract_id=identity) for kind in sorted(contracts.GUARDRAIL_TYPES)]
    frozen = {**_contract(payload), "contract_id": identity}
    before = deepcopy(frozen)
    tables = {
        contracts.DATA_CONTRACT_TABLE: [frozen],
        "METADATA_DATA_CATALOGUE": [
            {"table_id": "orders", "table_name": "orders", "metadata_level": "table", "environment_name": "dev", "is_active": True},
            {"table_id": "orders", "column_id": "id", "column_name": "order_id", "data_type": "int", "metadata_level": "column", "environment_name": "dev", "is_active": True},
        ],
    }
    monkeypatch.setattr(contracts, "read_lakehouse_table", lambda name, **_kwargs: tables[name])
    monkeypatch.setattr(contracts, "coerce_metadata_row_types", lambda _name, row: row)
    monkeypatch.setattr(contracts, "build_runtime_audit_fields", lambda **_kwargs: {})
    writes = []
    monkeypatch.setattr(contracts, "write_lakehouse_table", lambda rows, *_args, **_kwargs: writes.extend(rows))
    spark = SimpleNamespace(createDataFrame=lambda rows, schema: rows)
    draft = contracts.create_contract_draft(table_id="orders", config={}, env="dev", spark_session=spark)
    copied = json.loads(draft["contract_payload_json"])
    assert frozen == before
    assert len(writes) == 1 and draft["contract_version"] == 2
    assert copied["enrichment"]["table"][0]["value"] == "One row per order"
    assert len(copied["guardrails"]) == 6
    assert all(item["contract_version"] == 2 for item in copied["guardrails"])
    assert json.loads(frozen["contract_payload_json"])["guardrails"][0]["contract_version"] == 1


def test_missing_legacy_tables_are_empty_but_other_read_errors_propagate(monkeypatch):
    """Only explicit missing-table errors are suppressed by migration reads."""
    def read(name, **_kwargs):
        if name == contracts.DATA_CONTRACT_TABLE:
            return [_contract()]
        raise RuntimeError("[TABLE_OR_VIEW_NOT_FOUND] Table does not exist")

    monkeypatch.setattr(migration, "read_lakehouse_table", read)
    report = migration.migrate_contract_definitions(config={}, env="dev", spark_session=object())
    assert report["can_apply"] and not report["drafts"]
    monkeypatch.setattr(migration, "read_lakehouse_table", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("Access denied")))
    with pytest.raises(RuntimeError, match="Access denied"):
        migration.migrate_contract_definitions(config={}, env="dev", spark_session=object())


def test_malformed_frozen_payload_is_a_migration_blocker():
    """A missing authoritative frozen payload cannot be reconstructed by guessing."""
    frozen = {**_contract(), "contract_payload_json": "not JSON"}
    report = _plan([frozen], [_enrichment()])
    assert not report["can_apply"] and not report["drafts"]
    assert report["conflicts"][0]["field"] == "contract_payload_json"


def test_missing_environment_and_competing_active_policies_are_reported():
    """Unknown environment and independently identified competing rules are never chosen."""
    report = _plan(enrichment=[_enrichment(environment_name=None)])
    assert not report["can_apply"]
    assert report["conflicts"][0]["field"] == "environment_name"
    competing = _plan(guardrails=[_rule(), _rule(guardrail_rule_id="second-schema")])
    assert not competing["can_apply"] and not competing["drafts"]
    assert "Competing active Guardrails" in competing["conflicts"][0]["side_table_value"]


def test_widget_assembly_preserves_migration_provenance():
    """Saving a migrated draft cannot lose the fingerprint needed for repeat-run detection."""
    draft = _plan(enrichment=[_enrichment()])["drafts"][0]
    payload = json.loads(draft["contract_payload_json"])
    enrichment = [{**row, "environment_name": "dev"} for row in payload["enrichment"]["table"]]
    assembled, _ = contracts.assemble_contract_payload(
        draft=draft, environment_name="dev", enrichment_rows=enrichment, guardrail_rows=[],
        catalogue_rows=[{"table_id": "orders", "table_name": "orders", "metadata_level": "table", "environment_name": "dev", "is_active": True}],
    )
    assert assembled["definition_migration"] == payload["definition_migration"]

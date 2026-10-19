"""Explicit, report-first migration of retired definition tables into new drafts.

This maintenance operation is never part of setup, authoring, or execution.
Pause Governance authoring and legacy writers while applying a reviewed report.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import uuid
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.shared import is_table_not_found_error
from fabricops_kit.config.metadata_schemas import (
    coerce_metadata_row_types,
    metadata_table_physical_schema,
    metadata_table_schema_registry,
)
from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.io import read_lakehouse_table, write_lakehouse_table

_LEGACY_ENRICHMENT = "METADATA_ENRICHMENT"
_LEGACY_GUARDRAIL = "METADATA_GUARDRAIL"


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _definition(row: dict, *, guardrail: bool) -> dict:
    """Select authored fields, excluding denormalized names and audit history."""
    names = (
        ("guardrail_rule_id", "guardrail_version", "column_id", "guardrail_type", "rule_id", "rule_type", "action")
        if guardrail else ("enrichment_id", "column_id", "enrichment_level", "enrichment_type", "value")
    )
    result = {name: row.get(name) for name in names}
    result["column_id"] = str(row.get("column_id") or "")
    if not guardrail and not str(result.get("enrichment_id") or "").strip():
        result["enrichment_id"] = str(uuid.uuid5(
            uuid.NAMESPACE_URL,
            _json([row.get("environment_name"), row.get("contract_id"),
                   row.get("enrichment_level"), result["column_id"], row.get("enrichment_type")]),
        ))
    if guardrail:
        result["is_active"] = row.get("is_active", True)
        parameters = row.get("rule_parameters", {})
        if "rule_parameters_json" in row:
            parameters = json.loads(row["rule_parameters_json"])
        if not isinstance(parameters, dict):
            raise ValueError("rule_parameters must be a JSON object.")
        result["rule_parameters"] = parameters
    return result


def _key(row: dict, *, guardrail: bool) -> str:
    if guardrail:
        return str(row.get("guardrail_rule_id") or "")
    return "/".join(str(row.get(name) or "") for name in ("enrichment_level", "column_id", "enrichment_type"))


def _differences(left: Any, right: Any, prefix: str = "") -> list[tuple[str, Any, Any]]:
    if isinstance(left, dict) and isinstance(right, dict):
        return [
            difference
            for name in sorted(set(left) | set(right))
            for difference in _differences(left.get(name), right.get(name), f"{prefix}.{name}".strip("."))
        ]
    return [] if left == right else [(prefix, left, right)]


def _plan_contract_definition_migration(
    *, contract_rows: Any, enrichment_rows: Any, guardrail_rows: Any, environment_name: str,
) -> dict[str, Any]:
    """Return proposed draft rows and exact conflicts without performing any IO.

    All conflicts block the entire apply operation. No frozen row is rewritten.
    Existing open drafts are left for Governance to finish or discard first.
    Repeated identical source snapshots are recognized through payload provenance.
    """
    if not str(environment_name or "").strip():
        raise ValueError("environment_name is required for definition migration.")
    report: dict[str, Any] = {"environment_name": environment_name, "drafts": [], "conflicts": [], "already_migrated": []}
    rows = [row for row in contracts.row_dicts(contract_rows) if row.get("environment_name") == environment_name]
    indexed: dict[tuple[str, int], dict] = {}

    def conflict(identity, version, rule, field, old, new):
        report["conflicts"].append({
            "contract_id": identity, "contract_version": version, "rule": rule,
            "field": field, "payload_value": old, "side_table_value": new,
        })

    for row in rows:
        identity, version = contracts.validate_contract_identity(row.get("contract_id"), row.get("contract_version"))
        if (identity, version) in indexed:
            conflict(identity, version, "", "contract_version", "duplicate contract rows", version)
        indexed[identity, version] = row
    sources: dict[str, list[tuple[dict, bool]]] = {}
    for values, guardrail in ((enrichment_rows, False), (guardrail_rows, True)):
        for raw in contracts.row_dicts(values):
            if not str(raw.get("environment_name") or "").strip():
                conflict(raw.get("contract_id"), raw.get("contract_version"), _key(raw, guardrail=guardrail), "environment_name", environment_name, raw.get("environment_name"))
                continue
            if raw.get("environment_name") != environment_name:
                continue
            try:
                identity, version = contracts.validate_contract_identity(raw.get("contract_id"), raw.get("contract_version"))
            except ValueError as exc:
                conflict(raw.get("contract_id"), raw.get("contract_version"), "", "identity", None, str(exc))
                continue
            if (identity, version) not in indexed:
                conflict(identity, version, _key(raw, guardrail=guardrail), "contract_version", "missing parent", version)
                continue
            sources.setdefault(identity, []).append((raw, guardrail))

    for identity, source in sorted(sources.items()):
        owned = [row for row in rows if row["contract_id"] == identity]
        before = len(report["conflicts"])
        payloads = {}
        try:
            for row in owned:
                payload = json.loads(row.get("contract_payload_json") or "null")
                if not isinstance(payload, dict):
                    raise ValueError(f"version {row['contract_version']} has no canonical payload")
                if payload.get("contract", {}).get("contract_id") != identity or int(payload.get("contract", {}).get("contract_version") or 0) != int(row["contract_version"]):
                    raise ValueError(f"version {row['contract_version']} payload identity differs from its row")
                if payload.get("table", {}).get("table_id") != row.get("table_id"):
                    raise ValueError(f"version {row['contract_version']} payload table_id differs from its row")
                contracts.validate_contract_definitions(payload)
                payloads[int(row["contract_version"])] = payload
        except (TypeError, ValueError, KeyError) as exc:
            conflict(identity, row.get("contract_version"), "", "contract_payload_json", None, str(exc))
            continue
        # Fingerprint raw authored source records; malformed JSON is reported below.
        fingerprint = hashlib.sha256(_json(sorted(
            [{name: value for name, value in raw.items() if not name.startswith("_")}
             for raw, _guardrail in source], key=_json,
        )).encode()).hexdigest()
        # Validate each side-table record against its exact immutable version first.
        additions = []
        for raw, guardrail in source:
            version = int(raw["contract_version"])
            payload = payloads[version]
            key = _key(raw, guardrail=guardrail)
            try:
                item = _definition(raw, guardrail=guardrail)
                if raw.get("table_id") and raw["table_id"] != payload["table"]["table_id"]:
                    raise ValueError("side-table table_id differs from its exact contract")
                candidate = deepcopy(payload)
                collection = candidate["guardrails"] if guardrail else candidate["enrichment"]["columns" if item.get("column_id") else "table"]
                existing = next((entry for entry in collection if _key(entry, guardrail=guardrail) == key), None)
                if existing is not None:
                    left, right = _definition(existing, guardrail=guardrail), dict(item)
                    if not guardrail:
                        left.pop("enrichment_id", None)
                        right.pop("enrichment_id", None)
                    for field, old, new in _differences(left, right):
                        conflict(identity, version, key, field, old, new)
                else:
                    collection.append(item)
                    contracts.validate_contract_definitions(candidate)
                    additions.append((version, guardrail, item))
            except (TypeError, ValueError, KeyError) as exc:
                conflict(identity, version, key, "definition", None, str(exc))
        if len(report["conflicts"]) != before:
            continue
        if any(payload.get("definition_migration", {}).get("source_fingerprint") == fingerprint for payload in payloads.values()):
            report["already_migrated"].append(identity)
            continue
        if not additions:
            continue
        drafts = [row for row in owned if row.get("status") == "draft"]
        if drafts:
            conflict(identity, drafts[0]["contract_version"], "", "status", "open draft; finish or discard it before migration", "new draft required")
            continue
        frozen = [row for row in owned if row.get("status") == "frozen"]
        if not frozen:
            conflict(identity, 0, "", "status", "no frozen version to seed", "new draft required")
            continue
        previous = max(frozen, key=lambda row: int(row["contract_version"]))
        payload = deepcopy(payloads[int(previous["contract_version"])])
        for version, guardrail, item in additions:
            key = _key(item, guardrail=guardrail)
            collection = payload["guardrails"] if guardrail else payload["enrichment"]["columns" if item.get("column_id") else "table"]
            existing = next((entry for entry in collection if _key(entry, guardrail=guardrail) == key), None)
            if existing is None:
                collection.append(deepcopy(item))
            else:
                left, right = _definition(existing, guardrail=guardrail), dict(item)
                if not guardrail:
                    left.pop("enrichment_id", None)
                    right.pop("enrichment_id", None)
                for field, old, new in _differences(left, right):
                    conflict(identity, version, key, field, old, new)
        version = max(int(row["contract_version"]) for row in owned) + 1
        payload["contract"] = {"contract_id": identity, "contract_version": version, "status": "draft"}
        for item in [*payload["enrichment"]["table"], *payload["enrichment"]["columns"], *payload["guardrails"]]:
            item.update(contract_id=identity, contract_version=version)
        payload["definition_migration"] = {"source_fingerprint": fingerprint}
        try:
            contracts.validate_contract_definitions(payload)
        except (TypeError, ValueError, KeyError) as exc:
            conflict(identity, version, "", "definition", None, str(exc))
        if len(report["conflicts"]) == before:
            report["drafts"].append({
                **{name: value for name, value in previous.items() if not name.startswith("_")},
                "contract_version": version, "status": "draft", "is_active": False,
                "agreement_id": None, "agreement_version": None, "contract_payload_json": _json(payload),
            })
    report["can_apply"] = not report["conflicts"]
    report["snapshot_fingerprint"] = hashlib.sha256(_json({
        "contracts": sorted(rows, key=_json),
        "enrichment": sorted(contracts.row_dicts(enrichment_rows), key=_json),
        "guardrails": sorted(contracts.row_dicts(guardrail_rows), key=_json),
    }).encode()).hexdigest()
    return report


def migrate_contract_definitions(
    *, config: Any, env: str, spark_session: Any, dry_run: bool = True,
    reviewed_snapshot: str | None = None, authoring_paused: bool = False,
) -> dict[str, Any]:
    """Report retired table conflicts or append reviewed new draft versions.

    Apply requires the dry-run snapshot fingerprint and paused Governance/legacy
    writers. Changed snapshots and any conflicts block all writes. One append
    commits all planned drafts to the configured contract table. The operation
    never updates or deletes an existing row and never deletes a physical table.
    """
    context = {"config": config, "env": env, "_fabricops_suppress_io_log": True}
    schema = metadata_table_physical_schema(config, contracts.DATA_CONTRACT_TABLE)
    snapshots = []
    for name in (contracts.DATA_CONTRACT_TABLE, _LEGACY_ENRICHMENT, _LEGACY_GUARDRAIL):
        try:
            values = contracts.row_dicts(read_lakehouse_table(
                name, store="Metadata", schema=schema, spark_session=spark_session, context=context,
            ))
        except Exception as exc:
            if name == contracts.DATA_CONTRACT_TABLE or not is_table_not_found_error(exc):
                raise
            values = []
        snapshots.append(values)
    report = _plan_contract_definition_migration(
        contract_rows=snapshots[0], enrichment_rows=snapshots[1], guardrail_rows=snapshots[2], environment_name=env,
    )
    report["applied"] = False
    if dry_run:
        return report
    if not authoring_paused or not reviewed_snapshot:
        raise ValueError("Apply requires paused authoring/legacy writers and a reviewed dry-run snapshot fingerprint.")
    if report["conflicts"]:
        raise ValueError("Migration conflicts; no writes performed: " + _json(report["conflicts"]))
    if not report["drafts"]:
        return report
    if reviewed_snapshot != report["snapshot_fingerprint"]:
        raise ValueError("Migration snapshot changed since dry-run; review a new report before applying.")
    if report["drafts"]:
        audit = build_runtime_audit_fields(config=config, env=env, runtime_context=context)
        rows = [coerce_metadata_row_types(contracts.DATA_CONTRACT_TABLE, {**row, **audit}) for row in report["drafts"]]
        frame = spark_session.createDataFrame(rows, schema=metadata_table_schema_registry()[contracts.DATA_CONTRACT_TABLE])
        write_lakehouse_table(frame, contracts.DATA_CONTRACT_TABLE, store="Metadata", schema=schema, context=context, mode="append")
        report["applied"] = True
    return report

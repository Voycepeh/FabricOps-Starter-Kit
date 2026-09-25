"""UI-independent services for authoring versioned Data Contracts.

The functions in this module deliberately accept row-like Python/Spark values
and keep widget rendering concerns out of governance metadata semantics.
"""

from __future__ import annotations

from fabricops_kit.io import read_lakehouse_table, write_lakehouse_table

from collections.abc import Iterable, Mapping
from datetime import date, datetime
import json
import math
from typing import Any
import uuid

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import (
    coerce_metadata_row_types,
    metadata_table_physical_schema,
    metadata_table_schema_registry,
)
from fabricops_kit.data_contract.scheduled_refresh import canonical_scheduled_refresh
from fabricops_kit.pipeline.shared import validated_processing

DATA_CONTRACT_TABLE = "METADATA_DATA_CONTRACT"
ENRICHMENT_TABLE = "METADATA_ENRICHMENT"
GUARDRAIL_TABLE = "METADATA_GUARDRAIL"
GUARDRAIL_TYPES = frozenset({"schema", "freshness", "source_drift", "data_quality", "sensitive_data"})
GUARDRAIL_ACTIONS = frozenset({"Warn", "Block"})
SENSITIVE_DATA_TREATMENTS = frozenset({"tokenize", "mask", "bucket", "remove"})
ENRICHMENT_TYPES_BY_LEVEL = {
    "table": frozenset({"Description", "Classification"}),
    "column": frozenset({"Description", "Classification"}),
}
CONTRACT_SOURCE_TABLES = (
    "METADATA_DATA_CATALOGUE",
    ENRICHMENT_TABLE,
    GUARDRAIL_TABLE,
)
_CONTRACT_NAMESPACE = uuid.UUID("8383c7ec-23f5-4ad8-92ea-0871045c310c")


def _metadata_io_context(config: Any, env: str) -> dict[str, Any]:
    """Return quiet internal metadata IO context for Data Contract services."""
    return {"config": config, "env": env, "_fabricops_suppress_io_log": True}


def contract_lifecycle_id(table_id: str, environment_name: str) -> str:
    """Return the stable table/environment identity for one Data Contract lifecycle."""
    table = str(table_id or "").strip()
    environment = str(environment_name or "").strip()
    if not table or not environment:
        raise ValueError("table_id and environment_name are required for a Data Contract lifecycle.")
    return str(uuid.uuid5(_CONTRACT_NAMESPACE, f"{environment}\n{table}"))


def create_contract_draft(
    *, table_id: str, config: Any, env: str, spark_session: Any,
    context: Mapping[str, Any] | None = None, store: str = "Metadata",
    schema: str | None = None,
) -> dict[str, Any]:
    """Create or reopen the one mutable draft for a governed table."""
    lifecycle_id = contract_lifecycle_id(table_id, env)
    runtime_context = {
        "config": config, "env": env, **dict(context or {}),
        "_fabricops_suppress_io_log": True,
    }
    catalogue_rows = row_dicts(read_lakehouse_table(
        "METADATA_DATA_CATALOGUE", store=store,
        schema=metadata_table_physical_schema(config, "METADATA_DATA_CATALOGUE"),
        spark_session=spark_session, context=runtime_context,
    ))
    active_catalogue = [
        row for row in catalogue_rows
        if str(row.get("table_id") or "") == str(table_id).strip()
        and str(row.get("environment_name") or "") == env
        and row.get("is_active") is not False
    ]
    current = _latest(active_catalogue, ("table_id", "column_id"))
    table_rows = [
        row for row in current
        if str(row.get("metadata_level") or "").lower() == "table" or not row.get("column_id")
    ]
    if not table_rows:
        raise ValueError("table_id has no active table-level Catalogue row in the authoring environment.")
    table = table_rows[-1]
    columns = [
        _fields(row, ("column_id", "column_name", "data_type"))
        for row in current if row.get("column_id")
    ]

    rows = row_dicts(read_lakehouse_table(
        DATA_CONTRACT_TABLE, store=store, schema=schema,
        spark_session=spark_session, context=runtime_context,
    ))
    owned = [
        row for row in rows
        if str(row.get("contract_id") or "") == lifecycle_id
        and str(row.get("environment_name") or "") == env
    ]
    drafts = [row for row in owned if str(row.get("status") or "").lower() == "draft"]
    if len(drafts) > 1:
        raise RuntimeError(f"Data Contract integrity error: {table_id!r} has multiple open drafts.")
    if drafts:
        return dict(drafts[0])

    version = max((int(item.get("contract_version") or 0) for item in owned), default=0) + 1
    previous = max(
        (row for row in owned if str(row.get("status") or "").lower() == "frozen"),
        key=lambda row: int(row.get("contract_version") or 0),
        default=None,
    )
    previous_payload = (
        _json_value(previous.get("contract_payload_json"), field="contract_payload_json", default=None)
        if previous else None
    )
    seed = json.loads(json.dumps(previous_payload)) if isinstance(previous_payload, dict) else {}

    strategy = str(table.get("load_strategy") or "").strip()
    if strategy:
        parameters = _json_value(
            table.get("load_strategy_parameters_json"),
            field="load_strategy_parameters_json",
            default={},
        )
        if not isinstance(parameters, dict):
            raise ValueError("Catalogue load_strategy_parameters_json must contain a JSON object.")
        processing = validated_processing({**parameters, "load_strategy": strategy})
        processing_source = "catalogue"
    elif isinstance(previous_payload, dict):
        previous_processing = previous_payload.get("table", {}).get("processing")
        processing = validated_processing(previous_processing) if isinstance(previous_processing, dict) else {"load_strategy": "overwrite"}
        processing_source = "previous_contract"
    else:
        processing = {"load_strategy": "overwrite"}
        processing_source = "default"

    payload = {
        **seed,
        "contract": {
            "contract_id": lifecycle_id,
            "contract_version": version,
            "status": "draft",
        },
        "table": {
            **dict(seed.get("table") or {}),
            **_fields(table, ("table_id", "environment_name", "store_type", "layer", "schema_name", "table_name")),
            "columns": columns,
            "processing": processing,
            "processing_source": processing_source,
            "writer": {
                "notebook_id": str(table.get("_notebook_id") or "").strip(),
                "notebook_name": str(table.get("_notebook_name") or "").strip(),
            },
        },
        "enrichment": dict(seed.get("enrichment") or {"table": [], "columns": []}),
        "guardrails": list(seed.get("guardrails") or []),
    }
    payload["table"].pop("scheduled_refresh", None)
    for item in [*payload["enrichment"].get("table", []), *payload["enrichment"].get("columns", [])]:
        item["contract_id"] = lifecycle_id
        item["contract_version"] = version
    for item in payload["guardrails"]:
        item["contract_id"] = lifecycle_id
        item["contract_version"] = version

    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=runtime_context)
    row = coerce_metadata_row_types(DATA_CONTRACT_TABLE, {
        "contract_id": lifecycle_id,
        "contract_version": version,
        "agreement_id": None,
        "agreement_version": None,
        "table_id": str(table_id).strip(),
        "environment_name": env,
        "contract_payload_json": json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
        "status": "draft",
        "is_active": False,
        **audit,
    })
    write_lakehouse_table(
        spark_session.createDataFrame([row], schema=metadata_table_schema_registry()[DATA_CONTRACT_TABLE]),
        DATA_CONTRACT_TABLE, store=store, schema=schema,
        context=runtime_context, mode="append",
    )
    return row

def _sql_literal(value: Any) -> str:
    """Return one safely quoted scalar for an internal Spark SQL predicate."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return "'" + str(value or "").replace("'", "''") + "'"


def _scoped_rows(frame: Any, *predicates: str) -> list[dict[str, Any]]:
    """Apply lazy Spark predicates before collecting; preserve iterable test inputs."""
    scoped = frame
    if hasattr(scoped, "where"):
        for predicate in predicates:
            if predicate:
                scoped = scoped.where(predicate)
    return row_dicts(scoped)


def row_dicts(value: Any) -> list[dict[str, Any]]:
    """Return a DataFrame or iterable of row-like values as dictionaries."""
    if value is None:
        return []
    source = value.collect() if hasattr(value, "collect") else value
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in source]


def parse_approved_usages(value: Any) -> list[str]:
    """Return the canonical approved-usage list stored by a Data Agreement."""
    parsed = _json_value(value, field="approved_usage_json", default=[])
    if not isinstance(parsed, list) or any(not isinstance(item, str) for item in parsed):
        raise ValueError("approved_usage_json must be a JSON list of strings.")
    return list(dict.fromkeys(item.strip() for item in parsed if item.strip()))


def select_approved_usages(selected: Any, parent: list[str]) -> list[str]:
    """Validate and order a Data Contract usage subset by its Data Agreement."""
    values = list(dict.fromkeys(str(item).strip() for item in (selected or []) if str(item).strip()))
    invalid = sorted(set(values) - set(parent))
    if invalid:
        raise ValueError(
            "Data Contract approved usages must be a subset of the parent Data Agreement "
            "approved usages. Invalid value(s): " + ", ".join(invalid)
        )
    return [item for item in parent if item in values]


def _json_value(value: Any, *, field: str, default: Any) -> Any:
    """Parse a JSON metadata value with an actionable field error."""
    import json

    if value in (None, ""):
        return default
    try:
        return json.loads(str(value))
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{field} must contain valid JSON.") from exc


def _latest(rows: Iterable[Mapping[str, Any]], identity: tuple[str, ...]) -> list[dict[str, Any]]:
    """Select the latest audit row for each logical identity."""
    selected: dict[tuple[str, ...], dict[str, Any]] = {}
    for value in rows:
        row = dict(value)
        key = tuple(str(row.get(field) or "") for field in identity)
        rank = (str(row.get("_committed_at") or ""), str(row.get("_activity_id") or ""))
        current = selected.get(key)
        current_rank = (
            (str(current.get("_committed_at") or ""), str(current.get("_activity_id") or ""))
            if current else None
        )
        if current_rank is None or rank > current_rank:
            selected[key] = row
    return [selected[key] for key in sorted(selected)]


def contract_processing(record: Mapping[str, Any]) -> dict[str, Any]:
    """Return the processing definition stored in one Data Contract payload."""
    payload = _json_value(
        record.get("contract_payload_json"), field="contract_payload_json", default=None
    )
    processing = (
        payload.get("table", {}).get("processing")
        if isinstance(payload, dict) and isinstance(payload.get("table"), dict)
        else None
    )
    return validated_processing(processing) if isinstance(processing, dict) and processing else {}


def contract_processing_source(record: Mapping[str, Any]) -> str:
    """Return how the Data Contract draft processing was resolved."""
    payload = _json_value(
        record.get("contract_payload_json"), field="contract_payload_json", default=None
    )
    if not isinstance(payload, dict) or not isinstance(payload.get("table"), dict):
        return "default"
    return str(payload["table"].get("processing_source") or "default").strip() or "default"


def _payload_authoring_rows(
    payload: Mapping[str, Any], *, contract_id: str, contract_version: int, environment_name: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Convert one draft payload into the row shapes used by the authoring widget."""
    enrichment_doc = payload.get("enrichment") if isinstance(payload, Mapping) else {}
    enrichment_items = [
        *list((enrichment_doc or {}).get("table") or []),
        *list((enrichment_doc or {}).get("columns") or []),
    ]
    enrichment_rows = [
        {
            **dict(item),
            "contract_id": contract_id,
            "contract_version": contract_version,
            "environment_name": environment_name,
        }
        for item in enrichment_items
    ]
    guardrail_rows = []
    for item in list(payload.get("guardrails") or []):
        row = dict(item)
        row["contract_id"] = contract_id
        row["contract_version"] = contract_version
        row["environment_name"] = environment_name
        row["rule_parameters_json"] = json.dumps(
            dict(row.pop("rule_parameters", {}) or {}),
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        row["is_active"] = bool(item.get("is_active", True))
        guardrail_rows.append(row)
    return enrichment_rows, guardrail_rows


def save_contract_draft(
    *,
    draft: Mapping[str, Any],
    payload: Mapping[str, Any],
    config: Any,
    env: str,
    spark_session: Any,
    context: Mapping[str, Any] | None = None,
    store: str = "Metadata",
    schema: str | None = None,
) -> dict[str, Any]:
    """Overwrite the canonical JSON for one mutable Data Contract draft."""
    contract_id, contract_version = validate_contract_identity(
        draft.get("contract_id"), draft.get("contract_version")
    )
    if str(draft.get("status") or "").lower() != "draft":
        raise ValueError("Only a draft Data Contract version can be saved.")
    if str(draft.get("environment_name") or "") != str(env):
        raise ValueError("Draft Data Contract must stay in the authoring environment.")

    canonical = json.loads(json.dumps(dict(payload), default=str))
    canonical["contract"] = {
        "contract_id": contract_id,
        "contract_version": contract_version,
        "status": "draft",
    }
    if not isinstance(canonical.get("table"), dict):
        raise ValueError("Data Contract payload must contain one table definition.")
    if str(canonical["table"].get("table_id") or "") != str(draft.get("table_id") or ""):
        raise ValueError("Data Contract payload table_id must match the draft row.")
    canonical["table"]["processing"] = validated_processing(
        dict(canonical["table"].get("processing") or {})
    )

    runtime_context = {
        "config": config, "env": env, **dict(context or {}),
        "_fabricops_suppress_io_log": True,
    }
    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=runtime_context)
    updated = coerce_metadata_row_types(DATA_CONTRACT_TABLE, {
        **dict(draft),
        "contract_payload_json": json.dumps(
            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ),
        **audit,
    })
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - Fabric dependency
        raise RuntimeError("Delta Lake support is required to save a Data Contract draft.") from exc
    from fabricops_kit.io.shared import configured_lakehouse_schema, resolve_configured_lakehouse_table

    frame = spark_session.createDataFrame(
        [updated], schema=metadata_table_schema_registry()[DATA_CONTRACT_TABLE]
    )
    _, _, _, path = resolve_configured_lakehouse_table(
        store,
        DATA_CONTRACT_TABLE,
        metadata_table_physical_schema(config, DATA_CONTRACT_TABLE)
        if store == "Metadata" else schema or configured_lakehouse_schema(config, env, store),
        context=runtime_context,
    )
    (
        DeltaTable.forPath(spark_session, path)
        .alias("target")
        .merge(
            frame.alias("source"),
            "target.contract_id = source.contract_id "
            "AND target.contract_version = source.contract_version "
            "AND target.environment_name = source.environment_name",
        )
        .whenMatchedUpdateAll()
        .execute()
    )
    return updated

def _json_safe(value: Any) -> Any:
    """Convert Spark-compatible scalar values into JSON-compatible values."""
    return value.isoformat() if isinstance(value, (date, datetime)) else value


def _fields(row: Mapping[str, Any], names: tuple[str, ...]) -> dict[str, Any]:
    """Select canonical payload fields from one metadata row."""
    return {name: _json_safe(row.get(name)) for name in names}


def validate_contract_identity(contract_id: Any, contract_version: Any) -> tuple[str, int]:
    """Validate and normalize an exact Data Contract version identity."""
    identity = str(contract_id or "").strip()
    try:
        version = int(contract_version or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("contract_version must be a positive integer.") from exc
    if not identity or version < 1:
        raise ValueError("contract_id and a positive contract_version are required.")
    return identity, version


def normalize_guardrail_action(value: Any) -> str:
    """Return the canonical user-facing Guardrail action."""
    action = str(value or "Warn").strip().casefold()
    aliases = {"warn": "Warn", "warning": "Warn", "block": "Block", "blocking": "Block", "error": "Block"}
    try:
        return aliases[action]
    except KeyError as exc:
        raise ValueError("Guardrail action must be Warn or Block.") from exc


def validate_sensitive_data_parameters(parameters: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalize one column-scoped Sensitive Data policy."""
    values = dict(parameters)
    if values.get("scope") != "column":
        raise ValueError("Sensitive Data Guardrails require scope='column'.")
    treatment = str(values.get("treatment") or "").strip().lower()
    if treatment not in SENSITIVE_DATA_TREATMENTS:
        raise ValueError("Sensitive Data treatment must be tokenize, mask, bucket, or remove.")
    normalized: dict[str, Any] = {"scope": "column", "treatment": treatment}
    pii_type = str(values.get("pii_type") or "").strip().lower()
    pii_reason = str(values.get("pii_reason") or "").strip()
    if pii_type:
        if pii_type not in {"direct", "indirect"}:
            raise ValueError("Sensitive Data pii_type must be direct or indirect.")
        if not pii_reason:
            raise ValueError("Sensitive Data pii_reason is required when pii_type is provided.")
        normalized.update({"pii_type": pii_type, "pii_reason": pii_reason})
    elif pii_reason:
        raise ValueError("Sensitive Data pii_type is required when pii_reason is provided.")
    if treatment == "mask":
        for name in ("preserve_start", "preserve_end"):
            value = values.get(name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"Sensitive Data mask {name} must be an integer >= 0.")
            normalized[name] = value
        mask_character = str(values.get("mask_character") or "")
        if not mask_character:
            raise ValueError("Sensitive Data mask_character must be non-empty.")
        normalized["mask_character"] = mask_character
    elif treatment == "bucket":
        bins = values.get("bins")
        labels = values.get("labels")
        if not isinstance(bins, list) or not bins:
            raise ValueError("Sensitive Data bucket bins must be a non-empty list.")
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            for value in bins
        ):
            raise ValueError("Sensitive Data bucket bins must contain only finite numbers.")
        numeric_bins = [float(value) for value in bins]
        if any(left >= right for left, right in zip(numeric_bins, numeric_bins[1:])):
            raise ValueError("Sensitive Data bucket bins must be strictly increasing.")
        if not isinstance(labels, list) or len(labels) != len(numeric_bins):
            raise ValueError("Sensitive Data bucket labels count must match bins count.")
        normalized_labels = [str(label).strip() for label in labels]
        if any(not label for label in normalized_labels):
            raise ValueError("Sensitive Data bucket labels must be non-empty.")
        normalized.update({"bins": numeric_bins, "labels": normalized_labels})
    return normalized


def canonical_guardrail_rule_record(record: Mapping[str, Any], *, config: Any, env: str) -> dict[str, Any]:
    """Build one canonical, exact-contract-version Guardrail authoring row."""
    import json

    audit = build_runtime_audit_fields(config=config, env=env)
    contract_id, contract_version = validate_contract_identity(
        record.get("contract_id"), record.get("contract_version")
    )
    guardrail_type = str(record.get("guardrail_type") or "").strip().casefold().replace(" ", "_")
    if guardrail_type not in GUARDRAIL_TYPES:
        raise ValueError(
            "guardrail_type must be Schema, Freshness, Source Drift, Data Quality, or Sensitive Data."
        )
    raw_parameters = record.get("rule_parameters_json") or "{}"
    try:
        parameters = json.loads(raw_parameters) if isinstance(raw_parameters, str) else dict(raw_parameters)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("rule_parameters_json must contain a JSON object.") from exc
    if not isinstance(parameters, dict):
        raise ValueError("rule_parameters_json must contain a JSON object.")
    column_id = str(record.get("column_id") or "").strip()
    if guardrail_type == "sensitive_data":
        if not column_id:
            raise ValueError("Sensitive Data Guardrails require a canonical column_id.")
        parameters = validate_sensitive_data_parameters(parameters)
    return {
        "guardrail_rule_id": str(record.get("guardrail_rule_id") or "").strip(),
        "guardrail_version": int(record.get("guardrail_version") or 1),
        "contract_id": contract_id,
        "contract_version": contract_version,
        "column_id": column_id,
        "environment_name": str(record.get("environment_name") or env),
        "guardrail_type": guardrail_type,
        "rule_id": str(record.get("rule_id") or "").strip(),
        "rule_type": str(record.get("rule_type") or "").strip(),
        "rule_parameters_json": json.dumps(parameters, default=str, sort_keys=True, separators=(",", ":")),
        "action": normalize_guardrail_action(record.get("action")),
        "is_active": bool(record.get("is_active", True)),
        **audit,
    }



def contract_version_records(
    rows: Any,
    *,
    contract_id: str,
    contract_version: int,
    environment_name: str,
) -> list[dict[str, Any]]:
    """Return rows owned by exactly one contract version and environment."""
    identity, version = validate_contract_identity(contract_id, contract_version)
    env = str(environment_name or "").strip()
    if not env:
        raise ValueError("environment_name is required for contract authoring.")
    return [
        row for row in row_dicts(rows)
        if str(row.get("contract_id") or "") == identity
        and int(row.get("contract_version") or 0) == version
        and str(row.get("environment_name") or "") == env
    ]


def read_contract_records(
    table_name: str,
    *,
    config: Any,
    env: str,
    spark_session: Any,
    contract_id: str,
    contract_version: int,
) -> list[dict[str, Any]]:
    """Read exact-version governance records through the configured metadata target."""
    identity, version = validate_contract_identity(contract_id, contract_version)
    frame = read_lakehouse_table(
        table_name,
        store="Metadata",
        schema=metadata_table_physical_schema(config, table_name),
        context=_metadata_io_context(config, env),
        spark_session=spark_session,
    )
    return contract_version_records(
        _scoped_rows(
            frame,
            f"contract_id = {_sql_literal(identity)}",
            f"contract_version = {version}",
            f"environment_name = {_sql_literal(env)}",
        ),
        contract_id=identity,
        contract_version=version,
        environment_name=env,
    )


def read_all_enrichment(*, config: Any, env: str, spark_session: Any) -> list[dict[str, Any]]:
    """Read all Enrichment rows in one configured authoring environment."""
    try:
        frame = read_lakehouse_table(
            ENRICHMENT_TABLE, store="Metadata",
            schema=metadata_table_physical_schema(config, ENRICHMENT_TABLE),
            context=_metadata_io_context(config, env), spark_session=spark_session,
        )
    except Exception as exc:
        message = str(exc).lower()
        if any(marker in message for marker in ("not found", "does not exist", "path does not exist")):
            return []
        raise
    return canonical_enrichment_state(
        row for row in row_dicts(frame)
        if str(row.get("environment_name") or "") == str(env)
    )


def canonical_enrichment_state(rows: Any) -> list[dict[str, Any]]:
    """Return only descriptive Enrichment rows supported by the canonical model."""
    canonical = []
    for row in row_dicts(rows):
        allowed = ENRICHMENT_TYPES_BY_LEVEL.get(
            str(row.get("enrichment_level") or "").lower(), frozenset()
        )
        enrichment_type = next((
            name for name in allowed
            if name.casefold() == str(row.get("enrichment_type") or "").casefold()
        ), None)
        if enrichment_type is not None:
            canonical.append({**row, "enrichment_type": enrichment_type})
    return canonical




def get_contract_authoring_state(
    *,
    config: Any,
    env: str,
    spark_session: Any,
    contract_id: str,
    contract_version: int,
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Load one exact Data Contract version for editing or review."""
    identity, version = validate_contract_identity(contract_id, contract_version)
    context = _metadata_io_context(config, env)
    if contract is None:
        contract_frame = read_lakehouse_table(
            DATA_CONTRACT_TABLE, store="Metadata",
            schema=metadata_table_physical_schema(config, DATA_CONTRACT_TABLE),
            context=context, spark_session=spark_session,
        )
        matches = contract_version_records(
            _scoped_rows(
                contract_frame,
                f"contract_id = {_sql_literal(identity)}",
                f"contract_version = {version}",
                f"environment_name = {_sql_literal(env)}",
            ),
            contract_id=identity,
            contract_version=version,
            environment_name=env,
        )
        if not matches:
            raise ValueError("The exact Data Contract version does not exist.")
        draft = matches[0]
    else:
        matches = contract_version_records(
            [contract],
            contract_id=identity,
            contract_version=version,
            environment_name=env,
        )
        if not matches:
            raise ValueError("The supplied Data Contract row does not match the requested version.")
        draft = matches[0]

    table_id = str(draft.get("table_id") or "")
    catalogue_frame = read_lakehouse_table(
        "METADATA_DATA_CATALOGUE", store="Metadata",
        schema=metadata_table_physical_schema(config, "METADATA_DATA_CATALOGUE"),
        context=context, spark_session=spark_session,
    )
    catalogue_rows = _scoped_rows(
        catalogue_frame,
        f"table_id = {_sql_literal(table_id)}",
        f"environment_name = {_sql_literal(env)}",
    )
    payload = _json_value(
        draft.get("contract_payload_json"), field="contract_payload_json", default=None
    )
    if not isinstance(payload, dict):
        raise ValueError("Data Contract version has no valid canonical payload.")
    enrichment_rows, guardrail_rows = _payload_authoring_rows(
        payload,
        contract_id=identity,
        contract_version=version,
        environment_name=env,
    )
    state = {
        "contract": dict(draft),
        "contract_id": identity,
        "contract_version": version,
        "table_id": table_id,
        "environment_name": env,
        "catalogue_rows": [
            row for row in row_dicts(catalogue_rows)
            if str(row.get("environment_name") or "") == env
            and str(row.get("table_id") or "") == table_id
        ],
        "enrichment": canonical_enrichment_state(enrichment_rows),
        "guardrails": guardrail_rows,
        "payload": payload,
    }
    state["available_columns"] = [
        dict(row) for row in state["catalogue_rows"]
        if str(row.get("metadata_level") or "").lower() == "column"
        and row.get("is_active") is not False
    ]
    return state

def list_contract_governance_state(
    *, config: Any, env: str, spark_session: Any
) -> dict[str, list[dict[str, Any]]]:
    """Return governed tables and Data Contract versions for the authoring selector."""
    context = _metadata_io_context(config, env)
    catalogue = _scoped_rows(
        read_lakehouse_table(
            "METADATA_DATA_CATALOGUE", store="Metadata",
            schema=metadata_table_physical_schema(config, "METADATA_DATA_CATALOGUE"),
            context=context, spark_session=spark_session,
        ),
        f"environment_name = {_sql_literal(env)}",
    )
    contracts = _scoped_rows(
        read_lakehouse_table(
            DATA_CONTRACT_TABLE, store="Metadata",
            schema=metadata_table_physical_schema(config, DATA_CONTRACT_TABLE),
            context=context, spark_session=spark_session,
        ),
        f"environment_name = {_sql_literal(env)}",
    )
    tables = _latest([
        row for row in catalogue
        if str(row.get("environment_name") or "") == env
        and (str(row.get("metadata_level") or "").lower() == "table" or not row.get("column_id"))
        and row.get("is_active") is not False
    ], ("table_id",))
    versions = sorted(
        [row for row in contracts if str(row.get("environment_name") or "") == env],
        key=lambda row: (str(row.get("table_id") or ""), -int(row.get("contract_version") or 0)),
    )
    return {"tables": tables, "contracts": versions}


def get_contract_review_state(
    *, config: Any, env: str, spark_session: Any, contract_id: str, contract_version: int
) -> dict[str, Any]:
    """Load an exact draft or immutable Data Contract version for governance review."""
    identity, version = validate_contract_identity(contract_id, contract_version)
    rows = _scoped_rows(
        read_lakehouse_table(
            DATA_CONTRACT_TABLE, store="Metadata",
            schema=metadata_table_physical_schema(config, DATA_CONTRACT_TABLE),
            context=_metadata_io_context(config, env), spark_session=spark_session,
        ),
        f"contract_id = {_sql_literal(identity)}",
        f"contract_version = {version}",
        f"environment_name = {_sql_literal(env)}",
    )
    matches = contract_version_records(
        rows,
        contract_id=identity,
        contract_version=version,
        environment_name=env,
    )
    if not matches:
        raise ValueError("The exact Data Contract version does not exist.")
    contract = matches[0]
    if str(contract.get("status") or "").lower() == "draft":
        return get_contract_authoring_state(
            config=config, env=env, spark_session=spark_session,
            contract_id=identity, contract_version=version, contract=contract,
        )
    payload = _json_value(contract.get("contract_payload_json"), field="contract_payload_json", default=None)
    if not isinstance(payload, dict):
        raise ValueError("Immutable Data Contract version has no valid canonical payload.")
    return {
        "contract": contract, "contract_id": identity, "contract_version": version,
        "table_id": str(contract.get("table_id") or ""), "environment_name": env,
        "payload": payload, "catalogue_rows": [], "available_columns": payload.get("table", {}).get("columns", []),
        "enrichment": [*payload.get("enrichment", {}).get("table", []), *payload.get("enrichment", {}).get("columns", [])],
        "guardrails": payload.get("guardrails", []),
    }


def build_contract_manifest(
    *, draft: Mapping[str, Any], config: Any, env: str, spark_session: Any,
    scheduled_refresh: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """Build the exact canonical payload used by :func:`freeze_contract` without persisting it."""
    tables = {
        name: row_dicts(read_lakehouse_table(
            name, store="Metadata", schema=metadata_table_physical_schema(config, name),
            spark_session=spark_session, context=_metadata_io_context(config, env),
        )) for name in CONTRACT_SOURCE_TABLES
    }
    validate_contract_draft(
        draft, catalogue_rows=tables["METADATA_DATA_CATALOGUE"],
        enrichment_rows=tables[ENRICHMENT_TABLE], guardrail_rows=tables[GUARDRAIL_TABLE],
        environment_name=env,
    )
    return assemble_contract_payload(
        draft=draft, tables=tables, environment_name=env,
        scheduled_refresh=scheduled_refresh,
    )


def get_column_profile_context(
    *, config: Any, env: str, spark_session: Any, table_id: str, column_id: str
) -> dict[str, Any]:
    """Return top frequency values or a range from the latest completed profile snapshot."""
    context = _metadata_io_context(config, env)
    profiled = _scoped_rows(
        read_lakehouse_table(
            "METADATA_DATA_PROFILED", store="Metadata",
            schema=metadata_table_physical_schema(config, "METADATA_DATA_PROFILED"),
            context=context, spark_session=spark_session,
        ),
        f"table_id = {_sql_literal(table_id)}",
        f"column_id = {_sql_literal(column_id)}",
        f"environment_name = {_sql_literal(env)}",
    )
    candidates = [row for row in profiled
                  if str(row.get("table_id") or "") == str(table_id)
                  and str(row.get("column_id") or "") == str(column_id)
                  and str(row.get("environment_name") or env) == env
                  and str(row.get("status") or "completed").lower() == "completed"]
    if not candidates:
        return {"kind": "unavailable", "message": "No profile values available."}
    latest = max(candidates, key=lambda row: str(row.get("profiled_at") or row.get("_committed_at") or ""))
    snapshot = latest.get("profile_id") or latest.get("profile_snapshot_id")
    try:
        frequency_filters = []
        if snapshot is not None:
            frequency_filters.append(f"profile_id = {_sql_literal(snapshot)}")
        frequency = _scoped_rows(
            read_lakehouse_table(
                "METADATA_DATA_PROFILED_FREQUENCY", store="Metadata",
                schema=metadata_table_physical_schema(config, "METADATA_DATA_PROFILED_FREQUENCY"),
                context=context, spark_session=spark_session,
            ),
            *frequency_filters,
        )
    except Exception as exc:
        if not any(marker in str(exc).lower() for marker in ("not found", "does not exist", "path does not exist")):
            raise
        frequency = []
    values = [row for row in frequency
              if snapshot is None
              or row.get("profile_id") == snapshot
              or row.get("profile_snapshot_id") == snapshot]
    values.sort(key=lambda row: int(row.get("frequency") or row.get("count") or 0), reverse=True)
    if values:
        return {"kind": "values", "values": [
            {"value": row.get("value", row.get("observed_value")), "count": row.get("frequency", row.get("count"))}
            for row in values[:3]
        ], "profile": latest}
    if latest.get("min_value") is not None or latest.get("max_value") is not None:
        return {"kind": "range", "min": latest.get("min_value"), "max": latest.get("max_value"), "profile": latest}
    return {"kind": "unavailable", "message": "No profile values available.", "profile": latest}


def _contract_activation_changes(
    rows: list[dict[str, Any]], selected: dict[str, Any], *, agreement_id: str, agreement_version: str
) -> list[dict[str, Any]]:
    """Build activation-tag updates without changing frozen lifecycle status."""
    changes = [
        {
            "contract_id": row["contract_id"],
            "contract_version": int(row["contract_version"]),
            "is_active": False,
        }
        for row in rows
        if str(row.get("table_id") or "") == str(selected.get("table_id") or "")
        and row.get("is_active") is True
        and (str(row.get("contract_id")), int(row.get("contract_version") or 0))
        != (str(selected.get("contract_id")), int(selected.get("contract_version") or 0))
    ]
    if selected.get("is_active") is not True:
        changes.append({
            "contract_id": selected["contract_id"],
            "contract_version": int(selected["contract_version"]),
            "is_active": True,
            "agreement_id": agreement_id,
            "agreement_version": agreement_version,
        })
    return changes


def activate_contract_version(
    *, config: Any, env: str, table_id: str, contract_id: str, contract_version: int,
    agreement_id: str, agreement_version: str, store: str = "Metadata",
    schema: str | None = None, spark_session: Any = None, context: Any = None,
) -> dict[str, Any]:
    """Tag one frozen contract version as the active Production definition."""
    from fabricops_kit.io.shared import configured_lakehouse_schema, resolve_configured_lakehouse_table

    agreement_id, agreement_version = str(agreement_id or "").strip(), str(agreement_version or "").strip()
    if not agreement_id or not agreement_version:
        raise ValueError("Select an exact Data Agreement version before activation.")
    rows = row_dicts(read_lakehouse_table(
        DATA_CONTRACT_TABLE, store=store, schema=schema, spark_session=spark_session, context=context,
    ))
    selected = [
        row for row in rows
        if str(row.get("contract_id") or "") == contract_id
        and int(row.get("contract_version") or 0) == int(contract_version)
    ]
    if not selected:
        raise ValueError("Selected Data Contract version does not exist.")
    row = selected[0]
    if str(row.get("table_id") or "") != table_id:
        raise ValueError("Selected Data Contract version does not belong to the selected table_id.")
    if str(row.get("status") or "").lower() != "frozen":
        raise ValueError("Only a frozen Data Contract version can be activated.")
    payload = _json_value(row.get("contract_payload_json"), field="contract_payload_json", default=None)
    if not isinstance(payload, dict) or payload.get("contract", {}).get("contract_id") != contract_id:
        raise ValueError("Selected Data Contract payload identity is invalid.")
    current = (str(row.get("agreement_id") or ""), str(row.get("agreement_version") or ""))
    if row.get("is_active") is True and current != (agreement_id, agreement_version):
        raise ValueError("An active Data Contract cannot be relinked to a different Data Agreement.")
    agreements = row_dicts(read_lakehouse_table(
        "METADATA_DATA_AGREEMENT", store=store,
        schema=metadata_table_physical_schema(config, "METADATA_DATA_AGREEMENT"),
        spark_session=spark_session, context=context,
    ))
    if not any(
        str(item.get("agreement_id") or "") == agreement_id
        and str(item.get("agreement_version") or "") == agreement_version
        for item in agreements
    ):
        raise ValueError("Selected Data Agreement version does not exist.")
    if len([item for item in rows if item.get("table_id") == table_id and item.get("is_active") is True]) > 1:
        raise RuntimeError(f"Data Contract integrity error: {table_id!r} has multiple active versions.")
    changes = _contract_activation_changes(
        rows, row, agreement_id=agreement_id, agreement_version=agreement_version
    )
    if not changes:
        return {
            "changed": False,
            "contract_id": contract_id,
            "contract_version": int(contract_version),
            "changes": [],
        }
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - Fabric dependency
        raise RuntimeError("Delta Lake support is required to activate a Data Contract.") from exc
    source = spark_session.createDataFrame(changes)
    _, _, _, path = resolve_configured_lakehouse_table(
        store, DATA_CONTRACT_TABLE,
        metadata_table_physical_schema(config, DATA_CONTRACT_TABLE)
        if store == "Metadata" else schema or configured_lakehouse_schema(config, env, store),
        context=context,
    )
    (
        DeltaTable.forPath(spark_session, path)
        .alias("target")
        .merge(
            source.alias("source"),
            "target.contract_id = source.contract_id "
            "AND target.contract_version = source.contract_version",
        )
        .whenMatchedUpdate(
            set={
                "is_active": "source.is_active",
                "agreement_id": "coalesce(source.agreement_id, target.agreement_id)",
                "agreement_version": "coalesce(source.agreement_version, target.agreement_version)",
            }
        )
        .execute()
    )
    return {
        "changed": True,
        "contract_id": contract_id,
        "contract_version": int(contract_version),
        "changes": changes,
    }


def build_enrichment_records(
    records: Iterable[Mapping[str, Any]], *, config: Any = None, env: str
) -> list[dict[str, Any]]:
    """Build canonical exact-version Enrichment rows, omitting blank values."""
    import uuid

    audit = build_runtime_audit_fields(config=config, env=env)
    built = []
    for raw_value in records:
        raw = dict(raw_value)
        level = str(raw.get("enrichment_level") or "").strip().lower()
        if level not in {"table", "column"}:
            raise ValueError("enrichment_level must be 'table' or 'column'.")
        contract_id, contract_version = validate_contract_identity(raw.get("contract_id"), raw.get("contract_version"))
        row_env = str(raw.get("environment_name") or env).strip()
        if row_env != str(env):
            raise ValueError("Enrichment environment_name must match the authoring environment.")
        column_id = str(raw.get("column_id") or "").strip()
        if level == "column" and not column_id:
            raise ValueError("Column enrichment rows require column_id.")
        enrichment_type = str(raw.get("enrichment_type") or "").strip()
        allowed_types = ENRICHMENT_TYPES_BY_LEVEL[level]
        canonical_type = next(
            (name for name in allowed_types if name.casefold() == enrichment_type.casefold()), None
        )
        if canonical_type is None:
            raise ValueError(
                f"{level.title()} enrichment_type must be one of: "
                + ", ".join(sorted(allowed_types))
                + ". Enrichment is descriptive metadata only."
            )
        value = str(raw.get("value") or "").strip()
        if not value:
            continue
        built.append({
            "enrichment_id": str(raw.get("enrichment_id") or uuid.uuid4()),
            "contract_id": contract_id, "contract_version": contract_version,
            "column_id": column_id if level == "column" else "",
            "environment_name": row_env, "enrichment_level": level,
            "enrichment_type": canonical_type, "value": value,
            **{name: raw.get(name, default) for name, default in audit.items()},
        })
    return built


def save_enrichment(records: list[dict[str, Any]], *, config: Any, env: str, spark_session: Any) -> list[dict[str, Any]]:
    """Validate and append Enrichment through the configured metadata target."""
    canonical = build_enrichment_records(records, config=config, env=env)
    if canonical:
        write_lakehouse_table(
            spark_session.createDataFrame(
                [coerce_metadata_row_types(ENRICHMENT_TABLE, row) for row in canonical],
                schema=metadata_table_schema_registry()[ENRICHMENT_TABLE],
            ), ENRICHMENT_TABLE, store="Metadata",
            schema=metadata_table_physical_schema(config, ENRICHMENT_TABLE),
            context=_metadata_io_context(config, env), mode="append",
        )
    return canonical



def save_guardrails(records: list[dict[str, Any]], *, config: Any, env: str, spark_session: Any) -> list[dict[str, Any]]:
    """Validate and append exact-version Guardrail records."""
    canonical = [canonical_guardrail_rule_record(row, config=config, env=env) for row in records]
    for row in canonical:
        validate_contract_identity(row.get("contract_id"), row.get("contract_version"))
        if str(row.get("environment_name") or "") != str(env):
            raise ValueError("Guardrail environment_name must match the authoring environment.")
    if canonical:
        write_lakehouse_table(
            spark_session.createDataFrame([coerce_metadata_row_types(GUARDRAIL_TABLE, row) for row in canonical]),
            GUARDRAIL_TABLE, store="Metadata",
            schema=metadata_table_physical_schema(config, GUARDRAIL_TABLE),
            context=_metadata_io_context(config, env), mode="append",
        )
    return canonical



def validate_contract_draft(
    draft: Mapping[str, Any], *, catalogue_rows: Any, enrichment_rows: Any, guardrail_rows: Any, environment_name: str
) -> dict[str, Any]:
    """Validate structural completeness and return exact-version authoring state."""
    contract_id, version = validate_contract_identity(draft.get("contract_id"), draft.get("contract_version"))
    draft_environment = str(draft.get("environment_name") or "").strip()
    if draft_environment != str(environment_name):
        raise ValueError(
            "The draft environment_name must match the contract authoring environment."
        )
    if str(draft.get("status") or "").lower() != "draft":
        raise ValueError("Only a draft Data Contract version can be authored or frozen.")
    table_id = str(draft.get("table_id") or "").strip()
    if not table_id:
        raise ValueError("A draft requires one governed table_id.")
    if draft.get("agreement_id") not in (None, "") or draft.get("agreement_version") not in (None, ""):
        raise ValueError("Draft Data Contracts cannot be linked to a Data Agreement before activation.")
    catalogue = [row for row in row_dicts(catalogue_rows) if str(row.get("environment_name") or "") == environment_name and str(row.get("table_id") or "") == table_id]
    if not any(str(row.get("metadata_level") or "").lower() == "table" for row in catalogue):
        raise ValueError("The draft table_id has no table-level Catalogue row in the authoring environment.")
    return {
        "contract": dict(draft), "contract_id": contract_id, "contract_version": version,
        "table_id": table_id, "environment_name": environment_name,
        "catalogue_rows": catalogue,
        "enrichment": canonical_enrichment_state(contract_version_records(
            enrichment_rows, contract_id=contract_id, contract_version=version,
            environment_name=environment_name,
        )),
        "guardrails": contract_version_records(guardrail_rows, contract_id=contract_id, contract_version=version, environment_name=environment_name),
    }


def freeze_contract_record(
    *, draft: Mapping[str, Any], audit: Mapping[str, Any]
) -> dict[str, Any]:
    """Freeze one saved draft without changing its governed definition."""
    validate_contract_identity(draft.get("contract_id"), draft.get("contract_version"))
    if str(draft.get("status") or "").lower() != "draft":
        raise ValueError("Only a draft Data Contract version can be frozen.")
    payload = _json_value(
        draft.get("contract_payload_json"), field="contract_payload_json", default=None
    )
    if not isinstance(payload, dict):
        raise ValueError("Save the Data Contract draft before freezing it.")
    payload = json.loads(json.dumps(payload))
    payload["contract"] = {
        "contract_id": str(draft["contract_id"]),
        "contract_version": int(draft["contract_version"]),
        "status": "frozen",
    }
    return {
        **dict(draft),
        "contract_payload_json": json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ),
        "status": "frozen",
        "is_active": False,
        **dict(audit),
    }

def assemble_contract_payload(
    *,
    draft: Mapping[str, Any],
    tables: Mapping[str, Any],
    environment_name: str,
    scheduled_refresh: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """Assemble the canonical immutable payload for one exact Data Contract draft."""
    contract_id, contract_version = validate_contract_identity(
        draft.get("contract_id"), draft.get("contract_version")
    )
    table_id = str(draft.get("table_id") or "")
    catalogue = [
        row for row in row_dicts(tables["METADATA_DATA_CATALOGUE"])
        if str(row.get("table_id") or "") == table_id
        and str(row.get("environment_name") or "") == environment_name
        and row.get("is_active") is not False
    ]
    current = _latest(catalogue, ("table_id", "column_id"))
    table_rows = [
        row for row in current
        if str(row.get("metadata_level") or "").lower() == "table" or not row.get("column_id")
    ]
    if not table_rows:
        raise ValueError("Select one valid active METADATA_DATA_CATALOGUE table_id.")
    table = table_rows[-1]
    columns = [row for row in current if row.get("column_id")]
    column_docs = [_fields(row, ("column_id", "column_name", "data_type")) for row in columns]
    incomplete = [
        str(row.get("column_name") or row.get("column_id") or "<blank>")
        for row in column_docs
        if any(not str(row.get(name) or "").strip() for name in ("column_id", "column_name", "data_type"))
    ]
    if incomplete:
        raise ValueError(
            "Active METADATA_DATA_CATALOGUE columns must define column_id, column_name, "
            "and data_type before a Data Contract can be assembled: " + ", ".join(incomplete)
        )
    column_names = [str(row["column_name"]).strip() for row in column_docs]
    duplicates = sorted({name for name in column_names if column_names.count(name) > 1})
    if duplicates:
        raise ValueError(
            "Active METADATA_DATA_CATALOGUE columns contain duplicate column_name values: "
            + ", ".join(duplicates)
        )

    def owned(row: Mapping[str, Any]) -> bool:
        return (
            str(row.get("contract_id") or "") == contract_id
            and int(row.get("contract_version") or 0) == contract_version
            and str(row.get("environment_name") or "") == environment_name
        )

    enrichment = _latest(
        canonical_enrichment_state(row for row in row_dicts(tables[ENRICHMENT_TABLE]) if owned(row)),
        ("enrichment_id",),
    )
    enrichment_docs = [
        _fields(row, ("enrichment_id", "contract_id", "contract_version", "column_id", "enrichment_level", "enrichment_type", "value"))
        for row in enrichment
    ]
    guardrails = _latest(
        [row for row in row_dicts(tables[GUARDRAIL_TABLE]) if owned(row)],
        ("guardrail_rule_id",),
    )
    guardrail_docs = []
    for row in guardrails:
        item = _fields(row, ("guardrail_rule_id", "guardrail_version", "contract_id", "contract_version", "column_id", "guardrail_type", "rule_id", "rule_type", "action", "severity"))
        item["is_active"] = bool(row.get("is_active", True))
        parameters = _json_value(row.get("rule_parameters_json"), field="rule_parameters_json", default={})
        if not isinstance(parameters, dict):
            raise ValueError("rule_parameters_json must contain a JSON object.")
        if str(row.get("guardrail_type") or "").strip().lower() == "schema":
            parameters = {
                name: value for name, value in parameters.items()
                if name not in {"columns", "data_types", "selected_columns", "expected_data_types"}
            }
        item["rule_parameters"] = parameters
        guardrail_docs.append(item)

    try:
        processing = contract_processing(draft)
    except ValueError as exc:
        raise ValueError(
            f"Data Contract processing for table_id {table_id!r} is incomplete or invalid: {exc}"
        ) from exc
    if not processing:
        raise ValueError("Data Contract draft must define a load strategy before it can be frozen.")
    payload = {
        "contract": {
            "contract_id": contract_id,
            "contract_version": contract_version,
            "status": str(draft.get("status") or "draft").lower(),
        },
        "table": {
            **_fields(table, ("table_id", "environment_name", "store_type", "layer", "schema_name", "table_name")),
            "columns": column_docs,
            "processing": processing,
            "processing_source": contract_processing_source(draft),
            **({"scheduled_refresh": canonical_scheduled_refresh(scheduled_refresh)} if scheduled_refresh is not None else {}),
            "writer": {
                "notebook_id": str(table.get("_notebook_id") or "").strip(),
                "notebook_name": str(table.get("_notebook_name") or "").strip(),
            },
        },
        "enrichment": {
            "table": [row for row in enrichment_docs if not row.get("column_id")],
            "columns": [row for row in enrichment_docs if row.get("column_id")],
        },
        "guardrails": guardrail_docs,
    }
    warnings = []
    if not any(row.get("enrichment_type") == "Description" and not row.get("column_id") for row in enrichment_docs):
        warnings.append("Table description is missing.")
    described = {str(row.get("column_id")) for row in enrichment_docs if row.get("enrichment_type") == "Description"}
    if any(str(row.get("column_id")) not in described for row in column_docs):
        warnings.append("One or more column descriptions are missing.")
    if not any(row.get("is_active", True) for row in guardrail_docs):
        warnings.append("No active Guardrails are configured.")
    return payload, warnings


def freeze_contract(
    *,
    draft: Mapping[str, Any],
    config: Any,
    env: str,
    spark_session: Any,
    context: Mapping[str, Any] | None = None,
    store: str = "Metadata",
    schema: str | None = None,
    scheduled_refresh: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Freeze one already-saved draft; its governed JSON becomes immutable."""
    from delta.tables import DeltaTable
    from fabricops_kit.io.shared import configured_lakehouse_schema, resolve_configured_lakehouse_table

    if str(draft.get("environment_name") or "") != str(env):
        raise ValueError("Draft environment_name must match the authoring environment.")
    payload = _json_value(
        draft.get("contract_payload_json"), field="contract_payload_json", default=None
    )
    if not isinstance(payload, dict):
        raise ValueError("Save the Data Contract draft before freezing it.")
    table = payload.get("table")
    if not isinstance(table, dict) or str(table.get("table_id") or "") != str(draft.get("table_id") or ""):
        raise ValueError("Saved Data Contract payload does not match the draft table_id.")
    validated_processing(dict(table.get("processing") or {}))

    runtime_context = {"config": config, "env": env, **dict(context or {})}
    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=runtime_context)
    frozen = coerce_metadata_row_types(
        DATA_CONTRACT_TABLE,
        freeze_contract_record(draft=draft, audit=audit),
    )
    frame = spark_session.createDataFrame(
        [frozen], schema=metadata_table_schema_registry()[DATA_CONTRACT_TABLE]
    )
    _, _, _, path = resolve_configured_lakehouse_table(
        store,
        DATA_CONTRACT_TABLE,
        (
            metadata_table_physical_schema(config, DATA_CONTRACT_TABLE)
            if store == "Metadata"
            else schema or configured_lakehouse_schema(config, env, store)
        ),
        context=runtime_context,
    )
    (
        DeltaTable.forPath(spark_session, path)
        .alias("target")
        .merge(
            frame.alias("source"),
            "target.contract_id = source.contract_id AND "
            "target.contract_version = source.contract_version",
        )
        .whenMatchedUpdateAll()
        .execute()
    )
    frozen_payload = _json_value(
        frozen.get("contract_payload_json"), field="contract_payload_json", default={}
    )
    return {"contract": frozen, "payload": frozen_payload, "warnings": []}

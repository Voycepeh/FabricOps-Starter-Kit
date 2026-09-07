"""UI-independent services for authoring versioned Data Contracts.

The functions in this module deliberately accept row-like Python/Spark values
and keep widget rendering concerns out of governance metadata semantics.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import (
    coerce_metadata_row_types,
    metadata_table_physical_schema,
    metadata_table_schema_registry,
)
from fabricops_kit.io.shared import read_lakehouse_table_core, write_lakehouse_table_core
from fabricops_kit.pipeline.shared import canonical_guardrail_rule_record

DATA_CONTRACT_TABLE = "METADATA_DATA_CONTRACT"
ENRICHMENT_TABLE = "METADATA_ENRICHMENT"
GUARDRAIL_TABLE = "METADATA_GUARDRAIL"


def row_dicts(value: Any) -> list[dict[str, Any]]:
    """Return a DataFrame or iterable of row-like values as dictionaries."""
    if value is None:
        return []
    source = value.collect() if hasattr(value, "collect") else value
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in source]


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


def select_contract_authoring_context(
    contract_rows: Any,
    *,
    environment_name: str,
    table_id: str,
) -> dict[str, Any]:
    """Select the latest exact draft contract for a table in one environment."""
    env = str(environment_name or "").strip()
    table = str(table_id or "").strip()
    if not env or not table:
        raise ValueError("environment_name and table_id are required for contract authoring.")
    drafts = [
        row for row in row_dicts(contract_rows)
        if str(row.get("table_id") or "") == table
        and str(row.get("status") or "").lower() == "draft"
        and str(row.get("environment_name") or env) == env
    ]
    if not drafts:
        raise ValueError(f"No draft Data Contract exists for table_id={table!r} in environment {env!r}.")
    selected = max(drafts, key=lambda row: int(row.get("contract_version") or 0))
    contract_id, contract_version = validate_contract_identity(
        selected.get("contract_id"), selected.get("contract_version")
    )
    return {**selected, "contract_id": contract_id, "contract_version": contract_version, "environment_name": env}


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
    frame = read_lakehouse_table_core(
        table_name,
        target="metadata",
        schema=metadata_table_physical_schema(config, table_name),
        context={"config": config, "env": env},
        spark_session=spark_session,
    )
    return contract_version_records(
        frame,
        contract_id=contract_id,
        contract_version=contract_version,
        environment_name=env,
    )


def read_all_enrichment(*, config: Any, env: str, spark_session: Any) -> list[dict[str, Any]]:
    """Read all Enrichment rows in one configured authoring environment."""
    try:
        frame = read_lakehouse_table_core(
            ENRICHMENT_TABLE, target="metadata",
            schema=metadata_table_physical_schema(config, ENRICHMENT_TABLE),
            context={"config": config, "env": env}, spark_session=spark_session,
        )
    except Exception as exc:
        message = str(exc).lower()
        if any(marker in message for marker in ("not found", "does not exist", "path does not exist")):
            return []
        raise
    return [row for row in row_dicts(frame) if str(row.get("environment_name") or "") == str(env)]


def read_enrichment(
    *, config: Any, env: str, spark_session: Any, contract_id: str, contract_version: int
) -> list[dict[str, Any]]:
    """Read Enrichment owned by one exact Data Contract version."""
    return read_contract_records(
        ENRICHMENT_TABLE, config=config, env=env, spark_session=spark_session,
        contract_id=contract_id, contract_version=contract_version,
    )


def read_guardrails(
    *, config: Any, env: str, spark_session: Any, contract_id: str, contract_version: int
) -> list[dict[str, Any]]:
    """Read Guardrails owned by one exact Data Contract version."""
    return read_contract_records(
        GUARDRAIL_TABLE, config=config, env=env, spark_session=spark_session,
        contract_id=contract_id, contract_version=contract_version,
    )


def get_contract_authoring_state(
    *,
    config: Any,
    env: str,
    spark_session: Any,
    contract_id: str,
    contract_version: int,
) -> dict[str, Any]:
    """Load the governance state needed by a contract editor without UI objects."""
    identity, version = validate_contract_identity(contract_id, contract_version)
    context = {"config": config, "env": env}
    tables = {}
    for table_name in (DATA_CONTRACT_TABLE, "METADATA_DATA_CATALOGUE", ENRICHMENT_TABLE, GUARDRAIL_TABLE):
        tables[table_name] = row_dicts(read_lakehouse_table_core(
            table_name, target="metadata",
            schema=metadata_table_physical_schema(config, table_name),
            context=context, spark_session=spark_session,
        ))
    matches = [
        row for row in tables[DATA_CONTRACT_TABLE]
        if str(row.get("contract_id") or "") == identity
        and int(row.get("contract_version") or 0) == version
        and str(row.get("environment_name") or "") == str(env)
    ]
    if not matches:
        raise ValueError("The exact Data Contract version does not exist.")
    draft = matches[0]
    state = validate_contract_draft(
        draft, catalogue_rows=tables["METADATA_DATA_CATALOGUE"],
        enrichment_rows=tables[ENRICHMENT_TABLE], guardrail_rows=tables[GUARDRAIL_TABLE],
        environment_name=env,
    )
    state["available_columns"] = [
        dict(row) for row in state["catalogue_rows"]
        if str(row.get("metadata_level") or "").lower() == "column" and row.get("is_active") is not False
    ]
    return state


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
        if not enrichment_type:
            raise ValueError("Enrichment rows require enrichment_type.")
        value = str(raw.get("value") or "").strip()
        if not value:
            continue
        built.append({
            "enrichment_id": str(raw.get("enrichment_id") or uuid.uuid4()),
            "contract_id": contract_id, "contract_version": contract_version,
            "column_id": column_id if level == "column" else "",
            "environment_name": row_env, "enrichment_level": level,
            "enrichment_type": enrichment_type, "value": value,
            **{name: raw.get(name, default) for name, default in audit.items()},
        })
    return built


def save_enrichment(records: list[dict[str, Any]], *, config: Any, env: str, spark_session: Any) -> list[dict[str, Any]]:
    """Validate and append Enrichment through the configured metadata target."""
    canonical = build_enrichment_records(records, config=config, env=env)
    if canonical:
        write_lakehouse_table_core(
            spark_session.createDataFrame(
                [coerce_metadata_row_types(ENRICHMENT_TABLE, row) for row in canonical],
                schema=metadata_table_schema_registry()[ENRICHMENT_TABLE],
            ), ENRICHMENT_TABLE, target="metadata",
            schema=metadata_table_physical_schema(config, ENRICHMENT_TABLE),
            context={"config": config, "env": env}, mode="append",
        )
    return canonical


def delete_enrichment(*_args: Any, **_kwargs: Any) -> None:
    """Reject deletion because Enrichment currently has no tombstone semantics."""
    raise NotImplementedError("METADATA_ENRICHMENT deletion is not part of the current append-only contract.")


def save_guardrails(records: list[dict[str, Any]], *, config: Any, env: str, spark_session: Any) -> list[dict[str, Any]]:
    """Validate and append exact-version Guardrail records."""
    canonical = [canonical_guardrail_rule_record(row, config=config, env=env) for row in records]
    for row in canonical:
        validate_contract_identity(row.get("contract_id"), row.get("contract_version"))
        if str(row.get("environment_name") or "") != str(env):
            raise ValueError("Guardrail environment_name must match the authoring environment.")
    if canonical:
        write_lakehouse_table_core(
            spark_session.createDataFrame([coerce_metadata_row_types(GUARDRAIL_TABLE, row) for row in canonical]),
            GUARDRAIL_TABLE, target="metadata",
            schema=metadata_table_physical_schema(config, GUARDRAIL_TABLE),
            context={"config": config, "env": env}, mode="append",
        )
    return canonical


def delete_guardrail(record: Mapping[str, Any], *, config: Any, env: str, spark_session: Any) -> dict[str, Any]:
    """Append an inactive next version for one existing logical Guardrail."""
    prior = dict(record)
    validate_contract_identity(prior.get("contract_id"), prior.get("contract_version"))
    prior["guardrail_version"] = int(prior.get("guardrail_version") or 0) + 1
    prior["is_active"] = False
    return save_guardrails([prior], config=config, env=env, spark_session=spark_session)[0]


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
    agreement_id = str(draft.get("agreement_id") or "").strip()
    agreement_version = str(draft.get("agreement_version") or "").strip()
    if not table_id or not agreement_id or not agreement_version:
        raise ValueError("A draft requires table_id and an exact Data Agreement identity.")
    catalogue = [row for row in row_dicts(catalogue_rows) if str(row.get("environment_name") or "") == environment_name and str(row.get("table_id") or "") == table_id]
    if not any(str(row.get("metadata_level") or "").lower() == "table" for row in catalogue):
        raise ValueError("The draft table_id has no table-level Catalogue row in the authoring environment.")
    return {
        "contract": dict(draft), "contract_id": contract_id, "contract_version": version,
        "table_id": table_id, "environment_name": environment_name,
        "catalogue_rows": catalogue,
        "enrichment": contract_version_records(enrichment_rows, contract_id=contract_id, contract_version=version, environment_name=environment_name),
        "guardrails": contract_version_records(guardrail_rows, contract_id=contract_id, contract_version=version, environment_name=environment_name),
    }


def freeze_contract_record(*, draft: Mapping[str, Any], payload: Mapping[str, Any], audit: Mapping[str, Any]) -> dict[str, Any]:
    """Build the immutable lifecycle update for one exact draft version."""
    import json

    validate_contract_identity(draft.get("contract_id"), draft.get("contract_version"))
    if str(draft.get("status") or "").lower() != "draft":
        raise ValueError("Only a draft Data Contract version can be frozen.")
    if draft.get("contract_payload_json") not in (None, ""):
        raise ValueError("Draft Data Contract version already has a canonical payload.")
    return {**dict(draft), "contract_payload_json": json.dumps(dict(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=False), "status": "frozen", "is_active": False, **dict(audit)}

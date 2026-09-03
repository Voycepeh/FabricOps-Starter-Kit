"""Shared Direct PII classification and protected token-vault helpers."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping
from uuid import uuid4

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.shared import get_store, is_table_not_found_error
from fabricops_kit.io.shared import (
    configured_lakehouse_schema,
    read_lakehouse_table_core,
    write_lakehouse_table_core,
)
from fabricops_kit.pipeline.shared import resolve_active_data_contract

ENRICHMENT_TABLE = "METADATA_ENRICHMENT"
TOKEN_VAULT_TARGET = "pii_token_vault"
TOKEN_VERSION = 1
TOKEN_PREFIX = f"fo_pii_v{TOKEN_VERSION}_"


def _row_dict(row: Any) -> dict[str, Any]:
    """Return a Spark Row or mapping as a plain dictionary."""
    return row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)


def _latest_direct_pii(rows: list[dict[str, Any]], table_id: str, env: str) -> set[str]:
    """Return column identities whose latest authored classification is Direct PII."""
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        if (
            str(row.get("table_id") or "") != table_id
            or str(row.get("environment_name") or "") != env
            or str(row.get("enrichment_level") or "").lower() != "column"
            or str(row.get("enrichment_type") or "").lower() != "personal_identifier"
        ):
            continue
        column_id = str(row.get("column_id") or "").strip()
        if not column_id:
            continue
        key = (
            str(row.get("_committed_at") or ""),
            str(row.get("enrichment_id") or ""),
        )
        previous = latest.get(column_id)
        previous_key = (
            str((previous or {}).get("_committed_at") or ""),
            str((previous or {}).get("enrichment_id") or ""),
        )
        if previous is None or key > previous_key:
            latest[column_id] = row
    return {
        column_id
        for column_id, row in latest.items()
        if str(row.get("value") or "").strip().lower() == "direct pii"
    }


def resolve_direct_pii_columns(
    config: Any,
    env: str,
    table_id: str,
    *,
    spark_session: Any,
    context: Mapping[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Resolve Direct PII column identities and names from authoring or a frozen contract."""
    if env == "prod":
        contract = resolve_active_data_contract(
            config, env, table_id, spark_session=spark_session, required=True,
        )
        payload = (contract or {}).get("contract_payload") or {}
        enrichment = payload.get("enrichment") or {}
        rows = list(enrichment.get("columns") or [])
        direct_ids = {
            str(row.get("column_id") or "")
            for row in rows
            if str(row.get("enrichment_type") or "").lower() == "personal_identifier"
            and str(row.get("value") or "").strip().lower() == "direct pii"
        }
        columns = ((payload.get("table") or {}).get("columns") or [])
    else:
        try:
            enrichment_frame = read_lakehouse_table_core(
                ENRICHMENT_TABLE,
                target="metadata",
                schema=configured_lakehouse_schema(config, env, "metadata"),
                spark_session=spark_session,
                context=context or {"config": config, "env": env},
            )
            rows = [_row_dict(row) for row in enrichment_frame.collect()]
        except Exception as exc:
            if not is_table_not_found_error(exc):
                raise
            rows = []
        direct_ids = _latest_direct_pii(rows, table_id, env)
        catalogue_frame = read_lakehouse_table_core(
            "METADATA_DATA_CATALOGUE",
            target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            spark_session=spark_session,
            context=context or {"config": config, "env": env},
        )
        columns = [_row_dict(row) for row in catalogue_frame.collect()]
    resolved = []
    for raw in columns:
        row = _row_dict(raw)
        column_id = str(row.get("column_id") or "").strip()
        column_name = str(row.get("column_name") or "").strip()
        if column_id in direct_ids and column_name and (
            env == "prod"
            or (
                str(row.get("table_id") or "") == table_id
                and str(row.get("environment_name") or "") == env
                and row.get("is_active") is not False
            )
        ):
            resolved.append({"column_id": column_id, "column_name": column_name})
    return sorted(resolved, key=lambda item: (item["column_name"], item["column_id"]))


def token_vault_table_name(table_id: str) -> str:
    """Return an opaque, table-scoped vault table name."""
    digest = hashlib.sha256(table_id.encode("utf-8")).hexdigest()[:24]
    return f"PII_TOKEN_VAULT_{digest}"


def load_token_vault_rows(
    config: Any,
    env: str,
    table_id: str,
    *,
    spark_session: Any,
    context: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Load mappings from the separately configured, table-isolated protected vault."""
    store = get_store(config, env, TOKEN_VAULT_TARGET)
    if str(store.kind).lower() != "lakehouse":
        raise ValueError("The pii_token_vault target must be a separately permissioned Lakehouse.")
    try:
        frame = read_lakehouse_table_core(
            token_vault_table_name(table_id),
            target=TOKEN_VAULT_TARGET,
            schema=configured_lakehouse_schema(config, env, TOKEN_VAULT_TARGET),
            spark_session=spark_session,
            context=context or {"config": config, "env": env},
        )
    except Exception as exc:
        if is_table_not_found_error(exc):
            return []
        raise
    rows = [_row_dict(row) for row in frame.collect()]
    invalid = [row for row in rows if str(row.get("table_id") or "") != table_id]
    if invalid:
        raise RuntimeError("PII token-vault integrity error: a table-scoped vault contains another table_id.")
    return rows


def tokenise_direct_pii(
    dataframe: Any,
    *,
    config: Any,
    env: str,
    table_id: str,
    columns: list[dict[str, str]],
    spark_session: Any,
    context: Mapping[str, Any] | None = None,
) -> Any:
    """Replace Direct PII with opaque vault-backed tokens and persist new unique mappings."""
    if not columns:
        return dataframe
    from pyspark.sql import functions as F

    existing = load_token_vault_rows(
        config, env, table_id, spark_session=spark_session, context=context,
    )
    by_original = {
        (str(row.get("column_id") or ""), str(row.get("original_value"))): str(row.get("token") or "")
        for row in existing
        if row.get("original_value") is not None and str(row.get("token") or "")
    }
    approved_tokens = {
        (str(row.get("column_id") or ""), str(row.get("token") or ""))
        for row in existing
        if str(row.get("token") or "")
    }
    new_rows: list[dict[str, Any]] = []
    prepared = dataframe
    for column in columns:
        name = column["column_name"]
        column_id = column["column_id"]
        if name not in prepared.columns:
            continue
        values = [row[0] for row in prepared.select(name).where(F.col(name).isNotNull()).distinct().collect()]
        replacements: dict[str, str] = {}
        for value in values:
            original = str(value)
            if (column_id, original) in approved_tokens:
                continue
            token = by_original.get((column_id, original))
            if not token:
                token = TOKEN_PREFIX + uuid4().hex
                by_original[(column_id, original)] = token
                new_rows.append({
                    "table_id": table_id,
                    "column_id": column_id,
                    "token": token,
                    "original_value": original,
                    "token_version": TOKEN_VERSION,
                    **build_runtime_audit_fields(config=config, env=env),
                })
            replacements[original] = token
        if replacements:
            mapping = F.create_map(*[
                item
                for original, token in replacements.items()
                for item in (F.lit(original), F.lit(token))
            ])
            prepared = prepared.withColumn(
                name,
                F.when(F.col(name).isNull(), F.lit(None))
                .when(mapping[F.col(name).cast("string")].isNotNull(), mapping[F.col(name).cast("string")])
                .otherwise(F.col(name)),
            )
    if new_rows:
        write_lakehouse_table_core(
            spark_session.createDataFrame(new_rows),
            token_vault_table_name(table_id),
            target=TOKEN_VAULT_TARGET,
            schema=configured_lakehouse_schema(config, env, TOKEN_VAULT_TARGET),
            context=context or {"config": config, "env": env},
            mode="append",
        )
    return prepared


def pii_guardrail_core(
    dataframe: Any,
    *,
    direct_pii_columns: list[dict[str, str]],
    vault_rows: list[dict[str, Any]],
    severity: str = "blocking",
) -> dict[str, Any]:
    """Evaluate whether present Direct PII values are approved table/column-scoped tokens."""
    from pyspark.sql import functions as F

    approved = {
        (str(row.get("column_id") or ""), str(row.get("token") or ""))
        for row in vault_rows
    }
    untreated = []
    present = []
    for column in direct_pii_columns:
        name = column["column_name"]
        if name not in dataframe.columns:
            continue
        present.append(name)
        values = [row[0] for row in dataframe.select(name).where(F.col(name).isNotNull()).distinct().collect()]
        if any((column["column_id"], str(value)) not in approved for value in values):
            untreated.append(name)
    unsuccessful = bool(untreated)
    warning = unsuccessful and severity.lower() not in {"blocking", "error"}
    status = "warning" if warning else ("failed" if unsuccessful else "passed")
    return {
        "status": status,
        "can_continue": not unsuccessful or warning,
        "severity": severity,
        "classified_columns": [item["column_name"] for item in direct_pii_columns],
        "present_columns": present,
        "untreated_columns": untreated,
        "message": (
            "Raw Direct PII is present in: " + ", ".join(untreated) + "."
            if untreated else "Direct PII is absent or uses approved token-vault tokens."
        ),
    }

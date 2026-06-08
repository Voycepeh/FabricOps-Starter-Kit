"""Thin orchestration helpers for ``02_pipeline`` notebook templates."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any, Mapping
from uuid import uuid4

from .data_profiling import profile_dataframe
from .drift import monitor_data_changes, validate_schema
from .fabric_input_output import (
    read_lakehouse_csv,
    read_lakehouse_excel,
    read_lakehouse_parquet,
    read_lakehouse_table,
    read_warehouse_table,
    write_lakehouse_table,
    write_warehouse_table,
)
from .governance_review import CATALOGUE_TABLE, LINEAGE_TABLE, enforce_dq_rules
from .metadata import _build_metadata_table_key, _build_runtime_audit_fields

METADATA_PIPELINE_RUNS_TABLE = "METADATA_PIPELINE_RUNS"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _definition_name(name: str, definition: Mapping[str, Any]) -> str:
    return str(definition.get("table_name") or definition.get("name") or name)


def _summary_status(results: Mapping[str, Mapping[str, Any]]) -> str:
    statuses = {str(result.get("status", "unknown")).lower() for result in results.values()}
    if not statuses:
        return "not_run"
    if "failed" in statuses:
        return "failed"
    if "warning" in statuses:
        return "warning"
    if statuses <= {"passed", "success", "succeeded"}:
        return "passed"
    return ",".join(sorted(statuses))


def _runtime_audit_fields(config: Any, env: str) -> dict[str, str]:
    try:
        return _build_runtime_audit_fields(config=config, env=env)
    except Exception:
        return {
            "_committed_at": _now_iso(),
            "_committed_by": "unknown",
            "_workspace_name": "",
            "_notebook_name": "",
            "_metadata_lakehouse_name": "",
            "_activity_id": "",
        }


def _dq_summary_fields(dq_result: Mapping[str, Any] | None) -> dict[str, Any]:
    summary = dict((dq_result or {}).get("summary") or {})
    checks = list((dq_result or {}).get("checks") or [])
    failed = [check for check in checks if str(check.get("status", "")).lower() in {"failed", "fail"}]
    warning = [check for check in failed if str(check.get("severity", "")).lower() == "warning"]
    error = [check for check in failed if str(check.get("severity", "")).lower() != "warning"]
    return {
        "DQ_STATUS": str((dq_result or {}).get("status") or "not_run"),
        "DQ_RULE_COUNT": int(summary.get("rule_count", len(checks)) or 0),
        "DQ_FAILED_RULE_COUNT": int(summary.get("failed_rule_count", len(failed)) or 0),
        "DQ_WARNING_RULE_COUNT": int(summary.get("warning_rule_count", len(warning)) or 0),
        "DQ_ERROR_RULE_COUNT": int(summary.get("error_rule_count", len(error)) or 0),
        "DQ_FAILED_ROW_COUNT": int(summary.get("failed_row_count", 0) or 0),
        "DQ_FAILED_ROW_PERCENT": float(summary.get("failed_row_percent", 0.0) or 0.0),
        "DQ_CHECKED_AT": str(summary.get("checked_at") or _now_iso()),
    }


def read_pipeline_sources(
    source_definitions: Mapping[str, Mapping[str, Any]],
    *,
    config: Any,
    env: str,
    spark_session: Any = None,
) -> dict[str, Any]:
    """Read many source datasets from notebook-friendly source definitions.

    Parameters
    ----------
    source_definitions : mapping of str to mapping
        Source definitions keyed by dataset alias. Each definition must include
        ``kind`` and routing fields. Supported ``kind`` values are
        ``lakehouse``, ``warehouse``, ``csv``, ``parquet``, and ``excel``.
    config : FrameworkConfig or dict
        ``00_env_config`` configuration used for routed reads.
    env : str
        Environment key from ``00_env_config``.
    spark_session : pyspark.sql.SparkSession, optional
        Spark session to pass to read helpers.

    Returns
    -------
    dict[str, pyspark.sql.DataFrame]
        DataFrames keyed by the same aliases as ``source_definitions``.

    Notes
    -----
    This helper keeps read plumbing out of ``02_pipeline`` while preserving
    metadata lakehouse routing from ``00_env_config``.
    """
    dataframes: dict[str, Any] = {}
    for name, definition in source_definitions.items():
        kind = str(definition.get("kind", "lakehouse")).lower()
        layer = str(definition.get("layer") or definition.get("target") or "source")
        table = _definition_name(name, definition)
        if kind == "lakehouse":
            dataframes[name] = read_lakehouse_table(config, env, layer, table, spark_session=spark_session)
        elif kind == "warehouse":
            schema = str(definition.get("schema", "dbo"))
            dataframes[name] = read_warehouse_table(config, env, layer, schema, table, spark_session=spark_session)
        elif kind == "csv":
            dataframes[name] = read_lakehouse_csv(config, env, layer, str(definition["path"]), spark_session=spark_session, header=bool(definition.get("header", True)))
        elif kind == "parquet":
            dataframes[name] = read_lakehouse_parquet(config, env, layer, str(definition["path"]), spark_session=spark_session)
        elif kind == "excel":
            dataframes[name] = read_lakehouse_excel(config, env, layer, str(definition["path"]), spark_session=spark_session)
        else:
            raise ValueError(f"Unsupported source kind for {name!r}: {kind!r}.")
    return dataframes


def profile_pipeline_datasets(
    datasets: Mapping[str, Any],
    dataset_definitions: Mapping[str, Mapping[str, Any]],
    *,
    include_distributions: bool = True,
) -> dict[str, Any]:
    """Profile many source or target DataFrames using their definitions.

    Parameters
    ----------
    datasets : mapping of str to DataFrame
        DataFrames keyed by source or target alias.
    dataset_definitions : mapping of str to mapping
        Dataset definitions containing table names and optional profiling
        options such as ``exclude_columns`` and ``distribution_columns``.
    include_distributions : bool, default=True
        Whether to capture lightweight distribution evidence for drift checks.

    Returns
    -------
    dict[str, DataFrame]
        Profile DataFrames keyed by dataset alias.
    """
    profiles: dict[str, Any] = {}
    for name, dataframe in datasets.items():
        definition = dataset_definitions[name]
        profiles[name] = profile_dataframe(
            dataframe,
            table_name=_definition_name(name, definition),
            exclude_columns=definition.get("exclude_columns"),
            include_distributions=bool(definition.get("include_distributions", include_distributions)),
            distribution_columns=definition.get("distribution_columns"),
        )
    return profiles


def run_schema_guardrails(
    datasets: Mapping[str, Any],
    dataset_definitions: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Run schema guardrails for many datasets with per-dataset presets.

    Parameters
    ----------
    datasets : mapping of str to DataFrame
        Source or target DataFrames keyed by alias.
    dataset_definitions : mapping of str to mapping
        Definitions containing ``expected_schema`` and optional
        ``schema_preset`` values.

    Returns
    -------
    dict[str, dict]
        Guardrail results keyed by dataset alias.
    """
    return {
        name: validate_schema(
            dataframe,
            dict(dataset_definitions[name].get("expected_schema") or {}),
            preset=str(dataset_definitions[name].get("schema_preset", "strict")),
        )
        for name, dataframe in datasets.items()
    }


def run_data_drift_guardrails(
    datasets: Mapping[str, Any],
    dataset_definitions: Mapping[str, Mapping[str, Any]],
    *,
    spark: Any,
    config: Any,
    env: str,
    metadata_table: str = CATALOGUE_TABLE,
    run_id: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Run data drift guardrails for many datasets with per-dataset presets.

    Parameters
    ----------
    datasets : mapping of str to DataFrame
        Source or target DataFrames keyed by alias.
    dataset_definitions : mapping of str to mapping
        Definitions containing dataset/table identity, ``stage``, and optional
        ``drift_preset`` values.
    spark : pyspark.sql.SparkSession
        Spark session used by drift helpers to read catalogue evidence.
    config : FrameworkConfig or dict
        ``00_env_config`` route configuration.
    env : str
        Environment key from ``00_env_config``.
    metadata_table : str, default="METADATA_DATA_CATALOGUE"
        Catalogue metadata table used for baseline lookup.
    run_id : str, optional
        Current run id excluded from baseline lookup.

    Returns
    -------
    dict[str, dict]
        Drift guardrail results keyed by dataset alias.
    """
    results: dict[str, dict[str, Any]] = {}
    for name, dataframe in datasets.items():
        definition = dataset_definitions[name]
        results[name] = monitor_data_changes(
            spark,
            dataframe,
            metadata_table,
            str(definition.get("dataset_name") or _definition_name(name, definition)),
            _definition_name(name, definition),
            stage=str(definition.get("stage", "target")),
            preset=str(definition.get("drift_preset", "changing_data")),
            exclude_run_id=run_id,
            distribution_columns=definition.get("distribution_columns"),
            policy_overrides=definition.get("drift_policy_overrides"),
        )
    return results


def run_dq_guardrails(
    datasets: Mapping[str, Any],
    dataset_definitions: Mapping[str, Mapping[str, Any]],
    *,
    config: Any,
    env: str,
    spark_session: Any = None,
) -> dict[str, dict[str, Any]]:
    """Run approved DQ guardrails for many datasets with per-dataset presets.

    Parameters
    ----------
    datasets : mapping of str to DataFrame
        Source or target DataFrames keyed by alias.
    dataset_definitions : mapping of str to mapping
        Definitions containing dataset/table identity and optional ``dq_preset``.
        Use ``"skip"`` to explicitly skip DQ for a dataset.
    config : FrameworkConfig or dict
        ``00_env_config`` route configuration used to read ``METADATA_DQ_RULES``.
    env : str
        Environment key from ``00_env_config``.
    spark_session : pyspark.sql.SparkSession, optional
        Spark session passed to metadata read helpers.

    Returns
    -------
    dict[str, dict]
        DQ guardrail results keyed by dataset alias.
    """
    results: dict[str, dict[str, Any]] = {}
    for name, dataframe in datasets.items():
        definition = dataset_definitions[name]
        if str(definition.get("dq_preset", "approved_rules")).lower() in {"skip", "none", "off"}:
            results[name] = {"status": "skipped", "can_continue": True, "checks": [], "message": "DQ guardrail skipped by preset."}
            continue
        results[name] = enforce_dq_rules(
            dataframe,
            config,
            env,
            str(definition.get("dataset_name") or _definition_name(name, definition)),
            _definition_name(name, definition),
            spark_session=spark_session,
        )
    return results


def write_catalogue_evidence(
    profiles: Mapping[str, Any],
    dataset_definitions: Mapping[str, Mapping[str, Any]],
    *,
    config: Any,
    env: str,
    run_id: str,
    agreement_id: str = "",
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    pipeline_name: str = "",
    schema_results: Mapping[str, Mapping[str, Any]] | None = None,
    drift_results: Mapping[str, Mapping[str, Any]] | None = None,
    dq_results: Mapping[str, Mapping[str, Any]] | None = None,
    metadata_table: str = CATALOGUE_TABLE,
    mode: str = "append",
) -> dict[str, str]:
    """Enrich profile rows with guardrail context and write catalogue evidence.

    Parameters
    ----------
    profiles : mapping of str to DataFrame
        Profile DataFrames returned by :func:`profile_pipeline_datasets`.
    dataset_definitions : mapping of str to mapping
        Source or target definitions containing table, stage, and layer context.
    config, env : object, str
        Metadata lakehouse route from ``00_env_config``.
    run_id : str
        Pipeline run identifier.
    agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, pipeline_name : str, optional
        Governance context added to each catalogue row.
    schema_results, drift_results, dq_results : mapping, optional
        Guardrail results keyed by dataset alias.
    metadata_table : str, default="METADATA_DATA_CATALOGUE"
        Metadata table to append.
    mode : str, default="append"
        Write mode for catalogue evidence.

    Returns
    -------
    dict[str, str]
        Write status keyed by dataset alias.
    """
    from pyspark.sql import functions as F

    audit = _runtime_audit_fields(config, env)
    statuses: dict[str, str] = {}
    for name, profile_df in profiles.items():
        definition = dataset_definitions[name]
        table_name = _definition_name(name, definition)
        dataset_name = str(definition.get("dataset_name") or table_name)
        stage = str(definition.get("stage", "target"))
        drift_result = dict((drift_results or {}).get(name) or {})
        schema_result = dict((schema_results or {}).get(name) or {})
        dq_fields = _dq_summary_fields((dq_results or {}).get(name))
        row_count = None
        if hasattr(profile_df, "select"):
            try:
                row_count = profile_df.select("ROW_COUNT").first()["ROW_COUNT"]
            except Exception:
                row_count = None
        evidence = profile_df
        additions = {
            "metadata_table_key": _build_metadata_table_key(env, dataset_name, table_name),
            "environment_name": env,
            "dataset_name": dataset_name,
            "table_name": table_name,
            "layer": str(definition.get("layer", "")),
            "asset_kind": str(definition.get("kind", "lakehouse")),
            "pipeline_name": pipeline_name,
            "profile_run_id": run_id,
            "profile_stage": stage,
            "profile_status": "success",
            "baseline_status": str(drift_result.get("baseline_status", drift_result.get("status", ""))),
            "source_data_change_check": str(definition.get("drift_preset", "")),
            "profile_baseline_mode": str(drift_result.get("baseline_mode", "")),
            "agreement_id": agreement_id,
            "contract_version": agreement_contract_version,
            "AGREEMENT_ID": agreement_id,
            "AGREEMENT_CONTRACT_VERSION": agreement_contract_version,
            "NOTEBOOK_REGISTRY_ID": notebook_registry_id,
            "NOTEBOOK_ID": notebook_id,
            "PROFILE_RUN_ID": run_id,
            "ENVIRONMENT_NAME": env,
            "DATASET_NAME": dataset_name,
            "PIPELINE_NAME": pipeline_name,
            "EVIDENCE_ROLE": str(definition.get("evidence_role", f"{stage}_profile")),
            "PROFILE_STAGE": stage,
            "PROFILE_STATUS": "success",
            "BASELINE_STATUS": str(drift_result.get("status", "")),
            "SOURCE_SCHEMA_CHECK": str(definition.get("schema_preset", "")) if stage == "source" else "",
            "TARGET_SCHEMA_CHECK": str(definition.get("schema_preset", "")) if stage == "target" else "",
            "SOURCE_DATA_CHANGE_CHECK": str(definition.get("drift_preset", "")) if stage == "source" else "",
            "TARGET_DATA_CHANGE_CHECK": str(definition.get("drift_preset", "")) if stage == "target" else "",
            "SOURCE_CHANGE_SIGNAL_JSON": json.dumps({"schema": schema_result, "drift": drift_result}, default=str, sort_keys=True),
            "LAYER": str(definition.get("layer", "")),
            "ASSET_KIND": str(definition.get("kind", "lakehouse")),
            "PROFILED_TABLE_NAME": table_name,
            "PROFILED_ROW_COUNT": row_count,
            **dq_fields,
            **audit,
        }
        for column, value in additions.items():
            evidence = evidence.withColumn(column, F.lit(value))
        evidence = evidence.withColumn("metadata_column_key", F.concat_ws("::", F.lit(_build_metadata_table_key(env, dataset_name, table_name)), F.col("COLUMN_NAME")))
        write_lakehouse_table(evidence, config, env, "metadata", metadata_table, mode=mode)
        statuses[name] = "written"
    return statuses


def add_runtime_audit_columns(
    datasets: Mapping[str, Any],
    *,
    run_id: str,
    pipeline_name: str = "",
    created_at: str | None = None,
) -> dict[str, Any]:
    """Add standard runtime audit columns to many target DataFrames.

    Parameters
    ----------
    datasets : mapping of str to DataFrame
        Target DataFrames keyed by alias.
    run_id : str
        Pipeline run identifier.
    pipeline_name : str, optional
        Pipeline name stamped onto each row.
    created_at : str, optional
        Deterministic timestamp override. Defaults to current UTC time.

    Returns
    -------
    dict[str, DataFrame]
        DataFrames with ``_fabricops_run_id``, ``_fabricops_pipeline_name``, and
        ``_fabricops_created_at`` columns added.
    """
    from pyspark.sql import functions as F

    timestamp = created_at or _now_iso()
    return {
        name: dataframe.withColumn("_fabricops_run_id", F.lit(run_id))
        .withColumn("_fabricops_pipeline_name", F.lit(pipeline_name))
        .withColumn("_fabricops_created_at", F.lit(timestamp))
        for name, dataframe in datasets.items()
    }


def write_pipeline_targets(
    targets: Mapping[str, Any],
    target_definitions: Mapping[str, Mapping[str, Any]],
    *,
    config: Any,
    env: str,
    default_mode: str = "overwrite",
) -> dict[str, str]:
    """Write many target DataFrames to lakehouse or warehouse targets.

    Parameters
    ----------
    targets : mapping of str to DataFrame
        Target DataFrames keyed by alias.
    target_definitions : mapping of str to mapping
        Target definitions containing ``kind``, ``layer``, ``table_name``, and
        optional warehouse schema/write options.
    config : FrameworkConfig or dict
        ``00_env_config`` route configuration.
    env : str
        Environment key from ``00_env_config``.
    default_mode : str, default="overwrite"
        Write mode used when a target does not specify ``mode``.

    Returns
    -------
    dict[str, str]
        Write status keyed by target alias.
    """
    statuses: dict[str, str] = {}
    for name, dataframe in targets.items():
        definition = target_definitions[name]
        kind = str(definition.get("kind", "lakehouse")).lower()
        layer = str(definition.get("layer") or definition.get("target") or "product")
        table = _definition_name(name, definition)
        mode = str(definition.get("mode", default_mode))
        if kind == "lakehouse":
            write_lakehouse_table(
                dataframe,
                config,
                env,
                layer,
                table,
                mode=mode,
                partition_by=definition.get("partition_by"),
                repartition_by=definition.get("repartition_by"),
                overwrite_schema=bool(definition.get("overwrite_schema", mode == "overwrite")),
            )
        elif kind == "warehouse":
            write_warehouse_table(dataframe, config, env, layer, str(definition.get("schema", "dbo")), table, mode=mode)
        else:
            raise ValueError(f"Unsupported target kind for {name!r}: {kind!r}.")
        statuses[name] = "written"
    return statuses


def write_pipeline_lineage(
    *,
    spark: Any,
    config: Any,
    env: str,
    run_id: str,
    source_definitions: Mapping[str, Mapping[str, Any]],
    target_definitions: Mapping[str, Mapping[str, Any]],
    relationships: list[Mapping[str, Any]] | None = None,
    dataset_name: str = "",
    agreement_id: str = "",
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    pipeline_name: str = "",
    metadata_table: str = LINEAGE_TABLE,
    mode: str = "append",
) -> dict[str, Any]:
    """Write many-to-many source-to-target lineage evidence.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Spark session used to create lineage rows.
    config, env : object, str
        Metadata route from ``00_env_config``.
    run_id : str
        Pipeline run identifier.
    source_definitions, target_definitions : mapping
        Source and target definitions keyed by alias.
    relationships : list of mapping, optional
        Many-to-many lineage relationships. Each item may contain ``sources``,
        ``targets``, ``operation``, and ``description``. When omitted, every
        source is linked to every target.
    dataset_name, agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, pipeline_name : str, optional
        Governance context embedded in lineage payloads.
    metadata_table : str, default="METADATA_DATA_LINEAGE_TABLE"
        Metadata lineage table.
    mode : str, default="append"
        Write mode for lineage evidence.

    Returns
    -------
    dict[str, Any]
        Status, row count, and written rows.
    """
    audit = _runtime_audit_fields(config, env)
    created_at = _now_iso()
    if relationships is None:
        relationships = [{"sources": list(source_definitions), "targets": list(target_definitions), "operation": "pipeline_transform", "description": "User-defined pipeline transformation."}]
    rows: list[dict[str, Any]] = []
    sequence = 0
    for relationship in relationships:
        for source_alias in relationship.get("sources", []):
            for target_alias in relationship.get("targets", []):
                sequence += 1
                source_table = _definition_name(str(source_alias), source_definitions[str(source_alias)])
                target_table = _definition_name(str(target_alias), target_definitions[str(target_alias)])
                payload = {
                    "run_id": run_id,
                    "agreement_id": agreement_id,
                    "agreement_contract_version": agreement_contract_version,
                    "notebook_registry_id": notebook_registry_id,
                    "notebook_id": notebook_id,
                    "pipeline_name": pipeline_name,
                    "source_alias": source_alias,
                    "target_alias": target_alias,
                    "operation": relationship.get("operation", "pipeline_transform"),
                    "description": relationship.get("description", ""),
                }
                rows.append({
                    "lineage_id": f"{run_id}_{sequence}",
                    "dataset_name": dataset_name or str(target_definitions[str(target_alias)].get("dataset_name") or target_table),
                    "run_id": run_id,
                    "source_table": source_table,
                    "target_table": target_table,
                    "source_table_key": _build_metadata_table_key(env, str(source_definitions[str(source_alias)].get("dataset_name") or source_table), source_table),
                    "target_table_key": _build_metadata_table_key(env, str(target_definitions[str(target_alias)].get("dataset_name") or target_table), target_table),
                    "transformation_steps_json": json.dumps(payload, default=str, sort_keys=True),
                    "created_at": created_at,
                    **audit,
                })
    if rows:
        write_lakehouse_table(spark.createDataFrame(rows), config, env, "metadata", metadata_table, mode=mode)
    return {"status": "written" if rows else "skipped", "row_count": len(rows), "rows": rows}


def write_pipeline_run_summary(
    *,
    spark: Any,
    config: Any,
    env: str,
    run_id: str,
    agreement_id: str = "",
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    notebook_type: str = "02_pipeline",
    pipeline_name: str = "",
    started_at: str | None = None,
    completed_at: str | None = None,
    status: str = "completed",
    source_definitions: Mapping[str, Mapping[str, Any]] | None = None,
    target_definitions: Mapping[str, Mapping[str, Any]] | None = None,
    source_schema_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_schema_results: Mapping[str, Mapping[str, Any]] | None = None,
    source_drift_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_drift_results: Mapping[str, Mapping[str, Any]] | None = None,
    source_dq_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_dq_results: Mapping[str, Mapping[str, Any]] | None = None,
    lineage_status: str = "not_run",
    catalogue_status: str = "not_run",
    message: str = "",
    metadata_table: str = METADATA_PIPELINE_RUNS_TABLE,
    mode: str = "append",
) -> dict[str, Any]:
    """Write a pipeline runtime summary to metadata.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Spark session used to create the one-row summary DataFrame.
    config, env : object, str
        Metadata route from ``00_env_config``.
    run_id : str
        Pipeline run identifier.
    agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, notebook_type, pipeline_name : str, optional
        Agreement and notebook registry context.
    started_at, completed_at : str, optional
        Runtime timestamps. Defaults to current UTC time when omitted.
    status : str, default="completed"
        Overall pipeline status.
    source_definitions, target_definitions : mapping, optional
        Dataset definitions used to compute source and target counts.
    source_schema_results, target_schema_results, source_drift_results, target_drift_results, source_dq_results, target_dq_results : mapping, optional
        Guardrail result dictionaries included in the JSON summary.
    lineage_status, catalogue_status, message : str, optional
        Evidence write statuses and support message.
    metadata_table : str, default="METADATA_PIPELINE_RUNS"
        Metadata table that stores runtime summaries.
    mode : str, default="append"
        Write mode for the runtime summary row.

    Returns
    -------
    dict[str, Any]
        The summary row that was written.

    Notes
    -----
    The row is written via ``write_lakehouse_table(..., config, env,
    "metadata", metadata_table, mode="append")`` so runtime evidence never
    relies on a default attached lakehouse.
    """
    completed = completed_at or _now_iso()
    started = started_at or completed
    sources = source_definitions or {}
    targets = target_definitions or {}
    source_guardrail_status = _summary_status({**(source_schema_results or {}), **(source_drift_results or {})})
    target_guardrail_status = _summary_status({**(target_schema_results or {}), **(target_drift_results or {})})
    dq_status = _summary_status({**(source_dq_results or {}), **(target_dq_results or {})})
    run_summary = {
        "source_schema_results": source_schema_results or {},
        "target_schema_results": target_schema_results or {},
        "source_drift_results": source_drift_results or {},
        "target_drift_results": target_drift_results or {},
        "source_dq_results": source_dq_results or {},
        "target_dq_results": target_dq_results or {},
        "source_tables": [_definition_name(name, definition) for name, definition in sources.items()],
        "target_tables": [_definition_name(name, definition) for name, definition in targets.items()],
    }
    row = {
        "run_id": run_id or str(uuid4()),
        "agreement_id": agreement_id,
        "agreement_contract_version": agreement_contract_version,
        "notebook_registry_id": notebook_registry_id,
        "notebook_id": notebook_id,
        "notebook_type": notebook_type,
        "pipeline_name": pipeline_name,
        "environment_name": env,
        "started_at": started,
        "completed_at": completed,
        "status": status,
        "source_count": len(sources),
        "target_count": len(targets),
        "source_guardrail_status": source_guardrail_status,
        "target_guardrail_status": target_guardrail_status,
        "dq_status": dq_status,
        "lineage_status": lineage_status,
        "catalogue_status": catalogue_status,
        "message": message,
        "run_summary_json": json.dumps(run_summary, default=str, sort_keys=True),
        "created_at": _now_iso(),
    }
    write_lakehouse_table(spark.createDataFrame([row]), config, env, "metadata", metadata_table, mode=mode)
    return row

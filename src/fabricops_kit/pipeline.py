"""Thin orchestration helpers for ``02_pipeline`` notebook templates."""

from __future__ import annotations

import json
from typing import Any, Mapping
from uuid import uuid4

from .data_profiling import profile_dataframe
from .guardrails import enforce_freshness, enforce_profile_behavior, stop_if_failed, validate_schema
from .fabric_input_output import _configured_lakehouse_schema, write_lakehouse_table
from .governance_review import CATALOGUE_TABLE, LINEAGE_TABLE, enforce_dq_rules
from .config import _current_audit_timestamp, _get_audit_timezone
from .metadata import _build_metadata_table_key, _build_runtime_audit_fields, _write_guardrail_result_row

METADATA_PIPELINE_RUNS_TABLE = "METADATA_PIPELINE_RUNS"
GUARDRAIL_RESULTS_TABLE = "METADATA_GUARDRAIL_RESULTS"


def _now_iso(config: Any = None) -> str:
    return _current_audit_timestamp(config=config)


def _definition_name(name: str, definition: Mapping[str, Any]) -> str:
    return str(definition.get("table_name") or definition.get("name") or name)


def _summary_status(results: Mapping[str, Mapping[str, Any]]) -> str:
    """Return a roll-up status for guardrail result mappings.

    ``baseline_created`` is non-blocking and rolls up as ``passed``. ``skipped``
    is ignored when other concrete results exist and is returned only when all
    supplied results were skipped.
    """
    statuses = {str(result.get("status", "unknown")).lower() for result in results.values()}
    if not statuses:
        return "not_run"
    concrete = statuses - {"skipped"}
    if not concrete:
        return "skipped"
    if "failed" in concrete:
        return "failed"
    if "warning" in concrete:
        return "warning"
    if concrete <= {"passed", "success", "succeeded", "baseline_created"}:
        return "passed"
    return ",".join(sorted(concrete))


def _runtime_audit_fields(config: Any, env: str) -> dict[str, str]:
    try:
        return _build_runtime_audit_fields(config=config, env=env)
    except Exception:
        return {
            "_committed_at": _now_iso(config),
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
        "dq_status": str((dq_result or {}).get("status") or "not_run"),
        "dq_rule_count": int(summary.get("rule_count", len(checks)) or 0),
        "dq_failed_rule_count": int(summary.get("failed_rule_count", len(failed)) or 0),
        "dq_warning_rule_count": int(summary.get("warning_rule_count", len(warning)) or 0),
        "dq_error_rule_count": int(summary.get("error_rule_count", len(error)) or 0),
        "dq_failed_row_count": int(summary.get("failed_row_count", 0) or 0),
        "dq_failed_row_percent": float(summary.get("failed_row_percent", 0.0) or 0.0),
        "dq_checked_at": str(summary.get("checked_at") or _now_iso()),
    }


def _canonical_catalogue_profile_df(profile_df: Any):
    """Return profile evidence using lowercase catalogue column names only."""
    from pyspark.sql import functions as F

    profile_columns = list(getattr(profile_df, "columns", []) or [])
    by_lower = {str(column).lower(): column for column in profile_columns}
    source_map = {
        "table_name": ("table_name", "TABLE_NAME"),
        "column_name": ("column_name", "COLUMN_NAME"),
        "run_timestamp": ("run_timestamp", "RUN_TIMESTAMP"),
        "data_type": ("data_type", "DATA_TYPE"),
        "row_count": ("row_count", "ROW_COUNT"),
        "null_count": ("null_count", "NULL_COUNT"),
        "null_percent": ("null_percent", "NULL_PERCENT"),
        "distinct_count": ("distinct_count", "DISTINCT_COUNT"),
        "distinct_percent": ("distinct_percent", "DISTINCT_PERCENT"),
        "min_value": ("min_value", "MIN_VALUE"),
        "max_value": ("max_value", "MAX_VALUE"),
        "distribution_type": ("distribution_type", "DISTRIBUTION_TYPE"),
        "distribution_json": ("distribution_json", "DISTRIBUTION_JSON"),
    }
    expressions = []
    for target, candidates in source_map.items():
        source = next((candidate for candidate in candidates if candidate in profile_columns), None)
        if source is None:
            source = next((by_lower[candidate.lower()] for candidate in candidates if candidate.lower() in by_lower), None)
        if source is not None:
            expressions.append(F.col(source).alias(target))
    return profile_df.select(*expressions) if expressions else profile_df


def _normalize_catalogue_evidence_types(evidence_df: Any):
    """Cast catalogue evidence columns to the persisted metadata table schema."""
    from pyspark.sql import functions as F

    casts = {
        "row_count": "long",
        "null_count": "long",
        "distinct_count": "long",
        "null_percent": "double",
        "distinct_percent": "double",
        "run_timestamp": "timestamp",
    }
    normalized = evidence_df
    columns = set(getattr(evidence_df, "columns", []) or [])
    for column_name, data_type in casts.items():
        if column_name in columns:
            normalized = normalized.withColumn(column_name, F.col(column_name).cast(data_type))
    return normalized



def _add_audit_columns(dataframe: Any, *, run_id: str, pipeline_name: str, config: Any = None):
    """Return a DataFrame with standard FabricOps target audit columns."""
    from pyspark.sql import functions as F

    audit_created_at = _current_audit_timestamp(config=config)
    return (
        dataframe
        .withColumn("_fabricops_run_id", F.lit(run_id))
        .withColumn("_fabricops_pipeline_name", F.lit(pipeline_name))
        .withColumn("_fabricops_created_at", F.lit(audit_created_at))
    )


def prepare_pipeline_table_configs(
    table_configs: list[dict[str, Any]],
    default_settings: Mapping[str, Any],
    *,
    table_role: str,
    run_id: str = "",
    pipeline_name: str = "",
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Prepare source or target table configs for a pipeline notebook.

    Parameters
    ----------
    table_configs : list of dict
        User-authored table config dictionaries from ``SOURCE_TABLES`` or
        ``TARGET_TABLES``.
    default_settings : mapping
        Default guardrails, and for targets write options, merged before each
        table config. Table-specific values take precedence.
    table_role : {"source", "target"}
        Role-specific preparation mode. Source mode validates that each config
        already includes a DataFrame; target mode adds FabricOps audit columns
        and derives write metadata.
    run_id : str, optional
        Pipeline run identifier used for target audit columns. Required for
        target role.
    pipeline_name : str, optional
        Pipeline name used for target audit columns. Required for target role.

    Returns
    -------
    tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]
        Enriched table configs and a lookup keyed by table ``key``.

    Raises
    ------
    ValueError
        If ``table_role`` is not ``"source"`` or ``"target"``.

    Notes
    -----
    Source configs derive ``dataset_name`` from ``table_name`` and ``stage`` from
    ``layer``. Source
    DataFrames must be loaded directly in the notebook with the existing
    FabricOps read helpers and supplied in each source config as ``df``.

    Target configs derive ``dataset_name``, ``stage``, ``target_layer``,
    ``target_name``, and ``target_kind`` unless overridden, then add standard
    FabricOps audit columns.

    """
    normalized_role = str(table_role or "").lower().strip()
    if normalized_role not in {"source", "target"}:
        raise ValueError("table_role must be 'source' or 'target'.")

    enriched_tables: list[dict[str, Any]] = []
    for table_config in table_configs:
        merged_config = {**default_settings, **table_config}
        dataset_name = merged_config.get("dataset_name", merged_config["table_name"])
        stage = merged_config.get("stage", merged_config["layer"])
        if normalized_role == "source":
            if "df" not in merged_config:
                table_key = merged_config.get("key", merged_config.get("table_name", "<unknown>"))
                raise ValueError(
                    "Source table config "
                    f"{table_key!r} must include a pre-loaded DataFrame in the 'df' key. "
                    "Load the source with read_lakehouse_table, read_lakehouse_csv, "
                    "read_lakehouse_parquet, read_lakehouse_excel, read_warehouse_table, "
                    "or spark.read.table before calling prepare_pipeline_table_configs."
                )
            enriched_table = {
                **merged_config,
                "dataset_name": dataset_name,
                "stage": stage,
            }
        else:
            target_layer = merged_config.get("target_layer", merged_config["layer"])
            target_name = merged_config.get("target_name", merged_config["table_name"])
            target_kind = merged_config.get("target_kind", merged_config.get("kind", "lakehouse"))
            enriched_table = {
                **merged_config,
                "df": _add_audit_columns(merged_config["df"], run_id=run_id, pipeline_name=pipeline_name, config=merged_config.get("config", default_settings.get("config"))),
                "dataset_name": dataset_name,
                "stage": stage,
                "target_layer": target_layer,
                "target_name": target_name,
                "target_kind": target_kind,
            }
        enriched_tables.append(enriched_table)

    return enriched_tables, {table_config["key"]: table_config for table_config in enriched_tables}

def _table_key(table_config: Mapping[str, Any]) -> str:
    return str(table_config["key"])


def _table_name(table_config: Mapping[str, Any]) -> str:
    return str(table_config.get("table_name") or table_config.get("target_name") or table_config["key"])


def _guardrail_can_continue(result: Mapping[str, Any] | None) -> bool:
    return bool((result or {}).get("can_continue", True))


def _build_guardrail_evidence_definitions(table_configs: list[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """Build catalogue evidence definitions for pipeline table guardrails.

    Parameters
    ----------
    table_configs : list of mapping
        Source or target table configuration dictionaries. Each item must
        include ``key`` and normally includes ``table_name``, ``stage``, and
        optional target write metadata. DataFrame values are intentionally
        omitted from the returned definitions.

    Returns
    -------
    dict[str, dict[str, Any]]
        Definitions keyed by table key, suitable for
        :func:`write_catalogue_evidence`. Target definitions include resolved
        write-layer, kind, and mode fields when the stage is ``target``.

    """
    definitions: dict[str, dict[str, Any]] = {}
    for table_config in table_configs:
        table_key = _table_key(table_config)
        definition = {key: value for key, value in table_config.items() if key != "df"}
        definition["table_name"] = _table_name(table_config)
        definition["stage"] = table_config.get("stage", "target")
        if definition["stage"] == "target":
            definition["layer"] = table_config.get("target_layer", "unified")
            definition["kind"] = table_config.get("target_kind", "lakehouse")
            definition["mode"] = table_config.get("write_mode", "overwrite")
        definitions[table_key] = definition
    return definitions


def run_table_guardrails(
    table_configs: list[dict[str, Any]],
    *,
    config: Any,
    env: str,
    run_id: str,
    spark_session: Any,
    agreement_id: str = "",
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    pipeline_name: str = "",
    stop_on_failure: bool = False,
) -> dict[str, Any]:
    """Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails.

    Parameters
    ----------
    table_configs : list of dict
        Source or target table configs. Each config must contain ``key``,
        ``df``, and ``expected_schema``. Optional keys such as
        ``dataset_name``, ``stage``, ``schema_preset``, ``profile_mode``,
        ``profile_behavior_severity``, ``watermark_column``, ``dq_preset``,
        ``distribution_columns``, and ``exclude_columns`` control the guardrail
        behavior.
    config : Any
        FabricOps framework configuration from ``00_env_config``.
    env : str
        Environment key used for configured metadata routing.
    run_id : str
        Current pipeline run identifier.
    spark_session : Any
        Spark session used by profile behavior and DQ helpers.
    agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, pipeline_name : str, optional
        Governance context written with catalogue evidence.
    stop_on_failure : bool, default False
        When True, collect all guardrail results and catalogue evidence, then
        stop notebook execution via the standard guardrail stopper if any table
        cannot continue.

    Returns
    -------
    dict[str, Any]
        Guardrail result bundle containing profiles, schema results, freshness
        results, profile behavior results, DQ results, catalogue status, evidence definitions, concise
        ``summary``, ``can_continue``, and ``failed_tables``. Results remain
        separated by table key and guardrail type.

    Notes
    -----
    This helper intentionally collects all per-table schema, freshness, profile behavior, and DQ
    results before reporting blocking failures. DQ results that return an
    annotated DataFrame update the corresponding table config ``df`` in place
    so downstream writes use the checked DataFrame. Metadata reads and writes
    are routed through the configured metadata target by the called helpers.

    """
    profiles: dict[str, Any] = {}
    schema_results: dict[str, Mapping[str, Any]] = {}
    freshness_results: dict[str, Mapping[str, Any]] = {}
    stability_results: dict[str, Mapping[str, Any]] = {}
    dq_results: dict[str, Mapping[str, Any]] = {}
    failed_tables: list[str] = []
    evidence_definitions = _build_guardrail_evidence_definitions(table_configs)

    for table_config in table_configs:
        table_key = _table_key(table_config)
        table_name = _table_name(table_config)
        dataset_name = table_config.get("dataset_name", table_name)
        stage = table_config.get("stage", "target")
        dataframe = table_config["df"]

        profiles[table_key] = profile_dataframe(
            dataframe,
            table_name=table_name,
            # profile_dataframe automatically excludes FabricOps/DQ technical annotation columns
            # and unions those defaults with any table-specific exclude_columns.
            exclude_columns=table_config.get("exclude_columns"),
            include_distributions=True,
            distribution_columns=table_config.get("distribution_columns"),
            config=config,
            run_timestamp_timezone=table_config.get("run_timestamp_timezone"),
        )

        schema_results[table_key] = validate_schema(
            dataframe,
            table_config["expected_schema"],
            preset=table_config.get("schema_preset", "strict"),
        )

        freshness_results[table_key] = enforce_freshness(
            dataframe,
            table_config.get("freshness_column"),
            table_config.get("freshness_max_lag_days"),
            severity=table_config.get("freshness_severity", "blocking"),
        )

        stability_results[table_key] = enforce_profile_behavior(
            spark_session,
            dataframe,
            CATALOGUE_TABLE,
            dataset_name,
            table_name,
            stage=stage,
            run_id=run_id,
            profile_mode=table_config.get("profile_mode"),
            watermark_column=table_config.get("watermark_column"),
            severity=table_config.get("profile_behavior_severity", table_config.get("severity", "blocking")),
            rule_key=table_config.get("profile_behavior_rule_key", "profile_behavior_default"),
            exclude_columns=table_config.get("exclude_columns"),
            exclude_run_id=run_id,
            config=config,
            env=env,
            current_profile=profiles[table_key],
            write_results=table_config.get("write_profile_behavior_results", True),
            rules_table=table_config.get("profile_behavior_rules_table", "METADATA_GUARDRAIL_RULES"),
            rules_df=table_config.get("profile_behavior_rules_df"),
        )

        if table_config.get("dq_preset", "approved_rules") == "skip":
            dq_results[table_key] = {
                "status": "skipped",
                "can_continue": True,
                "checks": [],
                "message": "DQ guardrail skipped by preset.",
            }
        else:
            dq_results[table_key] = enforce_dq_rules(
                dataframe,
                config,
                env,
                dataset_name,
                table_name,
                spark_session=spark_session,
                run_id=run_id,
                write_results=False,
            )

        if "dataframe" in dq_results[table_key]:
            table_config["df"] = dq_results[table_key]["dataframe"]

        if table_config.get("write_guardrail_results", True) and hasattr(spark_session, "createDataFrame"):
            for guardrail_type, rule_type, guardrail_result in (
                ("schema", table_config.get("schema_preset", "strict"), schema_results[table_key]),
                ("freshness", table_config.get("freshness_column", "freshness"), freshness_results[table_key]),
                ("dq", table_config.get("dq_preset", "approved_rules"), dq_results[table_key]),
            ):
                _write_guardrail_result_row(
                    spark_session=spark_session,
                    config=config,
                    env=env,
                    run_id=run_id,
                    dataset_name=dataset_name,
                    table_name=table_name,
                    guardrail_type=guardrail_type,
                    rule_type=str(rule_type or guardrail_type),
                    result=guardrail_result,
                )

        table_can_continue = all(
            _guardrail_can_continue(result)
            for result in (schema_results[table_key], freshness_results[table_key], stability_results[table_key], dq_results[table_key])
        )
        if not table_can_continue:
            failed_tables.append(table_key)

    catalogue_status = write_catalogue_evidence(
        profiles,
        evidence_definitions,
        config=config,
        env=env,
        run_id=run_id,
        agreement_id=agreement_id,
        agreement_contract_version=agreement_contract_version,
        notebook_registry_id=notebook_registry_id,
        notebook_id=notebook_id,
        pipeline_name=pipeline_name,
        schema_results=schema_results,
        freshness_results=freshness_results,
        stability_results=stability_results,
        dq_results=dq_results,
    )

    summary = {
        "schema_results": schema_results,
        "freshness_results": freshness_results,
        "stability_results": stability_results,
        "dq_results": dq_results,
        "catalogue_status": catalogue_status,
        "failed_tables": failed_tables,
    }
    result = {
        "profiles": profiles,
        "schema_results": schema_results,
        "freshness_results": freshness_results,
        "stability_results": stability_results,
        "dq_results": dq_results,
        "catalogue_status": catalogue_status,
        "evidence_definitions": evidence_definitions,
        "summary": summary,
        "can_continue": not failed_tables,
        "failed_tables": failed_tables,
    }

    if stop_on_failure and failed_tables:
        stop_if_failed(
            {
                "status": "failed",
                "can_continue": False,
                "message": "Blocking guardrail failure for table(s): " + ", ".join(failed_tables),
                "failed_tables": failed_tables,
            }
        )

    return result


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
    freshness_results: Mapping[str, Mapping[str, Any]] | None = None,
    stability_results: Mapping[str, Mapping[str, Any]] | None = None,
    dq_results: Mapping[str, Mapping[str, Any]] | None = None,
    metadata_table: str = CATALOGUE_TABLE,
    mode: str = "append",
) -> dict[str, str]:
    """Write observed profile evidence to the metadata data catalogue.

    Parameters
    ----------
    profiles : mapping of str to DataFrame
        Profile DataFrames produced by ``profile_dataframe`` for each dataset.
    dataset_definitions : mapping of str to mapping
        Source or target definitions containing table, stage, and layer context.
    config, env : object, str
        Metadata lakehouse route from ``00_env_config``.
    run_id : str
        Pipeline run identifier.
    agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, pipeline_name : str, optional
        Governance context added to each catalogue row.
    schema_results, freshness_results, stability_results, dq_results : mapping, optional
        Runtime guardrail results accepted for API compatibility but not written
        to ``METADATA_DATA_CATALOGUE``.
    metadata_table : str, default="METADATA_DATA_CATALOGUE"
        Metadata table to append.
    mode : str, default="append"
        Physical write mode for catalogue evidence.

    Returns
    -------
    dict[str, str]
        Write status keyed by dataset alias.

    """
    from pyspark.sql import functions as F

    del schema_results, freshness_results, dq_results
    audit = _runtime_audit_fields(config, env)
    statuses: dict[str, str] = {}
    for name, profile_df in profiles.items():
        definition = dataset_definitions[name]
        table_name = _definition_name(name, definition)
        dataset_name = str(definition.get("dataset_name") or table_name)
        stage = str(definition.get("stage", "target"))
        stability_result = dict((stability_results or {}).get(name) or {})
        base_evidence = _canonical_catalogue_profile_df(profile_df)
        metadata_table_key = _build_metadata_table_key(env, dataset_name, table_name)
        profile_evidence_rows = list(stability_result.get("profile_evidence_rows") or [])
        if not profile_evidence_rows:
            profile_evidence_rows = [{
                "watermark_column": str(stability_result.get("watermark_column", definition.get("watermark_column", ""))),
                "watermark_value": str(stability_result.get("watermark_value", "__FULL_TABLE__" if str(stability_result.get("profile_mode", "")) == "static_data" else "")),
                "profile_payload_json": str(stability_result.get("profile_payload_json", "")),
                "profile_hash": str(stability_result.get("profile_hash", "")),
                "row_count": stability_result.get("row_count"),
            }]
        additions = {
            "metadata_table_key": metadata_table_key,
            "environment_name": env,
            "dataset_name": dataset_name,
            "table_name": table_name,
            "layer": str(definition.get("layer", "")),
            "asset_kind": str(definition.get("kind", "lakehouse")),
            "pipeline_name": pipeline_name,
            "profile_run_id": run_id,
            "profile_stage": stage,
            "profile_status": "success",
            "profiled_at": _now_iso(config),
            "agreement_id": agreement_id,
            "contract_version": agreement_contract_version,
            "notebook_registry_id": notebook_registry_id,
            "notebook_id": notebook_id,
            "evidence_role": str(definition.get("evidence_role", f"{stage}_profile")),
            "profile_mode": str(stability_result.get("profile_mode", definition.get("profile_mode", ""))),
            **audit,
        }
        for profile_evidence in profile_evidence_rows:
            evidence = base_evidence
            group_additions = {
                **additions,
                "watermark_column": str(profile_evidence.get("watermark_column", "")),
                "watermark_value": str(profile_evidence.get("watermark_value", "")),
                "profile_payload_json": str(profile_evidence.get("profile_payload_json", "")),
                "profile_hash": str(profile_evidence.get("profile_hash", "")),
            }
            if profile_evidence.get("row_count") not in (None, ""):
                group_additions["row_count"] = profile_evidence.get("row_count")
            for column, value in group_additions.items():
                evidence = evidence.withColumn(column, F.lit(value))
            evidence = evidence.withColumn("metadata_column_key", F.concat_ws("::", F.lit(metadata_table_key), F.col("column_name")))
            evidence = _normalize_catalogue_evidence_types(evidence)
            write_lakehouse_table(evidence, config, env, "metadata", metadata_table, schema=_configured_lakehouse_schema(config, env, "metadata"), mode=mode)
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
    created_at = _now_iso(config)
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
        write_lakehouse_table(spark.createDataFrame(rows), config, env, "metadata", metadata_table, schema=_configured_lakehouse_schema(config, env, "metadata"), mode=mode)
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
    source_freshness_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_freshness_results: Mapping[str, Mapping[str, Any]] | None = None,
    source_stability_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_stability_results: Mapping[str, Mapping[str, Any]] | None = None,
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
    source_schema_results, target_schema_results, source_freshness_results, target_freshness_results, source_stability_results, target_stability_results, source_dq_results, target_dq_results : mapping, optional
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
    completed = completed_at or _now_iso(config)
    started = started_at or completed
    sources = source_definitions or {}
    targets = target_definitions or {}
    source_guardrail_status = _summary_status({**(source_schema_results or {}), **(source_freshness_results or {}), **(source_stability_results or {})})
    target_guardrail_status = _summary_status({**(target_schema_results or {}), **(target_freshness_results or {}), **(target_stability_results or {})})
    dq_status = _summary_status({**(source_dq_results or {}), **(target_dq_results or {})})
    run_summary = {
        "source_schema_results": source_schema_results or {},
        "target_schema_results": target_schema_results or {},
        "source_freshness_results": source_freshness_results or {},
        "target_freshness_results": target_freshness_results or {},
        "source_stability_results": source_stability_results or {},
        "target_stability_results": target_stability_results or {},
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
        "created_at": _now_iso(config),
    }
    write_lakehouse_table(spark.createDataFrame([row]), config, env, "metadata", metadata_table, schema=_configured_lakehouse_schema(config, env, "metadata"), mode=mode)
    return row

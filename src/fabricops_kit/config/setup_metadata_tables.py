"""Public owner file for FabricOps metadata table setup."""

from __future__ import annotations

from typing import Any
from fabricops_kit.io.shared import read_lakehouse_table_core, write_lakehouse_table_core

from .metadata_schemas import (
    CANONICAL_METADATA_TABLES,
    GOVERNANCE_METADATA_TABLES,
    ENGINEERING_METADATA_TABLES,
    metadata_table_physical_schema,
    metadata_schema_type_name,
    metadata_table_field_names,
    metadata_table_schema_registry,
)
from .shared import FrameworkConfig, get_store, is_table_not_found_error, validate_framework_config


def _schema_fields_by_name(schema: Any) -> dict[str, Any]:
    """Return schema fields keyed by name for Spark-like schemas."""
    return {field.name: field for field in getattr(schema, "fields", [])}


def _validate_existing_metadata_schema(table_name: str, existing_schema: Any, expected_schema: Any) -> None:
    """Validate that required metadata columns exist with compatible physical types."""
    existing = _schema_fields_by_name(existing_schema)
    expected = _schema_fields_by_name(expected_schema)
    if not existing:
        existing = {name: None for name in getattr(existing_schema, "fieldNames", lambda: [])()}
    missing = [name for name in expected if name not in existing]
    if missing:
        raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing)}.")
    if table_name == "METADATA_DATA_PROFILED" and "frequency_json" in existing:
        raise ValueError("METADATA_DATA_PROFILED has unexpected legacy column: frequency_json.")
    mismatches: list[str] = []
    for name, expected_field in expected.items():
        existing_field = existing.get(name)
        if existing_field is None:
            continue
        expected_type = metadata_schema_type_name(expected_field.dataType)
        existing_type = metadata_schema_type_name(existing_field.dataType)
        if existing_type != expected_type:
            mismatches.append(f"{name} type expected {expected_type} but found {existing_type}")
    if mismatches:
        raise ValueError(
            f"{table_name} physical schema does not match the canonical FabricOps metadata schema: "
            + "; ".join(mismatches)
            + "."
        )


def _result(table_name: str, status: str, message: str, *, error_type: str | None = None) -> dict[str, Any]:
    """Return one per-table setup result."""
    item = {"table": table_name, "status": status, "message": message}
    if error_type:
        item["error_type"] = error_type
    return item


def _active_steward_presence(steward_rows: Any) -> int:
    """Return 1 when any active steward row exists, otherwise 0."""
    try:
        if steward_rows is None:
            return 0
        if hasattr(steward_rows, "where"):
            steward_rows = steward_rows.where("is_active = true")
        if hasattr(steward_rows, "limit"):
            steward_rows = steward_rows.limit(1)
        if hasattr(steward_rows, "take"):
            return 1 if steward_rows.take(1) else 0
        if hasattr(steward_rows, "head"):
            return 1 if steward_rows.head(1) else 0
        if hasattr(steward_rows, "first"):
            return 1 if steward_rows.first() is not None else 0
        if hasattr(steward_rows, "collect"):
            return 1 if steward_rows.collect()[:1] else 0
    except Exception:
        return 0
    return 0


def _print_setup_summary(
    *,
    total: int,
    created: list[str],
    validated: list[str],
    failed: list[str],
    table_results: dict[str, dict[str, Any]],
    active_stewards: int,
) -> None:
    """Print concise notebook-facing setup output after per-table progress."""
    active_label = "Yes" if active_stewards else "No"
    if failed:
        successful_count = len(created) + len(validated)
        print("\nFabricOps metadata setup completed with failures.")
        print(f"Successful: {successful_count}/{total}")
        print(f"Failed: {len(failed)}/{total}\n")
        print("Failed tables:")
        for table_name in failed:
            print(f"- {table_name}: {table_results[table_name].get('message', '')}")
        print(f"Active steward present: {active_label}")
        return
    if created:
        print(f"\nFabricOps metadata setup complete ({total}/{total}).")
        print(f"Created: {len(created)}")
        print(f"Validated: {len(validated)}")
        print("Created tables:")
        for table_name in created:
            print(f"- {table_name}")
        print(f"Active steward present: {active_label}")
        return
    print(f"\nFabricOps metadata tables ready ({total}/{total}).")
    print(f"Active steward present: {active_label}")


def setup_metadata_tables(
    *,
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    require_active_steward: bool = False,
    verbose: bool = True,
    raise_on_failure: bool = False,
) -> dict[str, Any]:
    """Create or check the FabricOps metadata tables for one environment.

    Creates missing metadata tables and validates existing metadata tables
    against the canonical registry for the installed FabricOps version. The
    function finds the metadata lakehouse configured for the selected
    environment, creates missing tables as empty Delta tables, leaves valid
    existing tables in place, reports invalid existing tables as failed, and
    returns a setup report.

    This function prepares the metadata table structures only. It does not
    create business metadata records such as stewards, agreements, catalogue
    rows, profiles, lineage events, enrichment records, guardrail rules, or
    guardrail results.

    Parameters
    ----------
    spark : Any
        Spark session used to create empty schema DataFrames and read or write
        the metadata lakehouse tables.
    config : FrameworkConfig | dict[str, Any]
        FabricOps configuration used to find the selected environment and its
        metadata lakehouse.
    env : str
        Environment whose configured metadata lakehouse should be initialized
        or validated.
    require_active_steward : bool, default=False
        When ``True``, raise if ``METADATA_DATA_STEWARD`` contains no active
        steward rows after setup. This option does not create a steward
        record.
    verbose : bool, default=True
        Controls whether the concise per-table setup summary is printed.
    raise_on_failure : bool, default=False
        When ``True``, raise a ``RuntimeError`` after processing all tables if
        any table failed creation or validation.

    Returns
    -------
    dict[str, Any]
        A dictionary summarizing the completed metadata lakehouse setup,
        including the resolved governance and engineering metadata schemas,
        metadata tables checked,
        tables created, existing tables successfully validated, failed tables,
        per-table messages, active steward readiness, fully qualified table
        names, and overall setup status. Key fields are ``status``,
        ``data_agreement``, ``governance``, ``engineering``, ``tables``,
        ``table_results``,
        ``metadata_schemas``, ``fully_qualified_tables``, ``created_tables``,
        ``validated_tables``, ``failed_tables``, ``created_or_checked_tables``,
        ``warnings``, ``active_metadata_tables``, and
        ``active_metadata_table_count``.

        ``status`` is ``"ready"`` when no table failures occur,
        ``"partial_failure"`` when some tables succeed and some fail, and
        ``"failed"`` when all table operations fail. ``data_agreement``
        summarizes steward, agreement, and contract readiness. ``governance``
        summarizes governance-authored tables, and ``engineering`` summarizes
        engineering-written tables. Active steward readiness depends on
        whether active steward rows already exist.

    Raises
    ------
    ValueError
        If the configuration is invalid, the resolved ``metadata`` target is
        not a schema-enabled lakehouse, or ``require_active_steward=True`` and
        no active steward rows exist after setup.
    RuntimeError
        If ``raise_on_failure=True`` and one or more metadata tables fail
        creation or validation after all tables have been processed.

    Notes
    -----
    Setup flow:

    1. Validate the supplied FabricOps configuration.
    2. Find the metadata lakehouse configured for the selected environment.
    3. Verify that the metadata target is a lakehouse.
    4. Resolve each table's physical schema from its canonical ownership and
       the configured governance/engineering schema names.
    5. Load the required FabricOps table definitions.
    6. Attempt to read each required metadata table.
    7. When a table is missing, create an empty Spark DataFrame using its
       required FabricOps table structure.
    8. Write that empty DataFrame to the metadata lakehouse using overwrite
       mode to create the table.
    9. Read the created table again.
    10. Validate required column names and physical Spark data types.
    11. Continue processing the remaining tables when one table fails.
    12. Check whether at least one active steward record exists.
    13. Return overall, data-agreement, governance, and per-table setup
        results.

    ``data_agreement["active_steward_count"]`` is retained for compatibility
    and reports readiness presence: ``1`` when at least one active steward
    exists and ``0`` otherwise. It is not a complete active steward population
    count.

    The canonical registry may expand in later compatible FabricOps releases.
    In v0.2.0, metadata tables created or validated from
    ``metadata_table_schema_registry()`` are ``METADATA_DATA_STEWARD``,
    ``METADATA_DATA_AGREEMENT``, ``METADATA_DATA_CONTRACT``,
    ``METADATA_DATA_CATALOGUE``, ``METADATA_DATA_PROFILED``,
    ``METADATA_DATA_PROFILED_FREQUENCY``, ``METADATA_DATA_LINEAGE``, ``METADATA_DATA_ACCESS``,
    ``METADATA_ENRICHMENT``, ``METADATA_GUARDRAIL``, and
    ``METADATA_GUARDRAIL_RESULTS`` and ``METADATA_GUARDRAIL_ROW_RESULTS``.

    Of that v0.2.0 inventory, ``METADATA_DATA_CATALOGUE``,
    ``METADATA_DATA_PROFILED``, ``METADATA_DATA_PROFILED_FREQUENCY``, and
    ``METADATA_DATA_LINEAGE`` are Live schemas with compatibility guarantees.
    Every other metadata schema in the registry remains Preview.

    Detailed table contents:

    - ``METADATA_DATA_STEWARD`` is a person registry storing ``steward_id``,
      ``steward_name``, ``steward_role``, ``contact``, ``is_active``,
      ``custom_fields_json``, and the standard audit fields. Responsibility
      effective periods remain on ``METADATA_DATA_AGREEMENT``.
    - ``METADATA_DATA_AGREEMENT`` stores ``agreement_id``,
      ``agreement_version``, ``agreement_name``, ``domain``,
      ``provider_steward_id``, ``recipient_steward_id``, ``recipient``,
      ``start_date``, ``expiry_date``, ``business_purpose``,
      ``custom_fields_json``, and the standard audit fields.
    - ``METADATA_DATA_CONTRACT`` first stores a payload-free draft identity
      through ``contract_id``, ``contract_version``, the exact ``agreement_id``
      and ``agreement_version``, and ``table_id``. Freezing the draft assembles
      ``contract_payload_json``; lifecycle status, activation state, and the
      standard audit fields complete the row.
    - ``METADATA_DATA_CATALOGUE`` stores the current structural registry through
      ``metadata_level``, ``table_id``, ``column_id``, ``environment_name``,
      physical table context, ``column_name``, ``data_type``, profiling dates,
      activation state, and the standard audit fields.
    - ``METADATA_DATA_PROFILED`` stores ``profile_id``,
      ``profile_snapshot_id``, ``table_id``, ``column_id``,
      ``environment_name``, ``data_type``,
      ``row_count``, ``non_null_count``, ``null_count``, ``null_percent``,
      ``distinct_count``, ``distinct_percent``, ``mean_value``,
      ``stddev_value``, ``min_value``, ``percentile_25_value``,
      ``median_value``, ``percentile_75_value``, ``max_value``,
      and the standard audit fields.
    - ``METADATA_DATA_PROFILED_FREQUENCY`` stores frequency rows through
      ``frequency_id``, ``profile_id``, ``profile_snapshot_id``, value, count,
      percentage, rank, profiled row totals, and the standard audit fields.
    - ``METADATA_DATA_LINEAGE`` stores ``lineage_id``, canonical ``table_id``,
      ``environment_name``, ``pipeline_role``, and the
      standard audit fields.
    - ``METADATA_DATA_ACCESS`` stores access scope, role, permission,
      approval, expiry, table and column identity, and audit information.
    - ``METADATA_ENRICHMENT`` stores business metadata enrichment,
      classification, sensitivity, ownership, governance review, activation,
      effective dates, and audit information.
    - ``METADATA_GUARDRAIL`` stores guardrail rule identity, scope,
      parameters, severity, lifecycle, governance review, approval, effective
      dates, and audit information.
    - ``METADATA_GUARDRAIL_RESULTS`` stores guardrail execution results,
      status, continuation decision, expected and actual values, result
      payload, and audit information.
    - ``METADATA_GUARDRAIL_ROW_RESULTS`` stores compact failed-row and failed
      DQ-rule evidence linked to its rule/run summary without copying complete
      source rows.

    Standard audit fields are ``_committed_by``, ``_committed_at``,
    ``_workspace_id``, ``_workspace_name``, ``_notebook_id``,
    ``_notebook_name``, ``_metadata_lakehouse_name``, and ``_activity_id``.

    Existing tables are validated for required column names and
    compatible Spark data types. Physical Spark/Delta nullability is
    intentionally not compared because persisted Fabric tables may report
    fields as nullable regardless of the canonical logical requirement. The
    legacy ``frequency_json`` column specifically fails
    ``METADATA_DATA_PROFILED`` validation; unrelated
    metadata tables continue to permit additive columns.
    Because normalized frequency persistence is a breaking physical-schema
    change, existing metadata tables may need recreation through this setup
    flow; no automatic migration is performed.
    Existing tables are not automatically overwritten merely because they
    already exist. Missing columns or incompatible types mark that table as
    failed, processing continues for remaining metadata tables, and
    ``raise_on_failure=True`` raises only after all tables have been processed
    when failures exist.

    A missing table is created by writing an empty Spark DataFrame with the
    required FabricOps table structure. This creates the metadata table structure but
    does not populate business metadata records. The function does not
    automatically create steward records, agreements, contracts, catalogue
    records, profile records, lineage events, access assignments, enrichment
    records, guardrail rules, or guardrail results; those are populated by
    their respective FabricOps workflows.

    """
    normalized = validate_framework_config(config)
    metadata_store = get_store(config=normalized, env=env, target="metadata")
    if getattr(metadata_store, "kind", None) != "lakehouse":
        raise ValueError(f"Target '{env}/metadata' is not a lakehouse store.")
    if metadata_store.schema_enabled is not True:
        raise ValueError("FabricOps Metadata Lakehouse must be schema-enabled.")
    context = {"config": normalized, "env": env}
    registry = metadata_table_schema_registry()

    table_results: dict[str, dict[str, Any]] = {}
    created_tables: list[str] = []
    validated_tables: list[str] = []
    failed_tables: list[str] = []

    total_tables = len(registry)
    steward_table = None

    for index, (table_name, schema) in enumerate(registry.items(), start=1):
        resolved_metadata_schema = metadata_table_physical_schema(normalized, table_name)
        try:
            created = False
            try:
                table = read_lakehouse_table_core(
                    table_name, target="metadata", schema=resolved_metadata_schema, spark_session=spark, context=context
                )
            except Exception as exc:
                if not is_table_not_found_error(exc):
                    raise RuntimeError(
                        f"Unable to read metadata table {table_name!r}. Original {type(exc).__name__}: {exc}"
                    ) from exc
                empty_frame = spark.createDataFrame([], schema=schema)
                write_lakehouse_table_core(
                    empty_frame,
                    table_name,
                    target="metadata",
                    schema=resolved_metadata_schema,
                    mode="overwrite",
                    verbose=False,
                    context=context,
                )
                created = True
                table = read_lakehouse_table_core(
                    table_name, target="metadata", schema=resolved_metadata_schema, spark_session=spark, context=context
                )
            if table is not None and hasattr(table, "schema"):
                _validate_existing_metadata_schema(table_name, table.schema, schema)
            else:
                columns = list(getattr(table, "columns", []) or []) if table is not None else []
                missing = [field for field in metadata_table_field_names(schema) if field not in columns]
                if missing:
                    raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing)}.")
            if table_name == "METADATA_DATA_STEWARD":
                steward_table = table
            if created:
                created_tables.append(table_name)
                table_results[table_name] = _result(table_name, "created", "Metadata table was created and validated.")
                if verbose:
                    print(f"[{index}/{total_tables}] Created {table_name}\n")
            else:
                validated_tables.append(table_name)
                table_results[table_name] = _result(
                    table_name, "validated", "Existing metadata table schema is compatible."
                )
        except Exception as exc:  # continue after per-table failures
            failed_tables.append(table_name)
            table_results[table_name] = _result(table_name, "failed", f"{exc}", error_type=type(exc).__name__)
            if verbose:
                print(f"[{index}/{total_tables}] Failed {table_name}")
                print(f"       {exc}\n")

    active_stewards = _active_steward_presence(steward_table)

    successful = created_tables + validated_tables
    status = "ready" if not failed_tables else ("partial_failure" if successful else "failed")
    data_agreement_tables = [
        "METADATA_DATA_STEWARD", "METADATA_DATA_AGREEMENT", "METADATA_DATA_CONTRACT",
    ]
    data_agreement_failed = [table for table in data_agreement_tables if table in failed_tables]
    data_agreement = {
        "status": "failed" if data_agreement_failed else ("ready" if active_stewards else "not_ready"),
        "tables": data_agreement_tables,
        "created_tables": [table for table in data_agreement_tables if table in created_tables],
        "validated_tables": [table for table in data_agreement_tables if table in validated_tables],
        "failed_tables": data_agreement_failed,
        "active_steward_count": active_stewards,
    }
    if require_active_steward and not active_stewards:
        raise ValueError("METADATA_DATA_STEWARD has no active steward rows yet.")
    governance_tables = list(GOVERNANCE_METADATA_TABLES)
    governance_failed = [table for table in governance_tables if table in failed_tables]
    governance = {
        "status": "failed" if governance_failed else "ready",
        "tables": governance_tables,
        "created_tables": [table for table in governance_tables if table in created_tables],
        "validated_tables": [table for table in governance_tables if table in validated_tables],
        "failed_tables": governance_failed,
    }
    engineering_tables = list(ENGINEERING_METADATA_TABLES)
    engineering_failed = [table for table in engineering_tables if table in failed_tables]
    engineering = {
        "status": "failed" if engineering_failed else "ready",
        "tables": engineering_tables,
        "created_tables": [table for table in engineering_tables if table in created_tables],
        "validated_tables": [table for table in engineering_tables if table in validated_tables],
        "failed_tables": engineering_failed,
    }
    metadata_schemas = {
        "governance": normalized.governance_metadata_schema,
        "engineering": normalized.engineering_metadata_schema,
    }
    fully_qualified_tables = [f"{metadata_table_physical_schema(normalized, table)}.{table}" for table in registry]
    result = {
        "status": status,
        "data_agreement": data_agreement,
        "governance": governance,
        "tables": list(registry),
        "table_results": table_results,
        "metadata_schemas": metadata_schemas,
        "engineering": engineering,
        "fully_qualified_tables": fully_qualified_tables,
        "created_tables": created_tables,
        "validated_tables": validated_tables,
        "failed_tables": failed_tables,
        "created_or_checked_tables": successful,
        "warnings": [],
        "active_metadata_tables": successful,
        "active_metadata_table_count": len(successful),
    }
    if verbose:
        _print_setup_summary(
            total=total_tables,
            created=created_tables,
            validated=validated_tables,
            failed=failed_tables,
            table_results=table_results,
            active_stewards=active_stewards,
        )
    if raise_on_failure and failed_tables:
        detail = "; ".join(f"{table}: {table_results[table]['message']}" for table in failed_tables)
        raise RuntimeError(f"FabricOps metadata setup failed for {len(failed_tables)} table(s): {detail}")
    return result


__all__ = ["setup_metadata_tables"]

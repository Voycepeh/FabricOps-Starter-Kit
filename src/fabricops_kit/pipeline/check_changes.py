"""Public deterministic changes check."""

from datetime import date, datetime
import json
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import get_store, is_table_not_found_error, resolve_fabric_context
from fabricops_kit.io.shared import configured_lakehouse_schema, read_lakehouse_table_core, write_lakehouse_table_core
from fabricops_kit.pipeline.guardrails_shared import (
    changes_check_core,
    evaluate_changes_guardrail,
    load_table_guardrail_rules,
    resolve_guardrail_change_behaviour,
    select_table_guardrail_rule,
    write_guardrail_result_row,
)

_OBSERVATION_TABLE = "METADATA_SOURCE_OBSERVATION"
_OBSERVATION_COLUMNS = {
    "metadata_table_key", "source_target", "source_schema", "source_table",
    "partition_column", "partition_value", "change_column", "row_count",
    "min_change_value", "max_change_value", "is_present", "observed_at",
}


def _rows(dataframe) -> list[dict[str, Any]]:
    values = dataframe.collect() if hasattr(dataframe, "collect") else dataframe
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in values]


def _is_observation(dataframe) -> bool:
    columns = set(getattr(dataframe, "columns", ()))
    if not columns and isinstance(dataframe, (list, tuple)) and dataframe:
        columns = set(dict(dataframe[0]))
    return _OBSERVATION_COLUMNS <= columns


def _previous_observation(history, *, identity: str, partition_column: str, change_column: str, observed_at) -> list[dict[str, Any]]:
    if hasattr(history, "where") and hasattr(history, "agg"):
        from pyspark.sql import functions as F

        comparable = history.where(
            (F.col("metadata_table_key") == identity)
            & (F.col("partition_column") == partition_column)
            & (F.col("change_column") == change_column)
            & (F.col("observed_at") < F.lit(observed_at))
        )
        timestamp_rows = comparable.agg(F.max("observed_at").alias("previous_observed_at")).collect()
        previous_at = timestamp_rows[0]["previous_observed_at"] if timestamp_rows else None
        if previous_at is None:
            return []
        return _rows(comparable.where(F.col("observed_at") == F.lit(previous_at)).select(
            "partition_value", "is_present", "row_count", "min_change_value",
            "max_change_value", "observed_at",
        ))
    candidates = [row for row in _rows(history) if (
        str(row.get("metadata_table_key")) == identity
        and str(row.get("partition_column")) == partition_column
        and str(row.get("change_column")) == change_column
        and row.get("observed_at") < observed_at
    )]
    previous_at = max((row["observed_at"] for row in candidates), default=None)
    return [row for row in candidates if row["observed_at"] == previous_at]


def _observation_changes(dataframe, *, rules_df=None, metadata_table_key: str = "") -> dict:
    current = _rows(dataframe)
    if not current:
        raise ValueError("observation dataframe must contain at least one row")
    identity = metadata_table_key or str(current[0]["metadata_table_key"])
    partition_column = str(current[0]["partition_column"])
    change_column = str(current[0]["change_column"])
    observed_at = current[0]["observed_at"]
    if any(row["observed_at"] != observed_at for row in current):
        raise ValueError("observation dataframe must contain one shared observed_at snapshot")

    config, env, context = resolve_fabric_context()
    metadata_schema = configured_lakehouse_schema(config, env, "metadata")
    try:
        history = read_lakehouse_table_core(
            _OBSERVATION_TABLE, target="metadata", schema=metadata_schema,
            spark_session=getattr(dataframe, "sparkSession", None), context=context,
        )
        previous = _previous_observation(
            history, identity=identity, partition_column=partition_column,
            change_column=change_column, observed_at=observed_at,
        )
    except Exception as exc:
        if not is_table_not_found_error(exc):
            raise RuntimeError(f"Unable to load table observation history for {identity!r}: {exc}") from exc
        previous = []
    current_by = {str(row["partition_value"]): row for row in current}
    previous_by = {str(row["partition_value"]): row for row in previous}
    new, changed, reappeared = [], [], []
    for value, row in current_by.items():
        prior = previous_by.get(value)
        if prior is None:
            new.append(row["partition_value"])
        elif not prior.get("is_present", True):
            reappeared.append(row["partition_value"])
        elif any(
            prior.get(field) != row.get(field)
            for field in ("row_count", "min_change_value", "max_change_value")
        ):
            changed.append(row["partition_value"])
    removed = [row["partition_value"] for value, row in previous_by.items()
               if row.get("is_present", True) and value not in current_by]

    if removed:
        audit = build_runtime_audit_fields(config=config, env=env, runtime_context=context)
        template = current[0]
        tombstones = [{
            **template, "partition_value": value, "row_count": 0,
            "min_change_value": None, "max_change_value": None,
            "is_present": False, **audit,
        } for value in removed]
        spark = getattr(dataframe, "sparkSession", None)
        tombstone_df = spark.createDataFrame(
            [coerce_metadata_row_types(_OBSERVATION_TABLE, row) for row in tombstones],
            schema=metadata_table_schema_registry()[_OBSERVATION_TABLE],
        )
        write_lakehouse_table_core(
            tombstone_df, _OBSERVATION_TABLE, target="metadata", schema=metadata_schema,
            context=context, mode="append",
        )
    if rules_df is None:
        rules_df = load_table_guardrail_rules(
            config, env, spark_session=getattr(dataframe, "sparkSession", None),
        )
    selected_rule = select_table_guardrail_rule(
        rules_df, guardrail_type="change", metadata_table_key=identity, environment_name=env,
    )
    source_pattern = "snapshot"
    if selected_rule:
        parameters = json.loads(selected_rule.get("rule_parameters_json") or "{}")
        if parameters.get("change_behaviour"):
            _, source_pattern = resolve_guardrail_change_behaviour(parameters["change_behaviour"])
        else:
            source_pattern = str(parameters.get("source_pattern") or "snapshot")
    pattern_result = changes_check_core(
        current, previous or None, key_columns=["partition_value"],
        non_key_columns=["row_count", "min_change_value", "max_change_value", "is_present"],
        source_pattern=source_pattern,
        comparison_scope="partial" if source_pattern == "incremental_append" else "complete",
    )
    has_changes = not previous or bool(new or changed or removed or reappeared)
    result = {
        "status": "changed" if has_changes else "unchanged", "can_continue": True,
        "check_type": "changes", "guardrail_type": "change", "changed": has_changes,
        "first_observation": not previous, "new_partitions": new,
        "changed_partitions": changed, "removed_partitions": removed,
        "reappeared_partitions": reappeared,
        "affected_partitions": [*new, *changed, *removed, *reappeared],
        "source_pattern": source_pattern,
        "pattern_semantics": pattern_result["pattern_semantics"],
        "append_violation_count": pattern_result["append_violation_count"],
        "reason": "First observation baseline created." if not previous else
                  ("Source observation changed." if has_changes else "Source observation is unchanged."),
    }
    if rules_df is not None:
        result["metadata_table_key"] = identity
        result = evaluate_changes_guardrail(
            result, rules_df=rules_df, table_name=str(current[0]["source_table"]),
            environment_name=env, metadata_table_key=identity,
        )
        if result.get("rule_key"):
            source_target = str(current[0]["source_target"])
            source_store_type = str(get_store(config, env, source_target).kind).lower()
            write_guardrail_result_row(
                spark_session=getattr(dataframe, "sparkSession", None), config=config, env=env,
                run_id=str(observed_at), dataset_name="", table_name=str(current[0]["source_table"]),
                store_type=source_store_type, layer=source_target,
                schema_name=current[0].get("source_schema"), guardrail_type="change",
                rule_type=str(result.get("rule_type") or "monitor_only"), result=result,
                rule_key=str(result["rule_key"]),
            )
        return result
    return result


def check_changes(
    dataframe,
    previous_dataframe=None,
    *,
    partition_columns: list[str] | tuple[str, ...] | None = None,
    key_columns: list[str] | tuple[str, ...] | None = None,
    non_key_columns: list[str] | tuple[str, ...] | None = None,
    range_column: str | None = None,
    source_pattern: str = "snapshot",
    comparison_scope: str = "complete",
    refresh_days: int = 0,
    version_column: str | None = None,
    reference_date: date | datetime | str | None = None,
    include_row_changes: bool = False,
    rules_df=None,
    metadata_table_key: str = "",
) -> dict:
    """Describe deterministic row and partition changes since an observation.

    Parameters
    ----------
    dataframe : DataFrame or iterable of mappings
        Current source observation.
    previous_dataframe : DataFrame or iterable of mappings, optional
        Previous comparable source observation.
    partition_columns : sequence of str, optional
        Columns defining cheap partition fingerprints.
    key_columns : sequence of str
        Non-null columns that uniquely identify a logical row.
    non_key_columns : sequence of str, optional
        Columns whose content identifies an update. Defaults to all non-key
        columns, except that a versioned source's ``version_column`` is used
        only for latest-record resolution unless explicitly included here.
    range_column : str, optional
        Date, timestamp, or ordered range column used for recent and unseen
        range classification.
    source_pattern : {"snapshot", "incremental_append", "mutable_incremental", "versioned"}
        Explicit source behavior; it is never inferred from table naming.
    comparison_scope : {"complete", "partitions", "partial"}
        Completeness of the current observation. ``complete`` can prove global
        deletions, ``partitions`` can prove deletions only inside supplied
        complete partitions, and ``partial`` never infers deletions.
    refresh_days : int, default=0
        Number of days in the expected mutable window. Zero means only values
        dated on ``reference_date`` are recent.
    version_column : str, optional
        Column used to select the latest row per logical key. Required when
        ``source_pattern="versioned"``.
    reference_date : date, datetime, str, optional
        End of the recent mutable window.
    include_row_changes : bool, default=False
        Include deterministic key hashes grouped by change classification.
    rules_df : DataFrame or iterable of mappings, optional
        Approved source-change rules for the canonical observation path. When
        omitted, the active rule is loaded by ``metadata_table_key``. Its
        ``change_required``, ``no_change_required``, or ``monitor_only`` intent
        governs continuation, and the runtime outcome is written to
        ``METADATA_GUARDRAIL_RESULTS``.
    metadata_table_key : str, optional
        Canonical identity used to scope the previous observation snapshot.

    Returns
    -------
    dict
        Structured changes summary, partition observations, counts, and
        observed ranges. This function does not merge or write target data;
        approved observation rules may write guardrail-result metadata.

    Raises
    ------
    ValueError
        If configuration is invalid or logical keys are null, missing, or
        duplicated.

    Examples
    --------
    >>> result = check_changes(current, previous, key_columns=["id"])
    >>> result["changed"]
    True

    """
    if _is_observation(dataframe):
        if previous_dataframe is not None:
            raise ValueError("previous_dataframe is loaded automatically for canonical observation evidence")
        return _observation_changes(dataframe, rules_df=rules_df, metadata_table_key=metadata_table_key)
    return changes_check_core(
        dataframe,
        previous_dataframe,
        partition_columns=partition_columns,
        key_columns=key_columns,
        non_key_columns=non_key_columns,
        range_column=range_column,
        source_pattern=source_pattern,
        comparison_scope=comparison_scope,
        refresh_days=refresh_days,
        version_column=version_column,
        reference_date=reference_date,
        include_row_changes=include_row_changes,
    )

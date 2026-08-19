"""Public deterministic changes check."""

import json
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import is_table_not_found_error, resolve_fabric_context
from fabricops_kit.io.shared import configured_lakehouse_schema, read_lakehouse_table_core, write_lakehouse_table_core
from fabricops_kit.pipeline.guardrail_shared import (
    evaluate_changes_guardrail,
    load_table_guardrail_rules,
    select_table_guardrail_rule,
)
from fabricops_kit.pipeline.guardrails_shared import (
    changes_check_core,
    resolve_guardrail_change_behaviour,
    write_guardrail_result_row,
)
from fabricops_kit.pipeline.shared import observation_rows

_OBSERVATION_TABLE = "METADATA_SOURCE_OBSERVATION"
_OBSERVATION_COLUMNS = {
    "observation_id",
    "table_id",
    "environment_name",
    "partition_value",
    "row_count",
    "min_change_value",
    "max_change_value",
    "is_present",
    "_committed_at",
    "_activity_id",
}


def _is_source_observation(observation) -> bool:
    columns = set(getattr(observation, "columns", ()))
    if not columns and isinstance(observation, (list, tuple)) and observation:
        columns = set(dict(observation[0]))
    return _OBSERVATION_COLUMNS <= columns


def _previous_observation(history, *, table_id: str, environment_name: str, committed_at) -> list[dict[str, Any]]:
    """Return the latest earlier observation for this table and environment."""
    if hasattr(history, "where") and hasattr(history, "agg"):
        from pyspark.sql import functions as F

        comparable = history.where(
            (F.col("table_id") == table_id)
            & (F.col("environment_name") == environment_name)
            & (F.col("_committed_at") < F.lit(committed_at))
        )
        timestamp_rows = comparable.agg(F.max("_committed_at").alias("previous_committed_at")).collect()
        previous_at = timestamp_rows[0]["previous_committed_at"] if timestamp_rows else None
        if previous_at is None:
            return []
        return observation_rows(
            comparable.where(F.col("_committed_at") == F.lit(previous_at)).select(
                "observation_id",
                "table_id",
                "environment_name",
                "partition_value",
                "is_present",
                "row_count",
                "min_change_value",
                "max_change_value",
                "_committed_at",
                "_activity_id",
            )
        )

    candidates = [
        row
        for row in observation_rows(history)
        if str(row.get("table_id") or "") == table_id
        and str(row.get("environment_name") or "") == environment_name
        and row.get("_committed_at") < committed_at
    ]
    previous_at = max((row["_committed_at"] for row in candidates), default=None)
    return [row for row in candidates if row["_committed_at"] == previous_at]


def _observation_changes(observation) -> dict:
    current = observation_rows(observation)
    if not current:
        raise ValueError("observation dataframe must contain at least one row")

    table_id = str(current[0].get("table_id") or "")
    environment_name = str(current[0].get("environment_name") or "")
    observation_id = str(current[0].get("observation_id") or "")
    committed_at = current[0]["_committed_at"]
    activity_id = str(current[0].get("_activity_id") or "")
    if not table_id or not observation_id or not environment_name or not activity_id:
        raise ValueError(
            "observation dataframe must contain table_id, observation_id, environment_name, and _activity_id"
        )
    if any(row["_committed_at"] != committed_at for row in current):
        raise ValueError("observation dataframe must contain one shared _committed_at snapshot")
    if any(str(row.get("_activity_id") or "") != activity_id for row in current):
        raise ValueError("observation dataframe must contain one shared _activity_id")
    if any(str(row.get("observation_id") or "") != observation_id for row in current):
        raise ValueError("observation dataframe must contain one shared observation_id")
    if any(str(row.get("table_id") or "") != table_id for row in current):
        raise ValueError("observation dataframe must contain one shared table_id")
    if any(str(row.get("environment_name") or "") != environment_name for row in current):
        raise ValueError("observation dataframe must contain one shared environment_name")

    config, env, context = resolve_fabric_context()
    if environment_name != env:
        raise ValueError(
            f"observation environment_name {environment_name!r} does not match active environment {env!r}."
        )
    metadata_schema = configured_lakehouse_schema(config, env, "metadata")
    try:
        history = read_lakehouse_table_core(
            _OBSERVATION_TABLE,
            target="metadata",
            schema=metadata_schema,
            spark_session=getattr(observation, "sparkSession", None),
            context=context,
        )
        previous = _previous_observation(
            history,
            table_id=table_id,
            environment_name=environment_name,
            committed_at=committed_at,
        )
    except Exception as exc:
        if not is_table_not_found_error(exc):
            raise RuntimeError(f"Unable to load table observation history for {table_id!r}: {exc}") from exc
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
    removed = [
        row["partition_value"]
        for value, row in previous_by.items()
        if row.get("is_present", True) and value not in current_by
    ]

    if removed:
        audit = build_runtime_audit_fields(config=config, env=env, runtime_context=context)
        template = current[0]
        tombstones = [
            {
                **template,
                "partition_value": value,
                "row_count": 0,
                "min_change_value": None,
                "max_change_value": None,
                "is_present": False,
                **audit,
            }
            for value in removed
        ]
        spark = getattr(observation, "sparkSession", None)
        tombstone_df = spark.createDataFrame(
            [coerce_metadata_row_types(_OBSERVATION_TABLE, row) for row in tombstones],
            schema=metadata_table_schema_registry()[_OBSERVATION_TABLE],
        )
        write_lakehouse_table_core(
            tombstone_df,
            _OBSERVATION_TABLE,
            target="metadata",
            schema=metadata_schema,
            context=context,
            mode="append",
        )

    rules_df = load_table_guardrail_rules(
        config,
        env,
        spark_session=getattr(observation, "sparkSession", None),
    )
    selected_rule = select_table_guardrail_rule(
        rules_df,
        guardrail_type="change",
        metadata_table_key=table_id,
        environment_name=env,
    )
    if selected_rule is None:
        raise ValueError(f"No active approved change rule exists for {table_id!r}.")
    parameters = json.loads(selected_rule.get("rule_parameters_json") or "{}")
    if parameters.get("change_behaviour"):
        _, source_pattern = resolve_guardrail_change_behaviour(parameters["change_behaviour"])
    else:
        source_pattern = str(parameters.get("source_pattern") or "snapshot")

    pattern_result = changes_check_core(
        current,
        previous or None,
        key_columns=["partition_value"],
        non_key_columns=["row_count", "min_change_value", "max_change_value", "is_present"],
        source_pattern=source_pattern,
        comparison_scope="partial" if source_pattern == "incremental_append" else "complete",
    )
    has_changes = not previous or bool(new or changed or removed or reappeared)
    result = {
        "status": "changed" if has_changes else "unchanged",
        "can_continue": True,
        "check_type": "changes",
        "guardrail_type": "change",
        "changed": has_changes,
        "first_observation": not previous,
        "new_partitions": new,
        "changed_partitions": changed,
        "removed_partitions": removed,
        "reappeared_partitions": reappeared,
        "affected_partitions": [*new, *changed, *removed, *reappeared],
        "source_pattern": source_pattern,
        "pattern_semantics": pattern_result["pattern_semantics"],
        "append_violation_count": pattern_result["append_violation_count"],
        "reason": (
            "First observation baseline created."
            if not previous
            else ("Source observation changed." if has_changes else "Source observation is unchanged.")
        ),
    }
    result = evaluate_changes_guardrail(
        result,
        rules_df=rules_df,
        environment_name=env,
        metadata_table_key=table_id,
    )
    if result.get("guardrail_rule_id"):
        write_guardrail_result_row(
            spark_session=getattr(observation, "sparkSession", None),
            config=config,
            env=env,
            run_id=activity_id,
            dataset_name="",
            table_name="",
            store_type="",
            layer="",
            schema_name=None,
            guardrail_type="change",
            rule_type=str(result.get("rule_type") or "monitor_only"),
            result=result,
        )
    return result


def check_changes(observation) -> dict:
    """Describe deterministic row and partition changes since an observation.
    
    Parameters
    ----------
    observation : pyspark.sql.DataFrame
        Canonical evidence returned by :func:`observe_table`.
    
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
    >>> observation = observe_table("orders", target="source", schema="dbo")
    >>> result = check_changes(observation)
    >>> result["changed"]
    True

    """
    if not _is_source_observation(observation):
        raise ValueError("observation must be canonical evidence returned by observe_table()")
    return _observation_changes(observation)

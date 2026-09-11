"""Public Source Stability Guardrail check."""

import json
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_physical_schema, metadata_table_schema_registry
from fabricops_kit.config.shared import is_table_not_found_error, resolve_fabric_context
from fabricops_kit.io.shared import read_lakehouse_table_core, write_lakehouse_table_core
from fabricops_kit.pipeline.shared import (
    evaluate_source_stability_guardrail,
    load_table_guardrail_rules,
    resolve_catalogue_table_identity,
    resolve_table_processing_definition,
    select_table_guardrail_rule,
)
from fabricops_kit.pipeline.shared import write_guardrail_result_row
from fabricops_kit.pipeline.shared import observation_rows

_OBSERVATION_TABLE = "METADATA_SOURCE_OBSERVATION"
_CONSUMPTION_TABLE = "METADATA_SOURCE_CONSUMPTION"
_OBSERVATION_COLUMNS = {
    "observation_id",
    "table_id",
    "environment_name",
    "partition_value",
    "row_count",
    "min_change_value",
    "max_change_value",
    "content_fingerprint",
    "is_present",
    "_committed_at",
    "_activity_id",
}


def _is_source_observation(observation) -> bool:
    columns = set(getattr(observation, "columns", ()))
    if not columns and isinstance(observation, (list, tuple)) and observation:
        columns = set(dict(observation[0]))
    return _OBSERVATION_COLUMNS <= columns


def _previous_observation(
    history, *, table_id: str, environment_name: str, committed_at, observation_id: str | None = None
) -> list[dict[str, Any]]:
    """Return the latest earlier observation for this table and environment."""
    if hasattr(history, "where") and hasattr(history, "agg"):
        from pyspark.sql import functions as F

        comparable = history.where(
            (F.col("table_id") == table_id)
            & (F.col("environment_name") == environment_name)
            & (F.col("_committed_at") < F.lit(committed_at))
        )
        if observation_id is not None:
            comparable = comparable.where(F.col("observation_id") == observation_id)
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
                "content_fingerprint",
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
        and (observation_id is None or str(row.get("observation_id") or "") == observation_id)
    ]
    previous_at = max((row["_committed_at"] for row in candidates), default=None)
    return [row for row in candidates if row["_committed_at"] == previous_at]


def _observation_stability(
    observation,
    *,
    target_table_id: str,
    successful_observation_id: str | None = None,
    successful_partition_state: dict[str, dict[str, Any]] | None = None,
) -> dict:
    """Return persisted change evidence for one canonical source observation."""
    current = observation_rows(observation)
    if not current:
        raise ValueError("observation dataframe must contain at least one row")

    observed_table_id = str(current[0].get("table_id") or "")
    environment_name = str(current[0].get("environment_name") or "")
    observation_id = str(current[0].get("observation_id") or "")
    committed_at = current[0]["_committed_at"]
    activity_id = str(current[0].get("_activity_id") or "")
    if not observed_table_id or not observation_id or not environment_name or not activity_id:
        raise ValueError(
            "observation dataframe must contain table_id, observation_id, environment_name, and _activity_id"
        )
    if any(row["_committed_at"] != committed_at for row in current):
        raise ValueError("observation dataframe must contain one shared _committed_at snapshot")
    if any(str(row.get("_activity_id") or "") != activity_id for row in current):
        raise ValueError("observation dataframe must contain one shared _activity_id")
    if any(str(row.get("observation_id") or "") != observation_id for row in current):
        raise ValueError("observation dataframe must contain one shared observation_id")
    if any(str(row.get("table_id") or "") != observed_table_id for row in current):
        raise ValueError("observation dataframe must contain one shared table_id")
    if any(str(row.get("environment_name") or "") != environment_name for row in current):
        raise ValueError("observation dataframe must contain one shared environment_name")

    config, env, context = resolve_fabric_context()
    if environment_name != env:
        raise ValueError(
            f"observation environment_name {environment_name!r} does not match active environment {env!r}."
        )
    source_table_id = observed_table_id
    spark_session = getattr(observation, "sparkSession", None)
    identity = resolve_catalogue_table_identity(
        config, env, source_table_id, spark_session=spark_session, context=context,
    )
    table_id = identity["table_id"]
    target_identity = resolve_catalogue_table_identity(
        config, env, str(target_table_id).strip(), spark_session=spark_session, context=context,
    )
    authored_processing = {
        **json.loads(target_identity.get("load_strategy_parameters_json") or "{}"),
        "load_strategy": target_identity.get("load_strategy"),
    }
    processing = resolve_table_processing_definition(
        config,
        env,
        target_identity["table_id"],
        spark_session=spark_session,
        context=context,
        authored_processing=authored_processing,
    )
    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=context)
    notebook_name = str(audit.get("_notebook_name") or "").strip()
    metadata_schema = metadata_table_physical_schema(config, _OBSERVATION_TABLE)
    history = []
    try:
        history = read_lakehouse_table_core(
            _OBSERVATION_TABLE,
            target="metadata",
            schema=metadata_schema,
            spark_session=getattr(observation, "sparkSession", None),
            context=context,
        )
        accepted_observation_id = successful_observation_id
        if accepted_observation_id is None and successful_partition_state is None:
            try:
                consumption = read_lakehouse_table_core(
                    _CONSUMPTION_TABLE,
                    target="metadata",
                    schema=metadata_table_physical_schema(config, _CONSUMPTION_TABLE),
                    spark_session=spark_session,
                    context=context,
                )
                accepted = [
                    row for row in observation_rows(consumption)
                    if str(row.get("notebook_name") or "") == notebook_name
                    and str(row.get("source_table_id") or "") == table_id
                    and str(row.get("target_table_id") or "") == target_identity["table_id"]
                    and str(row.get("environment_name") or "") == environment_name
                    and row.get("_committed_at") < committed_at
                ]
                if accepted:
                    accepted_observation_id = str(
                        max(accepted, key=lambda row: row["_committed_at"])["observation_id"]
                    )
            except Exception as exc:
                if not is_table_not_found_error(exc):
                    raise
        if successful_partition_state is None:
            previous = [] if accepted_observation_id is None else _previous_observation(
                history,
                table_id=table_id,
                environment_name=environment_name,
                committed_at=committed_at,
                observation_id=accepted_observation_id,
            )
        else:
            history_rows = observation_rows(history)
            previous = []
            for bucket, state in successful_partition_state.items():
                published_at = state.get("committed_at")
                candidates = [
                    row for row in history_rows
                    if str(row.get("table_id") or "") == table_id
                    and str(row.get("environment_name") or "") == environment_name
                    and str(row.get("partition_value")) == bucket
                    and row.get("_committed_at") < committed_at
                    and (published_at is None or row.get("_committed_at") <= published_at)
                ]
                if candidates:
                    previous.append(max(candidates, key=lambda row: row["_committed_at"]))
    except Exception as exc:
        if not is_table_not_found_error(exc):
            raise RuntimeError(f"Unable to load table observation history for {table_id!r}: {exc}") from exc
        previous = []

    current_by = {str(row["partition_value"]): row for row in current}
    previous_by = {str(row["partition_value"]): row for row in previous}
    latest_evidence_by: dict[str, dict[str, Any]] = {}
    if successful_partition_state is not None:
        for row in observation_rows(history):
            value = str(row.get("partition_value"))
            if (
                str(row.get("table_id") or "") == table_id
                and str(row.get("environment_name") or "") == environment_name
                and row.get("_committed_at") < committed_at
                and (
                    value not in latest_evidence_by
                    or row["_committed_at"] > latest_evidence_by[value]["_committed_at"]
                )
            ):
                latest_evidence_by[value] = row
    new, changed, reappeared = [], [], []
    for value, row in current_by.items():
        prior = previous_by.get(value)
        if prior is None:
            new.append(row["partition_value"])
        elif not latest_evidence_by.get(value, prior).get("is_present", True):
            reappeared.append(row["partition_value"])
        elif not prior.get("is_present", True):
            reappeared.append(row["partition_value"])
        elif any(
            prior.get(field) != row.get(field)
            for field in ("row_count", "min_change_value", "max_change_value", "content_fingerprint")
        ):
            changed.append(row["partition_value"])
    removed = [
        state["value"]
        for value, state in (successful_partition_state or {}).items()
        if value not in current_by
    ] if successful_partition_state is not None else [
        row["partition_value"] for value, row in previous_by.items()
        if row.get("is_present", True) and value not in current_by
    ]

    if removed:
        template = current[0]
        tombstones = [
            {
                **template,
                "partition_value": value,
                "row_count": 0,
                "min_change_value": None,
                "max_change_value": None,
                "content_fingerprint": None,
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
        table_id=table_id, context=context,
    )
    selected_rule = select_table_guardrail_rule(
        rules_df,
        guardrail_type="source_stability",
        table_id=table_id,
        environment_name=env,
    )
    if selected_rule is None:
        raise ValueError(f"No active approved Source Stability rule exists for {table_id!r}.")
    parameters = json.loads(selected_rule.get("rule_parameters_json") or "{}")

    first_observation = not successful_partition_state if successful_partition_state is not None else not previous
    has_changes = first_observation or bool(new or changed or removed or reappeared)
    result = {
        "table_id": table_id,
        "target_table_id": target_identity["table_id"],
        "environment_name": environment_name,
        "observation_id": observation_id,
        "status": "changed" if has_changes else "unchanged",
        "can_continue": True,
        "check_type": "source_stability",
        "guardrail_type": "source_stability",
        "changed": has_changes,
        "first_observation": first_observation,
        "new_partitions": new,
        "changed_partitions": changed,
        "removed_partitions": removed,
        "reappeared_partitions": reappeared,
        "affected_partitions": [*new, *changed, *removed, *reappeared],
        "partition_column": parameters.get("partition_column"),
        "reason": (
            "First observation baseline created."
            if first_observation
            else ("Source observation changed." if has_changes else "Source observation is unchanged.")
        ),
    }
    result = evaluate_source_stability_guardrail(
        result,
        rules_df=rules_df,
        environment_name=env,
        table_id=table_id,
        load_strategy=processing["load_strategy"],
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
            guardrail_type="source_stability",
            rule_type="historical_mutation",
            result=result,
        )
    return result


def check_source_stability(observation, *, target_table_id: str) -> dict:
    """Validate previously processed source data against the target load strategy.
    
    Parameters
    ----------
    observation : pyspark.sql.DataFrame
        Canonical evidence returned by :func:`observe_table`.
    target_table_id : str
        Governed target identity whose frozen Data Contract supplies the
        authoritative load strategy.
    
    Returns
    -------
    dict
        Source Stability evidence and its compatibility with the governed
        target load strategy. The function never writes target data.
    
    Raises
    ------
    ValueError
        If the observation, Source Stability rule, or target processing is invalid.

    Notes
    -----
    The comparison baseline is the observation referenced by the latest
    ``METADATA_SOURCE_CONSUMPTION`` record for the active logical notebook
    name, source ``table_id``, and ``target_table_id``. Raw observations from
    failed attempts or other source-to-target relationships are not baselines.

    New source data is compatible with append. Mutation, removal, or
    reappearance of previously processed data violates append stability;
    overwrite, SCD1, and SCD2 report that evidence as compatible because their
    governed write semantics can reconcile it. This Guardrail detects and
    validates evidence; it does not execute the load strategy.
    
    Examples
    --------
    >>> observation = observe_table("orders", target="source", schema="dbo")
    >>> result = check_source_stability(observation, target_table_id="lakehouse:unified:dbo:orders")
    >>> result["load_strategy"]
    'append'

    """
    if not _is_source_observation(observation):
        raise ValueError("observation must be canonical evidence returned by observe_table()")
    return _observation_stability(observation, target_table_id=target_table_id)

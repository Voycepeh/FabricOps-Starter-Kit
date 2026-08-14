"""Public deterministic changes check."""

from datetime import date, datetime
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import is_table_not_found_error, resolve_fabric_context
from fabricops_kit.io.shared import configured_lakehouse_schema, read_lakehouse_table_core, write_lakehouse_table_core
from fabricops_kit.pipeline.guardrails_shared import changes_check_core

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


def _observation_changes(dataframe, *, metadata_table_key: str = "") -> dict:
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
        candidates = [row for row in _rows(history) if (
            str(row.get("metadata_table_key")) == identity
            and str(row.get("partition_column")) == partition_column
            and str(row.get("change_column")) == change_column
            and row.get("observed_at") < observed_at
        )]
    except Exception as exc:
        if not is_table_not_found_error(exc):
            raise RuntimeError(f"Unable to load table observation history for {identity!r}: {exc}") from exc
        candidates = []
    previous_at = max((row["observed_at"] for row in candidates), default=None)
    previous = [row for row in candidates if row["observed_at"] == previous_at]
    current_by = {str(row["partition_value"]): row for row in current}
    previous_by = {str(row["partition_value"]): row for row in previous}
    new, changed = [], []
    for value, row in current_by.items():
        prior = previous_by.get(value)
        if prior is None:
            new.append(row["partition_value"])
        elif (not prior.get("is_present", True) or any(
            prior.get(field) != row.get(field)
            for field in ("row_count", "min_change_value", "max_change_value")
        )):
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
    has_changes = not previous or bool(new or changed or removed)
    return {
        "status": "changed" if has_changes else "unchanged", "can_continue": True,
        "check_type": "changes", "guardrail_type": "changes", "changed": has_changes,
        "first_observation": not previous, "new_partitions": new,
        "changed_partitions": changed, "removed_partitions": removed,
        "affected_partitions": [*new, *changed, *removed],
        "reason": "First observation baseline created." if not previous else
                  ("Source observation changed." if has_changes else "Source observation is unchanged."),
    }


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
        Approved change rules for the canonical observation path.
    metadata_table_key : str, optional
        Canonical identity used to scope the previous observation snapshot.

    Returns
    -------
    dict
        Structured changes summary, partition observations, counts, and
        observed ranges. This function does not merge or write target data.

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
        return _observation_changes(dataframe, metadata_table_key=metadata_table_key)
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

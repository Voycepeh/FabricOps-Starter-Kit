"""Owner file for incremental processing-plan selection."""

from typing import Any


def _values(result: dict[str, Any], name: str) -> list[Any]:
    return list(result.get(name) or [])


def plan_incremental_processing(
    changes_result: dict,
    write_strategy: str,
    *,
    partition_column: str | None = None,
    key_columns: list[str] | tuple[str, ...] | None = None,
    effective_column: str | None = None,
) -> dict:
    """Select source read scope and target maintenance from change evidence.

    Parameters
    ----------
    changes_result : dict
        Structured result returned by :func:`check_changes`.
    write_strategy : str
        Target strategy: ``overwrite``, ``append``, ``scd1``, or ``scd2``.
    partition_column : str, optional
        Explicit target partition column. It must represent the same identity
        as the observed source partition column.
    key_columns : list of str or tuple of str, optional
        Business keys required by ``scd1`` and ``scd2``.
    effective_column : str, optional
        Incoming sequence/effective column required by ``scd2``.

    Returns
    -------
    dict
        Deterministic notebook-friendly plan containing ``read_strategy``,
        ``write_strategy``, partition scope, keys, and a reason.

    Raises
    ------
    ValueError
        If the evidence or requested strategy is unsafe or incomplete.

    Notes
    -----
    This function only plans work. It does not read business data or write a
    target. Removed partitions are never translated into implicit deletes.

    Examples
    --------
    >>> plan = plan_incremental_processing(result, "scd1", key_columns=["order_id"])
    >>> plan["read_strategy"]
    'incremental'

    See Also
    --------
    check_changes, read_lakehouse_table

    """
    if not isinstance(changes_result, dict) or "changed" not in changes_result:
        raise ValueError("changes_result must be the structured result returned by check_changes().")
    strategy = str(write_strategy or "").strip().lower()
    if strategy not in {"overwrite", "append", "scd1", "scd2"}:
        raise ValueError("write_strategy must be one of: overwrite, append, scd1, scd2.")
    keys = list(key_columns or [])
    if strategy in {"scd1", "scd2"} and not keys:
        raise ValueError(f"{strategy} requires key_columns.")
    if strategy == "scd2" and not effective_column:
        raise ValueError("scd2 requires effective_column.")
    observed_column = changes_result.get("partition_column")
    if partition_column and observed_column and partition_column != observed_column:
        raise ValueError("partition_column must match the canonical observed partition column.")

    plan = {
        "read_strategy": "skip",
        "write_strategy": strategy,
        "partition_column": partition_column,
        "partition_values": [],
        "key_columns": keys,
        "effective_column": effective_column,
        "reason": "Source is unchanged; no processing is required.",
    }
    if not changes_result["changed"] and not changes_result.get("first_observation"):
        return plan
    if changes_result.get("first_observation"):
        plan.update(read_strategy="full", reason="First observation requires a baseline full load.")
        return plan

    new = _values(changes_result, "new_partitions")
    changed = _values(changes_result, "changed_partitions")
    reappeared = _values(changes_result, "reappeared_partitions")
    removed = _values(changes_result, "removed_partitions")
    if removed:
        if strategy == "overwrite":
            plan.update(read_strategy="full", reason="Removed source partitions require an explicit full overwrite.")
            return plan
        raise ValueError(f"{strategy} cannot safely process removed source partitions without explicit delete semantics.")
    if strategy == "append" and (changed or reappeared):
        raise ValueError("append only supports new partitions; changed or reappeared partitions could duplicate data.")

    affected = [*new, *changed, *reappeared]
    if strategy == "overwrite" and not partition_column:
        plan.update(read_strategy="full", reason="Overwrite has no compatible target partition; using a full overwrite.")
    else:
        plan.update(
            read_strategy="incremental",
            partition_values=affected,
            reason=(
                "Read and overwrite only affected target partitions."
                if strategy == "overwrite"
                else f"Read affected source partitions and apply {strategy}."
            ),
        )
    return plan

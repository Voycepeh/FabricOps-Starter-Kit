"""Public owner for the standard governed source lifecycle."""
from __future__ import annotations
from typing import Any
from fabricops_kit.pipeline.check_dq import check_dq
from fabricops_kit.pipeline.check_grain import check_grain
from fabricops_kit.pipeline.check_freshness import check_freshness
from fabricops_kit.pipeline.check_schema import check_schema
from fabricops_kit.pipeline.pipeline_read import pipeline_read
from fabricops_kit.pipeline.profile_table import profile_table
from fabricops_kit.pipeline.shared import (
    ExecutionSummary,
    _run_orchestration_stage,
    prepare_pipeline_execution,
    pipeline_guardrail_types,
    print_pipeline_contract,
)
from fabricops_kit.pipeline.resolve_table_id import resolve_table_id


def orchestrate_read(*, store: str, schema: str | None, table_name: str, read_mode: str = "full", query: str | None = None, read_parameters: dict[str, Any] | None = None, target_table_id: str | None = None, frequency_enabled: bool = True, frequency_top_n: int | None = 5, spark_session=None, verbose: bool = True) -> dict[str, Any]:
    """Execute the standard FabricOps governed Read lifecycle.

    Parameters
    ----------
    store : str
        Configured source store key.
    schema : str or None
        Physical source schema. This keyword is required; pass None for a store
        without schemas.
    table_name : str
        Physical source table name.
    read_mode : {"full", "incremental"}, default="full"
        Source read behaviour forwarded to the internal Read stage.
    query : str, optional
        Read-only Warehouse query forwarded to the internal Read stage.
    read_parameters : dict, optional
        Incremental configuration, for example {"watermark_column": "modified_datetime"}.
        A selected Data Contract must agree with the supplied watermark. Required
        for incremental mode when no selected contract supplies the watermark.
    target_table_id : str, optional
        Governed target identity required for incremental reads.
    frequency_enabled : bool, default=True
        Whether to calculate frequency distributions for this table.
    frequency_top_n : int or None, default=5
        Maximum ranked frequency values per eligible column; None retains all.
    spark_session : object, optional
        Spark session used by every stage.
    verbose : bool, default=True
        Print stage start, outcome, duration, and failure attribution.

    Returns
    -------
    dict
        The source-read result, including ``dataframe`` and ``table_id``,
        plus capability results and ``orchestration_stages``. ``read_metrics``
        contains ``rows_read`` and ``columns`` (None when unavailable).
        ``total_duration_seconds`` is the full lifecycle wall-clock duration.

    Raises
    ------
    RuntimeError
        If a stage fails. Its name is reported and the original exception is
        retained as ``__cause__``.

    Notes
    -----
    Read resolves its Data Contract once, then runs only its configured
    Freshness, Schema, Grain, and Data Quality stages before Profile, matching
    canonical ``02_pipeline``. Absent capability fields remain skipped in the
    returned result; orchestration_stages and stdout show executed stages only.
    A contract-free Development run prints one concise Guardrail decision.
    Grain checks only the returned rows (the incremental batch in incremental mode),
    using the configured physical row key; SCD2 history requires a version-aware
    key, such as business key plus effective timestamp.
    Incremental batches include only rows after the accepted watermark and at
    or below the upper watermark observed for this run. Bootstrap reads use
    the same upper bound and retain null-watermark rows. Later arrivals above
    that bound wait for the next run. This bounds progress, but does not make
    concurrent source updates a transactional snapshot.
    Incremental progress captures one aggregate summary per source, including
    empty-source evidence; Source Drift fingerprints remain independent.
    DataFrames are never displayed. Incremental batches are not profiled.
    With verbose=True, successful execution ends with a READ Summary on stdout.
    Counts reuse existing profiling results; no Spark action is added for
    reporting. An unavailable count is printed as ``Not available``.

    Examples
    --------
    >>> source = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
    >>> orders_df = source["dataframe"]

    See Also
    --------
    orchestrate_write, profile_table

    """
    summary = ExecutionSummary("READ", verbose=verbose)
    table_id = resolve_table_id(store=store, schema=schema, table_name=table_name)
    context = prepare_pipeline_execution([table_id], spark_session=spark_session)
    active = pipeline_guardrail_types(context, table_id)
    labels = [("freshness", "Freshness"), ("schema", "Schema"), ("grain", "Grain"), ("data_quality", "Data Quality")]
    names = ["Read", *[label for kind, label in labels if kind in active]]
    if read_mode == "full":
        names.append("Profile")
    stages = []
    if verbose:
        print(f"FabricOps READ · {table_name}")
    print_pipeline_contract(context, table_id, operation="Read", guardrails=[label for kind, label in labels if kind in active], verbose=verbose)
    def run(stage, function):
        result, record = _run_orchestration_stage(operation="READ", name=table_name, index=names.index(stage)+1, total=len(names), stage=stage, function=function, verbose=verbose)
        stages.append(record)
        return result
    source = run("Read", lambda: pipeline_read(store=store, schema=schema, table_name=table_name, read_mode=read_mode, query=query, read_parameters=read_parameters, target_table_id=target_table_id, spark_session=spark_session, verbose=False, context=context))
    reader_name = source.pop("_reader_name", None)
    metrics = dict(source.get("read_metrics") or {})
    metrics.setdefault("rows_read", None)
    columns = getattr(source["dataframe"], "columns", None)
    metrics.setdefault("columns", len(columns) if columns is not None else None)
    summary.details([("Physical reader", reader_name), ("Rows read", metrics["rows_read"]), ("Columns", metrics["columns"])])
    dataframe, table_id = source["dataframe"], source["table_id"]
    skipped = {"status": "skipped", "can_continue": True, "checks": []}
    freshness = run("Freshness", lambda: check_freshness(table_id, spark_session=spark_session, verbose=False, context=context)) if "freshness" in active else dict(skipped)
    schema_result = run("Schema", lambda: check_schema(dataframe, table_id=table_id, spark_session=spark_session, verbose=False, context=context)) if "schema" in active else dict(skipped)
    grain_result = run("Grain", lambda: check_grain(dataframe, table_id=table_id, scope="read_full" if read_mode == "full" else "read_incremental_batch", spark_session=spark_session, verbose=False, context=context)) if "grain" in active else dict(skipped)
    dq_result = run("Data Quality", lambda: check_dq(dataframe, table_id=table_id, spark_session=spark_session, verbose=False, context=context)) if "data_quality" in active else dict(skipped)
    profile = run("Profile", lambda: profile_table(dataframe=dataframe, store=store, schema=schema, table_name=table_name, frequency_enabled=frequency_enabled, frequency_top_n=frequency_top_n, spark_session=spark_session)) if read_mode == "full" else dict(skipped, reason="Incremental batch")
    if metrics["rows_read"] is None and read_mode == "full":
        metrics["rows_read"] = profile.get("row_count")
    duration = summary.finish([
        ("Source", ".".join(str(part) for part in (store, schema, table_name) if part)),
        ("Rows read", metrics["rows_read"]), ("Columns", metrics["columns"]),
    ])
    return {**source, "read_metrics": metrics, "total_duration_seconds": duration, "freshness_result": freshness, "schema_result": schema_result, "grain_result": grain_result, "dq_result": dq_result, "profile_result": profile, "orchestration_stages": stages}

"""Public owner for the standard governed target lifecycle."""
from __future__ import annotations
from typing import Any, Iterable
from fabricops_kit.pipeline.check_dq import check_dq
from fabricops_kit.pipeline.check_grain import check_grain
from fabricops_kit.pipeline.check_guardrail_coverage import check_guardrail_coverage
from fabricops_kit.pipeline.check_schema import check_schema
from fabricops_kit.pipeline.check_sensitive_data import check_sensitive_data
from fabricops_kit.pipeline.check_source_drift import check_source_drift
from fabricops_kit.pipeline.pipeline_write import pipeline_write
from fabricops_kit.pipeline.profile_table import profile_table
from fabricops_kit.pipeline.resolve_table_id import resolve_table_id
from fabricops_kit.pipeline.shared import (
    ExecutionSummary,
    _run_orchestration_stage,
    prepare_pipeline_execution,
    pipeline_guardrail_types,
    print_pipeline_contract,
    record_contract_validation,
)


def orchestrate_write(dataframe: Any, *, sources: Iterable[dict[str, Any]], store: str, schema: str | None, table_name: str, write_mode: str, write_parameters: dict[str, Any] | None = None, contracts: dict[str, Any] | None = None, repartition_by: int | None = None, grain_discovery_enabled: bool = True, grain_discovery_max_columns: int = 3, grain_discovery_max_candidates: int = 8, frequency_enabled: bool = True, frequency_top_n: int | None = 5, existing_mapping=None, spark_session=None, verbose: bool = True, dq_diagnostics: str = "sample") -> dict[str, Any]:
    """Execute the standard FabricOps governed Write lifecycle.

    Parameters
    ----------
    dataframe : object
        Transformed Spark DataFrame to validate and publish.
    sources : iterable of dict
        Governed source results containing ``table_id``. Pass [] for a source-free
        target.
    store : str
        Configured destination store key.
    schema : str or None
        Physical target schema. This keyword is required; pass None for a store
        without schemas.
    table_name : str
        Physical target table name.
    write_mode : str
        Notebook-facing Write mode forwarded to the internal Write stage as its governed load strategy.
    write_parameters : dict, optional
        Parameters for the selected Write mode, forwarded to the internal Write stage
        as ``load_strategy_parameters``. For example, SCD1 requires
        ``key_columns``; SCD2 requires ``key_columns`` and ``effective_column``
        and may also define ``tracked_columns``.
    contracts : dict, optional
        ``widget_select_data_contract`` result used to choose Validate or
        Enforce publication behaviour. Both modes run the same Guardrails.
    repartition_by : int, optional
        Spark write partition count.
    grain_discovery_enabled : bool, default=True
        Whether Profile discovers candidate Grain keys for this call. False skips
        discovery and preserves saved candidates; contract Grain checks still run.
    grain_discovery_max_columns : int, default=3
        Maximum columns in a candidate key. 1 checks single columns only; 2
        also checks pairs. Must be a positive integer. Wider searches can be costly.
    grain_discovery_max_candidates : int, default=8
        Maximum candidate keys to retain at the smallest valid key width.
        Must be a positive integer. Discovery stops after enough keys are found;
        this limit does not cap work when no valid key exists.
    frequency_enabled : bool, default=True
        Whether Profile calculates frequency distributions for this call.
        The caller controls when to enable discovery and frequency profiling.
    frequency_top_n : int or None, default=5
        Maximum ranked frequency values per eligible column; None retains all.
    existing_mapping : pyspark.sql.DataFrame, optional
        Previously returned Sensitive Data token mappings. Existing assignments
        are reused; the returned sensitive_result contains the support_mapping
        for the caller to persist and supply on later runs. After consuming the
        prepared DataFrame and persisting the mapping, call its unpersist()
        method to release its cache. Failed orchestration releases it automatically.
    spark_session : object, optional
        Spark session used by every stage.
    verbose : bool, default=True
        Print stage start, outcome, duration, and failure attribution.

    dq_diagnostics : {"sample", "none", "full"}, default="sample"
        Sample captures at most ten illustrative source records per DQ rule
        with exact metrics in the same aggregation. None captures metrics only.
        Full also returns every failure as a lazy diagnostic DataFrame.

    Returns
    -------
    dict
        Write identity and capability results. The top-level ``dataframe`` is
        the prepared input after Sensitive Data treatment, in both Validate
        and Enforce modes. It is the Write input, not necessarily the persisted
        target after Append, SCD1, or SCD2. ``sensitive_result`` retains its
        nested ``dataframe`` result. ``published`` is false when a Validate-mode
        contract passes without publication. ``write_metrics`` retains the
        internal Write measurements, with ``total_target_rows`` reused from
        persisted-target profiling when available. It never treats prepared
        input rows or profiled target rows as committed rows.
        ``total_duration_seconds`` measures the complete lifecycle, including
        Guardrails, metadata finalization, and profiling.

    Raises
    ------
    ValueError
        If a discovery limit is not a positive integer; checked before any stage runs.
    RuntimeError
        If any stage fails. Its name is reported and the original exception is
        retained as ``__cause__``.

    Notes
    -----
    Both contract modes evaluate the same configured Guardrails using contracts
    and rules resolved once per call. Absent Guardrails remain skipped in the
    result fields but are omitted from stdout and orchestration_stages.
    Contract-free Development prints one decision and proceeds to Write.
    DQ summaries retain exact observed pass/fail counts independently of the
    authored tolerance decision. Sample mode stores at most ten illustrative
    source records per rule in METADATA_GUARDRAIL_RESULTS.result_payload_json;
    dq_result["failed_values"] contains only those captured examples. None
    suppresses examples; full returns an unbounded lazy failure DataFrame.
    dq_result["dataframe"] retains lazy row tags. The top-level source/prepared
    DataFrame and published target do not acquire those tags automatically.
    Validate resolves the exact selected frozen candidate and records
    execution_type=validate evidence for activation, including a completion
    record for every covered contract after Guardrail Coverage passes, then returns without writing;
    Enforce continues through Write and persisted-target Profile. Existing
    metadata and Source Observation commit behaviour remains owned by
    the internal Write stage. The returned ``dataframe`` is the prepared Write input,
    not a reread of the persisted target; Append, SCD1, and SCD2 may produce a
    different target state. Grain checks the prepared input after Sensitive Data
    treatment for every strategy; it does not check existing target rows or
    guarantee resulting-table uniqueness for Append, SCD1, or SCD2. SCD strategies
    retain their separate business-key requirements and reject null business-key
    components before staging or merging. Use a version-aware Grain
    key for SCD2 history. No DataFrame is displayed or materialized for this
    return value. With verbose=True, every successful execution prints a final
    WRITE Summary to stdout, including Validate-only runs. Unavailable row
    metrics print as ``Not available``. Reporting adds no Spark actions.

    Examples
    --------
    >>> result = orchestrate_write(
    ...     transformed_df, sources=[orders], store="Silver", schema="demo",
    ...     table_name="curated_orders", write_mode="overwrite", contracts=CONTRACTS,
    ... )

    Development SCD1 with a source-free mapping table:

    >>> result = orchestrate_write(
    ...     product_mapping_df, sources=[], store="Silver", schema="demo",
    ...     table_name="product_mapping", write_mode="scd1",
    ...     write_parameters={"key_columns": ["product_id"]},
    ... )

    Discovery and frequency switches apply only when the lifecycle runs Profile.
    Pass ``grain_discovery_enabled=False, frequency_enabled=False`` on routine
    calls and enable either option on calls chosen by your own scheduler.

    See Also
    --------
    orchestrate_read, profile_table

    """
    for name, value in (
        ("grain_discovery_max_columns", grain_discovery_max_columns),
        ("grain_discovery_max_candidates", grain_discovery_max_candidates),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer.")
    if dq_diagnostics not in {"none", "sample", "full"}:
        raise ValueError("dq_diagnostics must be 'none', 'sample', or 'full'.")
    summary = ExecutionSummary("WRITE", verbose=verbose)
    target = ".".join(str(part) for part in (store, schema, table_name) if part)
    source_ids = [source["table_id"] for source in sources]
    target_id = resolve_table_id(store=store, schema=schema, table_name=table_name)
    contract = (contracts or {}).get("tables", {}).get(target_id) or {}
    contract_mode = str(contract.get("mode") or "enforce").strip().lower()
    context = prepare_pipeline_execution([target_id, *source_ids], contracts=contracts, spark_session=spark_session)
    active = pipeline_guardrail_types(context, target_id)
    drift_ids = [source_id for source_id in source_ids if "source_drift" in pipeline_guardrail_types(context, source_id)]
    governed = any(context["_pipeline_contracts"].values())
    names = []
    if "schema" in active:
        names.append("Schema")
    if "sensitive_data" in active:
        names.append("Sensitive Data")
    if drift_ids:
        names.append("Source Drift")
    if "grain" in active:
        names.append("Grain")
    if "data_quality" in active:
        names.append("Data Quality")
    if governed:
        names.append("Guardrail Coverage")
    if contract_mode != "validate":
        names.extend(["Write", "Profile"])
    stages = []
    if verbose:
        print(f"FabricOps WRITE · {table_name}")
    print_pipeline_contract(context, target_id, operation="Write", guardrails=[name for name in names if name not in {"Write", "Profile", "Guardrail Coverage"}], verbose=verbose)
    def run(stage, function):
        result, record = _run_orchestration_stage(operation="WRITE", name=table_name, index=names.index(stage)+1, total=len(names), stage=stage, function=function, verbose=verbose)
        stages.append(record)
        return result
    skipped = {"status": "skipped", "can_continue": True, "checks": []}
    sensitive = {**skipped, "dataframe": dataframe, "support_mapping": None}
    try:
        schema_result = run("Schema", lambda: check_schema(dataframe, table_id=target_id, spark_session=spark_session, verbose=False, context=context, execution_type=contract_mode)) if "schema" in active else dict(skipped)
        if "sensitive_data" in active:
            sensitive = run("Sensitive Data", lambda: check_sensitive_data(dataframe, table_id=target_id, existing_mapping=existing_mapping, spark_session=spark_session, verbose=False, context=context, execution_type=contract_mode))
        prepared = sensitive["dataframe"]
        drift = run("Source Drift", lambda: [check_source_drift(source_id, target_table_id=target_id, spark_session=spark_session, verbose=False, context=context, execution_type=contract_mode) if source_id in drift_ids else dict(skipped) for source_id in source_ids]) if drift_ids else [dict(skipped) for _ in source_ids]
        grain_result = run("Grain", lambda: check_grain(prepared, table_id=target_id, scope="write_prepared_input", spark_session=spark_session, verbose=False, context=context, execution_type=contract_mode)) if "grain" in active else dict(skipped)
        dq_result = run("Data Quality", lambda: check_dq(prepared, table_id=target_id, spark_session=spark_session, verbose=False, context=context, execution_type=contract_mode, diagnostics=dq_diagnostics)) if "data_quality" in active else dict(skipped)
        coverage = run("Guardrail Coverage", lambda: check_guardrail_coverage(target_table_id=target_id, source_table_ids=source_ids, spark_session=spark_session, verbose=False, context=context)) if governed else dict(skipped)
        common_results = {
            "table_id": target_id,
            "schema_result": schema_result,
            "sensitive_result": sensitive,
            "source_drift_results": drift,
            "grain_result": grain_result,
            "dq_result": dq_result,
            "coverage_result": coverage,
            "orchestration_stages": stages,
        }
        if contract_mode == "validate":
            record_contract_validation(context=context, target_table_id=target_id, coverage=coverage, spark_session=spark_session)
            columns = getattr(prepared, "columns", None)
            metrics = {"input_columns": len(columns) if columns is not None else None, "input_rows": None, "rows_committed": 0, "total_target_rows": None,
                       "rows_inserted": 0, "rows_updated": 0, "rows_unchanged": None,
                       "versions_inserted": 0, "versions_expired": 0,
                       "measurement_source": "validation_only"}
            duration = summary.finish([("Target", target), ("Strategy", write_mode.title()), ("Published", "No"), ("Rows committed", 0)])
            return {
                "write_metrics": metrics,
                "strategy": write_mode,
                "total_duration_seconds": duration,
                **common_results,
                "dataframe": prepared,
                "published": False,
                "validation_passed": True,
            }
        write_result = run("Write", lambda: pipeline_write(prepared, store=store, schema=schema, table_name=table_name, load_strategy=write_mode, load_strategy_parameters=write_parameters, source_table_ids=source_ids, repartition_by=repartition_by, spark_session=spark_session, verbose=False, context=context))
        metrics = dict(write_result.get("write_metrics") or {})
        for key in ("input_rows", "rows_committed", "total_target_rows", "rows_inserted", "rows_updated", "rows_unchanged", "versions_inserted", "versions_expired", "measurement_source"):
            metrics.setdefault(key, None)
        strategy = write_result.get("strategy", write_mode)
        columns = getattr(prepared, "columns", None)
        metrics.setdefault("input_columns", len(columns) if columns is not None else None)
        summary.details([("Strategy", strategy.title()), ("Target", target), ("Rows committed", metrics["rows_committed"]), ("Columns", metrics["input_columns"])])
        profile = run("Profile", lambda: profile_table(table_id=write_result["table_id"], grain_discovery_enabled=grain_discovery_enabled, grain_discovery_max_columns=grain_discovery_max_columns, grain_discovery_max_candidates=grain_discovery_max_candidates, frequency_enabled=frequency_enabled, frequency_top_n=frequency_top_n, spark_session=spark_session))
        metrics["total_target_rows"] = profile.get("row_count")
        fields = [("Target", target), ("Strategy", strategy.title()), ("Published", "Yes"), ("Rows committed", metrics["rows_committed"])]
        if strategy == "scd1":
            fields.extend((label, metrics[key]) for label, key in (("Rows inserted", "rows_inserted"), ("Rows updated", "rows_updated"), ("Rows unchanged", "rows_unchanged")))
        elif strategy == "scd2":
            fields.extend((label, metrics[key]) for label, key in (("Versions inserted", "versions_inserted"), ("Versions expired", "versions_expired"), ("Rows unchanged", "rows_unchanged")))
        duration = summary.finish(fields)
        return {**common_results, **write_result, "write_metrics": metrics, "total_duration_seconds": duration, "dataframe": prepared, "published": True, "profile_result": profile}
    except Exception:
        mapping = sensitive.get("support_mapping")
        if mapping is not None:
            mapping.unpersist()
        raise

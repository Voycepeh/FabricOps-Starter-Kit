"""Public owner for the standard governed target lifecycle."""
from __future__ import annotations
from typing import Any, Iterable
from fabricops_kit.pipeline.check_dq import check_dq
from fabricops_kit.pipeline.check_guardrail_coverage import check_guardrail_coverage
from fabricops_kit.pipeline.check_schema import check_schema
from fabricops_kit.pipeline.check_sensitive_data import check_sensitive_data
from fabricops_kit.pipeline.check_source_drift import check_source_drift
from fabricops_kit.pipeline.pipeline_write import pipeline_write
from fabricops_kit.pipeline.profile_table import profile_table
from fabricops_kit.pipeline.resolve_table_id import resolve_table_id
from fabricops_kit.pipeline.shared import _run_orchestration_stage


def orchestrate_write(dataframe: Any, *, name: str, sources: Iterable[dict[str, Any]], store: str, schema: str | None, table_name: str, load_strategy: str, contracts: dict[str, Any] | None = None, repartition_by: int | None = None, spark_session=None, verbose: bool = True) -> dict[str, Any]:
    """Execute the standard FabricOps governed Write lifecycle.

    Parameters
    ----------
    dataframe : object
        Transformed Spark DataFrame to validate and publish.
    name : str
        Notebook-facing target name used in orchestration output.
    sources : iterable of dict
        Governed source results containing ``table_id``.
    store : str
        Configured destination store key.
    schema : str, optional
        Physical target schema.
    table_name : str
        Physical target table name.
    load_strategy : str
        Governed strategy forwarded to :func:`pipeline_write`.
    contracts : dict, optional
        ``widget_select_data_contract`` result. Validate mode evaluates the
        frozen candidate and returns without publication.
    repartition_by : int, optional
        Spark write partition count.
    spark_session : object, optional
        Spark session used by every stage.
    verbose : bool, default=True
        Print stage start, outcome, duration, and failure attribution.

    Returns
    -------
    dict
        Write identity and capability results. ``published`` is false when a
        Validate-mode contract passes without publication.

    Raises
    ------
    RuntimeError
        If any stage fails. Its name is reported and the original exception is
        retained as ``__cause__``.

    Notes
    -----
    Order matches canonical ``02_pipeline``: Data Contract gate, Schema,
    Sensitive Data, Source Drift, Data Quality, Guardrail Coverage, Write, and
    persisted-target Profile. Existing metadata and Source Observation commit
    behaviour remains owned by ``pipeline_write``. No DataFrame is displayed.

    Examples
    --------
    >>> result = orchestrate_write(transformed_df, name="curated_orders", sources=[orders], store="Silver", schema="demo", table_name="curated_orders", load_strategy="overwrite", contracts=CONTRACTS)

    See Also
    --------
    pipeline_write, check_schema, check_sensitive_data, check_source_drift,
    check_dq, check_guardrail_coverage, profile_table

    """
    source_ids = [source["table_id"] for source in sources]
    target_id = resolve_table_id(store=store, schema=schema, table_name=table_name)
    names = ["Data Contract", "Schema", "Sensitive Data", "Source Drift", "Data Quality", "Guardrail Coverage", "Write", "Profile"]
    stages = []
    if verbose:
        print(f"FabricOps WRITE · {name}")
    def run(stage, function):
        result, record = _run_orchestration_stage(operation="WRITE", name=name, index=names.index(stage)+1, total=len(names), stage=stage, function=function, verbose=verbose)
        stages.append(record)
        return result
    contract = (contracts or {}).get("tables", {}).get(target_id)
    if contract and contract.get("mode") == "validate":
        validation = run("Data Contract", lambda: (contracts or {})["validate"](dataframe=dataframe, table_id=target_id, spark_session=spark_session))
        if not validation["validation_passed"]:
            cause = ValueError(f"Data Contract validation failed for {name}.")
            raise RuntimeError(f"WRITE {name!r} failed during Data Contract.") from cause
        return {"table_id": target_id, "published": False, "validation_result": validation, "orchestration_stages": stages}
    run("Data Contract", lambda: {"status": "skipped", "reason": "Enforce path"})
    schema_result = run("Schema", lambda: check_schema(dataframe, table_id=target_id, raise_on_failure=True, spark_session=spark_session, verbose=False))
    sensitive = run("Sensitive Data", lambda: check_sensitive_data(dataframe, table_id=target_id, raise_on_failure=True, spark_session=spark_session, verbose=False))
    prepared = sensitive["dataframe"]
    drift = run("Source Drift", lambda: [check_source_drift(source_id, target_table_id=target_id, raise_on_failure=True, spark_session=spark_session, verbose=False) for source_id in source_ids])
    dq_result = run("Data Quality", lambda: check_dq(prepared, table_id=target_id, raise_on_failure=True, spark_session=spark_session, verbose=False))
    coverage = run("Guardrail Coverage", lambda: check_guardrail_coverage(target_table_id=target_id, source_table_ids=source_ids, spark_session=spark_session, verbose=False))
    write_result = run("Write", lambda: pipeline_write(prepared, store=store, schema=schema, table_name=table_name, load_strategy=load_strategy, source_table_ids=source_ids, repartition_by=repartition_by, spark_session=spark_session, verbose=False))
    profile = run("Profile", lambda: profile_table(table_id=write_result["table_id"], spark_session=spark_session))
    return {**write_result, "published": True, "schema_result": schema_result, "sensitive_result": sensitive, "source_drift_results": drift, "dq_result": dq_result, "coverage_result": coverage, "profile_result": profile, "orchestration_stages": stages}

"""Public owner for the standard governed source lifecycle."""
from __future__ import annotations
from typing import Any
from fabricops_kit.pipeline.check_dq import check_dq
from fabricops_kit.pipeline.check_freshness import check_freshness
from fabricops_kit.pipeline.check_schema import check_schema
from fabricops_kit.pipeline.pipeline_read import pipeline_read
from fabricops_kit.pipeline.profile_table import profile_table
from fabricops_kit.pipeline.shared import _run_orchestration_stage


def orchestrate_read(*, name: str, store: str, schema: str | None, table_name: str, read_mode: str = "full", query: str | None = None, target_table_id: str | None = None, spark_session=None, verbose: bool = True) -> dict[str, Any]:
    """Execute the standard FabricOps governed Read lifecycle.

    Parameters
    ----------
    name : str
        Notebook-facing name used in orchestration output.
    store : str
        Configured source store key.
    schema : str, optional
        Physical source schema.
    table_name : str
        Physical source table name.
    read_mode : {"full", "incremental"}, default="full"
        Source read behaviour forwarded to :func:`pipeline_read`.
    query : str, optional
        Read-only Warehouse query forwarded to :func:`pipeline_read`.
    target_table_id : str, optional
        Governed target identity required for incremental reads.
    spark_session : object, optional
        Spark session used by every stage.
    verbose : bool, default=True
        Print stage start, outcome, duration, and failure attribution.

    Returns
    -------
    dict
        The ``pipeline_read`` result, including ``dataframe`` and ``table_id``,
        plus capability results and ``orchestration_stages``.

    Raises
    ------
    RuntimeError
        If a stage fails. Its name is reported and the original exception is
        retained as ``__cause__``.

    Notes
    -----
    Stages run as Read, Freshness, Schema, Data Quality, and Profile, matching
    canonical ``02_pipeline``. Skipped capability results remain skipped.
    DataFrames are never displayed. Incremental batches are not profiled.

    Examples
    --------
    >>> source = orchestrate_read(name="orders", store="Bronze", schema="demo", table_name="orders")
    >>> orders_df = source["dataframe"]

    See Also
    --------
    pipeline_read, check_freshness, check_schema, check_dq, profile_table

    """
    stages = []
    if verbose:
        print(f"FabricOps READ · {name}")
    def run(index, stage, function):
        result, record = _run_orchestration_stage(operation="READ", name=name, index=index, total=5, stage=stage, function=function, verbose=verbose)
        stages.append(record)
        return result
    source = run(1, "Read", lambda: pipeline_read(store=store, schema=schema, table_name=table_name, read_mode=read_mode, query=query, target_table_id=target_table_id, spark_session=spark_session, verbose=False))
    reader_name = source.pop("_reader_name", None)
    if verbose and reader_name:
        print(f"      Physical read → {reader_name}")
    dataframe, table_id = source["dataframe"], source["table_id"]
    freshness = run(2, "Freshness", lambda: check_freshness(table_id, raise_on_failure=True, spark_session=spark_session, verbose=False))
    schema_result = run(3, "Schema", lambda: check_schema(dataframe, table_id=table_id, raise_on_failure=True, spark_session=spark_session, verbose=False))
    dq_result = run(4, "Data Quality", lambda: check_dq(dataframe, table_id=table_id, raise_on_failure=True, spark_session=spark_session, verbose=False))
    profile = run(5, "Profile", lambda: profile_table(dataframe=dataframe, store=store, schema=schema, table_name=table_name, spark_session=spark_session) if read_mode == "full" else {"status": "skipped", "reason": "Incremental batch"})
    return {**source, "freshness_result": freshness, "schema_result": schema_result, "dq_result": dq_result, "profile_result": profile, "orchestration_stages": stages}

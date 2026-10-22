"""Public owner for notebook-facing statistical and frequency profiling."""

from __future__ import annotations

from fabricops_kit.pipeline.shared import execute_table_profile


def profile_table(
    *,
    dataframe=None,
    store: str | None = None,
    schema: str | None = None,
    table_name: str | None = None,
    table_id: str | None = None,
    grain_discovery_enabled: bool = True,
    grain_discovery_max_columns: int = 3,
    grain_discovery_max_candidates: int = 8,
    frequency_columns=None,
    frequency_enabled: bool = True, frequency_top_n: int | None = 5,
    frequency_max_distinct_percent: float | None = 80.0,
    context=None,
    spark_session=None,
    verbose: bool = True,
):
    """Profile a Spark DataFrame or a complete governed physical table.

    FabricOps calculates the canonical statistical profile and applicable
    frequency distribution close to the data. Supplied DataFrames and physical
    Lakehouse tables use PySpark; physical Warehouse tables use SQL pushdown for
    the calculations while normalizing reported ``DATA_TYPE`` values to the
    canonical PySpark schema vocabulary used by downstream schema and Guardrail
    checks. An identity may be supplied as a
    canonical ``table_id`` or as ``store``, optional ``schema``, and
    ``table_name``. When an identity is present, FabricOps associates the
    result with that governed table and persists Catalogue, profile, and
    frequency metadata. Without an identity, the exact supplied DataFrame is
    profiled without creating an identity or writing metadata.

    Parameters
    ----------
    dataframe : pyspark.sql.DataFrame, optional
        Required unless a complete governed identity is provided. With no
        DataFrame and no identity, the call raises ValueError. If an identity is also
        supplied, FabricOps does not re-read the physical table.
    store : str, optional
        Configured physical store key. Supply with ``table_name`` and optional
        ``schema`` instead of ``table_id``.
    schema : str, optional
        Physical schema when the configured store uses schemas.
    table_name : str, optional
        Physical table name. Required with ``store`` when ``table_id`` is
        omitted.
    table_id : str, optional
        Canonical governed table identity, mutually exclusive with physical
        coordinates.
    grain_discovery_enabled : bool, default=True
        Whether to discover candidate Grain keys for a governed table. False
        skips discovery queries and preserves saved Catalogue candidates.
        The caller controls when to enable discovery; no scheduling is applied.
        This option does not disable contract Grain checks. DataFrame-only
        profiling does not discover or persist candidates.
    grain_discovery_max_columns : int, default=3
        Maximum columns in a candidate key. 1 checks single columns only; 2
        also checks pairs. Must be a positive integer. Wider searches can be costly.
    grain_discovery_max_candidates : int, default=8
        Maximum candidate keys to retain at the smallest valid key width.
        Must be a positive integer. Discovery stops after enough keys are found;
        this limit does not cap work when no valid key exists.
    frequency_columns : sequence of str, optional
        Columns to frequency profile. ``None`` automatically selects eligible
        scalar columns; an empty sequence skips frequency profiling.
    frequency_enabled : bool, default=True
        Whether to calculate frequency distributions for this call. False skips all
        frequency columns. The caller controls when to enable frequency profiling.
    frequency_top_n : int or None, default=5
        Ranked values to retain per frequency column. ``None`` retains all.
    frequency_max_distinct_percent : float or None, default=80.0
        Maximum distinct-per-non-null percentage for automatically selected
        columns. ``None`` disables the cardinality filter.
    context : dict, optional
        Explicit pipeline context; Testing returns profiles without persistence.
    verbose : bool, optional
        Display profiling progress when True; orchestration uses the automatic report.
    spark_session : object, optional
        Spark session to use. When omitted, FabricOps uses the supplied
        DataFrame session or resolves the active session.

    Returns
    -------
    dict
        ``profile`` contains the canonical statistical Spark DataFrame and
        ``frequency_profile`` contains the applicable canonical frequency
        Spark DataFrame, or ``None`` when no columns were selected. Governed
        ``profile`` rows additionally contain persisted snapshot identities
        and audit fields.

    Notes
    -----
    The result also includes ``row_count``, reused from an existing aggregate
    when available (None otherwise). No additional Spark job is run for this
    metric. It describes the profiled dataset, not rows committed by a writer.

    Raises
    ------
    ValueError
        If identity inputs conflict or are incomplete, neither a DataFrame nor
        identity is supplied, frequency settings or discovery limits are invalid, or the resolved
        store is unsupported.
    RuntimeError
        If a governed metadata write requires unavailable Delta support.

    Maintainer Notes
    ----------------
    The orchestration performs these mechanical steps:

    1. Validate and resolve the optional canonical governed identity.
    2. Use the supplied DataFrame exactly, read a physical Lakehouse table into
       Spark, or keep physical Warehouse aggregation in Warehouse SQL.
    3. Calculate canonical statistical metrics with the selected backend.
    4. Select eligible frequency columns and calculate exact grouped counts,
       including null as a frequency value.
    5. When governed, create stable table and column identities, replace rows
       in ``METADATA_DATA_PROFILED`` and
       ``METADATA_DATA_PROFILED_FREQUENCY`` idempotently for the current
       Fabric activity, then update
       ``METADATA_DATA_CATALOGUE``.
    6. Return both profiling outputs. DataFrame-only mode performs no metadata
       writes and never invents a ``table_id``.

    A retry in the same Fabric activity reuses the snapshot and row identities
    and replaces that snapshot rather than appending duplicates. Catalogue is
    updated only after both profile components succeed; its table-level
    ``_activity_id`` and non-null ``last_profiled_at`` identify the completed
    snapshot for readers. A same-activity retry first clears that completion
    marker. If a later stage fails, snapshot removal is best-effort hygiene:
    Catalogue remains authoritative even if cleanup also fails, and the
    original profiling error is preserved. A later activity receives a
    distinct snapshot identity.

    Examples
    --------
    Profile an arbitrary DataFrame without persistence:

    >>> result = profile_table(dataframe=raw_df)
    >>> statistical_profile = result["profile"]
    >>> frequencies = result["frequency_profile"]

    Profile a governed complete physical table without knowing its store kind:

    >>> result = profile_table(store="Bronze", schema="dbo", table_name="orders")

    Profile a transformed DataFrame against an explicit governed identity:

    >>> result = profile_table(dataframe=transformed_df, table_id=target_table_id)

    Limit discovery to single columns and pairs, retaining up to two candidates:

    >>> result = profile_table(
    ...     table_id=target_table_id,
    ...     grain_discovery_max_columns=2, grain_discovery_max_candidates=2,
    ... )

    Refresh statistics while retaining saved key candidates and skipping frequency:

    >>> result = profile_table(
    ...     table_id=target_table_id,
    ...     grain_discovery_enabled=False, frequency_enabled=False,
    ... )

    See Also
    --------
    orchestrate_read, orchestrate_write, read_lakehouse_csv, read_lakehouse_excel,
    read_lakehouse_json, read_lakehouse_parquet

    """
    return execute_table_profile(
        dataframe=dataframe,
        store=store,
        schema=schema,
        table_name=table_name,
        table_id=table_id,
        grain_discovery_enabled=grain_discovery_enabled,
        grain_discovery_max_columns=grain_discovery_max_columns,
        grain_discovery_max_candidates=grain_discovery_max_candidates,
        frequency_columns=frequency_columns,
        frequency_enabled=frequency_enabled,
        frequency_top_n=frequency_top_n,
        frequency_max_distinct_percent=frequency_max_distinct_percent,
        context=context,
        spark_session=spark_session,
        verbose=verbose,
    )

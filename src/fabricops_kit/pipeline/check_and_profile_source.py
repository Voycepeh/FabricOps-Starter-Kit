"""Public owner for governed source validation and profiling."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.profile_and_register_table import PROFILE_AND_REGISTER_TABLE_CORE
from fabricops_kit.pipeline.shared import (
    build_profile_dataframe,
    check_dq_runtime,
    resolve_catalogue_table_identity,
    stop_if_failed,
)


def check_and_profile_source(
    dataframe,
    *,
    source_prep: Mapping[str, Any],
    register_full_profile: bool = True,
) -> dict[str, Any]:
    """Apply governed DQ and the correct source profiling behaviour.

    Parameters
    ----------
    dataframe : pyspark.sql.DataFrame
        Physical source rows read with the ``scope`` returned by
        :func:`read_pipeline_prep`.
    source_prep : mapping
        Governed preparation returned by :func:`read_pipeline_prep` for the
        same source.
    register_full_profile : bool, default=True
        Register a canonical profile when preparation selected the complete
        physical source. Set this to ``False`` when ``dataframe`` is an
        engineer-authored query result rather than the registered source
        table itself.

    Returns
    -------
    dict
        ``dq`` contains the governed DQ result and ``profile`` contains either
        the registered canonical profile or a non-persisted diagnostic profile.
        ``profile_kind`` is ``canonical`` or ``diagnostic``.

    Raises
    ------
    ValueError
        If ``source_prep`` is malformed, represents a skipped read, or
        ``register_full_profile`` is not Boolean.
    RuntimeError
        If a blocking DQ Guardrail rejects the source or metadata persistence
        required for a canonical profile is unavailable.

    Notes
    -----
    A ``full_dataset`` read may replace the current canonical source profile.
    An ``incremental_subset`` is always diagnostic and never writes
    ``METADATA_DATA_PROFILED``, ``METADATA_DATA_PROFILED_FREQUENCY``, or
    ``METADATA_DATA_CATALOGUE``. Governed DQ results continue to be written to
    ``METADATA_GUARDRAIL_RESULTS``.

    Examples
    --------
    >>> result = check_and_profile_source(source_df, source_prep=source_prep)
    >>> result["profile_kind"] in {"canonical", "diagnostic"}
    True

    See Also
    --------
    read_pipeline_prep, profile_and_register_table, profile_dataframe

    """
    if not isinstance(source_prep, Mapping):
        raise ValueError("source_prep must be the mapping returned by read_pipeline_prep().")
    source = source_prep.get("source")
    read_mode = source_prep.get("read_mode")
    if not isinstance(source, Mapping) or not source.get("table_id"):
        raise ValueError("source_prep must contain a canonical source identity.")
    if read_mode not in {"full_dataset", "incremental_subset", "skip"}:
        raise ValueError("source_prep must contain a valid read_mode.")
    if read_mode == "skip":
        raise ValueError("A source resolved to skip must not be read, checked, or profiled.")
    if not isinstance(register_full_profile, bool):
        raise ValueError("register_full_profile must be Boolean.")

    config, env, context = resolve_fabric_context()
    spark_session = getattr(dataframe, "sparkSession", None)
    identity = resolve_catalogue_table_identity(
        config,
        env,
        str(source["table_id"]),
        spark_session=spark_session,
        context=context,
    )
    dq = check_dq_runtime(
        dataframe,
        config,
        env,
        identity["table_name"],
        table_id=identity["table_id"],
        target=identity["target"],
        store_type=identity["store_type"],
        schema_name=identity["schema"],
        dataset_name="",
        run_id="",
        row_identity_columns=None,
        context=context,
    )
    stop_if_failed(dq)

    canonical = read_mode == "full_dataset" and register_full_profile
    profile = (
        PROFILE_AND_REGISTER_TABLE_CORE(dataframe, profile_role="source", table=source)
        if canonical
        else build_profile_dataframe(dataframe)
    )
    return {
        "dq": dq,
        "profile": profile,
        "profile_kind": "canonical" if canonical else "diagnostic",
    }

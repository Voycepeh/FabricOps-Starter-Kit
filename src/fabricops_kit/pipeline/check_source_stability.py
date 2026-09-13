"""Public Source Stability Guardrail check for a source-to-target relationship."""

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.shared import (
    check_source_stability_for_target,
    resolve_catalogue_table_identity,
    resolve_table_processing_definition,
    print_guardrail_result,
)


def check_source_stability(
    source_table_id: str,
    *,
    target_table_id: str,
    enabled: bool = True,
    raise_on_failure: bool = False,
    verbose: bool = True,
) -> dict:
    """Validate a source snapshot against one target consumption baseline.

    Parameters
    ----------
    source_table_id : str
        Canonical governed source identity returned by :func:`pipeline_read`.
    target_table_id : str
        Canonical governed target identity whose consumption baseline and load
        strategy determine Source Stability compatibility.
    enabled : bool, default=True
        Explicitly skip the check when ``False``.
    raise_on_failure : bool, default=False
        Raise ``RuntimeError`` when a blocking result cannot continue.
    verbose : bool, default=True
        Print the concise normalized check outcome when ``True``.

    Returns
    -------
    dict
        Source Stability evidence for the source-to-target relationship and its
        compatibility with the target's governed load strategy.

    Raises
    ------
    ValueError
        If either identity, transient observation, rule, or target processing
        definition is invalid.
    RuntimeError
        If metadata history cannot be read, or ``raise_on_failure=True`` and
        the target cannot safely reconcile the observed source change.

    Notes
    -----
    Notebook orchestration calls this function explicitly for every governed
    source before :func:`pipeline_write`. A successful write then commits the
    accepted source-to-target baseline in ``METADATA_SOURCE_OBSERVATION``.

    Examples
    --------
    >>> result = check_source_stability(
    ...     source_result["table_id"],
    ...     target_table_id=target_table_id,
    ... )
    >>> result["target_table_id"] == target_table_id
    True

    See Also
    --------
    pipeline_read, pipeline_write

    """
    if not enabled:
        result = {"status": "skipped", "can_continue": True, "checks": []}
        print_guardrail_result(
            "Source Stability",
            result,
            verbose=verbose,
            source_table_id=source_table_id,
            target_table_id=target_table_id,
        )
        return result
    config, env, context = resolve_fabric_context()
    target = resolve_catalogue_table_identity(config, env, target_table_id, context=context)
    processing = resolve_table_processing_definition(config, env, str(target["table_id"]), context=context)
    result = check_source_stability_for_target(
        source_table_id=str(source_table_id),
        target_table_id=str(target["table_id"]),
        target_processing=processing,
        raise_on_failure=False,
    )
    print_guardrail_result(
        "Source Stability",
        result,
        verbose=verbose,
        source_table_id=source_table_id,
        target_table_id=str(target["table_id"]),
    )
    if raise_on_failure and not result["can_continue"]:
        raise RuntimeError(
            f"A blocking Source Stability Guardrail failed for source_table_id {source_table_id!r} "
            f"and target_table_id {target['table_id']!r}."
        )
    return result

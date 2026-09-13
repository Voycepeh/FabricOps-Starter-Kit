"""Public Source Stability Guardrail check for a source-to-target relationship."""

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.shared import (
    check_source_stability_for_target,
    resolve_catalogue_table_identity,
    resolve_table_processing_definition,
)


def check_source_stability(
    table_id: str,
    *,
    target_table_id: str,
    raise_on_failure: bool = False,
) -> dict:
    """Validate a source snapshot against one target consumption baseline.

    Parameters
    ----------
    table_id : str
        Canonical governed source identity returned by :func:`pipeline_read`.
    target_table_id : str
        Canonical governed target identity whose consumption baseline and load
        strategy determine Source Stability compatibility.
    raise_on_failure : bool, default=False
        Raise ``RuntimeError`` when a blocking result cannot continue.

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
    Normal notebook orchestration does not call this function directly.
    :func:`pipeline_write` evaluates it for every explicit ``source_table_id``
    before physical publication. A successful write then commits the new
    source-to-target baseline in ``METADATA_SOURCE_OBSERVATION``.

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
    config, env, context = resolve_fabric_context()
    target = resolve_catalogue_table_identity(
        config, env, target_table_id, context=context
    )
    processing = resolve_table_processing_definition(
        config, env, str(target["table_id"]), context=context
    )
    return check_source_stability_for_target(
        source_table_id=str(table_id),
        target_table_id=str(target["table_id"]),
        target_processing=processing,
        raise_on_failure=raise_on_failure,
    )

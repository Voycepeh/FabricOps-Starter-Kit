"""Public Source Drift Guardrail check for a source-to-target relationship."""

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.shared import (
    check_source_drift_for_target,
    resolve_catalogue_table_identity,
    resolve_pipeline_data_contract,
    resolve_table_processing_definition,
    print_guardrail_result,
)


def check_source_drift(
    source_table_id: str,
    *,
    target_table_id: str,
    enabled: bool = True,
    raise_on_failure: bool = False,
    verbose: bool = True,
) -> dict:
    """Detect governed source drift against one target consumption baseline.

    Compare the current source observation with the last source observation
    successfully consumed by this target and detect source changes that violate
    the source table's governed load behaviour.

    Parameters
    ----------
    source_table_id : str
        Canonical governed source identity returned by :func:`pipeline_read`.
    target_table_id : str
        Canonical governed target identity used to select the last successfully
        consumed Source Observation baseline.
    enabled : bool, default=True
        Explicitly skip the check when ``False``.
    raise_on_failure : bool, default=False
        Raise ``RuntimeError`` when a blocking result cannot continue.
    verbose : bool, default=True
        Print the concise normalized check outcome when ``True``.

    Returns
    -------
    dict
        Source Drift evidence for the source-to-target relationship and its
        compatibility with the source's governed load behaviour.

    Raises
    ------
    ValueError
        If either identity, transient observation, rule, or source processing
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
    >>> result = check_source_drift(
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
            "Source Drift",
            result,
            verbose=verbose,
            source_table_id=source_table_id,
            target_table_id=target_table_id,
        )
        if verbose:
            print("  Details disabled explicitly; no contract, baseline, observation, or rule was evaluated")
        return result
    config, env, context = resolve_fabric_context()
    source = resolve_catalogue_table_identity(config, env, source_table_id, context=context)
    target = resolve_catalogue_table_identity(config, env, target_table_id, context=context)
    contract = resolve_pipeline_data_contract(
        config, env, str(source["table_id"]), context=context
    )
    if contract is None:
        result = {
            "status": "skipped",
            "can_continue": True,
            "checks": [],
            "reason": "No Data Contract selected; Development only.",
            "source_table_id": str(source["table_id"]),
            "target_table_id": str(target["table_id"]),
            "environment_name": env,
        }
        print_guardrail_result(
            "Source Drift",
            result,
            verbose=verbose,
            source_table_id=str(source["table_id"]),
            target_table_id=str(target["table_id"]),
        )
        if verbose:
            print("  Details no source Data Contract selected; drift evaluation and evidence persistence skipped")
        return result
    source_processing = resolve_table_processing_definition(
        config, env, str(source["table_id"]), context=context
    )
    result = check_source_drift_for_target(
        source_table_id=str(source["table_id"]),
        target_table_id=str(target["table_id"]),
        source_processing=source_processing,
        raise_on_failure=False,
    )
    print_guardrail_result(
        "Source Drift",
        result,
        verbose=verbose,
        source_table_id=source_table_id,
        target_table_id=str(target["table_id"]),
    )
    if verbose:
        strategy = str(source_processing.get("load_strategy") or "unspecified")
        rule_type = str(result.get("rule_type") or "source_drift")
        action = str(result.get("action") or "").strip() or "default"
        print("  Details")
        print("    Source and target identities resolved from the Data Catalogue")
        print("    Source Data Contract selected and Source Drift rule resolved")
        print(f"    Source processing strategy {strategy}")
        print("    Current observation comes from pipeline_read(); baseline is the last observation successfully consumed by this target")
        print(f"    Rule {rule_type} (action {action})")
        print("    Evaluation compares current source state with the target-specific accepted baseline")
        print("    Guardrail evidence appended to METADATA_GUARDRAIL_RESULTS; accepted baseline advances only after pipeline_write() succeeds")
    if raise_on_failure and not result["can_continue"]:
        raise RuntimeError(
            f"A blocking Source Drift Guardrail failed for source_table_id {source_table_id!r} "
            f"and target_table_id {target['table_id']!r}."
        )
    return result

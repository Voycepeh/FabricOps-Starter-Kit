"""Notebook-facing reviewed Pipeline Promotion."""
from __future__ import annotations


def promote_pipeline(review: dict, *, governance_confirmed: bool = False) -> dict:
    """Archive and promote one reviewed, manually tested notebook into a separate item.

    Parameters
    ----------
    review : dict
        Exact candidate returned by the Pipeline Promotion widget review action.
        Contains the saved notebook, destination physical bindings, exact Contracts
        and expected active version. Keep this object for safe lost-ack retries.
    governance_confirmed : bool, default=False
        Confirm the displayed review; actual Fabric permissions authorize changes.

    Returns
    -------
    dict
        Frozen per-version METADATA_PIPELINE_REGISTRY row. An active row does not
        override the pending signed-in Fabric validation gate for Governed starts.

    Raises
    ------
    ValueError
        If review, bindings, Contracts or expected version changed.
    RuntimeError
        If notebook APIs, archive readback or atomic commit cannot be verified.
        Staged artifacts are retained; the prior active version remains intact.

    Notes
    -----
    The complete notebook is frozen; imported dependencies are not. Same-workspace
    promotion creates a separate notebook in Governed/. Folders confer no access
    protection. Schedules are engineer-owned and never silently moved. Saved code
    checks have a TOCTOU limitation and cannot prevent privileged Spark bypass.

    Examples
    --------
    >>> result = promote_pipeline(review, governance_confirmed=True)

    """
    from fabricops_kit.activated_pipeline.shared import stage_pipeline_promotion
    return stage_pipeline_promotion(review, governance_confirmed=governance_confirmed)

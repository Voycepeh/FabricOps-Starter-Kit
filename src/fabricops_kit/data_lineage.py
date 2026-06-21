"""Notebook lineage helpers for deterministic parsing and metadata-ready evidence."""
from __future__ import annotations
from typing import Any

from .config import _current_audit_timestamp


def _validate_lineage_steps(lineage_steps: Any) -> dict[str, Any]:
    """Validate lineage step structure and flag records requiring human review.

    Parameters
    ----------
    lineage_steps : Any
        Candidate lineage payload, expected to be a list of dictionaries.

    Returns
    -------
    dict of str to Any
        Validation result with ``is_valid``, ``errors``, ``warnings``, and ``review_required``.

    """
    errors: list[str] = []
    warnings: list[str] = []
    review_required = False
    required_fields = ("source", "target", "transformation", "reason", "source_type", "target_type", "confidence")
    if not isinstance(lineage_steps, list):
        return {"is_valid": False, "errors": ["lineage_steps must be a list."], "warnings": [], "review_required": True}
    if not lineage_steps:
        return {"is_valid": False, "errors": ["lineage_steps cannot be empty."], "warnings": [], "review_required": True}
    for i, step in enumerate(lineage_steps, 1):
        if not isinstance(step, dict):
            errors.append(f"Step {i}: each lineage step must be a dict.")
            review_required = True
            continue
        for field_name in required_fields:
            if field_name not in step:
                errors.append(f"Step {i}: missing required field '{field_name}'.")
        if step.get("source_type") == "unknown" or step.get("target_type") == "unknown":
            review_required = True
            warnings.append(f"Step {i}: unknown type requires human review.")
        if step.get("confidence") == "low":
            review_required = True
            warnings.append(f"Step {i}: low confidence requires human review.")
    return {"is_valid": not errors, "errors": errors, "warnings": warnings, "review_required": review_required}


def _build_lineage_records(dataset_name: str, lineage_steps: list[dict], run_id: str | None = None, notebook_name: str | None = None, workspace_name: str | None = None, workspace_id: str | None = None, notebook_id: str | None = None, created_by: str | None = None, config: Any = None) -> list[dict]:
    """Build metadata-ready lineage rows from validated lineage steps.

    Parameters
    ----------
    dataset_name : str
        Dataset identifier associated with the lineage rows.
    lineage_steps : list of dict
        Validated lineage step dictionaries.
    run_id : str or None, default=None
        Optional run identifier.
    notebook_name : str or None, default=None
        Optional notebook name.
    workspace_name : str or None, default=None
        Optional workspace display name.
    workspace_id : str or None, default=None
        Optional workspace identifier.
    notebook_id : str or None, default=None
        Optional notebook identifier.
    created_by : str or None, default=None
        Optional creator identity.
    config : Any, optional
        Framework configuration used to resolve the configured audit timezone.

    Returns
    -------
    list of dict
        Lineage rows suitable for metadata persistence.

    """
    validation = _validate_lineage_steps(lineage_steps)
    if not validation["is_valid"]:
        raise ValueError(f"Invalid lineage_steps: {validation['errors']}")
    created_ts = _current_audit_timestamp(config=config, drop_microseconds=False)
    return [
        {
            "dataset_name": dataset_name,
            "step_number": step_number,
            **step,
            "run_id": run_id,
            "workspace_id": workspace_id,
            "workspace_name": workspace_name,
            "notebook_id": notebook_id,
            "notebook_name": notebook_name,
            "created_by": created_by,
            "created_ts": created_ts,
        }
        for step_number, step in enumerate(lineage_steps, 1)
    ]

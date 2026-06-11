"""Notebook lineage helpers for deterministic parsing and metadata-ready evidence."""
from __future__ import annotations
import ast
from typing import Any

from .config import _current_audit_timestamp

_ALLOWED_TYPES = {"dataframe", "lakehouse_table", "warehouse_table", "file", "unknown"}
_ALLOWED_CONFIDENCE = {"high", "medium", "low"}
READ_HELPERS = {"read_lakehouse_table": "lakehouse_table", "read_warehouse_table": "warehouse_table", "read_lakehouse_csv": "file", "read_lakehouse_excel": "file", "read_lakehouse_parquet": "file"}
WRITE_HELPERS = {"write_lakehouse_table": "lakehouse_table", "write_warehouse_table": "warehouse_table"}


def _flatten_chain(node: ast.AST) -> tuple[str | None, list[str]]:
    ops, cur = [], node
    while isinstance(cur, ast.Call) and isinstance(cur.func, ast.Attribute):
        ops.append(cur.func.attr)
        cur = cur.func.value
    return (cur.id if isinstance(cur, ast.Name) else None), list(reversed(ops))


def _resolve_write_target(cname: str, call: ast.Call) -> str:
    def literal(node: ast.AST) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return node.id if isinstance(node, ast.Name) else None

    if cname == "write_lakehouse_table":
        return literal(call.args[2]) if len(call.args) >= 3 else "unknown_lakehouse_table"
    if cname == "write_warehouse_table":
        if len(call.args) >= 5:
            return f"{literal(call.args[3]) or 'schema'}.{literal(call.args[4]) or 'table'}"
        return "unknown_warehouse_table"
    return "unknown_target"


def _scan_notebook_lineage(code: str) -> list[dict[str, Any]]:
    """Extract deterministic lineage steps from notebook code using AST parsing.

    Parameters
    ----------
    code : str
        Python notebook source code to analyze.

    Returns
    -------
    list of dict of str to Any
        Ordered lineage step dictionaries inferred from read, transform, and write calls.
    """
    def name(node: ast.AST) -> str | None:
        return node.id if isinstance(node, ast.Name) else None

    def call_name(call: ast.Call) -> str:
        if isinstance(call.func, ast.Name):
            return call.func.id
        if isinstance(call.func, ast.Attribute):
            return call.func.attr
        return "unknown"

    def step(source: str, target: str, transformation: str, source_type: str, target_type: str, confidence: str, lineno: int, ops: list[str], notes: str = "") -> dict[str, Any]:
        return {"source": source, "target": target, "transformation": transformation, "reason": "", "source_type": source_type, "target_type": target_type, "confidence": confidence, "notes": notes, "operation_types": ops, "code_refs": [f"line:{lineno}"]}

    tree = ast.parse(code)
    steps: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and node.targets and isinstance(node.value, ast.Call):
            lhs = name(node.targets[0])
            if not lhs:
                continue
            cname = call_name(node.value)
            if cname in READ_HELPERS:
                steps.append(step(cname, lhs, f"read via {cname}", READ_HELPERS[cname], "dataframe", "high", node.lineno, ["read"]))
                continue
            if cname in {"read_csv", "read_parquet", "read_excel"}:
                steps.append(step(cname, lhs, f"read via pandas.{cname}", "file", "dataframe", "high", node.lineno, ["read"]))
                continue
            src, ops = _flatten_chain(node.value)
            if ops:
                steps.append(step(src or "unknown", lhs, " -> ".join(ops), "dataframe" if src else "unknown", "dataframe", "high" if src else "medium", node.lineno, ops, "" if src else "base dataframe could not be inferred"))

        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call, cname = node.value, call_name(node.value)
            if cname in WRITE_HELPERS and call.args:
                src = name(call.args[0]) or "unknown"
                steps.append(step(src, _resolve_write_target(cname, call), f"write via {cname}", "dataframe" if src != "unknown" else "unknown", WRITE_HELPERS[cname], "high" if src != "unknown" else "medium", node.lineno, ["write"]))
    return steps


def _scan_notebook_cells(cells: list[str]) -> list[dict[str, Any]]:
    """Scan multiple notebook cells and append cell references to lineage steps.

    Parameters
    ----------
    cells : list of str
        Cell source strings in notebook execution order.

    Returns
    -------
    list of dict of str to Any
        Combined lineage steps with ``cell:<index>`` entries in ``code_refs``.
    """
    out: list[dict[str, Any]] = []
    for idx, cell in enumerate(cells):
        for step in _scan_notebook_lineage(cell):
            step["code_refs"].append(f"cell:{idx}")
            out.append(step)
    return out


def _enrich_lineage_steps_with_ai(lineage_steps: list[dict[str, Any]], ai_helper: Any | None = None) -> dict[str, Any]:
    """Optionally enrich deterministic lineage steps using an AI helper callable.

    Parameters
    ----------
    lineage_steps : list of dict of str to Any
        Deterministic lineage step dictionaries.
    ai_helper : Any or None, default=None
        Callable that accepts lineage steps and returns enriched steps.

    Returns
    -------
    dict of str to Any
        Enrichment payload containing steps, AI usage flag, fallback prompt, and notes.
    """
    if ai_helper is None:
        return {"steps": lineage_steps, "ai_used": False, "fallback_prompt": "Review these deterministic lineage steps and improve reasons/notes only; do not change structure. steps=" + str(lineage_steps), "notes": "AI helper unavailable; Copilot fallback prompt generated."}
    return {"steps": ai_helper(lineage_steps) or lineage_steps, "ai_used": True, "fallback_prompt": "", "notes": "AI enrichment applied."}


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
    required = ["source", "target", "transformation", "reason", "source_type", "target_type", "confidence"]
    if not isinstance(lineage_steps, list):
        return {"is_valid": False, "errors": ["lineage_steps must be a list."], "warnings": [], "review_required": True}
    if not lineage_steps:
        return {"is_valid": False, "errors": ["lineage_steps cannot be empty."], "warnings": [], "review_required": True}
    for i, step in enumerate(lineage_steps, 1):
        if not isinstance(step, dict):
            errors.append(f"Step {i}: each lineage step must be a dict.")
            review_required = True
            continue
        for f in required:
            if f not in step:
                errors.append(f"Step {i}: missing required field '{f}'.")
        if step.get("source_type") == "unknown" or step.get("target_type") == "unknown":
            review_required = True; warnings.append(f"Step {i}: unknown type requires human review.")
        if step.get("confidence") == "low":
            review_required = True; warnings.append(f"Step {i}: low confidence requires human review.")
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


def build_lineage_records(*, dataset_name: str, run_id: str, source_tables: list[str], target_table: str, transformation_steps: list[dict], config: Any = None) -> list[dict]:
    """Build compact lineage records for downstream metadata sinks.

    Parameters
    ----------
    dataset_name : str
        Dataset identifier for all output rows.
    run_id : str
        Unique run identifier.
    source_tables : list of str
        Source table names captured for the run.
    target_table : str
        Target table name produced by the run.
    transformation_steps : list of dict
        Transformation step dictionaries to merge into each output row.
    config : Any, optional
        Framework configuration used to resolve the configured audit timezone
        when adding timestamp metadata.

    Returns
    -------
    list of dict
        Row dictionaries suitable for metadata persistence.
    """
    return [{"run_id": run_id, "dataset_name": dataset_name, "source_tables": source_tables, "target_table": target_table, **({"created_ts": _current_audit_timestamp(config=config, drop_microseconds=False)} if config is not None else {}), **s} for s in transformation_steps]

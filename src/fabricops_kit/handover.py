"""Handover summary builders for notebook handover and metadata logging."""

from __future__ import annotations

from datetime import datetime, timezone


SECTION_KEYS = ["source_profile", "output_profile", "schema_drift", "incremental_safety", "quality", "contracts", "lineage"]


def _status_of(section: dict | None) -> str:
    if not section:
        return "not_provided"
    return section.get("status", "not_provided")


def build_handover(*, runtime_context: dict, contract: dict | None = None, source_profile: dict | None = None, output_profile: dict | None = None, schema_drift_result: dict | None = None, incremental_safety_result: dict | None = None, quality_result: dict | None = None, contract_validation_result: dict | None = None, lineage_summary: dict | None = None, notes: list[str] | None = None) -> dict:
    """Build a handover-friendly summary for one data product run.

    Parameters
    ----------
    runtime_context : dict
        Runtime identifiers and environment metadata for the run.
    contract : dict | None
        Optional normalized data-product contract used for validation and targets.

    Returns
    -------
    dict
        Consolidated summary payload used for lineage and handover documentation.
    """
    sections = {"purpose": (contract or {}).get("dataset", {}).get("purpose"), "source_profile": source_profile, "output_profile": output_profile, "schema_drift": schema_drift_result, "incremental_safety": incremental_safety_result, "quality": quality_result, "contracts": contract_validation_result, "lineage": lineage_summary, "notes": notes or []}
    not_provided_sections = [k for k in SECTION_KEYS if sections.get(k) is None]
    considered = [sections[k] for k in SECTION_KEYS if sections.get(k)]
    failed = any((v.get("can_continue") is False) or v.get("status") == "failed" for v in considered)
    warning = any(v.get("status") == "warning" for v in considered)
    overall = "failed" if failed else ("warning" if warning else "passed")
    action_items = []
    if failed:
        action_items.append("Investigate blocking checks before continuing.")
    if warning:
        action_items.append("Review warning checks and monitor downstream impact.")
    if not_provided_sections:
        action_items.append(f"Optional sections not provided: {', '.join(not_provided_sections)}.")
    return {"run_id": runtime_context.get("run_id"), "dataset_name": runtime_context.get("dataset_name") or (contract or {}).get("dataset", {}).get("name"), "environment": runtime_context.get("environment"), "source_table": runtime_context.get("source_table"), "target_table": runtime_context.get("target_table"), "started_at_utc": runtime_context.get("started_at_utc"), "generated_at_utc": datetime.now(timezone.utc).isoformat(), "overall_status": overall, "can_continue": not failed, "sections": sections, "not_provided_sections": not_provided_sections, "action_items": action_items}


def render_handover_markdown(summary: dict) -> str:
    """Render a handover summary dictionary into Markdown for handover notes.

    Parameters
    ----------
    summary : dict
        Output from :func:`build_handover`.

    Returns
    -------
    str
        Markdown text containing key run outcomes and diagnostics.
    """
    s = summary.get("sections", {})
    lines = [f"# Handover Summary — {summary.get('dataset_name', 'unknown')}", f"- Run ID: `{summary.get('run_id', 'unknown')}`", f"- Environment: `{summary.get('environment', 'unknown')}`", f"- Overall status: **{summary.get('overall_status', 'unknown')}**", "", "## Run Context", f"- Source table: `{summary.get('source_table', 'unknown')}`", f"- Target table: `{summary.get('target_table', 'unknown')}`", f"- Started at (UTC): `{summary.get('started_at_utc', 'unknown')}`", "", "## Dataset Purpose", f"{s.get('purpose') or 'Not provided.'}", "", "## Section Status", f"- Schema drift: **{_status_of(s.get('schema_drift'))}**", f"- Incremental safety: **{_status_of(s.get('incremental_safety'))}**", f"- Quality: **{_status_of(s.get('quality'))}**", f"- Contracts: **{_status_of(s.get('contracts'))}**"]
    lines.extend(["", "## Not Provided Sections"])
    lines.extend([f"- {n}" for n in summary.get("not_provided_sections", [])] or ["- None"])
    src_count = (s.get("source_profile") or {}).get("row_count")
    out_count = (s.get("output_profile") or {}).get("row_count")
    lines.extend(["", f"- Source row count: `{src_count}`", f"- Output row count: `{out_count}`", "", "## Action Items"])
    lines.extend([f"- {item}" for item in summary.get("action_items", [])] or ["- None"])
    lines.extend(["", "## Notes"])
    lines.extend([f"- {n}" for n in (s.get("notes") or [])] or ["- None"])
    return "\n".join(lines)


def _build_handover_record(summary: dict) -> dict:
    """Execute the `_build_handover_record` workflow step in FabricOps.
    
        Use this callable at its corresponding stage of the pipeline contract
        (configuration, IO, profiling, quality, drift, lineage, or handover)
        to produce deterministic artifacts and validation evidence.
    
        Parameters
        ----------
        summary : Any
            Input parameter `summary`.
    
        Returns
        -------
        Any
            Function output used by downstream FabricOps workflow steps.
    
        Raises
        ------
        Exception
            Propagates validation, runtime, or storage errors from underlying
            operations when execution cannot continue safely.
    
        Notes
        -----
        Side effects may include metadata writes, quality evidence generation,
        or persisted drift/lineage/handover artifacts depending on the function.
    
        Examples
        --------
        >>> _build_handover_record(...)
        """
    sections = summary.get("sections", {})
    return {"run_id": summary.get("run_id"), "dataset_name": summary.get("dataset_name"), "environment": summary.get("environment"), "source_table": summary.get("source_table"), "target_table": summary.get("target_table"), "overall_status": summary.get("overall_status"), "can_continue": summary.get("can_continue"), "generated_at_utc": summary.get("generated_at_utc"), "source_row_count": (sections.get("source_profile") or {}).get("row_count"), "output_row_count": (sections.get("output_profile") or {}).get("row_count"), "schema_drift_status": _status_of(sections.get("schema_drift")), "incremental_safety_status": _status_of(sections.get("incremental_safety")), "quality_status": _status_of(sections.get("quality")), "contract_status": _status_of(sections.get("contracts")), "action_item_count": len(summary.get("action_items", [])), "summary_markdown": render_handover_markdown(summary)}

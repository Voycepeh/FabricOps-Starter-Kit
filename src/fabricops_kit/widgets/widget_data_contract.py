"""Unified Data Contract governance authoring, review, and freeze widget."""

from __future__ import annotations

import html
import traceback
import json
import uuid
from decimal import Decimal, InvalidOperation
from functools import wraps
from time import perf_counter
from datetime import UTC, datetime, timedelta
from typing import Any, Mapping

from fabricops_kit.config.shared import metadata_timestamp_sort_key, normalize_audit_datetime, resolve_fabric_context, validate_ai_enrichment
from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.shared import dq_tolerance_parameter
from fabricops_kit.widgets import shared
from fabricops_kit.widgets.enrichment_shared import (
    PII_LABELS,
    ai_failure_diagnostic,
    build_ai_business_rule_context,
    build_ai_enrichment_context,
    build_ai_sensitive_data_context,
    suggest_enrichment,
    suggest_grain_key,
    suggest_business_rule,
    suggest_sensitive_data,
)

_SENSITIVE_TREATMENT_OPTIONS = (("Mask", "mask"), ("Tokenize", "tokenize"), ("Bucket numeric values", "bucket"), ("Remove column", "remove"))

DATA_CONTRACT_MANIFEST: dict[str, Any] | None = None
DATA_CONTRACT_MANIFEST_JSON: str | None = None


def _valid_dropdown_value(options: list[str] | tuple[str, ...], value: Any, *, fallback: Any = None) -> Any:
    """Return a widget-safe value when persisted metadata no longer matches its options."""
    candidate = str(value or "")
    return candidate if candidate in options else fallback


def _set_selection_value(
    control: Any,
    value: Any,
    *,
    control_name: str,
    table_name: str = "",
    column_name: str = "",
) -> None:
    """Assign a selection value and preserve useful context if ipywidgets rejects it."""
    try:
        control.value = value
    except Exception as exc:
        raw_options = list(getattr(control, "options", ()) or ())
        valid_options = [
            item[1] if isinstance(item, tuple) and len(item) > 1 else item
            for item in raw_options
        ]
        location = f"table={table_name!r}"
        if column_name:
            location += f", column={column_name!r}"
        raise ValueError(
            "Data Contract editor invalid selection: "
            f"control={control_name!r}, value={value!r}, {location}, "
            f"valid_options={valid_options!r}"
        ) from exc
_TABS = ("Table", "Columns", "Data Quality", "Review", "AI Usage")
_CONTRACT_STYLE = """<style>
.fabricops-data-contract {
    --contract-accent:var(--form-accent); --contract-border:var(--form-border);
    height:auto; max-height:none; overflow:visible;
    scrollbar-gutter:auto;
}
.fabricops-data-contract,
.fabricops-data-contract * { overflow-anchor:none !important; }
.fabricops-data-contract .fabricops-contract-nav { width:100%; margin:0; }
.fabricops-data-contract .fabricops-contract-nav-row {
    padding:0;
}
.fabricops-data-contract .fabricops-operation-progress {
    min-height:0;
    background:var(--form-canvas, #f6f8fb);
}
.fabricops-data-contract .fabricops-ai-usage-table {
    width:100%; min-width:560px; border-collapse:collapse; font-size:12px;
}
.fabricops-data-contract .fabricops-ai-usage-table :is(th,td) {
    text-align:left; padding:8px; border-bottom:1px solid var(--form-border); vertical-align:top;
}
.fabricops-data-contract .fabricops-ai-usage-table th { background:var(--form-tint); }
.fabricops-data-contract .fabricops-contract-nav > div {
    display:flex; flex-direction:row; flex-wrap:wrap; gap:4px; padding:4px; background:var(--form-tint);
    border:1px solid var(--form-border); border-radius:7px; width:100%;
}
.fabricops-data-contract .fabricops-contract-nav button {
    flex:1 1 120px; min-width:0; width:auto; text-align:center; min-height:36px; height:auto; padding:6px 10px; border:0; border-radius:5px; margin:0;
    background:transparent; color:#526477; font-weight:600; box-shadow:none;
}
.fabricops-data-contract .fabricops-contract-nav button.mod-active { background:#fff; color:var(--form-accent); border-left:3px solid var(--form-accent); }
.fabricops-data-contract .fabricops-contract-sidebar,
.fabricops-data-contract .fabricops-contract-selector {
    background:#fff; border:1px solid var(--form-border); border-radius:8px; padding:20px; gap:12px;
}
.fabricops-data-contract .fabricops-contract-sidebar {
    position:sticky; top:0; align-self:start; height:auto; min-height:0; overflow:visible; padding:14px; gap:8px;
}
.fabricops-data-contract .fabricops-contract-sidebar .widget-vbox { gap:8px; }
.fabricops-data-contract .fabricops-contract-workspace {
    gap:16px; min-height:0; align-items:start; overflow:visible;
}
.fabricops-data-contract .fabricops-contract-detail {
    height:auto; min-height:0; max-height:max(680px, calc(100vh - 200px)); border:0; padding:0;
    gap:16px; overflow-x:hidden; overflow-y:auto; scrollbar-gutter:stable;
    overscroll-behavior:contain;
}
.fabricops-data-contract .fabricops-contract-detail > .widget-vbox {
    background:#fff; border:1px solid var(--form-border); border-radius:8px;
    padding:20px; gap:16px; overflow:visible;
}
.fabricops-data-contract .fabricops-column-header {
    display:flex; flex-flow:row wrap; align-items:center; justify-content:space-between;
    gap:10px 20px; width:100%; min-width:0; padding:11px 16px;
    background:#fff; border:1px solid var(--form-border); border-radius:8px;
}
.fabricops-data-contract .fabricops-column-identity { flex:1 1 420px; min-width:0; gap:4px; }
.fabricops-data-contract .fabricops-column-context { min-width:0; line-height:1.35; }
.fabricops-data-contract .fabricops-column-name {
    color:var(--form-accent); font-size:16px; font-weight:700; overflow-wrap:anywhere;
}
.fabricops-data-contract .fabricops-column-meta,
.fabricops-data-contract .fabricops-column-status { font-size:12px; color:#667085; }
.fabricops-data-contract .fabricops-column-status { margin-left:10px; color:var(--form-accent); }
.fabricops-data-contract .fabricops-column-status.is-drift { color:#a4262c; font-weight:700; }
.fabricops-data-contract .fabricops-column-required-controls {
    flex:0 1 auto; min-width:170px; gap:2px; align-items:flex-start;
}
.fabricops-data-contract .fabricops-contract-labeled-grid { grid-template-columns:minmax(0,1fr) !important; gap:8px; }
.fabricops-data-contract .fabricops-contract-compound-field {
    display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px;
}
.fabricops-data-contract .fabricops-contract-compound-field > .widget-html { grid-column:1/-1; font-weight:600; }
.fabricops-data-contract .fabricops-contract-compound-field > .widget-html .widget-html-content > div { padding-top:0 !important; }
.fabricops-data-contract .fabricops-contract-compound-field > .widget-inline-hbox:nth-child(2):last-child { grid-column:1/-1; }
.fabricops-data-contract .fabricops-contract-options {
    width:100%; flex-wrap:wrap; padding:8px 10px; background:#f6f8fb;
    border:1px solid var(--form-border); border-radius:5px;
}
.fabricops-data-contract .fabricops-grain-controls {
    display:flex; flex-flow:row wrap; align-items:flex-end; gap:18px; width:100%;
}
.fabricops-data-contract .fabricops-grain-controls > .fabricops-grain-policy {
    flex:0 1 220px; width:220px !important; max-width:100%;
}
.fabricops-data-contract .fabricops-treatment-guide {
    background:#f8f6fc; border:1px solid #ded7ef; border-left:3px solid #6750a4;
    border-radius:5px; color:#243449; padding:10px 12px; font-size:12px; line-height:1.5;
}
.fabricops-data-contract .fabricops-treatment-guide p { margin:0 0 6px; }
.fabricops-data-contract .fabricops-treatment-example {
    display:flex; flex-wrap:wrap; align-items:center; gap:6px; margin-top:7px;
    color:#344054;
}
.fabricops-data-contract .fabricops-treatment-example code {
    background:#fff; border:1px solid #dce4ed; border-radius:4px; padding:2px 6px;
    color:#243449; overflow-wrap:anywhere;
}
.fabricops-data-contract .fabricops-guardrail-disclosure { border:1px solid var(--form-border); border-radius:6px; overflow:hidden; }
.fabricops-data-contract .fabricops-guardrail-disclosure > .widget-vbox { padding:10px; background:#fff; }
.fabricops-data-contract .fabricops-guardrail-sidebar .fabricops-guardrail-toggle {
    background:var(--form-tint); border:0; color:var(--form-text); padding:9px 10px;
    white-space:normal; text-align:left; overflow-wrap:anywhere; width:100%;
}
.fabricops-data-contract .fabricops-guardrail-toggle::before { content:'▸'; display:inline-block; width:14px; }
.fabricops-data-contract .fabricops-guardrail-toggle.mod-active::before { content:'▾'; }
.fabricops-data-contract .fabricops-guardrail-toggle .fa { display:none; }
.fabricops-data-contract .fabricops-guardrail-sidebar .fabricops-guardrail-summary {
    background:#fff; border:1px solid var(--form-border); padding:9px 10px;
    color:var(--form-text); white-space:normal; text-align:left; overflow-wrap:anywhere;
}
.fabricops-data-contract .fabricops-guardrail-detail { font-size:12px; line-height:1.5; overflow-wrap:anywhere; }
.fabricops-data-contract .fabricops-business-body {
    flex:0 1 auto; min-height:0; overflow:visible; scrollbar-gutter:auto;
}
.fabricops-data-contract .fabricops-business-footer {
    border-top:1px solid var(--form-border); padding-top:12px;
}
.fabricops-data-contract .fabricops-dq-ai-create {
    background:#f1edf8; border:1px solid #d8cfea; border-left:4px solid #6750a4;
    border-radius:6px; padding:12px;
}
.fabricops-data-contract .fabricops-dq-parameter-box { gap:8px; }
.fabricops-data-contract .fabricops-lineage-table {
    width:100%; min-width:340px; table-layout:fixed; border-collapse:collapse; font-size:11px;
}
.fabricops-data-contract .fabricops-lineage-table th {
    white-space:nowrap; overflow-wrap:normal; overflow:hidden; text-overflow:ellipsis;
}
.fabricops-data-contract .fabricops-lineage-table td {
    white-space:nowrap; overflow-wrap:normal; overflow:hidden; text-overflow:ellipsis;
}
.fabricops-data-contract .fabricops-dq-editor-heading {
    margin-top:4px; padding-top:12px; border-top:1px solid var(--form-border);
    color:var(--form-text); font-size:14px; font-weight:600;
}
.fabricops-data-contract .fabricops-delete-request {
    color:#a4262c; background:#fff; border:1px solid #a4262c;
}
.fabricops-data-contract .fabricops-contract-actions {
    width:100%; height:auto; max-height:none; overflow:visible;
}
.fabricops-data-contract .fabricops-business-chooser select { height:36px; }
.fabricops-data-contract .fabricops-dq-rule-list select {
    height:220px; min-height:160px; padding:0; border-radius:6px;
}
.fabricops-data-contract .fabricops-dq-rule-list option {
    padding:9px 10px; border-bottom:1px solid var(--form-border);
}
.fabricops-data-contract .fabricops-contract-list { overflow:visible !important; }
.fabricops-data-contract .fabricops-contract-list select {
    width:100%; min-width:0; max-width:100%; height:180px; min-height:180px;
    padding:5px; box-sizing:border-box; overflow-x:hidden; overflow-y:auto;
}
.fabricops-data-contract .fabricops-contract-list option {
    min-height:30px; padding:5px 8px; line-height:20px; box-sizing:border-box;
    max-width:100%; overflow:hidden; text-overflow:ellipsis;
}
.fabricops-data-contract .fabricops-contract-columns select {
    height:180px; min-height:130px;
}
@container (max-width:1000px) {
    .fabricops-data-contract .fabricops-contract-assistant-grid,
    .fabricops-data-contract .fabricops-contract-labeled-grid { grid-template-columns:minmax(0,1fr) !important; }
    .fabricops-data-contract .fabricops-contract-workspace { grid-template-columns:320px minmax(0,1fr) !important; }
}
@container (max-width:600px) {
    .fabricops-data-contract .fabricops-contract-workspace { grid-template-columns:220px minmax(0,1fr) !important; }
    .fabricops-data-contract .fabricops-contract-sidebar { padding:10px; }
    .fabricops-data-contract .fabricops-contract-nav button { flex-basis:100px; }
    .fabricops-data-contract .fabricops-contract-detail > .widget-vbox { padding:12px; }
    .fabricops-data-contract .fabricops-contract-selector > .widget-gridbox {
        grid-template-columns:minmax(0,1fr) !important;
        grid-template-areas:"table" "workspace" "contract" !important;
    }
    .fabricops-data-contract .fabricops-column-header { align-items:flex-start; }
    .fabricops-data-contract .fabricops-column-required-controls { flex-basis:100%; }
}

</style>"""
_COLUMN_DQ_TYPES = ("completeness", "uniqueness", "value_set", "range")
_DQ_HELP = {
    "completeness": "Limit missing values, with explicit blank-text handling.",
    "uniqueness": "All rows in duplicate key groups fail. For legacy distinct-key limits, explicitly set an accepted failure rate before updating.",
    "value_set": "Allowed Values checks whether a column value belongs to an approved governed set.",
    "range": "Value Rules apply numeric or date conditions such as below, above, between, or outside bounds.",
    "pattern": "Require populated text to match a governed regular expression.",
    "column_relationship": "Compare two columns row by row with a controlled operator.",
    "custom_expression": "Evaluate a constrained project-authored PySpark boolean Column expression.",
}


def _format_widget_exception(exc: Exception, *, phase: str) -> str:
    """Return a compact source-aware diagnostic for widget construction failures."""
    frames = traceback.extract_tb(exc.__traceback__)
    own_frames = [frame for frame in frames if frame.filename.endswith("widget_data_contract.py")]
    frame = own_frames[-1] if own_frames else (frames[-1] if frames else None)
    location = (
        f"{frame.name}() line {frame.lineno}: {frame.line or '<source unavailable>'}"
        if frame is not None
        else "<traceback unavailable>"
    )
    return (
        f"Data Contract widget failed during {phase}: {type(exc).__name__}: {exc}. "
        f"Location: {location}"
    )


def _expose_manifest(payload: dict[str, Any]) -> str:
    """Expose one canonical payload to both module and active notebook namespaces."""
    global DATA_CONTRACT_MANIFEST, DATA_CONTRACT_MANIFEST_JSON
    DATA_CONTRACT_MANIFEST = payload
    DATA_CONTRACT_MANIFEST_JSON = json.dumps(payload, indent=2, ensure_ascii=False, default=str)
    try:
        from IPython import get_ipython

        shell = get_ipython()
        if shell is not None:
            shell.user_ns["DATA_CONTRACT_MANIFEST"] = payload
            shell.user_ns["DATA_CONTRACT_MANIFEST_JSON"] = DATA_CONTRACT_MANIFEST_JSON
    except (ImportError, AttributeError):
        pass
    return DATA_CONTRACT_MANIFEST_JSON


def _parameters(row: Mapping[str, Any]) -> dict[str, Any]:
    """Return rule parameters from an authoring row or immutable manifest row."""
    value = row.get("rule_parameters", row.get("rule_parameters_json", {}))
    if isinstance(value, str):
        try:
            value = json.loads(value or "{}")
        except json.JSONDecodeError:
            return {}
    return dict(value) if isinstance(value, Mapping) else {}


def _format_decimal(value: Decimal) -> str:
    """Format a finite Decimal without insignificant trailing zeroes."""
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


def _mask_treatment_example(
    *, preserve_start: Any, preserve_end: Any, mask_character: Any = "*"
) -> tuple[str, str] | None:
    """Return an illustrative mask using the runtime's short-value safety rule."""
    source = "S1234567A"
    try:
        start = int(preserve_start)
        end = int(preserve_end)
    except (TypeError, ValueError):
        return None
    character = str(mask_character or "")
    if start < 0 or end < 0 or not character:
        return None
    if len(source) <= start + end + 1:
        return source, character * len(source)
    suffix = source[-end:] if end else ""
    return source, source[:start] + character * (len(source) - start - end) + suffix


def _bucket_treatment_example(parameters: Mapping[str, Any]) -> tuple[str, str] | None:
    """Return an example derived from approved ranges or fixed-width parameters."""
    if "bin_width" in parameters:
        try:
            width = Decimal(str(parameters.get("bin_width")))
            origin = Decimal(str(parameters.get("bin_origin", 0)))
        except (InvalidOperation, TypeError, ValueError):
            return None
        if not width.is_finite() or not origin.is_finite() or width <= 0:
            return None
        return _format_decimal(origin), (
            f"[{_format_decimal(origin)}, {_format_decimal(origin + width)})"
        )
    try:
        bins = [Decimal(str(value)) for value in parameters.get("bins", [])]
    except (InvalidOperation, TypeError, ValueError):
        return None
    labels = [str(value).strip() for value in parameters.get("labels", [])]
    if (
        not bins
        or len(bins) != len(labels)
        or any(not value.is_finite() for value in bins)
        or any(left >= right for left, right in zip(bins, bins[1:]))
        or any(not label for label in labels)
    ):
        return None
    index = 1 if len(bins) > 1 else 0
    return _format_decimal(bins[index]), labels[index]


def _sensitive_treatment_review(parameters: Mapping[str, Any]) -> str:
    """Describe the effective persisted treatment for contract review."""
    treatment = str(parameters.get("treatment") or "").lower()
    if treatment == "mask":
        start = int(parameters.get("preserve_start") or 0)
        end = int(parameters.get("preserve_end") or 0)
        character = str(parameters.get("mask_character") or "*")
        style = "Partial mask" if start or end else "Full mask"
        return (
            f"{style}; mask character: {character!r}; "
            f"preserve start: {start}; preserve end: {end}"
        )
    if treatment == "tokenize":
        return (
            "UUID tokens; repeated values share a token within one run; "
            "persistent mapping required for consistent reuse across runs"
        )
    if treatment == "bucket":
        if "bin_width" in parameters:
            return (
                "Fixed width; interval width: "
                f"{parameters.get('bin_width')}; starting point: {parameters.get('bin_origin', 0)}; "
                "lower boundary included"
            )
        bins = ", ".join(str(value) for value in parameters.get("bins", []))
        labels = ", ".join(str(value) for value in parameters.get("labels", []))
        return (
            f"Approved ranges; lower bounds: {bins or 'not configured'}; "
            f"labels: {labels or 'not configured'}; first and last ranges open-ended; "
            "each boundary from the second onward starts the next label"
        )
    if treatment == "remove":
        return "Column absent from the published dataset"
    return ""


def _sensitive_treatment_guidance(parameters: Mapping[str, Any]) -> str:
    """Render concise treatment behavior and a public-safe illustrative example."""
    treatment = str(parameters.get("treatment") or "").lower()
    mask_character = html.escape(str(parameters.get("mask_character") or "*"))
    descriptions = {
        "mask": (
            f"Replaces sensitive characters with <code>{mask_character}</code>. Full mask hides every "
            "character; partial mask preserves only the approved characters at the beginning "
            "or end. Short values that cannot be safely preserved are fully masked."
        ),
        "tokenize": (
            "Replaces original values with opaque UUID identifiers. Repeated values receive the "
            "same token within one run. Consistent reuse across runs requires a persistent token "
            "mapping. Tokenization is pseudonymisation, not "
            "guaranteed anonymisation. Original-to-token mappings are never shown here."
        ),
        "bucket": (
            "Replaces exact numeric values with configured category ranges without aggregating "
            "or removing rows."
        ),
        "remove": "Removes the entire column before downstream checks and publication.",
    }
    description = descriptions.get(treatment)
    if not description:
        return ""
    if treatment == "bucket":
        description += (
            " Fixed-width intervals use stable equal widths, include their lower boundary, and "
            "exclude their upper boundary."
            if "bin_width" in parameters else
            " Approved ranges use their supplied labels. The first label also covers values below "
            "the first configured bound; each boundary from the second onward starts the next "
            "label, and the final label is open-ended."
        )
    example: tuple[str, str] | None = None
    if treatment == "mask":
        example = _mask_treatment_example(
            preserve_start=parameters.get("preserve_start", 0),
            preserve_end=parameters.get("preserve_end", 0),
            mask_character=parameters.get("mask_character", "*"),
        )
    elif treatment == "bucket":
        example = _bucket_treatment_example(parameters)
    elif treatment == "tokenize":
        example = ("C001", "550e8400-e29b-41d4-a716-446655440000")
    elif treatment == "remove":
        example = ("NRIC", "Column removed")
    example_html = (
        "<div class='fabricops-treatment-example'><b>Example</b>"
        f"<code>{html.escape(example[0])}</code><span aria-hidden='true'>&rarr;</span>"
        f"<code>{html.escape(example[1])}</code></div>"
        if example else
        "<div class='fabricops-treatment-example'>Complete valid parameters to preview the result.</div>"
    )
    return (
        "<div class='fabricops-treatment-guide'>"
        f"<p><b>What happens</b><br>{description}</p>{example_html}</div>"
    )


def _latest(rows: list[dict[str, Any]], *identity: str) -> list[dict[str, Any]]:
    """Resolve append-only authoring rows to their latest logical configurations."""
    selected: dict[tuple[str, ...], dict[str, Any]] = {}
    for row in rows:
        key = tuple(str(row.get(name) or "") for name in identity)
        rank = (
            int(row.get("guardrail_version") or 0),
            metadata_timestamp_sort_key(row.get("_committed_at")),
            str(row.get("_activity_id") or ""),
        )
        previous = selected.get(key)
        previous_rank = (
            int(previous.get("guardrail_version") or 0),
            metadata_timestamp_sort_key(previous.get("_committed_at")),
            str(previous.get("_activity_id") or ""),
        ) if previous else None
        if previous_rank is None or rank >= previous_rank:
            selected[key] = row
    return list(selected.values())


def _manifest_sections(
    payload: dict[str, Any],
    *,
    column_profiles: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, str]:
    """Build one scannable review page from table, column, and cross-column contract rules."""
    table = payload.get("table", {})
    enrichments = payload.get("enrichment", {})
    guardrails = payload.get("guardrails", [])
    columns = table.get("columns", [])
    profiles = dict(column_profiles or {})

    column_enrichment: dict[tuple[str, str], str] = {
        (str(row.get("column_id") or ""), str(row.get("enrichment_type") or "")): str(
            row.get("value") or ""
        )
        for row in enrichments.get("columns", [])
    }
    required: set[str] = set()
    for rule in guardrails:
        if str(rule.get("guardrail_type") or "").lower() == "schema" and rule.get("is_active", True):
            required.update(_parameters(rule).get("required_columns", []))

    column_names_by_id = {
        str(row.get("column_id") or ""): str(row.get("column_name") or "")
        for row in columns
        if str(row.get("column_id") or "")
    }

    def parameter_text(row: Mapping[str, Any]) -> str:
        parts = []
        for name, value in _parameters(row).items():
            if value in (None, "", [], {}):
                continue
            if isinstance(value, list):
                display_values = (
                    [
                        column_names_by_id.get(str(item), str(item))
                        for item in value
                    ]
                    if name == "required_columns"
                    else value
                )
                shown = ", ".join(str(item) for item in display_values)
            elif isinstance(value, bool):
                shown = "Yes" if value else "No"
            else:
                shown = str(value)
            parts.append(f"{name.replace('_', ' ')}: {shown}")
        return " · ".join(parts)

    def rule_label(row: Mapping[str, Any]) -> str:
        rule_type = str(row.get("rule_type") or row.get("guardrail_type") or "")
        if rule_type == "value_set":
            mode = str(_parameters(row).get("mode") or "").lower()
            if mode == "allow":
                return "Whitelist"
            if mode == "block":
                return "Blacklist"
        return rule_type.replace("_", " ").title()

    def rule_list(rows: list[dict[str, Any]]) -> str:
        items = "".join(
            "<li><b>{}</b> · {}{}</li>".format(
                html.escape(rule_label(row)),
                html.escape(str(row.get("action") or "Warn")),
                (
                    " · " + html.escape(parameter_text(row))
                    if parameter_text(row) else ""
                ),
            )
            for row in rows
        ) or "<li>None configured</li>"
        return f"<ul>{items}</ul>"

    def business_rule_list(rows: list[dict[str, Any]]) -> str:
        if not rows:
            return "<ul><li>None configured</li></ul>"
        items = []
        for row in rows:
            params = _parameters(row)
            requirement = str(
                params.get("business_requirement") or params.get("description") or ""
            ).strip()
            columns = [str(value) for value in params.get("columns") or []]
            kind = str(row.get("rule_type") or "")
            review_required = (
                kind == "custom_expression"
                and bool(params.get("engineering_review_required", True))
            )
            review_status = str(
                params.get("engineering_review_status") or "pending"
            ).replace("_", " ").title()
            details = [
                f"<b>{html.escape(requirement or rule_label(row))}</b>",
                html.escape(rule_label(row)),
                html.escape(str(row.get("action") or "Warn")),
            ]
            if columns:
                details.append("Columns: " + html.escape(", ".join(columns)))
            if kind == "custom_expression" and params.get("expression"):
                details.append(
                    "Expression: <code>"
                    + html.escape(str(params["expression"]))
                    + "</code>"
                )
            if review_required:
                reviewer = str(params.get("engineering_reviewed_by") or "").strip()
                review = "Engineering review: " + html.escape(review_status)
                if reviewer and review_status.lower() == "approved":
                    review += " by " + html.escape(reviewer)
                details.append(review)
            else:
                details.append("Engineering review: Not required")
            items.append("<li>" + "<br>".join(details) + "</li>")
        return "<ul>" + "".join(items) + "</ul>"

    def example_values(column_id: str) -> str:
        profile = dict(profiles.get(column_id) or {})
        values = [
            value for value in list(profile.get("example_values") or [])
            if value not in (None, "")
        ][:3]
        if not values:
            fallback = []
            for name in ("min_value", "max_value"):
                value = profile.get(name)
                if value not in (None, "") and value not in fallback:
                    fallback.append(value)
            values = fallback[:2]
        if not values:
            return "<span style='color:#667085;'>—</span>"
        return "<br>".join(html.escape(str(value)) for value in values)

    active = [row for row in guardrails if row.get("is_active", True)]
    business_rules = [
        row for row in active
        if not str(row.get("column_id") or "")
        and str(row.get("guardrail_type") or "").lower() in {"data_quality", "dq"}
        and str(row.get("rule_type") or "") in {
            "column_relationship", "custom_expression"
        }
    ]
    business_rule_ids = {id(row) for row in business_rules}
    table_guardrails = [
        row for row in active
        if not str(row.get("column_id") or "") and id(row) not in business_rule_ids
    ]
    column_guardrails = [row for row in active if str(row.get("column_id") or "")]
    sensitive_by_column = {
        str(row.get("column_id") or ""): row
        for row in column_guardrails
        if str(row.get("guardrail_type") or "").lower() == "sensitive_data"
    }
    rules_by_column: dict[str, list[dict[str, Any]]] = {}
    for rule in column_guardrails:
        if str(rule.get("guardrail_type") or "").lower() == "sensitive_data":
            continue
        rules_by_column.setdefault(str(rule.get("column_id") or ""), []).append(rule)

    def sensitive_text(column_id: str) -> str:
        rule = sensitive_by_column.get(column_id)
        if not rule:
            return "Not PII"
        parameters = _parameters(rule)
        pii_type = str(parameters.get("pii_type") or "direct").lower()
        label = PII_LABELS.get(pii_type, pii_type.replace("_", " ").title())
        treatment_value = str(parameters.get("treatment") or rule.get("rule_type") or "")
        treatment = treatment_value.replace("_", " ").title()
        action = str(rule.get("action") or "Warn")
        detail = f"{label} · {treatment}" if treatment else label
        configuration = _sensitive_treatment_review(
            {**parameters, "treatment": treatment_value}
        )
        configuration_html = (
            "<br><span style='color:#667085;'>"
            + html.escape(configuration)
            + "</span>"
            if configuration else ""
        )
        return (
            f"{html.escape(detail)}<br><span style='color:#667085;'>"
            f"{html.escape(action)}</span>{configuration_html}"
        )

    def column_rule_list() -> str:
        if not rules_by_column and not sensitive_by_column:
            return "<ul><li>None configured</li></ul>"
        items = []
        column_names = {
            str(row.get("column_id") or ""): str(row.get("column_name") or "")
            for row in columns
        }
        for column_id in sorted(set(rules_by_column) | set(sensitive_by_column)):
            name = column_names.get(column_id, column_id or "Unknown column")
            rules = []
            sensitive = sensitive_by_column.get(column_id)
            if sensitive:
                rules.append(
                    "<div><b>Sensitive Data</b> · "
                    + sensitive_text(column_id)
                    + "</div>"
                )
            rules.extend(
                "<div><b>{}</b> · {}{}</div>".format(
                    html.escape(rule_label(rule)),
                    html.escape(str(rule.get("action") or "Warn")),
                    (
                        "<br><span style='color:#667085;'>"
                        + html.escape(parameter_text(rule))
                        + "</span>"
                        if parameter_text(rule) else ""
                    ),
                )
                for rule in rules_by_column.get(column_id, [])
            )
            items.append(
                "<li><b>" + html.escape(name) + "</b><div style='margin-top:4px;'>"
                + "".join(rules) + "</div></li>"
            )
        return "<ul>" + "".join(items) + "</ul>"

    column_rows = "".join(
        "<tr>"
        "<td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>"
        "</tr>".format(
            html.escape(str(row.get("column_name") or "")),
            example_values(str(row.get("column_id") or "")),
            html.escape(str(row.get("data_type") or "")),
            "Yes" if row.get("column_id") in required or row.get("column_name") in required else "No",
            sensitive_text(str(row.get("column_id") or "")),
            html.escape(column_enrichment.get(
                (str(row.get("column_id") or ""), "Classification"), ""
            )) or "<span style='color:#667085;'>—</span>",
            (
                "<details style='max-width:220px;'>"
                "<summary style='display:block;cursor:pointer;overflow:hidden;text-overflow:ellipsis;"
                "white-space:nowrap;max-width:220px;' title='Click to expand'>"
                + html.escape(column_enrichment.get(
                    (str(row.get("column_id") or ""), "Description"), ""
                ))
                + "</summary>"
                + "<div style='margin-top:6px;white-space:normal;overflow-wrap:anywhere;"
                "line-height:1.45;color:#344054;'>"
                + html.escape(column_enrichment.get(
                    (str(row.get("column_id") or ""), "Description"), ""
                ))
                + "</div></details>"
                if column_enrichment.get(
                    (str(row.get("column_id") or ""), "Description"), ""
                )
                else "<span style='color:#667085;'>—</span>"
            ),
        )
        for row in columns
    )
    guardrail_count = len(table_guardrails) + len(column_guardrails) + len(business_rules)
    guardrail_sections = (
        "<div style='margin-top:8px;'><b>Table</b>"
        + rule_list(table_guardrails)
        + "</div>"
        "<div style='margin-top:8px;'><b>Columns</b>"
        + column_rule_list()
        + "</div>"
        "<div style='margin-top:8px;'><b>DQ Rules</b>"
        + business_rule_list(business_rules)
        + "</div>"
    )
    details = (
        "<details open><summary><b>Column definitions</b> · "
        f"{len(columns)} columns</summary>"
        "<div style='overflow-x:auto;'>"
        "<table style='width:100%;font-size:12px;table-layout:fixed;'><thead><tr>"
        "<th style='width:18%;'>Column</th><th style='width:18%;'>Examples</th>"
        "<th style='width:11%;'>Datatype</th><th style='width:10%;'>Required</th>"
        "<th style='width:12%;'>Sensitive</th><th style='width:13%;'>Classification</th>"
        "<th style='width:18%;'>Description</th>"
        f"</tr></thead><tbody>{column_rows}</tbody></table></div></details>"
        "<details><summary><b>Guardrails</b> · "
        f"{guardrail_count} configured</summary>{guardrail_sections}</details>"
    )
    return {"Review": details}

def _manifest_html(payload: dict[str, Any]) -> str:
    """Render the human and exact JSON views from the same canonical dictionary."""
    sections = _manifest_sections(payload)
    exact_json = html.escape(_expose_manifest(payload))
    return "".join(sections.values()) + (
        f"<details><summary>Exact JSON manifest</summary><pre>{exact_json}</pre></details>"
    )


def _profile_html(context: dict[str, Any]) -> str:
    """Render a compact datatype-aware summary of governed profile evidence."""
    if context.get("kind") == "unavailable":
        return "<p>" + html.escape(str(context.get("message") or "Not yet profiled.")) + "</p>"

    profile = dict(context.get("profile") or {})
    values = list(context.get("values") or [])
    if not profile:
        return "<p>Not yet profiled.</p>"

    def shown(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, float):
            return f"{value:,.3f}".rstrip("0").rstrip(".")
        return str(value)

    def bold_value(value: Any, suffix: str = "") -> str:
        return f"<b>{html.escape(shown(value))}{suffix}</b>"

    facts = []
    if profile.get("profile_scope") == "bounded_selection":
        facts.append("Sampled evidence: arbitrary bounded selection (at most " +
                     html.escape(str(profile.get("profiling_max_rows"))) +
                     " rows). All counts, uniqueness and distributions describe the selection only; full-table facts are unknown.")
    elif profile.get("profile_scope") == "supplied_dataframe":
        facts.append("Scope: supplied DataFrame; complete physical table coverage is unverified.")
    for key, label, suffix in (
        ("row_count", "Row count", ""),
        ("distinct_count", "Distinct count", ""),
        ("distinct_percent", "Distinct percent", "%"),
        ("null_count", "Null count", ""),
        ("null_percent", "Null percent", "%"),
    ):
        if profile.get(key) is not None:
            facts.append(f"{label}: {bold_value(profile.get(key), suffix)}")

    lines = []
    if facts:
        lines.append(" · ".join(facts))

    range_facts = []
    if profile.get("min_value") is not None:
        range_facts.append(f"Min value: {bold_value(profile.get('min_value'))}")
    if profile.get("max_value") is not None:
        range_facts.append(f"Max value: {bold_value(profile.get('max_value'))}")
    if range_facts:
        lines.append(" · ".join(range_facts))

    distribution = []
    for key, label in (
        ("median_value", "Median value"),
        ("percentile_25_value", "Percentile 25 value"),
        ("percentile_75_value", "Percentile 75 value"),
        ("mean_value", "Mean value"),
        ("stddev_value", "Stddev value"),
    ):
        if profile.get(key) is not None:
            distribution.append(f"{label}: {bold_value(profile.get(key))}")
    if distribution:
        lines.append(" · ".join(distribution))

    if values:
        frequencies = []
        for item in values[:3]:
            parts = []
            if item.get("value") is not None:
                parts.append(f"Value: {bold_value(item.get('value'))}")
            if item.get("count") is not None:
                parts.append(f"Count: {bold_value(item.get('count'))}")
            if item.get("percent") is not None:
                parts.append(f"Percent: {bold_value(item.get('percent'), '%')}")
            if parts:
                frequencies.append(" · ".join(parts))
        lines.extend(frequencies)
    elif (
        profile.get("distinct_percent") is not None
        and float(profile["distinct_percent"]) >= 80.0
        and "date" not in str(profile.get("data_type") or "").lower()
        and "timestamp" not in str(profile.get("data_type") or "").lower()
    ):
        lines.append("Values are highly unique, so value frequency profiling was skipped.")

    if not lines:
        return "<p>A profile record exists, but no metrics were recorded for this column.</p>"
    return "<p style='margin:0;line-height:1.65;'>" + "<br>".join(lines) + "</p>"

def _ai_usage_html(records: list[dict[str, Any]]) -> str:
    """Render measured tokens and an explicitly estimated Fabric AI capacity equivalent."""
    # Microsoft AI Functions billing rates, checked 7 November 2026, per 1,000 tokens.
    rates = {"gpt-5-mini": (Decimal("8.40"), Decimal("0.84"), Decimal("67.23")),
             "gpt-5.1": (Decimal("42.02"), Decimal("4.20"), Decimal("336.13"))}
    rates["gpt-5-mini-2025-08-07"] = rates["gpt-5-mini"]
    rates["gpt-5.1-2025-11-13"] = rates["gpt-5.1"]
    fields = ("input_tokens", "output_tokens", "cached_tokens", "reasoning_tokens")
    totals = {field: 0 for field in fields}
    known = {field: 0 for field in fields}
    missing = {field: False for field in fields}
    estimated = Decimal(0)
    estimated_rows = 0
    estimate_partial = False
    cache_assumed = False
    rows = []
    labels = {"table_enrichment": "Table description", "column_enrichment": "Column description",
              "grain_key": "Grain and row key", "sensitive_data": "Sensitive Data",
              "business_rule_ai": "Data Quality suggestions"}

    def count(value: Any) -> int | None:
        if value is None or isinstance(value, bool):
            return None
        try:
            number = Decimal(str(value))
            return int(number) if number.is_finite() and number >= 0 and number == number.to_integral_value() else None
        except (InvalidOperation, ValueError, OverflowError):
            return None

    def shown(value: int, available: int, partial: bool) -> str:
        if not available:
            return "Unavailable"
        return f"{value:,}" + (" (partial)" if partial else "")

    for index, record in enumerate(records, 1):
        stats = record.get("statistics") or []
        values = {field: 0 for field in fields}
        available = {field: 0 for field in fields}
        partial = {field: not bool(stats) for field in fields}
        request_estimate = Decimal(0)
        request_priced = 0
        request_partial = not bool(stats)
        for stat in stats:
            counts = {field: count(stat.get(field)) for field in fields}
            for field, value in counts.items():
                if value is None:
                    partial[field] = True
                else:
                    values[field] += value
                    available[field] += 1
            input_count, output_count = counts["input_tokens"], counts["output_tokens"]
            cached_count = counts["cached_tokens"]
            model_rates = rates.get(str(stat.get("model") or record.get("model") or ""))
            if model_rates is None or input_count is None or output_count is None:
                request_partial = True
                continue
            if cached_count is None:
                cache_assumed = True
                cached_count = 0
            if cached_count > input_count:
                request_partial = True
                continue
            input_rate, cached_rate, output_rate = model_rates
            # Cached input and reasoning are breakdowns of input/output respectively.
            request_estimate += ((input_count - cached_count) * input_rate
                                 + cached_count * cached_rate + output_count * output_rate) / 1000
            request_priced += 1
        for field in fields:
            totals[field] += values[field]
            known[field] += available[field]
            missing[field] |= partial[field]
        estimated += request_estimate
        estimated_rows += request_priced
        estimate_partial |= request_partial
        operation = str(record.get("operation") or "AI request")
        model = str(record.get("model") or "Unknown")
        capacity = (f"{request_estimate:,.3f}" + (" (partial)" if request_partial else "")) if request_priced else "Unavailable"
        rows.append(
            f"<tr><td>{index}</td><td>{html.escape(labels.get(operation, operation))}</td>"
            f"<td>{html.escape(model)}</td>"
            f"<td><strong>{shown(values['input_tokens'], available['input_tokens'], partial['input_tokens'])}</strong></td>"
            f"<td><strong>{shown(values['output_tokens'], available['output_tokens'], partial['output_tokens'])}</strong></td>"
            f"<td>{capacity}</td></tr>"
        )
    unsaved = sum(record.get("persistence_status") == "unconfirmed" for record in records)
    persistence_notice = (f"<p><strong>{unsaved} AI usage audit write(s) unconfirmed.</strong> Check Metadata access; requests were not replayed.</p>" if unsaved else "")
    input_total = shown(totals["input_tokens"], known["input_tokens"], missing["input_tokens"]) if records else "0"
    output_total = shown(totals["output_tokens"], known["output_tokens"], missing["output_tokens"]) if records else "0"
    capacity_total = (
        f"{estimated:,.3f} CU-seconds ({estimated / 3600:,.6f} CU-hours)"
        + (" — partial estimate" if estimate_partial else "")
    ) if estimated_rows or not records else "Unavailable"
    table = (
        "<div style='overflow:auto;max-height:360px;max-width:100%;'><table class='fabricops-ai-usage-table'>"
        "<caption>Recorded AI requests for this widget instance</caption>"
        "<thead><tr><th>#</th><th>Operation</th><th>Model</th><th>Input tokens</th>"
        "<th>Output tokens</th><th>Estimated CU-seconds</th></tr></thead><tbody>"
        + "".join(rows) + "</tbody></table></div>"
    ) if rows else "<p>No AI requests made by this widget.</p>"
    return (
        persistence_notice +
        "<h4 style='margin:0 0 12px;'>AI usage</h4>"
        f"<p><strong>Total input tokens: {input_total}</strong><br>"
        f"<strong>Total output tokens: {output_total}</strong></p>"
        + ("<p style='font-size:12px;'>Included breakdowns — cached input: "
           + shown(totals["cached_tokens"], known["cached_tokens"], missing["cached_tokens"])
           + "; reasoning output: " + shown(totals["reasoning_tokens"], known["reasoning_tokens"], missing["reasoning_tokens"])
           + ".</p>" if records else "")
        + f"<p>Estimated AI capacity: <strong>{capacity_total}</strong></p>"
        + table
        + ("<p>Totals include available statistics only; missing values are not counted as zero.</p>"
           if any(missing.values()) and records else "")
        + ("<p>Cache statistics were unavailable for some requests; their estimate assumes no cached-input discount.</p>"
           if cache_assumed else "")
        + "<details><summary>Capacity and money estimate</summary>"
        "<p>Rates checked 7 Nov 2026; CU-seconds per 1,000 tokens: "
        "gpt-5-mini: input 8.40, cached input 0.84, output 67.23; "
        "gpt-5.1: input 42.02, cached input 4.20, output 336.13. Rates can change. "
        "Cached input is included in input tokens; reasoning is included in output tokens and is not added again.</p>"
        "<p>Money equivalent ≈ estimated CU-hours × (your capacity hourly price ÷ capacity CUs). "
        "This allocates capacity cost; it is not an invoice amount. Spark compute is separate.</p>"
        "<p>Verify consumption in <a href='https://learn.microsoft.com/en-us/fabric/enterprise/metrics-app'>"
        "Fabric Capacity Metrics</a>. <a href='https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/billing'>"
        "Microsoft AI Functions billing rates</a>.</p></details>"
        "<details><summary>Raw statistics</summary><pre style='white-space:pre-wrap;max-height:240px;overflow:auto;'>"
        + html.escape(json.dumps(records, ensure_ascii=False, indent=2, default=str)) + "</pre></details>"
    )


def widget_data_contract(
    *, table_id: str | None = None, contract_version: int | None = None,
    context: Any = None,
    ai_model: str | None = None, ai_reasoning_effort: str | None = None,
    ai_verbosity: str | None = None,
) -> dict[str, Any]:
    """Open the unified governance authoring and lifecycle experience for Data Contracts.

    Spark is resolved automatically from the existing execution session.
    No session is created; Spark-dependent work raises
    ``RuntimeError`` when no session is available.

    Parameters
    ----------
    table_id : str, optional
        Initial canonical governed table identity. If omitted, select it in the widget.
    contract_version : int, optional
        Initial exact lifecycle version. If omitted, the newest version is selected.
    context : object, optional
        FabricOps runtime context normally established by ``00_env_config``.
    ai_model : str, optional
        Built-in Fabric model: ``gpt-5-mini`` or ``gpt-5.1``. Overrides configuration.
    ai_reasoning_effort : str, optional
        ``minimal``, ``low``, ``medium``, or ``high``. Overrides configuration.
    ai_verbosity : str, optional
        ``low``, ``medium``, or ``high``. Overrides configuration. None uses configuration.
        Omitted overrides use ``GOVERNANCE_CONFIG.ai_enrichment``, then package defaults.

    Returns
    -------
    dict
        Current selector, editor, lifecycle state, and callable authoring actions.
        Retain this exact instance for ``ai_settings``, ``ai_usage``, and
        ``_ai_diagnostics`` (keyed by contract/version and operation). Raw exception
        chains in diagnostics are for maintainers and can include provider context;
        review before sharing. Opening makes no AI requests.

    Raises
    ------
    ValueError
        If an identity, authored record, or lifecycle action is invalid.
    RuntimeError
        If configured metadata routing or a lifecycle mutation fails.

    Notes
    -----
    Authoring, review, and freezing route through the configured central Governance
    Metadata Lakehouse even when the notebook workspace is not a pipeline environment.
    Tables retain their selected Catalogue observation. Named file datasets share
    the selector; enter a validated configured Files path and reader settings to
    observe a new file schema without registering a table. File contracts preserve
    Source ID and exact format/options through Save, Freeze and Activation.
    Returned state uses source_id for files and table_id for physical tables;
    dataset_id identifies either selection. File profiles remain session-only.
    Activation and governed execution still require configured environment mapping.
    Save overwrites the complete canonical JSON for the selected draft version, then reloads
    that exact version. A new draft is seeded from the previous frozen version when one exists.
    Engineering processing is reviewed through Pipeline Activation and is not authored in contracts.
    Profile context remains read-only and is never added
    to the canonical payload. Immutable versions are review-only. Grain description, selected key combination, and
    optional enforcement are independent. Enabling Grain defaults to Block.
    The sidebar includes collapsible read-only summaries of configured Read and Write
    rules. These summaries do not execute validation or navigate authoring controls.
    The Data Quality section is the single DQ authoring surface. Governance can add
    any supported deterministic rule manually, or generate transient proposals
    from business language when AI is enabled. Proposals require explicit review
    and addition. Both paths create the same editable Guardrail records; the
    Columns section contains column metadata and non-DQ settings only.
    Open Data Contract loads a manual-first editor without AI inference or AI-only
    profile reads. Top navigation keeps Table, Columns, Data Quality, Review,
    and AI Usage above the editor; lifecycle actions remain in the sidebar.
    Every AI request requires an explicit Generate, Suggest or Re-run action.
    Suggestions persist during navigation and require explicit acceptance.
    Switching columns reuses cached profile reads and suggestions.
    Long operations show an animated progress indicator and record elapsed seconds in
    ``_operation_timings``. Spark stays on the notebook thread. Text authoring updates
    on blur or Enter, while searches remain live. Full Review content is built on demand.
    Save and Freeze validate pending editor input through both buttons and returned actions.
    Optional AI request failures do not block valid manually authored contracts.
    Manual Completeness, Uniqueness, Value Set, Range, and Pattern authoring can
    stage the same configuration as one independent rule per selected column.
    Uniqueness can instead treat selected columns as one composite key.
    DQ authoring uses Warn/Block and accepted failure rate percent.
    Completeness counts missing rows; Uniqueness counts all duplicate-group rows.
    Legacy distinct-key limits retain their runtime meaning and require an explicit
    failure rate when edited.
    Allowed values, range, pattern, relationship, and custom row rules can use
    maximum failure percent. Conditional rules use matching applicable rows;
    null values ignored by value checks are not counted as passing rows.
    Prohibited-value lists remain strict. Required/Schema, Grain, Sensitive
    Data and Freshness do not gain a DQ row-percentage setting.
    Actual violation counts remain visible even when within the authored limit.
    Missing AI configuration disables AI actions for the widget session while
    manual authoring remains available. Execution and provider failures show a
    retryable message. Technical failure details are retained in the returned
    state rather than shown in the editor.
    When enabled through ``GOVERNANCE_CONFIG.ai_enrichment`` in ``00_env_config``,
    Sensitive Data AI assesses canonical columns as Direct PII, Indirect PII, or
    Not PII from governed metadata and profile evidence. Editable draft state remains
    separate until Governance accepts a suggestion. Manual Description or Classification
    edits mark dependent advice stale for explicit re-run. AI never saves, freezes,
    activates, or enforces a contract; runtime Sensitive Data enforcement remains deterministic.
    Sensitive Data offers Mask for categorical/text columns, Bucket for numeric
    columns, and Tokenize/Remove for either. Dates offer Tokenize/Remove; complex
    types offer Remove. Text defaults to full masking; partial preservation is optional.
    Numeric buckets use approved fixed ranges or an anchored interval width.
    Text grouping and distribution-derived boundaries belong in Engineering
    exploration and transformations. AI suggestions always receive governed
    schema and contract metadata. When profiling exists, they also receive profile
    summaries including min/max and the three most frequent values.
    Treatment failures always block.

    FabricOps AI helper requests automatically append measured token usage to
    ``misc.AI_TOKEN_USAGE`` in the configured Metadata Lakehouse. This standalone
    widget telemetry table is created on its first write; it is excluded from
    ``setup_metadata_tables()`` and the canonical Metadata model.
    ``gpt-5-mini`` is the default; ``ai_model`` can explicitly select ``gpt-5.1``.
    Prompts and generated text are not stored. Missing usage statistics remain
    unavailable. Audit write failures are shown in AI usage without replaying requests.

    Examples
    --------
    >>> state = widget_data_contract(table_id="table-orders", ai_model="gpt-5.1", ai_reasoning_effort="high")
    >>> state["refresh_manifest"]()

    See Also
    --------
    setup_pipeline

    """
    startup = shared.WidgetStartup("Data Contract")
    timing_log: list[dict[str, Any]] = []
    timing_panel = None

    def record_timing(operation: str, seconds: float, status: str = "ok") -> None:
        entry = {"operation": operation, "seconds": round(seconds, 3), "status": status}
        timing_log.append(entry)
        if len(timing_log) > 100:
            del timing_log[:-100]
        if timing_panel is not None:
            refresh_timing_panel()

    def refresh_timing_panel() -> None:
        if timing_panel is None:
            return
        rows = "".join(
            "<tr><td style='padding:3px 12px 3px 0'>" + html.escape(item["operation"])
            + "</td><td style='text-align:right;padding-right:12px'>" + f'{item["seconds"]:.3f}'
            + "</td><td>" + html.escape(item["status"]) + "</td></tr>"
            for item in timing_log
        )
        timing_panel.value = (
            "<details style='font-size:12px;margin:8px 0'><summary style='cursor:pointer'>"
            "Performance timings (kernel elapsed seconds)</summary>"
            "<table><thead><tr><th align='left'>Operation</th><th>Seconds</th><th>Status</th></tr></thead>"
            + "<tbody>" + rows + "</tbody></table>"
            "<div style='color:#667085'>Includes Spark execution and Python work; "
            "browser paint and notebook cold start are not measured.</div></details>"
        )
    with startup.phase("initialization", "Resolving FabricOps configuration…"):
        config, active_workspace_id, resolved = resolve_fabric_context(context=context)
        authoring_workspace_id = active_workspace_id
        path_config = (
            config.get("path_config") if isinstance(config, Mapping)
            else getattr(config, "path_config", None)
        )
        paths = (
            path_config.get("paths", path_config) if isinstance(path_config, Mapping)
            else getattr(path_config, "paths", {})
        )
        metadata_routes = sorted(
            str(workspace_id)
            for workspace_id, targets in paths.items()
            if isinstance(targets, Mapping) and "Metadata" in targets
        )
        if active_workspace_id in metadata_routes:
            routing_workspace_id = active_workspace_id
        elif metadata_routes:
            routing_workspace_id = metadata_routes[0]
        else:
            raise ValueError("FabricOps Metadata Lakehouse is not configured for any workspace.")
        active_workspace_id = routing_workspace_id
    governance_config = getattr(config, "governance_config", None)
    configured_ai = dict(getattr(governance_config, "ai_enrichment", {}) or {})
    for key, override in (("model_deployment_name", ai_model),
                          ("reasoning_effort", ai_reasoning_effort), ("verbosity", ai_verbosity)):
        if override is not None:
            configured_ai[key] = override
    ai_configuration_error = ""
    try:
        ai_enrichment = validate_ai_enrichment(configured_ai)
    except (TypeError, ValueError) as exc:
        ai_configuration_error = str(exc)
        ai_enrichment = validate_ai_enrichment({"enabled": False})
    classification_levels = [
        str(value).strip()
        for value in (getattr(governance_config, "classification_levels", []) or [])
        if str(value).strip()
    ] or ["Public", "Restricted", "Confidential", "Highly Sensitive"]
    classification_options = ("", *classification_levels)
    with startup.phase("spark_loading", "Resolving the Spark session…"):
        spark = get_spark_session(context=context)
    with startup.phase("metadata_loading", "Loading configured metadata…"):
        catalogue = contracts.list_contract_governance_state(
            config=config, active_workspace_id=active_workspace_id,
            spark_session=spark, metadata_workspace_id=routing_workspace_id,
            timing_callback=record_timing,
        )
        table_rows = catalogue["tables"]
        file_rows = contracts.contract_file_datasets(catalogue["contracts"], config=config, workspace_id=active_workspace_id)
        observed_files = contracts.pipeline_file_datasets(catalogue.get("pipeline_runs", []), config=config, workspace_id=active_workspace_id)
        existing_files = {row["source_id"]: row for row in file_rows}
        for row in observed_files:
            existing_files.setdefault(row["source_id"], row)
        file_rows = list(existing_files.values())
        if table_id is not None and str(table_id) not in {str(row.get("table_id")) for row in table_rows}:
            raise ValueError("table_id has no active table-level Catalogue row in central governance metadata.")
    state: dict[str, Any] = {
        "authoring_workspace_id": authoring_workspace_id,
        "workspace_id": None, "dataset_id": None, "table_id": None, "source_id": None, "contract_version": None,
        "pending_dataset_id": table_id, "pending_table_id": table_id, "pending_source_id": None, "pending_contract_version": contract_version,
        "contracts": catalogue["contracts"], "tables": table_rows, "current": None,
        "manifest": None, "profile_context": None, "message": "", "_controls": {},
        "_column_drafts": {}, "_profile_cache": {},
        "_ai_suggestions": {}, "_ai_errors": {}, "_ai_diagnostics": {},
        "_timing_log": timing_log,
        "ai_settings": {key: ai_enrichment[key] for key in ("model_deployment_name", "reasoning_effort", "verbosity")},
        "ai_usage": [],
        "_pending_enrichment": {}, "_pending_guardrails": {}, "_validation_errors": {},
        "_column_dq_selection": {}, "_selector_refreshing": False, "dirty": False,
        "_ai_unavailable": ai_configuration_error, "_ai_failure": "", "_ai_failure_category": "",
        "_ai_failure_diagnostic": {}, "_ai_buttons": [],
    }
    widgets = shared.require_ipywidgets()
    status = shared.status_message(widgets)
    operation_progress = widgets.HTML(layout=widgets.Layout(width="100%"))
    operation_progress.add_class("fabricops-operation-progress")
    timing_panel = widgets.HTML(layout=widgets.Layout(width="100%"))
    refresh_timing_panel()
    state["_operation_timings"] = []
    state["_busy_depth"] = 0

    def loading_html(label: str) -> str:
        """Animate in the browser while Spark blocks the notebook thread."""
        return (
            "<div role='status' aria-live='polite' aria-busy='true' style='width:100%;'>"
            f"<div style='font-size:12px;margin-bottom:4px;'>{html.escape(label)}</div>"
            f"<progress aria-label='{html.escape(label, quote=True)}' "
            "style='display:block;width:100%;height:6px;accent-color:var(--form-accent);'></progress>"
            "</div>"
        )

    def busy_action(label: str, *, ai_request: bool = False):
        """Show progress before blocking work and restore navigation on every exit."""
        def decorate(callback):
            @wraps(callback)
            def run(*args, **kwargs):
                if ai_request and state["_busy_depth"]:
                    return None
                outermost = state["_busy_depth"] == 0
                locked = []
                if outermost:
                    controls = state["_controls"]
                    candidates = [controls.get(key) for key in (
                        "top_nav", "table", "workspace_select", "contract", "column_select",
                        "open", "save_data_contract", "discard_data_contract",
                        "freeze", "freeze_confirm", "change_table", "confirm_exit_discard",
                        "confirm_discard_data_contract",
                    )] + state["_ai_buttons"]
                    seen = set()
                    for control in candidates:
                        if control is not None and id(control) not in seen and not control.disabled:
                            seen.add(id(control))
                            locked.append(control)
                            control.disabled = True
                state["_busy_depth"] += 1
                began = perf_counter()
                operation_progress.value = loading_html(label)
                status_value = "ok"
                try:
                    return callback(*args, **kwargs)
                except Exception:
                    status_value = "failed"
                    raise
                finally:
                    elapsed = perf_counter() - began
                    record_timing(label, elapsed, status_value)
                    state["_operation_timings"].append({"operation": label, "seconds": elapsed})
                    del state["_operation_timings"][:-100]
                    state["_busy_depth"] -= 1
                    if outermost:
                        for control in locked:
                            if not getattr(control, "closed", False):
                                control.disabled = False
                        refresh_ai_controls = state.get("_refresh_ai_controls")
                        if state.get("current") and callable(refresh_ai_controls):
                            refresh_ai_controls()
                        if not ai_available():
                            for control in state["_ai_buttons"]:
                                control.disabled = True
                        operation_progress.value = (
                            "<div role='status' style='font-size:12px;color:#667085;'>"
                            "Ready.</div>"
                        )
            return run
        return decorate
    top_nav = widgets.ToggleButtons(
        options=_TABS,
        value="Table",
        layout=widgets.Layout(width="100%"),
    )
    top_nav.add_class("fabricops-contract-nav")
    left = widgets.VBox(
        layout=widgets.Layout(
            width="100%", min_width="0", max_width="100%",
            border="1px solid #e1e6eb", padding="20px", gap="8px",
            align_items="stretch",
        )
    )
    right = widgets.VBox(
        layout=widgets.Layout(
            width="100%", min_width="0", max_width="100%",
            border="1px solid #e1e6eb", padding="20px 24px", gap="10px",
            align_items="stretch",
        )
    )
    left.add_class("fabricops-contract-sidebar")
    right.add_class("fabricops-contract-detail")
    right_column = widgets.VBox(
        [right], layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
    )
    workspace = widgets.GridBox(
        [left, right_column],
        layout=widgets.Layout(
            width="100%", min_width="0", max_width="100%",
            grid_template_columns="480px minmax(0, 1fr)",
            grid_gap="12px", align_items="flex-start", overflow="visible",
        ),
    )
    workspace.add_class("fabricops-contract-workspace")
    sidebar_actions = widgets.VBox(
        layout=widgets.Layout(
            width="100%", height="auto", overflow="visible", display="none",
        )
    )
    sidebar_actions.add_class("fabricops-contract-actions")
    section_heading = widgets.HTML()
    section_heading.add_class("fabricops-contract-section-heading")
    sidebar_content: tuple[Any, ...] = ()
    view_content: dict[str, tuple[tuple[Any, ...], tuple[Any, ...]]] = {}

    def ai_runtime_context(column_id: str | None = None) -> dict[str, Any]:
        """Route usage to central Metadata while preserving notebook and asset identity."""
        contract = (state.get("current") or {}).get("contract") or {}
        return {**resolved, "config": config, "scope_workspace_id": routing_workspace_id,
                "ai_usage_metadata": {"table_id": None if str(state.get("dataset_id")).startswith("file:") else state.get("dataset_id"), "column_id": column_id,
                                      "contract_id": contract.get("contract_id"),
                                      "contract_version": state.get("contract_version"),
                                      "evidence_workspace_id": active_workspace_id}}

    def apply_view(*_args: Any) -> None:
        selected_view = str(top_nav.value)
        left_children, right_children = view_content.get(selected_view, ((), ()))
        left.children = sidebar_content
        section_heading.value = f"<h3 style='margin:0;'>{html.escape(selected_view)}</h3>"
        right.children = (section_heading, *left_children, *right_children)
        if selected_view == "Data Quality":
            refresh_dq_rules = state.get("_refresh_dq_rules")
            if callable(refresh_dq_rules):
                refresh_dq_rules()
        if selected_view == "Columns":
            refresh_column_view = state.get("_refresh_column_view")
            if callable(refresh_column_view):
                refresh_column_view()
            load_selected_profile = state.get("_load_selected_profile")
            if callable(load_selected_profile):
                load_selected_profile()
        elif str(top_nav.value) == "Review":
            refresh_review = state.get("_refresh_review")
            if callable(refresh_review):
                try:
                    refresh_review()
                except Exception as exc:
                    set_status(_format_widget_exception(exc, phase="review context"), error=True)

    top_nav.observe(apply_view, names="value")

    def set_status(message: str, *, error: bool = False, warning: bool = False) -> None:
        state["message"] = message
        colour = "#a4262c" if error else "#8a6d1d" if warning else "#107c10"
        status.value = f'<div style="color:{colour};font-weight:600;">{html.escape(message)}</div>'

    def blocking_validation_errors() -> dict[str, str]:
        """Exclude optional AI generation failures from authored contract validation."""
        return {key: value for key, value in state["_validation_errors"].items()
                if key != "business_rule_ai"}

    def has_pending_authoring_changes() -> bool:
        current = state.get("current")
        if not current:
            return False
        scope = (str(current["contract_id"]), int(current["contract_version"]))
        return bool(state.get("dirty") or blocking_validation_errors()
                    or state["_column_drafts"].get(scope))

    def validate_authoring_session(action: str) -> None:
        errors = blocking_validation_errors()
        if errors:
            raise ValueError(
                f"Complete the current draft configuration before {action}: "
                + str(next(iter(errors.values())))
            )
        current = state["current"]
        scope = (str(current["contract_id"]), int(current["contract_version"]))
        if state["_column_drafts"].get(scope):
            raise ValueError(
                f"Complete the retained Column edits before {action} the Data Contract."
            )

    def refresh_manifest() -> dict[str, Any] | None:
        current = state.get("current")
        if not current:
            return None
        if str(current["contract"].get("status") or "").lower() == "draft":
            payload, warnings = contracts.assemble_contract_payload(
                draft=current["contract"],
                catalogue_rows=current.get("catalogue_rows", []),
                enrichment_rows=current.get("enrichment", []),
                guardrail_rows=current.get("guardrails", []),
                workspace_id=active_workspace_id,
                allow_incomplete_grain=True,
            )
            state["manifest_warnings"] = warnings
        else:
            payload = current["payload"]
            state["manifest_warnings"] = []
        state["manifest"] = payload
        _expose_manifest(payload)
        refresh_sidebar = state.get("_refresh_guardrail_sidebar")
        if callable(refresh_sidebar):
            refresh_sidebar()
        return payload

    def select(selected_table: str, version: int | None = None) -> dict[str, Any] | None:
        state.pop("_refresh_guardrail_sidebar", None)
        state["_validation_errors"].clear()
        state["dataset_id"] = str(selected_table or "").strip() or None
        is_file = str(state["dataset_id"]).startswith("file:")
        state["table_id"] = None if is_file else state["dataset_id"]
        state["source_id"] = state["dataset_id"] if is_file else None
        matches = [
            row for row in state["contracts"]
            if str(row.get("source_id") or row.get("table_id") or "") == str(state["dataset_id"] or "")
        ]
        if not matches:
            state["current"] = None
            return None
        if version is None:
            chosen = matches[0]
        else:
            chosen = next(
                (
                    row for row in matches
                    if int(row.get("contract_version") or 0) == int(version)
                ),
                None,
            )
            if chosen is None:
                raise ValueError(
                    f"Data Contract v{int(version)} was not found for table {state['dataset_id']}."
                )
        state["contract_version"] = int(chosen["contract_version"])
        began = perf_counter()
        try:
            state["current"] = contracts.get_contract_review_state(
                config=config, active_workspace_id=active_workspace_id, spark_session=spark,
                contract_id=str(chosen["contract_id"]), contract_version=state["contract_version"],
                metadata_workspace_id=routing_workspace_id,
            )
        finally:
            state["_operation_timings"].append({"operation": "Loading contract metadata", "seconds": perf_counter() - began})
        state["_saved_payload"] = json.loads(
            str(state["current"]["contract"].get("contract_payload_json") or "{}")
        )
        scope = (str(chosen["contract_id"]), state["contract_version"])
        state["dirty"] = bool(
            state["_pending_enrichment"].get(scope)
            or state["_pending_guardrails"].get(scope)
            or state["_column_drafts"].get(scope)
        )
        refresh_manifest()
        return state["current"]

    def new_draft() -> dict[str, Any]:
        if not state.get("dataset_id") or not state.get("workspace_id"):
            raise ValueError("Select a dataset and workspace before creating a draft.")
        draft = contracts.create_contract_draft(
            **({"file_source": {key: value for key, value in next(row for row in file_rows if row["source_id"] == state["dataset_id"]).items()
                 if key not in {"store", "columns", "configuration_workspace_id"}}, "columns": next(row["columns"] for row in file_rows if row["source_id"] == state["dataset_id"])}
                if str(state["dataset_id"]).startswith("file:") else {"table_id": str(state["dataset_id"])}),
            config=config, active_workspace_id=active_workspace_id,
            spark_session=spark, context=resolved,
            metadata_workspace_id=routing_workspace_id,
        )
        state["contracts"] = [draft, *[
            row for row in state["contracts"]
            if not (
                row.get("contract_id") == draft.get("contract_id")
                and row.get("contract_version") == draft.get("contract_version")
            )
        ]]
        select(str(state["dataset_id"]), int(draft["contract_version"]))
        return draft

    def stage_enrichment(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Stage Enrichment in widget session state without writing Metadata."""
        current = state.get("current")
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can be edited.")
        scope = (str(current["contract_id"]), int(current["contract_version"]))
        pending: dict[str, dict[str, Any]] = state["_pending_enrichment"].setdefault(scope, {})
        current_rows = list(current.get("enrichment", []))
        for record in records:
            key = str(record.get("enrichment_id") or "")
            pending[key] = dict(record)
            current_rows = [
                row for row in current_rows
                if str(row.get("enrichment_id") or "") != key
            ]
            current_rows.append(dict(record))
        current["enrichment"] = current_rows
        state["dirty"] = True
        refresh_manifest()
        return records

    def stage_guardrails(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Stage Guardrails in widget session state without writing Metadata."""
        current = state.get("current")
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can be edited.")
        scope = (str(current["contract_id"]), int(current["contract_version"]))
        pending: dict[str, dict[str, Any]] = state["_pending_guardrails"].setdefault(scope, {})
        current_rows = list(current.get("guardrails", []))
        for record in records:
            key = str(record.get("guardrail_rule_id") or "")
            pending[key] = dict(record)
            current_rows = [
                row for row in current_rows
                if str(row.get("guardrail_rule_id") or "") != key
            ]
            current_rows.append(dict(record))
        current["guardrails"] = current_rows
        state["dirty"] = True
        refresh_manifest()
        return records

    @busy_action("Saving Data Contract…")
    def save_data_contract_session(*, return_to_selector_after: bool = True) -> None:
        """Overwrite the selected draft JSON once, then reload canonical state once."""
        current = state.get("current")
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can be saved.")
        scope = (str(current["contract_id"]), int(current["contract_version"]))
        prepare_save = state.get("_prepare_data_contract_save")
        if callable(prepare_save):
            prepare_save()
        validate_authoring_session("saving")
        removed_column_ids = {
            str(rule.get("column_id") or "")
            for rule in current.get("guardrails", [])
            if str(rule.get("guardrail_type") or "").lower() == "sensitive_data"
            and bool(rule.get("is_active", True))
            and str(_parameters(rule).get("treatment") or rule.get("rule_type") or "").lower() == "remove"
        }
        contract_columns = json.loads(
            str(current["contract"].get("contract_payload_json") or "{}")
        ).get("table", {}).get("columns", [])
        conflicting_columns = sorted({
            str(column.get("column_name") or column.get("column_id") or "")
            for column in contract_columns
            if str(column.get("column_id") or "") in removed_column_ids
            and column.get("presence", "required") == "required"
        })
        if conflicting_columns:
            raise ValueError(
                "Removed output columns cannot be Required: "
                + ", ".join(conflicting_columns)
                + ". Clear Required before saving."
            )
        payload = refresh_manifest()
        if payload is None:
            raise ValueError("Data Contract draft has no payload to save.")
        saved = contracts.save_contract_draft(
            draft=current["contract"],
            payload=payload,
            config=config,
            active_workspace_id=active_workspace_id,
            spark_session=spark,
            context=resolved,
            metadata_workspace_id=routing_workspace_id,
        )
        current["contract"] = saved
        state["_pending_enrichment"].pop(scope, None)
        state["_pending_guardrails"].pop(scope, None)
        state["_column_drafts"].pop(scope, None)
        state["_column_dq_selection"].pop(scope, None)
        state["dirty"] = False
        if return_to_selector_after:
            return_to_selector = state.get("_return_to_selector")
            if callable(return_to_selector):
                return_to_selector("Data Contract draft saved. Select a dataset and contract.")
            else:
                set_status("Data Contract draft saved.")
        else:
            select(str(state["dataset_id"]), int(state["contract_version"]))
            set_status("Data Contract draft saved.")

    @busy_action("Discarding unsaved changes…")
    def discard_data_contract_session(*, return_to_selector_after: bool = False) -> None:
        """Discard staged changes, then reload or return directly to the selector."""
        current = state.get("current")
        if not current:
            return
        scope = (str(current["contract_id"]), int(current["contract_version"]))
        state["_pending_enrichment"].pop(scope, None)
        state["_pending_guardrails"].pop(scope, None)
        state["_column_drafts"].pop(scope, None)
        state["_column_dq_selection"].pop(scope, None)
        state["dirty"] = False
        if return_to_selector_after:
            return_to_selector("Unsaved changes discarded. Select a dataset and contract.")
        else:
            select(str(state["dataset_id"]), int(state["contract_version"]))
            render()
            set_status("Unsaved Data Contract changes discarded.")

    def load_profile_context(column_id: str) -> dict[str, Any]:
        """Load one column profile once per governed table and reuse it within the widget."""
        selected_table = str(state.get("dataset_id") or "").strip()
        selected_column = str(column_id or "").strip()
        if not selected_table or not selected_column:
            raise ValueError("Select a governed table and column before loading profile context.")
        cache_key = (active_workspace_id, selected_table, selected_column)
        profile_cache: dict[tuple[str, str, str], dict[str, Any]] = state["_profile_cache"]
        if selected_table.startswith("file:") and cache_key not in profile_cache:
            profile_cache[cache_key] = {"kind": "unavailable", "message": "File profiles are session-only; no persisted table profile is available."}
        if cache_key not in profile_cache:
            began = perf_counter()
            try:
                profile_cache[cache_key] = contracts.get_column_profile_context(
                    config=config, active_workspace_id=active_workspace_id, spark_session=spark,
                    table_id=selected_table, column_id=selected_column,
                    metadata_workspace_id=routing_workspace_id,
                )
            finally:
                state["_operation_timings"].append({"operation": "Loading profile context", "seconds": perf_counter() - began})
        profile = profile_cache[cache_key]
        state["profile_context"] = profile
        return profile

    @busy_action("Freezing Data Contract…")
    def freeze() -> dict[str, Any]:
        current = state.get("current")
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can be frozen.")
        validate_authoring_session("freezing")
        if state.get("dirty"):
            raise ValueError("Save the Data Contract before freezing this version.")
        result = contracts.freeze_contract(
            draft=current["contract"], config=config, active_workspace_id=active_workspace_id,
            spark_session=spark, context=resolved,
            metadata_workspace_id=routing_workspace_id,
        )
        latest = contracts.list_contract_governance_state(
            config=config, active_workspace_id=active_workspace_id, spark_session=spark,
            metadata_workspace_id=routing_workspace_id,
        )
        state["contracts"] = latest["contracts"]
        select(str(state["dataset_id"]), int(state["contract_version"]))
        return result

    state.update(
        select=select, new_draft=new_draft, refresh_manifest=refresh_manifest,
        freeze=freeze, stage_enrichment=stage_enrichment,
        stage_guardrails=stage_guardrails, save_data_contract=save_data_contract_session,
        discard_data_contract=discard_data_contract_session,
        load_profile_context=load_profile_context,
    )
    def ai_available() -> bool:
        """Allow AI actions only while configuration and the notebook runtime permit them."""
        return bool(ai_enrichment.get("enabled")) and not state["_ai_unavailable"]

    def ai_failure_message(exc: Exception, operation: Any) -> str:
        """Show an actionable AI error and retain its diagnostic for debugging."""
        diagnostic = ai_failure_diagnostic(exc)
        current = state.get("current") or {}
        scope = (str(current.get("contract_id") or ""), int(current.get("contract_version") or 0))
        state["_ai_diagnostics"].setdefault(scope, {})[operation] = diagnostic
        state["_ai_failure"] = diagnostic["detail"]
        state["_ai_failure_category"] = diagnostic["category"]
        state["_ai_failure_diagnostic"] = diagnostic
        if not diagnostic["recoverable"]:
            state["_validation_errors"].pop("business_rule_ai", None)
            state["_ai_unavailable"] = diagnostic["message"]
            for button in state["_ai_buttons"]:
                button.disabled = True
            ai_availability.value = f"<p>{html.escape(state['_ai_unavailable'])}</p>"
        return str(diagnostic["message"])

    def ai_recovered(message: str, *, operation: Any, remaining_errors: bool = False) -> None:
        """Clear the current recoverable failure after its operation succeeds."""
        current = state.get("current") or {}
        scope = (str(current.get("contract_id") or ""), int(current.get("contract_version") or 0))
        diagnostics = state["_ai_diagnostics"].get(scope, {})
        diagnostics.pop(operation, None)
        latest = next(reversed(diagnostics.values()), {}) if diagnostics else {}
        state["_ai_failure"] = latest.get("detail", "")
        state["_ai_failure_category"] = latest.get("category", "")
        state["_ai_failure_diagnostic"] = latest
        if remaining_errors:
            set_status(
                "Another AI suggestion still needs attention. Review the highlighted AI panels.",
                warning=True,
            )
        else:
            set_status(message)

    def dynamic_selector(*, placeholder: str, empty_label: str | None = None) -> dict[str, Any]:
        return shared.render_searchable_selector(
            widgets=widgets,
            label="",
            rows=[],
            label_fn=lambda row: str(row.get("label") or row.get("value") or ""),
            value_fn=lambda row: str(row.get("value") or ""),
            placeholder=placeholder,
            empty_label=empty_label,
        )

    table_selector = dynamic_selector(
        placeholder="Search governed tables...",
        empty_label="Select dataset",
    )
    contract_selector = dynamic_selector(placeholder="Search contract versions...", empty_label="Select contract")
    workspace_selector = dynamic_selector(placeholder="Search workspaces...", empty_label="Select workspace")
    workspace_control = workspace_selector["selector"]
    table_control = table_selector["selector"]
    contract_control = contract_selector["selector"]

    def selector_field(label: str, control: Any) -> Any:
        return widgets.VBox(
            [
                widgets.HTML(f"<b>{html.escape(label)}</b>"),
                control,
            ],
            layout=widgets.Layout(
                width="100%", min_width="0", align_items="stretch", gap="4px",
            ),
        )

    workspace_selector_field = selector_field("Workspace", workspace_selector["container"])
    table_selector_field = selector_field("Dataset", table_selector["container"])
    contract_selector_field = selector_field("Contract", contract_selector["container"])
    workspace_selector_field.layout.grid_area = "workspace"
    table_selector_field.layout.grid_area = "table"
    contract_selector_field.layout.grid_area = "contract"

    selector = widgets.GridBox(
        [
            table_selector_field,
            workspace_selector_field,
            contract_selector_field,
        ],
        layout=widgets.Layout(
            width="100%", min_width="0", max_width="100%",
            grid_template_columns="repeat(2, minmax(0, 1fr))",
            grid_template_areas='"table table" "workspace contract"',
            grid_gap="16px 24px",
            overflow="visible",
        ),
    )

    def configured_item_name(row: Mapping[str, Any]) -> str:
        workspace_id = str(row.get("workspace_id") or "")
        store_key = str(row.get("layer") or "")
        paths = getattr(getattr(config, "path_config", None), "paths", {}) or {}
        configured = paths.get(workspace_id, {}).get(store_key)
        if isinstance(configured, Mapping):
            return str(configured.get("name") or configured.get("item_id") or store_key)
        return str(
            getattr(configured, "name", None)
            or getattr(configured, "item_id", "")
            or store_key
        )

    def qualified_table_name(row: Mapping[str, Any]) -> str:
        schema_name = str(row.get("schema_name") or "").strip()
        table_name = str(row.get("table_name") or row.get("table_id") or "").strip()
        return f"{schema_name}.{table_name}" if schema_name else table_name

    def table_selector_label(row: Mapping[str, Any]) -> str:
        if row.get("source_type") == "file":
            return contracts.dataset_display_name(row)
        name = qualified_table_name(row)
        item = configured_item_name(row)
        workspace = row.get("_workspace_name") or row.get("workspace_id") or ""
        return f"{item} · {name} — Table · {workspace}"

    rows_cache: dict[str, Any] = {}

    def current_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        current = state["current"]
        for key, identity in (("enrichment", ("enrichment_level", "column_id", "enrichment_type")),
                              ("guardrails", ("guardrail_rule_id",))):
            rows = current.get(key, [])
            if rows_cache.get(key) is not rows:
                rows_cache[key] = rows
                rows_cache[key + "_latest"] = _latest(rows, *identity)
        return rows_cache["enrichment_latest"], rows_cache["guardrails_latest"]

    def enrichment_value(rows: list[dict[str, Any]], level: str, kind: str, column_id: str = "") -> str:
        return str(next((
            row.get("value") or "" for row in reversed(rows)
            if str(row.get("enrichment_level") or "").lower() == level
            and str(row.get("column_id") or "") == column_id
            and str(row.get("enrichment_type") or "") == kind
        ), ""))

    def enrichment_record(level: str, kind: str, value: str, column_id: str = "") -> dict[str, Any]:
        current = state["current"]
        contract_payload = json.loads(
            str(current["contract"].get("contract_payload_json") or "{}")
        )
        table_payload = contract_payload.get("table") or {}
        rows, _ = current_rows()
        previous = next((row for row in reversed(rows) if
            str(row.get("enrichment_level") or "").lower() == level
            and str(row.get("column_id") or "") == column_id
            and str(row.get("enrichment_type") or "") == kind), {})
        return {
            "enrichment_id": previous.get("enrichment_id") or str(uuid.uuid4()),
            "contract_id": current["contract_id"], "contract_version": current["contract_version"],
            "table_id": str(table_payload.get("table_id") or current["contract"].get("table_id") or ""),
            "table_name": str(table_payload.get("table_name") or ""),
            "workspace_id": active_workspace_id, "enrichment_level": level,
            "column_id": column_id,
            "column_name": next((str(item.get("column_name") or "") for item in current.get("available_columns", []) if str(item.get("column_id") or "") == column_id), "") if column_id else "",
            "enrichment_type": kind, "value": value,
        }

    def guardrail_record(
        guardrail_type: str, rule_type: str, parameters: dict[str, Any], *,
        column_id: str = "", action: str = "Warn", existing: Mapping[str, Any] | None = None,
        active: bool = True,
    ) -> dict[str, Any]:
        current = state["current"]
        contract_payload = json.loads(str(current["contract"].get("contract_payload_json") or "{}"))
        table_payload = contract_payload.get("table") or {}
        old = dict(existing or {})
        scope = (str(current["contract_id"]), int(current["contract_version"]))
        old_id = str(old.get("guardrail_rule_id") or "")
        pending = state["_pending_guardrails"].get(scope, {})
        version = int(old.get("guardrail_version") or 0)
        if not old_id or old_id not in pending:
            version += 1
        return {
            "guardrail_rule_id": old.get("guardrail_rule_id") or str(uuid.uuid4()),
            "guardrail_version": version,
            "contract_id": current["contract_id"], "contract_version": current["contract_version"],
            "table_id": str(table_payload.get("table_id") or current["contract"].get("table_id") or ""),
            "table_name": str(table_payload.get("table_name") or ""),
            "workspace_id": active_workspace_id, "column_id": column_id,
            "column_name": next((str(item.get("column_name") or "") for item in current.get("available_columns", []) if str(item.get("column_id") or "") == column_id), "") if column_id else "",
            "guardrail_type": guardrail_type, "rule_id": old.get("rule_id") or rule_type,
            "rule_type": rule_type, "rule_parameters_json": json.dumps(parameters),
            "action": "Block" if guardrail_type in {"schema", "sensitive_data"} else action, "is_active": active,
        }

    def render() -> None:
        current = state.get("current")
        previous_controls = dict(state["_controls"])
        sidebar_actions.children = ()
        dispose_editor = state.pop("_dispose_editor", None)
        if callable(dispose_editor):
            dispose_editor()
        for key in ("_refresh_review", "_refresh_dq_rules", "_refresh_ai_controls", "_load_selected_profile", "_refresh_column_view"):
            state.pop(key, None)
        sidebar_actions.layout.display = "none"
        state.pop("_refresh_guardrail_sidebar", None)
        dispose_sidebar = state.pop("_dispose_guardrail_sidebar", None)
        if not callable(dispose_editor) and callable(dispose_sidebar):
            dispose_sidebar()
        view_content.clear()
        state["_controls"].update({
            "table": table_control, "contract": contract_control,
            "top_nav": top_nav, "workspace": workspace, "left_pane": left,
            "right_pane": right, "status": status,
        })
        if not current:
            prompt = widgets.HTML("<p>Select a dataset and contract.</p>")
            left.children = (prompt,)
            right.children = ()
            return
        row = current["contract"]
        editable = str(row.get("status") or "").lower() == "draft"
        enrichments, guardrails = current_rows()

        def session_guardrails() -> list[dict[str, Any]]:
            return current_rows()[1]

        def set_validation_error(key: str, error: Exception | str | None = None) -> None:
            errors: dict[str, str] = state["_validation_errors"]
            if error is None:
                errors.pop(key, None)
            else:
                errors[key] = str(error)

        columns = sorted(
            list(current.get("available_columns", [])),
            key=lambda column: (
                str(column.get("column_name") or "").startswith("_"),
                str(column.get("column_name") or "").casefold(),
            ),
        )
        authoring_columns = [
            column
            for column in columns
            if not str(column.get("column_name") or "").startswith("_")
        ]
        resolution_controls = ()
        available_ids = {str(column.get("column_id") or "") for column in columns}
        unresolved = [
            item for item in [*enrichments, *guardrails]
            if item.get("column_id") and str(item["column_id"]) not in available_ids
        ]
        state["_controls"]["remove_unavailable_definitions"] = None
        if editable and unresolved:
            names_by_id = {
                str(item.get("column_id") or ""): str(item.get("column_name") or item.get("column_id"))
                for item in current.get("catalogue_rows", []) if item.get("column_id")
            }
            details = "<br>".join(html.escape(
                f"{names_by_id.get(str(item['column_id']), str(item['column_id']))}: "
                f"{item.get('enrichment_type') or item.get('guardrail_type')} "
                f"{item.get('value') or item.get('rule_type') or ''}"
            ) for item in unresolved)
            notice = widgets.HTML(
                "<p><strong>Definitions reference unavailable columns.</strong> "
                "Review them before removing them from this draft. "
                "The frozen version is unchanged.</p>" + details
            )
            remove_unavailable = widgets.Button(description="Remove unavailable definitions")

            def remove_unavailable_clicked(_button: Any) -> None:
                scope = (str(current["contract_id"]), int(current["contract_version"]))
                for field, pending_key in (("enrichment", "_pending_enrichment"), ("guardrails", "_pending_guardrails")):
                    current[field] = [
                        item for item in current.get(field, [])
                        if not item.get("column_id") or str(item["column_id"]) in available_ids
                    ]
                    pending = state[pending_key].get(scope, {})
                    state[pending_key][scope] = {
                        key: item for key, item in pending.items()
                        if not item.get("column_id") or str(item["column_id"]) in available_ids
                    }
                state["dirty"] = True
                refresh_manifest()
                render()
                set_status("Unavailable column definitions removed from the draft. Save to keep this change.")

            remove_unavailable.on_click(remove_unavailable_clicked)
            state["_controls"]["remove_unavailable_definitions"] = remove_unavailable
            resolution_controls = (notice, remove_unavailable)
        table = next((item for item in current.get("catalogue_rows", []) if not item.get("column_id")), {})
        if not table:
            table = (state.get("manifest") or {}).get("table", {})
        observed_names = {str(item.get("column_name")) for item in current.get("catalogue_rows", [])
                          if item.get("column_id") and item.get("is_active") is not False}
        if current.get("payload", {}).get("source", {}).get("source_type") == "file":
            observed_names = {str(item.get("column_name")) for item in current.get("available_columns", [])}
        contracted_names = {str(item.get("column_name")) for item in columns}
        state["observation_difference"] = {"unaccounted_columns": sorted(observed_names - contracted_names),
                                           "missing_contracted_columns": sorted(contracted_names - observed_names)}
        suggestion_scope = (str(current["contract_id"]), int(current["contract_version"]))
        ai_state = state["_ai_suggestions"].setdefault(
            suggestion_scope, {"table": {}, "columns": {}}
        )
        state["_ai_buttons"] = []
        ai_errors = state["_ai_errors"].setdefault(suggestion_scope, {})
        diagnostics = state["_ai_diagnostics"].get(suggestion_scope, {})
        latest = next(reversed(diagnostics.values()), {}) if diagnostics else {}
        state["_ai_failure"] = latest.get("detail", "")
        state["_ai_failure_category"] = latest.get("category", "")
        state["_ai_failure_diagnostic"] = latest
        column_names = [
            str(column.get("column_name") or "") for column in authoring_columns
        ]
        from fabricops_kit.config.metadata_schemas import decode_metadata_row
        discovery = decode_metadata_row("METADATA_DATA_CATALOGUE", {
            "profile_key_candidates_json": table.get("profile_key_candidates_json"),
        })["profile_key_candidates_json"] or {}
        raw_profile_key_candidates = discovery.get("candidates") or []
        profile_key_candidates = [
            dict(candidate)
            for candidate in raw_profile_key_candidates
            if isinstance(candidate, Mapping)
            and candidate.get("columns")
            and all(str(name) in column_names for name in candidate.get("columns", []))
        ] if isinstance(raw_profile_key_candidates, list) else []
        profiled_key_columns = (
            [str(name) for name in profile_key_candidates[0].get("columns", [])]
            if profile_key_candidates and discovery.get("profile_scope") != "bounded_selection" else []
        )
        checkbox_row_layout = widgets.Layout(gap="20px", align_items="center", flex_flow="row wrap")
        ai_visible = bool(ai_enrichment.get("enabled"))
        top_nav.options = _TABS
        if str(top_nav.value) not in _TABS:
            top_nav.value = "Table"

        # Table: passive identity plus explicitly saved Enrichment and table Guardrails.
        table_description = widgets.Textarea(continuous_update=False,
            value=enrichment_value(enrichments, "table", "Description"), disabled=not editable,
            **shared.widget_common(widgets, "Description", textarea=True),
        )
        table_classification = widgets.Dropdown(
            options=classification_options,
            value=_valid_dropdown_value(
                classification_options,
                enrichment_value(enrichments, "table", "Classification"),
                fallback="",
            ),
            disabled=True, **shared.widget_common(widgets, "Classification"),
        )
        table_description.description = ""
        table_description.layout.close()
        table_description.layout = widgets.Layout(width="100%", min_width="0", height="110px")
        table_classification.description = ""
        table_classification.layout.close()
        table_classification.layout = widgets.Layout(width="250px", max_width="100%", min_width="0")
        table_description_ai = widgets.HTML()
        accept_table_description = widgets.Button(description="Apply", disabled=not editable, button_style="info")
        rerun_table_description = widgets.Button(description="Re-run", disabled=not editable)
        state["_ai_buttons"].extend([accept_table_description, rerun_table_description])

        # Description, selected key, and enforcement are independent authoring choices.
        table_grain = widgets.Text(continuous_update=False,
            value=enrichment_value(enrichments, "table", "Grain"), disabled=not editable,
            placeholder="Example: One row per order line",
            **shared.widget_common(widgets, "Row grain"),
        )
        table_grain.layout.close()
        table_grain.layout = widgets.Layout(width="100%", max_width="560px", min_width="0")
        existing_row_key = next((rule for rule in guardrails if rule.get("guardrail_type") == "grain"), {})
        existing_row_key_columns = list(_parameters(existing_row_key).get("columns", []))
        row_key_rule = {"current": dict(existing_row_key)}
        row_key_columns = widgets.SelectMultiple(
            options=list(dict.fromkeys([*column_names, *existing_row_key_columns])),
            value=tuple(existing_row_key_columns if existing_row_key else profiled_key_columns),
            rows=5, disabled=not editable,
            **shared.widget_common(widgets, "Row key columns"),
        )
        row_key_columns.layout.close()
        row_key_columns.layout = widgets.Layout(
            width="100%", max_width="560px", min_width="0",
            height="auto",
            max_height="252px",
        )
        row_key_columns.add_class("fabricops-contract-list")
        grain_enabled = widgets.Checkbox(
            value=bool(existing_row_key and existing_row_key.get("is_active", True)),
            description="Enforce Grain", disabled=not editable,
            layout=widgets.Layout(width="auto", min_width="0"),
        )
        grain_policy = widgets.Dropdown(
            options=["Block", "Warn"], value=existing_row_key.get("action") or "Block",
            disabled=not editable or not grain_enabled.value,
            **shared.widget_common(widgets, "On violation"),
        )
        grain_policy.layout.close()
        grain_policy.layout = widgets.Layout(width="220px", max_width="100%")
        grain_policy.add_class("fabricops-grain-policy")
        grain_profile_evidence = widgets.HTML()
        grain_ai = widgets.HTML()
        suggest_grain = widgets.Button(
            description="Suggest grain",
            disabled=(
                not editable or not ai_available()
            ),
        )
        accept_grain = widgets.Button(
            description="Use grain wording", disabled=True, button_style="info"
        )
        state["_ai_buttons"].extend([suggest_grain, accept_grain])

        def render_grain_profile_evidence() -> None:
            if profile_key_candidates:
                rows = "".join(
                    "<li><code>{}</code> · <b>{}</b> · {}</li>".format(
                        html.escape(" + ".join(str(name) for name in candidate.get("columns", []))),
                        (html.escape(str(candidate["uniqueness_percent"])) + "% unique"
                         if candidate.get("uniqueness_percent") is not None else "Uniqueness not recorded"),
                        ("no missing key values" if candidate.get("null_count") == 0
                         else "Missing-key count not recorded" if candidate.get("null_count") is None
                         else html.escape(str(candidate["null_count"])) + " missing key values"),
                    )
                    for candidate in profile_key_candidates[:8]
                )
                grain_profile_evidence.value = (
                    "<div style='color:#667085;font-size:12px;line-height:1.5;'>"
                    "<details><summary>Profile evidence · suggested keys</summary><ul style='margin:5px 0 0 18px;'>"
                    + rows
                    + "</ul>"
                    + ("<p>Sampled Grain candidates: uniqueness applies only to the bounded selection; full-table uniqueness is unverified.</p>" if discovery.get("profile_scope") == "bounded_selection" else "")
                    + "<span>Suggested key only. Enable Grain explicitly to enforce it.</span></details></div>"
                )
                return
            grain_profile_evidence.value = (
                "<div style='color:#667085;font-size:12px;line-height:1.5;'>"
                "<b>Profile evidence</b><br>"
                + ("Sampled Grain discovery used a bounded selection; full-table uniqueness is unverified. " if discovery.get("profile_scope") == "bounded_selection" else "No row key suggestion available from the latest profile. ")
                + "Select a row key manually if this table has one.</div>"
            )

        def render_grain_ai() -> None:
            suggestion = ai_state["table"].get("grain_key")
            if not suggestion:
                return
            key_text = (
                ", ".join(profiled_key_columns)
                if profiled_key_columns else "No row key suggestion available"
            )
            grain_ai.value = (
                "<div style='background:#f6f8fa;border-left:3px solid var(--form-accent);"
                "padding:9px 11px;font-size:12px;line-height:1.5;'>"
                "<div style='font-size:11px;color:#667085;margin-bottom:5px'>Previously generated AI suggestion</div>"
                f"<b>Suggested grain:</b> {html.escape(suggestion['grain'] or 'Not inferred')}<br>"
                f"<b>Profiled row key:</b> {html.escape(key_text)}"
                "<details style='margin-top:5px;color:#667085;'>"
                "<summary style='cursor:pointer;'>Why this suggestion?</summary>"
                f"<div style='margin-top:4px;'>{html.escape(suggestion['rationale'])}</div>"
                "</details></div>"
            )
            accept_grain.disabled = not (editable and ai_available())
            suggest_grain.description = "Regenerate grain"

        render_grain_ai()

        @busy_action("Generating grain and row key suggestions…", ai_request=True)
        def run_grain_ai(*_args: Any) -> None:
            if not editable or not ai_available():
                return
            retrying = "grain_key" in ai_errors
            try:
                ensure_runtime_context()
                render_grain_profile_evidence()
                profile_rows = []
                for column in authoring_columns:
                    cid = str(column.get("column_id") or "")
                    profile_value = load_profile_context(cid)
                    profile = dict(profile_value.get("profile") or {})
                    profile_rows.append({
                        "column_name": str(column.get("column_name") or ""),
                        "data_type": str(column.get("data_type") or ""),
                        "description": enrichment_value(
                            enrichments, "column", "Description", cid
                        ),
                        **{
                            name: profile.get(name)
                            for name in (
                                "profile_scope", "profiling_max_rows",
                                "row_count", "non_null_count", "null_count", "null_percent",
                                "distinct_count", "distinct_percent",
                            )
                            if profile.get(name) is not None
                        },
                    })
                suggestion = suggest_grain_key(
                    {
                        "table_name": str(table.get("table_name") or ""),
                        "schema_name": str(table.get("schema_name") or ""),
                        "table_description": str(table_description.value or ""),
                        "table_classification": str(table_classification.value or ""),
                        "profile_key_candidates": profile_key_candidates if discovery.get("profile_scope") != "bounded_selection" else [],
                        "columns": profile_rows,
                    },
                    prompt=str(ai_enrichment.get("grain_prompt") or ""),
                    ai_config=ai_enrichment, spark_session=spark, usage=state["ai_usage"],
                    runtime_context=ai_runtime_context(), operation="grain_key",
                )
                ai_state["table"]["grain_key"] = suggestion
                refresh_ai_usage()
                ai_errors.pop("grain_key", None)
                if retrying:
                    ai_recovered(
                        "Grain AI suggestion generated after retry.",
                        operation="grain_key",
                        remaining_errors=bool(
                            ai_errors or state["_validation_errors"].get("business_rule_ai")
                        ),
                    )
                render_grain_ai()
            except (TypeError, ValueError, RuntimeError, ImportError) as exc:
                ai_state["table"].pop("grain_key", None)
                accept_grain.disabled = True
                refresh_ai_usage()
                message = ai_failure_message(exc, "grain_key")
                ai_errors["grain_key"] = message
                grain_ai.value = f"<p>{html.escape(message)}</p>"

        def accept_grain_ai(_button: Any) -> None:
            suggestion = ai_state["table"].get("grain_key") or {}
            table_grain.value = str(suggestion.get("grain") or "")
            render_table_summary()
            if grain_enabled.value:
                set_status("Suggested Grain wording applied.")
            else:
                set_status(
                    "Suggested Grain wording applied. Turn on Enforce Grain to activate "
                    "the selected row key.",
                    warning=True,
                )

        suggest_grain.on_click(run_grain_ai)
        accept_grain.on_click(accept_grain_ai)
        render_grain_profile_evidence()

        def render_table_ai() -> None:
            if state["_ai_unavailable"]:
                table_description_ai.value = f"<p>{state['_ai_unavailable']}</p>"
            elif not ai_enrichment.get("enabled"):
                table_description_ai.value = "<p>Disabled in 00_env_config.</p>"
            elif not editable:
                table_description_ai.value = "<p>Not run for review-only versions.</p>"
            elif not ai_state["table"].get("description") and str(table_description.value or "").strip():
                table_description_ai.value = "<p>Saved description retained. Use Generate to request a suggestion.</p>"
            else:
                table_description_ai.value = _suggestion_html(
                    "Description", ai_state["table"].get("description"), show_heading=False
                )
            available = (
                editable and ai_available()
            )
            accept_table_description.disabled = not (
                available and ai_state["table"].get("description")
                and not ai_state["table"]["description"].get("error")
            )
            rerun_table_description.disabled = not available
            rerun_table_description.description = "Re-run" if ai_state["table"].get("description") else "Generate"

        @busy_action("Generating table description…", ai_request=True)
        def run_table_ai(*, force: bool = False) -> None:
            if (
                not editable
                or not ai_available()
            ):
                render_table_ai()
                return
            if not force and ai_state["table"].get("description"):
                render_table_ai()
                return
            retrying = "table_enrichment" in ai_errors
            try:
                description_context = build_ai_enrichment_context(
                    table,
                    metadata_level="table",
                    existing_description=str(table_description.value or ""),
                    column_rows=authoring_columns,
                )
                grain_suggestion = ai_state["table"].get("grain_key") or {}
                description_context["grain"] = str(
                    table_grain.value or grain_suggestion.get("grain") or ""
                )
                description_context["classification"] = str(table_classification.value or "")
                result = suggest_enrichment(
                    description_context,
                    description_prompt=str(ai_enrichment.get("table_description_prompt") or ""),
                    ai_config=ai_enrichment, spark_session=spark, usage=state["ai_usage"],
                    runtime_context=ai_runtime_context(), operation="table_enrichment",
                )
                previous_value = str(ai_state["table"].get("description", {}).get("value") or "")
                new_value = str(result["Description"])
                ai_state["table"]["description"] = {"value": new_value, "stale": False}
                if previous_value and new_value != previous_value:
                    mark_all_sensitive_stale()
                refresh_ai_usage()
                ai_errors.pop("table_enrichment", None)
                if retrying:
                    ai_recovered(
                        "Table AI suggestion generated after retry.",
                        operation="table_enrichment",
                        remaining_errors=bool(
                            ai_errors or state["_validation_errors"].get("business_rule_ai")
                        ),
                    )
            except (TypeError, ValueError, RuntimeError, ImportError) as exc:
                refresh_ai_usage()
                message = ai_failure_message(exc, "table_enrichment")
                ai_state["table"]["description"] = {"error": message, "stale": False}
                ai_errors["table_enrichment"] = message
                set_status(f"Table AI suggestions unavailable: {message}", warning=True)
            render_table_ai()

        accept_table_description.on_click(
            lambda _button: setattr(
                table_description, "value",
                str(ai_state["table"].get("description", {}).get("value") or ""),
            )
        )
        rerun_table_description.on_click(lambda _button: run_table_ai(force=True))

        table_rules: dict[str, Any] = {}
        existing_freshness = next((r for r in guardrails if r.get("guardrail_type") == "freshness"), {})
        freshness_parameters = _parameters(existing_freshness)
        is_file_source = current.get("payload", {}).get("source", {}).get("source_type") == "file"
        freshness_evidence_method = "metadata"
        freshness_enabled = widgets.Checkbox(value=bool(existing_freshness and existing_freshness.get("is_active", True)), description="Enabled", disabled=not editable)
        freshness_block = widgets.Checkbox(value=existing_freshness.get("action") == "Block", description="Block on failure", disabled=not editable)
        freshness_method = widgets.Dropdown(
            options=[("File modification metadata" if is_file_source else "Delta transaction history", freshness_evidence_method)],
            value=freshness_evidence_method, disabled=True,
            **shared.widget_common(widgets, "Evidence source (automatic)"),
        )
        freshness_age = widgets.Text(value=str(freshness_parameters.get("maximum_age", "")), continuous_update=False, disabled=not editable, **shared.widget_common(widgets, "Maximum age"))
        freshness_unit = widgets.Dropdown(options=["minutes", "hours", "days"], value=freshness_parameters.get("maximum_age_unit", "days"), disabled=not editable, **shared.widget_common(widgets, "Age unit"))
        freshness_hint = widgets.HTML()
        freshness_hint.value = (
            "Uses file modification metadata; the oldest selected file determines freshness. "
            "This does not measure business-event time."
            if is_file_source else
            "Uses the latest data-changing Delta transaction. Warehouse history can lag SQL commits; "
            "unavailable metadata is reported explicitly, never replaced with a column scan."
        )
        def build_freshness_record():
            old = next((r for r in session_guardrails() if r.get("guardrail_type") == "freshness"), {})
            if not freshness_enabled.value and not old:
                return None
            parameters = _parameters(old)
            if freshness_enabled.value:
                parameters = {"evidence_method": "metadata", "evaluation_scope": "full_dataset",
                    "maximum_age": float(freshness_age.value), "maximum_age_unit": freshness_unit.value}
                from fabricops_kit.pipeline.shared import validate_freshness_parameters
                validate_freshness_parameters(parameters)
            return guardrail_record("freshness", "freshness", parameters, existing=old,
                action="Block" if freshness_block.value else "Warn", active=freshness_enabled.value)
        table_rules["freshness"] = {"enabled": freshness_enabled, "block": freshness_block,
            "parameters": [freshness_method, freshness_age, freshness_unit],
            "display": [freshness_method, freshness_age, freshness_unit, freshness_hint],
            "build_record": build_freshness_record}
        def derive_table_classification() -> str:
            """Return the highest ranked classification among columns retained by the write."""
            rank = {value: index for index, value in enumerate(classification_levels)}
            removed_columns = {
                str(rule.get("column_id") or "")
                for rule in session_guardrails()
                if str(rule.get("guardrail_type") or "").lower() == "sensitive_data"
                and bool(rule.get("is_active", True))
                and str(_parameters(rule).get("treatment") or rule.get("rule_type") or "").lower() == "remove"
            }
            values = [
                str(row.get("value") or "")
                for row in list((state.get("current") or {}).get("enrichment", []))
                if str(row.get("enrichment_level") or "").lower() == "column"
                and str(row.get("enrichment_type") or "").lower() == "classification"
                and str(row.get("column_id") or "") not in removed_columns
                and str(row.get("value") or "") in rank
            ]
            return max(values, key=rank.get) if values else ""

        table_classification_sources = widgets.HTML()

        def refresh_table_classification() -> None:
            derived = derive_table_classification()
            if str(table_classification.value or "") != derived:
                table_classification.value = derived
            if not derived:
                table_classification_sources.value = (
                    "<span style='color:#667085;font-size:12px;'>"
                    "No classified columns determine the table level yet.</span>"
                )
                return
            column_labels = {
                str(column.get("column_id") or ""): str(column.get("column_name") or "")
                for column in authoring_columns
            }
            removed = {
                str(rule.get("column_id") or "")
                for rule in session_guardrails()
                if str(rule.get("guardrail_type") or "").lower() == "sensitive_data"
                and bool(rule.get("is_active", True))
                and str(_parameters(rule).get("treatment") or rule.get("rule_type") or "").lower() == "remove"
            }
            latest_classifications = {
                str(row.get("column_id") or ""): str(row.get("value") or "")
                for row in list((state.get("current") or {}).get("enrichment", []))
                if str(row.get("enrichment_level") or "").lower() == "column"
                and str(row.get("enrichment_type") or "").lower() == "classification"
            }
            matches = [
                column_labels[column_id]
                for column_id, level in latest_classifications.items()
                if column_id in column_labels and column_id not in removed and level == derived
            ]
            count = len(matches)
            examples = ", ".join(html.escape(name) for name in matches[:3])
            extra = f" +{count - 3} more" if count > 3 else ""
            noun = "column" if count == 1 else "columns"
            table_classification_sources.value = (
                "<span style='color:#667085;font-size:12px;line-height:1.5;'>"
                f"Determined by {count} {noun} at this level"
                + (f": {examples}{extra}" if examples else ".")
                + "</span>"
            )

        refresh_table_classification()

        def sync_table_enrichment(_change: dict[str, Any] | None = None) -> None:
            if not editable:
                return
            try:
                stage_enrichment([
                    enrichment_record("table", "Description", table_description.value),
                    enrichment_record("table", "Classification", table_classification.value),
                    enrichment_record("table", "Grain", table_grain.value),
                ])
                set_validation_error("table.enrichment")
                render_table_summary()
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error("table.enrichment", exc)

        def sync_row_key(_change: dict[str, Any] | None = None) -> None:
            if not editable:
                return
            try:
                selected_keys = [str(name) for name in row_key_columns.value]
                current_rule = row_key_rule["current"]
                if current_rule or selected_keys or grain_enabled.value:
                    record = guardrail_record(
                        "grain", "uniqueness", {"columns": selected_keys},
                        existing=current_rule, action=grain_policy.value, active=grain_enabled.value,
                    )
                    # Keep incomplete edits visible, but prevent Save until the key is valid.
                    row_key_rule["current"] = record
                    stage_guardrails([record])
                    contracts.validate_grain_parameters({"columns": selected_keys}, active=grain_enabled.value)
                set_validation_error("table.row_key")
                render_table_summary()
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error("table.row_key", exc)
                render_table_summary()

        def sync_table_rule(
            rule_kind: str, _change: dict[str, Any] | None = None,
        ) -> None:
            if not editable:
                return
            try:
                record = table_rules[rule_kind]["build_record"]()
                if record is not None:
                    stage_guardrails([record])
                set_validation_error(f"table.{rule_kind}")
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error(f"table.{rule_kind}", exc)

        for control in (table_description, table_classification, table_grain):
            control.observe(sync_table_enrichment, names="value")
        row_key_columns.observe(sync_row_key, names="value")

        def prepare_data_contract_save() -> None:
            """Persist the currently displayed row-key choice when final Save is deliberate."""
            sync_row_key()

        state["_prepare_data_contract_save"] = prepare_data_contract_save
        grain_policy.observe(sync_row_key, names="value")
        def grain_enforcement_changed(change):
            grain_policy.disabled = not editable or not change["new"]
            if change["new"] and not change["old"]:
                grain_policy.value = "Block"
            sync_row_key()
        grain_enabled.observe(grain_enforcement_changed, names="value")
        for rule_kind, rule_controls in table_rules.items():
            rule_controls["enabled"].observe(
                lambda change, kind=rule_kind: sync_table_rule(kind, change), names="value"
            )
            rule_controls["block"].observe(
                lambda change, kind=rule_kind: sync_table_rule(kind, change), names="value"
            )
            for control in rule_controls["parameters"]:
                control.observe(
                    lambda change, kind=rule_kind: sync_table_rule(kind, change), names="value"
                )

        runtime_context: dict[str, Any] = {}

        def context_timestamp(value: Any) -> str:
            text = str(value or "").strip()
            if not text:
                return "Unknown"
            try:
                # Spark-collected naive datetimes represent process-local time;
                # offset-free strings retain the audit-input helper's semantics.
                instant = value.astimezone(UTC) if isinstance(value, datetime) else value
                parsed = normalize_audit_datetime(instant, config)
                return parsed.strftime("%d %b %Y, %H:%M")
            except ValueError:
                return text

        def runtime_context_html() -> str:
            profile = runtime_context.get("latest_profile")
            if profile:
                workspace_id = str(profile.get("workspace_id") or "")
                workspace_name = str(profile.get("workspace_name") or "").strip()
                if not workspace_name:
                    workspace_name = next((
                        str(observation.get("_workspace_name") or "").strip()
                        for observation in table_rows
                        if str(observation.get("workspace_id") or "") == workspace_id
                        and observation.get("_workspace_name")
                    ), "") or "Unknown workspace"
                pipeline_name = str(profile.get("pipeline_name") or "Unknown pipeline")
                committed_by = str(profile.get("committed_by") or "Unknown")
                rank, instant = metadata_timestamp_sort_key(profile.get("committed_at"))
                age = f"{max(0, (datetime.now(UTC) - instant).days)} days" if rank and isinstance(instant, datetime) else "Unknown"
                row_count = next((item.get("row_count") for item in runtime_context.get("column_profiles", {}).values()
                                  if item.get("row_count") is not None), "Unknown")
                scope_label = ("Sampled rows (bounded selection only)" if profile.get("profile_scope") == "bounded_selection"
                               else "Rows in supplied DataFrame" if profile.get("profile_scope") == "supplied_dataframe" else "Rows")
                profile_html = (
                    "<div style='margin-top:14px;'>"
                    "<div style='color:#667085;font-size:11px;'>Latest profile</div>"
                    f"<div style='font-weight:600;margin-top:3px;'>{html.escape(workspace_name)} · "
                    f"{html.escape(pipeline_name)}</div>"
                    f"<div style='color:#667085;font-size:12px;margin-top:2px;'>{html.escape(committed_by)} · "
                    f"{html.escape(context_timestamp(profile.get('committed_at')))}</div>"
                    f"<div style='color:#667085;font-size:12px;'>Age: {html.escape(age)} · {scope_label}: {html.escape(str(row_count))}</div></div>"
                )
            else:
                profile_html = (
                    "<div style='margin-top:14px;'>"
                    "<div style='color:#667085;font-size:11px;'>Latest profile</div>"
                    "<div style='color:#667085;font-size:12px;margin-top:3px;'>Not yet profiled</div></div>"
                )

            writer_count = int(runtime_context.get("writer_count") or 0)
            reader_count = int(runtime_context.get("reader_count") or 0)
            writer_label = "write" if writer_count == 1 else "writes"
            reader_label = "read" if reader_count == 1 else "reads"
            lineage_rows = list(runtime_context.get("lineage") or [])
            if lineage_rows:
                lineage_cells = []
                for item in lineage_rows:
                    workspace_id = str(item.get("workspace_id") or "")
                    workspace_value = str(item.get("workspace_name") or "").strip()
                    if not workspace_value:
                        workspace_value = next((
                            str(observation.get("_workspace_name") or "").strip()
                            for observation in table_rows
                            if str(observation.get("workspace_id") or "") == workspace_id
                            and observation.get("_workspace_name")
                        ), "") or "Unknown workspace"
                    pipeline_value = str(item.get("pipeline_name") or "")
                    relationship = str(item.get("relationship") or "")
                    relationship_key = relationship.lower()
                    role_value = (
                        "Read" if relationship_key in {"reader", "read"}
                        else "Write" if relationship_key in {"writer", "write"}
                        else relationship
                    )
                    last_seen_value = context_timestamp(item.get("last_seen"))
                    values = (
                        workspace_value, pipeline_value, role_value, last_seen_value,
                    )
                    lineage_cells.append(
                        "<tr>" + "".join(
                            f"<td style='padding:5px 8px;' title='{html.escape(value, quote=True)}'>"
                            f"{html.escape(value)}</td>"
                            for value in values
                        ) + "</tr>"
                    )
                rows_html = "".join(lineage_cells)
                detail_html = (
                    "<details style='margin-top:5px;'>"
                    "<summary style='cursor:pointer;color:var(--form-accent);font-size:12px;'>View lineage</summary>"
                    "<div style='overflow-x:auto;margin-top:6px;'>"
                    "<table class='fabricops-lineage-table'>"
                    "<colgroup><col style='width:31%'><col style='width:25%'>"
                    "<col style='width:12%'><col style='width:32%'></colgroup>"
                    "<thead><tr><th style='text-align:left;padding:5px 8px;'>Workspace</th>"
                    "<th style='text-align:left;padding:5px 8px;'>Pipeline</th>"
                    "<th style='text-align:left;padding:5px 8px;'>Role</th>"
                    "<th style='text-align:left;padding:5px 8px;'>Last seen</th></tr></thead>"
                    f"<tbody>{rows_html}</tbody></table></div></details>"
                )
            else:
                detail_html = "<div style='color:#667085;font-size:12px;margin-top:3px;'>No lineage recorded</div>"
            return (
                profile_html
                + "<div style='margin-top:14px;'>"
                "<div style='color:#667085;font-size:11px;'>Pipeline usage</div>"
                f"<div style='font-weight:600;margin-top:3px;'>{writer_count} {writer_label} · "
                f"{reader_count} {reader_label}</div>"
                + detail_html
                + "</div>"
            )

        def table_identity_html() -> str:
            workspace_name = str(
                table.get("_workspace_name")
                or "Unknown workspace"
            )
            item_name = configured_item_name(table) or "Unknown"
            full_table_name = qualified_table_name(table) or "Unknown"
            return (
                "<div style='margin-top:14px;'>"
                "<div style='color:#667085;font-size:11px;'>Workspace</div>"
                f"<div style='font-weight:600;margin-top:3px;'>{html.escape(workspace_name)}</div>"
                "<div style='color:#667085;font-size:11px;margin-top:10px;'>Fabric object</div>"
                f"<div style='font-weight:600;margin-top:3px;'>{html.escape(item_name)}</div>"
                "<div style='color:#667085;font-size:11px;margin-top:10px;'>Full table name</div>"
                f"<div style='font-weight:600;margin-top:3px;overflow-wrap:anywhere;'>"
                f"{html.escape(full_table_name)}</div></div>"
            )

        table_summary = widgets.HTML()
        table_context_content = widgets.HTML()
        table_context_accordion = widgets.Accordion([table_context_content], selected_index=None)
        table_context_accordion.set_title(0, "Table context")
        guardrail_sidebar = widgets.VBox(layout=widgets.Layout(width="100%", min_width="0", gap="8px"))
        guardrail_sidebar.add_class("fabricops-guardrail-sidebar")
        guardrail_disclosure = widgets.Accordion([guardrail_sidebar], selected_index=None)
        guardrail_disclosure.set_title(0, "Read / Write Guardrails")
        table_left = resolution_controls

        sidebar_groups = {}
        expanded_guardrails = {}
        sidebar_snapshot = {"signature": None}
        working_sensitive_controls: dict[str, Any] = {}

        def close_sidebar_widgets(nodes, *, preserve=()):
            seen = set()
            def remember(widget):
                if widget is None or id(widget) in seen:
                    return
                seen.add(id(widget))
                for child in getattr(widget, "children", ()):
                    remember(child)
                remember(getattr(widget, "layout", None))
                remember(getattr(widget, "style", None))
            for node in preserve:
                remember(node)
            def close_owned(widget):
                if widget is None or id(widget) in seen:
                    return
                seen.add(id(widget))
                if isinstance(widget, dict):
                    for child in widget.values():
                        close_owned(child)
                elif isinstance(widget, (list, tuple)):
                    for child in widget:
                        close_owned(child)
                for child in getattr(widget, "children", ()):
                    close_owned(child)
                # Layout and Style models have their own widget comms.
                close_owned(getattr(widget, "layout", None))
                close_owned(getattr(widget, "style", None))
                close = getattr(widget, "close", None)
                if callable(close):
                    close()
            for node in nodes:
                close_owned(node)

        def dispose_guardrail_sidebar():
            close_sidebar_widgets([guardrail_sidebar])

        state["_dispose_guardrail_sidebar"] = dispose_guardrail_sidebar

        def expandable_guardrail(title, content, key, *, default=False):
            expanded = expanded_guardrails.get(key, default)
            toggle = widgets.ToggleButton(
                value=expanded, description=title,
                icon="chevron-down" if expanded else "chevron-right",
                tooltip=("Collapse " if expanded else "Expand ") + title,
                layout=widgets.Layout(width="100%", min_width="0", height="auto"),
            )
            toggle.add_class("fabricops-guardrail-toggle")
            content.layout.display = "" if expanded else "none"
            def toggle_content(change):
                expanded_guardrails[key] = bool(change["new"])
                content.layout.display = "" if change["new"] else "none"
                toggle.icon = "chevron-down" if change["new"] else "chevron-right"
                toggle.tooltip = ("Collapse " if change["new"] else "Expand ") + title
                toggle.description = title
            toggle.observe(toggle_content, names="value")
            disclosure = widgets.VBox([toggle, content], layout=widgets.Layout(width="100%", min_width="0", gap="4px"))
            disclosure.add_class("fabricops-guardrail-disclosure")
            return disclosure

        def render_guardrail_sidebar():
            visible_types = {
                "freshness", "schema", "grain", "data_quality", "sensitive_data",
            }
            active = [
                rule for rule in session_guardrails()
                if str(rule.get("guardrail_type") or "") in visible_types
            ]
            names_by_id = {str(c.get("column_id")): str(c.get("column_name")) for c in columns}
            working_sensitive_column_id = str(
                getattr(
                    working_sensitive_controls.get("column_select"), "value", "",
                ) or ""
            )
            working_sensitive_enabled = bool(getattr(
                working_sensitive_controls.get("enabled"), "value", False,
            ))
            working_pii_type = str(getattr(
                working_sensitive_controls.get("pii_type"), "value", "none",
            ) or "none")
            if working_sensitive_column_id and (
                working_sensitive_enabled or working_pii_type != "none"
            ):
                working_treatment = str(getattr(
                    working_sensitive_controls.get("treatment"), "value", "",
                ) or "")
                working_reason = str(getattr(
                    working_sensitive_controls.get("reason"), "value", "",
                ) or "").strip()
                active = [
                    rule for rule in active
                    if not (
                        str(rule.get("guardrail_type") or "") == "sensitive_data"
                        and str(rule.get("column_id") or "")
                        == working_sensitive_column_id
                    )
                ]
                active.append({
                    "guardrail_type": "sensitive_data",
                    "column_id": working_sensitive_column_id,
                    "column_name": names_by_id.get(
                        working_sensitive_column_id, working_sensitive_column_id,
                    ),
                    "rule_type": working_treatment or "treatment required",
                    "action": "Block",
                    "is_active": working_sensitive_enabled,
                    "rule_parameters_json": json.dumps({
                        "scope": "column",
                        "treatment": working_treatment or "Not selected",
                        "pii_type": working_pii_type,
                        "pii_reason": working_reason,
                    }),
                    "_working_incomplete": bool(
                        working_sensitive_enabled
                        and (
                            working_pii_type == "none"
                            or not working_treatment
                            or not working_reason
                        )
                    ),
                    "_working_output_classification": str(
                        getattr(
                            working_sensitive_controls.get("classification"),
                            "value", "Not classified",
                        ) or "Not classified"
                    ),
                })
            payload_columns = json.loads(str(current["contract"].get("contract_payload_json") or "{}")).get("table", {}).get("columns", [])
            types = {str(c.get("column_name")): str(c.get("data_type")) for c in payload_columns}
            types = {str(c.get("column_name")): types.get(str(c.get("column_name")), str(c.get("data_type") or "")) for c in columns}
            signature = json.dumps({
                "rules": active, "types": types,
                "grain_description": table_grain.value if any(rule.get("guardrail_type") == "grain" for rule in active) else "",
                "grain_enabled": grain_enabled.value,
                "grain_policy": grain_policy.value,
            }, sort_keys=True, default=str)
            if signature == sidebar_snapshot["signature"]:
                return
            previous = guardrail_sidebar.children
            labels = {"schema": "Schema", "grain": "Grain", "data_quality": "Data Quality", "sensitive_data": "Sensitive Data", "freshness": "Freshness"}

            def affected(rule):
                params = _parameters(rule)
                return [names_by_id.get(str(name), str(name)) for name in params.get("columns", [])] or ([names_by_id.get(str(rule.get("column_id")), str(rule.get("column_name") or rule.get("column_id")))] if rule.get("column_id") else [])

            def escaped(value):
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                return html.escape(str(value))

            def rule_content(kind, rule, *, role, show_summary):
                params = _parameters(rule)
                policy = "Block" if kind in {"schema", "sensitive_data"} else str(rule.get("action") or ("Block" if kind == "grain" else "Warn"))
                affected_names = affected(rule)
                detail = []
                enabled = rule.get("is_active", True)
                if kind == "schema":
                    required_names = list(dict.fromkeys(names_by_id.get(str(name), str(name)) for name in params.get("required_columns", [])))
                    detail = [("Required columns", required_names or "None"), ("Frozen type expectations", ", ".join(f"{name}: {dtype}" for name, dtype in types.items()) or "None"), ("Policy", "Block missing required columns, extra columns and contracted datatype mismatches")]
                elif kind == "grain":
                    enabled = bool(grain_enabled.value)
                    policy = str(grain_policy.value or "Block")
                    affected_names = [
                        names_by_id.get(str(name), str(name))
                        for name in row_key_columns.value
                    ]
                    detail = [
                        ("Managed rule", "GRAIN — Uniqueness · " + " + ".join(affected_names) + " · " + (policy if enabled else "Not enforced")),
                        ("Policy", policy),
                        ("Edit", "Table tab · Grain & Row Key"),
                        ("State", "Enabled" if enabled else "Not enforced"),
                        ("Key", affected_names or "Not selected"),
                        (
                            "Checks",
                            "Returned rows before downstream processing."
                            if role == "read"
                            else "Prepared input before publication.",
                        ),
                    ]
                    if not enabled:
                        detail.append((
                            "Next step",
                            "Turn on Enforce Grain in the Table tab to activate this check.",
                        ))
                else:
                    detail = [("Scope", "Column" if rule.get("column_id") else "Table-level"), ("Columns", affected_names or "Table-level"), ("Rule", str(rule.get("rule_type") or "").replace("_", " ")), ("Policy", "Block · treatment must succeed" if kind == "sensitive_data" else policy)]
                    if kind == "sensitive_data":
                        pii_label = {
                            "direct": "Direct PII", "indirect": "Indirect PII",
                            "none": "Not PII",
                        }.get(
                            str(params.get("pii_type") or "none"),
                            str(params.get("pii_type") or "Not PII"),
                        )
                        detail.extend((
                            ("PII assessment", pii_label),
                            (
                                "Output classification",
                                rule.get("_working_output_classification")
                                or "Saved contract value",
                            ),
                        ))
                        if rule.get("_working_incomplete"):
                            detail.append((
                                "Configuration",
                                "Incomplete · provide a Reason before saving.",
                            ))
                    if kind == "freshness":
                        detail.append(("Scope", "Source Read · no refresh expected; no age validation" if rule.get("rule_type") == "skip" or params.get("refresh_expectation") == "static" else "Source returned by orchestrate_read(); latest timestamp relative to run time"))
                    detail.extend((("Accepted failure rate %" if key in {"maximum_missing_percent", "maximum_failure_percent"} else key.replace("_", " ").capitalize()), value) for key, value in params.items() if key not in {"columns", "engineering_reviewed_by", "engineering_review_note"})
                if kind != "grain":
                    detail.insert(0, ("State", "Enabled" if enabled else "Disabled · intentionally not executed"))
                text = "".join(f"<div><b>{escaped(key)}:</b> {escaped(value)}</div>" for key, value in detail)
                state_label = policy if enabled else "Not enforced"
                description = (", ".join(affected_names) + " · " if affected_names else "Table · ") + str(rule.get("rule_type") or labels[kind]).replace("_", " ") + " · " + state_label
                children = [widgets.HTML("<div class='fabricops-guardrail-detail'>" + text + "</div>")]
                if show_summary:
                    children.insert(0, widgets.HTML(
                        "<div class='fabricops-guardrail-summary'><b>"
                        + html.escape(description)
                        + "</b></div>"
                    ))
                return widgets.VBox(children, layout=widgets.Layout(min_width="0", gap="4px"))

            def group(role, title, subtitle, kinds):
                sections = []
                for kind in kinds:
                    rules = [r for r in active if r.get("guardrail_type") == kind or kind == "data_quality" and r.get("guardrail_type") == "grain"]
                    if not rules:
                        continue
                    if kind == "schema":
                        count = len({names_by_id.get(str(name), str(name)) for r in rules for name in _parameters(r).get("required_columns", [])})
                        summary = f"{count} required column{'s' if count != 1 else ''}"
                    elif kind == "grain":
                        grain_keys = [
                            names_by_id.get(str(name), str(name))
                            for name in row_key_columns.value
                        ]
                        grain_state = str(grain_policy.value or "Block") if grain_enabled.value else "Not enforced"
                        summary = (" + ".join(grain_keys) or "Key required") + " · " + grain_state
                    elif kind == "data_quality":
                        count = len(set(name for r in rules for name in affected(r)))
                        summary = f"{len(rules)} rule{'s' if len(rules) != 1 else ''} across {count} column{'s' if count != 1 else ''}"
                    elif kind == "sensitive_data":
                        summary = f"{len(rules)} treatment{'s' if len(rules) != 1 else ''}"
                    else:
                        params = _parameters(rules[0])
                        expectation = "No refresh expected" if rules[0].get("rule_type") == "skip" or params.get("refresh_expectation") == "static" else f"{params.get('evidence_method', 'Method required')} · {params.get('evaluation_scope', 'Scope required')} · {params.get('freshness_column', 'Physical update')} · ≤ {params.get('maximum_age', '?')} {params.get('maximum_age_unit', '')}"
                        summary = expectation + " · " + str(rules[0].get("action") or "Warn")
                    key = (role, kind)
                    content = widgets.VBox(
                        [
                            rule_content(
                                "grain" if rule.get("guardrail_type") == "grain" else kind, rule, role=role, show_summary=len(rules) > 1,
                            )
                            for rule in rules
                        ],
                        layout=widgets.Layout(min_width="0", gap="10px", padding="4px 8px"),
                    )
                    section = expandable_guardrail(labels[kind] + " · " + summary, content, key)
                    sections.append(section)
                content = widgets.VBox([widgets.HTML(f"<code>{subtitle}</code>"), *sections, *([] if sections else [widgets.HTML("<span style='color:#667085'>No configured Guardrails for this path.</span>")])], layout=widgets.Layout(min_width="0", gap="6px"))
                box = expandable_guardrail(title, content, ("group", role), default=True)
                sidebar_groups[role] = box
                return box

            guardrail_sidebar.children = (
                group("read", "When this table is read", "orchestrate_read()", ("freshness", "schema", "data_quality")),
                group("write", "Before this table is written", "orchestrate_write()", ("schema", "sensitive_data", "data_quality")),
            )
            sidebar_snapshot["signature"] = signature
            close_sidebar_widgets(previous)

        runtime_summary_html = (
            "<div style='color:#667085;font-size:12px;margin-top:14px;'>"
            "Expand to read saved profile, lineage and pipeline usage metadata.</div>"
        )

        def render_table_summary(_change: dict[str, Any] | None = None) -> None:
            freshness_controls = table_rules["freshness"]
            source_refresh_expectation = "Not configured"
            if freshness_controls["enabled"].value:
                source_refresh_expectation = f"metadata · full_dataset · {freshness_age.value} {freshness_unit.value}"

            table_summary.value = (
                "<div style='color:var(--form-accent);font-size:11px;font-weight:800;"
                "'>Table</div>"
                f"<div style='color:#172b4d;font-size:18px;font-weight:700;margin-top:6px;'>"
                f"{html.escape(str(table.get('table_name') or state.get('table_id') or ''))}</div>"
                f"<div style='color:#667085;font-size:12px;margin-top:2px;'>"
                f"{html.escape(str(table.get('schema_name') or ''))}</div>"
                f"<div style='color:#667085;font-size:12px;margin-top:5px;'>v{row['contract_version']} · "
                f"{html.escape(str(row.get('status') or '').upper())}</div>"
                + f"<div style='color:#667085;font-size:12px;'>{html.escape(str(table.get('_workspace_name') or 'Unknown workspace'))}</div>"
            )
            table_context_content.value = (
                table_identity_html()
                + runtime_summary_html
                + "<div style='border-top:1px solid #e6eaef;margin:14px 0;'></div>"
                + "<div style='margin-top:12px;'>"
                "<div style='color:#667085;font-size:11px;'>Grain</div>"
                f"<div style='font-weight:600;'>{html.escape(str(table_grain.value or 'Not defined'))}</div></div>"
                "<div style='margin-top:12px;'>"
                "<div style='color:#667085;font-size:11px;'>Classification</div>"
                f"<div style='font-weight:600;'>{html.escape(str(table_classification.value or 'Not classified'))}</div></div>"
                "<div style='margin-top:12px;'>"
                "<div style='color:#667085;font-size:11px;'>Row Key</div>"
                f"<div style='font-weight:600;'>{html.escape(', '.join(row_key_columns.value) or 'Not defined')}</div></div>"
                "<div style='margin-top:12px;'>"
                "<div style='color:#667085;font-size:11px;'>Expected source refresh</div>"
                f"<div style='font-weight:600;'>{html.escape(source_refresh_expectation)}</div></div>"
            )
            if state.get("workspace_id"):
                difference = state.get("observation_difference", {})
                for key, label in (("unaccounted_columns", "New / unaccounted columns"),
                                   ("missing_contracted_columns", "Missing contracted columns")):
                    if difference.get(key):
                        table_summary.value += f"<p><b>{label}:</b> {html.escape(', '.join(difference[key]))}</p>"
            render_guardrail_sidebar()

        table_grain.observe(render_table_summary, names="value")
        row_key_columns.observe(render_table_summary, names="value")
        table_classification.observe(render_table_summary, names="value")
        for rule_controls in table_rules.values():
            rule_controls["enabled"].observe(render_table_summary, names="value")
        for freshness_control in table_rules["freshness"]["parameters"]:
            freshness_control.observe(render_table_summary, names="value")

        @busy_action("Reading profile, lineage and pipeline usage metadata…")
        def ensure_runtime_context() -> None:
            nonlocal runtime_context, runtime_summary_html
            if runtime_context:
                return
            if current.get("payload", {}).get("source", {}).get("source_type") == "file":
                runtime_context = {"latest_profile": None, "column_profiles": {}, "profile_contexts": {}, "pipeline_usage": []}
                runtime_summary_html = runtime_context_html()
                return
            loaded = contracts.get_table_runtime_context(
                config=config, active_workspace_id=active_workspace_id, spark_session=spark,
                table_id=str(state.get("dataset_id") or ""),
                metadata_workspace_id=routing_workspace_id,
            )
            runtime_context = loaded
            # Reuse the bulk profile read when Columns is opened.
            if "profile_contexts" in loaded:
                profiles = loaded["profile_contexts"]
                for column in authoring_columns:
                    column_id = str(column.get("column_id") or "")
                    state["_profile_cache"][(active_workspace_id, str(state["dataset_id"]), column_id)] = profiles.get(
                        column_id, {"kind": "unavailable", "message": (
                            f"Not yet profiled in workspace {active_workspace_id}. "
                            "Select the workspace where profiling ran, then reopen the contract to reload its profiles."
                        )}
                    )
            runtime_summary_html = runtime_context_html()
            render_table_summary()

        def table_context_expanded(change: dict[str, Any]) -> None:
            if change.get("new") != 0 or runtime_context:
                return
            try:
                ensure_runtime_context()
            except Exception as exc:
                set_status(_format_widget_exception(exc, phase="table context metadata read"), error=True)

        table_context_accordion.observe(table_context_expanded, names="selected_index")
        def definition_section(
            title: str,
            classification: Any,
            description: Any,
            suggestion: Any,
            accept_button: Any,
            rerun_button: Any,
        ) -> Any:
            if ai_visible:
                suggestion_box = widgets.VBox(
                    [suggestion, shared.action_row(widgets, [accept_button, rerun_button])],
                    layout=widgets.Layout(width="100%", min_width="0", gap="4px"),
                )
                content = widgets.GridBox(
                    [
                        widgets.HTML("<b>Classification</b>"), classification, widgets.HTML(""),
                        widgets.HTML("<b>Description</b>"), description, suggestion_box,
                    ],
                    layout=widgets.Layout(
                        width="100%",
                        grid_template_columns="120px minmax(240px, 1fr) minmax(240px, 1fr)",
                        grid_gap="10px 16px",
                        align_items="flex-start",
                    ),
                )
            else:
                content = widgets.GridBox(
                    [
                        widgets.HTML("<b>Classification</b>"), classification,
                        widgets.HTML("<b>Description</b>"), description,
                    ],
                    layout=widgets.Layout(
                        width="100%",
                        grid_template_columns="120px minmax(240px, 1fr)",
                        grid_gap="10px 16px",
                        align_items="flex-start",
                    ),
                )
            content.add_class("fabricops-contract-labeled-grid")
            return shared.form_section(widgets, title=title, children=[content])

        def guardrail_section(
            title: str,
            *,
            banner_title: str,
            banner_detail: str,
            description: str,
            primary_children: list[Any],
            ai_children: list[Any] | None = None,
            header_controls: list[Any] | None = None,
        ) -> Any:
            """Render every Guardrail with one consistent primary/assistant layout."""
            banner = widgets.HTML(
                "<div style='background:#f6f8fa;border-left:3px solid var(--form-accent);"
                "padding:8px 10px;margin-bottom:8px;font-size:12px;line-height:1.5;'>"
                f"<b>{html.escape(banner_title)}</b>"
                f"<br><span style='color:#667085;'>{html.escape(banner_detail)}</span></div>"
            )
            primary = widgets.VBox(
                [
                    banner,
                    widgets.HTML(
                        "<div style='color:#667085;font-size:12px;line-height:1.5;"
                        "margin-bottom:4px;'>"
                        + html.escape(description)
                        + "</div>"
                    ),
                    *primary_children,
                ],
                layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
            )
            if ai_visible and ai_children:
                assistant = widgets.VBox(
                    list(ai_children),
                    layout=widgets.Layout(
                        width="100%", min_width="0", gap="8px",
                        padding="0 0 0 16px",
                        border_left="1px solid #e1e6eb",
                    ),
                )
                content = widgets.GridBox(
                    [primary, assistant],
                    layout=widgets.Layout(
                        width="100%",
                        grid_template_columns="minmax(0, 68fr) minmax(240px, 32fr)",
                        grid_gap="16px",
                        align_items="flex-start",
                    ),
                )
            else:
                content = primary
            section_children: list[Any] = []
            if header_controls:
                section_children.append(
                    widgets.HBox(
                        list(header_controls),
                        layout=widgets.Layout(
                            width="auto",
                            min_width="0",
                            gap="18px",
                            align_items="center",
                            justify_content="flex-start",
                            overflow="visible",
                        ),
                    )
                )
                section_children[-1].add_class("fabricops-contract-options")
            if ai_visible and ai_children:
                content.add_class("fabricops-contract-assistant-grid")
            section_children.append(content)
            return shared.form_section(widgets, title=title, children=section_children)

        table_definition_primary = widgets.VBox(
            [
                widgets.HTML("<b>Classification</b>"),
                table_classification,
                table_classification_sources,
                widgets.HTML("<b>Description</b>"),
                table_description,
            ],
            layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
        )
        if ai_visible:
            table_definition_assistant = widgets.VBox(
                [
                    widgets.HTML("<b>AI suggestion</b>"),
                    table_description_ai,
                    shared.action_row(
                        widgets, [accept_table_description, rerun_table_description]
                    ),
                ],
                layout=widgets.Layout(
                    width="100%", min_width="0", gap="8px",
                    padding="0 0 0 16px",
                    border_left="1px solid #e1e6eb",
                ),
            )
            table_definition_content = widgets.GridBox(
                [table_definition_primary, table_definition_assistant],
                layout=widgets.Layout(
                    width="100%",
                    grid_template_columns="minmax(0, 68fr) minmax(240px, 32fr)",
                    grid_gap="16px",
                    align_items="flex-start",
                ),
            )
        else:
            table_definition_content = table_definition_primary
        if ai_visible:
            table_definition_content.add_class("fabricops-contract-assistant-grid")
        table_definition = shared.form_section(
            widgets, title="Table definition", children=[table_definition_content]
        )
        grain_definition = shared.form_section(
            widgets,
            title="Grain & Row Key",
                children=[
                    widgets.HBox(
                        [grain_enabled, grain_policy],
                        layout=widgets.Layout(
                            width="100%", min_width="0",
                            align_items="flex-end", flex_flow="row wrap",
                        ),
                    ),
                    widgets.HTML(
                        "<div style='color:#667085;font-size:12px;line-height:1.5;"
                        "margin-bottom:4px;'>Define what one row represents, then "
                        "select the column or smallest column combination that should "
                        "uniquely identify that row. Enforcement is optional; enabling it defaults to Block. "
                        "A null in any key component fails; blank strings are values. "
                        "Read checks returned rows; Write checks prepared input after Sensitive Data treatment. "
                        "Append and SCD checks do not guarantee resulting-table uniqueness. "
                        "For SCD2 history, use a version-aware key such as business key + effective timestamp.</div>"
                    ),
                    widgets.GridBox(
                        [
                            widgets.VBox(
                                [
                                    table_grain,
                                    row_key_columns,
                                    grain_profile_evidence,
                                ],
                                layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
                            ),
                            *(
                                [
                                    widgets.VBox(
                                        [
                                            widgets.HTML("<b>AI suggestion</b>"),
                                            grain_ai,
                                            shared.action_row(
                                                widgets, [suggest_grain, accept_grain]
                                            ),
                                        ],
                                        layout=widgets.Layout(
                                            width="100%", min_width="0", gap="8px",
                                            padding="0 0 0 16px",
                                            border_left="1px solid #e1e6eb",
                                        ),
                                    )
                                ]
                                if ai_visible else []
                            ),
                        ],
                        layout=widgets.Layout(
                            width="100%",
                            grid_template_columns=(
                                "minmax(0, 68fr) minmax(240px, 32fr)"
                                if ai_visible else "minmax(0, 1fr)"
                            ),
                            grid_gap="16px",
                            align_items="flex-start",
                        ),
                    ),
                ],
            )
        grain_definition.children[1].add_class("fabricops-grain-controls")
        grain_definition.children[3].add_class("fabricops-grain-fields")
        grain_definition.children[3].add_class("fabricops-contract-assistant-grid")
        table_right = (
            grain_definition,
            table_definition,
            guardrail_section(
                "Freshness",
                banner_title="Applies when this dataset is read by a downstream pipeline.",
                banner_detail=(
                    "This rule is checked when the dataset is consumed as an input, "
                    "not when that dataset is written."
                ),
                description=(
                    "Check whether this source is recent enough. Evidence is selected automatically "
                    "by source type: file modification metadata for files, timestamp column for tables."
                ),
                header_controls=[
                    table_rules["freshness"]["enabled"],
                    table_rules["freshness"]["block"],
                ],
                primary_children=[
                    *table_rules["freshness"]["display"],
                ],
            ),
        )
        view_content["Table"] = (table_left, table_right)


        # Columns: one editor, hydrated on selection, with profile evidence isolated from payload.
        required_columns = {str(column["column_id"]) for column in columns if column.get("presence", "required") == "required"}
        render_table_summary()
        saved_payload = json.loads(
            str(current["contract"].get("contract_payload_json") or "{}")
        )
        contracted_columns = {
            str(item.get("column_id") or ""): dict(item)
            for item in (saved_payload.get("table", {}).get("columns", []) or [])
            if item.get("column_id")
        }
        observed_types = {
            str(item.get("column_id") or ""): str(item.get("data_type") or "")
            for item in current.get("catalogue_rows", []) if item.get("column_id") and item.get("is_active") is not False
        }
        observed_types = {str(column["column_id"]): observed_types.get(str(column["column_id"]), "") for column in columns}
        contracted_types = {
            cid: str(contracted_columns.get(cid, {}).get("data_type") or observed_type)
            for cid, observed_type in observed_types.items()
        }
        column_options: list[tuple[str, str]] = []
        column_option_style = widgets.HTML()
        column_search = widgets.Text(placeholder="Search columns", layout=widgets.Layout(width="100%", min_width="0", max_width="100%"))
        column_select = widgets.Select(
            options=(), rows=10,
            layout=widgets.Layout(
                width="100%", min_width="0", max_width="100%",
                height="180px", min_height="130px", max_height="180px", flex="0 0 auto",
            ),
        )
        column_select.add_class("fabricops-contract-columns")
        column_select.add_class("fabricops-contract-list")
        column_context = widgets.HTML()
        empty_column = widgets.HTML("<p>No columns match this search. Change or clear the search to select a column.</p>")
        profile_context = widgets.HTML(
            "<p>No column selected.</p>",
            layout=widgets.Layout(
                width="100%", min_width="0", max_width="100%",
                height="auto", overflow="visible",
            ),
        )
        column_description = widgets.Textarea(continuous_update=False, disabled=not editable, **shared.widget_common(widgets, "Description", textarea=True))
        column_classification = widgets.Dropdown(options=classification_options, disabled=not editable, **shared.widget_common(widgets, "Classification"))
        column_description.description = ""
        column_description.layout.close()
        column_description.layout = widgets.Layout(width="100%", min_width="0", height="110px")
        column_classification.description = "Output classification"
        column_classification.layout.close()
        column_classification.layout = widgets.Layout(
            width="100%", min_width="0", max_width="560px"
        )
        column_description_ai = widgets.HTML()
        accept_column_description = widgets.Button(description="Apply", disabled=not editable, button_style="info")
        rerun_column_description = widgets.Button(description="Re-run", disabled=not editable)
        state["_ai_buttons"].extend([accept_column_description, rerun_column_description])
        required = widgets.Checkbox(description="Required presence", tooltip="Controls whether the column must exist; null values are a separate concern.", disabled=not editable, layout=widgets.Layout(width="auto", min_width="0", margin="0"))
        required.add_class("fabricops-column-required")
        required_hint = widgets.HTML()
        column_required_controls = widgets.VBox(
            [required, required_hint],
            layout=widgets.Layout(width="auto", min_width="170px", gap="2px"),
        )
        column_required_controls.add_class("fabricops-column-required-controls")
        datatype_choice = widgets.Dropdown(
            options=(), disabled=not editable,
            **shared.widget_common(widgets, "Contract datatype"),
        )
        datatype_choice.layout.display = "none"
        column_identity = widgets.VBox(
            [column_context, datatype_choice],
            layout=widgets.Layout(width="100%", min_width="0", gap="4px"),
        )
        column_identity.add_class("fabricops-column-identity")
        column_header = widgets.HBox(
            [column_identity, column_required_controls],
            layout=widgets.Layout(
                width="100%", min_width="0", align_items="center",
                justify_content="space-between", flex_flow="row wrap",
            ),
        )
        column_header.add_class("fabricops-column-header")
        sensitive_enabled = widgets.Checkbox(description="Enabled", disabled=not editable)
        pii_type = widgets.Dropdown(
            options=[(label, value) for value, label in PII_LABELS.items()],
            value="none", disabled=not editable, **shared.widget_common(widgets, "PII assessment"),
        )
        pii_reason = widgets.Textarea(continuous_update=False,
            disabled=not editable, **shared.widget_common(widgets, "Reason", textarea=True)
        )
        sensitive_treatment = widgets.Dropdown(options=_SENSITIVE_TREATMENT_OPTIONS, disabled=not editable, **shared.widget_common(widgets, "Treatment"))
        working_sensitive_controls.update({
            "column_select": column_select,
            "enabled": sensitive_enabled,
            "pii_type": pii_type,
            "reason": pii_reason,
            "treatment": sensitive_treatment,
            "classification": column_classification,
        })
        for sensitive_field in (pii_type, sensitive_treatment, pii_reason):
            sensitive_field.layout.width = "100%"
            sensitive_field.layout.min_width = "0"
            sensitive_field.layout.max_width = "722px"
        sensitive_rule_preview = widgets.HTML()
        mask_mode = widgets.Dropdown(options=(("Full mask", "full"), ("Partial mask", "partial")),
                                     disabled=not editable, **shared.widget_common(widgets, "Mask style"))
        treatment_help = widgets.HTML()
        bucket_mode = widgets.Dropdown(options=(("Approved ranges", "ranges"), ("Fixed width", "width")),
                                       disabled=not editable, **shared.widget_common(widgets, "Bucket method"))
        bucket_width = widgets.Text(continuous_update=False, value="10", disabled=not editable, **shared.widget_common(widgets, "Interval width"))
        bucket_origin = widgets.Text(continuous_update=False, value="0", disabled=not editable, **shared.widget_common(widgets, "Starting point"))
        mask_start = widgets.Text(continuous_update=False, value="0", disabled=not editable, **shared.widget_common(widgets, "Visible characters at start"))
        mask_end = widgets.Text(continuous_update=False, value="0", disabled=not editable, **shared.widget_common(widgets, "Visible characters at end"))
        mask_character = widgets.Text(continuous_update=False, value="*", disabled=not editable, **shared.widget_common(widgets, "Mask character"))
        bucket_bins = widgets.Text(continuous_update=False, disabled=not editable, **shared.widget_common(widgets, "Lower bounds"))
        bucket_labels = widgets.Text(continuous_update=False, disabled=not editable, **shared.widget_common(widgets, "Band labels"))
        def dq_checkbox(label: str) -> Any:
            control = widgets.Checkbox(
                description=label,
                disabled=not editable,
                style={"description_width": "initial"},
                layout=widgets.Layout(width="auto", max_width="100%", min_width="0"),
            )
            control.add_class("fabricops-dq-checkbox")
            return control

        dq_completeness_failure = widgets.Text(continuous_update=False,
            value="0", disabled=not editable,
            **shared.widget_common(widgets, "Accepted failure rate %"),
        )
        dq_blank_missing = dq_checkbox("Count blank text as missing")
        dq_blank_missing.value = False
        dq_uniqueness_failure = widgets.Text(continuous_update=False,
            value="0", disabled=not editable,
            **shared.widget_common(widgets, "Accepted failure rate %"),
        )
        dq_whitelist_values = widgets.Text(continuous_update=False,
            disabled=not editable,
            placeholder="Example: Active, Inactive",
            **shared.widget_common(widgets, "Whitelist"),
        )
        dq_blacklist_values = widgets.Text(continuous_update=False,
            disabled=not editable,
            placeholder="Example: Unknown, N/A",
            **shared.widget_common(widgets, "Blacklist"),
        )
        dq_whitelist_count = widgets.HTML()
        dq_blacklist_count = widgets.HTML()

        def dq_value_count_text(raw: Any) -> str:
            values = [item.strip() for item in str(raw or "").split(",") if item.strip()]
            count = len(values)
            noun = "value" if count == 1 else "values"
            return (
                "<div style='margin-left:162px;color:#667085;font-size:11px;'>"
                f"{count} {noun} · comma-separated</div>"
            )

        def refresh_dq_value_counts(_change: dict[str, Any] | None = None) -> None:
            dq_whitelist_count.value = dq_value_count_text(dq_whitelist_values.value)
            dq_blacklist_count.value = dq_value_count_text(dq_blacklist_values.value)

        dq_whitelist_values.observe(refresh_dq_value_counts, names="value")
        dq_blacklist_values.observe(refresh_dq_value_counts, names="value")
        refresh_dq_value_counts()
        dq_minimum = widgets.Text(continuous_update=False,
            disabled=not editable, **shared.widget_common(widgets, "Lower bound")
        )
        dq_minimum_inclusive = dq_checkbox("Include lower bound")
        dq_minimum_inclusive.value = True
        dq_maximum = widgets.Text(continuous_update=False,
            disabled=not editable, **shared.widget_common(widgets, "Upper bound")
        )
        dq_maximum_inclusive = dq_checkbox("Include upper bound")
        dq_maximum_inclusive.value = True
        dq_whitelist_max_failure = widgets.Text(continuous_update=False,
            value="0", disabled=not editable,
            **shared.widget_common(widgets, "Accepted failure rate %"),
        )
        dq_range_max_failure = widgets.Text(continuous_update=False,
            value="0", disabled=not editable,
            **shared.widget_common(widgets, "Accepted failure rate %"),
        )
        dq_family_controls = {
            "completeness": {
                "enabled": dq_checkbox("Enabled"),
                "block": widgets.ToggleButtons(options=[("Warn", False), ("Block", True)], value=False, description="On failure", disabled=not editable),
                "parameters": (dq_completeness_failure, dq_blank_missing),
            },
            "uniqueness": {
                "enabled": dq_checkbox("Enabled"),
                "block": widgets.ToggleButtons(options=[("Warn", False), ("Block", True)], value=False, description="On failure", disabled=not editable),
                "parameters": (dq_uniqueness_failure,),
            },
            "value_set": {
                "enabled": dq_checkbox("Enabled"),
                "block": widgets.ToggleButtons(options=[("Warn", False), ("Block", True)], value=False, description="On failure", disabled=not editable),
                "parameters": (dq_whitelist_values, dq_blacklist_values, dq_whitelist_max_failure),
            },
            "range": {
                "enabled": dq_checkbox("Enabled"),
                "block": widgets.ToggleButtons(options=[("Warn", False), ("Block", True)], value=False, description="On failure", disabled=not editable),
                "parameters": (
                    dq_minimum, dq_minimum_inclusive,
                    dq_maximum, dq_maximum_inclusive, dq_range_max_failure,
                ),
            },
        }
        dq_parameter_controls = (
            dq_completeness_failure, dq_blank_missing, dq_uniqueness_failure, dq_whitelist_max_failure, dq_range_max_failure,
            dq_whitelist_values, dq_blacklist_values,
            dq_minimum, dq_minimum_inclusive, dq_maximum, dq_maximum_inclusive,
        )
        # Internal compatibility aliases follow the default deterministic family.
        dq_enabled = dq_family_controls["completeness"]["enabled"]
        dq_block = dq_family_controls["completeness"]["block"]
        sensitive_ai = widgets.HTML()
        accept_sensitive = widgets.Button(description="Apply", disabled=not editable, button_style="info")
        rerun_sensitive = widgets.Button(description="Re-run", disabled=not editable)
        state["_ai_buttons"].extend([accept_sensitive, rerun_sensitive])
        sensitive_ai_actions = shared.action_row(
            widgets, [accept_sensitive, rerun_sensitive]
        )
        for control in (
            table_description, table_classification,
            column_description, column_classification, datatype_choice,
            pii_type, pii_reason, sensitive_treatment,
            mask_start, mask_end, mask_character, bucket_bins, bucket_labels, bucket_mode, bucket_width, bucket_origin,
            dq_completeness_failure, dq_uniqueness_failure, dq_whitelist_values, dq_blacklist_values,

            dq_minimum, dq_maximum,
        ):
            control.layout.width = "100%"
            control.layout.max_width = "560px"
            control.layout.min_width = "0"
        for classification in (table_classification, column_classification):
            classification.layout.width = "250px"
            classification.layout.max_width = "100%"
        draft_scope = (str(current["contract_id"]), int(current["contract_version"]))
        unsaved_columns: dict[str, dict[str, Any]] = state["_column_drafts"].setdefault(
            draft_scope, {}
        )
        selected_dq_by_column: dict[str, str] = state["_column_dq_selection"].setdefault(
            draft_scope, {}
        )

        def selected_column() -> dict[str, Any]:
            return next((c for c in columns if str(c.get("column_id") or "") == str(column_select.value or "")), {})

        hydrating = {"active": False}
        refreshing_column_options = {"active": False}
        hydrated_column_snapshots: dict[str, dict[str, Any]] = {}

        def dq_snapshot() -> dict[str, dict[str, Any]]:
            return {
                kind: {
                    "enabled": bool(controls["enabled"].value),
                    "block": bool(controls["block"].value),
                    "parameters": [control.value for control in controls["parameters"]],
                }
                for kind, controls in dq_family_controls.items()
            }

        def column_editor_snapshot() -> dict[str, Any]:
            return {
                "description": column_description.value,
                "classification": column_classification.value,
                "required": required.value,
                "sensitive_enabled": sensitive_enabled.value,
                "pii_type": pii_type.value,
                "pii_reason": pii_reason.value,
                "sensitive_treatment": sensitive_treatment.value,
                "mask_mode": mask_mode.value,
                "bucket_mode": bucket_mode.value,
                "bucket_width": bucket_width.value,
                "bucket_origin": bucket_origin.value,
                "mask_start": mask_start.value,
                "mask_end": mask_end.value,
                "mask_character": mask_character.value,
                "bucket_bins": bucket_bins.value,
                "bucket_labels": bucket_labels.value,
                "dq": dq_snapshot(),
            }

        def hydrate_dq_family(column_id: str, kind: str) -> None:
            """Hydrate one column/family pair into its always-visible editor."""
            controls = dq_family_controls[kind]
            defaults = {
                "completeness": ("0", False),
                "uniqueness": ("0",),
                "value_set": ("", "", "0"),
                "range": ("", True, "", True, "0"),
            }[kind]
            for control, value in zip(controls["parameters"], defaults, strict=True):
                control.value = value
            controls["enabled"].value = False
            controls["block"].value = False
            matching_rules = [
                row for row in session_guardrails()
                if str(row.get("guardrail_type") or "").lower() in {"data_quality", "dq"}
                and str(row.get("column_id") or "") == column_id
                and str(row.get("rule_type") or "") == kind
            ]
            if not matching_rules:
                return
            if kind == "value_set":
                by_mode = {
                    str(_parameters(rule).get("mode") or "").lower(): rule
                    for rule in matching_rules
                }
                allow_rule = by_mode.get("allow", {})
                dq_whitelist_max_failure.value = str(_parameters(allow_rule).get("maximum_failure_percent", 0))
                block_rule = by_mode.get("block", {})
                dq_whitelist_values.value = ", ".join(
                    map(str, _parameters(allow_rule).get("values", []))
                )
                dq_blacklist_values.value = ", ".join(
                    map(str, _parameters(block_rule).get("values", []))
                )
                active_rules = [
                    rule for rule in (allow_rule, block_rule)
                    if rule and rule.get("is_active", True)
                ]
                controls["enabled"].value = bool(active_rules)
                controls["block"].value = bool(active_rules) and all(
                    str(rule.get("action") or "Warn") == "Block"
                    for rule in active_rules
                )
                refresh_dq_value_counts()
                return
            rule = matching_rules[0]
            params = _parameters(rule)
            values = {
                "completeness": (
                    str(params.get("maximum_missing_percent", 0)),
                    bool(params.get("treat_blank_as_missing", False)),
                ),
                "uniqueness": (
                    str(params.get("maximum_failure_percent", 0)) if params.get("minimum_unique_percent", 100) == 100 else "",
                ),
                "range": (
                    "" if params.get("minimum") is None else str(params["minimum"]),
                    bool(params.get("minimum_inclusive", True)),
                    "" if params.get("maximum") is None else str(params["maximum"]),
                    bool(params.get("maximum_inclusive", True)),
                    str(params.get("maximum_failure_percent", 0)),
                ),
            }[kind]
            for control, value in zip(controls["parameters"], values, strict=True):
                control.value = value
            controls["enabled"].value = bool(rule.get("is_active", True))
            controls["block"].value = str(rule.get("action") or "Warn") == "Block"

        # Column selection can run before the DQ sections have been built.
        dq_visibility = {"refresh": None}

        def hydrate_column(column_id: str) -> None:
            hydrating["active"] = True
            try:
                live_enrichments, live_guardrails = current_rows()
                selected = next((c for c in columns if str(c.get("column_id") or "") == column_id), {})
                observed_type = observed_types.get(column_id, "")
                contract_type = str(contracted_types.get(column_id) or observed_type)
                mismatch = bool(contract_type and observed_type and contract_type != observed_type)
                column_name = html.escape(str(selected.get("column_name") or ""))
                if mismatch:
                    column_context.value = (
                        "<div class='fabricops-column-context'>"
                        f"<span class='fabricops-column-name'>{column_name}</span>"
                        "<span class='fabricops-column-status is-drift'>Datatype drift detected</span>"
                        f"<div class='fabricops-column-meta'>"
                        f"Contract: <b>{html.escape(contract_type)}</b> · "
                        f"Observed: <b style='color:#a4262c'>{html.escape(observed_type)}</b></div>"
                        "</div>"
                    )
                    datatype_choice.options = (
                        (f"Keep contract · {contract_type}", contract_type),
                        (f"Accept observed · {observed_type}", observed_type),
                    )
                    _set_selection_value(
                        datatype_choice,
                        contract_type,
                        control_name="datatype_choice",
                        table_name=str(table.get("table_name") or ""),
                        column_name=str(selected.get("column_name") or ""),
                    )
                    datatype_choice.layout.display = ""
                else:
                    column_context.value = (
                        "<div class='fabricops-column-context'>"
                        f"<span class='fabricops-column-name'>{column_name}</span>"
                        f"<span class='fabricops-column-status'>"
                        f"{html.escape(contract_type or observed_type)}</span></div>"
                    )
                    datatype_choice.options = ((contract_type or observed_type, contract_type or observed_type),)
                    _set_selection_value(
                        datatype_choice,
                        contract_type or observed_type,
                        control_name="datatype_choice",
                        table_name=str(table.get("table_name") or ""),
                        column_name=str(selected.get("column_name") or ""),
                    )
                    datatype_choice.layout.display = "none"
                if editable and selected.get("review_status") in {"unreviewed", "changed"}:
                    label = "New column" if selected["review_status"] == "unreviewed" else "Changed datatype"
                    column_context.value += (
                        "<div class='fabricops-column-meta'>"
                        f"{label} · Review before freezing</div>"
                    )
                if state.get("workspace_id") and not observed_type:
                    column_context.value += (
                        "<div class='fabricops-column-meta'>"
                        "Missing from the selected current observation</div>"
                    )
                column_description.value = enrichment_value(live_enrichments, "column", "Description", column_id)
                _set_selection_value(
                    column_classification,
                    _valid_dropdown_value(
                        classification_options,
                        enrichment_value(
                            live_enrichments, "column", "Classification", column_id
                        ),
                        fallback="",
                    ),
                    control_name="column_classification",
                    table_name=str(table.get("table_name") or ""),
                    column_name=str(selected.get("column_name") or ""),
                )
                required.value = column_id in required_columns or selected.get("column_name") in required_columns
                sensitive = next((r for r in live_guardrails if str(r.get("guardrail_type") or "").lower() == "sensitive_data" and str(r.get("column_id") or "") == column_id), {})
                sensitive_parameters = _parameters(sensitive)
                pii_type_options = tuple(PII_LABELS)
                _set_selection_value(
                    pii_type,
                    _valid_dropdown_value(
                        pii_type_options,
                        sensitive_parameters.get("pii_type")
                        or ("direct" if sensitive else "none"),
                        fallback="none",
                    ),
                    control_name="pii_type",
                    table_name=str(table.get("table_name") or ""),
                    column_name=str(selected.get("column_name") or ""),
                )
                pii_reason.value = str(sensitive_parameters.get("pii_reason") or "")
                sensitive_enabled.value = bool(sensitive and sensitive.get("is_active", True))
                allowed_treatments = contracts.sensitive_data_treatments_for_type(str(datatype_choice.value or contract_type or observed_type))
                sensitive_treatment.options = tuple(option for option in _SENSITIVE_TREATMENT_OPTIONS if option[1] in allowed_treatments)
                _set_selection_value(
                    sensitive_treatment,
                    _valid_dropdown_value(
                        allowed_treatments,
                        sensitive_parameters.get("treatment") or allowed_treatments[0],
                        fallback=None if sensitive_parameters.get("treatment") in {"mask", "tokenize", "bucket", "remove"} else allowed_treatments[0],
                    ),
                    control_name="sensitive_treatment",
                    table_name=str(table.get("table_name") or ""),
                    column_name=str(selected.get("column_name") or ""),
                )
                mask_start.value = str(sensitive_parameters.get("preserve_start", 0))
                mask_end.value = str(sensitive_parameters.get("preserve_end", 0))
                mask_character.value = str(sensitive_parameters.get("mask_character") or "*")
                mask_mode.value = "partial" if int(mask_start.value) or int(mask_end.value) else "full"
                bucket_mode.value = "width" if "bin_width" in sensitive_parameters else "ranges"
                bucket_width.value = str(sensitive_parameters.get("bin_width", 10))
                bucket_origin.value = str(sensitive_parameters.get("bin_origin", 0))
                bucket_bins.value = ", ".join(map(str, sensitive_parameters.get("bins", [])))
                bucket_labels.value = ", ".join(map(str, sensitive_parameters.get("labels", [])))
                if dq_visibility["refresh"] is not None:
                    dq_visibility["refresh"](str(datatype_choice.value or contract_type or observed_type))
                for kind in _COLUMN_DQ_TYPES:
                    hydrate_dq_family(column_id, kind)
                hydrated_column_snapshots[column_id] = column_editor_snapshot()
                pending = unsaved_columns.get(column_id)
                if pending:
                    column_description.value = pending["description"]
                    column_classification.value = _valid_dropdown_value(
                        classification_options, pending["classification"], fallback=""
                    )
                    required.value = pending["required"]
                    sensitive_enabled.value = pending["sensitive_enabled"]
                    pii_type.value = _valid_dropdown_value(
                        tuple(PII_LABELS), pending["pii_type"], fallback="none"
                    )
                    pii_reason.value = pending["pii_reason"]
                    sensitive_treatment.value = _valid_dropdown_value(
                        allowed_treatments,
                        pending["sensitive_treatment"],
                        fallback=None,
                    )
                    mask_mode.value = pending["mask_mode"]
                    bucket_mode.value = pending["bucket_mode"]
                    bucket_width.value = pending["bucket_width"]
                    bucket_origin.value = pending["bucket_origin"]
                    mask_start.value = pending["mask_start"]
                    mask_end.value = pending["mask_end"]
                    mask_character.value = pending["mask_character"]
                    bucket_bins.value = pending["bucket_bins"]
                    bucket_labels.value = pending["bucket_labels"]
                    for kind, values in pending.get("dq", {}).items():
                        controls = dq_family_controls.get(kind)
                        if not controls:
                            continue
                        controls["enabled"].value = bool(values.get("enabled"))
                        controls["block"].value = bool(values.get("block"))
                        for control, value in zip(
                            controls["parameters"], values.get("parameters", []), strict=False
                        ):
                            control.value = value
                profile_context.value = "<p>Open Columns to load profile evidence.</p>"
            finally:
                hydrating["active"] = False

        def load_selected_profile() -> None:
            column_id = str(column_select.value or "")
            if not column_id:
                profile_context.value = "<p>No column selected.</p>"
                return
            try:
                ensure_runtime_context()
                profile_context.value = _profile_html(load_profile_context(column_id))
            except Exception as exc:
                profile_context.value = f"<p>{html.escape(str(exc))}</p>"

        state["_load_selected_profile"] = load_selected_profile


        removal_confirmation = widgets.HTML()
        confirm_removal = widgets.Button(description="Remove and uncheck Required", button_style="warning")
        cancel_removal = widgets.Button(description="Cancel")
        removal_confirmation_box = widgets.VBox(
            [removal_confirmation, widgets.HBox([confirm_removal, cancel_removal])],
            layout=widgets.Layout(width="100%", gap="6px", display="none"),
        )
        removal_state = {"pending": False, "previous_treatment": "tokenize", "previous_enabled": False}

        def current_sensitive_parameters() -> dict[str, Any]:
            """Return the working treatment settings for contextual guidance."""
            treatment = str(sensitive_treatment.value or "")
            parameters: dict[str, Any] = {"treatment": treatment}
            if treatment == "mask":
                parameters.update({
                    "preserve_start": mask_start.value,
                    "preserve_end": mask_end.value,
                    "mask_character": mask_character.value,
                })
            elif treatment == "bucket" and bucket_mode.value == "width":
                parameters.update({
                    "bin_width": bucket_width.value,
                    "bin_origin": bucket_origin.value,
                })
            elif treatment == "bucket":
                parameters.update({
                    "bins": [
                        value.strip()
                        for value in str(bucket_bins.value or "").split(",")
                        if value.strip()
                    ],
                    "labels": [
                        value.strip()
                        for value in str(bucket_labels.value or "").split(",")
                        if value.strip()
                    ],
                })
            return parameters

        def update_sensitive_fields(change: dict[str, Any] | None = None) -> None:
            treatment = str(sensitive_treatment.value or "")
            enabled = bool(sensitive_enabled.value) and str(pii_type.value or "none") != "none"
            mask_mode.layout.display = "" if enabled and treatment == "mask" else "none"
            for control in (mask_start, mask_end):
                control.layout.display = "" if enabled and treatment == "mask" and mask_mode.value == "partial" else "none"
            mask_character.layout.display = "none"
            bucket_mode.layout.display = "" if enabled and treatment == "bucket" else "none"
            for control in (bucket_bins, bucket_labels):
                control.layout.display = "" if enabled and treatment == "bucket" and bucket_mode.value == "ranges" else "none"
            for control in (bucket_width, bucket_origin):
                control.layout.display = "" if enabled and treatment == "bucket" and bucket_mode.value == "width" else "none"
            treatment_help.value = (
                _sensitive_treatment_guidance(current_sensitive_parameters())
                if enabled else ""
            )
            removing = bool(sensitive_enabled.value) and treatment == "remove"
            if removing and required.value and editable and not hydrating["active"] and not removal_state["pending"]:
                removal_state["pending"] = True
                if change and change.get("owner") is sensitive_treatment:
                    removal_state["previous_treatment"] = str(change.get("old") or "tokenize")
                    removal_state["previous_enabled"] = bool(sensitive_enabled.value)
                else:
                    removal_state["previous_treatment"] = treatment
                    removal_state["previous_enabled"] = False
            if removal_state["pending"] and (not removing or not required.value):
                removal_state["pending"] = False
            removal_confirmation_box.layout.display = "" if removal_state["pending"] else "none"
            removal_confirmation.value = (
                "<div style='background:#fff7e6;border-left:3px solid #b76e00;"
                "padding:9px 12px;font-size:12px;line-height:1.5;'>"
                "<b>Remove this column?</b> It is currently marked Required. "
                "Continuing will uncheck Required and exclude the column from the written output."
                "</div>"
            ) if removal_state["pending"] else ""
            required.disabled = (not editable) or (removing and not removal_state["pending"])
            required_hint.value = (
                "<span style='color:#667085;font-size:12px;'>"
                "Removed columns cannot be required in the written output.</span>"
                if removing and not removal_state["pending"] else ""
            )
            column_classification.disabled = (not editable) or treatment == "remove"
            column_classification.layout.width = "100%"
            column_classification.layout.min_width = "0"
            column_classification.layout.max_width = "722px"
            column_classification.layout.display = "none" if treatment == "remove" else ""

        def refresh_sensitive_rule_preview(
            _change: dict[str, Any] | None = None,
        ) -> None:
            pii_value = str(pii_type.value or "none")
            if not sensitive_enabled.value or pii_value == "none":
                treatment_help.value = ""
                sensitive_rule_preview.value = ""
                return
            treatment_help.value = _sensitive_treatment_guidance(
                current_sensitive_parameters()
            )
            pii_label = PII_LABELS.get(pii_value, pii_value)
            treatment = str(sensitive_treatment.value or "")
            action = "Treatment failure stops the write."
            detail = ""
            if treatment == "mask":
                detail = (
                    f" Preserve {html.escape(str(mask_start.value or '0'))} character(s) at the start "
                    f"and {html.escape(str(mask_end.value or '0'))} at the end."
                )
            elif treatment == "bucket" and bucket_mode.value == "width":
                detail = f" Fixed width: {html.escape(str(bucket_width.value))}; starting point: {html.escape(str(bucket_origin.value))}."
            elif treatment == "bucket":
                bins = str(bucket_bins.value or "").strip()
                labels = str(bucket_labels.value or "").strip()
                if bins:
                    detail = f" Bucket boundaries: <code>{html.escape(bins)}</code>."
                if labels:
                    detail += f" Labels: <code>{html.escape(labels)}</code>."
            reason = str(pii_reason.value or "").strip()
            reason_line = (
                f"<br><span style='color:#667085;'>Reason: {html.escape(reason)}</span>"
                if reason else ""
            )
            current_classification = str(column_classification.value or "")
            classification_effect = (
                " The column will be excluded from the written target."
                if treatment == "remove"
                else (
                     " Output classification: "
                    f"<b>{html.escape(current_classification)}</b>."
                    if current_classification else ""
                )
            )
            sensitive_rule_preview.value = (
                "<div style='background:#f6f8fa;border-left:3px solid var(--form-accent);"
                "padding:9px 11px;margin-top:8px;font-size:12px;line-height:1.5;'>"
                "<b>ⓘ Rule</b><br>"
                f"This column is assessed as <b>{html.escape(pii_label)}</b>. "
                f"Treatment: <b>{html.escape(treatment)}</b>.{detail}"
                f"{classification_effect} {action}"
                f"{reason_line}</div>"
            )

        for sensitive_control in (
            sensitive_enabled, pii_type, pii_reason, sensitive_treatment,
            mask_start, mask_end, mask_character, bucket_bins, bucket_labels, bucket_mode, bucket_width, bucket_origin,
        ):
            sensitive_control.observe(refresh_sensitive_rule_preview, names="value")

        def confirm_column_removal(_button: Any) -> None:
            if not removal_state["pending"]:
                return
            removal_state["pending"] = False
            required.value = False
            update_sensitive_fields()
            sync_sensitive()

        def cancel_column_removal(_button: Any) -> None:
            if not removal_state["pending"]:
                return
            removal_state["pending"] = False
            if str(sensitive_treatment.value or "") != removal_state["previous_treatment"]:
                sensitive_treatment.value = removal_state["previous_treatment"]
            else:
                sensitive_enabled.value = removal_state["previous_enabled"]
            update_sensitive_fields()

        confirm_removal.on_click(confirm_column_removal)
        cancel_removal.on_click(cancel_column_removal)
        def change_mask_style(_change: dict[str, Any]) -> None:
            if not hydrating["active"] and mask_mode.value == "full":
                hydrating["active"] = True
                try:
                    mask_start.value = "0"
                    mask_end.value = "0"
                    mask_character.value = "*"
                finally:
                    hydrating["active"] = False
            update_sensitive_fields()
            sync_sensitive()
            refresh_sensitive_rule_preview()

        mask_mode.observe(change_mask_style, names="value")
        bucket_mode.observe(update_sensitive_fields, names="value")
        sensitive_treatment.observe(update_sensitive_fields, names="value")
        sensitive_enabled.observe(update_sensitive_fields, names="value")
        column_classification.observe(refresh_sensitive_rule_preview, names="value")

        def working_sensitive_changed(change: dict[str, Any]) -> None:
            if hydrating["active"]:
                return
            enabled_now = bool(sensitive_enabled.value)
            if enabled_now and not bool(change.get("old")) and str(sensitive_treatment.value or "") != "remove":
                current = str(column_classification.value or "")
                if current in classification_levels:
                    index = classification_levels.index(current)
                    if index > 0:
                        column_classification.value = classification_levels[index - 1]
            state["_working_sensitive_enabled"] = enabled_now
            render_table_summary()

        def working_dq_changed(_change: dict[str, Any]) -> None:
            if hydrating["active"]:
                return
            state["_working_dq_enabled"] = any(
                bool(controls["enabled"].value)
                for controls in dq_family_controls.values()
            )
            render_table_summary()

        sensitive_enabled.observe(working_sensitive_changed, names="value")
        for controls in dq_family_controls.values():
            controls["enabled"].observe(working_dq_changed, names="value")
        update_sensitive_fields()

        def update_pii_fields(change: dict[str, Any] | None = None) -> None:
            is_pii = str(pii_type.value or "none") != "none"
            if not is_pii:
                sensitive_enabled.value = False
            sensitive_treatment.disabled = not editable or not is_pii
            update_sensitive_fields()

        pii_type.observe(update_pii_fields, names="value")
        update_pii_fields()
        refresh_sensitive_rule_preview()

        def column_changed(change: dict[str, Any]) -> None:
            if refreshing_column_options["active"]:
                return
            old = str(change.get("old") or "")
            if old:
                snapshot = column_editor_snapshot()
                if snapshot != hydrated_column_snapshots.get(old, snapshot):
                    unsaved_columns[old] = snapshot
                    set_status("Column edits were retained in the current draft session.")
                else:
                    unsaved_columns.pop(old, None)
            if change.get("new"):
                selected_id = str(change["new"])
                hydrate_column(selected_id)
            render_column_ai(str(change.get("new") or ""))
            if str(top_nav.value) == "Columns":
                refresh_column_view = state.get("_refresh_column_view")
                if callable(refresh_column_view):
                    refresh_column_view()
                load_selected_profile()

        column_select.observe(column_changed, names="value")

        def _suggestion_html(
            label: str, suggestion: dict[str, Any] | None, *, show_heading: bool = True
        ) -> str:
            heading = "<b>AI suggestion</b><br>" if show_heading else ""
            if not suggestion:
                return f"<p>{heading}<span style=\"color:#666\">Select Generate to request a suggestion.</span></p>"
            stale = " · <b>Needs refresh</b>" if suggestion.get("stale") else ""
            error = suggestion.get("error")
            if error:
                return (
                    f"<p>{heading}<span style=\"color:#a4262c\">"
                    f"{html.escape(str(error))}</span></p>"
                )
            value = suggestion.get("value")
            if label == "Sensitive Data":
                value = (
                    "<div style='font-weight:600;margin-bottom:6px;'>"
                    f"{html.escape(str(suggestion.get('pii_label') or ''))}</div>"
                    "<div style='margin-bottom:8px;'>"
                    f"{html.escape(str(suggestion.get('reason') or ''))}</div>"
                    "<div style='color:#475467;'>"
                    f"Treatment: {html.escape(str(suggestion.get('treatment') or 'None'))} · "
                    f"Action: {html.escape(str(suggestion.get('action') or 'None'))}</div>"
                )
            else:
                value = html.escape(str(value or ""))
            stale_text = (
                "<div style='margin:6px 0;color:#8a6d1d;font-weight:600;'>Needs refresh</div>"
                if stale else ""
            )
            return (
                "<div style='line-height:1.55;overflow-wrap:anywhere;'>"
                f"{heading}{stale_text}"
                f"<div style='margin-top:8px;'>{value}</div>"
                "</div>"
            )

        def _column_editable_values(column_id: str) -> tuple[str, str]:
            if str(column_select.value or "") == column_id:
                return str(column_description.value or ""), str(column_classification.value or "")
            live_enrichments, _live_guardrails = current_rows()
            pending = unsaved_columns.get(column_id, {})
            return (
                str(pending.get("description", enrichment_value(
                    live_enrichments, "column", "Description", column_id
                )) or ""),
                str(pending.get("classification", enrichment_value(
                    live_enrichments, "column", "Classification", column_id
                )) or ""),
            )

        def _effective_table_ai_description() -> str:
            """Return the freshest table Description context for dependent AI suggestions."""
            suggestion = ai_state["table"].get("description", {})
            if suggestion and not suggestion.get("error") and not suggestion.get("stale"):
                return str(suggestion.get("value") or table_description.value or "")
            return str(table_description.value or "")

        def render_column_ai(column_id: str) -> None:
            suggestions = ai_state["columns"].get(column_id, {})
            if state["_ai_unavailable"]:
                column_description_ai.value = f"<p>{state['_ai_unavailable']}</p>"
                sensitive_ai.value = f"<p>{state['_ai_unavailable']}</p>"
            elif not ai_enrichment.get("enabled"):
                column_description_ai.value = "<p>Disabled in 00_env_config.</p>"
                sensitive_ai.value = "<p><b>AI suggestion</b><br>Disabled in 00_env_config.</p>"
            elif not editable:
                column_description_ai.value = "<p>Not run for review-only versions.</p>"
                sensitive_ai.value = "<p><b>AI suggestion</b><br>Not run for review-only versions.</p>"
            else:
                column_description_ai.value = _suggestion_html(
                    "Description", suggestions.get("description"), show_heading=False
                )
                sensitive_ai.value = _suggestion_html(
                    "Sensitive Data", suggestions.get("sensitive_data")
                )
            available = (
                editable and ai_available() and bool(column_id)
            )
            accept_column_description.disabled = not (
                available and suggestions.get("description") and not suggestions["description"].get("error")
            )
            accept_sensitive.disabled = not (
                available and suggestions.get("sensitive_data") and not suggestions["sensitive_data"].get("error")
            )
            rerun_column_description.disabled = not available
            rerun_sensitive.disabled = not available
            rerun_column_description.description = "Re-run" if suggestions.get("description") else "Generate"
            rerun_sensitive.description = "Re-run" if suggestions.get("sensitive_data") else "Generate"

        def mark_sensitive_stale(column_id: str) -> None:
            """Mark one column's dependent Sensitive Data advice stale."""
            suggestion = ai_state["columns"].get(column_id, {}).get("sensitive_data")
            if suggestion:
                suggestion["stale"] = True

        def mark_all_sensitive_stale() -> None:
            """Mark all loaded column Sensitive Data suggestions stale."""
            for column_suggestions in ai_state["columns"].values():
                suggestion = column_suggestions.get("sensitive_data")
                if suggestion:
                    suggestion["stale"] = True

        @busy_action("Generating column description…", ai_request=True)
        def run_column_enrichment_ai(column_id: str, *, force: bool = False) -> None:
            if not column_id:
                render_column_ai("")
                return
            suggestions = ai_state["columns"].setdefault(column_id, {})
            if not editable or not ai_available():
                render_column_ai(column_id)
                return
            if not force and suggestions.get("description"):
                render_column_ai(column_id)
                return
            selected = next(
                (column for column in columns if str(column.get("column_id") or "") == column_id), {}
            )
            description, _ = _column_editable_values(column_id)
            error_key = (column_id, "enrichment")
            retrying = error_key in ai_errors
            try:
                profile_value = load_profile_context(column_id)
                result = suggest_enrichment(
                    build_ai_enrichment_context(
                        selected,
                        metadata_level="column",
                        existing_description=description,
                        profile_rows=[dict(profile_value.get("profile") or {})],
                    ),
                    description_prompt=str(ai_enrichment.get("column_description_prompt") or ""),
                    ai_config=ai_enrichment, spark_session=spark, usage=state["ai_usage"],
                    runtime_context=ai_runtime_context(column_id), operation="column_enrichment",
                )
                previous_value = str(suggestions.get("description", {}).get("value") or "")
                new_value = str(result["Description"])
                suggestions["description"] = {"value": new_value, "stale": False}
                if previous_value and new_value != previous_value:
                    mark_sensitive_stale(column_id)
                refresh_ai_usage()
                ai_errors.pop(error_key, None)
                if retrying:
                    ai_recovered(
                        "Column AI suggestion generated after retry.",
                        operation=error_key,
                        remaining_errors=bool(
                            ai_errors or state["_validation_errors"].get("business_rule_ai")
                        ),
                    )
            except (TypeError, ValueError, RuntimeError, ImportError) as exc:
                refresh_ai_usage()
                message = ai_failure_message(exc, error_key)
                suggestions["description"] = {"error": message, "stale": False}
                ai_errors[error_key] = message
                set_status(f"AI suggestions unavailable for this column: {message}", warning=True)
            render_column_ai(column_id)

        @busy_action("Assessing sensitive data…", ai_request=True)
        def run_sensitive_ai(
            column_id: str, *, force: bool = False
        ) -> None:
            if not column_id:
                render_column_ai("")
                return
            suggestions = ai_state["columns"].setdefault(column_id, {})
            if not editable or not ai_available():
                render_column_ai(column_id)
                return
            if not force and suggestions.get("sensitive_data"):
                render_column_ai(column_id)
                return
            selected = next(
                (column for column in columns if str(column.get("column_id") or "") == column_id), {}
            )
            description, classification = _column_editable_values(column_id)
            error_key = (column_id, "sensitive_data")
            retrying = error_key in ai_errors
            try:
                profile_value = load_profile_context(column_id)
                profile = dict(profile_value.get("profile") or {})
                context_value = build_ai_sensitive_data_context({
                    "table_id": state.get("dataset_id"),
                    "table_name": table.get("table_name"),
                    "schema_name": table.get("schema_name"),
                    "layer": table.get("layer"),
                    "contract_id": current.get("contract_id"),
                    "contract_version": current.get("contract_version"),
                    "table_description": str(table_description.value or ""),
                    "table_classification": table_classification.value,
                    "catalogue_profile_rows": [{
                        **dict(selected), "description": description,
                        "classification": classification,
                        **{name: profile.get(name) for name in (
                            "profile_scope", "profiling_max_rows",
                            "row_count", "non_null_count", "null_count", "null_percent",
                            "distinct_count", "distinct_percent", "min_value", "max_value",
                            "mean_value", "stddev_value", "percentile_25_value", "median_value", "percentile_75_value",
                        ) if profile.get(name) is not None},
                        "frequency_evidence": [
                            {name: item[name] for name in ("value", "count", "percent") if name in item}
                            for item in profile_value.get("values", [])
                        ],
                    }],
                })
                result = suggest_sensitive_data(
                    context_value, prompt=str(ai_enrichment.get("sensitive_data_prompt") or ""),
                    ai_config=ai_enrichment, spark_session=spark, usage=state["ai_usage"],
                    runtime_context=ai_runtime_context(column_id), operation="sensitive_data",
                )
                if len(result) != 1:
                    selected_name = str(selected.get("column_name") or column_id)
                    raise ValueError(
                        f"No Sensitive Data assessment matched {selected_name!r}."
                    )
                suggestions["sensitive_data"] = {**result[0], "stale": False}
                refresh_ai_usage()
                ai_errors.pop(error_key, None)
                if retrying:
                    ai_recovered(
                        "Sensitive Data AI suggestion generated after retry.",
                        operation=error_key,
                        remaining_errors=bool(
                            ai_errors or state["_validation_errors"].get("business_rule_ai")
                        ),
                    )
            except (TypeError, ValueError, RuntimeError, ImportError) as exc:
                refresh_ai_usage()
                message = ai_failure_message(exc, error_key)
                suggestions["sensitive_data"] = {"error": message, "stale": False}
                ai_errors[error_key] = message
                selected_name = str(selected.get("column_name") or column_id)
                set_status(
                    f"Sensitive Data AI suggestion skipped for {selected_name}: {message}",
                    warning=True,
                )
            render_column_ai(column_id)

        def accept_description_clicked(_button: Any) -> None:
            suggestion = ai_state["columns"].get(str(column_select.value or ""), {}).get("description", {})
            if not suggestion.get("error"):
                column_description.value = str(suggestion.get("value") or "")

        def accept_sensitive_clicked(_button: Any) -> None:
            suggestion = ai_state["columns"].get(str(column_select.value or ""), {}).get("sensitive_data", {})
            if not suggestion or suggestion.get("error"):
                return
            allowed = contracts.sensitive_data_treatments_for_type(str(datatype_choice.value or ""))
            treatment = str(suggestion.get("treatment") or sensitive_treatment.value or allowed[0])
            parameters = suggestion.get("parameters", {})
            try:
                if suggestion["pii_type"] != "none":
                    if treatment not in allowed:
                        raise ValueError("This treatment does not apply to the column datatype. Use Bucket for numeric values, Mask for text/categories, or Tokenize/Remove for supported scalar values.")
                    parameters = contracts.validate_sensitive_data_parameters({"scope": "column", "treatment": treatment, **parameters})
            except (TypeError, ValueError) as exc:
                set_status(str(exc), error=True)
                return
            previous_treatment = sensitive_treatment.value
            hydrating["active"] = True
            try:
                pii_type.value = str(suggestion["pii_type"])
                pii_reason.value = str(suggestion["reason"])
                sensitive_enabled.value = suggestion["pii_type"] != "none"
                sensitive_treatment.value = treatment
                mask_start.value = str(parameters.get("preserve_start", 0))
                mask_end.value = str(parameters.get("preserve_end", 0))
                mask_character.value = str(parameters.get("mask_character", "*"))
                mask_mode.value = "partial" if int(mask_start.value) or int(mask_end.value) else "full"
                bucket_mode.value = "width" if "bin_width" in parameters else "ranges"
                bucket_width.value = str(parameters.get("bin_width", 10))
                bucket_origin.value = str(parameters.get("bin_origin", 0))
                bucket_bins.value = ", ".join(map(str, parameters.get("bins", [])))
                bucket_labels.value = ", ".join(map(str, parameters.get("labels", [])))
            finally:
                hydrating["active"] = False
            update_sensitive_fields({"owner": sensitive_treatment, "old": previous_treatment})
            sync_sensitive()
            refresh_sensitive_rule_preview()

        accept_column_description.on_click(accept_description_clicked)
        accept_sensitive.on_click(accept_sensitive_clicked)
        rerun_column_description.on_click(
            lambda _button: run_column_enrichment_ai(str(column_select.value or ""), force=True)
        )
        rerun_sensitive.on_click(
            lambda _button: run_sensitive_ai(str(column_select.value or ""), force=True)
        )

        def description_changed(change: dict[str, Any]) -> None:
            if hydrating["active"]:
                return
            column_id = str(column_select.value or "")
            suggestions = ai_state["columns"].get(column_id, {})
            description_suggestion = suggestions.get("description")
            new_value = str(change.get("new") or "")
            if (
                description_suggestion
                and not description_suggestion.get("error")
                and new_value == str(description_suggestion.get("value") or "")
            ):
                render_column_ai(column_id)
                return
            if description_suggestion:
                description_suggestion["stale"] = True
            mark_sensitive_stale(column_id)
            render_column_ai(column_id)

        def classification_changed(_change: dict[str, Any]) -> None:
            if hydrating["active"]:
                return
            column_id = str(column_select.value or "")
            mark_sensitive_stale(column_id)
            render_column_ai(column_id)

        def table_description_changed(change: dict[str, Any]) -> None:
            suggestion = ai_state["table"].get("description")
            new_value = str(change.get("new") or "")
            if (
                suggestion
                and not suggestion.get("error")
                and new_value == str(suggestion.get("value") or "")
            ):
                return
            if suggestion:
                suggestion["stale"] = True
            mark_all_sensitive_stale()
            render_table_ai()
            selected_id = str(column_select.value or "")
            if selected_id:
                render_column_ai(selected_id)

        def table_classification_changed(_change: dict[str, Any]) -> None:
            mark_all_sensitive_stale()
            selected_id = str(column_select.value or "")
            if selected_id:
                render_column_ai(selected_id)

        column_description.observe(description_changed, names="value")
        column_classification.observe(classification_changed, names="value")
        table_description.observe(table_description_changed, names="value")
        table_classification.observe(table_classification_changed, names="value")

        def mark_column_hydrated(*keys: str) -> None:
            cid = str(column_select.value or "")
            if not cid:
                return
            current_snapshot = column_editor_snapshot()
            baseline = hydrated_column_snapshots.setdefault(cid, dict(current_snapshot))
            for key in keys:
                baseline[key] = current_snapshot[key]
            if baseline == current_snapshot:
                unsaved_columns.pop(cid, None)
            else:
                unsaved_columns[cid] = current_snapshot

        def sync_column_enrichment(_change: dict[str, Any] | None = None) -> None:
            if hydrating["active"] or not editable:
                return
            cid = str(column_select.value or "")
            if not cid:
                return
            key = f"column.{cid}.enrichment"
            try:
                stage_enrichment([
                    enrichment_record("column", "Description", column_description.value, cid),
                    enrichment_record("column", "Classification", column_classification.value, cid),
                ])
                refresh_table_classification()
                set_validation_error(key)
                mark_column_hydrated("description", "classification")
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error(key, exc)

        def build_required_record() -> dict[str, Any]:
            payload = json.loads(str(current["contract"]["contract_payload_json"]))
            required_ids = [str(column["column_id"]) for column in payload.get("table", {}).get("columns", [])
                            if column.get("presence", "required") == "required"]
            current_rule = next((rule for rule in session_guardrails() if rule.get("guardrail_type") == "schema"), {})
            return guardrail_record("schema", "strict", {"required_columns": required_ids}, existing=current_rule, action="Block")

        def sync_required(_change: dict[str, Any] | None = None) -> None:
            if hydrating["active"] or not editable:
                return
            cid = str(column_select.value or "")
            payload = json.loads(str(current["contract"]["contract_payload_json"]))
            for column in payload.get("table", {}).get("columns", []):
                if str(column.get("column_id") or "") == cid:
                    column["presence"] = "required" if required.value else "optional"
            current["contract"]["contract_payload_json"] = json.dumps(payload, sort_keys=True)
            for column in current.get("available_columns", []):
                if str(column.get("column_id") or "") == cid:
                    column["presence"] = "required" if required.value else "optional"
            stage_guardrails([build_required_record()])
            state["dirty"] = True
            refresh_manifest()
            mark_column_hydrated("required")

        def build_sensitive_record() -> dict[str, Any] | None:
            cid = str(column_select.value or "")
            existing = next((
                r for r in session_guardrails()
                if str(r.get("guardrail_type") or "").lower() == "sensitive_data"
                and str(r.get("column_id") or "") == cid
            ), {})
            if (
                not existing
                and not sensitive_enabled.value
                and str(pii_type.value or "none") == "none"
            ):
                return None
            if str(pii_type.value or "none") == "none" and sensitive_enabled.value:
                raise ValueError("Enable a Sensitive Data rule only for Direct or Indirect PII.")
            if sensitive_enabled.value and sensitive_treatment.value not in contracts.sensitive_data_treatments_for_type(str(datatype_choice.value or "")):
                raise ValueError("Select a treatment supported by this datatype: Bucket for numeric values, Mask for text/categories, or Tokenize/Remove.")
            parameters: dict[str, Any] = {
                "scope": "column", "treatment": sensitive_treatment.value,
            }
            if str(pii_type.value or "none") != "none":
                if not str(pii_reason.value or "").strip():
                    raise ValueError("Explain why this column is Direct or Indirect PII.")
                parameters.update({
                    "pii_type": str(pii_type.value),
                    "pii_reason": str(pii_reason.value or "").strip(),
                })
            if sensitive_treatment.value == "mask":
                parameters.update({
                    "preserve_start": int(mask_start.value),
                    "preserve_end": int(mask_end.value),
                    "mask_character": mask_character.value,
                })
            elif sensitive_treatment.value == "bucket" and bucket_mode.value == "width":
                parameters.update({"bin_width": float(bucket_width.value), "bin_origin": float(bucket_origin.value)})
            elif sensitive_treatment.value == "bucket":
                parameters.update({
                    "bins": [
                        float(value.strip()) for value in bucket_bins.value.split(",")
                        if value.strip()
                    ],
                    "labels": [
                        value.strip() for value in bucket_labels.value.split(",")
                        if value.strip()
                    ],
                })
            return guardrail_record(
                "sensitive_data", str(sensitive_treatment.value), parameters, column_id=cid,
                action="Block",
                existing=existing, active=sensitive_enabled.value,
            )

        def sync_sensitive(_change: dict[str, Any] | None = None) -> None:
            if hydrating["active"] or not editable or removal_state["pending"]:
                return
            cid = str(column_select.value or "")
            if not cid:
                return
            key = f"column.{cid}.sensitive"
            try:
                record = build_sensitive_record()
                if record is not None:
                    stage_guardrails([record])
                refresh_table_classification()
                set_validation_error(key)
                mark_column_hydrated(
                    "sensitive_enabled", "pii_type", "pii_reason", "sensitive_treatment",
                    "mask_start", "mask_end", "mask_character",
                    "bucket_bins", "bucket_labels", "mask_mode", "bucket_mode", "bucket_width", "bucket_origin",
                )
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error(key, exc)
            finally:
                render_table_summary()

        def sync_dq_family(kind: str) -> None:
            if hydrating["active"] or not editable:
                return
            cid = str(column_select.value or "")
            if not cid:
                return
            controls = dq_family_controls[kind]
            key = f"column.{cid}.dq.{kind}"
            try:
                selected = selected_column()
                matching_rules = [
                    r for r in session_guardrails()
                    if str(r.get("guardrail_type") or "").lower() in {"data_quality", "dq"}
                    and str(r.get("column_id") or "") == cid
                    and str(r.get("rule_type") or "") == kind
                ]
                if kind == "value_set":
                    column_name = str(selected.get("column_name") or cid)
                    values_by_mode = {
                        "allow": [
                            item.strip() for item in dq_whitelist_values.value.split(",")
                            if item.strip()
                        ],
                        "block": [
                            item.strip() for item in dq_blacklist_values.value.split(",")
                            if item.strip()
                        ],
                    }
                    existing_by_mode = {
                        str(_parameters(rule).get("mode") or "").lower(): rule
                        for rule in matching_rules
                    }
                    if controls["enabled"].value and not any(values_by_mode.values()):
                        raise ValueError(
                            "Whitelist or Blacklist requires at least one comma-separated value."
                        )
                    records = []
                    for mode, values in values_by_mode.items():
                        existing = existing_by_mode.get(mode, {})
                        if not values and not existing:
                            continue
                        params = (
                            {"columns": [column_name], "mode": mode, "values": values}
                            if values
                            else _parameters(existing)
                        )
                        if mode == "allow":
                            tolerance = float(dq_whitelist_max_failure.value)
                            if not 0 <= tolerance <= 100:
                                raise ValueError("Whitelist maximum failure % must be between 0 and 100.")
                            params["maximum_failure_percent"] = tolerance
                        records.append(guardrail_record(
                            "data_quality",
                            "value_set",
                            params,
                            column_id=cid,
                            action="Block" if controls["block"].value else "Warn",
                            existing=existing,
                            active=bool(controls["enabled"].value and values),
                        ))
                    if records:
                        stage_guardrails(records)
                    set_validation_error(key)
                    mark_column_hydrated("dq")
                    refresh_dq_value_counts()
                    return
                existing = matching_rules[0] if matching_rules else {}
                if not existing and not controls["enabled"].value:
                    set_validation_error(key)
                    mark_column_hydrated("dq")
                    return
                params: dict[str, Any] = {"columns": [str(selected.get("column_name") or cid)]}
                if kind == "completeness":
                    threshold = float(dq_completeness_failure.value)
                    if not 0 <= threshold <= 100:
                        raise ValueError("Accepted failure rate % must be between 0 and 100.")
                    params.update({
                        "maximum_missing_percent": threshold,
                        "treat_blank_as_missing": bool(dq_blank_missing.value),
                    })
                elif kind == "uniqueness":
                    if not dq_uniqueness_failure.value.strip():
                        raise ValueError("Set Accepted failure rate % explicitly: a legacy distinct-key limit cannot be converted exactly.")
                    threshold = float(dq_uniqueness_failure.value)
                    if not 0 <= threshold <= 100:
                        raise ValueError("Accepted failure rate % must be between 0 and 100.")
                    params["maximum_failure_percent"] = threshold
                elif kind == "range":
                    tolerance = float(dq_range_max_failure.value)
                    if not 0 <= tolerance <= 100:
                        raise ValueError("Accepted failure rate % must be between 0 and 100.")
                    params["maximum_failure_percent"] = tolerance
                    if not dq_minimum.value.strip() and not dq_maximum.value.strip():
                        raise ValueError("range requires a minimum or maximum.")
                    params.update({
                        "minimum": dq_minimum.value.strip() or None,
                        "minimum_inclusive": bool(dq_minimum_inclusive.value),
                        "maximum": dq_maximum.value.strip() or None,
                        "maximum_inclusive": bool(dq_maximum_inclusive.value),
                    })
                stage_guardrails([guardrail_record(
                    "data_quality", kind, params, column_id=cid,
                    action="Block" if controls["block"].value else "Warn",
                    existing=existing, active=controls["enabled"].value,
                )])
                set_validation_error(key)
                mark_column_hydrated("dq")
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error(key, exc)

        for control in (column_description, column_classification):
            control.observe(sync_column_enrichment, names="value")
        required.observe(sync_required, names="value")
        for control in (
            sensitive_enabled, pii_type, pii_reason, sensitive_treatment,
            mask_start, mask_end, mask_character, bucket_bins, bucket_labels, bucket_mode, bucket_width, bucket_origin,
        ):
            control.observe(sync_sensitive, names="value")
        for kind, controls in dq_family_controls.items():
            for control in (
                controls["enabled"], controls["block"], *controls["parameters"]
            ):
                control.observe(
                    lambda _change, family=kind: sync_dq_family(family),
                    names="value",
                )

        def rebuild_column_options() -> None:
            nonlocal column_options
            column_options = [
                (
                    f"{str(column.get('column_name') or '')}{' *' if str(column.get('column_id') or '') in required_columns or str(column.get('column_name') or '') in required_columns else ''}",
                    str(column.get("column_id") or ""),
                )
                for column in authoring_columns
            ]

        def refresh_column_options(*_args: Any) -> None:
            rebuild_column_options()
            query = str(column_search.value or "").strip().casefold()
            current_value = str(column_select.value or "")
            filtered = [
                option for option in column_options
                if not query or query in str(option[0]).casefold()
            ]
            required_option_rules = "".join(f".fabricops-contract-columns option:nth-child({index}){{color:var(--form-accent);font-weight:600;}}" for index, (label, _value) in enumerate(filtered, start=1) if str(label).endswith(" *"))
            column_option_style.value = "<style>.fabricops-contract-columns option:checked{font-weight:600;}" + required_option_rules + ".fabricops-form .fabricops-column-required{display:flex!important;grid-template-columns:none!important;width:auto!important;max-width:none!important;align-items:center!important;margin:0!important;}.fabricops-form .fabricops-column-required>.widget-label{width:auto!important;min-width:0!important;max-width:none!important;margin:0!important;}</style>"
            values = [str(value) for _label, value in filtered]
            selected_value = current_value if current_value in values else values[0] if values else None
            refreshing_column_options["active"] = True
            try:
                if tuple(column_select.options) != tuple(filtered):
                    column_select.options = filtered
                column_select.value = selected_value
            finally:
                refreshing_column_options["active"] = False
            if str(selected_value or "") != current_value:
                column_changed({"old": current_value, "new": selected_value})

        def required_feedback(change: dict[str, Any]) -> None:
            if hydrating["active"]:
                return
            cid = str(column_select.value or "")
            selected = selected_column()
            name = str(selected.get("column_name") or "")
            if bool(change.get("new")):
                required_columns.add(cid)
            else:
                required_columns.discard(cid)
                required_columns.discard(name)
            refresh_column_options()
            render_table_summary()

        def datatype_feedback(change: dict[str, Any]) -> None:
            if hydrating["active"] or not change.get("new"):
                return
            cid = str(column_select.value or "")
            contracted_types[cid] = str(change["new"])
            payload = json.loads(str(current["contract"].get("contract_payload_json") or "{}"))
            for item in payload.get("table", {}).get("columns", []):
                if str(item.get("column_id") or "") == cid:
                    item["data_type"] = contracted_types[cid]
                    break
            current["contract"]["contract_payload_json"] = json.dumps(
                payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            )
            state["dirty"] = True
            refresh_manifest()
            refresh_column_options()
            hydrate_column(cid)
            if str(top_nav.value) == "Columns":
                load_selected_profile()
            set_status("Contract datatype choice staged locally. Save the Data Contract to persist.")

        required.observe(required_feedback, names="value")
        datatype_choice.observe(datatype_feedback, names="value")
        column_search.observe(refresh_column_options, names="value")
        rebuild_column_options()
        refresh_column_options()

        column_left = (
            widgets.HTML(
                "<div style='color:var(--form-accent);font-size:11px;font-weight:800;"
                "'>Columns</div>"
                "<div style='color:#667085;font-size:12px;line-height:1.45;margin-top:4px;'>"
                "Select a column to review its details and rules.</div>"
            ),
            column_search,
            column_option_style,
            column_select,
        )
        def dq_option_row(field: Any, option: Any) -> Any:
            """Align an option checkbox with the field it modifies."""
            return widgets.VBox(
                [field, option],
                layout=widgets.Layout(
                    width="100%",
                    min_width="0",
                    max_width="100%",
                    gap="8px",
                    align_items="stretch",
                    overflow="visible",
                ),
            )

        dq_family_controls["completeness"]["display"] = (
            dq_option_row(dq_completeness_failure, dq_blank_missing),
        )
        dq_family_controls["value_set"]["display"] = (
            widgets.VBox(
                [dq_whitelist_values, dq_whitelist_count, dq_whitelist_max_failure],
                layout=widgets.Layout(width="100%", min_width="0", gap="2px"),
            ),
            widgets.VBox(
                [dq_blacklist_values, dq_blacklist_count, widgets.HTML(
                    "<small>Prohibited values are strict; no percentage tolerance applies.</small>"
                )],
                layout=widgets.Layout(width="100%", min_width="0", gap="2px"),
            ),
        )
        dq_family_controls["range"]["display"] = (
            dq_option_row(dq_minimum, dq_minimum_inclusive),
            dq_option_row(dq_maximum, dq_maximum_inclusive),
            dq_range_max_failure,
        )

        def dq_family_section(
            title: str, kind: str, description: str
        ) -> Any:
            controls = dq_family_controls[kind]
            primary = widgets.VBox(
                [
                    widgets.HTML(
                        f"<div style='font-size:13px;color:#667085;line-height:1.5;'>"
                        f"{html.escape(description)}</div>"
                    ),
                    *controls.get("display", controls["parameters"]),
                ],
                layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
            )
            children = [
                widgets.HTML(f"<h4 style='margin:0;'>{html.escape(title)}</h4>"),
                widgets.HBox(
                    [controls["enabled"], controls["block"]],
                    layout=widgets.Layout(
                        width="auto",
                        min_width="0",
                        gap="18px",
                        align_items="center",
                        justify_content="flex-start",
                        overflow="visible",
                    ),
                ),
                primary,
            ]
            children[1].add_class("fabricops-contract-options")
            return widgets.VBox(
                children,
                layout=widgets.Layout(
                    width="100%",
                    min_width="0",
                    max_width="760px",
                    gap="6px",
                    padding="14px 0",
                    border_bottom="1px solid #e1e6eb",
                    overflow="visible",
                ),
            )

        value_list_section = dq_family_section(
            "Value Lists", "value_set",
            "Use a whitelist for accepted values and a blacklist for rejected values. "
            "Each non-empty list is stored as its own deterministic rule.",
        )
        value_range_section = dq_family_section(
            "Value Rules", "range",
            "Set deterministic lower and upper bounds for numeric or date values.",
        )

        def refresh_dq_type_visibility(data_type: str) -> None:
            """Show only DQ families applicable to the active column's datatype."""
            normalized = str(data_type or "").strip().lower()
            base_type = normalized.split("(", 1)[0].strip()
            numeric = base_type in {
                "byte", "tinyint", "short", "smallint", "int", "integer", "long",
                "bigint", "float", "double", "decimal", "numeric",
            }
            selected_treatment = sensitive_treatment.value
            allowed = contracts.sensitive_data_treatments_for_type(data_type)
            options = tuple(option for option in _SENSITIVE_TREATMENT_OPTIONS if option[1] in allowed)
            was_hydrating = hydrating["active"]
            hydrating["active"] = True
            try:
                sensitive_treatment.options = tuple(options)
                sensitive_treatment.value = selected_treatment if selected_treatment in allowed else None
            finally:
                hydrating["active"] = was_hydrating
            if editable and sensitive_enabled.value and sensitive_treatment.value is None:
                set_validation_error(f"column.{column_select.value}.sensitive", "The saved treatment does not apply to this datatype. Select a supported treatment before saving.")
            update_sensitive_fields()
            temporal = base_type in {"date", "timestamp", "timestamp_ntz"}
            boolean = base_type in {"bool", "boolean"}
            scalar = base_type in {"string", "varchar", "char"} or numeric or temporal or boolean
            value_list_section.layout.display = "" if scalar else "none"
            value_range_section.layout.display = "" if numeric or temporal else "none"
            if boolean:
                dq_whitelist_values.placeholder = "Example: true, false"
                dq_blacklist_values.placeholder = "Example: false"
            elif temporal:
                example = "2026-01-01" if base_type == "date" else "2026-01-01 09:00:00"
                dq_whitelist_values.placeholder = f"Example: {example}"
                dq_blacklist_values.placeholder = f"Example: {example}"
            elif numeric:
                dq_whitelist_values.placeholder = "Example: 10, 20, 30"
                dq_blacklist_values.placeholder = "Example: -1, 0"
            else:
                dq_whitelist_values.placeholder = "Example: Active, Inactive"
                dq_blacklist_values.placeholder = "Example: Unknown, N/A"
            example_bound = (
                "2026-01-01" if base_type == "date"
                else "2026-01-01 09:00:00" if temporal
                else "0" if numeric else ""
            )
            dq_minimum.placeholder = example_bound
            dq_maximum.placeholder = example_bound

        dq_visibility["refresh"] = refresh_dq_type_visibility

        dq_primary = widgets.VBox(
            [
                dq_family_section(
                    "Completeness", "completeness",
                    "Limit missing values, with explicit blank-text handling.",
                ),
                dq_family_section(
                    "Uniqueness", "uniqueness",
                    "Distinct key values divided by total rows. Use 100% for strict DQ uniqueness; Grain & Row Key stays separate.",
                ),
                value_list_section,
                value_range_section,
            ],
            layout=widgets.Layout(width="100%", min_width="0", gap="0"),
        )
        dq_panel = guardrail_section(
            "Column data quality",
            banner_title="Applies when this governed column is validated or enforced in a pipeline.",
            banner_detail=(
                "FabricOps evaluates active deterministic Data Quality rules before a governed "
                "write is allowed to continue."
            ),
            description=(
                "Configure each deterministic rule directly."
            ),
            primary_children=[dq_primary],
        )
        column_definition = shared.form_section(
            widgets,
            title="Column definition",
            children=[
                widgets.GridBox(
                    [
                        widgets.HTML("<b>Description</b>"),
                        column_description,
                        *(
                            [
                                widgets.VBox(
                                    [
                                        column_description_ai,
                                        shared.action_row(
                                            widgets,
                                            [accept_column_description, rerun_column_description],
                                        ),
                                    ],
                                    layout=widgets.Layout(
                                        width="100%", min_width="0", gap="4px"
                                    ),
                                )
                            ]
                            if ai_visible else []
                        ),
                    ],
                    layout=widgets.Layout(
                        width="100%",
                        grid_template_columns=(
                            "120px minmax(240px, 1fr) minmax(240px, 1fr)"
                            if ai_visible else "120px minmax(240px, 1fr)"
                        ),
                        grid_gap="10px 16px",
                        align_items="flex-start",
                    ),
                )
            ],
        )
        column_definition.children[1].add_class("fabricops-contract-labeled-grid")
        sensitive_primary = widgets.VBox(
            [
                pii_type,
                sensitive_treatment,
                treatment_help,
                removal_confirmation_box,
                column_classification,
                mask_mode,
                mask_start,
                mask_end,
                bucket_mode,
                bucket_width,
                bucket_origin,
                bucket_bins,
                bucket_labels,
                pii_reason,
                sensitive_rule_preview,
            ],
            layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
        )
        sensitive_ai_panel = widgets.VBox(
            [sensitive_ai, sensitive_ai_actions],
            layout=widgets.Layout(
                width="100%", min_width="0", gap="8px",
                padding="0 0 0 16px",
                border_left="1px solid #e1e6eb",
            ),
        )
        column_right = (
            column_header,
            column_definition,
            shared.form_section(
                widgets,
                title="Profile evidence",
                children=[profile_context],
            ),
            guardrail_section(
                "Sensitive Data",
                banner_title="Applies before this governed table is written.",
                banner_detail=(
                    "Treatment runs before Data Quality and publication. Every treatment failure stops the write."
                ),
                description=(
                    "Assess whether this column contains PII, choose how the pipeline should treat "
                    "the sensitive value, and set the classification of the resulting output column."
                ),
                header_controls=[
                    sensitive_enabled,
                ],
                primary_children=[
                    sensitive_primary,
                ],
                ai_children=list(sensitive_ai_panel.children),
            ),
        )
        view_content["Columns"] = (column_left, column_right)

        def refresh_column_view() -> None:
            if str(top_nav.value) == "Columns":
                right.children = (section_heading, *column_left, *(column_right if column_select.value else (empty_column,)))
        state["_refresh_column_view"] = refresh_column_view

        render_table_ai()
        if column_options:
            _set_selection_value(
                column_select,
                column_options[0][1],
                control_name="column_select",
                table_name=str(table.get("table_name") or ""),
            )
            hydrate_column(str(column_select.value))
            render_column_ai(str(column_select.value))

        # Data Quality: manage the shared rule set manually or with optional AI assistance.
        new_rule_option = "__new_rule__"
        managed_grain_option = "__managed_grain__"
        business_saved = widgets.Select(
            rows=7,
            **shared.widget_common(widgets, "Rules")
        )
        business_editor_heading = widgets.HTML(
            "<div class='fabricops-dq-editor-heading'>Rule editor</div>"
        )
        business_requirement = widgets.Textarea(continuous_update=False,
            disabled=not editable,
            placeholder=(
                "Example: Approved orders require an approved date, "
                "total amount must be positive, and status must be Approved, Rejected, or Pending."
            ),
            **shared.widget_common(widgets, "Business requirement", textarea=True),
        )
        business_requirement.description = ""
        business_columns = widgets.SelectMultiple(
            rows=5, options=[
                (str(column.get("column_name") or ""), str(column.get("column_name") or ""))
                for column in authoring_columns
            ],
            disabled=not editable,
            **shared.widget_common(widgets, "Limit to columns (optional)"),
        )
        business_columns.description = ""
        business_columns.add_class("fabricops-contract-list")
        dq_column_options = [
            (str(column.get("column_name") or ""), str(column.get("column_name") or ""))
            for column in authoring_columns
        ]
        dq_column_options_with_blank = [("Select a column", ""), *dq_column_options]
        business_enabled = widgets.Checkbox(
            value=True, description="Enabled", disabled=not editable
        )
        business_block = widgets.ToggleButtons(
            options=[("Warn", False), ("Block", True)], value=False, description="On failure", disabled=not editable
        )
        business_tolerance = widgets.Text(continuous_update=False,
            value="0", disabled=not editable, **shared.widget_common(widgets, "Accepted failure rate %"),
        )
        business_tolerance_hint = widgets.HTML()
        business_parameters = widgets.Textarea(continuous_update=False,
            disabled=not editable,
            **shared.widget_common(widgets, "Rule parameters (JSON)", textarea=True),
        )
        business_parameters.layout.close()
        business_parameters.layout = widgets.Layout(
            width="100%", min_width="0", height="150px"
        )
        review_column = widgets.Dropdown(
            options=dq_column_options_with_blank,
            disabled=not editable,
            **shared.widget_common(widgets, "Column"),
        )
        review_key_columns = widgets.SelectMultiple(
            rows=5, options=dq_column_options,
            disabled=not editable,
            **shared.widget_common(widgets, "Key columns"),
        )
        review_key_columns.add_class("fabricops-contract-list")
        review_key_columns.layout.close()
        review_key_columns.layout = widgets.Layout(width="100%", height="auto")
        review_left_column = widgets.Dropdown(
            options=dq_column_options_with_blank, disabled=not editable,
            **shared.widget_common(widgets, "Left column"),
        )
        review_right_column = widgets.Dropdown(
            options=dq_column_options_with_blank, disabled=not editable,
            **shared.widget_common(widgets, "Right column"),
        )
        review_condition_column = widgets.Dropdown(
            options=dq_column_options_with_blank, disabled=not editable,
            **shared.widget_common(widgets, "Condition column"),
        )
        review_target_column = widgets.Dropdown(
            options=dq_column_options_with_blank, disabled=not editable,
            **shared.widget_common(widgets, "Target column"),
        )
        review_mode = widgets.Dropdown(
            options=(("Allow listed values", "allow"), ("Block listed values", "block")),
            disabled=not editable,
            **shared.widget_common(widgets, "Value behavior"),
        )
        review_values = widgets.Text(continuous_update=False,
            disabled=not editable, placeholder="Comma-separated values",
            **shared.widget_common(widgets, "Values"),
        )
        review_minimum = widgets.Text(continuous_update=False,
            disabled=not editable, **shared.widget_common(widgets, "Lower bound")
        )
        review_maximum = widgets.Text(continuous_update=False,
            disabled=not editable, **shared.widget_common(widgets, "Upper bound")
        )
        review_minimum_inclusive = dq_checkbox("Include lower bound")
        review_maximum_inclusive = dq_checkbox("Include upper bound")
        review_pattern = widgets.Text(continuous_update=False,
            disabled=not editable,
            **shared.widget_common(widgets, "Regular expression"),
        )
        review_operator = widgets.Dropdown(
            options=("=", "!=", ">", ">=", "<", "<="), disabled=not editable,
            **shared.widget_common(widgets, "Comparison"),
        )
        review_condition_operator = widgets.Dropdown(
            options=("=", "!="), disabled=not editable,
            **shared.widget_common(widgets, "Condition"),
        )
        review_condition_value = widgets.Text(continuous_update=False,
            disabled=not editable, **shared.widget_common(widgets, "Condition value")
        )
        review_blank_missing = dq_checkbox("Count blank text as missing")
        review_expression = widgets.Textarea(continuous_update=False,
            disabled=not editable,
            **shared.widget_common(widgets, "PySpark boolean expression", textarea=True),
        )
        review_expression.layout.close()
        review_expression.layout = widgets.Layout(width="100%", height="110px")
        review_parameter_box = widgets.VBox(
            layout=widgets.Layout(width="100%", min_width="0")
        )
        review_parameter_box.add_class("fabricops-dq-parameter-box")
        business_parameters.layout.display = "none"
        business_advanced_toggle = widgets.ToggleButton(
            value=False, description="Show advanced parameters",
            disabled=False, layout=widgets.Layout(width="210px"),
        )

        def toggle_business_advanced(change: dict[str, Any]) -> None:
            expanded = bool(change["new"])
            business_parameters.layout.display = "" if expanded else "none"
            business_advanced_toggle.description = (
                "Hide advanced parameters"
                if expanded else "Show advanced parameters"
            )

        business_advanced_toggle.observe(toggle_business_advanced, names="value")
        business_advanced = widgets.VBox(
            [business_advanced_toggle, business_parameters],
            layout=widgets.Layout(width="100%"),
        )
        business_advanced.add_class("fabricops-dq-parameter-box")
        business_rule_controls = widgets.VBox([
            review_parameter_box,
            widgets.HBox([business_enabled, business_block], layout=checkbox_row_layout),
            business_tolerance, business_tolerance_hint, business_advanced,
        ])
        business_validation = widgets.HTML()
        business_rule_controls.layout.display = "none"
        business_proposal_select = widgets.Dropdown(
            options=[("Generated rules will appear here", -1)],
            value=-1,
            **shared.widget_common(widgets, "Resolved DQ Rules"),
        )
        business_saved.add_class("fabricops-business-chooser")
        business_saved.add_class("fabricops-dq-rule-list")
        business_proposal_select.add_class("fabricops-business-chooser")
        business_proposal_select.layout.display = "none"
        business_proposal = widgets.HTML(
            "<p style='color:#667085;'>Describe a requirement on the left. "
            "FabricOps will resolve it into one or more atomic DQ Rules.</p>"
        )
        resolve_business_rule = widgets.Button(
            description="Generate DQ Rules",
            disabled=not (
                editable and ai_available()
            ),
            button_style="primary",
        )
        state["_ai_buttons"].append(resolve_business_rule)
        apply_business_rule = widgets.Button(
            description="Add DQ Rule", disabled=True, button_style="primary"
        )
        delete_business_rule = widgets.Button(
            description="Delete DQ Rule", disabled=True
        )
        delete_business_rule.add_class("fabricops-delete-request")
        confirm_delete_business_rule = widgets.Button(
            description="Confirm delete", disabled=not editable, button_style="danger"
        )
        confirm_delete_business_rule.add_class("fabricops-confirm-danger")
        cancel_delete_business_rule = widgets.Button(
            description="Cancel", disabled=not editable
        )
        delete_business_rule_status = widgets.HTML()
        delete_business_rule_confirm = widgets.VBox(
            [
                delete_business_rule_status,
                shared.action_row(
                    widgets, [confirm_delete_business_rule, cancel_delete_business_rule]
                ),
            ],
            layout=widgets.Layout(
                width="100%", gap="6px", padding="8px 10px",
                border="1px solid #e1e6eb",
            ),
        )
        delete_business_rule_confirm.layout.display = "none"
        engineering_reviewer = widgets.Text(continuous_update=False,
            disabled=not editable,
            placeholder="Engineer name or identifier",
            **shared.widget_common(widgets, "Engineering reviewer"),
        )
        engineering_review_note = widgets.Textarea(continuous_update=False,
            disabled=not editable,
            placeholder="Optional review note",
            **shared.widget_common(widgets, "Review note", textarea=True),
        )
        approve_engineering_review = widgets.Button(
            description="Approve engineering review", disabled=True, button_style="info"
        )
        engineering_review_status = widgets.HTML()
        engineering_review_panel = widgets.VBox(
            [
                engineering_review_status,
                engineering_reviewer,
                engineering_review_note,
                approve_engineering_review,
            ],
            layout=widgets.Layout(
                width="100%", gap="8px", padding="10px 12px",
                border="1px solid #e1e6eb",
            ),
        )
        engineering_review_panel.layout.display = "none"

        business_lookup: dict[str, dict[str, Any]] = {}
        business_resolved: list[dict[str, Any]] = []
        business_hydrating = {"active": False}
        business_active_saved = {"rule_id": ""}

        business_saved.layout.width = "100%"
        business_saved.layout.min_width = "0"
        business_requirement.layout.width = "100%"
        business_requirement.layout.min_width = "0"
        business_requirement.layout.height = "170px"
        business_columns.layout.width = "100%"
        business_columns.layout.min_width = "0"
        business_columns.layout.height = "auto"
        business_columns.layout.max_height = "220px"
        business_proposal_select.layout.width = "100%"
        business_proposal_select.layout.min_width = "0"
        engineering_review_note.layout.height = "80px"

        manual_rule_type = widgets.Dropdown(
            options=(
                ("Completeness", "completeness"),
                ("Uniqueness", "uniqueness"),
                ("Value set", "value_set"),
                ("Range", "range"),
                ("Pattern", "pattern"),
                ("Column relationship", "column_relationship"),
                ("Conditional completeness", "conditional_completeness"),
                ("Conditional values", "conditional_values"),
                ("Custom expression", "custom_expression"),
            ),
            disabled=not editable,
            **shared.widget_common(widgets, "Rule type"),
        )
        manual_apply_mode = widgets.ToggleButtons(
            options=(
                ("Each selected column", "each"),
                ("Columns together", "together"),
            ),
            value="each", description="Apply to", disabled=not editable,
            layout=widgets.Layout(width="100%"),
        )
        manual_batch_columns = widgets.SelectMultiple(
            rows=5, options=dq_column_options,
            disabled=not editable,
            **shared.widget_common(widgets, "Column"),
        )
        manual_batch_columns.add_class("fabricops-contract-list")
        manual_batch_columns.layout.close()
        manual_batch_columns.layout = widgets.Layout(
            width="100%", min_width="0", height="auto", max_height="220px"
        )
        manual_key_columns = widgets.SelectMultiple(
            rows=5, options=dq_column_options,
            disabled=not editable,
            **shared.widget_common(widgets, "Key columns"),
        )
        manual_key_columns.add_class("fabricops-contract-list")
        manual_key_columns.layout.close()
        manual_key_columns.layout = widgets.Layout(
            width="100%", min_width="0", height="auto", max_height="220px"
        )
        manual_left_column = widgets.Dropdown(
            options=dq_column_options_with_blank,
            disabled=not editable,
            **shared.widget_common(widgets, "Left column"),
        )
        manual_right_column = widgets.Dropdown(
            options=dq_column_options_with_blank,
            disabled=not editable,
            **shared.widget_common(widgets, "Right column"),
        )
        manual_condition_column = widgets.Dropdown(
            options=dq_column_options_with_blank,
            disabled=not editable,
            **shared.widget_common(widgets, "Condition column"),
        )
        manual_target_column = widgets.Dropdown(
            options=dq_column_options_with_blank,
            disabled=not editable,
            **shared.widget_common(widgets, "Target column"),
        )
        manual_mode = widgets.Dropdown(
            options=(("Allow listed values", "allow"), ("Block listed values", "block")),
            disabled=not editable,
            **shared.widget_common(widgets, "Value behavior"),
        )
        manual_values = widgets.Text(continuous_update=False,
            disabled=not editable,
            placeholder="Comma-separated values",
            **shared.widget_common(widgets, "Values"),
        )
        manual_minimum = widgets.Text(continuous_update=False,
            disabled=not editable, **shared.widget_common(widgets, "Lower bound")
        )
        manual_maximum = widgets.Text(continuous_update=False,
            disabled=not editable, **shared.widget_common(widgets, "Upper bound")
        )
        manual_minimum_inclusive = dq_checkbox("Include lower bound")
        manual_minimum_inclusive.value = True
        manual_maximum_inclusive = dq_checkbox("Include upper bound")
        manual_maximum_inclusive.value = True
        manual_pattern = widgets.Text(continuous_update=False,
            disabled=not editable,
            placeholder="Example: ^ORD-[0-9]+$",
            **shared.widget_common(widgets, "Regular expression"),
        )
        manual_operator = widgets.Dropdown(
            options=("=", "!=", ">", ">=", "<", "<="),
            disabled=not editable,
            **shared.widget_common(widgets, "Comparison"),
        )
        manual_condition_operator = widgets.Dropdown(
            options=("=", "!="),
            disabled=not editable,
            **shared.widget_common(widgets, "Condition"),
        )
        manual_condition_value = widgets.Text(continuous_update=False,
            disabled=not editable,
            **shared.widget_common(widgets, "Condition value"),
        )
        manual_blank_missing = dq_checkbox("Count blank text as missing")
        manual_expression = widgets.Textarea(continuous_update=False,
            disabled=not editable,
            placeholder='Example: F.col("amount") > 0',
            **shared.widget_common(widgets, "PySpark boolean expression", textarea=True),
        )
        manual_expression.layout.close()
        manual_expression.layout = widgets.Layout(
            width="100%", min_width="0", height="110px"
        )
        manual_tolerance = widgets.Text(continuous_update=False,
            value="0", disabled=not editable,
            **shared.widget_common(widgets, "Accepted failure rate %"),
        )
        manual_enabled = dq_checkbox("Enabled")
        manual_enabled.value = True
        manual_block = widgets.ToggleButtons(
            options=(("Warn", False), ("Block", True)), value=False,
            description="On failure", disabled=not editable,
        )
        add_manual_rule = widgets.Button(
            description="Add DQ Rule", disabled=not editable, button_style="primary"
        )
        manual_rule_hint = widgets.HTML()
        manual_preview = widgets.HTML()
        manual_validation = widgets.HTML()
        manual_parameter_box = widgets.VBox(
            layout=widgets.Layout(width="100%", min_width="0")
        )
        manual_parameter_box.add_class("fabricops-dq-parameter-box")
        manual_batch_rule_types = {
            "completeness", "uniqueness", "value_set", "range", "pattern",
        }

        def refresh_manual_rule_fields(
            _change: dict[str, Any] | None = None,
        ) -> None:
            rule_type = str(manual_rule_type.value or "")
            columns_by_type: dict[str, list[Any]] = {
                **{
                    batch_type: (
                        [manual_apply_mode, manual_batch_columns]
                        if batch_type == "uniqueness"
                        else [manual_batch_columns]
                    )
                    for batch_type in manual_batch_rule_types
                },
                "column_relationship": [manual_left_column, manual_right_column],
                "conditional_completeness": [
                    manual_condition_column, manual_target_column,
                ],
                "conditional_values": [
                    manual_condition_column, manual_target_column,
                ],
                "custom_expression": [manual_key_columns],
            }
            common = columns_by_type.get(rule_type, [])
            fields: dict[str, list[Any]] = {
                "completeness": [manual_blank_missing, manual_tolerance],
                "uniqueness": [manual_tolerance],
                "value_set": [manual_mode, manual_values, manual_tolerance],
                "range": [
                    manual_minimum, manual_minimum_inclusive,
                    manual_maximum, manual_maximum_inclusive, manual_tolerance,
                ],
                "pattern": [manual_pattern, manual_tolerance],
                "column_relationship": [manual_operator, manual_tolerance],
                "conditional_completeness": [
                    manual_condition_operator, manual_condition_value,
                    manual_blank_missing, manual_tolerance,
                ],
                "conditional_values": [
                    manual_condition_operator, manual_condition_value,
                    manual_mode, manual_values, manual_tolerance,
                ],
                "custom_expression": [manual_expression, manual_tolerance],
            }
            manual_parameter_box.children = tuple(common + fields.get(rule_type, []))
            column_guidance = {
                "uniqueness": "Create one rule per selected column, or treat the selection as one composite key.",
                "column_relationship": "Choose explicit left and right columns for the comparison.",
                "conditional_completeness": "Choose the condition column and the required target column.",
                "conditional_values": "Choose the condition column and the constrained target column.",
                "custom_expression": "Optionally select the columns used by the expression; FabricOps validates the expression before enforcement.",
            }.get(
                rule_type,
                "Select one or more columns. FabricOps creates one independent rule per column.",
            )
            manual_rule_hint.value = (
                "<div style='color:#667085;font-size:12px;line-height:1.45;'>"
                + html.escape(column_guidance)
                + " Manual rules use the same deterministic representation as generated rules.</div>"
            )
            tolerance = dq_tolerance_parameter(rule_type, str(manual_mode.value or ""))
            manual_tolerance.layout.display = "" if tolerance else "none"

        def refresh_manual_preview(
            _change: dict[str, Any] | None = None,
        ) -> None:
            selected_type = str(manual_rule_type.value or "")
            rule_type = selected_type.replace("_", " ").title()
            if selected_type in manual_batch_rule_types:
                selected_names = [
                    str(value) for value in manual_batch_columns.value
                ]
                together = (
                    selected_type == "uniqueness"
                    and manual_apply_mode.value == "together"
                )
                groups = [selected_names] if together and selected_names else [
                    [name] for name in selected_names
                ]
            elif selected_type == "custom_expression":
                names = [str(value) for value in manual_key_columns.value]
                groups = [names]
            elif selected_type == "column_relationship":
                names = [
                    str(manual_left_column.value or ""),
                    str(manual_right_column.value or ""),
                ]
                groups = [[name for name in names if name]]
            elif selected_type.startswith("conditional_"):
                names = [
                    str(manual_condition_column.value or ""),
                    str(manual_target_column.value or ""),
                ]
                groups = [[name for name in names if name]]
            else:
                groups = []
            groups = [group for group in groups if group]
            names = [name for group in groups for name in group]
            rule_count = len(groups)
            policy = "Block" if manual_block.value else "Warn"
            tolerance = (
                f"; accept up to {html.escape(str(manual_tolerance.value or '0'))}% failures"
                if manual_tolerance.layout.display != "none" else ""
            )
            batch_items = (
                "<ul style='margin:6px 0 0 18px;padding:0;'>"
                + "".join(
                    f"<li>{html.escape(rule_type)} · "
                    f"{html.escape(', '.join(group))}</li>"
                    for group in groups
                )
                + "</ul>"
                if rule_count > 1 else ""
            )
            manual_preview.value = (
                "<div style='background:#f8f6fc;border-left:3px solid #6750a4;"
                "padding:9px 11px;font-size:12px;line-height:1.5;'>"
                f"<b>{'Rule' if rule_count == 1 else f'{rule_count} rules'} preview:</b> "
                f"{html.escape(rule_type)} on "
                f"{html.escape(', '.join(names) or 'a selected column')}; "
                f"{policy} on failure{tolerance}."
                + batch_items + "</div>"
            )
            add_manual_rule.description = (
                f"Add {rule_count} DQ Rules"
                if rule_count > 1 else "Add DQ Rule"
            )

        manual_rule_type.observe(refresh_manual_rule_fields, names="value")
        manual_mode.observe(refresh_manual_rule_fields, names="value")
        for preview_control in (
            manual_rule_type, manual_apply_mode, manual_batch_columns,
            manual_key_columns, manual_mode,
            manual_left_column, manual_right_column, manual_condition_column,
            manual_target_column, manual_block, manual_tolerance,
        ):
            preview_control.observe(refresh_manual_preview, names="value")
        refresh_manual_rule_fields()
        refresh_manual_preview()

        review_editor_state: dict[str, Any] = {
            "rule_type": "", "base": {}, "hydrating": False,
        }

        def hydrate_review_editor(
            rule_type: str, params: Mapping[str, Any],
        ) -> None:
            review_editor_state.update({
                "rule_type": rule_type, "base": dict(params), "hydrating": True,
            })
            names = [str(value) for value in params.get("columns", [])]
            try:
                review_column.value = names[0] if len(names) == 1 else ""
                review_key_columns.value = tuple(
                    name for name in names
                    if name in {str(value) for _label, value in dq_column_options}
                )
                review_left_column.value = names[0] if len(names) > 0 else ""
                review_right_column.value = names[1] if len(names) > 1 else ""
                review_condition_column.value = names[0] if len(names) > 0 else ""
                review_target_column.value = names[1] if len(names) > 1 else ""
                review_mode.value = (
                    str(params.get("mode"))
                    if str(params.get("mode")) in {"allow", "block"}
                    else "allow"
                )
                review_values.value = ", ".join(
                    str(value) for value in params.get("values", [])
                )
                review_minimum.value = str(params.get("minimum") or "")
                review_maximum.value = str(params.get("maximum") or "")
                review_minimum_inclusive.value = bool(
                    params.get("minimum_inclusive", True)
                )
                review_maximum_inclusive.value = bool(
                    params.get("maximum_inclusive", True)
                )
                review_pattern.value = str(params.get("pattern") or "")
                review_operator.value = (
                    str(params.get("operator"))
                    if str(params.get("operator")) in {"=", "!=", ">", ">=", "<", "<="}
                    else "="
                )
                review_condition_operator.value = (
                    str(params.get("condition_operator"))
                    if str(params.get("condition_operator")) in {"=", "!="}
                    else "="
                )
                review_condition_value.value = str(
                    params.get("condition_value") or ""
                )
                review_blank_missing.value = bool(
                    params.get("treat_blank_as_missing", False)
                )
                review_expression.value = str(params.get("expression") or "")
                columns_by_type: dict[str, list[Any]] = {
                    "uniqueness": [review_key_columns],
                    "column_relationship": [
                        review_left_column, review_operator, review_right_column,
                    ],
                    "conditional_completeness": [
                        review_condition_column, review_condition_operator,
                        review_condition_value, review_target_column,
                        review_blank_missing,
                    ],
                    "conditional_values": [
                        review_condition_column, review_condition_operator,
                        review_condition_value, review_target_column,
                        review_mode, review_values,
                    ],
                    "custom_expression": [review_key_columns, review_expression],
                    "value_set": [review_column, review_mode, review_values],
                    "range": [
                        review_column, review_minimum, review_minimum_inclusive,
                        review_maximum, review_maximum_inclusive,
                    ],
                    "pattern": [review_column, review_pattern],
                    "completeness": [review_column, review_blank_missing],
                }
                review_parameter_box.children = tuple(
                    columns_by_type.get(rule_type, [review_column])
                )
            finally:
                review_editor_state["hydrating"] = False

        def sync_review_editor(
            _change: dict[str, Any] | None = None,
        ) -> None:
            if review_editor_state["hydrating"] or business_hydrating["active"]:
                return
            rule_type = str(review_editor_state["rule_type"] or "")
            if not rule_type:
                return
            params = dict(review_editor_state["base"])
            if rule_type in {"uniqueness", "custom_expression"}:
                names = [str(value) for value in review_key_columns.value]
            elif rule_type == "column_relationship":
                names = [
                    str(review_left_column.value or ""),
                    str(review_right_column.value or ""),
                ]
            elif rule_type.startswith("conditional_"):
                names = [
                    str(review_condition_column.value or ""),
                    str(review_target_column.value or ""),
                ]
            else:
                names = [str(review_column.value or "")]
            params["columns"] = [name for name in names if name]
            if rule_type in {"value_set", "conditional_values"}:
                params["mode"] = str(review_mode.value)
                params["values"] = [
                    value.strip() for value in str(review_values.value).split(",")
                    if value.strip()
                ]
            if rule_type == "range":
                params.update({
                    "minimum": str(review_minimum.value or "").strip() or None,
                    "minimum_inclusive": bool(review_minimum_inclusive.value),
                    "maximum": str(review_maximum.value or "").strip() or None,
                    "maximum_inclusive": bool(review_maximum_inclusive.value),
                })
            elif rule_type == "pattern":
                params["pattern"] = str(review_pattern.value or "").strip()
            elif rule_type == "column_relationship":
                params["operator"] = str(review_operator.value)
            elif rule_type.startswith("conditional_"):
                params["condition_operator"] = str(review_condition_operator.value)
                params["condition_value"] = str(review_condition_value.value)
            if rule_type in {"completeness", "conditional_completeness"}:
                params["treat_blank_as_missing"] = bool(review_blank_missing.value)
            if rule_type == "custom_expression":
                params["expression"] = str(review_expression.value or "").strip()
                params["expression_language"] = "pyspark"
            business_parameters.value = json.dumps(
                params, indent=2, sort_keys=True, ensure_ascii=False
            )

        for review_control in (
            review_column, review_key_columns, review_left_column,
            review_right_column, review_condition_column, review_target_column,
            review_mode, review_values, review_minimum, review_maximum,
            review_minimum_inclusive, review_maximum_inclusive, review_pattern,
            review_operator, review_condition_operator, review_condition_value,
            review_blank_missing, review_expression,
        ):
            review_control.observe(sync_review_editor, names="value")

        def rule_column_names(rule: Mapping[str, Any]) -> list[str]:
            params = _parameters(rule)
            names = [
                str(name) for name in params.get("columns", [])
                if str(name).strip()
            ]
            if names:
                return names
            column_id = str(rule.get("column_id") or "")
            if not column_id:
                return []
            name = next((
                str(column.get("column_name") or "")
                for column in columns
                if str(column.get("column_id") or "") == column_id
            ), "")
            return [name] if name else []

        def business_rule_label(rule: Mapping[str, Any]) -> str:
            rule_type = str(rule.get("rule_type") or "")
            if rule_type == "value_set":
                mode = str(_parameters(rule).get("mode") or "").lower()
                kind = "Whitelist" if mode == "allow" else "Blacklist" if mode == "block" else "Value Set"
            else:
                kind = rule_type.replace("_", " ").title()
            names = rule_column_names(rule)
            return f"{kind} · {', '.join(names)}" if names else (kind or "DQ Rule")

        def proposal_label(proposal: Mapping[str, Any]) -> str:
            kind = str(proposal.get("rule_type") or "").replace("_", " ").title()
            names = [
                str(name) for name in proposal.get("columns", [])
                if str(name).strip()
            ]
            return f"{kind} · {', '.join(names)}" if names else (kind or "DQ Rule")

        def refresh_business_saved_options(selected: str | None = None) -> None:
            previous = str(business_saved.value or "")
            business_lookup.clear()
            options: list[tuple[str, str]] = [(
                "Select a rule to edit, or click here to create a new rule",
                new_rule_option,
            )]
            keys = " + ".join(str(key) for key in row_key_columns.value) or "Key required"
            grain_status = str(grain_policy.value) if grain_enabled.value else "Not enforced"
            options.append((
                f"Locked  |  GRAIN — Uniqueness · {keys}  |  {grain_status}",
                managed_grain_option,
            ))
            for rule in session_guardrails():
                if str(rule.get("guardrail_type") or "").lower() not in {
                    "data_quality", "dq"
                }:
                    continue
                if str(rule.get("rule_type") or "") not in {
                    "completeness", "uniqueness", "value_set", "range", "pattern",
                    "column_relationship", "conditional_completeness",
                    "conditional_values", "custom_expression",
                }:
                    continue
                key = str(rule.get("guardrail_rule_id") or "")
                if not key:
                    continue
                business_lookup[key] = rule
                status = "Enabled" if rule.get("is_active", True) else "Disabled"
                action = str(rule.get("action") or "Warn")
                options.append((
                    f"{status}  |  {business_rule_label(rule)}  |  {action}",
                    key,
                ))
            options.extend(
                (
                    f"AI draft  |  {proposal_label(proposal)}  |  Review required",
                    f"__ai_draft__:{index}",
                )
                for index, proposal in enumerate(business_resolved)
            )
            business_saved.options = options
            option_values = {str(value) for _label, value in options}
            requested = selected if selected is not None else previous
            business_saved.value = (
                requested if requested in option_values else new_rule_option
            )

        def refresh_resolved_options(selected: int = 0) -> None:
            if not business_resolved:
                business_proposal_select.options = [
                    ("Generated rules will appear here", -1)
                ]
                business_proposal_select.value = -1
                refresh_business_saved_options()
                return
            business_proposal_select.options = [
                ("Select a resolved DQ Rule", -1),
                *[
                    (proposal_label(proposal), index)
                    for index, proposal in enumerate(business_resolved)
                ],
            ]
            business_proposal_select.value = min(
                max(selected, 0), len(business_resolved) - 1
            )
            refresh_business_saved_options(
                f"__ai_draft__:{business_proposal_select.value}"
            )

        def hide_business_delete_confirmation() -> None:
            delete_business_rule_confirm.layout.display = "none"
            delete_business_rule_status.value = ""

        def engineering_review_state(rule: Mapping[str, Any]) -> tuple[bool, str]:
            if str(rule.get("rule_type") or "") != "custom_expression":
                return False, "not_required"
            params = _parameters(rule)
            required = bool(params.get("engineering_review_required", True))
            status = str(params.get("engineering_review_status") or "pending").lower()
            return required, status

        def render_engineering_review(rule: Mapping[str, Any] | None = None) -> None:
            current_rule = dict(rule or {})
            required, status = engineering_review_state(current_rule)
            engineering_review_panel.layout.display = "" if required else "none"
            if not required:
                engineering_review_status.value = ""
                approve_engineering_review.disabled = True
                return
            params = _parameters(current_rule)
            approved = status == "approved"
            reviewer = str(params.get("engineering_reviewed_by") or "")
            note = str(params.get("engineering_review_note") or "")
            engineering_reviewer.value = reviewer
            engineering_review_note.value = note
            if approved:
                engineering_review_status.value = (
                    "<div style='color:#107c10;font-weight:600;'>Engineering review approved"
                    + (f" by {html.escape(reviewer)}" if reviewer else "")
                    + ".</div>"
                )
            else:
                engineering_review_status.value = (
                    "<div style='color:#8a6d1d;font-weight:600;'>Engineering review pending.</div>"
                    "<div style='color:#667085;font-size:12px;margin-top:3px;'>"
                    "Review the resolved Custom Expression before approving it for freeze.</div>"
                )
            approve_engineering_review.disabled = not editable or approved

        def render_business_proposal(
            proposal: Mapping[str, Any] | None = None,
            *,
            saved: bool = False,
        ) -> None:
            business_validation.value = ""
            if not proposal:
                business_rule_controls.layout.display = "none"
                review_parameter_box.children = ()
                review_editor_state.update({"rule_type": "", "base": {}})
                business_proposal.value = (
                    "<p style='color:#667085;'>No DQ Rule selected.</p>"
                )
                apply_business_rule.disabled = True
                apply_business_rule.description = "Add DQ Rule"
                render_engineering_review()
                return

            params = (
                _parameters(proposal)
                if saved
                else dict(proposal.get("parameters") or {})
            )
            if not saved and proposal.get("_parameters_draft"):
                try:
                    drafted_parameters = json.loads(str(proposal["_parameters_draft"]))
                    if isinstance(drafted_parameters, dict):
                        params = drafted_parameters
                except json.JSONDecodeError:
                    pass
            business_parameters.value = json.dumps(
                params, indent=2, sort_keys=True, ensure_ascii=False
            )
            rule_type = str(proposal.get("rule_type") or "")
            hydrate_review_editor(rule_type, params)
            tolerance_field = dq_tolerance_parameter(rule_type, str(params.get("mode") or ""))
            business_tolerance.layout.display = "" if tolerance_field else "none"
            if tolerance_field:
                business_tolerance.description = "Accepted failure rate %"
                existing_value = params.get(tolerance_field, 0)
                if rule_type == "uniqueness" and "minimum_unique_percent" in params:
                    existing_value = "" if params["minimum_unique_percent"] != 100 else 0
                business_tolerance.value = str(proposal.get("_tolerance_draft", existing_value))
                denominator = "matching applicable rows" if rule_type.startswith("conditional_") else "applicable rows"
                business_tolerance_hint.value = (
                    "<small>All rows in duplicate key groups fail. Legacy distinct-key limits require an explicit accepted failure rate when edited.</small>"
                    if rule_type == "uniqueness" else f"<small>Percentage of {denominator}. Actual violations remain visible within tolerance.</small>"
                )
            else:
                business_tolerance_hint.value = "<small>Prohibited values are strict; no percentage tolerance applies.</small>"
            names = (
                rule_column_names(proposal)
                if saved
                else [str(name) for name in proposal.get("columns", [])]
            )
            requirement = str(
                params.get("business_requirement")
                or proposal.get("business_requirement")
                or ""
            ).strip()
            details = []
            for name, value in params.items():
                if name in {
                    "columns", "business_requirement",
                    "engineering_review_required", "engineering_review_status",
                    "engineering_reviewed_by", "engineering_review_note",
                } or value in (None, "", [], {}):
                    continue
                shown = ", ".join(map(str, value)) if isinstance(value, list) else str(value)
                details.append(
                    "<div><b>{}</b>: {}</div>".format(
                        html.escape(name.replace("_", " ").title()),
                        html.escape(shown),
                    )
                )
            source = "Current draft DQ Rule" if saved else "Generated atomic DQ Rule"
            business_proposal.value = (
                "<div style='background:#f6f8fa;border-left:3px solid var(--form-accent);"
                "padding:12px 14px;font-size:12px;line-height:1.6;'>"
                f"<div style='color:#667085;'>{source}</div>"
                f"<div style='font-size:15px;font-weight:700;margin-top:2px;'>"
                f"{html.escape(rule_type.replace('_', ' ').title())}</div>"
                f"<div><b>Column(s)</b>: {html.escape(', '.join(names) or '—')}</div>"
                + (
                    f"<div><b>Requirement</b>: {html.escape(requirement)}</div>"
                    if requirement else ""
                )
                + ("<details><summary>Rule parameters</summary>" + "".join(details) + "</details>" if details else "")
                + "</div>"
            )
            business_rule_controls.layout.display = ""
            apply_business_rule.description = (
                "Update DQ Rule" if saved else "Add DQ Rule"
            )
            apply_business_rule.disabled = not editable
            if saved:
                render_engineering_review(proposal)
            else:
                render_engineering_review()

        def hydrate_business_saved(
            change: dict[str, Any] | None = None,
        ) -> None:
            if business_hydrating["active"]:
                return
            key = str(business_saved.value or "")
            if key == managed_grain_option:
                hide_business_delete_confirmation()
                business_active_saved["rule_id"] = ""
                delete_business_rule.disabled = True
                delete_business_rule.layout.display = "none"
                return
            if key.startswith("__ai_draft__:"):
                try:
                    index = int(key.rsplit(":", 1)[1])
                except ValueError:
                    render_business_proposal()
                    return
                business_proposal_select.value = index
                hydrate_resolved_business()
                return
            business_hydrating["active"] = True
            try:
                hide_business_delete_confirmation()
                rule = business_lookup.get(key, {})
                business_active_saved["rule_id"] = key if rule else ""
                delete_business_rule.disabled = not editable or not bool(rule)
                delete_business_rule.layout.display = "" if rule else "none"
                if not rule:
                    if int(business_proposal_select.value) if business_proposal_select.value is not None else -1 < 0:
                        render_business_proposal()
                    return
                business_editor_heading.value = (
                    "<div class='fabricops-dq-editor-heading'>Edit current rule</div>"
                )
                business_proposal_select.value = -1
                business_enabled.value = bool(rule.get("is_active", True))
                business_block.value = str(rule.get("action") or "Warn") == "Block"
                render_business_proposal(rule, saved=True)
            finally:
                business_hydrating["active"] = False

        def hydrate_resolved_business(
            change: dict[str, Any] | None = None,
        ) -> None:
            if business_hydrating["active"]:
                return
            index = int(business_proposal_select.value) if business_proposal_select.value is not None else -1
            if index < 0 or index >= len(business_resolved):
                if not business_active_saved["rule_id"]:
                    render_business_proposal()
                return
            business_hydrating["active"] = True
            try:
                business_editor_heading.value = (
                    "<div class='fabricops-dq-editor-heading'>Review AI draft</div>"
                )
                business_active_saved["rule_id"] = ""
                delete_business_rule.disabled = True
                delete_business_rule.layout.display = "none"
                proposal = business_resolved[index]
                business_enabled.value = bool(proposal.get("_enabled", True))
                business_block.value = bool(proposal.get("_block", False))
                render_business_proposal(proposal)
            finally:
                business_hydrating["active"] = False

        def remember_resolved_rule_settings(
            _change: dict[str, Any] | None = None,
        ) -> None:
            if business_hydrating["active"]:
                return
            index = int(business_proposal_select.value) if business_proposal_select.value is not None else -1
            if 0 <= index < len(business_resolved):
                business_resolved[index]["_enabled"] = bool(business_enabled.value)
                business_resolved[index]["_block"] = bool(business_block.value)
                business_resolved[index]["_tolerance_draft"] = business_tolerance.value
                business_resolved[index]["_parameters_draft"] = business_parameters.value

        def invalidate_business_proposal(
            _change: dict[str, Any] | None = None,
        ) -> None:
            if business_hydrating["active"]:
                return
            business_resolved.clear()
            business_active_saved["rule_id"] = ""
            refresh_resolved_options()
            apply_business_rule.disabled = True
            render_business_proposal()

        def current_rule_context() -> list[dict[str, Any]]:
            return [
                {
                    "rule_type": str(rule.get("rule_type") or ""),
                    "columns": rule_column_names(rule),
                    "parameters": {
                        key: value
                        for key, value in _parameters(rule).items()
                        if key not in {
                            "business_requirement",
                            "engineering_review_required",
                            "engineering_review_status",
                            "engineering_reviewed_by",
                            "engineering_review_note",
                        }
                    },
                }
                for rule in session_guardrails()
                if str(rule.get("guardrail_type") or "").lower() in {
                    "data_quality", "dq"
                }
                and rule_column_names(rule)
            ]

        @busy_action("Generating Data Quality proposals…", ai_request=True)
        def resolve_business_rule_clicked(_button: Any) -> None:
            if not editable or not ai_available():
                return
            resolve_business_rule.disabled = True
            resolve_business_rule.description = "Generating DQ Rules…"
            business_active_saved["rule_id"] = ""
            business_editor_heading.value = (
                "<div class='fabricops-dq-editor-heading'>Review AI draft</div>"
            )
            render_business_proposal()
            retrying = "business_rule_ai" in state["_validation_errors"]
            business_proposal.value = "<p role='status'>Generating proposals for review…</p>"
            try:
                ensure_runtime_context()
                profiles = dict(runtime_context.get("column_profiles") or {})
                context_payload = build_ai_business_rule_context({
                    "table_name": table.get("table_name"),
                    "schema_name": table.get("schema_name"),
                    "layer": table.get("layer"),
                    "table_description": _effective_table_ai_description(),
                    "table_classification": table_classification.value,
                    "columns": [
                        {
                            **column,
                            "description": _column_editable_values(
                                str(column.get("column_id") or "")
                            )[0],
                            "classification": _column_editable_values(
                                str(column.get("column_id") or "")
                            )[1],
                            "profile": profiles.get(
                                str(column.get("column_id") or ""), {}
                            ),
                        }
                        for column in authoring_columns
                    ],
                    "existing_dq_rules": current_rule_context(),
                })
                proposals = suggest_business_rule(
                    context_payload,
                    requirement=str(business_requirement.value or ""),
                    relevant_columns=list(business_columns.value),
                    prompt=str(ai_enrichment.get("business_rule_prompt") or ""),
                    ai_config=ai_enrichment, spark_session=spark, usage=state["ai_usage"],
                    runtime_context=ai_runtime_context(), operation="business_rule_ai",
                )
                business_resolved.clear()
                business_resolved.extend(
                    {
                        **proposal,
                        "_enabled": True,
                        "_block": False,
                    }
                    for proposal in proposals
                )
                business_active_saved["rule_id"] = ""
                refresh_resolved_options()
                hydrate_resolved_business()
                set_validation_error("business_rule_ai")
                refresh_ai_usage()
                if retrying:
                    ai_recovered(
                        "DQ Rule suggestions generated after retry.",
                        operation="business_rule_ai",
                        remaining_errors=bool(ai_errors),
                    )
            except (TypeError, ValueError, RuntimeError, ImportError) as exc:
                business_resolved.clear()
                refresh_resolved_options()
                apply_business_rule.disabled = True
                refresh_ai_usage()
                message = ai_failure_message(exc, "business_rule_ai")
                business_proposal.value = f"<p>{html.escape(message)}</p>"
                if not state["_ai_unavailable"]:
                    set_validation_error("business_rule_ai", exc)
            finally:
                resolve_business_rule.description = "Generate DQ Rules"
                resolve_business_rule.disabled = not (editable and ai_available())

        def sync_column_rule(rule: Mapping[str, Any]) -> None:
            column_id = str(rule.get("column_id") or "")
            rule_type = str(rule.get("rule_type") or "")
            if not column_id or rule_type not in _COLUMN_DQ_TYPES:
                return
            selected_dq_by_column[column_id] = rule_type
            if str(column_select.value or "") == column_id:
                hydrating["active"] = True
                try:
                    hydrate_dq_family(column_id, rule_type)
                finally:
                    hydrating["active"] = False

        def add_manual_rule_clicked(_button: Any) -> None:
            try:
                rule_type = str(manual_rule_type.value or "")
                if rule_type in manual_batch_rule_types:
                    selected_names = [
                        str(value) for value in manual_batch_columns.value
                    ]
                    together = (
                        rule_type == "uniqueness"
                        and manual_apply_mode.value == "together"
                    )
                    column_groups = (
                        [selected_names] if together else [
                            [name] for name in selected_names
                        ]
                    )
                elif rule_type == "custom_expression":
                    selected_names = [
                        str(value) for value in manual_key_columns.value
                    ]
                    column_groups = [selected_names]
                elif rule_type == "column_relationship":
                    selected_names = [
                        str(manual_left_column.value or ""),
                        str(manual_right_column.value or ""),
                    ]
                    column_groups = [selected_names]
                elif rule_type in {
                    "conditional_completeness", "conditional_values",
                }:
                    selected_names = [
                        str(manual_condition_column.value or ""),
                        str(manual_target_column.value or ""),
                    ]
                    column_groups = [selected_names]
                else:
                    selected_names = []
                    column_groups = []
                selected_names = [name for name in selected_names if name]
                column_groups = [
                    [name for name in group if name] for group in column_groups
                ]
                column_groups = [group for group in column_groups if group]
                if rule_type == "custom_expression" and not column_groups:
                    column_groups = [[]]
                expected = {
                    "completeness": (1, None),
                    "uniqueness": (1, None),
                    "value_set": (1, None),
                    "range": (1, None),
                    "pattern": (1, None),
                    "column_relationship": (2, 2),
                    "conditional_completeness": (2, 2),
                    "conditional_values": (2, 2),
                    "custom_expression": (0, None),
                }
                minimum, maximum = expected[rule_type]
                if len(selected_names) < minimum or (
                    maximum is not None and len(selected_names) > maximum
                ):
                    requirement = (
                        f"exactly {minimum}" if minimum == maximum
                        else f"at least {minimum}"
                    )
                    raise ValueError(
                        f"{rule_type.replace('_', ' ').title()} requires {requirement} selected column(s)."
                    )
                if len(selected_names) == 2 and selected_names[0] == selected_names[1]:
                    raise ValueError("Select two different columns.")

                tolerance_field = dq_tolerance_parameter(
                    rule_type, str(manual_mode.value or "")
                )
                params: dict[str, Any] = {"columns": selected_names}
                if tolerance_field:
                    tolerance = float(manual_tolerance.value)
                    if not 0 <= tolerance <= 100:
                        raise ValueError(
                            "Accepted failure rate % must be between 0 and 100."
                        )
                    params[tolerance_field] = tolerance
                values = [
                    item.strip() for item in str(manual_values.value or "").split(",")
                    if item.strip()
                ]
                if rule_type == "completeness":
                    params["treat_blank_as_missing"] = bool(manual_blank_missing.value)
                elif rule_type == "value_set":
                    if not values:
                        raise ValueError("Value Set requires at least one value.")
                    params.update({"mode": str(manual_mode.value), "values": values})
                elif rule_type == "range":
                    if not manual_minimum.value.strip() and not manual_maximum.value.strip():
                        raise ValueError("Range requires a lower or upper bound.")
                    params.update({
                        "minimum": manual_minimum.value.strip() or None,
                        "minimum_inclusive": bool(manual_minimum_inclusive.value),
                        "maximum": manual_maximum.value.strip() or None,
                        "maximum_inclusive": bool(manual_maximum_inclusive.value),
                    })
                elif rule_type == "pattern":
                    pattern = str(manual_pattern.value or "").strip()
                    if not pattern:
                        raise ValueError("Pattern requires a regular expression.")
                    params["pattern"] = pattern
                elif rule_type == "column_relationship":
                    params["operator"] = str(manual_operator.value)
                elif rule_type in {"conditional_completeness", "conditional_values"}:
                    params.update({
                        "condition_operator": str(manual_condition_operator.value),
                        "condition_value": str(manual_condition_value.value),
                    })
                    if rule_type == "conditional_completeness":
                        params["treat_blank_as_missing"] = bool(manual_blank_missing.value)
                    else:
                        if not values:
                            raise ValueError("Conditional Values requires at least one value.")
                        params.update({"mode": str(manual_mode.value), "values": values})
                elif rule_type == "custom_expression":
                    expression = str(manual_expression.value or "").strip()
                    if not expression:
                        raise ValueError("Custom Expression requires a PySpark boolean expression.")
                    params.update({
                        "expression_language": "pyspark",
                        "expression": expression,
                        "engineering_review_required": True,
                        "engineering_review_status": "pending",
                    })

                records: list[dict[str, Any]] = []
                for group in column_groups:
                    record_params = {**params, "columns": group}
                    column_id = ""
                    if len(group) == 1 and rule_type in manual_batch_rule_types:
                        column_id = next((
                            str(column.get("column_id") or "")
                            for column in columns
                            if str(column.get("column_name") or "") == group[0]
                        ), "")
                    records.append(guardrail_record(
                        "data_quality", rule_type, record_params,
                        column_id=column_id,
                        action="Block" if manual_block.value else "Warn",
                        active=bool(manual_enabled.value),
                    ))
                stage_guardrails(records)
                for record in records:
                    sync_column_rule(record)
                refresh_business_saved_options(
                    str(records[-1]["guardrail_rule_id"])
                )
                business_editor_heading.value = (
                    "<div class='fabricops-dq-editor-heading'>Edit current rule</div>"
                )
                render_table_summary()
                set_validation_error("manual_dq_rule")
                manual_validation.value = ""
                set_status(
                    f"{len(records)} DQ Rule{'s' if len(records) != 1 else ''} added "
                    "to the current draft. Save Data Contract to persist."
                )
                manual_batch_columns.value = ()
                manual_key_columns.value = ()
                manual_left_column.value = ""
                manual_right_column.value = ""
                manual_condition_column.value = ""
                manual_target_column.value = ""
                manual_values.value = ""
                manual_minimum.value = ""
                manual_maximum.value = ""
                manual_pattern.value = ""
                manual_condition_value.value = ""
                manual_expression.value = ""
                manual_tolerance.value = "0"
            except (KeyError, TypeError, ValueError, RuntimeError) as exc:
                set_validation_error("manual_dq_rule", exc)
                manual_validation.value = (
                    "<div role='alert' style='color:#a4262c;font-size:12px;font-weight:600;'>"
                    + html.escape(str(exc)) + "</div>"
                )
                set_status(str(exc), error=True)

        add_manual_rule.on_click(add_manual_rule_clicked)

        def apply_business_rule_clicked(_button: Any) -> None:
            try:
                saved_key = str(business_active_saved["rule_id"] or "")
                if saved_key:
                    existing = business_lookup.get(saved_key, {})
                    if not existing:
                        return
                    params = json.loads(str(business_parameters.value or "{}"))
                    if not isinstance(params, dict):
                        raise ValueError("Rule parameters must be a JSON object.")
                    field = dq_tolerance_parameter(str(existing.get("rule_type") or ""), str(params.get("mode") or ""))
                    if field:
                        value = float(business_tolerance.value)
                        if not 0 <= value <= 100:
                            raise ValueError("DQ percentage must be between 0 and 100.")
                        params.pop("minimum_unique_percent", None)
                        params[field] = value
                    edited_type = str(existing.get("rule_type") or "")
                    edited_columns = [str(value) for value in params.get("columns") or []]
                    edited_column_id = ""
                    if len(edited_columns) == 1 and edited_type in {
                        "completeness", "uniqueness", "value_set", "range", "pattern"
                    }:
                        edited_column_id = next((
                            str(column.get("column_id") or "")
                            for column in columns
                            if str(column.get("column_name") or "") == edited_columns[0]
                        ), "")
                    record = guardrail_record(
                        "data_quality",
                        edited_type,
                        params,
                        column_id=edited_column_id,
                        action="Block" if business_block.value else "Warn",
                        existing=existing,
                        active=bool(business_enabled.value),
                    )
                    stage_guardrails([record])
                    sync_column_rule(record)
                    refresh_business_saved_options(
                        str(record["guardrail_rule_id"])
                    )
                    render_table_summary()
                    business_validation.value = ""
                    set_validation_error("business_rule")
                    set_status(
                        "DQ Rule updated in the current draft. "
                        "Save Data Contract to persist."
                    )
                    return

                index = int(business_proposal_select.value) if business_proposal_select.value is not None else -1
                if index < 0 or index >= len(business_resolved):
                    return
                proposal = dict(business_resolved[index])
                params = json.loads(str(business_parameters.value or "{}"))
                if not isinstance(params, dict):
                    raise ValueError("Rule parameters must be a JSON object.")
                field = dq_tolerance_parameter(str(proposal.get("rule_type") or ""), str(params.get("mode") or ""))
                if field:
                    value = float(business_tolerance.value)
                    if not 0 <= value <= 100:
                        raise ValueError("DQ percentage must be between 0 and 100.")
                    params.pop("minimum_unique_percent", None)
                    params[field] = value
                if str(proposal.get("rule_type") or "") == "custom_expression":
                    params.update({
                        "engineering_review_required": True,
                        "engineering_review_status": "pending",
                    })
                    params.pop("engineering_reviewed_by", None)
                    params.pop("engineering_review_note", None)

                resolved_type = str(proposal["rule_type"])
                resolved_columns = [
                    str(value) for value in params.get("columns") or []
                ]
                column_rule_id = ""
                existing: Mapping[str, Any] = {}
                if resolved_type == "uniqueness":
                    existing = {}
                elif (
                    resolved_type in _COLUMN_DQ_TYPES
                    and len(resolved_columns) == 1
                ):
                    column_rule_id = next((
                        str(column.get("column_id") or "")
                        for column in columns
                        if str(column.get("column_name") or "")
                        == resolved_columns[0]
                    ), "")
                    if not column_rule_id:
                        raise ValueError(
                            "Resolved single-column DQ Rule does not match "
                            "a governed column."
                        )
                    existing = next((
                        rule for rule in session_guardrails()
                        if str(rule.get("guardrail_type") or "").lower()
                        in {"data_quality", "dq"}
                        and str(rule.get("column_id") or "") == column_rule_id
                        and str(rule.get("rule_type") or "") == resolved_type
                    ), {})

                record = guardrail_record(
                    "data_quality",
                    resolved_type,
                    params,
                    column_id=column_rule_id,
                    action="Block" if proposal.get("_block") else "Warn",
                    existing=existing,
                    active=bool(proposal.get("_enabled", True)),
                )
                stage_guardrails([record])
                sync_column_rule(record)
                render_table_summary()

                business_resolved.pop(index)
                refresh_resolved_options(
                    min(index, max(len(business_resolved) - 1, 0))
                )
                refresh_business_saved_options(
                    str(record["guardrail_rule_id"])
                )
                business_active_saved["rule_id"] = str(
                    record["guardrail_rule_id"]
                )
                set_validation_error("business_rule")
                business_validation.value = ""
                set_status(
                    "DQ Rule added to the current draft. "
                    "Save Data Contract to persist."
                )
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error("business_rule", exc)
                business_validation.value = (
                    "<div role='alert' style='color:#a4262c;font-size:12px;font-weight:600;'>"
                    + html.escape(str(exc)) + "</div>"
                )
                set_status(str(exc), error=True)

        def request_delete_business_rule_clicked(_button: Any) -> None:
            rule = business_lookup.get(str(business_saved.value or ""), {})
            if not editable or not rule:
                return
            delete_business_rule_status.value = (
                "<div style='color:#a4262c;font-weight:600;'>Delete this DQ Rule?</div>"
                "<div style='color:#667085;font-size:12px;margin-top:3px;'>"
                "The rule will be removed from the current draft. "
                "Save the Data Contract to persist the deletion.</div>"
            )
            delete_business_rule_confirm.layout.display = ""

        def cancel_delete_business_rule_clicked(_button: Any) -> None:
            hide_business_delete_confirmation()

        def confirm_delete_business_rule_clicked(_button: Any) -> None:
            key = str(business_saved.value or "")
            rule = business_lookup.get(key, {})
            if not editable or not key or not rule:
                hide_business_delete_confirmation()
                return
            current["guardrails"] = [
                row for row in current.get("guardrails", [])
                if str(row.get("guardrail_rule_id") or "") != key
            ]
            scope = (
                str(current["contract_id"]),
                int(current["contract_version"]),
            )
            state["_pending_guardrails"].get(scope, {}).pop(key, None)
            state["dirty"] = True
            deleted_column_id = str(rule.get("column_id") or "")
            deleted_type = str(rule.get("rule_type") or "")
            refresh_manifest()
            render_table_summary()
            refresh_business_saved_options()
            business_active_saved["rule_id"] = ""
            if (
                deleted_column_id
                and deleted_type in _COLUMN_DQ_TYPES
                and str(column_select.value or "") == deleted_column_id
            ):
                hydrating["active"] = True
                try:
                    hydrate_dq_family(deleted_column_id, deleted_type)
                finally:
                    hydrating["active"] = False
            hide_business_delete_confirmation()
            render_business_proposal()
            set_validation_error("business_rule")
            set_status(
                "DQ Rule deletion staged. Save Data Contract to persist."
            )

        def approve_engineering_review_clicked(_button: Any) -> None:
            try:
                rule = business_lookup.get(str(business_saved.value or ""), {})
                required, status = engineering_review_state(rule)
                if not required:
                    raise ValueError(
                        "The selected DQ Rule does not require Engineering review."
                    )
                if status == "approved":
                    return
                reviewer = str(engineering_reviewer.value or "").strip()
                if not reviewer:
                    raise ValueError(
                        "Engineering reviewer is required before approval."
                    )
                params = _parameters(rule)
                params.update({
                    "engineering_review_required": True,
                    "engineering_review_status": "approved",
                    "engineering_reviewed_by": reviewer,
                    "engineering_review_note": str(
                        engineering_review_note.value or ""
                    ).strip(),
                })
                record = guardrail_record(
                    "data_quality",
                    "custom_expression",
                    params,
                    action=str(rule.get("action") or "Warn"),
                    existing=rule,
                    active=bool(rule.get("is_active", True)),
                )
                stage_guardrails([record])
                refresh_business_saved_options(
                    str(record["guardrail_rule_id"])
                )
                render_engineering_review(record)
                set_validation_error("business_rule.engineering_review")
                set_status(
                    "Engineering review approved and staged. "
                    "Save Data Contract to persist."
                )
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error("business_rule.engineering_review", exc)
                set_status(str(exc), error=True)

        delete_business_rule.layout.display = "none"
        business_saved.observe(hydrate_business_saved, names="value")
        business_proposal_select.observe(
            hydrate_resolved_business, names="value"
        )
        business_requirement.observe(
            invalidate_business_proposal, names="value"
        )
        business_columns.observe(
            invalidate_business_proposal, names="value"
        )
        business_enabled.observe(
            remember_resolved_rule_settings, names="value"
        )
        business_block.observe(
            remember_resolved_rule_settings, names="value"
        )
        business_tolerance.observe(remember_resolved_rule_settings, names="value")
        business_parameters.observe(remember_resolved_rule_settings, names="value")
        resolve_business_rule.on_click(resolve_business_rule_clicked)
        apply_business_rule.on_click(apply_business_rule_clicked)
        delete_business_rule.on_click(request_delete_business_rule_clicked)
        confirm_delete_business_rule.on_click(
            confirm_delete_business_rule_clicked
        )
        cancel_delete_business_rule.on_click(
            cancel_delete_business_rule_clicked
        )
        approve_engineering_review.on_click(
            approve_engineering_review_clicked
        )
        refresh_business_saved_options()
        refresh_resolved_options()
        state["_refresh_dq_rules"] = refresh_business_saved_options

        business_ai_panel = widgets.VBox(
            [
                widgets.HTML(
                    "<div style='color:#6750a4;font-size:13px;font-weight:700;'>"
                    "Draft with AI (optional)</div>"
                    "<div style='color:#526477;font-size:12px;line-height:1.5;"
                    "margin-top:4px;'>"
                    "Describe the outcome in plain language. AI drafts deterministic "
                    "rules into the list for review; it does not add them to the "
                    "contract automatically.</div>"
                ),
                business_requirement,
            ],
            layout=widgets.Layout(
                width="100%", min_width="0", gap="8px"
            ),
        )
        business_ai_panel.add_class("fabricops-business-body")
        business_generate_actions = shared.action_row(widgets, [resolve_business_rule])
        business_generate_actions.add_class("fabricops-business-footer")
        business_primary = widgets.VBox(
            [business_proposal, business_rule_controls, business_validation,
             engineering_review_panel],
            layout=widgets.Layout(width="100%", min_width="0"),
        )
        business_primary.add_class("fabricops-business-body")
        business_review_actions = widgets.VBox([
            delete_business_rule_confirm,
            shared.action_row(widgets, [delete_business_rule, apply_business_rule]),
        ], layout=widgets.Layout(width="100%"))
        business_review_actions.add_class("fabricops-business-footer")
        current_rules_section = shared.form_section(
            widgets,
            title="Data Quality Rules",
            children=[
                widgets.HTML(
                    "<div style='color:#667085;font-size:12px;line-height:1.5;'>"
                    "Select a current rule or AI draft to edit it, or select the first "
                    "row to create a new rule. The locked GRAIN rule is managed in the Table tab. "
                    "AI drafts remain proposals until you review and add them.</div>"
                ),
                business_saved,
            ],
        )
        rule_reviewer = widgets.VBox(
            [business_editor_heading, business_primary, business_review_actions],
            layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
        )
        manual_rule_editor = widgets.VBox(
            [
                widgets.HTML(
                    "<div style='color:#243449;font-size:13px;font-weight:700;'>"
                    "Configure manually</div>"
                    "<div style='color:#667085;font-size:12px;line-height:1.5;"
                    "margin-top:4px;'>"
                    "Choose a deterministic rule type and configure it here.</div>"
                ),
                manual_rule_type,
                manual_rule_hint,
                manual_parameter_box,
                manual_preview,
                manual_validation,
                widgets.HBox(
                    [manual_enabled, manual_block],
                    layout=checkbox_row_layout,
                ),
                shared.action_row(widgets, [add_manual_rule]),
            ],
            layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
        )
        ai_rule_editor = widgets.VBox(
            [business_ai_panel, business_generate_actions],
            layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
        )
        ai_rule_editor.add_class("fabricops-dq-ai-create")
        new_rule_editor = widgets.VBox(
            [
                *([ai_rule_editor] if ai_visible and ai_available() else []),
                manual_rule_editor,
            ],
            layout=widgets.Layout(width="100%", min_width="0", gap="16px"),
        )
        managed_grain_review = widgets.HTML()
        rule_workspace_body = widgets.VBox(
            [new_rule_editor],
            layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
        )
        rule_workspace_section = shared.form_section(
            widgets, title="Rule workspace", children=[rule_workspace_body]
        )

        def set_rule_workspace(mode: str) -> None:
            if mode == "managed_grain":
                rule_workspace_body.children = (managed_grain_review,)
            elif mode == "review":
                rule_workspace_body.children = (rule_reviewer,)
            else:
                rule_workspace_body.children = (new_rule_editor,)

        def open_selected_rule(change: dict[str, Any]) -> None:
            if str(change.get("new") or "") == managed_grain_option:
                set_rule_workspace("managed_grain")
            elif str(change.get("new") or "") == new_rule_option:
                set_rule_workspace("create")
            elif str(change.get("new") or ""):
                set_rule_workspace("review")

        business_saved.observe(open_selected_rule, names="value")
        if str(business_saved.value or "") == new_rule_option:
            set_rule_workspace("create")
        elif business_saved.value == managed_grain_option:
            set_rule_workspace("managed_grain")
        elif business_saved.value:
            set_rule_workspace("review")

        managed_grain = widgets.HTML()
        def render_managed_grain(_change=None):
            keys = " + ".join(str(key) for key in row_key_columns.value) or "Key required"
            status = "Enabled" if grain_enabled.value else "Not enforced"
            managed_grain.value = (
                "<b>GRAIN — Uniqueness</b><br>"
                + html.escape(keys) + " · " + html.escape(str(grain_policy.value)) + " · " + status
                + "<br>Edit the row key and enforcement in the Table tab. Non-null keys are required."
            ) if grain_enabled.value else ""
            managed_grain_review.value = (
                "<div style='padding:12px;border:1px solid #dce4ed;border-radius:8px'>"
                "<b>Locked managed rule — GRAIN · Uniqueness</b><br>"
                + html.escape(keys) + " · " + html.escape(str(grain_policy.value))
                + "<p>Grain uniqueness is configured in the Table tab. "
                "It cannot be edited or deleted from Data Quality Rules.</p></div>"
            )
            refresh_business_saved_options()
        for control in (row_key_columns, grain_enabled, grain_policy):
            control.observe(render_managed_grain, names="value")
        render_managed_grain()
        business_left = (current_rules_section,)
        business_right = (rule_workspace_section,)
        view_content["Data Quality"] = (business_left, business_right)


        # Manifest: current working contract plus changes since the last persisted draft.
        payload = refresh_manifest() or {}
        saved_payload = state.get("_saved_payload") or {}

        def review_change_html() -> str:
            changes: list[str] = []
            old_table = dict(saved_payload.get("table") or {})
            new_table = dict(payload.get("table") or {})
            def enrichment_map(doc: dict[str, Any]) -> dict[tuple[str, str], str]:
                result: dict[tuple[str, str], str] = {}
                enrichment = doc.get("enrichment") or {}
                for item in [*(enrichment.get("table") or []), *(enrichment.get("columns") or [])]:
                    result[(str(item.get("column_id") or ""), str(item.get("enrichment_type") or ""))] = str(item.get("value") or "")
                return result

            old_enrichment, new_enrichment = enrichment_map(saved_payload), enrichment_map(payload)
            column_names = {
                str(item.get("column_id") or ""): str(item.get("column_name") or "Column")
                for item in [*(old_table.get("columns") or []), *(new_table.get("columns") or [])]
                if item.get("column_id")
            }
            for key in sorted(set(old_enrichment) | set(new_enrichment)):
                before, after = old_enrichment.get(key, ""), new_enrichment.get(key, "")
                if before != after:
                    target = column_names.get(key[0], "Column") if key[0] else "Table"
                    changes.append(
                        f"<li><b>{html.escape(target)} · {html.escape(key[1])}</b>: "
                        f"{html.escape(before or 'Not set')} → {html.escape(after or 'Not set')}</li>"
                    )

            old_columns = {
                str(item.get("column_id") or ""): item
                for item in old_table.get("columns", []) if item.get("column_id")
            }
            for item in new_table.get("columns", []):
                cid = str(item.get("column_id") or "")
                before = str(old_columns.get(cid, {}).get("data_type") or "")
                after = str(item.get("data_type") or "")
                if before and after and before != after:
                    changes.append(
                        f"<li><b>{html.escape(str(item.get('column_name') or cid))} datatype</b>: "
                        f"{html.escape(before)} → {html.escape(after)}</li>"
                    )

            def active_rules(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
                return {
                    str(item.get("guardrail_rule_id") or item.get("rule_id") or ""): item
                    for item in doc.get("guardrails", []) if item.get("is_active", True)
                }
            old_rules, new_rules = active_rules(saved_payload), active_rules(payload)
            added = [rule for key, rule in new_rules.items() if key not in old_rules]
            removed = [rule for key, rule in old_rules.items() if key not in new_rules]
            changed = [
                rule for key, rule in new_rules.items()
                if key in old_rules and rule != old_rules[key]
            ]
            if added:
                changes.append(f"<li><b>Guardrails</b>: +{len(added)} enabled configuration(s)</li>")
            if removed:
                changes.append(f"<li><b>Guardrails</b>: -{len(removed)} configuration(s)</li>")
            if changed:
                changes.append(f"<li><b>Guardrails</b>: {len(changed)} configuration(s) changed</li>")
            if not changes:
                return "<p style='color:#667085;'>No unsaved changes. Current draft matches the last save.</p>"
            return (
                "<div style='border-left:4px solid var(--form-accent);padding:10px 12px;background:#f5f9fd;'>"
                "<b>Changes since last save</b><ul style='margin-bottom:0;'>"
                + "".join(changes) + "</ul></div>"
            )

        current_summary = widgets.HTML(
            "<div style='color:#667085;font-size:12px;'>"
            "This is the complete contract that will replace the saved draft JSON.</div>"
        )
        change_preview = widgets.HTML()
        manifest_preview = widgets.HTML(
            value="",
            layout=widgets.Layout(width="100%", height="auto", overflow="visible"),
        )

        def refresh_review() -> None:
            nonlocal payload
            ensure_runtime_context()
            payload = refresh_manifest() or {}
            refreshed_sections = _manifest_sections(
                payload, column_profiles=runtime_context.get("column_profiles", {})
            )
            manifest_preview.value = refreshed_sections["Review"]
            change_preview.value = review_change_html()
        state["_refresh_review"] = refresh_review
        exact_json_content = widgets.HTML()
        exact_json = exact_json_content
        exact_json.layout.close()
        exact_json.layout = widgets.Layout(
            width="100%", min_width="0", max_width="100%",
            height="auto", overflow="visible",
        )
        refresh_review_base = refresh_review

        def refresh_review() -> None:
            refresh_review_base()
            exact_json_content.value = (
                "<details><summary>Exact JSON manifest</summary><pre>"
                + html.escape(_expose_manifest(payload))
                + "</pre></details>"
            )

        state["_refresh_review"] = refresh_review
        save_contract_button = None
        discard_contract_button = None
        discard_contract_confirm = None
        confirm_discard_contract = None
        cancel_discard_contract = None
        if editable:
            save_contract_button = widgets.Button(
                description="Save draft", button_style="primary",
                layout=widgets.Layout(width="auto", min_width="125px"),
            )
            discard_contract_button = widgets.Button(
                description="Discard",
                layout=widgets.Layout(width="auto", min_width="110px"),
                tooltip="Discard unsaved edits and return to the saved draft",
            )
            confirm_discard_contract = widgets.Button(
                description="Discard unsaved changes",
                button_style="danger",
            )
            confirm_discard_contract.add_class("fabricops-confirm-danger")
            cancel_discard_contract = widgets.Button(description="Cancel")
            discard_contract_confirm = widgets.VBox(
                [
                    widgets.HTML(
                        "<div><b>Discard unsaved Data Contract changes?</b><br>"
                        "The previously saved draft will remain unchanged.</div>"
                    ),
                    shared.action_row(
                        widgets,
                        [cancel_discard_contract, confirm_discard_contract],
                    ),
                ],
                layout=widgets.Layout(
                    width="100%", height="auto", overflow="visible",
                    display="none", gap="8px",
                ),
            )
            pending_engineering_review = any(
                str(rule.get("rule_type") or "") == "custom_expression"
                and rule.get("is_active", True)
                and bool(_parameters(rule).get("engineering_review_required", True))
                and str(_parameters(rule).get("engineering_review_status") or "pending").lower()
                != "approved"
                for rule in session_guardrails()
            )
            freeze_button = widgets.Button(
                description=f"Freeze v{row['contract_version']}…",
                disabled=pending_engineering_review,
                layout=widgets.Layout(width="auto", min_width="130px"),
                tooltip="Validate and make this version immutable; confirmation required",
            )
            freeze_confirm = widgets.VBox(layout=widgets.Layout(display="none"))
            freeze_cancel = widgets.Button(description="Cancel")
            freeze_confirm_message = widgets.HTML()
            freeze_confirm_button = widgets.Button(button_style="primary")
            freeze_confirm.children = (
                freeze_confirm_message,
                widgets.HBox(
                    [freeze_cancel, freeze_confirm_button],
                    layout=widgets.Layout(gap="8px"),
                ),
            )

            def save_contract_clicked(_button: Any) -> None:
                try:
                    save_data_contract_session()
                except (TypeError, ValueError, RuntimeError) as exc:
                    set_status(str(exc), error=True)

            def freeze_clicked(_button: Any) -> None:
                pending_review = any(
                    str(rule.get("rule_type") or "") == "custom_expression"
                    and rule.get("is_active", True)
                    and bool(_parameters(rule).get("engineering_review_required", True))
                    and str(_parameters(rule).get("engineering_review_status") or "pending").lower()
                    != "approved"
                    for rule in session_guardrails()
                )
                if pending_review:
                    set_status(
                        "Complete Engineering review for all active Custom Expression Data Quality rules before freezing.",
                        error=True,
                    )
                    return
                if state.get("dirty"):
                    freeze_confirm_message.value = (
                        f"<b>Save and freeze Data Contract v{row['contract_version']}?</b><br>"
                        "Your staged changes will be saved first, then this version will become immutable. "
                        "Further changes require a new contract version."
                    )
                    freeze_confirm_button.description = f"Save & Freeze v{row['contract_version']}"
                else:
                    freeze_confirm_message.value = (
                        f"<b>Freeze Data Contract v{row['contract_version']}?</b><br>"
                        "This version will become immutable. Further changes require a new contract version."
                    )
                    freeze_confirm_button.description = f"Freeze v{row['contract_version']}"
                freeze_confirm.layout.display = ""

            def freeze_cancel_clicked(_button: Any) -> None:
                freeze_confirm.layout.display = "none"

            @busy_action("Saving and freezing Data Contract…")
            def freeze_confirm_clicked(_button: Any) -> None:
                try:
                    freeze_confirm_button.disabled = True
                    if state.get("dirty"):
                        save_data_contract_session(return_to_selector_after=False)
                    freeze()
                    render()
                    set_status(f"Data Contract v{row['contract_version']} is FROZEN.")
                except (TypeError, ValueError, RuntimeError) as exc:
                    freeze_confirm_button.disabled = False
                    set_status(str(exc), error=True)

            def discard_contract_clicked(_button: Any) -> None:
                if has_pending_authoring_changes():
                    discard_contract_confirm.layout.display = ""
                    return
                try:
                    discard_data_contract_session(return_to_selector_after=True)
                except (ValueError, RuntimeError) as exc:
                    set_status(str(exc), error=True)

            def confirm_discard_contract_clicked(_button: Any) -> None:
                try:
                    discard_data_contract_session(return_to_selector_after=True)
                except (ValueError, RuntimeError) as exc:
                    set_status(str(exc), error=True)

            def cancel_discard_contract_clicked(_button: Any) -> None:
                discard_contract_confirm.layout.display = "none"
                set_status("Discard cancelled. Unsaved changes retained.", warning=True)

            save_contract_button.on_click(save_contract_clicked)
            discard_contract_button.on_click(discard_contract_clicked)
            confirm_discard_contract.on_click(confirm_discard_contract_clicked)
            cancel_discard_contract.on_click(cancel_discard_contract_clicked)
            freeze_button.on_click(freeze_clicked)
            freeze_cancel.on_click(freeze_cancel_clicked)
            freeze_confirm_button.on_click(freeze_confirm_clicked)
            sidebar_actions.children = (
                widgets.HTML("<b style='font-size:12px'>Contract actions</b>"),
                widgets.HBox([save_contract_button, discard_contract_button],
                    layout=widgets.Layout(width="100%", gap="8px", flex_flow="row wrap")),
                widgets.HTML("<div style='border-top:1px solid #e6eaef;margin:5px 0'></div>"),
                widgets.HBox([widgets.HTML("<span style='font-size:12px'><b>Finalize version</b><br>"
                    "<span style='color:#667085'>Validate and lock this version.</span></span>"), freeze_button],
                    layout=widgets.Layout(width="100%", gap="8px", align_items="center", justify_content="space-between")),
                discard_contract_confirm, freeze_confirm,
            )
            sidebar_actions.layout.display = ""
        else:
            sidebar_actions.children = (widgets.HTML("<p>Frozen contract: review only.</p>"),)
            sidebar_actions.layout.display = ""
        review_left = ()

        review_right = (
            widgets.VBox(
                [current_summary, change_preview, manifest_preview],
                layout=widgets.Layout(width="100%", gap="8px"),
            ),
            shared.form_section(
                widgets, title="Read / Write Guardrails",
                children=[guardrail_disclosure],
            ),
            shared.form_section(
                widgets,
                title="Exact JSON",
                children=[exact_json],
            ),
        )
        view_content["Review"] = (review_left, review_right)
        view_content["AI Usage"] = (
            (),
            (editor_ai_information, ai_usage_view),
        )
        nonlocal sidebar_content
        sidebar_content = (
            table_summary, table_context_accordion, sidebar_actions, table_exit_row,
            table_exit_confirm, operation_progress, status,
        )
        apply_view()

        state["_refresh_guardrail_sidebar"] = render_table_summary
        render_table_summary()
        # Show Table context immediately and load recorded metadata once.
        table_context_accordion.selected_index = 0

        state["_controls"].update({
            "table_description": table_description, "table_classification": table_classification,
            "managed_grain": managed_grain,
            "table_grain": table_grain, "row_key_columns": row_key_columns,
            "grain_enabled": grain_enabled, "grain_policy": grain_policy, "grain_profile_evidence": grain_profile_evidence,
            "grain_ai": grain_ai, "suggest_grain": suggest_grain, "accept_grain": accept_grain,
            "guardrail_sidebar": guardrail_sidebar, "guardrail_disclosure": guardrail_disclosure, "sidebar_groups": sidebar_groups,
            "table_context": table_context_accordion,
            "table_definition": table_definition,
            "table_guardrails": table_rules,
            "table_description_ai": table_description_ai,
            "accept_table_description": accept_table_description,
            "rerun_table_description": rerun_table_description,
            "column_search": column_search, "empty_column": empty_column,
            "column_select": column_select, "column_context": column_context,
            "column_header": column_header,
            "column_required_controls": column_required_controls,
            "column_definition": column_definition,
            "profile_context": profile_context, "column_description": column_description,
            "column_classification": column_classification, "required": required,
            "datatype_choice": datatype_choice, "column_option_style": column_option_style,
            "dq_panel": dq_panel, "dq_primary": dq_primary,
            "sensitive_enabled": sensitive_enabled, "sensitive_treatment": sensitive_treatment,
            "column_description_ai": column_description_ai,
            "accept_column_description": accept_column_description,
            "rerun_column_description": rerun_column_description,
            "pii_type": pii_type, "pii_reason": pii_reason,
            "sensitive_ai": sensitive_ai, "accept_sensitive": accept_sensitive,
            "rerun_sensitive": rerun_sensitive,
            "mask_mode": mask_mode, "treatment_help": treatment_help,
            "bucket_mode": bucket_mode, "bucket_width": bucket_width, "bucket_origin": bucket_origin,
            "mask_start": mask_start,
            "mask_end": mask_end, "mask_character": mask_character,
            "bucket_bins": bucket_bins, "bucket_labels": bucket_labels,
            "dq_family_controls": dq_family_controls,
            "dq_parameter_controls": dq_parameter_controls,
            "dq_completeness_failure": dq_completeness_failure, "dq_blank_missing": dq_blank_missing,
            "dq_uniqueness_failure": dq_uniqueness_failure,
            "dq_whitelist_max_failure": dq_whitelist_max_failure, "dq_range_max_failure": dq_range_max_failure,
            "dq_whitelist_values": dq_whitelist_values,
            "dq_blacklist_values": dq_blacklist_values,
            "dq_whitelist_count": dq_whitelist_count,
            "dq_blacklist_count": dq_blacklist_count,
            "dq_minimum": dq_minimum, "dq_minimum_inclusive": dq_minimum_inclusive,
            "dq_maximum": dq_maximum, "dq_maximum_inclusive": dq_maximum_inclusive,
            "dq_enabled": dq_enabled, "dq_block": dq_block,
            "business_saved": business_saved,
            "business_requirement": business_requirement,
            "business_columns": business_columns,
            "business_ai_panel": business_ai_panel,
            "business_primary": business_primary,
            "business_review_actions": business_review_actions,
            "rule_reviewer": rule_reviewer,
            "business_enabled": business_enabled,
            "business_parameters": business_parameters,
            "business_tolerance": business_tolerance, "business_tolerance_hint": business_tolerance_hint,
            "business_block": business_block,
            "business_rule_controls": business_rule_controls,
            "business_proposal": business_proposal,
            "resolve_business_rule": resolve_business_rule,
            "apply_business_rule": apply_business_rule,
            "delete_business_rule": delete_business_rule,
            "delete_business_rule_confirm": delete_business_rule_confirm,
            "confirm_delete_business_rule": confirm_delete_business_rule,
            "cancel_delete_business_rule": cancel_delete_business_rule,
            "engineering_review_panel": engineering_review_panel,
            "engineering_review_status": engineering_review_status,
            "engineering_reviewer": engineering_reviewer,
            "engineering_review_note": engineering_review_note,
            "approve_engineering_review": approve_engineering_review,
            "current_dq_rules_section": current_rules_section,
            "rule_workspace_body": rule_workspace_body,
            "new_rule_editor": new_rule_editor,
            "manual_rule_editor": manual_rule_editor,
            "ai_rule_editor": ai_rule_editor,
            "manual_rule_type": manual_rule_type,
            "manual_apply_mode": manual_apply_mode,
            "manual_batch_columns": manual_batch_columns,
            "manual_key_columns": manual_key_columns,
            "manual_left_column": manual_left_column,
            "manual_right_column": manual_right_column,
            "manual_condition_column": manual_condition_column,
            "manual_target_column": manual_target_column,
            "manual_parameter_box": manual_parameter_box,
            "manual_preview": manual_preview,
            "manual_mode": manual_mode,
            "manual_values": manual_values,
            "manual_minimum": manual_minimum,
            "manual_maximum": manual_maximum,
            "manual_pattern": manual_pattern,
            "manual_operator": manual_operator,
            "manual_condition_operator": manual_condition_operator,
            "manual_condition_value": manual_condition_value,
            "manual_blank_missing": manual_blank_missing,
            "manual_expression": manual_expression,
            "manual_tolerance": manual_tolerance,
            "manual_enabled": manual_enabled,
            "manual_block": manual_block,
            "add_manual_rule": add_manual_rule,
            "review_parameter_box": review_parameter_box,
            "review_column": review_column,
            "review_key_columns": review_key_columns,
            "review_left_column": review_left_column,
            "review_right_column": review_right_column,
            "review_condition_column": review_condition_column,
            "review_target_column": review_target_column,
            "review_operator": review_operator,
            "manifest_preview": manifest_preview,
            "sidebar_actions": sidebar_actions,
            "save_data_contract": save_contract_button,
            "discard_data_contract": discard_contract_button,
            "discard_data_contract_confirm": discard_contract_confirm,
            "confirm_discard_data_contract": confirm_discard_contract,
            "cancel_discard_data_contract": cancel_discard_contract,
            "freeze": freeze_button if editable else None,
            "freeze_confirm": freeze_confirm_button if editable else None,
        })

        def refresh_ai_controls() -> None:
            available = editable and ai_available()
            render_table_ai()
            render_column_ai(str(column_select.value or ""))
            suggest_grain.disabled = not available
            accept_grain.disabled = not (available and ai_state["table"].get("grain_key"))
            resolve_business_rule.disabled = not available

        state["_refresh_ai_controls"] = refresh_ai_controls
        editor_roots = [node for panes in view_content.values() for pane in panes for node in pane]
        editor_roots.extend([table_summary, table_context_accordion, *sidebar_actions.children])
        # Conditional fields may be unmounted, but their comms still need closing.
        editor_roots.extend([
            sensitive_ai_panel, business_advanced, business_rule_controls,
            business_proposal_select, review_mode, review_values,
            review_minimum, review_maximum, review_minimum_inclusive, review_maximum_inclusive,
            review_pattern, review_condition_operator, review_condition_value,
            review_blank_missing, review_expression, manual_minimum_inclusive, manual_maximum_inclusive,
        ])
        editor_roots.extend(value for key, value in state["_controls"].items()
                            if value is not previous_controls.get(key))

        def dispose_editor() -> None:
            close_sidebar_widgets(editor_roots, preserve=(
                table_exit_row, table_exit_confirm, editor_ai_information, ai_usage_view,
                contract_nav_row, top_nav, sidebar_actions, operation_progress, status, section_heading,
            ))
        state["_dispose_editor"] = dispose_editor

    def ai_information() -> Any:
        """Show effective settings before opt-in and inside the editor."""
        settings = state["ai_settings"]
        return widgets.HTML(
            "<div style='font:13px Segoe UI,system-ui,sans-serif;color:#243449;max-width:100%;overflow-wrap:anywhere;'>"
            "<strong>AI-assisted authoring</strong><br>Provider: Microsoft Fabric AI Functions<br>"
            f"Model: {html.escape(settings['model_deployment_name'])}; "
            f"Reasoning effort: {html.escape(settings['reasoning_effort'] or 'provider/model default')}; "
            f"Verbosity: {html.escape(settings['verbosity'] or 'provider/model default')}<br>"
            "Billing: Fabric capacity consumption. AI is optional; manual authoring remains available.<br>"
            f"{html.escape(ai_configuration_error)}<br>"
            "Availability depends on Microsoft's supported regions, tenant settings and eligible paid capacity. "
            "Stronger models and higher reasoning may increase consumption and latency."
            "<details><summary>Setup, consumption and stronger model example</summary>"
            "<p>Requires Runtime 2.0 and the tenant setting ‘Users can use Copilot and other features powered by Azure OpenAI’. "
            "Review all suggestions before accepting them. Opening and navigation make zero AI requests. Generate, Suggest and Re-run consume Fabric AI capacity only when requested.</p>"
            "<pre style='white-space:pre-wrap;'>widget_data_contract(\n"
            '    ai_model="gpt-5.1",\n    ai_reasoning_effort="high",\n    ai_verbosity="medium",\n)</pre>'
            "<p>Model calls use the Copilot and AI meter, reported as the AI Functions operation. "
            "Spark execution consumes capacity separately. Token statistics below are measured; AI capacity estimates use published token rates. "
            "Per-request CU consumption is not exposed by the documented PySpark stats interface; inspect exact consumption in the "
            "<a href='https://learn.microsoft.com/en-us/fabric/enterprise/metrics-app'>Fabric Capacity Metrics app</a>. "
            "See <a href='https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/billing'>Microsoft billing guidance</a> "
            "and <a href='https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/overview#prerequisites'>prerequisites</a>. "
            "The separate Copilot capacity allocation feature is distinct from AI Functions billing. "
            "Azure AI Foundry is a future option with separate Azure billing; this widget does not support it.</p>"
            "</details></div>", layout=widgets.Layout(width="100%", min_width="0"),
        )

    ai_usage_view = widgets.HTML()

    def refresh_ai_usage() -> None:
        """Display measured input/output totals separately from estimated AI capacity."""
        ai_usage_view.value = _ai_usage_html(state["ai_usage"])

    refresh_ai_usage()
    selector_ai_information = ai_information()
    editor_ai_information = ai_information()

    open_button = widgets.Button(
        description="Open Data Contract",
        button_style="primary",
        layout=widgets.Layout(width="220px"),
    )
    open_progress = widgets.HTML()

    def set_open_progress(label: str) -> None:
        """Show the active stage without estimating unknown Spark or AI duration."""
        open_progress.value = loading_html(label)
        operation_progress.value = open_progress.value

    ai_availability = widgets.HTML(
        html.escape(ai_configuration_error) if ai_configuration_error else "" if ai_enrichment.get("enabled") else
        "<span style='color:#666;font-size:12px;'>AI suggestions unavailable: disabled in 00_env_config.</span>"
    )
    change_table_button = widgets.Button(
        description="Exit",
        layout=widgets.Layout(width="120px"),
    )
    confirm_exit_discard = widgets.Button(
        description="Discard & exit",
        button_style="danger",
    )
    confirm_exit_discard.add_class("fabricops-confirm-danger")
    cancel_exit = widgets.Button(description="Cancel")
    table_exit_confirm = widgets.VBox(
        [
            widgets.HTML(
                "<div style='font-size:12px;line-height:1.5;text-align:center;'>"
                "<b>Discard unsaved changes?</b><br>"
                "<span style='color:#667085;'>Your staged Data Contract changes will be lost.</span>"
                "</div>"
            ),
            widgets.HBox(
                [cancel_exit, confirm_exit_discard],
                layout=widgets.Layout(width="100%", justify_content="center", gap="8px"),
            ),
        ],
        layout=widgets.Layout(
            width="100%", display="none", gap="8px", margin="8px 0 0 0"
        ),
    )
    table_exit_row = widgets.HBox(
        [change_table_button],
        layout=widgets.Layout(width="100%", justify_content="flex-end"),
    )
    selector_actions = widgets.VBox(
        [
            widgets.HBox(
                [open_button],
                layout=widgets.Layout(width="100%", justify_content="center", gap="12px"),
            ),
            ai_availability,
            open_progress,
        ],
        layout=widgets.Layout(width="100%", align_items="center", gap="8px", margin="16px 0 0 0"),
    )
    selector_panel = widgets.VBox(
        [selector, selector_ai_information, selector_actions, status],
        layout=widgets.Layout(width="100%", height="auto", overflow="visible", display=""),
    )
    selector_panel.add_class("fabricops-contract-selector")
    contract_nav_row = widgets.HBox(
        [top_nav],
        layout=widgets.Layout(
            width="100%", justify_content="flex-start", margin="0 0 8px 0",
        ),
    )
    contract_nav_row.add_class("fabricops-contract-nav-row")
    right_column.children = (contract_nav_row, right)
    editor_shell = widgets.VBox(
        [workspace],
        layout=widgets.Layout(width="100%", height="auto", overflow="visible", display="none", gap="7px"),
    )

    def refresh_table_options(*_args: Any) -> None:
        if state["_selector_refreshing"]:
            return
        options = contracts.dataset_selector_options(table_rows, file_rows, workspace_id=state.get("workspace_id"))
        eligible = [
            row for row in table_rows
            if str(row.get("table_id") or "") in options["tables"]
            and (
                not state.get("workspace_id")
                or str(row.get("workspace_id") or "") == str(state["workspace_id"])
            )
        ]
        rows_by_table_id: dict[str, dict[str, Any]] = {}
        for row in eligible:
            rows_by_table_id.setdefault(str(row["table_id"]), row)

        rows_by_table_id.update({row["source_id"]: row for row in file_rows})
        selected = str(state.get("pending_dataset_id") or "")
        state["pending_table_id"] = None if selected.startswith("file:") else selected or None
        state["pending_source_id"] = selected if selected.startswith("file:") else None
        state["_selector_refreshing"] = True
        try:
            table_control.refresh_rows(
                [
                    {"label": table_selector_label(rows_by_table_id[value]), "value": value}
                    for value in options["tables"] if value in rows_by_table_id
                ],
                selected if selected in options["tables"] else "",
            )
            workspaces = contracts.dataset_selector_options(table_rows, file_rows, table_id=selected)["workspaces"]
            labels = {str(row["workspace_id"]): str(row.get("_workspace_name") or row["workspace_id"]) for row in [*table_rows, *file_rows]}
            workspace_control.refresh_rows([{"label": f"{labels[value]} ({value})", "value": value} for value in workspaces],
                                           state.get("workspace_id") or "")
        finally:
            state["_selector_refreshing"] = False

    def table_changed(change: dict[str, Any]) -> None:
        if state["_selector_refreshing"]:
            return
        selected = str(change.get("new") or "")
        preferred = (
            str(state.get("pending_contract_version") or "")
            if change.get("initial") else ""
        )
        state["pending_dataset_id"] = selected or None
        state["pending_contract_version"] = None
        valid = contracts.dataset_selector_options(table_rows, file_rows, table_id=selected)["workspaces"]
        if state.get("workspace_id") not in valid:
            state["workspace_id"] = None
        refresh_table_options()
        matches = sorted(
            [row for row in state["contracts"] if str(row.get("source_id") or row.get("table_id") or "") == selected],
            key=lambda row: -int(row.get("contract_version") or 0),
        )
        rows = [{"label": f"v{row['contract_version']} · {str(row.get('status') or '').title()}",
                 "value": str(row["contract_version"])} for row in matches]
        if selected:
            rows.append({"label": "New Draft", "value": "new"})
        available = {row["value"] for row in rows}
        selected_contract = (
            preferred if preferred in available
            else str(matches[0]["contract_version"]) if matches
            else "new" if selected else ""
        )
        state["_selector_refreshing"] = True
        try:
            contract_control.refresh_rows(rows, selected_contract)
            state["pending_contract_version"] = (
                None if selected_contract in ("", "new") else int(selected_contract)
            )
        finally:
            state["_selector_refreshing"] = False

    def workspace_changed(change: dict[str, Any]) -> None:
        nonlocal active_workspace_id
        if state["_selector_refreshing"]:
            return
        selected = str(change.get("new") or "")
        state["workspace_id"] = selected or None
        active_workspace_id = selected or routing_workspace_id
        valid = contracts.dataset_selector_options(table_rows, file_rows, workspace_id=selected)["tables"]
        if state.get("pending_dataset_id") not in valid:
            state["pending_dataset_id"] = None
            state["pending_contract_version"] = None
        refresh_table_options()
        table_changed({"new": state.get("pending_dataset_id")})

    def contract_changed(change: dict[str, Any]) -> None:
        if state["_selector_refreshing"]:
            return
        value = change.get("new")
        state["pending_contract_version"] = None if value in (None, "", "new") else int(value)

    @busy_action("Opening Data Contract…")
    def open_selected() -> None:
        selected_table = str(state.get("pending_dataset_id") or "")
        selected_contract = contract_control.value
        if not selected_table or not selected_contract:
            set_status("Select a dataset and contract before opening.", error=True)
            return
        open_button.disabled = True
        set_open_progress(
            "Preparing a new Data Contract draft…" if selected_contract == "new"
            else "Selecting saved Data Contract version from governance metadata…"
        )
        try:
            if selected_contract == "new":
                if not state.get("workspace_id"):
                    raise ValueError("Select a workspace observation before creating a draft.")
                state["dataset_id"] = selected_table
                began = perf_counter()
                try:
                    new_draft()
                finally:
                    record_timing("Open: create draft / metadata", perf_counter() - began)
            else:
                began = perf_counter()
                try:
                    select(selected_table, int(selected_contract))
                finally:
                    record_timing("Open: select contract / metadata", perf_counter() - began)
            set_open_progress("Constructing Table, Columns, Data Quality and Review widget controls…")
            began = perf_counter()
            try:
                top_nav.value = "Table"
                render()
            finally:
                record_timing("Open: constructing editor controls", perf_counter() - began)
            set_open_progress("Mounting contract editor controls in notebook output…")
            selector_panel.children = tuple(child for child in selector_panel.children if child is not status)
            selector_panel.layout.display = "none"
            editor_shell.layout.display = ""
            open_progress.value = ""
            set_status(f"Data Contract v{state['contract_version']} opened.")
        except Exception as exc:
            open_progress.value = ""
            set_status(_format_widget_exception(exc, phase="editor render"), error=True)
        finally:
            open_button.disabled = False

    def return_to_selector(message: str) -> None:
        state["current"] = None
        state["manifest"] = None
        state["dataset_id"] = None
        state["table_id"] = None
        state["source_id"] = None
        state["contract_version"] = None
        editor_shell.layout.display = "none"
        selector_panel.layout.display = ""
        selector_panel.children = tuple(child for child in selector_panel.children if child is not status) + (status,)
        set_status(message)

    state["_return_to_selector"] = return_to_selector

    def change_table(_button: Any) -> None:
        if has_pending_authoring_changes():
            table_exit_confirm.layout.display = ""
            return
        return_to_selector("Select a dataset and contract.")

    def cancel_exit_clicked(_button: Any) -> None:
        table_exit_confirm.layout.display = "none"

    def confirm_exit_clicked(_button: Any) -> None:
        table_exit_confirm.layout.display = "none"
        if state.get("current"):
            discard_data_contract_session(return_to_selector_after=True)
        else:
            return_to_selector("Unsaved changes discarded. Select a dataset and contract.")

    open_button.on_click(lambda _button: open_selected())
    change_table_button.on_click(change_table)
    cancel_exit.on_click(cancel_exit_clicked)
    confirm_exit_discard.on_click(confirm_exit_clicked)

    refresh_table_options()
    if state.get("pending_dataset_id"):
        table_changed({"new": state["pending_dataset_id"], "initial": True})
    table_control.observe(table_changed, names="value")
    workspace_control.observe(workspace_changed, names="value")
    contract_control.observe(contract_changed, names="value")
    render()
    page = shared.form_page(
        widgets, title="Data Contract", tone="governance",
        description="Select, author, review, and freeze one governed dataset contract.",
        children=[selector_panel, editor_shell, timing_panel],
    )
    page.layout.height = "auto"
    page.layout.overflow = "visible"
    page.add_class("fabricops-data-contract")
    page.children[0].value += _CONTRACT_STYLE
    state["_controls"].update({
        "page": page, "selector_panel": selector_panel, "editor_shell": editor_shell,
        "contract_nav_row": contract_nav_row,
        "table": table_control, "table_search": table_selector["search"],
        "workspace_select": workspace_control, "workspace_search": workspace_selector["search"],
        "contract": contract_control, "contract_search": contract_selector["search"],
        "open": open_button, "open_progress": open_progress,
        "operation_progress": operation_progress,
        "selector_ai_information": selector_ai_information, "editor_ai_information": editor_ai_information,
        "ai_usage": ai_usage_view,
        "change_table": change_table_button,
        "table_exit_row": table_exit_row,
        "table_exit_confirm": table_exit_confirm,
        "confirm_exit_discard": confirm_exit_discard,
        "cancel_exit": cancel_exit,
    })
    startup.display(page)
    for phase in ("initialization", "spark_loading", "metadata_loading", "widget_construction"):
        if phase in startup.timings:
            record_timing("Startup: " + phase, startup.timings[phase])
    state["_startup_timings"] = startup.timings
    return state

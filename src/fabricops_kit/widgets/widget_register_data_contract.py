"""Public widget entrypoint for immutable Data Contract inventories."""

from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from datetime import datetime
import html
import json
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session, read_lakehouse_table_core, write_lakehouse_table_core
from fabricops_kit.widgets.shared import (
    action_row,
    checkbox_group,
    execution_log_section,
    form_grid,
    form_page,
    form_section,
    require_ipywidgets,
    widget_common,
)
from fabricops_kit.widgets import shared as _catalogue_browser


CONTRACT_TABLE = "METADATA_DATA_CONTRACT"
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"



def _parse_approved_usage_json(value: Any) -> list[str]:
    """Return approved usages from a JSON list without granting defaults."""
    try:
        selected = json.loads(str(value or "[]"))
    except json.JSONDecodeError as exc:
        raise ValueError("approved_usage_json must be a JSON list.") from exc
    if not isinstance(selected, list) or any(not isinstance(item, str) for item in selected):
        raise ValueError("approved_usage_json must be a JSON list of strings.")
    result: list[str] = []
    for item in selected:
        usage = item.strip()
        if usage and usage not in result:
            result.append(usage)
    return result


def _usage_label(value: str) -> str:
    """Return the checkbox label for a usage value."""
    return value.replace("_", " ").title()


def _agreement_approved_usages(agreement: dict[str, Any] | None, agreement_id: str | None) -> list[str]:
    """Resolve approved usages from the selected parent agreement state."""
    supplied = agreement or {}
    row = supplied
    if not str(agreement_id or "").strip() and "existing_record" in supplied:
        selected_id = str(getattr(supplied.get("existing_record"), "value", "") or "").strip()
        row = (supplied.get("existing_records_by_id") or {}).get(selected_id, {})
    return _parse_approved_usage_json(row.get("approved_usage_json"))


def _serialize_contract_approved_usages(selected: Any, parent_usages: list[str]) -> str:
    """Serialize contract usages after enforcing agreement inheritance."""
    selected_values = [str(value).strip() for value in (selected or []) if str(value).strip()]
    invalid = sorted(set(selected_values).difference(parent_usages))
    if invalid:
        raise ValueError(
            "Data Contract approved usages must be a subset of the parent Data Agreement approved usages. "
            "Invalid value(s): " + ", ".join(invalid)
        )
    ordered = [usage for usage in parent_usages if usage in selected_values]
    return json.dumps(ordered, separators=(",", ":"), ensure_ascii=False)

def _display_widget(value: Any) -> None:
    """Display a widget when the optional IPython runtime is available."""
    try:
        from IPython import display as ip
    except ModuleNotFoundError:
        return
    ip.display(value)


def _agreement_details(agreement: dict[str, Any] | None, agreement_id: str | None) -> tuple[str, str]:
    """Resolve the canonical ID and a readable label from supplied state only."""
    explicit = str(agreement_id or "").strip()
    supplied = agreement or {}
    row: dict[str, Any] = supplied
    resolved = explicit or str(supplied.get("agreement_id") or "").strip()
    if not resolved:
        selected = supplied.get("existing_record")
        selected_id = str(getattr(selected, "value", "") or "").strip()
        row = (supplied.get("existing_records_by_id") or {}).get(selected_id, {})
        resolved = str(row.get("agreement_id") or selected_id).strip()
    if not resolved:
        if "existing_record" in supplied:
            return "", ""
        raise ValueError("A valid agreement_id is required. Supply agreement_id or an agreement state with a selected agreement.")
    label = str(row.get("agreement_name") or supplied.get("agreement_name") or resolved).strip() or resolved
    return resolved, label


def _normalize_initial_ids(metadata_ids: Sequence[str] | None) -> list[str]:
    """Trim and de-duplicate optional initial identities in caller order."""
    if metadata_ids is None:
        return []
    if isinstance(metadata_ids, (str, bytes)):
        raise TypeError("metadata_ids must be a non-string sequence or None")
    result: list[str] = []
    for value in metadata_ids:
        key = str(value or "").strip()
        if key and key not in result:
            result.append(key)
    return result


def _commit_sort_value(value: Any) -> tuple[int, str]:
    """Return a comparable timestamp value that also handles test doubles."""
    if value is None:
        return (0, "")
    if isinstance(value, datetime):
        return (1, value.isoformat())
    return (1, str(value))


def _latest_catalogue_rows(catalogue, environment_name: str) -> list[dict[str, Any]]:
    """Return one deterministic latest observation per active-environment key."""
    from pyspark.sql import functions as F

    fields = [
        "metadata_table_key", "schema_fingerprint", "store_type", "layer",
        "schema_name", "table_name", "_committed_at",
    ]
    observed = [
        row.asDict(recursive=True)
        for row in catalogue.filter(F.col("environment_name") == environment_name).select(*fields).collect()
        if str(row["metadata_table_key"] or "").strip()
    ]
    latest: dict[str, dict[str, Any]] = {}
    for row in observed:
        key = str(row.get("metadata_table_key") or "").strip()
        rank = (
            _commit_sort_value(row.get("_committed_at")),
            str(row.get("schema_fingerprint") or ""),
            str(row.get("store_type") or ""),
            str(row.get("layer") or ""),
            str(row.get("schema_name") or ""),
            str(row.get("table_name") or ""),
        )
        current = latest.get(key)
        current_rank = (
            _commit_sort_value(current.get("_committed_at")),
            str(current.get("schema_fingerprint") or ""),
            str(current.get("store_type") or ""),
            str(current.get("layer") or ""),
            str(current.get("schema_name") or ""),
            str(current.get("table_name") or ""),
        ) if current else None
        if current_rank is None or rank > current_rank:
            latest[key] = row
    return [dict(latest[key], metadata_table_key=key) for key in sorted(latest)]


def _catalogue_schema_rows(
    catalogue,
    environment_name: str | None,
    metadata_table_key: str,
    schema_fingerprint: str,
) -> list[dict[str, str]]:
    """Return one normalized catalogue schema without profiling measurements."""
    from pyspark.sql import functions as F

    if not metadata_table_key or not schema_fingerprint:
        return []
    matching = catalogue.filter(
        (F.col("metadata_table_key") == metadata_table_key)
        & (F.col("schema_fingerprint") == schema_fingerprint)
    )
    if environment_name is not None:
        matching = matching.filter(F.col("environment_name") == environment_name)
    rows = matching.select("metadata_column_key", "column_name", "data_type").collect()
    normalized = {
        (
            str(row["metadata_column_key"] or ""),
            str(row["column_name"] or ""),
            str(row["data_type"] or ""),
        ) for row in rows
    }
    result = [{
        "metadata_column_key": metadata_column_key,
        "column_name": column_name,
        "data_type": data_type,
    } for metadata_column_key, column_name, data_type in normalized]
    return sorted(result, key=lambda row: (
        row["column_name"].casefold(), row["metadata_column_key"], row["data_type"],
    ))


def _compare_schemas(
    contracted_schema: list[dict[str, str]],
    current_schema: list[dict[str, str]],
) -> dict[str, list[dict[str, Any]]]:
    """Compare schemas by stable column key and retain readable names."""
    contracted = {row["metadata_column_key"]: row for row in contracted_schema}
    current = {row["metadata_column_key"]: row for row in current_schema}
    shared = sorted(contracted.keys() & current.keys())
    unchanged: list[dict[str, Any]] = []
    changed_types: list[dict[str, Any]] = []
    renamed: list[dict[str, Any]] = []
    for key in shared:
        before, after = contracted[key], current[key]
        if before["data_type"] != after["data_type"]:
            changed_types.append({
                "metadata_column_key": key,
                "column_name": after["column_name"],
                "contracted_data_type": before["data_type"],
                "current_data_type": after["data_type"],
            })
        else:
            unchanged.append(dict(after))
        if before["column_name"] != after["column_name"]:
            renamed.append({
                "metadata_column_key": key,
                "contracted_column_name": before["column_name"],
                "current_column_name": after["column_name"],
            })
    return {
        "unchanged_columns": unchanged,
        "added_columns": [dict(current[key]) for key in sorted(current.keys() - contracted.keys())],
        "removed_columns": [dict(contracted[key]) for key in sorted(contracted.keys() - current.keys())],
        "changed_data_types": changed_types,
        "renamed_columns": renamed,
    }


def _short_key(key: str) -> str:
    """Return a deterministic compact identity for fallback labels."""
    return key if len(key) <= 12 else f"{key[:8]}…{key[-4:]}"


def _latest_inventory(memberships, agreement_id: str) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """Return the latest audit activity summary and its membership rows."""
    from pyspark.sql import functions as F

    rows = [
        row.asDict(recursive=True)
        for row in memberships.filter(F.col("agreement_id") == agreement_id).collect()
    ]
    if not rows:
        return None, []
    latest_row = max(rows, key=lambda row: (
        _commit_sort_value(row.get("_committed_at")),
        str(row.get("_activity_id") or ""),
    ))
    activity_id = str(latest_row.get("_activity_id") or "")
    activity_rows = [row for row in rows if str(row.get("_activity_id") or "") == activity_id]
    summary = {
        "activity_id": activity_id,
        "agreement_id": agreement_id,
        "committed_at": latest_row.get("_committed_at"),
        "linked_dataset_count": len({str(row.get("metadata_table_key") or "") for row in activity_rows}),
    }
    return summary, _deduplicate_memberships(activity_rows)


def _deduplicate_memberships(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return one membership row per logical dataset identity."""
    by_key: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get("metadata_table_key") or "").strip()
        if key and key not in by_key:
            by_key[key] = row
    return [by_key[key] for key in sorted(by_key)]


def _append_inventory(
    *,
    membership_rows: list[dict[str, Any]],
    target: str,
    schema: str | None,
    spark_session: Any,
    context: dict[str, Any],
) -> None:
    """Append one complete immutable inventory under shared audit fields."""
    registry = metadata_table_schema_registry()
    membership_frame = spark_session.createDataFrame(
        [coerce_metadata_row_types(CONTRACT_TABLE, row) for row in membership_rows],
        schema=registry[CONTRACT_TABLE],
    )
    write_lakehouse_table_core(
        membership_frame, CONTRACT_TABLE, target=target, schema=schema,
        mode="append", context=context,
    )


def widget_register_data_contract(
    *,
    agreement: dict[str, Any] | None = None,
    agreement_id: str | None = None,
    metadata_ids: Sequence[str] | None = None,
    target: str = "metadata",
    schema: str | None = None,
    spark_session=None,
    context=None,
):
    """Manage agreement tables and review schema and enrichment context.

    Parameters
    ----------
    agreement : dict, optional
        Agreement record or agreement-widget state used to resolve the
        canonical agreement ID and a readable label locally. When the supplied
        state exposes ``existing_record``, changing that selector reloads the
        latest inventory without rerunning the cell. The editor remains
        disabled while no saved agreement is selected.
    agreement_id : str, optional
        Explicit canonical agreement identity. A non-empty trimmed value takes
        precedence over ``agreement``.
    metadata_ids : sequence of str, optional
        Additional unsaved initial inventory identities. Valid active-
        environment identities extend the latest snapshot only in memory;
        unknown identities are reported and never written.
    target : str, default="metadata"
        Configured FabricStore target containing FabricOps metadata tables.
    schema : str, optional
        Metadata Lakehouse schema override.
    spark_session : object, optional
        Spark session override.
    context : object, optional
        Active FabricOps context override, normally created by
        ``00_env_config``.

    Returns
    -------
    dict
        Mutable inventory state containing ``latest_activity_id``,
        ``latest_committed_at``, editable membership identities,
        ``saved_activity_id``, ``get_rows``, ``get_snapshot``, and notebook
        controls under ``_controls``. ``dataset_reviews`` and
        ``get_schema_review`` expose the contracted and current fingerprints,
        complete structural schemas, differences, and display classifications
        without requiring callers to parse HTML. Activity and commit values come directly
        from the standard FabricOps audit fields rather than dedicated schema
        columns.

    Raises
    ------
    ValueError
        If no valid agreement ID can be resolved.
    TypeError
        If ``metadata_ids`` is not a non-string sequence.

    Notes
    -----
    Select an agreement, manage its allocated tables, and review each table's
    latest schema and enrichment context. This widget selects catalogue datasets covered by an agreement and freezes
    each current schema fingerprint in an immutable inventory snapshot. It
    resolves the actual contracted schema from historical catalogue rows,
    compares it with the current active-environment catalogue schema, and
    displays additive and breaking structural differences. Catalogue datasets
    appear once by logical ``metadata_table_key``; selecting one previews the
    exact latest active-environment schema and fingerprint before it is added.
    Each explicit save
    records the currently displayed schema version in the data contract, builds the FabricOps audit fields
    once and appends the complete current membership list. ``_activity_id``
    groups the save and ``_committed_at`` orders saves, while the widget displays
    only the latest inventory. Historical rows are never updated or deleted.
    Within each activity, ``agreement_id + metadata_table_key`` is unique and
    identifies exactly one recorded ``schema_fingerprint``.
    Catalogue discovery is restricted to the active environment, but logical
    ``metadata_table_key`` membership remains environment-independent.
    An unsaved agreement draft cannot create an inventory snapshot; select an
    existing agreement or save the new agreement first.

    Current and historically removed columns are shown in the detail panel;
    removed columns include their last-observed timestamp. Latest table- and
    column-level enrichment is resolved by canonical metadata keys and is
    strictly read-only. Maintain enrichment with
    ``widget_enrich_table_metadata``. Saving writes only contract membership
    and schema fingerprint metadata; it never writes enrichment records.
    Schema comparison is informational, and guardrails and guardrail results remain separate workflows.
    Granularity, semantic calculation changes, data quality, freshness,
    sensitivity, and PII are not enforced by this widget. This widget does not
    claim Open Data Contract Standard completeness.

    Examples
    --------
    >>> contract_state = widget_register_data_contract(
    ...     agreement=agreement_state,
    ...     target="metadata",
    ...     schema=METADATA_SCHEMA,
    ...     spark_session=spark,
    ... )
    >>> contract_state = widget_register_data_contract(
    ...     agreement_id="agreement-123",
    ...     metadata_ids=["table-key-1", "table-key-2"],
    ...     target="metadata",
    ...     schema=METADATA_SCHEMA,
    ...     spark_session=spark,
    ... )

    See Also
    --------
    widget_render_data_agreement
    widget_view_agreement_catalogue
    widget_enrich_table_metadata

    """
    resolved_agreement_id, agreement_label = _agreement_details(agreement, agreement_id)
    parent_approved_usages = _agreement_approved_usages(agreement, agreement_id)
    initial_ids = _normalize_initial_ids(metadata_ids)
    try:
        widgets = require_ipywidgets()
    except ModuleNotFoundError as exc:
        message = str(exc)
        print(f"Data Contract inventory unavailable: {message}")
        state: dict[str, Any] = {
            "agreement_id": resolved_agreement_id, "agreement_label": agreement_label,
            "environment_name": None, "latest_activity_id": None,
            "latest_committed_at": None, "available_metadata_ids": [],
            "inventory_metadata_ids": [], "inventory_count": 0,
            "unknown_initial_metadata_ids": initial_ids, "has_unsaved_changes": False,
            "saved_activity_id": None, "saved_metadata_ids": [], "error": message,
            "dataset_reviews": [], "contract_schema_will_change": False,
            "selected_dataset_review": None,
            "agreement_approved_usages": [], "approved_usages": [],
            "_controls": {},
        }
        state["get_rows"] = lambda: []
        state["get_snapshot"] = lambda: {"header": None, "memberships": []}
        state["get_schema_review"] = lambda: []
        state["get_selected_dataset_review"] = lambda: None
        return state

    config, env, resolved = resolve_fabric_context(context=context)
    spark_session = get_spark_session(spark_session)
    runtime_context = {"config": config, "env": env, **(resolved or {})}
    catalogue = read_lakehouse_table_core(
        CATALOGUE_TABLE, target=target, schema=schema,
        spark_session=spark_session, context=runtime_context,
    )
    catalogue_rows = _latest_catalogue_rows(catalogue, env)
    catalogue_history = [
        row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        for row in catalogue.collect()
    ] if hasattr(catalogue, "collect") else list(catalogue_rows)
    catalogue_history = [
        row for row in catalogue_history
        if str(row.get("environment_name") or env) == env
    ]
    rows_by_id = {row["metadata_table_key"]: row for row in catalogue_rows}
    shared_options = _catalogue_browser.catalogue_table_options(catalogue_history)
    all_options = [
        (str(option["label"]), str(option["metadata_table_key"]))
        for option in shared_options
    ]
    option_by_id = {key: label for label, key in all_options}
    enrichment_error = ""
    try:
        enrichment_rows = _catalogue_browser.read_enrichment_records(
            config, env, spark_session=spark_session,
        )
        current_enrichment = _catalogue_browser.latest_enrichment_values(enrichment_rows)
    except Exception as exc:
        current_enrichment = {}
        enrichment_error = f"Unable to read METADATA_ENRICHMENT: {exc}"
    memberships = read_lakehouse_table_core(
        CONTRACT_TABLE, target=target, schema=schema,
        spark_session=spark_session, context=runtime_context,
    )
    latest_summary, latest_rows = (
        _latest_inventory(memberships, resolved_agreement_id)
        if resolved_agreement_id else (None, [])
    )
    latest_activity_id = str((latest_summary or {}).get("activity_id") or "") or None
    saved_contract_usages = _parse_approved_usage_json(latest_rows[0].get("approved_usage_json")) if latest_rows else []
    saved_ids = [str(row["metadata_table_key"]) for row in latest_rows]
    valid_initial_ids = [key for key in initial_ids if key in rows_by_id]
    inventory_ids = (
        list(dict.fromkeys([*saved_ids, *valid_initial_ids]))
        if resolved_agreement_id else []
    )
    unknown_ids = [key for key in initial_ids if key not in rows_by_id]

    search = widgets.Text(value="", placeholder="Search catalogue...", **widget_common(widgets, "Search catalogue"))
    available = widgets.Select(options=[], **widget_common(widgets, "Add datasets"))
    add = widgets.Button(description="Add table to contract")
    inventory = widgets.Select(options=[], **widget_common(widgets, "Existing inventory"))
    remove = widgets.Button(description="Remove selected dataset")
    approved_usage_checkboxes: dict[str, Any] = {}
    approved_usage_box = widgets.VBox([])
    save = widgets.Button(description="Save inventory", button_style="primary")
    summary = widgets.HTML(value="")
    selected_schema = widgets.HTML(value="<i>Select a catalogue dataset to review its current schema.</i>")
    contract_schema_warning = widgets.HTML(value="")
    status = widgets.HTML(value="")
    execution_output = widgets.Output()
    agreement_text = widgets.HTML(value=f"<b>Parent Data Agreement:</b> {html.escape(agreement_label or 'Select an agreement')}")
    environment_text = widgets.HTML(value=f"<b>Environment:</b> {html.escape(env)}")

    state: dict[str, Any] = {
        "agreement_id": resolved_agreement_id or None, "agreement_label": agreement_label,
        "environment_name": env, "latest_activity_id": latest_activity_id,
        "latest_committed_at": (latest_summary or {}).get("committed_at"),
        "available_metadata_ids": [key for _label, key in all_options],
        "inventory_metadata_ids": inventory_ids, "inventory_count": len(inventory_ids),
        "unknown_initial_metadata_ids": unknown_ids,
        "has_unsaved_changes": inventory_ids != saved_ids,
        "saved_activity_id": None, "saved_metadata_ids": [],
        "dataset_reviews": [], "contract_schema_will_change": False,
        "selected_dataset_review": None,
        "enrichment_read_error": enrichment_error,
        "pending_additions": [key for key in inventory_ids if key not in saved_ids],
        "pending_removals": [],
        "agreement_approved_usages": list(parent_approved_usages),
        "approved_usages": [usage for usage in saved_contract_usages if usage in parent_approved_usages],
    }
    agreement_drafts: dict[str, list[str]] = {}

    def readable_label(key: str) -> str:
        return option_by_id.get(key, f"Unavailable catalogue dataset — {_short_key(key)}")

    def build_dataset_review(key: str) -> dict[str, Any]:
        contracted_by_id = {str(row["metadata_table_key"]): row for row in latest_rows}
        contracted_fingerprint = str(
            contracted_by_id.get(key, {}).get("schema_fingerprint") or ""
        ) or None
        try:
            browser_state = _catalogue_browser.catalogue_table_browser_state(
                catalogue_history, key, current_enrichment,
            )
        except ValueError:
            browser_state = None
        current_fingerprint = (
            str(browser_state.get("latest_schema_fingerprint") or "") or None
            if browser_state else None
        )
        contracted_schema = _catalogue_schema_rows(
            catalogue, None, key, contracted_fingerprint or "",
        )
        current_schema = _catalogue_schema_rows(
            catalogue, env, key, current_fingerprint or "",
        )
        difference = _compare_schemas(contracted_schema, current_schema)
        if current_fingerprint is None:
            schema_status = "Unavailable in current catalogue"
        elif contracted_fingerprint is None:
            schema_status = "New"
        elif difference["removed_columns"] or difference["changed_data_types"]:
            schema_status = "Breaking schema change"
        elif difference["added_columns"]:
            schema_status = "Additive schema change"
        elif contracted_fingerprint != current_fingerprint:
            schema_status = "Schema fingerprint changed"
        else:
            schema_status = "Unchanged"
        return {
            "metadata_table_key": key,
            "dataset_label": readable_label(key),
            "contracted_fingerprint": contracted_fingerprint,
            "current_fingerprint": current_fingerprint,
            "contracted_schema": contracted_schema,
            "current_schema": current_schema,
            "schema_diff": difference,
            "schema_status": schema_status,
            "contract_schema_will_change": bool(
                contracted_fingerprint and current_fingerprint
                and contracted_fingerprint != current_fingerprint
            ),
            "catalogue_browser_state": deepcopy(browser_state),
            "latest_schema_timestamp": (
                browser_state.get("latest_schema_timestamp") if browser_state else None
            ),
            "current_columns": deepcopy(browser_state.get("current_columns", [])) if browser_state else [],
            "removed_columns": deepcopy(browser_state.get("removed_columns", [])) if browser_state else [],
            "table_enrichment": deepcopy(
                browser_state.get("current_enrichment_values", {}).get("table", {})
            ) if browser_state else {},
        }

    def build_dataset_reviews(current: list[str]) -> list[dict[str, Any]]:
        return [build_dataset_review(key) for key in current]

    def render_schema(review: dict[str, Any], field: str) -> str:
        rows = review[field]
        if not rows:
            return "<i>Not available</i>"
        body = "".join(
            f"<tr><td>{html.escape(row['column_name'])}</td>"
            f"<td>{html.escape(row['data_type'])}</td>"
            f"<td><code>{html.escape(_short_key(row['metadata_column_key']))}</code></td></tr>"
            for row in rows
        )
        return (
            "<div style='max-height:180px;overflow:auto'><table style='width:100%;font-size:12px'>"
            "<thead><tr><th>Column</th><th>Type</th><th>Key</th></tr></thead>"
            f"<tbody>{body}</tbody></table></div>"
        )

    def render_review(review: dict[str, Any]) -> str:
        difference = review["schema_diff"]
        contracted = html.escape(review["contracted_fingerprint"] or "Not available")
        current = html.escape(review["current_fingerprint"] or "Not available")

        def difference_rows(field: str, label: str) -> str:
            rows = difference[field]
            if not rows:
                return ""
            def type_label(row: dict[str, Any]) -> str:
                if field == "changed_data_types":
                    return (
                        f"{row['contracted_data_type']} → {row['current_data_type']}"
                    )
                return str(row.get("data_type") or "")
            values = "".join(
                f"<li><code>{html.escape(row['column_name'])}</code> — "
                f"{html.escape(type_label(row))}</li>"
                for row in rows
            )
            return f"<b>{label}</b><ul style='margin-top:2px'>{values}</ul>"

        differences = "".join([
            difference_rows("added_columns", "Added"),
            difference_rows("removed_columns", "Removed"),
            difference_rows("changed_data_types", "Changed data types"),
        ])
        if not differences:
            differences = (
                "<b>Schema difference:</b> The fingerprint changed, but the available "
                "catalogue rows do not expose the precise difference."
                if review["schema_status"] == "Schema fingerprint changed"
                else "<b>Schema difference:</b> No structural differences"
            )
        return (
            "<div style='border:1px solid #ddd;padding:12px'>"
            f"<h4 style='margin-top:0'>{html.escape(review['dataset_label'])}</h4>"
            f"<b>Status:</b> {html.escape(review['schema_status'])}<br>"
            f"<b>Contracted fingerprint:</b> <code title='{contracted}'>"
            f"{html.escape(_short_key(contracted))}</code><br>"
            f"<b>Current fingerprint:</b> <code title='{current}'>"
            f"{html.escape(_short_key(current))}</code><br>"
            f"<b>Current columns:</b> {len(review['current_schema'])}<br><br>"
            f"{differences}<br><b>Current schema to record</b>"
            f"{render_schema(review, 'current_schema')}"
            + (
                f"<br><b>Contracted schema</b>{render_schema(review, 'contracted_schema')}"
                if review["contracted_fingerprint"] else ""
            )
            + "<hr><h4>Catalogue context</h4>"
            + (
                _catalogue_browser.render_read_only_catalogue_detail(
                    review["catalogue_browser_state"]
                ) if review["catalogue_browser_state"] else
                "<i>Latest catalogue schema is unavailable.</i>"
            )
            + "</div>"
        )

    def select_review(key: str) -> None:
        key = str(key or "")
        review = build_dataset_review(key) if key else None
        state["selected_dataset_review"] = review
        selected_schema.value = (
            render_review(review) if review else
            "<i>Select a catalogue or inventory dataset to review its schema.</i>"
        )

    def selected_approved_usages() -> list[str]:
        return [usage for usage, checkbox in approved_usage_checkboxes.items() if checkbox.value]

    def refresh_usage_options() -> None:
        allowed = list(state.get("agreement_approved_usages") or [])
        current = selected_approved_usages() or list(state.get("approved_usages") or [])
        current = [usage for usage in current if usage in allowed]
        approved_usage_checkboxes.clear()
        approved_usage_checkboxes.update({
            usage: widgets.Checkbox(value=usage in current, description=_usage_label(usage))
            for usage in allowed
        })
        approved_usage_box.children = (
            checkbox_group(widgets, label="Approved usages", checkboxes=approved_usage_checkboxes.values()),
        )
        state["approved_usages"] = current

    def refresh_controls(*_args: Any) -> None:
        refresh_usage_options()
        current = list(state["inventory_metadata_ids"])
        current_set = set(current)
        inventory.options = [(readable_label(key), key) for key in current]
        query = str(search.value or "").strip().casefold()
        choices = [
            option for option in all_options
            if option[1] not in current_set and (not query or query in option[0].casefold())
        ]
        available.options = choices
        available.value = None
        add.disabled = True
        state["inventory_count"] = len(current)
        state["has_unsaved_changes"] = current != saved_ids
        state["pending_additions"] = [key for key in current if key not in saved_ids]
        state["pending_removals"] = [key for key in saved_ids if key not in current_set]
        agreement_key = str(state.get("agreement_id") or "")
        if agreement_key and not state["has_unsaved_changes"]:
            agreement_drafts.pop(agreement_key, None)
        state["dataset_reviews"] = build_dataset_reviews(current)
        state["contract_schema_will_change"] = any(
            review["contract_schema_will_change"] for review in state["dataset_reviews"]
        )
        contract_schema_warning.value = (
            "<div style='padding:8px;border-left:4px solid #d97706'><b>Warning:</b> "
            "Saving records the currently displayed schema version in the data contract.</div>"
            if state["contract_schema_will_change"] else ""
        )
        summary.value = (
            f"<b>Current inventory count:</b> {len(current)}<br>"
            f"<b>Unsaved changes:</b> {'Yes' if state['has_unsaved_changes'] else 'No'}"
        )
        selected_key = str(inventory.value or available.value or "")
        select_review(selected_key)

    def set_editor_enabled(enabled: bool) -> None:
        for control in (search, available, inventory, remove, save):
            control.disabled = not enabled
        add.disabled = not enabled or available.value is None

    def load_agreement(selected_id: str) -> None:
        nonlocal latest_summary
        selected_id = str(selected_id or "").strip()
        previous_id = str(state.get("agreement_id") or "")
        if previous_id:
            previous_current = list(state["inventory_metadata_ids"])
            if previous_current == saved_ids:
                agreement_drafts.pop(previous_id, None)
            else:
                agreement_drafts[previous_id] = previous_current
        if not selected_id:
            latest_summary = None
            latest_rows.clear()
            saved_ids.clear()
            state.update(
                agreement_id=None, agreement_label="", latest_activity_id=None,
                latest_committed_at=None, inventory_metadata_ids=[],
                inventory_count=0, has_unsaved_changes=False,
                saved_activity_id=None, saved_metadata_ids=[],
                agreement_approved_usages=[], approved_usages=[],
            )
            agreement_text.value = "<b>Parent Data Agreement:</b> Select or save an agreement first"
            status.value = "Select an existing agreement or save a new agreement before maintaining its dataset inventory."
            set_editor_enabled(False)
            refresh_controls()
            return
        selected_row = (agreement or {}).get("existing_records_by_id", {}).get(selected_id, {})
        selected_label = str(selected_row.get("agreement_name") or selected_id).strip() or selected_id
        latest_summary, loaded_rows = _latest_inventory(memberships, selected_id)
        loaded_usage = _parse_approved_usage_json(loaded_rows[0].get("approved_usage_json")) if loaded_rows else []
        allowed_usage = _parse_approved_usage_json(selected_row.get("approved_usage_json"))
        activity_id = str((latest_summary or {}).get("activity_id") or "") or None
        latest_rows[:] = loaded_rows
        saved_ids[:] = [str(row["metadata_table_key"]) for row in loaded_rows]
        valid_initial = [key for key in initial_ids if key in rows_by_id]
        current = agreement_drafts.get(
            selected_id, list(dict.fromkeys([*saved_ids, *valid_initial])),
        )
        state.update(
            agreement_id=selected_id, agreement_label=selected_label,
            latest_activity_id=activity_id,
            latest_committed_at=(latest_summary or {}).get("committed_at"),
            inventory_metadata_ids=current, inventory_count=len(current),
            has_unsaved_changes=current != saved_ids,
            saved_activity_id=None, saved_metadata_ids=[],
            agreement_approved_usages=allowed_usage,
            approved_usages=[usage for usage in loaded_usage if usage in allowed_usage],
        )
        agreement_text.value = f"<b>Parent Data Agreement:</b> {html.escape(selected_label)}"
        status.value = (
            "Unsaved contract changes were preserved for the previous agreement."
            if previous_id and previous_id != selected_id and previous_id in agreement_drafts
            else ""
        )
        set_editor_enabled(True)
        refresh_controls()

    def add_selected(_button: Any = None) -> None:
        key = str(available.value or "")
        if key and key in rows_by_id and key not in state["inventory_metadata_ids"]:
            state["inventory_metadata_ids"].append(key)
        refresh_controls()

    def select_available(change: dict[str, Any]) -> None:
        if change.get("name") == "value":
            add.disabled = not bool(state.get("agreement_id") and change.get("new"))
            if change.get("new"):
                select_review(str(change["new"]))

    def select_inventory(change: dict[str, Any]) -> None:
        if change.get("name") == "value" and change.get("new"):
            select_review(str(change["new"]))

    def remove_selected(_button: Any = None) -> None:
        key = str(inventory.value or "")
        state["inventory_metadata_ids"] = [
            value for value in state["inventory_metadata_ids"] if value != key
        ]
        refresh_controls()

    def get_rows() -> list[dict[str, Any]]:
        frame = read_lakehouse_table_core(
            CONTRACT_TABLE, target=target, schema=schema,
            spark_session=spark_session, context=runtime_context,
        )
        _summary, rows = _latest_inventory(frame, str(state.get("agreement_id") or ""))
        return rows

    def get_snapshot() -> dict[str, Any]:
        if not state["latest_activity_id"]:
            return {"header": None, "memberships": []}
        frame = read_lakehouse_table_core(
            CONTRACT_TABLE, target=target, schema=schema,
            spark_session=spark_session, context=runtime_context,
        )
        summary, rows = _latest_inventory(frame, str(state["agreement_id"]))
        return {"header": summary, "memberships": rows}

    def get_schema_review() -> list[dict[str, Any]]:
        return deepcopy(state["dataset_reviews"])

    def get_selected_dataset_review() -> dict[str, Any] | None:
        return deepcopy(state["selected_dataset_review"])

    def save_inventory(_button: Any = None) -> None:
        nonlocal latest_summary
        if not state.get("agreement_id"):
            status.value = "Select or save an agreement before saving an inventory."
            return
        current = list(dict.fromkeys(state["inventory_metadata_ids"]))
        selected_usage_json = _serialize_contract_approved_usages(
            selected_approved_usages(), list(state.get("agreement_approved_usages") or [])
        )
        state["approved_usages"] = _parse_approved_usage_json(selected_usage_json)
        fingerprints_changed = any(
            str(rows_by_id.get(key, {}).get("schema_fingerprint") or "")
            != str(next((row.get("schema_fingerprint") for row in latest_rows if row.get("metadata_table_key") == key), ""))
            for key in current if key in saved_ids and key in rows_by_id
        )
        if current == saved_ids and not fingerprints_changed:
            state["has_unsaved_changes"] = False
            status.value = "No contract changes to save."
            return
        if not current:
            status.value = "An inventory save must contain at least one logical dataset."
            return
        invalid_new = [
            key for key in current
            if key not in saved_ids
            and not str(rows_by_id.get(key, {}).get("schema_fingerprint") or "")
        ]
        if invalid_new:
            status.value = "New datasets require a valid current catalogue schema fingerprint before saving."
            return
        audit = build_runtime_audit_fields(config=config, env=env, runtime_context=runtime_context)
        activity_id = str(audit["_activity_id"])
        saved_at = audit["_committed_at"]
        rows = [{
            "agreement_id": state["agreement_id"],
            "metadata_table_key": key,
            "schema_fingerprint": str(rows_by_id.get(key, {}).get("schema_fingerprint") or next(
                (row.get("schema_fingerprint") for row in latest_rows if row.get("metadata_table_key") == key), ""
            )),
            "approved_usage_json": selected_usage_json,
            **audit,
        } for key in current]
        clear = getattr(execution_output, "clear_output", None)
        if clear is not None:
            clear(wait=True)
        with execution_output:
            _append_inventory(
                membership_rows=rows, target=target, schema=schema,
                spark_session=spark_session, context=runtime_context,
            )
        latest_summary = {
            "activity_id": activity_id, "agreement_id": state["agreement_id"],
            "committed_at": saved_at, "linked_dataset_count": len(current),
        }
        latest_rows[:] = rows
        saved_ids[:] = current
        state.update(
            latest_activity_id=activity_id, latest_committed_at=saved_at,
            inventory_metadata_ids=list(current), inventory_count=len(current),
            has_unsaved_changes=False, saved_activity_id=activity_id,
            saved_metadata_ids=list(current),
            approved_usages=_parse_approved_usage_json(selected_usage_json),
            pending_additions=[], pending_removals=[],
        )
        refresh_controls()
        status.value = f"Saved inventory with {len(current)} logical datasets."

    search.observe(refresh_controls, names="value")
    available.observe(select_available, names="value")
    inventory.observe(select_inventory, names="value")
    add.on_click(add_selected)
    remove.on_click(remove_selected)
    save.on_click(save_inventory)
    agreement_selector = (agreement or {}).get("existing_record")
    if agreement_selector is not None and hasattr(agreement_selector, "observe"):
        agreement_selector.observe(
            lambda change: load_agreement(str(change.get("new") or ""))
            if change.get("name") == "value" else None,
            names="value",
        )
    state["get_rows"] = get_rows
    state["get_snapshot"] = get_snapshot
    state["get_schema_review"] = get_schema_review
    state["get_selected_dataset_review"] = get_selected_dataset_review
    state["_controls"] = {
        "agreement": agreement_text, "environment": environment_text,
        "summary": summary, "inventory": inventory, "remove": remove,
        "schema_review": selected_schema, "selected_schema": selected_schema,
        "contract_schema_warning": contract_schema_warning,
        "approved_usage_checkboxes": approved_usage_checkboxes,
        "approved_usage_box": approved_usage_box,
        "search": search, "available": available, "add": add, "save": save,
        "status": status, "execution_output": execution_output,
    }
    refresh_controls()
    set_editor_enabled(bool(state["agreement_id"]))
    if not state["agreement_id"]:
        status.value = "Select an existing agreement or save a new agreement before maintaining its dataset inventory."
    elif not all_options:
        status.value = (
            "No registered datasets are available in the active environment.<br>"
            "Historical inventory memberships remain available for removal or preservation."
        )

    relationship_section = form_section(
        widgets,
        title="Data Agreement → Data Contract → Authorised tables",
        children=[form_grid(widgets, [agreement_text, environment_text])],
    )
    details_section = form_section(
        widgets,
        title="Contract details",
        children=[summary, approved_usage_box, inventory, action_row(widgets, [remove]), contract_schema_warning],
    )
    catalogue_section = form_section(
        widgets,
        title="Related catalogue datasets",
        children=[
            search,
            widgets.HBox(
                [
                    widgets.VBox([available]),
                    widgets.VBox([action_row(widgets, [add])]),
                ],
                layout=widgets.Layout(
                    display="grid", grid_template_columns="minmax(240px, 1fr) minmax(360px, 2fr)",
                    gap="16px", align_items="flex-start",
                ),
            ),
        ],
    )
    actions = form_section(
        widgets, title="Save contract", children=[action_row(widgets, [save])]
    )
    log_section = execution_log_section(widgets, execution_output)
    result_section = form_section(
        widgets, title="Save result", children=[status, log_section]
    )
    landscape = widgets.HBox(
        [
            widgets.VBox([relationship_section, actions, result_section], layout=widgets.Layout(flex="1 1 25%", min_width="220px")),
            widgets.VBox([details_section, catalogue_section], layout=widgets.Layout(flex="1 1 30%", min_width="260px")),
            widgets.VBox([selected_schema], layout=widgets.Layout(flex="1 1 45%", min_width="320px", overflow="auto")),
        ],
        layout=widgets.Layout(display="flex", flex_flow="row wrap", gap="12px", align_items="stretch"),
    )
    container = form_page(
        widgets,
        title="Data Contract Creation Widget",
        description=(
            "Dataset-level delivery promise: records the tables authorised under the selected "
            "Data Agreement and the schema fingerprints associated with the registered "
            "contract inventory."
        ),
        children=[landscape],
    )
    state["_controls"].update(
        container=container,
        relationship_section=relationship_section,
        details_section=details_section,
        action_section=actions,
        result_section=result_section,
        execution_log_section=log_section,
    )
    _display_widget(container)
    return state

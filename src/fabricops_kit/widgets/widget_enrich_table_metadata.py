"""Public widget entrypoint for ``widget_enrich_table_metadata``."""

from __future__ import annotations

import html
import importlib
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import configured_lakehouse_schema, read_lakehouse_table_core
from fabricops_kit.widgets import shared as _enrichment


def _rows(value: Any) -> list[dict[str, Any]]:
    """Convert a Spark frame or iterable of row-like values to dictionaries."""
    source = value.collect() if hasattr(value, "collect") else value
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in (source or [])]


def _display_time(value: Any) -> str:
    """Return a compact notebook-friendly catalogue timestamp."""
    text = str(value or "").replace("T", " ")
    return text[:19] if text else "Unavailable"


def widget_enrich_table_metadata(
    *,
    spark_session: Any,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Browse catalogue history and maintain table or column enrichment.

    Select a logical table, browse its latest and historical columns, and
    maintain table- or column-level enrichment. Current columns are editable;
    columns absent from the latest schema fingerprint are shown as removed and
    remain read-only for historical reference.

    Parameters
    ----------
    spark_session : Any
        Fabric Spark session used to read the canonical catalogue and append
        enrichment records through the configured metadata target.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context initialized by
        ``00_env_config``.

    Returns
    -------
    dict[str, Any]
        Browser controls and the selected table state, draft store,
        ``build_records`` callback, and ``save`` callback.

    Raises
    ------
    ValueError
        If catalogue rows lack a canonical table or current-column metadata key.
    RuntimeError
        If catalogue or enrichment metadata cannot be read or written.

    Notes
    -----
    Table enrichment supports ``Description`` and ``Classification``. Column
    enrichment additionally supports ``Personal_identifier``. Existing values,
    including values removed from current dropdown configuration, are preserved.
    Saving appends only non-empty changed values to ``METADATA_ENRICHMENT``;
    repeated unchanged saves produce no write. This workflow is independent of
    guardrail target selection and keeps unsaved drafts in memory while open.

    Examples
    --------
    >>> browser = widget_enrich_table_metadata(spark_session=spark)
    >>> state = browser.get("selected_table_state", {})

    See Also
    --------
    widget_view_data_catalogue
        Browse catalogue profile evidence without editing enrichment.

    """
    config, env, resolved = resolve_fabric_context(context=context)
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    status = widgets.HTML(value="")
    runtime_context = {"config": config, "env": env, **resolved}
    try:
        catalogue = read_lakehouse_table_core(
            _enrichment.CATALOGUE_TABLE,
            target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            context=runtime_context,
            spark_session=spark_session,
        )
        catalogue_rows = _rows(catalogue)
    except Exception as exc:
        raise RuntimeError(f"Unable to read METADATA_DATA_CATALOGUE: {exc}") from exc
    try:
        enrichment_rows = _enrichment.read_enrichment_records(config, env, spark_session=spark_session)
    except Exception as exc:
        raise RuntimeError(f"Unable to read METADATA_ENRICHMENT: {exc}") from exc

    table_options = _enrichment.catalogue_table_options(catalogue_rows)
    if not catalogue_rows:
        raise ValueError("METADATA_DATA_CATALOGUE has no catalogue rows available.")
    if not table_options:
        raise ValueError("METADATA_DATA_CATALOGUE has no logical tables with metadata_table_key.")
    current_values = _enrichment.latest_enrichment_values(enrichment_rows)
    classification_options, personal_options, _, _ = _enrichment.enrichment_control_options(config)
    drafts: dict[tuple[str, str], dict[str, str]] = {}
    originals: dict[tuple[str, str], dict[str, str]] = {}
    selected: dict[str, Any] = {"table_key": "", "item_token": ""}
    state_holder: dict[str, Any] = {}
    detail_state = {"is_rendering": False}

    def pane_layout(basis: str) -> Any:
        return widgets.Layout(
            flex=f"1 1 {basis}", min_width="220px", max_width="100%", overflow="auto", height="560px"
        )
    table_search = widgets.Text(description="Search tables", placeholder="Table, layer, schema, environment…", layout=widgets.Layout(width="100%"))
    table_select = widgets.Select(options=[], description="Logical table", layout=widgets.Layout(width="100%", height="360px"))
    table_summary = widgets.HTML(value="")
    fingerprint_summary = widgets.HTML(value="")
    column_search = widgets.Text(description="Search columns", placeholder="Column name or type…", layout=widgets.Layout(width="100%"))
    column_select = widgets.Select(options=[], description="Table / columns", layout=widgets.Layout(width="100%", height="390px"))
    detail_title = widgets.HTML(value="")
    technical_detail = widgets.HTML(value="")
    description = widgets.Textarea(description="Description", rows=5, layout=widgets.Layout(width="100%"))
    classification = widgets.Dropdown(description="Classification", options=[""], layout=widgets.Layout(width="100%"))
    personal = widgets.Dropdown(description="Personal identifier", options=[""], layout=widgets.Layout(width="100%"))
    save_button = widgets.Button(description="Save enrichment", button_style="success")
    unsaved = widgets.HTML(value="")
    controls = {"Description": description, "Classification": classification, "Personal_identifier": personal}

    def selected_identity() -> tuple[str, str]:
        token = str(selected.get("item_token") or "")
        level, _, key = token.partition(":")
        return level, key

    def values_from_controls(level: str) -> dict[str, str]:
        names = ("Description", "Classification") if level == "table" else ("Description", "Classification", "Personal_identifier")
        return {name: str(controls[name].value or "") for name in names}

    def remember_draft(*_: Any) -> None:
        if detail_state["is_rendering"]:
            return
        level, key = selected_identity()
        if not level or not key or controls["Description"].disabled:
            return
        drafts[(level, key)] = values_from_controls(level)
        changed = drafts[(level, key)] != originals.get((level, key), {})
        unsaved.value = "<b>Unsaved changes</b>" if changed else ""

    def options_with_current(configured: list[str], current: str) -> list[str]:
        return ["", *dict.fromkeys([*[str(value) for value in configured if str(value)], *([current] if current else [])])]

    def render_detail(*_: Any) -> None:
        token = str(column_select.value or "")
        if not token:
            return
        selected["item_token"] = token
        level, key = selected_identity()
        browser = state_holder["state"]
        if level == "table":
            item = {"column_name": browser["table_name"], "status": "current", "data_type": ""}
            loaded = browser["current_enrichment_values"]["table"]
        else:
            item = next(row for row in browser["all_historical_columns"] if row["metadata_column_key"] == key)
            loaded = item["enrichment_values"]
        originals.setdefault((level, key), dict(loaded))
        values = drafts.get((level, key), originals[(level, key)])
        removed = item["status"] == "removed"
        detail_title.value = f"<h3>{html.escape(str(item['column_name'] or browser['table_name']))}</h3>"
        technical_detail.value = (
            f"<small><b>Level:</b> {level} · <b>Metadata key:</b> {html.escape(str(key))}"
            + (f" · <b>Data type:</b> {html.escape(str(item['data_type']))} · <b>Status:</b> {item['status']}" if level == "column" else "")
            + "</small>"
        )
        detail_state["is_rendering"] = True
        try:
            description.value = values.get("Description", "")
            classification.options = options_with_current(classification_options, values.get("Classification", ""))
            classification.value = values.get("Classification", "")
            personal.options = options_with_current(personal_options, values.get("Personal_identifier", ""))
            personal.value = values.get("Personal_identifier", "")
            personal.layout.display = "none" if level == "table" else ""
            for control in controls.values():
                control.disabled = removed
            save_button.disabled = removed
        finally:
            detail_state["is_rendering"] = False
        if removed:
            unsaved.value = "This column is not part of the latest schema. Existing enrichment is shown for historical reference."
        else:
            unsaved.value = (
                "<b>Unsaved changes</b>"
                if (level, key) in drafts and drafts[(level, key)] != originals[(level, key)]
                else ""
            )

    def refresh_column_options(*_: Any) -> None:
        browser = state_holder.get("state")
        if not browser:
            return
        query = str(column_search.value or "").strip().casefold()
        options = [(f"▣ {browser['table_name']} (Table)", f"table:{browser['metadata_table_key']}")]
        for row in browser["all_historical_columns"]:
            haystack = f"{row['column_name']} {row['data_type']} {row['status']}".casefold()
            if query and query not in haystack:
                continue
            suffix = "Current" if row["status"] == "current" else f"Removed · last observed {_display_time(row['last_observed_at'])}"
            options.append((f"{'●' if row['status'] == 'current' else '○'} {row['column_name']} — {row['data_type']} — {suffix}", f"column:{row['metadata_column_key']}"))
        previous = str(selected.get("item_token") or "")
        column_select.options = options
        available = [value for _, value in options]
        column_select.value = previous if previous in available else options[0][1]
        render_detail()

    def select_table(*_: Any) -> None:
        key = str(table_select.value or "")
        if not key:
            return
        selected["table_key"] = key
        selected["item_token"] = ""
        browser = _enrichment.catalogue_table_browser_state(catalogue_rows, key, current_values)
        state_holder.setdefault("state", {}).clear()
        state_holder["state"].update(browser)
        table_summary.value = f"<b>{html.escape(str(browser['table_name']))}</b><br><small>{html.escape(str(key))}</small>"
        fingerprint_summary.value = (
            f"<b>Latest schema fingerprint:</b> {html.escape(str(browser['latest_schema_fingerprint']))}<br>"
            f"<b>Recorded:</b> {_display_time(browser['latest_schema_timestamp'])} · "
            f"<b>Current:</b> {len(browser['current_columns'])} · <b>Removed:</b> {len(browser['removed_columns'])}"
        )
        refresh_column_options()

    spark_read_count = 1
    def filter_tables(*_: Any) -> None:
        query = str(table_search.value or "").strip().casefold()
        filtered = [row for row in table_options if not query or query in " ".join(str(value) for value in row.values()).casefold()]
        options = [(row["label"], row["metadata_table_key"]) for row in filtered]
        previous = str(selected.get("table_key") or "")
        table_select.options = options
        values = [value for _, value in options]
        table_select.value = previous if previous in values else (values[0] if values else None)
        if table_select.value:
            select_table()

    def build_records() -> list[dict[str, Any]]:
        remember_draft()
        level, key = selected_identity()
        if not level or not key:
            raise ValueError("The selected item is missing its canonical metadata key.")
        if controls["Description"].disabled:
            return []
        values = drafts.get((level, key), values_from_controls(level))
        before = originals.get((level, key), {})
        inputs = [
            {"enrichment_level": level, "metadata_key": key, "enrichment_type": name, "value": value}
            for name, value in values.items() if value.strip() and value != before.get(name, "")
        ]
        return _enrichment.build_enrichment_records(inputs, config=config, env=env)

    def save() -> dict[str, list[dict[str, Any]]]:
        records = build_records()
        if not records:
            status.value = "No enrichment changes to save."
            return {"enrichment_records": []}
        try:
            _enrichment.write_enrichment_records(records, config=config, env=env, spark_session=spark_session)
        except Exception as exc:
            status.value = f"Enrichment write failed: {html.escape(str(exc))}"
            return {"enrichment_records": []}
        level, key = selected_identity()
        original = originals[(level, key)]
        for record in records:
            original[record["enrichment_type"]] = record["value"]
            current_values[(level, key, record["enrichment_type"])] = dict(record)
        drafts[(level, key)] = dict(original)
        refreshed = _enrichment.catalogue_table_browser_state(catalogue_rows, selected["table_key"], current_values)
        state_holder["state"].clear()
        state_holder["state"].update(refreshed)
        status.value = f"Saved {len(records)} enrichment row(s) to METADATA_ENRICHMENT."
        unsaved.value = ""
        return {"enrichment_records": records}

    for control in controls.values():
        control.observe(remember_draft, names="value")
    table_search.observe(filter_tables, names="value")
    table_select.observe(select_table, names="value")
    column_search.observe(refresh_column_options, names="value")
    column_select.observe(render_detail, names="value")
    save_button.on_click(lambda _: save())
    filter_tables()

    left = widgets.VBox([widgets.HTML("<h3>Tables</h3>"), table_search, table_select, table_summary], layout=pane_layout("25%"))
    middle = widgets.VBox([widgets.HTML("<h3>Schema browser</h3>"), fingerprint_summary, column_search, column_select], layout=pane_layout("30%"))
    right = widgets.VBox([detail_title, technical_detail, description, classification, personal, save_button, unsaved, status], layout=pane_layout("45%"))
    page = widgets.VBox([
        widgets.HTML("<h2>Enrich table metadata</h2><p>Select a logical table, browse current and historical columns, and maintain enrichment.</p>"),
        widgets.HBox([left, middle, right], layout=widgets.Layout(width="100%", display="flex", flex_flow="row wrap", align_items="stretch", gap="12px")),
    ], layout=widgets.Layout(width="100%", overflow="visible"))
    ip.display(page)
    return {
        "table_options": table_options, "table_search": table_search, "table_selector": table_select,
        "column_search": column_search, "column_selector": column_select, "controls": controls,
        "selected_table_state": state_holder["state"], "drafts": drafts, "original_values": originals,
        "build_records": build_records, "save": save, "save_button": save_button, "status": status,
        "spark_read_count": spark_read_count, "page": page,
    }

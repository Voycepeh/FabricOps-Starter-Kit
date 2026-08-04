"""Public widget entrypoint for ``widget_enrich_table_metadata``."""

from __future__ import annotations

import importlib
from typing import Any, Mapping

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.widgets import shared as _enrichment


def widget_enrich_table_metadata(
    guardrail_state: Mapping[str, Any],
    *,
    spark_session: Any,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Render controls that append generic column enrichment values.

    Parameters
    ----------
    guardrail_state : Mapping[str, Any]
        Selected target state containing catalogue/profile column identities.
    spark_session : Any
        Fabric Spark session used to append enrichment records.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context.

    Returns
    -------
    dict[str, Any]
        Rendered controls plus ``build_records`` and ``save`` callbacks.

    Raises
    ------
    ValueError
        If the selected target has no column metadata identities.

    Notes
    -----
    Current values are loaded from ``METADATA_ENRICHMENT`` and prepopulated.
    Saving appends one row for each changed or new property and skips unchanged
    values. Empty inputs are skipped; clearing a current value is not supported
    by this pre-release model. Classification and personal-identifier controls
    use the configured governance options.

    Examples
    --------
    >>> state = {"catalogue_profile_rows": [{"column_name": "student_id", "metadata_column_key": "col_xyz"}]}
    >>> result = widget_enrich_table_metadata(state, spark_session=spark)

    """
    config, env, _ = resolve_fabric_context(context=context)
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    profile_rows = _enrichment._selected_catalogue_rows_for_enrichment(guardrail_state)
    if not profile_rows:
        raise ValueError("Selected target has no column metadata identities.")

    enrichment_rows = _enrichment.read_enrichment_records(config, env, spark_session=spark_session)
    current_values = _enrichment.latest_enrichment_values(enrichment_rows)
    classification_options, personal_identifier_options, _, _ = _enrichment.enrichment_control_options(config)
    property_labels = {
        "Description": "Description",
        "Classification": "Classification",
        "Personal_identifier": "Personal identifier",
    }
    row_controls = []
    panels = []

    def refresh_item_state(item: dict[str, Any]) -> None:
        for enrichment_type, control in item["values"].items():
            before = item["original_values"][enrichment_type]
            state = "changed" if before and control.value != before else "existing" if before else "new"
            item["states"][enrichment_type].value = f"<small>{state}</small>"

    for row in profile_rows:
        metadata_key = str(_enrichment._value(row, "metadata_column_key"))
        original = {
            enrichment_type: str(current_values.get(("column", metadata_key, enrichment_type), {}).get("value") or "")
            for enrichment_type in property_labels
        }
        classification_choices = list(dict.fromkeys([*classification_options, original["Classification"]]))
        personal_identifier_choices = list(dict.fromkeys([*personal_identifier_options, original["Personal_identifier"]]))
        classification_choices = [value for value in classification_choices if value]
        personal_identifier_choices = [value for value in personal_identifier_choices if value]
        controls = {
            "Description": widgets.Textarea(value=original["Description"], description=property_labels["Description"], rows=2, layout=widgets.Layout(width="600px")),
            "Classification": widgets.Dropdown(options=["", *classification_choices], value=original["Classification"], description=property_labels["Classification"], layout=widgets.Layout(width="600px")),
            "Personal_identifier": widgets.Dropdown(options=["", *personal_identifier_choices], value=original["Personal_identifier"], description=property_labels["Personal_identifier"], layout=widgets.Layout(width="600px")),
        }
        state_labels = {name: widgets.HTML(value="") for name in property_labels}
        item = {"metadata_key": metadata_key, "column_name": str(_enrichment._value(row, "column_name")), "values": controls, "original_values": original, "states": state_labels}

        def refresh_state(*_: Any, item: dict[str, Any] = item) -> None:
            refresh_item_state(item)

        for control in controls.values():
            control.observe(refresh_state, names="value")
        refresh_state()
        row_controls.append(item)
        field_rows = [widgets.VBox([controls[name], state_labels[name]]) for name in property_labels]
        panels.append(widgets.VBox([widgets.HTML(f"<b>{item['column_name']}</b>"), *field_rows]))

    status = widgets.HTML(value="")

    def build_records() -> list[dict[str, Any]]:
        inputs = [
            {"enrichment_level": "column", "metadata_key": item["metadata_key"], "enrichment_type": enrichment_type, "value": control.value}
            for item in row_controls
            for enrichment_type, control in item["values"].items()
            if control.value.strip() and control.value != item["original_values"][enrichment_type]
        ]
        return _enrichment.build_enrichment_records(inputs, config=config, env=env)

    def save() -> dict[str, list[dict[str, Any]]]:
        records = build_records()
        if not records:
            status.value = "No enrichment changes to save."
            return {"enrichment_records": []}
        _enrichment.write_enrichment_records(records, config=config, env=env, spark_session=spark_session)
        items_by_key = {item["metadata_key"]: item for item in row_controls}
        for record in records:
            item = items_by_key[record["metadata_key"]]
            item["original_values"][record["enrichment_type"]] = record["value"]
            refresh_item_state(item)
        status.value = f"Saved {len(records)} enrichment row(s) to METADATA_ENRICHMENT."
        return {"enrichment_records": records}

    save_button = widgets.Button(description="Save enrichment", button_style="success")
    save_button.on_click(lambda _: save())
    ip.display(widgets.VBox([widgets.HTML("<h3>Enrich table metadata</h3>"), *panels, save_button, status]))
    return {"rows": row_controls, "build_records": build_records, "save": save, "save_button": save_button, "status": status}

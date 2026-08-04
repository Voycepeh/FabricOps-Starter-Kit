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
    Each populated property is one append-only row. Empty inputs are skipped;
    clearing a current value is not supported by this pre-release model.

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

    property_labels = {
        "Business_context": "Business context",
        "Classification": "Classification",
        "Personal_identifier": "Personal identifier",
        "Business_name": "Business name",
    }
    row_controls = []
    panels = []
    for row in profile_rows:
        controls = {
            name: widgets.Textarea(value="", description=label, rows=2, layout=widgets.Layout(width="600px"))
            for name, label in property_labels.items()
        }
        item = {"metadata_key": str(_enrichment._value(row, "metadata_column_key")), "column_name": str(_enrichment._value(row, "column_name")), "values": controls}
        row_controls.append(item)
        panels.append(widgets.VBox([widgets.HTML(f"<b>{item['column_name']}</b>"), *controls.values()]))

    status = widgets.HTML(value="")

    def build_records() -> list[dict[str, Any]]:
        inputs = [
            {"enrichment_level": "column", "metadata_key": item["metadata_key"], "enrichment_type": enrichment_type, "value": control.value}
            for item in row_controls
            for enrichment_type, control in item["values"].items()
            if control.value.strip()
        ]
        return _enrichment.build_enrichment_records(inputs, config=config, env=env)

    def save() -> dict[str, list[dict[str, Any]]]:
        records = build_records()
        _enrichment.write_enrichment_records(records, config=config, env=env, spark_session=spark_session)
        status.value = f"Saved {len(records)} enrichment row(s) to METADATA_ENRICHMENT."
        return {"enrichment_records": records}

    save_button = widgets.Button(description="Save enrichment", button_style="success")
    save_button.on_click(lambda _: save())
    ip.display(widgets.VBox([widgets.HTML("<h3>Enrich table metadata</h3>"), *panels, save_button, status]))
    return {"rows": row_controls, "build_records": build_records, "save": save, "save_button": save_button, "status": status}

"""Review direct activation records and the pending Governed deployment gate."""
from __future__ import annotations

import html
from typing import Any

from fabricops_kit.activated_pipeline.shared import read_registry, registry_control, review_pipeline_activation, DEPLOYMENT_PENDING
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.widgets import shared


def widget_activate_pipeline(*, pipeline_id=None, context=None) -> dict[str, Any]:
    """Inspect workspace pipeline activations and independently activated Contracts.

    The previous Test/approval/version-selection lifecycle is removed. Migrated
    pipelines are requires_reactivation candidates, never verified deployments.
    Pipeline activation and Governed publication remain disabled until a tenant-
    proven trusted deployment mechanism is integrated. A Git SHA typed into a
    widget cannot satisfy this requirement.

    Parameters
    ----------
    pipeline_id : str | None, optional
        Filter pipeline records by stable logical UUIDv4.
    context : dict | None, optional
        Existing FabricOps context; central Metadata routing is preserved.

    Returns
    -------
    dict
        Widget, scoped activation records, reviewed control token and readiness
        reason. Opening the widget changes no metadata or publication authority.

    Raises
    ------
    ValueError
        If identity or the Registry is missing, corrupt or ambiguous.
    RuntimeError
        If notebook/Spark/widget services are unavailable.

    Examples
    --------
    >>> review = widget_activate_pipeline()
    >>> reviewed_token = review["token"]

    Notes
    -----
    Use activate_data_contract for independent frozen Contract activation after
    review. Tenant permissions must restrict governance writes to trusted actors.
    This inspection UI does not authenticate or attest a deployment.

    """
    startup = shared.WidgetStartup("Pipeline activation", tone="governance", reserved_height="360px")
    config, workspace, runtime = resolve_fabric_context(context=context)
    if pipeline_id is not None:
        from fabricops_kit.pipeline.shared import validate_pipeline_id
        pipeline_id = validate_pipeline_id(pipeline_id)
    spark = get_spark_session(context=runtime)
    with startup.phase("metadata_loading", "Loading direct activation records…"):
        rows = read_registry(context={**runtime, "config": config, "scope_workspace_id": workspace}, spark_session=spark)
    scoped = [row for row in rows if row.get("workspace_id") == workspace and (
        row["record_type"] == "table_contract_activation" or pipeline_id is None or row.get("pipeline_id") == pipeline_id)]
    reviews = {}
    for row in scoped:
        if row["record_type"] == "pipeline_activation":
            try:
                reviews[row["pipeline_id"]] = review_pipeline_activation(row,
                    context={**runtime, "config": config, "scope_workspace_id": workspace}, spark_session=spark)
            except ValueError as exc:
                reviews[row["pipeline_id"]] = {"ready": False, "blocking_conflicts": [str(exc), DEPLOYMENT_PENDING]}
    widgets = shared.require_ipywidgets()
    content = "<p>" + html.escape(DEPLOYMENT_PENDING) + "</p><table><thead><tr><th>Record type</th><th>Identity</th><th>Status</th></tr></thead><tbody>"
    for row in scoped:
        content += "<tr>" + "".join("<td>" + html.escape(str(value)) + "</td>" for value in (
            row["record_type"], row.get("pipeline_id") or row.get("table_id"), row["status"])) + "</tr>"
    content += "</tbody></table>"
    root = shared.form_page(widgets, title="Pipeline activation", tone="governance",
        description="Workspace pipeline deployments and independent Table ID Contracts.", children=[widgets.HTML(content)])
    startup.display(root)
    return {"widget": root, "records": scoped, "reviews": reviews, "token": registry_control(rows)["token"],
        "ready": False, "reason": DEPLOYMENT_PENDING}

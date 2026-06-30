"""Public widget entrypoint for selecting a data agreement."""

from __future__ import annotations

from typing import Any

from fabricops_kit.widgets.shared import select_agreement_widget_workflow



def widget_select_agreement(agreement_rows: Any = None, *, context: dict[str, Any] | None = None, spark_session: Any = None, metadata_schema: str | None = None, register_notebook: bool = False, notebook_type: str | None = None, environment_name: str | None = None, dataset_name: str | None = None, table_name: str | None = None, topic: str | None = None, pipeline_name: str | None = None) -> Any:
    """Render a downstream agreement selector and retain the selected row.

    Parameters
    ----------
    agreement_rows : iterable, optional
        Preloaded agreement rows. When omitted, agreements are loaded from the
        active ``FABRIC_CONTEXT`` initialized by ``00_env_config``.
    context : dict, optional
        Advanced override context. Defaults to the active ``FABRIC_CONTEXT``.
    spark_session : pyspark.sql.SparkSession, optional
        Fabric Spark session used for configured metadata-table reads.
    metadata_schema : str, optional
        Explicit metadata Lakehouse schema override. Pass ``METADATA_SCHEMA``
        from ``00_env_config`` in schema-enabled Lakehouses so agreement reads
        and notebook registration use the same metadata route.
    register_notebook : bool, default=False
        When True, render registration status and a button that links the
        current notebook to the selected agreement.
    notebook_type, environment_name, dataset_name, table_name, topic, pipeline_name : str, optional
        Workflow metadata passed to notebook registration when
        ``register_notebook`` is enabled.

    Returns
    -------
    ipywidgets.Select
        Displayed searchable latest-version agreement selector control.

    """
    return select_agreement_widget_workflow(
        agreement_rows=agreement_rows,
        context=context,
        spark_session=spark_session,
        metadata_schema=metadata_schema,
        register_notebook=register_notebook,
        notebook_type=notebook_type,
        environment_name=environment_name,
        dataset_name=dataset_name,
        table_name=table_name,
        topic=topic,
        pipeline_name=pipeline_name,
    )


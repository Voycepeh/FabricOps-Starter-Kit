# widget_select_agreement

**Module:** `data_agreement`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Render an agreement selector and optionally register the active notebook.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def widget_select_agreement(agreement_rows_or_config: Any, env_name: str | None=None, *, spark_session: Any=None, register_notebook: bool=False, notebook_type: str | None=None, environment_name: str | None=None, dataset_name: str | None=None, table_name: str | None=None, topic: str | None=None, pipeline_name: str | None=None) -> Any
```

## Parameters

agreement_rows_or_config : FrameworkConfig or iterable
    Pass ``CONFIG`` in normal notebooks, or provide preloaded agreement
    rows when the caller already has them available.
env_name : str, optional
    Environment key used to load agreements when ``CONFIG`` is supplied.
spark_session : pyspark.sql.SparkSession, optional
    Fabric Spark session used for configured metadata-table reads.
register_notebook : bool, default=False
    When True, render registration status and a button that links the
    current notebook to the selected agreement.
notebook_type, environment_name, dataset_name, table_name, topic, pipeline_name : str, optional
    Workflow metadata passed to ``_register_current_notebook`` when
    ``register_notebook`` is enabled.

## Returns

ipywidgets.Select
    Displayed searchable latest-version agreement selector control. Its
    ``value`` remains the stable ``agreement_id`` for existing callers.
    When registration is enabled, registration widgets are attached as
    attributes on the selector for advanced notebook automation.

## Raises

Not documented yet

## Side effects

Not documented yet

## FabricOps context

Starter template: `02_pipeline / optional 99_explore`; segment: `Agreement selection`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../internal/data_agreement__html_escape/"><code>fabricops_kit.data_agreement._html_escape</code></a>
- <a href="../internal/data_agreement__latest_agreement_versions/"><code>fabricops_kit.data_agreement._latest_agreement_versions</code></a>
- <a href="../internal/data_agreement__list_data_agreements/"><code>fabricops_kit.data_agreement._list_data_agreements</code></a>
- <a href="../internal/data_agreement__render_searchable_selector/"><code>fabricops_kit.data_agreement._render_searchable_selector</code></a>
- <a href="../internal/data_agreement__require_ipywidgets/"><code>fabricops_kit.data_agreement._require_ipywidgets</code></a>
- <a href="../internal/metadata__current_notebook_active_registrations/"><code>fabricops_kit.metadata._current_notebook_active_registrations</code></a>
- <a href="../internal/metadata__register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="../../api/modules/data_agreement/#widget_select_agreement">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.widget_select_agreement`
- Short name: `widget_select_agreement`
- Module: `data_agreement`
- Classification: Callable
- Related module: `data_agreement`
- Inbound references count: 0
- Outbound references count: 7

## Outbound references
- <a href="../internal/data_agreement__html_escape/"><code>fabricops_kit.data_agreement._html_escape</code></a>
- <a href="../internal/data_agreement__latest_agreement_versions/"><code>fabricops_kit.data_agreement._latest_agreement_versions</code></a>
- <a href="../internal/data_agreement__list_data_agreements/"><code>fabricops_kit.data_agreement._list_data_agreements</code></a>
- <a href="../internal/data_agreement__render_searchable_selector/"><code>fabricops_kit.data_agreement._render_searchable_selector</code></a>
- <a href="../internal/data_agreement__require_ipywidgets/"><code>fabricops_kit.data_agreement._require_ipywidgets</code></a>
- <a href="../internal/metadata__current_notebook_active_registrations/"><code>fabricops_kit.metadata._current_notebook_active_registrations</code></a>
- <a href="../internal/metadata__register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>

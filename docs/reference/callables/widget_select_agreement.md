# widget_select_agreement

**Module:** `data_agreement`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use in 02_pipeline or 99_explore notebooks to let a user select an approved data agreement before reading, profiling, or writing governed data.

## When not to use this

Do not use when an agreement has already been programmatically selected and validated, or for catalogue table review selection in 03_review.

## Quick example

widget_select_agreement(CONFIG, env="Sandbox", spark_session=spark)
agreement = get_selected_agreement()

## Signature

```python
def widget_select_agreement(agreement_rows_or_config: Any, env_name: str | None=None, *, spark_session: Any=None, register_notebook: bool=False, notebook_type: str | None=None, environment_name: str | None=None, dataset_name: str | None=None, table_name: str | None=None, topic: str | None=None, pipeline_name: str | None=None) -> Any
```

## Parameters

config, env, optional spark_session, and notebook registration options for loading agreement choices from metadata.

## Returns

Interactive widget state; call get_selected_agreement to retrieve the selected agreement record.

## Raises

Raises metadata read, widget dependency, or configuration errors when agreement metadata cannot be loaded.

## Side effects

Displays an IPython widget and may register the active notebook selection in metadata when requested.

## FabricOps context

Requires agreement metadata created through 01_agreement and metadata routing from 00_env_config.

## AI implementation contract

- **required_context:** Requires agreement metadata created through 01_agreement and metadata routing from 00_env_config.
- **inputs:** config, env, optional spark_session, and notebook registration options for loading agreement choices from metadata.
- **output:** Interactive widget state; call get_selected_agreement to retrieve the selected agreement record.
- **side_effects:** Displays an IPython widget and may register the active notebook selection in metadata when requested.
- **failure_modes:** Raises metadata read, widget dependency, or configuration errors when agreement metadata cannot be loaded.
- **verification:** Verify the user selected an agreement and call get_selected_agreement before generating pipeline code that depends on agreement context.

## Related functions

- <a href="../get_selected_agreement/"><code>fabricops_kit.data_agreement.get_selected_agreement</code></a>
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

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

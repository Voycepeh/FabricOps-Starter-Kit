# start_pipeline_run

Start a guided notebook run and store runtime defaults.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:63`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L63-L151">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use near the top of 02_pipeline or read-only exploration notebooks that need agreement-aware runtime defaults.

### Do not use when

- Do not use when an advanced custom notebook needs to pass every runtime parameter explicitly to lower-level helpers.

### Additional context

Resolves runtime and agreement context once so template notebooks can call guardrail and summary helpers with concise defaults.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def start_pipeline_run(
    notebook_type: str='02_pipeline',
    select_agreement: bool=False,
    register_notebook: bool=False,
    read_only: bool=False,
    run_context: Any=None,
    spark_session: Any=None,
    metadata_schema: str | None=None,
    pipeline_name: str | None=None,
    context: dict[str, Any] | None=None,
) -> Any:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
PIPELINE = start_pipeline_run(notebook_type="02_pipeline", select_agreement=True, register_notebook=True)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `notebook_type` | `str` | No | FabricOps notebook type to associate with the active context. |
| `select_agreement` | `bool` | No | When True, render the agreement selector and capture the selected agreement for downstream defaults. |
| `register_notebook` | `bool` | No | When True, allow ``widget_select_agreement`` to register this notebook to the selected agreement. Use ``False`` for read-only exploration. |
| `read_only` | `bool` | No | Marks the active context as read-only for exploratory notebooks. The startup helper itself does not write metadata unless ``register_notebook=True`` is explicitly requested. |
| `run_context` | `Any` | No | ``RUN_CONTEXT`` from ``00_env_config``. Defaults to the active notebook variable named ``RUN_CONTEXT``. |
| `spark_session` | `Any` | No | Spark session. Defaults to the active notebook variable named ``spark``. |
| `metadata_schema` | `str \| None` | No | ``METADATA_SCHEMA`` from ``00_env_config`` when schema routing is used. |
| `pipeline_name` | `str \| None` | No | Friendly pipeline name. Defaults to Fabric runtime notebook metadata. |
| `context` | `dict[str, Any] \| None` | No | Advanced FabricOps context override. |

## Returns

Internal runtime context object with run_id, pipeline_name, notebook identity, agreement identity, and Spark context for downstream defaults. The concrete context class is internal and not a primary public API.

### Return interpretation

The returned context can be assigned to PIPELINE for target config and lineage fields while downstream helpers read the same active defaults automatically. The concrete context class is internal and not a primary public API.

## Raises / Errors

Not documented yet

### Common failure causes

- RUN_CONTEXT is unavailable.
- spark is unavailable.
- No agreement exists when select_agreement=True.
- The user has not selected an agreement.

## Relationships

### Used by

Not documented yet

### Calls

- <a href="get_selected_agreement/"><code>fabricops_kit.data_agreement.get_selected_agreement</code></a>
- <a href="widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>
- `fabricops_kit.pipeline._PipelineRunContext`
- `fabricops_kit.pipeline._notebook_global`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._runtime_metadata_value`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `02_pipeline`
- `99_explore`

**Side effects:**

Stores active in-memory context for the current notebook session; renders agreement selection when select_agreement=True and registers only when register_notebook=True.

**Notes:**

This helper keeps template code concise while preserving explicit lower-level
parameters on guardrail and summary helpers for advanced notebooks.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Tree is truncated to keep the page readable.

    Unique internal helpers: 34. Repeated calls may appear in multiple branches.

    <div class="reference-call-tree" role="tree">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>start_pipeline_run(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L46-L52"><code>_notebook_global(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L159-L160"><code>_now_iso(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│       └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L23-L40"><code>_PipelineRunContext(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L55-L60"><code>_runtime_metadata_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="../get_selected_agreement/"><code>get_selected_agreement(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="../widget_select_agreement/"><code>widget_select_agreement(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L451-L507"><code>_current_notebook_active_registrations(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L195-L198"><code>_html_escape(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L585-L601"><code>_latest_agreement_versions(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L616-L623"><code>_list_data_agreements(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L276-L395"><code>_register_current_notebook(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L201-L311"><code>_render_searchable_selector(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L63-L72"><code>_require_ipywidgets(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">        └── </span>…</div>
    </div>


<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.start_pipeline_run`
- Short name: `start_pipeline_run`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `63`
- Inbound references count: 0
- Outbound references count: 6
- Used in templates: 02_pipeline, 99_explore
- Glossary terms: notebook template, data agreement, metadata lakehouse

### Implementation contract

- **required_context:** Defaults to RUN_CONTEXT, spark, and METADATA_SCHEMA from 00_env_config.
- **inputs:** notebook_type, select_agreement, register_notebook, read_only, and optional runtime overrides.
- **output:** Internal runtime context object with run_id, pipeline_name, notebook identity, agreement identity, and Spark context for downstream defaults. The concrete context class is internal and not a primary public API.
- **side_effects:** Stores active in-memory context for the current notebook session; renders agreement selection when select_agreement=True and registers only when register_notebook=True.
- **failure_modes:** Not documented yet
- **verification:** Verify delivery notebooks use register_notebook=True and read-only exploration notebooks use register_notebook=False with read_only=True.

### Inbound references

Not documented yet

### Outbound references

- <a href="get_selected_agreement/"><code>fabricops_kit.data_agreement.get_selected_agreement</code></a>
- <a href="widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>
- `fabricops_kit.pipeline._PipelineRunContext`
- `fabricops_kit.pipeline._notebook_global`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._runtime_metadata_value`

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L63-L151">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L63-L151</a>
- Start line: `63`
- End line: `151`
- Signature:

```python
def start_pipeline_run(
    notebook_type: str='02_pipeline',
    select_agreement: bool=False,
    register_notebook: bool=False,
    read_only: bool=False,
    run_context: Any=None,
    spark_session: Any=None,
    metadata_schema: str | None=None,
    pipeline_name: str | None=None,
    context: dict[str, Any] | None=None,
) -> Any:
```

### Internal relationship graph

### Public related functions

- <a href="run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>
- <a href="widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>

### Internal implementation summary

- Internal helper count: 34
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<details class="glossary-chip"><summary>Notebook template</summary><span>Reusable starter notebook workflow that shows how to run a FabricOps phase.</span> <a href="../../../reference/glossary/#notebook-template">Full definition</a></details>
<details class="glossary-chip"><summary>Data agreement</summary><span>FabricOps agreement record that captures ownership, steward context, usage, and expectations.</span> <a href="../../../reference/glossary/#data-agreement">Full definition</a></details>
<details class="glossary-chip"><summary>Metadata lakehouse</summary><span>Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></details>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)

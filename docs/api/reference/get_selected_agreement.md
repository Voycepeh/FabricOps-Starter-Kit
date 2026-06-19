# get_selected_agreement

Return the agreement selected by widget_select_agreement.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/data_agreement.py:1027`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1027-L1043">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use after rendering and completing widget_select_agreement when code needs the selected agreement values.

### Do not use when

- Do not use before rendering and completing widget_select_agreement, or as a substitute for querying all agreement metadata.

### Additional context

Returns the agreement chosen by widget_select_agreement so downstream cells can pass consistent agreement identifiers to pipeline helpers.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def get_selected_agreement() -> dict[str, Any]
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
agreement = get_selected_agreement()
dataset_name = agreement["dataset_name"]
```

</div>

## Parameters

No parameters.

## Returns

Selected agreement dictionary for the active notebook session.

### Return interpretation

A returned dictionary contains the selected agreement fields. A missing value means the selector has not been completed in the current notebook state.

## Raises / Errors

Raises an error when no agreement has been selected in the current session.

### Common failure causes

- widget_select_agreement has not been run.
- The user has not selected an agreement.
- Notebook state was reset.
- The selected row is no longer present in metadata.

## Relationships

### Used by

Not documented yet

### Calls

Not documented yet

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `02_pipeline`

**Side effects:**

Reads session/widget state only; it does not write metadata, tables, or files.

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    Unique internal helpers: 0. Repeated calls may appear in multiple branches.

    <div class="reference-call-tree" role="tree">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><a href="get_selected_agreement/"><code>get_selected_agreement(...)</code></a></div>
    </div>


<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.get_selected_agreement`
- Short name: `get_selected_agreement`
- Module: `data_agreement`
- Classification: Callable
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source line: `1027`
- Inbound references count: 0
- Outbound references count: 0
- Used in templates: 02_pipeline
- Glossary terms: notebook template

### Implementation contract

- **required_context:** Depends on a prior widget_select_agreement call in the same notebook session and agreement metadata loaded via 00_env_config routing.
- **inputs:** No required parameters; reads the current in-memory widget selection state.
- **output:** Selected agreement dictionary for the active notebook session.
- **side_effects:** Reads session/widget state only; it does not write metadata, tables, or files.
- **failure_modes:** Raises an error when no agreement has been selected in the current session.
- **verification:** Verify the returned agreement has the expected dataset/table identifiers before using it to drive reads, writes, or governance evidence.

### Inbound references

Not documented yet

### Outbound references

Not documented yet

### Raw source metadata

- Source file path: `src/fabricops_kit/data_agreement.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1027-L1043">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1027-L1043</a>
- Start line: `1027`
- End line: `1043`
- Signature:

```python
def get_selected_agreement() -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

- <a href="widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>

### Internal implementation summary

- Internal helper count: 0
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Notebook template</summary>Reusable starter notebook workflow that shows how to run a FabricOps phase.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)

# get_selected_catalogue_table

Return the table selected by widget_select_governance_profile_target.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:336`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L336-L361">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use after the governance profile target selector has been rendered and the reviewer has chosen a table.

**Additional context:**

Returns the catalogue table selected by widget_select_governance_profile_target for downstream governance review cells.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def get_selected_catalogue_table(table_selector: Any | None=None) -> dict[str, Any]
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_selector` | `Any \| None` | No | Selector returned by ``widget_select_governance_profile_target``. Passing it is optional because the widget also maintains module-level selection state. |

## Returns

dict[str, Any]
    Stable table identity used by ``load_catalogue_profile_rows``.

### Return interpretation

A returned dictionary contains the selected table context. A missing value means the reviewer has not completed the selection in current state.

## Raises / Errors

Not documented yet

### Common failure causes

- The selector widget has not been run.
- No table is selected.
- Notebook state was cleared.
- The selected metadata row is no longer available.

## Relationships

### Used by

Not documented yet

### Calls

Not documented yet

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `03_governance`

**Side effects:**

Not documented yet

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    get_selected_catalogue_table(...)
    ```

??? info "Internal helpers used: 0"

    This callable uses 0 internal helpers; `get_selected_catalogue_table` does not have package-local helper descendants in the generated call graph.

    <div class="reference-helper-groups">
      <section class="reference-helper-group reference-helper-group-empty">
        <h4>No internal helpers detected</h4>
        <p>This callable does not have package-local helper descendants in the generated call graph.</p>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.get_selected_catalogue_table`
- Short name: `get_selected_catalogue_table`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `336`
- Inbound references count: 0
- Outbound references count: 0
- Used in templates: 03_governance
- Glossary terms: catalogue evidence, notebook template

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** table_selector : ipywidgets.VBox, optional
    Selector returned by ``widget_select_governance_profile_target``. Passing it is
    optional because the widget also maintains module-level selection state.
- **output:** dict[str, Any]
    Stable table identity used by ``load_catalogue_profile_rows``.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

Not documented yet

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L336-L361">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L336-L361</a>
- Start line: `336`
- End line: `361`
- Signature:

```python
def get_selected_catalogue_table(table_selector: Any | None=None) -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation summary

- Internal helper count: 0
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Governance Review](../../how-fabricops-works/governance-review.md)

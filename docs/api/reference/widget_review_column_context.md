# widget_review_column_context

Render standalone business-context review guidance for selected profile rows.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:724`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L724-L743">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 03_governance when profile rows need human-reviewed column descriptions or business meaning.

**Additional context:**

Renders review guidance for column business context so reviewers can approve or edit metadata for a selected table.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_review_column_context(
    profile_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `profile_rows` | `list[dict[str, Any]]` | Yes | Selected column profile evidence from ``load_catalogue_profile_rows``. |

## Returns

list[dict[str, Any]]
    Empty editable review list. Add approved context rows before calling
    ``record_table_governance``.

### Return interpretation

The widget captures review state; approved rows must still be passed to record_table_governance to persist metadata.

## Raises / Errors

Not documented yet

### Common failure causes

- No profile rows are loaded.
- Required review fields are incomplete.
- Widget dependencies are unavailable.
- Reviewer changes are not committed before persistence.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.governance_review._display_review_guidance`

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
    widget_review_column_context(...)
    └── _display_review_guidance(...)
        └── _value(...)
    ```

??? info "Internal helpers used: 2"

    This callable uses 2 internal helpers for other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L707-L721"><code>_display_review_guidance</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L78-L79"><code>_value</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_review_column_context`
- Short name: `widget_review_column_context`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `724`
- Inbound references count: 0
- Outbound references count: 1
- Used in templates: 03_governance
- Glossary terms: catalogue evidence, notebook template

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** profile_rows : list of dict
    Selected column profile evidence from ``load_catalogue_profile_rows``.
- **output:** list[dict[str, Any]]
    Empty editable review list. Add approved context rows before calling
    ``record_table_governance``.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.governance_review._display_review_guidance`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L724-L743">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L724-L743</a>
- Start line: `724`
- End line: `743`
- Signature:

```python
def widget_review_column_context(
    profile_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation summary

- Internal helper count: 2
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Governance Review](../../how-fabricops-works/governance-review.md)

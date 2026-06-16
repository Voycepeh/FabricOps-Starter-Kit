# widget_review_column_classification

Render standalone sensitivity and PII classification review guidance for selected profile rows.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:892`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/governance_review.py#L892-L911">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 03_governance when reviewers need to approve classification metadata before governance records are written.

**Additional context:**

Renders sensitivity and PII classification review guidance for columns in a selected table.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_review_column_classification(
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
    Empty editable review list. Add approved classification dictionaries
    before calling ``record_table_governance``.

### Return interpretation

The widget captures classification review state; approved classifications must be included in record_table_governance to persist them.

## Raises / Errors

Not documented yet

### Common failure causes

- No selected profile rows are available.
- Classification choices are incomplete.
- Reviewer approval status is missing.
- Widget state is not collected before persistence.

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
    widget_review_column_classification(...)
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
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/governance_review.py#L598-L612"><code>_display_review_guidance</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/governance_review.py#L73-L74"><code>_value</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_review_column_classification`
- Short name: `widget_review_column_classification`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `892`
- Inbound references count: 0
- Outbound references count: 1
- Used in templates: 03_governance
- Glossary terms: catalogue evidence, notebook template

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** profile_rows : list of dict
    Selected column profile evidence from ``load_catalogue_profile_rows``.
- **output:** list[dict[str, Any]]
    Empty editable review list. Add approved classification dictionaries
    before calling ``record_table_governance``.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.governance_review._display_review_guidance`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/governance_review.py#L892-L911">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/governance_review.py#L892-L911</a>
- Start line: `892`
- End line: `911`
- Signature:

```python
def widget_review_column_classification(
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

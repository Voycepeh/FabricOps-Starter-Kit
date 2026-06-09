# widget_review_dq_rules

Render standalone DQ-rule review guidance for selected profile rows.

## What this is for and when to use it

Render standalone DQ-rule review guidance for selected profile rows.

- Render standalone DQ-rule review guidance for selected profile rows.

## When not to use it

- Not documented yet

## Example

```python
Not documented yet
```

## Inputs

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Required</th>
      <th>Meaning</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>profile_rows</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Selected column profile evidence from ``load_catalogue_profile_rows``.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

list[dict[str, Any]]
    Empty editable review list. Add approved rule dictionaries before
    calling ``record_table_governance``.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Not documented yet

## Related functions

Not documented yet

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/governance_review__display_review_guidance/"><code>fabricops_kit.governance_review._display_review_guidance</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/15f1799b713dde469e690b3bbdf35ffe588ff83c/src/fabricops_kit/governance_review.py#L493-L511">View widget_review_dq_rules on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def widget_review_dq_rules(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Render standalone DQ-rule review guidance for ``03_governance``.

    Parameters
    ----------
    profile_rows : list of dict
        Selected column profile evidence from ``load_catalogue_profile_rows``.

    Returns
    -------
    list[dict[str, Any]]
        Empty editable review list. Add approved rule dictionaries before
        calling ``record_table_governance``.
    """
    return _display_review_guidance(
        "DQ rule review",
        profile_rows,
        "Author human-approved DQ rules for selected columns. These records are governance evidence and are not automatically enforced by 02_pipeline.",
    )
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_review_dq_rules`
- Short name: `widget_review_dq_rules`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `493`
- Inbound references count: 0
- Outbound references count: 1

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** profile_rows : list of dict
    Selected column profile evidence from ``load_catalogue_profile_rows``.
- **output:** list[dict[str, Any]]
    Empty editable review list. Add approved rule dictionaries before
    calling ``record_table_governance``.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- <a href="../internal/governance_review__display_review_guidance/"><code>fabricops_kit.governance_review._display_review_guidance</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/15f1799b713dde469e690b3bbdf35ffe588ff83c/src/fabricops_kit/governance_review.py#L493-L511">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/15f1799b713dde469e690b3bbdf35ffe588ff83c/src/fabricops_kit/governance_review.py#L493-L511</a>
- Start line: `493`
- End line: `511`
- Signature:

```python
def widget_review_dq_rules(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation helpers

- <a href="../internal/governance_review__display_review_guidance/"><code>fabricops_kit.governance_review._display_review_guidance</code></a>

</details>

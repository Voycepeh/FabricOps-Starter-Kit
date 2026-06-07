# widget_review_dq_rules

Render standalone DQ-rule review guidance for selected profile rows.

## Use this when

Render standalone DQ-rule review guidance for selected profile rows.

## Do not use this for

Not documented yet

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
      <th>What it means</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>profile_rows</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Selected column profile evidence from ``load_catalogue_profile_rows``.</td>
    </tr>
  </tbody>
</table>
</div>

<details class="reference-signature-details">
<summary>Full signature</summary>

```python
def widget_review_dq_rules(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]
```

</details>

## Output

list[dict[str, Any]]
    Empty editable review list. Add approved rule dictionaries before
    calling ``record_table_governance``.

## Raises

Not documented yet

## Side effects

Not documented yet

## Related functions

Not documented yet

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/governance_review__display_review_guidance/"><code>fabricops_kit.governance_review._display_review_guidance</code></a>

</details>

<details class="reference-metadata-details">
<summary>AI implementation contract</summary>

These fields are generated for agents and maintainers, not for quick-start reading.

- **required_context:** Starter template: `03_review`; segment: `Governance review`.
- **inputs:** profile_rows : list of dict
    Selected column profile evidence from ``load_catalogue_profile_rows``.
- **output:** list[dict[str, Any]]
    Empty editable review list. Add approved rule dictionaries before
    calling ``record_table_governance``.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

</details>

<details class="reference-metadata-details">
<summary>Function manifest</summary>

- Fully qualified function name: `fabricops_kit.governance_review.widget_review_dq_rules`
- Short name: `widget_review_dq_rules`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `467`
- Inbound references count: 0
- Outbound references count: 1

</details>

<details class="reference-metadata-details">
<summary>Raw inbound and outbound references</summary>

### Inbound references

Not documented yet

### Outbound references

- <a href="../internal/governance_review__display_review_guidance/"><code>fabricops_kit.governance_review._display_review_guidance</code></a>

</details>

## Source code

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L467-L485">View widget_review_dq_rules on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def widget_review_dq_rules(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Render standalone DQ-rule review guidance for ``03_review``.

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

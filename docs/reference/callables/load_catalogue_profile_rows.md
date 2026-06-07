# load_catalogue_profile_rows

Load column profile rows for the selected catalogue table.

## Use this when

Load column profile rows for the selected catalogue table.

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
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>selection</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark_session</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Not documented yet</td>
    </tr>
  </tbody>
</table>
</div>

<details class="reference-signature-details">
<summary>Full signature</summary>

```python
def load_catalogue_profile_rows(config: Any, env: str, selection: dict[str, Any], *, spark_session: Any) -> list[dict[str, Any]]
```

</details>

## Output

Not documented yet

## Raises

Not documented yet

## Side effects

Not documented yet

## Related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/governance_review__coerce_rows/"><code>fabricops_kit.governance_review._coerce_rows</code></a>
- <a href="../internal/governance_review__is_success/"><code>fabricops_kit.governance_review._is_success</code></a>
- <a href="../internal/governance_review__value/"><code>fabricops_kit.governance_review._value</code></a>
- <a href="../internal/metadata__build_metadata_table_key/"><code>fabricops_kit.metadata._build_metadata_table_key</code></a>

</details>

<details class="reference-metadata-details">
<summary>AI implementation contract</summary>

These fields are generated for agents and maintainers, not for quick-start reading.

- **required_context:** Starter template: `03_review`; segment: `Governance review`.
- **inputs:** Not documented yet
- **output:** Not documented yet
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

</details>

<details class="reference-metadata-details">
<summary>Function manifest</summary>

- Fully qualified function name: `fabricops_kit.governance_review.load_catalogue_profile_rows`
- Short name: `load_catalogue_profile_rows`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `332`
- Inbound references count: 0
- Outbound references count: 5

</details>

<details class="reference-metadata-details">
<summary>Raw inbound and outbound references</summary>

### Inbound references

Not documented yet

### Outbound references

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../internal/governance_review__coerce_rows/"><code>fabricops_kit.governance_review._coerce_rows</code></a>
- <a href="../internal/governance_review__is_success/"><code>fabricops_kit.governance_review._is_success</code></a>
- <a href="../internal/governance_review__value/"><code>fabricops_kit.governance_review._value</code></a>
- <a href="../internal/metadata__build_metadata_table_key/"><code>fabricops_kit.metadata._build_metadata_table_key</code></a>

</details>

## Source code

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b6a5693130e525f919566c2115ac67da9c6faef/src/fabricops_kit/governance_review.py#L332-L357">View load_catalogue_profile_rows on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def load_catalogue_profile_rows(config: Any, env: str, selection: dict[str, Any], *, spark_session: Any) -> list[dict[str, Any]]:
    """Load column rows for the selected latest successful profile run."""
    rows = _coerce_rows(read_lakehouse_table(config, env, "metadata", CATALOGUE_TABLE, spark_session=spark_session))
    filtered = []
    for row in rows:
        table_key = str(
            _value(row, "metadata_table_key")
            or _build_metadata_table_key(
                _value(row, "environment_name"),
                _value(row, "dataset_name"),
                _value(row, "table_name"),
            )
        )
        if (
            _is_success(row)
            and str(_value(row, "environment_name")) == str(selection["environment_name"])
            and str(_value(row, "dataset_name")) == str(selection["dataset_name"])
            and str(_value(row, "table_name")) == str(selection["table_name"])
            and str(_value(row, "profile_run_id")) == str(selection["profile_run_id"])
            and str(_value(row, "profile_stage")) == str(selection["profile_stage"])
            and table_key == str(selection["metadata_table_key"])
        ):
            filtered.append(row)
    if not filtered:
        raise ValueError("The selected successful profile has no column rows in METADATA_DATA_CATALOGUE.")
    return filtered
```

</details>

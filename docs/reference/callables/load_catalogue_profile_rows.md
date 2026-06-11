# load_catalogue_profile_rows

## Purpose

Load column profile rows for the selected catalogue table.

## At a glance

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Item</th>
      <th>Details</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Item">Use when</td>
      <td data-label="Details">Load column profile rows for the selected catalogue table.</td>
    </tr>
    <tr>
      <td data-label="Item">Do not use when</td>
      <td data-label="Details">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Item">Example</td>
      <td data-label="Details">```python
Not documented yet
```</td>
    </tr>
    <tr>
      <td data-label="Item">Errors</td>
      <td data-label="Details">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Item">Side effects</td>
      <td data-label="Details">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Item">Related functions</td>
      <td data-label="Details">- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a></td>
    </tr>
  </tbody>
</table>
</div>

## Parameters

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
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>selection</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark_session</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
  </tbody>
</table>
</div>

## Returns

Not documented yet

## Used by

- `fabricops_kit.governance_review._review_governance_evidence`

## Calls

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.governance_review._coerce_rows`
- `fabricops_kit.governance_review._is_success`
- `fabricops_kit.governance_review._value`
- `fabricops_kit.metadata._build_metadata_table_key`

## Implementation details

### Call flow

```text
load_catalogue_profile_rows(...)
├── _build_metadata_table_key(...)
│   └── _stable_metadata_key(...)
├── _coerce_rows(...)
├── _is_success(...)
│   └── _value(...)
├── _value(...)
└── read_lakehouse_table(...)
    ├── _current_database_matches(...)
    ├── _get_spark(...)
    ├── _get_store(...)
    ├── _normalize_table_name(...)
    ├── _registered_table_identifier(...)
    │   ├── _normalize_table_name(...)
    │   └── _quote_identifier(...)
    └── _uses_registered_metadata_table(...)
```

## Public callable source code

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L381-L406">View load_catalogue_profile_rows on GitHub</a>

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

## Nested helper functions

??? info "Nested helper functions: 5"

    These helpers support `load_catalogue_profile_rows` by handling shared implementation tasks reached from the public call flow; expand the source block only when you need maintainer-level details.

    <table class="reference-function-table">
      <thead>
        <tr>
          <th>Helper</th>
          <th>Role</th>
          <th>Source</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td data-label="Helper"><code>_coerce_rows</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L62-L67"><code>src/fabricops_kit/governance_review.py#L62-L67</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_is_success</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L74-L75"><code>src/fabricops_kit/governance_review.py#L74-L75</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_value</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L70-L71"><code>src/fabricops_kit/governance_review.py#L70-L71</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_build_metadata_table_key</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/metadata.py#L149-L150"><code>src/fabricops_kit/metadata.py#L149-L150</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_stable_metadata_key</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/metadata.py#L144-L146"><code>src/fabricops_kit/metadata.py#L144-L146</code></a></td>
        </tr>
      </tbody>
    </table>

    ??? example "View helper source code"

        **`def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]`**

        Used by `load_catalogue_profile_rows` through the implementation path shown above.

        ```python
        def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
            if rows_or_df is None:
                return []
            if hasattr(rows_or_df, "collect"):
                rows_or_df = rows_or_df.collect()
            return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows_or_df]
        ```

        **`def _is_success(row: dict[str, Any]) -> bool`**

        Used by `load_catalogue_profile_rows` through the implementation path shown above.

        ```python
        def _is_success(row: dict[str, Any]) -> bool:
            return str(_value(row, "profile_status", "")).strip().lower() in SUCCESS_STATUSES
        ```

        **`def _value(row: dict[str, Any], name: str, default: Any='') -> Any`**

        Used by `load_catalogue_profile_rows` through the implementation path shown above.

        ```python
        def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
            return row.get(name, row.get(name.upper(), default))
        ```

        **`def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str`**

        Used by `load_catalogue_profile_rows` through the implementation path shown above.

        ```python
        def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str:
            return _stable_metadata_key(environment_name, dataset_name, table_name)
        ```

        **`def _stable_metadata_key(*parts: Any) -> str`**

        Used by `load_catalogue_profile_rows` through the implementation path shown above.

        ```python
        def _stable_metadata_key(*parts: Any) -> str:
            normalized = "|".join(str(part or "").strip().lower() for part in parts)
            return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        ```


<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.load_catalogue_profile_rows`
- Short name: `load_catalogue_profile_rows`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `381`
- Inbound references count: 1
- Outbound references count: 5

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** Not documented yet
- **output:** Not documented yet
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

- `fabricops_kit.governance_review._review_governance_evidence`

### Outbound references

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.governance_review._coerce_rows`
- `fabricops_kit.governance_review._is_success`
- `fabricops_kit.governance_review._value`
- `fabricops_kit.metadata._build_metadata_table_key`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L381-L406">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L381-L406</a>
- Start line: `381`
- End line: `406`
- Signature:

```python
def load_catalogue_profile_rows(config: Any, env: str, selection: dict[str, Any], *, spark_session: Any) -> list[dict[str, Any]]
```

### Internal relationship graph

The human-readable implementation view above is the source of truth for public call flow, public callable source, and collapsed nested helper details.

### Public related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Call flow

```text
load_catalogue_profile_rows(...)
├── _build_metadata_table_key(...)
│   └── _stable_metadata_key(...)
├── _coerce_rows(...)
├── _is_success(...)
│   └── _value(...)
├── _value(...)
└── read_lakehouse_table(...)
    ├── _current_database_matches(...)
    ├── _get_spark(...)
    ├── _get_store(...)
    ├── _normalize_table_name(...)
    ├── _registered_table_identifier(...)
    │   ├── _normalize_table_name(...)
    │   └── _quote_identifier(...)
    └── _uses_registered_metadata_table(...)
```

</details>

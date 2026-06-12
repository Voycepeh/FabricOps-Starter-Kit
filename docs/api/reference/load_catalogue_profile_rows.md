# load_catalogue_profile_rows

Load column profile rows for the selected catalogue table.

## Purpose

This API reference documents the callable summarized above. Use the sections below for when to use it, inputs, return values, template usage, and implementation details.

## When to use this

- Load column profile rows for the selected catalogue table.

## At a glance

**Do not use when:**

- Not documented yet

**Errors:**

Not documented yet

**Side effects:**

Not documented yet

## Used in templates

- `03_governance`

## Used by

- `fabricops_kit.governance_review._review_governance_evidence`

## Calls

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.governance_review._coerce_rows`
- `fabricops_kit.governance_review._is_success`
- `fabricops_kit.governance_review._value`
- `fabricops_kit.metadata._build_metadata_table_key`

## Function details and source

### Function details

- Module: `governance_review`
- Classification: Callable
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `344`
- Signature:

```python
def load_catalogue_profile_rows(config: Any, env: str, selection: dict[str, Any], *, spark_session: Any) -> list[dict[str, Any]]
```

### Parameters

`config` : `Any`, required
: Not documented yet

`env` : `str`, required
: Not documented yet

`selection` : `dict[str, Any]`, required
: Not documented yet

`spark_session` : `Any`, required
: Not documented yet

### Returns

Not documented yet

### Return interpretation

Interpret the returned value according to the Returns section above.

### Common failure causes

No common failure causes are documented beyond the Errors section.

### Notes

No additional callable notes are documented.

### Example

```python
Not documented yet
```

### Public callable source code

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L344-L369">View load_catalogue_profile_rows on GitHub</a>

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

## Internal implementation summary

??? info "Call flow"

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

??? info "Internal helpers used: 5"

    This callable uses 5 internal helpers for metadata loading and other.

    <div class="module-table-scroll reference-input-table">
    <table class="reference-function-table">
      <thead>
        <tr>
          <th>Area</th>
          <th>Helpers</th>
          <th>What they do</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td data-label="Area">Metadata loading</td>
          <td data-label="Helpers"><code>_build_metadata_table_key</code>, <code>_stable_metadata_key</code></td>
          <td data-label="What they do">Load and identify the metadata or table context needed by the callable.</td>
        </tr>
        <tr>
          <td data-label="Area">Other</td>
          <td data-label="Helpers"><code>_coerce_rows</code>, <code>_is_success</code>, <code>_value</code></td>
          <td data-label="What they do">Support lower-level implementation details that do not fit the main helper areas.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Metadata loading helpers"

            **`def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/metadata.py#L77-L78)

            ```python
            def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str:
                return _stable_metadata_key(environment_name, dataset_name, table_name)
            ```

            **`def _stable_metadata_key(*parts: Any) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/metadata.py#L72-L74)

            ```python
            def _stable_metadata_key(*parts: Any) -> str:
                normalized = "|".join(str(part or "").strip().lower() for part in parts)
                return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            ```

        ??? example "Other helpers"

            **`def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L62-L67)

            ```python
            def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
                if rows_or_df is None:
                    return []
                if hasattr(rows_or_df, "collect"):
                    rows_or_df = rows_or_df.collect()
                return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows_or_df]
            ```

            **`def _is_success(row: dict[str, Any]) -> bool`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L74-L75)

            ```python
            def _is_success(row: dict[str, Any]) -> bool:
                return str(_value(row, "profile_status", "")).strip().lower() in SUCCESS_STATUSES
            ```

            **`def _value(row: dict[str, Any], name: str, default: Any='') -> Any`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L70-L71)

            ```python
            def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
                return row.get(name, row.get(name.upper(), default))
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
- Source line: `344`
- Inbound references count: 1
- Outbound references count: 5
- Used in templates: 03_governance
- Glossary terms: —

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
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L344-L369">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L344-L369</a>
- Start line: `344`
- End line: `369`
- Signature:

```python
def load_catalogue_profile_rows(config: Any, env: str, selection: dict[str, Any], *, spark_session: Any) -> list[dict[str, Any]]
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation summary

- Internal helper count: 5
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>

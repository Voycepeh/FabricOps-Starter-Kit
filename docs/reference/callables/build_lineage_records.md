# build_lineage_records

Build source-to-target lineage evidence records for a pipeline run.

## What this is for and when to use it

Build source-to-target lineage evidence records for a pipeline run.

- Use in pipeline notebooks to build source-to-target lineage evidence rows for a completed transformation run.

## When not to use it

- Do not use to scan notebooks automatically or persist metadata; it only builds records from supplied lineage inputs.

## Example

```python
lineage_rows = build_lineage_records(dataset_name=dataset_name, run_id=run_id, source_tables=["source.orders"], target_table="unified.orders", transformation_steps=[{"step": "clean_orders"}])
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
      <td data-label="Parameter"><code>dataset_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Dataset identifier for all output rows.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>run_id</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Unique run identifier.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>source_tables</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Source table names captured for the run.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>target_table</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Target table name produced by the run.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>transformation_steps</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Transformation step dictionaries to merge into each output row.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Framework configuration used to resolve the configured audit timezone when adding timestamp metadata.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

List of lineage record dictionaries suitable for metadata persistence.

## Errors and side effects

**Errors:** Raises normal Python errors if required lineage inputs are missing or malformed.

**Side effects:** Pure record-building helper; it does not write metadata, tables, or files.

## Related functions

- <a href="../setup_notebook/"><code>fabricops_kit.config.setup_notebook</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

### Call flow

```text
build_lineage_records(...)
└── _current_audit_timestamp(...)
    └── _get_audit_timezone(...)
        └── _validate_audit_timezone(...)
```

### Internal helpers used by this callable

### `def _current_audit_timestamp(config: Any=None, timezone_name: str | None=None, *, drop_microseconds: bool=True) -> str`

**What it does:**

Return the current audit timestamp in the configured audit timezone.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/config.py#L69-L75">View `_current_audit_timestamp` on GitHub</a>

**Code:**

```python
def _current_audit_timestamp(config: Any = None, timezone_name: str | None = None, *, drop_microseconds: bool = True) -> str:
    """Return the current audit timestamp in the configured audit timezone."""
    tz_name = _get_audit_timezone(config, timezone_name)
    value = datetime.now(ZoneInfo(tz_name))
    if drop_microseconds:
        value = value.replace(microsecond=0)
    return value.isoformat()
```

**Used here because:**

`build_lineage_records` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `build_lineage_records` or another caller that reaches `_current_audit_timestamp`.

### `def _get_audit_timezone(config: Any=None, timezone_name: str | None=None) -> str`

**What it does:**

Resolve the configured FabricOps audit timezone, defaulting to UTC.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/config.py#L61-L66">View `_get_audit_timezone` on GitHub</a>

**Code:**

```python
def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
    """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
    if timezone_name is not None:
        return _validate_audit_timezone(timezone_name)
    value = getattr(config, "audit_timezone", None) if config is not None else None
    return _validate_audit_timezone(value)
```

**Used here because:**

`build_lineage_records` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `build_lineage_records` or another caller that reaches `_get_audit_timezone`.

### `def _validate_audit_timezone(timezone_name: str | None) -> str`

**What it does:**

Return a valid IANA audit timezone name.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/config.py#L27-L58">View `_validate_audit_timezone` on GitHub</a>

**Code:**

```python
def _validate_audit_timezone(timezone_name: str | None) -> str:
    """Return a valid IANA audit timezone name.

    Parameters
    ----------
    timezone_name : str or None
        IANA timezone name to validate. Blank values default to ``"UTC"``.

    Returns
    -------
    str
        Validated timezone name.

    Raises
    ------
    ValueError
        If a non-blank value is not a valid IANA timezone name.
    """
    value = str(timezone_name or DEFAULT_AUDIT_TIMEZONE).strip() or DEFAULT_AUDIT_TIMEZONE
    if value != DEFAULT_AUDIT_TIMEZONE and "/" not in value:
        raise ValueError(
            f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
            'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
        )
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(
            f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
            'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
        ) from exc
    return value
```

**Used here because:**

`build_lineage_records` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `build_lineage_records` or another caller that reaches `_validate_audit_timezone`.


</details>

## Source

- Source file path: `src/fabricops_kit/data_lineage.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_lineage.py#L212-L236">View build_lineage_records on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def build_lineage_records(*, dataset_name: str, run_id: str, source_tables: list[str], target_table: str, transformation_steps: list[dict], config: Any = None) -> list[dict]:
    """Build compact lineage records for downstream metadata sinks.

    Parameters
    ----------
    dataset_name : str
        Dataset identifier for all output rows.
    run_id : str
        Unique run identifier.
    source_tables : list of str
        Source table names captured for the run.
    target_table : str
        Target table name produced by the run.
    transformation_steps : list of dict
        Transformation step dictionaries to merge into each output row.
    config : Any, optional
        Framework configuration used to resolve the configured audit timezone
        when adding timestamp metadata.

    Returns
    -------
    list of dict
        Row dictionaries suitable for metadata persistence.
    """
    return [{"run_id": run_id, "dataset_name": dataset_name, "source_tables": source_tables, "target_table": target_table, **({"created_ts": _current_audit_timestamp(config=config, drop_microseconds=False)} if config is not None else {}), **s} for s in transformation_steps]
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.data_lineage.build_lineage_records`
- Short name: `build_lineage_records`
- Module: `data_lineage`
- Classification: Callable
- Related module: `data_lineage`
- Source file path: `src/fabricops_kit/data_lineage.py`
- Source line: `212`
- Inbound references count: 0
- Outbound references count: 1

### AI implementation contract

- **required_context:** Use with run context from 00_env_config and persist through configured metadata routing when lineage evidence is required.
- **inputs:** dataset_name, run_id, source_tables, target_table, and transformation_steps.
- **output:** List of lineage record dictionaries suitable for metadata persistence.
- **side_effects:** Pure record-building helper; it does not write metadata, tables, or files.
- **failure_modes:** Raises normal Python errors if required lineage inputs are missing or malformed.
- **verification:** Verify each source table, target table, transformation step, dataset_name, and run_id are populated before persisting lineage records.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config._current_audit_timestamp`

### Raw source metadata

- Source file path: `src/fabricops_kit/data_lineage.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_lineage.py#L212-L236">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_lineage.py#L212-L236</a>
- Start line: `212`
- End line: `236`
- Signature:

```python
def build_lineage_records(*, dataset_name: str, run_id: str, source_tables: list[str], target_table: str, transformation_steps: list[dict], config: Any=None) -> list[dict]
```

### Internal relationship graph

### Public related functions

- <a href="../setup_notebook/"><code>fabricops_kit.config.setup_notebook</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>

### Internal implementation helpers

### Call flow

```text
build_lineage_records(...)
└── _current_audit_timestamp(...)
    └── _get_audit_timezone(...)
        └── _validate_audit_timezone(...)
```

### Internal helpers used by this callable

### `def _current_audit_timestamp(config: Any=None, timezone_name: str | None=None, *, drop_microseconds: bool=True) -> str`

**What it does:**

Return the current audit timestamp in the configured audit timezone.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/config.py#L69-L75">View `_current_audit_timestamp` on GitHub</a>

**Code:**

```python
def _current_audit_timestamp(config: Any = None, timezone_name: str | None = None, *, drop_microseconds: bool = True) -> str:
    """Return the current audit timestamp in the configured audit timezone."""
    tz_name = _get_audit_timezone(config, timezone_name)
    value = datetime.now(ZoneInfo(tz_name))
    if drop_microseconds:
        value = value.replace(microsecond=0)
    return value.isoformat()
```

**Used here because:**

`build_lineage_records` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `build_lineage_records` or another caller that reaches `_current_audit_timestamp`.

### `def _get_audit_timezone(config: Any=None, timezone_name: str | None=None) -> str`

**What it does:**

Resolve the configured FabricOps audit timezone, defaulting to UTC.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/config.py#L61-L66">View `_get_audit_timezone` on GitHub</a>

**Code:**

```python
def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
    """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
    if timezone_name is not None:
        return _validate_audit_timezone(timezone_name)
    value = getattr(config, "audit_timezone", None) if config is not None else None
    return _validate_audit_timezone(value)
```

**Used here because:**

`build_lineage_records` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `build_lineage_records` or another caller that reaches `_get_audit_timezone`.

### `def _validate_audit_timezone(timezone_name: str | None) -> str`

**What it does:**

Return a valid IANA audit timezone name.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/config.py#L27-L58">View `_validate_audit_timezone` on GitHub</a>

**Code:**

```python
def _validate_audit_timezone(timezone_name: str | None) -> str:
    """Return a valid IANA audit timezone name.

    Parameters
    ----------
    timezone_name : str or None
        IANA timezone name to validate. Blank values default to ``"UTC"``.

    Returns
    -------
    str
        Validated timezone name.

    Raises
    ------
    ValueError
        If a non-blank value is not a valid IANA timezone name.
    """
    value = str(timezone_name or DEFAULT_AUDIT_TIMEZONE).strip() or DEFAULT_AUDIT_TIMEZONE
    if value != DEFAULT_AUDIT_TIMEZONE and "/" not in value:
        raise ValueError(
            f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
            'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
        )
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(
            f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
            'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
        ) from exc
    return value
```

**Used here because:**

`build_lineage_records` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `build_lineage_records` or another caller that reaches `_validate_audit_timezone`.


</details>

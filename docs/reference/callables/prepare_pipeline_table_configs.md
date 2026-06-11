# prepare_pipeline_table_configs

Prepare source or target table configs for 02_pipeline.

## Purpose

Prepare source or target table configs for 02_pipeline.

## At a glance

**Use when:**

- Use after SOURCE_TABLES or TARGET_TABLES and their defaults are defined to derive standard config fields or add target audit columns.

**Do not use when:**

- Do not use for ad hoc reads or writes outside the pipeline table-config pattern.

**Example:**

```python
SOURCE_TABLES, SOURCE_CONFIG_BY_KEY = prepare_pipeline_table_configs(SOURCE_TABLES, DEFAULT_SOURCE_GUARDRAILS, table_role="source")
```

**Errors:**

ValueError
    If ``table_role`` is not ``"source"`` or ``"target"``.

**Side effects:**

Source role validates pre-loaded DataFrames. Target role adds FabricOps audit columns to target DataFrames.

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
      <td data-label="Parameter"><code>table_configs</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">User-authored table config dictionaries from ``SOURCE_TABLES`` or ``TARGET_TABLES``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>default_settings</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Default guardrails, and for targets write options, merged before each table config. Table-specific values take precedence.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>table_role</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Role-specific preparation mode. Source mode validates that each config already includes a DataFrame; target mode adds FabricOps audit columns and derives write metadata.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>run_id</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Pipeline run identifier used for target audit columns. Required for target role.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>pipeline_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Pipeline name used for target audit columns. Required for target role.</td>
    </tr>
  </tbody>
</table>
</div>

## Returns

Enriched table configs and a dictionary keyed by table key.

## Used by

Not documented yet

## Calls

- `fabricops_kit.pipeline._add_audit_columns`

## Implementation details

### Call flow

```text
prepare_pipeline_table_configs(...)
└── _add_audit_columns(...)
    └── _current_audit_timestamp(...)
        └── _get_audit_timezone(...)
            └── _validate_audit_timezone(...)
```

## Public callable source code

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/pipeline.py#L126-L214">View prepare_pipeline_table_configs on GitHub</a>

```python
def prepare_pipeline_table_configs(
    table_configs: list[dict[str, Any]],
    default_settings: Mapping[str, Any],
    *,
    table_role: str,
    run_id: str = "",
    pipeline_name: str = "",
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Prepare source or target table configs for a pipeline notebook.

    Parameters
    ----------
    table_configs : list of dict
        User-authored table config dictionaries from ``SOURCE_TABLES`` or
        ``TARGET_TABLES``.
    default_settings : mapping
        Default guardrails, and for targets write options, merged before each
        table config. Table-specific values take precedence.
    table_role : {"source", "target"}
        Role-specific preparation mode. Source mode validates that each config
        already includes a DataFrame; target mode adds FabricOps audit columns
        and derives write metadata.
    run_id : str, optional
        Pipeline run identifier used for target audit columns. Required for
        target role.
    pipeline_name : str, optional
        Pipeline name used for target audit columns. Required for target role.

    Returns
    -------
    tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]
        Enriched table configs and a lookup keyed by table ``key``.

    Raises
    ------
    ValueError
        If ``table_role`` is not ``"source"`` or ``"target"``.

    Notes
    -----
    Source configs derive ``dataset_name`` from ``table_name`` and ``stage`` from
    ``layer``. Source
    DataFrames must be loaded directly in the notebook with the existing
    FabricOps read helpers and supplied in each source config as ``df``.

    Target configs derive ``dataset_name``, ``stage``, ``target_layer``,
    ``target_name``, and ``target_kind`` unless overridden, then add standard
    FabricOps audit columns.
    """
    normalized_role = str(table_role or "").lower().strip()
    if normalized_role not in {"source", "target"}:
        raise ValueError("table_role must be 'source' or 'target'.")

    enriched_tables: list[dict[str, Any]] = []
    for table_config in table_configs:
        merged_config = {**default_settings, **table_config}
        dataset_name = merged_config.get("dataset_name", merged_config["table_name"])
        stage = merged_config.get("stage", merged_config["layer"])
        if normalized_role == "source":
            if "df" not in merged_config:
                table_key = merged_config.get("key", merged_config.get("table_name", "<unknown>"))
                raise ValueError(
                    "Source table config "
                    f"{table_key!r} must include a pre-loaded DataFrame in the 'df' key. "
                    "Load the source with read_lakehouse_table, read_lakehouse_csv, "
                    "read_lakehouse_parquet, read_lakehouse_excel, read_warehouse_table, "
                    "or spark.read.table before calling prepare_pipeline_table_configs."
                )
            enriched_table = {
                **merged_config,
                "dataset_name": dataset_name,
                "stage": stage,
            }
        else:
            target_layer = merged_config.get("target_layer", merged_config["layer"])
            target_name = merged_config.get("target_name", merged_config["table_name"])
            target_kind = merged_config.get("target_kind", merged_config.get("kind", "lakehouse"))
            enriched_table = {
                **merged_config,
                "df": _add_audit_columns(merged_config["df"], run_id=run_id, pipeline_name=pipeline_name, config=merged_config.get("config", default_settings.get("config"))),
                "dataset_name": dataset_name,
                "stage": stage,
                "target_layer": target_layer,
                "target_name": target_name,
                "target_kind": target_kind,
            }
        enriched_tables.append(enriched_table)

    return enriched_tables, {table_config["key"]: table_config for table_config in enriched_tables}
```

## Maintainer internals

??? info "Nested helper functions: 4"

    These nested helpers support `prepare_pipeline_table_configs` by handling lower-level implementation steps; expand this section only when maintaining or debugging the package internals.

    <div class="module-table-scroll reference-input-table">
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
          <td data-label="Helper"><code>_add_audit_columns</code></td>
          <td data-label="Role">Return a DataFrame with standard FabricOps target audit columns.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/pipeline.py#L113-L123">src/fabricops_kit/pipeline.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_current_audit_timestamp</code></td>
          <td data-label="Role">Return the current audit timestamp in the configured audit timezone.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L69-L75">src/fabricops_kit/config.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_get_audit_timezone</code></td>
          <td data-label="Role">Resolve the configured FabricOps audit timezone, defaulting to UTC.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L61-L66">src/fabricops_kit/config.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_validate_audit_timezone</code></td>
          <td data-label="Role">Return a valid IANA audit timezone name.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L27-L58">src/fabricops_kit/config.py</a></td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source code"

        **`def _add_audit_columns(dataframe: Any, *, run_id: str, pipeline_name: str, config: Any=None)`**

        Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/pipeline.py#L113-L123)

        ```python
        def _add_audit_columns(dataframe: Any, *, run_id: str, pipeline_name: str, config: Any = None):
            """Return a DataFrame with standard FabricOps target audit columns."""
            from pyspark.sql import functions as F

            audit_created_at = _current_audit_timestamp(config=config)
            return (
                dataframe
                .withColumn("_fabricops_run_id", F.lit(run_id))
                .withColumn("_fabricops_pipeline_name", F.lit(pipeline_name))
                .withColumn("_fabricops_created_at", F.lit(audit_created_at))
            )
        ```

        **`def _current_audit_timestamp(config: Any=None, timezone_name: str | None=None, *, drop_microseconds: bool=True) -> str`**

        Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L69-L75)

        ```python
        def _current_audit_timestamp(config: Any = None, timezone_name: str | None = None, *, drop_microseconds: bool = True) -> str:
            """Return the current audit timestamp in the configured audit timezone."""
            tz_name = _get_audit_timezone(config, timezone_name)
            value = datetime.now(ZoneInfo(tz_name))
            if drop_microseconds:
                value = value.replace(microsecond=0)
            return value.isoformat()
        ```

        **`def _get_audit_timezone(config: Any=None, timezone_name: str | None=None) -> str`**

        Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L61-L66)

        ```python
        def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
            """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
            if timezone_name is not None:
                return _validate_audit_timezone(timezone_name)
            value = getattr(config, "audit_timezone", None) if config is not None else None
            return _validate_audit_timezone(value)
        ```

        **`def _validate_audit_timezone(timezone_name: str | None) -> str`**

        Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L27-L58)

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


<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.prepare_pipeline_table_configs`
- Short name: `prepare_pipeline_table_configs`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `126`
- Inbound references count: 0
- Outbound references count: 1

### AI implementation contract

- **required_context:** Source DataFrames should be loaded directly in the notebook with existing FabricOps read helpers. Target audit columns require a Spark-compatible DataFrame.
- **inputs:** table_configs, default_settings, table_role, and role-specific context such as run_id/pipeline_name for targets.
- **output:** Enriched table configs and a dictionary keyed by table key.
- **side_effects:** Source role validates pre-loaded DataFrames. Target role adds FabricOps audit columns to target DataFrames.
- **failure_modes:** ValueError
    If ``table_role`` is not ``"source"`` or ``"target"``.
- **verification:** Verify the correct table_role is used and enriched configs are passed to run_table_guardrails before transformation or writes.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.pipeline._add_audit_columns`

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/pipeline.py#L126-L214">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/pipeline.py#L126-L214</a>
- Start line: `126`
- End line: `214`
- Signature:

```python
def prepare_pipeline_table_configs(table_configs: list[dict[str, Any]], default_settings: Mapping[str, Any], *, table_role: str, run_id: str='', pipeline_name: str='') -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation helpers

### Call flow

```text
prepare_pipeline_table_configs(...)
└── _add_audit_columns(...)
    └── _current_audit_timestamp(...)
        └── _get_audit_timezone(...)
            └── _validate_audit_timezone(...)
```

</details>

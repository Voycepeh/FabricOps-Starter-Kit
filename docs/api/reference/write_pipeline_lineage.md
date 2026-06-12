# write_pipeline_lineage

Write many-to-many source-to-target lineage evidence.

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use near the end of 02_pipeline after transformations and target config resolution have produced lineage-ready records.

**Additional context:**

Persists lineage records for a pipeline run so source tables, target tables, and transformation steps remain traceable.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def write_pipeline_lineage(
    spark: Any,
    config: Any,
    env: str,
    run_id: str,
    source_definitions: Mapping[str, Mapping[str, Any]],
    target_definitions: Mapping[str, Mapping[str, Any]],
    relationships: list[Mapping[str, Any]] | None=None,
    dataset_name: str='',
    agreement_id: str='',
    agreement_contract_version: str='',
    notebook_registry_id: str='',
    notebook_id: str='',
    pipeline_name: str='',
    metadata_table: str=LINEAGE_TABLE,
    mode: str='append',
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark` | `Any` | Yes | Spark session used to create lineage rows. |
| `config` | `Any` | Yes | Metadata route from ``00_env_config``. |
| `env` | `str` | Yes | Not documented yet |
| `run_id` | `str` | Yes | Pipeline run identifier. |
| `source_definitions` | `Mapping[str, Mapping[str, Any]]` | Yes | Source and target definitions keyed by alias. |
| `target_definitions` | `Mapping[str, Mapping[str, Any]]` | Yes | Not documented yet |
| `relationships` | `list[Mapping[str, Any]] \| None` | No | Many-to-many lineage relationships. Each item may contain ``sources``, ``targets``, ``operation``, and ``description``. When omitted, every source is linked to every target. |
| `dataset_name` | `str` | No | Governance context embedded in lineage payloads. |
| `agreement_id` | `str` | No | Not documented yet |
| `agreement_contract_version` | `str` | No | Not documented yet |
| `notebook_registry_id` | `str` | No | Not documented yet |
| `notebook_id` | `str` | No | Not documented yet |
| `pipeline_name` | `str` | No | Not documented yet |
| `metadata_table` | `str` | No | Metadata lineage table. |
| `mode` | `str` | No | Write mode for lineage evidence. |

## Returns

Status, row count, and lineage rows.

### Return interpretation

A successful result indicates lineage rows were prepared for metadata persistence; review returned counts against expected transformation steps.

## Raises / Errors

Not documented yet

### Common failure causes

- Lineage records are empty or malformed.
- run_id, source, or target identifiers are missing.
- The metadata table cannot be written.
- Audit fields cannot be resolved from configuration.

## Relationships

### Used by

Not documented yet

### Calls

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- `fabricops_kit.metadata._build_metadata_table_key`
- `fabricops_kit.pipeline._definition_name`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._runtime_audit_fields`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`

**Side effects:**

Writes METADATA_DATA_LINEAGE_TABLE through the configured metadata lakehouse target.

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    write_pipeline_lineage(...)
    ├── _build_metadata_table_key(...)
    │   └── _stable_metadata_key(...)
    ├── _definition_name(...)
    ├── _now_iso(...)
    │   └── _current_audit_timestamp(...)
    │       └── _get_audit_timezone(...)
    │           └── _validate_audit_timezone(...)
    ├── _runtime_audit_fields(...)
    │   ├── _build_runtime_audit_fields(...)
    │   │   ├── _context_get(...)
    │   │   ├── _current_audit_timestamp(...)
    │   │   │   └── _get_audit_timezone(...)
    │   │   │       └── _validate_audit_timezone(...)
    │   │   ├── _runtime_context(...)
    │   │   │   └── _context_get(...)
    │   │   └── _safe_str(...)
    │   └── _now_iso(...)
    │       └── _current_audit_timestamp(...)
    │           └── _get_audit_timezone(...)
    │               └── _validate_audit_timezone(...)
    └── write_lakehouse_table(...)
        ├── _get_store(...)
        ├── _normalize_table_name(...)
        ├── _registered_table_identifier(...)
        │   ├── _normalize_table_name(...)
        │   └── _quote_identifier(...)
        └── _uses_registered_metadata_table(...)
    ```

??? info "Internal helpers used: 12"

    This callable uses 12 internal helpers for audit timestamp, metadata loading, rule parsing, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/metadata.py#L147-L217"><code>_build_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/config.py#L69-L75"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/config.py#L61-L66"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L49-L60"><code>_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/config.py#L27-L58"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/metadata.py#L77-L78"><code>_build_metadata_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/metadata.py#L72-L74"><code>_stable_metadata_key</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L23-L24"><code>_definition_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/metadata.py#L101-L113"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L19-L20"><code>_now_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/metadata.py#L120-L144"><code>_runtime_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/metadata.py#L116-L117"><code>_safe_str</code></a>
        </div>
      </section>
    </div>

    ??? example "View helper source by area"

        ??? example "Audit timestamp helpers"

            **`def _build_runtime_audit_fields(*, config: Any=None, env: str | None=None, timestamp_field: str='_committed_at', user_field: str='_committed_by', workspace_field: str='_workspace_name', notebook_field: str='_notebook_name', metadata_lakehouse_field: str='_metadata_lakehouse_name', activity_field: str='_activity_id', committed_by: str | None=None, committed_at: str | None=None, runtime_context: dict[str, Any] | None=None) -> dict[str, str]`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/metadata.py#L147-L217)

            ```python
            def _build_runtime_audit_fields(
                *,
                config: Any = None,
                env: str | None = None,
                timestamp_field: str = "_committed_at",
                user_field: str = "_committed_by",
                workspace_field: str = "_workspace_name",
                notebook_field: str = "_notebook_name",
                metadata_lakehouse_field: str = "_metadata_lakehouse_name",
                activity_field: str = "_activity_id",
                committed_by: str | None = None,
                committed_at: str | None = None,
                runtime_context: dict[str, Any] | None = None,
            ) -> dict[str, str]:
                """Build reusable framework-managed audit fields for metadata-table rows.

                Parameters
                ----------
                config : FrameworkConfig | dict, optional
                    Framework config containing ``path_config.paths[env]["metadata"]``.
                env : str, optional
                    Environment key paired with ``config``.
                timestamp_field, user_field, workspace_field, notebook_field : str
                    Output keys for timestamp, user, workspace, and notebook audit values.
                metadata_lakehouse_field, activity_field : str
                    Output keys for metadata lakehouse and Fabric activity audit values.
                committed_by, committed_at : str, optional
                    Deterministic audit overrides. When omitted, values resolve from Fabric
                    runtime context and the configured audit timezone timestamp.
                runtime_context : dict[str, Any], optional
                    Values merged over :func:`_runtime_context`, primarily for tests or
                    controlled notebook overrides.

                Returns
                -------
                dict[str, str]
                    Framework-managed metadata audit values keyed by the supplied field
                    names.

                Notes
                -----
                DataFrame runtime audit columns and metadata-table audit fields both use
                underscore-prefixed names. This helper centralizes the metadata-table
                convention so notebooks can reuse runtime context when adding dataframe
                audit columns inline.
                """
                context = {**_runtime_context(), **(runtime_context or {})}

                def _first_non_blank(*keys: str) -> Any:
                    for key in keys:
                        value = _context_get(context, key)
                        if value is not None and str(value).strip():
                            return value
                    return None

                metadata_lakehouse_name = ""
                if config is not None and env is not None:
                    paths = config.path_config.paths if hasattr(config, "path_config") else config.paths
                    metadata_lakehouse_name = _safe_str(paths[env]["metadata"].name)
                return {
                    user_field: _safe_str(committed_by).strip()
                    if committed_by and _safe_str(committed_by).strip()
                    else _safe_str(_first_non_blank("userName", "userId") or "unknown"),
                    timestamp_field: _safe_str(committed_at)
                    if committed_at
                    else _current_audit_timestamp(config=config),
                    workspace_field: _safe_str(_first_non_blank("currentWorkspaceName", "workspaceName") or ""),
                    notebook_field: _safe_str(_first_non_blank("currentNotebookName", "notebookName") or ""),
                    metadata_lakehouse_field: metadata_lakehouse_name,
                    activity_field: _safe_str(_first_non_blank("activityId") or ""),
                }
            ```

            **`def _current_audit_timestamp(config: Any=None, timezone_name: str | None=None, *, drop_microseconds: bool=True) -> str`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/config.py#L69-L75)

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

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/config.py#L61-L66)

            ```python
            def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
                """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
                if timezone_name is not None:
                    return _validate_audit_timezone(timezone_name)
                value = getattr(config, "audit_timezone", None) if config is not None else None
                return _validate_audit_timezone(value)
            ```

            **`def _runtime_audit_fields(config: Any, env: str) -> dict[str, str]`**

            Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L49-L60)

            ```python
            def _runtime_audit_fields(config: Any, env: str) -> dict[str, str]:
                try:
                    return _build_runtime_audit_fields(config=config, env=env)
                except Exception:
                    return {
                        "_committed_at": _now_iso(config),
                        "_committed_by": "unknown",
                        "_workspace_name": "",
                        "_notebook_name": "",
                        "_metadata_lakehouse_name": "",
                        "_activity_id": "",
                    }
            ```

            **`def _validate_audit_timezone(timezone_name: str | None) -> str`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/config.py#L27-L58)

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

        ??? example "Metadata loading helpers"

            **`def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/metadata.py#L77-L78)

            ```python
            def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str:
                return _stable_metadata_key(environment_name, dataset_name, table_name)
            ```

            **`def _stable_metadata_key(*parts: Any) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/metadata.py#L72-L74)

            ```python
            def _stable_metadata_key(*parts: Any) -> str:
                normalized = "|".join(str(part or "").strip().lower() for part in parts)
                return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            ```

        ??? example "Rule parsing helpers"

            **`def _definition_name(name: str, definition: Mapping[str, Any]) -> str`**

            Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L23-L24)

            ```python
            def _definition_name(name: str, definition: Mapping[str, Any]) -> str:
                return str(definition.get("table_name") or definition.get("name") or name)
            ```

        ??? example "Other helpers"

            **`def _context_get(context: Any, *keys: str) -> Any`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/metadata.py#L101-L113)

            ```python
            def _context_get(context: Any, *keys: str) -> Any:
                for key in keys:
                    try:
                        if isinstance(context, dict):
                            value = context.get(key)
                        else:
                            getter = getattr(context, "get", None)
                            value = getter(key) if callable(getter) else None
                    except Exception:
                        value = None
                    if value is not None:
                        return value
                return None
            ```

            **`def _now_iso(config: Any=None) -> str`**

            Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L19-L20)

            ```python
            def _now_iso(config: Any = None) -> str:
                return _current_audit_timestamp(config=config)
            ```

            **`def _runtime_context() -> dict[str, Any]`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/metadata.py#L120-L144)

            ```python
            def _runtime_context() -> dict[str, Any]:
                try:
                    import notebookutils  # type: ignore
                except Exception:
                    return {}

                runtime = getattr(notebookutils, "runtime", None)
                context = getattr(runtime, "context", None)
                if context is None:
                    return {}

                keys = [
                    "currentWorkspaceId",
                    "currentWorkspaceName",
                    "currentNotebookId",
                    "currentNotebookName",
                    "workspaceId",
                    "workspaceName",
                    "notebookId",
                    "notebookName",
                    "userId",
                    "userName",
                    "activityId",
                ]
                return {key: _context_get(context, key) for key in keys}
            ```

            **`def _safe_str(value: Any) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/metadata.py#L116-L117)

            ```python
            def _safe_str(value: Any) -> str:
                return "" if value is None else str(value)
            ```


<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:559`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L559-L643">View on GitHub</a>
</div>

??? example "Source code"

    ```python
    def write_pipeline_lineage(
        *,
        spark: Any,
        config: Any,
        env: str,
        run_id: str,
        source_definitions: Mapping[str, Mapping[str, Any]],
        target_definitions: Mapping[str, Mapping[str, Any]],
        relationships: list[Mapping[str, Any]] | None = None,
        dataset_name: str = "",
        agreement_id: str = "",
        agreement_contract_version: str = "",
        notebook_registry_id: str = "",
        notebook_id: str = "",
        pipeline_name: str = "",
        metadata_table: str = LINEAGE_TABLE,
        mode: str = "append",
    ) -> dict[str, Any]:
        """Write many-to-many source-to-target lineage evidence.

        Parameters
        ----------
        spark : pyspark.sql.SparkSession
            Spark session used to create lineage rows.
        config, env : object, str
            Metadata route from ``00_env_config``.
        run_id : str
            Pipeline run identifier.
        source_definitions, target_definitions : mapping
            Source and target definitions keyed by alias.
        relationships : list of mapping, optional
            Many-to-many lineage relationships. Each item may contain ``sources``,
            ``targets``, ``operation``, and ``description``. When omitted, every
            source is linked to every target.
        dataset_name, agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, pipeline_name : str, optional
            Governance context embedded in lineage payloads.
        metadata_table : str, default="METADATA_DATA_LINEAGE_TABLE"
            Metadata lineage table.
        mode : str, default="append"
            Write mode for lineage evidence.

        Returns
        -------
        dict[str, Any]
            Status, row count, and written rows.
        """
        audit = _runtime_audit_fields(config, env)
        created_at = _now_iso(config)
        if relationships is None:
            relationships = [{"sources": list(source_definitions), "targets": list(target_definitions), "operation": "pipeline_transform", "description": "User-defined pipeline transformation."}]
        rows: list[dict[str, Any]] = []
        sequence = 0
        for relationship in relationships:
            for source_alias in relationship.get("sources", []):
                for target_alias in relationship.get("targets", []):
                    sequence += 1
                    source_table = _definition_name(str(source_alias), source_definitions[str(source_alias)])
                    target_table = _definition_name(str(target_alias), target_definitions[str(target_alias)])
                    payload = {
                        "run_id": run_id,
                        "agreement_id": agreement_id,
                        "agreement_contract_version": agreement_contract_version,
                        "notebook_registry_id": notebook_registry_id,
                        "notebook_id": notebook_id,
                        "pipeline_name": pipeline_name,
                        "source_alias": source_alias,
                        "target_alias": target_alias,
                        "operation": relationship.get("operation", "pipeline_transform"),
                        "description": relationship.get("description", ""),
                    }
                    rows.append({
                        "lineage_id": f"{run_id}_{sequence}",
                        "dataset_name": dataset_name or str(target_definitions[str(target_alias)].get("dataset_name") or target_table),
                        "run_id": run_id,
                        "source_table": source_table,
                        "target_table": target_table,
                        "source_table_key": _build_metadata_table_key(env, str(source_definitions[str(source_alias)].get("dataset_name") or source_table), source_table),
                        "target_table_key": _build_metadata_table_key(env, str(target_definitions[str(target_alias)].get("dataset_name") or target_table), target_table),
                        "transformation_steps_json": json.dumps(payload, default=str, sort_keys=True),
                        "created_at": created_at,
                        **audit,
                    })
        if rows:
            write_lakehouse_table(spark.createDataFrame(rows), config, env, "metadata", metadata_table, mode=mode)
        return {"status": "written" if rows else "skipped", "row_count": len(rows), "rows": rows}
    ```

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.write_pipeline_lineage`
- Short name: `write_pipeline_lineage`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `559`
- Inbound references count: 0
- Outbound references count: 5
- Used in templates: 02_pipeline
- Glossary terms: source table, target table, catalogue evidence, metadata lakehouse

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Lineage evidence`.
- **inputs:** spark, config, env, run_id, source_definitions, target_definitions, relationships, and governance context.
- **output:** Status, row count, and lineage rows.
- **side_effects:** Writes METADATA_DATA_LINEAGE_TABLE through the configured metadata lakehouse target.
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- `fabricops_kit.metadata._build_metadata_table_key`
- `fabricops_kit.pipeline._definition_name`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._runtime_audit_fields`

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L559-L643">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L559-L643</a>
- Start line: `559`
- End line: `643`
- Signature:

```python
def write_pipeline_lineage(
    spark: Any,
    config: Any,
    env: str,
    run_id: str,
    source_definitions: Mapping[str, Mapping[str, Any]],
    target_definitions: Mapping[str, Mapping[str, Any]],
    relationships: list[Mapping[str, Any]] | None=None,
    dataset_name: str='',
    agreement_id: str='',
    agreement_contract_version: str='',
    notebook_registry_id: str='',
    notebook_id: str='',
    pipeline_name: str='',
    metadata_table: str=LINEAGE_TABLE,
    mode: str='append',
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

### Internal implementation summary

- Internal helper count: 12
- Grouped helper summary and optional source snippets are rendered in the page-level Implementation details section.

</details>

## Source link

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:559`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L559-L643">View on GitHub</a>
</div>

## Glossary

- **Source table:** An input table or file read by the pipeline.
- **Target table:** An output table written by the pipeline.
- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
- [Metadata Tables](../../how-fabricops-works/metadata-tables.md)

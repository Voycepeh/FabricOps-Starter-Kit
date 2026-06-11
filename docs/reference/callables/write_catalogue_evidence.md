# write_catalogue_evidence

Enrich profile rows with guardrail context and write catalogue evidence.

## Purpose

Enrich profile rows with guardrail context and write catalogue evidence.

## At a glance

**Use when:**

- Use after source or target profiles and guardrail results are available to persist catalogue evidence through the configured metadata route.

**Do not use when:**

- Not documented yet

**Example:**

```python
Not documented yet
```

**Errors:**

Not documented yet

**Side effects:**

Writes METADATA_DATA_CATALOGUE through the configured metadata lakehouse target.

## Used by

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

## Calls

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- `fabricops_kit.metadata._build_metadata_table_key`
- `fabricops_kit.pipeline._canonical_catalogue_profile_df`
- `fabricops_kit.pipeline._definition_name`
- `fabricops_kit.pipeline._dq_summary_fields`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._runtime_audit_fields`

## Callable implementation

### Function details

- Module: `pipeline`
- Classification: Callable
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `451`
- Signature:

```python
def write_catalogue_evidence(profiles: Mapping[str, Any], dataset_definitions: Mapping[str, Mapping[str, Any]], *, config: Any, env: str, run_id: str, agreement_id: str='', agreement_contract_version: str='', notebook_registry_id: str='', notebook_id: str='', pipeline_name: str='', schema_results: Mapping[str, Mapping[str, Any]] | None=None, freshness_results: Mapping[str, Mapping[str, Any]] | None=None, stability_results: Mapping[str, Mapping[str, Any]] | None=None, dq_results: Mapping[str, Mapping[str, Any]] | None=None, metadata_table: str=CATALOGUE_TABLE, mode: str='append') -> dict[str, str]
```

### Parameters

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
      <td data-label="Parameter"><code>profiles</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Profile DataFrames produced by ``profile_dataframe`` for each dataset.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dataset_definitions</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Source or target definitions containing table, stage, and layer context.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Metadata lakehouse route from ``00_env_config``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>run_id</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Pipeline run identifier.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>agreement_id</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Governance context added to each catalogue row.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>agreement_contract_version</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>notebook_registry_id</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>notebook_id</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>pipeline_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>schema_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Guardrail results keyed by dataset alias.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>freshness_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>stability_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dq_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>metadata_table</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Metadata table to append.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>mode</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Write mode for catalogue evidence.</td>
    </tr>
  </tbody>
</table>
</div>

### Returns

Dictionary of write statuses keyed by dataset alias.

### Notes

No additional callable notes are documented.

### Public callable source code

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/pipeline.py#L451-L556">View write_catalogue_evidence on GitHub</a>

```python
def write_catalogue_evidence(
    profiles: Mapping[str, Any],
    dataset_definitions: Mapping[str, Mapping[str, Any]],
    *,
    config: Any,
    env: str,
    run_id: str,
    agreement_id: str = "",
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    pipeline_name: str = "",
    schema_results: Mapping[str, Mapping[str, Any]] | None = None,
    freshness_results: Mapping[str, Mapping[str, Any]] | None = None,
    stability_results: Mapping[str, Mapping[str, Any]] | None = None,
    dq_results: Mapping[str, Mapping[str, Any]] | None = None,
    metadata_table: str = CATALOGUE_TABLE,
    mode: str = "append",
) -> dict[str, str]:
    """Enrich profile rows with guardrail context and write catalogue evidence.

    Parameters
    ----------
    profiles : mapping of str to DataFrame
        Profile DataFrames produced by ``profile_dataframe`` for each dataset.
    dataset_definitions : mapping of str to mapping
        Source or target definitions containing table, stage, and layer context.
    config, env : object, str
        Metadata lakehouse route from ``00_env_config``.
    run_id : str
        Pipeline run identifier.
    agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, pipeline_name : str, optional
        Governance context added to each catalogue row.
    schema_results, freshness_results, stability_results, dq_results : mapping, optional
        Guardrail results keyed by dataset alias.
    metadata_table : str, default="METADATA_DATA_CATALOGUE"
        Metadata table to append.
    mode : str, default="append"
        Write mode for catalogue evidence.

    Returns
    -------
    dict[str, str]
        Write status keyed by dataset alias.
    """
    from pyspark.sql import functions as F

    audit = _runtime_audit_fields(config, env)
    statuses: dict[str, str] = {}
    for name, profile_df in profiles.items():
        definition = dataset_definitions[name]
        table_name = _definition_name(name, definition)
        dataset_name = str(definition.get("dataset_name") or table_name)
        stage = str(definition.get("stage", "target"))
        stability_result = dict((stability_results or {}).get(name) or {})
        freshness_result = dict((freshness_results or {}).get(name) or {})
        schema_result = dict((schema_results or {}).get(name) or {})
        dq_fields = _dq_summary_fields((dq_results or {}).get(name))
        evidence = _canonical_catalogue_profile_df(profile_df)
        metadata_table_key = _build_metadata_table_key(env, dataset_name, table_name)
        additions = {
            "metadata_table_key": metadata_table_key,
            "environment_name": env,
            "dataset_name": dataset_name,
            "table_name": table_name,
            "layer": str(definition.get("layer", "")),
            "asset_kind": str(definition.get("kind", "lakehouse")),
            "pipeline_name": pipeline_name,
            "profile_run_id": run_id,
            "profile_stage": stage,
            "profile_status": "success",
            "baseline_status": str(stability_result.get("baseline_status", stability_result.get("status", ""))),
            "source_data_change_check": str(definition.get("load_behavior", "")) if stage == "source" else "",
            "target_data_change_check": str(definition.get("load_behavior", "")) if stage == "target" else "",
            "profile_baseline_mode": str(stability_result.get("load_behavior", "")),
            "profiled_at": _now_iso(),
            "agreement_id": agreement_id,
            "contract_version": agreement_contract_version,
            "notebook_registry_id": notebook_registry_id,
            "notebook_id": notebook_id,
            "evidence_role": str(definition.get("evidence_role", f"{stage}_profile")),
            "source_schema_check": str(definition.get("schema_preset", "")) if stage == "source" else "",
            "target_schema_check": str(definition.get("schema_preset", "")) if stage == "target" else "",
            "stability_check_enabled": bool(stability_result.get("stability_check_enabled", False)),
            "load_behavior": str(stability_result.get("load_behavior", definition.get("load_behavior", ""))),
            "watermark_column": str(stability_result.get("watermark_column", definition.get("watermark_column", ""))),
            "freshness_column": str(freshness_result.get("freshness_column", definition.get("freshness_column", ""))),
            "freshness_max_lag_days": str(freshness_result.get("freshness_max_lag_days", definition.get("freshness_max_lag_days", ""))),
            "freshness_status": str(freshness_result.get("freshness_status", freshness_result.get("status", ""))),
            "freshness_can_continue": bool(freshness_result.get("freshness_can_continue", freshness_result.get("can_continue", True))),
            "freshness_message": str(freshness_result.get("freshness_message", freshness_result.get("message", ""))),
            "baseline_run_id": str(stability_result.get("baseline_run_id", "")),
            "stability_status": str(stability_result.get("stability_status", stability_result.get("status", ""))),
            "stability_can_continue": bool(stability_result.get("stability_can_continue", stability_result.get("can_continue", True))),
            "stability_message": str(stability_result.get("stability_message", stability_result.get("message", ""))),
            "stability_difference_summary": str(stability_result.get("stability_difference_summary", "")),
            "source_change_signal_json": json.dumps({"schema": schema_result, "freshness": freshness_result, "stability": stability_result}, default=str, sort_keys=True),
            **dq_fields,
            **audit,
        }
        for column, value in additions.items():
            evidence = evidence.withColumn(column, F.lit(value))
        evidence = evidence.withColumn("metadata_column_key", F.concat_ws("::", F.lit(metadata_table_key), F.col("column_name")))
        write_lakehouse_table(evidence, config, env, "metadata", metadata_table, mode=mode)
        statuses[name] = "written"
    return statuses
```

## Internal implementation summary

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in the internal implementation summary.

    ```text
    write_catalogue_evidence(...)
    ├── _build_metadata_table_key(...)
    │   └── _stable_metadata_key(...)
    ├── _canonical_catalogue_profile_df(...)
    ├── _definition_name(...)
    ├── _dq_summary_fields(...)
    │   └── _now_iso(...)
    │       └── …
    ├── _now_iso(...)
    │   └── _current_audit_timestamp(...)
    │       └── …
    ├── _runtime_audit_fields(...)
    │   ├── _build_runtime_audit_fields(...)
    │   │   └── …
    │   └── _now_iso(...)
    │       └── …
    └── write_lakehouse_table(...)
        ├── _get_store(...)
        ├── _normalize_table_name(...)
        ├── _registered_table_identifier(...)
        │   └── …
        └── _uses_registered_metadata_table(...)
    ```

??? info "Internal helpers used: 14"

    This callable uses 14 internal helpers for audit timestamp, metadata loading, rule parsing, rule evaluation, and other.

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
          <td data-label="Area">Audit timestamp</td>
          <td data-label="Helpers"><code>_build_runtime_audit_fields</code>, <code>_current_audit_timestamp</code>, <code>_get_audit_timezone</code>, <code>_runtime_audit_fields</code>, <code>_validate_audit_timezone</code></td>
          <td data-label="What they do">Resolve and stamp audit time consistently.</td>
        </tr>
        <tr>
          <td data-label="Area">Metadata loading</td>
          <td data-label="Helpers"><code>_build_metadata_table_key</code>, <code>_stable_metadata_key</code></td>
          <td data-label="What they do">Load and identify the metadata or table context needed by the callable.</td>
        </tr>
        <tr>
          <td data-label="Area">Rule parsing</td>
          <td data-label="Helpers"><code>_canonical_catalogue_profile_df</code>, <code>_definition_name</code></td>
          <td data-label="What they do">Normalize stored or user-provided values before applying rules.</td>
        </tr>
        <tr>
          <td data-label="Area">Rule evaluation</td>
          <td data-label="Helpers"><code>_dq_summary_fields</code></td>
          <td data-label="What they do">Convert configured rules into executable checks and evaluation results.</td>
        </tr>
        <tr>
          <td data-label="Area">Other</td>
          <td data-label="Helpers"><code>_context_get</code>, <code>_now_iso</code>, <code>_runtime_context</code>, <code>_safe_str</code></td>
          <td data-label="What they do">Support lower-level implementation details that do not fit the main helper areas.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Audit timestamp helpers"

            **`def _build_runtime_audit_fields(*, config: Any=None, env: str | None=None, timestamp_field: str='_committed_at', user_field: str='_committed_by', workspace_field: str='_workspace_name', notebook_field: str='_notebook_name', metadata_lakehouse_field: str='_metadata_lakehouse_name', activity_field: str='_activity_id', committed_by: str | None=None, committed_at: str | None=None, runtime_context: dict[str, Any] | None=None) -> dict[str, str]`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/metadata.py#L219-L289)

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

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/config.py#L69-L75)

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

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/config.py#L61-L66)

            ```python
            def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
                """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
                if timezone_name is not None:
                    return _validate_audit_timezone(timezone_name)
                value = getattr(config, "audit_timezone", None) if config is not None else None
                return _validate_audit_timezone(value)
            ```

            **`def _runtime_audit_fields(config: Any, env: str) -> dict[str, str]`**

            Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/pipeline.py#L49-L60)

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

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/config.py#L27-L58)

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

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/metadata.py#L149-L150)

            ```python
            def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str:
                return _stable_metadata_key(environment_name, dataset_name, table_name)
            ```

            **`def _stable_metadata_key(*parts: Any) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/metadata.py#L144-L146)

            ```python
            def _stable_metadata_key(*parts: Any) -> str:
                normalized = "|".join(str(part or "").strip().lower() for part in parts)
                return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            ```

        ??? example "Rule parsing helpers"

            **`def _canonical_catalogue_profile_df(profile_df: Any)`**

            Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/pipeline.py#L81-L109)

            ```python
            def _canonical_catalogue_profile_df(profile_df: Any):
                """Return profile evidence using lowercase catalogue column names only."""
                from pyspark.sql import functions as F

                profile_columns = list(getattr(profile_df, "columns", []) or [])
                by_lower = {str(column).lower(): column for column in profile_columns}
                source_map = {
                    "table_name": ("table_name", "TABLE_NAME"),
                    "column_name": ("column_name", "COLUMN_NAME"),
                    "run_timestamp": ("run_timestamp", "RUN_TIMESTAMP"),
                    "data_type": ("data_type", "DATA_TYPE"),
                    "row_count": ("row_count", "ROW_COUNT"),
                    "null_count": ("null_count", "NULL_COUNT"),
                    "null_percent": ("null_percent", "NULL_PERCENT"),
                    "distinct_count": ("distinct_count", "DISTINCT_COUNT"),
                    "distinct_percent": ("distinct_percent", "DISTINCT_PERCENT"),
                    "min_value": ("min_value", "MIN_VALUE"),
                    "max_value": ("max_value", "MAX_VALUE"),
                    "distribution_type": ("distribution_type", "DISTRIBUTION_TYPE"),
                    "distribution_json": ("distribution_json", "DISTRIBUTION_JSON"),
                }
                expressions = []
                for target, candidates in source_map.items():
                    source = next((candidate for candidate in candidates if candidate in profile_columns), None)
                    if source is None:
                        source = next((by_lower[candidate.lower()] for candidate in candidates if candidate.lower() in by_lower), None)
                    if source is not None:
                        expressions.append(F.col(source).alias(target))
                return profile_df.select(*expressions) if expressions else profile_df
            ```

            **`def _definition_name(name: str, definition: Mapping[str, Any]) -> str`**

            Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/pipeline.py#L23-L24)

            ```python
            def _definition_name(name: str, definition: Mapping[str, Any]) -> str:
                return str(definition.get("table_name") or definition.get("name") or name)
            ```

        ??? example "Rule evaluation helpers"

            **`def _dq_summary_fields(dq_result: Mapping[str, Any] | None) -> dict[str, Any]`**

            Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/pipeline.py#L63-L78)

            ```python
            def _dq_summary_fields(dq_result: Mapping[str, Any] | None) -> dict[str, Any]:
                summary = dict((dq_result or {}).get("summary") or {})
                checks = list((dq_result or {}).get("checks") or [])
                failed = [check for check in checks if str(check.get("status", "")).lower() in {"failed", "fail"}]
                warning = [check for check in failed if str(check.get("severity", "")).lower() == "warning"]
                error = [check for check in failed if str(check.get("severity", "")).lower() != "warning"]
                return {
                    "dq_status": str((dq_result or {}).get("status") or "not_run"),
                    "dq_rule_count": int(summary.get("rule_count", len(checks)) or 0),
                    "dq_failed_rule_count": int(summary.get("failed_rule_count", len(failed)) or 0),
                    "dq_warning_rule_count": int(summary.get("warning_rule_count", len(warning)) or 0),
                    "dq_error_rule_count": int(summary.get("error_rule_count", len(error)) or 0),
                    "dq_failed_row_count": int(summary.get("failed_row_count", 0) or 0),
                    "dq_failed_row_percent": float(summary.get("failed_row_percent", 0.0) or 0.0),
                    "dq_checked_at": str(summary.get("checked_at") or _now_iso()),
                }
            ```

        ??? example "Other helpers"

            **`def _context_get(context: Any, *keys: str) -> Any`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/metadata.py#L173-L185)

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

            Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/pipeline.py#L19-L20)

            ```python
            def _now_iso(config: Any = None) -> str:
                return _current_audit_timestamp(config=config)
            ```

            **`def _runtime_context() -> dict[str, Any]`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/metadata.py#L192-L216)

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

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/metadata.py#L188-L189)

            ```python
            def _safe_str(value: Any) -> str:
                return "" if value is None else str(value)
            ```


<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.write_catalogue_evidence`
- Short name: `write_catalogue_evidence`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `451`
- Inbound references count: 1
- Outbound references count: 7

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Catalogue evidence`.
- **inputs:** profiles, dataset definitions, config, env, run_id, agreement context, notebook context, and optional guardrail results.
- **output:** Dictionary of write statuses keyed by dataset alias.
- **side_effects:** Writes METADATA_DATA_CATALOGUE through the configured metadata lakehouse target.
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- `fabricops_kit.metadata._build_metadata_table_key`
- `fabricops_kit.pipeline._canonical_catalogue_profile_df`
- `fabricops_kit.pipeline._definition_name`
- `fabricops_kit.pipeline._dq_summary_fields`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._runtime_audit_fields`

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/pipeline.py#L451-L556">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/pipeline.py#L451-L556</a>
- Start line: `451`
- End line: `556`
- Signature:

```python
def write_catalogue_evidence(profiles: Mapping[str, Any], dataset_definitions: Mapping[str, Mapping[str, Any]], *, config: Any, env: str, run_id: str, agreement_id: str='', agreement_contract_version: str='', notebook_registry_id: str='', notebook_id: str='', pipeline_name: str='', schema_results: Mapping[str, Mapping[str, Any]] | None=None, freshness_results: Mapping[str, Mapping[str, Any]] | None=None, stability_results: Mapping[str, Mapping[str, Any]] | None=None, dq_results: Mapping[str, Mapping[str, Any]] | None=None, metadata_table: str=CATALOGUE_TABLE, mode: str='append') -> dict[str, str]
```

### Internal relationship graph

### Public related functions

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>

### Internal implementation summary

- Internal helper count: 14
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>

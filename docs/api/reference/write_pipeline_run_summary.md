# write_pipeline_run_summary

## Signature

```python
def write_pipeline_run_summary(*, spark: Any, config: Any, env: str, run_id: str, agreement_id: str='', agreement_contract_version: str='', notebook_registry_id: str='', notebook_id: str='', notebook_type: str='02_pipeline', pipeline_name: str='', started_at: str | None=None, completed_at: str | None=None, status: str='completed', source_definitions: Mapping[str, Mapping[str, Any]] | None=None, target_definitions: Mapping[str, Mapping[str, Any]] | None=None, source_schema_results: Mapping[str, Mapping[str, Any]] | None=None, target_schema_results: Mapping[str, Mapping[str, Any]] | None=None, source_freshness_results: Mapping[str, Mapping[str, Any]] | None=None, target_freshness_results: Mapping[str, Mapping[str, Any]] | None=None, source_stability_results: Mapping[str, Mapping[str, Any]] | None=None, target_stability_results: Mapping[str, Mapping[str, Any]] | None=None, source_dq_results: Mapping[str, Mapping[str, Any]] | None=None, target_dq_results: Mapping[str, Mapping[str, Any]] | None=None, lineage_status: str='not_run', catalogue_status: str='not_run', message: str='', metadata_table: str=METADATA_PIPELINE_RUNS_TABLE, mode: str='append') -> dict[str, Any]
```

## Summary

Write one pipeline runtime summary row to metadata.

## Usage note

- Use at the end of 02_pipeline when downstream operators need one metadata record describing the run outcome.

**Do not use when:**

- Not documented yet

**Additional context:**

Writes a compact run-level summary that ties pipeline name, agreement context, guardrail results, lineage, and write outcomes together.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark` | `Any` | Yes | Spark session used to create the one-row summary DataFrame. |
| `config` | `Any` | Yes | Metadata route from ``00_env_config``. |
| `env` | `str` | Yes | Not documented yet |
| `run_id` | `str` | Yes | Pipeline run identifier. |
| `agreement_id` | `str` | No | Agreement and notebook registry context. |
| `agreement_contract_version` | `str` | No | Not documented yet |
| `notebook_registry_id` | `str` | No | Not documented yet |
| `notebook_id` | `str` | No | Not documented yet |
| `notebook_type` | `str` | No | Not documented yet |
| `pipeline_name` | `str` | No | Not documented yet |
| `started_at` | `str \| None` | No | Runtime timestamps. Defaults to current UTC time when omitted. |
| `completed_at` | `str \| None` | No | Not documented yet |
| `status` | `str` | No | Overall pipeline status. |
| `source_definitions` | `Mapping[str, Mapping[str, Any]] \| None` | No | Dataset definitions used to compute source and target counts. |
| `target_definitions` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `source_schema_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Guardrail result dictionaries included in the JSON summary. |
| `target_schema_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `source_freshness_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `target_freshness_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `source_stability_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `target_stability_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `source_dq_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `target_dq_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `lineage_status` | `str` | No | Evidence write statuses and support message. |
| `catalogue_status` | `str` | No | Not documented yet |
| `message` | `str` | No | Not documented yet |
| `metadata_table` | `str` | No | Metadata table that stores runtime summaries. |
| `mode` | `str` | No | Write mode for the runtime summary row. |

## Returns

Runtime summary row that was written.

### Return interpretation

The returned summary shows what run metadata was assembled or written. Compare status and guardrail counts with expected pipeline outcomes.

## Raises / Errors

Not documented yet

### Common failure causes

- Required run identifiers are missing.
- Guardrail result structures are malformed.
- Metadata routing is unavailable.
- The configured summary table cannot be written.

## Example

```python
Not documented yet
```

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
- [Metadata Tables](../../how-fabricops-works/metadata-tables.md)

**Glossary terms**

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **can_continue:** A returned true/false value that tells downstream code whether the pipeline should keep running.
- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## Developer details

- Module: `pipeline`
- Classification: Callable
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `646`
- Signature:

```python
def write_pipeline_run_summary(*, spark: Any, config: Any, env: str, run_id: str, agreement_id: str='', agreement_contract_version: str='', notebook_registry_id: str='', notebook_id: str='', notebook_type: str='02_pipeline', pipeline_name: str='', started_at: str | None=None, completed_at: str | None=None, status: str='completed', source_definitions: Mapping[str, Mapping[str, Any]] | None=None, target_definitions: Mapping[str, Mapping[str, Any]] | None=None, source_schema_results: Mapping[str, Mapping[str, Any]] | None=None, target_schema_results: Mapping[str, Mapping[str, Any]] | None=None, source_freshness_results: Mapping[str, Mapping[str, Any]] | None=None, target_freshness_results: Mapping[str, Mapping[str, Any]] | None=None, source_stability_results: Mapping[str, Mapping[str, Any]] | None=None, target_stability_results: Mapping[str, Mapping[str, Any]] | None=None, source_dq_results: Mapping[str, Mapping[str, Any]] | None=None, target_dq_results: Mapping[str, Mapping[str, Any]] | None=None, lineage_status: str='not_run', catalogue_status: str='not_run', message: str='', metadata_table: str=METADATA_PIPELINE_RUNS_TABLE, mode: str='append') -> dict[str, Any]
```

**Used in templates:**

- `02_pipeline`

**Side effects:**

Writes METADATA_PIPELINE_RUNS through the configured metadata lakehouse target.

**Notes:**

The row is written via ``write_lakehouse_table(..., config, env,
"metadata", metadata_table, mode="append")`` so runtime evidence never
relies on a default attached lakehouse.

## Calls

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- `fabricops_kit.pipeline._definition_name`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._summary_status`

## Internal implementation summary

??? info "Call flow"

    ```text
    write_pipeline_run_summary(...)
    ├── _definition_name(...)
    ├── _now_iso(...)
    │   └── _current_audit_timestamp(...)
    │       └── _get_audit_timezone(...)
    │           └── _validate_audit_timezone(...)
    ├── _summary_status(...)
    └── write_lakehouse_table(...)
        ├── _get_store(...)
        ├── _normalize_table_name(...)
        ├── _registered_table_identifier(...)
        │   ├── _normalize_table_name(...)
        │   └── _quote_identifier(...)
        └── _uses_registered_metadata_table(...)
    ```

??? info "Internal helpers used: 6"

    This callable uses 6 internal helpers for audit timestamp, rule parsing, result summary, and other.

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
          <td data-label="Helpers"><code>_current_audit_timestamp</code>, <code>_get_audit_timezone</code>, <code>_validate_audit_timezone</code></td>
          <td data-label="What they do">Resolve and stamp audit time consistently.</td>
        </tr>
        <tr>
          <td data-label="Area">Rule parsing</td>
          <td data-label="Helpers"><code>_definition_name</code></td>
          <td data-label="What they do">Normalize stored or user-provided values before applying rules.</td>
        </tr>
        <tr>
          <td data-label="Area">Result summary</td>
          <td data-label="Helpers"><code>_summary_status</code></td>
          <td data-label="What they do">Build final statuses, counts, and messages for the caller.</td>
        </tr>
        <tr>
          <td data-label="Area">Other</td>
          <td data-label="Helpers"><code>_now_iso</code></td>
          <td data-label="What they do">Support lower-level implementation details that do not fit the main helper areas.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Audit timestamp helpers"

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

        ??? example "Rule parsing helpers"

            **`def _definition_name(name: str, definition: Mapping[str, Any]) -> str`**

            Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L23-L24)

            ```python
            def _definition_name(name: str, definition: Mapping[str, Any]) -> str:
                return str(definition.get("table_name") or definition.get("name") or name)
            ```

        ??? example "Result summary helpers"

            **`def _summary_status(results: Mapping[str, Mapping[str, Any]]) -> str`**

            Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L27-L46)

            ```python
            def _summary_status(results: Mapping[str, Mapping[str, Any]]) -> str:
                """Return a roll-up status for guardrail result mappings.

                ``baseline_created`` is non-blocking and rolls up as ``passed``. ``skipped``
                is ignored when other concrete results exist and is returned only when all
                supplied results were skipped.
                """
                statuses = {str(result.get("status", "unknown")).lower() for result in results.values()}
                if not statuses:
                    return "not_run"
                concrete = statuses - {"skipped"}
                if not concrete:
                    return "skipped"
                if "failed" in concrete:
                    return "failed"
                if "warning" in concrete:
                    return "warning"
                if concrete <= {"passed", "success", "succeeded", "baseline_created"}:
                    return "passed"
                return ",".join(sorted(concrete))
            ```

        ??? example "Other helpers"

            **`def _now_iso(config: Any=None) -> str`**

            Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L19-L20)

            ```python
            def _now_iso(config: Any = None) -> str:
                return _current_audit_timestamp(config=config)
            ```


## Source link

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L646-L758">View write_pipeline_run_summary on GitHub</a>

```python
def write_pipeline_run_summary(
    *,
    spark: Any,
    config: Any,
    env: str,
    run_id: str,
    agreement_id: str = "",
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    notebook_type: str = "02_pipeline",
    pipeline_name: str = "",
    started_at: str | None = None,
    completed_at: str | None = None,
    status: str = "completed",
    source_definitions: Mapping[str, Mapping[str, Any]] | None = None,
    target_definitions: Mapping[str, Mapping[str, Any]] | None = None,
    source_schema_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_schema_results: Mapping[str, Mapping[str, Any]] | None = None,
    source_freshness_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_freshness_results: Mapping[str, Mapping[str, Any]] | None = None,
    source_stability_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_stability_results: Mapping[str, Mapping[str, Any]] | None = None,
    source_dq_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_dq_results: Mapping[str, Mapping[str, Any]] | None = None,
    lineage_status: str = "not_run",
    catalogue_status: str = "not_run",
    message: str = "",
    metadata_table: str = METADATA_PIPELINE_RUNS_TABLE,
    mode: str = "append",
) -> dict[str, Any]:
    """Write a pipeline runtime summary to metadata.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Spark session used to create the one-row summary DataFrame.
    config, env : object, str
        Metadata route from ``00_env_config``.
    run_id : str
        Pipeline run identifier.
    agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, notebook_type, pipeline_name : str, optional
        Agreement and notebook registry context.
    started_at, completed_at : str, optional
        Runtime timestamps. Defaults to current UTC time when omitted.
    status : str, default="completed"
        Overall pipeline status.
    source_definitions, target_definitions : mapping, optional
        Dataset definitions used to compute source and target counts.
    source_schema_results, target_schema_results, source_freshness_results, target_freshness_results, source_stability_results, target_stability_results, source_dq_results, target_dq_results : mapping, optional
        Guardrail result dictionaries included in the JSON summary.
    lineage_status, catalogue_status, message : str, optional
        Evidence write statuses and support message.
    metadata_table : str, default="METADATA_PIPELINE_RUNS"
        Metadata table that stores runtime summaries.
    mode : str, default="append"
        Write mode for the runtime summary row.

    Returns
    -------
    dict[str, Any]
        The summary row that was written.

    Notes
    -----
    The row is written via ``write_lakehouse_table(..., config, env,
    "metadata", metadata_table, mode="append")`` so runtime evidence never
    relies on a default attached lakehouse.
    """
    completed = completed_at or _now_iso(config)
    started = started_at or completed
    sources = source_definitions or {}
    targets = target_definitions or {}
    source_guardrail_status = _summary_status({**(source_schema_results or {}), **(source_freshness_results or {}), **(source_stability_results or {})})
    target_guardrail_status = _summary_status({**(target_schema_results or {}), **(target_freshness_results or {}), **(target_stability_results or {})})
    dq_status = _summary_status({**(source_dq_results or {}), **(target_dq_results or {})})
    run_summary = {
        "source_schema_results": source_schema_results or {},
        "target_schema_results": target_schema_results or {},
        "source_freshness_results": source_freshness_results or {},
        "target_freshness_results": target_freshness_results or {},
        "source_stability_results": source_stability_results or {},
        "target_stability_results": target_stability_results or {},
        "source_dq_results": source_dq_results or {},
        "target_dq_results": target_dq_results or {},
        "source_tables": [_definition_name(name, definition) for name, definition in sources.items()],
        "target_tables": [_definition_name(name, definition) for name, definition in targets.items()],
    }
    row = {
        "run_id": run_id or str(uuid4()),
        "agreement_id": agreement_id,
        "agreement_contract_version": agreement_contract_version,
        "notebook_registry_id": notebook_registry_id,
        "notebook_id": notebook_id,
        "notebook_type": notebook_type,
        "pipeline_name": pipeline_name,
        "environment_name": env,
        "started_at": started,
        "completed_at": completed,
        "status": status,
        "source_count": len(sources),
        "target_count": len(targets),
        "source_guardrail_status": source_guardrail_status,
        "target_guardrail_status": target_guardrail_status,
        "dq_status": dq_status,
        "lineage_status": lineage_status,
        "catalogue_status": catalogue_status,
        "message": message,
        "run_summary_json": json.dumps(run_summary, default=str, sort_keys=True),
        "created_at": _now_iso(config),
    }
    write_lakehouse_table(spark.createDataFrame([row]), config, env, "metadata", metadata_table, mode=mode)
    return row
```

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.write_pipeline_run_summary`
- Short name: `write_pipeline_run_summary`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `646`
- Inbound references count: 0
- Outbound references count: 4
- Used in templates: 02_pipeline
- Glossary terms: guardrail, can_continue, catalogue evidence, metadata lakehouse

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Runtime summary`.
- **inputs:** spark, config, env, run_id, agreement context, source/target definitions, guardrail results, and evidence statuses.
- **output:** Runtime summary row that was written.
- **side_effects:** Writes METADATA_PIPELINE_RUNS through the configured metadata lakehouse target.
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- `fabricops_kit.pipeline._definition_name`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._summary_status`

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L646-L758">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/pipeline.py#L646-L758</a>
- Start line: `646`
- End line: `758`
- Signature:

```python
def write_pipeline_run_summary(*, spark: Any, config: Any, env: str, run_id: str, agreement_id: str='', agreement_contract_version: str='', notebook_registry_id: str='', notebook_id: str='', notebook_type: str='02_pipeline', pipeline_name: str='', started_at: str | None=None, completed_at: str | None=None, status: str='completed', source_definitions: Mapping[str, Mapping[str, Any]] | None=None, target_definitions: Mapping[str, Mapping[str, Any]] | None=None, source_schema_results: Mapping[str, Mapping[str, Any]] | None=None, target_schema_results: Mapping[str, Mapping[str, Any]] | None=None, source_freshness_results: Mapping[str, Mapping[str, Any]] | None=None, target_freshness_results: Mapping[str, Mapping[str, Any]] | None=None, source_stability_results: Mapping[str, Mapping[str, Any]] | None=None, target_stability_results: Mapping[str, Mapping[str, Any]] | None=None, source_dq_results: Mapping[str, Mapping[str, Any]] | None=None, target_dq_results: Mapping[str, Mapping[str, Any]] | None=None, lineage_status: str='not_run', catalogue_status: str='not_run', message: str='', metadata_table: str=METADATA_PIPELINE_RUNS_TABLE, mode: str='append') -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../write_pipeline_lineage/"><code>fabricops_kit.pipeline.write_pipeline_lineage</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>

### Internal implementation summary

- Internal helper count: 6
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>

# write_pipeline_run_summary

## Purpose

Write one pipeline runtime summary row to metadata.

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
      <td data-label="Details">Use at the end of 02_pipeline to store operational run evidence in METADATA_PIPELINE_RUNS.</td>
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
      <td data-label="Details">Writes METADATA_PIPELINE_RUNS through the configured metadata lakehouse target.</td>
    </tr>
    <tr>
      <td data-label="Item">Related functions</td>
      <td data-label="Details">- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a><br>- <a href="../write_pipeline_lineage/"><code>fabricops_kit.pipeline.write_pipeline_lineage</code></a><br>- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a></td>
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
      <td data-label="Parameter"><code>spark</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Spark session used to create the one-row summary DataFrame.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Metadata route from ``00_env_config``.</td>
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
      <td data-label="Meaning">Agreement and notebook registry context.</td>
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
      <td data-label="Parameter"><code>notebook_type</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>pipeline_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>started_at</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Runtime timestamps. Defaults to current UTC time when omitted.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>completed_at</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>status</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Overall pipeline status.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>source_definitions</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Dataset definitions used to compute source and target counts.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>target_definitions</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>source_schema_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Guardrail result dictionaries included in the JSON summary.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>target_schema_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>source_freshness_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>target_freshness_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>source_stability_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>target_stability_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>source_dq_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>target_dq_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>lineage_status</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Evidence write statuses and support message.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>catalogue_status</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>message</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>metadata_table</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Metadata table that stores runtime summaries.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>mode</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Write mode for the runtime summary row.</td>
    </tr>
  </tbody>
</table>
</div>

## Returns

Runtime summary row that was written.

## Used by

No public or package-local callers detected by the generated dependency graph.

## Calls

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- `fabricops_kit.pipeline._definition_name`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._summary_status`

## Implementation details

### Call flow

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

## Public callable source code

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/pipeline.py#L645-L757">View write_pipeline_run_summary on GitHub</a>

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

## Nested helper functions

??? info "Nested helper functions: 6"

    These helpers support `write_pipeline_run_summary` by handling shared implementation tasks reached from the public call flow; expand the source block only when you need maintainer-level details.

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
          <td data-label="Helper"><code>_definition_name</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/pipeline.py#L23-L24"><code>src/fabricops_kit/pipeline.py#L23-L24</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_now_iso</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/pipeline.py#L19-L20"><code>src/fabricops_kit/pipeline.py#L19-L20</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_current_audit_timestamp</code></td>
          <td data-label="Role">Return the current audit timestamp in the configured audit timezone.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/config.py#L69-L75"><code>src/fabricops_kit/config.py#L69-L75</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_get_audit_timezone</code></td>
          <td data-label="Role">Resolve the configured FabricOps audit timezone, defaulting to UTC.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/config.py#L61-L66"><code>src/fabricops_kit/config.py#L61-L66</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_validate_audit_timezone</code></td>
          <td data-label="Role">Return a valid IANA audit timezone name.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/config.py#L27-L58"><code>src/fabricops_kit/config.py#L27-L58</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_summary_status</code></td>
          <td data-label="Role">Return a roll-up status for guardrail result mappings.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/pipeline.py#L27-L46"><code>src/fabricops_kit/pipeline.py#L27-L46</code></a></td>
        </tr>
      </tbody>
    </table>

    ??? example "View helper source code"

        **`def _definition_name(name: str, definition: Mapping[str, Any]) -> str`**

        Used by `write_pipeline_run_summary` through the implementation path shown above.

        ```python
        def _definition_name(name: str, definition: Mapping[str, Any]) -> str:
            return str(definition.get("table_name") or definition.get("name") or name)
        ```

        **`def _now_iso(config: Any=None) -> str`**

        Used by `write_pipeline_run_summary` through the implementation path shown above.

        ```python
        def _now_iso(config: Any = None) -> str:
            return _current_audit_timestamp(config=config)
        ```

        **`def _current_audit_timestamp(config: Any=None, timezone_name: str | None=None, *, drop_microseconds: bool=True) -> str`**

        Used by `write_pipeline_run_summary` through the implementation path shown above.

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

        Used by `write_pipeline_run_summary` through the implementation path shown above.

        ```python
        def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
            """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
            if timezone_name is not None:
                return _validate_audit_timezone(timezone_name)
            value = getattr(config, "audit_timezone", None) if config is not None else None
            return _validate_audit_timezone(value)
        ```

        **`def _validate_audit_timezone(timezone_name: str | None) -> str`**

        Used by `write_pipeline_run_summary` through the implementation path shown above.

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

        **`def _summary_status(results: Mapping[str, Mapping[str, Any]]) -> str`**

        Used by `write_pipeline_run_summary` through the implementation path shown above.

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
- Source line: `645`
- Inbound references count: 0
- Outbound references count: 4

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
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/pipeline.py#L645-L757">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/pipeline.py#L645-L757</a>
- Start line: `645`
- End line: `757`
- Signature:

```python
def write_pipeline_run_summary(*, spark: Any, config: Any, env: str, run_id: str, agreement_id: str='', agreement_contract_version: str='', notebook_registry_id: str='', notebook_id: str='', notebook_type: str='02_pipeline', pipeline_name: str='', started_at: str | None=None, completed_at: str | None=None, status: str='completed', source_definitions: Mapping[str, Mapping[str, Any]] | None=None, target_definitions: Mapping[str, Mapping[str, Any]] | None=None, source_schema_results: Mapping[str, Mapping[str, Any]] | None=None, target_schema_results: Mapping[str, Mapping[str, Any]] | None=None, source_freshness_results: Mapping[str, Mapping[str, Any]] | None=None, target_freshness_results: Mapping[str, Mapping[str, Any]] | None=None, source_stability_results: Mapping[str, Mapping[str, Any]] | None=None, target_stability_results: Mapping[str, Mapping[str, Any]] | None=None, source_dq_results: Mapping[str, Mapping[str, Any]] | None=None, target_dq_results: Mapping[str, Mapping[str, Any]] | None=None, lineage_status: str='not_run', catalogue_status: str='not_run', message: str='', metadata_table: str=METADATA_PIPELINE_RUNS_TABLE, mode: str='append') -> dict[str, Any]
```

### Internal relationship graph

The human-readable implementation view above is the source of truth for public call flow, public callable source, and collapsed nested helper details.

### Public related functions

- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../write_pipeline_lineage/"><code>fabricops_kit.pipeline.write_pipeline_lineage</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>

### Call flow

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

</details>

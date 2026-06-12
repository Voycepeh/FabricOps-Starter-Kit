# run_table_guardrails

Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.

## When to use this

- Use in 02_pipeline to run source guardrails before transformation and target guardrails before writes while keeping per-table results separated.

## At a glance

**Do not use when:**

- Do not use as a replacement for individual helper calls when debugging one specific guardrail interactively.

**Errors:**

Not documented yet

**Side effects:**

Profiles DataFrames, reads stability/DQ metadata through configured metadata routing, writes catalogue evidence, and may update table config DataFrames with DQ annotations.

## Used in templates

- `02_pipeline`

## Used by

Not documented yet

## Calls

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../enforce_freshness/"><code>fabricops_kit.guardrails.enforce_freshness</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.guardrails.validate_schema</code></a>
- `fabricops_kit.pipeline._build_guardrail_evidence_definitions`
- `fabricops_kit.pipeline._guardrail_can_continue`
- `fabricops_kit.pipeline._table_key`
- `fabricops_kit.pipeline._table_name`
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

## Function details and source

### Function details

- Module: `pipeline`
- Classification: Callable
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `260`
- Signature:

```python
def run_table_guardrails(table_configs: list[dict[str, Any]], *, config: Any, env: str, run_id: str, spark_session: Any, agreement_id: str='', agreement_contract_version: str='', notebook_registry_id: str='', notebook_id: str='', pipeline_name: str='', stop_on_failure: bool=False) -> dict[str, Any]
```

### Parameters

`table_configs` : `list[dict[str, Any]]`, required
: Source or target table configs. Each config must contain ``key``, ``df``, and ``expected_schema``. Optional keys such as ``dataset_name``, ``stage``, ``schema_preset``, ``load_behavior``, ``watermark_column``, ``dq_preset``, ``distribution_columns``, and ``exclude_columns`` control the guardrail behavior.

`config` : `Any`, required
: FabricOps framework configuration from ``00_env_config``.

`env` : `str`, required
: Environment key used for configured metadata routing.

`run_id` : `str`, required
: Current pipeline run identifier.

`spark_session` : `Any`, required
: Spark session used by profile behavior and DQ helpers.

`agreement_id` : `str`, optional
: Governance context written with catalogue evidence.

`agreement_contract_version` : `str`, optional
: Not documented yet

`notebook_registry_id` : `str`, optional
: Not documented yet

`notebook_id` : `str`, optional
: Not documented yet

`pipeline_name` : `str`, optional
: Not documented yet

`stop_on_failure` : `bool`, optional
: When True, collect all guardrail results and catalogue evidence, then stop notebook execution via the standard guardrail stopper if any table cannot continue.

### Returns

Guardrail result bundle with profiles, schema results, freshness results, stability results, DQ results, catalogue status, evidence definitions, summary, can_continue, and failed_tables.

### Notes

This helper intentionally collects all per-table schema, freshness, profile behavior, and DQ
results before reporting blocking failures. DQ results that return an
annotated DataFrame update the corresponding table config ``df`` in place
so downstream writes use the checked DataFrame. Metadata reads and writes
are routed through the configured metadata target by the called helpers.

### Example

```python
source_guardrail_results = run_table_guardrails(SOURCE_TABLES, config=CONFIG, env=ENV_NAME, run_id=RUN_ID, spark_session=spark, stop_on_failure=True)
```

### Public callable source code

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/pipeline.py#L260-L448">View run_table_guardrails on GitHub</a>

```python
def run_table_guardrails(
    table_configs: list[dict[str, Any]],
    *,
    config: Any,
    env: str,
    run_id: str,
    spark_session: Any,
    agreement_id: str = "",
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    pipeline_name: str = "",
    stop_on_failure: bool = False,
) -> dict[str, Any]:
    """Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails.

    Parameters
    ----------
    table_configs : list of dict
        Source or target table configs. Each config must contain ``key``,
        ``df``, and ``expected_schema``. Optional keys such as
        ``dataset_name``, ``stage``, ``schema_preset``, ``load_behavior``,
        ``watermark_column``,
        ``dq_preset``, ``distribution_columns``, and ``exclude_columns``
        control the guardrail behavior.
    config : Any
        FabricOps framework configuration from ``00_env_config``.
    env : str
        Environment key used for configured metadata routing.
    run_id : str
        Current pipeline run identifier.
    spark_session : Any
        Spark session used by profile behavior and DQ helpers.
    agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, pipeline_name : str, optional
        Governance context written with catalogue evidence.
    stop_on_failure : bool, default False
        When True, collect all guardrail results and catalogue evidence, then
        stop notebook execution via the standard guardrail stopper if any table
        cannot continue.

    Returns
    -------
    dict[str, Any]
        Guardrail result bundle containing profiles, schema results, freshness
        results, profile behavior results, DQ results, catalogue status, evidence definitions, concise
        ``summary``, ``can_continue``, and ``failed_tables``. Results remain
        separated by table key and guardrail type.

    Notes
    -----
    This helper intentionally collects all per-table schema, freshness, profile behavior, and DQ
    results before reporting blocking failures. DQ results that return an
    annotated DataFrame update the corresponding table config ``df`` in place
    so downstream writes use the checked DataFrame. Metadata reads and writes
    are routed through the configured metadata target by the called helpers.
    """
    profiles: dict[str, Any] = {}
    schema_results: dict[str, Mapping[str, Any]] = {}
    freshness_results: dict[str, Mapping[str, Any]] = {}
    stability_results: dict[str, Mapping[str, Any]] = {}
    dq_results: dict[str, Mapping[str, Any]] = {}
    failed_tables: list[str] = []
    evidence_definitions = _build_guardrail_evidence_definitions(table_configs)

    for table_config in table_configs:
        table_key = _table_key(table_config)
        table_name = _table_name(table_config)
        dataset_name = table_config.get("dataset_name", table_name)
        stage = table_config.get("stage", "target")
        dataframe = table_config["df"]

        profiles[table_key] = profile_dataframe(
            dataframe,
            table_name=table_name,
            # profile_dataframe automatically excludes FabricOps/DQ technical annotation columns
            # and unions those defaults with any table-specific exclude_columns.
            exclude_columns=table_config.get("exclude_columns"),
            include_distributions=True,
            distribution_columns=table_config.get("distribution_columns"),
            config=config,
            run_timestamp_timezone=table_config.get("run_timestamp_timezone"),
        )

        schema_results[table_key] = validate_schema(
            dataframe,
            table_config["expected_schema"],
            preset=table_config.get("schema_preset", "strict"),
        )

        freshness_results[table_key] = enforce_freshness(
            dataframe,
            table_config.get("freshness_column"),
            table_config.get("freshness_max_lag_days"),
            severity=table_config.get("freshness_severity", "blocking"),
        )

        stability_results[table_key] = enforce_profile_behavior(
            spark_session,
            dataframe,
            CATALOGUE_TABLE,
            dataset_name,
            table_name,
            stage=stage,
            run_id=run_id,
            load_behavior=table_config.get("load_behavior", "append"),
            watermark_column=table_config.get("watermark_column"),
            exclude_columns=table_config.get("exclude_columns"),
            exclude_run_id=run_id,
            config=config,
            env=env,
            current_profile=profiles[table_key],
        )

        if table_config.get("dq_preset", "approved_rules") == "skip":
            dq_results[table_key] = {
                "status": "skipped",
                "can_continue": True,
                "checks": [],
                "message": "DQ guardrail skipped by preset.",
            }
        else:
            dq_results[table_key] = enforce_dq_rules(
                dataframe,
                config,
                env,
                dataset_name,
                table_name,
                spark_session=spark_session,
            )

        if "dataframe" in dq_results[table_key]:
            table_config["df"] = dq_results[table_key]["dataframe"]

        table_can_continue = all(
            _guardrail_can_continue(result)
            for result in (schema_results[table_key], freshness_results[table_key], stability_results[table_key], dq_results[table_key])
        )
        if not table_can_continue:
            failed_tables.append(table_key)

    catalogue_status = write_catalogue_evidence(
        profiles,
        evidence_definitions,
        config=config,
        env=env,
        run_id=run_id,
        agreement_id=agreement_id,
        agreement_contract_version=agreement_contract_version,
        notebook_registry_id=notebook_registry_id,
        notebook_id=notebook_id,
        pipeline_name=pipeline_name,
        schema_results=schema_results,
        freshness_results=freshness_results,
        stability_results=stability_results,
        dq_results=dq_results,
    )

    summary = {
        "schema_results": schema_results,
        "freshness_results": freshness_results,
        "stability_results": stability_results,
        "dq_results": dq_results,
        "catalogue_status": catalogue_status,
        "failed_tables": failed_tables,
    }
    result = {
        "profiles": profiles,
        "schema_results": schema_results,
        "freshness_results": freshness_results,
        "stability_results": stability_results,
        "dq_results": dq_results,
        "catalogue_status": catalogue_status,
        "evidence_definitions": evidence_definitions,
        "summary": summary,
        "can_continue": not failed_tables,
        "failed_tables": failed_tables,
    }

    if stop_on_failure and failed_tables:
        stop_if_failed(
            {
                "status": "failed",
                "can_continue": False,
                "message": "Blocking guardrail failure for table(s): " + ", ".join(failed_tables),
                "failed_tables": failed_tables,
            }
        )

    return result
```

## Internal implementation summary

??? info "Call flow"

    ```text
    run_table_guardrails(...)
    ├── _build_guardrail_evidence_definitions(...)
    │   ├── _table_key(...)
    │   └── _table_name(...)
    ├── _guardrail_can_continue(...)
    ├── _table_key(...)
    ├── _table_name(...)
    ├── enforce_dq_rules(...)
    │   ├── _dq_failed_row_count(...)
    │   │   ├── _dq_failed_expression(...)
    │   │   │   ├── _spark_sql_helpers(...)
    │   │   │   └── _validate_dq_rules(...)
    │   │   │       └── _canonical_dq_rule_type(...)
    │   │   └── _spark_sql_helpers(...)
    │   ├── _dq_summary(...)
    │   │   ├── _current_audit_timestamp(...)
    │   │   │   └── _get_audit_timezone(...)
    │   │   │       └── _validate_audit_timezone(...)
    │   │   └── _summarize_dq_guardrail(...)
    │   ├── _dq_tagged_dataframe(...)
    │   │   ├── _dq_failed_expression(...)
    │   │   │   ├── _spark_sql_helpers(...)
    │   │   │   └── _validate_dq_rules(...)
    │   │   │       └── _canonical_dq_rule_type(...)
    │   │   └── _spark_sql_helpers(...)
    │   ├── _load_active_dq_rules(...)
    │   │   ├── _canonical_dq_rule_type(...)
    │   │   ├── _coerce_rows(...)
    │   │   ├── _latest_dq_rule_versions(...)
    │   │   │   └── _spark_sql_helpers(...)
    │   │   ├── _spark_sql_helpers(...)
    │   │   └── _validate_dq_rules(...)
    │   │       └── _canonical_dq_rule_type(...)
    │   ├── _run_dq_guardrail_checks(...)
    │   │   ├── _dq_check_status(...)
    │   │   ├── _dq_failed_expression(...)
    │   │   │   ├── _spark_sql_helpers(...)
    │   │   │   └── _validate_dq_rules(...)
    │   │   │       └── _canonical_dq_rule_type(...)
    │   │   ├── _spark_sql_helpers(...)
    │   │   └── _validate_dq_rules(...)
    │   │       └── _canonical_dq_rule_type(...)
    │   ├── _summarize_dq_guardrail(...)
    │   └── read_lakehouse_table(...)
    │       ├── _current_database_matches(...)
    │       ├── _get_spark(...)
    │       ├── _get_store(...)
    │       ├── _normalize_table_name(...)
    │       ├── _registered_table_identifier(...)
    │       │   ├── _normalize_table_name(...)
    │       │   └── _quote_identifier(...)
    │       └── _uses_registered_metadata_table(...)
    ├── enforce_freshness(...)
    │   ├── _coerce_date(...)
    │   ├── _iso_date_value(...)
    │   │   └── _coerce_date(...)
    │   └── _max_column_value(...)
    ├── enforce_profile_behavior(...)
    │   ├── _catalogue_value(...)
    │   ├── _guardrail_exclude_columns(...)
    │   ├── _is_greater_than(...)
    │   │   └── _comparable_value(...)
    │   ├── _is_less_than(...)
    │   │   └── _comparable_value(...)
    │   ├── _is_missing_table_error(...)
    │   ├── _latest_catalogue_behavior_profile_row(...)
    │   │   ├── _catalogue_value(...)
    │   │   ├── _is_missing_table_error(...)
    │   │   ├── _row_to_dict(...)
    │   │   └── _string_value(...)
    │   ├── _profile_row_count(...)
    │   │   └── _normalize_profile(...)
    │   │       └── _normalize_profile(...) (recursive)
    │   ├── _profile_watermark_bounds(...)
    │   │   ├── _normalize_profile(...)
    │   │   │   └── _normalize_profile(...) (recursive)
    │   │   └── _string_value(...)
    │   ├── _string_value(...)
    │   ├── profile_dataframe(...)
    │   │   ├── _audit_timestamp_expr(...)
    │   │   │   └── _get_audit_timezone(...)
    │   │   │       └── _validate_audit_timezone(...)
    │   │   ├── _build_distribution_summaries(...)
    │   │   │   ├── _build_categorical_distribution(...)
    │   │   │   ├── _build_numeric_distribution(...)
    │   │   │   └── _numeric_bin_edges(...)
    │   │   ├── _get_audit_timezone(...)
    │   │   │   └── _validate_audit_timezone(...)
    │   │   ├── _get_profiled_columns(...)
    │   │   └── _is_min_max_supported_type(...)
    │   └── read_lakehouse_table(...)
    │       ├── _current_database_matches(...)
    │       ├── _get_spark(...)
    │       ├── _get_store(...)
    │       ├── _normalize_table_name(...)
    │       ├── _registered_table_identifier(...)
    │       │   ├── _normalize_table_name(...)
    │       │   └── _quote_identifier(...)
    │       └── _uses_registered_metadata_table(...)
    ├── profile_dataframe(...)
    │   ├── _audit_timestamp_expr(...)
    │   │   └── _get_audit_timezone(...)
    │   │       └── _validate_audit_timezone(...)
    │   ├── _build_distribution_summaries(...)
    │   │   ├── _build_categorical_distribution(...)
    │   │   ├── _build_numeric_distribution(...)
    │   │   └── _numeric_bin_edges(...)
    │   ├── _get_audit_timezone(...)
    │   │   └── _validate_audit_timezone(...)
    │   ├── _get_profiled_columns(...)
    │   └── _is_min_max_supported_type(...)
    ├── stop_if_failed(...)
    │   └── SchemaDriftError(...)
    ├── validate_schema(...)
    │   ├── _actual_schema(...)
    │   │   └── _normalize_datatype(...)
    │   └── _normalize_datatype(...)
    └── write_catalogue_evidence(...)
        ├── _build_metadata_table_key(...)
        │   └── _stable_metadata_key(...)
        ├── _canonical_catalogue_profile_df(...)
        ├── _definition_name(...)
        ├── _dq_summary_fields(...)
        │   └── _now_iso(...)
        │       └── _current_audit_timestamp(...)
        │           └── _get_audit_timezone(...)
        │               └── _validate_audit_timezone(...)
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

??? info "Internal helpers used: 4"

    This callable uses 4 internal helpers for metadata loading and other.

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
          <td data-label="Helpers"><code>_build_guardrail_evidence_definitions</code>, <code>_table_key</code>, <code>_table_name</code></td>
          <td data-label="What they do">Load and identify the metadata or table context needed by the callable.</td>
        </tr>
        <tr>
          <td data-label="Area">Other</td>
          <td data-label="Helpers"><code>_guardrail_can_continue</code></td>
          <td data-label="What they do">Support lower-level implementation details that do not fit the main helper areas.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Metadata loading helpers"

            **`def _build_guardrail_evidence_definitions(table_configs: list[Mapping[str, Any]]) -> dict[str, dict[str, Any]]`**

            Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/pipeline.py#L228-L257)

            ```python
            def _build_guardrail_evidence_definitions(table_configs: list[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
                """Build catalogue evidence definitions for pipeline table guardrails.

                Parameters
                ----------
                table_configs : list of mapping
                    Source or target table configuration dictionaries. Each item must
                    include ``key`` and normally includes ``table_name``, ``stage``, and
                    optional target write metadata. DataFrame values are intentionally
                    omitted from the returned definitions.

                Returns
                -------
                dict[str, dict[str, Any]]
                    Definitions keyed by table key, suitable for
                    :func:`write_catalogue_evidence`. Target definitions include resolved
                    write-layer, kind, and mode fields when the stage is ``target``.
                """
                definitions: dict[str, dict[str, Any]] = {}
                for table_config in table_configs:
                    table_key = _table_key(table_config)
                    definition = {key: value for key, value in table_config.items() if key != "df"}
                    definition["table_name"] = _table_name(table_config)
                    definition["stage"] = table_config.get("stage", "target")
                    if definition["stage"] == "target":
                        definition["layer"] = table_config.get("target_layer", "unified")
                        definition["kind"] = table_config.get("target_kind", "lakehouse")
                        definition["mode"] = table_config.get("write_mode", "overwrite")
                    definitions[table_key] = definition
                return definitions
            ```

            **`def _table_key(table_config: Mapping[str, Any]) -> str`**

            Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/pipeline.py#L216-L217)

            ```python
            def _table_key(table_config: Mapping[str, Any]) -> str:
                return str(table_config["key"])
            ```

            **`def _table_name(table_config: Mapping[str, Any]) -> str`**

            Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/pipeline.py#L220-L221)

            ```python
            def _table_name(table_config: Mapping[str, Any]) -> str:
                return str(table_config.get("table_name") or table_config.get("target_name") or table_config["key"])
            ```

        ??? example "Other helpers"

            **`def _guardrail_can_continue(result: Mapping[str, Any] | None) -> bool`**

            Source: [`src/fabricops_kit/pipeline.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/pipeline.py#L224-L225)

            ```python
            def _guardrail_can_continue(result: Mapping[str, Any] | None) -> bool:
                return bool((result or {}).get("can_continue", True))
            ```


<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.run_table_guardrails`
- Short name: `run_table_guardrails`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `260`
- Inbound references count: 0
- Outbound references count: 11
- Used in templates: 02_pipeline
- Glossary terms: —

### AI implementation contract

- **required_context:** Requires CONFIG and env from 00_env_config so metadata operations use the configured metadata target.
- **inputs:** table_configs plus config, env, run_id, spark_session, and agreement/notebook context.
- **output:** Guardrail result bundle with profiles, schema results, freshness results, stability results, DQ results, catalogue status, evidence definitions, summary, can_continue, and failed_tables.
- **side_effects:** Profiles DataFrames, reads stability/DQ metadata through configured metadata routing, writes catalogue evidence, and may update table config DataFrames with DQ annotations.
- **failure_modes:** Not documented yet
- **verification:** Verify stop_on_failure=True is used before transformation or writes when blocking guardrails should stop execution.

### Inbound references

Not documented yet

### Outbound references

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../enforce_freshness/"><code>fabricops_kit.guardrails.enforce_freshness</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.guardrails.validate_schema</code></a>
- `fabricops_kit.pipeline._build_guardrail_evidence_definitions`
- `fabricops_kit.pipeline._guardrail_can_continue`
- `fabricops_kit.pipeline._table_key`
- `fabricops_kit.pipeline._table_name`
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/pipeline.py#L260-L448">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/pipeline.py#L260-L448</a>
- Start line: `260`
- End line: `448`
- Signature:

```python
def run_table_guardrails(table_configs: list[dict[str, Any]], *, config: Any, env: str, run_id: str, spark_session: Any, agreement_id: str='', agreement_contract_version: str='', notebook_registry_id: str='', notebook_id: str='', pipeline_name: str='', stop_on_failure: bool=False) -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

- <a href="../prepare_pipeline_table_configs/"><code>fabricops_kit.pipeline.prepare_pipeline_table_configs</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

### Internal implementation summary

- Internal helper count: 4
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>

# setup_metadata_tables

Create or validate all FabricOps metadata tables through one setup action.

## Purpose

Create or validate all FabricOps metadata tables through one setup action.

## At a glance

**Use when:**

- Use after setup_notebook in 00_env_config to create or validate the FabricOps metadata tables required by agreement, profiling, lineage, stability, and governance workflows.

**Do not use when:**

- Do not use for writing business data or pipeline target tables; use write_lakehouse_table or write_warehouse_table for data outputs.

**Example:**

```python
setup_metadata_tables(CONFIG, env="Sandbox", spark_session=spark)
```

**Errors:**

Raises configuration, Spark, or storage errors when metadata routing or table preparation fails.

**Side effects:**

Creates or validates FabricOps metadata tables in the configured metadata lakehouse target.

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
      <td data-label="Meaning">Fabric Spark session used by the table setup helpers.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Shared ``00_env_config`` configuration containing the metadata target.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment key to prepare.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>require_active_steward</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Forwarded to the agreement metadata setup to optionally require an active steward before returning success.</td>
    </tr>
  </tbody>
</table>
</div>

## Returns

Setup result describing metadata table creation or validation status.

## Used by

Not documented yet

## Calls

- `fabricops_kit.config._get_active_metadata_tables`
- `fabricops_kit.config._metadata_tables_from_setup_results`
- `fabricops_kit.config._validate_metadata_table_registration`
- `fabricops_kit.data_agreement._setup_data_agreement_tables`
- `fabricops_kit.governance_review._setup_governance_metadata_tables`
- `fabricops_kit.metadata._setup_notebook_registry_table`

## Implementation details

### Call flow

```text
setup_metadata_tables(...)
├── _get_active_metadata_tables(...)
│   ├── _get_governance_metadata_schemas(...)
│   │   ├── _schema(...)
│   │   │   ├── _spark_types(...)
│   │   │   └── _validate_schema_field_names(...)
│   │   └── _spark_types(...)
│   └── _validate_framework_config(...)
│       ├── _validate_audit_timezone(...)
│       └── FrameworkConfig(...)
├── _metadata_tables_from_setup_results(...)
├── _setup_data_agreement_tables(...)
│   ├── _ensure_metadata_tables(...)
│   │   ├── _coerce_row_dicts(...)
│   │   ├── _config_value(...)
│   │   ├── read_lakehouse_table(...)
│   │   │   ├── _current_database_matches(...)
│   │   │   ├── _get_spark(...)
│   │   │   ├── _get_store(...)
│   │   │   ├── _normalize_table_name(...)
│   │   │   ├── _registered_table_identifier(...)
│   │   │   │   ├── _normalize_table_name(...)
│   │   │   │   └── _quote_identifier(...)
│   │   │   └── _uses_registered_metadata_table(...)
│   │   └── write_lakehouse_table(...)
│   │       ├── _get_store(...)
│   │       ├── _normalize_table_name(...)
│   │       ├── _registered_table_identifier(...)
│   │       │   ├── _normalize_table_name(...)
│   │       │   └── _quote_identifier(...)
│   │       └── _uses_registered_metadata_table(...)
│   └── _list_data_stewards(...)
│       ├── _active_steward(...)
│       │   └── _to_bool(...)
│       ├── _config_value(...)
│       ├── _latest_by_key(...)
│       │   └── _coerce_row_dicts(...)
│       └── read_lakehouse_table(...)
│           ├── _current_database_matches(...)
│           ├── _get_spark(...)
│           ├── _get_store(...)
│           ├── _normalize_table_name(...)
│           ├── _registered_table_identifier(...)
│           │   ├── _normalize_table_name(...)
│           │   └── _quote_identifier(...)
│           └── _uses_registered_metadata_table(...)
├── _setup_governance_metadata_tables(...)
│   ├── _coerce_rows(...)
│   ├── _get_governance_metadata_schemas(...)
│   │   ├── _schema(...)
│   │   │   ├── _spark_types(...)
│   │   │   └── _validate_schema_field_names(...)
│   │   └── _spark_types(...)
│   ├── _is_table_not_found_error(...)
│   ├── _schema_field_names(...)
│   ├── read_lakehouse_table(...)
│   │   ├── _current_database_matches(...)
│   │   ├── _get_spark(...)
│   │   ├── _get_store(...)
│   │   ├── _normalize_table_name(...)
│   │   ├── _registered_table_identifier(...)
│   │   │   ├── _normalize_table_name(...)
│   │   │   └── _quote_identifier(...)
│   │   └── _uses_registered_metadata_table(...)
│   └── write_lakehouse_table(...)
│       ├── _get_store(...)
│       ├── _normalize_table_name(...)
│       ├── _registered_table_identifier(...)
│       │   ├── _normalize_table_name(...)
│       │   └── _quote_identifier(...)
│       └── _uses_registered_metadata_table(...)
├── _setup_notebook_registry_table(...)
│   ├── _coerce_row_dicts(...)
│   ├── _registry_rows_with_defaults(...)
│   │   ├── _coerce_row_dicts(...)
│   │   ├── _notebook_registration_key(...)
│   │   └── _safe_str(...)
│   ├── _rows_for_spark(...)
│   ├── read_lakehouse_table(...)
│   │   ├── _current_database_matches(...)
│   │   ├── _get_spark(...)
│   │   ├── _get_store(...)
│   │   ├── _normalize_table_name(...)
│   │   ├── _registered_table_identifier(...)
│   │   │   ├── _normalize_table_name(...)
│   │   │   └── _quote_identifier(...)
│   │   └── _uses_registered_metadata_table(...)
│   └── write_lakehouse_table(...)
│       ├── _get_store(...)
│       ├── _normalize_table_name(...)
│       ├── _registered_table_identifier(...)
│       │   ├── _normalize_table_name(...)
│       │   └── _quote_identifier(...)
│       └── _uses_registered_metadata_table(...)
└── _validate_metadata_table_registration(...)
    ├── _detect_nested_metadata_delta_folders(...)
    │   └── _get_store(...)
    ├── _get_active_metadata_tables(...)
    │   ├── _get_governance_metadata_schemas(...)
    │   │   ├── _schema(...)
    │   │   │   ├── _spark_types(...)
    │   │   │   └── _validate_schema_field_names(...)
    │   │   └── _spark_types(...)
    │   └── _validate_framework_config(...)
    │       ├── _validate_audit_timezone(...)
    │       └── FrameworkConfig(...)
    ├── _show_tables_for_metadata_lakehouse(...)
    │   └── _get_store(...)
    └── _validate_framework_config(...)
        ├── _validate_audit_timezone(...)
        └── FrameworkConfig(...)
```

## Public callable source code

- Source file path: `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L1044-L1108">View setup_metadata_tables on GitHub</a>

```python
def setup_metadata_tables(
    *,
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    require_active_steward: bool = False,
) -> dict[str, Any]:
    """Prepare all FabricOps metadata tables for the configured environment.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session used by the table setup helpers.
    config : FrameworkConfig or dict
        Shared ``00_env_config`` configuration containing the metadata target.
    env : str
        Environment key to prepare.
    require_active_steward : bool, default=False
        Forwarded to the agreement metadata setup to optionally require an
        active steward before returning success.

    Returns
    -------
    dict[str, Any]
        Combined setup summary keyed by ``data_agreement``,
        ``notebook_registry``, and ``governance``.

    Notes
    -----
    This is the v1 notebook setup action for metadata provisioning. It keeps
    ``00_env_config`` simple while delegating to internal helpers that route all
    metadata reads and writes through the configured metadata lakehouse target.
    """
    from fabricops_kit.data_agreement import _setup_data_agreement_tables
    from fabricops_kit.governance_review import _setup_governance_metadata_tables
    from fabricops_kit.metadata import _setup_notebook_registry_table

    data_agreement = _setup_data_agreement_tables(
        spark=spark,
        config=config,
        env=env,
        require_active_steward=require_active_steward,
    )
    notebook_registry = _setup_notebook_registry_table(spark=spark, config=config, env=env)
    governance = _setup_governance_metadata_tables(spark=spark, config=config, env=env)
    expected_tables = _get_active_metadata_tables(config)
    created_or_checked = _metadata_tables_from_setup_results(data_agreement, notebook_registry, governance)
    registration_validation = _validate_metadata_table_registration(
        spark=spark,
        config=config,
        env=env,
        expected_tables=expected_tables,
    )
    statuses = [data_agreement.get("status"), notebook_registry.get("status"), governance.get("status")]
    registration_status = registration_validation.get("status")
    return {
        "status": "ready" if all(status == "ready" for status in statuses) and registration_status in {"ready", "skipped"} else "not_ready",
        "data_agreement": data_agreement,
        "notebook_registry": notebook_registry,
        "governance": governance,
        "active_metadata_tables": expected_tables,
        "active_metadata_table_count": len(expected_tables),
        "created_or_checked_tables": created_or_checked,
        "registration_validation": registration_validation,
    }
```

## Maintainer internals

??? info "Nested helper functions: 30"

    These nested helpers support `setup_metadata_tables` by handling lower-level implementation steps; expand this section only when maintaining or debugging the package internals.

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
          <td data-label="Helper"><code>_get_active_metadata_tables</code></td>
          <td data-label="Role">Return the canonical active metadata tables prepared by ``00_env_config``.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L898-L925">src/fabricops_kit/config.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_validate_framework_config</code></td>
          <td data-label="Role">Validate and normalize framework configuration input.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L551-L624">src/fabricops_kit/config.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_validate_audit_timezone</code></td>
          <td data-label="Role">Return a valid IANA audit timezone name.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L27-L58">src/fabricops_kit/config.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_get_governance_metadata_schemas</code></td>
          <td data-label="Role">Return typed Spark schemas prepared by ``00_env_config`` for governance.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L152-L195">src/fabricops_kit/governance_review.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_schema</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L140-L143">src/fabricops_kit/governance_review.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_spark_types</code></td>
          <td data-label="Role">Return Spark SQL type classes lazily so package import stays lightweight.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L103-L109">src/fabricops_kit/governance_review.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_validate_schema_field_names</code></td>
          <td data-label="Role">Validate that a metadata schema has no case-insensitive duplicates.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L112-L137">src/fabricops_kit/governance_review.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_metadata_tables_from_setup_results</code></td>
          <td data-label="Role">Return ordered metadata table names from setup helper summaries.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L928-L939">src/fabricops_kit/config.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_validate_metadata_table_registration</code></td>
          <td data-label="Role">Validate that active metadata tables are registered in the Spark catalog.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L1003-L1041">src/fabricops_kit/config.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_detect_nested_metadata_delta_folders</code></td>
          <td data-label="Role">Best-effort warning detector for legacy nested metadata Delta folders.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L980-L1000">src/fabricops_kit/config.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_get_store</code></td>
          <td data-label="Role">Resolve a configured Fabric path for an environment and target.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L627-L667">src/fabricops_kit/config.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_show_tables_for_metadata_lakehouse</code></td>
          <td data-label="Role">Inspect registered tables for the configured metadata lakehouse.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L942-L977">src/fabricops_kit/config.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_setup_data_agreement_tables</code></td>
          <td data-label="Role">Prepare intake tables and report whether agreement intake has a steward.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L451-L485">src/fabricops_kit/data_agreement.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_ensure_metadata_tables</code></td>
          <td data-label="Role">Idempotently create or validate lightweight ``01_agreement`` metadata tables.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L405-L448">src/fabricops_kit/data_agreement.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_coerce_row_dicts</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L397-L402">src/fabricops_kit/data_agreement.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_config_value</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L149-L153">src/fabricops_kit/data_agreement.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_list_data_stewards</code></td>
          <td data-label="Role">List latest append-only steward rows from the metadata lakehouse.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L536-L565">src/fabricops_kit/data_agreement.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_active_steward</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L516-L526">src/fabricops_kit/data_agreement.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_to_bool</code></td>
          <td data-label="Role">Normalize common notebook and metadata boolean representations.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L497-L513">src/fabricops_kit/data_agreement.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_latest_by_key</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L488-L494">src/fabricops_kit/data_agreement.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_setup_governance_metadata_tables</code></td>
          <td data-label="Role">Create or validate governance metadata tables via the configured route.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L221-L255">src/fabricops_kit/governance_review.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_coerce_rows</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L62-L67">src/fabricops_kit/governance_review.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_is_table_not_found_error</code></td>
          <td data-label="Role">Return whether a Spark/read exception clearly means the table is absent.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L198-L218">src/fabricops_kit/governance_review.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_schema_field_names</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L146-L149">src/fabricops_kit/governance_review.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_setup_notebook_registry_table</code></td>
          <td data-label="Role">Create or validate the notebook registry metadata table.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/metadata.py#L61-L130">src/fabricops_kit/metadata.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_coerce_row_dicts</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/metadata.py#L53-L58">src/fabricops_kit/metadata.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_registry_rows_with_defaults</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/metadata.py#L408-L419">src/fabricops_kit/metadata.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_notebook_registration_key</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/metadata.py#L41-L50">src/fabricops_kit/metadata.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_safe_str</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/metadata.py#L188-L189">src/fabricops_kit/metadata.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_rows_for_spark</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/metadata.py#L161-L170">src/fabricops_kit/metadata.py</a></td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source code"

        **`def _get_active_metadata_tables(config: FrameworkConfig | dict[str, Any]) -> list[str]`**

        Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L898-L925)

        ```python
        def _get_active_metadata_tables(config: FrameworkConfig | dict[str, Any]) -> list[str]:
            """Return the canonical active metadata tables prepared by ``00_env_config``.

            The active registry is intentionally source-driven: agreement tables come
            from ``DataAgreementConfig``, notebook registry from ``metadata.py``, and
            governance/pipeline tables from the governance schema registry.
            ``METADATA_DATA_ACCESS`` is documented as optional access-capture metadata
            and is not part of the current active setup registry.
            """
            normalized = _validate_framework_config(config)
            from fabricops_kit.data_agreement import DATA_AGREEMENT_EVIDENCE_TABLE, DATA_AGREEMENT_TABLE, DATA_STEWARD_TABLE
            from fabricops_kit.governance_review import _get_governance_metadata_schemas
            from fabricops_kit.metadata import NOTEBOOK_REGISTRY_TABLE

            metadata_tables = normalized.data_agreement_config.metadata_tables or {}
            tables = [
                str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)),
                str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)),
                str(metadata_tables.get("data_agreement_evidence", DATA_AGREEMENT_EVIDENCE_TABLE)),
                NOTEBOOK_REGISTRY_TABLE,
                *_get_governance_metadata_schemas().keys(),
            ]
            out: list[str] = []
            for table in tables:
                table_name = str(table or "").strip()
                if table_name and table_name not in out:
                    out.append(table_name)
            return out
        ```

        **`def _validate_framework_config(config: FrameworkConfig | dict[str, Any]) -> FrameworkConfig`**

        Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L551-L624)

        ```python
        def _validate_framework_config(config: FrameworkConfig | dict[str, Any]) -> FrameworkConfig:
            """Validate and normalize framework configuration input.

            Parameters
            ----------
            config : FrameworkConfig | dict[str, Any]
                Existing framework config object or compatible mapping containing the
                required user-facing component configs. Framework-only sections may be
                omitted and will use package defaults.

            Returns
            -------
            FrameworkConfig
                Normalized, validated framework config object.

            Raises
            ------
            ValueError
                Raised when required sections are missing, component types are invalid,
                or configured path targets are incomplete.

            Notes
            -----
            Validation checks configuration shape and required FabricStore fields.
            It does not perform external IO or provision Fabric resources.

            Examples
            --------
            >>> normalized = _validate_framework_config(framework_config)
            >>> isinstance(normalized, FrameworkConfig)
            True
            """
            if isinstance(config, FrameworkConfig):
                normalized = config
            elif isinstance(config, dict):
                required_keys = {
                    "path_config",
                    "notebook_runtime_config",
                    "ai_prompt_config",
                }
                missing_keys = sorted(required_keys.difference(config.keys()))
                if missing_keys:
                    raise ValueError(f"Framework config is missing required keys: {', '.join(missing_keys)}.")
                normalized = FrameworkConfig(**config)
            else:
                raise ValueError("config must be a FrameworkConfig object or compatible mapping.")

            if not isinstance(normalized.path_config, PathConfig):
                raise ValueError("path_config must be a PathConfig object.")
            if not isinstance(normalized.notebook_runtime_config, NotebookRuntimeConfig):
                raise ValueError("notebook_runtime_config must be a NotebookRuntimeConfig object.")
            if not isinstance(normalized.ai_prompt_config, AIPromptConfig):
                raise ValueError("ai_prompt_config must be an AIPromptConfig object.")
            if not isinstance(normalized.quality_config, QualityConfig):
                raise ValueError("quality_config must be a QualityConfig object.")
            if not isinstance(normalized.governance_config, GovernanceConfig):
                raise ValueError("governance_config must be a GovernanceConfig object.")
            if not isinstance(normalized.review_workflow_config, ReviewWorkflowConfig):
                raise ValueError("review_workflow_config must be a ReviewWorkflowConfig object.")
            if not isinstance(normalized.lineage_config, LineageConfig):
                raise ValueError("lineage_config must be a LineageConfig object.")
            if not isinstance(normalized.data_agreement_config, DataAgreementConfig):
                raise ValueError("data_agreement_config must be a DataAgreementConfig object.")
            _validate_audit_timezone(normalized.audit_timezone)

            for env_name, targets in normalized.path_config.paths.items():
                if not isinstance(targets, dict) or not targets:
                    raise ValueError(f"Environment '{env_name}' must contain at least one target.")
                for target_name, housepath in targets.items():
                    required = ("workspace_id", "item_id", "name", "kind")
                    if not all(hasattr(housepath, attr) for attr in required):
                        raise ValueError(f"Target '{env_name}/{target_name}' must provide FabricStore fields: {required}.")

            return normalized
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

        **`def _get_governance_metadata_schemas() -> dict[str, Any]`**

        Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L152-L195)

        ```python
        def _get_governance_metadata_schemas() -> dict[str, Any]:
            """Return typed Spark schemas prepared by ``00_env_config`` for governance.

            Returns
            -------
            dict[str, pyspark.sql.types.StructType]
                Physical metadata table names mapped to explicit nullable Spark schemas.

            Notes
            -----
            The bootstrap creates empty Delta tables with these explicit schemas instead
            of inferring all columns from empty strings. It does not seed data,
            duplicate pipeline configuration, or create a data-contract table.
            """
            BooleanType, DoubleType, LongType, StringType, _, _, TimestampType = _spark_types()
            string = StringType()
            long = LongType()
            double = DoubleType()
            boolean = BooleanType()
            timestamp = TimestampType()
            audit = [("_committed_at", string), ("_committed_by", string), ("_workspace_name", string), ("_notebook_name", string), ("_metadata_lakehouse_name", string), ("_activity_id", string)]
            catalogue = [
                ("metadata_table_key", string), ("metadata_column_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string),
                ("layer", string), ("asset_kind", string), ("pipeline_name", string), ("profile_run_id", string), ("profile_stage", string), ("profile_status", string), ("baseline_status", string),
                ("source_data_change_check", string), ("target_data_change_check", string), ("profile_baseline_mode", string), ("data_type", string), ("row_count", long), ("null_count", long), ("distinct_count", long),
                ("distribution_type", string), ("distribution_json", string), ("profiled_at", string), ("run_timestamp", timestamp), ("null_percent", double), ("distinct_percent", double), ("min_value", string), ("max_value", string),
                ("agreement_id", string), ("contract_version", string), ("notebook_registry_id", string), ("notebook_id", string), ("evidence_role", string),
                ("source_schema_check", string), ("target_schema_check", string),
                ("stability_check_enabled", boolean), ("load_behavior", string), ("watermark_column", string),
                ("freshness_column", string), ("freshness_max_lag_days", string), ("freshness_status", string), ("freshness_can_continue", boolean), ("freshness_message", string),
                ("baseline_run_id", string), ("stability_status", string), ("stability_can_continue", boolean), ("stability_message", string), ("stability_difference_summary", string),
                ("source_change_signal_json", string),
                ("dq_status", string), ("dq_rule_count", long), ("dq_failed_rule_count", long), ("dq_warning_rule_count", long), ("dq_error_rule_count", long), ("dq_failed_row_count", long), ("dq_failed_row_percent", double), ("dq_checked_at", string),
                *audit,
            ]
            return {
                CATALOGUE_TABLE: _schema(CATALOGUE_TABLE, catalogue),
                COLUMN_CONTEXT_TABLE: _schema(COLUMN_CONTEXT_TABLE, [("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("business_context", string), ("notes", string), ("review_status", string), ("approved_by", string), ("approved_at", string), ("ai_suggestion_json", string), *audit]),
                DQ_RULES_TABLE: _schema(DQ_RULES_TABLE, [("rule_key", string), ("rule_id", string), ("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("rule_type", string), ("rule_parameters_json", string), ("severity", string), ("description", string), ("is_active", boolean), ("review_status", string), ("approved_by", string), ("approved_at", string), ("ai_suggestion_json", string), ("action_type", string), *audit]),
                COLUMN_CLASSIFICATION_TABLE: _schema(COLUMN_CLASSIFICATION_TABLE, [("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("sensitivity_label", string), ("personal_data_classification", string), ("pii_identifier_type", string), ("handling_requirement", string), ("reasoning", string), ("review_status", string), ("approved_by", string), ("approved_at", string), ("ai_suggestion_json", string), *audit]),
                LINEAGE_TABLE: _schema(LINEAGE_TABLE, [("lineage_id", string), ("dataset_name", string), ("run_id", string), ("source_table", string), ("target_table", string), ("source_table_key", string), ("target_table_key", string), ("transformation_steps_json", string), ("created_at", string), *audit]),
                PIPELINE_RUNS_TABLE: _schema(PIPELINE_RUNS_TABLE, [("run_id", string), ("agreement_id", string), ("agreement_contract_version", string), ("notebook_registry_id", string), ("notebook_id", string), ("notebook_type", string), ("pipeline_name", string), ("environment_name", string), ("started_at", string), ("completed_at", string), ("status", string), ("source_count", long), ("target_count", long), ("source_guardrail_status", string), ("target_guardrail_status", string), ("dq_status", string), ("lineage_status", string), ("catalogue_status", string), ("message", string), ("run_summary_json", string), ("created_at", string)]),
                GOVERNANCE_REVIEWS_TABLE: _schema(GOVERNANCE_REVIEWS_TABLE, [("review_id", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("metadata_table_key", string), ("profile_run_id", string), ("profile_stage", string), ("pipeline_run_id", string), ("agreement_id", string), ("agreement_contract_version", string), ("outcome", string), ("blocker_count", long), ("warning_count", long), ("blockers_json", string), ("warnings_json", string), ("evidence_summary_json", string), ("reviewed_at", string), ("reviewed_by", string), *audit]),
            }
        ```

        **`def _schema(table_name: str, fields: list[tuple[str, Any]])`**

        Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L140-L143)

        ```python
        def _schema(table_name: str, fields: list[tuple[str, Any]]):
            _validate_schema_field_names(table_name, fields)
            _, _, _, _, StructField, StructType, _ = _spark_types()
            return StructType([StructField(name, data_type, True) for name, data_type in fields])
        ```

        **`def _spark_types()`**

        Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L103-L109)

        ```python
        def _spark_types():
            """Return Spark SQL type classes lazily so package import stays lightweight."""
            try:
                from pyspark.sql.types import BooleanType, DoubleType, LongType, StringType, StructField, StructType, TimestampType
            except Exception as exc:  # pragma: no cover - Fabric/runtime dependency guard
                raise RuntimeError("governance metadata schemas require pyspark.sql.types in the active runtime.") from exc
            return BooleanType, DoubleType, LongType, StringType, StructField, StructType, TimestampType
        ```

        **`def _validate_schema_field_names(table_name: str, fields: list[tuple[str, Any]]) -> None`**

        Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L112-L137)

        ```python
        def _validate_schema_field_names(table_name: str, fields: list[tuple[str, Any]]) -> None:
            """Validate that a metadata schema has no case-insensitive duplicates.

            Parameters
            ----------
            table_name : str
                Physical metadata table being prepared.
            fields : list of tuple
                ``(name, data_type)`` pairs used to build a Spark ``StructType``.

            Raises
            ------
            ValueError
                Raised when two or more physical field names collapse to the same
                logical name under Spark/Delta's case-insensitive column resolution.
            """
            logical_names: dict[str, list[str]] = {}
            for name, _data_type in fields:
                logical_names.setdefault(str(name).lower(), []).append(str(name))
            duplicates = {logical: names for logical, names in logical_names.items() if len(names) > 1}
            if duplicates:
                details = "; ".join(f"{logical}: {', '.join(names)}" for logical, names in sorted(duplicates.items()))
                raise ValueError(
                    f"{table_name} schema contains case-insensitive duplicate column names: {details}. "
                    "Use one canonical physical column name for each logical column before creating the Spark StructType."
                )
        ```

        **`def _metadata_tables_from_setup_results(*summaries: dict[str, Any]) -> list[str]`**

        Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L928-L939)

        ```python
        def _metadata_tables_from_setup_results(*summaries: dict[str, Any]) -> list[str]:
            """Return ordered metadata table names from setup helper summaries."""
            tables: list[str] = []
            for summary in summaries:
                for key in ("tables", "table"):
                    value = summary.get(key) if isinstance(summary, dict) else None
                    values = value if isinstance(value, list) else [value] if value else []
                    for table in values:
                        table_name = str(table or "").strip()
                        if table_name and table_name not in tables:
                            tables.append(table_name)
            return tables
        ```

        **`def _validate_metadata_table_registration(*, spark: Any, config: FrameworkConfig | dict[str, Any], env: str, expected_tables: list[str] | None=None) -> dict[str, Any]`**

        Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L1003-L1041)

        ```python
        def _validate_metadata_table_registration(
            *,
            spark: Any,
            config: FrameworkConfig | dict[str, Any],
            env: str,
            expected_tables: list[str] | None = None,
        ) -> dict[str, Any]:
            """Validate that active metadata tables are registered in the Spark catalog."""
            normalized = _validate_framework_config(config)
            expected = list(expected_tables or _get_active_metadata_tables(normalized))
            show_tables = _show_tables_for_metadata_lakehouse(spark=spark, config=normalized, env=env)
            observed = {str(name).lower(): str(name) for name in show_tables.get("tables", [])}
            show_tables_ready = show_tables.get("status") == "ready"
            missing = [table for table in expected if table.lower() not in observed] if show_tables_ready else []
            nested_paths = _detect_nested_metadata_delta_folders(config=normalized, env=env, expected_tables=expected)
            warnings: list[str] = []
            if missing:
                warnings.append("Expected metadata tables were not returned by SHOW TABLES.")
            if nested_paths:
                warnings.append(
                    "Detected legacy nested metadata Delta folders under Tables/<metadata_table>/Unidentified/_delta_log. "
                    "FabricOps will not delete or migrate user data automatically; review and migrate those folders manually if needed. "
                    "New metadata setup writes to registered Lakehouse table paths directly."
                )
            if not show_tables_ready:
                warnings.append(str(show_tables.get("message") or "SHOW TABLES validation was skipped."))
            status = "ready" if show_tables_ready and not missing else "not_ready" if show_tables_ready else "skipped"
            return {
                "status": status,
                "database": show_tables.get("database"),
                "expected_tables": expected,
                "expected_table_count": len(expected),
                "registered_tables": show_tables.get("tables", []),
                "missing_tables": missing,
                "nested_metadata_delta_paths": nested_paths,
                "warnings": warnings,
                "show_tables_statement": show_tables.get("statement"),
                "optional_documented_tables": ["METADATA_DATA_ACCESS"],
            }
        ```

        **`def _detect_nested_metadata_delta_folders(*, config: FrameworkConfig | dict[str, Any], env: str, expected_tables: list[str]) -> list[str]`**

        Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L980-L1000)

        ```python
        def _detect_nested_metadata_delta_folders(*, config: FrameworkConfig | dict[str, Any], env: str, expected_tables: list[str]) -> list[str]:
            """Best-effort warning detector for legacy nested metadata Delta folders."""
            try:
                import notebookutils  # type: ignore
            except Exception:
                return []

            fs = getattr(notebookutils, "fs", None)
            exists = getattr(fs, "exists", None)
            if not callable(exists):
                return []
            metadata_store = _get_store(config=config, env=env, target="metadata")
            nested: list[str] = []
            for table in expected_tables:
                path = f"{metadata_store.root.rstrip('/')}/Tables/{table}/Unidentified/_delta_log"
                try:
                    if exists(path):
                        nested.append(path)
                except Exception:
                    continue
            return nested
        ```

        **`def _get_store(config: FrameworkConfig | PathConfig | None, env: str, target: str) -> Any`**

        Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L627-L667)

        ```python
        def _get_store(config: FrameworkConfig | PathConfig | None, env: str, target: str) -> Any:
            """Resolve a configured Fabric path for an environment and target.

            Parameters
            ----------
            env : str
                Environment key such as ``Sandbox``, ``DE``, or ``Prod``.
            target : str
                Target key such as ``Source``, ``Unified``, ``Product``, or ``Warehouse``.
            config : FrameworkConfig | PathConfig | None
                Configuration that contains environment-to-target path mappings.

            Returns
            -------
            Any
                FabricStore object with ``workspace_id``, ``house_id``, ``house_name``, and ``root``.

            Raises
            ------
            ValueError
                If config is missing, or if the environment/target mapping does not exist.

            Examples
            --------
            >>> get_path("Sandbox", "Source", config=CONFIG)
            Housepath(...)
            """
            if config is None:
                raise ValueError("No Fabric config was provided. Pass a FrameworkConfig or PathConfig instance.")
            paths = config.path_config.paths if isinstance(config, FrameworkConfig) else config.paths
            if env not in paths:
                available_envs = ", ".join(sorted(paths.keys())) or "<none>"
                raise ValueError(
                    f"Environment '{env}' was not found in Fabric config. Available environments: {available_envs}."
                )
            if target not in paths[env]:
                available_targets = ", ".join(sorted(paths[env].keys())) or "<none>"
                raise ValueError(
                    f"Target '{target}' was not found under environment '{env}'. Available targets: {available_targets}."
                )
            return paths[env][target]
        ```

        **`def _show_tables_for_metadata_lakehouse(*, spark: Any, config: FrameworkConfig | dict[str, Any], env: str) -> dict[str, Any]`**

        Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L942-L977)

        ```python
        def _show_tables_for_metadata_lakehouse(*, spark: Any, config: FrameworkConfig | dict[str, Any], env: str) -> dict[str, Any]:
            """Inspect registered tables for the configured metadata lakehouse."""
            metadata_store = _get_store(config=config, env=env, target="metadata")
            if metadata_store.kind != "lakehouse":
                raise ValueError(f"Target '{env}/metadata' is not a lakehouse store.")
            if not hasattr(spark, "sql"):
                return {"status": "skipped", "database": metadata_store.name, "tables": [], "message": "Spark SQL is unavailable in this runtime."}

            statements = [f"SHOW TABLES IN `{str(metadata_store.name).replace('`', '``')}`", "SHOW TABLES"]
            last_error: Exception | None = None
            for statement in statements:
                try:
                    rows = spark.sql(statement).collect()
                    table_names: list[str] = []
                    for row in rows:
                        if hasattr(row, "asDict"):
                            item = row.asDict(recursive=True)
                        elif isinstance(row, dict):
                            item = row
                        else:
                            try:
                                item = dict(row)
                            except Exception:
                                item = {}
                        table_name = item.get("tableName") or item.get("table_name") or item.get("tablename")
                        if table_name is None and not item:
                            try:
                                table_name = row[1]
                            except Exception:
                                table_name = None
                        if table_name:
                            table_names.append(str(table_name))
                    return {"status": "ready", "database": metadata_store.name, "tables": sorted(set(table_names)), "statement": statement}
                except Exception as exc:  # pragma: no cover - depends on Fabric Spark catalog behavior
                    last_error = exc
            return {"status": "skipped", "database": metadata_store.name, "tables": [], "message": f"SHOW TABLES was unavailable: {last_error}"}
        ```

        **`def _setup_data_agreement_tables(*, spark: Any, config: Any, env: str, require_active_steward: bool=False) -> dict[str, Any]`**

        Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L451-L485)

        ```python
        def _setup_data_agreement_tables(*, spark: Any, config: Any, env: str, require_active_steward: bool = False) -> dict[str, Any]:
            """Prepare intake tables and report whether agreement intake has a steward.

            Parameters
            ----------
            spark : pyspark.sql.SparkSession
                Fabric Spark session used for idempotent table setup.
            config : FrameworkConfig or dict
                Configuration containing the metadata lakehouse route and table names.
            env : str
                Environment key configured by ``00_env_config``.
            require_active_steward : bool, default=False
                Raise when no active steward exists instead of returning ``not_ready``.

            Returns
            -------
            dict[str, Any]
                Setup status, checked tables, created tables, message, and active count.

            Notes
            -----
            ``00_env_config`` calls this before ``01_agreement``. Missing tables are created
            empty; no fake steward rows are seeded.
            """
            summary = _ensure_metadata_tables(config, env, spark=spark)
            profiles = _list_data_stewards(config, env, spark_session=spark, active_only=True, missing_ok=True)
            summary["active_steward_count"] = len(profiles)
            if profiles:
                summary["message"] = f"{DATA_STEWARD_TABLE} contains active steward rows. 01_agreement can render both intake widgets."
            else:
                summary["status"] = "not_ready"
                summary["message"] = f"{DATA_STEWARD_TABLE} has no active steward rows yet. Use the 01_agreement Data Steward widget to create one before saving an agreement."
                if require_active_steward:
                    raise ValueError(summary["message"])
            return summary
        ```

        **`def _ensure_metadata_tables(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]`**

        Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L405-L448)

        ```python
        def _ensure_metadata_tables(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]:
            """Idempotently create or validate lightweight ``01_agreement`` metadata tables.

            Parameters
            ----------
            config : FrameworkConfig or dict
                Configured metadata lakehouse route from ``00_env_config``.
            env_name : str
                Environment key configured by ``00_env_config``.
            spark : pyspark.sql.SparkSession
                Fabric Spark session used to create empty Delta tables when missing.

            Returns
            -------
            dict[str, Any]
                Setup summary with checked table names.

            Notes
            -----
            Metadata reads and writes always use the configured ``metadata`` target.
            Existing tables with different schemas require a deliberate migration; this
            helper does not destructively overwrite metadata.
            """
            metadata_tables = _config_value(config, "metadata_tables", {}) or {}
            table_schemas = {
                str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)): DATA_STEWARD_FIELDS,
                str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)): DATA_AGREEMENT_FIELDS,
                str(metadata_tables.get("data_agreement_evidence", DATA_AGREEMENT_EVIDENCE_TABLE)): DATA_AGREEMENT_EVIDENCE_FIELDS,
            }
            created = []
            for table_name, fields in table_schemas.items():
                try:
                    table = read_lakehouse_table(config, env_name, "metadata", table_name, spark_session=spark)
                except Exception:
                    empty_df = spark.createDataFrame([{field: "" for field in fields}]).limit(0)
                    write_lakehouse_table(empty_df, config, env_name, "metadata", table_name, mode="ignore", overwrite_schema=True)
                    table = read_lakehouse_table(config, env_name, "metadata", table_name, spark_session=spark)
                    created.append(table_name)
                rows = [] if hasattr(table, "columns") else _coerce_row_dicts(table)
                columns = list(table.columns) if hasattr(table, "columns") else list(rows[0]) if rows else []
                missing = [field for field in fields if field not in columns]
                if missing:
                    raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing)}. Migrate the table before rendering 01_agreement.")
            return {"status": "ready", "tables": list(table_schemas), "created_tables": created}
        ```

        **`def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]`**

        Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L397-L402)

        ```python
        def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]:
            if rows is None:
                return []
            if hasattr(rows, "collect"):
                rows = rows.collect()
            return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows]
        ```

        **`def _config_value(config: Any, name: str, default: Any) -> Any`**

        Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L149-L153)

        ```python
        def _config_value(config: Any, name: str, default: Any) -> Any:
            agreement_config = getattr(config, "data_agreement_config", config)
            if isinstance(agreement_config, dict):
                return agreement_config.get(name, default)
            return getattr(agreement_config, name, default)
        ```

        **`def _list_data_stewards(config: Any, env_name: str, *, spark_session: Any=None, active_only: bool=True, missing_ok: bool=False) -> list[dict[str, Any]]`**

        Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L536-L565)

        ```python
        def _list_data_stewards(config: Any, env_name: str, *, spark_session: Any = None, active_only: bool = True, missing_ok: bool = False) -> list[dict[str, Any]]:
            """List latest append-only steward rows from the metadata lakehouse.

            Parameters
            ----------
            config : FrameworkConfig or dict
                Metadata lakehouse configuration.
            env_name : str
                Configured environment key.
            spark_session : pyspark.sql.SparkSession, optional
                Fabric Spark session.
            active_only : bool, default=True
                Return only currently effective active steward assignments.
            missing_ok : bool, default=False
                Return an empty list when the table is not available.

            Returns
            -------
            list[dict[str, Any]]
                Latest steward rows sorted by stable ID.
            """
            metadata_tables = _config_value(config, "metadata_tables", {}) or {}
            try:
                rows = read_lakehouse_table(config, env_name, "metadata", str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), spark_session=spark_session)
            except Exception:
                if missing_ok:
                    return []
                raise
            latest = _latest_by_key(rows, "steward_id")
            return [row for row in latest if _active_steward(row)] if active_only else latest
        ```

        **`def _active_steward(row: dict[str, Any]) -> bool`**

        Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L516-L526)

        ```python
        def _active_steward(row: dict[str, Any]) -> bool:
            is_active = row.get("is_active")
            if is_active not in (None, "") and not _to_bool(is_active):
                return False
            today = datetime.now(timezone.utc).date()
            try:
                starts_before_today = not row.get("effective_from") or date.fromisoformat(str(row["effective_from"])[:10]) <= today
                ends_after_today = not row.get("effective_to") or date.fromisoformat(str(row["effective_to"])[:10]) >= today
                return starts_before_today and ends_after_today
            except ValueError as exc:
                raise ValueError(f"{DATA_STEWARD_TABLE} row '{row.get('steward_id', '')}' has an invalid effective date. Use ISO dates.") from exc
        ```

        **`def _to_bool(value: Any) -> bool`**

        Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L497-L513)

        ```python
        def _to_bool(value: Any) -> bool:
            """Normalize common notebook and metadata boolean representations.

            Blank values are treated as false. Any non-blank value outside the
            supported true/false spellings raises a clear validation error instead of
            relying on Python string truthiness.
            """
            if isinstance(value, bool):
                return value
            if value is None:
                return False
            normalized = str(value).strip().lower()
            if normalized in {"true", "1", "yes", "y"}:
                return True
            if normalized in {"", "false", "0", "no", "n"}:
                return False
            raise ValueError(f"Unsupported boolean value: {value!r}. Use true/false, 1/0, yes/no, or y/n.")
        ```

        **`def _latest_by_key(rows: Any, key: str) -> list[dict[str, Any]]`**

        Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/data_agreement.py#L488-L494)

        ```python
        def _latest_by_key(rows: Any, key: str) -> list[dict[str, Any]]:
            latest: dict[str, dict[str, Any]] = {}
            for row in _coerce_row_dicts(rows):
                value = str(row.get(key) or "").strip()
                if value and (value not in latest or str(row.get("_committed_at") or "") >= str(latest[value].get("_committed_at") or "")):
                    latest[value] = row
            return sorted(latest.values(), key=lambda row: str(row.get(key) or "").lower())
        ```

        **`def _setup_governance_metadata_tables(*, spark: Any, config: Any, env: str) -> dict[str, Any]`**

        Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L221-L255)

        ```python
        def _setup_governance_metadata_tables(*, spark: Any, config: Any, env: str) -> dict[str, Any]:
            """Create or validate governance metadata tables via the configured route.

            Parameters
            ----------
            spark : pyspark.sql.SparkSession
                Spark session used to create empty metadata tables when missing.
            config : FrameworkConfig or dict
                ``00_env_config`` configuration that contains the ``metadata`` target.
            env : str
                Environment key to prepare.

            Returns
            -------
            dict[str, Any]
                Setup status, checked tables, and newly created tables.
            """
            created: list[str] = []
            schemas = _get_governance_metadata_schemas()
            for table_name, schema in schemas.items():
                try:
                    table = read_lakehouse_table(config, env, "metadata", table_name, spark_session=spark)
                except Exception as exc:
                    if not _is_table_not_found_error(exc):
                        raise RuntimeError(f"Unable to read governance metadata table {table_name!r}; not attempting creation because the error was not a confirmed table-not-found condition.") from exc
                    empty_df = spark.createDataFrame([], schema=schema)
                    write_lakehouse_table(empty_df, config, env, "metadata", table_name, mode="ignore", overwrite_schema=True)
                    table = read_lakehouse_table(config, env, "metadata", table_name, spark_session=spark)
                    created.append(table_name)
                columns = list(getattr(table, "columns", [])) or (list(_coerce_rows(table)[0]) if _coerce_rows(table) else [])
                fields = _schema_field_names(schema)
                missing = [field for field in fields if field not in columns]
                if missing:
                    raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing)}. Migrate the table before running 03_governance.")
            return {"status": "ready", "tables": list(schemas), "created_tables": created}
        ```

        **`def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]`**

        Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L62-L67)

        ```python
        def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
            if rows_or_df is None:
                return []
            if hasattr(rows_or_df, "collect"):
                rows_or_df = rows_or_df.collect()
            return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows_or_df]
        ```

        **`def _is_table_not_found_error(exc: Exception) -> bool`**

        Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L198-L218)

        ```python
        def _is_table_not_found_error(exc: Exception) -> bool:
            """Return whether a Spark/read exception clearly means the table is absent."""
            error_class_getter = getattr(exc, "getErrorClass", None)
            try:
                error_class = str(error_class_getter() or "") if callable(error_class_getter) else ""
            except Exception:
                error_class = ""
            if error_class.upper() in {"PATH_NOT_FOUND", "TABLE_OR_VIEW_NOT_FOUND", "DELTA_TABLE_NOT_FOUND"}:
                return True
            message = str(exc).lower()
            not_found_markers = (
                "path does not exist",
                "path_not_found",
                "table_or_view_not_found",
                "table not found",
                "no such file or directory",
                "doesn't exist",
                "does not exist",
            )
            non_not_found_markers = ("permission", "access denied", "unauthorized", "forbidden", "authentication", "credential", "malformed", "invalid configuration")
            return any(marker in message for marker in not_found_markers) and not any(marker in message for marker in non_not_found_markers)
        ```

        **`def _schema_field_names(schema: Any) -> list[str]`**

        Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/governance_review.py#L146-L149)

        ```python
        def _schema_field_names(schema: Any) -> list[str]:
            if hasattr(schema, "fieldNames"):
                return list(schema.fieldNames())
            return [field.name for field in getattr(schema, "fields", [])]
        ```

        **`def _setup_notebook_registry_table(*, spark: Any, config: Any, env: str, metadata_table: str=NOTEBOOK_REGISTRY_TABLE) -> dict[str, Any]`**

        Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/metadata.py#L61-L130)

        ```python
        def _setup_notebook_registry_table(
            *, spark: Any, config: Any, env: str, metadata_table: str = NOTEBOOK_REGISTRY_TABLE
        ) -> dict[str, Any]:
            """Create or validate the notebook registry metadata table.

            Parameters
            ----------
            spark : pyspark.sql.SparkSession
                Fabric Spark session used to create an empty table when the registry is
                missing.
            config : FrameworkConfig or dict
                Configuration containing the metadata lakehouse route from
                ``00_env_config``.
            env : str
                Environment key configured by ``00_env_config``.
            metadata_table : str, default=NOTEBOOK_REGISTRY_TABLE
                Physical metadata table name to prepare.

            Returns
            -------
            dict[str, Any]
                Setup status, checked table, schema, and whether the table was created.

            Raises
            ------
            ValueError
                If an existing table is missing required registry columns.

            Notes
            -----
            This helper is separate from ``_setup_data_agreement_tables`` because the
            registry is workflow-notebook bootstrap metadata, not ``01_agreement`` agreement
            intake metadata. Reads and writes use the configured ``metadata`` target
            from ``00_env_config``.
            """
            fields = list(NOTEBOOK_REGISTRY_FIELDS)
            created = False
            try:
                table = read_lakehouse_table(config, env, "metadata", metadata_table, spark_session=spark)
            except Exception:
                empty_df = spark.createDataFrame([{field: "" for field in fields}]).limit(0)
                write_lakehouse_table(empty_df, config, env, "metadata", metadata_table, mode="ignore", overwrite_schema=True)
                table = read_lakehouse_table(config, env, "metadata", metadata_table, spark_session=spark)
                created = True

            rows = _coerce_row_dicts(table)
            columns = list(table.columns) if hasattr(table, "columns") else list(rows[0]) if rows else []
            missing_base = [field for field in NOTEBOOK_REGISTRY_BASE_FIELDS if field not in columns]
            if missing_base:
                raise ValueError(
                    f"{metadata_table} is missing required column(s): {', '.join(missing_base)}. Migrate or recreate the notebook registry table before workflow notebooks register themselves."
                )

            migrated = False
            missing_state = [field for field in NOTEBOOK_REGISTRY_STATE_FIELDS if field not in columns]
            if missing_state:
                migrated_rows = _registry_rows_with_defaults(rows)
                df = spark.createDataFrame(_rows_for_spark(migrated_rows or [{field: "" for field in fields}])).limit(
                    0 if not migrated_rows else len(migrated_rows)
                )
                write_lakehouse_table(df, config, env, "metadata", metadata_table, mode="overwrite", overwrite_schema=True)
                migrated = True
            return {
                "status": "ready",
                "table": metadata_table,
                "schema": fields,
                "created": created,
                "migrated": migrated,
                "created_tables": [metadata_table] if created else [],
            }
        ```

        **`def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]`**

        Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/metadata.py#L53-L58)

        ```python
        def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]:
            if rows is None:
                return []
            if hasattr(rows, "collect"):
                rows = rows.collect()
            return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows]
        ```

        **`def _registry_rows_with_defaults(rows: Any) -> list[dict[str, Any]]`**

        Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/metadata.py#L408-L419)

        ```python
        def _registry_rows_with_defaults(rows: Any) -> list[dict[str, Any]]:
            out = []
            for source in _coerce_row_dicts(rows):
                row = {field: _safe_str(source.get(field)) for field in NOTEBOOK_REGISTRY_BASE_FIELDS}
                row["agreement_contract_version"] = _safe_str(source.get("agreement_contract_version"))
                row["registration_role"] = _safe_str(source.get("registration_role") or "primary")
                row["registration_status"] = _safe_str(source.get("registration_status") or "active")
                row["superseded_at"] = _safe_str(source.get("superseded_at"))
                row["superseded_by_registration_id"] = _safe_str(source.get("superseded_by_registration_id"))
                row["registration_id"] = _safe_str(source.get("registration_id") or _notebook_registration_key(row))
                out.append({field: row.get(field, "") for field in NOTEBOOK_REGISTRY_FIELDS})
            return out
        ```

        **`def _notebook_registration_key(row: dict[str, Any]) -> str`**

        Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/metadata.py#L41-L50)

        ```python
        def _notebook_registration_key(row: dict[str, Any]) -> str:
            parts = [
                str(row.get("workspace_id") or ""),
                str(row.get("notebook_id") or ""),
                str(row.get("notebook_name") or ""),
                str(row.get("agreement_id") or ""),
                str(row.get("agreement_contract_version") or ""),
                str(row.get("registration_role") or ""),
            ]
            return hashlib.sha256("||".join(parts).encode("utf-8")).hexdigest()[:24]
        ```

        **`def _safe_str(value: Any) -> str`**

        Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/metadata.py#L188-L189)

        ```python
        def _safe_str(value: Any) -> str:
            return "" if value is None else str(value)
        ```

        **`def _rows_for_spark(rows: list[dict[str, Any]]) -> list[dict[str, Any]]`**

        Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/metadata.py#L161-L170)

        ```python
        def _rows_for_spark(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
            out = []
            for row in rows or []:
                item = dict(row)
                if isinstance(item.get("approved_at"), datetime):
                    item["approved_at"] = item["approved_at"].isoformat()
                if isinstance(item.get("ai_suggestion_json"), (dict, list)):
                    item["ai_suggestion_json"] = json.dumps(item["ai_suggestion_json"], sort_keys=True)
                out.append(item)
            return out
        ```


<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.config.setup_metadata_tables`
- Short name: `setup_metadata_tables`
- Module: `config`
- Classification: Callable
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source line: `1044`
- Inbound references count: 0
- Outbound references count: 7

### AI implementation contract

- **required_context:** Requires the metadata target from 00_env_config; metadata tables must be routed through CONFIG.path_config paths for the selected env.
- **inputs:** config, env, optional spark_session, and mode/check options used to prepare metadata storage through configured metadata routing.
- **output:** Setup result describing metadata table creation or validation status.
- **side_effects:** Creates or validates FabricOps metadata tables in the configured metadata lakehouse target.
- **failure_modes:** Raises configuration, Spark, or storage errors when metadata routing or table preparation fails.
- **verification:** Verify metadata setup completes before recommending agreement, profiling, lineage, stability, or governance workflows that persist evidence.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config._get_active_metadata_tables`
- `fabricops_kit.config._metadata_tables_from_setup_results`
- `fabricops_kit.config._validate_metadata_table_registration`
- `fabricops_kit.data_agreement._setup_data_agreement_tables`
- `fabricops_kit.governance_review._setup_governance_metadata_tables`
- `fabricops_kit.metadata._setup_notebook_registry_table`

### Raw source metadata

- Source file path: `src/fabricops_kit/config.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L1044-L1108">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L1044-L1108</a>
- Start line: `1044`
- End line: `1108`
- Signature:

```python
def setup_metadata_tables(*, spark: Any, config: FrameworkConfig | dict[str, Any], env: str, require_active_steward: bool=False) -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

- <a href="../setup_notebook/"><code>fabricops_kit.config.setup_notebook</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

### Internal implementation helpers

### Call flow

```text
setup_metadata_tables(...)
├── _get_active_metadata_tables(...)
│   ├── _get_governance_metadata_schemas(...)
│   │   ├── _schema(...)
│   │   │   ├── _spark_types(...)
│   │   │   └── _validate_schema_field_names(...)
│   │   └── _spark_types(...)
│   └── _validate_framework_config(...)
│       ├── _validate_audit_timezone(...)
│       └── FrameworkConfig(...)
├── _metadata_tables_from_setup_results(...)
├── _setup_data_agreement_tables(...)
│   ├── _ensure_metadata_tables(...)
│   │   ├── _coerce_row_dicts(...)
│   │   ├── _config_value(...)
│   │   ├── read_lakehouse_table(...)
│   │   │   ├── _current_database_matches(...)
│   │   │   ├── _get_spark(...)
│   │   │   ├── _get_store(...)
│   │   │   ├── _normalize_table_name(...)
│   │   │   ├── _registered_table_identifier(...)
│   │   │   │   ├── _normalize_table_name(...)
│   │   │   │   └── _quote_identifier(...)
│   │   │   └── _uses_registered_metadata_table(...)
│   │   └── write_lakehouse_table(...)
│   │       ├── _get_store(...)
│   │       ├── _normalize_table_name(...)
│   │       ├── _registered_table_identifier(...)
│   │       │   ├── _normalize_table_name(...)
│   │       │   └── _quote_identifier(...)
│   │       └── _uses_registered_metadata_table(...)
│   └── _list_data_stewards(...)
│       ├── _active_steward(...)
│       │   └── _to_bool(...)
│       ├── _config_value(...)
│       ├── _latest_by_key(...)
│       │   └── _coerce_row_dicts(...)
│       └── read_lakehouse_table(...)
│           ├── _current_database_matches(...)
│           ├── _get_spark(...)
│           ├── _get_store(...)
│           ├── _normalize_table_name(...)
│           ├── _registered_table_identifier(...)
│           │   ├── _normalize_table_name(...)
│           │   └── _quote_identifier(...)
│           └── _uses_registered_metadata_table(...)
├── _setup_governance_metadata_tables(...)
│   ├── _coerce_rows(...)
│   ├── _get_governance_metadata_schemas(...)
│   │   ├── _schema(...)
│   │   │   ├── _spark_types(...)
│   │   │   └── _validate_schema_field_names(...)
│   │   └── _spark_types(...)
│   ├── _is_table_not_found_error(...)
│   ├── _schema_field_names(...)
│   ├── read_lakehouse_table(...)
│   │   ├── _current_database_matches(...)
│   │   ├── _get_spark(...)
│   │   ├── _get_store(...)
│   │   ├── _normalize_table_name(...)
│   │   ├── _registered_table_identifier(...)
│   │   │   ├── _normalize_table_name(...)
│   │   │   └── _quote_identifier(...)
│   │   └── _uses_registered_metadata_table(...)
│   └── write_lakehouse_table(...)
│       ├── _get_store(...)
│       ├── _normalize_table_name(...)
│       ├── _registered_table_identifier(...)
│       │   ├── _normalize_table_name(...)
│       │   └── _quote_identifier(...)
│       └── _uses_registered_metadata_table(...)
├── _setup_notebook_registry_table(...)
│   ├── _coerce_row_dicts(...)
│   ├── _registry_rows_with_defaults(...)
│   │   ├── _coerce_row_dicts(...)
│   │   ├── _notebook_registration_key(...)
│   │   └── _safe_str(...)
│   ├── _rows_for_spark(...)
│   ├── read_lakehouse_table(...)
│   │   ├── _current_database_matches(...)
│   │   ├── _get_spark(...)
│   │   ├── _get_store(...)
│   │   ├── _normalize_table_name(...)
│   │   ├── _registered_table_identifier(...)
│   │   │   ├── _normalize_table_name(...)
│   │   │   └── _quote_identifier(...)
│   │   └── _uses_registered_metadata_table(...)
│   └── write_lakehouse_table(...)
│       ├── _get_store(...)
│       ├── _normalize_table_name(...)
│       ├── _registered_table_identifier(...)
│       │   ├── _normalize_table_name(...)
│       │   └── _quote_identifier(...)
│       └── _uses_registered_metadata_table(...)
└── _validate_metadata_table_registration(...)
    ├── _detect_nested_metadata_delta_folders(...)
    │   └── _get_store(...)
    ├── _get_active_metadata_tables(...)
    │   ├── _get_governance_metadata_schemas(...)
    │   │   ├── _schema(...)
    │   │   │   ├── _spark_types(...)
    │   │   │   └── _validate_schema_field_names(...)
    │   │   └── _spark_types(...)
    │   └── _validate_framework_config(...)
    │       ├── _validate_audit_timezone(...)
    │       └── FrameworkConfig(...)
    ├── _show_tables_for_metadata_lakehouse(...)
    │   └── _get_store(...)
    └── _validate_framework_config(...)
        ├── _validate_audit_timezone(...)
        └── FrameworkConfig(...)
```

</details>

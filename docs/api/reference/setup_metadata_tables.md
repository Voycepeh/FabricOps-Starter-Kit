# `setup_metadata_tables`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Create missing FabricOps metadata tables and check existing table columns and Spark data types.

<div class="reference-docstring-intro" markdown="1">

Creates missing metadata tables and validates existing metadata tables
against the canonical registry for the installed FabricOps version. The
function finds the metadata lakehouse configured for the selected
environment, creates missing tables as empty Delta tables, leaves valid
existing tables in place, reports invalid existing tables as failed, and
returns a setup report.

This function prepares the metadata table structures only. It does not
create business metadata records such as stewards, agreements, catalogue
rows, profiles, lineage events, enrichment records, guardrail rules, or
guardrail results.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/setup_metadata_tables.py:114`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L114-L452">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">00_env_config</span>
</p>

**Used in notebooks:** `00_env_config`

## Usage notes

Use this during setup to create the required metadata tables in the configured metadata lakehouse using predefined Starter Kit schemas.

This prepares the metadata store so downstream notebooks, widgets, lineage logging, evidence capture, and governance steps can write to the expected tables.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def setup_metadata_tables(
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    metadata_schema: str | None=None,
    require_active_steward: bool=False,
    verbose: bool=True,
    raise_on_failure: bool=False,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
setup_result = setup_metadata_tables(spark=spark, config=CONFIG, env=ENVIRONMENT_NAME, metadata_schema=METADATA_SCHEMA)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark` | `Any` | Yes | Spark session used to create empty schema DataFrames and read or write the metadata lakehouse tables. |
| `config` | `FrameworkConfig \| dict[str, Any]` | Yes | FabricOps configuration used to find the selected environment and its metadata lakehouse. |
| `env` | `str` | Yes | Environment whose configured metadata lakehouse should be initialized or validated. |
| `metadata_schema` | `str \| None` | No | Optional explicit schema for schema-enabled metadata lakehouses. When omitted, the configured metadata store schema is used where applicable. |
| `require_active_steward` | `bool` | No | When ``True``, raise if ``METADATA_DATA_STEWARD`` contains no active steward rows after setup. This option does not create a steward record. |
| `verbose` | `bool` | No | Controls whether the concise per-table setup summary is printed. |
| `raise_on_failure` | `bool` | No | When ``True``, raise a ``RuntimeError`` after processing all tables if any table failed creation or validation. |

## Returns

dict[str, Any] setup report after all managed metadata tables have been created or validated, including status, metadata_schema, fully_qualified_tables, created_tables, validated_tables, failed_tables, table_results, data_agreement, governance, and active metadata counts.

### Return interpretation

Use the returned status and per-table results to confirm that the physical metadata layer is ready. The function is primarily used for table-creation and validation side effects, not for registering business datasets.

## Raises / Errors

Raises configuration, Spark, or storage errors when metadata routing or table preparation fails.

### Common failure causes

- Missing or invalid metadata target configuration.
- Spark or Fabric lakehouse context is unavailable.
- The caller lacks permission to create or inspect metadata tables.
- An existing table is missing a required field or has an incompatible Spark field type.
- Nullability and field order are not validated; required field names and Spark data types are validated.
- One table can fail while later tables are still processed; raise_on_failure raises only after processing all tables.

## Notes

<div class="reference-docstring-notes" markdown="1">

Setup flow:

1. Validate the supplied FabricOps configuration.
2. Find the metadata lakehouse configured for the selected environment.
3. Verify that the metadata target is a lakehouse.
4. Resolve the metadata schema from ``metadata_schema`` or the configured
   metadata store.
5. Load the required FabricOps table definitions.
6. Attempt to read each required metadata table.
7. When a table is missing, create an empty Spark DataFrame using its
   required FabricOps table structure.
8. Write that empty DataFrame to the metadata lakehouse using overwrite
   mode to create the table.
9. Read the created table again.
10. Validate required column names and physical Spark data types.
11. Continue processing the remaining tables when one table fails.
12. Check whether at least one active steward record exists.
13. Return overall, data-agreement, governance, and per-table setup
    results.

``data_agreement["active_steward_count"]`` is retained for compatibility
and reports readiness presence: ``1`` when at least one active steward
exists and ``0`` otherwise. It is not a complete active steward population
count.

The canonical registry may expand in later compatible FabricOps releases.
In v0.2.0, metadata tables created or validated from
``metadata_table_schema_registry()`` are ``METADATA_DATA_STEWARD``,
``METADATA_DATA_AGREEMENT``, ``METADATA_DATA_CONTRACT``,
``METADATA_DATA_CATALOGUE``, ``METADATA_DATA_PROFILED``,
``METADATA_DATA_PROFILED_FREQUENCY``, ``METADATA_DATA_LINEAGE``, ``METADATA_DATA_ACCESS``,
``METADATA_ENRICHMENT``, ``METADATA_GUARDRAIL``, and
``METADATA_GUARDRAIL_RESULTS`` and ``METADATA_GUARDRAIL_ROW_RESULTS``.

Of that v0.2.0 inventory, ``METADATA_DATA_CATALOGUE``,
``METADATA_DATA_PROFILED``, ``METADATA_DATA_PROFILED_FREQUENCY``, and
``METADATA_DATA_LINEAGE`` are Live schemas with compatibility guarantees.
Every other metadata schema in the registry remains Preview.

Detailed table contents:

- ``METADATA_DATA_STEWARD`` is a person registry storing ``steward_id``,
  ``steward_name``, ``steward_role``, ``contact``, ``is_active``,
  ``custom_fields_json``, and the standard audit fields. Responsibility
  effective periods remain on ``METADATA_DATA_AGREEMENT``.
- ``METADATA_DATA_AGREEMENT`` stores ``agreement_id``,
  ``agreement_version``, ``agreement_name``, ``domain``,
  ``provider_steward_id``, ``recipient_steward_id``, ``recipient``,
  ``start_date``, ``expiry_date``, ``business_purpose``,
  ``custom_fields_json``, and the standard audit fields.
- ``METADATA_DATA_CONTRACT`` stores one immutable, versioned governed-table
  definition through ``contract_id``, ``contract_version``, the exact
  ``agreement_id`` and ``agreement_version``, ``table_id``,
  ``contract_payload_json``, lifecycle status, activation state, and the
  standard audit fields.
- ``METADATA_DATA_CATALOGUE`` stores the current structural registry through
  ``metadata_level``, ``table_id``, ``column_id``, ``environment_name``,
  physical table context, ``column_name``, ``data_type``, profiling dates,
  activation state, and the standard audit fields.
- ``METADATA_DATA_PROFILED`` stores ``profile_id``,
  ``profile_snapshot_id``, ``table_id``, ``column_id``,
  ``environment_name``, ``data_type``,
  ``row_count``, ``non_null_count``, ``null_count``, ``null_percent``,
  ``distinct_count``, ``distinct_percent``, ``mean_value``,
  ``stddev_value``, ``min_value``, ``percentile_25_value``,
  ``median_value``, ``percentile_75_value``, ``max_value``,
  and the standard audit fields.
- ``METADATA_DATA_PROFILED_FREQUENCY`` stores one flattened row per
  distinct profiled value with ``metadata_column_key``, value, count,
  percentage, rank, profiled row totals, ``profiled_at``, and audit fields.
  Join historical snapshots to ``METADATA_DATA_PROFILED`` through both
  ``metadata_column_key`` and ``profiled_at``.
- ``METADATA_DATA_LINEAGE`` stores ``lineage_event_id``, ``activity_id``,
  ``notebook_id``, ``notebook_name``, ``workspace_id``,
  ``workspace_name``, ``metadata_table_key``, ``schema_fingerprint``,
  ``profile_role``, ``profiled_at``, ``committed_by``,
  ``environment_name``, ``metadata_lakehouse_name``, and the standard
  audit fields.
- ``METADATA_DATA_ACCESS`` stores access scope, role, permission,
  approval, expiry, table and column identity, and audit information.
- ``METADATA_ENRICHMENT`` stores business metadata enrichment,
  classification, sensitivity, ownership, governance review, activation,
  effective dates, and audit information.
- ``METADATA_GUARDRAIL`` stores guardrail rule identity, scope,
  parameters, severity, lifecycle, governance review, approval, effective
  dates, and audit information.
- ``METADATA_GUARDRAIL_RESULTS`` stores guardrail execution results,
  status, continuation decision, expected and actual values, result
  payload, and audit information.
- ``METADATA_GUARDRAIL_ROW_RESULTS`` stores compact failed-row and failed
  DQ-rule evidence linked to its rule/run summary without copying complete
  source rows.

Standard audit fields are ``_committed_by``, ``_committed_at``,
``_workspace_id``, ``_workspace_name``, ``_notebook_id``,
``_notebook_name``, ``_metadata_lakehouse_name``, and ``_activity_id``.

Existing tables are validated for required column names and
compatible Spark data types. Physical Spark/Delta nullability is
intentionally not compared because persisted Fabric tables may report
fields as nullable regardless of the canonical logical requirement. The
legacy ``frequency_json`` column specifically fails
``METADATA_DATA_PROFILED`` validation; unrelated
metadata tables continue to permit additive columns.
Because normalized frequency persistence is a breaking physical-schema
change, existing metadata tables may need recreation through this setup
flow; no automatic migration is performed.
Existing tables are not automatically overwritten merely because they
already exist. Missing columns or incompatible types mark that table as
failed, processing continues for remaining metadata tables, and
``raise_on_failure=True`` raises only after all tables have been processed
when failures exist.

A missing table is created by writing an empty Spark DataFrame with the
required FabricOps table structure. This creates the metadata table structure but
does not populate business metadata records. The function does not
automatically create steward records, agreements, contracts, catalogue
records, profile records, lineage events, access assignments, enrichment
records, guardrail rules, or guardrail results; those are populated by
their respective FabricOps workflows.

</div>

## See also

- [Templates](../../notebook-templates.md)
- [Metadata Tables](../../reference/metadata.md)


<details>
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.2.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 35 |

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.1.0 |
| Live | 0.2.0 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.metadata_schemas.audit_schema_fields</code></li>
<li><code>fabricops_kit.config.metadata_schemas.build_metadata_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_schema_type_name</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_field_names</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_schema_registry</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._active_steward_presence</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._print_setup_summary</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._result</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._schema_fields_by_name</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._validate_existing_metadata_schema</code></li>
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared._validate_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.is_table_not_found_error</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.validate_framework_config</code></li>
<li><code>fabricops_kit.io.shared._join_lakehouse_area_path</code></li>
<li><code>fabricops_kit.io.shared._normalize_schema_name</code></li>
<li><code>fabricops_kit.io.shared._normalize_table_name</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_schema</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_table_path</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.normalize_write_mode</code></li>
<li><code>fabricops_kit.io.shared.read_delta_path</code></li>
<li><code>fabricops_kit.io.shared.read_lakehouse_table_core</code></li>
<li><code>fabricops_kit.io.shared.repartition_dataframe_for_write</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_lakehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_target_store</code></li>
<li><code>fabricops_kit.io.shared.validate_dataframe_writer</code></li>
<li><code>fabricops_kit.io.shared.write_delta_path</code></li>
<li><code>fabricops_kit.io.shared.write_lakehouse_table_core</code></li>
</ul>


</details>

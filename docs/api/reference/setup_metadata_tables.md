# `setup_metadata_tables`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Create missing FabricOps metadata tables and check existing table columns and Spark data types.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">00_env_config</span>
</p>

## Usage notes

Use after setup_notebook in 00_env_config to create or validate the FabricOps metadata tables required by agreement, profiling, lineage, stability, and governance workflows.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
setup_result = setup_metadata_tables(spark=spark, config=CONFIG, env=ENVIRONMENT_NAME)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def setup_metadata_tables(
    *,
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    require_active_steward: bool=False,
    verbose: bool=True,
    raise_on_failure: bool=False,
) -> dict[str, Any]:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `spark` | `Any` | Yes | `—` | Spark session used to create empty schema DataFrames and read or write the metadata lakehouse tables. |
| `config` | `FrameworkConfig \| dict[str, Any]` | Yes | `—` | FabricOps configuration used to find the selected environment and its metadata lakehouse. |
| `env` | `str` | Yes | `—` | Environment whose configured metadata lakehouse should be initialized or validated. |
| `require_active_steward` | `bool` | No | `False` | When ``True``, raise if ``METADATA_DATA_STEWARD`` contains no active steward rows after setup. This option does not create a steward record. |
| `verbose` | `bool` | No | `True` | Controls whether the concise per-table setup summary is printed. |
| `raise_on_failure` | `bool` | No | `False` | When ``True``, raise a ``RuntimeError`` after processing all tables if any table failed creation or validation. |

</div>

## Returns

dict[str, Any]
    A dictionary summarizing the completed metadata lakehouse setup,
    including the resolved governance and engineering metadata schemas,
    metadata tables checked,
    tables created, additively evolved, successfully validated, failed tables,
    per-table messages, active steward readiness, fully qualified table
    names, and overall setup status. Key fields are ``status``,
    ``data_agreement``, ``governance``, ``engineering``, ``tables``,
    ``table_results``,
    ``metadata_schemas``, ``fully_qualified_tables``, ``created_tables``,
    ``evolved_tables``, ``validated_tables``, ``failed_tables``,
    ``created_or_checked_tables``,
    ``warnings``, ``active_metadata_tables``, and
    ``active_metadata_table_count``.

    ``status`` is ``"ready"`` when no table failures occur,
    ``"partial_failure"`` when some tables succeed and some fail, and
    ``"failed"`` when all table operations fail. ``data_agreement``
    summarizes steward, agreement, and contract readiness. ``governance``
    summarizes governance-authored tables, and ``engineering`` summarizes
    engineering-written tables. Active steward readiness depends on
    whether active steward rows already exist. ``warnings`` contains
    advisory strings for detected retired Preview tables and failed
    retirement probes; these do not change canonical table readiness.

### Return interpretation

Use the returned status and per-table results to confirm that the physical metadata layer is ready and to distinguish tables that were created, evolved, validated, or failed. The function does not register business datasets.

## Raises / Errors

ValueError
    If the configuration is invalid, the resolved ``metadata`` target is
    not a schema-enabled lakehouse, or ``require_active_steward=True`` and
    no active steward rows exist after setup.
RuntimeError
    If ``raise_on_failure=True`` and one or more metadata tables fail
    creation or validation after all tables have been processed.

### Common failure causes

- Missing, invalid, or non-schema-enabled Metadata Lakehouse configuration.
- Spark or Fabric lakehouse context is unavailable.
- The caller lacks permission to create or inspect metadata tables.
- An existing canonical field has an incompatible Spark field type or a known legacy schema requires explicit migration.
- Missing canonical fields are added automatically; nullability and field order are not validated.
- One table can fail while later tables are still processed; raise_on_failure raises only after processing all tables.

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Creates missing metadata tables, additively evolves existing metadata
tables with missing canonical columns, and validates canonical column
types against the registry for the installed FabricOps version. Existing
data and extra physical columns are preserved; incompatible canonical
types and known legacy schemas are reported as failures.

This function prepares the metadata table structures only. It does not
create business metadata records such as stewards, agreements, catalogue
rows, profiles, lineage events, enrichment records, guardrail rules, or
guardrail results.

</div>

## See also

- [Templates](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks)
- [Metadata Tables](../../reference/metadata.md)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/setup_metadata_tables.py:219`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L219-L627">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

Setup flow:

1. Validate the supplied FabricOps configuration.
2. Find the metadata lakehouse configured for the selected environment.
3. Verify that the metadata target is a lakehouse.
4. Resolve each table's physical schema from its canonical ownership and
   the configured governance/engineering schema names.
5. Load the required FabricOps table definitions.
6. Attempt to read each required metadata table.
7. When a table is missing, create an empty Spark DataFrame using its
   required FabricOps table structure.
8. Write that empty DataFrame to the metadata lakehouse using overwrite
   mode to create the table.
9. Read the created table again.
10. Validate overlapping canonical column names and physical Spark data types.
11. Add missing canonical columns with an empty Delta append using
    ``mergeSchema=true``, then read and validate the table again.
12. Continue processing the remaining tables when one table fails.
13. Check whether at least one active steward record exists.
14. Return overall, data-agreement, governance, and per-table setup
    results.

``data_agreement["active_steward_count"]`` is retained for compatibility
and reports readiness presence: ``1`` when at least one active steward
exists and ``0`` otherwise. It is not a complete active steward population
count.

The current metadata tables created or validated from
``metadata_table_schema_registry()`` are ``METADATA_DATA_STEWARD``,
``METADATA_DATA_AGREEMENT``, ``METADATA_DATA_CONTRACT``,
``METADATA_ACTIVATION_STATE``, ``METADATA_PIPELINE_REGISTRY``, ``METADATA_PIPELINE_RUN``,
``METADATA_DATA_CATALOGUE``, ``METADATA_DATA_PROFILED``,
``METADATA_DATA_PROFILED_FREQUENCY``, ``METADATA_DATA_LINEAGE``, ``METADATA_DATA_ACCESS``,
``METADATA_GUARDRAIL_RESULTS``, and ``METADATA_PROCESSING_STATE``.

Of that inventory, ``METADATA_DATA_CATALOGUE``,
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
- ``METADATA_DATA_CONTRACT`` stores one table-centric lifecycle version.
  A draft keeps its complete editable governed definition in
  ``contract_payload_json``, including descriptive Enrichment and executable
  Guardrails; each Save overwrites that draft JSON in place.
  Separate definition tables are neither required nor deleted by setup.
  Freezing changes the version to ``frozen`` and makes its JSON immutable.
  A later version is seeded from the previous frozen JSON. Activation keeps
  ``status='frozen'`` and uses ``is_active`` to identify the Production
  version while linking the exact Data Agreement version.
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
- ``METADATA_DATA_PROFILED_FREQUENCY`` stores frequency rows through
  ``frequency_id``, ``profile_id``, ``profile_snapshot_id``, value, count,
  percentage, rank, profiled row totals, and the standard audit fields.
- ``METADATA_DATA_LINEAGE`` stores ``lineage_id``, canonical ``table_id``,
  ``environment_name``, ``pipeline_role``, and the
  standard audit fields.
- ``METADATA_DATA_ACCESS`` stores access scope, role, permission,
  approval, expiry, table and column identity, and audit information.
- ``METADATA_GUARDRAIL_RESULTS`` stores guardrail execution results,
  status, continuation decision, expected and actual values, result
  payload, and audit information.

Standard audit fields are ``_committed_by``, ``_committed_at``,
``_workspace_id``, ``_workspace_name``, ``_notebook_id``,
``_notebook_name``, ``_metadata_lakehouse_name``, and ``_activity_id``.

The Preview Processing State table is named ``METADATA_PROCESSING_STATE``.
From v0.3.0, ``METADATA_SOURCE_OBSERVATION`` is no longer used.
Setup probes known retired Preview names in both configured metadata schemas
without collecting rows. Detected tables produce advisory cleanup/migration
messages in ``warnings`` and, with ``verbose=True``, in printed output.
Probe errors other than a missing table also produce advisory warnings;
they do not claim the table is absent. No Preview data is automatically
migrated or deleted, and old tables do not block setup. Runtime uses only
canonical tables. Preserve required data before deleting retired tables;
explicitly map incompatible records rather than blindly appending them.

Existing tables are validated by canonical column name and compatible
Spark data type. Physical Spark/Delta nullability is intentionally not
compared or migrated. Missing canonical columns are added automatically
through an empty append with Delta ``mergeSchema=true``; existing rows and
unrelated extra columns are preserved. Existing canonical columns with
incompatible physical types still fail validation. The legacy
``frequency_json`` column specifically fails ``METADATA_DATA_PROFILED``
validation because that normalized-frequency change requires explicit
migration or recreation. Existing tables are never overwritten merely
because their schema differs. Processing continues for remaining metadata
tables, and ``raise_on_failure=True`` raises only after all tables have
been processed when failures exist.

Activation State and Pipeline Registry are seeded with their control row
using error-if-exists creation; repeat initialization validates existing rows
without replacing identity or approval history. A missing ordinary table is
created by writing an empty Spark DataFrame with the
required FabricOps table structure. This creates the metadata table structure but
does not populate business metadata records. The function does not
automatically create steward records, agreements, contracts, catalogue
records, profile records, lineage events, access assignments, enrichment
records, guardrail rules, or guardrail results; those are populated by
their respective FabricOps workflows.

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.2.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 33 |

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.1.0 |
| Live | 0.2.0 |
| Live | 0.2.5 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.activated_pipeline.shared.empty_activation_state</code></li>
<li><code>fabricops_kit.config.audit._audit_timestamp_value</code></li>
<li><code>fabricops_kit.config.audit._context_get</code></li>
<li><code>fabricops_kit.config.audit._require_audit_values</code></li>
<li><code>fabricops_kit.config.audit._valid_audit_value</code></li>
<li><code>fabricops_kit.config.audit.build_runtime_audit_fields</code></li>
<li><code>fabricops_kit.config.metadata_schemas.audit_schema_fields</code></li>
<li><code>fabricops_kit.config.metadata_schemas.build_metadata_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_schema_type_name</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_field_names</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_owner</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_physical_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_schema_registry</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._active_steward_presence</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._add_missing_metadata_columns</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._print_setup_summary</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._result</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._retired_preview_table_warnings</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._schema_fields_by_name</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._table_column_names</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._validate_existing_metadata_schema</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_context</code></li>
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared._validate_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_current_audit_timestamp</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.is_table_not_found_error</code></li>
<li><code>fabricops_kit.config.shared.normalize_audit_datetime</code></li>
<li><code>fabricops_kit.config.shared.resolve_runtime_context</code></li>
<li><code>fabricops_kit.config.shared.validate_framework_config</code></li>
<li><code>fabricops_kit.pipeline.shared.canonical_candidate_json</code></li>
</ul>


</details>

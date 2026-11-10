# `setup_metadata_tables`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Create missing FabricOps metadata tables and check existing table columns and Spark data types.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">`00_env_config`</span>
</p>

## Usage notes

Use after setup_notebook in 00_env_config to create or validate the FabricOps metadata tables required by agreement, profiling, lineage, stability, and governance workflows.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
setup_result = setup_metadata_tables(config=CONFIG, workspace_id=WORKSPACE_ID)
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def setup_metadata_tables(
    *,
    config: FrameworkConfig | dict[str, Any],
    workspace_id: str,
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
| `config` | `FrameworkConfig \| dict[str, Any]` | Yes | `—` | Configuration containing the selected workspace's central Metadata Lakehouse. Metadata must be a schema-enabled Lakehouse. |
| `workspace_id` | `str` | Yes | `—` | Configuration scope used to resolve the Metadata store. |
| `require_active_steward` | `bool` | No | `False` | Require an active Data Steward after table setup. No steward is created. |
| `verbose` | `bool` | No | `True` | Print concise per-table creation, evolution and readiness results. |
| `raise_on_failure` | `bool` | No | `False` | Raise after all tables have been processed when any table fails. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
result = setup_metadata_tables(config=CONFIG, workspace_id=WORKSPACE_ID)
result["status"]
```

```text
'ready'
```

</div>

## Returns

dict[str, Any]
    Overall readiness, configured ownership schemas, canonical table names,
    created/evolved/validated/failed tables, per-table results, steward
    readiness and advisory diagnostics for noncanonical metadata tables.

### Return interpretation

Use the returned status and per-table results to confirm that the physical metadata layer is ready and to distinguish tables that were created, evolved, validated, or failed. The function does not register business datasets.

## Raises / Errors

ValueError
    If configuration is invalid, Metadata is not a schema-enabled Lakehouse,
    or an explicitly required active steward is absent.
RuntimeError
    If Spark is unavailable or raise_on_failure is enabled and a table fails.

### Common failure causes

- Missing, invalid, or non-schema-enabled Metadata Lakehouse configuration.
- Spark or Fabric lakehouse context is unavailable.
- The caller lacks permission to create or inspect metadata tables.
- An existing canonical field has an incompatible Spark field type or an identity or processing schema is structurally incompatible.
- Missing canonical fields are added automatically; nullability and field order are not validated.
- One table can fail while later tables are still processed; raise_on_failure raises only after processing all tables.

## Notes

<div class="reference-docstring-notes" markdown="1">

Missing tables are created empty with error-if-exists semantics. Registry
and Contract Activation use Serializable isolation; Processing State is
created or upgraded to Serializable for atomic Source Drift acceptance.
Setup never manufactures
approvals, populates business metadata, deletes rows or replaces business
targets. Governance definitions and activation are independent workflows.

Compatible missing columns are added automatically. Catalogue and Pipeline
Run collection fields are stored as validated JSON strings; supported native
collections are converted atomically with tracked Delta reads and exact
schema/data readback. Existing rows, audit values, extension fields, table
identity/properties and Delta transaction identities are preserved. Run
provenance additions are nullable and preserve retained content hashes.
Repeated setup validates compliant tables without rewriting them.

Processing State observations, checkpoints, accepted baselines and publication
receipts remain intact. Missing progress is never inferred for populated
targets. Incompatible identity layouts, incorrect types, malformed JSON and
duplicate Run identities fail explicitly with the existing data preserved.
A failure in one table does not prevent validation of the remaining tables.
Physical nullability and field order are not rewritten.

Governed admission remains blocked pending signed-in Fabric acceptance.
Retirement presence diagnostics are advisory; unsupported tables are never
read as canonical authority or automatically deleted.

</div>

## See also

- [Templates](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks)
- [Metadata Tables](../../reference/metadata.md)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/setup_metadata_tables.py:393`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L393-L686">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.2.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 45 |

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.1.0 |
| Live | 0.2.0 |
| Live | 0.2.5 |
| Live | 0.3.0 |
| Live | 0.3.1 |
| Live | 0.4.0 |
| Live | 0.4.1 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.metadata_schemas.audit_schema_fields</code></li>
<li><code>fabricops_kit.config.metadata_schemas.build_metadata_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.decode_metadata_row</code></li>
<li><code>fabricops_kit.config.metadata_schemas.encode_metadata_row</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_json_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_schema_type_name</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_field_names</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_owner</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_physical_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_schema_registry</code></li>
<li><code>fabricops_kit.config.metadata_schemas.parse_metadata_json</code></li>
<li><code>fabricops_kit.config.metadata_schemas.validate_metadata_value</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._active_steward_presence</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._add_missing_metadata_columns</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._parse_catalogue_value</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._print_setup_summary</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._result</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._retired_preview_warnings</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._retired_table_is_missing</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._schema_fields_by_name</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._table_column_names</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._upgrade_json_metadata</code></li>
<li><code>fabricops_kit.config.setup_metadata_tables._validate_existing_metadata_schema</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_context</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_metadata</code></li>
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
<li><code>fabricops_kit.io.shared.resolve_configured_lakehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_store</code></li>
<li><code>fabricops_kit.io.shared.retry_delta_metadata</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_run</code></li>
</ul>


</details>

# `orchestrate_demo_reset`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.5.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Preview or reset Guided Demo data and processing progress to Day 1.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">00C_demo_setup</span>
</p>

## Usage notes

Preview is the default. reset=True discards all dedicated demo metadata, including frozen Contracts and activations, and resets only the eleven named business tables. This Preview API still requires live Fabric acceptance.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
from fabricops_kit import setup_notebook, orchestrate_demo_reset

context = setup_notebook()
RESET_DEMO = False
orchestrate_demo_reset(reset=RESET_DEMO)
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def orchestrate_demo_reset(*, reset: bool=False) -> None
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `reset` | `bool` | No | `False` | False prints configured destinations, scoped metadata counts and the eleven business tables without writing. True resets only those demo tables, their Processing State and profile snapshots after preflight. Only booleans are accepted. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
from fabricops_kit import setup_notebook, orchestrate_demo_reset
context = setup_notebook()
RESET_DEMO = False  # Preview before resetting demo data and progress.
orchestrate_demo_reset(reset=RESET_DEMO)
```

</div>

## Returns

None
    Prints actual removed counts and ``RESET COMPLETE`` after verification.

## Raises / Errors

ValueError
    If reset is not a boolean.
RuntimeError
    If setup, store mappings, required schemas, fixtures or catalog locations
    are invalid, a demo processing record links to a non-demo table, or
    verification fails. Fabric/Spark permission and transport errors propagate.

## Notes

<div class="reference-docstring-notes" markdown="1">

Deletion is restricted by exact demo identities and workspace: execution
workspace for ``misc.PROCESSING_STATE`` and asset workspace for
``METADATA_DATA_PROFILED`` and ``METADATA_DATA_PROFILED_FREQUENCY``. Only
configured mappings to the physical stores being reset participate. No
nested Run or Contract payloads are inspected to authorize deletion.

Contracts, activations, approvals, promotion history, Catalogue, Runs,
Lineage, Guardrail results and saved submissions, Dry Runs and notebook
snapshots are retained, including demo history. Profile snapshots for demo
assets are discarded so standard profiling can run again. Historical grain
and empty-frequency completion markers remain in retained Runs; use a zero
profiling interval when those activities must run again immediately.
This is a data restart, not a restart of governance authoring; use a separate
environment for a fresh governance walkthrough.

Four Day 1 source tables are overwritten. Orders CSV is validated and
retained. Five Silver outputs and obsolete Bronze Orders are removed from
the reserved ``demo`` schemas. Gold customer_summary is retained with zero
rows when present. Other business tables and all source files are preserved.

Preview never writes. Missing outputs and repeated resets are supported.
The reset is not atomic across stores; after a partial failure stop writers,
correct the cause and rerun. Never use it as production recovery. Actual
Microsoft Fabric validation remains required.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Call after ``setup_notebook()``. Stop all executions and schedules using the
reserved demo business tables, including promoted copies, and start fresh
scenario notebook sessions after resetting. A dedicated demo environment
is recommended; the Metadata Lakehouse need not be empty or demo-only.

</div>

## See also

- [Prepare and reset the demo](../../guided-demo/00C-prepare-demo-data-with-fabricops-io.md)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/orchestrate_demo_reset.py:267`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/orchestrate_demo_reset.py#L267-L433">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.5.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 47 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.5.0 |
| Live | 0.5.1 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.metadata_schemas.audit_schema_fields</code></li>
<li><code>fabricops_kit.config.metadata_schemas.build_metadata_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_schema_type_name</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_owner</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_physical_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_schema_registry</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_assert_source</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_check_processing_boundary</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_clear_gold_output</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_clear_metadata</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_gold_output_exists</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_metadata_counts</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_metadata_frame</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_metadata_predicate</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_prepare_gold_empty_output</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_remove_outputs</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_reset_scope</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_verify_outputs</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_context</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_metadata</code></li>
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared.build_table_id</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.stable_metadata_id</code></li>
<li><code>fabricops_kit.data_contract.shared.file_source_identity</code></li>
<li><code>fabricops_kit.io.shared._build_warehouse_object_name</code></li>
<li><code>fabricops_kit.io.shared._join_lakehouse_area_path</code></li>
<li><code>fabricops_kit.io.shared._normalize_schema_name</code></li>
<li><code>fabricops_kit.io.shared._normalize_table_name</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_schema</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_table_path</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.read_delta_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_lakehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_store</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_name</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_table_location</code></li>
<li><code>fabricops_kit.pipeline.shared.processing_state_path</code></li>
<li><code>fabricops_kit.pipeline.shared.processing_state_schema</code></li>
<li><code>fabricops_kit.pipeline.shared.read_processing_state</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_physical_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_processing_state_schema</code></li>
</ul>


</details>

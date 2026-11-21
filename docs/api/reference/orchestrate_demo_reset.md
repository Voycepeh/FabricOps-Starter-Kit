# `orchestrate_demo_reset`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.5.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Preview or reset the dedicated Guided Demo to Day 1.

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
| `reset` | `bool` | No | `False` | False prints configured store identities, metadata row counts and the eleven business tables in scope without writing. True opts into the destructive reset after all preflight checks pass. Only booleans are accepted; strings and integers are rejected. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
from fabricops_kit import setup_notebook, orchestrate_demo_reset
context = setup_notebook()
RESET_DEMO = False  # Set True only to discard the dedicated demo state.
orchestrate_demo_reset(reset=RESET_DEMO)
```

</div>

## Returns

None
    Prints a preview or verified reset summary, including actual removed
    metadata counts. ``RESET COMPLETE`` is printed only after verification.

## Raises / Errors

ValueError
    If reset is not a boolean.
RuntimeError
    If notebook setup is not ready, required stores or metadata schemas
    are invalid, non-demo references are found, fixtures
    are unavailable, or reset verification fails. Fabric/Spark permission,
    transport and storage failures propagate; correct the cause and rerun.

## Notes

<div class="reference-docstring-notes" markdown="1">

True clears all current canonical metadata rows in the dedicated item,
including frozen Contracts, activations, approvals, promotion history and
Runs. It also clears the dedicated Processing State table. Saved submissions, Dry Run evidence and notebook
snapshots in its three native lifecycle folders are removed too. Table
definitions remain; no metadata migration is performed. Historical Lineage
activity rows remain intact; only lineage_version=1 dependency facts are cleared.

Four Day 1 tables are overwritten, Orders CSV is validated and retained,
and five Silver outputs plus the obsolete Bronze Orders table are removed in the reserved
``demo`` schemas of the configured Bronze/Silver stores. The Gold customer_summary
table is retained with zero rows when present. Other business
tables and source files are preserved. Exact demo table/workspace references,
artifact contents, fixture counts and catalog locations are
checked before deletion. A dedicated name alone cannot prove ownership;
never share this Metadata item or these eleven tables with other projects.

Missing outputs and repeated resets are supported. A failure may leave a
partial reset: this operation is not atomic across tables/stores. Stop all
writers, correct the reported cause and rerun. Deployed notebooks, schedules
and apps are not removed. Live Fabric acceptance is still required.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Call after ``setup_notebook()`` with the package being validated installed.
The configured logical ``Metadata`` store must select a manually created,
schema-enabled Lakehouse named ``demo_metadata``, reserved exclusively for
this walkthrough. Stop all demo executions and schedules before resetting.

</div>

## See also

- [Prepare and reset the demo](../../guided-demo/00C-prepare-demo-data-with-fabricops-io.md)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/orchestrate_demo_reset.py:258`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/orchestrate_demo_reset.py#L258-L465">View on GitHub</a>
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
| Live-critical dependencies | 46 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.5.0 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.activated_pipeline.shared.snapshot_file</code></li>
<li><code>fabricops_kit.config.metadata_schemas.audit_schema_fields</code></li>
<li><code>fabricops_kit.config.metadata_schemas.build_metadata_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_schema_type_name</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_owner</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_physical_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_schema_registry</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_assert_source</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_check_metadata_scope</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_clear_gold_output</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_clear_metadata</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_gold_output_exists</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_metadata_counts</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_metadata_files</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_prepare_gold_empty_output</code></li>
<li><code>fabricops_kit.config.orchestrate_demo_reset._demo_remove_outputs</code></li>
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

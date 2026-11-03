# Explicit development metadata reset

Use a disposable development environment to replace the unreleased #1774 layout with the 13-table Pipeline Promotion model. This is an intentional destructive cutover, not a supported production migration.

!!! warning "Stop all writers before resetting"
    Resetting `METADATA_PIPELINE_RUN` destroys execution audit. Resetting `METADATA_PROCESSING_STATE` destroys checkpoints, accepted baselines and idempotence receipts. Reusing populated business targets without rebuilding the corresponding disposable targets or establishing reviewed new baselines can duplicate or corrupt results. Business tables are never deleted automatically.

## Review the deletion scope

The configured Metadata Lakehouse contains these FabricOps-owned canonical tables:

| Governance schema | Engineering schema |
| --- | --- |
| METADATA_DATA_STEWARD | METADATA_DATA_CATALOGUE |
| METADATA_DATA_AGREEMENT | METADATA_DATA_PROFILED |
| METADATA_DATA_CONTRACT | METADATA_DATA_PROFILED_FREQUENCY |
| METADATA_DATA_CONTRACT_ACTIVATION | METADATA_DATA_LINEAGE |
| | METADATA_DATA_ACCESS |
| | METADATA_PIPELINE_REGISTRY |
| | METADATA_PIPELINE_RUN |
| | METADATA_GUARDRAIL_RESULTS |
| | METADATA_PROCESSING_STATE |

Stop notebook executions and schedules in every workspace using this Metadata Lakehouse. Save any definitions you want to reauthor. Confirm that this is disposable development metadata, review the exact configured table paths, and remove only these tables through the Metadata Lakehouse administration surface. A missing new Contract Activation table is expected before cutover. Do not delete similarly named business targets or entire Lakehouses.

Publication coordination now retains the existing exclusive Serializable writer-claim protocol in `Files/fabricops/publication_coordination`, outside the canonical Registry. After stopping **all** writers and reconciling interrupted physical publications, explicitly remove this development-only ledger during the same reset. It is never automatically expired. Preserve `Files/fabricops/pipeline_snapshots` if archived notebook copies are still required; their presence never grants authority without a Registry version.

## Initialize and verify

1. Run `00_env_config` and `setup_notebook()` against the reviewed Metadata Lakehouse.
2. Run `setup_metadata_tables(config=CONFIG, workspace_id=WORKSPACE_ID, raise_on_failure=True)` and confirm all 13 tables are ready.
3. Repeat setup. Confirm the same schemas and rows remain; no control records or activations are manufactured.
4. Reauthor and freeze required Contracts. Independently review physical table bindings and activate Contracts in their **physical** workspace using `widget_activate_data_contract`.
5. Establish clean business targets or reviewed new processing baselines before persistent execution. Retain the released v0.3.1 load-strategy semantics.
6. Save a development notebook with a literal stable Pipeline ID and `pipeline_mode="Dry Run"`. Run it manually through finalization, then review it with `widget_activate_pipeline(dry_run=preview)`.

Normal `setup_metadata_tables` creates missing empty tables and validates existing schemas. It never performs this reset, migrates #1774 authority, deletes business targets, or converts old approvals into promotions. Obsolete development layouts fail with a link to this procedure.

## Expected result

Contract activations live only in Governance `METADATA_DATA_CONTRACT_ACTIVATION`. Engineering `METADATA_PIPELINE_REGISTRY` contains only immutable per-workspace Pipeline Promotion versions. `METADATA_PIPELINE_RUN` uses version 3 promotion provenance while retaining released operation JSON and content-hash semantics.

Governed admission remains blocked until the [signed-in Fabric checklist](governed-pipeline-promotion-v3-validation.md) is completed. Green local tests do not establish Fabric security or execution-time code identity.

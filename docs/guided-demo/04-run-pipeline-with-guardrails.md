# Step 4: Rerun the Development pipeline with Guardrails

**Rerun `02_pipeline` in Engineering Development so Governance-authored Guardrails and the governed processing definition control the pipeline boundaries.**

Development uses current authoring by default. After a Data Contract exists, the same notebook can instead select one exact frozen Data Contract version for a table and rerun against that frozen definition.

## Before you begin

Confirm that:

- Step 3 has authored the required Schema, Freshness, Changes, and DQ Guardrails
- the source and target tables are registered in the Data Catalogue as required by the workflow
- `02_pipeline` is using the Engineering Development `00_env_config`
- the target load strategy and its required parameters are defined for the run

## What to do

1. Open `02_pipeline` in Engineering Development.
2. Keep `widget_select_data_contract()` on **Current authoring Guardrails** for this first guarded rerun.
3. Use `read_pipeline_prep()` to observe the source, resolve the governed target processing definition, and prepare the source scope as `skip`, `full`, or `incremental`.
4. Run `check_schema()`, `check_freshness()`, and `check_changes()` before the business-data read and stop when a blocking result does not allow continuation.
5. Read the source using the prepared scope. A `skip` run performs no business-data read or target write.
6. Run `check_dq()` on the source DataFrame that is actually being processed.
7. Profile and register the source only when that DataFrame represents the **complete physical source table**.
8. Apply the visible transformation logic.
9. Run target Schema and DQ checks on the transformed target DataFrame.
10. Use `write_pipeline_prep()` to reuse the same resolved processing definition, add governed audit/lifecycle fields, and prepare the physical writer settings.
11. Write the target, read the persisted target back in full, then profile and register that full persisted target.
12. Review the recorded Guardrail Results and profiling/lineage evidence.

## Where Development rules come from

**Development uses current authoring unless an exact Data Contract version is selected for that table.**

| Development validation source | Rule and processing source |
| --- | --- |
| Current authoring | Current Guardrails plus the target load strategy declared for Development |
| Selected Data Contract version | Frozen Guardrails and processing definition inside that version's `contract_payload_json` |

The selection is table-scoped. Selecting a contract for one `table_id` does not apply that contract to another table.

??? info "Why FabricOps separates change detection from processing scope"

    Source observation and `check_changes()` answer **what changed** and whether the configured Changes Guardrail allows the run to continue. They do not independently decide how the target should be maintained.

    `read_pipeline_prep()` combines source-change evidence with the governed target processing definition to resolve a safe source scope:

    ```text
    source observation + governed target strategy
    → skip / full / incremental
    ```

    This matters because the same source change can be safe for one target strategy and unsafe for another. For example, append is rejected when an existing source partition changed or reappeared, and removed partitions require explicit delete semantics rather than being silently ignored.

??? info "Why FabricOps resolves the processing definition once"

    The processing definition used to decide the source scope is reused by `write_pipeline_prep()` for the target write. FabricOps does not resolve the contract a second time between the read and write boundaries.

    That keeps one governed decision authoritative for the whole run and avoids a pipeline reading under one processing definition and writing under another if Governance metadata changes while the notebook is running.

??? info "Why an incremental source slice is not a full-table profile"

    Incremental execution may intentionally read only affected source partitions. That DataFrame is valid for the current processing work, but it does not describe the complete physical source table.

    Registering that slice as the latest complete source profile would make the metadata misleading. FabricOps therefore keeps the previous complete source profile until a later full-source run produces a new complete profile. After the target write, the persisted target is read back in full and that complete persisted state is profiled and registered.

??? info "Why load strategies are governed instead of being arbitrary writer modes"

    `overwrite`, `append`, `scd1`, and `scd2` change the meaning of how a governed target is maintained, so FabricOps treats them as part of the target processing definition rather than a last-minute writer option.

    The runtime also preserves safety boundaries. Incremental Lakehouse overwrite can use partition-scoped replacement, while unsupported or ambiguous combinations deliberately fall back to a full scope or fail rather than guessing. Governed Warehouse SCD1/SCD2 execution remains unsupported until an explicit Warehouse merge implementation exists.

## Guardrail Results still record runtime evidence

A guarded run continues to write the normal evidence produced by the pipeline:

| Evidence area | Purpose |
| --- | --- |
| `METADATA_DATA_CATALOGUE` | Current table and column identity from complete registered profiles. |
| `METADATA_DATA_PROFILED` | Complete registered profiling evidence. |
| `METADATA_DATA_LINEAGE` | Runtime source and target participation recorded by the profiling workflow. |
| `METADATA_GUARDRAIL_RESULTS` | Guardrail outcomes and continuation decisions. |
| `METADATA_GUARDRAIL_ROW_RESULTS` | Failed-row evidence where a DQ rule records row-level failures. |

!!! note "Checks judge policy; preparation applies processing"

    `check_schema()`, `check_freshness()`, `check_changes()`, and `check_dq()` evaluate selected expectations and continuation. `read_pipeline_prep()` and `write_pipeline_prep()` own the governed processing preparation around the visible physical read and write calls.

## Expected result

You should now have a Development pipeline where Guardrails control continuation, the governed target strategy controls safe processing scope, and only complete physical-table states replace registered profiles. After Step 5 creates a Data Contract, you can return to this notebook and use `widget_select_data_contract()` to test an exact frozen version without changing the public check calls.

**Previous:** [Step 3: Enrich the Data Catalogue and define Guardrails](03-enrich-guardrails.md)  
**Next:** [Step 5: Create and activate the Data Contract](05-create-data-contract.md)

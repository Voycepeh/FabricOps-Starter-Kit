# Step 4: Rerun the Development pipeline with Guardrails

**Rerun `02_pipeline` in Engineering Development so Governance-authored Guardrails and the governed processing definition control the pipeline boundaries.**

This step uses the newer governed runtime path. The components are implemented but remain **Preview** in the Guided Demo until the complete flow is revalidated end to end in Fabric.

!!! info "Key concepts for this step"

    **Guardrails**, **Enforcement**, **Guardrail Result**, **Full Dataset**, **Incremental Subset**, and **Data Quality** are the key concepts for this step.

    The source strategy is configured separately as **Full Dataset**, **Incremental Watermark**, or **Incremental Partition**. The runtime read mode then resolves to `skip`, Full Dataset, or Incremental Subset.

    Hover over a glossary term for its canonical definition, or open the [Glossary](../glossary.md) for the full entry.

## High-level flow

```text
Select rule source
→ Prepare source scope
→ Pre-read Guardrails
→ Full Dataset / Incremental Subset read
→ DQ + complete-source profiling rule
→ Transform
→ Target Guardrails
→ Governed write preparation
→ Write + full read-back + target profile
```

## Before you begin

Confirm that Step 3 has authored the required Guardrails, the source and target tables are registered where required, `02_pipeline` uses the Engineering Development `00_env_config`, and the target load strategy plus required parameters are defined.

??? info "Preview — Select current authoring or a frozen Data Contract"

    Open `02_pipeline` in Engineering Development.

    Keep `widget_select_data_contract()` on **Current authoring Guardrails** for the first guarded rerun. After a Data Contract exists, the same selector can choose one exact frozen version for the same table.

    | Development validation source | Rule and processing source |
    | --- | --- |
    | Current authoring | Current Guardrails plus the target load strategy declared for Development |
    | Selected Data Contract version | Frozen Guardrails and processing definition inside that version's `contract_payload_json` |

    Selection is table-scoped. Selecting a contract for one `table_id` does not apply it to another table.

??? info "Preview — Prepare the source scope"

    Use `read_pipeline_prep()` to observe the source, resolve the governed target processing definition, and prepare the source runtime mode as `skip`, `full_dataset`, or `incremental_subset`.

    ```text
    configured source strategy + source observation + governed target strategy
    → skip / full_dataset / incremental_subset
    ```

    A `skip` run performs no business-data read, transformation, or target write.

??? info "Preview — Evaluate pre-read source Guardrails"

    Run `check_schema()`, `check_freshness()`, and `check_changes()` before the business-data read. Stop when a blocking result does not allow continuation.

    Source Observation and `check_changes()` answer **what changed**. `read_pipeline_prep()` combines those recorded observations with the configured source strategy and governed target processing definition to decide the safe processing scope.

??? info "Preview — Read the resolved source scope and run DQ"

    Read the source using the prepared scope. Run `check_dq()` on the DataFrame that is actually being processed.

    Profile and register the source only when that DataFrame represents the **complete physical source table**. An Incremental Subset is valid processing scope but must not replace the latest complete source profile.

???+ success "Live — Apply the visible transformation"

    Apply the normal user-defined transformation in `02_pipeline`. FabricOps continues to leave business transformation logic visible and project-owned.

??? info "Preview — Validate the target and prepare the governed write"

    Run target Schema and DQ checks on the transformed target DataFrame.

    Use `write_pipeline_prep()` to reuse the same resolved processing definition, add governed audit/lifecycle fields, and prepare the physical writer settings. The contract is not resolved again between read and write preparation.

??? info "Preview — Write, read back, and register the complete target"

    Write the target only when the Guardrail continuation decisions allow it. Then read the persisted target back in full and profile/register that complete persisted state.

    The governed load strategy controls how the target is maintained. `overwrite`, `append`, `scd1`, and `scd2` are processing definitions rather than arbitrary last-minute writer modes. Unsupported or ambiguous combinations fail or fall back to a safe full scope rather than guessing.

??? info "Preview — Review runtime records"

    A guarded run writes the normal records produced by the pipeline:

    | Metadata area | Purpose |
    | --- | --- |
    | `METADATA_DATA_CATALOGUE` | Current table and column identity from complete registered profiles. |
    | `METADATA_DATA_PROFILED` | Complete registered profiling records. |
    | `METADATA_DATA_LINEAGE` | Runtime source and target participation recorded by the profiling workflow. |
    | `METADATA_GUARDRAIL_RESULTS` | Guardrail outcomes and continuation decisions. |
    | `METADATA_GUARDRAIL_ROW_RESULTS` | Failed-row records where a DQ rule records row-level failures. |

## Expected result

You should understand the complete guarded Development lifecycle and where the Preview runtime components fit around the same visible ETL path used in Step 2. After Step 5 creates a Data Contract, this notebook can test an exact frozen version without changing the public check calls.

**Previous:** [Step 3: Enrich the Data Catalogue and define Guardrails](03-enrich-guardrails.md)  
**Next:** [Step 5: Create and activate the Data Contract](05-create-data-contract.md)

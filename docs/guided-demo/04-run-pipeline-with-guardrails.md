# Step 4: Validate with Guardrails / Data Contract

**Rerun `02_pipeline` in Engineering Development so Governance-authored Guardrails or a selected frozen Data Contract control the governed pipeline boundaries.**

This step uses the newer governed runtime path. The components are implemented but remain **Preview** in the Guided Demo until the complete flow is revalidated end to end in Fabric.

!!! info "Key concepts for this step"

    **Guardrails**, **Enforcement**, **Guardrail Result**, **Full Dataset**, **Incremental Subset**, and **Data Quality** are the key concepts for this step.

    The source strategy is configured separately as **Full Dataset**, **Incremental Watermark**, or **Incremental Partition**. The runtime read mode then resolves to `skip`, Full Dataset, or Incremental Subset.

    Hover over a glossary term for its canonical definition, or open the [Glossary](../glossary.md) for the full entry.

## High-level flow

```text
Select current Guardrails or frozen Data Contract
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

    Keep `widget_select_data_contract()` on **Current authoring Guardrails** for the first guarded rerun. After Step 5 freezes a Data Contract version, return to the same `02_pipeline` and select that exact frozen version to test it before activation.

    | Development validation source | Rule and processing source |
    | --- | --- |
    | Current authoring | Current Guardrails plus the target load strategy declared for Development |
    | Selected Data Contract version | Frozen Guardrails and processing definition inside that version's `contract_payload_json` |

    Selection is table-scoped. Selecting a contract for one `table_id` does not apply it to another table.

??? info "Preview — Prepare the source scope"

    Use `read_pipeline_prep()` with the source `table_id` to resolve its registered physical identity, observe source state, and prepare the source runtime mode as `skip`, `full_dataset`, or `incremental_subset`.

    The engineer chooses the **source strategy**. FabricOps then combines that choice with recorded source state to determine the **runtime read mode** for this run.

    ```mermaid
    flowchart TB
        FULL["Full Dataset"] --> FULLMODE["full_dataset"]
        WATERMARK["Incremental Watermark"] --> PREP["FabricOps preparation<br/>source state + successful checkpoint"]
        PARTITION["Incremental Partition"] --> PREP
        PREP --> FIRST{"Successful checkpoint exists?"}
        FIRST -->|No| FULLMODE
        FIRST -->|Yes| CHANGED{"Changes detected?"}
        CHANGED -->|Yes| SUBSET["incremental_subset"]
        CHANGED -->|No| SKIP["skip"]
    ```

    A `skip` run performs no business-data read, transformation, or target write. On the first incremental run, no successful checkpoint exists yet, so FabricOps uses a full-dataset runtime scope and records progress only after successful publication.

??? info "Preview — Evaluate pre-read source Guardrails"

    Run `check_schema()`, `check_freshness()`, and `check_changes()` before the business-data read. Stop when a blocking result does not allow continuation.

    Source Observation and `check_changes()` answer **what changed**. `read_pipeline_prep()` combines that source-owned state with the configured source strategy and the source table's own processing definition to decide a safe physical read scope.

??? info "Preview — Read the resolved source scope and run DQ"

    Read the source using the prepared scope. Run `check_dq()` on the DataFrame that is actually being processed.

    Profile and register the source only when that DataFrame represents the **complete physical source table**. An Incremental Subset is valid processing scope but must not replace the latest complete source profile.

???+ success "Live — Apply the visible transformation"

    Apply the normal user-defined transformation in `02_pipeline`. FabricOps continues to leave business transformation logic visible and project-owned.

??? info "Preview — Validate the target and prepare the governed write"

    Run target Schema and DQ checks on the transformed target DataFrame.

    Use `write_pipeline_prep()` with the target `table_id` to resolve that target's selected or active Data Contract, add governed audit/lifecycle fields, and prepare the physical writer settings and source completion context.

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

You should understand the complete guarded Development lifecycle and where the Preview runtime components fit around the same visible ETL path used in Step 2. The same notebook first validates current Governance authoring, then returns after Step 5 freezes a Data Contract so the exact frozen version can be tested before governance sign-off and activation.

**Previous:** [Step 3: Enrich the Data Catalogue and define Guardrails](03-enrich-guardrails.md)  
**Next:** [Step 5: Freeze, test, and activate the Data Contract](05-create-data-contract.md)

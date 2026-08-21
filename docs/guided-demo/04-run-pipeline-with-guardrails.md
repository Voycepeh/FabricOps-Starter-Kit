# Step 4: Rerun the Development pipeline with Guardrails

**Rerun `02_pipeline` in Engineering Development so the current Governance-authored Guardrails are evaluated and recorded before critical pipeline steps.**

Development uses current authoring Guardrails by default. After a Data Contract exists, the same notebook can instead select one exact frozen Data Contract version for a table and rerun the same checks against those frozen expectations.

## Before you begin

Confirm that:

- Step 3 has authored the required Schema, Freshness, Changes, and DQ Guardrails
- the table is already registered in the Data Catalogue
- `02_pipeline` is using the Engineering Development `00_env_config`

## What to do

1. Open `02_pipeline` in Engineering Development.
2. Keep `widget_select_data_contract()` on **Current authoring Guardrails** for this first guarded rerun.
3. Run `observe_table()` for the governed source.
4. Run `check_schema()`, `check_freshness()`, and `check_changes()` before the full source read.
5. Read the source only when the pre-read checks allow continuation.
6. Run `check_dq()` on the source DataFrame.
7. Profile and register the source, apply the visible transformation, and continue the normal Development target flow.
8. Run the target Schema and DQ checks and review the recorded Guardrail Results.

## Where Development rules come from

**Development uses the current authoring Guardrails unless an exact Data Contract version is selected for that table.**

| Development validation source | Rule source |
| --- | --- |
| Current authoring Guardrails | Current rules in `METADATA_GUARDRAIL` |
| Selected Data Contract version | Frozen Guardrails inside that version's `contract_payload_json` |

The selection is table-scoped. Selecting a contract for one `table_id` does not apply that contract to another table.

## Guardrail Results still record runtime evidence

A guarded run continues to write the normal evidence produced by the pipeline:

| Evidence area | Purpose |
| --- | --- |
| `METADATA_DATA_CATALOGUE` | Current table and column identity. |
| `METADATA_DATA_PROFILED` | Current profiling evidence. |
| `METADATA_DATA_LINEAGE` | Runtime source and target participation. |
| `METADATA_GUARDRAIL_RESULTS` | Guardrail outcomes and continuation decisions. |
| `METADATA_GUARDRAIL_ROW_RESULTS` | Failed-row evidence where a DQ rule records row-level failures. |

!!! note "Checks do not choose the processing strategy"

    `check_schema()`, `check_freshness()`, `check_changes()`, and `check_dq()` judge whether the observed data satisfies the selected expectations. They do not decide incremental read predicates, merge behaviour, or remediation.

## Expected result

You should now have a Development pipeline that evaluates the current authored Guardrails and records the resulting evidence. After Step 5 creates a Data Contract, you can return to this notebook and use `widget_select_data_contract()` to test an exact frozen version without changing the four check calls.

**Previous:** [Step 3: Enrich the Data Catalogue and define Guardrails](03-enrich-guardrails.md)  
**Next:** [Step 5: Create and activate the Data Contract](05-create-data-contract.md)

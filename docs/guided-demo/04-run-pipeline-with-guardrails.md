# Step 4: Select and Validate the Data Contract

**Use `02_pipeline` in Engineering Development to select the frozen Data Contract version for each governed `table_id` and validate it against the real ETL.**

## High-level flow

```text
governed table_id → select frozen version → run 02_pipeline
→ evaluate Guardrails → inspect results → confirm runtime behavior
```

## Before you begin

Confirm Step 3 froze the intended version and that `02_pipeline` is using the Engineering Development configuration from `00_env_config`.

## What to do

1. Open `02_pipeline` in Engineering Development.
2. For each relevant target `table_id`, run `widget_select_data_contract(...)`.
3. Choose the exact frozen Data Contract version authored in Step 3. Selection is table-scoped: choosing a version for one `table_id` does not affect another table.
4. Run the governed pipeline through its visible Extract, Transform, and Load path.
5. Evaluate the saved immutable requirements with the modular runtime functions: `check_schema()`, `check_freshness()`, `check_changes()`, `check_dq()`, and `check_sensitive_data()` where applicable.
6. Confirm Warn/Block continuation behavior and the saved processing definition behave as intended.
7. Inspect the summary records written to `METADATA_GUARDRAIL_RESULTS`. Inspect caller-owned DQ failed-row DataFrames where relevant; FabricOps does not automatically persist those rows.

!!! important "Selection is not activation"

    `widget_select_data_contract(...)` sets the Development runtime context for the same `table_id`. It does not activate the version, link it to a Data Agreement, or change what Production resolves.

??? info "Preview — validate mutable current authoring"

    The selector may still expose mutable current authoring for advanced or Preview investigation. That path is not the canonical lifecycle. Normal validation starts from the frozen version so Engineering tests the exact immutable definition Governance can later link and activate.

??? info "Sensitive Data support mappings"

    Token mappings returned by `check_sensitive_data()` remain caller-owned and outside FabricOps metadata. Projects may write them to an approved restricted store, including through `write_pii_token_map()` where appropriate; FabricOps does not persist them automatically.

## Expected result

Engineering has tested the selected frozen version for the same governed `table_id`, reviewed runtime behavior, and retained Guardrail summaries in `METADATA_GUARDRAIL_RESULTS`. The version is still not active for Production.

**Previous:** [Step 3: Author and freeze the Data Contract](03-enrich-guardrails.md)
**Next:** [Step 5: Link the tested Data Contract to the Data Agreement and activate](05-create-data-contract.md)

# Step 4. Test the frozen Data Contracts

Inspect and evaluate the configured pipeline before permitting publication. Use the current `02A_full_refresh_demo.ipynb` after authoring the frozen versions in Step 3.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Select and inspect the pipeline contracts

Testing evaluates actual source data and records explicit governance status.

</div>
</div>

1. Run Environment, set `PIPELINE_CONTRACT_TESTING=True` externally, and rerun the `setup_pipeline()` selector cell with the exact source and target identities to create a fresh selector for this Testing run. A previously built selector is locked, and its `build_plan()` returns the same plan. Historical Lineage is not required.
2. Leave the pipeline-wide switch in red **Testing**.
3. Select an eligible frozen version independently for every source and target. Do not leave choices implicit. Before contracts exist, choose No Contract for every participant. Contract-free Testing cannot be activated. Partial selections are rejected; Live requires approved contracts.
4. Expand Schema to inspect every expected column and exact type. Expand Grain, Data Quality, Freshness, Source Drift and Sensitive Data to inspect individual parameters, thresholds, actions and states. Non-applicable saved rules remain visible with their boundary explanation.
Selection does not edit or activate a contract.

5. Run `EXECUTION_PLAN = CONTRACTS["build_plan"]()` after selecting versions. All Reads and Writes must use this same plan.

**Data Contract → Configured Guardrails → Testing/Live Execution → Results**

The selected payload determines applicable checks. Empty Guardrail lists and intentionally disabled optional checks impose no extra requirement. Warn reports a failure and permits continuation. Block prevents Live publication; a configured check that cannot execute also fails closed. Partial contract selection is prohibited. Missing selections remain errors.

### Run Read → Transform → Write → Inspect

Testing reads real data and runs the transformation normally. The prepared Write input includes Sensitive Data treatment. Supported Overwrite, Append, SCD1 and SCD2 dry-run checks use the same processing definition, writer ownership and incremental safety checks as Live; SCD checks validate the input business keys.

```python
# The template defines the steps in separate cells, then runs them together.
with EXECUTION_PLAN:
    sources = {}
    read_1(sources)
    read_2(sources)
    read_3(sources)
    transformed_df, customer_summary_df = transform(sources)
    writes = {}
    write_1(sources, writes, transformed_df, customer_summary_df)
    write_2(sources, writes, transformed_df, customer_summary_df)
print(EXECUTION_PLAN.run_result["status"])
result = writes["curated_orders"]
print(result["execution_mode"], result["publication_status"])
print(result["validation_passed"], result["source_guardrail_results"])
CONTRACTS["refresh"]()  # Expand exact-version execution results in the inspector.
display(result["dataframe"].limit(10))
print(result["dry_run"])
print(result["checks_not_exercised"])
```

A failed Guardrail remains a diagnostic result in Testing. Inspect `schema_result`, `grain_result`, `dq_result`, `source_drift_results`, `sensitive_result`. DQ diagnostics retain exact counts and configured tolerances, with bounded samples by default and optional lazy full violations.

Evaluation-only Testing does not write target data, `METADATA_DATA_LINEAGE`, `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY`, `METADATA_SOURCE_OBSERVATION`, persistent token mappings, checkpoints or durable staging. It persists `METADATA_PIPELINE_RUN` and linked `METADATA_GUARDRAIL_RESULTS`, while retaining the in-memory inspection journal. Run all declared Reads, transformations and Writes inside `with plan:`; its exit records completion automatically, including read-only pipelines. Missing operations and blocking failures prevent successful completion. Supply a stable `pipeline_id` and deployed executable SHA-256 for qualifying Testing evidence.

Explicit `testing_writes=True` permits real Testing publication with mappings, checkpoints and ordinary metadata side effects. Review the destination and confirm the interactive authorization; Live-owned destinations are rejected. Evaluation-only Testing remains available without another execution requirement.

### Interpret the outcome

| Result | Meaning |
|---|---|
| `execution_mode="testing"`, `published=False` | No publication occurred. |
| `validation_passed=True` | The checks performed passed; publication was simulated. |
| `dry_run.fully_evaluated` | Input, processing, ownership and safety checks actually evaluated. |
| `checks_not_exercised` / `dry_run.not_verified` | Fabric permissions, real target transactions, concurrency and cross-store finalization need Live runtime validation. |

Without a successful historical Live publication, Source Drift may report its first observation rather than a historical comparison. Testing can inspect committed history and simulate recovery, but cannot advance that history. Each target returns its own result; Testing does not exit the notebook after the first target.

### Live publication is a separate decision

Governance approves one exact whole pipeline after successful finalization, using [`widget_activate_pipeline()`](../api/reference/widget_activate_pipeline.md). The service consumes the committed `METADATA_PIPELINE_RUN` snapshot and linked Guardrail diagnostics. Read-only and multiple-output candidates qualify only when every declared operation completed; ungoverned Testing and isolated passing rules cannot authorize activation.

Keep the tested notebook executable unchanged. Use runtime configuration for the Testing/Live mode and environment bindings. Deployment is separate; headless Live automatically resolves the approved environment revision.

**Expected result:** every selected frozen definition is inspectable, diagnostics report the actual checks performed, and Testing persists run records and Guardrail diagnostics while preserving publication boundaries.

**Next:** [Activate the pipeline and promote](05-activate-data-contract-and-promote.md).

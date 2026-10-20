# Step 4. Test the frozen Data Contracts

Inspect and evaluate the configured pipeline before permitting publication. Use the current `02A_full_refresh_demo.ipynb` after authoring the frozen versions in Step 3.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Select and inspect the pipeline contracts

Testing evaluates actual source data and returns diagnostics without durable changes.

</div>
</div>

1. Run Environment and configure the exact source and target identities. Historical Lineage is not required.
2. Leave the pipeline-wide switch in red **Testing**.
3. Select an eligible frozen version independently for every source and target. Do not leave choices implicit. For first-time bootstrap before contracts exist, explicitly select **No Contract** for every participant; it cannot bypass an active contract.
4. Expand Schema to inspect every expected column and exact type. Expand Grain, Data Quality, Freshness, Source Drift and Sensitive Data to inspect individual parameters, thresholds, actions and states. Non-applicable saved rules remain visible with their boundary explanation.
Selection does not edit or activate a contract.

5. Run `EXECUTION_PLAN = CONTRACTS["build_plan"]()` after selecting versions. All Reads and Writes must use this same plan.

**Data Contract → Configured Guardrails → Testing/Live Execution → Results**

The selected payload determines applicable checks. Empty Guardrail lists and intentionally disabled optional checks impose no extra requirement. Warn reports a failure and permits continuation. Block prevents Live publication; a configured check that cannot execute also fails closed. Explicit No Contract cannot bypass an active contract. Missing selections remain errors.

### Run Read → Transform → Write → Inspect

Testing reads real data and runs the transformation normally. The prepared Write input includes Sensitive Data treatment. Supported Overwrite, Append, SCD1 and SCD2 dry-run checks use the same processing definition, writer ownership and incremental safety checks as Live; SCD checks validate the input business keys.

```python
result = writes["curated_orders"]
print(result["execution_mode"], result["publication_status"])
print(result["validation_passed"], result["source_guardrail_results"])
CONTRACTS["refresh"]()  # Expand exact-version execution results in the inspector.
display(result["dataframe"].limit(10))
print(result["dry_run"])
print(result["checks_not_exercised"])
```

A failed Guardrail remains a diagnostic result in Testing. Inspect `schema_result`, `grain_result`, `dq_result`, `source_drift_results`, `sensitive_result`. DQ diagnostics retain exact counts and configured tolerances, with bounded samples by default and optional lazy full violations.

Testing never writes target data, `METADATA_DATA_LINEAGE`, `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY`, `METADATA_GUARDRAIL_RESULTS`, `METADATA_SOURCE_OBSERVATION`, persistent token mappings, checkpoints or durable staging. It never activates contracts or registers successful contract-validation evidence for activation. Evaluation results stay in the plan's in-memory journal.

### Interpret the outcome

| Result | Meaning |
|---|---|
| `execution_mode="testing"`, `published=False` | No publication occurred. |
| `validation_passed=True` | The checks performed passed; publication was simulated. |
| `dry_run.fully_evaluated` | Input, processing, ownership and safety checks actually evaluated. |
| `checks_not_exercised` / `dry_run.not_verified` | Fabric permissions, real target transactions, concurrency and cross-store finalization need Live runtime validation. |

Without a successful historical Live publication, Source Drift may report its first observation rather than a historical comparison. Testing can inspect committed history and simulate recovery, but cannot advance that history. Each target returns its own result; Testing does not exit the notebook after the first target.

### Live publication is a separate decision

After Governance has activated the appropriate frozen versions, switch the whole pipeline to green **Live**, build a new plan, and rerun Read → Transform → Write. Live rejects inactive candidates and preserves Warn/Block, required Guardrail execution, ownership, retry and recovery checks. A successful Live write commits authoritative Lineage at the existing boundary. Publication and metadata updates across Fabric stores are separate operations.

Pass the complete in-memory Testing Write reports to `widget_activate_data_contract(testing_results=list(writes.values()))` in the separate Governance review. It matches the exact contract ID, version and immutable payload, requires explicit review approval and Data Agreement linkage, then asks for confirmation. Testing itself never registers evidence, activates a contract or authorizes Live.

**Expected result:** every selected frozen definition is inspectable, diagnostics report the actual checks performed, and Testing produces zero persistent changes.

**Next:** [Activate Data Contracts and promote](05-activate-data-contract-and-promote.md).

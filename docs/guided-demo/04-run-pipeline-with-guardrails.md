# Step 4: Rerun the Development pipeline with Guardrails

**Rerun `02_pipeline` in Engineering Development so the Guardrails authored in Step 3 are loaded, evaluated, and recorded before critical publication steps.**

The guarded pipeline keeps the same read, profile, transform, profile, and write pattern from Step 2, then adds Guardrail retrieval, evaluation, severity handling, and continuation decisions.

## Guardrail workflow

```text
read
→ profile source
→ load source Guardrails
→ evaluate source Guardrails
→ transform
→ profile target
→ load target Guardrails
→ evaluate target Guardrails
→ decide whether the pipeline can continue
→ write target when allowed
→ register Guardrail Results and Data Lineage
```

## What to do

1. Read the source DataFrame.
2. Profile and register the source.
3. Load the active source Guardrails authored by Governance.
4. Evaluate source Guardrails.
5. Stop or continue based on severity and continuation results.
6. Apply transformation logic.
7. Profile and register the target.
8. Load active target Guardrails.
9. Evaluate target Guardrails before publication.
10. Write the target only when blocking checks permit continuation.
11. Persist Guardrail Results and runtime evidence.

## Normal pipeline evidence still applies

A guarded run still writes the normal pipeline evidence:

| Evidence area | Purpose |
| --- | --- |
| `METADATA_DATA_CATALOGUE` | Physical table and column identity snapshots. |
| `METADATA_DATA_PROFILED` | Statistical and schema evidence per column. |
| `METADATA_DATA_LINEAGE` | Runtime source and target participation evidence. |
| `METADATA_GUARDRAIL_RESULTS` | Guardrail evaluation outcomes and continuation decisions. |

!!! note "Guardrails add enforcement evidence"

    Guardrails do not replace Data Catalogue, Data Profiled, Data Profiled Frequency, or Data Lineage records. They add executable expectations and runtime outcomes around the normal pipeline workflow.

## Where rules come from

`02_pipeline` retrieves active Guardrail definitions from `METADATA_GUARDRAIL`. Runtime does not invent its own rules.

These records describe the Guardrail type, table or column scope, parameters, severity, activation state, and audit context.

## Profile mode and enforcement mode

| Mode | User outcome |
| --- | --- |
| Profile mode | Records observations without blocking publication. |
| Enforcement mode | Evaluates continuation and can block publication when required. |

Typical severity behaviour:

- **Warning** records an issue but normally allows continuation.
- **Error** blocks the next critical step when the Guardrail fails.

## Source and target enforcement points

| Run point | What happens | Why it matters |
| --- | --- | --- |
| After source read and profiling | Evaluate active source expectations. | Catch upstream issues before transformation. |
| Transformation | Apply deterministic business logic in visible notebook cells. | Keep the output explainable and repeatable. |
| Before target write | Evaluate active target expectations. | Prevent unsafe or non-compliant publication. |
| After checks pass | Write outputs and persist metadata evidence. | Preserve a reviewable execution trail. |

??? info "What Guardrail Results contain"

    `METADATA_GUARDRAIL_RESULTS` stores the runtime outcome of evaluated Guardrails, including rule identity, execution scope, Guardrail classification, status, continuation decision, severity, reason, expected and actual values, result payloads, and standard audit information.

    Statuses may represent pass, warning, fail, or skipped outcomes depending on the evaluated rule and severity. The key operational result is whether the notebook can continue past the guarded point.

## Expected result

You should now have a Development pipeline that evaluates approved Guardrails and records Guardrail Results while preserving the normal Data Catalogue, Data Profiled, Data Profiled Frequency where applicable, and Data Lineage evidence.

**Previous:** [Step 3: Enrich the Data Catalogue and define Guardrails](03-enrich-guardrails.md)  
**Next:** [Step 5: Create the Data Contract and prepare for promotion](05-create-data-contract.md)

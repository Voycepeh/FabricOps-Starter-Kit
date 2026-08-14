# ETL Guardrails

Apply Guardrails at the governed source and target boundaries while keeping Development open to intentional schema evolution and Production protected from unapproved changes.

## The target publication rule

**Engineering Development records the proposed target before validation; Engineering Production validates before publication.**

| Environment | Target lifecycle | Purpose |
| --- | --- | --- |
| Engineering Development (`dev`) | write → read target → profile/register → Schema and DQ Guardrails | Materialise intentional changes so Governance can review the newly observed target schema. |
| Engineering Production (`prod`) | Schema and DQ Guardrails on incoming DataFrame → write → read target → profile/register | Reject unapproved changes before they can modify the Production table. |

!!! important

    Keep the `ENV == "dev"` and `ENV == "prod"` branches visible in `02_pipeline`. Do not hide this ordering in another notebook orchestrator.

## Engineering Development

**Write and register the proposed target first, then evaluate its Guardrails.** This allows datatype changes and removal of previously required columns to exist in Development long enough to produce updated Data Catalogue and Data Profiled evidence for Governance.

```text
incoming target DataFrame
→ write Development target
→ read persisted target
→ profile and register target
→ check_schema() against persisted target
→ run target DQ Guardrails against persisted target
→ Governance reviews the new evidence
```

A blocking approved rule still reports the mismatch according to its configured severity. The important Development distinction is that the write and profiling evidence already exist before that judgement occurs.

## Engineering Production

**Validate the incoming target DataFrame before modifying Production.** `check_schema(..., dataframe=DF)` checks the supplied schema while resolving approved intent from the configured target, schema, and table identity.

```text
incoming target DataFrame
→ check_schema(..., dataframe=DF)
→ run target DQ Guardrails against DF
→ write Production target only when allowed
→ read persisted target
→ profile and register target
```

An unapproved blocking schema change stops at the guardrail boundary, before the Production write. After Governance approves the Development evidence, the same incoming schema can pass the Production Guardrail and proceed to publication.

## Source validation remains separate

**Target ordering does not replace the governed source boundary.** Initial source onboarding creates evidence; subsequent governed runs collect compact observations and apply source Guardrails before expensive work.

```text
INITIAL ONBOARDING
read source
→ profile and register
→ Governance authors Schema, Freshness, Changes, and DQ Guardrails

SUBSEQUENT GOVERNED RUNS
observe_table()
→ check_schema() → check_freshness() → check_changes()
→ full source read when allowed
→ source DQ Guardrails
→ profile source
→ transform
→ environment-aware target lifecycle
```

[`observe_table()`](../api/reference/observe_table.md) collects compact source facts. It does not author policy, decide severity, construct incremental read predicates, or perform row-level change tracking.

## Guardrail responsibilities

| Stage | Action | Responsibility |
| --- | --- | --- |
| Source onboarding | `profile_and_register_table()` | Produce catalogue and profiling evidence for Governance. |
| Source pre-read | `observe_table()` | Persist compact source observations. |
| Source pre-read | `check_schema()`, `check_freshness()`, `check_changes()` | Judge approved source intent before the full read. |
| Source rows | Existing DQ execution | Evaluate authored row-level rules against the source DataFrame. |
| Transform | Pipeline code | Produce the incoming target DataFrame. |
| Development target | Write and profile, then Schema and DQ Guardrails | Register proposed changes before Governance review. |
| Production target | Schema and DQ Guardrails, then write and profile | Protect the approved table before modification. |

Do not reproduce Guardrail continuation logic in the notebook. The approved Guardrail and existing check execution remain responsible for whether the workflow may continue.

## Metadata ownership

| Ownership | Metadata table | Responsibility |
| --- | --- | --- |
| Observed profiles | `METADATA_DATA_CATALOGUE` | Observed target and source table/column profiles. |
| Approved intent | `METADATA_GUARDRAIL_RULES` | Approved Schema, Freshness, Changes, and DQ Guardrail intent. |
| Runtime outcomes | `METADATA_GUARDRAIL_RESULTS` | Guardrail results and continuation decisions. |

## Expected result

Development can materialise and register intentional schema changes for Governance review. Production checks the incoming DataFrame against approved intent before any write, so an unapproved blocking change cannot modify the Production table.

## Next

Open the [notebook template guide](../notebook-templates.md), then follow the Guided Demo to [author Guardrails in Governance](../guided-demo/03-enrich-guardrails.md) and [run the pipeline with Guardrails](../guided-demo/04-run-pipeline-with-guardrails.md).

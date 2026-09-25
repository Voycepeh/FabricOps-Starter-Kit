# Step 3. Author and freeze the Data Contract

**Return to `01_governance` and turn the real Engineering evidence from Step 2 into a versioned Data Contract.**

This is where FabricOps closes the first Governance to Engineering loop. You are no longer defining rules against an imagined table. `02_pipeline` has already created and profiled the real target, so Governance can author against its canonical `table_id`.

## Select the governed table

Use the table selection section in `01_governance` to choose the target produced in Step 2.

Review the available Catalogue and profiling evidence so you understand the physical table before defining its contract.

## Open the Data Contract authoring widget

`widget_data_contract()` brings the table-specific Governance definition together in one place.

Author the contract in three parts:

1. **Enrichment**: descriptions, business meaning, classifications, sensitivity context, and other descriptive metadata.
2. **Guardrails**: enforceable Schema, Freshness, Source Drift, Data Quality, and Sensitive Data expectations.
3. **Processing**: the target load strategy and any parameters required by that strategy, plus the logical notebook ownership.

The important concept is that these are not separate disconnected metadata records from the user's point of view. Together they form the governed definition for that table and version.

For **Processing**, FabricOps saves the load strategy on the exact Data Contract version. A new version first uses the Engineering Catalogue value when one has been observed; that value is shown read-only. If Engineering has not resolved processing, FabricOps inherits the previous Data Contract version when available. If neither exists, the draft starts at `overwrite`. Inherited and defaulted values remain editable before you save and freeze the version.

## Make the Step 2 behaviour governed

Use the contract to formalise decisions that were only Development proposals in Step 2.

For example:

- keep `curated_orders` as `overwrite`, or
- configure a suitable target as `append`, SCD1, or SCD2 with its required keys and parameters,
- add a Schema Guardrail based on the observed table,
- add one or two understandable DQ rules,
- add Freshness and Source Drift expectations where appropriate,
- add Sensitive Data handling when the demo columns support it.

Do not add rules only to make the screen look busy. The goal is to make it obvious that the Data Contract changes what the same `02_pipeline` will enforce in Step 4.

### Review AI-assisted Sensitive Data assessments

**The Sensitive Data assistant proposes reviewable authoring state; it does not make a governance decision.**

When AI Enrichment is enabled in `00_env_config`, the widget prepares Description, Classification, and Sensitive Data suggestions automatically for each editable context as you open it. The assistant uses the canonical Catalogue identity, Description and information Classification from `METADATA_ENRICHMENT`, and available `METADATA_DATA_PROFILED` profile evidence. It does not sample source rows for this feature.

For each column, review one of these assessments:

| PII assessment | Meaning |
| --- | --- |
| **Direct PII** | The supplied context supports that the column can directly identify, contact, or uniquely associate with an individual. |
| **Indirect PII** | The supplied context supports that the column can identify or materially narrow down an individual when combined with other information. |
| **Not PII** | The supplied context does not provide a defensible basis for treating the column as personally identifying. |

AI suggestions remain visually separate from the editable contract. Choose **Accept** to copy only that Description, Classification, or Sensitive Data proposal into its corresponding editor; choose **Re-run** for new advice, or ignore the suggestion. For Direct or Indirect PII, the assistant can recommend an existing deterministic treatment—**Tokenize**, **Mask**, **Bucket**, or **Remove**—and a **Warn** or **Block** action. You can then edit the assessment, explanation, treatment parameters, and action, or disable the proposed rule before saving it.

When you save a Direct or Indirect PII rule, FabricOps requires a reason and retains the reviewed PII assessment and reason inside that Sensitive Data Guardrail's parameters. This keeps the rationale reviewable without adding another metadata table; runtime enforcement still validates and executes only the supported deterministic treatment. A **Not PII** assessment remains authoring state and does not create an enforceable treatment.

Manual Description changes mark the Classification and Sensitive Data suggestions as needing refresh. Manual Classification changes mark the Sensitive Data suggestion as needing refresh. The widget does not call AI while you type; use **Re-run** when you want refreshed advice based on the current unsaved Description and Classification.

!!! important "Keep the three decisions distinct"
    **Confidential** is an information Classification, **Direct PII** describes identifying characteristics, and **Mask** is an enforceable Sensitive Data treatment. Classification can inform an assessment, but it does not create a Sensitive Data Guardrail automatically.

The flow is **automatic suggestion → review → accept, edit, ignore, or re-run → normal Save → Freeze**. Suggestions and accepted-but-unsaved edits remain transient until you explicitly use the normal save action. AI never saves, freezes, activates, or enforces a contract. Freezing remains the Governance sign-off boundary, and [`check_sensitive_data()`](../api/reference/check_sensitive_data.md) applies only the reviewed Guardrail deterministically at runtime.

## Review the complete definition

Before freezing, review the selected `table_id`, Enrichment, Guardrails, Processing, and ownership together.

A user should be able to answer:

> What does this table mean, what must be true about it, and how is it allowed to be published?

## Freeze the version

Freeze the reviewed draft to create an immutable Data Contract version.

Freezing does not activate the version for Production. It creates the exact version Engineering Development can select and test next.

## Expected result

You now have a frozen immutable Data Contract built from the real table evidence produced in Step 2.

**Next:** [Step 4. Select and validate the Data Contract](04-run-pipeline-with-guardrails.md)

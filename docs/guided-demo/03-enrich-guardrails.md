# Step 3. Author and freeze the Data Contract

**Return to `01_governance` and turn the real Engineering evidence from Step 2 into a reviewed, immutable Data Contract.**

`02_pipeline` has already created and profiled the real target. Governance now authors against that canonical `table_id`, reviews the evidence, defines what the table means and what must be true, then freezes the exact version Engineering will validate in Step 4.

!!! warning "Using the AI authoring features requires Fabric AI Functions"
    FabricOps can author Data Contracts without AI. The deterministic editors remain available when AI is disabled.

    To use **AI suggestions**, confirm all of the following before continuing:

    1. In the Fabric Admin portal, **Users can use Copilot and other features powered by Azure OpenAI** is enabled for the relevant users or capacity.
    2. The workspace runs on a Fabric capacity and region supported by [Fabric AI Functions](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/overview). AI Functions require Fabric Runtime 1.3 or later and an eligible paid capacity.
    3. If your capacity region requires cross-geo processing, the corresponding Fabric tenant setting is enabled.
    4. `GOVERNANCE_CONFIG.ai_enrichment.enabled` is set to `True` in `00_env_config`.

    If your organisation does not permit Fabric AI Functions, keep AI Enrichment disabled. You can still complete this step manually; AI only proposes authoring state and never performs Governance approval.

## 1. Select the governed table

Open `01_governance`, run the setup cells, and select the target produced in Step 2.

Use the Catalogue and latest profiling evidence to confirm that you are authoring against the intended physical table. The profile is evidence for Governance decisions, not part of the Data Contract payload.

## 2. Open the unified Data Contract workspace

Run `widget_data_contract()`.

The current workspace is organised into four tabs:

| Tab | What you author or review |
| --- | --- |
| **Table** | Table definition, Classification, Description, Grain & Row Key, Processing, Freshness, and Source Drift. |
| **Columns** | Column definition, profile evidence, Schema participation, Sensitive Data treatment, and column-level Data Quality rules. |
| **Business Rules** | Cross-column or more expressive Data Quality requirements authored from business intent. |
| **Manifest & Freeze** | The complete contract manifest, validation state, Save Data Contract, and Freeze lifecycle actions. |

Treat these tabs as one contract. They are different views of the same governed definition for one `table_id` and contract version.

## 3. Define the table

Start in **Table**.

### Table definition

Review or enter the table Description and select the information Classification.

When AI Enrichment is enabled, FabricOps can suggest the Description from governed Catalogue and profile context. Classification remains a Governance choice.

### Grain & Row Key

Define what one row represents, then select the smallest defensible column or column combination that should uniquely identify that row.

FabricOps uses the selected Row Key to author the table-level uniqueness expectation. Per-column distinctness is useful evidence, but it does not by itself prove that a composite key is unique.

When AI is enabled, **Suggest Grain & Row Key** can propose a candidate from the governed metadata and profile evidence. Review it before applying it.

### Processing

Review the target load strategy and its required parameters.

FabricOps keeps Processing inside the exact Data Contract JSON. A new draft first uses an observed Engineering Catalogue value when one exists. Otherwise it inherits the previous frozen contract when available, then falls back to `overwrite`.

Observed Engineering processing is read-only. Inherited or defaulted draft values remain editable until the version is frozen.

### Freshness and Source Drift

Enable these only when they represent real requirements.

**Freshness** applies when the table is consumed as a source and checks whether the selected timestamp is recent enough for the downstream pipeline.

**Source Drift** also applies when the table is consumed as a source and checks whether previously consumed source data has changed unexpectedly.

## 4. Review and govern each column

Open **Columns** and work through the columns that matter for the demo.

The left side keeps the selected column and physical context visible. The right side combines authoring with the latest profile evidence so Governance can make a decision without leaving the contract workspace.

### Column definition and Schema

Review the datatype and profile evidence, write the column Description, choose its Classification, and decide whether the column is required by the Schema Guardrail.

Profile evidence is observational. Do not turn every observed statistic or common value into a contract requirement.

### Sensitive Data

Sensitive Data is separate from information Classification.

| Decision | Meaning |
| --- | --- |
| **Classification** | How the organisation classifies the information, for example Public, Internal, Confidential, or Restricted. |
| **PII assessment** | Whether the governed context supports Direct PII, Indirect PII, or Not PII. |
| **Treatment** | The deterministic runtime action, such as Tokenize, Mask, Bucket, or Remove. |

When AI is enabled, FabricOps can propose a PII assessment, rationale, treatment, parameters, and Warn or Block action from the governed column context. It does not sample raw source rows for this feature.

Governance can accept, edit, ignore, or re-run the suggestion. Direct and Indirect PII rules require a reviewed reason before they are saved. A Not PII assessment remains authoring context and does not create an enforceable treatment.

### Column-level Data Quality

Use the column editor for the simple rules that naturally belong to one column:

| Rule | Use it for |
| --- | --- |
| **Completeness** | Missing or blank-value tolerance. |
| **Allowed Values** | Stable governed allow or block sets. |
| **Value Rules** | Numeric or date conditions such as above, below, between, or outside bounds. |
| **Pattern** | A regular expression requirement for populated text. |

These rules should stay understandable and deterministic. Do not encode a large, constantly changing reference dictionary inside the contract. Ingest that reference data through the pipeline, derive the required flag or value, then govern the resulting column with a simple rule.

AI is useful where interpretation is genuinely needed. Pattern can use an AI suggestion when enabled; the other simple column rules remain normal governed inputs.

## 5. Add cross-column Business Rules

Open **Business Rules** for requirements that are not naturally a single-column rule.

Write the business requirement in plain language and, when useful, select the relevant columns. With AI enabled, **Resolve rule** maps that intent to the smallest supported deterministic FabricOps DQ rule.

Examples include:

* end date must be after start date
* when status is Approved, approved date is required
* total amount must equal quantity × unit price × (1 - discount)
* either email or mobile number must be present

FabricOps first tries the known DQ patterns, including Uniqueness, Column Relationship, Conditional Completeness, and Conditional Values. When none can represent the requirement faithfully, it can propose a constrained PySpark Custom Expression.

A Custom Expression is intentionally the escape hatch for a bounded deterministic boolean rule. It is not a place for arbitrary pipeline logic. More complicated transformations, external lookups, or project logic should remain in `02_pipeline`, with the Data Contract governing the resulting data surface.

When a Custom Expression requires Engineering review, complete that review before freezing the contract.

## 6. Understand what AI can and cannot do

AI suggestions are advisory authoring state.

FabricOps may use AI for Description, Grain & Row Key, Sensitive Data, Pattern, and Business Rule resolution when the corresponding AI configuration is enabled. Suggestions use governed metadata, reviewed descriptions and classifications, and available profile evidence.

AI never:

* saves a Data Contract
* freezes a version
* activates a version for Production
* bypasses Guardrail validation
* performs runtime enforcement

Manual Description or Classification changes can make dependent suggestions stale. Re-run the relevant suggestion when you want advice based on the updated draft context.

Runtime enforcement remains deterministic through the normal FabricOps Guardrail functions.

## 7. Review the manifest

Open **Manifest & Freeze** and review the whole definition together.

Before freezing, you should be able to answer:

> What does one row represent, how is it identified, what does this table and its columns mean, what must be true, how is sensitive data handled, and how is the table allowed to be published?

Fix any validation issues before continuing.

## 8. Save and freeze

While a version is **draft**, **Save Data Contract** overwrites that draft version's complete JSON definition in place. FabricOps does not create lifecycle history for every intermediate save.

When the draft is ready for Engineering validation, choose **Freeze**. The same version becomes `frozen` and its JSON becomes immutable.

Further Governance edits begin in the next draft version seeded from the frozen contract.

Freezing does not activate the version for Production. It creates the exact immutable candidate Engineering Development will select and validate in Step 4.

## Expected result

You now have a frozen Data Contract built from the real Step 2 table evidence, including its table definition, Grain & Row Key, column governance, Guardrails, Processing, and any reviewed Business Rules.

**Previous:** [Step 2. Run the Development pipeline](02-run-pipeline.md)  
**Next:** [Step 4. Select and validate the Data Contract](04-run-pipeline-with-guardrails.md)

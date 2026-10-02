# Direct & Indirect PII Discovery & Treatment with Built-in AI Suggestions

![Direct and Indirect PII Discovery and Treatment with Built-in AI Suggestions](../assets/AiDatacontract.png)

## The problem

Identifying sensitive data is only the first step. The more important governance decision often comes next: what should happen to that data?

Governance users still need to decide how Direct or Indirect PII should be treated and understand what its classification becomes after that treatment is applied.

## The solution

FabricOps turns sensitive-data governance into a three-step workflow:

1. **Identify sensitivity** — tag each governed column as **Direct PII**, **Indirect PII**, or **Not PII**.
2. **Apply treatment** — for sensitive columns, choose how the data should be handled before publication. FabricOps supports **Mask, Bucket, Tokenize, and Remove**.
3. **Classify the governed output** — record the classification that applies **after treatment**, so it describes the data downstream consumers actually receive.

These decisions are captured in the Data Contract. Once the reviewed contract is frozen, validated, and activated, FabricOps applies the approved treatment deterministically in the data pipeline.

### AI-assisted authoring

FabricOps taps into Microsoft Fabric AI capabilities to make the authoring workflow faster. Using the metadata and profiling evidence FabricOps has already captured, AI can provide a first-pass suggestion for whether a column contains **Direct PII**, **Indirect PII**, or **Not PII** and, for sensitive columns, suggest one of the four supported treatments.

Governance reviews and can change those suggestions, then records the final post-treatment classification. Classification is deliberately not inferred automatically by the current AI suggestion path; it remains an explicit governance decision describing the governed output.

AI therefore accelerates the workflow, while the final decision lies with a human: **AI suggests → Human decides → Data Contract records → Pipeline enforces**.

## How it works

The core of the workflow is the governed decision itself, not a sequence of AI steps:

| Governance decision | What FabricOps captures | AI assistance |
| --- | --- | --- |
| **1. Sensitivity** | Direct PII, Indirect PII, or Not PII | Suggests a first-pass PII type from metadata and profile evidence |
| **2. Treatment** | Mask, Bucket, Tokenize, or Remove for sensitive columns | Suggests a supported treatment and parameters |
| **3. Post-treatment classification** | The classification of the data downstream consumers will receive | Remains an explicit Governance decision in the current implementation |

Together, these decisions form the sensitive-data portion of the **Data Contract**. Fabric AI assists during authoring, but the reviewed contract is the boundary between suggestion and enforcement:

- FabricOps uses metadata and profile evidence as context for AI-assisted suggestions.
- Governance reviews the sensitivity, treatment, and post-treatment classification.
- The reviewed decisions are captured in the Data Contract.
- Once activated, the pipeline enforces the approved treatment deterministically.

## What Governance decides

For each governed column, FabricOps presents sensitivity, treatment, and classification together because the classification should describe the data that downstream users actually receive.

| Decision | Meaning |
| --- | --- |
| **Sensitivity** | Whether the column is Direct PII, Indirect PII, or Not PII |
| **Treatment** | The transformation Governance chooses for sensitive data before publication |
| **Classification** | The governed classification of the column after the selected treatment is applied |

For example, a Direct PII column may require treatment before publication. Once that treatment is selected, Governance records the classification appropriate to the resulting column. A non-PII column with no treatment can simply retain the classification appropriate to its state.

## Where AI helps

Sensitive Data governance does not depend on AI.

When enabled, Fabric AI Functions use the available column metadata and profiling context to help assess Direct PII, Indirect PII, or Not PII. Governance reviews the suggestion and remains responsible for the governed treatment and classification.

Grain & Row Key candidates are derived deterministically from profile evidence. Business-language translation into enforceable Data Quality rules is a separate AI-assisted workflow; see [Generate Enforceable Data Quality Rules from Business Rules](business-rules-to-data-quality.md).

<details markdown="1">
<summary><strong>Under the hood: how AI sensitivity suggestions are produced</strong></summary>

### What FabricOps gives the AI

FabricOps does not send the whole source table. It builds a compact context from governed metadata and profiling evidence, including the table identity and description plus each column's name, data type, description, current classification, profile statistics, and limited frequency evidence.

Raw business-table rows are not included in this context.

### How Fabric AI Functions are used

![FabricOps AI-assisted sensitive data authoring implementation](../assets/sensitive-data-ai-implementation.svg)

FabricOps places the complete instruction into a single-row temporary pandas DataFrame with one column named `fabricops_prompt`, then invokes Microsoft Fabric AI Functions through:

```python
frame.ai.generate_response("{fabricops_prompt}")
```

This is a one-row AI request. The DataFrame is only the interface used to invoke Fabric AI Functions; FabricOps is not asking the model to process the business table row by row.

The response is expected as structured JSON covering the supplied columns, including the suggested PII type, reason, treatment, action, and treatment parameters. Before a suggestion is shown, FabricOps validates the returned columns and values against the supported sensitive-data model.

The suggestion remains transient authoring assistance. A human reviews or changes the sensitivity and treatment, then records the final post-treatment classification. Saving, freezing, and activation remain explicit FabricOps lifecycle actions; once activated, the approved treatment is applied deterministically by the pipeline.

For the canonical persisted schema and runtime behaviour, use [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md), [METADATA_GUARDRAIL](../reference/metadata/metadata_guardrail.md), and [Sensitive Data Treatments](../reference/sensitive-data-treatments.md).

</details>

## How FabricOps applies the treatment

Once the Data Contract is activated, FabricOps automatically applies the approved treatment when the pipeline writes the data. For example, a column marked for masking is masked before the governed output is published.

FabricOps supports **Mask, Bucket, Tokenize, and Remove**. The treatment is applied deterministically, so the pipeline follows the approved Data Contract rather than asking AI to make the decision again.

See [Sensitive Data Treatments](../reference/sensitive-data-treatments.md) for the exact behaviour of each treatment.

## Go deeper

For the authoring workflow, see [Step 3: Author and freeze the Data Contract](../guided-demo/03-author-and-freeze-data-contract.md).

For the persisted contract schema, see [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md).

# Sensitive Data Classification & Treatment

![Sensitive Data Classification & Treatment](../assets/AiDatacontract.png)

## The problem

A useful Data Contract has to combine what Engineering actually produced with Governance decisions about meaning, quality, sensitivity, and acceptable behaviour. Recreating technical metadata manually is slow, while allowing AI-generated suggestions to become policy automatically would make the governed definition difficult to trust and review.

## The solution

FabricOps makes the Data Contract explicit, versioned, and executable. Microsoft Fabric AI Functions can assist where interpretation is useful, while deterministic FabricOps metadata and Governance decisions remain the source of truth.

The contract combines the observed Engineering definition with Governance-owned decisions rather than asking users to recreate technical metadata manually.

## How it works

```mermaid
flowchart LR
    A["Observe Engineering<br/>metadata"] --> B["Author contract"]
    C["AI-assisted<br/>suggestions"] --> B
    B --> D["Governance review"]
    D --> E["Freeze version"]
    E --> F["Validate in Development"]
    F --> G["Activate"]
    G --> H["Enforce in Production"]
    F -. "iterate" .-> B
```

## Implementation details

### What the Data Contract captures

A Data Contract is the governed definition for one `table_id`. Its versioned `contract_payload_json` brings together:

- **Contract lifecycle** — contract identity, version, draft/frozen state, and Production activation.
- **Table definition** — the governed table, observed columns and data types, and processing configuration.
- **Enrichment** — descriptions, classifications, and table grain that explain the data.
- **Guardrails** — executable Schema, Freshness, Source Drift, Data Quality, and Sensitive Data expectations.

Governance authors and reviews the contract through [`widget_data_contract()`](../api/reference/widget_data_contract.md) in `01_governance`.

### Where the definition comes from

Not every part of a Data Contract is authored the same way.

| Source | What it contributes | Role |
| --- | --- | --- |
| **FabricOps deterministic capture** | `table_id`, physical table identity, observed columns and data types, profiling and pipeline context, and processing context available from Engineering metadata | Grounds the contract in what Engineering actually produced |
| **Manual Governance authoring** | Reviewed descriptions, classifications, grain, Guardrail configuration, actions, and other governed decisions | Creates the authoritative business and governance definition |
| **AI-assisted suggestions** | Descriptions, classifications, Grain & Row Key suggestions, Sensitive Data assessment and treatment, Pattern suggestions, and business-rule interpretation | Accelerates authoring; Governance reviews before applying |

**AI suggestions never become the governed definition simply because AI produced them.** They are proposed authoring inputs. Governance decides what is applied, saved, and frozen.

### What is being captured

For example, the physical columns and data types originate from the Data Catalogue. Governance can then add descriptive Enrichment and executable Guardrails against those same columns. Processing records how the governed target is expected to be written.

This produces one versioned manifest that Engineering can resolve and execute instead of maintaining a separate policy document beside the pipeline.

### Available Guardrails

| Guardrail | What it governs |
| --- | --- |
| **Schema** | Whether the real data structure matches the governed definition |
| **Freshness** | Whether the source or governed data meets its expected freshness |
| **Source Drift** | Whether source observations have changed outside the accepted expectation |
| **Data Quality** | Deterministic quality rules such as completeness, uniqueness, allowed values, value rules, and patterns |
| **Sensitive Data** | Governed treatment of sensitive columns before Data Quality checks and publication. FabricOps supports Mask, Bucket, Tokenize, and Remove. See [Sensitive Data Treatments](../reference/sensitive-data-treatments.md) for examples and exact runtime behavior. |

Guardrails can be configured with **Warn** or **Block** behaviour. The contract records the governed expectation; FabricOps runtime functions perform the actual checks.

### Where and when enforcement happens

The contract moves through a deliberate Governance ↔ Engineering cycle:

1. **Author** — Governance works against the real `table_id` in `01_governance`.
2. **Freeze** — the reviewed contract version becomes immutable.
3. **Select and validate in Development** — `02_pipeline` selects the exact frozen version and executes its Guardrails against the real pipeline.
4. **Iterate when needed** — Governance authors another version if the definition changes; Engineering validates that new immutable version again.
5. **Activate** — the tested frozen version is linked to the Data Agreement and marked active for Production.
6. **Enforce in Production** — `02_pipeline` automatically resolves the active contract and executes the same governed expectations.

The runtime enforcement functions are:

- [`check_schema()`](../api/reference/check_schema.md)
- [`check_freshness()`](../api/reference/check_freshness.md)
- [`check_source_drift()`](../api/reference/check_source_drift.md)
- [`check_dq()`](../api/reference/check_dq.md)
- [`check_sensitive_data()`](../api/reference/check_sensitive_data.md)

Runtime outcomes are recorded in `METADATA_GUARDRAIL_RESULTS`.

### Where AI helps

Sensitive Data governance does not depend on AI. Governance can classify and configure treatment manually. AI is an optional authoring aid; it is **not the enforcement engine**.

Governance can author descriptions, classifications, and Sensitive Data treatments manually. When enabled, Fabric AI Functions can use Data Catalogue and profiling context to suggest descriptions, classifications, and Sensitive Data classification/treatment choices. Grain & Row Key candidates are derived deterministically from profile evidence, not AI. Business-language translation into enforceable Data Quality rules is a separate AI-assisted workflow; see [Generate Enforceable Data Quality Rules from Business Rules](business-rules-to-data-quality.md).

Governance reviews those suggestions in the same authoring workflow as manually entered decisions. Once accepted into a frozen Data Contract, enforcement is deterministic through the FabricOps Guardrail functions.

That separation is intentional: **manual Governance authoring is always available; AI can accelerate interpretation-heavy authoring; the approved Data Contract remains explicit and reviewable; Engineering enforcement remains deterministic.**

## Go deeper

For the hands-on workflow, see [Step 3: Author and freeze the Data Contract](../guided-demo/03-author-and-freeze-data-contract.md).

For the persisted contract schema, see [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md).

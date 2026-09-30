# Sensitive Data Treatments

Sensitive Data Guardrails do more than detect sensitive columns. They can **prepare the DataFrame before Data Quality checks and before a governed write**.

The treatment is part of the frozen Data Contract for a column. When `orchestrate_write()` evaluates the target, FabricOps applies the configured treatment and passes the resulting DataFrame to the remaining Write-side stages.

```text
Input DataFrame
→ Schema
→ Sensitive Data treatment
→ Source Drift
→ Data Quality
→ Guardrail Coverage
→ Write
→ Profile
```

## Available treatments

| Treatment | What happens to the column | Typical effect |
| --- | --- | --- |
| **Mask** | Keeps the column and obscures the middle characters while optionally preserving characters at the start and end. Nulls remain null. | `C1234567` can become a masked string such as `C******7`, depending on the configured preservation settings. |
| **Bucket** | Keeps a numeric column but replaces exact values with configured coarse labels. Nulls remain null and rows are not aggregated. | An exact age or amount can become a range/category label. |
| **Tokenize** | Keeps the column and replaces each distinct non-null value with an opaque UUID token. | Repeated source values use the same token when the same token mapping is supplied. |
| **Remove** | Drops the governed column from the prepared DataFrame. | The column is absent from the governed write and subsequent target profile. |

### Mask

Masking casts the governed value to a string, preserves the configured number of leading and trailing characters, and replaces the hidden middle characters with the configured mask character.

The column remains available to downstream Data Quality checks and to the target write, but its published representation is the masked value.

### Bucket

Bucketing is available only for numeric source columns. Governance supplies strictly increasing numeric boundaries and one label for each boundary.

Values below the first boundary use the first label. Each later boundary is inclusive, and values at or above the final boundary use the final label. FabricOps replaces the exact numeric value with the configured label; it does not aggregate or remove rows.

### Tokenize

Tokenization replaces each distinct non-null value with an opaque UUID token and returns a `support_mapping` containing the original-to-token relationship.

FabricOps **does not persist this mapping automatically**. The caller owns it. To preserve the same token for the same original value across runs, persist the mapping appropriately and provide it back to `check_sensitive_data()` as `existing_mapping`.

Raw original values are excluded from `METADATA_GUARDRAIL_RESULTS`; they exist in the returned support mapping.

### Remove

Remove drops the governed column before downstream Data Quality checks and before publication.

This can naturally produce a new governed state. For example:

```text
Contract v1
customer_id exists
→ Sensitive Data: Remove
→ governed target written without customer_id
→ target profile no longer contains customer_id
→ Governance can author a later contract version for the evolved schema
```

The frozen v1 remains the historical contract that records why the incoming column was removed. A later version can govern a shorter schema when that is the intended boundary definition.

## Validate versus Enforce

The treatment logic is the same, but publication differs:

- **Validate** applies the treatment to the in-memory prepared DataFrame so downstream Guardrails can be exercised, but the target is not written.
- **Enforce** applies the treatment and, if the remaining blocking Guardrails pass, writes the treated DataFrame.

This makes Development validation representative of the treatment that will occur when the contract is activated and enforced in Production.

## Warn and Block

Warn and Block apply when a treatment **cannot be applied**, rather than treating the mere presence of sensitive data as a failure.

- **Warn** records the treatment failure, leaves the input unchanged for that rule, and permits the pipeline to continue.
- **Block** records the failure and requires the caller to stop before writing.

A successfully applied treatment is a passing Sensitive Data Guardrail result.

## Lifecycle implications

Sensitive Data treatment happens before Data Quality and before the final target profile. This means downstream governance sees the treated state:

- **Mask** preserves the column with a string representation.
- **Bucket** preserves the column with categorical labels.
- **Tokenize** preserves the column with opaque token values.
- **Remove** eliminates the column entirely.

Data Quality rules therefore need to make sense against the **post-treatment DataFrame**, not only the original transformed values.

## Related documentation

- [AI-assisted Data Contract Authoring](../solutions/ai-assisted-data-contract-authoring.md)
- [Plug-and-Play Data Pipelines with Data Contract Enforcement](../solutions/plug-and-play-data-pipelines.md)
- [`check_sensitive_data()`](../api/reference/check_sensitive_data.md)
- [Guardrail metadata](metadata/metadata_guardrail.md)
- [Guardrail Results](metadata/metadata_guardrail_results.md)

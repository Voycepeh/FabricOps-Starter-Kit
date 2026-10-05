# Sensitive Data Treatments

Sensitive Data Guardrails can **prepare the DataFrame before Data Quality checks and before a governed write**.

The treatment is part of the frozen Data Contract for a column. During [`orchestrate_write()`](../api/reference/orchestrate_write.md), FabricOps applies the configured treatment and passes the prepared DataFrame to the remaining Write-side stages.

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

| Treatment | Result |
| --- | --- |
| **Mask** | Keep the column but obscure part of its value. |
| **Bucket** | Keep a numeric column but replace exact values with governed category labels. |
| **Tokenize** | Keep the column but replace each distinct value with an opaque token. |
| **Remove** | Drop the column from the prepared DataFrame. |

??? example "Mask — preserve the column, hide the sensitive value"

    ### What it does

    Mask casts the governed value to a string, optionally preserves characters at the beginning and end, and replaces the hidden middle characters with the configured mask character.

    Null values remain null.

    ### When to use it

    Use Mask when consumers still need a recognizable or join-independent representation of the field, but should not see the complete original value.

    ### Example

    Input:

    | customer_id | customer_name |
    | --- | --- |
    | C1234567 | Alice |
    | C7654321 | Bob |
    | null | Unknown |

    With the first and last character preserved, the prepared DataFrame can become:

    | customer_id | customer_name |
    | --- | --- |
    | C******7 | Alice |
    | C******1 | Bob |
    | null | Unknown |

    The column remains available to downstream Data Quality checks and the governed target write, but those stages see the **masked representation**.

??? example "Bucket — replace exact numeric values with governed ranges"

    ### What it does

    Bucket replaces an exact numeric value with a configured coarse label.

    It does not aggregate rows or remove records. The source column must be numeric, boundaries must be strictly increasing, and the configured labels must match the governed bins.

    Null values remain null.

    ### When to use it

    Use Bucket when downstream consumers need a useful category but do not need the precise sensitive number, such as age bands or amount ranges.

    ### Example

    Input:

    | customer_id | age |
    | --- | ---: |
    | C001 | 22 |
    | C002 | 37 |
    | C003 | 68 |
    | C004 | null |

    With governed labels such as `18–29`, `30–59`, and `60+`, the prepared DataFrame becomes:

    | customer_id | age |
    | --- | --- |
    | C001 | 18–29 |
    | C002 | 30–59 |
    | C003 | 60+ |
    | C004 | null |

    The exact age is no longer passed to downstream DQ or publication.

??? example "Tokenize — replace values with stable opaque identifiers"

    ### What it does

    Tokenize replaces each distinct non-null source value with an opaque UUID token.

    Repeated source values use the same token when the same token mapping is supplied.

    ### When to use it

    Use Tokenize when downstream processing needs consistent pseudonymous identity without exposing the original value.

    ### Example

    Input:

    | order_id | customer_id |
    | --- | --- |
    | O001 | C001 |
    | O002 | C002 |
    | O003 | C001 |

    Prepared DataFrame:

    | order_id | customer_id |
    | --- | --- |
    | O001 | 550e8400-e29b-41d4-a716-446655440000 |
    | O002 | 6ba7b810-9dad-11d1-80b4-00c04fd430c8 |
    | O003 | 550e8400-e29b-41d4-a716-446655440000 |

    C001 maps to the same token in both rows.

    ### Token mapping ownership

    FabricOps returns the original-to-token relationship as `support_mapping`, but **does not persist it automatically**.

    To keep tokens stable across runs, the project must persist the mapping appropriately and provide it back to [`check_sensitive_data()`](../api/reference/check_sensitive_data.md) as `existing_mapping`.

    Raw original values are excluded from `METADATA_GUARDRAIL_RESULTS`; they exist in the returned support mapping.

??? example "Remove — drop the sensitive column before publication"

    ### What it does

    Remove drops the governed column from the prepared DataFrame before downstream Data Quality checks and publication.

    ### When to use it

    Use Remove when the sensitive attribute is not required by the governed target at all.

    ### Example

    Input:

    | order_id | customer_id | order_total |
    | --- | --- | ---: |
    | O001 | C001 | 120.00 |
    | O002 | C002 | 85.00 |

    After `customer_id → Remove`:

    | order_id | order_total |
    | --- | ---: |
    | O001 | 120.00 |
    | O002 | 85.00 |

    `customer_id` is absent from downstream DQ, the governed target, and the subsequent target profile.

    ### Contract lifecycle

    This can naturally produce a new governed state:

    ```text
    Contract v1
    customer_id exists
    → Sensitive Data: Remove
    → governed target written without customer_id
    → target profile no longer contains customer_id
    → Governance can author a later contract version for the evolved schema
    ```

    Frozen v1 remains the historical contract recording why the incoming column was removed. A later contract version can govern the shorter schema when that becomes the intended boundary definition.

## Validate versus Enforce

The treatment logic is the same; publication is different.

| Mode | Treatment behavior | Target publication |
| --- | --- | --- |
| **Validate** | Applies treatment to the in-memory prepared DataFrame so downstream Guardrails exercise the treated state. | No target write. |
| **Enforce** | Applies treatment before downstream Guardrails. | Treated DataFrame is written only if the remaining blocking Guardrails pass. |

This makes Development validation representative of the treatment that will occur when the contract is activated and enforced in Production.

## Warn and Block

Warn and Block apply when a treatment **cannot be applied**. The mere presence of sensitive data is not itself a failed Sensitive Data Guardrail.

| Action | Treatment failure behavior |
| --- | --- |
| **Warn** | Record the failure, leave the input unchanged for that rule, and allow execution to continue. |
| **Block** | Record the failure and stop the governed write path. |

A successfully applied treatment is a passing Sensitive Data Guardrail result.

## Downstream implications

Data Quality sees the **post-treatment DataFrame**.

| Treatment | What downstream DQ sees |
| --- | --- |
| Mask | Masked string values |
| Bucket | Governed category labels |
| Tokenize | Opaque token values |
| Remove | Column no longer exists |

DQ rules therefore need to make sense against the treated representation, not only the original transformed values.

The final target profile is also based on the successfully published treated target. For example, a removed column does not appear in the resulting target profile.

## Related documentation

- [AI-assisted Data Contract Authoring](../solutions/ai-assisted-data-contract-authoring.md)
- [Plug-and-Play Data Pipelines with Data Contract Enforcement](../solutions/plug-and-play-data-pipelines.md)
- [Read & Write Modes](read-and-load-strategies.md)
- [`check_sensitive_data()`](../api/reference/check_sensitive_data.md)
- [Guardrail metadata](metadata/metadata_guardrail.md)
- [Guardrail Results](metadata/metadata_guardrail_results.md)

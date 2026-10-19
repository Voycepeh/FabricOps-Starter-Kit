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

    Mask defaults to hiding the complete value. Choose **Partial mask** to preserve approved characters at the beginning or end. The widget uses `*` for new masks and hides that technical setting. Existing saved mask characters remain supported.

    Short values that cannot safely accommodate the preserved characters are fully masked; they are never returned unchanged.

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

    It does not aggregate rows or remove records. The source column must be numeric.

    Choose **Approved ranges** to supply comma-separated lower bounds and matching labels. Bounds must be strictly increasing. The first label covers all values below the second bound, including values below the first bound. The last label covers all values at or above the final bound. Existing saved policies keep this behavior.

    Choose **Fixed width** for equal-width intervals anchored at a starting point. Width `10` and starting point `0` produce `[-10.0, 0.0)`, `[0.0, 10.0)`, `[10.0, 20.0)`, and so on. Lower boundaries are inclusive and upper boundaries exclusive. These intervals never change with batch minima, maxima or frequencies.

    Explore distributions and agree useful boundaries before authoring the contract. Automatic quantiles, equal-population groups, and arbitrary text mappings belong in Engineering transformations. Text grouping does not imply aggregation; use a managed reference mapping when categories need broader labels.

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

    FabricOps returns the original-to-token relationship as `result["sensitive_result"]["support_mapping"]`.

    Engineering can configure a restricted mapping store once, as described below. Enforce then reuses saved tokens and inserts missing assignments automatically. Validate reads existing mappings but does not persist newly generated assignments. With no configured store, Engineering must persist and supply `existing_mapping` on later runs. Returned mappings retain previous assignments for each treated table/column, including identities absent from the current batch.

    Token identities are scoped to the canonical table and column. They do not automatically join identities across different tables or columns.

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

## Configure managed token reuse

**Engineering owns the mapping store; Governance only chooses Tokenize.**

Configure an existing Lakehouse store in `00_env_config` and give it a separate access boundary from consumer data and general Metadata. Provision an empty Delta table with five string columns: `table_id`, `column_id`, `original_value`, `token_value`, and `original_data_type`. Only authorized pipeline/service identities should read or write it. FabricOps does not create permissions or silently create this table.

Set this project-level option when constructing `GovernanceConfig`:

```python
sensitive_data_token_mapping={
    "store": "Sensitive",
    "schema": "vault",
    "table_name": "token_mappings",
}
```

The store must resolve to a Lakehouse. The `Metadata` store key is rejected. Missing tables, invalid schemas, and conflicting original/token assignments block treatment. Token allocation uses insert-only Delta merges followed by an authoritative reread. Serialize allocation for the same table/column; a Delta merge is not a uniqueness constraint for competing writers. Existing conflicting mappings are rejected, never silently selected.

Mappings may reserve tokens before a later Guardrail or publication fails. Retaining those reservations makes retries stable. Validate never writes to the mapping store. The result's `sensitive_result["mapping_persisted"]` reports whether Enforce persisted the mapping. Returned mappings still contain original values, even when storage is managed.

## Decide and validate treatment

| Responsibility | Owner |
| --- | --- |
| Agree permitted detail and useful bands | Business and Governance |
| Explore distributions; implement text mappings | Engineering |
| Freeze the approved deterministic treatment | Data Contract author |
| Apply treatment before Grain, DQ and publication | FabricOps |

The authoring widget does not need every source row to declare fixed rules. Evaluating disclosure risk needs representative population evidence and consideration of combinations of identifying columns. Bucketing or tokenization alone does not establish anonymisation. Treatment covers the incoming write input; changing a rule does not rewrite historical target rows or SCD2 versions.

Sensitive Data AI receives column metadata and numeric row/null/distinct counts and percentages. Raw profile extrema, frequency values, samples and other profile statistics are excluded from its context. AI suggestions always resolve to Block and remain subject to human review.

## Validate versus Enforce

The treatment logic is the same; publication is different.

| Mode | Treatment behavior | Target publication |
| --- | --- | --- |
| **Validate** | Applies treatment to the in-memory prepared DataFrame so downstream Guardrails exercise the treated state. | No target write. |
| **Enforce** | Applies treatment before downstream Guardrails. | Treated DataFrame is written only if the remaining blocking Guardrails pass. |

This makes Development validation representative of the treatment that will occur when the contract is activated and enforced in Production.

After consuming the prepared DataFrame and persisting a returned token mapping, call its `unpersist()` method to release its cache. One returned mapping owns the cache for every tokenized column. Failed orchestration releases token caches automatically.

## Treatment failures block publication

Every active Sensitive Data treatment must succeed. FabricOps records a failed treatment in `METADATA_GUARDRAIL_RESULTS` and stops `orchestrate_write()` before publication. There is no Warn/Block selector for Sensitive Data.

A successfully applied treatment produces a passing result. Classification Enrichment alone does not activate a treatment.

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
- [Sensitive Data stage](../api/reference/orchestrate_write.md)
- [Data Contract payload](metadata/metadata_data_contract.md)
- [Guardrail Results](metadata/metadata_guardrail_results.md)

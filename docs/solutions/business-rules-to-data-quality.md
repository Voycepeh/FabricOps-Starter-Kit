# Data Quality Rules from Natural Language

![Business rules converted to enforceable Data Quality rules](../assets/BusinessRuletoDQ.png)

## The problem

FabricOps already provides simple controls for common Data Quality expectations. At the table level, Governance can configure Schema, Freshness, and Source Drift Guardrails. At the column level, common rules such as Completeness, Uniqueness, Value Sets, and Ranges can be configured directly.

That is a useful starting point, but real-world definitions of clean data are often more nuanced. Business rules can combine conditions, relationships, thresholds, and several columns in one requirement. Traditionally, that business knowledge has to be explained to Engineering, translated into validation logic, reviewed, and implemented.

## The solution

FabricOps lets users describe what clean data means in natural language. Built-in AI suggestions combine that requirement with governed table metadata, profile evidence, and a predefined list of supported DQ rule patterns to propose the smallest set of deterministic rules that represents the requirement.

One business requirement can therefore become several atomic DQ rules. Standard rule patterns are used wherever possible. Only requirements that cannot be represented faithfully by those patterns fall back to a constrained Custom Expression, where Engineering review is especially important.

The AI accelerates the translation from business knowledge to executable rules. It is not the runtime enforcement engine. Once reviewed and saved into the Data Contract, the resulting rules are explicit and enforced deterministically by FabricOps.

## The rule patterns

FabricOps gives the AI a bounded rule grammar rather than asking it to invent arbitrary validation logic.

| Pattern | What it expresses |
| --- | --- |
| **Completeness** | Maximum missing percentage for one column, with explicit blank handling. |
| **Uniqueness** | One column or a combination of columns must meet the required uniqueness level. |
| **Whitelist** | A column value must belong to an approved set. |
| **Blacklist** | A column value must not belong to a blocked set. |
| **Range** | A value must satisfy governed minimum or maximum bounds. |
| **Pattern** | Populated text must match a governed regular expression. |
| **Column Relationship** | Compare two columns row by row with `=`, `!=`, `>`, `>=`, `<`, or `<=`. |
| **Conditional Completeness** | When a condition is true, another column must be populated. |
| **Conditional Values** | When a condition is true, another column must satisfy a whitelist or blacklist. |
| **Custom Expression** | A constrained PySpark boolean expression for requirements the standard patterns cannot represent faithfully. |

<details markdown="1">
<summary><strong>Under the hood: how AI suggestions are produced</strong></summary>

### What FabricOps gives the AI

The AI does not receive the whole source table. FabricOps builds a compact governed context containing the table name, schema, layer, table description and classification, plus each column's name, data type, description, classification, profile evidence, and a few example values. Existing DQ rules are also included so the AI does not propose duplicates.

FabricOps combines four things into the instruction sent to the model:

1. the configured Business Rule prompt;
2. the user's plain-language business requirement and optional selected-column constraint;
3. the governed table and profile context;
4. the supported DQ rule grammar above, including the parameters and restrictions for every rule type.

Profile values are evidence only. The prompt explicitly tells the AI not to turn observed values into contractual thresholds, whitelists, blacklists, mappings, or patterns unless the business requirement actually states them.

### How Fabric AI Functions are used

![FabricOps AI-assisted DQ rule authoring implementation](../assets/business-rule-dq-implementation.svg)

FabricOps uses the Microsoft Fabric AI Functions pandas extension through `ai.generate_response()`.

The complete instruction is placed into a **single-row temporary pandas DataFrame** with one column named `fabricops_prompt`. FabricOps then calls:

```python
frame.ai.generate_response("{fabricops_prompt}")
```

This is deliberately a one-row AI request. The DataFrame is only the interface used to invoke Fabric AI Functions; FabricOps is not asking the model to process the business table row by row. The model receives the compact metadata/profile context and returns one JSON response.

The response must be a JSON array of atomic rule proposals. A compound requirement can therefore become several independent rules in one call.

Before anything is accepted, FabricOps validates the response: rule types must be supported, referenced columns must exist, parameters must have the expected shape, selected-column constraints must be respected, and executable content is tightly constrained. A Custom Expression is accepted only as a safe PySpark boolean Column expression using the supported grammar.

Internally the visible rule patterns map to nine canonical `rule_type` values because Whitelist and Blacklist are the `allow` and `block` modes of `value_set`.

</details>

## Example: one business requirement becomes multiple rules

The Guided Demo already provides a canonical 120-row `orders` table and a separate `orders_guardrail_failures.csv` fixture with deliberate failures. The same data can be used to demonstrate natural-language rule authoring and enforcement.

The Orders table contains `order_id`, `customer_id`, `order_datetime`, `modified_datetime`, `product_id`, `quantity`, `unit_price`, `discount`, `order_status`, and `shipping_country`.

Enter one compound Business Rule:

> Orders must have a customer and product. Quantity and unit price must be greater than zero. Discount must be between 0% and 20%. Order status must be NEW, PROCESSING, SHIPPED, DELIVERED, or CANCELLED. For shipped or delivered orders, the modified timestamp cannot be earlier than the order timestamp.

FabricOps can decompose that single requirement into multiple atomic rules:

| Part of the business requirement | Suggested FabricOps rule | Deterministic meaning |
| --- | --- | --- |
| Orders must have a customer | **Completeness** on `customer_id` | `customer_id` must be populated. |
| Orders must have a product | **Completeness** on `product_id` | `product_id` must be populated. |
| Quantity must be greater than zero | **Range** on `quantity` | Minimum `0`, exclusive. |
| Unit price must be greater than zero | **Range** on `unit_price` | Minimum `0`, exclusive. |
| Discount must be between 0% and 20% | **Range** on `discount` | `0 <= discount <= 0.20`. |
| Only approved order statuses are valid | **Whitelist** on `order_status` | Value must be one of `NEW`, `PROCESSING`, `SHIPPED`, `DELIVERED`, or `CANCELLED`. |
| Shipped or delivered orders cannot move backwards in time | **Custom Expression** | When status is SHIPPED or DELIVERED, `modified_datetime >= order_datetime`. |

This is the key feature: **one natural-language business rule can produce several known, independently reviewable DQ rules instead of one opaque AI-generated check.**

The existing failure fixture then makes the enforcement visible without inventing another demo table. For example, `GF004` has a negative quantity, `GF005` has a negative unit price, `GF006` has a discount of `1.25`, `GF007` has an `UNKNOWN` order status, and `GF009` has a missing customer.

## What enforcement looks like

At runtime the AI is no longer involved. The activated Data Contract supplies the explicit rules and FabricOps evaluates them against the pipeline DataFrame.

Conceptually, each applicable rule is a boolean question for each row: **does this row satisfy the rule?** Conditional rules only apply when their condition matches. FabricOps uses those evaluations to tag the DataFrame with the rules that failed and the resulting row status.

Using the existing Guardrail failure fixture, row-level inspection can show the generated rules catching real demo rows:

| order_id | Failed rule | `_dq_check_status` | Why |
| --- | --- | --- | --- |
| GF004 | quantity range | `failed`* | `quantity = -1`. |
| GF005 | unit price range | `failed`* | `unit_price = -399.0`. |
| GF006 | discount range | `failed`* | `discount = 1.25`, above the 20% maximum. |
| GF007 | order status whitelist | `failed`* | `order_status = "UNKNOWN"`. |
| GF009 | customer completeness | `failed`* | `customer_id` is missing. |

The timestamp relationship is still generated and enforced even though the current failure fixture does not deliberately violate it. A recording can therefore show both the generated rule set and several independent failures using the existing demo assets.

\* The exact row status depends on each rule's configured severity/action. FabricOps distinguishes warning-only failures from blocking/error failures.

The failed business rows themselves are **not persisted** in `METADATA_GUARDRAIL_RESULTS`. That metadata table stores the aggregate outcome for each Guardrail execution. A failing DQ rule result contains identifiers for the rule and contract plus fields such as `status`, `can_continue`, `severity`, `reason`, `execution_type`, `run_id`, and the aggregate `result_payload_json`.

So the two views serve different purposes:

| View | Purpose |
| --- | --- |
| **Tagged pipeline DataFrame** | Inspect which business rows failed which rules through `_dq_failed_rules` and `_dq_check_status`. |
| **METADATA_GUARDRAIL_RESULTS** | Persist the aggregate pass/fail outcome and continuation decision for the governed execution. |

If a failing rule is configured to block, the aggregate result sets the continuation decision accordingly and the governed pipeline can stop before the target write.

## Why the AI output stays governable

AI is used only to translate intent into candidate rule definitions. FabricOps still controls the allowed rule vocabulary, validates the returned JSON, checks column references and parameters, constrains Custom Expressions, requires human review, and performs the actual enforcement deterministically.

That means the same rule can be authored manually or suggested by AI and still ends up in the same Data Contract and the same runtime rule engine.

## Go deeper

See [Step 3: Author and freeze the Data Contract](../guided-demo/03-author-and-freeze-data-contract.md) for authoring and review, and [METADATA_GUARDRAIL_RESULTS](../reference/metadata/metadata_guardrail_results.md) for the persisted execution-result schema.

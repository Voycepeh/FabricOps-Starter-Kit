# Data Quality Rules from Natural Language

<span class="fabricops-release-status fabricops-release-status--preview">Preview</span>

![Business rules converted to enforceable Data Quality rules](../assets/BusinessRuletoDQ.png)

## The problem

Common Data Quality checks are easy to describe when the requirement maps directly to one rule. Governance can configure checks such as Completeness, Uniqueness, Value Sets, and Ranges directly.

Real business requirements are often more nuanced. One sentence can combine several columns, thresholds, conditions, and relationships. Translating that business intent into separate executable checks usually requires Engineering to interpret the requirement, implement the logic, and send it back for review.

That creates friction between the person who knows what clean data means and the person who has to turn that meaning into code.

## The solution

FabricOps lets Governance describe what clean data means in natural language.

Built in AI suggestions combine that requirement with governed table metadata, profile evidence, and the supported Data Quality rule vocabulary. FabricOps then proposes the smallest set of explicit rules that preserves the requirement.

A single business requirement can therefore become several atomic, independently reviewable rules. Standard rule types are preferred wherever they can represent the requirement faithfully. A constrained Custom Expression is used only when the supported structured rules cannot preserve the intended logic.

Once reviewed and saved into the Data Contract, the resulting rules are explicit. Runtime enforcement is deterministic and does not depend on AI.

**Natural language requirement → AI assisted translation → Human review → Data Contract → Deterministic enforcement**

## How it works

FabricOps separates business judgement, AI assisted translation, and deterministic enforcement.

| Responsibility | What happens |
| --- | --- |
| **Human configures and decides** | Describe the business requirement in natural language, optionally constrain it to selected columns, then review, change, or reject the proposed rules before saving them. |
| **AI supports** | Uses the requirement plus governed metadata and profile evidence to decompose the intent into the smallest supported set of atomic Data Quality rules. |
| **FabricOps handles deterministically** | Supplies the supported rule grammar, validates the returned rule types, columns, parameters, and expressions, records approved rules in the Data Contract, and evaluates them during governed pipeline execution. |

The AI does not decide whether data passes at runtime. It helps author candidate rule definitions. FabricOps performs the actual checks using the reviewed Data Contract.

<details markdown="1">
<summary><strong>Under the hood: how natural language becomes governed rules</strong></summary>

### What FabricOps gives the AI

FabricOps does not send the whole source table. It builds a compact governed context containing the table identity and description plus relevant column names, data types, descriptions, classifications, profile evidence, limited example values, and existing Data Quality rules.

The instruction combines:

1. the configured Business Rule prompt;
2. the user's natural language requirement and any selected column constraint;
3. the governed metadata and profile context;
4. the canonical supported Data Quality rule grammar and its parameter constraints.

Profile evidence is context, not policy. Observed values are not automatically converted into contractual thresholds, value sets, mappings, or patterns unless the requirement states them.

### How Fabric AI Functions are used

![FabricOps AI assisted DQ rule authoring implementation](../assets/business-rule-dq-implementation.svg)

FabricOps places the complete instruction into a single row temporary pandas DataFrame with a column named `fabricops_prompt`, then invokes Microsoft Fabric AI Functions through:

```python
frame.ai.generate_response("{fabricops_prompt}")
```

The DataFrame is only the interface used to invoke Fabric AI Functions. FabricOps is not processing the business table row by row with AI.

The response must be structured JSON containing atomic rule proposals. Before a proposal can be added to the draft, FabricOps validates the rule type, referenced columns, parameter shape, selected column constraints, and executable content.

A Custom Expression is accepted only as a constrained PySpark boolean Column expression using the supported grammar.

At runtime, AI is no longer involved. FabricOps evaluates the approved rules deterministically against the pipeline DataFrame and records the aggregate Guardrail execution result.

</details>

## Example

??? example "One business requirement becomes multiple Data Quality rules"

    Suppose Governance enters this requirement for the guided demo Orders table:

    > Orders must have a customer and product. Quantity and unit price must be greater than zero. Discount must be between 0% and 20%. Order status must be NEW, PROCESSING, SHIPPED, DELIVERED, or CANCELLED. For shipped or delivered orders, the modified timestamp cannot be earlier than the order timestamp.

    FabricOps can decompose that one requirement into several independently reviewable rules:

    | Requirement | Suggested rule | Deterministic meaning |
    | --- | --- | --- |
    | Customer is required | **Completeness** on `customer_id` | `customer_id` must be populated. |
    | Product is required | **Completeness** on `product_id` | `product_id` must be populated. |
    | Quantity must be positive | **Range** on `quantity` | Minimum `0`, exclusive. |
    | Unit price must be positive | **Range** on `unit_price` | Minimum `0`, exclusive. |
    | Discount must be between 0% and 20% | **Range** on `discount` | `0 <= discount <= 0.20`. |
    | Only approved statuses are valid | **Whitelist** on `order_status` | Value must be one of `NEW`, `PROCESSING`, `SHIPPED`, `DELIVERED`, or `CANCELLED`. |
    | Shipped or delivered orders cannot move backwards in time | **Custom Expression** | When status is SHIPPED or DELIVERED, `modified_datetime >= order_datetime`. |

    The important part is that FabricOps does not turn the entire sentence into one opaque AI generated check. Each resolved rule remains visible and reviewable before it becomes part of the Data Contract.

    During runtime, the approved rules are evaluated against the pipeline DataFrame. Row level inspection can show which rules failed through `_dq_failed_rules` and `_dq_check_status`, while `METADATA_GUARDRAIL_RESULTS` stores the aggregate execution outcome and continuation decision.

## Go deeper

For the authoritative rule types, parameters, constraints, and examples, see the [Data Quality Rules reference](../reference/dq-rules/index.md).

For the authoring and review workflow, see [Step 3: Author and freeze the Data Contract](../guided-demo/03-author-and-freeze-data-contract.md).

For persisted Guardrail execution outcomes, see [METADATA_GUARDRAIL_RESULTS](../reference/metadata/metadata_guardrail_results.md).

# expression_true — Custom expression

## What this rule does

Evaluates a built-in FabricOps boolean expression and fails rows where the expression is false. This rule type is user-facing as Custom expression, but the actual rule type remains `expression_true`.

## When to use it

Use only when no smaller built-in FabricOps rule can express the requirement. Prefer explicit rules for readability and safer review.

## Rule applies to

**Data applicability:** Any profiled row set where the required check is best expressed as a built-in Spark SQL boolean expression over available columns, after simpler named rules have been ruled out.

**Example column(s) on this page:** expression references `credits_attempted` and `credits_earned`

## Parameters

```yaml
rule_type: expression_true
expression: "credits_attempted >= credits_earned"
severity: error
```

## Example rule definition

```yaml
rule_id: expression_true_example
rule_type: expression_true
expression: "credits_attempted >= credits_earned"
severity: error
description: "Example approved metadata rule for expression_true."
```

Governance Review stores the same rule type and parameters in `METADATA_GUARDRAIL_RULES`, including `rule_parameters_json`.

## Sample input data

| student_id | credits_attempted | credits_earned |
| --- | --- | --- |
| S001 | 20 | 18 |
| S002 | 16 | 16 |
| S003 | 12 | 15 |
| S004 | 10 | 11 |

## Rows that pass

| student_id | credits_attempted | credits_earned | Why |
| --- | --- | --- | --- |
| S001 | 20 | 18 | Expression is true. |
| S002 | 16 | 16 | Expression is true. |

## Rows that fail

| student_id | credits_attempted | credits_earned | Why |
| --- | --- | --- | --- |
| S003 | 12 | 15 | Attempted credits are lower than earned credits. |
| S004 | 10 | 11 | Expression is false because attempted credits are lower than earned credits. |

## Notes

- This is not a custom Python plugin rule and does not add a `custom_expression` alias.
- Only trusted reviewers should approve expression rules because the expression is more flexible than named rule types.
- Actual enforcement depends on active approved rows with `guardrail_type="dq"` in `METADATA_GUARDRAIL_RULES`.

## Related rules

- [`value_when`](value-when.md)
- [`required_when`](required-when.md)
- [`regex_match`](regex-match.md)

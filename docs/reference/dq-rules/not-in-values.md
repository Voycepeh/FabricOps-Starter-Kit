# not_in_values

## What this rule does

Checks that populated values are not in a blocked list.

## When to use it

Use to catch placeholders, retired codes, test values, or values known to be unsafe.

## Rule applies to

**Data applicability:** Categorical, flag, status, code, or other profiled string-like columns where specific placeholder, retired, test, or blocked values must not appear.

**Example column(s) on this page:** `country_code`

## Parameters

```yaml
rule_type: not_in_values
columns: ["country_code"]
blocked_values: ["UNKNOWN", "N/A", "TEST"]
severity: warning
```

## Example rule definition

```yaml
rule_id: not_in_values_example
rule_type: not_in_values
columns: ["country_code"]
blocked_values: ["UNKNOWN", "N/A", "TEST"]
severity: warning
description: "Example approved metadata rule for not_in_values."
```

Governance Review stores the same rule type and parameters in `METADATA_GUARDRAIL_RULES`, including `rule_parameters_json`.

## Sample input data

| customer_id | country_code |
| --- | --- |
| C001 | SG |
| C002 | UNKNOWN |
| C003 | MY |
| C004 | TEST |

## Rows that pass

| customer_id | country_code | Why |
| --- | --- | --- |
| C001 | SG | Not blocked. |
| C003 | MY | Not blocked. |

## Rows that fail

| customer_id | country_code | Why |
| --- | --- | --- |
| C002 | UNKNOWN | Blocked placeholder. |
| C004 | TEST | Blocked test value. |

## Notes

- Null values do not fail this rule by themselves.
- Use `accepted_values` when every valid value can be enumerated.

## Related rules

- [`accepted_values`](accepted-values.md)
- [`non_empty_string`](non-empty-string.md)

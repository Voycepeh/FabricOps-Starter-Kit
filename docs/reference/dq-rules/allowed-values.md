# allowed_values

## What this rule does

Checks that populated values belong to an approved list.

## When to use it

Use for controlled domains such as status, category, currency, country group, or yes/no flags.

## Rule applies to

**Data applicability:** Categorical, flag, status, code, or other profiled string-like columns where the data catalogue shows a small governed domain of valid values.

**Example column(s) on this page:** `status`

## Parameters

```yaml
rule_type: allowed_values
columns: ["status"]
allowed_values: ["new", "active", "inactive", "closed"]
severity: warning
```

## Example rule definition

```yaml
rule_id: allowed_values_example
rule_type: allowed_values
columns: ["status"]
allowed_values: ["new", "active", "inactive", "closed"]
severity: warning
description: "Example approved metadata rule for allowed_values."
```

Governance Review stores the same rule type and parameters in `METADATA_GUARDRAIL`, including `rule_parameters_json`.

## Sample input data

| customer_id | status |
| --- | --- |
| C001 | new |
| C002 | active |
| C003 | inactive |
| C004 | pending |

## Rows that pass

| customer_id | status | Why |
| --- | --- | --- |
| C001 | new | Allowed value. |
| C002 | active | Allowed value. |
| C003 | inactive | Allowed value. |

## Rows that fail

| customer_id | status | Why |
| --- | --- | --- |
| C004 | pending | Not in the allowed value list. |

## Notes

- Null values do not fail this rule by themselves. Use `missing_values` with `maximum_null_percent=0` if the value is mandatory.
- Keep allowed lists small and governed.

## Related rules

- [`blocked_values`](blocked-values.md)
- [`conditional_value`](conditional-value.md)
- [`missing_values`](missing-values.md)

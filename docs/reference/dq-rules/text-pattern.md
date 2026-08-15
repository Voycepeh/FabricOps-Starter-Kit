# text_pattern

## What this rule does

Checks that populated string values match a configured regular expression.

## When to use it

Use for emails, fixed-format codes, identifiers, postcodes, and other structured strings.

## Rule applies to

**Data applicability:** Profiled string or string-castable columns with a known textual pattern, such as emails, codes, identifiers, or formatted reference numbers.

**Example column(s) on this page:** `email`

## Parameters

```yaml
rule_type: text_pattern
columns: ["email"]
pattern: "^[^@]+@[^@]+\\.[^@]+$"
severity: warning
```

## Example rule definition

```yaml
rule_id: text_pattern_example
rule_type: text_pattern
columns: ["email"]
pattern: "^[^@]+@[^@]+\.[^@]+$"
severity: warning
description: "Example approved metadata rule for text_pattern."
```

Governance Review stores the same rule type and parameters in `METADATA_GUARDRAIL`, including `rule_parameters_json`.

## Sample input data

| staff_id | email |
| --- | --- |
| S001 | amy@nus.edu.sg |
| S002 | ben.lee@company.com |
| S003 | charlie.company.com |
| S004 | diana@ |

## Rows that pass

| staff_id | email | Why |
| --- | --- | --- |
| S001 | amy@nus.edu.sg | Matches pattern. |
| S002 | ben.lee@company.com | Matches pattern. |

## Rows that fail

| staff_id | email | Why |
| --- | --- | --- |
| S003 | charlie.company.com | Missing `@`. |
| S004 | diana@ | Missing domain after `@`. |

## Notes

- Null values do not fail this rule by themselves. Use `missing_values` with `maximum_null_percent=0` if the value is mandatory.
- Keep patterns understandable for reviewers.

## Related rules

- [`allowed_values`](allowed-values.md)
- [`blank_text`](blank-text.md)
- [`required_when`](required-when.md)

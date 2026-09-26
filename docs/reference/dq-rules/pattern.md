# pattern

## What this rule does

Checks populated text against a regular expression.

## When to use it

Use for emails, codes, identifiers, postcodes, and other structured text.

## Data applicability

Single text or string-castable columns with a known textual format.

## Parameters

```yaml
rule_type: pattern
columns: ["email"]
pattern: "^[^@]+@[^@]+\\.[^@]+$"
```

## Example rule definition

```json
{"rule_type":"pattern","columns":["email"],"pattern":"^[^@]+@[^@]+\\.[^@]+$"}
```

## Sample input data

| staff_id | email |
|---|---|
| S001 | amy@nus.edu.sg |
| S002 | ben.lee@company.com |
| S003 | charlie.company.com |
| S004 | diana@ |

## Rows that pass

| staff_id | email | Why |
|---|---|---|
| S001 | amy@nus.edu.sg | Matches the pattern. |
| S002 | ben.lee@company.com | Matches the pattern. |

## Rows that fail

| staff_id | email | Why |
|---|---|---|
| S003 | charlie.company.com | Missing `@`. |
| S004 | diana@ | Missing domain after `@`. |

## Notes

- Pattern checks format, not whether the value is required.
- Combine with `completeness` when the column must also be populated.
- Sample strings may guide a regex suggestion but do not define the full allowed domain.

## Related rules

- [`completeness`](completeness.md)
- [`value_set`](value-set.md)

# Data Quality rules

FabricOps supports **9 Data Quality rule types**. The Data Contract UI intentionally presents these in Governance-friendly terms rather than exposing every runtime rule name directly.

## UI to DQ rule mapping

| Data Contract UI | What Governance authors | FabricOps rule type |
|---|---|---|
| Columns → Column data quality → **Completeness** | Missing-value threshold and blank handling | [`completeness`](completeness.md) |
| Columns → Column data quality → **Uniqueness** | Minimum unique percentage | [`uniqueness`](uniqueness.md) |
| Columns → Column data quality → **Value Lists → Whitelist** | Values that are permitted | [`value_set`](value-set.md) with `mode: allow` |
| Columns → Column data quality → **Value Lists → Blacklist** | Values that are rejected | [`value_set`](value-set.md) with `mode: block` |
| Columns → Column data quality → **Value Rules** | Lower/upper bounds and inclusivity | [`range`](range.md) |
| DQ Rules → **Business Rules** | Text-format requirement | [`pattern`](pattern.md) when resolved as a format rule |
| DQ Rules → **Business Rules** | Direct relationship between two columns | [`column_relationship`](column-relationship.md) |
| DQ Rules → **Business Rules** | A field is required only under a condition | [`conditional_completeness`](conditional-completeness.md) |
| DQ Rules → **Business Rules** | A whitelist or blacklist applies only under a condition | [`conditional_values`](conditional-values.md) |
| DQ Rules → **Business Rules** | Requirement that cannot be represented by a structured rule | [`custom_expression`](custom-expression.md) fallback |

Whitelist and Blacklist are separate Governance controls but share the same underlying `value_set` rule type. If both are configured, they are persisted as independent rules.

Business Rules are resolved into the smallest structured DQ rule or rules that preserve the requirement. `custom_expression` is reserved for requirements that cannot be represented without changing their meaning.

## Rule reference

| Rule | When to use it | Required parameters | Example |
|---|---|---|---|
| [`completeness`](completeness.md) | A column must be populated, or may be missing only up to an accepted threshold. | `columns`, `maximum_missing_percent`, `treat_blank_as_missing` | Customer ID must always exist. |
| [`uniqueness`](uniqueness.md) | One column or a combination of columns must uniquely identify rows. | `columns` | Order ID + line number must be unique. |
| [`value_set`](value-set.md) | A column must contain only approved values, or must not contain blocked values. | `columns`, `mode`, `values` | Status must be Open or Closed. |
| [`range`](range.md) | A numeric or date value must stay within governed bounds. | `columns`, minimum and/or maximum bounds | Amount must be between 0 and 100. |
| [`pattern`](pattern.md) | Populated text must follow a known format. | `columns`, `pattern` | Email must match the approved format. |
| [`column_relationship`](column-relationship.md) | Two columns must compare directly on the same row. | `columns`, `operator` | End date must be on or after start date. |
| [`conditional_completeness`](conditional-completeness.md) | A target column is required only when another column matches a condition. | `columns`, condition parameters, `treat_blank_as_missing` | Approved records require an approved date. |
| [`conditional_values`](conditional-values.md) | A target value set applies only when another column matches a condition. | `columns`, condition parameters, `mode`, `values` | SG records must use SGD. |
| [`custom_expression`](custom-expression.md) | No structured rule above can represent the requirement without changing its meaning. | `expression_language`, `expression` | Total amount must equal quantity × unit price after discount. |

Use the smallest structured rule that expresses the requirement. Reserve `custom_expression` for cases that cannot be represented by the named rule types.

Profile statistics and observed frequency values are evidence only. They do not become contract requirements unless Governance explicitly authors them as rules.

!!! note "Freshness is a dedicated guardrail"
    Configure Freshness separately at table level; it is not part of the Data Quality vocabulary.

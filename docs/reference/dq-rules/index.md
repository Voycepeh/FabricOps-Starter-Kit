# Data Quality rules

FabricOps supports **9 lightweight DQ rule types** in `METADATA_GUARDRAIL`. Prefer the smallest structured rule that preserves the governance requirement. Use `custom_expression` only when none of the structured patterns can represent the requirement without changing its meaning.

## Choose the right rule

| Requirement | Use | Example |
|---|---|---|
| A column must be populated, or may be missing only up to a threshold | [`completeness`](completeness.md) | Customer ID must always exist |
| One column or a combination of columns must uniquely identify rows | [`uniqueness`](uniqueness.md) | Order ID + line number must be unique |
| A column must be inside or outside an explicit governed set | [`value_set`](value-set.md) | Status must be Open or Closed |
| A numeric or date value must stay within bounds | [`range`](range.md) | Amount must be between 0 and 100 |
| Text must follow a format | [`pattern`](pattern.md) | Email must match the approved format |
| Two columns must compare directly on the same row | [`column_relationship`](column-relationship.md) | End date must be on or after start date |
| A target column is required only when another column matches a condition | [`conditional_completeness`](conditional-completeness.md) | Closed records require a closed date |
| A target value set applies only when another column matches a condition | [`conditional_values`](conditional-values.md) | SG records must use SGD |
| No structured rule above can preserve the requirement | [`custom_expression`](custom-expression.md) | Total amount must equal quantity × unit price after discount |

## Selection principles

Profile statistics and frequency values are **evidence**, not contract requirements. Observing values such as `1/apple` and `2/pear` does not mean those are the only permitted mappings unless Governance explicitly says so.

Prefer a structured rule whenever one fits. Structured rules are easier to review, edit, explain, test, and enforce consistently. `custom_expression` is an escape hatch, not the default for multi-column requirements.

## Architecture boundary

| Boundary | Rule types | Ownership |
|---|---|---|
| Column DQ | `completeness`, `value_set`, `range`, `pattern` | Structured, deterministic, manually editable, and safe for conservative AI suggestion. |
| Grain & Row Key | `uniqueness` | Table-level uniqueness derived from the selected single or composite row key. |
| Table relationship DQ | `column_relationship` | Explicit row-level comparison between two columns. |
| Conditional Business Rules | `conditional_completeness`, `conditional_values` | Structured conditional rules resolved before custom logic. |
| Business Rules escape hatch | `custom_expression` | Constrained PySpark boolean logic requiring Engineering review before freeze. |

AI suggestions are transient and must be reviewed before they become part of a contract.

!!! note "Freshness is a dedicated guardrail"
    Configure Freshness separately at table level; it is not part of the Data Quality vocabulary.

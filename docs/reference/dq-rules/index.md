# Data Quality rules

FabricOps supports **7 lightweight DQ rule types** in `METADATA_GUARDRAIL`: five standard families plus two explicitly authored table-level families.

## Architecture boundary

| Boundary | Rule types | Ownership |
|---|---|---|
| Standard DQ | [`completeness`](completeness.md), [`uniqueness`](uniqueness.md), [`value_set`](value-set.md), [`range`](range.md), [`pattern`](pattern.md) | Structured, deterministic, manually editable, and safe for conservative AI suggestion. |
| Table relationship DQ | [`column_relationship`](column-relationship.md) | Human-authored, structured cross-column row validation; FabricOps does not infer business relationships. |
| Custom Advanced DQ | [`custom_expression`](custom-expression.md) | Project-authored constrained PySpark boolean `Column` logic; FabricOps validates, executes, records, and applies Warn/Block. |
| Transform | Project code | Persisted derived business or validation columns. FabricOps never automatically persists an `is_valid_*` column. |

AI suggestions are transient. They use governed Catalogue, Enrichment, Data Profiled, and Data Profiled Frequency evidence, never save/freeze/activate/enforce, and never suggest relationship or custom rules.

Custom expressions are not arbitrary Python: the runtime compiles a deliberately constrained, side-effect-free PySpark `Column` grammar without `eval()` or Python UDFs.

!!! note "Freshness is a dedicated guardrail"
    Configure Freshness separately at table level; it is not part of the Data Quality vocabulary.

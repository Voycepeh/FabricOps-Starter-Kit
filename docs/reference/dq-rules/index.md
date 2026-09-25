# Data Quality rules

FabricOps supports **7 lightweight DQ rule types** in `METADATA_GUARDRAIL`: four column-level standard families, one table-level row-key uniqueness rule, and two explicitly authored Advanced families.

## Architecture boundary

| Boundary | Rule types | Ownership |
|---|---|---|
| Column DQ | [`completeness`](completeness.md), [`value_set`](value-set.md), [`range`](range.md), [`pattern`](pattern.md) | Structured, deterministic, manually editable, and safe for conservative AI suggestion. |
| Grain & Row Key | [`uniqueness`](uniqueness.md) | Table-level uniqueness derived from the selected single or composite row key. Profile evidence can suggest candidates; pipeline validation proves the configured key against table data. |
| Table relationship DQ | [`column_relationship`](column-relationship.md) | Human-authored, structured cross-column row validation; FabricOps does not infer business relationships. |
| Business Rules escape hatch | [`custom_expression`](custom-expression.md) | Natural-language Business Rules that do not resolve to a known FabricOps pattern use constrained PySpark boolean `Column` logic and require Engineering review before freeze. |
| Transform | Project code | Persisted derived business or validation columns. FabricOps never automatically persists an `is_valid_*` column. |

AI suggestions are transient. Column DQ suggestions use governed Catalogue, Enrichment, Data Profiled, and Data Profiled Frequency evidence and never save, freeze, activate, or enforce. Grain & Row Key suggestions may use profile distinctness to identify strong single-column candidates, but per-column statistics alone do not prove a composite key.

Custom expressions are not arbitrary Python: the runtime compiles a deliberately constrained, side-effect-free PySpark `Column` grammar without `eval()` or Python UDFs.

!!! note "Freshness is a dedicated guardrail"
    Configure Freshness separately at table level; it is not part of the Data Quality vocabulary.

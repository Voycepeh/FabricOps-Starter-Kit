# Table-scoped governance review

`04_gov_dataset_table` is the v1.0.0 governance review workflow. It selects a logical table directly from `METADATA_DATA_CATALOGUE`, loads the latest successful profile run, and lets a human approve append-only governance metadata.

```text
METADATA_DATA_CATALOGUE
    |
    +--> METADATA_DATA_LINEAGE_TABLE
    |
    +--> METADATA_COLUMN_CONTEXT
    |
    +--> METADATA_DQ_RULES
    |
    +--> METADATA_COLUMN_CLASSIFICATION
```

## Implemented in v1.0.0

- A single data catalogue table stores table context and column profile evidence.
- `03_pc` writes profile evidence to `METADATA_DATA_CATALOGUE` and table lineage to `METADATA_DATA_LINEAGE_TABLE`.
- `04_gov` approves column business context into `METADATA_COLUMN_CONTEXT`.
- `04_gov` approves DQ-rule metadata into `METADATA_DQ_RULES` without executing the rules.
- `04_gov` approves sensitivity and PII decisions into `METADATA_COLUMN_CLASSIFICATION`.
- Fabric AI suggestions are optional, editable, and advisory. No AI suggestion is written unless a human runs an explicit commit action.

## Planned

- Table access metadata.
- AI-assisted column lineage.
- `03_pc` enforcement of approved DQ rules and classification metadata.

## Removed from the v1.0.0 architecture

- Separate physical table-level and column-level catalogue tables.
- Profile rows stored outside the canonical catalogue.
- A separate data-contract metadata table.
- Mandatory Data Agreement relationship for `04_gov`.

## Enforcement boundary

For v1.0.0, schema and drift guardrails remain defined in each `03_pc` notebook. Governance metadata is authored and approved by `04_gov`; production enforcement is a later enhancement.

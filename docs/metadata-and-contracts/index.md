# Metadata and contracts appendix

The main [FabricOps Starter Kit Operating Model](../fabricops-operating-model.md) explains how shared metadata connects governance, exploration, engineering, enforcement, and handover.

Keep the metadata model lightweight. At minimum, think in terms of:

- `data_stewards`
- `data_agreements`
- `notebook_registry`
- `data_profiles`
- `data_lineage`
- `data_quality_rules`
- `sensitivity_classification`
- `business_context`
- `handover_manifest`

Metadata belongs in the governance workspace `metadata_lakehouse`. Reads and writes must use the metadata target configured by `00_env_config`, rather than an attached or default lakehouse.

Use these deeper appendices only when you need implementation detail:

- [Metadata architecture](metadata-architecture.md)
- [Assembled metadata views](metadata-columns.md)
- [Data quality rules](../data-quality-rules-system.md)

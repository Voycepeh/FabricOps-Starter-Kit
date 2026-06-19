# List of Metadata Tables

These pages are generated from the implemented metadata setup schema registry used by `00_env_config`.

| Metadata table | Purpose | Primary template step |
| --- | --- | --- |
| [`METADATA_DATA_ACCESS`](metadata-data-access.md) | Public-safe access context used by governance and metadata review workflows. | 03_governance.ipynb |
| [`METADATA_DATA_AGREEMENT`](metadata-data-agreement.md) | Agreement records that describe approved use, steward, recipient, and lifecycle context. | 01_agreement.ipynb, 02_pipeline.ipynb |
| [`METADATA_DATA_AGREEMENT_EVIDENCE`](metadata-data-agreement-evidence.md) | Supporting agreement files and evidence metadata captured during agreement intake. | 01_agreement.ipynb |
| [`METADATA_DATA_CATALOGUE`](metadata-data-catalogue.md) | Observed table and column profile evidence. This is runtime evidence, not approved guardrail intent. | 02_pipeline.ipynb, 03_governance.ipynb, 99_explore.ipynb |
| [`METADATA_DATA_LINEAGE_TABLE`](metadata-data-lineage-table.md) | Source-to-target lineage evidence written by pipeline runs. | 02_pipeline.ipynb |
| [`METADATA_DATA_STEWARD`](metadata-data-steward.md) | Active and historical data steward records used by agreement intake. | 01_agreement.ipynb |
| [`METADATA_ENRICHMENT_RULES`](metadata-enrichment-rules.md) | Append-only enrichment and business metadata intent authored and reviewed through governance workflows. | 02_pipeline.ipynb, 03_governance.ipynb |
| [`METADATA_GUARDRAIL_RESULTS`](metadata-guardrail-results.md) | Runtime guardrail outcomes written by pipeline enforcement. | 02_pipeline.ipynb |
| [`METADATA_GUARDRAIL_RULES`](metadata-guardrail-rules.md) | Approved or pending schema, freshness, profile behavior, and DQ guardrail intent. | 02_pipeline.ipynb, 03_governance.ipynb |
| [`METADATA_NOTEBOOK_REGISTRY`](metadata-notebook-registry.md) | Active notebook registration records linking notebooks to agreement, environment, dataset, and pipeline context. | 02_pipeline.ipynb |
| [`METADATA_PIPELINE_RUNS`](metadata-pipeline-runs.md) | Pipeline run summary evidence for execution, guardrail, lineage, and catalogue status. | 02_pipeline.ipynb |

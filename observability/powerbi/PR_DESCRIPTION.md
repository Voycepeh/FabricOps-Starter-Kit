# FabricOps Observability v1 PBIP

## Implemented functionality

- Functional PBIP with TMDL semantic model, enhanced PBIR report definitions, DAX measures, explicit relationships, theme, three visible pages, and two hidden native drillthrough pages.
- Configurable SQL endpoint, database, metadata schemas, workspace scope, and 180-day default history window.
- Explicit source projection and selective JSON extraction; no `SELECT *`, reporting views, persisted tables, or pipeline/metadata-writer changes.
- Actionable operational states, trends, duration baseline/deviation, Contract coverage, current Guardrail failures, Steward-centric Agreement exploration, current profiling, and per-run diagnostics.

## Preview

See `observability/powerbi/assets/report-preview.svg`. It is a labelled static design preview, not a production-data screenshot.

## Verified repository metadata mappings

Mappings are documented in `SOURCE_PROJECTION_MATRIX.md` and automatically compared with `metadata_schemas.py`. Workspace/Table, workspace/Pipeline, Contract/version, and Agreement/version composite identities are retained. Steward relationships use provider/recipient participation and do not assert ownership.

## Design assumptions

- Import through the Fabric SQL analytics endpoint is used because v1 requires selective JSON parsing and portable PBIP configuration.
- Latest Activation revision represents the current physical Contract selection; latest per-column profile represents current profiling.
- Pipeline status values follow the canonical runtime values; stage records do not have durations, and failures do not include messages or stack traces.

## Known gaps and Desktop validation status

Power BI Desktop and a live Fabric endpoint were unavailable in the implementation environment. Structural and repository-contract validation passed, but Desktop open/save, DAX/TMDL compilation, live refresh, interaction UI, rendered overflow, native Back rendering, and capacity performance remain manual checks listed in `VALIDATION.md`.

## Manual setup

Open the PBIP, set `MetadataServer`, `MetadataDatabase`, schema, workspace, and history parameters, sign in, apply, and refresh. Validate first against a non-production metadata target.

## Explicitly excluded from v1

RLS, data-access scanning, automated remediation, writeback, new pipeline/reporting infrastructure, persisted reporting tables/views, full frequency distributions, synthetic runtime details, and links for item kinds without a verified Fabric URL pattern.


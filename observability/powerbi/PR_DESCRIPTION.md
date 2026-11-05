# FabricOps Observability v1 PBIP

## Implemented functionality

- Functional PBIP with TMDL semantic model, enhanced PBIR report definitions, DAX measures, explicit relationships, theme, four visible pages, and two hidden native drillthrough pages.
- Configurable SQL endpoint, database, metadata schemas, workspace scope, and 180-day default history window.
- Explicit source projection and selective JSON extraction; no `SELECT *`, reporting views, persisted tables, or pipeline/metadata-writer changes.
- Descriptive pipeline activity and outcomes, activation decisions and submitted Dry Run evidence, duration versus historical median, all-table Governance exploration, Steward-filtered Data Owner tables, latest profiling/access observations, and per-run diagnostics.
- Current unified read/write execution metrics from `METADATA_PIPELINE_RUN.operations[].metrics`, with `measurement_source` retained and released top-level row counts used only as fallbacks for older Run records.

## Preview

See `observability/powerbi/assets/report-preview.svg`, `all-pages-preview.svg`, and `semantic-model-preview.svg`. They are labelled static previews with illustrative values, not production-data screenshots or evidence of Desktop rendering.

## Verified repository metadata mappings

Mappings are documented in `SOURCE_PROJECTION_MATRIX.md` and automatically compared with `metadata_schemas.py`. The validator also checks canonical Governance/Engineering schema routing and typed nested execution-metric paths. Workspace/Table, workspace/Pipeline, Contract/version, and Agreement/version composite identities are retained. Steward relationships use provider/recipient participation and do not assert ownership.

## Design assumptions

- Import through the Fabric SQL analytics endpoint is used because v1 requires selective JSON parsing and portable PBIP configuration.
- Latest Activation revision represents the current physical Contract selection; latest per-column profile represents current profiling.
- Pipeline status values follow the canonical runtime values; stage records do not have durations, and failures do not include messages or stack traces.
- Ordinary Dry Run is session-only. Accepted activation submissions retain required Dry Run evidence in `METADATA_PIPELINE_ACTIVATION`; its summary is shown separately and is never counted as a persisted `METADATA_PIPELINE_RUN` execution.
- Access visuals report existing `METADATA_DATA_ACCESS` observations and do not scan or calculate effective access.

## Known gaps and Desktop validation status

Power BI Desktop and a live Fabric endpoint were unavailable in the implementation environment. Structural and repository-contract validation passed, but Desktop open/save, DAX/TMDL compilation, live refresh, interaction UI, rendered overflow, native Back rendering, and capacity performance remain manual checks listed in `VALIDATION.md`.

Offline evidence: the PBIP validator passes across 194 generated paths, all four project entry files pass Microsoft’s published JSON schemas, deterministic regeneration and Ruff pass, and the expanded metadata/Pipeline execution suites pass 130 tests.

## Manual setup

Open the PBIP, set `MetadataServer`, `MetadataDatabase`, schema, workspace, and history parameters, sign in, apply, and refresh. Validate first against a non-production metadata target.

## Explicitly excluded from v1

RLS, data-access scanning, automated remediation, writeback, new pipeline/reporting infrastructure, persisted reporting tables/views, full frequency distributions, synthetic runtime details, and links for item kinds without a verified Fabric URL pattern.


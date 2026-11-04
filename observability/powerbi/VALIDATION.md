# Validation evidence

Run on the repository branch with:

```bash
python observability/powerbi/tools/build_pbip.py
python observability/powerbi/tools/validate_pbip.py
uv run pytest -q tests/unit/test_pipeline_handoff.py tests/unit/test_metadata_schemas.py
```

The PBIP validator passes across 193 generated paths. The two repository suites pass with 61 tests. The automated checks cover PBIP/PBIR references, JSON parseability, six-page visibility, native drillthrough bindings, explicit all-pair `DataFilter` interactions, semantic field references, relationship endpoints, source table/column mappings against `metadata_schemas.py`, absence of `SELECT *`, bounded history predicates, selective JSON paths, absence of unused loaded model columns, required DAX measures, activation package invariants, and representative mutually exclusive mock run outcomes.

Additional implementation-time checks:

- Microsoft `json-schemas`: report, page, and visual-container definitions are checked against their current official schemas.
- `pbiplint`: 0 errors. Remaining warnings are documented design choices: native SQL projection is reported as Power Query transformation; repository-native profile percentages are doubles; a separate Date table would add unused model surface in v1; and the measures-only table is intentionally calculated.

## Manually verified from repository source

- Metadata names and physical columns: `src/fabricops_kit/config/metadata_schemas.py`.
- Grains and supported relationships: `docs/reference/metadata.md` and generated per-table metadata pages.
- Pipeline operation/stage/failure JSON: canonical logical schema in `metadata_schemas.py` and pipeline-run tests.
- Steward participation: provider/recipient IDs on Agreement; participation is not table ownership.
- Agreement association: exact Agreement version is selected by `METADATA_DATA_CONTRACT_ACTIVATION` for a physical workspace/Table ID.
- Dry Run persistence: repository tests confirm ordinary Dry Run is session-only, while every accepted Pipeline Activation package requires a complete, boundary-complete `dry_run`. The report presents that submitted evidence and Governance decision status separately from persisted Run counts.
- Access wording: `METADATA_DATA_ACCESS` contains observed permissions; the report does not claim effective access or initiate scans.

## Not verified in this Linux environment

- Opening/saving the PBIP with Power BI Desktop.
- Live Fabric SQL authentication, refresh, and `OPENJSON` execution against a customer endpoint.
- Visual rendering, responsive text overflow, native Back button rendering, and Desktop's DAX/TMDL parser.
- Edit Interactions UI state after a Desktop round trip and live performance/capacity behavior.

These items must be checked in Power BI Desktop before release. The project does not claim full Desktop or Fabric validation. Use a non-production workspace first; sample assertions in the validator are synthetic and never presented as production data.

## Desktop acceptance checklist

1. Open the `.pbip` without migration or schema errors.
2. Configure the six parameters and refresh against a representative non-production Metadata Lakehouse/Warehouse.
3. Run **Validate formula** for all measures and confirm blank handling with zero runs, no Contract Activation, missing `completed_at`, and empty JSON arrays.
4. Confirm Overview, Engineering — Pipelines, Governance — Tables and Data Owner — Tables are visible and both detail pages are hidden.
5. Drill through a pipeline/run and a table; verify native Back and selection-specific activation decisions, submitted Dry Run evidence, operations, stages, failures, profiling, and activity.
6. In **Edit interactions**, inspect every data visual pair; selections must filter, never highlight, relevant targets.
7. Select a Steward and verify provider/recipient Agreement participation filters the Data Owner table subset without displaying an ownership claim.
8. Confirm Governance retains all registered physical tables, including rows without an active Contract or Agreement.
9. Confirm access visuals describe only the latest recorded snapshot and do not imply effective access.
10. Inspect 1280×720 layout at Fit to page and test long IDs, table names, reasons, and contacts for clipping.
11. Capture Performance Analyzer traces with the intended history window and record refresh/model size.
12. Reconcile one approved activation against its submission: verify Dry Run ID/status/boundary/operation count, and confirm it does not increase recorded Run Count.


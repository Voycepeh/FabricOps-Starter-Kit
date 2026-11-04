# Validation evidence

Run on the repository branch with:

```bash
python observability/powerbi/tools/build_pbip.py
python observability/powerbi/tools/validate_pbip.py
```

The automated validator checks PBIP/PBIR references, JSON parseability, five-page visibility, native drillthrough bindings, explicit all-pair `DataFilter` interactions, semantic field references, relationship endpoints, source table/column mappings against `metadata_schemas.py`, absence of `SELECT *`, bounded history predicates, selective JSON paths, required DAX measures, and representative mock-state classification.

Additional implementation-time checks:

- Microsoft `json-schemas`: report, page, and all 51 visual-container definitions passed their current official schemas.
- `pbiplint`: 0 errors across 80 model/report files. Remaining warnings are documented design choices: native SQL projection is reported as Power Query transformation; repository-native profile percentages are doubles; a separate Date table would add unused model surface in v1; and the measures-only table is intentionally calculated.

## Manually verified from repository source

- Metadata names and physical columns: `src/fabricops_kit/config/metadata_schemas.py`.
- Grains and supported relationships: `docs/reference/metadata.md` and generated per-table metadata pages.
- Pipeline operation/stage/failure JSON: canonical logical schema in `metadata_schemas.py` and pipeline-run tests.
- Steward participation: provider/recipient IDs on Agreement; participation is not table ownership.
- Agreement association: exact Agreement version is selected by `METADATA_DATA_CONTRACT_ACTIVATION` for a physical workspace/Table ID.

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
4. Confirm Overview/Maintainer/Data Owner are visible and both detail pages are hidden.
5. Drill through a pipeline/run and a table; verify native Back and selection-specific operations, stages, failures, profiling, and activity.
6. In **Edit interactions**, inspect every data visual pair; selections must filter, never highlight, relevant targets.
7. Select a Steward and verify provider/recipient Agreement participation flows to exact activations/tables without displaying an ownership claim.
8. Inspect 1280×720 layout at Fit to page and test long IDs, table names, reasons, and contacts for clipping.
9. Capture Performance Analyzer traces with the intended history window and record refresh/model size.


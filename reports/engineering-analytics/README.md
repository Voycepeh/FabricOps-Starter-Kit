# FabricOps Engineering Analytics

Open **FabricOps Engineering Analytics.pbip** in a current version of Power BI Desktop with PBIP, PBIR and TMDL support. The project contains a native Power BI report and an Import semantic model. The [analytical design](../../docs/maintainer/engineering-analytics-powerbi-plan.md) documents field projections, definitions and coverage.

## Connect the Metadata Lakehouse

1. In **Transform data → Manage parameters**, set `MetadataWorkspaceId` and `MetadataLakehouseId` to the workspace and item GUIDs of the Metadata Lakehouse configured in `00_env_config`.
2. Set `EngineeringMetadataSchema` to the configured physical schema, typically `engineering`. The model follows the Lakehouse connector's workspace → Lakehouse → schema → table navigation.
3. Optionally set `WorkspaceNames` to a JSON object mapping lowercase workspace IDs to friendly names. The model displays the ID suffix when a name is unavailable. Keep deployment values out of source control.
4. Authenticate using an organizational account with access to the four projected metadata tables and apply the model refresh. A repository checkout with both IDs blank returns empty metadata tables. Setting only one ID raises a configuration error.

The connector reads `METADATA_PIPELINE_RUN`, `METADATA_GUARDRAIL_RESULTS`, `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED`. It discards raw arrays after projecting the required fields. An invalid or truncated required array fails refresh with the affected Run ID and array name. Use the native Lakehouse route so the SQL analytics endpoint's documented string limit does not silently cut operational journals. The connection must pass the long-payload test below before deployment.

## Explore the report

Engineering Overview includes a date-independent latest status view. The historical Run filters start at 30 days. The date controls support 7, 30 and 90 days. Pipeline and Table Analytics use the selected execution workspace, logical pipeline and physical table. Choose a write strategy and one write metric to investigate volumes. For the SCD1 composition chart, select one operation series. The two elapsed time charts show individual Runs and individual operations in seconds.

On a row with a Run ID, use **Drill through → Run Detail** to inspect timestamps, status, operations, stage outcomes, aggregate Guardrail results, profiling and failure codes. Use the lineage page's own root selector to inspect known dependencies. The lineage page uses the latest complete successful Run per pipeline as its topology reference. The Run Detail exposure matrix shows downstream dependencies of recorded failed Run outputs.

## Acceptance before publishing

The checked-in project needs verification in Desktop and in the Fabric service using approved test metadata. Keep the model within the approved engineering audience. For workspace-isolated audiences, deploy separately or validate agreed row-level security before sharing.

1. Compare Spark and Power Query for a Run with an operations array over 8 KB and a Run with a profiling array over 8 KB. Match UTF-8 byte length, element counts, exact keys and final array entries. Refresh again after the same Run is finalized in Delta and confirm one Run row with the updated evidence.
2. Load representative 02A, 02B and 02C Runs. Confirm full same-day observation counts, separate Read and Write series, measured zero appends, distinct overwrite, SCD1 and SCD2 counts, and blanks for uncaptured metrics.
3. Verify current failure recovery across historical date filters, run drillthrough and stage isolation, guardrail row uniqueness, comparable duration changes, and profile scope and snapshot deduplication.
4. Verify native visual rendering and theme, all date presets and reset, synchronized slicers, dynamic write metrics, and drillthrough in Desktop. Verify unambiguous workspace labels, service credentials, refresh and closure size on the target history. Check for overlapping aliases or cross-workspace write bindings.
5. Verify a real or synthetic dependency cycle and converging paths. Confirm distinct downstream entities and maximum shortest-path depth.

Run the structural checks from the repository root with `python reports/engineering-analytics/tests/validate_project.py`. The validation uses `jsonschema` and retrieves Microsoft's public schema documents. It checks the declared layout, visual bindings, and DAX references. It does not execute DAX or Power Query. Historical stage durations, a standard Fabric Run deep link and confirmed downstream failure attribution lack the required recorded fields.

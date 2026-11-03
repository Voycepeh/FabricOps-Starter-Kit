# Pipeline Promotion: signed-in Fabric acceptance

**Status: not executed in Fabric.** The package keeps `FABRIC_GOVERNED_VALIDATED = False`; no widget, notebook parameter, caller-supplied identity or Registry row can enable Governed admission. Complete this checklist with actual tenant evidence before changing the release gate.

## Security and scope

Only the saved notebook is frozen; imported packages and referenced notebooks are not. Immutable archives and governance metadata need actual tenant permissions that exclude ordinary Engineering writes. A `Governed/` folder is organizational, not a permission boundary. Users with sufficient permissions can bypass FabricOps and execute Spark directly.

Saved-definition verification is subject to **TOCTOU**: fetching saved code before a managed operation cannot prove the identity of code already loaded in the kernel or prevent intervening edits. Do not advertise execution-time attestation. Keep admission blocked until the strongest supported managed-operation claim has been validated and these limits are accepted.

## Required tenant evidence

Record package commit/version, date, tester, disposable workspace names and outcomes. Do not put secrets, real item IDs or private URLs in public evidence.

| Check | Required result | Status |
| --- | --- | --- |
| Notebook Get Definition, ipynb format | Full saved notebook and parameter-cell metadata survive roundtrip; unsupported parts fail closed | Pending |
| Notebook Create Definition | Separate item in same and different workspaces; readback executable hash matches | Pending |
| Notebook Update Definition | Exact restoration preserves item identity and verifies saved executable content | Pending |
| Long-running APIs | 202 operation polling and `/result` retrieval work for Create/Get/Update | Pending |
| Workspace folder API | Same-workspace copy appears in Governed; folder alone grants no permission protection | Pending |
| OneLake Files | Write-once archive refuses overwrite; readback SHA matches; missing/corrupt archive blocks | Pending |
| Governance identity and permissions | Unprivileged Engineering identity cannot mutate activations, Registry or immutable archives | Pending |
| Destination configuration | Same/cross-workspace promotion uses destination configuration; intentional remote stores retain exact reviewed physical bindings | Pending |
| Contract scope | Same Table ID in two physical workspaces can select different frozen versions; missing/ambiguous source or target Contract blocks | Pending |
| Concurrent Delta promotion | Simultaneous first versions, stale expected versions, blind phantom inserts and lost acknowledgements preserve one active version | Pending |
| Writer coordination | Existing Serializable target claims exclude old/new writers and Contract Activation; crashed claims require reconciliation | Pending |
| Manual and scheduled starts | Both use identical admission; old notebook schedule fails after promotion; schedule-time edits alone are allowed | Pending |
| Runtime parameters | Injected behavior parameters, changed code/SQL and changed bindings block; Markdown-only edits are allowed | Pending |
| In-flight old version | Already admitted run finishes with captured version/Contracts; new starts use the new active notebook | Pending |
| Contract replacement | Next run adopts independently activated versions; current run retains captured exact payload SHA | Pending |
| Integrity repair | Changed copy saved before exact archived restore; readback reuses existing approval; different code requires new Dry Run/promotion | Pending |
| Partial staging | API/archive/clone failures leave previous authority active; staged artifacts identified by promotion ID and never treated as active | Pending |
| TOCTOU experiment | Manual Run versus API preflight timing and unsaved/running-cell edits documented without claiming prevention | Pending |
| Processing regression | `_row_hash`, append_all/new_only, overwrite, incremental, SCD1/2, profiling, lineage, observations, retries and receipts exercised in Fabric | Pending |

## Scheduling and rollback

Promotion never moves engineer-owned schedules. The new item ID is returned in the Registry row; engineers explicitly recreate/rebind schedules and confirm their intended active version. Starts against superseded physical notebook IDs must reject. Do not silently overwrite an old notebook while it may be executing.

Exact active-snapshot restoration uses `restore_pipeline`, preserving the changed copy under its promotion archive before Update Definition. Rollback to older logic requires copying the retained source notebook into development, manually Dry Running it, and reviewing a new monotonically increasing promotion; never mutate an old approval row. When the reviewed executable digest matches a retained prior version, the new promotion records its version in `restored_from_version`.

## Gate change

A gate change requires reviewed tenant results and tests for the actual verified behavior. Do not treat a unit-test monkeypatch, API response mock, green CI or a successful saved-code hash as proof of secured Governed execution.

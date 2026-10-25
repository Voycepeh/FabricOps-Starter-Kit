# Public API & Architecture

**Use this page to review the supported public API boundary, callable architecture, and generated call-flow artifacts.**

The [Release Guide](index.md) owns release procedure. This page owns architecture review details used during implementation cleanup and release validation.

## Supported public API boundary

`fabricops_kit.public_api.SUPPORTED_PUBLIC_API` is the canonical machine-readable boundary for notebook-facing supported public callables.

Maintainers should verify that:

1. release-facing functions are listed in `SUPPORTED_PUBLIC_API`
2. adding a function to Python source alone does not make it release-facing
3. notebook templates and public guidance import supported functions from the root package where appropriate
4. public exports are intentional in package `__init__.py` files and in `src/fabricops_kit/__init__.py` when the root API should expose them
5. generated references are review surfaces rather than the source of truth for the public boundary

!!! important "Public boundary rule"

    A callable is not part of the supported release boundary merely because it exists in source. The supported registry and intentional exports define what is public-facing.

## Public function architecture

**Keep public callable structure small and predictable.**

FabricOps uses this package pattern:

- one public owner file named after the function
- one package `shared.py` for reusable helpers and supporting objects
- one package `__init__.py` for exports
- root exports only for notebook-facing supported public API

Avoid catch-all files such as `public.py`, `models.py`, `classes.py`, adapter files, or resolver files unless explicitly approved.

### Architecture checks

Architecture review should confirm that changes do not introduce:

- public-to-public calls
- internal-to-public calls
- cross-file private helper dependencies
- private helpers surfaced as Public or Internal architecture layers

## Callable architecture contract

`docs/reference/_data/public-function-call-flows.json` is the committed callable architecture contract.

The v4 contract has three principal collections:

- `functions` contains one canonical identity, source, lifecycle, contract, usage, and documentation record per callable
- `relationships` contains one record per resolved direct caller-to-callee edge, with edge-specific evidence only
- `public_analysis` contains complexity metrics, refactor signals, and other analysis that exists only for a public entry point

Inbound callers, usage groups, unused-function rows, simple counts, and display labels are derived by consumers instead of being stored as duplicate records.

Use it to inspect:

- public callable scope and owner file
- direct and transitive callees
- helper reachability
- source locations
- architecture violations
- cleanup and refactor signals
- defined-but-not-used functions

!!! note "Source remains authoritative"

    If the JSON disagrees with source, fix the source inputs or generator and regenerate the contract. Do not hand-edit the JSON as the fix.

Run the call-flow generator when a source change affects callable structure, source locations, public exports, helper relationships, architecture classification, or public function flow metrics:

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
```

Commit the regenerated JSON only when the architecture contract is intentionally affected.

## Proposed activation execution requirements after PR #1693

**Proposal only: activation should require a committed, successful whole-pipeline run in the intended Fabric workspace.** This section records the follow-up to [PR #1693](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1693); it does not describe an implemented guarantee.

PR #1693 introduces permanent pipeline UUID registration. Its Test mode evaluates reads, transformations and Guardrails, simulates target publication, and returns an in-memory result from `finalize_pipeline()`. Governance supplies a Fabric run reference and attests verification before activation. The backend checks that supplied result but does not retrieve an authoritative Testing execution from `METADATA_PIPELINE_RUN` or verify Fabric run history. A successful Test therefore does not establish that target writes can complete in that workspace.

### Required activation boundary

The follow-up must make these requirements concrete before it is ready to merge:

1. `finalize_pipeline()` owns the successful whole-run commit to `METADATA_PIPELINE_RUN`. Individual operations, successful notebook cells, interpreter shutdown and caller-supplied result dictionaries cannot independently authorize activation.
2. A qualifying run identifies the permanent `pipeline_id`, registered Fabric workspace and notebook binding, execution activity, configured environment, physical source/target bindings, read/write modes, SQL hash and source associations. A run from another workspace, another environment or an earlier notebook binding cannot authorize the current candidate.
3. Every participating source and target `table_id` has its exact frozen `METADATA_DATA_CONTRACT` version and payload hash recorded. Missing contracts, changed contracts, missing operations or changed configuration require a new complete run.
4. Every required Read, transformation, applicable Guardrail, actual target Write and required post-write finalization completes. A simulated Write cannot qualify. Read-only pipelines may qualify when they have no declared target operations; incremental runs with no work must record their no-op outcome explicitly and must not imply that an unexercised publication path was verified.
5. Warning Guardrails may allow continuation and remain visible in the committed results and approval review. A blocking Guardrail stops the run and prevents activation. Read, transformation, Write, profiling, checkpoint or required metadata failures prevent a successful activation result, including when the business write already committed.
6. Activation review and approval both load the exact completed run and its rule-level `METADATA_GUARDRAIL_RESULTS` from configured metadata storage. A supplied run reference selects a committed record; an editable dictionary or human attestation cannot substitute for that record. Missing or duplicate run identities fail closed.
7. The successful run record is committed only after its required diagnostics and completion references are durable. Interrupted publication must leave no activatable success with missing dependencies. An uncertain commit acknowledgement requires exact durable read-back; retries must preserve run and diagnostic identities and must not replay business writes blindly.
8. `METADATA_PIPELINE_REGISTRY` continues to own atomic approval history, table mappings, writer ownership and execution reservations. Real validation writes must reserve their physical destinations and coordinate with Live executions and activation; this change must not create a route around existing ownership or concurrency controls.

These records establish what the selected run completed at that time. They do not guarantee that later Live runs will succeed after permissions, input data or infrastructure change.

### Write-mode decision

The implementation must explicitly choose whether Test performs real writes or a separate validation run performs them while Test remains read-only. This is a public behavior decision, not an internal persistence detail. Until it is resolved, keep this follow-up in draft. Do not silently turn existing Test calls into business writes or approve simulated publication as end-to-end verification.

Real validation writes require documented destination selection, execution reservations, failed-write recovery and treatment of already Live-owned targets. Approval itself must continue to write governance metadata only. Update the affected Preview API docstrings, notebook instructions, glossary and generated references with the chosen behavior; preserve frozen release snapshots.

### Acceptance checks

| Scenario | Required outcome |
| --- | --- |
| Complete run with all exact frozen contracts, exercised target Writes and durable finalization | Activation can review the committed run in the same workspace and environment. |
| Warning Guardrail with every other required operation successful | Run may qualify; warning remains visible in approval. |
| Blocking Guardrail, failed Read or transformation, failed Write or required post-write step | Pipeline stops or finalizes as failed; activation rejects it. Earlier business commits are reported for recovery. |
| One missing table contract, missing operation or unfinalized run | Activation rejects the candidate and identifies missing coverage. |
| Dry-run target publication or unevaluated required stage | Activation rejects the candidate as insufficient execution verification. |
| Fabricated result dictionary, unknown run ID or reviewer attestation without a committed run | Activation rejects it. |
| Correct environment name but different workspace, notebook binding, physical target or operation mode | Activation rejects it and requires a new run. |
| Diagnostics or final run commit fails; commit acknowledgement is lost | No unconfirmed success is accepted. Verify exact durable state before retrying. |
| Review becomes stale, affected Live execution is running, or destinations are reserved | Existing atomic approval and execution reservation checks continue to block conflicting actions. |

Use targeted unit tests for finalization and backend rejection, persisted Delta integration tests for commit ordering and retry behavior, and actual Microsoft Fabric execution for the workspace and publication claims. Local mocks and passing repository CI are not Fabric execution evidence. Record actual Fabric validation separately with version, date, tester, notebook and outcome; no such execution is claimed by this proposal.

## Review surfaces

| Surface | Purpose |
| --- | --- |
| [Function Reference](../reference/index.md) | Generated public callable catalogue from source metadata and docstrings. |
| [Call Graph Dashboard](../assets/public-function-call-flows-dashboard.html) | Interactive callable flow and architecture review. |
| [Function Call Graph](../function-call-graph.md) | Maintainer guide for the call-flow review workflow. |
| [Call-flow JSON contract](../reference/_data/public-function-call-flows.json) | Compact committed architecture contract for agent planning and review. |

## Regeneration commands

### Individual function references

Run before an actual release preparation or explicit generated-reference refresh:

```bash
PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py
```

### Dashboard

Run only when intentionally refreshing the published dashboard:

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_dashboard.py
```

!!! warning "Do not repair generated artifacts by hand"

    Do not manually edit generated function pages, dashboard HTML, or call-flow JSON as source of truth. Update source inputs or generator logic first, then regenerate the owned artifact.

# Public API compatibility snapshots

The Public Function Call Flows dashboard compares source-backed public API contracts across releases and the source tree used to generate the dashboard.

## Canonical inputs

- `src/fabricops_kit/public_api.py` is the lifecycle registry for Live, Preview, and Discontinued public callables.
- Each callable signature is parsed from Python source with `ast`; Fabric-dependent modules are never imported.
- Published versions come from semantic release tags and are read from each tag's own Git tree.
- The proposed release snapshot is read from the exact `origin/main` commit when available, otherwise the local `main` commit, and records its commit revision.
- The logical `working-tree` option is generated from the checked-out package source. It has no Git revision because the source may come from any branch or contain uncommitted changes; a deterministic SHA-256 source digest identifies its exact content.

The compatibility generator does not expect historical tags to contain a snapshot JSON file and never substitutes current source for a historical release.

## Generated contract

Run:

```bash
PYTHONPATH=src python scripts/generate_public_api_compatibility.py
```

This writes `docs/reference/_data/public-api-compatibility.json` using the versioned schema `fabricops_public_api_compatibility_v1`. The file contains:

- `metadata`: schema version and extraction rules
- `versions`: release tags, the exact `main` commit, and the separate working-tree snapshot
- `snapshots`: revision, extraction certainty, lifecycle source, and API records for every version
- `comparisons`: every ordered version pair with summary counts and classified changes

Each API record contains its registry-qualified name, lifecycle, extraction certainty, source identity, readable signature, ordered parameters, parameter kinds, required/default state, annotations, and return annotation. Registry identities resolve only to an exact source function or through a statically verified package `__init__.py` re-export. A same-named function elsewhere in the package is not accepted as identity evidence. Keys and records are sorted deterministically, and the contract has no generated timestamp.

Do not edit the JSON manually. Regenerate it after a package-source or generator change, then run the generator again and confirm that it produces no diff.

Normal generation refreshes the baseline from the current `origin/main` (or local `main`). To reproduce an existing snapshot, pass `--main-ref <recorded-commit-sha>`. Generated-artifact validation reads that SHA from the committed JSON and pins only the historical main baseline; it still regenerates the working-tree snapshot and all comparisons from current package source. This keeps PR and post-merge validation reproducible when `main` advances, while retaining stale-source detection. A validation run does not refresh the baseline or the dashboard HTML.

## Historical extraction and uncertainty

When a tag contains `src/fabricops_kit/public_api.py`, its literal lifecycle tuples are authoritative. A registry entry that cannot be resolved to exactly one top-level source function stays visible with an extraction error and makes the snapshot uncertain.

For a release that predates the lifecycle registry, the generator uses names from package `__all__` exports only when they resolve uniquely to a source function. Those records use lifecycle `Unknown`, the snapshot explains the fallback in `notes`, and every affected comparison requires review. Export discovery is evidence of public exposure, not evidence of a Live compatibility guarantee.

Missing, ambiguous, dynamic, or otherwise uncertain evidence is never classified as nonbreaking.

## Classification rules

The comparison reports added, removed, and modified APIs and uses three outcomes:

| Outcome | Examples |
| --- | --- |
| Potentially breaking | Live removal or demotion, parameter removal, required parameter addition, parameter-kind change, optional-to-required change, positional reordering, optional positional insertion before an existing positional parameter, or a new explicit parameter that can consume values previously bound by `*args` or `**kwargs` |
| Nonbreaking | New API, optional keyword-only or trailing positional parameter addition, required-to-optional change, Preview-to-Live promotion when no breaking signature change is present |
| Review required | Default or annotation change, Preview removal, unresolved source, Unknown lifecycle, or uncertain historical extraction |

The highest-risk finding wins for a modified callable. Static comparison cannot establish semantic behavior compatibility; targeted behavior tests and maintainer review remain required.

## Dashboard behavior

The dashboard loads the generated companion JSON beside the v4 call-flow contract. Both release questions compare the latest production release tag with the exact `main` commit. Selection uses `lifecycle_before`, so a released Live function stays in scope even if main demotes or removes it:

- **If I release main now, which Live/Public functions will break?** includes only removed or modified functions that were Live in production and classified potentially breaking. An empty result says “No breaking Live/Public function changes found.”
- **Will this release change functions users already use?** includes removed or modified functions that were Live or Preview in production. Display labels map `potentially_breaking` to **Breaking**, `nonbreaking` to **Compatible**, and `review_required` to **Needs review**.

These are selection and presentation changes; compatibility rules are unchanged. In particular, Preview removals still require review, default and annotation changes still require review, and Compatible describes the static contract comparison rather than proving behavioral equivalence. New functions, functions first exposed on main, Discontinued functions, and Unknown lifecycle records are excluded from both release summaries. Each function shows a brief reason and collapsed details with all findings and the exact released and main signatures. Counts belong to each question; there are no additional release totals or filters.

The separate historical mode compares release tags and retains its lifecycle filter and full change inventory. Returning to the release view always reloads production → main and clears historical URL parameters so a refresh preserves the release view. The working-tree snapshot remains available in the data contract for source inspection but is not presented as `main`. The compatibility artifact generation time is shown so maintainers can identify stale snapshots.

If the companion contract or a selected comparison is missing, the dashboard reports the missing generated data. It does not display an empty comparison as compatible.

## Validation

Run the focused checks:

```bash
PYTHONPATH=src python scripts/generate_public_api_compatibility.py
PYTHONPATH=src python scripts/generate_public_function_call_flows_dashboard.py
uv run pytest tests/unit/test_public_api_compatibility.py tests/unit/test_public_function_call_flows.py tests/unit/test_public_function_call_flows_browser.py
uv run ruff check scripts/generate_public_api_compatibility.py scripts/public_function_call_flows_dashboard_renderer.py tests/unit/test_public_api_compatibility.py
uv run mkdocs build --strict
```

Regenerate the compatibility JSON and dashboard a second time with generated timestamps preserved, then confirm the owned outputs have no diff.

# Function Call Graph

> **First make it exist. Then make it good.**
>
> AI helps FabricOps move quickly from idea to working public callable function:
>
> * create the function quickly
> * test whether the behaviour is useful
> * keep it if the behaviour is worth preserving
> * clean the architecture before the prototype becomes permanent
>
> The Function Call Graph is the maintainability checkpoint that helps us decide whether the implementation is clean enough to keep.

The Function Call Graph helps reviewers inspect public callable functions, understand review signals, and decide the next cleanup step before refactoring.

## Overview

The Function Call Graph is a v2 JSON contract boundary. The reference generator owns source scanning, architecture metadata, `function-call-graph.json`, and Markdown reference pages. The v2 dashboard/docs surfaces own rendering, review interactions, and cleanup/export workflows outside this script.

The source of truth is the repository code plus the generator, not the checked-in JSON snapshot.

## How it works

The Function Call Graph follows a simple v2 flow:

```text
Repository code → source scan → function-call-graph.json → v2 dashboard/docs consume JSON
```

![Function Call Graph setup](../assets/fabricops-call-graph-setup.png)

## Where the generated JSON lives

`function-call-graph.json` is a generated docs artifact.

During the docs deployment workflow, GitHub Actions runs:

```bash
PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py
```

This regenerates `docs/reference/_data/function-call-graph.json` inside the CI workspace before MkDocs builds the site. Mike then deploys the built documentation to `gh-pages`.

As a result, the deployed `gh-pages` documentation receives the fresh generated JSON for that build. The `main` branch is not automatically committed back with this regenerated JSON unless a maintainer intentionally runs the generator locally and commits the generated files.

For reviews, use:

- source code and `scripts/generate_individual_function_reference_pages.py` as the source of truth
- deployed `gh-pages` JSON as the current docs-build artifact
- checked-in JSON in `main` only as a snapshot, not as authoritative runtime state

## 1. Repository code

The repository is the source of truth.

FabricOps public callable functions, shared helpers, private functions, classes, and internal methods all live in the codebase. The Function Call Graph starts by scanning this code structure instead of relying on manually maintained documentation.

## 2. Source scan and generated data contract

The Function Call Graph data contract is generated from repository scans.

The source scanner is:

* [`scripts/generate_individual_function_reference_pages.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_individual_function_reference_pages.py)

The scanner reads the codebase and identifies:

* public callable functions
* supporting private functions
* shared helpers
* classes
* internal methods
* dependency edges between functions and modules

The scanner then writes the v2 callable architecture data contract:

* [function-call-graph.json](_data/function-call-graph.json)

This script also generates the individual Markdown API reference pages under `docs/api/reference/` so notebook authors and maintainers can review public callable behavior from source docstrings and metadata.

## 3. Enforce architecture

AI generated code can work correctly but still leave behind messy integration patterns:

* duplicated helpers
* private functions used across files
* wide dependency surfaces
* public callables depending on other public callables
* too many steps across thin wrapper functions

The question is not only whether the code works.

The question is whether the structure is still simple enough to keep.

The Function Call Graph is protected by an enforcement test that keeps the callable architecture intentional as the codebase changes.

The enforcement test makes sure public callables, shared helpers, and generated reference outputs do not drift silently.

The enforcement test is:

* [`tests/contract/test_callable_architecture_validation.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/tests/contract/test_callable_architecture_validation.py)

This helps prevent accidental architecture violations from becoming permanent.

### Data contract signals

The v2 JSON contract keeps deterministic architecture signals available for dashboard/docs rendering.

#### Public-flow signals

| Signal | Calculation | Reviewer action |
|---|---|---|
| Large width/depth | Width > 10 or Depth > 5 | Review whether the public callable has become too wide or too deeply nested. |
| Architecture violation | Any Type 1-6 architecture violation appears in the callable flow | Fix boundary violations before helper cleanup. |

#### Architecture violation types

| Type | Rule | Why it matters |
|---|---|---|
| Type 1 | Public function calls another public function directly | Public callables should own their workflow rather than chaining public entry points. |
| Type 2 | Shared function calls a public function directly | Shared helpers should not depend on public entry points. |
| Type 3 | Private function calls a public function directly | Private implementation details should not call public entry points. |
| Type 4 | Shared function calls a private function from another file | Shared helpers should not reach into another file’s private implementation. |
| Type 5 | Private function calls a private function from another file | Private helpers should stay file-local. |
| Type 6 | Private function calls a shared function directly | Private implementation details may need boundary review if they depend outward on shared helpers. |

#### Inventory suggestions

| Suggestion | Calculation | Reviewer action |
|---|---|---|
| Inline candidate | Called by exactly one parent, not used elsewhere, not recursive, not called multiple times by the same parent | Consider absorbing the helper into its caller. |
| Promote to shared | Private function called by more than one distinct caller | Consider moving it to a shared helper boundary. |

#### Metric definitions

| Metric | Definition |
|---|---|
| Width | Direct package-local calls from the selected public function. |
| Depth | Deepest nested call path. |
| Scope | Total downstream functions reached by the selected public function flow. |

The preferred public callable shape is still:

```text
public owner file → shared.py → internal implementation details
```

The pattern that usually needs review is:

```text
public callable → helper → helper → helper
```

Because these outputs are generated, update the scanner and architecture rules first, then regenerate the reference artifacts when intentionally refreshing this page.

## 4. v2 dashboard/docs ownership

The v2 dashboard/docs surfaces consume `docs/reference/_data/function-call-graph.json` and own visual rendering, review interactions, and cleanup/export workflows elsewhere.

The reference generator no longer produces the retired static dashboard HTML or embedded cleanup/export UI. Keep dashboard rendering and AI cleanup packet interactions in the v2 dashboard/app layer so this script remains focused on source scanning, JSON contract generation, and Markdown reference generation.

![Public Function Call Flows Dashboard](../assets/fabricops-call-graph-dashboard.png)

<!-- Legacy visual references retained for generated reference tests: ../assets/fabricops-call-graph-setup.png ../assets/fabricops-bad-example-large-surface-area.png ../assets/fabricops-bad-example-nested-functions.png ../assets/fabricops-call-graph-ai-refactor-package.png ../assets/fabricops-call-graph-ai-refactor-package%282%29.png -->

<div align="center" markdown>

[function-call-graph.json](_data/function-call-graph.json){ .md-button .md-button--primary }

</div>

The v2 dashboard/docs surfaces can use the JSON contract to help reviewers:

* see all public callable functions in one place
* understand what supports each public callable
* trace where dependencies go
* spot architecture violations and dependency chains that deserve a closer look
* manage cleanup and export interactions outside this generator

## 5. Markdown reference pages

This generator still writes individual Markdown API reference pages from source docstrings, package exports, metadata, and callable-flow analysis. Those pages remain the source-aligned reference surface for public callable behavior and implementation-helper context.

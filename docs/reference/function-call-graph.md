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
> The Function Call Graph is the v2 architecture review surface that helps us decide whether the public callable implementation is clean enough to keep.

The Function Call Graph helps reviewers inspect public callable flows, understand deterministic architecture signals, and plan focused cleanup PRs before prototype structure becomes permanent.

## Overview

The Function Call Graph has one maintainer-facing dashboard: the Public Function Call Flows Dashboard. That dashboard turns the v2 public function call flow payload into an interactive review surface for public callable cleanup.

## How it works

The Function Call Graph follows a simple flow:

```text
Repository Code → Static Analysis → Public Function Call Flow Payload → Dashboard Review → Focused Cleanup PRs
```

![Function Call Graph setup](../assets/fabricops-call-graph-setup.png)

## 1. Repository code

The repository is the source of truth.

FabricOps public callable functions, shared helpers, private functions, classes, and internal methods all live in the codebase. The Function Call Graph starts by analyzing this code structure instead of relying on manually maintained documentation.

## 2. Scan and analyze

The v2 Function Call Graph is generated from static repository analysis.

The v2 call flow generator is:

* [`scripts/generate_public_function_call_flows.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_public_function_call_flows.py)

The generator parses `src/fabricops_kit` and identifies:

* public functions exported from `src/fabricops_kit/__init__.py::__all__`
* defined top level functions
* package local function calls
* dependency edges between functions
* function types used for review
* deterministic architecture violation edges
* refactor signals such as large width/depth and architecture violations

The generator produces v2 review artifacts that make public callable flow architecture easier to inspect.

The generated review outputs are:

* [public-function-call-flows.json](_data/public-function-call-flows.json)
* [Public Function Call Flows Dashboard](../assets/public-function-call-flows-dashboard.html)

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

### What the dashboard signals

The dashboard uses deterministic rules from the v2 public function call flow payload.

#### Public-flow signals

| Signal | Color | Calculation | Reviewer action |
|---|---|---|---|
| Large width/depth | Yellow | Width > 10 or Depth > 5 | Review whether the public callable has become too wide or too deeply nested. |
| Architecture violation | Red | Any Type 1-6 architecture violation appears in the callable flow. | Fix boundary violations before helper cleanup. |

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

Generated dashboard and JSON outputs should normally be refreshed in a separate generator/reference refresh PR unless the PR is explicitly about refreshing generated outputs.

## 4. Public Function Call Flows Dashboard

The Public Function Call Flows Dashboard is the interactive review surface for the v2 call-flow data.

![Public Function Call Flows Dashboard](../assets/fabricops-call-graph-dashboard.png)

<div align="center" markdown>

[Open architecture dashboard](../assets/public-function-call-flows-dashboard.html){ .md-button .md-button--primary }

</div>

Reviewers use the dashboard to:

* choose a public callable scope
* inspect the dependency tree
* review architecture findings
* export a focused AI refactor packet when cleanup is needed

## 5. AI refactor packets

When a function is worth refactoring, the Public Function Call Flows Dashboard can export focused cleanup packets as JSON or YAML.

The Public Function Call Flows Dashboard exports one `fabricops_public_function_call_flow_refactor_packet_v2` built from selected callable flow data. The packet also carries the selected architecture scope, related public callable flow when applicable, architecture findings, and compatibility mode.

The packet keeps the AI refactor focused on:

* the selected function
* the supporting code assets
* the identified architecture risks
* the compatibility mode
* the relevant test expectations

![Function Call Graph AI refactor package](../assets/fabricops-call-graph-ai-refactor-package.png)

![Function Call Graph AI refactor package detail](../assets/fabricops-call-graph-ai-refactor-package%282%29.png)

The cleanup packet gives AI a focused review surface so it can improve the implementation without losing the original intent.

<!-- Test compatibility breadcrumbs: [Public Function Call Flows Dashboard](../assets/public-function-call-flows-dashboard.html) -->

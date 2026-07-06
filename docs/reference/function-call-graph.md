# Function Call Graph

> **First make it exist. Then make it good.**
>
> AI helps FabricOps move quickly from idea to a working public callable function. The Function Call Graph is the maintainability checkpoint that helps reviewers decide whether the implementation is clean enough to keep.

The workflow is simple: treat repository code as the source of truth, let the agent read the existing callable context, update the implementation, regenerate the call-flow JSON, then review the refreshed result in the dashboard.

<div align="center">
  <a class="md-button md-button--primary" href="../../assets/public-function-call-flows-dashboard.html">Open Public Function Call Flows Dashboard</a>
  <a class="md-button" href="../_data/public-function-call-flows.json">View JSON Contract</a>
</div>

![Function Call Graph workflow](../assets/fabricops-call-graph-setup.png)

## 1. Repository code is the source of truth

FabricOps functions and helpers live in the repository codebase:

* public callable functions
* shared helpers
* private helpers
* classes and internal methods

The call-flow contract is derived from this code. Do not treat the generated JSON or dashboard as a replacement for the implementation.

```text
src/
├── public function owner files
├── shared helpers
└── private implementation helpers
```

When generated output disagrees with the repository, fix the source scanner or generator rules rather than manually changing the JSON.

## 2. The agent reads the existing context

Before editing a public function or helper, the agent should read:

* `AGENTS.md`
* `docs/reference/_data/public-function-call-flows.json`

The JSON gives the agent the current review context, including:

* public callable scope
* helper reachability
* source locations
* width, depth, and total downstream scope
* architecture and cleanup signals

This lets the agent plan the change before touching the implementation.

## 3. Edit the function source

The agent updates the actual Python implementation, not the generated JSON.

Source changes may include:

* changing a public callable workflow
* extracting or combining helpers
* moving a helper to a shared boundary
* removing unnecessary wrapper layers
* correcting public, shared, or private classification

Keep the repository code authoritative. The generated contract should describe the implementation after the change.

## 4. Regenerate the call flow

After a function-level source change, run:

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
```

This refreshes:

```text
docs/reference/_data/public-function-call-flows.json
```

Commit the regenerated JSON when the change affects callable structure, source locations, public exports, helper relationships, architecture classification, or call-flow metrics.

Do not fix the JSON manually. Change the source or generator logic, then regenerate it.

## 5. Review the refreshed dashboard

The dashboard consumes the regenerated JSON and provides the main review surface.

Use it to:

* inspect the selected public function call tree
* review the callable inventory
* check width, depth, and total downstream scope
* identify architecture violations
* find inline or shared-helper candidates
* export a focused AI refactor packet

![Public Function Call Flows Dashboard](../assets/fabricops-call-graph-dashboard.png)

Selecting a public function should scope the call tree, inventory, signals, and export workflow around that callable.

## Review signals

The dashboard and JSON expose deterministic signals to guide cleanup. They support reviewer judgement; they are not a substitute for reviewing the implementation.

### Public-flow signals

| Signal | Calculation | Reviewer action |
|---|---|---|
| Large width or depth | Width > 10 or Depth > 5 | Review whether the public callable has become too wide or too deeply nested. |
| Architecture violation | Any Type 1 to Type 6 violation appears in the selected flow | Review the boundary shape before helper cleanup. |

### Architecture violation types

| Type | Rule | Why it matters |
|---|---|---|
| Type 1 | Public function calls another public function directly | Public callables should own their workflow instead of chaining public entry points. |
| Type 2 | Shared function calls a public function directly | Shared helpers should not depend on public entry points. |
| Type 3 | Private function calls a public function directly | Private implementation details should not call public entry points. |
| Type 4 | Shared function calls a private function from another file | Shared helpers should not reach into another file's private implementation. |
| Type 5 | Private function calls a private function from another file | Private helpers should remain file-local. |
| Type 6 | Private function calls a shared function directly | Review whether the private helper depends outward across the intended boundary. |

### Cleanup suggestions

| Suggestion | Calculation | Reviewer action |
|---|---|---|
| Inline candidate | Called by one parent, not recursive, not reused elsewhere, and not called repeatedly by the same parent | Consider absorbing the helper into its owner. |
| Promote to shared | Private function called by more than one distinct caller | Consider moving it to a shared helper boundary. |

## AI refactor packet

When a selected flow needs cleanup, use the dashboard export to create a focused packet rather than sending the whole repository.

![AI refactor packet export](../assets/fabricops-call-graph-ai-refactor-package.png)

A focused packet should contain enough context to plan a safe change while keeping the prompt specific to the selected public callable and its dependencies.

![AI refactor packet contents](../assets/fabricops-call-graph-ai-refactor-package%282%29.png)

## Generator ownership

The generated artifacts have separate owners:

| Script | Owns |
|---|---|
| `scripts/generate_public_function_call_flows_json.py` | `docs/reference/_data/public-function-call-flows.json` |
| `scripts/generate_public_function_call_flows_dashboard.py` | `docs/assets/public-function-call-flows-dashboard.html` |
| `scripts/generate_individual_function_reference_pages.py` | Individual pages under `docs/api/reference/` and the reference landing page at `docs/reference/index.md` |

`docs/reference/function-call-graph.md` is a standalone, manually maintained explanatory page. It must not be regenerated by the individual function reference generator.

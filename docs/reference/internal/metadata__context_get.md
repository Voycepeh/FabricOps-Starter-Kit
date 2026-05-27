# _context_get

## Internal helper
Internal helper. Do not call directly from notebooks unless extending FabricOps.

## Purpose
Supports callable orchestration internals.

## Used by callable functions
- `fabricops_kit.metadata.register_current_notebook`

## Used by internal helpers
- `fabricops_kit.metadata._resolve_action_by`
- `fabricops_kit.metadata._runtime_context`

## Debug relevance
Inspect this helper when parent callable outputs are malformed, missing evidence, or failing validation.

## Safe change guidance
Preserve helper contract, return shape, and side effects expected by parent callables.

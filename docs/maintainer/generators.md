# Generators

FabricOps keeps generated documentation and architecture artifacts derived from source inputs. Do not manually edit generated outputs as source of truth; update source, metadata, or generator logic first, then regenerate the owned artifacts.

## Important generators

| Generator | Primary output | When maintainers run it |
| --- | --- | --- |
| `scripts/generate_public_function_call_flows_json.py` | `docs/reference/_data/public-function-call-flows.json` | Function-level source changes that affect callable structure, exports, helper relationships, source locations, architecture classification, or public-flow metrics. |
| `scripts/generate_individual_function_reference_pages.py` | `docs/api/reference/*.md`, `docs/reference/index.md` | Release preparation or explicit generated-reference refreshes. Do not include these outputs in ordinary source PRs. |
| `scripts/generate_public_function_call_flows_dashboard.py` | `docs/assets/public-function-call-flows-dashboard.html` | Dashboard/generator refresh work, not routine source PRs. |
| `scripts/generate_release_inventory.py` | Release inventory validation inputs | Release preparation, usually with `--check`. |
| `scripts/generate_release_contract_pages.py` | `docs/releases/<version>/` contract pages | Release preparation after version and release inventory are ready. |

## Common commands

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py
PYTHONPATH=src python scripts/generate_public_function_call_flows_dashboard.py
PYTHONPATH=src python scripts/generate_release_inventory.py --check
PYTHONPATH=src python scripts/generate_release_contract_pages.py
```

## Supporting references

- [Release Workflow](release-workflow.md)
- [Public API & Architecture](public-api-architecture.md)
- [Function Call Graph](../function-call-graph.md)

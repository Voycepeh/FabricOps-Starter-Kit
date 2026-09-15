# Step 7. Consume approved Production data

**Use `99_explore` as the final handoff in the Guided Demo: project-specific consumers read approved Production data without recreating the Production engineering workflow.**

The required delivery work is already complete. Governance has established and activated the contract, and Engineering Production has published the governed output.

## Load the shared configuration

`99_explore` starts with:

```python
%run 00_env_config
```

In a consumer workspace, configure the logical Production stores that users are allowed to read.

## Read approved Production data

Use the foundational FabricOps readers to inspect the governed Production output through its configured logical store.

For example, read the appropriate Lakehouse table or Warehouse table/query without copying the `02_pipeline` transformation into the consumer workspace.

The consumer should receive the published result, not reimplement the engineering that produced it.

## Explore without mutating the governed workflow

`99_explore` is useful for:

- discovery and ad hoc analysis,
- BI, AI, and data-science exploration,
- Warehouse SQL pushdown through `read_warehouse_query()`,
- local exploratory profiling,
- read-oriented catalogue inspection and troubleshooting.

Keep repeatable transformation and governed publication in `02_pipeline`. Keep Governance authoring and approval in `01_governance`.

## See how the pieces now fit together

You have completed the same seven-stage operating flow described in How FabricOps Works:

1. Governance created the people and agreement context.
2. Engineering built and ran the real ETL, creating the technical evidence.
3. Governance authored the table-specific Data Contract.
4. Engineering selected and validated the frozen version.
5. Governance linked the agreement and activated the tested version.
6. Engineering promoted and ran the same pipeline in Production.
7. Consumers now use the approved Production output.

The four reusable notebooks have different responsibilities:

| Notebook | Responsibility |
| --- | --- |
| `00_env_config` | Environment and Fabric-store wiring. |
| `01_governance` | Steward, agreement, Data Contract authoring, freezing, and activation. |
| `02_pipeline` | Repeatable full-read Engineering, explicit checks, project transformation, governed publication, and technical metadata. |
| `99_explore` | Read-oriented consumption, exploration, and troubleshooting. |

That is the intended Guided Demo outcome: users should understand not just individual FabricOps functions, but how the entire operating practice fits together from setup through governed Production consumption.

**Complete:** return to the [Guided Demo overview](../guided-demo.md) or continue into the [Function Reference](../reference/index.md) for exact APIs.

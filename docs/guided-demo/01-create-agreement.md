# Step 1: Create Data Stewards and Data Agreements

**Use `01_governance` in the Governance workspace to establish accountable Data Stewards and the Data Agreement before Engineering starts.**

The agreement workflow uses `DATA_AGREEMENT_CONFIG` from `00_env_config` to control form fields and widget behaviour.

!!! info "Key concepts for this step"

    **Data Steward**, **Data Agreement**, and **Metadata** are the only glossary concepts you need before starting this step.

    In FabricOps, the Data Agreement is created between two distinct active Data Stewards: one provider and one recipient. Hover over a glossary term for its canonical definition, or open the [Glossary](../glossary.md) for the full entry.

## High-level flow

```text
Open Governance → Create provider and recipient Data Stewards → Create Data Agreement
```

## Before you begin

Confirm that the correct Fabric Environment is attached, `00_env_config` has been run, and the Governance metadata tables are available.

![Setup](../assets/01/Setup.png)

???+ success "Live — Create the Data Stewards"

    Populate the Data Steward records for the accountable provider and recipient roles.

    ![Steward](../assets/01/Steward.png)

???+ success "Live — Create the Data Agreement"

    Create the Data Agreement between the provider Data Steward and recipient Data Steward. Record the business purpose, approved usages, validity period, supporting documents, and other governance context required for the sharing relationship.

    ![Agreement](../assets/01/Agreement.png)

    ![Agreement 2](../assets/01/Agreement(2).png)

???+ success "Live — Understand what comes next"

    At this stage the Data Agreement exists independently. Step 3 later authors and freezes a table-centric Data Contract without Agreement linkage; Step 5 links the tested frozen version to this exact Data Agreement version during activation.

## Expected result

You should now have accountable provider and recipient Data Steward records, a Data Agreement describing their governed sharing relationship, and the governance foundation needed before running the Development pipeline.

**Next:** [Step 2: Run the Development pipeline](02-run-pipeline.md)

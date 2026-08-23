# Step 1: Create Data Stewards and Data Agreements

**Use `01_governance` in the Governance workspace to establish accountable Data Stewards and the Data Agreement before Engineering starts.**

The agreement workflow uses `DATA_AGREEMENT_CONFIG` from `00_env_config` to control form fields and widget behaviour.

## High-level flow

```text
Open Governance → Create Data Stewards → Create Data Agreement
```

## Before you begin

Confirm that the correct Fabric Environment is attached, `00_env_config` has been run, and the Governance metadata tables are available.

![Setup](../assets/01/Setup.png)

???+ success "Live — Create the Data Stewards"

    Populate the Data Steward records for the accountable parties.

    ![Steward](../assets/01/Steward.png)

???+ success "Live — Create the Data Agreement"

    Create the Data Agreement between the relevant Data Stewards.

    ![Agreement](../assets/01/Agreement.png)

    ![Agreement 2](../assets/01/Agreement(2).png)

???+ success "Live — Understand what comes next"

    At this stage the agreement exists before the Data Catalogue has been created. Step 5 returns to `01_governance` after `02_pipeline` has produced Engineering evidence and links the governed Data Catalogue to the Data Agreement through a Data Contract.

## Expected result

You should now have accountable Data Steward records, a Data Agreement describing the governance relationship, and the governance foundation needed before running the Development pipeline.

**Next:** [Step 2: Run the Development pipeline](02-run-pipeline.md)

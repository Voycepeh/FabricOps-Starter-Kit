# Step 3. Author and freeze the Data Contract

**Return to `01_governance`, review the generated contract against the profiled table, then freeze the version Engineering will validate in Step 4.**

Freezing creates an **immutable Data Contract** candidate for validation. Freezing does not activate it for Production.

!!! warning "Optional: enable Fabric AI Functions"
    FabricOps does not require AI. AI-assisted authoring is optional.

    To use it, meet the [AI Functions prerequisites](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/overview) and set `GOVERNANCE_CONFIG.ai_enrichment.enabled = True` in `00_env_config`.

    Learn more: [AI-assisted Data Contract Authoring](../solutions/ai-assisted-data-contract-authoring.md).

## 1. Open the Data Contract editor

Open `01_governance`, run the setup cells, select the target produced in Step 2, then run:

```python
widget_data_contract()
```

The editor uses the selected table's Catalogue and latest Profile as authoring evidence.

## 2. Table

Open **Table** and review:

* Description and Classification
* Grain & Row Key
* Processing
* Freshness, when required
* Source Drift, when required

Use AI suggestions where useful, then review them before applying.

## 3. Columns

Open **Columns**.

For each governed column, review the physical definition and examples, then author only what should become part of the contract:

* Required
* Classification and Description
* Sensitive Data treatment
* Column level Data Quality rules

Profile statistics are evidence only. They do not become contract requirements unless Governance authors a rule from them.

## 4. Business Rules

Open **Business Rules** for cross column requirements or rules that are easier to express in business language.

With AI enabled, describe the requirement and resolve it into a deterministic FabricOps Data Quality rule. Review the result before applying it.

Learn more: [Generate Enforceable Data Quality Rules from Business Rules](../solutions/business-rules-to-data-quality.md).

## 5. Manifest & Freeze

Open **Manifest & Freeze** and review the complete contract.

Choose **Save Data Contract** while the version is still a draft. When it is ready for Engineering validation, choose **Freeze**.

The frozen version is immutable and becomes the exact candidate Engineering selects in Step 4. Freezing does not activate it for Production.

## Expected result

You now have one frozen Data Contract ready for Engineering validation.

**Previous:** [Step 2. Run the Development pipeline](02-run-pipeline.md)  
**Next:** [Step 4. Select and validate the Data Contract](04-run-pipeline-with-guardrails.md)

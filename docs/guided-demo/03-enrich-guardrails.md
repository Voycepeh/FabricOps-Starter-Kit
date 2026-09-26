# Step 3. Author and freeze the Data Contract

**Return to `01_governance`, open the Data Contract editor, review the generated contract against the profiled table, then freeze the version Engineering will validate in Step 4.**

!!! warning "Optional: enable Fabric AI Functions"
    FabricOps does not require AI. Data Contracts can still be authored, frozen, validated, activated, and enforced without it.

    AI enables **Business Rule → Data Quality rule** translation plus Description, Grain & Row Key, Sensitive Data, and Pattern suggestions.

    Before using AI, confirm the [AI Functions prerequisites](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/overview) are met and set `GOVERNANCE_CONFIG.ai_enrichment.enabled = True` in `00_env_config`.

    AI only proposes changes. **Governance reviews and approves them.**

## 1. Open the Data Contract editor

Open `01_governance`, run the setup cells, select the target produced in Step 2, then run:

```python
widget_data_contract()
```

The editor uses the selected table's Catalogue and latest Profile as authoring evidence.

## 2. Table

Start with the **Table** tab.

Review and complete:

* Description and Classification
* Grain & Row Key
* Processing
* Freshness, when required
* Source Drift, when required

When AI is enabled, use the suggestion controls where useful, then review the proposed values before applying them.

## 3. Columns

Open **Columns**.

For each governed column, review the physical definition and examples shown by the editor, then author only what should become part of the contract:

* Required
* Classification and Description
* Sensitive Data treatment
* Column level Data Quality rules

Profile statistics are evidence only. They do not become contract requirements unless Governance explicitly authors a rule from them.

## 4. Business Rules

Open **Business Rules** for requirements that involve more than one column or are easier to express in business language.

With AI enabled, describe the requirement in plain language and resolve it into a deterministic FabricOps Data Quality rule.

Examples:

* end date must be after start date
* when status is Approved, approved date is required
* total amount must equal quantity × unit price × (1 - discount)
* either email or mobile number must be present

Review the resolved rule before applying it. If FabricOps resolves the requirement to a Custom Expression, complete the required Engineering review before freezing.

## 5. Manifest & Freeze

Open **Manifest & Freeze**.

Review the complete contract together. Confirm that the table definition, row key, column governance, Guardrails, Processing, and Business Rules match what Governance intends.

Choose **Save Data Contract** while the version is still a draft.

When it is ready for Engineering validation, choose **Freeze**.

The frozen version is immutable and becomes the exact candidate Engineering selects in Step 4. Freezing does not activate it for Production.

## Expected result

You now have one frozen Data Contract ready for Engineering validation.

**Previous:** [Step 2. Run the Development pipeline](02-run-pipeline.md)  
**Next:** [Step 4. Select and validate the Data Contract](04-run-pipeline-with-guardrails.md)

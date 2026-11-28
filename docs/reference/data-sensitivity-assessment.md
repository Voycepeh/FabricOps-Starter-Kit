# Data Sensitivity and Classification

Use Data Sensitivity Assessment to decide how to handle a column or dataset before approving its classification in a Data Contract.

## Try the classification calculator

Upload a CSV dataset for a suggested classification and personal data (PII) assessment. You can also try one of 53 synthetic scenarios.

<div class="sensitivity-calculator" data-sensitivity-calculator>
  <form>
    <div class="sensitivity-calculator__actions">
      <label for="sensitivity-dataset-file">Upload a CSV dataset
        <input id="sensitivity-dataset-file" type="file" accept=".csv,text/csv" aria-describedby="sensitivity-file-help" data-dataset-file>
      </label>
    </div>
    <small id="sensitivity-file-help">Use a UTF-8 CSV with a header row, up to 2 MB and 500 columns.</small>
    <div class="sensitivity-calculator__scenario-picker">
      <label for="sensitivity-scenario">Try a scenario
        <select id="sensitivity-scenario" data-scenario aria-describedby="sensitivity-scenario-help" disabled>
          <option value="">Loading scenarios…</option>
        </select>
      </label>
      <button type="button" class="md-button" data-load-scenario disabled>Load and assess</button>
    </div>
    <small id="sensitivity-scenario-help">Scenarios cover single columns, datasets, and Spark group-size checks.</small>
    <div data-calculator-inputs hidden>
      <h3>Column details</h3>
      <p><strong data-profile-name></strong></p>
      <p data-spark-reference hidden></p>
      <p>Review the suggested descriptions and categories. Edit them here or upload your own descriptions.</p>
      <label for="sensitivity-dictionary-file">Upload a data dictionary (optional)
        <input id="sensitivity-dictionary-file" type="file" accept=".csv,.json" aria-describedby="sensitivity-dictionary-help" data-dictionary-file>
      </label>
      <small id="sensitivity-dictionary-help">Use CSV with <code>column_name</code> and <code>description</code> headers, or JSON mapping column names to descriptions.</small>
      <div data-column-fields></div>
      <label for="sensitivity-linkage">Can sensitive information in this dataset identify people or a sensitive group?
        <select id="sensitivity-linkage" data-linkage>
          <option value="">Unknown</option>
          <option value="yes">Yes, linkage is confirmed</option>
          <option value="no">No, the information cannot be linked</option>
        </select>
      </label>
      <details>
        <summary>Policy settings</summary>
        <label for="sensitivity-policy">GovernanceConfig settings (JSON)
          <textarea id="sensitivity-policy" data-policy spellcheck="false"></textarea>
        </label>
        <div class="sensitivity-calculator__actions">
          <button type="button" class="md-button" data-apply>Apply policy and assess</button>
          <button type="button" class="md-button" data-reset>Reset to defaults</button>
        </div>
        <small>Apply changes to refresh the business categories and treatment targets and see the comparison.</small>
      </details>
      <details>
        <summary>Explore treatment suggestions</summary>
        <label for="sensitivity-target">Target classification
          <select id="sensitivity-target" data-target></select>
        </label>
      </details>
      <div class="sensitivity-calculator__actions">
        <button type="submit" class="md-button md-button--primary">Run assessment</button>
      </div>
    </div>
  </form>
  <p role="status"></p>
  <div data-results hidden></div>
  <noscript>Enable JavaScript to run the calculator.</noscript>
</div>

The calculator profiles the entire uploaded CSV and scans each column using the FabricOps value detectors. It shows inferred types and counts of blank and distinct values. Exact header matches can suggest business categories, such as Payroll for `monthly_salary`. Review those suggestions against the actual business use. Pattern matches flag possible PII and can raise minimum handling while the classification remains unresolved. The table result applies to the rows in the uploaded file.

A data dictionary can cover any subset of the columns. Use exact column names. CSV also accepts an optional `category` header. For JSON, a description can be a string or an object such as `{"description": "Monthly base salary", "category": "payroll"}`. A category must exist in the active policy. Edit the descriptions and categories or open **Policy settings** to compare a different rule, then run the assessment again.

The calculator runs deterministic Python in your browser. It loads the Python runtime on first use and keeps your CSV, dictionary, and policy edits in the tab. Use Fabric for approved Data Contracts, verified lineage, Spark group-size checks, and optional AI.

## Default policy rules

FabricOps bases its defaults on three governance principles. Data approved for general release may be handled as Unclassified. Data with uncertain classification needs at least Restricted handling. Combining data can increase the impact of disclosure or make sensitive information identifiable.

| Level | When to use it | Example |
| --- | --- | --- |
| **Unclassified** | General or public release has been authorised and disclosure has minimal impact. | Approved catalogue prices |
| **Restricted** | Access is limited to authorised internal users, or classification is still uncertain. | Internal budget or business contact details |
| **Confidential** | Information is sensitive or critical, or disclosure could have significant consequences. | Identifiable payroll, examination material, or business information with significant disclosure impact |

An assessment keeps three values visible. The **assessed classification** reflects the evidence, and can be unknown. The **approved classification** comes from Governance. The **minimum handling classification** is the protection to apply while the assessment or classification decision is open. An email-shaped value with unknown business use, for example, can leave the classification unknown while requiring Confidential handling and review.

## How FabricOps assesses a column

FabricOps reuses an applicable approved classification or inherits one through verified lineage. A rename or filter can preserve the values and their classification. A calculation or other change can require a fresh assessment while the upstream handling floor still applies. For a whole published Lakehouse target, automatic inheritance requires a profile pinned to the assessed Delta version and a matching committed publication.

For deterministic assessment, choose a business category in the widget or pass one in `column_definitions`. The policy maps that category to a class. Choosing **Payroll** for an `amount` column produces a Confidential classification under the defaults. Deterministic rules read the category field directly. A description such as “monthly staff salary” supplies context for review and optional AI.

Configured detectors recognise patterns such as email addresses and validate some identifiers with checksums. Positive evidence can raise minimum handling and trigger review. Profile statistics can miss rare values. Engineering can explicitly supply the same Spark DataFrame for local value checks. Optional AI assists with unresolved evidence when the endpoint is approved and the caller opts in. The request uses evidence codes and temporary column references. Frequency values and profile extrema stay local. Governance can explicitly opt in to sending business descriptions.

The defaults distinguish vendor bank accounts (Restricted) from employee or other personal bank accounts (Confidential), and internal programme information (Restricted) from individual grades or admissions records (Confidential). Select the category that describes the business use. A limited or sampled profile cannot establish a new Unclassified classification for the whole dataset. Apply at least the uncertain-data handling level unless an applicable approved dataset classification establishes its handling.

## When the dataset needs more protection

A compilation takes at least the highest applicable class of anything it contains. The combination can warrant a higher class even when the individual columns keep their original labels.

| Evidence | Individual columns | Dataset finding |
| --- | --- | --- |
| An approved catalogue price and an internal budget | Unclassified and Restricted | Restricted |
| An institutional identifier and de-identified employment statistics | Restricted and Restricted | Confirmed linkage makes the dataset Confidential. An unverified link calls for review. |
| Department and age band, both tagged as indirect identifiers, alongside a salary band | Each can be Restricted in isolation | A small group can make a salary band attributable to an individual. Review the combined dataset and apply the higher handling where identification is possible. |

A rule in `combinations` first checks whether all its categories are present. Rules with `requires_linkage: true` also need confirmation that the sensitive information identifies a person or a sensitive group. For example, a report owner's email does not identify the people in a separate salary summary. Use the calculator's linkage field or pass `sensitive_linkage=True` to record confirmed linkage. The default raises the dataset to Confidential while retaining the individual column labels. If linkage is unknown, a matching rule requests review. Spark group-size findings still apply when linkage is declared absent. For a table with at least two columns tagged `quasi_identifier`, you can supply its Spark DataFrame to count rows that share the same combination. A group smaller than `small_group_minimum` raises the dataset assessment to the configured suspected-sensitive level. The default of five is a review threshold. Even a larger group may be identifiable using other available information. Without a matching DataFrame, the assessment flags joint group sizes for review.

## Configure your organisation's policy

In **00 Environment Config**, edit the `GovernanceConfig` settings. You can save the calculator policy as JSON and load it with `GovernanceConfig(**json.loads(policy_json))`. Keep the existing settings for other governance workflows.

| Setting | What to enter |
| --- | --- |
| `classification_levels` | An ordered mapping of labels and their meanings, from lowest to highest protection. Keep existing labels in the configured order until Governance reviews any changes to saved classifications. |
| `sensitivity_assessment["categories"]` | Business categories mapped to a classification. Each category may also record whether it generally describes personal or sensitive data. A category supplied here can replace a built-in rule with the same key. |
| `sensitivity_assessment["combinations"]` | A list of categories that together warrant a dataset classification. Set `requires_linkage` to true for a rule that needs confirmed linkage. Providing the list replaces the default combinations. |
| `sensitivity_assessment["unresolved_handling"]` and `["suspected_handling"]` | The minimum handling for uncertain data and the level to apply when evidence suggests higher sensitivity. |
| `sensitivity_assessment["detectors"]` and `["small_group_minimum"]` | The value patterns to check and the threshold for local group-size review. |

For example, an organisation with its own three labels can adapt the following settings. The example defines the categories it uses. When renaming levels, map the categories, combinations, and handling floors to the new label strings.

```python
from fabricops_kit import GovernanceConfig

GOVERNANCE_CONFIG = GovernanceConfig(
    classification_levels={
        "Release approved": "Authorised for general release.",
        "Internal": "Limited to authorised internal users.",
        "Protected": "Sensitive information or high disclosure impact.",
    },
    sensitivity_assessment={
        "categories": {
            "institutional_identifier": {
                "classification": "Internal",
                "sensitive": True,
            },
            "deidentified_employment_statistics": {
                "classification": "Internal",
                "personal": False,
                "sensitive": True,
            },
        },
        "combinations": [{
            "categories": ["institutional_identifier", "deidentified_employment_statistics"],
            "classification": "Protected",
            "requires_linkage": True,
        }],
        "unresolved_handling": "Internal",
        "suspected_handling": "Protected",
        "detectors": ["email", "phone", "payment_card"],
        "small_group_minimum": 5,
    },
)
```

## Assess, treat and review

1. In the Data Contract widget, open **Columns → Data Sensitivity Assessment**, choose a category for each relevant column and select **All columns** to assess the dataset. Engineering can also pass an existing table profile or orchestration `profile_result` to the callable. Review the result's scope before applying its findings to the whole table. [Assessment function reference](../api/reference/assess_data_sensitivity.md)
2. If you want to assess a lower target, enter it explicitly. For an internal budget extract with a personal email column, removing the email could support a Restricted output if the remaining data cannot be linked back to individuals. If the remaining information stays sensitive, the higher protection still applies.
3. Stage the reviewed treatment through the Data Contract and verify that it ran on the actual published output. Reassess that output and obtain Governance approval before lowering its handling or sharing it more broadly. [Sensitive Data Treatments](sensitive-data-treatments.md) · [Author and freeze a Data Contract](../guided-demo/03-author-and-freeze-data-contract.md)

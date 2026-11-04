# Independent Pipeline Approval and Engineering deployment

Engineering submits a complete immutable notebook candidate, Governance independently decides it, and Engineering deploys the exact approved snapshot. Governed execution remains blocked pending [signed-in Fabric acceptance](governed-pipeline-fabric-acceptance.md).

## Metadata ownership and permissions

**Governance owns the entire central Metadata Lakehouse in its workspace, including Engineering metadata.** This is the accepted ownership model. Governance's workspace role grants access to both schemas; the `engineering` schema is not a security boundary against Governance. Engineering still has no access to the Governance notebook workspace and no write access to Governance policy or approval records.

| Resource | Engineering | Governance |
| --- | --- | --- |
| Metadata Lakehouse `engineering` schema | Read/write through granular OneLake permissions | Read/write as Lakehouse owner |
| Metadata Lakehouse `governance` schema | Read-only | Read/write |
| Engineering workspace | Read/write | No access required |
| Governance notebook workspace | No workspace role; explicit Metadata item access only | Read/write |
| `Files/fabricops/engineering/` | Read/write | Read/write as owner |
| `Files/fabricops/publication_coordination/` | Read/write for existing publication claims | Read/write for Contract Activation coordination |

Grant Engineering basic **Read on the Metadata item**, with granular OneLake roles for its schema, Governance policy reads and the explicitly listed Files paths. Do not grant Engineering a Contributor, Member or Admin role in the Governance workspace, item-wide Write, Reshare, or unrestricted parent-folder access. Review/remove broad DefaultReader assignments where they exceed intended reads. Table/schema permissions do not grant Files permissions. The publication ledger contains physical-target claims, never submission staging or approval authority.

Microsoft documents [granular ReadWrite roles](https://learn.microsoft.com/en-us/fabric/onelake/security/data-access-control-model) for Lakehouse tables/folders and Spark writes. Elevated workspace roles bypass those restrictions. Tenant availability, runtime support, inherited groups, direct paths, default roles and permission propagation must be tested under the actual two identities. If granular writes cannot be enforced in the tenant, this arrangement cannot provide the Engineering write restriction: leave Governed admission blocked. Application checks and confirmation boxes cannot substitute for Fabric permissions.

Bootstrap `setup_metadata_tables()` runs under the Metadata owner's identity. Engineering notebooks do not need permission to create Governance tables. Configuration-driven cross-workspace business source reads and target writes retain their existing authorized routing; metadata restrictions do not prohibit them.

## Canonical records

The canonical inventory contains **14 tables**. The only added table is `governance.METADATA_PIPELINE_ACTIVATION`; no existing table is removed.

| Table or path | Grain and responsibility |
| --- | --- |
| `METADATA_PIPELINE_ACTIVATION` | Append-only accepted-package import and Governance decision events, exact approval identity, monotonic pipeline revision, review policy, expiration and recovery intent |
| `METADATA_PIPELINE_REGISTRY` | Engineering deployment version, exact approval/submission identities, snapshots, operations, provenance and retained version lineage |
| `METADATA_DATA_CONTRACT_ACTIVATION` | Retained physical workspace/Table ID revisions selecting exact frozen Contracts and applicable Agreement versions; one active selection |
| `METADATA_DATA_CONTRACT` | Immutable global frozen Contract definitions |
| `METADATA_PIPELINE_RUN` | Actual execution and exact Contract ID/version/payload SHA for each operation |
| `Files/fabricops/engineering/dry_runs/` | Complete serializable saved-definition and recorded test claims retained before a captured Dry Run session ends |
| `Files/fabricops/engineering/submissions/` | Complete canonical packages saved automatically by Engineering Finalize; Governance reads them directly |
| `Files/fabricops/engineering/pipeline_snapshots/` | Write-once source/promoted snapshots and preserved modified copies during recovery |

Catalogue, Profiled, Profiled Frequency, Lineage, Data Access, Guardrail Results and Processing State retain their processing responsibilities. Released v0.3.1 records and content/hash projections are preserved. This change adds no adapters or migration machinery for the unreleased promotion model. Incompatible Preview layouts fail explicitly while retaining their contents; normal setup never deletes metadata or business data.

## Saved definition, execution claims and submission identity

A Dry Run captures the complete saved `.ipynb` at setup. Finalization retains available saved-definition and operation claims in Engineering Files without publishing business tables, Run rows, checkpoints, profiles or lineage. If no definition could be captured, no verifiable submission can be exported. Persistence errors surface; successful computation is not successful submission or approval.

`finalize_pipeline(preview)` verifies that the current saved executable behavior still equals the definition captured before execution. The complete pre-execution definition and current submitted saved notebook remain separate package components; changed outputs or Markdown do not pretend to be executed code. It automatically saves a JSON package containing:

- A versioned manifest with unique submission/Pipeline IDs, source workspace/notebook, destination workspace, creator/time and reviewed expected active version.
- Complete pre-execution, submitted source and promoted notebooks encoded as base64, distinct full SHA256 hashes and executable digests. Only the saved startup call is frozen to Governed; imported dependencies remain outside scope.
- Recorded Dry Run ID/result, stage outcomes, tested source/target Table IDs and complete physical bindings, plus the separately resolved deployment bindings.
- Read/write strategies, SQL hash, source/target associations, original requested schema, behavior parameters, and exact applicable recorded Contract payloads.
- A canonical SHA256 over **all** package components except the digest itself.

Validation rejects missing/duplicate JSON fields, altered bytes, incomplete runs, inconsistent parameters/operations and changed accepted submission identities. Retargeted bindings remain distinct from the physical destinations actually tested. Governance resolves the proposed destination from its own configuration and reviews that difference.

**These are untrusted Engineering claims.** A recomputed digest does not establish that claimed testing happened, nor attest kernel code identity. Governance reviews the complete notebook, recorded outcomes and independently resolved active policy. Self-approval by the claimed creator is rejected as a supplementary check; actual separation requires distinct security groups and protected Governance storage. Creator claims alone are not authentication.

## Saved submissions and decision state

1. **Engineering:** save the development notebook with a stable `PIPELINE_ID` and `PIPELINE_MODE = "Dry Run"`. Run it through `finalize_pipeline(pipeline)`. FabricOps automatically saves the submission in the Metadata Lakehouse.
2. **Governance:** run `widget_activate_pipeline()` and click **Refresh submissions**. Select the **Saved pipeline submission**, choose **Approve**, and click **Review submission**. Review the notebook and checks, enter a review note, tick the confirmation, and click **Save Governance decision**.
3. **Engineering:** beneath Finalize, click **Refresh approvals**, select that approval, and click **Review approved deployment**. Tick the deployment confirmation and click **Deploy approved notebook**. FabricOps creates the separate Governed notebook, archives its snapshot and records it in Registry.
4. **Engineering:** open the new notebook in the Engineering workspace's **Governed** folder and update your Fabric schedule or notebook activity to target it. Keep the development notebook in Dry Run mode.

There is no package download, upload or JSON paste. Governance reads the saved submission directly.

To reopen Engineering controls in the same kernel, rerun only `finalize_pipeline(pipeline)`. After a restart, rerun the Environment cell and call `finalize_pipeline(pipeline_id=PIPELINE_ID)`; another Dry Run is not required just to deploy an existing approval.

For recovery, select a **Retained implementation**, choose **Restore the active notebook** or **Rollback through a new version**, and click **Submit recovery request**. Governance selects that saved request in the same widget and approves it; Engineering then applies the approval using step 3.

Governance discovery reads `Files/fabricops/engineering/submissions/` in the configured Metadata Lakehouse. Opening or refreshing the widget does not import, approve or deploy. Review re-reads the selected package and rejects a changed digest since refresh, then saves the complete protected copy in `METADATA_PIPELINE_ACTIVATION.package_json` under Governance's identity. Decisions and deployments use that copy; changed or deleted Engineering files cannot replace it. Invalid individual submissions are reported without hiding valid packages or accepted history. No pending rows are added to Registry and no additional table is needed.

`setup_pipeline(..., pipeline_mode="Governed")` validates active notebook identity, approval, executable definition, parameters and physical bindings before managed work. Changing the source notebook's mode does not approve, freeze or deploy it. Setup blocks on drift and never overwrites edited notebooks. Finalize preserves its existing summary return value; export/UI errors are reported separately and may be retried without rerunning a completed execution.

Opening a widget grants no authority. Import is `imported`, not approved. Each decision appends a distinct `approval_id` with a pipeline-scoped increasing revision. Conditional mutation against the reviewed revision rejects stale/conflicting decisions; accepted package content never changes. Revocation and rejection remain in history. A later approved implementation supersedes earlier deployment requests. The current deployed implementation remains valid while the replacement awaits deployment; the conditional Registry commit selects the new version for new starts. Existing admitted runs retain captured authority unless it is revoked or expires. Approval alone never creates a notebook or an active deployment.

Governance may inspect Registry/Run metadata because it owns the Lakehouse. Its pipeline widget displays recorded deployments without opening source or deployed Engineering notebook items. Registry records remain Engineering deployment claims and do not become authoritative approval evidence.

## Agreement–Contract association

**Use the physical Contract Activation as the scoped association; no junction table is needed.** Each activation selects one frozen Contract and at most one exact Agreement ID/version/content SHA. One Agreement can govern many activations; the same global Contract can be reused under different terms in different physical workspaces. An Agreement is not automatically attached globally to every use of that Contract.

`widget_activate_data_contract()` independently reviews and conditionally activates that selection. Agreement content and effective dates are verified at review and mutation, and again for Governed policy resolution. Cross-workspace operations require an effective associated Agreement. Consumer provisioning resolves the same exact physical activation and requires its Agreement; an Engineering Registry edit cannot authorize consumption.

Registry Agreement columns are removed. Historical approval policy captures review-time Contract/Agreement selections; it does not pin runtime Contract selection forever. The conceptual link remains:

`METADATA_PIPELINE_REGISTRY.operations_json → METADATA_DATA_CONTRACT_ACTIVATION → METADATA_DATA_CONTRACT`

The first arrow is a logical physical workspace/Table ID association. Exact keyed references are application-enforced; Delta does not provide invented database foreign keys. Each new run resolves the active Contract independently, validates its strategy and Agreement, and records exact Contract provenance. An unchanged compatible notebook does not require promotion when Governance activates a new Contract version. In-flight runs retain their captured definitions and policy.

## Engineering deployment and runtime admission

The internal deployment service independently reads authoritative approval, verifies the complete accepted package, destination identity, current bindings/policy, revocation/expiration/supersession and expected active version. It never uses the latest editable source notebook for deployment.

Engineering archives full source/promoted snapshots, creates a separate Governed item under its own authorized Fabric identity, retrieves the complete definition and requires exact byte equality. A deterministic promotion identity and uniquely named staged item recover retries after lost acknowledgements; duplicate staged identities reject. Serializable whole-table conditional mutation atomically supersedes the old Registry version and inserts the next monotonic version. Failed staging preserves prior authority; retained versions are never silently rewritten or reactivated.

Governed admission independently checks the exact Governance decision, every authority-bearing Registry field, archived bytes, current saved executable implementation, parameters and physical operations. Runtime implementation comparison excludes transient code-cell outputs/counts and execution-only UI/timing metadata; code, parameter cells and behavior metadata remain bound; Markdown, raw documentation cells, cell IDs, outputs and execution counts may change. Full archived bytes and initial deployment readback remain exact. Setting Registry `status = active` cannot manufacture authority. New starts require the current active physical notebook. Managed boundaries reverify the captured immutable deployment; new implementation approval alone does not interrupt an already admitted older implementation. The existing exclusive physical-target publication claims coordinate old/new versions, Ungoverned writers and Contract Activation.

There is no distributed transaction spanning a Governance decision, an Engineering notebook API call and a Registry Delta commit. Approval is rechecked immediately before conditional commit and every governed admission/managed boundary. Revocation racing staging may leave an untrusted staged item or deployment record; neither authorizes execution independently. No claim of absolute cross-service atomicity is made.

## Promotion, rollback and restoration

- **New promotion:** a newly approved submission produces a separate item and a new immutable Registry version.
- **Rollback:** Engineering submits a retained implementation for a new Governance decision. After approval, deployment creates a new auditable version with `restored_from_version` lineage; it never reactivates an old row.
- **Restoration:** Engineering submits the active implementation for a separate exact restoration authorization. Governance approves the target promotion/version/snapshot. Engineering verifies both the original deployment approval and recovery authorization, retains modified content before update, restores the exact approved snapshot and verifies complete readback. The intended implementation version stays unchanged. A write-once Engineering Files receipt binds the recovery approval, retained modified-copy URI, operator and completion timestamp. Exact retries reuse that receipt; later executable modifications require a fresh recovery decision.

Governance authorizes sensitive decisions; Engineering performs technical notebook operations. Neither widget visibility nor a caller-provided confirmation grants backend authorization. The standalone public `promote_pipeline()`, `restore_pipeline()` and `activate_data_contract()` functions are removed without aliases. The two Governance activation interfaces remain `widget_activate_pipeline()` and `widget_activate_data_contract()`; `finalize_pipeline()` displays the Engineering submission, deployment and recovery controls; no separate public deployment or restore function is exposed.

## Fabric limits and release gate

Engineering workspace users may have direct permission to edit Governed notebook items or invoke Spark outside FabricOps. Saved-definition verification has a TOCTOU limit: it cannot prove which code is already loaded in a kernel or prevent all intervening edits. Governed folders organize items and confer no security. Write-once archive APIs are not storage-level WORM against privileged writers; runtime compares their bytes with the accepted Governance copy. Protect the canonical Metadata routing configuration and Governance groups; caller-owned alternative stores are not trusted authority.

No SPN, Workspace Identity or shared notebook kernel is required. No actual tenant permission or Fabric notebook API acceptance has been performed in this environment. Keep `FABRIC_GOVERNED_VALIDATED = False` until the signed-in checklist is completed. Local mocks verify application behavior, not Fabric access control.

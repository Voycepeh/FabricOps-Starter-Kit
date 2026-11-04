# Independent approval: signed-in Fabric acceptance

**Status: not executed in Fabric.** Keep `FABRIC_GOVERNED_VALIDATED = False` until genuine tenant acceptance is reviewed. Local tests, API mocks and successful hashes cannot enable the release gate.

Governance owns the central Metadata Lakehouse in its own workspace and may read/write all metadata. Engineering receives scoped schema and Files access, plus read-only Governance policy access. See the [architecture and accepted ownership model](governed-pipeline-promotion.md).

## Required tenant evidence

Record commit/version, date, tester, disposable workspace labels and outcomes. Keep real identifiers, credentials and private URLs out of public evidence. Test independent signed-in Engineering and Governance identities, not role flags in one Python kernel.

| Check | Required result | Status |
| --- | --- | --- |
| Engineering workspace isolation | Governance can review packages without entering the Engineering workspace or calling its notebook APIs | Pending |
| Governance workspace isolation | Engineering has only explicitly shared Metadata item access; no workspace role or notebook access | Pending |
| Governance ownership | Governance may read/write both metadata schemas as the accepted Lakehouse owner | Pending |
| Engineering metadata permissions | Engineering writes its allowed schema, reads Governance policy, and is denied direct Spark/OneLake/SQL writes to approvals, Contracts and activations | Pending |
| Files permissions | Engineering accesses only explicit operational Files paths; schema permissions do not confer Files access; no unrestricted parent grant | Pending |
| Group/default-role evaluation | No indirect Contributor/Member/Admin, item-wide Write or broad default role bypasses intended restrictions; propagation delays are observed | Pending |
| Metadata setup | Owner creates missing tables and validates Serializable properties; Engineering need not initialize Governance tables | Pending |
| Independent handoff | Finalize saves the completed captured Dry Run package; Governance lists and selects it directly in an unrelated session without download/paste; changed/deleted pending files reject review; decisions bind the protected review copy | Pending |
| Independent decision | Governance selects/reviews/approves saved submissions under its own identity; opening/refreshing reads only; review retains the protected copy and approval creates no Engineering notebook | Pending |
| Engineering deployment | Only an authorized Engineering operator can create the separate item; approval and deployment preserve distinct identities | Pending |
| Notebook Get/Create Definition | Full `.ipynb` including metadata, Markdown and code survives exact byte readback; normalization or unsupported parts fails closed | Pending |
| Notebook Update Definition | Separately authorized restoration preserves modified content first, retains intended version and verifies full saved bytes | Pending |
| Long-running APIs and retry | Create/Get/Update 202 polling and operation result work; a lost Create response recovers the uniquely named staged item without duplication | Pending |
| Archived snapshots | Write-once APIs reject overwrites; corruption or changed Engineering Registry hashes cannot bypass comparison with Governance's accepted copy | Pending |
| Approval state | Missing, stale, rejected, revoked, expired, superseded and conflicting decisions reject; Registry `active` alone grants no authority | Pending |
| Destination bindings | Configured cross-workspace sources and targets remain supported with exact approved physical bindings | Pending |
| Agreement authorization | Review and execution independently verify the active physical Contract's exact effective Agreement; consumer provisioning uses the same association | Pending |
| Contract replacement | Next run adopts a compatible newly activated Contract without notebook promotion; Run retains exact per-operation Contract ID/version/hash | Pending |
| Delta concurrency | Simultaneous first promotions, phantom inserts, stale versions and lost acknowledgements preserve at most one active monotonic version | Pending |
| Physical publication | Old/new admitted versions and Ungoverned/Contract Activation mutations use the existing exclusive target claims; interrupted claims require reconciliation | Pending |
| Revocation racing deployment | Staged artifacts/deployment records confer no authority after revocation; subsequent admission and managed boundaries fail closed | Pending |
| Manual/scheduled execution | Identical approval/integrity checks; superseded notebook schedules reject; Engineering explicitly rebinds schedules | Pending |
| Parameter overrides | Changed code, SQL, setup parameters, behavior metadata or physical operations reject; Markdown, raw documentation cells, cell IDs, outputs, counts and transient timing/UI metadata may change during execution | Pending |
| Captured prior authority | Already admitted superseded implementations finish under captured versions and Contracts; new starts use current authority | Pending |
| Rollback | Separate Governance decision returns to retained code through a new version, with immutable lineage | Pending |
| Restoration | Separate exact recovery decision and explicit action beneath Finalize required; Setup blocks on drift without automatic repair; stale target/approval rejects; modified copy retained before overwrite | Pending |
| Processing regressions | Standard 02 and 02A/02B/02C, Ungoverned, released v0.3.1 metadata, row hashes, append/incremental/SCD, observations and receipts remain functional | Pending |
| TOCTOU and direct bypass | Saved versus executing code and privileged direct Spark bypass are demonstrated and residual limits explicitly accepted | Pending |

## Security limits

Granular OneLake permissions must be available and effective for the tenant/runtime. If they cannot provide Engineering's scoped writes without broad Governance workspace privileges, record that concrete failure and keep the gate closed. Governance's owner access to Engineering metadata is intentional.

A Governed folder is organizational. Directly privileged Engineering users can edit notebooks or execute Spark outside FabricOps. Saved-definition checks cannot attest the running kernel. Imported dependencies are not frozen. There is no atomic transaction across approval, notebook APIs and Registry writes; runtime authority verification remains necessary.

No workspace identities or service principals are required for this manual workflow. A release-gate change requires reviewed signed-in acceptance evidence, not a local monkeypatch or green CI.

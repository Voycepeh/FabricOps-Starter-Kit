# Quality

This page explains: the data quality rule lifecycle from profiling to enforcement evidence.
Use this when: you need to implement, review, and operate DQ rules in FabricOps.
Next read: [Metadata](metadata-and-contracts/index.md), [Start](quick-start.md), [API](reference/index.md).

<figure markdown>
  ![Data quality workflow with AI suggestions, human review, approval, and deterministic enforcement in pipelines](assets/DQ-with-ai.png){ .full-width }
  <figcaption>Quality lifecycle ownership belongs here: profile, suggest, approve, persist, enforce, and evidence feedback.</figcaption>
</figure>

## Lifecycle

`profile → suggest → approve → persist → enforce → evidence`

1. **Profile (`02_ex_*`)**: collect distribution and quality signals.
2. **Suggest**: generate candidate rules (AI-assisted where useful).
3. **Approve**: humans approve/reject candidate rules.
4. **Persist**: write approved rules to metadata history.
5. **Enforce (`03_pc_*`)**: run deterministic rule checks.
6. **Evidence**: write pass/fail, accepted outputs, quarantined outputs, and run context.

## Output model

- **Accepted output:** rows/partitions that satisfy approved rules.
- **Quarantined output:** failed records for remediation paths.
- **Feedback loop:** enforcement evidence informs next profiling and rule refinement cycle.

# Generate Enforceable Data Quality Rules from Business Rules

Write a business rule in plain language. FabricOps translates it into a reviewable, enforceable Data Quality rule.

## How it works

Governance describes what must be true in business language. FabricOps uses AI to interpret that intent and resolves it into the smallest supported deterministic Data Quality rule.

Known FabricOps rule patterns are preferred first, including Uniqueness, Column Relationship, Conditional Completeness, and Conditional Values. A constrained Custom Expression is used only when the requirement cannot be represented faithfully by a standard pattern.

The resulting rule is still reviewed by a human before it enters the Data Contract. Runtime enforcement remains deterministic.

## Why it matters

Business intent stays readable while Engineering receives an explicit rule shape that can actually be validated and enforced.

A future screen recording will show the full flow from plain-language rule to reviewed Data Quality rule.

For the hands-on workflow, see [Step 3: Author and freeze the Data Contract](../guided-demo/03-enrich-guardrails.md).

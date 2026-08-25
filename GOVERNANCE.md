# Governance

## Decision authority

Assurance CI separates the ability to produce evidence from the authority to accept change. No test job, workflow generator or AI coding agent may grant itself merge authority.

| Role | Accountability | Conflict rule |
|---|---|---|
| Architecture owner | Defines profiles, critical properties and trust boundaries | Cannot waive evidence through an undocumented workflow edit |
| Finding owner | Drives invariant, regression, remediation and status | Cannot close a critical finding without independent evidence |
| Evidence producer owner | Maintains determinism, provenance and limitations | Cannot silently declare its producer optional |
| Aggregator owner | Maintains stable decision semantics and producer resolution | Must remain distinct from arbitrary pull request code paths where feasible |
| Independent reviewer | Challenges threat model, oracle and claim wording | Unresolved objections remain visible |
| Release authority | Confirms revision and evidence bundle | Cannot infer deployment readiness from merge eligibility alone |

## Decision rules

- Critical properties are conjunctive. One failed critical property blocks acceptance.
- Missing, stale, cancelled, skipped or inconclusive critical evidence fails closed.
- Applicability decisions must be explicit, reviewable and bound to the evaluated revision.
- Aggregate coverage or pass rate cannot override a failed critical property.
- Historical findings and superseded claims remain traceable.

## Weakening controls

Removing or weakening a critical control requires an ADR containing rationale, affected claims, affected findings, replacement evidence, reviewer identity and effective revision. Silent weakening through renaming, matrix changes or workflow refactoring is prohibited.

## Versioning

Architecture documents, schemas and profiles use semantic versioning where practical. Breaking evidence changes require a new schema identifier and migration note. Versioned releases are immutable; corrections create a new release.

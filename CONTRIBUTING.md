# Contributing

Contributions should strengthen the assurance contract, improve falsifiability or make evidence easier to reproduce. A larger test count is not, by itself, an assurance improvement.

## Change classes

| Class | Examples | Minimum review evidence |
|---|---|---|
| Editorial | Wording, links, diagrams | Documentation validation |
| Producer | Test, analyzer, replay or audit | Determinism, scope and output contract |
| Policy | Profile, applicability or severity | Claim impact and independent review |
| Authority | Aggregator, branch protection or release decision | Threat analysis, negative test and ADR |
| Schema | Evidence or profile contract | Compatibility analysis and example update |

## Pull request contract

Every material pull request should state:

1. The affected assurance surface.
2. The claim, invariant or finding being changed.
3. The evidence produced for the exact head revision.
4. Whether the change strengthens, preserves or weakens the merge contract.
5. How failure, blocked execution and inconclusive evidence are represented.

Use the repository pull request template. Do not normalize cancelled, skipped, timed-out or infrastructure-failed checks to `PASSED`.

## Closing a finding

A critical finding is closed only when:

- the forbidden state is explicit;
- a regression reproduces the vulnerable condition where feasible;
- the regression is attached to an appropriate required gate;
- the result is revision-bound and retained; and
- the affected claim is updated without deleting prior history.

## Local validation

```bash
python3 scripts/validate_repository.py
sha256sum --check checksums/SHA256SUMS
```

Keep the validator dependency-free. New external actions or build dependencies must be justified and pinned immutably where supported.

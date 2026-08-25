## Assurance impact

- Affected surface:
- Claim, invariant or finding:
- Change posture: strengthens / preserves / weakens

## Evidence

- Exact revision:
- Producer or regression:
- Expected outcome:
- Artifact or receipt:

## Failure semantics

- [ ] Missing, stale, skipped, cancelled and inconclusive critical evidence still fails closed.
- [ ] Required context names and producer resolution remain stable, or an ADR explains the change.
- [ ] Claim and finding registries are updated where applicable.
- [ ] Aggregator and invariant digests are updated where applicable.
- [ ] AI-assisted or generated oracles declare origin and independent review.
- [ ] Runtime claims include separate environment-bound evidence.
- [ ] `python3 scripts/validate_repository.py` passes.
- [ ] `python3 -m unittest discover -s tests -v` passes.
- [ ] `sha256sum --check checksums/SHA256SUMS` passes.

## Review notes

Describe limitations, applicability decisions and any required independent review.

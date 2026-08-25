# Changelog

All notable architecture and contract changes are recorded here.

## [1.1.0] - 2026-08-25

### Added

- Formal, digest-bound invariant bundle.
- Fail-closed policy-as-code reference aggregator and receipt schema.
- Evidence envelope v2 with attestation, validity, oracle and environment fields.
- Research-release profile v2 with adversarial, environment and reproduction gates.
- Assurance latency, compute and flake budgets.
- Temporal claim registry with supersession and belief history.
- Seeded known-bad controls executed by CI.
- Threat model, hardening addendum and three-phase implementation roadmap.

### Clarified

- Cryptographic verification is an independent evidence-producer boundary.
- Green repository CI is not evidence of a live external effect.
- External clean-room reproduction and immutable off-platform anchoring remain open exit criteria.

## [1.0.0] - 2026-08-25

### Added

- Initial Assurance CI architecture specification, REMORA-ACA-001.
- Evidence-envelope and assurance-profile schemas.
- Research-release policy profile.
- Claim and finding registries.
- Architecture decision record and governance model.
- Dependency-free repository integrity validation.
- GitHub Actions enforcement workflow.

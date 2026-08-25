# Implementation roadmap

## Phase 1: Bind the control plane

Status: **implemented in repository v1.1**

- Machine-readable invariant bundle.
- Digest-bound reference aggregator.
- Evidence envelope v2 and aggregator receipt schema.
- Claim validity and belief-history registry.
- Assurance budgets and seeded known-bad controls.

Exit criterion: repository tests block missing, stale, failed, wrong-revision, unverified and over-budget evidence.

## Phase 2: Verify external authority

Status: **contracted, integration pending**

- GitHub OIDC plus Sigstore or in-toto attestation verifier producer.
- Signed human exception and applicability decisions.
- Adversarial fuzzing and property testing at authorization and dispatch boundaries.
- Periodic control pull requests for matrix renaming, stale evidence and aggregator substitution.
- SBOM, VEX and vulnerability-exception lifecycle producers.

Exit criterion: a workflow cannot self-authorize, replace the aggregator or bypass a required family without a deterministic block.

## Phase 3: Externalize assurance

Status: **planned**

- Environment-bound runtime identity, custody and external read-back.
- One-command clean-room REMORA reproduction using pinned hashes and no GitHub Actions secrets.
- Bit-for-bit manifest comparison or declared nondeterministic exceptions.
- Content-addressed assurance bundles with independent retention or transparency anchoring.
- Independent operator reproduction and deliberate merge-authority bypass assessment.

Exit criterion: an external operator can reconstruct the declared release decision and separately verify any runtime claim.

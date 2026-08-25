# Assurance CI hardening v1.1

This addendum strengthens REMORA-ACA-001 by making invariants, aggregator logic, attestation boundaries and evidence validity first-class repository contracts.

## Control additions

| Area | v1.1 control | Repository artifact | Implementation state |
|---|---|---|---|
| Formal invariants | Structured preconditions, predicate, postconditions, threat scenario and producers | `policy/invariants.yaml` | Digest-bound and statically validated |
| Aggregator policy-as-code | Fail-closed reference evaluator with deterministic receipt | `assurance_ci/aggregate.py` | Executable reference implementation |
| Aggregator receipt | Stable decision, reasons, identities, budgets and limitations | `schemas/aggregator-receipt.schema.json` | Implemented |
| Adversarial assurance | Authorization fuzzing, dispatch properties, bypass and stale-evidence replay | `policy/research-release-v2.json` | Required release family; producers remain integration work |
| Attestation | Explicit externally verified OIDC/Sigstore outcomes | Evidence v2 and profile v2 | Contract implemented; cryptographic verification remains an independent producer |
| Environment evidence | Runtime identity, custody, validity and external read-back | Evidence v2 | Contract implemented; live integration remains open |
| Assurance budgets | Latency, compute and critical flake ceilings | Profile v2 and aggregator | Enforced by reference aggregator |
| Claim lifecycle | Scope, validity, supersession and immutable belief history | `registry/claims-v2.json` | Implemented as registry contract |
| Reproduction | One-command, secret-free clean-room requirement | Profile v2 and roadmap | Policy requirement; independent reproduction remains open |
| Seeded controls | Known-bad evidence sets with expected BLOCKED reasons | `registry/known-bad-revisions.json` | Executed in unit tests |

## Formal ratchet contract

The closure sequence is now machine-addressable:

```text
finding
  -> invariant ID + formal predicate
  -> deterministic failing fixture or regression
  -> required aggregator family
  -> evidence envelope v2
  -> digest-bound aggregation receipt
  -> claim belief-history update
```

An invariant bundle and aggregator program are SHA-256-bound in the selected profile. A modification that is not accompanied by a profile update causes `aggregator_program_digest_mismatch` or `invariant_bundle_digest_mismatch` and blocks the decision.

## Cryptographic trust boundary

The reference aggregator does **not** claim to verify signatures. It requires a separate trusted verifier producer to emit `verification_outcome: PASSED`, a verifier identity and an attestation bundle digest. This preserves custody separation:

1. The producer creates evidence or a human decision.
2. OIDC, Sigstore, in-toto, SSH or another mechanism signs or attests it.
3. An independent verifier validates the cryptographic material.
4. The aggregator consumes only the verifier's revision-bound result.

Self-attestation by the workflow being evaluated is not acceptable.

## Repository-bound versus environment-bound evidence

Repository evidence proves properties of a revision, build or release artifact. It cannot establish live runtime identity, key custody or external effect. Any evidence envelope evaluating a `runtime` claim therefore requires:

- environment identifier and runtime identity;
- time-limited observation;
- observation digest;
- key-custody attestation; and
- authoritative external read-back.

Absent or expired environment evidence blocks activation of the runtime claim.

## AI-generated oracle policy

AI-generated or AI-assisted test oracles must declare their origin. A critical oracle is not accepted merely because it agrees with the implementation that generated it. The evidence contract records whether independence was reviewed and by whom. High-value invariants should be grounded in an external specification, separately authored requirement or adversarially constructed counterexample.

## Supply-chain lifecycle

The release profile treats SBOM, VEX, provenance and vulnerability exceptions as separate evidence producers. An exception requires validity, owner, justification and signed decision; it must not erase the underlying vulnerability record.

## Evidence retention and anchoring

GitHub artifacts alone are not the long-term trust anchor. Full release assurance should publish content-addressed bundles to immutable retention and, where justified, anchor the manifest digest in an independent transparency or archival system. The repository currently preserves release-document checksums; external anchoring is roadmap work.

## Metrics that drive action

| Metric | Definition | Control response |
|---|---|---|
| Ratchet velocity | Confirmed critical finding to invariant plus live required regression | Escalate when target is exceeded |
| Bypass surface area | Known paths outside required aggregators | Reduce to zero or mark explicit scope exclusion |
| Claim drift rate | Claims becoming stale or contradicted without fidelity detection | Strengthen claim and documentation producers |
| Seeded-control survival | Known-bad controls still producing expected block | Block release on any false green |
| Assurance budget pressure | Latency, compute and flake consumption | Split fast and release paths without weakening release criteria |

These are diagnostic and operational metrics. They cannot override a failed critical property.

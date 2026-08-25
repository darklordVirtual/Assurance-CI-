# Threat model

## Protected decision

The protected decision is whether an exact revision may merge, release or activate a scoped claim. The primary security property is that no evidence producer, workflow author or AI agent can unilaterally grant that authority.

## Trust boundaries

- pull request and generated code;
- workflow definition and runner;
- evidence producer;
- attestation verifier;
- aggregator program and invariant bundle;
- protected branch or release authority;
- deployment environment and external effect observer;
- immutable evidence retention.

## Deliberate bypass scenarios

| Scenario | Required detection | Expected outcome |
|---|---|---|
| Required job renamed or removed from a matrix | Expected-producer resolution | `BLOCKED` |
| Evidence from another revision reused | Exact revision comparison | `BLOCKED` |
| Expired evidence replayed | Temporal validity check | `BLOCKED` |
| Workflow substitutes weaker aggregator logic | Program digest binding | `BLOCKED` |
| Invariant bundle edited without profile update | Invariant digest binding | `BLOCKED` |
| Workflow self-declares signature valid | Independent verifier allow-list | `BLOCKED` |
| `NOT_APPLICABLE` used to avoid a critical producer | Signed applicability decision | `BLOCKED` until verified |
| CI result presented as live-effect proof | Environment evidence requirement | Runtime claim remains inactive |
| AI-generated test validates its own assumption | Oracle-origin and independence review | Escalate or block critical claim |
| Assurance becomes too slow or flaky and is skipped | Budget outcome and stable release path | `BLOCKED`, not silent omission |

## Explicit limitations

The repository contains reference contracts and a deterministic aggregator. It does not yet supply live OIDC/Sigstore verification, production environment observation, external content-addressed retention or a full clean-room REMORA release. Those capabilities remain separate evidence producers and must not be inferred from green repository CI.

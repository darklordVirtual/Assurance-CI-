# Assurance CI Architecture

> Turning safety findings into merge-blocking evidence

**Document ID:** REMORA-ACA-001

**Version:** 1.0

**Status:** Architecture proposal

**Scope:** Research-grade CI/CD for governed agent execution

**Audience:** Maintainers, reviewers, adopters and research evaluators

**Date:** 25 August 2026

**Owner:** REMORA Research

| **CORE PROPOSITION** Assurance CI is not a collection of test jobs. It is an enforcement architecture that converts discovered failure modes into permanent, revision-bound conditions for change acceptance. |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# Document control

| **Field**        | **Definition**                                                      | **Decision rule**                                    |
|------------------|---------------------------------------------------------------------|------------------------------------------------------|
| Authority        | Repository maintainers and explicitly delegated reviewers           | No workflow may create its own governance authority. |
| Protected object | Main branch, release tags and research claims                       | Mutation requires complete assurance evidence.       |
| Unit of evidence | A result bound to commit SHA, workflow identity and artifact digest | Floating or unbound evidence is invalid.             |
| Failure posture  | Fail closed for missing, stale, inconclusive or bypassable checks   | Uncertainty is not converted into success.           |
| Primary output   | Merge decision plus replayable assurance bundle                     | A green badge alone is insufficient.                 |

# Executive summary

Modern AI-assisted development can produce changes faster than a human reviewer can reconstruct their full safety impact. Traditional CI responds by running more tests. Assurance CI responds differently: it defines which safety and research claims must remain true, what evidence is acceptable, and which stable checks have authority to block change.

The architecture treats CI as a repository-level policy enforcement point. Independent jobs produce evidence; stable aggregators evaluate completeness; branch protection enforces the result; and release bundles preserve the relationship between revision, checks, claims and artifacts. A failure is not considered resolved until its forbidden state is expressed as an invariant and protected by a deterministic regression path.

| **DECISION** Adopt Assurance CI as a named architectural subsystem of REMORA. Document its contracts, owners, failure semantics and evidence schema independently from individual GitHub Actions workflows. |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 1. Purpose and research question

The purpose of Assurance CI is to make rapid, AI-assisted research engineering compatible with cumulative safety assurance. It addresses the research question: How can a high-change repository ensure that each discovered failure permanently strengthens, rather than merely patches, the system?

The central mechanism is an assurance ratchet. Findings can move the repository toward stricter and more explicit guarantees, but they cannot silently disappear when code, documentation, dependencies or deployment configuration changes.

## 1.1 Scope

- Source code, policy, schema, workflow, dependency and documentation changes.

- Deterministic safety properties at assessment, authorization, dispatch and effect-verification boundaries.

- Research claims, negative results, remediation state and reproducibility artifacts.

- Merge, release and deployment evidence bound to an exact repository revision.

- Human review where policy or evidence requires an accountable decision.

## 1.2 Non-goals

- Proving that the complete system is secure under every environment or threat model.

- Replacing architectural judgment with a single score, coverage number or green badge.

- Treating a successful workflow execution as proof of external effect.

- Allowing an AI coding agent, workflow or test generator to grant itself merge authority.

- Using CI as a substitute for independent replication, human evaluation or operational monitoring.

# 2. Core concepts

| **Concept**         | **Meaning**                                                                           | **Assurance consequence**                                                 |
|---------------------|---------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| Assurance claim     | A precise statement expected to hold for a named surface and threat model.            | Must have current, revision-bound evidence and an owner.                  |
| Invariant           | A state or transition that must always hold, independent of model preference.         | Violation is merge-blocking unless explicitly removed through governance. |
| Evidence producer   | A test, analyzer, replay job, audit or human review that emits structured results.    | May report facts but may not unilaterally authorize merge.                |
| Required aggregator | A stable check that evaluates whether required evidence is present and acceptable.    | Provides the branch-protection contract despite dynamic job matrices.     |
| Negative result     | A falsified hypothesis, failed target or discovered bypass.                           | Must be preserved and linked to claim or remediation state.               |
| Assurance bundle    | Manifest of revision, workflow identity, inputs, outputs, digests and claim mappings. | Makes the decision auditable and replayable.                              |

# 3. Architectural principles

**Evidence before assertion.** A claim is active only when acceptable evidence exists for the exact revision and scope.

**Stable enforcement, dynamic execution.** Job matrices may change; required aggregator names and semantics must remain stable.

**Fail closed on missing meaning.** Missing, stale, cancelled, skipped or inconclusive evidence cannot be normalized to success.

**Independent evidence producers.** Security, deterministic execution, supply chain and claim integrity should fail independently before aggregation.

**Permanent memory of failure.** A defect is closed only after a regression reproduces it and a required path prevents recurrence.

**Exact revision binding.** Every accepted result is bound to commit SHA, workflow source, configuration identity and relevant artifact digests.

**No authority by transport success.** Exit code zero, HTTP 200 or workflow completion is not proof that the intended external effect occurred.

**No aggregate safety score.** Coverage and pass rates support decisions but cannot conceal a failed critical property.

# 4. System architecture

Assurance CI separates evidence production from the authority to accept change. Individual jobs are sensors. Required aggregators are policy decision points over those sensors. Branch protection is the enforcement point. The release bundle is the durable receipt.

![Layered diagram showing change intake, independent assurance checks, stable required aggregators, protected merge and release evidence.](../figures/assurance-ci-enforcement-architecture.png)

*Figure 1. Assurance CI separates evidence production, aggregation, enforcement and durable receipts.*

## 4.1 Component responsibilities

| **Layer**            | **Responsibility**                                                         | **Must not do**                                               |
|----------------------|----------------------------------------------------------------------------|---------------------------------------------------------------|
| Change intake        | Identify affected surfaces, policies, claims and required check profile.   | Silently reduce the check set because a change appears small. |
| Evidence producers   | Run deterministic, security, supply-chain, replay and integrity checks.    | Interpret missing prerequisites as success.                   |
| Evidence registry    | Store structured outcomes, digests, provenance and freshness.              | Accept mutable or unbound evidence.                           |
| Required aggregators | Evaluate completeness and critical-property outcomes under stable names.   | Re-run the underlying tests or hide their distinct failures.  |
| Branch protection    | Block merge unless all required aggregators succeed for the head revision. | Depend on optional or actor-controlled checks.                |
| Release evidence     | Package manifest, claims, negative results, SBOM and execution records.    | Claim production readiness merely because CI passed.          |

# 5. The assurance ratchet

The feedback loop is the defining property of the architecture. A patch without a ratchet can be accidentally reversed. A ratcheted fix changes the repository's future acceptance criteria.

![Six-step loop from finding through invariant, regression, required gate, evidence and claim update.](../figures/assurance-ratchet.png)

*Figure 2. A finding becomes durable only when it changes what future revisions are allowed to merge.*

## 5.1 Closure contract

1.  Record the finding with an explicit affected surface, threat scenario and observed consequence.

2.  State the forbidden state or transition as a testable invariant.

3.  Create a deterministic regression that fails on the vulnerable revision and passes only after remediation.

4.  Attach the regression to an appropriate required assurance profile or justify why it is non-blocking.

5.  Bind the result to the exact revision and preserve the output in the assurance bundle.

6.  Update claim, negative-result and remediation state without deleting the history of the earlier belief.

| **CLOSURE RULE** A finding is not closed because the code changed. It is closed when recurrence becomes detectable and merge-blocking at the correct boundary. |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 6. Assurance gate taxonomy

A mature repository needs several independent gate families. Each family protects a different failure domain and produces separately inspectable evidence.

| **Gate family**        | **Primary concern**                                                        | **Acceptance condition**                                             |
|------------------------|----------------------------------------------------------------------------|----------------------------------------------------------------------|
| Deterministic suite    | Policy decisions, canonicalization, leases, state transitions, idempotency | Tests are repeatable and all critical invariants hold                |
| Boundary replay        | Recorded proposals, decisions, dispatch events and outcomes                | Replay preserves expected disposition and detects drift              |
| Concurrency            | Exclusive claim, replay resistance, outbox and settlement races            | No duplicate authority or contradictory terminal state               |
| Static security        | Taint flow, injection, secret exposure, unsafe deserialization             | No unresolved critical findings in protected surfaces                |
| Supply chain           | Dependencies, lockfiles, SBOM, provenance and artifact digest              | Declared inputs are auditable and policy-compliant                   |
| Trust-base coverage    | Policy, execution, governance and authorization components                 | Component-specific floors hold; aggregate coverage cannot compensate |
| Claim integrity        | Claims, evidence links, supersession and status vocabulary                 | Every active claim has valid evidence and no contradictory state     |
| Documentation fidelity | Architecture, deployment boundaries, test counts and status                | Shipped surfaces and limitations match current implementation        |
| Deployment evidence    | Runtime identity, key custody, database policy and external read-back      | Live claims require live, environment-bound evidence                 |

## 6.1 Critical-property rule

Critical safety properties are conjunctive. A single failure in exact-call integrity, authority provenance, execution-boundary integrity or effect settlement blocks acceptance even when thousands of unrelated tests pass. Overall pass rate and total coverage are diagnostic metrics, not override mechanisms.

# 7. Aggregation and merge authority

Required aggregators provide a stable interface between changing workflow topology and branch protection. They should evaluate the declared check profile, not merely collect jobs that happened to run.

## 7.1 Required aggregator contract

- Use a stable, protected context name that cannot be replaced by an untrusted workflow.

- Resolve the exact expected producer set from revision-controlled policy.

- Reject missing, cancelled, skipped, stale or neutral critical producers.

- Preserve the distinct reason for failure rather than collapsing all outcomes into generic red.

- Verify that producer outputs refer to the pull request head SHA and expected workflow identity.

- Emit a structured aggregation receipt listing evaluated producers and decision rationale.

## 7.2 Recommended stable contexts for REMORA

| **Required context**         | **Purpose**                                         | **Examples of constituent evidence**                                        |
|------------------------------|-----------------------------------------------------|-----------------------------------------------------------------------------|
| quality-gates-required       | Code, documentation, claims and component coverage  | Lint, type checks, tests, coverage floors, claim registry, doc registration |
| deterministic-suite-required | Deterministic execution and policy invariants       | Hard guards, lease validation, transition contracts, replay and idempotency |
| supply-chain-required        | Dependency and artifact integrity                   | Lockfile audit, SBOM, provenance, digest verification                       |
| codeql-required              | Static security analysis across supported languages | CodeQL matrices and severity policy                                         |
| shadow-replay                | Behavioral drift against recorded governed traces   | Proposal-to-decision replay, lifecycle and effect expectations              |

## 7.3 Control-plane pseudocode

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>expected = assurance_profile.for_revision(head_sha)<br />
observed = evidence_registry.results(head_sha)<br />
<br />
for required in expected.producers:<br />
result = observed.get(required.identity)<br />
require(result is not None, reason="missing_evidence")<br />
require(result.revision == head_sha, reason="stale_revision")<br />
require(result.workflow_digest == required.workflow_digest,<br />
reason="unexpected_producer")<br />
require(result.outcome == "PASSED", reason=result.outcome)<br />
<br />
emit_aggregation_receipt(head_sha, expected, observed)<br />
return PASSED</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 8. Evidence model

Every merge and release decision should be reconstructable without relying on a transient CI user interface. Evidence must identify what ran, against which revision, with which policy and inputs, and what the result actually proves.

## 8.1 Minimum evidence envelope

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>{<br />
"schema_version": "assurance-evidence/v1",<br />
"repository": "darklordVirtual/REMORA-research",<br />
"revision": "&lt;40-character commit SHA&gt;",<br />
"producer": {<br />
"check_name": "deterministic-suite",<br />
"workflow_digest": "sha256:&lt;digest&gt;",<br />
"runner_identity": "&lt;attested identity&gt;"<br />
},<br />
"policy_identity": "sha256:&lt;assurance profile digest&gt;",<br />
"started_at": "&lt;RFC 3339&gt;",<br />
"finished_at": "&lt;RFC 3339&gt;",<br />
"outcome": "PASSED | FAILED | BLOCKED | INCONCLUSIVE | NOT_APPLICABLE",<br />
"claims_evaluated": ["CLAIM-..."],<br />
"artifacts": [{"path": "...", "sha256": "..."}],<br />
"limitations": []<br />
}</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 8.2 Evidence validity rules

- Freshness: evidence applies only to the exact revision unless an explicit content-addressed reuse rule is satisfied.

- Provenance: producer identity and workflow definition must be authenticated or digest-bound.

- Completeness: all required producers and claims in the selected profile must be represented.

- Immutability: published release evidence must be content-addressed and resistant to silent replacement.

- Interpretability: each result declares what was evaluated and what remains out of scope.

- Replayability: inputs, versions and execution instructions are sufficient for an independent rerun where feasible.

# 9. Failure semantics

Assurance outcomes require a richer vocabulary than success and failure. The aggregator must preserve uncertainty and infrastructure problems instead of laundering them into a green state.

| **Outcome**    | **Meaning**                                                                           | **Merge treatment**                                             |
|----------------|---------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| PASSED         | The declared property was evaluated and the acceptance condition held.                | Eligible, subject to all other required evidence.               |
| FAILED         | The property was evaluated and violated.                                              | Block.                                                          |
| BLOCKED        | The check could not run because a declared prerequisite or authority was unavailable. | Block; fix prerequisite or explicitly change policy.            |
| INCONCLUSIVE   | Execution completed but evidence cannot establish pass or fail.                       | Block critical properties; route to review where policy allows. |
| NOT_APPLICABLE | The property is outside the revision's declared affected surface.                     | Accept only with a validated applicability decision.            |

| **ANTI-PATTERN** Cancelled, skipped, timed out, flaky or infrastructure-failed checks must never be converted to PASSED merely to keep the development queue moving. |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 10. Worked examples

## 10.1 Exact-call identity gap

A review discovers that the policy enforcement point validates a lease but does not re-read the ToolSpec identity used during authorization. A patch that adds one comparison is insufficient.

| **Ratchet step** | **Required action**                                                                                              |
|------------------|------------------------------------------------------------------------------------------------------------------|
| Finding          | Record that a valid lease can be paired with a substituted ToolSpec identity.                                    |
| Invariant        | The ToolSpec digest at final PEP must equal the digest bound into the authority chain.                           |
| Regression       | Construct a valid-looking lease with a substituted specification; prove that the vulnerable revision accepts it. |
| Gate             | Attach the regression to deterministic-suite-required and execution TCB coverage.                                |
| Evidence         | Store the failing-before/passing-after result with revision and workflow digests.                                |
| Claim state      | Limit or supersede any exact-call integrity claim until the new evidence is active.                              |

## 10.2 Intermittent dispatch-boundary failure

A full suite fails intermittently at a remote dispatch boundary. Re-running until green is not assurance. The correct response is to classify whether the instability is product behavior, test synchronization, infrastructure or an invalid deterministic assumption. Until classified, the affected property is INCONCLUSIVE and the release profile remains blocked.

## 10.3 Stale architecture documentation

The implementation changes from a symmetric decision token to an asymmetric, custody-separated execution lease, while the paper retains the old mechanism. Documentation fidelity should fail because reviewers would otherwise evaluate a system that no longer exists. The resolution is a revision-bound architecture assertion, not merely a later editorial cleanup.

# 11. Governance and ownership

| **Role**                | **Accountability**                                                       | **Conflict rule**                                                  |
|-------------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------|
| Architecture owner      | Defines assurance profiles, critical properties and boundary model.      | Cannot waive evidence silently through workflow edits.             |
| Finding owner           | Drives invariant, regression, remediation and status update.             | May not close without independent evidence.                        |
| Evidence producer owner | Maintains determinism, provenance and documented limitations of a check. | May not self-declare the producer optional.                        |
| Aggregator owner        | Maintains stable decision semantics and complete producer resolution.    | Must be distinct from arbitrary PR code paths where feasible.      |
| Independent reviewer    | Challenges threat model, test adequacy and claim wording.                | Review identity is recorded; unresolved objections remain visible. |
| Release authority       | Confirms exact revision and evidence bundle before publication.          | Cannot infer deployment readiness from merge eligibility alone.    |

# 12. Metrics that matter

Metrics should reveal assurance health without becoming substitutes for critical-property decisions.

| **Metric**                  | **Definition**                                                          | **Desired direction**                |
|-----------------------------|-------------------------------------------------------------------------|--------------------------------------|
| Claim evidence coverage     | Active claims with current, revision-bound evidence / all active claims | Toward 100%                          |
| Escaped regression rate     | Previously ratcheted defects observed after protected merge             | Toward zero                          |
| Flake budget                | Critical runs requiring rerun or producing inconsistent outcomes        | Zero for release profile             |
| Median finding-to-gate time | Time from confirmed finding to required regression protection           | Down, without weaker tests           |
| Open remediation age        | Age distribution by severity and affected trust boundary                | Down; oldest critical first          |
| Evidence completeness       | Required envelope fields and artifacts present                          | Toward 100%                          |
| Bypass path count           | Known credential or dispatch paths outside enforced boundary            | Toward zero or explicit out-of-scope |
| Reproduction success        | Independent clean-environment runs matching declared results            | Up                                   |

# 13. Maturity model

| **Level**                  | **Capability**                                                                                 | **Exit criterion**                                       |
|----------------------------|------------------------------------------------------------------------------------------------|----------------------------------------------------------|
| 0 - Build automation       | Code compiles and basic tests run.                                                             | Repeatable build.                                        |
| 1 - Quality CI             | Tests, lint and coverage are visible.                                                          | Routine regressions are blocked.                         |
| 2 - Protected CI           | Stable required checks and branch protection exist.                                            | Unreviewed failure cannot merge.                         |
| 3 - Assurance CI           | Claims, critical invariants and structured evidence drive required aggregators.                | Every active critical claim has current evidence.        |
| 4 - Reproducible assurance | Release bundles, content-addressed artifacts and independent replay are routine.               | External operator reproduces the declared profile.       |
| 5 - Operational assurance  | Deployment identity, live effects and continuous control monitoring extend the evidence chain. | Runtime claims are backed by environment-bound evidence. |

*REMORA is best characterized as approaching Level 4 internally, while independent reproduction and full operational effect verification remain the decisive exit criteria.*

# 14. Implementation roadmap

## Phase 1 - Name and bind the architecture

- Create a revision-controlled assurance profile that maps protected surfaces to required producers and claims.

- Define stable schemas for producer results and aggregator receipts.

- Document ownership and prevent workflow changes from silently weakening required contexts.

- Bind paper, architecture and test statistics to a fixed research release SHA.

## Phase 2 - Eliminate ambiguous outcomes

- Adopt PASSED, FAILED, BLOCKED, INCONCLUSIVE and NOT_APPLICABLE across assurance producers.

- Fail required aggregators on missing or stale evidence.

- Treat critical flakiness as release-blocking until its cause is classified.

- Emit machine-readable evidence envelopes for all required checks.

## Phase 3 - Externalize assurance

- Publish a one-command clean-room reproduction bundle for a fixed release.

- Obtain independent review of threat model, aggregator semantics and high-value regressions.

- Apply the assurance profile to a real tool-interception pilot with external effect read-back.

- Archive manifests, SBOM, results and claims under a persistent research identifier.

# 15. Acceptance criteria

- \[ \] All protected branch rules reference stable required aggregator contexts.

- \[ \] The expected producer set is revision-controlled and digest-bound.

- \[ \] Critical missing, stale, skipped, cancelled and inconclusive evidence blocks merge.

- \[ \] Each active critical claim maps to at least one current evidence producer and explicit scope.

- \[ \] Every closed critical finding has a deterministic regression or a documented reason why one is impossible.

- \[ \] Component-specific trust-base coverage floors cannot be offset by unrelated coverage.

- \[ \] Release artifacts contain revision, workflow, policy and artifact digests.

- \[ \] Control pull requests periodically prove that branch protection blocks a deliberately failing required check.

- \[ \] Documentation fidelity checks cover architecture, shipped surfaces, limitations and reproduction instructions.

- \[ \] An independent operator can reproduce the declared research profile from a fixed release.

# 16. Research contribution

Assurance CI can be studied as more than repository hygiene. It is a method for converting empirical falsification into executable governance over future research revisions. The contribution is the explicit separation of evidence production, evidence aggregation, merge enforcement and claim lifecycle, joined by revision-bound receipts.

## 16.1 Testable hypotheses

- Repositories using an assurance ratchet have fewer recurrences of previously discovered critical failure classes than repositories using conventional regression CI alone.

- Stable required aggregators reduce branch-protection bypass caused by dynamic job names, matrices and workflow refactoring.

- Machine-enforced claim-to-evidence mappings reduce stale or contradicted research assertions after rapid architectural change.

- Explicit INCONCLUSIVE and BLOCKED states reduce false-green releases without requiring every infrastructure failure to be classified as a product defect.

- AI-assisted development achieves higher safe change throughput when prior findings are encoded as merge authority constraints rather than retained primarily in human review memory.

## 16.2 Evaluation design

A credible evaluation should compare conventional CI and Assurance CI over matched change histories or controlled seeded defects. Outcomes should include defect recurrence, time to detect, false-green rate, review effort, lead time, flake-induced delay and claim/document drift. External reviewers should attempt workflow bypass, stale-evidence reuse and critical-check omission.

# 17. Limitations

- Assurance CI can only enforce properties represented by correct checks, evidence policy and protected trust boundaries.

- A large test count does not compensate for missing real-world scenarios, incorrect oracles or bypassable credentials.

- Repository controls do not prove production deployment identity, key custody, availability or external effect without environment-bound evidence.

- Workflow and aggregator code become part of the trusted computing base and require their own review and protection.

- AI-generated tests may reproduce implementation assumptions rather than independent requirements unless reviewers challenge the oracle.

- Independent replication and human oversight remain necessary even when the internal evidence chain is complete.

# 18. Conclusion

Assurance CI explains how REMORA can sustain unusually high development velocity without relying on one maintainer to remember every prior failure and architectural decision. Its value is not the number of jobs. Its value is that discoveries change the future merge contract.

The architecture should be treated as a first-class REMORA subsystem and a candidate research contribution. The next step is to formalize the evidence schema and assurance profile, then validate the method through independent reproduction and deliberate attempts to bypass its merge authority.

| **FINAL PRINCIPLE** The repository becomes safer when every serious failure leaves behind a stronger rule than the patch that fixed it. |
|-----------------------------------------------------------------------------------------------------------------------------------------|

# Appendix A - Proposed repository artifacts

```text
docs/architecture/ASSURANCE_CI_ARCHITECTURE.md
docs/releases/Assurance_CI_Architecture_REMORA_v1.0.docx
schemas/assurance-profile.schema.json
schemas/assurance-evidence-envelope.schema.json
policy/research-release-v1.yaml
registry/claims.yaml
registry/findings.yaml
examples/evidence-envelope.example.json
.github/workflows/assurance-ci.yml
scripts/validate_repository.py
checksums/SHA256SUMS
```

# Appendix B - Proposed research-release profile

```yaml
schema_version: assurance-profile/v1
profile_id: research-release-v1
version: 1
revision_binding: exact_commit
failure_posture: fail_closed

required_aggregators:
  - quality-gates-required
  - deterministic-suite-required
  - supply-chain-required
  - codeql-required
  - shadow-replay

critical_outcomes_allowed: [PASSED]
non_success_outcomes:
  FAILED: block
  BLOCKED: block
  INCONCLUSIVE: block
  NOT_APPLICABLE: require_signed_applicability_decision

evidence_requirements:
  workflow_digest: true
  policy_digest: true
  artifact_digests: true
  claim_mapping: true
```

# Appendix C - Reference alignment

Assurance CI complements, but does not replace, established secure-development and supply-chain frameworks. Its distinctive focus is the repository-level relationship between failure discovery, critical invariants, claim lifecycle, stable merge authority and revision-bound research evidence.

| **Reference**                                          | **Relevant concept**                                            | **Assurance CI extension**                                                       |
|--------------------------------------------------------|-----------------------------------------------------------------|----------------------------------------------------------------------------------|
| NIST SP 800-218, Secure Software Development Framework | Secure development practices and vulnerability response         | Expresses closure as a required evidence and merge contract.                     |
| NIST AI Risk Management Framework                      | Govern, map, measure and manage AI risk                         | Binds selected controls and claims to executable repository evidence.            |
| SLSA                                                   | Build integrity, provenance and artifact supply-chain assurance | Adds claim, invariant and negative-result lifecycle above build provenance.      |
| OpenSSF Scorecard                                      | Automated repository security posture checks                    | Treats such checks as independent producers within a broader assurance decision. |
| GitHub protected branches and required checks          | Merge enforcement mechanism                                     | Defines stable aggregator semantics and revision-bound assurance receipts.       |

## Primary sources

> **NIST Secure Software Development Framework:** [<u>Official source</u>](https://csrc.nist.gov/projects/ssdf)
>
> **NIST AI Risk Management Framework 1.0:** [<u>Official source</u>](https://doi.org/10.6028/NIST.AI.100-1)
>
> **SLSA v1.2 provenance specification:** [<u>Official source</u>](https://slsa.dev/spec/v1.2/provenance)
>
> **OpenSSF Scorecard:** [<u>Official source</u>](https://www.scorecard.dev/)
>
> **GitHub protected branches and required checks:** [<u>Official source</u>](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

# Revision history

| **Version** | **Date**       | **Status**            | **Summary**                                                |
|-------------|----------------|-----------------------|------------------------------------------------------------|
| 1.0         | 25 August 2026 | Architecture proposal | Initial formalization of Assurance CI for REMORA Research. |

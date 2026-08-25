# ADR-0001: Treat Assurance CI as a first-class subsystem

- **Status:** Accepted
- **Date:** 2026-08-25
- **Decision owners:** REMORA Research maintainers
- **Architecture document:** REMORA-ACA-001 v1.0

## Context

Rapid, AI-assisted development can produce more change than a reviewer can safely reconstruct from memory. Conventional CI exposes job outcomes but often leaves merge authority, evidence completeness, claim lifecycle and failure semantics implicit. Dynamic matrix jobs and workflow refactoring can also weaken protected checks without changing the intended policy.

## Decision

Assurance CI is a named architectural subsystem with contracts independent of individual workflow files. It separates:

- evidence producers;
- revision-controlled assurance profiles;
- stable required aggregators;
- protected merge enforcement;
- release evidence; and
- claim and finding lifecycle.

Critical evidence fails closed unless the selected profile explicitly permits review. A result is valid only when bound to the exact revision and expected producer identity.

## Consequences

### Positive

- Discovered failures accumulate as permanent acceptance constraints.
- Branch protection depends on stable semantic interfaces.
- Merge and release decisions become reconstructable.
- Research claims can be limited or superseded when evidence changes.

### Costs and risks

- Aggregators and workflow identity become part of the trusted computing base.
- Additional schema, registry and evidence-retention work is required.
- Incorrect checks or oracles can still encode false confidence.
- Independent replication and environment-bound effect verification remain necessary.

## Exit criteria

The subsystem reaches reproducible assurance when an independent operator can recreate a fixed release profile, validate all required evidence and obtain the declared outcome without relying on a transient CI interface.

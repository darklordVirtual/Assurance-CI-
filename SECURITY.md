# Security policy

## Scope

Security-relevant reports include bypasses of required checks, untrusted replacement of a stable context, stale-evidence reuse, provenance substitution, claim/evidence mismatch and any path that converts blocked or inconclusive execution into success.

## Reporting

Use GitHub private vulnerability reporting for this repository when available. Do not publish exploit details, credentials or operational secrets in a public issue.

Include:

- affected revision and surface;
- expected invariant;
- minimal reproduction;
- observed decision or effect;
- whether the behavior is deterministic;
- proposed severity and blast radius.

## Response model

Confirmed findings are recorded in the finding registry, assigned an owner and processed through the assurance ratchet. A code patch alone is not sufficient closure for a critical finding.

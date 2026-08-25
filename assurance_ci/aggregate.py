#!/usr/bin/env python3
"""Fail-closed reference aggregator for Assurance CI evidence.

This module evaluates already-verified evidence envelopes. Cryptographic
signature verification remains an independent producer boundary; the
aggregator requires its explicit PASSED result and records the verifier.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
REVISION = re.compile(r"^[0-9a-f]{40,64}$")


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def unique_ordered(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _aggregator_config(profile: dict[str, Any], name: str) -> dict[str, Any] | None:
    for candidate in profile.get("required_aggregators", []):
        if candidate.get("name") == name:
            return candidate
    return None


def aggregate(
    *,
    profile: dict[str, Any],
    evidence: list[dict[str, Any]],
    revision: str,
    aggregator_name: str,
    decided_at: str,
    invariants_path: Path,
) -> dict[str, Any]:
    """Evaluate evidence and return a deterministic aggregation receipt."""

    reasons: list[str] = []
    limitations = [
        "The reference aggregator consumes attestation-verifier outcomes; it does not verify signatures itself."
    ]

    if not REVISION.fullmatch(revision):
        reasons.append("invalid_revision")

    try:
        decision_time = parse_time(decided_at)
    except (TypeError, ValueError):
        decision_time = datetime.max.replace(tzinfo=timezone.utc)
        reasons.append("invalid_decision_time")

    config = _aggregator_config(profile, aggregator_name)
    expected = list(config.get("producers", [])) if config else []
    if not config:
        reasons.append("unknown_aggregator")
    if not expected:
        reasons.append("empty_expected_producer_set")

    actual_program_digest = file_digest(Path(__file__).resolve())
    actual_invariant_digest = file_digest(invariants_path)
    binding = profile.get("digest_binding", {})
    if binding.get("aggregator_program_digest") != actual_program_digest:
        reasons.append("aggregator_program_digest_mismatch")
    if binding.get("invariant_bundle_digest") != actual_invariant_digest:
        reasons.append("invariant_bundle_digest_mismatch")

    profile_identity = canonical_digest(profile)
    by_name: dict[str, dict[str, Any]] = {}
    duplicate_names: list[str] = []
    for envelope in evidence:
        name = str(envelope.get("producer", {}).get("check_name", ""))
        if not name:
            reasons.append("producer_without_identity")
            continue
        if name in by_name:
            duplicate_names.append(name)
        by_name[name] = envelope
    reasons.extend(f"duplicate_producer:{name}" for name in sorted(set(duplicate_names)))

    unexpected = sorted(set(by_name) - set(expected))
    if unexpected and not profile.get("aggregation_policy", {}).get("allow_unexpected_producers", False):
        reasons.extend(f"unexpected_producer:{name}" for name in unexpected)

    attestation_policy = profile.get("attestation_policy", {})
    accepted_verifiers = set(attestation_policy.get("accepted_verifier_producers", []))
    oracle_policy = profile.get("oracle_policy", {})
    budgets = profile.get("assurance_budget", {})
    max_flake = float(budgets.get("critical_producer_max_flake_rate", 0.0))
    total_compute = 0.0
    total_wall_clock = 0.0
    observed: list[dict[str, Any]] = []
    environment_receipts: list[dict[str, Any]] = []

    for producer_name in expected:
        envelope = by_name.get(producer_name)
        if envelope is None:
            reasons.append(f"missing_evidence:{producer_name}")
            continue

        outcome = str(envelope.get("outcome", ""))
        envelope_revision = str(envelope.get("revision", ""))
        if envelope_revision != revision:
            reasons.append(f"revision_mismatch:{producer_name}")
        if envelope.get("policy_identity") != profile_identity:
            reasons.append(f"policy_identity_mismatch:{producer_name}")
        if outcome != "PASSED":
            reasons.append(f"producer_{outcome.lower() or 'missing_outcome'}:{producer_name}")

        validity = envelope.get("validity", {})
        try:
            observed_at = parse_time(str(validity.get("observed_at", "")))
            not_after = parse_time(str(validity.get("not_after", "")))
            if not observed_at <= decision_time <= not_after:
                reasons.append(f"stale_or_future_evidence:{producer_name}")
        except (TypeError, ValueError):
            reasons.append(f"invalid_validity_window:{producer_name}")

        execution = envelope.get("execution", {})
        try:
            total_compute += float(execution.get("compute_minutes", 0.0))
            total_wall_clock = max(total_wall_clock, float(execution.get("wall_clock_seconds", 0.0)))
            if float(execution.get("flake_rate", 1.0)) > max_flake:
                reasons.append(f"flake_budget_exceeded:{producer_name}")
        except (TypeError, ValueError):
            reasons.append(f"invalid_execution_metrics:{producer_name}")

        attestation = envelope.get("attestation", {})
        if attestation_policy.get("fail_on_unverified", True):
            verifier = str(attestation.get("verifier", ""))
            if attestation.get("verification_outcome") != "PASSED":
                reasons.append(f"unverified_attestation:{producer_name}")
            if verifier not in accepted_verifiers:
                reasons.append(f"untrusted_attestation_verifier:{producer_name}")
            if not DIGEST.fullmatch(str(attestation.get("bundle_digest", ""))):
                reasons.append(f"invalid_attestation_digest:{producer_name}")

        oracle = envelope.get("oracle", {})
        if oracle_policy.get("critical_requires_independence_review", True):
            if not oracle.get("independence_reviewed") or not oracle.get("reviewer"):
                reasons.append(f"unreviewed_oracle:{producer_name}")
        accepted_oracle_sources = set(oracle_policy.get("accepted_sources", []))
        if accepted_oracle_sources and oracle.get("source") not in accepted_oracle_sources:
            reasons.append(f"unaccepted_oracle_source:{producer_name}")

        runtime_claims = [
            claim for claim in envelope.get("claims_evaluated", [])
            if isinstance(claim, dict) and claim.get("scope") == "runtime"
        ]
        if runtime_claims:
            environment = envelope.get("environment")
            if not isinstance(environment, dict):
                reasons.append(f"missing_environment_evidence:{producer_name}")
            else:
                if not environment.get("external_readback"):
                    reasons.append(f"missing_external_readback:{producer_name}")
                if not environment.get("key_custody_attested"):
                    reasons.append(f"missing_key_custody_attestation:{producer_name}")
                if not DIGEST.fullmatch(str(environment.get("observation_digest", ""))):
                    reasons.append(f"invalid_environment_observation:{producer_name}")
                try:
                    environment_observed = parse_time(str(environment.get("observed_at", "")))
                    environment_not_after = parse_time(str(environment.get("not_after", "")))
                    max_age = float(profile.get("environment_evidence", {}).get("max_age_seconds", 0))
                    if not environment_observed <= decision_time <= environment_not_after:
                        reasons.append(f"stale_environment_evidence:{producer_name}")
                    if max_age and (environment_not_after - environment_observed).total_seconds() > max_age:
                        reasons.append(f"environment_validity_window_exceeded:{producer_name}")
                except (TypeError, ValueError):
                    reasons.append(f"invalid_environment_validity:{producer_name}")
                environment_receipts.append({
                    "producer": producer_name,
                    "environment_id": environment.get("environment_id"),
                    "observation_digest": environment.get("observation_digest"),
                })

        observed.append({
            "producer": producer_name,
            "outcome": outcome,
            "revision": envelope_revision,
            "evidence_digest": canonical_digest(envelope),
            "attestation_verifier": attestation.get("verifier"),
        })

    max_compute = float(budgets.get("max_compute_minutes", 0.0))
    max_wall_clock = float(budgets.get("max_aggregate_wall_clock_seconds", 0.0))
    if max_compute and total_compute > max_compute:
        reasons.append("compute_budget_exceeded")
    if max_wall_clock and total_wall_clock > max_wall_clock:
        reasons.append("latency_budget_exceeded")

    reasons = unique_ordered(reasons)
    decision = "BLOCKED" if reasons else "PASSED"
    return {
        "schema_version": "aggregator-receipt/v1",
        "repository": profile.get("repository"),
        "revision": revision,
        "profile_id": profile.get("profile_id"),
        "profile_identity": profile_identity,
        "aggregator": {
            "name": aggregator_name,
            "program_digest": actual_program_digest,
            "invariant_bundle_digest": actual_invariant_digest,
        },
        "expected_producers": expected,
        "observed_producers": observed,
        "decision": decision,
        "reason_codes": reasons,
        "decided_at": decided_at,
        "budget_observed": {
            "compute_minutes": round(total_compute, 6),
            "max_wall_clock_seconds": round(total_wall_clock, 6),
        },
        "environment_receipts": environment_receipts,
        "limitations": limitations,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate Assurance CI evidence")
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--evidence-set", required=True, type=Path)
    parser.add_argument("--invariants", required=True, type=Path)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--aggregator", required=True)
    parser.add_argument("--decided-at", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    evidence = json.loads(args.evidence_set.read_text(encoding="utf-8"))
    if not isinstance(evidence, list):
        raise SystemExit("evidence set must be a JSON array")

    receipt = aggregate(
        profile=profile,
        evidence=evidence,
        revision=args.revision,
        aggregator_name=args.aggregator,
        decided_at=args.decided_at,
        invariants_path=args.invariants,
    )
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if receipt["decision"] == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main())

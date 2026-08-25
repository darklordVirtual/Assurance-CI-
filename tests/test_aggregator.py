from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from assurance_ci.aggregate import aggregate


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0123456789abcdef0123456789abcdef01234567"
DECIDED_AT = "2026-08-25T18:00:30Z"


class AggregatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = json.loads((ROOT / "policy/research-release-v2.json").read_text())
        cls.passed = json.loads((ROOT / "tests/fixtures/passed-evidence-set.json").read_text())

    def evaluate(self, evidence: list[dict] | None = None) -> dict:
        return aggregate(
            profile=self.profile,
            evidence=copy.deepcopy(evidence if evidence is not None else self.passed),
            revision=REVISION,
            aggregator_name="quality-gates-required",
            decided_at=DECIDED_AT,
            invariants_path=ROOT / "policy/invariants.yaml",
        )

    def test_complete_current_evidence_passes(self) -> None:
        receipt = self.evaluate()
        self.assertEqual("PASSED", receipt["decision"])
        self.assertEqual([], receipt["reason_codes"])

    def test_missing_producer_blocks(self) -> None:
        receipt = self.evaluate(self.passed[:1])
        self.assertEqual("BLOCKED", receipt["decision"])
        self.assertIn("missing_evidence:claim-integrity", receipt["reason_codes"])

    def test_failed_producer_blocks(self) -> None:
        evidence = copy.deepcopy(self.passed)
        evidence[0]["outcome"] = "FAILED"
        receipt = self.evaluate(evidence)
        self.assertIn("producer_failed:repository-integrity", receipt["reason_codes"])

    def test_revision_mismatch_blocks(self) -> None:
        evidence = copy.deepcopy(self.passed)
        evidence[0]["revision"] = "f" * 40
        receipt = self.evaluate(evidence)
        self.assertIn("revision_mismatch:repository-integrity", receipt["reason_codes"])

    def test_stale_evidence_blocks(self) -> None:
        evidence = copy.deepcopy(self.passed)
        evidence[0]["validity"]["not_after"] = "2026-08-25T17:59:59Z"
        receipt = self.evaluate(evidence)
        self.assertIn("stale_or_future_evidence:repository-integrity", receipt["reason_codes"])

    def test_unverified_attestation_blocks(self) -> None:
        evidence = copy.deepcopy(self.passed)
        evidence[0]["attestation"]["verification_outcome"] = "INCONCLUSIVE"
        receipt = self.evaluate(evidence)
        self.assertIn("unverified_attestation:repository-integrity", receipt["reason_codes"])

    def test_untrusted_attestation_verifier_blocks(self) -> None:
        evidence = copy.deepcopy(self.passed)
        evidence[0]["attestation"]["verifier"] = "workflow-self-verifier"
        receipt = self.evaluate(evidence)
        self.assertIn("untrusted_attestation_verifier:repository-integrity", receipt["reason_codes"])

    def test_unreviewed_ai_oracle_blocks(self) -> None:
        evidence = copy.deepcopy(self.passed)
        evidence[0]["oracle"] = {
            "source": "ai-assisted",
            "independence_reviewed": False,
            "reviewer": "",
        }
        receipt = self.evaluate(evidence)
        self.assertIn("unreviewed_oracle:repository-integrity", receipt["reason_codes"])

    def test_compute_budget_blocks(self) -> None:
        evidence = copy.deepcopy(self.passed)
        evidence[0]["execution"]["compute_minutes"] = 31
        receipt = self.evaluate(evidence)
        self.assertIn("compute_budget_exceeded", receipt["reason_codes"])

    def test_latency_budget_blocks(self) -> None:
        evidence = copy.deepcopy(self.passed)
        evidence[0]["execution"]["wall_clock_seconds"] = 301
        receipt = self.evaluate(evidence)
        self.assertIn("latency_budget_exceeded", receipt["reason_codes"])

    def test_unexpected_producer_blocks(self) -> None:
        evidence = copy.deepcopy(self.passed)
        unexpected = copy.deepcopy(evidence[0])
        unexpected["producer"]["check_name"] = "actor-controlled-green-check"
        evidence.append(unexpected)
        receipt = self.evaluate(evidence)
        self.assertIn("unexpected_producer:actor-controlled-green-check", receipt["reason_codes"])

    def test_runtime_claim_requires_environment_evidence(self) -> None:
        evidence = copy.deepcopy(self.passed)
        evidence[0]["claims_evaluated"][0]["scope"] = "runtime"
        receipt = self.evaluate(evidence)
        self.assertIn("missing_environment_evidence:repository-integrity", receipt["reason_codes"])

    def test_runtime_claim_with_current_environment_evidence_passes(self) -> None:
        evidence = copy.deepcopy(self.passed)
        evidence[0]["claims_evaluated"][0]["scope"] = "runtime"
        evidence[0]["environment"] = {
            "environment_id": "synthetic-production",
            "runtime_identity": "spiffe://example.invalid/runtime",
            "observation_digest": "sha256:" + "a" * 64,
            "observed_at": "2026-08-25T18:00:00Z",
            "not_after": "2026-08-25T18:10:00Z",
            "external_readback": True,
            "key_custody_attested": True,
        }
        receipt = self.evaluate(evidence)
        self.assertEqual("PASSED", receipt["decision"])

    def test_digest_binding_detects_aggregator_substitution(self) -> None:
        profile = copy.deepcopy(self.profile)
        profile["digest_binding"]["aggregator_program_digest"] = "sha256:" + "0" * 64
        receipt = aggregate(
            profile=profile,
            evidence=copy.deepcopy(self.passed),
            revision=REVISION,
            aggregator_name="quality-gates-required",
            decided_at=DECIDED_AT,
            invariants_path=ROOT / "policy/invariants.yaml",
        )
        self.assertIn("aggregator_program_digest_mismatch", receipt["reason_codes"])

    def test_seeded_known_bad_controls_remain_blocked(self) -> None:
        registry = json.loads((ROOT / "registry/known-bad-revisions.json").read_text())
        for control in registry["controls"]:
            with self.subTest(control=control["id"]):
                evidence = json.loads((ROOT / control["fixture"]).read_text())
                receipt = self.evaluate(evidence)
                self.assertEqual(control["expected_decision"], receipt["decision"])
                self.assertIn(control["expected_reason_code"], receipt["reason_codes"])


if __name__ == "__main__":
    unittest.main()

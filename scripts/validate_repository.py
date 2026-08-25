#!/usr/bin/env python3
"""Dependency-free structural validation for the Assurance CI repository."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []

REQUIRED_PATHS = [
    "README.md",
    "GOVERNANCE.md",
    "CONTRIBUTING.md",
    "CITATION.cff",
    "docs/architecture/HARDENING_V1_1.md",
    "docs/THREAT_MODEL.md",
    "docs/implementation/ROADMAP.md",
    "docs/architecture/ASSURANCE_CI_ARCHITECTURE.md",
    "docs/adr/0001-assurance-ci-as-a-first-class-subsystem.md",
    "docs/figures/assurance-ci-enforcement-architecture.png",
    "docs/figures/assurance-ratchet.png",
    "docs/releases/Assurance_CI_Architecture_REMORA_v1.0.docx",
    "schemas/assurance-evidence-envelope.schema.json",
    "schemas/assurance-evidence-envelope-v2.schema.json",
    "schemas/assurance-profile.schema.json",
    "schemas/assurance-profile-v2.schema.json",
    "schemas/assurance-invariant.schema.json",
    "schemas/aggregator-receipt.schema.json",
    "schemas/claim-registry-v2.schema.json",
    "policy/research-release-v1.yaml",
    "policy/research-release-v2.json",
    "policy/invariants.yaml",
    "registry/claims.yaml",
    "registry/claims-v2.json",
    "registry/findings.yaml",
    "registry/known-bad-revisions.json",
    "examples/evidence-envelope.example.json",
    "examples/environment-attestation.example.json",
    "examples/aggregator-receipt.example.json",
    "assurance_ci/__init__.py",
    "assurance_ci/aggregate.py",
    "tests/test_aggregator.py",
    "tests/fixtures/passed-evidence-set.json",
    "tests/fixtures/known-bad-stale-evidence.json",
    "tests/fixtures/known-bad-revision-mismatch.json",
    "checksums/SHA256SUMS",
]

ALLOWED_OUTCOMES = {"PASSED", "FAILED", "BLOCKED", "INCONCLUSIVE", "NOT_APPLICABLE"}
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
REVISION = re.compile(r"^[0-9a-f]{40,64}$")
LOCAL_MD_LINK = re.compile(r"!?\[[^]]*]\((?!https?://|mailto:|#)([^)]+)\)")


def fail(message: str) -> None:
    ERRORS.append(message)


def require_paths() -> None:
    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).is_file():
            fail(f"missing required file: {relative}")


def load_json(relative: str) -> dict:
    try:
        data = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON in {relative}: {exc}")
        return {}
    if not isinstance(data, dict):
        fail(f"top-level JSON value must be an object: {relative}")
        return {}
    return data


def load_json_value(relative: str):
    try:
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON in {relative}: {exc}")
        return None


def canonical_digest(value) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def file_digest(relative: str) -> str:
    return "sha256:" + hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def validate_json_contracts() -> None:
    for relative in (
        "schemas/assurance-evidence-envelope.schema.json",
        "schemas/assurance-evidence-envelope-v2.schema.json",
        "schemas/assurance-profile.schema.json",
        "schemas/assurance-profile-v2.schema.json",
        "schemas/assurance-invariant.schema.json",
        "schemas/aggregator-receipt.schema.json",
        "schemas/claim-registry-v2.schema.json",
    ):
        schema = load_json(relative)
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            fail(f"unexpected JSON Schema dialect: {relative}")

    envelope = load_json("examples/evidence-envelope.example.json")
    required = {
        "schema_version", "repository", "revision", "producer", "policy_identity",
        "started_at", "finished_at", "outcome", "claims_evaluated", "artifacts", "limitations",
    }
    missing = sorted(required - envelope.keys())
    if missing:
        fail(f"evidence example missing keys: {', '.join(missing)}")
    if envelope.get("schema_version") != "assurance-evidence/v1":
        fail("evidence example has an unsupported schema_version")
    if not REVISION.fullmatch(str(envelope.get("revision", ""))):
        fail("evidence example revision is not a 40-64 character lowercase hex digest")
    if envelope.get("outcome") not in ALLOWED_OUTCOMES:
        fail("evidence example outcome is not in the controlled vocabulary")
    producer = envelope.get("producer", {})
    if not isinstance(producer, dict) or not DIGEST.fullmatch(str(producer.get("workflow_digest", ""))):
        fail("evidence example producer.workflow_digest is invalid")
    if not DIGEST.fullmatch(str(envelope.get("policy_identity", ""))):
        fail("evidence example policy_identity is invalid")
    for artifact in envelope.get("artifacts", []):
        if not isinstance(artifact, dict) or not DIGEST.fullmatch(str(artifact.get("digest", ""))):
            fail("evidence example contains an invalid artifact digest")

    profile = load_json("policy/research-release-v2.json")
    if profile.get("schema_version") != "assurance-profile/v2":
        fail("research-release-v2 has an unsupported schema_version")
    if profile.get("revision_binding") != "exact_commit" or profile.get("failure_posture") != "fail_closed":
        fail("research-release-v2 must bind exact commits and fail closed")
    binding = profile.get("digest_binding", {})
    expected_program = file_digest("assurance_ci/aggregate.py")
    expected_invariants = file_digest("policy/invariants.yaml")
    if binding.get("aggregator_program_digest") != expected_program:
        fail("research-release-v2 aggregator program digest is stale")
    if binding.get("invariant_bundle_digest") != expected_invariants:
        fail("research-release-v2 invariant bundle digest is stale")

    profile_identity = canonical_digest(profile)
    fixture_paths = (
        "tests/fixtures/passed-evidence-set.json",
        "tests/fixtures/known-bad-stale-evidence.json",
        "tests/fixtures/known-bad-revision-mismatch.json",
    )
    for relative in fixture_paths:
        evidence_set = load_json_value(relative)
        if not isinstance(evidence_set, list) or not evidence_set:
            fail(f"evidence fixture must be a non-empty array: {relative}")
            continue
        for index, item in enumerate(evidence_set):
            if not isinstance(item, dict) or item.get("schema_version") != "assurance-evidence/v2":
                fail(f"invalid v2 envelope at {relative}[{index}]")
                continue
            if item.get("policy_identity") != profile_identity:
                fail(f"profile identity mismatch at {relative}[{index}]")
            if item.get("outcome") not in ALLOWED_OUTCOMES:
                fail(f"invalid outcome at {relative}[{index}]")
            attestation = item.get("attestation", {})
            if not DIGEST.fullmatch(str(attestation.get("bundle_digest", ""))):
                fail(f"invalid attestation digest at {relative}[{index}]")

    environment_example = load_json("examples/environment-attestation.example.json")
    if environment_example.get("schema_version") != "assurance-evidence/v2":
        fail("environment attestation example must use assurance-evidence/v2")
    if not isinstance(environment_example.get("environment"), dict):
        fail("environment attestation example is missing environment-bound evidence")

    receipt_example = load_json("examples/aggregator-receipt.example.json")
    if receipt_example.get("schema_version") != "aggregator-receipt/v1":
        fail("aggregator receipt example has an unsupported schema_version")
    if receipt_example.get("decision") != "PASSED" or receipt_example.get("reason_codes") != []:
        fail("passing aggregator receipt example must be PASSED without reason codes")
    if receipt_example.get("profile_identity") != profile_identity:
        fail("aggregator receipt example is not bound to research-release-v2")

    claims = load_json("registry/claims-v2.json")
    claim_items = claims.get("claims", [])
    claim_ids = [item.get("id") for item in claim_items if isinstance(item, dict)]
    if len(claim_ids) != len(set(claim_ids)):
        fail("claim registry v2 contains duplicate claim IDs")
    for item in claim_items:
        if not item.get("belief_history"):
            fail(f"claim has no belief history: {item.get('id')}")
        if "supersedes" not in item or "valid_until" not in item:
            fail(f"claim lacks supersession or temporal validity fields: {item.get('id')}")

    controls = load_json("registry/known-bad-revisions.json")
    for control in controls.get("controls", []):
        fixture = ROOT / str(control.get("fixture", ""))
        if not fixture.is_file():
            fail(f"known-bad control fixture is missing: {control.get('id')}")
        if control.get("expected_decision") != "BLOCKED":
            fail(f"known-bad control must expect BLOCKED: {control.get('id')}")


def validate_controlled_text() -> None:
    expectations = {
        "policy/research-release-v1.yaml": [
            "revision_binding: exact_commit",
            "failure_posture: fail_closed",
            "FAILED: block",
            "BLOCKED: block",
            "INCONCLUSIVE: block",
            "NOT_APPLICABLE: require_signed_applicability_decision",
        ],
        "registry/claims.yaml": ["ACI-CLAIM-001", "ACI-CLAIM-002", "ACI-CLAIM-003", "ACI-CLAIM-004"],
        "registry/findings.yaml": ["ACI-FIND-001", "scripts/validate_repository.py"],
        "docs/architecture/ASSURANCE_CI_ARCHITECTURE.md": ["REMORA-ACA-001", "Version:** 1.0"],
        "policy/invariants.yaml": [
            "ACI-INV-001", "ACI-INV-002", "ACI-INV-003", "ACI-INV-004", "ACI-INV-005", "ACI-INV-006",
            "language: assurance-expression/v1", "failure_treatment: block",
        ],
        "docs/architecture/HARDENING_V1_1.md": [
            "Formal invariants", "Cryptographic trust boundary", "environment-bound evidence", "AI-generated oracle policy",
        ],
        "docs/THREAT_MODEL.md": ["Deliberate bypass scenarios", "Explicit limitations"],
    }
    for relative, tokens in expectations.items():
        try:
            text = (ROOT / relative).read_text(encoding="utf-8")
        except OSError as exc:
            fail(f"cannot read {relative}: {exc}")
            continue
        for token in tokens:
            if token not in text:
                fail(f"required contract token missing from {relative}: {token}")


def validate_markdown_links() -> None:
    for document in ROOT.rglob("*.md"):
        text = document.read_text(encoding="utf-8")
        for target in LOCAL_MD_LINK.findall(text):
            clean = target.split("#", 1)[0].strip().replace("%20", " ")
            if not clean:
                continue
            resolved = (document.parent / clean).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                fail(f"link escapes repository root in {document.relative_to(ROOT)}: {target}")
                continue
            if not resolved.exists():
                fail(f"broken local link in {document.relative_to(ROOT)}: {target}")


def validate_binary_artifacts() -> None:
    for relative in (
        "docs/figures/assurance-ci-enforcement-architecture.png",
        "docs/figures/assurance-ratchet.png",
    ):
        path = ROOT / relative
        if path.is_file() and path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            fail(f"invalid PNG signature: {relative}")

    release = ROOT / "docs/releases/Assurance_CI_Architecture_REMORA_v1.0.docx"
    if release.is_file():
        if not zipfile.is_zipfile(release):
            fail("versioned Word release is not a valid ZIP-based DOCX")
        else:
            with zipfile.ZipFile(release) as archive:
                required_parts = {"[Content_Types].xml", "word/document.xml"}
                if not required_parts.issubset(archive.namelist()):
                    fail("versioned Word release is missing required DOCX parts")


def validate_checksum_manifest() -> None:
    manifest = ROOT / "checksums/SHA256SUMS"
    if not manifest.is_file():
        return
    for line_number, raw in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        parts = raw.split(maxsplit=1)
        if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[0]):
            fail(f"invalid checksum line {line_number}")
            continue
        relative = parts[1].lstrip("* ")
        path = ROOT / relative
        if not path.is_file():
            fail(f"checksum target missing: {relative}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != parts[0]:
            fail(f"checksum mismatch: {relative}")


def validate_no_placeholders() -> None:
    extensions = {".md", ".json", ".yaml", ".yml", ".py", ".cff"}
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix in extensions:
            text = path.read_text(encoding="utf-8")
            if ("_PLACE" + "HOLDER") in text:
                fail(f"unresolved placeholder in {path.relative_to(ROOT)}")


def main() -> int:
    require_paths()
    validate_json_contracts()
    validate_controlled_text()
    validate_markdown_links()
    validate_binary_artifacts()
    validate_checksum_manifest()
    validate_no_placeholders()

    if ERRORS:
        print("Assurance repository validation: FAILED")
        for error in ERRORS:
            print(f"- {error}")
        return 1

    print(f"Assurance repository validation: PASSED ({len(REQUIRED_PATHS)} required artifacts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

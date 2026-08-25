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
    "docs/architecture/ASSURANCE_CI_ARCHITECTURE.md",
    "docs/adr/0001-assurance-ci-as-a-first-class-subsystem.md",
    "docs/figures/assurance-ci-enforcement-architecture.png",
    "docs/figures/assurance-ratchet.png",
    "docs/releases/Assurance_CI_Architecture_REMORA_v1.0.docx",
    "schemas/assurance-evidence-envelope.schema.json",
    "schemas/assurance-profile.schema.json",
    "policy/research-release-v1.yaml",
    "registry/claims.yaml",
    "registry/findings.yaml",
    "examples/evidence-envelope.example.json",
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


def validate_json_contracts() -> None:
    for relative in (
        "schemas/assurance-evidence-envelope.schema.json",
        "schemas/assurance-profile.schema.json",
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


def main() -> int:
    require_paths()
    validate_json_contracts()
    validate_controlled_text()
    validate_markdown_links()
    validate_binary_artifacts()
    validate_checksum_manifest()

    if ERRORS:
        print("Assurance repository validation: FAILED")
        for error in ERRORS:
            print(f"- {error}")
        return 1

    print(f"Assurance repository validation: PASSED ({len(REQUIRED_PATHS)} required artifacts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

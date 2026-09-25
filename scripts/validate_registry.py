#!/usr/bin/env python3
"""Subject/resource registry integrity validator.

Version: 0.2.0
Uses only the Python standard library.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SUBJECTS_PATH = ROOT / "data" / "subjects.json"
RESOURCES_PATH = ROOT / "data" / "resources.json"

ALLOWED_TYPES = {
    "foundation_textbook",
    "core_textbook",
    "reference_textbook",
    "advanced_textbook",
    "review_article",
    "authoritative_reference",
    "open_academic_resource",
}

ALLOWED_STAGES = {"foundation", "core", "intermediate", "advanced", "specialized"}

DISALLOWED_TYPES = {
    "laboratory_manual",
    "protocol",
    "sop",
    "hands_on_training",
    "practical_course",
    "wet_lab_guide",
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_https(value: str, label: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{label} must be an absolute HTTPS URL: {value!r}")


def main() -> None:
    subjects = load_json(SUBJECTS_PATH).get("subjects", [])
    resources = load_json(RESOURCES_PATH).get("resources", [])

    subject_ids = [subject["id"] for subject in subjects]
    if len(subject_ids) != len(set(subject_ids)):
        raise ValueError("Duplicate subject IDs found.")

    resource_ids = [resource["id"] for resource in resources]
    if len(resource_ids) != len(set(resource_ids)):
        raise ValueError("Duplicate resource IDs found.")

    subject_concepts: dict[str, set[str]] = {}
    subject_branches: dict[str, set[str]] = {}

    for subject in subjects:
        sid = subject["id"]
        if subject.get("scope") != "theoretical":
            raise ValueError(f"Subject {sid} is not theory-only.")

        stages = set(subject.get("roadmap_stages", []))
        if not stages or not stages <= ALLOWED_STAGES:
            raise ValueError(f"Subject {sid} has invalid roadmap stages.")

        concept_ids = [item["id"] for item in subject.get("concepts", [])]
        branch_ids = [item["id"] for item in subject.get("branches", [])]

        if not concept_ids:
            raise ValueError(f"Subject {sid} has no concepts.")
        if len(concept_ids) != len(set(concept_ids)):
            raise ValueError(f"Duplicate concept IDs in {sid}.")
        if len(branch_ids) != len(set(branch_ids)):
            raise ValueError(f"Duplicate branch IDs in {sid}.")

        subject_concepts[sid] = set(concept_ids)
        subject_branches[sid] = set(branch_ids)

    for resource in resources:
        rid = resource["id"]
        sid = resource["subject_id"]

        if sid not in subject_concepts:
            raise ValueError(f"{rid} references unknown subject {sid}.")

        rtype = resource.get("resource_type")
        if rtype in DISALLOWED_TYPES or rtype not in ALLOWED_TYPES:
            raise ValueError(f"{rid} has unsupported resource_type {rtype!r}.")

        if resource.get("learning_stage") not in ALLOWED_STAGES:
            raise ValueError(f"{rid} has invalid learning_stage.")

        if resource.get("theory_only") is not True:
            raise ValueError(f"{rid} violates the theory-only rule.")

        guidance = resource.get("student_guidance_fa", {})
        required_guidance = {"best_for", "why", "how_to_use", "next_step"}
        missing_guidance = [
            field for field in required_guidance
            if not isinstance(guidance.get(field), str) or not guidance.get(field).strip()
        ]
        if missing_guidance:
            raise ValueError(
                f"{rid} is missing Persian student guidance fields: {sorted(missing_guidance)}"
            )

        require_https(resource.get("publisher_url", ""), f"{rid} publisher_url")

        coverage = set(resource.get("coverage_concept_ids", []))
        if not coverage:
            raise ValueError(f"{rid} has no concept coverage.")

        unknown_concepts = coverage - subject_concepts[sid]
        if unknown_concepts:
            raise ValueError(f"{rid} references unknown concepts: {sorted(unknown_concepts)}")

        branches = set(resource.get("branch_ids", []))
        unknown_branches = branches - subject_branches[sid]
        if unknown_branches:
            raise ValueError(f"{rid} references unknown branches: {sorted(unknown_branches)}")

        if resource.get("learning_stage") == "specialized":
            if not branches:
                raise ValueError(f"{rid} is specialized but has no branch_ids.")
            branch_role = resource.get("branch_role")
            if branch_role not in {
                "branch_reference",
                "complementary_reference",
                "current_update",
            }:
                raise ValueError(f"{rid} has invalid or missing branch_role.")

        if rtype.endswith("textbook"):
            if not resource.get("isbn"):
                raise ValueError(f"{rid} textbook is missing ISBN.")
            if not resource.get("edition"):
                raise ValueError(f"{rid} textbook is missing edition.")
            if not resource.get("purchase_url"):
                raise ValueError(f"{rid} textbook is missing purchase_url.")
            require_https(resource["purchase_url"], f"{rid} purchase_url")
            cover = resource.get("cover", {})
            require_https(cover.get("url", ""), f"{rid} cover URL")

        if rtype == "review_article" and not resource.get("doi"):
            raise ValueError(f"{rid} review article is missing DOI.")

    for subject in subjects:
        sid = subject["id"]
        declared_branches = subject_branches[sid]
        covered_branches = {
            branch
            for resource in resources
            if resource["subject_id"] == sid
            and resource.get("learning_stage") == "specialized"
            for branch in resource.get("branch_ids", [])
        }
        uncovered = declared_branches - covered_branches
        if uncovered:
            raise ValueError(
                f"Subject {sid} has specialized branches without resources: "
                f"{sorted(uncovered)}"
            )

    print(
        f"Registry validation passed: {len(subjects)} subject(s), "
        f"{len(resources)} resource(s), all declared branches covered."
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Subject, resource-identity, and roadmap-placement integrity validator.

Version: 0.5.0
Uses only the Python standard library.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SUBJECTS_PATH = ROOT / "data" / "subjects.json"
RESOURCES_PATH = ROOT / "data" / "resources.json"
PLACEMENTS_PATH = ROOT / "data" / "placements.json"

ALLOWED_RESOURCE_TYPES = {
    "textbook",
    "review_article",
    "open_academic_resource",
    "book_chapter",
    "authoritative_reference",
}

ALLOWED_STAGES = {"foundation", "core", "intermediate", "advanced", "specialized"}
ALLOWED_BRANCH_ROLES = {"branch_reference", "complementary_reference", "current_update"}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_https(value: str, label: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{label} must be an absolute HTTPS URL: {value!r}")


def require_nonempty_string(value: object, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string.")


def assert_unique(values: list[str], label: str) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    if duplicates:
        raise ValueError(f"Duplicate {label}: {sorted(duplicates)}")


def main() -> None:
    subjects = load_json(SUBJECTS_PATH).get("subjects", [])
    resources = load_json(RESOURCES_PATH).get("resources", [])
    placements = load_json(PLACEMENTS_PATH).get("placements", [])

    subject_ids = [subject["id"] for subject in subjects]
    resource_ids = [resource["id"] for resource in resources]
    placement_ids = [placement["id"] for placement in placements]

    assert_unique(subject_ids, "subject IDs")
    assert_unique(resource_ids, "resource IDs")
    assert_unique(placement_ids, "placement IDs")

    resource_id_set = set(resource_ids)
    subject_id_set = set(subject_ids)

    dois = [resource["doi"].lower() for resource in resources if resource.get("doi")]
    isbns = [resource["isbn"].replace("-", "") for resource in resources if resource.get("isbn")]
    assert_unique(dois, "resource DOIs")
    assert_unique(isbns, "resource ISBNs")

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
        assert_unique(concept_ids, f"concept IDs in {sid}")
        assert_unique(branch_ids, f"branch IDs in {sid}")

        subject_concepts[sid] = set(concept_ids)
        subject_branches[sid] = set(branch_ids)

    for resource in resources:
        rid = resource["id"]
        rtype = resource.get("resource_type")

        if rtype not in ALLOWED_RESOURCE_TYPES:
            raise ValueError(f"{rid} has unsupported resource_type {rtype!r}.")
        if resource.get("theory_only") is not True:
            raise ValueError(f"{rid} violates the theory-only rule.")

        require_nonempty_string(resource.get("title"), f"{rid} title")
        require_https(resource.get("publisher_url", ""), f"{rid} publisher_url")

        if rtype == "textbook":
            for field in ("isbn", "edition", "purchase_url"):
                require_nonempty_string(resource.get(field), f"{rid} {field}")
            require_https(resource["purchase_url"], f"{rid} purchase_url")
            cover = resource.get("cover", {})
            require_https(cover.get("url", ""), f"{rid} cover URL")

        if rtype in {"review_article", "book_chapter"}:
            require_nonempty_string(resource.get("doi"), f"{rid} DOI")

    placement_pairs: list[str] = []

    for placement in placements:
        pid = placement["id"]
        rid = placement["resource_id"]
        sid = placement["subject_id"]

        if rid not in resource_id_set:
            raise ValueError(f"{pid} references unknown resource {rid}.")
        if sid not in subject_id_set:
            raise ValueError(f"{pid} references unknown subject {sid}.")

        placement_pairs.append(f"{sid}::{rid}")

        stage = placement.get("learning_stage")
        if stage not in ALLOWED_STAGES:
            raise ValueError(f"{pid} has invalid learning_stage {stage!r}.")

        coverage = set(placement.get("coverage_concept_ids", []))
        if not coverage:
            raise ValueError(f"{pid} has no concept coverage.")
        unknown_concepts = coverage - subject_concepts[sid]
        if unknown_concepts:
            raise ValueError(f"{pid} references unknown concepts: {sorted(unknown_concepts)}")

        branches = set(placement.get("branch_ids", []))
        unknown_branches = branches - subject_branches[sid]
        if unknown_branches:
            raise ValueError(f"{pid} references unknown branches: {sorted(unknown_branches)}")

        if stage == "specialized":
            if not branches:
                raise ValueError(f"{pid} is specialized but has no branch_ids.")
            if placement.get("branch_role") not in ALLOWED_BRANCH_ROLES:
                raise ValueError(f"{pid} has invalid or missing branch_role.")

        guidance = placement.get("student_guidance_fa", {})
        for field in ("best_for", "why", "how_to_use", "next_step"):
            require_nonempty_string(guidance.get(field), f"{pid} student_guidance_fa.{field}")

        require_nonempty_string(placement.get("selection_rationale"), f"{pid} selection_rationale")

    assert_unique(placement_pairs, "subject/resource placement pairs")

    for subject in subjects:
        sid = subject["id"]
        declared_branches = subject_branches[sid]
        covered_branches = {
            branch
            for placement in placements
            if placement["subject_id"] == sid
            and placement.get("learning_stage") == "specialized"
            for branch in placement.get("branch_ids", [])
        }
        uncovered = declared_branches - covered_branches
        if uncovered:
            raise ValueError(
                f"Subject {sid} has specialized branches without resources: "
                f"{sorted(uncovered)}"
            )

        status = subject.get("status")
        if status not in {"in_progress", "complete_candidate", "complete"}:
            raise ValueError(f"Subject {sid} has invalid or missing status {status!r}.")

        criteria = subject.get("completion_criteria", {})
        expected_general = criteria.get("general_roadmap_resources")
        expected_branches = criteria.get("specialized_branches_required")

        if not isinstance(expected_general, int) or expected_general < 1:
            raise ValueError(f"Subject {sid} has invalid general_roadmap_resources.")
        if expected_branches != len(declared_branches):
            raise ValueError(
                f"Subject {sid} completion criteria expect {expected_branches} branches "
                f"but {len(declared_branches)} are declared."
            )

        general_count = sum(
            1 for placement in placements
            if placement["subject_id"] == sid
            and placement.get("learning_stage") != "specialized"
        )
        if status in {"complete_candidate", "complete"} and general_count < expected_general:
            raise ValueError(
                f"Subject {sid} has {general_count} general roadmap placements; "
                f"{expected_general} required for completion."
            )

        if status == "complete" and not subject.get("completed_on"):
            raise ValueError(f"Completed subject {sid} is missing completed_on.")

    print(
        f"Registry validation passed: {len(subjects)} subject(s), "
        f"{len(resources)} unique resource(s), {len(placements)} placement(s), "
        "all declared branches covered."
    )


if __name__ == "__main__":
    main()

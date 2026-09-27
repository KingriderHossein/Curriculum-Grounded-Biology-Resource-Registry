#!/usr/bin/env python3
"""Subject, resource-identity, and roadmap-placement integrity validator.

Version: 0.6.0
Uses only the Python standard library.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SUBJECTS_PATH = ROOT / "data" / "subjects.json"
RESOURCES_PATH = ROOT / "data" / "resources.json"
PLACEMENTS_PATH = ROOT / "data" / "placements.json"
README_PATH = ROOT / "README.md"

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


DIGIT_TRANSLATION = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)


def parse_localized_int(value: str, label: str) -> int:
    normalized = value.translate(DIGIT_TRANSLATION)
    match = re.search(r"\d+", normalized)
    if not match:
        raise ValueError(f"{label} does not contain a numeric value: {value!r}")
    return int(match.group())


def normalize_subject_label(value: str) -> str:
    return " ".join(
        value.replace("\u2066", "").replace("\u2069", "").split()
    )


def validate_completed_subject_table(subjects: list[dict], placements: list[dict]) -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    heading = "## درس‌های تکمیل‌شده"
    heading_pos = readme.find(heading)
    if heading_pos == -1:
        raise ValueError("README is missing the completed-subject table heading.")

    section = readme[heading_pos + len(heading):]
    section_end = section.find("\n---")
    if section_end == -1:
        raise ValueError("README completed-subject table has no closing horizontal rule.")
    table_text = section[:section_end]

    rows: list[dict] = []
    for raw_line in table_text.splitlines():
        line = raw_line.strip()
        if not line.startswith("| ["):
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 4:
            raise ValueError(f"Malformed README completed-subject row: {line}")

        link_match = re.fullmatch(
            r"\[(?P<label>.+?)\]\((?P<path>subjects/[^)]+/README\.md)\)",
            cells[0],
        )
        if not link_match:
            raise ValueError(f"Malformed README subject link: {cells[0]!r}")

        rows.append(
            {
                "label": link_match.group("label"),
                "path": link_match.group("path"),
                "general": parse_localized_int(cells[1], f"{cells[0]} general-resource count"),
                "branches": parse_localized_int(cells[2], f"{cells[0]} branch count"),
                "total": parse_localized_int(cells[3], f"{cells[0]} placement count"),
            }
        )

    if not rows:
        raise ValueError("README completed-subject table contains no subject rows.")

    paths = [row["path"] for row in rows]
    assert_unique(paths, "README completed-subject paths")

    completed_subjects = [subject for subject in subjects if subject.get("status") == "complete"]
    expected_by_path: dict[str, dict] = {}
    for subject in completed_subjects:
        slug = subject["id"].lower().replace("_", "-")
        expected_path = f"subjects/{slug}/README.md"
        expected_by_path[expected_path] = subject
        if not (ROOT / expected_path).is_file():
            raise ValueError(
                f"Completed subject {subject['id']} has no roadmap file at {expected_path}."
            )

    actual_by_path = {row["path"]: row for row in rows}
    missing = sorted(set(expected_by_path) - set(actual_by_path))
    extra = sorted(set(actual_by_path) - set(expected_by_path))
    if missing:
        raise ValueError(
            "README completed-subject table is missing canonical subject row(s): "
            + ", ".join(missing)
        )
    if extra:
        raise ValueError(
            "README completed-subject table contains non-canonical or non-complete row(s): "
            + ", ".join(extra)
        )

    placements_by_subject: dict[str, list[dict]] = {}
    for placement in placements:
        placements_by_subject.setdefault(placement["subject_id"], []).append(placement)

    for path, subject in expected_by_path.items():
        sid = subject["id"]
        row = actual_by_path[path]
        subject_placements = placements_by_subject.get(sid, [])
        expected_general = sum(
            1 for placement in subject_placements
            if placement.get("learning_stage") != "specialized"
        )
        expected_branches = len(subject.get("branches", []))
        expected_total = len(subject_placements)
        expected_label = normalize_subject_label(
            f"{subject['fa_name']} {subject['en_name']}"
        )
        actual_label = normalize_subject_label(row["label"])

        if actual_label != expected_label:
            raise ValueError(
                f"README completed-subject label mismatch for {sid}: "
                f"{actual_label!r} != canonical {expected_label!r}."
            )
        if row["general"] != expected_general:
            raise ValueError(
                f"{sid}: README says {row['general']} general resources, "
                f"canonical registry has {expected_general}."
            )
        if row["branches"] != expected_branches:
            raise ValueError(
                f"{sid}: README says {row['branches']} branches, "
                f"canonical registry has {expected_branches}."
            )
        if row["total"] != expected_total:
            raise ValueError(
                f"{sid}: README says {row['total']} placements, "
                f"canonical registry has {expected_total}."
            )

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

    validate_completed_subject_table(subjects, placements)

    print(
        f"Registry validation passed: {len(subjects)} subject(s), "
        f"{len(resources)} unique resource(s), {len(placements)} placement(s), "
        "all declared branches covered."
    )


if __name__ == "__main__":
    main()

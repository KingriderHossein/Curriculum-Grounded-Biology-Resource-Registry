#!/usr/bin/env python3
"""Registry integrity validator.

Version: 0.1.0
Uses only the Python standard library.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
COURSES_PATH = ROOT / "data" / "courses.json"
RESOURCES_PATH = ROOT / "data" / "resources.json"

ALLOWED_TYPES = {
    "core_textbook",
    "reference_textbook",
    "advanced_textbook",
    "review_article",
    "authoritative_reference",
    "open_academic_resource",
}

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
    course_data = load_json(COURSES_PATH)
    resource_data = load_json(RESOURCES_PATH)

    courses = course_data.get("courses", [])
    resources = resource_data.get("resources", [])

    course_ids = [course["id"] for course in courses]
    if len(course_ids) != len(set(course_ids)):
        raise ValueError("Duplicate course IDs found.")

    resource_ids = [resource["id"] for resource in resources]
    if len(resource_ids) != len(set(resource_ids)):
        raise ValueError("Duplicate resource IDs found.")

    course_topics: dict[str, set[str]] = {}

    for course in courses:
        if course.get("delivery") != "theoretical":
            raise ValueError(f"Course {course['id']} is not theory-only.")

        topic_ids = [topic["id"] for topic in course.get("topics", [])]
        if len(topic_ids) != len(set(topic_ids)):
            raise ValueError(f"Duplicate topic IDs in course {course['id']}.")

        if not topic_ids:
            raise ValueError(f"Course {course['id']} has no syllabus topics.")

        course_topics[course["id"]] = set(topic_ids)

        source = course.get("curriculum_source", {})
        require_https(source.get("url", ""), f"{course['id']} curriculum source")

    for resource in resources:
        rid = resource["id"]
        cid = resource["course_id"]

        if cid not in course_topics:
            raise ValueError(f"{rid} references unknown course {cid}.")

        rtype = resource.get("resource_type")
        if rtype in DISALLOWED_TYPES or rtype not in ALLOWED_TYPES:
            raise ValueError(f"{rid} has unsupported resource_type {rtype!r}.")

        if resource.get("theory_only") is not True:
            raise ValueError(f"{rid} violates the theory-only rule.")

        require_https(resource.get("publisher_url", ""), f"{rid} publisher_url")

        coverage = set(resource.get("coverage_topic_ids", []))
        if not coverage:
            raise ValueError(f"{rid} has no syllabus coverage.")

        unknown_topics = coverage - course_topics[cid]
        if unknown_topics:
            raise ValueError(
                f"{rid} references unknown topics: {sorted(unknown_topics)}"
            )

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

    print(
        f"Registry validation passed: {len(courses)} course(s), "
        f"{len(resources)} resource(s)."
    )


if __name__ == "__main__":
    main()

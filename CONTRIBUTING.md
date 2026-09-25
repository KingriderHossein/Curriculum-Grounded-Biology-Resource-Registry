# Contributing

Contributions are welcome, but this is a curated scientific registry rather than an unrestricted link list.

## Before opening a PR

Confirm that the proposed resource:

1. belongs to an existing theoretical course or comes with a justified course proposal;
2. maps to one or more syllabus topic IDs;
3. is theory-only;
4. has stable bibliographic metadata;
5. has an authoritative source URL;
6. does not duplicate an existing edition/resource.

## Adding a book

Provide:

- title;
- authors/editors;
- edition;
- publication year;
- publisher;
- ISBN;
- official publisher URL;
- official purchase URL when available;
- cover URL;
- resource role;
- mapped syllabus topics;
- a concise selection rationale.

## Adding a review article

Provide:

- title;
- authors;
- journal;
- year;
- DOI and/or PMID;
- publisher/journal URL;
- mapped syllabus topics;
- why the review adds current value beyond the textbook.

## Theory-only rule

Do **not** submit:

- protocols;
- laboratory manuals;
- practical technique tutorials;
- SOPs;
- wet-lab workflows;
- instrument training.

Conceptual discussion of experimental methods is acceptable only when it is part of a theoretical syllabus.

## Review standard

A maintainer should be able to answer:

> Why this source, for this topic, at this degree level?

If the answer is not visible from the record and evidence, the contribution is not ready.

## Data validation

Run:

```bash
python scripts/validate_registry.py
```

A PR should keep the registry validator green.

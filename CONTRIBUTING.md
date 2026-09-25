# Contributing

Contributions are welcome, but this is a curated scientific roadmap rather than an unrestricted link list.

## Before opening a PR

Before creating anything, check whether the ISBN or DOI already exists in `data/resources.json`.

- If the resource already exists, add only a new Placement in `data/placements.json`.
- If it is new, add the bibliographic identity once in `data/resources.json`, then add its Placement.

Confirm that each Placement:

1. belongs to an existing Subject or comes with a justified Subject proposal;
2. has a clear learning stage;
3. maps to one or more concept IDs;
4. maps to a specialized branch when appropriate;
5. points to a theory-only resource;
6. explains why the resource belongs at that exact place in the roadmap;
7. includes Persian student guidance.

## Adding a new book identity

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
- bibliographic metadata only once in `data/resources.json`.

Then create a Placement containing:

- Subject ID;
- learning stage;
- concept coverage;
- branch mapping when specialized;
- concise selection rationale;
- Persian student guidance for: who it is for, why it is selected, how to use it, and what to read next.

## Adding a review article

Provide:

- Subject ID;
- title;
- authors;
- journal;
- year;
- DOI and/or PMID;
- journal URL;
- learning stage;
- concept/branch mapping;
- why it adds value beyond the broad textbooks.

## Theory-only rule

Do **not** submit protocols, laboratory manuals, practical technique tutorials, SOPs, wet-lab workflows or instrument training.

## Review question

A maintainer should be able to answer:

> Why this source, at this learning stage, for this concept or branch?

If that is not clear from the record, the contribution is not ready.

## Data validation

Run:

```bash
python scripts/validate_registry.py
```

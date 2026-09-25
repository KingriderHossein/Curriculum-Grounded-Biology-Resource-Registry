# Contributing

Contributions are welcome, but this is a curated scientific roadmap rather than an unrestricted link list.

## Before opening a PR

Confirm that the proposed resource:

1. belongs to an existing Subject or comes with a justified Subject proposal;
2. has a clear learning stage;
3. maps to one or more concept IDs;
4. maps to a specialized branch when appropriate;
5. is theory-only;
6. has stable bibliographic metadata;
7. has an authoritative source URL;
8. does not duplicate an existing edition/resource.

## Adding a book

Provide:

- Subject ID;
- title;
- authors/editors;
- edition;
- publication year;
- publisher;
- ISBN;
- official publisher URL;
- official purchase URL when available;
- cover URL;
- learning stage;
- concept coverage;
- branch mapping when specialized;
- concise selection rationale;
- what should be read before/after it when relevant.

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

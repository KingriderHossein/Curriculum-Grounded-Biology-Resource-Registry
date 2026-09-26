# Project Specification

## Purpose

Build a maintainable, community-expandable registry of high-quality **theoretical biology learning roadmaps**, organized by scientific subject rather than by university major.

## Primary object

The authoritative project model is:

`Subject → Learning stage / Concept / Branch → Placement → Resource`

A subject exists once. A scientific resource also exists once globally. Subject-specific learning stage, concept coverage, branch, rationale and Persian student guidance live in a separate Placement record. Degrees, majors, countries, universities and curricula may optionally map to a subject, but they never duplicate or own the subject.

## Learning stages

Every mature subject roadmap should distinguish:

1. **Foundation** — prerequisites and first exposure;
2. **Core** — the main textbook/resource sequence for learning the subject properly;
3. **Intermediate** — a stronger second pass and broader reference layer;
4. **Advanced** — deeper mechanistic or research-level references;
5. **Specialized branches** — subdomains that diverge inside the subject and need their own references.

A learner should be able to see not only *what to read*, but *in what order* and *why*.

## In scope

- theoretical textbooks;
- authoritative reference books;
- open academic textbooks/resources;
- recent high-quality review articles for fast-moving areas;
- subject-specific handbooks when conceptually oriented;
- official publisher/journal links;
- purchase links when available;
- book-cover thumbnails for recognition and navigation;
- optional curriculum mappings.

## Out of scope

- laboratory manuals;
- experimental protocols;
- SOPs;
- wet-lab tutorials;
- hands-on technique training;
- instrument-operation guides;
- practical-course resource lists.

## Resource-selection goal

The registry is not a bibliography dump.

For each resource, the project should answer:

- At what learning stage is it useful?
- Which concept areas does it cover?
- Is it broad or specialized?
- Why is it preferred at that stage?
- What should a learner read before or after it?

## Success criteria for a subject

A subject is considered meaningfully implemented when:

1. its prerequisite/foundation layer is identified;
2. a coherent Core → Intermediate → Advanced sequence exists;
3. major specialized branches are separated;
4. resources are mapped to stages and concept areas;
5. bibliographic metadata and authoritative URLs are verified;
6. cover presentation is consistent, matches the selected book/edition, and successfully renders on the real GitHub page;
7. theory-only validation passes;
8. contributors can extend a branch without duplicating the subject.

## Optional curriculum layer

Curriculum mappings may later answer which part of a roadmap corresponds to a named course or degree. They are secondary navigation metadata, not the scientific backbone.

## Reference implementations

The current reference-quality subjects are:

- **Cell Biology / زیست‌شناسی سلولی**
- **Biochemistry / بیوشیمی**
- **Genetics / ژنتیک**
- **Molecular Biology / زیست‌شناسی مولکولی**
- **Microbiology / میکروبیولوژی**
- **Evolutionary Biology / زیست‌شناسی تکاملی**
- **Ecology / اکولوژی**
- **Plant Biology / زیست‌شناسی گیاهی**
- **Developmental Biology / زیست‌شناسی تکوینی**
- **Immunology / ایمونولوژی**
- **Animal Physiology / فیزیولوژی جانوری**
- **Bioinformatics / بیوانفورماتیک**

New subjects should reuse this architecture instead of introducing a parallel resource model.

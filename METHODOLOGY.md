# Methodology

## 1. Curriculum first

Resources are selected only after a course and its syllabus topics are defined.

Preferred curriculum provenance, in order:

1. official ministry / curriculum authority;
2. official university-hosted copy of the approved curriculum;
3. clearly identifiable mirror of the approved document;
4. secondary description only as a temporary discovery aid.

Tier 3 material must be marked as provisional provenance until an official host is located. Secondary descriptions are not sufficient to declare a curriculum verified.

## 2. Theory-only gate

Allowed resource categories:

- `core_textbook`
- `reference_textbook`
- `advanced_textbook`
- `review_article`
- `authoritative_reference`
- `open_academic_resource`

Explicitly excluded:

- laboratory manuals
- protocols
- SOPs
- hands-on training
- practical-course guides
- wet-lab tutorials

## 3. Resource selection

A resource is evaluated on:

### Scientific authority
Publisher/journal reputation, author expertise, peer review where applicable, and bibliographic traceability.

### Curriculum coverage
The resource must map to explicit syllabus topic IDs. Broad relevance is not enough.

### Currency
Use the latest **published and available** edition when it is scientifically and pedagogically suitable. A forthcoming edition is not treated as the current core edition.

### Pedagogical fit
A technically excellent research monograph can still be a poor core source for a B.Sc. course. The intended learner level matters.

### Stability and verifiability
Prefer ISBN, DOI, PMID, official publisher pages, journal pages, and stable metadata.

## 4. Resource roles

- **Core**: best starting source for the course level and syllabus.
- **Reference**: deeper or more detailed source; useful alongside the core.
- **Advanced update**: recent peer-reviewed review that updates rapidly moving areas.

No numeric "best book" score is used. The registry records *why* a source fits a role.

## 5. Book-cover policy

Book covers are presentation metadata, not scientific evidence.

For the pilot:

- thumbnails are hot-linked by ISBN from Open Library;
- publisher pages remain the authoritative bibliographic/purchase source;
- no full book content is stored;
- local cover caching may be added later only with a clear source and rights policy.

If a cover fails, the resource record remains valid.

## 6. Verification states

- `candidate`: submitted but not reviewed;
- `verified`: bibliographic identity, source, role, and syllabus mapping checked;
- `provisional`: usable but one provenance field still needs stronger evidence;
- `outdated`: superseded or no longer recommended.

## 7. Recency policy

"Newest" does not automatically mean "best." For textbooks, the latest available edition is preferred unless there is a documented reason not to use it. For fast-moving topics, recent high-quality review literature supplements the textbook.

## 8. Audit trail

Each record stores a `verified_on` date and source URLs. Changes to edition, role, syllabus mapping, or verification status should be reviewable in Git history.

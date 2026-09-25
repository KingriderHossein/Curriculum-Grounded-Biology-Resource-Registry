# Methodology

## 1. Subject first

The project begins from a scientific subject, not from a national curriculum or major.

For each subject:

1. define prerequisite knowledge;
2. define the Core conceptual spine;
3. define the Advanced layer;
4. identify specialized branches;
5. select resources for each stage;
6. update fast-moving branches with recent peer-reviewed reviews.

Curricula may be mapped later as optional metadata.

## 2. Theory-only gate

Allowed resource categories:

- `foundation_textbook`
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

A technique may be discussed conceptually only when it is necessary to understand the subject.

## 3. Roadmap placement

Every resource must have a `learning_stage`:

- `foundation`
- `core`
- `intermediate`
- `advanced`
- `specialized`

A resource may cover several concept areas, but it should have one primary learning role.

## 4. Resource selection

### Scientific authority
Publisher/journal reputation, author expertise, peer review where applicable, and bibliographic traceability.

### Pedagogical fit
The resource must fit the learner stage. A definitive research reference is not automatically a good first book.

### Concept coverage
Each resource maps to explicit concept IDs within its Subject.

### Currency
Use the latest published and available edition when scientifically and pedagogically suitable. Recent review literature supplements textbooks in rapidly moving areas.

### Stability and verifiability
Prefer ISBN, DOI, PMID, official publisher pages, journal pages, and stable academic URLs.

## 5. Resource roles

- **Foundation**: prerequisite or first-exposure material.
- **Core**: the main learning resource for the subject.
- **Intermediate / Reference**: broad reinforcement or second-pass depth.
- **Advanced**: deeper mechanistic and research-level coverage.
- **Specialized**: focused branch-level literature.

No numeric “best book” score is used. The registry records *why* a source belongs at a particular stage.

## 6. Specialized branches

A branch belongs inside the parent Subject when it is a specialization of that subject rather than a fully independent discipline.

Example for Cell Biology:

- membranes & transport;
- organelle biology & trafficking;
- nucleus & nucleocytoplasmic transport;
- signaling;
- cytoskeleton & mechanics;
- cell cycle;
- cell death & autophagy;
- adhesion & extracellular matrix;
- plant-cell structures.

Each branch can later receive its own Foundation/Core/Advanced references if the literature is deep enough.

## 7. Book-cover policy

Book covers are presentation metadata, not scientific evidence.

- use official publisher-hosted cover images when available;
- publisher pages remain the authoritative bibliographic/purchase source;
- do not store full book content;
- keep the cover source identity;
- local cover caching requires a clear rights/source policy.

## 8. Verification states

- `candidate`
- `verified`
- `provisional`
- `outdated`

## 9. Audit trail

Each record stores a verification date and source URLs. Changes to edition, learning stage, concept mapping, branch mapping or verification status remain reviewable in Git history.

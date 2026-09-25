# Methodology

## 1. Subject first

The project begins from a scientific subject, not from a national curriculum or major.

For each subject:

1. define prerequisite knowledge;
2. define the Core conceptual spine;
3. define the Intermediate layer;
4. define the Advanced layer;
5. identify specialized branches;
6. select resources for each stage;
7. update fast-moving branches with recent peer-reviewed reviews.

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

Explicitly excluded: laboratory manuals, protocols, SOPs, hands-on training, practical-course guides, and wet-lab tutorials.

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

For Cell Biology these include membranes, organelle biology, nucleus/transport, signaling, cytoskeleton, cell cycle, cell death/autophagy, adhesion/ECM, and plant-cell structures.

## 7. Book-cover policy

Book covers are presentation metadata, not scientific evidence. Prefer official publisher-hosted cover images; keep publisher pages as the bibliographic/purchase authority; do not store full book content.

## 8. Verification states

- `candidate`
- `verified`
- `provisional`
- `outdated`

## 9. Audit trail

Each record stores a verification date and source URLs. Changes to edition, learning stage, concept mapping, branch mapping or verification status remain reviewable in Git history.

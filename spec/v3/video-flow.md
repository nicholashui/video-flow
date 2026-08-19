# AI video generation pipeline v3

This document is the implementation baseline for the Video Flow v3 production
system.

**Version:** 3.0
**Status:** Implementation baseline
**Date:** August 19, 2026
**Supersedes:** [`../v2/video-flow.md`](../v2/video-flow.md), which superseded
`../v1/video-flow.md`

This specification defines a local-first, human-controlled system that turns a
structured storyline, shot instructions, and selected reference material into
multilingual, publication-ready video packages.

Version 2 established the right foundation: immutable artifacts, provider-neutral
adapters, four human gates, calibrated rather than invented quality thresholds,
and an editorial timeline that does not live inside a model. Version 3 keeps all
of that and fixes the layer v2 described but never specified — the **execution
model**. v2 asserted that the pipeline is resumable, surgically repairable,
concurrency-safe, and budget-bounded. It did not define the state machine,
dependency graph, approval-binding rules, locking discipline, or accounting
that make those properties real. An implementer following v2 would have to
invent all of them, and would probably invent them inconsistently.

Version 3 also corrects one ordering defect and one compliance omission that
would each have caused rework or takedown risk in production:

- v2 locks picture before localization. Because the same meaning takes
  materially different time to speak in English, Putonghua, and Cantonese, this
  guarantees that at least one locale will not fit the approved edit.
- v2 never discloses synthetic content to the publishing platform, even though
  the entire pipeline generates synthetic content and the target platform
  requires disclosure and exposes an API field for it.

---

## Purpose and outcomes

The pipeline must produce repeatable creative work without removing human
editorial control. It must reduce expensive regeneration, preserve continuity,
and make every published asset traceable to approved inputs and decisions.

The required outcomes are unchanged from v2:

- A validated storyline and ordered shot plan.
- Rights-cleared reference segments with source lineage.
- Structured cinematography and transition analysis.
- A locked visual bible for recurring entities and style rules.
- An approved wireframe animatic before paid video generation.
- Approved generated clips assembled on a canonical editorial timeline.
- English, Putonghua, and Cantonese audio and subtitle deliverables.
- Highlights, an introduction logo, credits, an optional Easter egg, and an end
  card.
- A complete YouTube metadata and thumbnail package.
- A human-approved, auditable, disclosed publish action.

v3 adds three outcomes that v2 implied but did not deliver:

- A **shot-level execution record** that lets twenty shots occupy twenty
  different stages at once without losing gate integrity.
- A **symbolic continuity ledger** that catches contradictions before money is
  spent, instead of scoring pixels after.
- An **auditable spend ledger** in which every paid job is admitted against a
  reserved envelope, so the hard budget is a mechanism rather than a display
  value.

### Design principles

The eight v2 principles are retained. Principles 9 through 13 are new in v3 and
resolve the tradeoffs that v2 left to implementer discretion.

1. **Approve structure before fidelity.** Lock story, timing, blocking, and
   transitions before expensive generation.
2. **Keep the timeline model-neutral.** Store intent and editorial decisions
   outside any image, video, speech, or language model.
3. **Use local processing by default.** Upload assets only when an approved
   provider is required and the project privacy policy permits it.
4. **Treat probabilistic scores as calibrated evidence.** Do not present a
   similarity threshold as a universal fact.
5. **Make every stage resumable.** A failed worker or rejected shot must not
   restart unrelated work.
6. **Regenerate surgically.** Invalidate only artifacts that depend on the
   changed input, passport, shot, or timeline range.
7. **Separate approval from execution.** A human approval authorizes a specific
   artifact, not an evolving filename.
8. **Keep publishing reversible until the last action.** Upload as private or
   unlisted first, verify the remote result, and require a second confirmation
   before making it public.
9. **Approve meaning, not bytes.** An approval binds the editorial decisions
   that a human actually reviewed. Re-encoding the same edit with a newer
   encoder must not silently void a valid approval, and changing one frame of
   content must not silently survive one.
10. **Check symbolically before checking perceptually.** A contradiction that
    can be found by comparing declared state is never worth finding by
    generating video and measuring embeddings.
11. **Constrain the human to a vocabulary the machine can execute.** Free-text
    direction is preserved as rationale, never as the actionable payload.
12. **Plan for the worst-case locale first.** Timing decisions must accommodate
    the longest language before they are approved, not after.
13. **Ship something honest.** A shot that cannot meet its target within budget
    degrades along a declared ladder and is recorded as a known deviation. It
    does not silently lower the standard or block the release forever.

---

## What v3 changes

Each row is a defect or gap in v2, not a stylistic preference. The
corresponding v3 section is linked in the requirement baseline and the body.

| v2 limitation | Consequence if shipped as written | v3 resolution |
|---|---|---|
| The state machine has one global project state. | Twenty shots cannot legally occupy different stages, so either the state machine is bypassed or the pipeline serializes. | A two-level machine: project phases carry gates, shots carry a lifecycle. Phase advance is a rollup predicate over shot states (`STA-001` to `STA-006`). |
| Dependency invalidation is described by example only. | Every implementer invents a different blast radius; over-invalidation wastes money and under-invalidation ships stale work. | A typed artifact graph with an explicit change-class matrix and an invalidation algorithm (`GRA-001` to `GRA-007`). |
| Approvals bind to output hashes. | Re-rendering an unchanged edit produces a new hash and voids a valid approval; a metadata-only edit forces a full re-review. | Approvals bind an `edit_fingerprint` plus evidence hashes, with declared carry-forward rules and deterministic render requirements (`APR-001` to `APR-007`). |
| No concurrency model. | A passport version bump during generation corrupts in-flight work; two workers duplicate paid jobs. | Work leases with heartbeats and fencing tokens, optimistic versioning on projections, and commit-time input revalidation (`CON-001` to `CON-006`). |
| Budget is a global cap plus a reserve fraction. | Overrun happens inside the retry loop, which the cap cannot see until it is exceeded. | Hierarchical envelopes with admission control and escrow, commit, reconcile accounting, per-shot stop-loss, and a measured rate card (`BUD-001` to `BUD-008`). |
| Continuity is perceptual scoring against passports. | Metrics cannot know that the seal was *supposed* to change hands, so intended change reads as drift and unintended change reads as normal variance. | A symbolic continuity ledger of entity state with preconditions and effects, solved before generation, which then supplies the expected state to the perceptual check (`LED-001` to `LED-006`). |
| All quality metrics reward similarity. | Nothing bounds similarity to the copyrighted reference, which is the actual legal risk of reference-driven generation. | An originality ceiling that treats high similarity to a reference segment as a defect, plus a consent-scoped likeness screen (`ORG-001` to `ORG-005`). |
| Human review is "frame-accurate comments". | Notes are not machine-actionable, so a human decision cannot be applied surgically. | A closed set of typed directives, each with a declared scope, cost class, and graph effect (`DIR-001` to `DIR-004`). |
| Recurring rejections teach the system nothing. | The same note is given on shot 3 and again on shot 17. | A rejection taxonomy and a human-confirmed promotion path from repeated findings to project constraints (`DIR-005` to `DIR-007`). |
| Picture lock precedes localization. | The longest locale does not fit the approved edit, forcing re-approval of timing after Gate A. | A locale duration pre-flight before Gate A; animatic timing is sized to the worst-case locale (`LOC-006` to `LOC-010`). |
| Clip duration reconciliation is unspecified. | Models return quantized lengths that do not match shot targets, and the mismatch is resolved ad hoc. | Adapters declare duration quantization; a reconciliation policy defines trim, retime, and extend bounds (`OUT-005` to `OUT-007`). |
| A shot that cannot pass blocks indefinitely. | Real releases stall on one shot. | A declared degradation ladder with approval levels and deviation recording (`DEG-001` to `DEG-004`). |
| Synthetic content is never disclosed to the platform. | Policy violation risk on every publish, despite an available API field. | Mandatory synthetic-media disclosure as a deterministic publish gate, plus optional C2PA at a version the platform recognizes (`DIS-001` to `DIS-006`). |
| Upload idempotency is asserted in tests with no mechanism. | A retried upload can create a duplicate public video. | A publish intent recorded before the request, resumable session persistence, and pre-flight reconciliation (`DIS-007`, `WF-012`). |
| Windows is the target platform with no platform requirements. | Content-addressed nesting under a deep project root exceeds path limits, and CJK titles corrupt filenames. | Explicit path, encoding, and filesystem requirements (`PLT-001` to `PLT-005`). |
| Cost figures are invented constants. | A budget derived from a guess is not a control. | Estimates must cite a rate card measured from real receipts (`BUD-007`). |
| `schema_version` exists with no migration policy. | Old projects become unreadable or, worse, silently misread. | A compatibility and migration policy in which migration creates new artifacts and interacts explicitly with approvals (`EVO-001` to `EVO-004`). |
| Operational metrics are listed with no operator surface. | Nobody notices a stuck project. | A health projection, stuck-work detection, and defined operator actions (`OBS-001` to `OBS-004`). |

v3 removes nothing that v2 required. Every v2 requirement identifier is either
retained verbatim, retained with a tightened definition, or explicitly
superseded by a named v3 identifier in the traceability section.

---

## Scope, assumptions, and non-goals

### In scope

- Storyline and shot-plan validation.
- Reference acquisition when the user has the right to acquire the material.
- Relevant-segment discovery, confirmation, trimming, and retention control.
- Keyframe, transition, camera, lighting, style, motion, and audio analysis.
- Visual bible, continuity ledger, storyboard, wireframe, animatic, and
  style-frame workflows.
- Provider-neutral image, video, speech, transcription, translation, and
  scoring adapters.
- Multi-agent critique with bounded iteration and human arbitration.
- Editorial assembly, audio mixing, subtitles, packaging, and quality control.
- Locale duration planning before structural approval.
- Originality, likeness, and platform disclosure controls.
- YouTube metadata generation, guarded upload, verification, and publication.
- Cost estimation and enforcement, audit logging, provenance, and recovery.

### Out of scope

- Automatic copyright clearance or legal advice. The pipeline produces evidence
  for a human decision; it does not make the decision.
- Circumvention of access controls, digital rights management, paywalls,
  geographic restrictions, or platform safeguards.
- Unattended creation of new dialogue that changes the approved story.
- Unauthorized voice cloning, likeness replication, or impersonation.
- Open-set identification of private individuals. The likeness screen operates
  only against consented passports and a user-supplied exclusion list; it does
  not attempt to recognize arbitrary people.
- Real-time collaborative editing or live video generation.
- Training foundation models as part of the production workflow.
- Guaranteed deterministic output from probabilistic generation models. v3
  guarantees deterministic *assembly*, not deterministic *generation*.

### Assumptions

- One project has one locked frame rate, aspect ratio, and color profile.
- A project may contain horizontal, vertical, or cinematic output profiles, but
  each profile renders from a distinct timeline version.
- References inform shot grammar and do not become source footage in the final
  work unless the rights manifest explicitly permits reuse.
- The user supplies or approves all final story content.
- Human reviewers can reject any automated recommendation regardless of score.
- The initial deployment target is Windows, with worker interfaces that make no
  Windows-specific path assumptions.
- The primary publication channel is YouTube. Channel-specific behavior is
  isolated in a publish adapter and a capability matrix.

---

## Workflow diagram

The pipeline diagram is maintained as a standalone SVG so that it renders in
Markdown viewers, opens independently, and can be diffed as text. GitHub's
Markdown renderer strips inline `<svg>` elements, so the diagram is referenced
rather than pasted inline; the accessible description below is the normative
text equivalent and is sufficient to implement the flow without the image.

**File:** [`video-pipeline-workflow.svg`](./video-pipeline-workflow.svg)

![Video Flow v3 pipeline: six stage rows from intake and rights through
governance, creative pre-production, structure approval, generation control,
delivery and disclosure, and guarded publication, with a per-shot lifecycle
strip and a control plane panel.](./video-pipeline-workflow.svg)

The diagram distinguishes four categories of work, matching the requirement of
the project brief:

- **Automated processing** (blue) runs without a model making a creative choice:
  acquisition, normalization, rendering, deterministic checks, upload.
- **Agent decisions** (teal) are proposals produced or critiqued by a model.
  They are always advisory and always recorded with evidence.
- **Human approval gates** (amber, heavy border) are the only transitions that
  authorize downstream cost or exposure. There are four: A, B, C, and D.
- **The publication action** (red) is the single externally visible side effect,
  split into a non-public upload and a separately authorized visibility change.

### Accessible text description of the diagram

```text
ROW 1 - GOVERNANCE AND REFERENCE INTELLIGENCE
  0 Intake and rights  ->  1 Reference ingest  ->  2 Segment discovery
  ->  3 Film analysis  ->  4 Visual bible and ledger initialization

ROW 2 - CREATIVE PRE-PRODUCTION
  5 Shot design  ->  6 Wireframes  ->  7 Continuity ledger precheck
  ->  8 Locale duration pre-flight  ->  9 Animatic on OpenTimelineIO

ROW 3 - STRUCTURE APPROVAL
  GATE A human animatic approval, covering timing that already fits the
  longest locale  ->  10 Style frames  ->  11 Capability routing and budget
  admission  ->  12 Clip generation  ->  13 Automated quality control

ROW 4 - GENERATION CONTROL
  GATE B human clip approval in adjacent-shot context  ->  14 Picture lock
  ->  15 Audio and locale production  ->  16 Subtitles and mix
  ->  17 Packaging and metadata

ROW 5 - DELIVERY AND DISCLOSURE
  18 Originality, likeness, and disclosure screen  ->  19 Master quality
  control  ->  GATE C human master and delivery approval  ->  20 Guarded
  upload as private or unlisted  ->  21 Remote verification

ROW 6 - GUARDED PUBLICATION
  GATE D human publish authorization  ->  22 Public release
  ->  23 Post-publish verification and rollback runbook

PER-SHOT LIFECYCLE (independent of project phase)
  DRAFT -> DESIGNED -> BOARDED -> IN_ANIMATIC -> CONDITIONED -> GENERATING
  -> QC -> CANDIDATE -> APPROVED -> LOCKED
  Side states reachable from most stages: BLOCKED, DEGRADED, CUT.

CONTROL PLANE (active across every row)
  Workflow orchestrator: two-level state machine, gate readiness, leases,
    fencing tokens.
  Dependency graph service: typed edges, change classes, invalidation,
    stale versus revoked approvals.
  Continuity ledger: entity state preconditions and effects, contradiction
    detection before generation.
  Budget engine: envelopes, escrow, admission control, rate card, stop-loss.
  Direction and learning: typed directives, rejection taxonomy, promoted
    constraints.
  Provenance and disclosure: artifact hashes, edit fingerprints, synthetic
    media disclosure, audit bundle.

REJECTION AND ESCAPE PATHS
  Gate A rejection returns to shot design or wireframes for the affected
    shots only.
  Automated quality control retries within the shot budget, then escalates.
  Gate B rejection regenerates or re-selects only the affected shots and
    invalidates only the affected timeline ranges.
  Gate C rejection returns to the owning delivery stage.
  Remote verification failure keeps the video non-public.
  Any stage may enter the degradation ladder, which lowers shot ambition in
    declared steps and records a deviation rather than blocking the release.

CORE INVARIANTS
  An approval binds an edit fingerprint plus evidence hashes.
  No paid or remote final-video generation before Gate A.
  No public visibility before Gate D.
  No upload without a synthetic content disclosure decision on record.
```

---

## Requirement baseline

Each requirement has a stable identifier. Tests, gate reports, quality reports,
and approval records must cite these identifiers so that release evidence
remains traceable. Identifiers introduced in v2 keep their meaning unless the
row says otherwise.

### Input requirements

| ID | Requirement |
|---|---|
| `IN-001` | The project must include a versioned manifest with title, logline, duration target, output profiles, primary language, locales, budget policy, retention policy, loudness profile, and disclosure policy. |
| `IN-002` | Every scene and shot must have a stable identifier that never depends on display order. |
| `IN-003` | Every shot must define narrative purpose, timing intent, `when`, `what`, `how`, constraints, priority, and referenced entity identifiers. |
| `IN-004` | Every entity identifier must resolve to a character, prop, location, wardrobe item, or motif record before storyboard generation. |
| `IN-005` | Every external reference must include a source URL or local path, relevance hint, intended use, rights basis, and retention class. |
| `IN-006` | Validation errors must identify the field, requirement ID, source file, and remediation action. |
| `IN-007` | Every shot must declare a `story_time` ordinal used for continuity propagation, which may differ from `display_order` for non-linear narratives. |
| `IN-008` | Every dialogue-bearing shot must reference the beat identifiers of the intent script so that locale timing can be planned before Gate A. |

### Reference processing requirements

| ID | Requirement |
|---|---|
| `REF-001` | The rights gate must pass before a remote reference is downloaded or a local reference is analyzed. |
| `REF-002` | The system must prefer direct time hints, then chapters, then multimodal search when locating a relevant segment. |
| `REF-003` | The system must preserve source metadata, selected timestamps, confidence evidence, and a SHA-256 hash of each retained segment. |
| `REF-004` | Low-confidence or conflicting segment matches must require human confirmation. |
| `REF-005` | Precise cuts must decode and re-encode around non-keyframe boundaries; approximate cuts may use stream copy. |
| `REF-006` | Full downloaded references must be deleted or quarantined after segment approval according to the retention policy. |
| `REF-007` | Each retained segment must persist an originality baseline — frame embeddings, a motion signature, and a shot-grammar summary — so that generated output can later be tested for excessive similarity under `ORG-001`. |
| `REF-008` | A "no usable segment" result must be a valid, recordable outcome that does not force selection of a poor candidate. |

### Analysis and creative requirements

| ID | Requirement |
|---|---|
| `ANA-001` | Each approved segment must yield representative keyframes with source timecodes and extraction rationale. |
| `ANA-002` | Each keyframe must include composition, blocking, camera, lens, lighting, palette, production design, atmosphere, motion, and audio observations. |
| `ANA-003` | Consecutive keyframes must include a transition analysis that distinguishes camera movement, subject movement, edit type, and environmental change. |
| `ANA-004` | Model observations must be labeled as observations, inferences, or unknowns. |
| `ANA-005` | Analysis must record which properties are *transferable craft* (framing, lens, lighting ratio, pacing) and which are *protected expression* (specific character design, distinctive set, logo, on-screen text, recognizable performance), because only the former may inform generation. |
| `ANA-006` | Analysis reports must be reproducible from the retained segment hash, the adapter version, and the configuration hash. |
| `CRE-001` | A visual bible must define canonical descriptions, approved images, negative constraints, and versioned passports for recurring entities. |
| `CRE-002` | New shot designs must preserve narrative intent without directly copying distinctive protected expression from references. |
| `CRE-003` | Every shot must have start and end wireframes; shots with meaningful internal change must also have one or more intermediate wireframes. |
| `CRE-004` | Every shot must define camera motion, subject motion, transition behavior, duration, audio intent, and continuity dependencies. |
| `CRE-005` | A passport change must invalidate all unapproved descendants and queue approved descendants for impact review, following `GRA-004`. |
| `CRE-006` | Each passport must declare which of its attributes are *invariant* (identity-defining, never allowed to change) and which are *stateful* (allowed to change only through a declared ledger effect). |
| `CRE-007` | The visual bible must be internally consistency-checked before lock: no conflicting attributes, no unreferenced entities, no entity referenced by a shot but absent from the bible. |

### State and workflow requirements

| ID | Requirement |
|---|---|
| `STA-001` | The system must maintain a project phase state and an independent lifecycle state for every shot. |
| `STA-002` | Only transitions declared in the project phase table and the shot lifecycle table may be persisted; any other transition attempt must fail and be logged. |
| `STA-003` | A project phase may advance only when the declared rollup predicate over in-scope shot states is satisfied and all gate evidence exists. |
| `STA-004` | A shot may regress independently after a gate. Regression revokes gate coverage for that shot's scope only, not for the project. |
| `STA-005` | A phase is valid only while gate coverage is total over its scope; loss of coverage must move the phase back to the owning state automatically. |
| `STA-006` | Shot side states `BLOCKED`, `DEGRADED`, and `CUT` must each record an owner, a reason code, and the evidence that produced them. |
| `WF-001` | Every stage must be idempotent for the same inputs, configuration, adapter version, and operation key. |
| `WF-002` | The pipeline must resume from the last valid artifact after interruption. |
| `WF-003` | Automated critique must stop after the configured attempt or cost limit and escalate to a human. |
| `WF-004` | An agent must not approve an artifact that it generated. |
| `WF-005` | Gate A must approve the animatic before any paid or remote final-video generation. |
| `WF-006` | Gate B must approve selected clips before final editorial assembly is locked. |
| `WF-007` | Gate C must approve the complete master and delivery bundle. |
| `WF-008` | Gate D must authorize publication of the exact approved master and metadata. |
| `WF-009` | Approval records must include scope, edit fingerprint, evidence hashes, approver, timestamp, decision, comment, and expiry or revocation state. |
| `WF-010` | Every human-actionable request must have exactly one owning role and must appear in that role's queue until it is resolved or reassigned. |
| `WF-011` | No stage may write outside its declared output set; a stage that needs to change another stage's artifact must emit a directive instead. |
| `WF-012` | Any operation with an external side effect must record an intent record with an idempotency key *before* the request is issued, and must reconcile against that key before retrying. |

### Dependency graph requirements

| ID | Requirement |
|---|---|
| `GRA-001` | Every artifact must record its input artifact identifiers, and the resulting graph must be acyclic. |
| `GRA-002` | Every graph edge must carry a type from the declared edge vocabulary. |
| `GRA-003` | Every change must be classified into a declared change class before propagation. |
| `GRA-004` | Propagation must use the declared edge-type by change-class matrix to compute one of `INVALID`, `REVIEW`, or `INTACT` for each descendant, and must stop descending when the result is `INTACT`. |
| `GRA-005` | An approval covering an `INVALID` artifact must be revoked. An approval covering a `REVIEW` artifact must be marked stale and must be resolvable by an explicit low-cost confirmation rather than a full re-review. |
| `GRA-006` | Invalidation must be computed and recorded as an immutable impact report before any repair work is scheduled. |
| `GRA-007` | The system must be able to answer, for any artifact, both "what would break if this changed" and "what evidence supports this being approved" without scanning all project history. |

### Approval binding requirements

| ID | Requirement |
|---|---|
| `APR-001` | Every reviewable composite artifact must expose an `edit_fingerprint` computed from its canonical editorial decisions, excluding encoder identity, timestamps, filenames, and other non-editorial metadata. |
| `APR-002` | An approval must bind the `edit_fingerprint`, the set of content hashes that were actually reviewed, and the review render hash used to make the decision. |
| `APR-003` | A re-render whose `edit_fingerprint` is unchanged must carry the approval forward, recording the new encode hash as additional evidence. |
| `APR-004` | A change to any reviewed content hash must revoke the approval regardless of `edit_fingerprint` equality. |
| `APR-005` | Delivery renders must be produced with a deterministic render profile that pins the encoder, its flags, and metadata suppression, so that an unchanged edit reproduces an identical file where the encoder permits it. |
| `APR-006` | Where byte-identical reproduction is not achievable, the system must produce a difference report and require that all differences fall inside a declared allow-list of non-editorial fields. |
| `APR-007` | Gate D must bind the exact byte hash of the file that was uploaded, because that file is what becomes public. |

### Concurrency requirements

| ID | Requirement |
|---|---|
| `CON-001` | Work must be claimed by a lease with a bounded term, a holder identity, and a monotonically increasing fencing token. |
| `CON-002` | A worker must renew its lease by heartbeat; an expired lease makes the work reclaimable. |
| `CON-003` | An artifact write must be rejected if the writer's fencing token is lower than the token recorded for the most recent accepted write of that operation. |
| `CON-004` | A job must record the versions of every input it was built against and must revalidate them at commit time; a mid-flight input version change must fail the commit and produce an impact report rather than overwrite state. |
| `CON-005` | Mutable projections must use optimistic concurrency with a version check, and a conflicting update must be retried against fresh state rather than merged blindly. |
| `CON-006` | Two concurrent claims for the same paid generation operation key must result in exactly one billable request. |

### Continuity ledger requirements

| ID | Requirement |
|---|---|
| `LED-001` | Every stateful passport attribute must be declared as a ledger variable with a name, a value domain, and an initial value. |
| `LED-002` | Every shot may declare `requires` preconditions and `effects` postconditions over ledger variables. |
| `LED-003` | The ledger solver must propagate state in `story_time` order, detect unsatisfied preconditions and undeclared state changes, and report each contradiction with the two shots and the variable involved. |
| `LED-004` | The ledger solve must pass before wireframes are approved and must be re-run after any change to shot order, `story_time`, `requires`, `effects`, or passport state declarations. |
| `LED-005` | The expected ledger state for a shot must be supplied to the perceptual continuity check, so that a difference is reported as an error only when it contradicts the expected state. |
| `LED-006` | Invariant passport attributes must never appear as ledger variables, and an attempt to declare an effect on an invariant attribute must fail validation. |

### Originality and likeness requirements

| ID | Requirement |
|---|---|
| `ORG-001` | Every generated shot informed by a reference segment must be scored for similarity *against that segment*, and similarity above the project ceiling must be treated as a defect requiring redesign. |
| `ORG-002` | Near-duplicate detection must cover framing and composition, motion signature, and any reproduced text, logo, or distinctive graphic element. |
| `ORG-003` | Generated faces must be screened against consented likeness passports for expected identity, and against a user-supplied exclusion list for unintended resemblance. The system must not attempt open-set identification of private individuals. |
| `ORG-004` | An originality or likeness finding must escalate to a human with the compared pair, the score, and the specific region or interval implicated. It must not be auto-waived. |
| `ORG-005` | The delivery bundle must record the originality screen result for every shot, including the reference it was compared against. |

### Human direction and learning requirements

| ID | Requirement |
|---|---|
| `DIR-001` | Every human review action must be expressed as one or more directives drawn from the closed directive vocabulary. |
| `DIR-002` | Every directive must declare its scope, its cost class, and its effect on the dependency graph before it is applied. |
| `DIR-003` | Free-text comments must be attached to a directive as rationale and must never be the sole actionable payload. |
| `DIR-004` | Applying a directive must produce an immutable decision record and a resulting impact report. |
| `DIR-005` | Every rejection must carry a reason code from the declared rejection taxonomy. |
| `DIR-006` | When a reason code recurs beyond the configured threshold within a scope class, the system must propose a promoted constraint with links to the originating rejections. |
| `DIR-007` | A promoted constraint takes effect only after explicit human confirmation, must be expressed in the project constraint vocabulary, must be capped in total count, and must be individually revocable. |

### Quality requirements

| ID | Requirement |
|---|---|
| `QUA-001` | Deterministic checks must run before model-based critique, and a deterministic failure must block regardless of any aesthetic score. |
| `QUA-002` | Semantic metrics must be non-blocking until a calibration record demonstrates their error rates on project-representative labeled data. |
| `QUA-003` | Every quality report must preserve component evidence, not only an aggregate score. |
| `QUA-004` | Every calibration record must pin the dataset hashes, model version, threshold, confusion matrix, and reviewing owner, and must be invalidated by a change to any of them. |
| `QUA-005` | Every critic must return the declared structured critique contract; free-text-only output must be rejected by the schema. |

### Budget requirements

| ID | Requirement |
|---|---|
| `BUD-001` | The project must declare a hard limit, a delivery reserve, and an allocation policy that derives phase allocations and per-shot envelopes. |
| `BUD-002` | Every paid operation must pass admission control before it starts, using its worst-case cost rather than its expected cost. |
| `BUD-003` | Spend must be tracked through the states estimated, escrowed, committed, reconciled, and released, and unused escrow must be released promptly. |
| `BUD-004` | Worst-case cost must assume the provider bills for failed and timed-out jobs unless the provider contract states otherwise. |
| `BUD-005` | Cumulative spend on a single shot must not exceed its stop-loss multiple of its envelope; a breach must escalate and offer the degradation ladder. |
| `BUD-006` | Remote generation must be impossible before Gate A, enforced by policy rather than convention. |
| `BUD-007` | Every cost estimate must cite the version of a rate card measured from actual provider receipts and local benchmark runs. Hardcoded currency constants are not acceptable as estimates. |
| `BUD-008` | Cost must be reportable by project, phase, scene, shot, adapter, accepted take, and rejected take. |

### Localization and audio requirements

| ID | Requirement |
|---|---|
| `LOC-001` | The delivery bundle must include English, Putonghua, and Cantonese speech variants unless a project explicitly disables a language. |
| `LOC-002` | English, Simplified Chinese, and Traditional Chinese Cantonese subtitle tracks must be generated and reviewed. |
| `LOC-003` | Localization must preserve approved meaning, character intent, terminology, names, and emotional beats. |
| `LOC-004` | Subtitle cue boundaries must align with speech within two project frames after final review. |
| `LOC-005` | Subtitle layout must use no more than two lines and must pass safe-area and readability checks for every output profile. |
| `LOC-006` | An intent script with identified beats must exist before the animatic is built, and every dialogue beat must be anchored to a shot or timeline range. |
| `LOC-007` | A locale duration pre-flight must measure draft speech duration for every beat in every enabled locale using a declared draft voice profile. |
| `LOC-008` | Animatic beat timing must accommodate the longest measured locale duration plus the configured headroom before Gate A is offered. |
| `LOC-009` | Each locale must declare its accommodation policy: permitted speech-rate adjustment bounds, permitted pause compression, permitted use of shot handles, and the escalation path when none of these suffice. |
| `LOC-010` | When accommodation is exhausted, the system must request a length-controlled rewrite of the line rather than silently distorting speech rate or overrunning picture. |
| `LOC-011` | Every locale mix must meet the project loudness profile, and the measured integrated loudness and true peak must be recorded per deliverable. |

### Packaging, output, and publication requirements

| ID | Requirement |
|---|---|
| `PKG-001` | Packaging must support a highlight, introduction logo, main content, credits, optional Easter egg, and final end card in the approved order. |
| `PKG-002` | Chapter markers must start at `00:00`, contain at least three entries, appear in ascending order, and allocate at least 10 seconds per chapter. |
| `PKG-003` | The publication package must include title, short description, long description, chapters, tags, thumbnail, language metadata, licensing notes, and end-screen recommendations. |
| `PKG-004` | Tag sets must be validated against the channel's aggregate tag length limit before upload, not after rejection. |
| `PKG-005` | The highlight must be assembled only from approved shots and must respect a declared spoiler policy. |
| `OUT-001` | The canonical editorial timeline must be stored as OpenTimelineIO, with external media references and versioned markers. |
| `OUT-002` | The default upload master must be MP4 with H.264 High Profile video, AAC-LC audio, Rec.709 SDR, constant frame rate, and fast-start metadata. |
| `OUT-003` | Audio stems must use 48 kHz WAV; subtitle sources must include WebVTT and SRT. |
| `OUT-004` | Per-locale delivery must use the channel capability matrix to choose between separate per-language uploads and a single video with additional audio tracks, and must not claim API verification for a step that has no API. |
| `OUT-005` | Every generation adapter must declare its duration quantization, minimum and maximum duration, and whether it can honor an exact requested duration. |
| `OUT-006` | A returned clip whose duration differs from the shot target must be reconciled by the declared policy, in the declared order of preference, within the declared bounds. |
| `OUT-007` | Reconciliation must never silently change a shot's approved duration; a change beyond the declared bounds requires a directive and re-approval of the affected timeline range. |

### Disclosure, provenance, and rights requirements

| ID | Requirement |
|---|---|
| `DIS-001` | Every upload must carry an explicit synthetic-content disclosure decision, recorded with the deciding human and rationale. |
| `DIS-002` | When any generated media appears in the master, the disclosure field must be set affirmatively unless a recorded human determination establishes that the content is not realistic altered or synthetic content. |
| `DIS-003` | The disclosure decision must be verified as a deterministic pre-upload check and re-verified against the remote record after upload. |
| `DIS-004` | Optional provenance signing must use a C2PA version that the target platform recognizes; an unrecognized version must not be presented as platform-visible provenance. |
| `DIS-005` | Absence of external provenance signing must not weaken internal hash lineage or audit requirements. |
| `DIS-006` | The audit bundle must record the disclosure decision, its rationale, and the remote verification result. |
| `DIS-007` | Upload must use a resumable session whose URI is persisted, so that an interrupted transfer resumes instead of creating a second video. |
| `RGT-001` | The policy engine must hold records for reference acquisition basis, final-cut source permission, music and sound-effect licenses, font and logo licenses, likeness consent, and voice consent with allowed languages and uses. |
| `RGT-002` | Tool capability must never be treated as authorization; access-control circumvention and out-of-scope authenticated cookies are prohibited. |
| `RGT-003` | Territory, channel, expiry, attribution, and retention restrictions must be enforced at publish time, not only at ingest. |

### Reliability and degradation requirements

| ID | Requirement |
|---|---|
| `REL-001` | Failures must be classified into the declared failure classes, and each class must follow its declared recovery path. |
| `REL-002` | Transient retries must use bounded exponential backoff with jitter and must not apply to deterministic input failures or policy blocks. |
| `REL-003` | Generation-quality retries must be accounted separately from transient retries and must consume the shot budget. |
| `DEG-001` | The project must declare an ordered degradation ladder for shots that cannot meet their target within budget or quality limits. |
| `DEG-002` | Each ladder step must declare the minimum approval level required to apply it. |
| `DEG-003` | Any applied degradation must be recorded as a named deviation in the delivery manifest and surfaced at Gate C. |
| `DEG-004` | Cutting a shot requires a narrative review confirming that the shot's declared purpose is either preserved elsewhere or intentionally abandoned. |

### Platform, evolution, and operations requirements

| ID | Requirement |
|---|---|
| `PLT-001` | All filesystem access must use interfaces that support extended-length paths, and the artifact root must be configurable to a short path to keep total path length within platform limits. |
| `PLT-002` | Artifact filenames must be derived from identifiers and lowercase hex hashes only, never from user-supplied titles, and must avoid platform-reserved names. |
| `PLT-003` | All text artifacts must be UTF-8; subtitle files must declare and test their byte-level conventions, including the WebVTT header and the SRT line-ending and trailing-newline expectations. |
| `PLT-004` | Subprocess invocations must pass arguments as arrays with no shell interpolation, on every platform. |
| `PLT-005` | The test suite must run on the deployment platform, including path-length, Unicode-filename, and case-sensitivity cases. |
| `EVO-001` | Every schema must be versioned semantically, where a minor version may add only optional fields and a major version may change or remove required fields. |
| `EVO-002` | Readers must accept and preserve unknown optional fields and must reject artifacts whose major version they do not implement. |
| `EVO-003` | Migration must create new artifacts with a recorded `migrated_from` link and must never mutate an existing artifact. |
| `EVO-004` | A migrated artifact must resolve its approval status through the `APR-003` carry-forward rule; approvals must never be copied silently. |
| `OBS-001` | The system must expose a per-project health projection covering phase, blocked and degraded shots, open findings by severity, escrow against limit, stale approvals, and the oldest unresolved human request. |
| `OBS-002` | Stuck work must be detected automatically, including expired leases without heartbeat, shots exceeding stage duration thresholds, and gates that are ready but unreviewed. |
| `OBS-003` | Logs and metrics must use structured fields with declared redaction, and redaction must be verified by canary tests. |
| `OBS-004` | Every detected stuck condition must map to a declared operator action. |
| `OPS-001` | Every generated artifact must record input hashes, configuration hash, adapter identifier, model identifier, seed when supported, timing, cost, and log references. |
| `OPS-002` | The system must estimate cost before remote generation and stop before exceeding the hard project budget, enforced through `BUD-002`. |
| `OPS-003` | Secrets and authenticated cookies must never appear in prompts, logs, metadata packages, or audit exports. |
| `OPS-004` | Transcripts, captions, metadata, and model outputs from external media must be treated as untrusted data, not executable instructions. |
| `OPS-005` | The audit bundle must include manifests, approvals, prompts, decisions, model and tool versions, hashes, costs, quality reports, disclosure records, and publish receipts. |

---

## System architecture

The architecture separates durable control state from media processing. The
control plane coordinates immutable artifacts and events; stateless workers
perform acquisition, analysis, generation, rendering, and publishing through
versioned adapters.

v3 keeps the v2 component set and adds five components that correspond to the
newly specified execution model. The graph, ledger, budget, and direction
services are the difference between a described pipeline and an enforceable one.

| Component | Responsibility | Durable output |
|---|---|---|
| Project API and review UI | Collect inputs, display previews, capture typed directives, and expose state. | Project changes, directives, approval records |
| Workflow orchestrator | Enforce two-level transitions, gate readiness, leases, fencing, retries, and escalation. | Workflow events and operation records |
| **Dependency graph service** | Maintain the typed artifact graph, classify changes, compute invalidation, and mark approvals revoked or stale. | Graph edges and immutable impact reports |
| **Continuity ledger service** | Propagate entity state over story time, detect contradictions, and publish expected state to quality checks. | Ledger solutions and contradiction reports |
| **Budget engine** | Derive envelopes, admit or refuse paid work, hold escrow, reconcile receipts, enforce stop-loss. | Spend ledger and admission decisions |
| **Direction and learning service** | Validate directives, apply their graph effects, classify rejections, propose promoted constraints. | Decision records and learned constraints |
| Policy engine | Enforce rights, privacy, provider, voice, likeness, disclosure, and publish rules. | Policy decisions and evidence |
| Artifact service | Store content-addressed media and JSON artifacts with lineage and fingerprints. | Artifact envelopes and hashes |
| Reference worker | Acquire, normalize, segment, transcribe, extract frames, and capture originality baselines. | Reference segments and analysis inputs |
| Creative worker | Produce visual bibles, shot plans, wireframes, and style frames. | Versioned creative assets |
| Generation router | Match shot requirements to approved provider capabilities within admitted budget. | Generation jobs and candidate clips |
| Quality service | Run deterministic checks, calibrated metrics, originality screens, and critic reviews. | Quality reports and remediation requests |
| Editorial service | Maintain OpenTimelineIO, compute edit fingerprints, render through adapters. | Timeline versions and deterministic renders |
| Localization service | Plan locale durations, translate, synthesize, align, caption, mix, and package variants. | Scripts, stems, and subtitle tracks |
| Publish service | Upload with least privilege, disclose, verify remote state, and change visibility. | Upload, disclosure, and publication receipts |
| **Observability service** | Project health, stuck-work detection, and operator action routing. | Health projections and alerts |
| Audit exporter | Assemble reproducibility, rights, quality, cost, disclosure, and approval evidence. | Signed audit bundle |


---

## Execution model

This section is the substance of v3. It specifies the machinery that v2
described in prose: how work is staged, how change propagates, what an approval
actually binds, and how concurrent workers avoid corrupting each other.

### Two-level state machine

Production is not a single pipeline; it is one governance track and many
independent shot tracks. A single global state cannot express "shot 3 is
approved, shot 7 is regenerating, shot 12 is blocked on rights." v3 therefore
maintains a project phase and an independent lifecycle per shot.

#### Project phases

Phases carry gates and authorize classes of spending and exposure. A phase
advances only when its rollup predicate over in-scope shots holds and its gate
evidence exists.

| Phase | Rollup predicate over in-scope shots | Gate | Next phase |
|---|---|---|---|
| `P0_INTAKE` | none | rights and schema validation | `P1_REFERENCE` |
| `P1_REFERENCE` | every reference has an approved segment decision, an explicit no-match record, or a waiver | analysis completeness | `P2_DESIGN` |
| `P2_DESIGN` | every shot is at least `BOARDED`; visual bible locked; ledger solve clean | bible lock approval | `P3_STRUCTURE` |
| `P3_STRUCTURE` | every shot is `IN_ANIMATIC`; locale duration pre-flight satisfied for every dialogue beat | **Gate A** | `P4_GENERATION` |
| `P4_GENERATION` | every non-`CUT` shot is `APPROVED`, `LOCKED`, or approved-`DEGRADED` | **Gate B** | `P5_EDITORIAL` |
| `P5_EDITORIAL` | every timeline item references a `LOCKED` shot; picture lock rendered | master quality control | `P6_DELIVERY` |
| `P6_DELIVERY` | delivery bundle complete and valid for every enabled locale | **Gate C** | `P7_UPLOAD` |
| `P7_UPLOAD` | remote asset exists, is non-public, and passes remote verification | disclosure verification | `P8_AUTHORIZED` |
| `P8_AUTHORIZED` | remote and local identifiers match the approved delivery | **Gate D** | `P9_PUBLISHED` |
| `P9_PUBLISHED` | public visibility and metadata verified | terminal | — |
| `P_HALTED` | a project-wide policy or budget block is open | remediation | owning prior phase |

`P_HALTED` exists only for project-wide blocks such as an exhausted budget or a
revoked license. Shot-specific problems use shot side states so that one bad
shot never halts the project.

#### Shot lifecycle

| State | Meaning | Allowed next states |
|---|---|---|
| `DRAFT` | shot contract exists and validates | `DESIGNED`, `BLOCKED`, `CUT` |
| `DESIGNED` | shot description and motion plan approved by critics | `BOARDED`, `DRAFT`, `BLOCKED`, `CUT` |
| `BOARDED` | required wireframes exist and ledger preconditions hold | `IN_ANIMATIC`, `DESIGNED`, `BLOCKED`, `CUT` |
| `IN_ANIMATIC` | present in the animatic with locale-feasible timing | `CONDITIONED`, `BOARDED`, `BLOCKED`, `CUT` |
| `CONDITIONED` | style frames approved and a feasible generation route reserved | `GENERATING`, `IN_ANIMATIC`, `BLOCKED`, `CUT` |
| `GENERATING` | one or more candidate takes in flight | `QC`, `CONDITIONED`, `BLOCKED`, `DEGRADED` |
| `QC` | candidates undergoing deterministic and semantic checks | `CANDIDATE`, `GENERATING`, `BLOCKED`, `DEGRADED` |
| `CANDIDATE` | at least one take passes automated checks and awaits human review | `APPROVED`, `GENERATING`, `BLOCKED`, `DEGRADED`, `CUT` |
| `APPROVED` | a specific take is approved under Gate B | `LOCKED`, `CANDIDATE`, `BLOCKED` |
| `LOCKED` | take is referenced by the picture-locked timeline | `APPROVED` (on directive) |
| `BLOCKED` | blocked with an owner and reason code | owning prior state |
| `DEGRADED` | completed at a declared lower ladder step | `CANDIDATE`, `APPROVED`, `CUT` |
| `CUT` | intentionally removed; neighbours retimed | `DRAFT` (on reinstatement) |

Regression is normal and cheap. Advancement is gated.

#### Gate readiness and scoped approval

A gate is *offerable* only when its readiness predicate holds. For gate $G$ with
scope $S(G)$:

$$
\mathrm{ready}(G) = \Big(\forall s \in S(G): \mathrm{state}(s) \in \mathrm{Allowed}(G)\Big)
\wedge \big(\mathrm{blocking\_findings}(S(G)) = \emptyset\big)
\wedge \mathrm{evidence\_complete}(G)
\wedge \mathrm{budget\_invariants\_hold}()
$$

Approvals are *scoped*. Gate B is recorded per shot; Gate A and Gate C are
recorded over a composite artifact. A phase remains valid only while gate
coverage is total over its scope:

$$
\mathrm{coverage}(G) = \frac{\big|\{s \in S(G) : \exists\, \text{valid approval covering } s\}\big|}{|S(G)|} = 1
$$

If a single shot regresses after Gate B, coverage drops below one, the project
phase returns to `P4_GENERATION`, and the other shots keep their approvals. This
is the property v2 needed and did not define: a rejection costs one shot, not a
phase.

`STA-001` to `STA-006`, `WF-005` to `WF-008`.

### Artifact dependency graph

Every artifact records its inputs, so the project is a directed acyclic graph.
Invalidation is a graph traversal with typed edges, not a heuristic.

#### Edge vocabulary

| Edge type | Meaning | Example |
|---|---|---|
| `derives` | child content is computed from parent content | reference segment from normalized proxy |
| `conditions` | parent steers generation of the child | style frame or passport conditioning a clip |
| `constrains` | parent restricts what the child may contain | constraint list, negative prompt, policy rule |
| `times` | parent determines only the child's timing | shot duration determining caption cue bounds |
| `describes` | child is a report about the parent | quality report about a clip |
| `measures` | parent is the metric profile used to evaluate the child | calibration profile behind an identity score |
| `contains` | child composite includes the parent as a member | timeline containing a clip |

#### Change classes

| Change class | Meaning |
|---|---|
| `CONTENT` | the artifact's bytes or meaning changed |
| `TIMING` | duration or position changed while content is unchanged |
| `CONSTRAINT` | a constraint, negative prompt, or rule text changed |
| `METADATA` | a non-editorial descriptive field changed |
| `POLICY` | rights, consent, provider permission, or budget authority changed |
| `METRIC` | a metric profile or calibration record changed |
| `IDENTITY` | an invariant passport attribute changed |

#### Propagation matrix

Effects are `X` = `INVALID`, `R` = `REVIEW`, and `.` = `INTACT`.

| Edge type | `CONTENT` | `TIMING` | `CONSTRAINT` | `METADATA` | `POLICY` | `METRIC` | `IDENTITY` |
|---|---|---|---|---|---|---|---|
| `derives` | X | R | R | . | R | . | X |
| `conditions` | X | R | R | . | R | . | X |
| `constrains` | R | . | R | . | R | . | X |
| `times` | . | X | . | . | . | . | . |
| `describes` | X | R | . | . | . | . | R |
| `measures` | . | . | . | . | . | X | . |
| `contains` | X | X | . | . | R | . | X |

Two rows carry most of the value. The `times` row is why changing a clip's
pixels does not invalidate its captions, and changing its duration does. The
`measures` row is why recalibrating a metric invalidates the *report* and not
the media it scored — a distinction that v2's prose could not express and that
would otherwise trigger pointless regeneration.

#### Invalidation algorithm

```text
function propagate(root, change_class):
    severity = { INVALID: 2, REVIEW: 1, INTACT: 0 }
    impact   = {}                      # artifact_id -> effect
    queue    = [ (root, change_class) ]

    while queue is not empty:
        (node, cls) = queue.pop()
        for edge in outgoing_edges(node):        # node is the parent
            effect = MATRIX[edge.type][cls]
            if effect == INTACT:
                continue
            previous = impact.get(edge.child, INTACT)
            if severity[effect] <= severity[previous]:
                continue                          # no new information
            impact[edge.child] = effect
            if effect == INVALID:
                queue.push( (edge.child, CONTENT) )
            # REVIEW does not descend; see rule below

    return ImpactReport(root, change_class, impact, computed_at, hash)
```

Three rules make this terminate and stay useful:

1. **Severity is monotone.** An artifact's effect only ever increases, and the
   graph is acyclic, so the traversal terminates.
2. **`INVALID` descends as `CONTENT`.** If an artifact's content is now wrong,
   its dependants must treat it as a content change.
3. **`REVIEW` does not descend.** An artifact that merely needs human
   confirmation has unchanged bytes, so its dependants are unchanged too. If the
   review produces an actual change, that change is a new event and propagates
   normally. Without this rule, one constraint edit marks the entire project for
   review and the mechanism becomes noise that operators learn to ignore.

The impact report is immutable and is written before any repair work is
scheduled, so the blast radius of a decision is auditable after the fact.

`GRA-001` to `GRA-007`.

### Approval binding

v2 bound approvals to output hashes. That is correct for exposure control and
wrong for editorial control, because it conflates two different questions: *did
the reviewer see this content* and *is this the same file*.

An H.264 encode is not reproducible across encoder builds by default, since
encoders and muxers embed version strings. FFmpeg's `-bitexact` suppresses those
strings, which makes byte-identical re-encoding achievable but still fragile
across major encoder upgrades. Binding approval solely to the encode hash
therefore means a routine toolchain update silently voids every approval in the
project.

v3 separates the two identities.

| Identity | Computed from | Answers | Binds |
|---|---|---|---|
| `edit_fingerprint` | canonical editorial decision list | "is this the same edit?" | Gates A, B, C |
| `content_hashes` | SHA-256 of every reviewed source artifact | "is this the same material?" | Gates A, B, C |
| `encode_hash` | SHA-256 of the rendered file | "is this the same file?" | Gate D, evidence everywhere |

#### Canonical edit decision list

The `edit_fingerprint` is the hash of a normalized projection of the timeline.
It **includes**, for each item in track and record order: shot identifier,
source artifact hash, source in and out points, record in and out points,
transition specification, effect and reframe specification, audio track
references, caption track references, and marker text that affects delivery. All
times are exact rationals in the project time base. It also includes the render
profile identifier and the packaging element order.

It **excludes**: encoder name and version, muxer version, creation and
modification timestamps, absolute filenames, artifact identifiers that do not
affect output, review-only markers, and comment fields.

#### Carry-forward rules

| Change | `edit_fingerprint` | Reviewed content hashes | Approval outcome |
|---|---|---|---|
| Re-render, same profile, newer encoder | unchanged | unchanged | carried forward; new `encode_hash` recorded as evidence |
| Re-render, different render profile | changed | unchanged | revoked; profile is part of the edit |
| One clip replaced with a new take | changed | changed | revoked for that scope |
| Trim adjusted by one frame | changed | unchanged | revoked for that scope |
| Description or tag text edited | unchanged | unchanged for picture | picture approval carried; metadata approval required |
| Caption text corrected | unchanged for picture | changed for captions | picture approval carried; caption approval revoked |
| Artifact migrated to a new schema version | unchanged | unchanged | carried forward with a recorded migration link |

Delivery renders must use a deterministic render profile that pins the encoder,
its flags, and metadata suppression. Where byte-identical reproduction is not
achievable, the system produces a difference report and requires every
difference to fall inside a declared allow-list of non-editorial fields.

Gate D is deliberately different. It binds the exact `encode_hash` of the file
that was uploaded, because that file is what becomes public, and "the same edit"
is not a strong enough guarantee for an irreversible action.

`APR-001` to `APR-007`.

### Concurrency, leases, and fencing

Workers are stateless and may run in parallel, retry, or be presumed dead while
still alive. Three mechanisms keep that safe.

**Leases.** Work is claimed by a lease with a bounded term, a holder identity,
and a fencing token drawn from a monotonic counter. The holder renews by
heartbeat. An expired lease makes the work reclaimable by another worker, which
receives a strictly higher token.

**Fencing.** An artifact write is rejected if the writer's fencing token is
lower than the token recorded for the most recent accepted write of that
operation key. This is what prevents a resurrected worker from overwriting the
result of its replacement.

**Commit-time input revalidation.** Every job records the version of every
input it was built against — passport versions, ledger solution version,
constraint set version, calibration profile version. At commit time those
versions are revalidated. If a passport was bumped while a clip was generating,
the commit fails, the candidate is retained as an orphan artifact with its
lineage intact, and an impact report is produced. The alternative, which v2
left open, is a clip that silently claims conformance to a passport it never saw.

Mutable projections use optimistic concurrency with a version check. A
conflicting update is retried against fresh state, never merged blindly.

`CON-001` to `CON-006`.

### Idempotency and operation keys

An operation key is the hash of the stage identifier, the ordered input artifact
hashes, the configuration hash, the adapter identifier, and the adapter version:

```text
operation_key = sha256( stage || sorted(input_hashes) || config_hash
                        || adapter_id || adapter_version || attempt_class )
```

`attempt_class` distinguishes a deduplicated retry from an intentional request
for an additional candidate. Without it, "generate one more take" is
indistinguishable from "retry the take you already made," and the system either
refuses legitimate work or double-bills.

A repeated operation with the same key returns the existing valid artifact. For
paid operations, admission control and the operation key are checked in the same
transaction, so two concurrent claims produce exactly one billable request.

`WF-001`, `WF-002`, `WF-012`, `CON-006`.

---

## Canonical artifact contracts

Every stage exchanges immutable, schema-versioned artifacts. Mutable project
views are projections built from these artifacts and the append-only event log.
All examples below are valid JSON.

### Artifact envelope

```json
{
  "schema": "video-flow/artifact-envelope",
  "schema_version": "3.0.0",
  "artifact_id": "art_01J6R4M8QF3W3R3W8M6QF0XK2A",
  "artifact_type": "reference.segment",
  "project_id": "prj_moon_gate",
  "scope_id": "shot_S03_02",
  "created_at": "2026-08-19T12:00:00Z",
  "created_by": "worker.reference.segmenter",
  "content_uri": "artifacts/sha256/7a/7a93f2c1d4e5b6a7889900aabbccddeeff00112233445566778899aabbccddee.mp4",
  "sha256": "7a93f2c1d4e5b6a7889900aabbccddeeff00112233445566778899aabbccddee",
  "byte_length": 18420393,
  "inputs": [
    {
      "artifact_id": "art_01J6R4G88Q69W3FKS4JFN0MX1E",
      "edge_type": "derives",
      "version": 3
    }
  ],
  "configuration_sha256": "c2109988776655443322110099887766554433221100998877665544332211aa",
  "operation_key": "9f1c0b7d5e4a3928176554433221100ffeeddccbbaa99887766554433221100ff",
  "adapter": {
    "id": "segmenter.local",
    "version": "3.0.0",
    "runtime": "python"
  },
  "generation": {
    "model_id": null,
    "model_version": null,
    "seed": null
  },
  "lease": {
    "holder": "worker-07",
    "fencing_token": 4192
  },
  "cost": {
    "currency": "USD",
    "estimated": 0.0,
    "escrowed": 0.0,
    "committed": 0.0,
    "reconciled": 0.0,
    "local_gpu_seconds": 31.8,
    "rate_card_version": "rc-2026-08-12"
  },
  "retention_class": "reference-derived-30d"
}
```

### Project manifest

```json
{
  "schema": "video-flow/project",
  "schema_version": "3.0.0",
  "project_id": "prj_moon_gate",
  "title": "The Moon Gate",
  "logline": "A courier discovers that the package she protects remembers its owners.",
  "primary_language": "yue-Hant-HK",
  "delivery_locales": ["en", "zh-Hans-CN", "yue-Hant-HK"],
  "target_duration_seconds": 90,
  "output_profiles": [
    {
      "id": "youtube-16x9-1080p",
      "width": 1920,
      "height": 1080,
      "frame_rate": "24/1",
      "color_space": "bt709",
      "audio_sample_rate": 48000
    }
  ],
  "render_profiles": [
    {
      "id": "delivery-h264-deterministic",
      "container": "mp4",
      "video_codec": "libx264",
      "video_profile": "high",
      "audio_codec": "aac",
      "deterministic": true,
      "suppress_encoder_metadata": true,
      "faststart": true
    }
  ],
  "loudness_profile": {
    "integrated_lufs_target": -14.0,
    "integrated_tolerance_lu": 1.0,
    "true_peak_ceiling_dbtp": -1.0
  },
  "budget_policy": {
    "currency": "USD",
    "hard_limit": 25.0,
    "delivery_reserve_fraction": 0.2,
    "shot_stop_loss_multiple": 1.0,
    "remote_generation_before_gate_a": false,
    "rate_card_version": "rc-2026-08-12",
    "priority_weights": { "hero": 3.0, "supporting": 1.5, "broll": 1.0 }
  },
  "quality_policy": {
    "max_quality_retries_per_shot": 4,
    "semantic_metrics_blocking": false,
    "originality_ceiling": 0.82
  },
  "localization_policy": {
    "duration_headroom_fraction": 0.08,
    "speech_rate_adjustment_bounds": { "min": 0.94, "max": 1.06 },
    "allow_pause_compression": true,
    "allow_handle_extension": true
  },
  "disclosure_policy": {
    "synthetic_media_default": true,
    "require_human_disclosure_decision": true,
    "c2pa_signing": "optional",
    "c2pa_minimum_version": "2.1"
  },
  "retention_policy": {
    "full_reference_days": 0,
    "approved_segment_days": 30,
    "final_project_days": 365
  }
}
```

The numeric values here are project defaults, not universal constants. The
budget figure is meaningful only in combination with the cited rate card
version; `BUD-007` forbids treating it as an estimate on its own.

### Shot specification

```json
{
  "schema": "video-flow/shot",
  "schema_version": "3.0.0",
  "shot_id": "shot_S03_02",
  "scene_id": "scene_S03",
  "display_order": 12,
  "story_time": 12,
  "duration": {
    "target_seconds": 4.5,
    "minimum_seconds": 3.8,
    "maximum_seconds": 5.2,
    "handle_head_seconds": 0.4,
    "handle_tail_seconds": 0.4
  },
  "narrative_purpose": "Reveal recognition through a restrained push-in.",
  "when": "After the courier opens the wooden box.",
  "what": [
    {
      "entity_id": "char_antagonist",
      "action": "turns toward camera",
      "emotion": "cold recognition"
    },
    {
      "entity_id": "prop_jade_seal",
      "action": "remains partly hidden in the left hand"
    }
  ],
  "how": {
    "framing_start": "medium close-up",
    "framing_end": "close-up",
    "camera_angle": "slight low angle",
    "camera_motion": "slow 15 percent push-in",
    "lens_equivalent_mm": 85,
    "lighting": "hard upper-left key with deep negative fill",
    "palette": "cool shadows with a restrained warm skin highlight",
    "sound": "wind bed followed by a low tonal swell"
  },
  "requires": {
    "prop_jade_seal.holder": "char_antagonist",
    "prop_jade_seal.hand": "left",
    "char_antagonist.mask": "removed",
    "loc_gate.time_of_day": "dusk"
  },
  "effects": {
    "char_antagonist.identity_revealed": true
  },
  "dialogue_beats": ["beat_S03_02_a"],
  "constraints": ["period wardrobe", "no modern objects", "no visible text"],
  "references": ["ref_turn_reveal"],
  "originality": {
    "compare_against": ["ref_turn_reveal"],
    "ceiling_override": null
  },
  "priority": "hero"
}
```

`requires` and `effects` replace v2's opaque `continuity_in` and
`continuity_out` version tags. v2's version tags could only say "this shot uses
antagonist v3"; they could not say "the seal must already be in the left hand,"
which is the statement that actually catches continuity errors.

### Continuity ledger variable and solution

```json
{
  "schema": "video-flow/ledger-variable",
  "schema_version": "3.0.0",
  "entity_id": "prop_jade_seal",
  "variables": [
    {
      "name": "holder",
      "domain": ["none", "char_courier", "char_antagonist"],
      "initial": "char_courier",
      "kind": "stateful"
    },
    {
      "name": "hand",
      "domain": ["left", "right", "none"],
      "initial": "right",
      "kind": "stateful"
    },
    {
      "name": "carving_pattern",
      "domain": ["nine-petal lotus"],
      "initial": "nine-petal lotus",
      "kind": "invariant"
    }
  ]
}
```

```json
{
  "schema": "video-flow/ledger-solution",
  "schema_version": "3.0.0",
  "solution_id": "led_01J6R6C2P8",
  "project_id": "prj_moon_gate",
  "solved_at": "2026-08-19T13:10:00Z",
  "shot_order_hash": "b41d9c88ee77665544332211aabbccddeeff00112233445566778899aabbccdd",
  "status": "contradiction",
  "expected_state": {
    "shot_S03_02": {
      "prop_jade_seal.holder": "char_antagonist",
      "prop_jade_seal.hand": "left",
      "char_antagonist.mask": "removed"
    }
  },
  "contradictions": [
    {
      "variable": "prop_jade_seal.holder",
      "required_by": "shot_S03_02",
      "required_value": "char_antagonist",
      "actual_value": "char_courier",
      "last_set_by": "shot_S01_04",
      "explanation": "No shot between story_time 4 and 12 declares an effect transferring the seal.",
      "remediation": "Add a transfer effect to an intervening shot, or relax the precondition."
    }
  ]
}
```

### Direction record

```json
{
  "schema": "video-flow/direction",
  "schema_version": "3.0.0",
  "direction_id": "dir_01J6R7A9K2",
  "project_id": "prj_moon_gate",
  "gate": "GATE_B_CLIPS",
  "author_id": "human_director_01",
  "created_at": "2026-08-19T16:05:00Z",
  "directives": [
    {
      "type": "RESHOOT",
      "scope": { "shot_id": "shot_S03_02" },
      "reason_code": "MOTION_UNNATURAL",
      "parameters": {
        "add_constraints": ["no head rotation beyond 30 degrees"]
      },
      "cost_class": "paid",
      "rationale": "The turn accelerates unnaturally at the midpoint."
    },
    {
      "type": "TRIM",
      "scope": { "shot_id": "shot_S03_03" },
      "reason_code": "PACING_SLACK",
      "parameters": { "head_delta_seconds": 0.0, "tail_delta_seconds": -0.25 },
      "cost_class": "free",
      "rationale": "Cut a quarter second off the tail to tighten the cut."
    }
  ]
}
```

### Approval record

```json
{
  "schema": "video-flow/approval",
  "schema_version": "3.0.0",
  "approval_id": "apr_01J6R5B1XKQCF4YB8H6A2BTCPR",
  "project_id": "prj_moon_gate",
  "gate": "GATE_A_ANIMATIC",
  "scope": { "kind": "project", "shot_ids": null },
  "edit_fingerprint": "sha256:55b0e1aa22334455667788990011223344556677889900aabbccddeeff001122",
  "reviewed_content_hashes": [
    "sha256:a34290bbccddeeff00112233445566778899aabbccddeeff0011223344556677"
  ],
  "review_render_hash": "sha256:1d77aabbccddeeff00112233445566778899aabbccddeeff00112233445566aa",
  "decision": "approved",
  "approver_id": "human_director_01",
  "comment": "Timing and transitions approved; locale headroom verified.",
  "created_at": "2026-08-19T15:30:00Z",
  "expires_at": null,
  "revoked_at": null,
  "carried_forward_from": null,
  "stale": false
}
```

### Critique contract

```json
{
  "schema": "video-flow/critique",
  "schema_version": "3.0.0",
  "artifact_id": "art_candidate_clip_03",
  "critic_role": "continuity",
  "decision": "revise",
  "expected_state_ref": "led_01J6R6C2P8",
  "findings": [
    {
      "requirement_id": "LED-005",
      "severity": "major",
      "time_range": { "start_seconds": 1.8, "end_seconds": 2.6 },
      "evidence": "The seal appears in the right hand; the ledger expects the left hand for this shot.",
      "contradicts_expected_state": true,
      "remediation": "Regenerate with an explicit left-hand constraint.",
      "confidence": 0.91
    }
  ],
  "scores": {
    "identity": 0.86,
    "prop_continuity": 0.42,
    "style": 0.79
  },
  "metric_profile_version": "cal-2026-08-14"
}
```

The `contradicts_expected_state` flag is what makes continuity scoring
actionable. A low prop-continuity score against a passport is ambiguous, because
the prop may have been *supposed* to change. A low score that also contradicts
the ledger's expected state is unambiguously an error.

### Budget envelope and spend record

```json
{
  "schema": "video-flow/budget-envelope",
  "schema_version": "3.0.0",
  "project_id": "prj_moon_gate",
  "currency": "USD",
  "hard_limit": 25.0,
  "delivery_reserve": 5.0,
  "allocatable": 20.0,
  "rate_card_version": "rc-2026-08-12",
  "shot_envelopes": [
    { "shot_id": "shot_S03_02", "priority": "hero", "envelope": 1.85, "stop_loss": 1.85 },
    { "shot_id": "shot_S03_03", "priority": "supporting", "envelope": 0.92, "stop_loss": 0.92 }
  ],
  "totals": {
    "escrowed": 3.40,
    "committed": 11.20,
    "reconciled": 10.95,
    "released": 0.25
  }
}
```


### Project storage layout

The logical layout keeps source declarations separate from immutable artifacts
and human-readable exports. Implementations may map the artifact tree to a local
filesystem or object storage without changing contracts.

```text
projects/<project-id>/
  project.json
  rights/
    rights-manifest.json
    consent-records/
  story/
    storyline.json
    scenes.json
    shots.json
    intent-script.json
  ledger/
    variables.json
    solutions/led-<id>.json
  graph/
    edges.jsonl
    impact-reports/imp-<id>.json
  budget/
    envelope.json
    spend.jsonl
    rate-cards/rc-<version>.json
  timeline/
    edit-v001.otio
    edit-v002.otio
  reviews/
    approvals.jsonl
    directions.jsonl
    decisions.jsonl
  learning/
    rejections.jsonl
    promoted-constraints.json
  exports/
    previews/
    delivery/
    audit/

artifacts/sha256/<first-two-hash-characters>/<full-hash>.<extension>
events/<project-id>.jsonl
operations/<operation-id>.json
```

The artifact root is deliberately configurable and separate from the project
tree, so that deployments on platforms with restrictive path limits can place it
at a short absolute path (`PLT-001`).

---

## Production flow

Each stage declares its category, inputs, outputs, and exit condition. The
category corresponds to the diagram legend: **automated** work involves no
creative model decision, **agent** work is model-proposed and always advisory,
**human gate** work authorizes downstream cost or exposure, and **publish** work
is the externally visible side effect.

### Stage 0 — Intake, validation, and rights gate

*Category: automated, with a human rights declaration.*

1. Validate project, story, scene, shot, entity, reference, and output schemas.
2. Resolve all identifiers, reject dependency cycles, and verify that every
   `story_time` is unique and totally ordered.
3. Record the rights basis for each reference, music track, voice, likeness,
   logo, font, and final-source asset.
4. Classify privacy, retention, and provider restrictions.
5. Estimate duration, shot count, storage, and the cost envelope against the
   current rate card.
6. Produce an intake report and block progression until policy passes.

**Exit:** schema and cross-reference checks pass and the rights gate is clear.

### Stage 1 — Reference ingest and normalization

*Category: automated.*

1. Inspect remote metadata before download when the source supports it.
2. Prefer user-supplied start and end hints and partial acquisition.
3. Use an approved downloader adapter only when platform terms and the rights
   manifest permit acquisition.
4. Normalize analysis proxies to a known pixel format, frame rate, audio sample
   rate, and time base.
5. Extract media metadata and preserve the raw tool report.
6. Hash the normalized proxy and mark the original for policy-driven deletion.

**Exit:** all usable references have normalized proxies or explicit waivers.

### Stage 2 — Relevant-segment discovery

*Category: agent proposal with human confirmation.*

1. Generate candidate boundaries from hints, chapters, detected cuts, transcript
   units, and overlapping windows.
2. Sample frames adaptively so cuts and high-motion intervals get denser
   coverage.
3. Score each candidate against the shot instruction and reference hint.
4. Treat title cards, sponsorship, logos, dead air, and repeated outros as
   penalties rather than automatic deletions.
5. Present top candidates with evidence when confidence is not calibrated for
   automatic acceptance.
6. Refine approved boundaries to clean edit points and cut a frame-accurate
   retained segment.

**Exit:** a segment decision, source time range, score breakdown, transcript
excerpt, representative frames, and retained-segment hash — or a recorded
no-match result, which is a valid outcome (`REF-008`).

### Stage 3 — Cinematography and transition analysis

*Category: agent.*

1. Select keyframes using cut boundaries, visual novelty, action extrema, and
   camera-motion changes.
2. Describe composition, blocking, subject state, environment, lens cues, camera
   position, lighting, palette, texture, weather, and atmosphere.
3. Separate camera motion from subject motion using optical flow and tracks.
4. Describe edit type, pacing, sound, speech, music, and silence across each
   keyframe interval.
5. Label every property as observation, inference, or unknown.
6. **Partition findings into transferable craft and protected expression**
   (`ANA-005`). Only the craft partition is allowed to inform generation prompts.
7. Persist the originality baseline for the segment (`REF-007`).

**Exit:** machine-readable keyframe and transition reports, a craft/expression
partition, an originality baseline, and a human-readable contact sheet.

### Stage 4 — Visual bible, passports, and ledger initialization

*Category: agent proposal with human lock.*

1. Extract characters, props, locations, wardrobe, graphics, and motifs from the
   complete story.
2. Create canonical descriptions and negative constraints.
3. Attach approved identity sheets, turnarounds, color references, scale
   references, and material details.
4. Define project camera grammar, lighting rules, palette, texture, sound
   language, and forbidden elements.
5. **Classify every passport attribute as invariant or stateful** (`CRE-006`),
   and declare a ledger variable for each stateful attribute with its domain and
   initial value (`LED-001`).
6. Run the bible consistency check (`CRE-007`).
7. Lock the bible and record approval of its exact version.

**Exit:** a locked, versioned visual bible and an initialized ledger variable
set. Later changes create a new version and an impact report.

### Stage 5 — Shot design and wireframes

*Category: agent with bounded critique.*

1. Translate each shot contract into start, intermediate, and end beat
   descriptions.
2. Produce black-and-white wireframes with subject blocking, camera direction,
   screen direction, and safe areas.
3. Define camera and subject motion as separate curves or instructions.
4. Define transitions on both sides of the shot and verify editing handles.
5. Run continuity, composition, narrative, motion, and feasibility critics
   independently.
6. Revise within the attempt budget or escalate conflicting advice.

**Exit:** every required shot has an approved wireframe package and is at least
`BOARDED`.

### Stage 6 — Continuity ledger precheck

*Category: automated, deterministic.*

This stage is new in v3 and is the cheapest quality control in the pipeline. It
runs before any pixel is generated.

1. Order shots by `story_time`.
2. Initialize every ledger variable to its declared initial value.
3. For each shot in order, check that `requires` is satisfied by current state.
   Report any unsatisfied precondition with the variable, the required value, the
   actual value, and the shot that last set it.
4. Apply the shot's `effects` to the state.
5. Detect undeclared changes: a state that differs between consecutive shots
   without an intervening declared effect.
6. Reject any effect that targets an invariant attribute (`LED-006`).
7. Publish the per-shot expected state for later use by the perceptual continuity
   critic (`LED-005`).

**Exit:** a clean ledger solution, or a contradiction report that blocks
wireframe approval until resolved.

A worked failure: the seal is initialized to the courier's right hand, shot 12
requires it in the antagonist's left hand, and no intervening shot declares a
transfer. The ledger reports this in milliseconds. Under v2 the same defect would
have been discovered by generating shot 12, scoring prop continuity at 0.42, and
guessing whether the difference was drift or intent.

### Stage 7 — Intent script and locale duration pre-flight

*Category: automated measurement over an agent-authored script.*

This stage is new in v3 and exists to remove a guaranteed rework loop. The same
meaning takes materially different time to speak in English, Putonghua, and
Cantonese; length-controlled speech translation is an active research problem
precisely because naive translation breaks synchronization. Timing approved
without measuring the longest locale is timing that will have to be re-approved.

1. Author an intent script with one record per dialogue beat, carrying speaker,
   meaning, emotion, terminology, pronunciation notes, and the anchoring shot or
   timeline range (`LOC-006`).
2. Produce draft translations for every enabled locale, adapted for meaning
   rather than word count.
3. Synthesize draft speech for every beat in every locale using the declared
   low-cost draft voice profile, and measure the duration of each (`LOC-007`).
4. Compute the beat duration budget as the longest measured locale duration plus
   the configured headroom.
5. Compare each beat budget against its anchoring shot duration and report every
   beat that does not fit.
6. Resolve each overflow using the declared accommodation policy in order:
   permitted speech-rate adjustment, permitted pause compression, permitted
   handle extension, then shot duration increase.
7. When accommodation is exhausted, request a length-controlled rewrite of the
   line rather than distorting rate or overrunning picture (`LOC-010`).

**Exit:** every dialogue beat has a duration budget that all enabled locales can
meet, and the animatic can be timed against it.

### Stage 8 — Animatic assembly

*Category: automated.*

1. Build an OpenTimelineIO sequence from shot durations, transitions, and beat
   duration budgets.
2. Render wireframes with temporary motion, captions, narration, sound effects,
   and music placeholders.
3. Render draft speech for the longest locale into the review copy so that the
   reviewer hears worst-case timing, not best-case.
4. Display shot identifiers and review markers in the review render only, never
   in the delivery render.
5. Validate runtime, pacing, narrative clarity, continuity, and packaging order.
6. Compute the animatic `edit_fingerprint`.

**Exit:** a reviewable animatic with locale-feasible timing and a computed
fingerprint.

### Gate A — Structure approval

*Category: human approval gate.*

Gate A is the highest-leverage control in the pipeline: it is the last point
before spending is possible.

1. Present the animatic, the per-shot wireframe packages, the ledger solution,
   the locale duration report, and the projected cost against the envelope.
2. Accept only typed directives (`DIR-001`).
3. Record approval binding the animatic `edit_fingerprint`, the reviewed content
   hashes, and the review render hash.
4. On rejection, apply directives, compute the impact report, and return only
   the affected shots to Stage 5 or Stage 7.

**No paid or remote final-video generation is possible before this gate**, and
that is enforced by the budget engine and policy engine rather than by
convention (`BUD-006`, `WF-005`).

### Stage 9 — Style frames and generation preparation

*Category: agent.*

1. Create colored start, intermediate, and end style frames from approved
   wireframes and passports.
2. Evaluate identity, prop, location, palette, lighting, framing, and forbidden
   content.
3. Select approved frames and retain all candidates with lineage.
4. Build provider-neutral motion, camera, negative, duration, and continuity
   requirements from the shot contract and the expected ledger state.
5. Estimate candidate count and cost by shot priority against the rate card.
6. Reserve the shot envelope and the delivery reserve.

**Exit:** every shot has approved conditioning, a feasible route, and a reserved
envelope, and is `CONDITIONED`.

### Stage 10 — Capability routing and budget admission

*Category: automated policy decision.*

1. Filter adapters by hard constraints: privacy, rights, duration support,
   resolution, aspect ratio, region, and retention terms.
2. Rank eligible adapters by the routing score.
3. Compute the worst-case cost of the proposed job, assuming the provider bills
   for failures and timeouts unless its contract says otherwise (`BUD-004`).
4. Admit the job only if it fits the remaining shot envelope and the project
   allocatable budget (`BUD-002`).
5. Escrow the worst-case cost before dispatch.
6. On refusal, offer the next route down the fallback ladder or enter the
   degradation ladder.

**Exit:** an admitted, escrowed generation job with a recorded route rationale,
or a recorded refusal.

### Stage 11 — Clip generation

*Category: automated execution of an agent-selected route.*

1. Generate the minimum useful candidate count for the shot priority.
2. Record complete request and response manifests with secrets removed.
3. Record the input versions the job was built against, for commit-time
   revalidation (`CON-004`).
4. Reconcile actual cost against escrow and release the remainder.
5. Fail the commit if any input version changed mid-flight, retaining the
   candidate as an orphan with intact lineage.

**Exit:** candidate clips with complete generation manifests.

### Stage 12 — Automated quality control

*Category: automated checks plus agent critique.*

1. Run deterministic checks first: decode to end, duration, frame rate, pixel
   format, corruption, stream layout, safety.
2. Reconcile returned duration against the shot target using the declared policy
   (`OUT-006`).
3. Run calibrated semantic checks for identity, appearance, prop, location,
   style, and motion quality, supplying the expected ledger state so that
   intended change is not scored as drift.
4. **Run the originality screen** against every reference the shot was compared
   to, treating high similarity as a defect (`ORG-001`).
5. Run the likeness screen against consented passports and the exclusion list
   (`ORG-003`).
6. Rank candidates by calibrated evidence and critic rationale.
7. Retry only when the predicted quality gain justifies the remaining shot
   budget, and stop at the configured attempt limit or the stop-loss threshold.

**Exit:** candidate clips with quality reports and a recommended take, or an
escalation, or entry into the degradation ladder.

### Gate B — Contextual clip approval

*Category: human approval gate.*

1. Insert recommended takes into the latest animatic timeline.
2. Render each clip with at least the preceding and following shot, because a
   locally good clip can still break the sequence.
3. Show deterministic failures separately from aesthetic recommendations, and
   show originality and likeness findings separately again, because those are
   legal rather than aesthetic questions.
4. Accept typed directives: approve, select another take, trim, retime, reshoot
   with constraints, substitute, degrade, or cut.
5. Record Gate B per shot, binding the take's content hash.
6. Invalidate only affected timeline ranges on rejection.

**Exit:** every non-`CUT` shot is covered by a valid Gate B approval and is
`APPROVED`.

### Stage 13 — Canonical editorial assembly and picture lock

*Category: automated.*

1. Maintain the edit in OpenTimelineIO with clips, transitions, markers, handles,
   and metadata.
2. Preserve source and record timecodes for every clip.
3. Apply approved speed changes, reframing, overlays, and transitions.
4. Render review and delivery outputs through the deterministic render profile.
5. Verify that every timeline item references a Gate B approved hash and that no
   unapproved media appears.
6. Compute and record the picture-lock `edit_fingerprint`.
7. Mark contributing shots `LOCKED` and freeze a timeline version.

**Exit:** a picture-locked timeline, a deterministic render, and a fingerprint.

### Stage 14 — Audio, localization, subtitles, and packaging

*Category: agent authoring with automated validation.*

Because Stage 7 already sized the timing to the longest locale, this stage
performs production rather than negotiation.

1. Finalize per-locale scripts from the approved intent script without changing
   story facts.
2. Require consent records for any cloned or synthetic voice modeled on a person.
3. Generate or record dialogue at delivery quality and align it to picture and
   approved lip movement.
4. Build dialogue, music, ambience, and effects stems at 48 kHz.
5. Mix each locale to the project loudness profile and record measured
   integrated loudness and true peak (`LOC-011`).
6. Generate WebVTT and SRT subtitles for all three locales and run linguistic and
   visual review, including safe-area and line-count checks.
7. Assemble the highlight, logo bumper, credits, optional Easter egg, and end
   card in the approved order.
8. Generate title, descriptions, tags, chapters, thumbnail, and end-screen
   recommendations from approved facts, validating chapter rules and the
   aggregate tag length limit before upload (`PKG-002`, `PKG-004`).

**Exit:** approved scripts, stems, mixes, subtitle tracks, packaging timeline,
and a validated metadata manifest for every enabled locale.

### Stage 15 — Originality, likeness, and disclosure screen

*Category: automated screen with human determination.*

1. Re-run the originality screen over the assembled master, not only per shot,
   because assembly can reconstruct a reference sequence that no single shot
   reproduced.
2. Re-run the likeness screen over final frames.
3. Verify that no protected-expression element from the analysis partition
   appears in the output: reproduced on-screen text, logos, or distinctive
   graphic elements.
4. Determine the synthetic-content disclosure value. Because the pipeline
   generates synthetic media by construction, the default is affirmative;
   a negative determination requires a recorded human rationale (`DIS-002`).
5. Record the disclosure decision, its author, and its rationale.

**Exit:** an originality and likeness report for the master and a recorded
disclosure decision.

### Stage 16 — Master quality control

*Category: automated.*

1. Decode every master to the final frame and inspect all streams.
2. Verify resolution, frame rate, color tags, sample rate, channel layout,
   duration, language tags, subtitle timing, and chapter timestamps.
3. Compare the rendered timeline against approved clip hashes and durations.
4. Run black-frame, freeze-frame, clipping, silence, caption-overlap, and
   safe-area checks.
5. Verify loudness against the project profile for every locale.
6. Verify that the deterministic render reproduces the expected file, or produce
   a difference report confined to the allow-list (`APR-006`).
7. Export the audit bundle.

**Exit:** a complete, valid delivery manifest with quality evidence.

### Gate C — Master and delivery approval

*Category: human approval gate.*

1. Review picture, every locale audio track, every subtitle track, and every
   packaging element in context.
2. Review the originality and likeness report and the disclosure decision.
3. Review the list of applied degradations as named deviations (`DEG-003`).
4. Review final cost against budget.
5. Record approval binding the delivery `edit_fingerprint`, the reviewed content
   hashes, and the review render hash.

**Exit:** an immutable, approved delivery manifest.

### Stage 17 — Guarded upload

*Category: publish action, non-public.*

1. Write a publish intent record with a client-side idempotency key **before**
   issuing any request (`WF-012`).
2. Reconcile against that key: if a prior attempt produced a remote asset, resume
   or adopt it instead of uploading again.
3. Use least-privilege credentials held only by the publish service.
4. Upload the approved master with a resumable session whose URI is persisted, so
   an interrupted transfer resumes rather than duplicating (`DIS-007`).
5. Set visibility to private or unlisted.
6. Apply metadata, per-language title and description localizations, caption
   tracks, thumbnail, default audio language, made-for-kids status, and the
   synthetic-content disclosure.
7. For deliverables with no API path, emit the manual runbook rather than
   claiming completion.

**Exit:** a non-public remote asset with a recorded upload receipt.

### Stage 18 — Remote verification

*Category: automated.*

1. Read the remote video record back.
2. Verify duration against the local master within one frame of tolerance,
   accounting for the platform's duration rounding.
3. Verify processing state, visibility, title, description, tags, category,
   default audio language, thumbnail presence, caption track presence and
   language codes, and the synthetic-content disclosure field (`DIS-003`).
4. Verify chapter parsing by re-reading the published description.
5. Present local and remote identifiers side by side with the exact visibility
   change that Gate D would authorize.

**Exit:** a verification report. Any mismatch keeps the asset non-public and
returns to the owning stage.

### Gate D — Publish authorization

*Category: human approval gate, final.*

1. Present the verification report, the remote identifier, the uploaded file's
   `encode_hash`, the metadata hash, and the disclosure state.
2. Require explicit authorization of the exact visibility change.
3. Bind the approval to the uploaded `encode_hash` rather than only to the edit
   fingerprint (`APR-007`).

**Exit:** authorization to change visibility, or a recorded refusal.

### Stage 19 — Public release and post-publish verification

*Category: publish action, public.*

1. Change visibility to public, or set a scheduled publish time.
2. Re-read the remote record and verify public state, metadata, captions, and
   disclosure.
3. Store the publication receipt and canonical URL.
4. Execute any declared manual runbook steps, then verify them by human
   checklist, since they have no API to verify.
5. Keep the rollback runbook available: visibility can be reverted, but views,
   notifications, indexing, and downstream copies cannot. Gate D is the true
   point of no return, and the specification says so plainly rather than implying
   that publication is reversible.

**Exit:** `P9_PUBLISHED` with a verified public record and a stored receipt.


---

## Reference segment extraction algorithm

The algorithm combines deterministic boundaries with multimodal ranking. It never
deletes source regions solely because a model labels them irrelevant.

### Candidate construction

Candidate generation favours supplied evidence before inference.

1. Convert explicit timestamps and URL time parameters into highest-priority
   candidates.
2. Import source chapters and detected scene boundaries.
3. Add transcript sentence and speaker-turn intervals when speech exists.
4. Add overlapping windows between 3 and 20 seconds for uncovered regions.
5. Merge nearly identical intervals and preserve the origin of each boundary.

### Candidate scoring

Each candidate receives normalized evidence scores. The weights below are a
starting profile and must be calibrated on accepted project examples before they
gate anything.

$$
S(c) = 0.35V + 0.20T + 0.15H + 0.10A + 0.10M + 0.10B - P
$$

- $V$: visual-semantic similarity between sampled frames and the shot intent.
- $T$: transcript-semantic similarity when usable speech exists.
- $H$: agreement with the human relevance hint.
- $A$: agreement between independent visual and text analyses.
- $M$: motion and temporal-coherence evidence.
- $B$: boundary cleanliness and edit usability.
- $P$: penalties for unrelated title cards, intros, outros, advertisements,
  logos, dead air, or abrupt truncation.

Every component score is stored. The system must never expose only the aggregate.

### Confidence and acceptance

Confidence uses score margin, evidence coverage, cross-modal agreement, and
calibration history. During the MVP every selected range requires human approval.
Automatic acceptance may be enabled only after a held-out evaluation demonstrates
the configured maximum wrong-segment rate.

A low-confidence result presents the top three non-overlapping candidates with
contact sheets, transcript excerpts, and time ranges. A no-match result is valid
and must not be forced into a poor selection.

### Boundary refinement

- Expand to include the complete demonstrated action when the top interval
  truncates it.
- Snap to detected cuts or low-motion boundaries when semantic content is
  preserved.
- Add configurable pre-roll and post-roll handles.
- Use precise decoding for frame-accurate cuts.
- Verify the retained segment starts and ends on decodable frames and has
  monotonic timestamps.
- Persist the originality baseline for later comparison (`REF-007`).

---

## Continuity: symbolic ledger and perceptual verification

v2 treated continuity as a perceptual measurement problem. That is only half of
it, and it is the expensive half.

A perceptual metric compares a generated frame against a passport reference and
reports a similarity score. It cannot distinguish these two situations:

- The seal is in the wrong hand because the model drifted. This is a defect.
- The seal is in the other hand because the story requires it. This is correct.

Both produce a low prop-continuity score. v2 would have escalated the second case
to a human and, worse, might have "repaired" it by regenerating the shot back
into a continuity error. v3 therefore runs two layers with different jobs.

| Layer | Question | Cost | When |
|---|---|---|---|
| Symbolic ledger | Is the declared plan self-consistent? | negligible, deterministic | before generation |
| Perceptual metrics | Does the generated output realize the declared plan? | significant, probabilistic | after generation |

The ledger produces the expected state per shot; the perceptual layer consumes it.
A perceptual difference is reported as an error only when it contradicts the
expected state (`LED-005`). This inverts the failure mode: intended change no
longer looks like drift, and drift no longer hides inside expected variance.

### Perceptual dimensions

These remain calibrated evidence, not fixed thresholds. v1's constants such as
`0.72` for face similarity may seed an experiment; they are not gates until a
calibration record demonstrates their error rates (`QUA-002`, `QUA-004`).

| Dimension | Candidate evidence | Calibration target |
|---|---|---|
| Face identity | Face embeddings, landmark stability, human labels | Minimize wrong-identity acceptance on held-out frames |
| Full appearance | Image embeddings, clothing attributes, silhouette, palette | Detect costume or body drift without rejecting pose change |
| Prop continuity | Detection, crop embeddings, state attributes, hand association | Detect identity, state, and placement errors, cross-checked against expected ledger state |
| Location continuity | Scene embeddings, layout features, horizon, lighting | Detect unexplained environment change |
| Style continuity | Palette, contrast, grain, lens cues, aesthetic embeddings | Detect outliers while preserving intentional emphasis |
| Motion quality | Optical flow, track stability, temporal warping, critic labels | Detect flicker, morphing, impossible motion, camera discontinuity |
| Audio and lip alignment | Phoneme timing, mouth motion, speech boundaries, human labels | Detect perceptible synchronization error by locale |

### Calibration procedure

1. Label accepted and rejected pairs from the target project or a representative
   pilot.
2. Split labels by entity, shot type, lighting condition, and generation route.
3. Select thresholds on a training split against an explicit false-accept and
   false-reject policy.
4. Verify on a held-out split.
5. Record dataset hashes, model version, threshold, confusion matrix, and
   reviewing owner.
6. Recalibrate after any model, preprocessing, passport, or style-profile change.
   The change invalidates the reports, not the media (`measures` edge).

---

## Originality, likeness, and disclosure controls

Every quality metric described so far rewards similarity: to the passport, to the
adjacent shot, to the project style. v2 contained no metric that penalizes
similarity to anything. But the pipeline's inputs are third-party reference
videos, and the actual legal exposure of reference-driven generation is producing
output that resembles the reference too closely.

This is a genuine inversion, not an edge case, and it needs its own control.

### Originality ceiling

| Control | Rule |
|---|---|
| Comparison basis | Each generated shot is compared against every reference segment listed in its `originality.compare_against` set |
| Direction | Similarity above the project ceiling is a **defect**; similarity below it is normal |
| Dimensions | Framing and composition embeddings, motion signature, shot-grammar summary, and reproduced text or graphic elements |
| Sequence check | Re-run over the assembled master, because assembly can reconstruct a reference sequence that no single shot reproduced (`Stage 15`) |
| Resolution | An exceedance escalates to a human with the compared pair, the score, and the implicated interval. It cannot be auto-waived (`ORG-004`) |

The craft/expression partition from Stage 3 is what makes this workable. The
pipeline is allowed to reuse a lens choice, a lighting ratio, and an editing
rhythm. It is not allowed to reuse a character design, a distinctive set, a logo,
or on-screen text. Only the craft partition reaches a generation prompt.

### Likeness screen

The screen operates in a deliberately narrow scope, both for accuracy and for
ethics:

- Generated faces are checked for consistency with **consented** likeness
  passports, where a match is the expected outcome.
- Generated faces are checked against a **user-supplied exclusion list** of
  identities the production must not resemble, where a match is a finding.
- The system performs no open-set identification of private individuals and
  maintains no general identity database. A finding is a prompt for human legal
  review, never an automated determination about a real person.

### Platform disclosure

The pipeline generates synthetic media by construction. The target platform
requires creators to disclose meaningfully altered or synthetic content when it
appears realistic, and the Data API exposes a boolean field for that disclosure
on insert and update. v2 specified neither, which means a v2 implementation would
have published undisclosed synthetic content on every run.

v3 makes disclosure a deterministic gate:

1. The default disclosure value is affirmative whenever any generated media
   appears in the master (`DIS-002`).
2. A negative determination is permitted but requires a recorded human rationale,
   because the policy turns on whether the content is *realistic*, which is a
   judgement the pipeline is not entitled to make silently.
3. The disclosure field is verified before upload and re-verified against the
   remote record afterwards (`DIS-003`).
4. Optional C2PA signing must use a version the platform recognizes; at the time
   of writing the platform carries forward Content Credentials from version 2.1
   or higher, so signing at a lower version must not be presented as
   platform-visible provenance (`DIS-004`).
5. Internal hash lineage and the audit bundle remain mandatory regardless of
   whether external signing is used (`DIS-005`).

---

## Agent, critique, and human direction model

Agents propose and critique; the workflow engine authorizes transitions. Every
agent receives a bounded context package and a JSON output schema.

### Agent roles

| Role | Owns | Cannot do |
|---|---|---|
| Creative producer | Global intent, shot dependencies, unresolved creative decisions | Approve its own generated artifact |
| Reference analyst | Segment evidence, filmmaking observations, craft/expression partition | Treat source text as workflow instructions |
| Shot designer | Shot descriptions, wireframes, motion plans | Change narrative purpose or locked passports |
| Continuity critic | Identity, prop, wardrobe, location, screen direction, state checks against expected ledger state | Override human approval or contradict the ledger |
| Cinematography critic | Composition, camera, lens, lighting, edit grammar, feasibility | Introduce unapproved story content |
| Motion critic | Camera and subject motion, temporal artifacts, transition fit | Approve clips with deterministic media failures |
| Originality reviewer | Similarity-to-reference findings, protected-expression detection | Waive its own findings |
| Audio and localization director | Intent script, locale scripts, voice, mix, terminology, caption quality | Invent dialogue or use an unconsented voice |
| Technical quality agent | Deterministic media and package checks | Convert warnings into approvals |
| Publish operator | Upload, disclose, verify, apply authorized metadata | Make content public without Gate D |

### Review arbitration

- Deterministic failures block regardless of aesthetic scores.
- Ledger contradictions block regardless of perceptual scores.
- Originality and likeness findings are legal questions and route to a human,
  never to an averaging function.
- A hard project constraint outranks a critic preference.
- Two critics cannot silently average contradictory recommendations; the creative
  producer proposes a resolution with both rationales attached.
- A human resolves conflicts involving story, identity, rights, voice, or
  publication.
- Automatic revision stops after four attempts by default, or earlier when the
  cost policy predicts insufficient remaining budget.

### Typed direction vocabulary

v2 asked for "frame-accurate comments," which a system cannot execute. v3 defines
a closed vocabulary. Free text is preserved as rationale and is never the payload.

| Directive | Scope | Cost class | Graph effect |
|---|---|---|---|
| `ACCEPT` | take | free | records approval |
| `SELECT_TAKE` | take | free | `CONTENT` change on the timeline item |
| `TRIM` | shot | free | `TIMING` change |
| `RETIME` | shot or range | free | `TIMING` change |
| `REORDER` | shot | free | `TIMING` change plus ledger re-solve |
| `REPLACE_CONDITIONING` | shot | cheap local | `CONTENT` change on the conditioning edge |
| `CONSTRAIN` | shot, scene, or project | paid on regeneration | `CONSTRAINT` change |
| `AMEND_PASSPORT` | entity | paid on regeneration | `CONTENT` or `IDENTITY` change |
| `ADJUST_LEDGER` | entity variable from a shot onward | free | ledger re-solve plus `CONSTRAINT` change |
| `RESHOOT` | shot | paid | `CONTENT` change, new generation job |
| `SUBSTITUTE` | shot | free | `CONTENT` change to alternate coverage |
| `DEGRADE` | shot | varies by ladder step | `CONTENT` change plus deviation record |
| `CUT_SHOT` | shot | free | `TIMING` change on neighbours, ledger re-solve |
| `WAIVE` | finding | free | records an exception with approver and justification |
| `ESCALATE` | any | free | assigns an owner and a question |

Every directive produces an immutable decision record and an impact report before
work is scheduled (`DIR-004`). `REORDER`, `ADJUST_LEDGER`, and `CUT_SHOT` all
force a ledger re-solve, because each of them can create a continuity
contradiction that would otherwise surface much later and much more expensively.

### Rejection taxonomy and learned constraints

Every rejection carries a reason code. The taxonomy is intentionally small enough
to be used consistently.

| Group | Reason codes |
|---|---|
| Identity | `FACE_DRIFT`, `WARDROBE_DRIFT`, `PROP_IDENTITY`, `SCALE_ERROR` |
| Continuity | `LEDGER_CONTRADICTION`, `SCREEN_DIRECTION`, `LIGHTING_MISMATCH`, `STATE_UNEXPLAINED` |
| Motion | `MOTION_UNNATURAL`, `TEMPORAL_ARTIFACT`, `CAMERA_DISCONTINUITY`, `MORPHING` |
| Composition | `FRAMING_WEAK`, `BLOCKING_UNCLEAR`, `SAFE_AREA`, `STYLE_OUTLIER` |
| Narrative | `PURPOSE_LOST`, `PACING_SLACK`, `PACING_RUSHED`, `TONE_MISMATCH` |
| Audio | `LIP_SYNC`, `MIX_BALANCE`, `TERMINOLOGY`, `PRONUNCIATION` |
| Legal | `ORIGINALITY_CEILING`, `PROTECTED_EXPRESSION`, `LIKENESS_RISK`, `CONSENT_MISSING` |
| Technical | `DECODE_FAILURE`, `DURATION_MISMATCH`, `PROFILE_MISMATCH`, `CAPTION_TIMING` |

When a reason code recurs beyond the configured threshold within a scope class,
the system proposes a promoted constraint linked to the originating rejections.
Promotion requires explicit human confirmation, must be expressed in the project
constraint vocabulary, is capped in total count, and is individually revocable
(`DIR-006`, `DIR-007`).

The cap matters. An uncapped learning loop grows the prompt until it degrades
generation quality and nobody can explain why. The cap forces a human to retire a
constraint before adding a new one, which keeps the constraint set legible.

---

## Capability routing and duration reconciliation

The core specification names capabilities, not vendors. A registry maps approved
adapters to current providers and local models.

### Adapter declaration

Every generation adapter must declare:

- Supported input types: text, image, start frame, end frame, pose, depth, audio,
  video.
- Maximum duration, resolution, aspect ratios, frame rates, output formats.
- **Duration quantization**, minimum and maximum duration, and whether an exact
  requested duration can be honoured (`OUT-005`).
- Camera, motion, lip-sync, character-reference, and negative-prompt support.
- Seed and reproducibility behaviour.
- Safety, retention, training-use, region, and privacy terms.
- Cost formula, queue behaviour, timeout, cancellation, and refund behaviour.
- Estimated local memory requirement.
- Version identifier and last verification date.

### Routing policy

Hard constraints are applied before ranking:

$$
R(a, s) = Q(a, s) - \lambda_c C(a, s) - \lambda_l L(a, s)
          - \lambda_p P(a, s) - \lambda_r U(a, s)
$$

The terms are predicted quality, cost, latency, privacy exposure, and uncertainty
for adapter $a$ and shot $s$. Project policy sets the weights. An adapter that
violates a hard privacy, rights, duration, or budget constraint is ineligible
regardless of score.

The fallback order is local preferred adapter, approved remote standard adapter,
approved remote hero adapter, simplified motion plan, then the degradation ladder.
The router must never silently relax a story constraint.

### Duration reconciliation

Many video models emit only quantized durations. v2's shot contract had target,
minimum, and maximum seconds but no rule for what to do when a model returns 5.0
seconds for a 4.5-second shot, so the mismatch would have been resolved
differently by every implementer.

The reconciliation order is fixed:

1. **Trim to target using handles.** Permitted when the generated clip is longer
   and the trimmed region falls inside declared handles. Trim from the tail first
   unless the shot's action peak is in the tail.
2. **Retime within bounds.** Permitted within the declared speed-adjustment
   bounds and only when motion quality checks still pass afterwards.
3. **Extend the shot within its declared maximum.** Permitted when the timeline
   and the beat duration budget both allow it.
4. **Request a different route.** Prefer an adapter whose quantization fits.
5. **Escalate as a directive.** Any change beyond declared bounds requires a
   `RETIME` or `RESHOOT` directive and re-approval of the affected timeline range
   (`OUT-007`).

Reconciliation never silently changes an approved duration, because shot duration
is an input to caption timing, chapter timestamps, and the locale duration budget.

---

## Cost and resource control

Cost control is enforced before and during execution. Displaying an estimate
without a stop mechanism does not satisfy `OPS-002`.

### Hierarchical envelopes

$$
\text{allocatable} = \text{hard\_limit} \times (1 - \text{delivery\_reserve\_fraction})
$$

$$
\text{envelope}(s) = \text{allocatable} \times
\frac{w_{\text{priority}(s)}}{\sum_{t \in \text{shots}} w_{\text{priority}(t)}}
$$

Priority weights come from the project manifest. Hero shots receive more; b-roll
receives less. The delivery reserve is never allocatable to generation, because
the failure mode v2 permitted is spending the entire budget on picture and having
nothing left to render, mix, caption, and repair.

### Admission control

A paid job is admitted only if both conditions hold:

$$
\text{escrowed}(s) + \text{worst\_case}(j) \le \text{envelope}(s)
$$

$$
\text{escrowed}_{\text{project}} + \text{worst\_case}(j) \le \text{allocatable}
$$

Worst-case cost, not expected cost, is used, and it assumes the provider bills
for failed and timed-out jobs unless the contract states otherwise (`BUD-004`).
This is the difference between a budget that holds and a budget that is exceeded
by the retries that were never counted.

### Spend states

| State | Meaning | Transition trigger |
|---|---|---|
| `estimated` | predicted from the rate card | planning |
| `escrowed` | reserved against an envelope | admission |
| `committed` | provider accepted a billable request | dispatch acknowledged |
| `reconciled` | matched against a provider receipt | receipt retrieved |
| `released` | unused escrow returned | completion or cancellation |

Escrow must be released promptly on completion, cancellation, or lease
expiry; otherwise a crashed worker permanently sterilizes part of the budget.

### Stop-loss

Cumulative spend on one shot must not exceed its stop-loss multiple. On breach,
the shot escalates and the degradation ladder is offered. Without a per-shot
stop-loss, one difficult hero shot can consume the entire project budget while
every global check still passes.

### Rate card

Estimates must cite a rate card version measured from real provider receipts and
local benchmark runs (`BUD-007`). A rate card records, per adapter and per
capability: unit cost, observed failure rate, observed median and p95 latency,
and measured local wall time and memory by hardware profile.

v1 asserted "under $25 for a polished 60-second piece" and v2 carried that number
into a manifest default. Neither measured it. v3 keeps the number only as a
project default that is meaningless without its rate card, and forbids presenting
an unmeasured constant as an estimate.

### Local resource profiles

| Profile | Typical use |
|---|---|
| CPU only | Download, proxy work, scene detection, metadata, timeline, lightweight embeddings |
| GPU 8 GB | Quantized transcription, lightweight vision-language analysis, limited image work |
| GPU 16 GB | Higher-quality local analysis, embeddings, style frames, selected low-resolution motion models |
| GPU 24 GB or more | Larger local vision-language models, higher-resolution image work, broader local video options |

Each adapter publishes an estimated memory requirement and falls back cleanly
when capacity is insufficient. The pilot benchmarks actual wall time before the
project displays delivery estimates.


---

## Localization and audio

### Why timing is planned before Gate A

The same meaning does not take the same time to speak in English, Putonghua, and
Cantonese. Information density, syllable structure, and natural speech rate all
differ, which is why length-controlled and duration-aware speech translation is an
active research area rather than a solved preprocessing step.

v2's ordering — picture lock, then audio and localization — means the edit is
approved against exactly one implicit locale. The other two are then forced to
choose between unnatural speech rate, overrunning the picture, or reopening the
approved edit. All three outcomes are rework, and the third invalidates Gate B and
Gate C coverage for every affected range.

v3 measures first. Stage 7 produces a per-beat duration budget sized to the
longest locale plus headroom, and Gate A approves timing that every locale can
already meet.

### Accommodation ladder

When a locale overruns its beat budget, the following are applied in order, within
the bounds declared in `localization_policy`:

1. Speech-rate adjustment inside the declared bounds.
2. Pause and breath compression, where permitted.
3. Handle extension into the shot's declared head and tail handles.
4. Shot duration increase inside the shot's declared maximum.
5. Length-controlled rewrite of the line, preserving meaning and emotional intent.
6. Escalation as a directive, with the narrative critic confirming that the
   rewrite preserves the beat's purpose.

Rate adjustment bounds are a project setting rather than a universal constant,
because tolerance for time compression depends on the voice, the language, and the
emotional register of the line.

### Subtitle rules

- Soft tracks in both WebVTT and SRT for every locale (`OUT-003`).
- Cue boundaries aligned to speech within two project frames after final review
  (`LOC-004`).
- No more than two lines per cue, with safe-area and readability checks per output
  profile (`LOC-005`).
- Simplified Chinese for Putonghua, Traditional Chinese for Cantonese.
- Byte-level conventions are declared and tested rather than assumed: UTF-8
  without a byte-order mark, the `WEBVTT` header for WebVTT, and the SRT
  line-ending and trailing-newline conventions verified by a parser test
  (`PLT-003`).

### Loudness

Each locale mix is measured and recorded. The default profile targets an
integrated loudness consistent with the publishing platform's playback
normalization and a true-peak ceiling that leaves headroom for transcoding;
concrete values live in `loudness_profile` and are verified in Stage 16. Mixing
substantially louder than the platform target is pointless, because playback
normalization simply attenuates it while the reduced dynamic range remains.

---

## Packaging, metadata, and publication capability

v2 said the system should choose between per-language uploads and a multi-audio
package "according to channel capability" without stating what that capability is.
The distinction is not cosmetic: one path is fully automatable and verifiable, and
the other requires a human in a browser.

### Verified channel capability matrix

The following reflects the YouTube Data API v3 surface at the time of writing.
Adapters must re-verify it on a schedule and record the verification date.

| Deliverable | Mechanism | Automatable | Remotely verifiable |
|---|---|---|---|
| Video file, privacy status, scheduled publish | `videos.insert` with a resumable session | Yes | Yes |
| Title, description, tags, category | `videos.insert` snippet | Yes | Yes |
| Per-language title and description | `videos.update` with the `localizations` object | Yes | Yes |
| Default language and default audio language | snippet fields | Yes | Yes |
| Synthetic-content disclosure | `status.containsSyntheticMedia` | Yes | Yes |
| Made-for-kids declaration | `status.selfDeclaredMadeForKids` | Yes | Yes |
| Thumbnail | thumbnail upload endpoint | Yes | Yes |
| Caption tracks | `captions.insert` and `captions.update` | Yes | Yes |
| Chapters | timestamps inside the description | Yes, indirectly | Yes, by re-parsing the description |
| Playlist membership | `playlistItems.insert` | Yes | Yes |
| **Additional audio tracks per language** | **YouTube Studio on desktop only** | **No** | **No — human checklist** |
| **End screens and cards** | **YouTube Studio only** | **No** | **No — human checklist** |

Two consequences follow, and the specification states them rather than implying
completeness:

1. **Per-locale text metadata and captions are fully automatable; per-locale audio
   is not.** A project that wants one video with three audio tracks must accept a
   manual Studio step. A project that wants full automation must publish three
   separate videos. The choice belongs to the project, and `OUT-004` requires the
   delivery bundle to be structured for whichever is chosen.
2. **Any manual step must be emitted as a runbook and verified by human
   checklist.** The system must never report a manual step as verified, because it
   has no API with which to verify it. If the platform has already generated an
   automatic dubbed track for a language, that track must be removed before an
   authored track is attached for the same language.

### Metadata validation

- Chapters start at `00:00`, number at least three, ascend, and allocate at least
  10 seconds each (`PKG-002`).
- The aggregate tag length is validated against the channel limit before upload,
  counting separators and the quoting behaviour applied to multi-word tags
  (`PKG-004`).
- Descriptions, licensing notes, and end-screen recommendations are generated only
  from approved facts.
- The thumbnail is validated for dimensions and safe-area legibility.

---

## Delivery bundle

The bundle separates editorial sources from platform uploads so that a project can
be repaired or republished without regenerating creative work.

```text
delivery/<release-id>/
  manifest.json
  deviations.json
  masters/
    picture-master.mov
    upload-en.mp4
    upload-zh-Hans-CN.mp4
    upload-yue-Hant-HK.mp4
  audio/
    en-dialogue.wav
    zh-Hans-CN-dialogue.wav
    yue-Hant-HK-dialogue.wav
    music.wav
    effects.wav
    ambience.wav
  captions/
    en.vtt
    en.srt
    zh-Hans-CN.vtt
    zh-Hans-CN.srt
    yue-Hant-HK.vtt
    yue-Hant-HK.srt
  artwork/
    thumbnail-1280x720.png
    end-card.png
  metadata/
    youtube.json
    youtube-description.md
    localizations.json
  timeline/
    final.otio
    edit-fingerprint.json
  reports/
    media-qc.json
    language-qc.json
    loudness-qc.json
    originality-qc.json
    rights-qc.json
  runbooks/
    manual-studio-steps.md
  audit/
    audit-manifest.json
    approvals.jsonl
    disclosure.json
    artifact-hashes.sha256
```

`deviations.json` is new in v3 and records every applied degradation ladder step so
that Gate C reviews the release as it actually is (`DEG-003`). `runbooks/` holds
the manual steps that have no API path. The picture mezzanine codec is
configurable; upload outputs must satisfy `OUT-002`.

---

## Security, rights, and provenance

Media pipelines combine untrusted files, external text, model calls, secrets, and
public publishing, so controls apply at every stage rather than only at upload.

### Rights and consent controls

The policy engine holds records for reference acquisition basis, permission for any
source footage in the final cut, music and sound-effect licences, font and logo
licences, likeness and synthetic-performer consent, and voice consent with allowed
languages and uses. Territory, channel, expiry, attribution, and retention
restrictions are enforced at publish time as well as at ingest (`RGT-003`), because
a licence can expire between Gate C and Gate D.

The ability of a tool to access a URL is not evidence of authorization. The system
must not bypass access controls or use authenticated cookies outside the approved
source and purpose (`RGT-002`).

### Untrusted content controls

All external content is data, never instruction.

- Never concatenate transcripts, captions, comments, descriptions, or metadata
  into system instructions.
- Pass subprocess arguments as arrays with no shell interpolation (`PLT-004`).
- Disable untrusted downloader plugins and remote components by default.
- Validate MIME type, extension, container, stream count, duration, and decode
  limits before analysis.
- Run media tools with restricted filesystem access, timeouts, memory limits, and
  network policy.
- Redact cookies, tokens, local usernames, and provider request headers from logs
  and exports, and verify redaction with canary tests (`OBS-003`).

### Provenance and audit

SHA-256 lineage is mandatory. The audit bundle contains input manifests and rights
records, tool and adapter and model versions, prompts and seeds and parameters,
artifact envelopes and hashes, edit fingerprints, agent critiques and human
decisions and directives, impact reports, cost estimates and reconciled receipts,
timeline versions and render commands, quality and originality reports, the
disclosure decision and its rationale, exception waivers, and upload and
publication receipts.

---

## Reliability, recovery, and degraded completion

### Failure classes

| Failure class | Example | Recovery |
|---|---|---|
| Transient infrastructure | Network timeout, temporary provider error | Bounded exponential backoff with jitter, inside operation limits |
| Capacity | Local out-of-memory, provider queue saturation | Lower-resource approved route, or pause for capacity |
| Deterministic input | Corrupt media, invalid schema | Block and request corrected input; never retry unchanged work |
| Quality | Identity drift, motion artifact | Revise the smallest owning prompt, conditioning asset, or route |
| Ledger contradiction | Unsatisfied precondition | Block before generation; resolve by directive |
| Legal | Originality ceiling exceeded, likeness risk, missing consent | Escalate to a human; never auto-waive |
| Policy | Missing rights, budget, or provider permission | Block until a human supplies evidence or changes scope |
| Concurrency | Stale fencing token, mid-flight input version change | Fail the commit, retain the orphan, emit an impact report |
| Human rejection | Pacing, design, language, or performance concern | Decision record plus invalidation of dependent descendants only |
| Publish verification | Remote processing, metadata, caption, disclosure, or visibility mismatch | Keep non-public, repair, repeat verification |

### Retry policy

Three transient retries with capped exponential backoff. Generation-quality
retries are accounted separately, default to four, and consume the shot budget.
Deterministic failures, policy blocks, ledger contradictions, and legal findings do
not retry automatically.

### Degradation ladder

Real releases stall on one shot. v2 escalated to a human and stopped there, which
in practice means the project waits indefinitely for a shot that no amount of
retrying will fix. v3 declares an ordered ladder so that lowering ambition is an
explicit, approved, recorded decision rather than an informal one.

| Step | Action | Minimum approval | Recorded as |
|---|---|---|---|
| `L0` | Full generated motion as designed | none | baseline |
| `L1` | Reduce motion complexity, shorten duration, or simplify the camera move | automated within budget | deviation note |
| `L2` | Try an alternate route or alternate conditioning | automated within budget | deviation note |
| `L3` | Animate an approved style frame with a slow move or parallax | human directive | named deviation |
| `L4` | Substitute approved alternate coverage of the same beat | human directive | named deviation |
| `L5` | Cut the shot and retime neighbours | human directive plus narrative review | named deviation |
| `L6` | Escalate as a production decision: redesign, cut the scene, or accept the risk | human production owner | named deviation plus rationale |

`L5` requires a narrative review confirming that the shot's declared purpose is
either preserved elsewhere or intentionally abandoned (`DEG-004`). Every applied
step lands in `deviations.json` and is surfaced at Gate C, so the approver sees
the release as it actually is rather than as it was planned.

### Dependency invalidation in practice

The general algorithm is specified above; these are its concrete consequences.

- A changed transcript invalidates language alignment and captions, not picture
  generation (`times` and `derives` edges, not `conditions`).
- A changed shot duration invalidates downstream timeline, audio timing, captions,
  chapters, packaging, masters, and publish approvals.
- A changed passport marks dependent style frames and clips for impact review;
  an invariant identity change invalidates them outright.
- A changed calibration profile invalidates quality reports and leaves media
  intact.
- A changed final master revokes Gate C and Gate D.
- A metadata-only change preserves Gate C for picture and requires new metadata
  approval and a new Gate D.

---

## Platform and portability

The stated deployment target is Windows, which has specific constraints that a
content-addressed artifact store will hit immediately.

| Concern | Requirement |
|---|---|
| Path length | Content-addressed nesting under a deep project root can exceed the classic path limit. The artifact root must be configurable to a short absolute path, and all filesystem access must use interfaces that support extended-length paths (`PLT-001`). |
| Filename derivation | Filenames derive from identifiers and lowercase hex hashes only, never from user-supplied titles. Chinese titles live in metadata, not in paths (`PLT-002`). |
| Reserved names | Identifier schemes must not be able to produce platform-reserved device names. |
| Case sensitivity | Hash hex is always lowercase, so a case-insensitive filesystem cannot alias two artifacts. |
| Text encoding | All text artifacts are UTF-8. Subtitle byte conventions are declared and verified by parser tests rather than assumed (`PLT-003`). |
| Subprocess invocation | Arguments are passed as arrays with no shell interpolation on every platform (`PLT-004`). |
| Line endings | Repository and artifact text conventions are pinned so that a checkout on another platform does not change a file hash. |
| Test coverage | The suite runs on the deployment platform and includes path-length, Unicode-filename, and case-sensitivity cases (`PLT-005`). |

---

## Schema evolution

`schema_version` fields exist in v2 with no policy, which means the first breaking
change would have been resolved by hand.

| Rule | Requirement |
|---|---|
| Versioning | Semantic. A minor version may add only optional fields; a major version may change or remove required fields (`EVO-001`). |
| Forward compatibility | Readers accept and preserve unknown optional fields, and reject artifacts whose major version they do not implement (`EVO-002`). |
| Migration | Migration creates a new artifact with a recorded `migrated_from` link and never mutates an existing artifact (`EVO-003`). |
| Approvals | A migrated artifact resolves approval through the `APR-003` carry-forward rule. Because migration does not change editorial decisions, the `edit_fingerprint` is unchanged and the approval carries forward with a recorded migration link. Approvals are never copied silently (`EVO-004`). |
| Registry pinning | The audit bundle records the schema registry version used to write every artifact. |

The interaction between migration and approval is the part that is easy to get
wrong. Migrating an artifact changes its hash. Under v2's hash-bound approvals,
a routine schema migration would have revoked every approval in the project. The
fingerprint separation is what makes migration safe.

---

## Observability and operator surface

v2 listed operational metrics with no place for anybody to see them.

### Health projection

Per project: current phase, gate readiness, blocked shots with owners, degraded
shots with ladder steps, open findings by severity, escrowed spend against limit,
stale approvals awaiting confirmation, and the age of the oldest unresolved human
request (`OBS-001`).

### Stuck-work detection and operator actions

| Condition | Detection | Operator action |
|---|---|---|
| Dead worker | Lease expired with no heartbeat | Reclaim the lease with a higher fencing token |
| Stalled shot | Time in one lifecycle state exceeds the stage threshold | Inspect the shot's last operation and findings |
| Unreviewed gate | Gate ready but not acted on beyond the threshold | Notify the owning reviewer |
| Escrow leak | Escrow held with no active lease | Release the escrow and record the correction |
| Retry churn | Quality retries at the limit with no score improvement | Offer the degradation ladder |
| Stale approval backlog | Stale approvals above the threshold | Batch-confirm unchanged artifacts |
| Overdue retention | Assets past their retention class | Execute deletion and record it |

Every detected condition maps to exactly one declared action (`OBS-004`).

---

## Recommended implementation stack

The stack favours stable interchange and command interfaces. Exact dependency
versions belong in lockfiles and deployment manifests, not in a long-lived
architecture document.

| Concern | Recommended baseline | Reason |
|---|---|---|
| Control plane | Python service with an explicit two-level state machine | Strong media and machine-learning ecosystem with testable transitions |
| Project database | SQLite in WAL mode for the single-node MVP; PostgreSQL for multi-worker deployment | Local-first simplicity with a clear scale path |
| Graph and ledger storage | Relational tables in the project database, with the graph as an append-only edge log | Transactional consistency with approvals and spend |
| Artifact store | Content-addressed filesystem at a short root; S3-compatible storage when distributed | Immutable lineage and deduplication |
| Acquisition | Downloader adapter with policy checks and structured JSON output | Broad source support and partial-download capability |
| Media processing | FFmpeg and `ffprobe`, with a deterministic render profile | Mature stream, filter, transcode, metadata, and validation support |
| Scene detection | PySceneDetect | Multiple detectors and timeline export |
| Editorial interchange | OpenTimelineIO | Model-neutral clips, tracks, transitions, markers, and external media links |
| Rendering | FFmpeg baseline; a code-driven graphics adapter after licence review | Deterministic media core with optional motion graphics |
| Review UI | Web application with frame-accurate preview and a typed directive palette | Human gates and machine-actionable decisions in one surface |
| Agent integration | Provider-neutral structured-output interface | Prevents framework and model lock-in |
| Metrics | Local embedding, detection, optical-flow, and alignment adapters with versioned calibration | Low-cost evidence that can be recalibrated |
| Publishing | YouTube Data API adapter with least-privilege OAuth, resumable upload, and remote verification | Auditable upload, disclosure, and metadata operations |

The review UI is load-bearing in v3 in a way it was not in v2. A typed directive
palette is what converts human judgement into surgical graph operations, so it is
a control-plane component rather than a convenience.

---

## Implementation roadmap

Each milestone delivers a thin, testable vertical slice, can operate without later
milestones, and has an explicit exit criterion.

### Milestone 0 — Contracts, graph, and control plane

**Deliverables:** JSON Schemas for every artifact in this document; database
schema for projects, events, artifacts, graph edges, ledger variables and
solutions, operations, leases, approvals, directives, spend, and policies; the
two-level state machine with gate readiness predicates; the dependency graph
service with the propagation matrix and impact reports; the content-addressed
artifact store; edit fingerprint computation; a command-line interface for
validation and state inspection.

**Exit:** invalid transitions and stale approvals fail deterministically; a
project stops and resumes without duplicate artifacts; the invalidation algorithm
reproduces expected blast radii on fixture graphs; contract tests cover every
requirement from `IN-001` through `EVO-004`.

### Milestone 1 — Reference analysis vertical slice

**Deliverables:** rights gate and reference metadata capture; acquisition,
FFmpeg, scene-detection, transcription, embedding, and segment-ranking adapters;
the segment-candidate review screen; frame-accurate trimming, retention cleanup,
and originality baseline capture; structured keyframe and transition reports with
the craft and protected-expression partition.

**Exit:** a pilot with at least five varied references selects the
reviewer-approved interval or returns no match; interrupted downloads and analyses
resume safely; retention follows the manifest exactly; no remote model is required
for the baseline path.

### Milestone 2 — Bible, ledger, and symbolic continuity

**Deliverables:** entity extraction and passport editor with invariant and
stateful classification; ledger variable declaration; the ledger solver with
contradiction reporting; bible versioning with impact reports.

**Exit:** the solver detects seeded contradictions in a fixture project, including
an unsatisfied precondition, an undeclared state change, and an illegal effect on
an invariant attribute; a passport change identifies every dependent shot; the
solver runs in well under a second for a project of a hundred shots.

### Milestone 3 — Storyboard, locale pre-flight, and Gate A

**Deliverables:** shot design and wireframe adapters; the structured critic
service with bounded iteration; the intent script editor; the locale duration
pre-flight with draft synthesis and measurement; the accommodation ladder; the
OpenTimelineIO animatic builder; the typed directive palette; Gate A approval with
fingerprint binding.

**Exit:** a pilot with three scenes and at least eight shots reaches Gate A with no
paid generation; every dialogue beat has a budget that all three locales meet;
rejected shots re-render only affected ranges; every Gate A rejection is expressed
as typed directives with an impact report.

### Milestone 4 — Budgeted generation and Gate B

**Deliverables:** style-frame generation and selection; the capability registry
with at least one local and one remote clip adapter including declared duration
quantization; the budget engine with envelopes, admission control, escrow, and
stop-loss; the rate card measured from pilot receipts; deterministic media quality
control; versioned semantic metrics consuming expected ledger state; the
originality and likeness screens; contextual clip review and Gate B.

**Exit:** the pilot routes, generates, rejects, retries, and approves every shot
without exceeding its hard budget; a forced overrun is refused by admission
control rather than reported after the fact; the quality service preserves
component evidence; an originality ceiling breach blocks and escalates; no remote
request is possible before Gate A.

### Milestone 5 — Editorial, localization, delivery, and Gate C

**Deliverables:** canonical picture lock with the deterministic render profile;
per-locale script finalization, voice, alignment, and mixing; loudness
verification; subtitle generation and review for all locales; highlight, logo,
credits, Easter egg, end card, chapters, and thumbnail tooling; the degradation
ladder and deviation recording; full media, language, loudness, originality,
rights, and audit reports; Gate C over the delivery manifest.

**Exit:** all locale outputs decode and stay synchronized to one picture lock; a
re-render of an unchanged edit carries its approval forward; captions pass timing,
line, safe-area, encoding, and linguistic review; the audit exporter reconstructs
every delivery asset from lineage.

### Milestone 6 — Guarded publication and Gate D

**Deliverables:** least-privilege OAuth integration; the publish intent record
with an idempotency key; resumable upload with persisted session URI; metadata,
localizations, caption, thumbnail, and playlist operations; the synthetic-content
disclosure decision and its verification; remote verification; the manual-step
runbook and human checklist; Gate D authorization; post-publish verification and
the rollback runbook.

**Exit:** a repeated upload request never creates a second video; a verification
failure stays non-public; an upload without a recorded disclosure decision is
refused; only a human approval matching the uploaded byte hash can change
visibility to public.

---

## Test strategy

The canonical pilot uses synthetic or explicitly licensed media so that automated
tests never depend on third-party content.

### Test layers

- **Schema tests:** accepted, rejected, upgraded, and downgraded artifacts,
  including unknown-optional-field preservation.
- **State tests:** every allowed and forbidden transition at both levels, gate
  readiness predicates, scoped coverage loss, revocation, expiry, and resume.
- **Graph tests:** the propagation matrix cell by cell; blast radius on fixture
  graphs; the `REVIEW`-does-not-descend rule; termination on deep chains;
  approval revocation versus staleness.
- **Fingerprint tests:** re-render equality; profile change inequality;
  one-frame trim inequality; metadata-only change equality; migration equality.
- **Concurrency tests:** lease expiry and reclaim; stale fencing token rejection;
  mid-flight input version change failing the commit; exactly one billable request
  under concurrent claims.
- **Ledger tests:** unsatisfied preconditions, undeclared changes, illegal effects
  on invariants, re-solve after reorder and cut, and expected-state publication.
- **Budget tests:** admission refusal at the envelope boundary; worst-case
  accounting for billed failures; escrow release on crash; stop-loss escalation;
  reconciliation against fixture receipts.
- **Localization tests:** beat measurement across locales; accommodation ladder
  ordering; exhaustion triggering a rewrite request rather than rate distortion;
  loudness measurement; subtitle byte conventions.
- **Originality tests:** a near-duplicate of a reference is rejected; a
  legitimately different shot informed by the same reference passes; a reproduced
  logo or on-screen text is detected; assembly-level sequence similarity is
  detected.
- **Adapter contract tests:** each adapter against recorded fixtures, including
  declared duration quantization and reconciliation behaviour.
- **Media integration tests:** short generated fixtures verifying cuts, time
  bases, streams, captions, renders, and hashes.
- **Golden analysis tests:** scene boundaries, keyframes, segment candidates, and
  transition classifications against reviewed fixtures.
- **Calibration tests:** thresholds and confusion matrices reproduced from
  immutable labeled datasets.
- **Resilience tests:** interrupt workers, corrupt caches, exhaust budgets,
  simulate timeouts, verify idempotent recovery.
- **Security tests:** hostile filenames, metadata, and transcript text; oversized
  media; invalid containers; redaction canaries; prompt-injection attempts through
  transcripts and captions.
- **Platform tests:** path length, Unicode filenames, case sensitivity, reserved
  names, and line endings on the deployment platform.
- **Publish tests:** disclosure required before upload; duplicate-upload
  prevention under retry; remote verification mismatch keeping the asset
  non-public; Gate D bound to the uploaded byte hash.
- **End-to-end tests:** the canonical pilot through Gate C with fake remote
  adapters, and through Gate D against a non-public test channel.

### Release gates

A release candidate is acceptable only when all of the following hold.

1. Every requirement identifier maps to at least one automated test or a recorded
   human verification.
2. No critical or major deterministic media failure remains open.
3. All approval, budget, disclosure, and publish bypass tests fail closed.
4. The canonical pilot resumes successfully after interruption at every stage.
5. The audit bundle verifies all hashes and contains no secret canaries.
6. Cost reconciliation matches provider receipts within the configured tolerance.
7. An unchanged edit re-renders to a carried-forward approval, and a one-frame
   change revokes it.
8. The workflow SVG, Markdown links, JSON examples, and requirement
   cross-references all parse and resolve.

---

## Operational metrics

Metrics measure whether the pipeline reduces waste and preserves quality. They do
not substitute for creative review.

- Gate A approval rate before any remote generation.
- Generated seconds per accepted second.
- Cost per accepted shot and per finished minute, against rate card version.
- Automatic retry count and human intervention count per shot.
- Ledger contradictions caught before generation, versus continuity defects found
  after generation. A healthy project moves this ratio upward over time.
- Directive mix: the share of human actions that are free, cheap, or paid.
- Promoted constraints in force, and the rejection rate before and after promotion.
- Locale accommodation events by type, and rewrite requests per finished minute.
- Median time from rejection to replacement preview.
- Share of descendants correctly invalidated after a change, and stale approvals
  resolved by confirmation rather than re-review.
- False-accept and false-reject rates for each calibrated metric.
- Resume success after worker interruption.
- Escrow accuracy: reconciled cost against escrowed cost.
- Degradation ladder usage by step.
- Publish verification failures and unintended-publication count.
- Storage by retention class and overdue-deletion count.

The target is zero for unintended publication, rights-gate bypass, undisclosed
synthetic publication, secret leakage, approval bypass, and budget overrun.

---

## Decisions and extension points

These defaults are intentional and may change through versioned architecture
decisions.

| Decision | Default | Alternative and trigger |
|---|---|---|
| Editorial truth | OpenTimelineIO is canonical; renderers are adapters | A renderer-native project file, only if interchange is abandoned |
| Approval binding | Edit fingerprint plus reviewed content hashes | Pure byte binding, only if editorial reproducibility is abandoned |
| Continuity | Symbolic ledger first, perceptual verification second | Perceptual only, if entity state cannot be declared |
| State model | Two levels: project phase and shot lifecycle | A third level per take, if take-level governance becomes necessary |
| Invalidation | `REVIEW` does not descend | Full descent, if audits show missed stale descendants |
| Database | SQLite for single node | PostgreSQL when workers span machines |
| Artifact store | Local content-addressed filesystem | S3-compatible storage when distributed |
| Segment acceptance | Human approval always | Calibrated automatic acceptance after a held-out evaluation |
| Semantic metrics | Non-blocking until calibrated | Blocking, per dimension, after calibration |
| Locale delivery | Separate per-language uploads | Single video with manual Studio audio tracks, when one URL is required |
| Disclosure | Affirmative by default | Negative only with a recorded human determination |
| Provenance signing | C2PA optional, at a platform-recognized version | Mandatory, if a distribution partner requires it |
| Publication | Non-public upload, then separate authorization | Never a single-step publish |

---

## Open questions

These are unresolved and are recorded rather than papered over.

1. **Originality ceiling calibration.** The ceiling is a project setting with no
   principled default. It needs a labeled set of "too close" and "acceptably
   inspired" pairs before it can be trusted, and that set is expensive to build.
2. **Ledger expressiveness.** Preconditions and effects over discrete variables
   catch object state, position, and reveal ordering. They do not express
   continuous quantities such as fatigue or elapsed weather change. Extending to
   ranges is possible but increases authoring burden.
3. **Draft-to-final voice duration drift.** The locale pre-flight measures draft
   speech. A final voice at a different rate can invalidate the budget. The
   headroom fraction absorbs small drift; the acceptable drift bound needs
   measurement per voice.
4. **Adapter duration honesty.** Reconciliation depends on adapters declaring
   quantization accurately. Providers change behaviour without notice, so declared
   capability needs periodic empirical verification.
5. **Manual Studio steps in an audited pipeline.** Steps with no API cannot be
   verified programmatically, which leaves a genuine gap in the audit chain that a
   human checklist only partially closes.
6. **Promoted constraint interference.** Accumulated constraints can conflict with
   each other or degrade generation quality. The cap limits growth but does not
   detect semantic conflict between constraints.
7. **Cross-locale lip sync.** Aligning three languages to one picture lock is
   tractable for narration and difficult for close-up synchronized dialogue. The
   practical limit for a given shot size is not yet established.

---

## Traceability to the project brief

The brief's Section 8 requires seventeen deliverables. Each is addressed here.

| # | Brief deliverable | Location in this document |
|---|---|---|
| 1 | Formal requirements specification | Requirement baseline |
| 2 | Proposed system architecture | System architecture; Execution model |
| 3 | Component and agent responsibilities | System architecture; Agent, critique, and human direction model |
| 4 | Input and output schemas | Canonical artifact contracts |
| 5 | Data model and asset-management strategy | Canonical artifact contracts; Project storage layout; Delivery bundle |
| 6 | Reference-video extraction algorithm | Reference segment extraction algorithm |
| 7 | Keyframe-analysis workflow | Stage 3 |
| 8 | Wireframe and animatic workflow | Stages 5 through 8 |
| 9 | Multi-agent review and approval protocol | Agent, critique, and human direction model; Gate A through Gate D |
| 10 | Video-generation and assembly workflow | Stages 9 through 13; Capability routing and duration reconciliation |
| 11 | Localization and subtitle workflow | Stage 7; Stage 14; Localization and audio |
| 12 | YouTube packaging and publication workflow | Stage 14; Stages 17 through 19; Packaging, metadata, and publication capability |
| 13 | Quality gates and measurable acceptance criteria | Continuity; Quality requirements; Test strategy; Release gates |
| 14 | Cost, performance, privacy, and security controls | Cost and resource control; Security, rights, and provenance |
| 15 | Failure handling, retry policies, recovery procedures | Reliability, recovery, and degraded completion |
| 16 | Phased implementation roadmap with milestones and test strategy | Implementation roadmap; Test strategy |
| 17 | Risks, assumptions, open questions, recommended decisions | Scope and assumptions; Decisions and extension points; Open questions |

The brief's Section 9 requires an SVG workflow diagram with an accessible text
description, and a clear distinction between automated processing, agent
decisions, human approval gates, and the final publication action. The Workflow
diagram section provides all four, and every stage in the production flow declares
its category.

---

## Source notes

The following official sources were reviewed on August 19, 2026 and inform the
platform-specific and tool-specific requirements in this document. Content from
these sources has been paraphrased rather than reproduced.

- [yt-dlp][yt-dlp] documents structured metadata, partial downloads, retries,
  post-processing, and security-sensitive options.
- [FFmpeg][ffmpeg] documents precise seeking, stream copy, transcoding, stream
  mapping, filters, chapters, metadata, and validation behaviour. The
  [format options reference][ffmpeg-formats] documents the bit-exact flag used by
  the deterministic render profile, which suppresses encoder and muxer version
  strings so that unchanged inputs can produce identical output files.
- [PySceneDetect][pyscenedetect] documents multiple detectors, keyframe image
  output, splitting, and timeline export.
- [OpenTimelineIO][otio] defines the editorial interchange model used as canonical
  editorial truth; its API is documented as stable and under active development.
- [YouTube video chapters guidance][youtube-chapters] defines the chapter rules
  enforced by `PKG-002`: a first chapter at zero, at least three chapters in
  ascending order, and a minimum chapter length of ten seconds.
- [YouTube Data API video resource reference][youtube-videos] defines the fields
  used by the publish adapter, including the synthetic-media disclosure flag, the
  made-for-kids declaration, default audio language, and the localizations object
  for per-language titles and descriptions.
- [YouTube Data API video insert][youtube-upload] defines the upload interface used
  by the guarded publish adapter.
- [YouTube Data API captions reference][youtube-captions] defines the caption
  track operations used for per-locale subtitle delivery.
- [YouTube altered or synthetic content disclosure policy][youtube-synthetic]
  establishes the disclosure obligation implemented by `DIS-001` through
  `DIS-003`.
- [YouTube multi-language audio guidance][youtube-multiaudio] establishes that
  additional per-language audio tracks are added through YouTube Studio on
  desktop, which is why `OUT-004` requires a manual runbook rather than claiming an
  automated path.
- [YouTube content disclosure carry-forward guidance][youtube-disclosures]
  establishes that Content Credentials are carried forward from C2PA version 2.1
  or higher, which sets the minimum version in `DIS-004`.
- [C2PA specification][c2pa] provides the optional signed provenance standard.
- Length-aware and duration-constrained speech translation research documents the
  cross-lingual duration mismatch that motivates the locale duration pre-flight:
  [speech-aware length control for dubbing][dub1] and
  [length-aware speech translation for dubbing][dub2].
- [W3C guidance on text size in translation][w3c-textsize] documents the expansion
  and contraction behaviour that makes single-locale timing assumptions unsafe.

[yt-dlp]: https://github.com/yt-dlp/yt-dlp
[ffmpeg]: https://ffmpeg.org/ffmpeg.html
[ffmpeg-formats]: https://ffmpeg.org/ffmpeg-formats.html
[pyscenedetect]: https://www.scenedetect.com/docs/latest/
[otio]: https://opentimelineio.readthedocs.io/en/latest/
[youtube-chapters]: https://support.google.com/youtube/answer/9884579
[youtube-videos]: https://developers.google.com/youtube/v3/docs/videos
[youtube-upload]: https://developers.google.com/youtube/v3/docs/videos/insert
[youtube-captions]: https://developers.google.com/youtube/v3/docs/captions
[youtube-synthetic]: https://support.google.com/youtube/answer/14328491
[youtube-multiaudio]: https://support.google.com/youtube/answer/13338784
[youtube-disclosures]: https://support.google.com/youtube/answer/15447836
[c2pa]: https://spec.c2pa.org/
[dub1]: https://arxiv.org/abs/2211.16934
[dub2]: https://arxiv.org/abs/2506.00740
[w3c-textsize]: https://www.w3.org/International/articles/article-text-size

---

## Next steps

1. Build Milestone 0 in full. The graph service, the two-level state machine, and
   edit fingerprinting are prerequisites for every later guarantee, and retrofitting
   them is far more expensive than building them first.
2. Implement the ledger solver in Milestone 2 before any generation adapter. It is
   the cheapest defect-detection mechanism in the system and it changes what the
   perceptual metrics are able to conclude.
3. Measure a rate card during Milestone 1 and Milestone 4 pilots. Until then, treat
   every currency figure in this document as a placeholder rather than an estimate.
4. Run the locale duration pre-flight on a real three-locale script early, even
   with a throwaway draft voice. It is the fastest way to find out whether the
   intended pacing survives Cantonese and Putonghua at all.
5. Keep every adapter behind the versioned contracts, and require a Gate A pilot to
   pass before integrating any paid generation route.

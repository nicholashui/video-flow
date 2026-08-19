# Video Flow specification comparison: v1 to v3

This report compares the three Video Flow specifications: [v1], [v2], and
[v3]. It explains what each revision preserves, replaces, and adds, with an
emphasis on architecture, workflow control, quality, cost, localization, and
publishing safety.

[v1]: spec/v1/video-flow.md
[v2]: spec/v2/video-flow.md
[v3]: spec/v3/video-flow.md

## Executive summary

The specifications progress from a creative pipeline plan to a production
architecture and then to an enforceable execution model.

| Version | Primary role | Main contribution | Main remaining gap |
|---|---|---|---|
| v1 | Creative implementation plan | Defines the end-to-end video workflow, visual bible, multilingual output, continuity checks, and human gates. | Relies on fixed thresholds, named vendors, descriptive controls, and loosely specified state. |
| v2 | Production architecture baseline | Adds stable requirements, immutable artifacts, a control plane, OpenTimelineIO, rights controls, calibrated quality, recovery, and guarded publishing. | Describes resumability, invalidation, concurrency, and budget safety without fully defining their mechanisms. |
| v3 | Operational execution baseline | Specifies shot-level state, graph invalidation, approval fingerprints, leases, budget escrow, symbolic continuity, typed direction, localization pre-flight, disclosure, and operations. | Adds significant control-plane complexity and leaves several calibration and platform limitations open. |

The dominant change is:

```text
v1: define what the creative pipeline does
  -> v2: define the production system and its durable contracts
  -> v3: define how that system executes safely under change and concurrency
```

## Version snapshots

Each revision keeps the same product goal but changes the level of engineering
precision and operational control.

| Area | v1 | v2 | v3 |
|---|---|---|---|
| Document version | 1.1 | 2.0 | 3.0 |
| Workflow shape | 14 creative phases | 14 production phases | 20 numbered stages plus four gates |
| Human gates | A: animatic, B: clips, C: final master | Adds D: publish authorization | Retains A-D with scoped readiness and coverage rules |
| State model | Narrative phase sequence | Persisted project state machine | Project phases plus an independent lifecycle per shot |
| Editorial truth | Remotion preferred | OpenTimelineIO canonical; renderers are adapters | Retains OpenTimelineIO and adds edit fingerprints and deterministic render profiles |
| Artifact model | Deliverables and audit bundle | Immutable, schema-versioned, content-addressed artifacts | Adds typed graph edges, input versions, operation keys, leases, and migration links |
| Continuity | Fixed perceptual similarity thresholds | Calibrated perceptual evidence | Symbolic ledger before generation plus perceptual verification after generation |
| Cost control | Estimate and user cap; recommended default budget | Project hard limit and reserve | Hierarchical envelopes, worst-case admission, escrow, reconciliation, stop-loss, and measured rate cards |
| Human feedback | Per-shot comments and approval | Hash-bound approval records | Typed directives, impact reports, rejection taxonomy, and promoted constraints |
| Localization | Produced after picture assembly | Produced after picture lock | Duration pre-flight before Gate A, sized for the longest locale |
| Publishing | Final approval followed by publish | Non-public upload, verification, then Gate D | Adds publish intent, resumable upload, disclosure verification, and exact-byte Gate D binding |

## Change from v1 to v2

Version 2 preserves the creative sequence from v1 but replaces a planning-style
document with a production-oriented architecture. The largest improvement is
that requirements and decisions become durable, testable records.

### Preserved foundations

The following v1 decisions remain central in v2:

- Local processing is preferred before remote or paid generation.
- The visual bible and versioned entity passports protect continuity.
- The wireframe animatic is a hard gate before expensive generation.
- Generated clips receive automated critique and human contextual review.
- English, Putonghua, and Cantonese outputs remain required.
- Packaging includes a highlight, logo, credits, optional Easter egg, end card,
  thumbnail, and YouTube metadata.
- Prompts, model details, costs, decisions, and hashes remain auditable.

### Major replacements and additions

Version 2 changes the implementation model across the following areas.

| Area | v1 approach | v2 change | Practical effect |
|---|---|---|---|
| Requirements | Detailed prose, tables, and examples | Stable requirement identifiers such as `IN-001`, `WF-005`, and `OPS-002` | Tests and approvals can cite exact obligations. |
| Schemas | Example storyline and shot structures | Versioned artifact, project, shot, critique, and approval contracts with valid JSON | Stage boundaries become machine-validated. |
| Workflow | Ordered phases and gate rules | Persisted state machine with allowed transitions and evidence | Workers cannot advance the project by convention alone. |
| Artifacts | Named files and an audit package | Immutable, content-addressed artifacts with lineage | Work becomes resumable, deduplicated, and traceable. |
| Timeline | Remotion is the preferred source of truth | OpenTimelineIO is canonical; Remotion and FFmpeg are adapters | Editorial decisions no longer depend on one rendering tool. |
| Model selection | Specific models are recommended by task | Capability-based provider adapters | Vendor changes do not require shot-contract changes. |
| Quality | Universal thresholds such as face similarity `>= 0.72` | Project-calibrated metrics with held-out validation | Similarity scores become evidence rather than assumed truth. |
| Rights | Fair-use declaration and reference constraints | Rights, consent, likeness, voice, music, and retention gates | Availability of media is separated from permission to use it. |
| Approval | Human approves the current output | Approval records bind artifact hashes, scope, reviewer, and status | Mutable filenames cannot silently retain approval. |
| Publication | Final approval and publish form one phase | Gate C approves delivery; upload remains private or unlisted; Gate D authorizes public visibility | Transfer and irreversible exposure are separated. |
| Recovery | Failure modes are described | Idempotency, retry classes, dependency invalidation, and blocked states are specified | Interrupted work resumes without restarting unrelated stages. |
| Delivery | One primary master plus related assets | Structured mezzanine, locale, caption, metadata, report, timeline, and audit bundle | Repair and republishing do not require creative regeneration. |

### Workflow and roadmap impact

The phase count remains 14, but the responsibilities change. v2 adds intake and
rights control at the beginning, formal analysis before visual-bible lock,
OpenTimelineIO assembly, complete delivery quality control, and a separate
guarded upload phase.

The implementation plan also changes from five immediate actions in v1 to six
milestones in v2:

1. Build contracts and the control plane.
2. Prove reference analysis as a vertical slice.
3. Add the visual bible, storyboard, and Gate A.
4. Add budgeted clip generation and Gate B.
5. Add editorial, localization, and Gate C.
6. Add guarded YouTube publication and Gate D.

v2 also introduces a layered test strategy, explicit release gates, operational
metrics, architecture decisions, and official source notes. These additions
turn v1's proposed workflow into an implementation baseline.

## Change from v2 to v3

Version 3 retains the v2 architecture and concentrates on mechanisms that v2
claimed but did not fully define. It also changes localization order and adds
originality and synthetic-content controls.

### Execution and change control

The largest v3 changes make parallel work and surgical repair enforceable.

| v2 limitation | v3 resolution | Result |
|---|---|---|
| One global project state | Two-level state machine with project phases and per-shot lifecycle states | Different shots can be designed, generating, approved, blocked, degraded, or cut at the same time. |
| Gate status is project-wide | Gate readiness and scoped coverage predicates | Regressing one shot revokes only its coverage and returns only the affected scope. |
| Invalidation is described by examples | Typed artifact graph, change classes, propagation matrix, and immutable impact reports | Every change has a deterministic and auditable blast radius. |
| Approval binds output hashes | `edit_fingerprint`, reviewed content hashes, review render hash, and carry-forward rules | Harmless re-encoding can preserve approval while editorial changes revoke it. |
| No worker concurrency protocol | Leases, heartbeats, fencing tokens, optimistic versions, and commit-time input revalidation | Stale workers and duplicate paid requests cannot overwrite current work. |
| Idempotency lacks intentional-candidate semantics | Operation keys include an `attempt_class` | A retry differs from a deliberate request for another take. |

### Creative continuity and human direction

v3 moves preventable errors earlier and turns reviewer input into executable
operations.

- A symbolic continuity ledger declares stateful entity variables, shot
  preconditions, and shot effects in story order.
- Ledger contradictions block before wireframes are approved or paid media is
  generated.
- Perceptual metrics consume expected ledger state, so intended changes no
  longer appear as drift.
- Invariant identity attributes cannot be changed through ledger effects.
- Human feedback uses typed directives such as `TRIM`, `RETIME`, `RESHOOT`,
  `AMEND_PASSPORT`, `DEGRADE`, and `CUT_SHOT`.
- Every directive declares scope, cost class, and graph effect before execution.
- Rejections use a controlled taxonomy and can propose human-confirmed project
  constraints when a problem recurs.

This changes review from "comment on a frame" to "issue an auditable operation
that the workflow can apply surgically."

### Budget and generation control

v2 provides a hard project limit and reserve. v3 turns that policy into an
accounting mechanism:

- The project budget is split into a delivery reserve and weighted per-shot
  envelopes.
- Paid work is admitted using worst-case cost, not expected cost.
- Spend moves through `estimated`, `escrowed`, `committed`, `reconciled`, and
  `released` states.
- Each shot has a stop-loss, preventing one difficult shot from consuming the
  whole project budget.
- Estimates must cite a versioned rate card measured from provider receipts and
  local benchmark runs.
- Remote generation before Gate A is blocked by policy and budget admission.
- Adapter declarations now include duration quantization and exact-duration
  capability.
- Duration mismatch follows a fixed sequence: trim within handles, retime within
  bounds, extend within the approved maximum, reroute, then escalate.

The v1 and v2 default of USD 25 remains only a project placeholder in v3. It
cannot be represented as an estimate without measured rate-card evidence.

### Localization order

v3 corrects a workflow-order problem in v2. v2 locks picture before producing
the three locale tracks, which can force unnatural speech or reopen an approved
edit when one translation runs longer.

v3 adds an intent script and duration pre-flight before Gate A. Draft speech is
measured for every enabled locale, and animatic timing uses the longest locale
plus configured headroom. Overflow follows an accommodation ladder before a
length-controlled rewrite is requested.

This moves multilingual timing from post-production repair into structural
approval.

### Originality, likeness, and disclosure

v2 measures similarity to approved entities and style but does not limit
similarity to third-party references. v3 adds the opposite control: excessive
similarity to a reference is a defect.

- Reference analysis separates transferable craft from protected expression.
- Retained references store an originality baseline.
- Generated shots and the assembled master are checked against references for
  near-duplicate composition, motion, text, logos, and graphics.
- Likeness checks are limited to consented passports and a user-supplied
  exclusion list; open-set identification is out of scope.
- Originality and likeness findings require human review and cannot be
  automatically waived.
- Uploads carry an explicit synthetic-content disclosure decision.
- The disclosure field is checked before upload and against the remote record.
- Optional C2PA signing must use a platform-recognized version.

### Reliability, publication, and operations

v3 closes several operational gaps left by v2.

| Area | v2 | v3 |
|---|---|---|
| Failed shot | Escalates after bounded retries | Uses a declared degradation ladder from simplified motion through redesign or cut, with deviations reviewed at Gate C |
| Upload retry | Idempotency is a desired test property | Publish intent is recorded first, resumable session state is persisted, and retries reconcile before transfer |
| Platform capability | Chooses delivery according to channel capability | Defines what YouTube APIs can automate and which audio-track, end-screen, and card tasks require a human runbook |
| Windows support | Windows is an assumption | Adds path-length, hash filename, reserved-name, UTF-8, line-ending, subprocess, and platform-test requirements |
| Schema versioning | Versions exist | Semantic compatibility, unknown-field preservation, immutable migration, and approval carry-forward are defined |
| Observability | Metrics are listed | Health projections, stuck-work detection, owners, and operator actions are specified |
| Open issues | Mostly implied | Originality calibration, ledger expressiveness, voice-duration drift, provider capability drift, manual publishing steps, constraint conflicts, and lip sync are explicit |

### Requirement and roadmap expansion

v2 introduces the requirement families `IN`, `REF`, `ANA`, `CRE`, `WF`, `LOC`,
`PKG`, `OUT`, and `OPS`. v3 retains and tightens them while adding dedicated
families for:

- `STA`: project and shot state.
- `GRA`: dependency graph and invalidation.
- `APR`: approval identity and carry-forward.
- `CON`: concurrency, leases, and fencing.
- `LED`: symbolic continuity.
- `ORG`: originality and likeness.
- `DIR`: typed direction and learned constraints.
- `QUA`: deterministic and calibrated quality.
- `BUD`: budget admission and spend accounting.
- `DIS` and `RGT`: disclosure, provenance, rights, and consent.
- `REL` and `DEG`: recovery and degraded completion.
- `PLT`, `EVO`, and `OBS`: platform behavior, schema evolution, and operations.

The roadmap grows from six v2 milestones to seven v3 milestones. v3 separates
the bible and symbolic ledger from storyboard and Gate A, then adds the graph,
budget engine, originality checks, disclosure, and publish idempotency to the
relevant milestones. Its test strategy expands accordingly with graph,
fingerprint, concurrency, ledger, budget, localization, originality, platform,
and disclosure tests.

## Compatibility and implementation impact

The revisions preserve product intent, but they are not drop-in schema or
workflow upgrades.

### v1 to v2 impact

Moving to v2 requires these architectural changes:

- Replace informal input and output structures with versioned contracts.
- Introduce immutable artifact storage, lineage, events, and approvals.
- Move editorial truth from a Remotion composition to OpenTimelineIO.
- Replace vendor-specific generation decisions with capability adapters.
- Add rights and consent gates before ingest and publish.
- Split final approval from public publication.

v1 assets can inform v2 projects, but the specification does not define an
automatic v1-to-v2 migration.

### v2 to v3 impact

Moving to v3 requires new or changed contracts for projects, shots, artifacts,
approvals, critiques, budgets, directives, and ledger records. Important changes
include:

- Shots add `story_time`, dialogue beats, `requires`, `effects`, handles, and
  originality comparison data.
- Artifact inputs become typed graph edges and add operation, lease, and spend
  information.
- Approvals change from simple artifact-hash binding to fingerprint plus
  reviewed-content evidence.
- The project manifest adds render, loudness, quality, localization,
  disclosure, and richer budget policies.
- Existing workflows must adopt per-shot states, graph propagation, scoped gate
  coverage, and commit-time input validation.

v3 defines an immutable schema migration policy, but an implementation still
needs explicit migration functions for each v2 artifact type.

## Overall assessment

The three versions represent distinct maturity levels rather than competing
creative designs.

- **v1 proves creative feasibility.** It describes the desired filmmaking flow
  and establishes the core human-in-the-loop strategy.
- **v2 proves architectural feasibility.** It defines durable contracts,
  governance, editorial interchange, auditability, and guarded publication.
- **v3 targets operational feasibility.** It defines parallel execution,
  change propagation, approval semantics, spending safety, continuity logic,
  reviewer actions, platform disclosure, and operator recovery.

v3 is the strongest implementation baseline, but it is also materially more
complex. It moves substantial work into the control plane before generation can
begin. That tradeoff is intentional: more up-front structure reduces duplicate
spend, stale approvals, continuity defects, unsafe publishing, and ambiguous
repair later in production.

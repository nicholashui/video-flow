# AI video generation pipeline v2

This document is the implementation baseline for the complete Video Flow v2
production system.

**Version:** 2.0  
**Status:** Implementation baseline  
**Date:** August 19, 2026  
**Supersedes:** `../v1/video-flow.md`

This specification defines a local-first, human-controlled system that turns a
structured storyline, shot instructions, and selected reference material into
multilingual, publication-ready video packages. It covers the production flow,
artifact contracts, agent boundaries, approval rules, quality controls, cost
controls, and implementation roadmap.

The system treats generation as one replaceable stage in a broader production
process. The durable core is the project state, editorial timeline, artifact
lineage, review history, and human approval record.

## Purpose and outcomes

The pipeline must produce repeatable creative work without removing human
editorial control. It must reduce expensive regeneration, preserve continuity,
and make every published asset traceable to approved inputs and decisions.

The required outcomes are:

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
- A human-approved, auditable publish action.

### Design principles

These principles resolve tradeoffs consistently across every implementation
phase.

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
   artifact hash, not an evolving filename.
8. **Keep publishing reversible until the last action.** Upload as private or
   unlisted first, verify the remote result, and require a second confirmation
   before making it public.

## What v2 changes

Version 2 preserves the useful v1 stage sequence while replacing assumptions
that would be fragile in production.

| v1 limitation | v2 resolution |
|---|---|
| Narrative phases lacked machine-enforced transitions. | A persisted state machine defines allowed transitions, owners, and gate evidence. |
| Fixed similarity values appeared universal. | Project-specific calibration converts metrics into gates. |
| The shot example was not valid JSON. | All contract examples are valid JSON and include schema versions. |
| Vendor model names were part of the architecture. | Capability-based adapters isolate changing vendors and models. |
| Remotion was the only proposed timeline source. | OpenTimelineIO is the canonical editorial model; Remotion and FFmpeg are render adapters. |
| Rights review was a note rather than a gate. | Rights, likeness, voice, music, and retention declarations block ingestion and publishing. |
| Human approval referred to mutable outputs. | Every approval records artifact hashes, scope, approver, and expiry. |
| Publishing was a single step. | Final master approval and publish authorization are separate gates. |
| Failure handling was descriptive. | Idempotency, retries, dead-letter states, and dependency invalidation are specified. |
| Output requirements focused on one MP4. | The delivery bundle separates mezzanine, upload, language, caption, metadata, and audit assets. |

## Scope and assumptions

This version targets short-form and compact narrative productions that can be
processed scene by scene. The architecture can scale to longer work, but v2 does
not claim unattended feature-film generation.

### In scope

The system covers the following production and operational capabilities.

- Storyline and shot-plan validation.
- Reference acquisition when the user has the right to acquire the material.
- Relevant-segment discovery, confirmation, trimming, and retention control.
- Keyframe, transition, camera, lighting, style, motion, and audio analysis.
- Visual bible, storyboard, wireframe, animatic, and style-frame workflows.
- Provider-neutral image, video, speech, transcription, translation, and
  scoring adapters.
- Multi-agent critique with bounded iteration and human arbitration.
- Editorial assembly, audio mixing, subtitles, packaging, and quality control.
- YouTube metadata generation, guarded upload, verification, and publication.
- Cost estimation, audit logging, provenance, and project recovery.

### Out of scope

The following capabilities require a separate specification.

- Automatic copyright clearance or legal advice.
- Circumvention of access controls, digital rights management, paywalls,
  geographic restrictions, or platform safeguards.
- Unattended creation of new dialogue that changes the approved story.
- Unauthorized voice cloning, likeness replication, or impersonation.
- Real-time collaborative editing or live video generation.
- Training foundation models as part of the production workflow.
- Guaranteed deterministic output from probabilistic generation models.

### Assumptions

The implementation uses these defaults until a project manifest overrides
them.

- One project has one locked frame rate, aspect ratio, and color profile.
- A project can contain horizontal, vertical, or cinematic output profiles, but
  each profile renders from a distinct timeline version.
- References inform shot grammar and do not become source footage in the final
  work unless the rights manifest explicitly permits reuse.
- The user supplies or approves all final story content.
- Human reviewers can reject any automated recommendation regardless of score.
- The initial deployment runs on Windows, with portable worker interfaces that
  do not depend on Windows-specific path syntax.

## Requirement baseline

Each requirement has a stable identifier. Tests, gate reports, and approval
records must cite these identifiers so that release evidence remains traceable.

### Input requirements

Inputs must be structured enough to validate before media processing begins.

| ID | Requirement |
|---|---|
| `IN-001` | The project must include a versioned manifest with title, logline, duration target, output profiles, primary language, locales, budget policy, and retention policy. |
| `IN-002` | Every scene and shot must have a stable identifier that never depends on display order. |
| `IN-003` | Every shot must define narrative purpose, timing intent, `when`, `what`, `how`, constraints, priority, and referenced entity identifiers. |
| `IN-004` | Every entity identifier must resolve to a character, prop, location, wardrobe item, or motif record before storyboard generation. |
| `IN-005` | Every external reference must include a source URL or local path, relevance hint, intended use, rights basis, and retention class. |
| `IN-006` | Validation errors must identify the field, requirement ID, source file, and remediation action. |

### Reference processing requirements

Reference processing must minimize storage and avoid interpreting availability
as permission.

| ID | Requirement |
|---|---|
| `REF-001` | The rights gate must pass before a remote reference is downloaded or a local reference is analyzed. |
| `REF-002` | The system must prefer direct time hints, then chapters, then multimodal search when locating a relevant segment. |
| `REF-003` | The system must preserve source metadata, selected timestamps, confidence evidence, and a SHA-256 hash of each retained segment. |
| `REF-004` | Low-confidence or conflicting segment matches must require human confirmation. |
| `REF-005` | Precise cuts must decode and re-encode around non-keyframe boundaries; approximate cuts can use stream copy. |
| `REF-006` | Full downloaded references must be deleted or quarantined after segment approval according to the retention policy. |

### Analysis and creative requirements

Analysis outputs must be structured, reviewable, and reusable by later stages.

| ID | Requirement |
|---|---|
| `ANA-001` | Each approved segment must yield representative keyframes with source timecodes and extraction rationale. |
| `ANA-002` | Each keyframe must include composition, blocking, camera, lens, lighting, palette, production design, atmosphere, motion, and audio observations. |
| `ANA-003` | Consecutive keyframes must include a transition analysis that distinguishes camera movement, subject movement, edit type, and environmental change. |
| `ANA-004` | Model observations must be labeled as observations, inferences, or unknowns. |
| `CRE-001` | A visual bible must define canonical descriptions, approved images, negative constraints, and versioned passports for recurring entities. |
| `CRE-002` | New shot designs must preserve narrative intent without directly copying distinctive protected expression from references. |
| `CRE-003` | Every shot must have start and end wireframes; shots with meaningful internal change must also have one or more intermediate wireframes. |
| `CRE-004` | Every shot must define camera motion, subject motion, transition behavior, duration, audio intent, and continuity dependencies. |
| `CRE-005` | A passport change must invalidate all unapproved descendants and queue approved descendants for impact review. |

### Workflow and approval requirements

The control plane must prevent agents and workers from bypassing human gates.

| ID | Requirement |
|---|---|
| `WF-001` | Every stage must be idempotent for the same inputs, configuration, adapter version, and operation key. |
| `WF-002` | The pipeline must resume from the last valid artifact after interruption. |
| `WF-003` | Automated critique must stop after the configured attempt or cost limit and escalate to a human. |
| `WF-004` | An agent must not approve an artifact that it generated. |
| `WF-005` | Gate A must approve the animatic before any paid or remote final-video generation. |
| `WF-006` | Gate B must approve selected clips before final editorial assembly is locked. |
| `WF-007` | Gate C must approve the complete master and delivery bundle. |
| `WF-008` | Gate D must authorize publication of the exact approved master hash and metadata hash. |
| `WF-009` | Approval records must include scope, artifact hashes, approver, timestamp, decision, comment, and expiry or revocation state. |

### Localization and packaging requirements

Language variants must preserve meaning while remaining independently
reviewable.

| ID | Requirement |
|---|---|
| `LOC-001` | The delivery bundle must include English, Putonghua, and Cantonese speech variants unless a project explicitly disables a language. |
| `LOC-002` | English, Simplified Chinese, and Traditional Chinese Cantonese subtitle tracks must be generated and reviewed. |
| `LOC-003` | Localization must preserve approved meaning, character intent, terminology, names, and emotional beats. |
| `LOC-004` | Subtitle cue boundaries must align with speech within two project frames after final review. |
| `LOC-005` | Subtitle layout must use no more than two lines and must pass safe-area and readability checks for every output profile. |
| `PKG-001` | Packaging must support a highlight, introduction logo, main content, credits, optional Easter egg, and final end card in the approved order. |
| `PKG-002` | Chapter markers must start at `00:00`, contain at least three entries, appear in ascending order, and allocate at least 10 seconds per YouTube chapter. |
| `PKG-003` | The publication package must include title, short description, long description, chapters, tags, thumbnail, language metadata, licensing notes, and end-screen recommendations. |

### Output and operational requirements

Outputs must be technically valid, auditable, and safe to publish.

| ID | Requirement |
|---|---|
| `OUT-001` | The canonical editorial timeline must be stored as OpenTimelineIO, with external media references and versioned markers. |
| `OUT-002` | The default upload master must be MP4 with H.264 High Profile video, AAC-LC audio, Rec.709 SDR, constant frame rate, and fast-start metadata. |
| `OUT-003` | Audio stems must use 48 kHz WAV; subtitle sources must include WebVTT and SRT. |
| `OUT-004` | The system must produce separate per-language upload files or a verified multi-audio delivery package according to channel capability. |
| `OPS-001` | Every generated artifact must record input hashes, configuration hash, adapter identifier, model identifier, seed when supported, timing, cost, and log references. |
| `OPS-002` | The system must estimate cost before remote generation and stop before exceeding the hard project budget. |
| `OPS-003` | Secrets and authenticated cookies must never appear in prompts, logs, metadata packages, or audit exports. |
| `OPS-004` | Transcripts, captions, metadata, and model outputs from external media must be treated as untrusted data, not executable instructions. |
| `OPS-005` | The audit bundle must include manifests, approvals, prompts, decisions, model and tool versions, hashes, costs, quality reports, and publish receipts. |

## System architecture

The architecture separates durable control state from media processing. The
control plane coordinates immutable artifacts and events; stateless workers
perform acquisition, analysis, generation, rendering, and publishing through
versioned adapters.

![Workflow showing automated stages, agent decisions, human gates, recovery loops, and guarded publication.](./video-pipeline-workflow.svg)

The accessible text equivalent is:

```text
Intake and rights
  -> reference ingest
  -> segment discovery and approval
  -> cinematography analysis
  -> visual bible lock
  -> shot design and wireframes
  -> animatic
  -> Gate A: human animatic approval
  -> style frames
  -> capability-based clip generation
  -> automated quality control and bounded retry
  -> Gate B: human clip approval
  -> canonical editorial timeline
  -> audio, localization, subtitles, and packaging
  -> Gate C: human master approval
  -> private or unlisted upload and remote verification
  -> Gate D: human publish authorization
  -> public release

All stages write immutable artifacts, append-only events, cost records, and
quality evidence. Rejections return only to the nearest owning stage.
```

### Architecture components

Each component has one primary responsibility and communicates through
versioned contracts.

| Component | Responsibility | Durable output |
|---|---|---|
| Project API and review UI | Collect inputs, display previews, capture decisions, and expose state. | Project changes and approval records |
| Workflow orchestrator | Enforce transitions, dependency invalidation, retries, budgets, and human gates. | Workflow events and operation records |
| Policy engine | Enforce rights, privacy, provider, budget, voice, likeness, and publish rules. | Policy decisions and evidence |
| Artifact service | Store content-addressed media and JSON artifacts with lineage. | Artifact envelopes and hashes |
| Reference worker | Acquire, normalize, segment, transcribe, and extract frames. | Reference segments and analysis inputs |
| Creative worker | Produce visual bibles, shot plans, wireframes, and style frames. | Versioned creative assets |
| Generation router | Match shot requirements to approved provider capabilities. | Generation jobs and candidate clips |
| Quality service | Run deterministic checks, calibrated metrics, and critic reviews. | Quality reports and remediation requests |
| Editorial service | Maintain OpenTimelineIO and render through Remotion or FFmpeg adapters. | Timeline versions and renders |
| Localization service | Translate, synthesize, align, caption, and package language variants. | Scripts, stems, and subtitle tracks |
| Publish service | Upload with least privilege, verify remote assets, and change visibility. | Upload and publication receipts |
| Audit exporter | Assemble reproducibility, rights, quality, cost, and approval evidence. | Signed audit bundle |

### State machine

The orchestrator accepts only the transitions in this table. A rejection moves
the project or affected shot to the owning state without deleting prior
artifacts.

| State | Required evidence | Allowed next state |
|---|---|---|
| `DRAFT` | Project manifest exists. | `VALIDATED` |
| `VALIDATED` | Input schema and cross-reference checks pass. | `RIGHTS_CLEARED` |
| `RIGHTS_CLEARED` | Rights and consent records pass policy. | `REFERENCES_INGESTED` |
| `REFERENCES_INGESTED` | Normalized media and metadata hashes exist. | `SEGMENTS_APPROVED` |
| `SEGMENTS_APPROVED` | Relevant ranges have human or calibrated automatic acceptance. | `ANALYSIS_APPROVED` |
| `ANALYSIS_APPROVED` | Keyframe and transition reports pass completeness checks. | `BIBLE_LOCKED` |
| `BIBLE_LOCKED` | Visual bible version has explicit approval. | `STORYBOARD_READY` |
| `STORYBOARD_READY` | All required shot wireframes and transitions exist. | `ANIMATIC_REVIEW` |
| `ANIMATIC_REVIEW` | Animatic render and review manifest exist. | `ANIMATIC_APPROVED` or `STORYBOARD_READY` |
| `ANIMATIC_APPROVED` | Gate A approval matches the animatic hash. | `CLIP_GENERATION` |
| `CLIP_GENERATION` | Candidate clips and generation manifests exist. | `CLIP_REVIEW` or `BLOCKED` |
| `CLIP_REVIEW` | Quality reports and contextual preview exist. | `CLIPS_APPROVED` or `CLIP_GENERATION` |
| `CLIPS_APPROVED` | Gate B covers all timeline clips. | `MASTER_REVIEW` |
| `MASTER_REVIEW` | Picture, audio, captions, packaging, and metadata pass checks. | `MASTER_APPROVED` or `CLIPS_APPROVED` |
| `MASTER_APPROVED` | Gate C matches delivery bundle hashes. | `UPLOAD_VERIFICATION` |
| `UPLOAD_VERIFICATION` | Remote upload is private or unlisted and verified. | `PUBLISH_AUTHORIZED` or `MASTER_REVIEW` |
| `PUBLISH_AUTHORIZED` | Gate D matches remote video, master, and metadata hashes. | `PUBLISHED` |
| `PUBLISHED` | Remote visibility and metadata verification pass. | Terminal state |
| `BLOCKED` | Failure record and remediation owner exist. | Owning prior state |

## Canonical artifact contracts

Every stage exchanges immutable, schema-versioned artifacts. Mutable project
views are projections built from these artifacts and the append-only event log.

### Artifact envelope

The envelope provides lineage and reproducibility for every JSON or media
artifact.

```json
{
  "schema": "video-flow/artifact-envelope",
  "schema_version": "2.0.0",
  "artifact_id": "art_01J6R4M8QF3W3R3W8M6QF0XK2A",
  "artifact_type": "reference.segment",
  "project_id": "prj_moon_gate",
  "scope_id": "shot_S03_02",
  "created_at": "2026-08-19T12:00:00Z",
  "created_by": "worker.reference.segmenter",
  "content_uri": "artifacts/sha256/7a/7a93...f2.mp4",
  "sha256": "7a93...f2",
  "byte_length": 18420393,
  "input_artifact_ids": ["art_01J6R4G88Q69W3FKS4JFN0MX1E"],
  "configuration_sha256": "c210...99",
  "adapter": {
    "id": "segmenter.local",
    "version": "2.0.0",
    "runtime": "python"
  },
  "generation": {
    "model_id": null,
    "model_version": null,
    "seed": null
  },
  "cost": {
    "currency": "USD",
    "estimated": 0.0,
    "actual": 0.0,
    "local_gpu_seconds": 31.8
  },
  "retention_class": "reference-derived-30d"
}
```

### Project manifest

The manifest declares project-wide invariants and policies. Shot-level records
cannot override these fields without creating a new output profile or policy
decision.

```json
{
  "schema": "video-flow/project",
  "schema_version": "2.0.0",
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
  "budget_policy": {
    "currency": "USD",
    "hard_limit": 25.0,
    "reserve_fraction": 0.2,
    "remote_generation_before_gate_a": false
  },
  "retention_policy": {
    "full_reference_days": 0,
    "approved_segment_days": 30,
    "final_project_days": 365
  }
}
```

### Shot specification

The shot contract carries creative intent separately from generated prompts.
Adapters translate this stable contract into provider-specific requests.

```json
{
  "schema": "video-flow/shot",
  "schema_version": "2.0.0",
  "shot_id": "shot_S03_02",
  "scene_id": "scene_S03",
  "display_order": 12,
  "duration": {
    "target_seconds": 4.5,
    "minimum_seconds": 3.8,
    "maximum_seconds": 5.2
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
  "continuity_in": ["char_antagonist:v3", "prop_jade_seal:v2"],
  "continuity_out": ["char_antagonist:v3", "prop_jade_seal:v2"],
  "constraints": ["period wardrobe", "no modern objects", "no visible text"],
  "references": ["ref_turn_reveal"],
  "priority": "hero"
}
```

### Approval record

An approval is immutable and applies only to the listed hashes. A changed file
requires a new approval even when its filename remains unchanged.

```json
{
  "schema": "video-flow/approval",
  "schema_version": "2.0.0",
  "approval_id": "apr_01J6R5B1XKQCF4YB8H6A2BTCPR",
  "project_id": "prj_moon_gate",
  "gate": "GATE_A_ANIMATIC",
  "scope": ["project"],
  "artifact_hashes": ["sha256:55b0...e1", "sha256:a342...90"],
  "decision": "approved",
  "approver_id": "human_director_01",
  "comment": "Timing and transitions approved for style-frame production.",
  "created_at": "2026-08-19T15:30:00Z",
  "expires_at": null,
  "revoked_at": null
}
```

### Project storage layout

The logical layout keeps source declarations separate from immutable artifacts
and human-readable exports. Implementations can map the artifact tree to a local
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
  timeline/
    edit-v001.otio
    edit-v002.otio
  reviews/
    approvals.jsonl
    decisions.jsonl
  exports/
    previews/
    delivery/
    audit/

artifacts/sha256/<first-two-hash-characters>/<full-hash>.<extension>
events/<project-id>.jsonl
operations/<operation-id>.json
```

## Detailed production flow

The production flow uses small, independently reviewable stages. Every stage
defines its inputs, outputs, and exit condition.

### Phase 0: Intake, validation, and rights gate

This phase prevents incomplete, unsafe, or unauthorized projects from entering
media processing.

1. Validate the project, story, scene, shot, entity, reference, and output
   schemas.
2. Resolve all identifiers and reject cycles in shot dependencies.
3. Record the rights basis for each reference, music track, voice, likeness,
   logo, font, and final-source asset.
4. Classify privacy, retention, and provider restrictions.
5. Estimate the project duration, shot count, storage, and cost envelope.
6. Produce an intake report and block progression until policy passes.

The phase exits with `VALIDATED` and `RIGHTS_CLEARED` events.

### Phase 1: Reference ingest and normalization

This phase creates a stable local analysis copy without committing to full-file
retention.

1. Inspect remote metadata before download when the source supports it.
2. Prefer user-supplied start and end hints and partial acquisition.
3. Use an approved downloader adapter only when platform terms and the rights
   manifest permit acquisition.
4. Normalize analysis proxies to a known pixel format, frame rate, audio sample
   rate, and time base.
5. Extract media metadata with `ffprobe` and preserve the raw tool report.
6. Hash the normalized proxy and mark the original for policy-driven deletion.

The phase exits when all usable references have normalized proxies or explicit
waivers.

### Phase 2: Relevant-segment discovery

This phase finds the smallest coherent interval that demonstrates the requested
filmmaking technique.

1. Generate candidate boundaries from user hints, chapters, detected cuts,
   transcript units, and overlapping windows.
2. Sample frames adaptively so cuts and high-motion intervals receive denser
   coverage.
3. Score each candidate against the shot instruction and reference hint.
4. Detect title cards, sponsorship, logos, dead air, and repeated outros as
   penalties, not automatic deletions.
5. Present the top candidates with evidence when confidence is not calibrated
   for automatic acceptance.
6. Refine approved boundaries to clean edit points and create a frame-accurate
   retained segment.

The phase exits with a segment decision, source time range, score breakdown,
transcript excerpt, representative frames, and retained-segment hash.

### Phase 3: Cinematography and transition analysis

This phase converts reference material into structured filmmaking observations,
not a prose-only caption.

1. Select keyframes using cut boundaries, visual novelty, action extrema, and
   camera-motion changes.
2. Describe composition, blocking, subject state, environment, lens cues,
   camera position, lighting, palette, texture, weather, and atmosphere.
3. Analyze optical flow and tracks to separate camera motion from subject
   motion.
4. Describe edit type, pacing, sound, speech, music, and silence across each
   keyframe interval.
5. Label uncertain properties and avoid inventing camera settings that cannot
   be inferred.
6. Run a completeness critic and human spot-check before approval.

The phase exits with machine-readable keyframe and transition reports plus a
human-readable contact sheet.

### Phase 4: Visual bible and passport lock

This phase converts narrative entities into stable continuity constraints.

1. Extract characters, props, locations, wardrobe, graphics, and recurring
   motifs from the complete story.
2. Create canonical descriptions and negative constraints.
3. Generate or attach approved identity sheets, turnarounds, color references,
   scale references, and material details.
4. Define project camera grammar, lighting rules, palette, texture, sound
   language, and forbidden elements.
5. Review every passport for internal conflicts and cross-shot usability.
6. Lock the visual bible and record Gate 0 approval for its exact version.

The phase exits with `BIBLE_LOCKED`. Later changes create a new version and an
impact report.

### Phase 5: Shot design and wireframes

This phase creates an original, editable plan for every shot before detailed
image generation.

1. Translate each shot contract into start, intermediate, and end beat
   descriptions.
2. Produce black-and-white wireframes with subject blocking, camera direction,
   screen direction, and safe areas.
3. Define camera and subject motion as separate curves or instructions.
4. Define transitions at both sides of the shot and verify handles for editing.
5. Run continuity, composition, narrative, motion, and production feasibility
   critics independently.
6. Revise within the configured attempt budget or escalate conflicting advice.

The phase exits when every required shot has an approved wireframe package.

### Phase 6: Animatic and Gate A

This phase validates the complete viewing experience at low cost.

1. Build an OpenTimelineIO sequence from shot durations and transitions.
2. Render wireframes with temporary motion, captions, narration, sound effects,
   and music placeholders.
3. Display shot identifiers and review markers in the review render only.
4. Validate runtime, pacing, narrative clarity, continuity, and packaging order.
5. Capture per-shot and timeline-range comments.
6. Require Gate A approval of the animatic and timeline hashes.

No paid or remote final-video generation can begin before this gate passes.

### Phase 7: Style frames and generation preparation

This phase turns approved composition into high-fidelity conditioning without
yet paying for full motion generation.

1. Create colored start, intermediate, and end style frames from approved
   wireframes and passports.
2. Evaluate identity, prop, location, palette, lighting, framing, and forbidden
   content.
3. Select approved frames and store all candidates with lineage.
4. Build provider-neutral motion, camera, negative, duration, and continuity
   requirements.
5. Estimate candidate count and generation cost by shot priority.
6. Reserve budget for retries and final hero-shot repair.

The phase exits when every shot has approved conditioning and a feasible route.

### Phase 8: Clip generation and automated quality control

This phase generates only the motion clips authorized by the approved animatic
and style frames.

1. Route each shot to an approved adapter based on required capabilities,
   privacy, cost, latency, duration, and quality evidence.
2. Generate the minimum useful candidate count for the shot priority.
3. Record complete request and response manifests with secrets removed.
4. Run decode, duration, frame-rate, corruption, safety, identity, continuity,
   motion, and artifact checks.
5. Rank candidates by calibrated evidence and critic rationale.
6. Retry only when the predicted quality gain justifies the remaining budget.

The phase exits with candidate clips, quality reports, and a recommended take.

### Phase 9: Contextual clip review and Gate B

This phase prevents locally good clips from damaging continuity in the complete
sequence.

1. Insert recommended takes into the latest animatic timeline.
2. Render each clip with at least the preceding and following shot.
3. Show deterministic failures separately from aesthetic recommendations.
4. Let the reviewer approve, reject, choose another take, trim, or request a
   targeted regeneration.
5. Record Gate B per shot and for the assembled sequence.
6. Invalidate only affected timeline ranges after a rejection.

The phase exits when every final clip hash is covered by Gate B.

### Phase 10: Canonical editorial assembly

This phase produces a reproducible picture lock while preserving interchange
with human editing tools.

1. Maintain the edit in OpenTimelineIO with clips, transitions, markers,
   handles, and metadata.
2. Render review and delivery outputs through Remotion or FFmpeg adapters.
3. Preserve source and record timecodes for every clip.
4. Apply approved speed changes, reframing, overlays, and transitions.
5. Export a picture-lock report and verify that no unapproved media appears.
6. Freeze a timeline version for audio and localization.

The phase exits with a picture-locked timeline and render hashes.

### Phase 11: Audio, speech, localization, and subtitles

This phase creates synchronized language variants from one approved intent
script and one picture lock.

1. Create an intent script with speaker, meaning, emotion, timing, terminology,
   and pronunciation notes.
2. Translate and adapt English, Putonghua, and Cantonese scripts without
   changing story facts.
3. Require consent records for cloned or synthetic voices modeled on a person.
4. Generate or record dialogue, then align it to picture and approved lip
   movement.
5. Build dialogue, music, ambience, and effects stems at 48 kHz.
6. Generate WebVTT and SRT subtitles, then run linguistic and visual review.
7. Mix each language variant against a project loudness profile and check peaks,
   clipping, phase, silence, and intelligibility.

The phase exits with approved scripts, stems, mixes, and subtitle tracks for
each locale.

### Phase 12: Packaging and publication metadata

This phase creates the complete viewer-facing package around the main content.

1. Select a spoiler-safe highlight from approved moments and keep it within the
   configured duration.
2. Add the approved logo bumper before the main content.
3. Add credits, the optional Easter egg, and the final end card in order.
4. Generate title, short description, long description, tags, and licensing
   notes from approved facts.
5. Generate chapter timestamps from the final timeline and validate YouTube
   chapter rules.
6. Generate and review a 1280 by 720 thumbnail with legible safe-area content.
7. Produce end-screen and playlist recommendations without changing the video.

The phase exits with a validated metadata manifest and packaging timeline.

### Phase 13: Master quality control and Gate C

This phase validates every final deliverable, not only the primary video file.

1. Decode every master to the final frame and inspect all streams with
   `ffprobe`.
2. Verify resolution, frame rate, color tags, sample rate, channel layout,
   duration, language tags, subtitle timing, and chapter timestamps.
3. Compare the rendered timeline against approved clip hashes and durations.
4. Run black-frame, freeze-frame, clipping, silence, caption overlap, and safe
   area checks.
5. Review every language version and packaging element in context.
6. Export the audit bundle and require Gate C approval of all delivery hashes.

The phase exits with an immutable, approved delivery manifest.

### Phase 14: Guarded upload and Gate D

This phase separates transfer to a platform from public release.

1. Use least-privilege OAuth credentials held by the publish service.
2. Upload the approved master as private or unlisted by default.
3. Apply approved metadata, thumbnail, captions, language data, and playlist
   membership.
4. Read the remote video record back and verify duration, processing state,
   metadata, visibility, captions, and thumbnail.
5. Present local and remote hashes or stable identifiers with the exact
   visibility change that will occur.
6. Require Gate D approval before changing visibility to public.
7. Verify the public state and save the platform receipt and URL.

The phase exits at `PUBLISHED`. A failed verification remains private or
unlisted and returns to the owning stage.

## Reference segment extraction algorithm

The extraction algorithm combines deterministic boundaries with multimodal
ranking. It never deletes source regions solely because a model labels them
irrelevant.

### Candidate construction

Candidate generation favors supplied evidence before inference.

1. Convert explicit timestamps and URL time parameters into highest-priority
   candidates.
2. Import source chapters and detected scene boundaries.
3. Add transcript sentence and speaker-turn intervals when speech exists.
4. Add overlapping windows between 3 and 20 seconds for uncovered regions.
5. Merge nearly identical intervals and preserve the origin of each boundary.

### Candidate scoring

Each candidate receives normalized evidence scores. Initial weights are a
starting profile and must be calibrated on accepted project examples.

$$
S(c) = 0.35V + 0.20T + 0.15H + 0.10A + 0.10M + 0.10B - P
$$

The variables are:

- $V$: visual-semantic similarity between sampled frames and the shot intent.
- $T$: transcript-semantic similarity when usable speech exists.
- $H$: agreement with the human relevance hint.
- $A$: agreement between independent visual and text analyses.
- $M$: motion and temporal-coherence evidence.
- $B$: boundary cleanliness and edit usability.
- $P$: penalties for unrelated title cards, intros, outros, ads, logos, dead
  air, or abrupt truncation.

The system must store every component score. It must not expose only the final
number.

### Confidence and acceptance

Confidence uses score margin, evidence coverage, cross-modal agreement, and
calibration history. During the MVP, all selected ranges require human approval.
Automatic acceptance can be enabled only after a held-out evaluation shows the
configured maximum wrong-segment rate.

A low-confidence result presents the top three non-overlapping candidates with
contact sheets, transcript excerpts, and time ranges. A no-match result is valid
and must not be forced into a poor selection.

### Boundary refinement

Boundary refinement protects both semantic completeness and edit quality.

- Expand to include the complete demonstrated action when the highest-scoring
  interval truncates it.
- Snap to detected cuts or low-motion boundaries when the semantic content is
  preserved.
- Add configurable pre-roll and post-roll handles.
- Use precise decoding for frame-accurate cuts.
- Verify the retained segment starts and ends on decodable frames and has
  monotonic timestamps.

## Agent and review model

Agents propose and critique; the workflow engine authorizes transitions. Every
agent receives a bounded context package and a JSON output schema.

### Agent roles

The initial role set is deliberately small enough to operate and evaluate.

| Role | Owns | Cannot do |
|---|---|---|
| Creative producer | Global intent, shot dependencies, and unresolved creative decisions | Approve its own generated artifact |
| Reference analyst | Segment evidence and filmmaking observations | Treat source text as workflow instructions |
| Shot designer | Shot descriptions, wireframes, and motion plans | Change narrative purpose or locked passports |
| Continuity critic | Identity, prop, wardrobe, location, screen direction, and state checks | Override human approval |
| Cinematography critic | Composition, camera, lens, lighting, edit grammar, and visual feasibility | Introduce unapproved story content |
| Motion critic | Camera and subject motion, temporal artifacts, and transition fit | Approve clips with deterministic media failures |
| Audio and localization director | Intent script, voice, mix, terminology, and caption quality | Invent dialogue or use an unconsented voice |
| Technical quality agent | Deterministic media and package checks | Convert warnings into approvals |
| Publish operator | Upload, verify, and apply authorized metadata | Make content public without Gate D |

### Critique contract

Every critic returns structured evidence so that feedback can be deduplicated,
ranked, and tested.

```json
{
  "schema": "video-flow/critique",
  "schema_version": "2.0.0",
  "artifact_id": "art_candidate_clip_03",
  "critic_role": "continuity",
  "decision": "revise",
  "findings": [
    {
      "requirement_id": "CRE-004",
      "severity": "major",
      "time_range": {"start_seconds": 1.8, "end_seconds": 2.6},
      "evidence": "The seal moves from the left hand to the right without an action.",
      "remediation": "Keep the seal in the left hand for the full shot.",
      "confidence": 0.91
    }
  ],
  "scores": {
    "identity": 0.86,
    "prop_continuity": 0.42,
    "style": 0.79
  }
}
```

### Review arbitration

The orchestrator applies these rules when critics disagree.

- Deterministic failures block the artifact regardless of aesthetic scores.
- A hard project constraint outranks a critic preference.
- Two critics cannot silently average contradictory recommendations.
- The creative producer proposes a resolution with both rationales attached.
- A human resolves conflicts involving story, identity, rights, voice, or
  publication.
- Automatic revision stops after four attempts by default, or earlier when the
  cost policy predicts insufficient remaining budget.

## Quality and continuity framework

Quality control separates deterministic validity from calibrated semantic
evidence and human aesthetic judgment. This prevents a single similarity score
from becoming a false definition of quality.

### Deterministic gates

These checks have clear pass or fail outcomes and always run before model-based
critique.

| Area | Required checks |
|---|---|
| Media integrity | File opens, decodes to end, has monotonic timestamps, and contains expected streams. |
| Video profile | Resolution, pixel format, frame rate, color tags, duration, and codec match the output profile. |
| Audio profile | Sample rate, channel layout, duration, peaks, silence policy, and language tags match the manifest. |
| Captions | Files parse, cues are ordered, cues do not have invalid overlap, text fits line policy, and timing passes `LOC-004`. |
| Timeline | Every final clip hash has Gate B approval and every range maps to an OpenTimelineIO item. |
| Packaging | Required elements appear once and in the approved order. |
| Metadata | Chapter rules, title length, required descriptions, language metadata, and licensing fields pass. |
| Audit | Referenced artifacts exist, hashes match, secrets are absent, and Gate C evidence is complete. |

### Calibrated semantic checks

Semantic checks rank risk and guide review. They become blocking only after
calibration against accepted and rejected examples for the project style.

| Dimension | Candidate evidence | Calibration target |
|---|---|---|
| Face identity | Face embedding, landmark stability, and human labels | Minimize wrong-identity acceptance on held-out frames. |
| Full appearance | Image embeddings, clothing attributes, silhouette, and palette | Detect meaningful costume or body drift without rejecting pose changes. |
| Prop continuity | Detection, crop embeddings, state attributes, and hand association | Detect identity, state, and placement errors. |
| Location continuity | Scene embeddings, layout features, horizon, and lighting | Detect unexplained environment changes. |
| Style continuity | Palette, contrast, grain, lens cues, and aesthetic embeddings | Detect outliers while preserving intentional emphasis. |
| Motion quality | Optical flow, track stability, temporal warping, and critic labels | Detect flicker, morphing, impossible motion, and camera discontinuity. |
| Audio and lip alignment | Phoneme timing, mouth motion, speech boundaries, and human labels | Detect perceptible synchronization errors by locale. |

The v1 values such as `0.72` for face similarity and `0.78` for general image
similarity can seed an experiment, but they are not production gates until the
calibration set demonstrates their error rates.

### Calibration procedure

Each metric profile must be reproducible and tied to a model version.

1. Label accepted and rejected pairs from the target project or a representative
   pilot.
2. Split labels by entity, shot type, lighting condition, and generation route.
3. Select thresholds on a training split against an explicit false-accept and
   false-reject policy.
4. Verify thresholds on a held-out split.
5. Record the dataset hashes, model version, threshold, confusion matrix, and
   review owner.
6. Recalibrate after model, preprocessing, passport, or style-profile changes.

## Capability-based model routing

The core specification names capabilities, not preferred vendors. A registry
maps approved adapters to current providers and local models.

### Adapter declaration

Every generation adapter must declare these fields before it can receive work.

- Supported input types: text, image, start frame, end frame, pose, depth,
  audio, or video.
- Maximum duration, resolution, aspect ratios, frame rates, and output formats.
- Camera, motion, lip-sync, character-reference, and negative-prompt support.
- Seed and reproducibility behavior.
- Safety, retention, training-use, region, and privacy terms.
- Cost formula, queue behavior, timeout, cancellation, and refund behavior.
- Version identifier and last verification date.

### Routing policy

The router applies hard constraints before ranking eligible adapters.

$$
R(a, s) = Q(a, s) - \lambda_c C(a, s) - \lambda_l L(a, s)
          - \lambda_p P(a, s) - \lambda_r U(a, s)
$$

The terms represent predicted quality, cost, latency, privacy exposure, and
uncertainty for adapter $a$ and shot $s$. Project policy sets the weights. An
adapter that violates a hard privacy, rights, duration, or budget constraint is
ineligible regardless of score.

The fallback order is local preferred adapter, approved remote standard
adapter, approved remote hero adapter, simplified motion plan, then human
escalation. The router must never silently reduce a story constraint.

## Cost and resource controls

Cost control is enforced before and during execution. Displaying an estimate
without a stop mechanism does not satisfy `OPS-002`.

### Budget policy

The default policy uses the following controls.

- Reserve 20 percent of the hard budget for repair and final delivery.
- Block remote video generation before Gate A.
- Require a revised estimate when shot count, duration, candidate count, or
  adapter changes materially.
- Stop new remote jobs when committed cost plus reserve reaches the hard limit.
- Count timed-out and failed paid jobs according to the provider billing
  response, not an assumed refund.
- Report cost by project, scene, shot, stage, adapter, accepted take, and
  rejected take.

### Local resource profiles

Hardware detection chooses a profile rather than assuming 16 GB of video
memory.

| Profile | Typical use |
|---|---|
| CPU only | Download, FFmpeg proxy work, scene detection, metadata, timeline, and lightweight embeddings. |
| GPU 8 GB | Quantized transcription, lightweight vision-language analysis, and limited image work. |
| GPU 16 GB | Higher-quality local analysis, embeddings, style frames, and selected low-resolution motion models. |
| GPU 24 GB or more | Larger local vision-language models, higher-resolution image work, and broader local video options. |

Each adapter must publish an estimated memory requirement and fall back cleanly
when capacity is insufficient. The pilot benchmarks actual wall time before the
project displays delivery estimates.

## Security, rights, and provenance

Media pipelines combine untrusted files, external text, model calls, secrets,
and public publishing. Security and rights controls therefore apply at every
stage rather than only at upload.

### Rights and consent controls

The policy engine must enforce these records.

- Reference acquisition and analysis basis.
- Permission for any source footage included in the final edit.
- Music, sound-effect, font, logo, and stock-asset licenses.
- Likeness and synthetic-performer consent.
- Voice recording or voice-cloning consent, allowed languages, and allowed
  uses.
- Territory, channel, expiry, attribution, and retention restrictions.

The ability of `yt-dlp` or another tool to access a URL is not evidence of
authorization. The system must not bypass access controls or use authenticated
cookies outside the approved source and purpose.

### Untrusted content controls

The analysis boundary treats all external content as data.

- Do not concatenate transcripts, captions, comments, descriptions, or metadata
  into system instructions.
- Escape paths and pass subprocess arguments as arrays, not shell strings.
- Disable untrusted downloader plugins and remote components by default.
- Validate MIME type, extension, container, stream count, duration, and decode
  limits before analysis.
- Run media tools with restricted filesystem access, timeouts, memory limits,
  and network policy.
- Redact cookies, OAuth tokens, local usernames, and provider request headers
  from logs and exports.

### Provenance and audit

SHA-256 lineage is mandatory. A C2PA manifest is an optional delivery feature
when the chosen signing and platform tools support it; the absence of C2PA does
not weaken the internal audit requirements.

The audit bundle contains:

- Input manifests and rights records.
- Tool, adapter, and model versions.
- Prompts, seeds, parameters, and response identifiers.
- Artifact envelopes and hashes.
- Agent critiques and human decisions.
- Cost estimates and actual cost records.
- Timeline versions and render commands.
- Quality reports and exception waivers.
- Upload, verification, and publication receipts.

## Reliability and recovery

The workflow distinguishes transient failures, deterministic defects, policy
blocks, and human rejections. Each category has a different recovery path.

| Failure class | Example | Recovery |
|---|---|---|
| Transient infrastructure | Network timeout or temporary provider error | Retry with exponential backoff and jitter within operation limits. |
| Capacity | Local out-of-memory or provider queue saturation | Select an approved lower-resource route or pause for capacity. |
| Deterministic input | Corrupt media or invalid schema | Block and request corrected input; do not retry unchanged work. |
| Quality | Identity drift or motion artifact | Revise the smallest owning prompt, conditioning asset, or shot route. |
| Policy | Missing rights, consent, budget, or provider permission | Block until a human supplies valid evidence or changes scope. |
| Human rejection | Pacing, design, language, or performance concern | Create a decision record and invalidate only dependent descendants. |
| Publish verification | Remote processing, metadata, caption, or visibility mismatch | Keep private or unlisted, repair, and repeat verification. |

### Idempotency and retries

Every operation key is the hash of stage, input artifact hashes,
configuration hash, and adapter version. A repeated operation with the same key
returns the existing valid artifact unless the user explicitly requests a new
candidate.

The default retry policy permits three transient retries with capped
exponential backoff. Generation-quality retries are separate, default to four,
and consume the shot budget. Deterministic failures and policy blocks do not
retry automatically.

### Dependency invalidation

The artifact graph drives surgical repair.

- A changed transcript invalidates language alignment and captions, not picture
  generation.
- A changed shot duration invalidates downstream timeline, audio timing,
  captions, chapters, packaging, masters, and publish approvals.
- A changed passport triggers impact review for every dependent style frame and
  clip.
- A changed final master revokes Gate C and Gate D automatically.
- A metadata-only change preserves Gate C but requires new metadata approval
  and Gate D.

## Delivery bundle

The delivery bundle separates editorial sources from platform uploads so that
the project can be repaired or republished without regenerating creative work.

```text
delivery/<release-id>/
  manifest.json
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
  timeline/
    final.otio
  reports/
    media-qc.json
    language-qc.json
    rights-qc.json
  audit/
    audit-manifest.json
    approvals.jsonl
    artifact-hashes.sha256
```

The picture mezzanine codec is configurable because production environments
have different archival requirements. Upload outputs must satisfy `OUT-002`.
When a channel supports verified alternate audio tracks, the bundle can include
a multi-audio mezzanine in addition to separate language uploads.

## Recommended implementation stack

The stack favors stable interchange and command interfaces. Exact dependency
versions belong in lockfiles and deployment manifests, not in this long-lived
architecture document.

| Concern | Recommended baseline | Reason |
|---|---|---|
| Control plane | Python service with an explicit workflow state machine | Strong media and machine-learning ecosystem with testable transitions |
| Project database | SQLite in WAL mode for single-node MVP; PostgreSQL for multi-worker deployment | Local-first simplicity with a clear scale path |
| Artifact store | Content-addressed filesystem; S3-compatible storage when distributed | Immutable lineage and deduplication |
| Acquisition | `yt-dlp` adapter with policy checks and structured JSON output | Broad source support and partial-download capability |
| Media processing | FFmpeg and `ffprobe` | Mature stream, filter, transcode, metadata, and validation support |
| Scene detection | PySceneDetect | Multiple detectors and OpenTimelineIO output support |
| Editorial interchange | OpenTimelineIO | Model-neutral clips, tracks, transitions, markers, and metadata |
| Rendering | FFmpeg baseline; Remotion adapter after license review | Deterministic media core with optional code-driven graphics and review UI |
| Review UI | Web application with frame-accurate comments and approval actions | Central human gate and decision capture |
| Agent integration | Provider-neutral structured-output interface | Prevent framework or model lock-in |
| Metrics | Local embedding, detection, optical-flow, and alignment adapters | Low-cost evidence with calibratable versions |
| Publishing | YouTube Data API adapter with OAuth and remote verification | Auditable upload and metadata operations |

## Implementation roadmap

The roadmap delivers thin, testable vertical slices. Each milestone can operate
without the later milestones and has an explicit exit criterion.

### Milestone 0: Contracts and control plane

This milestone establishes the durable foundation before adding models.

**Deliverables:**

- JSON Schemas for project, scene, shot, entity, reference, artifact, critique,
  approval, quality report, operation, and delivery manifest.
- SQLite schema for projects, events, artifacts, dependencies, operations,
  approvals, costs, and policies.
- State-machine transition service with idempotency keys.
- Content-addressed local artifact store.
- Command-line interface for project validation and state inspection.

**Exit criteria:**

- Invalid transitions and stale approvals fail deterministically.
- A project can stop and resume without duplicate artifacts.
- Contract tests cover every schema and requirement from `IN-001` through
  `WF-009`.

### Milestone 1: Reference-analysis vertical slice

This milestone proves the low-cost local reference workflow on real samples.

**Deliverables:**

- Rights gate and reference metadata capture.
- `yt-dlp`, FFmpeg, `ffprobe`, PySceneDetect, transcription, embedding, and
  segment-ranking adapters.
- Segment-candidate review screen with contact sheets and transcripts.
- Frame-accurate trimming, retention cleanup, and artifact lineage.
- Structured keyframe and transition reports.

**Exit criteria:**

- A pilot with at least five varied references selects the reviewer-approved
  interval or returns no match.
- Interrupted downloads and analyses resume safely.
- Full-source retention follows the manifest exactly.
- No remote model is required for the baseline path.

### Milestone 2: Visual bible, storyboard, and Gate A

This milestone proves that humans can approve the complete production at low
fidelity.

**Deliverables:**

- Entity extraction and passport editor.
- Visual bible versioning and dependency impact reports.
- Shot-design and wireframe adapters.
- Structured critic service with bounded iteration.
- OpenTimelineIO animatic builder and review render.
- Frame-accurate review comments and Gate A approval.

**Exit criteria:**

- A canonical pilot project with three scenes and at least eight shots reaches
  Gate A without paid video generation.
- Passport changes identify every dependent shot.
- Rejected shots rerender only affected timeline ranges.

### Milestone 3: Style frames, clip generation, and Gate B

This milestone adds expensive generation behind budget and privacy controls.

**Deliverables:**

- Style-frame generation and selection.
- Capability registry and at least one local and one remote clip adapter.
- Cost reservation, cancellation, and actual-cost reconciliation.
- Deterministic media QC and versioned semantic metrics.
- Contextual clip review and Gate B approval.

**Exit criteria:**

- The pilot can route, generate, reject, retry, and approve each shot without
  exceeding its hard budget.
- The quality service preserves component evidence rather than one opaque score.
- No remote request is possible before Gate A.

### Milestone 4: Editorial, audio, localization, and Gate C

This milestone creates complete multilingual delivery bundles.

**Deliverables:**

- Canonical OpenTimelineIO picture lock and render adapters.
- Intent script, translation, terminology, TTS or recorded-voice, and alignment
  workflows.
- Audio stem mixing and subtitle generation for all three locales.
- Highlight, logo, credits, Easter egg, end-card, chapters, and thumbnail tools.
- Full media, language, packaging, rights, and audit quality reports.
- Gate C approval over the delivery manifest.

**Exit criteria:**

- All language outputs decode and remain synchronized to the same picture lock.
- Captions pass timing, line, safe-area, encoding, and linguistic review.
- The audit exporter reconstructs every delivery asset from lineage records.

### Milestone 5: Guarded YouTube publication and Gate D

This milestone adds the only public side effect after all local production work
is stable.

**Deliverables:**

- OAuth credential integration with least-privilege storage.
- Dry-run publication manifest and exact-action confirmation.
- Private or unlisted upload, metadata, caption, thumbnail, and playlist
  operations.
- Remote processing and metadata verification.
- Gate D visibility authorization and publication receipt.

**Exit criteria:**

- A repeated upload request does not create duplicate public videos.
- A verification failure remains non-public.
- Only a human approval matching the remote and local artifact identifiers can
  make the video public.

## Test strategy

Tests scale from contracts to a complete publish rehearsal. The canonical pilot
uses synthetic or explicitly licensed media so that automated tests do not
depend on third-party content.

### Test layers

The implementation must include these layers.

- **Schema tests:** Validate accepted, rejected, upgraded, and downgraded
  artifacts.
- **State tests:** Exercise every allowed and forbidden transition, revocation,
  expiry, and resume path.
- **Unit tests:** Cover scoring components, boundary construction, invalidation,
  budget math, chapter generation, path handling, and redaction.
- **Adapter contract tests:** Run each adapter against recorded fixtures and
  validate normalized outputs and errors.
- **Media integration tests:** Generate short media fixtures and verify cuts,
  time bases, streams, captions, renders, and hashes with FFmpeg.
- **Golden analysis tests:** Compare scene boundaries, keyframes, segment
  candidates, and transition classifications against reviewed fixtures.
- **Quality calibration tests:** Reproduce thresholds and confusion matrices
  from immutable labeled datasets.
- **Resilience tests:** Interrupt workers, corrupt caches, exhaust budgets,
  simulate timeouts, and verify idempotent recovery.
- **Security tests:** Inject hostile filenames, metadata, transcript text,
  oversized media, invalid containers, and redaction canaries.
- **End-to-end tests:** Run the canonical pilot through Gate C with fake remote
  adapters and through Gate D in a non-public YouTube test channel.

### Release gates

A release candidate is acceptable only when all of these conditions hold.

1. Every requirement ID maps to at least one automated test or recorded human
   verification.
2. No critical or major deterministic media failure remains open.
3. All approval and publish bypass tests fail closed.
4. The canonical pilot resumes successfully after interruption at every stage.
5. The audit bundle verifies all hashes and contains no secret canaries.
6. Cost reconciliation matches provider receipts within the configured
   rounding tolerance.
7. The workflow SVG, Markdown links, JSON examples, and XML parse checks pass.

## Operational metrics

Operational metrics measure whether the pipeline reduces waste and preserves
quality. They do not substitute for creative review.

- Gate A approval rate before remote generation.
- Generated seconds per accepted second.
- Cost per accepted shot and per finished minute.
- Automatic retry count and human intervention count per shot.
- Median time from rejection to replacement preview.
- Percentage of descendants correctly invalidated after a change.
- False-accept and false-reject rates for each calibrated quality metric.
- Resume success after worker interruption.
- Publish verification failures and unintended-publication count.
- Storage by retention class and overdue-deletion count.

The target for unintended publication, rights-gate bypass, secret leakage, and
approval bypass is zero.

## Decisions and extension points

The following defaults are intentional and can change through versioned
architecture decisions.

- OpenTimelineIO is the canonical timeline; Remotion is a render and graphics
  adapter, not the sole source of editorial truth.
- SQLite is the single-node MVP database; PostgreSQL is the distributed-worker
  upgrade path.
- The local filesystem is the MVP artifact store; S3-compatible storage is the
  distributed upgrade path.
- Automatic segment acceptance is disabled until calibration passes.
- Publishing uploads privately or as unlisted before public authorization.
- Provider and model selection lives in a capability registry that can change
  without changing shot contracts.
- C2PA signing is optional in v2, while internal hashes and audit lineage are
  mandatory.

## Source notes

The v2 design uses stable capabilities documented by the following official
projects and platforms. These sources were reviewed on August 19, 2026.

- [yt-dlp documentation][yt-dlp] documents structured metadata, partial
  downloads, retries, post-processing, and security-sensitive options.
- [FFmpeg documentation][ffmpeg] documents precise seeking, stream copy,
  transcoding, stream mapping, filters, chapters, metadata, progress, and
  validation behavior.
- [PySceneDetect documentation][pyscenedetect] documents multiple detectors,
  keyframe image output, splitting, and OpenTimelineIO export.
- [OpenTimelineIO documentation][otio] defines an editorial interchange model
  for clips, timing, tracks, transitions, markers, and external media links.
- [YouTube video chapters guidance][youtube-chapters] defines chapter timestamp
  constraints used by `PKG-002`.
- [YouTube Data API video insert documentation][youtube-upload] defines the
  upload interface used by the guarded publish adapter.
- [C2PA specification][c2pa] provides an optional standard for signed content
  provenance manifests.
- The [Remotion project][remotion] informs the optional code-driven render and
  motion-graphics adapter. Adoption requires review of its current license.

[yt-dlp]: https://github.com/yt-dlp/yt-dlp
[ffmpeg]: https://ffmpeg.org/ffmpeg.html
[pyscenedetect]: https://www.scenedetect.com/docs/latest/
[otio]: https://opentimelineio.readthedocs.io/en/latest/
[youtube-chapters]: https://support.google.com/youtube/answer/9884579?hl=en
[youtube-upload]: https://developers.google.com/youtube/v3/docs/videos/insert
[c2pa]: https://spec.c2pa.org/specifications/specifications/2.4/index.html
[remotion]: https://github.com/remotion-dev/remotion

## Next steps

Begin with Milestone 0 and keep every later adapter behind the versioned
contracts. Use the reference-analysis vertical slice as the first behavior-level
proof, then require a complete Gate A pilot before integrating paid generation.
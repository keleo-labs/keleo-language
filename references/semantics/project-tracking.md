[< Back to Semantic Guidance Hub](../semantics.md)

## 12 Project Execution Tracking

The Practice Language defines practices, methods, and baselines as methodology specifications — they describe *what should be done*. The Project type bridges the gap to execution, providing a structure for tracking *what is being done* against those specifications. A Project is an execution instance of a Practice or Method, recording team composition, a tailored plan, the currently assessed state of tracked concerns and artifacts, and the desired target state.

### 12.1 Project Purpose and Root Discrimination

A Project is distinct from Practice, Method, and PracticeBaseline. While those types define methodology constructs, a Project tracks real-world progress against a selected methodology. It is identified at the root level by the presence of `practiceName` or `methodName` — properties unique to the Project type.

**Root Discrimination:** The schema's if/then/else chain evaluates Project discrimination *before* the existing Method/Practice/PracticeBaseline checks. A document containing `practiceName` or `methodName` is validated as a Project; documents without these properties fall through to the existing discrimination logic.

**Practice/Method Reference:** A Project MUST name exactly one Practice or Method via an exclusive-or constraint:

- `practiceName` — symbolic link to a Practice (by name)
- `methodName` — symbolic link to a Method (by name)

Any system managing a Project would need to resolve all of the referenced Practice or Method's dependencies (including baseline and dependent practices) so the user operates against a single merged virtual practice. The resolution mechanism is a tooling concern, not a schema concern.

**Metadata:** Projects carry the same provenance metadata as Practice and PracticeBaseline: `authors`, `createdAt`, `updatedAt`, `version`, and `keywords`. Projects may also include `citations`, `acknowledgements`, and `assets`.

**Project-wide links:** The optional `links` array (ExternalLink objects) holds external references that describe the project as a whole rather than a specific tracked alpha/work-product instance — for example a remembered Smartsheet workspace/folder/plan URL, a team charter document, or a way-of-working document. Instance-specific links belong on that AlphaInstance/WorkProductInstance's own `links` instead.

### 12.2 Team Structure and Team API Principles

The Project's `team` property is inspired by the Team API concept from Team Topologies (Skelton & Pais). The Team API's core objective is to reduce cognitive load by making a team's purpose, membership, and communication preferences immediately discoverable. The Project schema distils this into three types:

**TeamEntry** — describes the project team:

- `name` and `description` establish the team's identity and purpose, answering "what does this team do and why does it exist?"
- `members` lists the individuals on the team (array of TeamMember objects)
- `communicationChannels` (optional) lists how to interact with the team (array of CommunicationChannel objects)
- `notes` (optional) captures team-level observations, decisions, and changes over time

**TeamMember** — identifies an individual team member:

- `name` and `contact` make the person findable and reachable
- `personaName` links the member to a Persona defined in the resolved practice/method scope, connecting real people to methodology-defined roles
- `role` (optional) is free text describing this member's specific responsibility on this project, complementing `personaName` when the generic persona doesn't capture project-specific nuance (e.g. `personaName: "ESA Manager"` with `role: "Sponsor / escalation path"`)
- `started` and `finished` (both optional) record when the member joined and left the project, supporting temporal membership tracking without overcomplicating the structure

**CommunicationChannel** — a team interaction point:

- `name` provides a human-readable label (e.g. "Slack", "Team Email", "Weekly Sync")
- `address` provides the channel's location (e.g. "#platform-eng", "platform@example.com", "Tuesdays 10:00 UTC")

**Validation:** All `personaName` entries in TeamMember objects must reference Personas defined in the resolved practice/method scope.

### 12.3 Plan Section and Pattern Ownership

The `plan` section establishes the project's lifecycle objectives. It contains an embedded Pattern (a new instance, not a symbolic link) and a notes array for plan-level commentary.

**Pattern as Project-Owned Declaration:** The plan's Pattern is a full declaration using the existing Pattern type, owned by the project and freely modifiable by the user. As a new instance rather than a reference, users can add, remove, or reorder PatternViews, adjust alpha state targets, and extend the pattern with objectives specific to their project. The Pattern type is extended with optional `alphaInstanceNames` and `workProductInstanceNames` arrays, allowing the Pattern to explicitly declare which instances are being tracked.

**Instance Declaration Vocabulary:** The Pattern's `alphaInstanceNames` array declares the alpha instances tracked by this project (e.g. "Platform Engineering Team" as an instance of the "Team" alpha). The `workProductInstanceNames` array declares the work product instances. These declarations provide the vocabulary that the Pattern's views reference when specifying phased objectives via AlphaInstance and WorkProductInstance objects. Optional `relatesTo` on those Name objects (and optional mirrors on current/target/cycle instances) records which tracked occurrences are associated — including concern ↔ work product — applying type-level `relatesTo` / `contributesTo` / `partOf` / purpose. Pairings are not inferred during merge; they are not a substitute for `evidenceBy`. See [Section 6.7](alphas.md#67-instance-relationships-applying-type-edges-to-named-instances).

**Plan Notes:** The plan's `notes` array captures changes, updates, and rationale about the planning process itself — commentary that is about the plan rather than part of the plan content (which lives in the Pattern).

**Tooling Guidance:** Systems supporting this schema should allow users to clone an existing Pattern from the resolved practice/method scope as a starting point for their plan. The cloned Pattern becomes an independent copy owned by the project. Tooling should ensure all tracked items are represented as AlphaInstanceName or WorkProductInstanceName declarations within the Pattern, defaulting instance names to names derived from the alpha/work product name when the user has not explicitly named them.

**External Planning Tool Sync:** The plan's optional `sync` object remembers the configuration for mirroring this plan to an external planning tool (e.g. Smartsheet, Jira) — tool-agnostic by design, so this schema does not encode any one vendor's vocabulary. `sync.tool` names the tool; `sync.link` (an `ExternalLink`) is the single source of truth for the live external plan this project currently syncs with; `sync.layout` is an optional, tool-defined view/layout identifier (e.g. Smartsheet's `"traditional" | "agile"`, per that tool's own sync contract — see `specifications/project-plan.md` in keleo-userskillz). Historical or secondary sync targets (e.g. a second sheet from a prior layout) belong on `Project.links`, not here — `sync.link` only ever holds the currently active target.

### 12.4 Current, Target, and Cycles

The `current`, `target`, and `cycles` sections serve complementary purposes:

- **Current** provides an assessed statement of the current status — "where are we now?" Its checklist states declare what has been completed, what remains, and what will not be completed.
- **Target** provides a statement of intent — "where do we want to be?"
- **Cycles** track the operational work — "what are we doing to get there?" (see [Section 12.7](#127-cycles-and-operational-work-tracking))

Both sections contain:

- `alphaInstances` — array of AlphaInstance objects, each referencing an alpha and its assessed (or target) state. Each AlphaInstance may carry a `checklistStates` array for granular checklist tracking.
- `workProductInstances` — array of WorkProductInstance objects, each referencing a work product and its assessed (or target) level of detail. Each WorkProductInstance may carry a `checklistStates` array.
- `notes` — optional array of Note objects for timestamped observations and commentary

The target section allows users to define objectives that may differ from the full pattern — for example, targeting a subset of alpha states or marking certain checklist items as not required.

### 12.5 ChecklistState and Evidence Tracking

ChecklistState tracks the completion status of individual checklist items within the project context. It provides a bridge between the practice-defined checklists (on Alpha States and WorkProduct LevelsOfDetail) and real-world execution.

**Co-location:** ChecklistState objects live on AlphaInstance and WorkProductInstance via their optional `checklistStates` arrays. Because they are co-located on the parent instance, the parent context (alphaName + stateName, or workProductName + levelOfDetailName) already identifies which checklist the item belongs to. ChecklistState itself needs only `checklistName` to identify the specific item.

**Structure:**

- `checklistName` — must match a `Checklist.name` within the parent instance's referenced State or LevelOfDetail
- `state` — enum: `"complete"`, `"not complete"`, `"not required"`
- `evidence` (optional) — an ExternalLink referencing external evidence supporting the item's state (e.g. a document, test result, approval record, or audit artifact)
- `notes` (optional) — array of Note objects for recording observations or rationale

**Dual-Use Semantics:**

- In the `current` section: `state` records actual completion — `"complete"` or `"not complete"`
- In the `target` section: `state` indicates requirement — `"not required"` marks checklist items explicitly excluded from this project's goals, while `"complete"` marks items that must be achieved

#### 12.5.1 Priority Threshold

The `priorityThreshold` property on Project and ProjectCycle enables teams to scope which checklist items are active based on their `priority` level (see [Section 5.2.2](practice-elements.md#522-checklist-priority)). Items at or above the threshold are in scope; items below it are implicitly not required.

**Threshold Semantics:**

The priority levels form an ordered hierarchy: `"must"` > `"should"` > `"could"`. A threshold of `"should"` includes items with priority `"must"` or `"should"`, and excludes items with priority `"could"`.

| Threshold value | Items in scope |
|---|---|
| `"could"` | All items (`must` + `should` + `could`) |
| `"should"` | `must` + `should` only |
| `"must"` | `must` only |

**Default when omitted:** `"could"` (all items in scope). This preserves backward compatibility — existing projects without a threshold behave identically to the pre-priority schema.

**Inheritance:** When `priorityThreshold` is set on a ProjectCycle, it overrides the project-level threshold for that cycle. When absent on a cycle, the cycle inherits the project-level threshold.

**Precedence Rules:**

Three mechanisms interact to determine whether a checklist item is active in a given context:

1. **Explicit ChecklistState always wins.** If a ChecklistState entry exists for an item (in `current`, `target`, or a cycle), its `state` value takes precedence regardless of the threshold. This allows teams to explicitly include a low-priority item (`ChecklistState.state = "complete"` or `"not complete"`) or explicitly exclude a high-priority item (`ChecklistState.state = "not required"`).
2. **Threshold filters the remainder.** For items without an explicit ChecklistState entry, the threshold determines scope. If the item's priority is below the effective threshold, tooling treats it as implicitly not required.
3. **Default priority fills gaps.** Items with no explicit `priority` property default to `"must"` and are never filtered out by any threshold.

**Tooling Guidance:**

- When generating to-do lists or progress dashboards, apply the effective threshold to determine which checklist items to include.
- When a cycle overrides the project threshold, display the override clearly so team members understand which items are in scope for the current work period.
- Items filtered out by the threshold should remain visible in the practice definition (they are not deleted) — the threshold affects project-level tracking, not the practice itself.

**Example:**

```json
{
  "name": "Platform Modernisation",
  "practiceName": "Cloud Platform Engineering",
  "priorityThreshold": "should",
  "currentCycleName": "Sprint 3",
  "cycles": [
    {
      "name": "Sprint 3",
      "description": "Fast-track infrastructure provisioning",
      "priorityThreshold": "must",
      "startedAt": "2026-08-01T00:00:00Z",
      "alphaInstances": [
        {
          "name": "Core Platform",
          "alphaName": "Platform",
          "stateName": "Provisioned"
        }
      ]
    }
  ],
  "current": { "alphaInstances": [], "workProductInstances": [] },
  "target": { "alphaInstances": [], "workProductInstances": [] },
  "plan": { "pattern": { "name": "Modernisation Plan", "description": "Lifecycle plan" } }
}
```

In this example, the project-level threshold is `"should"` — across the project, `must` and `should` items are in scope while `could` items are implicitly excluded. Sprint 3 tightens this to `"must"` only, focusing the team on essential verification criteria during a time-pressured cycle.

### 12.6 Notes, External Links, and Automated Journaling

The Note type provides timestamped commentary throughout the Project structure:

- `name` — short summary or title
- `timestamp` — ISO timestamp string (consistent with `createdAt`/`updatedAt` elsewhere in the schema)
- `content` — the note text (keep brief — see guidance below)
- `links` — optional array of ExternalLink objects referencing external resources

**Brevity Intent:** Notes are intended to be kept brief — a concise summary capturing the key decision, observation, or outcome. Detailed supporting material (meeting transcripts, lengthy analysis, design documents) should not be inlined into the `content` field. Instead, use the `links` array to reference those longer documents by URI. This keeps the project document lightweight and navigable while preserving full traceability to source material.

**ExternalLink Structure:**

The ExternalLink type provides a reusable reference to an external document or resource. It is used throughout the schema wherever an array of described external references is needed — on Notes, instance declarations, instance tracking entries, and practice references.

- `name` — short label identifying the linked resource (e.g., "Sprint Backlog", "Architecture Decision Record", "Team Charter")
- `description` — optional explanation of what this resource contains or why it is linked
- `uri` — optional URI of the external resource, when available
- `pages` — optional page or location reference within the linked resource, following APA 7th edition format (e.g., `"p. 5"`, `"pp. 12-15"`, `"Chapter 3"`, `"Section 2.1"`, `"para. 4"`, `"Table 2"`). Use when the relevant content is at a specific location within a larger document.
- `kind` — optional classification of the linked resource type from a closed enum: `document`, `sheet`, `channel`, `crm`, `folder`. Tool-agnostic: describes what the resource IS, not which tool hosts it (e.g., a Google Sheet and an Excel file are both `sheet`). When absent, the link is unclassified.

**Example: Note with Links**

```json
{
  "name": "Architecture decision: event-driven messaging",
  "timestamp": "2026-07-25T14:30:00Z",
  "content": "Team agreed to adopt event-driven messaging for inter-service communication. Key driver was decoupling deployment cycles between platform and consumer teams.",
  "links": [
    {
      "name": "Architecture Review Meeting Transcript",
      "uri": "https://docs.example.com/meetings/2026-07-25-arch-review",
      "kind": "document"
    },
    {
      "name": "ADR-042: Event-Driven Messaging",
      "description": "Architecture decision record for the event-driven messaging approach",
      "uri": "https://wiki.example.com/adrs/042-event-driven-messaging",
      "kind": "document",
      "pages": "Section 3"
    }
  ]
}
```

Notes appear at multiple levels: at the project top level, within `plan`, `current`, `target`, `cycles`, `team`, and on individual ChecklistState entries. This multi-level placement enables commentary to be captured at the appropriate level of specificity — from project-wide decisions down to rationale for a single checklist item's state.

**ExternalLink Usage Across Types:**

ExternalLink is used on instance types at two levels, mirroring the declaration-vs-tracking split described in [Section 6.5](alphas.md#65-alpha-instance-semantics-guidance-vs-tracking) and [Section 7.3](work-products.md#73-work-product-instance-semantics-guidance-vs-evidence-chains):

- **AlphaInstanceName / WorkProductInstanceName** — links point to the primary document(s) used to track the instance (e.g., the board, register, or wiki page where ongoing work lives)
- **AlphaInstance / WorkProductInstance** — links point to documents specific to a particular state or level of detail; typically omitted when the parent declaration's links apply, and used only when a specific state is tracked in a different document
- **Note** — links point to supporting material such as meeting transcripts, design documents, or external reports

**Automated Journaling:** Systems implementing this schema may automatically record Notes based on user interactions and state changes (e.g. when a checklist item is marked complete, when an alpha instance transitions state, or when team membership changes). Automated notes should be clearly distinguishable from user-authored notes — tooling may use a naming convention or additional metadata to indicate provenance.

### 12.7 Cycles and Operational Work Tracking

The `cycles` section is where a project tracks its operational work — the concrete objectives and tasks being pursued within bounded periods. While `current` provides an assessed snapshot and `target` declares intent, cycles record *what work is being undertaken* to move from one toward the other.

**The Three Roles:**

- **`current`** is an assessed statement of the current status. Its checklist states declare what has been completed, what remains, and what will not be completed. It is a point-in-time snapshot.
- **`target`** is a statement of intent — the overall destination.
- **`cycles`** are the journey. Each cycle tracks the objectives and tasks the team is pursuing (or has pursued) during a bounded period.

**Cycle Model:**

A ProjectCycle extends ProjectStateSection with cycle-specific metadata (`name`, `description`, `startedAt`, `completedAt`, `patternViewName`). The term "cycle" avoids methodology-specific connotations (sprint, iteration, increment) while clearly conveying a repeatable work period. Teams name cycles according to their own cadence: "Sprint 1", "Q3 2026", "August", "Release 2.0", etc.

The optional `patternViewName` links a cycle to a phase in the project plan's Pattern. This establishes traceability between operational work periods and the overarching lifecycle plan — a team can see which plan phase each cycle contributes to, and multiple cycles may contribute to the same phase (e.g. several sprints within a "Build" phase).

A cycle progresses through three phases:

1. **Open** — `completedAt` is absent. The cycle is actively tracking work. `currentCycleName` points to this cycle. The cycle's alpha instances and work product instances represent the objectives being pursued right now.
2. **Closed** — `completedAt` is set. The cycle is complete. Its instances record what was worked on during that period. `currentCycleName` may now point to a new cycle.
3. **Historical** — closed cycles accumulate as a project history, enabling retrospective analysis and velocity tracking.

**What Goes in a Cycle:**

A cycle's `alphaInstances` and `workProductInstances` record the objectives being tracked during that period — the alpha states being pursued and the work product levels being developed. These are the items the team has committed to working on. As work progresses, `current` is updated to reflect the latest assessed state, while the cycle records what was undertaken.

An alpha instance may appear in multiple sections simultaneously:

- In `target` at state "Operational" (the goal)
- In `current` at state "Provisioned" (the latest assessed state)
- In the active cycle at state "Operational" (the objective being pursued this cycle)
- In a closed cycle at state "Architecture Selected" (an earlier objective that was completed)

**Active Cycle Management:**

`currentCycleName` identifies the active cycle. Tooling should:

- Create a new cycle entry in `cycles` when the user starts a new cycle
- Set `currentCycleName` to the new cycle's name
- Track objectives within the active cycle as the team works toward them
- Update `current` as assessments change
- Set `completedAt` on the cycle when the user closes it
- Optionally auto-generate a retrospective Note on the cycle at close

**Example:**

```json
{
  "currentCycleName": "Sprint 2",
  "cycles": [
    {
      "name": "Sprint 1",
      "description": "Foundation and architecture selection",
      "patternViewName": "Assess",
      "startedAt": "2026-07-01T00:00:00Z",
      "completedAt": "2026-07-14T00:00:00Z",
      "alphaInstances": [
        {
          "name": "Core Platform",
          "description": "Primary platform instance",
          "alphaName": "Platform",
          "stateName": "Architecture Selected"
        }
      ],
      "notes": [
        {
          "name": "Sprint 1 retrospective",
          "timestamp": "2026-07-14T15:00:00Z",
          "content": "Architecture decision took longer than expected due to multi-cloud evaluation. Security team input was critical."
        }
      ]
    },
    {
      "name": "Sprint 2",
      "description": "Provisioning and initial deployment",
      "patternViewName": "Build",
      "startedAt": "2026-07-15T00:00:00Z",
      "alphaInstances": [
        {
          "name": "Core Platform",
          "description": "Primary platform instance",
          "alphaName": "Platform",
          "stateName": "Provisioned"
        }
      ]
    }
  ]
}
```

In this example, Sprint 1 is closed (has `completedAt`) — its objective was "Architecture Selected" for the Core Platform, contributing to the "Assess" phase of the plan. Sprint 2 is the active cycle (matches `currentCycleName`, lacks `completedAt`) — the team is now pursuing "Provisioned" as part of the "Build" phase. The `patternViewName` on each cycle establishes which plan phase the work period contributes to. The `current` section (not shown) would reflect the latest assessed state of the Core Platform independent of these cycle-level objectives.

### 12.8 Outcome Instances and Value Tracking

Projects instantiate practice-defined Outcomes as OutcomeInstances — setting specific targets and tracking achievement against the measurement framework inherited from the practice template.

**Template → Instance Pattern**

The relationship mirrors Alpha → AlphaInstance and WorkProduct → WorkProductInstance:

- The **practice** defines an Outcome template with measurement framework (contributions, forecast weights) — see [Section 9.4](execution-and-patterns.md#94-outcome-definitions-and-value-measurement)
- The **project** creates an OutcomeInstance referencing that template via `outcomeName`, setting a concrete `measure` target and tracking `status`

The measurement rules (which alphas, metrics, states, views contribute and at what weights) are inherited from the referenced Outcome template. The project only specifies what the target is and whether it has been achieved.

**Structure**

An OutcomeInstance has:
- `name` — project-specific name (e.g., "FY26 Cisco EMEA Revenue")
- `outcomeName` — symbolic link to the practice-defined Outcome template
- `measure` — the specific target as free text (e.g., "1.5M GBP ACV", "75% lifecycle completion")
- `targetValue` — optional numeric target for comparison with the computed aggregate
- `actualValue` — optional current actual measured value, updated as real data is collected
- `forecastValue` — optional projected value based on current trajectory and contributing metrics
- `unit` — optional unit of `targetValue`, `actualValue`, and `forecastValue` (should match contributing metric units)
- `status` — current achievement: `not-started`, `in-progress`, `achieved`, `missed`, or `deferred`
- `evidence` — optional ExternalLink to supporting evidence
- `notes` — optional timestamped progress notes

The computed aggregate is **derived at read time** and is not stored on the OutcomeInstance. `actualValue` records confirmed measurements; `forecastValue` captures projections. `status` is author-set; tooling does not infer it from computed vs `targetValue`.

**Placement**

OutcomeInstances appear in two locations:

- **Project-level `outcomes`** — overall project value targets spanning the full project duration. Default: one instance per practice Outcome template (rename freely; do not create one instance per contributing alpha).
- **Cycle-level `outcomes`** — cycle-scoped targets that decompose project outcomes into period-specific goals (e.g., sprint revenue targets, quarterly milestones)

**Value Computation**

A consuming system resolves outcome values by following the practice template's contribution chain. Computed values are not persisted on the OutcomeInstance.

*For metric outcomes:*
1. Resolve `outcomeName` → Outcome template → `metricContributions`
2. For each MetricContribution, find **current** alpha instances (`current.alphaInstances` only — not `target` or cycles) whose `alphaName` matches, **or** whose alpha `mapsTo` that name. Do not include `contributesTo` children unless they also match.
3. For each matching alpha instance, look up the forecast weight for its `stateName`. States not listed in `forecastWeights` have weight 0. When `forecastWeights` is omitted and `recognizedAtStateName` is set, that state has weight 1.0 and all others 0.
4. Resolve evidencing work products: take `evidenceBy` entries, **join by instance `name`** to `current.workProductInstances` (canonical metric store — do not rely on metrics embedded in the `evidenceBy` snapshot). Also include **`partOf` children** of those roots (composition roots often sit on `evidenceBy` while the metric lives on a child). Dedupe by work-product instance name within that alpha instance.
5. If `workProductName` is set, keep only instances of that work product type.
6. Extract `metrics[]` entries whose `name` matches `metricName`. Skip an instance with no matching metric (do not treat missing as 0).
7. Multiply each metric `value` × the alpha instance's state weight.
8. **Sum** those weighted values. Repeat for each MetricContribution on the Outcome and sum the contribution totals.
9. All contributing metrics must share a single `unit`. Mixed units: do not report a number; surface a warning.

*For objective outcomes:*
1. Resolve `outcomeName` → Outcome template → `objectiveContributions`
2. For each ObjectiveContribution, resolve `patternName` to the named pattern and determine the highest **completed** pattern view within it (all alpha-state and work-product objectives for that view are met on `current`)
3. Apply that view's forecast weight as the percentage progress (0–1). Views not listed have implicit weight 0.

**Example**

```json
{
  "kind": "project",
  "name": "Cisco EMEA TEP FY26",
  "outcomes": [
    {
      "name": "FY26 Cisco Revenue",
      "outcomeName": "Account Revenue",
      "measure": "1.5M GBP ACV",
      "status": "in-progress",
      "evidence": {
        "name": "Salesforce Dashboard",
        "uri": "https://crm.example.com/dashboards/cisco-fy26"
      }
    },
    {
      "name": "FY26 Engagement Maturity",
      "outcomeName": "Account Readiness",
      "measure": "75% lifecycle completion by EOY",
      "status": "in-progress"
    }
  ]
}
```

**Validation Rules**

- `OutcomeInstance.outcomeName` must match an Outcome.name in the resolved practice or method
- Each OutcomeInstance must have a unique `name` within its containing array

### 12.9 Actions and Team Work Tracking

Actions are the concrete tasks that team members perform to advance project objectives. While cycle objectives (alpha instances, work product instances) answer *what we're trying to achieve*, and outcomes answer *what value we expect to deliver*, actions answer *what each person is doing* to get there. Actions can appear in two locations: on a **ProjectCycle** (committed work within a bounded period) or on the **Project** itself (the backlog of candidate actions awaiting cycle assignment).

**Relationship to Activity (Practice-Level)**

An Action is NOT an ActivityInstance. The schema deliberately avoids the template-instance pattern used for Alphas and WorkProducts:

- An **Activity** is a practice-level methodology construct — a swimlane defining a type of work with structural contributions (`contributesTo`, `worksOn`), competency requirements, and persona involvement. Activities exist in the methodology definition and do not change per project.
- An **Action** is a project-level operational task — specific ("Deploy staging environment"), assigned to individuals ("Alice Chen"), time-bound ("due 2026-08-08"), and tracked through a status lifecycle. Actions exist in project cycles (committed work) or in the project-level backlog (candidate work).

The optional `activityName` property on Action provides methodology traceability — linking a concrete task back to the practice-defined activity it falls under — without coupling the two. Many actions will have no `activityName` at all, particularly ad-hoc tasks that arise during execution.

**Symbolic Link Resolution**

- `activityName` → Activity.name in the resolved practice or method scope
- `assignedTo[]` → TeamMember.name in the project's `team.members` array
- `advancesAlphaInstances[]` → AlphaInstance.name declared in the plan's `alphaInstanceNames` array
- `developsWorkProductInstances[]` → WorkProductInstance.name declared in the plan's `workProductInstanceNames` array
- `outcomeInstanceNames[]` → OutcomeInstance.name at either the project level or the same cycle level

**Status Lifecycle**

| Status | Meaning |
|---|---|
| `not-started` | Action created but work has not begun |
| `in-progress` | Work is actively being done |
| `done` | Work is complete; `completedAt` should be set |
| `blocked` | Work cannot proceed due to an impediment; use `notes` to capture the blocker |
| `deferred` | Work has been postponed; may be moved to a future cycle |
| `discarded` | Team reviewed this candidate and decided not to pursue it; preserved for auditability |

**Timestamps**

`dueAt` and `completedAt` follow the same ISO timestamp convention as cycle `startedAt`/`completedAt`. `dueAt` records the target completion date; `completedAt` records when the action was actually completed. Both are optional — lightweight tracking may omit dates entirely.

**Uniqueness**

Action `name` must be unique within its containing array — the parent cycle's `actions` or the project-level `actions` (backlog). The same action name may appear in different cycles (e.g., a recurring action across sprints) and may appear in both the backlog and a cycle (e.g., a backlog item that has been copied to a cycle for execution).

**Traceability Chain**

Actions connect team members to objectives and outcomes through multiple paths:

1. **Action → Objective**: `advancesAlphaInstances` and `developsWorkProductInstances` link directly to the cycle's alpha and work product objectives
2. **Action → Outcome**: `outcomeInstanceNames` links directly to outcome instances for actions that contribute to value measurement (e.g., updating CRM metrics)
3. **Action → Methodology**: `activityName` traces back to the practice-defined Activity, inheriting its contribution context (`contributesTo`, `worksOn`)
4. **Action → People**: `assignedTo` identifies the team members responsible
5. **Action → Verification**: `test` defines a structured acceptance criterion (Given/When/Then); `evidence` points to the deliverable. Together they answer *what does done look like?* and *where is the proof?*

**Example**

```json
{
  "name": "Sprint 3",
  "description": "Platform provisioning and initial deployment",
  "patternViewName": "Build",
  "startedAt": "2026-08-01T00:00:00Z",
  "alphaInstances": [
    {
      "name": "Core Platform",
      "alphaName": "Platform",
      "stateName": "Provisioned"
    }
  ],
  "workProductInstances": [
    {
      "name": "Infra Runbook",
      "workProductName": "Runbook",
      "levelOfDetailName": "Drafted"
    }
  ],
  "actions": [
    {
      "name": "Deploy staging environment",
      "description": "Provision staging cluster and configure CI/CD pipeline",
      "activityName": "Provision Infrastructure",
      "assignedTo": ["Alice Chen"],
      "status": "in-progress",
      "dueAt": "2026-08-08T00:00:00Z",
      "advancesAlphaInstances": ["Core Platform"],
      "developsWorkProductInstances": ["Infra Runbook"],
      "test": {
        "name": "Staging accepts deploys",
        "description": "Verify the staging cluster is operational and CI/CD pipeline delivers builds",
        "given": ["A staging cluster has been provisioned", "CI/CD pipeline is configured"],
        "when": ["A build is triggered from the main branch"],
        "then": ["The build deploys to staging within 10 minutes", "Health check endpoint returns 200"]
      }
    },
    {
      "name": "Review security compliance checklist",
      "assignedTo": ["Bob Smith"],
      "status": "not-started",
      "dueAt": "2026-08-10T00:00:00Z",
      "advancesAlphaInstances": ["Core Platform"]
    },
    {
      "name": "Update CRM with Q3 pipeline figures",
      "assignedTo": ["Carol Davis"],
      "status": "done",
      "completedAt": "2026-08-05T00:00:00Z",
      "outcomeInstanceNames": ["Q3 Revenue Target"]
    }
  ]
}
```

In this example, Sprint 3 has three actions: Alice is provisioning the staging environment (advancing the Core Platform objective and developing the Infra Runbook), Bob will review the security checklist (also advancing Core Platform), and Carol has already updated the CRM figures (contributing directly to the Q3 Revenue Target outcome).

**Tooling Guidance**

- When displaying a cycle, group actions by `assignedTo` to show each team member's workload
- When closing a cycle, tooling may flag actions still in `not-started` or `in-progress` status for carry-over to the next cycle or return to the project backlog
- Actions with status `blocked` should be surfaced prominently — they represent impediments to cycle objectives
- When displaying the project backlog, surface `discarded` actions separately (or filtered) so the active candidate list remains clean while preserving the audit trail
- When an action references both `advancesAlphaInstances` and `activityName`, tooling can validate consistency between the action's stated objectives and the Activity's structural `contributesTo` declarations

**Validation Rules**

- Each Action must have a unique `name` within its containing array (cycle-level or project-level)
- `assignedTo` entries must match a TeamMember.name in the project's team
- `advancesAlphaInstances` entries must match an AlphaInstanceName.name declared in the plan pattern
- `developsWorkProductInstances` entries must match a WorkProductInstanceName.name declared in the plan pattern
- `outcomeInstanceNames` entries must match an OutcomeInstance.name at the project or cycle level
- `activityName` must match an Activity.name in the resolved practice or method scope (requires resolved scope; same limitation as TeamMember.personaName validation)

### 12.9.1 Project-Level Action Backlog

The `actions` array on Project provides a staging area for candidate actions that have not yet been assigned to a cycle. This is the project backlog — where action ideas are captured and reviewed before the team commits them to a bounded period of work.

**Workflow**

1. **Capture**: Action ideas are created in `project.actions` with minimal detail — typically just `name` and `description`. Properties like `assignedTo`, `dueAt`, and `status` are optional at this stage.
2. **Review**: During cycle planning, the team reviews the backlog and decides which actions to include in the upcoming cycle.
3. **Promote**: Accepted actions are copied to the cycle's `actions` array, where they gain cycle-specific detail (assignment, due dates, objective links).
4. **Discard**: Rejected candidates are marked with `status: "discarded"` and optionally annotated with `notes` explaining the rationale. This preserves an audit trail of what was considered.

**Relationship to Cycle Actions**

Project-level and cycle-level actions use the same `Action` type. The difference is lifecycle stage, not structure. A backlog action is a candidate; a cycle action is committed work. The same action name may appear in both locations — the backlog retains the original while the cycle holds the working copy.

**Scope of Symbolic Links**

When validating project-level actions, `outcomeInstanceNames` resolves against project-level outcome instances only (not cycle-level outcomes, since the action is not yet in a cycle). All other symbolic links (`assignedTo`, `advancesAlphaInstances`, `developsWorkProductInstances`, `activityName`) resolve against the same scopes as cycle-level actions.

**Example**

```json
{
  "kind": "project",
  "name": "Platform Modernisation",
  "practiceName": "Cloud Migration",
  "actions": [
    {
      "name": "Evaluate service mesh options",
      "description": "Compare Istio, Linkerd, and Consul Connect for the platform's service mesh layer",
      "status": "not-started"
    },
    {
      "name": "Draft data residency policy",
      "description": "Document data residency requirements for EU customer data",
      "status": "discarded",
      "notes": [
        {
          "content": "Legal confirmed existing policy covers this — no new document needed.",
          "createdAt": "2026-08-12T10:00:00Z"
        }
      ]
    }
  ],
  "cycles": [ "..." ]
}
```

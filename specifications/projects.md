# The Project Type

## Objective

The Project type provides a mechanism for users to track the current state and desired state of their endeavours, based on a given Practice or Method. It bridges the gap between practice definition (what should be done) and practice execution (what is being done), enabling concrete progress tracking against methodology-defined milestones.

## Relationship to Existing Schema

A Project is a type of PracticeElement, inheriting `name`, `description`, and optional `tags`, `keywords`, `narratives`, and `assetNames`. Since narratives include `citationNames`, a Project may also include `citations` and `acknowledgements`.

A Project is distinct from Practice, Method, and PracticeBaseline — it is not a methodology definition but an execution instance of one. It must be discriminated at the root level alongside the existing types.

A Project includes a top-level `notes` array (of Note objects) for project-wide observations, decisions, and commentary that are not specific to the plan, current state, target state, or team.

## Practice/Method Reference

A Project MUST name exactly one Practice or Method on which it is based, using an exclusive-or reference:

- `practiceName` — symbolic link to a Practice (by name)
- `methodName` — symbolic link to a Method (by name)

Exactly one of these must be present (xor constraint, mirroring the Method's `baselinePractice` xor `baselinePracticeName` pattern).

Any system managing the Project would need to resolve all of the referenced Practice or Method's dependencies (including baseline and dependent practices) so the user operates against a single merged virtual practice. The resolution mechanism is outside the scope of this schema — it is a tooling concern.

## Team

Inspired by the Team API concept from Team Topologies (Skelton & Pais), the `team` property makes it clear who is involved in the project, what they do, and how to reach them. The Team API's core objective is to reduce cognitive load by making a team's purpose, membership, and communication preferences discoverable. This section distils that objective into the minimum structure needed for project tracking.

The `team` property is a single TeamEntry object describing the project team.

### TeamEntry

The TeamEntry describes the team working on the project.

**Structure:**

- `name` — the team's name (e.g. "Platform Engineering", "Security Governance")
- `description` — a brief statement of the team's focus and purpose within this project, answering "what does this team do and why does it exist?"
- `communicationChannels` — optional array of CommunicationChannel objects describing how to interact with this team (see below)
- `members` — array of TeamMember objects (see below)
- `notes` — optional array of Note objects for team-level observations, decisions, and changes over time

### TeamMember

Each TeamMember identifies a person, their role within the methodology, and how to contact them.

**Structure:**

- `name` — the individual's name
- `personaName` — symbolic link to a Persona defined in the resolved practice/method scope, identifying their role
- `contact` — a contact address (e.g. email, chat handle, phone). Format is not constrained — the value is whatever the team considers the best way to reach this person
- `started` — optional ISO timestamp string recording when this member joined the project
- `finished` — optional ISO timestamp string recording when this member left the project

This connects real people to the methodology's Persona definitions, enabling role-based views of project progress while keeping contact details immediately accessible. The optional `started`/`finished` timestamps support temporal membership tracking without overcomplicating the structure.

### CommunicationChannel

CommunicationChannel captures the team's preferred interaction points — the places other people should go to find or reach the team.

**Structure:**

- `name` — a human-readable label for the channel (e.g. "Slack", "Team Email", "Weekly Sync", "Backlog")
- `address` — the channel's address or location (e.g. `"#platform-eng"`, `"platform@example.com"`, `"Tuesdays 10:00 UTC"`, `"https://jira.example.com/board/PLAT"`)

## Main Content Sections

The Project's content is divided into three sections: `plan`, `current`, and `target`.

### Plan

The `plan` section establishes a high-level plan for the project. It contains an embedded Pattern (a new instance, not a symbolic link) and a notes array for plan-level commentary.

The Pattern type is extended with optional `alphaInstanceNames` and `workProductInstanceNames` arrays (see Schema Changes below), allowing the Pattern to explicitly declare which alpha instances and work product instances are being tracked. The Pattern's PatternViews provide the phased objectives, with each view's AlphaInstances identifying the desired state of tracked alpha instances per phase, and WorkProductInstances (if present) identifying the desired level of detail for work products per phase.

**Structure:**

- `pattern` — an embedded Pattern object defining the project's lifecycle plan. This is a new instance using the existing Pattern type, owned by the project. As a full declaration rather than a reference, the user is free to add, remove, or reorder PatternViews, adjust alpha state targets, and extend the pattern with objectives or requirements specific to their project. The Pattern's `alphaInstanceNames` and `workProductInstanceNames` arrays declare the instances being tracked.
- `notes` — optional array of Note objects for plan-level commentary, decisions, and rationale. These capture changes, updates, and context that are about the planning process itself rather than the plan content (which lives in the Pattern).

**Tooling guidance:** Systems supporting this schema should allow the user to clone an existing Pattern from the resolved practice/method scope as a starting point for their plan. The cloned Pattern becomes an independent copy owned by the project. Such a system would need to ensure all tracked items are represented as AlphaInstanceName or WorkProductInstanceName declarations within the Pattern, and may default instance names to names derived from the alpha/work product name when the user has not explicitly named them.

### Current

The `current` section tracks the currently assessed state of the project's alphas and work products. It contains:

- `alphaInstances` — array of AlphaInstance objects recording the current state of each tracked alpha instance (referencing `alphaName` and `stateName`). Each AlphaInstance carries its own optional `checklistStates` array recording the completion status of individual checklist items for that instance.
- `workProductInstances` — array of WorkProductInstance objects recording the current level of detail of each tracked work product instance (referencing `workProductName` and `levelOfDetailName`). Each WorkProductInstance carries its own optional `checklistStates` array.
- `notes` — optional array of Note objects providing timestamped observations and commentary

### Target

The `target` section mirrors the structure of the `current` section but records the desired/goal state that the project is working towards. It contains the same properties:

- `alphaInstances` — array of AlphaInstance objects recording the target state for each tracked alpha instance. ChecklistState entries here use `"not required"` to mark checklist items excluded from this project's goals.
- `workProductInstances` — array of WorkProductInstance objects recording the target level of detail for each tracked work product instance
- `notes` — optional array of Note objects

The target section allows users to define objectives that may differ from the full pattern — for example, a project may target a subset of alpha states or require only certain checklist items to be completed.

## Schema Changes to Existing Types

### Pattern (extended)

The existing Pattern type is extended with two optional arrays:

- `alphaInstanceNames` — optional array of AlphaInstanceName objects, explicitly declaring which alpha instances are tracked by this pattern
- `workProductInstanceNames` — optional array of WorkProductInstanceName objects, explicitly declaring which work product instances are tracked by this pattern

These additions are optional and do not affect existing Pattern usage in practices or methods. In the project context, they provide the declaration vocabulary for the instances that the Pattern's views reference when specifying phased objectives.

### AlphaInstance and WorkProductInstance (extended)

Both AlphaInstance and WorkProductInstance are extended with an optional `checklistStates` array:

- `checklistStates` — optional array of ChecklistState objects tracking the completion status of individual checklist items for this instance

This co-locates checklist tracking with the instance it belongs to. These additions are optional and do not affect existing usage.

## New Supporting Types

### ChecklistState

ChecklistState tracks the completion status of an individual checklist item within the project context. It provides a bridge between the practice-defined checklists (on Alpha States and WorkProduct LevelsOfDetail) and real-world execution. ChecklistState objects live on AlphaInstance and WorkProductInstance via their `checklistStates` arrays.

**Structure:**

- `checklistName` — the name of the specific Checklist item (must match a `Checklist.name` within the parent instance's referenced State or LevelOfDetail)
- `state` — enum: `"complete"`, `"not complete"`, `"not required"`
- `evidence` — optional ExternalLink referencing external evidence supporting the checklist item's state (e.g. a document, test result, approval record, or audit artifact)
- `notes` — optional array of Note objects for recording observations or rationale for the checklist item's state

Because ChecklistState is co-located on an AlphaInstance or WorkProductInstance, the parent context (alphaName + stateName, or workProductName + levelOfDetailName) already identifies which Alpha/State or WorkProduct/LevelOfDetail the checklist belongs to. There is no need for separate `alphaName`/`workProductName`/`levelName` fields on ChecklistState itself.

**Dual-use semantics:**

- In the `current` section: `state` records actual completion — `"complete"` or `"not complete"`
- In the `target` section: `state` indicates requirement — `"not required"` marks checklist items explicitly excluded from this project's goals, while `"complete"` marks items that must be achieved

### Note

Note provides timestamped commentary for project tracking.

**Structure:**

- `name` — short summary or title of the note
- `timestamp` — ISO timestamp string (consistent with `createdAt`/`updatedAt` elsewhere in the schema)
- `content` — the note text

Notes appear at multiple levels throughout the Project — at the top level, within `plan`, `current`, `target`, `team`, and on individual ChecklistState entries — providing a journal of observations, decisions, and rationale as the project progresses.

**Tooling guidance:** Systems implementing this schema may automatically record Notes based on user interactions and state changes (e.g. when a checklist item is marked complete, when an alpha instance transitions state, or when team membership changes). Automated notes should be clearly distinguishable from user-authored notes — tooling may use a naming convention or additional metadata to indicate provenance.

## Root Discrimination

The existing schema uses `if/then/else` blocks to discriminate between Method, Practice, and PracticeBaseline at the root level. A Project must be added to this discrimination chain. A Project is identified by the presence of `practiceName` or `methodName` (properties unique to this type), and the discrimination should be evaluated before the existing Practice/Method checks to avoid ambiguity.

## Metadata

A Project should include the same provenance metadata as Practice and PracticeBaseline:

- `authors` — array of strings
- `createdAt` — ISO timestamp string
- `updatedAt` — ISO timestamp string
- `version` — version string

## Validation Rules

1. Exactly one of `practiceName` or `methodName` must be present (xor)
2. The embedded `pattern` in `plan` must be a valid Pattern object conforming to the existing Pattern schema definition
3. All `alphaInstanceNames` in the plan's Pattern must reference valid alphas from the resolved practice/method scope
4. All `workProductInstanceNames` in the plan's Pattern must reference valid work products from the resolved practice/method scope
5. AlphaContributions within the plan's Pattern must reference valid alphas and states from the resolved practice/method scope
6. All AlphaInstance entries in `current` and `target` must reference alpha instance names declared in the plan's Pattern
7. All WorkProductInstance entries in `current` and `target` must reference work product instance names declared in the plan's Pattern
8. All ChecklistState entries on AlphaInstance objects must reference valid checklist items within the parent instance's referenced Alpha State
9. All ChecklistState entries on WorkProductInstance objects must reference valid checklist items within the parent instance's referenced WorkProduct LevelOfDetail
10. Team `personaName` entries in TeamMember objects must reference Personas defined in the resolved practice/method scope

## Open Questions

None currently outstanding.

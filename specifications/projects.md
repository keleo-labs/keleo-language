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

### Cycles

The `cycles` section tracks the objectives and tasks for the project, organised into bounded periods of work. It is an optional array of ProjectCycle objects, allowing progressive adoption — projects can begin without cycles and add them as work tracking is introduced.

- `cycles` — optional array of ProjectCycle objects. Each cycle tracks the objectives and tasks undertaken during a bounded period.
- `currentCycleName` — optional string at the Project level identifying the active cycle by name. When present, must match the `name` of an entry in the `cycles` array.

#### ProjectCycle

A ProjectCycle extends ProjectStateSection (inheriting `alphaInstances`, `workProductInstances`, and `notes`) with cycle-specific metadata. The term "cycle" is methodology-agnostic — teams may name cycles after sprints, iterations, months, quarters, or any other cadence that fits their way of working.

**Inherited from ProjectStateSection:**

- `alphaInstances` (optional) — array of AlphaInstance objects tracking the alpha states being pursued or achieved during this cycle
- `workProductInstances` (optional) — array of WorkProductInstance objects tracking the work product levels being pursued or achieved during this cycle
- `notes` (optional) — array of Note objects for cycle-level observations, decisions, and retrospective commentary

**Own properties:**

- `name` (required) — identifies the cycle (e.g. "Sprint 1", "Q3 2026", "August")
- `description` (optional) — what this cycle covers or aims to achieve
- `startedAt` (optional) — ISO timestamp recording when the cycle began
- `completedAt` (optional) — ISO timestamp recording when the cycle ended. Absent while the cycle is still active

#### Relationship Between Sections

The `current`, `target`, and `cycles` sections serve complementary purposes:

- **current** provides an assessed statement of the current status — where things are now. Its checklist states declare what has been completed, what remains, and what will not be completed.
- **target** provides a statement of intent — the alpha states and work product levels the project aims to achieve overall.
- **cycles** track the operational work — the concrete objectives and tasks being pursued within each bounded period. The active cycle records what the team is working on now; closed cycles record what was worked on previously.

`current` is a point-in-time snapshot. `target` is a destination. Cycles are the journey — they record *what work was undertaken* to move from current toward target.

#### Cycle Lifecycle

A cycle progresses through three phases:

1. **Open** — `completedAt` is absent. The cycle is actively tracking work. `currentCycleName` points to this cycle.
2. **Closed** — `completedAt` is set. The cycle is complete. `currentCycleName` may now point to a new cycle.
3. **Historical** — closed cycles accumulate as a project history, enabling retrospective analysis and velocity tracking.

**Tooling guidance:** Systems supporting this schema should allow users to create new cycles, close active cycles, and manage objectives within cycles. When a cycle is closed, tooling may automatically generate a retrospective Note on the cycle summarising what was accomplished.

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

### Feature: Practice or Method reference (rules 1)

```gherkin
Scenario: Valid project with practice reference
  Given a Project with "practiceName" set to "Cloud Platform Adoption"
  And "methodName" is absent
  When the project is validated
  Then validation succeeds

Scenario: Valid project with method reference
  Given a Project with "methodName" set to "Platform Engineering Method"
  And "practiceName" is absent
  When the project is validated
  Then validation succeeds

Scenario: Both practice and method reference present
  Given a Project with "practiceName" set to "Cloud Platform Adoption"
  And "methodName" set to "Platform Engineering Method"
  When the project is validated
  Then a validation error is reported: exactly one of practiceName or methodName must be present

Scenario: Neither practice nor method reference present
  Given a Project with neither "practiceName" nor "methodName"
  When the project is validated
  Then a validation error is reported: exactly one of practiceName or methodName must be present
```

### Feature: Plan validation (rules 2–5)

```gherkin
Scenario: Embedded pattern is a valid Pattern object
  Given a Project with a "plan" section containing a "pattern" object
  When the project is validated
  Then the pattern must conform to the Pattern schema definition

Scenario: Alpha instance names reference valid alphas
  Given a plan Pattern declaring alphaInstanceNames including "My Platform Instance"
  And the resolved practice scope contains an alpha named "Platform"
  And "My Platform Instance" references alphaName "Platform"
  When the project is validated
  Then validation succeeds for that alpha instance name

Scenario: Alpha instance names reference non-existent alpha
  Given a plan Pattern declaring alphaInstanceNames including "Ghost Instance"
  And "Ghost Instance" references alphaName "Non-Existent Alpha"
  And no alpha named "Non-Existent Alpha" exists in the resolved scope
  When the project is validated
  Then a validation error is reported: alphaInstanceName references unknown alpha "Non-Existent Alpha"

Scenario: Work product instance names reference valid work products
  Given a plan Pattern declaring workProductInstanceNames including "My Architecture Doc"
  And the resolved practice scope contains a work product named "Architecture"
  And "My Architecture Doc" references workProductName "Architecture"
  When the project is validated
  Then validation succeeds for that work product instance name

Scenario: AlphaContributions reference valid alphas and states
  Given a plan Pattern with a PatternView containing alphaStates
  And an AlphaContribution referencing alphaName "Platform" and stateName "Provisioned"
  And alpha "Platform" exists with state "Provisioned" in the resolved scope
  When the project is validated
  Then validation succeeds for that alpha contribution

Scenario: AlphaContributions reference non-existent state
  Given a plan Pattern with a PatternView containing alphaStates
  And an AlphaContribution referencing alphaName "Platform" and stateName "Imaginary State"
  And alpha "Platform" exists but has no state "Imaginary State"
  When the project is validated
  Then a validation error is reported: AlphaContribution references unknown state "Imaginary State" on alpha "Platform"
```

### Feature: Current and target state validation (rules 6–9)

```gherkin
Scenario: AlphaInstance in current references declared instance name
  Given a plan Pattern declaring alphaInstanceNames including "My Platform"
  And the "current" section contains an AlphaInstance with instanceName "My Platform"
  When the project is validated
  Then validation succeeds for that alpha instance

Scenario: AlphaInstance in current references undeclared instance name
  Given a plan Pattern with no alphaInstanceName "Undeclared Instance"
  And the "current" section contains an AlphaInstance with instanceName "Undeclared Instance"
  When the project is validated
  Then a validation error is reported: AlphaInstance references undeclared instance name "Undeclared Instance"

Scenario: WorkProductInstance in target references declared instance name
  Given a plan Pattern declaring workProductInstanceNames including "My Architecture"
  And the "target" section contains a WorkProductInstance with instanceName "My Architecture"
  When the project is validated
  Then validation succeeds for that work product instance

Scenario: ChecklistState on AlphaInstance references valid checklist item
  Given an AlphaInstance in "current" referencing alpha "Platform" at state "Provisioned"
  And state "Provisioned" defines a checklist item named "Infrastructure deployed"
  And a ChecklistState entry with checklistName "Infrastructure deployed"
  When the project is validated
  Then validation succeeds for that checklist state

Scenario: ChecklistState on AlphaInstance references non-existent checklist item
  Given an AlphaInstance in "current" referencing alpha "Platform" at state "Provisioned"
  And state "Provisioned" has no checklist item named "Nonexistent Check"
  And a ChecklistState entry with checklistName "Nonexistent Check"
  When the project is validated
  Then a validation error is reported: ChecklistState references unknown checklist item "Nonexistent Check" on state "Provisioned"

Scenario: ChecklistState on WorkProductInstance references valid checklist item
  Given a WorkProductInstance in "target" referencing work product "Architecture" at LOD "Detailed"
  And LOD "Detailed" defines a checklist item named "Integration patterns specified"
  And a ChecklistState entry with checklistName "Integration patterns specified"
  When the project is validated
  Then validation succeeds for that checklist state
```

### Feature: Team validation (rule 10)

```gherkin
Scenario: TeamMember personaName references defined persona
  Given the resolved practice scope defines a Persona named "Platform Engineer"
  And a TeamMember with personaName "Platform Engineer"
  When the project is validated
  Then validation succeeds for that team member

Scenario: TeamMember personaName references undefined persona
  Given the resolved practice scope does not define a Persona named "Unknown Role"
  And a TeamMember with personaName "Unknown Role"
  When the project is validated
  Then a validation error is reported: personaName "Unknown Role" does not match any Persona in scope
```

### Feature: Cycle validation (rules 11–14)

```gherkin
Scenario: Unique cycle names
  Given a Project with cycles named "Sprint 1", "Sprint 2", "Sprint 3"
  When the project is validated
  Then validation succeeds for cycle name uniqueness

Scenario: Duplicate cycle names
  Given a Project with two cycles both named "Sprint 1"
  When the project is validated
  Then a validation error is reported: duplicate cycle name "Sprint 1"

Scenario: currentCycleName matches an existing cycle
  Given a Project with cycles named "Sprint 1", "Sprint 2"
  And currentCycleName set to "Sprint 2"
  When the project is validated
  Then validation succeeds for currentCycleName

Scenario: currentCycleName does not match any cycle
  Given a Project with cycles named "Sprint 1", "Sprint 2"
  And currentCycleName set to "Sprint 3"
  When the project is validated
  Then a validation error is reported: currentCycleName "Sprint 3" does not match any cycle name

Scenario: Cycle AlphaInstance references declared instance name
  Given a plan Pattern declaring alphaInstanceNames including "My Platform"
  And a cycle containing an AlphaInstance with instanceName "My Platform"
  When the project is validated
  Then validation succeeds for that cycle alpha instance

Scenario: Cycle AlphaInstance references undeclared instance name
  Given a plan Pattern with no alphaInstanceName "Undeclared"
  And a cycle containing an AlphaInstance with instanceName "Undeclared"
  When the project is validated
  Then a validation error is reported: cycle AlphaInstance references undeclared instance name "Undeclared"

Scenario: Cycle WorkProductInstance references declared instance name
  Given a plan Pattern declaring workProductInstanceNames including "My Docs"
  And a cycle containing a WorkProductInstance with instanceName "My Docs"
  When the project is validated
  Then validation succeeds for that cycle work product instance
```

## Open Questions

None currently outstanding.

## Coverage Status

- **Schema:** Complete — Project, ProjectCycle, ProjectStateSection, TeamEntry, TeamMember, CommunicationChannel, ChecklistState, Note defined in `language.schema.json`
- **Semantics:** Covered in [`references/semantics.md` Section 12](../references/semantics.md#12-project-execution-tracking)
- **Validation:** Not yet implemented — planned as `validate/validate-project.py`

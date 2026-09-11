[< Back to Semantic Guidance Hub](../semantics.md)

## 5 PracticeElement Foundations

Foundation elements provide the baseline from which all other methodology constructs inherit. They establish the universal properties required for identification, metadata classification, and sequential verification.

### 5.1 PracticeElement, Tagging Taxonomy, and Narrative Anchors

The PracticeElement serves as the foundational root object, guaranteeing any instantiated element contains a unique name and a human-readable description. Crucially, it also introduces the narratives array as a universal property. By embedding narrative support at the root object level, the schema ensures that any methodology construct—from a micro-level Work Product to a macro-level Pattern—can be enriched with structured storytelling frameworks. To prevent semantic fragmentation, the schema implements an advanced tagging taxonomy utilizing the structured tags object, enforcing orthogonal data classification.

PracticeElement also carries an optional `contributingPatternName` string for merge-time provenance. This property records which Pattern introduced or enriched the element during practice composition. It is populated automatically by the merge algorithm and must not be set in source practice authoring. While `sourcePracticeName` (set during merge on specific element types) identifies the practice that introduced an element, `contributingPatternName` provides finer-grained attribution to the specific pattern within that practice. Elements introduced outside any pattern context leave this property absent. See [merge.md Section 8.2](../merge.md#82-pattern-level-provenance-contributingpatternname) for the full provenance rules.

#### 5.1.1 Orthogonal Tagging Taxonomy

The Practice Language uses a structured, multi-dimensional tagging system rather than a flat array of tags. This orthogonal design enables filtering and classification along independent dimensions, supporting advanced search, filtering, and knowledge graph integration.

**Tags Object Structure (NOT Flat Array):**

```json
{
  "tags": {
    "domainTags": ["string", "string", ...],
    "lifecycleTags": ["string", "string", ...],
    "organizationalTags": ["string", "string", ...]
  }
}
```

**CRITICAL**: Tags MUST use the structured object format with three orthogonal arrays. Flat tag arrays (e.g., `"tags": ["tag1", "tag2"]`) are invalid and will fail schema validation.

**Three Independent Classification Dimensions:**

1. **domainTags**: Denotes the specific technical discipline or subject matter domain governing the element
  - Examples: "Architecture", "Security", "FinOps", "DevOps", "Data Management", "Compliance"
  - Purpose: Enables filtering by technical expertise area
  - Use when: Element requires specific domain knowledge or belongs to a technical discipline
2. **lifecycleTags**: Maps the element to broader temporal frameworks or methodology phases
  - Examples: "Adoption", "Migration", "Optimization", "Decommissioning", "Assessment"
  - Purpose: Enables filtering by where element fits in organizational journey
  - Use when: Element is primarily relevant during specific lifecycle stages
3. **organizationalTags**: Indicates the business unit, team, or organizational context
  - Examples: "Platform Team", "Security", "Finance", "Product Engineering", "Operations"
  - Purpose: Enables filtering by organizational ownership or relevance
  - Use when: Element is owned by or primarily relevant to specific organizational units

**Orthogonality Principle:**

The three dimensions are independent—an element can have:

- Tags in all three dimensions (e.g., domain="Security", lifecycle="Adoption", org="Platform Team")
- Tags in only one or two dimensions (arrays for unused dimensions can be empty)
- Multiple tags within any dimension (e.g., both "Architecture" and "Security" domain tags)
- Zero tags total (all three arrays empty) if classification is not applicable

This independence enables rich, multi-faceted classification without forcing artificial hierarchies.

**Usage Across Element Types:**

- **Practice-level tags**: Classify the entire practice by domain, lifecycle, and organizational context
- **Alpha-level tags**: Identify which domains, lifecycle phases, and organizations are concerned with this alpha
- **Activity-level tags**: Categorize work by domain expertise required, lifecycle relevance, and organizational ownership
- **Work Product-level tags**: Classify deliverables by technical domain, lifecycle stage, and owning team
- **Persona-level tags**: Tag roles by domain expertise, lifecycle responsibilities, and organizational placement

**Example: Practice-Level Tags**

```json
{
  "name": "Cloud Platform Adoption",
  "tags": {
    "domainTags": ["Architecture", "DevOps", "Security"],
    "lifecycleTags": ["Adoption", "Migration"],
    "organizationalTags": ["Platform Team", "Cloud Center of Excellence"]
  }
}
```

**Example: Alpha-Level Tags**

```json
{
  "name": "Platform",
  "tags": {
    "domainTags": ["Architecture", "Infrastructure"],
    "lifecycleTags": ["Adoption", "Optimization", "Evolution"],
    "organizationalTags": ["Platform Team"]
  }
}
```

**Example: Activity-Level Tags**

```json
{
  "name": "Design Security Architecture",
  "tags": {
    "domainTags": ["Security", "Architecture"],
    "lifecycleTags": ["Adoption"],
    "organizationalTags": ["Security", "Platform Team"]
  }
}
```

**Anti-Pattern: Flat Tags Array (INVALID)**

```json
{
  "tags": ["Architecture", "Security", "Adoption", "Platform Team"]
}
```

**Problem**: Flat arrays lose dimensional semantics. "Architecture" and "Platform Team" are conflated despite being completely different classification dimensions (domain vs organization). Filtering becomes ambiguous and knowledge graph integration fails.

**How Tags Enable Filtering and Search:**

- **Domain Filtering**: "Show me all alphas related to Security" → filter by domainTags contains "Security"
- **Lifecycle Filtering**: "What work products are relevant during Migration?" → filter by lifecycleTags contains "Migration"
- **Organizational Filtering**: "What activities does Platform Team perform?" → filter by organizationalTags contains "Platform Team"
- **Multi-Dimensional**: "Show Security activities during Adoption" → filter by domainTags="Security" AND lifecycleTags="Adoption"

**Knowledge Graph Integration:**

The orthogonal structure enables semantic triples:

- `<Element> hasDomain <DomainTag>`
- `<Element> inLifecycle <LifecycleTag>`
- `<Element> ownedBy <OrganizationalTag>`

These triples support SPARQL queries, graph traversal, and relationship discovery across practice compositions.

**Phase 2 Translation Requirements:**

- Validate tags object has three arrays: domainTags, lifecycleTags, organizationalTags
- Each array can be empty [] (no tags for that dimension)
- Each array contains only strings
- Reject flat tag arrays or tags as simple strings

**Validation:**

```json
// VALID: All three dimensions present, some empty
{
  "tags": {
    "domainTags": ["Security"],
    "lifecycleTags": [],
    "organizationalTags": ["Platform Team", "Security"]
  }
}

// VALID: All dimensions empty
{
  "tags": {
    "domainTags": [],
    "lifecycleTags": [],
    "organizationalTags": []
  }
}

// INVALID: Missing dimensions
{
  "tags": {
    "domainTags": ["Security"]
  }
}

// INVALID: Flat array
{
  "tags": ["Security", "Platform Team"]
}
```

This structured tagging approach transforms simple labeling into a powerful multi-dimensional classification system, enabling sophisticated filtering, search, and knowledge graph operations while maintaining clean semantic separation between classification dimensions.

### 5.2 Checklists and Dynamic State-Gating

The Checklist element introduces sequential verification. A checklist item must represent an actionable task required for phase-gating. When the item carries a `test` or `examples`, those define the completion criteria (definition of done); the item's `name` and `description` are freed to describe what to do and why. Authors should utilize checklists to directly embed and track alphanumeric regulatory or architectural controls (e.g., SOC2 controls, ISO standards, internal architecture OE:05). If a configuration, organizational process, or architectural standard must be completed before moving to the next phase, it must be explicitly destructured into an actionable Checklist object attached to the target State or Level of Detail.

#### 5.2.1 Checklist Object Structure and Validation

Checklists provide the operational verification layer that transforms abstract alpha states and work product levels into concrete, auditable gates. The Practice Language defines a consistent checklist structure used across both alpha states and work product levels of detail.

**Checklist Object Structure:**

```json
{
  "seq": integer,
  "name": "string",
  "description": "string",
  "priority": "must" | "should" | "could" (optional, defaults to "must"),
  "evidencedBy": [WorkProductContribution] (optional),
  "test": Test (optional),
  "examples": [Test] (optional)
}
```

**Field Definitions:**

- **seq**: Integer ordering (1, 2, 3...) determining checklist evaluation sequence within the parent state or level
- **name**: **Action label** — imperative verb phrase identifying the task (3-8 words, e.g., "Define and monitor SLOs", "Document the reference architecture"). Appears in dashboards, task lists, and progress tracking. Carries WHAT to do.
- **description**: **Practitioner guidance** — the briefing a practitioner reads before starting (1-2 sentences). Carries WHY this matters and HOW to approach it: rationale, scope, method, or context not derivable from the name alone. Must not restate the name as a longer sentence. When `test` is present, focus on rationale and approach — the test defines completion criteria. When `test` is absent, the description must also convey what "done" looks like.
- **priority**: Optional MoSCoW-derived importance level (see [Section 5.2.2](#522-checklist-priority)). When omitted, defaults to `"must"` — the item is treated as essential
- **evidencedBy**: Optional array of WorkProductContribution objects linking this checklist to artifacts that provide evidence (see below)
- **test**: Optional Test object providing structured Given/When/Then verification (see [Section 5.3](#53-structured-guidance-the-gherkin-inspired-test-model))
- **examples**: Optional array of Test objects providing parameterized variations (see [Section 5.3](#53-structured-guidance-the-gherkin-inspired-test-model))

**Two Checklist Contexts:**

1. **Alpha State Checklists**: Actionable tasks for achieving an alpha state. Located in State.checklists arrays. These answer "what actions must be completed for this alpha to have reached this state?"
2. **Work Product LOD Checklists**: Quality actions for achieving a work product level of detail. Located in LevelOfDetail.checklists arrays. These answer "what must be done to this artifact for it to be considered at this maturity level?"

**EvidencedBy Structure (Optional but Recommended):**

When present, the evidencedBy array contains WorkProductContribution objects:

```json
{
  "workProductName": "string",
  "levelOfDetailName": "string"
}
```

This creates explicit traceability: "this checklist is satisfied when the specified work product reaches the specified maturity level."

**Validation Rules:**

- Checklists are arrays (can be empty [] if no actionable tasks defined)
- seq numbers provide ordering and should be unique within the parent array
- evidencedBy is optional—checklists can represent actionable tasks without explicit artifact linkage (e.g., organizational approvals, external validations)
- When evidencedBy is present, workProductName must reference a defined work product, and levelOfDetailName must match a level within that work product

**Checklist Authoring Guidance:**

- **Actionable Task**: Each item name is an imperative verb phrase describing a concrete action (e.g., "Define key metrics", "Establish security controls"). When `test` is present, the test's `then` clauses define what "done" looks like. When `test` is absent, the description must convey both the action and its completion criteria.
- **Positive and Additive**: Every checklist item must describe something to achieve, produce, or establish — never the absence or lack of something. Items like "Metrics absent" or "Security gaps identified" describe deficiencies, not achievements; they would need to be unchecked when the deficiency is resolved, which inverts the progressive nature of checklists. Instead, frame as "Define key metrics" or "Establish security controls". Use the state/level description and narratives to characterize qualities of the level (including what may be limited or missing at early stages).
- **Regulatory/Architectural Controls**: Embed specific controls (SOC2 requirements, ISO standards, internal architecture principles) directly as checklist items
- **Phase-Gating**: Checklists represent tasks that must be completed before progression to next state/level
- **Evidence Linkage**: Use evidencedBy when concrete artifacts prove checklist completion; omit when verification is external (e.g., stakeholder approval)
- **Information Independence**: Each field must carry information not present in the others. If you can derive one field from another by changing verb tense, the content is redundant and provides no practitioner value. Litmus test: cover the `name` and read the `description` — does it tell you something new (rationale, scope, method)? Cover both and read `test.then` — does it tell you how to verify completion beyond "was the action performed?"

**Anti-pattern — Echo checklist (INVALID):**

```json
{
  "name": "Identify Target AI Personas",
  "description": "Identify target AI personas across the organization.",
  "test": {
    "name": "Target AI Personas verification",
    "description": "Definition of done.",
    "given": [], "when": [],
    "then": ["target AI personas identified across the organization"]
  }
}
```

The description restates the name as a sentence. The test restates the description in past tense. Empty `given`/`when` provide no verification structure. None of the fields carry information beyond what the name already says.

**Corrected — each field carries distinct information:**

```json
{
  "name": "Identify Target AI Personas",
  "description": "Map the customer's organizational roles that will interact with AI capabilities to inform platform configuration and adoption sequencing.",
  "test": {
    "name": "AI persona coverage verification",
    "description": "Verify that AI personas span all relevant organizational functions.",
    "given": ["Customer has active or planned AI initiatives"],
    "when": ["Account team prepares AI platform engagement plan"],
    "then": [
      "Each business unit with AI initiatives has at least one mapped persona",
      "Persona-capability mapping informs platform configuration priorities"
    ]
  }
}
```

**Example: Alpha State Checklist**

```json
{
  "name": "Architecture Selected",
  "description": "Platform architecture approach chosen and documented",
  "seq": 1,
  "checklists": [
    {
      "seq": 1,
      "name": "Document the reference architecture",
      "description": "Create a reference architecture with technology stack decisions and rationale.",
      "evidencedBy": [
        {
          "workProductName": "Architecture",
          "levelOfDetailName": "Defined"
        }
      ]
    },
    {
      "seq": 2,
      "name": "Complete security review",
      "description": "Engage the security team to review and approve the architecture approach.",
      "evidencedBy": []
    },
    {
      "seq": 3,
      "name": "Validate infrastructure cost model",
      "description": "Develop financial projections for infrastructure costs and secure finance team approval.",
      "evidencedBy": [
        {
          "workProductName": "Financial Model",
          "levelOfDetailName": "Defined"
        }
      ]
    }
  ]
}
```

**Example: Work Product LOD Checklist**

```json
{
  "name": "Defined",
  "description": "Comprehensive architecture documentation",
  "seq": 2,
  "checklists": [
    {
      "seq": 1,
      "name": "Create component diagram",
      "description": "Visually document system components and their relationships."
    },
    {
      "seq": 2,
      "name": "Document technology decisions",
      "description": "Explain each major technology choice with rationale and alternatives considered."
    },
    {
      "seq": 3,
      "name": "Specify integration patterns",
      "description": "Define API contracts, data flows, and integration approaches."
    }
  ]
}
```

**Phase 2 Translation Requirements:**

- Extract checklist arrays from source material for both alpha states and work product LODs
- Validate seq ordering (should be sequential: 1, 2, 3...)
- Validate evidencedBy references against defined work products
- Empty checklist arrays are valid (indicates no actionable tasks from source)
- Missing checklists where source material specifies actionable tasks indicates translation failure

**Operational Semantics:**

The schema validation engine evaluates checklists using strict operational semantics to enable phase-gating:

- Checklists must be satisfied in seq order
- When evidencedBy is present, the specified work product must exist at the specified level before the checklist passes
- Automated tooling can generate task lists from incomplete checklists
- Progress dashboards can visualize checklist completion as state/level achievement indicators

This structured approach transforms qualitative methodology guidance into quantitative, traceable actionable tasks, enabling organizations to measure and validate their adoption progress objectively.

#### 5.2.2 Checklist Priority

The optional `priority` property on Checklist uses a MoSCoW-derived three-level scheme to communicate the relative importance of checklist tasks:

| Value | Meaning | Phase-gating implication |
|---|---|---|
| `"must"` | Essential task. The state or LOD cannot be considered achieved without completing it. | Required unless explicitly overridden via ChecklistState at the project level. |
| `"should"` | Expected and important. Full confidence in the state or LOD requires it, but it can be deferred or excluded with justification. | Included by default; skippable with rationale. |
| `"could"` | Supplementary. Adds depth or rigour but is genuinely optional. | Skippable without justification. |

**Default when omitted:** `"must"`. This preserves backward compatibility — existing documents with no `priority` field behave identically to the pre-priority schema where all items were equally essential. An unprioritized item is never accidentally filtered out by a project-level threshold.

**Why three levels, not four?** MoSCoW's fourth level "Won't" is a scoping decision made by project teams at execution time, not an inherent property of the checklist task. It is already represented by `ChecklistState.state = "not required"` in the project's target section (see [Section 12.5](project-tracking.md#125-checkliststate-and-evidence-tracking)).

**Authoring Guidance for Priority Assignment:**

- **Default to omitting priority.** If every item in a state is essential, leave `priority` absent on all of them — the default of `"must"` communicates this without cluttering the schema.
- **Use `"should"` for items that are important but context-dependent.** If a task is critical in regulated environments but less so in early-stage startups, mark it `"should"` — teams can include or exclude it based on their context.
- **Use `"could"` sparingly.** Reserve it for genuinely supplementary tasks — items that add confidence or rigour but whose absence does not meaningfully compromise the state. If most items in a state are `"could"`, the state's checklist may be over-specified.
- **Priority is stable across projects.** It reflects the practice author's assessment of importance, not a per-project scoping decision. Project-level scoping is handled by the `priorityThreshold` on Project and ProjectCycle (see [Section 12.5.1](project-tracking.md#1251-priority-threshold)).

**Example with Priority:**

```json
{
  "name": "Architecture Selected",
  "description": "Platform architecture approach chosen and documented",
  "seq": 1,
  "checklists": [
    {
      "seq": 1,
      "name": "Document the reference architecture",
      "description": "Create a reference architecture with technology stack decisions and rationale.",
      "evidencedBy": [
        {
          "workProductName": "Architecture",
          "levelOfDetailName": "Defined"
        }
      ]
    },
    {
      "seq": 2,
      "name": "Complete security review",
      "description": "Engage the security team to review and approve the architecture approach.",
      "priority": "should"
    },
    {
      "seq": 3,
      "name": "Validate infrastructure cost model",
      "description": "Develop financial projections for infrastructure costs and secure finance team approval.",
      "priority": "could",
      "evidencedBy": [
        {
          "workProductName": "Financial Model",
          "levelOfDetailName": "Defined"
        }
      ]
    }
  ]
}
```

In this example, "Document the reference architecture" is essential (no `priority` — defaults to `"must"`). "Complete security review" is important but can be deferred in contexts where security review happens later. "Validate infrastructure cost model" is supplementary — valuable for large initiatives but genuinely optional for smaller projects.

### 5.3 Structured Guidance: The Gherkin-Inspired Test Model

The Practice Language adapts concepts from the [Gherkin specification language](https://cucumber.io/docs/gherkin/) to provide structured practitioner guidance across the schema. In software engineering, Gherkin uses a business-readable, domain-specific language to define behaviour through Feature, Background, Scenario, Given/When/Then, and Scenario Outline constructs. The Practice Language repurposes these concepts — not for automated software testing, but for expressing practitioner-facing verification criteria and execution guidance in a structured, decomposable format.

**Design rationale:** Flat name/description pairs on checklist items and activities are sufficient for simple cases, but as practices grow in complexity, practitioners need structured answers to three questions: *what must already be true?* (preconditions), *what action or event is relevant?* (triggers), and *what should be observable afterwards?* (outcomes). Gherkin's Given/When/Then pattern maps directly to these questions. The Practice Language introduces a `Test` type — a PracticeElement with `given`, `when`, and `then` arrays — as the unified vehicle for this structured guidance. The `Background` type captures shared prerequisites at a higher scope (state, level of detail, activity space).

All Gherkin-inspired properties are optional. Existing elements with only name/description remain valid. Any combination of `background`, `test`, and `examples` can be used independently, supporting incremental adoption.

#### 5.3.1 The Test Type

The `Test` type extends `PracticeElement` via `allOf`, inheriting `name`, `description`, `tags`, `narratives`, and `assetNames`. It adds three optional string arrays:

| Property | Type | Purpose |
|---|---|---|
| `given` | string[] | Preconditions that must be true before the scenario is relevant |
| `when` | string[] | Action(s), event(s), or trigger(s) being evaluated |
| `then` | string[] | Expected outcome(s) or observable result(s) |

Because Test is a PracticeElement, every test scenario has its own `name` and `description`, making it a self-contained, identifiable unit. The same Test type is used in two roles:

- **`test`** — an optional property on Checklist and Activity. Captures the primary verification or execution scenario for that element.
- **`examples`** — an optional `Test[]` array on Checklist and Activity. Captures parameterized variations that illustrate how the parent element applies in different contexts (analogous to Gherkin's Scenario Outline).

**And/But conjunctions:** Gherkin's `And` and `But` keywords are expressed as additional array entries. Prefix entries with "but" for negative conditions:

```json
{
  "given": [
    "the monitoring stack is deployed",
    "the SLO framework has been agreed with stakeholders",
    "but the legacy monitoring has not yet been decommissioned"
  ]
}
```

#### 5.3.2 Mapping: Gherkin Concepts to Practice Language

| Gherkin Concept | Practice Language Equivalent | Where Used |
|---|---|---|
| Feature | State, LevelOfDetail, or Activity (name + description) | Already served by existing properties |
| Background | `background` property (Background type) | State, LevelOfDetail, AlphaInstance, WorkProductInstance, ActivitySpaceCore |
| Scenario | Checklist item or Activity (name + description) | Already served; Test adds structured decomposition |
| Given | `test.given` (string[]) | Test on Checklist or Activity |
| When | `test.when` (string[]) | Test on Checklist or Activity |
| Then | `test.then` (string[]) | Test on Checklist or Activity |
| And/But | Additional entries in given/when/then arrays | Natural extension via array items |
| Scenario Outline | `examples` (Test[]) | Checklist or Activity |

#### 5.3.3 Background: Shared Prerequisites

The `background` property declares prerequisites that must hold before any child element (checklist item or activity) can be evaluated. It is available on five types:

- **State**: practice-level prerequisites for an alpha state's checklists
- **LevelOfDetail**: practice-level prerequisites for a work product level's checklists
- **AlphaInstance**: project-specific prerequisites for a tracked alpha instance
- **WorkProductInstance**: project-specific prerequisites for a tracked work product instance
- **ActivitySpaceCore** (inherited by both ActivitySpace and Activity): prerequisites for execution — governance-level on ActivitySpace, activity-specific on Activity

**Background Object Structure:**

```json
{
  "given": ["string"],
  "alphaStates": [AlphaContribution],
  "workProductLevels": [WorkProductContribution],
  "alphaInstanceStates": [AlphaInstanceStateReference],
  "workProductInstanceLevels": [WorkProductInstanceLevelReference]
}
```

All fields are optional. The five properties address different prerequisite scopes:

- **given**: Natural-language preconditions (e.g., "the deployment pipeline is operational"). Use "but" prefix for negative conditions (e.g., "but the legacy system has not been decommissioned").
- **alphaStates**: Abstract alpha states that must be achieved, referencing by alphaName + stateName. Complements sequential progression within the same alpha by declaring cross-alpha prerequisites.
- **workProductLevels**: Abstract work product levels that must be achieved, referencing by workProductName + levelOfDetailName. Expresses the prerequisite direction of the LOD-to-State relationship (complementing the existing `contributesTo` which goes LOD→State).
- **alphaInstanceStates**: Specific alpha instances that must have reached a named state, referencing by instanceName + stateName. Used when prerequisites are about concrete tracked instances.
- **workProductInstanceLevels**: Specific work product instances that must have reached a named level, referencing by instanceName + levelOfDetailName. Used when prerequisites are about concrete tracked instances.

**Two-Level Semantics:**

At the practice level (State, LevelOfDetail), background defines what SHOULD hold — the template prerequisites for any project adopting this practice. At the instance level (AlphaInstance, WorkProductInstance), background records what APPLIES — the actual prerequisites relevant to a specific project context. When both exist, the instance-level background supplements the practice-level background (additive, not replacement). Tooling can merge them to produce a complete prerequisite picture for a given instance.

**Example: State with Background**

```json
{
  "name": "Operational",
  "description": "The platform is serving production workloads reliably.",
  "seq": 3,
  "background": {
    "given": [
      "the platform has passed integration testing",
      "production infrastructure is provisioned"
    ],
    "alphaStates": [
      { "alphaName": "Platform Capability", "stateName": "Validated" }
    ]
  },
  "checklist": [...]
}
```

#### 5.3.4 Test and Examples on Checklist Items

Individual checklist items can carry an optional `test` property (a Test object) and an optional `examples` array (Test[]).

When `test` is absent, the checklist's `name` and `description` must be self-contained — the name states the action, and the description conveys both what to do and what "done" looks like. When `test` is present, it defines the completion criteria (definition of done) — the test's `then` clauses specify what must be observable when the action is complete. The checklist's name/description are freed to focus on the action and its purpose, while the test decomposes completion into preconditions, triggers, and verifiable outcomes. The test's `given` supplements any background-level prerequisites on the parent state or level of detail.

Examples serve as practitioner guidance — they illustrate how a general checklist task applies in specific real-world scenarios. They do not replace the parent checklist's test; they specialise its completion criteria for concrete contexts.

**Test field roles (information independence):**

| Field | Carries | Anti-pattern |
|-------|---------|-------------|
| `test.name` | Short descriptor for the verification scenario | Mechanical "{name fragment} verification" |
| `test.description` | Why this verification matters and what is being verified | Literal "Definition of done." on every item |
| `test.given` | Preconditions — what must be true before verification is meaningful | Always empty `[]` |
| `test.when` | Trigger — the decision point, review event, or lifecycle moment that initiates evaluation | Always empty `[]` |
| `test.then` | Observable evidence of completion — things you can point to, count, or independently verify | Restating name/description in past tense |

A test where `given` and `when` are empty and `then` merely restates the description in past tense is a **skeleton test** — it adds mechanical structure without verification value. Either enrich it with preconditions, triggers, and independently observable evidence, or omit the test entirely.

**Example: Checklist with Test and Examples**

In this example, each field carries distinct information. The name labels the task. The description specifies scope and method (SLOs + monitoring dashboards + burn-rate alerts). The test adds preconditions (observability stack deployed), a trigger (platform team reviews dashboard), and independently verifiable outcomes (each service has >= 1 SLO, alerts fire within window).

```json
{
  "name": "Define and monitor SLOs",
  "description": "Establish service level objectives for critical services and configure monitoring dashboards with burn-rate alerts.",
  "seq": 1,
  "test": {
    "name": "SLO completion criteria",
    "description": "Definition of done: SLOs are defined and alerting is operational.",
    "given": ["the observability stack is deployed"],
    "when": ["the platform team reviews the SLO dashboard"],
    "then": [
      "each critical service has at least one SLO defined",
      "SLO burn-rate alerts fire within the agreed notification window",
      "but no alert fatigue is observed from excessive low-priority notifications"
    ]
  },
  "examples": [
    {
      "name": "API gateway SLO",
      "description": "Completion criteria for external-facing API gateway SLO.",
      "given": ["the API gateway handles external traffic"],
      "when": ["a latency spike exceeds the p99 threshold"],
      "then": ["an alert fires within 5 minutes", "the on-call engineer is paged"]
    },
    {
      "name": "Data pipeline SLO",
      "description": "Completion criteria for nightly data pipeline SLO.",
      "given": ["the ETL pipeline runs on a nightly schedule"],
      "when": ["the pipeline fails to complete within the SLO window"],
      "then": ["a data freshness alert fires", "downstream consumers are notified"]
    }
  ]
}
```

#### 5.3.5 Authoring Guidance

The following guidance applies to all uses of Background, Test, and Examples — whether on checklist items ([Section 5.3.4](#534-test-and-examples-on-checklist-items)) or activities ([Section 8.1.1](execution-and-patterns.md#811-gherkin-inspired-structure-on-activities)).

**When to use Background:**
- When a state, level, or activity space has prerequisites that apply to ALL its children (not just one checklist item or activity)
- When cross-alpha dependencies exist that cannot be expressed through sequential progression
- When work product prerequisites clarify the context for evaluation or execution
- At the instance level, when project-specific conditions supplement or specialise the practice-level background
- On an ActivitySpace, when a governance-level prerequisite applies to all activities in the space (e.g., stakeholder recognition, strategic approval). Do not duplicate ActivitySpace-level prerequisites on individual activities.

**When to use Test:**
- When the existing name/description alone do not convey the full completion criteria (what must be true before, what triggers evaluation, what must be observable after)
- When a checklist item or activity benefits from separating the precondition from the trigger from the completion criteria
- On activities, `test.when` is particularly valuable because it captures the trigger that is otherwise implicit — describe decision points, events, or lifecycle moments that initiate the work
- On activities, `test.then` should complement, not duplicate, the structural `contributesTo` and `worksOn` — use it for outcomes meaningful to practitioners but not captured by symbolic alpha/work-product references (e.g., "risk factors are documented" rather than restating "advances Opportunity to Determined")
- Partial use is valid: a test can have `given` without `when` or `then`, or `then` without `given`

**When to use Examples:**
- When a checklist item or activity applies differently across contexts (e.g., different service types, team structures, deployment models, greenfield vs migration)
- When concrete illustrations would help practitioners understand how to apply a general task
- When the element is inherently parameterized (the same pattern with different values)
- An element can have `examples` without a `test`, or a `test` without `examples`

**When NOT to use these constructs:**
- When the existing name/description adequately convey the task and its completion criteria
- When adding structure would be purely ceremonial without improving practitioner understanding
- When you cannot add information beyond the name and description — a test that restates the description in past tense (e.g., name "Define key metrics" + test.then "key metrics defined") is a skeleton test that adds no verification value. Omit it.
- When `given` and `when` would both be empty — empty preconditions and triggers signal that the test is not grounded in a meaningful evaluation scenario
- When the only `test.description` you can write is "Definition of done." — this indicates the test has no specific verification purpose
- Baseline checklists should remain minimal — the practice layer is the natural place for detailed Gherkin structure


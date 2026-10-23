[< Back to Semantic Guidance Hub](../semantics.md)

## 8 Execution Boundaries and Organizational Roles

### 8.1 Activity Spaces and Activities

- **ActivitySpace**: A generalized boundary categorizing broad areas of effort. Crucially, the ActivitySpace object features an involves array that references PersonaGroup.name. This explicitly links broad execution boundaries directly to grouped organizational roles, ensuring macro-level responsibilities are programmatically mapped to specific talent pools.  
- **Activity**: Extends the Activity Space, providing specific actionable swimlanes. It works on specific artifacts (worksOn) and defines strict recommendedCompetencyLevels. The optional `seq` integer provides deterministic ordering of activities within an activity space — used by external planning tools (e.g., Smartsheet predecessor/seq mapping) to establish predictable sequencing. When absent, activities are unordered within their space.
- **ledBy**: An optional property on ActivitySpaceCore (inherited by both ActivitySpace and Activity) that identifies the single Persona accountable for leading the work. While `involves` maps persona *groups* to the activity (answering "who participates?"), `ledBy` references a single `Persona.name` (answering "who is accountable?"). When omitted, the activity has no designated lead.

**Baseline Isolation Rules**: Practice authors should avoid creating new ActivitySpaces in extension practices. Instead, new tactical Activities should strictly map to existing overarching corporate governance boundaries by utilizing the activitySpaceName property to reference a baseline ActivitySpace.

#### 8.1.1 Gherkin-Inspired Structure on Activities

Activities and ActivitySpaces use the same Gherkin-inspired Test model described in [Section 5.3](practice-elements.md#53-structured-guidance-the-gherkin-inspired-test-model), adapted for execution context rather than verification. While states and checklists answer "what must be true?", activities answer "what work should be done, when, and with what expected outcomes?" See [Section 5.3.5](practice-elements.md#535-authoring-guidance) for consolidated authoring guidance covering both checklists and activities.

**Background on ActivitySpaceCore:**

Both ActivitySpace and Activity inherit an optional `background` property (via ActivitySpaceCore). On an ActivitySpace, `background` declares governance-level prerequisites that apply to all activities in the space. On an Activity, `background` declares activity-specific prerequisites. The Background type is the same as described in [Section 5.3.3](practice-elements.md#533-background-shared-prerequisites).

```json
{
  "name": "Assess Business Value",
  "description": "Conduct business analysis to quantify ROI.",
  "background": {
    "given": ["executive sponsorship has been secured"],
    "alphaStates": [
      { "alphaName": "Stakeholders", "stateName": "Recognized" }
    ]
  }
}
```

**Test and Examples on Activity:**

Activities support an optional `test` property and an optional `examples` array — the same Test type used on Checklist items ([Section 5.3.4](practice-elements.md#534-test-and-examples-on-checklist-items)). The key semantic differences from checklist usage:

- **test.when** captures the *trigger* that initiates work — a decision point, event, or lifecycle moment. This is distinct from `contributesTo` (which says what the activity advances, not when it starts).
- **test.then** complements the structural `contributesTo` (alpha state advancement) and `worksOn` (work product linkage) with human-readable narrative outcomes. It should not restate what the symbolic references already express.

**Example: Activity with Test and Examples**

```json
{
  "name": "Conduct ROI Analysis",
  "description": "Quantify expected return on platform investment.",
  "test": {
    "name": "ROI analysis execution",
    "description": "Verify that a comprehensive ROI analysis is produced.",
    "given": [
      "cost data from comparable implementations is available",
      "but vendor pricing has not been finalized"
    ],
    "when": ["the investment committee requests a business case"],
    "then": [
      "a quantified ROI projection exists with 3-year horizon",
      "risk factors are documented with mitigation strategies"
    ]
  },
  "examples": [
    {
      "name": "Greenfield platform investment",
      "description": "ROI analysis when no prior platform exists.",
      "given": ["no existing platform exists"],
      "when": ["the CTO approves the platform initiative"],
      "then": ["TCO comparison includes build vs buy analysis"]
    },
    {
      "name": "Platform migration",
      "description": "ROI analysis comparing migration costs against ongoing maintenance.",
      "given": ["a legacy platform exists with known maintenance costs"],
      "when": ["the annual budget cycle begins"],
      "then": ["migration cost is quantified against maintenance savings"]
    }
  ]
}
```

### 8.2 Organizational Roles and Persona Definitions

The Persona acts as a direct container for required competencies via the competencies array (linking to CompetencyLevelReference). For broader team mapping, the PersonaGroup element allows tooling to cluster multiple related roles, allowing ActivitySpaces to assign workflows to entire departments rather than isolated individuals.

#### 8.2.1 Hierarchical PersonaGroup Aggregation

A PersonaGroup may include other PersonaGroups as members via the optional `personaGroupNames` array (alongside the existing `personaNames` array for direct Persona membership). This creates a hierarchical aggregation where a parent group transitively includes all personas from its child groups.

**Use cases:**
- **Departmental rollups:** A "Cross-Functional Team" group includes sub-groups "Engineering Team" and "Product Team", each of which directly names individual personas.
- **Baseline extension:** A baseline defines broad role groups; an extension practice creates a specialized sub-group and includes it in the baseline group via merge.

**Membership resolution:** The effective member set of a PersonaGroup is the union of:
1. All personas named directly in `personaNames`.
2. All personas in the transitive closure of groups named in `personaGroupNames` (recursively expanding each child group's `personaNames` and `personaGroupNames`).

**Acyclicity constraint:** The directed graph formed by `personaGroupNames` references must be a DAG. A group cannot directly or transitively include itself. See [Section 14](acyclicity.md) for the full constraint specification.

**Example:**
```json
{
  "personaGroups": [
    {
      "name": "Engineering Team",
      "description": "Technical implementation roles.",
      "personaNames": ["Platform Engineer", "Site Reliability Engineer"]
    },
    {
      "name": "Product Team",
      "description": "Product strategy and design roles.",
      "personaNames": ["Product Manager", "UX Designer"]
    },
    {
      "name": "Delivery Squad",
      "description": "Cross-functional delivery team combining engineering and product.",
      "personaNames": ["Scrum Master"],
      "personaGroupNames": ["Engineering Team", "Product Team"]
    }
  ]
}
```

In this example, "Delivery Squad" effectively includes: Scrum Master, Platform Engineer, Site Reliability Engineer, Product Manager, UX Designer.

## 9 Lifecycle Orchestration: Patterns and Phase Models

Methodologies are orchestrated into overarching temporal models using Pattern elements.

### 9.1 Pattern Orchestration and Narrative Hooks

A Pattern structures language elements into reusable real-world execution lifecycles (e.g., Cloud Adoption Framework phases). These lifecycle models natively hook into the overarching narrative spine. The Pattern object utilizes the narrativeTypeName property to adopt a specific storytelling framework for the entire lifecycle.

### 9.2 The PatternView: Complete Structure and Semantics

A PatternView represents a distinct phase or milestone within a pattern's lifecycle, filtering the methodology to display only the elements, states, and activities relevant to that temporal window. PatternViews orchestrate progression tracking by declaring expected alpha states, tracking specific instances, identifying key deliverables, and coordinating active work.

**Complete PatternView Structure:**

```
PatternView {
  seq: integer (0 for prerequisites, 1+ for main phases)
  name: string (phase identifier)
  description: string (max 12 words - essence of this phase)
  narrativeContexts: array (optional - narrative slices for this phase)
  alphaStates: array (AlphaContribution objects - expected states)
  alphaInstances: array (AlphaInstance objects - instance tracking)
  workProducts: array (WorkProductContribution objects - deliverables)
  workProductLevels: array (WorkProductContribution objects - WP LOD objectives)
  activities: array (strings - activity names active in this phase)
}
```

**AlphaContribution Structure (Expected States):**

The alphaStates array declares which alphas should reach which states during this phase, using AlphaContribution objects:

- alphaName: References baseline or practice-defined alpha
- stateName: Target state for this phase
- evidenceBy: Array of WorkProductContribution objects that prove state achievement

Purpose: AlphaContribution objects answer "what conceptual milestones should be reached in this phase, and what deliverables prove them?" They represent the expected progression for abstract alphas.

**AlphaInstance Structure (Instance Tracking):**

The alphaInstances array tracks specific instances (see [Section 6.5](alphas.md#65-alpha-instance-semantics-guidance-vs-tracking)) within this phase, using AlphaInstance objects:

- instanceName: Must match a declared AlphaInstanceName
- alphaName: The baseline or practice alpha this instance represents
- stateName: The target state for this specific instance in this phase
- evidenceBy: Array of WorkProductInstance objects proving instance state

Purpose: AlphaInstance objects answer "what specific occurrences are we tracking, what state should each achieve, and what concrete artifacts prove it?" They enable concurrent tracking of multiple instances with distinct progression paths.

**WorkProductContribution Structure (Key Deliverables):**

The workProducts array identifies which work products should be developed to which maturity levels:

- workProductName: References baseline or practice-defined work product
- levelOfDetailName: Target level of detail for this phase

Purpose: WorkProductContribution objects answer "what artifacts should exist at what maturity by the end of this phase?" They establish deliverable milestones independent of evidence chains.

**WorkProductLevels Array (Work Product LOD Objectives):**

The `workProductLevels` array declares which work products should reach which levels of detail during this phase, using the same `WorkProductContribution` objects as `workProducts`. It complements `alphaStates` (which declares alpha state objectives) with work product maturity objectives.

- workProductName: References baseline or practice-defined work product
- levelOfDetailName: Target level of detail for this phase

Purpose: `workProductLevels` answers "what work product maturity milestones should be reached by the end of this phase?" While `workProducts` within `alphaStates.evidenceBy` ties work product maturity to specific alpha state evidence chains, `workProductLevels` declares phase-level work product objectives independently of alpha evidence. This enables planning and tracking of work product maturity even when the alpha-to-LOD mapping is not one-to-one.

**Activities Array (Active Work):**

The activities array contains simple strings—activity names that are actively performed during this phase. These reference Activity.name values defined elsewhere in the practice.

Purpose: The activities array answers "what work is being done in this phase?" It filters the full activity catalog to show only phase-relevant work.

**Narrative Contexts Array (Phase Storytelling):**

Individual PatternView elements utilize the narrativeContexts array to embed contextual, authored narrative slices directly into the lifecycle phase. Rather than acting as a static anchor, this allows a single PatternView to articulate its role across one or more narrative elements (e.g., providing the specific prose for both the 'Task' and 'Action' of a STAR narrative within a given phase).

Each NarrativeContext object contains:

- seq: Ordering within the phase's narrative
- narrativeElementName: Symbolic link to NarrativeElement from the Pattern's NarrativeType
- context: Authored prose (1-2 sentences providing phase-specific context)

The NarrativeContext must reference elements within the NarrativeType declared in the parent Pattern under the narrativeTypeName.

**Pruning Rules for Lifecycle Clarity:**

To maintain focus and prevent matrix bloat, operational tooling and authors should apply strict pruning:

1. **Cross-Pattern Pruning**: If an alpha's state does not change across the entire lifecycle (Pattern), it should be removed from all PatternViews. Only alphas that transition are relevant to lifecycle tracking.
2. **Sequential View Pruning**: If an alpha's state remains identical between two consecutive PatternViews, omit it from the subsequent view. Only show active state transitions to highlight what changes in each phase.
3. **Prerequisites Phase**: When mapping lifecycles, authors must explicitly account for "Phase 0" or preparation steps by creating a dedicated prerequisite PatternView at seq: 0. This establishes baseline conditions before the main progression begins.

**Empty Arrays Interpretation:**

- **Deliberate Empty Array []**: Explicitly indicates this phase has zero items for that dimension (e.g., no new alphas progress, no specific activities)
- **Missing Array / Null**: Indicates translation failure or incomplete specification
- **Validation**: Phase 2 translation distinguishes between intentionally empty arrays (valid) and missing content (error)

**Complete Example:**

```json
{
  "seq": 2,
  "name": "Foundation Build",
  "description": "Establish core platform infrastructure",
  "narrativeContexts": [
    {
      "seq": 1,
      "narrativeElementName": "Task",
      "context": "Build the foundational infrastructure and establish core capabilities that enable platform services."
    },
    {
      "seq": 2,
      "narrativeElementName": "Action",
      "context": "Deploy infrastructure, configure networking, establish security controls, and validate platform readiness."
    }
  ],
  "alphaStates": [
    {
      "alphaName": "Platform",
      "stateName": "Provisioned",
      "evidenceBy": [
        {
          "workProductName": "Platform Infrastructure",
          "levelOfDetailName": "Applied"
        }
      ]
    }
  ],
  "alphaInstances": [
    {
      "instanceName": "Core Platform",
      "alphaName": "Platform",
      "stateName": "Provisioned",
      "evidenceBy": [
        {
          "instanceName": "Platform Architecture",
          "workProductName": "Architecture",
          "levelOfDetailName": "Comprehensive"
        }
      ]
    }
  ],
  "workProducts": [
    {
      "workProductName": "Architecture",
      "levelOfDetailName": "Comprehensive"
    },
    {
      "workProductName": "Infrastructure Code",
      "levelOfDetailName": "Applied"
    }
  ],
  "workProductLevels": [
    {
      "workProductName": "Architecture",
      "levelOfDetailName": "Comprehensive"
    },
    {
      "workProductName": "Infrastructure Code",
      "levelOfDetailName": "Applied"
    },
    {
      "workProductName": "Security Assessment",
      "levelOfDetailName": "Defined"
    }
  ],
  "activities": [
    "Deploy Infrastructure",
    "Configure Networking",
    "Establish Security Controls"
  ]
}
```

**Validation Requirements:**

- Every alphaName must reference a defined alpha (baseline or practice)
- Every stateName must match a state within the referenced alpha
- Every workProductName must reference a defined work product
- Every levelOfDetailName must match a level within the referenced work product
- Every activity name must match a defined Activity.name
- Every instanceName in alphaInstances must match a declared AlphaInstanceName
- narrativeElementName values must match elements from the Pattern's NarrativeType

This comprehensive structure enables PatternViews to orchestrate methodology execution, tracking both abstract progression (alphaStates) and concrete instances (alphaInstances), coordinating deliverables (workProducts), declaring work product maturity objectives (workProductLevels), and guiding work (activities), all while providing narrative context that connects the phase to stakeholder-friendly storytelling frameworks.

### 9.2a Cyclical Patterns: Declaring That Phases Repeat

Iterative delivery is cyclical. A pattern's views advance in `seq` order, and until now the guidance described nothing but forward motion, so an author reading it reasonably concluded that a recurring cycle — plan, build, review, adapt, repeat — could not be expressed. Nothing in fact forbade it; the absence of any statement was doing the work.

`loopsBackTo` on the view where the cycle closes declares the return:

```json
{
  "name": "Adapt",
  "description": "Fold what the review found back into the plan.",
  "seq": 4,
  "alphaStates": [ ],
  "loopsBackTo": {
    "patternViewName": "Plan",
    "description": "Each increment re-plans from what the last one proved.",
    "condition": {
      "name": "More increments remain",
      "given": ["the release objective is not yet met"],
      "when": ["the increment review completes"],
      "then": ["the team re-enters planning for the next increment"]
    }
  }
}
```

**An edge, not a range.** The loop is expressed as an edge from the closing view to the view it returns to, rather than as a cycle declared on the pattern. This composes: several edges give nested or chained cycles — a build loop inside a release loop — where a single range could express only one cycle per pattern. It is also what gets drawn, as an arc from a later column back to an earlier one in the pattern matrix. And it leaves `seq` as the ordering authority, so a consumer that does not understand `loopsBackTo` still renders a correct linear pattern.

#### 9.2a.1 What Repeats, and What Does Not

**The work repeats; the maturity does not reset.** A loop re-runs the activities and work product maturation of the views it spans. A re-entered view's declared `alphaStates` are the **minimum that must hold on that pass**, not a reset to that state. Re-entering a "Plan" view that declares `Platform → Identified` does not mean the platform stops being Available; it means planning happens again with the platform at least Identified.

**Progress does not drop when a team iterates.** On re-entering an earlier view, the achieved forecast is the **highest weight reached on any pass**, not the weight attached to the view currently being worked. Without this rule a team's reported progress would fall every time they went round, which is precisely the complaint that cyclical delivery was impossible to represent honestly.

**The loop is a path to the end, not an alternative to it.** The pattern's final view remains the terminal objective. A cycle is how a team reaches it, and `loopsBackTo.condition` states when the loop is taken rather than exited.

**Sequential view pruning needs an exception inside a loop.** [Section 9.2](#92-the-patternview-complete-structure-and-semantics) rule 2 says to omit an alpha from a later view when its state is unchanged. On a re-entered view most states hold, so pruning strictly applied would empty the view out and hide what the iteration actually works on. Inside a loop, show what the iteration works on even where the state is unchanged.

#### 9.2a.2 Enacting a Cycle in a Project

The project side of this already existed before the declaration did. A `ProjectCycle` carries an optional `patternViewName`, and [Section 12.7](project-tracking.md#127-cycles-and-operational-work-tracking) already allowed several cycles to contribute to the same phase.

What `loopsBackTo` adds is the practice-level statement that going round again was *intended*. Successive cycles carrying the **same** `patternViewName` with different per-instance target states are what distinguish one lap from the next. See [Section 12.4](project-tracking.md#124-current-target-and-cycles) for how a cycle expresses its targets.

#### 9.2a.3 Relationship to the Acyclicity Constraints

Patterns appear nowhere in [Section 14](acyclicity.md), and a `loopsBackTo` edge does not change that. It is a **temporal** edge — it says work repeats — whereas Section 14 governs **structural** graphs: containment, specialization, and prerequisites. A pattern whose views loop still may not declare a cycle in `Background.alphaStates` or `Background.workProductLevels`; a prerequisite cycle is unsatisfiable regardless of how many times the work goes round.

### 9.3 Pattern Groups: Organising Patterns for Navigation

> **Deprecated as of schema 2.21.0.** Use [pattern orchestration](#95-pattern-orchestration-layering-patterns-across-an-endeavour) instead. Orchestration does everything a group does and adds the sequencing and entry/exit criteria that groups were increasingly being bent into expressing, and the other thing groups were used for — seeing which practice a pattern came from — is already available without them, because the merge stamps `sourcePracticeName` on every pattern ([merge.md Section 8.1](../merge.md#81-practice-level-provenance-sourcepracticename)).
>
> Pattern groups remain valid and are still merged exactly as described below; 203 authored documents use them and none of them break. They are scheduled for removal at the next major version.
>
> **Migrating.** Where the order of a group's entries means *then* — this pattern, then that one — it was already an orchestration, so declare it as one and give each stage its criteria. Where the group only answered *which practice contributed this?*, drop it and group on `sourcePracticeName` at the point of display. Baselines defining canonical groups with empty `entries` under [Section 9.3.1](#931-baseline-defined-canonical-groups) should stop doing so; that is the strongest form of the construct and the one with the most to unpick, so it is being handled as its own piece of work rather than alongside this change.

In methods composed of many practices, patterns from all practices are unioned into a flat list. A method with three practices contributing three patterns each produces nine patterns; a five-practice method may have fifteen or more. At this scale a flat list becomes unwieldy — users need navigational structure to find the patterns relevant to their current concern.

**PatternGroup** provides this structure. A PatternGroup is a named element that contains an ordered list of pattern references (`entries`), each pairing a `patternName` with a `seq` for sort order within the group. The group itself carries an optional `seq` for ordering groups relative to each other.

#### 9.3.1 Baseline-Defined Canonical Groups

Baselines define canonical patternGroups with **empty `entries` arrays**. These establish the navigational categories that extension practices should adopt. The baseline author identifies 3-5 groups based on the coordination archetypes most relevant to the domain (see grouping strategies below).

Extension practices then adopt baseline groups by defining patternGroups with the **same canonical name** and populating their `entries` with the practice's patterns. During method composition, groups with matching names merge via the [merge algorithm](../merge.md#615-patterngroup-merging), producing a single group per category that collects patterns from all contributing practices.

**Governance rules:**

- **Prefer adopting baseline groups.** When a practice's patterns fit an existing baseline group, use it. The baseline author has already identified the navigational categories most useful to consumers of the domain.
- **Novel groups require justification.** An extension practice may define a new patternGroup not present in the baseline, but only when its patterns represent a coordination concern genuinely absent from the baseline categories. The group name and description should make the rationale clear.
- **Never rename baseline groups.** Changing the name of a baseline group breaks the merge contract. If a baseline group name is suboptimal, update the baseline — don't work around it in extensions.

**Why baselines define groups:**

Without baseline-defined groups, each extension practice independently invents group names. In a three-practice method, this produces three disjoint sets of categories with no cross-practice merging — defeating the purpose of groups. Baseline-defined groups act as a shared vocabulary, ensuring that patterns from different practices land in coherent, merged categories.

Both practice and baseline validators report a `deprecation` warning for a non-empty `patternGroups` array, including groups whose `entries` are empty. The declaration remains valid; an absent or empty array produces no warning.

#### 9.3.2 When to Use PatternGroups

- When a practice contributes three or more patterns.
- When a method will compose ten or more patterns from multiple practices.
- Single-pattern practices generally do not need groups.

#### 9.3.3 Grouping Strategies

The source practice is already visible via `sourcePracticeName` — grouping by source practice is redundant. Instead, group by the coordination intent that cuts across practices:

- **By lifecycle archetype** — the most common strategy. Many practices naturally produce patterns that fall into archetypes: core lifecycles (the primary journey of each practice), optimisation cycles (iterative improvement patterns), and maturity progressions (patterns tracking growth along a maturity axis). For example, in a horticulture method with three practices, each contributing a primary lifecycle, an improvement cycle, and a maturity pathway, the nine patterns can be grouped into three groups of three — each group collecting one pattern from each practice.
- **By concern area** — when patterns map to distinct stakeholder concerns that span practices (e.g., technical patterns, governance patterns, operational patterns).
- **By engagement phase** — patterns relevant to getting started vs ongoing execution vs scaling and optimisation.

#### 9.3.4 Naming Guidance

Group names should describe the organisational category, not duplicate practice names:

- **Good**: "Core Lifecycles", "Maturity Progressions", "Governance & Compliance"
- **Bad**: "Plant Biology Patterns", "Production Patterns" (restates the source practice)

#### 9.3.5 Cross-Practice Merging

When two practices define a PatternGroup with the same canonical name, they merge into a single group during method composition (see [merge.md Section 6.15](../merge.md#615-patterngroup-merging)). This is the primary mechanism by which baseline-defined groups collect patterns from multiple practices into coherent categories.

#### 9.3.6 Ordering

- `PatternGroup.seq` orders groups relative to each other (e.g., Core Lifecycles before Maturity Progressions).
- `PatternGroupEntry.seq` orders patterns within each group.
- When `seq` is absent on a group, groups sort alphabetically by name.

#### 9.3.7 Ungrouped Patterns

Patterns not referenced by any PatternGroup remain valid and accessible. Consuming systems should render them in a default or ungrouped section. A pattern should appear in at most one group.

#### 9.3.8 Schema Structure

```
PatternGroup {
  name: string (group identifier)
  description: string (explains what this group covers)
  entries: PatternGroupEntry[] (required, minItems: 0)
  seq: integer (optional — presentation order among groups)
}

PatternGroupEntry {
  patternName: string (symbolic link to Pattern.name)
  seq: integer (sort order within the group)
}
```

Baselines define groups with `entries: []`. Extension practices define groups with populated entries. The [merge algorithm](../merge.md#615-patterngroup-merging) unions entries from groups sharing the same canonical name.

### 9.4 Outcome Definitions and Value Measurement

Outcomes define how a practice delivers measurable value. While narratives articulate *why* a practice matters, outcomes define *how value delivery is tracked* — connecting practice elements to quantifiable progress indicators.

An Outcome extends PracticeElement and operates as a template. Practices declare outcomes with measurement frameworks; projects instantiate them as OutcomeInstances with specific targets (see [Section 12.8](project-tracking.md#128-outcome-instances-and-value-tracking)).

#### Two Contribution Mechanisms

Outcomes support two distinct measurement mechanisms that operate on different underlying concepts:

**Metric Contributions** — aggregate numerical values through the alpha → work product → metrics evidence chain. A MetricContribution declares:
- Which alpha's instances to follow (`alphaName`); `mapsTo` variants of that alpha also contribute
- Which metric to extract from their evidencing work product instances (`metricName`)
- Optionally which work product type carries the metric (`workProductName`); when omitted, any evidencing work product with that metric name contributes
- At which alpha state the metric is fully recognized (`recognizedAtStateName`)
- State-level probability weights for forecast calculation (`forecastWeights`)

The evidentiary chain is specified in [Section 12.8](project-tracking.md#128-outcome-instances-and-value-tracking). Rates (percentages, ratios) should be stored as an already-computed value on one work product instance — do not ask the engine to average or otherwise reduce deal-level metrics into a rate.

**Objective Contributions** — compute percentage progress from completion, measured either against one pattern's views or against one orchestration's stages. Which of the two a contribution uses is declared the same way an `OrchestrationStage` declares its target: `patternName` and `orchestrationName` are mutually exclusive, and exactly one is present.

A pattern-scoped contribution declares:
- Which pattern's views are used to measure progress (`patternName`)
- At which pattern view the outcome is fully achieved (`recognizedAtPatternViewName`)
- View-level weights for cumulative progress calculation (`forecastWeights`)

An orchestration-scoped contribution declares:
- Which orchestration's stages are used to measure progress (`orchestrationName`)
- At which stage the outcome is fully achieved (`recognizedAtStage`)
- Stage-level weights for cumulative progress calculation (`stageForecastWeights`)

A consuming system checks which pattern views have been completed (all alpha state and work product objectives met for that phase), then applies the weight for the highest completed view — or, for an orchestration, the highest completed stage, resolved as below.

#### Recognising an Outcome Against an Orchestration

A practice may exist to declare an orchestration and nothing else — composing patterns its dependencies own, holding none of its own ([Section 9.5.6](#956-choosing-the-level)). That practice is usually the one with the best claim to the outcome, because it is the document describing the endeavour end to end while each constituent pattern sees only its own track. Pushing the outcome down into a constituent attributes it to a narrower scope than the one that earns it.

**A stage is identified by what it places and what it is placed against.** A stage carries no name, so `recognizedAtStage` and each entry in `stageForecastWeights` reference one by its `patternName` or `orchestrationName` together with its `relativeTo` host — the same composite key the merge uses ([Section 9.5.3](#953-reuse-and-cycles)). The reference is that key rather than a search for it: name the host where the stage declares one, and omit it where the stage has none, as sequential and on-demand stages do. Resolution is then a lookup, and a reference means the same stage to every consumer.

The alternative — naming only the target and disambiguating when it turns out to be placed twice — reads shorter and resolves worse. It needs a rule for the sprint that is nested in a milestone plan *and* available on demand, two implementations can disagree about that rule, and the on-demand placement has no host to disambiguate it with, so it could not be named at all.

References resolve against the **merged** orchestration, so stages contributed by the baseline chain and by declared dependencies are available to name, not only the stages this document wrote.

**A stage completes when the thing it places completes, and that resolves downwards.** A stage naming a pattern is complete when that pattern's views are complete, which is what view completion already means everywhere else and what a project records through `ProjectCycle.patternViewName` ([Section 12.7](project-tracking.md#127-cycles-and-operational-work-tracking)). A stage naming an orchestration is complete when that orchestration's own stages resolve the same way, one level down. The recursion terminates because an orchestration may not embed itself directly or through a chain ([Section 14.1.8](acyclicity.md#1418-patternorchestration-embedding-hierarchy-orchestrationstageorchestrationname)).

The consequence is that an orchestration-scoped outcome needs nothing new at the project level. It is computed from the same pattern view completions a pattern-scoped one is, aggregated through the shape of the endeavour rather than read off a single pattern.

**Sequence is what makes a curve mean anything.** `seq` is a strict order only among sequential stages; concurrent and nested stages are anchored to their host's position and on-demand stages have no position at all. Weights are therefore most legible across the sequential spine, with other stages weighted where they sit. An on-demand stage is a poor recognised point — an outcome that reaches full weight only when an exception is triggered is almost always a modelling mistake — so the validator warns where one is named.

#### Forecast Weights

Both contribution types use an analogous forecast weight pattern:

- **StateForecastWeight** maps alpha state names to probability weights (0–1). States not listed have implicit weight 0. The `recognizedAtStateName` should correspond to a weight of 1.0 in the forecast array.
- **ViewForecastWeight** maps pattern view names to cumulative progress weights (0–1). Views not listed have implicit weight 0. The `recognizedAtPatternViewName` should correspond to a weight of 1.0.
- **StageForecastWeight** maps orchestration stages to cumulative progress weights (0–1), by the same rule one level up. Stages not listed have implicit weight 0, and the stage named by `recognizedAtStage` should correspond to a weight of 1.0.

Forecast weights enable systems to compute weighted projections before full recognition — e.g., a sales pipeline that counts Committed opportunities at 80% and Best Case at 40%.

#### Authoring Guidance

- An outcome may have metric contributions, objective contributions, or both
- Use metric contributions when the outcome's progress is a numerical aggregate from external data (revenue, user counts, capacity)
- Use objective contributions when the outcome's progress maps to lifecycle phase completion (readiness, maturity, compliance)
- Scope an objective contribution to an orchestration when the practice owns the shape of the endeavour rather than its phases; a practice declaring an orchestration and no patterns is the clear case
- Scope it to a pattern when the practice owns that pattern, or depends on one whose phases are the right granularity for the outcome. Pattern names resolve across the baseline chain and declared dependencies, as every other symbolic link does
- The `measureDescription` should explain the measurement framework clearly enough for project teams to set meaningful targets
- Metric names in MetricContributions must match the `name` field on Metric objects in work product instances (see [Section 7.4](work-products.md#74-work-product-instance-metrics))
- When `workProductName` is set, it must match a WorkProduct.name in the practice or its dependencies
- Declare `expectedMetrics` on the work product that supplies each `metricName`
- State and view names in contributions are symbolic links and must match names within the referenced alphas and patterns
- Default project cardinality is **one OutcomeInstance per Outcome template**; do not instantiate one outcome per contributing alpha instance

#### Example: Practice with Both Outcome Types

```json
{
  "outcomes": [
    {
      "name": "Account Revenue",
      "description": "Total recognized revenue from managed opportunities.",
      "measureDescription": "Annual contract value (ACV) in target currency.",
      "metricContributions": [
        {
          "alphaName": "Opportunity",
          "metricName": "acv",
          "recognizedAtStateName": "Closed Won",
          "forecastWeights": [
            { "stateName": "Closed Won", "weight": 1.0 },
            { "stateName": "Committed", "weight": 0.8 },
            { "stateName": "Best Case", "weight": 0.4 },
            { "stateName": "Pipeline", "weight": 0.1 }
          ]
        }
      ]
    },
    {
      "name": "Account Readiness",
      "description": "Maturity of the strategic engagement lifecycle.",
      "measureDescription": "Percentage of lifecycle milestones achieved.",
      "objectiveContributions": [
        {
          "patternName": "Strategic Account Lifecycle",
          "recognizedAtPatternViewName": "Realize Value",
          "forecastWeights": [
            { "patternViewName": "Know Your Customer", "weight": 0.15 },
            { "patternViewName": "Build Your Strategy", "weight": 0.50 },
            { "patternViewName": "Make It Happen", "weight": 0.75 },
            { "patternViewName": "Realize Value", "weight": 1.0 }
          ]
        }
      ]
    }
  ]
}
```

#### Example: An Outcome on a Composition Practice

A practice that holds no patterns, declares one orchestration over patterns its dependencies own, and measures the endeavour it composes:

```json
{
  "outcomes": [
    {
      "name": "Programme Benefits Realised",
      "description": "The benefits the programme was chartered to deliver.",
      "measureDescription": "Percentage of the programme shape completed, weighted by tranche.",
      "objectiveContributions": [
        {
          "orchestrationName": "Programme Endeavour",
          "recognizedAtStage": { "orchestrationName": "Project Endeavour" },
          "stageForecastWeights": [
            { "stage": { "patternName": "Tranche Plan" }, "weight": 0.3 },
            { "stage": { "orchestrationName": "Project Endeavour" }, "weight": 1.0 }
          ]
        }
      ]
    }
  ]
}
```

The second stage is an embedded sub-endeavour, and naming it as the recognised point says the programme is realised when the project endeavour run inside it is. Resolving that stage goes one level down into the project's own stages and then into pattern views, which is where the project data lives.

Where the same orchestration places `Sprint` twice — nested in a milestone plan and again on demand — the two are different stages, and a weight entry names the host to say which it means. The nested placement:

```json
{ "stage": { "patternName": "Sprint", "relativeTo": { "patternName": "Milestone Plan" } }, "weight": 0.6 }
```

The on-demand one, which declares no host, carries no `relativeTo` either:

```json
{ "stage": { "patternName": "Sprint" }, "weight": 0.2 }
```

#### Validation Rules

- `MetricContribution.alphaName` must match an Alpha.name in the practice or its dependencies
- `MetricContribution.workProductName`, when present, must match a WorkProduct.name in the practice or its dependencies
- `MetricContribution.recognizedAtStateName` must match a State.name within the named alpha
- `MetricContribution.forecastWeights[].stateName` must match a State.name within the named alpha
- `ObjectiveContribution` carries exactly one of `patternName` and `orchestrationName`, with the recognition property and weight array of the other arm absent
- `ObjectiveContribution.patternName` must match a Pattern.name in the practice, its baseline chain or its declared dependencies
- `ObjectiveContribution.recognizedAtPatternViewName` must match a PatternView.name within the named pattern
- `ObjectiveContribution.forecastWeights[].patternViewName` must match a PatternView.name within the named pattern
- `ObjectiveContribution.orchestrationName` must match a PatternOrchestration.name in the same scope
- `ObjectiveContribution.recognizedAtStage` and each `stageForecastWeights[].stage` must match a stage of the merged orchestration on target and host together. A reference matching none is an error, including one that omits the host of a stage that declares one
- The stage named by `recognizedAtStage` must appear in `stageForecastWeights` carrying weight 1.0, as `recognizedAtPatternViewName` must in `forecastWeights`
- Naming an `onDemand` stage as the recognised point is a warning, not an error

### 9.5 Pattern Orchestration: Layering Patterns Across an Endeavour

Most patterns address one aspect of an endeavour — initial bootstrap, steady-state operation, cyclical change, release management, decommissioning. A `PatternOrchestration` expresses the level above: the shape of the whole, and how its constituent patterns are layered against one another. Some follow one another, some run alongside, some repeat inside the phases of a larger plan, and some are reached for when the team recognises the need.

```json
{
  "kind": "patternOrchestration",
  "name": "Platform Endeavour",
  "description": "The whole life of a platform, from first build to retirement.",
  "narrativeTypeName": "STAR",
  "stages": [
    {
      "patternName": "Bootstrap the Platform",
      "seq": 1,
      "exitCriteria": {
        "name": "Platform is usable",
        "description": "Whether the platform can carry a real workload.",
        "given": ["the platform has been built"],
        "when": ["a team deploys a production workload to it"],
        "then": ["the workload runs without manual intervention by the platform team"]
      },
      "narrativeContexts": [
        { "seq": 1, "narrativeElementName": "Situation", "context": "No shared foundation exists and every team builds its own." }
      ]
    },
    {
      "patternName": "Operate and Recover",
      "seq": 2,
      "entryCriteria": {
        "alphaStates": [{ "alphaName": "Platform", "stateName": "Operating" }]
      }
    }
  ]
}
```

**Why a distinct construct and not an extension of PatternGroup.** Putting sequencing and criteria on groups would have produced an ordering no single author owns, with each practice's `seq` values competing and nothing on an entry to say what the order meant. An orchestration avoids that because every stage declares its own placement and its owner keeps it: an orchestration's name may be extended by several practices ([Section 9.5.5](#955-baseline-published-shells)), but each stage within it belongs to whoever wrote that stage, and an overlay adds rather than re-places. Reusing `Pattern` recursively is also wrong: a `PatternView` requires `alphaStates`, and a view that orchestrates sub-patterns has none of its own.

**Entry criteria reuse `Background`.** It already expresses alpha-state and work-product-level prerequisites, and it is already covered by the acyclicity constraints in [Section 14.2](acyclicity.md#142-cross-element-prerequisite-cycles), so the stage prerequisite graph is protected against cycles without a new rule. Exit criteria reuse `Test`, matching how Gherkin is already carried on activities and checklists.

#### 9.5.1 How a Stage Is Placed

Real endeavours are layered, not a queue. Some patterns follow one another, some run alongside one another for a stretch, some repeat inside the phases of a larger plan, and some are run because the team recognised partway through that they were needed. `relationship` says which of these a stage is.

| Relationship | Placed by | Use for |
|---|---|---|
| `sequential` | Its own `seq`, after the preceding sequential stage | Phases that genuinely follow one another — bootstrap, then steady-state, then decommissioning |
| `concurrent` | The span of the pattern in `relativeTo` | A parallel track at the same level: assurance running alongside delivery for the whole of it |
| `nested` | Inside the pattern in `relativeTo`, bounded by it | A smaller cycle inside a larger plan: a sprint inside each phase of a milestone plan |
| `onDemand` | Nothing. Entered when `trigger` is recognised | A pattern run because circumstances called for it, not because it was next |

**`relationship` is always declared.** There is no default and omitting it is an error. How a pattern is layered into an endeavour is a modelling decision — whether assurance runs alongside delivery or waits its turn changes what the orchestration means — and a reader should not have to infer that from silence. A stage that genuinely follows the one before says `"relationship": "sequential"` and says it out loud.

**`seq` means different things by relationship.** For a sequential stage it is position in the order and must be unique among the sequential stages. For every other relationship it is the anchor point for presentation, and stages that begin alongside one another may share it. This is the one place the property is not a strict total order, and it is deliberate: concurrency has no total order to express.

**Uniqueness is across the merged orchestration, not within one document.** An orchestration's name may be extended by several practices ([Section 9.5.5](#955-baseline-published-shells)), so two of them taking the same sequential position produce one merged orchestration with two stages claiming to be third. Each document is internally consistent, which is why the position has to be read against every contribution in scope rather than against the document in hand.

**Concurrent against nested.** Both run during another pattern, and the distinction is subordination. A concurrent stage is a peer: it has its own lifetime, the host does not bound it, and it renders as a track beside the host. A nested stage is contained: the host's phase boundary ends it, and it renders inside the host. If the question "what happens to this pattern when the host's phase ends?" answers *it stops*, it is nested; if it answers *it carries on*, it is concurrent.

Validation warns once per merged orchestration when it has stages but none declares `relationship: "sequential"`. The check includes the baseline chain, dependencies and all practices in a method. An empty shell stays silent. An `onDemand` host with nested or concurrent stages still triggers the warning: hosting other stages does not declare progression.

##### Scoping to particular phases

`relativeTo.viewNames` narrows a concurrent or nested stage to named views of the host pattern. Omitted, the stage covers the whole host.

##### Repeating inside each phase

`recurrence` decides whether the stage runs once across the span it is placed in, or restarts for each host view in scope.

```json
{
  "patternName": "Sprint",
  "seq": 2,
  "relationship": "nested",
  "relativeTo": { "patternName": "Milestone Plan" },
  "recurrence": "perView",
  "exitCriteria": {
    "name": "Increment accepted",
    "description": "Whether the increment met the phase objective it was serving.",
    "given": ["a sprint has run to its end"],
    "when": ["the increment is reviewed against the phase objective"],
    "then": ["the increment is accepted or its shortfall carries into the next sprint"]
  }
}
```

That is the milestone-plan-with-sprints case: the sprint pattern repeats within every phase of the host plan rather than running once across all of them. `"recurrence": "once"`, the default, places the stage once across the whole span.

Repetition *within* a single run of a pattern is a different thing and is already handled — a pattern whose own views loop uses `loopsBackTo` ([Section 9.2a](#92a-cyclical-patterns-declaring-that-phases-repeat)). Use `recurrence` for "this pattern starts again at each phase boundary", and `loopsBackTo` for "this pattern's own phases go round".

##### Patterns the team reaches for

An `onDemand` stage has no position. It declares a `trigger` — what the team recognises that causes the pattern to be run — and is entered whenever that holds, however many times that turns out to be.

```json
{
  "patternName": "Incident Response",
  "seq": 4,
  "relationship": "onDemand",
  "trigger": {
    "name": "Production impact recognised",
    "description": "What the team notices that causes the incident pattern to be run.",
    "given": ["the platform is carrying production workloads"],
    "when": ["a user-visible failure is recognised by anyone on the team"],
    "then": ["the incident response pattern is entered regardless of the phase in progress"]
  }
}
```

This is the difference between a plan and a repertoire. Sequential, concurrent and nested stages say what the endeavour intends to do; an `onDemand` stage says what it is prepared to do.

#### 9.5.2 Narrative Binding

Where an orchestration declares a `narrativeTypeName`, its design follows that narrative template, and its stages reference the template's component parts — exactly the relationship a Pattern has with its PatternViews.

Each stage's `narrativeContexts` entry carries a `seq`, a `narrativeElementName` resolving to a `NarrativeElement` **inside the NarrativeType named on the enclosing orchestration**, and the authored `context` prose for that stage. A four-stage orchestration under a STAR narrative can place one stage per narrative element; a stage may also span more than one element, as a pattern view can.

`narrativeTypeName` is optional, as it is on `Pattern`. A stage carrying `narrativeContexts` requires its orchestration to declare one, which crosses object boundaries and so is enforced by the validator rather than the schema.

#### 9.5.3 Reuse and Cycles

**A pattern may appear in several orchestrations**, and more than once within one. Reuse is the point: a release pattern belongs to more than one programme shape, and a sprint pattern may be nested in the phases of a milestone plan *and* run on demand when an unplanned increment is needed. The same holds for an embedded orchestration, which is reusable by more than one host by definition ([Section 9.5.4](#954-embedding-an-orchestration)). What must not repeat is the same target placed the same way twice — two stages naming the same pattern or orchestration with the same `relativeTo` are a duplicate, not a layer. This is the counterpart of [Section 9.3.7](#937-ungrouped-patterns), which limits a pattern to one group.

**Target and host are the identity of a stage.** A stage carries no `name` of its own, and `seq` is unique only among sequential stages, so what distinguishes one stage from another is the pair above and nothing else — including the `relationship`, which says how a stage is placed rather than which stage it is. The merge algorithm keys on the same pair, and [merge.md §6.15a](../merge.md#615a-patternorchestration-merging) states it normatively.

**A recurring phase is a stage whose pattern loops.** There is no separate "this stage repeats" property, because [Section 9.2a](#92a-cyclical-patterns-declaring-that-phases-repeat) already provides one: a stage naming a pattern that declares `loopsBackTo` is a recurring phase. Steady-state operation and cyclical change are exactly the phases that need it.

#### 9.5.4 Embedding an Orchestration

A stage names either a pattern or another orchestration. Naming an orchestration places that whole sub-endeavour at this point, under the same `relationship` vocabulary [Section 9.5.1](#951-how-a-stage-is-placed) already defines: a project's endeavour nested inside each tranche of a programme, an assurance endeavour running concurrent with delivery, a recovery endeavour entered on demand.

```json
{
  "name": "Programme Endeavour",
  "description": "A programme delivering benefits through successive tranches, each tranche running projects.",
  "stages": [
    { "patternName": "Tranche Plan", "seq": 1, "relationship": "sequential" },
    {
      "orchestrationName": "Project Endeavour",
      "seq": 1,
      "relationship": "nested",
      "relativeTo": { "patternName": "Tranche Plan" },
      "recurrence": "perView"
    }
  ]
}
```

The project endeavour belongs to the practice that authored it. The programme places it; it does not restate it, and a later change to the project's internal ordering reaches the programme without the programme being edited. Flattening the project's stages into the programme would copy an ordering the programme does not own, and the copy would go stale the first time the original moved.

**Both kinds of name resolve across scope** — the baseline chain, a declared dependency, or this document — in common with every other symbolic link in the language. A stage may therefore name a pattern another document owns. That is permitted, and the validator warns where the owning document has already placed that pattern in an orchestration of its own, because embedding that orchestration keeps the ordering with its author and stays correct when the author changes it. The warning is advice about which construct expresses the intent, not a restriction on what may be written.

**Embedding must not form a cycle.** An orchestration cannot embed itself, directly or through a chain, and the constraint is stated with the other acyclicity rules at [Section 14.1.8](acyclicity.md#1418-patternorchestration-embedding-hierarchy-orchestrationstageorchestrationname).

Two limits are worth naming because they are deliberate rather than overlooked. `relativeTo.viewNames` scopes a stage to named views of a host **pattern**; an orchestration host has stages rather than views, so the property does not apply to it, and a stage placed against part of a sub-endeavour is not currently expressible. `recurrence: perView` likewise restarts a stage for each view of a pattern host and means nothing against an orchestration.

#### 9.5.5 Baseline-Published Shells

A baseline may declare an orchestration with no stages. The shell publishes a name and the shape of an endeavour the domain recognises, and extension practices merge their stages into it — the mechanism canonical pattern groups used in [Section 9.3.1](#931-baseline-defined-canonical-groups), applied to a construct that carries sequencing rather than classification alone.

```json
{ "name": "Adoption Endeavour", "description": "The shape every adoption follows, from first contact to steady-state operation.", "stages": [] }
```

This does not reinstate the problem that retired grouping. A group's entries carried only order, so practices filling one competed over `seq` and the result was an ordering no author had written. A stage states its `relationship`, its host and its criteria, so a practice contributing to a shell says where its work sits and against what. The merged orchestration means something each contributor could have read before writing.

**Extension is additive.** A practice redeclaring an orchestration it inherits contributes stages that serve the shape the owner published. It does not renumber, re-place or redefine a stage it inherited: that stage's placement belongs to whoever wrote it, and the merge gives the original precedence over any overlay restating it. A sequential stage a practice adds appends after the inherited sequence rather than inserting into it, since an insertion renumbers the rest in everything but name.

**What a practice inherits is every declaration in scope, merged.** A shell carries no stages, so reading the shell alone says the sequence is empty and anything may be appended at position one. What the author actually inherits is the shell together with whatever the baseline chain and the declared dependencies have already contributed under that name, merged by the rule in `merge.md` §6.15a. An empty shell is the start of a name, not the start of an order.

The natural shapes for a contribution are the ones that disturb nothing — `concurrent` for a track running alongside inherited work, `nested` for one bounded by an inherited phase, `onDemand` for one entered on recognition. A practice reaching past these for a mid-sequence insertion usually wants a different endeavour rather than a quarrel about this one.

**Wanting to reorder is diagnostic.** An author who needs the inherited stages in a different order does not have an extension of the published shape; they have another shape, and the honest expression is a new orchestration whose description says what makes it different. Two orchestrations that each mean what their author wrote cost less than one shared name that no longer means what either intended. [Section 9.5.6](#956-choosing-the-level) covers the choice; `merge.md` §6.15a covers what the merge does with it.

#### 9.5.6 Choosing the Level

The construct offers four placements and two kinds of target, and most authoring mistakes are a choice between levels rather than a mistake within one. The question is always the same: is this thing part of the endeavour being described, or an endeavour of its own that this one reaches for?

**Levels are distinguished by who owns the decision and what completes, not by size.** Every hierarchy that has settled this question settles it the same way. The PMI *Standard for Program Management* and MSP separate a programme from a project by what each delivers — benefits against outputs — not by duration or headcount. SAFe separates portfolio, large solution, ART and team by the cadence each owns. BPMN separates a sub-process, drawn inside its parent, from a call activity that invokes a process defined and owned elsewhere. APQC's process classification separates its levels by the scope of the result. A large project is still a project; a two-week endeavour with its own owner and its own completion is still an endeavour.

**Embed or nest** is that question applied to a stage. Three checks, and embedding wants all three:

- Does the sub-endeavour have an owner other than this document?
- Does it complete on its own terms, rather than ending because the host's phase ended?
- Is it reused, or plausibly reusable, by a host other than this one?

Any no means a `nested` pattern stage. This is [Section 9.5.1](#951-how-a-stage-is-placed)'s concurrent-against-nested test one level up — *what happens to this when the host's phase ends?* — with ownership added, and it is BPMN's sub-process against its call activity.

**Extend, embed, or author new** is the question applied to the orchestration itself, when one already exists in scope. Take the first that fits:

| When | Route | Cost of getting it wrong |
|---|---|---|
| An orchestration in scope already describes this shape, and what you are adding serves the purpose its description states | Extend it by name, adding only your own stages | Low. The shape accumulates the tracks it always implied |
| Your patterns form a self-contained sub-endeavour of a shape in scope | Author your own and let it be embedded | Low. Both owners keep their ordering |
| Neither — nothing in scope describes this shape | Author a new one, and say in its description what makes it distinct | This is the right answer when it is the right answer, and the wrong one by default |

The failure that matters is the last row chosen without checking the first two: an orchestration per practice, each describing a shape two others already described, and no reader able to tell which is authoritative. The check costs a read of what is in scope. The alternative accumulates.

The opposite failure is quieter and worse. Extending a shared orchestration with stages that do not serve its stated purpose leaves a name whose description no longer describes it, and every later author inherits the confusion. Read the host's description before extending. If what you are adding would make it untrue, you are in the third row.

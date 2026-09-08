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

### 9.3 Pattern Groups: Organising Patterns for Navigation

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

**Objective Contributions** — compute percentage progress from pattern view completion. An ObjectiveContribution declares:
- Which pattern's views are used to measure progress (`patternName`)
- At which pattern view the outcome is fully achieved (`recognizedAtPatternViewName`)
- View-level weights for cumulative progress calculation (`forecastWeights`)

A consuming system checks which pattern views have been completed (all alpha state and work product objectives met for that phase), then applies the weight for the highest completed view.

#### Forecast Weights

Both contribution types use an analogous forecast weight pattern:

- **StateForecastWeight** maps alpha state names to probability weights (0–1). States not listed have implicit weight 0. The `recognizedAtStateName` should correspond to a weight of 1.0 in the forecast array.
- **ViewForecastWeight** maps pattern view names to cumulative progress weights (0–1). Views not listed have implicit weight 0. The `recognizedAtPatternViewName` should correspond to a weight of 1.0.

Forecast weights enable systems to compute weighted projections before full recognition — e.g., a sales pipeline that counts Committed opportunities at 80% and Best Case at 40%.

#### Authoring Guidance

- An outcome may have metric contributions, objective contributions, or both
- Use metric contributions when the outcome's progress is a numerical aggregate from external data (revenue, user counts, capacity)
- Use objective contributions when the outcome's progress maps to lifecycle phase completion (readiness, maturity, compliance)
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

#### Validation Rules

- `MetricContribution.alphaName` must match an Alpha.name in the practice or its dependencies
- `MetricContribution.workProductName`, when present, must match a WorkProduct.name in the practice or its dependencies
- `MetricContribution.recognizedAtStateName` must match a State.name within the named alpha
- `MetricContribution.forecastWeights[].stateName` must match a State.name within the named alpha
- `ObjectiveContribution.patternName` must match a Pattern.name in the practice or its dependencies
- `ObjectiveContribution.recognizedAtPatternViewName` must match a PatternView.name within the named pattern
- `ObjectiveContribution.forecastWeights[].patternViewName` must match a PatternView.name within the named pattern


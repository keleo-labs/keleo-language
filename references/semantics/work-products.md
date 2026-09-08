[< Back to Semantic Guidance Hub](../semantics.md)

## 7 Evidentiary Verification via Work Product Elements

A WorkProduct is the tangible artifact providing the empirical evidence necessary to validate Alpha state progressions. Work Products are the evidentiary artifacts of the practice. To ensure rigorous maturity tracking, a Work Product must explicitly define its progression through at least three Levels of Detail, aligning with progressive organizational adoption.

### 7.1 Structure of Work Products

Every WorkProduct is defined by a progression sequence of LevelOfDetail objects (minimum of 2). Each level dictates specific quality gates, and achieving a specific level directly contributes to advancing parent Alphas via an AlphaContribution.

**LevelOfDetail Naming and Content Maturity Progression:**

LOD names must describe the maturity or sophistication of the artifact's content — what the artifact contains at each level. They must not describe the abstract concern the artifact evidences (see [Section 4.6](composition.md#46-practice-partitioning-and-value-driven-scoping) for the full Alpha vs Work Product decision framework).

Well-designed LOD names answer the question: "What does this document look like at this level of maturity?" Use the five-level rubric defined in `references/workproduct-assessment-rubric.csv` as the primary lens for designing LOD progression:

- **Basic / Descriptive** (Rubric Level 1): The artifact exists in skeletal form — high-level lists, brief mentions, basic identification. Content is descriptive but lacks logical structure or analytical depth. Example LOD names: "Outlined", "Draft Reference", "Checklist", "Backlog", "Component List", "Parameter Log".
- **Defined / Logical** (Rubric Level 2): The artifact presents structured, logical content — documented frameworks, step-by-step guides, detailed specifications, logical mappings. Example LOD names: "Detailed", "Defined", "Comprehensive Reference", "Prioritized Plan", "Scored Risk Matrix", "Modular".
- **Applied / Behavioural** (Rubric Level 3): The artifact includes worked examples, scenario-based guidance, and behavioural context that demonstrates application to specific situations. Example LOD names: "Validated", "Scenario-Based", "Tested Templates", "Applied", "Performance-Validated".
- **Comprehensive / Automated** (Rubric Level 4): The artifact incorporates automation, interactive tooling, or executable components that reduce manual effort. Example LOD names: "Automated", "Interactive", "Self-Service Platform", "Predictive Analytics Platform", "Adaptive Governance".

**LOD Naming Principles:**

1. **Content-descriptive, not concern-descriptive**: "Quantitative Health Profile" describes what the document contains. "Optimized" would describe the concern's health — wrong for an LOD name.
2. **Domain-appropriate vocabulary**: "Observational Checklist" (horticulture), "Operator Configuration" (infrastructure), "Informal Guidelines" (governance) each use terms natural to the artifact's domain.
3. **No generic numbered labels**: Use meaningful names, never "Level 1", "Level 2", or "LOD 1". The schema requires a descriptive name string, not a number prefix.
4. **Progressive sophistication**: Each LOD name should convey greater content depth, analytical rigour, or automation than the previous level.

**The Purpose Hub: `contributesToAlphaNames`:**

The `contributesToAlphaNames` property declares at the work product level which alphas this artifact exists to serve. It is the "purpose hub" — the single place consuming systems look to understand why this work product exists.

- **Type**: array of `Alpha.name` symbolic links
- **Optional in schema**: existing work products without this property remain valid
- **Validator enforcement**: if `contributesToAlphaNames` is absent or empty AND no LOD on the work product has a non-empty `contributesTo`, the work product is floating (validation error)
- **Superset rule**: every `alphaName` appearing in any LOD's `contributesTo` array must also appear in `contributesToAlphaNames` (when the WP-level array is present). The WP-level array is the union; individual LODs provide finer-grained state linkage
- **Migration**: stamp from `union(levelsOfDetail[].contributesTo[].alphaName)` for existing work products
- **Authoring guidance**: authors should always fill this property. Consuming systems (e.g., keleo-userskillz) use it as the primary purpose indicator for grouping next-steps and rendering work product context

```json
{
  "name": "Architecture",
  "description": "Technical blueprint detailing platform infrastructure.",
  "contributesToAlphaNames": ["Platform"],
  "levelsOfDetail": [
    {
      "name": "Outlined", "seq": 1,
      "checklist": [],
      "contributesTo": [{"alphaName": "Platform", "stateName": "Architecture Selected"}]
    },
    {
      "name": "Detailed", "seq": 2,
      "checklist": [],
      "contributesTo": [{"alphaName": "Platform", "stateName": "Provisioned"}]
    }
  ]
}
```

**Structural Requirements:**

- Each LevelOfDetail MAY include a `contributesTo` array of AlphaContribution objects (`{alphaName, stateName}`) linking this maturity level to the alpha state(s) it advances (see [Section 4.6](composition.md#46-practice-partitioning-and-value-driven-scoping) for the semantic rationale). `contributesTo` is optional on individual LODs — not every level needs to name a specific state. However, at least one LOD on the work product must have a non-empty `contributesTo`, OR the work product must have a non-empty `contributesToAlphaNames`. This ensures no work product floats without a purpose in the alpha graph.
- Each LevelOfDetail MUST include a `checklist` array (may be empty) defining quality gates for achieving that level
- LOD checklists describe positive characteristics the artifact must exhibit at this maturity level, not steps to create it and not the absence of characteristics. Each item is an achievement to reach, not a deficiency to observe
- The `seq` integer determines ordering; lower LODs represent less mature content

### 7.2 Artifact Instantiation and Concurrency

The evidenceRequired property dictates the ingestion of a URI linking the logical JSON object to physical reality. Because enterprise execution is inherently parallelized, implementations must support branching metadata to allow tracking of experimental drafts without corrupting canonical Alpha calculations.

### **7.3 Work Product Instance Semantics: Guidance vs Evidence Chains**

The Practice Language uses two distinct object types for work product instance management, mirroring the alpha instance design ([Section 6.5](alphas.md#65-alpha-instance-semantics-declaration-vs-execution-tracking)). As with alpha instances, their purpose shifts depending on context: in practices they provide guidance about expected deliverables; in projects they identify and track specific artifacts.

**WorkProductInstanceName**

The WorkProductInstanceName object declares and describes an instance of a work product. These objects reside in the workProductInstances array of a Practice, Method, or Project.

Structure:

- instanceName: Unique identifier for this variant (e.g., "Security Requirements", "Platform Architecture")
- description: Brief explanation of what this variant represents
- workProductName: References the baseline or practice-defined work product being instantiated
- links: Optional array of ExternalLink objects pointing to the primary document(s) used to track this work product (e.g., a shared document, repository, or wiki page)
- relatesTo: Optional array of InstanceRelationship objects associating this instance with other concern or work-product instances (system of record; see [Section 6.7](alphas.md#67-instance-relationships-applying-type-edges-to-named-instances))
- narratives: Optional contextual storytelling for this instance
- tags: Optional classification metadata

In a **Practice or Method**, WorkProductInstanceName objects illustrate the kinds of deliverable variants that adopters should expect to produce. A practice might declare "Platform Architecture" and "Network Architecture" as instances of a baseline "Architecture" work product to show that the abstract concept decomposes into distinct artifacts addressing different architectural concerns.

In a **Project**, WorkProductInstanceName objects identify the specific, concrete artifacts being tracked in this execution context. The optional links array connects each instance to the external systems where the artifact is actually maintained.

**WorkProductInstance**

The WorkProductInstance object records a specific artifact's maturity level. These objects appear in evidence arrays (AlphaInstance.evidenceBy, AlphaContribution.evidenceBy) and in Project current/target/cycles sections, linking abstract progression to concrete deliverables.

Structure:

- instanceName: Identifier for the specific artifact (may or may not match a declared WorkProductInstanceName)
- workProductName: The baseline or practice work product this represents
- levelOfDetailName: The target maturity level this artifact has achieved
- relatesTo: Optional array of InstanceRelationship objects (may mirror WorkProductInstanceName.relatesTo)
- links: Optional array of ExternalLink objects pointing to documents specific to this level of detail. Typically omitted when the parent WorkProductInstanceName links apply; use only when this particular maturity level is tracked in a different document

In a **Practice**, WorkProductInstance objects within evidence arrays illustrate what artifacts at what maturity levels would prove state achievement — showing adopters the expected evidence chain.

In a **Project**, WorkProductInstance objects record the assessed or desired maturity of each tracked artifact, answering "what artifact at what maturity level proves this progression?" The levelOfDetailName indicates how comprehensive or mature the artifact is, directly mapping to the work product's defined levels of detail.

**Comparison Table**


| Aspect          | WorkProductInstanceName                                    | WorkProductInstance                                              |
| --------------- | ---------------------------------------------------------- | ---------------------------------------------------------------- |
| Purpose         | Declare and describe instances (guidance or identification) | Record maturity level (illustrative or assessed)                 |
| Location        | Practice/Method/Project workProductInstances                | evidenceBy arrays, Project current/target                        |
| Required Fields | instanceName, workProductName                              | instanceName, workProductName, levelOfDetailName                 |
| Optional Fields | description, narratives, tags, links, relatesTo            | links, relatesTo                                                 |
| In Practices    | Guidance — illustrates expected deliverable variants        | Illustrative — shows what evidence proves state achievement      |
| In Projects     | Identification — names the specific artifacts being tracked | Tracking — records current or target maturity with evidence      |
| Validation      | instanceName must be unique within context                  | workProductName must match defined work product                  |


**Usage in Evidence Chains**

WorkProductInstance objects form the foundation of the Practice Language's evidence-based progression model:

1. **Alpha State Evidence**: An AlphaContribution declares that achieving a work product at a specific level of detail enables an alpha to reach a particular state
2. **Instance Evidence**: An AlphaInstance's evidenceBy array lists which specific work product instances (at which maturity levels) prove the instance has achieved its target state
3. **Validation**: Operational tooling verifies that evidence chains are complete — every claimed state has corresponding work product evidence at appropriate maturity levels

**Example**

Practice declares architecture variants:

```json
{
  "workProductInstances": [
    {
      "instanceName": "Platform Architecture",
      "workProductName": "Architecture",
      "description": "Core platform technical architecture and design",
      "links": [
        {
          "name": "Architecture Document",
          "description": "Living architecture decision record for the platform",
          "uri": "https://wiki.example.com/platform/architecture"
        }
      ]
    },
    {
      "instanceName": "Security Architecture",
      "workProductName": "Architecture", 
      "description": "Security controls and compliance architecture"
    }
  ]
}
```

Evidence chain proving alpha state:

```json
{
  "instanceName": "Core Platform",
  "alphaName": "Platform",
  "stateName": "Baselined",
  "evidenceBy": [
    {
      "instanceName": "Platform Architecture",
      "workProductName": "Architecture",
      "levelOfDetailName": "Comprehensive"
    },
    {
      "instanceName": "Platform Requirements",
      "workProductName": "Requirements",
      "levelOfDetailName": "Defined"
    }
  ]
}
```

This design serves both guidance and execution: practices use work product instances to illustrate the kinds of deliverables adopters will produce and how they evidence progression, while projects use the same structures to identify and track the specific artifacts being managed at measurable maturity levels.

### 7.4 Work Product Instance Metrics

Work product instances serve as proxies for external documents. The optional `metrics` array on WorkProductInstance brings quantitative data from those external documents into the project JSON as structured, named values.

**Purpose**

Metrics capture specific numerical data points extracted from external systems — deal values from a CRM, user counts from analytics, financial figures from reports. They provide the raw data that outcome metric contributions aggregate into project-level value measurements.

**Structure**

Each Metric has:
- `name` — identifier matching the `metricName` declared in a MetricContribution (e.g., "acv", "users", "capacity")
- `value` — numeric value
- `unit` — optional unit of measurement (e.g., "GBP", "USD", "hours")

**Relationship to Outcomes**

Metrics on work product instances feed into the outcome measurement chain:

1. A practice-level Outcome declares MetricContributions specifying which alpha's evidence chain to follow and which metric name to aggregate
2. A project's alpha instances reference work product instances via `evidenceBy`
3. Those work product instances carry `metrics` with the named values
4. A consuming system follows the chain: Outcome → MetricContribution → alpha instances (state determines weight) → evidenceBy → work product instances → metrics (provides the value)

**Example**

A CRM opportunity record tracked as a work product instance:

```json
{
  "instanceName": "SFDC: AI Platform Deal",
  "workProductName": "Opportunity Record",
  "levelOfDetailName": "Qualified",
  "metrics": [
    { "name": "acv", "value": 500000, "unit": "GBP" },
    { "name": "arr", "value": 600000, "unit": "GBP" }
  ]
}
```

**Declared metrics on the WorkProduct template**

A WorkProduct may declare `expectedMetrics` — `{name, description, unit?}` templates for the quantitative fields its instances may carry. Practices use this so authors and collecting systems know which metric names belong on instances of that artifact (e.g. an Initiative Card carries `acv`). Outcome `MetricContribution.metricName` values should match an expected metric on the work product that supplies the value.

**Authoring Guidance**

- Metric names should be short, lowercase identifiers that match the `metricName` in practice-level MetricContributions
- Declare `expectedMetrics` on the WorkProduct that is the source of truth for each metric; do not leave metric names only on Outcome contributions
- Not all work product instances need metrics — only those that contribute quantitative data to outcomes
- Units should be consistent across all instances contributing to the same outcome
- Metrics are point-in-time values; update them as external documents change
- Store the canonical metric on `current.workProductInstances`. `evidenceBy` snapshots on alpha instances may omit `metrics`; consuming systems join by instance name.

### 7.5 Work Product Composition (`partOf`)

Work products can declare a `partOf` relationship to indicate that one work product is logically contained within another. The relationship is unidirectional: the child declares which parent it belongs to. There is no reciprocal `composedOf` array on the parent — tooling can compute the inverse at runtime.

**When to Use `partOf`**

Use `partOf` when a work product represents a distinct, independently trackable artifact that is logically a component or section of a larger deliverable. Both parent and child retain their own levels of detail and progress independently through them.

Examples:
- "Done Criteria" partOf "Definition of Done Specification" — the criteria are a trackable artifact contained within the broader specification
- "API Contract" partOf "Architecture" — the API contract is a concrete deliverable within the overall architecture documentation
- "Migration Runbook" partOf "Migration Plan" — the runbook is an operational component of the plan

**When NOT to Use `partOf`**

- When the "part" is just a section of a document that does not warrant independent tracking — use LOD checklists instead
- When the relationship is "contributes evidence to" rather than "is contained in" — use `contributesTo` on LevelOfDetail to connect work products to alpha states
- When work products are related but not in a containment relationship — use narratives to document the association

**Structural Rules**

- `partOf` is optional (0..1) — a work product may have at most one parent
- The value is a symbolic link: it must exactly match a `WorkProduct.name` in the same practice, a dependency practice, or the baseline
- Self-references are invalid: a work product cannot be `partOf` itself
- Circular chains are invalid: if A partOf B, then B must not directly or transitively declare partOf A. See [Section 14 — Acyclicity Constraints and Circular Reference Protection](acyclicity.md#14-acyclicity-constraints-and-circular-reference-protection) for the comprehensive acyclicity rules and implementation requirements.
- Keep hierarchies shallow — one level of containment is typical

**Contrast with Alpha `contributesTo`**

Alpha `contributesTo` models specialization: a sub-concern contributing to the health of a parent concern (abstract progress rollup). WorkProduct `partOf` models composition: a sub-artifact physically contained within a parent artifact (tangible containment). The semantic distinction matters: `contributesTo` aggregates state progression; `partOf` declares structural nesting of deliverables.

**`components` — Merge-Populated Inverse of `partOf`:**

The `components` property on a WorkProduct is an array of full `WorkProduct` objects (the same pattern as `variants`). It provides a pre-computed inverse of the `partOf` relationship: for a given parent work product, `components` contains all work products that declare `partOf` this parent. This enables containment rendering without requiring consumers to scan the entire work product graph.

- **Populated during merge** (see [`merge.md`](../merge.md)): after all extension layers merge, the merge algorithm collects every work product whose `partOf` names a given parent and embeds the full WorkProduct object in that parent's `components` array
- **Do not set in source practice authoring**: authors declare `partOf` on child work products; `components` is computed, not authored
- **Rendering**: UIs use `components` to display containment hierarchies and nested artifact structures

**Merge Behavior**

During practice composition ([Section 4.2](composition.md#42-practice-and-method-composition-merge)), `partOf` merges as a scalar field: the first non-empty value (from the kernel or earliest overlay) wins. After all extension layers merge, work products with `partOf` are aggregated into the target work product's `components` array.

**Example**

```json
{
  "workProducts": [
    {
      "name": "Definition of Done Specification",
      "description": "Comprehensive specification defining the quality standard that every Increment must satisfy before release.",
      "levelsOfDetail": [
        { "name": "Drafted", "seq": 1, "description": "Initial criteria captured.", "checklist": [], "contributesTo": [{"alphaName": "Definition of Done", "stateName": "Identified"}] },
        { "name": "Agreed", "seq": 2, "description": "Criteria reviewed and accepted by the team.", "checklist": [], "contributesTo": [{"alphaName": "Definition of Done", "stateName": "Established"}] }
      ]
    },
    {
      "name": "Done Criteria",
      "description": "Specific testable criteria that must be satisfied for an Increment to be considered done.",
      "partOf": "Definition of Done Specification",
      "levelsOfDetail": [
        { "name": "Listed", "seq": 1, "description": "Criteria enumerated as a checklist.", "checklist": [], "contributesTo": [{"alphaName": "Definition of Done", "stateName": "Identified"}] },
        { "name": "Measurable", "seq": 2, "description": "Each criterion has objective acceptance tests.", "checklist": [], "contributesTo": [{"alphaName": "Definition of Done", "stateName": "Established"}] }
      ]
    }
  ]
}
```

### 7.6 Work Product Variant Mapping (`mapsTo`)

Work products can declare a `mapsTo` relationship to indicate that one work product is a specialized variant of another. This mirrors the `mapsTo` relationship on Alphas ([Section 4.4](composition.md#44-redeclaration-vs-specialization-decision-framework)) — the variant IS-A type of the parent work product, following the same levels of detail with domain-specific checklists.

**When to Use `mapsTo`**

Use `mapsTo` when a work product represents a distinct named variant of a parent work product that follows the same LOD progression. The variant has its own name, description, and checklists but shares the same levels of detail as its parent.

Examples:
- "Cloud Architecture" mapsTo "Architecture" — the cloud architecture is a specialized variant with the same maturity levels (Outlined → Detailed → Validated) but cloud-specific checklists
- "Security Assessment Report" mapsTo "Assessment Report" — same LOD progression with security-specific verification criteria
- "Platform Onboarding Guide" mapsTo "Onboarding Guide" — same content maturity levels with platform-specific content

**When NOT to Use `mapsTo`**

- When the work product is logically contained within a larger work product — use `partOf` instead
- When the work product needs different levels of detail from the parent — `mapsTo` requires identical LOD names and sequences
- When the relationship is "contributes evidence to" rather than "is a variant of" — use `contributesTo` on LevelOfDetail to connect work products to alpha states

**Structural Rules**

- `mapsTo` is optional (0..1) — a work product may map to at most one parent
- `mapsTo` and `partOf` are **mutually exclusive** — a work product cannot be both a component of and a variant of another work product
- The value is a symbolic link: it must exactly match a `WorkProduct.name` in the same practice, a dependency practice, or the baseline
- Self-references are invalid: a work product cannot `mapsTo` itself
- Circular chains are invalid: if A mapsTo B, then B must not directly or transitively declare mapsTo or partOf A. See [Section 14 — Acyclicity Constraints and Circular Reference Protection](acyclicity.md#14-acyclicity-constraints-and-circular-reference-protection) for the comprehensive acyclicity rules and implementation requirements
- Levels of detail MUST match the target work product exactly (same LOD names and sequences). The variant CAN have a different name, description, and checklists.

**Contrast with `partOf`**

- **`partOf`** models **containment**: a sub-artifact physically contained within a parent artifact (e.g., "API Contract" partOf "Architecture")
- **`mapsTo`** models **variant equivalence**: a specialized version of the same artifact type (e.g., "Cloud Architecture" mapsTo "Architecture")

The semantic distinction matters: `partOf` declares structural nesting of deliverables; `mapsTo` declares that the variant IS the parent artifact, viewed through a domain-specific lens. On merge, `mapsTo` work products are embedded in the parent's `variants` array ([Section 4.2](composition.md#42-practice-and-method-composition-merge)), enabling UIs to present them as related types.

**Merge Behavior**

During practice composition ([Section 4.2](composition.md#42-practice-and-method-composition-merge)), `mapsTo` merges as a scalar field: the first non-empty value wins. After all extension layers merge, work products with `mapsTo` are aggregated into the target work product's `variants` array (see [merge.md Section 7.2b](../merge.md#72b-work-product-variant-aggregation)).

**Example**

```json
{
  "workProducts": [
    {
      "name": "Architecture",
      "description": "Technical blueprint detailing platform infrastructure, capability domains, and integration patterns.",
      "levelsOfDetail": [
        { "name": "Outlined", "seq": 1, "description": "High-level block diagram.", "checklist": [], "contributesTo": [{"alphaName": "Platform", "stateName": "Architecture Selected"}] },
        { "name": "Detailed", "seq": 2, "description": "Comprehensive documentation.", "checklist": [], "contributesTo": [{"alphaName": "Platform", "stateName": "Provisioned"}] },
        { "name": "Validated", "seq": 3, "description": "Production-proven architecture.", "checklist": [], "contributesTo": [{"alphaName": "Platform", "stateName": "Hosting Assets"}] }
      ]
    },
    {
      "name": "Cloud Architecture",
      "description": "Cloud-specific architecture variant documenting cloud provider selection, multi-region strategy, and cloud-native design patterns.",
      "mapsTo": "Architecture",
      "levelsOfDetail": [
        { "name": "Outlined", "seq": 1, "description": "High-level block diagram.", "checklist": [
          { "seq": 1, "name": "Cloud provider selected", "description": "Target cloud platform identified and approved" }
        ], "contributesTo": [{"alphaName": "Platform", "stateName": "Architecture Selected"}] },
        { "name": "Detailed", "seq": 2, "description": "Comprehensive documentation.", "checklist": [
          { "seq": 1, "name": "Multi-region strategy documented", "description": "Geographic distribution and failover approach defined" }
        ], "contributesTo": [{"alphaName": "Platform", "stateName": "Provisioned"}] },
        { "name": "Validated", "seq": 3, "description": "Production-proven architecture.", "checklist": [
          { "seq": 1, "name": "Cloud scaling validated", "description": "Auto-scaling behaviour confirmed under production load" }
        ], "contributesTo": [{"alphaName": "Platform", "stateName": "Hosting Assets"}] }
      ]
    }
  ]
}
```

**Reasoning**: Cloud Architecture IS an Architecture — it follows the same maturity levels (Outlined → Detailed → Validated) with cloud-specific checklists. Using `mapsTo` rather than `partOf` because: (a) it has the same LOD progression as its parent, (b) it is a distinct named variant, not a sub-component contained within the parent, and (c) on merge it should appear within the Architecture work product's `variants` array for UI rendering.


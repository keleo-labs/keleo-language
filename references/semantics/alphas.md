[< Back to Semantic Guidance Hub](../semantics.md)

## 6 The Alpha-State Trajectory and Dynamic Semantics

The Alpha (Abstract-Level Progress Health Attribute) defines the essential elements of an endeavor requiring tracking and progression.

### 6.1 Defining Core Alphas and Baseline Isolation

Every Alpha contains a mandatory array of states (minimum of 3) and is categorized under a focusName. The operational guidance emphasizes the strict separation of the conceptual entity from its documentation. A "Requirements" Alpha represents actual stakeholder needs, not the requirements document itself.

#### **Baseline Isolation Rules: The Floating Alpha Prohibition**

**THE CRITICAL RULE: NO FLOATING ALPHAS**

When extending a baseline practice, all new alphas introduced in a practice extension MUST explicitly declare at least one of `contributesTo` or `mapsTo` pointing to a valid alpha. This is not a guideline—it is an absolute constraint enforced during Phase 2 validation. Alphas that lack both relationships are known as "floating alphas" and are strictly prohibited by the Practice Language semantics. An alpha may declare both properties simultaneously (e.g., it maps to one alpha as a variant and contributes to another as a sub-concern), but the targets must be different alphas. Use `contributesTo` for specialization (sub-concern with distinct state progression) and `mapsTo` for variant mapping (IS-A variant with identical state progression).

**Why This Rule Exists:**

- **Ensures Composability**: Practices can be combined and reused because all elements trace back to a common ontology
- **Maintains Ontological Coherence**: Every practice-specific concept maps to a broader framework, preventing semantic fragmentation
- **Enables Hierarchical Rollups**: Child alpha states can influence parent alpha progression calculations through the contributesTo relationship, or declare state equivalence through the mapsTo relationship
- **Supports Validation**: Tooling can verify that practice extensions enhance rather than diverge from the baseline architecture
- **Prevents Semantic Drift**: Organizations maintain consistency across multiple practices when all concepts anchor to shared alphas

**Valid contributesTo / mapsTo Targets:**

Both `contributesTo` and `mapsTo` can reference three types of alphas:

1. **Baseline Practice Alphas** (most common): Reference alphas defined in the baselinePractice
   - Example: `"contributesTo": "Platform"` (where "Platform" is a baseline alpha)
   - Use when: Specializing or contributing to a universally applicable concept

2. **Practice-Local Alphas** (creates internal hierarchy): Reference other new alphas defined within the same practice
   - Example: Alpha "Platform Service" → `"contributesTo": "Platform Capability"` (where "Platform Capability" is another new alpha in this practice)
   - Use when: Building multi-level specialization hierarchies within a practice
   - **CRITICAL**: The referenced alpha must be defined in the SAME practice and must itself have a valid contributesTo chain to baseline

3. **External Practice Alphas** (creates practice dependency): Reference alphas from another practice
   - Example: `"contributesTo": "Team Interaction"` (where "Team Interaction" is defined in the "Team Topologies" practice)
   - Use when: The practice depends on concepts from another practice
   - **CRITICAL**: This creates an explicit practice dependency that must be declared in the practice's `dependencies` array
   - The external practice name must be specified, and that practice must be available for validation

**Common contributesTo Mapping Patterns:**

While specific alpha names vary by baselinePractice, typical baseline patterns include:

- Technology/infrastructure concepts typically contribute to platform-related alphas in the baseline
- Content/artifact types typically contribute to asset or artifact-related alphas
- Process/workflow types typically contribute to work or process-related alphas
- Governance mechanisms typically contribute to governance-related alphas
- Risk/compliance frameworks typically contribute to risk-related alphas
- Value/economic models typically contribute to value-related alphas
- Team structures typically contribute to team or organizational alphas
- Stakeholder types typically contribute to stakeholder-related alphas
- Requirements types typically contribute to requirements-related alphas

**Validation Rules:**

1. **Baseline References**: The `contributesTo` or `mapsTo` value must be an exact, case-sensitive string match to a baseline alpha name
2. **Practice-Local References**: The value must reference another alpha defined in the SAME practice, and that alpha must have its own valid `contributesTo` or `mapsTo` chain
3. **External Practice References**: The value must reference an alpha from a practice declared in the `dependencies` array, and that practice must be available for resolution
4. **Distinct Targets**: When both `contributesTo` and `mapsTo` are present, they MUST reference different alphas
5. **State Matching for mapsTo**: A `mapsTo` alpha MUST have identical state names and sequences as its target alpha. It CAN have a different name, description, and checklists.

**No Circular Dependencies**: Alpha A cannot contribute to Alpha B if Alpha B (or any alpha in B's `contributesTo`/`mapsTo` chain) contributes/maps to Alpha A. See [Section 14 — Acyclicity Constraints and Circular Reference Protection](acyclicity.md#14-acyclicity-constraints-and-circular-reference-protection) for the comprehensive acyclicity rules and implementation requirements.

#### **Semantic Relationships: The relatesTo Property**

Beyond specialization (`contributesTo`) and variant mapping (`mapsTo`), alphas can declare rich semantic relationships via the optional `relatesTo` array. This property enables the Practice Language to capture domain-specific dependencies, influences, constraints, and other interactions between alphas that are not hierarchical in nature.

**AlphaRelationship Structure:**

```json
{
  "relationship": "string",
  "alphaName": "string",
  "direction": "outgoing | incoming | mutual",
  "relationshipKind": "string (optional enum)",
  "description": "string (optional)"
}
```

**Field Definitions:**

- **relationship**: The type of relationship expressed as a domain-appropriate verb (e.g., "depends on", "influences", "constrains", "validates", "precedes", "enables", "provides", "guides", "evidences", "funds", "impacts", "justifies", "demonstrates ROI for"). This is the human-readable label; tooling should not parse this string programmatically.
- **alphaName**: Name of the related alpha in the same baseline (symbolic link; must match Alpha.name exactly)
- **direction**: Explicit directionality enabling programmatic traversal without semantic interpretation of the relationship verb:
  - `outgoing` — this alpha acts upon the target (e.g., A "depends on" B, A "constrains" B)
  - `incoming` — the target acts upon this alpha (e.g., A "is governed by" B, A "is supported by" B)
  - `mutual` — symmetric relationship in both directions (e.g., A "correlates with" B)
- **relationshipKind** (optional): Machine-traversable classification from a closed enum. The `relationship` property remains the human-readable domain verb; `relationshipKind` provides a stable, parseable category for programmatic traversal without verb NLP. When absent, tooling falls back to `direction`-based traversal only. Values:
  - `dependency` — this alpha requires the target's output, state, or existence (maps to: "depends on", "requires", "validated by", "evidenced by")
  - `production` — this alpha creates, builds, or delivers the target (maps to: "produces", "delivers", "creates", "built by", "performed by")
  - `guidance` — this alpha guides, drives, constrains, or governs the target (maps to: "guides", "drives", "directs", "constrains", "governs", "enforces policies on", "governed by")
  - `information-flow` — this alpha provides information, feedback, or value to the target (maps to: "provides", "communicates value to", "provides feedback to")
  - `enabling` — this alpha enables, facilitates, or supports the target (maps to: "enables", "facilitates", "supports", "enables access to", "exposes")
  - `impact` — this alpha influences or impacts the target without direct control (maps to: "influences", "impacts", "justifies", "demonstrates ROI for")
  - `consumption` — this alpha consumes, hosts, or runs on the target (maps to: "consumes", "hosts", "runs on", "realizes")
  - `mutual` — symmetric relationship without a dominant direction (maps to: "correlates with", "interacts with")
- **description** (optional): Human-readable explanation of the relationship — why it exists and what it means in this domain context

**Purpose and Use Cases:**

The `relatesTo` property captures non-hierarchical relationships that `contributesTo` cannot express:

- **Dependency Relationships**: "Requirements" depends on "Stakeholders" (information flow)
- **Production Relationships**: "Work" produces "Platform" (creation)
- **Governance Relationships**: "Platform Governance" constrains "Platform" (control)
- **Validation Relationships**: "Platform Consumption Interface" validates "Requirements" (proof)
- **Influence Relationships**: "Platform Risk And Compliance" influences "Requirements" (indirect impact)
- **Enabling Relationships**: "Organizational Change" enables "Team" (capability provision)

**Relationship Type Patterns:**

The Practice Language uses domain-appropriate relationship verbs organized by pattern. The `direction` value indicates how the relationship reads from the declaring alpha's perspective:

1. **Dependency Patterns**
   - "depends on", "requires" — `outgoing` (this alpha depends on the target)
   - "validated by", "evidenced by" — `incoming` (the target validates this alpha)

2. **Creation/Production Patterns**
   - "produces", "delivers", "creates" — `outgoing` (this alpha produces the target)
   - "built by", "performed by" — `incoming` (the target builds this alpha)

3. **Guidance/Control Patterns**
   - "guides", "drives", "directs" — `outgoing` (this alpha guides the target)
   - "constrains", "governs", "enforces policies on" — `outgoing` (this alpha constrains the target)
   - "governed by" — `incoming` (the target governs this alpha)

4. **Information Flow Patterns**
   - "provides", "communicates value to" — `outgoing` (this alpha provides to the target)
   - "provides feedback to" — `outgoing`

5. **Enabling Patterns**
   - "enables", "facilitates", "supports" — `outgoing` (this alpha enables the target)
   - "enables access to", "exposes" — `outgoing`

6. **Impact Patterns**
   - "influences", "impacts" — `outgoing` (this alpha influences the target)
   - "justifies", "demonstrates ROI for" — `outgoing`

7. **Consumption Patterns**
   - "consumes", "hosts", "runs on" — `outgoing` (this alpha consumes/hosts the target)
   - "realizes" — `outgoing`

8. **Mutual Patterns**
   - "correlates with", "interacts with" — `mutual` (symmetric relationship)

**Validation Rules:**

- The `relatesTo` array is optional (can be empty or omitted)
- Every `alphaName` in a relationship must reference a valid alpha in the same baseline or practice
- Relationship strings should use domain-appropriate verbs (no formal validation of relationship types)
- Every relationship must declare a `direction` (`outgoing`, `incoming`, or `mutual`)
- The `direction` must be consistent with the relationship verb — e.g., "depends on" should be `outgoing` (this alpha depends on the target), not `incoming`
- `relationshipKind`, when present, must be one of the defined enum values and should be consistent with the `relationship` verb and the relationship type pattern it falls under

#### Example: Platform Adoption Kernel Relationships

```json
{
  "name": "Platform",
  "description": "The unified system of infrastructure, compute resources, networking, storage, and foundational services",
  "focusName": "Solution",
  "relatesTo": [
    {
      "relationship": "built by",
      "alphaName": "Team",
      "direction": "incoming",
      "relationshipKind": "production",
      "description": "The platform is constructed and maintained by the team responsible for its delivery."
    },
    {
      "relationship": "hosts",
      "alphaName": "Platform Asset",
      "direction": "outgoing",
      "relationshipKind": "consumption",
      "description": "The platform hosts individual platform assets such as services, tools, and infrastructure components."
    },
    {
      "relationship": "exposes",
      "alphaName": "Platform Consumption Interface",
      "direction": "outgoing",
      "relationshipKind": "enabling"
    },
    {
      "relationship": "governed by",
      "alphaName": "Platform Governance",
      "direction": "incoming",
      "relationshipKind": "guidance"
    }
  ],
  "states": [...]
}
```

**Contrast with contributesTo:**

- **contributesTo**: Creates parent-child hierarchical relationships for specialization (e.g., "Platform Capability" contributes to "Platform")
- **relatesTo**: Captures peer-level or cross-cutting relationships without hierarchy (e.g., "Platform" is "governed by" "Platform Governance")

**Phase 2 Translation Requirements:**

- Identify domain-specific relationships in source material
- Use relationship verbs that match the semantic intent (avoid generic "relates to")
- Validate that all referenced alphas exist in the baseline or practice
- Document relationship rationale in Phase 1 analysis when non-obvious
- Empty `relatesTo` arrays are valid (not all alphas have semantic relationships beyond contributesTo)

**Tooling and Visualization:**

The `relatesTo` property enables advanced capabilities:

- **Dependency Analysis**: "What alphas does Platform depend on?" → filter relatesTo for `outgoing` dependency relationships, or use `relationshipKind: "dependency"` for precise filtering
- **Impact Analysis**: "What alphas are affected if Requirements change?" → find all alphas with `incoming` relationships referencing Requirements
- **Knowledge Graphs**: Each relationship becomes a directed semantic triple (`<Alpha> relationship <Alpha>`) for graph databases, with `direction` determining edge orientation and `relationshipKind` providing categorical grouping
- **Workflow Automation**: "guides" and "produces" relationships (or `relationshipKind: "guidance"` / `"production"`) inform activity sequencing
- **Progress Tracking**: "evidenced by" relationships link abstract progress to concrete artifacts

**Common Mistakes:**

- Using `relatesTo` for specialization (use `contributesTo` instead)
- Setting `direction` inconsistently with the relationship verb (e.g., "depends on" with `incoming` — the verb implies `outgoing`)
- Using vague relationship types like "related to" instead of specific verbs
- Referencing alphas from external practices without declaring practice dependencies
- Conflating relationships with narrative context (relationships are structural, narratives are explanatory)

This dual-relationship model—`contributesTo` for hierarchy and `relatesTo` for semantics—provides both ontological coherence (all concepts anchor to baseline) and rich domain expressiveness (practices can model complex alpha interactions).

Type-level `relatesTo` names **which kinds of concerns interact**. Instance-level `relatesTo` ([Section 6.7](#67-instance-relationships-applying-type-edges-to-named-instances)) records **which tracked occurrences** of those concerns — and of related work products — are linked in a project or example.

**Invalid vs Valid Pattern Examples:**

**INVALID Example (Floating Alpha):**

```json
{
  "name": "Security Framework",
  "description": "Security policies and controls maturity",
  "focusName": "Solution",
  "states": [...]
}
```

This alpha lacks a contributesTo property and therefore cannot be validated against the baseline. It is a floating alpha and will be rejected during validation.

**VALID Example (Properly Anchored):**

```json
{
  "name": "Security Framework",
  "description": "Security policies and controls maturity",
  "focusName": "Solution",
  "contributesTo": "Platform Governance",
  "states": [...]
}
```

This alpha explicitly contributes to a governance-related baseline alpha, establishing its place in the ontology and enabling hierarchical progression tracking.

**Enforcement:** Phase 2 JSON translation validates that every new alpha (not a redeclaration of a baseline alpha) contains a contributesTo property with a value matching a valid baseline alpha name. Practices that introduce floating alphas will fail validation and require remediation before acceptance.

### 6.2 State Progression and the Guidance Function

A State is a discrete point of maturity governed by a sequence integer (seq) and validated through associated checklist items. The transition trigger programmatically evaluates the state of prerequisite Alphas before allowing progression, transforming the schema into a prescriptive engine that generates dynamic "to-do" lists of required Activities.

#### State-Level Contribution Mapping (`contributesToState`)

When an Alpha declares `contributesTo` or `mapsTo` (naming a parent alpha it specializes or maps to), its individual states can optionally declare which state on the parent alpha they correspond to via the `contributesToState` property. This makes state-level mapping a first-class concept within baselines and practices.

```json
{
  "name": "Platform Capability",
  "contributesTo": "Platform",
  "states": [
    { "name": "Identified", "seq": 1, "contributesToState": "Recognized", "checklist": [...] },
    { "name": "Available", "seq": 2, "contributesToState": "Provisioned", "checklist": [...] },
    { "name": "Operational", "seq": 3, "checklist": [...] }
  ]
}
```

In this example, the "Platform Capability" alpha contributes to the "Platform" alpha. Reaching the "Identified" state on Platform Capability contributes to the "Recognized" state on Platform. The "Operational" state has no mapping — not every state needs a correspondence, and gaps are expected.

**Validation:** `contributesToState` is only meaningful when the owning Alpha has a `contributesTo` or `mapsTo` property set. The named state must exist on the target parent alpha.

#### State-Level Mapping in `mapsTo` Context

When an Alpha declares `mapsTo` (naming a parent alpha it is a variant of), `contributesToState` takes on **equivalence** semantics rather than **contribution** semantics:

- In `contributesTo` context: "reaching this state contributes evidence toward the named parent state" — one of potentially many inputs to the parent's progression
- In `mapsTo` context: "this state IS the named parent state, expressed through this variant's lens" — a direct 1:1 equivalence

Because `mapsTo` requires identical state names, the mapping is typically the identity (each state maps to its identically-named counterpart on the parent). Explicit `contributesToState` declarations can be omitted when state names match — tooling can infer the mapping — but explicit declaration is recommended for clarity.

For cross-baseline state mapping (where the contributing alpha was authored independently of the target), see [Section 4.8 — Method-Level Alpha Bindings](composition.md#48-method-level-alpha-bindings).

### 6.3 Programmatic Transition Triggers and Alpha Rollups

The schema natively supports hierarchical alpha dependencies through the `supportingAlphas` property. Child alpha states roll up into parent alpha evaluations; a parent Alpha cannot successfully transition to a higher state unless its designated supportingAlphas have met their calculated prerequisite maturity levels.

**`supportingAlphas` — Merge-Populated Inverse of `contributesTo`:**

The `supportingAlphas` property on an Alpha is an array of full `Alpha` objects (the same pattern as `variants`). It provides a pre-computed inverse of the `contributesTo` relationship: for a given parent alpha, `supportingAlphas` contains all alphas that declare `contributesTo` this parent. This enables hierarchical rendering and state rollup computation without requiring consumers to scan the entire alpha graph.

- **Populated during merge** (see [merge.md](../merge.md)): after all extension layers merge, the merge algorithm collects every alpha whose `contributesTo` names a given parent and embeds the full Alpha object in that parent's `supportingAlphas` array
- **Do not set in source practice authoring**: authors declare `contributesTo` on child alphas; `supportingAlphas` is computed, not authored
- **Rendering**: UIs use `supportingAlphas` to display hierarchical alpha trees and compute aggregate state rollups
- **Rollup semantics**: a parent alpha's state progression depends on whether its supporting alphas have reached prerequisite maturity levels — the specific rollup algorithm is implementation-defined but the `supportingAlphas` array provides the input set

### **6.4 Abstract Concepts and Instantiation**

While an Alpha defines an overarching abstract concept or area of concern, real-world execution requires working with specific occurrences of those concepts. The Practice Language supports this through two complementary instance types — AlphaInstanceName and AlphaInstance — whose meaning shifts depending on the context in which they appear.

In a **Practice or Method**, instances provide guidance. They illustrate the kinds of instances that adopters should expect to create, suggest how abstract concepts decompose into concrete concerns, and direct users toward structuring their implementations. For example, a migration practice might declare "Database Migration", "Application Migration", and "Data Migration" as instances of a "Migration Plan" alpha — not to prescribe exactly these instances, but to show the shape of the work ahead. Narratives on these instances provide additional context to help adopters understand when and why each instance matters.

In a **Project**, the same structures take on an operational role. Instances identify the specific, concrete things being tracked — "Q3 PostgreSQL Migration" rather than "Database Migration" — along with their current or target states and the evidence supporting progression.

### **6.5 Alpha Instance Semantics: Guidance vs Tracking**

The Practice Language uses two distinct object types for instance management. The AlphaInstanceName declares and describes instances, while the AlphaInstance records state progression. Their purpose depends on context: in practices they provide guidance; in projects they drive tracking.

**AlphaInstanceName**

The AlphaInstanceName object declares and describes an instance of an alpha concept. These objects reside in the alphaInstances array of a Practice, Method, or Project.

Structure:

- instanceName: Unique identifier for this instance (e.g., "Security Team", "Platform Team")
- description: Brief explanation of what this instance represents
- alphaName: References the baseline or practice-defined alpha being instantiated
- links: Optional array of ExternalLink objects pointing to the primary document(s) used to track this instance (e.g., a Jira board, a Confluence page, a shared register)
- relatesTo: Optional array of InstanceRelationship objects associating this instance with other concern or work-product instances (system of record; see [Section 6.7](#67-instance-relationships-applying-type-edges-to-named-instances))
- narratives: Optional contextual storytelling for this instance
- tags: Optional classification metadata

In a **Practice or Method**, AlphaInstanceName objects provide guidance — they illustrate the kinds of instances adopters should anticipate and, through narratives and descriptions, explain why each matters. A practice might declare "Security Team" and "Platform Team" as instances of the "Team" alpha to show that different teams will have different roles and progression paths, without prescribing that adopters must use exactly these instances.

In a **Project**, AlphaInstanceName objects identify the specific, concrete instances being tracked in this execution context. The optional links array connects each instance to the external systems where it is actually managed.

**AlphaInstance**

The AlphaInstance object records the state of a specific instance at a point in the lifecycle. These objects appear in PatternView.alphaInstances arrays (within practices) and in Project current/target/cycles sections.

Structure:

- instanceName: Must match an instanceName from a declared AlphaInstanceName
- alphaName: The baseline or practice alpha this instance represents
- stateName: The target state for this instance in this phase
- evidenceBy: Array of WorkProductInstance objects proving the state achievement
- relatesTo: Optional array of InstanceRelationship objects (may mirror AlphaInstanceName.relatesTo for consumers that only load current/target)
- links: Optional array of ExternalLink objects pointing to documents specific to this state. Typically omitted when the parent AlphaInstanceName links apply; use only when this particular state is tracked in a different document

In a **Practice**, AlphaInstance objects within pattern views illustrate the expected progression of example instances across phases — showing adopters what states to target and what evidence to gather at each stage of the lifecycle.

In a **Project**, AlphaInstance objects in the current and target sections record the assessed or desired state of each tracked instance, answering "what state has this specific instance achieved, and what evidence proves it?" The evidenceBy array links to concrete work product artifacts, creating a traceable evidence chain from abstract concern through specific instance to tangible deliverable.

**Comparison Table**


| Aspect          | AlphaInstanceName                                          | AlphaInstance                                                     |
| --------------- | ---------------------------------------------------------- | ----------------------------------------------------------------- |
| Purpose         | Declare and describe instances (guidance or identification) | Record state progression (illustrative or assessed)               |
| Location        | Practice/Method/Project alphaInstances                      | PatternView.alphaInstances, Project current/target                |
| Required Fields | instanceName, alphaName                                    | instanceName, alphaName, stateName                                |
| Optional Fields | description, narratives, tags, links, relatesTo            | evidenceBy (recommended), links, relatesTo                        |
| In Practices    | Guidance — illustrates expected instance types              | Illustrative — shows target states per pattern phase              |
| In Projects     | Identification — names the specific things being tracked    | Tracking — records current or target state with evidence          |
| Validation      | instanceName must be unique within context                  | instanceName must match declared AlphaInstanceName                |


**Usage in Practices**

1. **Provide Guidance:** Author declares AlphaInstanceName objects that illustrate the kinds of instances adopters should expect — e.g., different team types, different risk categories, different migration streams
2. **Show Progression:** Pattern views use AlphaInstance objects to illustrate how those example instances should progress through phases
3. **Evidence Chain:** Each AlphaInstance's evidenceBy array shows what work product instances would evidence a given state
4. **Validation:** Operational tooling validates that every AlphaInstance.instanceName matches a declared AlphaInstanceName.instanceName

**Usage in Projects**

1. **Identify Instances:** AlphaInstanceName objects name the specific real-world concerns being tracked in this project
2. **Assess Current State:** The current section uses AlphaInstance objects to record where each instance stands today
3. **Define Target State:** The target section uses AlphaInstance objects to define the desired end state
4. **Track Evidence:** Each AlphaInstance's evidenceBy array links to concrete work product instances that prove state achievement

**Example**

Practice declares two team instances:

```json
{
  "alphaInstances": [
    {
      "instanceName": "Platform Engineering Team",
      "alphaName": "Team",
      "description": "Core platform development and operations team",
      "links": [
        {
          "name": "Team Workspace",
          "description": "Confluence space for the platform engineering team",
          "uri": "https://wiki.example.com/spaces/platform-eng"
        }
      ]
    },
    {
      "instanceName": "Security Team", 
      "alphaName": "Team",
      "description": "Security governance and compliance team"
    }
  ]
}
```

Pattern tracks progression:

```json
{
  "name": "Phase 2: Build Foundation",
  "alphaInstances": [
    {
      "instanceName": "Platform Engineering Team",
      "alphaName": "Team",
      "stateName": "Performs",
      "evidenceBy": [
        {
          "instanceName": "Platform Team Charter",
          "workProductName": "Team Definition",
          "levelOfDetailName": "Defined"
        }
      ]
    }
  ]
}
```

This design serves both guidance and execution: practices use instances to illustrate the kinds of concerns adopters will encounter and how they progress, while projects use the same structures to identify and track the specific real-world instances being managed.

### 6.6 Reference Content: Actionable Examples and Reusable Resources

Practices curate actionable, reusable resources that give practitioners a concrete starting point for their work at specific alpha states. The `references` array on a Practice contains `AlphaInstance` objects — templates, sample artifacts, worked examples, reference architectures, or exemplary implementations that practitioners can directly use or adapt. References are NOT documentation explaining how to do work or describing what an alpha state means; they are things a practitioner can pick up and use.

#### Purpose and Distinction from Other Instance Uses

The Practice Language uses `AlphaInstance` in three distinct contexts, each with different semantics:

| Context | Location | Purpose |
|---------|----------|---------|
| Pattern view instances | `PatternView.alphaInstances` | Illustrate expected progression across lifecycle phases |
| Project instances | Project `current`/`target`/`cycles` | Track actual state in a live engagement |
| **Reference content** | **`Practice.references`** | **Curate actionable starting points — templates, sample artifacts, worked examples** |

Pattern view instances are bound to a specific pattern's phase model — they show what states to target at each stage. Project instances record assessed or desired state in a live execution context. Reference content is neither — it provides actionable, standalone resources that exist independently of any pattern phase or project timeline. The actionability test: "Could a practitioner pick this up and start working with it, or does it merely explain a concept?" If the latter, it is not a reference — it belongs in citations or narrative context instead.

#### Structure

Each reference is an `AlphaInstance` anchored to an alpha at a specific state. Work product references are embedded as `evidenceBy` entries within each alpha reference. External content is linked via `links`.

```json
{
  "references": [
    {
      "name": "TOGAF-Based Platform Architecture",
      "description": "Example of a platform that has achieved the Architecture Selected state following TOGAF architectural patterns.",
      "alphaName": "Platform",
      "stateName": "Architecture Selected",
      "links": [
        {
          "name": "TOGAF Architecture Framework",
          "description": "The Open Group Architecture Framework reference",
          "uri": "https://www.opengroup.org/togaf"
        }
      ],
      "evidenceBy": [
        {
          "name": "TOGAF Architecture Document Template",
          "description": "Template for creating architecture documentation following TOGAF standards with ADR structure.",
          "workProductName": "Architecture",
          "levelOfDetailName": "Defined",
          "links": [
            {
              "name": "Architecture Document Template",
              "description": "Downloadable TOGAF-aligned architecture document template",
              "uri": "https://example.com/templates/togaf-architecture.docx"
            }
          ]
        }
      ]
    }
  ]
}
```

In this example, the reference provides a usable template for the "Platform" alpha at the "Architecture Selected" state. It links to the TOGAF framework as the source, and includes a work product instance — a downloadable architecture document template at the "Defined" level — that practitioners can directly adapt for their own architecture documentation.

**Page-Level References with `ExternalLink.pages` (REQUIRED when applicable):**

Most source documents are primarily explanatory — they describe how to do work, not provide reusable artifacts. But many contain templates, examples, checklists, or sample artifacts at specific locations within the larger document. When the actionable content (template, example, sample artifact) is at a specific location within a larger document, you MUST use the `pages` property on ExternalLink to direct practitioners to the exact reusable content. Without `pages`, the link points to the entire document — which is documentation, not a starting point. This follows APA 7th edition format conventions.

```json
{
  "name": "ISO 27001 Security Controls Template",
  "description": "Example of a security assessment that has achieved the Comprehensive state using ISO 27001 controls mapping.",
  "alphaName": "Platform Risk And Compliance",
  "stateName": "Mitigated",
  "links": [
    {
      "name": "ISO/IEC 27001:2022 Information Security Standard",
      "description": "Annex A controls checklist template for platform security assessment",
      "uri": "https://www.iso.org/standard/27001",
      "pages": "pp. 23-31"
    }
  ],
  "evidenceBy": [
    {
      "name": "Platform Security Controls Register",
      "workProductName": "Security Assessment",
      "levelOfDetailName": "Comprehensive",
      "links": [
        {
          "name": "NIST CSF Mapping Template",
          "description": "Template for mapping controls to NIST Cybersecurity Framework categories",
          "uri": "https://example.com/templates/nist-csf-mapping.xlsx",
          "pages": "Section 3"
        }
      ]
    }
  ]
}
```

In this example, `pages: "pp. 23-31"` directs the practitioner to the specific pages within the ISO standard where the Annex A controls checklist is located, and `pages: "Section 3"` points to the relevant section in the NIST mapping template.

#### Authoring Guidance

**When to use references:**

- When templates, starter documents, or sample artifacts exist that practitioners can adapt rather than creating from scratch — references are the primary mechanism for giving practitioners a starting point for completing their work products
- When worked examples or exemplary implementations show a concrete result a practitioner can study and replicate
- When external standards or reference architectures provide reusable structures (not just explanatory text) — use `ExternalLink.pages` to point to the specific reusable content within the document
- When a large document contains a template, example, checklist, or sample artifact at a specific location — use `ExternalLink.pages` to direct practitioners to the actionable content, not the document as a whole

**When NOT to use references:**

- **For documentation that explains how to do work** — this is not a reference, it is a citation or narrative context. A link to a methodology guide's overview chapter is a citation, not a reference. A link to the template appendix within that guide (with `pages`) is a reference.
- For showing expected progression across lifecycle phases — use pattern views with `AlphaInstance` entries instead
- For tracking actual state in a project — use Project `current`/`target` sections
- For declaring the kinds of instances adopters should anticipate — use `alphaInstances` (AlphaInstanceName) at the practice level

**Actionability test (apply to every candidate):**

Ask: "If a practitioner followed this link, would they find something they can directly use, adapt, or fill in — or would they find text explaining a concept?" Only the former qualifies as a reference. Documentation, conceptual overviews, and methodology descriptions belong in citations.

**Naming conventions:**

- Reference names should be specific and descriptive, identifying the source or nature of the example (e.g., "AWS Well-Architected Platform" rather than "Platform Example 1")
- Work product instance names within `evidenceBy` should identify the specific artifact (e.g., "TOGAF Architecture Document Template" rather than "Architecture Template")

**Categorisation via tags:**

Use the structured tags object on each reference to classify by type:

```json
{
  "name": "Zero-Trust Network Architecture Template",
  "alphaName": "Platform",
  "stateName": "Provisioned",
  "tags": {
    "domainTags": ["Security", "Architecture"],
    "lifecycleTags": ["Adoption"],
    "organizationalTags": ["Platform Team"]
  }
}
```

This enables consuming systems to filter references by domain, lifecycle stage, or organisational context.

#### Validation Rules

1. Each reference's `alphaName` must match a defined alpha in the baseline or practice
2. Each reference's `stateName` must match a state on the referenced alpha
3. Each `evidenceBy` entry's `workProductName` must match a defined work product in the baseline or practice
4. Each `evidenceBy` entry's `levelOfDetailName` must match a level of detail on the referenced work product
5. Reference names should be unique within the `references` array (tooling should warn on duplicates)

### 6.7 Instance Relationships: Applying Type Edges to Named Instances

Type-level relationships (`Alpha.relatesTo`, `Alpha.contributesTo`, `WorkProduct.partOf`, `WorkProduct.contributesToAlphaNames`) describe how **kinds** of concerns and artefacts interact. Instance-level `relatesTo` records how **named occurrences** of those kinds are linked in a project or in practice example instances.

An Account Plan type `produces` Opportunity. That does not say which Opportunity instance belongs to which plan or initiative. An Initiative Card work product exists to serve Opportunity and Account Plan. That does not say which deal is the pipeline expression of which initiative. Instance `relatesTo` is the join.

**InstanceRelationship structure:**

```json
{
  "relationship": "evidenced by",
  "direction": "outgoing",
  "relationshipKind": "purpose",
  "workProductInstanceName": "Platform Modernization",
  "description": "This opportunity is the pipeline expression of the platform modernization initiative."
}
```

**Field definitions:**

- **relationship** — domain verb (e.g. "produces", "part of", "contributes to", "evidenced by"). Human-readable; tooling must not parse this string.
- **direction** — `outgoing`, `incoming`, or `mutual`, from the declaring instance.
- **alphaInstanceName** xor **workProductInstanceName** — symbolic link to another tracked instance. Exactly one must be present. The target may be a concern instance or a work-product instance (cross-kind links are first-class).
- **relationshipKind** (optional) — which type-level edge this row applies:
  - Alpha `relatesTo` kinds: `dependency`, `production`, `guidance`, `information-flow`, `enabling`, `impact`, `consumption`, `mutual`
  - `containment` — instance application of `WorkProduct.partOf`
  - `contribution` — instance application of `Alpha.contributesTo`
  - `purpose` — work-product instance serves this concern instance (`contributesToAlphaNames`)
- **description** (optional) — why these two instances are associated here

Self-links are invalid. The schema does not require the inverse row on the target; tooling may write one side or both.

**Where it lives:**

| Type | Role |
|------|------|
| `AlphaInstanceName` / `WorkProductInstanceName` | **System of record** — plan identity; exists before assessment |
| `AlphaInstance` / `WorkProductInstance` | Optional mirror on `current` / `target` / `cycles` (and pattern-view examples) for consumers that only load those sections |

Prefer declaring pairings on the Name types. Instance copies are the same graph, not a second one.

**Contrast with nearby fields:**

| Field | Meaning |
|-------|---------|
| Instance `relatesTo` | These two tracked things are associated (structure) |
| `AlphaInstance.evidenceBy` | This work-product instance at a LOD **proves** the concern's assessed state |
| `background.alphaInstanceStates` / `workProductInstanceLevels` | Gherkin Given — those instances must have reached a named state/LOD before checklists apply |
| Type `mapsTo` | IS-A variant. Do **not** instantiate as a `relatesTo` row; instantiate the variant type |

An Opportunity can be associated with an Initiative Card without that card being the evidence that the Opportunity is `Qualified`.

**Authoring:** Persist actionable kinds (`production`, `enabling`, `dependency`, `impact`, `containment`, `contribution`, `purpose`). Skip noisy type-level verbs such as "uses" or "governed by" unless the team needs those links. `mapsTo` stays type-only.

**Example (concern ↔ work product):**

```json
{
  "name": "Acme OpenShift Renewal",
  "alphaName": "Opportunity",
  "relatesTo": [
    {
      "relationship": "evidenced by",
      "direction": "outgoing",
      "relationshipKind": "purpose",
      "workProductInstanceName": "Platform Modernization",
      "description": "Pipeline expression of the platform modernization initiative."
    }
  ]
}
```

The Initiative Card may declare the reverse (`alphaInstanceName` + `incoming` / `purpose`). Either side is enough for traversal.


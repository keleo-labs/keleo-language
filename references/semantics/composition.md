[< Back to Semantic Guidance Hub](../semantics.md)

## 4 Adapting and Composing Practices

The schema is built for modularity, allowing practices to be adapted and combined.

### 4.1 Practice Dependencies

The Practice object supports an array of practiceDependencyNames. This acts as a symbolic link to other required methodologies. Tooling must resolve these dependencies to allow organizations to build modular, composable methodologies where advanced practices inherit or require the successful validation of foundational ones.

### 4.1.1 Dependency Version Constraints

Documents that reference other documents by name can optionally declare version constraints via the `dependencyVersions` array. Each entry is a `DocumentVersionConstraint` object containing:

- `documentName` — the name of the referenced document (must match a dependency name declared elsewhere in the same document, e.g. a `baselinePracticeName`, `practiceDependencyNames` entry, `practiceNames` entry, `practiceName`, or `methodName`).
- `versionRange` — a semver range constraint using npm/node-semver syntax (e.g. `^2.0.0`, `>=1.0.0 <3.0.0`, `~1.2.0`).

**Example:**

```json
{
  "name": "Platform Engineering",
  "baselinePracticeName": "Platform Adoption Essentials",
  "practiceDependencyNames": ["Team Topologies Lifecycle"],
  "dependencyVersions": [
    { "documentName": "Platform Adoption Essentials", "versionRange": ">=1.2.0 <2.0.0" },
    { "documentName": "Team Topologies Lifecycle", "versionRange": "^1.0.0" }
  ]
}
```

**Resolution semantics:**

1. Dependencies are still resolved by name (unchanged from current behaviour).
2. If the referring document has a `dependencyVersions` entry matching the resolved document's name, tooling normalises the resolved document's `version` to three-part semver and checks it against the `versionRange`.
3. Version mismatches produce **warnings** by default, not errors. Practice authors should not be blocked during authoring; CI pipelines and package validation may use a strict mode that treats mismatches as errors.
4. If no matching `dependencyVersions` entry exists for a dependency, any version is accepted (current behaviour, unchanged).
5. A `dependencyVersions` entry whose `documentName` does not match any declared dependency name is an orphaned constraint; tooling should warn about it.

**Interaction with the package layer:**

Document-level `dependencyVersions` complements the package-level `PackageDependency` mechanism. The package layer operates at package identity (which package, at what version range); the document layer operates at document identity (which specific document, at what version range). A package may satisfy its package-level dependency constraint yet contain a document at a version that violates a document-level constraint. Tooling should resolve both layers: first select a compatible package, then verify that documents within it satisfy document-level constraints. When documents are consumed outside packages (standalone files resolved via a library index), document-level `dependencyVersions` is the only version constraint mechanism available.

### 4.2 Practice and Method Composition (Merge)

When a Method is composed or a Practice's dependencies are resolved, the system produces a single merged document by layering the baseline and extension practices in dependency order. This merge process is fundamental to how the Practice Language achieves modularity — practices are authored independently but consumed as a unified whole.

The merge follows a strict hierarchy: the baseline seeds the accumulator, then each extension practice overlays in dependency-resolved order. Same-named elements are merged rather than duplicated, descriptions from earlier layers (especially the baseline) are preserved, and arrays are unioned using type-aware strategies (name-keyed merge for practice elements, deduplication for primitives, specialized merge for contributions and tags).

For a complete specification of the merge algorithm — including element-level merge rules, array merge strategies, dependency resolution, and post-merge finalization — see [merge.md](../merge.md).

### 4.3 Practice Aliasing and Strict Isolation

Because abstract naming conventions can obscure domain-specific adaptations, a practice or baseline practice can declare aliases via the PracticeElementAlias object. This defines a local name alias for an element type and target name, allowing frictionless alignment with user-specific taxonomy without destroying the structural integrity of the root elements. Baseline practices that adapt a parent baseline for a specific domain (e.g., Infrastructure Automation adapting Platform Adoption Essentials) use aliases to remap parent terminology to domain-appropriate terms while preserving structural references.

**PracticeElementAlias Structure:**

```json
{
  "elementType": "Alpha | WorkProduct | Activity | Persona | PersonaGroup",
  "name": "canonical baseline or practice element name",
  "aliasName": "user-friendly alternative term"
}
```

Purpose: Allows practices to adopt terminology from source methodologies or organizational vocabulary while preserving structural references to canonical baseline names.

#### **CRITICAL RULE: Strict Alias Isolation**

Vendor-specific or localized names must be isolated entirely within the PracticeElementAlias array. **The aliasName string must NEVER be used for internal structural references within the JSON document.** All structural relationships (such as alphaName inside an AlphaContribution, activitySpaceName inside an Activity, or contributesTo on a new alpha) must strictly use the canonical baseline name. The alias serves ONLY as a presentation-layer substitution, not a structural foreign key.

**Why This Rule Exists:**

- **Preserves Structural Integrity**: Ensures all references validate against the canonical baseline, not localized terminology
- **Enables Validation**: Tooling can verify references against baseline definitions without resolving aliases first
- **Supports Practice Composition**: Multiple practices using different aliases for the same baseline element can compose cleanly
- **Prevents Reference Fragmentation**: Structural graph remains coherent even when presentation layer varies

**Invalid vs Valid Pattern Examples:**

**INVALID Example (Alias Used in Structure):**

```json
{
  "aliases": [
    {
      "elementType": "Alpha",
      "name": "Platform",
      "aliasName": "Cloud Platform"
    }
  ],
  "patterns": [
    {
      "name": "Adoption Journey",
      "views": [
        {
          "name": "Phase 1",
          "alphaStates": [
            {
              "alphaName": "Cloud Platform",  // WRONG - uses alias in structural reference
              "stateName": "Provisioned"
            }
          ]
        }
      ]
    }
  ]
}
```

**Problem**: The alphaName field uses "Cloud Platform" (the alias) instead of "Platform" (the canonical name). This breaks validation because no alpha named "Cloud Platform" is defined. Aliases are for presentation only.

**VALID Example (Canonical Name in Structure):**

```json
{
  "aliases": [
    {
      "elementType": "Alpha",
      "name": "Platform",
      "aliasName": "Cloud Platform"
    }
  ],
  "patterns": [
    {
      "name": "Adoption Journey",
      "views": [
        {
          "name": "Phase 1",
          "alphaStates": [
            {
              "alphaName": "Platform",  // CORRECT - uses canonical baseline name
              "stateName": "Provisioned"
            }
          ]
        }
      ]
    }
  ]
}
```

**Correct**: The alphaName field uses "Platform" (canonical). Presentation tooling will display this as "Cloud Platform" to users based on the alias, but the structural reference remains valid against the baseline.

**Example: Activity Space Alias**

Source methodology uses "Build & Deploy" instead of baseline "Architect and Build the Foundation":

```json
{
  "aliases": [
    {
      "elementType": "ActivitySpace",
      "name": "Architect and Build the Foundation",
      "aliasName": "Build & Deploy"
    }
  ],
  "activities": [
    {
      "name": "Deploy Infrastructure",
      "activitySpaceName": "Architect and Build the Foundation",  // CANONICAL, not "Build & Deploy"
      "description": "Provision core platform infrastructure"
    }
  ]
}
```

**Example: Multiple Aliases for Different Audiences**

Practice can define multiple aliases to serve different stakeholder perspectives:

```json
{
  "aliases": [
    {
      "elementType": "Alpha",
      "name": "Platform",
      "aliasName": "Cloud Infrastructure"  // Technical audience
    },
    {
      "elementType": "Alpha",
      "name": "Platform Value And Economics",
      "aliasName": "Business Case"  // Business audience
    }
  ]
}
```

All structural references still use "Platform" and "Platform Value And Economics" (canonical names), but presentation layer can adapt based on audience context.

**Validation Enforcement:**

- **Phase 2 Translation**: Must use canonical baseline names in all structural fields (alphaName, stateName, workProductName, activitySpaceName, contributesTo, etc.)
- **Alias Validation**: Every alias.name must match either a baseline element name or a practice-defined element name
- **Presentation Layer Only**: Aliases apply only when rendering to humans (UIs, reports, narratives), never in JSON structure
- **Tooling**: Editors and validators should warn if aliasName appears in any structural field

**Common Mistakes:**

- Using aliasName in contributesTo (breaks floating alpha validation)
- Referencing alias in AlphaContribution.alphaName (breaks state validation)
- Expecting aliases to work as "symbolic links" in structure (they don't—presentation only)
- Creating aliases for elements that don't exist (alias.name must match defined element)

This strict isolation ensures that the Practice Language maintains referential integrity and composability while still accommodating diverse organizational vocabularies at the presentation layer.

### 4.4 Redeclaration vs Specialization vs Variant Mapping Decision Framework

When extending a baseline practice with alpha-related content, authors must decide whether to redeclare (enrich) an existing baseline alpha, create a new specialized alpha, or create a variant mapping. This decision profoundly affects practice composability, validation, and semantic coherence. The fundamental decision question is: **"Is this content generally applicable (universal), a sub-concern with distinct progression (specialization), or a named variant of the same concept (variant mapping)?"**

**Redeclaration (Enrichment) - Use When:**

- Source material enhances a baseline alpha with additional verification criteria or quality gates
- Content applies universally to the alpha concept, regardless of practice domain
- The same state progression as baseline is appropriate (no new states needed)
- Multiple perspectives (Business, Technology, People, Process) contribute content to the same conceptual alpha
- Examples: Adding security-focused checklists to platform states, adding compliance criteria to governance states, adding risk assessment criteria to existing progression
- Source material enhances a baseline Activity space with additional context

**Specialization (New Alpha) - Use When:**

- Source material describes a focused subset of a baseline concept requiring distinct state progression
- Content is practice-specific and would not apply universally to all uses of the baseline alpha
- The baseline state progression is insufficient—different maturity milestones are needed
- The concept is reusable across multiple scenarios within the practice domain but not universally
- **CRITICAL**: The new alpha MUST declare a contributesTo relationship to a baseline alpha (see [Section 6.1](alphas.md#61-defining-core-alphas-and-baseline-isolation))
- Examples: "Platform Capability" alpha (specialized progression) contributing to baseline "Platform" alpha, "Security Controls Framework" contributing to baseline governance alpha

**Variant Mapping (mapsTo) - Use When:**

- Source material describes a distinct named variant of a baseline concept that follows the same state progression
- The concept IS-A type of the parent alpha (e.g., "AI-Ready Enterprise" IS a "Sales Play"), not a sub-part
- The baseline state progression is appropriate—the variant uses the same milestones with domain-specific checklists
- Multiple variants may exist in parallel, each standing in for the parent as an independent specialised version
- On merge, variant alphas appear within the parent alpha (via the `variants` array), enabling UIs and renderers to present them as related types
- **CRITICAL**: The new alpha MUST declare a `mapsTo` relationship to a parent alpha. States MUST match the target alpha exactly. An alpha may also declare `contributesTo` alongside `mapsTo`, but the targets must be different alphas (e.g., an alpha can map to one alpha and contribute to another).
- Examples: "AI-Ready Enterprise" mapsTo "Sales Play" (same lifecycle, AI-specific checklists), "AI Platform Domain" mapsTo "Technical Decision Point" (same progression, domain-specific verification)

**Decision Matrix:**


| Source Content                                    | Same States as Baseline? | Generally Applicable? | Scope                       | Approach                        |
| ------------------------------------------------- | ------------------------ | --------------------- | --------------------------- | ------------------------------- |
| Adds verification criteria to existing states     | Yes                      | Yes                   | Universal enhancement       | Redeclaration                   |
| Maintains scope and objectives of baseline        | Yes                      | Yes                   | Universal                   | Redeclaration                   |
| Different state progression needed                | No                       | No                    | Practice-specific subset    | New Alpha (Specialization)      |
| Focused domain subset requiring distinct maturity | No                       | No                    | Specialized domain          | New Alpha (Specialization)      |
| Multi-perspective view of same concept            | Yes                      | Yes                   | Different analytical angles | Merged Redeclaration            |
| IS-A variant with same state progression          | Yes                      | No (domain-specific)  | Named variant of parent     | Variant Mapping (mapsTo)        |
| Domain-specific lens on universal concept         | Yes                      | No (domain-specific)  | Specialized version         | Variant Mapping (mapsTo)        |


**Concrete Examples:**

**Example 1: Redeclaration (Valid)**

Source material provides cloud-specific checkpoints for platform maturity but uses the same progression as the baseline:

```json
{
  "name": "Platform",
  "description": "(exact copy from baseline)",
  "focusName": "Solution",
  "states": [
    {
      "name": "Architecture Selected",
      "description": "(exact copy from baseline)",
      "seq": 1,
      "checklists": [
        {
          "seq": 1,
          "name": "Cloud provider selected",
          "description": "Target cloud platform identified and approved"
        },
        {
          "seq": 2,
          "name": "Multi-region strategy defined",
          "description": "Geographic distribution and failover approach documented"
        }
      ]
    }
  ]
}
```

**Reasoning**: These checklists apply universally when platform adoption involves cloud infrastructure. They enhance the baseline without narrowing its scope or changing state progression.

**Example 2: Specialization (Valid)**

Source material describes platform capabilities as distinct from the overall platform, requiring focused progression:

```json
{
  "name": "Platform Capability",
  "description": "Individual platform service or capability maturity",
  "focusName": "Solution",
  "contributesTo": "Platform",
  "states": [
    {
      "name": "Identified",
      "description": "Capability need recognized",
      "seq": 1
    },
    {
      "name": "Designed",
      "description": "Capability interface and behavior specified",
      "seq": 2
    },
    {
      "name": "Implemented",
      "description": "Capability code complete and tested",
      "seq": 3
    },
    {
      "name": "Published",
      "description": "Capability available to consumers",
      "seq": 4
    },
    {
      "name": "Adopted",
      "description": "Capability actively used by consumer teams",
      "seq": 5
    }
  ]
}
```

**Reasoning**: Platform capabilities have their own lifecycle distinct from overall platform maturity. This specialized progression tracks individual services while contributing to the parent "Platform" alpha's health.

**Example 3: Invalid Approach (Should Be Redeclaration, Not Specialization)**

Author creates new alpha "Cloud Platform" for cloud-specific platform tracking with identical states as baseline "Platform":

```json
{
  "name": "Cloud Platform",
  "description": "Cloud-based platform maturity",
  "focusName": "Solution",
  "contributesTo": "Platform",
  "states": [
    "(identical to baseline Platform states)"
  ]
}
```

**Problem**: This duplicates the baseline without adding value. The cloud-specific content should be added as checklists to a Platform redeclaration, not a separate alpha. This creates semantic fragmentation and validation confusion. Note: if "Cloud Platform" genuinely IS a Platform (same states, domain-specific checklists, distinct identity), use `mapsTo` instead — see Example 5.

**Example 4: Multi-Perspective Merged Redeclaration**

Module 00 analysis identifies that both Business and Technology perspectives enhance the baseline "Platform" alpha:

```json
{
  "name": "Platform",
  "description": "(exact copy from baseline)",
  "focusName": "Solution",
  "states": [
    {
      "name": "Baselined",
      "description": "(exact copy from baseline)",
      "seq": 3,
      "checklists": [
        {
          "seq": 1,
          "name": "Architecture documented (Technology)",
          "description": "Reference architecture and design decisions recorded"
        },
        {
          "seq": 2,
          "name": "Financial model approved (Business)",
          "description": "Platform economics and chargeback model validated"
        },
        {
          "seq": 3,
          "name": "ROI projections documented (Business)",
          "description": "Expected business value and cost savings quantified"
        }
      ]
    }
  ]
}
```

**Reasoning**: One merged redeclaration accommodates both perspectives rather than creating separate definitions. The checklists are tagged by perspective for clarity.

**Example 5: Variant Mapping (Valid)**

Source material describes a Sales Play variant for AI-Ready Enterprise that follows the same lifecycle as all Sales Plays but with domain-specific checklists:

```json
{
  "name": "AI-Ready Enterprise",
  "description": "Sales play focused on AI readiness transformation, guiding sellers through the standard sales play lifecycle with AI-specific verification criteria and domain expertise.",
  "mapsTo": "Sales Play",
  "focusName": "Value",
  "states": [
    {
      "name": "Selected",
      "description": "Sales play identified as appropriate for this opportunity",
      "seq": 1,
      "checklist": [
        { "seq": 1, "name": "AI maturity assessed", "description": "Customer AI readiness and current capabilities evaluated" },
        { "seq": 2, "name": "AI use cases identified", "description": "High-value AI application areas mapped to customer needs" }
      ]
    },
    { "name": "Activated", "seq": 2, "checklist": ["..."] },
    { "name": "Executing", "seq": 3, "checklist": ["..."] },
    { "name": "Measured", "seq": 4, "checklist": ["..."] },
    { "name": "Optimized", "seq": 5, "checklist": ["..."] }
  ]
}
```

**Reasoning**: AI-Ready Enterprise IS a Sales Play — it follows the same lifecycle (Selected → Activated → Executing → Measured → Optimized) with AI-specific checklists. Using `mapsTo` rather than `contributesTo` because: (a) it has the same state progression as its parent, (b) it is a distinct named variant, not a sub-concern feeding into the parent, and (c) on merge it should appear within the Sales Play alpha's `variants` array for UI rendering. This is different from specialization (which would have its own distinct states) and from redeclaration (which would keep the parent's name).

**Common Mistakes:**

- Creating specialized alphas when checklists would suffice
- Using redeclaration when states need to differ (forcing awkward checklist-only tracking)
- Forgetting contributesTo or mapsTo on new alphas (violating the floating alpha prohibition)
- Creating multiple redeclarations of the same baseline alpha instead of merging perspectives
- Changing baseline name or description during redeclaration (forbidden—breaks referential integrity)
- Using `contributesTo` when the alpha has identical states as its parent and IS-A semantics apply (should be `mapsTo`)
- Using `mapsTo` when the alpha needs a different state progression (should be `contributesTo`)
- Setting `mapsTo` and `contributesTo` to the same target alpha (they must reference different alphas)

**Validation Enforcement:**

- Phase 2 translation validates that redeclarations preserve baseline name, description, and state structure exactly
- Phase 2 validates that all new alphas have contributesTo or mapsTo relationships
- Phase 2 validates that `mapsTo` alphas have identical state names and sequences as their target alpha
- Phase 2 validates that `mapsTo` and `contributesTo` reference different alphas when both are present
- Practice composition tooling should warn when multiple redeclarations of the same baseline alpha are detected (should be merged)

### 4.5 Adapting and Extending Practice Elements

Practices can now adapt PracticeElements from dependent practices or the baselinePractice. The objective is to allow Practices to add new information to existing PracticeElements while maintaining core operational integrity.

**Redeclaration:** Enrichment of baseline Alpha, ActivitySpace, or Competency

- Source enhances baseline elements with additional information
- The redeclaration **MUST NOT** narrow the scope of the original element's objectives or outcomes - use a *Specialization* instead. 
- Additional information can include checklists (alphas or workProducts), new narratives, tags, and keywords. 
- Multiple perspectives enhance the same concept
- **Plan:** Merge perspectives into single redeclaration

**Specialization:** New Alpha, Activity, WorkProduct, Persona, PersonaGroup

- Source describes a narrower, more specific objective or outcome. 
- **Plan:** Create new practiceElement with a contributesTo relationship to the original element

**Instances:** For Alphas and WorkProducts

- Source describes specific occurrences or examples
- Multiple concurrent versions (e.g., different team types, or work products for different instances)
- Patterns and PatternViews can be used to 
- **Plan:** Declare AlphaInstanceName, track in patterns

**PracticeElementAlias:** Adopt the language of the source methodology

- Source methodology uses alternative term to mean the same thing
- Providing an alias will allow users to better understand the methodology
- Can be used with Redeclaration
- Available on both Practice and PracticeBaseline — baselines adapting a parent baseline for a domain use aliases to remap terminology (e.g., "Platform" → "Automation Platform")

**Decision Matrix:**


| Source Content                           | Same States? | Multiple Concurrent? | Scope              | Approach             |
| ---------------------------------------- | ------------ | -------------------- | ------------------ | -------------------- |
| Adds criteria to baseline                | Yes          | No                   | Universal          | Redeclaration        |
| Maintains scope of objective and outcome | Yes          | No                   | Universal          | Redeclaration        |
| **Alphas:** Different state progression  | No           | No                   | Specialized subset | New Alpha            |
| Multiple examples                        | Varies       | Yes                  | Specific instances | Instances            |
| Multi-perspective view                   | Yes          | No                   | Different aspects  | Merged Redeclaration |
| Same meaning, different term             | Yes          | No                   | Universal          | PracticeElementAlias |


When extending existing elements:

- The new practice **MUST NOT** change the name property of the original element (as it is the unique key).  
- The new practice **MUST NOT** change the description property of the original element.  
- The new practice **CAN** add new narratives, tags, and keywords.

**Alpha Redeclaration:** Alphas have States. These Alpha States **MUST NOT** be changed. However, the State checklists **CAN** be added to.

### 4.6 Practice Partitioning and Value-Driven Scoping

When composing extension practices, authors must avoid "functional decomposition" (e.g., creating a generic "Testing Practice" or "Coding Practice" consisting only of flat task lists). Instead, a Practice must be scoped as a Value-Additive Unit addressing a discrete, cohesive area of concern (e.g., "Product Discovery" or "Zero-Trust Networking"). Authors should evaluate their methodology across four distinct perspectives: Business (commercial logic), Technology (system design), People (team RACI), and Process (operational workflows). If source material blends multiple distinct value-streams, it must be partitioned into separate, cohesive Practice documents, resolving cross-dependencies via the practiceDependencyNames array.

### 4.7 Alpha vs Work Product Decision Framework

When translating source methodology content into the Practice Language, authors must correctly classify each concept as either an Alpha (abstract concern) or a Work Product (tangible artifact). Misclassification is the most common ontological error in practice generation and fundamentally corrupts the evidence model. The fundamental decision question is: **"Am I tracking the health and progress of an abstract concern, or am I describing the developing maturity of a tangible artifact?"**

**Alpha (Abstract Concern) — Model as Alpha When:**

- The concept represents a domain of concern whose health or progress matters to the endeavor (e.g., "Plant Health," "Platform Adoption," "Stakeholder Alignment")
- You cannot hand someone the concept — it is observed indirectly through evidence
- States represent conceptual milestones in the concern's evolution (e.g., Identified → Understood → Monitored → Optimized)
- Multiple different artifacts could provide evidence that this concern has reached a given state
- Removing all documentation would not eliminate the concern itself — it would still exist as an abstract reality
- The concept answers "what must go well?" rather than "what must we produce?"

**Work Product (Tangible Artifact) — Model as Work Product When:**

- The concept describes a specific type of content that a team produces — configuration files, documentation, dashboards, assessment records, source code, presentations, templates
- You can point to a concrete deliverable — a file, a repository, a report, a dashboard
- Levels of Detail represent the developing maturity of that content from skeletal to comprehensive (e.g., Observational Checklist → Quantitative Health Profile → Diagnostic Case File)
- The concept answers "what must we deliver?" rather than "what must go well?"
- The artifact serves as evidence for one or more alpha state achievements via the `contributesTo` relationship on each Level of Detail

**The Litmus Test — Three Quick Checks:**

1. **The Handoff Test**: Can you hand it to a colleague as a file, document, or deliverable? If yes → Work Product. If no → Alpha.
2. **The Deletion Test**: If you deleted every document about it, would the concern still exist? If yes → Alpha. If no → Work Product.
3. **The Evidence Test**: Does this thing *provide* evidence, or does it *require* evidence? Work Products provide evidence for alpha states. Alphas require evidence (from work products) to prove state achievement.

**Decision Matrix:**

| Source Concept | Can Hand Off? | Survives Deletion? | Provides or Requires Evidence? | Classification |
| --- | --- | --- | --- | --- |
| "The overall health of our security posture" | No | Yes | Requires evidence | Alpha |
| "Security audit report documenting findings" | Yes | No | Provides evidence | Work Product |
| "Architecture maturity across the platform" | No | Yes | Requires evidence | Alpha |
| "Architecture document with diagrams and ADRs" | Yes | No | Provides evidence | Work Product |
| "Plant health and development trajectory" | No | Yes | Requires evidence | Alpha |
| "Plant health assessment record" | Yes | No | Provides evidence | Work Product |
| "Adoption readiness of the platform" | No | Yes | Requires evidence | Alpha |
| "Platform onboarding guide for developers" | Yes | No | Provides evidence | Work Product |

**The Structural Bridge: evidencedBy and contributesTo**

Alphas and Work Products are not independent — they form an evidence network. The Practice Language provides two complementary linkage mechanisms:

1. **Work Product LOD → Alpha State** (`contributesTo` on LevelOfDetail): Each LOD declares which alpha states it advances. This is required by schema.
2. **Alpha State Checklist → Work Product LOD** (`evidencedBy` on Checklist): Each alpha state checklist item can declare which work product at which LOD proves it is satisfied. This is optional but recommended.

If you cannot articulate either direction of this relationship, the modeling is wrong. Every alpha state should be evidenced by at least one work product LOD, and every work product LOD should contribute to at least one alpha state. A "floating" work product that contributes to nothing, or an alpha state with no conceivable evidence, signals a classification error.

**Example 1: Correct Separation (Platform Domain)**

Source material describes "platform architecture" — the abstract concern of having a sound architecture, and the concrete document that captures architectural decisions.

Alpha (abstract concern being tracked):

```json
{
  "name": "Platform",
  "states": [
    {"name": "Architecture Selected", "seq": 1,
     "checklist": [
       {"name": "Architecture documented", "seq": 1,
        "description": "Reference architecture created with technology decisions and rationale",
        "evidencedBy": [
          {"workProductName": "Architecture", "levelOfDetailName": "Outlined"}
        ]}
     ]},
    {"name": "Provisioned", "seq": 3,
     "checklist": [
       {"name": "Architecture validated in production", "seq": 1,
        "description": "Architecture proven through production deployment with validated scaling",
        "evidencedBy": [
          {"workProductName": "Architecture", "levelOfDetailName": "Validated"}
        ]}
     ]}
  ]
}
```

Work Product (tangible artifact providing evidence):

```json
{
  "name": "Architecture",
  "description": "Technical blueprint detailing platform infrastructure, capability domains, and integration patterns.",
  "levelsOfDetail": [
    {"name": "Outlined", "seq": 1,
     "description": "High-level block diagram showing major capability domains and technology choices.",
     "checklist": [
       {"seq": 1, "name": "Component diagram created",
        "description": "System components and their relationships visually documented"},
       {"seq": 2, "name": "Technology decisions documented",
        "description": "Each major technology choice explained with rationale"}
     ],
     "contributesTo": [{"alphaName": "Platform", "stateName": "Architecture Selected"}]},
    {"name": "Detailed", "seq": 2,
     "description": "Comprehensive architecture documenting all capability domains with integration patterns and API contracts.",
     "checklist": [
       {"seq": 1, "name": "Integration patterns specified",
        "description": "API contracts, data flows, and integration approaches defined"},
       {"seq": 2, "name": "Scaling strategy documented",
        "description": "Horizontal and vertical scaling approaches with capacity projections"}
     ],
     "contributesTo": [{"alphaName": "Platform", "stateName": "Provisioned"}]},
    {"name": "Validated", "seq": 3,
     "description": "Architecture proven through production deployment with validated scaling, security, and DR characteristics.",
     "checklist": [
       {"seq": 1, "name": "Production performance validated",
        "description": "Load testing confirms architecture meets scaling requirements"},
       {"seq": 2, "name": "DR procedures tested",
        "description": "Disaster recovery failover validated against RTO/RPO targets"}
     ],
     "contributesTo": [{"alphaName": "Platform", "stateName": "Hosting Assets"}]}
  ]
}
```

**Reasoning**: "Platform" is the abstract concern — you cannot hand someone a platform's architectural health. "Architecture" is the tangible document that provides evidence. The LOD names (Outlined → Detailed → Validated) describe the content's developing maturity. The alpha states (Architecture Selected → Provisioned → Hosting Assets) describe conceptual milestones of the platform concern. The `contributesTo` and `evidencedBy` relationships form the structural bridge between them.

**Example 2: Correct Separation (Horticulture Domain)**

Alpha (abstract concern):

```json
{
  "name": "Plant Health & Development",
  "states": [
    {"name": "Identified", "seq": 1,
     "checklist": [
       {"name": "Plant inventory established", "seq": 1,
        "description": "All plants catalogued with species and location data"}
     ]},
    {"name": "Monitored", "seq": 3,
     "checklist": [
       {"name": "Health assessment covers key indicators", "seq": 1,
        "description": "Systematic evaluation of vitality, growth rate, pest pressure, and stress markers",
        "evidencedBy": [
          {"workProductName": "Plant Health Assessment Record",
           "levelOfDetailName": "Observational Checklist"}
        ]}
     ]}
  ]
}
```

Work Product (tangible artifact):

```json
{
  "name": "Plant Health Assessment Record",
  "description": "Documented evaluation of plant vitality, growth patterns, and condition over time.",
  "levelsOfDetail": [
    {"name": "Observational Checklist", "seq": 1,
     "description": "Visual inspection form recording symptom presence and basic condition.",
     "checklist": [
       {"seq": 1, "name": "Visual indicators recorded",
        "description": "Leaf colour, wilting, pest damage, and growth abnormalities noted"}
     ],
     "contributesTo": [
       {"alphaName": "Plant Health & Development", "stateName": "Monitored"}
     ]},
    {"name": "Quantitative Health Profile", "seq": 2,
     "description": "Measured parameters with calibrated severity ratings and trend data.",
     "checklist": [
       {"seq": 1, "name": "Quantitative metrics captured",
        "description": "Soil pH, moisture levels, growth measurements with instrument readings"}
     ],
     "contributesTo": [
       {"alphaName": "Plant Health & Development", "stateName": "Optimized"}
     ]}
  ]
}
```

**Reasoning**: "Plant Health & Development" is abstract — you cannot hand someone a plant's health trajectory. The "Plant Health Assessment Record" is the tangible document that evidences progress. LODs describe the document's developing maturity (visual checklist → quantitative profile). States describe the concern's conceptual milestones (Identified → Monitored → Optimized).

**Example 3: Anti-Pattern — Alpha Whose States Read Like Document Versions (WRONG)**

```json
{
  "name": "Security Policy",
  "description": "Organization's security controls and compliance requirements.",
  "states": [
    {"name": "Drafted", "seq": 1, "checklist": []},
    {"name": "Reviewed", "seq": 2, "checklist": []},
    {"name": "Approved", "seq": 3, "checklist": []},
    {"name": "Published", "seq": 4, "checklist": []},
    {"name": "Enforced", "seq": 5, "checklist": []}
  ]
}
```

**Problem**: These states describe document lifecycle stages (Drafted → Reviewed → Approved → Published), not the health progression of an abstract concern. The litmus test: you can hand someone a security policy document. This should be a Work Product with LODs describing content maturity, not an Alpha.

**Correct modeling**: Split into an Alpha "Security Posture" (abstract concern with states: Assessed → Defined → Implemented → Validated → Adaptive) and a Work Product "Security Policy Document" (tangible artifact with LODs: Policy Outline → Comprehensive Controls → Automated Compliance Checks).

**Example 4: Anti-Pattern — Work Product Whose LODs Read Like Abstract Concern Progression (WRONG)**

```json
{
  "name": "Team Effectiveness Report",
  "levelsOfDetail": [
    {"name": "Forming", "seq": 1,
     "description": "Team is being assembled.",
     "checklist": [], "contributesTo": []},
    {"name": "Storming", "seq": 2,
     "description": "Team is resolving conflicts.",
     "checklist": [], "contributesTo": []},
    {"name": "Performing", "seq": 3,
     "description": "Team is delivering value.",
     "checklist": [], "contributesTo": []}
  ]
}
```

**Problem**: These LODs describe the abstract concern of team maturity (Tuckman stages), not the maturity of a report's content. The litmus test: "Forming" describes the team's state, not the report's content quality. This conflates the Alpha concern (team health) with the Work Product (the report documenting it).

**Correct modeling**: Alpha "Team" with states Formed → Collaborating → Performing. Work Product "Team Effectiveness Report" with LODs describing the report's developing content maturity: Summary Scorecard → Detailed Analysis → Trend Dashboard.

**LOD Content Model and Naming Guidance:**

LOD names must describe the depth and fidelity of the artifact's content, not the progression of the abstract concern it evidences. The critical principle is that **every LOD covers the full scope of the work product — the difference between levels is depth and fidelity, not breadth**. A Level 1 document has the same table of contents as a Level 4 document; each section is simply briefer. Use the five-level rubric in `references/workproduct-assessment-rubric.csv` as a lens when designing LODs:

| Rubric Level | LOD Content Character | Example LOD Names |
| --- | --- | --- |
| Level 1: Summarised | Complete scope in brief form — concise statements, short bullet lists, one-paragraph overviews per topic | Outlined, Summary, Checklist, Brief, Overview |
| Level 2: Structured | Complete scope with logical organisation — defined sections, relationships between concepts, supporting rationale | Detailed, Defined, Comprehensive, Framework, Blueprint |
| Level 3: Elaborated | Complete scope with full explanatory depth — worked examples, evidence, scenarios, contextual guidance | Applied, Scenario-Based, Validated, Evidence-Based, Contextualised |
| Level 4: Actionable | Complete scope with operational readiness — templates, decision frameworks, automation, calculators | Automated, Interactive, Self-Service, Executable, Toolkit |

**Depth vs Breadth**: LODs must NOT be additive — where each level introduces new topics or perspectives absent from lower levels. That pattern makes LODs resemble alpha state progressions (a process) rather than content maturity (a depth dial). Instead, every level addresses the same complete set of concerns; what changes is how deeply each concern is treated. A Level 1 "Architecture" document briefly covers components, relationships, failure modes, and capacity. A Level 3 version covers the same topics with worked deployment examples, trade-off analysis, and contextualised scenarios.

Not every work product requires four LODs — use what fits the source content (minimum 2 per schema). LOD names should be domain-appropriate for the artifact type, not generic labels. "Observational Checklist → Quantitative Health Profile → Diagnostic Case File" is good because each name tells you what the document actually contains at that depth level.

**Common Mistakes:**

- Modeling a document or artifact as an Alpha because it feels "important" — importance does not determine classification, tangibility does
- Writing Alpha states that describe document lifecycle stages (Drafted, Reviewed, Approved) instead of concern health milestones
- Writing Work Product LODs that describe abstract concern progression instead of artifact content maturity
- Creating a Work Product with no `contributesTo` links — a floating artifact that evidences nothing
- Creating an Alpha whose states cannot be evidenced by any conceivable work product
- Naming LODs with generic numbered labels ("Level 1", "Level 2") instead of content-descriptive names

**Validation Enforcement:**

- Phase 1 analysis must explicitly classify each source concept as Alpha or Work Product using the litmus test before proceeding to Phase 2
- Phase 2 must validate that every LevelOfDetail has at least one `contributesTo` entry (required by schema)
- Phase 2 should flag alpha state names that resemble document lifecycle terminology (drafted, reviewed, approved, published, versioned)
- Phase 2 should flag LOD names that resemble abstract concern progression rather than content maturity descriptors
- Cross-validation: every alpha state should be reachable via at least one work product LOD `contributesTo`; orphaned states indicate missing work products or incorrect classification

### 4.8 Method-Level Bindings

Methods compose practices from orthogonal baseline families — for example, a project management family and a platform adoption family. These families are designed independently on separate baselines, with no knowledge of each other. When composed into a method, elements in one family need to connect to elements in another: placeholder alphas (e.g., "Deliverable" in project management) to concrete alphas (e.g., "Platform" in platform adoption), and work products in one family to work products in another.

The `bindings` property on Method declares these cross-baseline relationships. It is an object containing two arrays — `alphaBindings` and `workProductBindings` — each supporting both **contribution** and **variant** relationship types. The method is the right place for these declarations because it is the only construct that knows both baseline families.

#### Relationship Types

Each binding declares a `relationship` that determines its semantic meaning:

| Relationship | Alpha semantics | Work product semantics | Within-baseline equivalent |
|---|---|---|---|
| `"contribution"` | Source alphas contribute evidence toward the target alpha | Source work products are components of the target work product | `contributesTo` / `partOf` |
| `"variant"` | Source alphas are domain-specific versions of the target (IS-A) | Source work products are domain-specific versions of the target (IS-A) | `mapsTo` |

#### Structure

A binding has three parts:

- **relationship** — `"contribution"` or `"variant"`, declaring the semantic type of the binding.
- **target** — a `BaselineAlphaReference` or `BaselineWorkProductReference` identifying the target element by baseline name and element name.
- **sources** — an array of `ContributingAlpha` or `ContributingWorkProduct` entries, each identifying an element from another baseline with optional state/LOD-level mappings.

**Alpha binding example (contribution):**

```json
{
  "bindings": {
    "alphaBindings": [
      {
        "relationship": "contribution",
        "targetAlpha": {
          "baselineName": "Project Management Essentials",
          "alphaName": "Deliverable"
        },
        "sourceAlphas": [
          {
            "baselineName": "Platform Adoption Essentials",
            "alphaName": "Platform",
            "stateContributions": [
              { "fromState": "Operational", "toState": "Built" },
              { "fromState": "Adopted", "toState": "Accepted" }
            ]
          },
          {
            "baselineName": "Platform Adoption Essentials",
            "alphaName": "Migration Path"
          }
        ]
      }
    ]
  }
}
```

In this example, the method composes project management and platform adoption practices. The binding declares that "Platform" and "Migration Path" from the platform adoption baseline contribute to "Deliverable" from the project management baseline. "Platform" includes state-level mappings (reaching "Operational" contributes to "Built" on Deliverable; reaching "Adopted" contributes to "Accepted"). "Migration Path" contributes at the alpha level only — no state correspondence is declared.

**Alpha binding example (variant):**

```json
{
  "relationship": "variant",
  "targetAlpha": {
    "baselineName": "Sales Essentials",
    "alphaName": "Sales Play"
  },
  "sourceAlphas": [
    {
      "baselineName": "AI Adoption Essentials",
      "alphaName": "AI Sales Play",
      "stateContributions": [
        { "fromState": "Opportunity Qualified", "toState": "Selected" },
        { "fromState": "Solution Mapped", "toState": "Activated" },
        { "fromState": "Proof Delivered", "toState": "Executing" },
        { "fromState": "Deal Closed", "toState": "Measured" }
      ]
    }
  ]
}
```

Here the AI baseline uses 4 states with different names while Sales Essentials uses 5. The mapping declares which correspond; the unmapped target state "Optimized" is not directly expressed by the AI variant.

**Work product binding example (contribution):**

```json
{
  "workProductBindings": [
    {
      "relationship": "contribution",
      "targetWorkProduct": {
        "baselineName": "Project Management Essentials",
        "workProductName": "Project Documentation"
      },
      "sourceWorkProducts": [
        {
          "baselineName": "Platform Adoption Essentials",
          "workProductName": "Architecture",
          "lodContributions": [
            { "fromLevelOfDetail": "Validated", "toLevelOfDetail": "Complete" }
          ]
        }
      ]
    }
  ]
}
```

**Work product binding example (variant):**

```json
{
  "relationship": "variant",
  "targetWorkProduct": {
    "baselineName": "Platform Adoption Essentials",
    "workProductName": "Architecture"
  },
  "sourceWorkProducts": [
    {
      "baselineName": "Cloud Essentials",
      "workProductName": "Cloud Architecture",
      "lodContributions": [
        { "fromLevelOfDetail": "Cloud Blueprint", "toLevelOfDetail": "Outlined" },
        { "fromLevelOfDetail": "Cloud Design Document", "toLevelOfDetail": "Detailed" },
        { "fromLevelOfDetail": "Validated Cloud Architecture", "toLevelOfDetail": "Validated" }
      ]
    }
  ]
}
```

#### Two Levels of State/LOD Mapping

State and LOD mapping operates at two levels:

1. **Within-baseline** — When an alpha declares `contributesTo` or `mapsTo` within its own baseline or practice, individual states can declare `contributesToState` directly on the State object. Similarly, work products use `partOf` or `mapsTo` within their baseline. The practice author declares mappings at authoring time because the elements know each other. See [Section 6.2](alphas.md#62-state-progression-and-the-guidance-function) and [Section 7.4](work-products.md#74-work-product-instance-metrics).

2. **Cross-baseline** — When the relationship is declared via a binding, the source element was authored independently of the target. Its states/LODs cannot declare direct mappings because they didn't know about the target. Instead, the method author declares mappings in the binding itself via `stateContributions` (for alphas) or `lodContributions` (for work products).

Both levels express the same concept — which states/LODs on a source correspond to states/LODs on a target — but at different levels appropriate to their context.

#### Mapping Guidance and Gap Semantics

Cross-baseline elements are authored independently, so they may use different terminology and different granularity for their states/LODs. The method author must reconcile these differences through explicit mappings.

**Authoring rule:** Map every source state/LOD to its closest semantic equivalent on the target. Prefer full coverage of the target side. Many-to-one mappings are expected and normal — multiple fine-grained source states/LODs may map to one coarser target state/LOD. One-to-many mappings are valid for contribution bindings (one source state advances multiple target states).

**When gaps remain despite best-effort mapping:**

| Gap type | Contribution semantics | Variant semantics |
|---|---|---|
| **Unmapped source** state/LOD | Progress within the source that hasn't reached a contribution threshold — no signal to target | Variant-specific granularity with no parent equivalent — visible only when viewing through the variant lens |
| **Unmapped target** state/LOD | This source doesn't advance that target state/LOD — other sources or evidence must cover it | The variant doesn't distinguish this parent state/LOD — tooling interpolates it between the nearest mapped states/LODs before and after |

**Interpolation rule for variant bindings:** When a variant source reaches a mapped target state/LOD T(n), all unmapped target states/LODs between T(n) and the previously mapped target state/LOD T(n-1) are considered implicitly reached. This follows from IS-A semantics: if the variant has progressed past a point, the parent has too.

**Example:** Source reaches "Implemented" → maps to target "Built". Target "Designed" (unmapped, between "Scoped" and "Built") is implicitly reached because the source has progressed past it.

**Many-to-one example (source more granular):**

```
Source:  Qualified → Assessed → Designed → Validated → Adopted
Target:  Selected  →           Built     →             Accepted
```

```json
"stateContributions": [
  { "fromState": "Qualified", "toState": "Selected" },
  { "fromState": "Assessed",  "toState": "Selected" },
  { "fromState": "Designed",  "toState": "Built" },
  { "fromState": "Validated", "toState": "Built" },
  { "fromState": "Adopted",   "toState": "Accepted" }
]
```

#### Design Principles

- **Bind baselines, not practices.** Bindings reference baseline names. All practices built on those baselines automatically inherit the linkage, keeping everything consistent without per-practice declarations.
- **Map to the closest match.** When source and target use different terminology or granularity, map each state/LOD to its closest semantic equivalent. Many-to-one mappings are preferred over leaving gaps.
- **Bindings are additive.** They declare new edges that emerge from the composition. They do not replace existing `contributesTo`, `partOf`, or `mapsTo` relationships within either baseline.
- **Bindings are directional.** Source elements relate TO the target element. For contribution bindings, progress on sources drives progress on the target. For variant bindings, sources are domain-specific versions of the target.

#### When to Use Bindings

| Scenario | Mechanism |
|----------|-----------|
| Alpha specialization within a baseline | `Alpha.contributesTo` (string naming parent alpha) |
| Alpha variant within a baseline | `Alpha.mapsTo` (string naming parent alpha) |
| State mapping within a baseline | `State.contributesToState` (string naming parent state) |
| Work product containment within a baseline | `WorkProduct.partOf` (string naming parent work product) |
| Work product variant within a baseline | `WorkProduct.mapsTo` (string naming parent work product) |
| Cross-baseline alpha contribution in a method | `AlphaBinding` with `relationship: "contribution"` |
| Cross-baseline alpha variant in a method | `AlphaBinding` with `relationship: "variant"` |
| Cross-baseline state mapping in a method | `stateContributions` on `ContributingAlpha` |
| Cross-baseline work product contribution in a method | `WorkProductBinding` with `relationship: "contribution"` |
| Cross-baseline work product variant in a method | `WorkProductBinding` with `relationship: "variant"` |
| Cross-baseline LOD mapping in a method | `lodContributions` on `ContributingWorkProduct` |

#### Relationship to Merge

Bindings are consumed **after** the merge algorithm produces the unified document. The merge layers baselines and practices in dependency order ([Section 4.2](#42-practice-and-method-composition-merge)). Bindings provide additional edges that tooling should inject into the merged result. The merge algorithm itself does not process bindings — they are post-merge metadata that tooling interprets when rendering or analysing the composed method.

#### Validation Rules

1. Each `baselineName` in a binding must reference a baseline accessible to the method — either the method's own baseline, a baseline it depends on via `baselinePracticeNames`, or a baseline of one of its composed practices.
2. Each `alphaName` must exist within the referenced baseline (for alpha bindings).
3. Each `workProductName` must exist within the referenced baseline (for work product bindings).
4. Each `fromState` in a `stateContributions` entry must be a valid state name within the source alpha.
5. Each `toState` must be a valid state name within the target alpha.
6. Each `fromLevelOfDetail` in a `lodContributions` entry must be a valid LOD name within the source work product.
7. Each `toLevelOfDetail` must be a valid LOD name within the target work product.
8. The same source element (same baselineName + alphaName/workProductName) should not appear in multiple bindings targeting the same target element.
9. Unmapped target states/LODs in contribution bindings produce a warning — confirm the gap is intentional.
10. Unmapped target states/LODs in variant bindings produce an informational notice — interpolation will apply.

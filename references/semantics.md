# **Semantic Guidance and Operational Architecture for the Practice Language JSON Schema**

## Table of Contents

1. [Introduction and Architectural Context](#1-introduction-and-architectural-context)
2. [Ontological Principles and Semantic Integration](#2-ontological-principles-and-semantic-integration)
3. [Method, Practice, and Baseline Architecture](#3-method-practice-and-baseline-architecture)
   - 3.1 [Method Root Type and Discrimination Logic](#31-method-root-type-and-discrimination-logic)
   - 3.2 [Metadata and Provenance](#32-metadata-and-provenance)
   - 3.3 [Schema Versioning and Document Compatibility](#33-schema-versioning-and-document-compatibility)
   - 3.4 [Document Version Format](#34-document-version-format)
4. [Adapting and Composing Practices](#4-adapting-and-composing-practices)
   - 4.1 [Practice Dependencies](#41-practice-dependencies)
     - 4.1.1 [Dependency Version Constraints](#411-dependency-version-constraints)
   - 4.2 [Practice and Method Composition (Merge)](#42-practice-and-method-composition-merge)
   - 4.3 [Practice Aliasing and Strict Isolation](#43-practice-aliasing-and-strict-isolation)
   - 4.4 [Redeclaration vs Specialization Decision Framework](#44-redeclaration-vs-specialization-decision-framework)
   - 4.5 [Adapting and Extending Practice Elements](#45-adapting-and-extending-practice-elements)
   - 4.6 [Practice Partitioning and Value-Driven Scoping](#46-practice-partitioning-and-value-driven-scoping)
   - 4.7 [Alpha vs Work Product Decision Framework](#47-alpha-vs-work-product-decision-framework)
   - 4.8 [Method-Level Bindings](#48-method-level-bindings)
5. [PracticeElement Foundations](#5-practiceelement-foundations)
   - 5.1 [PracticeElement, Tagging Taxonomy, and Narrative Anchors](#51-practiceelement-tagging-taxonomy-and-narrative-anchors)
   - 5.2 [Checklists and Dynamic State-Gating](#52-checklists-and-dynamic-state-gating)
   - 5.3 [Structured Guidance: The Gherkin-Inspired Test Model](#53-structured-guidance-the-gherkin-inspired-test-model)
6. [The Alpha-State Trajectory and Dynamic Semantics](#6-the-alpha-state-trajectory-and-dynamic-semantics)
   - 6.1 [Defining Core Alphas and Baseline Isolation](#61-defining-core-alphas-and-baseline-isolation)
   - 6.2 [State Progression and the Guidance Function](#62-state-progression-and-the-guidance-function)
   - 6.3 [Programmatic Transition Triggers and Alpha Rollups](#63-programmatic-transition-triggers-and-alpha-rollups)
   - 6.4 [Abstract Concepts and Expected Instantiations](#64-abstract-concepts-and-expected-instantiations)
   - 6.5 [Alpha Instance Semantics: Declaration vs Execution Tracking](#65-alpha-instance-semantics-declaration-vs-execution-tracking)
7. [Evidentiary Verification via Work Product Elements](#7-evidentiary-verification-via-work-product-elements)
   - 7.1 [Structure of Work Products](#71-structure-of-work-products)
   - 7.2 [Artifact Instantiation and Concurrency](#72-artifact-instantiation-and-concurrency)
   - 7.3 [Work Product Instance Semantics: Declaration vs Evidence Chains](#73-work-product-instance-semantics-declaration-vs-evidence-chains)
   - 7.4 [Work Product Composition (`partOf`)](#74-work-product-composition-partof)
8. [Execution Boundaries and Organizational Roles](#8-execution-boundaries-and-organizational-roles)
   - 8.1 [Activity Spaces and Activities](#81-activity-spaces-and-activities)
     - 8.1.1 [Gherkin-Inspired Structure on Activities](#811-gherkin-inspired-structure-on-activities)
   - 8.2 [Organizational Roles and Persona Definitions](#82-organizational-roles-and-persona-definitions)
9. [Lifecycle Orchestration: Patterns and Phase Models](#9-lifecycle-orchestration-patterns-and-phase-models)
   - 9.1 [Pattern Orchestration and Narrative Hooks](#91-pattern-orchestration-and-narrative-hooks)
   - 9.2 [The PatternView: Complete Structure and Semantics](#92-the-patternview-complete-structure-and-semantics)
10. [Narrative Management](#10-narrative-management)
    - 10.1 [Narrative Tooling Synchronization and Execution Guidelines](#101-narrative-tooling-synchronization-and-execution-guidelines)
    - 10.2 [Cognitive Storytelling Frameworks](#102-cognitive-storytelling-frameworks)
    - 10.3 [Bibliographic Citations and Reference Management](#103-bibliographic-citations-and-reference-management)
    - 10.4 [Acknowledgements and Attribution](#104-acknowledgements-and-attribution)
11. [Visual Assets and Practice Elements](#11-visual-assets-and-practice-elements)
    - 11.1 [Asset Declaration](#111-asset-declaration)
    - 11.2 [Element-Level Asset References](#112-element-level-asset-references)
    - 11.3 [Common Asset Use Cases](#113-common-asset-use-cases)
    - 11.4 [Distribution and Bundling](#114-distribution-and-bundling)
    - 11.5 [Validation Rules](#115-validation-rules)
    - 11.6 [Semantic Guidance](#116-semantic-guidance)
    - 11.7 [Phase 2 Translation Guidance](#117-phase-2-translation-guidance)
    - 11.8 [Best Practices](#118-best-practices)
12. [Project Execution Tracking](#12-project-execution-tracking)
    - 12.1 [Project Purpose and Root Discrimination](#121-project-purpose-and-root-discrimination)
    - 12.2 [Team Structure and Team API Principles](#122-team-structure-and-team-api-principles)
    - 12.3 [Plan Section and Pattern Ownership](#123-plan-section-and-pattern-ownership)
    - 12.4 [Current and Target Sections](#124-current-and-target-sections)
    - 12.5 [ChecklistState and Evidence Tracking](#125-checkliststate-and-evidence-tracking)
    - 12.6 [Notes, External Links, and Automated Journaling](#126-notes-external-links-and-automated-journaling)
13. [Change Requests](#13-change-requests)
14. [Acyclicity Constraints and Circular Reference Protection](#14-acyclicity-constraints-and-circular-reference-protection)
    - 14.1 [Hierarchical Properties Subject to Acyclicity Constraints](#141-hierarchical-properties-subject-to-acyclicity-constraints)
    - 14.2 [Cross-Element Prerequisite Cycles](#142-cross-element-prerequisite-cycles)
    - 14.3 [Document Dependency Graphs](#143-document-dependency-graphs)
    - 14.4 [Revision Chain Acyclicity](#144-revision-chain-acyclicity)
    - 14.5 [Validation Rules Summary](#145-validation-rules-summary)
    - 14.6 [Implementation Requirements](#146-implementation-requirements)
15. [Conclusion](#15-conclusion)

## 1 Introduction and Architectural Context

The proliferation of on-demand computing services, agile software development, and hyperscale cloud infrastructure has fundamentally altered the paradigm of digital business transformation. Organizations are increasingly shifting from static, capital-intensive infrastructure and monolithic project management to dynamic, scalable ecosystems governed by continuous delivery and platform economics. The Practice Language JSON Schema is a meta-model for describing practices, translating abstract engineering and methodology concepts into machine-readable, operational constructs. However, structural JSON definitions alone are insufficient for enterprise-scale methodology enactment. While the schema defines the structural hierarchy of elements—ranging from foundational building blocks to complex execution patterns—it requires comprehensive semantic guidance to ensure practitioners and system architects instantiate, track, and orchestrate these elements effectively. A JSON schema, without rigorous ontological grounding, risks devolving into a static descriptive taxonomy rather than functioning as a prescriptive operational engine. This document provides an exhaustive operational architecture and semantic guidance framework for the Practice Language JSON Schema. It bridges structural JSON definitions with the abstract syntax and operational intent of the language constructs, applying advanced enterprise ontology management.

## 2 Ontological Principles and Semantic Integration

Before examining specific language elements, it is necessary to establish the overarching ontological principles governing the schema. The design of a methodology language must avoid common ontological errors, such as confusing information artifacts (Work Products) with the reality they denote (Alphas). To support interoperability and semantic coherence, the schema prioritizes developer-friendly JSON structures that utilize native values and map to well-known identifiers. Schema authors must explicitly declare the JSON Schema dialect utilizing the $schema keyword (currently [https://json-schema.org/draft/2020-12/schema](https://json-schema.org/draft/2020-12/schema)), ensuring validation engines apply correct specification rules.

**External Analysis Framework:** When developing practices, practitioners should apply the four-perspective enterprise analysis framework documented in `references/domain-framework.md`. This framework (Business, Technology, People, Process perspectives) guides the identification and classification of source methodology content, informing which alphas, activities, and work products should be derived. The framework itself is not part of the Practice Language schema—it is an analytical tool for methodology translation. The Business perspective typically maps to Value focus elements, Technology to Solution focus, and People to Endeavor focus, while Process perspectives may span multiple focuses as cross-cutting concerns.

**Knowledge Graph Integration:** The establishment of unique $id properties is an absolute necessity, providing a stable namespace Internationalized Resource Identifier (IRI) for all methodology components. This allows elements to be reliably referenced across disparate distributed systems. By annotating schemas with JSON-LD metadata, organizations can embed schema definitions inside broader enterprise knowledge graphs. This architectural decision facilitates advanced semantic search capabilities and retrieval-augmented generation (RAG) applications.

## 3 Method, Practice, and Baseline Architecture

At the highest structural level, the schema utilizes a root-level if/then/else validation block to programmatically discriminate between operational entities. This ensures that extension practices are not erroneously validated as full baselines.

### 3.1 Method Root Type and Discrimination Logic

- **PracticeBaseline**: A domain-agnostic, version-controlled registry of core constructs.  
- **Practice**: An applied methodology extension, identified by the presence of a baselinePracticeName.  
- **Method**: The highest-level container, orchestrating a core baselinePractice alongside an array of supplementary practices.

### 3.2 Metadata and Provenance

Both Practice and PracticeBaselineShape mandate explicit metadata properties: authors, createdAt, updatedAt, version, and keywords. Operational tooling must enforce strict version control and standardized ISO timestamp formats for these fields to ensure auditability, intellectual property tracking, and proper lifecycle management of the methodology itself.

### 3.3 Schema Versioning and Document Compatibility

The Practice Language schema declares its own version via a `$comment` keyword at the root level (e.g. `"$comment": "schemaVersion:1.0.0"`). This version follows semantic versioning (semver) conventions:

- **Major** version bump: breaking structural changes (removed fields, renamed types, changed discrimination logic). Documents authored against a prior major version may not validate.
- **Minor** version bump: additive, non-breaking changes (new optional fields, new `$defs` types, expanded enums). Documents authored against a prior minor version still validate.
- **Patch** version bump: non-structural changes (description corrections, documentation updates).

Individual documents declare which schema version they target via an optional `schemaVersion` property (pattern `^\d+\.\d+\.\d+$`). This field is available on Practice, PracticeBaseline, Method, Project, ChangeRequest, and ChangeSet. When present, consuming systems should check compatibility before parsing:

- If the document's major version exceeds the tool's supported major version, reject the document.
- If the document's minor version exceeds the tool's, emit a warning (some features may not be understood).
- If `schemaVersion` is absent, proceed without compatibility checking (backwards compatible).

When a document is packaged in a `.keleo` file, its `schemaVersion` should be consistent with the `PackageManifest.schemaVersion`. The package-level declaration applies to all documents in the package; the document-level field provides finer-grained compatibility information for documents consumed outside a package context.

### 3.4 Document Version Format

The `version` field on Practice, PracticeBaseline, Method, and Project represents the version of that document. The recommended format is semver (e.g. `1.0.0`), but shortened forms like `1.0` remain valid for backwards compatibility. Tooling that performs version range comparison should normalise non-semver versions to three-part form: `1.0` becomes `1.0.0`, `2` becomes `2.0.0`.

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

For a complete specification of the merge algorithm — including element-level merge rules, array merge strategies, dependency resolution, and post-merge finalization — see [merge.md](merge.md).

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
- **CRITICAL**: The new alpha MUST declare a contributesTo relationship to a baseline alpha (see Section 6.1)
- Examples: "Platform Capability" alpha (specialized progression) contributing to baseline "Platform" alpha, "Security Controls Framework" contributing to baseline governance alpha

**Variant Mapping (mapsTo) - Use When:**

- Source material describes a distinct named variant of a baseline concept that follows the same state progression
- The concept IS-A type of the parent alpha (e.g., "AI-Ready Enterprise" IS a "Sales Play"), not a sub-part
- The baseline state progression is appropriate—the variant uses the same milestones with domain-specific checklists
- Multiple variants may exist in parallel, each standing in for the parent as an independent specialised version
- On merge, variant alphas appear within the parent alpha (via the `variants` array), enabling UIs and renderers to present them as related types
- **CRITICAL**: The new alpha MUST declare a `mapsTo` relationship to a parent alpha. `mapsTo` and `contributesTo` are mutually exclusive. States MUST match the target alpha exactly.
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
- Setting both `mapsTo` and `contributesTo` on the same alpha (mutually exclusive)

**Validation Enforcement:**

- Phase 2 translation validates that redeclarations preserve baseline name, description, and state structure exactly
- Phase 2 validates that all new alphas have contributesTo or mapsTo relationships
- Phase 2 validates that `mapsTo` alphas have identical state names and sequences as their target alpha
- Phase 2 validates that `mapsTo` and `contributesTo` are mutually exclusive on a given alpha
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

1. **Within-baseline** — When an alpha declares `contributesTo` or `mapsTo` within its own baseline or practice, individual states can declare `contributesToState` directly on the State object. Similarly, work products use `partOf` or `mapsTo` within their baseline. The practice author declares mappings at authoring time because the elements know each other. See Sections 6.2 and 7.4.

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

Bindings are consumed **after** the merge algorithm produces the unified document. The merge layers baselines and practices in dependency order (Section 4.2). Bindings provide additional edges that tooling should inject into the merged result. The merge algorithm itself does not process bindings — they are post-merge metadata that tooling interprets when rendering or analysing the composed method.

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

## 5 PracticeElement Foundations

Foundation elements provide the baseline from which all other methodology constructs inherit. They establish the universal properties required for identification, metadata classification, and sequential verification.

### 5.1 PracticeElement, Tagging Taxonomy, and Narrative Anchors

The PracticeElement serves as the foundational root object, guaranteeing any instantiated element contains a unique name and a human-readable description. Crucially, it also introduces the narratives array as a universal property. By embedding narrative support at the root object level, the schema ensures that any methodology construct—from a micro-level Work Product to a macro-level Pattern—can be enriched with structured storytelling frameworks. To prevent semantic fragmentation, the schema implements an advanced tagging taxonomy utilizing the structured tags object, enforcing orthogonal data classification.

PracticeElement also carries an optional `contributingPatternName` string for merge-time provenance. This property records which Pattern introduced or enriched the element during practice composition. It is populated automatically by the merge algorithm and must not be set in source practice authoring. While `sourcePracticeName` (set during merge on specific element types) identifies the practice that introduced an element, `contributingPatternName` provides finer-grained attribution to the specific pattern within that practice. Elements introduced outside any pattern context leave this property absent. See [merge.md Section 8.2](merge.md#82-pattern-level-provenance-contributingpatternname) for the full provenance rules.

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

The Checklist element introduces sequential verification. A checklist item must represent a demonstrable operational truth required for phase-gating. Authors should utilize checklists to directly embed and track alphanumeric regulatory or architectural controls (e.g., SOC2 controls, ISO standards, internal architecture OE:05). If a configuration, organizational process, or architectural standard must be true before moving to the next phase, it must be explicitly destructured into an actionable Checklist object attached to the target State or Level of Detail.

#### 5.2.1 Checklist Object Structure and Validation

Checklists provide the operational verification layer that transforms abstract alpha states and work product levels into concrete, auditable gates. The Practice Language defines a consistent checklist structure used across both alpha states and work product levels of detail.

**Checklist Object Structure:**

```json
{
  "seq": integer,
  "name": "string",
  "description": "string",
  "evidencedBy": [WorkProductContribution] (optional),
  "test": Test (optional),
  "examples": [Test] (optional)
}
```

**Field Definitions:**

- **seq**: Integer ordering (1, 2, 3...) determining checklist evaluation sequence within the parent state or level
- **name**: String identifier for the checklist item (typically concise, 3-8 words)
- **description**: String explaining what must be verified or achieved (1-2 sentences describing the operational truth)
- **evidencedBy**: Optional array of WorkProductContribution objects linking this checklist to artifacts that provide evidence (see below)
- **test**: Optional Test object providing structured Given/When/Then verification (see Section 5.3)
- **examples**: Optional array of Test objects providing parameterized variations (see Section 5.3)

**Two Checklist Contexts:**

1. **Alpha State Checklists**: Verification criteria for achieving an alpha state. Located in State.checklists arrays. These answer "what must be demonstrably true for this alpha to have reached this state?"
2. **Work Product LOD Checklists**: Quality gates for achieving a work product level of detail. Located in LevelOfDetail.checklists arrays. These answer "what quality criteria must this artifact satisfy to be considered at this maturity level?"

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

- Checklists are arrays (can be empty [] if no verification criteria defined)
- seq numbers provide ordering and should be unique within the parent array
- evidencedBy is optional—checklists can represent verification criteria without explicit artifact linkage (e.g., organizational approvals, external validations)
- When evidencedBy is present, workProductName must reference a defined work product, and levelOfDetailName must match a level within that work product

**Checklist Authoring Guidance:**

- **Demonstrable Truth**: Each item represents something that can be objectively verified or measured
- **Regulatory/Architectural Controls**: Embed specific controls (SOC2 requirements, ISO standards, internal architecture principles) directly as checklist items
- **Phase-Gating**: Checklists should represent gates that must be passed before progression to next state/level
- **Evidence Linkage**: Use evidencedBy when concrete artifacts prove checklist satisfaction; omit when verification is external (e.g., stakeholder approval)

**Example: Alpha State Checklist**

```json
{
  "name": "Architecture Selected",
  "description": "Platform architecture approach chosen and documented",
  "seq": 1,
  "checklists": [
    {
      "seq": 1,
      "name": "Architecture documented",
      "description": "Reference architecture created with technology stack decisions and rationale",
      "evidencedBy": [
        {
          "workProductName": "Architecture",
          "levelOfDetailName": "Defined"
        }
      ]
    },
    {
      "seq": 2,
      "name": "Security review completed",
      "description": "Security team has reviewed and approved architecture approach",
      "evidencedBy": []
    },
    {
      "seq": 3,
      "name": "Cost model validated",
      "description": "Financial projections for infrastructure costs approved by finance team",
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
      "name": "Component diagram created",
      "description": "System components and their relationships visually documented"
    },
    {
      "seq": 2,
      "name": "Technology decisions documented",
      "description": "Each major technology choice explained with rationale and alternatives considered"
    },
    {
      "seq": 3,
      "name": "Integration patterns specified",
      "description": "API contracts, data flows, and integration approaches defined"
    }
  ]
}
```

**Phase 2 Translation Requirements:**

- Extract checklist arrays from source material for both alpha states and work product LODs
- Validate seq ordering (should be sequential: 1, 2, 3...)
- Validate evidencedBy references against defined work products
- Empty checklist arrays are valid (indicates no verification criteria from source)
- Missing checklists where source material specifies verification criteria indicates translation failure

**Operational Semantics:**

The schema validation engine evaluates checklists using strict operational semantics to enable phase-gating:

- Checklists must be satisfied in seq order
- When evidencedBy is present, the specified work product must exist at the specified level before the checklist passes
- Automated tooling can generate "to-do" lists from unsatisfied checklists
- Progress dashboards can visualize checklist completion as state/level achievement indicators

This structured approach transforms qualitative methodology guidance into quantitative, traceable verification criteria, enabling organizations to measure and validate their adoption progress objectively.

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

When `test` is absent, the checklist's own `name` and `description` continue to serve their current role as the complete outcome specification (full backward compatibility). When `test` is present, it provides structured verification detail — the checklist's name/description remain the concise label, while the test decomposes the verification into preconditions, triggers, and outcomes. The test's `given` supplements any background-level prerequisites on the parent state or level of detail.

Examples serve as practitioner guidance — they illustrate how a general checklist item manifests in specific real-world scenarios. They do not replace the parent checklist's test scenario; they specialise it for concrete contexts.

**Example: Checklist with Test and Examples**

```json
{
  "name": "SLOs defined and monitored",
  "description": "Service level objectives are defined and dashboards are actively monitored.",
  "seq": 1,
  "test": {
    "name": "SLO verification",
    "description": "Verify that SLOs are defined and alerts are operational.",
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
      "description": "SLO verification for external-facing API gateway.",
      "given": ["the API gateway handles external traffic"],
      "when": ["a latency spike exceeds the p99 threshold"],
      "then": ["an alert fires within 5 minutes", "the on-call engineer is paged"]
    },
    {
      "name": "Data pipeline SLO",
      "description": "SLO verification for nightly data pipeline.",
      "given": ["the ETL pipeline runs on a nightly schedule"],
      "when": ["the pipeline fails to complete within the SLO window"],
      "then": ["a data freshness alert fires", "downstream consumers are notified"]
    }
  ]
}
```

#### 5.3.5 Authoring Guidance

The following guidance applies to all uses of Background, Test, and Examples — whether on checklist items (Section 5.3.4) or activities (Section 8.1.1).

**When to use Background:**
- When a state, level, or activity space has prerequisites that apply to ALL its children (not just one checklist item or activity)
- When cross-alpha dependencies exist that cannot be expressed through sequential progression
- When work product prerequisites clarify the context for evaluation or execution
- At the instance level, when project-specific conditions supplement or specialise the practice-level background
- On an ActivitySpace, when a governance-level prerequisite applies to all activities in the space (e.g., stakeholder recognition, strategic approval). Do not duplicate ActivitySpace-level prerequisites on individual activities.

**When to use Test:**
- When the existing name/description alone do not convey the full context (what must be true, what to do, what to observe)
- When a checklist item or activity benefits from separating the precondition from the action from the outcome
- On activities, `test.when` is particularly valuable because it captures the trigger that is otherwise implicit — describe decision points, events, or lifecycle moments that initiate the work
- On activities, `test.then` should complement, not duplicate, the structural `contributesTo` and `worksOn` — use it for outcomes meaningful to practitioners but not captured by symbolic alpha/work-product references (e.g., "risk factors are documented" rather than restating "advances Opportunity to Determined")
- Partial use is valid: a test can have `given` without `when` or `then`, or `then` without `given`

**When to use Examples:**
- When a checklist item or activity applies differently across contexts (e.g., different service types, team structures, deployment models, greenfield vs migration)
- When concrete illustrations would help practitioners understand how to apply a general criterion
- When the element is inherently parameterized (the same pattern with different values)
- An element can have `examples` without a `test`, or a `test` without `examples`

**When NOT to use these constructs:**
- When the existing name/description adequately convey the criterion or intent
- When adding structure would be purely ceremonial without improving practitioner understanding
- Baseline checklists should remain minimal — the practice layer is the natural place for detailed Gherkin structure

## 6 The Alpha-State Trajectory and Dynamic Semantics

The Alpha (Abstract-Level Progress Health Attribute) defines the essential elements of an endeavor requiring tracking and progression.

### 6.1 Defining Core Alphas and Baseline Isolation

Every Alpha contains a mandatory array of states (minimum of 3) and is categorized under a focusName. The operational guidance emphasizes the strict separation of the conceptual entity from its documentation. A "Requirements" Alpha represents actual stakeholder needs, not the requirements document itself.

#### **Baseline Isolation Rules: The Floating Alpha Prohibition**

**THE CRITICAL RULE: NO FLOATING ALPHAS**

When extending a baseline practice, all new alphas introduced in a practice extension MUST explicitly declare either a `contributesTo` or `mapsTo` relationship pointing to a valid alpha. This is not a guideline—it is an absolute constraint enforced during Phase 2 validation. Alphas that lack either relationship are known as "floating alphas" and are strictly prohibited by the Practice Language semantics. The two properties are mutually exclusive on a given alpha—use `contributesTo` for specialization (sub-concern with distinct state progression) and `mapsTo` for variant mapping (IS-A variant with identical state progression).

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
4. **Mutual Exclusivity**: `contributesTo` and `mapsTo` are mutually exclusive—an alpha MUST NOT have both properties
5. **State Matching for mapsTo**: A `mapsTo` alpha MUST have identical state names and sequences as its target alpha. It CAN have a different name, description, and checklists.

**No Circular Dependencies**: Alpha A cannot contribute to Alpha B if Alpha B (or any alpha in B's `contributesTo`/`mapsTo` chain) contributes/maps to Alpha A. See [Section 14 — Acyclicity Constraints and Circular Reference Protection](#14-acyclicity-constraints-and-circular-reference-protection) for the comprehensive acyclicity rules and implementation requirements.

#### **Semantic Relationships: The relatesTo Property**

Beyond specialization (`contributesTo`) and variant mapping (`mapsTo`), alphas can declare rich semantic relationships via the optional `relatesTo` array. This property enables the Practice Language to capture domain-specific dependencies, influences, constraints, and other interactions between alphas that are not hierarchical in nature.

**AlphaRelationship Structure:**

```json
{
  "relationship": "string",
  "alphaName": "string",
  "direction": "outgoing | incoming | mutual",
  "description": "string (optional)"
}
```

**Field Definitions:**

- **relationship**: The type of relationship (e.g., "depends on", "influences", "constrains", "validates", "precedes", "enables", "provides", "guides", "evidences", "funds", "impacts", "justifies", "demonstrates ROI for")
- **alphaName**: Name of the related alpha in the same baseline (symbolic link; must match Alpha.name exactly)
- **direction**: Explicit directionality enabling programmatic traversal without semantic interpretation of the relationship verb:
  - `outgoing` — this alpha acts upon the target (e.g., A "depends on" B, A "constrains" B)
  - `incoming` — the target acts upon this alpha (e.g., A "is governed by" B, A "is supported by" B)
  - `mutual` — symmetric relationship in both directions (e.g., A "correlates with" B)
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
      "description": "The platform is constructed and maintained by the team responsible for its delivery."
    },
    {
      "relationship": "hosts",
      "alphaName": "Platform Asset",
      "direction": "outgoing",
      "description": "The platform hosts individual platform assets such as services, tools, and infrastructure components."
    },
    {
      "relationship": "exposes",
      "alphaName": "Platform Consumption Interface",
      "direction": "outgoing"
    },
    {
      "relationship": "governed by",
      "alphaName": "Platform Governance",
      "direction": "incoming"
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

- **Dependency Analysis**: "What alphas does Platform depend on?" → filter relatesTo for `outgoing` dependency relationships
- **Impact Analysis**: "What alphas are affected if Requirements change?" → find all alphas with `incoming` relationships referencing Requirements
- **Knowledge Graphs**: Each relationship becomes a directed semantic triple (`<Alpha> relationship <Alpha>`) for graph databases, with `direction` determining edge orientation
- **Workflow Automation**: "guides" and "produces" relationships inform activity sequencing
- **Progress Tracking**: "evidenced by" relationships link abstract progress to concrete artifacts

**Common Mistakes:**

- Using `relatesTo` for specialization (use `contributesTo` instead)
- Setting `direction` inconsistently with the relationship verb (e.g., "depends on" with `incoming` — the verb implies `outgoing`)
- Using vague relationship types like "related to" instead of specific verbs
- Referencing alphas from external practices without declaring practice dependencies
- Conflating relationships with narrative context (relationships are structural, narratives are explanatory)

This dual-relationship model—`contributesTo` for hierarchy and `relatesTo` for semantics—provides both ontological coherence (all concepts anchor to baseline) and rich domain expressiveness (practices can model complex alpha interactions).

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

For cross-baseline state mapping (where the contributing alpha was authored independently of the target), see Section 4.8 (Method-Level Alpha Bindings).

### 6.3 Programmatic Transition Triggers and Alpha Rollups

The schema natively supports hierarchical alpha dependencies through the supportingAlphas property. Child alpha states roll up into parent alpha evaluations; a parent Alpha cannot successfully transition to a higher state unless its designated supportingAlphas have met their calculated prerequisite maturity levels.

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
- links: Optional array of ExternalLink objects pointing to documents specific to this state. Typically omitted when the parent AlphaInstanceName links apply; use only when this particular state is tracked in a different document

In a **Practice**, AlphaInstance objects within pattern views illustrate the expected progression of example instances across phases — showing adopters what states to target and what evidence to gather at each stage of the lifecycle.

In a **Project**, AlphaInstance objects in the current and target sections record the assessed or desired state of each tracked instance, answering "what state has this specific instance achieved, and what evidence proves it?" The evidenceBy array links to concrete work product artifacts, creating a traceable evidence chain from abstract concern through specific instance to tangible deliverable.

**Comparison Table**


| Aspect          | AlphaInstanceName                                          | AlphaInstance                                                     |
| --------------- | ---------------------------------------------------------- | ----------------------------------------------------------------- |
| Purpose         | Declare and describe instances (guidance or identification) | Record state progression (illustrative or assessed)               |
| Location        | Practice/Method/Project alphaInstances                      | PatternView.alphaInstances, Project current/target                |
| Required Fields | instanceName, alphaName                                    | instanceName, alphaName, stateName                                |
| Optional Fields | description, narratives, tags, links                       | evidenceBy (recommended), links                                   |
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

### 6.6 Reference Content: Curated Examples and Reusable Resources

Practices can curate concrete, real-world examples and reusable resources that illustrate alphas at specific states. The `references` array on a Practice contains `AlphaInstance` objects that serve as standalone reference content — templates, case studies, sample artifacts, or exemplary implementations that consuming systems can surface to practitioners as available resources.

#### Purpose and Distinction from Other Instance Uses

The Practice Language uses `AlphaInstance` in three distinct contexts, each with different semantics:

| Context | Location | Purpose |
|---------|----------|---------|
| Pattern view instances | `PatternView.alphaInstances` | Illustrate expected progression across lifecycle phases |
| Project instances | Project `current`/`target`/`cycles` | Track actual state in a live engagement |
| **Reference content** | **`Practice.references`** | **Curate standalone exemplars — templates, case studies, sample artifacts** |

Pattern view instances are bound to a specific pattern's phase model — they show what states to target at each stage. Project instances record assessed or desired state in a live execution context. Reference content is neither — it provides curated, standalone examples that exist independently of any pattern phase or project timeline.

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

In this example, the reference illustrates the "Platform" alpha at the "Architecture Selected" state. It links to the TOGAF framework as context, and includes a work product instance — a template architecture document at the "Defined" level — that practitioners can use as a starting point.

#### Authoring Guidance

**When to use references:**

- When a practice has access to real-world examples that would help practitioners understand what "good" looks like at a specific alpha state
- When templates, starter documents, or sample artifacts exist that practitioners can adapt rather than creating from scratch
- When case studies or exemplary implementations illustrate how an alpha progresses through states in practice
- When external standards, frameworks, or reference architectures map to specific alpha states

**When NOT to use references:**

- For showing expected progression across lifecycle phases — use pattern views with `AlphaInstance` entries instead
- For tracking actual state in a project — use Project `current`/`target` sections
- For declaring the kinds of instances adopters should anticipate — use `alphaInstances` (AlphaInstanceName) at the practice level

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

## 7 Evidentiary Verification via Work Product Elements

A WorkProduct is the tangible artifact providing the empirical evidence necessary to validate Alpha state progressions. Work Products are the evidentiary artifacts of the practice. To ensure rigorous maturity tracking, a Work Product must explicitly define its progression through at least three Levels of Detail, aligning with progressive organizational adoption.

### 7.1 Structure of Work Products

Every WorkProduct is defined by a progression sequence of LevelOfDetail objects (minimum of 2). Each level dictates specific quality gates, and achieving a specific level directly contributes to advancing parent Alphas via an AlphaContribution.

**LevelOfDetail Naming and Content Maturity Progression:**

LOD names must describe the maturity or sophistication of the artifact's content — what the artifact contains at each level. They must not describe the abstract concern the artifact evidences (see Section 4.6 for the full Alpha vs Work Product decision framework).

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

**Structural Requirements:**

- Each LevelOfDetail MUST include a `contributesTo` array with at least one AlphaContribution (`{alphaName, stateName}`) linking this maturity level to the alpha state(s) it advances (see Section 4.6 for the semantic rationale)
- Each LevelOfDetail MUST include a `checklist` array (may be empty) defining quality gates for achieving that level
- LOD checklists describe characteristics the artifact must exhibit at this maturity level, not steps to create it
- The `seq` integer determines ordering; lower LODs represent less mature content

### 7.2 Artifact Instantiation and Concurrency

The evidenceRequired property dictates the ingestion of a URI linking the logical JSON object to physical reality. Because enterprise execution is inherently parallelized, implementations must support branching metadata to allow tracking of experimental drafts without corrupting canonical Alpha calculations.

### **7.3 Work Product Instance Semantics: Guidance vs Evidence Chains**

The Practice Language uses two distinct object types for work product instance management, mirroring the alpha instance design (Section 6.5). As with alpha instances, their purpose shifts depending on context: in practices they provide guidance about expected deliverables; in projects they identify and track specific artifacts.

**WorkProductInstanceName**

The WorkProductInstanceName object declares and describes an instance of a work product. These objects reside in the workProductInstances array of a Practice, Method, or Project.

Structure:

- instanceName: Unique identifier for this variant (e.g., "Security Requirements", "Platform Architecture")
- description: Brief explanation of what this variant represents
- workProductName: References the baseline or practice-defined work product being instantiated
- links: Optional array of ExternalLink objects pointing to the primary document(s) used to track this work product (e.g., a shared document, repository, or wiki page)
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
- links: Optional array of ExternalLink objects pointing to documents specific to this level of detail. Typically omitted when the parent WorkProductInstanceName links apply; use only when this particular maturity level is tracked in a different document

In a **Practice**, WorkProductInstance objects within evidence arrays illustrate what artifacts at what maturity levels would prove state achievement — showing adopters the expected evidence chain.

In a **Project**, WorkProductInstance objects record the assessed or desired maturity of each tracked artifact, answering "what artifact at what maturity level proves this progression?" The levelOfDetailName indicates how comprehensive or mature the artifact is, directly mapping to the work product's defined levels of detail.

**Comparison Table**


| Aspect          | WorkProductInstanceName                                    | WorkProductInstance                                              |
| --------------- | ---------------------------------------------------------- | ---------------------------------------------------------------- |
| Purpose         | Declare and describe instances (guidance or identification) | Record maturity level (illustrative or assessed)                 |
| Location        | Practice/Method/Project workProductInstances                | evidenceBy arrays, Project current/target                        |
| Required Fields | instanceName, workProductName                              | instanceName, workProductName, levelOfDetailName                 |
| Optional Fields | description, narratives, tags, links                       | links                                                            |
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

### 7.4 Work Product Composition (`partOf`)

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
- Circular chains are invalid: if A partOf B, then B must not directly or transitively declare partOf A. See [Section 14 — Acyclicity Constraints and Circular Reference Protection](#14-acyclicity-constraints-and-circular-reference-protection) for the comprehensive acyclicity rules and implementation requirements.
- Keep hierarchies shallow — one level of containment is typical

**Contrast with Alpha `contributesTo`**

Alpha `contributesTo` models specialization: a sub-concern contributing to the health of a parent concern (abstract progress rollup). WorkProduct `partOf` models composition: a sub-artifact physically contained within a parent artifact (tangible containment). The semantic distinction matters: `contributesTo` aggregates state progression; `partOf` declares structural nesting of deliverables.

**Merge Behavior**

During practice composition (Section 4.2), `partOf` merges as a scalar field: the first non-empty value (from the kernel or earliest overlay) wins.

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

### 7.5 Work Product Variant Mapping (`mapsTo`)

Work products can declare a `mapsTo` relationship to indicate that one work product is a specialized variant of another. This mirrors the `mapsTo` relationship on Alphas (Section 4.4) — the variant IS-A type of the parent work product, following the same levels of detail with domain-specific checklists.

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
- Circular chains are invalid: if A mapsTo B, then B must not directly or transitively declare mapsTo or partOf A. See [Section 14 — Acyclicity Constraints and Circular Reference Protection](#14-acyclicity-constraints-and-circular-reference-protection) for the comprehensive acyclicity rules and implementation requirements
- Levels of detail MUST match the target work product exactly (same LOD names and sequences). The variant CAN have a different name, description, and checklists.

**Contrast with `partOf`**

- **`partOf`** models **containment**: a sub-artifact physically contained within a parent artifact (e.g., "API Contract" partOf "Architecture")
- **`mapsTo`** models **variant equivalence**: a specialized version of the same artifact type (e.g., "Cloud Architecture" mapsTo "Architecture")

The semantic distinction matters: `partOf` declares structural nesting of deliverables; `mapsTo` declares that the variant IS the parent artifact, viewed through a domain-specific lens. On merge, `mapsTo` work products are embedded in the parent's `variants` array (Section 4.2), enabling UIs to present them as related types.

**Merge Behavior**

During practice composition (Section 4.2), `mapsTo` merges as a scalar field: the first non-empty value wins. After all extension layers merge, work products with `mapsTo` are aggregated into the target work product's `variants` array (see [merge.md Section 7.2b](merge.md#72b-work-product-variant-aggregation)).

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

## 8 Execution Boundaries and Organizational Roles

### 8.1 Activity Spaces and Activities

- **ActivitySpace**: A generalized boundary categorizing broad areas of effort. Crucially, the ActivitySpace object features an involves array that references PersonaGroup.name. This explicitly links broad execution boundaries directly to grouped organizational roles, ensuring macro-level responsibilities are programmatically mapped to specific talent pools.  
- **Activity**: Extends the Activity Space, providing specific actionable swimlanes. It works on specific artifacts (worksOn) and defines strict recommendedCompetencyLevels.

**Baseline Isolation Rules**: Practice authors should avoid creating new ActivitySpaces in extension practices. Instead, new tactical Activities should strictly map to existing overarching corporate governance boundaries by utilizing the activitySpaceName property to reference a baseline ActivitySpace.

#### 8.1.1 Gherkin-Inspired Structure on Activities

Activities and ActivitySpaces use the same Gherkin-inspired Test model described in Section 5.3, adapted for execution context rather than verification. While states and checklists answer "what must be true?", activities answer "what work should be done, when, and with what expected outcomes?" See Section 5.3.5 for consolidated authoring guidance covering both checklists and activities.

**Background on ActivitySpaceCore:**

Both ActivitySpace and Activity inherit an optional `background` property (via ActivitySpaceCore). On an ActivitySpace, `background` declares governance-level prerequisites that apply to all activities in the space. On an Activity, `background` declares activity-specific prerequisites. The Background type is the same as described in Section 5.3.3.

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

Activities support an optional `test` property and an optional `examples` array — the same Test type used on Checklist items (Section 5.3.4). The key semantic differences from checklist usage:

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

The alphaInstances array tracks specific instances (see Section 6.5) within this phase, using AlphaInstance objects:

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

This comprehensive structure enables PatternViews to orchestrate methodology execution, tracking both abstract progression (alphaStates) and concrete instances (alphaInstances), coordinating deliverables (workProducts), and guiding work (activities), all while providing narrative context that connects the phase to stakeholder-friendly storytelling frameworks.

## 10 Narrative Management

Narratives provide a way for practices to include additional information and context about any PracticeElement. When used the narrative content **MUST** be kept succinct, providing information in a minimal outlined style. It should **NOT** replicate sections of the source content, instead it should provide a summary of that content, with **Citations** being used to direct the user to further reading.

**Narrative Naming:**

The `name` property of a Narrative must summarize what the narrative tells the reader, not what structural role the narrative plays. The `narrativeTypeName` already carries the structural role (e.g., "Hero's Journey", "STAR", "Practice Intent"). The `name` must convey the specific story or message so that a reader scanning a method with multiple practices can distinguish each narrative at a glance.

**Anti-Pattern — Generic Role-Based Names (WRONG):**

- "Practice Intent" — which practice? What does it intend?
- "Overview Narrative" — overview of what?
- "Hero's Journey for Platform" — exposes template mechanics

**Correct — Content-Descriptive Names:**

- "Accelerating Platform Adoption Through Self-Service Infrastructure"
- "From Manual Provisioning to Automated Golden Paths"
- "Transforming Developer Experience with Internal Platform Capabilities"

Each name should be specific enough that reading it alone tells you the subject matter and perspective of the narrative. In a method with five practices, five narratives named "Practice Intent" are indistinguishable; five content-descriptive names create a scannable table of contents.

**Narrative Context Self-Containment:**

Users consume narratives as: **name**, **description**, and a sequence of **context** strings. The narrative element names (from the NarrativeType) are authoring scaffolding — they guide the writer but are **NOT displayed** to the reader. Each `context` value must therefore be self-contained: coherent and meaningful when read in sequence without any element headings.

**The Self-Containment Test:** Read the narrative's name, description, and contexts in order as a continuous piece of prose. If any context is a non sequitur — a list of items, warnings, or steps that only makes sense under a heading like "Common Pitfalls" or "Prerequisites" — it fails the test.

**Anti-Pattern — Heading-Dependent Context (WRONG):**

> *Name:* VM Inventory Discovery and Compatibility Classification
> *Description:* How to discover, classify, and assess source VMs for migration readiness.
> *Context 1:* Install the MTV operator, create Provider CRs for each source platform...
> *Context 2:* Create Provider CRs with platform-specific credentials...
> *Context 3:* Failing to validate VMware VDDK version compatibility. Overlooking the 47-character VM naming constraint. Attempting to assess the entire estate at once.

Context 3 is a bare list of mistakes — without the "Common Pitfalls" heading it reads as a non sequitur.

**Correct — Self-Contained Context:**

> *Context 3:* Common mistakes include failing to validate VMware VDDK version compatibility and NFC memory settings before assessment, overlooking the 47-character VM naming constraint for Kubernetes resources, and attempting to assess the entire VM estate at once rather than progressively by provider type.

A single framing clause ("Common mistakes include...") makes the context readable as prose without any external heading.

**Rules:**
1. Each context must open with a framing sentence or clause that establishes what the paragraph is about
2. Bare lists (gerund phrases, noun phrases, or sentence fragments without a lead-in) require a framing introduction
3. The sequence of contexts must read as coherent prose: name → description → context 1 → context 2 → ... → context N

### 10.1 Narrative Tooling Synchronization and Execution Guidelines

The NarrativeType class defines specific narrative approaches by acting as a container for embedded NarrativeElement objects. Crucially, each NarrativeElement contains a required howToUse string. This property provides explicit authoring instructions for practitioners, detailing exactly how the narrative spine element should be applied in practice. Operational tooling must explicitly synchronize the narrativeName with human-facing interfaces. Execution milestones are mapped to this narrative spine via NarrativeContext elements, delivering highly relevant contextual slices based on the user's progress.

### 10.2 Cognitive Storytelling Frameworks

The following are examples of NarrativeTypes that could be described in the baselinePractice for practice authors to use, **Always** check the baselinePractice for the latest frameworks. 

- **The STAR Format (Situation, Task, Action, Result)**: Enforces a strict cause-and-effect relationship between context and outcomes.  
- **The Hero's Journey / Pixar Framework**: Highly effective for macro-level lifecycle orchestrations (platform adoptions, transformations).  
- **The Three-Act Structure & StoryBrand**: Positions the consumer as the Hero and the Platform Engineering team as the Guide utilizing the defined approach.  
- **Micro-Narratives (ABT and PAS)**: Shorter frameworks (And/But/Therefore) designed for rapid, highly persuasive daily execution updates.

### 10.3 Bibliographic Citations and Reference Management

The schema provides native support for bibliographic references through the Citation type, enabling practices and methods to establish authoritative provenance and intellectual lineage. Citations are first-class objects within the Practice Language, ensuring proper attribution and enabling knowledge graph integration.

**Citation Structure**: Each Citation must define a unique name (serving as the citation identifier), a description, an authors array (minimum one author), a publication date, and a source (publisher, journal, or retrieval URL). The name property acts as the symbolic key for cross-referencing within narratives and other elements.

**Citation Scope and Aggregation**: Citations can be defined at multiple levels of the methodology hierarchy. PracticeBaseline documents may declare foundational citations for core concepts. Practice documents can add domain-specific citations relevant to the practice domain. Method documents aggregate citations from their baseline and constituent practices, providing a unified bibliography for the complete methodology composition.

**Narrative Integration**: The Narrative object supports an optional citationNames array, enabling authors to explicitly link narrative contexts to their supporting literature. Each entry in citationNames must match the name property of a Citation object within the same practice or method scope. This symbolic linking allows operational tooling to generate properly formatted reference lists, validate citation integrity, and support advanced knowledge retrieval patterns.

**Operational Guidance**: When authoring practices, citations should be declared for all external frameworks, research papers, standards documents, and authoritative sources that inform the practice definition. Citation names should use represent the title of the cited work. Tooling implementations must resolve citation references across the practice composition hierarchy, ensuring that narratives can reference citations from dependent practices or the baseline without duplication.

### 10.4 Acknowledgements and Attribution

The schema provides the Acknowledgement type to recognise individuals, groups, or institutions that have contributed to or supported the development of a practice, baseline, or method. Acknowledgements are distinct from Citations — they attribute human contributions and support rather than referencing published works.

**Acknowledgement Structure:**

Each Acknowledgement extends PracticeElement (requiring `name` and `description`) and adds an optional `url` property:

```json
{
  "name": "Jane Smith",
  "description": "Subject matter expert who contributed domain analysis and review of the platform adoption states.",
  "url": "mailto:jane.smith@example.com"
}
```

**Field Definitions:**

- **name** (required): The name of the person, group, or institution being acknowledged
- **description** (required): A brief explanation of the contribution or support provided
- **url** (optional): A contact or profile link — may be a `mailto:` URI, a personal website, or an organisational profile page

**Acknowledgement Scope and Aggregation:**

Acknowledgements can be declared at multiple levels of the methodology hierarchy:

- **PracticeBaseline**: Acknowledge contributors to the foundational baseline (e.g., original framework authors, domain experts who shaped the core ontology)
- **Practice**: Acknowledge contributors to the specific practice extension (e.g., practitioners who provided domain expertise, reviewers, or pilot teams)
- **Method**: Acknowledge contributors at the method composition level, aggregating recognition across the baseline and constituent practices

**Operational Guidance:**

- Use acknowledgements to recognise substantive intellectual contributions, domain expertise, review efforts, or institutional support
- The `name` property should identify the contributor clearly — use full names for individuals, official names for organisations
- The `description` should briefly explain the nature of the contribution (e.g., "Provided security domain expertise during state model design" rather than simply "Helped with the project")
- The `url` property supports various URI schemes: `mailto:` for email, `https://` for web profiles, or any other relevant link
- Acknowledgements are presentation metadata — they do not participate in structural validation or cross-referencing like citations do

**Example: Baseline Acknowledgements**

```json
{
  "acknowledgements": [
    {
      "name": "Platform Engineering Working Group",
      "description": "Collaborative working group that developed and validated the platform adoption state model through industry workshops."
    },
    {
      "name": "Dr. Alex Chen",
      "description": "Academic advisor who reviewed the ontological foundations and alpha-state progression semantics.",
      "url": "https://university.edu/profiles/achen"
    }
  ]
}
```

**Example: Method-Level Acknowledgements**

```json
{
  "acknowledgements": [
    {
      "name": "Acme Corp Platform Team",
      "description": "Pilot team whose real-world adoption experience validated and refined the pattern lifecycle.",
      "url": "mailto:platform-team@acme.example.com"
    }
  ]
}
```

## 11 Visual Assets and Practice Elements

Visual assets (diagrams, templates, icons) enhance practice comprehension and adoption. The Practice Language supports declarative asset references at both the practice/method level and individual element level.

### 11.1 Asset Declaration

Assets are declared in a top-level `assets` array on Practice, PracticeBaseline, or Method objects. Each asset has:

- **`name`** (required): Unique identifier for symbolic referencing
- **`type`** (required): Asset category - `image`, `diagram`, `template`, `icon`, or `font-character`
- **`description`** (optional): Human-readable explanation of what the asset depicts

**File-based assets** use:
- `path`: Relative path to the asset file within the practice bundle (e.g., `assets/diagrams/platform-states.svg`)
- `mimeType`: MIME type (e.g., `image/svg+xml`, `image/png`, `image/jpeg`, `application/pdf`)
- `checksum`: SHA-256 hash for integrity verification (format: `sha256:...`)
- `url`: External URL for remote hosting
- `dataUri`: Base64-encoded data URI for embedded small assets (<10KB)

**Font character assets** use:
- `fontFamily`: Font library name (e.g., `Font Awesome 6 Free`, `Material Icons`)
- `fontCharacter`: Character identifier (e.g., `fa-cog`, `settings`, ``)
- `fontWeight`: Font weight (e.g., `400`, `900`, `bold`)

### 11.2 Element-Level Asset References

Any practice element (Alpha, State, WorkProduct, LevelOfDetail, Activity, Pattern, etc.) can reference assets via the `assetNames` property — an array of `AssetReference` objects. Each `AssetReference` contains an `assetName` (symbolic link to an `Asset.name` in the top-level `assets` array) and a `type` that classifies how the asset is used in context:

- **`icon`**: UI markers, visual identity (alpha icons, competency badges, activity type indicators)
- **`illustrative`**: Documentation diagrams, architecture visualizations, workflow charts
- **`template`**: Reusable documents, forms, decision records
- **`diagram`**: Technical architecture, state progression, pattern orchestration

An element may reference multiple assets with different semantic types (e.g., an icon and a diagram for the same alpha).

**Example**:
```json
{
  "alphas": [
    {
      "name": "Platform",
      "description": "Platform infrastructure capability",
      "assetNames": [
        { "assetName": "platform-icon", "type": "icon" },
        { "assetName": "platform-state-diagram", "type": "diagram" }
      ],
      "states": [...]
    }
  ],
  "activities": [
    {
      "name": "Design Architecture",
      "description": "Create platform architecture",
      "assetNames": [
        { "assetName": "design-activity-icon", "type": "icon" },
        { "assetName": "architecture-template", "type": "template" }
      ]
    }
  ],
  "assets": [
    {
      "name": "platform-state-diagram",
      "description": "State progression for Platform alpha",
      "type": "diagram",
      "path": "assets/diagrams/platform-states.svg",
      "mimeType": "image/svg+xml",
      "checksum": "sha256:abc123..."
    },
    {
      "name": "architecture-template",
      "description": "Architecture decision record template",
      "type": "template",
      "url": "https://example.com/templates/adr.pdf"
    },
    {
      "name": "team-icon",
      "description": "Team collaboration icon",
      "type": "font-character",
      "fontFamily": "Font Awesome 6 Free",
      "fontCharacter": "fa-users",
      "fontWeight": "900"
    }
  ]
}
```

### 11.3 Common Asset Use Cases

1. **Pattern Diagrams**: Visual workflows showing alpha progression across PatternViews
   - Referenced by: Pattern elements
   - Format: SVG (preferred for scalability and editing)

2. **Alpha State Diagrams**: State machine diagrams showing transitions and gates
   - Referenced by: Alpha elements
   - Format: SVG or PNG

3. **Work Product Templates**: Example documents, spreadsheets, or diagrams
   - Referenced by: WorkProduct or LevelOfDetail elements
   - Format: PNG, PDF, SVG

4. **Activity Flowcharts**: Process flows for complex activities
   - Referenced by: Activity elements
   - Format: SVG (preferred for workflow diagrams)

5. **Architecture Diagrams**: Reference architectures for Solution focus elements
   - Referenced by: Alpha, WorkProduct, or Pattern elements
   - Format: SVG, PNG

6. **Value Stream Maps**: For Value focus patterns and activities
   - Referenced by: Pattern or Activity elements
   - Format: SVG, PNG

7. **Practice Icons**: Visual identity for practices in tooling
   - Referenced by: Practice metadata
   - Format: SVG (preferred for UI rendering)

### 11.4 Distribution and Bundling

Assets support multiple distribution models:

1. **Package Distribution**: Practice Language documents + `assets/` directory packaged as a `.keleo` archive
2. **Single-File Distribution**: Small assets embedded as data URIs within JSON
3. **Remote Hosting**: Assets hosted externally, referenced by URL
4. **Font Characters**: Icon fonts loaded separately, referenced by family/character

**Package Format (`.keleo`):**

Practice Language documents with file-based assets are distributed as `.keleo` packages — ZIP archives (MIME type `application/vnd.keleo.package+zip`) with a defined internal structure and a `manifest.json` describing the package contents. A package can contain any root type (practices, baselines, methods, projects) and supports externalised practice distribution where the merge algorithm resolves symbolic name references from the package's document inventory.

For the complete specification — including manifest schema, directory layout, validation rules, and package resolution — see [specifications/packaging.md](../specifications/packaging.md). The manifest schema is defined as `$defs/PackageManifest` in `language.schema.json`.

**Package as Library:**

When a Method uses `practiceNames` or `baselinePracticeName` string references, the merge algorithm requires a library lookup index (see [merge.md](merge.md), Section 2.3). A `.keleo` package serves as such a library: its manifest maps document names to file paths, enabling the merge algorithm to resolve names to document bodies without external configuration.

**Asset Embedding (Alternative):**

For documents requiring single-file distribution, small assets (icons, simple diagrams) can be embedded using data URIs in the `dataUri` field:

```json
{
  "name": "practice-icon",
  "description": "Practice identity icon",
  "dataUri": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53...",
  "mimeType": "image/svg+xml",
  "checksum": "sha256:abc123..."
}
```

This approach maintains single-file portability while supporting asset references. However, file-based assets (packaged in a `.keleo` archive) are recommended for:

- Assets larger than 10KB
- Assets that change frequently
- Binary formats (PNG, JPEG, PDF)
- Practices under version control

### 11.5 Validation Rules

- Asset names must be unique within the practice
- All `assetName` values within `AssetReference` objects must resolve to a defined asset in the `assets` array
- Asset paths must be relative (no absolute paths or URLs in the `path` field)
- Checksums should be validated when loading the bundle
- Missing asset files should generate validation warnings (not errors, to support partial bundles)

### 11.6 Semantic Guidance

- **Multiple assets per element**: Each element can reference multiple assets via `assetNames` array, each with a semantic `type` classification
- **Asset names must be unique**: Within a practice or method, asset names are unique identifiers
- **Optional integrity verification**: `checksum` enables validation that downloaded/extracted assets match expected content
- **Accessibility**: Include meaningful `description` fields to support alternative text for visual assets

Assets are **optional metadata** that enhance practices but are never required for core functionality. Practices without assets remain fully valid.

### 11.7 Phase 2 Translation Guidance

When generating mapping guides, identify visual artifacts in source materials:

- Architecture diagrams
- State transition diagrams
- Workflow visualizations
- Example templates or screenshots
- Process maps

Document these as asset references in the mapping guide, with descriptions and proposed paths. Phase 3 JSON generation populates the `assets` array and links elements via `assetNames` (array of `AssetReference` objects with `assetName` and `type`).

### 11.8 Best Practices

- **Use SVG for diagrams**: Scalable, editable, text-based (git-friendly)
- **Include alt text**: Asset descriptions serve as accessibility text
- **Organize by type**: Group assets in subdirectories (diagrams, templates, icons)
- **Version assets**: Update checksums when assets change
- **Minimize file sizes**: Compress images, optimize SVGs
- **Document asset sources**: If diagrams use specific tools (draw.io, PlantUML), include source files

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
- `started` and `finished` (both optional) record when the member joined and left the project, supporting temporal membership tracking without overcomplicating the structure

**CommunicationChannel** — a team interaction point:

- `name` provides a human-readable label (e.g. "Slack", "Team Email", "Weekly Sync")
- `address` provides the channel's location (e.g. "#platform-eng", "platform@example.com", "Tuesdays 10:00 UTC")

**Validation:** All `personaName` entries in TeamMember objects must reference Personas defined in the resolved practice/method scope.

### 12.3 Plan Section and Pattern Ownership

The `plan` section establishes the project's lifecycle objectives. It contains an embedded Pattern (a new instance, not a symbolic link) and a notes array for plan-level commentary.

**Pattern as Project-Owned Declaration:** The plan's Pattern is a full declaration using the existing Pattern type, owned by the project and freely modifiable by the user. As a new instance rather than a reference, users can add, remove, or reorder PatternViews, adjust alpha state targets, and extend the pattern with objectives specific to their project. The Pattern type is extended with optional `alphaInstanceNames` and `workProductInstanceNames` arrays, allowing the Pattern to explicitly declare which instances are being tracked.

**Instance Declaration Vocabulary:** The Pattern's `alphaInstanceNames` array declares the alpha instances tracked by this project (e.g. "Platform Engineering Team" as an instance of the "Team" alpha). The `workProductInstanceNames` array declares the work product instances. These declarations provide the vocabulary that the Pattern's views reference when specifying phased objectives via AlphaInstance and WorkProductInstance objects.

**Plan Notes:** The plan's `notes` array captures changes, updates, and rationale about the planning process itself — commentary that is about the plan rather than part of the plan content (which lives in the Pattern).

**Tooling Guidance:** Systems supporting this schema should allow users to clone an existing Pattern from the resolved practice/method scope as a starting point for their plan. The cloned Pattern becomes an independent copy owned by the project. Tooling should ensure all tracked items are represented as AlphaInstanceName or WorkProductInstanceName declarations within the Pattern, defaulting instance names to names derived from the alpha/work product name when the user has not explicitly named them.

### 12.4 Current, Target, and Cycles

The `current`, `target`, and `cycles` sections serve complementary purposes:

- **Current** provides an assessed statement of the current status — "where are we now?" Its checklist states declare what has been completed, what remains, and what will not be completed.
- **Target** provides a statement of intent — "where do we want to be?"
- **Cycles** track the operational work — "what are we doing to get there?" (see Section 12.7)

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

### 12.6 Notes, External Links, and Automated Journaling

The Note type provides timestamped commentary throughout the Project structure:

- `name` — short summary or title
- `timestamp` — ISO timestamp string (consistent with `createdAt`/`updatedAt` elsewhere in the schema)
- `content` — the note text (keep brief — see guidance below)
- `links` — optional array of ExternalLink objects referencing external resources

**Brevity Intent:** Notes are intended to be kept brief — a concise summary capturing the key decision, observation, or outcome. Detailed supporting material (meeting transcripts, lengthy analysis, design documents) should not be inlined into the `content` field. Instead, use the `links` array to reference those longer documents by URI. This keeps the project document lightweight and navigable while preserving full traceability to source material.

**ExternalLink Structure:**

The ExternalLink type provides a reusable reference to an external document or resource. It is used throughout the schema wherever an array of described external references is needed — on Notes, instance declarations, and instance tracking entries.

- `name` — short label identifying the linked resource (e.g., "Sprint Backlog", "Architecture Decision Record", "Team Charter")
- `description` — optional explanation of what this resource contains or why it is linked
- `uri` — optional URI of the external resource, when available

**Example: Note with Links**

```json
{
  "name": "Architecture decision: event-driven messaging",
  "timestamp": "2026-07-25T14:30:00Z",
  "content": "Team agreed to adopt event-driven messaging for inter-service communication. Key driver was decoupling deployment cycles between platform and consumer teams.",
  "links": [
    {
      "name": "Architecture Review Meeting Transcript",
      "uri": "https://docs.example.com/meetings/2026-07-25-arch-review"
    },
    {
      "name": "ADR-042: Event-Driven Messaging",
      "description": "Architecture decision record for the event-driven messaging approach",
      "uri": "https://wiki.example.com/adrs/042-event-driven-messaging"
    }
  ]
}
```

Notes appear at multiple levels: at the project top level, within `plan`, `current`, `target`, `cycles`, `team`, and on individual ChecklistState entries. This multi-level placement enables commentary to be captured at the appropriate level of specificity — from project-wide decisions down to rationale for a single checklist item's state.

**ExternalLink Usage Across Types:**

ExternalLink is used on instance types at two levels, mirroring the declaration-vs-tracking split described in Sections 6.5 and 7.3:

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

## 13 Change Requests

The ChangeRequest type provides a pull-request-like mechanism for proposing, reviewing, and applying changes to Practice Language documents (baselines, practices, and methods). It enables structured change management across the practice lifecycle — from initial proposal through review to acceptance or rejection.

### 13.1 Purpose and Scope

A ChangeRequest is a meta-document that describes a set of proposed changes to a target Practice Language document. It is NOT a practice element — it does not extend PracticeElement and its identity is `changeId`, not `name`. ChangeRequests target methodology definitions only (`practiceBaseline`, `practice`, `method`); Projects are execution instances and are not targets for change requests.

Key capabilities:
- **Atomic bundling**: All operations in a ChangeRequest are grouped together and applied as a unit
- **Review workflow**: Status lifecycle tracks the proposal through draft, review, acceptance, or rejection
- **Temporary preview**: Operations can be temporarily applied during method composition to preview the effect without committing changes
- **Downstream propagation**: Advisory metadata identifies dependent documents that would need refactoring if the change is accepted

### 13.2 Identity and Root Discrimination

The `changeId` property serves as the ChangeRequest's unique identifier and its root-level discriminating property. The schema's if/then/else chain checks for `changeId` first, before all other root types.

**changeId Convention:**

The changeId is a human-readable pseudo-UUID derived from the author's name and a timestamp. The convention is:

```
author-slug-YYYYMMDD-HHMMSS
```

Examples:
- `eseymour-20260729-143022`
- `john-doe-20260729-160000`
- `platform-team-20260801-091500`

The schema enforces the pattern `^[a-z0-9]+(-[a-z0-9]+)*-[0-9]{8}-[0-9]{6}$`. The changeId must be unique within the scope of the target document's lifecycle.

**Supersedes Chain:**

When a rejected or withdrawn change request is revised, the author creates a new ChangeRequest with a new `changeId` and sets the `supersedes` property to the old `changeId`. This creates a traceable revision chain without mutating historical records.

### 13.3 Operation Types and Semantics

The `operations` array contains an ordered sequence of ChangeOperation objects. Each operation targets a specific element type and element name within the target document. Operations are applied in sequence — order matters (e.g., an add must precede any modify of the same element within one ChangeRequest).

The `elementType` field uses free strings matching the JSON storage name convention established by `PracticeElementAlias.practiceElementType` (e.g., `"Alpha"`, `"WorkProduct"`, `"Activity"`, `"ActivitySpace"`, `"Pattern"`, `"Persona"`, `"Focus"`, `"Competency"`).

#### Add Operation

Adds a new practice element to the target document. The `element` field contains the full element definition as a JSON object. Validation of the element's internal structure against its type-specific schema (e.g., Alpha requires states, WorkProduct requires levelsOfDetail) is a tooling concern, not enforced by the ChangeOperation schema itself.

```json
{
  "operation": "add",
  "elementType": "Alpha",
  "elementName": "Supply Chain Security",
  "rationale": "The baseline lacks a dedicated alpha for software supply chain security posture.",
  "element": {
    "name": "Supply Chain Security",
    "description": "The maturity and assurance level of the software supply chain.",
    "focusName": "Solution",
    "contributesTo": "Platform Governance",
    "states": [
      { "name": "Identified", "description": "Supply chain risks catalogued", "seq": 1, "checklist": [] },
      { "name": "Controlled", "description": "Provenance tracking in place", "seq": 2, "checklist": [] },
      { "name": "Verified", "description": "Build integrity validated end-to-end", "seq": 3, "checklist": [] }
    ]
  }
}
```

#### Modify Operation

Modifies properties of an existing practice element. The `modifications` field contains a partial overlay — only the fields present are affected. **Override semantics** apply: provided scalar fields replace existing values. This explicitly differs from the merge algorithm — descriptions CAN be changed, because a ChangeRequest represents a deliberate proposed change, not an accidental overlay. For array fields within modifications, the same union-by-name strategy as the merge algorithm applies (arrays are merged, not replaced wholesale).

```json
{
  "operation": "modify",
  "elementType": "Alpha",
  "elementName": "Platform",
  "rationale": "Add cloud-native criteria to the Architecture Selected state.",
  "modifications": {
    "states": [
      {
        "name": "Architecture Selected",
        "checklist": [
          { "seq": 4, "name": "Cloud-native patterns evaluated", "description": "Containerisation, serverless, and managed service options assessed" }
        ]
      }
    ]
  }
}
```

#### Remove Operation

Removes an existing practice element from the target document. Tooling should validate that removal does not leave dangling symbolic references (e.g., removing an alpha that is referenced in AlphaContributions, or an activity space that activities belong to).

```json
{
  "operation": "remove",
  "elementType": "Activity",
  "elementName": "Manual Infrastructure Provisioning",
  "rationale": "Superseded by automated provisioning activity."
}
```

#### Rename Operation (Disruptive — Prefer Alias)

Renames an existing practice element by changing its identity key (the `name` property). This is the most disruptive operation because names are used as symbolic references throughout the Practice Language — in AlphaContributions, AlphaRelationships, focusName links, activitySpaceName links, WorkProductContributions, and during practice composition/merge.

**The `referenceUpdates` array MUST be exhaustive** — it must list every structural reference to the old name within the target document's scope. Each ReferenceUpdate identifies the element containing the reference, the field, and the from/to values. Tooling should validate that no references to the old name remain after all updates are applied.

**Prefer adding a PracticeElementAlias (via an add operation) over renaming.** Use rename only when the canonical name itself must change (e.g., the name is incorrect, misleading, or conflicts with another element). When the goal is simply to present a different term to users, an alias preserves structural integrity while providing user-friendly terminology.

```json
{
  "operation": "rename",
  "elementType": "ActivitySpace",
  "elementName": "Architect and Build the Foundation",
  "newName": "Design and Build the Foundation",
  "rationale": "'Architect' is overloaded; 'Design' better reflects iterative work.",
  "referenceUpdates": [
    {
      "elementType": "Activity",
      "elementName": "Deploy Infrastructure",
      "field": "activitySpaceName",
      "fromValue": "Architect and Build the Foundation",
      "toValue": "Design and Build the Foundation"
    },
    {
      "elementType": "PatternView",
      "elementName": "Foundation Build",
      "field": "activitySpaces",
      "fromValue": "Architect and Build the Foundation",
      "toValue": "Design and Build the Foundation"
    }
  ]
}
```

#### Adding Aliases (Preferred Over Rename)

To add an alias, use an `add` operation with `elementType: "PracticeElementAlias"`. This adds a PracticeElementAlias to the target document's `practiceElementAliases` array — a presentation-layer alias without changing the structural identity of the element. The alias follows the strict isolation rules defined in Section 4.3: the aliasName is used only for presentation and NEVER appears in structural references.

```json
{
  "operation": "add",
  "elementType": "PracticeElementAlias",
  "elementName": "Platform → Developer Platform",
  "rationale": "Organisation uses 'Developer Platform' to distinguish from infrastructure platforms.",
  "element": {
    "practiceElementType": "Alpha",
    "practiceElementName": "Platform",
    "aliasName": "Developer Platform"
  }
}
```

### 13.4 Status Lifecycle

The `status` field tracks the ChangeRequest through its review lifecycle:

```
draft ──→ proposed ──→ accepted
                    ├─→ rejected
                    └─→ withdrawn

draft ──→ withdrawn (author cancels before submitting)
```

- **draft**: Being authored, not yet submitted for review
- **proposed**: Submitted for review; visible to reviewers; eligible for temporary merge preview
- **accepted**: Approved and ready for permanent application to the target document
- **rejected**: Reviewed and declined; the change will not be applied
- **withdrawn**: Retracted by the author at any point before acceptance or rejection

If a rejected or withdrawn ChangeRequest is revised, the author creates a new ChangeRequest with a new `changeId` and sets `supersedes` to the old `changeId`. This preserves the historical record while creating a clean revision chain.

The `reviewNotes` array captures timestamped commentary from the review process — reviewer feedback, discussion outcomes, and revision rationale. Each entry is a Note object with optional links to supporting materials.

### 13.5 Temporary Merge Preview

One of the key capabilities of the ChangeRequest is temporary merge preview — allowing end users to see what a practice, baseline, or method would look like with the proposed changes applied, without permanently committing those changes.

**How it works** (tooling behaviour, not schema concern):

1. Take the target document and a ChangeRequest with status `proposed` or `accepted`
2. Apply the ChangeRequest's operations in sequence to produce a preview document:
   - **add**: Insert the element into the appropriate array (including PracticeElementAlias additions into the practiceElementAliases array)
   - **modify**: Deep-overlay the modifications onto the matched element (override semantics)
   - **remove**: Remove the matched element from its array
   - **rename**: Change the element's name and apply all referenceUpdates
3. If composing a method, run the standard merge algorithm on the preview document
4. The preview is ephemeral — it is not persisted or committed

This enables stakeholders to evaluate proposed changes in context before committing to them, particularly useful for changes that affect multiple interconnected elements.

### 13.6 Name Changes and Downstream Accommodation

When a ChangeRequest renames elements, any practice or method that depends on the target document needs to know what changed. The `nameChanges` array serves as a notice to dependents:

> **If you depend on `targetDocumentName`, accommodate the following name changes.**

Each entry records:

- **elementType**: The type of element renamed (e.g., `"Alpha"`, `"ActivitySpace"`)
- **fromName**: The previous name
- **toName**: The new name

A dependent practice or method reads this list and checks its own references. For example, if a practice references an alpha called `"Platform Capability"` from the target document, and the nameChanges list says that alpha is now called `"Platform Service"`, the practice author knows to update their reference.

```json
{
  "nameChanges": [
    {
      "elementType": "ActivitySpace",
      "fromName": "Architect and Build the Foundation",
      "toName": "Design and Build the Foundation"
    },
    {
      "elementType": "Alpha",
      "fromName": "Platform Capability",
      "toName": "Platform Service"
    }
  ]
}
```

Read as: *"If your practice or method depends on this document, the ActivitySpace formerly called 'Architect and Build the Foundation' is now 'Design and Build the Foundation', and the Alpha formerly called 'Platform Capability' is now 'Platform Service'. Check your references and update accordingly."*

**Relationship to RenameOperation:** A rename operation's `referenceUpdates` handle cascading references *within* the target document. The `nameChanges` array is the external-facing notice — it tells dependents what changed so they can update their own references independently.

### 13.7 Validation Rules

1. `changeId` must match the pattern `^[a-z0-9]+(-[a-z0-9]+)*-[0-9]{8}-[0-9]{6}$` and be unique within the target document's lifecycle
2. `targetDocumentName` must reference an existing document of the specified `targetDocumentType`
3. `operations` must contain at least one operation
4. For `add` operations: `elementName` must not already exist in the target document for the given `elementType`
5. For `modify`, `remove`, `rename` operations: `elementName` must exist in the target document for the given `elementType`
6. For `rename` operations: `referenceUpdates` must be exhaustive — every structural reference to the old name within the target document must be listed
7. For `add` operations adding a PracticeElementAlias: the resulting alias must not duplicate an existing alias with the same composite key (practiceElementType + practiceElementName + aliasName)
8. `supersedes` (if present) must reference the `changeId` of an existing ChangeRequest for the same `targetDocumentName`
9. Status transitions must follow the defined lifecycle (Section 13.4)
10. `nameChanges` entries should correspond to rename operations within the same ChangeRequest

### 13.8 Change Sets

A ChangeSet batches multiple ChangeRequests into a single reviewable unit. This is useful when related changes span multiple target documents — for example, adding an alpha to a baseline and simultaneously updating dependent practices to reference it.

**Structure:**

- `changeSetId` — human-readable pseudo-UUID (same convention as changeId)
- `status` — lifecycle status covering the entire batch (draft, proposed, accepted, rejected, withdrawn)
- `note` — describes the cohesive rationale for grouping these changes together
- `authors`, `createdAt`, `updatedAt` — provenance metadata
- `changeRequests` — ordered array of ChangeRequest objects (at least one)
- `reviewNotes` — optional review commentary for the set as a whole

**Batch Semantics:**

When a ChangeSet is accepted, all contained ChangeRequests are accepted together. When rejected, all are rejected. This ensures atomicity across documents — a baseline change and its corresponding practice updates are applied as a unit or not at all.

Individual ChangeRequests within a ChangeSet retain their own `status` field for granular tracking during review, but the ChangeSet's `status` governs the overall outcome.

**Root Discrimination:**

A ChangeSet is discriminated at root level by the presence of `changeSetId` (checked before `changeId`). This means a document with `changeSetId` is always a ChangeSet, never a standalone ChangeRequest.

**Example:**

```json
{
  "changeSetId": "eseymour-20260729-150000",
  "status": "proposed",
  "note": {
    "name": "Supply chain security across baseline and practices",
    "timestamp": "2026-07-29T15:00:00Z",
    "content": "Adds supply chain security to the baseline and updates DevSecOps practice to reference it."
  },
  "authors": ["E. Seymour"],
  "createdAt": "2026-07-29T15:00:00Z",
  "updatedAt": "2026-07-29T15:00:00Z",
  "changeRequests": [
    {
      "changeId": "eseymour-20260729-150001",
      "targetDocumentName": "Platform Adoption Kernel",
      "targetDocumentType": "practiceBaseline",
      "status": "proposed",
      "note": {
        "name": "Add supply chain security alpha",
        "timestamp": "2026-07-29T15:00:01Z",
        "content": "Adds a new alpha to the baseline."
      },
      "authors": ["E. Seymour"],
      "createdAt": "2026-07-29T15:00:01Z",
      "updatedAt": "2026-07-29T15:00:01Z",
      "operations": [
        {
          "operation": "add",
          "elementType": "Alpha",
          "elementName": "Supply Chain Security",
          "element": {
            "name": "Supply Chain Security",
            "description": "Software supply chain security posture.",
            "focusName": "Solution",
            "contributesTo": "Platform Governance",
            "states": [
              { "name": "Identified", "description": "Risks catalogued", "seq": 1, "checklist": [] },
              { "name": "Controlled", "description": "Policies in place", "seq": 2, "checklist": [] },
              { "name": "Verified", "description": "Validated end-to-end", "seq": 3, "checklist": [] }
            ]
          }
        }
      ]
    },
    {
      "changeId": "eseymour-20260729-150002",
      "targetDocumentName": "DevSecOps",
      "targetDocumentType": "practice",
      "status": "proposed",
      "note": {
        "name": "Reference new supply chain alpha",
        "timestamp": "2026-07-29T15:00:02Z",
        "content": "Updates the DevSecOps practice to reference the new baseline alpha."
      },
      "authors": ["E. Seymour"],
      "createdAt": "2026-07-29T15:00:02Z",
      "updatedAt": "2026-07-29T15:00:02Z",
      "operations": [
        {
          "operation": "modify",
          "elementType": "Activity",
          "elementName": "Implement Security Controls",
          "modifications": {
            "contributesTo": [
              { "alphaName": "Supply Chain Security", "stateName": "Controlled" }
            ]
          }
        }
      ]
    }
  ]
}
```

### 13.9 Packaging

ChangeRequests and ChangeSets can be included in .keleo packages by adding entries with `documentType: "changeRequest"` or `documentType: "changeSet"` to the PackageDocument inventory. This enables distribution of proposed changes alongside the documents they target.

A package might contain both the target document and one or more ChangeRequests for it, or a package might contain only ChangeRequests intended to be applied against documents from a dependency package. ChangeSets that span multiple target documents are a natural fit for packages that bundle a baseline with its extension practices.

### 13.10 Complete ChangeRequest Example

The following ChangeRequest proposes three changes to a Platform Adoption baseline: adding a supply chain security alpha, adding an activity space alias, and modifying an existing alpha's checklist:

```json
{
  "changeId": "eseymour-20260729-143022",
  "targetDocumentName": "Platform Adoption Kernel",
  "targetDocumentType": "practiceBaseline",
  "status": "proposed",
  "note": {
    "name": "Add supply chain security alpha and modernise activity space naming",
    "timestamp": "2026-07-29T14:30:22Z",
    "content": "Adds a Supply Chain Security alpha reflecting the growing importance of software supply chain integrity. Also aliases 'Architect and Build the Foundation' to 'Design and Build' for better alignment with iterative practices. A rename is avoided to preserve structural references across dependent practices.",
    "links": [
      {
        "name": "Supply Chain Security RFC",
        "uri": "https://wiki.example.com/rfcs/supply-chain-security"
      },
      {
        "name": "SLSA Framework",
        "uri": "https://slsa.dev/"
      }
    ]
  },
  "authors": ["E. Seymour"],
  "createdAt": "2026-07-29T14:30:22Z",
  "updatedAt": "2026-07-29T14:30:22Z",
  "operations": [
    {
      "operation": "add",
      "elementType": "Alpha",
      "elementName": "Supply Chain Security",
      "rationale": "The baseline lacks a dedicated alpha for software supply chain security posture.",
      "element": {
        "name": "Supply Chain Security",
        "description": "The maturity and assurance level of the software supply chain, from dependency provenance through build integrity to deployment attestation.",
        "focusName": "Solution",
        "contributesTo": "Platform Governance",
        "states": [
          {
            "name": "Identified",
            "description": "Supply chain risks and components catalogued",
            "seq": 1,
            "checklist": [
              { "seq": 1, "name": "Dependency inventory created", "description": "All direct and transitive dependencies catalogued with provenance" }
            ]
          },
          {
            "name": "Controlled",
            "description": "Provenance tracking and dependency policies in place",
            "seq": 2,
            "checklist": [
              { "seq": 1, "name": "Dependency policy enforced", "description": "Automated gates block unapproved or vulnerable dependencies" }
            ]
          },
          {
            "name": "Verified",
            "description": "Build integrity and attestation validated end-to-end",
            "seq": 3,
            "checklist": [
              { "seq": 1, "name": "SLSA Level 2 achieved", "description": "Build provenance generated and verified for all production artifacts" }
            ]
          }
        ]
      }
    },
    {
      "operation": "add",
      "elementType": "PracticeElementAlias",
      "elementName": "Architect and Build the Foundation → Design and Build",
      "rationale": "'Architect' is overloaded; alias preserves structural integrity while providing clearer terminology.",
      "element": {
        "practiceElementType": "ActivitySpace",
        "practiceElementName": "Architect and Build the Foundation",
        "aliasName": "Design and Build"
      }
    },
    {
      "operation": "modify",
      "elementType": "Alpha",
      "elementName": "Platform",
      "rationale": "Link the Baselined state to supply chain security evidence.",
      "modifications": {
        "states": [
          {
            "name": "Baselined",
            "checklist": [
              {
                "seq": 5,
                "name": "Supply chain security baseline established",
                "description": "Dependency provenance and build integrity controls in place"
              }
            ]
          }
        ]
      }
    }
  ],
  "reviewNotes": [
    {
      "name": "Initial review feedback",
      "timestamp": "2026-07-29T16:00:00Z",
      "content": "Reviewer agreed with alias over rename for activity space. Suggested adding SLSA checklist items to the Verified state.",
      "links": []
    }
  ]
}
```

## 14 Acyclicity Constraints and Circular Reference Protection

Several properties in the Practice Language create directed graphs — hierarchies, containment trees, dependency chains, and prerequisite networks. When these graphs contain cycles, the consequences range from infinite loops during traversal (crashing parsers and renderers) to deadlocked prerequisite chains (states that can never be achieved) to security vulnerabilities (stack overflow exploits via crafted documents). This section consolidates all acyclicity constraints into a single authoritative reference and defines the implementation requirements for consuming software.

**Governing Principle:** Every directed reference graph formed by the properties listed below MUST be a Directed Acyclic Graph (DAG). A cycle at any level — direct (A→A), mutual (A→B→A), or transitive (A→B→C→A) — is a validation error. This constraint is absolute and applies at authoring time, merge time, and runtime.

### 14.1 Hierarchical Properties Subject to Acyclicity Constraints

The following properties create parent-child or containment hierarchies. Each forms an independent DAG that must be validated separately.

#### 14.1.1 Alpha Specialization Hierarchy (`Alpha.contributesTo`)

**Property:** `Alpha.contributesTo` — string naming a parent alpha.

**Graph:** Each alpha with `contributesTo` set forms an edge from child to parent. The resulting graph across all alphas in scope (baseline + practice + dependencies) must be acyclic.

**Invalid Examples:**
- **Self-reference:** Alpha "Platform" with `contributesTo: "Platform"`
- **Mutual:** Alpha "A" contributesTo "B", Alpha "B" contributesTo "A"
- **Transitive:** Alpha "A" contributesTo "B", "B" contributesTo "C", "C" contributesTo "A"

**Constraint:** For any alpha X, walking the `contributesTo` chain must terminate at an alpha with no `contributesTo` property (a root alpha). The chain must never revisit a previously visited alpha.

#### 14.1.2 Alpha Variant Mapping Hierarchy (`Alpha.mapsTo`)

**Property:** `Alpha.mapsTo` — string naming a parent alpha that this alpha is a variant of.

**Graph:** Each alpha with `mapsTo` set forms an edge from variant to parent. The resulting graph must be acyclic.

**Invalid Examples:**
- **Self-reference:** Alpha "Sales Play" with `mapsTo: "Sales Play"`
- **Mutual:** Alpha "A" mapsTo "B", Alpha "B" mapsTo "A"

**Constraint:** Identical to `contributesTo` — the chain must terminate at a root alpha without revisiting any node.

#### 14.1.3 Mixed `contributesTo`/`mapsTo` Chains

Because `contributesTo` and `mapsTo` are mutually exclusive on a single alpha but both reference parent alphas, cycles can span both relationship types. The acyclicity constraint applies to the **union** of both edge sets.

**Invalid Example:**
- Alpha "A" contributesTo "B", Alpha "B" mapsTo "C", Alpha "C" contributesTo "A"

**Constraint:** Construct a single directed graph where each alpha with `contributesTo` or `mapsTo` has exactly one outgoing edge to its target. This combined graph must be acyclic.

#### 14.1.4 Work Product Containment Hierarchy (`WorkProduct.partOf`)

**Property:** `WorkProduct.partOf` — string naming a parent work product.

**Graph:** Each work product with `partOf` set forms an edge from child to parent. The resulting graph must be acyclic.

**Invalid Examples:**
- **Self-reference:** WorkProduct "Architecture" with `partOf: "Architecture"`
- **Mutual:** WorkProduct "A" partOf "B", WorkProduct "B" partOf "A"
- **Transitive:** WorkProduct "A" partOf "B", "B" partOf "C", "C" partOf "A"

**Constraint:** For any work product X, walking the `partOf` chain must terminate at a work product with no `partOf` property. The chain must never revisit a previously visited work product.

#### 14.1.5 Work Product Variant Mapping Hierarchy (`WorkProduct.mapsTo`)

**Property:** `WorkProduct.mapsTo` — string naming a parent work product that this work product is a variant of.

**Graph:** Each work product with `mapsTo` set forms an edge from variant to parent. The resulting graph must be acyclic.

**Invalid Examples:**
- **Self-reference:** WorkProduct "Architecture" with `mapsTo: "Architecture"`
- **Mutual:** WorkProduct "A" mapsTo "B", WorkProduct "B" mapsTo "A"

**Constraint:** Identical to `partOf` — the chain must terminate at a root work product without revisiting any node.

#### 14.1.6 Mixed `partOf`/`mapsTo` Chains (Work Products)

Because `partOf` and `mapsTo` are mutually exclusive on a single work product but both reference parent work products, cycles can span both relationship types. The acyclicity constraint applies to the **union** of both edge sets.

**Invalid Example:**
- WorkProduct "A" partOf "B", WorkProduct "B" mapsTo "C", WorkProduct "C" partOf "A"

**Constraint:** Construct a single directed graph where each work product with `partOf` or `mapsTo` has exactly one outgoing edge to its target. This combined graph must be acyclic.

### 14.2 Cross-Element Prerequisite Cycles

Background prerequisites create cross-element dependency graphs that are harder to detect than single-property hierarchies because cycles span multiple element types and properties.

#### 14.2.1 Alpha State Background Prerequisites (`Background.alphaStates`)

**Property:** `Background.alphaStates` on State — declares that achieving this state requires another alpha to have reached a specific state.

**Graph:** Each `Background.alphaStates` entry creates an edge from the declaring state (identified by its owning alpha + state name) to the required state (alphaName + stateName). The resulting graph across all states in scope must be acyclic.

**Invalid Example:**
- Alpha "Platform", state "Provisioned" has background requiring Alpha "Team" at state "Performs"
- Alpha "Team", state "Performs" has background requiring Alpha "Platform" at state "Provisioned"

This creates a deadlock — neither state can ever be achieved because each requires the other first.

**Constraint:** The cross-alpha prerequisite graph formed by all `Background.alphaStates` entries must be a DAG. A state must never be a transitive prerequisite of itself.

#### 14.2.2 Work Product Level Background Prerequisites (`Background.workProductLevels`)

**Property:** `Background.workProductLevels` on State or LevelOfDetail — declares that achieving this state/level requires a work product to have reached a specific level of detail.

**Graph:** Each entry creates an edge from the declaring state or level to the required work product level. Combined with `LevelOfDetail.contributesTo` (which links LODs back to alpha states), cycles can form across element types.

**Invalid Example:**
- Alpha "Platform", state "Provisioned" has background requiring WorkProduct "Architecture" at LOD "Validated"
- WorkProduct "Architecture", LOD "Validated" has background requiring Alpha "Platform" at state "Provisioned"

**Constraint:** The combined prerequisite graph formed by `Background.alphaStates`, `Background.workProductLevels`, and their transitive closures must be a DAG.

#### 14.2.3 Instance-Level Background Prerequisites

**Properties:** `Background.alphaInstanceStates` and `Background.workProductInstanceLevels` on AlphaInstance and WorkProductInstance.

These follow the same acyclicity rules as their abstract counterparts (14.2.1 and 14.2.2) but operate at the instance level within a Project context. Instance-level backgrounds supplement practice-level backgrounds, so cycle detection must consider both layers combined.

#### 14.2.4 State Contribution Mapping (`State.contributesToState`)

**Property:** `State.contributesToState` — string naming a state on the parent alpha (identified by the owning alpha's `contributesTo` or `mapsTo` target).

**Graph:** This property creates edges between states across the alpha hierarchy. Combined with `Background.alphaStates`, cycles can form where state A's background requires state B, and state B's `contributesToState` points back to state A.

**Constraint:** The state-level contribution graph, overlaid with the state-level prerequisite graph, must be acyclic. Tooling should validate both graphs together.

### 14.3 Document Dependency Graphs

Document-level references create dependency graphs that must be acyclic to support resolution ordering.

#### 14.3.1 Baseline Dependencies (`PracticeBaseline.baselinePracticeNames`)

**Property:** `PracticeBaseline.baselinePracticeNames` — array of baseline names this baseline depends on.

**Constraint:** The directed graph formed by baseline dependency edges must be a DAG. Baseline A cannot depend on Baseline B if B (directly or transitively) depends on A.

#### 14.3.2 Practice Dependencies (`Practice.practiceDependencyNames`)

**Property:** `Practice.practiceDependencyNames` — array of practice names this practice depends on.

**Constraint:** The directed graph formed by practice dependency edges must be a DAG. Practice A cannot depend on Practice B if B (directly or transitively) depends on A.

#### 14.3.3 Cross-Layer Dependencies

Practices also reference baselines via `baselinePracticeName`. While a practice depending on a baseline does not typically create a cycle (baselines do not reference practices), tooling should validate the complete resolution graph — baseline dependencies plus practice dependencies plus baseline-to-practice edges — as a single DAG.

### 14.4 Revision Chain Acyclicity

#### 14.4.1 ChangeRequest Supersedes Chain (`ChangeRequest.supersedes`)

**Property:** `ChangeRequest.supersedes` — changeId of a previous ChangeRequest that this one replaces.

**Constraint:** The chain formed by `supersedes` references must be acyclic. A ChangeRequest cannot directly or transitively supersede itself. Self-reference (`supersedes` pointing to the document's own `changeId`) is invalid.

### 14.5 Validation Rules Summary

| Property | Element Type | Graph Type | Acyclicity Scope |
|---|---|---|---|
| `contributesTo` | Alpha | Specialization tree | All alphas in baseline + practice + dependencies |
| `mapsTo` | Alpha | Variant mapping tree | All alphas in baseline + practice + dependencies |
| `contributesTo` + `mapsTo` (combined) | Alpha | Combined parent graph | Union of both edge sets |
| `partOf` | WorkProduct | Containment tree | All work products in baseline + practice + dependencies |
| `mapsTo` | WorkProduct | Variant mapping tree | All work products in baseline + practice + dependencies |
| `partOf` + `mapsTo` (combined) | WorkProduct | Combined parent graph | Union of both edge sets |
| `Background.alphaStates` | State, LevelOfDetail | Cross-alpha prerequisites | All states in scope |
| `Background.workProductLevels` | State, LevelOfDetail | Cross-element prerequisites | All states and LODs in scope |
| `Background.alphaInstanceStates` | AlphaInstance, WorkProductInstance | Instance prerequisites | All instances in project |
| `Background.workProductInstanceLevels` | AlphaInstance, WorkProductInstance | Instance prerequisites | All instances in project |
| `contributesToState` | State | State-level contribution | States across alpha hierarchy |
| `baselinePracticeNames` | PracticeBaseline | Document dependencies | All baselines in registry |
| `practiceDependencyNames` | Practice | Document dependencies | All practices in registry |
| `supersedes` | ChangeRequest | Revision chain | All change requests for target document |

**Validation Order:** Validate acyclicity constraints in this order, as earlier checks enable meaningful later checks:

1. Document dependency graphs (baseline and practice dependencies)
2. Alpha hierarchy (`contributesTo` + `mapsTo` combined)
3. Work product hierarchy (`partOf` + `mapsTo` combined)
4. Cross-element prerequisites (backgrounds)
5. State-level contributions (`contributesToState`)
6. Revision chains (`supersedes`)

### 14.6 Implementation Requirements

Software that parses, validates, traverses, or renders Practice Language documents MUST implement circular reference protection. The full specification — including algorithms, depth limits, error reporting, and security hardening — is defined in [specifications/circular-reference-protection.md](../specifications/circular-reference-protection.md).

**Minimum requirements for all implementations:**

1. **Validate acyclicity** for every property listed in Section 14.5 before performing any traversal or computation that follows reference chains
2. **Enforce depth limits** on all recursive traversals, even after acyclicity validation, as a defense-in-depth measure against malformed data
3. **Track visited nodes** during any graph traversal to detect and halt cycles at runtime
4. **Report errors** with sufficient context to identify the cycle (the chain of element names forming the loop)
5. **Never crash or hang** when processing a document containing circular references — gracefully reject the document with a diagnostic error

## 15 Conclusion

The transformation of organizational endeavors from static, document-driven processes to dynamic, state-driven ecosystems requires a highly rigorous operational architecture. The Practice Language JSON Schema provides the structural capacity to model extreme complexity across any domain. Maximizing its efficacy, however, demands profound semantic guidance. By enforcing strict ontological tagging taxonomies, embedding blocking failure logic and quantitative thresholds into validation checklists, and defining automated mathematical triggers for Alpha state transitions, enterprise architects eliminate process ambiguity. Furthermore, operationalizing the schema through strict physical Work Product URI linking, explicitly linked organizational Persona Groups, and programmatic root-level methodology discrimination ensures that the methodology aligns precisely with operational reality. By orchestrating these elements through conditional Pattern Views tethered to specific cognitive narrative frameworks, this semantic guidance framework transforms the JSON Schema from a mere structural validator into a prescriptive, highly actionable operational engine capable of driving modern hyperscale transformations.

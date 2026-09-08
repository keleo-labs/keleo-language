# **Semantic Guidance and Operational Architecture for the Practice Language JSON Schema**

## Table of Contents

1. [Introduction and Architectural Context](#1-introduction-and-architectural-context)
2. [Ontological Principles and Semantic Integration](#2-ontological-principles-and-semantic-integration)
3. [Method, Practice, and Baseline Architecture](#3-method-practice-and-baseline-architecture)
   - 3.1 [Method Root Type and Discrimination Logic](#31-method-root-type-and-discrimination-logic)
   - 3.2 [Metadata and Provenance](#32-metadata-and-provenance)
   - 3.3 [Schema Versioning and Document Compatibility](#33-schema-versioning-and-document-compatibility)
   - 3.4 [Document Version Format](#34-document-version-format)
4. [Adapting and Composing Practices](semantics/composition.md)
   - 4.1 [Practice Dependencies](semantics/composition.md#41-practice-dependencies)
   - 4.2 [Practice and Method Composition (Merge)](semantics/composition.md#42-practice-and-method-composition-merge)
   - 4.3 [Practice Aliasing and Strict Isolation](semantics/composition.md#43-practice-aliasing-and-strict-isolation)
   - 4.4 [Redeclaration vs Specialization vs Variant Mapping Decision Framework](semantics/composition.md#44-redeclaration-vs-specialization-vs-variant-mapping-decision-framework)
   - 4.5 [Adapting and Extending Practice Elements](semantics/composition.md#45-adapting-and-extending-practice-elements)
   - 4.6 [Practice Partitioning and Value-Driven Scoping](semantics/composition.md#46-practice-partitioning-and-value-driven-scoping)
   - 4.7 [Alpha vs Work Product Decision Framework](semantics/composition.md#47-alpha-vs-work-product-decision-framework)
   - 4.8 [Method-Level Bindings](semantics/composition.md#48-method-level-bindings)
5. [PracticeElement Foundations](semantics/practice-elements.md)
   - 5.1 [PracticeElement, Tagging Taxonomy, and Narrative Anchors](semantics/practice-elements.md#51-practiceelement-tagging-taxonomy-and-narrative-anchors)
   - 5.2 [Checklists and Dynamic State-Gating](semantics/practice-elements.md#52-checklists-and-dynamic-state-gating)
   - 5.3 [Structured Guidance: The Gherkin-Inspired Test Model](semantics/practice-elements.md#53-structured-guidance-the-gherkin-inspired-test-model)
6. [The Alpha-State Trajectory and Dynamic Semantics](semantics/alphas.md)
   - 6.1 [Defining Core Alphas and Baseline Isolation](semantics/alphas.md#61-defining-core-alphas-and-baseline-isolation)
   - 6.2 [State Progression and the Guidance Function](semantics/alphas.md#62-state-progression-and-the-guidance-function)
   - 6.3 [Programmatic Transition Triggers and Alpha Rollups](semantics/alphas.md#63-programmatic-transition-triggers-and-alpha-rollups)
   - 6.4 [Abstract Concepts and Instantiation](semantics/alphas.md#64-abstract-concepts-and-instantiation)
   - 6.5 [Alpha Instance Semantics: Guidance vs Tracking](semantics/alphas.md#65-alpha-instance-semantics-guidance-vs-tracking)
   - 6.6 [Reference Content: Actionable Examples and Reusable Resources](semantics/alphas.md#66-reference-content-actionable-examples-and-reusable-resources)
   - 6.7 [Instance Relationships: Applying Type Edges to Named Instances](semantics/alphas.md#67-instance-relationships-applying-type-edges-to-named-instances)
7. [Evidentiary Verification via Work Product Elements](semantics/work-products.md)
   - 7.1 [Structure of Work Products](semantics/work-products.md#71-structure-of-work-products)
   - 7.2 [Artifact Instantiation and Concurrency](semantics/work-products.md#72-artifact-instantiation-and-concurrency)
   - 7.3 [Work Product Instance Semantics: Guidance vs Evidence Chains](semantics/work-products.md#73-work-product-instance-semantics-guidance-vs-evidence-chains)
   - 7.4 [Work Product Instance Metrics](semantics/work-products.md#74-work-product-instance-metrics)
   - 7.5 [Work Product Composition (`partOf`)](semantics/work-products.md#75-work-product-composition-partof)
   - 7.6 [Work Product Variant Mapping (`mapsTo`)](semantics/work-products.md#76-work-product-variant-mapping-mapsto)
8. [Execution Boundaries and Organizational Roles](semantics/execution-and-patterns.md#8-execution-boundaries-and-organizational-roles)
   - 8.1 [Activity Spaces and Activities](semantics/execution-and-patterns.md#81-activity-spaces-and-activities)
     - 8.1.1 [Gherkin-Inspired Structure on Activities](semantics/execution-and-patterns.md#811-gherkin-inspired-structure-on-activities)
   - 8.2 [Organizational Roles and Persona Definitions](semantics/execution-and-patterns.md#82-organizational-roles-and-persona-definitions)
9. [Lifecycle Orchestration: Patterns and Phase Models](semantics/execution-and-patterns.md#9-lifecycle-orchestration-patterns-and-phase-models)
   - 9.1 [Pattern Orchestration and Narrative Hooks](semantics/execution-and-patterns.md#91-pattern-orchestration-and-narrative-hooks)
   - 9.2 [The PatternView: Complete Structure and Semantics](semantics/execution-and-patterns.md#92-the-patternview-complete-structure-and-semantics)
   - 9.3 [Pattern Groups: Organising Patterns for Navigation](semantics/execution-and-patterns.md#93-pattern-groups-organising-patterns-for-navigation)
   - 9.4 [Outcome Definitions and Value Measurement](semantics/execution-and-patterns.md#94-outcome-definitions-and-value-measurement)
10. [Narrative Management](semantics/narrative-and-assets.md#10-narrative-management)
    - 10.1 [Narrative Tooling Synchronization and Execution Guidelines](semantics/narrative-and-assets.md#101-narrative-tooling-synchronization-and-execution-guidelines)
    - 10.2 [Cognitive Storytelling Frameworks](semantics/narrative-and-assets.md#102-cognitive-storytelling-frameworks)
    - 10.3 [Bibliographic Citations and Reference Management](semantics/narrative-and-assets.md#103-bibliographic-citations-and-reference-management)
    - 10.4 [Acknowledgements and Attribution](semantics/narrative-and-assets.md#104-acknowledgements-and-attribution)
11. [Visual Assets and Practice Elements](semantics/narrative-and-assets.md#11-visual-assets-and-practice-elements)
    - 11.1 [Asset Declaration](semantics/narrative-and-assets.md#111-asset-declaration)
    - 11.2 [Element-Level Asset References](semantics/narrative-and-assets.md#112-element-level-asset-references)
    - 11.3 [Common Asset Use Cases](semantics/narrative-and-assets.md#113-common-asset-use-cases)
    - 11.4 [Distribution and Bundling](semantics/narrative-and-assets.md#114-distribution-and-bundling)
    - 11.5 [Validation Rules](semantics/narrative-and-assets.md#115-validation-rules)
    - 11.6 [Semantic Guidance](semantics/narrative-and-assets.md#116-semantic-guidance)
    - 11.7 [Phase 2 Translation Guidance](semantics/narrative-and-assets.md#117-phase-2-translation-guidance)
    - 11.8 [Best Practices](semantics/narrative-and-assets.md#118-best-practices)
12. [Project Execution Tracking](semantics/project-tracking.md)
    - 12.1 [Project Purpose and Root Discrimination](semantics/project-tracking.md#121-project-purpose-and-root-discrimination)
    - 12.2 [Team Structure and Team API Principles](semantics/project-tracking.md#122-team-structure-and-team-api-principles)
    - 12.3 [Plan Section and Pattern Ownership](semantics/project-tracking.md#123-plan-section-and-pattern-ownership)
    - 12.4 [Current, Target, and Cycles](semantics/project-tracking.md#124-current-target-and-cycles)
    - 12.5 [ChecklistState and Evidence Tracking](semantics/project-tracking.md#125-checkliststate-and-evidence-tracking)
    - 12.6 [Notes, External Links, and Automated Journaling](semantics/project-tracking.md#126-notes-external-links-and-automated-journaling)
    - 12.7 [Cycles and Operational Work Tracking](semantics/project-tracking.md#127-cycles-and-operational-work-tracking)
    - 12.8 [Outcome Instances and Value Tracking](semantics/project-tracking.md#128-outcome-instances-and-value-tracking)
13. [Change Requests](semantics/change-requests.md)
14. [Acyclicity Constraints and Circular Reference Protection](semantics/acyclicity.md)
    - 14.1 [Hierarchical Properties Subject to Acyclicity Constraints](semantics/acyclicity.md#141-hierarchical-properties-subject-to-acyclicity-constraints)
    - 14.2 [Cross-Element Prerequisite Cycles](semantics/acyclicity.md#142-cross-element-prerequisite-cycles)
    - 14.3 [Document Dependency Graphs](semantics/acyclicity.md#143-document-dependency-graphs)
    - 14.4 [Revision Chain Acyclicity](semantics/acyclicity.md#144-revision-chain-acyclicity)
    - 14.5 [Validation Rules Summary](semantics/acyclicity.md#145-validation-rules-summary)
    - 14.6 [Implementation Requirements](semantics/acyclicity.md#146-implementation-requirements)
15. [Conclusion](#15-conclusion)

---

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

---

## 4 Adapting and Composing Practices

Covers all mechanisms for combining and tailoring practices: dependency declarations and version constraints (4.1), merge composition (4.2), aliasing and strict isolation (4.3), the Redeclaration vs Specialization vs Variant Mapping decision framework (4.4), element adaptation and extension (4.5), practice partitioning and value-driven scoping (4.6), the Alpha vs Work Product decision framework (4.7), and Method-level bindings for cross-baseline composition (4.8). Read when designing multi-practice methods, deciding how new concerns relate to baseline elements, or partitioning methodology content into practices.

**Full guidance:** [semantics/composition.md](semantics/composition.md)

---

## 5 PracticeElement Foundations

Defines the universal base properties inherited by all methodology constructs: PracticeElement identification, the orthogonal tagging taxonomy for multi-dimensional classification (5.1), checklists with dynamic state-gating and priority thresholds (5.2), and the Gherkin-inspired structured test model for verification and execution scenarios on states, LODs, checklists, and activities (5.3). Read when authoring practice elements, designing checklists, or adding structured Gherkin guidance.

**Full guidance:** [semantics/practice-elements.md](semantics/practice-elements.md)

---

## 6 The Alpha-State Trajectory and Dynamic Semantics

Defines Alphas (Abstract-Level Progress Health Attributes) — the essential concerns requiring tracking and progression. Covers baseline isolation and the floating alpha prohibition (6.1), state progression and the guidance function (6.2), programmatic transition triggers and alpha rollups (6.3), abstract concepts and expected instantiations (6.4), alpha instance semantics for declaration vs execution tracking (6.5), reference content with actionable examples and reusable resources (6.6), and instance relationships applying type edges to named instances (6.7). Read when defining alphas, designing state progressions, or working with alpha instances.

**Full guidance:** [semantics/alphas.md](semantics/alphas.md)

---

## 7 Evidentiary Verification via Work Product Elements

Defines Work Products — the tangible artifacts providing empirical evidence to validate Alpha state progressions. Covers work product structure and Level of Detail (LOD) progression (7.1), artifact instantiation and concurrency (7.2), work product instance semantics for declaration vs evidence chains (7.3), instance metrics (7.4), containment composition via `partOf` (7.5), and variant mapping via `mapsTo` (7.6). Read when designing work products, defining LOD progressions, or establishing containment/variant relationships between artifacts.

**Full guidance:** [semantics/work-products.md](semantics/work-products.md)

---

## 8 Execution Boundaries and Organizational Roles

Defines the execution model: Activity Spaces as generalized effort boundaries, Activities as specific actionable swimlanes with `worksOn` and competency requirements (8.1), Gherkin-inspired structure on activities for execution scenarios (8.1.1), and organizational Personas and PersonaGroups (8.2). Read when designing activities, defining organizational roles, or adding Gherkin test structures to activities.

**Full guidance:** [semantics/execution-and-patterns.md](semantics/execution-and-patterns.md) — Sections 8-9

---

## 9 Lifecycle Orchestration: Patterns and Phase Models

Defines how methodologies are orchestrated into temporal models using Patterns. Covers pattern orchestration and narrative hooks (9.1), the PatternView structure and semantics including alpha state expectations, instance tracking, deliverables, and active work (9.2), pattern groups for navigation organisation (9.3), and outcome definitions with value measurement and metric/objective contributions (9.4). Read when designing lifecycle patterns, defining phase milestones, organising pattern groups, or establishing outcome measurement.

**Full guidance:** [semantics/execution-and-patterns.md](semantics/execution-and-patterns.md) — Sections 8-9

---

## 10 Narrative Management

Defines how practices include contextual information about practice elements through narratives. Covers narrative naming conventions, content guidelines, and tooling synchronization (10.1), cognitive storytelling frameworks (10.2), bibliographic citations and reference management (10.3), and acknowledgements and attribution (10.4). Read when enriching practice elements with narrative content, adding citations, or working with storytelling frameworks.

**Full guidance:** [semantics/narrative-and-assets.md](semantics/narrative-and-assets.md) — Sections 10-11

---

## 11 Visual Assets and Practice Elements

Defines declarative asset references for diagrams, templates, icons, and other visual content. Covers asset declaration (11.1), element-level asset references (11.2), common use cases (11.3), distribution and bundling (11.4), validation rules (11.5), semantic guidance (11.6), Phase 2 translation guidance (11.7), and best practices (11.8). Read when adding visual assets to practices or establishing element-level asset references.

**Full guidance:** [semantics/narrative-and-assets.md](semantics/narrative-and-assets.md) — Sections 10-11

---

## 12 Project Execution Tracking

Defines the Project type — an execution instance of a Practice or Method that tracks real-world progress. Covers project purpose and root discrimination (12.1), team structure and Team API principles (12.2), plan section and pattern ownership (12.3), current and target state sections (12.4), ChecklistState and evidence tracking with priority thresholds (12.5), notes, external links, and automated journaling (12.6), cycles and operational work tracking (12.7), and outcome instances with value tracking (12.8). Read when working with project documents, tracking execution state, or designing team structures.

**Full guidance:** [semantics/project-tracking.md](semantics/project-tracking.md)

---

## 13 Change Requests

Defines the ChangeRequest type — a pull-request-like mechanism for proposing, reviewing, and applying changes to Practice Language documents. Covers change request identity, operations (add, modify, remove, rename, alias), status lifecycle, temporary merge preview, validation rules, change sets, packaging, and complete worked examples. Read when implementing or using the change request workflow for methodology evolution.

**Full guidance:** [semantics/change-requests.md](semantics/change-requests.md)

---

## 14 Acyclicity Constraints and Circular Reference Protection

Consolidates all acyclicity constraints for directed reference graphs in the Practice Language. Covers hierarchical properties (alpha specialization, variant mapping, WP containment, WP variants) (14.1), cross-element prerequisite cycles (14.2), document dependency graphs (14.3), revision chain acyclicity (14.4), a validation rules summary (14.5), and implementation requirements (14.6). Every directed reference graph must be a DAG — cycles at any level are validation errors. Read when implementing validators or authoring elements with hierarchical relationships. See also the implementation specification in [`specifications/circular-reference-protection.md`](../specifications/circular-reference-protection.md).

**Full guidance:** [semantics/acyclicity.md](semantics/acyclicity.md)

---

## 15 Conclusion

The transformation of organizational endeavors from static, document-driven processes to dynamic, state-driven ecosystems requires a highly rigorous operational architecture. The Practice Language JSON Schema provides the structural capacity to model extreme complexity across any domain. Maximizing its efficacy, however, demands profound semantic guidance. By enforcing strict ontological tagging taxonomies, embedding blocking failure logic and quantitative thresholds into validation checklists, and defining automated mathematical triggers for Alpha state transitions, enterprise architects eliminate process ambiguity. Furthermore, operationalizing the schema through strict physical Work Product URI linking, explicitly linked organizational Persona Groups, and programmatic root-level methodology discrimination ensures that the methodology aligns precisely with operational reality. By orchestrating these elements through conditional Pattern Views tethered to specific cognitive narrative frameworks, this semantic guidance framework transforms the JSON Schema from a mere structural validator into a prescriptive, highly actionable operational engine capable of driving modern hyperscale transformations.

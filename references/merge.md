# Practice and Method Composition: Merge Algorithm Specification

## Table of Contents

1. [Overview](#1-overview)
2. [Dependency Resolution](#2-dependency-resolution)
   - 2.1 [Baseline Dependencies](#21-baseline-dependencies)
   - 2.2 [Practice Dependencies](#22-practice-dependencies)
   - 2.3 [Method Composition Entry Point](#23-method-composition-entry-point)
3. [Merge Hierarchy and Layer Ordering](#3-merge-hierarchy-and-layer-ordering)
   - 3.1 [Accumulator Initialization from Baseline](#31-accumulator-initialization-from-baseline)
   - 3.2 [Extension Practice Overlay](#32-extension-practice-overlay)
   - 3.3 [Embedded Method Recursion](#33-embedded-method-recursion)
4. [Element-Level Merge Rules](#4-element-level-merge-rules)
   - 4.1 [The Core Merge Function](#41-the-core-merge-function)
   - 4.2 [Description Preservation](#42-description-preservation)
   - 4.3 [Scalar Field Handling](#43-scalar-field-handling)
   - 4.4 [Tag Merging](#44-tag-merging)
5. [Array Merge Strategies](#5-array-merge-strategies)
   - 5.1 [Named Element Arrays](#51-named-element-arrays)
   - 5.2 [Contribution Arrays](#52-contribution-arrays)
   - 5.3 [Relationship Arrays](#53-relationship-arrays)
   - 5.4 [WorksOn Arrays](#54-workson-arrays)
   - 5.5 [Competency Level Arrays](#55-competency-level-arrays)
   - 5.6 [Primitive Arrays](#56-primitive-arrays)
6. [Domain-Specific Merge Functions](#6-domain-specific-merge-functions)
   - 6.1 [Alpha Merging](#61-alpha-merging)
   - 6.2 [State and Checklist Merging](#62-state-and-checklist-merging)
   - 6.3 [Activity Space and Activity Merging](#63-activity-space-and-activity-merging)
   - 6.4 [Work Product and Level of Detail Merging](#64-work-product-and-level-of-detail-merging)
   - 6.5 [Pattern and PatternView Merging](#65-pattern-and-patternview-merging)
   - 6.6 [Competency Merging](#66-competency-merging)
   - 6.7 [Persona and PersonaGroup Merging](#67-persona-and-personagroup-merging)
   - 6.8 [Narrative Merging](#68-narrative-merging)
   - 6.9 [Citation Merging](#69-citation-merging)
   - 6.10 [Asset Merging](#610-asset-merging)
   - 6.11 [Alias Merging](#611-alias-merging)
   - 6.12 [Instance Declaration Merging](#612-instance-declaration-merging)
7. [Post-Merge Finalization](#7-post-merge-finalization)
   - 7.1 [Alpha Binding Resolution](#71-alpha-binding-resolution)
   - 7.2 [Supporting Alpha Aggregation](#72-supporting-alpha-aggregation)
   - 7.3 [Focus Name Propagation](#73-focus-name-propagation)
   - 7.4 [Baseline Description Re-stamping](#74-baseline-description-re-stamping)
8. [Source Provenance Tracking](#8-source-provenance-tracking)
9. [Name Canonicalization](#9-name-canonicalization)
10. [Practice Resolution Modes](#10-practice-resolution-modes)
    - 10.1 [Method Resolution](#101-method-resolution)
    - 10.2 [Practice Resolution with Pruning](#102-practice-resolution-with-pruning)
    - 10.3 [Baseline Resolution](#103-baseline-resolution)

---

## 1 Overview

The Practice Language supports modular authoring — practices are written independently, then composed into a unified document for rendering and interaction. The merge algorithm is the mechanism that produces this unified document.

Given a Method (a baseline practice plus one or more extension practices), the merge algorithm produces a single Practice-shaped document where:

- All same-named elements from different practices are merged rather than duplicated.
- The baseline practice's descriptions and structural identity are preserved.
- Extension practices enrich the baseline with additional checklists, narratives, tags, activities, work products, patterns, and other elements.
- Dependencies are resolved transitively before merging.

The output is a flat, kernel-shaped document that tooling can render without needing to understand the composition hierarchy.

---

## 2 Dependency Resolution

Before any element-level merging occurs, the system must determine the complete set of practices to merge and their order. The Practice Language supports two independent dependency chains: baseline dependencies (baselines that build on other baselines) and practice dependencies (extension practices that require other extension practices).

### 2.1 Baseline Dependencies

A PracticeBaseline may declare `baselinePracticeNames` — an array of other baseline names it builds upon. Resolution uses **post-order depth-first search**: dependencies are fully resolved before the dependent baseline, ensuring the foundational kernel is always the first layer in the merge.

**Cycle detection**: If a baseline's dependency chain references itself (directly or transitively), resolution throws an error. Missing library entries are silently skipped.

**Resolution process**: The ordered baselines are composed using the same merge algorithm (via an internal synthetic Method), producing a single resolved baseline that serves as the kernel for subsequent practice merging.

### 2.2 Practice Dependencies

A Practice may declare `practiceDependencyNames` — an array of other practice names it requires. These are resolved using the same **post-order DFS** strategy: each dependency's own dependencies are resolved first, and each distinct practice name is processed exactly once.

**Ordering guarantee**: Dependencies appear before the practices that require them in the merge layer order. This ensures that when practice B depends on practice A, A's contributions to shared elements (e.g., adding checklists to a baseline alpha) are already present when B's contributions merge.

**Cycle detection**: Circular `practiceDependencyNames` chains throw an error. Missing library entries are skipped.

### 2.3 Method Composition Entry Point

A Method document declares a `baselinePractice` (or `baselinePracticeName` for library resolution) and a `practices` array (or `practiceNames` for library resolution). The composition function:

1. Resolves the baseline (including its transitive baseline dependencies).
2. Resolves extension practices (including their transitive practice dependencies).
3. Merges all layers in order: baseline first, then extensions.

When the Method uses name-based references instead of embedded data, a library lookup index is required. The index maps practice and baseline names to their full document bodies, preferring standalone artifacts over embedded duplicates when the same name appears in multiple library roots.

---

## 3 Merge Hierarchy and Layer Ordering

### 3.1 Accumulator Initialization from Baseline

The merge begins by seeding an accumulator document from the resolved baseline:

- **Focuses, alphas, competencies**: Cloned directly from the baseline.
- **Activity spaces**: Converted into an internal slot map (space → activities) for efficient merging.
- **Work products, patterns, personas, persona groups, narrative types, citations, assets**: Initialized from the baseline arrays.
- **Alpha instances, work product instances, aliases**: Initialized if present on the baseline.
- **Metadata fields**: `authors`, `keywords`, `createdAt`, `updatedAt`, `version` are seeded from the baseline.
- **Method-level fields**: The Method's own `name`, `description`, `tags`, `narratives`, `citations`, and `assets` are applied at initialization, with the Method's description taking precedence.

A `mergesBaselinePracticeName` provenance field records which baseline was used, enabling tooling to distinguish merged composites from raw baselines.

### 3.2 Extension Practice Overlay

Each extension practice is merged onto the accumulator in dependency-resolved order. The first extension in the array is closest to the baseline (highest precedence among extensions); the last is the leaf practice (lowest precedence). For each extension, every element collection is merged:

- Activity spaces and activities merge into the slot map.
- Alphas, competencies, focuses, work products, patterns, personas, persona groups, narrative types, citations, assets, alpha instances, work product instances, and aliases all merge using their respective merge functions.
- `authors`, `keywords`, and `practiceDependencyNames` are unioned as string arrays.
- `updatedAt` is updated if the extension provides a newer timestamp.

**Narrative isolation**: Extension practice root-level narratives are NOT merged into the composite root. Only the Method's own narratives appear at root level. Practice-specific narratives remain within their respective practice elements.

### 3.3 Embedded Method Recursion

The `practices` array of a Method may contain not only plain Practice objects but also embedded Method objects (identified by having an object-valued `baselinePractice` property). When an embedded Method is encountered:

1. Its baseline is merged as a **secondary baseline kernel** (if it differs from the primary baseline).
2. Its nested `practices` array is recursively processed using the same merge logic.

This enables hierarchical method composition — a Method can include sub-Methods whose baselines and practices all fold into a single unified document.

---

## 4 Element-Level Merge Rules

### 4.1 The Core Merge Function

At the heart of the algorithm is a recursive record merge function that combines two practice element records (a `base` and an `overlay`). The merge follows these principles:

- The `name` field is never changed by the overlay.
- The `description` field is always preserved from the base (see Section 4.2).
- Tags merge via structured tag merging (see Section 4.4).
- Narratives merge additively by name (see Section 6.8).
- Narrative contexts merge additively by element name and sequence (see Section 6.8).
- Array fields merge using type-aware strategies (see Section 5).
- Nested object fields recurse with the same merge function.
- Scalar fields: the base value is kept unless it is vacant (null, undefined, or empty string), in which case the overlay fills the vacuum.

### 4.2 Description Preservation

**The description from the earliest layer always wins.** When a same-named element exists in both the base (accumulator) and the overlay (extension practice), the base's description is preserved regardless of what the overlay provides. This enforces the principle that the baseline defines what an element IS, while extensions enrich HOW it is verified and used.

After all extension layers merge, a final pass re-stamps every baseline-defined element's description from the original kernel document. This guards against incidental overwrites from intermediate cloning or spreading during merge operations (see Section 7.3).

### 4.3 Scalar Field Handling

For non-description scalar fields:

- **Vacant base, substantive overlay**: The overlay fills the gap. A value is "vacant" if it is `undefined`, `null`, or an empty/whitespace-only string.
- **Substantive base, any overlay**: The base value is kept. Extensions cannot override existing scalar values from earlier layers.
- **Both vacant**: Remains vacant.

This means the first layer to provide a substantive value for a scalar field owns that value permanently through the merge chain.

### 4.4 Tag Merging

Structured tags (`domainTags`, `lifecycleTags`, `organizationalTags`) merge by **union within each dimension**. If the base has `domainTags: ["Security"]` and the overlay has `domainTags: ["Architecture"]`, the result is `domainTags: ["Security", "Architecture"]`. Tags are deduplicated.

---

## 5 Array Merge Strategies

The merge algorithm selects different strategies for array fields based on the content shape and field key.

### 5.1 Named Element Arrays

When both the base and overlay arrays contain objects with a string `name` property, the arrays merge **by canonical name key**:

- Elements with matching names (after canonicalization) are merged using the recursive record merge function.
- Elements unique to either array appear in the output unchanged.

This is the default strategy for most practice element collections (alphas, states, activities, work products, etc.).

### 5.2 Contribution Arrays

Arrays keyed by `contributesTo` (or ending in `Contributes`) and containing objects with `alphaName` and `stateName` merge by **`alphaName::stateName` composite key**. Duplicate contributions are deduplicated; unique contributions from both arrays are unioned.

### 5.3 Relationship Arrays

The `relatesTo` array merges by **`alphaName`** key. If both the base and overlay declare a relationship to the same alpha, the overlay's relationship replaces the base's (last writer wins for relationships to the same target).

### 5.4 WorksOn Arrays

The `worksOn` array on activities merges by **`workProductName::levelOfDetailName`** composite key. Entries with matching keys are merged; unique entries are added.

### 5.5 Competency Level Arrays

The `recommendedCompetencyLevels` array merges by **`competencyName::competencyLevelName`** composite key.

### 5.6 Primitive Arrays

When arrays contain only primitive values (strings, numbers, booleans, null), they are **concatenated and deduplicated**. For mixed arrays of objects without `name` properties, deduplication uses JSON serialization for equality comparison.

---

## 6 Domain-Specific Merge Functions

Each element type has a specialized merge function that applies the core merge rules with type-appropriate handling.

### 6.1 Alpha Merging

Alphas merge by canonical name. When two alphas share the same name:

- **States**: Merge using state-specific logic (see Section 6.2).
- **`focusName`**: Prefers the non-implicit value. If the base has a real focus name (e.g., "Solution") and the overlay has an implicit placeholder, the base's focus name is kept. If the base has an implicit focus and the overlay provides a real one, the overlay's value is adopted.
- **`contributesTo`**: The first non-empty value wins (base priority).
- **`supportingAlphas`**: String arrays are unioned and deduplicated.
- **Source provenance**: The `sourcePracticeName` of the first layer to introduce the alpha is preserved (see Section 8).

### 6.2 State and Checklist Merging

**States** within an alpha merge by canonical name:

- The `seq` value from the overlay takes precedence (allows reordering).
- **Checklists** within a state merge by canonical checklist item name:
  - Same-named checklist items are merged using the core record merge function.
  - New checklist items from the overlay are appended.
  - Results are sorted by `seq` value.

This allows extension practices to add new checklist items to existing baseline states without altering the baseline's original items.

### 6.3 Activity Space and Activity Merging

Activity spaces use a **slot map** representation during merging. Each activity space is a slot containing the space metadata and a map of activities keyed by canonical name.

**Activity space slot merging**:

- Space metadata merges using the core record merge function.
- `contributesTo`, `requiredCompetencies`, and `involves` arrays are unioned.
- `focusName` prefers non-implicit values.
- Activities within the space merge by canonical name.

**Activity merging** (within a space):

- `activitySpaceName` from the overlay takes precedence.
- `focusName` prefers non-implicit values.
- `contributesTo`, `requiredCompetencies`, `worksOn`, and `recommendedCompetencyLevels` arrays are unioned/merged.

**Activity space ordering**: The final output preserves the ordering of activity spaces as they appear across the baseline and extensions. Baseline spaces appear first, followed by spaces introduced by each extension in dependency order. Spaces not referenced in any ordering hint are sorted alphabetically at the end.

**Flat activities**: Practices may declare activities either nested within `activitySpaces` or as top-level `activities` entries with an `activitySpaceName` reference. The merge algorithm canonicalizes both forms into the slot map representation, then outputs the combined result.

### 6.4 Work Product and Level of Detail Merging

Work products merge by canonical name. When two work products share the same name:

- **Levels of Detail** merge by canonical name within the work product:
  - The `seq` value from the overlay takes precedence.
  - `contributesTo` arrays are unioned by `alphaName::stateName` key.
  - **Checklists** within a level merge by canonical name (same logic as alpha state checklists).
  - Results are sorted by `seq` value.

### 6.5 Pattern and PatternView Merging

Patterns merge by canonical name. When two patterns share the same name:

- `narrativeTypeName`: The first non-empty value wins.
- **PatternViews** merge by canonical name within the pattern:
  - The `seq` value from the overlay takes precedence.
  - `narrativeElementName`: The first non-empty value wins.
  - `activitySpaces` and `activities` string arrays are unioned.
  - **`alphaStates`** (AlphaContribution arrays) merge using pattern-view-specific logic that unions alpha state entries by `alphaName::stateName` key.
  - **`alphaInstances`** merge by canonical instance name:
    - `evidenceBy` arrays are deduplicated by `name::workProductName::levelOfDetailName` composite key.
  - Results are sorted by `seq` value.

### 6.6 Competency Merging

Competencies merge by canonical name. Within a competency:

- **Levels** merge by composite key `level:name` (integer level number + canonical level name).
- Same-keyed levels merge using the core record merge function.
- Results are sorted by level number.

### 6.7 Persona and PersonaGroup Merging

**Personas** merge by canonical name. The `competencies` array is unioned and deduplicated by `competencyName::competencyLevelName` composite key.

**PersonaGroups** merge by canonical name. The `personaNames` string array is unioned and deduplicated.

### 6.8 Narrative Merging

The merge algorithm handles two distinct narrative structures:

**Narratives** (top-level narrative entries): Merge by canonical name. When two narratives share the same name, they are merged using the core record merge function, which recursively merges their nested structures.

**NarrativeContexts** (within PatternViews and other containers): Merge additively by composite key `narrativeElementName::seq`. When two contexts share the same key:

- Non-prose fields merge using the core record merge function.
- Prose content (stored in `context`, `content`, `narrativeContext`, `body`, `text`, or `description` fields) is **concatenated** (base prose followed by overlay prose, separated by double newline), not replaced.

This additive prose merging allows multiple practices to contribute context to the same narrative element within the same lifecycle phase.

**NarrativeTypes** merge by canonical name. Within a narrative type, `narrativeElements` merge by canonical name using the core record merge function.

### 6.9 Citation Merging

Citations merge by canonical name. When two citations share the same name:

- `authors` arrays are unioned and deduplicated.
- `date` from the overlay takes precedence (later citation wins).
- `source` from the overlay takes precedence.
- Other fields merge using the core record merge function.

### 6.10 Asset Merging

Assets merge by canonical name with **atomic replacement**: a later asset definition completely replaces an earlier one with the same name. Unlike most other element types, assets do not perform field-level merging — the entire asset object is replaced.

### 6.11 Alias Merging

Practice element aliases are deduplicated by composite key `practiceElementType + practiceElementName + aliasName`. The first occurrence of each unique key is kept; duplicates are discarded.

### 6.12 Instance Declaration Merging

**AlphaInstanceName** and **WorkProductInstanceName** declarations merge by canonical name using the core record merge function. These are keyed practice element overlays — same-named declarations combine their metadata; unique declarations are preserved.

---

## 7 Post-Merge Finalization

After all extension layers have been merged into the accumulator, several finalization passes run.

### 7.1 Alpha Binding Resolution

When the source document is a Method with an `alphaBindings` array, the merge algorithm injects cross-baseline contribution relationships into the merged document. This step runs **before** supporting alpha aggregation (Section 7.2) so that the injected `contributesTo` properties are automatically picked up by the aggregation pass.

For each `AlphaBinding` in the Method's `alphaBindings` array:

1. **Resolve the target alpha.** Look up the `baselineAlpha` by matching `baselineName` and `alphaName` against the alphas in the merged document. If the target alpha is not found, emit a validation warning and skip this binding.

2. **Inject `contributesTo` on each contributing alpha.** For each entry in `contributingAlphas`, find the contributing alpha in the merged document by matching `baselineName` and `alphaName`. Set the contributing alpha's `contributesTo` property to the target alpha's name. If the contributing alpha already has a `contributesTo` value (from its own baseline), emit a warning — method-level bindings should not override existing within-baseline contribution relationships.

3. **Inject `contributesToState` on contributing alpha states.** For each `stateContributions` entry on the contributing alpha, find the state matching `fromState` within the contributing alpha's `states` array and set its `contributesToState` property to the `toState` value. If the state already has a `contributesToState` value, emit a warning and do not override.

**Example:** Given a Method with this binding:

```json
{
  "baselineAlpha": {
    "baselineName": "Project Management Essentials",
    "alphaName": "Deliverable"
  },
  "contributingAlphas": [
    {
      "baselineName": "Platform Adoption Essentials",
      "alphaName": "Platform",
      "stateContributions": [
        { "fromState": "Operational", "toState": "Built" }
      ]
    }
  ]
}
```

After this step, the "Platform" alpha in the merged document will have `contributesTo: "Deliverable"`, and its "Operational" state will have `contributesToState: "Built"`.

**Ordering dependency:** This step must run before Section 7.2 (Supporting Alpha Aggregation) because the aggregation pass walks all `contributesTo` declarations to build `supportingAlphas` arrays. By injecting `contributesTo` first, the "Deliverable" alpha will automatically gain "Platform" in its `supportingAlphas` array without additional logic.

### 7.2 Supporting Alpha Aggregation

Every alpha that declares a `contributesTo` relationship is automatically added to the target (parent) alpha's `supportingAlphas` array. This ensures that the parent alpha's rollup calculation can discover all its children without requiring explicit `supportingAlphas` declarations across multiple practices.

The aggregation walks all alphas, collects `contributesTo → child name` mappings, and unions them into each parent's `supportingAlphas` array (deduplicating with any explicitly declared entries).

### 7.3 Focus Name Propagation

Two passes resolve focus names on the merged document:

1. **Derived focus name propagation**: Alphas with a `contributesTo` relationship inherit their parent's `focusName` if they do not declare one explicitly. Activities inherit focus from their containing activity space or from the alphas they contribute to.

2. **Implicit focus placeholder finalization**: Any element still carrying an implicit/unresolved focus name after propagation is assigned a default placeholder value so that visualization tooling can render it in a catch-all swimlane.

### 7.4 Baseline Description Re-stamping

A final pass walks every element type (focuses, alphas, states, checklist items, activity spaces, activities, competencies, competency levels, narrative types, narrative elements, patterns, pattern views, work products, levels of detail, LOD checklist items, personas, and persona groups) and re-stamps the `description` from the original kernel baseline document onto any same-named element in the merged output.

This pass runs last to guarantee that no intermediate operation (cloning, spreading, focus placeholder insertion) can leave extension-layer prose on elements that are structurally defined by the baseline. It is the authoritative enforcement of Section 4.2 (Description Preservation).

---

## 8 Source Provenance Tracking

The merge algorithm tracks which practice introduced each element via a `sourcePracticeName` property. This is set on alphas, activities, activity spaces, work products, and patterns.

**Provenance rules**:

- When an element first enters the accumulator from the baseline, its `sourcePracticeName` is set to the baseline practice name.
- When an extension practice introduces a new element (not present in the accumulator), its `sourcePracticeName` is set to the extension practice name.
- When an extension practice merges with an existing element, the **existing** `sourcePracticeName` is preserved. The first practice to introduce an element retains provenance credit.

This provenance information enables tooling to display element origins, show which practice contributed which content, and support practice-aware filtering in the navigator.

---

## 9 Name Canonicalization

All name-based merging and keying uses **canonical name comparison**. The canonicalization function normalizes element names to provide case-insensitive, whitespace-normalized matching. This ensures that minor variations in element naming across practices (e.g., different capitalization or extra whitespace) do not prevent proper merging.

Activity spaces have an additional identity key normalization that accounts for the structural distinction between activity spaces (containers) and practice activity nodes (leaf activities declared at the space level).

---

## 10 Practice Resolution Modes

The merge algorithm supports three resolution modes depending on the document type being resolved.

### 10.1 Method Resolution

A Method document is resolved by directly invoking the composition function:

1. Resolve the baseline (with its transitive baseline dependencies).
2. Expand extension practices (including transitive practice dependencies).
3. Compose all layers into a single merged document.
4. Run post-merge finalization.

The output is a kernel-shaped document suitable for rendering.

### 10.2 Practice Resolution with Pruning

When resolving a standalone Practice (not within a Method), the merge produces a full composite but then **prunes** it to the documentation closure — the set of elements actually referenced by the primary practice and its dependencies.

**Documentation closure**: The system collects all element names referenced by the primary practice (alphas, activity spaces, activities, competencies, work products, personas, persona groups, patterns) across all structural fields (contributesTo, activitySpaceName, worksOn, alphaStates, etc.). This closure is expanded transitively along contribution edges and persona/group membership.

All baseline alphas and activity spaces are always included in the closure to provide a complete view of the baseline coverage, even if the extension practice does not explicitly reference them.

Elements not in the closure are removed from the merged output, producing a focused document that shows the practice in the context of its baseline without including unrelated baseline content.

### 10.3 Baseline Resolution

When resolving a PracticeBaseline with `baselinePracticeNames`, the system creates a synthetic Method from the dependency chain and composes it. The result is a fully resolved baseline with all parent baseline content merged in.

---

## Summary of Merge Precedence

| Aspect | Rule |
|---|---|
| **Description** | Baseline always wins; re-stamped as final step |
| **Scalar fields** | First substantive value wins (base over overlay) |
| **Named elements** | Merged by canonical name; new elements added |
| **Arrays (named objects)** | Union by name key with recursive merge |
| **Arrays (primitives)** | Concatenate and deduplicate |
| **Tags** | Union within each dimension |
| **Contributions** | Union by `alphaName::stateName` |
| **Relationships** | Last writer wins per `alphaName` |
| **Assets** | Last writer wins (atomic replacement) |
| **Citations** | Field-level merge; authors union; later date/source wins |
| **Narratives** | Merge by name; narrative context prose concatenates |
| **Aliases** | Deduplicate by composite key |
| **Focus names** | Prefer non-implicit values; propagate from parent |
| **Source provenance** | First practice to introduce element retains credit |
| **Layer ordering** | Baseline → transitive deps (post-order) → direct practices |

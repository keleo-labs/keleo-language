[< Back to Semantic Guidance Hub](../semantics.md)

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

To add an alias, use an `add` operation with `elementType: "PracticeElementAlias"`. This adds a PracticeElementAlias to the target document's `practiceElementAliases` array — a presentation-layer alias without changing the structural identity of the element. The alias follows the strict isolation rules defined in [Section 4.3](composition.md#43-practice-aliasing-and-strict-isolation): the aliasName is used only for presentation and NEVER appears in structural references.

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
9. Status transitions must follow the defined lifecycle ([Section 13.4](#134-status-lifecycle))
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

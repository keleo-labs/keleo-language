[< Back to Semantic Guidance Hub](../semantics.md)

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

Both `contributesTo` and `mapsTo` reference parent alphas, and an alpha may have both (targeting different alphas). Cycles can span both relationship types. The acyclicity constraint applies to the **union** of both edge sets.

**Invalid Example:**
- Alpha "A" contributesTo "B", Alpha "B" mapsTo "C", Alpha "C" contributesTo "A"

**Constraint:** Construct a single directed graph where each alpha's `contributesTo` and `mapsTo` values are outgoing edges to their targets (an alpha with both properties has two outgoing edges). This combined graph must be acyclic.

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

# Circular Reference Protection — Implementation Specification

## 1 Purpose

This specification defines the requirements for software implementations that parse, validate, traverse, or render Practice Language documents. It ensures that circular references in document content — whether introduced by authoring error, malicious crafting, or merge artefacts — are detected, reported, and handled gracefully without crashes, infinite loops, stack overflows, or resource exhaustion.

This specification complements the acyclicity constraints defined in [semantics.md Section 14](../references/semantics.md#14-acyclicity-constraints-and-circular-reference-protection), which defines **what** must be acyclic. This document defines **how** implementations must enforce those constraints.

## 2 Scope

This specification applies to any software that:

- Validates Practice Language documents (schema validators, linters)
- Resolves symbolic references (merge algorithms, dependency resolvers)
- Traverses reference graphs (renderers, progress calculators, rollup engines)
- Imports or deserialises Practice Language JSON (loaders, parsers)

## 3 Threat Model

Circular references in Practice Language documents can arise from:

1. **Authoring error** — a practice author inadvertently creates a cycle (e.g., Alpha A `contributesTo` Alpha B, and B `contributesTo` A)
2. **Merge artefacts** — the merge algorithm combines independently authored practices that, when composed, form a cycle that neither practice exhibited alone
3. **Malicious input** — a crafted document intentionally creates deep or wide cycles to exploit stack-based recursion, exhaust memory via unbounded queue growth, or trigger denial-of-service through CPU-bound cycle detection on large graphs

Implementations must handle all three scenarios.

## 4 Properties Requiring Protection

The following properties create directed reference graphs. Each must be protected independently. See [semantics.md Section 14.5](../references/semantics.md#145-validation-rules-summary) for the complete property table.

### 4.1 Single-Parent Hierarchies

These properties create at most one outgoing edge per element, forming a forest (set of trees) when acyclic.

| Property | Element | Edge Semantics |
|---|---|---|
| `Alpha.contributesTo` | Alpha | child → parent specialisation |
| `Alpha.mapsTo` | Alpha | variant → parent mapping |
| `WorkProduct.partOf` | WorkProduct | component → container |
| `ChangeRequest.supersedes` | ChangeRequest | revision → predecessor |

**Combined constraint:** `Alpha.contributesTo` and `Alpha.mapsTo` form a single combined graph (an alpha has at most one of the two, creating one outgoing edge). Validate as one graph.

### 4.2 Multi-Edge Prerequisite Graphs

These properties create multiple outgoing edges per element, forming a general directed graph.

| Property | Element | Edge Semantics |
|---|---|---|
| `Background.alphaStates` | State, LevelOfDetail | state → required alpha state |
| `Background.workProductLevels` | State, LevelOfDetail | state → required WP level |
| `Background.alphaInstanceStates` | AlphaInstance, WorkProductInstance | instance → required instance state |
| `Background.workProductInstanceLevels` | AlphaInstance, WorkProductInstance | instance → required instance level |
| `State.contributesToState` | State | child state → parent state |

### 4.3 Document Dependency Graphs

| Property | Element | Edge Semantics |
|---|---|---|
| `PracticeBaseline.baselinePracticeNames` | PracticeBaseline | dependent → dependency |
| `Practice.practiceDependencyNames` | Practice | dependent → dependency |

## 5 Detection Algorithms

### 5.1 Acyclicity Validation (Authoring and Load Time)

Implementations MUST validate acyclicity for each graph category (Section 4) when a document is loaded, saved, or merged. The recommended algorithm depends on graph structure:

**For single-parent hierarchies (Section 4.1):** Use tortoise-and-hare (Floyd's cycle detection) or visited-set chain walking. Time complexity: O(n) where n is the number of elements.

```
function validateChain(startElement, getParent):
    visited = new Set()
    current = startElement
    while current is not null:
        if visited.has(current.name):
            return CycleError(chain: visited, loopAt: current.name)
        visited.add(current.name)
        current = getParent(current)
    return Valid
```

**For multi-edge graphs (Sections 4.2, 4.3):** Use depth-first search with three-colour marking (white/grey/black) or Kahn's algorithm (topological sort via in-degree counting). Time complexity: O(V + E) where V is the number of nodes and E is the number of edges.

```
function validateDAG(nodes, getEdges):
    WHITE = 0, GREY = 1, BLACK = 2
    colour = new Map()  // all nodes start WHITE
    path = []

    function visit(node):
        if colour.get(node) == BLACK:
            return Valid
        if colour.get(node) == GREY:
            cycleStart = path.indexOf(node)
            return CycleError(chain: path.slice(cycleStart))
        colour.set(node, GREY)
        path.push(node)
        for each target in getEdges(node):
            result = visit(target)
            if result is CycleError:
                return result
        path.pop()
        colour.set(node, BLACK)
        return Valid

    for each node in nodes:
        result = visit(node)
        if result is CycleError:
            return result
    return Valid
```

### 5.2 Runtime Traversal Protection (Defense in Depth)

Even after acyclicity validation, implementations MUST protect all recursive traversals against cycles. This provides defense in depth against:

- Validation being skipped (e.g., documents loaded from a trusted cache without revalidation)
- Concurrent mutation introducing cycles between validation and traversal
- Bugs in the validation logic itself

**Visited-set guard:** Every recursive traversal must maintain a set of visited node identifiers. If a node is encountered that is already in the visited set, the traversal must halt and report the cycle.

```
function traverse(element, getChildren, visitor):
    visited = new Set()

    function walk(node, depth):
        if depth > MAX_DEPTH:
            throw DepthLimitExceeded(node, depth)
        if visited.has(node.name):
            throw CircularReferenceDetected(node.name, visited)
        visited.add(node.name)
        visitor(node)
        for each child in getChildren(node):
            walk(child, depth + 1)
        visited.delete(node.name)  // backtrack for DAG (not tree) traversal

    walk(element, 0)
```

## 6 Depth Limits

Implementations MUST enforce maximum depth limits on all recursive traversals, independent of cycle detection. Depth limits protect against:

- Extremely deep (but acyclic) hierarchies that exhaust the call stack
- Maliciously crafted documents designed to consume resources through deep nesting

### 6.1 Recommended Depth Limits

| Graph Category | Recommended Max Depth | Rationale |
|---|---|---|
| Alpha hierarchy (`contributesTo`/`mapsTo`) | 20 | Practice hierarchies rarely exceed 3–4 levels; 20 provides margin |
| Work product containment (`partOf`) | 10 | Containment should be shallow (typically 1–2 levels) |
| Background prerequisites | 50 | Cross-element chains can legitimately span many elements |
| Document dependencies | 30 | Dependency chains are typically short but may span many practices |
| State contribution mapping | 20 | Mirrors alpha hierarchy depth |
| Supersedes chain | 100 | Revision chains grow over time but linearly |

### 6.2 Configurability

Implementations SHOULD allow depth limits to be configured by the deploying organisation, with the values in Section 6.1 as defaults. Implementations MUST NOT allow depth limits to be disabled entirely — a hard ceiling of 1000 must be enforced regardless of configuration.

### 6.3 Depth Limit Exceeded Behaviour

When a depth limit is exceeded, the implementation MUST:

1. Halt the traversal immediately
2. Report a diagnostic error identifying the element at which the limit was exceeded and the current traversal path
3. Not crash, hang, or produce partial/corrupt output

## 7 Error Reporting

### 7.1 Cycle Detection Errors

When a cycle is detected (at validation time or runtime), the error report MUST include:

1. **Error type:** clearly identified as a circular reference / cycle error
2. **Property:** the schema property that forms the cycle (e.g., `contributesTo`, `partOf`, `Background.alphaStates`)
3. **Cycle chain:** the ordered list of element names (or element type + name pairs) forming the cycle, starting and ending at the same element
4. **Document context:** the document name(s) containing the elements involved

**Example error message:**

```
Circular reference detected in Alpha.contributesTo chain:
  "Platform Capability" → "Platform Service" → "Platform Capability"
  in practice "Cloud Platform Engineering"
```

### 7.2 Depth Limit Errors

When a depth limit is exceeded, the error report MUST include:

1. **Error type:** clearly identified as a depth limit exceeded error
2. **Limit:** the configured maximum depth
3. **Element:** the element at which the limit was reached
4. **Path:** the traversal path from root to the element (or a truncated suffix if the path is very long)

### 7.3 Error Severity

| Context | Severity | Behaviour |
|---|---|---|
| Schema validation / linting | Error | Reject the document; do not proceed with merge or rendering |
| Merge algorithm | Error | Halt the merge; report which practice introduced the cycle |
| Runtime traversal (rendering, rollup) | Error | Skip the cyclic subgraph; render remaining content with a warning |
| Import / deserialisation | Warning + quarantine | Load the document but flag it as containing cycles; prevent use in merge or rendering until cycles are resolved |

## 8 Security Hardening

### 8.1 Stack Overflow Protection

Recursive traversals that use the call stack (natural recursion) are vulnerable to stack overflow on deep or cyclic graphs. Implementations MUST use one of:

- **Iterative traversal with an explicit stack** (preferred) — eliminates call stack dependency entirely
- **Depth-limited recursion** with the limits defined in Section 6 — bounds stack growth

Implementations MUST NOT rely solely on language-level stack overflow exceptions (e.g., Python's `RecursionError`, JavaScript's `RangeError: Maximum call stack size exceeded`) as the protection mechanism. These exceptions are unreliable across platforms and may not be catchable in all execution contexts.

### 8.2 Memory Exhaustion Protection

Breadth-first traversals using queues can exhaust memory if a graph contains nodes with very high fan-out (e.g., a state with hundreds of background prerequisites). Implementations SHOULD:

- Bound queue size to a reasonable maximum (e.g., 10,000 pending nodes)
- Use streaming/lazy evaluation when traversing large graphs
- Report an error if the queue size limit is exceeded

### 8.3 CPU Exhaustion Protection

Naive cycle detection on dense graphs can have quadratic or worse time complexity. Implementations MUST use algorithms with known polynomial time complexity (Section 5.1). For the graph sizes typical in Practice Language documents (hundreds to low thousands of nodes), O(V + E) algorithms complete in milliseconds.

### 8.4 Untrusted Input

When processing documents from untrusted sources (e.g., user uploads, package registry imports, API submissions), implementations MUST:

1. Validate acyclicity before any traversal or computation
2. Enforce depth limits on all traversals
3. Enforce time limits on validation operations (recommended: 30 seconds maximum for a single document)
4. Reject documents that exceed size thresholds before attempting graph analysis (recommended: 50MB maximum document size)

## 9 Testing Requirements

Implementations MUST include test cases covering:

### 9.1 Cycle Detection Tests

For each property in Section 4:

1. **Self-reference:** Element X references itself (e.g., Alpha "A" with `contributesTo: "A"`)
2. **Mutual cycle:** Two elements reference each other (A→B, B→A)
3. **Transitive cycle:** Three or more elements form a chain that loops (A→B→C→A)
4. **Valid DAG:** A deep but acyclic hierarchy is accepted without error

### 9.2 Cross-Property Cycle Tests

1. **Mixed `contributesTo`/`mapsTo` cycle:** A cycle spanning both properties
2. **Cross-element prerequisite cycle:** A Background.alphaStates entry on State X requires a state whose own Background requires State X
3. **Cross-type prerequisite cycle:** A state requiring a work product level whose background requires that state

### 9.3 Depth Limit Tests

1. **At limit:** A chain of exactly MAX_DEPTH elements is accepted
2. **Exceeds limit:** A chain of MAX_DEPTH + 1 elements is rejected with a clear error
3. **No crash:** A chain of 10× MAX_DEPTH elements does not cause a crash or hang

### 9.4 Error Reporting Tests

1. **Cycle chain accuracy:** The reported cycle chain exactly matches the actual cycle
2. **Property identification:** The error correctly identifies which property created the cycle
3. **Document context:** The error names the document(s) containing the cycle

## 10 Compliance Levels

### Level 1 — Minimum Viable Protection

Required for any software that loads Practice Language documents:

- Depth-limited traversals for all recursive operations (Section 6)
- Visited-set guards on all recursive traversals (Section 5.2)
- No crashes or hangs on cyclic input

### Level 2 — Full Validation

Required for validators, merge tools, and authoring tools:

- All Level 1 requirements
- Acyclicity validation for all properties in Section 4 at load/save time (Section 5.1)
- Error reporting meeting Section 7 requirements
- Test coverage meeting Section 9 requirements

### Level 3 — Security Hardened

Required for software processing untrusted input (registries, APIs, import tools):

- All Level 2 requirements
- Iterative (non-recursive) traversal (Section 8.1)
- Memory exhaustion protection (Section 8.2)
- Time and size limits on untrusted input (Section 8.4)
- Fuzzing or property-based testing with randomly generated cyclic graphs

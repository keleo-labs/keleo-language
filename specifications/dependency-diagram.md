# The Dependency Diagram

## Objective

The Dependency Diagram provides a visual map of the compositional structure behind a practice, method, or baseline — showing which baselines and extension practices contribute to the document being viewed and how they relate to each other. It appears on the navigator's introduction page, giving practitioners immediate context on what they are looking at before they explore individual elements.

The diagram answers the question: *"What is this built from?"*

The diagram exists in two forms:

1. **Interactive (navigator)** — a React component with click-to-select behaviour, where selecting a dependency node opens its details in the navigator's secondary panel.
2. **Static (export)** — a self-contained SVG string for use in downloadable static sites, consuming a pre-computed layout.

Both forms consume the same `DependencyDiagramLayout` data structure and produce visually consistent output.

## Relationship to Existing Schema

The diagram renders the compositional relationships expressed by symbolic name references in Practice Language documents:

- **`baselinePracticeName`** — on a Practice or Method, names the baseline this document extends or composes from.
- **`practiceDependencyNames`** — on a Practice, names other practices that must be resolved before this one.
- **`practiceNames` / `practices`** — on a Method, names the extension practices composed into the method.
- **`baselinePracticeNames`** — on a PracticeBaseline, names other baselines this baseline builds upon.

These are the same symbolic references that the packaging specification's dependency mechanism resolves. The diagram visualises the resolution tree that the merge algorithm traverses during practice composition.

## Relationship to Other Diagrams

The Dependency Diagram is structurally distinct from the Concerns Overview and Activities Overview diagrams:

| Property | Dependency Diagram | Concerns / Activities Overview |
|----------|-------------------|-------------------------------|
| Data source | Cross-document symbolic references | Single-document structural hierarchy |
| Tree depth | Variable, follows transitive dependencies | Fixed (`contributesTo` for alphas, 2-level for activities) |
| Node identity | Document names (practices, baselines) | Element names (alphas, activity spaces, activities) |
| Grouping | By baseline practice | By focus area |
| Layout direction | Left-to-right (root → dependencies) | Top-to-bottom (parent → children) |

## Visual Structure

The diagram uses a left-to-right layout with the root document on the left and its dependencies fanning out to the right, grouped by baseline:

```
                    ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
                      Baseline A
                    │                                   │
                      ┌───────────────┐
                    │ │ ■ Baseline A  │ ─────────────── │──┐
                      └───────────────┘                     │
┌───────────────┐   │        │                          │   │
│ ■ Root Doc    │────        │                              │
└───────────────┘   │   ┌────┴──────────┐               │   │
                    │   │ ◆ Practice X  │                   │
                    │   └───────────────┘               │   │
                    └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘   │
                                                            │
                    ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐   │
                      Baseline B                            │
                    │                                   │   │
                      ┌───────────────┐                     │
                    │ │ ■ Baseline B  │ ◄───────────────────┘
                      └───────────────┘
                    │                                   │
                    └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
```

### Layers

The SVG is rendered in three visual layers, painted in this order:

1. **Group backgrounds** — semi-transparent rounded rectangles behind each baseline's cluster of nodes, with the baseline name as a label.
2. **Edges** — curved connector lines with arrowheads showing dependency direction (from dependent to dependency).
3. **Node cards** — rectangular cards for each document, styled by kind.

## Data Pipeline

The diagram is produced in three stages: tree building, layout computation, and rendering.

### Stage 1: Tree Building

`buildDependencyTree(doc, libraryIndex)` takes the document being viewed and a library lookup index, and produces a `DependencyTreeData` — a tree of `DependencyNode` objects plus a list of all baseline names encountered.

#### Document Classification

The document is first classified as `"practice"`, `"method"`, or `"baselinePractice"` using the library classifier. This determines which reference fields to follow.

#### Recursive Expansion

Starting from the root document:

- **Practice:** Follow `baselinePracticeName` (producing a `baselinePractice` child), then follow each entry in `practiceDependencyNames` (producing `practice` children). Each practice child is recursively expanded via `buildPracticeNode`, which follows its own `practiceDependencyNames`.
- **Method:** Follow `baselinePracticeName` or `baselinePractice.name` (producing a `baselinePractice` child), then follow each entry in `practices` or `practiceNames` (producing `practice` children), each recursively expanded.
- **Baseline:** Follow each entry in `baselinePracticeNames` (producing `baselinePractice` children), each recursively expanded via `buildBaselineNode`.

#### Cycle Prevention

A `visited` set tracks all names encountered during traversal. If a name has already been visited, that branch is not expanded. This prevents infinite recursion from circular dependencies.

#### Node Types

Each node in the tree carries:

| Field | Description |
|-------|-------------|
| `name` | The document name (symbolic reference key) |
| `kind` | `"root"` (the viewed document), `"practice"`, or `"baselinePractice"` |
| `baselineName` | The baseline this node belongs to (null for the root, self-referential for baselines) |
| `children` | Array of child `DependencyNode` objects |

#### Output

```typescript
type DependencyTreeData = {
  root: DependencyNode;
  baselineNames: string[];  // deduplicated list of all baseline names in the tree
};
```

### Stage 2: Layout Computation

`computeDependencyLayout(tree)` converts the tree into positioned geometry: node rectangles, edge coordinates, group bounding boxes, and a viewport.

#### Layout Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `NODE_WIDTH` | 160px | Width of every node card |
| `NODE_HEIGHT` | 48px | Height of every node card |
| `COLUMN_GAP` | 60px | Horizontal gap between depth columns |
| `ROW_GAP` | 16px | Vertical gap between rows within a group |
| `GROUP_PADDING_X` | 16px | Horizontal padding inside group backgrounds |
| `GROUP_PADDING_Y` | 28px | Vertical padding inside group backgrounds (top, accommodating the label) |
| `GROUP_GAP` | 24px | Vertical gap between groups |
| `ROOT_GAP` | 40px | Horizontal gap between the root node and the dependency columns |

#### Flattening

The tree is flattened via depth-first traversal into an array of `FlatNode` objects, each recording its `column` (depth from root, starting at 0 for the root itself) and `parentName`.

#### Grouping by Baseline

Non-root nodes are partitioned by `baselineName`. Nodes with no baseline are placed in a synthetic `"__ungrouped__"` group (which does not render a group background). Within each group, baseline nodes sort before practice nodes, then by column depth.

#### Row Assignment Within Groups

Each group's nodes are arranged into rows:

1. **Baseline row.** All baseline nodes in the group are placed in the first row. Since a group typically contains one baseline, this is usually a single-node row.
2. **Practice chains.** Practices are traced into chains by following `parentName` links within the group. Each chain becomes its own row. A chain head is a practice whose parent is the root node, or whose parent is not in the same group.
3. **Unassigned practices.** Any practices not reached by chain traversal are placed in solo rows.

#### Node Positioning

Nodes are positioned using column and row indices:

```
x = groupXStart + GROUP_PADDING_X + (column - minDepColumn) × (NODE_WIDTH + COLUMN_GAP)
y = currentGroupY + GROUP_PADDING_Y + rowIndex × (NODE_HEIGHT + ROW_GAP)
```

Where `groupXStart = NODE_WIDTH + ROOT_GAP` (the root card occupies column 0, and all dependency nodes start after the root gap).

#### Group Bounding Boxes

For each named group (not `"__ungrouped__"`), a bounding rectangle is computed from the min/max positions of its member nodes, expanded by `GROUP_PADDING_X` on left and right and `GROUP_PADDING_Y` on top. The bottom padding uses `GROUP_PADDING_X` (not `GROUP_PADDING_Y`), keeping vertical spacing tighter below the last row.

Groups are stacked vertically, separated by `GROUP_GAP`. After placing all nodes in a group, `currentGroupY` advances past the lowest node by `NODE_HEIGHT / 2 + GROUP_GAP`.

#### Root Node Positioning

The root node is placed at `x = 0`, vertically centred relative to all dependency nodes. The centre point is the midpoint between the highest and lowest dependency node centres:

```
centerY = (min(depNodeCenters) + max(depNodeCenters)) / 2
rootY = centerY - NODE_HEIGHT / 2
```

#### Edge Computation

For each parent-child pair in the flattened tree, an edge is created:

```
x1 = parent.x + parent.width     (right edge of parent)
y1 = parent.y + parent.height / 2 (vertical centre of parent)
x2 = child.x                      (left edge of child)
y2 = child.y + child.height / 2   (vertical centre of child)
```

#### Viewport Adjustment

The viewport is computed to encompass all nodes and groups with 20px margin. If any element has a negative y-coordinate (the root may be positioned above the first group), all coordinates are shifted down by `10 - minY` to ensure a 10px top margin.

#### Output

```typescript
type DependencyDiagramLayout = {
  nodes: LayoutNode[];    // positioned rectangles with kind metadata
  edges: LayoutEdge[];    // parent-to-child connection coordinates
  groups: LayoutGroup[];  // baseline group bounding boxes
  viewBoxWidth: number;
  viewBoxHeight: number;
};
```

### Stage 3: Rendering

The rendering stage consumes a `DependencyDiagramLayout` and produces SVG.

#### Arrow Markers

A reusable arrow marker is defined in `<defs>`:

- **Marker dimensions:** 8×6px
- **Shape:** Filled triangle (polygon `0,0 8,3 0,6`)
- **Colour:** `rgba(102, 102, 102, 0.7)`
- **Reference point:** `(8, 3)` — the tip of the arrow

#### Group Backgrounds

Each `LayoutGroup` is rendered as:

- A rounded rectangle (`rx="6"`, `ry="6"`) with light gray fill and 1px border, at 50% opacity.
- A text label showing the baseline name, positioned 8px from the left edge and 16px from the top edge of the group rectangle (11px font).

#### Edges

Each `LayoutEdge` is rendered as a cubic Bezier curve with an arrowhead:

```
M x1,y1 C midX,y1 midX,y2 x2,y2
```

Where `midX = (x1 + x2) / 2`. This produces an S-curve that exits the parent horizontally and enters the child horizontally, with the inflection point at the midpoint. The arrowhead marker is attached to the end of the path.

Edge style: 1.5px stroke, `rgba(102, 102, 102, 0.6)`.

#### Node Cards

Each node is rendered as a rounded rectangle (`rx="4"`, `ry="4"`) with a `foreignObject` containing an icon and a label. Card styling varies by node kind:

| Property | Root | Baseline | Practice | Selected |
|----------|------|----------|----------|----------|
| Fill | White | Light gray | White | Primary-tinted white (8% mix) |
| Border colour | Default gray | Primary blue | Default gray | Primary blue |
| Border width | 1.5px | 2px | 1.5px | 2.5px |
| Icon | Layer group (■) | Layer group (■) | Puzzle piece (◆) | (unchanged) |
| Icon colour | Primary blue | Primary blue | Gray | (unchanged) |
| Clickable | No | Yes | Yes | Yes (toggles off) |

The icon and label are rendered inside a `foreignObject` using HTML:

- **Icon:** Font Awesome class (`fa-solid fa-layer-group` for root/baseline, `fa-solid fa-puzzle-piece` for practice), 12px, flex-shrink 0.
- **Label:** The document name, bold 11px, with CSS line clamping (max 2 lines, vertical ellipsis via `-webkit-line-clamp`). A `title` attribute provides the full name on hover.

In the static export, the `foreignObject` uses inline HTML with explicit `xmlns` and the icon is rendered as an HTML entity (■ for baseline/root, ◆ for practice). A `<text>` fallback is not used in the dependency diagram's static form because the layout assumes `foreignObject` support for proper icon and text alignment.

## Visibility Rules

The diagram is only rendered when the dependency tree contains at least 2 nodes (the root plus at least one dependency). A standalone baseline with no dependencies, or a practice with no resolvable baseline or dependency names, produces a single-node tree and the diagram is omitted.

This prevents the diagram from appearing as a lone card with no connections, which would add visual clutter without informational value.

## Interaction (Interactive Only)

### Selection

Clicking a non-root node selects it (or deselects if already selected). The root node is not selectable — it represents the document already being viewed.

Selection triggers the `onSelectElement` callback, which in the navigator context opens the selected practice or baseline's details in the secondary panel, allowing the user to inspect a dependency without leaving the introduction page.

### Scrolling

The diagram is wrapped in a horizontally scrollable container (`overflow-x: auto`). Documents with deep or wide dependency trees may exceed the panel width; horizontal scrolling ensures all nodes remain accessible.

## Static Export

The static SVG export (`generateDependencyDiagramSvg`) consumes the same `DependencyDiagramLayout` and produces a self-contained SVG string. It uses hardcoded colour values instead of CSS custom properties, making it independent of any runtime theme:

| Interactive (CSS variable) | Static (hardcoded) |
|---------------------------|-------------------|
| `--pf-v6-global--BackgroundColor--200` | `#f0f0f0` |
| `--pf-v6-global--BorderColor--100` | `#d2d2d2` |
| `--pf-v6-global--Color--200` | `#6a6e73` |
| `--pf-v6-global--primary-color--100` | `#0066cc` |
| `--pf-v6-global--Color--100` | `#151515` |
| `--pf-v6-global--FontFamily--text` | `RedHatText, Helvetica, Arial, sans-serif` |

The static export omits selection behaviour — all non-root nodes use their default styling.

## Implementation Parity

Both implementations consume the same `DependencyDiagramLayout` and must produce the same visual structure. The shared invariants are:

1. Same node positions, dimensions, and bounding boxes
2. Same edge geometry (cubic Bezier curves with arrowheads)
3. Same group background rectangles with labels
4. Same three-layer paint order (groups → edges → nodes)
5. Same node styling rules by kind

Differences between the two forms:

| Concern | Interactive | Static |
|---------|------------|--------|
| Colours | CSS custom properties with fallbacks | Hardcoded hex values |
| Selection | Click-to-select with visual feedback | None |
| Icons | Font Awesome CSS classes | HTML entities |
| Text overflow | CSS `-webkit-line-clamp` (2 lines) | CSS line clamping in `foreignObject` |
| Scroll | Horizontally scrollable container | Fixed viewport |
| Font | Theme font variable | `RedHatText, Helvetica, Arial, sans-serif` |

## Open Questions

1. **Transitive depth limit.** The tree is expanded transitively with no depth limit. Should there be a configurable maximum depth to prevent excessively wide diagrams for deeply nested dependency chains?
2. **Ungrouped nodes.** Nodes with no `baselineName` are placed in a synthetic ungrouped cluster with no background. Should these be visually distinguished (e.g., a labeled "Standalone" group)?
3. **Method vs practice root styling.** The root node uses the same visual treatment regardless of whether the viewed document is a practice, method, or baseline. Should the root card's icon or border style vary by document kind?

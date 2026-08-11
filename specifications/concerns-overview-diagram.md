# The Concerns Overview Diagram

## Objective

The Concerns Overview Diagram provides a visual map of all alphas in a practice or method, organised by focus area and rendered as a hierarchical tree structure. It gives practitioners an at-a-glance view of what a practice is concerned with — the essential things it tracks and the relationships between them.

The diagram exists in two forms:

1. **Interactive (navigator)** — a React component with click-to-select behaviour, score-based colouring, and integration with the element details panel.
2. **Static (export)** — a self-contained SVG string for use in downloadable static sites and PDF reports, with no runtime dependencies.

Both forms use the same layout constants and produce visually consistent output. When one changes, the other must be updated to match.

## Relationship to Existing Schema

The diagram renders directly from the `PracticeBaseline` type's structural properties:

- **`alphas`** — the array of Alpha objects, each with `name`, `contributesTo` (parent reference), `mapsTo` (variant mapping reference), `focusName` (grouping key), `seq` (sort order within focus), and optional `assetNames` (icon references).
- **`focuses`** — the array of Focus objects providing names, descriptions, and ordering for the grouping sections.
- **`assets`** — the array of Asset objects for resolving icon references on cards.

The `contributesTo` and `mapsTo` fields on Alpha are the structural backbone of the diagram — they define the parent-child tree that the layout algorithm renders. Alphas where both `contributesTo` and `mapsTo` are absent or null are root alphas; all others are positioned as children of the alpha they name. The two fields are mutually exclusive on any given alpha: `contributesTo` indicates a sub-alpha relationship, while `mapsTo` indicates a variant mapping relationship (same state progression, different name/description).

## Visual Structure

The diagram is organised into three visual layers:

```
┌─────────────────────────────────────────────────────────┐
│  Focus Heading                                          │  ← Focus layer
│  Focus description (italic)                             │
│                                                         │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│  │ Root α A │   │ Root α B │   │ Root α C │            │  ← Tree layer
│  └──────────┘   └──────────┘   └──────────┘            │
│       │              │                                  │
│       ├── ┌────────┐ ├── ┌────────┐                     │
│       │   │ Child  │ │   │ Child  │                     │  ← Card layer
│       │   └────────┘ │   └────────┘                     │
│       │              │                                  │
│       └── ┌────────┐ └── ┌────────┐                     │
│           │ Child  │     │ Child  │                     │
│           └────────┘     └────────┘                     │
│                                                         │
│  Focus Heading                                          │  ← Next focus
│  ...                                                    │
└─────────────────────────────────────────────────────────┘
```

### Focus Groups

Alphas are first partitioned by their `focusName` property. Each focus group is rendered as a vertical section with:

- A **heading** displaying the focus name (bold, 14px sans-serif)
- An optional **description** in italic (11px, truncated to 80 characters in static export)

Focus groups are ordered by the `seq` (or declaration order) of the corresponding Focus object in `baseline.focuses`. Alphas with no `focusName` or with a name not matching any Focus object are placed in an "Other" group at the end.

### Alpha Trees

Within each focus group, root alphas (those with neither `contributesTo` nor `mapsTo`) are rendered as independent trees laid out horizontally. Each tree consists of:

1. A **root card** at the top
2. **Child cards** indented below, connected by tree lines
3. **Grandchild cards** further indented, recursively

Children of a parent alpha are collected from two sources: alphas whose `mapsTo` names the parent, and alphas whose `contributesTo` names the parent. **MapsTo children are sorted first**, appearing above contributesTo children within the same parent. This ordering is applied at every level of the tree, not only at the first level below the root.

Trees within a focus group wrap onto new rows when they exceed the available width.

### Cards

Each alpha is rendered as a rectangular card:

- **Dimensions:** 180px wide × 48px tall
- **Corner radius:** 4px
- **Content:** An optional icon (from the alpha's `assetNames` where `type === "icon"`) followed by the alpha name (bold, 11px)
- **Border:** 1px solid, colour varies by selection state

In the interactive form, cards use `foreignObject` to embed HTML content (supporting icon fonts and rich text). In the static form, cards use a dual-rendering strategy: a `<text>` element for environments that strip `foreignObject` (such as GitHub's SVG sanitiser), and a `foreignObject` with embedded HTML for environments that support it.

## Layout Algorithm

### Layout Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `CARD_WIDTH` | 180px | Width of every alpha card |
| `CARD_HEIGHT` | 48px | Height of every alpha card |
| `CARD_GAP` | 12px | Vertical gap between sibling cards |
| `VERTICAL_PADDING` | 12px | Extra padding after a subtree before the next sibling |
| `INDENT` | 42px | Horizontal indent per tree depth level |
| `LINE_OFFSET` | 21px | X-offset of the vertical connector line from the parent card's left edge (half of `INDENT`) |
| `FOCUS_HEADING_HEIGHT` | 40px | Vertical space reserved for focus heading + description |
| `FOCUS_GAP` | 32px | Vertical gap between focus groups |
| `WRAP_WIDTH` | 1100px | Maximum row width before trees wrap to a new row (static export) |
| `TREE_GAP_X` | 24px | Horizontal gap between sibling trees in a row |
| `ROW_GAP` | 24px | Vertical gap between wrapped rows of trees |
| `COLUMN_GAP` | 24px | Horizontal gap between columns within a multi-column tree |
| `MULTI_COL_THRESHOLD` | 420px | Height threshold (7 × card slot) before multi-column layout activates |
| `MAPS_TO_BAR_WIDTH` | 6px | Width of the vertical bar connector for `mapsTo` relationships |
| `CONTRIBUTES_TO_COLOR` | `rgba(102, 102, 102, 0.8)` | Connector line colour for `contributesTo` relationships (grey) |
| `MAPS_TO_COLOR` | `rgba(0, 102, 204, 0.6)` | Fill colour for the `mapsTo` bar connector (blue) |

### Tree Building

For each root alpha, the algorithm builds a tree by recursively collecting children (alphas whose `mapsTo` or `contributesTo` matches the parent's name):

1. **Filter children** of the current parent from the full alpha array. Collect `mapsTo` children first, then `contributesTo` children, concatenating both lists so that mapsTo children appear before contributesTo children.
2. **Sort** children by `seq` within their focus group (sorting happens at the focus level before tree building).
3. For each child:
   - Assign `x = parentX + INDENT` and `y = currentY`.
   - If the child has its own children, recurse. Advance `currentY` by the child's card height + gap + the subtree's total height + vertical padding.
   - If the child is a leaf, advance `currentY` by card height + gap.
4. Return the node array and the total height consumed.

### Multi-Column Layout

When a root alpha has many direct children, the single-column layout can become excessively tall. The multi-column algorithm redistributes children across columns to reduce overall height:

1. **Measure** each direct child's slot height (card height + gap, plus subtree height if it has grandchildren).
2. **Check threshold.** If the total children height exceeds `MULTI_COL_THRESHOLD` and there are at least 2 direct children, attempt a 2-column split.
3. **Balanced split.** Use a prefix-sum approach to find the split point that minimises the maximum column height. For 2 columns, try every possible split point; for 3 columns, try every pair of split points.
4. **Accept the split** only if the maximum column height is ≤ 70% of the single-column height (i.e., the split provides at least a 30% height reduction). If the 2-column result still exceeds the threshold and there are at least 4 children, attempt a 3-column split with the same 70% acceptance criterion.
5. **Layout columns.** Each column is laid out independently. The column width is determined by the maximum tree depth within that column: `(maxDepth + 1) × INDENT + CARD_WIDTH`. Columns are separated by `COLUMN_GAP`.
6. **Root card width.** In multi-column mode, the root card stretches to span all columns (`totalWidth`). In single-column mode, it remains `CARD_WIDTH`.

### Row Wrapping (Static Export)

In the static export, multiple trees within a focus group are laid out in a wrapping horizontal flow:

1. Place trees left-to-right, separated by `TREE_GAP_X`.
2. When the next tree would exceed `WRAP_WIDTH`, start a new row below, separated by `ROW_GAP`.
3. Track the maximum row width to determine the SVG viewport width.

The interactive form uses CSS flexbox with `flex-wrap: wrap` and a 24px gap, producing equivalent wrapping behaviour at the browser's discretion.

## Connector Lines

Parent-child relationships are rendered using two distinct visual styles depending on the relationship type:

### ContributesTo Connectors (Orthogonal Lines)

`contributesTo` children use the existing orthogonal line connector:

1. **Vertical trunk.** A 3px grey (`rgba(102, 102, 102, 0.8)`) line extending from the parent card's bottom edge (`parentY + CARD_HEIGHT`) down to the vertical centre of the last `contributesTo` child.
2. **Horizontal branches.** For each `contributesTo` child, a 3px grey line from the trunk's x-position (`parentX + LINE_OFFSET`) to the child card's left edge, at the child's vertical centre.

### MapsTo Connectors (Vertical Bar)

`mapsTo` children use a thick vertical rectangular bar instead of line connectors, creating a stronger visual bond:

- **Shape:** A filled `<rect>` with `MAPS_TO_BAR_WIDTH` (6px) width and 2px corner radius.
- **Colour:** `rgba(0, 102, 204, 0.6)` (blue), constant `MAPS_TO_COLOR`.
- **X-position:** Immediately to the left of the child cards (`childX - MAPS_TO_BAR_WIDTH`), which places it at `parentX + INDENT - 6`. This avoids the `LINE_OFFSET` position used by `contributesTo` trunk lines — the two connector types occupy different horizontal positions and do not overlap.
- **Y-span:** From the parent card's bottom edge (`parentY + CARD_HEIGHT`) to the bottom edge of the last `mapsTo` child card (`lastMapsToChild.y + CARD_HEIGHT`).
- **No horizontal branches.** The bar alone indicates the relationship; no individual lines connect it to each child card.

### Mixed Children

When a parent has both `mapsTo` and `contributesTo` children, both connector types are rendered independently. Since `mapsTo` children are sorted first (above `contributesTo` children), and the bar and trunk occupy different x-positions, the two connector types do not interfere visually.

The connector lines and bar are rendered as a separate pass before the cards, ensuring they appear behind cards in the SVG paint order.

## Score Colouring (Interactive Only)

In the interactive form, each card's fill colour is determined by its alpha coverage score, as defined in the Scoring specification. The score-to-colour mapping uses the score intensity scale:

| Score | Fill |
|-------|------|
| 0 | `#FFFFFF` (white) |
| 1 | `#E7F1FA` (light blue) |
| 2 | `#BEE1F4` (mid blue) |
| 3+ | `#73BCF7` (dark blue) |

The selected card overrides this with a primary-colour tinted background and a 3px primary-colour border.

The static export does not include score colouring — all cards use a white fill with a `#d2d2d2` border. This is because the static export is a snapshot of structure, not a live analysis tool, and scores require the full scoring pipeline which is not available at export time.

## Selection Behaviour (Interactive Only)

Clicking a card selects it (or deselects if already selected). Selection state is communicated via:

- **Fill:** Primary colour tint (`color-mix(in srgb, var(--pf-v6-global--primary-color--100) 10%, #ffffff)`)
- **Border:** 3px primary colour stroke (vs. 1px default)

Selection triggers the `onSelectElement` callback, which typically opens the element details panel in the navigator.

## Icon Rendering

Cards may display an icon to the left of the alpha name. Icons are resolved from the alpha's `assetNames` array by finding the entry where `type === "icon"` and looking up the corresponding Asset object.

In the interactive form, icons are rendered via the `IconAsset` React component at 18px size. In the static form, icons are rendered as inline HTML within `foreignObject`, with font-character assets generating the appropriate `@import` CSS rules in the SVG's `<defs>` block. Icon font CDN URLs are collected from all referenced assets and deduplicated.

## Text Handling

Alpha names are displayed using the display alias system (`AliasedName` in the interactive form, `DisplayAliasFn` in the static form), which allows practices to define shorter display names for elements. In the static form, names are truncated to 22 characters with an ellipsis to prevent overflow.

## Static Export Specifics

The static SVG export (`generateConcernsOverviewSvg`) produces a self-contained SVG string with:

- An explicit `xmlns` declaration for standalone SVG file compatibility
- `width` and `height` attributes set to the computed dimensions (minimum 400px wide)
- A matching `viewBox` for proper scaling
- Optional `<defs>` block with `@import` CSS rules for icon font families
- All coordinates computed in pixels, no CSS variables or theme dependencies

## Implementation Parity

Both implementations must produce the same visual layout. The shared invariants are:

1. Same layout constants (card dimensions, gaps, indents, thresholds, connector colours)
2. Same tree-building algorithm (recursive, depth-first, collecting `mapsTo` then `contributesTo` children)
3. Same multi-column split logic (prefix-sum balancing, 70% acceptance, max 3 columns)
4. Same connector geometry: orthogonal lines for `contributesTo`, vertical bar for `mapsTo`
5. Same focus group ordering and partitioning

Differences between the two forms are limited to:

| Concern | Interactive | Static |
|---------|------------|--------|
| Card fill | Score-based colouring | White (`#ffffff`) |
| Selection | Click-to-select with visual feedback | None |
| Icons | `IconAsset` React component | Inline HTML in `foreignObject` + `<text>` fallback |
| Text | `AliasedName` component | Plain text with 22-char truncation |
| Row wrapping | CSS flexbox | Computed `wrapLayout` with `WRAP_WIDTH` |
| Font loading | Browser-managed | `@import` rules in SVG `<defs>` |

## Open Questions

1. **Score colouring in static export.** Should the static export include score colouring? This would require either pre-computing scores at export time or accepting that static scores become stale.
2. **Accessibility.** The interactive form uses `cursor: pointer` but does not provide keyboard navigation or ARIA labels for the SVG cards. Should the cards be rendered as focusable elements with `role="button"`?
3. **MapsTo card styling.** Currently, mapsTo and contributesTo children use identical card styling (same dimensions, fill, border). Should mapsTo children have a distinct card appearance (e.g., a subtle blue tint or dashed border) to reinforce the connector colour distinction?

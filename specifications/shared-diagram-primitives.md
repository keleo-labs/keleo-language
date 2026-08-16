# Shared Diagram Primitives

Common layout constants, rendering rules, and conventions shared across the diagram specifications in this directory. Individual diagram specs reference this document for shared behaviour and define only their unique aspects (card shapes, connector styles, tree depth, and diagram-specific algorithms).

**Consuming specifications:**

- [Concerns Overview Diagram](concerns-overview-diagram.md) — alpha hierarchy visualisation
- [Activities Overview Diagram](activities-overview-diagram.md) — activity space and activity visualisation
- [Dependency Diagram](dependency-diagram.md) — document dependency tree (uses its own layout constants but shares static export conventions and icon rendering)

## Layout Constants

These constants govern card dimensions, spacing, and layout thresholds. All diagram specifications that render cards within focus groups use these values unless they define overrides.

| Constant | Value | Purpose |
|----------|-------|---------|
| `CARD_WIDTH` | 180px | Width of every card |
| `CARD_HEIGHT` | 48px | Height of every card |
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

## Focus Group Rendering

Elements are partitioned into focus groups by their `focusName` property. Each focus group is rendered as a vertical section:

- A **heading** displaying the focus name (bold, 14px sans-serif).
- An optional **description** in italic (11px). In the static export, descriptions are truncated to 80 characters.

**Ordering:** Focus groups are ordered by the `seq` (or declaration order) of the corresponding Focus object in `baseline.focuses`. Elements with no `focusName` or with a name not matching any Focus object are placed in an "Other" group at the end.

## Score Colouring (Interactive Only)

In the interactive form, card fill colour is determined by the element's coverage score (see the [Scoring specification](scoring.md) for how scores are computed). The score-to-colour mapping uses a white-to-blue intensity scale:

| Score | Fill |
|-------|------|
| 0 | `#FFFFFF` (white) |
| 1 | `#E7F1FA` (light blue) |
| 2 | `#BEE1F4` (mid blue) |
| 3+ | `#73BCF7` (dark blue) |

**Selection styling:** The selected card overrides score colouring with a primary-colour tinted background (`color-mix(in srgb, var(--pf-v6-global--primary-color--100) 10%, #ffffff)`) and a 3px primary-colour border (vs. 1px default).

**Static export:** All cards use a white fill (`#ffffff`) with a `#d2d2d2` border. Score colouring is not included because the static export is a structural snapshot, not a live analysis tool.

## Icon Rendering

Cards may display an icon to the left of the element name, resolved from the element's `assetNames` array by finding the entry where `type === "icon"` and looking up the corresponding Asset object.

| Form | Rendering approach |
|------|--------------------|
| **Interactive** | `IconAsset` React component at 18px size |
| **Static** | Inline HTML within `foreignObject`, with font-character assets generating `@import` CSS rules in the SVG's `<defs>` block. Icon font CDN URLs are collected from all referenced assets and deduplicated. |

## Text Handling

Element names are displayed using the display alias system:

- **Interactive:** `AliasedName` component
- **Static:** `DisplayAliasFn` function, with names truncated to a diagram-specific character limit to prevent overflow (e.g., 22 characters for concerns, 20 for activities)

Individual diagram specs define their own truncation limits based on available content width within their card shape.

## Row Wrapping

Trees within a focus group are arranged horizontally and wrap to new rows when they exceed the available width.

| Form | Wrapping mechanism |
|------|--------------------|
| **Interactive** | CSS flexbox with `flex-wrap: wrap` and a 24px gap |
| **Static** | Computed `wrapLayout` algorithm: place trees left-to-right separated by `TREE_GAP_X`; when the next tree would exceed `WRAP_WIDTH`, start a new row below, separated by `ROW_GAP`. Track the maximum row width to determine the SVG viewport width. |

Both forms produce equivalent wrapping behaviour.

## Static Export Conventions

All static SVG exports share these characteristics:

- **Namespace:** Explicit `xmlns` declaration for standalone SVG file compatibility
- **Dimensions:** `width` and `height` attributes set to the computed dimensions (minimum 400px wide)
- **Viewport:** A matching `viewBox` for proper scaling
- **Fonts:** Optional `<defs>` block with `@import` CSS rules for icon font families
- **Coordinates:** All positions computed in pixels — no CSS variables or theme dependencies
- **Colours:** Hardcoded hex values instead of CSS custom properties, making the SVG independent of any runtime theme

## Implementation Parity

Both interactive and static implementations of a diagram must produce the same visual layout. The shared invariants are:

1. Same layout constants (card dimensions, gaps, indents, thresholds)
2. Same tree-building algorithm
3. Same focus group ordering and partitioning
4. Same row-wrapping logic (equivalent output, different mechanism)

Differences between the two forms are limited to presentation concerns:

| Concern | Interactive | Static |
|---------|------------|--------|
| Card fill | Score-based colouring | White (`#ffffff`) |
| Selection | Click-to-select with visual feedback | None |
| Icons | `IconAsset` React component | Inline HTML in `foreignObject` + `<text>` fallback |
| Text | `AliasedName` component | Plain text with character truncation |
| Row wrapping | CSS flexbox | Computed `wrapLayout` with `WRAP_WIDTH` |
| Font loading | Browser-managed | `@import` rules in SVG `<defs>` |

Individual diagram specs extend this table with diagram-specific differences (e.g., connector colours, card shapes).

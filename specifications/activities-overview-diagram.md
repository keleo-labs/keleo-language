# The Activities Overview Diagram

## Objective

The Activities Overview Diagram provides a visual map of all activity spaces and their contained activities in a practice or method, organised by focus area. It gives practitioners an at-a-glance view of what a practice prescribes — the spaces of work and the specific activities that fill them.

The diagram exists in two forms:

1. **Interactive (navigator)** — a React component with click-to-select behaviour, score-based colouring, and integration with the element details panel.
2. **Static (export)** — a self-contained SVG string for use in downloadable static sites and PDF reports, with no runtime dependencies.

Both forms use the same layout constants and produce visually consistent output. When one changes, the other must be updated to match.

## Relationship to Existing Schema

The diagram renders directly from the `PracticeBaseline` type's structural properties:

- **`activitySpaces`** — the array of ActivitySpace objects, each with `name`, `focusName` (grouping key), `seq` (sort order within focus), optional `assetNames` (icon references), and an `activities` sub-array.
- **`activitySpaces[].activities`** — the array of Activity objects within each space, each with `name` and optional `assetNames`.
- **`focuses`** — the array of Focus objects providing names, descriptions, and ordering for the grouping sections.
- **`assets`** — the array of Asset objects for resolving icon references on cards.

Unlike alphas, which form arbitrary-depth trees via `contributesTo`, the activity hierarchy is always exactly two levels deep: activity spaces contain activities. This fixed depth simplifies the layout — there is no multi-column logic and no recursive tree building.

## Relationship to the Concerns Overview Diagram

The Activities Overview Diagram shares the same focus-group organisation, layout constants, connector line style, icon rendering strategy, and row-wrapping logic as the Concerns Overview Diagram. The key differences are:

1. **Card shape.** Activity spaces and activities use a chevron (arrow) shape instead of a rectangle, visually distinguishing "things you do" from "things you track."
2. **Tree depth.** Always two levels (space → activities), never deeper.
3. **Border style.** Activity space cards use a dashed border to visually distinguish containers (spaces) from concrete work items (activities).
4. **No multi-column layout.** The fixed two-level hierarchy does not produce the tall trees that trigger multi-column splitting.

## Visual Structure

```
┌─────────────────────────────────────────────────────────┐
│  Focus Heading                                          │
│  Focus description (italic)                             │
│                                                         │
│  ╔══════════▷   ╔══════════▷   ╔══════════▷             │
│  ║ Space A  ║   ║ Space B  ║   ║ Space C  ║             │  ← Space cards
│  ╚══════════╝   ╚══════════╝   ╚══════════╝             │     (dashed border)
│       │              │                                  │
│       ├── ╔════════▷ ├── ╔════════▷                     │
│       │   ║ Act 1  ║ │   ║ Act 1  ║                     │  ← Activity cards
│       │   ╚════════╝ │   ╚════════╝                     │     (solid border)
│       │              │                                  │
│       └── ╔════════▷ └── ╔════════▷                     │
│           ║ Act 2  ║     ║ Act 2  ║                     │
│           ╚════════╝     ╚════════╝                     │
│                                                         │
│  Focus Heading                                          │
│  ...                                                    │
└─────────────────────────────────────────────────────────┘
```

### Focus Groups

Activity spaces are partitioned by `focusName` and rendered identically to the Concerns Overview Diagram's focus groups: a bold heading, optional italic description, and the same ordering rules. See the Concerns Overview Diagram specification for details.

### Activity Space Trees

Each activity space is rendered as an independent two-level tree:

1. A **space card** (chevron shape, dashed border) at the top
2. **Activity cards** (chevron shape, solid border) indented below, connected by tree lines

Trees within a focus group wrap onto new rows using the same wrapping logic as the Concerns Overview Diagram.

## Card Shape

Both activity space and activity cards use a chevron (arrow) shape instead of a rectangle. The chevron is a five-point polygon with the right edge forming an arrow point:

```
SVG path: M 0 0 L 168 0 L 180 24 L 168 48 L 0 48 Z
          ╰─flat top─╯  ╰point╯  ╰─flat bottom─╯ ╰close╯
```

Expressed in terms of layout constants:

```
M 0 0
L (CARD_WIDTH - 12) 0
L CARD_WIDTH (CARD_HEIGHT / 2)
L (CARD_WIDTH - 12) CARD_HEIGHT
L 0 CARD_HEIGHT
Z
```

The arrow inset is 12px from the card width, creating a triangular point at the right edge. This reduces the usable content width to `CARD_WIDTH - 12` (168px).

### Activity Space vs Activity Cards

| Property | Activity Space | Activity |
|----------|---------------|----------|
| Shape | Chevron | Chevron |
| Border style | Dashed (`stroke-dasharray="4"`) | Solid |
| Border colour | `#d2d2d2` (default) or primary (selected) | `#d2d2d2` (default) or primary (selected) |
| Fill | Score-based (interactive) or white (static) | Score-based (interactive) or white (static) |

The dashed border on activity space cards signals that they are abstract containers — they define a space of work but are not directly actionable. Activities within them have solid borders, indicating concrete work items.

## Layout Algorithm

### Layout Constants

The Activities Overview Diagram uses the same constants as the Concerns Overview Diagram (see that specification for the full table). The relevant subset:

| Constant | Value | Purpose |
|----------|-------|---------|
| `CARD_WIDTH` | 180px | Width of every card (space and activity) |
| `CARD_HEIGHT` | 48px | Height of every card |
| `CARD_GAP` | 12px | Vertical gap between sibling activity cards |
| `VERTICAL_PADDING` | 12px | Extra padding after the last activity before the next tree |
| `INDENT` | 42px | Horizontal indent of activity cards from their space card |
| `LINE_OFFSET` | 21px | X-offset of the vertical connector line (half of `INDENT`) |

### Tree Building

For each activity space:

1. Place the **space card** at `(startX, startY)` with dimensions `CARD_WIDTH × CARD_HEIGHT`.
2. If the space has activities:
   - Place the first activity card at `(startX + INDENT, startY + CARD_HEIGHT + CARD_GAP)`.
   - Place subsequent activity cards at increments of `CARD_HEIGHT + CARD_GAP`.
3. Calculate tree dimensions:
   - **Width:** `CARD_WIDTH + INDENT` if activities exist, `CARD_WIDTH` otherwise.
   - **Height:** `CARD_HEIGHT + CARD_GAP + (activityCount × (CARD_HEIGHT + CARD_GAP)) + VERTICAL_PADDING` if activities exist, `CARD_HEIGHT` otherwise (plus `CARD_GAP` for inter-tree spacing).

### Row Wrapping

Trees are arranged horizontally within each focus group and wrap to new rows using the same `wrapLayout` algorithm as the Concerns Overview Diagram. In the interactive form, CSS flexbox handles wrapping; in the static form, the computed layout positions trees within a `WRAP_WIDTH` of 1100px.

## Connector Lines

Activity spaces connect to their activities using the same orthogonal connector style as the Concerns Overview Diagram:

1. **Vertical trunk.** A single vertical line from the bottom edge of the space card (`spaceY + CARD_HEIGHT`) to the vertical centre of the last activity card.
2. **Horizontal branch.** For each activity, a horizontal line from the trunk's x-position (`LINE_OFFSET`) to the activity card's left edge (`INDENT`), at the activity's vertical centre.

Line style: 3px stroke, `rgba(102, 102, 102, 0.8)`.

Connector lines are only rendered when the space has at least one activity. Empty spaces render as standalone chevron cards with no lines.

## Score Colouring (Interactive Only)

In the interactive form, both space and activity cards receive score-based fill colouring. The scores come from the ActivitySpace Coverage scoring pipeline (see the Scoring specification):

- **Space cards** are coloured by the composite activity space score.
- **Activity cards** are coloured by their individual activity score.

The score-to-colour mapping uses the same intensity scale as the Concerns Overview Diagram:

| Score | Fill |
|-------|------|
| 0 | `#FFFFFF` (white) |
| 1 | `#E7F1FA` (light blue) |
| 2 | `#BEE1F4` (mid blue) |
| 3+ | `#73BCF7` (dark blue) |

The static export does not include score colouring — all cards use a white fill.

## Selection Behaviour (Interactive Only)

Both space cards and activity cards are individually selectable. Clicking a card selects it (or deselects if already selected). The selection visual treatment is identical to the Concerns Overview Diagram: primary-colour tinted fill and 3px primary-colour border.

Selecting a space card and selecting an activity card are independent — selecting an activity does not select its parent space.

## Icon Rendering

Cards may display an icon to the left of the element name, resolved from the element's `assetNames` array. The rendering strategy is identical to the Concerns Overview Diagram: `IconAsset` component in the interactive form, inline HTML with `foreignObject` and `<text>` fallback in the static form.

## Text Handling

Element names use the display alias system. In the static form, names are truncated to 20 characters (slightly shorter than the Concerns diagram's 22 characters, to account for the reduced content width in chevron cards).

## Static Export Specifics

The static SVG export (`generateActivitiesOverviewSvg`) produces a self-contained SVG string with the same characteristics as the Concerns export: explicit `xmlns`, computed `width`/`height` (minimum 400px wide), matching `viewBox`, and optional `<defs>` block for icon font CSS.

The chevron path is pre-computed as a constant string and reused for all cards. Activity cards within a space are positioned using a `transform="translate(x, y)"` attribute on the `<path>` element.

## Implementation Parity

Both implementations must produce the same visual layout. The shared invariants are:

1. Same layout constants
2. Same chevron path geometry
3. Same two-level tree structure (space → activities)
4. Same connector line geometry
5. Same focus group ordering and partitioning
6. Same row-wrapping logic

Differences between the two forms:

| Concern | Interactive | Static |
|---------|------------|--------|
| Card fill | Score-based colouring | White (`#ffffff`) |
| Border style (space) | Dashed (`strokeDasharray="4"`) | Dashed (`stroke-dasharray="4"`) |
| Selection | Click-to-select with visual feedback | None |
| Icons | `IconAsset` React component | Inline HTML in `foreignObject` + `<text>` fallback |
| Text | `AliasedName` component | Plain text with 20-char truncation |
| Row wrapping | CSS flexbox | Computed `wrapLayout` with `WRAP_WIDTH` |
| Font loading | Browser-managed | `@import` rules in SVG `<defs>` |

## Open Questions

1. **Score colouring in static export.** Same question as the Concerns Overview Diagram — should pre-computed scores be baked into the static SVG?
2. **Empty activity spaces.** An activity space with no activities renders as a standalone chevron. Should empty spaces be visually distinguished further (e.g., a different fill or a "no activities" label)?
3. **Activity ordering.** Activities within a space are currently rendered in array order. Should they support a `seq` property for explicit ordering, consistent with how alphas and activity spaces are ordered within focuses?

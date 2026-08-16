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

The Activities Overview Diagram shares [common diagram primitives](shared-diagram-primitives.md) with the [Concerns Overview Diagram](concerns-overview-diagram.md). The key differences are:

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

Activity spaces are partitioned by `focusName` and rendered using the [shared focus group rendering](shared-diagram-primitives.md#focus-group-rendering) rules.

### Activity Space Trees

Each activity space is rendered as an independent two-level tree:

1. A **space card** (chevron shape, dashed border) at the top
2. **Activity cards** (chevron shape, solid border) indented below, connected by tree lines

Trees within a focus group wrap onto new rows using the [shared row wrapping](shared-diagram-primitives.md#row-wrapping) logic.

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

This diagram uses the [shared layout constants](shared-diagram-primitives.md#layout-constants). The constants most relevant to the activities layout are `CARD_WIDTH`, `CARD_HEIGHT`, `CARD_GAP`, `VERTICAL_PADDING`, `INDENT`, and `LINE_OFFSET`.

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

Trees are arranged horizontally within each focus group and wrap to new rows using the [shared row wrapping algorithm](shared-diagram-primitives.md#row-wrapping).

## Connector Lines

Activity spaces connect to their activities using orthogonal connectors (the `contributesTo` style from the [Concerns Overview Diagram](concerns-overview-diagram.md#contributesto-connectors-orthogonal-lines)):

1. **Vertical trunk.** A single vertical line from the bottom edge of the space card (`spaceY + CARD_HEIGHT`) to the vertical centre of the last activity card.
2. **Horizontal branch.** For each activity, a horizontal line from the trunk's x-position (`LINE_OFFSET`) to the activity card's left edge (`INDENT`), at the activity's vertical centre.

Line style: 3px stroke, `rgba(102, 102, 102, 0.8)`.

Connector lines are only rendered when the space has at least one activity. Empty spaces render as standalone chevron cards with no lines.

## Score Colouring (Interactive Only)

This diagram uses the [shared score colouring](shared-diagram-primitives.md#score-colouring) system. The activities-specific mapping:

- **Space cards** are coloured by the composite activity space score (see [Scoring specification](scoring.md#composite-space-score)).
- **Activity cards** are coloured by their individual activity score.

## Selection Behaviour (Interactive Only)

Both space cards and activity cards are individually selectable. Clicking a card selects it (or deselects if already selected). The selection visual treatment is identical to the Concerns Overview Diagram: primary-colour tinted fill and 3px primary-colour border.

Selecting a space card and selecting an activity card are independent — selecting an activity does not select its parent space.

## Icon Rendering

Cards may display an icon to the left of the element name, resolved from the element's `assetNames` array. See [shared icon rendering](shared-diagram-primitives.md#icon-rendering) for the rendering strategy.

## Text Handling

Element names use the [shared text handling](shared-diagram-primitives.md#text-handling) system. In the static form, names are truncated to 20 characters (shorter than the standard 22, to account for the reduced content width in chevron cards).

## Static Export Specifics

The static SVG export (`generateActivitiesOverviewSvg`) follows the [shared static export conventions](shared-diagram-primitives.md#static-export-conventions). The chevron path is pre-computed as a constant string and reused for all cards. Activity cards within a space are positioned using a `transform="translate(x, y)"` attribute on the `<path>` element.

## Implementation Parity

Both implementations follow the [shared implementation parity template](shared-diagram-primitives.md#implementation-parity). The activities-specific invariants are:

1. Same chevron path geometry
2. Same two-level tree structure (space → activities)
3. Same connector line geometry (orthogonal only — no `mapsTo` bar connectors)
4. Same dashed border on space cards (`stroke-dasharray="4"`)

The only activities-specific difference beyond the [shared differences](shared-diagram-primitives.md#implementation-parity) is the dashed border style on space cards, which uses `strokeDasharray="4"` in the interactive form and `stroke-dasharray="4"` in the static form.

## Resolved Design Decisions

### 1. Score colouring in static export

**Question:** Should pre-computed scores be baked into the static SVG?

**Decision:** No. Static export remains white-fill for all cards.

**Rationale:** The static export is a structural snapshot, not a live analysis tool. Scores require the full scoring pipeline, which is not available at export time. Baking stale scores would mislead users. Consistent with the [Concerns Overview Diagram](concerns-overview-diagram.md#resolved-design-decisions) decision.

### 2. Empty activity spaces

**Question:** Should empty activity spaces (no activities) be visually distinguished further (different fill, "no activities" label)?

**Decision:** No further distinction needed. Empty spaces render as standalone chevron cards with no additional styling.

**Rationale:** The absence of connector lines and child cards already signals "no activities defined." Adding labels or different fills would add visual noise for a rare edge case. If an activity space has no activities, the practice author should either add activities or remove the space — the visual gap is the signal.

### 3. Activity ordering

**Question:** Should activities support a `seq` property for explicit ordering, consistent with how alphas and activity spaces are ordered within focuses?

**Decision:** Yes, activities should use `seq` for ordering when available. Current behaviour (array order) is the fallback.

**Rationale:** Consistent with the ordering mechanism used by alphas, states, checklist items, and activity spaces. The schema does not currently define `seq` on `Activity` — this is an identified schema gap to be addressed in a future minor version bump.

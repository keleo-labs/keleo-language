# Scoring and Visual Colouring

## Objective

The scoring system provides quantitative measures of practice coverage and project progress. These scores drive a visual colouring system that gives users an at-a-glance understanding of where a practice is well-defined and where gaps exist, or — in the project context — how far along execution has progressed against defined milestones.

Scoring operates in two distinct contexts:

1. **Practice Analysis** (authoring-time) — measures how structurally complete a practice's definitions are, evaluating narrative depth, checklist coverage, cross-element contribution, and compositional breadth.
2. **Project Tracking** (execution-time) — measures progress through the practice's defined milestones, based on checklist completion and alpha/work product state advancement.

Both contexts produce normalised scores that map to a shared visual colouring vocabulary.

## Relationship to Existing Schema

Scoring is a **derived, runtime concern** — no scores are persisted in Practice Language documents. All scores are computed from structural properties already defined in the schema: narrative arrays, checklist arrays, `contributesTo` references, activity and work product associations, and (in the project context) `ChecklistState` entries on `AlphaInstance` and `WorkProductInstance`.

The scoring system depends on:

- **Focus grouping** — Alphas and ActivitySpaces are scored within the context of their parent Focus. The Focus hierarchy (Value, Solution, Endeavour, or custom focus names) provides the organisational structure for score presentation.
- **The merge algorithm** — When scoring an extension practice, the merged (resolved) practice is compared against the pure baseline to isolate the extension's contribution.
- **The Project type** — Project tracking scores depend on `ChecklistState` entries defined in the Projects specification.

## Practice Analysis Scoring

Practice analysis scoring evaluates how thoroughly a practice defines its elements. It answers the question: *"How well-specified is this practice?"*

All practice analysis scores are normalised to a **0–5 integer scale**, where 0 indicates no meaningful coverage and 5 indicates comprehensive coverage across all evaluated dimensions.

### Alpha Coverage Score

An Alpha Coverage Score measures how well a practice defines a single alpha — its narrative depth, state-level detail, and integration with other elements.

#### Dimensions

| # | Dimension | Max Points | Description |
|---|-----------|-----------|-------------|
| 1 | Narrative Coverage | 2 | Does the alpha have narrative descriptions explaining its purpose and usage? Base score of 1 if the alpha exists; +1 per narrative entry, capped at 2. |
| 2 | State Checklist Coverage | 4 | Do the alpha's states have actionable checklists? +1 for each state with a non-empty `checklist` array, normalised by total state count, then floored. Capped at 4. |
| 3 | Work Product Contribution | 2 | Is this alpha evidenced by work products? Binary: 2 if any work product's `levelsOfDetail[].contributesTo` references this alpha, 0 otherwise. |
| 4 | Activity Contribution | 2 | Is this alpha advanced by activities? Binary: 2 if any activity's `contributesTo` references this alpha, 0 otherwise. |
| 5 | Contributing Alphas | 2 | Do other alphas support this one? +1 per alpha whose `contributesTo` includes this alpha, capped at 2. |

**Maximum raw score:** 12 (2 + 4 + 2 + 2 + 2)

**Normalisation formula:**

```
score = round((5 × rawScore) / 12)
```

#### Extension Alphas

When a practice introduces new alphas via `contributesTo` (indicating they support a baseline alpha), these extension alphas are scored individually using the same dimensions. Their scores are then averaged and combined with the parent baseline alpha's score, with the combined result capped at the score ceiling for the baseline alpha.

This cap prevents extension alphas from inflating a baseline alpha's score beyond what the baseline's own structural completeness warrants. The extension can fill gaps but cannot compensate for fundamental baseline deficiencies.

### ActivitySpace Coverage Score

An ActivitySpace Coverage Score measures what an extension practice contributes to an activity space beyond what the baseline already provides. Unlike alpha scoring, this is explicitly **differential** — it evaluates the delta between the merged practice and the pure baseline.

This differential approach reflects the compositional nature of the Practice Language: a practice's value lies in what it adds to the baseline, not in restating what the baseline already defines.

#### Dimensions

| # | Dimension | Max Points | Description |
|---|-----------|-----------|-------------|
| 1 | Narrative Coverage | 2 | Narratives added by the extension beyond the baseline. |
| 2 | Activity Count | 3 | Number of activities added: 1 pt for 1+, 2 pts for 3+, 3 pts for 5+. |
| 3 | Alpha Contribution | 2 | Count of unique alpha names newly contributed to by extension activities. |
| 4 | Competency Diversity | 2 | Count of new competencies referenced by extension activities. |
| 5 | PersonaGroup Involvement | 1 | Binary: 1 if any new persona group references are introduced, 0 otherwise. |

**Maximum raw score:** 10 (2 + 3 + 2 + 2 + 1)

**Normalisation formula:**

```
score = round((5 × rawScore) / 10)
```

#### Individual Activity Score

Each newly added activity within a space is also scored individually:

| # | Dimension | Max Points | Description |
|---|-----------|-----------|-------------|
| 1 | Narrative Coverage | 2 | Narratives on the activity. |
| 2 | Alpha State Contribution | 3 | Number of alpha states referenced via `contributesTo`. |
| 3 | Work Product Contribution | 3 | Number of work products referenced via `contributesTo`. |
| 4 | Competency Levels | 2 | Number of recommended competency levels defined. |

**Maximum raw score:** 10

**Normalisation formula:** same as above.

#### Composite Space Score

The final ActivitySpace score is the average of the space-level score and the mean of its individual activity scores. This balances breadth (how much the space contributes overall) with depth (how well-defined each activity within it is).

### Focus-Level Aggregation

Alphas and ActivitySpaces are grouped by their parent Focus (e.g., Value, Solution, Endeavour). Scores are presented per-focus to highlight which areas of concern are well-covered and which have gaps. The aggregation is presentational — each element retains its individual score.

## Project Tracking Scoring

Project tracking scoring evaluates execution progress against the milestones defined in the resolved practice or method. It answers the question: *"How far along is this project?"*

### Alpha Instance Progress

An Alpha Instance's progress is derived from its `checklistStates` array, comparing completion against requirement:

1. **Identify applicable checklist items.** For the alpha instance's current state (referenced by `stateName`), collect all checklist items defined in the resolved practice's alpha state.
2. **Determine requirements.** If the project's `target` section includes `ChecklistState` entries for this instance, items marked `"not required"` are excluded from the denominator. All other items are required.
3. **Calculate completion ratio.**

```
progress = completedCount / requiredCount
```

Where:
- `completedCount` = checklist items with `state: "complete"` in the `current` section
- `requiredCount` = total checklist items minus those marked `"not required"` in the `target` section

4. **State advancement.** Progress can also be expressed as the ordinal position of the current state within the alpha's state sequence. If an alpha has 5 states and the instance is in state 3, ordinal progress is 3/5 (0.6).

### Work Product Instance Progress

Same logic as Alpha Instance Progress, but applied to `WorkProductInstance` and its `levelOfDetailName` / checklist items.

### Composite Project Progress

An overall project progress score can be derived by averaging alpha instance and work product instance progress scores, optionally weighted by the number of checklist items in each (so elements with more granular tracking contribute proportionally more to the composite).

## Simple Completeness Score

A lightweight structural heuristic provides a coarse ordering of documents by richness, useful for sorting in library views where the full scoring pipeline would be excessive.

| Element | Points |
|---------|--------|
| Alpha | 3 |
| Activity | 2 |
| Work Product | 2 |

For methods, the score is the sum across all constituent practices (recursively). This score is **not normalised** — it is only meaningful for relative ordering within a set of documents.

## Visual Colouring System

The visual colouring system translates scores into colour to provide immediate visual feedback. It uses two independent colour vocabularies: **score intensity** (how well-defined or how complete) and **focus identity** (which area of concern).

### Design Principles

1. **Score maps to intensity, not hue.** A single hue (blue) varies in lightness to encode score magnitude. This avoids colour-meaning conflicts with the categorical focus colours and works well for users with colour vision deficiencies.
2. **Focus maps to hue.** Each focus area has a distinct hue used for swimlane backgrounds, chart segments, and categorical grouping. These are soft, low-saturation tints — they organise, not compete with score intensity.
3. **Zero is visually distinct.** Score 0 uses neutral gray (not the lightest blue), signalling "not covered" rather than "minimally covered." This distinction matters — a score of 1 means the practice has started addressing this element; 0 means it has not.
4. **The palette is theme-aware.** Colours adapt to light and dark themes, maintaining contrast ratios and visual hierarchy in both.

### Score Intensity Scale

Score intensity uses a white-to-blue gradient with a gray anchor at zero. The mapping is defined for the normalised 0–5 range but is typically presented in coarser bands for visual clarity.

#### Reference Palette (Light Theme)

| Band | Score Range | Background | Border | Text | Semantics |
|------|-----------|------------|--------|------|-----------|
| None | 0 | `#F5F5F5` | `#D2D2D2` | `#8C8C8C` | No coverage — element not addressed |
| Low | 1 | `#E7F1FA` | `#73BCF7` | `#004368` | Minimal coverage — element exists but is skeletal |
| Medium | 2 | `#BEE1F4` | `#2B9AF3` | `#002952` | Partial coverage — some depth but gaps remain |
| High | 3–5 | `#73BCF7` | `#0066CC` | `#FFFFFF` | Good to comprehensive coverage |

The three-band visual grouping (Low/Medium/High) is intentional — finer gradations at the high end add visual noise without actionable insight. A score of 3 and a score of 5 both communicate "this area is well-covered"; the numerical score provides precision when needed.

#### Dark Theme Adaptation

Dark theme colours invert the lightness relationship while preserving the hue:

| Band | Score Range | Background | Border |
|------|-----------|------------|--------|
| None | 0 | `#1A1A1A` | `#3C3C3C` |
| Low | 1 | `#0A2A40` | `#1A5276` |
| Medium | 2 | `#0D3B5E` | `#2171A5` |
| High | 3–5 | `#1A5276` | `#2B9AF3` |

### Focus Identity Colours

Focus areas use categorical colours for swimlane backgrounds, radar chart segments, and grouping indicators. These are low-saturation tints that do not compete with score intensity.

| Focus | Solid / Stroke | Fill (Light Theme) | Fill (Dark Theme) |
|-------|---------------|-------------------|------------------|
| Value | `#4ADE80` (green) | `rgba(34, 197, 94, 0.14)` | `rgba(74, 222, 128, 0.16)` |
| Solution | `#FACC15` (yellow) | `rgba(234, 179, 8, 0.14)` | `rgba(250, 204, 21, 0.16)` |
| Endeavour | `#38BDF8` (blue) | `rgba(14, 165, 233, 0.14)` | `rgba(56, 189, 248, 0.16)` |
| Fallback | `#888888` (gray) | `rgba(128, 128, 128, 0.14)` | `rgba(128, 128, 128, 0.16)` |

The fallback colour applies to custom focus names that do not match the standard three. Implementations may extend the palette for custom focuses, but the standard three should always use these assignments.

### State Progression Colours

When displaying an alpha's state sequence (e.g., in a state table or checklist view), individual states use a generated HSL colour that progresses across a hue range to convey ordinal position:

```
hue = 210 + (stateIndex / max(totalStates - 1, 1)) × 90
colour = hsl(hue, 70%, 50%)
```

This produces a blue-to-purple gradient across the state sequence, providing visual differentiation without implying a traffic-light pass/fail judgement.

### Checklist State Colours

Individual checklist items in the project tracking context use semantic colours:

| State | Colour | Semantics |
|-------|--------|-----------|
| `complete` | `#3E8635` (green) | Item achieved |
| `not complete` | `#6A6E73` (dark gray) | Item pending |
| `not required` | `#8A8D90` (light gray) | Item excluded from scope |

### Colour Composition

Score intensity and focus identity compose without conflict because they occupy different visual layers:

- **Background layer:** Focus identity tints (swimlane bands, section backgrounds)
- **Element layer:** Score intensity fills (cards, badges, diagram nodes)
- **Detail layer:** State progression and checklist colours (inline indicators)

A card for an alpha in the Value focus would sit on a green-tinted background band, with its own fill ranging from gray (score 0) to saturated blue (score 3+). The two colour systems reinforce rather than contradict each other.

## Implementation Notes

### Scoring is Computed, Not Stored

Scores are derived at runtime from document structure. They are not persisted in Practice Language documents and must not be added to the schema. This ensures scores always reflect the current state of a document and avoids synchronisation problems between stored scores and document content.

Implementations should cache computed scores and invalidate on document change.

### Colour Definitions Should Be Centralised

Implementations should define the score intensity palette, focus identity colours, and state/checklist colours in a single shared location rather than duplicating values across components. This ensures visual consistency and simplifies theme adaptation.

### Accessibility

The blue intensity scale was chosen for its performance under the most common forms of colour vision deficiency (protanopia and deuteranopia). Implementations should additionally ensure:

- Minimum contrast ratio of 4.5:1 between text and background in all bands
- Score information is never conveyed by colour alone — numerical scores or textual labels must be available as alternatives
- Focus identity colours include non-colour differentiators (labels, icons, or spatial grouping) for users who cannot distinguish the hues

## Behavioural Scenarios

### Feature: Alpha Coverage Score Calculation

```gherkin
Scenario: Alpha with no coverage scores zero
  Given an alpha with no narratives
  And no states have checklists
  And no work product LOD contributes to this alpha
  And no activity contributes to this alpha
  And no other alpha declares contributesTo this alpha
  When the alpha coverage score is calculated
  Then the raw score is 0
  And the normalised score is 0

Scenario: Alpha with full coverage across all dimensions scores 5
  Given an alpha with 2 or more narratives
  And all states have non-empty checklists
  And at least one work product LOD contributes to this alpha
  And at least one activity contributes to this alpha
  And at least 2 other alphas declare contributesTo this alpha
  When the alpha coverage score is calculated
  Then the raw score is 12
  And the normalised score is round((5 × 12) / 12) = 5

Scenario: Normalisation rounding
  Given an alpha with a raw score of 7
  When the alpha coverage score is normalised
  Then the normalised score is round((5 × 7) / 12) = round(2.917) = 3
```

### Feature: Extension Alpha Cap

```gherkin
Scenario: Extension alphas cannot inflate a baseline alpha's score beyond its own completeness
  Given a baseline alpha "Platform" with a coverage score of 2
  And an extension practice adds alpha "Platform Capability" with contributesTo "Platform"
  And "Platform Capability" has a coverage score of 5
  When the combined score for "Platform" is calculated
  Then the combined score is capped at 2
  Because extension alphas fill gaps but cannot compensate for baseline deficiencies

Scenario: Extension fills gaps in a partially-covered baseline alpha
  Given a baseline alpha "Platform" with a raw score of 4 (no work product contribution, no activity contribution)
  And an extension practice adds activities and work products that contribute to "Platform"
  When the combined score for "Platform" is calculated
  Then the extension's contributions increase the raw score up to the baseline's structural ceiling
```

### Feature: ActivitySpace Coverage Score (Differential)

```gherkin
Scenario: Extension adds no activities to a space
  Given a baseline activity space "Architect and Build the Foundation"
  And the extension practice does not add any activities to this space
  When the activity space coverage score is calculated
  Then the score is 0
  Because the differential score measures only what the extension adds

Scenario: Extension adds activities with broad contributions
  Given a baseline activity space "Architect and Build the Foundation"
  And the extension practice adds 5 activities to this space
  And the added activities contribute to 2 unique alphas
  And the added activities reference 2 new competencies
  And the added activities introduce a new persona group reference
  When the activity space coverage score is calculated
  Then the raw score includes 3 points for activity count (5+ threshold)
  And 2 points for alpha contribution diversity
  And 2 points for competency diversity
  And 1 point for persona group involvement
```

### Feature: Project Tracking Progress

```gherkin
Scenario: All required checklist items complete
  Given an alpha instance in state "Operational" with 5 checklist items
  And the target section marks all 5 items as required
  And the current section marks all 5 items as "complete"
  When the alpha instance progress is calculated
  Then progress is 5 / 5 = 1.0

Scenario: Some items marked not required are excluded from denominator
  Given an alpha instance in state "Operational" with 5 checklist items
  And the target section marks 2 items as "not required"
  And the current section marks the remaining 3 items as "complete"
  When the alpha instance progress is calculated
  Then the required count is 3 (5 total minus 2 not required)
  And progress is 3 / 3 = 1.0

Scenario: No checklist items defined
  Given an alpha instance in a state with no checklist items defined
  When the alpha instance progress is calculated
  Then progress is 0
  Because there are no items to evaluate (zero denominator yields zero, not an error)
```

## Resolved Design Decisions

1. **Dimension weighting**

   **Question:** Should certain scoring dimensions (e.g., State Checklist Coverage) carry more weight than others to better reflect practice quality?

   **Decision:** Keep equal weighting as the default.

   **Rationale:** Equal weighting is the simplest approach and avoids embedding subjective quality judgements into the algorithm. If weighting is needed in future, it should be introduced as a schema extension (e.g., a configurable weight property on dimensions), not baked into the scoring formula. This follows the design principle of keeping it simple — complexity should be justified by a concrete need, not a hypothetical one.

2. **Extension alpha cap**

   **Question:** Should the cap on combined baseline + extension alpha scores be configurable or context-dependent?

   **Decision:** Keep the cap fixed.

   **Rationale:** The cap prevents extension practices from inflating a baseline alpha's score beyond what the baseline's own structural completeness warrants. Context-dependent caps add complexity without clear benefit — a well-structured practice should not need to override the cap. If a baseline alpha is sparsely defined, the correct fix is to improve the baseline, not to relax the cap.

3. **Project tracking aggregation**

   **Question:** Should composite project progress weight alpha instances differently from work product instances?

   **Decision:** Weight equally by instance count.

   **Rationale:** Equal weighting by instance count is the simplest heuristic and avoids privileging one element type over another without clear justification. If weighting is needed in future, it belongs in the Project type as explicit configuration (e.g., a weighting property on instances), keeping the scoring algorithm itself clean.

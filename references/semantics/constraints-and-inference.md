[< Back to Semantic Guidance Hub](../semantics.md)

## 16 Constraints and Inference Guarantees

This section states what the Practice Language guarantees about a document, in one place,
for someone building validation into a program rather than authoring a practice by hand.
Everywhere else in this guidance explains how to model well; this explains what the
language promises and who checks it.

Each guarantee below names the validator that enforces it. Where nothing enforces one,
it says so — the gaps are as useful as the guarantees, because a rule that only exists in
prose will be broken by any generator that has not read the prose.

### 16.1 How to read this section

A guarantee has three parts: the rule, the layer that expresses it, and the check that
enforces it.

| Layer | What it can express |
|---|---|
| Schema (`language.schema.json`) | Structure, types, required properties, cardinality, enumerated values |
| Semantics (this guidance) | Meaning, relationships between properties, rules that span elements |
| Validators (`validate/`) | Everything the schema cannot express but a program can check |

The schema alone accepts documents that are semantically wrong. A practice can satisfy
every structural constraint and still reference an alpha that does not exist, declare a
cycle in its containment hierarchy, or weight an outcome so that progress runs backwards.
That is why the validators exist and why conformance means passing them, not merely
validating against the schema.

Validator entry points:

| Document kind | Validator |
|---|---|
| Practice, Method | [`validate-practice.py`](../../validate/validate-practice.py) |
| PracticeBaseline | [`validate-baseline.py`](../../validate/validate-baseline.py) |
| Project | [`validate-project.py`](../../validate/validate-project.py) |
| IntegrationMapping | [`validate-integration-mapping.py`](../../validate/validate-integration-mapping.py) |
| Any, structure only | [`validate-schema.js`](../../validate/validate-schema.js) |

### 16.2 Reference guarantees

**Every cross-reference is a symbolic link resolved by exact, case-sensitive string
match.** Elements refer to each other by name, never by embedded copy or by identifier.
`alphaName`, `stateName`, `workProductName`, `patternName`, `activitySpaceName` and every
other `*Name` property is a name that must match a declared element exactly. Case,
whitespace and punctuation all matter; there is no normalisation step and no fuzzy
matching anywhere in the language.

*Enforced by* `validate_internal_integrity` and `validate_baseline_references` in the
practice validator, and the equivalents in the baseline and project validators.

**A consequence worth stating separately: two elements must not share a name.** Because
references resolve by name alone, a duplicate name makes every reference to it ambiguous
and there is no tie-break. Where two elements are genuinely different things, one has to
be renamed.

*Enforced by* `validate_internal_integrity`. Note that renaming is a breaking change for
any document that referenced the old name.

**A reference resolves within a defined scope**, not globally: the document itself, the
baseline it declares in `baselinePracticeName`, and the practices named in
`practiceDependencyNames`. An alias declared in `practiceElementAliases` is strictly
isolated — see [§4.3](composition.md#43-practice-aliasing-and-strict-isolation) — and does
not leak into the scope of other practices.

*Enforced by* `validate_baseline_references` and `validate_aliases`.

### 16.3 Structural guarantees

**No floating elements.** Every alpha declares `contributesTo` or `mapsTo` unless it is a
baseline alpha or a redeclaration of one. Every work product is connected to the alpha
hierarchy, either through `contributesToAlphaNames` on the work product or through
`contributesTo` on at least one of its levels of detail. An element with no structural
connection to the baseline hierarchy is an error, not a warning.

*Enforced by* `validate_redeclaration_vs_new` and `validate_work_product_purpose` in the
practice validator; `validate_alphas` in the baseline validator.

**`contributesTo` and `mapsTo` are mutually exclusive on an alpha.** A concern either
feeds into a parent concern or is a named variant of it; it cannot be both. The same
exclusivity once applied to `partOf` and `mapsTo` on work products and no longer does —
see [§7](work-products.md) for the `partOf` inheritance rule that replaced it.

*Enforced by* `validate_internal_integrity`.

**Cardinality minimums live in the schema and nowhere else.** `Pattern` requires at least
one `patternView`; `PatternView` requires `seq` and `alphaStates`; `Alpha` requires
`states` and `focusName`; `State` and `LevelOfDetail` require `seq` and `checklist`;
`WorkProduct` requires `levelsOfDetail`. A document missing any of these fails structural
validation before any semantic check runs.

*Enforced by* `validate_schema`, which runs first in every validator.

### 16.4 Acyclicity guarantees

Every directed reference graph in the language is a DAG. The full set, with the
traversal rules, is in [§14](acyclicity.md); the guarantee in summary is that cycles are
errors in all of the following:

- `Alpha.contributesTo` and `Alpha.mapsTo`, including chains that mix the two
- `WorkProduct.partOf` and `WorkProduct.mapsTo`, including mixed chains
- `PersonaGroup.personaGroupNames`
- `Background.alphaStates`, `Background.workProductLevels` and their instance-level
  counterparts
- `State.contributesToState`
- `PracticeBaseline.baselinePracticeNames` and `Practice.practiceDependencyNames`
- `ChangeRequest.supersedes`

*Enforced by* `validate_acyclicity` in the practice and baseline validators.

**Temporal edges are not part of this guarantee and are not cycles for this purpose.**
`PatternView.loopsBackTo` and `State.loopsBackTo` declare that work repeats. They say
nothing about prerequisites and do not license a cycle in any graph above — an alpha
whose states loop still may not have circular `Background` prerequisites. See
[§9.2a](execution-and-patterns.md) and [§6](alphas.md) for what a loop does and does not
mean.

### 16.5 Progression and measurement guarantees

**An outcome's recognised point carries full weight.** `MetricContribution.forecastWeights`
maps alpha states to weights and `ObjectiveContribution.forecastWeights` maps pattern
views to weights. In both, the state or view named by `recognizedAtStateName` or
`recognizedAtPatternViewName` must be present in the weights and must carry `1.0`. A
curve whose recognised point sits below full weight contradicts the schema's own
definition of the property.

*Enforced by* `validate_outcomes` in the practice validator.

**Weights do not fall back.** Once a contribution reaches full weight it stays there for
later states and views. Where a pattern or an alpha loops, the achieved forecast is the
highest weight reached on any pass, not the weight of the view or state currently being
worked — otherwise reported progress would drop each time a team iterated.

*Not enforced here.* The monotonicity check lives in keleo-pgen-llm's `assess-practice.py`
rather than in these validators, so a document validated only with `validate-practice.py`
can carry a decreasing curve beyond the recognised point.

**An alpha targets at most one state per pattern view.** A view that names two states for
the same alpha is ambiguous about what the phase is meant to achieve.

*Enforced by* `validate_internal_integrity`.

### 16.6 Composition guarantees

**Merging is specified, not implementation-defined.** [`merge.md`](../merge.md) is the
normative description of how documents compose: which arrays union, which scalars take
the overlay, and which properties are populated by the merge rather than authored.
A consumer that composes practices differently from that specification will disagree with
every other consumer.

**Merge-populated properties are not author-declared.** `Alpha.variants`,
`Alpha.supportingAlphas`, `WorkProduct.components`, `PracticeElement.specificity` and
`sourcePracticeName` are outputs of composition. A document that declares them by hand is
asserting something the merge may contradict.

*Enforced for* `specificity` by `validate_specificity`. The older merge-populated
properties are not checked.

**Suppression resolves by declaration precedence.** Where one practice suppresses an
element another still needs, the conflict is resolved deterministically rather than
arbitrarily: baselines outrank practices, each ordered by position in
`baselinePracticeNames` and `practiceDependencyNames`, with a practice from another family
taking its own baseline's position. See [§4.9](composition.md).

*Enforced by* `validate_suppression`.

### 16.7 What the language does not guarantee

Worth stating plainly, because each of these is something a reader may assume.

- **That prose is accurate.** No check reads a description against the structure it
  describes. An alpha can be named one thing and described as another.
- **That a checklist is sufficient.** `validate_checklist_quality` reports shape and
  wording problems, not whether the criteria actually establish the state.
- **That narrative element references resolve.** [§9.2](execution-and-patterns.md)
  requires a pattern view's `narrativeContexts` to reference elements within the
  NarrativeType named on the parent pattern. Nothing enforced this before
  `validate_orchestrations` was added, and documents predating that check may violate it.
- **That a document is complete.** Minimum counts for alphas, activities, patterns and
  citations are applied by the corpus tooling in keleo-pgen-llm, not by these validators.
- **That two documents in a bundle agree.** Cross-document consistency within a `.keleo`
  package is a packaging concern — see
  [`specifications/packaging.md`](../../specifications/packaging.md).

### 16.8 Breaking Changes and Migration

The schema follows semantic versioning, and a MAJOR bump means some document that was valid is no longer. Each one is recorded here with what to change.

#### 3.0.0 — `OrchestrationStage.relationship` is required

**What changed.** `relationship` was introduced in 2.22.0 as optional, defaulting to `sequential`. It is now required and has no default, so a stage that omits it is rejected.

**Who is affected.** Only documents declaring `patternOrchestrations`, a construct introduced in 2.21.0. No baseline or practice in the corpus used it at the time of the change, so the practical migration set was empty.

**How to migrate.** Add `"relationship": "sequential"` to any stage that does not declare one. That is exactly what the omission meant, so the change is mechanical and cannot alter behaviour.

**Why it was worth a major bump.** How a pattern is layered into an endeavour — following, alongside, inside, or on recognition of need — is a modelling decision that changes what the orchestration means. A default let the most consequential property on the stage be set by silence, and a reader could not tell a deliberate choice from an unconsidered one.

### 16.9 Conformance

A document conforms when it validates against `language.schema.json` **and** passes the
validator for its kind with zero errors. Warnings are advisory: they report things that
are usually wrong but legitimately may not be, and a conforming document may carry them.

The schema version a document targets is declared in its own `schemaVersion` property and
checked against the version in the schema's root `$comment`. A document declaring a
newer minor version than the schema in use may rely on properties that schema does not
have; a document declaring an older one remains valid, because minor versions only add
optional properties.

*Enforced by* `validate_schema_version` in every validator.

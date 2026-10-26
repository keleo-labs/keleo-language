[< Back to Semantic Guidance Hub](../semantics.md)

## Project hierarchy and reporting

Schema **4.0.0** separates persistent project identity, ownership, reporting and
delegation. These contracts let consumers connect independent projects without
changing their methods or interpreting relationship prose. The executable
requirements are in [project-hierarchy.feature](../../specifications/project-hierarchy.feature).

### Identity and ownership

Every Project requires `projectId`, a UUID generated once by its writer. Use
UUIDv4 when assigning a new identity. Preserve it through renames and moves;
copying a project to create an independent project requires a new UUID.

`Project` already extends `PracticeElement`. Its required `name` and
`description` describe it to a reader; `projectId` identifies it to a resolver.
Compare UUID values, so uppercase and lowercase representations identify the
same project. Two projects may share a name. Methodology elements continue to
use their existing symbolic names.

`parentProject` identifies at most one owning parent. Derive the parent's children
by finding projects with that parent reference. `projectReferences` are
non-owning links and establish neither child membership nor a contribution to
progress or value. Ownership has no prescribed business levels or depth limit.

`ProjectItemReference` identifies a project, an exact instance collection and an
instance name. Cycle collections also require `cycleName`. A reference to a
current assessment is distinct from a reference to its plan declaration or
target. Do not search other collections to repair an unresolved reference.
`ProjectReportReference` identifies a named report separately.

### Supplied snapshots and resolution

A `ProjectCatalogue` contains `projects`, each with a complete `document` and
an opaque `revision`. Consumers must change that revision whenever the source
document changes. A catalogue is the caller's authoritative snapshot for this
validation; validators cannot detect files the caller omitted.

Optional `containingProjectId` records the physical parent observed by a
consumer that mirrors ownership in folders. A disagreement with `parentProject`
is an error. Validators report it without choosing an authority or moving files.

Reject duplicate UUIDs, self-ownership and ownership cycles. An absent owner is
unresolved, never an implicit root. Without a catalogue, external resolution is
unchecked and unresolved references are warnings; preflight requires the inputs
needed by an operation. With a catalogue, unresolved ownership is an error.
Missing report sources remain reporting gaps.

Methodology contexts arrive separately through `--document`. Referenced
methods, practices and baseline dependencies form the context for type and
assessment resolution. Project names are not inserted into a shared name index
to resolve UUID references.

### Discoverable definitions

`ReportDefinition`, `ReportingMetricDefinition`, `ReportBinding` and
`ReportingRequirement` extend `PracticeElement`. Creation templates, their
variants, named selectors and creation reporting bindings do so too. Each has
required `name` and `description`, with optional tags, narratives and asset
references for discovery and explanation.

Narrative types, citations and assets resolve in the enclosing aggregate and
its declared methodology scope. The new elements participate in metadata
validation, including nested elements and method-level templates. References,
values, provenance, previews, diagnostics and receipts retain their smaller
purpose-specific shapes.

Specificity and suppression retain their methodology-composition meaning.
They cannot suppress local project reports or remove inherited reporting
obligations. An authored `specificity` remains invalid merge output.
Creation templates compose atomically: only whole inherited template versions
support visibility controls. Change nested selectors or variants through a new
template version rather than a partial suppression overlay.

### Reporting contracts and outcome values

A report declares its semantic metric, aggregation, unit and period. The metric's
`metricId` and exact semver `version` identify meaning independently of its name.
Equal identity/version with different semantic descriptions is a conflict.
Matching display names or units is insufficient evidence of compatible meaning.

Periods are half-open timestamp intervals: `start` is included and `end` is
excluded. Require start before end. Use an explicit unit, including `1` for a
unitless quantity or `count` for attainment. No currency conversion is inferred.

Sum reports require `valueKind` from `OutcomeValueKind`:

- `actual` selects an outcome instance's `actualValue`, or explicitly requested
  derivation using the outcome's recognition rules.
- `forecast` selects `forecastValue`, or explicitly requested derivation using
  the existing metric contributions and originating forecast weights.
- `target` selects `targetValue`. It requires an explicit numeric target and
  applies no forecast or recognition weighting.

`Outcome` remains the methodology definition: its `measureDescription`,
`metricContributions` and `objectiveContributions` describe measurement.
`OutcomeInstance` owns project-specific targets, measurements and author-set
status. Reporting neither writes derived values into it nor changes its status.
Never parse the instance's free-text `measure` into a target or substitute a
forecast when `targetValue` is missing.

A target report summing children with targets 100 and 200 yields 300. The
parent's independently declared target of 400 remains 400. Include a distinct
parent-local contribution only through an explicit additional binding.

### Sources and assessed attainment

A report binding selects an outcome in its own project, a current assessment
with an explicit local target, or a named report from an immediate owning child.
It does not read arbitrary descendants directly. Ownership and non-owning
references alone contribute nothing.

Outcome bindings explicitly choose `recorded` or `derived` values. Numeric
sources declare `reportingSource` metadata: source identity, semantic metric and
period. Units come from the numeric source. A missing measurement, incompatible
contract or unresolved source is a gap, not zero.

Derived numeric reporting follows the existing canonical metric chain:
current alpha assessments, explicit evidencing work products, canonical current
work-product metrics and explicit instance containment. Actual derivation
requires a recognition state. Forecast derivation applies source weights once.
Targets cannot use that derivation.

`attainmentCount` binds current assessments to explicit target or cycle
objectives. Resolve each assessment in its own method. Its current state or
level must reach its goal, with required checklist completions and evidence.
For cyclical types, a later sequence number alone does not prove attainment.
Missing evidence records non-attainment; an unresolved assessment definition
creates a reporting gap. No unrelated lifecycle percentages are averaged.

### Contribution identity and results

`ReportingSource.identity` contains a namespace and source key. Prefer a
namespaced external identity when one is available. Otherwise use
`project:<canonical UUID>` and an explicit local source key. Delegation
preserves the original identity instead of inventing a second contribution.

Each contribution retains its original and current source references, metric,
period, value kind and input revision. The identity used for deduplication is
namespace, source key, metric identity/version, period and value kind. Revision
is a fact about that identity, not permission to count another copy.

Repeated identical lineage counts once. Conflicting values, revisions or
weighting create a diagnostic; input order cannot select a winner. Keep the
paths available through `via`. Without shared identity, tools cannot claim to
detect semantic duplicates.

A `ReportResult` contains the report reference, `calculatedAt`, contribution
rows, declared child coverage, diagnostics and `complete`. A complete result
requires its headline `total`. An incomplete result prohibits that total but
retains valid contributor rows. Validation checks the supplied facts and total
against the snapshot; consumers implement production calculations.

### Creation templates and previews

Practices and methods may embed versioned `projectCreationTemplates`. A template
declares the applicable root kind/type, named selectors and one or more child
methodology variants. A default variant is a suggestion, not execution authority.

Selectors identify the root, explicitly named local items or direct associations
whose `relationshipKind` and direction are explicit. Relationship labels are
prose. Neither name similarity nor a type-level relationship creates an instance
association or expands the selected scope.

A variant declares instance/type mappings, state and level correspondences,
state-scoped checklist mappings, selected action destinations and reporting
bindings. Creation reporting bindings use local child references in the template;
the preview expands them using the chosen child UUID. They support actual,
forecast, target and evidenced-attainment reports.

`ProjectCreationPreview` records the operation identity, exact template/version,
parent and source item, selected variant, proposed child Project, expanded
selection, mappings and source revisions. `sourceSnapshots` records the
transferred assessments and actions with their original references, timestamps
and attribution. The preview does not write either project.

Pin the parent catalogue revision and every consulted methodology document.
Methodology revisions use `sha256:` followed by the SHA-256 digest of UTF-8 JSON
serialized with sorted keys, no insignificant spaces and unescaped Unicode
(`json.dumps(document, sort_keys=True, separators=(',', ':'), ensure_ascii=False)`).
This is the validator's defined snapshot encoding, not the document's release
version. Stale inputs require a new preview and renewed confirmation.

### Assessment transfer and ownership commitment

Copy assessments only when the method and type semantics match. Across methods,
use explicit state, level and checklist mappings. Missing or ambiguous mappings
leave the destination unassessed: retain its plan declaration and omit its
`current` row. Never invent a lifecycle state for "unassessed".

Transfer evidence by reference while preserving its contents. Only explicitly
selected open actions transfer, with resolved child assignments, cycle
destinations and rewritten references. Closed actions stay historical.

The parent owns selected detail until its delegation record is `committed`.
Prepared or failed child writes remain outside the active catalogue. A failed
operation retains the parent's detail. Storage transactions, staging and
recovery belong to the consumer.

A committed record retains the preview and attributed history, identifies the
child and names the parent's summary report. Transferred detail cannot remain
an independently editable parent assessment. Retain the parent root declaration
and its own acceptance targets; any subsequent parent assessment evaluates
those parent-owned criteria. Child completion never completes them implicitly.

Retrying the same successful operation identifies the existing child. Reusing
its identity with different inputs, recording a second child or activating two
owners is invalid. Historical successful records are checked as receipts rather
than replayed against later source revisions.

### Local recommendations and authority

`RecommendationCard.localRecommendation` is an alternative to the existing
journal/recommendation reference. It records the local source, rationale, advice
and preview without manufacturing an external signal. The existing inbox,
reviewing, accepted, dismissed and applied states remain the workflow.

Manual creation requires confirmation of the selected method and scope.
Automatic creation requires a policy naming the exact template/version and
permitted source item. Revocation affects future attempts without invalidating
earlier authorised receipts. Acceptance alone is not application: success must
identify the operation and child and resolve to the committed delegation.

### Inherited requirements and coverage

`reportingRequirements` declare versioned reporting obligations. A local
`reportingRequirementBindings` entry maps a requirement identity/version to a
named report. Descendants inherit reporting obligations, not methods, teams,
targets or project contents.

Resolve declarations ancestor-first. The same requirement identity must retain
its pinned version and measurement contract, including actual/forecast/target.
Accumulate all-child coverage obligations, retain the strictest age limit and
permit exclusions only when every applicable declaration permits them. A
descendant may add requirements but cannot silently weaken inherited ones.
Conflicts retain references to both declarations and withhold affected reports.

Persist `childCoverage` with either binding names or an exclusion reason for
each configured child. All-child requirements compare that scope with the
catalogue's immediate children. A new unmapped child is an alignment gap. A
configured child that disappears remains a gap rather than reducing the total.
Exclusions remain inspectable and cannot override an ancestor's obligation.

### Source freshness and diagnostics

Freshness uses `observedAt`, then `synchronizedAt`, then the named integration's
`lastSyncedAt`. A missing or invalid timestamp is unknown; a future timestamp
cannot satisfy an age limit. `calculatedAt` never proves recent observation or
external import. Without an age limit, unknown freshness remains visible.

Report diagnostics carry stable codes, affected project/report, offending
source and, for inherited obligations, requirement identity and originating
project. Conflicts retain related declaration references. CLI output separates
`reporting.alignmentComplete` from local `valid`.

Malformed documents, contradictory ownership and unsafe operations are validation
errors. Missing mappings, freshness and incompatible reporting contributions
withhold affected totals while local project work remains usable. A supplied
result that falsely claims completeness is itself an error. Unrelated reports
remain available.

### Migration from schema 3

Schema 4 deliberately rejects Projects without UUIDs. Assign and persist one
UUID per existing project, update project package entries and update applicable
`schemaVersion` declarations. Do not regenerate UUIDs on each load or derive
them from names or paths.

Consumers must adopt UUID lookup before reading schema-4 projects. Existing
methodology names, local instance references and independently owned outcome
targets retain their meaning. Catalogues, previews and report results are API
envelopes validated through their `$defs`, not new package document kinds.

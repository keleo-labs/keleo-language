[< Back to Semantic Guidance Hub](../semantics.md)

## External signals and contextual recommendations

Schema **3.3.0** adds signal rules, a standalone `SignalJournal` and project-owned
recommendation cards. These retain why external content matters without treating
an inferred opportunity as an existing external-system record. See the
[behavioural specification](../../specifications/external-signals.feature) and
[RFE #23](https://github.com/keleo-labs/keleo-language/issues/23).

### Discovery rules

An `IntegrationMapping` must contain a non-empty `entityMappings` array, a
non-empty `signalRules` array or both. Existing entity mappings retain their
synchronisation meaning. Signal rules produce journal records and grant no
authority to write project data.

Each `SignalRule` names a query in the same mapping through `queryTemplateName`.
It declares its execution `tier`, interpretation instructions and recommendation
guidance. Optional `targets` reuse `MappingTarget` to identify relevant alpha,
work product, outcome or action targets. Rule names must be unique within the
mapping. Query parameters retain their existing service-connection mechanism;
scheduling and subscriptions belong to the automation.

Mappings declaring signal rules require `schemaVersion` and a semver `version`
so journal records can pin their provenance. Existing entity-only mappings keep
their previous metadata requirements.

For the annual-report example, a query finds reports for the company supplied
in `service.parameters`. Its rule identifies explicit IT investment, establishes
which company the passage concerns and proposes investigation using Initiative
and Opportunity. An ambiguous company match should produce advice for review
rather than executable proposals.

The tiers describe execution mechanisms, not measured probabilities or
permission levels. Retrieved content is untrusted evidence: instructions embedded
in a report must not alter rules, policies or application authority.

### Journal identity and evidence

A journal is identified by `name` and discriminated by `"journalKind": "signals"`.
It requires semver `version` and `schemaVersion`, plus `signals` and
`recommendations` arrays, either of which may initially be empty. Its package
inventory `documentType` is `signalJournal`.

An `ExternalSignal` requires a stable `name`, `sourceKey`, source link,
`discoveredAt` timestamp and interpretation. The source uses `ExternalLink`
and must include a non-empty `uri`. Retain relevant text in `excerpt` and its
location in `source.pages` when available. Record `publishedAt` only when known;
discovery time is not publication time. The fixture excerpt is invented example
content, not a quotation from a real report.

`sourceKey` identifies the source version and extracted finding, not the search
run. Use a publisher identifier or canonical URI with a revision, digest or
publication identity, plus a stable finding key. Multiple findings in one report
have different keys. Repeated discovery reuses the existing key and signal name.

Names are unique within each journal array. Materially revised evidence receives
a new name and source key, with `supersedes` referencing its predecessor. Revised
recommendations likewise receive new names and may reference a predecessor
through `supersedes`. These references resolve within the journal and must be
acyclic. Retain old records while cards reference them; never rewrite a reviewed
proposal or transfer approval to a revision.

### Relevance and recommendations

A `SignalRecommendation` references one or more `signalNames` in its journal.
Its `context` identifies a `practice`, `method` or `project` by `documentName`.
Optional `elements` identify methodology elements by `targetKind` and
`elementName`, resolved in the composed methodology, including for project
contexts. Methodology advice requires no project.

Every recommendation retains `advice`, `rationale`, `createdAt` and rule
provenance: `integrationMappingName`, exact semver `mappingVersion` and
`ruleName`. Preserve that mapping version for audit and preflight checks.
Validators accept several versions of the same mapping together.

Reuse an existing recommendation when evidence, rule version, context and
response are unchanged. The validator rejects records with those same fields
irrespective of name or creation timestamp. It cannot determine whether
differently worded recommendations mean the same thing; runtimes must preserve
stable identities instead of regenerating prose as a deduplication strategy.

Methodology advice may reference a reviewed `ChangeRequest.changeId` using
`changeRequestName`. The change request must target the same methodology name
and type. Its existing lifecycle governs review; the reference grants no
authority. Projects remain excluded from change-request targets.

### Typed project proposals

Only project-context recommendations may contain `proposals`. Advice without
proposals can be accepted without application. Each proposal declares
`operation` (`create` or `update`), `collection` and a complete `value`.
Collections are existing project arrays:

- `plan.pattern.alphaInstanceNames` and `plan.pattern.workProductInstanceNames`
  for tracked instance declarations.
- `current.alphaInstances` and `current.workProductInstances` for assessments.
- `target.alphaInstances` and `target.workProductInstances` for desired states.
- `outcomes` and `actions` for project-level outcomes and backlog tasks.

The schema validates `value` against the existing type for that collection.
An update replaces the named object and requires `previous`, the complete
object expected before replacement. Both objects must have the same name.
Creates omit `previous` and require an absent target name. Renames, deletions,
cycle changes and arbitrary JSON paths are outside this format.

Targets must be unique within a recommendation. Proposals form one atomic unit:
preflight checks the whole proposed result, then the runtime commits all changes
or none. A plan declaration does not imply an assessed state. Include a separate
typed assessment proposal when evidence supports recording a state.

### Project cards and Kanban

`Project.recommendations` contains cards with their own `name`, referencing a
journal and recommendation through `journalName` and `recommendationName`.
Only one card per journal/recommendation pair may exist in a project.
Project-context recommendations belong to their named project. Methodology advice
may be shared by projects directly referencing that practice or method, with
independent cards and decisions.

The five fixed `status` values are Kanban columns. A new card starts in `inbox`;
users may move it to `reviewing`, then `accepted` or `dismissed`, or decide
directly from the inbox. Decisions and applied cards require `decidedAt` and
`decidedBy`. Optional `assignedTo` entries reference team members. Append
decisions and rationale to `notes` when changing a decision to preserve context.

Acceptance performs no write. Successful application moves an accepted card to
`applied`; advice without proposals remains accepted. Failed attempts leave the
card accepted for retry. A team may subsequently dismiss it while retaining
failed attempts and recording the later dismissal. A dismissed card with no
attempts may reopen for review; otherwise retain its decision and use notes for
further investigation. Applied cards are terminal. Revised recommendations
start new inbox cards and require new decisions.

### Authority and application receipts

Omitting `recommendationPolicies` grants no automatic authority. A policy pins
`integrationMappingName`, `mappingVersion` and `ruleName` and lists allowed
`operations` and `collections`. Automatic application names one policy covering
every proposal; partial grants cannot be combined. Policies cannot authorise
practice or method changes. Policy editing requires the project's trusted
authorisation mechanism, outside source content and generated recommendations.

Each application receipt records a unique attempt `name`, `attemptedAt`,
`actor`, `mode` and `outcome`. Automatic mode requires `policyName`; manual
mode represents user-authorised application and omits it. Failure requires
`error` without results. Success requires `results` identifying every proposed
collection and instance name exactly once, without an error. Successful result
references must resolve in the project.

Receipts are chronological. A card may have at most one success and no subsequent
attempts. Retain policies referenced by historical receipts. Set `revokedAt` to
withdraw a policy's authority from that instant; receipts for earlier attempts
remain valid, while attempts at or after revocation are rejected. Snapshot validation
checks declared grants and receipt consistency, but cannot prove who authorised
a policy or that an external writer executed a change.

Immediately before application, validate loaded context and compare update
preimages against current project data. Pending cards referencing superseded
recommendations or signals are invalid for application; historical applied cards
remain valid. Use the project/journal/recommendation identity as the idempotency
key. Commit changes and the successful receipt together under a transaction or
compare-and-swap operation. Reconcile uncertain outcomes before retrying.
Snapshot validation alone cannot prevent concurrent writers or duplicate alerts.

### Validation and consumer adoption

The journal validator checks structure, identities, references and supersession.
Supply referenced documents using repeatable `--document` arguments. Unloaded
references warn; `--strict` makes them errors. Missing records in loaded documents
are always errors.

The project validator accepts the same option and checks decisions, assignment,
policies and receipts. `--preflight` requires resolved references and checks
accepted proposals against current data, methodology element/state references
and existing project instance/action integrity on an in-memory candidate. No
validator fetches sources, interprets instructions or writes project data.

Project validation checks journal-wide structural integrity but resolves external
contexts only for that project's referenced recommendations. Other projects'
contexts in a shared journal need not be loaded to apply a local card.

The integration mapping validator also accepts `--document` for signal-rule
dependencies, in addition to its existing optional practice/method positional
argument. This lets signal targets resolve against loaded baselines and practice
dependencies without changing existing command invocations.

Supply composed methodology for aliases or other merge transformations.
Validators follow loaded dependencies but do not duplicate the merge engine.
Runtimes must resolve and validate that scope through existing composition tools.

The annual-report fixtures are executable examples:

```bash
python3 validate/validate-signal-journal.py \
  validate/fixtures/fixture-signal-journal.json language.schema.json \
  --document validate/fixtures/fixture-signal-project.json \
  --document validate/fixtures/fixture-signal-mapping.json \
  --document validate/fixtures/fixture-signal-practice.json \
  --document validate/fixtures/fixture-baseline.json --strict

python3 validate/validate-project.py \
  validate/fixtures/fixture-signal-project.json language.schema.json \
  --document validate/fixtures/fixture-signal-journal.json \
  --document validate/fixtures/fixture-signal-mapping.json \
  --document validate/fixtures/fixture-signal-practice.json \
  --document validate/fixtures/fixture-baseline.json --preflight
```

Existing documents need no migration. Consumers must adopt schema 3.3.0 before
loading journals or the new project properties. Package journals separately and
load referenced journal and mapping versions before enabling application.
Journals, policies and cards do not participate in methodology composition.

The design borrows identities from
[CloudEvents](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md),
passage references from [W3C Web Annotation](https://www.w3.org/TR/annotation-model/)
and advice/suggestion feedback distinctions from [CDS Hooks](https://cds-hooks.hl7.org/2.0/).
These formats are not required.

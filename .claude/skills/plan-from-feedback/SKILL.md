---
name: plan-from-feedback
description: Triage and resolve keleo-language issues from its GitHub tracker — the Practice Language schema, its semantics, and the validators that enforce them
triggerPatterns:
  - "plan.*feedback"
  - "triage.*issues"
  - "work.*backlog"
  - "process.*issues"
---

# Plan from Feedback — keleo-language

Read `.claude/skills/feedback-foundation/FEEDBACK-FOUNDATION.md` for the workflow,
routing, sanitisation, commit linking and closing rules. This file declares only what
is specific to keleo-language.

**Routing:** `keleo-labs/keleo-language` — **public**, so anything filed from here to
another project is sanitised.

This project does **not** read the feedback register. Its queue is its own tracker.
Issues reach it either because keleo-pgen-llm routed a register row here, or because
someone filed directly.

---

## Change levels

| Level | Scope | When |
|---|---|---|
| **L1** | `language.schema.json` | The constraint is structural — a missing property, a wrong cardinality, a type that cannot express what the domain needs |
| **L2** | `validate/*.py`, `validate/validate-schema.js` | The schema is right but nothing enforces it, or a validator reports something that is not actually wrong |
| **L3** | `references/semantics/` | The rule cannot be expressed in JSON Schema and has to be stated as semantics, with a validator check behind it |

Most issues touch two of these. A new constraint that is only in the schema is
undocumented; one that is only in the semantics is unenforced. **Three-layer coverage
applies**: schema, semantics, validation. A change touching one layer is incomplete.

---

## This project sits upstream

Every other keleo project depends on this schema, so a change here propagates outward
rather than escalating up. There is no L4 to escalate to — this is where it stops.

That inverts the closing obligation. **Before closing an issue that changed the schema
or a validator, re-validate the downstream corpus**, because a change that is correct in
isolation can invalidate documents that were valid yesterday:

```bash
cd ../keleo-pgen-llm
python3 utils/scan-corpus.py --severity error --schema deps/language.schema.json
```

`deps/language.schema.json` there is a symlink to this repository, so the corpus is
already validating against the working copy. A new error in a document nobody touched
is caused by the schema change, not by the document.

Where the change is deliberately breaking, say so on the issue, bump the schema version
accordingly, and file an issue on each affected consumer rather than leaving them to
discover it.

---

## Locating the change

| Issue is about | Look in |
|---|---|
| A type, property or constraint | `language.schema.json`, by `$defs` name |
| What a construct means, or how to use it | `references/semantics/` — the hub `references/semantics.md` maps sections to files |
| A check that fires wrongly or not at all | `validate/validate-<kind>.py` |
| Schema conformance only | `validate/validate-schema.js` |

The schema declares its own version in the root `$comment` as `schemaVersion:X.Y.Z`.

---

## Validating the change

```bash
node validate/validate-schema.js <file.json>
python3 validate/validate-practice.py <practice.json> <baseline.json> language.schema.json
python3 validate/validate-baseline.py <baseline.json> language.schema.json
```

The Python validators bootstrap their own virtualenv on first run; no install step is
needed and `pip install jsonschema` fails under PEP 668 on most machines.

A schema change is validated by the downstream corpus run above, not by the validators
alone — they check conformance to the schema, so they cannot tell you the schema is
wrong.

---

## Versioning

Schema changes follow semver, and the version is part of the fix rather than an
afterthought:

| Change | Bump |
|---|---|
| New optional property, new enum value, new `$defs` type | MINOR |
| New required property, removed or renamed property, changed meaning | MAJOR |
| Description, example or comment only | PATCH |

A MAJOR bump is published to a public repository and consumed by tooling that validates
against it, so state the migration path on the issue before closing.

## Project notes

- `references/` and `validate/` are symlinked into keleo-pgen-llm. A change here is live
  there immediately, before anything is committed — useful for the corpus run above, and
  a reason to be careful about leaving the working tree half-changed.
- The repository had no secret scanning until recently; `guardrails.py --check` must be
  clean before pushing.

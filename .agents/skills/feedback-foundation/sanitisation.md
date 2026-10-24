# Sanitisation

Read this before drafting anything for a **public** tracker. Check the destination's
visibility and access before including private detail in any tracker.

## Why the bar is this high

The register is internal. The `keleo-labs` repositories are public. A published issue is
indexed within minutes and stays reachable by SHA after deletion, so there is no
retraction — only an admission. That asymmetry is why the posture is deny-by-default and
why a human approves the first run.

## What must never appear

| Class | Examples |
|---|---|
| People | Reporter emails, named individuals, team names, Slack channels |
| Customers and partners | Named accounts, "a French client", "preparing material for …" |
| Internal locations | Private document URLs, internal hostnames, spreadsheet and document ids |
| Vendor products | Hardware and software product names, model numbers, part numbers |
| Methodology names | Practice, method, baseline, alpha, work product and outcome names from the library |

The last two are easy to miss. A private practice name can reveal a vendor
relationship, a product line and the shape of a methodology catalogue.

## What survives

More than you would expect. The defect itself is usually generic:

> **Blocked**: A report names a private practice and the specific hardware models
> whose power figures are missing.

> **Publishable**: "A hardware configuration practice requires the power and cooling
> budget to be closed before a configuration is accepted, but publishes no per-device
> power figures, so the check cannot be performed from the practice alone."

The private register row retains the practice and device details. The public
issue describes the defect that needs fixing.

## Drafting

Write the issue; do not transform the row. The register description is written for an
internal reader who already knows the context, and redacting it word by word produces
something full of `[…]` that reads as though it is hiding something. Start from the
defect and state it plainly in general terms.

Keep: the defect, why it matters, what is expected, how to reproduce where that is
generic. Drop: where you were when you found it, who asked, which engagement, which
document.

## The gate

```bash
python3 utils/issue-sanitiser.py --check draft.md
```

Exit 1 means blocking findings. Exit 0 means nothing *enumerable* was found — which is
not the same as safe.

Build denylists from private source material where available, and keep those
denylists private. **A row describing something absent can name a term the gate
cannot know.** Review the draft as well as the scan results.

Single ordinary English words are dropped from the harvest — the corpus names elements
`Architecture`, `Backlog` and `Benefits`, and blocking those would flag every second
sentence until the gate was ignored. That is a deliberate narrow false negative bought
to keep the gate credible.

Refresh the denylist when practices have been added:

```bash
python3 utils/issue-sanitiser.py --build-denylist
```

## Rules

- **Never weaken the denylist to make one issue pass.** Rewrite the issue.
- **Never bypass the gate.** `forge-issues.py --create` enforces it for public targets
  precisely so it cannot be skipped.
- **Engagement language is advisory, not blocking.** `client`, `customer`,
  `on behalf of` are flagged for a human to confirm no real engagement is identifiable.
- **When no useful statement survives**, do not publish a vague one. Set Issue State
  `Not Published` with a reason. A row that cannot be published safely stays internal,
  and that is a legitimate outcome.

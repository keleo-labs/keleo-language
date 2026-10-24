# AGENTS.md - Keleo Language

## Codex support

Codex reads this file for project instructions and discovers shared skills in
`.agents/skills/`. The feedback workflow starts at
`.agents/skills/plan-from-feedback/SKILL.md`.

Keep shared instructions generic. Credentials, personal paths, company details and
private feedback belong outside the repository. Local agent state and private
working directories are ignored by Git; review staged content before publishing
because ignore rules cannot detect sensitive text inside a shared file.

## Project Overview

**keleo-language** is the canonical source of truth for the Practice Language JSON Schema and its semantic guidance. The Practice Language is a meta-model for describing practices, methods, baselines, and projects derived from SEMAT Essence.

This project is consumed by other keleo projects via symlinks:
- **keleo-studio** — uses the schema for validation and rendering
- **keleo-pgen-llm** — uses the schema and semantics for LLM-driven practice generation

## Project Structure

```
keleo-language/
├── language.schema.json          # The JSON Schema (Draft 2020-12)
├── references/
│   ├── semantics.md              # Semantic guidance hub (summaries + links to sub-documents)
│   ├── semantics/                # Detailed semantic guidance sub-documents
│   │   ├── composition.md        # §4: Adapting and composing practices
│   │   ├── practice-elements.md  # §5: PracticeElement foundations
│   │   ├── alphas.md             # §6: Alpha-state trajectory and dynamics
│   │   ├── work-products.md      # §7: Work product elements
│   │   ├── execution-and-patterns.md  # §8-9: Activities, roles, patterns, outcomes
│   │   ├── narrative-and-assets.md    # §10-11: Narratives, citations, visual assets
│   │   ├── project-tracking.md   # §12: Project execution tracking
│   │   ├── change-requests.md    # §13: Change request lifecycle
│   │   └── acyclicity.md         # §14: Acyclicity constraints
│   ├── design-principles.md      # Design principles for schema evolution and project changes
│   ├── merge.md                  # Merge algorithm specification
│   └── domain-framework.md       # Enterprise analysis framework (referenced by semantics.md)
├── specifications/
│   ├── shared-diagram-primitives.md  # Shared constants and patterns for diagram specs
│   └── projects.md               # Project type specification
├── validate/
│   ├── validate-schema.js        # Node.js AJV schema validator
│   ├── validate-practice.py      # Practice/Method validator (schema + baseline + integrity)
│   ├── validate-baseline.py      # Baseline validator (schema + structure + integrity)
│   └── validate-project.py       # Project validator (schema + internal integrity)
├── package.json                  # Node.js dependencies (ajv, ajv-formats)
└── .gitignore
```

## Key Files

| File | Purpose |
|------|---------|
| `language.schema.json` | JSON Schema (Draft 2020-12) defining Practice, PracticeBaseline, Method, and Project structures |
| `references/semantics.md` | Semantic guidance hub — summaries and links to detailed sub-documents in `references/semantics/` |
| `references/semantics/` | Detailed semantic guidance, split by topic (composition, alphas, work products, patterns, etc.) |
| `references/design-principles.md` | Project-specific design principles for schema evolution (supplements global coding standards) |
| `references/merge.md` | Merge algorithm specification for practice and method composition |
| `references/domain-framework.md` | Four-perspective enterprise analysis framework used during practice authoring |
| `specifications/projects.md` | Design specification for the Project type |
| `specifications/shared-diagram-primitives.md` | Shared layout constants and rendering patterns for diagram specifications |

## Validation

### Schema-only validation (Node.js)

```bash
npm install
node validate/validate-schema.js <file.json>
```

### Practice validation (Python)

Validates against schema, baseline references, and internal cross-reference integrity:

```bash
python3 validate/validate-practice.py <practice.json> <baseline.json> language.schema.json
```

Python validators bootstrap their own virtual environment; no system-wide install
is required.

### Project validation (Python)

Validates project-specific structure (practice/method reference, cycle integrity, pattern view references):

```bash
python3 validate/validate-project.py <project.json> language.schema.json
```

### Baseline validation (Python)

Validates baseline-specific structure (no floating alphas check, relatesTo completeness):

```bash
python3 validate/validate-baseline.py <baseline.json> language.schema.json
# With parent baseline:
python3 validate/validate-baseline.py <baseline.json> <parent-baseline.json> language.schema.json
```

## Design Principles

See [`references/design-principles.md`](references/design-principles.md) — read before proposing schema changes, adding types, or writing specifications.

## Schema Evolution

When modifying `language.schema.json`:

1. Update the schema
2. Update the relevant sub-document in `references/semantics/` if the change affects operational semantics (and update the summary in `references/semantics.md` if a new section is added)
3. Run validators against existing practices to check for regressions
4. Consuming projects pick up changes automatically via symlinks

## Consuming Projects

Projects reference keleo-language files via symlinks:

- `keleo-studio/web/public/language.schema.json` → `../../../keleo-language/language.schema.json`
- `keleo-pgen-llm/deps/language.schema.json` → `../../keleo-language/language.schema.json`
- `keleo-pgen-llm/references/semantics.md` → `../../keleo-language/references/semantics.md`
- `keleo-pgen-llm/references/semantics/` → `../../keleo-language/references/semantics/`
- `keleo-pgen-llm/references/domain-framework.md` → `../../keleo-language/references/domain-framework.md`

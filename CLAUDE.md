# CLAUDE.md - Keleo Language

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
│   ├── semantics.md              # Semantic guidance for the schema
│   ├── design-principles.md      # Design principles for schema evolution and project changes
│   ├── merge.md                  # Merge algorithm specification
│   └── domain-framework.md       # Enterprise analysis framework (referenced by semantics.md)
├── specifications/
│   ├── shared-diagram-primitives.md  # Shared constants and patterns for diagram specs
│   └── projects.md               # Project type specification
├── validate/
│   ├── validate-schema.js        # Node.js AJV schema validator
│   ├── validate-practice.py      # Practice/Method validator (schema + baseline + integrity)
│   └── validate-baseline.py      # Baseline validator (schema + structure + integrity)
├── package.json                  # Node.js dependencies (ajv, ajv-formats)
└── .gitignore
```

## Key Files

| File | Purpose |
|------|---------|
| `language.schema.json` | JSON Schema (Draft 2020-12) defining Practice, PracticeBaseline, Method, and Project structures |
| `references/semantics.md` | Operational architecture and semantic guidance — the "why" behind schema structures |
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
pip install jsonschema
python3 validate/validate-practice.py <practice.json> <baseline.json> language.schema.json
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
2. Update `references/semantics.md` if the change affects operational semantics
3. Run validators against existing practices to check for regressions
4. Consuming projects pick up changes automatically via symlinks

## Consuming Projects

Projects reference keleo-language files via symlinks:

- `keleo-studio/web/public/language.schema.json` → `../../../keleo-language/language.schema.json`
- `keleo-pgen-llm/deps/language.schema.json` → `../../keleo-language/language.schema.json`
- `keleo-pgen-llm/references/semantics.md` → `../../keleo-language/references/semantics.md`
- `keleo-pgen-llm/references/domain-framework.md` → `../../keleo-language/references/domain-framework.md`

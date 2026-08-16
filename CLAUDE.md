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
│   └── domain-framework.md       # Enterprise analysis framework (referenced by semantics.md)
├── specifications/
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
| `references/domain-framework.md` | Four-perspective enterprise analysis framework used during practice authoring |
| `specifications/projects.md` | Design specification for the Project type |

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

### Specifications and Documentation

- **Gherkin-based specifications.** Specifications and design documents should express requirements using Given/When/Then structure where applicable. This mirrors the Practice Language's own Test model and produces unambiguous, verifiable requirements rather than prose descriptions.
- **Three-layer coverage.** Every language concept requires coverage in three layers: schema definition (`language.schema.json`), semantic guidance (`references/semantics.md`), and validator support (`validate/`). A change that touches only one layer is incomplete.
- **Semantics document the why, schema encodes the what.** The schema defines structural constraints; `semantics.md` explains operational meaning, authoring guidance, and decision frameworks. Neither is sufficient alone.
- **Merge spec tracks composition behaviour.** Any schema change that affects how elements compose across practices or baselines must be reflected in `references/merge.md`. The merge algorithm is the consumer of the schema — if the merge spec doesn't know about a new type or relationship, it won't be processed during composition.

### Schema Design

- **Within-baseline uses direct properties; cross-baseline uses bindings.** Relationships that exist within a single baseline or practice (e.g., `contributesTo`, `partOf`, `mapsTo`) are declared as properties on the element. Relationships that emerge from composing practices from different baseline families are declared in the Method's `bindings` object — these cannot exist within either family independently.
- **Prefer explicit relationship enums over structural discrimination.** When a type supports multiple relationship semantics (e.g., contribution vs variant), use a `relationship` enum rather than separate types or structural differences. This keeps the schema surface small and makes the semantic intent readable without inspecting structure.
- **Mutually exclusive relationships are explicitly declared.** When two properties are mutually exclusive (e.g., `contributesTo`/`mapsTo`, `partOf`/`mapsTo`), the schema documents this constraint and validators enforce it. Don't rely on consumers inferring exclusivity from semantics.
- **State/LOD mappings support terminology and granularity differences.** Cross-baseline mappings should never assume exact name matching. Baselines are authored independently — they use different terms and different granularity. Mappings must support many-to-one, one-to-many, and gaps with defined semantics for unmapped entries.
- **No floating elements.** Every alpha must declare `contributesTo` or `mapsTo` unless it is a baseline alpha or a redeclaration. Every work product LOD must declare `contributesTo`. Elements without structural connections to the baseline hierarchy are validation errors.
- **Symbolic links, not embedded objects.** Cross-references between elements use string names (symbolic links), not embedded copies. This keeps the document graph navigable, prevents duplication, and allows validation by name resolution.

### Versioning and Breaking Changes

- **Semver governs schema evolution.** Major version bumps for breaking changes (removed/renamed fields, changed discrimination logic). Minor version bumps for additive changes (new optional fields, new `$defs` types). Patch version bumps for documentation-only changes.
- **Breaking changes rename, don't deprecate.** When a breaking change is warranted, rename cleanly rather than maintaining backwards compatibility shims. The major version bump signals consumers to migrate.
- **The `$comment` schemaVersion is the source of truth.** The version in the schema's `$comment` field is authoritative. Document-level `schemaVersion` fields reference it for compatibility checking.

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

# Design Principles

Guiding principles specific to the Practice Language schema and its evolution. These principles supplement the global coding standards (defined in `~/.claude/CLAUDE.md`) with project-specific rules — read both before proposing schema modifications, adding new types, or writing specifications.

## Specifications and Documentation

- **Three-layer coverage.** Every language concept requires coverage in three layers: schema definition (`language.schema.json`), semantic guidance (`references/semantics.md`), and validator support (`validate/`). A change that touches only one layer is incomplete.
- **Semantics document the why, schema encodes the what.** The schema defines structural constraints; `semantics.md` explains operational meaning, authoring guidance, and decision frameworks. Neither is sufficient alone.
- **Merge spec tracks composition behaviour.** Any schema change that affects how elements compose across practices or baselines must be reflected in `references/merge.md`. The merge algorithm is the consumer of the schema — if the merge spec doesn't know about a new type or relationship, it won't be processed during composition.

## Schema Design

- **Within-baseline uses direct properties; cross-baseline uses bindings.** Relationships that exist within a single baseline or practice (e.g., `contributesTo`, `partOf`, `mapsTo`) are declared as properties on the element. Relationships that emerge from composing practices from different baseline families are declared in the Method's `bindings` object — these cannot exist within either family independently.
- **Prefer explicit relationship enums over structural discrimination.** When a type supports multiple relationship semantics (e.g., contribution vs variant), use a `relationship` enum rather than separate types or structural differences. This keeps the schema surface small and makes the semantic intent readable without inspecting structure.
- **Mutually exclusive relationships are explicitly declared.** When two properties are mutually exclusive (e.g., `contributesTo`/`mapsTo`, `partOf`/`mapsTo`), the schema documents this constraint and validators enforce it. Don't rely on consumers inferring exclusivity from semantics.
- **State/LOD mappings support terminology and granularity differences.** Cross-baseline mappings should never assume exact name matching. Baselines are authored independently — they use different terms and different granularity. Mappings must support many-to-one, one-to-many, and gaps with defined semantics for unmapped entries.
- **No floating elements.** Every alpha must declare `contributesTo` or `mapsTo` unless it is a baseline alpha or a redeclaration. Every work product LOD must declare `contributesTo`. Elements without structural connections to the baseline hierarchy are validation errors.
- **Symbolic links, not embedded objects.** Cross-references between elements use string names (symbolic links), not embedded copies. This keeps the document graph navigable, prevents duplication, and allows validation by name resolution.

## Versioning

The `$comment` field in `language.schema.json` contains the authoritative version string in the format `schemaVersion:X.Y.Z`. Document-level `schemaVersion` fields in practices, baselines, methods, and projects reference this version for compatibility checking.

Version component examples specific to this schema:
- **MAJOR** — removing or renaming a field, changing a required/optional boundary, altering enum values, restructuring type hierarchies.
- **MINOR** — adding a new optional field, introducing a new `$defs` type, adding a new enum value to a non-exclusive set.
- **PATCH** — correcting a description, fixing a typo in a `$comment`, updating documentation-only files (`semantics.md`, `merge.md`, this document).

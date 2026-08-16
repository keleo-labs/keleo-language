# Design Principles

Guiding principles for evolving the Practice Language schema, specifications, and project structure. These principles inform every change to this project — read them before proposing schema modifications, adding new types, or writing specifications.

## Specifications and Documentation

- **Gherkin-based specifications.** Specifications and design documents should express requirements using Given/When/Then structure where applicable. This mirrors the Practice Language's own Test model and produces unambiguous, verifiable requirements rather than prose descriptions.
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

## Versioning and Breaking Changes

- **Semver governs schema evolution.** Major version bumps for breaking changes (removed/renamed fields, changed discrimination logic). Minor version bumps for additive changes (new optional fields, new `$defs` types). Patch version bumps for documentation-only changes.
- **Breaking changes rename, don't deprecate.** When a breaking change is warranted, rename cleanly rather than maintaining backwards compatibility shims. The major version bump signals consumers to migrate.
- **The `$comment` schemaVersion is the source of truth.** The version in the schema's `$comment` field is authoritative. Document-level `schemaVersion` fields reference it for compatibility checking.

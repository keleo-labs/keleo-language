# The Package Format

## Objective

The `.keleo` package format provides a mechanism for distributing Practice Language documents and their associated visual assets as a single, self-contained archive. It formalises the bundle concept described in the semantic guidance into a concrete file format with a defined internal structure, a machine-readable manifest, and validation rules.

A package can contain any combination of Practice Language root types — practices, baselines, methods, and projects — enabling both method distribution (a method with its externalised practices and baseline) and library distribution (standalone practices or baselines for independent consumption and reuse).

## Relationship to Existing Schema

The package format builds on two existing schema mechanisms:

1. **Externalised references** — Methods support string-based symbolic references (`baselinePracticeName`, `practiceNames`) instead of embedded objects. Practices reference their baseline via `baselinePracticeName` and declare dependencies via `practiceDependencyNames`. These symbolic links require a resolution mechanism; the package provides one.

2. **Asset paths** — The Asset type's `path` field uses relative paths (e.g., `assets/diagrams/platform-states.svg`). Within a package, these paths resolve relative to the package root, requiring zero transformation between authored and packaged forms.

The manifest schema is defined as four new `$defs` in `language.schema.json`: `PackageManifest`, `PackageIdentity`, `PackageDocument`, and `PackageDependency`. The manifest is not a Practice Language document — it is metadata *about* Practice Language documents and is not subject to root-level type discrimination. Consumers validate it via `language.schema.json#/$defs/PackageManifest`.

## File Format

A `.keleo` file is a ZIP archive with the following characteristics:

- **Extension**: `.keleo`
- **MIME type**: `application/vnd.keleo.package+zip`
- **Compression**: DEFLATE (recommended) or STORE
- **Character encoding**: UTF-8 for all JSON and text files
- **No encryption**: Use transport-layer security for confidentiality; the archive itself is not encrypted

The MIME type follows the `application/vnd.*+zip` structured syntax suffix convention (RFC 6839), signalling to tooling that the content is a ZIP archive with domain-specific structure.

## Internal Structure

Every package has the same top-level layout:

```text
example.keleo (ZIP archive)
├── manifest.json
├── documents/
│   ├── baseline.json
│   ├── practice-a.json
│   ├── practice-b.json
│   └── method.json
└── assets/
    ├── diagrams/
    │   ├── platform-states.svg
    │   └── value-stream-map.png
    ├── templates/
    │   └── architecture-doc-template.pdf
    └── icons/
        └── practice-icon.svg
```

### manifest.json

The manifest is always at the ZIP root. It is the entry point: a consumer opens the archive, reads `manifest.json`, and discovers everything else from its declarations.

### documents/

All Practice Language JSON documents live in a flat `documents/` directory. Documents are not organised into subdirectories by type because their type is self-describing via the schema's root discrimination rules and is explicitly declared in the manifest's document inventory.

### assets/

All file-based visual assets live under `assets/`, organised by type subdirectory (`diagrams/`, `templates/`, `icons/`). This matches the existing Asset `path` convention — an Asset declaring `"path": "assets/diagrams/platform-states.svg"` resolves to the ZIP entry at that exact path.

Packages where all assets use data URIs, external URLs, or font characters may omit the `assets/` directory entirely.

### Path Constraints

- All paths use forward slashes (POSIX convention), regardless of the host operating system
- No absolute paths — all paths are relative to the package root
- No `.` or `..` path components
- Maximum path length: 255 characters
- No nested `.keleo` packages within a package

## Manifest

The `manifest.json` file is the machine-readable declaration of a package's contents. Its schema is `$defs/PackageManifest` in `language.schema.json`.

### Schema Version

The `schemaVersion` field (required, semver string) declares which version of the Practice Language schema this package's documents target. Consumers use this for compatibility checking before attempting to parse documents — a consumer supporting schema `1.x` can reject a package targeting `2.0.0` without loading any documents.

### Package Identity

The `package` field (required, `PackageIdentity` object) provides:

- `name` — unique package name in kebab-case (e.g., `platform-engineering-method`)
- `version` — semantic version (e.g., `1.0.0`)
- `description` — human-readable summary of purpose and contents
- `authors` — optional array of package author names
- `license` — optional SPDX license identifier (e.g., `Apache-2.0`, `CC-BY-4.0`)
- `url` — optional URI for the package homepage, repository, or registry listing

### Document Inventory

The `documents` array (required, at least one entry) provides an ordered inventory of all Practice Language JSON documents in the package. Each `PackageDocument` entry declares:

- `path` — relative path to the JSON file within the ZIP (must begin with `documents/` and end with `.json`)
- `documentType` — the root type: `practiceBaseline`, `practice`, `method`, or `project`
- `documentName` — the `name` property of the root document, which is the identity key used for symbolic resolution
- `entryPoint` — boolean flag (default `false`) indicating whether this document is a primary entry point

Entry points are the documents a consumer should resolve first. A method package marks the method as the entry point; a library package might mark all practices as entry points for independent consumption. At least one document SHOULD be marked as an entry point.

### Dependencies

The `dependencies` array (optional) declares external package dependencies. A dependency is required when documents in this package use symbolic name references (`baselinePracticeName`, `practiceNames`, `practiceDependencyNames`, `practiceName`, `methodName`) that resolve to documents in other packages.

Each `PackageDependency` entry declares:

- `packageName` — name of the required package (must match the dependency's `PackageIdentity.name`)
- `versionRange` — semantic version range constraint (e.g., `>=1.0.0 <2.0.0`, `^1.2.0`). Consumers use this to select a compatible version
- `documentNames` — optional array of specific document names required from the dependency. When omitted, all documents from the dependency are available for resolution

Dependencies are package-level, not document-level. A practice's `baselinePracticeName` declares *what* it needs by name; the package's `dependencies` array declares *where* to find it by package. This keeps Practice Language JSON documents package-unaware — the same practice JSON works both inside and outside a package.

## Validation Rules

### Feature: Structural validation

```gherkin
Scenario: Manifest exists at ZIP root (1)
  Given a .keleo ZIP archive
  When the package is opened
  Then a "manifest.json" entry MUST exist at the ZIP root

Scenario: Missing manifest (1)
  Given a .keleo ZIP archive with no "manifest.json" at the root
  When the package is validated
  Then a validation error is reported: "manifest.json not found at package root"

Scenario: Manifest validates against schema (2)
  Given a package with a "manifest.json" file
  When the manifest is validated against language.schema.json#/$defs/PackageManifest
  Then validation succeeds with no schema errors

Scenario: Invalid manifest schema (2)
  Given a package with a "manifest.json" missing the required "package" field
  When the manifest is validated against language.schema.json#/$defs/PackageManifest
  Then a validation error is reported identifying the missing required field

Scenario: Document paths resolve to ZIP entries (3)
  Given a manifest declaring document path "documents/practice-a.json"
  And the ZIP archive contains an entry at "documents/practice-a.json"
  When the package is validated
  Then structural validation succeeds for that document entry

Scenario: Missing document path (3)
  Given a manifest declaring document path "documents/missing.json"
  And no ZIP entry exists at "documents/missing.json"
  When the package is validated
  Then a validation error is reported: unresolvable document path "documents/missing.json"

Scenario: At least one entry point declared (4)
  Given a manifest with three document entries
  And none have entryPoint set to true
  When the package is validated
  Then a validation warning is reported: "no document marked as entryPoint"

Scenario: Unique document names within type (5)
  Given a manifest with two entries both declaring documentType "practice" and documentName "Platform Engineering"
  When the package is validated
  Then a validation error is reported: duplicate documentName "Platform Engineering" within documentType "practice"
```

### Feature: Document validation

```gherkin
Scenario: Documents validate against Practice Language schema (6)
  Given a package with document "documents/practice-a.json"
  When the document is validated against language.schema.json
  Then schema validation succeeds

Scenario: Invalid document content (6)
  Given a package with document "documents/practice-a.json" containing invalid JSON structure
  When the document is validated against language.schema.json
  Then a validation error is reported identifying the schema violation

Scenario: Document type matches manifest declaration (7)
  Given a manifest entry declaring documentType "practice" for "documents/practice-a.json"
  And the document's root discrimination resolves to "practice"
  When the package is validated
  Then document type validation succeeds

Scenario: Document type mismatch (7)
  Given a manifest entry declaring documentType "practice" for "documents/baseline.json"
  And the document's root discrimination resolves to "practiceBaseline"
  When the package is validated
  Then a validation error is reported: document type "practiceBaseline" does not match declared "practice"

Scenario: Document name matches manifest declaration (8)
  Given a manifest entry declaring documentName "Platform Engineering" for "documents/practice-a.json"
  And the document's root name property is "Platform Engineering"
  When the package is validated
  Then document name validation succeeds

Scenario: Document name mismatch (8)
  Given a manifest entry declaring documentName "Platform Engineering" for "documents/practice-a.json"
  And the document's root name property is "Cloud Platform Engineering"
  When the package is validated
  Then a validation error is reported: document name "Cloud Platform Engineering" does not match declared "Platform Engineering"
```

### Feature: Asset validation

```gherkin
Scenario: Asset paths resolve to ZIP entries (9)
  Given a document declaring an Asset with path "assets/diagrams/platform-states.svg"
  And the ZIP archive contains an entry at "assets/diagrams/platform-states.svg"
  When the package is validated
  Then asset path validation succeeds

Scenario: Missing asset path (9)
  Given a document declaring an Asset with path "assets/diagrams/missing.svg"
  And no ZIP entry exists at "assets/diagrams/missing.svg"
  When the package is validated
  Then a validation error is reported: unresolvable asset path "assets/diagrams/missing.svg"

Scenario: Asset checksum matches (10)
  Given a document declaring an Asset with path "assets/diagrams/states.svg" and a checksum value
  And the SHA-256 hash of the ZIP entry content matches the declared checksum
  When the package is validated
  Then asset checksum validation succeeds

Scenario: Asset checksum mismatch (10)
  Given a document declaring an Asset with path "assets/diagrams/states.svg" and a checksum value
  And the SHA-256 hash of the ZIP entry content does not match the declared checksum
  When the package is validated
  Then a validation error is reported: checksum mismatch for "assets/diagrams/states.svg"

Scenario: Orphan asset detection (11)
  Given a ZIP archive containing "assets/icons/unused-icon.svg"
  And no document in the package references "assets/icons/unused-icon.svg" in its assets array
  When the package is validated
  Then a validation warning is reported: orphan asset "assets/icons/unused-icon.svg"
```

### Feature: Dependency validation

```gherkin
Scenario: Symbolic name references resolve (12)
  Given a practice document with baselinePracticeName "Platform Adoption Kernel"
  And the package contains a document with documentName "Platform Adoption Kernel" and documentType "practiceBaseline"
  When the package is validated
  Then symbolic name resolution succeeds

Scenario: Symbolic name resolves via declared dependency (12)
  Given a practice document with baselinePracticeName "Platform Adoption Kernel"
  And the package does not contain that document
  But a declared dependency provides documentName "Platform Adoption Kernel"
  When the package is validated
  Then symbolic name resolution succeeds

Scenario: Unresolvable symbolic name (12)
  Given a practice document with baselinePracticeName "Unknown Baseline"
  And no document in the package or declared dependencies provides that name
  When the package is validated
  Then a validation error is reported: unresolvable reference "Unknown Baseline"

Scenario: No circular package dependencies (13)
  Given package "A" declares a dependency on package "B"
  And package "B" declares a dependency on package "A"
  When the dependency graph is validated
  Then a validation error is reported: circular dependency between "A" and "B"
```

## Package as Library

### Name Resolution Index

The merge algorithm (described in `references/merge.md`, Section 2.3) requires a library lookup index that maps practice and baseline names to their full document bodies. A `.keleo` package serves as such a library: its manifest's `documents` array maps `(documentType, documentName)` pairs to file paths, enabling the merge algorithm to resolve symbolic name references to document bodies without external configuration.

When a Method uses `practiceNames` or `baselinePracticeName` string references, the consumer builds a resolution index from the package's document inventory. The merge algorithm then resolves names against this index during composition.

### Multi-Package Resolution

When multiple packages are loaded, name collisions across packages are resolved by precedence:

1. Documents in the consuming document's own package take precedence
2. Explicit dependency declarations take precedence over ambient (non-declared) packages
3. If a name is still ambiguous, the consumer MUST report an error — implicit resolution order across packages is not defined

### Externalised Practice Distribution

The primary use case for packaging is externalised method distribution. A Method JSON uses `practiceNames` and `baselinePracticeName` string references, and all referenced documents are included in the same package. The method document itself is lean — it declares composition intent, while the baseline and practices are full standalone documents that can also be consumed independently.

This enables reuse: the same practice can appear in multiple method packages without duplication of its definition. When a practice is shared, it can be distributed as its own package and declared as a dependency by method packages that use it.

## Common Package Patterns

### Method Distribution

A complete method with its externalised baseline and practices:

```text
platform-engineering.keleo
├── manifest.json
├── documents/
│   ├── platform-kernel.json          (PracticeBaseline)
│   ├── platform-practice.json        (Practice)
│   ├── devsecops-practice.json       (Practice)
│   └── platform-engineering.json     (Method, entryPoint)
└── assets/
    ├── diagrams/
    │   └── platform-states.svg
    └── icons/
        └── practice-icon.svg
```

```json
{
  "schemaVersion": "1.0.0",
  "package": {
    "name": "platform-engineering",
    "version": "2.1.0",
    "description": "Platform Engineering method with DevSecOps extension practice.",
    "authors": ["Practice Authors"],
    "license": "CC-BY-4.0"
  },
  "documents": [
    {
      "path": "documents/platform-kernel.json",
      "documentType": "practiceBaseline",
      "documentName": "Platform Adoption Kernel"
    },
    {
      "path": "documents/platform-practice.json",
      "documentType": "practice",
      "documentName": "Platform Engineering"
    },
    {
      "path": "documents/devsecops-practice.json",
      "documentType": "practice",
      "documentName": "DevSecOps"
    },
    {
      "path": "documents/platform-engineering.json",
      "documentType": "method",
      "documentName": "Platform Engineering Method",
      "entryPoint": true
    }
  ]
}
```

The method JSON uses externalised references:

```json
{
  "kind": "method",
  "name": "Platform Engineering Method",
  "description": "...",
  "baselinePracticeName": "Platform Adoption Kernel",
  "practiceNames": ["Platform Engineering", "DevSecOps"]
}
```

### Practice Library

Multiple standalone practices sharing a baseline, each available for independent consumption:

```text
cloud-practices.keleo
├── manifest.json
├── documents/
│   ├── cloud-kernel.json             (PracticeBaseline)
│   ├── finops-practice.json          (Practice, entryPoint)
│   ├── sre-practice.json             (Practice, entryPoint)
│   └── devsecops-practice.json       (Practice, entryPoint)
└── assets/
    └── diagrams/
        └── cloud-overview.svg
```

Each practice is marked as an entry point. A consumer can resolve any individual practice (plus the shared baseline) without loading the others.

### Baseline-Only

A reusable baseline distributed for other packages to depend on:

```text
platform-kernel.keleo
├── manifest.json
└── documents/
    └── platform-adoption-kernel.json (PracticeBaseline, entryPoint)
```

```json
{
  "schemaVersion": "1.0.0",
  "package": {
    "name": "platform-kernel",
    "version": "1.0.0",
    "description": "Platform Adoption Kernel baseline practice.",
    "authors": ["Kernel Authors"],
    "license": "CC-BY-4.0"
  },
  "documents": [
    {
      "path": "documents/platform-adoption-kernel.json",
      "documentType": "practiceBaseline",
      "documentName": "Platform Adoption Kernel",
      "entryPoint": true
    }
  ]
}
```

Other packages depend on this baseline:

```json
{
  "dependencies": [
    {
      "packageName": "platform-kernel",
      "versionRange": "^1.0.0",
      "documentNames": ["Platform Adoption Kernel"]
    }
  ]
}
```

### Project Snapshot

A project with its referenced method included for portability:

```text
q3-assessment.keleo
├── manifest.json
├── documents/
│   ├── platform-kernel.json          (PracticeBaseline)
│   ├── platform-practice.json        (Practice)
│   ├── platform-method.json          (Method)
│   └── q3-assessment.json            (Project, entryPoint)
└── assets/
    └── diagrams/
        └── current-state.svg
```

The project is the entry point; the method and its constituents are included so the project is fully self-contained and portable.

## Schema Changes

The package format adds four `$defs` to `language.schema.json`:

| Definition | Required Fields | Purpose |
|---|---|---|
| `PackageManifest` | `schemaVersion`, `package`, `documents` | Root object of `manifest.json` |
| `PackageIdentity` | `name`, `version`, `description` | Package name, version, and metadata |
| `PackageDocument` | `path`, `documentType`, `documentName` | Document inventory entry |
| `PackageDependency` | `packageName`, `versionRange` | External package reference |

No changes to root-level type discrimination, the `kind` enum, or any existing definitions. The manifest schema is referenced directly as `language.schema.json#/$defs/PackageManifest` — it does not participate in the root `if/then/else` chain.

## Coverage Status

- **Schema:** Complete — `PackageManifest`, `PackageIdentity`, `PackageDocument`, `PackageDependency` defined in `language.schema.json`
- **Semantics:** Covered in `references/semantics.md` Section 11.4
- **Validation:** Not yet implemented — planned as `validate/validate-package.py`

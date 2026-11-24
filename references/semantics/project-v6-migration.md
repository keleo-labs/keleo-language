## Migrate projects to Language schema v6

Language schema 6.0.0, distributed with npm package 7.0.0, replaces the flat project and cycle `priorityThreshold` fields. At each level, move the value to `assessmentPolicy.priorityThreshold`. Keep an absent threshold absent. Projects that omit `assessmentPolicy.rigour` keep their existing assessment and attainment rules.

Run the migration against an explicit v5 Project. Write the output to a separate file and review it before replacing the original.

```sh
python3 utils/migrate-project-v6.py project.json > project.v6.json
```

The utility validates the migrated Project before writing JSON to standard output. Conflicting flat and nested values cause an error. If a v5 Project has no `schemaVersion`, confirm its source schema and add that version to the input copy first.

The Language validators' existing major-version check also applies to other Language documents that declare a v5 `schemaVersion`. Validate those documents with the v6 tools after updating their declared version. Standalone catalog formats keep their own versions.

Before adopting v6, update consumers that load or write the old paths. Keleo Project needs coordinated changes to its scaffold, policy setters, dashboard, checklist scope calculations and bundled schema. Pin a v5 schema until the consumer can read and write the nested policy. A symlink or a resolver that reads a sibling checkout can pick up the new schema as soon as that checkout changes.

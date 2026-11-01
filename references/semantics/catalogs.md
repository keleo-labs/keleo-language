## Local source and practice catalogs

Source catalogs retain a structured snapshot of material used to author practices.
Each snapshot records its source URI, a digest of extracted text, a local input
file digest where applicable and sections with
heading paths, locators and text. Its section IDs include the digest, so a later
revision cannot silently change what an existing link means. A source workspace
may hold several revisions of the same source. Its `latest.json` state records
which revision was most recently checked and whether that check succeeded.

Practice catalogs are local indexes of one practice or baseline JSON document.
Each entry points to an element by JSON Pointer and may name supporting source
sections. The catalog records the document's version and byte digest; an edit
invalidates the index until it is rebuilt. Source section links are optional
where no source was used, but a declared link must resolve to a snapshot.
For new factual claims, a linked source revision must be the current, freshly
checked snapshot. Historical snapshots remain available to explain older work.

Catalogs are authoring metadata, stored outside `.keleo` packages. A practice's
`citations` and `references` retain their existing meaning and remain in the
practice document. Catalogs neither replace them nor participate in practice
composition. The schemas are `source-catalog.schema.json` and
`practice-catalog.schema.json`, each at version `1.0.0`; use
`validate/validate-catalog.py` for schema, identity and link checks.

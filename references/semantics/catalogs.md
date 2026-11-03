## Local source, methodology and Project catalogs

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
composition. The schemas are [`source-catalog.schema.json`](../../schemas/catalogs/source-catalog.schema.json) and
[`practice-catalog.schema.json`](../../schemas/catalogs/practice-catalog.schema.json), each at version `1.0.0`; use
`validate/validate-catalog.py` for schema, identity and link checks.

Named Method and Practice catalogs serve Projects that reuse the same methodology.
Each file keeps separate variants for document versions and content hashes. A
Method and a Practice with the same name use distinct files. These indexes do not
embed Project evidence because one methodology can support several Projects.

Each Project keeps its own catalog beside versioned snapshots of its citations
and linked sources. The Project catalog records its JSON digest, element pointers,
links to shared methodology catalogs and explicit element-to-source-section
mappings. A methodology mapping includes the catalog filename, variant hash and
element pointer. Agents add these mappings only after checking the cited section.
An unavailable source retains its previous snapshot with stale status. A missing
first snapshot is reported without changing Project JSON.

The additional schemas are [`methodology-catalog.schema.json`](../../schemas/catalogs/methodology-catalog.schema.json) and
[`project-catalog.schema.json`](../../schemas/catalogs/project-catalog.schema.json), both at version `1.0.0`. The existing
`practice-catalog.schema.json` remains the single-document authoring format used
by practice generation.

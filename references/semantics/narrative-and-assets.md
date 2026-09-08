[< Back to Semantic Guidance Hub](../semantics.md)

## 10 Narrative Management

Narratives provide a way for practices to include additional information and context about any PracticeElement. When used the narrative content **MUST** be kept succinct, providing information in a minimal outlined style. It should **NOT** replicate sections of the source content, instead it should provide a summary of that content, with **Citations** being used to direct the user to further reading.

**Narrative Naming:**

The `name` property of a Narrative must summarize what the narrative tells the reader, not what structural role the narrative plays. The `narrativeTypeName` already carries the structural role (e.g., "Hero's Journey", "STAR", "Practice Intent"). The `name` must convey the specific story or message so that a reader scanning a method with multiple practices can distinguish each narrative at a glance.

**Anti-Pattern — Generic Role-Based Names (WRONG):**

- "Practice Intent" — which practice? What does it intend?
- "Overview Narrative" — overview of what?
- "Hero's Journey for Platform" — exposes template mechanics

**Correct — Content-Descriptive Names:**

- "Accelerating Platform Adoption Through Self-Service Infrastructure"
- "From Manual Provisioning to Automated Golden Paths"
- "Transforming Developer Experience with Internal Platform Capabilities"

Each name should be specific enough that reading it alone tells you the subject matter and perspective of the narrative. In a method with five practices, five narratives named "Practice Intent" are indistinguishable; five content-descriptive names create a scannable table of contents.

**Narrative Context Self-Containment:**

Users consume narratives as: **name**, **description**, and a sequence of **context** strings. The narrative element names (from the NarrativeType) are authoring scaffolding — they guide the writer but are **NOT displayed** to the reader. Each `context` value must therefore be self-contained: coherent and meaningful when read in sequence without any element headings.

**The Self-Containment Test:** Read the narrative's name, description, and contexts in order as a continuous piece of prose. If any context is a non sequitur — a list of items, warnings, or steps that only makes sense under a heading like "Common Pitfalls" or "Prerequisites" — it fails the test.

**Anti-Pattern — Heading-Dependent Context (WRONG):**

> *Name:* VM Inventory Discovery and Compatibility Classification
> *Description:* How to discover, classify, and assess source VMs for migration readiness.
> *Context 1:* Install the MTV operator, create Provider CRs for each source platform...
> *Context 2:* Create Provider CRs with platform-specific credentials...
> *Context 3:* Failing to validate VMware VDDK version compatibility. Overlooking the 47-character VM naming constraint. Attempting to assess the entire estate at once.

Context 3 is a bare list of mistakes — without the "Common Pitfalls" heading it reads as a non sequitur.

**Correct — Self-Contained Context:**

> *Context 3:* Common mistakes include failing to validate VMware VDDK version compatibility and NFC memory settings before assessment, overlooking the 47-character VM naming constraint for Kubernetes resources, and attempting to assess the entire VM estate at once rather than progressively by provider type.

A single framing clause ("Common mistakes include...") makes the context readable as prose without any external heading.

**Rules:**
1. Each context must open with a framing sentence or clause that establishes what the paragraph is about
2. Bare lists (gerund phrases, noun phrases, or sentence fragments without a lead-in) require a framing introduction
3. The sequence of contexts must read as coherent prose: name → description → context 1 → context 2 → ... → context N

### 10.1 Narrative Tooling Synchronization and Execution Guidelines

The NarrativeType class defines specific narrative approaches by acting as a container for embedded NarrativeElement objects. Crucially, each NarrativeElement contains a required howToUse string. This property provides explicit authoring instructions for practitioners, detailing exactly how the narrative spine element should be applied in practice. Operational tooling must explicitly synchronize the narrativeName with human-facing interfaces. Execution milestones are mapped to this narrative spine via NarrativeContext elements, delivering highly relevant contextual slices based on the user's progress.

### 10.2 Cognitive Storytelling Frameworks

The following are examples of NarrativeTypes that could be described in the baselinePractice for practice authors to use, **Always** check the baselinePractice for the latest frameworks. 

- **The STAR Format (Situation, Task, Action, Result)**: Enforces a strict cause-and-effect relationship between context and outcomes.  
- **The Hero's Journey / Pixar Framework**: Highly effective for macro-level lifecycle orchestrations (platform adoptions, transformations).  
- **The Three-Act Structure & StoryBrand**: Positions the consumer as the Hero and the Platform Engineering team as the Guide utilizing the defined approach.  
- **Micro-Narratives (ABT and PAS)**: Shorter frameworks (And/But/Therefore) designed for rapid, highly persuasive daily execution updates.

### 10.3 Bibliographic Citations and Reference Management

The schema provides native support for bibliographic references through the Citation type, enabling practices and methods to establish authoritative provenance and intellectual lineage. Citations are first-class objects within the Practice Language, ensuring proper attribution and enabling knowledge graph integration.

**Citation Structure**: Each Citation must define a unique name (serving as the citation identifier), a description, an authors array (minimum one author), a publication date, and a source (publisher, journal, or retrieval URL). The name property acts as the symbolic key for cross-referencing within narratives and other elements. The optional `pages` property records the page range or location within the cited work, following APA 7th edition format conventions:

- Single page: `"p. 23"`
- Page range: `"pp. 112-127"`
- Chapter: `"Chapter 3"`
- Section: `"Section 2.1"`
- Paragraph (for online works without page numbers): `"para. 4"`
- Table or figure: `"Table 2"`, `"Figure 5"`

Use `pages` when the citation refers to a specific portion of a larger work — a chapter in an edited book, an article spanning specific pages in a journal, or a section within a standard.

**Citation Scope and Aggregation**: Citations can be defined at multiple levels of the methodology hierarchy. PracticeBaseline documents may declare foundational citations for core concepts. Practice documents can add domain-specific citations relevant to the practice domain. Method documents aggregate citations from their baseline and constituent practices, providing a unified bibliography for the complete methodology composition.

**Narrative Integration**: The Narrative object supports an optional citationNames array, enabling authors to explicitly link narrative contexts to their supporting literature. Each entry in citationNames must match the name property of a Citation object within the same practice or method scope. This symbolic linking allows operational tooling to generate properly formatted reference lists, validate citation integrity, and support advanced knowledge retrieval patterns.

**Operational Guidance**: When authoring practices, citations should be declared for all external frameworks, research papers, standards documents, and authoritative sources that inform the practice definition. Citation names should use represent the title of the cited work. Tooling implementations must resolve citation references across the practice composition hierarchy, ensuring that narratives can reference citations from dependent practices or the baseline without duplication.

### 10.4 Acknowledgements and Attribution

The schema provides the Acknowledgement type to recognise individuals, groups, or institutions that have contributed to or supported the development of a practice, baseline, or method. Acknowledgements are distinct from Citations — they attribute human contributions and support rather than referencing published works.

**Acknowledgement Structure:**

Each Acknowledgement extends PracticeElement (requiring `name` and `description`) and adds an optional `url` property:

```json
{
  "name": "Jane Smith",
  "description": "Subject matter expert who contributed domain analysis and review of the platform adoption states.",
  "url": "mailto:jane.smith@example.com"
}
```

**Field Definitions:**

- **name** (required): The name of the person, group, or institution being acknowledged
- **description** (required): A brief explanation of the contribution or support provided
- **url** (optional): A contact or profile link — may be a `mailto:` URI, a personal website, or an organisational profile page

**Acknowledgement Scope and Aggregation:**

Acknowledgements can be declared at multiple levels of the methodology hierarchy:

- **PracticeBaseline**: Acknowledge contributors to the foundational baseline (e.g., original framework authors, domain experts who shaped the core ontology)
- **Practice**: Acknowledge contributors to the specific practice extension (e.g., practitioners who provided domain expertise, reviewers, or pilot teams)
- **Method**: Acknowledge contributors at the method composition level, aggregating recognition across the baseline and constituent practices

**Operational Guidance:**

- Use acknowledgements to recognise substantive intellectual contributions, domain expertise, review efforts, or institutional support
- The `name` property should identify the contributor clearly — use full names for individuals, official names for organisations
- The `description` should briefly explain the nature of the contribution (e.g., "Provided security domain expertise during state model design" rather than simply "Helped with the project")
- The `url` property supports various URI schemes: `mailto:` for email, `https://` for web profiles, or any other relevant link
- Acknowledgements are presentation metadata — they do not participate in structural validation or cross-referencing like citations do

**Example: Baseline Acknowledgements**

```json
{
  "acknowledgements": [
    {
      "name": "Platform Engineering Working Group",
      "description": "Collaborative working group that developed and validated the platform adoption state model through industry workshops."
    },
    {
      "name": "Dr. Alex Chen",
      "description": "Academic advisor who reviewed the ontological foundations and alpha-state progression semantics.",
      "url": "https://university.edu/profiles/achen"
    }
  ]
}
```

**Example: Method-Level Acknowledgements**

```json
{
  "acknowledgements": [
    {
      "name": "Acme Corp Platform Team",
      "description": "Pilot team whose real-world adoption experience validated and refined the pattern lifecycle.",
      "url": "mailto:platform-team@acme.example.com"
    }
  ]
}
```

## 11 Visual Assets and Practice Elements

Visual assets (diagrams, templates, icons) enhance practice comprehension and adoption. The Practice Language supports declarative asset references at both the practice/method level and individual element level.

### 11.1 Asset Declaration

Assets are declared in a top-level `assets` array on Practice, PracticeBaseline, or Method objects. Each asset has:

- **`name`** (required): Unique identifier for symbolic referencing
- **`type`** (required): Asset category - `image`, `diagram`, `template`, `icon`, or `font-character`
- **`description`** (optional): Human-readable explanation of what the asset depicts

**File-based assets** use:
- `path`: Relative path to the asset file within the practice bundle (e.g., `assets/diagrams/platform-states.svg`)
- `mimeType`: MIME type (e.g., `image/svg+xml`, `image/png`, `image/jpeg`, `application/pdf`)
- `checksum`: SHA-256 hash for integrity verification (format: `sha256:...`)
- `url`: External URL for remote hosting
- `dataUri`: Base64-encoded data URI for embedded small assets (<10KB)

**Font character assets** use:
- `fontFamily`: Font library name (e.g., `Font Awesome 6 Free`, `Material Icons`)
- `fontCharacter`: Character identifier (e.g., `fa-cog`, `settings`, ``)
- `fontWeight`: Font weight (e.g., `400`, `900`, `bold`)

### 11.2 Element-Level Asset References

Any practice element (Alpha, State, WorkProduct, LevelOfDetail, Activity, Pattern, etc.) can reference assets via the `assetNames` property — an array of `AssetReference` objects. Each `AssetReference` contains an `assetName` (symbolic link to an `Asset.name` in the top-level `assets` array) and a `type` that classifies how the asset is used in context:

- **`icon`**: UI markers, visual identity (alpha icons, competency badges, activity type indicators)
- **`illustrative`**: Documentation diagrams, architecture visualizations, workflow charts
- **`template`**: Reusable documents, forms, decision records
- **`diagram`**: Technical architecture, state progression, pattern orchestration

An element may reference multiple assets with different semantic types (e.g., an icon and a diagram for the same alpha).

**Example**:
```json
{
  "alphas": [
    {
      "name": "Platform",
      "description": "Platform infrastructure capability",
      "assetNames": [
        { "assetName": "platform-icon", "type": "icon" },
        { "assetName": "platform-state-diagram", "type": "diagram" }
      ],
      "states": [...]
    }
  ],
  "activities": [
    {
      "name": "Design Architecture",
      "description": "Create platform architecture",
      "assetNames": [
        { "assetName": "design-activity-icon", "type": "icon" },
        { "assetName": "architecture-template", "type": "template" }
      ]
    }
  ],
  "assets": [
    {
      "name": "platform-state-diagram",
      "description": "State progression for Platform alpha",
      "type": "diagram",
      "path": "assets/diagrams/platform-states.svg",
      "mimeType": "image/svg+xml",
      "checksum": "sha256:abc123..."
    },
    {
      "name": "architecture-template",
      "description": "Architecture decision record template",
      "type": "template",
      "url": "https://example.com/templates/adr.pdf"
    },
    {
      "name": "team-icon",
      "description": "Team collaboration icon",
      "type": "font-character",
      "fontFamily": "Font Awesome 6 Free",
      "fontCharacter": "fa-users",
      "fontWeight": "900"
    }
  ]
}
```

### 11.3 Common Asset Use Cases

1. **Pattern Diagrams**: Visual workflows showing alpha progression across PatternViews
   - Referenced by: Pattern elements
   - Format: SVG (preferred for scalability and editing)

2. **Alpha State Diagrams**: State machine diagrams showing transitions and gates
   - Referenced by: Alpha elements
   - Format: SVG or PNG

3. **Work Product Templates**: Example documents, spreadsheets, or diagrams
   - Referenced by: WorkProduct or LevelOfDetail elements
   - Format: PNG, PDF, SVG

4. **Activity Flowcharts**: Process flows for complex activities
   - Referenced by: Activity elements
   - Format: SVG (preferred for workflow diagrams)

5. **Architecture Diagrams**: Reference architectures for Solution focus elements
   - Referenced by: Alpha, WorkProduct, or Pattern elements
   - Format: SVG, PNG

6. **Value Stream Maps**: For Value focus patterns and activities
   - Referenced by: Pattern or Activity elements
   - Format: SVG, PNG

7. **Practice Icons**: Visual identity for practices in tooling
   - Referenced by: Practice metadata
   - Format: SVG (preferred for UI rendering)

### 11.4 Distribution and Bundling

Assets support multiple distribution models:

1. **Package Distribution**: Practice Language documents + `assets/` directory packaged as a `.keleo` archive
2. **Single-File Distribution**: Small assets embedded as data URIs within JSON
3. **Remote Hosting**: Assets hosted externally, referenced by URL
4. **Font Characters**: Icon fonts loaded separately, referenced by family/character

**Package Format (`.keleo`):**

Practice Language documents with file-based assets are distributed as `.keleo` packages — ZIP archives (MIME type `application/vnd.keleo.package+zip`) with a defined internal structure and a `manifest.json` describing the package contents. A package can contain any root type (practices, baselines, methods, projects) and supports externalised practice distribution where the merge algorithm resolves symbolic name references from the package's document inventory.

For the complete specification — including manifest schema, directory layout, validation rules, and package resolution — see [specifications/packaging.md](../specifications/packaging.md). The manifest schema is defined as `$defs/PackageManifest` in `language.schema.json`.

**Package as Library:**

When a Method uses `practiceNames` or `baselinePracticeName` string references, the merge algorithm requires a library lookup index (see [merge.md](../merge.md), Section 2.3). A `.keleo` package serves as such a library: its manifest maps document names to file paths, enabling the merge algorithm to resolve names to document bodies without external configuration.

**Asset Embedding (Alternative):**

For documents requiring single-file distribution, small assets (icons, simple diagrams) can be embedded using data URIs in the `dataUri` field:

```json
{
  "name": "practice-icon",
  "description": "Practice identity icon",
  "dataUri": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53...",
  "mimeType": "image/svg+xml",
  "checksum": "sha256:abc123..."
}
```

This approach maintains single-file portability while supporting asset references. However, file-based assets (packaged in a `.keleo` archive) are recommended for:

- Assets larger than 10KB
- Assets that change frequently
- Binary formats (PNG, JPEG, PDF)
- Practices under version control

### 11.5 Validation Rules

- Asset names must be unique within the practice
- All `assetName` values within `AssetReference` objects must resolve to a defined asset in the `assets` array
- Asset paths must be relative (no absolute paths or URLs in the `path` field)
- Checksums should be validated when loading the bundle
- Missing asset files should generate validation warnings (not errors, to support partial bundles)

### 11.6 Semantic Guidance

- **Multiple assets per element**: Each element can reference multiple assets via `assetNames` array, each with a semantic `type` classification
- **Asset names must be unique**: Within a practice or method, asset names are unique identifiers
- **Optional integrity verification**: `checksum` enables validation that downloaded/extracted assets match expected content
- **Accessibility**: Include meaningful `description` fields to support alternative text for visual assets

Assets are **optional metadata** that enhance practices but are never required for core functionality. Practices without assets remain fully valid.

### 11.7 Phase 2 Translation Guidance

When generating mapping guides, identify visual artifacts in source materials:

- Architecture diagrams
- State transition diagrams
- Workflow visualizations
- Example templates or screenshots
- Process maps

Document these as asset references in the mapping guide, with descriptions and proposed paths. Phase 3 JSON generation populates the `assets` array and links elements via `assetNames` (array of `AssetReference` objects with `assetName` and `type`).

### 11.8 Best Practices

- **Use SVG for diagrams**: Scalable, editable, text-based (git-friendly)
- **Include alt text**: Asset descriptions serve as accessibility text
- **Organize by type**: Group assets in subdirectories (diagrams, templates, icons)
- **Version assets**: Update checksums when assets change
- **Minimize file sizes**: Compress images, optimize SVGs
- **Document asset sources**: If diagrams use specific tools (draw.io, PlantUML), include source files

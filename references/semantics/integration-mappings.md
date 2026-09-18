[< Back to Semantic Guidance Hub](../semantics.md)

## 15 Integration Mappings

The IntegrationMapping system bridges external services -- CRM platforms, project management tools, document stores, data warehouses, and other enterprise systems -- to Practice Language project elements. Rather than embedding ad-hoc mapping instructions in skill code or agent prompts, the Practice Language provides a structured, validatable document type for declaring how external entities correspond to alphas, work products, outcomes, and actions.

### 15.1 Purpose and Design Rationale

External systems hold data that reflects the real-world state of a project's tracked concerns. A CRM records opportunity stages that correspond to alpha states; a project management tool tracks deliverables that correspond to work product instances; an analytics platform reports metrics that correspond to outcome measurements. Without structured mappings, every integration point requires custom code or natural-language instructions that are brittle, untestable, and opaque.

IntegrationMapping addresses this by introducing a standalone document type with the following design properties:

- **Decoupled from practices.** An IntegrationMapping references a practice or method by name but is authored, versioned, and distributed independently. The practice author defines the methodology; the integration author defines how a specific service type connects to it.
- **Organisation-specific.** Different organisations use different external systems, or configure the same system differently. A company's Salesforce instance may have custom fields, non-standard stage names, or unique opportunity types. IntegrationMappings capture these specifics without modifying the practice itself.
- **Structured and validatable.** Mapping rules are expressed as data, not prose. Validators can check that element references resolve against the target practice, that value maps cover expected external values, and that identity keys reference valid match targets.
- **Three-tier confidence model.** Not all mappings are deterministic. The tier system (direct, pattern, llm-assisted) makes the confidence level of each mapping explicit, enabling runtimes to execute deterministic mappings mechanically and route ambiguous ones to an LLM.

### 15.2 Three-Tier Mapping Model

Every MappingTarget, FieldMapping, QueryTemplate, and MappingCondition declares a `tier` that classifies its execution confidence. Different parts of the same mapping can use different tiers -- a single EntityMapping might use direct tiers for stage-to-state translation but an llm-assisted tier for matching activity descriptions.

**Direct tier** -- deterministic mapping: x maps to a.

Direct mappings require no interpretation. The external value maps to exactly one schema value through explicit enumeration or simple lookup. A generic runtime can execute direct mappings without LLM involvement.

Example: Salesforce opportunity stage "Discover" maps to the "Identified" state on the Opportunity alpha. The mapping is a literal string-to-string translation.

```json
{
  "name": "stage-to-state",
  "externalField": "STAGE_NAME",
  "tier": "direct",
  "target": { "property": "stateName" },
  "valueMap": [
    { "from": "Discover", "to": "Identified" },
    { "from": "Qualify", "to": "Validated" },
    { "from": "Propose", "to": "Solution Proposed" },
    { "from": "Negotiate", "to": "Agreement Reached" },
    { "from": "Closed Won", "to": "Won" }
  ]
}
```

**Pattern tier** -- regex or fuzzy matching: pattern maps to a.

Pattern mappings use regular expressions, substring matching, or other pattern-matching techniques. They are more flexible than direct mappings but still mechanically executable. A generic runtime can evaluate them without LLM involvement.

Example: detecting renewal opportunities by name pattern to route them to a different target.

```json
{
  "name": "renewal-detection",
  "description": "Skip sales-motion alpha for renewal opportunities",
  "when": "Opportunity.Name matches /renew(al)?/i",
  "then": "skip",
  "tier": "pattern"
}
```

**LLM-assisted tier** -- requires semantic interpretation.

LLM-assisted mappings are the least deterministic. They are used when the external data requires natural-language understanding to map correctly -- for example, matching free-text activity descriptions from a project management tool to method activities, or classifying unstructured notes into alpha state evidence. LLM-assisted mappings should be used as a fallback when direct or pattern tiers cannot cover the mapping reliably.

Example: matching external task descriptions to method activities.

```json
{
  "name": "task-to-activity",
  "externalField": "TASK_DESCRIPTION",
  "tier": "llm-assisted",
  "target": {
    "property": "value",
    "description": "Match the task description to the most appropriate Activity.name in the resolved practice scope. Consider the activity's description and worksOn references when selecting."
  }
}
```

**Tier selection guidance:**

| Criterion | Direct | Pattern | LLM-assisted |
|-----------|--------|---------|---------------|
| External values are a known, finite set | Yes | -- | -- |
| External values follow a predictable format | -- | Yes | -- |
| External values are free-text or context-dependent | -- | -- | Yes |
| Runtime can execute without LLM | Yes | Yes | No |
| Determinism | Guaranteed | High | Variable |

### 15.3 Document Structure and Root Discrimination

IntegrationMapping extends PracticeElement (inheriting `name`, `description`, `tags`, and `narratives`) and adds integration-specific properties. It is a root-level document type, discriminated in the schema's if/then/else chain by the presence of `serviceKind`. The check for `serviceKind` occurs before the Project check, so a document containing both `serviceKind` and `practiceName` is validated as an IntegrationMapping, not a Project.

**Required properties:**

- `serviceKind` -- functional classification of the external service: `crm`, `project-management`, `document-store`, `data-warehouse`, `api`, `file`. This is tool-agnostic: it describes what the service does, not which product it is. A Salesforce integration and a HubSpot integration both use `"crm"`.
- `entityMappings` -- array of EntityMapping objects (minimum 1), each declaring how one external entity type maps to schema elements.

**Optional practice/method reference:**

- `practiceName` -- symbolic link to the Practice whose elements this mapping targets.
- `methodName` -- symbolic link to the Method whose elements this mapping targets.
- These are mutually exclusive (enforced by a `oneOf` constraint). Both may be absent when the mapping targets baseline elements or is practice-agnostic.
- When present, validators check that `elementName` references in MappingTargets resolve against the named practice or method's merged element set.

**Other metadata:**

Standard document metadata: `version`, `schemaVersion`, `authors`, `createdAt`, `updatedAt`, `keywords`, `citations`, and `links`. The `links` array is particularly useful for referencing external API documentation or service configuration guides.

**Minimal example:**

```json
{
  "name": "salesforce-opportunities",
  "description": "Maps Salesforce Opportunity records to Customer Account Planning practice elements.",
  "serviceKind": "crm",
  "practiceName": "Customer Account Planning",
  "version": "1.0.0",
  "schemaVersion": "2.15.0",
  "authors": ["Integration Team"],
  "createdAt": "2026-09-01",
  "updatedAt": "2026-09-01",
  "keywords": ["salesforce", "crm", "opportunities"],
  "entityMappings": [ ]
}
```

### 15.4 Entity Mapping Authoring

Each EntityMapping covers one external entity type (e.g., "Opportunity", "Account", "Case") and declares what Practice Language elements it creates or updates. An IntegrationMapping contains one or more EntityMappings in its `entityMappings` array.

**Required properties:**

- `name` -- identifier for the mapping (e.g., `"opportunity-to-opportunity"`).
- `externalEntityType` -- the type name in the external system (e.g., `"Opportunity"`, `"Account"`, `"TSPC__AP__c"`). This is the external system's own vocabulary, not the Practice Language's.
- `targets` -- array of MappingTarget objects (minimum 1) declaring what schema elements this entity maps to.

**MappingTarget structure:**

Each target declares:

- `targetKind` -- which schema element type: `alpha`, `workProduct`, `outcome`, or `action`.
- `elementName` -- symbolic link resolved by `targetKind`. When `targetKind` is `alpha`, `elementName` must match an Alpha.name in the referenced practice; when `workProduct`, a WorkProduct.name; and so on.
- `tier` -- mapping confidence tier for this target.
- `instanceNameTemplate` (optional) -- template for generating instance names from external field values. Uses `{FieldName}` placeholders (e.g., `"{Opportunity.Name}"`). When omitted, the runtime generates an instance name from the element name.
- `condition` (optional) -- when this target applies. For direct/pattern tiers, a simple expression; for llm-assisted, a natural-language description.

**Cardinality:**

The `cardinality` property on EntityMapping declares the relationship between external entities and schema instances:

- `one-to-one` -- each external entity creates exactly one instance set.
- `one-to-many` -- each external entity creates multiple instances (e.g., an Account entity creates instances for each associated team member).
- `conditional` -- cardinality depends on runtime conditions (e.g., some opportunity types create additional alpha instances).

**Multiple targets per entity:**

A single EntityMapping can declare multiple targets. This is the common case -- an external entity typically maps to more than one schema element. For example, a Salesforce Opportunity might create both an alpha instance (tracking the opportunity's state progression) and a work product instance (the opportunity record itself as documentary evidence):

```json
{
  "name": "opportunity-mapping",
  "externalEntityType": "Opportunity",
  "cardinality": "one-to-one",
  "targets": [
    {
      "targetKind": "alpha",
      "elementName": "Opportunity",
      "instanceNameTemplate": "{Opportunity.Name}",
      "tier": "direct"
    },
    {
      "targetKind": "workProduct",
      "elementName": "Opportunity Record",
      "instanceNameTemplate": "{Opportunity.Name} Record",
      "tier": "direct"
    }
  ]
}
```

### 15.5 Field Mapping and Value Maps

FieldMappings connect external system fields to specific properties on schema element instances. They appear in the `fieldMappings` array on an EntityMapping.

**Required properties:**

- `name` -- identifier for this field mapping (e.g., `"stage-to-state"`, `"acv-to-deal-value"`).
- `externalField` -- field path in the external system (e.g., `"STAGE_NAME"`, `"ACV_OPPORTUNITY_AMOUNT"`).
- `tier` -- mapping confidence tier.
- `target` -- what schema property this field maps to.

**Target property resolution:**

The `target` object identifies which instance property receives the mapped value. It uses one of two mutually exclusive approaches (enforced by a `oneOf` constraint):

- `property` -- a well-known enum value: `stateName`, `metric`, `checklistState`, `levelOfDetailName`, `link`, `status`, `value`, `evidence`. Covers the most common mapping targets.
- `path` -- a JSON-path expression for custom property targets not covered by the property enum. Use when the target property is specific to a particular practice's instance structure.

When `property` is `metric`, the additional `metricName` and `metricUnit` fields identify which metric to write and its unit (e.g., `"metricName": "deal-value"`, `"metricUnit": "USD"`).

The optional `description` on the target provides guidance for the llm-assisted tier, explaining how to interpret and apply the mapping.

**Value maps:**

The `valueMap` array provides explicit value-to-value translations. Each entry has:

- `from` -- the external value to match (literal string, or regex when `matchType` is `pattern`).
- `to` -- the schema value to write.
- `matchType` (optional) -- how to compare: `exact` (default), `pattern` (regex), or `contains` (substring).

Value maps are evaluated in order; the first match wins. This ordering is significant when patterns overlap -- place more specific matches before general ones.

```json
{
  "name": "stage-to-state",
  "externalField": "STAGE_NAME",
  "tier": "direct",
  "target": { "property": "stateName" },
  "valueMap": [
    { "from": "Discover", "to": "Identified" },
    { "from": "Qualify", "to": "Validated" },
    { "from": "Propose", "to": "Solution Proposed" },
    { "from": "Closed Won", "to": "Won" },
    { "from": "Closed Lost", "to": "Lost" }
  ]
}
```

**Transforms:**

The optional `transform` field holds an expression applied to the external value before writing. Transforms handle formatting, unit conversion, URL construction, and similar mechanical adjustments. They are applied after value map resolution (if both are present, the value map resolves first, then the transform applies to the result).

Example: constructing a Salesforce link from a record ID.

```json
{
  "name": "opportunity-link",
  "externalField": "Id",
  "tier": "direct",
  "target": { "property": "link" },
  "transform": "https://mycompany.my.salesforce.com/{Id}"
}
```

### 15.6 Identity Resolution and Create vs Update

When an integration runtime processes external records, it must determine whether each record represents a new instance (create) or updates an existing one (update). The `identityKeys` array on EntityMapping provides the resolution rules.

**IdentityKey structure:**

- `externalField` -- field path in the external system used as the identity key.
- `matchTarget` -- what property on the existing instance to match against: `instanceName`, `linkUri`, `linkName`, or `metricValue`.
- `matchType` (optional) -- how to compare: `exact` (default), `contains`, or `pattern`.

**Resolution algorithm:**

1. For each external record, evaluate identity keys in array order.
2. For each identity key, compare the external field value against the `matchTarget` property on all existing instances of the relevant element type.
3. If a match is found, the external record updates the matched instance.
4. If no identity key produces a match, the external record creates a new instance.

Multiple identity keys provide fallback resolution -- the first match wins. This supports scenarios where the primary identity (e.g., a direct link URI) may not be present on older instances, so a secondary identity (e.g., instance name) serves as a fallback.

```json
"identityKeys": [
  {
    "externalField": "OPPORTUNITY_URL",
    "matchTarget": "linkUri",
    "matchType": "exact"
  },
  {
    "externalField": "OPPORTUNITY_NAME",
    "matchTarget": "instanceName",
    "matchType": "exact"
  }
]
```

### 15.7 Query Templates

The `queryTemplates` array on IntegrationMapping defines reusable query definitions for retrieving data from the external service. Query templates decouple the data retrieval logic from the mapping logic, making queries reusable and parameterisable.

**Properties:**

- `name` -- identifier for the query template (e.g., `"resolve-account"`, `"windowed-opportunities"`).
- `description` -- what data this query retrieves.
- `template` -- parameterised query string (SQL, SOQL, URL template, etc.). Uses `{paramName}` placeholders.
- `intent` -- natural-language description for LLM-routed queries. Used when the query cannot be expressed as a mechanical template.
- `parameters` -- declared parameters. Each parameter has a `name` (matching `{placeholders}` in the template), `description`, and optional `source` indicating where to resolve the value at runtime.
- `tier` -- execution tier. Direct/pattern templates can be executed mechanically by substituting parameters; llm-assisted intents need LLM interpretation.

Parameters are resolved at runtime from the ServiceConnection's `parameters` array on the IntegrationInstance. The parameter `name` in the query template matches the parameter `name` in the service connection, providing the resolution bridge.

```json
{
  "name": "windowed-opportunities",
  "description": "Retrieve opportunities modified within a time window",
  "template": "SELECT Id, Name, StageName, Amount FROM Opportunity WHERE Account.Name = '{accountName}' AND LastModifiedDate >= {syncWindowStart}",
  "parameters": [
    {
      "name": "accountName",
      "description": "Account name to filter opportunities",
      "source": "service.parameters"
    },
    {
      "name": "syncWindowStart",
      "description": "ISO timestamp for the start of the sync window",
      "source": "integration.lastSyncedAt"
    }
  ],
  "tier": "direct"
}
```

### 15.8 Conditional Logic

MappingConditions control when entity mappings or specific targets apply. They appear in the `conditions` array on EntityMapping.

**Required properties:**

- `name` -- identifier for the condition.
- `description` -- what this condition checks and why.
- `when` -- condition expression. For direct/pattern tiers, a simple evaluable expression. For llm-assisted tiers, a natural-language description.
- `then` -- action to take when the condition is true: `skip` (do not create/update), `use-target X` (apply a specific target by name), or `override-field Y` (replace a field mapping's value).

**Optional `tier`** defaults to the parent EntityMapping's predominant tier when omitted.

**Common patterns:**

**Subtype routing** -- different external subtypes should skip certain targets or route to alternative ones:

```json
{
  "name": "renewal-skip-sales-motion",
  "description": "Renewal opportunities do not progress the Sales Motion alpha",
  "when": "Opportunity.Type == 'Renewal'",
  "then": "skip",
  "tier": "direct"
}
```

**Conditional target activation** -- some targets only apply under specific conditions:

```json
{
  "name": "large-deal-escalation",
  "description": "Opportunities above threshold create an Escalation action",
  "when": "Opportunity.Amount > 500000",
  "then": "use-target escalation-action",
  "tier": "direct"
}
```

**LLM-assisted classification** -- when the condition requires semantic understanding:

```json
{
  "name": "strategic-account-detection",
  "description": "Detect whether the account is strategic from the account plan narrative",
  "when": "The Account Plan description indicates a strategic, long-term partnership focus rather than a transactional relationship",
  "then": "use-target strategic-account-alpha",
  "tier": "llm-assisted"
}
```

### 15.9 Conflict Resolution

When multiple data sources -- or multiple EntityMappings -- provide values for the same target property on the same instance, the conflict resolution system determines which value prevails.

**Document-level defaults:**

The `conflictPolicy` object on IntegrationMapping sets the baseline strategy:

- `defaultStrategy` -- applied when no field-specific rule matches: `first-writer`, `last-writer`, `highest-state`, or `manual`.
- `rules` -- array of field-specific overrides, each specifying a `property` and a `strategy`.

**Strategies:**

| Strategy | Behaviour | Best for |
|----------|-----------|----------|
| `first-writer` | First value written wins; subsequent writes are ignored | Instance names, identity properties |
| `last-writer` | Most recent value overwrites previous | Regularly refreshed data (metrics, timestamps) |
| `highest-state` | Keeps the value that represents the most advanced progression | Alpha state names (states should only advance) |
| `manual` | Flags the conflict for human resolution | Ambiguous or high-stakes properties |

**Entity-level priority:**

The `priority` field on EntityMapping resolves cross-mapping conflicts when multiple IntegrationMappings target the same element. Higher priority wins; default is 0. For example, a company-specific Salesforce mapping at priority 5 overrides a generic CRM mapping at priority 0.

**Example:**

```json
"conflictPolicy": {
  "defaultStrategy": "last-writer",
  "rules": [
    {
      "property": "stateName",
      "strategy": "highest-state",
      "description": "Alpha states should only advance; never regress from external data."
    },
    {
      "property": "instanceName",
      "strategy": "first-writer",
      "description": "Instance names are set on creation and should not be renamed by subsequent syncs."
    }
  ]
}
```

### 15.10 Project-Level Integration Instances

While IntegrationMapping declares mapping rules in the abstract, IntegrationInstance connects those rules to a specific external service within a specific project. IntegrationInstances appear in the `integrations` array on the Project type.

**Required properties:**

- `name` -- project-specific label for this connection (e.g., `"Acme CRM - Opportunities"`).
- `integrationMappingName` -- symbolic link to an IntegrationMapping document. Must match the IntegrationMapping's `name` property. The runtime resolves the mapping document from the available bundles.
- `service` -- a ServiceConnection object carrying the connection details.

**ServiceConnection:**

The ServiceConnection identifies the specific external service instance:

- `tool` -- name of the external tool or platform (e.g., `"Salesforce"`, `"Jira"`, `"Dataverse"`). Tool-agnostic: describes the tool, not vendor API vocabulary.
- `link` -- canonical URI for this service instance (an ExternalLink). For example, the Salesforce org URL or Jira project URL.
- `parameters` -- connection-specific parameter values resolved for this project. Parameter names should match `QueryTemplate.parameters` defined in the referenced IntegrationMapping.

**Sync state:**

- `status` -- current state of the integration: `active`, `paused`, or `disconnected`.
- `lastSyncedAt` -- ISO timestamp of the most recent sync operation. Runtimes update this after each successful sync.
- `notes` -- timestamped journal of sync operations and observations (array of Note objects). Provides an audit trail of what was synced, when, and any issues encountered.

**Multiple integrations per project:**

A Project can have multiple IntegrationInstances. Common scenarios:

- Different systems serving different aspects of the project (CRM for opportunities, Jira for delivery actions).
- Multiple configurations of the same system (e.g., two Salesforce orgs with different mappings).
- Staged migration from one integration to another (old integration paused, new one active).

**Example:**

```json
{
  "integrations": [
    {
      "name": "Acme CRM - Opportunities",
      "integrationMappingName": "salesforce-opportunities",
      "service": {
        "tool": "Salesforce",
        "link": {
          "name": "Acme Salesforce Org",
          "uri": "https://acme.my.salesforce.com"
        },
        "parameters": [
          {
            "name": "accountName",
            "value": "Acme Corporation",
            "description": "Primary account for opportunity filtering"
          }
        ]
      },
      "status": "active",
      "lastSyncedAt": "2026-09-15T14:30:00Z",
      "notes": [
        {
          "text": "Initial sync: 12 opportunities imported, 3 skipped (renewal type).",
          "author": "sync-agent",
          "createdAt": "2026-09-15T14:30:00Z"
        }
      ]
    }
  ]
}
```

### 15.11 Bundle Distribution

IntegrationMappings are distributed in `.keleo` bundles using the `"integrationMapping"` value in the PackageManifest's `documentType` enum. This places them alongside the existing document types (`practiceBaseline`, `practice`, `method`, `project`, `changeRequest`, `changeSet`).

**Distribution patterns:**

- **Bundled with a practice.** A practice author may include generic IntegrationMappings alongside the practice itself, providing out-of-the-box integration for common service types. Both documents appear as entries in the same PackageManifest.
- **Standalone mapping bundle.** An integration mapping can be packaged and distributed independently. This is the common pattern for organisation-specific mappings -- a company packages its Salesforce-specific mapping separately from the generic practice it targets.
- **Multiple mappings per bundle.** A bundle can contain several IntegrationMappings (e.g., one for CRM, one for project management), each as a separate document entry in the manifest.

**Practice resolution:**

When an IntegrationMapping declares `practiceName` or `methodName`, the runtime must resolve the referenced practice or method bundle. This resolution is a tooling concern -- the IntegrationMapping itself carries only the symbolic name, not a direct file reference. The runtime's bundle resolution mechanism locates the practice bundle, loads its element set, and validates that the IntegrationMapping's element references (`elementName` values in MappingTargets, `metricName` values in FieldMappings) resolve against the practice's merged element set.

**Versioning independence:**

IntegrationMappings follow the same versioning conventions as other Practice Language documents (see [Section 3.3](../semantics.md#33-schema-versioning-and-document-compatibility)). Their version evolves independently of the practice they reference. A practice at version 2.0.0 may be paired with an IntegrationMapping at version 1.3.0 -- the mapping was updated less frequently because the external system's data model changed less often than the practice content.

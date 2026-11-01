"""Resolve one caller-supplied project snapshot; never discover or mutate files."""

import hashlib
import json
from uuid import UUID

from jsonschema import Draft202012Validator

from signal_validation import FORMATS, SignalValidator, document_type


def project_key(value):
    return str(UUID(value))


def document_revision(document):
    data = json.dumps(document, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return 'sha256:' + hashlib.sha256(data.encode('utf-8')).hexdigest()


def reference_key(reference):
    return (project_key(reference['projectId']), reference.get('collection'),
            reference.get('cycleName'), reference.get('instanceName'), reference.get('reportName'))


def named_elements(document):
    """Walk the new authored elements, not operational receipts or copied history."""
    children = ('reports', 'reportingRequirements', 'projectCreationTemplates',
                'bindings', 'selectors', 'variants', 'reportingBindings')
    for collection in children:
        for index, element in enumerate(document.get(collection, [])):
            path = f'{collection}[{index}]'
            yield path, element
            for suffix, child in named_elements(element):
                yield f'{path}.{suffix}', child
    if 'metric' in document:
        yield 'metric', document['metric']


class ProjectCatalogue:
    def __init__(self, schema, catalogue=None, project=None, documents=(), preflight=False):
        self.schema = schema
        self.supplied = catalogue is not None
        self.preflight = preflight
        self.errors, self.warnings = [], []
        self.projects, self.revisions, self.physical_parents = {}, {}, {}
        self.documents = []
        pending = list(documents)
        while pending:
            document = pending.pop(0)
            if not self.check(document):
                continue
            if document in self.documents:
                continue
            self.documents.append(document)
            pending.extend(p for p in document.get('practices', []) if isinstance(p, dict))
            if isinstance(document.get('baselinePractice'), dict):
                pending.append(document['baselinePractice'])
        self.usable = True
        if catalogue is not None and not self.check(catalogue, 'ProjectCatalogue'):
            self.usable = False
            return
        for index, entry in enumerate((catalogue or {}).get('projects', [])):
            document = entry['document']
            key = project_key(document['projectId'])
            if key in self.projects:
                self.issue('DUPLICATE_PROJECT_ID', 'Duplicate project UUID', document['projectId'],
                           path=f'projects[{index}]')
                continue
            self.projects[key], self.revisions[key] = document, entry['revision']
            if 'containingProjectId' in entry:
                self.physical_parents[key] = project_key(entry['containingProjectId'])
        if project is not None:
            if not self.check(project, 'Project'):
                self.usable = False
                return
            key = project_key(project['projectId'])
            if key in self.projects and self.projects[key] != project:
                self.issue('CATALOGUE_SNAPSHOT_CONFLICT', 'Project file differs from catalogue snapshot', key)
            else:
                self.projects[key] = project

    def issue(self, code, message, project_id=None, path='', warning=False, **details):
        target = self.warnings if warning else self.errors
        target.append({'category': 'catalogue', 'severity': 'warning' if warning else 'error',
                       'code': code, 'projectId': project_id, 'path': path, 'issue': message, **details})

    def check(self, data, definition=None, issue=None):
        schema = {'$ref': f'#/$defs/{definition}', '$defs': self.schema['$defs']} if definition else self.schema
        errors = list(Draft202012Validator(schema, format_checker=FORMATS).iter_errors(data))
        for error in errors:
            path = '.'.join(map(str, error.absolute_path))
            (issue or self.issue)('SCHEMA_INVALID', error.message, path=path)
        return not errors

    def project(self, project_id, issue=None):
        result = self.projects.get(project_key(project_id))
        if result is None:
            (issue or self.issue)('PROJECT_UNRESOLVED', 'Project is absent from the supplied snapshot',
                                  source={'projectId': project_id})
        return result

    def children(self, project_id):
        key = project_key(project_id)
        return [doc for doc in self.projects.values()
                if 'parentProject' in doc and project_key(doc['parentProject']['projectId']) == key]

    def delegated_origin(self, reference):
        if reference['collection'] not in ('current.alphaInstances', 'current.workProductInstances'):
            return None
        for project in self.projects.values():
            for operation in project.get('delegations', []):
                if operation['status'] != 'committed':
                    continue
                for transfer in operation['preview']['instanceMappings']:
                    target = transfer['target']
                    same_kind = ('alphaInstance' in target['collection']) == ('alphaInstance' in reference['collection'])
                    if (project_key(target['projectId']) == project_key(reference['projectId'])
                            and target['instanceName'] == reference['instanceName'] and same_kind):
                        return transfer['origin'], transfer['originalSource']
        return None

    def ancestors(self, project_id):
        chain, seen = [], set()
        current = self.projects.get(project_key(project_id))
        while current and project_key(current['projectId']) not in seen:
            seen.add(project_key(current['projectId']))
            chain.append(current)
            parent = current.get('parentProject', {}).get('projectId')
            current = self.projects.get(project_key(parent)) if parent else None
        return list(reversed(chain))

    def items(self, project, reference):
        parts = reference['collection'].split('.')
        value = project
        if parts[0] == 'cycles':
            cycles = [c for c in project.get('cycles', []) if c['name'] == reference['cycleName']]
            if len(cycles) != 1:
                return []
            value, parts = cycles[0], parts[1:]
        for part in parts:
            value = value.get(part, {})
        return value if isinstance(value, list) else []

    def item(self, reference, issue=None, project=None):
        callback = issue or self.issue
        owner = project if project is not None else self.project(reference['projectId'], callback)
        if owner is None:
            return None
        matches = [item for item in self.items(owner, reference)
                   if item.get('name') == reference['instanceName']]
        if len(matches) != 1:
            callback('INSTANCE_UNRESOLVED' if not matches else 'INSTANCE_AMBIGUOUS',
                     'Expected exactly one instance in the specified collection', source=reference)
            return None
        return matches[0]

    def report(self, reference, issue=None):
        callback = issue or self.issue
        owner = self.project(reference['projectId'], callback)
        if owner is None:
            return None
        matches = [report for report in owner.get('reports', [])
                   if report['name'] == reference['reportName']]
        if len(matches) != 1:
            callback('REPORT_UNRESOLVED' if not matches else 'REPORT_AMBIGUOUS',
                     'Expected exactly one named report', source=reference)
            return None
        return matches[0]

    def methodology(self, reference, issue=None):
        matches = [document for document in self.documents
                   if document_type(document) == reference['documentType']
                   and document.get('name') == reference['documentName']
                   and document.get('version') == reference['version']]
        if len(matches) != 1:
            (issue or self.issue)('METHODOLOGY_UNRESOLVED', 'Expected exactly one pinned methodology',
                                  source=reference)
            return None
        return matches[0]

    def scope(self, project, issue=None):
        kind = 'practice' if 'practiceName' in project else 'method'
        name = project.get(f'{kind}Name')
        matches = [doc for doc in self.documents if document_type(doc) == kind and doc.get('name') == name]
        if len(matches) != 1:
            (issue or self.issue)('METHODOLOGY_UNRESOLVED', 'Project methodology is not uniquely supplied',
                                  source={'documentType': kind, 'documentName': name})
            return []
        return self.methodology_scope(matches[0], issue)

    def methodology_scope(self, document, issue=None):
        resolver = SignalValidator(self.schema, self.documents, self.preflight)
        scope = resolver.elements(document, 'methodology')
        for diagnostic in resolver.errors + resolver.warnings:
            (issue or self.issue)('METHODOLOGY_UNRESOLVED', diagnostic['issue'], path=diagnostic['path'])
        return scope

    def validate(self):
        if not self.usable:
            return
        for key, document in self.projects.items():
            parent = document.get('parentProject', {}).get('projectId')
            if parent:
                parent_key = project_key(parent)
                if parent_key == key:
                    self.issue('OWNERSHIP_SELF', 'A project cannot own itself', key)
                if parent_key not in self.projects:
                    self.issue('PARENT_UNRESOLVED', 'Owning parent is absent from the snapshot', key,
                               warning=not self.supplied and not self.preflight, source=document['parentProject'])
            physical = self.physical_parents.get(key)
            if physical and (not parent or physical != project_key(parent)):
                self.issue('OWNERSHIP_LOCATION_CONFLICT', 'Declared owner differs from containing project', key,
                           source=document.get('parentProject', {}), relatedReferences=[{'projectId': physical}])
            for reference in document.get('projectReferences', []):
                if project_key(reference['projectId']) not in self.projects:
                    self.issue('PROJECT_UNRESOLVED', 'Non-owning project reference is unresolved', key,
                               warning=not self.supplied and not self.preflight, source=reference)
            seen, current = set(), key
            while current in self.projects:
                if current in seen:
                    self.issue('OWNERSHIP_CYCLE', 'Ownership contains a cycle', key,
                               relatedReferences=[{'projectId': pid} for pid in sorted(seen)])
                    break
                seen.add(current)
                owner = self.projects[current].get('parentProject', {}).get('projectId')
                current = project_key(owner) if owner else None
            names = [r['name'] for r in document.get('reports', [])]
            if len(names) != len(set(names)):
                self.issue('REPORT_AMBIGUOUS', 'Report names must be unique within a project', key)

    def validate_project_inventory(self, manifest, documents_by_path):
        """Package consumers supply already loaded ZIP entries; no archive IO here."""
        if not self.check(manifest, 'PackageManifest'):
            return False
        seen = set()
        for entry in manifest['documents']:
            if entry['documentType'] != 'project':
                continue
            document = documents_by_path.get(entry['path'])
            if document is None:
                self.issue('PACKAGE_PROJECT_UNRESOLVED', 'Project inventory path has no loaded document', source=entry)
                continue
            if not self.check(document, 'Project'):
                continue
            key = project_key(entry['projectId'])
            if key != project_key(document['projectId']) or entry['documentName'] != document['name']:
                self.issue('PACKAGE_PROJECT_IDENTITY_MISMATCH', 'Inventory UUID/name differs from the packaged project', source=entry)
            if key in seen:
                self.issue('DUPLICATE_PROJECT_ID', 'Package contains duplicate project identities', key)
            seen.add(key)
        return not self.errors


def validate_element_metadata(document, scope, issue, inherited_templates=()):
    """Apply PracticeElement metadata semantics to the new authored collections."""
    inherited = {(t['name'], t['version']) for t in inherited_templates}
    assets = {a['name'] for doc in scope for a in doc.get('assets', [])}
    citations = {c['name'] for doc in scope for c in doc.get('citations', [])}
    narratives = {n['name']: n for doc in scope for n in doc.get('narrativeTypes', [])}
    for path, element in named_elements(document):
        template = path.startswith('projectCreationTemplates[')
        top = document.get('projectCreationTemplates', [])
        ancestor = next((t for i, t in enumerate(top) if path.startswith(f'projectCreationTemplates[{i}]')), None)
        inherited_here = template and ancestor and '.' not in path and (ancestor['name'], ancestor['version']) in inherited
        if 'specificity' in element:
            issue('ELEMENT_METADATA_INVALID', 'specificity is merge output, not authored metadata', path=path)
        if ('specificityName' in element or element.get('suppressed')) and not inherited_here and 'requirementId' not in element:
            issue('ELEMENT_METADATA_INVALID', 'Specificity and suppression require an inherited methodology element', path=path)
        for reference in element.get('assetNames', []):
            if reference['assetName'] not in assets:
                issue('ASSET_UNRESOLVED', 'Element references an undefined asset', path=path, source=reference)
        for narrative in element.get('narratives', []):
            definition = narratives.get(narrative['narrativeTypeName'])
            if definition is None:
                issue('NARRATIVE_UNRESOLVED', 'Element references an undefined narrative type', path=path)
                continue
            names = {n['name'] for n in definition.get('narrativeElements', [])}
            if any(c['narrativeElementName'] not in names for c in narrative['narrativeContexts']):
                issue('NARRATIVE_UNRESOLVED', 'Narrative context references an undefined element', path=path)
            if any(c not in citations for c in narrative.get('citationNames', [])):
                issue('CITATION_UNRESOLVED', 'Narrative references an undefined citation', path=path)

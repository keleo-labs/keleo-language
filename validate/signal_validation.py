"""Schema 3.3 signal integrity checks shared by journal, mapping and project CLIs."""

from copy import deepcopy
from datetime import datetime
import json
import re

from jsonschema import Draft202012Validator, FormatChecker


FORMATS = FormatChecker()


def parse_timestamp(value):
    return datetime.fromisoformat(value.upper().replace('Z', '+00:00'))


@FORMATS.checks('date-time', raises=ValueError)
def valid_timestamp(value):
    """Check RFC 3339 without jsonschema's optional format dependencies."""
    if not isinstance(value, str):
        return True
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-](?:[01]\d|2[0-3]):[0-5]\d)', value):
        return False
    parse_timestamp(value)
    return True


def document_type(document):
    if 'journalKind' in document:
        return 'signalJournal'
    if 'serviceKind' in document:
        return 'integrationMapping'
    if 'changeId' in document:
        return 'changeRequest'
    if 'plan' in document and ('practiceName' in document or 'methodName' in document):
        return 'project'
    if any(key in document for key in ('practices', 'practiceNames', 'baselinePractice')):
        return 'method'
    if 'baselinePracticeName' in document:
        return 'practice'
    return 'practiceBaseline'


def collection_items(project, collection):
    for part in collection.split('.'):
        project = project.get(part, {})
    return project if isinstance(project, list) else []


class SignalValidator:
    """Validate snapshots; preflight additionally checks current write preconditions.

    This validator never fetches sources, evaluates rule text or applies writes.
    """

    def __init__(self, schema, documents=(), preflight=False):
        self.schema = schema
        self.preflight = preflight
        self.errors = []
        self.warnings = []
        self.documents = {}
        self.checked_journals = set()
        for idx, document in enumerate(documents):
            if not self.schema_check(document, path=f'documents[{idx}]'):
                continue
            key = (document_type(document), document.get('name', document.get('changeId')))
            if key[0] == 'integrationMapping':
                key += (document.get('version'),)
            if key in self.documents:
                self.issue('documents', f'Duplicate loaded document identity: {key}')
            self.documents[key] = document

    def issue(self, path, message, warning=False):
        target = self.warnings if warning else self.errors
        target.append({'category': 'signal', 'severity': 'warning' if warning else 'error',
                       'path': path, 'issue': message})

    def schema_check(self, document, definition=None, path='root'):
        schema = {'$ref': f'#/$defs/{definition}', '$defs': self.schema['$defs']} if definition else self.schema
        validator = Draft202012Validator(schema, format_checker=FORMATS)
        errors = list(validator.iter_errors(document))
        for error in errors:
            suffix = '.'.join(str(item) for item in error.absolute_path)
            self.issue(f'{path}.{suffix}' if suffix else path, error.message)
        return not errors

    def index(self, items, path, key='name'):
        indexed = {}
        for idx, item in enumerate(items):
            name = item[key]
            if name in indexed:
                self.issue(f'{path}[{idx}].{key}', f'Duplicate {key}: {name}')
            indexed[name] = item
        return indexed

    def resolve(self, kind, name, path, version=None):
        key = (kind, name, version) if kind == 'integrationMapping' else (kind, name)
        document = self.documents.get(key)
        if document is None:
            label = f'{name}@{version}' if version else name
            self.issue(path, f'Unresolved {kind} document: {label}', warning=not self.preflight)
        return document

    def elements(self, document, path, seen=None):
        """Collect supplied scope; consumers may supply an already composed method."""
        seen = set() if seen is None else seen
        key = (document_type(document), document.get('name'))
        if key in seen:
            return []
        seen.add(key)
        result = [document]
        for field in ('baselinePractice', 'practices'):
            embedded = document.get(field, [])
            if isinstance(embedded, dict):
                embedded = [embedded]
            for entry in embedded:
                if isinstance(entry, dict):
                    result.extend(self.elements(entry, path, seen))
                elif isinstance(entry, str):
                    dependency = self.resolve('practice', entry, path)
                    if dependency:
                        result.extend(self.elements(dependency, path, seen))
        for field, kind in (('practiceName', 'practice'), ('methodName', 'method'),
                            ('baselinePracticeName', 'practiceBaseline')):
            if document.get(field):
                dependency = self.resolve(kind, document[field], path)
                if dependency:
                    result.extend(self.elements(dependency, path, seen))
        for field in ('practiceNames', 'practiceDependencyNames'):
            for name in document.get(field, []):
                dependency = self.resolve('practice', name, path)
                if dependency:
                    result.extend(self.elements(dependency, path, seen))
        return result

    def check_elements(self, scope, references, path):
        collections = {'alpha': 'alphas', 'workProduct': 'workProducts',
                       'outcome': 'outcomes', 'activity': 'activities'}
        for reference in references:
            kind = reference['targetKind']
            if kind == 'action':
                continue  # Existing mapping targets use an action name template.
            names = {item['name'] for doc in scope for item in doc.get(collections[kind], [])}
            if reference['elementName'] not in names:
                self.issue(path, f"Unresolved {kind} element: {reference['elementName']}")

    def validate_mapping(self, mapping, context=None):
        rules = mapping.get('signalRules', [])
        if not rules:
            return
        if not self.schema_check(rules, 'SignalRuleList'):
            return
        self.index(rules, 'signalRules')
        queries = {query.get('name') for query in mapping.get('queryTemplates', [])}
        for idx, rule in enumerate(rules):
            path = f'signalRules[{idx}]'
            if rule['queryTemplateName'] not in queries:
                self.issue(path, f"Unresolved query template: {rule['queryTemplateName']}")
            if context:
                if not self.schema_check(context):
                    continue
                scope = self.elements(context, path)
                self.check_elements(scope, rule.get('targets', []), path)

    def check_chain(self, records, path):
        for name, record in records.items():
            previous = record.get('supersedes')
            if previous and previous not in records:
                self.issue(path, f'Unresolved supersedes reference: {previous}')
            visited = {name}
            while previous in records:
                if previous in visited:
                    self.issue(path, f'Cyclic supersedes chain at {previous}')
                    break
                visited.add(previous)
                previous = records[previous].get('supersedes')

    def validate_journal(self, journal, recommendation_names=None):
        if not self.schema_check(journal, 'SignalJournal'):
            return
        if journal['schemaVersion'].split('.')[0] != self.schema['$comment'].split(':')[1].split('.')[0]:
            self.issue('schemaVersion', 'Journal schema major version is incompatible')
        signals = self.index(journal['signals'], 'signals')
        self.index(journal['signals'], 'signals', 'sourceKey')
        recommendations = self.index(journal['recommendations'], 'recommendations')
        self.check_chain(signals, 'signals')
        self.check_chain(recommendations, 'recommendations')
        identities = set()
        for idx, recommendation in enumerate(journal['recommendations']):
            path = f'recommendations[{idx}]'
            for name in recommendation['signalNames']:
                if name not in signals:
                    self.issue(path, f'Unresolved signal: {name}')
            identity_data = {key: recommendation.get(key) for key in (
                'signalNames', 'context', 'integrationMappingName', 'mappingVersion',
                'ruleName', 'advice', 'proposals', 'changeRequestName')}
            identity_data['signalNames'] = sorted(identity_data['signalNames'])
            if identity_data['proposals']:
                identity_data['proposals'] = sorted(identity_data['proposals'],
                                                    key=lambda item: (item['collection'], item['value']['name']))
            identity_data['context'] = dict(identity_data['context'])
            identity_data['context']['elements'] = sorted(
                identity_data['context'].get('elements', []), key=lambda item: (item['targetKind'], item['elementName']))
            identity = json.dumps(identity_data, sort_keys=True)
            if identity in identities:
                self.issue(path, 'Duplicate recommendation for the same evidence, rule and context')
            identities.add(identity)
            context = recommendation['context']
            if recommendation_names is None or recommendation['name'] in recommendation_names:
                document = self.resolve(context['documentType'], context['documentName'], path)
                scope = self.elements(document, path) if document else []
                if document:
                    self.check_elements(scope, context.get('elements', []), path)
                self.check_rule(recommendation, path, scope)
                change_id = recommendation.get('changeRequestName')
                if change_id:
                    change = self.resolve('changeRequest', change_id, path)
                    if change and (change.get('targetDocumentName') != context['documentName'] or
                                   change.get('targetDocumentType') != context['documentType']):
                        self.issue(path, 'ChangeRequest targets a different methodology context')
            targets = set()
            for proposal in recommendation.get('proposals', []):
                target = (proposal['collection'], proposal['value']['name'])
                if target in targets:
                    self.issue(path, f'Duplicate proposal target: {target}')
                targets.add(target)
                if proposal['operation'] == 'update' and proposal['previous']['name'] != target[1]:
                    self.issue(path, 'Update cannot rename an instance')

    def check_rule(self, recommendation, path, scope=None):
        mapping = self.resolve('integrationMapping', recommendation['integrationMappingName'], path,
                               recommendation['mappingVersion'])
        if mapping and self.schema_check(mapping, 'IntegrationMapping', path):
            self.validate_mapping(mapping)
            if recommendation['ruleName'] not in {r['name'] for r in mapping.get('signalRules', [])}:
                self.issue(path, f"Unresolved signal rule: {recommendation['ruleName']}")
            if scope:
                for kind in ('practice', 'method'):
                    expected = mapping.get(f'{kind}Name')
                    if expected and not any(document_type(doc) == kind and doc.get('name') == expected for doc in scope):
                        self.issue(path, 'Mapping methodology does not match recommendation context')

    def validate_project(self, project):
        cards = project.get('recommendations', [])
        policies = project.get('recommendationPolicies', [])
        if not (cards or policies):
            return
        if not self.schema_check(project, 'Project'):
            return
        valid = self.schema_check(cards, 'RecommendationCardList', 'recommendations')
        valid = self.schema_check(policies, 'RecommendationPolicyList', 'recommendationPolicies') and valid
        if not valid:
            return
        policy_index = self.index(policies, 'recommendationPolicies')
        self.index(cards, 'recommendations')
        for policy in policies:
            self.check_rule(policy, 'recommendationPolicies')
        seen = set()
        for idx, card in enumerate(cards):
            path = f'recommendations[{idx}]'
            key = (card['journalName'], card['recommendationName'])
            if key in seen:
                self.issue(path, 'Duplicate card for the same journal recommendation')
            seen.add(key)
            members = {member['name'] for member in project.get('team', {}).get('members', [])}
            for member in card.get('assignedTo', []):
                if member not in members:
                    self.issue(path, f'Unresolved team member: {member}')
            attempts = card.get('applications', [])
            self.index(attempts, f'{path}.applications')
            successful = [attempt for attempt in attempts if attempt['outcome'] == 'succeeded']
            if len(successful) > 1:
                self.issue(path, 'Recommendation may succeed at most once')
            if bool(successful) != (card['status'] == 'applied'):
                self.issue(path, 'Only applied cards may contain a successful application')
            if attempts and card['status'] not in ('accepted', 'applied', 'dismissed'):
                self.issue(path, 'Application attempts require a decided card')
            if successful and attempts[-1] != successful[0]:
                self.issue(path, 'No application attempt may follow successful application')
            previous_time = card.get('decidedAt') if card['status'] != 'dismissed' else None
            for attempt in attempts:
                if previous_time and parse_timestamp(attempt['attemptedAt']) < parse_timestamp(previous_time):
                    self.issue(path, 'Application attempts must follow the decision and be chronological')
                previous_time = attempt['attemptedAt']
            if attempts and card['status'] == 'dismissed' and parse_timestamp(
                    attempts[-1]['attemptedAt']) > parse_timestamp(card['decidedAt']):
                self.issue(path, 'Dismissal must follow failed application attempts')
            journal = self.resolve('signalJournal', card['journalName'], path)
            if not journal:
                continue
            if not self.schema_check(journal, 'SignalJournal', path):
                continue
            if card['journalName'] not in self.checked_journals:
                self.checked_journals.add(card['journalName'])
                referenced = {c['recommendationName'] for c in cards if c['journalName'] == card['journalName']}
                self.validate_journal(journal, referenced)
            recommendation = next((r for r in journal['recommendations'] if r['name'] == card['recommendationName']), None)
            if recommendation is None:
                self.issue(path, f"Unresolved recommendation: {card['recommendationName']}")
                continue
            context = recommendation['context']
            if context['documentType'] == 'project':
                if context['documentName'] != project['name']:
                    self.issue(path, 'Recommendation belongs to another project')
            elif context['documentName'] != project.get(f"{context['documentType']}Name"):
                self.issue(path, 'Methodology recommendation does not match the project context')
            proposals = recommendation.get('proposals', [])
            if not proposals and attempts:
                self.issue(path, 'Advice and methodology recommendations cannot be applied as project changes')
            superseded = any(r.get('supersedes') == recommendation['name'] for r in journal['recommendations'])
            old_signals = {s['supersedes'] for s in journal['signals'] if 'supersedes' in s}
            if not successful and card['status'] in ('inbox', 'reviewing', 'accepted') and (
                    superseded or old_signals.intersection(recommendation['signalNames'])):
                self.issue(path, 'Recommendation or supporting signal has been superseded')
            for attempt in attempts:
                if attempt['mode'] == 'automatic':
                    policy = policy_index.get(attempt['policyName'])
                    if not policy or any(policy[key] != recommendation[key] for key in (
                            'integrationMappingName', 'mappingVersion', 'ruleName')) or any(
                            p['operation'] not in policy['operations'] or p['collection'] not in policy['collections']
                            for p in proposals):
                        self.issue(path, 'Automatic application lacks a matching project policy')
                    elif policy.get('revokedAt') and parse_timestamp(
                            attempt['attemptedAt']) >= parse_timestamp(policy['revokedAt']):
                        self.issue(path, 'Automatic application used a revoked project policy')
                if attempt['outcome'] == 'succeeded':
                    expected = {(p['collection'], p['value']['name']) for p in proposals}
                    actual = {(r['collection'], r['instanceName']) for r in attempt['results']}
                    if actual != expected:
                        self.issue(path, 'Application results must identify every proposal target exactly once')
                    for collection, name in actual:
                        if not any(item.get('name') == name for item in collection_items(project, collection)):
                            self.issue(path, f'Unresolved application result: {collection}/{name}')
            if self.preflight and card['status'] == 'accepted' and proposals:
                self.check_rule(recommendation, path)
                self.preflight_proposals(project, proposals, path)

    def preflight_proposals(self, project, proposals, path):
        candidate = deepcopy(project)
        for proposal in proposals:
            collection = proposal['collection']
            value = proposal['value']
            items = collection_items(candidate, collection)
            existing = next((item for item in items if item.get('name') == value['name']), None)
            if proposal['operation'] == 'create' and existing is not None:
                self.issue(path, f"Create target already exists: {collection}/{value['name']}")
            if proposal['operation'] == 'update' and existing != proposal['previous']:
                self.issue(path, f"Stale update precondition: {collection}/{value['name']}")
            # Build the candidate without changing the user's project.
            parent = candidate
            for part in collection.split('.')[:-1]:
                parent = parent[part]
            items = parent.setdefault(collection.split('.')[-1], [])
            if existing is not None:
                items.remove(existing)
            items.append(deepcopy(value))
        if not self.schema_check(candidate, 'Project', path):
            return
        scope = self.elements(project, path)
        for proposal in proposals:
            value = proposal['value']
            for field, kind, collection, progress, steps in (
                    ('alphaName', 'alpha', 'alphas', 'stateName', 'states'),
                    ('workProductName', 'workProduct', 'workProducts', 'levelOfDetailName', 'levelsOfDetail'),
                    ('outcomeName', 'outcome', 'outcomes', None, None),
                    ('activityName', 'activity', 'activities', None, None)):
                if field not in value:
                    continue
                self.check_elements(scope, [{'targetKind': kind, 'elementName': value[field]}], path)
                if progress and progress in value:
                    allowed = {step['name'] for doc in scope for element in doc.get(collection, [])
                               if element['name'] == value[field] for step in element.get(steps, [])}
                    if value[progress] not in allowed:
                        self.issue(path, f"Unresolved {progress}: {value[progress]}")
        # Reuse the project validator for cross-instance integrity after all writes.
        from importlib.util import module_from_spec, spec_from_file_location
        from pathlib import Path
        spec = spec_from_file_location('signal_project_preflight', Path(__file__).with_name('validate-project.py'))
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        validator = module.ProjectValidator.__new__(module.ProjectValidator)
        validator.project, validator.schema = candidate, self.schema
        validator.errors, validator.warnings = [], []
        for check in ('validate_instance_consistency', 'validate_instance_relationships', 'validate_actions'):
            getattr(validator, check)()
        self.errors.extend(validator.errors)
        self.warnings.extend(validator.warnings)

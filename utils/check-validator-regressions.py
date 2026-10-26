#!/usr/bin/env python3
"""Run focused regression checks for composition diagnostics and documented examples."""

import importlib.util
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest
from datetime import datetime, timezone
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'validate'))
from _venv_bootstrap import ensure_dependencies

ensure_dependencies()
from jsonschema import Draft202012Validator
from signal_validation import SignalValidator
from project_catalogue import ProjectCatalogue, document_revision, project_key, reference_key
from reporting_validation import ReportingValidator
from delegation_validation import DelegationValidator, validate_templates
from signal_validation import FORMATS, document_type


def load_validator(filename, classname):
    spec = importlib.util.spec_from_file_location(classname, ROOT / 'validate' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, classname)


BaselineValidator = load_validator('validate-baseline.py', 'BaselineValidator')
PracticeValidator = load_validator('validate-practice.py', 'PracticeValidator')
ProjectValidator = load_validator('validate-project.py', 'ProjectValidator')
IntegrationMappingValidator = load_validator('validate-integration-mapping.py', 'IntegrationMappingValidator')
SCHEMA = ROOT / 'language.schema.json'
FIXTURES = ROOT / 'validate' / 'fixtures'


class CompositionDiagnostics(unittest.TestCase):
    def test_baseline_group_deprecation(self):
        validator = BaselineValidator(FIXTURES / 'fixture-baseline.json', None, SCHEMA)
        for groups, count in (([], 0), ([{'name': 'Template', 'entries': []}], 1)):
            with self.subTest(groups=groups):
                validator.baseline['patternGroups'] = groups
                validator.warnings = []
                validator.validate_pattern_groups()
                self.assertEqual(len(validator.warnings), count)
                if count:
                    self.assertEqual(validator.warnings[0]['category'], 'deprecation')
                self.assertEqual(validator.errors, [])

    def test_merged_orchestration_progression(self):
        validator = PracticeValidator(FIXTURES / 'fixture-practice-orchestration.json',
                                      FIXTURES / 'fixture-baseline.json', SCHEMA)
        validator.practice = {'name': 'Local', 'patternOrchestrations': [
            {'name': 'Journey', 'stages': []}]}
        validator.dependencies = []
        for inherited, local, count in (([], [], 0), ([], ['onDemand'], 1),
                                        (['sequential'], ['onDemand'], 0),
                                        (['onDemand'], ['onDemand'], 1)):
            with self.subTest(inherited=inherited, local=local):
                validator.errors, validator.warnings = [], []
                validator.dependencies = [{'name': 'Dependency', 'patternOrchestrations': [
                    {'name': 'Journey', 'stages': [
                        {'patternName': 'Inherited', 'relationship': rel, 'seq': 1}
                        for rel in inherited]}]}]
                validator.practice['patternOrchestrations'][0]['stages'] = [
                    {'patternName': 'Local', 'relationship': rel, 'seq': 2} for rel in local]
                validator.validate_orchestrations()
                warnings = [w for w in validator.warnings if 'no sequential stage' in w['issue']]
                self.assertEqual(len(warnings), count)

    def test_documented_suppression_alpha(self):
        text = (ROOT / 'references/semantics/composition.md').read_text()
        section = text.split('### 4.9 Restricting Inherited Content', 1)[1]
        alpha = json.loads(re.search(r'```json\n(.*?)\n```', section, re.S).group(1))
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator({'$ref': '#/$defs/Alpha', '$defs': schema['$defs']}).validate(alpha)
        self.assertTrue(alpha['suppressed'])
        self.assertEqual(len(alpha['states']), 3)
        validator = PracticeValidator(FIXTURES / 'fixture-practice-orchestration.json',
                                      FIXTURES / 'fixture-baseline.json', SCHEMA)
        validator.practice.pop('patterns', None)
        validator.practice.pop('patternOrchestrations', None)
        validator.practice['alphas'] = [alpha]
        inherited = deepcopy(alpha)
        inherited.pop('suppressed')
        validator.baseline['alphas'].append(inherited)
        validator._index_baseline()
        self.assertTrue(validator.validate_schema(), validator.errors)
        self.assertTrue(validator.validate_redeclaration_vs_new(), validator.errors)
        self.assertTrue(validator.validate_suppression(), validator.errors)
        validator.practice['patterns'] = [{'name': 'Reference', 'patternViews': [
            {'name': 'View', 'alphaStates': [
                {'alphaName': alpha['name'], 'stateName': alpha['states'][0]['name']}]}]}]
        self.assertFalse(validator.validate_suppression())
        self.assertTrue(any('suppressed alpha' in error['issue'] for error in validator.errors))

    def test_method_contributions_warn_once(self):
        validator = PracticeValidator(FIXTURES / 'fixture-practice-orchestration.json',
                                      FIXTURES / 'fixture-baseline.json', SCHEMA)
        first = {'name': 'First', 'patternOrchestrations': [{'name': 'Journey', 'stages': [
            {'patternName': 'Host', 'relationship': 'onDemand', 'seq': 1}]}]}
        second = {'name': 'Second', 'patternOrchestrations': [{'name': 'Journey', 'stages': [
            {'patternName': 'Child', 'relationship': 'nested', 'seq': 1,
             'relativeTo': {'patternName': 'Host'}}]}]}
        validator.practice = {'practices': [first, second]}
        validator.validate_orchestrations()
        warnings = [w for w in validator.warnings if 'no sequential stage' in w['issue']]
        self.assertEqual(len(warnings), 1)
        first['patternOrchestrations'][0]['stages'][0]['relationship'] = 'sequential'
        validator.warnings = []
        validator.validate_orchestrations()
        self.assertFalse(any('no sequential stage' in w['issue'] for w in validator.warnings))


class ExternalSignals(unittest.TestCase):
    """Examples trace to specifications/external-signals.feature (RFE #23)."""

    def setUp(self):
        self.schema = json.loads(SCHEMA.read_text())
        self.journal = self.fixture('journal')
        self.project = self.fixture('project')
        self.mapping = self.fixture('mapping')
        self.practice = self.fixture('practice')
        self.baseline = json.loads((FIXTURES / 'fixture-baseline.json').read_text())

    def fixture(self, kind):
        return json.loads((FIXTURES / f'fixture-signal-{kind}.json').read_text())

    def checker(self, preflight=False):
        return SignalValidator(self.schema, [self.journal, self.project, self.mapping,
                                            self.practice, self.baseline], preflight)

    def project_check(self, preflight=False):
        checker = self.checker(preflight)
        checker.validate_project(self.project)
        return checker

    def apply_success(self, mode='automatic'):
        proposals = self.journal['recommendations'][0]['proposals']
        self.project['plan']['pattern']['alphaInstanceNames'] = [deepcopy(p['value']) for p in proposals]
        self.project['recommendations'][0].update(status='applied', applications=[{
            'name': 'attempt-1', 'attemptedAt': '2026-10-24T09:01:00Z',
            'actor': 'Account automation', 'mode': mode, 'outcome': 'succeeded',
            'results': [{'collection': p['collection'], 'instanceName': p['value']['name']} for p in proposals]}])
        if mode == 'automatic':
            self.project['recommendations'][0]['applications'][0]['policyName'] = self.project['recommendationPolicies'][0]['name']

    def test_discover_investment_and_methodology_advice(self):
        checker = self.checker(True)
        checker.validate_journal(self.journal)
        checker.validate_mapping(self.mapping, self.practice)
        checker.validate_project(self.project)
        self.assertEqual(checker.errors, [])
        self.assertEqual(checker.warnings, [])
        Draft202012Validator(self.schema).validate(self.journal)
        Draft202012Validator(self.schema).validate(self.mapping)
        Draft202012Validator(self.schema).validate(self.project)
        Draft202012Validator(self.schema).validate(self.practice)

    def test_existing_entity_mapping_remains_valid(self):
        self.mapping.pop('signalRules')
        self.mapping['entityMappings'] = [{'name': 'existing', 'externalEntityType': 'Account',
                                          'targets': [{'targetKind': 'alpha', 'elementName': 'Initiative', 'tier': 'direct'}]}]
        Draft202012Validator(self.schema).validate(self.mapping)
        checker = self.checker()
        checker.validate_mapping(self.mapping)
        self.assertFalse(checker.errors)

    def test_signal_rules_require_a_resolved_query(self):
        self.mapping['signalRules'][0]['queryTemplateName'] = 'missing'
        checker = self.checker()
        checker.validate_mapping(self.mapping, self.practice)
        self.assertTrue(any('query template' in e['issue'] for e in checker.errors))

    def test_empty_mapping_is_invalid(self):
        self.mapping.pop('signalRules')
        self.assertFalse(Draft202012Validator(self.schema).is_valid(self.mapping))

    def test_project_validator_entrypoint(self):
        validator = ProjectValidator(FIXTURES / 'fixture-signal-project.json', SCHEMA)
        self.assertTrue(validator.validate_schema(), validator.errors)
        self.assertTrue(validator.validate_recommendations(
            [self.journal, self.mapping, self.practice, self.baseline], True), validator.errors)

    def test_mapping_validator_entrypoint(self):
        validator = IntegrationMappingValidator(FIXTURES / 'fixture-signal-mapping.json', SCHEMA,
                                               FIXTURES / 'fixture-signal-practice.json')
        self.assertTrue(validator.validate_schema(), validator.errors)
        self.assertTrue(validator.validate_signal_rules(), validator.errors)

    def test_duplicate_source_fixture_is_invalid(self):
        checker = self.checker()
        checker.validate_journal(self.fixture('journal-invalid'))
        self.assertTrue(any('sourceKey' in e['issue'] for e in checker.errors))

    def test_unresolved_signal_is_invalid(self):
        self.journal['recommendations'][0]['signalNames'] = ['missing']
        checker = self.checker()
        checker.validate_journal(self.journal)
        self.assertTrue(any('Unresolved signal:' in e['issue'] for e in checker.errors))

    def test_duplicate_recommendation_and_card_are_invalid(self):
        duplicate = deepcopy(self.journal['recommendations'][0])
        duplicate['name'] = 'another-name'
        duplicate['proposals'].reverse()
        self.journal['recommendations'].append(duplicate)
        self.project['recommendations'].append(deepcopy(self.project['recommendations'][0]))
        checker = self.project_check()
        self.assertTrue(any('Duplicate recommendation' in e['issue'] for e in checker.errors))
        self.assertTrue(any('Duplicate card' in e['issue'] for e in checker.errors))

    def test_unloaded_documents_warn_or_fail_in_preflight(self):
        for strict in (False, True):
            checker = SignalValidator(self.schema, preflight=strict)
            checker.validate_project(self.project)
            self.assertEqual(bool(checker.errors), strict)
            self.assertEqual(bool(checker.warnings), not strict)

    def test_shared_journal_does_not_require_other_project_contexts(self):
        other = deepcopy(self.journal['recommendations'][1])
        other.update(name='other-project-advice', context={'documentType': 'project', 'documentName': 'Unloaded project'})
        self.journal['recommendations'].append(other)
        self.assertFalse(self.project_check(True).errors)
        checker = self.checker(True)
        checker.validate_journal(self.journal)
        self.assertTrue(any('Unloaded project' in e['issue'] for e in checker.errors))

    def test_rule_context_cannot_cross_methodology_boundaries(self):
        self.mapping['practiceName'] = 'Another practice'
        self.assertTrue(any('Mapping methodology' in e['issue'] for e in self.project_check(True).errors))

    def test_wrong_project_context_is_invalid(self):
        self.journal['recommendations'][0]['context']['documentName'] = 'Another account'
        self.assertTrue(any('another project' in e['issue'] for e in self.project_check().errors))

    def test_independent_project_decisions_on_shared_advice(self):
        first = self.project['recommendations'][0]
        first['recommendationName'] = self.journal['recommendations'][1]['name']
        other = deepcopy(self.project)
        other['name'] = 'Another company account plan'
        other['recommendations'][0]['status'] = 'dismissed'
        checker = self.checker()
        checker.validate_project(other)
        self.assertFalse(checker.errors, checker.errors)
        self.assertEqual(first['status'], 'accepted')

    def test_advice_cannot_have_application_receipts(self):
        self.apply_success('manual')
        self.project['recommendations'][0]['recommendationName'] = self.journal['recommendations'][1]['name']
        self.assertTrue(any('cannot be applied' in e['issue'] for e in self.project_check().errors))

    def test_automatic_and_manual_success(self):
        for mode in ('automatic', 'manual'):
            with self.subTest(mode=mode):
                self.apply_success(mode)
                checker = self.project_check(True)
                self.assertFalse(checker.errors, checker.errors)

    def test_automatic_success_requires_exact_policy(self):
        self.apply_success()
        for field, value in (('operations', ['update']), ('collections', ['actions']),
                             ('mappingVersion', '2.0.0'), ('ruleName', 'different')):
            with self.subTest(field=field):
                policy = self.project['recommendationPolicies'][0]
                original = policy[field]
                policy[field] = value
                self.assertTrue(any('authority' in e['issue'] or 'policy' in e['issue']
                                    for e in self.project_check().errors))
                policy[field] = original
        self.project['recommendationPolicies'] = []
        self.assertTrue(self.project_check().errors)

    def test_failed_application_retains_acceptance(self):
        self.project['recommendations'][0]['applications'] = [{
            'name': 'attempt-1', 'attemptedAt': '2026-10-24T09:01:00Z',
            'actor': 'Account team', 'mode': 'manual', 'outcome': 'failed', 'error': 'Storage unavailable'}]
        checker = self.project_check()
        self.assertFalse(checker.errors, checker.errors)
        self.assertEqual(self.project['recommendations'][0]['status'], 'accepted')

    def test_failed_application_can_be_dismissed_later(self):
        self.test_failed_application_retains_acceptance()
        self.project['recommendations'][0].update(status='dismissed', decidedAt='2026-10-24T10:00:00Z')
        self.assertFalse(self.project_check().errors)

    def test_policy_revocation_preserves_history(self):
        self.apply_success()
        policy = self.project['recommendationPolicies'][0]
        policy['revokedAt'] = '2026-10-24T10:00:00Z'
        self.assertFalse(self.project_check().errors)
        policy['revokedAt'] = '2026-10-24T09:01:00Z'
        self.assertTrue(any('revoked' in e['issue'] for e in self.project_check().errors))

    def test_archived_mapping_versions_resolve_independently(self):
        newer = deepcopy(self.mapping)
        newer['version'] = '2.0.0'
        checker = SignalValidator(self.schema, [self.mapping, newer, self.journal,
                                               self.project, self.practice, self.baseline], True)
        checker.validate_project(self.project)
        self.assertFalse(checker.errors, checker.errors)

    def test_timestamp_offsets_and_invalid_calendar_dates(self):
        self.apply_success('manual')
        card = self.project['recommendations'][0]
        card['decidedAt'] = '2026-10-24T10:00:00+01:00'
        self.assertFalse(self.project_check().errors)
        card['decidedAt'] = '2026-02-30T10:00:00Z'
        self.assertTrue(self.project_check().errors)
        card['decidedAt'] = '2026-10-24T10:00:00+01:60'
        self.assertTrue(self.project_check().errors)

    def test_malformed_referenced_documents_report_errors(self):
        checker = SignalValidator(self.schema, [[], {'name': []}])
        self.assertTrue(checker.errors)

    def test_success_requires_applied_status_and_complete_results(self):
        self.apply_success()
        card = self.project['recommendations'][0]
        card['status'] = 'accepted'
        self.assertTrue(self.project_check().errors)
        card['status'] = 'applied'
        card['applications'][0]['results'].pop()
        self.assertTrue(any('every proposal' in e['issue'] for e in self.project_check().errors))

    def test_duplicate_success_and_missing_result_are_invalid(self):
        self.apply_success()
        card = self.project['recommendations'][0]
        second = deepcopy(card['applications'][0])
        second['name'] = 'attempt-2'
        card['applications'].append(second)
        self.assertTrue(self.project_check().errors)
        card['applications'].pop()
        self.project['plan']['pattern']['alphaInstanceNames'] = []
        self.assertTrue(any('application result' in e['issue'] for e in self.project_check().errors))

    def test_conflicting_create_is_rejected_in_preflight(self):
        self.project['plan']['pattern']['alphaInstanceNames'] = [deepcopy(self.journal['recommendations'][0]['proposals'][0]['value'])]
        self.assertFalse(self.project_check().errors)
        self.assertTrue(any('already exists' in e['issue'] for e in self.project_check(True).errors))

    def test_update_preconditions_and_instance_identity(self):
        proposal = self.journal['recommendations'][0]['proposals'][0]
        proposal['operation'] = 'update'
        proposal['previous'] = deepcopy(proposal['value'])
        self.project['plan']['pattern']['alphaInstanceNames'] = [deepcopy(proposal['previous'])]
        proposal['value']['description'] = 'Reviewed investigation scope.'
        self.assertFalse(self.project_check(True).errors)
        self.project['plan']['pattern']['alphaInstanceNames'][0]['description'] = 'Changed by another user.'
        self.assertTrue(any('Stale update' in e['issue'] for e in self.project_check(True).errors))
        proposal['value']['name'] = 'renamed'
        self.assertTrue(any('rename' in e['issue'] for e in self.project_check().errors))

    def test_unknown_element_and_state_are_rejected(self):
        proposal = self.journal['recommendations'][0]['proposals'][0]
        proposal['value']['alphaName'] = 'Missing alpha'
        self.assertTrue(any('Missing alpha' in e['issue'] for e in self.project_check(True).errors))
        proposal['value']['alphaName'] = 'Initiative'
        proposal['collection'] = 'current.alphaInstances'
        proposal['value']['stateName'] = 'Missing state'
        self.assertTrue(any('stateName' in e['issue'] for e in self.project_check(True).errors))

    def test_typed_payloads_cover_each_supported_collection(self):
        alpha = {'name': 'Investigation', 'description': 'Investigate the signal.', 'alphaName': 'Initiative'}
        work_product = {'name': 'Investigation record', 'description': 'Supporting findings.', 'workProductName': 'Account research'}
        cases = [
            ('plan.pattern.alphaInstanceNames', alpha),
            ('plan.pattern.workProductInstanceNames', work_product),
            ('current.alphaInstances', dict(alpha, stateName='Identified')),
            ('target.alphaInstances', dict(alpha, stateName='Validated')),
            ('current.workProductInstances', dict(work_product, levelOfDetailName='Draft')),
            ('target.workProductInstances', dict(work_product, levelOfDetailName='Reviewed')),
            ('outcomes', {'name': 'Engagement', 'outcomeName': 'Account engagement'}),
            ('actions', {'name': 'Discuss report with the account team'})]
        for collection, value in cases:
            with self.subTest(collection=collection):
                for operation in ('create', 'update'):
                    proposal = {'operation': operation, 'collection': collection, 'value': value}
                    if operation == 'update':
                        proposal['previous'] = deepcopy(value)
                    checker = self.checker()
                    self.assertTrue(checker.schema_check(proposal, 'RecommendationProposal'), checker.errors)
                    proposal['value'] = dict(value, name=123)
                    self.assertFalse(checker.schema_check(proposal, 'RecommendationProposal'))

    def test_atomic_candidate_supports_references_without_mutating_project(self):
        proposals = self.journal['recommendations'][0]['proposals']
        proposals.append({'operation': 'create', 'collection': 'actions', 'value': {
            'name': 'Investigate the report', 'advancesAlphaInstances': [proposals[0]['value']['name']]}})
        original = deepcopy(self.project)
        checker = self.project_check(True)
        self.assertFalse(checker.errors, checker.errors)
        self.assertEqual(self.project, original)
        proposals[-1]['value']['advancesAlphaInstances'] = ['Missing initiative']
        self.assertTrue(self.project_check(True).errors)

    def test_signal_mapping_requires_versioned_provenance(self):
        self.mapping.pop('version')
        self.assertFalse(Draft202012Validator(self.schema).is_valid(self.mapping))

    def test_methodology_changes_cannot_be_project_proposals(self):
        recommendation = self.journal['recommendations'][0]
        recommendation['context'] = {'documentType': 'practice', 'documentName': self.practice['name']}
        self.assertFalse(Draft202012Validator(self.schema).is_valid(self.journal))

    def test_method_context_and_reviewed_change_request(self):
        recommendation = self.journal['recommendations'][1]
        recommendation['context'] = {'documentType': 'method', 'documentName': 'Account method'}
        recommendation['changeRequestName'] = 'editor-20261024-090000'
        checker = self.checker(True)
        checker.documents[('method', 'Account method')] = {'name': 'Account method', 'practices': [self.practice]}
        checker.documents[('changeRequest', recommendation['changeRequestName'])] = {
            'targetDocumentName': 'Account method', 'targetDocumentType': 'method'}
        checker.validate_journal(self.journal)
        self.assertFalse(checker.errors, checker.errors)
        checker.documents[('changeRequest', recommendation['changeRequestName'])]['targetDocumentName'] = 'Wrong method'
        checker.validate_journal(self.journal)
        self.assertTrue(any('different methodology' in e['issue'] for e in checker.errors))

    def test_superseded_proposals_block_pending_not_historical_cards(self):
        revised = deepcopy(self.journal['recommendations'][0])
        revised.update(name='revised', supersedes=revised['name'], advice='Investigate revised scope.')
        self.journal['recommendations'].append(revised)
        self.assertTrue(any('superseded' in e['issue'] for e in self.project_check().errors))
        self.apply_success()
        self.assertFalse(self.project_check().errors)

    def test_supersedes_cycles_and_dangling_references_are_invalid(self):
        for previous in ('missing', self.journal['signals'][0]['name']):
            self.journal['signals'][0]['supersedes'] = previous
            checker = self.checker()
            checker.validate_journal(self.journal)
            self.assertTrue(any('supersedes' in e['issue'] for e in checker.errors))

    def test_malformed_timestamps_and_untyped_payloads_are_invalid(self):
        self.project['recommendations'][0]['decidedAt'] = 'yesterday'
        self.assertTrue(self.project_check().errors)
        self.journal['recommendations'][0]['proposals'][0]['value'] = {'name': 'not-an-instance'}
        checker = self.checker()
        checker.validate_journal(self.journal)
        self.assertTrue(checker.errors)

    def test_journal_package_inventory(self):
        entry = {'path': 'documents/signals.json', 'documentType': 'signalJournal', 'documentName': self.journal['name']}
        Draft202012Validator({'$ref': '#/$defs/PackageDocument', '$defs': self.schema['$defs']}).validate(entry)


class ProjectHierarchy(unittest.TestCase):
    """Scenarios: specifications/project-hierarchy.feature, RFEs #26–#29."""

    def setUp(self):
        self.schema = json.loads(SCHEMA.read_text())
        self.catalogue = json.loads((FIXTURES / 'fixture-project-catalogue.json').read_text())
        self.parent, self.first, self.second = [entry['document'] for entry in self.catalogue['projects']]
        self.practice = json.loads((FIXTURES / 'fixture-signal-practice.json').read_text())
        self.practice['outcomes'] = [{'name': 'Value', 'description': 'Declared value for this project.'}]
        self.template = json.loads((FIXTURES / 'fixture-project-template.json').read_text())
        self.practice['projectCreationTemplates'] = [self.template]
        alternate = deepcopy(self.practice)
        alternate['name'] = 'Fixture Alternate Delivery'
        alternate.pop('projectCreationTemplates')
        self.baseline = json.loads((FIXTURES / 'fixture-baseline.json').read_text())
        self.documents = [self.practice, alternate, self.baseline]
        self.now = datetime(2026, 10, 26, 10, tzinfo=timezone.utc)

    def context(self, preflight=False):
        context = ProjectCatalogue(self.schema, self.catalogue, self.parent, self.documents, preflight)
        context.validate()
        return context

    def reporting(self, results=()):
        context = self.context()
        checker = ReportingValidator(context, results, self.now)
        checker.validate()
        return context, checker

    def definition(self, name):
        return Draft202012Validator({'$ref': f'#/$defs/{name}', '$defs': self.schema['$defs']}, format_checker=FORMATS)

    @staticmethod
    def codes(context, checker=None):
        diagnostics = context.errors + context.warnings
        if isinstance(checker, ReportingValidator):
            diagnostics += checker.summary()['diagnostics']
        return {d['code'] for d in diagnostics}

    def row(self, index, value_kind='target'):
        project = (self.first, self.second)[index]
        outcome = project['outcomes'][0]
        metadata = outcome['reportingSource']
        reference = {'projectId': project['projectId'], 'collection': 'outcomes', 'instanceName': 'Value'}
        row = {'bindingName': ('First delivery', 'Second delivery')[index], 'origin': metadata['identity'],
               'originalSource': reference, 'source': reference, 'metricId': metadata['metric']['metricId'],
               'metricVersion': '1.0.0', 'unit': 'GBP', 'period': metadata['period'], 'valueKind': value_kind,
               'inputRevision': self.catalogue['projects'][index + 1]['revision'], 'evidence': [],
               'value': outcome[value_kind + 'Value']}
        for field in ('observedAt', 'synchronizedAt'):
            if field in metadata:
                row[field] = metadata[field]
        return row

    def result(self, value_kind='target'):
        rows = [self.row(0, value_kind), self.row(1, value_kind)]
        return {'report': {'projectId': self.parent['projectId'], 'reportName': 'Targets'},
                'calculatedAt': '2026-10-26T10:00:00Z', 'complete': True,
                'contributions': rows, 'coverage': deepcopy(self.parent['reports'][0]['childCoverage']),
                'diagnostics': [], 'total': {'actual': 90, 'forecast': 230, 'target': 300}[value_kind]}

    def require_reports(self, **changes):
        contract = {field: deepcopy(self.parent['reports'][0][field]) for field in ('metric', 'aggregation', 'unit', 'period', 'valueKind')}
        requirement = {'name': 'Consistent targets', 'description': 'Comparable declared targets throughout the tree.',
                       'requirementId': 'example:targets', 'version': '1.0.0', 'coverAllChildren': True,
                       'allowExclusions': False, **contract, **changes}
        self.parent['reportingRequirements'] = [requirement]
        for project in (self.parent, self.first, self.second):
            project['reportingRequirementBindings'] = [{'requirementId': requirement['requirementId'],
                                                       'version': '1.0.0', 'reportName': 'Targets'}]
        return requirement

    def preview(self):
        child = deepcopy(self.first)
        child['projectId'] = '4b1a9e5b-8d7b-4ba6-b662-8ff24be2be76'
        child['name'] = 'Delegated delivery'
        child['plan']['pattern']['alphaInstanceNames'] = [{**self.parent['plan']['pattern']['alphaInstanceNames'][0], 'name': 'Delivery'}]
        original = self.parent['current']['alphaInstances'][0]
        child['current'] = {'alphaInstances': [{**deepcopy(original), 'name': 'Delivery'}]}
        child['target'] = {'alphaInstances': [{**deepcopy(self.parent['target']['alphaInstances'][0]), 'name': 'Delivery'}]}
        child['reports'][0]['bindings'][0]['source']['projectId'] = child['projectId']
        child['outcomes'][0]['reportingSource']['identity']['key'] = 'delegated-value'
        root = {'projectId': self.parent['projectId'], 'collection': 'plan.pattern.alphaInstanceNames', 'instanceName': 'Expansion'}
        assessed = {**root, 'collection': 'current.alphaInstances'}
        source_snapshot = {'source': assessed, 'recordedAt': '2026-10-26T09:00:00Z',
                           'attributedTo': 'Example owner', 'snapshot': deepcopy(original)}
        template_ref = {'methodology': {'documentType': 'practice', 'documentName': self.practice['name'], 'version': '1.0.0'},
                        'templateName': self.template['name'], 'version': '1.0.0'}
        return {'operationId': 'delegate-expansion-1', 'template': template_ref,
                'parentProjectId': self.parent['projectId'], 'source': root, 'variantName': 'Same practice',
                'sourceRevisions': [{'projectId': self.parent['projectId'], 'revision': 'parent-r1'}] + [
                    {'methodology': {'documentType': document_type(doc), 'documentName': doc['name'], 'version': doc['version']},
                     'revision': document_revision(doc)} for doc in (self.practice, self.baseline)],
                'sourceSnapshots': [source_snapshot], 'selectedItems': [root], 'child': child,
                'instanceMappings': [{'source': root, 'target': {'projectId': child['projectId'], 'collection': 'plan.pattern.alphaInstanceNames', 'instanceName': 'Delivery'},
                                      'assessmentTransfer': 'copy', 'origin': {'namespace': 'project:' + self.parent['projectId'], 'key': 'current.alphaInstances/Expansion'},
                                      'originalSource': assessed}],
                'actionMappings': [], 'reportingBindings': [{'parentReportName': 'Targets', 'childReport': deepcopy(child['reports'][0]),
                    'parentBinding': {'name': 'Delegated target', 'description': 'Child-owned delivery value.', 'sourceKind': 'report',
                                      'source': {'projectId': child['projectId'], 'reportName': 'Targets'}}}],
                'confirmedBy': 'Example owner', 'confirmedAt': '2026-10-26T09:30:00Z'}

    def delegation(self, preview, preflight=True):
        context = self.context(preflight)
        checker = DelegationValidator(context)
        checker.validate([preview])
        return context, checker

    def test_project_uuid_and_package_inventory_are_required(self):
        for identity in (None, '', 'Portfolio', '673dcb6bf27f4fd8a68521bf43d516bb'):
            project = deepcopy(self.parent)
            if identity is None:
                project.pop('projectId')
            else:
                project['projectId'] = identity
            self.assertFalse(self.definition('Project').is_valid(project))
        entry = {'path': 'documents/project.json', 'documentType': 'project', 'documentName': 'Portfolio'}
        self.assertFalse(self.definition('PackageDocument').is_valid(entry))
        entry['projectId'] = self.parent['projectId']
        self.definition('PackageDocument').validate(entry)
        legacy = deepcopy(self.parent)
        legacy.pop('projectId')
        legacy.pop('reports')
        legacy['schemaVersion'] = '3.3.0'
        original = deepcopy(legacy)
        migrated = deepcopy(legacy)
        migrated.update(projectId=self.parent['projectId'], schemaVersion='4.0.0')
        validator = ProjectValidator(FIXTURES / 'fixture-signal-project.json', SCHEMA, project=migrated)
        self.assertTrue(validator.validate_local(), validator.errors)
        self.assertEqual(legacy, original)
        migrated['schemaVersion'] = '3.3.0'
        self.assertFalse(validator.validate_schema_version())
        self.assertTrue(any(e['path'] == 'schemaVersion' for e in validator.errors))

    def test_rename_same_names_and_uuid_case_preserve_identity(self):
        context = self.context()
        ref = {'projectId': self.first['projectId'].upper(), 'collection': 'outcomes', 'instanceName': 'Value'}
        self.first['name'] = 'Renamed delivery'
        self.assertEqual(context.item(ref)['targetValue'], 100)
        self.assertEqual(len(context.children(self.parent['projectId'])), 2)
        self.assertEqual(context.errors, [])

    def test_duplicate_uuid_cycle_missing_parent_and_folder_disagreement(self):
        duplicate = deepcopy(self.catalogue['projects'][1])
        duplicate['document']['projectId'] = duplicate['document']['projectId'].upper()
        self.catalogue['projects'].append(duplicate)
        self.assertIn('DUPLICATE_PROJECT_ID', self.codes(self.context()))
        self.catalogue['projects'].pop()
        self.parent['parentProject'] = {'projectId': self.first['projectId']}
        self.assertIn('OWNERSHIP_CYCLE', self.codes(self.context()))
        self.parent.pop('parentProject')
        self.catalogue['projects'][1]['containingProjectId'] = self.second['projectId']
        self.assertIn('OWNERSHIP_LOCATION_CONFLICT', self.codes(self.context()))
        self.first['parentProject']['projectId'] = '11111111-1111-4111-8111-111111111111'
        self.assertIn('PARENT_UNRESOLVED', self.codes(self.context()))

    def test_nonowning_references_do_not_create_children(self):
        self.first.pop('parentProject')
        self.catalogue['projects'][1].pop('containingProjectId')
        self.parent['projectReferences'] = [{'projectId': self.first['projectId']}]
        self.assertEqual(len(self.context().children(self.parent['projectId'])), 1)

    def test_collection_and_cycle_scopes_do_not_fall_back(self):
        ref = {'projectId': self.first['projectId'], 'collection': 'current.alphaInstances', 'instanceName': 'Value'}
        context = self.context()
        self.assertIsNone(context.item(ref))
        self.assertIn('INSTANCE_UNRESOLVED', self.codes(context))
        ref['collection'] = 'cycles.outcomes'
        self.assertFalse(self.definition('ProjectItemReference').is_valid(ref))
        ref['cycleName'] = 'Iteration 1'
        self.definition('ProjectItemReference').validate(ref)

    def test_valid_actual_forecast_and_target_results_preserve_parent(self):
        original = deepcopy(self.catalogue)
        for kind in ('actual', 'forecast', 'target'):
            for project in (self.parent, self.first, self.second):
                project['reports'][0]['valueKind'] = kind
            context, checker = self.reporting([self.result(kind)])
            self.assertEqual(context.errors, [], context.errors)
            self.assertEqual(checker.summary()['diagnostics'], [])
        self.assertEqual(self.parent['outcomes'][0]['targetValue'], 400)
        self.assertEqual(self.parent['current'], original['projects'][0]['document']['current'])

    def test_repeated_lineage_is_counted_once(self):
        result = self.result()
        result['contributions'].append(deepcopy(result['contributions'][0]))
        context, checker = self.reporting([result])
        self.assertEqual(context.errors, [], context.errors)
        self.assertFalse(checker.summary()['diagnostics'])
        result['contributions'][-1]['value'] = 999
        context, checker = self.reporting([result])
        self.assertIn('REPORT_LINEAGE_CONFLICT', self.codes(context, checker))
        self.assertIn('REPORT_RESULT_FALSE_COMPLETE', self.codes(context, checker))

    def test_missing_targets_units_periods_and_derived_targets_are_gaps(self):
        self.first['outcomes'][0].pop('targetValue')
        context, checker = self.reporting()
        self.assertIn('REPORT_VALUE_MISSING', self.codes(context, checker))
        self.assertEqual(context.errors, [])
        self.first['outcomes'][0]['targetValue'] = 100
        self.first['outcomes'][0]['unit'] = 'USD'
        self.assertIn('REPORT_UNIT_MISMATCH', self.codes(*self.reporting()))
        self.first['outcomes'][0]['unit'] = 'GBP'
        self.first['outcomes'][0]['reportingSource']['period']['end'] = '2027-02-01T00:00:00Z'
        self.assertIn('REPORT_MEASUREMENT_MISMATCH', self.codes(*self.reporting()))
        self.first['reports'][0]['bindings'][0]['valueSource'] = 'derived'
        self.assertIn('REPORT_TARGET_DERIVATION_INVALID', self.codes(*self.reporting()))

    def test_target_weights_and_incomplete_headlines_are_rejected(self):
        result = self.result()
        result['contributions'][0].update(weight=0.5, rawValue=200)
        self.assertFalse(self.definition('ReportResult').is_valid(result))
        result = self.result()
        result['complete'] = False
        self.assertFalse(self.definition('ReportResult').is_valid(result))

    def test_local_value_requires_explicit_binding(self):
        report = self.parent['reports'][0]
        self.parent['outcomes'][0]['reportingSource'] = deepcopy(self.first['outcomes'][0]['reportingSource'])
        self.parent['outcomes'][0]['reportingSource']['identity']['key'] = 'parent-distinct-value'
        report['bindings'].append({'name': 'Local value', 'description': 'Explicit additional parent scope.', 'sourceKind': 'outcome',
                                   'source': {'projectId': self.parent['projectId'], 'collection': 'outcomes', 'instanceName': 'Value'}, 'valueSource': 'recorded'})
        result = self.result()
        row = self.row(0)
        row.update(bindingName='Local value', origin=self.parent['outcomes'][0]['reportingSource']['identity'],
                   source={**row['source'], 'projectId': self.parent['projectId']}, originalSource={**row['originalSource'], 'projectId': self.parent['projectId']},
                   inputRevision='parent-r1', value=400)
        result['contributions'].append(row)
        result['total'] = 700
        context, checker = self.reporting([result])
        self.assertEqual(context.errors, [], context.errors)
        self.assertFalse(checker.summary()['diagnostics'])

    def test_inherited_mapping_gaps_keep_local_project_valid(self):
        self.require_reports()
        self.first.pop('reportingRequirementBindings')
        context, checker = self.reporting()
        self.assertEqual(context.errors, [])
        self.assertIn('REQUIREMENT_MAPPING_MISSING', self.codes(context, checker))
        validator = ProjectValidator(FIXTURES / 'fixture-signal-project.json', SCHEMA, project=self.parent)
        self.assertTrue(validator.validate_local(), validator.errors)
        validator.validate_hierarchy(self.catalogue, self.documents, now=self.now)
        self.assertTrue(validator.generate_report()['valid'])
        self.assertFalse(validator.reporting['alignmentComplete'])

    def test_inherited_contract_conflicts_and_value_kinds(self):
        requirement = self.require_reports()
        weaker = deepcopy(requirement)
        weaker['allowExclusions'] = True
        self.first['reportingRequirements'] = [weaker]
        self.assertIn('REQUIREMENT_CONFLICT', self.codes(*self.reporting()))
        self.first.pop('reportingRequirements')
        self.first['reports'][0]['valueKind'] = 'actual'
        self.assertIn('REQUIREMENT_REPORT_MISMATCH', self.codes(*self.reporting()))

    def test_new_and_vanished_children_remain_coverage_gaps(self):
        self.require_reports()
        self.parent['reports'][0]['childCoverage'].pop()
        self.assertIn('REPORT_CHILD_MAPPING_MISSING', self.codes(*self.reporting()))
        self.catalogue['projects'].pop()
        self.assertIn('PROJECT_UNRESOLVED', self.codes(*self.reporting()))

    def test_exclusions_remain_visible_and_cannot_weaken_ancestors(self):
        requirement = self.require_reports(allowExclusions=True)
        report = self.parent['reports'][0]
        report['bindings'].pop()
        report['childCoverage'][1] = {'projectId': self.second['projectId'], 'exclusionReason': 'Separate reporting scope.'}
        context, checker = self.reporting()
        self.assertEqual(context.errors, [])
        self.assertFalse(checker.summary()['diagnostics'])
        self.assertIn('exclusionReason', report['childCoverage'][1])
        requirement['allowExclusions'] = False
        self.assertIn('REPORT_EXCLUSION_FORBIDDEN', self.codes(*self.reporting()))

    def test_source_age_uses_source_time_not_calculation_time(self):
        self.require_reports(maxSourceAgeSeconds=7200)
        self.first['outcomes'][0]['reportingSource'].pop('observedAt')
        context, checker = self.reporting()
        self.assertIn('REPORT_SOURCE_AGE_UNKNOWN', self.codes(context, checker))
        self.assertTrue(any(not f['known'] for f in checker.summary()['sourceFreshness']))
        self.first['outcomes'][0]['reportingSource']['observedAt'] = '2026-10-01T00:00:00Z'
        self.assertIn('REPORT_SOURCE_TOO_OLD', self.codes(*self.reporting()))

    def test_named_definitions_require_description_and_accept_metadata(self):
        requirement = self.require_reports()
        objects = {'ReportDefinition': self.parent['reports'][0], 'ReportingMetricDefinition': self.parent['reports'][0]['metric'],
                   'ReportBinding': self.parent['reports'][0]['bindings'][0], 'ReportingRequirement': requirement,
                   'ProjectCreationTemplate': self.template, 'ProjectCreationVariant': self.template['variants'][0],
                   'ProjectScopeSelector': self.template['selectors'][0], 'CreationReportingBinding': self.template['variants'][0]['reportingBindings'][0]}
        for name, original in objects.items():
            with self.subTest(name=name):
                element = deepcopy(original)
                element['tags'] = {'domainTags': ['Delivery']}
                element['assetNames'] = [{'assetName': 'Overview', 'type': 'diagram'}]
                self.definition(name).validate(element)
                element.pop('description')
                self.assertFalse(self.definition(name).is_valid(element))

    def test_metadata_references_and_suppression_are_checked(self):
        report = self.parent['reports'][0]
        report['assetNames'] = [{'assetName': 'Missing diagram', 'type': 'diagram'}]
        self.assertIn('ASSET_UNRESOLVED', self.codes(*self.reporting()))
        report['suppressed'] = True
        self.assertIn('ELEMENT_METADATA_INVALID', self.codes(*self.reporting()))
        report['narratives'] = [{'name': 'Context', 'description': 'Reporting context.', 'narrativeTypeName': 'Missing narrative', 'narrativeContexts': []}]
        self.assertIn('NARRATIVE_UNRESOLVED', self.codes(*self.reporting()))

    def test_preview_is_valid_and_never_mutates_sources(self):
        preview = self.preview()
        before = deepcopy(self.catalogue)
        self.definition('ProjectCreationPreview').validate(preview)
        context, checker = self.delegation(preview)
        self.assertEqual(context.errors, [], context.errors)
        self.assertEqual(self.catalogue, before)
        self.assertEqual(checker.results[0]['childProjectId'], preview['child']['projectId'])

    def test_stale_parent_and_methodology_revisions_reject_preview(self):
        preview = self.preview()
        self.catalogue['projects'][0]['revision'] = 'parent-r2'
        self.assertIn('DELEGATION_STALE_INPUT', self.codes(self.delegation(preview)[0]))
        self.catalogue['projects'][0]['revision'] = 'parent-r1'
        self.practice['description'] += ' Revised.'
        self.assertIn('DELEGATION_STALE_INPUT', self.codes(self.delegation(preview)[0]))

    def test_unmapped_assessment_stays_absent(self):
        preview = self.preview()
        preview['instanceMappings'][0]['assessmentTransfer'] = 'unassessed'
        preview['child']['current'] = {}
        context, _ = self.delegation(preview)
        self.assertEqual(context.errors, [], context.errors)
        preview['child']['current'] = deepcopy(self.parent['current'])
        preview['child']['current']['alphaInstances'][0]['name'] = 'Delivery'
        self.assertIn('DELEGATION_ASSESSMENT_INVENTED', self.codes(self.delegation(preview)[0]))

    def test_explicit_scope_and_confirmation_are_required(self):
        preview = self.preview()
        preview.pop('confirmedBy')
        preview.pop('confirmedAt')
        self.assertIn('DELEGATION_CONFIRMATION_REQUIRED', self.codes(self.delegation(preview)[0]))
        preview['selectedItems'].append({'projectId': self.first['projectId'], 'collection': 'outcomes', 'instanceName': 'Value'})
        self.assertIn('DELEGATION_SCOPE_INVALID', self.codes(self.delegation(preview)[0]))

    def test_template_conflicts_and_undeclared_selectors(self):
        conflicting = deepcopy(self.template)
        conflicting['rootTypeName'] = 'Opportunity'
        self.practice['projectCreationTemplates'].append(conflicting)
        context = self.context()
        validate_templates(context, self.practice, [self.practice, self.baseline])
        self.assertIn('TEMPLATE_CONFLICT', self.codes(context))
        self.template['variants'][0]['instanceMappings'][0]['selectorName'] = 'Undefined'
        validate_templates(context, self.practice, [self.practice, self.baseline])
        self.assertIn('TEMPLATE_SELECTOR_UNRESOLVED', self.codes(context))

    def test_committed_operation_retries_return_existing_child(self):
        preview = self.preview()
        self.parent['reports'][0]['bindings'].append(deepcopy(preview['reportingBindings'][0]['parentBinding']))
        operation = {'preview': deepcopy(preview), 'status': 'committed', 'committedAt': '2026-10-26T09:45:00Z',
                     'summaryReportName': 'Targets', 'history': deepcopy(preview['sourceSnapshots'])}
        self.parent['delegations'] = [operation]
        self.parent['current'] = {}
        self.catalogue['projects'].append({'revision': 'new-child-r1', 'document': deepcopy(preview['child'])})
        context, checker = self.delegation(preview)
        self.assertEqual(context.errors, [], context.errors)
        self.assertTrue(all(r['existing'] for r in checker.results))
        changed = deepcopy(preview)
        changed['child']['projectId'] = '11111111-1111-4111-8111-111111111111'
        self.assertIn('DELEGATION_OPERATION_CONFLICT', self.codes(self.delegation(changed)[0]))

    def test_failed_creation_retains_parent_and_no_second_owner(self):
        preview = self.preview()
        self.parent['delegations'] = [{'preview': preview, 'status': 'failed', 'error': 'Staging failed.', 'history': []}]
        context = self.context()
        DelegationValidator(context).validate()
        self.assertEqual(context.errors, [], context.errors)
        self.assertEqual(self.parent['current']['alphaInstances'][0]['stateName'], 'Validated')
        self.catalogue['projects'].append({'revision': 'bad-stage', 'document': preview['child']})
        context = self.context()
        DelegationValidator(context).validate()
        self.assertIn('DELEGATION_SECOND_OWNER', self.codes(context))

    def test_local_recommendation_reuses_workflow_without_signal(self):
        preview = self.preview()
        card = {'name': 'Delegate Expansion', 'status': 'accepted', 'decidedBy': 'Example owner', 'decidedAt': '2026-10-26T09:30:00Z',
                'localRecommendation': {'source': preview['source'], 'createdAt': '2026-10-26T09:00:00Z',
                                        'rationale': 'The work has an independent delivery scope.', 'advice': 'Confirm scope and method.', 'proposal': preview}}
        self.parent['recommendations'] = [card]
        checker = SignalValidator(self.schema, [self.parent, *self.documents], True)
        checker.validate_project(self.parent)
        self.assertEqual(checker.errors, [], checker.errors)
        context = self.context(True)
        DelegationValidator(context).validate()
        self.assertEqual(context.errors, [], context.errors)
        card['status'] = 'applied'
        checker = SignalValidator(self.schema, [self.parent], True)
        checker.validate_project(self.parent)
        self.assertTrue(checker.errors)

    def test_automatic_creation_is_scoped_to_template_version_and_source(self):
        preview = self.preview()
        preview.pop('confirmedAt')
        preview.pop('confirmedBy')
        preview['policyName'] = 'Explicit delegation policy'
        self.assertIn('DELEGATION_AUTHORITY_MISSING', self.codes(self.delegation(preview)[0]))
        self.parent['recommendationPolicies'] = [{'name': preview['policyName'], 'template': preview['template'], 'source': preview['source']}]
        self.assertEqual(self.delegation(preview)[0].errors, [])
        self.parent['recommendationPolicies'][0]['revokedAt'] = '2026-10-26T09:00:00Z'
        self.assertIn('DELEGATION_AUTHORITY_REVOKED', self.codes(self.delegation(preview)[0]))

    def test_cli_uuid_parity_and_reporting_gaps_have_distinct_exit_status(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'project.json'
            catalogue = Path(folder) / 'catalogue.json'
            path.write_text(json.dumps(self.parent))
            catalogue.write_text(json.dumps(self.catalogue))
            node = subprocess.run(['node', str(ROOT / 'validate/validate-schema.js'), str(path)], capture_output=True, text=True)
            self.assertEqual(node.returncode, 0, node.stderr + node.stdout)
            self.require_reports()
            self.first.pop('reportingRequirementBindings')
            path.write_text(json.dumps(self.parent))
            catalogue.write_text(json.dumps(self.catalogue))
            command = [sys.executable, str(ROOT / 'validate/validate-project.py'), str(path), str(SCHEMA), '--catalogue', str(catalogue), '--quiet']
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertFalse(json.loads(result.stdout)['reporting']['alignmentComplete'])
            self.parent.pop('projectId')
            path.write_text(json.dumps(self.parent))
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertNotEqual(subprocess.run(['node', str(ROOT / 'validate/validate-schema.js'), str(path)], capture_output=True).returncode, 0)

    def test_malformed_catalogues_and_contexts_report_errors_without_crashing(self):
        for snapshot in ({'projects': [{'document': self.parent}]}, [], {'projects': 'invalid'}):
            context = ProjectCatalogue(self.schema, snapshot)
            context.validate()
            ReportingValidator(context).validate()
            DelegationValidator(context).validate()
            self.assertIn('SCHEMA_INVALID', self.codes(context))
        context = ProjectCatalogue(self.schema, documents=[[]])
        self.assertIn('SCHEMA_INVALID', self.codes(context))

    def test_gap_diagnostics_retain_requirement_and_source_provenance(self):
        self.require_reports()
        self.first.pop('reportingRequirementBindings')
        context, checker = self.reporting()
        result = self.result()
        result['complete'] = False
        result.pop('total')
        result['diagnostics'] = deepcopy(checker.gaps[(project_key(self.parent['projectId']), 'Targets')])
        context, checker = self.reporting([result])
        self.assertEqual(context.errors, [], context.errors)
        result['diagnostics'][0]['projectId'] = self.first['projectId']
        self.assertIn('REPORT_DIAGNOSTICS_MISSING', self.codes(*self.reporting([result])))

    def test_source_weight_is_applied_once_and_conflicts_are_reported(self):
        outcome = self.practice['outcomes'][0]
        outcome['metricContributions'] = [{'alphaName': 'Initiative', 'metricName': 'value', 'recognizedAtStateName': 'Addressed',
                                           'forecastWeights': [{'stateName': 'Validated', 'weight': 0.5}, {'stateName': 'Addressed', 'weight': 1}]}]
        report = self.parent['reports'][0]
        report['valueKind'] = 'forecast'
        report.pop('childCoverage')
        report['bindings'] = [{'name': 'Derived', 'description': 'Source-weighted forecast.', 'sourceKind': 'outcome', 'valueSource': 'derived',
                               'source': {'projectId': self.parent['projectId'], 'collection': 'outcomes', 'instanceName': 'Value'}}]
        source = self.parent['current']['alphaInstances'][0]
        source['evidenceBy'] = [{'name': 'Evidence', 'description': 'Canonical value record.', 'workProductName': 'Ledger', 'levelOfDetailName': 'Published'}]
        metric = {'name': 'value', 'value': 100, 'unit': 'GBP', 'reportingSource': deepcopy(self.first['outcomes'][0]['reportingSource'])}
        metric['reportingSource']['identity']['key'] = 'parent-metric'
        self.parent['current']['workProductInstances'] = [{**deepcopy(source['evidenceBy'][0]), 'metrics': [metric]}]
        context, checker = self.reporting()
        self.assertEqual(context.errors, [], context.errors)
        facts = checker.facts[(project_key(self.parent['projectId']), 'Targets')]
        self.assertEqual([(f['rawValue'], f['weight'], f['value']) for f in facts], [(100, 0.5, 50)])
        grandparent = deepcopy(self.first)
        grandparent['projectId'] = 'ce536019-333a-4cb2-9510-f94e1b96f1aa'
        grandparent.pop('parentProject')
        grandparent['reports'] = [{**deepcopy(report), 'bindings': [
            {'name': 'Portfolio', 'description': 'Forward source weighting unchanged.', 'sourceKind': 'report',
             'source': {'projectId': self.parent['projectId'], 'reportName': 'Targets'}}]}]
        self.parent['parentProject'] = {'projectId': grandparent['projectId']}
        self.catalogue['projects'].append({'document': grandparent, 'revision': 'grandparent-r1'})
        context, checker = self.reporting()
        self.assertEqual(checker.facts[(project_key(grandparent['projectId']), 'Targets')][0]['value'], 50)
        other = deepcopy(source)
        other['name'], other['stateName'] = 'Another assessment', 'Addressed'
        self.parent['current']['alphaInstances'].append(other)
        self.assertIn('REPORT_LINEAGE_CONFLICT', self.codes(*self.reporting()))

    def test_attainment_requires_own_method_target_and_evidence(self):
        report = self.parent['reports'][0]
        report.update(aggregation='attainmentCount', unit='count')
        report.pop('valueKind')
        report.pop('childCoverage')
        report['metric'].update(metricId='example:attained', description='Evidenced attainment of the local target.')
        report['bindings'] = [{'name': 'Acceptance', 'description': 'Parent-owned acceptance.', 'sourceKind': 'assessment',
                               'source': {'projectId': self.parent['projectId'], 'collection': 'current.alphaInstances', 'instanceName': 'Expansion'},
                               'target': {'projectId': self.parent['projectId'], 'collection': 'target.alphaInstances', 'instanceName': 'Expansion'}}]
        self.practice['alphas'][0]['states'][-1]['checklist'] = [{'name': 'Approval', 'description': 'Approval is evidenced.', 'seq': 1}]
        current = self.parent['current']['alphaInstances'][0]
        current.update(stateName='Addressed', checklistStates=[{'checklistName': 'Approval', 'state': 'complete',
                                                             'evidence': {'name': 'Approval record', 'uri': 'https://example.org/approval'}}])
        original = deepcopy(self.parent['current'])
        context, checker = self.reporting()
        self.assertEqual(context.errors, [], context.errors)
        self.assertTrue(checker.facts[(project_key(self.parent['projectId']), 'Targets')][0]['attained'])
        self.assertEqual(self.parent['current'], original)
        current['checklistStates'][0].pop('evidence')
        self.assertFalse(self.reporting()[1].facts[(project_key(self.parent['projectId']), 'Targets')][0]['attained'])
        current['stateName'] = 'A state from another method'
        self.assertIn('REPORT_ASSESSMENT_UNRESOLVED', self.codes(*self.reporting()))

    def test_cross_method_mapping_preserves_evidence_and_rejects_missing_checklist_maps(self):
        self.practice['alphas'][0]['states'][1]['checklist'] = [{'name': 'Approval', 'description': 'Approved.', 'seq': 1}]
        self.parent['current']['alphaInstances'][0]['checklistStates'] = [{'checklistName': 'Approval', 'state': 'complete',
                                                                        'evidence': {'name': 'Approval', 'uri': 'https://example.org/approval'}}]
        alternate = self.documents[1]
        alternate['alphas'][0]['states'][1].update(name='Ready', checklist=[{'name': 'Verified', 'description': 'Verified.', 'seq': 1}])
        variant = self.template['variants'][0]
        variant['methodology']['documentName'] = alternate['name']
        rule = variant['instanceMappings'][0]
        rule.update(stateMappings=[{'fromState': 'Validated', 'toState': 'Ready'}],
                    checklistMappings=[{'fromStateOrLevel': 'Validated', 'fromChecklist': 'Approval', 'toStateOrLevel': 'Ready', 'toChecklist': 'Verified'}])
        preview = self.preview()
        preview['child']['practiceName'] = alternate['name']
        target = preview['child']['current']['alphaInstances'][0]
        target['stateName'], target['checklistStates'][0]['checklistName'] = 'Ready', 'Verified'
        transfer = preview['instanceMappings'][0]
        transfer.update(assessmentTransfer='mapped', stateMappings=deepcopy(rule['stateMappings']), checklistMappings=deepcopy(rule['checklistMappings']))
        preview['sourceRevisions'].append({'methodology': {'documentType': 'practice', 'documentName': alternate['name'], 'version': '1.0.0'}, 'revision': document_revision(alternate)})
        context, _ = self.delegation(preview)
        self.assertEqual(context.errors, [], context.errors)
        self.assertEqual(target['checklistStates'][0]['evidence'], self.parent['current']['alphaInstances'][0]['checklistStates'][0]['evidence'])
        rule['checklistMappings'] = []
        transfer['checklistMappings'] = []
        preview['sourceRevisions'][1]['revision'] = document_revision(self.practice)
        self.assertIn('DELEGATION_CHECKLIST_MAPPING_AMBIGUOUS', self.codes(self.delegation(preview)[0]))

    def test_action_transfer_checks_open_status_assignments_and_cycle_destination(self):
        self.parent['actions'] = [{'name': 'Prepare', 'status': 'in-progress', 'assignedTo': ['Owner'], 'advancesAlphaInstances': ['Expansion'], 'outcomeInstanceNames': ['Value']}]
        self.template['selectors'].append({'name': 'Open action', 'description': 'Explicitly selected follow-up.', 'selection': 'named', 'items': [{'collection': 'actions', 'instanceName': 'Prepare'}]})
        rule = {'selectorName': 'Open action', 'targetCycleName': 'Iteration 1', 'assigneeMappings': [{'from': 'Owner', 'to': 'Delegate'}]}
        self.template['variants'][0]['actionMappings'] = [rule]
        preview = self.preview()
        source = {'projectId': self.parent['projectId'], 'collection': 'actions', 'instanceName': 'Prepare'}
        target = {'projectId': preview['child']['projectId'], 'collection': 'cycles.actions', 'cycleName': 'Iteration 1', 'instanceName': 'Prepare'}
        preview['selectedItems'].append(source)
        preview['actionMappings'] = [{'source': source, 'target': target, 'assigneeMappings': deepcopy(rule['assigneeMappings'])}]
        preview['sourceSnapshots'].append({'source': source, 'recordedAt': '2026-10-26T09:00:00Z', 'attributedTo': 'Owner', 'snapshot': deepcopy(self.parent['actions'][0])})
        preview['child']['team'] = {'name': 'Delivery team', 'description': 'Owners of the delivery.', 'members': [{'name': 'Delegate', 'personaName': 'Lead', 'contact': 'example'}]}
        preview['child']['cycles'] = [{'name': 'Iteration 1', 'description': 'Delivery interval.', 'actions': [{**deepcopy(self.parent['actions'][0]), 'assignedTo': ['Delegate'], 'advancesAlphaInstances': ['Delivery']}]}]
        context, _ = self.delegation(preview)
        self.assertEqual(context.errors, [], context.errors)
        target['cycleName'] = 'Missing iteration'
        self.assertIn('INSTANCE_UNRESOLVED', self.codes(self.delegation(preview)[0]))
        target['cycleName'] = 'Iteration 1'
        preview['child']['team']['members'] = []
        self.assertIn('DELEGATION_ASSIGNMENT_UNRESOLVED', self.codes(self.delegation(preview)[0]))
        self.parent['actions'][0]['status'] = 'done'
        self.assertIn('DELEGATION_ACTION_CLOSED', self.codes(self.delegation(preview)[0]))

    def test_templates_are_checked_through_practice_validator(self):
        validator = PracticeValidator(FIXTURES / 'fixture-signal-practice.json', FIXTURES / 'fixture-baseline.json', SCHEMA)
        validator.practice = self.practice
        self.assertTrue(validator.validate_project_creation_templates(), validator.errors)
        self.template['defaultVariantName'] = 'Unknown method'
        self.assertFalse(validator.validate_project_creation_templates())
        self.assertIn('TEMPLATE_VARIANT_UNRESOLVED', {e['code'] for e in validator.errors})

    def test_requirement_suppression_is_a_gap_and_does_not_remove_obligations(self):
        requirement = self.require_reports()
        weaker = deepcopy(requirement)
        weaker['suppressed'] = True
        self.first['reportingRequirements'] = [weaker]
        context, checker = self.reporting()
        self.assertEqual(context.errors, [], context.errors)
        self.assertIn('REQUIREMENT_CONFLICT', self.codes(context, checker))

    def test_extra_child_assessments_and_actions_are_not_invented(self):
        preview = self.preview()
        preview['child']['current']['alphaInstances'].append({**deepcopy(preview['child']['current']['alphaInstances'][0]), 'name': 'Unselected'})
        preview['child']['actions'] = [{'name': 'Unselected action'}]
        context, _ = self.delegation(preview)
        self.assertIn('DELEGATION_ASSESSMENT_INVENTED', self.codes(context))
        self.assertIn('DELEGATION_ACTION_UNDECLARED', self.codes(context))

    def test_delegated_identity_survives_new_assessment_location(self):
        preview = self.preview()
        operation = {'preview': preview, 'status': 'committed', 'history': preview['sourceSnapshots'],
                     'committedAt': '2026-10-26T09:45:00Z', 'summaryReportName': 'Targets'}
        self.parent['delegations'] = [operation]
        self.parent['current'] = {}
        self.catalogue['projects'].append({'document': preview['child'], 'revision': 'child-r1'})
        context = self.context()
        reference = {**preview['instanceMappings'][0]['target'], 'collection': 'current.alphaInstances'}
        self.assertEqual(context.delegated_origin(reference), (preview['instanceMappings'][0]['origin'], preview['instanceMappings'][0]['originalSource']))
        self.assertIsNone(context.delegated_origin({**reference, 'collection': 'outcomes'}))

    def test_package_inventory_uuid_matches_document_and_rejects_duplicates(self):
        entry = {'path': 'documents/project.json', 'documentType': 'project', 'documentName': self.parent['name'], 'projectId': self.parent['projectId']}
        manifest = {'schemaVersion': '4.0.0', 'package': {'name': 'example', 'description': 'Synthetic project snapshot.', 'version': '1.0.0'}, 'documents': [entry]}
        context = self.context()
        self.assertTrue(context.validate_project_inventory(manifest, {entry['path']: self.parent}), context.errors)
        entry['projectId'] = self.first['projectId']
        self.assertFalse(context.validate_project_inventory(manifest, {entry['path']: self.parent}))
        self.assertIn('PACKAGE_PROJECT_IDENTITY_MISMATCH', self.codes(context))
        entry['projectId'] = self.parent['projectId']
        manifest['documents'].append({**entry, 'path': 'documents/duplicate.json'})
        context = self.context()
        context.validate_project_inventory(manifest, {entry['path']: self.parent, 'documents/duplicate.json': self.parent})
        self.assertIn('DUPLICATE_PROJECT_ID', self.codes(context))

    def test_metric_conflicts_affect_both_declarations_and_paths_are_checked(self):
        self.first['reports'][0]['metric']['description'] = 'A different semantic definition.'
        context, checker = self.reporting()
        for project in (self.parent, self.first):
            self.assertTrue(any(d['code'] == 'REPORT_METRIC_DEFINITION_CONFLICT' for d in checker.gaps[(project_key(project['projectId']), 'Targets')]))
        self.first['reports'][0]['metric']['description'] = self.parent['reports'][0]['metric']['description']
        result = self.result()
        result['contributions'][0]['via'] = [{'projectId': self.first['projectId'], 'reportName': 'Targets'}]
        self.assertEqual(self.reporting([result])[0].errors, [])
        result['contributions'][0]['via'][0]['reportName'] = 'Unrelated report'
        self.assertIn('REPORT_LINEAGE_PATH_INVALID', self.codes(*self.reporting([result])))


if __name__ == '__main__':
    unittest.main()

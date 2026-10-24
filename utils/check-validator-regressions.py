#!/usr/bin/env python3
"""Run focused regression checks for composition diagnostics and documented examples."""

import importlib.util
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'validate'))
from _venv_bootstrap import ensure_dependencies

ensure_dependencies()
from jsonschema import Draft202012Validator
from signal_validation import SignalValidator


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


if __name__ == '__main__':
    unittest.main()

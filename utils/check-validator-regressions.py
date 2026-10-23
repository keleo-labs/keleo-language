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


def load_validator(filename, classname):
    spec = importlib.util.spec_from_file_location(classname, ROOT / 'validate' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, classname)


BaselineValidator = load_validator('validate-baseline.py', 'BaselineValidator')
PracticeValidator = load_validator('validate-practice.py', 'PracticeValidator')
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


if __name__ == '__main__':
    unittest.main()

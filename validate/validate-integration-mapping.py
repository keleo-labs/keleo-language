#!/usr/bin/env python3
"""
IntegrationMapping Language JSON Validator

Validates IntegrationMapping JSON files against:
1. JSON Schema (language.schema.json)
2. Internal cross-reference integrity (unique names, consistent targets)
3. Optional practice/method element resolution (when a practice file is provided)

Usage:
  python3 validate-integration-mapping.py <mapping.json> <schema.json> [practice.json]

Outputs structured JSON report for skill consumption.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import jsonschema
    from jsonschema import Draft202012Validator, RefResolver
except ImportError:
    print("ERROR: jsonschema library not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(2)


class IntegrationMappingValidator:
    """Validates IntegrationMapping JSON against schema and internal integrity"""

    TARGET_KINDS = {"alpha", "workProduct", "outcome", "action"}
    TIERS = {"direct", "pattern", "llm-assisted"}
    SERVICE_KINDS = {"crm", "project-management", "document-store", "data-warehouse", "api", "file"}

    def __init__(self, mapping_file: Path, schema_file: Path,
                 practice_file: Optional[Path] = None):
        self.mapping_file = mapping_file
        self.schema_file = schema_file
        self.practice_file = practice_file
        self.errors = []
        self.warnings = []

        self.mapping = self._load_json(mapping_file)
        self.schema = self._load_json(schema_file)
        self.practice = self._load_json(practice_file) if practice_file else None

        if self.practice:
            self._index_practice()

    def _load_json(self, file_path: Path) -> Dict:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in {file_path}: {e}", file=sys.stderr)
            sys.exit(1)

    def _index_practice(self):
        self.practice_alphas = set()
        self.practice_alpha_states = {}
        self.practice_work_products = set()
        self.practice_outcomes = set()

        for alpha in self.practice.get('alphas', []):
            name = alpha.get('name', '')
            self.practice_alphas.add(name)
            self.practice_alpha_states[name] = {
                s.get('name', '') for s in alpha.get('states', [])
            }

        for wp in self.practice.get('workProducts', []):
            self.practice_work_products.add(wp.get('name', ''))

        for outcome in self.practice.get('outcomes', []):
            self.practice_outcomes.add(outcome.get('name', ''))

    def validate_schema(self) -> bool:
        try:
            schema_dir = self.schema_file.parent
            resolver = RefResolver(
                base_uri=f"file://{schema_dir}/",
                referrer=self.schema
            )
            validator = Draft202012Validator(self.schema, resolver=resolver)
            schema_errors = list(validator.iter_errors(self.mapping))

            for error in schema_errors:
                path = "root"
                if error.absolute_path:
                    path = ".".join([str(p) for p in error.absolute_path])
                self.errors.append({
                    "category": "schema",
                    "severity": "error",
                    "path": path,
                    "issue": error.message,
                    "expected": error.validator_value if hasattr(error, 'validator_value') else None,
                    "actual": error.instance if len(str(error.instance)) < 100 else str(error.instance)[:100] + "...",
                    "suggestion": "Review schema definition and adjust JSON structure"
                })
            return len(schema_errors) == 0
        except Exception as e:
            self.errors.append({
                "category": "schema",
                "severity": "error",
                "path": "root",
                "issue": f"Schema validation failed: {str(e)}",
                "expected": None,
                "actual": None,
                "suggestion": "Check schema file and integration mapping JSON structure"
            })
            return False

    def validate_unique_entity_mapping_names(self) -> bool:
        has_errors = False
        seen = set()
        for idx, em in enumerate(self.mapping.get('entityMappings', [])):
            name = em.get('name', '')
            if name in seen:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"entityMappings[{idx}].name",
                    "issue": f"Duplicate EntityMapping name: '{name}'",
                    "expected": "Unique entity mapping names within the document",
                    "actual": name,
                    "suggestion": "Rename this entity mapping to be unique"
                })
                has_errors = True
            seen.add(name)
        return not has_errors

    def validate_unique_field_mapping_names(self) -> bool:
        has_errors = False
        for em_idx, em in enumerate(self.mapping.get('entityMappings', [])):
            seen = set()
            for fm_idx, fm in enumerate(em.get('fieldMappings', [])):
                name = fm.get('name', '')
                if name in seen:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": f"entityMappings[{em_idx}].fieldMappings[{fm_idx}].name",
                        "issue": f"Duplicate FieldMapping name: '{name}' within EntityMapping '{em.get('name', '')}'",
                        "expected": "Unique field mapping names within each entity mapping",
                        "actual": name,
                        "suggestion": "Rename this field mapping to be unique within its entity mapping"
                    })
                    has_errors = True
                seen.add(name)
        return not has_errors

    def validate_unique_query_template_names(self) -> bool:
        has_errors = False
        seen = set()
        for idx, qt in enumerate(self.mapping.get('queryTemplates', [])):
            name = qt.get('name', '')
            if name in seen:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"queryTemplates[{idx}].name",
                    "issue": f"Duplicate QueryTemplate name: '{name}'",
                    "expected": "Unique query template names within the document",
                    "actual": name,
                    "suggestion": "Rename this query template to be unique"
                })
                has_errors = True
            seen.add(name)
        return not has_errors

    def validate_element_references(self) -> bool:
        if not self.practice:
            practice_name = self.mapping.get('practiceName') or self.mapping.get('methodName')
            if practice_name:
                self.warnings.append({
                    "category": "integrity",
                    "severity": "warning",
                    "path": "practiceName" if 'practiceName' in self.mapping else "methodName",
                    "issue": f"References '{practice_name}' but no practice file provided — element name resolution skipped",
                    "expected": "Provide practice file as third argument for full validation",
                    "actual": practice_name,
                    "suggestion": f"Run: python3 validate-integration-mapping.py <mapping> <schema> <practice.json>"
                })
            return True

        has_errors = False
        for em_idx, em in enumerate(self.mapping.get('entityMappings', [])):
            for t_idx, target in enumerate(em.get('targets', [])):
                kind = target.get('targetKind', '')
                element_name = target.get('elementName', '')
                path = f"entityMappings[{em_idx}].targets[{t_idx}].elementName"

                if kind == 'alpha' and element_name not in self.practice_alphas:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": path,
                        "issue": f"Alpha '{element_name}' not found in practice",
                        "expected": f"One of: {sorted(self.practice_alphas)}" if self.practice_alphas else "Define alphas in the practice",
                        "actual": element_name,
                        "suggestion": "Check the alpha name matches a declared Alpha in the referenced practice"
                    })
                    has_errors = True

                elif kind == 'workProduct' and element_name not in self.practice_work_products:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": path,
                        "issue": f"WorkProduct '{element_name}' not found in practice",
                        "expected": f"One of: {sorted(self.practice_work_products)}" if self.practice_work_products else "Define work products in the practice",
                        "actual": element_name,
                        "suggestion": "Check the work product name matches a declared WorkProduct in the referenced practice"
                    })
                    has_errors = True

                elif kind == 'outcome' and element_name not in self.practice_outcomes:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": path,
                        "issue": f"Outcome '{element_name}' not found in practice",
                        "expected": f"One of: {sorted(self.practice_outcomes)}" if self.practice_outcomes else "Define outcomes in the practice",
                        "actual": element_name,
                        "suggestion": "Check the outcome name matches a declared Outcome in the referenced practice"
                    })
                    has_errors = True

            for fm_idx, fm in enumerate(em.get('fieldMappings', [])):
                target = fm.get('target', {})
                if target.get('property') == 'stateName' and fm.get('valueMap'):
                    for vm_idx, vm in enumerate(fm['valueMap']):
                        to_value = vm.get('to', '')
                        for t in em.get('targets', []):
                            if t.get('targetKind') == 'alpha':
                                alpha_name = t.get('elementName', '')
                                states = self.practice_alpha_states.get(alpha_name, set())
                                if states and to_value not in states:
                                    self.warnings.append({
                                        "category": "integrity",
                                        "severity": "warning",
                                        "path": f"entityMappings[{em_idx}].fieldMappings[{fm_idx}].valueMap[{vm_idx}].to",
                                        "issue": f"State name '{to_value}' not found in alpha '{alpha_name}'",
                                        "expected": f"One of: {sorted(states)}",
                                        "actual": to_value,
                                        "suggestion": "Check state name matches a declared State in the target alpha"
                                    })

        return not has_errors

    def validate_schema_version(self) -> bool:
        doc_version = self.mapping.get('schemaVersion')
        if not doc_version:
            return True

        schema_comment = self.schema.get('$comment', '')
        if schema_comment.startswith('schemaVersion:'):
            schema_version = schema_comment.split(':')[1]
            doc_major = doc_version.split('.')[0]
            schema_major = schema_version.split('.')[0]
            if doc_major != schema_major:
                self.errors.append({
                    "category": "compatibility",
                    "severity": "error",
                    "path": "schemaVersion",
                    "issue": f"Major version mismatch: document targets {doc_version}, schema is {schema_version}",
                    "expected": f"Major version {schema_major}.x.x",
                    "actual": doc_version,
                    "suggestion": "Update the document to target the current schema major version"
                })
                return False
        return True

    def generate_report(self) -> Dict:
        return {
            "valid": len(self.errors) == 0,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "file": str(self.mapping_file),
            "document_name": self.mapping.get('name', 'unknown'),
            "service_kind": self.mapping.get('serviceKind', 'unknown'),
            "entity_mapping_count": len(self.mapping.get('entityMappings', [])),
            "errors": self.errors,
            "warnings": self.warnings
        }


def main():
    import argparse as _argparse

    parser = _argparse.ArgumentParser(
        description="Validate IntegrationMapping JSON against schema and integrity rules"
    )
    parser.add_argument("mapping", help="IntegrationMapping JSON file")
    parser.add_argument("schema", help="Language schema JSON file")
    parser.add_argument("practice", nargs="?", default=None,
                        help="Optional practice/method JSON file for element name resolution")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress progress messages to stderr")
    parser.add_argument("--brief", action="store_true",
                        help="Print one-line summary instead of full JSON report")
    args = parser.parse_args()

    mapping_file = Path(args.mapping)
    schema_file = Path(args.schema)
    practice_file = Path(args.practice) if args.practice else None

    def progress(msg):
        if not args.quiet:
            print(msg, file=sys.stderr)

    validator = IntegrationMappingValidator(mapping_file, schema_file, practice_file)

    progress("Validating schema...")
    validator.validate_schema()

    progress("Validating unique entity mapping names...")
    validator.validate_unique_entity_mapping_names()

    progress("Validating unique field mapping names...")
    validator.validate_unique_field_mapping_names()

    progress("Validating unique query template names...")
    validator.validate_unique_query_template_names()

    progress("Validating element references...")
    validator.validate_element_references()

    progress("Validating schema version...")
    validator.validate_schema_version()

    report = validator.generate_report()

    if args.brief:
        status = "PASS" if report["valid"] else "FAIL"
        errs = report.get("error_count", 0)
        warns = report.get("warning_count", 0)
        warn_str = f" ({warns} warnings)" if warns else ""
        print(f"{status} {errs} errors{warn_str} — {mapping_file.name}")
    else:
        print(json.dumps(report, indent=2))

    sys.exit(0 if report['valid'] else 1)


if __name__ == '__main__':
    main()

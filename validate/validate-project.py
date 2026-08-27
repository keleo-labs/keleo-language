#!/usr/bin/env python3
"""
Project Language JSON Validator

Validates Project JSON files against:
1. JSON Schema (language.schema.json)
2. Internal cross-reference integrity (cycle names, pattern view refs, instance consistency)

Outputs structured JSON report for skill consumption.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

try:
    import jsonschema
    from jsonschema import Draft202012Validator, RefResolver
except ImportError:
    print("ERROR: jsonschema library not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(2)


class ProjectValidator:
    """Validates Project JSON against schema and internal cross-reference integrity"""

    def __init__(self, project_file: Path, schema_file: Path):
        self.project_file = project_file
        self.schema_file = schema_file
        self.errors = []
        self.warnings = []

        self.project = self._load_json(project_file)
        self.schema = self._load_json(schema_file)

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

    def validate_schema(self) -> bool:
        try:
            schema_dir = self.schema_file.parent
            resolver = RefResolver(
                base_uri=f"file://{schema_dir}/",
                referrer=self.schema
            )
            validator = Draft202012Validator(self.schema, resolver=resolver)
            schema_errors = list(validator.iter_errors(self.project))

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
                "suggestion": "Check schema file and project JSON structure"
            })
            return False

    def validate_practice_reference(self) -> bool:
        has_practice = 'practiceName' in self.project
        has_method = 'methodName' in self.project

        if not has_practice and not has_method:
            self.errors.append({
                "category": "integrity",
                "severity": "error",
                "path": "root",
                "issue": "Project must declare exactly one of practiceName or methodName",
                "expected": "practiceName XOR methodName",
                "actual": "Neither present",
                "suggestion": "Add practiceName or methodName to identify the practice/method this project is based on"
            })
            return False

        if has_practice and has_method:
            self.errors.append({
                "category": "integrity",
                "severity": "error",
                "path": "root",
                "issue": "Project has both practiceName and methodName (mutually exclusive)",
                "expected": "Exactly one of practiceName or methodName",
                "actual": f"practiceName: '{self.project['practiceName']}', methodName: '{self.project['methodName']}'",
                "suggestion": "Remove one — a project is based on a single practice or method"
            })
            return False

        return True

    def validate_cycles(self) -> bool:
        has_errors = False
        cycles = self.project.get('cycles', [])
        current_cycle_name = self.project.get('currentCycleName')

        cycle_names = set()
        for idx, cycle in enumerate(cycles):
            cycle_name = cycle.get('name', '')
            path = f"cycles[{idx}]"

            if cycle_name in cycle_names:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"{path}.name",
                    "issue": f"Duplicate cycle name: '{cycle_name}'",
                    "expected": "Unique cycle names within the project",
                    "actual": cycle_name,
                    "suggestion": "Rename this cycle to be unique"
                })
                has_errors = True
            cycle_names.add(cycle_name)

        if current_cycle_name and current_cycle_name not in cycle_names:
            self.errors.append({
                "category": "integrity",
                "severity": "error",
                "path": "currentCycleName",
                "issue": f"currentCycleName '{current_cycle_name}' does not match any cycle",
                "expected": f"One of: {sorted(cycle_names)}" if cycle_names else "Define a cycle first",
                "actual": current_cycle_name,
                "suggestion": "Set currentCycleName to match an existing cycle name"
            })
            has_errors = True

        return not has_errors

    def validate_pattern_view_references(self) -> bool:
        has_errors = False
        plan = self.project.get('plan', {})
        pattern = plan.get('pattern', {})
        pattern_views = pattern.get('patternViews', [])

        view_names = set()
        for view in pattern_views:
            view_names.add(view.get('name', ''))

        for idx, cycle in enumerate(self.project.get('cycles', [])):
            pv_name = cycle.get('patternViewName')
            if pv_name and pv_name not in view_names:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"cycles[{idx}].patternViewName",
                    "issue": f"patternViewName '{pv_name}' does not match any pattern view in the plan",
                    "expected": f"One of: {sorted(view_names)}" if view_names else "Define pattern views in plan.pattern first",
                    "actual": pv_name,
                    "suggestion": "Use a pattern view name from plan.pattern.patternViews"
                })
                has_errors = True

        return not has_errors

    def validate_instance_consistency(self) -> bool:
        """Check that instance names used in current/target/cycles are consistent"""
        has_errors = False

        all_alpha_instances = set()
        all_wp_instances = set()

        for section_name in ('current', 'target'):
            section = self.project.get(section_name, {})
            for inst in section.get('alphaInstances', []):
                name = inst.get('name') or inst.get('instanceName')
                if name:
                    all_alpha_instances.add(name)
            for inst in section.get('workProductInstances', []):
                name = inst.get('name') or inst.get('instanceName')
                if name:
                    all_wp_instances.add(name)

        for idx, cycle in enumerate(self.project.get('cycles', [])):
            for inst in cycle.get('alphaInstances', []):
                name = inst.get('name') or inst.get('instanceName')
                if name:
                    all_alpha_instances.add(name)
            for inst in cycle.get('workProductInstances', []):
                name = inst.get('name') or inst.get('instanceName')
                if name:
                    all_wp_instances.add(name)

        current = self.project.get('current', {})
        target = self.project.get('target', {})

        current_alpha_names = {(inst.get('name') or inst.get('instanceName')) for inst in current.get('alphaInstances', [])}
        target_alpha_names = {(inst.get('name') or inst.get('instanceName')) for inst in target.get('alphaInstances', [])}

        target_only = target_alpha_names - current_alpha_names
        for name in sorted(target_only):
            if name:
                self.warnings.append({
                    "category": "integrity",
                    "severity": "warning",
                    "path": "target.alphaInstances",
                    "issue": f"Alpha instance '{name}' in target but not in current — no baseline for progress tracking",
                    "expected": "Instances tracked in both current and target",
                    "actual": name,
                    "suggestion": "Add a corresponding entry in current to establish the baseline state"
                })

        return not has_errors

    def validate_schema_version(self) -> bool:
        schema_comment = self.schema.get('$comment', '')
        if schema_comment.startswith('schemaVersion:'):
            schema_version = schema_comment.split(':')[1]
        else:
            return True

        doc_version = self.project.get('schemaVersion')
        if not doc_version:
            self.warnings.append({
                "category": "schema",
                "severity": "warning",
                "path": "schemaVersion",
                "issue": "Project does not declare a schemaVersion",
                "expected": f"schemaVersion: '{schema_version}'",
                "actual": "Missing",
                "suggestion": f"Add schemaVersion: '{schema_version}' for compatibility checking"
            })
            return True

        doc_major = int(doc_version.split('.')[0])
        schema_major = int(schema_version.split('.')[0])
        if doc_major != schema_major:
            self.errors.append({
                "category": "schema",
                "severity": "error",
                "path": "schemaVersion",
                "issue": f"Major version mismatch: document v{doc_version} vs schema v{schema_version}",
                "expected": f"Major version {schema_major}",
                "actual": f"Major version {doc_major}",
                "suggestion": f"Update document to schema version {schema_version} or use a compatible schema"
            })
            return False

        return True

    def generate_report(self) -> Dict:
        return {
            "project_file": str(self.project_file),
            "schema_file": str(self.schema_file),
            "valid": len(self.errors) == 0,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "schema": sum(1 for e in self.errors if e['category'] == 'schema'),
                "integrity": sum(1 for e in self.errors if e['category'] == 'integrity'),
            }
        }


def main():
    import argparse as _argparse

    parser = _argparse.ArgumentParser(
        description="Validate Project JSON against schema and internal integrity rules"
    )
    parser.add_argument("project", help="Project JSON file")
    parser.add_argument("schema", help="Language schema JSON file")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress progress messages to stderr")
    parser.add_argument("--brief", action="store_true",
                        help="Print one-line summary instead of full JSON report")
    args = parser.parse_args()

    project_file = Path(args.project)
    schema_file = Path(args.schema)

    def progress(msg):
        if not args.quiet:
            print(msg, file=sys.stderr)

    validator = ProjectValidator(project_file, schema_file)

    progress("Validating schema...")
    validator.validate_schema()

    progress("Validating practice/method reference...")
    validator.validate_practice_reference()

    progress("Validating cycles...")
    validator.validate_cycles()

    progress("Validating pattern view references...")
    validator.validate_pattern_view_references()

    progress("Validating instance consistency...")
    validator.validate_instance_consistency()

    progress("Validating schema version...")
    validator.validate_schema_version()

    report = validator.generate_report()

    if args.brief:
        status = "PASS" if report["valid"] else "FAIL"
        errs = report.get("error_count", 0)
        warns = report.get("warning_count", 0)
        warn_str = f" ({warns} warnings)" if warns else ""
        print(f"{status} {errs} errors{warn_str} — {project_file.name}")
    else:
        print(json.dumps(report, indent=2))

    sys.exit(0 if report['valid'] else 1)


if __name__ == '__main__':
    main()

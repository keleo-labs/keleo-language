#!/usr/bin/env python3
"""
Comprehensive Practice Language JSON Validator

Validates Practice/Method JSON files against:
1. JSON Schema (deps/language.schema.json)
2. Baseline practice references (user-provided baseline)
3. Internal cross-reference integrity

Outputs structured JSON report for skill consumption.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _venv_bootstrap import ensure_dependencies  # noqa: E402

ensure_dependencies()

import jsonschema  # noqa: E402
from jsonschema import Draft202012Validator, RefResolver  # noqa: E402


class PracticeValidator:
    """Validates Practice/Method JSON against schema, baseline, and internal refs"""

    def __init__(self, practice_file: Path, baseline_file: Path, schema_file: Path,
                 dependency_files: Optional[List[Path]] = None):
        self.practice_file = practice_file
        self.baseline_file = baseline_file
        self.schema_file = schema_file
        self.dependency_files = dependency_files or []
        self.errors = []
        self.warnings = []

        # Load files
        self.practice = self._load_json(practice_file)
        self.baseline = self._load_json(baseline_file)
        self.schema = self._load_json(schema_file)
        self.dependencies = [self._load_json(f) for f in self.dependency_files]

        # Build baseline indexes
        self.baseline_alphas = {}
        self.baseline_alpha_states = defaultdict(set)
        self.baseline_competencies = set()
        self.baseline_activity_spaces = set()
        self.baseline_focuses = set()

        self._index_baseline()

        # Build dependency indexes (from parent/dependency practice files)
        self.dep_alphas = {}
        self.dep_alpha_states = defaultdict(set)
        self.dep_competencies = set()
        self.dep_competency_levels = defaultdict(set)
        self.dep_activity_spaces = set()
        self.dep_focuses = set()

        self._index_dependencies()

    def _load_json(self, file_path: Path) -> Dict:
        """Load and parse JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in {file_path}: {e}", file=sys.stderr)
            sys.exit(1)

    def _resolve_baseline_chain(self) -> List[Dict]:
        """Walk the baseline inheritance chain and return all baselines (child-first)."""
        chain = [self.baseline]
        visited = {self.baseline.get('name')}
        current = self.baseline
        resolved_parent = self.baseline_file.resolve().parent
        search_dirs = [resolved_parent]
        project_root = resolved_parent
        while project_root != project_root.parent:
            if (project_root / 'deps').is_dir() or (project_root / 'baselines').is_dir():
                search_dirs.extend([project_root / 'deps', project_root / 'baselines'])
                break
            project_root = project_root.parent

        while True:
            parent_name = current.get('baselinePracticeName')
            if not parent_name or parent_name in visited:
                break
            visited.add(parent_name)
            parent = self._find_baseline_by_name(parent_name, search_dirs)
            if not parent:
                print(f"WARNING: Could not find parent baseline '{parent_name}' in search path", file=sys.stderr)
                break
            chain.append(parent)
            current = parent
        return chain

    def _find_baseline_by_name(self, name: str, search_dirs: List[Path]) -> Optional[Dict]:
        """Search for a baseline JSON file by its document name."""
        for d in search_dirs:
            if not d.is_dir():
                continue
            for f in d.rglob('*.json'):
                try:
                    with open(f, 'r', encoding='utf-8') as fh:
                        data = json.load(fh)
                    if data.get('name') == name and data.get('kind') == 'practiceBaseline':
                        return data
                except (json.JSONDecodeError, OSError, KeyError):
                    continue
        return None

    def _index_baseline(self):
        """Build indexes of baseline elements, walking the inheritance chain."""
        chain = self._resolve_baseline_chain()
        for baseline in reversed(chain):
            for focus in baseline.get('focuses', []):
                self.baseline_focuses.add(focus['name'])

            for alpha in baseline.get('alphas', []):
                alpha_name = alpha['name']
                self.baseline_alphas[alpha_name] = alpha
                for state in alpha.get('states', []):
                    self.baseline_alpha_states[alpha_name].add(state['name'])

            for comp in baseline.get('competencies', []):
                self.baseline_competencies.add(comp['name'])

            for asp in baseline.get('activitySpaces', []):
                self.baseline_activity_spaces.add(asp['name'])

    def _index_dependencies(self):
        """Build indexes of dependency practice elements for validation"""
        for dep in self.dependencies:
            # Index alphas and their states
            for alpha in dep.get('alphas', []):
                alpha_name = alpha['name']
                self.dep_alphas[alpha_name] = alpha
                for state in alpha.get('states', []):
                    self.dep_alpha_states[alpha_name].add(state['name'])

            # Index competencies and their levels
            for comp in dep.get('competencies', []):
                self.dep_competencies.add(comp['name'])
                for level in comp.get('levels', []):
                    self.dep_competency_levels[comp['name']].add(level['name'])

            # Index activity spaces
            for asp in dep.get('activitySpaces', []):
                self.dep_activity_spaces.add(asp['name'])

            # Index focuses (from dependency practices/baselines that define focuses)
            for focus in dep.get('focuses', []):
                self.dep_focuses.add(focus['name'])

    def validate_schema(self) -> bool:
        """Validate against JSON Schema"""
        try:
            # Create resolver for $ref handling
            schema_dir = self.schema_file.parent
            resolver = RefResolver(
                base_uri=f"file://{schema_dir}/",
                referrer=self.schema
            )

            validator = Draft202012Validator(self.schema, resolver=resolver)

            schema_errors = list(validator.iter_errors(self.practice))

            for error in schema_errors:
                # Build path string
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
                    "suggestion": self._suggest_schema_fix(error)
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
                "suggestion": "Check schema file and practice JSON structure"
            })
            return False

    def _suggest_schema_fix(self, error: jsonschema.ValidationError) -> str:
        """Generate helpful suggestion for schema errors"""
        if error.validator == 'required':
            return f"Add required property: {error.message}"
        elif error.validator == 'type':
            return f"Change type to {error.validator_value}"
        elif error.validator == 'additionalProperties':
            return f"Remove unevaluated property or check property name spelling"
        elif error.validator == 'oneOf':
            return "Check that object matches one of the allowed schemas"
        else:
            return "Review schema definition and adjust JSON structure"

    def validate_baseline_references(self) -> bool:
        """Validate references to baseline practice elements"""
        has_errors = False

        # Determine if this is a Practice or Method
        is_method = 'practices' in self.practice or 'baselinePractice' in self.practice

        if is_method:
            practices = self.practice.get('practices', [])
        else:
            practices = [self.practice]

        # Build practice-defined elements (alphas, work products, etc.)
        practice_alphas = {}
        practice_alpha_states = defaultdict(set)

        # Index alphas from ALL practices in method (for cross-practice references)
        for practice in practices:
            # Index practice-defined alphas and merge states
            for alpha in practice.get('alphas', []):
                alpha_name = alpha['name']
                practice_alphas[alpha_name] = alpha

                for state in alpha.get('states', []):
                    practice_alpha_states[alpha_name].add(state['name'])

        # Merge baseline + dependency + practice alpha states
        merged_alpha_states = defaultdict(set)
        for alpha_name in self.baseline_alpha_states:
            merged_alpha_states[alpha_name].update(self.baseline_alpha_states[alpha_name])
        for alpha_name in self.dep_alpha_states:
            merged_alpha_states[alpha_name].update(self.dep_alpha_states[alpha_name])
        for alpha_name in practice_alpha_states:
            merged_alpha_states[alpha_name].update(practice_alpha_states[alpha_name])

        # Validate each practice
        for practice_idx, practice in enumerate(practices):
            prefix = f"practices[{practice_idx}]" if is_method else ""

            # Build allowed alphas for THIS practice
            # Includes: baseline + dependency + practice-defined + cross-practice dependencies
            allowed_alphas = set(self.baseline_alphas.keys())
            allowed_alphas.update(self.dep_alphas.keys())
            allowed_alphas.update(practice_alphas.keys())

            # For cross-practice dependencies (via practiceDependencyNames),
            # allow alpha references without validation since dependency practices
            # may not be available at validation time
            practice_deps = practice.get('practiceDependencyNames', [])
            has_cross_practice_deps = len(practice_deps) > 0

            # Validate competency references
            has_errors |= self._validate_competencies(practice, prefix)

            # Validate alpha and state references
            has_errors |= self._validate_alphas(
                practice,
                merged_alpha_states,
                prefix,
                allowed_alphas,
                has_cross_practice_deps
            )

            # Validate focus references
            has_errors |= self._validate_focuses(practice, prefix)

            # Validate activity space references
            has_errors |= self._validate_activity_spaces(practice, prefix)

            # Validate practice element aliases
            has_errors |= self._validate_aliases(practice, prefix)

        return not has_errors

    def _validate_competencies(self, practice: Dict, prefix: str) -> bool:
        """Validate competency name references against baseline, dependency, and practice-defined competencies"""
        has_errors = False

        # Merge baseline + dependency + practice-defined competencies for validation
        all_competencies = self.baseline_competencies | self.dep_competencies
        # Include competencies defined in the practice itself (schema supports Practice.competencies)
        for comp in practice.get('competencies', []):
            all_competencies.add(comp['name'])

        # Check activities
        for idx, activity in enumerate(practice.get('activities', [])):
            path = f"{prefix}.activities[{idx}]" if prefix else f"activities[{idx}]"

            # requiredCompetencies (array of strings)
            for comp_idx, comp_name in enumerate(activity.get('requiredCompetencies', [])):
                if comp_name not in all_competencies:
                    self.errors.append({
                        "category": "baseline",
                        "severity": "error",
                        "path": f"{path}.requiredCompetencies[{comp_idx}]",
                        "issue": f"Invalid competency name: '{comp_name}'",
                        "expected": f"One of: {sorted(all_competencies)}",
                        "actual": comp_name,
                        "suggestion": self._suggest_competency(comp_name)
                    })
                    has_errors = True

            # recommendedCompetencyLevels (array of {competencyName, competencyLevelName})
            for clr_idx, clr in enumerate(activity.get('recommendedCompetencyLevels', [])):
                comp_name = clr.get('competencyName')
                if comp_name and comp_name not in all_competencies:
                    self.errors.append({
                        "category": "baseline",
                        "severity": "error",
                        "path": f"{path}.recommendedCompetencyLevels[{clr_idx}].competencyName",
                        "issue": f"Invalid competency name: '{comp_name}'",
                        "expected": f"One of: {sorted(all_competencies)}",
                        "actual": comp_name,
                        "suggestion": self._suggest_competency(comp_name)
                    })
                    has_errors = True

        # Check personas
        for idx, persona in enumerate(practice.get('personas', [])):
            path = f"{prefix}.personas[{idx}]" if prefix else f"personas[{idx}]"

            for clr_idx, clr in enumerate(persona.get('competencies', [])):
                comp_name = clr.get('competencyName')
                if comp_name and comp_name not in all_competencies:
                    self.errors.append({
                        "category": "baseline",
                        "severity": "error",
                        "path": f"{path}.competencies[{clr_idx}].competencyName",
                        "issue": f"Invalid competency name: '{comp_name}'",
                        "expected": f"One of: {sorted(all_competencies)}",
                        "actual": comp_name,
                        "suggestion": self._suggest_competency(comp_name)
                    })
                    has_errors = True

        return has_errors

    def _suggest_competency(self, comp_name: str) -> str:
        """Suggest correct competency name based on fuzzy matching"""
        # Simple substring matching
        comp_lower = comp_name.lower()

        if any(word in comp_lower for word in ['security', 'compliance', 'govern']):
            return "Use: 'Platform Security And Compliance Enforcement'"
        elif any(word in comp_lower for word in ['strategy', 'strategic', 'align']):
            return "Use: 'Platform Strategic Alignment'"
        elif any(word in comp_lower for word in ['reliability', 'sre', 'site']):
            return "Use: 'Site Reliability'"
        elif any(word in comp_lower for word in ['stakeholder', 'represent']):
            return "Use: 'Stakeholder Representation'"
        elif any(word in comp_lower for word in ['engineer', 'develop', 'build']):
            return "Use: 'Engineering'"
        elif any(word in comp_lower for word in ['analy', 'research']):
            return "Use: 'Analysis'"
        elif any(word in comp_lower for word in ['lead', 'leader']):
            return "Use: 'Leadership'"
        elif any(word in comp_lower for word in ['manage', 'project']):
            return "Use: 'Management'"
        else:
            return f"Check baseline competencies: {sorted(self.baseline_competencies)}"

    def _validate_alphas(self, practice: Dict, merged_alpha_states: Dict, prefix: str,
                         allowed_alphas: set, has_cross_practice_deps: bool) -> bool:
        """Validate alpha and state references"""
        has_errors = False

        # Use provided allowed_alphas set (includes baseline + practice-defined)
        valid_alphas = allowed_alphas

        # Check new alphas have contributesTo or mapsTo (or are from practice dependencies)
        for idx, alpha in enumerate(practice.get('alphas', [])):
            alpha_name = alpha['name']
            path = f"{prefix}.alphas[{idx}]" if prefix else f"alphas[{idx}]"
            contributes_to = alpha.get('contributesTo')
            maps_to = alpha.get('mapsTo')

            # If not a baseline or dependency practice alpha, must have contributesTo or mapsTo
            if alpha_name not in self.baseline_alphas and alpha_name not in self.dep_alphas:
                if not contributes_to and not maps_to:
                    self.errors.append({
                        "category": "baseline",
                        "severity": "error",
                        "path": f"{path}",
                        "issue": f"New alpha '{alpha_name}' missing contributesTo or mapsTo (floating alpha)",
                        "expected": "contributesTo or mapsTo pointing to a parent alpha",
                        "actual": None,
                        "suggestion": f"Add contributesTo (specialization) or mapsTo (variant mapping) pointing to one of: {sorted(self.baseline_alphas.keys())} or practice-local alpha defined earlier"
                    })
                    has_errors = True
                if contributes_to and contributes_to not in self.baseline_alphas and contributes_to not in valid_alphas:
                    if not has_cross_practice_deps:
                        self.errors.append({
                            "category": "baseline",
                            "severity": "error",
                            "path": f"{path}.contributesTo",
                            "issue": f"contributesTo references unknown alpha: '{contributes_to}'",
                            "expected": f"One of: {sorted(self.baseline_alphas.keys())} or practice-local alpha",
                            "actual": contributes_to,
                            "suggestion": f"Use exact baseline alpha name (case-sensitive) or add to practiceDependencyNames if from external practice"
                        })
                        has_errors = True
                if maps_to and maps_to not in self.baseline_alphas and maps_to not in valid_alphas:
                    if not has_cross_practice_deps:
                        self.errors.append({
                            "category": "baseline",
                            "severity": "error",
                            "path": f"{path}.mapsTo",
                            "issue": f"mapsTo references unknown alpha: '{maps_to}'",
                            "expected": f"One of: {sorted(self.baseline_alphas.keys())} or practice-local alpha",
                            "actual": maps_to,
                            "suggestion": f"Use exact baseline alpha name (case-sensitive) or add to practiceDependencyNames if from external practice"
                        })
                        has_errors = True
                if contributes_to and maps_to and contributes_to == maps_to:
                    self.errors.append({
                        "category": "baseline",
                        "severity": "error",
                        "path": f"{path}",
                        "issue": f"Alpha '{alpha_name}' has contributesTo and mapsTo referencing the same alpha: '{contributes_to}'",
                        "expected": "contributesTo and mapsTo must reference different alphas",
                        "actual": f"Both reference '{contributes_to}'",
                        "suggestion": "An alpha can both contribute to one alpha and map to another, but the targets must be different"
                    })
                    has_errors = True

        # Validate AlphaContribution references in activities
        for idx, activity in enumerate(practice.get('activities', [])):
            path = f"{prefix}.activities[{idx}]" if prefix else f"activities[{idx}]"

            for contrib_idx, contrib in enumerate(activity.get('contributesTo', [])):
                alpha_name = contrib.get('alphaName')
                state_name = contrib.get('stateName')
                contrib_path = f"{path}.contributesTo[{contrib_idx}]"

                if alpha_name and alpha_name not in valid_alphas:
                    # If practice has cross-practice dependencies, allow reference (may be from external practice)
                    if not has_cross_practice_deps:
                        self.errors.append({
                            "category": "baseline",
                            "severity": "error",
                            "path": f"{contrib_path}.alphaName",
                            "issue": f"Unknown alpha: '{alpha_name}'",
                            "expected": f"One of: {sorted(valid_alphas)}",
                            "actual": alpha_name,
                            "suggestion": "Use exact alpha name (case-sensitive) or add to practiceDependencyNames if from external practice"
                        })
                        has_errors = True

                if alpha_name and state_name:
                    # Only validate state if alpha is known (in merged_alpha_states)
                    if alpha_name in merged_alpha_states:
                        if state_name not in merged_alpha_states.get(alpha_name, set()):
                            self.errors.append({
                                "category": "baseline",
                                "severity": "error",
                                "path": f"{contrib_path}.stateName",
                                "issue": f"Unknown state '{state_name}' for alpha '{alpha_name}'",
                                "expected": f"One of: {sorted(merged_alpha_states.get(alpha_name, set()))}",
                                "actual": state_name,
                                "suggestion": f"Check state names defined in {alpha_name} alpha"
                            })
                            has_errors = True
                    elif not has_cross_practice_deps:
                        # Alpha unknown and no cross-practice deps - error
                        self.errors.append({
                            "category": "baseline",
                            "severity": "error",
                            "path": f"{contrib_path}.alphaName",
                            "issue": f"Cannot validate state for unknown alpha: '{alpha_name}'",
                            "expected": f"Define alpha in practice or add to practiceDependencyNames",
                            "actual": alpha_name,
                            "suggestion": "Add alpha definition or declare practice dependency"
                        })
                        has_errors = True

        # Validate AlphaContribution in work product LODs
        for wp_idx, wp in enumerate(practice.get('workProducts', [])):
            wp_path = f"{prefix}.workProducts[{wp_idx}]" if prefix else f"workProducts[{wp_idx}]"

            for lod_idx, lod in enumerate(wp.get('levelsOfDetail', [])):
                lod_path = f"{wp_path}.levelsOfDetail[{lod_idx}]"

                for contrib_idx, contrib in enumerate(lod.get('contributesTo', [])):
                    alpha_name = contrib.get('alphaName')
                    state_name = contrib.get('stateName')
                    contrib_path = f"{lod_path}.contributesTo[{contrib_idx}]"

                    if alpha_name and alpha_name not in valid_alphas:
                        # If practice has cross-practice dependencies, allow reference (may be from external practice)
                        if not has_cross_practice_deps:
                            self.errors.append({
                                "category": "baseline",
                                "severity": "error",
                                "path": f"{contrib_path}.alphaName",
                                "issue": f"Unknown alpha: '{alpha_name}'",
                                "expected": f"One of: {sorted(valid_alphas)}",
                                "actual": alpha_name,
                                "suggestion": "Use exact alpha name (case-sensitive) or add to practiceDependencyNames if from external practice"
                            })
                            has_errors = True

                    if alpha_name and state_name:
                        # Only validate state if alpha is known (in merged_alpha_states)
                        if alpha_name in merged_alpha_states:
                            if state_name not in merged_alpha_states.get(alpha_name, set()):
                                self.errors.append({
                                    "category": "baseline",
                                    "severity": "error",
                                    "path": f"{contrib_path}.stateName",
                                    "issue": f"Unknown state '{state_name}' for alpha '{alpha_name}'",
                                    "expected": f"One of: {sorted(merged_alpha_states.get(alpha_name, set()))}",
                                    "actual": state_name,
                                    "suggestion": f"Check state names defined in {alpha_name} alpha"
                                })
                                has_errors = True
                        elif not has_cross_practice_deps:
                            # Alpha unknown and no cross-practice deps - error
                            self.errors.append({
                                "category": "baseline",
                                "severity": "error",
                                "path": f"{contrib_path}.alphaName",
                                "issue": f"Cannot validate state for unknown alpha: '{alpha_name}'",
                                "expected": f"Define alpha in practice or add to practiceDependencyNames",
                                "actual": alpha_name,
                                "suggestion": "Add alpha definition or declare practice dependency"
                            })
                            has_errors = True

        return has_errors

    def _validate_focuses(self, practice: Dict, prefix: str) -> bool:
        """Validate focus references against baseline and dependency focuses"""
        has_errors = False

        # Merge baseline + dependency focuses for validation
        all_focuses = self.baseline_focuses | self.dep_focuses

        # Check alpha focus references
        for idx, alpha in enumerate(practice.get('alphas', [])):
            focus_name = alpha.get('focusName')
            if focus_name and focus_name not in all_focuses:
                path = f"{prefix}.alphas[{idx}].focusName" if prefix else f"alphas[{idx}].focusName"
                self.errors.append({
                    "category": "baseline",
                    "severity": "error",
                    "path": path,
                    "issue": f"Unknown focus: '{focus_name}'",
                    "expected": f"One of: {sorted(all_focuses)}",
                    "actual": focus_name,
                    "suggestion": f"Use one of: {sorted(all_focuses)}"
                })
                has_errors = True

        # Check activity focus references
        for idx, activity in enumerate(practice.get('activities', [])):
            focus_name = activity.get('focusName')
            if focus_name and focus_name not in all_focuses:
                path = f"{prefix}.activities[{idx}].focusName" if prefix else f"activities[{idx}].focusName"
                self.errors.append({
                    "category": "baseline",
                    "severity": "error",
                    "path": path,
                    "issue": f"Unknown focus: '{focus_name}'",
                    "expected": f"One of: {sorted(all_focuses)}",
                    "actual": focus_name,
                    "suggestion": f"Use one of: {sorted(all_focuses)}"
                })
                has_errors = True

        return has_errors

    def _validate_activity_spaces(self, practice: Dict, prefix: str) -> bool:
        """Validate activity space references and required activity properties"""
        has_errors = False

        # Check activity references to activity spaces
        for idx, activity in enumerate(practice.get('activities', [])):
            # Required properties for Activity (per schema)
            required_activity_props = {
                'activitySpaceName': 'string (references ActivitySpace.name)',
                'focusName': 'string (references Focus.name)',
                'contributesTo': 'array of AlphaContribution',
                'worksOn': 'array of WorkProductContribution',
                'requiredCompetencies': 'array of Competency.name strings',
                'recommendedCompetencyLevels': 'array of CompetencyLevelReference'
            }

            # Check for missing required properties
            for prop, prop_type in required_activity_props.items():
                if prop not in activity:
                    path = f"{prefix}.activities[{idx}]" if prefix else f"activities[{idx}]"
                    self.errors.append({
                        "category": "schema",
                        "severity": "error",
                        "path": path,
                        "issue": f"Missing required Activity property: '{prop}'",
                        "expected": f"Activity must have '{prop}' ({prop_type})",
                        "actual": f"Activity '{activity.get('name', 'unnamed')}' missing '{prop}'",
                        "suggestion": f"Add '{prop}' property to activity. According to schema, Activity extends ActivitySpaceCore which requires: activitySpaceName (for flat Practice.activities), focusName, contributesTo, requiredCompetencies. Activity also requires: worksOn, recommendedCompetencyLevels."
                    })
                    has_errors = True

            # Validate activitySpaceName reference if present
            asp_name = activity.get('activitySpaceName')
            all_activity_spaces = self.baseline_activity_spaces | self.dep_activity_spaces
            if asp_name and asp_name not in all_activity_spaces:
                path = f"{prefix}.activities[{idx}].activitySpaceName" if prefix else f"activities[{idx}].activitySpaceName"
                self.errors.append({
                    "category": "baseline",
                    "severity": "warning",
                    "path": path,
                    "issue": f"Unknown activity space: '{asp_name}'",
                    "expected": f"One of: {sorted(all_activity_spaces)}",
                    "actual": asp_name,
                    "suggestion": "Verify activity space name or define it in practice"
                })
                has_errors = True

        return has_errors

    def _validate_aliases(self, practice: Dict, prefix: str) -> bool:
        """Validate practiceElementAliases: targets exist, no duplicates, no dependency collisions"""
        has_errors = False
        aliases = practice.get('practiceElementAliases', [])
        if not aliases:
            return False

        # Build index of practice-defined elements by type
        element_index = defaultdict(set)
        for alpha in practice.get('alphas', []):
            element_index['Alpha'].add(alpha['name'])
        for wp in practice.get('workProducts', []):
            element_index['WorkProduct'].add(wp['name'])
        for act in practice.get('activities', []):
            element_index['Activity'].add(act['name'])
        for persona in practice.get('personas', []):
            element_index['Persona'].add(persona['name'])
        for pattern in practice.get('patterns', []):
            element_index['Pattern'].add(pattern['name'])
        for team in practice.get('teams', []):
            element_index['Team'].add(team['name'])

        # Include baseline and dependency elements
        for alpha_name in self.baseline_alphas:
            element_index['Alpha'].add(alpha_name)
        for alpha_name in self.dep_alphas:
            element_index['Alpha'].add(alpha_name)
        for comp_name in self.baseline_competencies | self.dep_competencies:
            element_index['Competency'].add(comp_name)

        # Also index dependency-sourced elements by type
        for dep in self.dependencies:
            for wp in dep.get('workProducts', []):
                element_index['WorkProduct'].add(wp['name'])
            for act in dep.get('activities', []):
                element_index['Activity'].add(act['name'])
            for persona in dep.get('personas', []):
                element_index['Persona'].add(persona['name'])
            for pattern in dep.get('patterns', []):
                element_index['Pattern'].add(pattern['name'])
            for team in dep.get('teams', []):
                element_index['Team'].add(team['name'])

        # Build dependency alias index for collision detection
        dep_aliases = {}
        for dep in self.dependencies:
            for a in dep.get('practiceElementAliases', []):
                dep_aliases[a.get('aliasName', '')] = a.get('practiceElementName', '')

        seen_alias_names = {}
        for idx, alias in enumerate(aliases):
            path = f"{prefix}.practiceElementAliases[{idx}]" if prefix else f"practiceElementAliases[{idx}]"
            alias_name = alias.get('aliasName', '')
            element_name = alias.get('practiceElementName', '')
            element_type = alias.get('practiceElementType', '')

            # Check alias target references a valid element of the declared type
            if element_type and element_name:
                if element_type in element_index and element_name not in element_index[element_type]:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": f"{path}.practiceElementName",
                        "issue": f"Alias references undefined {element_type}: '{element_name}'",
                        "expected": f"One of: {sorted(element_index.get(element_type, set()))}",
                        "actual": element_name,
                        "suggestion": f"Correct the element name or define the {element_type}"
                    })
                    has_errors = True

            # Check for duplicate alias names within this practice
            if alias_name in seen_alias_names:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"{path}.aliasName",
                    "issue": f"Duplicate alias name: '{alias_name}'",
                    "expected": "Unique alias names within a practice",
                    "actual": f"'{alias_name}' already defined for '{seen_alias_names[alias_name]}'",
                    "suggestion": "Remove the duplicate or differentiate the alias name"
                })
                has_errors = True
            else:
                seen_alias_names[alias_name] = element_name

            # Check for collisions with dependency practice aliases
            if alias_name in dep_aliases:
                dep_target = dep_aliases[alias_name]
                if dep_target != element_name:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": f"{path}.aliasName",
                        "issue": f"Alias name '{alias_name}' collides with dependency alias (different target)",
                        "expected": f"Dependency maps '{alias_name}' -> '{dep_target}'",
                        "actual": f"Practice maps '{alias_name}' -> '{element_name}'",
                        "suggestion": f"Use a differentiated alias name (e.g. prefix with practice domain)"
                    })
                    has_errors = True
                else:
                    self.warnings.append({
                        "category": "redundancy",
                        "severity": "warning",
                        "path": f"{path}.aliasName",
                        "issue": f"Alias '{alias_name}' -> '{element_name}' duplicates a dependency practice alias",
                        "expected": "Aliases inherited from dependency practices do not need re-declaration",
                        "actual": f"Same alias defined in both this practice and a dependency",
                        "suggestion": "Remove this alias — it is inherited from the dependency practice"
                    })

        return has_errors

    def _validate_references(self, practice: Dict, prefix: str,
                             all_alphas: set, all_alpha_states: Dict,
                             all_work_products: set, all_wp_lods: Dict,
                             has_cross_practice_deps: bool) -> bool:
        """Validate references array: alpha/state and work product/LOD cross-references, duplicate names, missing links"""
        has_errors = False

        seen_ref_names = set()
        for ref_idx, ref in enumerate(practice.get('references', [])):
            ref_path = f"{prefix}.references[{ref_idx}]" if prefix else f"references[{ref_idx}]"
            ref_name = ref.get('name', '')
            alpha_name = ref.get('alphaName')
            state_name = ref.get('stateName')

            if ref_name in seen_ref_names:
                self.warnings.append({
                    "category": "integrity",
                    "severity": "warning",
                    "path": f"{ref_path}.name",
                    "issue": f"Duplicate reference name: '{ref_name}'",
                    "expected": "Unique reference names within a practice",
                    "actual": ref_name,
                    "suggestion": "Differentiate reference names to avoid ambiguity"
                })
            seen_ref_names.add(ref_name)

            links = ref.get('links', [])
            if not links:
                self.warnings.append({
                    "category": "integrity",
                    "severity": "warning",
                    "path": f"{ref_path}.links",
                    "issue": f"Reference '{ref_name}' has no links — references without external links provide limited actionable value",
                    "expected": "At least one links entry with a valid URI",
                    "actual": "No links",
                    "suggestion": "Add at least one ExternalLink with a URI to make this reference actionable"
                })

            if alpha_name and alpha_name not in all_alphas and not has_cross_practice_deps:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"{ref_path}.alphaName",
                    "issue": f"Reference '{ref.get('name', '')}' references undefined alpha: '{alpha_name}'",
                    "expected": f"One of: {sorted(all_alphas)}",
                    "actual": alpha_name,
                    "suggestion": "Define alpha or correct reference"
                })
                has_errors = True

            if alpha_name and state_name and alpha_name in all_alpha_states:
                if state_name not in all_alpha_states.get(alpha_name, set()):
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": f"{ref_path}.stateName",
                        "issue": f"Reference '{ref.get('name', '')}' references undefined state '{state_name}' for alpha '{alpha_name}'",
                        "expected": f"One of: {sorted(all_alpha_states.get(alpha_name, set()))}",
                        "actual": state_name,
                        "suggestion": f"Check state names defined in {alpha_name} alpha"
                    })
                    has_errors = True

            for ev_idx, evidence in enumerate(ref.get('evidenceBy', []) or []):
                ev_path = f"{ref_path}.evidenceBy[{ev_idx}]"
                wp_name = evidence.get('workProductName')
                lod_name = evidence.get('levelOfDetailName')

                if wp_name and wp_name not in all_work_products and not has_cross_practice_deps:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": f"{ev_path}.workProductName",
                        "issue": f"Reference evidence '{evidence.get('name', '')}' references undefined work product: '{wp_name}'",
                        "expected": f"One of: {sorted(all_work_products)}",
                        "actual": wp_name,
                        "suggestion": "Define work product or correct reference"
                    })
                    has_errors = True

                if wp_name and lod_name and wp_name in all_wp_lods:
                    if lod_name not in all_wp_lods.get(wp_name, set()):
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": f"{ev_path}.levelOfDetailName",
                            "issue": f"Reference evidence '{evidence.get('name', '')}' references undefined level '{lod_name}' for work product '{wp_name}'",
                            "expected": f"One of: {sorted(all_wp_lods.get(wp_name, set()))}",
                            "actual": lod_name,
                            "suggestion": f"Check level names defined in {wp_name} work product"
                        })
                        has_errors = True

        return has_errors

    def validate_internal_integrity(self) -> bool:
        """Validate internal cross-references within practice/method"""
        has_errors = False

        # Determine if this is a Practice or Method
        is_method = 'practices' in self.practice or 'baselinePractice' in self.practice

        if is_method:
            practices = self.practice.get('practices', [])
        else:
            practices = [self.practice]

        # Build element indexes across all practices
        all_alphas = set()
        all_alpha_states = defaultdict(set)
        all_work_products = set()
        all_activities = set()

        # Track which practices have cross-practice dependencies
        practices_with_deps = {}
        for practice in practices:
            practice_name = practice.get('name')
            practice_deps = practice.get('practiceDependencyNames', [])
            if practice_deps:
                practices_with_deps[practice_name] = practice_deps

        # Index baseline elements
        for alpha in self.baseline.get('alphas', []):
            all_alphas.add(alpha['name'])
            for state in alpha.get('states', []):
                all_alpha_states[alpha['name']].add(state['name'])

        # Index dependency practice elements (alphas, states, work products, activities)
        for dep in self.dependencies:
            for alpha in dep.get('alphas', []):
                all_alphas.add(alpha['name'])
                for state in alpha.get('states', []):
                    all_alpha_states[alpha['name']].add(state['name'])
            for wp in dep.get('workProducts', []):
                all_work_products.add(wp['name'])
            for activity in dep.get('activities', []):
                all_activities.add(activity['name'])

        # Index practice-defined elements
        for practice in practices:
            for alpha in practice.get('alphas', []):
                alpha_name = alpha['name']
                all_alphas.add(alpha_name)
                for state in alpha.get('states', []):
                    all_alpha_states[alpha_name].add(state['name'])

            for wp in practice.get('workProducts', []):
                all_work_products.add(wp['name'])

            for activity in practice.get('activities', []):
                all_activities.add(activity['name'])

        # Build ordered LOD sequence index for mapsTo validation
        wp_lod_sequences = {}
        for wp in self.baseline.get('workProducts', []):
            lods = wp.get('levelsOfDetail', [])
            wp_lod_sequences[wp['name']] = [lod['name'] for lod in sorted(lods, key=lambda l: l.get('seq', 0))]
        for dep in self.dependencies:
            for wp in dep.get('workProducts', []):
                lods = wp.get('levelsOfDetail', [])
                wp_lod_sequences.setdefault(wp['name'], [lod['name'] for lod in sorted(lods, key=lambda l: l.get('seq', 0))])
        for practice in practices:
            for wp in practice.get('workProducts', []):
                lods = wp.get('levelsOfDetail', [])
                wp_lod_sequences.setdefault(wp['name'], [lod['name'] for lod in sorted(lods, key=lambda l: l.get('seq', 0))])

        # Validate each practice
        for practice_idx, practice in enumerate(practices):
            prefix = f"practices[{practice_idx}]" if is_method else ""
            practice_name = practice.get('name')
            has_cross_practice_deps = practice_name in practices_with_deps

            # Validate activity -> work product references
            for act_idx, activity in enumerate(practice.get('activities', [])):
                path = f"{prefix}.activities[{act_idx}]" if prefix else f"activities[{act_idx}]"

                for wp_idx, wp_contrib in enumerate(activity.get('worksOn', [])):
                    wp_name = wp_contrib.get('workProductName')
                    if wp_name and wp_name not in all_work_products:
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": f"{path}.worksOn[{wp_idx}].workProductName",
                            "issue": f"Activity references undefined work product: '{wp_name}'",
                            "expected": f"One of: {sorted(all_work_products)}",
                            "actual": wp_name,
                            "suggestion": "Define work product or correct reference"
                        })
                        has_errors = True

            # Validate work product partOf and mapsTo references
            for wp_idx, wp in enumerate(practice.get('workProducts', [])):
                wp_path = f"{prefix}.workProducts[{wp_idx}]" if prefix else f"workProducts[{wp_idx}]"
                part_of = wp.get('partOf')
                maps_to = wp.get('mapsTo')

                # partOf and mapsTo may coexist but must reference different work products
                if part_of and maps_to and part_of == maps_to:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": wp_path,
                        "issue": f"Work product '{wp.get('name')}' has partOf and mapsTo referencing the same work product: '{part_of}'",
                        "expected": "partOf and mapsTo must reference different work products",
                        "actual": f"partOf: '{part_of}', mapsTo: '{maps_to}'",
                        "suggestion": "partOf models containment (sub-artifact within parent). mapsTo models variant mapping (IS-A variant with same LODs). They must reference different targets."
                    })
                    has_errors = True

                if part_of:
                    if part_of == wp.get('name'):
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": f"{wp_path}.partOf",
                            "issue": f"Work product '{wp.get('name')}' cannot be partOf itself",
                            "expected": "Different work product name",
                            "actual": part_of,
                            "suggestion": "Remove self-referencing partOf or correct the reference"
                        })
                        has_errors = True
                    elif part_of not in all_work_products and not has_cross_practice_deps:
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": f"{wp_path}.partOf",
                            "issue": f"partOf references undefined work product: '{part_of}'",
                            "expected": f"One of: {sorted(all_work_products)}",
                            "actual": part_of,
                            "suggestion": "Define work product or correct reference"
                        })
                        has_errors = True

                if maps_to:
                    if maps_to == wp.get('name'):
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": f"{wp_path}.mapsTo",
                            "issue": f"Work product '{wp.get('name')}' cannot mapsTo itself",
                            "expected": "Different work product name",
                            "actual": maps_to,
                            "suggestion": "Remove self-referencing mapsTo or correct the reference"
                        })
                        has_errors = True
                    elif maps_to not in all_work_products and not has_cross_practice_deps:
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": f"{wp_path}.mapsTo",
                            "issue": f"mapsTo references undefined work product: '{maps_to}'",
                            "expected": f"One of: {sorted(all_work_products)}",
                            "actual": maps_to,
                            "suggestion": "Define work product or correct reference"
                        })
                        has_errors = True
                    elif maps_to in wp_lod_sequences:
                        variant_lods = [lod['name'] for lod in sorted(wp.get('levelsOfDetail', []), key=lambda l: l.get('seq', 0))]
                        parent_lods = wp_lod_sequences[maps_to]
                        if variant_lods != parent_lods:
                            self.errors.append({
                                "category": "integrity",
                                "severity": "error",
                                "path": f"{wp_path}.mapsTo",
                                "issue": f"mapsTo variant '{wp.get('name')}' LODs do not match parent '{maps_to}' — variant LODs must be identical",
                                "expected": f"LODs: {parent_lods}",
                                "actual": f"LODs: {variant_lods}",
                                "suggestion": "mapsTo requires identical LOD names and sequences. Use the same LOD names as the parent work product with domain-specific checklists."
                            })
                            has_errors = True

            # Validate pattern view -> activity/alpha references
            for pattern_idx, pattern in enumerate(practice.get('patterns', [])):
                pattern_path = f"{prefix}.patterns[{pattern_idx}]" if prefix else f"patterns[{pattern_idx}]"
                pattern_name = pattern.get('name', f'pattern[{pattern_idx}]')

                view_count = len(pattern.get('patternViews', []))
                if view_count < 2:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": f"{pattern_path}.patternViews",
                        "issue": f"Pattern '{pattern_name}' has {view_count} patternView(s), minimum is 2",
                        "expected": "At least 2 patternViews showing progressive alpha advancement",
                        "actual": f"{view_count} patternView(s)",
                        "suggestion": "Add patternViews from the mapping guide — patterns must show progression across at least 2 phases"
                    })
                    has_errors = True

                for view_idx, view in enumerate(pattern.get('patternViews', [])):
                    view_path = f"{pattern_path}.patternViews[{view_idx}]"
                    view_name = view.get('name', f'view[{view_idx}]')

                    # Check for ambiguous alpha targets (same alpha, multiple states)
                    alpha_state_map = defaultdict(list)
                    for as_entry in view.get('alphaStates', []):
                        if isinstance(as_entry, dict):
                            alpha_state_map[as_entry.get('alphaName', '')].append(
                                as_entry.get('stateName', ''))
                    for alpha_name, states in alpha_state_map.items():
                        if len(states) > 1:
                            self.errors.append({
                                "category": "integrity",
                                "severity": "error",
                                "path": f"{view_path}.alphaStates",
                                "issue": f"Ambiguous pattern view: alpha '{alpha_name}' targets {len(states)} states in '{view_name}'",
                                "expected": "At most one target state per alpha per patternView",
                                "actual": f"{alpha_name} -> {states}",
                                "suggestion": f"Split '{view_name}' into sequential sub-views so each advances '{alpha_name}' by one state"
                            })
                            has_errors = True

                    # Check activity references
                    for act_idx, act_name in enumerate(view.get('activities', [])):
                        if act_name not in all_activities:
                            self.errors.append({
                                "category": "integrity",
                                "severity": "error",
                                "path": f"{view_path}.activities[{act_idx}]",
                                "issue": f"Pattern view references undefined activity: '{act_name}'",
                                "expected": f"One of: {sorted(all_activities)}",
                                "actual": act_name,
                                "suggestion": "Define activity or correct reference"
                            })
                            has_errors = True

                    # Check alpha/state references
                    for as_idx, alpha_state in enumerate(view.get('alphaStates', [])):
                        if isinstance(alpha_state, dict):
                            alpha_name = alpha_state.get('alphaName')
                            state_name = alpha_state.get('stateName')

                            if alpha_name and alpha_name not in all_alphas:
                                # If practice has cross-practice deps, allow reference (may be from dependency)
                                if not has_cross_practice_deps:
                                    self.errors.append({
                                        "category": "integrity",
                                        "severity": "error",
                                        "path": f"{view_path}.alphaStates[{as_idx}].alphaName",
                                        "issue": f"Pattern view references undefined alpha: '{alpha_name}'",
                                        "expected": f"One of: {sorted(all_alphas)}",
                                        "actual": alpha_name,
                                        "suggestion": "Define alpha or add to practiceDependencyNames if from external practice"
                                    })
                                    has_errors = True

                            if alpha_name and state_name:
                                # Only validate state if alpha is known
                                if alpha_name in all_alpha_states:
                                    if state_name not in all_alpha_states.get(alpha_name, set()):
                                        self.errors.append({
                                            "category": "integrity",
                                            "severity": "error",
                                            "path": f"{view_path}.alphaStates[{as_idx}].stateName",
                                            "issue": f"Pattern view references undefined state: '{state_name}' for alpha '{alpha_name}'",
                                            "expected": f"One of: {sorted(all_alpha_states.get(alpha_name, set()))}",
                                            "actual": state_name,
                                            "suggestion": "Define state or correct reference"
                                        })
                                        has_errors = True
                                elif not has_cross_practice_deps:
                                    # Alpha unknown and no cross-practice deps
                                    self.errors.append({
                                        "category": "integrity",
                                        "severity": "error",
                                        "path": f"{view_path}.alphaStates[{as_idx}].alphaName",
                                        "issue": f"Cannot validate state for unknown alpha: '{alpha_name}'",
                                        "expected": f"Define alpha in practice or add to practiceDependencyNames",
                                        "actual": alpha_name,
                                        "suggestion": "Add alpha definition or declare practice dependency"
                                    })
                                    has_errors = True

        # Validate pattern group references
        for practice_idx, practice in enumerate(practices):
            prefix = f"practices[{practice_idx}]" if is_method else ""
            all_pattern_names = set()
            for p in practice.get('patterns', []):
                all_pattern_names.add(p.get('name', ''))
            for dep in self.dependencies:
                for p in dep.get('patterns', []):
                    all_pattern_names.add(p.get('name', ''))

            seen_pattern_refs = {}
            for pg_idx, pg in enumerate(practice.get('patternGroups', [])):
                pg_path = f"{prefix}.patternGroups[{pg_idx}]" if prefix else f"patternGroups[{pg_idx}]"
                pg_name = pg.get('name', f'patternGroup[{pg_idx}]')

                for entry_idx, entry in enumerate(pg.get('entries', [])):
                    entry_path = f"{pg_path}.entries[{entry_idx}]"
                    pn = entry.get('patternName', '')

                    if pn and pn not in all_pattern_names:
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": f"{entry_path}.patternName",
                            "issue": f"PatternGroup '{pg_name}' references undefined pattern: '{pn}'",
                            "expected": f"One of: {sorted(all_pattern_names)}",
                            "actual": pn,
                            "suggestion": "Define pattern or correct reference"
                        })
                        has_errors = True

                    if pn and pn in seen_pattern_refs:
                        self.warnings.append({
                            "category": "integrity",
                            "severity": "warning",
                            "path": f"{entry_path}.patternName",
                            "issue": f"Pattern '{pn}' appears in multiple groups: '{seen_pattern_refs[pn]}' and '{pg_name}'",
                            "expected": "A pattern should appear in at most one group",
                            "actual": f"'{pn}' in both '{seen_pattern_refs[pn]}' and '{pg_name}'",
                            "suggestion": "Remove the duplicate entry from one group"
                        })
                    elif pn:
                        seen_pattern_refs[pn] = pg_name

            # Warn when practice creates patternGroups not defined in baseline
            baseline_pg_names = set()
            for bl in [self.baseline] + list(getattr(self, '_baseline_chain', [])):
                for bpg in bl.get('patternGroups', []):
                    bl_name = bpg.get('name', '')
                    if bl_name:
                        baseline_pg_names.add(bl_name)
            if baseline_pg_names:
                for pg_idx, pg in enumerate(practice.get('patternGroups', [])):
                    pg_name = pg.get('name', '')
                    if pg_name and pg_name not in baseline_pg_names:
                        pg_path = f"{prefix}.patternGroups[{pg_idx}]" if prefix else f"patternGroups[{pg_idx}]"
                        self.warnings.append({
                            "category": "governance",
                            "severity": "warning",
                            "path": f"{pg_path}.name",
                            "issue": f"PatternGroup '{pg_name}' is not defined in the baseline — prefer adopting baseline-defined groups",
                            "expected": f"One of: {sorted(baseline_pg_names)}",
                            "actual": pg_name,
                            "suggestion": "Use a baseline-defined group name, or justify why a novel group is needed"
                        })

        # Build work product LOD index for reference validation
        all_wp_lods = defaultdict(set)
        for dep in self.dependencies:
            for wp in dep.get('workProducts', []):
                for lod in wp.get('levelsOfDetail', []):
                    all_wp_lods[wp['name']].add(lod['name'])
        for practice_scan in practices:
            for wp in practice_scan.get('workProducts', []):
                for lod in wp.get('levelsOfDetail', []):
                    all_wp_lods[wp['name']].add(lod['name'])

        # Validate practice references (curated alpha/work product examples)
        for practice_idx, practice in enumerate(practices):
            prefix = f"practices[{practice_idx}]" if is_method else ""
            practice_name = practice.get('name')
            has_cross_practice_deps = practice_name in practices_with_deps

            has_errors |= self._validate_references(
                practice, prefix, all_alphas, all_alpha_states,
                all_work_products, all_wp_lods, has_cross_practice_deps
            )

        # Detect circular partOf/mapsTo chains across all work products
        # Both partOf and mapsTo create parent edges; a work product may have both
        wp_edges = {}
        for practice_scan in practices:
            for wp in practice_scan.get('workProducts', []):
                edges = set()
                if wp.get('partOf'):
                    edges.add(wp['partOf'])
                if wp.get('mapsTo'):
                    edges.add(wp['mapsTo'])
                if edges:
                    wp_edges[wp['name']] = edges
        for dep in self.dependencies:
            for wp in dep.get('workProducts', []):
                if wp['name'] not in wp_edges:
                    edges = set()
                    if wp.get('partOf'):
                        edges.add(wp['partOf'])
                    if wp.get('mapsTo'):
                        edges.add(wp['mapsTo'])
                    if edges:
                        wp_edges[wp['name']] = edges

        reported_cycles = set()
        for start_name in wp_edges:
            stack = [(start_name, {start_name})]
            while stack:
                current, visited = stack.pop()
                for neighbor in wp_edges.get(current, set()):
                    if neighbor in visited:
                        cycle_key = frozenset(visited | {neighbor})
                        if cycle_key not in reported_cycles:
                            reported_cycles.add(cycle_key)
                            self.errors.append({
                                "category": "integrity",
                                "severity": "error",
                                "path": "workProducts",
                                "issue": f"Circular partOf/mapsTo chain detected involving work product '{start_name}'",
                                "expected": "Acyclic partOf/mapsTo relationships",
                                "actual": f"Cycle: {start_name} -> {' -> '.join(sorted(visited - {start_name}))} -> {neighbor}",
                                "suggestion": "Remove one partOf or mapsTo reference to break the cycle"
                            })
                            has_errors = True
                    elif neighbor in wp_edges:
                        stack.append((neighbor, visited | {neighbor}))

        return not has_errors

    def generate_report(self) -> Dict:
        """Generate structured validation report"""
        return {
            "practice_file": str(self.practice_file),
            "baseline_file": str(self.baseline_file),
            "schema_file": str(self.schema_file),
            "dependency_files": [str(f) for f in self.dependency_files],
            "valid": len(self.errors) == 0,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "schema": sum(1 for e in self.errors if e['category'] == 'schema'),
                "baseline": sum(1 for e in self.errors if e['category'] == 'baseline'),
                "integrity": sum(1 for e in self.errors if e['category'] == 'integrity'),
                "acyclicity": sum(1 for e in self.errors if e['category'] == 'acyclicity'),
                "bindings": sum(1 for e in self.errors if e['category'] == 'bindings'),
                "semantic": sum(1 for w in self.warnings if w['category'] == 'semantic'),
                "outcomes": sum(1 for e in self.errors if e['category'] == 'outcomes')
            }
        }

    def validate_work_product_purpose(self) -> bool:
        """Validate work product purpose hub: contributesToAlphaNames and LOD contributesTo coherence"""
        has_errors = False

        is_method = 'practices' in self.practice or 'baselinePractice' in self.practice
        practices = self.practice.get('practices', []) if is_method else [self.practice]

        all_alphas = set(self.baseline_alphas.keys()) | set(self.dep_alphas.keys())
        for practice in practices:
            for alpha in practice.get('alphas', []):
                all_alphas.add(alpha['name'])

        for practice_idx, practice in enumerate(practices):
            prefix = f"practices[{practice_idx}]" if is_method else ""
            practice_name = practice.get('name')
            has_cross_practice_deps = bool(practice.get('practiceDependencyNames', []))

            for wp_idx, wp in enumerate(practice.get('workProducts', [])):
                wp_path = f"{prefix}.workProducts[{wp_idx}]" if prefix else f"workProducts[{wp_idx}]"
                wp_name = wp.get('name', f'workProduct[{wp_idx}]')
                wp_alpha_names = wp.get('contributesToAlphaNames', [])
                has_wp_purpose = bool(wp_alpha_names)

                lod_alpha_names = set()
                any_lod_has_contributes_to = False
                for lod in wp.get('levelsOfDetail', []):
                    contributes_to = lod.get('contributesTo', [])
                    if contributes_to:
                        any_lod_has_contributes_to = True
                        for contrib in contributes_to:
                            alpha_name = contrib.get('alphaName')
                            if alpha_name:
                                lod_alpha_names.add(alpha_name)

                # Floating WP check: must have purpose via contributesToAlphaNames or LOD contributesTo
                if not has_wp_purpose and not any_lod_has_contributes_to:
                    # Skip if this is a baseline redeclaration (name exists in baseline)
                    baseline_wp_names = set()
                    for bl in self._resolve_baseline_chain():
                        for bwp in bl.get('workProducts', []):
                            baseline_wp_names.add(bwp['name'])
                    if wp_name not in baseline_wp_names:
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": wp_path,
                            "issue": f"Floating work product '{wp_name}': no contributesToAlphaNames and no LOD has contributesTo",
                            "expected": "contributesToAlphaNames array OR at least one LOD with non-empty contributesTo",
                            "actual": "No alpha purpose declared",
                            "suggestion": f"Add contributesToAlphaNames listing the alphas this work product serves, or add contributesTo on at least one LOD"
                        })
                        has_errors = True

                # Alpha existence: every name in contributesToAlphaNames must resolve
                if has_wp_purpose and not has_cross_practice_deps:
                    for name_idx, alpha_name in enumerate(wp_alpha_names):
                        if alpha_name not in all_alphas:
                            self.errors.append({
                                "category": "integrity",
                                "severity": "error",
                                "path": f"{wp_path}.contributesToAlphaNames[{name_idx}]",
                                "issue": f"contributesToAlphaNames references undefined alpha: '{alpha_name}'",
                                "expected": f"One of: {sorted(all_alphas)}",
                                "actual": alpha_name,
                                "suggestion": "Use exact alpha name (case-sensitive)"
                            })
                            has_errors = True

                # LOD ⊆ WP check: LOD alphaNames must be subset of contributesToAlphaNames
                if has_wp_purpose and lod_alpha_names:
                    wp_alpha_set = set(wp_alpha_names)
                    missing = lod_alpha_names - wp_alpha_set
                    if missing:
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": f"{wp_path}.contributesToAlphaNames",
                            "issue": f"LOD contributesTo references alphas not in contributesToAlphaNames: {sorted(missing)}",
                            "expected": f"contributesToAlphaNames must be superset of all LOD alphaNames",
                            "actual": f"WP alphas: {sorted(wp_alpha_set)}, LOD alphas: {sorted(lod_alpha_names)}",
                            "suggestion": f"Add {sorted(missing)} to contributesToAlphaNames"
                        })
                        has_errors = True

        return not has_errors

    # Practice element collections that carry PracticeElement properties. Used by the
    # specificity and suppression checks, which apply to every element kind rather than
    # to one type, because `specificityName` and `suppressed` are declared on
    # PracticeElement and so reach all 31 types that extend it.
    ELEMENT_COLLECTIONS = [
        'focuses', 'alphas', 'alphaInstances', 'workProductInstances', 'activitySpaces',
        'competencies', 'activities', 'workProducts', 'personas', 'personaGroups',
        'narrativeTypes', 'patterns', 'patternGroups', 'outcomes',
    ]

    def _inherited_element_names(self) -> Dict[str, set]:
        """Names available through the baseline chain and dependency practices, by collection.

        An element whose name appears here is a redeclaration; one that does not is
        net-new. Parts (states, levels of detail, checklists) are collected under
        synthetic keys so the same lookup serves them.
        """
        if getattr(self, '_inherited_cache', None) is not None:
            return self._inherited_cache

        inherited = defaultdict(set)
        for doc in self._resolve_baseline_chain() + self.dependencies:
            for collection in self.ELEMENT_COLLECTIONS:
                for element in doc.get(collection, []):
                    if not isinstance(element, dict) or 'name' not in element:
                        continue
                    inherited[collection].add(element['name'])
                    for state in element.get('states', []):
                        if isinstance(state, dict) and 'name' in state:
                            inherited['states'].add(f"{element['name']}::{state['name']}")
                    for lod in element.get('levelsOfDetail', []):
                        if isinstance(lod, dict) and 'name' in lod:
                            inherited['levelsOfDetail'].add(f"{element['name']}::{lod['name']}")

        self._inherited_cache = inherited
        return inherited

    def _walk_elements(self):
        """Yield (practice, path, collection, element) for every practice element.

        Covers methods (which nest practices) and single practices alike, so a check
        written against this walker applies to both without special-casing.
        """
        is_method = 'practices' in self.practice or 'baselinePractice' in self.practice
        practices = self.practice.get('practices', []) if is_method else [self.practice]
        for practice_idx, practice in enumerate(practices):
            prefix = f"practices[{practice_idx}]." if is_method else ""
            for collection in self.ELEMENT_COLLECTIONS:
                for idx, element in enumerate(practice.get(collection, [])):
                    if isinstance(element, dict):
                        yield practice, f"{prefix}{collection}[{idx}]", collection, element

    def validate_specificity(self) -> bool:
        """Validate specificityName placement and reject author-declared specificity.

        See semantics/composition.md section 4.5.1. `specificityName` names the dimension
        of specificity a redeclaration adds; `specificity` is the chain the merge
        accumulates across the practices actually loaded, so an authored value cannot
        know what it should contain.
        """
        has_errors = False
        inherited = self._inherited_element_names()

        for root_property in ('specificityName', 'specificity'):
            if root_property in self.practice:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": root_property,
                    "issue": f"'{root_property}' declared on the document root",
                    "expected": "specificity applies to practice elements, not to the document",
                    "actual": f"root.{root_property} is present",
                    "suggestion": f"Remove '{root_property}' from the document root"
                })
                has_errors = True

        for practice, path, collection, element in self._walk_elements():
            name = element.get('name', '<unnamed>')

            if 'specificity' in element:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"{path}.specificity",
                    "issue": f"'{name}' declares 'specificity', which is populated by the merge",
                    "expected": "specificity is merge output; authors declare specificityName",
                    "actual": f"specificity: {element.get('specificity')}",
                    "suggestion": "Remove 'specificity' and declare 'specificityName' with this practice's own contribution"
                })
                has_errors = True

            specificity_name = element.get('specificityName')
            if specificity_name is None:
                continue

            if not str(specificity_name).strip():
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"{path}.specificityName",
                    "issue": f"'{name}' declares an empty specificityName",
                    "expected": "a non-empty dimension of specificity, or the property omitted",
                    "actual": repr(specificity_name),
                    "suggestion": "Name the specificity this redeclaration adds, or remove the property"
                })
                has_errors = True
                continue

            if name not in inherited.get(collection, set()):
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"{path}.specificityName",
                    "issue": f"'{name}' is not a redeclaration, so it cannot add specificity",
                    "expected": "specificityName only on an element inherited through the baseline or a dependency",
                    "actual": f"'{name}' is declared new in this practice",
                    "suggestion": f"Remove specificityName from '{name}', or name it after the inherited element it makes more specific"
                })
                has_errors = True

        return not has_errors

    def _precedence_order(self) -> List[str]:
        """Declaration precedence for suppression conflicts, highest precedence first.

        Baselines outrank practices; within each group, declaration order decides. A
        practice from another baseline family takes the position of its own baseline,
        which is what makes two practices from different families comparable at all.
        See semantics/composition.md section 4.9.1.
        """
        order = []
        for baseline in reversed(self._resolve_baseline_chain()):
            name = baseline.get('name')
            if name and name not in order:
                order.append(name)
            for parent in baseline.get('baselinePracticeNames', []):
                if parent not in order:
                    order.append(parent)

        baseline_position = {name: idx for idx, name in enumerate(order)}
        practices = []
        for dep in self.dependencies:
            name = dep.get('name')
            if not name:
                continue
            # A dependency's rank is its own baseline's rank, then its declaration order.
            rank = baseline_position.get(dep.get('baselinePracticeName'), len(order))
            practices.append((rank, len(practices), name))
        order.extend(name for _, _, name in sorted(practices))

        own = self.practice.get('name')
        if own and own not in order:
            order.append(own)
        return order

    def validate_suppression(self) -> bool:
        """Validate that suppressed elements are inherited and leave nothing dangling.

        See semantics/composition.md section 4.9. One property on PracticeElement covers
        whole elements and parts alike, because every part type extends PracticeElement.
        """
        has_errors = False
        inherited = self._inherited_element_names()

        if 'suppressed' in self.practice:
            self.errors.append({
                "category": "integrity",
                "severity": "error",
                "path": "suppressed",
                "issue": "'suppressed' declared on the document root",
                "expected": "suppression applies to inherited practice elements, not to the document",
                "actual": "root.suppressed is present",
                "suggestion": "Remove 'suppressed' from the document root"
            })
            has_errors = True

        suppressed_states = set()
        suppressed_lods = set()
        suppressed_elements = set()

        for practice, path, collection, element in self._walk_elements():
            name = element.get('name', '<unnamed>')

            if element.get('suppressed') is True:
                suppressed_elements.add((collection, name))
                if name not in inherited.get(collection, set()):
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": f"{path}.suppressed",
                        "issue": f"'{name}' is not inherited, so there is nothing to suppress",
                        "expected": "suppressed only on an element inherited through the baseline chain or a dependency",
                        "actual": f"'{name}' is declared by this practice itself",
                        "suggestion": f"Remove the declaration of '{name}' rather than suppressing it"
                    })
                    has_errors = True

            # Parts: states and levels of detail carry the same property.
            for part_key, part_collection, bucket in (
                ('states', 'states', suppressed_states),
                ('levelsOfDetail', 'levelsOfDetail', suppressed_lods),
            ):
                for part_idx, part in enumerate(element.get(part_key, [])):
                    if not isinstance(part, dict) or part.get('suppressed') is not True:
                        continue
                    part_name = part.get('name', f'{part_key}[{part_idx}]')
                    bucket.add((name, part_name))
                    if f"{name}::{part_name}" not in inherited.get(part_collection, set()):
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": f"{path}.{part_key}[{part_idx}].suppressed",
                            "issue": f"'{part_name}' on '{name}' is not inherited, so there is nothing to suppress",
                            "expected": "suppressed only on a part inherited through the baseline chain or a dependency",
                            "actual": f"'{part_name}' is declared by this practice itself",
                            "suggestion": f"Remove '{part_name}' rather than suppressing it"
                        })
                        has_errors = True

        if not (suppressed_states or suppressed_lods or suppressed_elements):
            return not has_errors

        # Anything still pointing at a suppressed element or part is dangling once the
        # merge removes it. Reporting it here is the whole value of the check: the
        # author suppressing an element is the person who can fix the references.
        has_errors |= self._report_suppressed_references(
            suppressed_elements, suppressed_states, suppressed_lods)
        return not has_errors

    def _report_suppressed_references(self, elements, states, lods) -> bool:
        """Report references into suppressed elements and parts."""
        found = False
        suppressed_alphas = {name for collection, name in elements if collection == 'alphas'}
        suppressed_wps = {name for collection, name in elements if collection == 'workProducts'}

        is_method = 'practices' in self.practice or 'baselinePractice' in self.practice
        practices = self.practice.get('practices', []) if is_method else [self.practice]

        def flag(path, what, referenced_by):
            nonlocal found
            self.errors.append({
                "category": "integrity",
                "severity": "error",
                "path": path,
                "issue": f"{referenced_by} references {what}, which this practice suppresses",
                "expected": "no reference to a suppressed element or part survives the merge",
                "actual": what,
                "suggestion": "Remove the reference, or do not suppress what is still needed"
            })
            found = True

        for practice_idx, practice in enumerate(practices):
            prefix = f"practices[{practice_idx}]." if is_method else ""
            for p_idx, pattern in enumerate(practice.get('patterns', [])):
                for v_idx, view in enumerate(pattern.get('patternViews', [])):
                    for a_idx, entry in enumerate(view.get('alphaStates', [])):
                        if not isinstance(entry, dict):
                            continue
                        alpha_name = entry.get('alphaName')
                        state_name = entry.get('stateName')
                        path = f"{prefix}patterns[{p_idx}].patternViews[{v_idx}].alphaStates[{a_idx}]"
                        if alpha_name in suppressed_alphas:
                            flag(path, f"suppressed alpha '{alpha_name}'", "Pattern view")
                        elif (alpha_name, state_name) in states:
                            flag(path, f"suppressed state '{alpha_name}::{state_name}'", "Pattern view")

            for o_idx, outcome in enumerate(practice.get('outcomes', [])):
                for m_idx, mc in enumerate(outcome.get('metricContributions', [])):
                    alpha_name = mc.get('alphaName')
                    base = f"{prefix}outcomes[{o_idx}].metricContributions[{m_idx}]"
                    if alpha_name in suppressed_alphas:
                        flag(base, f"suppressed alpha '{alpha_name}'", "Outcome metric contribution")
                    for w_idx, weight in enumerate(mc.get('forecastWeights', [])):
                        if (alpha_name, weight.get('stateName')) in states:
                            flag(f"{base}.forecastWeights[{w_idx}]",
                                 f"suppressed state '{alpha_name}::{weight.get('stateName')}'",
                                 "Forecast weight")

            for a_idx, activity in enumerate(practice.get('activities', [])):
                for w_idx, works in enumerate(activity.get('worksOn', [])):
                    wp_name = works.get('workProductName')
                    path = f"{prefix}activities[{a_idx}].worksOn[{w_idx}]"
                    if wp_name in suppressed_wps:
                        flag(path, f"suppressed work product '{wp_name}'", "Activity worksOn")
                    elif (wp_name, works.get('levelOfDetailName')) in lods:
                        flag(path,
                             f"suppressed level of detail '{wp_name}::{works.get('levelOfDetailName')}'",
                             "Activity worksOn")

        return found

    def validate_loops(self) -> bool:
        """Validate loopsBackTo edges on pattern views and alpha states.

        Deliberately thin. This is a semantics change, not a validation one, so the
        only job here is that the edge points somewhere real and backwards. No check
        may treat a loop as a defect -- see semantics/execution-and-patterns.md 9.2a
        and semantics/alphas.md 6.8.
        """
        has_errors = False

        def check(container_kind, container_name, siblings, link_key, path):
            """Resolve one loopsBackTo edge against its sibling set."""
            nonlocal has_errors
            by_name = {}
            for sibling in siblings:
                if isinstance(sibling, dict) and 'name' in sibling:
                    by_name[sibling['name']] = sibling

            for idx, sibling in enumerate(siblings):
                if not isinstance(sibling, dict):
                    continue
                loop = sibling.get('loopsBackTo')
                if not isinstance(loop, dict):
                    continue
                here = sibling.get('name', f'[{idx}]')
                target_name = loop.get(link_key)
                loop_path = f"{path}[{idx}].loopsBackTo"

                target = by_name.get(target_name)
                if target is None:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": f"{loop_path}.{link_key}",
                        "issue": f"'{here}' loops back to '{target_name}', which is not in {container_kind} '{container_name}'",
                        "expected": f"a {link_key} naming a sibling of '{here}'",
                        "actual": target_name,
                        "suggestion": f"Name one of: {sorted(by_name)}"
                    })
                    has_errors = True
                    continue

                if target_name == here:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": f"{loop_path}.{link_key}",
                        "issue": f"'{here}' loops back to itself",
                        "expected": "a loop spans at least two entries",
                        "actual": target_name,
                        "suggestion": "Point the loop at the entry the cycle restarts from"
                    })
                    has_errors = True
                    continue

                here_seq = sibling.get('seq')
                target_seq = target.get('seq')
                if isinstance(here_seq, int) and isinstance(target_seq, int) and target_seq >= here_seq:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": f"{loop_path}.{link_key}",
                        "issue": f"'{here}' loops back to '{target_name}', which does not come earlier",
                        "expected": f"target seq lower than {here_seq}",
                        "actual": f"'{target_name}' has seq {target_seq}",
                        "suggestion": "A loop returns to an earlier entry; check the seq values"
                    })
                    has_errors = True

        for practice, path, collection, element in self._walk_elements():
            name = element.get('name', '<unnamed>')
            if collection == 'alphas':
                check('alpha', name, element.get('states', []), 'stateName', f"{path}.states")
            elif collection == 'patterns':
                check('pattern', name, element.get('patternViews', []),
                      'patternViewName', f"{path}.patternViews")

        return not has_errors

    def _narrative_elements_in_scope(self) -> Dict[str, set]:
        """NarrativeType.name -> set of its NarrativeElement names, across the whole scope."""
        if getattr(self, '_narrative_cache', None) is not None:
            return self._narrative_cache

        types = defaultdict(set)
        is_method = 'practices' in self.practice or 'baselinePractice' in self.practice
        own = self.practice.get('practices', []) if is_method else [self.practice]
        for doc in self._resolve_baseline_chain() + self.dependencies + own:
            for nt in doc.get('narrativeTypes', []):
                if not isinstance(nt, dict) or 'name' not in nt:
                    continue
                for ne in nt.get('narrativeElements', []):
                    if isinstance(ne, dict) and 'name' in ne:
                        types[nt['name']].add(ne['name'])
        self._narrative_cache = types
        return types

    def _check_narrative_contexts(self, contexts, narrative_type_name, owner, path,
                                  severity="error") -> bool:
        """Contexts must name elements of the NarrativeType declared on their parent.

        Section 9.2 has always required this for pattern views and nothing enforced it.
        Retrofitting it as an error would invalidate documents that have been valid for
        as long as the rule has existed, so pattern views get a warning and the migration
        path, while orchestration stages -- a construct with no installed base -- are
        held to it from the start. Both report the same defect; only the severity differs.
        """
        if not contexts:
            return False
        has_errors = False
        types = self._narrative_elements_in_scope()
        sink = self.errors if severity == "error" else self.warnings

        def report(entry):
            entry["severity"] = severity
            sink.append(entry)
            return severity == "error"

        if not narrative_type_name:
            return report({
                "category": "integrity",
                "path": path,
                "issue": f"'{owner}' declares narrativeContexts but its parent declares no narrativeTypeName",
                "expected": "narrative contexts resolve against a declared narrative type",
                "actual": "no narrativeTypeName on the parent",
                "suggestion": "Declare narrativeTypeName on the parent, or remove the narrativeContexts"
            })

        known = types.get(narrative_type_name)
        if known is None:
            return report({
                "category": "integrity",
                "path": path,
                "issue": f"Narrative type '{narrative_type_name}' is not in scope",
                "expected": "a NarrativeType declared in the baseline chain, a dependency, or this document",
                "actual": narrative_type_name,
                "suggestion": f"Declare it, or name one of: {sorted(types)}"
            })

        for idx, context in enumerate(contexts):
            if not isinstance(context, dict):
                continue
            element_name = context.get('narrativeElementName')
            if element_name not in known:
                has_errors |= report({
                    "category": "integrity",
                    "path": f"{path}[{idx}].narrativeElementName",
                    "issue": f"'{element_name}' is not an element of narrative type '{narrative_type_name}'",
                    "expected": f"one of: {sorted(known)}",
                    "actual": element_name,
                    "suggestion": f"Name an element of '{narrative_type_name}', or change the parent's narrativeTypeName"
                })
        return has_errors

    def _practice_documents_in_scope(self, own):
        """Documents whose patterns and orchestrations a symbolic link may name.

        Same scope every other symbolic link resolves against -- the baseline chain,
        declared dependencies, and this document. Mirrors _narrative_elements_in_scope.
        A method's constituent practices are unwrapped so their elements resolve too.

        Used by orchestration stage targets and by outcome contributions, which the
        semantics give the same scope.
        """
        docs = []
        for doc in self._resolve_baseline_chain() + self.dependencies + list(own):
            if not isinstance(doc, dict):
                continue
            docs.append(doc)
            for inner in doc.get('practices', []):
                if isinstance(inner, dict):
                    docs.append(inner)
        return docs

    def _patterns_in_scope(self, own) -> Dict[str, tuple]:
        """Pattern.name -> (pattern object, owning document name)."""
        found = {}
        for doc in self._practice_documents_in_scope(own):
            owner = doc.get('name', '<unnamed>')
            for pattern in doc.get('patterns', []):
                if isinstance(pattern, dict) and 'name' in pattern:
                    found.setdefault(pattern['name'], (pattern, owner))
        return found

    def _orchestrations_in_scope(self, own) -> Dict[str, tuple]:
        """PatternOrchestration.name -> (orchestration object, owning document name).

        First writer wins, matching the merge rule in merge.md 6.15a: where a practice
        extends an orchestration it inherits, the inherited declaration is the owner.
        """
        found = {}
        for doc in self._practice_documents_in_scope(own):
            owner = doc.get('name', '<unnamed>')
            for orch in doc.get('patternOrchestrations', []):
                if isinstance(orch, dict) and 'name' in orch:
                    found.setdefault(orch['name'], (orch, owner))
        return found

    def _merged_orchestration_stages(self, name, own):
        """Every stage declared under `name` anywhere in scope, keyed by identity.

        An orchestration merges by name across the baseline chain, declared
        dependencies and this document (merge.md 6.15a), so anything referencing a
        stage resolves against the merge rather than against whichever declaration
        happened to be found first. A baseline shell carries no stages at all, and
        reading only that would hide every stage a dependency contributed.

        Keyed by (target, host) with the first writer winning, as the merge does.
        Differs from _inherited_orchestration, which deliberately excludes this
        document's own declaration because that is the thing being checked.
        """
        merged = {}
        for doc in self._practice_documents_in_scope(own):
            for orch in doc.get('patternOrchestrations', []):
                if not isinstance(orch, dict) or orch.get('name') != name:
                    continue
                for stage in orch.get('stages', []):
                    if isinstance(stage, dict):
                        key = (self._stage_target(stage), self._stage_host(stage))
                        merged.setdefault(key, stage)
        return merged

    def _resolve_stage_ref(self, ref, merged_stages):
        """The stage a StageRef names, or None.

        A StageRef is the identity of a stage rather than a search for one: target
        plus host, the same key the merge uses, so resolution is a lookup and the
        reference means the same stage to every consumer. A target-only reference
        would have to carry a rule for what happens when one pattern is placed
        twice -- nested in a plan and also available on demand, which semantics
        9.5.3 permits -- and two implementations of that rule can disagree. The
        on-demand placement also has no host, so under a target-only reference with
        a disambiguator it could not be named at all.

        A StageRef has the same shape as the identifying half of a stage, so the
        stage accessors read it directly.
        """
        if not isinstance(ref, dict):
            return None
        key = (self._stage_target(ref), self._stage_host(ref))
        return merged_stages.get(key)

    @staticmethod
    def _describe_stage_ref(ref):
        """A StageRef as it reads in a message."""
        kind, name = PracticeValidator._stage_target(ref)
        host_kind, host_name = PracticeValidator._stage_host(ref)
        text = f"{kind} '{name}'"
        if host_name:
            text += f" against {host_kind} '{host_name}'"
        return text

    @staticmethod
    def _stage_target(stage):
        """(kind, name) for what a stage places -- 'pattern' or 'orchestration'."""
        if stage.get('orchestrationName'):
            return 'orchestration', stage['orchestrationName']
        return 'pattern', stage.get('patternName')

    @staticmethod
    def _stage_host(stage):
        """(kind, name) for what a stage is placed against, or (None, None)."""
        rel = stage.get('relativeTo') or {}
        if rel.get('orchestrationName'):
            return 'orchestration', rel['orchestrationName']
        if rel.get('patternName'):
            return 'pattern', rel['patternName']
        return None, None

    def _check_stage_host(self, stage, patterns, orchestrations,
                          orchestration_name, s_path, target_kind, target_name,
                          relationship) -> bool:
        """Resolve the host a concurrent or nested stage is placed against.

        See semantics/execution-and-patterns.md 9.5.1 and 9.5.4. The host must exist in
        scope, must not be the stage's own target, and any named views must belong to it.
        A host may be a pattern or an embedded orchestration.
        """
        has_errors = False
        host_kind, host_name = self._stage_host(stage)
        view_names = (stage.get('relativeTo') or {}).get('viewNames')
        prop = f"relativeTo.{'orchestrationName' if host_kind == 'orchestration' else 'patternName'}"
        known = orchestrations if host_kind == 'orchestration' else patterns

        if host_name not in known:
            self.errors.append({
                "category": "integrity",
                "severity": "error",
                "path": f"{s_path}.{prop}",
                "issue": f"Stage for '{target_name}' is {relationship} to unknown {host_kind} '{host_name}'",
                "expected": f"a {'PatternOrchestration' if host_kind == 'orchestration' else 'Pattern'} in scope to run alongside or inside",
                "actual": host_name,
                "suggestion": f"Name one of: {sorted(known)}"
            })
            return True

        if host_kind == target_kind and host_name == target_name:
            self.errors.append({
                "category": "integrity",
                "severity": "error",
                "path": f"{s_path}.{prop}",
                "issue": f"Stage for '{target_name}' in '{orchestration_name}' is placed relative to itself",
                "expected": f"a different {host_kind} as the host",
                "actual": host_name,
                "suggestion": "For a pattern whose own phases repeat, use loopsBackTo on the pattern rather than nesting it in itself"
            })
            return True

        if view_names and host_kind == 'orchestration':
            # shortcut: no stageNames property for scoping against part of a sub-endeavour,
            # upgrade when a document needs to run alongside some stages of a host
            # orchestration rather than all of it (semantics 9.5.4).
            self.errors.append({
                "category": "integrity",
                "severity": "error",
                "path": f"{s_path}.relativeTo.viewNames",
                "issue": f"viewNames is scoped to pattern views, but host '{host_name}' is an orchestration",
                "expected": "viewNames only where the host is a Pattern",
                "actual": f"{len(view_names)} view name(s) against an orchestration host",
                "suggestion": "Drop viewNames to place the stage against the whole sub-endeavour, or name a pattern as the host"
            })
            return True

        if host_kind == 'pattern':
            host = known[host_name][0]
            host_views = {v['name'] for v in host.get('patternViews', [])
                          if isinstance(v, dict) and 'name' in v}
            for view_name in (view_names or []):
                if view_name not in host_views:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": f"{s_path}.relativeTo.viewNames",
                        "issue": f"'{view_name}' is not a view of host pattern '{host_name}'",
                        "expected": f"one of: {sorted(host_views)}",
                        "actual": view_name,
                        "suggestion": f"Name a view of '{host_name}', or widen the scope by omitting viewNames"
                    })
                    has_errors = True
        return has_errors

    def _check_embedding_acyclic(self, orchestrations, prefix) -> bool:
        """No orchestration may embed itself, directly or through a chain.

        See semantics/acyclicity.md 14.1.8. Only OrchestrationStage.orchestrationName
        forms an edge -- relativeTo names a host within a shared orchestration, not a
        containment relationship, so it is not part of this graph.
        """
        has_errors = False
        reported = set()

        def walk(name, path, seen):
            nonlocal has_errors
            entry = orchestrations.get(name)
            if entry is None:
                return
            for stage in entry[0].get('stages', []):
                if not isinstance(stage, dict):
                    continue
                child = stage.get('orchestrationName')
                if not child:
                    continue
                if child in seen:
                    # Report each cycle once however it was entered: take the looping
                    # portion and rotate it to start at its smallest member.
                    loop = path[path.index(child):] if child in path else path
                    start = loop.index(min(loop))
                    rotated = loop[start:] + loop[:start]
                    cycle = " -> ".join(rotated + [rotated[0]])
                    if cycle not in reported:
                        reported.add(cycle)
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": f"{prefix}patternOrchestrations",
                            "issue": f"Orchestration embedding forms a cycle: {cycle}",
                            "expected": "the embedding graph is acyclic (acyclicity.md 14.1.8)",
                            "actual": cycle,
                            "suggestion": "Break the cycle. A pattern whose own phases repeat uses loopsBackTo, which is not an embedding"
                        })
                        has_errors = True
                    continue
                walk(child, path + [child], seen | {child})

        for name in sorted(orchestrations):
            walk(name, [name], {name})
        return has_errors

    def _inherited_orchestration(self, name, own_practice):
        """What this document inherits under `name`, as one merged declaration.

        Every in-scope declaration counts, not whichever is found first. A baseline
        commonly publishes an orchestration as an empty shell for extensions to fill
        (semantics 9.5.5), so the first match is routinely the one carrying no stages
        -- and returning it hid every stage a dependency had already contributed
        through the same name. The overlay checks then had nothing to measure an
        addition against, and an insertion into a sequence someone else owned
        validated clean.

        Stages merge by the composite key of merge.md 6.15a with the first writer
        winning, so documents are visited in merge order: the most foundational
        baseline first, then down the chain, then declared dependencies. The
        document's own declaration is the thing being checked, not the thing it
        extends, so it is skipped.
        """
        merged_stages = {}
        narrative_type = None
        found = False
        in_merge_order = list(reversed(self._resolve_baseline_chain())) + self.dependencies
        for doc in in_merge_order:
            if not isinstance(doc, dict):
                continue
            candidates = [doc] + [p for p in doc.get('practices', []) if isinstance(p, dict)]
            for candidate in candidates:
                if candidate is own_practice:
                    continue
                for orch in candidate.get('patternOrchestrations', []):
                    if not isinstance(orch, dict) or orch.get('name') != name:
                        continue
                    found = True
                    if narrative_type is None:
                        narrative_type = orch.get('narrativeTypeName')
                    for stage in orch.get('stages', []):
                        if not isinstance(stage, dict):
                            continue
                        key = (self._stage_target(stage), self._stage_host(stage))
                        merged_stages.setdefault(key, stage)
        if not found:
            return None
        merged = {"name": name, "stages": list(merged_stages.values())}
        if narrative_type:
            merged["narrativeTypeName"] = narrative_type
        return merged

    def _warn_foreign_pattern(self, pattern_name, patterns, orchestrations,
                              o_name, path) -> bool:
        """Advise embedding where a foreign pattern is already placed by its owner.

        See semantics/execution-and-patterns.md 9.5.4. Placing another document's
        pattern is permitted; where the owner has already placed it in an orchestration,
        embedding that orchestration keeps the ordering with its author and stays correct
        when the author changes it. Advice about which construct fits, so never an error.
        """
        owner = patterns.get(pattern_name, (None, None))[1]
        for other_name, (other, other_owner) in orchestrations.items():
            if other_name == o_name or other_owner != owner:
                continue
            for stage in other.get('stages', []):
                if isinstance(stage, dict) and stage.get('patternName') == pattern_name:
                    self.warnings.append({
                        "category": "integrity",
                        "severity": "warning",
                        "path": path,
                        "issue": f"'{pattern_name}' is owned by '{owner}' and already placed in orchestration '{other_name}'",
                        "expected": "embedding the orchestration that owns the ordering",
                        "actual": f"the pattern is placed directly in '{o_name}'",
                        "suggestion": f"Name orchestrationName '{other_name}' instead, so the ordering stays with its author and follows any change to it"
                    })
                    return False
        return False

    def _check_orchestration_overlay(self, orch, inherited, o_path, o_name) -> bool:
        """Extension by name is additive.

        See semantics/execution-and-patterns.md 9.5.5 and merge.md 6.15a. A practice
        redeclaring an orchestration it inherits contributes stages; it does not re-place
        the stages already there, and a sequential stage it adds appends rather than
        inserting into an order it does not own.
        """
        has_errors = False
        placement = ('seq', 'relationship', 'recurrence', 'relativeTo', 'trigger')

        inherited_stages = {}
        max_inherited_seq = None
        for stage in inherited.get('stages', []):
            if not isinstance(stage, dict):
                continue
            key = (self._stage_target(stage), self._stage_host(stage))
            inherited_stages[key] = stage
            if stage.get('relationship') == 'sequential':
                seq = stage.get('seq')
                if isinstance(seq, int):
                    max_inherited_seq = seq if max_inherited_seq is None else max(max_inherited_seq, seq)

        if orch.get('narrativeTypeName') and inherited.get('narrativeTypeName') \
                and orch['narrativeTypeName'] != inherited['narrativeTypeName']:
            self.errors.append({
                "category": "integrity",
                "severity": "error",
                "path": f"{o_path}.narrativeTypeName",
                "issue": f"'{o_name}' changes the narrative type of the orchestration it extends",
                "expected": f"'{inherited['narrativeTypeName']}', declared by the owner",
                "actual": orch['narrativeTypeName'],
                "suggestion": "Extension adds stages. For a different narrative spine, author a new orchestration"
            })
            has_errors = True

        for s_idx, stage in enumerate(orch.get('stages', [])):
            if not isinstance(stage, dict):
                continue
            s_path = f"{o_path}.stages[{s_idx}]"
            (_, target_name) = self._stage_target(stage)
            key = (self._stage_target(stage), self._stage_host(stage))
            prior = inherited_stages.get(key)

            if prior is not None:
                changed = [p for p in placement if p in stage and stage.get(p) != prior.get(p)]
                if changed:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": s_path,
                        "issue": f"'{target_name}' is already placed in '{o_name}' and this restates its {', '.join(changed)}",
                        "expected": "extension adds stages; the placement of an inherited stage belongs to its author",
                        "actual": ", ".join(f"{p}={stage.get(p)!r} (was {prior.get(p)!r})" for p in changed),
                        "suggestion": "Add your own stages instead, or author a new orchestration if the shape itself differs"
                    })
                    has_errors = True
                continue

            if stage.get('relationship') == 'sequential' and max_inherited_seq is not None \
                    and isinstance(stage.get('seq'), int) and stage['seq'] <= max_inherited_seq:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"{s_path}.seq",
                    "issue": f"Sequential stage for '{target_name}' inserts into the inherited order of '{o_name}'",
                    "expected": f"seq greater than {max_inherited_seq}, the last inherited sequential stage",
                    "actual": f"seq {stage['seq']}",
                    "suggestion": "Append after the inherited sequence, place the stage concurrent/nested/onDemand against it, or author a new orchestration"
                })
                has_errors = True
        return has_errors

    def validate_orchestrations(self) -> bool:
        """Validate pattern orchestrations, and narrative binding on patterns too.

        See semantics/execution-and-patterns.md section 9.5. The narrative-resolution
        check is shared with patterns because the rule is the same one level down and
        has never been enforced there either.
        """
        has_errors = False
        is_method = 'practices' in self.practice or 'baselinePractice' in self.practice
        practices = self.practice.get('practices', []) if is_method else [self.practice]

        # Both kinds of stage target resolve across the baseline chain and declared
        # dependencies, as every other symbolic link does (semantics 9.5.4).
        own = practices if is_method else [self.practice]
        patterns_in_scope = self._patterns_in_scope(own)
        orchestrations_in_scope = self._orchestrations_in_scope(own)

        # Once over the whole in-scope graph, not once per practice -- the graph spans
        # documents, so repeating it per practice would report each cycle many times.
        has_errors |= self._check_embedding_acyclic(orchestrations_in_scope, "")

        # seq is unique among the sequential stages of the merged orchestration, so
        # the pool spans every practice contributing to a name rather than resetting
        # per practice. Sibling practices of a method are not in one another's
        # dependencies, so nothing else sees two of them taking the same position.
        # Keyed by orchestration name: {name: {seq: path of the first stage there}}.
        method_sequential_seq = defaultdict(dict)

        for practice_idx, practice in enumerate(practices):
            prefix = f"practices[{practice_idx}]." if is_method else ""
            local_patterns = {p['name'] for p in practice.get('patterns', [])
                              if isinstance(p, dict) and 'name' in p}

            # Shared rule, applied to patterns: section 9.2 required this already.
            for p_idx, pattern in enumerate(practice.get('patterns', [])):
                for v_idx, view in enumerate(pattern.get('patternViews', [])):
                    has_errors |= self._check_narrative_contexts(
                        view.get('narrativeContexts'),
                        pattern.get('narrativeTypeName'),
                        view.get('name', f'view[{v_idx}]'),
                        f"{prefix}patterns[{p_idx}].patternViews[{v_idx}].narrativeContexts",
                        severity="warning")

            for o_idx, orch in enumerate(practice.get('patternOrchestrations', [])):
                o_path = f"{prefix}patternOrchestrations[{o_idx}]"
                o_name = orch.get('name', f'orchestration[{o_idx}]')
                # Placement collisions stay per document: two practices declaring the
                # same target the same way is a legitimate merge under 6.15a, first
                # writer winning, not a clash. A shared seq is a clash.
                placements = {}
                sequential_seq = method_sequential_seq[o_name]

                # Extension by name is additive (semantics 9.5.5, merge.md 6.15a).
                inherited = self._inherited_orchestration(o_name, practice)
                if inherited is not None:
                    has_errors |= self._check_orchestration_overlay(
                        orch, inherited, o_path, o_name)

                for s_idx, stage in enumerate(orch.get('stages', [])):
                    s_path = f"{o_path}.stages[{s_idx}]"
                    target_kind, target_name = self._stage_target(stage)
                    seq = stage.get('seq')
                    relationship = stage.get('relationship', 'sequential')
                    host_kind, host_name = self._stage_host(stage)
                    target_prop = 'orchestrationName' if target_kind == 'orchestration' else 'patternName'
                    known = orchestrations_in_scope if target_kind == 'orchestration' else patterns_in_scope

                    if target_name not in known:
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": f"{s_path}.{target_prop}",
                            "issue": f"Orchestration '{o_name}' stage references unknown {target_kind} '{target_name}'",
                            "expected": f"a {'PatternOrchestration' if target_kind == 'orchestration' else 'Pattern'} in scope",
                            "actual": target_name,
                            "suggestion": f"Name one of: {sorted(known)}"
                        })
                        has_errors = True
                    elif target_kind == 'orchestration' and target_name == o_name:
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": f"{s_path}.orchestrationName",
                            "issue": f"Orchestration '{o_name}' embeds itself",
                            "expected": "a different orchestration, or a pattern (acyclicity.md 14.1.8)",
                            "actual": target_name,
                            "suggestion": "Name the patterns directly, or embed an orchestration that does not lead back here"
                        })
                        has_errors = True
                    elif target_kind == 'pattern' and target_name not in local_patterns:
                        has_errors |= self._warn_foreign_pattern(
                            target_name, patterns_in_scope, orchestrations_in_scope,
                            o_name, f"{s_path}.patternName")

                    # A target may be placed more than once, but not the same way twice.
                    placement = (target_kind, target_name, relationship, host_kind, host_name)
                    if placement in placements:
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": f"{s_path}.{target_prop}",
                            "issue": f"{target_kind.capitalize()} '{target_name}' is placed the same way twice in orchestration '{o_name}'",
                            "expected": "a pattern or orchestration may be layered more than once, but each placement must differ",
                            "actual": f"{relationship}" + (f" relative to '{host_name}'" if host_name else "") +
                                      f", also at stages[{placements[placement]}]",
                            "suggestion": "Merge the two stages, or give them different relationships or hosts"
                        })
                        has_errors = True
                    else:
                        placements[placement] = s_idx

                    # seq is a strict order only among sequential stages. Concurrent,
                    # nested and on-demand stages may share a seq because they begin
                    # alongside one another -- concurrency has no total order.
                    if relationship == 'sequential':
                        if seq in sequential_seq:
                            self.errors.append({
                                "category": "integrity",
                                "severity": "error",
                                "path": f"{s_path}.seq",
                                "issue": f"Duplicate seq {seq} among sequential stages of '{o_name}'",
                                "expected": "seq unique among sequential stages",
                                "actual": f"also at {sequential_seq[seq]}",
                                "suggestion": "Renumber, or mark one stage concurrent if they genuinely run alongside"
                            })
                            has_errors = True
                        else:
                            sequential_seq[seq] = s_path

                    if relationship in ('concurrent', 'nested'):
                        has_errors |= self._check_stage_host(
                            stage, patterns_in_scope, orchestrations_in_scope,
                            o_name, s_path, target_kind, target_name, relationship)

                    if relationship != 'onDemand' and stage.get('trigger'):
                        self.warnings.append({
                            "category": "integrity",
                            "severity": "warning",
                            "path": f"{s_path}.trigger",
                            "issue": f"Stage for '{target_name}' declares a trigger but is {relationship}, not onDemand",
                            "expected": "a trigger is what causes an onDemand stage to be entered",
                            "actual": f"relationship: {relationship}",
                            "suggestion": "Mark the stage onDemand, or move the condition to entryCriteria"
                        })

                    if stage.get('recurrence') == 'perView':
                        if relationship not in ('concurrent', 'nested'):
                            self.warnings.append({
                                "category": "integrity",
                                "severity": "warning",
                                "path": f"{s_path}.recurrence",
                                "issue": f"Stage for '{target_name}' declares recurrence perView but is {relationship}",
                                "expected": "perView repeats a stage across the views of a host pattern",
                                "actual": f"relationship: {relationship}, no host pattern",
                                "suggestion": "Make the stage nested or concurrent against a host, or drop the recurrence"
                            })
                        elif host_kind == 'orchestration':
                            # shortcut: no perStage recurrence value, upgrade when a document
                            # needs a stage repeating per sub-stage of an orchestration host
                            # (semantics 9.5.4).
                            self.warnings.append({
                                "category": "integrity",
                                "severity": "warning",
                                "path": f"{s_path}.recurrence",
                                "issue": f"Stage for '{target_name}' declares perView against orchestration host '{host_name}'",
                                "expected": "perView restarts a stage for each view of a pattern host",
                                "actual": "the host is an orchestration, which has stages rather than views",
                                "suggestion": "Place the stage against a pattern of the host, or drop the recurrence"
                            })

                    has_errors |= self._check_narrative_contexts(
                        stage.get('narrativeContexts'),
                        orch.get('narrativeTypeName'),
                        f"stage {s_idx} of '{o_name}'",
                        f"{s_path}.narrativeContexts")

            if practice.get('patternGroups'):
                self.warnings.append({
                    "category": "deprecation",
                    "severity": "warning",
                    "path": f"{prefix}patternGroups",
                    "issue": "patternGroups is deprecated as of schema 2.21.0",
                    "expected": "patternOrchestrations, or grouping on the merge-stamped sourcePracticeName",
                    "actual": f"{len(practice['patternGroups'])} group(s) declared",
                    "suggestion": "Where the order means 'then', declare an orchestration; where it only showed which practice contributed a pattern, group on sourcePracticeName at display time. Still valid until the next major version."
                })

        return not has_errors

    def validate_semantic_alignment(self) -> bool:
        """
        Validate semantic appropriateness of contributesTo relationships.

        Uses state alignment heuristic to detect potentially incorrect contributesTo choices.
        Generates warnings (not errors) since semantic fit can be subjective.
        """
        practices = self.practice.get('practices', [self.practice])

        for practice in practices:
            practice_name = practice.get('name', 'Unknown')

            for alpha in practice.get('alphas', []):
                alpha_name = alpha.get('name', 'Unknown')
                contributes_to = alpha.get('contributesTo')

                # Only validate new alphas with contributesTo
                if not contributes_to:
                    continue

                # Get parent alpha from baseline or dependency
                all_parent_alphas = {**self.baseline_alphas, **self.dep_alphas}
                if contributes_to not in all_parent_alphas:
                    continue  # Already flagged by baseline validation

                parent_alpha = all_parent_alphas[contributes_to]
                parent_states = [s['name'] for s in parent_alpha.get('states', [])]
                child_states = [s['name'] for s in alpha.get('states', [])]

                # Calculate state alignment
                alignment_score, matches = self._calculate_state_alignment(child_states, parent_states)

                # Warn if alignment is weak
                if alignment_score < 0.5:  # <50% alignment
                    self.warnings.append({
                        'category': 'semantic',
                        'severity': 'warning',
                        'practice': practice_name,
                        'alpha': alpha_name,
                        'contributesTo': contributes_to,
                        'issue': f'Weak state alignment ({alignment_score:.0%}) between child and parent alpha',
                        'details': {
                            'child_states': child_states,
                            'parent_states': parent_states,
                            'matches': matches,
                            'alignment_score': f'{alignment_score:.0%}'
                        },
                        'suggestion': 'Review contributesTo decision using state alignment heuristic (references/semantics.md Section 9.2.5). Consider if different parent alpha is more semantically appropriate, or if this should be a redeclaration instead of specialization.'
                    })

                # Info if alignment is moderate (50-70%)
                elif alignment_score < 0.7:
                    self.warnings.append({
                        'category': 'semantic',
                        'severity': 'info',
                        'practice': practice_name,
                        'alpha': alpha_name,
                        'contributesTo': contributes_to,
                        'issue': f'Moderate state alignment ({alignment_score:.0%}) - verify semantic fit',
                        'details': {
                            'child_states': child_states,
                            'parent_states': parent_states,
                            'matches': matches,
                            'alignment_score': f'{alignment_score:.0%}'
                        },
                        'suggestion': 'State alignment is moderate. Verify that alpha description also aligns with parent description to confirm correct contributesTo choice.'
                    })

        # Concentration check: flag when multiple alphas target the same parent
        # with weak alignment — suggests the agent defaulted without evaluating alternatives
        for practice in practices:
            practice_name = practice.get('name', 'Unknown')
            target_counts = {}
            target_weak = {}
            all_parent_alphas = {**self.baseline_alphas, **self.dep_alphas}
            for alpha in practice.get('alphas', []):
                ct = alpha.get('contributesTo')
                if not ct:
                    continue
                alpha_name = alpha.get('name', 'Unknown')
                target_counts.setdefault(ct, []).append(alpha_name)
                if ct in all_parent_alphas:
                    parent_states = [s['name'] for s in all_parent_alphas[ct].get('states', [])]
                    child_states = [s['name'] for s in alpha.get('states', [])]
                    score, _ = self._calculate_state_alignment(child_states, parent_states)
                    if score < 0.25:
                        target_weak.setdefault(ct, []).append(alpha_name)

            for target, alphas_list in target_counts.items():
                weak_alphas = target_weak.get(target, [])
                if len(alphas_list) >= 3 and len(weak_alphas) >= 2:
                    self.warnings.append({
                        'category': 'semantic',
                        'severity': 'warning',
                        'practice': practice_name,
                        'issue': f'contributesTo concentration: {len(alphas_list)} alphas target '
                                 f'\'{target}\', {len(weak_alphas)} with <25% state alignment',
                        'details': {
                            'target': target,
                            'all_alphas': alphas_list,
                            'weak_alignment_alphas': weak_alphas,
                        },
                        'suggestion': 'Multiple alphas defaulting to the same parent with weak '
                                      'alignment suggests the target was not evaluated against '
                                      'alternatives. Review each alpha\'s contributesTo target '
                                      'independently.'
                    })

        return True  # Semantic validation never fails, only warns

    def validate_checklist_quality(self) -> bool:
        """
        Flag checklist items that are meta-statements referencing other checklist
        items rather than being independently assessable. Warnings only.
        """
        meta_patterns = [
            re.compile(r'\ball\b.*\brequirements?\b.*\bmet\b', re.IGNORECASE),
            re.compile(r'\bminimum\b.*\b(met|achieved|satisfied)\b', re.IGNORECASE),
            re.compile(r'\bcriteria\b.*\bsatisfied\b', re.IGNORECASE),
            re.compile(r'\bstandards?\b.*\bachieved\b', re.IGNORECASE),
            re.compile(r'\bpasses?\b.*\ball\b.*\bchecks?\b', re.IGNORECASE),
            re.compile(r'\b\d+\b.*\b(requirements?|criteria|standards?)\b.*\b(met|satisfied|achieved|completed)\b', re.IGNORECASE),
            re.compile(r'\ball\b.*\b(mandatory|required)\b.*\b(items?|fields?|elements?)\b.*\b(completed|met|present)\b', re.IGNORECASE),
        ]

        practices = self.practice.get('practices', [self.practice])

        for practice in practices:
            practice_name = practice.get('name', 'Unknown')

            for alpha in practice.get('alphas', []):
                alpha_name = alpha.get('name', 'Unknown')
                for state in alpha.get('states', []):
                    state_name = state.get('name', 'Unknown')
                    for ci, item in enumerate(state.get('checklist', [])):
                        text = f"{item.get('name', '')} {item.get('description', '')}"
                        for pattern in meta_patterns:
                            if pattern.search(text):
                                self.warnings.append({
                                    'category': 'semantic',
                                    'severity': 'warning',
                                    'practice': practice_name,
                                    'path': f"alphas[{alpha_name}].states[{state_name}].checklist[{ci}]",
                                    'issue': f"Meta-checklist item references other checklist items instead of being independently assessable: \"{item.get('name', '')}\"",
                                    'suggestion': 'Remove this item — the checklist IS the requirements. Items that summarise or count other items are circular.'
                                })
                                break

            for wp in practice.get('workProducts', []):
                wp_name = wp.get('name', 'Unknown')
                for lod in wp.get('levelsOfDetail', []):
                    lod_name = lod.get('name', 'Unknown')
                    for ci, item in enumerate(lod.get('checklist', [])):
                        text = f"{item.get('name', '')} {item.get('description', '')}"
                        for pattern in meta_patterns:
                            if pattern.search(text):
                                self.warnings.append({
                                    'category': 'semantic',
                                    'severity': 'warning',
                                    'practice': practice_name,
                                    'path': f"workProducts[{wp_name}].levelsOfDetail[{lod_name}].checklist[{ci}]",
                                    'issue': f"Meta-checklist item references other checklist items instead of being independently assessable: \"{item.get('name', '')}\"",
                                    'suggestion': 'Remove this item — the checklist IS the requirements. Items that summarise or count other items are circular.'
                                })
                                break

        return True  # Checklist quality never fails, only warns

    def _calculate_state_alignment(self, child_states: List[str], parent_states: List[str]) -> Tuple[float, List[str]]:
        """
        Calculate state alignment score using fuzzy matching.

        Returns (alignment_score, list_of_matches)
        alignment_score = matches / len(child_states)
        """
        if not child_states or not parent_states:
            return 0.0, []

        matches = []

        for child_state in child_states:
            # Exact match
            if child_state in parent_states:
                matches.append(f'{child_state} = {child_state} (exact)')
                continue

            # Fuzzy match (case-insensitive substring)
            child_lower = child_state.lower()
            for parent_state in parent_states:
                parent_lower = parent_state.lower()

                # Check for substring matches or common synonyms
                if (child_lower in parent_lower or parent_lower in child_lower or
                    self._are_synonyms(child_lower, parent_lower)):
                    matches.append(f'{child_state} ~ {parent_state} (semantic)')
                    break

        alignment_score = len(matches) / len(child_states) if child_states else 0.0
        return alignment_score, matches

    def _are_synonyms(self, state1: str, state2: str) -> bool:
        """Check if two state names are conceptual synonyms"""
        synonyms = [
            {'deployed', 'available', 'provisioned', 'operational'},
            {'scoped', 'defined', 'bounded'},
            {'optimized', 'evolved', 'mature', 'optimised'},
            {'functional', 'working', 'active', 'operational'},
            {'ready', 'prepared', 'enabled'},
            {'identified', 'recognized', 'discovered'},
        ]

        state1_words = set(state1.lower().split())
        state2_words = set(state2.lower().split())

        for synonym_set in synonyms:
            if state1_words & synonym_set and state2_words & synonym_set:
                return True

        return False

    def _validate_background(self, background: Dict, path: str,
                              all_alphas: set, all_alpha_states: Dict,
                              all_work_products: set, all_wp_lods: Dict,
                              all_alpha_instance_names: set, all_wp_instance_names: set,
                              has_cross_practice_deps: bool,
                              owner_alpha_name: str = None,
                              owner_wp_name: str = None) -> bool:
        """Validate cross-references within a Background object"""
        has_errors = False

        for idx, contrib in enumerate(background.get('alphaStates', [])):
            alpha_name = contrib.get('alphaName')
            state_name = contrib.get('stateName')
            ref_path = f"{path}.background.alphaStates[{idx}]"

            if alpha_name and owner_alpha_name and alpha_name == owner_alpha_name:
                self.warnings.append({
                    "category": "redundancy",
                    "severity": "warning",
                    "path": f"{ref_path}.alphaName",
                    "issue": f"Background references previous state of the same alpha '{alpha_name}' — sequential progression is implicit in seq ordering",
                    "expected": "Cross-alpha dependencies only",
                    "actual": alpha_name,
                    "suggestion": f"Remove self-referencing alphaState entry for '{alpha_name}'"
                })

            if alpha_name and alpha_name not in all_alphas and not has_cross_practice_deps:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"{ref_path}.alphaName",
                    "issue": f"Background references undefined alpha: '{alpha_name}'",
                    "expected": f"One of: {sorted(all_alphas)}",
                    "actual": alpha_name,
                    "suggestion": "Define alpha or correct reference"
                })
                has_errors = True

            if alpha_name and state_name and alpha_name in all_alpha_states:
                if state_name not in all_alpha_states.get(alpha_name, set()):
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": f"{ref_path}.stateName",
                        "issue": f"Background references undefined state '{state_name}' for alpha '{alpha_name}'",
                        "expected": f"One of: {sorted(all_alpha_states.get(alpha_name, set()))}",
                        "actual": state_name,
                        "suggestion": f"Check state names defined in {alpha_name} alpha"
                    })
                    has_errors = True

        for idx, contrib in enumerate(background.get('workProductLevels', [])):
            wp_name = contrib.get('workProductName')
            lod_name = contrib.get('levelOfDetailName')
            ref_path = f"{path}.background.workProductLevels[{idx}]"

            if wp_name and owner_wp_name and wp_name == owner_wp_name:
                self.warnings.append({
                    "category": "redundancy",
                    "severity": "warning",
                    "path": f"{ref_path}.workProductName",
                    "issue": f"Background references previous LOD of the same work product '{wp_name}' — sequential progression is implicit in seq ordering",
                    "expected": "Cross-work-product dependencies only",
                    "actual": wp_name,
                    "suggestion": f"Remove self-referencing workProductLevel entry for '{wp_name}'"
                })

            if wp_name and wp_name not in all_work_products:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"{ref_path}.workProductName",
                    "issue": f"Background references undefined work product: '{wp_name}'",
                    "expected": f"One of: {sorted(all_work_products)}",
                    "actual": wp_name,
                    "suggestion": "Define work product or correct reference"
                })
                has_errors = True

            if wp_name and lod_name and wp_name in all_wp_lods:
                if lod_name not in all_wp_lods.get(wp_name, set()):
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": f"{ref_path}.levelOfDetailName",
                        "issue": f"Background references undefined level '{lod_name}' for work product '{wp_name}'",
                        "expected": f"One of: {sorted(all_wp_lods.get(wp_name, set()))}",
                        "actual": lod_name,
                        "suggestion": f"Check level names defined in {wp_name} work product"
                    })
                    has_errors = True

        for idx, ref in enumerate(background.get('alphaInstanceStates', [])):
            inst_name = ref.get('instanceName')
            ref_path = f"{path}.background.alphaInstanceStates[{idx}]"

            if inst_name and inst_name not in all_alpha_instance_names and not has_cross_practice_deps:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"{ref_path}.instanceName",
                    "issue": f"Background references undefined alpha instance: '{inst_name}'",
                    "expected": f"One of: {sorted(all_alpha_instance_names)}",
                    "actual": inst_name,
                    "suggestion": "Define alpha instance name or correct reference"
                })
                has_errors = True

        for idx, ref in enumerate(background.get('workProductInstanceLevels', [])):
            inst_name = ref.get('instanceName')
            ref_path = f"{path}.background.workProductInstanceLevels[{idx}]"

            if inst_name and inst_name not in all_wp_instance_names and not has_cross_practice_deps:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"{ref_path}.instanceName",
                    "issue": f"Background references undefined work product instance: '{inst_name}'",
                    "expected": f"One of: {sorted(all_wp_instance_names)}",
                    "actual": inst_name,
                    "suggestion": "Define work product instance name or correct reference"
                })
                has_errors = True

        return has_errors

    def validate_backgrounds(self) -> bool:
        """Validate all background cross-references across the practice/method"""
        has_errors = False

        is_method = 'practices' in self.practice or 'baselinePractice' in self.practice
        practices = self.practice.get('practices', []) if is_method else [self.practice]

        all_alphas = set(self.baseline_alphas.keys()) | set(self.dep_alphas.keys())
        all_alpha_states = defaultdict(set)
        all_work_products = set()
        all_wp_lods = defaultdict(set)
        all_alpha_instance_names = set()
        all_wp_instance_names = set()

        for alpha_name in self.baseline_alpha_states:
            all_alpha_states[alpha_name].update(self.baseline_alpha_states[alpha_name])
        for alpha_name in self.dep_alpha_states:
            all_alpha_states[alpha_name].update(self.dep_alpha_states[alpha_name])

        # Index dependency practice elements for background validation
        for dep in self.dependencies:
            for wp in dep.get('workProducts', []):
                all_work_products.add(wp['name'])
                for lod in wp.get('levelsOfDetail', []):
                    all_wp_lods[wp['name']].add(lod['name'])

        for practice in practices:
            for alpha in practice.get('alphas', []):
                all_alphas.add(alpha['name'])
                for state in alpha.get('states', []):
                    all_alpha_states[alpha['name']].add(state['name'])
            for wp in practice.get('workProducts', []):
                all_work_products.add(wp['name'])
                for lod in wp.get('levelsOfDetail', []):
                    all_wp_lods[wp['name']].add(lod['name'])
            for ain in practice.get('alphaInstances', []):
                all_alpha_instance_names.add(ain['name'])
            for wpin in practice.get('workProductInstances', []):
                all_wp_instance_names.add(wpin['name'])

        for practice_idx, practice in enumerate(practices):
            prefix = f"practices[{practice_idx}]" if is_method else ""
            practice_name = practice.get('name')
            has_deps = bool(practice.get('practiceDependencyNames', []))

            for a_idx, alpha in enumerate(practice.get('alphas', [])):
                a_path = f"{prefix}.alphas[{a_idx}]" if prefix else f"alphas[{a_idx}]"
                for s_idx, state in enumerate(alpha.get('states', [])):
                    bg = state.get('background')
                    if bg:
                        s_path = f"{a_path}.states[{s_idx}]"
                        has_errors |= self._validate_background(
                            bg, s_path, all_alphas, all_alpha_states,
                            all_work_products, all_wp_lods,
                            all_alpha_instance_names, all_wp_instance_names, has_deps,
                            owner_alpha_name=alpha.get('name'))

            for wp_idx, wp in enumerate(practice.get('workProducts', [])):
                wp_path = f"{prefix}.workProducts[{wp_idx}]" if prefix else f"workProducts[{wp_idx}]"
                for lod_idx, lod in enumerate(wp.get('levelsOfDetail', [])):
                    bg = lod.get('background')
                    if bg:
                        lod_path = f"{wp_path}.levelsOfDetail[{lod_idx}]"
                        has_errors |= self._validate_background(
                            bg, lod_path, all_alphas, all_alpha_states,
                            all_work_products, all_wp_lods,
                            all_alpha_instance_names, all_wp_instance_names, has_deps,
                            owner_wp_name=wp.get('name'))

            for asp_idx, asp in enumerate(practice.get('activitySpaces', [])):
                asp_path = f"{prefix}.activitySpaces[{asp_idx}]" if prefix else f"activitySpaces[{asp_idx}]"
                bg = asp.get('background')
                if bg:
                    has_errors |= self._validate_background(
                        bg, asp_path, all_alphas, all_alpha_states,
                        all_work_products, all_wp_lods,
                        all_alpha_instance_names, all_wp_instance_names, has_deps)
                for act_idx, act in enumerate(asp.get('activities', [])):
                    act_bg = act.get('background')
                    if act_bg:
                        act_path = f"{asp_path}.activities[{act_idx}]"
                        has_errors |= self._validate_background(
                            act_bg, act_path, all_alphas, all_alpha_states,
                            all_work_products, all_wp_lods,
                            all_alpha_instance_names, all_wp_instance_names, has_deps)

            for act_idx, act in enumerate(practice.get('activities', [])):
                act_path = f"{prefix}.activities[{act_idx}]" if prefix else f"activities[{act_idx}]"
                act_bg = act.get('background')
                if act_bg:
                    has_errors |= self._validate_background(
                        act_bg, act_path, all_alphas, all_alpha_states,
                        all_work_products, all_wp_lods,
                        all_alpha_instance_names, all_wp_instance_names, has_deps)

        return not has_errors

    def _collect_instance_names(self, practice: Dict) -> Tuple[set, set]:
        alphas: set = set()
        wps: set = set()

        def _add(container, key, bucket):
            for inst in container.get(key) or []:
                if not isinstance(inst, dict):
                    continue
                n = inst.get("name") or inst.get("instanceName")
                if n:
                    bucket.add(n)

        _add(practice, "alphaInstances", alphas)
        _add(practice, "workProductInstances", wps)
        for pattern in practice.get("patterns") or []:
            if not isinstance(pattern, dict):
                continue
            _add(pattern, "alphaInstanceNames", alphas)
            _add(pattern, "workProductInstanceNames", wps)
            for view in pattern.get("patternViews") or []:
                if not isinstance(view, dict):
                    continue
                _add(view, "alphaInstances", alphas)
                _add(view, "workProductInstances", wps)
        _add(practice, "references", alphas)
        return alphas, wps

    def _validate_instance_relates_to(
        self,
        owner: Dict,
        owner_name: Optional[str],
        path: str,
        declared_alphas: set,
        declared_wps: set,
    ) -> bool:
        has_errors = False
        owner_name = (owner_name or "").strip()
        for idx, rel in enumerate(owner.get("relatesTo") or []):
            if not isinstance(rel, dict):
                continue
            rpath = f"{path}.relatesTo[{idx}]"
            alpha = str(rel.get("alphaInstanceName") or "").strip()
            wp = str(rel.get("workProductInstanceName") or "").strip()
            if bool(alpha) == bool(wp):
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": rpath,
                    "issue": "relatesTo must have exactly one of alphaInstanceName or workProductInstanceName",
                    "expected": "Exactly one target name field",
                    "actual": {
                        "alphaInstanceName": alpha or None,
                        "workProductInstanceName": wp or None,
                    },
                    "suggestion": "Set alphaInstanceName for a concern instance or workProductInstanceName for a work-product instance, not both or neither",
                })
                has_errors = True
                continue
            target = alpha or wp
            if owner_name and target == owner_name:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": rpath,
                    "issue": "relatesTo must not reference the declaring instance",
                    "expected": "A different named instance in this document",
                    "actual": target,
                    "suggestion": "Remove the self-link or point at another instance",
                })
                has_errors = True
            if alpha and declared_alphas and alpha not in declared_alphas:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"{rpath}.alphaInstanceName",
                    "issue": f"relatesTo references unknown alpha instance name '{alpha}'",
                    "expected": f"One of: {sorted(declared_alphas)}",
                    "actual": alpha,
                    "suggestion": "Use an AlphaInstanceName.name declared in this document",
                })
                has_errors = True
            if wp and declared_wps and wp not in declared_wps:
                self.errors.append({
                    "category": "integrity",
                    "severity": "error",
                    "path": f"{rpath}.workProductInstanceName",
                    "issue": f"relatesTo references unknown work product instance name '{wp}'",
                    "expected": f"One of: {sorted(declared_wps)}",
                    "actual": wp,
                    "suggestion": "Use a WorkProductInstanceName.name declared in this document",
                })
                has_errors = True
        return has_errors

    def _walk_instance_relates_to(
        self,
        practice: Dict,
        prefix: str,
        declared_alphas: set,
        declared_wps: set,
    ) -> bool:
        has_errors = False

        def _owner_name(inst):
            return inst.get("name") or inst.get("instanceName")

        def _check_list(container, key, path_base):
            nonlocal has_errors
            for i, inst in enumerate(container.get(key) or []):
                if not isinstance(inst, dict):
                    continue
                path = f"{path_base}[{i}]" if path_base else f"{key}[{i}]"
                has_errors |= self._validate_instance_relates_to(
                    inst, _owner_name(inst), path, declared_alphas, declared_wps
                )

        pfx = f"{prefix}." if prefix else ""
        _check_list(practice, "alphaInstances", f"{pfx}alphaInstances")
        _check_list(practice, "workProductInstances", f"{pfx}workProductInstances")
        _check_list(practice, "references", f"{pfx}references")
        for pidx, pattern in enumerate(practice.get("patterns") or []):
            if not isinstance(pattern, dict):
                continue
            ppath = f"{pfx}patterns[{pidx}]"
            _check_list(pattern, "alphaInstanceNames", f"{ppath}.alphaInstanceNames")
            _check_list(pattern, "workProductInstanceNames", f"{ppath}.workProductInstanceNames")
            for vidx, view in enumerate(pattern.get("patternViews") or []):
                if not isinstance(view, dict):
                    continue
                vpath = f"{ppath}.patternViews[{vidx}]"
                _check_list(view, "alphaInstances", f"{vpath}.alphaInstances")
                _check_list(view, "workProductInstances", f"{vpath}.workProductInstances")
        return has_errors

    def validate_instance_relationships(self) -> bool:
        """If example instances carry relatesTo, names must resolve within this document."""
        has_errors = False
        is_method = "practices" in self.practice or "baselinePractice" in self.practice
        practices = self.practice.get("practices", []) if is_method else [self.practice]

        declared_alphas: set = set()
        declared_wps: set = set()
        for practice in practices:
            a, w = self._collect_instance_names(practice)
            declared_alphas |= a
            declared_wps |= w
        if is_method:
            a, w = self._collect_instance_names(self.practice)
            declared_alphas |= a
            declared_wps |= w

        for practice_idx, practice in enumerate(practices):
            prefix = f"practices[{practice_idx}]" if is_method else ""
            has_errors |= self._walk_instance_relates_to(
                practice, prefix, declared_alphas, declared_wps
            )
        if is_method:
            has_errors |= self._walk_instance_relates_to(
                self.practice, "", declared_alphas, declared_wps
            )
        return not has_errors

    def validate_led_by(self) -> bool:
        """Validate ledBy references on activities and activity spaces resolve to a Persona.name in scope"""
        has_errors = False

        is_method = 'practices' in self.practice or 'baselinePractice' in self.practice
        practices = self.practice.get('practices', []) if is_method else [self.practice]

        all_personas = set()
        for dep in self.dependencies:
            for persona in dep.get('personas', []):
                all_personas.add(persona['name'])
        for practice in practices:
            for persona in practice.get('personas', []):
                all_personas.add(persona['name'])

        for practice_idx, practice in enumerate(practices):
            prefix = f"practices[{practice_idx}]" if is_method else ""
            has_deps = bool(practice.get('practiceDependencyNames', []))

            for asp_idx, asp in enumerate(practice.get('activitySpaces', [])):
                asp_path = f"{prefix}.activitySpaces[{asp_idx}]" if prefix else f"activitySpaces[{asp_idx}]"
                led_by = asp.get('ledBy')
                if led_by and led_by not in all_personas and not has_deps:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": f"{asp_path}.ledBy",
                        "issue": f"ledBy references undefined persona: '{led_by}'",
                        "expected": f"One of: {sorted(all_personas)}",
                        "actual": led_by,
                        "suggestion": "Define persona or correct reference"
                    })
                    has_errors = True

                for act_idx, act in enumerate(asp.get('activities', [])):
                    act_path = f"{asp_path}.activities[{act_idx}]"
                    led_by = act.get('ledBy')
                    if led_by and led_by not in all_personas and not has_deps:
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": f"{act_path}.ledBy",
                            "issue": f"ledBy references undefined persona: '{led_by}'",
                            "expected": f"One of: {sorted(all_personas)}",
                            "actual": led_by,
                            "suggestion": "Define persona or correct reference"
                        })
                        has_errors = True

            for act_idx, act in enumerate(practice.get('activities', [])):
                act_path = f"{prefix}.activities[{act_idx}]" if prefix else f"activities[{act_idx}]"
                led_by = act.get('ledBy')
                if led_by and led_by not in all_personas and not has_deps:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": f"{act_path}.ledBy",
                        "issue": f"ledBy references undefined persona: '{led_by}'",
                        "expected": f"One of: {sorted(all_personas)}",
                        "actual": led_by,
                        "suggestion": "Define persona or correct reference"
                    })
                    has_errors = True

        return not has_errors

    def validate_acyclicity(self) -> bool:
        """Validate acyclicity constraints per semantics.md Section 14."""
        has_errors = False

        is_method = 'practices' in self.practice or 'baselinePractice' in self.practice
        practices = self.practice.get('practices', []) if is_method else [self.practice]

        has_errors |= self._validate_alpha_hierarchy_acyclicity(practices)
        has_errors |= self._validate_work_product_hierarchy_acyclicity(practices)
        has_errors |= self._validate_contributes_to_state_acyclicity(practices)
        has_errors |= self._validate_prerequisite_acyclicity(practices)

        return not has_errors

    def _validate_alpha_hierarchy_acyclicity(self, practices: List[Dict]) -> bool:
        """Detect cycles in the combined contributesTo/mapsTo alpha graph."""
        has_errors = False

        parent_map = {}
        for practice in practices:
            for alpha in practice.get('alphas', []):
                parent = alpha.get('contributesTo') or alpha.get('mapsTo')
                if parent:
                    parent_map[alpha['name']] = parent

        for dep in self.dependencies:
            for alpha in dep.get('alphas', []):
                parent = alpha.get('contributesTo') or alpha.get('mapsTo')
                if parent and alpha['name'] not in parent_map:
                    parent_map[alpha['name']] = parent

        reported_cycles = set()
        for start_name in parent_map:
            visited = []
            visited_set = set()
            current = start_name
            while current in parent_map:
                if current in visited_set:
                    cycle_start_idx = visited.index(current)
                    cycle = visited[cycle_start_idx:] + [current]
                    cycle_key = frozenset(cycle)
                    if cycle_key not in reported_cycles:
                        reported_cycles.add(cycle_key)
                        self.errors.append({
                            "category": "acyclicity",
                            "severity": "error",
                            "path": "alphas",
                            "issue": f"Circular reference in Alpha hierarchy (contributesTo/mapsTo): {' → '.join(cycle)}",
                            "expected": "Acyclic alpha hierarchy",
                            "actual": f"Cycle: {' → '.join(cycle)}",
                            "suggestion": "Remove one contributesTo or mapsTo reference to break the cycle"
                        })
                        has_errors = True
                    break
                visited.append(current)
                visited_set.add(current)
                current = parent_map[current]

        return has_errors

    def _validate_work_product_hierarchy_acyclicity(self, practices: List[Dict]) -> bool:
        """Detect cycles in the combined partOf/mapsTo work product graph."""
        has_errors = False

        edges = {}
        for practice in practices:
            for wp in practice.get('workProducts', []):
                wp_edges = set()
                if wp.get('partOf'):
                    wp_edges.add(wp['partOf'])
                if wp.get('mapsTo'):
                    wp_edges.add(wp['mapsTo'])
                if wp_edges:
                    edges[wp['name']] = wp_edges

        for dep in self.dependencies:
            for wp in dep.get('workProducts', []):
                if wp['name'] not in edges:
                    wp_edges = set()
                    if wp.get('partOf'):
                        wp_edges.add(wp['partOf'])
                    if wp.get('mapsTo'):
                        wp_edges.add(wp['mapsTo'])
                    if wp_edges:
                        edges[wp['name']] = wp_edges

        WHITE, GRAY, BLACK = 0, 1, 2
        color = {name: WHITE for name in edges}
        reported_cycles = set()

        def dfs(node, path):
            nonlocal has_errors
            color[node] = GRAY
            path.append(node)
            for neighbor in edges.get(node, set()):
                if neighbor in color and color[neighbor] == GRAY:
                    cycle_start_idx = path.index(neighbor)
                    cycle = path[cycle_start_idx:] + [neighbor]
                    cycle_key = frozenset(cycle)
                    if cycle_key not in reported_cycles:
                        reported_cycles.add(cycle_key)
                        self.errors.append({
                            "category": "acyclicity",
                            "severity": "error",
                            "path": "workProducts",
                            "issue": f"Circular reference in WorkProduct hierarchy (partOf/mapsTo): {' → '.join(cycle)}",
                            "expected": "Acyclic work product hierarchy",
                            "actual": f"Cycle: {' → '.join(cycle)}",
                            "suggestion": "Remove one partOf or mapsTo reference to break the cycle"
                        })
                        has_errors = True
                elif neighbor in color and color[neighbor] == WHITE:
                    dfs(neighbor, path)
            path.pop()
            color[node] = BLACK

        for node in edges:
            if color.get(node, WHITE) == WHITE:
                dfs(node, [])

        return has_errors

    def _validate_contributes_to_state_acyclicity(self, practices: List[Dict]) -> bool:
        """Detect cycles in State.contributesToState references."""
        has_errors = False

        parent_map = {}
        for practice in practices:
            for alpha in practice.get('alphas', []):
                target_alpha = alpha.get('contributesTo') or alpha.get('mapsTo')
                if not target_alpha:
                    continue
                for state in alpha.get('states', []):
                    cts = state.get('contributesToState')
                    if cts and isinstance(cts, str):
                        parent_map[(alpha['name'], state['name'])] = (target_alpha, cts)

        reported_cycles = set()
        for start_node in parent_map:
            visited = []
            visited_set = set()
            current = start_node
            while current in parent_map:
                if current in visited_set:
                    cycle_start_idx = visited.index(current)
                    cycle_nodes = visited[cycle_start_idx:] + [current]
                    cycle_key = frozenset(visited[cycle_start_idx:])
                    if cycle_key not in reported_cycles:
                        reported_cycles.add(cycle_key)
                        cycle_str = ' → '.join(f'{a}.{s}' for a, s in cycle_nodes)
                        self.errors.append({
                            "category": "acyclicity",
                            "severity": "error",
                            "path": "alphas.states.contributesToState",
                            "issue": f"Circular reference in State.contributesToState: {cycle_str}",
                            "expected": "Acyclic state contribution mapping",
                            "actual": f"Cycle: {cycle_str}",
                            "suggestion": "Remove one contributesToState reference to break the cycle"
                        })
                        has_errors = True
                    break
                visited.append(current)
                visited_set.add(current)
                current = parent_map[current]

        return has_errors

    def _validate_prerequisite_acyclicity(self, practices: List[Dict]) -> bool:
        """Detect cycles in Background prerequisite graph (cross-element deadlocks)."""
        has_errors = False

        edges = defaultdict(set)
        all_nodes = set()

        def collect_bg_edges(source_key, bg):
            all_nodes.add(source_key)
            for req in bg.get('alphaStates', []):
                if req.get('alphaName') and req.get('stateName'):
                    target = f"alpha:{req['alphaName']}.{req['stateName']}"
                    edges[source_key].add(target)
                    all_nodes.add(target)
            for req in bg.get('workProductLevels', []):
                if req.get('workProductName') and req.get('levelOfDetailName'):
                    target = f"wp:{req['workProductName']}.{req['levelOfDetailName']}"
                    edges[source_key].add(target)
                    all_nodes.add(target)

        for practice in practices:
            for alpha in practice.get('alphas', []):
                for state in alpha.get('states', []):
                    bg = state.get('background')
                    if bg:
                        collect_bg_edges(f"alpha:{alpha['name']}.{state['name']}", bg)
            for wp in practice.get('workProducts', []):
                for lod in wp.get('levelsOfDetail', []):
                    bg = lod.get('background')
                    if bg:
                        collect_bg_edges(f"wp:{wp['name']}.{lod['name']}", bg)

        for dep in self.dependencies:
            for alpha in dep.get('alphas', []):
                for state in alpha.get('states', []):
                    bg = state.get('background')
                    if bg:
                        collect_bg_edges(f"alpha:{alpha['name']}.{state['name']}", bg)
            for wp in dep.get('workProducts', []):
                for lod in wp.get('levelsOfDetail', []):
                    bg = lod.get('background')
                    if bg:
                        collect_bg_edges(f"wp:{wp['name']}.{lod['name']}", bg)

        for alpha in self.baseline.get('alphas', []):
            for state in alpha.get('states', []):
                bg = state.get('background')
                if bg:
                    collect_bg_edges(f"alpha:{alpha['name']}.{state['name']}", bg)

        if not all_nodes:
            return has_errors

        # Iterative DFS with three-colour marking
        WHITE, GREY, BLACK = 0, 1, 2
        colour = defaultdict(int)
        reported_cycles = set()

        for start in all_nodes:
            if colour[start] != WHITE:
                continue

            stack = [(start, iter(edges.get(start, set())))]
            colour[start] = GREY
            path = [start]

            while stack:
                node, edge_iter = stack[-1]
                child = next(edge_iter, None)

                if child is not None:
                    child_colour = colour[child]
                    if child_colour == GREY:
                        idx = path.index(child)
                        cycle = path[idx:] + [child]
                        cycle_key = frozenset(path[idx:])
                        if cycle_key not in reported_cycles:
                            reported_cycles.add(cycle_key)
                            self.errors.append({
                                "category": "acyclicity",
                                "severity": "error",
                                "path": "backgrounds",
                                "issue": f"Circular prerequisite dependency: {' → '.join(cycle)}",
                                "expected": "Acyclic prerequisite graph (no deadlocks)",
                                "actual": f"Cycle: {' → '.join(cycle)}",
                                "suggestion": "Remove one background prerequisite to break the deadlock cycle"
                            })
                            has_errors = True
                    elif child_colour == WHITE:
                        colour[child] = GREY
                        path.append(child)
                        stack.append((child, iter(edges.get(child, set()))))
                else:
                    stack.pop()
                    path.pop()
                    colour[node] = BLACK

        return has_errors

    def _normalise_version(self, version: str) -> Optional[str]:
        """Normalise a version string to three-part semver (e.g. '1.0' -> '1.0.0')."""
        if not version:
            return None
        parts = version.strip().split('.')
        while len(parts) < 3:
            parts.append('0')
        try:
            return '.'.join(str(int(p)) for p in parts[:3])
        except ValueError:
            return None

    def _parse_version_tuple(self, version: str) -> Optional[tuple]:
        """Parse a semver string into a (major, minor, patch) tuple."""
        normalised = self._normalise_version(version)
        if not normalised:
            return None
        parts = normalised.split('.')
        try:
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            return None

    def _version_satisfies_range(self, version: str, version_range: str) -> Optional[bool]:
        """Check if a version satisfies a semver range constraint.

        Returns True/False if determinable, None if the range syntax is too complex.
        Supports: exact ('1.0.0'), caret ('^1.0.0'), tilde ('~1.0.0'),
        simple comparisons ('>=1.0.0', '<2.0.0'), and space-separated compound ranges.
        """
        ver = self._parse_version_tuple(version)
        if ver is None:
            return None

        range_str = version_range.strip()

        if range_str.startswith('^'):
            base = self._parse_version_tuple(range_str[1:])
            if base is None:
                return None
            if base[0] > 0:
                return base <= ver < (base[0] + 1, 0, 0)
            elif base[1] > 0:
                return base <= ver < (0, base[1] + 1, 0)
            else:
                return ver == base

        if range_str.startswith('~'):
            base = self._parse_version_tuple(range_str[1:])
            if base is None:
                return None
            return base <= ver < (base[0], base[1] + 1, 0)

        if ' ' in range_str:
            parts = range_str.split()
            for part in parts:
                result = self._version_satisfies_range(version, part)
                if result is None:
                    return None
                if not result:
                    return False
            return True

        if range_str.startswith('>='):
            base = self._parse_version_tuple(range_str[2:])
            return ver >= base if base else None
        if range_str.startswith('>'):
            base = self._parse_version_tuple(range_str[1:])
            return ver > base if base else None
        if range_str.startswith('<='):
            base = self._parse_version_tuple(range_str[2:])
            return ver <= base if base else None
        if range_str.startswith('<'):
            base = self._parse_version_tuple(range_str[1:])
            return ver < base if base else None

        base = self._parse_version_tuple(range_str)
        if base:
            return ver == base

        return None

    def _check_stage_contribution(self, oc, oc_path, oname, orchestrations, own) -> bool:
        """The orchestration arm of an objective contribution.

        See semantics/execution-and-patterns.md 9.4. A practice may declare the shape
        of an endeavour while holding none of its patterns, and is then the document
        with the best claim to the outcome; the pattern arm cannot express that,
        because the practice has no pattern to name.
        """
        has_errors = False
        o_name = oc.get('orchestrationName', '')
        if o_name not in orchestrations:
            self.errors.append({
                "category": "outcomes",
                "path": f"{oc_path}.orchestrationName",
                "issue": f"Outcome '{oname}' references unknown orchestration '{o_name}'",
                "expected": f"One of: {sorted(orchestrations)}" if orchestrations else "An orchestration name",
                "actual": o_name,
                "suggestion": "Use a PatternOrchestration.name declared in this practice, its baseline chain, or a declared dependency"
            })
            return True

        merged = self._merged_orchestration_stages(o_name, own)

        def resolve(ref, path):
            stage = self._resolve_stage_ref(ref, merged)
            if stage is not None:
                return stage
            described = self._describe_stage_ref(ref) if isinstance(ref, dict) else repr(ref)
            self.errors.append({
                "category": "outcomes",
                "path": path,
                "issue": (f"Outcome '{oname}' stage reference to {described} matches no stage of "
                          f"orchestration '{o_name}'"),
                "expected": f"One of: {sorted(self._describe_stage_ref(s) for s in merged.values())}" if merged else "A stage of the named orchestration",
                "actual": described,
                "suggestion": "Name the stage exactly as the orchestration places it, including relativeTo where the stage declares a host"
            })
            return None

        recognized_stage = None
        if oc.get('recognizedAtStage') is not None:
            recognized_stage = resolve(oc['recognizedAtStage'], f"{oc_path}.recognizedAtStage")
            if recognized_stage is None:
                has_errors = True
            elif recognized_stage.get('relationship') == 'onDemand':
                # Advice, not a rule. An outcome reaching full weight only when an
                # exception fires is almost always a modelling mistake, but an
                # endeavour whose whole point is the exception is conceivable.
                self.warnings.append({
                    "category": "outcomes",
                    "severity": "warning",
                    "path": f"{oc_path}.recognizedAtStage",
                    "issue": f"Outcome '{oname}' is recognised at an onDemand stage of '{o_name}'",
                    "expected": "Recognition at a stage the endeavour reaches by design",
                    "actual": "An onDemand stage, entered only when its trigger is recognised",
                    "suggestion": "Recognise the outcome at the stage that completes the endeavour, and weight the onDemand stage below it"
                })

        weights = oc.get('stageForecastWeights', []) or []
        recognized_weight = None
        for fw_idx, fw in enumerate(weights):
            if not isinstance(fw, dict):
                continue
            stage = resolve(fw.get('stage'), f"{oc_path}.stageForecastWeights[{fw_idx}].stage")
            if stage is None:
                has_errors = True
            elif recognized_stage is not None and stage is recognized_stage:
                recognized_weight = fw.get('weight')

        if recognized_stage is not None and weights:
            described = self._describe_stage_ref(oc['recognizedAtStage'])
            if recognized_weight is None:
                self.warnings.append({
                    "category": "outcomes",
                    "severity": "warning",
                    "path": f"{oc_path}.stageForecastWeights",
                    "issue": f"Outcome '{oname}' recognizedAtStage ({described}) is not listed in stageForecastWeights",
                    "expected": f"Entry for {described} with weight 1.0",
                    "actual": "Not present in stageForecastWeights",
                    "suggestion": "Add a stageForecastWeight entry for the recognised stage with weight 1.0"
                })
            elif recognized_weight != 1.0:
                self.warnings.append({
                    "category": "outcomes",
                    "severity": "warning",
                    "path": f"{oc_path}.stageForecastWeights",
                    "issue": f"Outcome '{oname}' recognizedAtStage ({described}) does not have weight 1.0 in stageForecastWeights",
                    "expected": f"Weight 1.0 for {described}",
                    "actual": recognized_weight,
                    "suggestion": "The recognised stage should have weight 1.0 (full recognition)"
                })

        return has_errors

    def validate_outcomes(self) -> bool:
        """Validate outcomes array: cross-references, count, and measureDescription."""
        has_errors = False
        is_method = 'practices' in self.practice or 'baselinePractice' in self.practice
        practices = self.practice.get('practices', [self.practice]) if is_method else [self.practice]

        all_alphas = set()
        all_alpha_states = defaultdict(set)
        all_pattern_views = set()
        all_pattern_names = set()
        pattern_views_by_pattern = defaultdict(set)
        wp_expected_metrics = defaultdict(set)
        all_work_products = set()

        # Patterns resolve across the baseline chain and declared dependencies, as
        # semantics 9.4 says they do and as the alphas and work products below
        # already did. Indexing only the declaring practice meant a practice could
        # not bind an outcome to a pattern a dependency owned, and -- because the
        # index was built inside the per-practice loop and read in the same
        # iteration -- an outcome in a method's first member practice naming a
        # pattern of a later member failed on document order alone.
        #
        # Views are unioned across every declaration of a name rather than taken
        # from the first. Patterns merge by name and their views merge additively,
        # so the merged pattern is what an outcome measures against.
        # _patterns_in_scope answers "who owns this name", which is the wrong
        # question here: where a practice extends an inherited pattern,
        # first-writer-wins hands back the inherited views and drops the ones the
        # practice declared itself, so its own outcome stops resolving against its
        # own phases.
        orchestrations_in_scope = self._orchestrations_in_scope(practices)
        for doc in self._practice_documents_in_scope(practices):
            for pattern in doc.get('patterns', []):
                if not isinstance(pattern, dict):
                    continue
                pat_name = pattern.get('name', '')
                if pat_name:
                    all_pattern_names.add(pat_name)
                for view in pattern.get('patternViews', []):
                    vname = view.get('name')
                    if vname:
                        all_pattern_views.add(vname)
                        if pat_name:
                            pattern_views_by_pattern[pat_name].add(vname)

        for alpha in self.baseline.get('alphas', []):
            all_alphas.add(alpha['name'])
            for state in alpha.get('states', []):
                all_alpha_states[alpha['name']].add(state['name'])
        for wp in self.baseline.get('workProducts', []):
            if wp.get('name'):
                all_work_products.add(wp['name'])
        for dep in self.dependencies:
            for alpha in dep.get('alphas', []):
                all_alphas.add(alpha['name'])
                for state in alpha.get('states', []):
                    all_alpha_states[alpha['name']].add(state['name'])
            for wp in dep.get('workProducts', []):
                if wp.get('name'):
                    all_work_products.add(wp['name'])

        for practice in practices:
            pname = practice.get('name', '<unnamed>')
            prefix = f"practice[{pname}]" if is_method else ""

            for alpha in practice.get('alphas', []):
                all_alphas.add(alpha['name'])
                for state in alpha.get('states', []):
                    all_alpha_states[alpha['name']].add(state['name'])

            for wp in practice.get('workProducts', []):
                wpname = wp.get('name')
                if wpname:
                    all_work_products.add(wpname)
                    for em in wp.get('expectedMetrics', []):
                        if em.get('name'):
                            wp_expected_metrics[wpname].add(em['name'])

            outcomes = practice.get('outcomes', [])
            path_prefix = f"{prefix}.outcomes" if prefix else "outcomes"

            if not outcomes:
                self.warnings.append({
                    "category": "outcomes",
                    "path": path_prefix,
                    "issue": f"Practice '{pname}' has no outcomes — practices should have 1-3 outcomes describing value delivery",
                    "suggestion": "Add 1-3 outcomes with measureDescription"
                })
                continue

            if len(outcomes) > 5:
                self.warnings.append({
                    "category": "outcomes",
                    "path": path_prefix,
                    "issue": f"Practice '{pname}' has {len(outcomes)} outcomes — practices should have 1-3 (max 5)",
                    "suggestion": "Consolidate outcomes — they are value propositions, not activities"
                })

            for idx, outcome in enumerate(outcomes):
                opath = f"{path_prefix}[{idx}]"
                oname = outcome.get('name', f'<index {idx}>')

                if not outcome.get('measureDescription'):
                    self.warnings.append({
                        "category": "outcomes",
                        "path": f"{opath}.measureDescription",
                        "issue": f"Outcome '{oname}' has no measureDescription",
                        "suggestion": "Add measureDescription explaining how success is measured"
                    })

                has_metrics = bool(outcome.get('metricContributions'))
                has_objectives = bool(outcome.get('objectiveContributions'))
                if not has_metrics and not has_objectives:
                    self.errors.append({
                        "category": "outcomes",
                        "severity": "error",
                        "path": opath,
                        "issue": f"Outcome '{oname}' has neither metricContributions nor objectiveContributions",
                        "expected": "At least one of metricContributions or objectiveContributions",
                        "actual": "Neither present",
                        "suggestion": "Add metricContributions (for numerical aggregates like revenue) or objectiveContributions (for lifecycle phase completion)"
                    })
                    has_errors = True

                for mc_idx, mc in enumerate(outcome.get('metricContributions', [])):
                    mc_path = f"{opath}.metricContributions[{mc_idx}]"
                    alpha_name = mc.get('alphaName', '')
                    if alpha_name not in all_alphas:
                        self.errors.append({
                            "category": "outcomes",
                            "path": f"{mc_path}.alphaName",
                            "issue": f"Outcome '{oname}' metricContribution references unknown alpha '{alpha_name}'",
                            "expected": f"One of: {sorted(all_alphas)[:10]}...",
                            "actual": alpha_name,
                            "suggestion": "Use an alpha name defined in baseline, practice, or dependencies"
                        })
                        has_errors = True
                    wp_filter = mc.get('workProductName')
                    if wp_filter and wp_filter not in all_work_products:
                        self.errors.append({
                            "category": "outcomes",
                            "path": f"{mc_path}.workProductName",
                            "issue": f"Outcome '{oname}' metricContribution references unknown work product '{wp_filter}'",
                            "expected": f"One of: {sorted(all_work_products)[:10]}...",
                            "actual": wp_filter,
                            "suggestion": "Use a work product name defined in baseline, practice, or dependencies"
                        })
                        has_errors = True
                    if alpha_name in all_alphas:
                        recognized = mc.get('recognizedAtStateName')
                        if recognized and recognized not in all_alpha_states.get(alpha_name, set()):
                            self.errors.append({
                                "category": "outcomes",
                                "path": f"{mc_path}.recognizedAtStateName",
                                "issue": f"Outcome '{oname}' recognizedAtStateName '{recognized}' not found on alpha '{alpha_name}'",
                                "expected": f"One of: {sorted(all_alpha_states[alpha_name])}",
                                "actual": recognized,
                                "suggestion": "Use a state name defined on the referenced alpha"
                            })
                            has_errors = True

                        fw_list = mc.get('forecastWeights', [])
                        if recognized and fw_list:
                            recognized_weights = [fw for fw in fw_list if fw.get('stateName') == recognized]
                            if recognized_weights and recognized_weights[0].get('weight') != 1.0:
                                self.warnings.append({
                                    "category": "outcomes",
                                    "severity": "warning",
                                    "path": f"{mc_path}.forecastWeights",
                                    "issue": f"Outcome '{oname}' recognizedAtStateName '{recognized}' does not have weight 1.0 in forecastWeights",
                                    "expected": f"Weight 1.0 for '{recognized}'",
                                    "actual": recognized_weights[0].get('weight'),
                                    "suggestion": "The recognizedAt state should have weight 1.0 (full recognition)"
                                })
                            elif not recognized_weights:
                                self.warnings.append({
                                    "category": "outcomes",
                                    "severity": "warning",
                                    "path": f"{mc_path}.forecastWeights",
                                    "issue": f"Outcome '{oname}' recognizedAtStateName '{recognized}' is not listed in forecastWeights",
                                    "expected": f"Entry for '{recognized}' with weight 1.0",
                                    "actual": "Not present in forecastWeights",
                                    "suggestion": "Add a forecastWeight entry for the recognizedAt state with weight 1.0"
                                })

                        for fw_idx, fw in enumerate(fw_list):
                            sname = fw.get('stateName', '')
                            if sname not in all_alpha_states.get(alpha_name, set()):
                                self.errors.append({
                                    "category": "outcomes",
                                    "path": f"{mc_path}.forecastWeights[{fw_idx}].stateName",
                                    "issue": f"Outcome '{oname}' forecastWeight stateName '{sname}' not found on alpha '{alpha_name}'",
                                    "expected": f"One of: {sorted(all_alpha_states[alpha_name])}",
                                    "actual": sname,
                                    "suggestion": "Use a state name defined on the referenced alpha"
                                })
                                has_errors = True

                    metric_name = mc.get('metricName', '')
                    if metric_name and wp_expected_metrics:
                        declared_anywhere = any(
                            metric_name in metrics
                            for metrics in wp_expected_metrics.values()
                        )
                        if not declared_anywhere:
                            self.warnings.append({
                                "category": "outcomes",
                                "path": f"{mc_path}.metricName",
                                "issue": f"Outcome '{oname}' metricName '{metric_name}' not declared in any work product's expectedMetrics",
                                "suggestion": f"Add an expectedMetrics entry with name '{metric_name}' to the work product whose instances will carry this metric"
                            })

                for oc_idx, oc in enumerate(outcome.get('objectiveContributions', [])):
                    oc_path = f"{opath}.objectiveContributions[{oc_idx}]"
                    oc_pattern = oc.get('patternName', '')
                    oc_orch = oc.get('orchestrationName', '')

                    # Exactly one arm, as the schema's oneOf says and as an
                    # OrchestrationStage declares its own target. Checked here too
                    # because this validator is run against documents whose schema
                    # conformance has not always been established first.
                    if oc_pattern and oc_orch:
                        self.errors.append({
                            "category": "outcomes",
                            "path": oc_path,
                            "issue": f"Outcome '{oname}' objectiveContribution names both a pattern and an orchestration",
                            "expected": "Exactly one of patternName and orchestrationName",
                            "actual": f"patternName '{oc_pattern}' and orchestrationName '{oc_orch}'",
                            "suggestion": "Measure against the pattern's views or the orchestration's stages, not both; split them into two contributions if both are meant"
                        })
                        has_errors = True
                        continue

                    if oc_orch:
                        has_errors |= self._check_stage_contribution(
                            oc, oc_path, oname, orchestrations_in_scope, practices)
                        continue

                    if not oc_pattern:
                        self.errors.append({
                            "category": "outcomes",
                            "path": oc_path,
                            "issue": f"Outcome '{oname}' objectiveContribution names neither a pattern nor an orchestration",
                            "expected": f"patternName (one of: {sorted(all_pattern_names)}) or orchestrationName" if all_pattern_names else "A patternName or an orchestrationName",
                            "actual": "(neither present)",
                            "suggestion": "Add patternName to measure against a pattern's views, or orchestrationName to measure against an orchestration's stages"
                        })
                        has_errors = True
                        scoped_views = all_pattern_views
                    elif oc_pattern not in all_pattern_names:
                        self.errors.append({
                            "category": "outcomes",
                            "path": f"{oc_path}.patternName",
                            "issue": f"Outcome '{oname}' references unknown pattern '{oc_pattern}'",
                            "expected": f"One of: {sorted(all_pattern_names)}",
                            "actual": oc_pattern,
                            "suggestion": "Use a Pattern.name defined in this practice, its baseline chain, or a declared dependency"
                        })
                        has_errors = True
                        scoped_views = all_pattern_views
                    else:
                        scoped_views = pattern_views_by_pattern.get(oc_pattern, set())

                    recognized_view = oc.get('recognizedAtPatternViewName')
                    if recognized_view and recognized_view not in scoped_views:
                        self.errors.append({
                            "category": "outcomes",
                            "path": f"{oc_path}.recognizedAtPatternViewName",
                            "issue": f"Outcome '{oname}' recognizedAtPatternViewName '{recognized_view}' not found in pattern '{oc_pattern}'",
                            "expected": f"One of: {sorted(scoped_views)}" if scoped_views else "A pattern view name",
                            "actual": recognized_view,
                            "suggestion": f"Use a patternView name from pattern '{oc_pattern}'"
                        })
                        has_errors = True

                    for fw_idx, fw in enumerate(oc.get('forecastWeights', [])):
                        vname = fw.get('patternViewName', '')
                        if vname not in scoped_views:
                            self.errors.append({
                                "category": "outcomes",
                                "path": f"{oc_path}.forecastWeights[{fw_idx}].patternViewName",
                                "issue": f"Outcome '{oname}' forecastWeight patternViewName '{vname}' not found in pattern '{oc_pattern}'",
                                "expected": f"One of: {sorted(scoped_views)}" if scoped_views else "A pattern view name",
                                "actual": vname,
                                "suggestion": f"Use a patternView name from pattern '{oc_pattern}'"
                            })
                            has_errors = True

            # Deliberately the practice's own patterns and orchestrations, not the
            # in-scope indexes above. The advice is that a practice owning a lifecycle
            # or the shape of an endeavour should track maturity against it; a practice
            # that merely depends on one owns no such claim, and reading the wider
            # index here would fire on every extension practice in the corpus.
            if (practice.get('patterns') or practice.get('patternOrchestrations')) and outcomes:
                has_objective = any(
                    outcome.get('objectiveContributions')
                    for outcome in outcomes
                )
                if not has_objective:
                    self.warnings.append({
                        "category": "outcomes",
                        "path": path_prefix,
                        "issue": f"Practice '{pname}' declares lifecycle patterns or an orchestration but has no outcome with objectiveContributions — at least one outcome should track adoption maturity against the shape it owns",
                        "suggestion": "Add objectiveContributions to one outcome: patternName with recognizedAtPatternViewName and forecastWeights for a lifecycle pattern, or orchestrationName with recognizedAtStage and stageForecastWeights for an endeavour shape, increasing monotonically"
                    })

        return has_errors

    def validate_version_constraints(self) -> bool:
        """Validate dependencyVersions constraints.

        Checks:
        1. Each documentName matches a declared dependency name
        2. If the referenced document is loaded, its version satisfies the range
        """
        dep_versions = self.practice.get('dependencyVersions', [])
        if not dep_versions:
            return True

        declared_deps = set()
        baseline_name = self.practice.get('baselinePracticeName')
        if baseline_name:
            declared_deps.add(baseline_name)
        for dep_name in self.practice.get('practiceDependencyNames', []):
            declared_deps.add(dep_name)

        dep_docs_by_name = {}
        if baseline_name and self.baseline:
            dep_docs_by_name[baseline_name] = self.baseline
        for dep in self.dependencies:
            dep_name = dep.get('name')
            if dep_name:
                dep_docs_by_name[dep_name] = dep

        has_warnings = False
        for idx, constraint in enumerate(dep_versions):
            doc_name = constraint.get('documentName', '')
            version_range = constraint.get('versionRange', '')
            path = f"dependencyVersions[{idx}]"

            if doc_name not in declared_deps:
                self.warnings.append({
                    "category": "version",
                    "severity": "warning",
                    "path": f"{path}.documentName",
                    "issue": f"Orphaned version constraint: '{doc_name}' does not match any declared dependency",
                    "expected": f"One of: {sorted(declared_deps)}",
                    "actual": doc_name,
                    "suggestion": "Remove this constraint or correct the documentName"
                })
                has_warnings = True
                continue

            if doc_name in dep_docs_by_name:
                dep_doc = dep_docs_by_name[doc_name]
                dep_version = dep_doc.get('version')
                if dep_version and version_range:
                    satisfies = self._version_satisfies_range(dep_version, version_range)
                    if satisfies is False:
                        normalised = self._normalise_version(dep_version)
                        self.warnings.append({
                            "category": "version",
                            "severity": "warning",
                            "path": path,
                            "issue": f"Version mismatch: '{doc_name}' is at version {dep_version} (normalised: {normalised}) but constraint requires {version_range}",
                            "expected": f"Version satisfying {version_range}",
                            "actual": dep_version,
                            "suggestion": f"Update '{doc_name}' to a version satisfying {version_range}, or relax the constraint"
                        })
                        has_warnings = True

        return True

    def validate_schema_version(self) -> bool:
        """Validate schemaVersion compatibility if present."""
        schema_version = self.practice.get('schemaVersion')
        if not schema_version:
            return True

        schema_comment = self.schema.get('$comment', '')
        if schema_comment.startswith('schemaVersion:'):
            declared_schema_ver = schema_comment.split(':', 1)[1]
            doc_ver = self._parse_version_tuple(schema_version)
            schema_ver = self._parse_version_tuple(declared_schema_ver)

            if doc_ver and schema_ver:
                if doc_ver[0] > schema_ver[0]:
                    self.errors.append({
                        "category": "version",
                        "severity": "error",
                        "path": "schemaVersion",
                        "issue": f"Document targets schema {schema_version} but validator supports {declared_schema_ver} (major version mismatch)",
                        "expected": f"Schema major version <= {schema_ver[0]}",
                        "actual": schema_version,
                        "suggestion": "Update to a compatible schema version or upgrade the validator"
                    })
                    return False
                elif doc_ver[1] > schema_ver[1] and doc_ver[0] == schema_ver[0]:
                    self.warnings.append({
                        "category": "version",
                        "severity": "warning",
                        "path": "schemaVersion",
                        "issue": f"Document targets schema {schema_version} but validator supports {declared_schema_ver} (minor version ahead)",
                        "expected": f"Schema version <= {declared_schema_ver}",
                        "actual": schema_version,
                        "suggestion": "Some features may not be validated — consider upgrading the validator"
                    })
        return True

    def validate_bindings(self) -> bool:
        """Validate method-level bindings (cross-baseline alpha and work product relationships)."""
        is_method = 'practices' in self.practice or 'baselinePractice' in self.practice
        if not is_method:
            return True

        bindings = self.practice.get('bindings')
        if not bindings:
            return True

        has_errors = False

        # Build index of all accessible baselines and their elements
        # For now, validate against what we can see (baseline + dependencies)
        accessible_alphas = defaultdict(dict)  # baselineName -> {alphaName -> alpha}
        accessible_alpha_states = defaultdict(lambda: defaultdict(set))  # baselineName -> alphaName -> {states}
        accessible_work_products = defaultdict(dict)  # baselineName -> {wpName -> wp}
        accessible_wp_lods = defaultdict(lambda: defaultdict(set))  # baselineName -> wpName -> {lods}

        baseline_name = self.baseline.get('name', '')
        for alpha in self.baseline.get('alphas', []):
            accessible_alphas[baseline_name][alpha['name']] = alpha
            for state in alpha.get('states', []):
                accessible_alpha_states[baseline_name][alpha['name']].add(state['name'])
        for wp in self.baseline.get('workProducts', []):
            accessible_work_products[baseline_name][wp['name']] = wp
            for lod in wp.get('levelsOfDetail', []):
                accessible_wp_lods[baseline_name][wp['name']].add(lod['name'])

        for dep in self.dependencies:
            dep_name = dep.get('name', '')
            dep_baseline = dep.get('baselinePracticeName', dep_name)
            for alpha in dep.get('alphas', []):
                accessible_alphas[dep_baseline][alpha['name']] = alpha
                accessible_alphas[dep_name][alpha['name']] = alpha
                for state in alpha.get('states', []):
                    accessible_alpha_states[dep_baseline][alpha['name']].add(state['name'])
                    accessible_alpha_states[dep_name][alpha['name']].add(state['name'])
            for wp in dep.get('workProducts', []):
                accessible_work_products[dep_baseline][wp['name']] = wp
                accessible_work_products[dep_name][wp['name']] = wp
                for lod in wp.get('levelsOfDetail', []):
                    accessible_wp_lods[dep_baseline][wp['name']].add(lod['name'])
                    accessible_wp_lods[dep_name][wp['name']].add(lod['name'])

        # Also index practices within the method
        for practice in self.practice.get('practices', []):
            p_baseline = practice.get('baselinePracticeName', '')
            for alpha in practice.get('alphas', []):
                accessible_alphas[p_baseline][alpha['name']] = alpha
                for state in alpha.get('states', []):
                    accessible_alpha_states[p_baseline][alpha['name']].add(state['name'])
            for wp in practice.get('workProducts', []):
                accessible_work_products[p_baseline][wp['name']] = wp
                for lod in wp.get('levelsOfDetail', []):
                    accessible_wp_lods[p_baseline][wp['name']].add(lod['name'])

        # Validate alpha bindings
        seen_alpha_targets = defaultdict(set)
        for idx, binding in enumerate(bindings.get('alphaBindings', [])):
            path = f"bindings.alphaBindings[{idx}]"
            target = binding.get('targetAlpha', {})
            t_baseline = target.get('baselineName', '')
            t_alpha = target.get('alphaName', '')

            if t_baseline and t_alpha:
                if t_baseline in accessible_alphas and t_alpha not in accessible_alphas[t_baseline]:
                    self.errors.append({
                        "category": "bindings",
                        "severity": "error",
                        "path": f"{path}.targetAlpha.alphaName",
                        "issue": f"Target alpha '{t_alpha}' not found in baseline '{t_baseline}'",
                        "expected": f"One of: {sorted(accessible_alphas.get(t_baseline, {}).keys())}",
                        "actual": t_alpha,
                        "suggestion": "Check alpha name spelling or baseline name"
                    })
                    has_errors = True

            target_states = accessible_alpha_states.get(t_baseline, {}).get(t_alpha, set())

            for s_idx, source in enumerate(binding.get('sourceAlphas', [])):
                s_path = f"{path}.sourceAlphas[{s_idx}]"
                s_baseline = source.get('baselineName', '')
                s_alpha = source.get('alphaName', '')

                if s_baseline in accessible_alphas and s_alpha not in accessible_alphas[s_baseline]:
                    self.errors.append({
                        "category": "bindings",
                        "severity": "error",
                        "path": f"{s_path}.alphaName",
                        "issue": f"Source alpha '{s_alpha}' not found in baseline '{s_baseline}'",
                        "expected": f"One of: {sorted(accessible_alphas.get(s_baseline, {}).keys())}",
                        "actual": s_alpha,
                        "suggestion": "Check alpha name spelling or baseline name"
                    })
                    has_errors = True

                # Check for duplicate source in same target
                source_key = (s_baseline, s_alpha)
                target_key = (t_baseline, t_alpha)
                if source_key in seen_alpha_targets[target_key]:
                    self.warnings.append({
                        "category": "bindings",
                        "severity": "warning",
                        "path": s_path,
                        "issue": f"Duplicate source alpha '{s_alpha}' from '{s_baseline}' targeting '{t_alpha}'",
                        "expected": "Each source alpha appears at most once per target",
                        "actual": f"{s_baseline}.{s_alpha}",
                        "suggestion": "Remove duplicate binding entry"
                    })
                seen_alpha_targets[target_key].add(source_key)

                source_states = accessible_alpha_states.get(s_baseline, {}).get(s_alpha, set())

                mapped_target_states = set()
                for sc_idx, sc in enumerate(source.get('stateContributions', [])):
                    sc_path = f"{s_path}.stateContributions[{sc_idx}]"
                    from_state = sc.get('fromState', '')
                    to_state = sc.get('toState', '')

                    if source_states and from_state not in source_states:
                        self.errors.append({
                            "category": "bindings",
                            "severity": "error",
                            "path": f"{sc_path}.fromState",
                            "issue": f"State '{from_state}' not found on source alpha '{s_alpha}'",
                            "expected": f"One of: {sorted(source_states)}",
                            "actual": from_state,
                            "suggestion": "Check state name spelling"
                        })
                        has_errors = True

                    if target_states and to_state not in target_states:
                        self.errors.append({
                            "category": "bindings",
                            "severity": "error",
                            "path": f"{sc_path}.toState",
                            "issue": f"State '{to_state}' not found on target alpha '{t_alpha}'",
                            "expected": f"One of: {sorted(target_states)}",
                            "actual": to_state,
                            "suggestion": "Check state name spelling"
                        })
                        has_errors = True
                    else:
                        mapped_target_states.add(to_state)

                # Warn about unmapped target states
                relationship = binding.get('relationship', 'contribution')
                if target_states and source.get('stateContributions') is not None:
                    unmapped = target_states - mapped_target_states
                    if unmapped:
                        severity = "warning" if relationship == "contribution" else "info"
                        label = "not advanced by this source" if relationship == "contribution" else "will be interpolated from surrounding mapped states"
                        self.warnings.append({
                            "category": "bindings",
                            "severity": severity,
                            "path": s_path,
                            "issue": f"Unmapped target states on '{t_alpha}': {sorted(unmapped)} — {label}",
                            "expected": "Full target state coverage preferred",
                            "actual": f"Mapped: {sorted(mapped_target_states)}, Unmapped: {sorted(unmapped)}",
                            "suggestion": "Map each target state to its closest semantic equivalent on the source, using many-to-one if needed"
                        })

        # Validate work product bindings
        seen_wp_targets = defaultdict(set)
        for idx, binding in enumerate(bindings.get('workProductBindings', [])):
            path = f"bindings.workProductBindings[{idx}]"
            target = binding.get('targetWorkProduct', {})
            t_baseline = target.get('baselineName', '')
            t_wp = target.get('workProductName', '')

            if t_baseline and t_wp:
                if t_baseline in accessible_work_products and t_wp not in accessible_work_products[t_baseline]:
                    self.errors.append({
                        "category": "bindings",
                        "severity": "error",
                        "path": f"{path}.targetWorkProduct.workProductName",
                        "issue": f"Target work product '{t_wp}' not found in baseline '{t_baseline}'",
                        "expected": f"One of: {sorted(accessible_work_products.get(t_baseline, {}).keys())}",
                        "actual": t_wp,
                        "suggestion": "Check work product name spelling or baseline name"
                    })
                    has_errors = True

            target_lods = accessible_wp_lods.get(t_baseline, {}).get(t_wp, set())

            for s_idx, source in enumerate(binding.get('sourceWorkProducts', [])):
                s_path = f"{path}.sourceWorkProducts[{s_idx}]"
                s_baseline = source.get('baselineName', '')
                s_wp = source.get('workProductName', '')

                if s_baseline in accessible_work_products and s_wp not in accessible_work_products[s_baseline]:
                    self.errors.append({
                        "category": "bindings",
                        "severity": "error",
                        "path": f"{s_path}.workProductName",
                        "issue": f"Source work product '{s_wp}' not found in baseline '{s_baseline}'",
                        "expected": f"One of: {sorted(accessible_work_products.get(s_baseline, {}).keys())}",
                        "actual": s_wp,
                        "suggestion": "Check work product name spelling or baseline name"
                    })
                    has_errors = True

                # Check for duplicate source in same target
                source_key = (s_baseline, s_wp)
                target_key = (t_baseline, t_wp)
                if source_key in seen_wp_targets[target_key]:
                    self.warnings.append({
                        "category": "bindings",
                        "severity": "warning",
                        "path": s_path,
                        "issue": f"Duplicate source work product '{s_wp}' from '{s_baseline}' targeting '{t_wp}'",
                        "expected": "Each source work product appears at most once per target",
                        "actual": f"{s_baseline}.{s_wp}",
                        "suggestion": "Remove duplicate binding entry"
                    })
                seen_wp_targets[target_key].add(source_key)

                source_lods = accessible_wp_lods.get(s_baseline, {}).get(s_wp, set())

                mapped_target_lods = set()
                for lc_idx, lc in enumerate(source.get('lodContributions', [])):
                    lc_path = f"{s_path}.lodContributions[{lc_idx}]"
                    from_lod = lc.get('fromLevelOfDetail', '')
                    to_lod = lc.get('toLevelOfDetail', '')

                    if source_lods and from_lod not in source_lods:
                        self.errors.append({
                            "category": "bindings",
                            "severity": "error",
                            "path": f"{lc_path}.fromLevelOfDetail",
                            "issue": f"LOD '{from_lod}' not found on source work product '{s_wp}'",
                            "expected": f"One of: {sorted(source_lods)}",
                            "actual": from_lod,
                            "suggestion": "Check LOD name spelling"
                        })
                        has_errors = True

                    if target_lods and to_lod not in target_lods:
                        self.errors.append({
                            "category": "bindings",
                            "severity": "error",
                            "path": f"{lc_path}.toLevelOfDetail",
                            "issue": f"LOD '{to_lod}' not found on target work product '{t_wp}'",
                            "expected": f"One of: {sorted(target_lods)}",
                            "actual": to_lod,
                            "suggestion": "Check LOD name spelling"
                        })
                        has_errors = True
                    else:
                        mapped_target_lods.add(to_lod)

                # Warn about unmapped target LODs
                relationship = binding.get('relationship', 'contribution')
                if target_lods and source.get('lodContributions') is not None:
                    unmapped = target_lods - mapped_target_lods
                    if unmapped:
                        severity = "warning" if relationship == "contribution" else "info"
                        label = "not advanced by this source" if relationship == "contribution" else "will be interpolated from surrounding mapped LODs"
                        self.warnings.append({
                            "category": "bindings",
                            "severity": severity,
                            "path": s_path,
                            "issue": f"Unmapped target LODs on '{t_wp}': {sorted(unmapped)} — {label}",
                            "expected": "Full target LOD coverage preferred",
                            "actual": f"Mapped: {sorted(mapped_target_lods)}, Unmapped: {sorted(unmapped)}",
                            "suggestion": "Map each target LOD to its closest semantic equivalent on the source, using many-to-one if needed"
                        })

        return not has_errors

    def validate_redeclaration_vs_new(self) -> bool:
        """
        Validate that alphas are correctly classified as redeclaration vs new.

        Errors:
        - Alpha has contributesTo but name matches baseline (should be redeclaration)
        - Alpha doesn't have contributesTo and name doesn't match baseline (should have contributesTo)

        This is a CRITICAL validation that prevents the "Platform Governance" error class.
        """
        practices = self.practice.get('practices', [self.practice])
        has_errors = False

        for practice_idx, practice in enumerate(practices):
            practice_name = practice.get('name', 'Unknown')
            prefix = f"practices[{practice_idx}]" if 'practices' in self.practice else ""

            for alpha_idx, alpha in enumerate(practice.get('alphas', [])):
                alpha_name = alpha.get('name')
                has_contributes_to = 'contributesTo' in alpha
                has_maps_to = 'mapsTo' in alpha

                path = f"{prefix}.alphas[{alpha_idx}]" if prefix else f"alphas[{alpha_idx}]"

                # contributesTo and mapsTo must reference different alphas
                if has_contributes_to and has_maps_to and alpha.get('contributesTo') == alpha.get('mapsTo'):
                    self.errors.append({
                        'category': 'baseline',
                        'severity': 'error',
                        'practice': practice_name,
                        'path': path,
                        'alpha': alpha_name,
                        'issue': f'Alpha "{alpha_name}" has contributesTo and mapsTo referencing the same alpha: "{alpha.get("contributesTo")}"',
                        'expected': 'contributesTo and mapsTo must reference different alphas',
                        'actual': f'Both reference "{alpha.get("contributesTo")}"',
                        'suggestion': 'An alpha can both contribute to one alpha and map to another, but the targets must be different.'
                    })
                    has_errors = True

                # Check if this alpha name exactly matches a baseline alpha name
                is_baseline_alpha = alpha_name in self.baseline_alphas

                # Check if this alpha name matches a dependency practice alpha
                is_dep_alpha = alpha_name in self.dep_alphas

                if is_baseline_alpha:
                    # This is a baseline alpha - should be REDECLARATION
                    if has_contributes_to:
                        contributes_to = alpha.get('contributesTo')
                        self.errors.append({
                            'category': 'baseline',
                            'severity': 'error',
                            'practice': practice_name,
                            'path': path,
                            'alpha': alpha_name,
                            'issue': f'Alpha "{alpha_name}" exists in baseline but has contributesTo property',
                            'expected': 'No contributesTo property (baseline alphas are redeclared, not specialized)',
                            'actual': f'contributesTo: "{contributes_to}"',
                            'suggestion': f'Remove contributesTo property. "{alpha_name}" should be a REDECLARATION (enrichment) of the baseline alpha, not a new specialized alpha. Preserve baseline name, description, and state structure exactly. Only add practice-specific checklists to existing states.'
                        })
                        has_errors = True
                    if has_maps_to:
                        maps_to = alpha.get('mapsTo')
                        self.errors.append({
                            'category': 'baseline',
                            'severity': 'error',
                            'practice': practice_name,
                            'path': path,
                            'alpha': alpha_name,
                            'issue': f'Alpha "{alpha_name}" exists in baseline but has mapsTo property',
                            'expected': 'No mapsTo property (baseline alphas are redeclared, not mapped)',
                            'actual': f'mapsTo: "{maps_to}"',
                            'suggestion': f'Remove mapsTo property. "{alpha_name}" should be a REDECLARATION (enrichment) of the baseline alpha. Preserve baseline name, description, and state structure exactly.'
                        })
                        has_errors = True

                    # Additionally check if states match baseline (redeclarations MUST preserve baseline states)
                    baseline_alpha = self.baseline_alphas[alpha_name]
                    baseline_state_names = {s['name'] for s in baseline_alpha.get('states', [])}
                    practice_state_names = {s['name'] for s in alpha.get('states', [])}

                    if baseline_state_names != practice_state_names:
                        missing_states = baseline_state_names - practice_state_names
                        extra_states = practice_state_names - baseline_state_names

                        issue_parts = []
                        if missing_states:
                            issue_parts.append(f'missing baseline states: {sorted(missing_states)}')
                        if extra_states:
                            issue_parts.append(f'has extra states not in baseline: {sorted(extra_states)}')

                        self.errors.append({
                            'category': 'baseline',
                            'severity': 'error',
                            'practice': practice_name,
                            'path': f'{path}.states',
                            'alpha': alpha_name,
                            'issue': f'Redeclared alpha "{alpha_name}" state mismatch: {"; ".join(issue_parts)}',
                            'expected': f'Exact baseline states: {sorted(baseline_state_names)}',
                            'actual': f'Practice states: {sorted(practice_state_names)}',
                            'suggestion': f'Redeclarations MUST preserve baseline state names exactly. Use baseline states: {sorted(baseline_state_names)}. You can only ADD checklists to existing states, not modify state names or add/remove states.'
                        })
                        has_errors = True

                elif is_dep_alpha:
                    # This is a dependency practice alpha - REDECLARATION of parent practice alpha
                    # Should NOT have contributesTo or mapsTo (redeclaration enriches existing alpha)
                    dep_alpha = self.dep_alphas[alpha_name]
                    if has_contributes_to and not dep_alpha.get('contributesTo'):
                        contributes_to = alpha.get('contributesTo')
                        self.errors.append({
                            'category': 'baseline',
                            'severity': 'error',
                            'practice': practice_name,
                            'path': path,
                            'alpha': alpha_name,
                            'issue': f'Alpha "{alpha_name}" exists in dependency practice but has contributesTo property',
                            'expected': 'No contributesTo property (dependency practice alphas are redeclared, not specialized)',
                            'actual': f'contributesTo: "{contributes_to}"',
                            'suggestion': f'Remove contributesTo property. "{alpha_name}" should be a REDECLARATION (enrichment) of the dependency practice alpha.'
                        })
                        has_errors = True
                    if has_maps_to and not dep_alpha.get('mapsTo'):
                        maps_to = alpha.get('mapsTo')
                        self.errors.append({
                            'category': 'baseline',
                            'severity': 'error',
                            'practice': practice_name,
                            'path': path,
                            'alpha': alpha_name,
                            'issue': f'Alpha "{alpha_name}" exists in dependency practice but has mapsTo property',
                            'expected': 'No mapsTo property (dependency practice alphas are redeclared, not mapped)',
                            'actual': f'mapsTo: "{maps_to}"',
                            'suggestion': f'Remove mapsTo property. "{alpha_name}" should be a REDECLARATION (enrichment) of the dependency practice alpha.'
                        })
                        has_errors = True

                    # Check if states match dependency practice alpha
                    dep_state_names = {s['name'] for s in dep_alpha.get('states', [])}
                    practice_state_names = {s['name'] for s in alpha.get('states', [])}

                    if dep_state_names != practice_state_names:
                        missing_states = dep_state_names - practice_state_names
                        extra_states = practice_state_names - dep_state_names

                        issue_parts = []
                        if missing_states:
                            issue_parts.append(f'missing dependency practice states: {sorted(missing_states)}')
                        if extra_states:
                            issue_parts.append(f'has extra states not in dependency practice: {sorted(extra_states)}')

                        self.errors.append({
                            'category': 'baseline',
                            'severity': 'error',
                            'practice': practice_name,
                            'path': f'{path}.states',
                            'alpha': alpha_name,
                            'issue': f'Redeclared alpha "{alpha_name}" state mismatch: {"; ".join(issue_parts)}',
                            'expected': f'Exact dependency practice states: {sorted(dep_state_names)}',
                            'actual': f'Practice states: {sorted(practice_state_names)}',
                            'suggestion': f'Redeclarations MUST preserve dependency practice state names exactly. Use states: {sorted(dep_state_names)}. You can only ADD checklists to existing states, not modify state names or add/remove states.'
                        })
                        has_errors = True

                else:
                    # This is a new alpha - MUST have contributesTo or mapsTo
                    if not has_contributes_to and not has_maps_to:
                        all_parent_alphas = sorted(set(self.baseline_alphas.keys()) | set(self.dep_alphas.keys()))
                        self.errors.append({
                            'category': 'baseline',
                            'severity': 'error',
                            'practice': practice_name,
                            'path': path,
                            'alpha': alpha_name,
                            'issue': f'New alpha "{alpha_name}" missing contributesTo or mapsTo property',
                            'expected': 'contributesTo: "<ParentAlphaName>" or mapsTo: "<ParentAlphaName>"',
                            'actual': 'No contributesTo or mapsTo property',
                            'suggestion': f'Add contributesTo (specialization with own states) or mapsTo (variant with same states) pointing to a parent alpha. NO FLOATING ALPHAS. Available: {all_parent_alphas}'
                        })
                        has_errors = True

                    # mapsTo alphas MUST have identical states to their target
                    if has_maps_to and not has_contributes_to:
                        maps_to = alpha.get('mapsTo')
                        target_alpha = None
                        if maps_to in self.baseline_alphas:
                            target_alpha = self.baseline_alphas[maps_to]
                        elif maps_to in self.dep_alphas:
                            target_alpha = self.dep_alphas[maps_to]
                        else:
                            for other_alpha in practice.get('alphas', []):
                                if other_alpha.get('name') == maps_to:
                                    target_alpha = other_alpha
                                    break

                        if target_alpha:
                            target_state_names = [s['name'] for s in target_alpha.get('states', [])]
                            practice_state_names = [s['name'] for s in alpha.get('states', [])]

                            if target_state_names != practice_state_names:
                                missing_states = set(target_state_names) - set(practice_state_names)
                                extra_states = set(practice_state_names) - set(target_state_names)

                                issue_parts = []
                                if missing_states:
                                    issue_parts.append(f'missing target states: {sorted(missing_states)}')
                                if extra_states:
                                    issue_parts.append(f'has extra states not in target: {sorted(extra_states)}')

                                self.errors.append({
                                    'category': 'baseline',
                                    'severity': 'error',
                                    'practice': practice_name,
                                    'path': f'{path}.states',
                                    'alpha': alpha_name,
                                    'issue': f'mapsTo alpha "{alpha_name}" state mismatch with target "{maps_to}": {"; ".join(issue_parts)}',
                                    'expected': f'Exact target states (ordered): {target_state_names}',
                                    'actual': f'Practice states: {practice_state_names}',
                                    'suggestion': f'mapsTo alphas MUST have identical state names and sequence as their target alpha. Use states: {target_state_names}. You can add different checklists but state names must match exactly.'
                                })
                                has_errors = True

        return not has_errors


def main():
    """Main entry point"""
    import argparse as _argparse

    parser = _argparse.ArgumentParser(
        description="Validate Practice/Method JSON against schema, baseline, and integrity rules"
    )
    parser.add_argument("practice", help="Practice or method JSON file")
    parser.add_argument("baseline", help="Baseline practice JSON file")
    parser.add_argument("schema", help="Language schema JSON file")
    parser.add_argument("deps", nargs="*", help="Additional dependency practice JSON files")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress progress messages to stderr")
    parser.add_argument("--brief", action="store_true",
                        help="Print one-line summary instead of full JSON report")
    args = parser.parse_args()

    practice_file = Path(args.practice)
    baseline_file = Path(args.baseline)
    schema_file = Path(args.schema)

    dependency_files = [Path(d) for d in (args.deps or [])]

    def progress(msg):
        if not args.quiet:
            print(msg, file=sys.stderr)

    # Auto-discover dependency files in the practice directory
    for auto_name in ('_effective-parent.json', '_effective-context.json'):
        auto_path = practice_file.parent / auto_name
        if auto_path.exists() and auto_path not in dependency_files:
            progress(f"Auto-discovered dependency: {auto_path}")
            dependency_files.append(auto_path)

    # Validate
    validator = PracticeValidator(practice_file, baseline_file, schema_file, dependency_files)

    # Run all validations
    progress("Validating schema...")
    schema_valid = validator.validate_schema()

    progress("Validating baseline references...")
    baseline_valid = validator.validate_baseline_references()

    progress("Validating method-level bindings...")
    bindings_valid = validator.validate_bindings()

    progress("Validating redeclaration vs new alpha classification...")
    redeclaration_valid = validator.validate_redeclaration_vs_new()

    progress("Validating internal integrity...")
    integrity_valid = validator.validate_internal_integrity()

    progress("Validating ledBy references...")
    led_by_valid = validator.validate_led_by()

    progress("Validating background references...")
    backgrounds_valid = validator.validate_backgrounds()

    progress("Validating instance relationships...")
    instance_rel_valid = validator.validate_instance_relationships()

    progress("Validating acyclicity constraints...")
    acyclicity_valid = validator.validate_acyclicity()

    progress("Validating work product purpose hub...")
    wp_purpose_valid = validator.validate_work_product_purpose()

    progress("Validating specificity declarations...")
    specificity_valid = validator.validate_specificity()

    progress("Validating suppression of inherited content...")
    suppression_valid = validator.validate_suppression()

    progress("Validating loop declarations...")
    loops_valid = validator.validate_loops()

    progress("Validating pattern orchestrations...")
    orchestrations_valid = validator.validate_orchestrations()

    progress("Validating semantic alignment...")
    semantic_valid = validator.validate_semantic_alignment()

    progress("Validating checklist quality...")
    validator.validate_checklist_quality()

    progress("Validating outcomes...")
    validator.validate_outcomes()

    progress("Validating version constraints...")
    validator.validate_version_constraints()

    progress("Validating schema version...")
    schema_version_valid = validator.validate_schema_version()

    # Generate report
    report = validator.generate_report()

    if args.brief:
        status = "PASS" if report["valid"] else "FAIL"
        errs = report.get("error_count", 0)
        warns = report.get("warning_count", 0)
        warn_str = f" ({warns} warnings)" if warns else ""
        print(f"{status} {errs} errors{warn_str} — {practice_file.name}")
    else:
        print(json.dumps(report, indent=2))

    # Exit code
    sys.exit(0 if report['valid'] else 1)


if __name__ == '__main__':
    main()

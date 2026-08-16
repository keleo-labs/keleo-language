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
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict

try:
    import jsonschema
    from jsonschema import Draft202012Validator, RefResolver
except ImportError:
    print("ERROR: jsonschema library not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(2)


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

                # Mutual exclusivity: partOf and mapsTo cannot coexist
                if part_of and maps_to:
                    self.errors.append({
                        "category": "integrity",
                        "severity": "error",
                        "path": wp_path,
                        "issue": f"Work product '{wp.get('name')}' has both partOf and mapsTo (mutually exclusive)",
                        "expected": "Either partOf OR mapsTo, not both",
                        "actual": f"partOf: '{part_of}', mapsTo: '{maps_to}'",
                        "suggestion": "Use partOf for containment (sub-artifact within parent). Use mapsTo for variant mapping (IS-A variant with same LODs). Remove one."
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
        # Both partOf and mapsTo create parent edges; cycles can span both types
        wp_parent_map = {}
        for practice_scan in practices:
            for wp in practice_scan.get('workProducts', []):
                parent = wp.get('partOf') or wp.get('mapsTo')
                if parent:
                    wp_parent_map[wp['name']] = parent
        for dep in self.dependencies:
            for wp in dep.get('workProducts', []):
                parent = wp.get('partOf') or wp.get('mapsTo')
                if parent:
                    wp_parent_map[wp['name']] = parent

        reported_cycles = set()
        for wp_name in wp_parent_map:
            visited = {wp_name}
            current = wp_parent_map[wp_name]
            while current in wp_parent_map:
                if current in visited:
                    cycle_key = frozenset(visited | {current})
                    if cycle_key not in reported_cycles:
                        reported_cycles.add(cycle_key)
                        self.errors.append({
                            "category": "integrity",
                            "severity": "error",
                            "path": "workProducts",
                            "issue": f"Circular partOf/mapsTo chain detected involving work product '{wp_name}'",
                            "expected": "Acyclic partOf/mapsTo relationships",
                            "actual": f"Cycle: {wp_name} -> {' -> '.join(sorted(visited - {wp_name}))} -> {current}",
                            "suggestion": "Remove one partOf or mapsTo reference to break the cycle"
                        })
                        has_errors = True
                    break
                visited.add(current)
                current = wp_parent_map.get(current)

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
                "semantic": sum(1 for w in self.warnings if w['category'] == 'semantic')
            }
        }

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

        return True  # Semantic validation never fails, only warns

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

        parent_map = {}
        for practice in practices:
            for wp in practice.get('workProducts', []):
                parent = wp.get('partOf') or wp.get('mapsTo')
                if parent:
                    parent_map[wp['name']] = parent

        for dep in self.dependencies:
            for wp in dep.get('workProducts', []):
                parent = wp.get('partOf') or wp.get('mapsTo')
                if parent and wp['name'] not in parent_map:
                    parent_map[wp['name']] = parent

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
                            "path": "workProducts",
                            "issue": f"Circular reference in WorkProduct hierarchy (partOf/mapsTo): {' → '.join(cycle)}",
                            "expected": "Acyclic work product hierarchy",
                            "actual": f"Cycle: {' → '.join(cycle)}",
                            "suggestion": "Remove one partOf or mapsTo reference to break the cycle"
                        })
                        has_errors = True
                    break
                visited.append(current)
                visited_set.add(current)
                current = parent_map[current]

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

                # Mutual exclusivity: contributesTo and mapsTo cannot coexist
                if has_contributes_to and has_maps_to:
                    self.errors.append({
                        'category': 'baseline',
                        'severity': 'error',
                        'practice': practice_name,
                        'path': path,
                        'alpha': alpha_name,
                        'issue': f'Alpha "{alpha_name}" has both contributesTo and mapsTo (mutually exclusive)',
                        'expected': 'Either contributesTo OR mapsTo, not both',
                        'actual': f'contributesTo: "{alpha.get("contributesTo")}", mapsTo: "{alpha.get("mapsTo")}"',
                        'suggestion': 'Use contributesTo for specialization (different state progression, sub-concern). Use mapsTo for variant mapping (same state progression, IS-A relationship). Remove one.'
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
    if len(sys.argv) < 4:
        print("Usage: validate-practice-json.py <practice.json> <baseline.json> <schema.json> [dep1.json dep2.json ...]", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print("  validate-practice-json.py practices/my-practice/my-practice.json \\", file=sys.stderr)
        print("                            deps/platform-adoption-kernel.json \\", file=sys.stderr)
        print("                            deps/language.schema.json", file=sys.stderr)
        print("\nWith dependency practices:", file=sys.stderr)
        print("  validate-practice-json.py practices/child/child.json \\", file=sys.stderr)
        print("                            deps/baseline.json \\", file=sys.stderr)
        print("                            deps/language.schema.json \\", file=sys.stderr)
        print("                            practices/parent/_effective-parent.json", file=sys.stderr)
        print("\nNote: If _effective-parent.json or _effective-context.json exists in the", file=sys.stderr)
        print("      practice directory, it is auto-loaded as a dependency for validation.", file=sys.stderr)
        sys.exit(1)

    practice_file = Path(sys.argv[1])
    baseline_file = Path(sys.argv[2])
    schema_file = Path(sys.argv[3])

    # Collect explicit dependency practice files from additional arguments
    dependency_files = [Path(arg) for arg in sys.argv[4:]]

    # Auto-discover dependency files in the practice directory
    for auto_name in ('_effective-parent.json', '_effective-context.json'):
        auto_path = practice_file.parent / auto_name
        if auto_path.exists() and auto_path not in dependency_files:
            print(f"Auto-discovered dependency: {auto_path}", file=sys.stderr)
            dependency_files.append(auto_path)

    # Validate
    validator = PracticeValidator(practice_file, baseline_file, schema_file, dependency_files)

    # Run all validations
    print("Validating schema...", file=sys.stderr)
    schema_valid = validator.validate_schema()

    print("Validating baseline references...", file=sys.stderr)
    baseline_valid = validator.validate_baseline_references()

    print("Validating redeclaration vs new alpha classification...", file=sys.stderr)
    redeclaration_valid = validator.validate_redeclaration_vs_new()

    print("Validating internal integrity...", file=sys.stderr)
    integrity_valid = validator.validate_internal_integrity()

    print("Validating background references...", file=sys.stderr)
    backgrounds_valid = validator.validate_backgrounds()

    print("Validating acyclicity constraints...", file=sys.stderr)
    acyclicity_valid = validator.validate_acyclicity()

    print("Validating semantic alignment...", file=sys.stderr)
    semantic_valid = validator.validate_semantic_alignment()

    print("Validating version constraints...", file=sys.stderr)
    validator.validate_version_constraints()

    print("Validating schema version...", file=sys.stderr)
    schema_version_valid = validator.validate_schema_version()

    # Generate report
    report = validator.generate_report()

    # Output JSON report
    print(json.dumps(report, indent=2))

    # Exit code
    sys.exit(0 if report['valid'] else 1)


if __name__ == '__main__':
    main()

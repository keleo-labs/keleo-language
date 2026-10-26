"""Check reporting definitions and consumer-supplied results without writing assessments."""

from copy import deepcopy
from datetime import datetime, timezone
from math import isclose, isfinite
import json

from project_catalogue import named_elements, project_key, reference_key, validate_element_metadata
from signal_validation import parse_timestamp


def contract_key(report):
    return (report['metric']['metricId'], report['metric']['version'], report['metric']['description'], report['aggregation'],
            report['unit'], parse_timestamp(report['period']['start']),
            parse_timestamp(report['period']['end']), report.get('valueKind'))


def report_key(reference):
    return project_key(reference['projectId']), reference['reportName']


class ReportingValidator:
    def __init__(self, catalogue, results=(), now=None):
        self.catalogue = catalogue
        self.now = now or datetime.now(timezone.utc)
        self.gaps, self.facts, self.requirements, self.results = {}, {}, {}, {}
        self.result_checks = []
        for result in results:
            if not catalogue.check(result, 'ReportResult'):
                continue
            key = report_key(result['report'])
            if key in self.results:
                catalogue.issue('REPORT_RESULT_DUPLICATE', 'Several results supplied for the same report', key[0])
            self.results[key] = result

    def issue(self, project, report_name, code, message, **details):
        key = (project_key(project['projectId']), report_name)
        diagnostic = {'code': code, 'projectId': project['projectId'], 'reportName': report_name,
                      'issue': message, **details}
        if diagnostic not in self.gaps.setdefault(key, []):
            self.gaps[key].append(diagnostic)

    def callback(self, project, report_name):
        return lambda code, message, **details: self.issue(project, report_name, code, message, **details)

    def validate(self):
        if not self.catalogue.usable:
            return
        metric_definitions = {}
        for project in self.catalogue.projects.values():
            if project.get('reports') or project.get('reportingRequirements'):
                scope = self.catalogue.scope(project) if any(
                    e.get('narratives') for _, e in named_elements(project)) else []
                validate_element_metadata(project, [project, *scope],
                                          lambda code, message, **d: self.catalogue.issue(
                                              code, message, project['projectId'], **d))
            for report in project.get('reports', []) + project.get('reportingRequirements', []):
                metric = report['metric']
                key = metric['metricId'], metric['version']
                metric_definitions.setdefault(key, []).append((metric['description'], project, report['name']))
                if parse_timestamp(report['period']['start']) >= parse_timestamp(report['period']['end']):
                    self.catalogue.issue('REPORT_PERIOD_INVALID', 'Reporting period must have start before end',
                                         project['projectId'], path=report['name'])
            self.validate_requirements(project)
        for declarations in metric_definitions.values():
            if len({description for description, _, _ in declarations}) > 1:
                for _, project, name in declarations:
                    self.issue(project, name, 'REPORT_METRIC_DEFINITION_CONFLICT',
                               'The same metric identity/version has different semantic definitions')
        for project in self.catalogue.projects.values():
            for report in project.get('reports', []):
                facts = self.source_facts(project, report)
                seen = {}
                for fact in facts:
                    key = self.lineage(fact)
                    if key in seen and not self.facts_equal(fact, seen[key]):
                        self.issue(project, report['name'], 'REPORT_LINEAGE_CONFLICT',
                                   'Original contribution has conflicting facts or weighting', source=fact['source'])
                    seen[key] = fact
        for project in self.catalogue.projects.values():
            for report in project.get('reports', []):
                self.validate_coverage(project, report)
        # Propagate descendant gaps after every report's own requirements and coverage are known.
        for _ in range(len(self.catalogue.projects)):
            changed = False
            for project in self.catalogue.projects.values():
                for report in project.get('reports', []):
                    before = len(self.gaps.get((project_key(project['projectId']), report['name']), []))
                    for binding in report['bindings']:
                        if binding['sourceKind'] == 'report' and self.gaps.get(report_key(binding['source'])):
                            self.issue(project, report['name'], 'REPORT_CHILD_INCOMPLETE',
                                       'A child report is incomplete', source=binding['source'])
                    changed |= before != len(self.gaps.get((project_key(project['projectId']), report['name']), []))
            if not changed:
                break
        for key, result in sorted(self.results.items(), key=lambda entry: -len(self.catalogue.ancestors(entry[0][0]))):
            self.validate_result(key, result)

    def validate_requirements(self, project):
        effective = {}
        for ancestor in self.catalogue.ancestors(project['projectId']):
            local_ids = set()
            for requirement in ancestor.get('reportingRequirements', []):
                identity = requirement['requirementId']
                origin = ancestor['projectId']
                previous = effective.get(identity)
                conflict = identity in local_ids or requirement.get('suppressed', False) or 'specificityName' in requirement
                local_ids.add(identity)
                if previous:
                    old, old_origin = previous
                    conflict |= (old['version'] != requirement['version'] or
                                 contract_key(old) != contract_key(requirement) or
                                 (old.get('coverAllChildren', False) and not requirement.get('coverAllChildren', False)) or
                                 (not old.get('allowExclusions', False) and requirement.get('allowExclusions', False)) or
                                 ('maxSourceAgeSeconds' in old and 'maxSourceAgeSeconds' in requirement and
                                  requirement['maxSourceAgeSeconds'] > old['maxSourceAgeSeconds']))
                    merged = deepcopy(old)
                    merged['coverAllChildren'] = old.get('coverAllChildren', False) or requirement.get('coverAllChildren', False)
                    merged['allowExclusions'] = old.get('allowExclusions', False) and requirement.get('allowExclusions', False)
                    ages = [r['maxSourceAgeSeconds'] for r in (old, requirement) if 'maxSourceAgeSeconds' in r]
                    if ages:
                        merged['maxSourceAgeSeconds'] = min(ages)
                    effective[identity] = merged, old_origin
                else:
                    effective[identity] = deepcopy(requirement), origin
                if conflict:
                    bindings = [b for b in project.get('reportingRequirementBindings', []) if b['requirementId'] == identity]
                    name = bindings[0]['reportName'] if bindings else requirement['name']
                    self.issue(project, name, 'REQUIREMENT_CONFLICT', 'Incompatible inherited requirement declarations',
                               requirementId=identity, originatingProjectId=effective[identity][1],
                               source={'projectId': origin, 'requirementId': identity, 'version': requirement['version']},
                               relatedReferences=[{'projectId': effective[identity][1], 'requirementId': identity,
                                                   'version': effective[identity][0]['version']}])
        self.requirements[project_key(project['projectId'])] = effective
        for binding in project.get('reportingRequirementBindings', []):
            if binding['requirementId'] not in effective:
                self.issue(project, binding['reportName'], 'REQUIREMENT_UNRESOLVED', 'Binding names an unknown requirement',
                           requirementId=binding['requirementId'], source=binding)
        for identity, (requirement, origin) in effective.items():
            bindings = [b for b in project.get('reportingRequirementBindings', []) if b['requirementId'] == identity]
            name = bindings[0]['reportName'] if bindings else requirement['name']
            if len(bindings) != 1:
                candidates = [r['name'] for r in project.get('reports', []) if contract_key(r) == contract_key(requirement)]
                for candidate in candidates or [name]:
                    self.issue(project, candidate, 'REQUIREMENT_MAPPING_MISSING', 'Requirement needs exactly one explicit local report mapping',
                               requirementId=identity, originatingProjectId=origin, source={'requirementId': identity})
                continue
            report = self.catalogue.report({'projectId': project['projectId'], 'reportName': name}, self.callback(project, name))
            if report and (bindings[0]['version'] != requirement['version'] or contract_key(report) != contract_key(requirement)):
                self.issue(project, name, 'REQUIREMENT_REPORT_MISMATCH', 'Report does not satisfy the inherited measurement contract',
                           requirementId=identity, originatingProjectId=origin, source=bindings[0])

    def source_facts(self, project, report, stack=()):
        key = project_key(project['projectId']), report['name']
        if key in self.facts:
            return self.facts[key]
        if key in stack:
            self.issue(project, report['name'], 'REPORT_CYCLE', 'Report references contain a cycle')
            return []
        issue, facts, names = self.callback(project, report['name']), [], set()
        for binding in report['bindings']:
            if binding['name'] in names:
                self.catalogue.issue('REPORT_BINDING_AMBIGUOUS', 'Binding names must be unique in a report', project['projectId'])
            names.add(binding['name'])
            source = binding['source']
            if binding['sourceKind'] == 'report':
                child = self.catalogue.project(source['projectId'], issue)
                child_report = self.catalogue.report(source, issue)
                if not child or not child_report:
                    continue
                if project_key(child.get('parentProject', {}).get('projectId', child['projectId'])) != key[0]:
                    issue('REPORT_NOT_IMMEDIATE_CHILD', 'Report sources must be immediate owning children', source=source)
                    continue
                if contract_key(child_report) != contract_key(report):
                    issue('REPORT_CONTRACT_MISMATCH', 'Child report has an incompatible measurement contract', source=source)
                    continue
                for fact in self.source_facts(child, child_report, (*stack, key)):
                    facts.append({**fact, 'bindingName': binding['name'], 'via': [*fact.get('via', []), source]})
                continue
            if project_key(source['projectId']) != key[0]:
                issue('REPORT_NONLOCAL_SOURCE', 'Instance bindings must refer to this project', source=source)
                continue
            item = self.catalogue.item(source, issue)
            if item is None:
                continue
            if binding['sourceKind'] == 'outcome':
                if report['aggregation'] != 'sum' or source['collection'] not in ('outcomes', 'cycles.outcomes'):
                    issue('REPORT_SOURCE_KIND_MISMATCH', 'Numeric outcome bindings require an outcome source and sum report', source=source)
                elif binding['valueSource'] == 'derived':
                    facts.extend(self.derived_facts(project, report, binding, item))
                else:
                    field = report['valueKind'] + 'Value'
                    if field not in item:
                        issue('REPORT_VALUE_MISSING', f'Source has no explicit {field}', source=source)
                    else:
                        fact = self.fact(project, report, binding, source, item, value=item[field])
                        if fact:
                            facts.append(fact)
            else:
                if report['aggregation'] != 'attainmentCount' or source['collection'] not in ('current.alphaInstances', 'current.workProductInstances'):
                    issue('REPORT_SOURCE_KIND_MISMATCH', 'Attainment sources must be current assessments', source=source)
                    continue
                target = self.catalogue.item(binding['target'], issue)
                if project_key(binding['target']['projectId']) != key[0] or binding['target']['collection'] not in (
                        'target.alphaInstances', 'target.workProductInstances', 'cycles.alphaInstances', 'cycles.workProductInstances'):
                    issue('REPORT_TARGET_INVALID', 'Assessment target must be a local target or cycle objective', source=binding['target'])
                    continue
                if target:
                    attained, evidence = self.attainment(project, item, target, binding, issue)
                    fact = self.fact(project, report, binding, source, item, attained=attained, evidence=evidence)
                    if fact:
                        facts.append(fact)
        self.facts[key] = facts
        return facts

    def fact(self, project, report, binding, source, item, **values):
        issue = self.callback(project, report['name'])
        if 'value' in values and not isfinite(values['value']):
            issue('REPORT_VALUE_INVALID', 'Numeric source values must be finite', source=source)
            return None
        metadata = item.get('reportingSource', {})
        if 'value' in values and not metadata:
            issue('REPORT_MEASUREMENT_UNDECLARED', 'Numeric sources need explicit metric identity and period', source=source)
            return None
        if metadata and (metadata['metric']['metricId'] != report['metric']['metricId'] or
                         metadata['metric']['version'] != report['metric']['version'] or
                         metadata['metric']['description'] != report['metric']['description'] or
                         tuple(map(parse_timestamp, (metadata['period']['start'], metadata['period']['end']))) !=
                         tuple(map(parse_timestamp, (report['period']['start'], report['period']['end'])))):
            issue('REPORT_MEASUREMENT_MISMATCH', 'Source metric meaning/version or period differs from report', source=source)
            return None
        if 'value' in values and item.get('unit') != report['unit']:
            issue('REPORT_UNIT_MISMATCH', 'Source and report units differ', source=source)
            return None
        revision = self.catalogue.revisions.get(project_key(project['projectId']))
        if revision is None:
            issue('REPORT_REVISION_UNKNOWN', 'Source project has no catalogue revision', source=source)
        identity = metadata.get('identity', {'namespace': 'project:' + project_key(project['projectId']),
                                             'key': '/'.join(str(v) for v in reference_key(source)[1:4] if v is not None)})
        original_source = metadata.get('originalSource', source)
        delegated = self.catalogue.delegated_origin(source)
        if delegated:
            if metadata and ('alphaName' in item or 'workProductName' in item) and metadata['identity'] != delegated[0]:
                issue('REPORT_DELEGATION_ORIGIN_CONFLICT', 'Source identity differs from its committed delegation', source=source)
            if not metadata:
                identity = delegated[0]
            original_source = metadata.get('originalSource', delegated[1])
        fact = {'bindingName': binding['name'], 'origin': identity, 'originalSource': original_source,
                'source': source, 'metricId': report['metric']['metricId'], 'metricVersion': report['metric']['version'],
                'unit': report['unit'], 'period': report['period'], 'inputRevision': revision,
                'evidence': values.pop('evidence', [item['evidence']] if item.get('evidence') else []), **values}
        if report['aggregation'] == 'sum':
            fact['valueKind'] = report['valueKind']
        for field in ('observedAt', 'synchronizedAt', 'integrationName'):
            if field in metadata:
                fact[field] = metadata[field]
        return fact

    def derived_facts(self, project, report, binding, outcome):
        issue = self.callback(project, report['name'])
        if report['valueKind'] == 'target':
            issue('REPORT_TARGET_DERIVATION_INVALID', 'Targets must use explicit targetValue without forecast weighting', source=binding['source'])
            return []
        scope = self.catalogue.scope(project, issue)
        definitions = [o for doc in scope for o in doc.get('outcomes', []) if o['name'] == outcome['outcomeName']]
        contributions = [c for definition in definitions for c in definition.get('metricContributions', [])]
        if not contributions:
            issue('REPORT_DERIVATION_UNRESOLVED', 'Outcome has no resolved metric contributions', source=binding['source'])
            return []
        facts = []
        alphas = {a['name']: a for doc in reversed(scope) for a in doc.get('alphas', [])}
        work_products = project.get('current', {}).get('workProductInstances', [])
        declared_wps = project['plan']['pattern'].get('workProductInstanceNames', [])
        for contribution in contributions:
            for alpha in project.get('current', {}).get('alphaInstances', []):
                if alpha['alphaName'] != contribution['alphaName'] and alphas.get(alpha['alphaName'], {}).get('mapsTo') != contribution['alphaName']:
                    continue
                if report['valueKind'] == 'forecast':
                    weights = contribution.get('forecastWeights')
                    weight = next((w['weight'] for w in weights if w['stateName'] == alpha['stateName']), 0) if weights is not None else int(alpha['stateName'] == contribution.get('recognizedAtStateName'))
                else:
                    if 'recognizedAtStateName' not in contribution:
                        issue('REPORT_RECOGNITION_UNDEFINED', 'Derived actuals require an explicit recognition state', source=binding['source'])
                        continue
                    weight = int(alpha['stateName'] == contribution['recognizedAtStateName'])
                evidence_names = {wp['name'] for wp in alpha.get('evidenceBy', [])}
                # Follow only explicit instance containment, never type/name similarity.
                for _ in range(len(declared_wps)):
                    expanded = {wp['name'] for wp in declared_wps if any(
                        r.get('relationshipKind') == 'containment' and r['direction'] == 'outgoing'
                        and r.get('workProductInstanceName') in evidence_names for r in wp.get('relatesTo', []))}
                    if expanded <= evidence_names:
                        break
                    evidence_names |= expanded
                for wp in work_products:
                    if wp['name'] not in evidence_names or contribution.get('workProductName', wp['workProductName']) != wp['workProductName']:
                        continue
                    metrics = [m for m in wp.get('metrics', []) if m['name'] == contribution['metricName']]
                    if len(metrics) != 1:
                        issue('REPORT_METRIC_MISSING', 'Expected one matching canonical work-product metric', source=binding['source'])
                        continue
                    metric = metrics[0]
                    source = {'projectId': project['projectId'], 'collection': 'current.workProductInstances', 'instanceName': wp['name']}
                    fact = self.fact(project, report, binding, source, metric,
                                     value=metric['value'] * weight, rawValue=metric['value'], weight=weight)
                    if fact:
                        facts.append(fact)
        if not facts:
            issue('REPORT_INPUT_MISSING', 'No contributing canonical metric instances resolved', source=binding['source'])
        return facts

    def attainment(self, project, current, target, binding, issue):
        alpha = 'alphaName' in current
        type_field, phase_field, collection = ('alphaName', 'stateName', 'alphas') if alpha else ('workProductName', 'levelOfDetailName', 'workProducts')
        if current[type_field] != target.get(type_field):
            issue('REPORT_TARGET_TYPE_MISMATCH', 'Current and target assessments must use the same local type', source=binding['target'])
            return False, []
        scope = self.catalogue.scope(project, issue)
        definitions = [e for doc in scope for e in doc.get(collection, []) if e['name'] == current[type_field]]
        phases = {s['name']: s for definition in definitions for s in definition.get('states' if alpha else 'levelsOfDetail', [])}
        if target[phase_field] not in phases or current[phase_field] not in phases:
            issue('REPORT_ASSESSMENT_UNRESOLVED', 'Assessment state/level is absent from its own methodology', source=binding['source'])
            return False, []
        goal, actual = phases[target[phase_field]], phases[current[phase_field]]
        reached = current[phase_field] == target[phase_field] or (
            not any(p.get('loopsBackTo') for p in phases.values()) and actual['seq'] >= goal['seq'])
        target_flags = {c['checklistName']: c['state'] for c in target.get('checklistStates', [])}
        current_flags = {c['checklistName']: c for c in current.get('checklistStates', [])}
        threshold = project.get('priorityThreshold', 'could')
        if binding['target'].get('cycleName'):
            cycle = next(c for c in project['cycles'] if c['name'] == binding['target']['cycleName'])
            threshold = cycle.get('priorityThreshold', threshold)
        priorities = {'must': 0, 'should': 1, 'could': 2}
        evidence = []
        for checklist in goal['checklist']:
            name = checklist['name']
            flag = target_flags.get(name)
            required = flag != 'not required' and (flag is not None or priorities[checklist.get('priority', 'must')] <= priorities[threshold])
            if not required:
                continue
            record = current_flags.get(name, {})
            if record.get('state') != 'complete' or not record.get('evidence'):
                reached = False
            else:
                evidence.append(record['evidence'])
            for requirement in checklist.get('evidencedBy', []):
                canonical = {w['name']: w for w in project.get('current', {}).get('workProductInstances', [])}
                candidates = [canonical[w['name']] for w in current.get('evidenceBy', []) if w['name'] in canonical]
                if not any(w['workProductName'] == requirement['workProductName'] and
                           w['levelOfDetailName'] == requirement['levelOfDetailName'] for w in candidates):
                    reached = False
        return reached, evidence

    def validate_coverage(self, project, report):
        issue = self.callback(project, report['name'])
        coverage = report.get('childCoverage', [])
        entries = {project_key(c['projectId']): c for c in coverage}
        if len(entries) != len(coverage):
            issue('REPORT_COVERAGE_DUPLICATE', 'Child coverage must contain each child at most once')
        bindings = {b['name']: b for b in report['bindings']}
        relevant = [(r, origin) for identity, (r, origin) in self.requirements.get(project_key(project['projectId']), {}).items()
                    if any(b['requirementId'] == identity and b['reportName'] == report['name'] for b in project.get('reportingRequirementBindings', []))]
        all_children = any(r.get('coverAllChildren') for r, _ in relevant)
        allow_exclusions = bool(relevant) and all(r.get('allowExclusions', False) for r, _ in relevant)
        if all_children:
            for child in self.catalogue.children(project['projectId']):
                if project_key(child['projectId']) not in entries:
                    requirement, origin = next((r, o) for r, o in relevant if r.get('coverAllChildren'))
                    issue('REPORT_CHILD_MAPPING_MISSING', 'Immediate child has no declared coverage mapping',
                          requirementId=requirement['requirementId'], originatingProjectId=origin,
                          source={'projectId': child['projectId']})
        for key, entry in entries.items():
            child = self.catalogue.project(entry['projectId'], issue)
            if child and project_key(child.get('parentProject', {}).get('projectId', child['projectId'])) != project_key(project['projectId']):
                issue('REPORT_COVERAGE_NOT_CHILD', 'Coverage entry is not an immediate owning child', source=entry)
            if 'exclusionReason' in entry:
                if relevant and not allow_exclusions:
                    issue('REPORT_EXCLUSION_FORBIDDEN', 'An inherited requirement prohibits this exclusion', source=entry,
                          requirementId=relevant[0][0]['requirementId'], originatingProjectId=relevant[0][1])
                if any(b['sourceKind'] == 'report' and project_key(b['source']['projectId']) == key for b in report['bindings']):
                    issue('REPORT_EXCLUSION_CONFLICT', 'An excluded child also has a contribution binding', source=entry)
            else:
                for name in entry['bindingNames']:
                    binding = bindings.get(name)
                    if not binding or binding['sourceKind'] != 'report' or project_key(binding['source']['projectId']) != key:
                        issue('REPORT_COVERAGE_BINDING_INVALID', 'Coverage must name this child\'s report bindings', source=entry)
        for requirement, origin in relevant:
            if 'maxSourceAgeSeconds' not in requirement:
                continue
            for fact in self.facts.get((project_key(project['projectId']), report['name']), []):
                timestamp = self.freshness(fact)
                code = None
                if timestamp is None:
                    code = 'REPORT_SOURCE_AGE_UNKNOWN'
                elif timestamp > self.now or (self.now - timestamp).total_seconds() > requirement['maxSourceAgeSeconds']:
                    code = 'REPORT_SOURCE_TOO_OLD'
                if code:
                    issue(code, 'Source freshness does not satisfy the inherited age limit', requirementId=requirement['requirementId'],
                          originatingProjectId=origin, source=fact['source'])

    def freshness(self, fact):
        timestamp = fact.get('observedAt') or fact.get('synchronizedAt')
        if timestamp is None and fact.get('integrationName'):
            project = self.catalogue.projects.get(project_key(fact['source']['projectId']), {})
            integrations = [i for i in project.get('integrations', []) if i['name'] == fact['integrationName']]
            timestamp = integrations[0].get('lastSyncedAt') if len(integrations) == 1 else None
        if timestamp:
            try:
                parsed = parse_timestamp(timestamp)
                return parsed if parsed.tzinfo is not None else None
            except (ValueError, TypeError):
                return None
        return None

    @staticmethod
    def lineage(fact):
        return (fact['origin']['namespace'], fact['origin']['key'], fact['metricId'], fact['metricVersion'],
                parse_timestamp(fact['period']['start']), parse_timestamp(fact['period']['end']), fact.get('valueKind'))

    @staticmethod
    def facts_equal(left, right):
        fields = ('origin', 'metricId', 'metricVersion', 'unit', 'inputRevision', 'valueKind',
                  'value', 'attained', 'weight', 'rawValue', 'evidence', 'observedAt', 'synchronizedAt', 'integrationName')
        return (all(left.get(f) == right.get(f) for f in fields)
                and reference_key(left['source']) == reference_key(right['source'])
                and reference_key(left['originalSource']) == reference_key(right['originalSource'])
                and left['period'] == right['period'])

    def validate_result(self, key, result):
        project = self.catalogue.projects.get(key[0])
        if project is None:
            self.catalogue.issue('REPORT_RESULT_UNRESOLVED', 'Result names an unknown project', key[0])
            return
        report = self.catalogue.report(result['report'], self.callback(project, key[1]))
        if report is None:
            return
        issue = self.callback(project, key[1])
        for binding in report['bindings']:
            if binding['sourceKind'] == 'report' and self.gaps.get(report_key(binding['source'])):
                issue('REPORT_CHILD_INCOMPLETE', 'A supplied child report is incomplete', source=binding['source'])
        if parse_timestamp(result['calculatedAt']) > self.now:
            issue('REPORT_CALCULATION_FUTURE', 'Calculation timestamp is in the future')
        expected = self.facts.get(key, [])
        unique, expected_unique = {}, {}
        for fact in expected:
            identity = self.lineage(fact)
            if identity in expected_unique and not self.facts_equal(fact, expected_unique[identity]):
                issue('REPORT_LINEAGE_CONFLICT', 'Original contribution has conflicting facts or weighting', source=fact['source'])
            expected_unique[identity] = fact
        for fact in result['contributions']:
            identity = self.lineage(fact)
            matches = [f for f in expected if f['bindingName'] == fact['bindingName'] and self.lineage(f) == identity]
            if not any(self.facts_equal(fact, candidate) for candidate in matches):
                issue('REPORT_CONTRIBUTION_INVALID', 'Contribution does not match its bound source snapshot', source=fact['source'])
            if 'via' in fact and not any([report_key(r) for r in fact['via']] == [report_key(r) for r in candidate.get('via', [])] for candidate in matches):
                issue('REPORT_LINEAGE_PATH_INVALID', 'Contribution path differs from the declared reporting chain', source=fact['source'])
            if identity in unique and not self.facts_equal(unique[identity], fact):
                issue('REPORT_LINEAGE_CONFLICT', 'Repeated lineage has conflicting facts or weights', source=fact['source'])
            unique[identity] = fact
            if 'value' in fact and not isfinite(fact['value']):
                issue('REPORT_VALUE_INVALID', 'Contribution must be finite', source=fact['source'])
        if set(unique) != set(expected_unique):
            issue('REPORT_INPUT_MISSING', 'Result does not retain every expected original contribution')
        if result['coverage'] != report.get('childCoverage', []):
            issue('REPORT_COVERAGE_CHANGED', 'Result coverage differs from declared scope')
        if result['complete']:
            if self.gaps.get(key):
                self.catalogue.issue('REPORT_RESULT_FALSE_COMPLETE', 'Result claims completeness despite reporting gaps', key[0], path=key[1])
            total = sum(f.get('value', int(f.get('attained', False))) for f in unique.values())
            if not isfinite(result['total']) or not isclose(result['total'], total, rel_tol=1e-12, abs_tol=1e-12):
                self.catalogue.issue('REPORT_TOTAL_INVALID', 'Headline total does not equal unique source contributions', key[0], path=key[1])
        else:
            def diagnostic_key(diagnostic):
                return json.dumps({field: diagnostic.get(field) for field in (
                    'code', 'projectId', 'reportName', 'requirementId', 'originatingProjectId', 'source', 'relatedReferences')}, sort_keys=True)

            required = {diagnostic_key(d) for d in self.gaps.get(key, [])}
            if not required or not required <= {diagnostic_key(d) for d in result['diagnostics']}:
                self.catalogue.issue('REPORT_DIAGNOSTICS_MISSING', 'Incomplete result must retain its structured gap diagnostics', key[0], path=key[1])
        self.result_checks.append({'report': result['report'], 'complete': result['complete'] and not self.gaps.get(key),
                                   'diagnostics': self.gaps.get(key, [])})

    def summary(self):
        diagnostics = [d for group in self.gaps.values() for d in group]
        ancestry_unknown = not self.catalogue.supplied and any(w['code'] == 'PARENT_UNRESOLVED' for w in self.catalogue.warnings)
        return {'alignmentComplete': None if ancestry_unknown else not diagnostics, 'diagnostics': diagnostics, 'results': self.result_checks,
                'sourceFreshness': [{'report': {'projectId': key[0], 'reportName': key[1]},
                                     'source': fact['source'], 'known': self.freshness(fact) is not None}
                                    for key, facts in self.facts.items() for fact in facts]}

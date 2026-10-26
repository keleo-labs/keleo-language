"""Validate explicit delegation previews, immutable history and application authority."""

from copy import deepcopy

from project_catalogue import (document_revision, project_key,
                               reference_key, validate_element_metadata)
from reporting_validation import contract_key
from signal_validation import document_type, parse_timestamp


def template_payload(template):
    """Composition metadata may change visibility, never executable mappings."""
    if isinstance(template, list):
        return [template_payload(item) for item in template]
    if not isinstance(template, dict):
        return template
    metadata = {'tags', 'narratives', 'assetNames', 'specificityName', 'specificity', 'suppressed', 'contributingPatternName'}
    if 'metricId' not in template:
        metadata.add('description')
    return {key: template_payload(value) for key, value in template.items() if key not in metadata}


def validate_templates(context, document, scope):
    templates = {}
    for owner in reversed(scope):
        owner_scope = context.methodology_scope(owner)
        inherited = [t for dependency in owner_scope if dependency is not owner
                     for t in dependency.get('projectCreationTemplates', [])]
        validate_element_metadata(owner, scope, context.issue, inherited)
        for template in owner.get('projectCreationTemplates', []):
            key = template['name'], template['version']
            if key in templates and template_payload(templates[key]) != template_payload(template):
                context.issue('TEMPLATE_CONFLICT', 'Template identity/version has conflicting executable contents', source={'templateName': key[0], 'version': key[1]})
            templates[key] = template
            selectors = {s['name']: s for s in template['selectors']}
            variants = {v['name']: v for v in template['variants']}
            if len(selectors) != len(template['selectors']) or len(variants) != len(template['variants']):
                context.issue('TEMPLATE_NAME_AMBIGUOUS', 'Selector and variant names must be unique', path=template['name'])
            if template.get('defaultVariantName') and template['defaultVariantName'] not in variants:
                context.issue('TEMPLATE_VARIANT_UNRESOLVED', 'Default variant does not exist', path=template['name'])
            roots = [e for doc in scope for e in doc.get('alphas' if template['rootKind'] == 'alpha' else 'workProducts', [])
                     if e['name'] == template['rootTypeName']]
            if not roots:
                context.issue('TEMPLATE_ROOT_UNRESOLVED', 'Template root type is absent from its methodology', path=template['name'])
            for variant in template['variants']:
                for mapping in variant['instanceMappings'] + variant['actionMappings']:
                    if mapping['selectorName'] not in selectors:
                        context.issue('TEMPLATE_SELECTOR_UNRESOLVED', 'Mapping names an undefined selector', path=variant['name'])
                for binding in variant['reportingBindings']:
                    if binding.get('valueKind') == 'target' and binding.get('valueSource') != 'recorded':
                        context.issue('REPORT_TARGET_DERIVATION_INVALID', 'Template targets must use recorded targetValue', path=binding['name'])
    return templates


class DelegationValidator:
    def __init__(self, catalogue):
        self.catalogue = catalogue
        self.operations, self.results = {}, []

    def issue(self, code, message, **details):
        warning = not self.catalogue.preflight and not self.catalogue.supplied and code.endswith('_UNRESOLVED')
        self.catalogue.issue(code, message, warning=warning, **details)

    def validate(self, previews=()):
        if not self.catalogue.usable:
            return
        owners = {}
        for project in self.catalogue.projects.values():
            for operation in project.get('delegations', []):
                preview = operation['preview']
                identity = preview['operationId']
                previous = self.operations.get(identity)
                if previous:
                    self.issue('DELEGATION_OPERATION_CONFLICT', 'Operation identity has conflicting records', project_id=project['projectId'])
                self.operations[identity] = operation
                if project_key(preview['parentProjectId']) != project_key(project['projectId']):
                    self.issue('DELEGATION_WRONG_PARENT', 'Delegation must be recorded by its parent', project_id=project['projectId'])
                if operation['status'] == 'committed':
                    for reference in preview['selectedItems']:
                        key = reference_key(reference)
                        if key in owners and owners[key] != identity:
                            self.issue('DELEGATION_SECOND_OWNER', 'Selected detail has two committed owners', source=reference)
                        owners[key] = identity
        for project in self.catalogue.projects.values():
            for operation in project.get('delegations', []):
                if operation['status'] == 'committed':
                    self.committed(project, operation)
                else:
                    self.preview(operation['preview'], require_authority=False)
                    child = self.catalogue.projects.get(project_key(operation['preview']['child']['projectId']))
                    if child and any(child.get('current', {}).get(c) for c in ('alphaInstances', 'workProductInstances')):
                        self.issue('DELEGATION_SECOND_OWNER', 'Uncommitted child detail must stay outside the active catalogue', project_id=child['projectId'])
            for card in project.get('recommendations', []):
                if 'localRecommendation' in card:
                    self.recommendation(project, card)
        for preview in previews:
            self.preview(preview)

    def preview(self, preview, require_authority=True):
        if not self.catalogue.check(preview, 'ProjectCreationPreview'):
            return
        existing = self.operations.get(preview['operationId'])
        if existing and existing['status'] == 'committed':
            if existing['preview'] != preview:
                self.issue('DELEGATION_OPERATION_CONFLICT', 'A successful operation cannot be reused with different inputs')
            else:
                self.results.append({'operationId': preview['operationId'], 'childProjectId': preview['child']['projectId'], 'existing': True})
            return
        parent = self.catalogue.project(preview['parentProjectId'], self.issue)
        if parent is None:
            return
        child = preview['child']
        if project_key(child['projectId']) in self.catalogue.projects:
            self.issue('DELEGATION_CHILD_ID_IN_USE', 'Child UUID is already enrolled', project_id=child['projectId'])
        if project_key(child.get('parentProject', {}).get('projectId', child['projectId'])) != project_key(parent['projectId']):
            self.issue('DELEGATION_CHILD_OWNER_INVALID', 'Proposed child must declare this parent', project_id=child['projectId'])
        if project_key(preview['source']['projectId']) != project_key(parent['projectId']):
            self.issue('DELEGATION_SOURCE_INVALID', 'Source item must belong to the parent', source=preview['source'])
            return
        source = self.catalogue.item(preview['source'], self.issue)
        methodology = self.catalogue.methodology(preview['template']['methodology'], self.issue)
        if source is None or methodology is None:
            return
        scope = self.catalogue.scope(parent, self.issue)
        if methodology not in scope:
            self.issue('DELEGATION_TEMPLATE_OUT_OF_SCOPE', 'Template methodology is not in the parent dependency scope')
            return
        templates = validate_templates(self.catalogue, methodology, self.catalogue.methodology_scope(methodology, self.issue))
        template = templates.get((preview['template']['templateName'], preview['template']['version']))
        if not template or template.get('suppressed'):
            self.issue('DELEGATION_TEMPLATE_UNRESOLVED', 'Pinned creation template is missing or suppressed')
            return
        root_collection = 'plan.pattern.alphaInstanceNames' if template['rootKind'] == 'alpha' else 'plan.pattern.workProductInstanceNames'
        type_field = 'alphaName' if template['rootKind'] == 'alpha' else 'workProductName'
        if preview['source']['collection'] != root_collection or source.get(type_field) != template['rootTypeName']:
            self.issue('DELEGATION_ROOT_INVALID', 'Source must be the applicable tracked root declaration', source=preview['source'])
        variant = next((v for v in template['variants'] if v['name'] == preview['variantName']), None)
        if variant is None:
            self.issue('DELEGATION_VARIANT_UNRESOLVED', 'Selected method variant does not exist')
            return
        child_method = self.catalogue.methodology(variant['methodology'], self.issue)
        expected_field = variant['methodology']['documentType'] + 'Name'
        if child.get(expected_field) != variant['methodology']['documentName']:
            self.issue('DELEGATION_METHOD_MISMATCH', 'Child does not use the selected methodology')
        consulted = [*scope]
        if child_method:
            consulted.extend(self.catalogue.methodology_scope(child_method, self.issue))
        self.revisions(preview, parent, consulted)
        selected = set()
        expanded = {}
        for selector in template['selectors']:
            items = self.select(parent, preview['source'], source, selector)
            expanded[selector['name']] = {reference_key(item) for item in items}
        permitted = set().union(*expanded.values())
        for item in preview['selectedItems']:
            key = reference_key(item)
            if project_key(item['projectId']) != project_key(parent['projectId']) or key not in permitted:
                self.issue('DELEGATION_SCOPE_INVALID', 'Selected item is outside explicit template scope', source=item)
            self.catalogue.item(item, self.issue)
            selected.add(key)
        if reference_key(preview['source']) not in selected:
            self.issue('DELEGATION_ROOT_MISSING', 'Confirmed scope must retain its root summary declaration')
        mapped_sources, mapped_targets = set(), set()
        for transfer in preview['instanceMappings']:
            source_key, target_key = reference_key(transfer['source']), reference_key(transfer['target'])
            if source_key in mapped_sources or target_key in mapped_targets:
                self.issue('DELEGATION_MAPPING_AMBIGUOUS', 'Instance mappings must have unique sources and targets')
            mapped_sources.add(source_key)
            mapped_targets.add(target_key)
            if source_key not in selected:
                self.issue('DELEGATION_SCOPE_INVALID', 'Instance mapping is not explicitly selected', source=transfer['source'])
                continue
            original = self.catalogue.item(transfer['source'], self.issue)
            destination = self.catalogue.item(transfer['target'], self.issue, project=child)
            if original is None or destination is None:
                continue
            self.transfer(preview, parent, child, original, destination, transfer, variant, expanded)
        self.actions(preview, parent, child, variant, expanded, selected)
        expected_selected = mapped_sources | {reference_key(m['source']) for m in preview['actionMappings']}
        if selected != expected_selected:
            self.issue('DELEGATION_MAPPING_MISSING', 'Every selected item needs an explicit instance or action mapping')
        assessed_targets = {(m['target']['instanceName'], 'alphaInstances' if 'alphaInstance' in m['target']['collection'] else 'workProductInstances')
                            for m in preview['instanceMappings'] if m['assessmentTransfer'] != 'unassessed'}
        for collection in ('alphaInstances', 'workProductInstances'):
            for assessment in child.get('current', {}).get(collection, []):
                if (assessment['name'], collection) not in assessed_targets:
                    self.issue('DELEGATION_ASSESSMENT_INVENTED', 'Child assessments must come from explicit selected transfers')
        allowed_actions = {reference_key(m['target']) for m in preview['actionMappings']}
        for container, actions in [(None, child.get('actions', [])), *[(c['name'], c.get('actions', [])) for c in child.get('cycles', [])]]:
            for action in actions:
                reference = {'projectId': child['projectId'], 'collection': 'cycles.actions' if container else 'actions', 'instanceName': action['name']}
                if container:
                    reference['cycleName'] = container
                if reference_key(reference) not in allowed_actions:
                    self.issue('DELEGATION_ACTION_UNDECLARED', 'Child actions must come from explicit selected transfers')
        self.snapshots(preview, parent)
        self.reporting(preview, variant)
        if require_authority and self.catalogue.preflight:
            self.authority(parent, preview)
        self.results.append({'operationId': preview['operationId'], 'childProjectId': child['projectId'], 'existing': False})

    def select(self, parent, root_reference, root, selector):
        if selector['selection'] == 'root':
            return [root_reference]
        if selector['selection'] == 'named':
            return [{'projectId': parent['projectId'], **item} for item in selector['items']]
        items = []
        for relationship in root.get('relatesTo', []):
            if relationship.get('relationshipKind') != selector['relationshipKind'] or relationship['direction'] != selector['direction']:
                continue
            alpha = 'alphaInstanceName' in relationship
            items.append({'projectId': parent['projectId'],
                          'collection': 'plan.pattern.alphaInstanceNames' if alpha else 'plan.pattern.workProductInstanceNames',
                          'instanceName': relationship['alphaInstanceName' if alpha else 'workProductInstanceName']})
        return items

    def revisions(self, preview, parent, consulted):
        seen = set()
        for revision in preview['sourceRevisions']:
            if 'projectId' in revision:
                key = ('project', project_key(revision['projectId']))
                current = self.catalogue.revisions.get(key[1])
                if key[1] != project_key(parent['projectId']):
                    self.issue('DELEGATION_SCOPE_INVALID', 'Preview cannot silently import other projects', source=revision)
            else:
                ref = revision['methodology']
                key = ref['documentType'], ref['documentName'], ref['version']
                document = self.catalogue.methodology(ref, self.issue)
                current = document_revision(document) if document else None
            if key in seen:
                self.issue('DELEGATION_REVISION_DUPLICATE', 'Each source revision must appear once')
            seen.add(key)
            if current is None:
                self.issue('DELEGATION_REVISION_UNRESOLVED', 'Source revision is not supplied', source=revision)
            elif current != revision['revision']:
                self.issue('DELEGATION_STALE_INPUT', 'Source revision differs from the preview', source=revision)
        required = {('project', project_key(parent['projectId']))}
        required.update((document_type(doc), doc['name'], doc.get('version')) for doc in consulted)
        if not required <= seen:
            self.issue('DELEGATION_REVISION_MISSING', 'Preview must pin parent and all consulted methodology documents')

    def transfer(self, preview, parent, child, source, target, transfer, variant, expanded):
        alpha = 'alphaName' in source
        field, phase, collection = ('alphaName', 'stateName', 'alphaInstances') if alpha else ('workProductName', 'levelOfDetailName', 'workProductInstances')
        if project_key(transfer['target']['projectId']) != project_key(child['projectId']) or transfer['target']['collection'] != (
                'plan.pattern.alphaInstanceNames' if alpha else 'plan.pattern.workProductInstanceNames'):
            self.issue('DELEGATION_DESTINATION_INVALID', 'Target must be a matching child tracked declaration', source=transfer['target'])
        rules = [m for m in variant['instanceMappings'] if reference_key(transfer['source']) in expanded.get(m['selectorName'], set())
                 and m['instanceKind'] == ('alpha' if alpha else 'workProduct')
                 and m['sourceTypeName'] == source.get(field) and m['targetTypeName'] == target.get(field)]
        if len(rules) != 1:
            self.issue('DELEGATION_MAPPING_UNDECLARED', 'Instance mapping does not select exactly one template rule')
            return
        rule = rules[0]
        for mapping_field in ('stateMappings', 'lodMappings', 'checklistMappings'):
            if transfer.get(mapping_field, []) != rule.get(mapping_field, []):
                self.issue('DELEGATION_MAPPING_UNDECLARED', 'Preview must preserve the template assessment mappings')
        originals = [a for a in parent.get('current', {}).get(collection, []) if a['name'] == source['name']]
        destinations = [a for a in child.get('current', {}).get(collection, []) if a['name'] == target['name']]
        original = originals[0] if len(originals) == 1 else None
        destination = destinations[0] if len(destinations) == 1 else None
        current_reference = {'projectId': parent['projectId'], 'collection': 'current.' + collection, 'instanceName': source['name']}
        metadata = original.get('reportingSource', {}) if original else {}
        identity = metadata.get('identity', {'namespace': 'project:' + project_key(parent['projectId']), 'key': 'current.' + collection + '/' + source['name']})
        original_source = metadata.get('originalSource', current_reference)
        delegated = self.catalogue.delegated_origin(current_reference)
        if delegated:
            identity, original_source = delegated
        if transfer['origin'] != identity or reference_key(transfer['originalSource']) != reference_key(original_source):
            self.issue('DELEGATION_ORIGIN_CHANGED', 'Delegation must preserve original contribution identity')
        self.phase_references(self.catalogue.scope(parent, self.issue), self.catalogue.scope(child, self.issue),
                              source[field], original.get(phase) if original else None, alpha, rule, target[field])
        if transfer['assessmentTransfer'] == 'unassessed':
            if destination:
                self.issue('DELEGATION_ASSESSMENT_INVENTED', 'Unmapped target must have no current assessment')
            return
        if not original or not destination:
            self.issue('DELEGATION_ASSESSMENT_MISSING', 'An assessment transfer requires source and destination assessments')
            return
        same_method = parent.get('practiceName', parent.get('methodName')) == child.get('practiceName', child.get('methodName'))
        expected = deepcopy(original)
        expected['name'], expected[field] = target['name'], target[field]
        if original.get('evidenceBy'):
            references = []
            for evidence in original['evidenceBy']:
                mappings = [m for m in preview['instanceMappings'] if 'workProductInstance' in m['source']['collection']
                            and m['source']['instanceName'] == evidence['name'] and m['assessmentTransfer'] != 'unassessed']
                current = [wp for wp in child.get('current', {}).get('workProductInstances', [])
                           if len(mappings) == 1 and wp['name'] == mappings[0]['target']['instanceName']]
                if len(current) != 1:
                    self.issue('DELEGATION_EVIDENCE_MAPPING_MISSING', 'Embedded evidence needs an explicitly mapped canonical child work product')
                    return
                references.append(current[0])
            expected['evidenceBy'] = references
        if transfer['assessmentTransfer'] == 'copy':
            if not same_method or source[field] != target[field]:
                self.issue('DELEGATION_COPY_INCOMPATIBLE', 'Copy requires matching method and assessment type')
        else:
            maps = rule.get('stateMappings' if alpha else 'lodMappings', [])
            from_key, to_key = ('fromState', 'toState') if alpha else ('fromLevelOfDetail', 'toLevelOfDetail')
            phases = [m[to_key] for m in maps if m[from_key] == original[phase]]
            if len(phases) != 1:
                self.issue('DELEGATION_ASSESSMENT_MAPPING_MISSING', 'Absent or ambiguous phase mappings require an unassessed target')
                return
            expected[phase] = phases[0]
            flags = []
            for flag in original.get('checklistStates', []):
                mappings = [m for m in rule.get('checklistMappings', []) if m['fromStateOrLevel'] == original[phase]
                            and m['fromChecklist'] == flag['checklistName'] and m['toStateOrLevel'] == expected[phase]]
                if len(mappings) == 1:
                    flags.append({**flag, 'checklistName': mappings[0]['toChecklist']})
                else:
                    self.issue('DELEGATION_CHECKLIST_MAPPING_AMBIGUOUS', 'Missing or ambiguous checklist mappings require an unassessed target')
                    return
            if 'checklistStates' in expected:
                expected['checklistStates'] = flags
        # A destination may explicitly attach the preserved original provenance.
        if 'reportingSource' not in expected and 'reportingSource' in destination:
            expected['reportingSource'] = destination['reportingSource']
            if destination['reportingSource']['identity'] != identity:
                self.issue('DELEGATION_ORIGIN_CHANGED', 'Destination provenance must preserve original source identity')
        if destination != expected:
            self.issue('DELEGATION_ASSESSMENT_CHANGED', 'Transferred assessment/evidence differs from the explicit mapping')
    def phase_references(self, source_scope, target_scope, source_type, source_phase, alpha, rule, target_type):
        collection, phases = ('alphas', 'states') if alpha else ('workProducts', 'levelsOfDetail')
        sources = {s['name']: s for doc in source_scope for e in doc.get(collection, []) if e['name'] == source_type for s in e.get(phases, [])}
        targets = {s['name']: s for doc in target_scope for e in doc.get(collection, []) if e['name'] == target_type for s in e.get(phases, [])}
        if not sources or not targets or (source_phase is not None and source_phase not in sources):
            self.issue('DELEGATION_ASSESSMENT_UNRESOLVED', 'Mapping types/states must resolve in their own methodology scopes')
        from_key, to_key = ('fromState', 'toState') if alpha else ('fromLevelOfDetail', 'toLevelOfDetail')
        for mapping in rule.get('stateMappings' if alpha else 'lodMappings', []):
            if mapping[to_key] not in targets or mapping[from_key] not in sources:
                self.issue('DELEGATION_ASSESSMENT_UNRESOLVED', 'Mapped destination phase is undefined')
        for mapping in rule.get('checklistMappings', []):
            target = targets.get(mapping['toStateOrLevel'], {})
            source = sources.get(mapping['fromStateOrLevel'], {})
            if not any(c['name'] == mapping['toChecklist'] for c in target.get('checklist', [])) or not any(c['name'] == mapping['fromChecklist'] for c in source.get('checklist', [])):
                self.issue('DELEGATION_CHECKLIST_UNRESOLVED', 'Mapped destination checklist is undefined')

    def actions(self, preview, parent, child, variant, expanded, selected):
        targets, sources = set(), set()
        members = {m['name'] for m in child.get('team', {}).get('members', [])}
        mapped_instances = {m['source']['instanceName']: m['target']['instanceName'] for m in preview['instanceMappings']}
        for transfer in preview['actionMappings']:
            source_key, target_key = reference_key(transfer['source']), reference_key(transfer['target'])
            if source_key in sources or target_key in targets:
                self.issue('DELEGATION_ACTION_AMBIGUOUS', 'Action transfer sources and targets must be unique')
            sources.add(source_key)
            targets.add(target_key)
            if source_key not in selected or transfer['source']['collection'] not in ('actions', 'cycles.actions'):
                self.issue('DELEGATION_SCOPE_INVALID', 'Only explicitly selected actions may transfer')
                continue
            rules = [m for m in variant['actionMappings'] if source_key in expanded.get(m['selectorName'], set())]
            if len(rules) != 1:
                self.issue('DELEGATION_ACTION_UNDECLARED', 'Action transfer has no unique template rule')
                continue
            rule = rules[0]
            if transfer['assigneeMappings'] != rule['assigneeMappings']:
                self.issue('DELEGATION_ACTION_UNDECLARED', 'Assignee mappings differ from the template')
            source = self.catalogue.item(transfer['source'], self.issue)
            target = self.catalogue.item(transfer['target'], self.issue, project=child)
            if source is None or target is None:
                continue
            expected_collection = 'cycles.actions' if rule.get('targetCycleName') else 'actions'
            if project_key(transfer['target']['projectId']) != project_key(child['projectId']) or transfer['target']['collection'] != expected_collection or transfer['target'].get('cycleName') != rule.get('targetCycleName'):
                self.issue('DELEGATION_ACTION_DESTINATION_INVALID', 'Action destination differs from its declared cycle')
            if source.get('status') in ('done', 'discarded') or source.get('completedAt'):
                self.issue('DELEGATION_ACTION_CLOSED', 'Closed actions cannot transfer')
            assignments = {m['from']: m['to'] for m in transfer['assigneeMappings']}
            if len(assignments) != len(transfer['assigneeMappings']):
                self.issue('DELEGATION_ASSIGNMENT_AMBIGUOUS', 'Assignee mappings must have unique sources')
            if any(person not in assignments or assignments[person] not in members for person in source.get('assignedTo', [])):
                self.issue('DELEGATION_ASSIGNMENT_UNRESOLVED', 'Every transferred assignment needs a valid destination member')
            expected = {**source, 'name': target['name']}
            if 'assignedTo' in source:
                expected['assignedTo'] = [assignments.get(person) for person in source['assignedTo']]
            for field in ('advancesAlphaInstances', 'developsWorkProductInstances'):
                if field in source:
                    if any(name not in mapped_instances for name in source[field]):
                        self.issue('DELEGATION_ACTION_REFERENCE_UNRESOLVED', 'Action references unselected detail')
                    expected[field] = [mapped_instances.get(name) for name in source[field]]
            if expected != target:
                self.issue('DELEGATION_ACTION_CHANGED', 'Action differs from the declared transfer')
            outcome_names = {o['name'] for o in child.get('outcomes', [])}
            if transfer['target'].get('cycleName'):
                cycle = next((c for c in child.get('cycles', []) if c['name'] == transfer['target']['cycleName']), {})
                outcome_names |= {o['name'] for o in cycle.get('outcomes', [])}
            if any(name not in outcome_names for name in target.get('outcomeInstanceNames', [])):
                self.issue('DELEGATION_ACTION_REFERENCE_UNRESOLVED', 'Action outcome references must resolve in the child')

    def snapshots(self, preview, parent):
        expected = set()
        for transfer in preview['instanceMappings']:
            collection = 'current.alphaInstances' if 'alphaInstance' in transfer['source']['collection'] else 'current.workProductInstances'
            reference = {**transfer['source'], 'collection': collection}
            if any(item['name'] == reference['instanceName'] for item in self.catalogue.items(parent, reference)):
                expected.add(reference_key(reference))
        expected |= {reference_key(m['source']) for m in preview['actionMappings']}
        actual = set()
        for record in preview['sourceSnapshots']:
            reference = record['source']
            if project_key(reference['projectId']) != project_key(parent['projectId']):
                self.issue('DELEGATION_HISTORY_INVALID', 'History must identify the parent source')
            item = self.catalogue.item(reference, self.issue)
            if item != record['snapshot']:
                self.issue('DELEGATION_HISTORY_INVALID', 'Historical snapshot differs from source input')
            actual.add(reference_key(reference))
        if actual != expected or len(actual) != len(preview['sourceSnapshots']):
            self.issue('DELEGATION_HISTORY_MISSING', 'Preserve every transferred assessment and action exactly once')

    def reporting(self, preview, variant):
        mappings = preview['reportingBindings']
        if len(mappings) != len(variant['reportingBindings']):
            self.issue('DELEGATION_REPORT_MAPPING_MISSING', 'Every template reporting binding must be expanded')
        for template in variant['reportingBindings']:
            matches = [m for m in mappings if m['parentReportName'] == template['parentReportName'] and m['childReport']['name'] == template['childReportName']]
            if len(matches) != 1:
                self.issue('DELEGATION_REPORT_MAPPING_MISSING', 'Template report mapping is absent or ambiguous')
                continue
            mapping = matches[0]
            report = mapping['childReport']
            source = {'projectId': preview['child']['projectId'], **template['source']}
            if contract_key(report) != contract_key(template):
                self.issue('DELEGATION_REPORT_CONTRACT_MISMATCH', 'Child report differs from template measurement contract')
            bindings = [b for b in report['bindings'] if b['source'] == source]
            if len(bindings) != 1 or bindings[0].get('valueSource') != template.get('valueSource'):
                self.issue('DELEGATION_REPORT_MAPPING_INVALID', 'Child report must use the declared local source')
            if bindings and template.get('target') and bindings[0].get('target') != {'projectId': preview['child']['projectId'], **template['target']}:
                self.issue('DELEGATION_REPORT_MAPPING_INVALID', 'Child attainment report must use the declared target')
            parent_binding = mapping['parentBinding']
            if parent_binding['sourceKind'] != 'report' or parent_binding['source'] != {'projectId': preview['child']['projectId'], 'reportName': template['childReportName']}:
                self.issue('DELEGATION_REPORT_MAPPING_INVALID', 'Parent summary must bind the child report')
            if report not in preview['child'].get('reports', []):
                self.issue('DELEGATION_REPORT_MAPPING_MISSING', 'Proposed child must contain its declared report')

    def authority(self, parent, preview, attempted_at=None, mode=None, policy_name=None):
        name = policy_name or preview.get('policyName')
        if mode == 'manual' or (mode is None and not name):
            if not preview.get('confirmedBy') or not preview.get('confirmedAt'):
                self.issue('DELEGATION_CONFIRMATION_REQUIRED', 'Confirm selected method and scope before creation')
            elif attempted_at and parse_timestamp(preview['confirmedAt']) > parse_timestamp(attempted_at):
                self.issue('DELEGATION_CONFIRMATION_REQUIRED', 'Confirmation must precede application')
            return
        policies = [p for p in parent.get('recommendationPolicies', []) if p['name'] == name]
        policy = policies[0] if len(policies) == 1 else None
        if not policy or policy.get('template') != preview['template'] or reference_key(policy.get('source', preview['source'])) != reference_key(preview['source']):
            self.issue('DELEGATION_AUTHORITY_MISSING', 'Automatic creation needs a matching template/version and source policy')
        elif policy.get('revokedAt') and (attempted_at is None or parse_timestamp(attempted_at) >= parse_timestamp(policy['revokedAt'])):
            self.issue('DELEGATION_AUTHORITY_REVOKED', 'Automatic creation policy is revoked')

    def committed(self, parent, operation):
        preview = operation['preview']
        child = self.catalogue.project(preview['child']['projectId'], self.issue)
        if child is None:
            return
        if project_key(child.get('parentProject', {}).get('projectId', child['projectId'])) != project_key(parent['projectId']):
            self.issue('DELEGATION_CHILD_OWNER_INVALID', 'Committed child must declare its owning parent')
        selected = {reference_key(r) for r in preview['selectedItems']}
        mapped = {reference_key(m['source']) for m in preview['instanceMappings'] + preview['actionMappings']}
        if selected != mapped or reference_key(preview['source']) not in selected or any(
                project_key(r['projectId']) != project_key(parent['projectId']) for r in preview['selectedItems']):
            self.issue('DELEGATION_SCOPE_INVALID', 'Committed mappings must retain exactly their selected parent scope')
        methodology = self.catalogue.methodology(preview['template']['methodology'], self.issue)
        if methodology:
            scope = self.catalogue.methodology_scope(methodology, self.issue)
            templates = validate_templates(self.catalogue, methodology, scope)
            template = templates.get((preview['template']['templateName'], preview['template']['version']))
            variant = next((v for v in template['variants'] if v['name'] == preview['variantName']), None) if template else None
            if not variant:
                self.issue('DELEGATION_TEMPLATE_UNRESOLVED', 'Committed operation must retain its pinned template and variant')
            else:
                self.reporting(preview, variant)
                child_field = variant['methodology']['documentType'] + 'Name'
                if preview['child'].get(child_field) != variant['methodology']['documentName']:
                    self.issue('DELEGATION_METHOD_MISMATCH', 'Committed preview differs from its selected methodology')
        for revision in preview['sourceRevisions']:
            if 'methodology' in revision:
                document = self.catalogue.methodology(revision['methodology'], self.issue)
                if document and document_revision(document) != revision['revision']:
                    self.issue('DELEGATION_HISTORY_INVALID', 'Pinned historical methodology content has changed')
        if operation['history'] != preview['sourceSnapshots']:
            self.issue('DELEGATION_HISTORY_MISSING', 'Commit must retain the preview\'s attributed source snapshots')
        if not any(r['name'] == operation['summaryReportName'] for r in parent.get('reports', [])):
            self.issue('DELEGATION_SUMMARY_UNRESOLVED', 'Parent summary report must remain available')
        else:
            report = next(r for r in parent['reports'] if r['name'] == operation['summaryReportName'])
            if not any(b['sourceKind'] == 'report' and project_key(b['source']['projectId']) == project_key(child['projectId']) for b in report['bindings']):
                self.issue('DELEGATION_SUMMARY_UNRESOLVED', 'Summary must explicitly reference the committed child report')
        if parse_timestamp(operation['committedAt']) < max((parse_timestamp(h['recordedAt']) for h in operation['history']), default=parse_timestamp(operation['committedAt'])):
            self.issue('DELEGATION_HISTORY_INVALID', 'History snapshots must precede commitment')
        self.authority(parent, preview, operation['committedAt'])
        root_key = reference_key(preview['source'])
        for transfer in preview['instanceMappings']:
            if project_key(transfer['target']['projectId']) != project_key(child['projectId']):
                self.issue('DELEGATION_DESTINATION_INVALID', 'Committed detail must belong to the recorded child')
            self.catalogue.item(transfer['target'], self.issue)
            if reference_key(transfer['source']) != root_key:
                remaining = [i for i in self.catalogue.items(parent, transfer['source']) if i['name'] == transfer['source']['instanceName']]
                if remaining:
                    self.issue('DELEGATION_SECOND_OWNER', 'Delegated detail must not remain an editable parent declaration', source=transfer['source'])
        for transfer in preview['actionMappings']:
            if project_key(transfer['target']['projectId']) != project_key(child['projectId']):
                self.issue('DELEGATION_ACTION_DESTINATION_INVALID', 'Committed action must belong to the recorded child')
            self.catalogue.item(transfer['target'], self.issue)
        for record in operation['history']:
            active = [i for i in self.catalogue.items(parent, record['source']) if i['name'] == record['source']['instanceName']]
            if active and (active[0] == record['snapshot'] or active[0].get('reportingSource', {}).get('identity') == preview_origin(preview, record['source'])):
                self.issue('DELEGATION_SECOND_OWNER', 'Historical detail cannot remain a current editable assessment/action', source=record['source'])
        self.results.append({'operationId': preview['operationId'], 'childProjectId': child['projectId'], 'existing': True})

    def recommendation(self, project, card):
        recommendation = card['localRecommendation']
        preview = recommendation['proposal']
        if reference_key(recommendation['source']) != reference_key(preview['source']) or project_key(project['projectId']) != project_key(preview['parentProjectId']):
            self.issue('DELEGATION_RECOMMENDATION_SOURCE_INVALID', 'Recommendation and proposal must identify the same local source')
        attempts = card.get('applications', [])
        for attempt in attempts:
            self.authority(project, preview, attempt['attemptedAt'], attempt['mode'], attempt.get('policyName'))
            if attempt['outcome'] == 'succeeded':
                expected = [{'operationId': preview['operationId'], 'childProjectId': preview['child']['projectId']}]
                if attempt['results'] != expected:
                    self.issue('DELEGATION_RECEIPT_INVALID', 'Application result must identify the proposed operation and child')
                operation = self.operations.get(preview['operationId'])
                if not operation or operation['status'] != 'committed' or operation['preview'] != preview:
                    self.issue('DELEGATION_RECEIPT_UNRESOLVED', 'Successful application requires the matching committed delegation')
        if self.catalogue.preflight and card['status'] == 'accepted':
            self.preview(preview)


def preview_origin(preview, source):
    return next((m['origin'] for m in preview['instanceMappings']
                 if m['source']['instanceName'] == source['instanceName']), None)

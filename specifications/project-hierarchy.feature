@schema-4.0.0 @rfe-26 @rfe-27 @rfe-28 @rfe-29
Feature: Independent projects with explicit ownership and reporting

  Scenario: Rename a project without breaking references
    Given another project references a project by UUID
    When the referenced project's name changes
    Then the reference still resolves to the same project

  Scenario: Require project identity
    Given a project without a UUID
    When schema 4 validation runs
    Then validation rejects the project without assigning an identity

  Scenario: Reject contradictory ownership
    Given a catalogue contains duplicate identities or an ownership cycle
    When ownership is validated
    Then structured diagnostics identify the conflicting projects

  Scenario: Detect a folder disagreement
    Given a consumer supplies the physical parent of a project
    When it differs from the declared owner
    Then a diagnostic identifies both references

  Scenario: Aggregate declared targets independently
    Given two children declare compatible targets of 100 and 200
    And the parent declares its own target of 400
    When the child-target report is validated
    Then its total is 300
    And the parent's declared target remains 400

  Scenario: Preserve contribution lineage
    Given repeated reporting paths carry the same original contribution
    When their result is validated
    Then the contribution is counted once
    And conflicting values or weights withhold the headline total

  Scenario: Keep actual forecast and target separate
    Given a source has actual forecast and target values
    When its reports are validated
    Then each report uses its declared value kind
    And target contributions have no forecast weighting

  Scenario: Preserve local assessment ownership
    Given assessed instances use different methods and explicit targets
    When evidenced attainment is reported
    Then each instance is assessed using its own method
    And the parent's own assessments are unchanged

  Scenario: Describe discoverable definitions
    Given a report requirement or creation template is authored
    When it is validated
    Then its name and description are required
    And its tags narratives and asset references are supported

  Scenario: Preview explicit delegation
    Given a source item has typed associations and an applicable template
    When child creation is previewed
    Then only explicitly selected scope is included
    And the selected method and source revisions are recorded

  Scenario: Reject a stale preview
    Given a creation preview records source revisions
    When a source revision changes
    Then operation preflight requires a refreshed preview

  Scenario: Preserve an unmapped assessment
    Given a source assessment has no mapping in the chosen child method
    When child creation is previewed
    Then the target remains unassessed
    And the source assessment remains in its attributed history

  Scenario: Retry a successful operation
    Given a delegation operation has already committed a child
    When the same operation is validated again
    Then it identifies that existing child
    And a second successful child is rejected

  Scenario: Recover from failed creation
    Given detail is owned by the parent
    When creation fails before commitment
    Then the parent retains ownership
    And no second active owner is reported

  Scenario: Recommend delegation from local work
    Given a local item is a candidate for delegation
    When its recommendation is accepted
    Then no external signal is required
    And successful application still requires an authorised receipt

  Scenario: Preserve an inherited target obligation
    Given an ancestor requires target reporting in GBP for a defined period
    When a descendant binds an actual report to that requirement
    Then alignment reports a value-kind conflict
    And the affected target report is incomplete

  Scenario: Preserve reporting scope
    Given a report expects contributions from its children
    When a new unmapped child appears or a configured child disappears
    Then the affected report has a visible coverage gap

  Scenario: Inspect explicit exclusions
    Given every applicable requirement permits exclusions
    When a child is excluded with a reason
    Then the exclusion and reason remain in report coverage

  Scenario: Evaluate source freshness
    Given an inherited requirement limits source age
    When a contribution has no known source timestamp
    Then freshness does not satisfy the requirement
    And recalculation time cannot make the source current

  Scenario: Keep local work usable during an alignment gap
    Given a child satisfies its local project schema
    And it lacks a report required by its ancestor
    When catalogue validation runs
    Then the child remains locally valid
    And the affected ancestor report is incomplete

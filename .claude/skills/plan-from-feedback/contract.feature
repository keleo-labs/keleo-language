Feature: Plan from Feedback — keleo-language
  As the maintainer of the Practice Language
  I want issues triaged and resolved from this project's tracker
  So that schema, semantics and validation stay in step and consumers are not broken silently

  Background:
    Given keleo-labs/keleo-language is a public GitHub repository with issues enabled
    And the feedback foundation defines the workflow, routing and sanitisation rules
    And this project does not read the feedback register

  # --- Queue ---

  Scenario: Queue comes from this project's tracker
    Given issues exist on keleo-labs/keleo-language
    When the resolution workflow begins
    Then the queue is read from the tracker
    And the feedback register is not consulted

  Scenario: Issue routed here from the register
    Given an issue body names a register row
    When it is triaged
    Then the row is read for context
    And the resolution is still recorded on the issue

  # --- Three-layer coverage ---

  Scenario: Structural constraint reaches all three layers
    Given an issue reports that a construct cannot express what a domain needs
    When the fix is applied
    Then the schema carries the constraint
    And the semantics document it
    And a validator enforces it

  Scenario: Change touching only one layer is incomplete
    Given a constraint has been added to the schema alone
    When the change is reviewed before closing
    Then the missing semantics or validation is identified as outstanding
    And the issue is not closed until all applicable layers are covered

  Scenario: Rule that JSON Schema cannot express
    Given a constraint depends on relationships between documents
    When the fix is planned
    Then it is stated in references/semantics/
    And enforced by a validator rather than the schema

  # --- Upstream obligation ---

  Scenario: Downstream corpus re-validated before closing
    Given a change modified the schema or a validator
    When the issue is ready to close
    Then the keleo-pgen-llm corpus is scanned for new errors
    And an error in a document nobody edited is attributed to this change

  Scenario: Deliberately breaking change
    Given a change invalidates documents that were previously valid
    When it is accepted
    Then the schema major version is bumped
    And the migration path is stated on the issue
    And an issue is filed on each affected consumer project

  Scenario: No level to escalate to
    Given an issue cannot be resolved within schema, semantics or validation
    When the resolution is planned
    Then it is resolved here rather than escalated
    And any consumer-side consequence is filed on that consumer

  # --- Validation ---

  Scenario: Validators run without an install step
    Given a fresh machine with no jsonschema installed
    When a Python validator is run
    Then it bootstraps its own environment and completes

  Scenario: Schema correctness is not proven by the validators alone
    Given the validators pass against the changed schema
    When the change is verified
    Then the downstream corpus run is also required
    And conformance alone is not treated as evidence the schema is right

  # --- Closing ---

  Scenario: Change links to its issue
    Given a commit resolves an issue
    When the commit message is written
    Then it carries "Refs" or "Closes" with the issue number

  Scenario: Cross-project defect is filed, not fixed
    Given an issue reveals a defect in a consumer project
    When the resolution is planned
    Then an issue is filed on that project
    And its code is not edited from here

@rfe-23 @schema-3.3.0
Feature: External signals and contextual recommendations
  External evidence informs methodology and project decisions without granting
  automation implicit authority to change either.

  Scenario: Discover investment relevant to an account project
    Given an account project whose practice defines Initiative and Opportunity
    When an annual report announcing IT modernisation is recorded
    Then the journal retains its source passage and discovery time
    And recommendations identify the account context and proposed instances

  Scenario: Relate content to a methodology
    Given external content relevant to a practice or method
    When a recommendation is recorded without a project
    Then its methodology and element references can be validated
    And methodology changes require review

  Scenario: Manage responses independently
    Given two projects reference the same journal recommendation
    When one project dismisses its card
    Then the other project's workflow state is unchanged

  Scenario: Accept advice without applying a change
    Given an information-only recommendation
    When a project accepts the advice
    Then the card may remain accepted without an application receipt
    And marking it applied is invalid

  Scenario: Apply under an explicit project policy
    Given a project policy authorises the rule version and proposed operations
    When successful automatic application is recorded
    Then the card is applied and identifies the resulting instances or actions

  Scenario: Reject unauthorised automatic application
    Given no project policy authorises the recommendation
    When successful automatic application is recorded
    Then validation reports an application authority error

  Scenario: Revoke future authority without invalidating history
    Given a policy authorises an earlier successful application
    When that policy is revoked at a later instant
    Then the earlier application remains valid
    And automatic attempts at or after revocation are rejected

  Scenario: Preserve an application failure
    Given an accepted recommendation
    When application fails
    Then the card remains accepted and retains the failed attempt

  Scenario: Avoid duplicate discovery and application
    Given a discovery already has a recommendation and project card
    When duplicate source identities, cards or successful receipts are recorded
    Then validation rejects the duplicates

  Scenario: Reject a conflicting update
    Given a proposal records the previous value of an existing instance
    When that instance changes before application
    Then preflight validation rejects the stale proposal

  Scenario: Preserve revised evidence
    Given a recommendation is superseded by a new recommendation
    When the old card is still awaiting application
    Then validation rejects application of the superseded proposal
    And historical successful application remains valid

  Scenario: Resolve only the project's shared journal contexts
    Given a journal contains recommendations for several projects
    When one project validates its recommendation cards for application
    Then other projects' context documents need not be loaded

  Scenario: Retain independent mapping versions
    Given historical recommendations reference an earlier mapping version
    When the earlier and newer mapping versions are loaded together
    Then each recommendation resolves its recorded rule version

  Scenario: Preserve existing integrations
    Given an existing mapping containing only entity mappings
    When the mapping is validated against schema 3.3.0
    Then signal rules and journal records are not required

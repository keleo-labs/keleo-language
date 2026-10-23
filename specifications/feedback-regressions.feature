Feature: Composition guidance and validation diagnostics

  Scenario: Baseline group templates are deprecated
    Given a baseline declares a pattern group with empty entries
    When the baseline is validated
    Then a deprecation warning identifies patternGroups
    And the warning does not invalidate the baseline

  Scenario: A populated orchestration has no progression
    Given several practices contribute only on-demand or hosted stages to one orchestration
    When their merged orchestration is validated
    Then one warning reports that it has no sequential stage

  Scenario: A dependency supplies progression
    Given a dependency contributes a sequential stage to an orchestration
    And the extending practice contributes an on-demand stage
    When their merged orchestration is validated
    Then no missing-sequential-stage warning is reported

  Scenario: An empty orchestration shell awaits contributions
    Given an orchestration has no stages in any loaded document
    When it is validated
    Then no missing-sequential-stage warning is reported

  Scenario: An overlay retargets a loop
    Given a base loop declares a target and a condition
    And an overlay declares a different loop target without a condition
    When the declarations merge
    Then the overlay replaces the whole loop object including removal of the base condition

  Scenario: A reference does not veto suppression
    Given a practice suppresses an inherited element
    And another loaded document references it without redeclaring it
    When suppression resolves
    Then the element is removed
    And a surviving reference to it is reported as an error

  Scenario: A suppression retains authoring requirements
    Given an inherited alpha has three states
    When a practice suppresses it using the example in composition section 4.9
    Then the declaration conforms to the Alpha schema
    And all three inherited states are restated

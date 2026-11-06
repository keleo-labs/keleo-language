Feature: Layered baseline alpha relationships and state progressions
  As a practice author
  I want a derived baseline to build on its declared parent
  So that its relationships and progression resolve without changing the parent

  Scenario: Contribution to a declared parent alpha
    Given a parent baseline defines alpha "Deliverable"
    And a derived baseline declares the parent in baselinePracticeNames
    And its alpha "Platform" contributesTo "Deliverable"
    When the derived baseline is validated with the parent
    Then the contribution is valid

  Scenario: Invalid contribution target or cycle
    Given a derived baseline declares a contributesTo target that is missing or cyclic
    When the derived baseline is validated
    Then validation reports an error for that relationship

  Scenario: Explicit replacement of inherited states
    Given a parent baseline defines alpha "Governance" with three states
    And a derived baseline redeclares "Governance" with five states and inheritedStatePolicy "replace"
    When the derived baseline is resolved
    Then "Governance" has exactly the derived baseline's five states
    And the parent baseline still has its original three states

  Scenario: State replacement without an inherited alpha
    Given an alpha is new to a baseline or belongs to an extension practice
    And it declares inheritedStatePolicy "replace"
    When the document is validated
    Then validation reports that replacement is unavailable there

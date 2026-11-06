Feature: Layered baseline alpha relationships
  As a practice author
  I want a derived baseline to build on its declared parent
  So that its relationships resolve through the declared parent

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

Feature: Project assessment policy

  Scenario: Migrate priority scope
    Given a v5 Project sets project and cycle priority thresholds
    When the Project migrates to v6
    Then the thresholds keep their effective scope at the same levels
    And the project has no selected assessment rigour

  Scenario: Keep existing attainment rules without an explicit rigour
    Given a project omits assessment rigour
    When a report evaluates attainment
    Then the existing checklist evidence rules apply
    And the report omits assessment rigour

  Scenario Outline: Report attainment at the selected rigour
    Given a reached assessment uses <rigour>
    When a report evaluates attainment
    Then attainment requires <record>
    And the report identifies the selected rigour

    Examples:
      | rigour                | record                                  |
      | team-reported         | a dated confirmation of the assessment  |
      | source-supported      | source evidence for the assessment      |
      | evidence-per-item     | evidence for every applicable item      |
      | evidence-and-sign-off | evidence and sign-off for every applicable item |

  Scenario: Assess an objective with no applicable items
    Given an item-level policy and a resolved objective with every item out of scope
    When a report evaluates attainment
    Then source evidence for the assessment is required

  Scenario: Replace evidence after sign-off
    Given a reviewer confirmed the evidence for an applicable item
    When the evidence changes
    Then the project remains valid
    And attainment under the evidence and sign-off policy stays pending until a reviewer confirms the replacement

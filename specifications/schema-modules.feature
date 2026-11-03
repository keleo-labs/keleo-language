Feature: Modular Practice Language schemas
  Practice Language documents have the same constraints through either entry point.

  Scenario: Existing documents validate through either entry point
    Given an existing Practice Language document
    When it is validated against the modular and compatibility schemas
    Then both entry points return the same validity result

  Scenario: Invalid documents fail through either entry point
    Given a baseline alpha without its required name
    When the baseline is validated against both entry points
    Then both entry points reject it

  Scenario: A definition references another module
    Given the Alpha definition extends PracticeElement
    When the modular schema resolves Alpha
    Then PracticeElement is resolved from the common module

  Scenario: The compatibility schema retains definition pointers
    Given every definition belongs to one modular schema
    When the compatibility schema is built
    Then each definition remains available at its existing $defs pointer
    And a second build produces the same schema

  Scenario: Authoring catalogs stay separate from the language bundle
    Given the four local catalog schemas are stored under schemas/catalogs
    When the compatibility schema is built
    Then catalog definitions are not added to the Practice Language schema
    And each catalog remains validatable on its own

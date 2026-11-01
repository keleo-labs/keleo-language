Feature: Local authoring catalogs
  As a practice engineer
  I want reusable source snapshots and a catalog of practice elements
  So that later amendments can find their evidence without rereading every source

  Scenario: Reuse a source across practices
    Given two practice catalogs link to a section in one source snapshot
    When their source links are validated
    Then both links resolve to the same section ID

  Scenario: Source revision changes
    Given a source snapshot is linked from a practice catalog
    When a later source revision is captured
    Then the earlier snapshot remains available
    And the earlier section IDs are no longer current for new claims

  Scenario: Practice changes after indexing
    Given a practice catalog records a practice JSON digest
    When the practice JSON changes
    Then catalog validation reports a digest mismatch

  Scenario: Source link is missing
    Given a practice element links to a source section ID
    When that ID is absent from the source workspace
    Then catalog validation fails

  Scenario: Catalogs stay local
    Given a practice and its two catalogs are available
    When a .keleo package is built
    Then the package contains the practice and its existing citations
    And it does not contain either catalog

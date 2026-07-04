## ADDED Requirements

### Requirement: Default agent identity SHALL be OpenBuffett
The system MUST expose the default research agent as `OpenBuffett` across its active runtime surfaces, default prompt identity, current user-facing documentation, and current test expectations. The active product surface MUST NOT continue presenting `SmartIPO` as the default brand identity.

#### Scenario: Default agent composition is built
- **WHEN** the system creates the default local agent
- **THEN** the exported brand identity and default system prompt MUST identify the agent as `OpenBuffett`

#### Scenario: Current runtime surface is shown to a user
- **WHEN** a user opens the active workbench or reads the current README and active package metadata
- **THEN** the visible product identity MUST use `OpenBuffett` rather than `SmartIPO`

### Requirement: Default self-description SHALL reflect valuation-first capability priority
The default agent self-description MUST present capabilities in the following order: professional valuation analysis first, IPO subscription analysis second, and market-data auxiliary analysis third. When the agent recommends example questions, it MUST reflect this priority order instead of leading with generic IPO-first prompts.

#### Scenario: Agent introduces its capabilities
- **WHEN** the system surfaces the default self-introduction or recommended question set
- **THEN** it MUST emphasize valuation analysis before IPO subscription analysis and market-data assistance

### Requirement: Completed research SHALL end with a report-generation follow-up
After the agent completes a full research answer, it MUST proactively ask whether the user wants a Markdown research report generated in the current working directory. The follow-up MUST treat Chinese Simplified as the default report language and MUST frame the report as conclusion-first with explicit evidence support and admitted unknowns.

#### Scenario: A full research answer completes
- **WHEN** the agent finishes a complete valuation or IPO subscription analysis
- **THEN** it MUST ask whether to generate a Chinese Markdown report in the current working directory

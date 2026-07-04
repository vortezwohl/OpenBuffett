## ADDED Requirements

### Requirement: TUI SHALL show an assistant opening message before the first user turn
The workbench TUI MUST display a proactive assistant opening message immediately after startup, before the user submits the first message. This opening message MUST introduce the agent, summarize what it can help with, and recommend example questions in the default capability-priority order.

#### Scenario: User opens the workbench
- **WHEN** the TUI finishes mounting its initial screen
- **THEN** the timeline MUST already contain a proactive assistant opening message before any user input is submitted

### Requirement: Opening copy SHALL be maintained as a dedicated exported constant
The startup opening message MUST be maintained as a dedicated exported constant rather than as an inline TUI-only literal. The TUI MUST consume that constant instead of owning a separate hard-coded product introduction string.

#### Scenario: Opening copy is updated
- **WHEN** maintainers update the default opening message
- **THEN** they MUST be able to change a dedicated exported constant without editing scattered inline TUI literals

### Requirement: Active TUI surface SHALL present OpenBuffett branding
The active TUI surface MUST present `OpenBuffett` as its title, system-message brand, and default input affordance branding. The current runtime surface MUST NOT continue exposing `SmartIPO` as the default user-facing label.

#### Scenario: User inspects the active workbench chrome
- **WHEN** the TUI title, system banners, or input placeholder are rendered
- **THEN** those runtime-facing labels MUST use `OpenBuffett` branding

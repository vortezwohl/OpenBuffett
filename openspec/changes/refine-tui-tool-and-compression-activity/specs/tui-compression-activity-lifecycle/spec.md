## ADDED Requirements

### Requirement: Compression activity MUST be represented by a single timeline item per run
SmartIPO TUI MUST treat one compression run as one local timeline activity. A `compress started` event MUST create or activate a compression item, and the matching terminal event MUST update that same item instead of appending a second visible message.

#### Scenario: Started and completed compression collapse into one visible entry
- **WHEN** the TUI receives a `compress` event with `started` status and later receives a matching `completed` status for the same run
- **THEN** the visible timeline MUST contain exactly one compression entry for that run
- **AND** that entry MUST stop counting time after completion

#### Scenario: Started and failed compression still collapse into one visible entry
- **WHEN** the TUI receives a `compress` event with `started` status and later receives a matching `failed` status for the same run
- **THEN** the visible timeline MUST contain exactly one compression entry for that run
- **AND** the failed terminal text MUST replace the temporary running text on that same entry

### Requirement: Successful compression MUST surface the exact terminal message `Conversation compressed`
When a compression run completes successfully, SmartIPO TUI MUST render the final visible message as `Conversation compressed`.

#### Scenario: Successful compression uses the new terminal copy
- **WHEN** a compression run reaches `completed`
- **THEN** the visible compression entry MUST read `duration 路 Conversation compressed`

### Requirement: Failed or cancelled compression MUST preserve truthful terminal semantics
SmartIPO TUI MUST keep compression failure and cancellation distinct from successful completion. A failed or cancelled compression run MUST NOT be rendered as `Conversation compressed`.

#### Scenario: Failed compression remains a failure message
- **WHEN** a compression run reaches `failed`
- **THEN** the visible compression entry MUST describe failure rather than success
- **AND** it MUST NOT render the terminal message `Conversation compressed`

#### Scenario: Cancelled compression remains an interrupted message
- **WHEN** a compression run reaches `cancelled`
- **THEN** the visible compression entry MUST describe interruption rather than success
- **AND** it MUST NOT render the terminal message `Conversation compressed`

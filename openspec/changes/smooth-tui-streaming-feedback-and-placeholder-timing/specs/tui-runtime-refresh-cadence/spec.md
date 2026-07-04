## ADDED Requirements

### Requirement: Active timeline refresh MUST use a global 10ms cadence
SmartIPO TUI MUST run its active-turn timeline refresh loop on a global `10ms` interval while the application is mounted.

#### Scenario: running items and display backlogs advance on the 10ms global refresh
- **WHEN** the application has mounted and an active turn is present
- **THEN** the TUI MUST use the same global `10ms` refresh cadence to advance running durations, deferred placeholder checks, and visible text reveal work
- **AND** the system MUST NOT keep the previous `50ms` active timeline refresh interval

### Requirement: Thinking indicator animation MUST advance every 100ms
SmartIPO TUI MUST animate running `Thinking` indicators using a `100ms` frame cadence for the `.` / `..` / `...` cycle.

#### Scenario: waiting placeholder uses the 100ms animation cadence
- **WHEN** a turn is currently showing the temporary local `Thinking` placeholder
- **THEN** the visible dot animation MUST advance on `100ms` frame boundaries

#### Scenario: real running thinking uses the 100ms animation cadence
- **WHEN** runtime has entered a real active `thinking` phase that has not yet been preserved as stable history
- **THEN** the visible dot animation for that running thinking indicator MUST advance on `100ms` frame boundaries

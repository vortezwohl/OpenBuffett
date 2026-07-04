## ADDED Requirements

### Requirement: The initial Thinking placeholder MUST remain visible for at least 50ms
SmartIPO TUI MUST keep the turn's initial local `Thinking ...` placeholder visible for at least `50ms` before any real runtime action is allowed to visually replace it.

#### Scenario: first tool activity arrives before the 50ms minimum visibility window ends
- **WHEN** a new turn has started and its local `Thinking ...` placeholder has been visible for less than `50ms`
- **AND** the first real runtime action arrives as `tool started`
- **THEN** the TUI MUST continue showing the placeholder until the `50ms` minimum visibility window has elapsed
- **AND** the tool activity MUST NOT visually replace the placeholder before that threshold

#### Scenario: first assistant or thinking text arrives before the 50ms minimum visibility window ends
- **WHEN** a new turn has started and its local `Thinking ...` placeholder has been visible for less than `50ms`
- **AND** the first real runtime action arrives as visible `thinking` or `assistant` output
- **THEN** the TUI MUST continue showing the placeholder until the `50ms` minimum visibility window has elapsed
- **AND** the visible runtime output MUST NOT replace the placeholder before that threshold

### Requirement: Deferred placeholder-covering events MUST replay in original order
SmartIPO TUI MUST preserve the arrival order of real runtime actions that were deferred only because the placeholder minimum-visibility window had not yet expired.

#### Scenario: multiple real actions queue behind the minimum-visibility window
- **WHEN** more than one placeholder-covering runtime event arrives during the same active `50ms` minimum-visibility window
- **THEN** the TUI MUST replay those deferred events in the same order they originally arrived
- **AND** the first visible post-placeholder action MUST match the earliest deferred runtime event

### Requirement: Placeholder buffering MUST NOT strand the turn without waiting feedback
SmartIPO TUI MUST continue to provide waiting feedback during the buffered handoff from placeholder to real activity and after real activity ends while the turn is still active.

#### Scenario: buffered first action completes and the turn still has more work ahead
- **WHEN** the initial placeholder has been replaced by a real runtime action that later reaches a terminal state
- **AND** the turn is still active with no other visible running activity
- **THEN** the TUI MUST restore waiting feedback for the turn
- **AND** the timeline MUST NOT enter a blank waiting gap with neither real activity nor `Thinking ...`

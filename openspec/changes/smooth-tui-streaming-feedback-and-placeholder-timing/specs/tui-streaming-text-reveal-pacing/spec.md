## ADDED Requirements

### Requirement: Runtime thinking and assistant text MUST reveal one character at a time in arrival order
SmartIPO TUI MUST display runtime `thinking` text and final `assistant` reply text through a single ordered reveal flow that emits visible characters one by one instead of appending each incoming delta as a full block.

#### Scenario: thinking text reveals gradually instead of jumping by delta chunk
- **WHEN** the active turn receives runtime `thinking delta` or `thinking completed` text containing multiple characters
- **THEN** the timeline MUST reveal that visible thinking history one character at a time in the same order the text was received
- **AND** the TUI MUST NOT append the whole delta chunk to the visible timeline in a single paint

#### Scenario: assistant reply reveals gradually instead of jumping by delta chunk
- **WHEN** the active turn receives runtime `assistant delta` or `assistant completed` text containing multiple characters
- **THEN** the timeline MUST reveal the visible assistant reply one character at a time in the same order the text was received
- **AND** the TUI MUST NOT append the whole delta chunk to the visible assistant message in a single paint

### Requirement: Character reveal pacing MUST use a 10ms cadence
SmartIPO TUI MUST pace visible `thinking` and `assistant` character reveal at one character per `10ms` tick while backlog is present.

#### Scenario: reveal backlog advances on each 10ms display tick
- **WHEN** the active turn has buffered visible text that has not yet been revealed
- **THEN** each `10ms` display tick MUST reveal at most the next single character from the ordered backlog
- **AND** the backlog MUST continue draining on subsequent `10ms` ticks until empty

### Requirement: Turn completion MUST wait for visible text reveal to finish
SmartIPO TUI MUST NOT mark a turn complete, failed, or cancelled for display purposes until all queued visible text for that turn has been revealed to the timeline in order.

#### Scenario: raw stream completes while assistant text still has unrevealed characters
- **WHEN** the underlying agent event stream for the active turn has already ended
- **AND** the visible `assistant` or `thinking` reveal backlog for that same turn is not yet empty
- **THEN** the TUI MUST keep the turn in an active display state
- **AND** the TUI MUST delay the final turn-complete transition until the reveal backlog is fully drained

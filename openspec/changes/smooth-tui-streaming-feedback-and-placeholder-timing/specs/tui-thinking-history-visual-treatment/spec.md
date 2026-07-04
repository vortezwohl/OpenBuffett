## ADDED Requirements

### Requirement: Preserved thinking history MUST normalize newline control characters before display
When SmartIPO TUI preserves runtime `thinking` text as visible history, it MUST normalize newline control characters before that text enters the timeline so users never see raw `\r` or `\n` line breaks inside the preserved thinking message.

#### Scenario: thinking history replaces newline characters before it becomes visible
- **WHEN** an active turn receives runtime `thinking delta` or `thinking completed` text containing `\r\n`, `\r`, or `\n`
- **THEN** the TUI MUST replace those newline control characters before the text is shown as preserved thinking history
- **AND** the visible `Assistant (Thinking) > ` history message MUST NOT contain raw carriage-return or newline characters

#### Scenario: newline normalization does not downgrade thinking to a normal assistant reply
- **WHEN** preserved runtime thinking history contains text that required newline normalization
- **THEN** the TUI MUST still render that history with the `Assistant (Thinking) > ` prefix
- **AND** the visible message MUST keep the darker thinking-history treatment instead of the normal `Assistant > ` reply treatment

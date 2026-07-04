## ADDED Requirements

### Requirement: Default SmartIPO agent MUST use an explicit 900000-token conversation window budget
The default SmartIPO agent configuration MUST set an explicit `context_window_limit` of `900000` tokens in project-owned model configuration, instead of relying on provider lookup fallback behavior.

#### Scenario: Unknown model lookup still uses explicit 900000-token limit
- **WHEN** the default SmartIPO model ID does not exist in the upstream context-window lookup table
- **THEN** the project runtime MUST still construct the default model with `context_window_limit=900000`
- **AND** proactive compression calculations MUST use that explicit limit rather than the upstream fallback default

### Requirement: Default SmartIPO summarizing manager MUST preserve the most recent 6 messages
The default SmartIPO agent configuration MUST construct its summarizing conversation manager with `preserve_recent_messages=6`.

#### Scenario: Default agent keeps 6 recent messages during summarization
- **WHEN** the project constructs the default SmartIPO agent
- **THEN** its summarizing conversation manager MUST preserve 6 recent messages
- **AND** the project MUST NOT keep the previous lower preserve count as the default

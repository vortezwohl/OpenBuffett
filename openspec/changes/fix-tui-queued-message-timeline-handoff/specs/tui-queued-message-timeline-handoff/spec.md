## ADDED Requirements

### Requirement: Queued messages remain outside the main timeline until execution starts
The TUI SHALL keep queued user submissions out of the main conversation timeline while they are still waiting in the local turn queue. A queued submission MUST remain visible through the queue tray surface until it becomes the active turn.

#### Scenario: Queued submission is only visible in the queue tray
- **WHEN** the user submits a second message while another turn is still active
- **THEN** the second message MUST appear in the queue tray
- **THEN** the second message MUST NOT appear as `User >` in the main timeline yet

#### Scenario: Multiple queued submissions stay out of the timeline
- **WHEN** the user submits multiple messages while an earlier turn is still running
- **THEN** only the active turn's user message MAY remain in the main timeline
- **THEN** every not-yet-started submission MUST remain outside the main timeline until its own execution begins

### Requirement: Starting a queued turn appends a new user timeline event at handoff time
When a queued submission becomes the active turn, the TUI SHALL append a new `User >` conversation item to the main timeline at that moment. The timeline position of that user item MUST reflect execution handoff order rather than original queue insertion order.

#### Scenario: Next queued message becomes a visible user timeline event when execution starts
- **WHEN** the current active turn finishes and the next queued turn starts
- **THEN** the queue tray entry for that next turn MUST disappear from the queue tray
- **THEN** the main timeline MUST append a new `User >` item for that next turn

#### Scenario: User timeline item appears before follow-up runtime activity of the same turn
- **WHEN** a queued turn starts and later emits local thinking, assistant, or tool activity
- **THEN** the new `User >` item for that turn MUST appear earlier in the timeline than those follow-up activities

#### Scenario: Handoff order is preserved across multiple queued turns
- **WHEN** three or more user submissions are processed sequentially from the local queue
- **THEN** each new `User >` timeline item MUST appear in the same order as turns actually start execution
- **THEN** no queued submission MAY reappear at an older historical position in the timeline

### Requirement: Queue handoff semantics remain stable after interrupted or failed turns
The TUI SHALL use the same queued-message handoff rules when the previous turn ends in failure or cancellation. Finishing one turn abnormally MUST NOT cause the next queued user submission to disappear without a corresponding `User >` timeline entry.

#### Scenario: Failed turn still hands off the next queued message into the timeline
- **WHEN** the current active turn fails and the next queued turn begins
- **THEN** the next queued message MUST leave the queue tray
- **THEN** the next queued message MUST be appended to the main timeline as a new `User >` item before its own reply activity continues

#### Scenario: Cancelled turn still hands off the next queued message into the timeline
- **WHEN** the current active turn is cancelled or interrupted and the next queued turn begins
- **THEN** the next queued message MUST be appended to the main timeline as a new `User >` item at the moment that queued turn becomes active

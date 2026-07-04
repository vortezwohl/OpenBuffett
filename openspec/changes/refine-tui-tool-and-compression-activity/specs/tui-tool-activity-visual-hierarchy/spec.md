## ADDED Requirements

### Requirement: Tool activity main line MUST omit braced syntax while preserving scan structure
SmartIPO TUI MUST render the first visible line of a tool activity as `duration 路 Tool <name> 路 <status>`. The main line MUST NOT include `{` or `}` characters, and it MUST keep the `Tool`, tool name, and status label as separately renderable segments.

#### Scenario: Running tool shows unbraced main line
- **WHEN** a tool activity enters the `started` state
- **THEN** the first visible tool line MUST match the format `duration 路 Tool <name> 路 Running`
- **AND** that line MUST NOT contain `{` or `}`

#### Scenario: Completed tool keeps summary outside the main line
- **WHEN** a tool activity completes with preview text
- **THEN** the first visible tool line MUST remain `duration 路 Tool <name> 路 Done`
- **AND** any tool summary text MUST be rendered after the main line rather than folded into braces

### Requirement: Tool activity colors MUST use secondary hierarchy instead of the brightest accent
SmartIPO TUI MUST render tool activity using secondary-tone colors rather than the brightest green or pure white currently used for chat emphasis. The `Tool` label and status label MUST remain visually distinct from ordinary tool-name or summary text.

#### Scenario: Tool label and status remain distinct from ordinary text
- **WHEN** the TUI renders a tool main line as Rich text
- **THEN** the `Tool` label and status label MUST use a non-default style distinct from ordinary body text
- **AND** the tool name text MUST use a softer secondary light tone rather than pure white

#### Scenario: Tool activity does not reuse the brightest chat accent
- **WHEN** the TUI renders a tool main line
- **THEN** the main tool label/status accent MUST NOT use the same brightest accent style reserved for stronger chat emphasis
- **AND** the visible hierarchy MUST remain readable without relying on `{}` characters

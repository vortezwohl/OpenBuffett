## ADDED Requirements

### Requirement: IPO subscription analysis SHALL be gated by pre-listing eligibility
The system MUST only treat a request as IPO subscription analysis when the target security is not yet listed and is currently open for subscription or is about to open for subscription. If the company is already listed, the system MUST not continue under an IPO subscription framing.

#### Scenario: User asks whether to subscribe to a listed company
- **WHEN** the target company is already publicly listed
- **THEN** the system MUST refuse the IPO subscription framing and fall back to ordinary post-listing valuation or market analysis

#### Scenario: User asks about an upcoming subscription candidate
- **WHEN** the target company is still pre-listing and is open or about to open for subscription
- **THEN** the system MAY continue into IPO subscription analysis

### Requirement: IPO subscription analysis SHALL build on valuation analysis
The system MUST complete or reuse a valuation analysis baseline before producing an IPO subscription recommendation. IPO subscription judgment MUST be treated as an extension of valuation work rather than as an isolated shortcut answer.

#### Scenario: User requests IPO subscription judgment without prior valuation context
- **WHEN** the user asks whether an eligible IPO is worth subscribing to
- **THEN** the system MUST first establish a valuation baseline before producing the subscription conclusion

### Requirement: IPO subscription output SHALL cover prospectus, structure, scenarios, and dated probability estimates
For an eligible IPO subscription analysis, the system MUST analyze the prospectus or equivalent primary disclosures, offering structure, dilution, lock-up or unlock pressure, trading and demand context, and bull/bear scenario framing. The conclusion MUST include dated probability estimates for expected upside and downside under the current time point, and it MUST explain the evidence behind those estimates.

#### Scenario: System produces a full IPO subscription analysis
- **WHEN** the target has passed the pre-listing eligibility gate
- **THEN** the answer MUST include prospectus-driven analysis, offering-structure analysis, upside/downside scenarios, and time-anchored probability estimates with supporting reasons

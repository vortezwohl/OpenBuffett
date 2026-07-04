## ADDED Requirements

### Requirement: Valuation analysis SHALL be the default research mainline
The system MUST treat professional valuation analysis as the default mainline for supported equity research requests. A complete analysis MUST be conclusion-first and MUST explicitly separate verified facts, fact-based inference, and unresolved uncertainty.

#### Scenario: User requests company valuation analysis
- **WHEN** the user asks for a research or valuation view on a supported equity
- **THEN** the system MUST answer through a valuation-first workflow rather than an IPO-first workflow

### Requirement: Valuation output SHALL include evidence-graded fundamentals and comparable analysis
The system MUST ground valuation analysis in business quality, financial quality, valuation level, and peer comparison. The analysis MUST use evidence grading that distinguishes primary disclosures from structured data sources and lower-confidence secondary materials.

#### Scenario: User receives a full valuation answer
- **WHEN** the system provides a full valuation analysis
- **THEN** it MUST include evidence-supported discussion of company quality, financial quality, and comparable companies from the same or closely related sector

### Requirement: Valuation output SHALL include multi-horizon judgment and current-market risk framing
For a complete valuation answer, the system MUST state whether the target appears cheap or expensive across at least four horizons: 1 year, 5 years, 10 years, and 15 years. The answer MUST also warn about the risk of immediately going long or short under the current market regime and MUST anchor the conclusion to the current analysis date.

#### Scenario: User asks whether a stock is cheap or expensive
- **WHEN** the system provides a full valuation conclusion
- **THEN** it MUST include 1-year, 5-year, 10-year, and 15-year valuation perspectives and explicit current long/short risk warnings with a date anchor

### Requirement: Unsupported market-data coverage SHALL be disclosed instead of fabricated
When a user asks for a non-core asset or a data view that is not reliably covered by the currently integrated tools, the system MUST state that the requested analysis cannot be verified with the current data surface. It MUST NOT overstate support or fabricate precise conclusions for unsupported instruments.

#### Scenario: User requests unsupported or weakly covered market analysis
- **WHEN** the current integrated data tools cannot rigorously support the requested asset or data view
- **THEN** the system MUST explicitly disclose the coverage limit instead of pretending that complete analysis is available

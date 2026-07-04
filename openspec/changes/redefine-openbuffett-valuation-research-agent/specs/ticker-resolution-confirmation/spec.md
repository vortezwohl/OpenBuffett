## ADDED Requirements

### Requirement: Non-ticker inputs SHALL trigger candidate ticker resolution
When a user provides a company full name, fuzzy name, or likely misspelled name instead of a confirmed stock ticker, the system MUST actively resolve one or more candidate tickers using searchable market or web sources before beginning formal valuation analysis.

#### Scenario: User provides a company name instead of a ticker
- **WHEN** the user requests research using a company name or ambiguous identifier
- **THEN** the system MUST resolve and present candidate ticker mappings before formal valuation analysis continues

### Requirement: User confirmation SHALL be required before formal analysis continues
The system MUST NOT proceed into full valuation analysis, IPO subscription analysis, or other formal research conclusions until the user confirms the resolved ticker candidate.

#### Scenario: Candidate ticker is found
- **WHEN** the system has identified one or more likely ticker candidates
- **THEN** it MUST ask the user to confirm the intended ticker before continuing into formal research output

### Requirement: Ambiguous or failed resolution SHALL remain explicit
If multiple plausible candidates remain or no reliable ticker can be found, the system MUST say so explicitly and MUST not quietly select one candidate as if certainty existed.

#### Scenario: Multiple plausible candidates exist
- **WHEN** the resolution step returns several plausible public companies
- **THEN** the system MUST present the ambiguity and request clarification instead of choosing one silently

#### Scenario: No reliable ticker can be verified
- **WHEN** the system cannot confidently verify a public-market ticker for the requested name
- **THEN** it MUST say that the ticker could not be reliably confirmed and stop short of formal valuation conclusions

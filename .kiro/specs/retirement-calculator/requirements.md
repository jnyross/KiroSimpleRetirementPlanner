# Requirements Document

## Introduction

A simple command-line retirement prediction tool that uses historical stock and bond returns to calculate when a user can retire with over 99% confidence of not running out of money by age 100. The tool prioritizes simplicity and effectiveness over complex features, focusing on core retirement planning calculations using real market data.

## Requirements

### Requirement 1

**User Story:** As a user planning for retirement, I want to input my current financial situation, so that I can get a personalized retirement prediction.

#### Acceptance Criteria

1. WHEN the user runs the tool THEN the system SHALL prompt for current age
2. WHEN the user runs the tool THEN the system SHALL prompt for current savings amount
3. WHEN the user runs the tool THEN the system SHALL prompt for monthly savings amount
4. WHEN the user enters invalid data (negative numbers, non-numeric values) THEN the system SHALL display an error message and re-prompt
5. WHEN the user enters valid data THEN the system SHALL accept the input and proceed to calculation

### Requirement 2

**User Story:** As a user, I want the tool to use real historical market data, so that my retirement prediction is based on actual market performance rather than theoretical returns.

#### Acceptance Criteria

1. WHEN the system calculates retirement projections THEN it SHALL use historical stock market returns data
2. WHEN the system calculates retirement projections THEN it SHALL use historical bond market returns data
3. WHEN the system performs calculations THEN it SHALL run Monte Carlo simulations using historical return sequences
4. WHEN the system runs simulations THEN it SHALL test thousands of different historical return scenarios
5. WHEN the system calculates projections THEN it SHALL assume a diversified portfolio allocation between stocks and bonds

### Requirement 3

**User Story:** As a user, I want to know when I can retire with high confidence, so that I can plan my career and life decisions accordingly.

#### Acceptance Criteria

1. WHEN the system completes calculations THEN it SHALL display the age at which retirement is possible where over 99% of simulation scenarios still have money remaining at age 100
2. WHEN the system runs simulations THEN it SHALL calculate the percentage of scenarios where money lasts until age 100 for each potential retirement age
3. WHEN the system displays results THEN it SHALL show the exact percentage of successful scenarios for the recommended retirement age
4. WHEN the system displays results THEN it SHALL show the projected portfolio value at retirement age
5. WHEN the system displays results THEN it SHALL output a time series chart showing 10th percentile, median (50th percentile), and 90th percentile portfolio values over time
6. WHEN no retirement age achieves 99% success rate THEN the system SHALL inform the user that more savings or longer working period is needed

### Requirement 4

**User Story:** As a user, I want the tool to be simple to use and maintain, so that I can easily run it and update it as needed without complexity.

#### Acceptance Criteria

1. WHEN the user wants to run the tool THEN it SHALL be executable from command line with a single command
2. WHEN the tool runs THEN it SHALL complete the entire process in one session without requiring multiple steps
3. WHEN the tool displays output THEN it SHALL be clear, concise, and easy to understand
4. WHEN the tool needs updates THEN the historical data SHALL be easily updatable through simple data files
5. WHEN the tool encounters errors THEN it SHALL display helpful error messages without technical jargon

### Requirement 5

**User Story:** As a user, I want the tool to use a guard rails withdrawal system, so that my retirement plan can adapt to market performance and increase the likelihood of success.

#### Acceptance Criteria

1. WHEN the system simulates retirement withdrawals THEN it SHALL implement a guard rails system that reduces spending during poor market performance
2. WHEN portfolio performance is below certain thresholds THEN the system SHALL reduce withdrawal amounts to preserve capital
3. WHEN portfolio performance is above certain thresholds THEN the system SHALL allow normal or slightly increased withdrawal amounts
4. WHEN the system calculates guard rails thresholds THEN it SHALL use established methodologies for determining when to reduce spending
5. WHEN the system applies spending adjustments THEN it SHALL factor these into the Monte Carlo simulations for accurate success rate calculations

### Requirement 6

**User Story:** As a user in the UK, I want the tool to automatically calculate taxes on my retirement withdrawals, so that I can see the true cost of my desired retirement lifestyle.

#### Acceptance Criteria

1. WHEN the system calculates withdrawal amounts THEN it SHALL automatically apply current UK tax rates based on the withdrawal amount
2. WHEN the system calculates taxes THEN it SHALL account for personal allowance thresholds and progressive tax bands
3. WHEN the system calculates taxes THEN it SHALL determine the gross withdrawal amount needed to achieve the desired net spending
4. WHEN the system runs simulations THEN it SHALL apply tax calculations to each withdrawal in every simulation scenario
5. WHEN the system displays results THEN it SHALL show both gross withdrawal amounts and net after-tax amounts

### Requirement 7

**User Story:** As a user, I want to see how different portfolio allocations impact my retirement timeline, so that I can understand the trade-offs between risk and retirement age.

#### Acceptance Criteria

1. WHEN the system runs calculations THEN it SHALL test 6 different portfolio allocations: 100% cash (earning nothing after inflation), 100% bonds, 25% equities/75% bonds, 50% equities/50% bonds, 75% equities/25% bonds, and 100% equities
2. WHEN the system displays results THEN it SHALL show the retirement age and success rate for each of the 6 portfolio allocations
3. WHEN the system runs simulations THEN it SHALL use the same Monte Carlo methodology for all portfolio allocations to ensure fair comparison
4. WHEN the system calculates cash returns THEN it SHALL assume zero real return (inflation-adjusted) for the cash scenario
5. WHEN the system displays results THEN it SHALL clearly indicate which portfolio allocation provides the earliest retirement age with 99% confidence
6. WHEN the system outputs charts THEN it SHALL show time series data for each portfolio allocation to visualize the differences

### Requirement 8

**User Story:** As a user, I want all calculations and results to be in today's purchasing power, so that I can understand what my retirement income will actually be worth.

#### Acceptance Criteria

1. WHEN the system performs any calculations THEN it SHALL use real (inflation-adjusted) returns for all asset classes
2. WHEN the system displays results THEN it SHALL show all monetary amounts in today's purchasing power (real terms)
3. WHEN the system calculates portfolio growth THEN it SHALL apply historical inflation rates to convert nominal returns to real returns
4. WHEN the system calculates withdrawal amounts THEN it SHALL maintain constant purchasing power throughout retirement
5. WHEN the system displays projected values THEN it SHALL clearly indicate that all figures are in today's money terms

### Requirement 9

**User Story:** As a user, I want reasonable assumptions built into the tool, so that I don't need to specify complex financial parameters.

#### Acceptance Criteria

1. WHEN the system calculates retirement needs THEN it SHALL assume withdrawal rate based on established safe withdrawal rate principles
2. WHEN the system runs THEN it SHALL use reasonable default assumptions that can be easily modified in the code if needed
3. WHEN the system calculates guard rails THEN it SHALL use established thresholds and adjustment percentages that can be easily updated
4. WHEN the system uses historical data THEN it SHALL source reliable historical return and inflation data for accurate real return calculations
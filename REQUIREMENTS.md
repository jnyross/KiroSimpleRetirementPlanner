# Kiro Simple Retirement Planner - Requirements Document

## Version 1.0.1
Last Updated: January 2025

## Overview

The Kiro Simple Retirement Planner is a command-line tool that uses Monte Carlo simulation with historical UK market data to determine retirement feasibility. Users can select their desired confidence level (50-100%) for retirement success.

## Functional Requirements

### 1. User Input Collection

The system shall collect the following inputs from users:

#### 1.1 Current Age
- **Range**: 18-80 years
- **Validation**: Must be a positive integer within range
- **Purpose**: Determines accumulation period and retirement timeline

#### 1.2 Current Savings
- **Range**: £0 or greater
- **Format**: Numeric value (no currency symbols or commas)
- **Validation**: Must be non-negative
- **Purpose**: Starting portfolio value for projections

#### 1.3 Monthly Savings
- **Range**: £0 or greater
- **Format**: Numeric value representing monthly contribution
- **Validation**: Must be non-negative
- **Purpose**: Regular contributions during accumulation phase

#### 1.4 Desired Annual Income
- **Range**: Greater than £0
- **Format**: After-tax annual amount in today's purchasing power
- **Validation**: Must be positive
- **Purpose**: Target retirement spending level

#### 1.5 Target Success Rate (NEW in v1.0.1)
- **Range**: 50-100%
- **Default**: 99%
- **Format**: Percentage (accepts both 95 and 0.95 formats)
- **Validation**: Must be between 0.5 and 1.0
- **Purpose**: User's risk tolerance level
- **Guidance**:
  - 99% = Very conservative (prioritizes security)
  - 95% = Conservative (good balance)
  - 90% = Moderate (accepts some risk)
  - 85% = Aggressive (prioritizes early retirement)

### 2. Monte Carlo Simulation

#### 2.1 Simulation Parameters
- **Number of Simulations**: 10,000 default (configurable via CLI)
- **Time Horizon**: Current age to age 100
- **Bootstrap Sampling**: Use historical return sequences from 1980-2023

#### 2.2 Portfolio Allocations
The system shall test 7 different portfolio allocations:
1. 100% Cash (0% real return)
2. 100% Bonds
3. 25% Equities / 75% Bonds
4. 50% Equities / 50% Bonds
5. 75% Equities / 25% Bonds
6. 100% Equities
7. Dynamic Glide Path (Age-Based)

#### 2.3 Dynamic Glide Path Details
- **Starting Allocation**: 90% equities at age 25 and younger
- **Pre-Retirement**: Linear decrease to 30% equities at retirement
- **Post-Retirement**: Linear decrease to 20% equities by age 75
- **Minimum Equity**: 20% after age 75

### 3. Guard Rails System

#### 3.1 Spending Adjustment Thresholds
- **Upper Guard Rail**: Portfolio ≥ 120% of initial → Normal spending
- **Normal Zone**: Portfolio 85-120% of initial → Normal spending
- **Lower Guard Rail**: Portfolio 85-75% of initial → 10% spending reduction
- **Severe Guard Rail**: Portfolio ≤ 75% of initial → 20% spending reduction

#### 3.2 Implementation
- Apply adjustments to gross (pre-tax) withdrawals
- Recalculate each simulation year
- Allow recovery to normal spending when portfolio improves

### 4. Tax Calculations

#### 4.1 UK Tax System (2024/25)
- **Personal Allowance**: £12,570
- **Basic Rate**: 20% (£12,570 - £50,270)
- **Higher Rate**: 40% (£50,270 - £125,140)
- **Additional Rate**: 45% (above £125,140)

#### 4.2 Calculation Method
- Convert desired net income to gross withdrawal amount
- Apply progressive tax brackets
- Account for personal allowance

### 5. Analysis and Results

#### 5.1 Success Rate Calculation
- **Definition**: Percentage of simulations where portfolio lasts to age 100
- **Target**: User-selected success rate (50-100%)
- **Calculation**: Count successful scenarios ÷ total scenarios

#### 5.2 Optimal Retirement Age
- Find earliest age achieving user's target success rate
- Test each portfolio allocation independently
- Use binary search for efficiency

#### 5.3 Portfolio Recommendation
- Select portfolio with earliest retirement age at target success rate
- If none achieve target, select highest success rate portfolio
- Provide comparison across all allocations

### 6. Output Generation

#### 6.1 Console Output
- User input summary with target success rate
- Recommended portfolio and retirement age
- Comparison table of all portfolios
- Key insights and suggestions
- Retirement readiness score

#### 6.2 Chart Generation
- Portfolio comparison bar chart
- Time-series percentile charts (10th, 50th, 90th)
- Organized in timestamped subdirectories
- Format: charts/analysis_YYYYMMDD_HHMMSS/

## Non-Functional Requirements

### 1. Performance
- Complete 10,000 simulations in under 5 minutes on standard hardware
- Provide progress indicators for long operations
- Support batch processing for memory efficiency

### 2. Usability
- Interactive CLI with clear prompts
- Helpful validation messages
- Progress bars during simulation
- Comprehensive error messages

### 3. Reliability
- Validate all user inputs
- Handle edge cases gracefully
- Provide consistent results for same inputs
- Comprehensive test coverage

### 4. Maintainability
- Modular architecture with clear separation of concerns
- Well-documented code with docstrings
- Historical data in easily updatable CSV format
- Configuration via command-line arguments

### 5. Data Quality
- Use 44 years of historical UK market data
- Include major market events and cycles
- Calculate real (inflation-adjusted) returns
- Validate data integrity on load

## Technical Requirements

### 1. Platform Requirements
- Python 3.8 or later
- Cross-platform compatibility (Windows, macOS, Linux)
- Command-line interface

### 2. Dependencies
- numpy ≥1.21.0 (numerical calculations)
- pandas ≥1.3.0 (data management)
- matplotlib ≥3.4.0 (chart generation)
- click ≥8.0.0 (CLI framework)
- tqdm ≥4.62.0 (progress bars)
- pytest ≥6.0.0 (testing)

### 3. Data Storage
- CSV format for historical data
- File-based output for charts
- No database required

## Constraints and Assumptions

### 1. Constraints
- UK-specific tax calculations only
- Historical data limited to 1980-2023
- No investment fees or transaction costs modeled
- Single person calculation (no couples)

### 2. Assumptions
- All values in real (inflation-adjusted) terms
- Annual portfolio rebalancing
- No other retirement income sources
- Constant real spending (adjusted by guard rails)
- Retirement ends at age 100
- No inheritance goals
- Disciplined investor behavior

## Future Enhancements (Not in Current Scope)

1. Multiple currency support
2. Couples retirement planning
3. State pension integration
4. Investment fee modeling
5. Healthcare cost projections
6. Part-time work scenarios
7. Geographic cost-of-living adjustments
8. Web-based interface
9. PDF report generation
10. Scenario comparison features

## Change History

### Version 1.0.1 (January 2025)
- Added user-selectable success rate feature (50-100%)
- Updated all components to use user's target success rate
- Enhanced CLI with risk tolerance guidance
- Removed hardcoded 99% threshold

### Version 1.0.0 (January 2025)
- Initial release
- Dynamic glide path portfolio allocation
- Chart organization in timestamped subdirectories
- Guard rails system implementation
- UK tax integration
- Monte Carlo simulation engine
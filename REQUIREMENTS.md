# Kiro Simple Retirement Planner - Requirements Document

## Version 1.1.0
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
- **Default**: 95% (updated from 99% in v1.1.0)
- **Format**: Percentage (accepts both 95 and 0.95 formats)
- **Validation**: Must be between 0.5 and 1.0
- **Purpose**: User's risk tolerance level
- **Guidance**:
  - 99% = Very conservative (prioritizes security)
  - 95% = Conservative (good balance, recommended)
  - 90% = Moderate (accepts some risk)
  - 85% = Aggressive (prioritizes early retirement)

#### 1.6 Cash Buffer (NEW in v1.1.0)
- **Range**: 0-5 years of spending
- **Default**: 2 years
- **Format**: Numeric value representing years
- **Validation**: Must be non-negative
- **Purpose**: Emergency fund held outside portfolio for market downturns

#### 1.7 State Pension Details (NEW in v1.1.0)
- **State Pension Age**: 
  - Default: 67 (current UK state pension age)
  - Range: 60-75 years
- **State Pension Amount**: 
  - Default: £9,110 (current UK full state pension)
  - Range: £0-20,000 annually
- **Purpose**: Reduces required portfolio withdrawals in later years

#### 1.8 Spending Phases (NEW in v1.1.0)
- **Format**: List of (age, spending_multiplier) tuples
- **Default**: [(75, 0.75)] - 25% reduction at age 75
- **Validation**: Ages must be sequential, multipliers 0.1-1.0
- **Purpose**: Models realistic spending reduction in later retirement

### 2. Monte Carlo Simulation

#### 2.1 Simulation Parameters
- **Number of Simulations**: 10,000 default (configurable via CLI)
- **Time Horizon**: Current age to age 100
- **Bootstrap Sampling**: Use historical return sequences from 1980-2023
- **Historical Backtesting Mode** (NEW in v1.1.0): Optional deterministic testing of all historical periods

#### 2.2 Portfolio Allocations
The system shall test 9 different portfolio allocations (expanded in v1.1.0):
1. 100% Cash (0% real return)
2. 100% Bonds
3. 25% Equities / 75% Bonds
4. 50% Equities / 50% Bonds
5. 75% Equities / 25% Bonds
6. 100% Equities
7. Dynamic Glide Path (Age-Based Decreasing)
8. Rising Glide Path (Bond-to-Equity) (NEW in v1.1.0)
9. Target Date Fund Style (NEW in v1.1.0)

#### 2.3 Dynamic Glide Path Details
##### 2.3.1 Traditional Decreasing Glide Path
- **Starting Allocation**: 90% equities at age 25 and younger
- **Pre-Retirement**: Linear decrease to 30% equities at retirement
- **Post-Retirement**: Linear decrease to 20% equities by age 75
- **Minimum Equity**: 20% after age 75

##### 2.3.2 Rising Glide Path (NEW in v1.1.0)
- **Starting Allocation**: 30% equities at retirement
- **Post-Retirement**: Linear increase to 70% equities by age 85
- **Purpose**: Mitigate sequence of returns risk in early retirement
- **Research**: Based on Pfau-Kitces studies showing improved outcomes

##### 2.3.3 Target Date Fund Style (NEW in v1.1.0)
- **Formula**: 120 minus age = equity percentage
- **Example**: Age 60 = 60% equities, Age 80 = 40% equities
- **Floor**: Minimum 20% equities

### 3. Guard Rails System

#### 3.1 Basic Guard Rails (Existing)
- **Upper Guard Rail**: Portfolio ≥ 120% of initial → Normal spending
- **Normal Zone**: Portfolio 85-120% of initial → Normal spending
- **Lower Guard Rail**: Portfolio 75-85% of initial → 10% spending reduction
- **Severe Guard Rail**: Portfolio ≤ 75% of initial → 20% spending reduction

#### 3.2 Guyton-Klinger Enhanced Guard Rails (NEW in v1.1.0)
- **Ratcheting Feature**: Permanent spending increases during good times
  - If portfolio > 120% of initial: 10% permanent spending increase
  - Ratchet can trigger multiple times (compound growth)
- **Capital Preservation Rule**: No withdrawals from principal if portfolio return < 0%
- **Portfolio Management Rule**: Skip inflation adjustment if withdrawal rate > initial rate + 20%
- **Initial Withdrawal Rate**: Can start at 5-6% with dynamic adjustments

#### 3.3 Vanguard Dynamic Spending Rule (NEW in v1.1.0)
- **Alternative to Guard Rails**: Smoother adjustments
- **Formula**: Previous withdrawal × (1 + inflation) × performance factor
- **Ceiling**: Maximum 5% annual increase
- **Floor**: Maximum 2.5% annual decrease
- **Purpose**: Less volatility in spending changes

#### 3.4 Implementation
- Apply adjustments to gross (pre-tax) withdrawals
- Recalculate each simulation year
- Allow recovery to normal spending when portfolio improves
- User selectable strategy: Basic, Guyton-Klinger, or Vanguard

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
- **Target**: User-selected success rate (50-100%, default 95%)
- **Calculation**: Count successful scenarios ÷ total scenarios
- **Safe Withdrawal Rate** (NEW in v1.1.0): Calculate sustainable withdrawal rate for UK/global data (typically 3-3.5%)

#### 5.2 Historical Backtesting (NEW in v1.1.0)
- **Rolling Period Analysis**: Test all historical N-year retirement periods
- **Worst-Case Identification**: Find worst historical sequence for each portfolio
- **Success Rate by Era**: Show performance across different historical periods
- **Deterministic Validation**: Complement Monte Carlo with actual historical paths

#### 5.3 Optimal Retirement Age
- Find earliest age achieving user's target success rate
- Test each portfolio allocation independently
- Use binary search for efficiency
- Consider state pension kick-in for UK retirees

#### 5.4 Portfolio Recommendation
- Select portfolio with earliest retirement age at target success rate
- If none achieve target, select highest success rate portfolio
- Provide comparison across all allocations
- Factor in cash buffer and spending phases for accurate projections

### 6. Output Generation

#### 6.1 Console Output
- User input summary with target success rate, cash buffer, state pension
- Recommended portfolio and retirement age
- Comparison table of all portfolios (expanded to 9 allocations)
- Safe withdrawal rate calculation for UK context
- Key insights including worst historical periods
- Retirement readiness score
- Effective spending rate after adjustments

#### 6.2 Chart Generation
- Portfolio comparison bar chart (all 9 allocations)
- Time-series percentile charts (10th, 50th, 90th)
- Historical backtest visualization (NEW in v1.1.0)
- Spending adjustment timeline (NEW in v1.1.0)
- Cash buffer depletion chart (NEW in v1.1.0)
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
- **Current Data**: 44 years of global market data (1980-2023)
- **Extended Data** (NEW in v1.1.0): Support for 100+ year datasets (1900-present)
  - Source: Barclays Equity Gilt Study, Dimson-Marsh-Staunton Global Returns
  - Purpose: Capture rare events (Great Depression, World Wars, 1970s stagflation)
- Include major market events and cycles
- Calculate real (inflation-adjusted) returns
- Validate data integrity on load
- Support both stochastic (Monte Carlo) and deterministic (historical backtest) modes

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
- Core historical data 1980-2023 (extended data 1900-present optional)
- Investment fees not modeled (user should reduce returns accordingly)
- Single person calculation (no couples)
- Cash buffer held separately from invested portfolio

### 2. Assumptions
- All values in real (inflation-adjusted) terms
- Annual portfolio rebalancing
- State pension integrated (NEW in v1.1.0)
- Dynamic spending with guard rails or Vanguard rule
- Retirement ends at age 100
- Legacy goals optional (95% success rate allows buffer)
- Disciplined investor behavior
- Safe withdrawal rates 3-3.5% for UK/global data

## Future Enhancements (Not in Current Scope)

1. Multiple currency support
2. Couples retirement planning
3. Investment fee modeling (explicit)
4. Healthcare/long-term care cost projections
5. Part-time work scenarios
6. Geographic cost-of-living adjustments
7. Web-based interface
8. PDF report generation
9. Tax-advantaged accounts (ISA, SIPP)
10. International tax scenarios
11. Inheritance planning tools
12. Social Security optimization (US users)

## Change History

### Version 1.1.0 (January 2025) - James Shack Strategy Integration
Major update incorporating evidence-based strategies from UK financial planning:

**New Features:**
- Extended historical backtesting mode (1900-present data support)
- Cash buffer implementation (2-5 years emergency fund)
- State pension integration (reduces portfolio withdrawals)
- Phased spending (realistic retirement spending patterns)
- Guyton-Klinger enhanced guard rails with ratcheting
- Vanguard dynamic spending rule option
- Rising equity glidepath (sequence risk mitigation)
- Target date fund allocation strategy
- Safe withdrawal rate calculations (3-3.5% for UK/global)
- Historical worst-case scenario analysis
- Default success rate changed from 99% to 95%

**Expanded Capabilities:**
- 9 portfolio allocations (up from 7)
- Multiple dynamic spending strategies
- Deterministic + stochastic analysis modes
- Enhanced chart visualizations

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
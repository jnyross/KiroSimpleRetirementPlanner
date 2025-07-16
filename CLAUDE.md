# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kiro Simple Retirement Planner is a command-line Python application that uses Monte Carlo simulation with historical market data to predict when a user can retire with 99% confidence of not running out of money by age 100. The tool is designed for UK-based individuals and prioritizes simplicity and effectiveness.

## Architecture

The project follows a modular architecture with clear separation of concerns:

### Core Components
- **Historical Data Manager**: Loads and manages CSV files with UK market data
- **Monte Carlo Simulator**: Runs 10,000+ retirement scenarios using bootstrap sampling
- **Guard Rails Engine**: Implements dynamic spending adjustments based on portfolio performance
- **UK Tax Calculator**: Applies UK tax calculations to withdrawal amounts
- **Results Analyzer**: Processes simulation results and calculates success rates
- **Chart Generator**: Creates time series visualizations using matplotlib
- **CLI Interface**: Handles user input and output formatting

### Project Structure
```
retirement-calculator/
├── main.py                    # Entry point and CLI interface
├── requirements.txt           # Python dependencies
├── data/                     # Historical market data (CSV files)
│   ├── uk_equity_returns.csv
│   ├── uk_bond_returns.csv
│   ├── uk_inflation_rates.csv
│   └── portfolio_allocations.csv
├── src/                      # Core application modules
│   ├── models.py            # Data classes
│   ├── data_manager.py      # Historical data management
│   ├── tax_calculator.py    # UK tax calculations
│   ├── guard_rails.py       # Guard rails system
│   ├── simulator.py         # Monte Carlo simulation
│   ├── analyzer.py          # Results analysis
│   ├── charts.py            # Chart generation
│   └── cli.py               # Command-line interface
└── tests/                   # Unit and integration tests
```

## Key Features

### Portfolio Allocations
Tests 6 different portfolio mixes:
- 100% Cash (0% real return after inflation)
- 100% Bonds
- 25% Equities/75% Bonds
- 50% Equities/50% Bonds
- 75% Equities/25% Bonds
- 100% Equities

### Guard Rails System
- **Upper Guard Rail**: 20% above initial portfolio value → allow normal spending
- **Lower Guard Rail**: 15% below initial portfolio value → reduce spending by 10%
- **Severe Guard Rail**: 25% below initial portfolio value → reduce spending by 20%
- **Recovery**: Gradual return to normal spending as portfolio recovers

### User Input Requirements
- Current age
- Current savings amount
- Monthly savings amount
- Desired annual retirement income (after-tax)

## Development Commands

### Run the Application
```bash
python3 main.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
python -m pytest tests/
```

### Technology Stack
- **Python 3.8+**: Core language
- **NumPy**: Numerical calculations and array operations
- **Pandas**: Data manipulation and CSV handling
- **Matplotlib**: Chart generation for time series plots
- **Click**: Command-line interface framework

## Implementation Notes

- All calculations use real (inflation-adjusted) returns
- Bootstrap sampling from historical return sequences
- No databases - simple file-based data storage
- Success threshold: 99% confidence level
- Time horizon: From current age to age 100
- Comprehensive input validation and error handling
- Focus on UK tax calculations and market data

## AI Coding Guidelines

### Critical Rules
- **ALWAYS** reference the requirements, design, and tasks documents in `.kiro/specs/retirement-calculator/`
- **NEVER** deviate from the specified architecture without explicit user approval
- **IMPLEMENT** features exactly as described in the acceptance criteria
- **USE** the exact directory structure defined in `structure.md`
- **FOLLOW** the task sequence in `tasks.md` exactly

### Technology Stack Compliance
- **USE ONLY** the specified technologies: Python 3.8+, NumPy, Pandas, Matplotlib, Click
- **IMPLEMENT** vectorized operations with NumPy for performance
- **HANDLE** CSV data loading with Pandas
- **CREATE** CLI interfaces with Click framework
- **GENERATE** charts with Matplotlib only

### Data and Calculations Requirements
- **WORK** exclusively in real (inflation-adjusted) terms
- **IMPLEMENT** the 6 portfolio allocations exactly as specified
- **USE** bootstrap sampling from historical data, not parametric distributions
- **APPLY** UK tax calculations to all withdrawal scenarios
- **IMPLEMENT** guard rails system with specified thresholds (20% upper, 15% lower, 25% severe)

### Monte Carlo Simulation Requirements
- **RUN** 10,000+ simulations per portfolio allocation
- **TARGET** 99% success rate for retirement feasibility
- **SIMULATE** from current age to age 100
- **INTEGRATE** guard rails and tax calculations in every scenario
- **CALCULATE** 10th, 50th, and 90th percentiles for visualization

### Forbidden Actions
- **NEVER** use databases or complex storage systems
- **NEVER** create GUI components
- **NEVER** use theoretical return assumptions instead of historical data
- **NEVER** skip the guard rails implementation
- **NEVER** ignore UK tax calculations
- **NEVER** compromise the 99% confidence threshold

### Code Quality Standards
- **WRITE** comprehensive docstrings for all classes and methods
- **CREATE** unit tests for all calculation components
- **HANDLE** errors gracefully with user-friendly messages
- **VALIDATE** all user inputs with clear error messages
- **SHOW** progress indicators for long-running operations

### User Experience Requirements
- **KEEP** the interface simple: single command execution
- **PROMPT** for user inputs with validation and re-prompting
- **DISPLAY** clear, actionable results comparing all 6 portfolios
- **GENERATE** time series charts showing percentile ranges
- **INDICATE** which portfolio allows earliest retirement with 99% confidence

## Current Status

The project currently has only a basic `main.py` file with a placeholder implementation. The comprehensive specifications are ready for implementation following the detailed requirements and design documents in the `.kiro` directory.
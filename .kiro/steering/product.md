# Product Overview

This is a command-line retirement prediction tool that uses Monte Carlo simulation with historical market data to calculate when a user can retire with 99% confidence of not running out of money by age 100.

## Key Features

- **Monte Carlo Simulation**: Uses historical stock and bond returns to run thousands of retirement scenarios
- **Multiple Portfolio Allocations**: Tests 6 different portfolio mixes from 100% cash to 100% equity
- **Guard Rails System**: Implements dynamic spending adjustments based on portfolio performance
- **UK Tax Integration**: Automatically calculates UK taxes on retirement withdrawals
- **Real Returns Focus**: All calculations in inflation-adjusted terms (today's purchasing power)
- **High Confidence Threshold**: Targets 99% success rate for retirement feasibility

## Target User

UK-based individuals planning for retirement who want data-driven predictions based on historical market performance rather than theoretical returns.

## Design Philosophy

Prioritizes simplicity and effectiveness over complex features. Single command-line execution with clear, actionable output. Easily maintainable with updateable historical data files.
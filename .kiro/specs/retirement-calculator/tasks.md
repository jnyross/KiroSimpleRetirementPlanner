# Implementation Plan

- [x] 1. Set up project structure and core data models
  - Create directory structure for the retirement calculator application
  - Define core data classes (UserInput, PortfolioAllocation, SimulationResult) using Python dataclasses
  - Create __init__.py files and basic module structure
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Implement historical data management system
  - Create HistoricalDataManager class to load CSV data files
  - Implement methods to load equity returns, bond returns, and inflation data
  - Create sample historical data CSV files with realistic global market data from reliable sources
  - Add data validation and error handling for missing or invalid data files
  - _Requirements: 2.1, 2.2, 8.1, 8.3, 9.4_

- [x] 3. Create UK tax calculation engine
  - Implement UKTaxCalculator class with current UK tax bands and personal allowance
  - Create method to calculate gross withdrawal needed for desired net income
  - Add method to calculate tax on given income amount
  - Write unit tests for various income levels and tax scenarios
  - _Requirements: 6.1, 6.2, 6.4, 6.5_

- [x] 4. Build portfolio allocation system
  - Create PortfolioManager class to handle the 6 different portfolio allocations
  - Define the 6 portfolio configurations (100% cash through 100% equity)
  - Implement method to calculate portfolio returns based on allocation and historical data
  - Add portfolio validation and return calculation logic
  - _Requirements: 7.1, 7.2, 8.4_

- [x] 5. Implement guard rails withdrawal system
  - Create GuardRailsEngine class with guard rail thresholds and adjustment logic
  - Implement method to calculate withdrawal adjustments based on portfolio performance
  - Add logic for upper, lower, and severe guard rail scenarios
  - Create method to apply spending adjustments during retirement simulation
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 6. Build Monte Carlo simulation engine
  - Create MonteCarloSimulator class with bootstrap sampling from historical returns
  - Implement single scenario simulation method that tracks portfolio value from current age to 100
  - Add integration with guard rails engine and tax calculator within each simulation
  - Create method to run thousands of simulations and track success/failure for each scenario
  - _Requirements: 2.3, 2.4, 3.1, 3.2_

- [x] 7. Create results analysis and statistics calculator
  - Implement ResultsAnalyzer class to process simulation outputs
  - Add method to calculate success rates (percentage of scenarios with money at age 100)
  - Create percentile calculation methods (10th, 50th, 90th) for portfolio values over time
  - Implement method to determine optimal retirement age for 99% confidence threshold
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 8. Build chart generation system
  - Create ChartGenerator class using matplotlib for time series visualization
  - Implement method to generate charts showing 10th, 50th, and 90th percentile portfolio values
  - Add functionality to create separate charts for each of the 6 portfolio allocations
  - Create method to save charts to files and display summary statistics
  - _Requirements: 3.5, 7.5_

- [x] 9. Implement command-line interface
  - Create CLI module using Click framework for user input collection
  - Add input validation for age, current savings, monthly savings, and desired income
  - Implement prompts with clear error messages and re-prompting for invalid data
  - Create main application flow that orchestrates all components
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 4.3_

- [x] 10. Integrate all components and create main application runner
  - Create main application class that coordinates all components
  - Implement the complete workflow: input → simulation → analysis → output
  - Add progress indicators for long-running simulations
  - Create method to run simulations for all 6 portfolios and compare results
  - _Requirements: 4.1, 4.2, 7.2, 7.3, 7.4_

- [x] 11. Add comprehensive error handling and user feedback
  - Implement error handling for file loading, calculation errors, and invalid inputs
  - Add helpful error messages without technical jargon
  - Create progress feedback during simulation execution
  - Add validation for reasonable input ranges and edge cases
  - _Requirements: 1.4, 4.5, 9.2, 9.3_

- [x] 12. Create output formatting and results display
  - Implement console output formatter for simulation results
  - Add clear display of retirement age, success rates, and portfolio projections for each allocation
  - Create summary table comparing all 6 portfolio allocations
  - Add indication of which portfolio provides earliest retirement with 99% confidence
  - _Requirements: 3.3, 3.4, 4.3, 7.2, 7.4, 8.5_

- [x] 13. Write comprehensive unit tests
  - Create test suite for tax calculator with various UK tax scenarios
  - Add tests for guard rails engine with different portfolio performance scenarios
  - Write tests for historical data loading and validation
  - Create integration tests for complete simulation workflows
  - _Requirements: All requirements - testing ensures correctness_

- [x] 14. Add real historical data and documentation
  - Source and create real historical data files for UK equity returns, bond returns, and inflation rates from reliable financial data sources
  - Add README with installation and usage instructions
  - Create example runs showing typical output format
  - Add comments and docstrings throughout codebase for maintainability
  - _Requirements: 4.4, 9.1, 9.3_

## Remaining Tasks

- [x] 15. Fix percentile calculation in simulator and analyzer
  - Update MonteCarloSimulator to properly collect and return percentile data from all simulation runs
  - Modify ResultsAnalyzer to use actual simulation percentiles instead of synthetic data
  - Ensure percentile data is correctly passed to chart generation
  - _Requirements: 3.5, 7.5_

- [x] 16. Enhance chart generation with real percentile data
  - Update ChartGenerator to handle actual percentile trajectories from simulations
  - Fix chart generation to work with the corrected percentile data structure
  - Test chart generation with realistic simulation data
  - _Requirements: 3.5, 7.5_

- [x] 17. Create comprehensive README documentation
  - Write installation instructions for Python dependencies
  - Add usage examples with sample commands and expected output
  - Document the methodology and assumptions used in calculations
  - Include troubleshooting section for common issues
  - _Requirements: 4.4, 9.1, 9.3_

- [x] 18. Add final integration testing and validation
  - Run full end-to-end tests with realistic user scenarios
  - Validate that all 6 portfolio allocations produce reasonable results
  - Test edge cases (very young/old users, extreme savings rates, etc.)
  - Verify that 99% confidence threshold is properly implemented
  - _Requirements: All requirements - final validation_

## Additional Tasks Identified

- [ ] 19. Improve unit test coverage and organization
  - Move existing test files from root directory to tests/ directory
  - Create proper pytest test structure with test classes
  - Add comprehensive unit tests for all core components
  - Ensure test coverage for edge cases and error conditions
  - _Requirements: All requirements - testing ensures correctness_

- [ ] 20. Enhance error handling and user experience
  - Add better error messages for common data loading issues
  - Improve input validation with more specific feedback
  - Add graceful handling of missing or corrupted data files
  - Implement better progress reporting during long simulations
  - _Requirements: 1.4, 4.5, 9.2, 9.3_

- [ ] 21. Optimize performance for large simulations
  - Profile the Monte Carlo simulation performance
  - Implement vectorized operations where possible
  - Add memory management for very large simulation runs
  - Consider parallel processing for portfolio comparisons
  - _Requirements: 2.3, 2.4, 3.1, 3.2_

- [ ] 22. Add data validation and quality checks
  - Implement comprehensive validation of historical data files
  - Add checks for data consistency and reasonable ranges
  - Create data quality reports and warnings
  - Add functionality to handle missing years in historical data
  - _Requirements: 2.1, 2.2, 8.1, 8.3, 9.4_
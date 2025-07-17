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
  - Create PortfolioManager class to handle the 7 different portfolio allocations (including dynamic glide path)
  - Define the 6 static portfolio configurations (100% cash through 100% equity) plus dynamic glide path
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
  - Add optimized simulator for better performance with large simulation counts
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
  - Add functionality to create separate charts for each of the 7 portfolio allocations
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
  - Create method to run simulations for all 7 portfolios and compare results
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
  - Create summary table comparing all 7 portfolio allocations
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
  - Add comprehensive README with installation and usage instructions
  - Create example runs showing typical output format
  - Add comments and docstrings throughout codebase for maintainability
  - _Requirements: 4.4, 9.1, 9.3_

- [x] 15. Implement dynamic glide path portfolio allocation
  - Add DynamicGlidePath class that adjusts allocation based on age
  - Implement age-based allocation formula (90% equity at 25, decreasing to 20% at 75+)
  - Integrate dynamic allocation into portfolio manager and simulator
  - Test dynamic allocation with various age scenarios
  - _Requirements: 7.1, 7.2, 8.4_

- [x] 16. Add data validation and quality assurance system
  - Implement DataValidator class for comprehensive data file validation
  - Add CLI commands for data validation and quality reporting
  - Create data quality reports with statistics and warnings
  - Add validation for data consistency and reasonable ranges
  - _Requirements: 2.1, 2.2, 8.1, 8.3, 9.4_

- [x] 17. Optimize performance with vectorized operations
  - Create OptimizedMonteCarloSimulator using NumPy vectorization
  - Implement batch processing for memory efficiency
  - Add parallel processing capabilities for multi-core systems
  - Profile and compare performance between standard and optimized simulators
  - _Requirements: 2.3, 2.4, 3.1, 3.2_

- [x] 18. Enhance user experience and error handling
  - Improve CLI with better progress indicators and user feedback
  - Add comprehensive error handling with user-friendly messages
  - Implement graceful handling of edge cases and invalid inputs
  - Add interactive validation and confirmation prompts
  - _Requirements: 1.4, 4.1, 4.2, 4.3, 4.5, 9.2, 9.3_

- [x] 19. Create comprehensive documentation and examples
  - Write detailed README with installation, usage, and troubleshooting sections
  - Document all portfolio allocations and their characteristics
  - Explain guard rails system and tax calculations in detail
  - Add performance optimization tips and technical details
  - _Requirements: 4.4, 9.1, 9.3_

- [x] 20. Final integration testing and validation
  - Run comprehensive end-to-end tests with realistic user scenarios
  - Test the complete CLI workflow from input to chart generation
  - Validate that all 7 portfolio allocations produce reasonable results
  - Test edge cases (very young/old users, extreme savings rates, etc.)
  - Verify that 99% confidence threshold is properly implemented across all components
  - _Requirements: All requirements - final validation_

## Project Status

✅ **COMPLETE** - All core requirements have been implemented and tested. The retirement calculator is fully functional with:

- **7 Portfolio Allocations**: Including dynamic glide path strategy
- **Monte Carlo Simulation**: 10,000+ simulations with bootstrap sampling from historical data
- **Guard Rails System**: Dynamic spending adjustments for market volatility
- **UK Tax Integration**: Automatic tax calculations for withdrawal planning
- **Comprehensive CLI**: User-friendly interface with validation and progress feedback
- **Performance Optimization**: Vectorized operations and parallel processing
- **Data Validation**: Quality checks and validation for historical data
- **Chart Generation**: Visual analysis with percentile projections
- **Extensive Documentation**: Complete README with troubleshooting guide
- **Test Coverage**: Unit and integration tests for all components

The application successfully meets all requirements from the specification and is ready for production use.
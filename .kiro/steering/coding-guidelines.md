# AI Coding Agent Guidelines

## Project Adherence Rules

### Follow the Specification Documents
- **ALWAYS** reference the requirements, design, and tasks documents in `.kiro/specs/retirement-calculator/`
- **NEVER** deviate from the specified architecture without explicit user approval
- **IMPLEMENT** features exactly as described in the acceptance criteria
- **MAINTAIN** the modular design with clear separation of concerns

### Code Structure and Organization
- **USE** the exact directory structure defined in `structure.md`
- **PLACE** all core logic in the `src/` directory with proper module separation
- **CREATE** dataclasses in `models.py` for all data structures
- **SEPARATE** concerns: data management, simulation, tax calculation, visualization
- **FOLLOW** Python naming conventions: snake_case for files and functions

### Technology Stack Compliance
- **USE ONLY** the specified technologies: Python 3.8+, NumPy, Pandas, Matplotlib, Click
- **IMPLEMENT** vectorized operations with NumPy for performance
- **HANDLE** CSV data loading with Pandas
- **CREATE** CLI interfaces with Click framework
- **GENERATE** charts with Matplotlib only

### Data and Calculations
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

### Implementation Order
- **FOLLOW** the task sequence in `tasks.md` exactly
- **COMPLETE** each task fully before moving to the next
- **TEST** each component as it's built
- **INTEGRATE** components incrementally

### Forbidden Actions
- **NEVER** use databases or complex storage systems
- **NEVER** create GUI components
- **NEVER** use theoretical return assumptions instead of historical data
- **NEVER** skip the guard rails implementation
- **NEVER** ignore UK tax calculations
- **NEVER** compromise the 99% confidence threshold

### File and Data Management
- **STORE** historical data in CSV files in `data/` directory
- **MAKE** data easily updatable without code changes
- **VALIDATE** data file formats and handle missing files gracefully
- **USE** relative imports within the `src/` package
- **MAINTAIN** clean separation between data, logic, and presentation
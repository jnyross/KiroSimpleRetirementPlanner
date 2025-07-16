# Project Structure

## Directory Organization

```
retirement-calculator/
├── main.py                    # Entry point and CLI interface
├── requirements.txt           # Python dependencies
├── README.md                 # Installation and usage guide
├── data/                     # Historical market data (CSV files)
│   ├── uk_equity_returns.csv
│   ├── uk_bond_returns.csv
│   ├── uk_inflation_rates.csv
│   └── portfolio_allocations.csv
├── src/                      # Core application modules
│   ├── __init__.py
│   ├── models.py            # Data classes (UserInput, PortfolioAllocation, etc.)
│   ├── data_manager.py      # HistoricalDataManager class
│   ├── portfolio_manager.py # Portfolio allocation logic
│   ├── tax_calculator.py    # UK tax calculations
│   ├── guard_rails.py       # Guard rails withdrawal system
│   ├── simulator.py         # Monte Carlo simulation engine
│   ├── analyzer.py          # Results analysis and statistics
│   ├── charts.py            # Chart generation with matplotlib
│   └── cli.py               # Command-line interface logic
├── tests/                   # Unit and integration tests
│   ├── __init__.py
│   ├── test_tax_calculator.py
│   ├── test_guard_rails.py
│   ├── test_simulator.py
│   └── test_integration.py
└── .kiro/                   # Kiro configuration
    ├── specs/               # Project specifications
    └── steering/            # AI assistant guidance
```

## Module Responsibilities

- **main.py**: Application entry point, orchestrates all components
- **models.py**: Core data structures using Python dataclasses
- **data_manager.py**: Loads and validates historical CSV data
- **tax_calculator.py**: UK-specific tax calculations for withdrawals
- **guard_rails.py**: Dynamic spending adjustment logic
- **simulator.py**: Monte Carlo engine with bootstrap sampling
- **analyzer.py**: Success rate calculations and percentile analysis
- **charts.py**: Time series visualization generation

## File Naming Conventions

- **Snake case**: All Python files use snake_case naming
- **Descriptive names**: Module names clearly indicate their purpose
- **Test prefix**: Test files prefixed with `test_`
- **CSV data**: Historical data files use descriptive names with underscores

## Import Structure

- **Relative imports**: Within src/ package use relative imports
- **Absolute imports**: External libraries use absolute imports
- **Grouped imports**: Standard library, third-party, then local imports

## Configuration Files

- **requirements.txt**: Pinned dependency versions for reproducibility
- **CSV data files**: Easily updatable historical market data
- **No config files**: Simple hardcoded defaults that can be modified in code
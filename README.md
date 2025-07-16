# Kiro Simple Retirement Planner

A command-line retirement prediction tool that uses Monte Carlo simulation with historical UK market data to calculate when you can retire with 99% confidence of not running out of money by age 100.

## Features

- **Monte Carlo Simulation**: Uses historical stock and bond returns to run 10,000+ retirement scenarios
- **Multiple Portfolio Allocations**: Tests 6 different portfolio mixes from 100% cash to 100% equity
- **Guard Rails System**: Implements dynamic spending adjustments based on portfolio performance  
- **UK Tax Integration**: Automatically calculates UK taxes on retirement withdrawals
- **Real Returns Focus**: All calculations in inflation-adjusted terms (today's purchasing power)
- **High Confidence Threshold**: Targets 99% success rate for retirement feasibility

## Installation

1. Clone or download this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the retirement calculator:
```bash
python3 main.py
```

### Command Line Options

```bash
python3 main.py --help
```

Options:
- `--simulations, -s`: Number of Monte Carlo simulations (default: 10,000)
- `--charts, -c`: Generate charts automatically
- `--verbose, -v`: Enable verbose output

### Example Usage

```bash
# Run with 5,000 simulations and generate charts
python3 main.py --simulations 5000 --charts

# Run with reduced simulations for faster testing
python3 main.py -s 1000
```

## Input Requirements

The tool will prompt you for:
- **Current age** (18-80)
- **Current savings** (in £)
- **Monthly savings** (in £)
- **Desired annual retirement income** (after-tax, in £)

## Output

The tool provides:
- **Recommended portfolio allocation** for optimal retirement timing
- **Retirement age** for each portfolio with 99% confidence
- **Success rates** for all 6 portfolio allocations
- **Portfolio comparison** showing trade-offs between risk and retirement age
- **Improvement suggestions** for better retirement outcomes
- **Retirement readiness score** (0-100)

## Portfolio Allocations Tested

1. **100% Cash** - No real return after inflation
2. **100% Bonds** - Conservative bond allocation
3. **25% Equities/75% Bonds** - Conservative mixed allocation
4. **50% Equities/50% Bonds** - Balanced allocation
5. **75% Equities/25% Bonds** - Growth-oriented allocation
6. **100% Equities** - Aggressive growth allocation

## Guard Rails System

The tool implements a dynamic spending adjustment system:
- **Upper Guard Rail**: 20% above initial portfolio value → normal spending
- **Lower Guard Rail**: 15% below initial portfolio value → reduce spending by 10%
- **Severe Guard Rail**: 25% below initial portfolio value → reduce spending by 20%

## Tax Calculations

Uses current UK tax brackets (2024/25):
- Personal allowance: £12,570
- Basic rate: 20% (£12,570 - £50,270)
- Higher rate: 40% (£50,270 - £125,140)
- Additional rate: 45% (above £125,140)

## Technical Details

### Architecture

- **Modular Design**: Clear separation between data management, simulation, tax calculations, and output
- **Bootstrap Sampling**: Uses historical return sequences rather than theoretical distributions
- **Real Returns**: All calculations in inflation-adjusted terms
- **Monte Carlo Engine**: Runs thousands of scenarios to assess retirement feasibility

### Data Sources

The tool uses historical UK market data:
- UK equity returns (1980-2023)
- UK bond returns (1980-2023)
- UK inflation rates (1980-2023)

### Performance

- **10,000 simulations**: Typically completes in 2-3 minutes
- **Memory efficient**: Processes simulations in batches
- **Progress feedback**: Shows progress during long calculations

## Testing

Run the test suite:
```bash
python3 -m pytest tests/ -v
```

Test coverage includes:
- UK tax calculation scenarios
- Guard rails system behavior
- Portfolio allocation logic
- Monte Carlo simulation accuracy
- End-to-end integration testing

## File Structure

```
retirement-calculator/
├── main.py                    # Entry point and CLI interface
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── data/                     # Historical market data
│   ├── uk_equity_returns.csv
│   ├── uk_bond_returns.csv
│   └── uk_inflation_rates.csv
├── src/                      # Core application modules
│   ├── models.py            # Data classes
│   ├── data_manager.py      # Historical data management
│   ├── portfolio_manager.py # Portfolio allocation logic
│   ├── tax_calculator.py    # UK tax calculations
│   ├── guard_rails.py       # Guard rails system
│   ├── simulator.py         # Monte Carlo simulation
│   ├── analyzer.py          # Results analysis
│   ├── charts.py            # Chart generation
│   └── cli.py               # Command-line interface
└── tests/                   # Unit and integration tests
    ├── test_tax_calculator.py
    ├── test_guard_rails.py
    └── test_integration.py
```

## Design Philosophy

This tool prioritizes:
- **Simplicity**: Single command execution with clear output
- **Effectiveness**: Focus on core retirement planning using proven methodologies
- **Maintainability**: Modular design with easily updatable data files
- **Transparency**: Open source with comprehensive testing

## Limitations

- UK-specific tax calculations (designed for UK residents)
- Historical data may not predict future performance
- Does not account for other income sources in retirement
- Assumes constant real spending throughout retirement (with guard rails adjustments)

## Contributing

This is a focused retirement planning tool. The codebase is designed to be:
- Easy to understand and modify
- Well-tested with comprehensive unit tests
- Documented with clear code comments
- Extensible for additional features

## License

This project is designed as a simple, effective retirement planning tool. See the code for implementation details.

## Disclaimer

This tool is for educational and planning purposes only. It should not be considered as financial advice. Always consult with qualified financial advisors for retirement planning decisions.
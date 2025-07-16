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

### Prerequisites

- Python 3.7 or later
- pip package manager

### Installation Steps

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd kiro-simple-retirement-planner
   ```

2. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Required Dependencies

The tool requires the following Python packages:
- `numpy` - Numerical computing and array operations
- `pandas` - Data manipulation and CSV file handling
- `matplotlib` - Chart generation and visualization
- `click` - Command-line interface framework
- `tqdm` - Progress bar display during simulations
- `pytest` - Testing framework (for running tests)

### Alternative Installation

If you don't have a requirements.txt file, install dependencies manually:
```bash
pip install numpy pandas matplotlib click tqdm pytest
```

### Verify Installation

Test that the installation works:
```bash
python3 main.py --help
```

This should display the help text for the retirement calculator.

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

### Methodology

**Monte Carlo Simulation Process:**
1. **Historical Bootstrap**: Randomly samples years from 1980-2023 historical data
2. **Real Return Calculation**: Converts nominal returns to real returns using formula: `(1 + nominal) / (1 + inflation) - 1`
3. **Portfolio Construction**: Applies allocation weights to equity, bond, and cash components
4. **Accumulation Phase**: Simulates savings growth from current age to retirement
5. **Withdrawal Phase**: Applies guard rails system and tax calculations during retirement
6. **Success Assessment**: Counts scenarios where portfolio survives to age 100

**Guard Rails Implementation:**
- **Dynamic Spending**: Adjusts withdrawal amounts based on portfolio performance
- **Sequence Risk Protection**: Reduces spending during poor market periods
- **Recovery Mechanism**: Allows spending to normalize when portfolio recovers

**Tax Integration:**
- **Gross Calculation**: Determines pre-tax withdrawal needed for desired net income
- **Progressive Tax**: Applies UK tax brackets including personal allowance
- **Real-time Adjustment**: Recalculates tax burden each simulation year

### Data Sources

The tool uses historical UK market data:
- **UK equity returns (1980-2023)**: FTSE All-Share index annual returns
- **UK bond returns (1980-2023)**: UK government bond index returns
- **UK inflation rates (1980-2023)**: Consumer Price Index (CPI) data

**Data Quality Features:**
- 44 years of historical data covering multiple market cycles
- Includes major market events (1987 crash, 2008 crisis, dot-com bubble)
- Real return calculation using proper compound formula
- Validation checks for data consistency and reasonable ranges

### Performance

- **10,000 simulations**: Typically completes in 2-3 minutes
- **Memory efficient**: Processes simulations in batches
- **Progress feedback**: Shows progress during long calculations
- **Scalable**: Can handle 1,000 to 100,000+ simulations

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

## Troubleshooting

### Common Issues

**1. Import Errors**
```
ModuleNotFoundError: No module named 'src.models'
```
**Solution**: Make sure you're running from the project root directory and that all `__init__.py` files are present in the src/ directory.

**2. Missing Data Files**
```
FileNotFoundError: Equity returns file not found: data/uk_equity_returns.csv
```
**Solution**: Ensure all CSV files are present in the data/ directory:
- `uk_equity_returns.csv`
- `uk_bond_returns.csv`
- `uk_inflation_rates.csv`

**3. Memory Issues with Large Simulations**
```
MemoryError: Unable to allocate array
```
**Solution**: Reduce the number of simulations using the `-s` flag:
```bash
python3 main.py -s 1000
```

**4. Slow Performance**
If simulations are taking too long, try:
- Reducing simulation count: `python3 main.py -s 5000`
- Running without chart generation first
- Checking available system memory

**5. Invalid Input Values**
```
ValueError: Current age must be between 18 and 80
```
**Solution**: Ensure input values are within reasonable ranges:
- Age: 18-80 years
- Savings: Positive values
- Monthly savings: Positive values
- Desired income: Positive values

**6. Chart Generation Issues**
```
ImportError: No module named 'matplotlib'
```
**Solution**: Install matplotlib:
```bash
pip install matplotlib
```

**7. Unusual Results**
If retirement age seems too high or success rates are very low:
- Check that your desired income is realistic relative to your savings
- Consider increasing monthly savings amounts
- Verify that current age and savings are correct

### Performance Tips

- **Start Small**: Begin with 1,000-2,000 simulations for quick testing
- **Use Verbose Mode**: Add `-v` flag to see detailed progress
- **Monitor Memory**: Large simulations may require 1-2GB RAM
- **Chart Generation**: Can be disabled for faster runs if not needed

### Data Validation

The tool includes built-in validation for:
- Data file format consistency
- Reasonable return value ranges
- Minimum data requirements (10+ years)
- Input parameter bounds

### Getting Help

If you encounter issues:
1. Check the error message carefully
2. Verify all dependencies are installed
3. Ensure data files are complete and properly formatted
4. Try running with reduced simulations first
5. Check that input values are reasonable

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
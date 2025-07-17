# Kiro Simple Retirement Planner

A command-line retirement prediction tool that uses Monte Carlo simulation with historical UK market data to calculate when you can retire with your chosen confidence level (50-100%) of not running out of money by age 100.

## Key Features

- **Monte Carlo Simulation**: Uses historical stock and bond returns to run 10,000+ retirement scenarios
- **Multiple Portfolio Allocations**: Tests 7 different portfolio mixes from 100% cash to 100% equity, including dynamic glide path
- **Guard Rails System**: Implements dynamic spending adjustments based on portfolio performance  
- **UK Tax Integration**: Automatically calculates UK taxes on retirement withdrawals
- **Real Returns Focus**: All calculations in inflation-adjusted terms (today's purchasing power)
- **User-Selectable Success Rate**: Choose your own risk tolerance (50-100% success rate)
- **Comprehensive Analysis**: Provides detailed comparison across all portfolio allocations
- **Visual Charts**: Generates time-series charts showing portfolio performance over time

## Installation

### Prerequisites

- **Python 3.8 or later** (Python 3.7+ supported, but 3.8+ recommended)
- **pip package manager** (usually comes with Python)
- **At least 1GB RAM** for large simulations
- **50MB disk space** for the application and data files

### Quick Installation

1. **Download or clone this repository**
   ```bash
   # If using git
   git clone <repository-url>
   cd retirement-calculator
   
   # Or download and extract the ZIP file, then navigate to the directory
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python main.py --help
   ```

### Detailed Installation Steps

#### Step 1: Check Python Version
```bash
python --version
# or
python3 --version
```
Ensure you have Python 3.8 or later. If not, download from [python.org](https://www.python.org/downloads/).

#### Step 2: Set Up Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv retirement-calc-env

# Activate virtual environment
# On Windows:
retirement-calc-env\Scripts\activate
# On macOS/Linux:
source retirement-calc-env/bin/activate
```

#### Step 3: Install Required Dependencies
The tool requires these specific packages with minimum versions:

| Package | Version | Purpose |
|---------|---------|---------|
| numpy | ≥1.21.0 | Numerical calculations and Monte Carlo simulations |
| pandas | ≥1.3.0 | Historical data loading and manipulation |
| matplotlib | ≥3.4.0 | Chart generation and visualization |
| click | ≥8.0.0 | Command-line interface framework |
| tqdm | ≥4.62.0 | Progress bars during long simulations |
| pytest | ≥6.0.0 | Testing framework (development only) |

```bash
# Install from requirements.txt (recommended)
pip install -r requirements.txt

# Or install manually with specific versions
pip install "numpy>=1.21.0" "pandas>=1.3.0" "matplotlib>=3.4.0" "click>=8.0.0" "tqdm>=4.62.0" "pytest>=6.0.0"
```

#### Step 4: Verify Data Files
Ensure these CSV files exist in the `data/` directory:
```bash
ls data/
# Should show:
# uk_equity_returns.csv
# uk_bond_returns.csv  
# uk_inflation_rates.csv
```

#### Step 5: Test Installation
```bash
# Test basic functionality
python main.py --help

# Run a quick test with minimal simulations
python main.py -s 100
```

### Platform-Specific Installation

#### Windows
```cmd
# Use Command Prompt or PowerShell
python -m pip install -r requirements.txt
python main.py --help
```

#### macOS
```bash
# May need to use python3 explicitly
python3 -m pip install -r requirements.txt
python3 main.py --help
```

#### Linux (Ubuntu/Debian)
```bash
# Install Python development headers if needed
sudo apt update
sudo apt install python3-dev python3-pip

# Install dependencies
pip3 install -r requirements.txt
python3 main.py --help
```

### Alternative Installation Methods

#### Using conda
```bash
# Create conda environment
conda create -n retirement-calc python=3.8
conda activate retirement-calc

# Install packages
conda install numpy pandas matplotlib click tqdm pytest
```

#### Docker Installation (Advanced)
```dockerfile
# Create Dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Troubleshooting Installation

**Common Installation Issues:**

1. **Permission Errors**
   ```bash
   # Use --user flag to install for current user only
   pip install --user -r requirements.txt
   ```

2. **Outdated pip**
   ```bash
   # Upgrade pip first
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Missing C++ Compiler (Windows)**
   - Install Microsoft Visual C++ Build Tools
   - Or use pre-compiled wheels: `pip install --only-binary=all -r requirements.txt`

4. **Apple Silicon Mac Issues**
   ```bash
   # Use conda for better compatibility
   conda install numpy pandas matplotlib
   pip install click tqdm pytest
   ```

## Usage

### Basic Usage

Run the retirement calculator with default settings:
```bash
python main.py
```

The tool will guide you through entering your financial information and then run a comprehensive analysis.

### Command Line Options

View all available options:
```bash
python main.py --help
```

**Available Options:**
- `--simulations, -s INTEGER`: Number of Monte Carlo simulations (default: 10,000)
- `--charts, -c`: Generate charts automatically without prompting
- `--verbose, -v`: Enable verbose output with detailed progress information
- `--help`: Show help message and exit

### Example Usage Scenarios

#### Quick Test Run (Fast)
```bash
# Run with fewer simulations for quick testing
python main.py -s 1000
```

#### Full Analysis with Charts
```bash
# Run full analysis and automatically generate charts
python main.py --simulations 10000 --charts
```

#### Verbose Analysis
```bash
# Run with detailed progress information
python main.py --verbose --charts
```

#### High-Precision Analysis
```bash
# Run with more simulations for higher precision (slower)
python main.py -s 50000
```

### Interactive Input Process

When you run the tool, you'll be prompted for the following information:

#### 1. Current Age
```
Enter your current age (18-80): 35
```
- **Range**: 18-80 years
- **Purpose**: Determines accumulation period and retirement timeline

#### 2. Current Savings
```
Enter your current savings (£): 50000
```
- **Format**: Enter amount in pounds (no commas or currency symbols)
- **Purpose**: Starting point for portfolio growth calculations

#### 3. Monthly Savings
```
Enter your monthly savings (£): 1000
```
- **Format**: Monthly amount in pounds
- **Purpose**: Ongoing contributions during accumulation phase

#### 4. Desired Annual Income
```
Enter your desired annual retirement income (after-tax, £): 30000
```
- **Format**: Annual amount in pounds (after-tax)
- **Purpose**: Target spending level in retirement

#### 5. Target Success Rate
```
What success rate do you want to target? (50-100%): 95
```
- **Format**: Percentage (50-100)
- **Purpose**: Your risk tolerance level
- **Common choices**: 
  - 99% = Very conservative (prioritizes security)
  - 95% = Conservative (good balance)
  - 90% = Moderate (accepts some risk)
  - 85% = Aggressive (prioritizes early retirement)

### Sample Output

Here's what you can expect to see after running the analysis:

```
============================================================
RETIREMENT ANALYSIS RESULTS
============================================================

User Profile:
  Current Age: 35
  Current Savings: £50,000.00
  Monthly Savings: £1,000.00
  Desired Annual Income: £30,000.00
  Target Success Rate: 95.0%

RECOMMENDATION:
  Best Portfolio: 75% Equities/25% Bonds
  Recommended Retirement Age: 58

PORTFOLIO COMPARISON:
Portfolio                 Retirement Age  Success Rate    Median End Wealth   
---------------------------------------------------------------------------
100% Cash                 Never          0.0%            £0              
100% Bonds                67             99.2%           £245,000        
25% Equities/75% Bonds    62             99.1%           £380,000        
50% Equities/50% Bonds    59             99.3%           £520,000        
75% Equities/25% Bonds    58             99.1%           £680,000        
100% Equities             57             98.8%           £850,000        

KEY INSIGHTS:
  Earliest Possible Retirement: Age 57
  Best Success Rate: 99.3%
  Average Success Rate: 82.7%
  Withdrawal Rate: 3.2% (£37,500 from £1,170,000)
  Note: Low withdrawal rate means portfolio may grow during retirement

IMPROVEMENT SUGGESTIONS:
  1. Consider increasing monthly savings by £200 to retire 2 years earlier
  2. The 75% Equities/25% Bonds allocation provides good balance of growth and stability
  3. Your current savings rate puts you on track for a comfortable retirement

RETIREMENT READINESS SCORE: 85.2/100
```

### Chart Output

When charts are generated (using `-c` flag or when prompted), the tool creates:

1. **Portfolio Comparison Chart**: Shows retirement age for each allocation
2. **Percentile Charts**: Time-series showing 10th, 50th, and 90th percentiles for each portfolio
3. **Savings Projection Chart**: Shows portfolio growth over time

Charts are saved in the `charts/` directory with timestamps for easy reference.

### Understanding the Results

#### Retirement Age
- **Age shown**: The youngest age where your target success rate is achieved
- **"Never"**: Indicates the portfolio allocation cannot achieve your target success rate
- **Lower ages**: Generally associated with higher-risk portfolios or lower success rate targets

#### Success Rate
- **Percentage**: Proportion of simulations where money lasts until age 100
- **Target**: Your chosen success rate (defaults to 99%)
- **Interpretation**: Higher percentages indicate more reliable retirement plans but may delay retirement

#### Median End Wealth
- **Amount**: Expected portfolio value at age 100 in 50% of scenarios
- **Real terms**: All amounts shown in today's purchasing power
- **Higher values**: Indicate potential for leaving inheritance or handling unexpected expenses

## Portfolio Allocations Explained

The tool tests 7 different portfolio allocations to help you understand the trade-offs between risk and retirement timing. Each allocation represents a different investment strategy:

### 1. 100% Cash (Ultra-Conservative)
- **Composition**: 100% cash equivalents (savings accounts, money market funds)
- **Real Return**: 0% after inflation (purchasing power preserved but no growth)
- **Risk Level**: Lowest risk, but inflation risk
- **Typical Result**: Usually cannot achieve 99% success rate for retirement
- **Best For**: Emergency funds, not long-term retirement savings

### 2. 100% Bonds (Conservative)
- **Composition**: 100% UK government and high-grade corporate bonds
- **Expected Real Return**: ~1-3% annually after inflation
- **Risk Level**: Low volatility, but interest rate and inflation risk
- **Typical Result**: Longest time to retirement, but very stable
- **Best For**: Risk-averse investors close to retirement

### 3. 25% Equities/75% Bonds (Conservative Mixed)
- **Composition**: 25% UK/global stocks, 75% bonds
- **Expected Real Return**: ~2-4% annually after inflation
- **Risk Level**: Low-moderate volatility with some growth potential
- **Typical Result**: Moderate retirement timeline with good stability
- **Best For**: Conservative investors wanting some growth

### 4. 50% Equities/50% Bonds (Balanced)
- **Composition**: 50% UK/global stocks, 50% bonds
- **Expected Real Return**: ~3-5% annually after inflation
- **Risk Level**: Moderate volatility, balanced risk/reward
- **Typical Result**: Good balance of retirement timing and stability
- **Best For**: Moderate risk tolerance, classic balanced approach

### 5. 75% Equities/25% Bonds (Growth-Oriented)
- **Composition**: 75% UK/global stocks, 25% bonds
- **Expected Real Return**: ~4-6% annually after inflation
- **Risk Level**: Higher volatility but strong long-term growth
- **Typical Result**: Often the optimal choice for earlier retirement
- **Best For**: Long investment horizon, moderate-high risk tolerance

### 6. 100% Equities (Aggressive Growth)
- **Composition**: 100% UK/global stocks
- **Expected Real Return**: ~5-7% annually after inflation
- **Risk Level**: Highest volatility, maximum growth potential
- **Typical Result**: Earliest retirement age but highest risk
- **Best For**: Long investment horizon, high risk tolerance

### 7. Dynamic Glide Path (Age-Based)
- **Composition**: Automatically adjusts from 90% equities (age 25) to 20% equities (age 75+)
- **Expected Real Return**: Varies by age - higher when young, lower when older
- **Risk Level**: High growth early, conservative in retirement
- **Typical Result**: Balanced approach with good success rates and reasonable retirement age
- **Best For**: Those wanting automatic risk reduction as they age (target-date fund approach)

**Glide Path Details:**
- **Age 25 and younger**: 90% equities / 10% bonds
- **Age 25 to retirement**: Linear decrease in equity allocation
- **At retirement**: 30% equities / 70% bonds
- **Age 75 and older**: 20% equities / 80% bonds
- **Benefits**: Captures growth when young, reduces volatility near/in retirement

### Portfolio Selection Guidance

**How the Tool Chooses the Best Portfolio:**
1. **Success Rate**: Must achieve your target success rate
2. **Retirement Age**: Earlier retirement is preferred
3. **Stability**: Considers volatility and downside risk
4. **Recovery Ability**: How well the portfolio handles market downturns

**Key Insights:**
- **Higher equity allocations** generally allow earlier retirement but with more volatility
- **The "optimal" portfolio** often falls in the 50-75% equity range
- **100% equity** may not always be best due to sequence of returns risk
- **Diversification** between stocks and bonds reduces overall portfolio risk

## Guard Rails System Explained

The guard rails system is a dynamic spending adjustment mechanism that helps protect your retirement portfolio during market downturns while allowing you to maintain spending during good market conditions. This system significantly improves the probability of your money lasting throughout retirement.

### How Guard Rails Work

The system monitors your portfolio value relative to its initial retirement value and adjusts your spending accordingly:

#### 1. Upper Guard Rail (20% Above Initial Value)
- **Trigger**: Portfolio value is 20% or more above the initial retirement value
- **Action**: Allow normal spending (no reduction)
- **Purpose**: Ensures you can maintain your desired lifestyle when markets perform well
- **Example**: If you retire with £1M and your portfolio grows to £1.2M+, spend normally

#### 2. Normal Zone (Within ±15% of Initial Value)
- **Trigger**: Portfolio value is between 85% and 120% of initial retirement value
- **Action**: Normal spending continues
- **Purpose**: Provides a buffer zone for typical market fluctuations
- **Example**: Portfolio between £850K and £1.2M maintains normal spending

#### 3. Lower Guard Rail (15% Below Initial Value)
- **Trigger**: Portfolio value falls 15% below initial retirement value
- **Action**: Reduce spending by 10%
- **Purpose**: Preserves capital during moderate market downturns
- **Example**: Portfolio drops to £850K, reduce spending from £30K to £27K annually

#### 4. Severe Guard Rail (25% Below Initial Value)
- **Trigger**: Portfolio value falls 25% below initial retirement value
- **Action**: Reduce spending by 20%
- **Purpose**: Aggressive capital preservation during severe market downturns
- **Example**: Portfolio drops to £750K, reduce spending from £30K to £24K annually

### Guard Rails Benefits

#### Sequence of Returns Risk Protection
- **Problem**: Poor market returns early in retirement can devastate a portfolio
- **Solution**: Guard rails reduce spending during poor market periods, preserving capital
- **Result**: Higher probability of portfolio survival over 30+ year retirement

#### Behavioral Framework
- **Provides Structure**: Clear rules for spending adjustments remove emotional decision-making
- **Reduces Anxiety**: Knowing there's a plan for market downturns provides peace of mind
- **Maintains Flexibility**: Allows for lifestyle adjustments based on actual market performance

#### Mathematical Advantage
- **Improved Success Rates**: Studies show guard rails can improve portfolio survival rates by 10-20%
- **Reduced Required Savings**: May allow retirement with smaller initial portfolio
- **Downside Protection**: Limits the impact of worst-case market scenarios

### Guard Rails in Practice

#### Example Scenario: Market Crash in Year 2 of Retirement
```
Year 1: Portfolio £1,000,000 → Spend £30,000 (normal)
Year 2: Market crash, Portfolio £700,000 → Severe guard rail triggered
        → Reduce spending to £24,000 (20% reduction)
Year 3: Partial recovery, Portfolio £800,000 → Lower guard rail
        → Spending increases to £27,000 (10% reduction)
Year 4: Full recovery, Portfolio £950,000 → Normal zone
        → Return to normal £30,000 spending
```

#### Recovery Mechanism
- **Gradual Return**: Spending adjustments reverse as portfolio recovers
- **No Permanent Cuts**: Temporary reductions during market stress
- **Upside Participation**: Can increase spending if portfolio performs exceptionally well

### Implementation Details

#### Calculation Method
1. **Track Initial Value**: Record portfolio value at retirement start
2. **Monitor Current Value**: Check portfolio value each year
3. **Calculate Ratio**: Current value ÷ Initial value
4. **Apply Rules**: Adjust spending based on which guard rail zone applies
5. **Update Baseline**: Some implementations update the baseline periodically

#### Tax Integration
- **Gross Adjustments**: Guard rail reductions apply to gross (pre-tax) withdrawals
- **Net Impact**: Actual spending reduction accounts for tax implications
- **Efficiency**: Reduces both portfolio withdrawals and tax burden during downturns

#### Inflation Adjustments
- **Real Terms**: All guard rail calculations use inflation-adjusted values
- **Purchasing Power**: Maintains consistent purchasing power comparisons
- **Base Adjustment**: Initial portfolio value adjusted for inflation each year

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

The tool uses historical Global market data:
- **Global equity returns (1980-2023)**: MSCI World index annual returns
- **Global bond returns (1980-2023)**: Global government bond index returns
- **UK inflation rates (1980-2023)**: UK Consumer Price Index (CPI) data

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

### Common Issues and Solutions

#### 1. Installation and Setup Issues

**Import Errors**
```
ModuleNotFoundError: No module named 'src.models'
```
**Causes**: Running from wrong directory, missing `__init__.py` files, or incorrect Python path
**Solutions**:
```bash
# Ensure you're in the project root directory
pwd  # Should show path ending in retirement-calculator

# Check that src directory exists and has __init__.py
ls src/
ls src/__init__.py

# Try running with explicit Python path
PYTHONPATH=. python main.py --help
```

**Missing Dependencies**
```
ModuleNotFoundError: No module named 'numpy'
```
**Solutions**:
```bash
# Check if dependencies are installed
pip list | grep numpy

# Reinstall dependencies
pip install -r requirements.txt

# If using virtual environment, ensure it's activated
source retirement-calc-env/bin/activate  # Linux/Mac
# or
retirement-calc-env\Scripts\activate     # Windows
```

#### 2. Data File Issues

**Missing Data Files**
```
FileNotFoundError: Equity returns file not found: data/global_equity_returns.csv
```
**Solutions**:
```bash
# Check data directory exists and contains required files
ls data/
# Should show: global_equity_returns.csv, global_bond_returns.csv, uk_inflation_rates.csv

# If files are missing, ensure you have the complete download
# Check file permissions
ls -la data/
```

**Corrupted Data Files**
```
pandas.errors.EmptyDataError: No columns to parse from file
```
**Solutions**:
```bash
# Check file contents
head data/global_equity_returns.csv

# Verify file size (should not be 0 bytes)
ls -la data/*.csv

# Re-download or restore data files if corrupted
```

#### 3. Performance and Memory Issues

**Memory Issues with Large Simulations**
```
MemoryError: Unable to allocate array
```
**Solutions**:
```bash
# Reduce simulation count
python main.py -s 1000

# Check available memory
free -h  # Linux
# or check Task Manager on Windows

# Close other applications to free memory
# Consider using a machine with more RAM for large simulations
```

**Slow Performance**
**Symptoms**: Simulations taking more than 10 minutes
**Solutions**:
```bash
# Start with fewer simulations for testing
python main.py -s 2000

# Use verbose mode to monitor progress
python main.py -v -s 5000

# Skip chart generation initially
python main.py -s 10000  # Charts will be prompted separately

# Check system resources
top  # Linux/Mac
# or Task Manager on Windows
```

#### 4. Input Validation Issues

**Invalid Age Range**
```
ValueError: Current age must be between 18 and 80
```
**Solution**: Enter age between 18-80. The tool is designed for working-age adults.

**Negative or Zero Values**
```
ValueError: Savings amount must be positive
```
**Solutions**:
- Enter positive values for all financial inputs
- Use whole numbers (no commas or currency symbols)
- For zero current savings, enter a small positive value like 1

**Unrealistic Input Combinations**
**Symptoms**: Tool shows "Never" for retirement age or very low success rates
**Common Causes and Solutions**:
```
# Desired income too high relative to savings
# Example: £100K income with £10K savings and £100/month contributions
# Solution: Reduce desired income or increase savings rate

# Very low savings rate
# Example: £50/month savings with £50K desired income
# Solution: Increase monthly savings significantly

# Starting too late
# Example: Age 60 with minimal savings
# Solution: Consider working longer or reducing retirement income expectations
```

#### 5. Chart Generation Issues

**Matplotlib Import Errors**
```
ImportError: No module named 'matplotlib'
```
**Solutions**:
```bash
# Install matplotlib specifically
pip install matplotlib

# Or reinstall all dependencies
pip install -r requirements.txt

# Check matplotlib installation
python -c "import matplotlib; print(matplotlib.__version__)"
```

**Chart Display Issues**
```
UserWarning: Matplotlib is currently using agg, which is a non-GUI backend
```
**Solutions**:
```bash
# For headless servers, this is normal - charts save to files
# For desktop use, install GUI backend
pip install matplotlib[gui]

# Or set backend explicitly
export MPLBACKEND=TkAgg  # Linux/Mac
set MPLBACKEND=TkAgg     # Windows
```

#### 6. Results Interpretation Issues

**Unusual Results**
**"Never" Retirement Age**:
- **Cause**: Portfolio allocation cannot achieve your target success rate
- **Solution**: Increase savings rate, reduce desired income, or accept lower success rate target

**Very High Retirement Ages (70+)**:
- **Cause**: Conservative portfolio or high income expectations
- **Solutions**: Consider higher equity allocation, increase savings, or reduce income expectations

**All Portfolios Show Similar Results**:
- **Cause**: Very high or very low savings rate dominates portfolio allocation effects
- **Solution**: This may be correct - savings rate is more important than allocation in extreme cases

#### 7. Technical Issues

**Python Version Compatibility**
```
SyntaxError: invalid syntax (dataclass usage)
```
**Solution**: Ensure Python 3.8+ is being used:
```bash
python --version
# If using older Python, upgrade or use python3 explicitly
python3 main.py
```

**Permission Errors**
```
PermissionError: [Errno 13] Permission denied: 'charts/'
```
**Solutions**:
```bash
# Check directory permissions
ls -la

# Create charts directory manually
mkdir charts

# Run with appropriate permissions
sudo python main.py  # Not recommended
# Better: fix directory permissions
chmod 755 .
```

### Performance Optimization Tips

#### For Faster Testing
```bash
# Quick test run (30 seconds)
python main.py -s 500

# Medium test run (2-3 minutes)
python main.py -s 2000

# Production run (5-10 minutes)
python main.py -s 10000
```

#### For Large-Scale Analysis
```bash
# High precision run (20-30 minutes)
python main.py -s 50000

# Maximum precision (1+ hours)
python main.py -s 100000
```

#### Memory Management
- **Close other applications** before running large simulations
- **Use 64-bit Python** for better memory handling
- **Monitor system resources** during execution
- **Consider cloud computing** for very large simulations

### Data Validation and Quality Checks

The tool includes comprehensive validation:

#### Input Validation
- **Age range**: 18-80 years (working age adults)
- **Financial values**: Must be positive and reasonable
- **Consistency checks**: Warns about unusual input combinations

#### Data File Validation
- **File existence**: Checks all required CSV files are present
- **Data format**: Validates CSV structure and column names
- **Value ranges**: Ensures historical returns are within reasonable bounds
- **Completeness**: Requires minimum 10 years of historical data

#### Results Validation
- **Success rate bounds**: Ensures rates are between 0-100%
- **Portfolio value consistency**: Validates simulation mathematics
- **Chart data integrity**: Verifies data before visualization

### Getting Help and Support

#### Self-Diagnosis Steps
1. **Check error messages carefully** - they usually indicate the specific problem
2. **Verify installation** - run `python main.py --help` to test basic functionality
3. **Test with minimal data** - use `-s 100` for quick validation
4. **Check file permissions** - ensure you can read data files and write to charts directory
5. **Validate inputs** - ensure all values are positive and reasonable

#### Common Resolution Strategies
1. **Start simple** - use default settings first, then customize
2. **Isolate the problem** - test individual components (installation, data loading, simulation)
3. **Check system resources** - ensure adequate memory and disk space
4. **Update dependencies** - ensure you have compatible package versions
5. **Use verbose mode** - add `-v` flag to see detailed progress and error information

#### When Results Seem Wrong
1. **Verify input values** - double-check age, savings, and income figures
2. **Understand the methodology** - 99% success rate is very conservative
3. **Consider market reality** - historical data includes major crashes and recoveries
4. **Check assumptions** - the tool assumes no other retirement income sources
5. **Compare scenarios** - try different input values to understand sensitivity

#### Advanced Troubleshooting
```bash
# Enable Python debugging
python -u main.py -v -s 1000

# Check package versions
pip list | grep -E "(numpy|pandas|matplotlib)"

# Validate data files manually
python -c "import pandas as pd; print(pd.read_csv('data/global_equity_returns.csv').head())"

# Test individual components
python -c "from src.models import UserInput; print('Models import OK')"
```

## File Structure

```
retirement-calculator/
├── main.py                    # Entry point and CLI interface
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── data/                     # Historical market data
│   ├── global_equity_returns.csv
│   ├── global_bond_returns.csv
│   └── uk_inflation_rates.csv
├── src/                      # Core application modules
│   ├── models.py            # Data classes
│   ├── data_manager.py      # Historical data loading
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
    ├── test_simulator.py
    └── test_integration.py
```

## Design Philosophy

This tool prioritizes:
- **Simplicity**: Single command execution with clear output
- **Effectiveness**: Focus on core retirement planning using proven methodologies
- **Maintainability**: Modular design with easily updatable data files
- **Transparency**: Open source with comprehensive testing

## Methodology and Assumptions

### Monte Carlo Simulation Methodology

#### Historical Bootstrap Sampling
The tool uses **bootstrap sampling** from historical data rather than parametric distributions:

1. **Data Period**: Uses 44 years of UK market data (1980-2023)
2. **Sampling Method**: Randomly selects historical years with replacement
3. **Sequence Preservation**: Maintains the actual historical relationships between equity returns, bond returns, and inflation
4. **Market Cycles**: Includes multiple complete market cycles, crashes, and recoveries

#### Real Return Calculations
All calculations use **real (inflation-adjusted) returns**:

```
Real Return = (1 + Nominal Return) / (1 + Inflation Rate) - 1
```

**Example**: If stocks return 8% nominal and inflation is 3%:
```
Real Return = (1.08 / 1.03) - 1 = 4.85%
```

This ensures all projections are in today's purchasing power.

#### Simulation Process Detail

**Accumulation Phase (Current Age to Retirement)**:
1. **Monthly Contributions**: Add monthly savings to portfolio
2. **Annual Returns**: Apply randomly selected historical returns
3. **Portfolio Rebalancing**: Maintain target allocation percentages
4. **Real Growth**: All growth calculated in inflation-adjusted terms

**Withdrawal Phase (Retirement to Age 100)**:
1. **Annual Withdrawals**: Calculate gross withdrawal needed for desired net income
2. **Tax Calculation**: Apply UK tax brackets to determine actual withdrawal
3. **Guard Rails Check**: Adjust withdrawal based on portfolio performance
4. **Portfolio Update**: Apply historical returns and subtract withdrawals
5. **Success Check**: Verify portfolio value remains positive

#### Statistical Analysis
- **Success Rate**: Percentage of simulations where portfolio survives to age 100
- **Percentile Analysis**: 10th, 50th (median), and 90th percentiles of portfolio values
- **Confidence Intervals**: User-selected confidence threshold for retirement age recommendations
- **Sensitivity Analysis**: Tests multiple portfolio allocations for comparison

### Key Assumptions

#### Investment Assumptions
- **Diversified Portfolios**: Assumes broad market index investing
- **No Investment Fees**: Does not account for management fees or transaction costs
- **Rebalancing**: Assumes annual rebalancing to maintain target allocations
- **No Market Timing**: Uses systematic, disciplined investment approach
- **Liquidity**: Assumes ability to buy/sell without market impact

#### Tax Assumptions
- **Current UK Tax Rates**: Uses 2024/25 tax brackets and personal allowance
- **No Tax Changes**: Assumes current tax structure remains constant
- **Income Tax Only**: Does not include National Insurance, capital gains, or inheritance tax
- **No Tax-Advantaged Accounts**: Does not model ISAs, pensions, or other tax-sheltered savings
- **Gross Withdrawal Calculation**: Determines pre-tax amount needed for desired after-tax income

#### Retirement Assumptions
- **Constant Real Spending**: Maintains same purchasing power throughout retirement (with guard rail adjustments)
- **No Other Income**: Does not include state pension, workplace pensions, or other retirement income
- **Age 100 Target**: Plans for money to last until age 100
- **No Long-Term Care**: Does not specifically model long-term care costs
- **No Inheritance Goals**: Focuses on spending money rather than leaving bequests

#### Economic Assumptions
- **Historical Patterns Continue**: Assumes future returns will be similar to historical patterns
- **Market Efficiency**: Assumes markets are reasonably efficient over long periods
- **No Structural Changes**: Does not model major economic or demographic shifts
- **Inflation Consistency**: Uses historical inflation patterns for future projections

### Limitations and Considerations

#### Model Limitations
- **UK-Specific**: Tax calculations and data sources are UK-focused
- **Historical Bias**: Past performance may not predict future results
- **Simplified Tax Model**: Does not capture all nuances of UK tax system
- **No Behavioral Factors**: Assumes disciplined saving and spending behavior
- **Static Assumptions**: Does not adapt assumptions based on changing circumstances

#### Data Limitations
- **44-Year Period**: Limited to post-1980 UK market data
- **Survivorship Bias**: Historical data may not include failed markets or companies
- **Index Returns**: Uses broad market indices rather than individual stock performance
- **Currency Risk**: Does not model currency fluctuations for international investments

#### Practical Considerations
- **Implementation Gap**: Real-world results may differ due to fees, taxes, and behavior
- **Changing Circumstances**: Life events may require plan adjustments
- **Market Evolution**: Financial markets and products continue to evolve
- **Regulatory Changes**: Tax laws and retirement rules may change over time

### Validation and Accuracy

#### Model Validation
- **Cross-Validation**: Results tested against different historical periods
- **Sensitivity Analysis**: Tested with various input parameters
- **Benchmark Comparison**: Results compared to academic retirement research
- **Edge Case Testing**: Validated with extreme market scenarios

#### Accuracy Considerations
- **Statistical Significance**: 10,000+ simulations provide robust statistical basis
- **Confidence Intervals**: User-selected threshold allows for personal risk tolerance
- **Conservative Approach**: Default 99% threshold errs on side of caution
- **Regular Updates**: Historical data and assumptions updated periodically

## Limitations

- **UK-specific tax calculations** (designed for UK residents)
- **Historical data may not predict future performance**
- **Does not account for other income sources in retirement** (state pension, workplace pensions)
- **Assumes constant real spending throughout retirement** (with guard rails adjustments)
- **Does not include investment fees or transaction costs**
- **Uses current tax rates** (may change in future)
- **Does not model long-term care costs or major health expenses**
- **Assumes disciplined investment behavior** (no panic selling or market timing)

## Contributing

This is a focused retirement planning tool designed for simplicity and effectiveness. The codebase is structured to be:

- **Easy to understand and modify** with clear module separation
- **Well-tested** with comprehensive unit and integration tests
- **Documented** with detailed code comments and docstrings
- **Extensible** for additional features while maintaining core simplicity

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd retirement-calculator

# Set up development environment
python -m venv dev-env
source dev-env/bin/activate  # Linux/Mac
# or dev-env\Scripts\activate  # Windows

# Install dependencies including development tools
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Run with test data
python main.py -s 1000
```

### Code Structure
- **Modular design** with clear separation of concerns
- **Data classes** for type safety and clarity
- **Comprehensive error handling** with user-friendly messages
- **Progress indicators** for long-running operations
- **Extensive testing** covering edge cases and integration scenarios

## License

This project is designed as a simple, effective retirement planning tool for educational and personal planning purposes. The code is structured to be easily understood, modified, and extended while maintaining focus on core retirement planning functionality.

## Disclaimer

**Important**: This tool is for educational and planning purposes only. It should not be considered as professional financial advice. The projections are based on historical data and mathematical models that may not accurately predict future market performance.

**Key Disclaimers**:
- **Past performance does not guarantee future results**
- **Market conditions and economic factors can change significantly**
- **Individual circumstances vary and may require different approaches**
- **Tax laws and retirement regulations may change**
- **Professional financial advice is recommended for major financial decisions**

**Always consult with qualified financial advisors** for comprehensive retirement planning that considers your complete financial situation, risk tolerance, and personal goals.

---

**Version**: 1.0.1  
**Last Updated**: January 2025  
**Compatibility**: Python 3.8+, UK tax system 2024/25  

## Web Interface

In addition to the command-line interface, the tool now includes a modern web application that provides the same powerful retirement planning capabilities through an intuitive browser interface.

### Web Application Features

- **Interactive Form**: User-friendly web form with real-time validation
- **Dynamic Charts**: Interactive Plotly.js visualizations that update with your data
- **Scenario Management**: Save and compare multiple retirement scenarios
- **Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile devices
- **Progress Tracking**: Real-time progress indicators for calculations
- **Results Export**: Download results as JSON or print professional reports
- **Quick Edit**: Modify inputs and recalculate without starting over

### Accessing the Web Interface

#### Local Development
```bash
# Start the web application
python app.py

# Open your browser to:
http://localhost:5000
```

#### Production Deployment
The web application is configured for deployment on Vercel:
- **Main Application**: Access the calculator form
- **Results Page**: View detailed analysis and interactive charts
- **Deployment Status**: `/deployment-status` for system health monitoring

### Web Interface Components

#### Calculator Form (`/`)
- **Input Validation**: Real-time validation with helpful error messages
- **Progress Indicators**: Shows calculation progress during processing
- **Mobile Optimized**: Responsive design for all screen sizes

#### Results Display (`/results`)
- **Portfolio Comparison**: Interactive table showing all portfolio allocations
- **Interactive Charts**: Plotly.js charts with zoom, pan, and export capabilities
- **Scenario Management**: Save current scenario and compare with previous calculations
- **Quick Edit**: Modify inputs without losing current results

#### API Endpoints
- `POST /calculate` - Run retirement calculations
- `GET /health` - System health check
- `GET /deployment-status` - Detailed system status
- `POST /api/quick-test` - Quick system verification

### Technology Stack

- **Backend**: Flask 2.3.3 (Python web framework)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Plotly.js for interactive visualizations
- **Forms**: WTForms for server-side validation
- **Deployment**: Vercel (serverless platform)

### Configuration

The web application uses the same calculation engine as the CLI tool but adds:
- **Session Management**: Tracks calculation progress across requests
- **Chart Generation**: Creates interactive web-ready visualizations
- **Form Handling**: Validates and processes user inputs
- **Error Handling**: User-friendly error messages and recovery

### Deployment

The web application is configured for Vercel deployment:
- **Build Configuration**: `vercel.json` defines build settings
- **Environment Variables**: Automatically configured for production
- **Performance**: Optimized for 1024MB memory, 30-second timeout
- **Monitoring**: Built-in health checks and status pages

### Changelog
- **v1.1.0**: Added web interface with interactive charts and scenario management
- **v1.0.1**: Added user-selectable success rate feature (50-100%)
- **v1.0.0**: Initial release with dynamic glide path and chart organization
# Technology Stack

## Core Technologies

- **Python 3.8+**: Primary language for all components
- **NumPy**: Numerical calculations and efficient array operations
- **Pandas**: Data manipulation and CSV file handling
- **Matplotlib**: Time series chart generation and visualization
- **Click**: Command-line interface framework for user interaction

## Architecture Approach

- **Modular Design**: Clear separation between data management, simulation logic, tax calculations, and output
- **Data-Driven**: CSV files for historical data (easily updatable)
- **Object-Oriented**: Dataclasses for core models, classes for major components
- **Functional Components**: Pure functions for calculations where possible

## Data Storage

- **CSV Files**: Historical market data stored in `data/` directory
- **No Database**: Keeps deployment simple and data easily auditable
- **Real Returns**: All historical data pre-processed to inflation-adjusted terms

## Key Libraries Usage

- **NumPy**: Vectorized operations for Monte Carlo simulations
- **Pandas**: Loading and validating historical return data
- **Matplotlib**: Percentile charts (10th, 50th, 90th) over time
- **Click**: Input validation and command-line prompts

## Common Commands

```bash
# Run the retirement calculator
python main.py

# Run with verbose output
python main.py --verbose

# Run unit tests
python -m pytest tests/

# Install dependencies
pip install -r requirements.txt
```

## Performance Considerations

- **Vectorized Operations**: Use NumPy arrays for 10,000+ simulations
- **Memory Efficiency**: Process simulations in batches if needed
- **Progress Feedback**: Show progress for long-running calculations
"""
Command-line interface for data quality validation and reporting.

This module provides a CLI tool for validating historical data files
and generating comprehensive data quality reports.
"""

import click
import sys
import os
from .data_manager import HistoricalDataManager
from .data_validator import DataValidator


@click.group()
def cli():
    """Data quality validation tools for the retirement calculator."""
    pass


@cli.command()
@click.option('--data-dir', default='data', help='Directory containing data files')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
def validate(data_dir, verbose):
    """Validate historical data files for quality and consistency."""
    click.echo("🔍 Validating historical data files...")
    
    validator = DataValidator(data_dir)
    result = validator.validate_all_data_files()
    
    if result.is_valid:
        click.echo("✅ All data files passed validation!")
        
        if verbose:
            click.echo("\nValidation Details:")
            if result.info:
                click.echo("Information:")
                for info in result.info:
                    click.echo(f"  • {info}")
            
            if result.warnings:
                click.echo("\nWarnings:")
                for warning in result.warnings:
                    click.echo(f"  ⚠️  {warning}")
    else:
        click.echo("❌ Data validation failed!")
        click.echo("\nErrors:")
        for error in result.errors:
            click.echo(f"  • {error}")
        
        if result.warnings:
            click.echo("\nWarnings:")
            for warning in result.warnings:
                click.echo(f"  ⚠️  {warning}")
        
        sys.exit(1)


@cli.command()
@click.option('--data-dir', default='data', help='Directory containing data files')
@click.option('--output', '-o', help='Output file for the report')
def report(data_dir, output):
    """Generate a comprehensive data quality report."""
    click.echo("📊 Generating data quality report...")
    
    data_manager = HistoricalDataManager(data_dir)
    report_content = data_manager.get_data_quality_report()
    
    if output:
        with open(output, 'w') as f:
            f.write(report_content)
        click.echo(f"Report saved to: {output}")
    else:
        click.echo(report_content)


@cli.command()
@click.option('--data-dir', default='data', help='Directory containing data files')
def stats(data_dir):
    """Show statistical summary of loaded data."""
    click.echo("📈 Loading data statistics...")
    
    try:
        data_manager = HistoricalDataManager(data_dir)
        data_manager.load_all_data(validate_quality=False)  # Skip validation for stats
        
        stats = data_manager.get_data_statistics()
        
        for data_type, stat_dict in stats.items():
            click.echo(f"\n{data_type.replace('_', ' ').title()}:")
            for key, value in stat_dict.items():
                if key.startswith('year_range'):
                    continue
                elif key in ['mean', 'std', 'min', 'max']:
                    click.echo(f"  {key}: {value:.4f}")
                else:
                    click.echo(f"  {key}: {value}")
            
            if 'year_range_start' in stat_dict and 'year_range_end' in stat_dict:
                click.echo(f"  year_range: {stat_dict['year_range_start']}-{stat_dict['year_range_end']}")
    
    except Exception as e:
        click.echo(f"❌ Error loading data: {e}")
        sys.exit(1)


@cli.command()
@click.option('--data-dir', default='data', help='Directory containing data files')
def check(data_dir):
    """Quick health check of data files."""
    click.echo("🏥 Performing quick health check...")
    
    # Check if directory exists
    if not os.path.exists(data_dir):
        click.echo(f"❌ Data directory not found: {data_dir}")
        sys.exit(1)
    
    # Check for required files
    required_files = [
        'uk_equity_returns.csv',
        'uk_bond_returns.csv', 
        'uk_inflation_rates.csv'
    ]
    
    missing_files = []
    for filename in required_files:
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            missing_files.append(filename)
    
    if missing_files:
        click.echo("❌ Missing required files:")
        for filename in missing_files:
            click.echo(f"  • {filename}")
        sys.exit(1)
    
    # Quick validation
    validator = DataValidator(data_dir)
    result = validator.validate_all_data_files()
    
    if result.is_valid:
        click.echo("✅ All files present and valid!")
        
        # Show basic info
        if 'cross_validation' in result.data_summary:
            cv_data = result.data_summary['cross_validation']
            overlap_years = cv_data.get('overlapping_years', 0)
            quality_score = cv_data.get('average_quality_score', 0)
            
            click.echo(f"📊 Data quality: {quality_score:.1f}/100")
            click.echo(f"📅 Overlapping years: {overlap_years}")
    else:
        click.echo("❌ Data validation issues found!")
        click.echo("Run 'validate' command for details.")
        sys.exit(1)


if __name__ == '__main__':
    cli()
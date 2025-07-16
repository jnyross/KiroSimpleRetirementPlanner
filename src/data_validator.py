"""
Data validation and quality checking system for historical market data.

This module provides comprehensive validation of historical data files,
including data consistency checks, reasonable range validation, and
data quality reporting with warnings for missing or problematic data.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ValidationResult:
    """Result of data validation with details about issues found."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    info: List[str]
    data_summary: Dict[str, Any]


@dataclass
class DataQualityReport:
    """Comprehensive data quality report for historical data."""
    file_name: str
    total_records: int
    year_range: Tuple[int, int]
    missing_years: List[int]
    duplicate_years: List[int]
    outliers: List[Tuple[int, float]]
    data_gaps: List[Tuple[int, int]]  # (start_year, end_year) of gaps
    statistics: Dict[str, float]
    quality_score: float  # 0-100 score


class DataValidator:
    """Comprehensive data validation and quality checking system."""
    
    def __init__(self, data_directory: str = "data"):
        """
        Initialize the data validator.
        
        Args:
            data_directory: Directory containing CSV data files
        """
        self.data_directory = data_directory
        
        # Expected data ranges for validation
        self.expected_ranges = {
            'equity_returns': (-0.90, 3.00),  # -90% to +300%
            'bond_returns': (-0.70, 1.50),   # -70% to +150%
            'inflation_rates': (-0.30, 0.50)  # -30% to +50%
        }
        
        # Outlier thresholds (number of standard deviations)
        self.outlier_threshold = 3.0
        
        # Minimum required years of data
        self.min_years_required = 10
    
    def validate_all_data_files(self) -> ValidationResult:
        """
        Validate all required historical data files.
        
        Returns:
            ValidationResult with comprehensive validation details
        """
        errors = []
        warnings = []
        info = []
        data_summary = {}
        
        # Check if data directory exists
        if not os.path.exists(self.data_directory):
            errors.append(f"Data directory does not exist: {self.data_directory}")
            return ValidationResult(False, errors, warnings, info, data_summary)
        
        info.append(f"Data directory found: {self.data_directory}")
        
        # Define required files and their validation functions
        required_files = {
            'uk_equity_returns.csv': ('equity_returns', self._validate_equity_returns),
            'uk_bond_returns.csv': ('bond_returns', self._validate_bond_returns),
            'uk_inflation_rates.csv': ('inflation_rates', self._validate_inflation_rates)
        }
        
        # Validate each file
        file_results = {}
        for filename, (data_type, validator_func) in required_files.items():
            file_path = os.path.join(self.data_directory, filename)
            
            if not os.path.exists(file_path):
                errors.append(f"Required data file missing: {filename}")
                continue
            
            try:
                result = validator_func(file_path)
                file_results[data_type] = result
                
                # Collect errors and warnings from file validation
                errors.extend([f"{filename}: {error}" for error in result.errors])
                warnings.extend([f"{filename}: {warning}" for warning in result.warnings])
                info.extend([f"{filename}: {info_item}" for info_item in result.info])
                
                data_summary[data_type] = result.data_summary
                
            except Exception as e:
                errors.append(f"Unexpected error validating {filename}: {str(e)}")
        
        # Cross-file validation if all files loaded successfully
        if len(file_results) == 3:
            cross_validation = self._validate_data_consistency(file_results)
            errors.extend(cross_validation.errors)
            warnings.extend(cross_validation.warnings)
            info.extend(cross_validation.info)
            data_summary['cross_validation'] = cross_validation.data_summary
        
        # Determine overall validation result
        is_valid = len(errors) == 0
        
        return ValidationResult(is_valid, errors, warnings, info, data_summary)
    
    def _validate_equity_returns(self, file_path: str) -> ValidationResult:
        """Validate equity returns data file."""
        return self._validate_returns_file(
            file_path, 
            'equity_returns',
            expected_columns=['year', 'return'],
            data_type_name="Equity Returns"
        )
    
    def _validate_bond_returns(self, file_path: str) -> ValidationResult:
        """Validate bond returns data file."""
        return self._validate_returns_file(
            file_path,
            'bond_returns', 
            expected_columns=['year', 'return'],
            data_type_name="Bond Returns"
        )
    
    def _validate_inflation_rates(self, file_path: str) -> ValidationResult:
        """Validate inflation rates data file."""
        return self._validate_returns_file(
            file_path,
            'inflation_rates',
            expected_columns=['year', 'inflation_rate'],
            data_type_name="Inflation Rates"
        )
    
    def _validate_returns_file(self, file_path: str, data_type: str, 
                              expected_columns: List[str], data_type_name: str) -> ValidationResult:
        """
        Generic validation for returns/rates data files.
        
        Args:
            file_path: Path to the CSV file
            data_type: Type of data for range validation
            expected_columns: List of expected column names
            data_type_name: Human-readable name for error messages
        """
        errors = []
        warnings = []
        info = []
        data_summary = {}
        
        try:
            # Load the CSV file
            try:
                df = pd.read_csv(file_path)
            except pd.errors.EmptyDataError:
                errors.append(f"File is empty")
                return ValidationResult(False, errors, warnings, info, data_summary)
            except pd.errors.ParserError as e:
                errors.append(f"Cannot parse CSV file: {str(e)}")
                return ValidationResult(False, errors, warnings, info, data_summary)
            
            # Basic structure validation
            if df.empty:
                errors.append("File contains no data")
                return ValidationResult(False, errors, warnings, info, data_summary)
            
            # Column validation
            missing_columns = [col for col in expected_columns if col not in df.columns]
            if missing_columns:
                errors.append(f"Missing required columns: {missing_columns}")
                errors.append(f"Available columns: {list(df.columns)}")
                return ValidationResult(False, errors, warnings, info, data_summary)
            
            extra_columns = [col for col in df.columns if col not in expected_columns]
            if extra_columns:
                warnings.append(f"Unexpected columns found (will be ignored): {extra_columns}")
            
            # Data type validation
            year_col = 'year'
            value_col = expected_columns[1]  # 'return' or 'inflation_rate'
            
            if not pd.api.types.is_numeric_dtype(df[year_col]):
                errors.append(f"'{year_col}' column must contain numeric values")
            
            if not pd.api.types.is_numeric_dtype(df[value_col]):
                errors.append(f"'{value_col}' column must contain numeric values")
            
            if errors:  # Don't continue if basic validation failed
                return ValidationResult(False, errors, warnings, info, data_summary)
            
            # Missing values check
            missing_years = df[year_col].isna().sum()
            missing_values = df[value_col].isna().sum()
            
            if missing_years > 0:
                errors.append(f"Missing values in '{year_col}' column: {missing_years} rows")
            
            if missing_values > 0:
                if missing_values <= 2:  # Allow a few missing values with warning
                    warnings.append(f"Missing values in '{value_col}' column: {missing_values} rows (will be interpolated)")
                else:
                    errors.append(f"Too many missing values in '{value_col}' column: {missing_values} rows")
            
            # Remove rows with missing data for further validation
            df_clean = df.dropna()
            
            if len(df_clean) < self.min_years_required:
                errors.append(f"Insufficient data after removing missing values: {len(df_clean)} years (minimum: {self.min_years_required})")
                return ValidationResult(False, errors, warnings, info, data_summary)
            
            # Year validation
            years = df_clean[year_col].astype(int)
            current_year = datetime.now().year
            
            if years.min() < 1800:
                warnings.append(f"Very old data detected: earliest year is {years.min()}")
            
            if years.max() > current_year:
                errors.append(f"Future years detected: latest year is {years.max()} (current year: {current_year})")
            
            # Check for duplicate years
            duplicate_years = years[years.duplicated()].tolist()
            if duplicate_years:
                errors.append(f"Duplicate years found: {duplicate_years}")
                return ValidationResult(False, errors, warnings, info, data_summary)
            
            # Value range validation
            values = df_clean[value_col]
            min_val, max_val = self.expected_ranges[data_type]
            
            out_of_range = values[(values < min_val) | (values > max_val)]
            if len(out_of_range) > 0:
                errors.append(f"Values outside expected range ({min_val:.1%} to {max_val:.1%}): {len(out_of_range)} values")
                errors.append(f"Out of range values: {out_of_range.tolist()}")
            
            # Statistical validation and outlier detection
            mean_val = values.mean()
            std_val = values.std()
            
            # Detect outliers (only if we have enough data and variation)
            if len(values) > 5 and std_val > 0:
                z_scores = np.abs((values - mean_val) / std_val)
                outlier_mask = z_scores > self.outlier_threshold
                outliers = df_clean[outlier_mask]
                
                if len(outliers) > 0:
                    outlier_info = [(int(row[year_col]), row[value_col]) for _, row in outliers.iterrows()]
                    warnings.append(f"Statistical outliers detected (>{self.outlier_threshold} std devs): {len(outliers)} values")
                    if len(outliers) <= 5:  # Show details for small number of outliers
                        warnings.append(f"Outlier details: {outlier_info}")
            else:
                outliers = pd.DataFrame()  # Empty DataFrame if no outlier detection
            
            # Data continuity check
            years_sorted = sorted(years)
            data_gaps = self._find_data_gaps(years_sorted)
            
            if data_gaps:
                gap_info = [f"{start}-{end}" for start, end in data_gaps]
                warnings.append(f"Data gaps detected: {gap_info}")
            
            # Generate data summary
            data_summary = {
                'total_records': len(df),
                'valid_records': len(df_clean),
                'year_range': (int(years.min()), int(years.max())),
                'value_range': (float(values.min()), float(values.max())),
                'mean': float(mean_val),
                'std_dev': float(std_val),
                'missing_values': int(missing_values),
                'duplicate_years': duplicate_years,
                'outliers': len(outliers),
                'data_gaps': data_gaps
            }
            
            info.append(f"Loaded {len(df_clean)} years of data ({years.min()}-{years.max()})")
            info.append(f"Value statistics: mean={mean_val:.3f}, std={std_val:.3f}")
            
            is_valid = len(errors) == 0
            return ValidationResult(is_valid, errors, warnings, info, data_summary)
            
        except Exception as e:
            errors.append(f"Unexpected error during validation: {str(e)}")
            return ValidationResult(False, errors, warnings, info, data_summary)
    
    def _find_data_gaps(self, years_sorted: List[int]) -> List[Tuple[int, int]]:
        """
        Find gaps in the data years.
        
        Args:
            years_sorted: Sorted list of years
            
        Returns:
            List of (start_year, end_year) tuples representing gaps
        """
        gaps = []
        
        for i in range(len(years_sorted) - 1):
            current_year = years_sorted[i]
            next_year = years_sorted[i + 1]
            
            if next_year - current_year > 1:
                gaps.append((current_year + 1, next_year - 1))
        
        return gaps
    
    def _validate_data_consistency(self, file_results: Dict[str, ValidationResult]) -> ValidationResult:
        """
        Validate consistency across different data files.
        
        Args:
            file_results: Dictionary of validation results for each file
            
        Returns:
            ValidationResult for cross-file consistency
        """
        errors = []
        warnings = []
        info = []
        data_summary = {}
        
        try:
            # Extract year ranges from each file
            year_ranges = {}
            for data_type, result in file_results.items():
                if result.is_valid and 'year_range' in result.data_summary:
                    year_ranges[data_type] = result.data_summary['year_range']
            
            if len(year_ranges) < 3:
                warnings.append("Cannot perform cross-file validation due to invalid files")
                return ValidationResult(True, errors, warnings, info, data_summary)
            
            # Find overlapping years
            all_starts = [start for start, _ in year_ranges.values()]
            all_ends = [end for _, end in year_ranges.values()]
            
            overlap_start = max(all_starts)
            overlap_end = min(all_ends)
            
            if overlap_start > overlap_end:
                errors.append("No overlapping years found between all data files")
                errors.append(f"Year ranges: {year_ranges}")
            else:
                overlap_years = overlap_end - overlap_start + 1
                info.append(f"Overlapping data period: {overlap_start}-{overlap_end} ({overlap_years} years)")
                
                if overlap_years < self.min_years_required:
                    errors.append(f"Insufficient overlapping data: {overlap_years} years (minimum: {self.min_years_required})")
                elif overlap_years < 20:
                    warnings.append(f"Limited overlapping data: {overlap_years} years (recommended: 20+ years)")
            
            # Check data quality consistency
            quality_scores = []
            for data_type, result in file_results.items():
                if result.is_valid:
                    # Calculate a simple quality score based on completeness and outliers
                    summary = result.data_summary
                    total_records = summary.get('total_records', 0)
                    valid_records = summary.get('valid_records', 0)
                    outliers = summary.get('outliers', 0)
                    gaps = len(summary.get('data_gaps', []))
                    
                    completeness_score = (valid_records / total_records) * 100 if total_records > 0 else 0
                    outlier_penalty = min(outliers * 5, 30)  # Max 30 point penalty
                    gap_penalty = min(gaps * 10, 20)  # Max 20 point penalty
                    
                    quality_score = max(0, completeness_score - outlier_penalty - gap_penalty)
                    quality_scores.append(quality_score)
                    
                    info.append(f"{data_type} quality score: {quality_score:.1f}/100")
            
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                data_summary['average_quality_score'] = avg_quality
                
                if avg_quality < 70:
                    warnings.append(f"Overall data quality is moderate: {avg_quality:.1f}/100")
                elif avg_quality >= 90:
                    info.append(f"Excellent data quality: {avg_quality:.1f}/100")
                else:
                    info.append(f"Good data quality: {avg_quality:.1f}/100")
            
            data_summary['overlapping_years'] = overlap_years if overlap_start <= overlap_end else 0
            data_summary['overlap_period'] = (overlap_start, overlap_end) if overlap_start <= overlap_end else None
            
            is_valid = len(errors) == 0
            return ValidationResult(is_valid, errors, warnings, info, data_summary)
            
        except Exception as e:
            errors.append(f"Error during cross-file validation: {str(e)}")
            return ValidationResult(False, errors, warnings, info, data_summary)
    
    def generate_data_quality_report(self) -> str:
        """
        Generate a comprehensive data quality report.
        
        Returns:
            Formatted string containing the data quality report
        """
        validation_result = self.validate_all_data_files()
        
        report_lines = []
        report_lines.append("📊 DATA QUALITY REPORT")
        report_lines.append("=" * 50)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Data Directory: {self.data_directory}")
        report_lines.append("")
        
        # Overall status
        if validation_result.is_valid:
            report_lines.append("✅ OVERALL STATUS: VALID")
        else:
            report_lines.append("❌ OVERALL STATUS: INVALID")
        
        report_lines.append("")
        
        # Errors section
        if validation_result.errors:
            report_lines.append("🚨 ERRORS:")
            for error in validation_result.errors:
                report_lines.append(f"   • {error}")
            report_lines.append("")
        
        # Warnings section
        if validation_result.warnings:
            report_lines.append("⚠️  WARNINGS:")
            for warning in validation_result.warnings:
                report_lines.append(f"   • {warning}")
            report_lines.append("")
        
        # Information section
        if validation_result.info:
            report_lines.append("ℹ️  INFORMATION:")
            for info_item in validation_result.info:
                report_lines.append(f"   • {info_item}")
            report_lines.append("")
        
        # Data summary section
        if validation_result.data_summary:
            report_lines.append("📈 DATA SUMMARY:")
            
            for data_type, summary in validation_result.data_summary.items():
                if data_type == 'cross_validation':
                    continue  # Handle separately
                
                report_lines.append(f"   {data_type.replace('_', ' ').title()}:")
                if isinstance(summary, dict):
                    for key, value in summary.items():
                        if key == 'year_range':
                            report_lines.append(f"     - Year Range: {value[0]}-{value[1]}")
                        elif key == 'value_range':
                            report_lines.append(f"     - Value Range: {value[0]:.3f} to {value[1]:.3f}")
                        elif key in ['mean', 'std_dev']:
                            report_lines.append(f"     - {key.replace('_', ' ').title()}: {value:.4f}")
                        else:
                            report_lines.append(f"     - {key.replace('_', ' ').title()}: {value}")
                report_lines.append("")
            
            # Cross-validation summary
            if 'cross_validation' in validation_result.data_summary:
                cv_summary = validation_result.data_summary['cross_validation']
                report_lines.append("   Cross-File Analysis:")
                for key, value in cv_summary.items():
                    if key == 'overlap_period' and value:
                        report_lines.append(f"     - Overlap Period: {value[0]}-{value[1]}")
                    elif key != 'overlap_period':
                        report_lines.append(f"     - {key.replace('_', ' ').title()}: {value}")
                report_lines.append("")
        
        # Recommendations section
        report_lines.append("💡 RECOMMENDATIONS:")
        
        if validation_result.errors:
            report_lines.append("   • Fix all errors before using the data for analysis")
        
        if validation_result.warnings:
            report_lines.append("   • Review warnings and consider data improvements")
        
        # Specific recommendations based on data summary
        if validation_result.data_summary:
            cv_data = validation_result.data_summary.get('cross_validation', {})
            overlap_years = cv_data.get('overlapping_years', 0)
            
            if overlap_years < 20:
                report_lines.append("   • Consider adding more historical data for better analysis")
            
            avg_quality = cv_data.get('average_quality_score', 100)
            if avg_quality < 80:
                report_lines.append("   • Improve data quality by filling gaps and reviewing outliers")
        
        if validation_result.is_valid:
            report_lines.append("   • Data is ready for Monte Carlo simulation analysis")
        
        return "\n".join(report_lines)
    
    def handle_missing_years(self, df: pd.DataFrame, value_column: str) -> pd.DataFrame:
        """
        Handle missing years in historical data by interpolation.
        
        Args:
            df: DataFrame with 'year' and value columns
            value_column: Name of the value column to interpolate
            
        Returns:
            DataFrame with missing years filled by interpolation
        """
        if df.empty:
            return df
        
        # Create complete year range
        min_year = int(df['year'].min())
        max_year = int(df['year'].max())
        complete_years = pd.DataFrame({'year': range(min_year, max_year + 1)})
        
        # Merge with existing data
        df_complete = complete_years.merge(df, on='year', how='left')
        
        # Interpolate missing values
        df_complete[value_column] = df_complete[value_column].interpolate(method='linear')
        
        # Fill any remaining NaN values at the edges with forward/backward fill
        df_complete[value_column] = df_complete[value_column].fillna(method='ffill').fillna(method='bfill')
        
        return df_complete
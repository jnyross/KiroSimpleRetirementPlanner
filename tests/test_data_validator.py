"""
Unit tests for the data validation and quality checking system.

Tests comprehensive validation of historical data files, including data consistency
checks, reasonable range validation, and data quality reporting.
"""

import os
import tempfile
import shutil
import pandas as pd
import pytest
from unittest.mock import patch
from src.data_validator import DataValidator, ValidationResult, DataQualityReport


class TestDataValidator:
    """Test suite for the DataValidator class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.validator = DataValidator(self.test_dir)
    
    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        # Remove temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_test_data_file(self, filename: str, data: dict, columns: list = None):
        """Helper method to create test data files."""
        if columns is None:
            columns = list(data.keys())
        
        df = pd.DataFrame(data)
        file_path = os.path.join(self.test_dir, filename)
        df.to_csv(file_path, index=False)
        return file_path
    
    def test_validate_all_data_files_missing_directory(self):
        """Test validation when data directory doesn't exist."""
        validator = DataValidator("nonexistent_directory")
        result = validator.validate_all_data_files()
        
        assert not result.is_valid
        assert len(result.errors) > 0
        assert "Data directory does not exist" in result.errors[0]
    
    def test_validate_all_data_files_missing_files(self):
        """Test validation when required files are missing."""
        result = self.validator.validate_all_data_files()
        
        assert not result.is_valid
        assert len(result.errors) == 3  # All three files missing
        assert any("global_equity_returns.csv" in error for error in result.errors)
        assert any("global_bond_returns.csv" in error for error in result.errors)
        assert any("uk_inflation_rates.csv" in error for error in result.errors)
    
    def test_validate_equity_returns_valid_data(self):
        """Test validation of valid equity returns data."""
        # Create valid equity returns data
        equity_data = {
            'year': list(range(2000, 2021)),
            'return': [0.05 + i * 0.01 for i in range(21)]  # 5% to 25%
        }
        self.create_test_data_file("global_equity_returns.csv", equity_data)
        
        # Create valid inflation data (needed for real returns calculation)
        inflation_data = {
            'year': list(range(2000, 2021)),
            'inflation_rate': [0.02] * 21  # 2% inflation
        }
        self.create_test_data_file("uk_inflation_rates.csv", inflation_data)
        
        result = self.validator._validate_equity_returns(
            os.path.join(self.test_dir, "global_equity_returns.csv")
        )
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.data_summary['total_records'] == 21
        assert result.data_summary['year_range'] == (2000, 2020)
    
    def test_validate_equity_returns_missing_columns(self):
        """Test validation when equity returns file has missing columns."""
        # Create file with wrong columns
        equity_data = {
            'year': list(range(2000, 2011)),
            'wrong_column': [0.05] * 11
        }
        self.create_test_data_file("global_equity_returns.csv", equity_data)
        
        result = self.validator._validate_equity_returns(
            os.path.join(self.test_dir, "global_equity_returns.csv")
        )
        
        assert not result.is_valid
        assert any("Missing required columns" in error for error in result.errors)
    
    def test_validate_equity_returns_out_of_range_values(self):
        """Test validation when equity returns have unreasonable values."""
        # Create data with extreme values
        equity_data = {
            'year': list(range(2000, 2011)),
            'return': [5.0] * 11  # 500% returns - unreasonable
        }
        self.create_test_data_file("global_equity_returns.csv", equity_data)
        
        result = self.validator._validate_equity_returns(
            os.path.join(self.test_dir, "global_equity_returns.csv")
        )
        
        assert not result.is_valid
        assert any("Values outside expected range" in error for error in result.errors)
    
    def test_validate_bond_returns_valid_data(self):
        """Test validation of valid bond returns data."""
        # Create valid bond returns data
        bond_data = {
            'year': list(range(2000, 2021)),
            'return': [0.03 + i * 0.001 for i in range(21)]  # 3% to 5%
        }
        self.create_test_data_file("global_bond_returns.csv", bond_data)
        
        # Create valid inflation data
        inflation_data = {
            'year': list(range(2000, 2021)),
            'inflation_rate': [0.02] * 21
        }
        self.create_test_data_file("uk_inflation_rates.csv", inflation_data)
        
        result = self.validator._validate_bond_returns(
            os.path.join(self.test_dir, "global_bond_returns.csv")
        )
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.data_summary['total_records'] == 21
    
    def test_validate_inflation_rates_valid_data(self):
        """Test validation of valid inflation rates data."""
        # Create valid inflation data
        inflation_data = {
            'year': list(range(2000, 2021)),
            'inflation_rate': [0.02 + i * 0.001 for i in range(21)]  # 2% to 4%
        }
        self.create_test_data_file("uk_inflation_rates.csv", inflation_data)
        
        result = self.validator._validate_inflation_rates(
            os.path.join(self.test_dir, "uk_inflation_rates.csv")
        )
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.data_summary['total_records'] == 21
    
    def test_validate_inflation_rates_extreme_values(self):
        """Test validation when inflation rates have extreme values."""
        # Create data with extreme inflation
        inflation_data = {
            'year': list(range(2000, 2011)),
            'inflation_rate': [1.0] * 11  # 100% inflation - unreasonable
        }
        self.create_test_data_file("uk_inflation_rates.csv", inflation_data)
        
        result = self.validator._validate_inflation_rates(
            os.path.join(self.test_dir, "uk_inflation_rates.csv")
        )
        
        assert not result.is_valid
        assert any("Values outside expected range" in error for error in result.errors)
    
    def test_validate_data_with_missing_values(self):
        """Test validation when data files contain missing values."""
        # Create equity data with missing values
        equity_data = {
            'year': [2000, 2001, 2002, None, 2004],
            'return': [0.05, None, 0.07, 0.08, 0.09]
        }
        self.create_test_data_file("global_equity_returns.csv", equity_data)
        
        result = self.validator._validate_equity_returns(
            os.path.join(self.test_dir, "global_equity_returns.csv")
        )
        
        assert not result.is_valid
        assert any("Missing values" in error for error in result.errors)
    
    def test_validate_data_with_duplicate_years(self):
        """Test validation when data files contain duplicate years."""
        # Create data with duplicate years (enough data to pass minimum requirement)
        years = list(range(2000, 2011)) + [2005]  # Duplicate 2005
        returns = [0.05 + i * 0.01 for i in range(12)]
        equity_data = {
            'year': years,
            'return': returns
        }
        self.create_test_data_file("global_equity_returns.csv", equity_data)
        
        result = self.validator._validate_equity_returns(
            os.path.join(self.test_dir, "global_equity_returns.csv")
        )
        
        assert not result.is_valid
        assert any("Duplicate years found" in error for error in result.errors)
    
    def test_validate_data_insufficient_data(self):
        """Test validation when data files don't have enough years."""
        # Create data with only 5 years (minimum is 10)
        equity_data = {
            'year': list(range(2000, 2005)),
            'return': [0.05] * 5
        }
        self.create_test_data_file("global_equity_returns.csv", equity_data)
        
        result = self.validator._validate_equity_returns(
            os.path.join(self.test_dir, "global_equity_returns.csv")
        )
        
        assert not result.is_valid
        assert any("Insufficient data" in error for error in result.errors)
    
    def test_find_data_gaps(self):
        """Test detection of gaps in year sequences."""
        # Test with no gaps
        years_no_gaps = [2000, 2001, 2002, 2003, 2004]
        gaps = self.validator._find_data_gaps(years_no_gaps)
        assert len(gaps) == 0
        
        # Test with single gap
        years_single_gap = [2000, 2001, 2003, 2004]  # Missing 2002
        gaps = self.validator._find_data_gaps(years_single_gap)
        assert len(gaps) == 1
        assert gaps[0] == (2002, 2002)
        
        # Test with multiple gaps
        years_multiple_gaps = [2000, 2002, 2005, 2006]  # Missing 2001, 2003-2004
        gaps = self.validator._find_data_gaps(years_multiple_gaps)
        assert len(gaps) == 2
        assert (2001, 2001) in gaps
        assert (2003, 2004) in gaps
    
    def test_cross_file_validation_valid_data(self):
        """Test cross-file validation with valid overlapping data."""
        # Create all three files with overlapping years
        years = list(range(2000, 2021))
        
        equity_data = {'year': years, 'return': [0.05] * 21}
        bond_data = {'year': years, 'return': [0.03] * 21}
        inflation_data = {'year': years, 'inflation_rate': [0.02] * 21}
        
        self.create_test_data_file("global_equity_returns.csv", equity_data)
        self.create_test_data_file("global_bond_returns.csv", bond_data)
        self.create_test_data_file("uk_inflation_rates.csv", inflation_data)
        
        result = self.validator.validate_all_data_files()
        
        assert result.is_valid
        assert 'cross_validation' in result.data_summary
        assert result.data_summary['cross_validation']['overlapping_years'] == 21
    
    def test_cross_file_validation_no_overlap(self):
        """Test cross-file validation with no overlapping years."""
        # Create files with non-overlapping years (all in the past)
        equity_data = {'year': list(range(1990, 2001)), 'return': [0.05] * 11}
        bond_data = {'year': list(range(2001, 2012)), 'return': [0.03] * 11}
        inflation_data = {'year': list(range(2012, 2023)), 'inflation_rate': [0.02] * 11}
        
        self.create_test_data_file("global_equity_returns.csv", equity_data)
        self.create_test_data_file("global_bond_returns.csv", bond_data)
        self.create_test_data_file("uk_inflation_rates.csv", inflation_data)
        
        result = self.validator.validate_all_data_files()
        
        assert not result.is_valid
        assert any("No overlapping years" in error for error in result.errors)
    
    def test_handle_missing_years(self):
        """Test handling of missing years through interpolation."""
        # Create data with missing years
        df = pd.DataFrame({
            'year': [2000, 2001, 2003, 2005],  # Missing 2002, 2004
            'return': [0.05, 0.06, 0.08, 0.10]
        })
        
        result_df = self.validator.handle_missing_years(df, 'return')
        
        # Should have all years from 2000 to 2005
        expected_years = list(range(2000, 2006))
        assert list(result_df['year']) == expected_years
        
        # Check interpolated values
        assert result_df[result_df['year'] == 2002]['return'].iloc[0] == 0.07  # Interpolated
        assert result_df[result_df['year'] == 2004]['return'].iloc[0] == 0.09  # Interpolated
    
    def test_generate_data_quality_report(self):
        """Test generation of comprehensive data quality report."""
        # Create valid test data
        years = list(range(2000, 2021))
        equity_data = {'year': years, 'return': [0.05] * 21}
        bond_data = {'year': years, 'return': [0.03] * 21}
        inflation_data = {'year': years, 'inflation_rate': [0.02] * 21}
        
        self.create_test_data_file("global_equity_returns.csv", equity_data)
        self.create_test_data_file("global_bond_returns.csv", bond_data)
        self.create_test_data_file("uk_inflation_rates.csv", inflation_data)
        
        report = self.validator.generate_data_quality_report()
        
        assert "DATA QUALITY REPORT" in report
        assert "OVERALL STATUS: VALID" in report
        assert "INFORMATION:" in report
        assert "DATA SUMMARY:" in report
        assert "RECOMMENDATIONS:" in report
    
    def test_generate_data_quality_report_with_errors(self):
        """Test data quality report generation when there are validation errors."""
        # Create invalid data (missing files)
        report = self.validator.generate_data_quality_report()
        
        assert "DATA QUALITY REPORT" in report
        assert "OVERALL STATUS: INVALID" in report
        assert "ERRORS:" in report
        assert "Required data file missing" in report
    
    def test_outlier_detection(self):
        """Test statistical outlier detection in data validation."""
        # Create data with extreme outliers (more than 3 standard deviations)
        # Base returns around 5% with small variation, then add extreme outliers
        base_returns = [0.05 + (i % 3 - 1) * 0.01 for i in range(18)]  # 4-6% range
        extreme_outliers = [2.0, -0.8, 1.5]  # Very extreme outliers: 200%, -80%, 150%
        returns = base_returns + extreme_outliers
        
        equity_data = {
            'year': list(range(2000, 2021)),
            'return': returns
        }
        self.create_test_data_file("global_equity_returns.csv", equity_data)
        
        # Create inflation data
        inflation_data = {
            'year': list(range(2000, 2021)),
            'inflation_rate': [0.02] * 21
        }
        self.create_test_data_file("uk_inflation_rates.csv", inflation_data)
        
        result = self.validator._validate_equity_returns(
            os.path.join(self.test_dir, "global_equity_returns.csv")
        )
        
        # Should detect outliers but still be valid (outliers are warnings, not errors)
        assert result.is_valid
        assert any("Statistical outliers detected" in warning for warning in result.warnings)
    
    def test_empty_file_validation(self):
        """Test validation of empty data files."""
        # Create empty file
        empty_file = os.path.join(self.test_dir, "global_equity_returns.csv")
        with open(empty_file, 'w') as f:
            f.write("")  # Empty file
        
        result = self.validator._validate_equity_returns(empty_file)
        
        assert not result.is_valid
        assert any("File is empty" in error for error in result.errors)
    
    def test_malformed_csv_validation(self):
        """Test validation of malformed CSV files."""
        # Create malformed CSV
        malformed_file = os.path.join(self.test_dir, "global_equity_returns.csv")
        with open(malformed_file, 'w') as f:
            f.write("year,return\n2000,0.05\n2001,invalid,extra_column\n")
        
        result = self.validator._validate_equity_returns(malformed_file)
        
        assert not result.is_valid
        # Should catch parsing error or data type validation error
        assert len(result.errors) > 0


class TestDataValidatorIntegration:
    """Integration tests for data validator with actual data manager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_complete_test_dataset(self):
        """Create a complete set of valid test data files."""
        years = list(range(1990, 2021))  # 31 years of data
        
        # Create realistic equity returns (higher volatility)
        equity_returns = [0.08 + (i % 7 - 3) * 0.05 for i in range(len(years))]
        equity_data = {'year': years, 'return': equity_returns}
        
        # Create realistic bond returns (lower volatility)
        bond_returns = [0.04 + (i % 3 - 1) * 0.01 for i in range(len(years))]
        bond_data = {'year': years, 'return': bond_returns}
        
        # Create realistic inflation rates
        inflation_rates = [0.025 + (i % 5 - 2) * 0.005 for i in range(len(years))]
        inflation_data = {'year': years, 'inflation_rate': inflation_rates}
        
        # Write files
        for filename, data in [
            ("global_equity_returns.csv", equity_data),
            ("global_bond_returns.csv", bond_data),
            ("uk_inflation_rates.csv", inflation_data)
        ]:
            df = pd.DataFrame(data)
            df.to_csv(os.path.join(self.test_dir, filename), index=False)
    
    def test_integration_with_data_manager(self):
        """Test integration between validator and data manager."""
        from src.data_manager import HistoricalDataManager
        
        self.create_complete_test_dataset()
        
        # Create data manager with test directory
        data_manager = HistoricalDataManager(self.test_dir)
        
        # Should load successfully with validation
        data_manager.load_all_data(validate_quality=True)
        
        # Verify data was loaded
        assert data_manager.equity_returns is not None
        assert data_manager.bond_returns is not None
        assert data_manager.inflation_rates is not None
        
        # Test quality report generation
        report = data_manager.get_data_quality_report()
        assert "DATA QUALITY REPORT" in report
        assert "OVERALL STATUS: VALID" in report
    
    def test_integration_validation_failure(self):
        """Test integration when validation fails."""
        from src.data_manager import HistoricalDataManager
        
        # Create invalid data (insufficient years)
        years = list(range(2020, 2025))  # Only 5 years
        equity_data = {'year': years, 'return': [0.05] * 5}
        bond_data = {'year': years, 'return': [0.03] * 5}
        inflation_data = {'year': years, 'inflation_rate': [0.02] * 5}
        
        for filename, data in [
            ("global_equity_returns.csv", equity_data),
            ("global_bond_returns.csv", bond_data),
            ("uk_inflation_rates.csv", inflation_data)
        ]:
            df = pd.DataFrame(data)
            df.to_csv(os.path.join(self.test_dir, filename), index=False)
        
        data_manager = HistoricalDataManager(self.test_dir)
        
        # Should raise ValueError due to validation failure
        with pytest.raises(ValueError) as exc_info:
            data_manager.load_all_data(validate_quality=True)
        
        assert "Data validation failed" in str(exc_info.value)
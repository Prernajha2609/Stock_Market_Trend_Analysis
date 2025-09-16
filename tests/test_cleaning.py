"""
Unit tests for data cleaning functions.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_cleaner import clean_stock_data, engineer_features

class TestDataCleaning:
    """Test cases for data cleaning functions."""
    
    def test_clean_stock_data_duplicates(self):
        """Test removing duplicate records."""
        # Create data with duplicates
        data = {
            'symbol': ['AAPL', 'AAPL', 'AAPL', 'AAPL'],
            'date': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02'],
            'open': [100.0, 100.5, 101.0, 101.5],
            'high': [105.0, 105.5, 106.0, 106.5],
            'low': [95.0, 95.5, 96.0, 96.5],
            'close': [103.0, 103.5, 104.0, 104.5],
            'volume': [1000000, 1100000, 1200000, 1300000]
        }
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        cleaned_df = clean_stock_data(df)
        
        assert isinstance(cleaned_df, pd.DataFrame)
        assert len(cleaned_df) < len(df)  # Should remove duplicates
        assert cleaned_df['date'].nunique() == 2  # Should have 2 unique dates
    
    def test_clean_stock_data_missing_values(self):
        """Test handling missing values."""
        data = {
            'symbol': ['AAPL', 'AAPL', 'AAPL'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'open': [100.0, np.nan, 102.0],
            'high': [105.0, 106.0, np.nan],
            'low': [95.0, 96.0, 97.0],
            'close': [103.0, 104.0, 105.0],
            'volume': [1000000, np.nan, 1200000]
        }
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        cleaned_df = clean_stock_data(df)
        
        assert isinstance(cleaned_df, pd.DataFrame)
        # Should handle missing values appropriately
    
    def test_clean_stock_data_invalid_prices(self):
        """Test removing invalid prices."""
        data = {
            'symbol': ['AAPL', 'AAPL', 'AAPL', 'AAPL'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
            'open': [100.0, -50.0, 0.0, 102.0],  # Invalid prices
            'high': [105.0, 106.0, 107.0, 108.0],
            'low': [95.0, 96.0, 97.0, 98.0],
            'close': [103.0, 104.0, 105.0, 106.0],
            'volume': [1000000, 1100000, 1200000, 1300000]
        }
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        cleaned_df = clean_stock_data(df)
        
        assert isinstance(cleaned_df, pd.DataFrame)
        assert len(cleaned_df) < len(df)  # Should remove invalid prices
        assert (cleaned_df['open'] > 0).all()  # All prices should be positive
    
    def test_clean_stock_data_price_logic(self):
        """Test price logic validation."""
        data = {
            'symbol': ['AAPL', 'AAPL', 'AAPL'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'open': [100.0, 101.0, 102.0],
            'high': [95.0, 96.0, 97.0],  # High < Low
            'low': [105.0, 106.0, 107.0],  # Low > High
            'close': [103.0, 104.0, 105.0],
            'volume': [1000000, 1100000, 1200000]
        }
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        cleaned_df = clean_stock_data(df)
        
        assert isinstance(cleaned_df, pd.DataFrame)
        # Should remove rows where high < low
        if not cleaned_df.empty:
            assert (cleaned_df['high'] >= cleaned_df['low']).all()

class TestFeatureEngineering:
    """Test cases for feature engineering functions."""
    
    def test_engineer_features_moving_averages(self):
        """Test moving average calculation."""
        # Create sample data
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        prices = np.random.randn(30).cumsum() + 100
        
        df = pd.DataFrame({
            'symbol': ['AAPL'] * 30,
            'date': dates,
            'open': prices + np.random.randn(30),
            'high': prices + np.abs(np.random.randn(30)),
            'low': prices - np.abs(np.random.randn(30)),
            'close': prices,
            'volume': np.random.randint(1000000, 5000000, 30)
        })
        
        # Clean data first
        cleaned_df = clean_stock_data(df)
        
        if not cleaned_df.empty:
            engineered_df = engineer_features(cleaned_df)
            
            assert isinstance(engineered_df, pd.DataFrame)
            assert 'ma_5' in engineered_df.columns
            assert 'ma_10' in engineered_df.columns
            assert 'ma_20' in engineered_df.columns
            assert 'daily_return' in engineered_df.columns
            
            # Check that moving averages are calculated
            assert engineered_df['ma_5'].isna().all() is False
            assert engineered_df['ma_10'].isna().all() is False
            assert engineered_df['ma_20'].isna().all() is False
    
    def test_engineer_features_daily_returns(self):
        """Test daily return calculation."""
        # Create sample data with known price changes
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        prices = [100, 102, 98, 105, 103, 107, 110, 108, 112, 115]
        
        df = pd.DataFrame({
            'symbol': ['AAPL'] * 10,
            'date': dates,
            'open': prices,
            'high': [p + 2 for p in prices],
            'low': [p - 2 for p in prices],
            'close': prices,
            'volume': [1000000] * 10
        })
        
        cleaned_df = clean_stock_data(df)
        engineered_df = engineer_features(cleaned_df)
        
        assert 'daily_return' in engineered_df.columns
        
        # Check that daily returns are calculated correctly
        expected_returns = [np.nan, 2.0, -3.92, 7.14, -1.90, 3.88, 2.80, -1.82, 3.70, 2.68]
        calculated_returns = engineered_df['daily_return'].values
        
        # Compare non-NaN values
        for i in range(1, len(expected_returns)):
            if not np.isnan(expected_returns[i]):
                assert abs(calculated_returns[i] - expected_returns[i]) < 0.1
    
    def test_engineer_features_additional_features(self):
        """Test additional feature engineering."""
        # Create sample data
        dates = pd.date_range('2024-01-01', periods=20, freq='D')
        prices = np.random.randn(20).cumsum() + 100
        
        df = pd.DataFrame({
            'symbol': ['AAPL'] * 20,
            'date': dates,
            'open': prices + np.random.randn(20),
            'high': prices + np.abs(np.random.randn(20)),
            'low': prices - np.abs(np.random.randn(20)),
            'close': prices,
            'volume': np.random.randint(1000000, 5000000, 20)
        })
        
        cleaned_df = clean_stock_data(df)
        engineered_df = engineer_features(cleaned_df)
        
        # Check for additional features
        additional_features = ['price_range', 'price_range_pct', 'volume_ma_5', 
                            'volatility_5', 'volatility_10', 'rsi']
        
        for feature in additional_features:
            if feature in engineered_df.columns:
                assert not engineered_df[feature].isna().all()

if __name__ == "__main__":
    pytest.main([__file__]) 
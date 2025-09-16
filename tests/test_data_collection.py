# """
# Unit tests for data collection functions.
# """
import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.stock_data_collector import download_stock_data
from data.data_cleaner import clean_stock_data
from data.news_data_collector import fetch_news_headlines, clean_headline

class TestStockDataCollection:
    """Test cases for stock data collection."""
    
    def test_download_stock_data(self):
        """Test downloading stock data."""
        # Test with a valid symbol
        df = download_stock_data('AAPL', '2024-01-01', '2024-01-31')
        
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert 'symbol' in df.columns
            assert 'date' in df.columns
            assert 'open' in df.columns
            assert 'high' in df.columns
            assert 'low' in df.columns
            assert 'close' in df.columns
            assert 'volume' in df.columns
            assert df['symbol'].iloc[0] == 'AAPL'
    
    def test_download_stock_data_invalid_symbol(self):
        """Test downloading data for invalid symbol."""
        df = download_stock_data('INVALID_SYMBOL_123', '2024-01-01', '2024-01-31')
        assert isinstance(df, pd.DataFrame)
        # Should return empty DataFrame for invalid symbol
    
    def test_clean_stock_data(self):
        """Test cleaning stock data."""
        # Create sample data
        data = {
            'symbol': ['AAPL', 'AAPL', 'AAPL'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-02'],  # Duplicate date
            'open': [100.0, 101.0, 102.0],
            'high': [105.0, 106.0, 107.0],
            'low': [95.0, 96.0, 97.0],
            'close': [103.0, 104.0, 105.0],
            'volume': [1000000, 1100000, 1200000]
        }
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        cleaned_df = clean_stock_data(df)
        
        assert isinstance(cleaned_df, pd.DataFrame)
        assert len(cleaned_df) <= len(df)  # Should remove duplicates
        assert (cleaned_df['high'] >= cleaned_df['low']).all()  # High >= Low

class TestNewsDataCollection:
    """Test cases for news data collection."""
    
    def test_fetch_news_headlines(self):
        """Test fetching news headlines."""
        df = fetch_news_headlines('AAPL', max_articles=5)
        
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert 'symbol' in df.columns
            assert 'date' in df.columns
            assert 'headline' in df.columns
            assert 'link' in df.columns
            assert 'source' in df.columns
            assert df['symbol'].iloc[0] == 'AAPL'
    
    def test_clean_headline(self):
        """Test headline cleaning function."""
        # Test normal headline
        headline = "Apple Stock Rises 5% Today"
        cleaned = clean_headline(headline)
        assert cleaned == "Apple Stock Rises 5% Today"
        
        # Test headline with extra whitespace
        headline = "  Apple   Stock   Rises  5%  Today  "
        cleaned = clean_headline(headline)
        assert cleaned == "Apple Stock Rises 5% Today"
        
        # Test long headline
        long_headline = "A" * 600
        cleaned = clean_headline(long_headline)
        assert len(cleaned) <= 500
        assert cleaned.endswith("...")
        
        # Test headline with special characters
        headline = "Apple@#$%^&*()Stock!@#$%^&*()Rises"
        cleaned = clean_headline(headline)
        assert "Apple" in cleaned
        assert "Stock" in cleaned
        assert "Rises" in cleaned

if __name__ == "__main__":
    pytest.main([__file__])

"""
Unit tests for model functions.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.sentiment_analyzer import analyze_sentiment, batch_sentiment_analysis
from models.arima_forecaster import check_stationarity
from models.random_forest_predictor import create_target_variable, prepare_features

class TestSentimentAnalysis:
    """Test cases for sentiment analysis."""
    
    def test_analyze_sentiment_positive(self):
        """Test sentiment analysis for positive text."""
        score = analyze_sentiment("Apple stock rises 10% today, great news!")
        assert isinstance(score, float)
        assert -1 <= score <= 1
        assert score > 0  # Should be positive
    
    def test_analyze_sentiment_negative(self):
        """Test sentiment analysis for negative text."""
        score = analyze_sentiment("Apple stock crashes 20%, terrible news!")
        assert isinstance(score, float)
        assert -1 <= score <= 1
        assert score < 0  # Should be negative
    
    def test_analyze_sentiment_neutral(self):
        """Test sentiment analysis for neutral text."""
        score = analyze_sentiment("Apple stock remains unchanged today.")
        assert isinstance(score, float)
        assert -1 <= score <= 1
    
    def test_batch_sentiment_analysis(self):
        """Test batch sentiment analysis."""
        headlines = [
            "Apple stock rises 5%",
            "Apple stock falls 3%",
            "Apple stock unchanged"
        ]
        
        df = pd.DataFrame({
            'headline': headlines,
            'symbol': ['AAPL'] * 3,
            'date': [datetime.now().date()] * 3
        })
        
        result_df = batch_sentiment_analysis(df)
        
        assert isinstance(result_df, pd.DataFrame)
        assert 'sentiment_score' in result_df.columns
        assert len(result_df) == len(headlines)
        assert all(isinstance(score, float) for score in result_df['sentiment_score'])

class TestARIMAModel:
    """Test cases for ARIMA model."""
    
    def test_check_stationarity_stationary(self):
        """Test stationarity check for stationary series."""
        # Create a stationary time series (random walk)
        np.random.seed(42)
        stationary_series = pd.Series(np.random.randn(100).cumsum())
        
        is_stationary = check_stationarity(stationary_series)
        assert isinstance(is_stationary, bool)
    
    def test_check_stationarity_trend(self):
        """Test stationarity check for trending series."""
        # Create a trending time series
        trend_series = pd.Series(np.arange(100) + np.random.randn(100))
        
        is_stationary = check_stationarity(trend_series)
        assert isinstance(is_stationary, bool)

class TestRandomForestModel:
    """Test cases for Random Forest model."""
    
    def test_create_target_variable(self):
        """Test target variable creation."""
        # Create sample stock data
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        prices = np.random.randn(100).cumsum() + 100
        
        df = pd.DataFrame({
            'date': dates,
            'close': prices,
            'open': prices + np.random.randn(100),
            'high': prices + np.abs(np.random.randn(100)),
            'low': prices - np.abs(np.random.randn(100)),
            'volume': np.random.randint(1000000, 5000000, 100)
        })
        
        result_df = create_target_variable(df, days_ahead=30)
        
        assert isinstance(result_df, pd.DataFrame)
        assert 'target' in result_df.columns
        assert 'future_price' in result_df.columns
        assert 'price_change_pct' in result_df.columns
        assert all(target in [0, 1] for target in result_df['target'].dropna())
    
    def test_prepare_features(self):
        """Test feature preparation."""
        # Create sample data with features
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        prices = np.random.randn(50).cumsum() + 100
        
        df = pd.DataFrame({
            'date': dates,
            'close': prices,
            'open': prices + np.random.randn(50),
            'high': prices + np.abs(np.random.randn(50)),
            'low': prices - np.abs(np.random.randn(50)),
            'volume': np.random.randint(1000000, 5000000, 50),
            'ma_5': pd.Series(prices).rolling(5).mean(),
            'ma_10': pd.Series(prices).rolling(10).mean(),
            'daily_return': pd.Series(prices).pct_change() * 100,
            'target': np.random.randint(0, 2, 50)
        })
        
        # Remove NaN values
        df = df.dropna()
        
        X, y, feature_names = prepare_features(df)
        
        assert isinstance(X, np.ndarray)
        assert isinstance(y, np.ndarray)
        assert isinstance(feature_names, list)
        assert X.shape[0] == y.shape[0]
        assert X.shape[1] == len(feature_names)
        assert not np.isnan(X).any()
        assert not np.isnan(y).any()

if __name__ == "__main__":
    pytest.main([__file__]) 
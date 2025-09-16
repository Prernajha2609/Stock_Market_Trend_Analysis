"""
ARIMA model for stock price forecasting.
Trains an ARIMA model on historical closing prices and forecasts future prices.
"""
import argparse
import logging
import sys
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import warnings
warnings.filterwarnings('ignore')
# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import create_tables, read_dataframe, insert_dataframe, execute_query
from config import DEFAULT_SYMBOL, ARIMA_ORDER, FORECAST_DAYS, TOP_50_TICKERS
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def load_cleaned_data(symbol):
    """
    Load cleaned stock data from database.
    Args:
        symbol (str): Stock symbol
    Returns:
        pd.DataFrame: Cleaned stock data with closing prices
    """
    try:
        logger.info(f"Loading cleaned data for {symbol}")
        query = """
        SELECT date, close 
        FROM stocks_clean 
        WHERE symbol = %(symbol)s 
        ORDER BY date
        """
        df = read_dataframe(query, {'symbol': symbol})
        if df.empty:
            logger.warning(f"No cleaned data found for {symbol}")
            return pd.DataFrame()
        # Set date as index
        df = df.set_index('date')
        logger.info(f"Loaded {len(df)} records for {symbol}")
        return df
    except Exception as e:
        logger.error(f"Error loading cleaned data for {symbol}: {e}")
        raise

def check_stationarity(timeseries):
    """
    Check if time series is stationary using Augmented Dickey-Fuller test.
    Args:
        timeseries (pd.Series): Time series data
    Returns:
        bool: True if stationary, False otherwise
    """
    try:
        result = adfuller(timeseries.dropna())
        # Extract test statistic and p-value
        test_statistic = result[0]
        p_value = result[1]
        logger.info(f"ADF Test Statistic: {test_statistic:.4f}")
        logger.info(f"P-value: {p_value:.4f}")
        # If p-value < 0.05, series is stationary
        is_stationary = p_value < 0.05
        if is_stationary:
            logger.info("Time series is stationary")
        else:
            logger.info("Time series is not stationary")     
        return is_stationary       
    except Exception as e:
        logger.error(f"Error checking stationarity: {e}")
        return False

def find_optimal_arima_order(timeseries, max_p=3, max_d=2, max_q=3):
    """
    Find optimal ARIMA parameters using grid search.  
    Args:
        timeseries (pd.Series): Time series data
        max_p (int): Maximum p parameter
        max_d (int): Maximum d parameter
        max_q (int): Maximum q parameter 
    Returns:
        tuple: Optimal (p, d, q) parameters
    """
    try:
        logger.info("Finding optimal ARIMA parameters")       
        best_aic = np.inf
        best_order = None       
        # Grid search for optimal parameters
        for p in range(0, max_p + 1):
            for d in range(0, max_d + 1):
                for q in range(0, max_q + 1):
                    try:
                        model = ARIMA(timeseries, order=(p, d, q))
                        fitted_model = model.fit()                       
                        if fitted_model.aic < best_aic:
                            best_aic = fitted_model.aic
                            best_order = (p, d, q)
                    except:
                        continue
        if best_order is None:
            logger.warning("Could not find optimal parameters, using default")
            return ARIMA_ORDER
        logger.info(f"Optimal ARIMA order: {best_order} (AIC: {best_aic:.2f})")
        return best_order
    except Exception as e:
        logger.error(f"Error finding optimal ARIMA order: {e}")
        return ARIMA_ORDER
def train_arima_model(timeseries, order):
    """
    Train ARIMA model on time series data.
    Args:
        timeseries (pd.Series): Time series data
        order (tuple): ARIMA order (p, d, q)
    Returns:
        ARIMAResults: Fitted ARIMA model
    """
    try:
        logger.info(f"Training ARIMA model with order {order}")
        # Fit ARIMA model
        model = ARIMA(timeseries, order=order)
        fitted_model = model.fit()
        logger.info(f"Model AIC: {fitted_model.aic:.2f}")
        logger.info(f"Model BIC: {fitted_model.bic:.2f}")
        return fitted_model
    except Exception as e:
        logger.error(f"Error training ARIMA model: {e}")
        raise
def forecast_prices(model, steps):
    """
    Generate price forecasts using fitted ARIMA model.
    Args:
        model: Fitted ARIMA model
        steps (int): Number of steps to forecast
    Returns:
        tuple: (forecast_values, confidence_intervals)
    """
    try:
        logger.info(f"Generating {steps}-day forecast")
        # Generate forecast
        forecast = model.forecast(steps=steps)
        # Get confidence intervals
        forecast_ci = model.get_forecast(steps=steps).conf_int()
        return forecast, forecast_ci
    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        raise
def plot_forecast(actual, forecast, confidence_intervals, symbol):
    """
    Plot actual vs predicted values.
    Args:
        actual (pd.Series): Actual closing prices
        forecast (pd.Series): Forecasted prices
        confidence_intervals (pd.DataFrame): Confidence intervals
        symbol (str): Stock symbol
    """
    try:
        plt.figure(figsize=(12, 6))
        # Plot actual values
        plt.plot(actual.index, actual.values, label='Actual', color='blue')
        # Plot forecast
        forecast_dates = pd.date_range(start=actual.index[-1] + timedelta(days=1), 
                                     periods=len(forecast), freq='D')
        plt.plot(forecast_dates, forecast.values, label='Forecast', color='red')
        # Plot confidence intervals
        if confidence_intervals is not None:
            plt.fill_between(forecast_dates, 
                           confidence_intervals.iloc[:, 0], 
                           confidence_intervals.iloc[:, 1], 
                           alpha=0.3, color='red', label='Confidence Interval')
        plt.title(f'ARIMA Forecast for {symbol}')
        plt.xlabel('Date')
        plt.ylabel('Price ($)')
        plt.legend()
        plt.grid(True)
        # Save plot
        plot_filename = f'arima_forecast_{symbol.lower()}.png'
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Forecast plot saved as {plot_filename}")
    except Exception as e:
        logger.error(f"Error plotting forecast: {e}")
def save_predictions(forecast, confidence_intervals, symbol):
    """
    Save forecast predictions to database.
    Args:
        forecast (pd.Series): Forecasted prices
        confidence_intervals (pd.DataFrame): Confidence intervals
        symbol (str): Stock symbol
    """
    try:
        # Create forecast dates
        forecast_dates = pd.date_range(start=datetime.now().date() + timedelta(days=1), 
                                     periods=len(forecast), freq='D')
        # Prepare data for database
        predictions_data = []
        for i, (date, price) in enumerate(zip(forecast_dates, forecast)):
            prediction = {
                'symbol': symbol,
                'date': date.date(),
                'predicted_price': float(price),
                'confidence_lower': float(confidence_intervals.iloc[i, 0]) if confidence_intervals is not None else None,
                'confidence_upper': float(confidence_intervals.iloc[i, 1]) if confidence_intervals is not None else None,
                'model_type': 'ARIMA'}
            predictions_data.append(prediction)
        # Convert to DataFrame
        df = pd.DataFrame(predictions_data)
        # Save to database
        insert_dataframe(df, 'predictions')
        logger.info(f"Saved {len(df)} predictions for {symbol}")
    except Exception as e:
        logger.error(f"Error saving predictions: {e}")
        raise
def main():
    """Main function to train ARIMA model and generate forecasts."""
    parser = argparse.ArgumentParser(description='Train ARIMA model and forecast stock prices')
    parser.add_argument('--symbol', type=str, default=DEFAULT_SYMBOL,
                       help=f'Stock symbol (default: {DEFAULT_SYMBOL})')
    parser.add_argument('--forecast_days', type=int, default=FORECAST_DAYS,
                       help=f'Number of days to forecast (default: {FORECAST_DAYS})')
    parser.add_argument('--auto_order', action='store_true',
                       help='Automatically find optimal ARIMA order')
    parser.add_argument('--all', action='store_true',
                       help='Train ARIMA model for all tickers in TOP_50_TICKERS')
    parser.add_argument('--symbols', type=str, default=None,
                       help='Comma-separated list of stock symbols to process')
    args = parser.parse_args()
    if args.all:
        tickers = TOP_50_TICKERS
    elif args.symbols:
        tickers = [s.strip().upper() for s in args.symbols.split(',') if s.strip()]
    else:
        tickers = [args.symbol.upper()]
    try:
        # Create database tables if they don't exist
        create_tables()
        for symbol in tickers:
            # Load cleaned data
            df = load_cleaned_data(symbol)
            if df.empty:
                logger.error(f"No data available for {symbol}")
                continue
            # Get closing prices
            closing_prices = df['close']
            # Check stationarity
            is_stationary = check_stationarity(closing_prices)
            # Determine ARIMA order
            if args.auto_order:
                order = find_optimal_arima_order(closing_prices)
            else:
                order = ARIMA_ORDER
            # Train ARIMA model
            model = train_arima_model(closing_prices, order)
            # Generate forecast
            forecast, confidence_intervals = forecast_prices(model, args.forecast_days)
            # Plot results
            plot_forecast(closing_prices, forecast, confidence_intervals, symbol)
            # Save predictions
            save_predictions(forecast, confidence_intervals, symbol)
            logger.info(f"ARIMA forecasting completed for {symbol}")
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main() 
"""
Data cleaning and feature engineering for stock data.
Loads historical stock data from PostgreSQL, cleans it, and engineers additional features.
"""
import argparse
import logging
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import create_tables, read_dataframe, insert_dataframe, execute_query
from config import DEFAULT_SYMBOL, MOVING_AVERAGE_PERIODS, TOP_50_TICKERS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_stock_data(symbol, start_date=None, end_date=None):
    """
    Load historical stock data from PostgreSQL database.
    
    Args:
        symbol (str): Stock symbol
        start_date (str): Start date in YYYY-MM-DD format (optional)
        end_date (str): End date in YYYY-MM-DD format (optional)
    
    Returns:
        pd.DataFrame: Historical stock data
    """
    try:
        logger.info(f"Loading stock data for {symbol}")
        
        # Build query
        query = "SELECT * FROM stocks WHERE symbol = %(symbol)s ORDER BY date"
        params = {'symbol': symbol}
        
        if start_date:
            query += " AND date >= :start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += " AND date <= :end_date"
            params['end_date'] = end_date
        
        # Load data
        df = read_dataframe(query, params)
        
        if df.empty:
            logger.warning(f"No data found for {symbol}")
            return pd.DataFrame()
        
        logger.info(f"Successfully loaded {len(df)} records for {symbol}")
        return df
        
    except Exception as e:
        logger.error(f"Error loading stock data for {symbol}: {e}")
        raise

def clean_stock_data(df):
    """
    Clean stock data by removing duplicates and handling missing values.
    
    Args:
        df (pd.DataFrame): Raw stock data
    
    Returns:
        pd.DataFrame: Cleaned stock data
    """
    try:
        logger.info("Cleaning stock data")
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['symbol', 'date'])
        logger.info(f"Removed {initial_count - len(df)} duplicate records")
        
        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)
        
        # Handle missing values
        missing_counts = df.isnull().sum()
        if missing_counts.sum() > 0:
            logger.warning(f"Found missing values: {missing_counts.to_dict()}")
            
            # Forward fill for OHLC prices
            price_columns = ['open', 'high', 'low', 'close']
            df[price_columns] = df[price_columns].fillna(method='ffill')
            
            # Fill volume with 0 if missing
            df['volume'] = df['volume'].fillna(0)
        
        # Remove rows with invalid prices (negative or zero)
        invalid_prices = (df[['open', 'high', 'low', 'close']] <= 0).any(axis=1)
        if invalid_prices.sum() > 0:
            logger.warning(f"Removing {invalid_prices.sum()} rows with invalid prices")
            df = df[~invalid_prices]
        
        # Ensure high >= low and high >= open, high >= close
        df = df[
            (df['high'] >= df['low']) &
            (df['high'] >= df['open']) &
            (df['high'] >= df['close'])
        ]
        
        logger.info(f"Cleaned data: {len(df)} records remaining")
        return df
        
    except Exception as e:
        logger.error(f"Error cleaning stock data: {e}")
        raise

def engineer_features(df):
    """
    Engineer additional features for stock data.
    
    Args:
        df (pd.DataFrame): Cleaned stock data
    
    Returns:
        pd.DataFrame: Stock data with engineered features
    """
    try:
        logger.info("Engineering features")
        
        # Calculate moving averages
        for period in MOVING_AVERAGE_PERIODS:
            df[f'ma_{period}'] = df['close'].rolling(window=period).mean()
            logger.info(f"Added {period}-day moving average")
        
        # Calculate daily returns
        df['daily_return'] = df['close'].pct_change() * 100
        logger.info("Added daily return percentage")
        
        # Calculate price ranges
        df['price_range'] = df['high'] - df['low']
        df['price_range_pct'] = (df['price_range'] / df['close']) * 100
        
        # Calculate volume moving average
        df['volume_ma_5'] = df['volume'].rolling(window=5).mean()
        
        # Calculate volatility (rolling standard deviation of returns)
        df['volatility_5'] = df['daily_return'].rolling(window=5).std()
        df['volatility_10'] = df['daily_return'].rolling(window=10).std()
        
        # Calculate RSI (Relative Strength Index)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        logger.info("Feature engineering completed")
        return df
        
    except Exception as e:
        logger.error(f"Error engineering features: {e}")
        raise

def save_cleaned_data(df, symbol):
    """
    Save cleaned and feature-engineered data to database.
    
    Args:
        df (pd.DataFrame): Cleaned stock data with features
        symbol (str): Stock symbol
    """
    try:
        if not df.empty:
            # Remove any remaining NaN values
            df = df.dropna()
            
            # Select columns for database
            columns_to_save = [
                'symbol', 'date', 'open', 'high', 'low', 'close', 'volume',
                'ma_5', 'ma_10', 'ma_20', 'daily_return'
            ]
            
            # Only include columns that exist
            available_columns = [col for col in columns_to_save if col in df.columns]
            df_to_save = df[available_columns].copy()
            
            # Remove duplicates
            df_to_save = df_to_save.drop_duplicates(subset=['symbol', 'date'])
            
            # Insert data into database
            insert_dataframe(df_to_save, 'stocks_clean')
            
            logger.info(f"Successfully saved {len(df_to_save)} cleaned records for {symbol}")
        else:
            logger.warning(f"No cleaned data to save for {symbol}")
            
    except Exception as e:
        logger.error(f"Error saving cleaned data to database: {e}")
        raise

def check_existing_cleaned_data(symbol):
    """
    Check if cleaned data already exists in database for the given symbol.
    
    Args:
        symbol (str): Stock symbol
    
    Returns:
        bool: True if cleaned data exists, False otherwise
    """
    try:
        query = """
        SELECT COUNT(*) FROM stocks_clean 
        WHERE symbol = %(symbol)s
        """
        
        result = execute_query(query, {'symbol': symbol})
        count = result.scalar()
        return (count is not None) and (count > 0)
        
    except Exception as e:
        logger.error(f"Error checking existing cleaned data: {e}")
        return False

def main():
    """Main function to clean and engineer stock data."""
    parser = argparse.ArgumentParser(description='Clean and engineer stock data features')
    parser.add_argument('--symbol', type=str, default=DEFAULT_SYMBOL,
                       help=f'Stock symbol (default: {DEFAULT_SYMBOL})')
    parser.add_argument('--start_date', type=str, default=None,
                       help='Start date in YYYY-MM-DD format (optional)')
    parser.add_argument('--end_date', type=str, default=None,
                       help='End date in YYYY-MM-DD format (optional)')
    parser.add_argument('--force', action='store_true',
                       help='Force processing even if cleaned data already exists')
    parser.add_argument('--all', action='store_true',
                       help='Clean and engineer data for all tickers in TOP_50_TICKERS')
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
            # Check if cleaned data already exists
            if not args.force and check_existing_cleaned_data(symbol):
                logger.info(f"Cleaned data for {symbol} already exists in database")
                logger.info("Use --force flag to re-process data")
                continue

            # Load stock data
            df = load_stock_data(symbol, args.start_date, args.end_date)

            if df.empty:
                logger.error(f"No data found for {symbol}")
                continue

            # Clean data
            df_clean = clean_stock_data(df)

            if df_clean.empty:
                logger.error(f"No data remaining after cleaning for {symbol}")
                continue

            # Engineer features
            df_feat = engineer_features(df_clean)

            # Save cleaned data
            save_cleaned_data(df_feat, symbol)

            logger.info(f"Data cleaning and feature engineering completed for {symbol}")

    except Exception as e:
        logger.error(f"Error in main function: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
"""
Stock data collector using yfinance library.
Downloads historical stock price data and saves to PostgreSQL database.
"""
import argparse
import logging
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import create_tables, insert_dataframe, execute_query
from config import DEFAULT_START_DATE, DEFAULT_END_DATE, DEFAULT_SYMBOL, TOP_50_TICKERS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_dates(start_date, end_date):
    """
    Validate that the requested dates are valid and not in the future.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Parse dates
        start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        today = datetime.now().date()
        
        # Check if dates are in the future
        if start_dt > today:
            return False, f"❌ Start date {start_date} is in the future. Stock data is only available for past dates."
        
        if end_dt > today:
            return False, f"❌ End date {end_date} is in the future. Stock data is only available for past dates."
        
        # Check if start date is after end date
        if start_dt > end_dt:
            return False, f"❌ Start date {start_date} is after end date {end_date}."
        
        # Allow today's date for real-time data
        if end_dt == today:
            logger.info(f"📊 Fetching real-time data up to today ({today})")
        else:
            logger.info(f"📊 Fetching historical data from {start_date} to {end_date}")
        
        return True, ""
        
    except ValueError as e:
        return False, f"❌ Invalid date format. Please use YYYY-MM-DD format (e.g., 2024-01-01). Error: {e}"

def download_stock_data(symbol, start_date, end_date):
    """
    Download historical stock data using yfinance.
    
    Args:
        symbol (str): Stock symbol (e.g., 'AAPL')
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
    
    Returns:
        pd.DataFrame: Historical stock data with columns: Date, Open, High, Low, Close, Volume
    """
    try:
        # Validate dates first
        is_valid, error_message = validate_dates(start_date, end_date)
        if not is_valid:
            logger.error(error_message)
            return pd.DataFrame()
        
        logger.info(f"Downloading stock data for {symbol} from {start_date} to {end_date}")
        
        # Download data using yfinance
        ticker = yf.Ticker(symbol)
        
        # Try different approaches to get data
        data = ticker.history(start=start_date, end=end_date)
        
        if data.empty:
            # Try with a broader date range to see if the symbol is valid
            logger.info(f"⚠️  No data found for {symbol} in specified range. Trying broader range...")
            broader_data = ticker.history(period="1y")
            
            if broader_data.empty:
                logger.error(f"❌ No data found for {symbol}. Symbol may be invalid or delisted.")
                return pd.DataFrame()
            else:
                logger.warning(f"⚠️  Symbol {symbol} exists but no data for {start_date} to {end_date}")
                try:
                    min_date = broader_data.index.min()
                    max_date = broader_data.index.max()
                    min_str = str(min_date).split()[0]
                    max_str = str(max_date).split()[0]
                    logger.info(f"💡 Available data range: {min_str} to {max_str}")
                    logger.info(f"💡 Try using: --start_date {min_str} --end_date {max_str}")
                except:
                    logger.info("💡 Data range not available")
                return pd.DataFrame()
        
        # Reset index to make Date a column
        data = data.reset_index()
        
        # Rename columns to match database schema
        data = data.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Add symbol column
        data['symbol'] = symbol
        
        # Reorder columns to match database schema
        data = data[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']]
        
        logger.info(f"✅ Successfully downloaded {len(data)} records for {symbol}")
        return data
        
    except Exception as e:
        logger.error(f"Error downloading data for {symbol}: {e}")
        raise

def save_to_database(df, symbol):
    """
    Save stock data to PostgreSQL database.
    
    Args:
        df (pd.DataFrame): Stock data to save
        symbol (str): Stock symbol
    """
    try:
        # Check if data already exists for this symbol and date range
        if not df.empty:
            # Remove duplicates based on symbol and date
            df = df.drop_duplicates(subset=['symbol', 'date'])
            
            # Insert data into database
            insert_dataframe(df, 'stocks')
            
            logger.info(f"Successfully saved {len(df)} records for {symbol} to database")
        else:
            logger.warning(f"No data to save for {symbol}")
            
    except Exception as e:
        logger.error(f"Error saving data to database: {e}")
        raise

def check_existing_data(symbol, start_date, end_date):
    """
    Check if data already exists in database for the given symbol and date range.
    
    Args:
        symbol (str): Stock symbol
        start_date (str): Start date
        end_date (str): End date
    
    Returns:
        bool: True if data exists, False otherwise
    """
    try:
        query = """
        SELECT COUNT(*) FROM stocks 
        WHERE symbol = :symbol
        AND date BETWEEN :start_date AND :end_date
        """
        
        result = execute_query(query, {
            'symbol': symbol,
            'start_date': start_date,
            'end_date': end_date
        })
        
        count = result.scalar()
        return (count is not None) and (count > 0)
        
    except Exception as e:
        logger.error(f"Error checking existing data: {e}")
        return False

def main():
    """Main function to collect stock data."""
    parser = argparse.ArgumentParser(description='Download stock data using yfinance')
    parser.add_argument('--symbol', type=str, default=DEFAULT_SYMBOL,
                       help=f'Stock symbol (default: {DEFAULT_SYMBOL})')
    parser.add_argument('--start_date', type=str, default=DEFAULT_START_DATE,
                       help=f'Start date in YYYY-MM-DD format (default: {DEFAULT_START_DATE})')
    parser.add_argument('--end_date', type=str, default=DEFAULT_END_DATE,
                       help=f'End date in YYYY-MM-DD format (default: {DEFAULT_END_DATE})')
    parser.add_argument('--force', action='store_true',
                       help='Force download even if data already exists')
    parser.add_argument('--all', action='store_true',
                       help='Download data for all tickers in TOP_50_TICKERS')
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
            # Check if data already exists
            if not args.force and check_existing_data(symbol, args.start_date, args.end_date):
                logger.info(f"Data for {symbol} from {args.start_date} to {args.end_date} already exists in database")
                logger.info("Use --force flag to re-download data")
                continue

            # Download stock data
            df = download_stock_data(symbol, args.start_date, args.end_date)

            if not df.empty:
                # Save to database
                save_to_database(df, symbol)
                logger.info(f"✅ Stock data collection completed for {symbol}")
            else:
                logger.error(f"❌ Failed to download data for {symbol}")
                # Provide helpful suggestions
                today = datetime.now().date()
                suggested_start = (today - timedelta(days=30)).strftime('%Y-%m-%d')
                suggested_end = today.strftime('%Y-%m-%d')
                logger.info(f"💡 Try using recent dates: --start_date {suggested_start} --end_date {suggested_end}")

    except Exception as e:
        logger.error(f"Error in main function: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
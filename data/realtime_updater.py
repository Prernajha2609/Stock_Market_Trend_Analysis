"""
Real-time stock data updater.
Automatically fetches and updates the latest stock data in the database.
"""
import argparse
import logging
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import time

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import create_tables, insert_dataframe, execute_query
from config import TOP_50_TICKERS, UPDATE_FREQUENCY_HOURS, MAX_DAYS_BACK

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_latest_data_date(symbol):
    """
    Get the latest date for which we have data in the database.
    
    Args:
        symbol (str): Stock symbol
    
    Returns:
        datetime.date: Latest date in database, or None if no data exists
    """
    try:
        query = """
        SELECT MAX(date) FROM stocks 
        WHERE symbol = :symbol
        """
        
        result = execute_query(query, {'symbol': symbol})
        latest_date = result.scalar()
        
        return latest_date
        
    except Exception as e:
        logger.error(f"Error getting latest date for {symbol}: {e}")
        return None

def fetch_latest_data(symbol, days_back=7):
    """
    Fetch the latest stock data from yfinance.
    
    Args:
        symbol (str): Stock symbol
        days_back (int): Number of days to look back for updates
    
    Returns:
        pd.DataFrame: Latest stock data
    """
    try:
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        logger.info(f"Fetching latest data for {symbol} from {start_date} to {end_date}")
        
        # Download data using yfinance
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date + timedelta(days=1))
        
        if data.empty:
            logger.warning(f"No new data found for {symbol}")
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
        
        # Convert date to date object
        data['date'] = pd.to_datetime(data['date']).dt.date
        
        logger.info(f"✅ Fetched {len(data)} new records for {symbol}")
        return data
        
    except Exception as e:
        logger.error(f"Error fetching latest data for {symbol}: {e}")
        return pd.DataFrame()

def update_stock_data(symbol, force_update=False):
    """
    Update stock data for a specific symbol.
    
    Args:
        symbol (str): Stock symbol
        force_update (bool): Force update even if data is recent
    
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        # Get latest date in database
        latest_db_date = get_latest_data_date(symbol)
        today = datetime.now().date()
        
        if latest_db_date is None:
            logger.info(f"No existing data for {symbol}, fetching historical data")
            # Fetch more historical data for new symbols
            days_back = MAX_DAYS_BACK
        else:
            # Check if we need to update
            days_since_update = (today - latest_db_date).days
            
            if days_since_update == 0 and not force_update:
                logger.info(f"✅ {symbol} data is up to date (last update: {latest_db_date})")
                return True
            
            if days_since_update > 7 and not force_update:
                logger.info(f"⚠️  {symbol} data is {days_since_update} days old, updating...")
            
            days_back = min(days_since_update + 2, MAX_DAYS_BACK)  # Add buffer
        
        # Fetch latest data
        new_data = fetch_latest_data(symbol, days_back)
        
        if new_data.empty:
            logger.warning(f"No new data available for {symbol}")
            return False
        
        # Remove duplicates based on symbol and date
        new_data = new_data.drop_duplicates(subset=['symbol', 'date'])
        
        # Insert new data into database
        insert_dataframe(new_data, 'stocks')
        
        logger.info(f"✅ Successfully updated {symbol} with {len(new_data)} new records")
        return True
        
    except Exception as e:
        logger.error(f"Error updating data for {symbol}: {e}")
        return False

def update_all_stocks(force_update=False):
    """
    Update data for all stocks in TOP_50_TICKERS.
    
    Args:
        force_update (bool): Force update for all stocks
    """
    logger.info(f"🔄 Starting real-time update for all stocks (force_update={force_update})")
    
    success_count = 0
    total_count = len(TOP_50_TICKERS)
    
    for i, symbol in enumerate(TOP_50_TICKERS, 1):
        logger.info(f"📊 Processing {symbol} ({i}/{total_count})")
        
        if update_stock_data(symbol, force_update):
            success_count += 1
        
        # Add small delay to avoid rate limiting
        time.sleep(0.5)
    
    logger.info(f"✅ Update completed: {success_count}/{total_count} stocks updated successfully")

def continuous_update(interval_hours=UPDATE_FREQUENCY_HOURS):
    """
    Run continuous updates at specified intervals.
    
    Args:
        interval_hours (int): Hours between updates
    """
    logger.info(f"🔄 Starting continuous updates every {interval_hours} hours")
    
    while True:
        try:
            update_all_stocks()
            
            # Wait for next update
            next_update = datetime.now() + timedelta(hours=interval_hours)
            logger.info(f"⏰ Next update scheduled for {next_update.strftime('%Y-%m-%d %H:%M:%S')}")
            
            time.sleep(interval_hours * 3600)  # Convert hours to seconds
            
        except KeyboardInterrupt:
            logger.info("🛑 Continuous update stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in continuous update: {e}")
            logger.info("Retrying in 1 hour...")
            time.sleep(3600)

def get_data_summary():
    """
    Get a summary of data availability in the database.
    """
    try:
        query = """
        SELECT 
            symbol,
            MIN(date) as earliest_date,
            MAX(date) as latest_date,
            COUNT(*) as total_records
        FROM stocks 
        GROUP BY symbol
        ORDER BY latest_date DESC
        """
        
        result = execute_query(query)
        summary_df = pd.DataFrame(result.fetchall(), columns=['symbol', 'earliest_date', 'latest_date', 'total_records'])
        
        today = datetime.now().date()
        
        # Add days since last update
        summary_df['days_since_update'] = (today - pd.to_datetime(summary_df['latest_date']).dt.date).dt.days
        
        return summary_df
        
    except Exception as e:
        logger.error(f"Error getting data summary: {e}")
        return pd.DataFrame()

def main():
    """Main function for real-time data updates."""
    parser = argparse.ArgumentParser(description='Real-time stock data updater')
    parser.add_argument('--symbol', type=str, default=None,
                       help='Update specific stock symbol')
    parser.add_argument('--all', action='store_true',
                       help='Update all stocks in TOP_50_TICKERS')
    parser.add_argument('--force', action='store_true',
                       help='Force update even if data is recent')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuous updates')
    parser.add_argument('--interval', type=int, default=UPDATE_FREQUENCY_HOURS,
                       help=f'Hours between updates (default: {UPDATE_FREQUENCY_HOURS})')
    parser.add_argument('--summary', action='store_true',
                       help='Show data summary')

    args = parser.parse_args()

    try:
        # Create database tables if they don't exist
        create_tables()

        if args.summary:
            # Show data summary
            summary_df = get_data_summary()
            if not summary_df.empty:
                print("\n📊 Data Summary:")
                print("=" * 80)
                print(summary_df.to_string(index=False))
                
                # Show outdated data
                outdated = summary_df[summary_df['days_since_update'] > 1]
                if not outdated.empty:
                    print(f"\n⚠️  {len(outdated)} stocks need updates:")
                    for _, row in outdated.head(10).iterrows():
                        print(f"   {row['symbol']}: {row['days_since_update']} days old")
            else:
                print("❌ No data found in database")
            return

        if args.continuous:
            # Run continuous updates
            continuous_update(args.interval)
        elif args.all:
            # Update all stocks
            update_all_stocks(args.force)
        elif args.symbol:
            # Update specific symbol
            symbol = args.symbol.upper()
            if symbol in TOP_50_TICKERS:
                update_stock_data(symbol, args.force)
            else:
                logger.warning(f"Symbol {symbol} not in TOP_50_TICKERS, but attempting update anyway")
                update_stock_data(symbol, args.force)
        else:
            # Default: update all stocks
            update_all_stocks(args.force)

    except Exception as e:
        logger.error(f"Error in main function: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
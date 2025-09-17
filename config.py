"""
Configuration settings for the stock market prediction project.
"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
# Load environment variables
load_dotenv()
# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:1234@localhost:3306/stock_market_db')
# Default settings - Use real-time dates
DEFAULT_START_DATE = '2020-01-01'
DEFAULT_END_DATE = datetime.now().strftime('%Y-%m-%d')  # Today's date
DEFAULT_SYMBOL = 'AAPL'
# Model parameters
ARIMA_ORDER = (1, 1, 1)  # (p, d, q) parameters
FORECAST_DAYS = 30
MOVING_AVERAGE_PERIODS = [5, 10, 20]
# News API settings
NEWS_RSS_FEED = "https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en"
# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# Real-time update settings
AUTO_UPDATE_ENABLED = True
UPDATE_FREQUENCY_HOURS = 6  # Update every 6 hours
MAX_DAYS_BACK = 365  # Maximum days to look back for updates
# Check database connection
SQLALCHEMY_DATABASE_URI = DATABASE_URL
# from sqlalchemy import text
# engine = create_engine(SQLALCHEMY_DATABASE_URI)
# with engine.connect() as conn:
#     print(conn.execute(text("SELECT 1")).fetchall()) 
# Standard Top 50 US tickers (S&P 500 large caps, for example)
TOP_50_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH', 'JPM',
    'V', 'XOM', 'LLY', 'AVGO', 'JNJ', 'WMT', 'MA', 'PG', 'CVX', 'MRK',
    'HD', 'COST', 'ABBV', 'ADBE', 'PEP', 'BAC', 'KO', 'PFE', 'NFLX', 'TMO',
    'DIS', 'ABT', 'CSCO', 'MCD', 'CRM', 'ACN', 'DHR', 'LIN', 'VZ', 'WFC',
    'INTC', 'TXN', 'NEE', 'PM', 'BMY', 'UNP', 'HON', 'ORCL', 'AMGN', 'IBM'
] 

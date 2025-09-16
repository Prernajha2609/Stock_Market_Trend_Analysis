"""
News data collector using Google News RSS feed.
Fetches stock-related news headlines and saves to PostgreSQL database.
"""
import argparse
import logging
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import feedparser
import requests
from urllib.parse import quote_plus
import re
import time
# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import create_tables, insert_dataframe, execute_query
from config import NEWS_RSS_FEED, DEFAULT_SYMBOL, TOP_50_TICKERS
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def fetch_news_headlines(symbol, max_articles=50):
    """
    Fetch news headlines for a given stock symbol using Google News RSS feed.
    Args:
        symbol (str): Stock symbol (e.g., 'AAPL')
        max_articles (int): Maximum number of articles to fetch
    Returns:
        pd.DataFrame: News headlines with columns: symbol, date, headline, link, source
    """
    try:
        logger.info(f"Fetching news headlines for {symbol}")
        # Create search query
        search_query = f"{symbol} stock"
        encoded_query = quote_plus(search_query)
        # Construct RSS feed URL
        rss_url = NEWS_RSS_FEED.format(encoded_query)
        # Parse RSS feed
        feed = feedparser.parse(rss_url)
        if not feed.entries:
            logger.warning(f"No news articles found for {symbol}")
            return pd.DataFrame()
        # Extract article information
        articles = []
        for entry in feed.entries[:max_articles]:
            try:
                # Extract date
                if hasattr(entry, 'published_parsed') and entry.published_parsed and isinstance(entry.published_parsed, time.struct_time):
                    date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                else:
                    date = datetime.now()               
                # Extract source from link or title
                source = extract_source(entry.link) if hasattr(entry, 'link') else "Unknown"                
                # Clean headline
                headline = clean_headline(entry.title) if hasattr(entry, 'title') else ""               
                articles.append({
                    'symbol': symbol,
                    'date': date.date(),
                    'headline': headline,
                    'link': entry.link if hasattr(entry, 'link') else "",
                    'source': source})                
            except Exception as e:
                logger.warning(f"Error processing article: {e}")
                continue        
        if not articles:
            logger.warning(f"No valid articles found for {symbol}")
            return pd.DataFrame()        
        df = pd.DataFrame(articles)
        logger.info(f"Successfully fetched {len(df)} news articles for {symbol}")
        return df        
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        raise

def extract_source(url):
    """
    Extract source name from URL.    
    Args:
        url (str): Article URL    
    Returns:
        str: Source name
    """
    try:
        # Extract domain from URL
        if 'news.google.com' in url:
            # For Google News URLs, try to extract the actual source
            match = re.search(r'url=([^&]+)', url)
            if match:
                url = match.group(1)        
        # Extract domain
        domain = url.split('//')[-1].split('/')[0]        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]        
        # Clean up domain name
        source = domain.split('.')[0].title()       
        return source if source else "Unknown"        
    except Exception:
        return "Unknown"

def clean_headline(headline):
    """
    Clean and normalize headline text.    
    Args:
        headline (str): Raw headline text    
    Returns:
        str: Cleaned headline
    """
    try:
        # Remove extra whitespace
        headline = re.sub(r'\s+', ' ', headline.strip())        
        # Remove special characters that might cause database issues
        headline = re.sub(r'[^\w\s\-.,!?]', '', headline)        
        # Limit length
        if len(headline) > 500:
            headline = headline[:497] + "..."        
        return headline       
    except Exception:
        return headline

def save_to_database(df, symbol):
    """
    Save news data to PostgreSQL database.    
    Args:
        df (pd.DataFrame): News data to save
        symbol (str): Stock symbol
    """
    try:
        if not df.empty:
            # Remove duplicates based on symbol, date, and headline
            df = df.drop_duplicates(subset=['symbol', 'date', 'headline'])            
            # Insert data into database
            insert_dataframe(df, 'news')            
            logger.info(f"Successfully saved {len(df)} news articles for {symbol} to database")
        else:
            logger.warning(f"No news data to save for {symbol}")            
    except Exception as e:
        logger.error(f"Error saving news data to database: {e}")
        raise

def check_existing_news(symbol, days_back=7):
    """
    Check if recent news already exists in database for the given symbol.    
    Args:
        symbol (str): Stock symbol
        days_back (int): Number of days to check back   
    Returns:
        bool: True if recent news exists, False otherwise
    """
    try:
        cutoff_date = datetime.now().date() - timedelta(days=days_back)        
        query = """
        SELECT COUNT(*) FROM news 
        WHERE symbol = :symbol
        AND date >= :cutoff_date
        """        
        result = execute_query(query, {
            'symbol': symbol,
            'cutoff_date': cutoff_date})        
        count = result.scalar()
        return (count is not None) and (count > 0)       
    except Exception as e:
        logger.error(f"Error checking existing news: {e}")
        return False

def main():
    """Main function to collect news data."""
    parser = argparse.ArgumentParser(description='Fetch news headlines using Google News RSS')
    parser.add_argument('--symbol', type=str, default=DEFAULT_SYMBOL,
                       help=f'Stock symbol (default: {DEFAULT_SYMBOL})')
    parser.add_argument('--max_articles', type=int, default=50,
                       help='Maximum number of articles to fetch (default: 50)')
    parser.add_argument('--force', action='store_true',
                       help='Force fetch even if recent news already exists')
    parser.add_argument('--all', action='store_true',
                       help='Fetch news for all tickers in TOP_50_TICKERS')
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
            # Check if recent news already exists
            if not args.force and check_existing_news(symbol):
                logger.info(f"Recent news for {symbol} already exists in database")
                logger.info("Use --force flag to re-fetch news")
                continue
            # Fetch news headlines
            df = fetch_news_headlines(symbol, args.max_articles)
            if not df.empty:
                # Save to database
                save_to_database(df, symbol)
                logger.info(f"News data collection completed for {symbol}")
            else:
                logger.error(f"Failed to fetch news for {symbol}")
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main() 
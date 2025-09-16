"""
Sentiment analysis for news headlines using VADER.
Analyzes sentiment of news headlines and updates the database.
"""
import argparse
import logging
import sys
import os
import pandas as pd
import numpy as np
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import create_tables, read_dataframe, execute_query
from config import DEFAULT_SYMBOL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_nltk_data():
    """Download required NLTK data."""
    try:
        nltk.download('vader_lexicon', quiet=True)
        logger.info("NLTK VADER lexicon downloaded successfully")
    except Exception as e:
        logger.error(f"Error downloading NLTK data: {e}")
        raise

def load_news_data(symbol=None):
    """
    Load news headlines from database.
    
    Args:
        symbol (str): Stock symbol (optional, if None loads all symbols)
    
    Returns:
        pd.DataFrame: News headlines with sentiment scores
    """
    try:
        logger.info(f"Loading news data for {symbol if symbol else 'all symbols'}")
        
        if symbol:
            query = """
            SELECT id, symbol, date, headline, link, source, sentiment_score
            FROM news 
            WHERE symbol = %(symbol)s
            ORDER BY date DESC
            """
            params = {'symbol': symbol}
        else:
            query = """
            SELECT id, symbol, date, headline, link, source, sentiment_score
            FROM news 
            ORDER BY date DESC
            """
            params = {}
        
        df = read_dataframe(query, params)
        
        if df.empty:
            logger.warning("No news data found")
            return pd.DataFrame()
        
        logger.info(f"Loaded {len(df)} news articles")
        return df
        
    except Exception as e:
        logger.error(f"Error loading news data: {e}")
        raise

def analyze_sentiment(headline):
    """
    Analyze sentiment of a headline using VADER.
    
    Args:
        headline (str): News headline
    
    Returns:
        float: Sentiment score (-1 to 1, where -1 is very negative, 1 is very positive)
    """
    try:
        # Initialize VADER sentiment analyzer
        sia = SentimentIntensityAnalyzer()
        
        # Get sentiment scores
        scores = sia.polarity_scores(headline)
        
        # Return compound score (normalized between -1 and 1)
        return scores['compound']
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return 0.0

def batch_sentiment_analysis(df):
    """
    Perform sentiment analysis on a batch of headlines.
    
    Args:
        df (pd.DataFrame): DataFrame with headlines
    
    Returns:
        pd.DataFrame: DataFrame with sentiment scores added
    """
    try:
        logger.info("Performing sentiment analysis on headlines")
        
        # Create a copy to avoid modifying original
        df_analyzed = df.copy()
        
        # Analyze sentiment for each headline
        sentiment_scores = []
        for idx, row in df_analyzed.iterrows():
            score = analyze_sentiment(row['headline'])
            sentiment_scores.append(score)
        
        # Add sentiment scores to DataFrame
        df_analyzed['sentiment_score'] = sentiment_scores
        
        # Calculate sentiment statistics
        positive_count = len(df_analyzed[df_analyzed['sentiment_score'] > 0.1])
        negative_count = len(df_analyzed[df_analyzed['sentiment_score'] < -0.1])
        neutral_count = len(df_analyzed) - positive_count - negative_count
        
        logger.info(f"Sentiment analysis completed:")
        logger.info(f"  Positive headlines: {positive_count}")
        logger.info(f"  Negative headlines: {negative_count}")
        logger.info(f"  Neutral headlines: {neutral_count}")
        logger.info(f"  Average sentiment: {df_analyzed['sentiment_score'].mean():.3f}")
        
        return df_analyzed
        
    except Exception as e:
        logger.error(f"Error in batch sentiment analysis: {e}")
        raise

def update_sentiment_scores(df):
    """
    Update sentiment scores in the database.
    
    Args:
        df (pd.DataFrame): DataFrame with sentiment scores
    """
    try:
        logger.info("Updating sentiment scores in database")
        
        # Update each record
        updated_count = 0
        for idx, row in df.iterrows():
            query = """
            UPDATE news 
            SET sentiment_score = :sentiment_score
            WHERE id = :id
            """
            
            result = execute_query(query, {
                'sentiment_score': row['sentiment_score'],
                'id': row['id']
            })
            
            updated_count += 1
        
        logger.info(f"Updated sentiment scores for {updated_count} articles")
        
    except Exception as e:
        logger.error(f"Error updating sentiment scores: {e}")
        raise

def get_sentiment_summary(symbol=None):
    """
    Get sentiment summary statistics.
    
    Args:
        symbol (str): Stock symbol (optional)
    
    Returns:
        dict: Sentiment summary statistics
    """
    try:
        if symbol:
            query = """
            SELECT 
                AVG(sentiment_score) as avg_sentiment,
                COUNT(CASE WHEN sentiment_score > 0.1 THEN 1 END) as positive_count,
                COUNT(CASE WHEN sentiment_score < -0.1 THEN 1 END) as negative_count,
                COUNT(CASE WHEN sentiment_score BETWEEN -0.1 AND 0.1 THEN 1 END) as neutral_count,
                COUNT(*) as total_count
            FROM news 
            WHERE symbol = :symbol AND sentiment_score IS NOT NULL
            """
            params = {'symbol': symbol}
        else:
            query = """
            SELECT 
                AVG(sentiment_score) as avg_sentiment,
                COUNT(CASE WHEN sentiment_score > 0.1 THEN 1 END) as positive_count,
                COUNT(CASE WHEN sentiment_score < -0.1 THEN 1 END) as negative_count,
                COUNT(CASE WHEN sentiment_score BETWEEN -0.1 AND 0.1 THEN 1 END) as neutral_count,
                COUNT(*) as total_count
            FROM news 
            WHERE sentiment_score IS NOT NULL
            """
            params = {}
        
        result = execute_query(query, params)
        row = result.fetchone()
        
        if row:
            summary = {
                'avg_sentiment': float(row[0]) if row[0] else 0.0,
                'positive_count': int(row[1]),
                'negative_count': int(row[2]),
                'neutral_count': int(row[3]),
                'total_count': int(row[4])
            }
            
            logger.info("Sentiment Summary:")
            logger.info(f"  Average sentiment: {summary['avg_sentiment']:.3f}")
            logger.info(f"  Positive articles: {summary['positive_count']}")
            logger.info(f"  Negative articles: {summary['negative_count']}")
            logger.info(f"  Neutral articles: {summary['neutral_count']}")
            logger.info(f"  Total articles: {summary['total_count']}")
            
            return summary
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting sentiment summary: {e}")
        return None

def main():
    """Main function to analyze sentiment of news headlines."""
    parser = argparse.ArgumentParser(description='Analyze sentiment of news headlines')
    parser.add_argument('--symbol', type=str, default=DEFAULT_SYMBOL,
                       help=f'Stock symbol (default: {DEFAULT_SYMBOL})')
    parser.add_argument('--all_symbols', action='store_true',
                       help='Analyze sentiment for all symbols')
    parser.add_argument('--summary_only', action='store_true',
                       help='Only show sentiment summary, do not analyze')
    
    args = parser.parse_args()
    
    try:
        # Download NLTK data if needed
        download_nltk_data()
        
        # Create database tables if they don't exist
        create_tables()
        
        if args.summary_only:
            # Show sentiment summary only
            if args.all_symbols:
                summary = get_sentiment_summary()
            else:
                summary = get_sentiment_summary(args.symbol)
            return
        
        # Load news data
        if args.all_symbols:
            df = load_news_data()
        else:
            df = load_news_data(args.symbol)
        
        if df.empty:
            logger.error("No news data found for analysis")
            sys.exit(1)
        
        # Filter out articles that already have sentiment scores
        df_to_analyze = df[df['sentiment_score'].isnull()]
        
        if df_to_analyze.empty:
            logger.info("All articles already have sentiment scores")
            # Show summary
            if args.all_symbols:
                get_sentiment_summary()
            else:
                get_sentiment_summary(args.symbol)
            return
        
        logger.info(f"Analyzing sentiment for {len(df_to_analyze)} articles")
        
        # Perform sentiment analysis
        df_analyzed = batch_sentiment_analysis(df_to_analyze)
        
        # Update database with sentiment scores
        update_sentiment_scores(df_analyzed)
        
        # Show summary
        if args.all_symbols:
            get_sentiment_summary()
        else:
            get_sentiment_summary(args.symbol)
        
        logger.info("Sentiment analysis completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
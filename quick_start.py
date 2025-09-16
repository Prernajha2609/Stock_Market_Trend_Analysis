"""
Quick start script to run the entire stock market prediction pipeline.
"""
import argparse
import logging
import sys
import os
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and log the result."""
    logger.info(f"🔄 {description}")
    try:
        result = os.system(command)
        if result == 0:
            logger.info(f"✅ {description} completed successfully")
            return True
        else:
            logger.error(f"❌ {description} failed with exit code {result}")
            return False
    except Exception as e:
        logger.error(f"❌ Error running {description}: {e}")
        return False

def main():
    """Main quick start function."""
    parser = argparse.ArgumentParser(description='Quick start for stock market prediction pipeline')
    parser.add_argument('--symbol', type=str, default='AAPL',
                       help='Stock symbol (default: AAPL)')
    parser.add_argument('--start_date', type=str, default='2023-01-01',
                       help='Start date for data collection (default: 2023-01-01)')
    parser.add_argument('--skip_data_collection', action='store_true',
                       help='Skip data collection steps')
    parser.add_argument('--skip_models', action='store_true',
                       help='Skip model training steps')
    parser.add_argument('--launch_dashboard', action='store_true',
                       help='Launch Streamlit dashboard after completion')
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting Stock Market Prediction Pipeline")
    logger.info(f"📈 Target Symbol: {args.symbol}")
    logger.info(f"📅 Start Date: {args.start_date}")
    
    # Step 1: Data Collection
    if not args.skip_data_collection:
        logger.info("=" * 50)
        logger.info("📊 STEP 1: Data Collection")
        logger.info("=" * 50)
        
        # Collect stock data
        stock_cmd = f"python data/stock_data_collector.py --symbol {args.symbol} --start_date {args.start_date}"
        if not run_command(stock_cmd, "Collecting stock data"):
            logger.error("❌ Stock data collection failed. Stopping pipeline.")
            return False
        
        # Collect news data
        news_cmd = f"python data/news_data_collector.py --symbol {args.symbol}"
        if not run_command(news_cmd, "Collecting news data"):
            logger.warning("⚠️ News data collection failed, but continuing...")
        
        # Clean and engineer features
        clean_cmd = f"python data/data_cleaner.py --symbol {args.symbol}"
        if not run_command(clean_cmd, "Cleaning and engineering features"):
            logger.error("❌ Data cleaning failed. Stopping pipeline.")
            return False
    
    # Step 2: Model Training
    if not args.skip_models:
        logger.info("=" * 50)
        logger.info("🤖 STEP 2: Model Training")
        logger.info("=" * 50)
        
        # Train ARIMA model
        arima_cmd = f"python models/arima_forecaster.py --symbol {args.symbol}"
        if not run_command(arima_cmd, "Training ARIMA model"):
            logger.warning("⚠️ ARIMA model training failed, but continuing...")
        
        # Analyze sentiment
        sentiment_cmd = f"python models/sentiment_analyzer.py --symbol {args.symbol}"
        if not run_command(sentiment_cmd, "Analyzing sentiment"):
            logger.warning("⚠️ Sentiment analysis failed, but continuing...")
        
        # Train Random Forest model
        rf_cmd = f"python models/random_forest_predictor.py --symbol {args.symbol}"
        if not run_command(rf_cmd, "Training Random Forest model"):
            logger.warning("⚠️ Random Forest training failed, but continuing...")
    
    # Step 3: Launch Dashboard
    if args.launch_dashboard:
        logger.info("=" * 50)
        logger.info("📊 STEP 3: Launching Dashboard")
        logger.info("=" * 50)
        
        dashboard_cmd = "streamlit run dashboard/app.py"
        logger.info("🌐 Launching Streamlit dashboard...")
        logger.info("📱 Dashboard will be available at: http://localhost:8501")
        logger.info("🔄 Press Ctrl+C to stop the dashboard")
        
        try:
            os.system(dashboard_cmd)
        except KeyboardInterrupt:
            logger.info("👋 Dashboard stopped by user")
    
    logger.info("=" * 50)
    logger.info("🎉 Pipeline completed successfully!")
    logger.info("=" * 50)
    
    if not args.launch_dashboard:
        logger.info("💡 To launch the dashboard, run:")
        logger.info("   streamlit run dashboard/app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
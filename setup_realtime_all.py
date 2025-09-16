#!/usr/bin/env python3
"""
Complete real-time setup for ALL stocks.
This script sets up the entire system for real-time data collection across all stocks.
"""
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.realtime_updater import update_all_stocks, get_data_summary
from data.stock_data_collector import download_stock_data
from data.data_cleaner import main as clean_data_main
from models.arima_forecaster import main as arima_main
from models.random_forest_predictor import main as rf_main
from models.sentiment_analyzer import main as sentiment_main
from config import TOP_50_TICKERS

def setup_all_stocks_realtime():
    """Set up real-time data collection for all stocks."""
    print("🚀 Setting Up Real-Time Data for ALL Stocks")
    print("=" * 60)
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"📅 Today's date: {today}")
    print(f"📊 Total stocks to process: {len(TOP_50_TICKERS)}")
    
    # Step 1: Initial data collection for all stocks
    print("\n📈 Step 1: Initial Data Collection")
    print("-" * 40)
    
    success_count = 0
    for i, symbol in enumerate(TOP_50_TICKERS, 1):
        print(f"📊 Processing {symbol} ({i}/{len(TOP_50_TICKERS)})")
        
        try:
            # Download historical data
            df = download_stock_data(symbol, "2020-01-01", today)
            if not df.empty:
                print(f"   ✅ {symbol}: {len(df)} records")
                success_count += 1
            else:
                print(f"   ❌ {symbol}: No data")
        except Exception as e:
            print(f"   ❌ {symbol}: Error - {e}")
    
    print(f"\n✅ Initial collection completed: {success_count}/{len(TOP_50_TICKERS)} stocks")
    
    # Step 2: Clean and engineer data for all stocks
    print("\n🧹 Step 2: Data Cleaning and Feature Engineering")
    print("-" * 40)
    
    clean_count = 0
    for i, symbol in enumerate(TOP_50_TICKERS, 1):
        print(f"🧹 Cleaning {symbol} ({i}/{len(TOP_50_TICKERS)})")
        
        try:
            # Run data cleaning for this symbol
            import sys
            original_argv = sys.argv
            sys.argv = ['data_cleaner.py', '--symbol', symbol, '--force']
            clean_data_main()
            sys.argv = original_argv
            print(f"   ✅ {symbol}: Cleaned successfully")
            clean_count += 1
        except Exception as e:
            print(f"   ❌ {symbol}: Error - {e}")
    
    print(f"\n✅ Data cleaning completed: {clean_count}/{len(TOP_50_TICKERS)} stocks")
    
    # Step 3: Train ARIMA models for all stocks
    print("\n🔮 Step 3: Training ARIMA Models")
    print("-" * 40)
    
    arima_count = 0
    for i, symbol in enumerate(TOP_50_TICKERS, 1):
        print(f"🔮 Training ARIMA for {symbol} ({i}/{len(TOP_50_TICKERS)})")
        
        try:
            # check if the model is already trained
            # Run ARIMA training for this symbol
            import sys
            original_argv = sys.argv
            sys.argv = ['arima_forecaster.py', '--symbol', symbol]
            arima_main()
            sys.argv = original_argv
            print(f"   ✅ {symbol}: ARIMA trained")
            arima_count += 1
        except Exception as e:
            print(f"   ❌ {symbol}: Error - {e}")
    
    print(f"\n✅ ARIMA training completed: {arima_count}/{len(TOP_50_TICKERS)} stocks")
    
    # Step 4: Train Random Forest models for all stocks
    print("\n🌲 Step 4: Training Random Forest Models")
    print("-" * 40)
    
    rf_count = 0
    for i, symbol in enumerate(TOP_50_TICKERS, 1):
        print(f"🌲 Training RF for {symbol} ({i}/{len(TOP_50_TICKERS)})")
        
        try:
            # Run Random Forest training for this symbol
            import sys
            original_argv = sys.argv
            sys.argv = ['random_forest_predictor.py', '--symbol', symbol]
            rf_main()
            sys.argv = original_argv
            print(f"   ✅ {symbol}: Random Forest trained")
            rf_count += 1
        except Exception as e:
            print(f"   ❌ {symbol}: Error - {e}")
    
    print(f"\n✅ Random Forest training completed: {rf_count}/{len(TOP_50_TICKERS)} stocks")
    
    # Step 5: Analyze sentiment for all stocks
    print("\n😊 Step 5: Sentiment Analysis")
    print("-" * 40)
    
    sentiment_count = 0
    for i, symbol in enumerate(TOP_50_TICKERS, 1):
        print(f"😊 Analyzing sentiment for {symbol} ({i}/{len(TOP_50_TICKERS)})")
        
        try:
            # Run sentiment analysis for this symbol
            import sys
            original_argv = sys.argv
            sys.argv = ['sentiment_analyzer.py', '--symbol', symbol]
            sentiment_main()
            sys.argv = original_argv
            print(f"   ✅ {symbol}: Sentiment analyzed")
            sentiment_count += 1
        except Exception as e:
            print(f"   ❌ {symbol}: Error - {e}")
    
    print(f"\n✅ Sentiment analysis completed: {sentiment_count}/{len(TOP_50_TICKERS)} stocks")
    
    # Step 6: Initial real-time update
    print("\n🔄 Step 6: Initial Real-Time Update")
    print("-" * 40)
    
    update_all_stocks(force_update=True)
    
    # Final summary
    print("\n🎉 SETUP COMPLETED!")
    print("=" * 60)
    print(f"📊 Total stocks processed: {len(TOP_50_TICKERS)}")
    print(f"📈 Data collection: {success_count}/{len(TOP_50_TICKERS)}")
    print(f"🧹 Data cleaning: {clean_count}/{len(TOP_50_TICKERS)}")
    print(f"🔮 ARIMA models: {arima_count}/{len(TOP_50_TICKERS)}")
    print(f"🌲 Random Forest models: {rf_count}/{len(TOP_50_TICKERS)}")
    print(f"😊 Sentiment analysis: {sentiment_count}/{len(TOP_50_TICKERS)}")
    
    return {
        'data_collection': success_count,
        'data_cleaning': clean_count,
        'arima_models': arima_count,
        'random_forest_models': rf_count,
        'sentiment_analysis': sentiment_count
    }

def show_data_summary():
    """Show current data status for all stocks."""
    print("\n📋 Current Data Summary")
    print("=" * 60)
    
    summary_df = get_data_summary()
    if not summary_df.empty:
        print(f"✅ Database has data for {len(summary_df)} symbols")
        print(f"📈 Latest data: {summary_df['latest_date'].max()}")
        print(f"📉 Earliest data: {summary_df['earliest_date'].min()}")
        
        # Show stocks that need updates
        today = datetime.now().date()
        import pandas as pd
        summary_df['days_old'] = (today - pd.to_datetime(summary_df['latest_date']).dt.date).dt.days
        
        outdated = summary_df[summary_df['days_old'] > 1]
        if not outdated.empty:
            print(f"\n⚠️  {len(outdated)} stocks need updates:")
            for _, row in outdated.head(10).iterrows():
                print(f"   {row['symbol']}: {row['days_old']} days old")
    else:
        print("❌ No data in database yet")

def show_usage_commands():
    """Show commands for managing all stocks."""
    print("\n💡 Commands for Managing ALL Stocks")
    print("=" * 60)
    
    print("🔄 Update all stocks with latest data:")
    print("   python data/realtime_updater.py --all")
    
    print("\n🔄 Force update all stocks:")
    print("   python data/realtime_updater.py --all --force")
    
    print("\n🔄 Continuous updates (every 6 hours):")
    print("   python data/realtime_updater.py --continuous")
    
    print("\n📋 Check data status:")
    print("   python data/realtime_updater.py --summary")
    
    print("\n📊 Launch dashboard:")
    print("   streamlit run dashboard/app.py")
    
    print("\n🎯 Quick update check:")
    print("   python realtime_demo.py")

def main():
    """Main setup function."""
    print("🎯 Complete Real-Time Setup for ALL Stocks")
    print("=" * 60)
    
    # Check if user wants to proceed
    print("This will set up real-time data collection for ALL stocks.")
    print("This process may take 30-60 minutes depending on your system.")
    
    response = input("\nDo you want to continue? (y/n): ").lower().strip()
    if response != 'y':
        print("Setup cancelled.")
        return
    
    # Run the complete setup
    results = setup_all_stocks_realtime()
    
    # Show summary
    show_data_summary()
    
    # Show usage commands
    show_usage_commands()
    
    print("\n🎉 Your real-time stock data system is ready!")
    print("\nNext steps:")
    print("1. Run: python data/realtime_updater.py --continuous")
    print("2. Launch: streamlit run dashboard/app.py")
    print("3. Monitor: python data/realtime_updater.py --summary")

if __name__ == "__main__":
    main() 
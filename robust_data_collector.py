#!/usr/bin/env python3
"""
Robust data collector for ALL stocks with retry logic and rate limiting.
This script handles network issues, API rate limits, and temporary failures.
"""
import subprocess
import sys
import os
import time
import random
from datetime import datetime, timedelta

def run_command_with_retry(command, description, max_retries=3, delay=5):
    """Run a command with retry logic."""
    print(f"\n🔄 {description}")
    print(f"Command: {command}")
    print("-" * 50)
    
    for attempt in range(max_retries):
        try:
            print(f"   Attempt {attempt + 1}/{max_retries}...")
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ {description} completed successfully")
                return True
            else:
                print(f"   ❌ Attempt {attempt + 1} failed")
                print(f"   Error: {result.stderr}")
                
                if attempt < max_retries - 1:
                    wait_time = delay * (attempt + 1) + random.uniform(1, 3)
                    print(f"   ⏳ Waiting {wait_time:.1f} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print(f"   ❌ {description} failed after {max_retries} attempts")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Attempt {attempt + 1} failed with exception: {e}")
            
            if attempt < max_retries - 1:
                wait_time = delay * (attempt + 1) + random.uniform(1, 3)
                print(f"   ⏳ Waiting {wait_time:.1f} seconds before retry...")
                time.sleep(wait_time)
            else:
                print(f"   ❌ {description} failed after {max_retries} attempts")
                return False
    
    return False

def collect_data_for_all_stocks():
    """Collect data for all stocks with robust error handling."""
    print("🚀 Robust Data Collection for ALL Stocks")
    print("=" * 60)
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"📅 Today's date: {today}")
    
    # Step 1: Collect data for all stocks (with retries)
    print("\n📈 Step 1: Collecting Data for ALL Stocks")
    command1 = f"python data/stock_data_collector.py --all --start_date 2020-01-01 --end_date {today}"
    success1 = run_command_with_retry(command1, "Data collection for all stocks", max_retries=3, delay=10)
    
    if not success1:
        print("\n⚠️  Data collection failed. Trying individual stocks...")
        success1 = collect_individual_stocks()
    
    return success1

def collect_individual_stocks():
    """Collect data for individual stocks if batch collection fails."""
    print("\n📊 Collecting Data for Individual Stocks")
    print("=" * 50)
    
    # Get list of stocks from config
    try:
        from config import TOP_50_TICKERS
        stocks = TOP_50_TICKERS
    except:
        # Fallback list if config import fails
        stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "UNH", "JPM"]
    
    today = datetime.now().strftime('%Y-%m-%d')
    success_count = 0
    
    for i, symbol in enumerate(stocks, 1):
        print(f"\n📊 Processing {symbol} ({i}/{len(stocks)})")
        
        command = f"python data/stock_data_collector.py --symbol {symbol} --start_date 2020-01-01 --end_date {today}"
        success = run_command_with_retry(command, f"Data collection for {symbol}", max_retries=2, delay=5)
        
        if success:
            success_count += 1
        
        # Add delay between stocks to avoid rate limiting
        if i < len(stocks):
            delay = random.uniform(2, 5)
            print(f"   ⏳ Waiting {delay:.1f} seconds before next stock...")
            time.sleep(delay)
    
    print(f"\n✅ Individual collection completed: {success_count}/{len(stocks)} stocks")
    return success_count > 0

def clean_data_for_all_stocks():
    """Clean and engineer data for all stocks."""
    print("\n🧹 Step 2: Cleaning and Engineering Data for ALL Stocks")
    command2 = "python data/data_cleaner.py --all --force"
    return run_command_with_retry(command2, "Data cleaning for all stocks", max_retries=2, delay=5)

def train_models_for_all_stocks():
    """Train models for all stocks."""
    print("\n🔮 Step 3: Training Models for ALL Stocks")
    
    # Train ARIMA models
    print("\n🔮 Training ARIMA Models")
    command3 = "python models/arima_forecaster.py --all"
    success3 = run_command_with_retry(command3, "ARIMA training for all stocks", max_retries=2, delay=5)
    
    # Train Random Forest models
    print("\n🌲 Training Random Forest Models")
    command4 = "python models/random_forest_predictor.py --all"
    success4 = run_command_with_retry(command4, "Random Forest training for all stocks", max_retries=2, delay=5)
    
    # Analyze sentiment
    print("\n😊 Analyzing Sentiment")
    command5 = "python models/sentiment_analyzer.py --all"
    success5 = run_command_with_retry(command5, "Sentiment analysis for all stocks", max_retries=2, delay=5)
    
    return success3, success4, success5

def update_real_time_data():
    """Update real-time data for all stocks."""
    print("\n🔄 Step 4: Initial Real-Time Update for ALL Stocks")
    command6 = "python data/realtime_updater.py --all --force"
    return run_command_with_retry(command6, "Initial real-time update", max_retries=2, delay=5)

def main():
    """Main function."""
    print("🎯 Robust Data Collection for ALL Stocks")
    print("=" * 60)
    
    print("This script will collect data for ALL stocks with robust error handling.")
    print("It includes retry logic, rate limiting, and fallback mechanisms.")
    
    response = input("\nDo you want to continue? (y/n): ").lower().strip()
    if response != 'y':
        print("Setup cancelled.")
        return
    
    # Run the robust collection
    success1 = collect_data_for_all_stocks()
    success2 = clean_data_for_all_stocks()
    success3, success4, success5 = train_models_for_all_stocks()
    success6 = update_real_time_data()
    
    # Summary
    print("\n🎉 COLLECTION SUMMARY")
    print("=" * 60)
    steps = [
        ("Data Collection", success1),
        ("Data Cleaning", success2),
        ("ARIMA Models", success3),
        ("Random Forest Models", success4),
        ("Sentiment Analysis", success5),
        ("Real-time Update", success6)
    ]
    
    for step_name, success in steps:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{step_name}: {status}")
    
    successful_steps = sum(1 for _, success in steps if success)
    print(f"\nOverall: {successful_steps}/{len(steps)} steps completed successfully")
    
    if successful_steps >= 4:
        print("\n🎉 Great! Most steps completed successfully.")
        print("Your real-time stock data system is ready!")
    else:
        print("\n⚠️  Some steps failed. You may need to run them individually.")
    
    # Show next steps
    print("\n💡 Next Steps")
    print("=" * 60)
    print("🔄 Start continuous updates:")
    print("   python data/realtime_updater.py --continuous")
    print("\n📊 Launch dashboard:")
    print("   streamlit run dashboard/app.py")
    print("\n📋 Check data status:")
    print("   python data/realtime_updater.py --summary")

if __name__ == "__main__":
    main() 
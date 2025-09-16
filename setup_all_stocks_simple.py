#!/usr/bin/env python3
"""
Simple setup script for ALL stocks using subprocess calls.
This avoids import issues and uses the existing command-line scripts.
"""
import subprocess
import sys
import os
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def setup_all_stocks():
    """Set up real-time data collection for all stocks."""
    print("🚀 Setting Up Real-Time Data for ALL Stocks")
    print("=" * 60)
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"📅 Today's date: {today}")
    
    # Step 1: Collect data for all stocks
    print("\n📈 Step 1: Collecting Data for ALL Stocks")
    command1 = f"python data/stock_data_collector.py --all --start_date 2020-01-01 --end_date {today}"
    success1 = run_command(command1, "Data collection for all stocks")
    
    # Step 2: Clean and engineer data for all stocks
    print("\n🧹 Step 2: Cleaning and Engineering Data for ALL Stocks")
    command2 = "python data/data_cleaner.py --all --force"
    success2 = run_command(command2, "Data cleaning for all stocks")
    
    # Step 3: Train ARIMA models for all stocks
    print("\n🔮 Step 3: Training ARIMA Models for ALL Stocks")
    command3 = "python models/arima_forecaster.py --all"
    success3 = run_command(command3, "ARIMA training for all stocks")
    
    # Step 4: Train Random Forest models for all stocks
    print("\n🌲 Step 4: Training Random Forest Models for ALL Stocks")
    command4 = "python models/random_forest_predictor.py --all"
    success4 = run_command(command4, "Random Forest training for all stocks")
    
    # Step 5: Analyze sentiment for all stocks
    print("\n😊 Step 5: Sentiment Analysis for ALL Stocks")
    command5 = "python models/sentiment_analyzer.py --all"
    success5 = run_command(command5, "Sentiment analysis for all stocks")
    
    # Step 6: Initial real-time update
    print("\n🔄 Step 6: Initial Real-Time Update for ALL Stocks")
    command6 = "python data/realtime_updater.py --all --force"
    success6 = run_command(command6, "Initial real-time update")
    
    # Summary
    print("\n🎉 SETUP SUMMARY")
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

def show_next_steps():
    """Show what to do next."""
    print("\n💡 Next Steps")
    print("=" * 60)
    
    print("🔄 Start continuous updates:")
    print("   python data/realtime_updater.py --continuous")
    
    print("\n📊 Launch dashboard:")
    print("   streamlit run dashboard/app.py")
    
    print("\n📋 Check data status:")
    print("   python data/realtime_updater.py --summary")
    
    print("\n🎯 Quick management:")
    print("   python manage_all_stocks.py status")
    print("   python manage_all_stocks.py update")

def main():
    """Main function."""
    print("🎯 Simple Setup for ALL Stocks")
    print("=" * 60)
    
    print("This will set up real-time data collection for ALL stocks.")
    print("This process may take 30-60 minutes depending on your system.")
    
    response = input("\nDo you want to continue? (y/n): ").lower().strip()
    if response != 'y':
        print("Setup cancelled.")
        return
    
    # Run the setup
    setup_all_stocks()
    
    # Show next steps
    show_next_steps()
    
    print("\n🎉 Setup process completed!")
    print("Your real-time stock data system is ready for ALL stocks!")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Real-time stock data demonstration.
Shows how to fetch and update stock data in real-time.
"""
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.realtime_updater import update_stock_data, get_data_summary, update_all_stocks
from data.stock_data_collector import download_stock_data
from config import TOP_50_TICKERS

def demonstrate_realtime_fetching():
    """Demonstrate real-time data fetching capabilities."""
    print("🚀 Real-Time Stock Data Demo")
    print("=" * 60)
    
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"📅 Today's date: {today}")
    print(f"📊 Available symbols: {len(TOP_50_TICKERS)} stocks")
    
    # Show current data status
    print("\n📋 Current Database Status:")
    print("-" * 40)
    summary_df = get_data_summary()
    if not summary_df.empty:
        print(f"✅ Database has data for {len(summary_df)} symbols")
        print(f"📈 Latest data: {summary_df['latest_date'].max()}")
        print(f"📉 Earliest data: {summary_df['earliest_date'].min()}")
    else:
        print("❌ No data in database yet")
    
    return summary_df

def fetch_realtime_data(symbol="AAPL"):
    """Fetch real-time data for a specific symbol."""
    print(f"\n📈 Fetching Real-Time Data for {symbol}")
    print("-" * 50)
    
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Fetch data up to today
    print(f"🔍 Fetching data from 2020-01-01 to {today}...")
    
    df = download_stock_data(symbol, "2020-01-01", today)
    
    if not df.empty:
        print(f"✅ Successfully fetched {len(df)} records")
        print(f"📊 Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"💰 Latest price: ${df['close'].iloc[-1]:.2f}")
        print(f"📈 Price range: ${df['close'].min():.2f} to ${df['close'].max():.2f}")
        
        # Show recent data
        recent_data = df.tail(5)
        print(f"\n📅 Recent data (last 5 days):")
        for _, row in recent_data.iterrows():
            print(f"   {row['date']}: ${row['close']:.2f} (Volume: {row['volume']:,})")
    else:
        print("❌ No data fetched")

def update_single_stock(symbol="AAPL"):
    """Update a single stock with latest data."""
    print(f"\n🔄 Updating {symbol} with Latest Data")
    print("-" * 50)
    
    success = update_stock_data(symbol, force_update=True)
    
    if success:
        print(f"✅ {symbol} updated successfully")
    else:
        print(f"❌ Failed to update {symbol}")

def update_all_stocks_demo():
    """Demonstrate updating all stocks."""
    print(f"\n🔄 Updating All Stocks (Demo with first 5)")
    print("-" * 50)
    
    # Update first 5 stocks for demo
    demo_symbols = TOP_50_TICKERS[:5]
    
    for symbol in demo_symbols:
        print(f"📊 Updating {symbol}...")
        success = update_stock_data(symbol, force_update=False)
        if success:
            print(f"   ✅ {symbol} updated")
        else:
            print(f"   ⚠️  {symbol} no update needed or failed")

def show_usage_examples():
    """Show usage examples for real-time data."""
    print("\n💡 Usage Examples for ALL Stocks")
    print("=" * 50)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    print("🚀 Complete setup for ALL stocks:")
    print("   python setup_realtime_all.py")
    
    print("\n📊 Fetch real-time data for ALL stocks:")
    print(f"   python data/stock_data_collector.py --all --start_date 2020-01-01 --end_date {today}")
    
    print("\n🔄 Update ALL stocks with latest data:")
    print("   python data/realtime_updater.py --all")
    
    print("\n🔄 Force update ALL stocks:")
    print("   python data/realtime_updater.py --all --force")
    
    print("\n🔄 Quick management commands:")
    print("   python manage_all_stocks.py update")
    print("   python manage_all_stocks.py status")
    print("   python manage_all_stocks.py list")
    
    print("\n🔄 Continuous updates (every 6 hours):")
    print("   python data/realtime_updater.py --continuous")
    
    print("\n📋 Check data status for ALL stocks:")
    print("   python data/realtime_updater.py --summary")
    
    print("\n📈 Individual stock commands:")
    print("   python data/stock_data_collector.py --symbol AAPL --start_date 2020-01-01 --end_date 2024-12-31")
    print("   python data/realtime_updater.py --symbol AAPL --force")

def main():
    """Main demonstration function."""
    print("🎯 Real-Time Stock Data System Demo")
    print("=" * 60)
    
    # Show current status
    summary_df = demonstrate_realtime_fetching()
    
    # Fetch real-time data
    fetch_realtime_data("AAPL")
    
    # Update single stock
    update_single_stock("AAPL")
    
    # Update all stocks (demo)
    update_all_stocks_demo()
    
    # Show usage examples
    show_usage_examples()
    
    print("\n✅ Demo completed!")
    print("\n🎯 Key Features:")
    print("   • Real-time data up to today")
    print("   • Automatic database updates")
    print("   • Continuous monitoring")
    print("   • Flexible date ranges")
    print("   • 50+ major stocks supported")

if __name__ == "__main__":
    main() 
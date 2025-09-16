#!/usr/bin/env python3
"""
Test script to demonstrate stock data collection with proper date validation.
This script shows both valid and invalid date scenarios.
"""
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.stock_data_collector import download_stock_data, validate_dates

def test_date_validation():
    """Test date validation with various scenarios."""
    print("🧪 Testing Date Validation")
    print("=" * 50)
    
    # Get today's date
    today = datetime.now().date()
    
    # Test cases
    test_cases = [
        # Valid dates
        ("2024-01-01", "2024-01-31", "Valid past dates"),
        (today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'), "Today's date"),
        
        # Invalid future dates
        ("2025-07-08", "2025-07-15", "Future dates (your original issue)"),
        ("2025-01-01", "2025-12-31", "Future year"),
        
        # Invalid date formats
        ("2024/01/01", "2024/01/31", "Wrong date format"),
        ("01-01-2024", "31-01-2024", "Wrong date format"),
    ]
    
    for start_date, end_date, description in test_cases:
        print(f"\n📅 Test: {description}")
        print(f"   Start: {start_date}, End: {end_date}")
        
        is_valid, error_message = validate_dates(start_date, end_date)
        
        if is_valid:
            print(f"   ✅ Valid dates")
        else:
            print(f"   ❌ {error_message}")

def test_stock_download():
    """Test actual stock data download with valid dates."""
    print("\n📈 Testing Stock Data Download")
    print("=" * 50)
    
    # Get recent valid dates
    today = datetime.now().date()
    start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    print(f"📅 Using valid date range: {start_date} to {end_date}")
    
    # Test with AAPL
    symbol = "AAPL"
    print(f"\n🔍 Downloading data for {symbol}...")
    
    df = download_stock_data(symbol, start_date, end_date)
    
    if not df.empty:
        print(f"✅ Successfully downloaded {len(df)} records")
        print(f"📊 Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"💰 Price range: ${df['close'].min():.2f} to ${df['close'].max():.2f}")
    else:
        print("❌ No data downloaded")

def demonstrate_future_date_error():
    """Demonstrate the specific error you encountered."""
    print("\n🚫 Demonstrating Future Date Error")
    print("=" * 50)
    
    # Your original dates
    start_date = "2025-07-08"
    end_date = "2025-07-15"
    symbol = "AAPL"
    
    print(f"📅 Attempting to fetch data for {symbol} from {start_date} to {end_date}")
    print("⚠️  This will trigger the future date validation error...")
    
    df = download_stock_data(symbol, start_date, end_date)
    
    if df.empty:
        print("✅ Error properly caught and handled")
    else:
        print("❌ Unexpected: Data was downloaded (this shouldn't happen)")

def show_helpful_commands():
    """Show helpful commands for valid data collection."""
    print("\n💡 Helpful Commands")
    print("=" * 50)
    
    today = datetime.now().date()
    
    # Recent data
    recent_start = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    recent_end = today.strftime('%Y-%m-%d')
    
    # Historical data
    historical_start = "2020-01-01"
    historical_end = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print("📊 For recent data (last 30 days):")
    print(f"   python data/stock_data_collector.py --symbol AAPL --start_date {recent_start} --end_date {recent_end}")
    
    print("\n📈 For historical data (since 2020):")
    print(f"   python data/stock_data_collector.py --symbol AAPL --start_date {historical_start} --end_date {historical_end}")
    
    print("\n🎯 For specific date range (example):")
    print("   python data/stock_data_collector.py --symbol AAPL --start_date 2024-01-01 --end_date 2024-12-31")
    
    print("\n🚀 For all top 50 stocks:")
    print("   python data/stock_data_collector.py --all --start_date 2024-01-01 --end_date 2024-12-31")

def main():
    """Main function to run all tests."""
    print("🎯 Stock Data Collection Test Suite")
    print("=" * 60)
    
    # Run tests
    test_date_validation()
    test_stock_download()
    demonstrate_future_date_error()
    show_helpful_commands()
    
    print("\n✅ Test suite completed!")
    print("\n💡 Key Takeaways:")
    print("   • Stock data is only available for past dates")
    print("   • Use YYYY-MM-DD format for dates")
    print("   • The system now provides helpful error messages")
    print("   • Try recent dates for testing")

if __name__ == "__main__":
    main() 
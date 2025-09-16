#!/usr/bin/env python3
"""
Test script to debug data fetching issues.
This will help identify why data fetching is failing for dates after 2024.
"""
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import yfinance as yf
import pandas as pd
from data.stock_data_collector import download_stock_data, validate_dates

def test_symbol_data(symbol="MSFT"):
    """Test data fetching for a specific symbol."""
    print(f"🔍 Testing data fetching for {symbol}")
    print("=" * 60)
    
    # Test different date ranges
    test_ranges = [
        ("2024-01-01", "2024-12-31", "Full 2024"),
        ("2024-06-01", "2024-12-31", "Second half 2024"),
        ("2024-12-01", "2024-12-31", "December 2024"),
        ("2024-12-15", "2024-12-31", "Last two weeks 2024"),
        ("2024-12-30", "2024-12-31", "Last day 2024"),
        ("2025-01-01", "2025-01-31", "January 2025"),
        ("2025-06-01", "2025-07-19", "Recent 2025"),
    ]
    
    for start_date, end_date, description in test_ranges:
        print(f"\n📅 Testing: {description} ({start_date} to {end_date})")
        
        # Validate dates
        is_valid, error_msg = validate_dates(start_date, end_date)
        if not is_valid:
            print(f"   ❌ Date validation failed: {error_msg}")
            continue
        
        # Test direct yfinance call
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if not data.empty:
                print(f"   ✅ Direct yfinance: {len(data)} records")
                print(f"      Date range: {data.index.min().date()} to {data.index.max().date()}")
                print(f"      Latest price: ${data['Close'].iloc[-1]:.2f}")
            else:
                print(f"   ❌ Direct yfinance: No data")
                
                # Try broader range
                broader = ticker.history(period="1y")
                if not broader.empty:
                    print(f"      💡 Available range: {broader.index.min().date()} to {broader.index.max().date()}")
                else:
                    print(f"      💡 No data available for this symbol")
                    
        except Exception as e:
            print(f"   ❌ Direct yfinance error: {e}")
        
        # Test our download function
        try:
            df = download_stock_data(symbol, start_date, end_date)
            if not df.empty:
                print(f"   ✅ Our function: {len(df)} records")
            else:
                print(f"   ❌ Our function: No data")
        except Exception as e:
            print(f"   ❌ Our function error: {e}")

def test_multiple_symbols():
    """Test data fetching for multiple symbols."""
    print("\n🔍 Testing Multiple Symbols")
    print("=" * 60)
    
    symbols = ["MSFT", "AAPL", "GOOGL", "AMZN", "NVDA"]
    
    for symbol in symbols:
        print(f"\n📊 Testing {symbol}")
        print("-" * 40)
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Test recent data
            recent_data = ticker.history(period="1mo")
            if not recent_data.empty:
                print(f"   ✅ Recent data available: {len(recent_data)} records")
                print(f"      Latest: {recent_data.index.max().date()} - ${recent_data['Close'].iloc[-1]:.2f}")
            else:
                print(f"   ❌ No recent data")
            
            # Test 2024 data
            data_2024 = ticker.history(start="2024-01-01", end="2024-12-31")
            if not data_2024.empty:
                print(f"   ✅ 2024 data available: {len(data_2024)} records")
            else:
                print(f"   ❌ No 2024 data")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_yfinance_availability():
    """Test what data is actually available from yfinance."""
    print("\n🔍 Testing yfinance Data Availability")
    print("=" * 60)
    
    symbol = "MSFT"
    print(f"📊 Testing {symbol} with different periods")
    
    periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    
    for period in periods:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if not data.empty:
                print(f"   ✅ {period}: {len(data)} records")
                print(f"      Range: {data.index.min().date()} to {data.index.max().date()}")
            else:
                print(f"   ❌ {period}: No data")
                
        except Exception as e:
            print(f"   ❌ {period}: Error - {e}")

def main():
    """Main test function."""
    print("🧪 Data Fetching Debug Test")
    print("=" * 60)
    
    today = datetime.now().date()
    print(f"📅 Current date: {today}")
    
    # Test individual symbol
    test_symbol_data("MSFT")
    
    # Test multiple symbols
    test_multiple_symbols()
    
    # Test yfinance availability
    test_yfinance_availability()
    
    print("\n✅ Test completed!")
    print("\n💡 If you see 'No data' for 2024 dates, it might be because:")
    print("   • yfinance API has rate limits")
    print("   • Data for those specific dates is not available")
    print("   • Network connectivity issues")
    print("   • Symbol might be delisted or changed")

if __name__ == "__main__":
    main() 
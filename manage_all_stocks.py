#!/usr/bin/env python3
"""
Quick management script for ALL stocks.
Easy commands to update, monitor, and manage all stocks in the system.
"""
import sys
import os
import argparse
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.realtime_updater import update_all_stocks, get_data_summary, update_stock_data
from config import TOP_50_TICKERS

def update_all():
    """Update all stocks with latest data."""
    print("🔄 Updating ALL stocks with latest data...")
    print(f"📊 Total stocks: {len(TOP_50_TICKERS)}")
    
    success_count = 0
    for i, symbol in enumerate(TOP_50_TICKERS, 1):
        print(f"📈 {symbol} ({i}/{len(TOP_50_TICKERS)})")
        try:
            if update_stock_data(symbol, force_update=False):
                success_count += 1
                print(f"   ✅ Updated")
            else:
                print(f"   ⚠️  No update needed")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Update completed: {success_count}/{len(TOP_50_TICKERS)} stocks updated")

def force_update_all():
    """Force update all stocks."""
    print("🔄 Force updating ALL stocks...")
    update_all_stocks(force_update=True)

def show_status():
    """Show status of all stocks."""
    print("📋 Status of ALL stocks")
    print("=" * 50)
    
    summary_df = get_data_summary()
    if summary_df.empty:
        print("❌ No data in database")
        return
    
    today = datetime.now().date()
    summary_df['days_old'] = (today - summary_df['latest_date'].dt.date).dt.days
    
    # Count by status
    up_to_date = len(summary_df[summary_df['days_old'] == 0])
    one_day_old = len(summary_df[summary_df['days_old'] == 1])
    outdated = len(summary_df[summary_df['days_old'] > 1])
    
    print(f"✅ Up to date: {up_to_date} stocks")
    print(f"⚠️  1 day old: {one_day_old} stocks")
    print(f"❌ Outdated: {outdated} stocks")
    
    if outdated > 0:
        print(f"\n📊 Outdated stocks:")
        outdated_stocks = summary_df[summary_df['days_old'] > 1].sort_values('days_old', ascending=False)
        for _, row in outdated_stocks.head(10).iterrows():
            print(f"   {row['symbol']}: {row['days_old']} days old")

def show_summary():
    """Show detailed summary."""
    print("📊 Detailed Summary")
    print("=" * 50)
    
    summary_df = get_data_summary()
    if not summary_df.empty:
        print(summary_df.to_string(index=False))
    else:
        print("❌ No data available")

def list_stocks():
    """List all available stocks."""
    print("📋 Available Stocks")
    print("=" * 50)
    
    for i, symbol in enumerate(TOP_50_TICKERS, 1):
        print(f"{i:2d}. {symbol}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Manage ALL stocks in the system')
    parser.add_argument('action', choices=['update', 'force-update', 'status', 'summary', 'list'],
                       help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'update':
        update_all()
    elif args.action == 'force-update':
        force_update_all()
    elif args.action == 'status':
        show_status()
    elif args.action == 'summary':
        show_summary()
    elif args.action == 'list':
        list_stocks()

if __name__ == "__main__":
    main() 
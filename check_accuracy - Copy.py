"""
Script to check if accuracy metrics exist in the database.
"""
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import create_tables, execute_query

def check_accuracy_data():
    """Check if accuracy metrics exist in the database."""
    try:
        # Create tables
        create_tables()
        
        # Check for AAPL specifically
        query = """
        SELECT symbol, model_type, accuracy, `precision`, recall, f1_score, created_at
        FROM model_metrics 
        WHERE symbol = 'AAPL'
        ORDER BY created_at DESC 
        LIMIT 5
        """
        
        result = execute_query(query)
        rows = result.fetchall()
        
        print(f"Found {len(rows)} accuracy records for AAPL:")
        for row in rows:
            print(f"  {row}")
        
        # Check total count
        count_query = """
        SELECT COUNT(*) as total_count, COUNT(DISTINCT symbol) as unique_symbols
        FROM model_metrics
        """
        
        count_result = execute_query(count_query)
        count_row = count_result.fetchone()
        print(f"\nTotal accuracy records: {count_row[0]}")
        print(f"Unique symbols: {count_row[1]}")
        
        # Check a few random symbols
        sample_query = """
        SELECT symbol, accuracy, created_at
        FROM model_metrics 
        ORDER BY RAND()
        LIMIT 10
        """
        
        sample_result = execute_query(sample_query)
        sample_rows = sample_result.fetchall()
        
        print(f"\nSample accuracy records:")
        for row in sample_rows:
            print(f"  {row[0]}: {row[1]:.1%} ({row[2]})")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_accuracy_data() 
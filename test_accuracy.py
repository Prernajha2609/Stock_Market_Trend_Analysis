"""
Test script to manually insert accuracy metrics and test dashboard display.
"""
import sys
import os
from datetime import datetime

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import create_tables, execute_query

def insert_test_accuracy():
    """Insert test accuracy metrics for AAPL."""
    try:
        # Create tables
        create_tables()
        
        # Insert test accuracy data
        query = """
        INSERT INTO model_metrics (symbol, model_type, accuracy, `precision`, recall, f1_score, created_at)
        VALUES ('AAPL', 'RandomForest', 0.8708, 0.8723, 0.8708, 0.8692, :created_at)
        """
        
        execute_query(query, {'created_at': datetime.now().date()})
        print("✅ Test accuracy metrics inserted successfully for AAPL")
        
        # Test reading the data
        test_query = """
        SELECT accuracy, `precision`, recall, f1_score, model_type, created_at
        FROM model_metrics 
        WHERE symbol = 'AAPL'
        ORDER BY created_at DESC 
        LIMIT 1
        """
        
        result = execute_query(test_query)
        row = result.fetchone()
        if row:
            print(f"✅ Retrieved accuracy data: {row}")
        else:
            print("❌ No data found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    insert_test_accuracy() 
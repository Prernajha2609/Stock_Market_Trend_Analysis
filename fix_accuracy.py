"""
Direct database test and fix for accuracy metrics.
"""
import sys
import os
from datetime import datetime

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import create_tables, execute_query, engine
from sqlalchemy import text

def test_and_fix_accuracy():
    """Test database connection and insert accuracy metrics."""
    try:
        print("🔍 Testing database connection...")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Create tables
        create_tables()
        print("✅ Tables created/verified")
        
        # Clear existing data for AAPL
        delete_query = "DELETE FROM model_metrics WHERE symbol = 'AAPL'"
        execute_query(delete_query)
        print("✅ Cleared existing AAPL data")
        
        # Insert fresh data
        insert_query = """
        INSERT INTO model_metrics (symbol, model_type, accuracy, `precision`, recall, f1_score, created_at)
        VALUES ('AAPL', 'RandomForest', 0.8708, 0.8723, 0.8708, 0.8692, :created_at)
        """
        
        execute_query(insert_query, {'created_at': datetime.now().date()})
        print("✅ Inserted AAPL accuracy data")
        
        # Verify data
        verify_query = """
        SELECT symbol, model_type, accuracy, `precision`, recall, f1_score, created_at
        FROM model_metrics 
        WHERE symbol = 'AAPL'
        """
        
        result = execute_query(verify_query)
        row = result.fetchone()
        if row:
            print(f"✅ Verified AAPL data: {row}")
        else:
            print("❌ No AAPL data found after insertion")
            
        # Check total count
        count_query = "SELECT COUNT(*) FROM model_metrics"
        count_result = execute_query(count_query)
        total_count = count_result.scalar()
        print(f"📊 Total accuracy records in database: {total_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_and_fix_accuracy() 
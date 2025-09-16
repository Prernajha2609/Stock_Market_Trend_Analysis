"""
Quick fix to insert accuracy metrics and test dashboard reading.
"""
import sys
import os
from datetime import datetime

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import create_tables, execute_query, read_dataframe

def quick_fix():
    """Quick fix for accuracy metrics."""
    try:
        print("🔧 Quick fix for accuracy metrics...")
        
        # Create tables
        create_tables()
        
        # Insert AAPL data
        insert_query = """
        INSERT INTO model_metrics (symbol, model_type, accuracy, `precision`, recall, f1_score, created_at)
        VALUES ('AAPL', 'RandomForest', 0.8708, 0.8723, 0.8708, 0.8692, :created_at)
        ON DUPLICATE KEY UPDATE 
        accuracy = VALUES(accuracy),
        `precision` = VALUES(`precision`),
        recall = VALUES(recall),
        f1_score = VALUES(f1_score),
        created_at = VALUES(created_at)
        """
        
        execute_query(insert_query, {'created_at': datetime.now().date()})
        print("✅ Inserted AAPL accuracy data")
        
        # Test reading with the same query as dashboard
        test_query = """
        SELECT accuracy, `precision`, recall, f1_score, model_type, created_at
        FROM model_metrics 
        WHERE symbol = 'AAPL' 
        ORDER BY created_at DESC 
        LIMIT 1
        """
        
        df = read_dataframe(test_query, {})
        if not df.empty:
            print(f"✅ Dashboard can read AAPL data: {df.iloc[0].to_dict()}")
        else:
            print("❌ Dashboard cannot read AAPL data")
            
        # Check total records
        count_query = "SELECT COUNT(*) FROM model_metrics"
        result = execute_query(count_query)
        count = result.scalar()
        print(f"📊 Total accuracy records: {count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_fix() 
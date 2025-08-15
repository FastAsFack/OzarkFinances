#!/usr/bin/env python3
"""
Test the debt report functionality after fixing the PaymentMethod column issue
"""

from app import app, db_manager
import sqlite3
from pathlib import Path

def test_debt_report():
    """Test that the debt report function works without column errors"""
    
    with app.app_context():
        try:
            print("Testing debt report functionality...")
            
            # Test debt data query
            debt_data = db_manager.execute_query("""
                SELECT DebtName, Amount, OriginalDebt, 
                       COALESCE(Category, 'Uncategorized') as Category,
                       COALESCE(DueDate, '') as DueDate,
                       COALESCE(MinimumPayment, 0) as MinimumPayment,
                       COALESCE(InterestRate, 0) as InterestRate,
                       COALESCE(AddedDate, '') as AddedDate,
                       COALESCE(Notes, '') as Notes
                FROM DebtRegister ORDER BY Amount DESC
            """)
            
            print(f"✓ Main debt query successful - found {len(debt_data)} debts")
            
            # Test individual debt database queries
            for debt in debt_data:
                debt_name = debt['DebtName']
                debt_db_path = Path(f"{debt_name}.sqlite")
                
                if debt_db_path.exists():
                    with sqlite3.connect(debt_db_path) as conn:
                        conn.row_factory = sqlite3.Row
                        payments = conn.execute("""
                            SELECT CreatedDate, Amount, PaymentMethod, Notes 
                            FROM DebtSource ORDER BY UNIX DESC LIMIT 5
                        """).fetchall()
                        
                        print(f"✓ {debt_name}: query successful - {len(payments)} payments")
                else:
                    print(f"⚠ {debt_name}: no individual database file found")
            
            print("\n🎉 All debt report tests passed! The report button should now work.")
            
        except Exception as e:
            print(f"✗ Error in debt report test: {e}")
            raise

if __name__ == "__main__":
    test_debt_report()

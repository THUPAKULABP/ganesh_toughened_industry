import sqlite3
import os

def update_invoice_items_schema():
    db_name = "ganesh_toughened_industry.db"
    
    if not os.path.exists(db_name):
        print("Database does not exist. Run the main application to create it.")
        return
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    try:
        # Check if rounded_sqft column exists in invoice_items table
        cursor.execute("PRAGMA table_info(invoice_items)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'rounded_sqft' not in columns:
            print("Adding rounded_sqft column to invoice_items table...")
            cursor.execute("ALTER TABLE invoice_items ADD COLUMN rounded_sqft REAL")
        
        conn.commit()
        print("Database schema updated successfully!")
        
    except Exception as e:
        print(f"Error updating database schema: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    update_invoice_items_schema()
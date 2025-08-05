import sqlite3
import os

def update_database_schema():
    """Update the existing database schema with missing columns"""
    db_name = "ganesh_toughened_industry.db"
    
    if not os.path.exists(db_name):
        print("Database does not exist. It will be created when you run the main application.")
        return
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    try:
        # Check if description column exists in products table
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'description' not in columns:
            print("Adding description column to products table...")
            cursor.execute("ALTER TABLE products ADD COLUMN description TEXT")
        
        # Check if email column exists in customers table
        cursor.execute("PRAGMA table_info(customers)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'email' not in columns:
            print("Adding email column to customers table...")
            cursor.execute("ALTER TABLE customers ADD COLUMN email TEXT")
        
        # Check if notes column exists in inventory table
        cursor.execute("PRAGMA table_info(inventory)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'notes' not in columns:
            print("Adding notes column to inventory table...")
            cursor.execute("ALTER TABLE inventory ADD COLUMN notes TEXT")
        
        conn.commit()
        print("Database schema updated successfully!")
        
    except Exception as e:
        print(f"Error updating database schema: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    update_database_schema()
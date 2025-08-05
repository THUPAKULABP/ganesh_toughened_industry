import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name="ganesh_toughened_industry.db"):
        self.db_name = db_name
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize the database with required tables"""
        # Check if database exists
        db_exists = os.path.exists(self.db_name)
        
        # Create connection
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        # Customers table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            place TEXT,
            phone TEXT,
            gst TEXT,
            address TEXT,
            email TEXT
        )
        """)
        
        # Products table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            description TEXT,
            rate_per_sqft REAL
        )
        """)
        
        # Invoices table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            date TEXT NOT NULL,
            invoice_number TEXT NOT NULL UNIQUE,
            subtotal REAL,
            extra_charges REAL,
            round_off REAL,
            total REAL,
            payment_mode TEXT,
            p_pay_no TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
        """)
        
        # Invoice items table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            product_id INTEGER,
            actual_height REAL,
            actual_width REAL,
            chargeable_height REAL,
            chargeable_width REAL,
            sqft REAL,
            rate REAL,
            amount REAL,
            quantity INTEGER,
            FOREIGN KEY (invoice_id) REFERENCES invoices (invoice_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
        """)
        
        # Payments table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            mode TEXT,
            reference TEXT,
            invoice_id INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
            FOREIGN KEY (invoice_id) REFERENCES invoices (invoice_id)
        )
        """)
        
        # Workers table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            worker_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            photo_path TEXT
        )
        """)
        
        # Attendance table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER,
            date TEXT NOT NULL,
            morning INTEGER DEFAULT 0,
            afternoon INTEGER DEFAULT 0,
            notes TEXT,
            FOREIGN KEY (worker_id) REFERENCES workers (worker_id),
            UNIQUE(worker_id, date)
        )
        """)
        
        # Expenses table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT
        )
        """)
        
        # Customer visits table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_visits (
            visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            name TEXT NOT NULL,
            city TEXT,
            purpose TEXT,
            date TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
        """)
        
        # Works table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS works (
            work_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            date TEXT NOT NULL,
            type TEXT,
            size TEXT,
            quantity INTEGER,
            status TEXT,
            FOREIGN KEY (invoice_id) REFERENCES invoices (invoice_id)
        )
        """)
        
        # Inventory table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            date TEXT NOT NULL,
            type TEXT,
            quantity INTEGER,
            notes TEXT,
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
        """)
        
        # Settings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)
        
        # Insert default settings if database is new
        if not db_exists:
            default_settings = [
                ("company_name", "GANESH TOUGHENED INDUSTRY"),
                ("company_address", "Plot no:B13, Industrial Estate, Madanapalli"),
                ("company_phone", "9398530499, 7013374872"),
                ("company_gst", "37EXFPK2395CIZE"),
                ("upi_id", "ganeshtoughened@ybl"),
                ("upi_name", "GANESH TOUGHENED INDUSTRY"),
                ("bank_name", "State Bank of India"),
                ("bank_account", "12345678901"),
                ("bank_ifsc", "SBIN0001234"),
                ("bank_branch", "Madanapalli")
            ]
            
            cursor.executemany("INSERT INTO settings (key, value) VALUES (?, ?)", default_settings)
            
            # Insert sample products
            sample_products = [
                ("Toughened Glass 4mm", "Glass", "4mm toughened glass", 100.0),
                ("Toughened Glass 5mm", "Glass", "5mm toughened glass", 120.0),
                ("Toughened Glass 6mm", "Glass", "6mm toughened glass", 150.0),
                ("Toughened Glass 8mm", "Glass", "8mm toughened glass", 200.0),
                ("Toughened Glass 10mm", "Glass", "10mm toughened glass", 250.0),
                ("Toughened Glass 12mm", "Glass", "12mm toughened glass", 300.0)
            ]
            
            cursor.executemany("INSERT INTO products (name, type, description, rate_per_sqft) VALUES (?, ?, ?, ?)", sample_products)
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
    
    def get_invoices(self):
        """Get all invoices from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT i.invoice_id, i.invoice_number, i.date, i.subtotal, i.extra_charges, 
                   i.round_off, i.total, i.payment_mode, i.p_pay_no, c.name as customer_name,
                   c.place as customer_place, c.phone as customer_phone, c.gst as customer_gst
            FROM invoices i
            JOIN customers c ON i.customer_id = c.customer_id
            ORDER BY i.date DESC
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            invoices = []
            for row in rows:
                invoice = {
                    "invoice_id": row[0],
                    "invoice_number": row[1],
                    "date": datetime.strptime(row[2], "%Y-%m-%d").date(),
                    "subtotal": row[3],
                    "extra_charges": row[4],
                    "round_off": row[5],
                    "total": row[6],
                    "payment_mode": row[7],
                    "p_pay_no": row[8],
                    "customer_name": row[9],
                    "customer_place": row[10],
                    "customer_phone": row[11],
                    "customer_gst": row[12]
                }
                invoices.append(invoice)
            
            conn.close()
            return invoices
        except Exception as e:
            print(f"Error getting invoices: {e}")
            return []
    
    def get_invoice_by_number(self, invoice_number):
        """Get invoice by invoice number"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT i.invoice_id, i.invoice_number, i.date, i.subtotal, i.extra_charges, 
                   i.round_off, i.total, i.payment_mode, i.p_pay_no, c.name as customer_name,
                   c.place as customer_place, c.phone as customer_phone, c.gst as customer_gst
            FROM invoices i
            JOIN customers c ON i.customer_id = c.customer_id
            WHERE i.invoice_number = ?
            """
            
            cursor.execute(query, (invoice_number,))
            row = cursor.fetchone()
            
            if row:
                invoice = {
                    "invoice_id": row[0],
                    "invoice_number": row[1],
                    "date": datetime.strptime(row[2], "%Y-%m-%d").date(),
                    "subtotal": row[3],
                    "extra_charges": row[4],
                    "round_off": row[5],
                    "total": row[6],
                    "payment_mode": row[7],
                    "p_pay_no": row[8],
                    "customer_name": row[9],
                    "customer_place": row[10],
                    "customer_phone": row[11],
                    "customer_gst": row[12]
                }
                conn.close()
                return invoice
            
            conn.close()
            return None
        except Exception as e:
            print(f"Error getting invoice by number: {e}")
            return None
    
    def get_invoice_items(self, invoice_id):
        """Get items for a specific invoice"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT ii.item_id, ii.invoice_id, ii.product_id, ii.actual_height, ii.actual_width,
                   ii.chargeable_height, ii.chargeable_width, ii.sqft, ii.rate, ii.amount, ii.quantity,
                   p.name as product_name
            FROM invoice_items ii
            JOIN products p ON ii.product_id = p.product_id
            WHERE ii.invoice_id = ?
            """
            
            cursor.execute(query, (invoice_id,))
            rows = cursor.fetchall()
            
            items = []
            for row in rows:
                item = {
                    "item_id": row[0],
                    "invoice_id": row[1],
                    "product_id": row[2],
                    "actual_height": row[3],
                    "actual_width": row[4],
                    "chargeable_height": row[5],
                    "chargeable_width": row[6],
                    "sqft": row[7],
                    "rate": row[8],
                    "amount": row[9],
                    "quantity": row[10],
                    "product_name": row[11]
                }
                items.append(item)
            
            conn.close()
            return items
        except Exception as e:
            print(f"Error getting invoice items: {e}")
            return []
    
    def search_invoices(self, customer=None, from_date=None, to_date=None):
        """Search invoices based on criteria"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT i.invoice_id, i.invoice_number, i.date, i.subtotal, i.extra_charges, 
                   i.round_off, i.total, i.payment_mode, i.p_pay_no, c.name as customer_name,
                   c.place as customer_place, c.phone as customer_phone, c.gst as customer_gst
            FROM invoices i
            JOIN customers c ON i.customer_id = c.customer_id
            WHERE 1=1
            """
            
            params = []
            
            if customer:
                query += " AND c.name LIKE ?"
                params.append(f"%{customer}%")
            
            if from_date:
                query += " AND i.date >= ?"
                params.append(from_date)
            
            if to_date:
                query += " AND i.date <= ?"
                params.append(to_date)
            
            query += " ORDER BY i.date DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            invoices = []
            for row in rows:
                invoice = {
                    "invoice_id": row[0],
                    "invoice_number": row[1],
                    "date": datetime.strptime(row[2], "%Y-%m-%d").date(),
                    "subtotal": row[3],
                    "extra_charges": row[4],
                    "round_off": row[5],
                    "total": row[6],
                    "payment_mode": row[7],
                    "p_pay_no": row[8],
                    "customer_name": row[9],
                    "customer_place": row[10],
                    "customer_phone": row[11],
                    "customer_gst": row[12]
                }
                invoices.append(invoice)
            
            conn.close()
            return invoices
        except Exception as e:
            print(f"Error searching invoices: {e}")
            return []
    
    def get_customers(self):
        """Get all customers from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = "SELECT customer_id, name, place, phone, gst, address, email FROM customers"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            customers = []
            for row in rows:
                customer = {
                    "customer_id": row[0],
                    "name": row[1],
                    "place": row[2],
                    "phone": row[3],
                    "gst": row[4],
                    "address": row[5],
                    "email": row[6]
                }
                customers.append(customer)
            
            conn.close()
            return customers
        except Exception as e:
            print(f"Error getting customers: {e}")
            return []
    
    def get_products(self):
        """Get all products from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = "SELECT product_id, name, type, description, rate_per_sqft FROM products"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            products = []
            for row in rows:
                product = {
                    "product_id": row[0],
                    "name": row[1],
                    "type": row[2],
                    "description": row[3],
                    "rate_per_sqft": row[4]
                }
                products.append(product)
            
            conn.close()
            return products
        except Exception as e:
            print(f"Error getting products: {e}")
            return []
    
    def get_setting(self, key):
        """Get a setting value by key"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = "SELECT value FROM settings WHERE key = ?"
            cursor.execute(query, (key,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return row[0]
            return None
        except Exception as e:
            print(f"Error getting setting: {e}")
            return None
    
    def generate_invoice_number(self):
        """Generate a new invoice number"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Get current year
            current_year = datetime.now().year
            
            # Get the last invoice number for this year
            query = """
            SELECT invoice_number 
            FROM invoices 
            WHERE invoice_number LIKE ?
            ORDER BY invoice_number DESC
            LIMIT 1
            """
            
            cursor.execute(query, (f"GT/{current_year}/%",))
            row = cursor.fetchone()
            
            if row:
                # Extract the sequence number from the last invoice
                last_invoice = row[0]
                last_sequence = int(last_invoice.split('/')[-1])
                new_sequence = last_sequence + 1
            else:
                # Start with sequence 1 if no invoices found for this year
                new_sequence = 1
            
            # Format the new invoice number
            new_invoice_number = f"GT/{current_year}/{new_sequence:04d}"
            
            conn.close()
            return new_invoice_number
        except Exception as e:
            print(f"Error generating invoice number: {e}")
            return f"GT/{datetime.now().year}/0001"
    
    def add_invoice(self, customer_id, date, invoice_number, subtotal, extra_charges, round_off, total, payment_mode, p_pay_no):
        """Add a new invoice to the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            INSERT INTO invoices (customer_id, date, invoice_number, subtotal, extra_charges, round_off, total, payment_mode, p_pay_no)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                customer_id, date.strftime("%Y-%m-%d"), invoice_number, 
                subtotal, extra_charges, round_off, total, payment_mode, p_pay_no
            ))
            
            invoice_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return invoice_id
        except Exception as e:
            print(f"Error adding invoice: {e}")
            return None
    
    def add_invoice_item(self, invoice_id, product_id, actual_height, actual_width, chargeable_height, chargeable_width, sqft, rate, amount, quantity):
        """Add an item to an invoice"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            INSERT INTO invoice_items (invoice_id, product_id, actual_height, actual_width, chargeable_height, chargeable_width, sqft, rate, amount, quantity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                invoice_id, product_id, actual_height, actual_width, 
                chargeable_height, chargeable_width, sqft, rate, amount, quantity
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding invoice item: {e}")
            return False
    
    def add_payment(self, customer_id, date, amount, mode, reference, invoice_id=None):
        """Add a payment to the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            INSERT INTO payments (customer_id, date, amount, mode, reference, invoice_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                customer_id, date.strftime("%Y-%m-%d"), amount, mode, reference, invoice_id
            ))
            
            payment_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return payment_id
        except Exception as e:
            print(f"Error adding payment: {e}")
            return None
    
    def add_visit(self, customer_id, name, city, purpose, date_time=None):
        """Add a customer visit to the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Use current date and time if not provided
            if date_time is None:
                date_time = datetime.now()
            
            query = """
            INSERT INTO customer_visits (customer_id, name, city, purpose, date)
            VALUES (?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                customer_id, name, city, purpose, date_time.strftime("%Y-%m-%d")
            ))
            
            visit_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return visit_id
        except Exception as e:
            print(f"Error adding customer visit: {e}")
            return None
    
    def add_work(self, invoice_id, date, type, size, quantity, status):
        """Add a work record to the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            INSERT INTO works (invoice_id, date, type, size, quantity, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                invoice_id, date.strftime("%Y-%m-%d"), type, size, quantity, status
            ))
            
            work_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return work_id
        except Exception as e:
            print(f"Error adding work record: {e}")
            return None
    
    def add_inventory(self, product_id, date, type, quantity, notes=None):
        """Add an inventory record to the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            INSERT INTO inventory (product_id, date, type, quantity, notes)
            VALUES (?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                product_id, date.strftime("%Y-%m-%d"), type, quantity, notes
            ))
            
            inventory_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return inventory_id
        except Exception as e:
            print(f"Error adding inventory record: {e}")
            return None
    
    def add_customer(self, name, place=None, phone=None, gst=None, address=None, email=None):
        """Add a new customer to the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            INSERT INTO customers (name, place, phone, gst, address, email)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (name, place, phone, gst, address, email))
            
            customer_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return customer_id
        except Exception as e:
            print(f"Error adding customer: {e}")
            return None
    
    def get_workers(self):
        """Get all workers from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = "SELECT worker_id, name, phone, photo_path FROM workers"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            workers = []
            for row in rows:
                worker = {
                    "worker_id": row[0],
                    "name": row[1],
                    "phone": row[2],
                    "photo_path": row[3]
                }
                workers.append(worker)
            
            conn.close()
            return workers
        except Exception as e:
            print(f"Error getting workers: {e}")
            return []
    
    def add_worker(self, name, phone=None, photo_path=None):
        """Add a new worker to the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            INSERT INTO workers (name, phone, photo_path)
            VALUES (?, ?, ?)
            """
            
            cursor.execute(query, (name, phone, photo_path))
            
            worker_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return worker_id
        except Exception as e:
            print(f"Error adding worker: {e}")
            return None
    
    def update_worker(self, worker_id, name, phone=None, photo_path=None):
        """Update worker in the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            UPDATE workers SET name = ?, phone = ?, photo_path = ?
            WHERE worker_id = ?
            """
            
            cursor.execute(query, (name, phone, photo_path, worker_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating worker: {e}")
            return False
    
    def delete_worker(self, worker_id):
        """Delete worker from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Delete attendance records first
            cursor.execute("DELETE FROM attendance WHERE worker_id = ?", (worker_id,))
            
            # Delete worker
            cursor.execute("DELETE FROM workers WHERE worker_id = ?", (worker_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting worker: {e}")
            return False
    
    def get_attendance(self, worker_id, date):
        """Get attendance for a worker on a specific date"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT attendance_id, worker_id, date, morning, afternoon, notes
            FROM attendance
            WHERE worker_id = ? AND date = ?
            """
            
            cursor.execute(query, (worker_id, date.strftime("%Y-%m-%d")))
            row = cursor.fetchone()
            
            if row:
                attendance = {
                    "attendance_id": row[0],
                    "worker_id": row[1],
                    "date": datetime.strptime(row[2], "%Y-%m-%d").date(),
                    "morning": bool(row[3]),
                    "afternoon": bool(row[4]),
                    "notes": row[5]
                }
                conn.close()
                return attendance
            
            conn.close()
            return None
        except Exception as e:
            print(f"Error getting attendance: {e}")
            return None
    
    def get_attendance_by_worker(self, worker_id, start_date, end_date):
        """Get attendance for a worker within a date range"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT attendance_id, worker_id, date, morning, afternoon, notes
            FROM attendance
            WHERE worker_id = ? AND date >= ? AND date <= ?
            ORDER BY date
            """
            
            cursor.execute(query, (worker_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            rows = cursor.fetchall()
            
            attendance_list = []
            for row in rows:
                attendance = {
                    "attendance_id": row[0],
                    "worker_id": row[1],
                    "date": datetime.strptime(row[2], "%Y-%m-%d").date(),
                    "morning": bool(row[3]),
                    "afternoon": bool(row[4]),
                    "notes": row[5]
                }
                attendance_list.append(attendance)
            
            conn.close()
            return attendance_list
        except Exception as e:
            print(f"Error getting attendance by worker: {e}")
            return []
    
    def add_attendance(self, worker_id, date, morning=False, afternoon=False, notes=None):
        """Add or update attendance for a worker"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Check if attendance already exists
            existing = self.get_attendance(worker_id, date)
            
            if existing:
                # Update existing record
                query = """
                UPDATE attendance SET morning = ?, afternoon = ?, notes = ?
                WHERE worker_id = ? AND date = ?
                """
                cursor.execute(query, (morning, afternoon, notes, worker_id, date.strftime("%Y-%m-%d")))
            else:
                # Insert new record
                query = """
                INSERT INTO attendance (worker_id, date, morning, afternoon, notes)
                VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(query, (worker_id, date.strftime("%Y-%m-%d"), morning, afternoon, notes))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding attendance: {e}")
            return False
    
    def get_attendance_by_date(self, date):
        """Get attendance for all workers on a specific date"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT a.attendance_id, a.worker_id, a.date, a.morning, a.afternoon, a.notes, w.name as worker_name
            FROM attendance a
            JOIN workers w ON a.worker_id = w.worker_id
            WHERE a.date = ?
            ORDER BY w.name
            """
            
            cursor.execute(query, (date.strftime("%Y-%m-%d"),))
            rows = cursor.fetchall()
            
            attendance_list = []
            for row in rows:
                attendance = {
                    "attendance_id": row[0],
                    "worker_id": row[1],
                    "date": datetime.strptime(row[2], "%Y-%m-%d").date(),
                    "morning": bool(row[3]),
                    "afternoon": bool(row[4]),
                    "notes": row[5],
                    "worker_name": row[6]
                }
                attendance_list.append(attendance)
            
            conn.close()
            return attendance_list
        except Exception as e:
            print(f"Error getting attendance by date: {e}")
            return []
    
    def get_expenses(self, start_date=None, end_date=None, category=None):
        """Get expenses with optional filters"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = "SELECT expense_id, date, description, amount, category FROM expenses WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date.strftime("%Y-%m-%d"))
            
            if end_date:
                query += " AND date <= ?"
                params.append(end_date.strftime("%Y-%m-%d"))
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY date DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            expenses = []
            for row in rows:
                expense = {
                    "expense_id": row[0],
                    "date": datetime.strptime(row[1], "%Y-%m-%d").date(),
                    "description": row[2],
                    "amount": row[3],
                    "category": row[4]
                }
                expenses.append(expense)
            
            conn.close()
            return expenses
        except Exception as e:
            print(f"Error getting expenses: {e}")
            return []
    
    def add_expense(self, date, description, amount, category=None):
        """Add an expense to the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            INSERT INTO expenses (date, description, amount, category)
            VALUES (?, ?, ?, ?)
            """
            
            cursor.execute(query, (date.strftime("%Y-%m-%d"), description, amount, category))
            
            expense_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return expense_id
        except Exception as e:
            print(f"Error adding expense: {e}")
            return None
    
    def get_visits(self, start_date=None, end_date=None, customer_id=None):
        """Get customer visits with optional filters"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT v.visit_id, v.customer_id, v.name, v.city, v.date, v.purpose, c.name as customer_name
            FROM customer_visits v
            LEFT JOIN customers c ON v.customer_id = c.customer_id
            WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND v.date >= ?"
                params.append(start_date.strftime("%Y-%m-%d"))
            
            if end_date:
                query += " AND v.date <= ?"
                params.append(end_date.strftime("%Y-%m-%d"))
            
            if customer_id:
                query += " AND v.customer_id = ?"
                params.append(customer_id)
            
            query += " ORDER BY v.date DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            visits = []
            for row in rows:
                visit = {
                    "visit_id": row[0],
                    "customer_id": row[1],
                    "name": row[2],
                    "city": row[3],
                    "date": datetime.strptime(row[4], "%Y-%m-%d").date(),
                    "purpose": row[5],
                    "customer_name": row[6] if row[6] else row[2]
                }
                visits.append(visit)
            
            conn.close()
            return visits
        except Exception as e:
            print(f"Error getting visits: {e}")
            return []
    
    def get_works(self, start_date=None, end_date=None, status=None):
        """Get work records with optional filters"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = "SELECT work_id, invoice_id, date, type, size, quantity, status FROM works WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date.strftime("%Y-%m-%d"))
            
            if end_date:
                query += " AND date <= ?"
                params.append(end_date.strftime("%Y-%m-%d"))
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY date DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            works = []
            for row in rows:
                work = {
                    "work_id": row[0],
                    "invoice_id": row[1],
                    "date": datetime.strptime(row[2], "%Y-%m-%d").date(),
                    "type": row[3],
                    "size": row[4],
                    "quantity": row[5],
                    "status": row[6]
                }
                works.append(work)
            
            conn.close()
            return works
        except Exception as e:
            print(f"Error getting works: {e}")
            return []
    
    def update_work_status(self, work_id, status):
        """Update work status"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = "UPDATE works SET status = ? WHERE work_id = ?"
            cursor.execute(query, (status, work_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating work status: {e}")
            return False
    
    def get_current_inventory(self):
        """Get current inventory status for all products"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT p.product_id, p.name, p.type,
                   COALESCE(SUM(CASE WHEN i.type = 'stock_in' THEN i.quantity ELSE 0 END), 0) as stock_in,
                   COALESCE(SUM(CASE WHEN i.type = 'stock_out' THEN i.quantity ELSE 0 END), 0) as stock_out,
                   COALESCE(SUM(CASE WHEN i.type = 'stock_in' THEN i.quantity ELSE 0 END), 0) - 
                   COALESCE(SUM(CASE WHEN i.type = 'stock_out' THEN i.quantity ELSE 0 END), 0) as current_stock
            FROM products p
            LEFT JOIN inventory i ON p.product_id = i.product_id
            GROUP BY p.product_id
            ORDER BY p.type, p.name
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            inventory = []
            for row in rows:
                item = {
                    "product_id": row[0],
                    "name": row[1],
                    "type": row[2],
                    "stock_in": row[3],
                    "stock_out": row[4],
                    "current_stock": row[5]
                }
                inventory.append(item)
            
            conn.close()
            return inventory
        except Exception as e:
            print(f"Error getting current inventory: {e}")
            return []
    
    def get_daily_inventory(self, date):
        """Get inventory movements for a specific date"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT i.inventory_id, i.product_id, i.date, i.type, i.quantity, i.notes, p.name as product_name
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            WHERE i.date = ?
            ORDER BY i.type, p.name
            """
            
            cursor.execute(query, (date.strftime("%Y-%m-%d"),))
            rows = cursor.fetchall()
            
            inventory = []
            for row in rows:
                item = {
                    "inventory_id": row[0],
                    "product_id": row[1],
                    "date": datetime.strptime(row[2], "%Y-%m-%d").date(),
                    "type": row[3],
                    "quantity": row[4],
                    "notes": row[5],
                    "product_name": row[6]
                }
                inventory.append(item)
            
            conn.close()
            return inventory
        except Exception as e:
            print(f"Error getting daily inventory: {e}")
            return []
    
    def get_payments_by_customer(self, customer_id):
        """Get all payments for a customer"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT payment_id, date, amount, mode, reference, invoice_id
            FROM payments
            WHERE customer_id = ?
            ORDER BY date DESC
            """
            
            cursor.execute(query, (customer_id,))
            rows = cursor.fetchall()
            
            payments = []
            for row in rows:
                payment = {
                    "payment_id": row[0],
                    "date": datetime.strptime(row[1], "%Y-%m-%d").date(),
                    "amount": row[2],
                    "mode": row[3],
                    "reference": row[4],
                    "invoice_id": row[5]
                }
                payments.append(payment)
            
            conn.close()
            return payments
        except Exception as e:
            print(f"Error getting payments by customer: {e}")
            return []
    
    def get_customer_outstanding(self, customer_id=None):
        """Get outstanding balance for customers"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if customer_id:
                # Get outstanding for a specific customer
                query = """
                SELECT c.customer_id, c.name, 
                       COALESCE(SUM(i.total), 0) as total_invoices,
                       COALESCE(SUM(p.amount), 0) as total_payments,
                       COALESCE(SUM(i.total), 0) - COALESCE(SUM(p.amount), 0) as outstanding
                FROM customers c
                LEFT JOIN invoices i ON c.customer_id = i.customer_id
                LEFT JOIN payments p ON c.customer_id = p.customer_id
                WHERE c.customer_id = ?
                GROUP BY c.customer_id
                """
                cursor.execute(query, (customer_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "customer_id": row[0],
                        "name": row[1],
                        "total_invoices": row[2],
                        "total_payments": row[3],
                        "outstanding": row[4]
                    }
                return None
            else:
                # Get outstanding for all customers
                query = """
                SELECT c.customer_id, c.name, 
                       COALESCE(SUM(i.total), 0) as total_invoices,
                       COALESCE(SUM(p.amount), 0) as total_payments,
                       COALESCE(SUM(i.total), 0) - COALESCE(SUM(p.amount), 0) as outstanding
                FROM customers c
                LEFT JOIN invoices i ON c.customer_id = i.customer_id
                LEFT JOIN payments p ON c.customer_id = p.customer_id
                GROUP BY c.customer_id
                HAVING outstanding > 0
                ORDER BY outstanding DESC
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                
                outstanding_list = []
                for row in rows:
                    outstanding_list.append({
                        "customer_id": row[0],
                        "name": row[1],
                        "total_invoices": row[2],
                        "total_payments": row[3],
                        "outstanding": row[4]
                    })
                
                conn.close()
                return outstanding_list
        except Exception as e:
            print(f"Error getting customer outstanding: {e}")
            return [] if customer_id is None else None
    
    def get_invoices_by_customer(self, customer_id):
        """Get all invoices for a specific customer"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT i.invoice_id, i.invoice_number, i.date, i.subtotal, i.extra_charges, 
                   i.round_off, i.total, i.payment_mode, i.p_pay_no
            FROM invoices i
            WHERE i.customer_id = ?
            ORDER BY i.date DESC
            """
            
            cursor.execute(query, (customer_id,))
            rows = cursor.fetchall()
            
            invoices = []
            for row in rows:
                invoices.append({
                    "invoice_id": row[0],
                    "invoice_number": row[1],
                    "date": datetime.strptime(row[2], "%Y-%m-%d").date(),
                    "subtotal": row[3],
                    "extra_charges": row[4],
                    "round_off": row[5],
                    "total": row[6],
                    "payment_mode": row[7],
                    "p_pay_no": row[8]
                })
            
            conn.close()
            return invoices
        except Exception as e:
            print(f"Error getting invoices by customer: {e}")
            return []
import sqlite3
import os
from datetime import datetime, date

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
    
    def add_product(self, name, type, description, rate_per_sqft):
        """Add a new product to the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            INSERT INTO products (name, type, description, rate_per_sqft)
            VALUES (?, ?, ?, ?)
            """
            
            cursor.execute(query, (name, type, description, rate_per_sqft))
            
            product_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return product_id
        except Exception as e:
            print(f"Error adding product: {e}")
            return None
    
    def add_expense(self, date, description, amount, category):
        """Add a new expense to the database"""
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
    
    def add_attendance(self, worker_id, date, morning, afternoon, notes=None):
        """Add attendance record to the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            INSERT OR REPLACE INTO attendance (worker_id, date, morning, afternoon, notes)
            VALUES (?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (worker_id, date.strftime("%Y-%m-%d"), morning, afternoon, notes))
            
            attendance_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return attendance_id
        except Exception as e:
            print(f"Error adding attendance: {e}")
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
    
    def get_attendance(self, date=None):
        """Get attendance records from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if date:
                query = """
                SELECT a.attendance_id, a.worker_id, a.date, a.morning, a.afternoon, a.notes, w.name as worker_name
                FROM attendance a
                JOIN workers w ON a.worker_id = w.worker_id
                WHERE a.date = ?
                ORDER BY w.name
                """
                cursor.execute(query, (date.strftime("%Y-%m-%d"),))
            else:
                query = """
                SELECT a.attendance_id, a.worker_id, a.date, a.morning, a.afternoon, a.notes, w.name as worker_name
                FROM attendance a
                JOIN workers w ON a.worker_id = w.worker_id
                ORDER BY a.date DESC, w.name
                """
                cursor.execute(query)
            
            rows = cursor.fetchall()
            
            attendance_records = []
            for row in rows:
                record = {
                    "attendance_id": row[0],
                    "worker_id": row[1],
                    "date": datetime.strptime(row[2], "%Y-%m-%d").date(),
                    "morning": row[3],
                    "afternoon": row[4],
                    "notes": row[5],
                    "worker_name": row[6]
                }
                attendance_records.append(record)
            
            conn.close()
            return attendance_records
        except Exception as e:
            print(f"Error getting attendance: {e}")
            return []
    
    def get_attendance_by_worker(self, worker_id, from_date=None, to_date=None):
        """Get attendance records for a specific worker"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT attendance_id, worker_id, date, morning, afternoon, notes
            FROM attendance
            WHERE worker_id = ?
            """
            
            params = [worker_id]
            
            if from_date:
                query += " AND date >= ?"
                params.append(from_date.strftime("%Y-%m-%d"))
            
            if to_date:
                query += " AND date <= ?"
                params.append(to_date.strftime("%Y-%m-%d"))
            
            query += " ORDER BY date DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            attendance_records = []
            for row in rows:
                record = {
                    "attendance_id": row[0],
                    "worker_id": row[1],
                    "date": datetime.strptime(row[2], "%Y-%m-%d").date(),
                    "morning": row[3],
                    "afternoon": row[4],
                    "notes": row[5]
                }
                attendance_records.append(record)
            
            conn.close()
            return attendance_records
        except Exception as e:
            print(f"Error getting attendance by worker: {e}")
            return []
    
    def get_expenses(self, from_date=None, to_date=None, category=None):
        """Get expenses from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = "SELECT expense_id, date, description, amount, category FROM expenses WHERE 1=1"
            params = []
            
            if from_date:
                query += " AND date >= ?"
                params.append(from_date.strftime("%Y-%m-%d"))
            
            if to_date:
                query += " AND date <= ?"
                params.append(to_date.strftime("%Y-%m-%d"))
            
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
    
    def get_visits(self, from_date=None, to_date=None, customer=None):
        """Get customer visits from the database"""
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
            
            if from_date:
                query += " AND v.date >= ?"
                params.append(from_date.strftime("%Y-%m-%d"))
            
            if to_date:
                query += " AND v.date <= ?"
                params.append(to_date.strftime("%Y-%m-%d"))
            
            if customer:
                query += " AND (v.name LIKE ? OR c.name LIKE ?)"
                params.append(f"%{customer}%")
                params.append(f"%{customer}%")
            
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
    
    def get_works(self, from_date=None, to_date=None, status=None):
        """Get works from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT w.work_id, w.invoice_id, w.date, w.type, w.size, w.quantity, w.status, i.invoice_number
            FROM works w
            LEFT JOIN invoices i ON w.invoice_id = i.invoice_id
            WHERE 1=1
            """
            
            params = []
            
            if from_date:
                query += " AND w.date >= ?"
                params.append(from_date.strftime("%Y-%m-%d"))
            
            if to_date:
                query += " AND w.date <= ?"
                params.append(to_date.strftime("%Y-%m-%d"))
            
            if status:
                query += " AND w.status = ?"
                params.append(status)
            
            query += " ORDER BY w.date DESC"
            
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
                    "status": row[6],
                    "invoice_number": row[7]
                }
                works.append(work)
            
            conn.close()
            return works
        except Exception as e:
            print(f"Error getting works: {e}")
            return []
    
    def get_current_inventory(self):
        """Get current inventory status"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT p.product_id, p.name, p.type, p.description, p.rate_per_sqft,
                   SUM(CASE WHEN i.type = 'IN' THEN i.quantity ELSE -i.quantity END) as current_quantity
            FROM products p
            LEFT JOIN inventory i ON p.product_id = i.product_id
            GROUP BY p.product_id
            ORDER BY p.name
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            inventory = []
            for row in rows:
                item = {
                    "product_id": row[0],
                    "name": row[1],
                    "type": row[2],
                    "description": row[3],
                    "rate_per_sqft": row[4],
                    "current_quantity": row[5] if row[5] else 0
                }
                inventory.append(item)
            
            conn.close()
            return inventory
        except Exception as e:
            print(f"Error getting current inventory: {e}")
            return []
    
    def get_daily_inventory(self, date=None):
        """Get daily inventory movements"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if date:
                query = """
                SELECT i.inventory_id, i.product_id, i.date, i.type, i.quantity, i.notes, p.name as product_name
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                WHERE i.date = ?
                ORDER BY i.inventory_id DESC
                """
                cursor.execute(query, (date.strftime("%Y-%m-%d"),))
            else:
                query = """
                SELECT i.inventory_id, i.product_id, i.date, i.type, i.quantity, i.notes, p.name as product_name
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                ORDER BY i.date DESC, i.inventory_id DESC
                """
                cursor.execute(query)
            
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
        """Get payments for a specific customer"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            SELECT p.payment_id, p.date, p.amount, p.mode, p.reference, p.invoice_id, i.invoice_number
            FROM payments p
            LEFT JOIN invoices i ON p.invoice_id = i.invoice_id
            WHERE p.customer_id = ?
            ORDER BY p.date DESC
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
                    "invoice_id": row[5],
                    "invoice_number": row[6]
                }
                payments.append(payment)
            
            conn.close()
            return payments
        except Exception as e:
            print(f"Error getting payments by customer: {e}")
            return []
    
    def update_setting(self, key, value):
        """Update a setting value"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)"
            cursor.execute(query, (key, value))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating setting: {e}")
            return False
    
    def update_customer(self, customer_id, name, place, phone, gst, address, email):
        """Update customer information"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            UPDATE customers
            SET name = ?, place = ?, phone = ?, gst = ?, address = ?, email = ?
            WHERE customer_id = ?
            """
            
            cursor.execute(query, (name, place, phone, gst, address, email, customer_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating customer: {e}")
            return False
    
    def update_product(self, product_id, name, type, description, rate_per_sqft):
        """Update product information"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            UPDATE products
            SET name = ?, type = ?, description = ?, rate_per_sqft = ?
            WHERE product_id = ?
            """
            
            cursor.execute(query, (name, type, description, rate_per_sqft, product_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating product: {e}")
            return False
    
    def update_worker(self, worker_id, name, phone, photo_path):
        """Update worker information"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = """
            UPDATE workers
            SET name = ?, phone = ?, photo_path = ?
            WHERE worker_id = ?
            """
            
            cursor.execute(query, (name, phone, photo_path, worker_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating worker: {e}")
            return False
    
    def delete_customer(self, customer_id):
        """Delete a customer from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # First, check if customer has invoices
            cursor.execute("SELECT COUNT(*) FROM invoices WHERE customer_id = ?", (customer_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                conn.close()
                return False  # Cannot delete customer with invoices
            
            # Delete the customer
            cursor.execute("DELETE FROM customers WHERE customer_id = ?", (customer_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting customer: {e}")
            return False
    
    def delete_product(self, product_id):
        """Delete a product from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # First, check if product is used in invoices
            cursor.execute("SELECT COUNT(*) FROM invoice_items WHERE product_id = ?", (product_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                conn.close()
                return False  # Cannot delete product used in invoices
            
            # Delete the product
            cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False
    
    def delete_worker(self, worker_id):
        """Delete a worker from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # First, check if worker has attendance records
            cursor.execute("SELECT COUNT(*) FROM attendance WHERE worker_id = ?", (worker_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                conn.close()
                return False  # Cannot delete worker with attendance records
            
            # Delete the worker
            cursor.execute("DELETE FROM workers WHERE worker_id = ?", (worker_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting worker: {e}")
            return False
    
    def delete_expense(self, expense_id):
        """Delete an expense from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM expenses WHERE expense_id = ?", (expense_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting expense: {e}")
            return False
    
    def delete_visit(self, visit_id):
        """Delete a visit from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM customer_visits WHERE visit_id = ?", (visit_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting visit: {e}")
            return False
    
    def delete_work(self, work_id):
        """Delete a work from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM works WHERE work_id = ?", (work_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting work: {e}")
            return False
    
    def get_customer_balance(self, customer_id):
        """Get customer balance (total invoice amount - total payments)"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Get total invoice amount
            cursor.execute("SELECT SUM(total) FROM invoices WHERE customer_id = ?", (customer_id,))
            invoice_total = cursor.fetchone()[0] or 0
            
            # Get total payments
            cursor.execute("SELECT SUM(amount) FROM payments WHERE customer_id = ?", (customer_id,))
            payment_total = cursor.fetchone()[0] or 0
            
            balance = invoice_total - payment_total
            
            conn.close()
            return balance
        except Exception as e:
            print(f"Error getting customer balance: {e}")
            return 0
    
    def get_monthly_summary(self, year, month):
        """Get monthly summary of invoices and payments"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Get invoice total for the month
            cursor.execute("""
            SELECT SUM(total) 
            FROM invoices 
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            """, (str(year), str(month).zfill(2)))
            
            invoice_total = cursor.fetchone()[0] or 0
            
            # Get payment total for the month
            cursor.execute("""
            SELECT SUM(amount) 
            FROM payments 
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            """, (str(year), str(month).zfill(2)))
            
            payment_total = cursor.fetchone()[0] or 0
            
            # Get expense total for the month
            cursor.execute("""
            SELECT SUM(amount) 
            FROM expenses 
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            """, (str(year), str(month).zfill(2)))
            
            expense_total = cursor.fetchone()[0] or 0
            
            summary = {
                "invoice_total": invoice_total,
                "payment_total": payment_total,
                "expense_total": expense_total,
                "net_profit": invoice_total - expense_total
            }
            
            conn.close()
            return summary
        except Exception as e:
            print(f"Error getting monthly summary: {e}")
            return {
                "invoice_total": 0,
                "payment_total": 0,
                "expense_total": 0,
                "net_profit": 0
            }
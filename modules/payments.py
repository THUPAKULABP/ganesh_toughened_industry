import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import calendar

class PaymentsModule:
    def __init__(self, parent, db, app):
        self.parent = parent
        self.db = db
        self.app = app
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """Create the payments UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="PAYMENTS MODULE", style="Title.TLabel")
        title.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        incoming_tab = ttk.Frame(notebook)
        outgoing_tab = ttk.Frame(notebook)
        summary_tab = ttk.Frame(notebook)
        
        notebook.add(incoming_tab, text="Incoming Payments")
        notebook.add(outgoing_tab, text="Outgoing Payments")
        notebook.add(summary_tab, text="Payment Summary")
        
        # Create incoming payments tab
        self.create_incoming_tab(incoming_tab)
        
        # Create outgoing payments tab
        self.create_outgoing_tab(outgoing_tab)
        
        # Create payment summary tab
        self.create_summary_tab(summary_tab)
    
    def create_incoming_tab(self, parent):
        """Create the incoming payments tab"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Filter frame
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Customer filter
        ttk.Label(filter_frame, text="Customer:").pack(side=tk.LEFT, padx=5)
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(filter_frame, textvariable=self.customer_var)
        self.customer_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Date range
        ttk.Label(filter_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.from_date_var = tk.StringVar(value=(date.today() - timedelta(days=30)).strftime("%d/%m/%Y"))
        ttk.Entry(filter_frame, textvariable=self.from_date_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.to_date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(filter_frame, textvariable=self.to_date_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Payment mode filter
        ttk.Label(filter_frame, text="Mode:").pack(side=tk.LEFT, padx=5)
        self.mode_var = tk.StringVar()
        payment_modes = ["All", "Cash", "UPI", "NEFT", "Cheque", "Other"]
        mode_combo = ttk.Combobox(filter_frame, textvariable=self.mode_var, values=payment_modes, state="readonly")
        mode_combo.pack(side=tk.LEFT, padx=5)
        
        # Search button
        search_btn = ttk.Button(filter_frame, text="Search", command=self.search_incoming_payments)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Add payment button
        add_btn = ttk.Button(filter_frame, text="Add Payment", command=self.add_payment)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Minus payment button (for advance payments)
        minus_btn = ttk.Button(filter_frame, text="Minus Payment", command=self.minus_payment)
        minus_btn.pack(side=tk.LEFT, padx=5)
        
        # Edit payment button
        edit_btn = ttk.Button(filter_frame, text="Edit Payment", command=self.edit_payment)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete payment button
        delete_btn = ttk.Button(filter_frame, text="Delete Payment", command=self.delete_payment)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Payments display
        payments_frame = ttk.Frame(main_frame)
        payments_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Payments treeview
        self.incoming_tree = ttk.Treeview(payments_frame, columns=("id", "date", "customer", "amount", "mode", "reference", "notes"), show="headings")
        self.incoming_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        self.incoming_tree.heading("id", text="ID")
        self.incoming_tree.heading("date", text="Date")
        self.incoming_tree.heading("customer", text="Customer")
        self.incoming_tree.heading("amount", text="Amount")
        self.incoming_tree.heading("mode", text="Mode")
        self.incoming_tree.heading("reference", text="Reference")
        self.incoming_tree.heading("notes", text="Notes")
        
        # Define columns
        self.incoming_tree.column("id", width=0, stretch=False)  # Hidden column
        self.incoming_tree.column("date", width=100)
        self.incoming_tree.column("customer", width=150)
        self.incoming_tree.column("amount", width=100)
        self.incoming_tree.column("mode", width=100)
        self.incoming_tree.column("reference", width=100)
        self.incoming_tree.column("notes", width=150)
        
        # Hide the ID column
        self.incoming_tree.column("id", minwidth=0, width=0, stretch=False)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(payments_frame, orient=tk.VERTICAL, command=self.incoming_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.incoming_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click to view details
        self.incoming_tree.bind("<Double-1>", self.view_payment_details)
        
        # Bind Delete key to delete payment
        self.incoming_tree.bind("<Delete>", lambda e: self.delete_payment())
        
        # Summary frame
        summary_frame = ttk.Frame(main_frame)
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Total amount
        total_frame = ttk.Frame(summary_frame)
        total_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(total_frame, text="Total Amount:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.incoming_total_var = tk.StringVar(value="0.00")
        ttk.Label(total_frame, textvariable=self.incoming_total_var, font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
        
        # Load customers
        self.load_customers()
        
        # Load initial payments
        self.search_incoming_payments()
    
    def create_outgoing_tab(self, parent):
        """Create the outgoing payments tab"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Filter frame
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Category filter
        ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT, padx=5)
        self.category_var = tk.StringVar()
        categories = ["All", "Salary", "Rent", "Material", "Utilities", "Maintenance", "Other"]
        category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var, values=categories, state="readonly")
        category_combo.pack(side=tk.LEFT, padx=5)
        
        # Date range
        ttk.Label(filter_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.exp_from_date_var = tk.StringVar(value=(date.today() - timedelta(days=30)).strftime("%d/%m/%Y"))
        ttk.Entry(filter_frame, textvariable=self.exp_from_date_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.exp_to_date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(filter_frame, textvariable=self.exp_to_date_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Search button
        search_btn = ttk.Button(filter_frame, text="Search", command=self.search_outgoing_payments)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Add expense button
        add_btn = ttk.Button(filter_frame, text="Add Expense", command=self.add_expense)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Edit expense button
        edit_btn = ttk.Button(filter_frame, text="Edit Expense", command=self.edit_expense)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete expense button
        delete_btn = ttk.Button(filter_frame, text="Delete Expense", command=self.delete_expense)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Expenses display
        expenses_frame = ttk.Frame(main_frame)
        expenses_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Expenses treeview
        self.outgoing_tree = ttk.Treeview(expenses_frame, columns=("id", "date", "description", "amount", "category", "notes"), show="headings")
        self.outgoing_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        self.outgoing_tree.heading("id", text="ID")
        self.outgoing_tree.heading("date", text="Date")
        self.outgoing_tree.heading("description", text="Description")
        self.outgoing_tree.heading("amount", text="Amount")
        self.outgoing_tree.heading("category", text="Category")
        self.outgoing_tree.heading("notes", text="Notes")
        
        # Define columns
        self.outgoing_tree.column("id", width=0, stretch=False)  # Hidden column
        self.outgoing_tree.column("date", width=100)
        self.outgoing_tree.column("description", width=200)
        self.outgoing_tree.column("amount", width=100)
        self.outgoing_tree.column("category", width=100)
        self.outgoing_tree.column("notes", width=150)
        
        # Hide the ID column
        self.outgoing_tree.column("id", minwidth=0, width=0, stretch=False)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(expenses_frame, orient=tk.VERTICAL, command=self.outgoing_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.outgoing_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click to view details
        self.outgoing_tree.bind("<Double-1>", self.view_expense_details)
        
        # Bind Delete key to delete expense
        self.outgoing_tree.bind("<Delete>", lambda e: self.delete_expense())
        
        # Summary frame
        summary_frame = ttk.Frame(main_frame)
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Total amount
        total_frame = ttk.Frame(summary_frame)
        total_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(total_frame, text="Total Amount:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.outgoing_total_var = tk.StringVar(value="0.00")
        ttk.Label(total_frame, textvariable=self.outgoing_total_var, font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
        
        # Load initial expenses
        self.search_outgoing_payments()
    
    def create_summary_tab(self, parent):
        """Create the payment summary tab"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Date range
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(date_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.sum_from_date_var = tk.StringVar(value=(date.today() - timedelta(days=30)).strftime("%d/%m/%Y"))
        ttk.Entry(date_frame, textvariable=self.sum_from_date_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.sum_to_date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(date_frame, textvariable=self.sum_to_date_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Load button
        load_btn = ttk.Button(date_frame, text="Load Summary", command=self.load_summary)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        # Summary display
        summary_frame = ttk.Frame(main_frame)
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for summary sections
        summary_notebook = ttk.Notebook(summary_frame)
        summary_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Overall summary tab
        overall_tab = ttk.Frame(summary_notebook)
        summary_notebook.add(overall_tab, text="Overall Summary")
        
        # Customer-wise summary tab
        customer_tab = ttk.Frame(summary_notebook)
        summary_notebook.add(customer_tab, text="Customer-wise")
        
        # Category-wise summary tab
        category_tab = ttk.Frame(summary_notebook)
        summary_notebook.add(category_tab, text="Category-wise")
        
        # Create overall summary UI
        self.create_overall_summary(overall_tab)
        
        # Create customer-wise summary UI
        self.create_customer_summary(customer_tab)
        
        # Create category-wise summary UI
        self.create_category_summary(category_tab)
        
        # Load initial summary
        self.load_summary()
    
    def create_overall_summary(self, parent):
        """Create the overall summary UI"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Summary frame
        summary_frame = ttk.LabelFrame(main_frame, text="Payment Summary")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Incoming payments
        incoming_frame = ttk.Frame(summary_frame)
        incoming_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(incoming_frame, text="Total Incoming Payments:").pack(side=tk.LEFT)
        self.total_incoming_var = tk.StringVar(value="0.00")
        ttk.Label(incoming_frame, textvariable=self.total_incoming_var).pack(side=tk.RIGHT)
        
        # Outgoing payments
        outgoing_frame = ttk.Frame(summary_frame)
        outgoing_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(outgoing_frame, text="Total Outgoing Payments:").pack(side=tk.LEFT)
        self.total_outgoing_var = tk.StringVar(value="0.00")
        ttk.Label(outgoing_frame, textvariable=self.total_outgoing_var).pack(side=tk.RIGHT)
        
        # Net amount
        net_frame = ttk.Frame(summary_frame)
        net_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(net_frame, text="Net Amount:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.net_amount_var = tk.StringVar(value="0.00")
        ttk.Label(net_frame, textvariable=self.net_amount_var, font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
    
    def create_customer_summary(self, parent):
        """Create the customer-wise summary UI"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Customer summary treeview
        self.customer_summary_tree = ttk.Treeview(main_frame, columns=("customer", "total_invoices", "total_payments", "outstanding"), show="headings")
        self.customer_summary_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        self.customer_summary_tree.heading("customer", text="Customer")
        self.customer_summary_tree.heading("total_invoices", text="Total Invoices")
        self.customer_summary_tree.heading("total_payments", text="Total Payments")
        self.customer_summary_tree.heading("outstanding", text="Outstanding")
        
        # Define columns
        self.customer_summary_tree.column("customer", width=150)
        self.customer_summary_tree.column("total_invoices", width=120)
        self.customer_summary_tree.column("total_payments", width=120)
        self.customer_summary_tree.column("outstanding", width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.customer_summary_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.customer_summary_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click to view details
        self.customer_summary_tree.bind("<Double-1>", self.view_customer_payment_details)
    
    def create_category_summary(self, parent):
        """Create the category-wise summary UI"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Category summary treeview
        self.category_summary_tree = ttk.Treeview(main_frame, columns=("category", "amount", "percentage"), show="headings")
        self.category_summary_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        self.category_summary_tree.heading("category", text="Category")
        self.category_summary_tree.heading("amount", text="Amount")
        self.category_summary_tree.heading("percentage", text="Percentage")
        
        # Define columns
        self.category_summary_tree.column("category", width=150)
        self.category_summary_tree.column("amount", width=120)
        self.category_summary_tree.column("percentage", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.category_summary_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.category_summary_tree.configure(yscrollcommand=scrollbar.set)
    
    def load_customers(self):
        """Load customers into combobox"""
        customers = self.db.get_customers()
        customer_names = [customer["name"] for customer in customers]
        self.customer_combo["values"] = customer_names
    
    def search_incoming_payments(self):
        """Search incoming payments based on filters"""
        # Clear existing items
        for item in self.incoming_tree.get_children():
            self.incoming_tree.delete(item)
        
        # Get filter values
        customer_name = self.customer_var.get()
        from_date_str = self.from_date_var.get()
        to_date_str = self.to_date_var.get()
        mode = self.mode_var.get()
        
        # Parse dates
        try:
            from_day, from_month, from_year = from_date_str.split('/')
            from_date = date(int(from_year), int(from_month), int(from_day))
            
            to_day, to_month, to_year = to_date_str.split('/')
            to_date = date(int(to_year), int(to_month), int(to_day))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dates in DD/MM/YYYY format")
            return
        
        # Get payments
        try:
            # Get customer ID if selected
            customer_id = None
            if customer_name:
                customers = self.db.get_customers()
                for customer in customers:
                    if customer["name"] == customer_name:
                        customer_id = customer["customer_id"]
                        break
            
            # Get payments based on filters
            if customer_id:
                # Get payments for specific customer
                payments = self.db.get_payments_by_customer(customer_id)
            else:
                # Get all payments
                payments = self.db.get_all_payments(from_date, to_date, None if mode == "All" else mode)
            
            # Filter by date and mode if needed
            total_amount = 0
            for payment in payments:
                # Check if date exists
                if not payment.get("date"):
                    continue
                    
                # Parse payment date
                try:
                    if isinstance(payment["date"], str):
                        payment_date = datetime.strptime(payment["date"], "%Y-%m-%d").date()
                    else:
                        payment_date = payment["date"]
                except (ValueError, TypeError):
                    # Skip if date is invalid
                    continue
                
                # Check if payment is within date range
                if from_date <= payment_date <= to_date:
                    # Check if payment matches mode filter
                    if mode == "All" or payment["mode"] == mode:
                        # Get customer name
                        if customer_id:
                            customer_name = customer_name
                        else:
                            customer_name = payment.get("customer_name", "Unknown")
                        
                        # Format date for display
                        if isinstance(payment["date"], str):
                            display_date = payment["date"]
                        else:
                            display_date = payment["date"].strftime("%Y-%m-%d")
                        
                        # Get notes, default to empty string if None
                        notes = payment.get("notes", "") or ""
                        
                        # Add to treeview
                        self.incoming_tree.insert("", "end", values=(
                            payment.get("payment_id", ""),  # Payment ID
                            display_date,
                            customer_name,
                            f"{payment['amount']:.2f}",
                            payment["mode"],
                            payment["reference"] or "",
                            notes[:50] + "..." if len(str(notes)) > 50 else notes  # Truncate long notes
                        ))
                        
                        # Add to total
                        total_amount += payment["amount"]
            
            # Update total
            self.incoming_total_var.set(f"{total_amount:.2f}")
            
        except Exception as e:
            print(f"Error searching incoming payments: {e}")
            messagebox.showerror("Error", f"Error searching payments: {e}")
    
    def search_outgoing_payments(self):
        """Search outgoing payments based on filters"""
        # Clear existing items
        for item in self.outgoing_tree.get_children():
            self.outgoing_tree.delete(item)
        
        # Get filter values
        category = self.category_var.get()
        from_date_str = self.exp_from_date_var.get()
        to_date_str = self.exp_to_date_var.get()
        
        # Parse dates
        try:
            from_day, from_month, from_year = from_date_str.split('/')
            from_date = date(int(from_year), int(from_month), int(from_day))
            
            to_day, to_month, to_year = to_date_str.split('/')
            to_date = date(int(to_year), int(to_month), int(to_day))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dates in DD/MM/YYYY format")
            return
        
        # Get expenses
        try:
            expenses = self.db.get_expenses(from_date, to_date, None if category == "All" else category)
            
            # Calculate total
            total_amount = 0
            for expense in expenses:
                # Format date for display
                if isinstance(expense["date"], str):
                    display_date = expense["date"]
                else:
                    display_date = expense["date"].strftime("%Y-%m-%d")
                
                # Get notes, default to empty string if None
                notes = expense.get("notes", "") or ""
                
                # Add to treeview
                self.outgoing_tree.insert("", "end", values=(
                    expense.get("expense_id", ""),  # Expense ID
                    display_date,
                    expense["description"],
                    f"{expense['amount']:.2f}",
                    expense["category"] or "",
                    notes[:50] + "..." if len(str(notes)) > 50 else notes  # Truncate long notes
                ))
                
                # Add to total
                total_amount += expense["amount"]
            
            # Update total
            self.outgoing_total_var.set(f"{total_amount:.2f}")
            
        except Exception as e:
            print(f"Error searching outgoing payments: {e}")
            messagebox.showerror("Error", f"Error searching expenses: {e}")
    
    def load_summary(self):
        """Load payment summary"""
        # Get date range
        from_date_str = self.sum_from_date_var.get()
        to_date_str = self.sum_to_date_var.get()
        
        # Parse dates
        try:
            from_day, from_month, from_year = from_date_str.split('/')
            from_date = date(int(from_year), int(from_month), int(from_day))
            
            to_day, to_month, to_year = to_date_str.split('/')
            to_date = date(int(to_year), int(to_month), int(to_day))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dates in DD/MM/YYYY format")
            return
        
        # Load overall summary
        self.load_overall_summary(from_date, to_date)
        
        # Load customer summary
        self.load_customer_summary(from_date, to_date)
        
        # Load category summary
        self.load_category_summary(from_date, to_date)
    
    def load_overall_summary(self, from_date, to_date):
        """Load overall payment summary"""
        try:
            # Get all payments
            all_payments = self.db.get_all_payments(from_date, to_date)
            total_incoming = sum(payment["amount"] for payment in all_payments)
            
            # Get outgoing payments
            expenses = self.db.get_expenses(from_date, to_date)
            total_outgoing = sum(expense["amount"] for expense in expenses)
            
            # Calculate net amount
            net_amount = total_incoming - total_outgoing
            
            # Update UI
            self.total_incoming_var.set(f"{total_incoming:.2f}")
            self.total_outgoing_var.set(f"{total_outgoing:.2f}")
            self.net_amount_var.set(f"{net_amount:.2f}")
            
        except Exception as e:
            print(f"Error loading overall summary: {e}")
    
    def load_customer_summary(self, from_date, to_date):
        """Load customer-wise payment summary"""
        # Clear existing items
        for item in self.customer_summary_tree.get_children():
            self.customer_summary_tree.delete(item)
        
        try:
            # Get customers
            customers = self.db.get_customers()
            
            for customer in customers:
                # Get invoices for customer
                invoices = self.db.get_invoices_by_customer(customer["customer_id"])
                
                # Calculate total invoices within date range
                total_invoices = 0
                for invoice in invoices:
                    # Parse invoice date
                    try:
                        if isinstance(invoice["date"], str):
                            invoice_date = datetime.strptime(invoice["date"], "%Y-%m-%d").date()
                        else:
                            invoice_date = invoice["date"]
                    except (ValueError, TypeError):
                        # Skip if date is invalid
                        continue
                    
                    # Check if invoice is within date range
                    if from_date <= invoice_date <= to_date:
                        total_invoices += invoice["total"]
                
                # Get payments for customer
                payments = self.db.get_payments_by_customer(customer["customer_id"])
                
                # Calculate total payments within date range
                total_payments = 0
                for payment in payments:
                    # Parse payment date
                    try:
                        if isinstance(payment["date"], str):
                            payment_date = datetime.strptime(payment["date"], "%Y-%m-%d").date()
                        else:
                            payment_date = payment["date"]
                    except (ValueError, TypeError):
                        # Skip if date is invalid
                        continue
                    
                    # Check if payment is within date range
                    if from_date <= payment_date <= to_date:
                        total_payments += payment["amount"]
                
                # Calculate outstanding
                outstanding = total_invoices - total_payments
                
                # Add to treeview if there are any transactions
                if total_invoices > 0 or total_payments > 0:
                    self.customer_summary_tree.insert("", "end", values=(
                        customer["name"],
                        f"{total_invoices:.2f}",
                        f"{total_payments:.2f}",
                        f"{outstanding:.2f}"
                    ))
            
        except Exception as e:
            print(f"Error loading customer summary: {e}")
    
    def load_category_summary(self, from_date, to_date):
        """Load category-wise payment summary"""
        # Clear existing items
        for item in self.category_summary_tree.get_children():
            self.category_summary_tree.delete(item)
        
        try:
            # Get expenses
            expenses = self.db.get_expenses(from_date, to_date)
            
            # Group by category
            category_totals = {}
            total_amount = 0
            
            for expense in expenses:
                category = expense["category"] or "Other"
                amount = expense["amount"]
                
                if category not in category_totals:
                    category_totals[category] = 0
                
                category_totals[category] += amount
                total_amount += amount
            
            # Add to treeview
            for category, amount in category_totals.items():
                percentage = (amount / total_amount) * 100 if total_amount > 0 else 0
                
                self.category_summary_tree.insert("", "end", values=(
                    category,
                    f"{amount:.2f}",
                    f"{percentage:.1f}%"
                ))
            
        except Exception as e:
            print(f"Error loading category summary: {e}")
    
    def add_payment(self):
        """Add a new payment"""
        # Create payment dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Payment")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Payment details
        ttk.Label(dialog, text="Customer:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        customer_var = tk.StringVar()
        customer_combo = ttk.Combobox(dialog, textvariable=customer_var)
        customer_combo.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Load customers
        customers = self.db.get_customers()
        customer_names = [customer["name"] for customer in customers]
        customer_combo["values"] = customer_names
        
        ttk.Label(dialog, text="Date:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(dialog, textvariable=date_var).grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Amount:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        amount_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=amount_var).grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Payment Mode:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        mode_var = tk.StringVar()
        payment_modes = ["Cash", "UPI", "NEFT", "Cheque", "Other"]
        mode_combo = ttk.Combobox(dialog, textvariable=mode_var, values=payment_modes, state="readonly")
        mode_combo.grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Reference:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        reference_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=reference_var).grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Notes:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        notes_var = tk.StringVar()
        notes_entry = ttk.Entry(dialog, textvariable=notes_var)
        notes_entry.grid(row=5, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=10)
        
        def save_payment():
            try:
                # Get customer
                customer_name = customer_var.get()
                if not customer_name:
                    messagebox.showerror("Error", "Please select a customer")
                    return
                
                customer_id = None
                for customer in customers:
                    if customer["name"] == customer_name:
                        customer_id = customer["customer_id"]
                        break
                
                if not customer_id:
                    messagebox.showerror("Error", "Customer not found")
                    return
                
                # Parse date
                date_str = date_var.get()
                day, month, year = date_str.split('/')
                payment_date = date(int(year), int(month), int(day))
                
                # Get amount
                amount = float(amount_var.get())
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0")
                    return
                
                # Get payment mode
                mode = mode_var.get()
                if not mode:
                    messagebox.showerror("Error", "Please select a payment mode")
                    return
                
                # Add payment
                payment_id = self.db.add_payment(
                    customer_id=customer_id,
                    date=payment_date,
                    amount=amount,
                    mode=mode,
                    reference=reference_var.get(),
                    notes=notes_var.get()
                )
                
                if payment_id:
                    messagebox.showinfo("Success", "Payment added successfully")
                    dialog.destroy()
                    # Refresh payments
                    self.search_incoming_payments()
                else:
                    messagebox.showerror("Error", "Could not add payment")
                    
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values")
            except Exception as e:
                messagebox.showerror("Error", f"Could not add payment: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        dialog.columnconfigure(1, weight=1)
    
    def minus_payment(self):
        """Add a minus payment (advance payment)"""
        # Create payment dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Minus Payment (Advance)")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Payment details
        ttk.Label(dialog, text="Customer:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        customer_var = tk.StringVar()
        customer_combo = ttk.Combobox(dialog, textvariable=customer_var)
        customer_combo.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Load customers
        customers = self.db.get_customers()
        customer_names = [customer["name"] for customer in customers]
        customer_combo["values"] = customer_names
        
        ttk.Label(dialog, text="Date:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(dialog, textvariable=date_var).grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Amount:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        amount_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=amount_var).grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Payment Mode:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        mode_var = tk.StringVar()
        payment_modes = ["Cash", "UPI", "NEFT", "Cheque", "Other"]
        mode_combo = ttk.Combobox(dialog, textvariable=mode_var, values=payment_modes, state="readonly")
        mode_combo.grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Reference:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        reference_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=reference_var).grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Notes:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        notes_var = tk.StringVar()
        notes_entry = ttk.Entry(dialog, textvariable=notes_var)
        notes_entry.grid(row=5, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=10)
        
        def save_payment():
            try:
                # Get customer
                customer_name = customer_var.get()
                if not customer_name:
                    messagebox.showerror("Error", "Please select a customer")
                    return
                
                customer_id = None
                for customer in customers:
                    if customer["name"] == customer_name:
                        customer_id = customer["customer_id"]
                        break
                
                if not customer_id:
                    messagebox.showerror("Error", "Customer not found")
                    return
                
                # Parse date
                date_str = date_var.get()
                day, month, year = date_str.split('/')
                payment_date = date(int(year), int(month), int(day))
                
                # Get amount
                amount = float(amount_var.get())
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0")
                    return
                
                # Get payment mode
                mode = mode_var.get()
                if not mode:
                    messagebox.showerror("Error", "Please select a payment mode")
                    return
                
                # Add payment as negative amount (advance payment)
                payment_id = self.db.add_payment(
                    customer_id=customer_id,
                    date=payment_date,
                    amount=-amount,  # Negative amount for advance payment
                    mode=mode,
                    reference=reference_var.get(),
                    notes=f"Advance payment: {notes_var.get()}"
                )
                
                if payment_id:
                    messagebox.showinfo("Success", "Advance payment added successfully")
                    dialog.destroy()
                    # Refresh payments
                    self.search_incoming_payments()
                else:
                    messagebox.showerror("Error", "Could not add advance payment")
                    
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values")
            except Exception as e:
                messagebox.showerror("Error", f"Could not add advance payment: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        dialog.columnconfigure(1, weight=1)
    
    def add_expense(self):
        """Add a new expense"""
        # Create expense dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Expense")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Expense details
        ttk.Label(dialog, text="Date:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(dialog, textvariable=date_var).grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Description:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        description_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=description_var).grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Amount:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        amount_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=amount_var).grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Category:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        category_var = tk.StringVar()
        categories = ["Salary", "Rent", "Material", "Utilities", "Maintenance", "Other"]
        category_combo = ttk.Combobox(dialog, textvariable=category_var, values=categories, state="readonly")
        category_combo.grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Notes:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        notes_var = tk.StringVar()
        notes_entry = ttk.Entry(dialog, textvariable=notes_var)
        notes_entry.grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        
        def save_expense():
            try:
                # Parse date
                date_str = date_var.get()
                day, month, year = date_str.split('/')
                expense_date = date(int(year), int(month), int(day))
                
                # Get description
                description = description_var.get().strip()
                if not description:
                    messagebox.showerror("Error", "Description is required")
                    return
                
                # Get amount
                amount = float(amount_var.get())
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0")
                    return
                
                # Get category
                category = category_var.get()
                if not category:
                    messagebox.showerror("Error", "Please select a category")
                    return
                
                # Add expense
                expense_id = self.db.add_expense(
                    date=expense_date,
                    description=description,
                    amount=amount,
                    category=category,
                    notes=notes_var.get()
                )
                
                if expense_id:
                    messagebox.showinfo("Success", "Expense added successfully")
                    dialog.destroy()
                    # Refresh expenses
                    self.search_outgoing_payments()
                else:
                    messagebox.showerror("Error", "Could not add expense")
                    
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values")
            except Exception as e:
                messagebox.showerror("Error", f"Could not add expense: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_expense).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        dialog.columnconfigure(1, weight=1)
    
    def edit_payment(self):
        """Edit an existing payment"""
        selected = self.incoming_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a payment to edit")
            return
        
        # Get payment details
        item = self.incoming_tree.item(selected[0])
        payment_id = item["values"][0]
        date_str = item["values"][1]
        customer_name = item["values"][2]
        amount_str = item["values"][3]
        mode = item["values"][4]
        reference = item["values"][5]
        
        # Find the payment in the database to get additional details like notes
        try:
            # Get customer ID
            customers = self.db.get_customers()
            customer_id = None
            for customer in customers:
                if customer["name"] == customer_name:
                    customer_id = customer["customer_id"]
                    break
            
            if not customer_id:
                messagebox.showerror("Error", "Customer not found")
                return
            
            # Get payments for this customer
            payments = self.db.get_payments_by_customer(customer_id)
            
            # Find the matching payment using multiple criteria
            payment = None
            for p in payments:
                # Check if payment_id matches
                if str(p.get("payment_id", "")) == str(payment_id):
                    payment = p
                    break
            
            if not payment:
                messagebox.showerror("Error", "Payment details not found")
                return
            
            # Create edit payment dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title("Edit Payment")
            dialog.geometry("400x300")
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # Payment details
            ttk.Label(dialog, text="Customer:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            customer_var = tk.StringVar(value=customer_name)
            customer_combo = ttk.Combobox(dialog, textvariable=customer_var, state="readonly")
            customer_combo.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
            
            # Load customers
            customer_names = [customer["name"] for customer in customers]
            customer_combo["values"] = customer_names
            
            ttk.Label(dialog, text="Date:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
            date_var = tk.StringVar(value=date_str)
            ttk.Entry(dialog, textvariable=date_var).grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
            
            ttk.Label(dialog, text="Amount:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
            amount_var = tk.StringVar(value=amount_str)
            ttk.Entry(dialog, textvariable=amount_var).grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
            
            ttk.Label(dialog, text="Payment Mode:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
            mode_var = tk.StringVar(value=mode)
            payment_modes = ["Cash", "UPI", "NEFT", "Cheque", "Other"]
            mode_combo = ttk.Combobox(dialog, textvariable=mode_var, values=payment_modes, state="readonly")
            mode_combo.grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
            
            ttk.Label(dialog, text="Reference:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
            reference_var = tk.StringVar(value=reference)
            ttk.Entry(dialog, textvariable=reference_var).grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)
            
            ttk.Label(dialog, text="Notes:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
            notes_var = tk.StringVar(value=payment.get("notes", "") or "")
            notes_entry = ttk.Entry(dialog, textvariable=notes_var)
            notes_entry.grid(row=5, column=1, padx=10, pady=5, sticky=tk.EW)
            
            # Buttons
            button_frame = ttk.Frame(dialog)
            button_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=10)
            
            def update_payment():
                try:
                    # Get customer
                    customer_name = customer_var.get()
                    if not customer_name:
                        messagebox.showerror("Error", "Please select a customer")
                        return
                    
                    customer_id = None
                    for customer in customers:
                        if customer["name"] == customer_name:
                            customer_id = customer["customer_id"]
                            break
                    
                    if not customer_id:
                        messagebox.showerror("Error", "Customer not found")
                        return
                    
                    # Parse date
                    date_str = date_var.get()
                    # Try different date formats
                    try:
                        day, month, year = date_str.split('/')
                        payment_date = date(int(year), int(month), int(day))
                    except ValueError:
                        try:
                            # Try YYYY-MM-DD format
                            year, month, day = date_str.split('-')
                            payment_date = date(int(year), int(month), int(day))
                        except ValueError:
                            messagebox.showerror("Error", "Invalid date format. Please use DD/MM/YYYY or YYYY-MM-DD")
                            return
                    
                    # Get amount
                    amount = float(amount_var.get())
                    if amount == 0:
                        messagebox.showerror("Error", "Amount cannot be zero")
                        return
                    
                    # Get payment mode
                    mode = mode_var.get()
                    if not mode:
                        messagebox.showerror("Error", "Please select a payment mode")
                        return
                    
                    # Update payment
                    success = self.db.update_payment(
                        payment_id=payment_id,
                        customer_id=customer_id,
                        date=payment_date,
                        amount=amount,
                        mode=mode,
                        reference=reference_var.get(),
                        notes=notes_var.get()
                    )
                    
                    if success:
                        messagebox.showinfo("Success", "Payment updated successfully")
                        dialog.destroy()
                        # Refresh payments
                        self.search_incoming_payments()
                    else:
                        messagebox.showerror("Error", "Could not update payment")
                        
                except ValueError as e:
                    messagebox.showerror("Error", f"Please enter valid values: {str(e)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not update payment: {e}")
            
            ttk.Button(button_frame, text="Update", command=update_payment).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            
            # Configure grid weights
            dialog.columnconfigure(1, weight=1)
            
        except Exception as e:
            print(f"Error editing payment: {e}")
            messagebox.showerror("Error", f"Error editing payment: {e}")
    
    def delete_payment(self):
        """Delete a payment"""
        selected = self.incoming_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a payment to delete")
            return
        
        # Get payment details
        item = self.incoming_tree.item(selected[0])
        payment_id = item["values"][0]
        customer_name = item["values"][2]
        amount_str = item["values"][3]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the payment of {amount_str} from {customer_name}? This will move it to the Recycle Bin."
        )
        
        if not confirm:
            return
        
        try:
            # Delete payment (moved to recycle bin)
            success = self.db.delete_payment(payment_id)
            
            if success:
                messagebox.showinfo("Success", "Payment moved to Recycle Bin")
                # Refresh payments
                self.search_incoming_payments()
            else:
                messagebox.showerror("Error", "Could not delete payment")
                
        except Exception as e:
            print(f"Error deleting payment: {e}")
            messagebox.showerror("Error", f"Error deleting payment: {e}")
    
    def edit_expense(self):
        """Edit an existing expense"""
        selected = self.outgoing_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an expense to edit")
            return
        
        # Get expense details
        item = self.outgoing_tree.item(selected[0])
        expense_id = item["values"][0]
        date_str = item["values"][1]
        description = item["values"][2]
        amount_str = item["values"][3]
        category = item["values"][4]
        
        # Parse date to find the expense in the database
        try:
            # Try to parse the date string in the format from the database
            expense_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            try:
                # Try to parse in case it's in a different format
                expense_date = datetime.strptime(date_str, "%d/%m/%Y").date()
            except ValueError:
                messagebox.showerror("Error", "Invalid date format")
                return
        
        # Get expenses from database for this date and description
        try:
            expenses = self.db.get_expenses(expense_date, expense_date)
            expense = None
            
            # Find the matching expense
            for exp in expenses:
                if str(exp.get("expense_id", "")) == str(expense_id):
                    expense = exp
                    break
            
            if not expense:
                messagebox.showerror("Error", "Expense details not found")
                return
            
            # Create edit expense dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title("Edit Expense")
            dialog.geometry("400x300")
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # Expense details
            ttk.Label(dialog, text="Date:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            date_var = tk.StringVar(value=date_str)
            ttk.Entry(dialog, textvariable=date_var).grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
            
            ttk.Label(dialog, text="Description:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
            description_var = tk.StringVar(value=description)
            ttk.Entry(dialog, textvariable=description_var).grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
            
            ttk.Label(dialog, text="Amount:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
            amount_var = tk.StringVar(value=amount_str)
            ttk.Entry(dialog, textvariable=amount_var).grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
            
            ttk.Label(dialog, text="Category:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
            category_var = tk.StringVar(value=category)
            categories = ["Salary", "Rent", "Material", "Utilities", "Maintenance", "Other"]
            category_combo = ttk.Combobox(dialog, textvariable=category_var, values=categories, state="readonly")
            category_combo.grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
            
            ttk.Label(dialog, text="Notes:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
            notes_var = tk.StringVar(value=expense.get("notes", "") or "")
            notes_entry = ttk.Entry(dialog, textvariable=notes_var)
            notes_entry.grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)
            
            # Buttons
            button_frame = ttk.Frame(dialog)
            button_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
            
            def update_expense():
                try:
                    # Parse date
                    date_str = date_var.get()
                    # Try different date formats
                    try:
                        day, month, year = date_str.split('/')
                        expense_date = date(int(year), int(month), int(day))
                    except ValueError:
                        try:
                            # Try YYYY-MM-DD format
                            year, month, day = date_str.split('-')
                            expense_date = date(int(year), int(month), int(day))
                        except ValueError:
                            messagebox.showerror("Error", "Invalid date format. Please use DD/MM/YYYY or YYYY-MM-DD")
                            return
                    
                    # Get description
                    description = description_var.get().strip()
                    if not description:
                        messagebox.showerror("Error", "Description is required")
                        return
                    
                    # Get amount
                    amount = float(amount_var.get())
                    if amount <= 0:
                        messagebox.showerror("Error", "Amount must be greater than 0")
                        return
                    
                    # Get category
                    category = category_var.get()
                    if not category:
                        messagebox.showerror("Error", "Please select a category")
                        return
                    
                    # Update expense
                    success = self.db.update_expense(
                        expense_id=expense_id,
                        date=expense_date,
                        description=description,
                        amount=amount,
                        category=category,
                        notes=notes_var.get()
                    )
                    
                    if success:
                        messagebox.showinfo("Success", "Expense updated successfully")
                        dialog.destroy()
                        # Refresh expenses
                        self.search_outgoing_payments()
                    else:
                        messagebox.showerror("Error", "Could not update expense")
                        
                except ValueError as e:
                    messagebox.showerror("Error", f"Please enter valid values: {str(e)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not update expense: {e}")
            
            ttk.Button(button_frame, text="Update", command=update_expense).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            
            # Configure grid weights
            dialog.columnconfigure(1, weight=1)
            
        except Exception as e:
            print(f"Error editing expense: {e}")
            messagebox.showerror("Error", f"Error editing expense: {e}")
    
    def delete_expense(self):
        """Delete an expense"""
        selected = self.outgoing_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an expense to delete")
            return
        
        # Get expense details
        item = self.outgoing_tree.item(selected[0])
        expense_id = item["values"][0]
        description = item["values"][2]
        amount_str = item["values"][3]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the expense '{description}' of {amount_str}? This will move it to the Recycle Bin."
        )
        
        if not confirm:
            return
        
        try:
            # Delete expense (moved to recycle bin)
            success = self.db.delete_expense(expense_id)
            
            if success:
                messagebox.showinfo("Success", "Expense moved to Recycle Bin")
                # Refresh expenses
                self.search_outgoing_payments()
            else:
                messagebox.showerror("Error", "Could not delete expense")
                
        except Exception as e:
            print(f"Error deleting expense: {e}")
            messagebox.showerror("Error", f"Error deleting expense: {e}")
    
    def view_payment_details(self, event=None):
        """View payment details"""
        selected = self.incoming_tree.selection()
        if not selected:
            return
        
        # Get payment details from treeview
        item = self.incoming_tree.item(selected[0])
        payment_id = item["values"][0]
        date_str = item["values"][1]
        customer_name = item["values"][2]
        amount_str = item["values"][3]
        mode = item["values"][4]
        reference = item["values"][5]
        
        # Find the payment in the database to get additional details like notes
        try:
            # Get customer ID
            customers = self.db.get_customers()
            customer_id = None
            for customer in customers:
                if customer["name"] == customer_name:
                    customer_id = customer["customer_id"]
                    break
            
            if not customer_id:
                messagebox.showerror("Error", "Customer not found")
                return
            
            # Get payments for this customer
            payments = self.db.get_payments_by_customer(customer_id)
            
            # Find the matching payment using multiple criteria
            payment = None
            for p in payments:
                # Check if payment_id matches
                if str(p.get("payment_id", "")) == str(payment_id):
                    payment = p
                    break
            
            if not payment:
                messagebox.showerror("Error", "Payment details not found")
                return
            
            # Create payment details dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title("Payment Details")
            dialog.geometry("500x350")
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # Payment details
            details_frame = ttk.LabelFrame(dialog, text="Payment Details")
            details_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Date
            date_frame = ttk.Frame(details_frame)
            date_frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(date_frame, text="Date:").pack(side=tk.LEFT, padx=(0, 5))
            ttk.Label(date_frame, text=date_str).pack(side=tk.LEFT)
            
            # Customer
            cust_frame = ttk.Frame(details_frame)
            cust_frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(cust_frame, text="Customer:").pack(side=tk.LEFT, padx=(0, 5))
            ttk.Label(cust_frame, text=customer_name).pack(side=tk.LEFT)
            
            # Amount
            amount_frame = ttk.Frame(details_frame)
            amount_frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(amount_frame, text="Amount:").pack(side=tk.LEFT, padx=(0, 5))
            ttk.Label(amount_frame, text=amount_str).pack(side=tk.LEFT)
            
            # Mode
            mode_frame = ttk.Frame(details_frame)
            mode_frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT, padx=(0, 5))
            ttk.Label(mode_frame, text=mode).pack(side=tk.LEFT)
            
            # Reference
            ref_frame = ttk.Frame(details_frame)
            ref_frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(ref_frame, text="Reference:").pack(side=tk.LEFT, padx=(0, 5))
            ttk.Label(ref_frame, text=reference or "").pack(side=tk.LEFT)
            
            # Notes
            notes_frame = ttk.Frame(details_frame)
            notes_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
            
            # Notes label
            ttk.Label(notes_frame, text="Notes:").pack(anchor=tk.W, padx=(0, 5))
            
            # Create a text widget for notes
            notes_container = ttk.Frame(notes_frame)
            notes_container.pack(fill=tk.BOTH, expand=True)
            
            notes_text = tk.Text(notes_container, height=6, wrap=tk.WORD)
            notes_text.pack(fill=tk.BOTH, expand=True)
            notes_text.insert(tk.END, payment.get("notes", "") or "")
            notes_text.config(state=tk.DISABLED)
            
            # Action buttons
            action_frame = ttk.Frame(dialog)
            action_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Edit button
            edit_btn = ttk.Button(action_frame, text="Edit", command=lambda: (dialog.destroy(), self.edit_payment()))
            edit_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Delete button
            delete_btn = ttk.Button(action_frame, text="Delete", command=lambda: (dialog.destroy(), self.delete_payment()))
            delete_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Close button
            close_btn = ttk.Button(action_frame, text="Close", command=dialog.destroy)
            close_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
        except Exception as e:
            print(f"Error viewing payment details: {e}")
            messagebox.showerror("Error", f"Error viewing payment details: {e}")
    
    def view_expense_details(self, event=None):
        """View expense details"""
        selected = self.outgoing_tree.selection()
        if not selected:
            return
        
        # Get expense details from treeview
        item = self.outgoing_tree.item(selected[0])
        expense_id = item["values"][0]
        date_str = item["values"][1]
        description = item["values"][2]
        amount_str = item["values"][3]
        category = item["values"][4]
        
        # Parse date to find the expense in the database
        try:
            # Try to parse the date string in the format from the database
            expense_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            try:
                # Try to parse in case it's in a different format
                expense_date = datetime.strptime(date_str, "%d/%m/%Y").date()
            except ValueError:
                messagebox.showerror("Error", "Invalid date format")
                return
        
        # Get expenses from database for this date and description
        try:
            expenses = self.db.get_expenses(expense_date, expense_date)
            expense = None
            
            # Find the matching expense
            for exp in expenses:
                if str(exp.get("expense_id", "")) == str(expense_id):
                    expense = exp
                    break
            
            if not expense:
                messagebox.showerror("Error", "Expense details not found")
                return
            
            # Create expense details dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title("Expense Details")
            dialog.geometry("500x350")
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # Expense details
            details_frame = ttk.LabelFrame(dialog, text="Expense Details")
            details_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Date
            date_frame = ttk.Frame(details_frame)
            date_frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(date_frame, text="Date:").pack(side=tk.LEFT, padx=(0, 5))
            ttk.Label(date_frame, text=expense["date"]).pack(side=tk.LEFT)
            
            # Description
            desc_frame = ttk.Frame(details_frame)
            desc_frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(desc_frame, text="Description:").pack(side=tk.LEFT, padx=(0, 5))
            ttk.Label(desc_frame, text=expense["description"]).pack(side=tk.LEFT)
            
            # Amount
            amount_frame = ttk.Frame(details_frame)
            amount_frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(amount_frame, text="Amount:").pack(side=tk.LEFT, padx=(0, 5))
            ttk.Label(amount_frame, text=f"{expense['amount']:.2f}").pack(side=tk.LEFT)
            
            # Category
            cat_frame = ttk.Frame(details_frame)
            cat_frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(cat_frame, text="Category:").pack(side=tk.LEFT, padx=(0, 5))
            ttk.Label(cat_frame, text=expense["category"] or "").pack(side=tk.LEFT)
            
            # Notes
            notes_frame = ttk.Frame(details_frame)
            notes_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
            
            # Notes label
            ttk.Label(notes_frame, text="Notes:").pack(anchor=tk.W, padx=(0, 5))
            
            # Create a text widget for notes
            notes_container = ttk.Frame(notes_frame)
            notes_container.pack(fill=tk.BOTH, expand=True)
            
            notes_text = tk.Text(notes_container, height=6, wrap=tk.WORD)
            notes_text.pack(fill=tk.BOTH, expand=True)
            notes_text.insert(tk.END, expense.get("notes", "") or "")
            notes_text.config(state=tk.DISABLED)
            
            # Action buttons
            action_frame = ttk.Frame(dialog)
            action_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Edit button
            edit_btn = ttk.Button(action_frame, text="Edit", command=lambda: (dialog.destroy(), self.edit_expense()))
            edit_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Delete button
            delete_btn = ttk.Button(action_frame, text="Delete", command=lambda: (dialog.destroy(), self.delete_expense()))
            delete_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Close button
            close_btn = ttk.Button(action_frame, text="Close", command=dialog.destroy)
            close_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
        except Exception as e:
            print(f"Error viewing expense details: {e}")
            messagebox.showerror("Error", f"Error viewing expense details: {e}")
    
    def view_customer_payment_details(self, event=None):
        """View customer payment details"""
        selected = self.customer_summary_tree.selection()
        if not selected:
            return
        
        # Get customer details
        item = self.customer_summary_tree.item(selected[0])
        customer_name = item["values"][0]
        
        # Get customer from database
        customers = self.db.get_customers()
        customer = None
        for c in customers:
            if c["name"] == customer_name:
                customer = c
                break
        
        if not customer:
            messagebox.showerror("Error", "Customer not found")
            return
        
        # Create customer payment details dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Customer Payment Details - {customer_name}")
        dialog.geometry("800x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Invoices tab
        invoices_tab = ttk.Frame(notebook)
        notebook.add(invoices_tab, text="Invoices")
        
        # Create invoices UI
        self.create_customer_invoices_ui(invoices_tab, customer)
        
        # Payments tab
        payments_tab = ttk.Frame(notebook)
        notebook.add(payments_tab, text="Payments")
        
        # Create payments UI
        self.create_customer_payments_ui(payments_tab, customer)
    
    def create_customer_invoices_ui(self, parent, customer):
        """Create UI for customer invoices"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Invoices treeview
        invoices_tree = ttk.Treeview(main_frame, columns=("invoice_number", "date", "total", "payment_mode"), show="headings")
        invoices_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        invoices_tree.heading("invoice_number", text="Invoice #")
        invoices_tree.heading("date", text="Date")
        invoices_tree.heading("total", text="Total")
        invoices_tree.heading("payment_mode", text="Payment Mode")
        
        # Define columns
        invoices_tree.column("invoice_number", width=100)
        invoices_tree.column("date", width=100)
        invoices_tree.column("total", width=100)
        invoices_tree.column("payment_mode", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=invoices_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        invoices_tree.configure(yscrollcommand=scrollbar.set)
        
        # Load invoices
        try:
            invoices = self.db.get_invoices_by_customer(customer["customer_id"])
            
            for invoice in invoices:
                # Format date for display
                if isinstance(invoice["date"], str):
                    display_date = invoice["date"]
                else:
                    display_date = invoice["date"].strftime("%Y-%m-%d")
                    
                invoices_tree.insert("", "end", values=(
                    invoice["invoice_number"],
                    display_date,
                    f"{invoice['total']:.2f}",
                    invoice["payment_mode"] or ""
                ))
        except Exception as e:
            print(f"Error loading customer invoices: {e}")
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Close button
        close_btn = ttk.Button(action_frame, text="Close", command=parent.destroy)
        close_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def create_customer_payments_ui(self, parent, customer):
        """Create UI for customer payments"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Payments treeview
        payments_tree = ttk.Treeview(main_frame, columns=("id", "date", "amount", "mode", "reference", "notes"), show="headings")
        payments_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        payments_tree.heading("id", text="ID")
        payments_tree.heading("date", text="Date")
        payments_tree.heading("amount", text="Amount")
        payments_tree.heading("mode", text="Mode")
        payments_tree.heading("reference", text="Reference")
        payments_tree.heading("notes", text="Notes")
        
        # Define columns
        payments_tree.column("id", width=0, stretch=False)  # Hidden column
        payments_tree.column("date", width=100)
        payments_tree.column("amount", width=100)
        payments_tree.column("mode", width=100)
        payments_tree.column("reference", width=100)
        payments_tree.column("notes", width=150)
        
        # Hide the ID column
        payments_tree.column("id", minwidth=0, width=0, stretch=False)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=payments_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        payments_tree.configure(yscrollcommand=scrollbar.set)
        
        # Load payments
        try:
            payments = self.db.get_payments_by_customer(customer["customer_id"])
            
            for payment in payments:
                # Format date for display
                if isinstance(payment["date"], str):
                    display_date = payment["date"]
                else:
                    display_date = payment["date"].strftime("%Y-%m-%d")
                
                # Get notes, default to empty string if None
                notes = payment.get("notes", "") or ""
                    
                payments_tree.insert("", "end", values=(
                    payment.get("payment_id", ""),  # Payment ID
                    display_date,
                    f"{payment['amount']:.2f}",
                    payment["mode"],
                    payment["reference"] or "",
                    notes[:50] + "..." if len(str(notes)) > 50 else notes  # Truncate long notes
                ))
        except Exception as e:
            print(f"Error loading customer payments: {e}")
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add payment button
        add_btn = ttk.Button(action_frame, text="Add Payment", 
                            command=lambda: self.add_customer_payment(customer))
        add_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Minus payment button (for advance payments)
        minus_btn = ttk.Button(action_frame, text="Minus Payment", 
                              command=lambda: self.minus_customer_payment(customer))
        minus_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Close button
        close_btn = ttk.Button(action_frame, text="Close", command=parent.destroy)
        close_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def add_customer_payment(self, customer):
        """Add a payment for a specific customer"""
        # Create payment dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Add Payment - {customer['name']}")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Payment details
        ttk.Label(dialog, text="Date:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(dialog, textvariable=date_var).grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Amount:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        amount_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=amount_var).grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Payment Mode:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        mode_var = tk.StringVar()
        payment_modes = ["Cash", "UPI", "NEFT", "Cheque", "Other"]
        mode_combo = ttk.Combobox(dialog, textvariable=mode_var, values=payment_modes, state="readonly")
        mode_combo.grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Reference:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        reference_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=reference_var).grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Notes:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        notes_var = tk.StringVar()
        notes_entry = ttk.Entry(dialog, textvariable=notes_var)
        notes_entry.grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        
        def save_payment():
            try:
                # Parse date
                date_str = date_var.get()
                day, month, year = date_str.split('/')
                payment_date = date(int(year), int(month), int(day))
                
                # Get amount
                amount = float(amount_var.get())
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0")
                    return
                
                # Get payment mode
                mode = mode_var.get()
                if not mode:
                    messagebox.showerror("Error", "Please select a payment mode")
                    return
                
                # Add payment
                payment_id = self.db.add_payment(
                    customer_id=customer["customer_id"],
                    date=payment_date,
                    amount=amount,
                    mode=mode,
                    reference=reference_var.get(),
                    notes=notes_var.get()
                )
                
                if payment_id:
                    messagebox.showinfo("Success", "Payment added successfully")
                    dialog.destroy()
                    # Refresh payments
                    self.search_incoming_payments()
                else:
                    messagebox.showerror("Error", "Could not add payment")
                    
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values")
            except Exception as e:
                messagebox.showerror("Error", f"Could not add payment: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        dialog.columnconfigure(1, weight=1)
    
    def minus_customer_payment(self, customer):
        """Add a minus payment (advance payment) for a specific customer"""
        # Create payment dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Minus Payment (Advance) - {customer['name']}")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Payment details
        ttk.Label(dialog, text="Date:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(dialog, textvariable=date_var).grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Amount:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        amount_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=amount_var).grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Payment Mode:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        mode_var = tk.StringVar()
        payment_modes = ["Cash", "UPI", "NEFT", "Cheque", "Other"]
        mode_combo = ttk.Combobox(dialog, textvariable=mode_var, values=payment_modes, state="readonly")
        mode_combo.grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Reference:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        reference_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=reference_var).grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Notes:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        notes_var = tk.StringVar()
        notes_entry = ttk.Entry(dialog, textvariable=notes_var)
        notes_entry.grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        
        def save_payment():
            try:
                # Parse date
                date_str = date_var.get()
                day, month, year = date_str.split('/')
                payment_date = date(int(year), int(month), int(day))
                
                # Get amount
                amount = float(amount_var.get())
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0")
                    return
                
                # Get payment mode
                mode = mode_var.get()
                if not mode:
                    messagebox.showerror("Error", "Please select a payment mode")
                    return
                
                # Add payment as negative amount (advance payment)
                payment_id = self.db.add_payment(
                    customer_id=customer["customer_id"],
                    date=payment_date,
                    amount=-amount,  # Negative amount for advance payment
                    mode=mode,
                    reference=reference_var.get(),
                    notes=f"Advance payment: {notes_var.get()}"
                )
                
                if payment_id:
                    messagebox.showinfo("Success", "Advance payment added successfully")
                    dialog.destroy()
                    # Refresh payments
                    self.search_incoming_payments()
                else:
                    messagebox.showerror("Error", "Could not add advance payment")
                    
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values")
            except Exception as e:
                messagebox.showerror("Error", f"Could not add advance payment: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        dialog.columnconfigure(1, weight=1)
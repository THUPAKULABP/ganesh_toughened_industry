import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import calendar
import json

class CustomerHistoryModule:
    def __init__(self, parent, db, app):
        self.parent = parent
        self.db = db
        self.app = app
        self.selected_customer = None
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """Create the customer history UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="CUSTOMER HISTORY", style="Title.TLabel")
        title.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        history_tab = ttk.Frame(notebook)
        outstanding_tab = ttk.Frame(notebook)
        
        notebook.add(history_tab, text="History")
        #notebook.add(outstanding_tab, text="Outstanding")
        
        # Bind tab selection to refresh outstanding when selected
        notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Create history tab
        self.create_history_tab(history_tab)
        
        # Create outstanding tab
        self.create_outstanding_tab(outstanding_tab)
    
    def on_tab_changed(self, event):
        """Handle tab change event"""
        notebook = event.widget
        current_tab = notebook.tab(notebook.select(), "text")
        if current_tab == "Outstanding":
            self.load_outstanding()
    
    def create_history_tab(self, parent):
        """Create the history tab"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Customer filter
        ttk.Label(search_frame, text="Customer:").pack(side=tk.LEFT, padx=5)
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(search_frame, textvariable=self.customer_var)
        self.customer_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.customer_combo.bind("<<ComboboxSelected>>", self.on_customer_selected)
        
        # Load customers
        self.load_customers()
        
        # Year filter
        ttk.Label(search_frame, text="Year:").pack(side=tk.LEFT, padx=5)
        current_year = datetime.now().year
        years = [str(year) for year in range(current_year - 5, current_year + 1)]
        self.year_var = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(search_frame, textvariable=self.year_var, values=years, state="readonly", width=10)
        year_combo.pack(side=tk.LEFT, padx=5)
        
        # Month filter
        ttk.Label(search_frame, text="Month:").pack(side=tk.LEFT, padx=5)
        months = list(calendar.month_name)[1:]  # Remove empty string at index 0
        self.month_var = tk.StringVar(value=calendar.month_name[datetime.now().month])
        month_combo = ttk.Combobox(search_frame, textvariable=self.month_var, values=months, state="readonly")
        month_combo.pack(side=tk.LEFT, padx=5)
        
        # Search button
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_history)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # History display
        history_frame = ttk.Frame(main_frame)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for month grouping
        self.history_notebook = ttk.Notebook(history_frame)
        self.history_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Load initial history
        self.search_history()
    
    def create_outstanding_tab(self, parent):
        """Create the outstanding tab"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Outstanding treeview
        self.outstanding_tree = ttk.Treeview(main_frame, columns=("customer", "place", "total_invoices", "total_payments", "outstanding"), show="headings")
        self.outstanding_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        self.outstanding_tree.heading("customer", text="Customer")
        self.outstanding_tree.heading("place", text="Place")
        self.outstanding_tree.heading("total_invoices", text="Total Invoices")
        self.outstanding_tree.heading("total_payments", text="Total Payments")
        self.outstanding_tree.heading("outstanding", text="Outstanding")
        
        # Define columns
        self.outstanding_tree.column("customer", width=150)
        self.outstanding_tree.column("place", width=100)
        self.outstanding_tree.column("total_invoices", width=120)
        self.outstanding_tree.column("total_payments", width=120)
        self.outstanding_tree.column("outstanding", width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.outstanding_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.outstanding_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click to view details
        self.outstanding_tree.bind("<Double-1>", self.view_customer_details)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Refresh button
        refresh_btn = ttk.Button(action_frame, text="Refresh", command=self.load_outstanding)
        refresh_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Load outstanding data
        self.load_outstanding()
    
    def load_customers(self):
        """Load customers into combobox"""
        try:
            customers = self.db.get_customers()
            customer_names = [customer["name"] for customer in customers]
            self.customer_combo["values"] = customer_names
        except Exception as e:
            print(f"Error loading customers: {e}")
            messagebox.showerror("Error", f"Failed to load customers: {e}")
    
    def on_customer_selected(self, event):
        """Handle customer selection"""
        customer_name = self.customer_var.get()
        if customer_name:
            # Get customer details
            try:
                customers = self.db.get_customers()
                for customer in customers:
                    if customer["name"] == customer_name:
                        self.selected_customer = customer
                        break
            except Exception as e:
                print(f"Error selecting customer: {e}")
                messagebox.showerror("Error", f"Failed to select customer: {e}")
    
    def search_history(self):
        """Search customer history based on filters"""
        # Clear existing tabs
        for tab_id in self.history_notebook.tabs():
            self.history_notebook.forget(tab_id)
        
        # Get filter values
        customer_name = self.customer_var.get()
        year = self.year_var.get()
        month = self.month_var.get()
        
        # Convert month name to number
        try:
            month_num = list(calendar.month_name).index(month)
        except ValueError:
            messagebox.showerror("Error", "Invalid month selected")
            return
        
        # Get customer ID if selected
        customer_id = None
        if self.selected_customer:
            customer_id = self.selected_customer["customer_id"]
        
        # Get invoices for the selected period
        try:
            # Build query with proper date filtering
            query = """
            SELECT i.invoice_id, i.invoice_number, i.date, i.subtotal, i.extra_charges, 
                   i.round_off, i.total, i.payment_mode, i.p_pay_no, c.name as customer_name,
                   c.place as customer_place, c.customer_id, i.extra_charges_breakdown
            FROM invoices i
            JOIN customers c ON i.customer_id = c.customer_id
            WHERE 1=1
            """
            params = []
            
            if customer_id:
                query += " AND i.customer_id = ?"
                params.append(customer_id)
            
            # Add year and month filtering
            query += " AND strftime('%Y', i.date) = ?"
            params.append(year)
            
            query += " AND strftime('%m', i.date) = ?"
            params.append(f"{month_num:02d}")
            
            # Execute query
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            # Convert rows to dictionaries
            invoices = []
            for row in cursor.fetchall():
                invoice = dict(zip(column_names, row))
                invoices.append(invoice)
            
            # Group invoices by month
            monthly_invoices = {}
            for invoice in invoices:
                # Parse date
                date_obj = datetime.strptime(invoice["date"], "%Y-%m-%d")
                invoice_month = date_obj.month
                invoice_year = date_obj.year
                
                # Create key for month-year
                key = f"{invoice_year}-{invoice_month:02d}"
                
                if key not in monthly_invoices:
                    monthly_invoices[key] = []
                
                monthly_invoices[key].append(invoice)
            
            # Create tabs for each month
            for key in sorted(monthly_invoices.keys(), reverse=True):
                year_month = key.split("-")
                tab_year = int(year_month[0])
                tab_month = int(year_month[1])
                tab_month_name = calendar.month_name[tab_month]
                
                # Create tab
                tab_frame = ttk.Frame(self.history_notebook)
                self.history_notebook.add(tab_frame, text=f"{tab_month_name} {tab_year}")
                
                # Create treeview for invoices
                invoices_tree = ttk.Treeview(tab_frame, columns=("invoice_number", "date", "total", "payment_mode"), show="headings")
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
                
                # Add invoices
                for invoice in monthly_invoices[key]:
                    # Format date for display
                    date_obj = datetime.strptime(invoice["date"], "%Y-%m-%d")
                    display_date = date_obj.strftime("%d/%m/%Y")
                    
                    invoices_tree.insert("", "end", values=(
                        invoice["invoice_number"],
                        display_date,
                        f"{invoice['total']:.2f}",
                        invoice["payment_mode"] or ""
                    ))
                
                # Add scrollbar
                tab_scrollbar = ttk.Scrollbar(tab_frame, orient=tk.VERTICAL, command=invoices_tree.yview)
                tab_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                invoices_tree.configure(yscrollcommand=tab_scrollbar.set)
                
                # Bind double-click to view invoice
                invoices_tree.bind("<Double-1>", lambda e, inv=invoice: self.view_invoice(inv))
            
            # If no invoices found
            if not monthly_invoices:
                no_data_frame = ttk.Frame(self.history_notebook)
                self.history_notebook.add(no_data_frame, text="No Data")
                ttk.Label(no_data_frame, text="No invoices found for the selected criteria").pack(pady=20)
            
            # Close connection
            conn.close()
            
        except Exception as e:
            print(f"Error searching history: {e}")
            messagebox.showerror("Error", f"Failed to search history: {e}")
    
    def view_invoice(self, invoice):
        """View invoice details"""
        # Create invoice view dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Invoice View - {invoice['invoice_number']}")
        dialog.geometry("800x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Invoice details tab
        details_tab = ttk.Frame(notebook)
        notebook.add(details_tab, text="Invoice Details")
        
        # Create invoice details UI
        self.create_invoice_details_ui(details_tab, invoice)
        
        # Payment history tab
        payment_tab = ttk.Frame(notebook)
        notebook.add(payment_tab, text="Payment History")
        
        # Create payment history UI
        self.create_payment_history_ui(payment_tab, invoice["customer_id"])
    
    def create_invoice_details_ui(self, parent, invoice):
        """Create UI for invoice details"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Invoice details
        details_frame = ttk.LabelFrame(main_frame, text="Invoice Details")
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Invoice number
        inv_num_frame = ttk.Frame(details_frame)
        inv_num_frame.pack(fill=tk.X, padx=5, pady=2)
        inv_label = ttk.Label(inv_num_frame, text="Invoice #:", width=15)
        inv_label.pack(side=tk.LEFT)
        ttk.Label(inv_num_frame, text=invoice["invoice_number"]).pack(side=tk.LEFT)
        
        # Date
        date_frame = ttk.Frame(details_frame)
        date_frame.pack(fill=tk.X, padx=5, pady=2)
        date_label = ttk.Label(date_frame, text="Date:", width=15)
        date_label.pack(side=tk.LEFT)
        # Format date for display
        try:
            date_obj = datetime.strptime(invoice["date"], "%Y-%m-%d")
            display_date = date_obj.strftime("%d/%m/%Y")
        except:
            display_date = invoice["date"]
        ttk.Label(date_frame, text=display_date).pack(side=tk.LEFT)
        
        # Customer
        cust_frame = ttk.Frame(details_frame)
        cust_frame.pack(fill=tk.X, padx=5, pady=2)
        cust_label = ttk.Label(cust_frame, text="Customer:", width=15)
        cust_label.pack(side=tk.LEFT)
        ttk.Label(cust_frame, text=invoice["customer_name"]).pack(side=tk.LEFT)
        
        # Place
        place_frame = ttk.Frame(details_frame)
        place_frame.pack(fill=tk.X, padx=5, pady=2)
        place_label = ttk.Label(place_frame, text="Place:", width=15)
        place_label.pack(side=tk.LEFT)
        ttk.Label(place_frame, text=invoice["customer_place"] or "").pack(side=tk.LEFT)
        
        # Payment mode
        pay_mode_frame = ttk.Frame(details_frame)
        pay_mode_frame.pack(fill=tk.X, padx=5, pady=2)
        pay_mode_label = ttk.Label(pay_mode_frame, text="Payment Mode:", width=15)
        pay_mode_label.pack(side=tk.LEFT)
        ttk.Label(pay_mode_frame, text=invoice["payment_mode"] or "").pack(side=tk.LEFT)
        
        # P-PAY No.
        ppay_frame = ttk.Frame(details_frame)
        ppay_frame.pack(fill=tk.X, padx=5, pady=2)
        ppay_label = ttk.Label(ppay_frame, text="P-PAY No.:", width=15)
        ppay_label.pack(side=tk.LEFT)
        ttk.Label(ppay_frame, text=invoice["p_pay_no"] or "").pack(side=tk.LEFT)
        
        # Summary
        summary_frame = ttk.LabelFrame(main_frame, text="Summary")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Subtotal
        subtotal_frame = ttk.Frame(summary_frame)
        subtotal_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(subtotal_frame, text="Subtotal:").pack(side=tk.LEFT)
        ttk.Label(subtotal_frame, text=f"{invoice['subtotal']:.2f}").pack(side=tk.RIGHT)
        
        # Extra charges
        extra_frame = ttk.Frame(summary_frame)
        extra_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(extra_frame, text="Extra Charges:").pack(side=tk.LEFT)
        ttk.Label(extra_frame, text=f"{invoice['extra_charges']:.2f}").pack(side=tk.RIGHT)
        
        # Display extra charges breakdown if available
        extra_charges_breakdown = invoice.get("extra_charges_breakdown")
        if extra_charges_breakdown:
            try:
                # Parse the JSON string
                extra_charges = json.loads(extra_charges_breakdown)
                
                for charge_name, charge_amount in extra_charges.items():
                    charge_frame = ttk.Frame(summary_frame)
                    charge_frame.pack(fill=tk.X, padx=5, pady=2)
                    ttk.Label(charge_frame, text=f"  - {charge_name}:").pack(side=tk.LEFT)
                    ttk.Label(charge_frame, text=f"{charge_amount:.2f}").pack(side=tk.RIGHT)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to handle as simple key-value pairs
                try:
                    # Sometimes it might be stored as "key1:value1,key2:value2"
                    if ':' in extra_charges_breakdown:
                        charges = extra_charges_breakdown.split(',')
                        for charge in charges:
                            if ':' in charge:
                                charge_name, charge_amount = charge.split(':', 1)
                                charge_frame = ttk.Frame(summary_frame)
                                charge_frame.pack(fill=tk.X, padx=5, pady=2)
                                ttk.Label(charge_frame, text=f"  - {charge_name.strip()}:").pack(side=tk.LEFT)
                                ttk.Label(charge_frame, text=f"{float(charge_amount):.2f}").pack(side=tk.RIGHT)
                except Exception as e:
                    print(f"Error parsing extra charges breakdown: {e}")
            except Exception as e:
                print(f"Error parsing extra charges breakdown: {e}")
        
        # Round off
        round_frame = ttk.Frame(summary_frame)
        round_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(round_frame, text="Round Off:").pack(side=tk.LEFT)
        ttk.Label(round_frame, text=f"{invoice['round_off']:.2f}").pack(side=tk.RIGHT)
        
        # Total
        total_frame = ttk.Frame(summary_frame)
        total_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(total_frame, text="Total:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(total_frame, text=f"{invoice['total']:.2f}", font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Close button
        close_btn = ttk.Button(action_frame, text="Close", command=parent.destroy)
        close_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def create_payment_history_ui(self, parent, customer_id):
        """Create UI for payment history"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Payment history treeview
        payments_tree = ttk.Treeview(main_frame, columns=("date", "amount", "mode", "reference"), show="headings")
        payments_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        payments_tree.heading("date", text="Date")
        payments_tree.heading("amount", text="Amount")
        payments_tree.heading("mode", text="Mode")
        payments_tree.heading("reference", text="Reference")
        
        # Define columns
        payments_tree.column("date", width=100)
        payments_tree.column("amount", width=100)
        payments_tree.column("mode", width=100)
        payments_tree.column("reference", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=payments_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        payments_tree.configure(yscrollcommand=scrollbar.set)
        
        # Load payment history
        try:
            payments = self.db.get_payments_by_customer(customer_id)
            
            for payment in payments:
                # Format date for display
                try:
                    date_obj = datetime.strptime(payment["date"], "%Y-%m-%d")
                    display_date = date_obj.strftime("%d/%m/%Y")
                except:
                    display_date = payment["date"]
                
                payments_tree.insert("", "end", values=(
                    display_date,
                    f"{payment['amount']:.2f}",
                    payment["mode"],
                    payment["reference"] or ""
                ))
        except Exception as e:
            print(f"Error loading payment history: {e}")
            messagebox.showerror("Error", f"Failed to load payment history: {e}")
        
        # Summary
        summary_frame = ttk.LabelFrame(main_frame, text="Summary")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Get totals
        try:
            # Get total invoice amount
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
            SELECT COALESCE(SUM(total), 0) as total_invoices
            FROM invoices WHERE customer_id = ?
            """, (customer_id,))
            
            result = cursor.fetchone()
            total_invoices = result[0] if result and result[0] is not None else 0
            
            # Get total payments
            cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as total_payments
            FROM payments WHERE customer_id = ?
            """, (customer_id,))
            
            result = cursor.fetchone()
            total_payments = result[0] if result and result[0] is not None else 0
            
            # Calculate outstanding
            outstanding = total_invoices - total_payments
            
            # Display summary
            inv_frame = ttk.Frame(summary_frame)
            inv_frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(inv_frame, text="Total Invoices:").pack(side=tk.LEFT)
            ttk.Label(inv_frame, text=f"{total_invoices:.2f}").pack(side=tk.RIGHT)
            
            pay_frame = ttk.Frame(summary_frame)
            pay_frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(pay_frame, text="Total Payments:").pack(side=tk.LEFT)
            ttk.Label(pay_frame, text=f"{total_payments:.2f}").pack(side=tk.RIGHT)
            
            out_frame = ttk.Frame(summary_frame)
            out_frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(out_frame, text="Outstanding:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
            ttk.Label(out_frame, text=f"{outstanding:.2f}", font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
            
            # Close connection
            conn.close()
            
        except Exception as e:
            print(f"Error calculating payment summary: {e}")
            messagebox.showerror("Error", f"Failed to calculate payment summary: {e}")
    
    def load_outstanding(self):
        """Load outstanding balances for all customers"""
        # Clear existing items
        for item in self.outstanding_tree.get_children():
            self.outstanding_tree.delete(item)
        
        # Get customers with outstanding balances
        try:
            # Use the get_customer_outstanding method from the database
            outstanding_customers = self.db.get_customer_outstanding()
            
            if not outstanding_customers:
                # Insert a row indicating no outstanding balances
                self.outstanding_tree.insert("", "end", values=("No outstanding balances", "", "", "", ""))
                return
            
            for customer in outstanding_customers:
                # Add to treeview
                self.outstanding_tree.insert("", "end", values=(
                    customer["name"],
                    customer["place"] or "",
                    f"{customer['total_invoices']:.2f}",
                    f"{customer['total_payments']:.2f}",
                    f"{customer['outstanding']:.2f}"
                ))
            
        except Exception as e:
            print(f"Error loading outstanding balances: {e}")
            messagebox.showerror("Error", f"Failed to load outstanding balances: {e}")
    
    def view_customer_details(self, event=None):
        """View customer details"""
        selected = self.outstanding_tree.selection()
        if not selected:
            return
        
        # Get customer details
        item = self.outstanding_tree.item(selected[0])
        customer_name = item["values"][0]
        
        # Skip if it's the "No outstanding balances" row
        if customer_name == "No outstanding balances":
            return
        
        # Get customer from database
        try:
            customers = self.db.get_customers()
            customer = None
            for c in customers:
                if c["name"] == customer_name:
                    customer = c
                    break
            
            if not customer:
                messagebox.showerror("Error", "Customer not found")
                return
            
            # Create customer details dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title(f"Customer Details - {customer_name}")
            dialog.geometry("600x400")
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # Customer details
            details_frame = ttk.LabelFrame(dialog, text="Customer Details")
            details_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Name
            name_frame = ttk.Frame(details_frame)
            name_frame.pack(fill=tk.X, padx=5, pady=2)
            name_label = ttk.Label(name_frame, text="Name:", width=10)
            name_label.pack(side=tk.LEFT)
            ttk.Label(name_frame, text=customer["name"]).pack(side=tk.LEFT)
            
            # Place
            place_frame = ttk.Frame(details_frame)
            place_frame.pack(fill=tk.X, padx=5, pady=2)
            place_label = ttk.Label(place_frame, text="Place:", width=10)
            place_label.pack(side=tk.LEFT)
            ttk.Label(place_frame, text=customer["place"] or "").pack(side=tk.LEFT)
            
            # Phone
            phone_frame = ttk.Frame(details_frame)
            phone_frame.pack(fill=tk.X, padx=5, pady=2)
            phone_label = ttk.Label(phone_frame, text="Phone:", width=10)
            phone_label.pack(side=tk.LEFT)
            ttk.Label(phone_frame, text=customer["phone"] or "").pack(side=tk.LEFT)
            
            # GST
            gst_frame = ttk.Frame(details_frame)
            gst_frame.pack(fill=tk.X, padx=5, pady=2)
            gst_label = ttk.Label(gst_frame, text="GST:", width=10)
            gst_label.pack(side=tk.LEFT)
            ttk.Label(gst_frame, text=customer["gst"] or "").pack(side=tk.LEFT)
            
            # Address
            addr_frame = ttk.Frame(details_frame)
            addr_frame.pack(fill=tk.X, padx=5, pady=2)
            addr_label = ttk.Label(addr_frame, text="Address:", width=10)
            addr_label.pack(side=tk.LEFT)
            ttk.Label(addr_frame, text=customer["address"] or "").pack(side=tk.LEFT)
            
            # Financial summary
            summary_frame = ttk.LabelFrame(dialog, text="Financial Summary")
            summary_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Get totals
            try:
                # Get total invoice amount
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                SELECT COALESCE(SUM(total), 0) as total_invoices
                FROM invoices WHERE customer_id = ?
                """, (customer["customer_id"],))
                
                result = cursor.fetchone()
                total_invoices = result[0] if result and result[0] is not None else 0
                
                # Get total payments
                cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) as total_payments
                FROM payments WHERE customer_id = ?
                """, (customer["customer_id"],))
                
                result = cursor.fetchone()
                total_payments = result[0] if result and result[0] is not None else 0
                
                # Calculate outstanding
                outstanding = total_invoices - total_payments
                
                # Display summary
                inv_frame = ttk.Frame(summary_frame)
                inv_frame.pack(fill=tk.X, padx=5, pady=2)
                ttk.Label(inv_frame, text="Total Invoices:").pack(side=tk.LEFT)
                ttk.Label(inv_frame, text=f"{total_invoices:.2f}").pack(side=tk.RIGHT)
                
                pay_frame = ttk.Frame(summary_frame)
                pay_frame.pack(fill=tk.X, padx=5, pady=2)
                ttk.Label(pay_frame, text="Total Payments:").pack(side=tk.LEFT)
                ttk.Label(pay_frame, text=f"{total_payments:.2f}").pack(side=tk.RIGHT)
                
                out_frame = ttk.Frame(summary_frame)
                out_frame.pack(fill=tk.X, padx=5, pady=2)
                ttk.Label(out_frame, text="Outstanding:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
                ttk.Label(out_frame, text=f"{outstanding:.2f}", font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
                
                # Close connection
                conn.close()
                
            except Exception as e:
                print(f"Error calculating payment summary: {e}")
                messagebox.showerror("Error", f"Failed to calculate payment summary: {e}")
            
            # Action buttons
            action_frame = ttk.Frame(dialog)
            action_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # View history button
            history_btn = ttk.Button(action_frame, text="View History", 
                                    command=lambda d=dialog: self.view_customer_history(customer, d))
            history_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Add payment button
            payment_btn = ttk.Button(action_frame, text="Add Payment", 
                                   command=lambda: self.add_payment(customer))
            payment_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Delete customer button
            delete_btn = ttk.Button(action_frame, text="Delete Customer", 
                                  command=lambda: self.delete_customer(customer, dialog))
            delete_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Close button
            close_btn = ttk.Button(action_frame, text="Close", command=dialog.destroy)
            close_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
        except Exception as e:
            print(f"Error viewing customer details: {e}")
            messagebox.showerror("Error", f"Failed to view customer details: {e}")
    
    def delete_customer(self, customer, parent_dialog=None):
        """Delete a customer"""
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete {customer['name']}? "
                              f"The customer will be moved to the recycle bin."):
            try:
                # Get customer data before deletion
                customer_data = self.db.get_customer_by_id(customer["customer_id"])
                
                if customer_data:
                    # Add to recycle bin
                    self.db.add_to_recycle_bin("customers", customer["customer_id"], customer_data)
                    
                    # Delete customer from database
                    success = self.db.delete_customer(customer["customer_id"])
                    
                    if success:
                        # Close parent dialog if provided
                        if parent_dialog:
                            parent_dialog.destroy()
                        
                        # Refresh outstanding
                        self.load_outstanding()
                        
                        # Refresh customers list
                        self.load_customers()
                        
                        messagebox.showinfo("Success", "Customer moved to recycle bin")
                    else:
                        messagebox.showerror("Error", "Could not delete customer")
                else:
                    messagebox.showerror("Error", "Customer not found")
                    
            except Exception as e:
                print(f"Error deleting customer: {e}")
                messagebox.showerror("Error", f"Could not delete customer: {e}")
    
    def view_customer_history(self, customer, parent_dialog=None):
        """View full history for a customer"""
        # Close the parent dialog if provided
        if parent_dialog:
            parent_dialog.destroy()
            
        # Create history dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Customer History - {customer['name']}")
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
                try:
                    date_obj = datetime.strptime(invoice["date"], "%Y-%m-%d")
                    display_date = date_obj.strftime("%d/%m/%Y")
                except:
                    display_date = invoice["date"]
                
                invoices_tree.insert("", "end", values=(
                    invoice["invoice_number"],
                    display_date,
                    f"{invoice['total']:.2f}",
                    invoice["payment_mode"] or ""
                ))
        except Exception as e:
            print(f"Error loading customer invoices: {e}")
            messagebox.showerror("Error", f"Failed to load customer invoices: {e}")
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # View invoice button
        view_btn = ttk.Button(action_frame, text="View Invoice", 
                             command=lambda: self.view_selected_invoice(invoices_tree))
        view_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Close button
        close_btn = ttk.Button(action_frame, text="Close", command=parent.destroy)
        close_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def create_customer_payments_ui(self, parent, customer):
        """Create UI for customer payments"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Payments treeview
        payments_tree = ttk.Treeview(main_frame, columns=("date", "amount", "mode", "reference"), show="headings")
        payments_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        payments_tree.heading("date", text="Date")
        payments_tree.heading("amount", text="Amount")
        payments_tree.heading("mode", text="Mode")
        payments_tree.heading("reference", text="Reference")
        
        # Define columns
        payments_tree.column("date", width=100)
        payments_tree.column("amount", width=100)
        payments_tree.column("mode", width=100)
        payments_tree.column("reference", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=payments_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        payments_tree.configure(yscrollcommand=scrollbar.set)
        
        # Load payments
        try:
            payments = self.db.get_payments_by_customer(customer["customer_id"])
            
            for payment in payments:
                # Format date for display
                try:
                    date_obj = datetime.strptime(payment["date"], "%Y-%m-%d")
                    display_date = date_obj.strftime("%d/%m/%Y")
                except:
                    display_date = payment["date"]
                
                payments_tree.insert("", "end", values=(
                    display_date,
                    f"{payment['amount']:.2f}",
                    payment["mode"],
                    payment["reference"] or ""
                ))
        except Exception as e:
            print(f"Error loading customer payments: {e}")
            messagebox.showerror("Error", f"Failed to load customer payments: {e}")
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add payment button
        add_btn = ttk.Button(action_frame, text="Add Payment", 
                            command=lambda: self.add_payment(customer))
        add_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Close button
        close_btn = ttk.Button(action_frame, text="Close", command=parent.destroy)
        close_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def view_selected_invoice(self, tree):
        """View selected invoice"""
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an invoice to view")
            return
        
        # Get invoice details
        item = tree.item(selected[0])
        invoice_number = item["values"][0]
        
        try:
            # Get invoice from database
            invoice = self.db.get_invoice_by_number(invoice_number)
            
            if not invoice:
                messagebox.showerror("Error", "Invoice not found")
                return
            
            # View invoice
            self.view_invoice(invoice)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not view invoice: {e}")
    
    def add_payment(self, customer):
        """Add a payment for a customer"""
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
        ttk.Entry(dialog, textvariable=notes_var).grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)
        
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
                    # Refresh outstanding
                    self.load_outstanding()
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
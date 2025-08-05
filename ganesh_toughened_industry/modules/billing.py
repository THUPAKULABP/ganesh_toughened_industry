import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
from PIL import Image, ImageTk
import os
from ui_theme import ClaymorphismTheme

class BillingModule:
    def __init__(self, parent, db, app):
        self.parent = parent
        self.db = db
        self.app = app
        self.current_invoice = None
        self.invoice_items = []
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """Create the billing UI with claymorphism style"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ClaymorphismTheme.create_label(
            main_frame, 
            text="BILLING MODULE", 
            style="Title.TLabel"
        )
        title.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ClaymorphismTheme.create_notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        new_invoice_tab = ttk.Frame(notebook)
        invoices_tab = ttk.Frame(notebook)
        
        notebook.add(new_invoice_tab, text="New Invoice")
        notebook.add(invoices_tab, text="View Invoices")
        
        # Create new invoice tab
        self.create_new_invoice_tab(new_invoice_tab)
        
        # Create view invoices tab
        self.create_view_invoices_tab(invoices_tab)
    
    def create_new_invoice_tab(self, parent):
        """Create the new invoice tab with claymorphism style"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Invoice details card
        details_card = ClaymorphismTheme.create_card(main_frame, text="Invoice Details", padding=15)
        details_card.pack(fill=tk.X, pady=(0, 15))
        
        # Invoice details form
        details_form = ttk.Frame(details_card)
        details_form.pack(fill=tk.X)
        
        # Customer selection
        customer_frame = ttk.Frame(details_form)
        customer_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(customer_frame, text="Customer:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.customer_var = tk.StringVar()
        self.customer_combo = ClaymorphismTheme.create_combobox(customer_frame, textvariable=self.customer_var)
        self.customer_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        add_customer_btn = ClaymorphismTheme.create_button(
            customer_frame, 
            text="Add Customer", 
            command=self.add_customer,
            style="Success.TButton"
        )
        add_customer_btn.pack(side=tk.LEFT)
        
        # Date selection
        date_frame = ttk.Frame(details_form)
        date_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(date_frame, text="Date:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        date_entry_frame, date_entry = ClaymorphismTheme.create_date_entry(date_frame, textvariable=self.date_var)
        date_entry_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        # Invoice number
        invoice_frame = ttk.Frame(details_form)
        invoice_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(invoice_frame, text="Invoice #:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.invoice_number_var = tk.StringVar(value=self.db.generate_invoice_number())
        invoice_entry = ClaymorphismTheme.create_entry(invoice_frame, textvariable=self.invoice_number_var)
        invoice_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        generate_btn = ClaymorphismTheme.create_button(
            invoice_frame, 
            text="Generate", 
            command=self.generate_invoice_number
        )
        generate_btn.pack(side=tk.LEFT)
        
        # Items card
        items_card = ClaymorphismTheme.create_card(main_frame, text="Invoice Items", padding=15)
        items_card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Items form
        items_form = ttk.Frame(items_card)
        items_form.pack(fill=tk.X)
        
        # Product selection
        product_frame = ttk.Frame(items_form)
        product_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(product_frame, text="Product:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.product_var = tk.StringVar()
        self.product_combo = ClaymorphismTheme.create_combobox(product_frame, textvariable=self.product_var)
        self.product_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.product_combo.bind("<<ComboboxSelected>>", self.on_product_selected)
        
        # Dimensions
        dimensions_frame = ttk.Frame(items_form)
        dimensions_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(dimensions_frame, text="Dimensions (in inches):", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        # Height
        height_frame = ttk.Frame(dimensions_frame)
        height_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ClaymorphismTheme.create_label(height_frame, text="Height:").pack(side=tk.LEFT)
        self.height_var = tk.StringVar()
        height_entry = ClaymorphismTheme.create_numeric_entry(height_frame, textvariable=self.height_var, width=8)
        height_entry.pack(side=tk.LEFT)
        
        # Width
        width_frame = ttk.Frame(dimensions_frame)
        width_frame.pack(side=tk.LEFT)
        
        ClaymorphismTheme.create_label(width_frame, text="Width:").pack(side=tk.LEFT)
        self.width_var = tk.StringVar()
        width_entry = ClaymorphismTheme.create_numeric_entry(width_frame, textvariable=self.width_var, width=8)
        width_entry.pack(side=tk.LEFT)
        
        # Rate
        rate_frame = ttk.Frame(items_form)
        rate_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(rate_frame, text="Rate (₹/sqft):", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.rate_var = tk.StringVar()
        rate_entry = ClaymorphismTheme.create_numeric_entry(rate_frame, textvariable=self.rate_var, width=10)
        rate_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Calculate button
        calculate_btn = ClaymorphismTheme.create_button(
            rate_frame, 
            text="Calculate", 
            command=self.calculate_item,
            style="Secondary.TButton"
        )
        calculate_btn.pack(side=tk.LEFT)
        
        # Quantity
        quantity_frame = ttk.Frame(items_form)
        quantity_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(quantity_frame, text="Quantity:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.quantity_var = tk.StringVar(value="1")
        quantity_entry = ClaymorphismTheme.create_numeric_entry(quantity_frame, textvariable=self.quantity_var, width=8)
        quantity_entry.pack(side=tk.LEFT)
        
        # Amount
        amount_frame = ttk.Frame(items_form)
        amount_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(amount_frame, text="Amount (₹):", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.amount_var = tk.StringVar()
        amount_entry = ClaymorphismTheme.create_numeric_entry(amount_frame, textvariable=self.amount_var, width=12)
        amount_entry.pack(side=tk.LEFT)
        
        # Add item button
        add_item_btn = ClaymorphismTheme.create_button(
            items_form, 
            text="Add Item", 
            command=self.add_item,
            style="Success.TButton"
        )
        add_item_btn.pack(pady=10)
        
        # Items treeview
        items_tree_frame = ttk.Frame(items_card)
        items_tree_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.items_tree, scrollbar = ClaymorphismTheme.create_treeview(
            items_tree_frame, 
            columns=("product", "dimensions", "rate", "sqft", "amount", "quantity", "total")
        )
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Define headings
        self.items_tree.heading("product", text="Product")
        self.items_tree.heading("dimensions", text="Dimensions")
        self.items_tree.heading("rate", text="Rate")
        self.items_tree.heading("sqft", text="Sqft")
        self.items_tree.heading("amount", text="Amount")
        self.items_tree.heading("quantity", text="Quantity")
        self.items_tree.heading("total", text="Total")
        
        # Define columns
        self.items_tree.column("product", width=150)
        self.items_tree.column("dimensions", width=100)
        self.items_tree.column("rate", width=80)
        self.items_tree.column("sqft", width=80)
        self.items_tree.column("amount", width=100)
        self.items_tree.column("quantity", width=80)
        self.items_tree.column("total", width=100)
        
        # Totals card
        totals_card = ClaymorphismTheme.create_card(main_frame, padding=15)
        totals_card.pack(fill=tk.X, pady=(0, 15))
        
        # Totals form
        totals_form = ttk.Frame(totals_card)
        totals_form.pack(fill=tk.X)
        
        # Subtotal
        subtotal_frame = ttk.Frame(totals_form)
        subtotal_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(subtotal_frame, text="Subtotal (₹):", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.subtotal_var = tk.StringVar(value="0.00")
        subtotal_entry = ClaymorphismTheme.create_entry(subtotal_frame, textvariable=self.subtotal_var, width=15)
        subtotal_entry.pack(side=tk.LEFT)
        
        # Extra charges
        extra_frame = ttk.Frame(totals_form)
        extra_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(extra_frame, text="Extra Charges (₹):", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.extra_var = tk.StringVar(value="0.00")
        extra_entry = ClaymorphismTheme.create_entry(extra_frame, textvariable=self.extra_var, width=15)
        extra_entry.pack(side=tk.LEFT)
        
        # Round off
        round_frame = ttk.Frame(totals_form)
        round_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(round_frame, text="Round Off (₹):", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.round_var = tk.StringVar(value="0.00")
        round_entry = ClaymorphismTheme.create_entry(round_frame, textvariable=self.round_var, width=15)
        round_entry.pack(side=tk.LEFT)
        
        # Total
        total_frame = ttk.Frame(totals_form)
        total_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(total_frame, text="Total (₹):", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.total_var = tk.StringVar(value="0.00")
        total_entry = ClaymorphismTheme.create_entry(total_frame, textvariable=self.total_var, width=15)
        total_entry.pack(side=tk.LEFT)
        
        # Calculate total button
        calculate_total_btn = ClaymorphismTheme.create_button(
            total_frame, 
            text="Calculate", 
            command=self.calculate_total,
            style="Secondary.TButton"
        )
        calculate_total_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Payment mode
        payment_frame = ttk.Frame(totals_form)
        payment_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(payment_frame, text="Payment Mode:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.payment_var = tk.StringVar()
        payment_combo = ClaymorphismTheme.create_combobox(payment_frame, textvariable=self.payment_var)
        payment_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        payment_combo["values"] = ["Cash", "Cheque", "Online Transfer", "UPI"]
        
        # P Pay No
        p_pay_frame = ttk.Frame(totals_form)
        p_pay_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(p_pay_frame, text="P Pay No:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.p_pay_var = tk.StringVar()
        p_pay_entry = ClaymorphismTheme.create_entry(p_pay_frame, textvariable=self.p_pay_var)
        p_pay_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Action buttons card
        action_card = ClaymorphismTheme.create_card(main_frame, padding=15)
        action_card.pack(fill=tk.X)
        
        # Action buttons
        action_frame = ttk.Frame(action_card)
        action_frame.pack(fill=tk.X)
        
        # Save button
        save_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Save Invoice", 
            command=self.save_invoice,
            style="Success.TButton"
        )
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Print button
        print_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Print Invoice", 
            command=self.print_invoice,
            style="Secondary.TButton"
        )
        print_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Clear button
        clear_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Clear", 
            command=self.clear_form,
            style="Danger.TButton"
        )
        clear_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Load initial data
        self.load_customers()
        self.load_products()
    
    def create_view_invoices_tab(self, parent):
        """Create the view invoices tab with claymorphism style"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Filter card
        filter_card = ClaymorphismTheme.create_card(main_frame, padding=15)
        filter_card.pack(fill=tk.X, pady=(0, 15))
        
        # Filter frame
        filter_frame = ttk.Frame(filter_card)
        filter_frame.pack(fill=tk.X)
        
        # Customer filter
        customer_frame = ttk.Frame(filter_frame)
        customer_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(customer_frame, text="Customer:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.filter_customer_var = tk.StringVar()
        filter_customer_combo = ClaymorphismTheme.create_combobox(customer_frame, textvariable=self.filter_customer_var)
        filter_customer_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Date range
        date_frame = ttk.Frame(filter_frame)
        date_frame.pack(fill=tk.X, pady=5)
        
        ClaymorphismTheme.create_label(date_frame, text="From:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.from_date_var = tk.StringVar(value=(date.today() - timedelta(days=30)).strftime("%d/%m/%Y"))
        from_date_frame, from_date_entry = ClaymorphismTheme.create_date_entry(date_frame, textvariable=self.from_date_var)
        from_date_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        ClaymorphismTheme.create_label(date_frame, text="To:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.to_date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        to_date_frame, to_date_entry = ClaymorphismTheme.create_date_entry(date_frame, textvariable=self.to_date_var)
        to_date_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        # Search button
        search_btn = ClaymorphismTheme.create_button(
            date_frame, 
            text="Search", 
            command=self.search_invoices
        )
        search_btn.pack(side=tk.LEFT)
        
        # Invoices treeview card
        invoices_card = ClaymorphismTheme.create_card(main_frame, padding=15)
        invoices_card.pack(fill=tk.BOTH, expand=True)
        
        # Invoices treeview
        self.invoices_tree, scrollbar = ClaymorphismTheme.create_treeview(
            invoices_card, 
            columns=("invoice_number", "date", "customer_name", "total", "payment_mode")
        )
        self.invoices_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Define headings
        self.invoices_tree.heading("invoice_number", text="Invoice #")
        self.invoices_tree.heading("date", text="Date")
        self.invoices_tree.heading("customer_name", text="Customer")
        self.invoices_tree.heading("total", text="Total")
        self.invoices_tree.heading("payment_mode", text="Payment Mode")
        
        # Define columns
        self.invoices_tree.column("invoice_number", width=120)
        self.invoices_tree.column("date", width=100)
        self.invoices_tree.column("customer_name", width=150)
        self.invoices_tree.column("total", width=100)
        self.invoices_tree.column("payment_mode", width=100)
        
        # Bind double-click to view details
        self.invoices_tree.bind("<Double-1>", self.view_invoice_details)
        
        # Action buttons card
        action_card = ClaymorphismTheme.create_card(main_frame, padding=15)
        action_card.pack(fill=tk.X, pady=(15, 0))
        
        # Action buttons
        action_frame = ttk.Frame(action_card)
        action_frame.pack(fill=tk.X)
        
        # View details button
        details_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="View Details", 
            command=self.view_selected_invoice,
            style="Secondary.TButton"
        )
        details_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Print button
        print_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Print Invoice", 
            command=self.print_selected_invoice,
            style="Secondary.TButton"
        )
        print_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Delete button
        delete_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Delete", 
            command=self.delete_invoice,
            style="Danger.TButton"
        )
        delete_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Load initial data
        self.load_customers_for_filter()
        self.load_invoices()
    
    def load_customers(self):
        """Load customers into combobox"""
        customers = self.db.get_customers()
        customer_names = [customer["name"] for customer in customers]
        self.customer_combo["values"] = customer_names
    
    def load_customers_for_filter(self):
        """Load customers into filter combobox"""
        customers = self.db.get_customers()
        customer_names = [customer["name"] for customer in customers]
        self.filter_customer_combo["values"] = customer_names
    
    def load_products(self):
        """Load products into combobox"""
        products = self.db.get_products()
        product_names = [product["name"] for product in products]
        self.product_combo["values"] = product_names
    
    def on_product_selected(self, event=None):
        """Handle product selection"""
        product_name = self.product_var.get()
        if product_name:
            products = self.db.get_products()
            for product in products:
                if product["name"] == product_name:
                    self.rate_var.set(str(product["rate_per_sqft"]))
                    break
    
    def calculate_item(self):
        """Calculate item amount"""
        try:
            height = float(self.height_var.get() or 0)
            width = float(self.width_var.get() or 0)
            rate = float(self.rate_var.get() or 0)
            
            # Calculate sqft
            sqft = height * width
            
            # Calculate amount
            amount = sqft * rate
            
            # Update display
            self.amount_var.set(f"{amount:.2f}")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dimensions and rate")
    
    def add_item(self):
        """Add item to invoice"""
        try:
            product_name = self.product_var.get()
            if not product_name:
                messagebox.showerror("Error", "Please select a product")
                return
            
            height = float(self.height_var.get() or 0)
            width = float(self.width_var.get() or 0)
            rate = float(self.rate_var.get() or 0)
            amount = float(self.amount_var.get() or 0)
            quantity = int(self.quantity_var.get() or 1)
            
            # Calculate total
            total = amount * quantity
            
            # Add to items list
            item = {
                "product": product_name,
                "dimensions": f"{height} x {width}",
                "rate": rate,
                "sqft": height * width,
                "amount": amount,
                "quantity": quantity,
                "total": total
            }
            self.invoice_items.append(item)
            
            # Add to treeview
            self.items_tree.insert("", "end", values=(
                product_name,
                f"{height} x {width}",
                f"₹{rate:.2f}",
                f"{height * width:.2f}",
                f"₹{amount:.2f}",
                quantity,
                f"₹{total:.2f}"
            ))
            
            # Clear form
            self.height_var.set("")
            self.width_var.set("")
            self.rate_var.set("")
            self.amount_var.set("")
            self.quantity_var.set("1")
            
            # Update subtotal
            self.update_subtotal()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid values")
    
    def update_subtotal(self):
        """Update subtotal"""
        subtotal = sum(item["total"] for item in self.invoice_items)
        self.subtotal_var.set(f"{subtotal:.2f}")
    
    def calculate_total(self):
        """Calculate total amount"""
        try:
            subtotal = float(self.subtotal_var.get() or 0)
            extra = float(self.extra_var.get() or 0)
            round_off = float(self.round_var.get() or 0)
            
            # Calculate total
            total = subtotal + extra + round_off
            
            # Update display
            self.total_var.set(f"{total:.2f}")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid values")
    
    def generate_invoice_number(self):
        """Generate a new invoice number"""
        self.invoice_number_var.set(self.db.generate_invoice_number())
    
    def add_customer(self):
        """Add a new customer"""
        # Create customer dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Customer")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Apply theme to dialog
        ClaymorphismTheme.setup_theme(dialog)
        
        # Customer details card
        details_card = ClaymorphismTheme.create_card(dialog, text="Customer Details", padding=20)
        details_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Customer details
        ClaymorphismTheme.create_label(details_card, text="Name:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        name_var = tk.StringVar()
        name_entry = ClaymorphismTheme.create_entry(details_card, textvariable=name_var)
        name_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)
        
        ClaymorphismTheme.create_label(details_card, text="Place:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        place_var = tk.StringVar()
        place_entry = ClaymorphismTheme.create_entry(details_card, textvariable=place_var)
        place_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.EW)
        
        ClaymorphismTheme.create_label(details_card, text="Phone:", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        phone_var = tk.StringVar()
        phone_entry = ClaymorphismTheme.create_entry(details_card, textvariable=phone_var)
        phone_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.EW)
        
        ClaymorphismTheme.create_label(details_card, text="GST:", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        gst_var = tk.StringVar()
        gst_entry = ClaymorphismTheme.create_entry(details_card, textvariable=gst_var)
        gst_entry.grid(row=3, column=1, padx=10, pady=10, sticky=tk.EW)
        
        # Buttons card
        button_card = ClaymorphismTheme.create_card(dialog, padding=15)
        button_card.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(button_card)
        button_frame.pack(fill=tk.X)
        
        def save_customer():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Customer name is required")
                return
            
            # Add customer to database
            customer_id = self.db.add_customer(
                name=name,
                place=place_var.get().strip(),
                phone=phone_var.get().strip(),
                gst=gst_var.get().strip()
            )
            
            if customer_id:
                # Refresh customers list
                self.load_customers()
                
                # Set the new customer as selected
                self.customer_var.set(name)
                
                # Close dialog
                dialog.destroy()
                
                messagebox.showinfo("Success", "Customer added successfully")
            else:
                messagebox.showerror("Error", "Could not add customer")
        
        save_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Save", 
            command=save_customer,
            style="Success.TButton"
        )
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        cancel_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Cancel", 
            command=dialog.destroy,
            style="Danger.TButton"
        )
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Configure grid weights
        dialog.columnconfigure(1, weight=1)
    
    def save_invoice(self):
        """Save invoice to database"""
        try:
            # Get customer
            customer_name = self.customer_var.get()
            if not customer_name:
                messagebox.showerror("Error", "Please select a customer")
                return
            
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
            
            # Get date
            date_str = self.date_var.get()
            day, month, year = date_str.split('/')
            invoice_date = date(int(year), int(month), int(day))
            
            # Get invoice details
            invoice_number = self.invoice_number_var.get()
            subtotal = float(self.subtotal_var.get() or 0)
            extra = float(self.extra_var.get() or 0)
            round_off = float(self.round_var.get() or 0)
            total = float(self.total_var.get() or 0)
            payment_mode = self.payment_var.get()
            p_pay_no = self.p_pay_var.get()
            
            # Save invoice
            invoice_id = self.db.add_invoice(
                customer_id=customer_id,
                date=invoice_date,
                invoice_number=invoice_number,
                subtotal=subtotal,
                extra_charges=extra,
                round_off=round_off,
                total=total,
                payment_mode=payment_mode,
                p_pay_no=p_pay_no
            )
            
            if invoice_id:
                # Save invoice items
                for item in self.invoice_items:
                    # Get product ID
                    products = self.db.get_products()
                    product_id = None
                    for product in products:
                        if product["name"] == item["product"]:
                            product_id = product["product_id"]
                            break
                    
                    if product_id:
                        # Calculate dimensions
                        height, width = item["dimensions"].split(" x ")
                        height = float(height)
                        width = float(width)
                        
                        # Save invoice item
                        self.db.add_invoice_item(
                            invoice_id=invoice_id,
                            product_id=product_id,
                            actual_height=height,
                            actual_width=width,
                            chargeable_height=height,
                            chargeable_width=width,
                            sqft=item["sqft"],
                            rate=item["rate"],
                            amount=item["amount"],
                            quantity=item["quantity"]
                        )
                
                # Show success message
                messagebox.showinfo("Success", "Invoice saved successfully")
                
                # Clear form
                self.clear_form()
                
                # Switch to view invoices tab
                self.parent.select(1)  # Index of "View Invoices" tab
                self.load_invoices()
            else:
                messagebox.showerror("Error", "Could not save invoice")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid data: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save invoice: {e}")
    
    def clear_form(self):
        """Clear the form"""
        # Clear variables
        self.customer_var.set("")
        self.date_var.set(date.today().strftime("%d/%m/%Y"))
        self.invoice_number_var.set(self.db.generate_invoice_number())
        self.product_var.set("")
        self.height_var.set("")
        self.width_var.set("")
        self.rate_var.set("")
        self.amount_var.set("")
        self.quantity_var.set("1")
        self.subtotal_var.set("0.00")
        self.extra_var.set("0.00")
        self.round_var.set("0.00")
        self.total_var.set("0.00")
        self.payment_var.set("")
        self.p_pay_var.set("")
        
        # Clear items
        self.invoice_items = []
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
    
    def print_invoice(self):
        """Print the current invoice"""
        if not self.invoice_items:
            messagebox.showinfo("Info", "No items to print")
            return
        
        # Create print dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Print Invoice")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Apply theme to dialog
        ClaymorphismTheme.setup_theme(dialog)
        
        # Print options card
        options_card = ClaymorphismTheme.create_card(dialog, text="Print Options", padding=20)
        options_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Print options
        options_frame = ttk.Frame(options_card)
        options_frame.pack(fill=tk.BOTH, expand=True)
        
        # Copy to clipboard option
        copy_btn = ClaymorphismTheme.create_button(
            options_frame, 
            text="Copy to Clipboard", 
            command=self.copy_invoice_to_clipboard,
            style="Secondary.TButton"
        )
        copy_btn.pack(fill=tk.X, pady=5)
        
        # Save as PDF option
        pdf_btn = ClaymorphismTheme.create_button(
            options_frame, 
            text="Save as PDF", 
            command=self.save_invoice_as_pdf,
            style="Secondary.TButton"
        )
        pdf_btn.pack(fill=tk.X, pady=5)
        
        # Close button
        close_btn = ClaymorphismTheme.create_button(
            options_frame, 
            text="Close", 
            command=dialog.destroy
        )
        close_btn.pack(fill=tk.X, pady=5)
    
    def copy_invoice_to_clipboard(self):
        """Copy invoice to clipboard"""
        try:
            # Generate invoice text
            invoice_text = self.generate_invoice_text()
            
            # Copy to clipboard
            self.parent.clipboard_clear()
            self.parent.clipboard_append(invoice_text)
            
            messagebox.showinfo("Success", "Invoice copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy invoice: {e}")
    
    def save_invoice_as_pdf(self):
        """Save invoice as PDF"""
        try:
            # This is a placeholder for PDF generation
            # In a real implementation, you would use a library like ReportLab
            messagebox.showinfo("Info", "PDF generation would be implemented here")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save PDF: {e}")
    
    def generate_invoice_text(self):
        """Generate invoice text for clipboard"""
        # Get company details
        company_name = self.db.get_setting("company_name") or "GANESH TOUGHENED INDUSTRY"
        company_address = self.db.get_setting("company_address") or ""
        company_phone = self.db.get_setting("company_phone") or ""
        company_gst = self.db.get_setting("company_gst") or ""
        
        # Get customer details
        customer_name = self.customer_var.get()
        customers = self.db.get_customers()
        customer = None
        for c in customers:
            if c["name"] == customer_name:
                customer = c
                break
        
        # Get invoice details
        invoice_number = self.invoice_number_var.get()
        invoice_date = self.date_var.get()
        subtotal = self.subtotal_var.get()
        extra = self.extra_var.get()
        round_off = self.round_var.get()
        total = self.total_var.get()
        payment_mode = self.payment_var.get()
        
        # Generate invoice text
        invoice_text = f"""
{company_name}
{company_address}
Phone: {company_phone}
GSTIN: {company_gst}

--------------------------------------------------
TAX INVOICE
--------------------------------------------------
Invoice No: {invoice_number}
Date: {invoice_date}

Customer: {customer_name}
{customer['place'] if customer else ''}
{customer['phone'] if customer else ''}
GSTIN: {customer['gst'] if customer else ''}

--------------------------------------------------
S.No.  Description          Dimensions   Rate    Sq.ft.  Amount   Qty.    Total
--------------------------------------------------
"""
        
        # Add items
        for i, item in enumerate(self.invoice_items, 1):
            invoice_text += f"{i:5d}  {item['product']:<18} {item['dimensions']:<10} {item['rate']:<7} {item['sqft']:<7} {item['amount']:<8} {item['quantity']:<6} {item['total']:<8}\n"
        
        # Add totals
        invoice_text += f"""
--------------------------------------------------
Subtotal: {subtotal}
Extra Charges: {extra}
Round Off: {round_off}
Total: {total}
Payment Mode: {payment_mode}
--------------------------------------------------
"""
        
        return invoice_text
    
    def load_invoices(self):
        """Load invoices into treeview"""
        # Clear existing items
        for item in self.invoices_tree.get_children():
            self.invoices_tree.delete(item)
        
        # Get filter values
        customer_name = self.filter_customer_var.get()
        from_date_str = self.from_date_var.get()
        to_date_str = self.to_date_var.get()
        
        # Parse dates
        try:
            from_day, from_month, from_year = from_date_str.split('/')
            from_date = date(int(from_year), int(from_month), int(from_day))
            
            to_day, to_month, to_year = to_date_str.split('/')
            to_date = date(int(to_year), int(to_month), int(to_day))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dates in DD/MM/YYYY format")
            return
        
        # Get customer ID if selected
        customer_id = None
        if customer_name:
            customers = self.db.get_customers()
            for customer in customers:
                if customer["name"] == customer_name:
                    customer_id = customer["customer_id"]
                    break
        
        # Get invoices
        invoices = self.db.search_invoices(customer=customer_name, from_date=from_date, to_date=to_date)
        
        # Add to treeview
        for invoice in invoices:
            self.invoices_tree.insert("", "end", values=(
                invoice["invoice_number"],
                invoice["date"].strftime("%d/%m/%Y"),
                invoice["customer_name"],
                f"₹{invoice['total']:.2f}",
                invoice["payment_mode"] or ""
            ), tags=(invoice["invoice_id"],))
    
    def search_invoices(self):
        """Search invoices based on filters"""
        self.load_invoices()
    
    def view_invoice_details(self, event=None):
        """View invoice details"""
        selected = self.invoices_tree.selection()
        if not selected:
            return
        
        # Get invoice ID
        invoice_id = self.invoices_tree.item(selected[0])["tags"][0]
        
        # Get invoice from database
        invoices = self.db.get_invoices()
        invoice = None
        for inv in invoices:
            if inv["invoice_id"] == invoice_id:
                invoice = inv
                break
        
        if not invoice:
            messagebox.showerror("Error", "Invoice not found")
            return
        
        # Get invoice items
        items = self.db.get_invoice_items(invoice_id)
        
        # Create invoice details dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Invoice Details - {invoice['invoice_number']}")
        dialog.geometry("600x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Apply theme to dialog
        ClaymorphismTheme.setup_theme(dialog)
        
        # Invoice details card
        details_card = ClaymorphismTheme.create_card(dialog, text="Invoice Details", padding=20)
        details_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Invoice details
        details_frame = ttk.Frame(details_card)
        details_frame.pack(fill=tk.X)
        
        # Invoice number
        number_frame = ttk.Frame(details_frame)
        number_frame.pack(fill=tk.X, pady=5)
        ClaymorphismTheme.create_label(number_frame, text="Invoice #:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        ClaymorphismTheme.create_label(number_frame, text=invoice["invoice_number"]).pack(side=tk.LEFT)
        
        # Date
        date_frame = ttk.Frame(details_frame)
        date_frame.pack(fill=tk.X, pady=5)
        ClaymorphismTheme.create_label(date_frame, text="Date:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        ClaymorphismTheme.create_label(date_frame, text=invoice["date"].strftime("%d/%m/%Y")).pack(side=tk.LEFT)
        
        # Customer
        customer_frame = ttk.Frame(details_frame)
        customer_frame.pack(fill=tk.X, pady=5)
        ClaymorphismTheme.create_label(customer_frame, text="Customer:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        ClaymorphismTheme.create_label(customer_frame, text=invoice["customer_name"]).pack(side=tk.LEFT)
        
        # Payment mode
        payment_frame = ttk.Frame(details_frame)
        payment_frame.pack(fill=tk.X, pady=5)
        ClaymorphismTheme.create_label(payment_frame, text="Payment Mode:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        ClaymorphismTheme.create_label(payment_frame, text=invoice["payment_mode"] or "").pack(side=tk.LEFT)
        
        # Totals
        totals_frame = ttk.Frame(details_frame)
        totals_frame.pack(fill=tk.X, pady=5)
        ClaymorphismTheme.create_label(totals_frame, text="Subtotal:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        ClaymorphismTheme.create_label(totals_frame, text=f"₹{invoice['subtotal']:.2f}").pack(side=tk.LEFT)
        
        extra_frame = ttk.Frame(details_frame)
        extra_frame.pack(fill=tk.X, pady=5)
        ClaymorphismTheme.create_label(extra_frame, text="Extra Charges:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        ClaymorphismTheme.create_label(extra_frame, text=f"₹{invoice['extra_charges']:.2f}").pack(side=tk.LEFT)
        
        round_frame = ttk.Frame(details_frame)
        round_frame.pack(fill=tk.X, pady=5)
        ClaymorphismTheme.create_label(round_frame, text="Round Off:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        ClaymorphismTheme.create_label(round_frame, text=f"₹{invoice['round_off']:.2f}").pack(side=tk.LEFT)
        
        total_frame = ttk.Frame(details_frame)
        total_frame.pack(fill=tk.X, pady=5)
        ClaymorphismTheme.create_label(total_frame, text="Total:", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        ClaymorphismTheme.create_label(total_frame, text=f"₹{invoice['total']:.2f}").pack(side=tk.LEFT)
        
        # Items card
        items_card = ClaymorphismTheme.create_card(dialog, text="Invoice Items", padding=15)
        items_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Items treeview
        items_tree, scrollbar = ClaymorphismTheme.create_treeview(
            items_card, 
            columns=("product", "dimensions", "rate", "sqft", "amount", "quantity", "total")
        )
        items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Define headings
        items_tree.heading("product", text="Product")
        items_tree.heading("dimensions", text="Dimensions")
        items_tree.heading("rate", text="Rate")
        items_tree.heading("sqft", text="Sqft")
        items_tree.heading("amount", text="Amount")
        items_tree.heading("quantity", text="Quantity")
        items_tree.heading("total", text="Total")
        
        # Define columns
        items_tree.column("product", width=150)
        items_tree.column("dimensions", width=100)
        items_tree.column("rate", width=80)
        items_tree.column("sqft", width=80)
        items_tree.column("amount", width=100)
        items_tree.column("quantity", width=80)
        items_tree.column("total", width=100)
        
        # Add items
        for item in items:
            items_tree.insert("", "end", values=(
                item["product_name"],
                f"{item['actual_height']} x {item['actual_width']}",
                f"₹{item['rate']:.2f}",
                f"{item['sqft']:.2f}",
                f"₹{item['amount']:.2f}",
                item["quantity"],
                f"₹{item['total']:.2f}"
            ))
        
        # Action buttons card
        action_card = ClaymorphismTheme.create_card(dialog, padding=15)
        action_card.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Action buttons
        action_frame = ttk.Frame(action_card)
        action_frame.pack(fill=tk.X)
        
        # Print button
        print_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Print Invoice", 
            command=lambda: self.print_invoice_by_id(invoice_id),
            style="Secondary.TButton"
        )
        print_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Close button
        close_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Close", 
            command=dialog.destroy
        )
        close_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def view_selected_invoice(self):
        """View selected invoice details"""
        selected = self.invoices_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an invoice")
            return
        
        # Get invoice ID
        invoice_id = self.invoices_tree.item(selected[0])["tags"][0]
        
        # View invoice details
        self.view_invoice_details(invoice_id=invoice_id)
    
    def print_selected_invoice(self):
        """Print selected invoice"""
        selected = self.invoices_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an invoice")
            return
        
        # Get invoice ID
        invoice_id = self.invoices_tree.item(selected[0])["tags"][0]
        
        # Print invoice
        self.print_invoice_by_id(invoice_id)
    
    def print_invoice_by_id(self, invoice_id):
        """Print invoice by ID"""
        # Get invoice from database
        invoices = self.db.get_invoices()
        invoice = None
        for inv in invoices:
            if inv["invoice_id"] == invoice_id:
                invoice = inv
                break
        
        if not invoice:
            messagebox.showerror("Error", "Invoice not found")
            return
        
        # Get invoice items
        items = self.db.get_invoice_items(invoice_id)
        
        # Create print dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Print Invoice - {invoice['invoice_number']}")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Apply theme to dialog
        ClaymorphismTheme.setup_theme(dialog)
        
        # Print options card
        options_card = ClaymorphismTheme.create_card(dialog, text="Print Options", padding=20)
        options_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Print options
        options_frame = ttk.Frame(options_card)
        options_frame.pack(fill=tk.BOTH, expand=True)
        
        # Copy to clipboard option
        copy_btn = ClaymorphismTheme.create_button(
            options_frame, 
            text="Copy to Clipboard", 
            command=lambda: self.copy_invoice_to_clipboard_by_id(invoice_id),
            style="Secondary.TButton"
        )
        copy_btn.pack(fill=tk.X, pady=5)
        
        # Save as PDF option
        pdf_btn = ClaymorphismTheme.create_button(
            options_frame, 
            text="Save as PDF", 
            command=lambda: self.save_invoice_as_pdf_by_id(invoice_id),
            style="Secondary.TButton"
        )
        pdf_btn.pack(fill=tk.X, pady=5)
        
        # Close button
        close_btn = ClaymorphismTheme.create_button(
            options_frame, 
            text="Close", 
            command=dialog.destroy
        )
        close_btn.pack(fill=tk.X, pady=5)
    
    def copy_invoice_to_clipboard_by_id(self, invoice_id):
        """Copy invoice to clipboard by ID"""
        try:
            # Get invoice from database
            invoices = self.db.get_invoices()
            invoice = None
            for inv in invoices:
                if inv["invoice_id"] == invoice_id:
                    invoice = inv
                    break
            
            if not invoice:
                messagebox.showerror("Error", "Invoice not found")
                return
            
            # Get invoice items
            items = self.db.get_invoice_items(invoice_id)
            
            # Generate invoice text
            invoice_text = self.generate_invoice_text_by_id(invoice, items)
            
            # Copy to clipboard
            self.parent.clipboard_clear()
            self.parent.clipboard_append(invoice_text)
            
            messagebox.showinfo("Success", "Invoice copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy invoice: {e}")
    
    def save_invoice_as_pdf_by_id(self, invoice_id):
        """Save invoice as PDF by ID"""
        try:
            # This is a placeholder for PDF generation
            # In a real implementation, you would use a library like ReportLab
            messagebox.showinfo("Info", "PDF generation would be implemented here")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save PDF: {e}")
    
    def generate_invoice_text_by_id(self, invoice, items):
        """Generate invoice text for clipboard by ID"""
        # Get company details
        company_name = self.db.get_setting("company_name") or "GANESH TOUGHENED INDUSTRY"
        company_address = self.db.get_setting("company_address") or ""
        company_phone = self.db.get_setting("company_phone") or ""
        company_gst = self.db.get_setting("company_gst") or ""
        
        # Get customer details
        customers = self.db.get_customers()
        customer = None
        for c in customers:
            if c["customer_id"] == invoice["customer_id"]:
                customer = c
                break
        
        # Generate invoice text
        invoice_text = f"""
{company_name}
{company_address}
Phone: {company_phone}
GSTIN: {company_gst}

--------------------------------------------------
TAX INVOICE
--------------------------------------------------
Invoice No: {invoice["invoice_number"]}
Date: {invoice["date"].strftime("%d/%m/%Y")}

Customer: {customer["name"]}
{customer['place'] if customer else ''}
{customer['phone'] if customer else ''}
GSTIN: {customer['gst'] if customer else ''}

--------------------------------------------------
S.No.  Description          Dimensions   Rate    Sq.ft.  Amount   Qty.    Total
--------------------------------------------------
"""
        
        # Add items
        for i, item in enumerate(items, 1):
            invoice_text += f"{i:5d}  {item['product_name']:<18} {item['actual_height']}x{item['actual_width']:<10} {item['rate']:<7} {item['sqft']:<7} {item['amount']:<8} {item['quantity']:<6} {item['total']:<8}\n"
        
        # Add totals
        invoice_text += f"""
--------------------------------------------------
Subtotal: {invoice['subtotal']:.2f}
Extra Charges: {invoice['extra_charges']:.2f}
Round Off: {invoice['round_off']:.2f}
Total: {invoice['total']:.2f}
Payment Mode: {invoice['payment_mode'] or ""}
--------------------------------------------------
"""
        
        return invoice_text
    
    def delete_invoice(self):
        """Delete selected invoice"""
        selected = self.invoices_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an invoice")
            return
        
        # Get invoice ID
        invoice_id = self.invoices_tree.item(selected[0])["tags"][0]
        
        # Get invoice details
        invoices = self.db.get_invoices()
        invoice = None
        for inv in invoices:
            if inv["invoice_id"] == invoice_id:
                invoice = inv
                break
        
        if not invoice:
            messagebox.showerror("Error", "Invoice not found")
            return
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete invoice {invoice['invoice_number']}?"):
            # Delete invoice items first
            conn = sqlite3.connect(self.db.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
            
            # Delete invoice
            cursor.execute("DELETE FROM invoices WHERE invoice_id = ?", (invoice_id,))
            
            conn.commit()
            conn.close()
            
            # Refresh invoices list
            self.load_invoices()
            
            messagebox.showinfo("Success", "Invoice deleted successfully")
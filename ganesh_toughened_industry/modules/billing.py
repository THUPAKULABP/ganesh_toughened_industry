import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import os
import sys
import qrcode
from PIL import Image, ImageTk, ImageDraw
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import subprocess
import platform

class BillingModule:
    def __init__(self, parent, db, app):
        self.parent = parent
        self.db = db
        self.app = app
        self.invoice_items = []
        self.selected_customer = None
        self.selected_product = None
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """Create the billing module UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="CUSTOMER BILLING SYSTEM", style="Title.TLabel")
        title.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        billing_tab = ttk.Frame(notebook)
        history_tab = ttk.Frame(notebook)
        
        notebook.add(billing_tab, text="New Bill")
        notebook.add(history_tab, text="Bill History")
        
        # Create billing form
        self.create_billing_form(billing_tab)
        
        # Create bill history
        self.create_bill_history(history_tab)
    
    def create_billing_form(self, parent):
        """Create the billing form"""
        # Main container
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left column - Customer and product details
        left_frame = ttk.Frame(form_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Customer details
        customer_frame = ttk.LabelFrame(left_frame, text="Customer Details")
        customer_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Customer selection
        customer_select_frame = ttk.Frame(customer_frame)
        customer_select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(customer_select_frame, text="Customer:").pack(side=tk.LEFT)
        
        self.customer_var = tk.StringVar()
        self.customer_combobox = ttk.Combobox(customer_select_frame, textvariable=self.customer_var, state="readonly")
        self.customer_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.customer_combobox.bind("<<ComboboxSelected>>", self.on_customer_selected)
        
        # New customer button
        new_customer_btn = ttk.Button(customer_select_frame, text="New", command=self.add_new_customer)
        new_customer_btn.pack(side=tk.LEFT, padx=5)
        
        # Customer details
        self.customer_details_frame = ttk.Frame(customer_frame)
        self.customer_details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Customer name
        name_frame = ttk.Frame(self.customer_details_frame)
        name_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(name_frame, text="Name:", width=10).pack(side=tk.LEFT)
        self.customer_name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.customer_name_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Customer place
        place_frame = ttk.Frame(self.customer_details_frame)
        place_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(place_frame, text="Place:", width=10).pack(side=tk.LEFT)
        self.customer_place_var = tk.StringVar()
        ttk.Entry(place_frame, textvariable=self.customer_place_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Customer phone
        phone_frame = ttk.Frame(self.customer_details_frame)
        phone_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(phone_frame, text="Phone:", width=10).pack(side=tk.LEFT)
        self.customer_phone_var = tk.StringVar()
        ttk.Entry(phone_frame, textvariable=self.customer_phone_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Customer GST
        gst_frame = ttk.Frame(self.customer_details_frame)
        gst_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(gst_frame, text="GST:", width=10).pack(side=tk.LEFT)
        self.customer_gst_var = tk.StringVar()
        ttk.Entry(gst_frame, textvariable=self.customer_gst_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Invoice details
        invoice_frame = ttk.LabelFrame(left_frame, text="Invoice Details")
        invoice_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Invoice number
        inv_num_frame = ttk.Frame(invoice_frame)
        inv_num_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(inv_num_frame, text="Invoice #:", width=10).pack(side=tk.LEFT)
        self.invoice_number_var = tk.StringVar()
        ttk.Entry(inv_num_frame, textvariable=self.invoice_number_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Date
        date_frame = ttk.Frame(invoice_frame)
        date_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(date_frame, text="Date:", width=10).pack(side=tk.LEFT)
        self.invoice_date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(date_frame, textvariable=self.invoice_date_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Product details
        product_frame = ttk.LabelFrame(left_frame, text="Product Details")
        product_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Product selection
        product_select_frame = ttk.Frame(product_frame)
        product_select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(product_select_frame, text="Product:").pack(side=tk.LEFT)
        
        self.product_var = tk.StringVar()
        self.product_combobox = ttk.Combobox(product_select_frame, textvariable=self.product_var, state="readonly")
        self.product_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.product_combobox.bind("<<ComboboxSelected>>", self.on_product_selected)
        
        # Load products
        self.load_products()
        
        # Size details
        size_frame = ttk.Frame(product_frame)
        size_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Actual size
        actual_size_frame = ttk.LabelFrame(size_frame, text="Actual Size")
        actual_size_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Height
        height_frame = ttk.Frame(actual_size_frame)
        height_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(height_frame, text="Height:").pack(side=tk.LEFT)
        self.actual_height_var = tk.StringVar()
        ttk.Entry(height_frame, textvariable=self.actual_height_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(height_frame, text="(inches)").pack(side=tk.LEFT)
        
        # Width
        width_frame = ttk.Frame(actual_size_frame)
        width_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(width_frame, text="Width:").pack(side=tk.LEFT)
        self.actual_width_var = tk.StringVar()
        ttk.Entry(width_frame, textvariable=self.actual_width_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(width_frame, text="(inches)").pack(side=tk.LEFT)
        
        # Chargeable size
        chargeable_size_frame = ttk.LabelFrame(size_frame, text="Chargeable Size")
        chargeable_size_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Height
        charge_height_frame = ttk.Frame(chargeable_size_frame)
        charge_height_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(charge_height_frame, text="Height:").pack(side=tk.LEFT)
        self.chargeable_height_var = tk.StringVar()
        ttk.Entry(charge_height_frame, textvariable=self.chargeable_height_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(charge_height_frame, text="(inches)").pack(side=tk.LEFT)
        
        # Width
        charge_width_frame = ttk.Frame(chargeable_size_frame)
        charge_width_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(charge_width_frame, text="Width:").pack(side=tk.LEFT)
        self.chargeable_width_var = tk.StringVar()
        ttk.Entry(charge_width_frame, textvariable=self.chargeable_width_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(charge_width_frame, text="(inches)").pack(side=tk.LEFT)
        
        # Calculate button
        calc_btn = ttk.Button(product_frame, text="Calculate SQ.FT", command=self.calculate_sqft)
        calc_btn.pack(pady=5)
        
        # SQ.FT and Rate
        calc_frame = ttk.Frame(product_frame)
        calc_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # SQ.FT
        sqft_frame = ttk.Frame(calc_frame)
        sqft_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(sqft_frame, text="SQ.FT:").pack(side=tk.LEFT)
        self.sqft_var = tk.StringVar()
        ttk.Entry(sqft_frame, textvariable=self.sqft_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Rate
        rate_frame = ttk.Frame(calc_frame)
        rate_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(rate_frame, text="Rate:").pack(side=tk.LEFT)
        self.rate_var = tk.StringVar()
        ttk.Entry(rate_frame, textvariable=self.rate_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Quantity
        qty_frame = ttk.Frame(calc_frame)
        qty_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(qty_frame, text="Qty:").pack(side=tk.LEFT)
        self.quantity_var = tk.StringVar(value="1")
        ttk.Entry(qty_frame, textvariable=self.quantity_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Amount
        amount_frame = ttk.Frame(product_frame)
        amount_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(amount_frame, text="Amount:").pack(side=tk.LEFT)
        self.amount_var = tk.StringVar()
        ttk.Entry(amount_frame, textvariable=self.amount_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Add item button
        add_item_btn = ttk.Button(product_frame, text="Add Item", command=self.add_item)
        add_item_btn.pack(pady=5)
        
        # Right column - Invoice items and summary
        right_frame = ttk.Frame(form_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Invoice items
        items_frame = ttk.LabelFrame(right_frame, text="Invoice Items")
        items_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Items treeview
        self.items_tree = ttk.Treeview(items_frame, columns=("product", "actual_size", "chargeable_size", "sqft", "rate", "qty", "amount"), show="headings")
        self.items_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        self.items_tree.heading("product", text="Product")
        self.items_tree.heading("actual_size", text="Actual Size")
        self.items_tree.heading("chargeable_size", text="Chargeable Size")
        self.items_tree.heading("sqft", text="SQ.FT")
        self.items_tree.heading("rate", text="Rate")
        self.items_tree.heading("qty", text="Qty")
        self.items_tree.heading("amount", text="Amount")
        
        # Define columns
        self.items_tree.column("product", width=150)
        self.items_tree.column("actual_size", width=100)
        self.items_tree.column("chargeable_size", width=100)
        self.items_tree.column("sqft", width=50)
        self.items_tree.column("rate", width=50)
        self.items_tree.column("qty", width=50)
        self.items_tree.column("amount", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        # Delete item button
        delete_item_btn = ttk.Button(items_frame, text="Delete Selected Item", command=self.delete_selected_item)
        delete_item_btn.pack(pady=5)
        
        # Invoice summary
        summary_frame = ttk.LabelFrame(right_frame, text="Invoice Summary")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Subtotal
        subtotal_frame = ttk.Frame(summary_frame)
        subtotal_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(subtotal_frame, text="Subtotal:").pack(side=tk.LEFT)
        self.subtotal_var = tk.StringVar(value="0.00")
        ttk.Entry(subtotal_frame, textvariable=self.subtotal_var, state="readonly").pack(side=tk.RIGHT)
        
        # Extra charges
        extra_frame = ttk.LabelFrame(summary_frame, text="Extra Charges")
        extra_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Cut out charges
        cutout_frame = ttk.Frame(extra_frame)
        cutout_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(cutout_frame, text="Cut Out Charges:").pack(side=tk.LEFT)
        self.cutout_var = tk.StringVar(value="0.00")
        ttk.Entry(cutout_frame, textvariable=self.cutout_var).pack(side=tk.RIGHT)
        
        # Hole charges
        hole_frame = ttk.Frame(extra_frame)
        hole_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(hole_frame, text="Hole Charges:").pack(side=tk.LEFT)
        self.hole_var = tk.StringVar(value="0.00")
        ttk.Entry(hole_frame, textvariable=self.hole_var).pack(side=tk.RIGHT)
        
        # Door handle hole charges
        handle_frame = ttk.Frame(extra_frame)
        handle_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(handle_frame, text="Door Handle Hole Charges:").pack(side=tk.LEFT)
        self.handle_var = tk.StringVar(value="0.00")
        ttk.Entry(handle_frame, textvariable=self.handle_var).pack(side=tk.RIGHT)
        
        # Jumbo size charges
        jumbo_frame = ttk.Frame(extra_frame)
        jumbo_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(jumbo_frame, text="Jumbo Size Charges:").pack(side=tk.LEFT)
        self.jumbo_var = tk.StringVar(value="0.00")
        ttk.Entry(jumbo_frame, textvariable=self.jumbo_var).pack(side=tk.RIGHT)
        
        # Total extra charges
        total_extra_frame = ttk.Frame(extra_frame)
        total_extra_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(total_extra_frame, text="Total Extra Charges:").pack(side=tk.LEFT)
        self.total_extra_var = tk.StringVar(value="0.00")
        ttk.Entry(total_extra_frame, textvariable=self.total_extra_var, state="readonly").pack(side=tk.RIGHT)
        
        # Round off
        round_frame = ttk.Frame(summary_frame)
        round_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(round_frame, text="Round Off:").pack(side=tk.LEFT)
        self.round_var = tk.StringVar(value="0.00")
        ttk.Entry(round_frame, textvariable=self.round_var).pack(side=tk.RIGHT)
        
        # Gross total
        total_frame = ttk.Frame(summary_frame)
        total_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(total_frame, text="Gross Total:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.total_var = tk.StringVar(value="0.00")
        ttk.Entry(total_frame, textvariable=self.total_var, state="readonly", font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
        
        # Calculate total button
        calc_total_btn = ttk.Button(summary_frame, text="Calculate Total", command=self.calculate_total)
        calc_total_btn.pack(pady=5)
        
        # Payment details
        payment_frame = ttk.LabelFrame(right_frame, text="Payment Details")
        payment_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Payment mode
        mode_frame = ttk.Frame(payment_frame)
        mode_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(mode_frame, text="Payment Mode:").pack(side=tk.LEFT)
        self.payment_mode_var = tk.StringVar()
        payment_modes = ["Cash", "UPI", "NEFT", "Cheque", "Other"]
        payment_mode_combo = ttk.Combobox(mode_frame, textvariable=self.payment_mode_var, values=payment_modes, state="readonly")
        payment_mode_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # P-PAY No.
        ppay_frame = ttk.Frame(payment_frame)
        ppay_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(ppay_frame, text="P-PAY No.:").pack(side=tk.LEFT)
        self.ppay_var = tk.StringVar()
        ttk.Entry(ppay_frame, textvariable=self.ppay_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Account info
        account_frame = ttk.Frame(payment_frame)
        account_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Bank details
        bank_name = self.db.get_setting("bank_name") or ""
        bank_account = self.db.get_setting("bank_account") or ""
        bank_ifsc = self.db.get_setting("bank_ifsc") or ""
        bank_branch = self.db.get_setting("bank_branch") or ""
        
        bank_details = f"Bank: {bank_name}\nAccount: {bank_account}\nIFSC: {bank_ifsc}\nBranch: {bank_branch}"
        ttk.Label(account_frame, text=bank_details, justify=tk.LEFT).pack(side=tk.LEFT, padx=5)
        
        # UPI QR code
        upi_frame = ttk.Frame(payment_frame)
        upi_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Generate UPI QR code
        self.upi_qr_label = ttk.Label(upi_frame)
        self.upi_qr_label.pack(side=tk.LEFT, padx=5)
        self.generate_upi_qr()
        
        # UPI payment button
        upi_id = self.db.get_setting("upi_id") or ""
        upi_btn = ttk.Button(upi_frame, text=f"Pay via UPI ({upi_id})", command=self.open_upi_app)
        upi_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Action buttons
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Generate PDF button
        pdf_btn = ttk.Button(action_frame, text="Generate PDF", command=self.generate_pdf)
        pdf_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Save button
        save_btn = ttk.Button(action_frame, text="Save Bill", command=self.save_bill)
        save_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Share button
        share_btn = ttk.Button(action_frame, text="Share Bill", command=self.share_bill)
        share_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # New bill button
        new_btn = ttk.Button(action_frame, text="New Bill", command=self.new_bill)
        new_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Generate invoice number
        self.invoice_number_var.set(self.db.generate_invoice_number())
    
    def create_bill_history(self, parent):
        """Create the bill history tab"""
        # Main container
        history_frame = ttk.Frame(parent)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search frame
        search_frame = ttk.Frame(history_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Customer filter
        ttk.Label(search_frame, text="Customer:").pack(side=tk.LEFT, padx=5)
        self.history_customer_var = tk.StringVar()
        self.history_customer_combo = ttk.Combobox(search_frame, textvariable=self.history_customer_var)
        self.history_customer_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Date range
        ttk.Label(search_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.history_from_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.history_from_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(search_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.history_to_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.history_to_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Search button
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_bills)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Bills treeview
        self.bills_tree = ttk.Treeview(history_frame, columns=("invoice_number", "date", "customer", "total", "payment_mode"), show="headings")
        self.bills_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        self.bills_tree.heading("invoice_number", text="Invoice #")
        self.bills_tree.heading("date", text="Date")
        self.bills_tree.heading("customer", text="Customer")
        self.bills_tree.heading("total", text="Total")
        self.bills_tree.heading("payment_mode", text="Payment Mode")
        
        # Define columns
        self.bills_tree.column("invoice_number", width=100)
        self.bills_tree.column("date", width=100)
        self.bills_tree.column("customer", width=150)
        self.bills_tree.column("total", width=100)
        self.bills_tree.column("payment_mode", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.bills_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.bills_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click to view bill
        self.bills_tree.bind("<Double-1>", self.view_bill)
        
        # Action buttons
        action_frame = ttk.Frame(history_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # View bill button
        view_btn = ttk.Button(action_frame, text="View Bill", command=self.view_bill)
        view_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Print bill button
        print_btn = ttk.Button(action_frame, text="Print Bill", command=self.print_bill)
        print_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Load customers for both tabs
        self.load_customers()
        
        # Load bill history
        self.load_bill_history()
    
    def load_customers(self):
        """Load customers into combobox"""
        customers = self.db.get_customers()
        customer_names = [customer["name"] for customer in customers]
        self.customer_combobox["values"] = customer_names
        
        # Also load for history tab if it exists
        if hasattr(self, 'history_customer_combo'):
            self.history_customer_combo["values"] = customer_names
    
    def load_products(self):
        """Load products into combobox"""
        products = self.db.get_products()
        product_names = [f"{product['name']} ({product['type']})" for product in products]
        self.product_combobox["values"] = product_names
    
    def on_customer_selected(self, event):
        """Handle customer selection"""
        customer_name = self.customer_var.get()
        if customer_name:
            # Get customer details
            customers = self.db.get_customers()
            for customer in customers:
                if customer["name"] == customer_name:
                    self.selected_customer = customer
                    self.customer_name_var.set(customer["name"])
                    self.customer_place_var.set(customer["place"] or "")
                    self.customer_phone_var.set(customer["phone"] or "")
                    self.customer_gst_var.set(customer["gst"] or "")
                    break
    
    def on_product_selected(self, event):
        """Handle product selection"""
        product_name = self.product_var.get()
        if product_name:
            # Get product details
            products = self.db.get_products()
            for product in products:
                if f"{product['name']} ({product['type']})" == product_name:
                    self.selected_product = product
                    self.rate_var.set(str(product["rate_per_sqft"]))
                    break
    
    def calculate_sqft(self):
        """Calculate square footage based on dimensions"""
        try:
            actual_height = float(self.actual_height_var.get())
            actual_width = float(self.actual_width_var.get())
            
            # Calculate actual SQ.FT
            actual_sqft = (actual_height * actual_width) / 144
            
            # Set chargeable size (same as actual for now, but can be modified)
            self.chargeable_height_var.set(self.actual_height_var.get())
            self.chargeable_width_var.set(self.actual_width_var.get())
            
            # Calculate chargeable SQ.FT
            chargeable_height = float(self.chargeable_height_var.get())
            chargeable_width = float(self.chargeable_width_var.get())
            chargeable_sqft = (chargeable_height * chargeable_width) / 144
            
            # Set SQ.FT
            self.sqft_var.set(f"{chargeable_sqft:.2f}")
            
            # Calculate amount
            if self.selected_product:
                rate = self.selected_product["rate_per_sqft"]
                quantity = int(self.quantity_var.get())
                amount = chargeable_sqft * rate * quantity
                self.amount_var.set(f"{amount:.2f}")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dimensions")
    
    def add_item(self):
        """Add item to invoice"""
        if not self.selected_product:
            messagebox.showerror("Error", "Please select a product")
            return
        
        try:
            actual_height = float(self.actual_height_var.get())
            actual_width = float(self.actual_width_var.get())
            chargeable_height = float(self.chargeable_height_var.get())
            chargeable_width = float(self.chargeable_width_var.get())
            sqft = float(self.sqft_var.get())
            rate = float(self.rate_var.get())
            quantity = int(self.quantity_var.get())
            amount = float(self.amount_var.get())
            
            # Add item to list
            item = {
                "product_id": self.selected_product["product_id"],
                "product_name": self.selected_product["name"],
                "actual_height": actual_height,
                "actual_width": actual_width,
                "chargeable_height": chargeable_height,
                "chargeable_width": chargeable_width,
                "sqft": sqft,
                "rate": rate,
                "quantity": quantity,
                "amount": amount
            }
            
            self.invoice_items.append(item)
            
            # Add to treeview
            actual_size = f"{actual_height}\" x {actual_width}\""
            chargeable_size = f"{chargeable_height}\" x {chargeable_width}\""
            
            self.items_tree.insert("", "end", values=(
                self.selected_product["name"],
                actual_size,
                chargeable_size,
                f"{sqft:.2f}",
                f"{rate:.2f}",
                quantity,
                f"{amount:.2f}"
            ))
            
            # Update subtotal
            self.update_subtotal()
            
            # Reset form
            self.actual_height_var.set("")
            self.actual_width_var.set("")
            self.chargeable_height_var.set("")
            self.chargeable_width_var.set("")
            self.sqft_var.set("")
            self.amount_var.set("")
            self.quantity_var.set("1")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid values")
    
    def delete_selected_item(self):
        """Delete selected item from invoice"""
        selected = self.items_tree.selection()
        if selected:
            # Get index
            index = self.items_tree.index(selected[0])
            
            # Remove from list
            if 0 <= index < len(self.invoice_items):
                self.invoice_items.pop(index)
            
            # Remove from treeview
            self.items_tree.delete(selected)
            
            # Update subtotal
            self.update_subtotal()
    
    def update_subtotal(self):
        """Update subtotal based on invoice items"""
        subtotal = sum(item["amount"] for item in self.invoice_items)
        self.subtotal_var.set(f"{subtotal:.2f}")
    
    def calculate_total(self):
        """Calculate total including extra charges and round off"""
        try:
            # Get subtotal
            subtotal = float(self.subtotal_var.get())
            
            # Get extra charges
            cutout = float(self.cutout_var.get())
            hole = float(self.hole_var.get())
            handle = float(self.handle_var.get())
            jumbo = float(self.jumbo_var.get())
            
            # Calculate total extra charges
            total_extra = cutout + hole + handle + jumbo
            self.total_extra_var.set(f"{total_extra:.2f}")
            
            # Get round off
            round_off = float(self.round_var.get())
            
            # Calculate total
            total = subtotal + total_extra + round_off
            self.total_var.set(f"{total:.2f}")
            
            # Update UPI QR code with new total
            self.generate_upi_qr()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid values for extra charges")
    
    def generate_upi_qr(self):
        """Generate UPI QR code"""
        try:
            upi_id = self.db.get_setting("upi_id") or "ganeshtoughened@ybl"
            upi_name = self.db.get_setting("upi_name") or "GANESH TOUGHENED INDUSTRY"
            total = self.total_var.get() or "0.00"
            
            # Create UPI payment string
            upi_string = f"upi://pay?pa={upi_id}&pn={upi_name}&am={total}&cu=INR"
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(upi_string)
            qr.make(fit=True)
            
            # Create an image from the QR Code
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to PhotoImage
            img = img.resize((150, 150), Image.LANCZOS)
            self.upi_qr_photo = ImageTk.PhotoImage(img)
            
            # Update label
            self.upi_qr_label.configure(image=self.upi_qr_photo)
            
        except Exception as e:
            print(f"Error generating UPI QR: {e}")
    
    def open_upi_app(self):
        """Open UPI app for payment"""
        try:
            upi_id = self.db.get_setting("upi_id") or "ganeshtoughened@ybl"
            upi_name = self.db.get_setting("upi_name") or "GANESH TOUGHENED INDUSTRY"
            total = self.total_var.get() or "0.00"
            
            # Create UPI payment string
            upi_string = f"upi://pay?pa={upi_id}&pn={upi_name}&am={total}&cu=INR"
            
            # Open UPI app based on OS
            if platform.system() == "Windows":
                os.startfile(upi_string)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", upi_string])
            else:  # Linux
                subprocess.call(["xdg-open", upi_string])
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not open UPI app: {e}")
    
    def generate_pdf(self):
        """Generate PDF for the invoice"""
        if not self.selected_customer:
            messagebox.showerror("Error", "Please select a customer")
            return
        
        if not self.invoice_items:
            messagebox.showerror("Error", "Please add at least one item")
            return
        
        try:
            # Get file path
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"Invoice_{self.invoice_number_var.get()}.pdf"
            )
            
            if not file_path:
                return
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Company details
            company_name = self.db.get_setting("company_name") or "GANESH TOUGHENED INDUSTRY"
            company_address = self.db.get_setting("company_address") or "Plot no:B13, Industrial Estate, Madanapalli"
            company_phone = self.db.get_setting("company_phone") or "9398530499, 7013374872"
            company_gst = self.db.get_setting("company_gst") or "37EXFPK2395CIZE"
            
            # Company header
            company_data = [
                [Paragraph(f"<b>{company_name}</b>", styles["Heading1"])],
                [Paragraph(company_address, styles["Normal"])],
                [Paragraph(f"Phone: {company_phone}", styles["Normal"])],
                [Paragraph(f"GST: {company_gst}", styles["Normal"])]
            ]
            
            company_table = Table(company_data, colWidths=[6*inch])
            company_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            
            elements.append(company_table)
            elements.append(Spacer(1, 0.2*inch))
            
            # Invoice title
            invoice_title = Paragraph("<b>INVOICE</b>", styles["Heading2"])
            elements.append(invoice_title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Invoice details
            invoice_data = [
                ["Invoice #:", self.invoice_number_var.get()],
                ["Date:", self.invoice_date_var.get()],
                ["Customer:", self.selected_customer["name"]],
                ["Place:", self.selected_customer["place"] or ""],
                ["Phone:", self.selected_customer["phone"] or ""],
                ["GST:", self.selected_customer["gst"] or ""]
            ]
            
            invoice_table = Table(invoice_data, colWidths=[1.5*inch, 4.5*inch])
            invoice_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(invoice_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Items table
            items_data = [["S.No", "Product", "Actual Size", "Chargeable Size", "SQ.FT", "Rate", "Qty", "Amount"]]
            
            for i, item in enumerate(self.invoice_items, 1):
                actual_size = f"{item['actual_height']}\" x {item['actual_width']}\""
                chargeable_size = f"{item['chargeable_height']}\" x {item['chargeable_width']}\""
                
                items_data.append([
                    str(i),
                    item["product_name"],
                    actual_size,
                    chargeable_size,
                    f"{item['sqft']:.2f}",
                    f"{item['rate']:.2f}",
                    str(item["quantity"]),
                    f"{item['amount']:.2f}"
                ])
            
            items_table = Table(items_data, colWidths=[0.5*inch, 1.5*inch, 1*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.5*inch, 0.7*inch])
            items_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(items_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Summary table
            subtotal = float(self.subtotal_var.get())
            cutout = float(self.cutout_var.get())
            hole = float(self.hole_var.get())
            handle = float(self.handle_var.get())
            jumbo = float(self.jumbo_var.get())
            total_extra = float(self.total_extra_var.get())
            round_off = float(self.round_var.get())
            total = float(self.total_var.get())
            
            summary_data = [
                ["Subtotal:", f"{subtotal:.2f}"],
                ["Cut Out Charges:", f"{cutout:.2f}"],
                ["Hole Charges:", f"{hole:.2f}"],
                ["Door Handle Hole Charges:", f"{handle:.2f}"],
                ["Jumbo Size Charges:", f"{jumbo:.2f}"],
                ["Total Extra Charges:", f"{total_extra:.2f}"],
                ["Round Off:", f"{round_off:.2f}"],
                ["<b>Gross Total:</b>", f"<b>{total:.2f}</b>"]
            ]
            
            summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-2, -2), 'RIGHT'),
                ('ALIGN', (1, 0), (-1, -2), 'RIGHT'),
                ('ALIGN', (0, -1), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Payment details
            payment_mode = self.payment_mode_var.get() or ""
            ppay_no = self.ppay_var.get() or ""
            
            payment_data = [
                ["Payment Mode:", payment_mode],
                ["P-PAY No.:", ppay_no]
            ]
            
            payment_table = Table(payment_data, colWidths=[1.5*inch, 4.5*inch])
            payment_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(payment_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Bank details
            bank_name = self.db.get_setting("bank_name") or ""
            bank_account = self.db.get_setting("bank_account") or ""
            bank_ifsc = self.db.get_setting("bank_ifsc") or ""
            bank_branch = self.db.get_setting("bank_branch") or ""
            
            bank_data = [
                ["Bank Details:"],
                [f"Bank: {bank_name}"],
                [f"Account: {bank_account}"],
                [f"IFSC: {bank_ifsc}"],
                [f"Branch: {bank_branch}"]
            ]
            
            bank_table = Table(bank_data, colWidths=[6*inch])
            bank_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(bank_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # UPI details
            upi_id = self.db.get_setting("upi_id") or ""
            upi_name = self.db.get_setting("upi_name") or ""
            
            upi_data = [
                ["UPI Details:"],
                [f"UPI ID: {upi_id}"],
                [f"Name: {upi_name}"]
            ]
            
            upi_table = Table(upi_data, colWidths=[6*inch])
            upi_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(upi_table)
            
            # Build PDF
            doc.build(elements)
            
            messagebox.showinfo("Success", "PDF generated successfully")
            
            # Open PDF
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", file_path])
            else:  # Linux
                subprocess.call(["xdg-open", file_path])
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate PDF: {e}")
    
    def save_bill(self):
        """Save bill to database"""
        if not self.selected_customer:
            messagebox.showerror("Error", "Please select a customer")
            return
        
        if not self.invoice_items:
            messagebox.showerror("Error", "Please add at least one item")
            return
        
        try:
            # Calculate totals
            subtotal = float(self.subtotal_var.get())
            total_extra = float(self.total_extra_var.get())
            round_off = float(self.round_var.get())
            total = float(self.total_var.get())
            
            # Parse date
            date_str = self.invoice_date_var.get()
            day, month, year = date_str.split('/')
            invoice_date = date(int(year), int(month), int(day))
            
            # Get payment details
            payment_mode = self.payment_mode_var.get()
            ppay_no = self.ppay_var.get()
            
            # Add invoice
            invoice_id = self.db.add_invoice(
                customer_id=self.selected_customer["customer_id"],
                date=invoice_date,
                invoice_number=self.invoice_number_var.get(),
                subtotal=subtotal,
                extra_charges=total_extra,
                round_off=round_off,
                total=total,
                payment_mode=payment_mode,
                p_pay_no=ppay_no
            )
            
            if not invoice_id:
                messagebox.showerror("Error", "Could not save invoice")
                return
            
            # Add invoice items
            for item in self.invoice_items:
                self.db.add_invoice_item(
                    invoice_id=invoice_id,
                    product_id=item["product_id"],
                    actual_height=item["actual_height"],
                    actual_width=item["actual_width"],
                    chargeable_height=item["chargeable_height"],
                    chargeable_width=item["chargeable_width"],
                    sqft=item["sqft"],
                    rate=item["rate"],
                    amount=item["amount"],
                    quantity=item["quantity"]
                )
            
            # Add payment if payment mode is provided
            if payment_mode:
                self.db.add_payment(
                    customer_id=self.selected_customer["customer_id"],
                    date=invoice_date,
                    amount=total,
                    mode=payment_mode,
                    reference=ppay_no,
                    invoice_id=invoice_id
                )
            
            # Add to customer visits
            self.db.add_visit(
                customer_id=self.selected_customer["customer_id"],
                name=self.selected_customer["name"],
                city=self.selected_customer["place"],
                purpose="Billing"
            )
            
            # Add to works completed
            for item in self.invoice_items:
                size = f"{item['chargeable_height']}\" x {item['chargeable_width']}\""
                self.db.add_work(
                    invoice_id=invoice_id,
                    date=invoice_date,
                    type=item["product_name"],
                    size=size,
                    quantity=item["quantity"],
                    status="Completed"
                )
            
            # Update inventory
            for item in self.invoice_items:
                self.db.add_inventory(
                    product_id=item["product_id"],
                    date=invoice_date,
                    type="stock_out",
                    quantity=item["quantity"]
                )
            
            messagebox.showinfo("Success", "Bill saved successfully")
            
            # Refresh bill history
            self.load_bill_history()
            
            # Reset form
            self.new_bill()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save bill: {e}")
    
    def share_bill(self):
        """Share bill via system share options"""
        if not self.selected_customer:
            messagebox.showerror("Error", "Please select a customer")
            return
        
        if not self.invoice_items:
            messagebox.showerror("Error", "Please add at least one item")
            return
        
        try:
            # Generate PDF
            file_path = f"Invoice_{self.invoice_number_var.get()}.pdf"
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Company details
            company_name = self.db.get_setting("company_name") or "GANESH TOUGHENED INDUSTRY"
            company_address = self.db.get_setting("company_address") or "Plot no:B13, Industrial Estate, Madanapalli"
            company_phone = self.db.get_setting("company_phone") or "9398530499, 7013374872"
            company_gst = self.db.get_setting("company_gst") or "37EXFPK2395CIZE"
            
            # Company header
            company_data = [
                [Paragraph(f"<b>{company_name}</b>", styles["Heading1"])],
                [Paragraph(company_address, styles["Normal"])],
                [Paragraph(f"Phone: {company_phone}", styles["Normal"])],
                [Paragraph(f"GST: {company_gst}", styles["Normal"])]
            ]
            
            company_table = Table(company_data, colWidths=[6*inch])
            company_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            
            elements.append(company_table)
            elements.append(Spacer(1, 0.2*inch))
            
            # Invoice title
            invoice_title = Paragraph("<b>INVOICE</b>", styles["Heading2"])
            elements.append(invoice_title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Invoice details
            invoice_data = [
                ["Invoice #:", self.invoice_number_var.get()],
                ["Date:", self.invoice_date_var.get()],
                ["Customer:", self.selected_customer["name"]],
                ["Place:", self.selected_customer["place"] or ""],
                ["Phone:", self.selected_customer["phone"] or ""],
                ["GST:", self.selected_customer["gst"] or ""]
            ]
            
            invoice_table = Table(invoice_data, colWidths=[1.5*inch, 4.5*inch])
            invoice_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(invoice_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Items table
            items_data = [["S.No", "Product", "Actual Size", "Chargeable Size", "SQ.FT", "Rate", "Qty", "Amount"]]
            
            for i, item in enumerate(self.invoice_items, 1):
                actual_size = f"{item['actual_height']}\" x {item['actual_width']}\""
                chargeable_size = f"{item['chargeable_height']}\" x {item['chargeable_width']}\""
                
                items_data.append([
                    str(i),
                    item["product_name"],
                    actual_size,
                    chargeable_size,
                    f"{item['sqft']:.2f}",
                    f"{item['rate']:.2f}",
                    str(item["quantity"]),
                    f"{item['amount']:.2f}"
                ])
            
            items_table = Table(items_data, colWidths=[0.5*inch, 1.5*inch, 1*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.5*inch, 0.7*inch])
            items_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(items_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Summary table
            subtotal = float(self.subtotal_var.get())
            cutout = float(self.cutout_var.get())
            hole = float(self.hole_var.get())
            handle = float(self.handle_var.get())
            jumbo = float(self.jumbo_var.get())
            total_extra = float(self.total_extra_var.get())
            round_off = float(self.round_var.get())
            total = float(self.total_var.get())
            
            summary_data = [
                ["Subtotal:", f"{subtotal:.2f}"],
                ["Cut Out Charges:", f"{cutout:.2f}"],
                ["Hole Charges:", f"{hole:.2f}"],
                ["Door Handle Hole Charges:", f"{handle:.2f}"],
                ["Jumbo Size Charges:", f"{jumbo:.2f}"],
                ["Total Extra Charges:", f"{total_extra:.2f}"],
                ["Round Off:", f"{round_off:.2f}"],
                ["<b>Gross Total:</b>", f"<b>{total:.2f}</b>"]
            ]
            
            summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-2, -2), 'RIGHT'),
                ('ALIGN', (1, 0), (-1, -2), 'RIGHT'),
                ('ALIGN', (0, -1), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Payment details
            payment_mode = self.payment_mode_var.get() or ""
            ppay_no = self.ppay_var.get() or ""
            
            payment_data = [
                ["Payment Mode:", payment_mode],
                ["P-PAY No.:", ppay_no]
            ]
            
            payment_table = Table(payment_data, colWidths=[1.5*inch, 4.5*inch])
            payment_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(payment_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Bank details
            bank_name = self.db.get_setting("bank_name") or ""
            bank_account = self.db.get_setting("bank_account") or ""
            bank_ifsc = self.db.get_setting("bank_ifsc") or ""
            bank_branch = self.db.get_setting("bank_branch") or ""
            
            bank_data = [
                ["Bank Details:"],
                [f"Bank: {bank_name}"],
                [f"Account: {bank_account}"],
                [f"IFSC: {bank_ifsc}"],
                [f"Branch: {bank_branch}"]
            ]
            
            bank_table = Table(bank_data, colWidths=[6*inch])
            bank_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(bank_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # UPI details
            upi_id = self.db.get_setting("upi_id") or ""
            upi_name = self.db.get_setting("upi_name") or ""
            
            upi_data = [
                ["UPI Details:"],
                [f"UPI ID: {upi_id}"],
                [f"Name: {upi_name}"]
            ]
            
            upi_table = Table(upi_data, colWidths=[6*inch])
            upi_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(upi_table)
            
            # Build PDF
            doc.build(elements)
            
            # Share file based on OS
            if platform.system() == "Windows":
                os.startfile(f"explorer.exe /select,\"{file_path}\"")
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", "-R", file_path])
            else:  # Linux
                subprocess.call(["xdg-open", file_path])
                
            messagebox.showinfo("Success", "Bill generated and ready to share")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not share bill: {e}")
    
    def new_bill(self):
        """Reset form for new bill"""
        # Reset customer
        self.customer_var.set("")
        self.selected_customer = None
        self.customer_name_var.set("")
        self.customer_place_var.set("")
        self.customer_phone_var.set("")
        self.customer_gst_var.set("")
        
        # Reset product
        self.product_var.set("")
        self.selected_product = None
        self.actual_height_var.set("")
        self.actual_width_var.set("")
        self.chargeable_height_var.set("")
        self.chargeable_width_var.set("")
        self.sqft_var.set("")
        self.rate_var.set("")
        self.quantity_var.set("1")
        self.amount_var.set("")
        
        # Clear invoice items
        self.invoice_items = []
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Reset summary
        self.subtotal_var.set("0.00")
        self.cutout_var.set("0.00")
        self.hole_var.set("0.00")
        self.handle_var.set("0.00")
        self.jumbo_var.set("0.00")
        self.total_extra_var.set("0.00")
        self.round_var.set("0.00")
        self.total_var.set("0.00")
        
        # Reset payment
        self.payment_mode_var.set("")
        self.ppay_var.set("")
        
        # Generate new invoice number
        self.invoice_number_var.set(self.db.generate_invoice_number())
        
        # Update UPI QR code
        self.generate_upi_qr()
    
    def load_bill_history(self):
        """Load bill history from database"""
        # Clear existing items
        for item in self.bills_tree.get_children():
            self.bills_tree.delete(item)
        
        # Get bills from database
        bills = self.db.get_invoices()
        
        # Add bills to treeview
        for bill in bills:
            self.bills_tree.insert("", "end", values=(
                bill["invoice_number"],
                bill["date"].strftime("%d/%m/%Y"),
                bill["customer_name"],
                f"{bill['total']:.2f}",
                bill["payment_mode"] or ""
            ))
    
    def search_bills(self):
        """Search bills based on criteria"""
        # Get search criteria
        customer = self.history_customer_var.get()
        from_date = self.history_from_var.get()
        to_date = self.history_to_var.get()
        
        # Clear existing items
        for item in self.bills_tree.get_children():
            self.bills_tree.delete(item)
        
        # Get bills from database
        bills = self.db.search_invoices(customer, from_date, to_date)
        
        # Add bills to treeview
        for bill in bills:
            self.bills_tree.insert("", "end", values=(
                bill["invoice_number"],
                bill["date"].strftime("%d/%m/%Y"),
                bill["customer_name"],
                f"{bill['total']:.2f}",
                bill["payment_mode"] or ""
            ))
    
    def view_bill(self, event=None):
        """View selected bill"""
        # Get selected bill
        selected = self.bills_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a bill to view")
            return
        
        # Get invoice number
        invoice_number = self.bills_tree.item(selected[0])["values"][0]
        
        # Get invoice details
        invoice = self.db.get_invoice_by_number(invoice_number)
        if not invoice:
            messagebox.showerror("Error", "Invoice not found")
            return
        
        # Get invoice items
        items = self.db.get_invoice_items(invoice["invoice_id"])
        
        # Switch to billing tab
        # Note: This would require access to the notebook widget
        # For now, we'll just show the invoice details in a message box
        
        # Create message
        message = f"Invoice #: {invoice['invoice_number']}\n"
        message += f"Date: {invoice['date'].strftime('%d/%m/%Y')}\n"
        message += f"Customer: {invoice['customer_name']}\n"
        message += f"Total: {invoice['total']:.2f}\n"
        message += f"Payment Mode: {invoice['payment_mode'] or 'N/A'}\n\n"
        
        message += "Items:\n"
        for item in items:
            message += f"- {item['product_name']}: {item['quantity']} x {item['sqft']:.2f} sq.ft @ {item['rate']:.2f} = {item['amount']:.2f}\n"
        
        messagebox.showinfo("Invoice Details", message)
    
    def print_bill(self):
        """Print selected bill"""
        # Get selected bill
        selected = self.bills_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a bill to print")
            return
        
        # Get invoice number
        invoice_number = self.bills_tree.item(selected[0])["values"][0]
        
        # Get invoice details
        invoice = self.db.get_invoice_by_number(invoice_number)
        if not invoice:
            messagebox.showerror("Error", "Invoice not found")
            return
        
        # Generate PDF and print
        try:
            # Create temporary PDF file
            file_path = f"temp_invoice_{invoice_number}.pdf"
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Company details
            company_name = self.db.get_setting("company_name") or "GANESH TOUGHENED INDUSTRY"
            company_address = self.db.get_setting("company_address") or "Plot no:B13, Industrial Estate, Madanapalli"
            company_phone = self.db.get_setting("company_phone") or "9398530499, 7013374872"
            company_gst = self.db.get_setting("company_gst") or "37EXFPK2395CIZE"
            
            # Company header
            company_data = [
                [Paragraph(f"<b>{company_name}</b>", styles["Heading1"])],
                [Paragraph(company_address, styles["Normal"])],
                [Paragraph(f"Phone: {company_phone}", styles["Normal"])],
                [Paragraph(f"GST: {company_gst}", styles["Normal"])]
            ]
            
            company_table = Table(company_data, colWidths=[6*inch])
            company_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            
            elements.append(company_table)
            elements.append(Spacer(1, 0.2*inch))
            
            # Invoice title
            invoice_title = Paragraph("<b>INVOICE</b>", styles["Heading2"])
            elements.append(invoice_title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Invoice details
            invoice_data = [
                ["Invoice #:", invoice["invoice_number"]],
                ["Date:", invoice["date"].strftime("%d/%m/%Y")],
                ["Customer:", invoice["customer_name"]],
                ["Place:", invoice["customer_place"] or ""],
                ["Phone:", invoice["customer_phone"] or ""],
                ["GST:", invoice["customer_gst"] or ""]
            ]
            
            invoice_table = Table(invoice_data, colWidths=[1.5*inch, 4.5*inch])
            invoice_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(invoice_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Get invoice items
            items = self.db.get_invoice_items(invoice["invoice_id"])
            
            # Items table
            items_data = [["S.No", "Product", "Actual Size", "Chargeable Size", "SQ.FT", "Rate", "Qty", "Amount"]]
            
            for i, item in enumerate(items, 1):
                actual_size = f"{item['actual_height']}\" x {item['actual_width']}\""
                chargeable_size = f"{item['chargeable_height']}\" x {item['chargeable_width']}\""
                
                items_data.append([
                    str(i),
                    item["product_name"],
                    actual_size,
                    chargeable_size,
                    f"{item['sqft']:.2f}",
                    f"{item['rate']:.2f}",
                    str(item["quantity"]),
                    f"{item['amount']:.2f}"
                ])
            
            items_table = Table(items_data, colWidths=[0.5*inch, 1.5*inch, 1*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.5*inch, 0.7*inch])
            items_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(items_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Summary table
            summary_data = [
                ["Subtotal:", f"{invoice['subtotal']:.2f}"],
                ["Extra Charges:", f"{invoice['extra_charges']:.2f}"],
                ["Round Off:", f"{invoice['round_off']:.2f}"],
                ["<b>Gross Total:</b>", f"<b>{invoice['total']:.2f}</b>"]
            ]
            
            summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-2, -2), 'RIGHT'),
                ('ALIGN', (1, 0), (-1, -2), 'RIGHT'),
                ('ALIGN', (0, -1), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Payment details
            payment_data = [
                ["Payment Mode:", invoice["payment_mode"] or ""],
                ["P-PAY No.:", invoice["p_pay_no"] or ""]
            ]
            
            payment_table = Table(payment_data, colWidths=[1.5*inch, 4.5*inch])
            payment_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(payment_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Bank details
            bank_name = self.db.get_setting("bank_name") or ""
            bank_account = self.db.get_setting("bank_account") or ""
            bank_ifsc = self.db.get_setting("bank_ifsc") or ""
            bank_branch = self.db.get_setting("bank_branch") or ""
            
            bank_data = [
                ["Bank Details:"],
                [f"Bank: {bank_name}"],
                [f"Account: {bank_account}"],
                [f"IFSC: {bank_ifsc}"],
                [f"Branch: {bank_branch}"]
            ]
            
            bank_table = Table(bank_data, colWidths=[6*inch])
            bank_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(bank_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # UPI details
            upi_id = self.db.get_setting("upi_id") or ""
            upi_name = self.db.get_setting("upi_name") or ""
            
            upi_data = [
                ["UPI Details:"],
                [f"UPI ID: {upi_id}"],
                [f"Name: {upi_name}"]
            ]
            
            upi_table = Table(upi_data, colWidths=[6*inch])
            upi_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(upi_table)
            
            # Build PDF
            doc.build(elements)
            
            # Print PDF based on OS
            if platform.system() == "Windows":
                os.startfile(file_path, "print")
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["lpr", file_path])
            else:  # Linux
                subprocess.call(["lpr", file_path])
                
            messagebox.showinfo("Success", "Bill sent to printer")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not print bill: {e}")
    
    def add_new_customer(self):
        """Add a new customer"""
        # Create a new window for adding customer
        customer_window = tk.Toplevel(self.parent)
        customer_window.title("Add New Customer")
        customer_window.geometry("400x300")
        customer_window.resizable(False, False)
        
        # Make window modal
        customer_window.transient(self.parent)
        customer_window.grab_set()
        
        # Customer form
        form_frame = ttk.Frame(customer_window, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="Name:").pack(side=tk.LEFT)
        name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=name_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Place
        place_frame = ttk.Frame(form_frame)
        place_frame.pack(fill=tk.X, pady=5)
        ttk.Label(place_frame, text="Place:").pack(side=tk.LEFT)
        place_var = tk.StringVar()
        ttk.Entry(place_frame, textvariable=place_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Phone
        phone_frame = ttk.Frame(form_frame)
        phone_frame.pack(fill=tk.X, pady=5)
        ttk.Label(phone_frame, text="Phone:").pack(side=tk.LEFT)
        phone_var = tk.StringVar()
        ttk.Entry(phone_frame, textvariable=phone_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # GST
        gst_frame = ttk.Frame(form_frame)
        gst_frame.pack(fill=tk.X, pady=5)
        ttk.Label(gst_frame, text="GST:").pack(side=tk.LEFT)
        gst_var = tk.StringVar()
        ttk.Entry(gst_frame, textvariable=gst_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Address
        address_frame = ttk.Frame(form_frame)
        address_frame.pack(fill=tk.X, pady=5)
        ttk.Label(address_frame, text="Address:").pack(side=tk.LEFT)
        address_var = tk.StringVar()
        ttk.Entry(address_frame, textvariable=address_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Email
        email_frame = ttk.Frame(form_frame)
        email_frame.pack(fill=tk.X, pady=5)
        ttk.Label(email_frame, text="Email:").pack(side=tk.LEFT)
        email_var = tk.StringVar()
        ttk.Entry(email_frame, textvariable=email_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def save_customer():
            # Validate inputs
            if not name_var.get():
                messagebox.showerror("Error", "Name is required")
                return
            
            # Add customer to database
            customer_id = self.db.add_customer(
                name=name_var.get(),
                place=place_var.get(),
                phone=phone_var.get(),
                gst=gst_var.get(),
                address=address_var.get(),
                email=email_var.get()
            )
            
            if customer_id:
                messagebox.showinfo("Success", "Customer added successfully")
                customer_window.destroy()
                
                # Refresh customer list
                self.load_customers()
                
                # Select the new customer
                self.customer_var.set(name_var.get())
                self.on_customer_selected(None)
            else:
                messagebox.showerror("Error", "Could not add customer")
        
        save_btn = ttk.Button(button_frame, text="Save", command=save_customer)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=customer_window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
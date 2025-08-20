import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import os
import sys
import qrcode
from PIL import Image, ImageTk, ImageDraw
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
import subprocess
import platform
import json
import threading
import sqlite3
from .share_utils import ShareUtils  # Fixed import path

class BillingModule:
    def __init__(self, parent, db, app):
        self.parent = parent
        self.db = db
        self.app = app
        self.invoice_items = []
        self.selected_customer = None
        self.selected_product = None
        self.draft_file = "draft_bill.json"
        self.auto_save_interval = 60  # seconds
        self.last_saved_invoice = None  # Store the last saved invoice for PDF generation
        self.last_pdf_path = None  # Store the path to the last generated PDF
        
        # Create UI
        self.create_ui()
        
        # Load draft if exists
        self.load_draft()
        
        # Start auto-save timer
        self.auto_save_timer = None
        self.start_auto_save()
    
    def create_ui(self):
        """Create the billing module UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="CUSTOMER BILLING SYSTEM", style="Title.TLabel")
        title.pack(pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        billing_tab = ttk.Frame(self.notebook)
        history_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(billing_tab, text="New Bill")
        self.notebook.add(history_tab, text="Bill History")
        
        # Create billing form with scrolling
        self.create_billing_form(billing_tab)
        
        # Create bill history
        self.create_bill_history(history_tab)
    
    def create_billing_form(self, parent):
        """Create the billing form with scrolling"""
        # Create a canvas and scrollbar for the billing form
        self.canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure the scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Enable mouse wheel scrolling - Fixed to work properly
        def _on_mousewheel(event):
            # Handle both Windows and Linux scrolling
            if event.num == 5 or event.delta == -120:
                self.canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta == 120:
                self.canvas.yview_scroll(-1, "units")
        
        # Bind to all widgets for consistent scrolling
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.canvas.bind_all("<Button-4>", _on_mousewheel)
        self.canvas.bind_all("<Button-5>", _on_mousewheel)
        
        # Now create the form content in the scrollable frame
        self.create_form_content(scrollable_frame)
    
    def create_form_content(self, parent):
        """Create the actual form content inside the scrollable frame"""
        # Main container with proper layout
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create paned window for resizable left and right sections
        paned_window = ttk.PanedWindow(form_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Customer and product details
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # Right column - Invoice items and summary
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)
        
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
        
        # New/Edit/Delete customer buttons - Added Delete button
        button_frame = ttk.Frame(customer_select_frame)
        button_frame.pack(side=tk.LEFT, padx=5)
        new_customer_btn = ttk.Button(button_frame, text="New", command=self.add_new_customer)
        new_customer_btn.pack(side=tk.TOP, padx=5)
        edit_customer_btn = ttk.Button(button_frame, text="Edit", command=self.edit_customer)
        edit_customer_btn.pack(side=tk.TOP, padx=5)
        delete_customer_btn = ttk.Button(button_frame, text="Delete", command=self.delete_customer)
        delete_customer_btn.pack(side=tk.TOP, padx=5)
        
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
        
        # Customer Email - Added this section
        email_frame = ttk.Frame(self.customer_details_frame)
        email_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(email_frame, text="Email:", width=10).pack(side=tk.LEFT)
        self.customer_email_var = tk.StringVar()
        ttk.Entry(email_frame, textvariable=self.customer_email_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
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
        self.actual_height_var.trace('w', self.update_chargeable_size)
        
        # Width
        width_frame = ttk.Frame(actual_size_frame)
        width_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(width_frame, text="Width:").pack(side=tk.LEFT)
        self.actual_width_var = tk.StringVar()
        ttk.Entry(width_frame, textvariable=self.actual_width_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(width_frame, text="(inches)").pack(side=tk.LEFT)
        self.actual_width_var.trace('w', self.update_chargeable_size)
        
        # Chargeable size
        chargeable_size_frame = ttk.LabelFrame(size_frame, text="Chargeable Size")
        chargeable_size_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Height
        charge_height_frame = ttk.Frame(chargeable_size_frame)
        charge_height_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(charge_height_frame, text="Height:").pack(side=tk.LEFT)
        self.chargeable_height_var = tk.StringVar()
        ttk.Entry(charge_height_frame, textvariable=self.chargeable_height_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(charge_height_frame, text="(inches)").pack(side=tk.LEFT)
        
        # Width
        charge_width_frame = ttk.Frame(chargeable_size_frame)
        charge_width_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(charge_width_frame, text="Width:").pack(side=tk.LEFT)
        self.chargeable_width_var = tk.StringVar()
        ttk.Entry(charge_width_frame, textvariable=self.chargeable_width_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
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
        
        # Invoice items
        items_frame = ttk.LabelFrame(right_frame, text="Invoice Items")
        items_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Items treeview with scrollbar
        tree_frame = ttk.Frame(items_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.items_tree = ttk.Treeview(tree_frame, columns=("product", "actual_size", "chargeable_size", "sqft", "rounded_sqft", "rate", "qty", "amount"), show="headings")
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Define headings
        self.items_tree.heading("product", text="Product")
        self.items_tree.heading("actual_size", text="Actual Size")
        self.items_tree.heading("chargeable_size", text="Chargeable Size")
        self.items_tree.heading("sqft", text="SQ.FT")
        self.items_tree.heading("rounded_sqft", text="Rounded SQ.FT")
        self.items_tree.heading("rate", text="Rate")
        self.items_tree.heading("qty", text="Qty")
        self.items_tree.heading("amount", text="Amount")
        
        # Define columns
        self.items_tree.column("product", width=150)
        self.items_tree.column("actual_size", width=100)
        self.items_tree.column("chargeable_size", width=100)
        self.items_tree.column("sqft", width=50)
        self.items_tree.column("rounded_sqft", width=80)
        self.items_tree.column("rate", width=50)
        self.items_tree.column("qty", width=50)
        self.items_tree.column("amount", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
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
        self.cutout_var.trace('w', self.update_total)
        
        # Hole charges
        hole_frame = ttk.Frame(extra_frame)
        hole_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(hole_frame, text="Hole Charges:").pack(side=tk.LEFT)
        self.hole_var = tk.StringVar(value="0.00")
        ttk.Entry(hole_frame, textvariable=self.hole_var).pack(side=tk.RIGHT)
        self.hole_var.trace('w', self.update_total)
        
        # Door handle hole charges
        handle_frame = ttk.Frame(extra_frame)
        handle_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(handle_frame, text="Door Handle Hole Charges:").pack(side=tk.LEFT)
        self.handle_var = tk.StringVar(value="0.00")
        ttk.Entry(handle_frame, textvariable=self.handle_var).pack(side=tk.RIGHT)
        self.handle_var.trace('w', self.update_total)
        
        # Jumbo size charges
        jumbo_frame = ttk.Frame(extra_frame)
        jumbo_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(jumbo_frame, text="Jumbo Size Charges:").pack(side=tk.LEFT)
        self.jumbo_var = tk.StringVar(value="0.00")
        ttk.Entry(jumbo_frame, textvariable=self.jumbo_var).pack(side=tk.RIGHT)
        self.jumbo_var.trace('w', self.update_total)
        
        # Total extra charges
        total_extra_frame = ttk.Frame(extra_frame)
        total_extra_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(total_extra_frame, text="Total Extra Charges:").pack(side=tk.LEFT)
        self.total_extra_var = tk.StringVar(value="0.00")
        ttk.Entry(total_extra_frame, textvariable=self.total_extra_var, state="readonly").pack(side=tk.RIGHT)
        
        # Gross total
        total_frame = ttk.Frame(summary_frame)
        total_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(total_frame, text="Gross Total:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.total_var = tk.StringVar(value="0.00")
        ttk.Entry(total_frame, textvariable=self.total_var, state="readonly", font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
        
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
        self.ppay_var = tk.StringVar(value="7013374872")  # Set default P-Pay number
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
        
        # UPI QR code - Use static image
        upi_frame = ttk.Frame(payment_frame)
        upi_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Load static QR code image - Fixed path
        try:
            qr_image_path = "assets/images/upi_qr.png"
            if not os.path.exists(qr_image_path):
                qr_image_path = "ganesh_toughened_industry/assets/images/upi_qr.png"
            
            if os.path.exists(qr_image_path):
                self.qr_image = Image.open(qr_image_path)
                self.qr_image = self.qr_image.resize((150, 150), Image.LANCZOS)
                self.upi_qr_photo = ImageTk.PhotoImage(self.qr_image)
                self.upi_qr_label = ttk.Label(upi_frame, image=self.upi_qr_photo)
                self.upi_qr_label.pack(side=tk.LEFT, padx=5)
            else:
                self.upi_qr_label = ttk.Label(upi_frame, text="QR Code Image Not Found")
                self.upi_qr_label.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            print(f"Error loading QR code image: {e}")
            self.upi_qr_label = ttk.Label(upi_frame, text="QR Code Image Error")
            self.upi_qr_label.pack(side=tk.LEFT, padx=5)
        
        # UPI payment button
        upi_id = self.db.get_setting("upi_id") or ""
        upi_btn = ttk.Button(upi_frame, text=f"Pay via UPI ({upi_id})", command=self.open_upi_app)
        upi_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Action buttons frame with proper layout
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Create a frame for each button to ensure they're properly sized
        button_container1 = ttk.Frame(action_frame)
        button_container1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Generate PDF button
        pdf_btn = ttk.Button(button_container1, text="Generate PDF", command=self.generate_pdf)
        pdf_btn.pack(fill=tk.X, padx=2, pady=2)
        
        # Create a frame for the Save Bill button to make it more prominent
        button_container2 = ttk.Frame(action_frame)
        button_container2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Save button - Made more prominent
        save_btn = ttk.Button(button_container2, text="SAVE BILL", command=self.save_bill, style="Success.TButton")
        save_btn.pack(fill=tk.X, padx=2, pady=2)
        
        # Create a frame for the Share Bill button
        button_container3 = ttk.Frame(action_frame)
        button_container3.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Share button
        share_btn = ttk.Button(button_container3, text="Share Bill", command=self.share_bill)
        share_btn.pack(fill=tk.X, padx=2, pady=2)
        
        # Create a frame for the New Bill button
        button_container4 = ttk.Frame(action_frame)
        button_container4.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # New bill button
        new_btn = ttk.Button(button_container4, text="New Bill", command=self.new_bill)
        new_btn.pack(fill=tk.X, padx=2, pady=2)
        
        # Add some padding at the bottom to ensure all content is visible
        padding_frame = ttk.Frame(right_frame)
        padding_frame.pack(fill=tk.X, padx=5, pady=10)
        
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
        
        # Sort frame
        sort_frame = ttk.Frame(history_frame)
        sort_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(sort_frame, text="Sort By:").pack(side=tk.LEFT, padx=5)
        self.sort_var = tk.StringVar()
        sort_options = ["Date (Newest First)", "Date (Oldest First)", "Customer (A-Z)", "Customer (Z-A)", "Total (High to Low)", "Total (Low to High)"]
        sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_var, values=sort_options, state="readonly")
        sort_combo.pack(side=tk.LEFT, padx=5)
        sort_combo.current(0)  # Default to newest first
        
        sort_btn = ttk.Button(sort_frame, text="Apply Sort", command=self.apply_sort)
        sort_btn.pack(side=tk.LEFT, padx=5)
        
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
        
        # Added keyboard delete support
        self.bills_tree.bind("<Delete>", lambda e: self.delete_bill())
        
        # Action buttons
        action_frame = ttk.Frame(history_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # View bill button
        view_btn = ttk.Button(action_frame, text="View Bill", command=self.view_bill)
        view_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Edit bill button
        edit_btn = ttk.Button(action_frame, text="Edit Bill", command=self.edit_bill)
        edit_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Delete bill button
        delete_btn = ttk.Button(action_frame, text="Delete Bill", command=self.delete_bill)
        delete_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Print bill button
        print_btn = ttk.Button(action_frame, text="Print Bill", command=self.print_bill)
        print_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Load customers for both tabs
        self.load_customers()
        
        # Load bill history
        self.load_bill_history()
    
    def apply_sort(self):
        """Apply sorting to the bill history"""
        sort_option = self.sort_var.get()
        
        # Get all items from the treeview
        items = []
        for item_id in self.bills_tree.get_children():
            item = self.bills_tree.item(item_id)
            values = item['values']
            items.append({
                'id': item_id,
                'invoice_number': values[0],
                'date': values[1],
                'customer': values[2],
                'total': float(values[3]),
                'payment_mode': values[4]
            })
        
        # Sort based on selected option
        if sort_option == "Date (Newest First)":
            items.sort(key=lambda x: datetime.strptime(x['date'], "%d/%m/%Y"), reverse=True)
        elif sort_option == "Date (Oldest First)":
            items.sort(key=lambda x: datetime.strptime(x['date'], "%d/%m/%Y"))
        elif sort_option == "Customer (A-Z)":
            items.sort(key=lambda x: x['customer'])
        elif sort_option == "Customer (Z-A)":
            items.sort(key=lambda x: x['customer'], reverse=True)
        elif sort_option == "Total (High to Low)":
            items.sort(key=lambda x: x['total'], reverse=True)
        elif sort_option == "Total (Low to High)":
            items.sort(key=lambda x: x['total'])
        
        # Clear the treeview
        for item_id in self.bills_tree.get_children():
            self.bills_tree.delete(item_id)
        
        # Re-add sorted items
        for item in items:
            self.bills_tree.insert("", "end", values=(
                item['invoice_number'],
                item['date'],
                item['customer'],
                f"{item['total']:.2f}",
                item['payment_mode']
            ))
    
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
                    self.customer_email_var.set(customer["email"] or "")  # Added email
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
    
    def update_chargeable_size(self, *args):
        """Automatically update chargeable size based on actual size"""
        try:
            actual_height = self.actual_height_var.get()
            actual_width = self.actual_width_var.get()
            if actual_height and actual_width:
                height = float(actual_height)
                width = float(actual_width)
                self.chargeable_height_var.set(f"{height + 2:.2f}")
                self.chargeable_width_var.set(f"{width + 2:.2f}")
        except ValueError:
            pass
    
    def calculate_sqft(self):
        """Calculate square footage based on chargeable dimensions"""
        try:
            chargeable_height = float(self.chargeable_height_var.get())
            chargeable_width = float(self.chargeable_width_var.get())
            
            # Calculate chargeable SQ.FT
            chargeable_sqft = (chargeable_height * chargeable_width) / 144
            
            # Apply rounding logic
            rounded_sqft = self.round_sqft(chargeable_sqft)
            
            # Set SQ.FT
            self.sqft_var.set(f"{chargeable_sqft:.2f}")
            
            # Calculate amount
            if self.selected_product:
                rate = self.selected_product["rate_per_sqft"]
                quantity = int(self.quantity_var.get())
                amount = rounded_sqft * rate * quantity
                self.amount_var.set(f"{amount:.2f}")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dimensions")
    
    def round_sqft(self, sqft):
        """Round SQ.FT to one decimal place using standard rounding"""
        return round(sqft, 1)
    
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
            
            # Apply rounding
            rounded_sqft = self.round_sqft(sqft)
            amount = rounded_sqft * rate * quantity
            
            # Add item to list
            item = {
                "product_id": self.selected_product["product_id"],
                "product_name": self.selected_product["name"],
                "actual_height": actual_height,
                "actual_width": actual_width,
                "chargeable_height": chargeable_height,
                "chargeable_width": chargeable_width,
                "sqft": sqft,
                "rounded_sqft": rounded_sqft,
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
                f"{rounded_sqft:.1f}",
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
        try:
            subtotal = sum(item["amount"] for item in self.invoice_items)
            self.subtotal_var.set(f"{subtotal:.2f}")
            self.update_total()
        except Exception as e:
            print(f"Error updating subtotal: {e}")
            self.subtotal_var.set("0.00")
            self.update_total()
    
    def update_total(self, *args):
        """Update total including extra charges"""
        try:
            subtotal = float(self.subtotal_var.get())
            cutout = float(self.cutout_var.get())
            hole = float(self.hole_var.get())
            handle = float(self.handle_var.get())
            jumbo = float(self.jumbo_var.get())
            
            total_extra = cutout + hole + handle + jumbo
            self.total_extra_var.set(f"{total_extra:.2f}")
            
            total = subtotal + total_extra
            self.total_var.set(f"{total:.2f}")
            
        except ValueError:
            self.total_extra_var.set("0.00")
            self.total_var.set("0.00")
    
    def save_bill(self):
        """Save bill to database"""
        if not self.selected_customer:
            messagebox.showerror("Error", "Please select a customer")
            return
        
        if not self.invoice_items:
            messagebox.showerror("Error", "Please add at least one item")
            return
        
        try:
            subtotal = float(self.subtotal_var.get())
            total_extra = float(self.total_extra_var.get())
            total = float(self.total_var.get())
            
            date_str = self.invoice_date_var.get()
            day, month, year = date_str.split('/')
            invoice_date = date(int(year), int(month), int(day))
            
            payment_mode = self.payment_mode_var.get()
            ppay_no = self.ppay_var.get()
            
            # Generate new invoice number to avoid duplicates
            invoice_number = self.db.generate_invoice_number()
            self.invoice_number_var.set(invoice_number)
            
            # Prepare extra charges breakdown
            extra_charges_breakdown = json.dumps({
                "cutout": float(self.cutout_var.get()),
                "hole": float(self.hole_var.get()),
                "handle": float(self.handle_var.get()),
                "jumbo": float(self.jumbo_var.get())
            })
            
            invoice_id = self.db.add_invoice(
                customer_id=self.selected_customer["customer_id"],
                date=invoice_date,
                invoice_number=invoice_number,
                subtotal=subtotal,
                extra_charges=total_extra,
                round_off=0,
                total=total,
                payment_mode=payment_mode,
                p_pay_no=ppay_no,
                extra_charges_breakdown=extra_charges_breakdown  # Add this parameter
            )
            
            if not invoice_id:
                messagebox.showerror("Error", "Could not save invoice")
                return
            
            for item in self.invoice_items:
                self.db.add_invoice_item(
                    invoice_id=invoice_id,
                    product_id=item["product_id"],
                    actual_height=item["actual_height"],
                    actual_width=item["actual_width"],
                    chargeable_height=item["chargeable_height"],
                    chargeable_width=item["chargeable_width"],
                    sqft=item["sqft"],
                    rounded_sqft=item["rounded_sqft"],
                    rate=item["rate"],
                    amount=item["amount"],
                    quantity=item["quantity"]
                )
            
            if payment_mode:
                self.db.add_payment(
                    customer_id=self.selected_customer["customer_id"],
                    date=invoice_date,
                    amount=total,
                    mode=payment_mode,
                    reference=ppay_no,
                    invoice_id=invoice_id
                )
            
            self.db.add_visit(
                customer_id=self.selected_customer["customer_id"],
                name=self.selected_customer["name"],
                city=self.selected_customer["place"],
                purpose="Billing"
            )
            
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
            
            for item in self.invoice_items:
                self.db.add_inventory(
                    product_id=item["product_id"],
                    date=invoice_date,
                    type="stock_out",
                    quantity=item["quantity"]
                )
            
            # Store the last saved invoice for PDF generation
            self.last_saved_invoice = {
                "invoice_id": invoice_id,
                "invoice_number": invoice_number,
                "customer": self.selected_customer,
                "items": self.invoice_items,
                "date": invoice_date,
                "subtotal": subtotal,
                "total_extra": total_extra,
                "total": total,
                "payment_mode": payment_mode,
                "ppay_no": ppay_no,
                "extra_charges_breakdown": extra_charges_breakdown  # Add this
            }
            
            messagebox.showinfo("Success", "Bill saved successfully")
            self.load_bill_history()
            
            # Only clear the invoice items and extra charges, not the entire form
            # Commented out to keep all data after saving
            # self.invoice_items = []
            # for item_id in self.items_tree.get_children():
            #     self.items_tree.delete(item_id)
            
            # # Reset extra charges
            # self.cutout_var.set("0.00")
            # self.hole_var.set("0.00")
            # self.handle_var.set("0.00")
            # self.jumbo_var.set("0.00")
            
            # # Update totals
            # self.update_subtotal()
            
            # Delete draft after successful save
            self.delete_draft()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save bill: {e}")
    
    def generate_pdf(self):
        """Generate PDF for the invoice"""
        # Use last saved invoice if available, otherwise use current form data
        if self.last_saved_invoice:
            self._generate_pdf_from_saved_invoice()
        elif self.selected_customer and self.invoice_items:
            self._generate_pdf_from_form()
        else:
            messagebox.showerror("Error", "No bill data available. Please save a bill first.")
    
    def _generate_pdf_common(self, invoice_number, customer, items, invoice_date, subtotal, total_extra, total, payment_mode, ppay_no):
        """Common PDF generation logic to avoid duplication"""
        try:
            # Create invoices directory if it doesn't exist
            if not os.path.exists("invoices"):
                os.makedirs("invoices")
            
            # Sanitize invoice number for file name
            safe_invoice_number = invoice_number.replace('/', '_')
            file_path = os.path.join("invoices", f"Invoice_{safe_invoice_number}.pdf")
            
            # Generate the PDF
            success = self._generate_invoice_pdf_to_path(
                invoice_number, customer, items, invoice_date, 
                subtotal, total_extra, total, payment_mode, ppay_no, file_path
            )
            
            if success:
                # Store the file path for sharing
                self.last_pdf_path = file_path
                
                # Show success message
                messagebox.showinfo("Success", f"PDF generated successfully at {file_path}")
                
                # Show custom dialog with Open and Cancel buttons
                self.show_pdf_generated_dialog(file_path)
                
                return True
            else:
                messagebox.showerror("Error", "Failed to generate PDF")
                return False
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate PDF: {e}")
            return False
    
    def _generate_pdf_from_saved_invoice(self):
        """Generate PDF from the last saved invoice"""
        if not self.last_saved_invoice:
            messagebox.showerror("Error", "No saved invoice available")
            return
            
        self._generate_pdf_common(
            self.last_saved_invoice['invoice_number'],
            self.last_saved_invoice['customer'],
            self.last_saved_invoice['items'],
            self.last_saved_invoice['date'],
            self.last_saved_invoice['subtotal'],
            self.last_saved_invoice['total_extra'],
            self.last_saved_invoice['total'],
            self.last_saved_invoice['payment_mode'],
            self.last_saved_invoice['ppay_no']
        )
    
    def _generate_pdf_from_form(self):
        """Generate PDF from current form data"""
        if not self.selected_customer or not self.invoice_items:
            messagebox.showerror("Error", "Please select a customer and add items")
            return
            
        try:
            invoice_date = datetime.strptime(self.invoice_date_var.get(), "%d/%m/%Y").date()
            self._generate_pdf_common(
                self.invoice_number_var.get(),
                self.selected_customer,
                self.invoice_items,
                invoice_date,
                float(self.subtotal_var.get()),
                float(self.total_extra_var.get()),
                float(self.total_var.get()),
                self.payment_mode_var.get(),
                self.ppay_var.get()
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate PDF: {e}")
    
    def show_pdf_generated_dialog(self, file_path):
        """Show a custom dialog when PDF is generated with Open and Cancel buttons"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("PDF Generated")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Message
        message_frame = ttk.Frame(dialog, padding="20")
        message_frame.pack(fill=tk.BOTH, expand=True)
        
        message_label = ttk.Label(message_frame, text=f"PDF generated successfully at {file_path}")
        message_label.pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        open_btn = ttk.Button(button_frame, text="Open", command=lambda: self.open_pdf(file_path, dialog))
        open_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Wait for dialog to close
        self.parent.wait_window(dialog)
    
    def open_pdf(self, file_path, dialog=None):
        """Open PDF file and close dialog if provided"""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", file_path])
            else:
                subprocess.call(["xdg-open", file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF: {e}")
        finally:
            if dialog:
                dialog.destroy()
    
    def share_bill(self):
        """Share the bill using ShareUtils"""
        if not self.last_saved_invoice:
            messagebox.showerror("Error", "No saved bill to share")
            return
            
        # Generate PDF if not already generated
        if not hasattr(self, 'last_pdf_path') or not self.last_pdf_path:
            success = self.generate_pdf()
            if not success:
                messagebox.showerror("Error", "Could not generate PDF for sharing")
                return
    
        if hasattr(self, 'last_pdf_path') and self.last_pdf_path:
            # Use the improved share dialog
            ShareUtils.share_dialog(self.last_pdf_path, self.parent)
        else:
            messagebox.showerror("Error", "Could not generate PDF for sharing")
        
    def print_bill(self):
        """Print the selected bill"""
        selected = self.bills_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a bill to print")
            return
    
        # Get invoice number
        item = self.bills_tree.item(selected[0])
        invoice_number = item['values'][0]
    
        # Get invoice details
        invoice = self.db.get_invoice_by_number(invoice_number)
        if not invoice:
            messagebox.showerror("Error", "Could not find invoice details")
            return
    
        # Generate PDF if needed
        safe_invoice_number = invoice_number.replace('/', '_')
        file_path = os.path.join("invoices", f"Invoice_{safe_invoice_number}.pdf")
    
        # Always regenerate PDF to ensure it's up to date
        # Fixed date handling - ensure date is a date object
        invoice_date = invoice['date']
        if isinstance(invoice_date, str):
            try:
                invoice_date = datetime.strptime(invoice_date, "%Y-%m-%d").date()
            except ValueError:
                invoice_date = date.today()
                
        success = self._generate_invoice_pdf_to_path(
            invoice_number,
            {
                "name": invoice['customer_name'],
                "place": invoice['customer_place'],
                "phone": invoice['customer_phone'],
                "gst": invoice['customer_gst'],
                "email": invoice.get('customer_email', '')  # Added email
            },
            self.db.get_invoice_items(invoice['invoice_id']),
            invoice_date,
            invoice['subtotal'],
            invoice['extra_charges'],
            invoice['total'],
            invoice['payment_mode'],
            invoice['p_pay_no'],
            file_path
        )
        
        if not success:
            messagebox.showerror("Error", "Could not generate PDF for printing")
            return
    
        # Show print dialog
        try:
            if platform.system() == "Windows":
                # Try to use win32api if available, but handle ImportError gracefully
                try:
                    import win32api
                    import win32print
                    import win32con
                    
                    # Get the default printer
                    printer_name = win32print.GetDefaultPrinter()
                    
                    # Show print dialog
                    try:
                        # This will show the print dialog
                        win32api.ShellExecute(
                            0, 
                            "printto", 
                            file_path, 
                            f'"{printer_name}"', 
                            ".", 
                            0
                        )
                    except Exception as e:
                        # Fallback to standard print method
                        os.startfile(file_path, "print")
                except ImportError:
                    # win32api is not available, use standard print method
                    os.startfile(file_path, "print")
                    
            elif platform.system() == "Darwin":  # macOS
                # Use lpr command on macOS with print dialog
                subprocess.run(["lpr", "-o", "print-dialog", file_path])
            else:  # Linux and other Unix-like systems
                # Use xdg-open on Linux to show print dialog
                subprocess.run(["xdg-open", file_path])
                
            messagebox.showinfo("Success", "Print job sent successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Could not print bill: {e}")
         
    def view_bill(self, event=None):
        """View the selected bill"""
        selected = self.bills_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a bill to view")
            return
        
        # Get the invoice number
        item = self.bills_tree.item(selected[0])
        invoice_number = item['values'][0]
        
        # Get the invoice details
        invoice = self.db.get_invoice_by_number(invoice_number)
        if not invoice:
            messagebox.showerror("Error", "Invoice not found")
            return
        
        # Get the invoice items
        items = self.db.get_invoice_items(invoice['invoice_id'])
        
        # Generate the PDF
        safe_invoice_number = invoice_number.replace('/', '_')
        file_path = os.path.join("invoices", f"Invoice_{safe_invoice_number}.pdf")
        
        # Generate the PDF if it doesn't exist
        if not os.path.exists(file_path):
            # Fixed date handling - ensure date is a date object
            invoice_date = invoice['date']
            if isinstance(invoice_date, str):
                try:
                    invoice_date = datetime.strptime(invoice_date, "%Y-%m-%d").date()
                except ValueError:
                    invoice_date = date.today()
                    
            success = self._generate_invoice_pdf_to_path(
                invoice_number,
                {
                    "name": invoice['customer_name'],
                    "place": invoice['customer_place'],
                    "phone": invoice['customer_phone'],
                    "gst": invoice['customer_gst'],
                    "email": invoice.get('customer_email', '')  # Added email
                },
                items,
                invoice_date,
                invoice['subtotal'],
                invoice['extra_charges'],
                invoice['total'],
                invoice['payment_mode'],
                invoice['p_pay_no'],
                file_path
            )
            
            if not success:
                messagebox.showerror("Error", "Could not generate PDF for viewing")
                return
        
        # Open the PDF
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", file_path])
            else:
                subprocess.call(["xdg-open", file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open bill: {e}")
    
    def edit_bill(self):
        """Edit the selected bill"""
        selected = self.bills_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a bill to edit")
            return
        
        # Get the invoice number
        item = self.bills_tree.item(selected[0])
        invoice_number = item['values'][0]
        
        # Get the invoice details
        invoice = self.db.get_invoice_by_number(invoice_number)
        if not invoice:
            messagebox.showerror("Error", "Invoice not found")
            return
        
        # Get the invoice items
        items = self.db.get_invoice_items(invoice['invoice_id'])
        
        # Switch to the billing tab
        self.notebook.select(0)
        
        # Load the invoice data into the form
        self.load_invoice_data(invoice, items)
    
    def load_invoice_data(self, invoice, items):
        """Load invoice data into the form"""
        # Set customer
        customers = self.db.get_customers()
        for customer in customers:
            if customer["customer_id"] == invoice.get("customer_id"):
                self.customer_var.set(customer["name"])
                self.on_customer_selected(None)
                break
    
        # Set invoice number and date
        self.invoice_number_var.set(invoice["invoice_number"])
        
        # Fixed: Check if date is a string or date object
        if isinstance(invoice["date"], str):
            # Parse the date string
            try:
                date_obj = datetime.strptime(invoice["date"], "%Y-%m-%d").date()
                self.invoice_date_var.set(date_obj.strftime("%d/%m/%Y"))
            except ValueError:
                # If parsing fails, use today's date
                self.invoice_date_var.set(date.today().strftime("%d/%m/%Y"))
        else:
            # It's already a date object
            self.invoice_date_var.set(invoice["date"].strftime("%d/%m/%Y"))
    
        # Clear existing items
        self.invoice_items = []
        for item_id in self.items_tree.get_children():
            self.items_tree.delete(item_id)
    
        # Add items
        for item in items:
            # Add to list
            invoice_item = {
                "product_id": item["product_id"],
                "product_name": item["product_name"],
                "actual_height": item["actual_height"],
                "actual_width": item["actual_width"],
                "chargeable_height": item["chargeable_height"],
                "chargeable_width": item["chargeable_width"],
                "sqft": item["sqft"],
                "rounded_sqft": item["rounded_sqft"],
                "rate": item["rate"],
                "quantity": item["quantity"],
                "amount": item["amount"]
            }
            self.invoice_items.append(invoice_item)
        
            # Add to treeview
            actual_size = f"{item['actual_height']}\" x {item['actual_width']}\""
            chargeable_size = f"{item['chargeable_height']}\" x {item['chargeable_width']}\""
            self.items_tree.insert("", "end", values=(
                item["product_name"],
                actual_size,
                chargeable_size,
                f"{item['sqft']:.2f}",
                f"{item['rounded_sqft']:.1f}",
                f"{item['rate']:.2f}",
                item["quantity"],
                f"{item['amount']:.2f}"
            ))
    
        # Update subtotal
        self.update_subtotal()
    
        # Load extra charges if available
        if 'extra_charges_breakdown' in invoice and invoice['extra_charges_breakdown']:
            try:
                extra_charges = json.loads(invoice['extra_charges_breakdown'])
                self.cutout_var.set(str(extra_charges.get('cutout', 0)))
                self.hole_var.set(str(extra_charges.get('hole', 0)))
                self.handle_var.set(str(extra_charges.get('handle', 0)))
                self.jumbo_var.set(str(extra_charges.get('jumbo', 0)))
            except:
                # If parsing fails, set to 0
                self.cutout_var.set("0.00")
                self.hole_var.set("0.00")
                self.handle_var.set("0.00")
                self.jumbo_var.set("0.00")
        else:
            # Default to 0 if no breakdown available
            self.cutout_var.set("0.00")
            self.hole_var.set("0.00")
            self.handle_var.set("0.00")
            self.jumbo_var.set("0.00")
    
        # Update total
        self.update_total()
    
        # Set payment details
        self.payment_mode_var.set(invoice["payment_mode"] or "")
        self.ppay_var.set(invoice["p_pay_no"] or "7013374872")
    
    def delete_bill(self):
        """Delete the selected bill"""
        selected = self.bills_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a bill to delete")
            return
        
        # Get the invoice number
        item = self.bills_tree.item(selected[0])
        invoice_number = item['values'][0]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete invoice {invoice_number}?"):
            return
        
        # Get the invoice details
        invoice = self.db.get_invoice_by_number(invoice_number)
        if not invoice:
            messagebox.showerror("Error", "Invoice not found")
            return
        
        # Get the invoice items
        items = self.db.get_invoice_items(invoice['invoice_id'])
        
        # Prepare invoice data for recycle bin
        invoice_data = {
            "invoice_id": invoice["invoice_id"],
            "customer_id": invoice["customer_id"],
            "invoice_number": invoice["invoice_number"],
            "date": invoice["date"],
            "subtotal": invoice["subtotal"],
            "extra_charges": invoice["extra_charges"],
            "round_off": invoice["round_off"],
            "total": invoice["total"],
            "payment_mode": invoice["payment_mode"],
            "p_pay_no": invoice["p_pay_no"],
            "extra_charges_breakdown": invoice["extra_charges_breakdown"],
            "customer_name": invoice["customer_name"],
            "customer_place": invoice["customer_place"],
            "customer_phone": invoice["customer_phone"],
            "customer_gst": invoice["customer_gst"],
            "customer_email": invoice.get("customer_email", ""),
            "items": items
        }
        
        # Add to recycle bin before deletion
        self.db.add_to_recycle_bin("invoices", invoice["invoice_id"], invoice_data)
        
        # Delete the invoice from the database
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Delete invoice items
            cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice["invoice_id"],))
            
            # Delete payments
            cursor.execute("DELETE FROM payments WHERE invoice_id = ?", (invoice["invoice_id"],))
            
            # Delete works
            cursor.execute("DELETE FROM works WHERE invoice_id = ?", (invoice["invoice_id"],))
            
            # Delete inventory records
            cursor.execute("DELETE FROM inventory WHERE product_id IN (SELECT product_id FROM invoice_items WHERE invoice_id = ?)", 
                         (invoice["invoice_id"],))
            
            # Delete the invoice
            cursor.execute("DELETE FROM invoices WHERE invoice_id = ?", (invoice["invoice_id"],))
            
            conn.commit()
            conn.close()
            
            # Refresh the bill history
            self.load_bill_history()
            
            messagebox.showinfo("Success", "Invoice moved to recycle bin")
        except Exception as e:
            conn.rollback()
            conn.close()
            messagebox.showerror("Error", f"Could not delete invoice: {e}")
    
    def delete_customer(self):
        """Delete the selected customer"""
        if not self.selected_customer:
            messagebox.showerror("Error", "Please select a customer first")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {self.selected_customer['name']}?"):
            return
        
        # Check if customer has related records and handle foreign key constraints
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check for invoices
            cursor.execute("SELECT COUNT(*) FROM invoices WHERE customer_id = ?", (self.selected_customer["customer_id"],))
            invoice_count = cursor.fetchone()[0]
            
            # Check for payments
            cursor.execute("SELECT COUNT(*) FROM payments WHERE customer_id = ?", (self.selected_customer["customer_id"],))
            payment_count = cursor.fetchone()[0]
            
            # Check for visits
            cursor.execute("SELECT COUNT(*) FROM customer_visits WHERE customer_id = ?", (self.selected_customer["customer_id"],))
            visit_count = cursor.fetchone()[0]
            
            if invoice_count > 0 or payment_count > 0 or visit_count > 0:
                # Customer has related records, ask for confirmation with details
                details = []
                if invoice_count > 0:
                    details.append(f"{invoice_count} invoice(s)")
                if payment_count > 0:
                    details.append(f"{payment_count} payment(s)")
                if visit_count > 0:
                    details.append(f"{visit_count} visit(s)")
                
                if not messagebox.askyesno("Confirm Delete", 
                                         f"Customer has related records: {', '.join(details)}.\n\n"
                                         f"Deleting this customer will also delete all related records.\n\n"
                                         f"Are you sure you want to continue?"):
                    conn.close()
                    return
            
            # Add customer to recycle bin before deletion
            self.db.add_to_recycle_bin("customers", self.selected_customer["customer_id"], self.selected_customer)
            
            # Delete all related records
            # Delete invoice items and inventory records for invoices
            cursor.execute("DELETE FROM invoice_items WHERE invoice_id IN (SELECT invoice_id FROM invoices WHERE customer_id = ?)", 
                         (self.selected_customer["customer_id"],))
            cursor.execute("DELETE FROM inventory WHERE product_id IN (SELECT product_id FROM invoice_items WHERE invoice_id IN (SELECT invoice_id FROM invoices WHERE customer_id = ?))", 
                         (self.selected_customer["customer_id"],))
            
            # Delete invoices
            cursor.execute("DELETE FROM invoices WHERE customer_id = ?", (self.selected_customer["customer_id"],))
            
            # Delete payments
            cursor.execute("DELETE FROM payments WHERE customer_id = ?", (self.selected_customer["customer_id"],))
            
            # Delete visits
            cursor.execute("DELETE FROM customer_visits WHERE customer_id = ?", (self.selected_customer["customer_id"],))
            
            # Delete the customer
            cursor.execute("DELETE FROM customers WHERE customer_id = ?", (self.selected_customer["customer_id"],))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Customer moved to recycle bin")
            # Refresh customer list
            self.load_customers()
            # Clear customer details
            self.customer_var.set("")
            self.selected_customer = None
            self.customer_name_var.set("")
            self.customer_place_var.set("")
            self.customer_phone_var.set("")
            self.customer_gst_var.set("")
            self.customer_email_var.set("")
        except Exception as e:
            conn.rollback()
            conn.close()
            messagebox.showerror("Error", f"Could not delete customer: {e}")
    
    def search_bills(self):
        """Search bills based on criteria"""
        customer = self.history_customer_var.get()
        from_date_str = self.history_from_var.get()
        to_date_str = self.history_to_var.get()
        
        from_date = None
        to_date = None
        
        if from_date_str:
            try:
                day, month, year = from_date_str.split('/')
                from_date = date(int(year), int(month), int(day))
            except ValueError:
                messagebox.showerror("Error", "Invalid from date format. Use DD/MM/YYYY")
                return
        
        if to_date_str:
            try:
                day, month, year = to_date_str.split('/')
                to_date = date(int(year), int(month), int(day))
            except ValueError:
                messagebox.showerror("Error", "Invalid to date format. Use DD/MM/YYYY")
                return
        
        # Search invoices
        invoices = self.db.search_invoices(customer, from_date, to_date)
        
        # Clear the treeview
        for item_id in self.bills_tree.get_children():
            self.bills_tree.delete(item_id)
        
        # Add search results
        for invoice in invoices:
            # Fixed: Check if date is a string or date object
            if isinstance(invoice["date"], str):
                # Parse the date string
                try:
                    date_obj = datetime.strptime(invoice["date"], "%Y-%m-%d").date()
                    display_date = date_obj.strftime("%d/%m/%Y")
                except ValueError:
                    # If parsing fails, use the original string
                    display_date = invoice["date"]
            else:
                # It's already a date object
                display_date = invoice["date"].strftime("%d/%m/%Y")
                
            self.bills_tree.insert("", "end", values=(
                invoice["invoice_number"],
                display_date,
                invoice["customer_name"],
                f"{invoice['total']:.2f}",
                invoice["payment_mode"] or ""
            ))
    
    def load_bill_history(self):
        """Load bill history into the treeview"""
        # Clear the treeview
        for item_id in self.bills_tree.get_children():
            self.bills_tree.delete(item_id)
        
        # Get invoices
        invoices = self.db.get_invoices()
        
        # Add invoices to the treeview
        for invoice in invoices:
            # Fixed: Check if date is a string or date object
            if isinstance(invoice["date"], str):
                # Parse the date string
                try:
                    date_obj = datetime.strptime(invoice["date"], "%Y-%m-%d").date()
                    display_date = date_obj.strftime("%d/%m/%Y")
                except ValueError:
                    # If parsing fails, use the original string
                    display_date = invoice["date"]
            else:
                # It's already a date object
                display_date = invoice["date"].strftime("%d/%m/%Y")
                
            self.bills_tree.insert("", "end", values=(
                invoice["invoice_number"],
                display_date,
                invoice["customer_name"],
                f"{invoice['total']:.2f}",
                invoice["payment_mode"] or ""
            ))
    
    def add_new_customer(self):
        """Add a new customer"""
        # Create a new window for adding customer
        customer_window = tk.Toplevel(self.parent)
        customer_window.title("Add New Customer")
        customer_window.geometry("400x300")
        customer_window.transient(self.parent)
        customer_window.grab_set()
        
        # Customer details form
        ttk.Label(customer_window, text="Name:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        name_var = tk.StringVar()
        ttk.Entry(customer_window, textvariable=name_var).grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(customer_window, text="Place:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        place_var = tk.StringVar()
        ttk.Entry(customer_window, textvariable=place_var).grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(customer_window, text="Phone:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        phone_var = tk.StringVar()
        ttk.Entry(customer_window, textvariable=phone_var).grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(customer_window, text="GST:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        gst_var = tk.StringVar()
        ttk.Entry(customer_window, textvariable=gst_var).grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(customer_window, text="Address:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        address_var = tk.StringVar()
        ttk.Entry(customer_window, textvariable=address_var).grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(customer_window, text="Email:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        email_var = tk.StringVar()
        ttk.Entry(customer_window, textvariable=email_var).grid(row=5, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Buttons
        button_frame = ttk.Frame(customer_window)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
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
                gst=gst_var.get().strip(),
                address=address_var.get().strip(),
                email=email_var.get().strip()
            )
            
            if customer_id:
                messagebox.showinfo("Success", "Customer added successfully")
                customer_window.destroy()
                # Refresh customer list
                self.load_customers()
            else:
                messagebox.showerror("Error", "Could not add customer")
        
        ttk.Button(button_frame, text="Save", command=save_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=customer_window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        customer_window.columnconfigure(1, weight=1)
    
    def edit_customer(self):
        """Edit the selected customer"""
        if not self.selected_customer:
            messagebox.showerror("Error", "Please select a customer first")
            return
        
        # Create a new window for editing customer
        customer_window = tk.Toplevel(self.parent)
        customer_window.title("Edit Customer")
        customer_window.geometry("400x300")
        customer_window.transient(self.parent)
        customer_window.grab_set()
        
        # Customer details form
        ttk.Label(customer_window, text="Name:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        name_var = tk.StringVar(value=self.selected_customer["name"])
        ttk.Entry(customer_window, textvariable=name_var).grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(customer_window, text="Place:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        place_var = tk.StringVar(value=self.selected_customer["place"] or "")
        ttk.Entry(customer_window, textvariable=place_var).grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(customer_window, text="Phone:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        phone_var = tk.StringVar(value=self.selected_customer["phone"] or "")
        ttk.Entry(customer_window, textvariable=phone_var).grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(customer_window, text="GST:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        gst_var = tk.StringVar(value=self.selected_customer["gst"] or "")
        ttk.Entry(customer_window, textvariable=gst_var).grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(customer_window, text="Address:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        address_var = tk.StringVar(value=self.selected_customer["address"] or "")
        ttk.Entry(customer_window, textvariable=address_var).grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(customer_window, text="Email:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        email_var = tk.StringVar(value=self.selected_customer["email"] or "")
        ttk.Entry(customer_window, textvariable=email_var).grid(row=5, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Buttons
        button_frame = ttk.Frame(customer_window)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        def update_customer():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Customer name is required")
                return
            
            # Update customer in database
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                UPDATE customers SET name = ?, place = ?, phone = ?, gst = ?, address = ?, email = ?
                WHERE customer_id = ?
                """, (
                    name,
                    place_var.get().strip(),
                    phone_var.get().strip(),
                    gst_var.get().strip(),
                    address_var.get().strip(),
                    email_var.get().strip(),
                    self.selected_customer["customer_id"]
                ))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Customer updated successfully")
                customer_window.destroy()
                # Refresh customer list and selected customer
                self.load_customers()
                self.customer_var.set(name)
                self.on_customer_selected(None)
            except Exception as e:
                conn.rollback()
                conn.close()
                messagebox.showerror("Error", f"Could not update customer: {e}")
        
        ttk.Button(button_frame, text="Save", command=update_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=customer_window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        customer_window.columnconfigure(1, weight=1)
    
    def new_bill(self):
        """Start a new bill"""
        # Clear form
        self.customer_var.set("")
        self.selected_customer = None
        self.customer_name_var.set("")
        self.customer_place_var.set("")
        self.customer_phone_var.set("")
        self.customer_gst_var.set("")
        self.customer_email_var.set("")
        
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
        
        self.invoice_items = []
        for item_id in self.items_tree.get_children():
            self.items_tree.delete(item_id)
        
        self.subtotal_var.set("0.00")
        self.cutout_var.set("0.00")
        self.hole_var.set("0.00")
        self.handle_var.set("0.00")
        self.jumbo_var.set("0.00")
        self.total_extra_var.set("0.00")
        self.total_var.set("0.00")
        
        self.payment_mode_var.set("")
        self.ppay_var.set("7013374872")
        
        # Generate new invoice number
        self.invoice_number_var.set(self.db.generate_invoice_number())
        
        # Clear last saved invoice
        self.last_saved_invoice = None
        self.last_pdf_path = None
        
        # Delete draft
        self.delete_draft()
    
    def start_auto_save(self):
        """Start auto-save timer"""
        self.auto_save_timer = threading.Timer(self.auto_save_interval, self.auto_save_draft)
        self.auto_save_timer.daemon = True
        self.auto_save_timer.start()
    
    def auto_save_draft(self):
        """Auto-save the current bill as draft"""
        try:
            self.save_draft()
        except Exception as e:
            print(f"Error auto-saving draft: {e}")
        finally:
            # Restart the timer
            self.start_auto_save()
    
    def save_draft(self):
        """Save current bill as draft"""
        try:
            draft_data = {
                "customer": self.customer_var.get(),
                "items": self.invoice_items,
                "extra_charges": {
                    "cutout": self.cutout_var.get(),
                    "hole": self.hole_var.get(),
                    "handle": self.handle_var.get(),
                    "jumbo": self.jumbo_var.get()
                },
                "payment": {
                    "mode": self.payment_mode_var.get(),
                    "ppay_no": self.ppay_var.get()
                }
            }
            
            with open(self.draft_file, 'w') as f:
                json.dump(draft_data, f)
        except Exception as e:
            print(f"Error saving draft: {e}")
    
    def load_draft(self):
        """Load draft bill"""
        if os.path.exists(self.draft_file):
            try:
                with open(self.draft_file, 'r') as f:
                    draft_data = json.load(f)
                
                # Load customer
                if 'customer' in draft_data and draft_data['customer']:
                    customer_name = draft_data['customer']
                    self.customer_var.set(customer_name)
                    self.on_customer_selected(None)
                
                # Load invoice items
                if 'items' in draft_data:
                    self.invoice_items = draft_data['items']
                    # Refresh the treeview
                    for item in self.items_tree.get_children():
                        self.items_tree.delete(item)
                    for item in self.invoice_items:
                        actual_size = f"{item['actual_height']}\" x {item['actual_width']}\""
                        chargeable_size = f"{item['chargeable_height']}\" x {item['chargeable_width']}\""
                        self.items_tree.insert("", "end", values=(
                            item["product_name"],
                            actual_size,
                            chargeable_size,
                            f"{item['sqft']:.2f}",
                            f"{item['rounded_sqft']:.1f}",
                            f"{item['rate']:.2f}",
                            item["quantity"],
                            f"{item['amount']:.2f}"
                        ))
                    self.update_subtotal()
                
                # Load extra charges
                if 'extra_charges' in draft_data:
                    extra = draft_data['extra_charges']
                    self.cutout_var.set(str(extra.get('cutout', 0)))
                    self.hole_var.set(str(extra.get('hole', 0)))
                    self.handle_var.set(str(extra.get('handle', 0)))
                    self.jumbo_var.set(str(extra.get('jumbo', 0)))
                
                # Load payment details
                if 'payment' in draft_data:
                    payment = draft_data['payment']
                    self.payment_mode_var.set(payment.get('mode', ''))
                    self.ppay_var.set(payment.get('ppay_no', '7013374872'))
            except Exception as e:
                print(f"Error loading draft: {e}")
                # Delete corrupted draft file
                try:
                    os.remove(self.draft_file)
                except:
                    pass
    
    def delete_draft(self):
        """Delete draft file"""
        try:
            if os.path.exists(self.draft_file):
                os.remove(self.draft_file)
        except Exception as e:
            print(f"Error deleting draft: {e}")
    
    def _generate_invoice_pdf_to_path(self, invoice_number, customer, items, invoice_date, subtotal, total_extra, total, payment_mode, ppay_no, file_path):
        """Generate PDF for an invoice to a specific path with modern styling"""
        try:
            # Create invoices directory if it doesn't exist
            if not os.path.exists("invoices"):
                os.makedirs("invoices")
            
            doc = SimpleDocTemplate(file_path, pagesize=A4, 
                                    rightMargin=30, leftMargin=30, 
                                    topMargin=30, bottomMargin=30)
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Define modern color scheme using hex values
            primary_color = "#000080"  # dark blue
            secondary_color = "#0000FF"  # blue
            accent_color = "#FF0000"  # red
            light_gray = "#D3D3D3"  # light gray
            
            # Add custom styles for modern look
            styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=20,
                textColor=HexColor(primary_color),
                alignment=TA_CENTER,
                borderWidth=1,
                borderColor=HexColor(primary_color),
                borderPadding=5
            ))
            
            styles.add(ParagraphStyle(
                name='CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=HexColor(primary_color),
                borderWidth=1,
                borderColor=HexColor(primary_color),
                borderPadding=3
            ))
            
            styles.add(ParagraphStyle(
                name='CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=HexColor("#000000"),  # black
                spaceAfter=6
            ))
            
            # Create a table for logo and company details side by side
            company_data = []
            
            # Add logo if available
            logo_path = "assets/images/logo.png"
            if not os.path.exists(logo_path):
                logo_path = "ganesh_toughened_industry/assets/images/logo.png"
                
            logo_cell = None
            if os.path.exists(logo_path):
                logo = RLImage(logo_path, width=2*inch, height=1.5*inch)
                logo_cell = logo
            
            # Company details
            company_name = self.db.get_setting("company_name") or "GANESH TOUGHENED INDUSTRY"
            company_address = self.db.get_setting("company_address") or "Plot no:B13, Industrial Estate, Madanapalli"
            company_phone = self.db.get_setting("company_phone") or "9398530499, 7013374872"
            company_gst = self.db.get_setting("company_gst") or "37EXFPK2395CIZE"
            
            company_details = [
                [Paragraph(f"<b>{company_name}</b>", styles["CustomTitle"])],
                [Paragraph(company_address, styles["CustomNormal"])],
                [Paragraph(f"Phone: {company_phone}", styles["CustomNormal"])],
                [Paragraph(f"GST: {company_gst}", styles["CustomNormal"])]
            ]
            
            company_table = Table(company_details, colWidths=[10*cm])
            company_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            # Create table with logo and company details
            if logo_cell:
                company_layout_data = [[logo_cell, company_table]]
                company_layout_table = Table(company_layout_data, colWidths=[2*inch, 10*cm])
            else:
                company_layout_table = company_table
            
            company_layout_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(company_layout_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Invoice title with modern styling
            invoice_title = Paragraph("<b>INVOICE</b>", styles["CustomHeading"])
            elements.append(invoice_title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Invoice details in a modern table
            invoice_data = [
                ["Invoice #:", invoice_number],
                ["Date:", invoice_date.strftime("%d/%m/%Y")],
                ["Customer:", customer["name"]],
                ["Place:", customer["place"] or ""],
                ["Phone:", customer["phone"] or ""],
                ["GST:", customer["gst"] or ""]
            ]
            
            invoice_table = Table(invoice_data, colWidths=[4*cm, 12*cm])
            invoice_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 0), (-1, -1), HexColor(light_gray)),
                ('BOX', (0, 0), (-1, -1), 1, HexColor(primary_color)),
                ('ROUNDEDCORNERS', [10, 10, 10, 10]),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ]))
            
            elements.append(invoice_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Items table with improved formatting
            items_data = [[
                "Product", "Actual Size", "Chargeable Size", "SQ.FT", "Rounded SQ.FT", "Rate", "Qty", "Amount"
            ]]
            
            for item in items:
                actual_size = f"{item['actual_height']}\" x {item['actual_width']}\""
                chargeable_size = f"{item['chargeable_height']}\" x {item['chargeable_width']}\""
                items_data.append([
                    item["product_name"],
                    actual_size,
                    chargeable_size,
                    f"{item['sqft']:.2f}",
                    f"{item['rounded_sqft']:.1f}",
                    f"{item['rate']:.2f}",
                    str(item["quantity"]),
                    f"{item['amount']:.2f}"
                ])
            
            # Adjust column widths for better text fitting
            items_table = Table(items_data, colWidths=[3.5*cm, 2.5*cm, 2.5*cm, 1.5*cm, 2*cm, 1.5*cm, 1*cm, 2*cm])
            items_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), HexColor(primary_color)),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor("#FFFFFF")),  # white
                ('GRID', (0, 0), (-1, -1), 1, HexColor(primary_color)),
                ('FONTSIZE', (0, 0), (-1, 0), 9),  # Reduced font size
                ('FONTSIZE', (0, 1), (-1, -1), 8),  # Reduced font size
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('ROUNDEDCORNERS', [10, 10, 10, 10]),
            ]))
            
            elements.append(items_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Extra charges section - Fixed to always show breakdown
            extra_charges_data = [["Description", "Amount"]]
            
            # Get extra charges breakdown from the last saved invoice or use current values
            extra_charges = {}
            if hasattr(self, 'last_saved_invoice') and self.last_saved_invoice and 'extra_charges_breakdown' in self.last_saved_invoice:
                try:
                    extra_charges = json.loads(self.last_saved_invoice['extra_charges_breakdown'])
                except:
                    pass
            
            # Always add all charge types, even if they're zero
            extra_charges_data.append(["Cut Out Charges", f"{float(extra_charges.get('cutout', 0)):.2f}"])
            extra_charges_data.append(["Hole Charges", f"{float(extra_charges.get('hole', 0)):.2f}"])
            extra_charges_data.append(["Door Handle Hole Charges", f"{float(extra_charges.get('handle', 0)):.2f}"])
            extra_charges_data.append(["Jumbo Size Charges", f"{float(extra_charges.get('jumbo', 0)):.2f}"])
            
            extra_charges_table = Table(extra_charges_data, colWidths=[8*cm, 4*cm])
            extra_charges_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), HexColor(primary_color)),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor("#FFFFFF")),  # white
                ('GRID', (0, 0), (-1, -1), 1, HexColor(primary_color)),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ]))
            
            elements.append(extra_charges_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Summary table with modern styling
            summary_data = [
                ["Subtotal:", f"{subtotal:.2f}"],
                ["Extra Charges:", f"{total_extra:.2f}"],
                ["Total:", f"{total:.2f}"]
            ]
            
            summary_table = Table(summary_data, colWidths=[12*cm, 4*cm])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, -1), HexColor(light_gray)),
                ('GRID', (0, 0), (-1, -1), 1, HexColor(primary_color)),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('ROUNDEDCORNERS', [10, 10, 10, 10]),
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Payment details with bank info and QR code side by side
            # Create a 2-column layout for payment details
            payment_layout = Table([
                [
                    # Left column - Payment details and bank info
                    [
                        Paragraph("<b>Payment Details</b>", styles["CustomHeading"]),
                        Spacer(1, 0.2*inch),
                        Paragraph(f"Payment Mode: {payment_mode or ''}", styles["CustomNormal"]),
                        Paragraph(f"P-PAY No.: {ppay_no or ''}", styles["CustomNormal"]),
                        Spacer(1, 0.3*inch),
                        Paragraph("<b>Bank Details</b>", styles["CustomHeading"]),
                        Spacer(1, 0.1*inch),
                        Paragraph(f"Bank: {self.db.get_setting('bank_name') or ''}", styles["CustomNormal"]),
                        Paragraph(f"Account: {self.db.get_setting('bank_account') or ''}", styles["CustomNormal"]),
                        Paragraph(f"IFSC: {self.db.get_setting('bank_ifsc') or ''}", styles["CustomNormal"]),
                        Paragraph(f"Branch: {self.db.get_setting('bank_branch') or ''}", styles["CustomNormal"])
                    ],
                    # Right column - QR code
                    [
                        Paragraph("<b>UPI Payment</b>", styles["CustomHeading"]),
                        Spacer(1, 0.1*inch)
                    ]
                ]
            ], colWidths=[10*cm, 5*cm])
            
            payment_layout.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            elements.append(payment_layout)
            elements.append(Spacer(1, 0.3*inch))
            
            # Add UPI QR code
            upi_id = self.db.get_setting("upi_id") or ""
            upi_name = self.db.get_setting("upi_name") or ""
            upi_data = f"upi://pay?pa={upi_id}&pn={upi_name}&am={total}&cu=INR"
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(upi_data)
            qr.make(fit=True)
            
            # Use RGB tuples for qrcode
            img = qr.make_image(fill_color=(0, 0, 128), back_color=(255, 255, 255))  # darkblue and white as RGB
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            qr_image = RLImage(img_byte_arr, width=1.5*inch, height=1.5*inch)
            elements.append(qr_image)
            
            # Add footer with modern styling
            footer_text = f"Generated on {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | {company_name}"
            footer = Paragraph(footer_text, styles["CustomNormal"])
            elements.append(Spacer(1, 0.5*inch))
            elements.append(footer)
            
            # Build the PDF
            doc.build(elements)
            
            return True
        except Exception as e:
            print(f"Error generating PDF: {e}")
            messagebox.showerror("Error", f"Failed to generate PDF: {e}")
            return False
    
    def open_upi_app(self):
        """Open UPI payment app or URL"""
        try:
            upi_id = self.db.get_setting("upi_id") or ""
            if not upi_id:
                messagebox.showerror("Error", "UPI ID not configured")
                return
            
            # Get total amount
            total = self.total_var.get()
            if not total:
                messagebox.showerror("Error", "No amount specified")
                return
            
            # Get UPI name
            upi_name = self.db.get_setting("upi_name") or "GANESH TOUGHENED INDUSTRY"
            
            # Create UPI payment URL
            upi_url = f"upi://pay?pa={upi_id}&pn={upi_name}&am={total}&cu=INR"
            
            # Open UPI URL based on platform
            if platform.system() == "Windows":
                os.startfile(upi_url)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", upi_url])
            else:  # Linux and other Unix-like systems
                subprocess.call(["xdg-open", upi_url])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open UPI app: {e}")
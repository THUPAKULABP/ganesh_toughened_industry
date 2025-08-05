import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from theme import ClaymorphismTheme

class BillingModule:
    def __init__(self, parent, db, app):
        self.parent = parent
        self.db = db
        self.app = app
        self.create_ui()
    
    def create_ui(self):
        # Main container
        main_container = tk.Frame(self.parent, bg=ClaymorphismTheme.BG_PRIMARY)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame, header_card = ClaymorphismTheme.create_card(
            main_container, 
            text="Billing & Invoicing", 
            height=80
        )
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Content area
        content_frame = tk.Frame(main_container, bg=ClaymorphismTheme.BG_PRIMARY)
        content_frame.pack(fill="both", expand=True)
        
        # Left panel - Invoice list
        left_panel = tk.Frame(content_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Search and filter
        search_frame, search_card = ClaymorphismTheme.create_card(left_panel, height=100)
        search_frame.pack(fill="x", pady=(0, 10))
        
        # Customer search
        customer_label = tk.Label(search_card, text="Customer:", bg=ClaymorphismTheme.BG_CARD, 
                                font=ClaymorphismTheme.FONT_NORMAL)
        customer_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.customer_entry_frame, self.customer_entry = ClaymorphismTheme.create_entry(search_card, width=20)
        self.customer_entry_frame.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # Date range
        from_label = tk.Label(search_card, text="From:", bg=ClaymorphismTheme.BG_CARD, 
                            font=ClaymorphismTheme.FONT_NORMAL)
        from_label.grid(row=0, column=2, sticky="w", padx=10, pady=5)
        
        self.from_date_frame, self.from_date = ClaymorphismTheme.create_entry(search_card, width=15)
        self.from_date_frame.grid(row=0, column=3, sticky="w", padx=10, pady=5)
        
        to_label = tk.Label(search_card, text="To:", bg=ClaymorphismTheme.BG_CARD, 
                          font=ClaymorphismTheme.FONT_NORMAL)
        to_label.grid(row=0, column=4, sticky="w", padx=10, pady=5)
        
        self.to_date_frame, self.to_date = ClaymorphismTheme.create_entry(search_card, width=15)
        self.to_date_frame.grid(row=0, column=5, sticky="w", padx=10, pady=5)
        
        # Search button
        search_btn_frame, search_btn = ClaymorphismTheme.create_button(
            search_card, 
            text="Search",
            command=self.search_invoices
        )
        search_btn_frame.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Clear button
        clear_btn_frame, clear_btn = ClaymorphismTheme.create_button(
            search_card, 
            text="Clear",
            command=self.clear_search
        )
        clear_btn_frame.grid(row=1, column=2, columnspan=2, sticky="w", padx=10, pady=5)
        
        # New invoice button
        new_btn_frame, new_btn = ClaymorphismTheme.create_button(
            search_card, 
            text="New Invoice",
            command=self.new_invoice
        )
        new_btn_frame.grid(row=1, column=4, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Invoice list
        list_frame, list_card = ClaymorphismTheme.create_card(left_panel)
        list_frame.pack(fill="both", expand=True)
        
        # Treeview for invoices
        self.invoice_tree = ttk.Treeview(list_card, columns=("ID", "Number", "Date", "Customer", "Amount"), show="headings")
        self.invoice_tree.heading("ID", text="ID")
        self.invoice_tree.heading("Number", text="Invoice #")
        self.invoice_tree.heading("Date", text="Date")
        self.invoice_tree.heading("Customer", text="Customer")
        self.invoice_tree.heading("Amount", text="Amount")
        
        self.invoice_tree.column("ID", width=50)
        self.invoice_tree.column("Number", width=120)
        self.invoice_tree.column("Date", width=100)
        self.invoice_tree.column("Customer", width=150)
        self.invoice_tree.column("Amount", width=100)
        
        self.invoice_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.invoice_tree.bind("<<TreeviewSelect>>", self.on_invoice_select)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_card, orient="vertical", command=self.invoice_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.invoice_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = tk.Frame(left_panel, bg=ClaymorphismTheme.BG_PRIMARY)
        button_frame.pack(fill="x", pady=10)
        
        view_btn_frame, view_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="View Invoice",
            command=self.view_invoice
        )
        view_btn_frame.pack(side="left", padx=5)
        
        print_btn_frame, print_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Print Invoice",
            command=self.print_invoice
        )
        print_btn_frame.pack(side="left", padx=5)
        
        refresh_btn_frame, refresh_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Refresh",
            command=self.load_invoices
        )
        refresh_btn_frame.pack(side="left", padx=5)
        
        # Right panel - Invoice details
        right_panel = tk.Frame(content_frame, bg=ClaymorphismTheme.BG_PRIMARY, width=600)
        right_panel.pack(side="right", fill="both")
        right_panel.pack_propagate(False)
        
        # Invoice details card
        details_frame, details_card = ClaymorphismTheme.create_card(right_panel, text="Invoice Details")
        details_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initially show a placeholder
        placeholder_label = tk.Label(details_card, text="Select an invoice to view details", 
                                   bg=ClaymorphismTheme.BG_CARD, 
                                   font=ClaymorphismTheme.FONT_SUBTITLE,
                                   fg=ClaymorphismTheme.TEXT_SECONDARY)
        placeholder_label.pack(pady=50)
        
        self.details_content = placeholder_label
        
        # Load invoices
        self.load_invoices()
    
    def load_invoices(self):
        """Load invoices into the treeview"""
        # Clear existing items
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        
        # Get invoices from database
        invoices = self.db.get_invoices()
        
        # Add invoices to treeview
        for invoice in invoices:
            self.invoice_tree.insert("", "end", values=(
                invoice["invoice_id"],
                invoice["invoice_number"],
                invoice["date"].strftime("%Y-%m-%d"),
                invoice["customer_name"],
                f"₹{invoice['total']:.2f}"
            ))
    
    def search_invoices(self):
        """Search invoices based on criteria"""
        customer = self.customer_entry.get().strip()
        from_date_str = self.from_date.get().strip()
        to_date_str = self.to_date.get().strip()
        
        from_date = None
        to_date = None
        
        if from_date_str:
            try:
                from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showwarning("Invalid Date", "Please enter a valid from date in YYYY-MM-DD format.")
                return
        
        if to_date_str:
            try:
                to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showwarning("Invalid Date", "Please enter a valid to date in YYYY-MM-DD format.")
                return
        
        # Clear existing items
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        
        # Get invoices from database
        invoices = self.db.search_invoices(customer=customer, from_date=from_date, to_date=to_date)
        
        # Add invoices to treeview
        for invoice in invoices:
            self.invoice_tree.insert("", "end", values=(
                invoice["invoice_id"],
                invoice["invoice_number"],
                invoice["date"].strftime("%Y-%m-%d"),
                invoice["customer_name"],
                f"₹{invoice['total']:.2f}"
            ))
    
    def clear_search(self):
        """Clear search fields"""
        self.customer_entry.delete(0, "end")
        self.from_date.delete(0, "end")
        self.to_date.delete(0, "end")
        self.load_invoices()
    
    def on_invoice_select(self, event):
        """Handle invoice selection"""
        selected_items = self.invoice_tree.selection()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        invoice_id = self.invoice_tree.item(selected_item, "values")[0]
        
        # Get invoice details
        invoice = self.db.get_invoice_by_number(self.invoice_tree.item(selected_item, "values")[1])
        
        if invoice:
            self.display_invoice_details(invoice)
    
    def display_invoice_details(self, invoice):
        """Display invoice details in the right panel"""
        # Clear existing content
        if self.details_content:
            self.details_content.destroy()
        
        # Get invoice items
        items = self.db.get_invoice_items(invoice["invoice_id"])
        
        # Create details frame
        details_frame = tk.Frame(self.parent, bg=ClaymorphismTheme.BG_CARD)
        self.details_content = details_frame
        
        # Invoice header
        header_frame = tk.Frame(details_frame, bg=ClaymorphismTheme.BG_CARD)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Invoice number and date
        inv_num_label = tk.Label(header_frame, text=f"Invoice: {invoice['invoice_number']}", 
                               bg=ClaymorphismTheme.BG_CARD, 
                               font=ClaymorphismTheme.FONT_SUBTITLE,
                               fg=ClaymorphismTheme.TEXT_PRIMARY)
        inv_num_label.pack(side="left")
        
        inv_date_label = tk.Label(header_frame, text=f"Date: {invoice['date'].strftime('%d-%m-%Y')}", 
                                 bg=ClaymorphismTheme.BG_CARD, 
                                 font=ClaymorphismTheme.FONT_NORMAL,
                                 fg=ClaymorphismTheme.TEXT_SECONDARY)
        inv_date_label.pack(side="right")
        
        # Customer details
        customer_frame = tk.Frame(details_frame, bg=ClaymorphismTheme.BG_CARD)
        customer_frame.pack(fill="x", padx=10, pady=5)
        
        cust_label = tk.Label(customer_frame, text="Customer:", bg=ClaymorphismTheme.BG_CARD, 
                            font=ClaymorphismTheme.FONT_SUBTITLE,
                            fg=ClaymorphismTheme.TEXT_PRIMARY)
        cust_label.pack(anchor="w")
        
        cust_name_label = tk.Label(customer_frame, text=invoice["customer_name"], 
                                  bg=ClaymorphismTheme.BG_CARD, 
                                  font=ClaymorphismTheme.FONT_NORMAL,
                                  fg=ClaymorphismTheme.TEXT_PRIMARY)
        cust_name_label.pack(anchor="w", padx=20)
        
        if invoice["customer_place"]:
            cust_place_label = tk.Label(customer_frame, text=invoice["customer_place"], 
                                       bg=ClaymorphismTheme.BG_CARD, 
                                       font=ClaymorphismTheme.FONT_NORMAL,
                                       fg=ClaymorphismTheme.TEXT_SECONDARY)
            cust_place_label.pack(anchor="w", padx=20)
        
        if invoice["customer_phone"]:
            cust_phone_label = tk.Label(customer_frame, text=invoice["customer_phone"], 
                                      bg=ClaymorphismTheme.BG_CARD, 
                                      font=ClaymorphismTheme.FONT_NORMAL,
                                      fg=ClaymorphismTheme.TEXT_SECONDARY)
            cust_phone_label.pack(anchor="w", padx=20)
        
        # Items table
        items_frame = tk.Frame(details_frame, bg=ClaymorphismTheme.BG_CARD)
        items_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        items_label = tk.Label(items_frame, text="Items:", bg=ClaymorphismTheme.BG_CARD, 
                              font=ClaymorphismTheme.FONT_SUBTITLE,
                              fg=ClaymorphismTheme.TEXT_PRIMARY)
        items_label.pack(anchor="w")
        
        # Create treeview for items
        items_tree = ttk.Treeview(items_frame, columns=("Product", "Height", "Width", "Sqft", "Rate", "Amount"), show="headings")
        items_tree.heading("Product", text="Product")
        items_tree.heading("Height", text="Height")
        items_tree.heading("Width", text="Width")
        items_tree.heading("Sqft", text="Sqft")
        items_tree.heading("Rate", text="Rate")
        items_tree.heading("Amount", text="Amount")
        
        items_tree.column("Product", width=150)
        items_tree.column("Height", width=80)
        items_tree.column("Width", width=80)
        items_tree.column("Sqft", width=80)
        items_tree.column("Rate", width=80)
        items_tree.column("Amount", width=100)
        
        items_tree.pack(fill="both", expand=True, pady=5)
        
        # Add items to treeview
        for item in items:
            items_tree.insert("", "end", values=(
                item["product_name"],
                f"{item['actual_height']:.2f}",
                f"{item['actual_width']:.2f}",
                f"{item['sqft']:.2f}",
                f"₹{item['rate']:.2f}",
                f"₹{item['amount']:.2f}"
            ))
        
        # Totals
        totals_frame = tk.Frame(details_frame, bg=ClaymorphismTheme.BG_CARD)
        totals_frame.pack(fill="x", padx=10, pady=10)
        
        # Subtotal
        subtotal_label = tk.Label(totals_frame, text=f"Subtotal: ₹{invoice['subtotal']:.2f}", 
                                 bg=ClaymorphismTheme.BG_CARD, 
                                 font=ClaymorphismTheme.FONT_NORMAL,
                                 fg=ClaymorphismTheme.TEXT_PRIMARY)
        subtotal_label.pack(anchor="e")
        
        # Extra charges
        if invoice["extra_charges"]:
            extra_label = tk.Label(totals_frame, text=f"Extra Charges: ₹{invoice['extra_charges']:.2f}", 
                                 bg=ClaymorphismTheme.BG_CARD, 
                                 font=ClaymorphismTheme.FONT_NORMAL,
                                 fg=ClaymorphismTheme.TEXT_PRIMARY)
            extra_label.pack(anchor="e")
        
        # Round off
        if invoice["round_off"]:
            round_label = tk.Label(totals_frame, text=f"Round Off: ₹{invoice['round_off']:.2f}", 
                                  bg=ClaymorphismTheme.BG_CARD, 
                                  font=ClaymorphismTheme.FONT_NORMAL,
                                  fg=ClaymorphismTheme.TEXT_PRIMARY)
            round_label.pack(anchor="e")
        
        # Total
        total_label = tk.Label(totals_frame, text=f"Total: ₹{invoice['total']:.2f}", 
                              bg=ClaymorphismTheme.BG_CARD, 
                              font=ClaymorphismTheme.FONT_SUBTITLE,
                              fg=ClaymorphismTheme.TEXT_PRIMARY)
        total_label.pack(anchor="e", pady=(10, 0))
        
        # Payment details
        payment_frame = tk.Frame(details_frame, bg=ClaymorphismTheme.BG_CARD)
        payment_frame.pack(fill="x", padx=10, pady=10)
        
        payment_label = tk.Label(payment_frame, text="Payment:", bg=ClaymorphismTheme.BG_CARD, 
                               font=ClaymorphismTheme.FONT_SUBTITLE,
                               fg=ClaymorphismTheme.TEXT_PRIMARY)
        payment_label.pack(anchor="w")
        
        mode_label = tk.Label(payment_frame, text=f"Mode: {invoice['payment_mode']}", 
                             bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL,
                             fg=ClaymorphismTheme.TEXT_PRIMARY)
        mode_label.pack(anchor="w", padx=20)
        
        if invoice["p_pay_no"]:
            ref_label = tk.Label(payment_frame, text=f"Reference: {invoice['p_pay_no']}", 
                                bg=ClaymorphismTheme.BG_CARD, 
                                font=ClaymorphismTheme.FONT_NORMAL,
                                fg=ClaymorphismTheme.TEXT_PRIMARY)
            ref_label.pack(anchor="w", padx=20)
        
        # Store current invoice for printing
        self.current_invoice = invoice
        self.current_items = items
    
    def new_invoice(self):
        """Open dialog to create a new invoice"""
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Create New Invoice")
        dialog.geometry("900x600")
        dialog.configure(bg=ClaymorphismTheme.BG_PRIMARY)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create invoice form
        form_frame = tk.Frame(dialog, bg=ClaymorphismTheme.BG_PRIMARY)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame, header_card = ClaymorphismTheme.create_card(form_frame, text="New Invoice", height=60)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Customer selection
        customer_frame = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        customer_frame.pack(fill="x", pady=10)
        
        customer_label = tk.Label(customer_frame, text="Customer:", bg=ClaymorphismTheme.BG_PRIMARY, 
                                 font=ClaymorphismTheme.FONT_NORMAL)
        customer_label.pack(side="left", padx=5)
        
        customer_combo_frame, customer_combo = ClaymorphismTheme.create_combobox(customer_frame, width=30)
        customer_combo_frame.pack(side="left", padx=5)
        
        # Get customers and populate combobox
        customers = self.db.get_customers()
        customer_names = [f"{c['customer_id']} - {c['name']}" for c in customers]
        customer_combo['values'] = customer_names
        
        # Date
        date_label = tk.Label(customer_frame, text="Date:", bg=ClaymorphismTheme.BG_PRIMARY, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        date_label.pack(side="left", padx=5)
        
        date_entry_frame, date_entry = ClaymorphismTheme.create_entry(customer_frame, width=15)
        date_entry_frame.pack(side="left", padx=5)
        
        # Set today's date
        today = datetime.now().strftime("%Y-%m-%d")
        date_entry.insert(0, today)
        
        # Invoice number (auto-generated)
        inv_num_label = tk.Label(customer_frame, text="Invoice #:", bg=ClaymorphismTheme.BG_PRIMARY, 
                                font=ClaymorphismTheme.FONT_NORMAL)
        inv_num_label.pack(side="left", padx=5)
        
        inv_num_frame, inv_num_entry = ClaymorphismTheme.create_entry(customer_frame, width=15)
        inv_num_frame.pack(side="left", padx=5)
        
        # Generate invoice number
        invoice_number = self.db.generate_invoice_number()
        inv_num_entry.insert(0, invoice_number)
        inv_num_entry.config(state="disabled")
        
        # Items frame
        items_frame, items_card = ClaymorphismTheme.create_card(form_frame, text="Invoice Items")
        items_frame.pack(fill="both", expand=True, pady=10)
        
        # Items table
        items_container = tk.Frame(items_card, bg=ClaymorphismTheme.BG_CARD)
        items_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create treeview for items
        items_tree = ttk.Treeview(items_container, columns=("Product", "Height", "Width", "Sqft", "Rate", "Amount"), show="headings")
        items_tree.heading("Product", text="Product")
        items_tree.heading("Height", text="Height")
        items_tree.heading("Width", text="Width")
        items_tree.heading("Sqft", text="Sqft")
        items_tree.heading("Rate", text="Rate")
        items_tree.heading("Amount", text="Amount")
        
        items_tree.column("Product", width=150)
        items_tree.column("Height", width=80)
        items_tree.column("Width", width=80)
        items_tree.column("Sqft", width=80)
        items_tree.column("Rate", width=80)
        items_tree.column("Amount", width=100)
        
        items_tree.pack(fill="both", expand=True, pady=5)
        
        # Scrollbar for items treeview
        items_scrollbar = ttk.Scrollbar(items_container, orient="vertical", command=items_tree.yview)
        items_scrollbar.pack(side="right", fill="y")
        items_tree.configure(yscrollcommand=items_scrollbar.set)
        
        # Add item button
        add_item_btn_frame, add_item_btn = ClaymorphismTheme.create_button(
            items_card, 
            text="Add Item",
            command=lambda: self.add_invoice_item(dialog, items_tree, customers)
        )
        add_item_btn_frame.pack(pady=10)
        
        # Totals frame
        totals_frame = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        totals_frame.pack(fill="x", pady=10)
        
        # Subtotal
        subtotal_label = tk.Label(totals_frame, text="Subtotal: ₹0.00", 
                                 bg=ClaymorphismTheme.BG_PRIMARY, 
                                 font=ClaymorphismTheme.FONT_NORMAL,
                                 fg=ClaymorphismTheme.TEXT_PRIMARY)
        subtotal_label.pack(side="left", padx=20)
        
        # Extra charges
        extra_frame = tk.Frame(totals_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        extra_frame.pack(side="left", padx=20)
        
        extra_label = tk.Label(extra_frame, text="Extra Charges:", bg=ClaymorphismTheme.BG_PRIMARY, 
                              font=ClaymorphismTheme.FONT_NORMAL,
                              fg=ClaymorphismTheme.TEXT_PRIMARY)
        extra_label.pack(side="left")
        
        extra_entry_frame, extra_entry = ClaymorphismTheme.create_entry(extra_frame, width=10)
        extra_entry_frame.pack(side="left")
        extra_entry.insert(0, "0.00")
        
        # Round off
        round_frame = tk.Frame(totals_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        round_frame.pack(side="left", padx=20)
        
        round_label = tk.Label(round_frame, text="Round Off:", bg=ClaymorphismTheme.BG_PRIMARY, 
                               font=ClaymorphismTheme.FONT_NORMAL,
                               fg=ClaymorphismTheme.TEXT_PRIMARY)
        round_label.pack(side="left")
        
        round_entry_frame, round_entry = ClaymorphismTheme.create_entry(round_frame, width=10)
        round_entry_frame.pack(side="left")
        round_entry.insert(0, "0.00")
        
        # Total
        total_label = tk.Label(totals_frame, text="Total: ₹0.00", 
                              bg=ClaymorphismTheme.BG_PRIMARY, 
                              font=ClaymorphismTheme.FONT_SUBTITLE,
                              fg=ClaymorphismTheme.TEXT_PRIMARY)
        total_label.pack(side="right", padx=20)
        
        # Payment details
        payment_frame = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        payment_frame.pack(fill="x", pady=10)
        
        # Payment mode
        mode_label = tk.Label(payment_frame, text="Payment Mode:", bg=ClaymorphismTheme.BG_PRIMARY, 
                            font=ClaymorphismTheme.FONT_NORMAL)
        mode_label.pack(side="left", padx=5)
        
        mode_combo_frame, mode_combo = ClaymorphismTheme.create_combobox(payment_frame, width=15)
        mode_combo_frame.pack(side="left", padx=5)
        mode_combo['values'] = ("Cash", "UPI", "Bank Transfer", "Cheque")
        mode_combo.current(0)
        
        # Reference number
        ref_label = tk.Label(payment_frame, text="Reference:", bg=ClaymorphismTheme.BG_PRIMARY, 
                            font=ClaymorphismTheme.FONT_NORMAL)
        ref_label.pack(side="left", padx=5)
        
        ref_entry_frame, ref_entry = ClaymorphismTheme.create_entry(payment_frame, width=15)
        ref_entry_frame.pack(side="left", padx=5)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        button_frame.pack(fill="x", pady=20)
        
        save_btn_frame, save_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Save Invoice",
            command=lambda: self.save_invoice(
                dialog, customer_combo, date_entry, inv_num_entry, items_tree,
                extra_entry, round_entry, total_label, mode_combo, ref_entry, customers
            )
        )
        save_btn_frame.pack(side="left", padx=5)
        
        cancel_btn_frame, cancel_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Cancel",
            command=dialog.destroy
        )
        cancel_btn_frame.pack(side="left", padx=5)
        
        # Store references to UI elements
        dialog.items_tree = items_tree
        dialog.subtotal_label = subtotal_label
        dialog.total_label = total_label
    
    def add_invoice_item(self, dialog, items_tree, customers):
        """Open dialog to add an item to the invoice"""
        # Create dialog window
        item_dialog = tk.Toplevel(dialog)
        item_dialog.title("Add Invoice Item")
        item_dialog.geometry("500x300")
        item_dialog.configure(bg=ClaymorphismTheme.BG_PRIMARY)
        item_dialog.transient(dialog)
        item_dialog.grab_set()
        
        # Center the dialog
        item_dialog.update_idletasks()
        width = item_dialog.winfo_width()
        height = item_dialog.winfo_height()
        x = (item_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (item_dialog.winfo_screenheight() // 2) - (height // 2)
        item_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Form frame
        form_frame = tk.Frame(item_dialog, bg=ClaymorphismTheme.BG_PRIMARY)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Product selection
        product_label = tk.Label(form_frame, text="Product:", bg=ClaymorphismTheme.BG_PRIMARY, 
                                font=ClaymorphismTheme.FONT_NORMAL)
        product_label.grid(row=0, column=0, sticky="w", pady=5)
        
        product_combo_frame, product_combo = ClaymorphismTheme.create_combobox(form_frame, width=30)
        product_combo_frame.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Get products and populate combobox
        products = self.db.get_products()
        product_names = [p["name"] for p in products]
        product_combo['values'] = product_names
        
        # Dimensions
        height_label = tk.Label(form_frame, text="Height (ft):", bg=ClaymorphismTheme.BG_PRIMARY, 
                               font=ClaymorphismTheme.FONT_NORMAL)
        height_label.grid(row=1, column=0, sticky="w", pady=5)
        
        height_entry_frame, height_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        height_entry_frame.grid(row=1, column=1, sticky="ew", pady=5)
        
        width_label = tk.Label(form_frame, text="Width (ft):", bg=ClaymorphismTheme.BG_PRIMARY, 
                              font=ClaymorphismTheme.FONT_NORMAL)
        width_label.grid(row=2, column=0, sticky="w", pady=5)
        
        width_entry_frame, width_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        width_entry_frame.grid(row=2, column=1, sticky="ew", pady=5)
        
        # Chargeable dimensions
        chargeable_frame = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        chargeable_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)
        
        chargeable_label = tk.Label(chargeable_frame, text="Chargeable Dimensions:", bg=ClaymorphismTheme.BG_PRIMARY, 
                                   font=ClaymorphismTheme.FONT_NORMAL)
        chargeable_label.pack(side="left", padx=5)
        
        chargeable_height_frame, chargeable_height_entry = ClaymorphismTheme.create_entry(chargeable_frame, width=10)
        chargeable_height_frame.pack(side="left", padx=5)
        
        chargeable_width_frame, chargeable_width_entry = ClaymorphismTheme.create_entry(chargeable_frame, width=10)
        chargeable_width_frame.pack(side="left", padx=5)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        add_btn_frame, add_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Add",
            command=lambda: self.add_item_to_invoice(
                item_dialog, dialog, product_combo, height_entry, width_entry,
                chargeable_height_entry, chargeable_width_entry, products
            )
        )
        add_btn_frame.pack(side="left", padx=5)
        
        cancel_btn_frame, cancel_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Cancel",
            command=item_dialog.destroy
        )
        cancel_btn_frame.pack(side="left", padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
        # Bind events to auto-calculate chargeable dimensions
        height_entry.bind("<KeyRelease>", lambda e: self.calculate_chargeable(height_entry, width_entry, chargeable_height_entry, chargeable_width_entry))
        width_entry.bind("<KeyRelease>", lambda e: self.calculate_chargeable(height_entry, width_entry, chargeable_height_entry, chargeable_width_entry))
    
    def calculate_chargeable(self, height_entry, width_entry, chargeable_height_entry, chargeable_width_entry):
        """Calculate chargeable dimensions based on actual dimensions"""
        try:
            height = float(height_entry.get())
            width = float(width_entry.get())
            
            # Calculate chargeable dimensions (round up to nearest 0.5)
            chargeable_height = ((int(height * 2) + 1) // 2) / 2
            chargeable_width = ((int(width * 2) + 1) // 2) / 2
            
            chargeable_height_entry.delete(0, "end")
            chargeable_height_entry.insert(0, str(chargeable_height))
            
            chargeable_width_entry.delete(0, "end")
            chargeable_width_entry.insert(0, str(chargeable_width))
        except ValueError:
            pass
    
    def add_item_to_invoice(self, item_dialog, dialog, product_combo, height_entry, width_entry, 
                           chargeable_height_entry, chargeable_width_entry, products):
        """Add item to invoice"""
        # Get form data
        product_name = product_combo.get()
        height_str = height_entry.get().strip()
        width_str = width_entry.get().strip()
        chargeable_height_str = chargeable_height_entry.get().strip()
        chargeable_width_str = chargeable_width_entry.get().strip()
        
        # Validate form
        if not product_name:
            messagebox.showwarning("Validation Error", "Please select a product.")
            return
        
        if not height_str or not width_str:
            messagebox.showwarning("Validation Error", "Height and width are required.")
            return
        
        try:
            height = float(height_str)
            width = float(width_str)
            chargeable_height = float(chargeable_height_str)
            chargeable_width = float(chargeable_width_str)
            
            if height <= 0 or width <= 0 or chargeable_height <= 0 or chargeable_width <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation Error", "Dimensions must be positive numbers.")
            return
        
        # Get product details
        product = next((p for p in products if p["name"] == product_name), None)
        if not product:
            messagebox.showerror("Error", "Product not found.")
            return
        
        # Calculate sqft and amount
        sqft = chargeable_height * chargeable_width
        rate = product["rate_per_sqft"]
        amount = sqft * rate
        
        # Add item to treeview
        dialog.items_tree.insert("", "end", values=(
            product_name,
            f"{height:.2f}",
            f"{width:.2f}",
            f"{sqft:.2f}",
            f"₹{rate:.2f}",
            f"₹{amount:.2f}"
        ))
        
        # Update totals
        self.update_invoice_totals(dialog)
        
        # Close dialog
        item_dialog.destroy()
    
    def update_invoice_totals(self, dialog):
        """Update invoice totals"""
        subtotal = 0
        
        # Calculate subtotal from items
        for item in dialog.items_tree.get_children():
            values = dialog.items_tree.item(item, "values")
            amount_str = values[5].replace("₹", "")
            amount = float(amount_str)
            subtotal += amount
        
        # Get extra charges and round off
        extra_str = dialog.children['!frame'].children['!frame3'].children['!frame'].children['!entry'].get()
        round_str = dialog.children['!frame'].children['!frame3'].children['!frame2'].children['!entry'].get()
        
        try:
            extra = float(extra_str)
        except ValueError:
            extra = 0
        
        try:
            round_off = float(round_str)
        except ValueError:
            round_off = 0
        
        # Calculate total
        total = subtotal + extra + round_off
        
        # Update labels
        dialog.subtotal_label.config(text=f"Subtotal: ₹{subtotal:.2f}")
        dialog.total_label.config(text=f"Total: ₹{total:.2f}")
    
    def save_invoice(self, dialog, customer_combo, date_entry, inv_num_entry, items_tree,
                    extra_entry, round_entry, total_label, mode_combo, ref_entry, customers):
        """Save invoice to database"""
        # Get form data
        customer_str = customer_combo.get()
        date_str = date_entry.get().strip()
        invoice_number = inv_num_entry.get().strip()
        extra_str = extra_entry.get().strip()
        round_str = round_entry.get().strip()
        payment_mode = mode_combo.get()
        reference = ref_entry.get().strip()
        
        # Validate form
        if not customer_str:
            messagebox.showwarning("Validation Error", "Please select a customer.")
            return
        
        if not date_str:
            messagebox.showwarning("Validation Error", "Date is required.")
            return
        
        if not invoice_number:
            messagebox.showwarning("Validation Error", "Invoice number is required.")
            return
        
        if not payment_mode:
            messagebox.showwarning("Validation Error", "Payment mode is required.")
            return
        
        # Check if there are any items
        if not items_tree.get_children():
            messagebox.showwarning("Validation Error", "Please add at least one item to the invoice.")
            return
        
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter a valid date in YYYY-MM-DD format.")
            return
        
        try:
            extra = float(extra_str)
        except ValueError:
            extra = 0
        
        try:
            round_off = float(round_str)
        except ValueError:
            round_off = 0
        
        # Get customer ID
        customer_id = int(customer_str.split(" - ")[0])
        
        # Get total
        total_str = total_label.cget("text").replace("Total: ₹", "")
        total = float(total_str)
        
        # Calculate subtotal
        subtotal = total - extra - round_off
        
        # Add invoice to database
        invoice_id = self.db.add_invoice(
            customer_id, date, invoice_number, subtotal, extra, round_off, total, payment_mode, reference
        )
        
        if not invoice_id:
            messagebox.showerror("Error", "Failed to create invoice.")
            return
        
        # Add items to database
        all_items_saved = True
        
        for item in items_tree.get_children():
            values = items_tree.item(item, "values")
            product_name = values[0]
            actual_height = float(values[1])
            actual_width = float(values[2])
            chargeable_height = float(values[3])
            chargeable_width = float(values[4])
            sqft = float(values[4])
            rate = float(values[5].replace("₹", ""))
            amount = float(values[6].replace("₹", ""))
            
            # Get product ID
            products = self.db.get_products()
            product = next((p for p in products if p["name"] == product_name), None)
            
            if not product:
                all_items_saved = False
                continue
            
            # Add item to database
            success = self.db.add_invoice_item(
                invoice_id, product["product_id"], actual_height, actual_width,
                chargeable_height, chargeable_width, sqft, rate, amount, 1
            )
            
            if not success:
                all_items_saved = False
        
        if all_items_saved:
            messagebox.showinfo("Success", "Invoice created successfully.")
            dialog.destroy()
            self.load_invoices()
        else:
            messagebox.showerror("Error", "Failed to save some invoice items.")
    
    def view_invoice(self):
        """View selected invoice"""
        selected_items = self.invoice_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select an invoice to view.")
            return
        
        # Get invoice details
        selected_item = selected_items[0]
        invoice_number = self.invoice_tree.item(selected_item, "values")[1]
        
        invoice = self.db.get_invoice_by_number(invoice_number)
        
        if invoice:
            self.display_invoice_details(invoice)
    
    def print_invoice(self):
        """Print selected invoice"""
        if not hasattr(self, 'current_invoice'):
            messagebox.showwarning("No Invoice", "Please select an invoice to print.")
            return
        
        # In a real application, this would generate a PDF or print the invoice
        # For now, we'll just show a message
        messagebox.showinfo("Print Invoice", f"Invoice {self.current_invoice['invoice_number']} sent to printer.")
    
    @staticmethod
    def create_combobox(parent, width=20, **kwargs):
        """Create a claymorphism-style combobox widget"""
        combo_frame = tk.Frame(parent, bg=ClaymorphismTheme.BG_PRIMARY)
        
        # Shadow effect
        shadow = tk.Frame(combo_frame, bg=ClaymorphismTheme.SHADOW, 
                         highlightthickness=0)
        shadow.place(x=2, y=2, relwidth=1, relheight=1)
        
        # Combobox
        combo = ttk.Combobox(combo_frame, width=width, **kwargs)
        combo.pack(fill="both", expand=True, padx=5, pady=5)
        
        return combo_frame, combo
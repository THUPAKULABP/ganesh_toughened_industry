import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from theme import ClaymorphismTheme

class InventoryModule:
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
            text="Inventory Management", 
            height=80
        )
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Content area
        content_frame = tk.Frame(main_container, bg=ClaymorphismTheme.BG_PRIMARY)
        content_frame.pack(fill="both", expand=True)
        
        # Left panel - Inventory status
        left_panel = tk.Frame(content_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Inventory status card
        status_frame, status_card = ClaymorphismTheme.create_card(left_panel, text="Current Inventory")
        status_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Treeview for inventory status
        self.inventory_tree = ttk.Treeview(status_card, columns=("ID", "Name", "Type", "Quantity"), show="headings")
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text="Name")
        self.inventory_tree.heading("Type", text="Type")
        self.inventory_tree.heading("Quantity", text="Quantity")
        
        self.inventory_tree.column("ID", width=50)
        self.inventory_tree.column("Name", width=150)
        self.inventory_tree.column("Type", width=100)
        self.inventory_tree.column("Quantity", width=100)
        
        self.inventory_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(status_card, orient="vertical", command=self.inventory_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = tk.Frame(left_panel, bg=ClaymorphismTheme.BG_PRIMARY)
        button_frame.pack(fill="x", pady=10)
        
        refresh_btn_frame, refresh_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Refresh",
            command=self.load_inventory
        )
        refresh_btn_frame.pack(side="left", padx=5)
        
        # Right panel - Inventory transactions
        right_panel = tk.Frame(content_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Inventory transactions card
        trans_frame, trans_card = ClaymorphismTheme.create_card(right_panel, text="Inventory Transactions")
        trans_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Filter frame
        filter_frame = tk.Frame(trans_card, bg=ClaymorphismTheme.BG_CARD)
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        # Date filter
        date_label = tk.Label(filter_frame, text="Date:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        date_label.pack(side="left", padx=5)
        
        self.date_entry_frame, self.date_entry = ClaymorphismTheme.create_entry(filter_frame, width=15)
        self.date_entry_frame.pack(side="left", padx=5)
        
        # Set today's date as default
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today)
        
        # Filter button
        filter_btn_frame, filter_btn = ClaymorphismTheme.create_button(
            filter_frame, 
            text="Filter",
            command=self.filter_transactions
        )
        filter_btn_frame.pack(side="left", padx=5)
        
        # Clear filter button
        clear_btn_frame, clear_btn = ClaymorphismTheme.create_button(
            filter_frame, 
            text="Clear",
            command=self.clear_filter
        )
        clear_btn_frame.pack(side="left", padx=5)
        
        # Add transaction button
        add_btn_frame, add_btn = ClaymorphismTheme.create_button(
            filter_frame, 
            text="Add Transaction",
            command=self.add_transaction
        )
        add_btn_frame.pack(side="right", padx=5)
        
        # Transactions treeview
        self.trans_tree = ttk.Treeview(trans_card, columns=("ID", "Date", "Product", "Type", "Quantity", "Notes"), show="headings")
        self.trans_tree.heading("ID", text="ID")
        self.trans_tree.heading("Date", text="Date")
        self.trans_tree.heading("Product", text="Product")
        self.trans_tree.heading("Type", text="Type")
        self.trans_tree.heading("Quantity", text="Quantity")
        self.trans_tree.heading("Notes", text="Notes")
        
        self.trans_tree.column("ID", width=50)
        self.trans_tree.column("Date", width=100)
        self.trans_tree.column("Product", width=150)
        self.trans_tree.column("Type", width=70)
        self.trans_tree.column("Quantity", width=80)
        self.trans_tree.column("Notes", width=150)
        
        self.trans_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar for transactions treeview
        trans_scrollbar = ttk.Scrollbar(trans_card, orient="vertical", command=self.trans_tree.yview)
        trans_scrollbar.pack(side="right", fill="y")
        self.trans_tree.configure(yscrollcommand=trans_scrollbar.set)
        
        # Load inventory data
        self.load_inventory()
        self.load_transactions()
    
    def load_inventory(self):
        """Load current inventory status"""
        # Clear existing items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Get inventory from database
        inventory = self.db.get_current_inventory()
        
        # Add inventory to treeview
        for item in inventory:
            self.inventory_tree.insert("", "end", values=(
                item["product_id"],
                item["name"],
                item["type"],
                item["current_quantity"]
            ))
    
    def load_transactions(self, date=None):
        """Load inventory transactions"""
        # Clear existing items
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)
        
        # Get transactions from database
        if date:
            transactions = self.db.get_daily_inventory(date)
        else:
            transactions = self.db.get_daily_inventory()
        
        # Add transactions to treeview
        for trans in transactions:
            self.trans_tree.insert("", "end", values=(
                trans["inventory_id"],
                trans["date"].strftime("%Y-%m-%d"),
                trans["product_name"],
                trans["type"],
                trans["quantity"],
                trans["notes"] or ""
            ))
    
    def filter_transactions(self):
        """Filter transactions by date"""
        date_str = self.date_entry.get().strip()
        
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            self.load_transactions(date)
        except ValueError:
            messagebox.showwarning("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")
    
    def clear_filter(self):
        """Clear date filter"""
        self.date_entry.delete(0, "end")
        self.load_transactions()
    
    def add_transaction(self):
        """Open dialog to add inventory transaction"""
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Inventory Transaction")
        dialog.geometry("500x300")
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
        
        # Form frame
        form_frame = tk.Frame(dialog, bg=ClaymorphismTheme.BG_PRIMARY)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Product selection
        product_label = tk.Label(form_frame, text="Product:", bg=ClaymorphismTheme.BG_PRIMARY, 
                                 font=ClaymorphismTheme.FONT_NORMAL)
        product_label.grid(row=0, column=0, sticky="w", pady=5)
        
        product_frame, product_combo = ClaymorphismTheme.create_combobox(form_frame, width=30)
        product_frame.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Get products and populate combobox
        products = self.db.get_products()
        product_names = [p["name"] for p in products]
        product_combo['values'] = product_names
        
        # Transaction type
        type_label = tk.Label(form_frame, text="Type:", bg=ClaymorphismTheme.BG_PRIMARY, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        type_label.grid(row=1, column=0, sticky="w", pady=5)
        
        type_frame, type_combo = ClaymorphismTheme.create_combobox(form_frame, width=30)
        type_frame.grid(row=1, column=1, sticky="ew", pady=5)
        type_combo['values'] = ("IN", "OUT")
        type_combo.current(0)
        
        # Quantity
        qty_label = tk.Label(form_frame, text="Quantity:", bg=ClaymorphismTheme.BG_PRIMARY, 
                            font=ClaymorphismTheme.FONT_NORMAL)
        qty_label.grid(row=2, column=0, sticky="w", pady=5)
        
        qty_frame, qty_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        qty_frame.grid(row=2, column=1, sticky="ew", pady=5)
        
        # Notes
        notes_label = tk.Label(form_frame, text="Notes:", bg=ClaymorphismTheme.BG_PRIMARY, 
                              font=ClaymorphismTheme.FONT_NORMAL)
        notes_label.grid(row=3, column=0, sticky="nw", pady=5)
        
        notes_text = tk.Text(form_frame, height=4, width=30, 
                            bg=ClaymorphismTheme.BG_SECONDARY,
                            fg=ClaymorphismTheme.TEXT_PRIMARY,
                            relief="flat",
                            borderwidth=0,
                            font=ClaymorphismTheme.FONT_NORMAL)
        notes_text.grid(row=3, column=1, sticky="ew", pady=5)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        save_btn_frame, save_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Save",
            command=lambda: self.save_transaction(
                dialog, product_combo, type_combo, qty_entry, notes_text, products
            )
        )
        save_btn_frame.pack(side="left", padx=5)
        
        cancel_btn_frame, cancel_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Cancel",
            command=dialog.destroy
        )
        cancel_btn_frame.pack(side="left", padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
    
    def save_transaction(self, dialog, product_combo, type_combo, qty_entry, notes_text, products):
        """Save inventory transaction"""
        # Get form data
        product_name = product_combo.get()
        trans_type = type_combo.get()
        qty_str = qty_entry.get().strip()
        notes = notes_text.get(1.0, "end").strip()
        
        # Validate form
        if not product_name:
            messagebox.showwarning("Validation Error", "Please select a product.")
            return
        
        if not qty_str:
            messagebox.showwarning("Validation Error", "Quantity is required.")
            return
        
        try:
            quantity = int(qty_str)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation Error", "Quantity must be a positive integer.")
            return
        
        # Get product ID
        product = next((p for p in products if p["name"] == product_name), None)
        if not product:
            messagebox.showerror("Error", "Product not found.")
            return
        
        # Get current date
        today = datetime.now().date()
        
        # Add inventory record
        inventory_id = self.db.add_inventory(
            product["product_id"], today, trans_type, quantity, notes
        )
        
        if inventory_id:
            messagebox.showinfo("Success", "Inventory transaction added successfully.")
            dialog.destroy()
            self.load_inventory()
            self.load_transactions()
        else:
            messagebox.showerror("Error", "Failed to add inventory transaction.")
    
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
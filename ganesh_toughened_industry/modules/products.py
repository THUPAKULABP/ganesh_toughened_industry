import tkinter as tk
from tkinter import ttk, messagebox
from theme import ClaymorphismTheme

class ProductsModule:
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
            text="Product Management", 
            height=80
        )
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Content area
        content_frame = tk.Frame(main_container, bg=ClaymorphismTheme.BG_PRIMARY)
        content_frame.pack(fill="both", expand=True)
        
        # Left panel - Product list
        left_panel = tk.Frame(content_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Search and filter
        search_frame, search_card = ClaymorphismTheme.create_card(left_panel, height=60)
        search_frame.pack(fill="x", pady=(0, 10))
        
        search_label = tk.Label(search_card, text="Search:", bg=ClaymorphismTheme.BG_CARD, 
                               font=ClaymorphismTheme.FONT_NORMAL)
        search_label.pack(side="left", padx=10, pady=10)
        
        self.search_entry_frame, self.search_entry = ClaymorphismTheme.create_entry(
            search_card, 
            placeholder="Search by name or type...",
            width=30
        )
        self.search_entry_frame.pack(side="left", padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self.search_products)
        
        # Product list
        list_frame, list_card = ClaymorphismTheme.create_card(left_panel)
        list_frame.pack(fill="both", expand=True)
        
        # Treeview for products
        self.product_tree = ttk.Treeview(list_card, columns=("ID", "Name", "Type", "Rate"), show="headings")
        self.product_tree.heading("ID", text="ID")
        self.product_tree.heading("Name", text="Name")
        self.product_tree.heading("Type", text="Type")
        self.product_tree.heading("Rate", text="Rate (₹/sqft)")
        
        self.product_tree.column("ID", width=50)
        self.product_tree.column("Name", width=150)
        self.product_tree.column("Type", width=100)
        self.product_tree.column("Rate", width=100)
        
        self.product_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.product_tree.bind("<<TreeviewSelect>>", self.on_product_select)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_card, orient="vertical", command=self.product_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = tk.Frame(left_panel, bg=ClaymorphismTheme.BG_PRIMARY)
        button_frame.pack(fill="x", pady=10)
        
        add_btn_frame, add_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Add Product",
            command=self.add_product
        )
        add_btn_frame.pack(side="left", padx=5)
        
        edit_btn_frame, edit_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Edit Product",
            command=self.edit_product
        )
        edit_btn_frame.pack(side="left", padx=5)
        
        delete_btn_frame, delete_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Delete Product",
            command=self.delete_product
        )
        delete_btn_frame.pack(side="left", padx=5)
        
        refresh_btn_frame, refresh_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Refresh",
            command=self.load_products
        )
        refresh_btn_frame.pack(side="left", padx=5)
        
        # Right panel - Product details
        right_panel = tk.Frame(content_frame, bg=ClaymorphismTheme.BG_PRIMARY, width=400)
        right_panel.pack(side="right", fill="both")
        right_panel.pack_propagate(False)
        
        # Product details card
        details_frame, details_card = ClaymorphismTheme.create_card(right_panel, text="Product Details")
        details_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Form fields
        form_frame = tk.Frame(details_card, bg=ClaymorphismTheme.BG_CARD)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Name
        name_label = tk.Label(form_frame, text="Name:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        name_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.name_entry_frame, self.name_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        self.name_entry_frame.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Type
        type_label = tk.Label(form_frame, text="Type:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        type_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.type_combo_frame, self.type_combo = ClaymorphismTheme.create_combobox(form_frame, width=27)
        self.type_combo['values'] = ("Glass", "Frame", "Hardware", "Other")
        self.type_combo_frame.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Description
        desc_label = tk.Label(form_frame, text="Description:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        desc_label.grid(row=2, column=0, sticky="nw", pady=5)
        
        self.desc_text = tk.Text(form_frame, height=4, width=30, 
                               bg=ClaymorphismTheme.BG_SECONDARY,
                               fg=ClaymorphismTheme.TEXT_PRIMARY,
                               relief="flat",
                               borderwidth=0,
                               font=ClaymorphismTheme.FONT_NORMAL)
        self.desc_text.grid(row=2, column=1, sticky="ew", pady=5)
        
        # Rate
        rate_label = tk.Label(form_frame, text="Rate (₹/sqft):", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        rate_label.grid(row=3, column=0, sticky="w", pady=5)
        
        self.rate_entry_frame, self.rate_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        self.rate_entry_frame.grid(row=3, column=1, sticky="ew", pady=5)
        
        # Buttons
        button_frame2 = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_CARD)
        button_frame2.grid(row=4, column=0, columnspan=2, pady=10)
        
        save_btn_frame, save_btn = ClaymorphismTheme.create_button(
            button_frame2, 
            text="Save",
            command=self.save_product
        )
        save_btn_frame.pack(side="left", padx=5)
        
        cancel_btn_frame, cancel_btn = ClaymorphismTheme.create_button(
            button_frame2, 
            text="Cancel",
            command=self.clear_form
        )
        cancel_btn_frame.pack(side="left", padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
        # Load products
        self.load_products()
        
        # Initially disable form
        self.toggle_form(False)
    
    def load_products(self):
        """Load products into the treeview"""
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Get products from database
        products = self.db.get_products()
        
        # Add products to treeview
        for product in products:
            self.product_tree.insert("", "end", values=(
                product["product_id"],
                product["name"],
                product["type"],
                f"{product['rate_per_sqft']:.2f}"
            ))
    
    def search_products(self, event=None):
        """Search products based on search entry"""
        search_term = self.search_entry.get().lower()
        
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Get products from database
        products = self.db.get_products()
        
        # Filter products based on search term
        for product in products:
            if (search_term in product["name"].lower() or 
                search_term in product["type"].lower()):
                self.product_tree.insert("", "end", values=(
                    product["product_id"],
                    product["name"],
                    product["type"],
                    f"{product['rate_per_sqft']:.2f}"
                ))
    
    def on_product_select(self, event):
        """Handle product selection"""
        selected_items = self.product_tree.selection()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        product_id = self.product_tree.item(selected_item, "values")[0]
        
        # Get product details
        products = self.db.get_products()
        product = next((p for p in products if p["product_id"] == int(product_id)), None)
        
        if product:
            # Populate form fields
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, product["name"])
            
            self.type_combo.set(product["type"])
            
            self.desc_text.delete(1.0, "end")
            self.desc_text.insert(1.0, product["description"] or "")
            
            self.rate_entry.delete(0, "end")
            self.rate_entry.insert(0, str(product["rate_per_sqft"]))
            
            # Enable form
            self.toggle_form(True)
            self.current_product_id = product["product_id"]
    
    def add_product(self):
        """Add a new product"""
        # Clear form
        self.clear_form()
        
        # Enable form
        self.toggle_form(True)
        
        # Set focus to name entry
        self.name_entry.focus()
        
        # Set mode to add
        self.mode = "add"
    
    def edit_product(self):
        """Edit selected product"""
        selected_items = self.product_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a product to edit.")
            return
        
        # Set mode to edit
        self.mode = "edit"
    
    def delete_product(self):
        """Delete selected product"""
        selected_items = self.product_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a product to delete.")
            return
        
        selected_item = selected_items[0]
        product_id = self.product_tree.item(selected_item, "values")[0]
        product_name = self.product_tree.item(selected_item, "values")[1]
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {product_name}?"):
            # Delete product
            success = self.db.delete_product(int(product_id))
            
            if success:
                messagebox.showinfo("Success", "Product deleted successfully.")
                self.load_products()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Cannot delete product used in invoices.")
    
    def save_product(self):
        """Save product data"""
        # Get form data
        name = self.name_entry.get().strip()
        type_val = self.type_combo.get()
        description = self.desc_text.get(1.0, "end").strip()
        rate_str = self.rate_entry.get().strip()
        
        # Validate form
        if not name:
            messagebox.showwarning("Validation Error", "Name is required.")
            return
        
        if not type_val:
            messagebox.showwarning("Validation Error", "Type is required.")
            return
        
        try:
            rate = float(rate_str)
            if rate <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation Error", "Rate must be a positive number.")
            return
        
        # Save product
        if hasattr(self, 'mode') and self.mode == "add":
            # Add new product
            product_id = self.db.add_product(name, type_val, description, rate)
            
            if product_id:
                messagebox.showinfo("Success", "Product added successfully.")
                self.load_products()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to add product.")
        else:
            # Update existing product
            success = self.db.update_product(
                self.current_product_id, name, type_val, description, rate
            )
            
            if success:
                messagebox.showinfo("Success", "Product updated successfully.")
                self.load_products()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to update product.")
    
    def clear_form(self):
        """Clear form fields"""
        self.name_entry.delete(0, "end")
        self.type_combo.set("")
        self.desc_text.delete(1.0, "end")
        self.rate_entry.delete(0, "end")
        
        # Disable form
        self.toggle_form(False)
        
        # Clear selection
        for item in self.product_tree.selection():
            self.product_tree.selection_remove(item)
    
    def toggle_form(self, enabled):
        """Enable or disable form fields"""
        state = "normal" if enabled else "disabled"
        
        self.name_entry.config(state=state)
        self.type_combo.config(state=state)
        self.desc_text.config(state=state)
        self.rate_entry.config(state=state)
    
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
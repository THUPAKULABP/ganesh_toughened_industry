import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

class InventoryModule:
    def __init__(self, parent, db, app):
        self.parent = parent
        self.db = db
        self.app = app
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """Create the inventory UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="PRODUCT INVENTORY", style="Title.TLabel")
        title.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        current_tab = ttk.Frame(notebook)
        movements_tab = ttk.Frame(notebook)
        products_tab = ttk.Frame(notebook)
        
        notebook.add(current_tab, text="Current Inventory")
        notebook.add(movements_tab, text="Stock Movements")
        notebook.add(products_tab, text="Product Management")
        
        # Create current inventory tab
        self.create_current_inventory_tab(current_tab)
        
        # Create stock movements tab
        self.create_movements_tab(movements_tab)
        
        # Create product management tab
        self.create_products_tab(products_tab)
    
    def create_current_inventory_tab(self, parent):
        """Create the current inventory tab"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Filter frame
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Product type filter
        ttk.Label(filter_frame, text="Product Type:").pack(side=tk.LEFT, padx=5)
        self.type_var = tk.StringVar()
        product_types = ["All", "Plain", "Toughened", "Laminated"]
        type_combo = ttk.Combobox(filter_frame, textvariable=self.type_var, values=product_types, state="readonly")
        type_combo.pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        refresh_btn = ttk.Button(filter_frame, text="Refresh", command=self.refresh_current_inventory)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Inventory treeview
        self.inventory_tree = ttk.Treeview(main_frame, columns=("product", "type", "stock_in", "stock_out", "current_stock"), show="headings")
        self.inventory_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        self.inventory_tree.heading("product", text="Product")
        self.inventory_tree.heading("type", text="Type")
        self.inventory_tree.heading("stock_in", text="Stock In")
        self.inventory_tree.heading("stock_out", text="Stock Out")
        self.inventory_tree.heading("current_stock", text="Current Stock")
        
        # Define columns
        self.inventory_tree.column("product", width=200)
        self.inventory_tree.column("type", width=100)
        self.inventory_tree.column("stock_in", width=100)
        self.inventory_tree.column("stock_out", width=100)
        self.inventory_tree.column("current_stock", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        
        # Summary frame
        summary_frame = ttk.Frame(main_frame)
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Total stock in
        stock_in_frame = ttk.Frame(summary_frame)
        stock_in_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(stock_in_frame, text="Total Stock In:").pack(side=tk.LEFT)
        self.total_stock_in_var = tk.StringVar(value="0")
        ttk.Label(stock_in_frame, textvariable=self.total_stock_in_var).pack(side=tk.RIGHT)
        
        # Total stock out
        stock_out_frame = ttk.Frame(summary_frame)
        stock_out_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(stock_out_frame, text="Total Stock Out:").pack(side=tk.LEFT)
        self.total_stock_out_var = tk.StringVar(value="0")
        ttk.Label(stock_out_frame, textvariable=self.total_stock_out_var).pack(side=tk.RIGHT)
        
        # Total current stock
        current_stock_frame = ttk.Frame(summary_frame)
        current_stock_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(current_stock_frame, text="Total Current Stock:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.total_current_stock_var = tk.StringVar(value="0")
        ttk.Label(current_stock_frame, textvariable=self.total_current_stock_var, font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
        
        # Load initial inventory
        self.refresh_current_inventory()
    
    def create_movements_tab(self, parent):
        """Create the stock movements tab"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Filter frame
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Date filter
        ttk.Label(filter_frame, text="Date:").pack(side=tk.LEFT, padx=5)
        self.movement_date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(filter_frame, textvariable=self.movement_date_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Movement type filter
        ttk.Label(filter_frame, text="Type:").pack(side=tk.LEFT, padx=5)
        self.movement_type_var = tk.StringVar()
        movement_types = ["All", "stock_in", "stock_out"]
        movement_type_combo = ttk.Combobox(filter_frame, textvariable=self.movement_type_var, values=movement_types, state="readonly")
        movement_type_combo.pack(side=tk.LEFT, padx=5)
        
        # Search button
        search_btn = ttk.Button(filter_frame, text="Search", command=self.search_movements)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Add movement button
        add_btn = ttk.Button(filter_frame, text="Add Movement", command=self.add_movement)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Movements treeview
        self.movements_tree = ttk.Treeview(main_frame, columns=("date", "product", "type", "quantity", "notes"), show="headings")
        self.movements_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        self.movements_tree.heading("date", text="Date")
        self.movements_tree.heading("product", text="Product")
        self.movements_tree.heading("type", text="Type")
        self.movements_tree.heading("quantity", text="Quantity")
        self.movements_tree.heading("notes", text="Notes")
        
        # Define columns
        self.movements_tree.column("date", width=100)
        self.movements_tree.column("product", width=200)
        self.movements_tree.column("type", width=100)
        self.movements_tree.column("quantity", width=100)
        self.movements_tree.column("notes", width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.movements_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.movements_tree.configure(yscrollcommand=scrollbar.set)
        
        # Summary frame
        summary_frame = ttk.Frame(main_frame)
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Stock in
        in_frame = ttk.Frame(summary_frame)
        in_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(in_frame, text="Stock In:").pack(side=tk.LEFT)
        self.movement_in_var = tk.StringVar(value="0")
        ttk.Label(in_frame, textvariable=self.movement_in_var).pack(side=tk.RIGHT)
        
        # Stock out
        out_frame = ttk.Frame(summary_frame)
        out_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(out_frame, text="Stock Out:").pack(side=tk.LEFT)
        self.movement_out_var = tk.StringVar(value="0")
        ttk.Label(out_frame, textvariable=self.movement_out_var).pack(side=tk.RIGHT)
        
        # Net movement
        net_frame = ttk.Frame(summary_frame)
        net_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(net_frame, text="Net Movement:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.net_movement_var = tk.StringVar(value="0")
        ttk.Label(net_frame, textvariable=self.net_movement_var, font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
        
        # Load initial movements
        self.search_movements()
    
    def create_products_tab(self, parent):
        """Create the product management tab"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Products treeview
        self.products_tree = ttk.Treeview(main_frame, columns=("name", "type", "rate"), show="headings")
        self.products_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        self.products_tree.heading("name", text="Product Name")
        self.products_tree.heading("type", text="Type")
        self.products_tree.heading("rate", text="Rate per SQ.FT")
        
        # Define columns
        self.products_tree.column("name", width=200)
        self.products_tree.column("type", width=100)
        self.products_tree.column("rate", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add product button
        add_btn = ttk.Button(action_frame, text="Add Product", command=self.add_product)
        add_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Edit product button
        edit_btn = ttk.Button(action_frame, text="Edit Product", command=self.edit_product)
        edit_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Delete product button
        delete_btn = ttk.Button(action_frame, text="Delete Product", command=self.delete_product)
        delete_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Load products
        self.load_products()
    
    def refresh_current_inventory(self):
        """Refresh current inventory display"""
        # Clear existing items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Get filter value
        product_type = None if self.type_var.get() == "All" else self.type_var.get()
        
        # Get current inventory
        try:
            inventory = self.db.get_current_inventory()
            
            # Calculate totals
            total_stock_in = 0
            total_stock_out = 0
            total_current_stock = 0
            
            for item in inventory:
                # Apply type filter
                if product_type and item["type"] != product_type:
                    continue
                
                # Add to treeview
                self.inventory_tree.insert("", "end", values=(
                    item["name"],
                    item["type"],
                    f"{item['stock_in']:.2f}",
                    f"{item['stock_out']:.2f}",
                    f"{item['current_stock']:.2f}"
                ))
                
                # Add to totals
                total_stock_in += item["stock_in"]
                total_stock_out += item["stock_out"]
                total_current_stock += item["current_stock"]
            
            # Update totals
            self.total_stock_in_var.set(f"{total_stock_in:.2f}")
            self.total_stock_out_var.set(f"{total_stock_out:.2f}")
            self.total_current_stock_var.set(f"{total_current_stock:.2f}")
            
        except Exception as e:
            print(f"Error refreshing current inventory: {e}")
    
    def search_movements(self):
        """Search stock movements based on filters"""
        # Clear existing items
        for item in self.movements_tree.get_children():
            self.movements_tree.delete(item)
        
        # Get filter values
        date_str = self.movement_date_var.get()
        movement_type = self.movement_type_var.get()
        
        # Parse date
        try:
            day, month, year = date_str.split('/')
            movement_date = date(int(year), int(month), int(day))
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid date in DD/MM/YYYY format")
            return
        
        # Get movements
        try:
            movements = self.db.get_daily_inventory(movement_date)
            
            # Apply type filter
            if movement_type != "All":
                movements = [m for m in movements if m["type"] == movement_type]
            
            # Calculate totals
            total_in = 0
            total_out = 0
            
            for movement in movements:
                # Add to treeview
                self.movements_tree.insert("", "end", values=(
                    movement["date"],
                    movement["product_name"],
                    movement["type"],
                    f"{movement['quantity']:.2f}",
                    movement["notes"] or ""
                ))
                
                # Add to totals
                if movement["type"] == "stock_in":
                    total_in += movement["quantity"]
                else:
                    total_out += movement["quantity"]
            
            # Calculate net movement
            net_movement = total_in - total_out
            
            # Update totals
            self.movement_in_var.set(f"{total_in:.2f}")
            self.movement_out_var.set(f"{total_out:.2f}")
            self.net_movement_var.set(f"{net_movement:.2f}")
            
        except Exception as e:
            print(f"Error searching movements: {e}")
    
    def add_movement(self):
        """Add a new stock movement"""
        # Create movement dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Stock Movement")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Movement details
        ttk.Label(dialog, text="Date:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(dialog, textvariable=date_var).grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Product:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(dialog, textvariable=product_var)
        product_combo.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Load products
        products = self.db.get_products()
        product_names = [f"{product['name']} ({product['type']})" for product in products]
        product_combo["values"] = product_names
        
        ttk.Label(dialog, text="Type:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(dialog, textvariable=type_var, values=["stock_in", "stock_out"], state="readonly")
        type_combo.grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Quantity:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        quantity_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=quantity_var).grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Notes:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        notes_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=notes_var).grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        
        def save_movement():
            try:
                # Parse date
                date_str = date_var.get()
                day, month, year = date_str.split('/')
                movement_date = date(int(year), int(month), int(day))
                
                # Get product
                product_name = product_var.get()
                if not product_name:
                    messagebox.showerror("Error", "Please select a product")
                    return
                
                # Get product ID
                product_id = None
                for product in products:
                    if f"{product['name']} ({product['type']})" == product_name:
                        product_id = product["product_id"]
                        break
                
                if not product_id:
                    messagebox.showerror("Error", "Product not found")
                    return
                
                # Get type
                movement_type = type_var.get()
                if not movement_type:
                    messagebox.showerror("Error", "Please select a movement type")
                    return
                
                # Get quantity
                quantity = float(quantity_var.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0")
                    return
                
                # Add movement
                movement_id = self.db.add_inventory(
                    product_id=product_id,
                    date=movement_date,
                    type=movement_type,
                    quantity=quantity,
                    notes=notes_var.get()
                )
                
                if movement_id:
                    messagebox.showinfo("Success", "Stock movement added successfully")
                    dialog.destroy()
                    # Refresh movements
                    self.search_movements()
                    # Refresh current inventory
                    self.refresh_current_inventory()
                else:
                    messagebox.showerror("Error", "Could not add stock movement")
                    
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values")
            except Exception as e:
                messagebox.showerror("Error", f"Could not add stock movement: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_movement).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        dialog.columnconfigure(1, weight=1)
    
    def load_products(self):
        """Load products into treeview"""
        # Clear existing items
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Get products
        try:
            products = self.db.get_products()
            
            for product in products:
                self.products_tree.insert("", "end", values=(
                    product["name"],
                    product["type"],
                    f"{product['rate_per_sqft']:.2f}"
                ))
        except Exception as e:
            print(f"Error loading products: {e}")
    
    def add_product(self):
        """Add a new product"""
        # Create product dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Product")
        dialog.geometry("400x200")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Product details
        ttk.Label(dialog, text="Name:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var).grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Type:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(dialog, textvariable=type_var, values=["Plain", "Toughened", "Laminated"], state="readonly")
        type_combo.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Rate per SQ.FT:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        rate_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=rate_var).grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        
        def save_product():
            try:
                # Get name
                name = name_var.get().strip()
                if not name:
                    messagebox.showerror("Error", "Product name is required")
                    return
                
                # Get type
                product_type = type_var.get()
                if not product_type:
                    messagebox.showerror("Error", "Please select a product type")
                    return
                
                # Get rate
                rate = float(rate_var.get())
                if rate <= 0:
                    messagebox.showerror("Error", "Rate must be greater than 0")
                    return
                
                # Add product
                product_id = self.db.add_product(
                    name=name,
                    type=product_type,
                    rate_per_sqft=rate
                )
                
                if product_id:
                    messagebox.showinfo("Success", "Product added successfully")
                    dialog.destroy()
                    # Refresh products
                    self.load_products()
                else:
                    messagebox.showerror("Error", "Could not add product")
                    
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values")
            except Exception as e:
                messagebox.showerror("Error", f"Could not add product: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        dialog.columnconfigure(1, weight=1)
    
    def edit_product(self):
        """Edit selected product"""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a product to edit")
            return
        
        # Get product details
        item = self.products_tree.item(selected[0])
        product_name = item["values"][0]
        product_type = item["values"][1]
        rate_str = item["values"][2]
        
        # Get product from database
        products = self.db.get_products()
        product = None
        for p in products:
            if p["name"] == product_name and p["type"] == product_type:
                product = p
                break
        
        if not product:
            messagebox.showerror("Error", "Product not found")
            return
        
        # Create edit product dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Edit Product - {product_name}")
        dialog.geometry("400x200")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Product details
        ttk.Label(dialog, text="Name:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        name_var = tk.StringVar(value=product["name"])
        ttk.Entry(dialog, textvariable=name_var).grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Type:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        type_var = tk.StringVar(value=product["type"])
        type_combo = ttk.Combobox(dialog, textvariable=type_var, values=["Plain", "Toughened", "Laminated"], state="readonly")
        type_combo.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Rate per SQ.FT:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        rate_var = tk.StringVar(value=str(product["rate_per_sqft"]))
        ttk.Entry(dialog, textvariable=rate_var).grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        
        def save_product():
            try:
                # Get name
                name = name_var.get().strip()
                if not name:
                    messagebox.showerror("Error", "Product name is required")
                    return
                
                # Get type
                product_type = type_var.get()
                if not product_type:
                    messagebox.showerror("Error", "Please select a product type")
                    return
                
                # Get rate
                rate = float(rate_var.get())
                if rate <= 0:
                    messagebox.showerror("Error", "Rate must be greater than 0")
                    return
                
                # Update product
                success = self.db.update_product(
                    product_id=product["product_id"],
                    name=name,
                    type=product_type,
                    rate_per_sqft=rate
                )
                
                if success:
                    messagebox.showinfo("Success", "Product updated successfully")
                    dialog.destroy()
                    # Refresh products
                    self.load_products()
                else:
                    messagebox.showerror("Error", "Could not update product")
                    
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values")
            except Exception as e:
                messagebox.showerror("Error", f"Could not update product: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        dialog.columnconfigure(1, weight=1)
    
    def delete_product(self):
        """Delete selected product"""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a product to delete")
            return
        
        # Get product details
        item = self.products_tree.item(selected[0])
        product_name = item["values"][0]
        product_type = item["values"][1]
        
        # Get product from database
        products = self.db.get_products()
        product = None
        for p in products:
            if p["name"] == product_name and p["type"] == product_type:
                product = p
                break
        
        if not product:
            messagebox.showerror("Error", "Product not found")
            return
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {product_name}?"):
            # Delete product from database
            success = self.db.delete_product(product["product_id"])
            
            if success:
                # Refresh products
                self.load_products()
                
                messagebox.showinfo("Success", "Product deleted successfully")
            else:
                messagebox.showerror("Error", "Could not delete product")
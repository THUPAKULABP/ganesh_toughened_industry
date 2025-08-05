import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from theme import ClaymorphismTheme

class CustomersModule:
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
            text="Customer Management", 
            height=80
        )
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Content area
        content_frame = tk.Frame(main_container, bg=ClaymorphismTheme.BG_PRIMARY)
        content_frame.pack(fill="both", expand=True)
        
        # Left panel - Customer list
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
            placeholder="Search by name, place, or phone...",
            width=30
        )
        self.search_entry_frame.pack(side="left", padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self.search_customers)
        
        # Customer list
        list_frame, list_card = ClaymorphismTheme.create_card(left_panel)
        list_frame.pack(fill="both", expand=True)
        
        # Treeview for customers
        self.customer_tree = ttk.Treeview(list_card, columns=("ID", "Name", "Place", "Phone", "GST"), show="headings")
        self.customer_tree.heading("ID", text="ID")
        self.customer_tree.heading("Name", text="Name")
        self.customer_tree.heading("Place", text="Place")
        self.customer_tree.heading("Phone", text="Phone")
        self.customer_tree.heading("GST", text="GST")
        
        self.customer_tree.column("ID", width=50)
        self.customer_tree.column("Name", width=150)
        self.customer_tree.column("Place", width=100)
        self.customer_tree.column("Phone", width=120)
        self.customer_tree.column("GST", width=100)
        
        self.customer_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.customer_tree.bind("<<TreeviewSelect>>", self.on_customer_select)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_card, orient="vertical", command=self.customer_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.customer_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = tk.Frame(left_panel, bg=ClaymorphismTheme.BG_PRIMARY)
        button_frame.pack(fill="x", pady=10)
        
        add_btn_frame, add_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Add Customer",
            command=self.add_customer
        )
        add_btn_frame.pack(side="left", padx=5)
        
        edit_btn_frame, edit_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Edit Customer",
            command=self.edit_customer
        )
        edit_btn_frame.pack(side="left", padx=5)
        
        delete_btn_frame, delete_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Delete Customer",
            command=self.delete_customer
        )
        delete_btn_frame.pack(side="left", padx=5)
        
        refresh_btn_frame, refresh_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Refresh",
            command=self.load_customers
        )
        refresh_btn_frame.pack(side="left", padx=5)
        
        # Right panel - Customer details
        right_panel = tk.Frame(content_frame, bg=ClaymorphismTheme.BG_PRIMARY, width=400)
        right_panel.pack(side="right", fill="both")
        right_panel.pack_propagate(False)
        
        # Customer details card
        details_frame, details_card = ClaymorphismTheme.create_card(right_panel, text="Customer Details")
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
        
        # Place
        place_label = tk.Label(form_frame, text="Place:", bg=ClaymorphismTheme.BG_CARD, 
                              font=ClaymorphismTheme.FONT_NORMAL)
        place_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.place_entry_frame, self.place_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        self.place_entry_frame.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Phone
        phone_label = tk.Label(form_frame, text="Phone:", bg=ClaymorphismTheme.BG_CARD, 
                              font=ClaymorphismTheme.FONT_NORMAL)
        phone_label.grid(row=2, column=0, sticky="w", pady=5)
        
        self.phone_entry_frame, self.phone_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        self.phone_entry_frame.grid(row=2, column=1, sticky="ew", pady=5)
        
        # GST
        gst_label = tk.Label(form_frame, text="GST:", bg=ClaymorphismTheme.BG_CARD, 
                            font=ClaymorphismTheme.FONT_NORMAL)
        gst_label.grid(row=3, column=0, sticky="w", pady=5)
        
        self.gst_entry_frame, self.gst_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        self.gst_entry_frame.grid(row=3, column=1, sticky="ew", pady=5)
        
        # Address
        address_label = tk.Label(form_frame, text="Address:", bg=ClaymorphismTheme.BG_CARD, 
                                font=ClaymorphismTheme.FONT_NORMAL)
        address_label.grid(row=4, column=0, sticky="nw", pady=5)
        
        self.address_text = tk.Text(form_frame, height=4, width=30, 
                                   bg=ClaymorphismTheme.BG_SECONDARY,
                                   fg=ClaymorphismTheme.TEXT_PRIMARY,
                                   relief="flat",
                                   borderwidth=0,
                                   font=ClaymorphismTheme.FONT_NORMAL)
        self.address_text.grid(row=4, column=1, sticky="ew", pady=5)
        
        # Email
        email_label = tk.Label(form_frame, text="Email:", bg=ClaymorphismTheme.BG_CARD, 
                              font=ClaymorphismTheme.FONT_NORMAL)
        email_label.grid(row=5, column=0, sticky="w", pady=5)
        
        self.email_entry_frame, self.email_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        self.email_entry_frame.grid(row=5, column=1, sticky="ew", pady=5)
        
        # Balance
        balance_label = tk.Label(form_frame, text="Balance:", bg=ClaymorphismTheme.BG_CARD, 
                                font=ClaymorphismTheme.FONT_NORMAL)
        balance_label.grid(row=6, column=0, sticky="w", pady=5)
        
        self.balance_label = tk.Label(form_frame, text="₹0.00", bg=ClaymorphismTheme.BG_CARD, 
                                     font=ClaymorphismTheme.FONT_SUBTITLE,
                                     fg=ClaymorphismTheme.TEXT_PRIMARY)
        self.balance_label.grid(row=6, column=1, sticky="w", pady=5)
        
        # Buttons
        button_frame2 = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_CARD)
        button_frame2.grid(row=7, column=0, columnspan=2, pady=10)
        
        save_btn_frame, save_btn = ClaymorphismTheme.create_button(
            button_frame2, 
            text="Save",
            command=self.save_customer
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
        
        # Load customers
        self.load_customers()
        
        # Initially disable form
        self.toggle_form(False)
    
    def load_customers(self):
        """Load customers into the treeview"""
        # Clear existing items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        # Get customers from database
        customers = self.db.get_customers()
        
        # Add customers to treeview
        for customer in customers:
            self.customer_tree.insert("", "end", values=(
                customer["customer_id"],
                customer["name"],
                customer["place"],
                customer["phone"],
                customer["gst"]
            ))
    
    def search_customers(self, event=None):
        """Search customers based on search entry"""
        search_term = self.search_entry.get().lower()
        
        # Clear existing items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        # Get customers from database
        customers = self.db.get_customers()
        
        # Filter customers based on search term
        for customer in customers:
            if (search_term in customer["name"].lower() or 
                search_term in customer["place"].lower() or 
                search_term in customer["phone"].lower()):
                self.customer_tree.insert("", "end", values=(
                    customer["customer_id"],
                    customer["name"],
                    customer["place"],
                    customer["phone"],
                    customer["gst"]
                ))
    
    def on_customer_select(self, event):
        """Handle customer selection"""
        selected_items = self.customer_tree.selection()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        customer_id = self.customer_tree.item(selected_item, "values")[0]
        
        # Get customer details
        customers = self.db.get_customers()
        customer = next((c for c in customers if c["customer_id"] == int(customer_id)), None)
        
        if customer:
            # Populate form fields
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, customer["name"])
            
            self.place_entry.delete(0, "end")
            self.place_entry.insert(0, customer["place"] or "")
            
            self.phone_entry.delete(0, "end")
            self.phone_entry.insert(0, customer["phone"] or "")
            
            self.gst_entry.delete(0, "end")
            self.gst_entry.insert(0, customer["gst"] or "")
            
            self.address_text.delete(1.0, "end")
            self.address_text.insert(1.0, customer["address"] or "")
            
            self.email_entry.delete(0, "end")
            self.email_entry.insert(0, customer["email"] or "")
            
            # Get customer balance
            balance = self.db.get_customer_balance(customer["customer_id"])
            self.balance_label.config(text=f"₹{balance:.2f}")
            
            # Enable form
            self.toggle_form(True)
            self.current_customer_id = customer["customer_id"]
    
    def add_customer(self):
        """Add a new customer"""
        # Clear form
        self.clear_form()
        
        # Enable form
        self.toggle_form(True)
        
        # Set focus to name entry
        self.name_entry.focus()
        
        # Set mode to add
        self.mode = "add"
    
    def edit_customer(self):
        """Edit selected customer"""
        selected_items = self.customer_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a customer to edit.")
            return
        
        # Set mode to edit
        self.mode = "edit"
    
    def delete_customer(self):
        """Delete selected customer"""
        selected_items = self.customer_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a customer to delete.")
            return
        
        selected_item = selected_items[0]
        customer_id = self.customer_tree.item(selected_item, "values")[0]
        customer_name = self.customer_tree.item(selected_item, "values")[1]
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {customer_name}?"):
            # Delete customer
            success = self.db.delete_customer(int(customer_id))
            
            if success:
                messagebox.showinfo("Success", "Customer deleted successfully.")
                self.load_customers()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Cannot delete customer with existing invoices.")
    
    def save_customer(self):
        """Save customer data"""
        # Get form data
        name = self.name_entry.get().strip()
        place = self.place_entry.get().strip()
        phone = self.phone_entry.get().strip()
        gst = self.gst_entry.get().strip()
        address = self.address_text.get(1.0, "end").strip()
        email = self.email_entry.get().strip()
        
        # Validate form
        if not name:
            messagebox.showwarning("Validation Error", "Name is required.")
            return
        
        # Save customer
        if hasattr(self, 'mode') and self.mode == "add":
            # Add new customer
            customer_id = self.db.add_customer(name, place, phone, gst, address, email)
            
            if customer_id:
                messagebox.showinfo("Success", "Customer added successfully.")
                self.load_customers()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to add customer.")
        else:
            # Update existing customer
            success = self.db.update_customer(
                self.current_customer_id, name, place, phone, gst, address, email
            )
            
            if success:
                messagebox.showinfo("Success", "Customer updated successfully.")
                self.load_customers()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to update customer.")
    
    def clear_form(self):
        """Clear form fields"""
        self.name_entry.delete(0, "end")
        self.place_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.gst_entry.delete(0, "end")
        self.address_text.delete(1.0, "end")
        self.email_entry.delete(0, "end")
        self.balance_label.config(text="₹0.00")
        
        # Disable form
        self.toggle_form(False)
        
        # Clear selection
        for item in self.customer_tree.selection():
            self.customer_tree.selection_remove(item)
    
    def toggle_form(self, enabled):
        """Enable or disable form fields"""
        state = "normal" if enabled else "disabled"
        
        self.name_entry.config(state=state)
        self.place_entry.config(state=state)
        self.phone_entry.config(state=state)
        self.gst_entry.config(state=state)
        self.address_text.config(state=state)
        self.email_entry.config(state=state)
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3  # Add this import
from theme import ClaymorphismTheme

class VisitsModule:
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
            text="Customer Visits", 
            height=80
        )
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Content area
        content_frame = tk.Frame(main_container, bg=ClaymorphismTheme.BG_PRIMARY)
        content_frame.pack(fill="both", expand=True)
        
        # Left panel - Visit list
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
            command=self.search_visits
        )
        search_btn_frame.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Clear button
        clear_btn_frame, clear_btn = ClaymorphismTheme.create_button(
            search_card, 
            text="Clear",
            command=self.clear_search
        )
        clear_btn_frame.grid(row=1, column=2, columnspan=2, sticky="w", padx=10, pady=5)
        
        # New visit button
        new_btn_frame, new_btn = ClaymorphismTheme.create_button(
            search_card, 
            text="New Visit",
            command=self.new_visit
        )
        new_btn_frame.grid(row=1, column=4, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Visit list
        list_frame, list_card = ClaymorphismTheme.create_card(left_panel)
        list_frame.pack(fill="both", expand=True)
        
        # Treeview for visits
        self.visit_tree = ttk.Treeview(list_card, columns=("ID", "Date", "Name", "City", "Purpose"), show="headings")
        self.visit_tree.heading("ID", text="ID")
        self.visit_tree.heading("Date", text="Date")
        self.visit_tree.heading("Name", text="Name")
        self.visit_tree.heading("City", text="City")
        self.visit_tree.heading("Purpose", text="Purpose")
        
        self.visit_tree.column("ID", width=50)
        self.visit_tree.column("Date", width=100)
        self.visit_tree.column("Name", width=150)
        self.visit_tree.column("City", width=100)
        self.visit_tree.column("Purpose", width=150)
        
        self.visit_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.visit_tree.bind("<<TreeviewSelect>>", self.on_visit_select)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_card, orient="vertical", command=self.visit_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.visit_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = tk.Frame(left_panel, bg=ClaymorphismTheme.BG_PRIMARY)
        button_frame.pack(fill="x", pady=10)
        
        view_btn_frame, view_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="View Details",
            command=self.view_visit_details
        )
        view_btn_frame.pack(side="left", padx=5)
        
        edit_btn_frame, edit_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Edit Visit",
            command=self.edit_visit
        )
        edit_btn_frame.pack(side="left", padx=5)
        
        delete_btn_frame, delete_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Delete Visit",
            command=self.delete_visit
        )
        delete_btn_frame.pack(side="left", padx=5)
        
        refresh_btn_frame, refresh_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Refresh",
            command=self.load_visits
        )
        refresh_btn_frame.pack(side="left", padx=5)
        
        # Right panel - Visit details
        right_panel = tk.Frame(content_frame, bg=ClaymorphismTheme.BG_PRIMARY, width=400)
        right_panel.pack(side="right", fill="both")
        right_panel.pack_propagate(False)
        
        # Visit details card
        details_frame, details_card = ClaymorphismTheme.create_card(right_panel, text="Visit Details")
        details_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initially show a placeholder
        placeholder_label = tk.Label(details_card, text="Select a visit to view details", 
                                   bg=ClaymorphismTheme.BG_CARD, 
                                   font=ClaymorphismTheme.FONT_SUBTITLE,
                                   fg=ClaymorphismTheme.TEXT_SECONDARY)
        placeholder_label.pack(pady=50)
        
        self.details_content = placeholder_label
        
        # Load visits
        self.load_visits()
    
    def load_visits(self):
        """Load visits into the treeview"""
        # Clear existing items
        for item in self.visit_tree.get_children():
            self.visit_tree.delete(item)
        
        # Get visits from database
        visits = self.db.get_visits()
        
        # Add visits to treeview
        for visit in visits:
            self.visit_tree.insert("", "end", values=(
                visit["visit_id"],
                visit["date"].strftime("%Y-%m-%d"),
                visit["customer_name"],
                visit["city"] or "",
                visit["purpose"] or ""
            ))
    
    def search_visits(self):
        """Search visits based on criteria"""
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
        for item in self.visit_tree.get_children():
            self.visit_tree.delete(item)
        
        # Get visits from database
        visits = self.db.get_visits(from_date=from_date, to_date=to_date, customer=customer)
        
        # Add visits to treeview
        for visit in visits:
            self.visit_tree.insert("", "end", values=(
                visit["visit_id"],
                visit["date"].strftime("%Y-%m-%d"),
                visit["customer_name"],
                visit["city"] or "",
                visit["purpose"] or ""
            ))
    
    def clear_search(self):
        """Clear search fields"""
        self.customer_entry.delete(0, "end")
        self.from_date.delete(0, "end")
        self.to_date.delete(0, "end")
        self.load_visits()
    
    def on_visit_select(self, event):
        """Handle visit selection"""
        selected_items = self.visit_tree.selection()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        visit_id = self.visit_tree.item(selected_item, "values")[0]
        
        # Get visit details
        visits = self.db.get_visits()
        visit = next((v for v in visits if v["visit_id"] == int(visit_id)), None)
        
        if visit:
            self.display_visit_details(visit)
    
    def display_visit_details(self, visit):
        """Display visit details in the right panel"""
        # Clear existing content
        if self.details_content:
            self.details_content.destroy()
        
        # Create details frame
        details_frame = tk.Frame(self.parent, bg=ClaymorphismTheme.BG_CARD)
        self.details_content = details_frame
        
        # Visit header
        header_frame = tk.Frame(details_frame, bg=ClaymorphismTheme.BG_CARD)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Visit ID and date
        visit_id_label = tk.Label(header_frame, text=f"Visit ID: {visit['visit_id']}", 
                                 bg=ClaymorphismTheme.BG_CARD, 
                                 font=ClaymorphismTheme.FONT_SUBTITLE,
                                 fg=ClaymorphismTheme.TEXT_PRIMARY)
        visit_id_label.pack(side="left")
        
        visit_date_label = tk.Label(header_frame, text=f"Date: {visit['date'].strftime('%d-%m-%Y')}", 
                                   bg=ClaymorphismTheme.BG_CARD, 
                                   font=ClaymorphismTheme.FONT_NORMAL,
                                   fg=ClaymorphismTheme.TEXT_SECONDARY)
        visit_date_label.pack(side="right")
        
        # Customer details
        customer_frame = tk.Frame(details_frame, bg=ClaymorphismTheme.BG_CARD)
        customer_frame.pack(fill="x", padx=10, pady=5)
        
        cust_label = tk.Label(customer_frame, text="Customer:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_SUBTITLE,
                             fg=ClaymorphismTheme.TEXT_PRIMARY)
        cust_label.pack(anchor="w")
        
        cust_name_label = tk.Label(customer_frame, text=visit["customer_name"], 
                                  bg=ClaymorphismTheme.BG_CARD, 
                                  font=ClaymorphismTheme.FONT_NORMAL,
                                  fg=ClaymorphismTheme.TEXT_PRIMARY)
        cust_name_label.pack(anchor="w", padx=20)
        
        if visit["city"]:
            cust_city_label = tk.Label(customer_frame, text=visit["city"], 
                                      bg=ClaymorphismTheme.BG_CARD, 
                                      font=ClaymorphismTheme.FONT_NORMAL,
                                      fg=ClaymorphismTheme.TEXT_SECONDARY)
            cust_city_label.pack(anchor="w", padx=20)
        
        # Visit purpose
        purpose_frame = tk.Frame(details_frame, bg=ClaymorphismTheme.BG_CARD)
        purpose_frame.pack(fill="x", padx=10, pady=5)
        
        purpose_label = tk.Label(purpose_frame, text="Purpose of Visit:", bg=ClaymorphismTheme.BG_CARD, 
                                font=ClaymorphismTheme.FONT_SUBTITLE,
                                fg=ClaymorphismTheme.TEXT_PRIMARY)
        purpose_label.pack(anchor="w")
        
        purpose_text = tk.Label(purpose_frame, text=visit["purpose"] or "Not specified", 
                               bg=ClaymorphismTheme.BG_CARD, 
                               font=ClaymorphismTheme.FONT_NORMAL,
                               fg=ClaymorphismTheme.TEXT_PRIMARY,
                               wraplength=350,
                               justify="left")
        purpose_text.pack(anchor="w", padx=20)
        
        # Store current visit
        self.current_visit = visit
    
    def new_visit(self):
        """Open dialog to create a new visit"""
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("New Customer Visit")
        dialog.geometry("500x400")
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
        
        # Customer selection
        customer_label = tk.Label(form_frame, text="Customer:", bg=ClaymorphismTheme.BG_PRIMARY, 
                                 font=ClaymorphismTheme.FONT_NORMAL)
        customer_label.grid(row=0, column=0, sticky="w", pady=5)
        
        customer_combo_frame, customer_combo = ClaymorphismTheme.create_combobox(form_frame, width=30)
        customer_combo_frame.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Get customers and populate combobox
        customers = self.db.get_customers()
        customer_names = [f"{c['customer_id']} - {c['name']}" for c in customers]
        customer_combo['values'] = customer_names
        
        # Name (for new customers)
        name_label = tk.Label(form_frame, text="or Name:", bg=ClaymorphismTheme.BG_PRIMARY, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        name_label.grid(row=1, column=0, sticky="w", pady=5)
        
        name_entry_frame, name_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        name_entry_frame.grid(row=1, column=1, sticky="ew", pady=5)
        
        # City
        city_label = tk.Label(form_frame, text="City:", bg=ClaymorphismTheme.BG_PRIMARY, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        city_label.grid(row=2, column=0, sticky="w", pady=5)
        
        city_entry_frame, city_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        city_entry_frame.grid(row=2, column=1, sticky="ew", pady=5)
        
        # Date
        date_label = tk.Label(form_frame, text="Date:", bg=ClaymorphismTheme.BG_PRIMARY, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        date_label.grid(row=3, column=0, sticky="w", pady=5)
        
        date_entry_frame, date_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        date_entry_frame.grid(row=3, column=1, sticky="ew", pady=5)
        
        # Set today's date
        today = datetime.now().strftime("%Y-%m-%d")
        date_entry.insert(0, today)
        
        # Purpose
        purpose_label = tk.Label(form_frame, text="Purpose:", bg=ClaymorphismTheme.BG_PRIMARY, 
                               font=ClaymorphismTheme.FONT_NORMAL)
        purpose_label.grid(row=4, column=0, sticky="nw", pady=5)
        
        purpose_text = tk.Text(form_frame, height=4, width=30, 
                             bg=ClaymorphismTheme.BG_SECONDARY,
                             fg=ClaymorphismTheme.TEXT_PRIMARY,
                             relief="flat",
                             borderwidth=0,
                             font=ClaymorphismTheme.FONT_NORMAL)
        purpose_text.grid(row=4, column=1, sticky="ew", pady=5)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        save_btn_frame, save_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Save Visit",
            command=lambda: self.save_visit(
                dialog, customer_combo, name_entry, city_entry, date_entry, purpose_text, customers
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
    
    def save_visit(self, dialog, customer_combo, name_entry, city_entry, date_entry, purpose_text, customers):
        """Save visit to database"""
        # Get form data
        customer_str = customer_combo.get()
        name = name_entry.get().strip()
        city = city_entry.get().strip()
        date_str = date_entry.get().strip()
        purpose = purpose_text.get(1.0, "end").strip()
        
        # Validate form
        if not customer_str and not name:
            messagebox.showwarning("Validation Error", "Please select a customer or enter a name.")
            return
        
        if not date_str:
            messagebox.showwarning("Validation Error", "Date is required.")
            return
        
        try:
            visit_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter a valid date in YYYY-MM-DD format.")
            return
        
        # Get customer ID if selected
        customer_id = None
        if customer_str:
            customer_id = int(customer_str.split(" - ")[0])
        
        # Add visit to database
        visit_id = self.db.add_visit(customer_id, name, city, purpose, visit_date)
        
        if visit_id:
            messagebox.showinfo("Success", "Visit added successfully.")
            dialog.destroy()
            self.load_visits()
        else:
            messagebox.showerror("Error", "Failed to add visit.")
    
    def view_visit_details(self):
        """View selected visit details"""
        selected_items = self.visit_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a visit to view.")
            return
        
        # Get visit details
        selected_item = selected_items[0]
        visit_id = self.visit_tree.item(selected_item, "values")[0]
        
        visits = self.db.get_visits()
        visit = next((v for v in visits if v["visit_id"] == int(visit_id)), None)
        
        if visit:
            self.display_visit_details(visit)
    
    def edit_visit(self):
        """Edit selected visit"""
        selected_items = self.visit_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a visit to edit.")
            return
        
        # Get visit details
        selected_item = selected_items[0]
        visit_id = self.visit_tree.item(selected_item, "values")[0]
        
        visits = self.db.get_visits()
        visit = next((v for v in visits if v["visit_id"] == int(visit_id)), None)
        
        if not visit:
            return
        
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Customer Visit")
        dialog.geometry("500x400")
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
        
        # Customer selection
        customer_label = tk.Label(form_frame, text="Customer:", bg=ClaymorphismTheme.BG_PRIMARY, 
                                 font=ClaymorphismTheme.FONT_NORMAL)
        customer_label.grid(row=0, column=0, sticky="w", pady=5)
        
        customer_combo_frame, customer_combo = ClaymorphismTheme.create_combobox(form_frame, width=30)
        customer_combo_frame.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Get customers and populate combobox
        customers = self.db.get_customers()
        customer_names = [f"{c['customer_id']} - {c['name']}" for c in customers]
        customer_combo['values'] = customer_names
        
        # Set current customer if available
        if visit["customer_id"]:
            customer = next((c for c in customers if c["customer_id"] == visit["customer_id"]), None)
            if customer:
                customer_combo.set(f"{customer['customer_id']} - {customer['name']}")
        
        # Name
        name_label = tk.Label(form_frame, text="Name:", bg=ClaymorphismTheme.BG_PRIMARY, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        name_label.grid(row=1, column=0, sticky="w", pady=5)
        
        name_entry_frame, name_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        name_entry_frame.grid(row=1, column=1, sticky="ew", pady=5)
        name_entry.insert(0, visit["name"])
        
        # City
        city_label = tk.Label(form_frame, text="City:", bg=ClaymorphismTheme.BG_PRIMARY, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        city_label.grid(row=2, column=0, sticky="w", pady=5)
        
        city_entry_frame, city_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        city_entry_frame.grid(row=2, column=1, sticky="ew", pady=5)
        city_entry.insert(0, visit["city"] or "")
        
        # Date
        date_label = tk.Label(form_frame, text="Date:", bg=ClaymorphismTheme.BG_PRIMARY, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        date_label.grid(row=3, column=0, sticky="w", pady=5)
        
        date_entry_frame, date_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        date_entry_frame.grid(row=3, column=1, sticky="ew", pady=5)
        date_entry.insert(0, visit["date"].strftime("%Y-%m-%d"))
        
        # Purpose
        purpose_label = tk.Label(form_frame, text="Purpose:", bg=ClaymorphismTheme.BG_PRIMARY, 
                               font=ClaymorphismTheme.FONT_NORMAL)
        purpose_label.grid(row=4, column=0, sticky="nw", pady=5)
        
        purpose_text = tk.Text(form_frame, height=4, width=30, 
                             bg=ClaymorphismTheme.BG_SECONDARY,
                             fg=ClaymorphismTheme.TEXT_PRIMARY,
                             relief="flat",
                             borderwidth=0,
                             font=ClaymorphismTheme.FONT_NORMAL)
        purpose_text.grid(row=4, column=1, sticky="ew", pady=5)
        purpose_text.insert(1.0, visit["purpose"] or "")
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        save_btn_frame, save_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Save Changes",
            command=lambda: self.update_visit(
                dialog, visit_id, customer_combo, name_entry, city_entry, date_entry, purpose_text, customers
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
    
    def update_visit(self, dialog, visit_id, customer_combo, name_entry, city_entry, date_entry, purpose_text, customers):
        """Update visit in database"""
        # Get form data
        customer_str = customer_combo.get()
        name = name_entry.get().strip()
        city = city_entry.get().strip()
        date_str = date_entry.get().strip()
        purpose = purpose_text.get(1.0, "end").strip()
        
        # Validate form
        if not customer_str and not name:
            messagebox.showwarning("Validation Error", "Please select a customer or enter a name.")
            return
        
        if not date_str:
            messagebox.showwarning("Validation Error", "Date is required.")
            return
        
        try:
            visit_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter a valid date in YYYY-MM-DD format.")
            return
        
        # Get customer ID if selected
        customer_id = None
        if customer_str:
            customer_id = int(customer_str.split(" - ")[0])
        
        # Update visit in database
        try:
            conn = sqlite3.connect(self.db.db_name)
            cursor = conn.cursor()
            
            query = """
            UPDATE customer_visits
            SET customer_id = ?, name = ?, city = ?, purpose = ?, date = ?
            WHERE visit_id = ?
            """
            
            cursor.execute(query, (customer_id, name, city, purpose, visit_date.strftime("%Y-%m-%d"), visit_id))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Visit updated successfully.")
            dialog.destroy()
            self.load_visits()
        except Exception as e:
            print(f"Error updating visit: {e}")
            messagebox.showerror("Error", "Failed to update visit.")
    
    def delete_visit(self):
        """Delete selected visit"""
        selected_items = self.visit_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a visit to delete.")
            return
        
        selected_item = selected_items[0]
        visit_id = self.visit_tree.item(selected_item, "values")[0]
        visit_name = self.visit_tree.item(selected_item, "values")[2]
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the visit by {visit_name}?"):
            # Delete visit
            success = self.db.delete_visit(int(visit_id))
            
            if success:
                messagebox.showinfo("Success", "Visit deleted successfully.")
                self.load_visits()
                
                # Clear details if this visit was being viewed
                if hasattr(self, 'current_visit') and self.current_visit["visit_id"] == int(visit_id):
                    if self.details_content:
                        self.details_content.destroy()
                    
                    placeholder_label = tk.Label(self.parent, text="Select a visit to view details", 
                                               bg=ClaymorphismTheme.BG_CARD, 
                                               font=ClaymorphismTheme.FONT_SUBTITLE,
                                               fg=ClaymorphismTheme.TEXT_SECONDARY)
                    placeholder_label.pack(pady=50)
                    self.details_content = placeholder_label
            else:
                messagebox.showerror("Error", "Failed to delete visit.")
    
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
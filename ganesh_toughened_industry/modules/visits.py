import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from ui_theme import ClaymorphismTheme

class VisitsModule:
    def __init__(self, parent, db, app):
        self.parent = parent
        self.db = db
        self.app = app
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """Create the customer visits UI with claymorphism style"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = ClaymorphismTheme.create_label(
            main_frame, 
            text="CUSTOMER VISITS LOG", 
            style="Title.TLabel"
        )
        title.pack(pady=(0, 20))
        
        # Filter card
        filter_card = ClaymorphismTheme.create_card(main_frame, padding=15)
        filter_card.pack(fill=tk.X, pady=(0, 15))
        
        # Filter frame
        filter_frame = ttk.Frame(filter_card)
        filter_frame.pack(fill=tk.X)
        
        # Date range
        ClaymorphismTheme.create_label(filter_frame, text="From:").pack(side=tk.LEFT, padx=(0, 10))
        self.from_date_var = tk.StringVar(value=(date.today() - timedelta(days=7)).strftime("%d/%m/%Y"))
        from_date_entry = ClaymorphismTheme.create_entry(filter_frame, textvariable=self.from_date_var, width=10)
        from_date_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        ClaymorphismTheme.create_label(filter_frame, text="To:").pack(side=tk.LEFT, padx=(0, 10))
        self.to_date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        to_date_entry = ClaymorphismTheme.create_entry(filter_frame, textvariable=self.to_date_var, width=10)
        to_date_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        # Customer filter
        ClaymorphismTheme.create_label(filter_frame, text="Customer:").pack(side=tk.LEFT, padx=(0, 10))
        self.customer_var = tk.StringVar()
        self.customer_combo = ClaymorphismTheme.create_combobox(filter_frame, textvariable=self.customer_var)
        self.customer_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        # Search button
        search_btn = ClaymorphismTheme.create_button(
            filter_frame, 
            text="Search", 
            command=self.search_visits
        )
        search_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add visit button
        add_btn = ClaymorphismTheme.create_button(
            filter_frame, 
            text="Add Visit", 
            command=self.add_visit,
            style="Success.TButton"
        )
        add_btn.pack(side=tk.LEFT)
        
        # Visits display
        visits_frame = ttk.Frame(main_frame)
        visits_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for visits and summary
        notebook = ClaymorphismTheme.create_notebook(visits_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Visits tab
        visits_tab = ttk.Frame(notebook)
        notebook.add(visits_tab, text="Visits")
        
        # Summary tab
        summary_tab = ttk.Frame(notebook)
        notebook.add(summary_tab, text="Summary")
        
        # Create visits UI
        self.create_visits_ui(visits_tab)
        
        # Create summary UI
        self.create_summary_ui(summary_tab)
        
        # Load customers
        self.load_customers()
        
        # Load initial visits
        self.search_visits()
    
    def create_visits_ui(self, parent):
        """Create the visits UI with claymorphism style"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Visits card
        visits_card = ClaymorphismTheme.create_card(main_frame, padding=15)
        visits_card.pack(fill=tk.BOTH, expand=True)
        
        # Visits treeview
        self.visits_tree, scrollbar = ClaymorphismTheme.create_treeview(
            visits_card, 
            columns=("date", "name", "city", "purpose")
        )
        self.visits_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Define headings
        self.visits_tree.heading("date", text="Date")
        self.visits_tree.heading("name", text="Name")
        self.visits_tree.heading("city", text="City")
        self.visits_tree.heading("purpose", text="Purpose")
        
        # Define columns
        self.visits_tree.column("date", width=150)
        self.visits_tree.column("name", width=150)
        self.visits_tree.column("city", width=100)
        self.visits_tree.column("purpose", width=200)
        
        # Bind double-click to view details
        self.visits_tree.bind("<Double-1>", self.view_visit_details)
    
    def create_summary_ui(self, parent):
        """Create the summary UI with claymorphism style"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Summary card
        summary_card = ClaymorphismTheme.create_card(main_frame, padding=15)
        summary_card.pack(fill=tk.BOTH, expand=True)
        
        # Summary treeview
        self.summary_tree, scrollbar = ClaymorphismTheme.create_treeview(
            summary_card, 
            columns=("date", "visits_count")
        )
        self.summary_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Define headings
        self.summary_tree.heading("date", text="Date")
        self.summary_tree.heading("visits_count", text="Visits Count")
        
        # Define columns
        self.summary_tree.column("date", width=150)
        self.summary_tree.column("visits_count", width=150)
    
    def load_customers(self):
        """Load customers into combobox"""
        customers = self.db.get_customers()
        customer_names = [customer["name"] for customer in customers]
        self.customer_combo["values"] = customer_names
    
    def search_visits(self):
        """Search visits based on filters"""
        # Clear existing items
        for item in self.visits_tree.get_children():
            self.visits_tree.delete(item)
        
        for item in self.summary_tree.get_children():
            self.summary_tree.delete(item)
        
        # Get filter values
        customer_name = self.customer_var.get()
        from_date_str = self.from_date_var.get()
        to_date_str = self.to_date_var.get()
        
        # Get customer ID if selected
        customer_id = None
        if customer_name:
            customers = self.db.get_customers()
            for customer in customers:
                if customer["name"] == customer_name:
                    customer_id = customer["customer_id"]
                    break
        
        # Parse dates
        try:
            from_day, from_month, from_year = from_date_str.split('/')
            from_date = date(int(from_year), int(from_month), int(from_day))
            
            to_day, to_month, to_year = to_date_str.split('/')
            to_date = date(int(to_year), int(to_month), int(to_day))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dates in DD/MM/YYYY format")
            return
        
        # Get visits
        try:
            visits = self.db.get_visits(from_date, to_date, customer_id)
            
            # Group visits by date for summary
            daily_visits = {}
            
            for visit in visits:
                # Format date for display
                visit_date_str = visit["date"].strftime("%d/%m/%Y")
                
                # Add to visits tree
                self.visits_tree.insert("", "end", values=(
                    visit_date_str,
                    visit["name"] or visit["customer_name"] or "Unknown",
                    visit["city"] or "",
                    visit["purpose"] or ""
                ))
                
                # Add to daily summary
                date_key = visit["date"].strftime("%Y-%m-%d")
                if date_key not in daily_visits:
                    daily_visits[date_key] = 0
                daily_visits[date_key] += 1
            
            # Add to summary tree
            for date_key, count in daily_visits.items():
                # Format date
                date_obj = datetime.strptime(date_key, "%Y-%m-%d").date()
                formatted_date = date_obj.strftime("%d %b %Y")
                
                self.summary_tree.insert("", "end", values=(
                    formatted_date,
                    count
                ))
            
        except Exception as e:
            print(f"Error searching visits: {e}")
    
    def add_visit(self):
        """Add a new visit"""
        # Create visit dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Visit")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Apply theme to dialog
        ClaymorphismTheme.setup_theme(dialog)
        
        # Visit details card
        details_card = ClaymorphismTheme.create_card(dialog, padding=20)
        details_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Visit details
        ClaymorphismTheme.create_label(details_card, text="Customer:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        customer_var = tk.StringVar()
        customer_combo = ClaymorphismTheme.create_combobox(details_card, textvariable=customer_var)
        customer_combo.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)
        
        # Load customers
        customers = self.db.get_customers()
        customer_names = [customer["name"] for customer in customers]
        customer_combo["values"] = customer_names
        
        # New customer option
        new_customer_var = tk.StringVar()
        new_customer_check = ttk.Checkbutton(
            details_card, 
            text="New Customer", 
            variable=new_customer_var,
            command=lambda: self.toggle_customer_field(customer_combo, new_customer_var.get())
        )
        new_customer_check.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)
        
        ClaymorphismTheme.create_label(details_card, text="Name:", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        name_var = tk.StringVar()
        name_entry = ClaymorphismTheme.create_entry(details_card, textvariable=name_var)
        name_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.EW)
        name_entry.configure(state="disabled")
        
        ClaymorphismTheme.create_label(details_card, text="City:", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        city_var = tk.StringVar()
        city_entry = ClaymorphismTheme.create_entry(details_card, textvariable=city_var)
        city_entry.grid(row=3, column=1, padx=10, pady=10, sticky=tk.EW)
        
        ClaymorphismTheme.create_label(details_card, text="Date:", font=("Segoe UI", 10, "bold")).grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        date_entry = ClaymorphismTheme.create_entry(details_card, textvariable=date_var)
        date_entry.grid(row=4, column=1, padx=10, pady=10, sticky=tk.EW)
        
        ClaymorphismTheme.create_label(details_card, text="Purpose:", font=("Segoe UI", 10, "bold")).grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        purpose_var = tk.StringVar()
        purpose_entry = ClaymorphismTheme.create_entry(details_card, textvariable=purpose_var)
        purpose_entry.grid(row=5, column=1, padx=10, pady=10, sticky=tk.EW)
        
        # Buttons card
        button_card = ClaymorphismTheme.create_card(dialog, padding=15)
        button_card.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(button_card)
        button_frame.pack(fill=tk.X)
        
        def save_visit():
            try:
                # Get customer
                customer_id = None
                customer_name = None
                
                if new_customer_var.get():
                    # New customer
                    customer_name = name_var.get().strip()
                    if not customer_name:
                        messagebox.showerror("Error", "Customer name is required")
                        return
                else:
                    # Existing customer
                    customer_name = customer_var.get()
                    if not customer_name:
                        messagebox.showerror("Error", "Please select a customer")
                        return
                    
                    # Get customer ID
                    for customer in customers:
                        if customer["name"] == customer_name:
                            customer_id = customer["customer_id"]
                            break
                    
                    if not customer_id:
                        messagebox.showerror("Error", "Customer not found")
                        return
                
                # Parse date
                date_str = date_var.get()
                day, month, year = date_str.split('/')
                visit_date = date(int(year), int(month), int(day))
                
                # Get city
                city = city_var.get().strip()
                
                # Get purpose
                purpose = purpose_var.get().strip()
                
                # Add visit
                visit_id = self.db.add_visit(
                    customer_id=customer_id,
                    name=customer_name,
                    city=city,
                    purpose=purpose,
                    date_time=visit_date
                )
                
                if visit_id:
                    messagebox.showinfo("Success", "Visit added successfully")
                    dialog.destroy()
                    # Refresh visits
                    self.search_visits()
                else:
                    messagebox.showerror("Error", "Could not add visit")
                    
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid date format: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not add visit: {e}")
        
        save_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Save", 
            command=save_visit,
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
    
    def toggle_customer_field(self, combo, is_new):
        """Toggle customer field state"""
        if is_new:
            combo.config(state="disabled")
            combo.set("")
        else:
            combo.config(state="readonly")
    
    def view_visit_details(self, event=None):
        """View visit details"""
        selected = self.visits_tree.selection()
        if not selected:
            return
        
        # Get visit details
        item = self.visits_tree.item(selected[0])
        date_str = item["values"][0]
        name = item["values"][1]
        city = item["values"][2]
        purpose = item["values"][3]
        
        # Create visit details dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Visit Details")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Apply theme to dialog
        ClaymorphismTheme.setup_theme(dialog)
        
        # Visit details card
        details_card = ClaymorphismTheme.create_card(dialog, text="Visit Details", padding=20)
        details_card.pack(fill=tk.X, padx=20, pady=20)
        
        # Date
        date_frame = ttk.Frame(details_card)
        date_frame.pack(fill=tk.X, pady=5)
        ClaymorphismTheme.create_label(date_frame, text="Date:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        ClaymorphismTheme.create_label(date_frame, text=date_str).pack(side=tk.LEFT)
        
        # Name
        name_frame = ttk.Frame(details_card)
        name_frame.pack(fill=tk.X, pady=5)
        ClaymorphismTheme.create_label(name_frame, text="Name:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        ClaymorphismTheme.create_label(name_frame, text=name).pack(side=tk.LEFT)
        
        # City
        city_frame = ttk.Frame(details_card)
        city_frame.pack(fill=tk.X, pady=5)
        ClaymorphismTheme.create_label(city_frame, text="City:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        ClaymorphismTheme.create_label(city_frame, text=city or "").pack(side=tk.LEFT)
        
        # Purpose
        purpose_frame = ttk.Frame(details_card)
        purpose_frame.pack(fill=tk.X, pady=5)
        ClaymorphismTheme.create_label(purpose_frame, text="Purpose:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        ClaymorphismTheme.create_label(purpose_frame, text=purpose or "").pack(side=tk.LEFT)
        
        # Action buttons card
        action_card = ClaymorphismTheme.create_card(dialog, padding=15)
        action_card.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Action buttons
        action_frame = ttk.Frame(action_card)
        action_frame.pack(fill=tk.X)
        
        # Close button
        close_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Close", 
            command=dialog.destroy
        )
        close_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
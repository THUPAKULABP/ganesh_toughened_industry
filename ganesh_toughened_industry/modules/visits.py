import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta

class VisitsModule:
    def __init__(self, parent, db, app):
        self.parent = parent
        self.db = db
        self.app = app
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """Create the customer visits UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="CUSTOMER VISITS LOG", style="Title.TLabel")
        title.pack(pady=10)
        
        # Filter frame
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Date range
        ttk.Label(filter_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.from_date_var = tk.StringVar(value=(date.today() - timedelta(days=7)).strftime("%d/%m/%Y"))
        ttk.Entry(filter_frame, textvariable=self.from_date_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.to_date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(filter_frame, textvariable=self.to_date_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Customer filter
        ttk.Label(filter_frame, text="Customer:").pack(side=tk.LEFT, padx=5)
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(filter_frame, textvariable=self.customer_var)
        self.customer_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Search button
        search_btn = ttk.Button(filter_frame, text="Search", command=self.search_visits)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Add visit button
        add_btn = ttk.Button(filter_frame, text="Add Visit", command=self.add_visit)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Visits display
        visits_frame = ttk.Frame(main_frame)
        visits_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create notebook for visits and summary
        notebook = ttk.Notebook(visits_frame)
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
        """Create the visits UI"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Visits treeview
        self.visits_tree = ttk.Treeview(main_frame, columns=("date", "name", "city", "purpose"), show="headings")
        self.visits_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
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
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.visits_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.visits_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click to view details
        self.visits_tree.bind("<Double-1>", self.view_visit_details)
    
    def create_summary_ui(self, parent):
        """Create the summary UI"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Summary treeview
        self.summary_tree = ttk.Treeview(main_frame, columns=("date", "visits_count"), show="headings")
        self.summary_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        self.summary_tree.heading("date", text="Date")
        self.summary_tree.heading("visits_count", text="Visits Count")
        
        # Define columns
        self.summary_tree.column("date", width=150)
        self.summary_tree.column("visits_count", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.summary_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.summary_tree.configure(yscrollcommand=scrollbar.set)
    
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
        
        # Visit details
        ttk.Label(dialog, text="Customer:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        customer_var = tk.StringVar()
        customer_combo = ttk.Combobox(dialog, textvariable=customer_var)
        customer_combo.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Load customers
        customers = self.db.get_customers()
        customer_names = [customer["name"] for customer in customers]
        customer_combo["values"] = customer_names
        
        # New customer option
        new_customer_var = tk.StringVar()
        new_customer_check = ttk.Checkbutton(dialog, text="New Customer", variable=new_customer_var,
                                           command=lambda: self.toggle_customer_field(customer_combo, new_customer_var.get()))
        new_customer_check.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Name:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, state="disabled")
        name_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="City:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        city_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=city_var).grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Date:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(dialog, textvariable=date_var).grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Purpose:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        purpose_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=purpose_var).grid(row=5, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=10)
        
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
        
        ttk.Button(button_frame, text="Save", command=save_visit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
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
        
        # Visit details
        details_frame = ttk.LabelFrame(dialog, text="Visit Details")
        details_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Date
        date_frame = ttk.Frame(details_frame)
        date_frame.pack(fill=tk.X, padx=5, pady=2)
        date_label = ttk.Label(date_frame, text="Date:", width=15)
        date_label.pack(side=tk.LEFT, padx=5)
        ttk.Label(date_frame, text=date_str).pack(side=tk.LEFT)
        
        # Name
        name_frame = ttk.Frame(details_frame)
        name_frame.pack(fill=tk.X, padx=5, pady=2)
        name_label = ttk.Label(name_frame, text="Name:", width=15)
        name_label.pack(side=tk.LEFT, padx=5)
        ttk.Label(name_frame, text=name).pack(side=tk.LEFT)
        
        # City
        city_frame = ttk.Frame(details_frame)
        city_frame.pack(fill=tk.X, padx=5, pady=2)
        city_label = ttk.Label(city_frame, text="City:", width=15)
        city_label.pack(side=tk.LEFT, padx=5)
        ttk.Label(city_frame, text=city or "").pack(side=tk.LEFT)
        
        # Purpose
        purpose_frame = ttk.Frame(details_frame)
        purpose_frame.pack(fill=tk.X, padx=5, pady=2)
        purpose_label = ttk.Label(purpose_frame, text="Purpose:", width=15)
        purpose_label.pack(side=tk.LEFT, padx=5)
        ttk.Label(purpose_frame, text=purpose or "").pack(side=tk.LEFT)
        
        # Action buttons
        action_frame = ttk.Frame(dialog)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Close button
        close_btn = ttk.Button(action_frame, text="Close", command=dialog.destroy)
        close_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
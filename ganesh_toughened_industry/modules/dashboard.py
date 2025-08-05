import tkinter as tk
from tkinter import ttk
from datetime import datetime, date, timedelta  # Add timedelta import
from theme import ClaymorphismTheme

class DashboardModule:
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
            text="Dashboard", 
            height=80
        )
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Content area
        content_frame = tk.Frame(main_container, bg=ClaymorphismTheme.BG_PRIMARY)
        content_frame.pack(fill="both", expand=True)
        
        # Stats cards
        stats_frame = tk.Frame(content_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Today's sales card
        sales_frame, sales_card = ClaymorphismTheme.create_card(stats_frame, height=150, width=250)
        sales_frame.pack(side="left", padx=10)
        
        sales_title = tk.Label(sales_card, text="Today's Sales", 
                              bg=ClaymorphismTheme.BG_CARD, 
                              font=ClaymorphismTheme.FONT_NORMAL,
                              fg=ClaymorphismTheme.TEXT_SECONDARY)
        sales_title.pack(pady=(10, 5))
        
        self.sales_amount = tk.Label(sales_card, text="₹0.00", 
                                    bg=ClaymorphismTheme.BG_CARD, 
                                    font=ClaymorphismTheme.FONT_TITLE,
                                    fg=ClaymorphismTheme.TEXT_PRIMARY)
        self.sales_amount.pack()
        
        # Monthly sales card
        monthly_frame, monthly_card = ClaymorphismTheme.create_card(stats_frame, height=150, width=250)
        monthly_frame.pack(side="left", padx=10)
        
        monthly_title = tk.Label(monthly_card, text="Monthly Sales", 
                                bg=ClaymorphismTheme.BG_CARD, 
                                font=ClaymorphismTheme.FONT_NORMAL,
                                fg=ClaymorphismTheme.TEXT_SECONDARY)
        monthly_title.pack(pady=(10, 5))
        
        self.monthly_amount = tk.Label(monthly_card, text="₹0.00", 
                                      bg=ClaymorphismTheme.BG_CARD, 
                                      font=ClaymorphismTheme.FONT_TITLE,
                                      fg=ClaymorphismTheme.TEXT_PRIMARY)
        self.monthly_amount.pack()
        
        # Customers card
        customers_frame, customers_card = ClaymorphismTheme.create_card(stats_frame, height=150, width=250)
        customers_frame.pack(side="left", padx=10)
        
        customers_title = tk.Label(customers_card, text="Total Customers", 
                                  bg=ClaymorphismTheme.BG_CARD, 
                                  font=ClaymorphismTheme.FONT_NORMAL,
                                  fg=ClaymorphismTheme.TEXT_SECONDARY)
        customers_title.pack(pady=(10, 5))
        
        self.customers_count = tk.Label(customers_card, text="0", 
                                       bg=ClaymorphismTheme.BG_CARD, 
                                       font=ClaymorphismTheme.FONT_TITLE,
                                       fg=ClaymorphismTheme.TEXT_PRIMARY)
        self.customers_count.pack()
        
        # Products card
        products_frame, products_card = ClaymorphismTheme.create_card(stats_frame, height=150, width=250)
        products_frame.pack(side="left", padx=10)
        
        products_title = tk.Label(products_card, text="Total Products", 
                                bg=ClaymorphismTheme.BG_CARD, 
                                font=ClaymorphismTheme.FONT_NORMAL,
                                fg=ClaymorphismTheme.TEXT_SECONDARY)
        products_title.pack(pady=(10, 5))
        
        self.products_count = tk.Label(products_card, text="0", 
                                     bg=ClaymorphismTheme.BG_CARD, 
                                     font=ClaymorphismTheme.FONT_TITLE,
                                     fg=ClaymorphismTheme.TEXT_PRIMARY)
        self.products_count.pack()
        
        # Recent activities
        activities_frame, activities_card = ClaymorphismTheme.create_card(content_frame, text="Recent Activities")
        activities_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create notebook for different activity types
        notebook = ttk.Notebook(activities_card)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Recent invoices tab
        invoices_tab = tk.Frame(notebook, bg=ClaymorphismTheme.BG_CARD)
        notebook.add(invoices_tab, text="Recent Invoices")
        
        # Create treeview for recent invoices
        invoices_tree = ttk.Treeview(invoices_tab, columns=("ID", "Number", "Date", "Customer", "Amount"), show="headings")
        invoices_tree.heading("ID", text="ID")
        invoices_tree.heading("Number", text="Invoice #")
        invoices_tree.heading("Date", text="Date")
        invoices_tree.heading("Customer", text="Customer")
        invoices_tree.heading("Amount", text="Amount")
        
        invoices_tree.column("ID", width=50)
        invoices_tree.column("Number", width=120)
        invoices_tree.column("Date", width=100)
        invoices_tree.column("Customer", width=150)
        invoices_tree.column("Amount", width=100)
        
        invoices_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Recent visits tab
        visits_tab = tk.Frame(notebook, bg=ClaymorphismTheme.BG_CARD)
        notebook.add(visits_tab, text="Recent Visits")
        
        # Create treeview for recent visits
        visits_tree = ttk.Treeview(visits_tab, columns=("ID", "Date", "Name", "City"), show="headings")
        visits_tree.heading("ID", text="ID")
        visits_tree.heading("Date", text="Date")
        visits_tree.heading("Name", text="Name")
        visits_tree.heading("City", text="City")
        
        visits_tree.column("ID", width=50)
        visits_tree.column("Date", width=100)
        visits_tree.column("Name", width=150)
        visits_tree.column("City", width=100)
        
        visits_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Load dashboard data
        self.load_dashboard_data(invoices_tree, visits_tree)
    
    def load_dashboard_data(self, invoices_tree, visits_tree):
        """Load dashboard data"""
        # Get today's date
        today = date.today()
        
        # Calculate today's sales
        today_invoices = self.db.search_invoices(
            from_date=today.strftime("%Y-%m-%d"),
            to_date=today.strftime("%Y-%m-%d")
        )
        
        today_sales = sum(invoice["total"] for invoice in today_invoices)
        self.sales_amount.config(text=f"₹{today_sales:.2f}")
        
        # Calculate monthly sales
        current_month = today.month
        current_year = today.year
        
        # Get first day of current month
        first_day = date(current_year, current_month, 1)
        
        # Get last day of current month
        if current_month == 12:
            last_day = date(current_year + 1, 1, 1) - timedelta(days=1)  # Fixed: Use timedelta directly
        else:
            last_day = date(current_year, current_month + 1, 1) - timedelta(days=1)  # Fixed: Use timedelta directly
        
        monthly_invoices = self.db.search_invoices(
            from_date=first_day.strftime("%Y-%m-%d"),
            to_date=last_day.strftime("%Y-%m-%d")
        )
        
        monthly_sales = sum(invoice["total"] for invoice in monthly_invoices)
        self.monthly_amount.config(text=f"₹{monthly_sales:.2f}")
        
        # Get customer count
        customers = self.db.get_customers()
        self.customers_count.config(text=str(len(customers)))
        
        # Get product count
        products = self.db.get_products()
        self.products_count.config(text=str(len(products)))
        
        # Load recent invoices
        for invoice in today_invoices[:5]:  # Show only 5 most recent
            invoices_tree.insert("", "end", values=(
                invoice["invoice_id"],
                invoice["invoice_number"],
                invoice["date"].strftime("%Y-%m-%d"),
                invoice["customer_name"],
                f"₹{invoice['total']:.2f}"
            ))
        
        # Load recent visits
        visits = self.db.get_visits()
        today_visits = [visit for visit in visits if visit["date"] == today]
        
        for visit in today_visits[:5]:  # Show only 5 most recent
            visits_tree.insert("", "end", values=(
                visit["visit_id"],
                visit["date"].strftime("%Y-%m-%d"),
                visit["customer_name"],
                visit["city"] or ""
            ))

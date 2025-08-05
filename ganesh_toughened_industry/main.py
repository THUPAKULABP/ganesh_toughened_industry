import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime, date
from database import Database
from ui_theme import ClaymorphismTheme
from modules.attendance import AttendanceModule
from modules.visits import VisitsModule
from modules.billing import BillingModule
from modules.customers import CustomersModule
from modules.products import ProductsModule
from modules.inventory import InventoryModule
from modules.expenses import ExpensesModule
from modules.reports import ReportsModule
from modules.settings import SettingsModule

class ModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GANESH TOUGHENED INDUSTRY")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Apply claymorphism theme
        ClaymorphismTheme.setup_theme(root)
        
        # Initialize database
        self.db = Database()
        
        # Current module tracking
        self.current_module = None
        
        # Create main UI
        self.create_ui()
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_ui(self):
        """Create the main UI with claymorphism style"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Logo and company name
        logo_frame = ttk.Frame(header_frame)
        logo_frame.pack(side=tk.LEFT)
        
        # Company name
        company_name = ClaymorphismTheme.create_label(
            logo_frame, 
            text="GANESH TOUGHENED INDUSTRY", 
            style="Title.TLabel"
        )
        company_name.pack(side=tk.LEFT, padx=(0, 20))
        
        # User info
        user_frame = ttk.Frame(header_frame)
        user_frame.pack(side=tk.RIGHT)
        
        user_label = ClaymorphismTheme.create_label(user_frame, text="Admin User")
        user_label.pack(side=tk.RIGHT)
        
        # Navigation sidebar
        nav_frame = ttk.Frame(main_container)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 0), pady=20)
        
        # Navigation card
        nav_card = ClaymorphismTheme.create_card(nav_frame, padding=20)
        nav_card.pack(fill=tk.BOTH, expand=True)
        
        # Navigation title
        nav_title = ClaymorphismTheme.create_label(
            nav_card, 
            text="NAVIGATION", 
            font=("Segoe UI", 12, "bold")
        )
        nav_title.pack(pady=(0, 20))
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.show_dashboard),
            ("Attendance", self.show_attendance),
            ("Visits", self.show_visits),
            ("Billing", self.show_billing),
            ("Customers", self.show_customers),
            ("Products", self.show_products),
            ("Inventory", self.show_inventory),
            ("Expenses", self.show_expenses),
            ("Reports", self.show_reports),
            ("Settings", self.show_settings)
        ]
        
        self.nav_buttons = {}
        for text, command in nav_buttons:
            btn = ClaymorphismTheme.create_button(
                nav_card, 
                text=text, 
                command=command,
                width=15
            )
            btn.pack(fill=tk.X, pady=5)
            self.nav_buttons[text] = btn
        
        # Main content area
        content_frame = ttk.Frame(main_container)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 20), pady=20)
        
        # Content card
        self.content_card = ClaymorphismTheme.create_card(content_frame, padding=20)
        self.content_card.pack(fill=tk.BOTH, expand=True)
        
        # Content area
        self.main_content = ttk.Frame(self.content_card)
        self.main_content.pack(fill=tk.BOTH, expand=True)
        
        # Footer
        footer_frame = ttk.Frame(main_container)
        footer_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        footer_text = ClaymorphismTheme.create_label(
            footer_frame, 
            text=f"© {datetime.now().year} GANESH TOUGHENED INDUSTRY. All rights reserved.",
            font=("Segoe UI", 9)
        )
        footer_text.pack()
    
    def show_dashboard(self):
        """Show the dashboard"""
        self.clear_content()
        self.highlight_nav_button("Dashboard")
        
        # Dashboard title
        dashboard_title = ClaymorphismTheme.create_label(
            self.main_content, 
            text="DASHBOARD", 
            style="Title.TLabel"
        )
        dashboard_title.pack(pady=(0, 20))
        
        # Dashboard cards container
        cards_container = ttk.Frame(self.main_content)
        cards_container.pack(fill=tk.BOTH, expand=True)
        
        # Create dashboard cards
        cards = [
            ("Total Workers", self.get_total_workers(), "#4299e1"),
            ("Today's Attendance", self.get_today_attendance(), "#48bb78"),
            ("Pending Visits", self.get_pending_visits(), "#ed8936"),
            ("Monthly Revenue", self.get_monthly_revenue(), "#9f7aea")
        ]
        
        for i, (title, value, color) in enumerate(cards):
            card_frame = ttk.Frame(cards_container)
            card_frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            
            # Configure grid weights
            cards_container.grid_rowconfigure(i//2, weight=1)
            cards_container.grid_columnconfigure(i%2, weight=1)
            
            # Create card
            card = ClaymorphismTheme.create_card(card_frame, padding=20)
            card.pack(fill=tk.BOTH, expand=True)
            
            # Card content
            title_label = ClaymorphismTheme.create_label(card, text=title)
            title_label.pack(anchor=tk.W)
            
            value_label = ClaymorphismTheme.create_label(
                card, 
                text=str(value), 
                font=("Segoe UI", 24, "bold")
            )
            value_label.pack(anchor=tk.W, pady=(10, 0))
    
    def show_attendance(self):
        """Show the attendance module"""
        self.clear_content()
        self.highlight_nav_button("Attendance")
        self.current_module = AttendanceModule(self.main_content, self.db, self)
    
    def show_visits(self):
        """Show the visits module"""
        self.clear_content()
        self.highlight_nav_button("Visits")
        self.current_module = VisitsModule(self.main_content, self.db, self)
    
    def show_billing(self):
        """Show the billing module"""
        self.clear_content()
        self.highlight_nav_button("Billing")
        self.current_module = BillingModule(self.main_content, self.db, self)
    
    def show_customers(self):
        """Show the customers module"""
        self.clear_content()
        self.highlight_nav_button("Customers")
        self.current_module = CustomersModule(self.main_content, self.db, self)
    
    def show_products(self):
        """Show the products module"""
        self.clear_content()
        self.highlight_nav_button("Products")
        self.current_module = ProductsModule(self.main_content, self.db, self)
    
    def show_inventory(self):
        """Show the inventory module"""
        self.clear_content()
        self.highlight_nav_button("Inventory")
        self.current_module = InventoryModule(self.main_content, self.db, self)
    
    def show_expenses(self):
        """Show the expenses module"""
        self.clear_content()
        self.highlight_nav_button("Expenses")
        self.current_module = ExpensesModule(self.main_content, self.db, self)
    
    def show_reports(self):
        """Show the reports module"""
        self.clear_content()
        self.highlight_nav_button("Reports")
        self.current_module = ReportsModule(self.main_content, self.db, self)
    
    def show_settings(self):
        """Show the settings module"""
        self.clear_content()
        self.highlight_nav_button("Settings")
        self.current_module = SettingsModule(self.main_content, self.db, self)
    
    def clear_content(self):
        """Clear the main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Clean up current module if it exists
        if self.current_module:
            self.current_module = None
    
    def highlight_nav_button(self, button_text):
        """Highlight the active navigation button"""
        for text, button in self.nav_buttons.items():
            if text == button_text:
                button.configure(style="Secondary.TButton")
            else:
                button.configure(style="TButton")
    
    def get_total_workers(self):
        """Get the total number of workers"""
        workers = self.db.get_workers()
        return len(workers)
    
    def get_today_attendance(self):
        """Get today's attendance count"""
        attendance = self.db.get_attendance_by_date(date.today())
        return len(attendance)
    
    def get_pending_visits(self):
        """Get the number of pending visits"""
        from datetime import timedelta
        pending_visits = self.db.get_visits(date.today(), date.today() + timedelta(days=7))
        return len(pending_visits)
    
    def get_monthly_revenue(self):
        """Get the monthly revenue"""
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        
        invoices = self.db.search_invoices(from_date=start_of_month, to_date=today)
        total_revenue = sum(invoice["total"] for invoice in invoices)
        
        return f"₹{total_revenue:,.2f}"

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernApp(root)
    root.mainloop()
import tkinter as tk
from tkinter import ttk
import os
import sys
from datetime import datetime

# Add the current directory to the path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from theme import ClaymorphismTheme
from modules.dashboard import DashboardModule
from modules.billing import BillingModule
from modules.attendance import AttendanceModule
from modules.visits import VisitsModule
from modules.works import WorksModule
from modules.customers import CustomersModule
from modules.products import ProductsModule
from modules.inventory import InventoryModule
from modules.expenses import ExpensesModule
from modules.reports import ReportsModule
from modules.settings import SettingsModule

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("GANESH TOUGHENED INDUSTRY")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Set background color
        self.root.configure(bg=ClaymorphismTheme.BG_PRIMARY)
        
        # Initialize database
        self.db = Database()
        
        # Apply claymorphism theme
        ClaymorphismTheme.configure_styles(root)
        
        # Create main layout
        self.create_layout()
        
        # Load dashboard by default
        self.load_module("dashboard")
    
    def create_layout(self):
        # Create header
        self.header = tk.Frame(self.root, bg=ClaymorphismTheme.BG_PRIMARY, height=80)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        
        # Company logo and name
        logo_frame = tk.Frame(self.header, bg=ClaymorphismTheme.BG_PRIMARY)
        logo_frame.pack(side="left", padx=20, pady=10)
        
        company_name = tk.Label(logo_frame, text="GANESH TOUGHENED INDUSTRY", 
                               font=ClaymorphismTheme.FONT_TITLE,
                               bg=ClaymorphismTheme.BG_PRIMARY,
                               fg=ClaymorphismTheme.TEXT_PRIMARY)
        company_name.pack()
        
        company_tagline = tk.Label(logo_frame, text="Quality Glass Solutions", 
                                  font=ClaymorphismTheme.FONT_SMALL,
                                  bg=ClaymorphismTheme.BG_PRIMARY,
                                  fg=ClaymorphismTheme.TEXT_SECONDARY)
        company_tagline.pack()
        
        # Current date and time
        date_frame = tk.Frame(self.header, bg=ClaymorphismTheme.BG_PRIMARY)
        date_frame.pack(side="right", padx=20, pady=10)
        
        current_date = datetime.now().strftime("%d %B %Y")
        date_label = tk.Label(date_frame, text=current_date, 
                             font=ClaymorphismTheme.FONT_NORMAL,
                             bg=ClaymorphismTheme.BG_PRIMARY,
                             fg=ClaymorphismTheme.TEXT_PRIMARY)
        date_label.pack()
        
        # Create sidebar
        self.sidebar = tk.Frame(self.root, bg=ClaymorphismTheme.BG_PRIMARY, width=200)
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)
        
        # Navigation buttons
        nav_items = [
            ("Dashboard", "dashboard"),
            ("Billing", "billing"),
            ("Attendance", "attendance"),
            ("Customer Visits", "visits"),
            ("Works", "works"),
            ("Customers", "customers"),
            ("Products", "products"),
            ("Inventory", "inventory"),
            ("Expenses", "expenses"),
            ("Reports", "reports"),
            ("Settings", "settings")
        ]
        
        # Create navigation buttons
        for item_name, item_id in nav_items:
            btn_frame, btn = ClaymorphismTheme.create_button(
                self.sidebar, 
                text=item_name,
                command=lambda m=item_id: self.load_module(m)
            )
            btn_frame.pack(fill="x", padx=15, pady=5)
        
        # Create main content area
        self.main_content = tk.Frame(self.root, bg=ClaymorphismTheme.BG_PRIMARY)
        self.main_content.pack(fill="both", expand=True, side="right")
        
        # Footer
        self.footer = tk.Frame(self.root, bg=ClaymorphismTheme.BG_PRIMARY, height=30)
        self.footer.pack(fill="x", side="bottom")
        self.footer.pack_propagate(False)
        
        footer_text = tk.Label(self.footer, 
                              text="© 2023 Ganesh Toughened Industry. All rights reserved.",
                              font=ClaymorphismTheme.FONT_SMALL,
                              bg=ClaymorphismTheme.BG_PRIMARY,
                              fg=ClaymorphismTheme.TEXT_SECONDARY)
        footer_text.pack(pady=5)
    
    def load_module(self, module_id):
        # Clear current content
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Load the selected module
        if module_id == "dashboard":
            self.current_module = DashboardModule(self.main_content, self.db, self)
        elif module_id == "billing":
            self.current_module = BillingModule(self.main_content, self.db, self)
        elif module_id == "attendance":
            self.current_module = AttendanceModule(self.main_content, self.db, self)
        elif module_id == "visits":
            self.current_module = VisitsModule(self.main_content, self.db, self)
        elif module_id == "works":
            self.current_module = WorksModule(self.main_content, self.db, self)
        elif module_id == "customers":
            self.current_module = CustomersModule(self.main_content, self.db, self)
        elif module_id == "products":
            self.current_module = ProductsModule(self.main_content, self.db, self)
        elif module_id == "inventory":
            self.current_module = InventoryModule(self.main_content, self.db, self)
        elif module_id == "expenses":
            self.current_module = ExpensesModule(self.main_content, self.db, self)
        elif module_id == "reports":
            self.current_module = ReportsModule(self.main_content, self.db, self)
        elif module_id == "settings":
            self.current_module = SettingsModule(self.main_content, self.db, self)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

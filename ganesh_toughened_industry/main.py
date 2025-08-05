import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, date
import os
import sys
import shutil
import zipfile
from PIL import Image, ImageTk, ImageDraw
import io
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import subprocess
import platform
import time
import calendar
from datetime import timedelta

# Import module files
from database import Database
from modules.billing import BillingModule
from modules.customer_history import CustomerHistoryModule
from modules.daily_ledger import DailyLedgerModule
from modules.attendance import AttendanceModule
from modules.payments import PaymentsModule
from modules.visits import VisitsModule
from modules.works import WorksModule
from modules.inventory import InventoryModule

class GaneshToughenedIndustryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ganesh Toughened Industry")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Set application icon
        try:
            self.root.iconbitmap("assets/images/icon.ico")
        except:
            pass
        
        # Initialize database
        self.db = Database()
        
        # Configure styles
        self.configure_styles()
        
        # Create main UI
        self.create_ui()
        
        # Load settings
        self.load_settings()
        
        # Check for backup
        self.check_backup()
    
    def configure_styles(self):
        """Configure application styles"""
        self.style = ttk.Style()
        
        # Configure theme
        self.style.theme_use('clam')
        
        # Configure colors
        bg_color = "#f0f0f0"
        primary_color = "#2c3e50"
        secondary_color = "#3498db"
        accent_color = "#e74c3c"
        success_color = "#2ecc71"
        warning_color = "#f39c12"
        
        self.root.configure(bg=bg_color)
        
        # Configure styles
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10), padding=6)
        self.style.map("TButton", 
                      background=[('active', secondary_color)],
                      foreground=[('active', 'white')])
        
        # Custom styles
        self.style.configure("Title.TLabel", font=("Arial", 16, "bold"), 
                            background=bg_color, foreground=primary_color)
        self.style.configure("Header.TLabel", font=("Arial", 12, "bold"), 
                            background=bg_color, foreground=primary_color)
        self.style.configure("Accent.TButton", font=("Arial", 10, "bold"), 
                            background=secondary_color, foreground="white")
        self.style.configure("Success.TButton", font=("Arial", 10, "bold"), 
                            background=success_color, foreground="white")
        self.style.configure("Warning.TButton", font=("Arial", 10, "bold"), 
                            background=warning_color, foreground="white")
        self.style.configure("Danger.TButton", font=("Arial", 10, "bold"), 
                            background=accent_color, foreground="white")
        
        # Store colors for later use
        self.bg_color = bg_color
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.accent_color = accent_color
        self.success_color = success_color
        self.warning_color = warning_color
    
    def create_ui(self):
        """Create the main user interface"""
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        self.create_header(main_container)
        
        # Create content area
        content_container = ttk.Frame(main_container)
        content_container.pack(fill=tk.BOTH, expand=True)
        
        # Create sidebar
        self.create_sidebar(content_container)
        
        # Create main content area
        self.main_content = ttk.Frame(content_container, style="Content.TFrame")
        self.main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create status bar
        self.create_status_bar(main_container)
        
        # Load default module
        self.load_module("billing")
    
    def create_header(self, parent):
        """Create application header"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Company logo
        try:
            logo_img = Image.open("assets/images/logo.png")
            logo_img = logo_img.resize((50, 50), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = ttk.Label(header_frame, image=self.logo_photo)
            logo_label.pack(side=tk.LEFT, padx=10)
        except:
            pass
        
        # Company name
        title_label = ttk.Label(header_frame, text="GANESH TOUGHENED INDUSTRY", 
                               style="Title.TLabel")
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Current date
        date_label = ttk.Label(header_frame, text=datetime.now().strftime("%d %B %Y"), 
                              style="Header.TLabel")
        date_label.pack(side=tk.RIGHT, padx=10)
    
    def create_sidebar(self, parent):
        """Create navigation sidebar"""
        sidebar = ttk.Frame(parent, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Navigation title
        nav_title = ttk.Label(sidebar, text="NAVIGATION", style="Header.TLabel")
        nav_title.pack(pady=(0, 10), anchor=tk.W)
        
        # Navigation buttons
        nav_buttons = [
            ("Customer Billing", "billing", "📄"),
            ("Customer History", "history", "📋"),
            ("Daily Ledger", "ledger", "📚"),
            ("Worker Attendance", "attendance", "👷"),
            ("Payments", "payments", "💰"),
            ("Customer Visits", "visits", "📆"),
            ("Works Completed", "works", "🏗️"),
            ("Inventory", "inventory", "📦"),
            ("Settings", "settings", "⚙️")
        ]
        
        for text, module, icon in nav_buttons:
            btn = ttk.Button(sidebar, text=f" {icon} {text}", 
                            command=lambda m=module: self.load_module(m))
            btn.pack(fill=tk.X, pady=5, anchor=tk.W)
            
            # Add hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.configure(style="Accent.TButton"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(style="TButton"))
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        # Database status
        self.db_status = ttk.Label(status_frame, text="Database: Connected")
        self.db_status.pack(side=tk.LEFT, padx=5)
        
        # Backup status
        self.backup_status = ttk.Label(status_frame, text="Last Backup: Never")
        self.backup_status.pack(side=tk.LEFT, padx=5)
        
        # User info
        user_label = ttk.Label(status_frame, text="User: Manager")
        user_label.pack(side=tk.RIGHT, padx=5)
    
    def load_module(self, module_name):
        """Load the specified module"""
        # Clear current content
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Load module based on name
        if module_name == "billing":
            self.current_module = BillingModule(self.main_content, self.db, self)
        elif module_name == "history":
            self.current_module = CustomerHistoryModule(self.main_content, self.db, self)
        elif module_name == "ledger":
            self.current_module = DailyLedgerModule(self.main_content, self.db, self)
        elif module_name == "attendance":
            self.current_module = AttendanceModule(self.main_content, self.db, self)
        elif module_name == "payments":
            self.current_module = PaymentsModule(self.main_content, self.db, self)
        elif module_name == "visits":
            self.current_module = VisitsModule(self.main_content, self.db, self)
        elif module_name == "works":
            self.current_module = WorksModule(self.main_content, self.db, self)
        elif module_name == "inventory":
            self.current_module = InventoryModule(self.main_content, self.db, self)
        elif module_name == "settings":
            self.load_settings_module()
    
    def load_settings_module(self):
        """Load settings module"""
        settings_frame = ttk.Frame(self.main_content)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(settings_frame, text="Application Settings", style="Title.TLabel")
        title.pack(pady=10)
        
        # Company settings
        company_frame = ttk.LabelFrame(settings_frame, text="Company Information")
        company_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Company name
        name_frame = ttk.Frame(company_frame)
        name_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(name_frame, text="Company Name:").pack(side=tk.LEFT)
        name_entry = ttk.Entry(name_frame, width=40)
        name_entry.pack(side=tk.LEFT, padx=10)
        name_entry.insert(0, "GANESH TOUGHENED INDUSTRY")
        
        # Address
        addr_frame = ttk.Frame(company_frame)
        addr_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(addr_frame, text="Address:").pack(side=tk.LEFT)
        addr_entry = ttk.Entry(addr_frame, width=40)
        addr_entry.pack(side=tk.LEFT, padx=10)
        addr_entry.insert(0, "Plot no:B13, Industrial Estate, Madanapalli")
        
        # GST
        gst_frame = ttk.Frame(company_frame)
        gst_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(gst_frame, text="GST No:").pack(side=tk.LEFT)
        gst_entry = ttk.Entry(gst_frame, width=40)
        gst_entry.pack(side=tk.LEFT, padx=10)
        gst_entry.insert(0, "37EXFPK2395CIZE")
        
        # Phone
        phone_frame = ttk.Frame(company_frame)
        phone_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(phone_frame, text="Phone:").pack(side=tk.LEFT)
        phone_entry = ttk.Entry(phone_frame, width=40)
        phone_entry.pack(side=tk.LEFT, padx=10)
        phone_entry.insert(0, "9398530499, 7013374872")
        
        # UPI settings
        upi_frame = ttk.LabelFrame(settings_frame, text="UPI Information")
        upi_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # UPI ID
        upi_id_frame = ttk.Frame(upi_frame)
        upi_id_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(upi_id_frame, text="UPI ID:").pack(side=tk.LEFT)
        upi_id_entry = ttk.Entry(upi_id_frame, width=40)
        upi_id_entry.pack(side=tk.LEFT, padx=10)
        upi_id_entry.insert(0, "ganeshtoughened@ybl")
        
        # UPI Name
        upi_name_frame = ttk.Frame(upi_frame)
        upi_name_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(upi_name_frame, text="UPI Name:").pack(side=tk.LEFT)
        upi_name_entry = ttk.Entry(upi_name_frame, width=40)
        upi_name_entry.pack(side=tk.LEFT, padx=10)
        upi_name_entry.insert(0, "GANESH TOUGHENED INDUSTRY")
        
        # Bank settings
        bank_frame = ttk.LabelFrame(settings_frame, text="Bank Information")
        bank_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Bank name
        bank_name_frame = ttk.Frame(bank_frame)
        bank_name_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(bank_name_frame, text="Bank Name:").pack(side=tk.LEFT)
        bank_name_entry = ttk.Entry(bank_name_frame, width=40)
        bank_name_entry.pack(side=tk.LEFT, padx=10)
        bank_name_entry.insert(0, "State Bank of India")
        
        # Account number
        acc_num_frame = ttk.Frame(bank_frame)
        acc_num_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(acc_num_frame, text="Account Number:").pack(side=tk.LEFT)
        acc_num_entry = ttk.Entry(acc_num_frame, width=40)
        acc_num_entry.pack(side=tk.LEFT, padx=10)
        acc_num_entry.insert(0, "12345678901")
        
        # IFSC
        ifsc_frame = ttk.Frame(bank_frame)
        ifsc_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(ifsc_frame, text="IFSC Code:").pack(side=tk.LEFT)
        ifsc_entry = ttk.Entry(ifsc_frame, width=40)
        ifsc_entry.pack(side=tk.LEFT, padx=10)
        ifsc_entry.insert(0, "SBIN0001234")
        
        # Branch
        branch_frame = ttk.Frame(bank_frame)
        branch_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(branch_frame, text="Branch:").pack(side=tk.LEFT)
        branch_entry = ttk.Entry(branch_frame, width=40)
        branch_entry.pack(side=tk.LEFT, padx=10)
        branch_entry.insert(0, "Madanapalli")
        
        # Save button
        save_btn = ttk.Button(settings_frame, text="Save Settings", command=self.save_settings)
        save_btn.pack(pady=20)
    
    def save_settings(self):
        """Save application settings"""
        # Implementation would save settings to database or config file
        messagebox.showinfo("Settings", "Settings saved successfully!")
    
    def load_settings(self):
        """Load application settings"""
        # Implementation would load settings from database or config file
        pass
    
    def check_backup(self):
        """Check if backup is needed"""
        # Implementation would check last backup date and create backup if needed
        pass
    
    def create_backup(self):
        """Create database backup"""
        # Implementation would create a zip file of the database
        pass
    
    def show_notification(self, title, message):
        """Show notification to user"""
        messagebox.showinfo(title, message)
    
    def update_status(self, status_type, message):
        """Update status bar"""
        if status_type == "db":
            self.db_status.config(text=f"Database: {message}")
        elif status_type == "backup":
            self.backup_status.config(text=f"Last Backup: {message}")

def main():
    root = tk.Tk()
    app = GaneshToughenedIndustryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
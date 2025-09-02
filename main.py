# main.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, date, timedelta
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
import threading
import json

# Import module files
from database import Database
from settings_manager import SettingsManager  # Import the new settings manager

# Try to import modules with error handling
try:
    from modules.billing import BillingModule
    from modules.customer_history import CustomerHistoryModule
    from modules.daily_ledger import DailyLedgerModule
    from modules.attendance import AttendanceModule
    from modules.payments import PaymentsModule
    from modules.visits import VisitsModule
    from modules.works import WorksModule
    from modules.inventory import InventoryModule
    
    try:
        from modules.recycle_bin import RecycleBinModule
    except ImportError:
        # Create placeholder module if it doesn't exist
        class RecycleBinModule:
            def __init__(self, parent, db, app):
                ttk.Label(parent, text="Recycle Bin Module - Not Available").pack(pady=20)
except ImportError as e:
    print(f"Import error: {e}")
    # Create placeholder modules if they don't exist
    class BillingModule:
        def __init__(self, parent, db, app):
            ttk.Label(parent, text="Billing Module - Not Available").pack(pady=20)
    
    class CustomerHistoryModule:
        def __init__(self, parent, db, app):
            ttk.Label(parent, text="Customer History Module - Not Available").pack(pady=20)
    
    class DailyLedgerModule:
        def __init__(self, parent, db, app):
            ttk.Label(parent, text="Daily Ledger Module - Not Available").pack(pady=20)
    
    class AttendanceModule:
        def __init__(self, parent, db, app):
            ttk.Label(parent, text="Attendance Module - Not Available").pack(pady=20)
    
    class PaymentsModule:
        def __init__(self, parent, db, app):
            ttk.Label(parent, text="Payments Module - Not Available").pack(pady=20)
    
    class VisitsModule:
        def __init__(self, parent, db, app):
            ttk.Label(parent, text="Visits Module - Not Available").pack(pady=20)
    
    class WorksModule:
        def __init__(self, parent, db, app):
            ttk.Label(parent, text="Works Module - Not Available").pack(pady=20)
    
    class InventoryModule:
        def __init__(self, parent, db, app):
            ttk.Label(parent, text="Inventory Module - Not Available").pack(pady=20)
    
    # Create placeholder module if it doesn't exist
    class RecycleBinModule:
        def __init__(self, parent, db, app):
            ttk.Label(parent, text="Recycle Bin Module - Not Available").pack(pady=20)

def enable_mousewheel_support(root):
    """Enable mouse wheel support for all scrollable widgets in the application"""
    
    def _on_mousewheel(event, widget):
        # Handle both Windows and Linux scrolling
        if event.num == 5 or event.delta == -120:
            widget.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120:
            widget.yview_scroll(-1, "units")
    
    # Find all canvas widgets and bind mouse wheel events
    def bind_mousewheel_to_all_widgets(widget):
        if isinstance(widget, tk.Canvas):
            widget.bind("<MouseWheel>", lambda e: _on_mousewheel(e, widget))
            widget.bind("<Button-4>", lambda e: _on_mousewheel(e, widget))
            widget.bind("<Button-5>", lambda e: _on_mousewheel(e, widget))
        
        # Recursively check child widgets
        for child in widget.winfo_children():
            bind_mousewheel_to_all_widgets(child)
    
    # Apply to all widgets in the application
    bind_mousewheel_to_all_widgets(root)

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
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Configure styles
        self.configure_styles()
        
        # Initialize backup settings variables before creating UI
        self.auto_backup_var = tk.BooleanVar(value=self.settings_manager.is_backup_enabled())
        self.backup_interval_var = tk.StringVar(value=str(self.settings_manager.get_backup_interval_hours()))
        self.backup_location_var = tk.StringVar(value=self.settings_manager.get_setting("backup_location", ""))
        
        # Create main UI
        self.create_ui()
        
        # Check for backup
        self.check_backup()
        
        # Start backup scheduler
        self.schedule_backup()
    
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
        title_label = ttk.Label(header_frame, text=self.settings_manager.get_company_name(), 
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
            ("Recycle Bin", "recycle_bin", "🗑️"),
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
        elif module_name == "recycle_bin":
            self.current_module = RecycleBinModule(self.main_content, self.db, self)
        elif module_name == "settings":
            self.load_settings_module()
        
        # Enable mouse wheel support for the newly loaded module
        enable_mousewheel_support(self.main_content)
    
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
        self.name_entry = ttk.Entry(name_frame, width=40)
        self.name_entry.pack(side=tk.LEFT, padx=10)
        self.name_entry.insert(0, self.settings_manager.get_company_name())
        
        # Address
        addr_frame = ttk.Frame(company_frame)
        addr_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(addr_frame, text="Address:").pack(side=tk.LEFT)
        self.addr_entry = ttk.Entry(addr_frame, width=40)
        self.addr_entry.pack(side=tk.LEFT, padx=10)
        self.addr_entry.insert(0, self.settings_manager.get_company_address())
        
        # GST
        gst_frame = ttk.Frame(company_frame)
        gst_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(gst_frame, text="GST No:").pack(side=tk.LEFT)
        self.gst_entry = ttk.Entry(gst_frame, width=40)
        self.gst_entry.pack(side=tk.LEFT, padx=10)
        self.gst_entry.insert(0, self.settings_manager.get_company_gst())
        
        # Phone
        phone_frame = ttk.Frame(company_frame)
        phone_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(phone_frame, text="Phone:").pack(side=tk.LEFT)
        self.phone_entry = ttk.Entry(phone_frame, width=40)
        self.phone_entry.pack(side=tk.LEFT, padx=10)
        self.phone_entry.insert(0, self.settings_manager.get_company_phone())
        
        # UPI settings
        upi_frame = ttk.LabelFrame(settings_frame, text="UPI Information")
        upi_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # UPI ID
        upi_id_frame = ttk.Frame(upi_frame)
        upi_id_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(upi_id_frame, text="UPI ID:").pack(side=tk.LEFT)
        self.upi_id_entry = ttk.Entry(upi_id_frame, width=40)
        self.upi_id_entry.pack(side=tk.LEFT, padx=10)
        self.upi_id_entry.insert(0, self.settings_manager.get_upi_id())
        
        # UPI Name
        upi_name_frame = ttk.Frame(upi_frame)
        upi_name_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(upi_name_frame, text="UPI Name:").pack(side=tk.LEFT)
        self.upi_name_entry = ttk.Entry(upi_name_frame, width=40)
        self.upi_name_entry.pack(side=tk.LEFT, padx=10)
        self.upi_name_entry.insert(0, self.settings_manager.get_upi_name())
        
        # Bank settings
        bank_frame = ttk.LabelFrame(settings_frame, text="Bank Information")
        bank_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Bank name
        bank_name_frame = ttk.Frame(bank_frame)
        bank_name_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(bank_name_frame, text="Bank Name:").pack(side=tk.LEFT)
        self.bank_name_entry = ttk.Entry(bank_name_frame, width=40)
        self.bank_name_entry.pack(side=tk.LEFT, padx=10)
        self.bank_name_entry.insert(0, self.settings_manager.get_bank_name())
        
        # Account number
        acc_num_frame = ttk.Frame(bank_frame)
        acc_num_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(acc_num_frame, text="Account Number:").pack(side=tk.LEFT)
        self.acc_num_entry = ttk.Entry(acc_num_frame, width=40)
        self.acc_num_entry.pack(side=tk.LEFT, padx=10)
        self.acc_num_entry.insert(0, self.settings_manager.get_bank_account())
        
        # IFSC
        ifsc_frame = ttk.Frame(bank_frame)
        ifsc_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(ifsc_frame, text="IFSC Code:").pack(side=tk.LEFT)
        self.ifsc_entry = ttk.Entry(ifsc_frame, width=40)
        self.ifsc_entry.pack(side=tk.LEFT, padx=10)
        self.ifsc_entry.insert(0, self.settings_manager.get_bank_ifsc())
        
        # Branch
        branch_frame = ttk.Frame(bank_frame)
        branch_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(branch_frame, text="Branch:").pack(side=tk.LEFT)
        self.branch_entry = ttk.Entry(branch_frame, width=40)
        self.branch_entry.pack(side=tk.LEFT, padx=10)
        self.branch_entry.insert(0, self.settings_manager.get_bank_branch())
        
        # Backup settings
        backup_frame = ttk.LabelFrame(settings_frame, text="Backup Settings")
        backup_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Auto backup
        auto_backup_frame = ttk.Frame(backup_frame)
        auto_backup_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(auto_backup_frame, text="Enable automatic backup", 
                        variable=self.auto_backup_var).pack(side=tk.LEFT)
        
        # Backup interval
        interval_frame = ttk.Frame(backup_frame)
        interval_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(interval_frame, text="Backup interval (hours):").pack(side=tk.LEFT)
        ttk.Spinbox(interval_frame, from_=1, to=168, textvariable=self.backup_interval_var, 
                    width=5).pack(side=tk.LEFT, padx=5)
        
        # Backup location
        location_frame = ttk.Frame(backup_frame)
        location_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(location_frame, text="Backup location:").pack(side=tk.LEFT)
        ttk.Entry(location_frame, textvariable=self.backup_location_var, width=30).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Browse button
        browse_btn = ttk.Button(location_frame, text="Browse", command=self.browse_backup_location)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        # Manual backup button
        manual_backup_btn = ttk.Button(backup_frame, text="Create Backup Now", command=self.create_backup)
        manual_backup_btn.pack(pady=10)
        
        # Save button
        save_btn = ttk.Button(settings_frame, text="Save Settings", command=self.save_settings)
        save_btn.pack(pady=20)
    
    def browse_backup_location(self):
        """Browse for backup location"""
        folder_path = filedialog.askdirectory(title="Select Backup Location")
        if folder_path:
            self.backup_location_var.set(folder_path)
    
    def save_settings(self):
        """Save application settings"""
        try:
            # Update settings
            self.settings_manager.update_setting("company_name", self.name_entry.get())
            self.settings_manager.update_setting("company_address", self.addr_entry.get())
            self.settings_manager.update_setting("company_phone", self.phone_entry.get())
            self.settings_manager.update_setting("company_gst", self.gst_entry.get())
            self.settings_manager.update_setting("upi_id", self.upi_id_entry.get())
            self.settings_manager.update_setting("upi_name", self.upi_name_entry.get())
            self.settings_manager.update_setting("bank_name", self.bank_name_entry.get())
            self.settings_manager.update_setting("bank_account", self.acc_num_entry.get())
            self.settings_manager.update_setting("bank_ifsc", self.ifsc_entry.get())
            self.settings_manager.update_setting("bank_branch", self.branch_entry.get())
            self.settings_manager.update_setting("backup_enabled", self.auto_backup_var.get())
            
            # Save both the frequency string and the interval hours
            self.settings_manager.update_setting("backup_frequency", f"{self.backup_interval_var.get()}hours")
            self.settings_manager.update_setting("backup_interval_hours", int(self.backup_interval_var.get()))
            
            self.settings_manager.update_setting("backup_location", self.backup_location_var.get())
            
            # Refresh settings in the main application
            self.refresh_settings()
            
            messagebox.showinfo("Settings", "Settings saved successfully!")
            
            # Restart backup scheduler with new settings
            self.schedule_backup()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def refresh_settings(self):
        """Refresh all settings from the settings manager"""
        # Update company name in header
        if hasattr(self, 'title_label'):
            self.title_label.config(text=self.settings_manager.get_company_name())
        
        # Update status bar if it exists
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text=f"Database: Connected | Last Backup: {self.last_backup_time}")
    
    def check_backup(self):
        """Check if backup is needed"""
        # Get the last backup date from the settings
        last_backup_date = None
        
        try:
            last_backup_str = self.settings_manager.get_setting("last_backup")
            if last_backup_str:
                last_backup_date = datetime.strptime(last_backup_str, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Error loading backup date: {e}")
        
        # Update the backup status
        if last_backup_date:
            self.update_status("backup", last_backup_date.strftime("%d/%m/%Y %H:%M"))
        else:
            self.update_status("backup", "Never")
    
    def schedule_backup(self):
        """Schedule automatic backup"""
        # Cancel any existing backup timer
        if hasattr(self, 'backup_timer') and self.backup_timer:
            self.backup_timer.cancel()
        
        # Check if auto backup is enabled
        if self.auto_backup_var.get():
            try:
                # Get backup interval in hours using the settings manager
                interval_hours = self.settings_manager.get_backup_interval_hours()
                
                # Schedule backup
                self.backup_timer = threading.Timer(interval_hours * 3600, self.auto_backup)
                self.backup_timer.daemon = True
                self.backup_timer.start()
                
                print(f"Next backup scheduled in {interval_hours} hours")
            except Exception as e:
                print(f"Error scheduling backup: {e}")
    
    def auto_backup(self):
        """Perform automatic backup"""
        try:
            # Create the backup
            success = self.create_backup()
            
            if success:
                # Save the backup date to settings
                self.settings_manager.update_setting("last_backup", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                # Schedule next backup
                self.schedule_backup()
        except Exception as e:
            print(f"Error in auto backup: {e}")
    
    def create_backup(self):
        """Create database backup"""
        try:
            # Get backup location
            backup_location = self.backup_location_var.get()
            
            if not backup_location:
                # Use default backup location
                backup_location = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
            
            # Create backup directory if it doesn't exist
            if not os.path.exists(backup_location):
                os.makedirs(backup_location)
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"ganesh_toughened_industry_backup_{timestamp}.zip"
            backup_path = os.path.join(backup_location, backup_filename)
            
            # Create a zip file
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add database file
                db_path = self.db.db_name
                if os.path.exists(db_path):
                    zipf.write(db_path, os.path.basename(db_path))
                
                # Add settings file if it exists
                settings_path = self.settings_manager.settings_file
                if os.path.exists(settings_path):
                    zipf.write(settings_path, os.path.basename(settings_path))
                
                # Add assets directory if it exists
                assets_path = "assets"
                if os.path.exists(assets_path):
                    for root, dirs, files in os.walk(assets_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(assets_path))
                            zipf.write(file_path, arcname)
            
            # Update backup status
            self.update_status("backup", datetime.now().strftime("%d/%m/%Y %H:%M"))
            
            # Show notification if this is a manual backup
            if not threading.current_thread().daemon:
                messagebox.showinfo("Backup Complete", f"Backup created successfully at:\n{backup_path}")
            
            return True
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to create backup: {e}")
            return False
    
    def show_notification(self, title, message):
        """Show notification to user"""
        messagebox.showinfo(title, message)
    
    def update_status(self, status_type, message):
        """Update status bar"""
        if status_type == "db":
            self.db_status.config(text=f"Database: {message}")
        elif status_type == "backup":
            self.backup_status.config(text=f"Last Backup: {message}")
            self.last_backup_time = message

def main():
    root = tk.Tk()
    app = GaneshToughenedIndustryApp(root)
    
    # Enable mouse wheel support for the entire application
    enable_mousewheel_support(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()
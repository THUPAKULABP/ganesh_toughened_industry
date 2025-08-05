"""
Utils package for Ganesh Toughened Industry Desktop Application.

This package contains utility functions and classes used throughout the application:
- pdf_generator: PDF generation utilities for invoices and reports
- backup: Database backup and restore functionality
- helpers: Common helper functions for formatting, validation, etc.
"""

__version__ = "1.0.0"
__author__ = "Ganesh Toughened Industry"

# Import all utility modules for easy access
from . import pdf_generator
from . import backup
from . import helpers

# Import commonly used classes and functions directly
from .pdf_generator import PDFGenerator
from .backup import BackupManager
from .helpers import Helpers

# Package information dictionary
PACKAGE_INFO = {
    "name": "Ganesh Toughened Industry Utils",
    "version": __version__,
    "author": __author__,
    "description": "Utility functions and classes for the Ganesh Toughened Industry Desktop Application",
    "modules": {
        "pdf_generator": {
            "name": "PDF Generator",
            "description": "Generate PDF invoices, reports, and other documents",
            "class": "PDFGenerator"
        },
        "backup": {
            "name": "Backup Manager",
            "description": "Handle database backup and restore operations",
            "class": "BackupManager"
        },
        "helpers": {
            "name": "Helper Functions",
            "description": "Common helper functions for formatting, validation, and file operations",
            "class": "Helpers"
        }
    }
}

def get_package_info():
    """Get information about the utils package"""
    return PACKAGE_INFO

def get_module_info(module_name):
    """Get information about a specific utility module"""
    return PACKAGE_INFO.get("modules", {}).get(module_name, {
        "name": "Unknown",
        "description": "No description available",
        "class": None
    })

def list_all_modules():
    """List all available utility modules with their information"""
    return [(module, info["name"], info["description"]) 
            for module, info in PACKAGE_INFO.get("modules", {}).items()]

def create_pdf_generator(db):
    """Create and return a PDFGenerator instance"""
    return PDFGenerator(db)

def create_backup_manager(db_path, backup_dir="backups"):
    """Create and return a BackupManager instance"""
    return BackupManager(db_path, backup_dir)

# Utility functions that are commonly used throughout the application
def format_currency(amount):
    """Format amount as currency (shortcut to Helpers.format_currency)"""
    return Helpers.format_currency(amount)

def format_date(date_obj, format_str="%d/%m/%Y"):
    """Format date object as string (shortcut to Helpers.format_date)"""
    return Helpers.format_date(date_obj, format_str)

def parse_date(date_str, format_str="%d/%m/%Y"):
    """Parse date string to date object (shortcut to Helpers.parse_date)"""
    return Helpers.parse_date(date_str, format_str)

def calculate_sqft(height, width):
    """Calculate square footage from height and width in inches (shortcut to Helpers.calculate_sqft)"""
    return Helpers.calculate_sqft(height, width)

def validate_phone(phone):
    """Validate phone number (shortcut to Helpers.validate_phone)"""
    return Helpers.validate_phone(phone)

def validate_email(email):
    """Validate email address (shortcut to Helpers.validate_email)"""
    return Helpers.validate_email(email)

def validate_gst(gst):
    """Validate GST number (shortcut to Helpers.validate_gst)"""
    return Helpers.validate_gst(gst)

def generate_invoice_number(prefix="GTI"):
    """Generate a unique invoice number (shortcut to Helpers.generate_invoice_number)"""
    return Helpers.generate_invoice_number(prefix)

def resource_path(relative_path):
    """Get absolute path to resource (shortcut to Helpers.resource_path)"""
    return Helpers.resource_path(relative_path)

def open_file(file_path):
    """Open file with default application (shortcut to Helpers.open_file)"""
    return Helpers.open_file(file_path)

def get_file_size(file_path):
    """Get file size in human readable format (shortcut to Helpers.get_file_size)"""
    return Helpers.get_file_size(file_path)

def create_directory_if_not_exists(directory):
    """Create directory if it doesn't exist (shortcut to Helpers.create_directory_if_not_exists)"""
    return Helpers.create_directory_if_not_exists(directory)

def is_numeric(value):
    """Check if value is numeric (shortcut to Helpers.is_numeric)"""
    return Helpers.is_numeric(value)

def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers (shortcut to Helpers.safe_divide)"""
    return Helpers.safe_divide(numerator, denominator, default)

def truncate_text(text, max_length=30):
    """Truncate text to maximum length (shortcut to Helpers.truncate_text)"""
    return Helpers.truncate_text(text, max_length)

def get_month_start_end(date_obj):
    """Get start and end date of month for a given date (shortcut to Helpers.get_month_start_end)"""
    return Helpers.get_month_start_end(date_obj)

def get_week_start_end(date_obj):
    """Get start and end date of week for a given date (shortcut to Helpers.get_week_start_end)"""
    return Helpers.get_week_start_end(date_obj)
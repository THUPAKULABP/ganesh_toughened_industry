import os
import sys
import subprocess
import platform
from datetime import datetime, date, timedelta
import calendar

class Helpers:
    """Helper functions for the application"""
    
    @staticmethod
    def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    @staticmethod
    def format_currency(amount):
        """Format amount as currency"""
        return f"₹{amount:,.2f}"
    
    @staticmethod
    def format_date(date_obj, format_str="%d/%m/%Y"):
        """Format date object as string"""
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_obj, "%d/%m/%Y").date()
                except ValueError:
                    return date_obj
        
        return date_obj.strftime(format_str)
    
    @staticmethod
    def parse_date(date_str, format_str="%d/%m/%Y"):
        """Parse date string to date object"""
        try:
            return datetime.strptime(date_str, format_str).date()
        except ValueError:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return None
    
    @staticmethod
    def calculate_sqft(height, width):
        """Calculate square footage from height and width in inches"""
        try:
            return (height * width) / 144
        except (TypeError, ValueError):
            return 0
    
    @staticmethod
    def round_off(amount):
        """Round off amount to nearest integer"""
        return round(amount)
    
    @staticmethod
    def get_month_start_end(date_obj):
        """Get start and end date of month for a given date"""
        year = date_obj.year
        month = date_obj.month
        
        # Get first day of month
        start_date = date(year, month, 1)
        
        # Get last day of month
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        return start_date, end_date
    
    @staticmethod
    def get_week_start_end(date_obj):
        """Get start and end date of week for a given date (Monday to Sunday)"""
        # Get weekday (Monday is 0 and Sunday is 6)
        weekday = date_obj.weekday()
        
        # Calculate start of week (Monday)
        start_date = date_obj - timedelta(days=weekday)
        
        # Calculate end of week (Sunday)
        end_date = start_date + timedelta(days=6)
        
        return start_date, end_date
    
    @staticmethod
    def open_file(file_path):
        """Open file with default application"""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", file_path])
            else:  # Linux
                subprocess.call(["xdg-open", file_path])
            return True
        except Exception as e:
            print(f"Error opening file: {e}")
            return False
    
    @staticmethod
    def generate_invoice_number(prefix="GTI"):
        """Generate a unique invoice number"""
        now = datetime.now()
        year_month = now.strftime("%y%m")
        
        # This would typically be implemented in the database module
        # Here we're just providing a template
        return f"{prefix}{year_month}0001"
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number"""
        if not phone:
            return True
        
        # Remove any non-digit characters
        phone = ''.join(filter(str.isdigit, phone))
        
        # Check if phone number has 10 digits
        return len(phone) == 10
    
    @staticmethod
    def validate_email(email):
        """Validate email address"""
        if not email:
            return True
        
        # Simple email validation
        return '@' in email and '.' in email.split('@')[-1]
    
    @staticmethod
    def validate_gst(gst):
        """Validate GST number"""
        if not gst:
            return True
        
        # Remove any non-alphanumeric characters
        gst = ''.join(filter(str.isalnum, gst))
        
        # Check if GST number has 15 characters
        return len(gst) == 15
    
    @staticmethod
    def truncate_text(text, max_length=30):
        """Truncate text to maximum length"""
        if len(text) <= max_length:
            return text
        
        return text[:max_length-3] + "..."
    
    @staticmethod
    def get_file_size(file_path):
        """Get file size in human readable format"""
        if not os.path.exists(file_path):
            return "0 bytes"
        
        size = os.path.getsize(file_path)
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        
        return f"{size:.2f} TB"
    
    @staticmethod
    def create_directory_if_not_exists(directory):
        """Create directory if it doesn't exist"""
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    @staticmethod
    def is_numeric(value):
        """Check if value is numeric"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def safe_divide(numerator, denominator, default=0):
        """Safely divide two numbers"""
        try:
            if denominator == 0:
                return default
            return numerator / denominator
        except (TypeError, ZeroDivisionError):
            return default
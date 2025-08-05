"""
Modules package for Ganesh Toughened Industry Desktop Application.

This package contains all the functional modules for the application:
- billing: Customer billing system
- customer_history: Customer history tracking
- daily_ledger: Daily ledger management
- attendance: Worker attendance system
- payments: Payment tracking
- visits: Customer visit logs
- works: Works completed tracking
- inventory: Product inventory management
"""

__version__ = "1.0.0"
__author__ = "Ganesh Toughened Industry"

# Import all modules for easy access
from . import billing
from . import customer_history
from . import daily_ledger
from . import attendance
from . import payments
from . import visits
from . import works
from . import inventory

# Module information dictionary
MODULE_INFO = {
    "billing": {
        "name": "Customer Billing System",
        "description": "Create and manage customer invoices with PDF generation"
    },
    "customer_history": {
        "name": "Customer History",
        "description": "Track customer billing history and outstanding payments"
    },
    "daily_ledger": {
        "name": "Daily Ledger",
        "description": "View daily glass size entries and calculate total SQ.FT"
    },
    "attendance": {
        "name": "Worker Attendance",
        "description": "Track worker attendance with morning and afternoon sessions"
    },
    "payments": {
        "name": "Payment Tracking",
        "description": "Manage incoming and outgoing payments with detailed reports"
    },
    "visits": {
        "name": "Customer Visits",
        "description": "Log customer visits and track daily visitor statistics"
    },
    "works": {
        "name": "Works Completed",
        "description": "Track completed and pending glass works"
    },
    "inventory": {
        "name": "Product Inventory",
        "description": "Manage glass product inventory with stock movements"
    }
}

def get_module_info(module_name):
    """Get information about a specific module"""
    return MODULE_INFO.get(module_name, {"name": "Unknown", "description": "No description available"})

def list_all_modules():
    """List all available modules with their information"""
    return [(module, info["name"], info["description"]) for module, info in MODULE_INFO.items()]
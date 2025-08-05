import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from theme import ClaymorphismTheme
import csv

class ReportsModule:
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
            text="Reports & Analytics", 
            height=80
        )
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Content area
        content_frame = tk.Frame(main_container, bg=ClaymorphismTheme.BG_PRIMARY)
        content_frame.pack(fill="both", expand=True)
        
        # Left panel - Report options
        left_panel = tk.Frame(content_frame, bg=ClaymorphismTheme.BG_PRIMARY, width=300)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Report options card
        options_frame, options_card = ClaymorphismTheme.create_card(left_panel, text="Report Options")
        options_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Report type
        type_label = tk.Label(options_card, text="Report Type:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        type_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        self.report_type_frame, self.report_type = ClaymorphismTheme.create_combobox(options_card, width=25)
        self.report_type_frame.pack(fill="x", padx=20, pady=5)
        self.report_type['values'] = (
            "Sales Report", 
            "Customer Report", 
            "Inventory Report", 
            "Expense Report",
            "Attendance Report",
            "Profit & Loss Statement"
        )
        self.report_type.current(0)
        self.report_type.bind("<<ComboboxSelected>>", self.on_report_type_change)
        
        # Date range
        date_label = tk.Label(options_card, text="Date Range:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        date_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        # From date
        from_label = tk.Label(options_card, text="From:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_SMALL)
        from_label.pack(anchor="w", padx=20, pady=5)
        
        self.from_date_frame, self.from_date = ClaymorphismTheme.create_entry(options_card, width=25)
        self.from_date_frame.pack(fill="x", padx=20, pady=5)
        
        # Set to first day of current month
        today = datetime.now()
        first_day = today.replace(day=1)
        self.from_date.insert(0, first_day.strftime("%Y-%m-%d"))
        
        # To date
        to_label = tk.Label(options_card, text="To:", bg=ClaymorphismTheme.BG_CARD, 
                           font=ClaymorphismTheme.FONT_SMALL)
        to_label.pack(anchor="w", padx=20, pady=5)
        
        self.to_date_frame, self.to_date = ClaymorphismTheme.create_entry(options_card, width=25)
        self.to_date_frame.pack(fill="x", padx=20, pady=5)
        
        # Set to today
        self.to_date.insert(0, today.strftime("%Y-%m-%d"))
        
        # Generate button
        generate_btn_frame, generate_btn = ClaymorphismTheme.create_button(
            options_card, 
            text="Generate Report",
            command=self.generate_report
        )
        generate_btn_frame.pack(fill="x", padx=20, pady=20)
        
        # Export button
        export_btn_frame, export_btn = ClaymorphismTheme.create_button(
            options_card, 
            text="Export to CSV",
            command=self.export_report
        )
        export_btn_frame.pack(fill="x", padx=20, pady=5)
        
        # Right panel - Report display
        right_panel = tk.Frame(content_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Report display card
        display_frame, display_card = ClaymorphismTheme.create_card(right_panel, text="Report Preview")
        display_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Summary frame
        self.summary_frame = tk.Frame(display_card, bg=ClaymorphismTheme.BG_CARD)
        self.summary_frame.pack(fill="x", padx=10, pady=10)
        
        # Report treeview
        self.report_tree = ttk.Treeview(display_card)
        self.report_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(display_card, orient="vertical", command=self.report_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.report_tree.configure(yscrollcommand=scrollbar.set)
        
        # Initialize with sales report
        self.on_report_type_change()
    
    def on_report_type_change(self, event=None):
        """Handle report type change"""
        report_type = self.report_type.get()
        
        # Clear existing treeview columns
        for col in self.report_tree["columns"]:
            self.report_tree.heading(col, text="")
        
        self.report_tree["columns"] = ()
        self.report_tree["show"] = "headings"
        
        # Clear summary frame
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        
        # Configure treeview based on report type
        if report_type == "Sales Report":
            self.report_tree["columns"] = ("ID", "Date", "Invoice", "Customer", "Amount")
            self.report_tree.heading("ID", text="ID")
            self.report_tree.heading("Date", text="Date")
            self.report_tree.heading("Invoice", text="Invoice")
            self.report_tree.heading("Customer", text="Customer")
            self.report_tree.heading("Amount", text="Amount")
            
            self.report_tree.column("ID", width=50)
            self.report_tree.column("Date", width=100)
            self.report_tree.column("Invoice", width=120)
            self.report_tree.column("Customer", width=150)
            self.report_tree.column("Amount", width=100)
            
            # Add summary labels
            total_label = tk.Label(self.summary_frame, text="Total Sales: ₹0.00", 
                                  bg=ClaymorphismTheme.BG_CARD, 
                                  font=ClaymorphismTheme.FONT_SUBTITLE,
                                  fg=ClaymorphismTheme.TEXT_PRIMARY)
            total_label.pack(side="left", padx=20, pady=10)
            
            self.total_sales_label = total_label
            
        elif report_type == "Customer Report":
            self.report_tree["columns"] = ("ID", "Name", "Place", "Phone", "Balance")
            self.report_tree.heading("ID", text="ID")
            self.report_tree.heading("Name", text="Name")
            self.report_tree.heading("Place", text="Place")
            self.report_tree.heading("Phone", text="Phone")
            self.report_tree.heading("Balance", text="Balance")
            
            self.report_tree.column("ID", width=50)
            self.report_tree.column("Name", width=150)
            self.report_tree.column("Place", width=100)
            self.report_tree.column("Phone", width=120)
            self.report_tree.column("Balance", width=100)
            
            # Add summary labels
            count_label = tk.Label(self.summary_frame, text="Total Customers: 0", 
                                  bg=ClaymorphismTheme.BG_CARD, 
                                  font=ClaymorphismTheme.FONT_SUBTITLE,
                                  fg=ClaymorphismTheme.TEXT_PRIMARY)
            count_label.pack(side="left", padx=20, pady=10)
            
            self.customer_count_label = count_label
            
            balance_label = tk.Label(self.summary_frame, text="Total Balance: ₹0.00", 
                                   bg=ClaymorphismTheme.BG_CARD, 
                                   font=ClaymorphismTheme.FONT_SUBTITLE,
                                   fg=ClaymorphismTheme.TEXT_PRIMARY)
            balance_label.pack(side="left", padx=20, pady=10)
            
            self.total_balance_label = balance_label
            
        elif report_type == "Inventory Report":
            self.report_tree["columns"] = ("ID", "Name", "Type", "Quantity")
            self.report_tree.heading("ID", text="ID")
            self.report_tree.heading("Name", text="Name")
            self.report_tree.heading("Type", text="Type")
            self.report_tree.heading("Quantity", text="Quantity")
            
            self.report_tree.column("ID", width=50)
            self.report_tree.column("Name", width=150)
            self.report_tree.column("Type", width=100)
            self.report_tree.column("Quantity", width=100)
            
            # Add summary labels
            count_label = tk.Label(self.summary_frame, text="Total Products: 0", 
                                  bg=ClaymorphismTheme.BG_CARD, 
                                  font=ClaymorphismTheme.FONT_SUBTITLE,
                                  fg=ClaymorphismTheme.TEXT_PRIMARY)
            count_label.pack(side="left", padx=20, pady=10)
            
            self.product_count_label = count_label
            
        elif report_type == "Expense Report":
            self.report_tree["columns"] = ("ID", "Date", "Description", "Amount", "Category")
            self.report_tree.heading("ID", text="ID")
            self.report_tree.heading("Date", text="Date")
            self.report_tree.heading("Description", text="Description")
            self.report_tree.heading("Amount", text="Amount")
            self.report_tree.heading("Category", text="Category")
            
            self.report_tree.column("ID", width=50)
            self.report_tree.column("Date", width=100)
            self.report_tree.column("Description", width=200)
            self.report_tree.column("Amount", width=100)
            self.report_tree.column("Category", width=100)
            
            # Add summary labels
            total_label = tk.Label(self.summary_frame, text="Total Expenses: ₹0.00", 
                                  bg=ClaymorphismTheme.BG_CARD, 
                                  font=ClaymorphismTheme.FONT_SUBTITLE,
                                  fg=ClaymorphismTheme.TEXT_PRIMARY)
            total_label.pack(side="left", padx=20, pady=10)
            
            self.total_expenses_label = total_label
            
        elif report_type == "Attendance Report":
            self.report_tree["columns"] = ("ID", "Worker", "Date", "Morning", "Afternoon", "Notes")
            self.report_tree.heading("ID", text="ID")
            self.report_tree.heading("Worker", text="Worker")
            self.report_tree.heading("Date", text="Date")
            self.report_tree.heading("Morning", text="Morning")
            self.report_tree.heading("Afternoon", text="Afternoon")
            self.report_tree.heading("Notes", text="Notes")
            
            self.report_tree.column("ID", width=50)
            self.report_tree.column("Worker", width=150)
            self.report_tree.column("Date", width=100)
            self.report_tree.column("Morning", width=80)
            self.report_tree.column("Afternoon", width=80)
            self.report_tree.column("Notes", width=150)
            
            # Add summary labels
            count_label = tk.Label(self.summary_frame, text="Total Records: 0", 
                                  bg=ClaymorphismTheme.BG_CARD, 
                                  font=ClaymorphismTheme.FONT_SUBTITLE,
                                  fg=ClaymorphismTheme.TEXT_PRIMARY)
            count_label.pack(side="left", padx=20, pady=10)
            
            self.attendance_count_label = count_label
            
        elif report_type == "Profit & Loss Statement":
            self.report_tree["columns"] = ("Month", "Income", "Expenses", "Profit")
            self.report_tree.heading("Month", text="Month")
            self.report_tree.heading("Income", text="Income")
            self.report_tree.heading("Expenses", text="Expenses")
            self.report_tree.heading("Profit", text="Profit")
            
            self.report_tree.column("Month", width=100)
            self.report_tree.column("Income", width=100)
            self.report_tree.column("Expenses", width=100)
            self.report_tree.column("Profit", width=100)
            
            # Add summary labels
            total_label = tk.Label(self.summary_frame, text="Net Profit: ₹0.00", 
                                  bg=ClaymorphismTheme.BG_CARD, 
                                  font=ClaymorphismTheme.FONT_SUBTITLE,
                                  fg=ClaymorphismTheme.TEXT_PRIMARY)
            total_label.pack(side="left", padx=20, pady=10)
            
            self.net_profit_label = total_label
    
    def generate_report(self):
        """Generate the selected report"""
        report_type = self.report_type.get()
        from_date_str = self.from_date.get().strip()
        to_date_str = self.to_date.get().strip()
        
        # Validate dates
        try:
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Invalid Date", "Please enter a valid from date in YYYY-MM-DD format.")
            return
        
        try:
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Invalid Date", "Please enter a valid to date in YYYY-MM-DD format.")
            return
        
        # Clear existing items
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        # Generate report based on type
        if report_type == "Sales Report":
            self.generate_sales_report(from_date, to_date)
        elif report_type == "Customer Report":
            self.generate_customer_report()
        elif report_type == "Inventory Report":
            self.generate_inventory_report()
        elif report_type == "Expense Report":
            self.generate_expense_report(from_date, to_date)
        elif report_type == "Attendance Report":
            self.generate_attendance_report(from_date, to_date)
        elif report_type == "Profit & Loss Statement":
            self.generate_profit_loss_report()
    
    def generate_sales_report(self, from_date, to_date):
        """Generate sales report"""
        # Get invoices within date range
        invoices = self.db.search_invoices(from_date=from_date.strftime("%Y-%m-%d"), 
                                          to_date=to_date.strftime("%Y-%m-%d"))
        
        total_sales = 0
        
        # Add invoices to treeview
        for invoice in invoices:
            self.report_tree.insert("", "end", values=(
                invoice["invoice_id"],
                invoice["date"].strftime("%Y-%m-%d"),
                invoice["invoice_number"],
                invoice["customer_name"],
                f"₹{invoice['total']:.2f}"
            ))
            total_sales += invoice["total"]
        
        # Update summary
        self.total_sales_label.config(text=f"Total Sales: ₹{total_sales:.2f}")
    
    def generate_customer_report(self):
        """Generate customer report"""
        customers = self.db.get_customers()
        total_balance = 0
        
        # Add customers to treeview
        for customer in customers:
            balance = self.db.get_customer_balance(customer["customer_id"])
            self.report_tree.insert("", "end", values=(
                customer["customer_id"],
                customer["name"],
                customer["place"] or "",
                customer["phone"] or "",
                f"₹{balance:.2f}"
            ))
            total_balance += balance
        
        # Update summary
        self.customer_count_label.config(text=f"Total Customers: {len(customers)}")
        self.total_balance_label.config(text=f"Total Balance: ₹{total_balance:.2f}")
    
    def generate_inventory_report(self):
        """Generate inventory report"""
        inventory = self.db.get_current_inventory()
        
        # Add inventory items to treeview
        for item in inventory:
            self.report_tree.insert("", "end", values=(
                item["product_id"],
                item["name"],
                item["type"],
                item["current_quantity"]
            ))
        
        # Update summary
        self.product_count_label.config(text=f"Total Products: {len(inventory)}")
    
    def generate_expense_report(self, from_date, to_date):
        """Generate expense report"""
        expenses = self.db.get_expenses(from_date=from_date, to_date=to_date)
        total_expenses = 0
        
        # Add expenses to treeview
        for expense in expenses:
            self.report_tree.insert("", "end", values=(
                expense["expense_id"],
                expense["date"].strftime("%Y-%m-%d"),
                expense["description"],
                f"₹{expense['amount']:.2f}",
                expense["category"] or ""
            ))
            total_expenses += expense["amount"]
        
        # Update summary
        self.total_expenses_label.config(text=f"Total Expenses: ₹{total_expenses:.2f}")
    
    def generate_attendance_report(self, from_date, to_date):
        """Generate attendance report"""
        attendance = self.db.get_attendance()
        
        # Filter by date range
        filtered_attendance = [
            a for a in attendance 
            if from_date <= a["date"] <= to_date
        ]
        
        # Add attendance records to treeview
        for record in filtered_attendance:
            morning = "Yes" if record["morning"] else "No"
            afternoon = "Yes" if record["afternoon"] else "No"
            
            self.report_tree.insert("", "end", values=(
                record["attendance_id"],
                record["worker_name"],
                record["date"].strftime("%Y-%m-%d"),
                morning,
                afternoon,
                record["notes"] or ""
            ))
        
        # Update summary
        self.attendance_count_label.config(text=f"Total Records: {len(filtered_attendance)}")
    
    def generate_profit_loss_report(self):
        """Generate profit and loss statement"""
        # Get current year
        current_year = datetime.now().year
        
        # Generate monthly summary
        monthly_data = []
        net_profit = 0
        
        for month in range(1, 13):
            summary = self.db.get_monthly_summary(current_year, month)
            
            month_name = datetime(current_year, month, 1).strftime("%B %Y")
            
            monthly_data.append({
                "month": month_name,
                "income": summary["invoice_total"],
                "expenses": summary["expense_total"],
                "profit": summary["net_profit"]
            })
            
            net_profit += summary["net_profit"]
        
        # Add monthly data to treeview
        for data in monthly_data:
            self.report_tree.insert("", "end", values=(
                data["month"],
                f"₹{data['income']:.2f}",
                f"₹{data['expenses']:.2f}",
                f"₹{data['profit']:.2f}"
            ))
        
        # Update summary
        self.net_profit_label.config(text=f"Net Profit: ₹{net_profit:.2f}")
    
    def export_report(self):
        """Export report to CSV"""
        report_type = self.report_type.get()
        
        # Get file path
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title=f"Export {report_type}"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers
                headers = [self.report_tree.heading(col)["text"] for col in self.report_tree["columns"]]
                writer.writerow(headers)
                
                # Write data
                for item in self.report_tree.get_children():
                    values = self.report_tree.item(item, "values")
                    writer.writerow(values)
            
            messagebox.showinfo("Export Successful", f"Report exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")
    
    @staticmethod
    def create_combobox(parent, width=20, **kwargs):
        """Create a claymorphism-style combobox widget"""
        combo_frame = tk.Frame(parent, bg=ClaymorphismTheme.BG_PRIMARY)
        
        # Shadow effect
        shadow = tk.Frame(combo_frame, bg=ClaymorphismTheme.SHADOW, 
                         highlightthickness=0)
        shadow.place(x=2, y=2, relwidth=1, relheight=1)
        
        # Combobox
        combo = ttk.Combobox(combo_frame, width=width, **kwargs)
        combo.pack(fill="both", expand=True, padx=5, pady=5)
        
        return combo_frame, combo
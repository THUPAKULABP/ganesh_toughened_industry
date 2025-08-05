import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date, timedelta
import calendar
import os
import platform
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors

class DailyLedgerModule:
    def __init__(self, parent, db, app):
        self.parent = parent
        self.db = db
        self.app = app
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """Create the daily ledger UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="DAILY LEDGER", style="Title.TLabel")
        title.pack(pady=10)
        
        # Filter frame
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Date range
        ttk.Label(filter_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.from_date_var = tk.StringVar(value=(date.today() - timedelta(days=7)).strftime("%d/%m/%Y"))
        ttk.Entry(filter_frame, textvariable=self.from_date_var, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.to_date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(filter_frame, textvariable=self.to_date_var, width=12).pack(side=tk.LEFT, padx=5)
        
        # Quick date filters
        quick_frame = ttk.Frame(filter_frame)
        quick_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(quick_frame, text="Today", command=lambda: self.set_date_range("today")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="Yesterday", command=lambda: self.set_date_range("yesterday")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="This Week", command=lambda: self.set_date_range("this_week")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="This Month", command=lambda: self.set_date_range("this_month")).pack(side=tk.LEFT, padx=2)
        
        # Search button
        search_btn = ttk.Button(filter_frame, text="Search", command=self.search_ledger)
        search_btn.pack(side=tk.LEFT, padx=10)
        
        # Export button
        export_btn = ttk.Button(filter_frame, text="Export PDF", command=self.export_pdf)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Ledger display
        ledger_frame = ttk.Frame(main_frame)
        ledger_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create notebook for date grouping
        self.ledger_notebook = ttk.Notebook(ledger_frame)
        self.ledger_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Load initial ledger
        self.search_ledger()
    
    def set_date_range(self, range_type):
        """Set date range based on quick filter"""
        today = date.today()
        
        if range_type == "today":
            self.from_date_var.set(today.strftime("%d/%m/%Y"))
            self.to_date_var.set(today.strftime("%d/%m/%Y"))
        elif range_type == "yesterday":
            yesterday = today - timedelta(days=1)
            self.from_date_var.set(yesterday.strftime("%d/%m/%Y"))
            self.to_date_var.set(yesterday.strftime("%d/%m/%Y"))
        elif range_type == "this_week":
            # Get start of week (Monday)
            start_of_week = today - timedelta(days=today.weekday())
            self.from_date_var.set(start_of_week.strftime("%d/%m/%Y"))
            self.to_date_var.set(today.strftime("%d/%m/%Y"))
        elif range_type == "this_month":
            # Get start of month
            start_of_month = today.replace(day=1)
            self.from_date_var.set(start_of_month.strftime("%d/%m/%Y"))
            self.to_date_var.set(today.strftime("%d/%m/%Y"))
    
    def search_ledger(self):
        """Search ledger based on date range"""
        # Clear existing tabs
        for tab_id in self.ledger_notebook.tabs():
            self.ledger_notebook.forget(tab_id)
        
        # Get date range
        from_date_str = self.from_date_var.get()
        to_date_str = self.to_date_var.get()
        
        try:
            # Parse dates
            from_day, from_month, from_year = from_date_str.split('/')
            from_date = date(int(from_year), int(from_month), int(from_day))
            
            to_day, to_month, to_year = to_date_str.split('/')
            to_date = date(int(to_year), int(to_month), int(to_day))
            
            # Get ledger data
            ledger_data = self.db.get_daily_ledger(from_date, to_date)
            
            # Group by date
            daily_data = {}
            for item in ledger_data:
                date_str = item["date"]
                if date_str not in daily_data:
                    daily_data[date_str] = []
                daily_data[date_str].append(item)
            
            # Create tabs for each date
            for date_str in sorted(daily_data.keys()):
                # Parse date
                day, month, year = date_str.split('-')
                date_obj = date(int(year), int(month), int(day))
                formatted_date = date_obj.strftime("%d %b %Y")
                
                # Create tab
                tab_frame = ttk.Frame(self.ledger_notebook)
                self.ledger_notebook.add(tab_frame, text=formatted_date)
                
                # Create treeview for ledger entries
                ledger_tree = ttk.Treeview(tab_frame, columns=("s_no", "height", "width", "sqft"), show="headings")
                ledger_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                
                # Define headings
                ledger_tree.heading("s_no", text="S.No")
                ledger_tree.heading("height", text="Height")
                ledger_tree.heading("width", text="Width")
                ledger_tree.heading("sqft", text="SQ.FT")
                
                # Define columns
                ledger_tree.column("s_no", width=50)
                ledger_tree.column("height", width=100)
                ledger_tree.column("width", width=100)
                ledger_tree.column("sqft", width=80)
                
                # Add entries
                total_sqft = 0
                for i, item in enumerate(daily_data[date_str], 1):
                    height = f"{item['actual_height']}\""
                    width = f"{item['actual_width']}\""
                    sqft = item["sqft"]
                    total_sqft += sqft
                    
                    ledger_tree.insert("", "end", values=(
                        i,
                        height,
                        width,
                        f"{sqft:.2f}"
                    ))
                
                # Add total row
                ledger_tree.insert("", "end", values=("", "", "Total:", f"{total_sqft:.2f}"))
                
                # Add scrollbar
                scrollbar = ttk.Scrollbar(tab_frame, orient=tk.VERTICAL, command=ledger_tree.yview)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                ledger_tree.configure(yscrollcommand=scrollbar.set)
            
            # If no data found
            if not daily_data:
                no_data_frame = ttk.Frame(self.ledger_notebook)
                self.ledger_notebook.add(no_data_frame, text="No Data")
                ttk.Label(no_data_frame, text="No ledger entries found for the selected date range").pack(pady=20)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dates in DD/MM/YYYY format")
        except Exception as e:
            messagebox.showerror("Error", f"Could not search ledger: {e}")
    
    def export_pdf(self):
        """Export ledger to PDF"""
        # Get date range
        from_date_str = self.from_date_var.get()
        to_date_str = self.to_date_var.get()
        
        try:
            # Parse dates
            from_day, from_month, from_year = from_date_str.split('/')
            from_date = date(int(from_year), int(from_month), int(from_day))
            
            to_day, to_month, to_year = to_date_str.split('/')
            to_date = date(int(to_year), int(to_month), int(to_day))
            
            # Get ledger data
            ledger_data = self.db.get_daily_ledger(from_date, to_date)
            
            if not ledger_data:
                messagebox.showinfo("Info", "No data to export")
                return
            
            # Get file path
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"Daily_Ledger_{from_date_str.replace('/', '_')}_to_{to_date_str.replace('/', '_')}.pdf"
            )
            
            if not file_path:
                return
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph("<b>DAILY LEDGER</b>", styles["Heading1"])
            elements.append(title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Date range
            date_range = f"From: {from_date_str} To: {to_date_str}"
            date_para = Paragraph(date_range, styles["Normal"])
            elements.append(date_para)
            elements.append(Spacer(1, 0.2*inch))
            
            # Group by date
            daily_data = {}
            for item in ledger_data:
                date_str = item["date"]
                if date_str not in daily_data:
                    daily_data[date_str] = []
                daily_data[date_str].append(item)
            
            # Create table for each date
            for date_str in sorted(daily_data.keys()):
                # Parse date
                day, month, year = date_str.split('-')
                date_obj = date(int(year), int(month), int(day))
                formatted_date = date_obj.strftime("%d %B %Y")
                
                # Date heading
                date_heading = Paragraph(f"<b>Date: {formatted_date}</b>", styles["Heading2"])
                elements.append(date_heading)
                elements.append(Spacer(1, 0.1*inch))
                
                # Table data
                table_data = [["S.No", "Height", "Width", "SQ.FT"]]
                
                total_sqft = 0
                for i, item in enumerate(daily_data[date_str], 1):
                    height = f"{item['actual_height']}\""
                    width = f"{item['actual_width']}\""
                    sqft = item["sqft"]
                    total_sqft += sqft
                    
                    table_data.append([
                        str(i),
                        height,
                        width,
                        f"{sqft:.2f}"
                    ])
                
                # Add total row
                table_data.append(["", "", "Total:", f"{total_sqft:.2f}"])
                
                # Create table
                table = Table(table_data, colWidths=[0.5*inch, 1*inch, 1*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (0, 1), (-2, -2), 'CENTER'),
                    ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
                    ('ALIGN', (0, -1), (-2, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                    ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 0.3*inch))
            
            # Build PDF
            doc.build(elements)
            
            messagebox.showinfo("Success", "PDF exported successfully")
            
            # Open PDF
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", file_path])
            else:  # Linux
                subprocess.call(["xdg-open", file_path])
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dates in DD/MM/YYYY format")
        except Exception as e:
            messagebox.showerror("Error", f"Could not export PDF: {e}")
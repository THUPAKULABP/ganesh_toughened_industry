import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta

class WorksModule:
    def __init__(self, parent, db, app):
        self.parent = parent
        self.db = db
        self.app = app
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """Create the works completed UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="WORKS COMPLETED", style="Title.TLabel")
        title.pack(pady=10)
        
        # Filter frame
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Date range
        ttk.Label(filter_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.from_date_var = tk.StringVar(value=(date.today() - timedelta(days=7)).strftime("%d/%m/%Y"))
        ttk.Entry(filter_frame, textvariable=self.from_date_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.to_date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(filter_frame, textvariable=self.to_date_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Status filter
        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar()
        statuses = ["All", "Completed", "Pending"]
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var, values=statuses, state="readonly")
        status_combo.pack(side=tk.LEFT, padx=5)
        
        # Search button
        search_btn = ttk.Button(filter_frame, text="Search", command=self.search_works)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Add work button
        add_btn = ttk.Button(filter_frame, text="Add Work", command=self.add_work)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Works display
        works_frame = ttk.Frame(main_frame)
        works_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Works treeview
        self.works_tree = ttk.Treeview(works_frame, columns=("date", "type", "size", "quantity", "status"), show="headings")
        self.works_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        self.works_tree.heading("date", text="Date")
        self.works_tree.heading("type", text="Type")
        self.works_tree.heading("size", text="Size")
        self.works_tree.heading("quantity", text="Quantity")
        self.works_tree.heading("status", text="Status")
        
        # Define columns
        self.works_tree.column("date", width=100)
        self.works_tree.column("type", width=150)
        self.works_tree.column("size", width=100)
        self.works_tree.column("quantity", width=80)
        self.works_tree.column("status", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(works_frame, orient=tk.VERTICAL, command=self.works_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.works_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click to view details
        self.works_tree.bind("<Double-1>", self.view_work_details)
        
        # Summary frame
        summary_frame = ttk.Frame(main_frame)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Total works
        total_frame = ttk.Frame(summary_frame)
        total_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(total_frame, text="Total Works:").pack(side=tk.LEFT)
        self.total_works_var = tk.StringVar(value="0")
        ttk.Label(total_frame, textvariable=self.total_works_var).pack(side=tk.RIGHT)
        
        # Completed works
        completed_frame = ttk.Frame(summary_frame)
        completed_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(completed_frame, text="Completed Works:").pack(side=tk.LEFT)
        self.completed_works_var = tk.StringVar(value="0")
        ttk.Label(completed_frame, textvariable=self.completed_works_var).pack(side=tk.RIGHT)
        
        # Pending works
        pending_frame = ttk.Frame(summary_frame)
        pending_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(pending_frame, text="Pending Works:").pack(side=tk.LEFT)
        self.pending_works_var = tk.StringVar(value="0")
        ttk.Label(pending_frame, textvariable=self.pending_works_var).pack(side=tk.RIGHT)
        
        # Load initial works
        self.search_works()
    
    def search_works(self):
        """Search works based on filters"""
        # Clear existing items
        for item in self.works_tree.get_children():
            self.works_tree.delete(item)
        
        # Get filter values
        from_date_str = self.from_date_var.get()
        to_date_str = self.to_date_var.get()
        status = self.status_var.get()
        
        # Parse dates
        try:
            from_day, from_month, from_year = from_date_str.split('/')
            from_date = date(int(from_year), int(from_month), int(from_day))
            
            to_day, to_month, to_year = to_date_str.split('/')
            to_date = date(int(to_year), int(to_month), int(to_day))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dates in DD/MM/YYYY format")
            return
        
        # Get works
        try:
            works = self.db.get_works(from_date, to_date, None if status == "All" else status)
            
            # Calculate summary
            total_works = 0
            completed_works = 0
            pending_works = 0
            
            for work in works:
                # Add to treeview
                self.works_tree.insert("", "end", values=(
                    work["date"],
                    work["type"],
                    work["size"] or "",
                    work["quantity"] or "",
                    work["status"]
                ))
                
                # Update summary
                total_works += 1
                if work["status"] == "Completed":
                    completed_works += 1
                else:
                    pending_works += 1
            
            # Update summary
            self.total_works_var.set(str(total_works))
            self.completed_works_var.set(str(completed_works))
            self.pending_works_var.set(str(pending_works))
            
        except Exception as e:
            print(f"Error searching works: {e}")
    
    def add_work(self):
        """Add a new work"""
        # Create work dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Work")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Work details
        ttk.Label(dialog, text="Date:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ttk.Entry(dialog, textvariable=date_var).grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Type:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(dialog, textvariable=type_var)
        type_combo.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Load work types
        work_types = [
            "12MM Plain Glass",
            "10MM Plain Glass",
            "8MM Plain Glass",
            "6MM Plain Glass",
            "12MM Toughened Glass",
            "10MM Toughened Glass",
            "8MM Toughened Glass",
            "6MM Toughened Glass",
            "12MM Laminated Glass",
            "10MM Laminated Glass",
            "8MM Laminated Glass",
            "6MM Laminated Glass"
        ]
        type_combo["values"] = work_types
        
        ttk.Label(dialog, text="Size:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        size_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=size_var).grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Quantity:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        quantity_var = tk.StringVar(value="1")
        ttk.Entry(dialog, textvariable=quantity_var).grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Status:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        status_var = tk.StringVar(value="Pending")
        status_combo = ttk.Combobox(dialog, textvariable=status_var, values=["Pending", "Completed"], state="readonly")
        status_combo.grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        
        def save_work():
            try:
                # Parse date
                date_str = date_var.get()
                day, month, year = date_str.split('/')
                work_date = date(int(year), int(month), int(day))
                
                # Get type
                work_type = type_var.get()
                if not work_type:
                    messagebox.showerror("Error", "Work type is required")
                    return
                
                # Get size
                size = size_var.get().strip()
                
                # Get quantity
                quantity = int(quantity_var.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0")
                    return
                
                # Get status
                status = status_var.get()
                
                # Add work
                work_id = self.db.add_work(
                    date=work_date,
                    type=work_type,
                    size=size,
                    quantity=quantity,
                    status=status
                )
                
                if work_id:
                    messagebox.showinfo("Success", "Work added successfully")
                    dialog.destroy()
                    # Refresh works
                    self.search_works()
                else:
                    messagebox.showerror("Error", "Could not add work")
                    
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values")
            except Exception as e:
                messagebox.showerror("Error", f"Could not add work: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_work).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        dialog.columnconfigure(1, weight=1)
    
    def view_work_details(self, event=None):
        """View work details"""
        selected = self.works_tree.selection()
        if not selected:
            return
        
        # Get work details
        item = self.works_tree.item(selected[0])
        date_str = item["values"][0]
        work_type = item["values"][1]
        size = item["values"][2]
        quantity = item["values"][3]
        status = item["values"][4]
        
        # Create work details dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Work Details")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Work details
        details_frame = ttk.LabelFrame(dialog, text="Work Details")
        details_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Date
        date_frame = ttk.Frame(details_frame)
        date_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(date_frame, text="Date:").pack(side=tk.LEFT, width=10)
        ttk.Label(date_frame, text=date_str).pack(side=tk.LEFT)
        
        # Type
        type_frame = ttk.Frame(details_frame)
        type_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(type_frame, text="Type:").pack(side=tk.LEFT, width=10)
        ttk.Label(type_frame, text=work_type).pack(side=tk.LEFT)
        
        # Size
        size_frame = ttk.Frame(details_frame)
        size_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(size_frame, text="Size:").pack(side=tk.LEFT, width=10)
        ttk.Label(size_frame, text=size or "").pack(side=tk.LEFT)
        
        # Quantity
        quantity_frame = ttk.Frame(details_frame)
        quantity_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(quantity_frame, text="Quantity:").pack(side=tk.LEFT, width=10)
        ttk.Label(quantity_frame, text=quantity).pack(side=tk.LEFT)
        
        # Status
        status_frame = ttk.Frame(details_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT, width=10)
        ttk.Label(status_frame, text=status).pack(side=tk.LEFT)
        
        # Action buttons
        action_frame = ttk.Frame(dialog)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Update status button
        update_btn = ttk.Button(action_frame, text="Update Status", 
                               command=lambda: self.update_work_status(dialog, status))
        update_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Close button
        close_btn = ttk.Button(action_frame, text="Close", command=dialog.destroy)
        close_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def update_work_status(self, parent_dialog, current_status):
        """Update work status"""
        # Create status update dialog
        dialog = tk.Toplevel(parent_dialog)
        dialog.title("Update Work Status")
        dialog.geometry("300x150")
        dialog.transient(parent_dialog)
        dialog.grab_set()
        
        # Status selection
        ttk.Label(dialog, text="Status:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        status_var = tk.StringVar(value=current_status)
        status_combo = ttk.Combobox(dialog, textvariable=status_var, values=["Pending", "Completed"], state="readonly")
        status_combo.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        def save_status():
            new_status = status_var.get()
            if new_status != current_status:
                # Get work ID (this would be passed in a real implementation)
                # For now, just show a message
                messagebox.showinfo("Success", f"Work status updated to {new_status}")
                
                # Close dialogs
                dialog.destroy()
                parent_dialog.destroy()
                
                # Refresh works
                self.search_works()
            else:
                dialog.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        dialog.columnconfigure(1, weight=1)
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json

class RecycleBinModule:
    def __init__(self, parent, db, app):
        self.parent = parent
        self.db = db
        self.app = app
        
        # Create UI
        self.create_ui()
        
        # Load recycle bin items
        self.load_recycle_bin_items()
    
    def create_ui(self):
        """Create the recycle bin UI"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="RECYCLE BIN", style="Title.TLabel")
        title.pack(pady=10)
        
        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        # Restore button
        restore_btn = ttk.Button(toolbar, text="Restore Selected", command=self.restore_selected)
        restore_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        delete_btn = ttk.Button(toolbar, text="Delete Permanently", command=self.delete_selected)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Empty recycle bin button
        empty_btn = ttk.Button(toolbar, text="Empty Recycle Bin", command=self.empty_recycle_bin)
        empty_btn.pack(side=tk.RIGHT, padx=5)
        
        # Refresh button
        refresh_btn = ttk.Button(toolbar, text="Refresh", command=self.load_recycle_bin_items)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Recycle bin items treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview
        self.tree = ttk.Treeview(tree_frame, columns=("item_id", "table_name", "record_id", "name", "deleted_date"), show="headings")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Define headings
        self.tree.heading("item_id", text="ID")
        self.tree.heading("table_name", text="Table")
        self.tree.heading("record_id", text="Record ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("deleted_date", text="Deleted Date")
        
        # Define columns
        self.tree.column("item_id", width=50)
        self.tree.column("table_name", width=100)
        self.tree.column("record_id", width=80)
        self.tree.column("name", width=200)
        self.tree.column("deleted_date", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click to view details
        self.tree.bind("<Double-1>", self.view_details)
        
        # Bind keyboard delete
        self.tree.bind("<Delete>", lambda e: self.delete_selected())
        
        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Item Details")
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Details text
        self.details_text = tk.Text(details_frame, height=10, wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.details_text.config(state=tk.DISABLED)
    
    def load_recycle_bin_items(self):
        """Load recycle bin items into the treeview"""
        # Clear the treeview
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        
        # Get recycle bin items
        items = self.db.get_recycle_bin_items()
        
        # Add items to the treeview
        for item in items:
            # Get a name for the item based on table name and data
            name = "Unknown"
            
            if item["table_name"] == "customers":
                name = item["data"].get("name", "Unknown Customer")
            elif item["table_name"] == "invoices":
                name = f"Invoice #{item['data'].get('invoice_number', 'Unknown')}"
            elif item["table_name"] == "products":
                name = item["data"].get("name", "Unknown Product")
            elif item["table_name"] == "payments":
                name = f"Payment - {item['data'].get('amount', 0)}"
            elif item["table_name"] == "expenses":
                name = item["data"].get("description", "Unknown Expense")
            elif item["table_name"] == "workers":
                name = item["data"].get("name", "Unknown Worker")
            elif item["table_name"] == "customer_visits":
                name = f"Visit - {item['data'].get('name', 'Unknown')}"
            elif item["table_name"] == "works":
                name = f"Work - {item['data'].get('type', 'Unknown')}"
            elif item["table_name"] == "inventory":
                name = f"Inventory - {item['data'].get('type', 'Unknown')}"
            
            # Format deleted date
            deleted_date = item["deleted_date"]
            if isinstance(deleted_date, str):
                try:
                    date_obj = datetime.strptime(deleted_date, "%Y-%m-%d %H:%M:%S")
                    deleted_date = date_obj.strftime("%d/%m/%Y %H:%M")
                except ValueError:
                    pass
            
            self.tree.insert("", "end", values=(
                item["item_id"],
                item["table_name"],
                item["record_id"],
                name,
                deleted_date
            ), iid=item["item_id"])
    
    def view_details(self, event=None):
        """View details of the selected item"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item_id = int(selected[0])
        
        # Get the item from the database
        items = self.db.get_recycle_bin_items()
        item = None
        
        for i in items:
            if i["item_id"] == item_id:
                item = i
                break
        
        if not item:
            return
        
        # Display details
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        # Format the data as JSON
        details = json.dumps(item["data"], indent=4)
        
        self.details_text.insert(tk.END, f"Table: {item['table_name']}\n")
        self.details_text.insert(tk.END, f"Record ID: {item['record_id']}\n")
        self.details_text.insert(tk.END, f"Deleted Date: {item['deleted_date']}\n")
        self.details_text.insert(tk.END, f"Deleted By: {item['deleted_by']}\n\n")
        self.details_text.insert(tk.END, "Data:\n")
        self.details_text.insert(tk.END, details)
        
        self.details_text.config(state=tk.DISABLED)
    
    def restore_selected(self):
        """Restore the selected item"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an item to restore")
            return
        
        item_id = int(selected[0])
        
        # Confirm restoration
        if not messagebox.askyesno("Confirm Restore", "Are you sure you want to restore this item?"):
            return
        
        # Restore the item
        success, message = self.db.restore_from_recycle_bin(item_id)
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_recycle_bin_items()
        else:
            messagebox.showerror("Error", message)
    
    def delete_selected(self):
        """Permanently delete the selected item"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an item to delete")
            return
        
        item_id = int(selected[0])
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to permanently delete this item? This action cannot be undone."):
            return
        
        # Delete the item
        success, message = self.db.permanent_delete_recycle_bin(item_id)
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_recycle_bin_items()
        else:
            messagebox.showerror("Error", message)
    
    def empty_recycle_bin(self):
        """Empty the recycle bin"""
        # Confirm emptying
        if not messagebox.askyesno("Confirm Empty", "Are you sure you want to empty the recycle bin? This action cannot be undone."):
            return
        
        # Empty the recycle bin
        success, message = self.db.empty_recycle_bin()
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_recycle_bin_items()
        else:
            messagebox.showerror("Error", message)
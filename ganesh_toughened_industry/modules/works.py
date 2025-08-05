import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3  # Add this import
from theme import ClaymorphismTheme

class WorksModule:
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
            text="Works Management", 
            height=80
        )
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Content area
        content_frame = tk.Frame(main_container, bg=ClaymorphismTheme.BG_PRIMARY)
        content_frame.pack(fill="both", expand=True)
        
        # Left panel - Works list
        left_panel = tk.Frame(content_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Search and filter
        search_frame, search_card = ClaymorphismTheme.create_card(left_panel, height=100)
        search_frame.pack(fill="x", pady=(0, 10))
        
        # Date range
        from_label = tk.Label(search_card, text="From:", bg=ClaymorphismTheme.BG_CARD, 
                            font=ClaymorphismTheme.FONT_NORMAL)
        from_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.from_date_frame, self.from_date = ClaymorphismTheme.create_entry(search_card, width=15)
        self.from_date_frame.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        to_label = tk.Label(search_card, text="To:", bg=ClaymorphismTheme.BG_CARD, 
                          font=ClaymorphismTheme.FONT_NORMAL)
        to_label.grid(row=0, column=2, sticky="w", padx=10, pady=5)
        
        self.to_date_frame, self.to_date = ClaymorphismTheme.create_entry(search_card, width=15)
        self.to_date_frame.grid(row=0, column=3, sticky="w", padx=10, pady=5)
        
        # Status filter
        status_label = tk.Label(search_card, text="Status:", bg=ClaymorphismTheme.BG_CARD, 
                              font=ClaymorphismTheme.FONT_NORMAL)
        status_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.status_frame, self.status_combo = ClaymorphismTheme.create_combobox(search_card, width=15)
        self.status_frame.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        self.status_combo['values'] = ("All", "Pending", "In Progress", "Completed")
        self.status_combo.current(0)
        
        # Search button
        search_btn_frame, search_btn = ClaymorphismTheme.create_button(
            search_card, 
            text="Search",
            command=self.search_works
        )
        search_btn_frame.grid(row=1, column=2, sticky="w", padx=10, pady=5)
        
        # Clear button
        clear_btn_frame, clear_btn = ClaymorphismTheme.create_button(
            search_card, 
            text="Clear",
            command=self.clear_search
        )
        clear_btn_frame.grid(row=1, column=3, sticky="w", padx=10, pady=5)
        
        # New work button
        new_btn_frame, new_btn = ClaymorphismTheme.create_button(
            search_card, 
            text="New Work",
            command=self.new_work
        )
        new_btn_frame.grid(row=1, column=4, sticky="w", padx=10, pady=5)
        
        # Works list
        list_frame, list_card = ClaymorphismTheme.create_card(left_panel)
        list_frame.pack(fill="both", expand=True)
        
        # Treeview for works
        self.works_tree = ttk.Treeview(list_card, columns=("ID", "Date", "Type", "Size", "Quantity", "Status", "Invoice"), show="headings")
        self.works_tree.heading("ID", text="ID")
        self.works_tree.heading("Date", text="Date")
        self.works_tree.heading("Type", text="Type")
        self.works_tree.heading("Size", text="Size")
        self.works_tree.heading("Quantity", text="Quantity")
        self.works_tree.heading("Status", text="Status")
        self.works_tree.heading("Invoice", text="Invoice")
        
        self.works_tree.column("ID", width=50)
        self.works_tree.column("Date", width=100)
        self.works_tree.column("Type", width=100)
        self.works_tree.column("Size", width=100)
        self.works_tree.column("Quantity", width=80)
        self.works_tree.column("Status", width=100)
        self.works_tree.column("Invoice", width=120)
        
        self.works_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.works_tree.bind("<<TreeviewSelect>>", self.on_work_select)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_card, orient="vertical", command=self.works_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.works_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = tk.Frame(left_panel, bg=ClaymorphismTheme.BG_PRIMARY)
        button_frame.pack(fill="x", pady=10)
        
        view_btn_frame, view_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="View Details",
            command=self.view_work_details
        )
        view_btn_frame.pack(side="left", padx=5)
        
        edit_btn_frame, edit_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Edit Work",
            command=self.edit_work
        )
        edit_btn_frame.pack(side="left", padx=5)
        
        delete_btn_frame, delete_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Delete Work",
            command=self.delete_work
        )
        delete_btn_frame.pack(side="left", padx=5)
        
        refresh_btn_frame, refresh_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Refresh",
            command=self.load_works
        )
        refresh_btn_frame.pack(side="left", padx=5)
        
        # Right panel - Work details
        right_panel = tk.Frame(content_frame, bg=ClaymorphismTheme.BG_PRIMARY, width=400)
        right_panel.pack(side="right", fill="both")
        right_panel.pack_propagate(False)
        
        # Work details card
        details_frame, details_card = ClaymorphismTheme.create_card(right_panel, text="Work Details")
        details_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initially show a placeholder
        placeholder_label = tk.Label(details_card, text="Select a work to view details", 
                                   bg=ClaymorphismTheme.BG_CARD, 
                                   font=ClaymorphismTheme.FONT_SUBTITLE,
                                   fg=ClaymorphismTheme.TEXT_SECONDARY)
        placeholder_label.pack(pady=50)
        
        self.details_content = placeholder_label
        
        # Load works
        self.load_works()
    
    def load_works(self):
        """Load works into the treeview"""
        # Clear existing items
        for item in self.works_tree.get_children():
            self.works_tree.delete(item)
        
        # Get works from database
        works = self.db.get_works()
        
        # Add works to treeview
        for work in works:
            self.works_tree.insert("", "end", values=(
                work["work_id"],
                work["date"].strftime("%Y-%m-%d"),
                work["type"] or "",
                work["size"] or "",
                work["quantity"] or 0,
                work["status"] or "",
                work["invoice_number"] or ""
            ))
    
    def search_works(self):
        """Search works based on criteria"""
        from_date_str = self.from_date.get().strip()
        to_date_str = self.to_date.get().strip()
        status = self.status_combo.get()
        
        from_date = None
        to_date = None
        
        if from_date_str:
            try:
                from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showwarning("Invalid Date", "Please enter a valid from date in YYYY-MM-DD format.")
                return
        
        if to_date_str:
            try:
                to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showwarning("Invalid Date", "Please enter a valid to date in YYYY-MM-DD format.")
                return
        
        if status == "All":
            status = None
        
        # Clear existing items
        for item in self.works_tree.get_children():
            self.works_tree.delete(item)
        
        # Get works from database
        works = self.db.get_works(from_date=from_date, to_date=to_date, status=status)
        
        # Add works to treeview
        for work in works:
            self.works_tree.insert("", "end", values=(
                work["work_id"],
                work["date"].strftime("%Y-%m-%d"),
                work["type"] or "",
                work["size"] or "",
                work["quantity"] or 0,
                work["status"] or "",
                work["invoice_number"] or ""
            ))
    
    def clear_search(self):
        """Clear search fields"""
        self.from_date.delete(0, "end")
        self.to_date.delete(0, "end")
        self.status_combo.current(0)
        self.load_works()
    
    def on_work_select(self, event):
        """Handle work selection"""
        selected_items = self.works_tree.selection()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        work_id = self.works_tree.item(selected_item, "values")[0]
        
        # Get work details
        works = self.db.get_works()
        work = next((w for w in works if w["work_id"] == int(work_id)), None)
        
        if work:
            self.display_work_details(work)
    
    def display_work_details(self, work):
        """Display work details in the right panel"""
        # Clear existing content
        if self.details_content:
            self.details_content.destroy()
        
        # Create details frame
        details_frame = tk.Frame(self.parent, bg=ClaymorphismTheme.BG_CARD)
        self.details_content = details_frame
        
        # Work header
        header_frame = tk.Frame(details_frame, bg=ClaymorphismTheme.BG_CARD)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Work ID and date
        work_id_label = tk.Label(header_frame, text=f"Work ID: {work['work_id']}", 
                                bg=ClaymorphismTheme.BG_CARD, 
                                font=ClaymorphismTheme.FONT_SUBTITLE,
                                fg=ClaymorphismTheme.TEXT_PRIMARY)
        work_id_label.pack(side="left")
        
        work_date_label = tk.Label(header_frame, text=f"Date: {work['date'].strftime('%d-%m-%Y')}", 
                                 bg=ClaymorphismTheme.BG_CARD, 
                                 font=ClaymorphismTheme.FONT_NORMAL,
                                 fg=ClaymorphismTheme.TEXT_SECONDARY)
        work_date_label.pack(side="right")
        
        # Work details
        details_container = tk.Frame(details_frame, bg=ClaymorphismTheme.BG_CARD)
        details_container.pack(fill="x", padx=10, pady=5)
        
        # Type
        type_label = tk.Label(details_container, text="Type:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_SUBTITLE,
                             fg=ClaymorphismTheme.TEXT_PRIMARY)
        type_label.pack(anchor="w")
        
        type_text = tk.Label(details_container, text=work["type"] or "Not specified", 
                            bg=ClaymorphismTheme.BG_CARD, 
                            font=ClaymorphismTheme.FONT_NORMAL,
                            fg=ClaymorphismTheme.TEXT_PRIMARY)
        type_text.pack(anchor="w", padx=20)
        
        # Size
        size_label = tk.Label(details_container, text="Size:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_SUBTITLE,
                             fg=ClaymorphismTheme.TEXT_PRIMARY)
        size_label.pack(anchor="w")
        
        size_text = tk.Label(details_container, text=work["size"] or "Not specified", 
                            bg=ClaymorphismTheme.BG_CARD, 
                            font=ClaymorphismTheme.FONT_NORMAL,
                            fg=ClaymorphismTheme.TEXT_PRIMARY)
        size_text.pack(anchor="w", padx=20)
        
        # Quantity
        qty_label = tk.Label(details_container, text="Quantity:", bg=ClaymorphismTheme.BG_CARD, 
                            font=ClaymorphismTheme.FONT_SUBTITLE,
                            fg=ClaymorphismTheme.TEXT_PRIMARY)
        qty_label.pack(anchor="w")
        
        qty_text = tk.Label(details_container, text=str(work["quantity"] or 0), 
                           bg=ClaymorphismTheme.BG_CARD, 
                           font=ClaymorphismTheme.FONT_NORMAL,
                           fg=ClaymorphismTheme.TEXT_PRIMARY)
        qty_text.pack(anchor="w", padx=20)
        
        # Status
        status_label = tk.Label(details_container, text="Status:", bg=ClaymorphismTheme.BG_CARD, 
                              font=ClaymorphismTheme.FONT_SUBTITLE,
                              fg=ClaymorphismTheme.TEXT_PRIMARY)
        status_label.pack(anchor="w")
        
        status_text = tk.Label(details_container, text=work["status"] or "Not specified", 
                              bg=ClaymorphismTheme.BG_CARD, 
                              font=ClaymorphismTheme.FONT_NORMAL,
                              fg=ClaymorphismTheme.TEXT_PRIMARY)
        status_text.pack(anchor="w", padx=20)
        
        # Invoice
        if work["invoice_number"]:
            invoice_label = tk.Label(details_container, text="Invoice:", bg=ClaymorphismTheme.BG_CARD, 
                                   font=ClaymorphismTheme.FONT_SUBTITLE,
                                   fg=ClaymorphismTheme.TEXT_PRIMARY)
            invoice_label.pack(anchor="w")
            
            invoice_text = tk.Label(details_container, text=work["invoice_number"], 
                                   bg=ClaymorphismTheme.BG_CARD, 
                                   font=ClaymorphismTheme.FONT_NORMAL,
                                   fg=ClaymorphismTheme.TEXT_PRIMARY)
            invoice_text.pack(anchor="w", padx=20)
        
        # Store current work
        self.current_work = work
    
    def new_work(self):
        """Open dialog to create a new work"""
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("New Work")
        dialog.geometry("500x400")
        dialog.configure(bg=ClaymorphismTheme.BG_PRIMARY)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Form frame
        form_frame = tk.Frame(dialog, bg=ClaymorphismTheme.BG_PRIMARY)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Invoice selection
        invoice_label = tk.Label(form_frame, text="Invoice (Optional):", bg=ClaymorphismTheme.BG_PRIMARY, 
                               font=ClaymorphismTheme.FONT_NORMAL)
        invoice_label.grid(row=0, column=0, sticky="w", pady=5)
        
        invoice_combo_frame, invoice_combo = ClaymorphismTheme.create_combobox(form_frame, width=30)
        invoice_combo_frame.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Get invoices and populate combobox
        invoices = self.db.get_invoices()
        invoice_numbers = [f"{inv['invoice_id']} - {inv['invoice_number']}" for inv in invoices]
        invoice_combo['values'] = invoice_numbers
        
        # Date
        date_label = tk.Label(form_frame, text="Date:", bg=ClaymorphismTheme.BG_PRIMARY, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        date_label.grid(row=1, column=0, sticky="w", pady=5)
        
        date_entry_frame, date_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        date_entry_frame.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Set today's date
        today = datetime.now().strftime("%Y-%m-%d")
        date_entry.insert(0, today)
        
        # Type
        type_label = tk.Label(form_frame, text="Type:", bg=ClaymorphismTheme.BG_PRIMARY, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        type_label.grid(row=2, column=0, sticky="w", pady=5)
        
        type_entry_frame, type_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        type_entry_frame.grid(row=2, column=1, sticky="ew", pady=5)
        
        # Size
        size_label = tk.Label(form_frame, text="Size:", bg=ClaymorphismTheme.BG_PRIMARY, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        size_label.grid(row=3, column=0, sticky="w", pady=5)
        
        size_entry_frame, size_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        size_entry_frame.grid(row=3, column=1, sticky="ew", pady=5)
        
        # Quantity
        qty_label = tk.Label(form_frame, text="Quantity:", bg=ClaymorphismTheme.BG_PRIMARY, 
                            font=ClaymorphismTheme.FONT_NORMAL)
        qty_label.grid(row=4, column=0, sticky="w", pady=5)
        
        qty_entry_frame, qty_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        qty_entry_frame.grid(row=4, column=1, sticky="ew", pady=5)
        
        # Status
        status_label = tk.Label(form_frame, text="Status:", bg=ClaymorphismTheme.BG_PRIMARY, 
                              font=ClaymorphismTheme.FONT_NORMAL)
        status_label.grid(row=5, column=0, sticky="w", pady=5)
        
        status_combo_frame, status_combo = ClaymorphismTheme.create_combobox(form_frame, width=30)
        status_combo_frame.grid(row=5, column=1, sticky="ew", pady=5)
        status_combo['values'] = ("Pending", "In Progress", "Completed")
        status_combo.current(0)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        save_btn_frame, save_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Save Work",
            command=lambda: self.save_work(
                dialog, invoice_combo, date_entry, type_entry, size_entry, qty_entry, status_combo, invoices
            )
        )
        save_btn_frame.pack(side="left", padx=5)
        
        cancel_btn_frame, cancel_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Cancel",
            command=dialog.destroy
        )
        cancel_btn_frame.pack(side="left", padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
    
    def save_work(self, dialog, invoice_combo, date_entry, type_entry, size_entry, qty_entry, status_combo, invoices):
        """Save work to database"""
        # Get form data
        invoice_str = invoice_combo.get()
        date_str = date_entry.get().strip()
        work_type = type_entry.get().strip()
        size = size_entry.get().strip()
        qty_str = qty_entry.get().strip()
        status = status_combo.get()
        
        # Validate form
        if not date_str:
            messagebox.showwarning("Validation Error", "Date is required.")
            return
        
        if not work_type:
            messagebox.showwarning("Validation Error", "Type is required.")
            return
        
        if not qty_str:
            messagebox.showwarning("Validation Error", "Quantity is required.")
            return
        
        try:
            work_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter a valid date in YYYY-MM-DD format.")
            return
        
        try:
            quantity = int(qty_str)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation Error", "Quantity must be a positive integer.")
            return
        
        # Get invoice ID if selected
        invoice_id = None
        if invoice_str:
            invoice_id = int(invoice_str.split(" - ")[0])
        
        # Add work to database
        work_id = self.db.add_work(invoice_id, work_date, work_type, size, quantity, status)
        
        if work_id:
            messagebox.showinfo("Success", "Work added successfully.")
            dialog.destroy()
            self.load_works()
        else:
            messagebox.showerror("Error", "Failed to add work.")
    
    def view_work_details(self):
        """View selected work details"""
        selected_items = self.works_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a work to view.")
            return
        
        # Get work details
        selected_item = selected_items[0]
        work_id = self.works_tree.item(selected_item, "values")[0]
        
        works = self.db.get_works()
        work = next((w for w in works if w["work_id"] == int(work_id)), None)
        
        if work:
            self.display_work_details(work)
    
    def edit_work(self):
        """Edit selected work"""
        selected_items = self.works_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a work to edit.")
            return
        
        # Get work details
        selected_item = selected_items[0]
        work_id = self.works_tree.item(selected_item, "values")[0]
        
        works = self.db.get_works()
        work = next((w for w in works if w["work_id"] == int(work_id)), None)
        
        if not work:
            return
        
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Work")
        dialog.geometry("500x400")
        dialog.configure(bg=ClaymorphismTheme.BG_PRIMARY)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Form frame
        form_frame = tk.Frame(dialog, bg=ClaymorphismTheme.BG_PRIMARY)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Invoice selection
        invoice_label = tk.Label(form_frame, text="Invoice (Optional):", bg=ClaymorphismTheme.BG_PRIMARY, 
                               font=ClaymorphismTheme.FONT_NORMAL)
        invoice_label.grid(row=0, column=0, sticky="w", pady=5)
        
        invoice_combo_frame, invoice_combo = ClaymorphismTheme.create_combobox(form_frame, width=30)
        invoice_combo_frame.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Get invoices and populate combobox
        invoices = self.db.get_invoices()
        invoice_numbers = [f"{inv['invoice_id']} - {inv['invoice_number']}" for inv in invoices]
        invoice_combo['values'] = invoice_numbers
        
        # Set current invoice if available
        if work["invoice_id"]:
            invoice = next((inv for inv in invoices if inv["invoice_id"] == work["invoice_id"]), None)
            if invoice:
                invoice_combo.set(f"{invoice['invoice_id']} - {invoice['invoice_number']}")
        
        # Date
        date_label = tk.Label(form_frame, text="Date:", bg=ClaymorphismTheme.BG_PRIMARY, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        date_label.grid(row=1, column=0, sticky="w", pady=5)
        
        date_entry_frame, date_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        date_entry_frame.grid(row=1, column=1, sticky="ew", pady=5)
        date_entry.insert(0, work["date"].strftime("%Y-%m-%d"))
        
        # Type
        type_label = tk.Label(form_frame, text="Type:", bg=ClaymorphismTheme.BG_PRIMARY, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        type_label.grid(row=2, column=0, sticky="w", pady=5)
        
        type_entry_frame, type_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        type_entry_frame.grid(row=2, column=1, sticky="ew", pady=5)
        type_entry.insert(0, work["type"] or "")
        
        # Size
        size_label = tk.Label(form_frame, text="Size:", bg=ClaymorphismTheme.BG_PRIMARY, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        size_label.grid(row=3, column=0, sticky="w", pady=5)
        
        size_entry_frame, size_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        size_entry_frame.grid(row=3, column=1, sticky="ew", pady=5)
        size_entry.insert(0, work["size"] or "")
        
        # Quantity
        qty_label = tk.Label(form_frame, text="Quantity:", bg=ClaymorphismTheme.BG_PRIMARY, 
                            font=ClaymorphismTheme.FONT_NORMAL)
        qty_label.grid(row=4, column=0, sticky="w", pady=5)
        
        qty_entry_frame, qty_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        qty_entry_frame.grid(row=4, column=1, sticky="ew", pady=5)
        qty_entry.insert(0, str(work["quantity"] or 0))
        
        # Status
        status_label = tk.Label(form_frame, text="Status:", bg=ClaymorphismTheme.BG_PRIMARY, 
                              font=ClaymorphismTheme.FONT_NORMAL)
        status_label.grid(row=5, column=0, sticky="w", pady=5)
        
        status_combo_frame, status_combo = ClaymorphismTheme.create_combobox(form_frame, width=30)
        status_combo_frame.grid(row=5, column=1, sticky="ew", pady=5)
        status_combo['values'] = ("Pending", "In Progress", "Completed")
        status_combo.set(work["status"] or "Pending")
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        save_btn_frame, save_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Save Changes",
            command=lambda: self.update_work(
                dialog, work_id, invoice_combo, date_entry, type_entry, size_entry, qty_entry, status_combo, invoices
            )
        )
        save_btn_frame.pack(side="left", padx=5)
        
        cancel_btn_frame, cancel_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Cancel",
            command=dialog.destroy
        )
        cancel_btn_frame.pack(side="left", padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
    
    def update_work(self, dialog, work_id, invoice_combo, date_entry, type_entry, size_entry, qty_entry, status_combo, invoices):
        """Update work in database"""
        # Get form data
        invoice_str = invoice_combo.get()
        date_str = date_entry.get().strip()
        work_type = type_entry.get().strip()
        size = size_entry.get().strip()
        qty_str = qty_entry.get().strip()
        status = status_combo.get()
        
        # Validate form
        if not date_str:
            messagebox.showwarning("Validation Error", "Date is required.")
            return
        
        if not work_type:
            messagebox.showwarning("Validation Error", "Type is required.")
            return
        
        if not qty_str:
            messagebox.showwarning("Validation Error", "Quantity is required.")
            return
        
        try:
            work_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter a valid date in YYYY-MM-DD format.")
            return
        
        try:
            quantity = int(qty_str)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation Error", "Quantity must be a positive integer.")
            return
        
        # Get invoice ID if selected
        invoice_id = None
        if invoice_str:
            invoice_id = int(invoice_str.split(" - ")[0])
        
        # Update work in database
        try:
            conn = sqlite3.connect(self.db.db_name)
            cursor = conn.cursor()
            
            query = """
            UPDATE works
            SET invoice_id = ?, date = ?, type = ?, size = ?, quantity = ?, status = ?
            WHERE work_id = ?
            """
            
            cursor.execute(query, (invoice_id, work_date.strftime("%Y-%m-%d"), work_type, size, quantity, status, work_id))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Work updated successfully.")
            dialog.destroy()
            self.load_works()
        except Exception as e:
            print(f"Error updating work: {e}")
            messagebox.showerror("Error", "Failed to update work.")
    
    def delete_work(self):
        """Delete selected work"""
        selected_items = self.works_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a work to delete.")
            return
        
        selected_item = selected_items[0]
        work_id = self.works_tree.item(selected_item, "values")[0]
        work_type = self.works_tree.item(selected_item, "values")[2]
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete this {work_type} work?"):
            # Delete work
            success = self.db.delete_work(int(work_id))
            
            if success:
                messagebox.showinfo("Success", "Work deleted successfully.")
                self.load_works()
                
                # Clear details if this work was being viewed
                if hasattr(self, 'current_work') and self.current_work["work_id"] == int(work_id):
                    if self.details_content:
                        self.details_content.destroy()
                    
                    placeholder_label = tk.Label(self.parent, text="Select a work to view details", 
                                               bg=ClaymorphismTheme.BG_CARD, 
                                               font=ClaymorphismTheme.FONT_SUBTITLE,
                                               fg=ClaymorphismTheme.TEXT_SECONDARY)
                    placeholder_label.pack(pady=50)
                    self.details_content = placeholder_label
            else:
                messagebox.showerror("Error", "Failed to delete work.")
    
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
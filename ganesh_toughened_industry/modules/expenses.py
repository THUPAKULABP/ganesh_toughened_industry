import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3  # Add this import
from theme import ClaymorphismTheme

class ExpensesModule:
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
            text="Expense Management", 
            height=80
        )
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Content area
        content_frame = tk.Frame(main_container, bg=ClaymorphismTheme.BG_PRIMARY)
        content_frame.pack(fill="both", expand=True)
        
        # Left panel - Expense list
        left_panel = tk.Frame(content_frame, bg=ClaymorphismTheme.BG_PRIMARY)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Filter frame
        filter_frame, filter_card = ClaymorphismTheme.create_card(left_panel, height=100)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # From date
        from_label = tk.Label(filter_card, text="From Date:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        from_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.from_date_frame, self.from_date = ClaymorphismTheme.create_entry(filter_card, width=15)
        self.from_date_frame.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # To date
        to_label = tk.Label(filter_card, text="To Date:", bg=ClaymorphismTheme.BG_CARD, 
                           font=ClaymorphismTheme.FONT_NORMAL)
        to_label.grid(row=0, column=2, sticky="w", padx=10, pady=5)
        
        self.to_date_frame, self.to_date = ClaymorphismTheme.create_entry(filter_card, width=15)
        self.to_date_frame.grid(row=0, column=3, sticky="w", padx=10, pady=5)
        
        # Category
        cat_label = tk.Label(filter_card, text="Category:", bg=ClaymorphismTheme.BG_CARD, 
                            font=ClaymorphismTheme.FONT_NORMAL)
        cat_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.cat_frame, self.cat_combo = ClaymorphismTheme.create_combobox(filter_card, width=15)
        self.cat_frame.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        self.cat_combo['values'] = ("All", "Rent", "Utilities", "Salaries", "Materials", "Transport", "Other")
        self.cat_combo.current(0)
        
        # Filter button
        filter_btn_frame, filter_btn = ClaymorphismTheme.create_button(
            filter_card, 
            text="Filter",
            command=self.filter_expenses
        )
        filter_btn_frame.grid(row=1, column=2, sticky="w", padx=10, pady=5)
        
        # Clear button
        clear_btn_frame, clear_btn = ClaymorphismTheme.create_button(
            filter_card, 
            text="Clear",
            command=self.clear_filter
        )
        clear_btn_frame.grid(row=1, column=3, sticky="w", padx=10, pady=5)
        
        # Expense list
        list_frame, list_card = ClaymorphismTheme.create_card(left_panel)
        list_frame.pack(fill="both", expand=True)
        
        # Treeview for expenses
        self.expense_tree = ttk.Treeview(list_card, columns=("ID", "Date", "Description", "Amount", "Category"), show="headings")
        self.expense_tree.heading("ID", text="ID")
        self.expense_tree.heading("Date", text="Date")
        self.expense_tree.heading("Description", text="Description")
        self.expense_tree.heading("Amount", text="Amount")
        self.expense_tree.heading("Category", text="Category")
        
        self.expense_tree.column("ID", width=50)
        self.expense_tree.column("Date", width=100)
        self.expense_tree.column("Description", width=200)
        self.expense_tree.column("Amount", width=100)
        self.expense_tree.column("Category", width=100)
        
        self.expense_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.expense_tree.bind("<<TreeviewSelect>>", self.on_expense_select)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_card, orient="vertical", command=self.expense_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.expense_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = tk.Frame(left_panel, bg=ClaymorphismTheme.BG_PRIMARY)
        button_frame.pack(fill="x", pady=10)
        
        add_btn_frame, add_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Add Expense",
            command=self.add_expense
        )
        add_btn_frame.pack(side="left", padx=5)
        
        edit_btn_frame, edit_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Edit Expense",
            command=self.edit_expense
        )
        edit_btn_frame.pack(side="left", padx=5)
        
        delete_btn_frame, delete_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Delete Expense",
            command=self.delete_expense
        )
        delete_btn_frame.pack(side="left", padx=5)
        
        refresh_btn_frame, refresh_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Refresh",
            command=self.load_expenses
        )
        refresh_btn_frame.pack(side="left", padx=5)
        
        # Right panel - Expense details
        right_panel = tk.Frame(content_frame, bg=ClaymorphismTheme.BG_PRIMARY, width=400)
        right_panel.pack(side="right", fill="both")
        right_panel.pack_propagate(False)
        
        # Expense details card
        details_frame, details_card = ClaymorphismTheme.create_card(right_panel, text="Expense Details")
        details_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Form fields
        form_frame = tk.Frame(details_card, bg=ClaymorphismTheme.BG_CARD)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Date
        date_label = tk.Label(form_frame, text="Date:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        date_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.date_entry_frame, self.date_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        self.date_entry_frame.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Set today's date as default
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today)
        
        # Description
        desc_label = tk.Label(form_frame, text="Description:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        desc_label.grid(row=1, column=0, sticky="nw", pady=5)
        
        self.desc_text = tk.Text(form_frame, height=4, width=30, 
                               bg=ClaymorphismTheme.BG_SECONDARY,
                               fg=ClaymorphismTheme.TEXT_PRIMARY,
                               relief="flat",
                               borderwidth=0,
                               font=ClaymorphismTheme.FONT_NORMAL)
        self.desc_text.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Amount
        amount_label = tk.Label(form_frame, text="Amount:", bg=ClaymorphismTheme.BG_CARD, 
                               font=ClaymorphismTheme.FONT_NORMAL)
        amount_label.grid(row=2, column=0, sticky="w", pady=5)
        
        self.amount_entry_frame, self.amount_entry = ClaymorphismTheme.create_entry(form_frame, width=30)
        self.amount_entry_frame.grid(row=2, column=1, sticky="ew", pady=5)
        
        # Category
        cat_label2 = tk.Label(form_frame, text="Category:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        cat_label2.grid(row=3, column=0, sticky="w", pady=5)
        
        self.cat_frame2, self.cat_combo2 = ClaymorphismTheme.create_combobox(form_frame, width=27)
        self.cat_frame2.grid(row=3, column=1, sticky="ew", pady=5)
        self.cat_combo2['values'] = ("Rent", "Utilities", "Salaries", "Materials", "Transport", "Other")
        
        # Buttons
        button_frame2 = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_CARD)
        button_frame2.grid(row=4, column=0, columnspan=2, pady=10)
        
        save_btn_frame, save_btn = ClaymorphismTheme.create_button(
            button_frame2, 
            text="Save",
            command=self.save_expense
        )
        save_btn_frame.pack(side="left", padx=5)
        
        cancel_btn_frame, cancel_btn = ClaymorphismTheme.create_button(
            button_frame2, 
            text="Cancel",
            command=self.clear_form
        )
        cancel_btn_frame.pack(side="left", padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
        # Load expenses
        self.load_expenses()
        
        # Initially disable form
        self.toggle_form(False)
    
    def load_expenses(self, from_date=None, to_date=None, category=None):
        """Load expenses into the treeview"""
        # Clear existing items
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        
        # Get expenses from database
        expenses = self.db.get_expenses(from_date, to_date, category)
        
        # Add expenses to treeview
        for expense in expenses:
            self.expense_tree.insert("", "end", values=(
                expense["expense_id"],
                expense["date"].strftime("%Y-%m-%d"),
                expense["description"],
                f"₹{expense['amount']:.2f}",
                expense["category"] or ""
            ))
    
    def filter_expenses(self):
        """Filter expenses based on filter criteria"""
        from_date_str = self.from_date.get().strip()
        to_date_str = self.to_date.get().strip()
        category = self.cat_combo.get()
        
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
        
        if category == "All":
            category = None
        
        self.load_expenses(from_date, to_date, category)
    
    def clear_filter(self):
        """Clear filter fields"""
        self.from_date.delete(0, "end")
        self.to_date.delete(0, "end")
        self.cat_combo.current(0)
        self.load_expenses()
    
    def on_expense_select(self, event):
        """Handle expense selection"""
        selected_items = self.expense_tree.selection()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        expense_id = self.expense_tree.item(selected_item, "values")[0]
        
        # Get expense details
        expenses = self.db.get_expenses()
        expense = next((e for e in expenses if e["expense_id"] == int(expense_id)), None)
        
        if expense:
            # Populate form fields
            self.date_entry.delete(0, "end")
            self.date_entry.insert(0, expense["date"].strftime("%Y-%m-%d"))
            
            self.desc_text.delete(1.0, "end")
            self.desc_text.insert(1.0, expense["description"])
            
            self.amount_entry.delete(0, "end")
            self.amount_entry.insert(0, str(expense["amount"]))
            
            self.cat_combo2.set(expense["category"] or "")
            
            # Enable form
            self.toggle_form(True)
            self.current_expense_id = expense["expense_id"]
    
    def add_expense(self):
        """Add a new expense"""
        # Clear form
        self.clear_form()
        
        # Enable form
        self.toggle_form(True)
        
        # Set focus to description
        self.desc_text.focus()
        
        # Set mode to add
        self.mode = "add"
    
    def edit_expense(self):
        """Edit selected expense"""
        selected_items = self.expense_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select an expense to edit.")
            return
        
        # Set mode to edit
        self.mode = "edit"
    
    def delete_expense(self):
        """Delete selected expense"""
        selected_items = self.expense_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select an expense to delete.")
            return
        
        selected_item = selected_items[0]
        expense_id = self.expense_tree.item(selected_item, "values")[0]
        description = self.expense_tree.item(selected_item, "values")[2]
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete this expense: {description}?"):
            # Delete expense
            success = self.db.delete_expense(int(expense_id))
            
            if success:
                messagebox.showinfo("Success", "Expense deleted successfully.")
                self.load_expenses()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to delete expense.")
    
    def save_expense(self):
        """Save expense data"""
        # Get form data
        date_str = self.date_entry.get().strip()
        description = self.desc_text.get(1.0, "end").strip()
        amount_str = self.amount_entry.get().strip()
        category = self.cat_combo2.get()
        
        # Validate form
        if not date_str:
            messagebox.showwarning("Validation Error", "Date is required.")
            return
        
        if not description:
            messagebox.showwarning("Validation Error", "Description is required.")
            return
        
        if not amount_str:
            messagebox.showwarning("Validation Error", "Amount is required.")
            return
        
        if not category:
            messagebox.showwarning("Validation Error", "Category is required.")
            return
        
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter a valid date in YYYY-MM-DD format.")
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation Error", "Amount must be a positive number.")
            return
        
        # Save expense
        if hasattr(self, 'mode') and self.mode == "add":
            # Add new expense
            expense_id = self.db.add_expense(date, description, amount, category)
            
            if expense_id:
                messagebox.showinfo("Success", "Expense added successfully.")
                self.load_expenses()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to add expense.")
        else:
            # Update existing expense
            # Note: Database doesn't have update_expense method, so we'll implement it here
            try:
                conn = sqlite3.connect(self.db.db_name)
                cursor = conn.cursor()
                
                query = """
                UPDATE expenses
                SET date = ?, description = ?, amount = ?, category = ?
                WHERE expense_id = ?
                """
                
                cursor.execute(query, (date.strftime("%Y-%m-%d"), description, amount, category, self.current_expense_id))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Expense updated successfully.")
                self.load_expenses()
                self.clear_form()
            except Exception as e:
                print(f"Error updating expense: {e}")
                messagebox.showerror("Error", "Failed to update expense.")
    
    def clear_form(self):
        """Clear form fields"""
        self.date_entry.delete(0, "end")
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today)
        
        self.desc_text.delete(1.0, "end")
        
        self.amount_entry.delete(0, "end")
        
        self.cat_combo2.set("")
        
        # Disable form
        self.toggle_form(False)
        
        # Clear selection
        for item in self.expense_tree.selection():
            self.expense_tree.selection_remove(item)
    
    def toggle_form(self, enabled):
        """Enable or disable form fields"""
        state = "normal" if enabled else "disabled"
        
        self.date_entry.config(state=state)
        self.desc_text.config(state=state)
        self.amount_entry.config(state=state)
        self.cat_combo2.config(state=state)
    
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
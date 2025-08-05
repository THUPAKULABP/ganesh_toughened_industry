import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
from theme import ClaymorphismTheme

class AttendanceModule:
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
            text="Worker Attendance", 
            height=80
        )
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Content area
        content_frame = tk.Frame(main_container, bg=ClaymorphismTheme.BG_PRIMARY)
        content_frame.pack(fill="both", expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill="both", expand=True)
        
        # Daily attendance tab
        daily_tab = tk.Frame(notebook, bg=ClaymorphismTheme.BG_PRIMARY)
        notebook.add(daily_tab, text="Daily Attendance")
        self.create_daily_tab(daily_tab)
        
        # Workers tab
        workers_tab = tk.Frame(notebook, bg=ClaymorphismTheme.BG_PRIMARY)
        notebook.add(workers_tab, text="Workers")
        self.create_workers_tab(workers_tab)
        
        # Reports tab
        reports_tab = tk.Frame(notebook, bg=ClaymorphismTheme.BG_PRIMARY)
        notebook.add(reports_tab, text="Reports")
        self.create_reports_tab(reports_tab)
    
    def create_daily_tab(self, parent):
        # Main container
        main_container = tk.Frame(parent, bg=ClaymorphismTheme.BG_PRIMARY)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Date selection
        date_frame, date_card = ClaymorphismTheme.create_card(main_container, height=80)
        date_frame.pack(fill="x", pady=(0, 10))
        
        date_label = tk.Label(date_card, text="Select Date:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        date_label.pack(side="left", padx=20, pady=10)
        
        self.date_entry_frame, self.date_entry = ClaymorphismTheme.create_entry(date_card, width=15)
        self.date_entry_frame.pack(side="left", padx=10, pady=10)
        
        # Set today's date
        today = date.today().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today)
        
        # Load button
        load_btn_frame, load_btn = ClaymorphismTheme.create_button(
            date_card, 
            text="Load Attendance",
            command=self.load_daily_attendance
        )
        load_btn_frame.pack(side="left", padx=10, pady=10)
        
        # Save button
        save_btn_frame, save_btn = ClaymorphismTheme.create_button(
            date_card, 
            text="Save Attendance",
            command=self.save_daily_attendance
        )
        save_btn_frame.pack(side="left", padx=10, pady=10)
        
        # Attendance table
        table_frame, table_card = ClaymorphismTheme.create_card(main_container)
        table_frame.pack(fill="both", expand=True)
        
        # Create treeview for attendance
        self.attendance_tree = ttk.Treeview(table_card, columns=("ID", "Worker", "Morning", "Afternoon", "Notes"), show="headings")
        self.attendance_tree.heading("ID", text="ID")
        self.attendance_tree.heading("Worker", text="Worker")
        self.attendance_tree.heading("Morning", text="Morning")
        self.attendance_tree.heading("Afternoon", text="Afternoon")
        self.attendance_tree.heading("Notes", text="Notes")
        
        self.attendance_tree.column("ID", width=50)
        self.attendance_tree.column("Worker", width=200)
        self.attendance_tree.column("Morning", width=100)
        self.attendance_tree.column("Afternoon", width=100)
        self.attendance_tree.column("Notes", width=200)
        
        self.attendance_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.attendance_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)
        
        # Load today's attendance
        self.load_daily_attendance()
    
    def create_workers_tab(self, parent):
        # Main container
        main_container = tk.Frame(parent, bg=ClaymorphismTheme.BG_PRIMARY)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Workers list
        list_frame, list_card = ClaymorphismTheme.create_card(main_container, text="Workers List")
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create treeview for workers
        self.workers_tree = ttk.Treeview(list_card, columns=("ID", "Name", "Phone"), show="headings")
        self.workers_tree.heading("ID", text="ID")
        self.workers_tree.heading("Name", text="Name")
        self.workers_tree.heading("Phone", text="Phone")
        
        self.workers_tree.column("ID", width=50)
        self.workers_tree.column("Name", width=200)
        self.workers_tree.column("Phone", width=150)
        
        self.workers_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.workers_tree.bind("<<TreeviewSelect>>", self.on_worker_select)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_card, orient="vertical", command=self.workers_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.workers_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = tk.Frame(main_container, bg=ClaymorphismTheme.BG_PRIMARY)
        button_frame.pack(fill="x", pady=10)
        
        add_btn_frame, add_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Add Worker",
            command=self.add_worker
        )
        add_btn_frame.pack(side="left", padx=5)
        
        edit_btn_frame, edit_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Edit Worker",
            command=self.edit_worker
        )
        edit_btn_frame.pack(side="left", padx=5)
        
        delete_btn_frame, delete_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Delete Worker",
            command=self.delete_worker
        )
        delete_btn_frame.pack(side="left", padx=5)
        
        refresh_btn_frame, refresh_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Refresh",
            command=self.load_workers
        )
        refresh_btn_frame.pack(side="left", padx=5)
        
        # Worker details
        details_frame, details_card = ClaymorphismTheme.create_card(main_container, text="Worker Details")
        details_frame.pack(fill="both", expand=True)
        
        # Form fields
        form_frame = tk.Frame(details_card, bg=ClaymorphismTheme.BG_CARD)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Name
        name_label = tk.Label(form_frame, text="Name:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        name_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.worker_name_frame, self.worker_name = ClaymorphismTheme.create_entry(form_frame, width=30)
        self.worker_name_frame.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Phone
        phone_label = tk.Label(form_frame, text="Phone:", bg=ClaymorphismTheme.BG_CARD, 
                              font=ClaymorphismTheme.FONT_NORMAL)
        phone_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.worker_phone_frame, self.worker_phone = ClaymorphismTheme.create_entry(form_frame, width=30)
        self.worker_phone_frame.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Photo
        photo_label = tk.Label(form_frame, text="Photo:", bg=ClaymorphismTheme.BG_CARD, 
                              font=ClaymorphismTheme.FONT_NORMAL)
        photo_label.grid(row=2, column=0, sticky="w", pady=5)
        
        photo_frame = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_CARD)
        photo_frame.grid(row=2, column=1, sticky="ew", pady=5)
        
        self.photo_path_label = tk.Label(photo_frame, text="No photo selected", 
                                        bg=ClaymorphismTheme.BG_CARD, 
                                        font=ClaymorphismTheme.FONT_NORMAL,
                                        fg=ClaymorphismTheme.TEXT_SECONDARY)
        self.photo_path_label.pack(side="left", padx=5)
        
        browse_btn_frame, browse_btn = ClaymorphismTheme.create_button(
            photo_frame, 
            text="Browse",
            command=self.browse_photo
        )
        browse_btn_frame.pack(side="left", padx=5)
        
        # Buttons
        button_frame2 = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_CARD)
        button_frame2.grid(row=3, column=0, columnspan=2, pady=10)
        
        save_btn_frame, save_btn = ClaymorphismTheme.create_button(
            button_frame2, 
            text="Save",
            command=self.save_worker
        )
        save_btn_frame.pack(side="left", padx=5)
        
        cancel_btn_frame, cancel_btn = ClaymorphismTheme.create_button(
            button_frame2, 
            text="Cancel",
            command=self.clear_worker_form
        )
        cancel_btn_frame.pack(side="left", padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
        # Load workers
        self.load_workers()
        
        # Initially disable form
        self.toggle_worker_form(False)
    
    def create_reports_tab(self, parent):
        # Main container
        main_container = tk.Frame(parent, bg=ClaymorphismTheme.BG_PRIMARY)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Report options
        options_frame, options_card = ClaymorphismTheme.create_card(main_container, height=120)
        options_frame.pack(fill="x", pady=(0, 10))
        
        # Worker selection
        worker_label = tk.Label(options_card, text="Worker:", bg=ClaymorphismTheme.BG_CARD, 
                               font=ClaymorphismTheme.FONT_NORMAL)
        worker_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.worker_combo_frame, self.worker_combo = ClaymorphismTheme.create_combobox(options_card, width=25)
        self.worker_combo_frame.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # Date range
        from_label = tk.Label(options_card, text="From:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        from_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.report_from_frame, self.report_from = ClaymorphismTheme.create_entry(options_card, width=15)
        self.report_from_frame.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        to_label = tk.Label(options_card, text="To:", bg=ClaymorphismTheme.BG_CARD, 
                           font=ClaymorphismTheme.FONT_NORMAL)
        to_label.grid(row=1, column=2, sticky="w", padx=10, pady=5)
        
        self.report_to_frame, self.report_to = ClaymorphismTheme.create_entry(options_card, width=15)
        self.report_to_frame.grid(row=1, column=3, sticky="w", padx=10, pady=5)
        
        # Generate button
        generate_btn_frame, generate_btn = ClaymorphismTheme.create_button(
            options_card, 
            text="Generate Report",
            command=self.generate_attendance_report
        )
        generate_btn_frame.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Export button
        export_btn_frame, export_btn = ClaymorphismTheme.create_button(
            options_card, 
            text="Export to CSV",
            command=self.export_attendance_report
        )
        export_btn_frame.grid(row=2, column=2, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Report display
        report_frame, report_card = ClaymorphismTheme.create_card(main_container)
        report_frame.pack(fill="both", expand=True)
        
        # Create treeview for report
        self.report_tree = ttk.Treeview(report_card, columns=("Date", "Morning", "Afternoon", "Notes"), show="headings")
        self.report_tree.heading("Date", text="Date")
        self.report_tree.heading("Morning", text="Morning")
        self.report_tree.heading("Afternoon", text="Afternoon")
        self.report_tree.heading("Notes", text="Notes")
        
        self.report_tree.column("Date", width=100)
        self.report_tree.column("Morning", width=100)
        self.report_tree.column("Afternoon", width=100)
        self.report_tree.column("Notes", width=300)
        
        self.report_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(report_card, orient="vertical", command=self.report_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.report_tree.configure(yscrollcommand=scrollbar.set)
        
        # Load workers for combobox
        self.load_workers_for_combobox()
    
    def load_daily_attendance(self):
        """Load attendance for the selected date"""
        date_str = self.date_entry.get().strip()
        
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")
            return
        
        # Clear existing items
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        # Get workers
        workers = self.db.get_workers()
        
        # Get attendance for the selected date
        attendance_records = self.db.get_attendance(selected_date)
        
        # Create a dictionary for quick lookup
        attendance_dict = {record["worker_id"]: record for record in attendance_records}
        
        # Add workers to treeview
        for worker in workers:
            worker_id = worker["worker_id"]
            
            if worker_id in attendance_dict:
                record = attendance_dict[worker_id]
                morning = "Yes" if record["morning"] else "No"
                afternoon = "Yes" if record["afternoon"] else "No"
                notes = record["notes"] or ""
            else:
                morning = "No"
                afternoon = "No"
                notes = ""
            
            self.attendance_tree.insert("", "end", values=(
                worker_id,
                worker["name"],
                morning,
                afternoon,
                notes
            ))
    
    def save_daily_attendance(self):
        """Save attendance for the selected date"""
        date_str = self.date_entry.get().strip()
        
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")
            return
        
        # Save attendance for each worker
        for item in self.attendance_tree.get_children():
            values = self.attendance_tree.item(item, "values")
            worker_id = int(values[0])
            morning = 1 if values[2] == "Yes" else 0
            afternoon = 1 if values[3] == "Yes" else 0
            notes = values[4]
            
            # Save attendance record
            self.db.add_attendance(worker_id, selected_date, morning, afternoon, notes)
        
        messagebox.showinfo("Success", "Attendance saved successfully.")
    
    def load_workers(self):
        """Load workers into the treeview"""
        # Clear existing items
        for item in self.workers_tree.get_children():
            self.workers_tree.delete(item)
        
        # Get workers from database
        workers = self.db.get_workers()
        
        # Add workers to treeview
        for worker in workers:
            self.workers_tree.insert("", "end", values=(
                worker["worker_id"],
                worker["name"],
                worker["phone"] or ""
            ))
    
    def on_worker_select(self, event):
        """Handle worker selection"""
        selected_items = self.workers_tree.selection()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        worker_id = self.workers_tree.item(selected_item, "values")[0]
        
        # Get worker details
        workers = self.db.get_workers()
        worker = next((w for w in workers if w["worker_id"] == int(worker_id)), None)
        
        if worker:
            # Populate form fields
            self.worker_name.delete(0, "end")
            self.worker_name.insert(0, worker["name"])
            
            self.worker_phone.delete(0, "end")
            self.worker_phone.insert(0, worker["phone"] or "")
            
            if worker["photo_path"]:
                self.photo_path_label.config(text=worker["photo_path"])
            else:
                self.photo_path_label.config(text="No photo selected")
            
            # Enable form
            self.toggle_worker_form(True)
            self.current_worker_id = worker["worker_id"]
    
    def add_worker(self):
        """Add a new worker"""
        # Clear form
        self.clear_worker_form()
        
        # Enable form
        self.toggle_worker_form(True)
        
        # Set focus to name entry
        self.worker_name.focus()
        
        # Set mode to add
        self.mode = "add"
    
    def edit_worker(self):
        """Edit selected worker"""
        selected_items = self.workers_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a worker to edit.")
            return
        
        # Set mode to edit
        self.mode = "edit"
    
    def delete_worker(self):
        """Delete selected worker"""
        selected_items = self.workers_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a worker to delete.")
            return
        
        selected_item = selected_items[0]
        worker_id = self.workers_tree.item(selected_item, "values")[0]
        worker_name = self.workers_tree.item(selected_item, "values")[1]
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {worker_name}?"):
            # Delete worker
            success = self.db.delete_worker(int(worker_id))
            
            if success:
                messagebox.showinfo("Success", "Worker deleted successfully.")
                self.load_workers()
                self.clear_worker_form()
            else:
                messagebox.showerror("Error", "Cannot delete worker with attendance records.")
    
    def save_worker(self):
        """Save worker data"""
        # Get form data
        name = self.worker_name.get().strip()
        phone = self.worker_phone.get().strip()
        photo_path = self.photo_path_label.cget("text")
        
        if photo_path == "No photo selected":
            photo_path = None
        
        # Validate form
        if not name:
            messagebox.showwarning("Validation Error", "Name is required.")
            return
        
        # Save worker
        if hasattr(self, 'mode') and self.mode == "add":
            # Add new worker
            worker_id = self.db.add_worker(name, phone, photo_path)
            
            if worker_id:
                messagebox.showinfo("Success", "Worker added successfully.")
                self.load_workers()
                self.clear_worker_form()
            else:
                messagebox.showerror("Error", "Failed to add worker.")
        else:
            # Update existing worker
            success = self.db.update_worker(
                self.current_worker_id, name, phone, photo_path
            )
            
            if success:
                messagebox.showinfo("Success", "Worker updated successfully.")
                self.load_workers()
                self.clear_worker_form()
            else:
                messagebox.showerror("Error", "Failed to update worker.")
    
    def clear_worker_form(self):
        """Clear worker form fields"""
        self.worker_name.delete(0, "end")
        self.worker_phone.delete(0, "end")
        self.photo_path_label.config(text="No photo selected")
        
        # Disable form
        self.toggle_worker_form(False)
        
        # Clear selection
        for item in self.workers_tree.selection():
            self.workers_tree.selection_remove(item)
    
    def toggle_worker_form(self, enabled):
        """Enable or disable worker form fields"""
        state = "normal" if enabled else "disabled"
        
        self.worker_name.config(state=state)
        self.worker_phone.config(state=state)
    
    def browse_photo(self):
        """Browse for worker photo"""
        file_path = filedialog.askopenfilename(
            title="Select Worker Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        
        if file_path:
            self.photo_path_label.config(text=file_path)
    
    def load_workers_for_combobox(self):
        """Load workers for the combobox in reports tab"""
        # Get workers from database
        workers = self.db.get_workers()
        
        # Create list of worker names
        worker_names = [worker["name"] for worker in workers]
        
        # Add "All Workers" option
        worker_names.insert(0, "All Workers")
        
        # Set combobox values
        self.worker_combo['values'] = worker_names
        self.worker_combo.current(0)
    
    def generate_attendance_report(self):
        """Generate attendance report"""
        worker_name = self.worker_combo.get()
        from_date_str = self.report_from.get().strip()
        to_date_str = self.report_to.get().strip()
        
        # Validate dates
        try:
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date() if from_date_str else None
        except ValueError:
            messagebox.showwarning("Invalid Date", "Please enter a valid from date in YYYY-MM-DD format.")
            return
        
        try:
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date() if to_date_str else None
        except ValueError:
            messagebox.showwarning("Invalid Date", "Please enter a valid to date in YYYY-MM-DD format.")
            return
        
        # Clear existing items
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        # Get worker ID if specific worker is selected
        worker_id = None
        if worker_name != "All Workers":
            workers = self.db.get_workers()
            worker = next((w for w in workers if w["name"] == worker_name), None)
            if worker:
                worker_id = worker["worker_id"]
        
        # Get attendance records
        if worker_id:
            attendance_records = self.db.get_attendance_by_worker(worker_id, from_date, to_date)
        else:
            # Get all attendance records within date range
            all_records = self.db.get_attendance()
            attendance_records = []
            
            for record in all_records:
                record_date = record["date"]
                
                # Filter by date range
                if from_date and record_date < from_date:
                    continue
                
                if to_date and record_date > to_date:
                    continue
                
                attendance_records.append(record)
        
        # Add records to treeview
        for record in attendance_records:
            morning = "Yes" if record["morning"] else "No"
            afternoon = "Yes" if record["afternoon"] else "No"
            
            self.report_tree.insert("", "end", values=(
                record["date"].strftime("%Y-%m-%d"),
                morning,
                afternoon,
                record["notes"] or ""
            ))
    
    def export_attendance_report(self):
        """Export attendance report to CSV"""
        # Check if there's data to export
        if not self.report_tree.get_children():
            messagebox.showwarning("No Data", "Please generate a report first.")
            return
        
        # Get file path
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Attendance Report"
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
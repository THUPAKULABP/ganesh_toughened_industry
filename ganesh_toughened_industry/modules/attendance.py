import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date, timedelta
import calendar
import os
from PIL import Image, ImageTk, ImageDraw
from ui_theme import ClaymorphismTheme

class AttendanceModule:
    def __init__(self, parent, db, app):
        self.parent = parent
        self.db = db
        self.app = app
        self.selected_worker = None
        self.selected_date = date.today()
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """Create the worker attendance UI with claymorphism style"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = ClaymorphismTheme.create_label(
            main_frame, 
            text="WORKER ATTENDANCE", 
            style="Title.TLabel"
        )
        title.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ClaymorphismTheme.create_notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        daily_tab = ttk.Frame(notebook)
        workers_tab = ttk.Frame(notebook)
        calendar_tab = ttk.Frame(notebook)
        
        notebook.add(daily_tab, text="Daily Attendance")
        notebook.add(workers_tab, text="Workers")
        notebook.add(calendar_tab, text="Calendar View")
        
        # Create daily attendance tab
        self.create_daily_tab(daily_tab)
        
        # Create workers tab
        self.create_workers_tab(workers_tab)
        
        # Create calendar view tab
        self.create_calendar_tab(calendar_tab)
    
    def create_daily_tab(self, parent):
        """Create the daily attendance tab with claymorphism style"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Date selection card
        date_card = ClaymorphismTheme.create_card(main_frame, padding=15)
        date_card.pack(fill=tk.X, pady=(0, 15))
        
        # Date selection
        date_frame = ttk.Frame(date_card)
        date_frame.pack(fill=tk.X)
        
        ClaymorphismTheme.create_label(date_frame, text="Date:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        date_entry = ClaymorphismTheme.create_entry(date_frame, textvariable=self.date_var, width=12)
        date_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        # Today button
        today_btn = ClaymorphismTheme.create_button(
            date_frame, 
            text="Today", 
            command=self.set_today,
            style="Secondary.TButton"
        )
        today_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Load button
        load_btn = ClaymorphismTheme.create_button(
            date_frame, 
            text="Load", 
            command=self.load_daily_attendance
        )
        load_btn.pack(side=tk.LEFT)
        
        # Attendance display card
        attendance_card = ClaymorphismTheme.create_card(main_frame, padding=15)
        attendance_card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Attendance treeview
        self.attendance_tree, scrollbar = ClaymorphismTheme.create_treeview(
            attendance_card, 
            columns=("worker", "morning", "afternoon", "notes")
        )
        self.attendance_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Define headings
        self.attendance_tree.heading("worker", text="Worker")
        self.attendance_tree.heading("morning", text="Morning")
        self.attendance_tree.heading("afternoon", text="Afternoon")
        self.attendance_tree.heading("notes", text="Notes")
        
        # Define columns
        self.attendance_tree.column("worker", width=150)
        self.attendance_tree.column("morning", width=80)
        self.attendance_tree.column("afternoon", width=80)
        self.attendance_tree.column("notes", width=200)
        
        # Action buttons card
        action_card = ClaymorphismTheme.create_card(main_frame, padding=15)
        action_card.pack(fill=tk.X)
        
        # Action buttons
        action_frame = ttk.Frame(action_card)
        action_frame.pack(fill=tk.X)
        
        # Mark present button
        present_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Mark Present", 
            command=self.mark_present,
            style="Success.TButton"
        )
        present_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Mark absent button
        absent_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Mark Absent", 
            command=self.mark_absent,
            style="Danger.TButton"
        )
        absent_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Save button
        save_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Save", 
            command=self.save_attendance
        )
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Load initial attendance
        self.load_daily_attendance()
    
    def create_workers_tab(self, parent):
        """Create the workers management tab with claymorphism style"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Workers list card
        workers_card = ClaymorphismTheme.create_card(main_frame, padding=15)
        workers_card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Workers treeview
        self.workers_tree, scrollbar = ClaymorphismTheme.create_treeview(
            workers_card, 
            columns=("name", "phone")
        )
        self.workers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Define headings
        self.workers_tree.heading("name", text="Name")
        self.workers_tree.heading("phone", text="Phone")
        
        # Define columns
        self.workers_tree.column("name", width=200)
        self.workers_tree.column("phone", width=150)
        
        # Bind double-click to view worker details
        self.workers_tree.bind("<Double-1>", self.view_worker_details)
        
        # Action buttons card
        action_card = ClaymorphismTheme.create_card(main_frame, padding=15)
        action_card.pack(fill=tk.X)
        
        # Action buttons
        action_frame = ttk.Frame(action_card)
        action_frame.pack(fill=tk.X)
        
        # Add worker button
        add_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Add Worker", 
            command=self.add_worker,
            style="Success.TButton"
        )
        add_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Edit worker button
        edit_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Edit Worker", 
            command=self.edit_worker,
            style="Secondary.TButton"
        )
        edit_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Delete worker button
        delete_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Delete Worker", 
            command=self.delete_worker,
            style="Danger.TButton"
        )
        delete_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Load workers
        self.load_workers()
    
    def create_calendar_tab(self, parent):
        """Create the calendar view tab with claymorphism style"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Month selection card
        month_card = ClaymorphismTheme.create_card(main_frame, padding=15)
        month_card.pack(fill=tk.X, pady=(0, 15))
        
        # Month selection
        month_frame = ttk.Frame(month_card)
        month_frame.pack(fill=tk.X)
        
        ClaymorphismTheme.create_label(month_frame, text="Month:").pack(side=tk.LEFT, padx=(0, 10))
        
        current_year = datetime.now().year
        years = [str(year) for year in range(current_year - 5, current_year + 6)]
        self.year_var = tk.StringVar(value=str(current_year))
        year_combo = ClaymorphismTheme.create_combobox(
            month_frame, 
            textvariable=self.year_var, 
            values=years, 
            width=8
        )
        year_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        months = list(calendar.month_name)[1:]  # Remove empty string at index 0
        self.month_var = tk.StringVar(value=calendar.month_name[datetime.now().month])
        month_combo = ClaymorphismTheme.create_combobox(
            month_frame, 
            textvariable=self.month_var, 
            values=months, 
            width=12
        )
        month_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # Worker selection
        ClaymorphismTheme.create_label(month_frame, text="Worker:").pack(side=tk.LEFT, padx=(0, 10))
        self.worker_var = tk.StringVar()
        self.worker_combo = ClaymorphismTheme.create_combobox(month_frame, textvariable=self.worker_var)
        self.worker_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        # Load button
        load_btn = ClaymorphismTheme.create_button(
            month_frame, 
            text="Load", 
            command=self.load_calendar_view
        )
        load_btn.pack(side=tk.LEFT)
        
        # Calendar display card
        calendar_card = ClaymorphismTheme.create_card(main_frame, padding=15)
        calendar_card.pack(fill=tk.BOTH, expand=True)
        
        # Calendar display
        self.calendar_frame = ttk.Frame(calendar_card)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True)
        
        # Load initial calendar view
        self.load_calendar_view()
    
    def set_today(self):
        """Set date to today"""
        self.date_var.set(date.today().strftime("%d/%m/%Y"))
        self.load_daily_attendance()
    
    def load_daily_attendance(self):
        """Load daily attendance for selected date"""
        # Clear existing items
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        # Get date
        date_str = self.date_var.get()
        try:
            day, month, year = date_str.split('/')
            self.selected_date = date(int(year), int(month), int(day))
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid date in DD/MM/YYYY format")
            return
        
        # Get workers
        workers = self.db.get_workers()
        
        # Get attendance for each worker
        for worker in workers:
            # Get attendance
            attendance = self.db.get_attendance(worker["worker_id"], self.selected_date)
            
            if attendance:
                morning = "✓" if attendance["morning"] else "✗"
                afternoon = "✓" if attendance["afternoon"] else "✗"
                notes = attendance["notes"] or ""
            else:
                morning = ""
                afternoon = ""
                notes = ""
            
            # Add to treeview
            self.attendance_tree.insert("", "end", values=(
                worker["name"],
                morning,
                afternoon,
                notes
            ), tags=(worker["worker_id"],))
        
        # Configure tags for selection
        self.attendance_tree.tag_configure("selected", background="#e6f7ff")
    
    def mark_present(self):
        """Mark selected worker as present"""
        selected = self.attendance_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a worker")
            return
        
        # Get worker ID
        worker_id = self.attendance_tree.item(selected[0])["tags"][0]
        
        # Update treeview
        item = self.attendance_tree.item(selected[0])
        values = list(item["values"])
        values[1] = "✓"  # Morning
        values[2] = "✓"  # Afternoon
        self.attendance_tree.item(selected[0], values=values)
    
    def mark_absent(self):
        """Mark selected worker as absent"""
        selected = self.attendance_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a worker")
            return
        
        # Get worker ID
        worker_id = self.attendance_tree.item(selected[0])["tags"][0]
        
        # Update treeview
        item = self.attendance_tree.item(selected[0])
        values = list(item["values"])
        values[1] = "✗"  # Morning
        values[2] = "✗"  # Afternoon
        self.attendance_tree.item(selected[0], values=values)
    
    def save_attendance(self):
        """Save attendance for all workers"""
        # Get all items
        items = self.attendance_tree.get_children()
        
        if not items:
            messagebox.showinfo("Info", "No workers to save")
            return
        
        # Save attendance for each worker
        for item in items:
            # Get worker ID and values
            worker_id = self.attendance_tree.item(item)["tags"][0]
            values = self.attendance_tree.item(item)["values"]
            
            # Parse attendance
            morning = values[1] == "✓"
            afternoon = values[2] == "✓"
            notes = values[3]
            
            # Save to database
            self.db.add_attendance(
                worker_id=worker_id,
                date=self.selected_date,
                morning=morning,
                afternoon=afternoon,
                notes=notes
            )
        
        messagebox.showinfo("Success", "Attendance saved successfully")
    
    def load_workers(self):
        """Load workers into treeview"""
        # Clear existing items
        for item in self.workers_tree.get_children():
            self.workers_tree.delete(item)
        
        # Get workers
        workers = self.db.get_workers()
        
        # Add to treeview
        for worker in workers:
            self.workers_tree.insert("", "end", values=(
                worker["name"],
                worker["phone"] or ""
            ), tags=(worker["worker_id"],))
        
        # Also load for calendar view
        worker_names = [worker["name"] for worker in workers]
        if hasattr(self, 'worker_combo'):
            self.worker_combo["values"] = worker_names
    
    def view_worker_details(self, event=None):
        """View worker details"""
        selected = self.workers_tree.selection()
        if not selected:
            return
        
        # Get worker ID
        worker_id = self.workers_tree.item(selected[0])["tags"][0]
        
        # Get worker from database
        workers = self.db.get_workers()
        worker = None
        for w in workers:
            if w["worker_id"] == worker_id:
                worker = w
                break
        
        if not worker:
            messagebox.showerror("Error", "Worker not found")
            return
        
        # Create worker details dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Worker Details - {worker['name']}")
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Apply theme to dialog
        ClaymorphismTheme.setup_theme(dialog)
        
        # Worker details card
        details_card = ClaymorphismTheme.create_card(dialog, text="Worker Details", padding=20)
        details_card.pack(fill=tk.X, padx=20, pady=20)
        
        # Name
        name_frame = ttk.Frame(details_card)
        name_frame.pack(fill=tk.X, pady=5)
        ClaymorphismTheme.create_label(name_frame, text="Name:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        ClaymorphismTheme.create_label(name_frame, text=worker["name"]).pack(side=tk.LEFT)
        
        # Phone
        phone_frame = ttk.Frame(details_card)
        phone_frame.pack(fill=tk.X, pady=5)
        ClaymorphismTheme.create_label(phone_frame, text="Phone:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        ClaymorphismTheme.create_label(phone_frame, text=worker["phone"] or "").pack(side=tk.LEFT)
        
        # Photo
        photo_frame = ttk.Frame(details_card)
        photo_frame.pack(fill=tk.X, pady=10)
        
        ClaymorphismTheme.create_label(photo_frame, text="Photo:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        # Display photo if available
        if worker["photo_path"] and os.path.exists(worker["photo_path"]):
            try:
                photo_img = Image.open(worker["photo_path"])
                photo_img = photo_img.resize((150, 150), Image.LANCZOS)
                photo_photo = ImageTk.PhotoImage(photo_img)
                photo_img_label = ttk.Label(photo_frame, image=photo_photo)
                photo_img_label.image = photo_photo  # Keep a reference
                photo_img_label.pack(side=tk.LEFT, padx=5)
            except Exception as e:
                ClaymorphismTheme.create_label(photo_frame, text="No photo available").pack(side=tk.LEFT, padx=5)
        else:
            ClaymorphismTheme.create_label(photo_frame, text="No photo available").pack(side=tk.LEFT, padx=5)
        
        # Attendance summary card
        summary_card = ClaymorphismTheme.create_card(dialog, text="Attendance Summary", padding=20)
        summary_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Get attendance summary
        try:
            # Get current month
            now = datetime.now()
            start_date = date(now.year, now.month, 1)
            
            # Get end date (last day of month)
            if now.month == 12:
                end_date = date(now.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(now.year, now.month + 1, 1) - timedelta(days=1)
            
            # Get attendance
            attendance = self.db.get_attendance_by_worker(worker_id, start_date, end_date)
            
            # Calculate summary
            total_days = len(attendance)
            present_mornings = sum(1 for a in attendance if a["morning"])
            present_afternoons = sum(1 for a in attendance if a["afternoon"])
            
            # Display summary
            days_frame = ttk.Frame(summary_card)
            days_frame.pack(fill=tk.X, pady=5)
            ClaymorphismTheme.create_label(days_frame, text="Total Days:").pack(side=tk.LEFT)
            ClaymorphismTheme.create_label(days_frame, text=str(total_days)).pack(side=tk.RIGHT)
            
            mornings_frame = ttk.Frame(summary_card)
            mornings_frame.pack(fill=tk.X, pady=5)
            ClaymorphismTheme.create_label(mornings_frame, text="Present Mornings:").pack(side=tk.LEFT)
            ClaymorphismTheme.create_label(mornings_frame, text=str(present_mornings)).pack(side=tk.RIGHT)
            
            afternoons_frame = ttk.Frame(summary_card)
            afternoons_frame.pack(fill=tk.X, pady=5)
            ClaymorphismTheme.create_label(afternoons_frame, text="Present Afternoons:").pack(side=tk.LEFT)
            ClaymorphismTheme.create_label(afternoons_frame, text=str(present_afternoons)).pack(side=tk.RIGHT)
            
        except Exception as e:
            print(f"Error calculating attendance summary: {e}")
        
        # Action buttons card
        action_card = ClaymorphismTheme.create_card(dialog, padding=15)
        action_card.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Action buttons
        action_frame = ttk.Frame(action_card)
        action_frame.pack(fill=tk.X)
        
        # Edit button
        edit_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Edit", 
            command=lambda: self.edit_worker_from_dialog(worker, dialog),
            style="Secondary.TButton"
        )
        edit_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Close button
        close_btn = ClaymorphismTheme.create_button(
            action_frame, 
            text="Close", 
            command=dialog.destroy
        )
        close_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def add_worker(self):
        """Add a new worker"""
        # Create worker dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Worker")
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Apply theme to dialog
        ClaymorphismTheme.setup_theme(dialog)
        
        # Worker details card
        details_card = ClaymorphismTheme.create_card(dialog, padding=20)
        details_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Worker details
        ClaymorphismTheme.create_label(details_card, text="Name:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        name_var = tk.StringVar()
        name_entry = ClaymorphismTheme.create_entry(details_card, textvariable=name_var)
        name_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)
        
        ClaymorphismTheme.create_label(details_card, text="Phone:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        phone_var = tk.StringVar()
        phone_entry = ClaymorphismTheme.create_entry(details_card, textvariable=phone_var)
        phone_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.EW)
        
        # Photo
        ClaymorphismTheme.create_label(details_card, text="Photo:", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        photo_frame = ttk.Frame(details_card)
        photo_frame.grid(row=2, column=1, padx=10, pady=10, sticky=tk.EW)
        
        photo_label = ClaymorphismTheme.create_label(photo_frame, text="No photo selected")
        photo_label.pack(side=tk.LEFT, padx=5)
        
        photo_path_var = tk.StringVar()
        
        def select_photo():
            file_path = filedialog.askopenfilename(
                title="Select Photo",
                filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
            )
            
            if file_path:
                photo_path_var.set(file_path)
                
                # Display photo
                try:
                    photo_img = Image.open(file_path)
                    photo_img = photo_img.resize((150, 150), Image.LANCZOS)
                    photo_photo = ImageTk.PhotoImage(photo_img)
                    photo_label.configure(image=photo_photo)
                    photo_label.image = photo_photo  # Keep a reference
                except Exception as e:
                    messagebox.showerror("Error", f"Could not load photo: {e}")
        
        select_btn = ClaymorphismTheme.create_button(
            photo_frame, 
            text="Select Photo", 
            command=select_photo,
            style="Secondary.TButton"
        )
        select_btn.pack(side=tk.LEFT, padx=5)
        
        # Buttons card
        button_card = ClaymorphismTheme.create_card(dialog, padding=15)
        button_card.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(button_card)
        button_frame.pack(fill=tk.X)
        
        def save_worker():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Worker name is required")
                return
            
            # Add worker to database
            worker_id = self.db.add_worker(
                name=name,
                phone=phone_var.get().strip(),
                photo_path=photo_path_var.get()
            )
            
            if worker_id:
                # Refresh workers list
                self.load_workers()
                
                # Close dialog
                dialog.destroy()
                
                messagebox.showinfo("Success", "Worker added successfully")
            else:
                messagebox.showerror("Error", "Could not add worker")
        
        save_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Save", 
            command=save_worker,
            style="Success.TButton"
        )
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        cancel_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Cancel", 
            command=dialog.destroy,
            style="Danger.TButton"
        )
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Configure grid weights
        dialog.columnconfigure(1, weight=1)
    
    def edit_worker(self):
        """Edit selected worker"""
        selected = self.workers_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a worker to edit")
            return
        
        # Get worker ID
        worker_id = self.workers_tree.item(selected[0])["tags"][0]
        
        # Get worker from database
        workers = self.db.get_workers()
        worker = None
        for w in workers:
            if w["worker_id"] == worker_id:
                worker = w
                break
        
        if not worker:
            messagebox.showerror("Error", "Worker not found")
            return
        
        # Create edit worker dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Edit Worker - {worker['name']}")
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Apply theme to dialog
        ClaymorphismTheme.setup_theme(dialog)
        
        # Worker details card
        details_card = ClaymorphismTheme.create_card(dialog, padding=20)
        details_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Worker details
        ClaymorphismTheme.create_label(details_card, text="Name:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        name_var = tk.StringVar(value=worker["name"])
        name_entry = ClaymorphismTheme.create_entry(details_card, textvariable=name_var)
        name_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)
        
        ClaymorphismTheme.create_label(details_card, text="Phone:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        phone_var = tk.StringVar(value=worker["phone"] or "")
        phone_entry = ClaymorphismTheme.create_entry(details_card, textvariable=phone_var)
        phone_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.EW)
        
        # Photo
        ClaymorphismTheme.create_label(details_card, text="Photo:", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        photo_frame = ttk.Frame(details_card)
        photo_frame.grid(row=2, column=1, padx=10, pady=10, sticky=tk.EW)
        
        # Display current photo if available
        if worker["photo_path"] and os.path.exists(worker["photo_path"]):
            try:
                photo_img = Image.open(worker["photo_path"])
                photo_img = photo_img.resize((150, 150), Image.LANCZOS)
                photo_photo = ImageTk.PhotoImage(photo_img)
                photo_label = ttk.Label(photo_frame, image=photo_photo)
                photo_label.image = photo_photo  # Keep a reference
                photo_label.pack(side=tk.LEFT, padx=5)
            except Exception as e:
                photo_label = ClaymorphismTheme.create_label(photo_frame, text="No photo available")
                photo_label.pack(side=tk.LEFT, padx=5)
        else:
            photo_label = ClaymorphismTheme.create_label(photo_frame, text="No photo available")
            photo_label.pack(side=tk.LEFT, padx=5)
        
        photo_path_var = tk.StringVar(value=worker["photo_path"] or "")
        
        def select_photo():
            file_path = filedialog.askopenfilename(
                title="Select Photo",
                filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
            )
            
            if file_path:
                photo_path_var.set(file_path)
                
                # Display photo
                try:
                    photo_img = Image.open(file_path)
                    photo_img = photo_img.resize((150, 150), Image.LANCZOS)
                    photo_photo = ImageTk.PhotoImage(photo_img)
                    photo_label.configure(image=photo_photo)
                    photo_label.image = photo_photo  # Keep a reference
                except Exception as e:
                    messagebox.showerror("Error", f"Could not load photo: {e}")
        
        select_btn = ClaymorphismTheme.create_button(
            photo_frame, 
            text="Select Photo", 
            command=select_photo,
            style="Secondary.TButton"
        )
        select_btn.pack(side=tk.LEFT, padx=5)
        
        # Buttons card
        button_card = ClaymorphismTheme.create_card(dialog, padding=15)
        button_card.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(button_card)
        button_frame.pack(fill=tk.X)
        
        def save_worker():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Worker name is required")
                return
            
            # Update worker in database
            success = self.db.update_worker(
                worker_id=worker_id,
                name=name,
                phone=phone_var.get().strip(),
                photo_path=photo_path_var.get()
            )
            
            if success:
                # Refresh workers list
                self.load_workers()
                
                # Close dialog
                dialog.destroy()
                
                messagebox.showinfo("Success", "Worker updated successfully")
            else:
                messagebox.showerror("Error", "Could not update worker")
        
        save_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Save", 
            command=save_worker,
            style="Success.TButton"
        )
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        cancel_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Cancel", 
            command=dialog.destroy,
            style="Danger.TButton"
        )
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Configure grid weights
        dialog.columnconfigure(1, weight=1)
    
    def edit_worker_from_dialog(self, worker, parent_dialog):
        """Edit worker from details dialog"""
        parent_dialog.destroy()
        self.edit_worker()
    
    def delete_worker(self):
        """Delete selected worker"""
        selected = self.workers_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a worker to delete")
            return
        
        # Get worker ID
        worker_id = self.workers_tree.item(selected[0])["tags"][0]
        
        # Get worker from database
        workers = self.db.get_workers()
        worker = None
        for w in workers:
            if w["worker_id"] == worker_id:
                worker = w
                break
        
        if not worker:
            messagebox.showerror("Error", "Worker not found")
            return
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {worker['name']}?"):
            # Delete worker from database
            success = self.db.delete_worker(worker_id)
            
            if success:
                # Refresh workers list
                self.load_workers()
                
                messagebox.showinfo("Success", "Worker deleted successfully")
            else:
                messagebox.showerror("Error", "Could not delete worker")
    
    def load_calendar_view(self):
        """Load calendar view for selected month and worker"""
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Get month and year
        month_name = self.month_var.get()
        year = int(self.year_var.get())
        
        # Convert month name to number
        month_num = list(calendar.month_name).index(month_name)
        
        # Get worker
        worker_name = self.worker_var.get()
        worker_id = None
        
        if worker_name:
            workers = self.db.get_workers()
            for worker in workers:
                if worker["name"] == worker_name:
                    worker_id = worker["worker_id"]
                    break
        
        # Create calendar
        cal = calendar.monthcalendar(year, month_num)
        
        # Create header
        header_frame = ttk.Frame(self.calendar_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Day names
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in day_names:
            day_label = ClaymorphismTheme.create_label(header_frame, text=day, font=("Segoe UI", 10, "bold"))
            day_label.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Create calendar grid
        for week in cal:
            week_frame = ttk.Frame(self.calendar_frame)
            week_frame.pack(fill=tk.X, padx=5, pady=2)
            
            for day in week:
                if day == 0:  # Day not in month
                    day_label = ClaymorphismTheme.create_label(week_frame, text="")
                    day_label.pack(side=tk.LEFT, padx=2, pady=2)
                else:
                    # Create day frame
                    day_frame = ttk.Frame(week_frame, relief=tk.RIDGE, borderwidth=1)
                    day_frame.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.BOTH, expand=True)
                    
                    # Day number
                    day_label = ClaymorphismTheme.create_label(day_frame, text=str(day), font=("Segoe UI", 10, "bold"))
                    day_label.pack()
                    
                    # Get attendance for this day
                    if worker_id:
                        date_obj = date(year, month_num, day)
                        attendance = self.db.get_attendance(worker_id, date_obj)
                        
                        if attendance:
                            # Create attendance indicators
                            att_frame = ttk.Frame(day_frame)
                            att_frame.pack()
                            
                            if attendance["morning"]:
                                morning_label = ClaymorphismTheme.create_label(att_frame, text="✓", font=("Segoe UI", 12))
                                morning_label.configure(foreground="#48bb78")  # Green
                                morning_label.pack(side=tk.LEFT)
                            else:
                                morning_label = ClaymorphismTheme.create_label(att_frame, text="✗", font=("Segoe UI", 12))
                                morning_label.configure(foreground="#f56565")  # Red
                                morning_label.pack(side=tk.LEFT)
                            
                            if attendance["afternoon"]:
                                afternoon_label = ClaymorphismTheme.create_label(att_frame, text="✓", font=("Segoe UI", 12))
                                afternoon_label.configure(foreground="#48bb78")  # Green
                                afternoon_label.pack(side=tk.LEFT)
                            else:
                                afternoon_label = ClaymorphismTheme.create_label(att_frame, text="✗", font=("Segoe UI", 12))
                                afternoon_label.configure(foreground="#f56565")  # Red
                                afternoon_label.pack(side=tk.LEFT)
import tkinter as tk
from tkinter import ttk, messagebox
from theme import ClaymorphismTheme

class SettingsModule:
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
            text="Application Settings", 
            height=80
        )
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Content area
        content_frame = tk.Frame(main_container, bg=ClaymorphismTheme.BG_PRIMARY)
        content_frame.pack(fill="both", expand=True)
        
        # Settings form
        settings_frame, settings_card = ClaymorphismTheme.create_card(content_frame, text="Company Information")
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Form fields
        form_frame = tk.Frame(settings_card, bg=ClaymorphismTheme.BG_CARD)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Company name
        name_label = tk.Label(form_frame, text="Company Name:", bg=ClaymorphismTheme.BG_CARD, 
                             font=ClaymorphismTheme.FONT_NORMAL)
        name_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.name_entry_frame, self.name_entry = ClaymorphismTheme.create_entry(form_frame, width=40)
        self.name_entry_frame.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Company address
        address_label = tk.Label(form_frame, text="Address:", bg=ClaymorphismTheme.BG_CARD, 
                                font=ClaymorphismTheme.FONT_NORMAL)
        address_label.grid(row=1, column=0, sticky="nw", pady=5)
        
        self.address_text = tk.Text(form_frame, height=3, width=40, 
                                   bg=ClaymorphismTheme.BG_SECONDARY,
                                   fg=ClaymorphismTheme.TEXT_PRIMARY,
                                   relief="flat",
                                   borderwidth=0,
                                   font=ClaymorphismTheme.FONT_NORMAL)
        self.address_text.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Company phone
        phone_label = tk.Label(form_frame, text="Phone:", bg=ClaymorphismTheme.BG_CARD, 
                              font=ClaymorphismTheme.FONT_NORMAL)
        phone_label.grid(row=2, column=0, sticky="w", pady=5)
        
        self.phone_entry_frame, self.phone_entry = ClaymorphismTheme.create_entry(form_frame, width=40)
        self.phone_entry_frame.grid(row=2, column=1, sticky="ew", pady=5)
        
        # Company GST
        gst_label = tk.Label(form_frame, text="GST:", bg=ClaymorphismTheme.BG_CARD, 
                            font=ClaymorphismTheme.FONT_NORMAL)
        gst_label.grid(row=3, column=0, sticky="w", pady=5)
        
        self.gst_entry_frame, self.gst_entry = ClaymorphismTheme.create_entry(form_frame, width=40)
        self.gst_entry_frame.grid(row=3, column=1, sticky="ew", pady=5)
        
        # Separator
        separator = ttk.Separator(form_frame, orient="horizontal")
        separator.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Payment settings
        payment_label = tk.Label(form_frame, text="Payment Information", bg=ClaymorphismTheme.BG_CARD, 
                               font=ClaymorphismTheme.FONT_SUBTITLE)
        payment_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=5)
        
        # UPI ID
        upi_id_label = tk.Label(form_frame, text="UPI ID:", bg=ClaymorphismTheme.BG_CARD, 
                              font=ClaymorphismTheme.FONT_NORMAL)
        upi_id_label.grid(row=6, column=0, sticky="w", pady=5)
        
        self.upi_id_entry_frame, self.upi_id_entry = ClaymorphismTheme.create_entry(form_frame, width=40)
        self.upi_id_entry_frame.grid(row=6, column=1, sticky="ew", pady=5)
        
        # UPI Name
        upi_name_label = tk.Label(form_frame, text="UPI Name:", bg=ClaymorphismTheme.BG_CARD, 
                                 font=ClaymorphismTheme.FONT_NORMAL)
        upi_name_label.grid(row=7, column=0, sticky="w", pady=5)
        
        self.upi_name_entry_frame, self.upi_name_entry = ClaymorphismTheme.create_entry(form_frame, width=40)
        self.upi_name_entry_frame.grid(row=7, column=1, sticky="ew", pady=5)
        
        # Bank name
        bank_name_label = tk.Label(form_frame, text="Bank Name:", bg=ClaymorphismTheme.BG_CARD, 
                                  font=ClaymorphismTheme.FONT_NORMAL)
        bank_name_label.grid(row=8, column=0, sticky="w", pady=5)
        
        self.bank_name_entry_frame, self.bank_name_entry = ClaymorphismTheme.create_entry(form_frame, width=40)
        self.bank_name_entry_frame.grid(row=8, column=1, sticky="ew", pady=5)
        
        # Bank account
        bank_account_label = tk.Label(form_frame, text="Account Number:", bg=ClaymorphismTheme.BG_CARD, 
                                    font=ClaymorphismTheme.FONT_NORMAL)
        bank_account_label.grid(row=9, column=0, sticky="w", pady=5)
        
        self.bank_account_entry_frame, self.bank_account_entry = ClaymorphismTheme.create_entry(form_frame, width=40)
        self.bank_account_entry_frame.grid(row=9, column=1, sticky="ew", pady=5)
        
        # Bank IFSC
        bank_ifsc_label = tk.Label(form_frame, text="IFSC Code:", bg=ClaymorphismTheme.BG_CARD, 
                                  font=ClaymorphismTheme.FONT_NORMAL)
        bank_ifsc_label.grid(row=10, column=0, sticky="w", pady=5)
        
        self.bank_ifsc_entry_frame, self.bank_ifsc_entry = ClaymorphismTheme.create_entry(form_frame, width=40)
        self.bank_ifsc_entry_frame.grid(row=10, column=1, sticky="ew", pady=5)
        
        # Bank branch
        bank_branch_label = tk.Label(form_frame, text="Branch:", bg=ClaymorphismTheme.BG_CARD, 
                                   font=ClaymorphismTheme.FONT_NORMAL)
        bank_branch_label.grid(row=11, column=0, sticky="w", pady=5)
        
        self.bank_branch_entry_frame, self.bank_branch_entry = ClaymorphismTheme.create_entry(form_frame, width=40)
        self.bank_branch_entry_frame.grid(row=11, column=1, sticky="ew", pady=5)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=ClaymorphismTheme.BG_CARD)
        button_frame.grid(row=12, column=0, columnspan=2, pady=20)
        
        save_btn_frame, save_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Save Settings",
            command=self.save_settings
        )
        save_btn_frame.pack(side="left", padx=5)
        
        reset_btn_frame, reset_btn = ClaymorphismTheme.create_button(
            button_frame, 
            text="Reset to Default",
            command=self.reset_settings
        )
        reset_btn_frame.pack(side="left", padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
        # Load current settings
        self.load_settings()
    
    def load_settings(self):
        """Load current settings from database"""
        # Company information
        company_name = self.db.get_setting("company_name") or ""
        self.name_entry.insert(0, company_name)
        
        company_address = self.db.get_setting("company_address") or ""
        self.address_text.insert(1.0, company_address)
        
        company_phone = self.db.get_setting("company_phone") or ""
        self.phone_entry.insert(0, company_phone)
        
        company_gst = self.db.get_setting("company_gst") or ""
        self.gst_entry.insert(0, company_gst)
        
        # Payment information
        upi_id = self.db.get_setting("upi_id") or ""
        self.upi_id_entry.insert(0, upi_id)
        
        upi_name = self.db.get_setting("upi_name") or ""
        self.upi_name_entry.insert(0, upi_name)
        
        bank_name = self.db.get_setting("bank_name") or ""
        self.bank_name_entry.insert(0, bank_name)
        
        bank_account = self.db.get_setting("bank_account") or ""
        self.bank_account_entry.insert(0, bank_account)
        
        bank_ifsc = self.db.get_setting("bank_ifsc") or ""
        self.bank_ifsc_entry.insert(0, bank_ifsc)
        
        bank_branch = self.db.get_setting("bank_branch") or ""
        self.bank_branch_entry.insert(0, bank_branch)
    
    def save_settings(self):
        """Save settings to database"""
        # Get form data
        company_name = self.name_entry.get().strip()
        company_address = self.address_text.get(1.0, "end").strip()
        company_phone = self.phone_entry.get().strip()
        company_gst = self.gst_entry.get().strip()
        
        upi_id = self.upi_id_entry.get().strip()
        upi_name = self.upi_name_entry.get().strip()
        bank_name = self.bank_name_entry.get().strip()
        bank_account = self.bank_account_entry.get().strip()
        bank_ifsc = self.bank_ifsc_entry.get().strip()
        bank_branch = self.bank_branch_entry.get().strip()
        
        # Save settings
        settings = [
            ("company_name", company_name),
            ("company_address", company_address),
            ("company_phone", company_phone),
            ("company_gst", company_gst),
            ("upi_id", upi_id),
            ("upi_name", upi_name),
            ("bank_name", bank_name),
            ("bank_account", bank_account),
            ("bank_ifsc", bank_ifsc),
            ("bank_branch", bank_branch)
        ]
        
        all_saved = True
        for key, value in settings:
            if not self.db.update_setting(key, value):
                all_saved = False
        
        if all_saved:
            messagebox.showinfo("Success", "Settings saved successfully.")
        else:
            messagebox.showerror("Error", "Failed to save some settings.")
    
    def reset_settings(self):
        """Reset settings to default values"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all settings to default values?"):
            # Default settings
            default_settings = {
                "company_name": "GANESH TOUGHENED INDUSTRY",
                "company_address": "Plot no:B13, Industrial Estate, Madanapalli",
                "company_phone": "9398530499, 7013374872",
                "company_gst": "37EXFPK2395CIZE",
                "upi_id": "ganeshtoughened@ybl",
                "upi_name": "GANESH TOUGHENED INDUSTRY",
                "bank_name": "State Bank of India",
                "bank_account": "12345678901",
                "bank_ifsc": "SBIN0001234",
                "bank_branch": "Madanapalli"
            }
            
            # Reset form fields
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, default_settings["company_name"])
            
            self.address_text.delete(1.0, "end")
            self.address_text.insert(1.0, default_settings["company_address"])
            
            self.phone_entry.delete(0, "end")
            self.phone_entry.insert(0, default_settings["company_phone"])
            
            self.gst_entry.delete(0, "end")
            self.gst_entry.insert(0, default_settings["company_gst"])
            
            self.upi_id_entry.delete(0, "end")
            self.upi_id_entry.insert(0, default_settings["upi_id"])
            
            self.upi_name_entry.delete(0, "end")
            self.upi_name_entry.insert(0, default_settings["upi_name"])
            
            self.bank_name_entry.delete(0, "end")
            self.bank_name_entry.insert(0, default_settings["bank_name"])
            
            self.bank_account_entry.delete(0, "end")
            self.bank_account_entry.insert(0, default_settings["bank_account"])
            
            self.bank_ifsc_entry.delete(0, "end")
            self.bank_ifsc_entry.insert(0, default_settings["bank_ifsc"])
            
            self.bank_branch_entry.delete(0, "end")
            self.bank_branch_entry.insert(0, default_settings["bank_branch"])
            
            # Save default settings
            self.save_settings()
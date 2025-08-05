import tkinter as tk
from tkinter import ttk

class ClaymorphismTheme:
    # Color palette
    BG_PRIMARY = "#f0f4f8"
    BG_SECONDARY = "#ffffff"
    BG_CARD = "#ffffff"
    BG_BUTTON = "#4a6fa5"
    BG_BUTTON_HOVER = "#3a5a8a"
    TEXT_PRIMARY = "#2d3748"
    TEXT_SECONDARY = "#4a5568"
    TEXT_LIGHT = "#ffffff"
    ACCENT = "#63b3ed"
    SHADOW = "#d1d5db"
    BORDER = "#e2e8f0"
    
    # Fonts
    FONT_TITLE = ("Segoe UI", 16, "bold")
    FONT_SUBTITLE = ("Segoe UI", 12, "bold")
    FONT_NORMAL = ("Segoe UI", 10)
    FONT_SMALL = ("Segoe UI", 9)
    
    @staticmethod
    def configure_styles(root):
        style = ttk.Style(root)
        style.theme_use('clam')
        
        # Configure styles for various widgets
        style.configure("TFrame", background=ClaymorphismTheme.BG_PRIMARY)
        style.configure("TLabel", background=ClaymorphismTheme.BG_PRIMARY, 
                       foreground=ClaymorphismTheme.TEXT_PRIMARY, 
                       font=ClaymorphismTheme.FONT_NORMAL)
        style.configure("TButton", 
                       font=ClaymorphismTheme.FONT_NORMAL,
                       padding=10,
                       relief="flat",
                       background=ClaymorphismTheme.BG_BUTTON)
        style.map("TButton",
                 background=[('active', ClaymorphismTheme.BG_BUTTON_HOVER)],
                 foreground=[('active', ClaymorphismTheme.TEXT_LIGHT)])
        style.configure("TEntry", 
                       fieldbackground=ClaymorphismTheme.BG_SECONDARY,
                       borderwidth=0,
                       relief="flat",
                       padding=8,
                       font=ClaymorphismTheme.FONT_NORMAL)
        style.configure("TCombobox", 
                       fieldbackground=ClaymorphismTheme.BG_SECONDARY,
                       background=ClaymorphismTheme.BG_SECONDARY,
                       borderwidth=0,
                       relief="flat",
                       padding=8,
                       font=ClaymorphismTheme.FONT_NORMAL)
        style.configure("TNotebook", 
                       background=ClaymorphismTheme.BG_PRIMARY,
                       borderwidth=0,
                       tabmargins=[0, 5, 0, 0])
        style.configure("TNotebook.Tab", 
                       background=ClaymorphismTheme.BG_SECONDARY,
                       padding=[12, 8],
                       borderwidth=0,
                       font=ClaymorphismTheme.FONT_NORMAL)
        style.map("TNotebook.Tab",
                 background=[('selected', ClaymorphismTheme.BG_CARD),
                             ('active', ClaymorphismTheme.BG_PRIMARY)])
        style.configure("Treeview", 
                       background=ClaymorphismTheme.BG_CARD,
                       foreground=ClaymorphismTheme.TEXT_PRIMARY,
                       fieldbackground=ClaymorphismTheme.BG_CARD,
                       borderwidth=0,
                       font=ClaymorphismTheme.FONT_NORMAL)
        style.configure("Treeview.Heading", 
                       background=ClaymorphismTheme.BG_PRIMARY,
                       foreground=ClaymorphismTheme.TEXT_PRIMARY,
                       font=ClaymorphismTheme.FONT_SUBTITLE)
        style.map("Treeview",
                 background=[('selected', ClaymorphismTheme.ACCENT)])

    @staticmethod
    def create_card(parent, text="", width=20, height=10, **kwargs):
        """Create a claymorphism-style card widget"""
        frame = tk.Frame(parent, bg=ClaymorphismTheme.BG_CARD, 
                        highlightthickness=1, 
                        highlightbackground=ClaymorphismTheme.BORDER,
                        **kwargs)
        
        # Add shadow effect
        shadow = tk.Frame(frame, bg=ClaymorphismTheme.SHADOW)
        shadow.place(x=2, y=2, relwidth=1, relheight=1)
        
        # Main card content
        card = tk.Frame(frame, bg=ClaymorphismTheme.BG_CARD, width=width, height=height)
        card.place(x=0, y=0, relwidth=1, relheight=1)
        card.pack_propagate(False)
        
        if text:
            label = tk.Label(card, text=text, bg=ClaymorphismTheme.BG_CARD, 
                            font=ClaymorphismTheme.FONT_SUBTITLE,
                            fg=ClaymorphismTheme.TEXT_PRIMARY)
            label.pack(pady=10)
        
        return frame, card

    @staticmethod
    def create_button(parent, text, command=None, **kwargs):
        """Create a claymorphism-style button"""
        button_frame = tk.Frame(parent, bg=ClaymorphismTheme.BG_PRIMARY)
        
        # Shadow effect
        shadow = tk.Frame(button_frame, bg=ClaymorphismTheme.SHADOW, 
                         highlightthickness=0)
        shadow.place(x=2, y=2, relwidth=1, relheight=1)
        
        # Button
        button = tk.Button(button_frame, text=text, 
                          bg=ClaymorphismTheme.BG_BUTTON,
                          fg=ClaymorphismTheme.TEXT_LIGHT,
                          activebackground=ClaymorphismTheme.BG_BUTTON_HOVER,
                          activeforeground=ClaymorphismTheme.TEXT_LIGHT,
                          relief="flat",
                          borderwidth=0,
                          font=ClaymorphismTheme.FONT_NORMAL,
                          padx=15,
                          pady=8,
                          cursor="hand2",
                          command=command,
                          **kwargs)
        button.pack(fill="both", expand=True)
        
        return button_frame

    @staticmethod
    def create_entry(parent, placeholder="", **kwargs):
        """Create a claymorphism-style entry widget"""
        entry_frame = tk.Frame(parent, bg=ClaymorphismTheme.BG_PRIMARY)
        
        # Shadow effect
        shadow = tk.Frame(entry_frame, bg=ClaymorphismTheme.SHADOW, 
                         highlightthickness=0)
        shadow.place(x=2, y=2, relwidth=1, relheight=1)
        
        # Entry
        entry = tk.Entry(entry_frame, 
                         bg=ClaymorphismTheme.BG_SECONDARY,
                         fg=ClaymorphismTheme.TEXT_PRIMARY,
                         relief="flat",
                         borderwidth=0,
                         font=ClaymorphismTheme.FONT_NORMAL,
                         **kwargs)
        entry.pack(fill="both", expand=True, padx=5, pady=5)
        
        if placeholder:
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda e: entry.delete(0, "end") if entry.get() == placeholder else None)
            entry.bind("<FocusOut>", lambda e: entry.insert(0, placeholder) if entry.get() == "" else None)
            entry.config(fg=ClaymorphismTheme.TEXT_SECONDARY)
        
        return entry_frame, entry
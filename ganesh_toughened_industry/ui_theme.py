import tkinter as tk
from tkinter import ttk

class ClaymorphismTheme:
    """Claymorphism UI theme with soft shadows, rounded corners, and modern colors"""
    
    @staticmethod
    def setup_theme(root):
        """Setup the claymorphism theme for the application"""
        style = ttk.Style(root)
        
        # Set the theme to 'clam' as a base
        style.theme_use('clam')
        
        # Define colors
        bg_color = "#f0f4f8"  # Light blue-gray background
        fg_color = "#2d3748"  # Dark blue-gray text
        primary_color = "#4299e1"  # Blue
        secondary_color = "#ed8936"  # Orange
        success_color = "#48bb78"  # Green
        danger_color = "#f56565"  # Red
        card_color = "#ffffff"  # White for cards
        shadow_color = "#cbd5e0"  # Light gray for shadows
        
        # Configure root window
        root.configure(bg=bg_color)
        
        # Configure styles
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 10))
        style.configure("TButton", 
                      background=primary_color, 
                      foreground="white", 
                      font=("Segoe UI", 10, "bold"),
                      borderwidth=0,
                      focuscolor="none")
        style.map("TButton",
                 background=[("active", secondary_color)],
                 foreground=[("active", "white")])
        
        style.configure("Title.TLabel", 
                      background=bg_color, 
                      foreground=fg_color, 
                      font=("Segoe UI", 16, "bold"))
        
        style.configure("Card.TFrame", 
                      background=card_color, 
                      relief="solid", 
                      borderwidth=1)
        
        style.configure("Card.TLabel", 
                      background=card_color, 
                      foreground=fg_color)
        
        style.configure("Treeview", 
                      background=card_color, 
                      foreground=fg_color, 
                      fieldbackground=card_color,
                      borderwidth=0,
                      font=("Segoe UI", 10))
        
        style.configure("Treeview.Heading", 
                      background=primary_color, 
                      foreground="white", 
                      font=("Segoe UI", 10, "bold"))
        
        style.configure("TEntry", 
                      background=card_color, 
                      foreground=fg_color, 
                      borderwidth=1,
                      relief="solid",
                      font=("Segoe UI", 10))
        
        style.configure("TCombobox", 
                      background=card_color, 
                      foreground=fg_color, 
                      fieldbackground=card_color,
                      borderwidth=1,
                      relief="solid",
                      font=("Segoe UI", 10))
        
        style.configure("TNotebook", 
                      background=bg_color, 
                      borderwidth=0)
        
        style.configure("TNotebook.Tab", 
                      background=card_color, 
                      foreground=fg_color, 
                      padding=[12, 8],
                      font=("Segoe UI", 10))
        
        style.map("TNotebook.Tab",
                 background=[("selected", primary_color)],
                 foreground=[("selected", "white")])
        
        # Success button style
        style.configure("Success.TButton", 
                      background=success_color, 
                      foreground="white")
        
        style.map("Success.TButton",
                 background=[("active", "#38a169")])
        
        # Danger button style
        style.configure("Danger.TButton", 
                      background=danger_color, 
                      foreground="white")
        
        style.map("Danger.TButton",
                 background=[("active", "#e53e3e")])
        
        # Secondary button style
        style.configure("Secondary.TButton", 
                      background=secondary_color, 
                      foreground="white")
        
        style.map("Secondary.TButton",
                 background=[("active", "#dd6b20")])
    
    @staticmethod
    def create_card(parent, text="", padding=20):
        """Create a card with claymorphism style"""
        # Create a frame for the card
        card_frame = ttk.Frame(parent, style="Card.TFrame")
        
        # Add padding inside the card
        if padding > 0:
            inner_frame = ttk.Frame(card_frame, style="Card.TFrame")
            inner_frame.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)
            
            # Add text if provided
            if text:
                ttk.Label(inner_frame, text=text, style="Card.TLabel").pack(anchor=tk.W, pady=(0, 10))
            
            return inner_frame
        
        # Add text if provided
        if text:
            ttk.Label(card_frame, text=text, style="Card.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        return card_frame
    
    @staticmethod
    def create_button(parent, text, command=None, style="TButton", width=None):
        """Create a button with claymorphism style"""
        button = ttk.Button(parent, text=text, command=command, style=style)
        
        if width:
            button.configure(width=width)
        
        return button
    
    @staticmethod
    def create_label(parent, text, style="TLabel", font=None):
        """Create a label with claymorphism style"""
        if font:
            return ttk.Label(parent, text=text, style=style, font=font)
        return ttk.Label(parent, text=text, style=style)
    
    @staticmethod
    def create_entry(parent, textvariable=None, width=None):
        """Create an entry with claymorphism style"""
        entry = ttk.Entry(parent, textvariable=textvariable)
        
        if width:
            entry.configure(width=width)
        
        return entry
    
    @staticmethod
    def create_combobox(parent, textvariable=None, values=None, width=None):
        """Create a combobox with claymorphism style"""
        combobox = ttk.Combobox(parent, textvariable=textvariable)
        
        if values:
            combobox["values"] = values
        
        if width:
            combobox.configure(width=width)
        
        return combobox
    
    @staticmethod
    def create_treeview(parent, columns, show="headings"):
        """Create a treeview with claymorphism style"""
        tree = ttk.Treeview(parent, columns=columns, show=show)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        return tree, scrollbar
    
    @staticmethod
    def create_notebook(parent):
        """Create a notebook with claymorphism style"""
        notebook = ttk.Notebook(parent)
        return notebook
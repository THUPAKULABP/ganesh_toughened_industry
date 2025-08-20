import os
import subprocess
import platform
import tkinter as tk
from tkinter import ttk, messagebox
import tempfile
import webbrowser
import shutil

class ShareUtils:
    """Utilities for sharing files across different platforms"""
    
    @staticmethod
    def share_file(file_path, parent=None):
        """
        Share a file using the platform's native sharing capabilities
        
        Args:
            file_path (str): Path to the file to share
            parent (tk.Widget): Parent widget for error messages
            
        Returns:
            bool: True if sharing was initiated successfully, False otherwise
        """
        if not os.path.exists(file_path):
            if parent:
                messagebox.showerror("Error", f"File not found: {file_path}")
            return False
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # On Windows, try using the share verb
                try:
                    os.startfile(file_path, "share")
                    return True
                except:
                    # Fallback to opening the file location
                    file_dir = os.path.dirname(file_path)
                    subprocess.call(["explorer", "/select,", file_path])
                    return True
                    
            elif system == "Darwin":  # macOS
                # On macOS, we can use the share command via AppleScript
                applescript = f'''
                tell application "Finder"
                    activate
                    share POSIX file "{file_path}"
                end tell
                '''
                subprocess.call(["osascript", "-e", applescript])
                return True
                
            else:  # Linux and other Unix-like systems
                # Try using xdg-share if available
                try:
                    subprocess.call(["xdg-share", file_path])
                    return True
                except:
                    # Fallback to opening the file location
                    file_dir = os.path.dirname(file_path)
                    subprocess.call(["xdg-open", file_dir])
                    return True
                    
        except Exception as e:
            if parent:
                messagebox.showerror("Error", f"Could not share file: {e}")
            return False
    
    @staticmethod
    def share_via_email(file_path, parent=None):
        """
        Share a file via email
        
        Args:
            file_path (str): Path to the file to share
            parent (tk.Widget): Parent widget for error messages
            
        Returns:
            bool: True if email client was opened successfully, False otherwise
        """
        if not os.path.exists(file_path):
            if parent:
                messagebox.showerror("Error", f"File not found: {file_path}")
            return False
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # Create a temporary script to open email with attachment
                temp_script = os.path.join(tempfile.gettempdir(), "email_attachment.vbs")
                with open(temp_script, "w") as f:
                    f.write(f"""
                    Set olApp = CreateObject("Outlook.Application")
                    Set olMail = olApp.CreateItem(0)
                    olMail.Subject = "Invoice from GANESH TOUGHENED INDUSTRY"
                    olMail.Body = "Please find the attached invoice."
                    olMail.Attachments.Add("{file_path}")
                    olMail.Display
                    """)
                
                subprocess.call(["cscript", temp_script])
                os.remove(temp_script)
                return True
                
            elif system == "Darwin":  # macOS
                # Use AppleScript to create email with attachment
                applescript = f'''
                tell application "Mail"
                    activate
                    set newMessage to make new outgoing message with properties {{subject:"Invoice from GANESH TOUGHENED INDUSTRY", content:"Please find the attached invoice." & return}}
                    tell newMessage
                        make new attachment with properties {{file name:"{file_path}"}}
                        visible
                    end tell
                end tell
                '''
                subprocess.call(["osascript", "-e", applescript])
                return True
                
            else:  # Linux and other Unix-like systems
                # Try with Thunderbird
                try:
                    subprocess.call(["thunderbird", "-compose", f"subject=Invoice from GANESH TOUGHENED INDUSTRY,body=Please find the attached invoice.,attachment={file_path}"])
                    return True
                except:
                    # Try with Evolution
                    try:
                        subprocess.call(["evolution", f"mailto:?subject=Invoice from GANESH TOUGHENED INDUSTRY&body=Please find the attached invoice.&attachment={file_path}"])
                        return True
                    except:
                        # Fallback to xdg-open with mailto:
                        try:
                            subprocess.call(["xdg-open", f"mailto:?subject=Invoice from GANESH TOUGHENED INDUSTRY&body=Please find the attached invoice.&attachment={file_path}"])
                            return True
                        except:
                            if parent:
                                messagebox.showinfo("Info", "Please open your email client and attach the file manually.")
                            return False
                    
        except Exception as e:
            if parent:
                messagebox.showerror("Error", f"Could not open email client: {e}")
            return False
    
    @staticmethod
    def share_via_whatsapp(file_path, parent=None):
        """Share a file via WhatsApp"""
        if not os.path.exists(file_path):
            if parent:
                messagebox.showerror("Error", f"File not found: {file_path}")
            return False
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # Try to open WhatsApp Desktop with the file
                try:
                    # Check if WhatsApp Desktop is installed
                    whatsapp_path = os.path.expanduser("~\\AppData\\Local\\WhatsApp\\WhatsApp.exe")
                    if os.path.exists(whatsapp_path):
                        # Copy file to a temporary location that WhatsApp can access
                        temp_dir = os.path.join(tempfile.gettempdir(), "whatsapp_share")
                        os.makedirs(temp_dir, exist_ok=True)
                        temp_file = os.path.join(temp_dir, os.path.basename(file_path))
                        shutil.copy2(file_path, temp_file)
                        
                        # Open WhatsApp
                        subprocess.Popen([whatsapp_path])
                        
                        if parent:
                            messagebox.showinfo("Info", f"WhatsApp has been opened. Please send the file: {temp_file}")
                        return True
                    else:
                        # Fallback to WhatsApp Web
                        web_whatsapp = "https://web.whatsapp.com/"
                        webbrowser.open(web_whatsapp)
                        if parent:
                            messagebox.showinfo("Info", "Please attach the file manually in WhatsApp Web.")
                        return True
                except Exception as e:
                    # Fallback to WhatsApp Web
                    web_whatsapp = "https://web.whatsapp.com/"
                    webbrowser.open(web_whatsapp)
                    if parent:
                        messagebox.showinfo("Info", "Please attach the file manually in WhatsApp Web.")
                    return True
                    
            elif system == "Darwin":  # macOS
                # Try to open WhatsApp Desktop with the file
                try:
                    # Check if WhatsApp Desktop is installed
                    whatsapp_path = "/Applications/WhatsApp.app"
                    if os.path.exists(whatsapp_path):
                        # Copy file to a temporary location that WhatsApp can access
                        temp_dir = os.path.join(tempfile.gettempdir(), "whatsapp_share")
                        os.makedirs(temp_dir, exist_ok=True)
                        temp_file = os.path.join(temp_dir, os.path.basename(file_path))
                        shutil.copy2(file_path, temp_file)
                        
                        # Open WhatsApp
                        subprocess.Popen(["open", whatsapp_path])
                        
                        if parent:
                            messagebox.showinfo("Info", f"WhatsApp has been opened. Please send the file: {temp_file}")
                        return True
                    else:
                        # Fallback to WhatsApp Web
                        web_whatsapp = "https://web.whatsapp.com/"
                        webbrowser.open(web_whatsapp)
                        if parent:
                            messagebox.showinfo("Info", "Please attach the file manually in WhatsApp Web.")
                        return True
                except Exception as e:
                    # Fallback to WhatsApp Web
                    web_whatsapp = "https://web.whatsapp.com/"
                    webbrowser.open(web_whatsapp)
                    if parent:
                        messagebox.showinfo("Info", "Please attach the file manually in WhatsApp Web.")
                    return True
                    
            else:  # Linux and other Unix-like systems
                # Try to open WhatsApp Desktop with the file
                try:
                    # Check if WhatsApp Desktop is installed
                    result = subprocess.run(["which", "whatsapp-desktop"], capture_output=True, text=True)
                    if result.returncode == 0:
                        # Copy file to a temporary location that WhatsApp can access
                        temp_dir = os.path.join(tempfile.gettempdir(), "whatsapp_share")
                        os.makedirs(temp_dir, exist_ok=True)
                        temp_file = os.path.join(temp_dir, os.path.basename(file_path))
                        shutil.copy2(file_path, temp_file)
                        
                        # Open WhatsApp
                        subprocess.Popen(["whatsapp-desktop"])
                        
                        if parent:
                            messagebox.showinfo("Info", f"WhatsApp has been opened. Please send the file: {temp_file}")
                        return True
                    else:
                        # Fallback to WhatsApp Web
                        web_whatsapp = "https://web.whatsapp.com/"
                        webbrowser.open(web_whatsapp)
                        if parent:
                            messagebox.showinfo("Info", "Please attach the file manually in WhatsApp Web.")
                        return True
                except Exception as e:
                    # Fallback to WhatsApp Web
                    web_whatsapp = "https://web.whatsapp.com/"
                    webbrowser.open(web_whatsapp)
                    if parent:
                        messagebox.showinfo("Info", "Please attach the file manually in WhatsApp Web.")
                    return True
                    
        except Exception as e:
            if parent:
                messagebox.showerror("Error", f"Could not open WhatsApp: {e}")
            return False
    
    @staticmethod
    def share_dialog(file_path, parent=None):
        """
        Show a dialog with sharing options
        
        Args:
            file_path (str): Path to the file to share
            parent (tk.Widget): Parent widget for the dialog
        
        Returns:
            bool: True if sharing was initiated successfully, False otherwise
        """
        if not os.path.exists(file_path):
            if parent:
                messagebox.showerror("Error", f"File not found: {file_path}")
            return False
        
        # Create a more spacious dialog
        dialog = tk.Toplevel(parent)
        dialog.title("Share Bill")
        dialog.geometry("400x300")  # Increased size
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(parent)
        dialog.grab_set()
        
        # Add a title
        title_label = ttk.Label(dialog, text="Choose how to share this bill:", font=("Arial", 12, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Frame for buttons with more padding
        button_frame = ttk.Frame(dialog, padding="20")
        button_frame.pack(fill=tk.BOTH, expand=True)
        
        # System share button
        system_share_btn = ttk.Button(
            button_frame, 
            text="System Share",
            command=lambda: (
                ShareUtils.share_file(file_path, parent) and dialog.destroy()
            )
        )
        system_share_btn.pack(fill=tk.X, pady=8)
        
        # Email share button
        email_share_btn = ttk.Button(
            button_frame, 
            text="Share via Email",
            command=lambda: (
                ShareUtils.share_via_email(file_path, parent) and dialog.destroy()
            )
        )
        email_share_btn.pack(fill=tk.X, pady=8)
        
        # WhatsApp share button
        whatsapp_share_btn = ttk.Button(
            button_frame, 
            text="Share via WhatsApp",
            command=lambda: (
                ShareUtils.share_via_whatsapp(file_path, parent) and dialog.destroy()
            )
        )
        whatsapp_share_btn.pack(fill=tk.X, pady=8)
        
        # Cancel button
        cancel_btn = ttk.Button(
            button_frame, 
            text="Cancel",
            command=dialog.destroy
        )
        cancel_btn.pack(fill=tk.X, pady=8)
        
        # Wait for dialog to close
        parent.wait_window(dialog)
        
        return True
    
    @staticmethod
    def copy_to_clipboard(file_path, parent=None):
        """
        Copy file to clipboard
        
        Args:
            file_path (str): Path to the file to copy
            parent (tk.Widget): Parent widget for error messages
            
        Returns:
            bool: True if file was copied to clipboard successfully, False otherwise
        """
        if not os.path.exists(file_path):
            if parent:
                messagebox.showerror("Error", f"File not found: {file_path}")
            return False
        
        try:
            system = platform.system()
            
            if system == "Windows":
                import win32clipboard
                import win32con
                
                # Set clipboard data
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_HDROP, file_path)
                win32clipboard.CloseClipboard()
                
                if parent:
                    messagebox.showinfo("Success", "File copied to clipboard. You can now paste it in other applications.")
                return True
                
            elif system == "Darwin":  # macOS
                # Use pbcopy to copy file path
                subprocess.run(["pbcopy"], input=file_path.encode('utf-8'))
                
                if parent:
                    messagebox.showinfo("Success", "File path copied to clipboard. You can now paste it in other applications.")
                return True
                
            else:  # Linux and other Unix-like systems
                # Use xclip to copy file path
                try:
                    subprocess.run(["xclip", "-selection", "clipboard"], input=file_path.encode('utf-8'))
                    
                    if parent:
                        messagebox.showinfo("Success", "File path copied to clipboard. You can now paste it in other applications.")
                    return True
                except:
                    if parent:
                        messagebox.showinfo("Info", "Please manually copy the file: " + file_path)
                    return False
                    
        except Exception as e:
            if parent:
                messagebox.showerror("Error", f"Could not copy file to clipboard: {e}")
            return False
import os
import sqlite3
import shutil
import zipfile
from datetime import datetime, date, timedelta
import json

class BackupManager:
    """Backup system for the application"""
    
    def __init__(self, db_path, backup_dir="backups"):
        """Initialize backup manager"""
        self.db_path = db_path
        self.backup_dir = backup_dir
        
        # Create backup directory if it doesn't exist
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self):
        """Create a backup of the database"""
        try:
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.zip"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Create a zip file
            with zipfile.ZipFile(backup_path, 'w') as zipf:
                # Add database file
                zipf.write(self.db_path, os.path.basename(self.db_path))
                
                # Add config files if they exist
                config_dir = "config"
                if os.path.exists(config_dir):
                    for root, dirs, files in os.walk(config_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(config_dir))
                            zipf.write(file_path, arcname)
            
            # Update last backup date in settings
            self.update_last_backup_date()
            
            return backup_path
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    def restore_backup(self, backup_path):
        """Restore database from backup"""
        try:
            # Extract the backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Extract all files
                zipf.extractall(os.path.dirname(self.db_path))
            
            return True
            
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def list_backups(self):
        """List all available backups"""
        try:
            backups = []
            
            for file in os.listdir(self.backup_dir):
                if file.endswith(".zip"):
                    file_path = os.path.join(self.backup_dir, file)
                    file_stat = os.stat(file_path)
                    
                    # Extract timestamp from filename
                    timestamp_str = file.replace("backup_", "").replace(".zip", "")
                    try:
                        timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        date_str = timestamp.strftime("%d/%m/%Y %H:%M:%S")
                    except ValueError:
                        date_str = "Unknown"
                    
                    backups.append({
                        "filename": file,
                        "path": file_path,
                        "date": date_str,
                        "size": file_stat.st_size
                    })
            
            # Sort by date (newest first)
            backups.sort(key=lambda x: x["filename"], reverse=True)
            
            return backups
            
        except Exception as e:
            print(f"Error listing backups: {e}")
            return []
    
    def delete_backup(self, backup_path):
        """Delete a backup file"""
        try:
            os.remove(backup_path)
            return True
        except Exception as e:
            print(f"Error deleting backup: {e}")
            return False
    
    def check_backup_needed(self):
        """Check if a backup is needed (weekly)"""
        try:
            # Get last backup date from settings
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = 'last_backup'")
                result = cursor.fetchone()
                
                if result:
                    last_backup_str = result[0]
                    if last_backup_str == "Never":
                        return True
                    
                    last_backup = datetime.strptime(last_backup_str, "%Y-%m-%d")
                    
                    # Check if a week has passed
                    if datetime.now() - last_backup >= timedelta(days=7):
                        return True
                
                return True
                
        except Exception as e:
            print(f"Error checking backup needed: {e}")
            return True
    
    def update_last_backup_date(self):
        """Update the last backup date in settings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if setting exists
                cursor.execute("SELECT 1 FROM settings WHERE key = 'last_backup'")
                if cursor.fetchone():
                    # Update existing setting
                    cursor.execute("""
                    UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE key = 'last_backup'
                    """, (datetime.now().strftime("%Y-%m-%d"),))
                else:
                    # Insert new setting
                    cursor.execute("""
                    INSERT INTO settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    """, ("last_backup", datetime.now().strftime("%Y-%m-%d")))
                
                conn.commit()
                
        except Exception as e:
            print(f"Error updating last backup date: {e}")
    
    def auto_backup(self):
        """Automatically create backup if needed"""
        if self.check_backup_needed():
            backup_path = self.create_backup()
            if backup_path:
                print(f"Automatic backup created: {backup_path}")
                return True
        return False
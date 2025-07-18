#!/usr/bin/env python3
"""
Launcher for Uma Musume PC Automation Tools
Provides easy access to all automation utilities
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading

class AutomationLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Uma Musume PC Automation - Launcher")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Uma Musume PC Automation", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Tool buttons
        tools_frame = ttk.LabelFrame(main_frame, text="Tools", padding="20")
        tools_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Main automation tool
        automation_btn = ttk.Button(tools_frame, text="🎮 Main Automation Tool", 
                                   command=self.launch_automation, width=30)
        automation_btn.grid(row=0, column=0, pady=10)
        
        # Template creator
        template_btn = ttk.Button(tools_frame, text="🖼️ Template Creator", 
                                 command=self.launch_template_creator, width=30)
        template_btn.grid(row=1, column=0, pady=10)
        
        # Installation test
        test_btn = ttk.Button(tools_frame, text="🔧 Test Installation", 
                             command=self.run_installation_test, width=30)
        test_btn.grid(row=2, column=0, pady=10)
        
        # Documentation
        docs_btn = ttk.Button(tools_frame, text="📖 View Documentation", 
                             command=self.open_documentation, width=30)
        docs_btn.grid(row=3, column=0, pady=10)
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.status_label = ttk.Label(status_frame, text="Ready", font=("Arial", 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Quick start guide
        guide_frame = ttk.LabelFrame(main_frame, text="Quick Start Guide", padding="10")
        guide_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        guide_text = """
1. First time? Run "Test Installation" to check setup
2. Create UI templates using "Template Creator"
3. Launch "Main Automation Tool" to start automation
4. Configure settings and start automation
        """
        guide_label = ttk.Label(guide_frame, text=guide_text, justify=tk.LEFT, font=("Arial", 9))
        guide_label.grid(row=0, column=0, sticky=tk.W)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
    def launch_automation(self):
        """Launch the main automation tool"""
        try:
            self.status_label.config(text="Launching automation tool...")
            self.root.update()
            
            # Run in separate thread to avoid blocking GUI
            def run_automation():
                try:
                    subprocess.run([sys.executable, "uma_automation.py"], check=True)
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Failed to launch automation tool: {e}")
                except FileNotFoundError:
                    messagebox.showerror("Error", "uma_automation.py not found")
            
            thread = threading.Thread(target=run_automation, daemon=True)
            thread.start()
            
            self.status_label.config(text="Automation tool launched")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch automation tool: {e}")
            self.status_label.config(text="Error launching automation tool")
    
    def launch_template_creator(self):
        """Launch the template creator tool"""
        try:
            self.status_label.config(text="Launching template creator...")
            self.root.update()
            
            def run_template_creator():
                try:
                    subprocess.run([sys.executable, "template_creator.py"], check=True)
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Failed to launch template creator: {e}")
                except FileNotFoundError:
                    messagebox.showerror("Error", "template_creator.py not found")
            
            thread = threading.Thread(target=run_template_creator, daemon=True)
            thread.start()
            
            self.status_label.config(text="Template creator launched")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch template creator: {e}")
            self.status_label.config(text="Error launching template creator")
    
    def run_installation_test(self):
        """Run the installation test"""
        try:
            self.status_label.config(text="Running installation test...")
            self.root.update()
            
            def run_test():
                try:
                    result = subprocess.run([sys.executable, "test_installation.py"], 
                                          capture_output=True, text=True, check=True)
                    messagebox.showinfo("Installation Test", f"Test completed successfully!\n\n{result.stdout}")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Installation Test", f"Test failed:\n\n{e.stdout}\n{e.stderr}")
                except FileNotFoundError:
                    messagebox.showerror("Error", "test_installation.py not found")
            
            thread = threading.Thread(target=run_test, daemon=True)
            thread.start()
            
            self.status_label.config(text="Installation test completed")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run installation test: {e}")
            self.status_label.config(text="Error running installation test")
    
    def open_documentation(self):
        """Open the README documentation"""
        try:
            readme_path = "README.md"
            if os.path.exists(readme_path):
                if sys.platform == "darwin":  # macOS
                    subprocess.run(["open", readme_path])
                elif sys.platform == "win32":  # Windows
                    subprocess.run(["start", readme_path], shell=True)
                else:  # Linux
                    subprocess.run(["xdg-open", readme_path])
                
                self.status_label.config(text="Documentation opened")
            else:
                messagebox.showwarning("Warning", "README.md not found")
                self.status_label.config(text="README.md not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open documentation: {e}")
            self.status_label.config(text="Error opening documentation")
    
    def run(self):
        """Run the launcher"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("Uma Musume PC Automation - Launcher")
    print("=" * 40)
    
    app = AutomationLauncher()
    app.run()

if __name__ == "__main__":
    main() 
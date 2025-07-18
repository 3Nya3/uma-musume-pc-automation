#!/usr/bin/env python3
"""
Template Creator Utility for Uma Musume PC Automation
Helps users create template images for UI element recognition
"""

import cv2
import numpy as np
import pyautogui
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageGrab
import os
import json
from typing import Tuple, Optional

class TemplateCreator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Template Creator - Uma Musume PC Automation")
        self.root.geometry("800x600")
        
        self.templates_dir = "templates"
        self.current_screenshot = None
        self.selection_start = None
        self.selection_end = None
        self.drawing = False
        
        # Ensure templates directory exists
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
        
        self.setup_gui()
        self.load_template_list()
    
    def setup_gui(self):
        """Setup the GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Template Creator", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left panel - Controls
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Screenshot controls
        screenshot_frame = ttk.LabelFrame(left_panel, text="Screenshot", padding="10")
        screenshot_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(screenshot_frame, text="Capture Screen", command=self.capture_screen).grid(row=0, column=0, pady=5)
        ttk.Button(screenshot_frame, text="Capture Game Window", command=self.capture_game_window).grid(row=1, column=0, pady=5)
        
        # Template controls
        template_frame = ttk.LabelFrame(left_panel, text="Template", padding="10")
        template_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(template_frame, text="Template Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.template_name = tk.StringVar()
        ttk.Entry(template_frame, textvariable=self.template_name, width=20).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        ttk.Button(template_frame, text="Save Selection", command=self.save_template).grid(row=2, column=0, pady=10)
        ttk.Button(template_frame, text="Clear Selection", command=self.clear_selection).grid(row=3, column=0, pady=5)
        
        # Template list
        list_frame = ttk.LabelFrame(left_panel, text="Existing Templates", padding="10")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.template_listbox = tk.Listbox(list_frame, height=10, width=25)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.template_listbox.yview)
        self.template_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.template_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        ttk.Button(list_frame, text="Delete Selected", command=self.delete_template).grid(row=1, column=0, pady=5)
        
        # Right panel - Image display
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Image display
        image_frame = ttk.LabelFrame(right_panel, text="Screenshot", padding="5")
        image_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.canvas = tk.Canvas(image_frame, bg="white", cursor="cross")
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Instructions
        instructions_frame = ttk.LabelFrame(right_panel, text="Instructions", padding="10")
        instructions_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        instructions_text = """
1. Click "Capture Screen" or "Capture Game Window"
2. Click and drag to select the UI element
3. Enter a template name (e.g., "training_button")
4. Click "Save Selection" to save the template
5. Repeat for all required UI elements
        """
        ttk.Label(instructions_frame, text=instructions_text, justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        left_panel.rowconfigure(2, weight=1)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        right_panel.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)
        image_frame.columnconfigure(0, weight=1)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
    
    def capture_screen(self):
        """Capture the entire screen"""
        try:
            screenshot = ImageGrab.grab()
            self.display_screenshot(screenshot)
            messagebox.showinfo("Success", "Screenshot captured successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture screenshot: {e}")
    
    def capture_game_window(self):
        """Capture only the game window"""
        try:
            # Try to find Uma Musume window
            from window_detector import WindowDetector
            detector = WindowDetector()
            game_region = detector.get_game_region()
            
            if game_region:
                screenshot = ImageGrab.grab(bbox=game_region)
                self.display_screenshot(screenshot)
                messagebox.showinfo("Success", "Game window captured successfully!")
            else:
                messagebox.showwarning("Warning", "Game window not detected. Capturing full screen instead.")
                self.capture_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture game window: {e}")
            self.capture_screen()
    
    def display_screenshot(self, screenshot: Image.Image):
        """Display screenshot on canvas"""
        # Resize screenshot to fit canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not yet sized, use default
            canvas_width, canvas_height = 600, 400
        
        # Calculate scale to fit image in canvas
        img_width, img_height = screenshot.size
        scale = min(canvas_width / img_width, canvas_height / img_height)
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Resize image
        screenshot_resized = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.photo_image = ImageTk.PhotoImage(screenshot_resized)
        self.current_screenshot = screenshot
        
        # Clear canvas and display image
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        
        # Store scale for coordinate conversion
        self.scale_factor = scale
    
    def on_mouse_down(self, event):
        """Handle mouse button press"""
        self.selection_start = (event.x, event.y)
        self.drawing = True
        self.canvas.delete("selection")
    
    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        if self.drawing and self.selection_start:
            self.canvas.delete("selection")
            x1, y1 = self.selection_start
            x2, y2 = event.x, event.y
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2, tags="selection")
    
    def on_mouse_up(self, event):
        """Handle mouse button release"""
        if self.drawing and self.selection_start:
            self.selection_end = (event.x, event.y)
            self.drawing = False
            
            # Draw final selection rectangle
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2, tags="selection")
    
    def save_template(self):
        """Save the selected region as a template"""
        if not self.current_screenshot or not self.selection_start or not self.selection_end:
            messagebox.showwarning("Warning", "Please capture a screenshot and select a region first.")
            return
        
        template_name = self.template_name.get().strip()
        if not template_name:
            messagebox.showwarning("Warning", "Please enter a template name.")
            return
        
        try:
            # Convert canvas coordinates to image coordinates
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            
            # Convert to image coordinates
            img_x1 = int(x1 / self.scale_factor)
            img_y1 = int(y1 / self.scale_factor)
            img_x2 = int(x2 / self.scale_factor)
            img_y2 = int(y2 / self.scale_factor)
            
            # Ensure coordinates are in correct order
            img_x1, img_x2 = min(img_x1, img_x2), max(img_x1, img_x2)
            img_y1, img_y2 = min(img_y1, img_y2), max(img_y1, img_y2)
            
            # Crop the image
            template_image = self.current_screenshot.crop((img_x1, img_y1, img_x2, img_y2))
            
            # Save template
            template_path = os.path.join(self.templates_dir, f"{template_name}.png")
            template_image.save(template_path)
            
            messagebox.showinfo("Success", f"Template saved as {template_name}.png")
            
            # Clear selection and name
            self.clear_selection()
            self.template_name.set("")
            
            # Refresh template list
            self.load_template_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save template: {e}")
    
    def clear_selection(self):
        """Clear the current selection"""
        self.selection_start = None
        self.selection_end = None
        self.canvas.delete("selection")
    
    def load_template_list(self):
        """Load and display existing templates"""
        self.template_listbox.delete(0, tk.END)
        
        if os.path.exists(self.templates_dir):
            for filename in os.listdir(self.templates_dir):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    template_name = os.path.splitext(filename)[0]
                    self.template_listbox.insert(tk.END, template_name)
    
    def delete_template(self):
        """Delete the selected template"""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a template to delete.")
            return
        
        template_name = self.template_listbox.get(selection[0])
        template_path = os.path.join(self.templates_dir, f"{template_name}.png")
        
        if os.path.exists(template_path):
            try:
                os.remove(template_path)
                messagebox.showinfo("Success", f"Template {template_name} deleted.")
                self.load_template_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete template: {e}")
    
    def run(self):
        """Run the template creator"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("Template Creator for Uma Musume PC Automation")
    print("=" * 50)
    
    app = TemplateCreator()
    app.run()

if __name__ == "__main__":
    main() 
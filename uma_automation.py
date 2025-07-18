#!/usr/bin/env python3
"""
Uma Musume PC Automation Tool
A Python-based automation tool for Uma Musume Pretty Derby Global version on PC
"""

import cv2
import numpy as np
import pyautogui
import pytesseract
import time
import json
import logging
from PIL import Image, ImageGrab
from typing import Tuple, Optional, List, Dict
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import configparser
import os
from window_detector import WindowDetector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UmaMusumeAutomation:
    def __init__(self):
        self.running = False
        self.config = self.load_config()
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Window detection
        self.window_detector = WindowDetector()
        self.game_region = None
        
        # OCR Configuration for English text
        pytesseract.pytesseract.tesseract_cmd = self.config.get('OCR', 'tesseract_path', fallback='tesseract')
        
        # UI element templates (will be loaded from templates folder)
        self.templates = {}
        self.load_templates()
        
        # Game state tracking
        self.current_screen = "unknown"
        self.turn_count = 0
        self.stats = {
            'speed': 0, 'stamina': 0, 'power': 0, 
            'guts': 0, 'intelligence': 0, 'technique': 0
        }
        
        # Performance tracking
        self.session_stats = {
            'training_sessions': 0,
            'races_completed': 0,
            'events_handled': 0,
            'errors_encountered': 0
        }
        
    def load_config(self) -> configparser.ConfigParser:
        """Load configuration from config.ini"""
        config = configparser.ConfigParser()
        config_file = 'config.ini'
        
        if os.path.exists(config_file):
            config.read(config_file)
        else:
            # Create default config
            config['OCR'] = {
                'tesseract_path': 'tesseract',
                'confidence_threshold': '0.7'
            }
            config['Automation'] = {
                'click_delay': '0.5',
                'screenshot_delay': '1.0',
                'max_retries': '3'
            }
            config['Training'] = {
                'priority_stats': 'speed,stamina,power',
                'skip_races': 'false',
                'farm_fans': 'false'
            }
            
            with open(config_file, 'w') as f:
                config.write(f)
        
        return config
    
    def load_templates(self):
        """Load UI element templates from templates folder"""
        templates_dir = 'templates'
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
            logger.info(f"Created templates directory: {templates_dir}")
            return
        
        for filename in os.listdir(templates_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                template_name = os.path.splitext(filename)[0]
                template_path = os.path.join(templates_dir, filename)
                self.templates[template_name] = cv2.imread(template_path, cv2.IMREAD_COLOR)
                logger.info(f"Loaded template: {template_name}")
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Capture screen or region of screen"""
        try:
            # Update game region if window detection is enabled
            if self.config.getboolean('Automation', 'window_detection_enabled', fallback=True):
                self.game_region = self.window_detector.get_game_region()
            
            # Use game region if available and no specific region requested
            if region is None and self.game_region:
                region = self.game_region
                logger.debug(f"Using game region: {region}")
            
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            # Convert PIL image to OpenCV format
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            return screenshot_cv
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            return None
    
    def find_template(self, template_name: str, screenshot: np.ndarray, 
                     threshold: float = 0.8) -> Optional[Tuple[int, int, int, int]]:
        """Find template in screenshot using template matching"""
        if template_name not in self.templates:
            logger.warning(f"Template {template_name} not found")
            return None
        
        template = self.templates[template_name]
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            h, w = template.shape[:2]
            x, y = max_loc
            return (x, y, x + w, y + h)
        
        return None
    
    def ocr_text(self, image: np.ndarray, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """Extract text from image using OCR"""
        try:
            if region:
                x1, y1, x2, y2 = region
                image = image[y1:y2, x1:x2]
            
            # Convert to grayscale for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing for better text recognition
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Extract text
            text = pytesseract.image_to_string(gray, config='--psm 6')
            return text.strip()
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""
    
    def click_at(self, x: int, y: int, delay: float = 0.5):
        """Click at specified coordinates"""
        try:
            # Focus game window before clicking
            if self.config.getboolean('Automation', 'window_detection_enabled', fallback=True):
                self.window_detector.focus_game_window()
                time.sleep(0.1)  # Brief delay for window focus
            
            pyautogui.click(x, y)
            time.sleep(delay)
            logger.info(f"Clicked at ({x}, {y})")
        except Exception as e:
            logger.error(f"Failed to click at ({x}, {y}): {e}")
            self.session_stats['errors_encountered'] += 1
    
    def detect_screen(self, screenshot: np.ndarray) -> str:
        """Detect current screen based on UI elements"""
        # Check for main menu
        if self.find_template('main_menu', screenshot):
            return "main_menu"
        
        # Check for training screen
        if self.find_template('training_screen', screenshot):
            return "training_screen"
        
        # Check for race screen
        if self.find_template('race_screen', screenshot):
            return "race_screen"
        
        # Check for event screen
        if self.find_template('event_screen', screenshot):
            return "event_screen"
        
        return "unknown"
    
    def handle_main_menu(self):
        """Handle main menu actions"""
        logger.info("Handling main menu")
        screenshot = self.capture_screen()
        
        # Look for training button
        training_btn = self.find_template('training_button', screenshot)
        if training_btn:
            x, y = (training_btn[0] + training_btn[2]) // 2, (training_btn[1] + training_btn[3]) // 2
            self.click_at(x, y)
            return True
        
        return False
    
    def handle_training_screen(self):
        """Handle training screen actions"""
        logger.info("Handling training screen")
        screenshot = self.capture_screen()
        
        # Check available training options
        training_options = ['speed_train', 'stamina_train', 'power_train', 
                          'guts_train', 'intelligence_train', 'technique_train']
        
        for option in training_options:
            btn = self.find_template(option, screenshot)
            if btn:
                x, y = (btn[0] + btn[2]) // 2, (btn[1] + btn[3]) // 2
                self.click_at(x, y)
                return True
        
        return False
    
    def handle_event_screen(self):
        """Handle event screen actions"""
        logger.info("Handling event screen")
        screenshot = self.capture_screen()
        
        # Look for confirm/continue button
        confirm_btn = self.find_template('confirm_button', screenshot)
        if confirm_btn:
            x, y = (confirm_btn[0] + confirm_btn[2]) // 2, (confirm_btn[1] + confirm_btn[3]) // 2
            self.click_at(x, y)
            return True
        
        return False
    
    def handle_race_screen(self):
        """Handle race screen actions"""
        logger.info("Handling race screen")
        screenshot = self.capture_screen()
        
        # Check if we should skip race
        if self.config.getboolean('Training', 'skip_races', fallback=False):
            skip_btn = self.find_template('skip_race_button', screenshot)
            if skip_btn:
                x, y = (skip_btn[0] + skip_btn[2]) // 2, (skip_btn[1] + skip_btn[3]) // 2
                self.click_at(x, y)
                return True
        
        # Look for race start button
        start_btn = self.find_template('race_start_button', screenshot)
        if start_btn:
            x, y = (start_btn[0] + start_btn[2]) // 2, (start_btn[1] + start_btn[3]) // 2
            self.click_at(x, y)
            return True
        
        return False
    
    def handle_race_result(self):
        """Handle race result screen"""
        logger.info("Handling race result screen")
        screenshot = self.capture_screen()
        
        # Look for continue button to proceed
        continue_btn = self.find_template('continue_button', screenshot)
        if continue_btn:
            x, y = (continue_btn[0] + continue_btn[2]) // 2, (continue_btn[1] + continue_btn[3]) // 2
            self.click_at(x, y)
            self.session_stats['races_completed'] += 1
            return True
        
        return False
    
    def handle_training_result(self):
        """Handle training result screen"""
        logger.info("Handling training result screen")
        screenshot = self.capture_screen()
        
        # Look for continue button
        continue_btn = self.find_template('continue_button', screenshot)
        if continue_btn:
            x, y = (continue_btn[0] + continue_btn[2]) // 2, (continue_btn[1] + continue_btn[3]) // 2
            self.click_at(x, y)
            self.session_stats['training_sessions'] += 1
            return True
        
        return False
    
    def handle_choice_screen(self):
        """Handle choice/event screen with multiple options"""
        logger.info("Handling choice screen")
        screenshot = self.capture_screen()
        
        # Try to read the choice text using OCR
        choice_text = self.ocr_text(screenshot)
        logger.info(f"Choice text: {choice_text}")
        
        # Look for the first option (usually the most positive one)
        option_btn = self.find_template('choice_option_1', screenshot)
        if option_btn:
            x, y = (option_btn[0] + option_btn[2]) // 2, (option_btn[1] + option_btn[3]) // 2
            self.click_at(x, y)
            self.session_stats['events_handled'] += 1
            return True
        
        return False
    
    def check_for_errors(self, screenshot: np.ndarray) -> bool:
        """Check for common error screens or dialogs"""
        # Check for error dialogs
        error_indicators = ['error', 'failed', 'connection lost', 'retry']
        screenshot_text = self.ocr_text(screenshot).lower()
        
        for indicator in error_indicators:
            if indicator in screenshot_text:
                logger.warning(f"Error detected: {indicator}")
                return True
        
        return False
    
    def get_session_stats(self) -> Dict[str, int]:
        """Get current session statistics"""
        return self.session_stats.copy()
    
    def run_automation(self):
        """Main automation loop"""
        logger.info("Starting Uma Musume automation")
        self.running = True
        
        # Try to detect game window
        if self.config.getboolean('Automation', 'window_detection_enabled', fallback=True):
            self.game_region = self.window_detector.get_game_region()
            if self.game_region:
                logger.info(f"Game window detected: {self.game_region}")
            else:
                logger.warning("Game window not detected, using full screen")
        
        consecutive_unknown_screens = 0
        max_unknown_screens = 10
        
        while self.running:
            try:
                screenshot = self.capture_screen()
                if screenshot is None:
                    logger.warning("Failed to capture screenshot")
                    time.sleep(1)
                    continue
                
                # Check for errors first
                if self.check_for_errors(screenshot):
                    logger.warning("Error detected, waiting before retry")
                    time.sleep(3)
                    continue
                
                current_screen = self.detect_screen(screenshot)
                logger.info(f"Current screen: {current_screen}")
                
                # Reset unknown screen counter if we found a known screen
                if current_screen != "unknown":
                    consecutive_unknown_screens = 0
                else:
                    consecutive_unknown_screens += 1
                    if consecutive_unknown_screens >= max_unknown_screens:
                        logger.error("Too many unknown screens, stopping automation")
                        break
                
                # Handle different screens
                handled = False
                if current_screen == "main_menu":
                    handled = self.handle_main_menu()
                elif current_screen == "training_screen":
                    handled = self.handle_training_screen()
                elif current_screen == "event_screen":
                    handled = self.handle_event_screen()
                elif current_screen == "race_screen":
                    handled = self.handle_race_screen()
                elif current_screen == "race_result":
                    handled = self.handle_race_result()
                elif current_screen == "training_result":
                    handled = self.handle_training_result()
                elif current_screen == "choice_screen":
                    handled = self.handle_choice_screen()
                else:
                    logger.warning(f"Unknown screen detected: {current_screen}")
                    # Try to click continue button as fallback
                    continue_btn = self.find_template('continue_button', screenshot)
                    if continue_btn:
                        x, y = (continue_btn[0] + continue_btn[2]) // 2, (continue_btn[1] + continue_btn[3]) // 2
                        self.click_at(x, y)
                        handled = True
                
                # If no action was taken, wait a bit longer
                if not handled:
                    time.sleep(float(self.config.get('Automation', 'screenshot_delay', fallback='1.0')))
                else:
                    time.sleep(0.5)  # Shorter delay after successful action
                
            except KeyboardInterrupt:
                logger.info("Automation stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in automation loop: {e}")
                self.session_stats['errors_encountered'] += 1
                time.sleep(2)
        
        self.running = False
        logger.info("Automation stopped")
        logger.info(f"Session stats: {self.get_session_stats()}")

class AutomationGUI:
    def __init__(self):
        self.automation = UmaMusumeAutomation()
        self.root = tk.Tk()
        self.root.title("Uma Musume PC Automation")
        self.root.geometry("600x400")
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Uma Musume PC Automation", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Settings section
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Priority stats
        ttk.Label(settings_frame, text="Priority Stats:").grid(row=0, column=0, sticky=tk.W)
        self.priority_stats = tk.StringVar(value="speed,stamina,power")
        priority_entry = ttk.Entry(settings_frame, textvariable=self.priority_stats, width=30)
        priority_entry.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        
        # Skip races checkbox
        self.skip_races = tk.BooleanVar()
        skip_races_cb = ttk.Checkbutton(settings_frame, text="Skip Races", variable=self.skip_races)
        skip_races_cb.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Farm fans checkbox
        self.farm_fans = tk.BooleanVar()
        farm_fans_cb = ttk.Checkbutton(settings_frame, text="Farm Fans", variable=self.farm_fans)
        farm_fans_cb.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start Automation", command=self.start_automation)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Automation", command=self.stop_automation, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=(10, 0))
        
        # Status and Stats
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(status_frame, text="Ready", font=("Arial", 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Session stats
        self.stats_label = ttk.Label(status_frame, text="Training: 0 | Races: 0 | Events: 0 | Errors: 0", 
                                    font=("Arial", 9))
        self.stats_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.log_text = tk.Text(log_frame, height=10, width=70)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def log_message(self, message: str):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
    
    def update_stats_display(self):
        """Update the session statistics display"""
        stats = self.automation.get_session_stats()
        stats_text = f"Training: {stats['training_sessions']} | Races: {stats['races_completed']} | Events: {stats['events_handled']} | Errors: {stats['errors_encountered']}"
        self.stats_label.config(text=stats_text)
    
    def start_automation(self):
        """Start the automation process"""
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Running...")
        self.log_message("Starting automation...")
        
        # Update config with current settings
        self.automation.config.set('Training', 'priority_stats', self.priority_stats.get())
        self.automation.config.set('Training', 'skip_races', str(self.skip_races.get()))
        self.automation.config.set('Training', 'farm_fans', str(self.farm_fans.get()))
        
        # Start automation in separate thread
        self.automation_thread = threading.Thread(target=self.automation.run_automation)
        self.automation_thread.daemon = True
        self.automation_thread.start()
        
        # Start stats update timer
        self.update_stats_timer()
    
    def stop_automation(self):
        """Stop the automation process"""
        self.automation.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped")
        self.log_message("Automation stopped")
        self.update_stats_display()  # Final stats update
    
    def update_stats_timer(self):
        """Update stats display periodically"""
        if self.automation.running:
            self.update_stats_display()
            self.root.after(1000, self.update_stats_timer)  # Update every second
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("Uma Musume PC Automation Tool")
    print("=" * 40)
    
    # Check if running in GUI mode or command line
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        # Command line mode
        automation = UmaMusumeAutomation()
        try:
            automation.run_automation()
        except KeyboardInterrupt:
            print("\nAutomation stopped by user")
    else:
        # GUI mode (default)
        app = AutomationGUI()
        app.run()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Window Detection Utility for Uma Musume PC Client
Detects the game window size and position for proper automation
"""

import cv2
import numpy as np
import pyautogui
import time
import logging
from typing import Tuple, Optional, List
import subprocess
import re
import platform

logger = logging.getLogger(__name__)

class WindowDetector:
    def __init__(self):
        self.system = platform.system()
        self.game_window = None
        self.window_rect = None
        
    def find_uma_musume_window(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Find Uma Musume game window and return its coordinates
        Returns: (x, y, width, height) or None if not found
        """
        if self.system == "Darwin":  # macOS
            return self._find_window_macos()
        elif self.system == "Windows":
            return self._find_window_windows()
        elif self.system == "Linux":
            return self._find_window_linux()
        else:
            logger.error(f"Unsupported operating system: {self.system}")
            return None
    
    def _find_window_macos(self) -> Optional[Tuple[int, int, int, int]]:
        """Find Uma Musume window on macOS"""
        try:
            # Use osascript to get window information
            cmd = [
                'osascript', '-e',
                'tell application "System Events" to get position and size of window 1 of process "Uma Musume"'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse the output: "x, y, width, height"
                coords = result.stdout.strip().split(', ')
                if len(coords) == 4:
                    x, y, width, height = map(int, coords)
                    return (x, y, width, height)
            
            # Alternative: try to find by window title
            cmd = [
                'osascript', '-e',
                'tell application "System Events" to get position and size of window 1 of process "Uma Musume Pretty Derby"'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                coords = result.stdout.strip().split(', ')
                if len(coords) == 4:
                    x, y, width, height = map(int, coords)
                    return (x, y, width, height)
                    
        except Exception as e:
            logger.error(f"Error finding window on macOS: {e}")
        
        return None
    
    def _find_window_windows(self) -> Optional[Tuple[int, int, int, int]]:
        """Find Uma Musume window on Windows"""
        try:
            import win32gui
            import win32con
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if "Uma Musume" in window_text or "Pretty Derby" in window_text:
                        rect = win32gui.GetWindowRect(hwnd)
                        x, y, w, h = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
                        windows.append((x, y, w, h))
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                return windows[0]  # Return first matching window
                
        except ImportError:
            logger.warning("win32gui not available, trying alternative method")
            # Fallback: try to find by process name
            try:
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq UmaMusume.exe'], 
                                      capture_output=True, text=True)
                if "UmaMusume.exe" in result.stdout:
                    # Window exists, use screen center as fallback
                    screen_width, screen_height = pyautogui.size()
                    return (0, 0, screen_width, screen_height)
            except Exception as e:
                logger.error(f"Error finding window on Windows: {e}")
        
        return None
    
    def _find_window_linux(self) -> Optional[Tuple[int, int, int, int]]:
        """Find Uma Musume window on Linux"""
        try:
            # Try using wmctrl
            result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Uma Musume' in line or 'Pretty Derby' in line:
                        # Parse window ID and get geometry
                        parts = line.split()
                        if len(parts) >= 2:
                            window_id = parts[0]
                            geom_result = subprocess.run(['wmctrl', '-G', '-r', window_id], 
                                                       capture_output=True, text=True)
                            if geom_result.returncode == 0:
                                geom_parts = geom_result.stdout.split()
                                if len(geom_parts) >= 6:
                                    x, y, w, h = map(int, geom_parts[2:6])
                                    return (x, y, w, h)
        except Exception as e:
            logger.error(f"Error finding window on Linux: {e}")
        
        return None
    
    def get_game_region(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the current game window region
        Returns: (left, top, right, bottom) for screenshot region
        """
        if self.window_rect is None:
            self.window_rect = self.find_uma_musume_window()
        
        if self.window_rect:
            x, y, width, height = self.window_rect
            return (x, y, x + width, y + height)
        
        return None
    
    def is_game_window_active(self) -> bool:
        """Check if the game window is currently active/focused"""
        if self.system == "Darwin":
            try:
                cmd = ['osascript', '-e', 'tell application "System Events" to get name of first process whose frontmost is true']
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    active_app = result.stdout.strip()
                    return "Uma Musume" in active_app
            except Exception as e:
                logger.error(f"Error checking active window: {e}")
        
        return True  # Assume active if we can't determine
    
    def focus_game_window(self) -> bool:
        """Bring the game window to front"""
        if self.system == "Darwin":
            try:
                cmd = ['osascript', '-e', 'tell application "Uma Musume" to activate']
                result = subprocess.run(cmd, capture_output=True)
                return result.returncode == 0
            except Exception as e:
                logger.error(f"Error focusing window: {e}")
        
        return False
    
    def get_relative_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """
        Convert screen coordinates to game window relative coordinates
        Useful for scaling templates to different window sizes
        """
        if self.window_rect:
            window_x, window_y, window_w, window_h = self.window_rect
            rel_x = (x - window_x) / window_w
            rel_y = (y - window_y) / window_h
            return (rel_x, rel_y)
        
        return (x / pyautogui.size()[0], y / pyautogui.size()[1])
    
    def get_absolute_coordinates(self, rel_x: float, rel_y: float) -> Tuple[int, int]:
        """
        Convert relative coordinates back to absolute screen coordinates
        """
        if self.window_rect:
            window_x, window_y, window_w, window_h = self.window_rect
            abs_x = int(window_x + (rel_x * window_w))
            abs_y = int(window_y + (rel_y * window_h))
            return (abs_x, abs_y)
        
        screen_w, screen_h = pyautogui.size()
        return (int(rel_x * screen_w), int(rel_y * screen_h))

def test_window_detection():
    """Test function to verify window detection works"""
    detector = WindowDetector()
    
    print("Testing window detection...")
    window_rect = detector.find_uma_musume_window()
    
    if window_rect:
        x, y, width, height = window_rect
        print(f"Found Uma Musume window at: ({x}, {y}) with size {width}x{height}")
        
        # Test region calculation
        region = detector.get_game_region()
        print(f"Game region: {region}")
        
        # Test coordinate conversion
        rel_coords = detector.get_relative_coordinates(100, 100)
        print(f"Relative coordinates for (100, 100): {rel_coords}")
        
        abs_coords = detector.get_absolute_coordinates(rel_coords[0], rel_coords[1])
        print(f"Absolute coordinates: {abs_coords}")
        
    else:
        print("Uma Musume window not found. Make sure the game is running.")
        print("You can still use the automation with full screen capture.")

if __name__ == "__main__":
    test_window_detection() 
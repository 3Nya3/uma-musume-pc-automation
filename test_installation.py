#!/usr/bin/env python3
"""
Installation Test Script for Uma Musume PC Automation
Tests all dependencies and basic functionality
"""

import sys
import importlib
import subprocess
import platform

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✓ {package_name or module_name} - OK")
        return True
    except ImportError as e:
        print(f"✗ {package_name or module_name} - FAILED: {e}")
        return False

def test_tesseract():
    """Test if Tesseract OCR is available"""
    try:
        import pytesseract
        # Try to get version
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract OCR - OK (version: {version})")
        return True
    except Exception as e:
        print(f"✗ Tesseract OCR - FAILED: {e}")
        return False

def test_screen_capture():
    """Test screen capture functionality"""
    try:
        from PIL import ImageGrab
        # Try to capture a small region
        screenshot = ImageGrab.grab(bbox=(0, 0, 100, 100))
        print("✓ Screen Capture - OK")
        return True
    except Exception as e:
        print(f"✗ Screen Capture - FAILED: {e}")
        return False

def test_window_detection():
    """Test window detection functionality"""
    try:
        from window_detector import WindowDetector
        detector = WindowDetector()
        print("✓ Window Detection - OK")
        return True
    except Exception as e:
        print(f"✗ Window Detection - FAILED: {e}")
        return False

def test_automation_class():
    """Test automation class initialization"""
    try:
        from uma_automation import UmaMusumeAutomation
        automation = UmaMusumeAutomation()
        print("✓ Automation Class - OK")
        return True
    except Exception as e:
        print(f"✗ Automation Class - FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("Uma Musume PC Automation - Installation Test")
    print("=" * 50)
    
    # System information
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print()
    
    # Test required modules
    print("Testing required modules:")
    print("-" * 30)
    
    modules = [
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("pyautogui", "PyAutoGUI"),
        ("pytesseract", "Pytesseract"),
        ("PIL", "Pillow"),
        ("tkinter", "Tkinter"),
        ("threading", "Threading"),
        ("configparser", "ConfigParser"),
    ]
    
    all_modules_ok = True
    for module_name, package_name in modules:
        if not test_import(module_name, package_name):
            all_modules_ok = False
    
    print()
    
    # Test Tesseract
    print("Testing Tesseract OCR:")
    print("-" * 30)
    tesseract_ok = test_tesseract()
    
    print()
    
    # Test functionality
    print("Testing functionality:")
    print("-" * 30)
    
    screen_capture_ok = test_screen_capture()
    window_detection_ok = test_window_detection()
    automation_class_ok = test_automation_class()
    
    print()
    
    # Summary
    print("Test Summary:")
    print("-" * 30)
    
    if all_modules_ok and tesseract_ok and screen_capture_ok and window_detection_ok and automation_class_ok:
        print("✓ All tests passed! Installation is complete.")
        print("\nNext steps:")
        print("1. Run 'python template_creator.py' to create UI templates")
        print("2. Run 'python uma_automation.py' to start the automation tool")
        return True
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        print("\nCommon solutions:")
        if not tesseract_ok:
            print("- Install Tesseract OCR:")
            if platform.system() == "Darwin":
                print("  brew install tesseract")
            elif platform.system() == "Windows":
                print("  Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            else:
                print("  sudo apt-get install tesseract-ocr")
        
        if not all_modules_ok:
            print("- Install missing Python packages:")
            print("  pip install -r requirements.txt")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
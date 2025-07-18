# Setup Guide - Uma Musume PC Automation

This guide will help you set up the Uma Musume PC automation tool on your system.

## Prerequisites

- Python 3.8 or higher
- Uma Musume Pretty Derby Global version (PC)
- Administrator/sudo access (for installing dependencies)

## Step-by-Step Setup

### 1. Install Python Dependencies

First, install all required Python packages:

```bash
# Install dependencies
pip3 install -r requirements.txt
```

If you encounter permission issues, you may need to use:
```bash
pip3 install --user -r requirements.txt
```

### 2. Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install and add to PATH
- Update `config.ini` with the full path to tesseract.exe

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

### 3. Test Installation

Run the installation test to verify everything is working:

```bash
python3 test_installation.py
```

You should see "✓ All tests passed!" if everything is installed correctly.

### 4. Create UI Templates

Before using the automation, you need to create template images for UI recognition:

```bash
python3 template_creator.py
```

**Required Templates:**
- `main_menu.png` - Main menu screen
- `training_screen.png` - Training selection screen
- `race_screen.png` - Race screen
- `event_screen.png` - Event/choice screen
- `training_button.png` - Training menu button
- `speed_train.png` - Speed training button
- `stamina_train.png` - Stamina training button
- `power_train.png` - Power training button
- `guts_train.png` - Guts training button
- `intelligence_train.png` - Intelligence training button
- `technique_train.png` - Technique training button
- `continue_button.png` - Continue/OK button
- `back_button.png` - Back button

### 5. Configure Settings

Edit `config.ini` to customize the automation:

```ini
[Training]
priority_stats = speed,stamina,power  # Training priority order
skip_races = false                   # Skip races during training
farm_fans = false                    # Focus on fan farming

[Automation]
click_delay = 0.5                    # Delay between clicks
screenshot_delay = 1.0               # Delay between screenshots
window_detection_enabled = true      # Auto-detect game window
```

### 6. Launch the Tool

**Option 1: Use the launcher (recommended)**
```bash
python3 launcher.py
```

**Option 2: Direct launch**
```bash
python3 uma_automation.py
```

**Option 3: Use shell scripts**
- Windows: Double-click `start.bat`
- macOS/Linux: Run `./start.sh`

## Troubleshooting

### Common Issues

**1. "No module named 'cv2'"**
```bash
pip3 install opencv-python
```

**2. "Tesseract not found"**
- Ensure Tesseract is installed and in PATH
- Update `tesseract_path` in `config.ini`

**3. "Permission denied" on macOS**
```bash
# Grant accessibility permissions to Terminal/your IDE
# System Preferences > Security & Privacy > Privacy > Accessibility
```

**4. Window detection fails**
- Ensure Uma Musume is running and visible
- Try running the game in windowed mode
- Check window title matches expected names

**5. Templates not recognized**
- Ensure template images are clear and match game UI
- Verify game resolution matches template resolution
- Recreate templates if game UI changes

### Getting Help

1. Run `python3 test_installation.py` to diagnose issues
2. Check the log output in the GUI for error messages
3. Ensure all templates are created and named correctly
4. Verify game is running in the expected language (English)

## Safety Notes

- Always test the automation in a safe environment first
- Keep the game window visible and don't minimize it
- Use the emergency stop button (Ctrl+C) if needed
- Monitor the automation to ensure it's working correctly
- The tool is for educational use only

## Next Steps

After setup is complete:

1. Launch Uma Musume Pretty Derby
2. Start the automation tool
3. Configure your preferred settings
4. Create necessary UI templates
5. Start automation and monitor performance

For detailed usage instructions, see the main README.md file. 
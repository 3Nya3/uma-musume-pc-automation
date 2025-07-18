# Uma Musume PC Automation Tool

A Python-based automation tool for Uma Musume Pretty Derby Global version on PC. This tool automates various aspects of the game including training, racing, and event management.

## Features

- **Automated Training**: Automatically selects and performs training sessions based on priority stats
- **Race Automation**: Handles race participation and result processing
- **Event Management**: Automatically responds to events and choices
- **Multi-platform Support**: Works on Windows, macOS, and Linux
- **GUI Interface**: User-friendly graphical interface for easy control
- **Window Detection**: Automatically detects and focuses the game window
- **OCR Text Recognition**: Reads in-game text for decision making
- **Configurable Settings**: Customizable automation parameters

## Requirements

- Python 3.8 or higher
- Uma Musume Pretty Derby Global version (PC)
- Tesseract OCR engine
- Required Python packages (see requirements.txt)

## Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd uma-musume-pc-automation
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR**
   
   **Windows:**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Add to PATH or update config.ini with full path
   
   **macOS:**
   ```bash
   brew install tesseract
   ```
   
   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt-get install tesseract-ocr
   ```

4. **Configure the tool**
   - Edit `config.ini` to match your preferences
   - Add UI templates to the `templates/` folder (see Templates section)

## Usage

1. **Start the automation tool**
   ```bash
   python uma_automation.py
   ```

2. **Launch Uma Musume Pretty Derby**

3. **Configure automation settings in the GUI**
   - Set priority stats for training
   - Choose automation features to enable
   - Adjust timing parameters

4. **Start automation**
   - Click "Start Automation" in the GUI
   - The tool will automatically detect the game window and begin

## Templates

The tool uses image templates to recognize UI elements. Create the following template images in the `templates/` folder:

### Required Templates
- `main_menu.png` - Main menu screen
- `training_screen.png` - Training selection screen
- `race_screen.png` - Race screen
- `event_screen.png` - Event/choice screen

### Training Templates
- `speed_train.png` - Speed training button
- `stamina_train.png` - Stamina training button
- `power_train.png` - Power training button
- `guts_train.png` - Guts training button
- `intelligence_train.png` - Intelligence training button
- `technique_train.png` - Technique training button

### Navigation Templates
- `training_button.png` - Training menu button
- `race_button.png` - Race menu button
- `continue_button.png` - Continue/OK button
- `back_button.png` - Back button

## Configuration

Edit `config.ini` to customize the automation:

```ini
[Training]
priority_stats = speed,stamina,power  # Training priority order
skip_races = false                   # Skip races during training
farm_fans = false                    # Focus on fan farming
max_training_sessions = 50           # Maximum training sessions

[Automation]
click_delay = 0.5                    # Delay between clicks
screenshot_delay = 1.0               # Delay between screenshots
max_retries = 3                      # Maximum retry attempts
```

## Safety Features

- **Emergency Stop**: Press Ctrl+C in terminal or use GUI stop button
- **Window Detection**: Automatically detects game window position
- **Error Recovery**: Handles common errors and retries operations
- **Logging**: Detailed logs for troubleshooting

## Troubleshooting

### Common Issues

1. **Tesseract not found**
   - Install Tesseract OCR
   - Update `tesseract_path` in config.ini

2. **Templates not recognized**
   - Ensure template images are clear and match game UI
   - Check template file names match expected names
   - Verify game resolution matches template resolution

3. **Window detection fails**
   - Ensure game is running and visible
   - Check window title matches expected names
   - Try manual window positioning

4. **OCR accuracy issues**
   - Adjust `confidence_threshold` in config.ini
   - Ensure game text is clear and readable
   - Check game language settings

### Debug Mode

Enable debug logging by setting `log_level = DEBUG` in config.ini.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Disclaimer

This tool is for educational and personal use only. Use at your own risk and in accordance with the game's terms of service. The developers are not responsible for any consequences of using this automation tool.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the original Android automation tool by steve1316
- Adapted for PC version with English language support
- Uses OpenCV for image processing and template matching
- Uses Tesseract OCR for text recognition 
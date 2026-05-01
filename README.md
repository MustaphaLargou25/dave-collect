# Data Collection System

A modular Python application for collecting synchronized data from cameras and Arduino sensors, with a real-time Pygame interface. Perfect for building datasets, prototyping IoT projects, and running live sensor monitoring systems.

[![Python 3.7+](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Modules](#-modules)
- [Configuration](#-configuration)
- [Data Structure](#-data-structure)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [FAQ](#-faq)

---

## ✨ Features

🎥 **Camera Integration**
- Multi-camera support with device auto-detection
- Configurable resolution and frame rates
- Frame capture with timestamp synchronization
- Automatic resource cleanup

📊 **Arduino Sensor Support**
- Auto-detection of Arduino ports
- Real-time sensor data streaming
- Support for multiple sensor types (temperature, humidity, distance, etc.)
- Robust error handling and reconnection logic
- Customizable baud rates and data formats

🎮 **Real-Time UI**
- Live camera feed visualization
- Sensor data dashboard with graphs
- Session management interface
- Keyboard shortcuts for quick actions
- Customizable color schemes

💾 **Data Persistence**
- Organized, structured file system
- Synchronized image + metadata + labels
- JSON-based metadata storage
- Session summaries and statistics
- Timestamp-based file naming

🔧 **Modular Architecture**
- Clean separation of concerns
- Easy to extend and customize
- Reusable components
- Unit test ready

---

## 🏗️ Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                        main.py                          │
│              (Application Orchestrator)                 │
└────────────┬──────────┬──────────┬──────────┬──────────┘
             │          │          │          │
    ┌────────▼──┐  ┌────▼────┐  ┌─▼─────┐  ┌▼──────────┐
    │ camera_   │  │arduino_ │  │ui_    │  │data_      │
    │ manager   │  │serial   │  │pygame │  │logger     │
    └───────────┘  └─────────┘  └───────┘  └───────────┘
         │              │           │            │
    ┌────▼────┐    ┌────▼────┐ ┌───▼────┐  ┌────▼────┐
    │ Camera  │    │ Arduino │ │Pygame  │  │datasets/│
    │ Device  │    │ Sensors │ │Display │  │         │
    └─────────┘    └─────────┘ └────────┘  └─────────┘
```

### Data Flow

```
User Input (Space/S/ESC)
         │
         ▼
┌─────────────────────────┐
│   UI Event Handler      │
└────────────┬────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
Capture Frame    Save Summary
    │                 │
    ▼                 ▼
Read Sensors      Generate Report
    │                 │
    ▼                 ▼
Sync Data         Output JSON
    │                 │
    ▼                 ▼
Save Files        Update UI
```

---

## 🚀 Quick Start

### 1-Minute Setup

```bash
# Clone and navigate
git clone https://github.com/yourusername/data-collection-system.git
cd data-collection-system

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

**That's it!** The application will:
- ✅ Detect and initialize your camera
- ✅ Auto-connect to Arduino (if available)
- ✅ Open the Pygame interface
- ✅ Start collecting data

---

## 📦 Installation

### Prerequisites

- **Python 3.7+**
- **USB Camera** (built-in or external)
- **Arduino** (optional, for sensor data)
- **Pygame** and **OpenCV** (installed via pip)

### Step-by-Step Setup

#### 1. Clone Repository
```bash
git clone https://github.com/yourusername/data-collection-system.git
cd data-collection-system
```

#### 2. Create Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. (Optional) Arduino Setup

If using Arduino sensors:

1. **Install Arduino IDE** from [arduino.cc](https://www.arduino.cc/)
2. **Upload sketch** to your Arduino board
3. **Note the COM port** (Windows) or device (macOS/Linux)
4. **Update** `main.py` with correct port if needed:
   ```python
   self.arduino = ArduinoSerial(port="COM3", baudrate=9600)  # Windows
   # or
   self.arduino = ArduinoSerial(port="/dev/ttyUSB0", baudrate=9600)  # Linux
   ```

#### 5. Run Application
```bash
python main.py
```

---

## 🎮 Usage

### Basic Operation

1. **Start Application**
   ```bash
   python main.py
   ```

2. **View Live Feed**
   - Camera stream displays in Pygame window
   - Sensor data shown in real-time

3. **Capture Data**
   - Press `SPACE` to capture frame + sensors
   - Data auto-saves to `datasets/` folder

4. **Save Session**
   - Press `S` to manually save summary
   - Or press `ESC` to quit (auto-saves)

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `SPACE` | Capture frame + sensor data |
| `S` | Save session summary |
| `R` | Reset session counter |
| `D` | Toggle debug mode |
| `ESC` | Quit application |

### Example Workflow

```bash
# Start application
$ python main.py

# Console output:
# [INFO] Initializing camera...
# [INFO] Camera initialized at 640x480
# [INFO] Attempting Arduino connection...
# [INFO] Arduino connected on COM3
# [INFO] Pygame UI initialized
# [INFO] Ready to capture! Press SPACE to start.

# (Application running with live feed)

# Press SPACE to capture
# [INFO] Captured frame 1 (temperature: 23.5°C, humidity: 45%)
# [INFO] Saved to datasets/images/20240115_143022_0001_20240115_143025_123.jpg

# ... (repeat captures) ...

# Press S to save summary
# [INFO] Session summary saved
# [INFO] Total captures: 42
# [INFO] Session duration: 15 minutes

# Press ESC to quit
# [INFO] Shutting down...
# [INFO] Camera released
# [INFO] Arduino disconnected
# [INFO] Goodbye!
```

---

## 🔧 Modules

### 1. `camera_manager.py`

Manages all camera operations.

**Main Class**: `CameraManager`

**Initialization**:
```python
from camera_manager import CameraManager

camera = CameraManager(
    camera_index=0,      # Camera device ID
    width=640,           # Frame width
    height=480           # Frame height
)
camera.initialize()
```

**Key Methods**:

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `initialize()` | - | `bool` | Set up camera connection |
| `capture_frame()` | - | `np.ndarray` | Capture single frame |
| `set_resolution(w, h)` | `width, height` | `bool` | Change resolution |
| `get_resolution()` | - | `tuple` | Get current resolution |
| `is_initialized()` | - | `bool` | Check initialization status |
| `release()` | - | `None` | Release camera resources |

**Example**:
```python
camera = CameraManager(width=1280, height=720)
if camera.initialize():
    frame = camera.capture_frame()
    print(f"Frame shape: {frame.shape}")
    camera.release()
```

---

### 2. `arduino_serial.py`

Handles serial communication with Arduino.

**Main Class**: `ArduinoSerial`

**Initialization**:
```python
from arduino_serial import ArduinoSerial

arduino = ArduinoSerial(
    port="COM3",         # Serial port (auto-detect if None)
    baudrate=9600        # Baud rate
)
arduino.connect()
```

**Key Methods**:

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `connect()` | - | `bool` | Establish connection |
| `is_connected()` | - | `bool` | Check connection status |
| `read_sensor_data()` | - | `dict` | Read parsed sensor data |
| `send_command(cmd)` | `command_str` | `bool` | Send command to Arduino |
| `disconnect()` | - | `None` | Close connection |
| `list_ports()` | - | `list` | List available COM ports |

**Data Format**:
```
Arduino sends: "sensor1:value1,sensor2:value2,sensor3:value3"
Parsed to: {"sensor1": value1, "sensor2": value2, "sensor3": value3}
```

**Example**:
```python
arduino = ArduinoSerial(port="COM3")
if arduino.connect():
    data = arduino.read_sensor_data()
    print(f"Temperature: {data.get('temp')}°C")
    print(f"Humidity: {data.get('humidity')}%")
```

---

### 3. `ui_pygame.py`

Provides graphical user interface using Pygame.

**Main Class**: `PygameUI`

**Initialization**:
```python
from ui_pygame import PygameUI

ui = PygameUI(
    width=1024,
    height=768,
    title="Data Collection System",
    fps=30
)
ui.initialize()
```

**Key Methods**:

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `initialize()` | - | `bool` | Set up Pygame window |
| `process_events()` | - | `dict` | Handle input; returns event data |
| `draw_frame(frame)` | `np.ndarray` | `None` | Display camera feed |
| `draw_sensor_data(data)` | `dict` | `None` | Visualize sensor readings |
| `draw_status(message)` | `message_str` | `None` | Show status message |
| `update()` | - | `None` | Refresh display |
| `quit()` | - | `None` | Close window gracefully |

**Example**:
```python
ui = PygameUI(width=1024, height=768)
ui.initialize()

while True:
    events = ui.process_events()
    if events.get("quit"):
        break
    
    ui.draw_frame(frame)
    ui.draw_sensor_data({"temp": 23.5, "humidity": 45})
    ui.update()
```

---

### 4. `data_logger.py`

Manages data persistence and organization.

**Main Class**: `DataLogger`

**Initialization**:
```python
from data_logger import DataLogger

logger = DataLogger(base_path="datasets")
logger.start_session()
```

**Key Methods**:

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `start_session()` | - | `str` | Begin new session; returns session_id |
| `save_capture(frame, label, sensors)` | `np.ndarray, str, dict` | `bool` | Save complete capture |
| `save_session_summary()` | - | `bool` | Generate session summary JSON |
| `get_capture_count()` | - | `int` | Get total captures in session |
| `get_session_id()` | - | `str` | Get current session ID |
| `get_dataset_path()` | - | `str` | Get datasets folder path |

**Example**:
```python
logger = DataLogger(base_path="datasets")
logger.start_session()

# Later, save a capture
logger.save_capture(
    frame=frame_data,
    label="sample_001",
    sensors={"temp": 23.5, "humidity": 45}
)

# Save session summary
logger.save_session_summary()
```

---

### 5. `main.py`

Application entry point and orchestrator.

**Main Class**: `DataCollectionApp`

**Initialization**:
```python
from main import DataCollectionApp

app = DataCollectionApp()
app.run()
```

**Key Methods**:

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `initialize_modules()` | - | `bool` | Set up all components |
| `run()` | - | `None` | Main application loop |
| `shutdown()` | - | `None` | Clean resource cleanup |

---

## 📁 Data Structure

### Folder Organization

```
datasets/
├── images/              # Captured images
│   ├── session1_0001_timestamp.jpg
│   ├── session1_0002_timestamp.jpg
│   └── ...
│
├── labels/              # Annotation/label data
│   ├── session1_0001_timestamp.json
│   ├── session1_0002_timestamp.json
│   └── ...
│
└── metadata/            # Sensor data and session info
    ├── session1_0001_timestamp.json
    ├── session1_0002_timestamp.json
    ├── session_session1_summary.json
    └── ...
```

### File Naming Convention

Format: `{session_id}_{capture_number:04d}_{timestamp}.{ext}`

Example: `20240115_143022_0001_20240115_143025_123.jpg`

- **session_id**: Date+time of session start (YYYYMMDD_HHMMSS)
- **capture_number**: 4-digit index (0001, 0002, etc.)
- **timestamp**: Capture timestamp with milliseconds

### Metadata Structures

**Capture Metadata** (`metadata/{filename}.json`):
```json
{
  "timestamp": "20240115_143025_123",
  "session_id": "20240115_143022",
  "capture_number": 1,
  "image_path": "images/20240115_143022_0001_20240115_143025_123.jpg",
  "label": "sample_001",
  "sensor_data": {
    "temperature": 23.5,
    "humidity": 45.2,
    "distance": 150.3,
    "pressure": 1013.25
  },
  "notes": "Optional notes about this capture"
}
```

**Session Summary** (`metadata/session_{session_id}_summary.json`):
```json
{
  "session_id": "20240115_143022",
  "start_time": "20240115_143022",
  "end_time": "20240115_144530_456",
  "duration_minutes": 15,
  "total_captures": 42,
  "sensor_stats": {
    "temperature": {
      "min": 22.1,
      "max": 24.8,
      "avg": 23.5
    },
    "humidity": {
      "min": 40.2,
      "max": 50.5,
      "avg": 45.2
    }
  },
  "image_count": 42,
  "images_path": "images",
  "labels_path": "labels",
  "metadata_path": "metadata",
  "notes": "Optional session notes"
}
```

---

## ⚙️ Configuration

### Basic Configuration

Edit `main.py` to customize settings:

```python
# Camera settings
CAMERA_INDEX = 0           # Device ID (0 = default)
CAMERA_WIDTH = 640         # Frame width in pixels
CAMERA_HEIGHT = 480        # Frame height in pixels
CAMERA_FPS = 30            # Frames per second

# Arduino settings
ARDUINO_PORT = None        # None = auto-detect
ARDUINO_BAUDRATE = 9600    # Serial baud rate
ARDUINO_TIMEOUT = 1        # Read timeout in seconds

# UI settings
UI_WIDTH = 1024            # Window width
UI_HEIGHT = 768            # Window height
UI_FPS = 30                # Display refresh rate

# Data settings
DATASET_PATH = "datasets"  # Base folder for data storage
AUTO_SAVE_INTERVAL = 60    # Auto-save summary every N seconds
```

### Advanced Configuration

Create `config.json` for persistent settings:

```json
{
  "camera": {
    "index": 0,
    "width": 1280,
    "height": 720,
    "fps": 30
  },
  "arduino": {
    "port": "COM3",
    "baudrate": 115200,
    "timeout": 2
  },
  "ui": {
    "width": 1280,
    "height": 960,
    "theme": "dark"
  },
  "data": {
    "path": "datasets",
    "auto_save": true,
    "auto_save_interval": 60
  }
}
```

Load in `main.py`:
```python
import json

with open("config.json", "r") as f:
    config = json.load(f)
```

---

## 🐛 Troubleshooting

### Camera Issues

**Problem**: "Camera not found" error

**Solution**:
```python
# Test camera detection
import cv2

# List available cameras
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera {i} available")
        cap.release()
```

**Problem**: "Cannot grab frame" error

**Solution**:
```bash
# Restart camera driver
# Windows: Restart camera service
# Linux: Try different camera index (start from 1)
# macOS: Restart application or restart Mac
```

---

### Arduino Issues

**Problem**: "Arduino port not found"

**Solution**:
```python
from arduino_serial import ArduinoSerial

# List available ports
ports = ArduinoSerial.list_ports()
print("Available ports:", ports)

# Connect with specific port
arduino = ArduinoSerial(port=ports[0])
```

**Problem**: "Data parsing error" 

**Solution**:
Check Arduino sends correct format:
```
Expected: "sensor1:23.5,sensor2:45.2"
NOT: "23.5,45.2" or "sensor1=23.5"
```

---

### UI Issues

**Problem**: Pygame window not opening

**Solution**:
```bash
# Reinstall Pygame
pip uninstall pygame
pip install pygame --upgrade

# On Windows, may need: pip install pygame-ce
```

**Problem**: Display freezes during capture

**Solution**:
- Run in separate thread (example in `main.py`)
- Reduce image resolution
- Lower camera FPS

---

### Data Issues

**Problem**: Files not saving to `datasets/`

**Solution**:
```python
# Check permissions
import os
os.makedirs("datasets/images", exist_ok=True)
os.makedirs("datasets/labels", exist_ok=True)
os.makedirs("datasets/metadata", exist_ok=True)

# Verify write access
with open("datasets/test.txt", "w") as f:
    f.write("test")
```

---

## 🤝 Contributing

We welcome contributions! Here's how to help:

### 1. Fork the Repository
```bash
git clone https://github.com/yourusername/data-collection-system.git
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes & Test
```bash
python -m pytest tests/
```

### 4. Commit & Push
```bash
git commit -m "Add: description of changes"
git push origin feature/your-feature-name
```

### 5. Open Pull Request

---

## ❓ FAQ

**Q: Can I use multiple cameras?**
A: Yes! Modify `camera_manager.py` to support array of cameras.

**Q: How do I add more sensor types?**
A: Edit `arduino_serial.py` `read_sensor_data()` method to parse new formats.

**Q: Can I export data in different formats?**
A: Yes! Extend `data_logger.py` with methods for CSV, XML, etc.

**Q: What's the maximum capture rate?**
A: Depends on camera and system; typically 30-120 fps.

**Q: Can I use this on Raspberry Pi?**
A: Yes! Requires: `pip install opencv-python-headless pygame pyserial`

**Q: Is data automatically backed up?**
A: No, but you can add cloud sync to `data_logger.py`.

---

## 📄 License

MIT License - Feel free to use, modify, and distribute.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/data-collection-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/data-collection-system/discussions)

---

**Made with ❤️ for data collectors and IoT enthusiasts**

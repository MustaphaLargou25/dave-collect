# Data Collection System

A modular Python application for collecting synchronized data from cameras and Arduino sensors, with a real-time Pygame interface.

## Architecture Overview

The application is built with a modular architecture, with each component having a specific responsibility:

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

## Modules

### 1. `camera_manager.py`
**Purpose**: Manages camera operations

**Key Features**:
- Camera initialization and configuration
- Frame capture with error handling
- Resolution adjustment
- Automatic resource cleanup

**Main Class**: `CameraManager`

**Key Methods**:
- `initialize()` - Set up camera connection
- `capture_frame()` - Capture a single frame
- `set_resolution(width, height)` - Change camera resolution
- `release()` - Release camera resources

---

### 2. `arduino_serial.py`
**Purpose**: Handles serial communication with Arduino

**Key Features**:
- Auto-detection of Arduino ports
- Robust serial communication
- Sensor data parsing
- Command sending/receiving

**Main Class**: `ArduinoSerial`

**Key Methods**:
- `connect()` - Establish serial connection
- `read_sensor_data()` - Read and parse sensor data
- `send_command(command)` - Send command to Arduino
- `disconnect()` - Close connection

**Data Format**: Expects sensor data in format: `sensor1:value1,sensor2:value2,...`

---

### 3. `ui_pygame.py`
**Purpose**: Provides graphical user interface

**Key Features**:
- Real-time camera feed display
- Sensor data visualization
- Status indicators
- User input handling
- Customizable color scheme

**Main Class**: `PygameUI`

**Key Methods**:
- `initialize()` - Set up Pygame window
- `process_events()` - Handle keyboard/mouse input
- `draw_frame(frame)` - Display camera feed
- `draw_sensor_data(data)` - Visualize sensor readings
- `update()` - Refresh display

**Controls**:
- `SPACE` - Capture and save frame
- `S` - Save session summary
- `ESC` - Quit application

---

### 4. `data_logger.py`
**Purpose**: Manages data persistence

**Key Features**:
- Organized file storage
- Session management
- Synchronized saving (image + metadata + labels)
- JSON metadata format
- Session summaries

**Main Class**: `DataLogger`

**Key Methods**:
- `start_session()` - Begin new logging session
- `save_capture(frame, label_data, sensor_data)` - Save complete capture
- `save_session_summary()` - Create session summary
- `get_capture_count()` - Get number of captures

---

### 5. `main.py`
**Purpose**: Application entry point and orchestrator

**Key Features**:
- Module initialization and coordination
- Main application loop
- Event handling and routing
- Graceful shutdown

**Main Class**: `DataCollectionApp`

**Key Methods**:
- `initialize_modules()` - Set up all components
- `run()` - Main application loop
- `shutdown()` - Clean resource cleanup

---

## Dataset Folder Structure

```
datasets/
├── images/          # Captured images
│   ├── {session}_{index}_{timestamp}.jpg
│   └── ...
├── labels/          # Label/annotation data (JSON)
│   ├── {session}_{index}_{timestamp}.json
│   └── ...
└── metadata/        # Sensor data and session info (JSON)
    ├── {session}_{index}_{timestamp}.json
    ├── session_{session}_summary.json
    └── ...
```

### File Naming Convention

Images and associated data files use synchronized naming:
- Format: `{session_id}_{capture_number:04d}_{timestamp}.{ext}`
- Example: `20240115_143022_0001_20240115_143025_123.jpg`

### Metadata Structure

**Capture Metadata** (`metadata/{filename}.json`):
```json
{
  "timestamp": "20240115_143025_123",
  "session_id": "20240115_143022",
  "capture_number": 1,
  "sensor_data": {
    "temperature": 23.5,
    "humidity": 45.2,
    "distance": 150.3
  }
}
```

**Session Summary** (`metadata/session_{session_id}_summary.json`):
```json
{
  "session_id": "20240115_143022",
  "total_captures": 42,
  "start_time": "20240115_143022",
  "end_time": "20240115_144530_456",
  "images_path": "datasets/images",
  "labels_path": "datasets/labels",
  "metadata_path": "datasets/metadata"
}
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure camera is connected (USB or built-in)

3. (Optional) Connect Arduino via USB for sensor data

## Usage

Run the application:
```bash
python main.py
```

The application will:
1. Initialize camera and attempt to connect to Arduino
2. Open a Pygame window showing the camera feed
3. Display sensor data (if Arduino connected)
4. Wait for user input to capture frames

### Capturing Data

1. Press `SPACE` to capture the current frame along with sensor data
2. Data is automatically saved to the `datasets/` folder
3. Press `S` to manually save a session summary
4. Press `ESC` to quit (automatically saves summary)

## Configuration

To customize settings, modify the initialization parameters in `main.py`:

```python
# Camera settings
self.camera = CameraManager(camera_index=0, width=640, height=480)

# Arduino settings
self.arduino = ArduinoSerial(baudrate=9600)

# UI settings
self.ui = PygameUI(width=1024, height=768, title="Data Collection System")

# Data logger settings
self.logger = DataLogger(base_path="datasets")
```

## Extending the System

### Adding New Sensor Types

Edit `arduino_serial.py` to handle new data formats in the `read_sensor_data()` method.

### Custom UI Elements

Modify `ui_pygame.py` to add new visualization components using the provided drawing methods.

### Additional Data Processing

Extend `data_logger.py` to add preprocessing, validation, or additional export formats.

## Requirements

- Python 3.7+
- OpenCV (cv2)
- Pygame
- PySerial
- NumPy

## License

This project is open source and available for modification and distribution.

# Application Architecture

## Project Structure

```
data-collection-system/
├── main.py                    # Application entry point and orchestrator
├── camera_manager.py          # Camera operations module
├── arduino_serial.py          # Arduino serial communication module
├── ui_pygame.py               # Pygame UI module
├── data_logger.py             # Data persistence module
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── ARCHITECTURE.md           # This file
├── .gitignore                # Git ignore rules
└── datasets/                  # Dataset storage
    ├── images/                # Captured image files
    │   └── .gitkeep
    ├── labels/                # Label/annotation files (JSON)
    │   └── .gitkeep
    └── metadata/              # Metadata files (JSON)
        └── .gitkeep
```

## Module Architecture

### Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                   DataCollectionApp                          │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ initialize_ │  │     run()    │  │   shutdown()     │   │
│  │  modules()  │─▶│  (main loop) │─▶│ (cleanup)        │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└─────┬────────┬────────┬────────┬──────────────────────────┘
      │        │        │        │
      ▼        ▼        ▼        ▼
┌──────────┐ ┌────────┐ ┌──────┐ ┌─────────┐
│ Camera   │ │Arduino │ │  UI  │ │  Data   │
│ Manager  │ │ Serial │ │Pygame│ │ Logger  │
└──────────┘ └────────┘ └──────┘ └─────────┘
```

### Module Responsibilities

| Module | Responsibility | Key Operations |
|--------|---------------|----------------|
| **main.py** | Application orchestration | Initialize modules, event loop, coordinate components |
| **camera_manager.py** | Camera I/O | Capture frames, configure resolution, manage camera lifecycle |
| **arduino_serial.py** | Serial communication | Connect to Arduino, read sensor data, send commands |
| **ui_pygame.py** | User interface | Display video feed, render UI, handle input events |
| **data_logger.py** | Data persistence | Save images/metadata, organize files, session management |
| **config.py** | Configuration | Centralized settings for all modules |

## Data Flow

### Capture Workflow

```
┌──────────┐
│  User    │
│ (SPACE)  │
└────┬─────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│           main.py: handle_capture()         │
└───┬───────────────────────────────────┬─────┘
    │                                   │
    ▼                                   ▼
┌─────────────┐                  ┌──────────────┐
│ Camera      │                  │  Arduino     │
│ Manager     │                  │  Serial      │
│             │                  │              │
│ Get current │                  │ Get sensor   │
│ frame       │                  │ data         │
└──────┬──────┘                  └──────┬───────┘
       │                                │
       └───────────┬────────────────────┘
                   ▼
           ┌───────────────┐
           │ Data Logger   │
           │               │
           │ save_capture()│
           └───────┬───────┘
                   │
                   ▼
           ┌─────────────────┐
           │   datasets/     │
           │  ├─ images/     │
           │  ├─ labels/     │
           │  └─ metadata/   │
           └─────────────────┘
```

### Real-time Update Loop

```
┌───────────────────────────────────┐
│       main.py: run()              │
│                                   │
│  while running:                   │
│    1. Process UI events           │◄─┐
│    2. Update camera               │  │
│    3. Update sensors              │  │
│    4. Render UI                   │  │
│    5. Handle user input           │  │
└───────────────────────────────────┘  │
                                       │
                └────────────────────┘
                    (30 FPS loop)
```

## Class Diagrams

### CameraManager

```python
class CameraManager:
    # Attributes
    - camera_index: int
    - width: int
    - height: int
    - camera: VideoCapture
    - is_initialized: bool
    
    # Methods
    + __init__(camera_index, width, height)
    + initialize() -> bool
    + capture_frame() -> (bool, ndarray)
    + get_frame_dimensions() -> (int, int)
    + set_resolution(width, height) -> bool
    + release()
```

### ArduinoSerial

```python
class ArduinoSerial:
    # Attributes
    - port: str
    - baudrate: int
    - timeout: float
    - serial_connection: Serial
    - is_connected: bool
    
    # Methods
    + __init__(port, baudrate, timeout)
    + list_available_ports() -> List[str]
    + auto_detect_arduino() -> str
    + connect() -> bool
    + disconnect()
    + send_command(command: str) -> bool
    + read_line() -> str
    + read_sensor_data() -> Dict[str, Any]
    + flush()
```

### PygameUI

```python
class PygameUI:
    # Attributes
    - width: int
    - height: int
    - screen: Surface
    - clock: Clock
    - is_initialized: bool
    - colors: Dict[str, tuple]
    
    # Methods
    + __init__(width, height, title)
    + initialize() -> bool
    + process_events() -> Dict[str, Any]
    + draw_frame(frame, position)
    + draw_text(text, position, color, large)
    + draw_panel(rect, title)
    + draw_sensor_data(data, position)
    + clear()
    + update(fps)
    + quit()
```

### DataLogger

```python
class DataLogger:
    # Attributes
    - base_path: str
    - images_path: str
    - labels_path: str
    - metadata_path: str
    - session_id: str
    - capture_count: int
    
    # Methods
    + __init__(base_path)
    + start_session(session_name)
    + save_image(frame, label) -> str
    + save_label(filename, label_data) -> bool
    + save_metadata(filename, metadata) -> bool
    + save_capture(frame, label_data, sensor_data) -> bool
    + save_session_summary() -> bool
    + get_capture_count() -> int
```

### DataCollectionApp

```python
class DataCollectionApp:
    # Attributes
    - camera: CameraManager
    - arduino: ArduinoSerial
    - ui: PygameUI
    - logger: DataLogger
    - running: bool
    - current_frame: ndarray
    - sensor_data: Dict
    
    # Methods
    + __init__()
    + initialize_modules() -> bool
    + update_camera()
    + update_sensors()
    + handle_capture()
    + handle_save_summary()
    + render_ui()
    + run()
    + shutdown()
```

## Design Patterns Used

### 1. **Module Pattern**
Each component is encapsulated in its own module with a clear interface.

### 2. **Manager Pattern**
Classes like `CameraManager` and `DataLogger` manage their respective resources.

### 3. **Orchestrator Pattern**
`DataCollectionApp` in `main.py` orchestrates all components without tight coupling.

### 4. **Separation of Concerns**
- Hardware I/O: `camera_manager.py`, `arduino_serial.py`
- User Interface: `ui_pygame.py`
- Data Persistence: `data_logger.py`
- Business Logic: `main.py`

### 5. **Resource Management**
All classes implement proper cleanup in `__del__` methods and explicit cleanup methods.

## Configuration Management

Centralized configuration in `config.py`:
- Easy to modify settings without changing code
- Grouped by module
- Type-safe access through classes

## Error Handling Strategy

1. **Graceful Degradation**: System continues if non-critical components fail (e.g., Arduino)
2. **User Feedback**: Status indicators in UI show connection states
3. **Logging**: Console output for debugging and monitoring
4. **Safe Shutdown**: Ensures all resources are properly released

## Extension Points

### Adding New Features

1. **New Sensor Types**: Extend `ArduinoSerial.read_sensor_data()`
2. **Data Processing**: Add preprocessing in `DataLogger.save_capture()`
3. **UI Elements**: Add new draw methods in `PygameUI`
4. **Camera Effects**: Extend `CameraManager` with filters
5. **Export Formats**: Add new save methods in `DataLogger`

### Example: Adding a New Sensor

```python
# In arduino_serial.py
def read_temperature(self) -> float:
    """Read temperature sensor."""
    data = self.read_sensor_data()
    return data.get('temperature', 0.0)

# In main.py
def update_sensors(self):
    if self.arduino and self.arduino.is_connected:
        temp = self.arduino.read_temperature()
        self.sensor_data['temperature'] = temp
```

## Performance Considerations

- **Frame Rate**: UI runs at 30 FPS for smooth rendering
- **Non-blocking I/O**: Serial reads have timeout to prevent freezing
- **Efficient Rendering**: Only updates changed UI elements
- **Memory Management**: Proper cleanup prevents memory leaks

## Dependencies

| Package | Purpose | Module |
|---------|---------|--------|
| opencv-python | Camera capture and image processing | camera_manager.py |
| pygame | GUI rendering and input handling | ui_pygame.py |
| pyserial | Serial communication with Arduino | arduino_serial.py |
| numpy | Array operations for images | All modules |

## Testing Strategy

Recommended test structure:

```
tests/
├── test_camera_manager.py
├── test_arduino_serial.py
├── test_ui_pygame.py
├── test_data_logger.py
└── test_integration.py
```

Each module can be tested independently due to loose coupling.

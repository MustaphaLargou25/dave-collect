"""
Configuration Module

Centralized configuration settings for the data collection system.
"""


class CameraConfig:
    """Camera-related configuration."""
    INDEX = 0
    WIDTH = 640
    HEIGHT = 480


class ArduinoConfig:
    """Arduino serial communication configuration."""
    PORT = None
    BAUDRATE = 9600
    TIMEOUT = 1.0


class UIConfig:
    """User interface configuration."""
    WINDOW_WIDTH = 1024
    WINDOW_HEIGHT = 768
    WINDOW_TITLE = "Data Collection System"
    TARGET_FPS = 30
    
    COLORS = {
        'background': (30, 30, 30),
        'text': (255, 255, 255),
        'text_secondary': (180, 180, 180),
        'success': (0, 255, 0),
        'error': (255, 0, 0),
        'warning': (255, 165, 0),
        'panel': (50, 50, 50)
    }


class DataLoggerConfig:
    """Data logger configuration."""
    BASE_PATH = "datasets"
    IMAGE_FORMAT = "jpg"
    IMAGE_QUALITY = 95


class AppConfig:
    """General application configuration."""
    CAMERA = CameraConfig
    ARDUINO = ArduinoConfig
    UI = UIConfig
    DATA_LOGGER = DataLoggerConfig

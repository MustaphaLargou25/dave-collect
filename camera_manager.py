"""
Camera Manager Module

Handles camera initialization, configuration, and frame capture operations.
"""

import cv2
import numpy as np
from typing import Optional, Tuple, Dict, List
from datetime import datetime
import threading
import time


class CameraManager:
    """Manages camera operations including initialization, capture, and configuration."""
    
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480, role: str = "unknown"):
        """
        Initialize the camera manager.
        
        Args:
            camera_index: Index of the camera device (default: 0 for primary camera)
            width: Frame width in pixels
            height: Frame height in pixels
            role: Logical role of the camera (front, left, right)
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.role = role
        self.camera: Optional[cv2.VideoCapture] = None
        self.is_initialized = False
        self.current_frame: Optional[np.ndarray] = None
        self.frame_timestamp: Optional[str] = None
        self.frame_lock = threading.Lock()
        self.running = False
        self.capture_thread: Optional[threading.Thread] = None
    
    def initialize(self) -> bool:
        """
        Initialize the camera with configured settings.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                print(f"Error: Could not open camera {self.camera_index}")
                return False
            
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            self.is_initialized = True
            print(f"Camera initialized: {self.width}x{self.height}")
            return True
            
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def capture_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Capture a single frame from the camera.
        
        Returns:
            Tuple[bool, Optional[np.ndarray]]: (success, frame) where success indicates
                                                if capture was successful
        """
        if not self.is_initialized or self.camera is None:
            return False, None
        
        ret, frame = self.camera.read()
        
        if not ret:
            print("Error: Failed to capture frame")
            return False, None
        
        return True, frame

    def _capture_loop(self):
        """
        Continuous capture loop for non-blocking frame acquisition.
        """
        while self.running:
            if self.camera is not None and self.is_initialized:
                ret, frame = self.camera.read()
                if ret:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                    with self.frame_lock:
                        self.current_frame = frame
                        self.frame_timestamp = timestamp
            time.sleep(0.001)  # Small delay to prevent CPU overload

    def start_capture_thread(self):
        """
        Start the continuous capture thread for non-blocking frame acquisition.
        """
        if not self.is_initialized:
            return False
        
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        print(f"Camera {self.camera_index} ({self.role}) capture thread started")
        return True

    def stop_capture_thread(self):
        """
        Stop the continuous capture thread.
        """
        self.running = False
        if self.capture_thread is not None:
            self.capture_thread.join(timeout=1.0)
            self.capture_thread = None
        print(f"Camera {self.camera_index} ({self.role}) capture thread stopped")

    def get_latest_frame(self) -> Tuple[bool, Optional[np.ndarray], Optional[str]]:
        """
        Get the latest captured frame with timestamp (non-blocking).
        
        Returns:
            Tuple[bool, Optional[np.ndarray], Optional[str]]: (success, frame, timestamp)
        """
        with self.frame_lock:
            if self.current_frame is not None:
                return True, self.current_frame.copy(), self.frame_timestamp
            else:
                return False, None, None
    
    def get_frame_dimensions(self) -> Tuple[int, int]:
        """
        Get the current frame dimensions.
        
        Returns:
            Tuple[int, int]: (width, height) of frames
        """
        return self.width, self.height
    
    def set_resolution(self, width: int, height: int) -> bool:
        """
        Change the camera resolution.
        
        Args:
            width: New frame width
            height: New frame height
        
        Returns:
            bool: True if resolution changed successfully
        """
        if not self.is_initialized or self.camera is None:
            return False
        
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        self.width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Resolution changed to: {self.width}x{self.height}")
        return True
    
    def release(self):
        """Release the camera resource."""
        self.stop_capture_thread()
        if self.camera is not None:
            self.camera.release()
            self.is_initialized = False
            print(f"Camera {self.camera_index} ({self.role}) released")
    
    def __del__(self):
        """Ensure camera is released when object is destroyed."""
        self.release()

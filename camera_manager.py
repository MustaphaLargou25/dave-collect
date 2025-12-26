"""
Camera Manager Module

Handles camera initialization, configuration, and frame capture operations.
"""

import cv2
import numpy as np
from typing import Optional, Tuple


class CameraManager:
    """Manages camera operations including initialization, capture, and configuration."""
    
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        """
        Initialize the camera manager.
        
        Args:
            camera_index: Index of the camera device (default: 0 for primary camera)
            width: Frame width in pixels
            height: Frame height in pixels
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.camera: Optional[cv2.VideoCapture] = None
        self.is_initialized = False
    
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
        if self.camera is not None:
            self.camera.release()
            self.is_initialized = False
            print("Camera released")
    
    def __del__(self):
        """Ensure camera is released when object is destroyed."""
        self.release()

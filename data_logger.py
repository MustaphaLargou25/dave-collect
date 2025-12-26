"""
Data Logger Module

Handles logging and saving of captured images, sensor data, and metadata
to organized dataset folders.
"""

import os
import cv2
import json
from datetime import datetime
from typing import Optional, Dict, Any
import numpy as np


class DataLogger:
    """Manages data logging for images, labels, and metadata."""
    
    def __init__(self, base_path: str = "datasets"):
        """
        Initialize the data logger.
        
        Args:
            base_path: Base directory for storing datasets
        """
        self.base_path = base_path
        self.images_path = os.path.join(base_path, "images")
        self.labels_path = os.path.join(base_path, "labels")
        self.metadata_path = os.path.join(base_path, "metadata")
        
        self.session_id: Optional[str] = None
        self.capture_count = 0
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        os.makedirs(self.images_path, exist_ok=True)
        os.makedirs(self.labels_path, exist_ok=True)
        os.makedirs(self.metadata_path, exist_ok=True)
        print(f"Data logger initialized. Base path: {self.base_path}")
    
    def start_session(self, session_name: Optional[str] = None):
        """
        Start a new logging session with a unique identifier.
        
        Args:
            session_name: Optional custom session name. If None, uses timestamp.
        """
        if session_name:
            self.session_id = f"{session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.capture_count = 0
        print(f"Started logging session: {self.session_id}")
    
    def get_timestamp(self) -> str:
        """
        Get current timestamp string.
        
        Returns:
            str: Formatted timestamp
        """
        return datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
    
    def save_image(self, frame: np.ndarray, label: Optional[str] = None) -> Optional[str]:
        """
        Save a captured frame as an image.
        
        Args:
            frame: Image frame to save
            label: Optional label for the image
        
        Returns:
            Optional[str]: Filename if saved successfully, None otherwise
        """
        if frame is None:
            print("Error: Cannot save None frame")
            return None
        
        if self.session_id is None:
            self.start_session()
        
        timestamp = self.get_timestamp()
        if label:
            filename = f"{self.session_id}_{self.capture_count:04d}_{timestamp}_{label}.jpg"
        else:
            filename = f"{self.session_id}_{self.capture_count:04d}_{timestamp}.jpg"
        filepath = os.path.join(self.images_path, filename)
        
        try:
            cv2.imwrite(filepath, frame)
            self.capture_count += 1
            print(f"Image saved: {filename}")
            return filename
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    
    def save_label(self, filename: str, label_data: Dict[str, Any]) -> bool:
        """
        Save label/annotation data for a captured image.
        
        Args:
            filename: Name of the associated image file
            label_data: Dictionary containing label information
        
        Returns:
            bool: True if saved successfully
        """
        try:
            base_name = os.path.splitext(filename)[0]
            label_filename = f"{base_name}.json"
            label_filepath = os.path.join(self.labels_path, label_filename)
            
            with open(label_filepath, 'w') as f:
                json.dump(label_data, f, indent=2)
            
            print(f"Label saved: {label_filename}")
            return True
            
        except Exception as e:
            print(f"Error saving label: {e}")
            return False
    
    def save_metadata(self, filename: str, metadata: Dict[str, Any]) -> bool:
        """
        Save metadata for a capture (sensor data, timestamps, etc.).
        
        Args:
            filename: Name of the associated image file
            metadata: Dictionary containing metadata
        
        Returns:
            bool: True if saved successfully
        """
        try:
            base_name = os.path.splitext(filename)[0]
            metadata_filename = f"{base_name}.json"
            metadata_filepath = os.path.join(self.metadata_path, metadata_filename)
            
            metadata['timestamp'] = self.get_timestamp()
            metadata['session_id'] = self.session_id
            metadata['capture_number'] = self.capture_count - 1
            
            with open(metadata_filepath, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"Metadata saved: {metadata_filename}")
            return True
            
        except Exception as e:
            print(f"Error saving metadata: {e}")
            return False
    
    def save_capture(self, frame: np.ndarray, label_data: Optional[Dict[str, Any]] = None,
                    sensor_data: Optional[Dict[str, Any]] = None, camera_role: str = "unknown") -> bool:
        """
        Save a complete capture including image, label, and metadata.
        
        Args:
            frame: Image frame to save
            label_data: Optional label/annotation data
            sensor_data: Optional sensor readings
            camera_role: Role of the camera (front, left, right)
        
        Returns:
            bool: True if all data saved successfully
        """
        filename = self.save_image(frame, label=camera_role)
        
        if filename is None:
            return False
        
        success = True
        
        if label_data:
            success = success and self.save_label(filename, label_data)
        
        if sensor_data:
            metadata = {'sensor_data': sensor_data, 'camera_role': camera_role}
            success = success and self.save_metadata(filename, metadata)
        
        return success
    
    def save_session_summary(self) -> bool:
        """
        Save a summary of the current session.
        
        Returns:
            bool: True if saved successfully
        """
        if self.session_id is None:
            print("No active session to summarize")
            return False
        
        try:
            summary = {
                'session_id': self.session_id,
                'total_captures': self.capture_count,
                'start_time': self.session_id,
                'end_time': self.get_timestamp(),
                'images_path': self.images_path,
                'labels_path': self.labels_path,
                'metadata_path': self.metadata_path
            }
            
            summary_filename = f"session_{self.session_id}_summary.json"
            summary_filepath = os.path.join(self.metadata_path, summary_filename)
            
            with open(summary_filepath, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"Session summary saved: {summary_filename}")
            print(f"Total captures in session: {self.capture_count}")
            return True
            
        except Exception as e:
            print(f"Error saving session summary: {e}")
            return False
    
    def get_capture_count(self) -> int:
        """
        Get the number of captures in the current session.
        
        Returns:
            int: Number of captures
        """
        return self.capture_count
    
    def get_session_id(self) -> Optional[str]:
        """
        Get the current session ID.
        
        Returns:
            Optional[str]: Session ID or None if no active session
        """
        return self.session_id

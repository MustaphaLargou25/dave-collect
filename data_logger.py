"""
Data Logger Module

Handles logging and saving of captured images, sensor data, and metadata
to organized dataset folders.
"""

import os
import cv2
import json
import csv
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
        self.dataset_path = os.path.join(base_path, "dataset")
        self.views = ["front", "left", "right"]
        self.view_paths = {}
        
        self.csv_filename = "steering.csv"
        self.csv_filepath = os.path.join(self.dataset_path, self.csv_filename)
        
        self.session_id: Optional[str] = None
        self.capture_count = 0
        self.is_recording = False
        self.recording_start_time: Optional[datetime] = None
        
        self._ensure_directories()
        self._init_csv()
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        os.makedirs(self.dataset_path, exist_ok=True)
        for view in self.views:
            view_path = os.path.join(self.dataset_path, view)
            os.makedirs(view_path, exist_ok=True)
            self.view_paths[view] = view_path
        print(f"Data logger initialized. Dataset path: {self.dataset_path}")
    
    def _init_csv(self):
        """Initialize steering CSV file with headers."""
        if not os.path.exists(self.csv_filepath):
            with open(self.csv_filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'view', 'steering_angle', 'capture_index'])
    
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
    
    def start_recording(self):
        """Start recording data."""
        self.is_recording = True
        self.recording_start_time = datetime.now()
        print("Recording started")
    
    def stop_recording(self):
        """Stop recording data."""
        self.is_recording = False
        print("Recording stopped")
    
    def is_active(self) -> bool:
        """Check if recording is active."""
        return self.is_recording
    
    def get_timestamp(self) -> str:
        """
        Get current timestamp string.
        
        Returns:
            str: Formatted timestamp
        """
        return datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
    
    def save_steering_data(self, steering_angle: float, view: str = "front") -> bool:
        """
        Save steering angle with timestamp to CSV.
        
        Args:
            steering_angle: The steering angle value
            view: Which camera view this data belongs to
        
        Returns:
            bool: True if saved successfully
        """
        try:
            timestamp = self.get_timestamp()
            with open(self.csv_filepath, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, view, steering_angle, self.capture_count])
            return True
        except Exception as e:
            print(f"Error saving steering data: {e}")
            return False
    
    def save_image(self, frame: np.ndarray, view: str = "front", 
                   steering_angle: Optional[float] = None) -> Optional[str]:
        """
        Save a captured frame as an image in the appropriate view folder.
        
        Args:
            frame: Image frame to save
            view: Which view folder to save to (front, left, right)
            steering_angle: Optional steering angle to log
        
        Returns:
            Optional[str]: Filename if saved successfully, None otherwise
        """
        if frame is None:
            print("Error: Cannot save None frame")
            return None
        
        if view not in self.views:
            print(f"Error: Unknown view '{view}'. Valid views: {self.views}")
            return None
        
        if self.session_id is None:
            self.start_session()
        
        timestamp = self.get_timestamp()
        filename = f"{self.session_id}_{self.capture_count:04d}_{timestamp}.jpg"
        filepath = os.path.join(self.view_paths[view], filename)
        
        try:
            cv2.imwrite(filepath, frame)
            self.capture_count += 1
            
            if steering_angle is not None:
                self.save_steering_data(steering_angle, view)
            
            print(f"Image saved: {view}/{filename}")
            return filename
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    
    def save_label(self, filename: str, label_data: Dict[str, Any], view: str = "front") -> bool:
        """
        Save label/annotation data for a captured image.
        
        Args:
            filename: Name of the associated image file
            label_data: Dictionary containing label information
            view: Which view folder the image is in
        
        Returns:
            bool: True if saved successfully
        """
        try:
            base_name = os.path.splitext(filename)[0]
            view_folder = self.view_paths.get(view, self.view_paths["front"])
            label_filename = f"{base_name}.json"
            label_filepath = os.path.join(view_folder, label_filename)
            
            with open(label_filepath, 'w') as f:
                json.dump(label_data, f, indent=2)
            
            print(f"Label saved: {view}/{label_filename}")
            return True
            
        except Exception as e:
            print(f"Error saving label: {e}")
            return False
    
    def save_metadata(self, filename: str, metadata: Dict[str, Any], view: str = "front") -> bool:
        """
        Save metadata for a capture (sensor data, timestamps, etc.).
        
        Args:
            filename: Name of the associated image file
            metadata: Dictionary containing metadata
            view: Which view folder the image is in
        
        Returns:
            bool: True if saved successfully
        """
        try:
            base_name = os.path.splitext(filename)[0]
            view_folder = self.view_paths.get(view, self.view_paths["front"])
            metadata_filename = f"{base_name}.json"
            metadata_filepath = os.path.join(view_folder, metadata_filename)
            
            metadata['timestamp'] = self.get_timestamp()
            metadata['session_id'] = self.session_id
            metadata['capture_number'] = self.capture_count - 1
            
            with open(metadata_filepath, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"Metadata saved: {view}/{metadata_filename}")
            return True
            
        except Exception as e:
            print(f"Error saving metadata: {e}")
            return False
    
    def save_capture(self, frame: np.ndarray, view: str = "front",
                    steering_angle: Optional[float] = None,
                    label_data: Optional[Dict[str, Any]] = None,
                    sensor_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save a complete capture including image, steering data, label, and metadata.
        
        Args:
            frame: Image frame to save
            view: Which view folder to save to (front, left, right)
            steering_angle: Optional steering angle to log
            label_data: Optional label/annotation data
            sensor_data: Optional sensor readings
        
        Returns:
            bool: True if all data saved successfully
        """
        if not self.is_recording:
            print("Warning: Not recording. Call start_recording() first.")
            return False
        
        filename = self.save_image(frame, view, steering_angle)
        
        if filename is None:
            return False
        
        success = True
        
        if label_data:
            success = success and self.save_label(filename, label_data, view)
        
        if sensor_data:
            metadata = {'sensor_data': sensor_data}
            success = success and self.save_metadata(filename, metadata, view)
        
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
                'dataset_path': self.dataset_path,
                'views': self.views,
                'csv_file': self.csv_filename,
                'recording_active': self.is_recording
            }
            
            summary_filename = f"session_{self.session_id}_summary.json"
            summary_filepath = os.path.join(self.dataset_path, summary_filename)
            
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

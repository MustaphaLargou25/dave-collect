"""
Main Application Entry Point

Orchestrates all modules (camera, arduino, UI, data logger) to create
a complete data collection system.
"""

import sys
from typing import Optional, Dict, Any
from camera_manager import CameraManager
from arduino_serial import ArduinoSerial
from ui_pygame import PygameUI
from data_logger import DataLogger


class DataCollectionApp:
    """Main application class that coordinates all modules."""
    
    def __init__(self):
        """Initialize the application and all modules."""
        self.cameras: Dict[str, Optional[CameraManager]] = {}
        self.arduino: Optional[ArduinoSerial] = None
        self.ui: Optional[PygameUI] = None
        self.logger: Optional[DataLogger] = None
        
        self.running = False
        self.current_frames: Dict[str, Optional[np.ndarray]] = {}
        self.frame_timestamps: Dict[str, Optional[str]] = {}
        self.sensor_data = {}
        
        print("=" * 50)
        print("Data Collection System")
        print("=" * 50)
    
    def initialize_modules(self) -> bool:
        """
        Initialize all application modules.
        
        Returns:
            bool: True if all modules initialized successfully
        """
        print("\nInitializing modules...")
        
        # Initialize 3 cameras with assigned roles
        camera_configs = [
            {"index": 0, "role": "front", "position": (10, 10)},
            {"index": 1, "role": "left", "position": (660, 10)},
            {"index": 2, "role": "right", "position": (10, 360)}
        ]
        
        cameras_initialized = 0
        for config in camera_configs:
            try:
                camera = CameraManager(camera_index=config["index"], width=640, height=480, role=config["role"])
                if camera.initialize():
                    self.cameras[config["role"]] = camera
                    cameras_initialized += 1
                    print(f"Camera {config['index']} ({config['role']}) initialized successfully")
                else:
                    print(f"Warning: Camera {config['index']} ({config['role']}) initialization failed")
            except Exception as e:
                print(f"Error initializing camera {config['index']} ({config['role']}): {e}")
        
        if cameras_initialized == 0:
            print("Error: No cameras initialized successfully")
            return False
        
        # Start capture threads for all initialized cameras
        for role, camera in self.cameras.items():
            if camera:
                camera.start_capture_thread()
        
        self.arduino = ArduinoSerial(baudrate=9600)
        if not self.arduino.connect():
            print("Warning: Arduino connection failed - continuing without sensor data")
        
        self.ui = PygameUI(width=1280, height=960, title="Multi-Camera Data Collection System")
        if not self.ui.initialize():
            print("Error: UI initialization failed")
            return False
        
        self.logger = DataLogger(base_path="datasets")
        self.logger.start_session()
        
        print("\nInitialization complete!")
        print("\nControls:")
        print("  SPACE - Capture and save frames from all cameras")
        print("  S     - Save session summary")
        print("  ESC   - Quit application")
        print("-" * 50)
        
        return True
    
    def update_camera(self):
        """Update camera feeds from all cameras."""
        for role, camera in self.cameras.items():
            if camera and camera.is_initialized:
                success, frame, timestamp = camera.get_latest_frame()
                if success:
                    self.current_frames[role] = frame
                    self.frame_timestamps[role] = timestamp
    
    def update_sensors(self):
        """Update sensor data from Arduino."""
        if self.arduino and self.arduino.is_connected:
            data = self.arduino.read_sensor_data()
            if data:
                self.sensor_data = data
    
    def handle_capture(self):
        """Handle capture event - save frames from all cameras with sensor data."""
        if not self.logger:
            return False
        
        capture_success = False
        for role, frame in self.current_frames.items():
            if frame is not None:
                # Create metadata with timestamp and camera role
                metadata = {
                    'camera_role': role,
                    'timestamp': self.frame_timestamps.get(role, 'unknown'),
                    'sensor_data': self.sensor_data if self.sensor_data else None
                }
                
                # Save the capture with camera role information
                success = self.logger.save_capture(
                    frame=frame,
                    sensor_data=None,  # We'll use metadata instead
                    label_data={'camera_role': role},
                    camera_role=role
                )
                
                # Save metadata separately with timestamp
                if success:
                    filename = self.logger.save_image(frame, label=role)
                    if filename:
                        self.logger.save_metadata(filename, metadata)
                        capture_success = True
        
        if capture_success:
            print(f"Captures saved from all cameras! Total: {self.logger.get_capture_count()}")
            return True
        return False
    
    def handle_save_summary(self):
        """Handle save session summary event."""
        if self.logger:
            self.logger.save_session_summary()
    
    def render_ui(self):
        """Render the user interface."""
        if not self.ui:
            return
        
        self.ui.clear()
        
        # Draw frames from all cameras
        camera_positions = {
            'front': (10, 10),
            'left': (660, 10),
            'right': (10, 360)
        }
        
        for role, position in camera_positions.items():
            if role in self.current_frames and self.current_frames[role] is not None:
                self.ui.draw_frame(self.current_frames[role], position=position, scale=0.4)
                # Draw camera role label
                self.ui.draw_text(f"{role.upper()} CAMERA", (position[0], position[1] - 30), color='success', large=True)
                # Draw timestamp if available
                timestamp = self.frame_timestamps.get(role, '')
                if timestamp:
                    self.ui.draw_text(f"TS: {timestamp}", (position[0], position[1] - 5), color='text_secondary')
        
        # Draw session info panel
        frame_info_x = 660
        y_offset = 370
        
        self.ui.draw_panel((frame_info_x - 10, y_offset - 10, 350, 250), title="Session Info")
        y_offset += 50
        
        if self.logger:
            session_id = self.logger.get_session_id() or "N/A"
            capture_count = self.logger.get_capture_count()
            self.ui.draw_text(f"Session: {session_id[:20]}...", (frame_info_x, y_offset), color='text_secondary')
            y_offset += 30
            self.ui.draw_text(f"Captures: {capture_count}", (frame_info_x, y_offset), color='success')
            y_offset += 50
        
        # Draw camera status for each camera
        for role, camera in self.cameras.items():
            camera_status = "Connected" if (camera and camera.is_initialized) else "Disconnected"
            camera_color = "success" if (camera and camera.is_initialized) else "error"
            self.ui.draw_text(f"{role.upper()} Camera: {camera_status}", (frame_info_x, y_offset), color=camera_color)
            y_offset += 30
        
        arduino_status = "Connected" if (self.arduino and self.arduino.is_connected) else "Disconnected"
        arduino_color = "success" if (self.arduino and self.arduino.is_connected) else "warning"
        self.ui.draw_text(f"Arduino: {arduino_status}", (frame_info_x, y_offset), color=arduino_color)
        
        if self.sensor_data:
            sensor_y = 630
            self.ui.draw_panel((frame_info_x - 10, sensor_y, 350, 200), title="Sensor Data")
            self.ui.draw_sensor_data(self.sensor_data, (frame_info_x, sensor_y + 50))
        
        instructions_y = self.ui.height - 180
        self.ui.draw_panel((10, instructions_y, 300, 170))
        self.ui.draw_instructions((20, instructions_y + 10))
        
        fps_text = f"FPS: {self.ui.get_fps():.1f}"
        self.ui.draw_text(fps_text, (self.ui.width - 100, self.ui.height - 30), color='text_secondary')
        
        self.ui.update(fps=30)
    
    def run(self):
        """Main application loop."""
        if not self.initialize_modules():
            print("Failed to initialize modules. Exiting.")
            return
        
        self.running = True
        
        try:
            while self.running:
                events = self.ui.process_events()
                
                if events['quit'] or events['escape']:
                    self.running = False
                    break
                
                if events['capture']:
                    self.handle_capture()
                
                if events['save']:
                    self.handle_save_summary()
                
                self.update_camera()
                self.update_sensors()
                self.render_ui()
                
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown of all modules."""
        print("\nShutting down...")
        
        if self.logger:
            self.logger.save_session_summary()
        
        # Release all cameras
        for role, camera in self.cameras.items():
            if camera:
                camera.release()
        
        if self.arduino:
            self.arduino.disconnect()
        
        if self.ui:
            self.ui.quit()
        
        print("Shutdown complete. Goodbye!")


def main():
    """Application entry point."""
    app = DataCollectionApp()
    app.run()
    sys.exit(0)


if __name__ == "__main__":
    main()

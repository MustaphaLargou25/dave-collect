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
        self.camera: Optional[CameraManager] = None
        self.arduino: Optional[ArduinoSerial] = None
        self.ui: Optional[PygameUI] = None
        self.logger: Optional[DataLogger] = None
        
        self.running = False
        self.current_frame = None
        self.sensor_data = {}
        self.current_steering: Optional[float] = None
        self.last_steering_timestamp: float = 0.0
        
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
        
        self.camera = CameraManager(camera_index=0, width=640, height=480)
        if not self.camera.initialize():
            print("Warning: Camera initialization failed")
        
        self.arduino = ArduinoSerial(baudrate=9600)
        if not self.arduino.connect():
            print("Warning: Arduino connection failed - continuing without sensor data")
        
        self.ui = PygameUI(width=1024, height=768, title="Data Collection System")
        if not self.ui.initialize():
            print("Error: UI initialization failed")
            return False
        
        self.logger = DataLogger(base_path="datasets")
        self.logger.start_session()
        
        print("\nInitialization complete!")
        print("\nControls:")
        print("  SPACE - Capture and save frame")
        print("  S     - Save session summary")
        print("  ESC   - Quit application")
        print("-" * 50)
        
        return True
    
    def update_camera(self):
        """Update camera feed."""
        if self.camera and self.camera.is_initialized:
            success, frame = self.camera.capture_frame()
            if success:
                self.current_frame = frame
    
    def update_sensors(self):
        """Update sensor data from Arduino with high-precision timestamps."""
        if self.arduino and self.arduino.is_connected:
            steering, timestamp = self.arduino.read_steering_angle_with_timestamp()
            if steering is not None:
                self.current_steering = steering
                self.last_steering_timestamp = timestamp
                self.sensor_data = {'steering': steering}
    
    def handle_capture(self):
        """Handle capture event - save frame with synchronized sensor data and high-precision timestamps."""
        if self.current_frame is not None and self.logger:
            import time
            
            frame_timestamp = time.perf_counter() * 1e6
            
            steering = self.current_steering
            sensor_timestamp = self.last_steering_timestamp
            
            if steering is None and self.arduino and self.arduino.is_connected:
                steering, sensor_timestamp = self.arduino.read_steering_angle_with_timestamp()
            
            success = self.logger.save_sync_capture(
                frame=self.current_frame,
                steering_angle=steering,
                frame_timestamp=frame_timestamp,
                sensor_timestamp=sensor_timestamp
            )
            
            if success:
                print(f"Capture saved! Steering: {steering} | Time diff: {abs(frame_timestamp - sensor_timestamp):.1f}us | Total: {self.logger.get_capture_count()}")
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
        
        if self.current_frame is not None:
            self.ui.draw_frame(self.current_frame, position=(10, 10))
        
        frame_info_x = 660
        y_offset = 20
        
        self.ui.draw_panel((frame_info_x - 10, y_offset - 10, 350, 250), title="Session Info")
        y_offset += 50
        
        if self.logger:
            session_id = self.logger.get_session_id() or "N/A"
            capture_count = self.logger.get_capture_count()
            self.ui.draw_text(f"Session: {session_id[:20]}...", (frame_info_x, y_offset), color='text_secondary')
            y_offset += 30
            self.ui.draw_text(f"Captures: {capture_count}", (frame_info_x, y_offset), color='success')
            y_offset += 50
        
        camera_status = "Connected" if (self.camera and self.camera.is_initialized) else "Disconnected"
        camera_color = "success" if (self.camera and self.camera.is_initialized) else "error"
        self.ui.draw_text(f"Camera: {camera_status}", (frame_info_x, y_offset), color=camera_color)
        y_offset += 30
        
        arduino_status = "Connected" if (self.arduino and self.arduino.is_connected) else "Disconnected"
        arduino_color = "success" if (self.arduino and self.arduino.is_connected) else "warning"
        self.ui.draw_text(f"Arduino: {arduino_status}", (frame_info_x, y_offset), color=arduino_color)
        
        if self.sensor_data:
            sensor_y = 290
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
        
        if self.camera:
            self.camera.release()
        
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

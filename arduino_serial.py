"""
Arduino Serial Module

Handles serial communication with Arduino devices for sensor data collection.
"""

import serial
import serial.tools.list_ports
from typing import Optional, List, Dict, Any, Tuple
import time


class ArduinoSerial:
    """Manages serial communication with Arduino."""
    
    def __init__(self, port: Optional[str] = None, baudrate: int = 9600, timeout: float = 1.0):
        """
        Initialize Arduino serial communication.
        
        Args:
            port: Serial port name (e.g., 'COM3' or '/dev/ttyUSB0'). If None, auto-detect.
            baudrate: Communication baud rate (default: 9600)
            timeout: Read timeout in seconds (default: 1.0)
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected = False
    
    @staticmethod
    def list_available_ports() -> List[str]:
        """
        List all available serial ports.
        
        Returns:
            List[str]: List of available port names
        """
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def auto_detect_arduino(self) -> Optional[str]:
        """
        Attempt to auto-detect Arduino port.
        
        Returns:
            Optional[str]: Detected port name or None if not found
        """
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            if 'Arduino' in port.description or 'CH340' in port.description or 'USB Serial' in port.description:
                print(f"Detected Arduino on port: {port.device}")
                return port.device
        
        if ports:
            print(f"Arduino not auto-detected. Available ports: {[p.device for p in ports]}")
        else:
            print("No serial ports found")
        
        return None
    
    def connect(self) -> bool:
        """
        Establish connection to Arduino.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self.port is None:
                self.port = self.auto_detect_arduino()
                
                if self.port is None:
                    available_ports = self.list_available_ports()
                    if available_ports:
                        self.port = available_ports[0]
                        print(f"Using first available port: {self.port}")
                    else:
                        print("Error: No serial ports available")
                        return False
            
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            time.sleep(2)
            
            self.is_connected = True
            print(f"Connected to Arduino on {self.port} at {self.baudrate} baud")
            return True
            
        except serial.SerialException as e:
            print(f"Error connecting to Arduino: {e}")
            return False
    
    def disconnect(self):
        """Close the serial connection."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            print("Disconnected from Arduino")
    
    def send_command(self, command: str) -> bool:
        """
        Send a command to Arduino.
        
        Args:
            command: Command string to send
        
        Returns:
            bool: True if command sent successfully
        """
        if not self.is_connected or self.serial_connection is None:
            print("Error: Not connected to Arduino")
            return False
        
        try:
            self.serial_connection.write(f"{command}\n".encode())
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    
    def read_line(self) -> Optional[str]:
        """
        Read a line of data from Arduino.
        
        Returns:
            Optional[str]: Decoded line or None if no data available
        """
        if not self.is_connected or self.serial_connection is None:
            return None
        
        try:
            if self.serial_connection.in_waiting > 0:
                line = self.serial_connection.readline().decode('utf-8').strip()
                return line
        except Exception as e:
            print(f"Error reading from Arduino: {e}")
        
        return None
    
    def read_sensor_data(self) -> Optional[Dict[str, Any]]:
        """
        Read and parse sensor data from Arduino.
        Expected format: "sensor1:value1,sensor2:value2,..."
        
        Returns:
            Optional[Dict[str, Any]]: Parsed sensor data or None
        """
        line = self.read_line()
        
        if line is None:
            return None
        
        try:
            data = {}
            pairs = line.split(',')
            
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    try:
                        data[key.strip()] = float(value.strip())
                    except ValueError:
                        data[key.strip()] = value.strip()
            
            return data if data else None
            
        except Exception as e:
            print(f"Error parsing sensor data: {e}")
            return None
    
    def read_steering_angle_with_timestamp(self) -> Tuple[Optional[float], float]:
        """
        Read steering angle with a high-precision timestamp.
        
        Returns:
            Tuple[Optional[float], float]: (steering_angle, timestamp_us) where 
                timestamp_us is the read time in microseconds
        """
        timestamp_us = time.perf_counter() * 1e6
        
        data = self.read_sensor_data()
        
        if data is None:
            return None, timestamp_us
        
        steering_angle = data.get('steering') or data.get('steering_angle')
        
        if steering_angle is not None:
            return float(steering_angle), timestamp_us
        
        return None, timestamp_us
    
    def read_steering_angle(self) -> Optional[float]:
        """
        Read steering angle from Arduino.
        
        Returns:
            Optional[float]: Steering angle value or None if not available
        """
        data = self.read_sensor_data()
        
        if data is None:
            return None
        
        steering_angle = data.get('steering') or data.get('steering_angle')
        
        if steering_angle is not None:
            return float(steering_angle)
        
        return None
    
    def flush(self):
        """Flush the input and output buffers."""
        if self.is_connected and self.serial_connection:
            self.serial_connection.reset_input_buffer()
            self.serial_connection.reset_output_buffer()
    
    def __del__(self):
        """Ensure serial connection is closed when object is destroyed."""
        self.disconnect()

"""Arduino Serial Module

Handles serial communication with Arduino devices for sensor data collection.

This module also supports reading a potentiometer value (raw ADC) and converting
it into a steering angle (degrees) using a simple linear calibration.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Dict, List, Optional

import serial
import serial.tools.list_ports

logger = logging.getLogger(__name__)


class ArduinoSerial:
    """Manages serial communication with Arduino."""

    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: int = 9600,
        timeout: float = 1.0,
        *,
        pot_key: str = "pot",
        pot_min_raw: int = 0,
        pot_max_raw: int = 1023,
        steering_min_deg: float = -45.0,
        steering_max_deg: float = 45.0,
        steering_invert: bool = False,
        auto_reconnect: bool = True,
        reconnect_interval_sec: float = 2.0,
    ):
        """Initialize Arduino serial communication.

        Args:
            port: Serial port name (e.g., 'COM3' or '/dev/ttyUSB0'). If None, auto-detect.
            baudrate: Communication baud rate.
            timeout: Read timeout in seconds.
            pot_key: Key name used by Arduino when sending potentiometer data in key/value format.
            pot_min_raw: Minimum raw ADC value for the potentiometer calibration.
            pot_max_raw: Maximum raw ADC value for the potentiometer calibration.
            steering_min_deg: Steering angle corresponding to pot_min_raw.
            steering_max_deg: Steering angle corresponding to pot_max_raw.
            steering_invert: If True, invert the mapping (swap direction).
            auto_reconnect: If True, periodically attempt to reconnect after disconnect.
            reconnect_interval_sec: Minimum interval between reconnect attempts.
        """

        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        self.pot_key = pot_key
        self.pot_min_raw = pot_min_raw
        self.pot_max_raw = pot_max_raw
        self.steering_min_deg = steering_min_deg
        self.steering_max_deg = steering_max_deg
        self.steering_invert = steering_invert

        self.auto_reconnect = auto_reconnect
        self.reconnect_interval_sec = reconnect_interval_sec

        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected = False

        self.last_error: Optional[str] = None
        self.last_read_time: Optional[float] = None
        self.last_valid_data_time: Optional[float] = None
        self.consecutive_timeouts = 0
        self.invalid_line_count = 0

        self._last_reconnect_attempt: float = 0.0

    @staticmethod
    def list_available_ports() -> List[str]:
        """List all available serial ports."""

        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def auto_detect_arduino(self) -> Optional[str]:
        """Attempt to auto-detect Arduino port."""

        ports = serial.tools.list_ports.comports()

        for port in ports:
            if (
                "Arduino" in port.description
                or "CH340" in port.description
                or "USB Serial" in port.description
            ):
                print(f"Detected Arduino on port: {port.device}")
                return port.device

        if ports:
            print(f"Arduino not auto-detected. Available ports: {[p.device for p in ports]}")
        else:
            print("No serial ports found")

        return None

    def connect(self) -> bool:
        """Establish connection to Arduino."""

        try:
            if self.port is None:
                self.port = self.auto_detect_arduino()

                if self.port is None:
                    available_ports = self.list_available_ports()
                    if available_ports:
                        self.port = available_ports[0]
                        print(f"Using first available port: {self.port}")
                    else:
                        self.last_error = "No serial ports available"
                        print("Error: No serial ports available")
                        return False

            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.timeout,
            )

            time.sleep(2)

            self.serial_connection.reset_input_buffer()
            self.serial_connection.reset_output_buffer()

            self.is_connected = True
            self.last_error = None
            self.consecutive_timeouts = 0
            self.invalid_line_count = 0

            print(f"Connected to Arduino on {self.port} at {self.baudrate} baud")
            return True

        except (serial.SerialException, OSError) as e:
            self.last_error = str(e)
            self.is_connected = False
            print(f"Error connecting to Arduino: {e}")
            return False

    def _mark_disconnected(self, reason: str):
        self.last_error = reason
        self.is_connected = False

        try:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
        except Exception:
            pass
        finally:
            self.serial_connection = None

    def disconnect(self):
        """Close the serial connection."""

        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
            except Exception:
                pass

        self.serial_connection = None
        self.is_connected = False
        print("Disconnected from Arduino")

    def reconnect_if_needed(self) -> bool:
        """Attempt a reconnect if disconnected and auto_reconnect is enabled."""

        if self.is_connected:
            return True

        if not self.auto_reconnect:
            return False

        now = time.time()
        if now - self._last_reconnect_attempt < self.reconnect_interval_sec:
            return False

        self._last_reconnect_attempt = now
        return self.connect()

    def send_command(self, command: str) -> bool:
        """Send a command to Arduino."""

        if not self.is_connected or self.serial_connection is None:
            print("Error: Not connected to Arduino")
            return False

        try:
            self.serial_connection.write(f"{command}\n".encode("utf-8"))
            return True
        except (serial.SerialException, OSError, ValueError) as e:
            self._mark_disconnected(f"Serial write error: {e}")
            print(f"Error sending command: {e}")
            return False

    def read_line(self) -> Optional[str]:
        """Read a single line from Arduino.

        Returns:
            Decoded line without trailing newline, or None on timeout/no data.
            On serial errors/disconnects, it marks the connection as disconnected.
        """

        if not self.is_connected or self.serial_connection is None:
            return None

        try:
            raw = self.serial_connection.readline()

            if raw == b"":
                self.consecutive_timeouts += 1
                return None

            self.consecutive_timeouts = 0
            line = raw.decode("utf-8", errors="replace").strip()

            if not line:
                return None

            self.last_read_time = time.time()
            return line

        except (serial.SerialException, OSError) as e:
            self._mark_disconnected(f"Serial read error: {e}")
            print(f"Error reading from Arduino: {e}")
            return None

    @staticmethod
    def _parse_scalar(value: str) -> Any:
        value = value.strip()
        try:
            if re.fullmatch(r"-?\d+", value):
                return int(value)
            return float(value)
        except ValueError:
            return value

    def _parse_key_value_line(self, line: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {}

        pairs = [p.strip() for p in line.split(",") if p.strip()]
        for pair in pairs:
            if ":" in pair:
                key, value = pair.split(":", 1)
            elif "=" in pair:
                key, value = pair.split("=", 1)
            else:
                continue

            key = key.strip()
            if not key:
                continue

            data[key] = self._parse_scalar(value)

        return data

    def _extract_pot_raw(self, line: str, parsed: Optional[Dict[str, Any]] = None) -> Optional[int]:
        if parsed is None:
            parsed = {}

        if self.pot_key in parsed:
            value = parsed[self.pot_key]
            try:
                raw = int(float(value))
            except (TypeError, ValueError):
                return None
            return raw

        # Common alternate keys
        for key in ("pot_raw", "potentiometer", "steering_raw", "analog"):
            if key in parsed:
                try:
                    return int(float(parsed[key]))
                except (TypeError, ValueError):
                    return None

        # Plain integer line (most common simple Arduino sketches)
        if re.fullmatch(r"\s*-?\d+\s*", line):
            try:
                return int(line.strip())
            except ValueError:
                return None

        # "pot:512" / "pot=512" embedded
        match = re.search(r"(?:pot|steer|steering)\s*[:=]\s*(-?\d+)", line, flags=re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None

        return None

    def raw_to_steering_angle(self, raw: int) -> float:
        """Convert a raw potentiometer ADC value into steering angle degrees."""

        if self.pot_max_raw == self.pot_min_raw:
            raise ValueError("pot_max_raw must differ from pot_min_raw")

        raw_clamped = max(min(raw, max(self.pot_min_raw, self.pot_max_raw)), min(self.pot_min_raw, self.pot_max_raw))

        ratio = (raw_clamped - self.pot_min_raw) / (self.pot_max_raw - self.pot_min_raw)
        if self.steering_invert:
            ratio = 1.0 - ratio

        return self.steering_min_deg + ratio * (self.steering_max_deg - self.steering_min_deg)

    def read_sensor_data(self) -> Optional[Dict[str, Any]]:
        """Read and parse sensor data from Arduino.

        Supported formats:
          - key/value: "sensor1:value1,sensor2:value2" (also supports '=' delimiter)
          - raw potentiometer integer: "512" (interpreted as potentiometer raw)
          - embedded potentiometer: "pot:512" / "pot=512"

        If a potentiometer reading is detected, the returned dict will also include:
          - pot_raw
          - steering_angle_deg
        """

        line = self.read_line()
        if line is None:
            return None

        try:
            data: Dict[str, Any] = {}

            if ":" in line or "," in line or "=" in line:
                data = self._parse_key_value_line(line)

            pot_raw = self._extract_pot_raw(line, data)
            if pot_raw is not None:
                # Basic validation: reject obviously wrong ADC values
                if pot_raw < 0 or pot_raw > 4095:
                    self.invalid_line_count += 1
                    return None

                angle = self.raw_to_steering_angle(pot_raw)
                data.setdefault(self.pot_key, pot_raw)
                data["pot_raw"] = pot_raw
                data["steering_angle_deg"] = round(angle, 3)

            if not data:
                self.invalid_line_count += 1
                return None

            self.last_valid_data_time = time.time()
            return data

        except ValueError as e:
            # Conversion/calibration error
            self.last_error = str(e)
            self.invalid_line_count += 1
            logger.exception("Error parsing sensor data")
            return None
        except Exception as e:
            self.last_error = str(e)
            self.invalid_line_count += 1
            print(f"Error parsing sensor data: {e}")
            return None

    def read_steering_angle(self) -> Optional[float]:
        """Read a potentiometer value and return steering angle in degrees."""

        data = self.read_sensor_data()
        if not data:
            return None

        angle = data.get("steering_angle_deg")
        if isinstance(angle, (int, float)):
            return float(angle)

        return None

    def flush(self):
        """Flush the input and output buffers."""

        if self.is_connected and self.serial_connection:
            try:
                self.serial_connection.reset_input_buffer()
                self.serial_connection.reset_output_buffer()
            except (serial.SerialException, OSError) as e:
                self._mark_disconnected(f"Serial flush error: {e}")

    def __del__(self):
        """Ensure serial connection is closed when object is destroyed."""

        try:
            self.disconnect()
        except Exception:
            pass

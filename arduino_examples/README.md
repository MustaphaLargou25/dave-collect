# Arduino Examples

This directory contains Arduino sketches that work with the Data Collection System.

## Potentiometer Steering Angle Reader

**File**: `potentiometer_steering.ino`

### Purpose
Reads a potentiometer value and sends it over serial to the Python application, which converts it to a steering angle in degrees.

### Hardware Setup

1. **Components Needed:**
   - Arduino board (Uno, Nano, Mega, etc.)
   - 10K potentiometer
   - USB cable
   - Breadboard and jumper wires (optional)

2. **Wiring:**
   ```
   Potentiometer Pin 1 (outer) → Arduino 5V
   Potentiometer Pin 2 (wiper)  → Arduino A0
   Potentiometer Pin 3 (outer) → Arduino GND
   ```

### Upload Instructions

1. Open `potentiometer_steering.ino` in Arduino IDE
2. Select your board: `Tools → Board → [Your Arduino Model]`
3. Select the correct port: `Tools → Port → [Your Arduino Port]`
4. Click Upload button (→)
5. Wait for "Done uploading" message

### Configuration

The sketch supports three output formats (set `FORMAT` constant):

1. **FORMAT_SIMPLE**: Just the raw value
   ```
   512
   513
   514
   ```

2. **FORMAT_KEY_VALUE**: Key-value pairs (recommended)
   ```
   pot:512
   pot:513
   pot:514
   ```

3. **FORMAT_EXTENDED**: Multiple values with timestamp
   ```
   pot:512,time:12345
   pot:513,time:12395
   ```

### Calibration

The Python application in `config.py` has calibration settings:

```python
POTENTIOMETER_MIN_RAW = 0      # Raw value at minimum position
POTENTIOMETER_MAX_RAW = 1023   # Raw value at maximum position
STEERING_MIN_DEG = -45.0       # Steering angle at minimum
STEERING_MAX_DEG = 45.0        # Steering angle at maximum
STEERING_INVERT = False        # Flip direction if needed
```

**To calibrate:**

1. Upload the Arduino sketch
2. Open Serial Monitor (Tools → Serial Monitor)
3. Set baud rate to 9600
4. Turn potentiometer fully left → note the value (e.g., 10)
5. Turn potentiometer fully right → note the value (e.g., 1015)
6. Update `config.py`:
   ```python
   POTENTIOMETER_MIN_RAW = 10
   POTENTIOMETER_MAX_RAW = 1015
   ```

### Testing

1. **Test in Arduino IDE:**
   - Open Serial Monitor (Ctrl+Shift+M)
   - Set baud rate to 9600
   - You should see values updating as you turn the potentiometer

2. **Test with Python application:**
   ```bash
   python main.py
   ```
   - The UI should show "Arduino: Connected"
   - Sensor data panel should display:
     - `pot_raw`: Raw ADC value (0-1023)
     - `steering_angle_deg`: Calculated angle

### Troubleshooting

**Problem**: No values in Serial Monitor
- Check USB connection
- Verify correct port selected
- Try pressing Reset button on Arduino

**Problem**: Values don't change when turning potentiometer
- Check wiring connections
- Verify potentiometer is connected to correct analog pin (A0)
- Test potentiometer with multimeter

**Problem**: Values are noisy/jumpy
- Add decoupling capacitor (0.1µF) between A0 and GND
- Enable averaging in the sketch (see calibration notes)
- Ensure good connections

**Problem**: Python app can't connect to Arduino
- Close Arduino Serial Monitor (can't have two programs using same port)
- Check port name in `config.py` or let it auto-detect
- Verify serial permissions on Linux: `sudo usermod -a -G dialout $USER`

**Problem**: Steering angle is reversed
- Set `STEERING_INVERT = True` in `config.py`

### Advanced Modifications

#### Add Smoothing Filter
```cpp
const int NUM_SAMPLES = 10;
long sum = 0;
for (int i = 0; i < NUM_SAMPLES; i++) {
    sum += analogRead(POT_PIN);
    delay(1);
}
int potValue = sum / NUM_SAMPLES;
```

#### Add Multiple Sensors
```cpp
int pot1 = analogRead(A0);
int pot2 = analogRead(A1);
Serial.print("pot1:");
Serial.print(pot1);
Serial.print(",pot2:");
Serial.println(pot2);
```

#### Increase Update Rate
```cpp
const int READ_DELAY_MS = 20;  // 50Hz update rate
```

## Additional Examples

More Arduino examples can be added to this directory. The Python application's `ArduinoSerial` class supports:

- Simple integer values
- Key-value pairs (with `:` or `=` delimiter)
- Multiple comma-separated values
- Custom sensor names

All examples should use 9600 baud rate by default (configurable in `config.py`).

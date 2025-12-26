/*
 * Arduino Potentiometer Steering Angle Reader
 * 
 * This sketch reads a potentiometer value connected to an analog pin
 * and sends it over serial to a Python application.
 * 
 * Hardware Setup:
 *   - Connect a 10K potentiometer to analog pin A0
 *   - Connect the outer pins to 5V and GND
 *   - Connect the middle (wiper) pin to A0
 * 
 * Output Format Options:
 *   1. Simple integer: "512"
 *   2. Key-value format: "pot:512"
 *   3. Extended format: "pot:512,other_sensor:123"
 */

const int POT_PIN = A0;        // Analog pin connected to potentiometer
const int BAUD_RATE = 9600;    // Serial communication speed
const int READ_DELAY_MS = 50;  // Delay between readings (50ms = 20Hz)

// Output format (choose one)
enum OutputFormat {
  FORMAT_SIMPLE,      // Just the number: "512"
  FORMAT_KEY_VALUE,   // Key-value: "pot:512"
  FORMAT_EXTENDED     // Extended with timestamp: "pot:512,time:12345"
};

const OutputFormat FORMAT = FORMAT_KEY_VALUE;

void setup() {
  Serial.begin(BAUD_RATE);
  
  // Wait for serial port to connect (for Leonardo/Micro)
  while (!Serial) {
    ; // wait for serial port to connect
  }
  
  pinMode(POT_PIN, INPUT);
  
  Serial.println("# Arduino Potentiometer Reader Started");
  Serial.print("# Format: ");
  
  switch (FORMAT) {
    case FORMAT_SIMPLE:
      Serial.println("SIMPLE");
      break;
    case FORMAT_KEY_VALUE:
      Serial.println("KEY_VALUE");
      break;
    case FORMAT_EXTENDED:
      Serial.println("EXTENDED");
      break;
  }
}

void loop() {
  // Read the potentiometer value (0-1023 on most Arduinos)
  int potValue = analogRead(POT_PIN);
  
  // Send data based on selected format
  switch (FORMAT) {
    case FORMAT_SIMPLE:
      // Simple format: just the raw value
      Serial.println(potValue);
      break;
      
    case FORMAT_KEY_VALUE:
      // Key-value format: "pot:512"
      Serial.print("pot:");
      Serial.println(potValue);
      break;
      
    case FORMAT_EXTENDED:
      // Extended format with multiple values
      Serial.print("pot:");
      Serial.print(potValue);
      Serial.print(",time:");
      Serial.println(millis());
      break;
  }
  
  delay(READ_DELAY_MS);
}


/*
 * CALIBRATION NOTES:
 * 
 * If your potentiometer reads reversed (e.g., left = 1023, right = 0):
 * - Set STEERING_INVERT = True in config.py
 * - Or invert in Arduino code: potValue = 1023 - potValue;
 * 
 * If your potentiometer doesn't use the full range:
 * - Adjust POTENTIOMETER_MIN_RAW and POTENTIOMETER_MAX_RAW in config.py
 * - Or use map() function in Arduino:
 *   potValue = map(analogRead(POT_PIN), actualMin, actualMax, 0, 1023);
 * 
 * For smoother readings, add averaging:
 * 
 *   const int NUM_SAMPLES = 10;
 *   long sum = 0;
 *   for (int i = 0; i < NUM_SAMPLES; i++) {
 *     sum += analogRead(POT_PIN);
 *     delay(1);
 *   }
 *   int potValue = sum / NUM_SAMPLES;
 */

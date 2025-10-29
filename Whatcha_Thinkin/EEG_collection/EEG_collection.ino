#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads; 

// Filter parameters
const float alpha = 0.95;  // IIR filter coefficient for DC removal

// Variables for filtering
float lastDCValue = 0;

// Butterworth filter coefficients for bandpass (~8Hz to ~100Hz at 250Hz sampling)
// These coefficients were pre-calculated for a 4th order Butterworth filter
// Higher sampling rate needed for gamma waves (up to 100Hz)
const int FILTER_ORDER = 4;
float a[FILTER_ORDER+1] = {1.0000, -3.0636, 3.5416, -1.8369, 0.3598}; // Denominator coefficients
float b[FILTER_ORDER+1] = {0.0291, 0.0000, -0.0582, 0.0000, 0.0291};  // Numerator coefficients

// Filter state variables
float x[FILTER_ORDER+1] = {0}; // Input history
float y[FILTER_ORDER+1] = {0}; // Output history

// Timing for consistent sampling rate
unsigned long lastSampleTime = 0;
const int samplingInterval = 4;  // 4ms = 250Hz sampling rate (needed for gamma waves)

void setup() {
  Serial.begin(115200);  // Fast serial for EEG data
  Wire.begin();          // Initialize I2C
  
  // Initialize ADS1115
  if (!ads.begin()) {
    Serial.println("ADS1115 not found!");
    while (1);  // Halt if initialization fails
  }
  
  // Configure gain for EEG signals
  ads.setGain(GAIN_SIXTEEN);  // ±0.256V range (1 bit = 7.8125µV)
  
  // Set ADC data rate to highest possible
  ads.setDataRate(RATE_ADS1115_860SPS);
  
  // Brief startup message
  Serial.println("raw,voltage,filtered");
}

// Apply Butterworth filter to input sample
float applyFilter(float input) {
  // Shift input history
  for (int i = FILTER_ORDER; i > 0; i--) {
    x[i] = x[i-1];
  }
  x[0] = input;
  
  // Calculate output
  float output = 0;
  for (int i = 0; i <= FILTER_ORDER; i++) {
    output += b[i] * x[i];
  }
  
  for (int i = 1; i <= FILTER_ORDER; i++) {
    output -= a[i] * y[i-1];
  }
  
  // Shift output history
  for (int i = FILTER_ORDER; i > 0; i--) {
    y[i] = y[i-1];
  }
  y[0] = output;
  
  return output;
}

void loop() {
  // Maintain consistent sampling rate
  unsigned long currentTime = micros();
  if (currentTime - lastSampleTime >= samplingInterval * 1000) {
    lastSampleTime = currentTime;
    
    // Read differential voltage between A0 (EEG signal) and A1 (reference)
    int16_t raw_value = ads.readADC_Differential_0_1();
    
    // Convert raw value to microvolts (µV)
    float voltage_uv = raw_value * 7.8125;  // For GAIN_SIXTEEN
    
    // DC offset removal (high-pass filter)
    lastDCValue = alpha * lastDCValue + (1 - alpha) * voltage_uv;
    float dc_removed = voltage_uv - lastDCValue;
    
    // Apply bandpass filter to capture both beta (13-30Hz) and gamma (30-100Hz) waves
    float filtered = applyFilter(dc_removed);
    
    // Send data to Python in easily parseable format
    Serial.print(raw_value);
    Serial.print(",");
    Serial.print(voltage_uv);
    Serial.print(",");
    Serial.println(filtered);
  }
}

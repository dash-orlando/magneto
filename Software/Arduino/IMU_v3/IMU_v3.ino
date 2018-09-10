/*
 *  Obtain magnetic field vector using multiplexed LSM9DS1 IMU sensors.
 *  Obtained values take into account the magnetic field of the earth
 *  and the immediate surrounding area and SUBTRACTS them from the readings
 *  to give a calibrated reading independent of the surrounding magnetic field.
 *
 *  AUTHOR                  : Edward Daniel Nichols
 *  LAST CONTRIBUTION DATE  : Sep. 29th, 2017, Year of Our Lord
 *
 *  AUTHOR                  : Mohammad Odeh 
 *  LAST CONTRIBUTION DATE  : Oct. 26th, 2017 Year of Our Lord
 *
 *  CHANGELOG:-
 *   1- Use 2 I2C addresses for communicating with sensors
 *                (Improves data output rate)
 */

// Include required libraries
#include <Wire.h>
#include <SPI.h>
#include <SparkFunLSM9DS1.h>

// Define important constants
#define LSM9DS1_M_HIGH        0x1E    // Would be 0x1C if SDO_M is LOW
#define LSM9DS1_AG_HIGH       0x6B    // Would be 0x6A if SDO_AG is LOW
#define LSM9DS1_M_LOW         0x1C    // SDO_M on these IMU's are LOW
#define LSM9DS1_AG_LOW        0x6B    // SDO_AG on these IMU's are HIGH [PINS NOT GROUNDED]***
#define CALIBRATION_INDEX     50      // Accounting for ambient magnetic fields
#define BAUDRATE              115200  // Serial communication baudrate
#define NPINS                 3       // Number of select pins
#define NSENS                 6       // Number of sensors
#define NPAIR                 3       // Number of pairs
#define NAXES                 3       // Number of axes

LSM9DS1 imuHIGH;                      // Instantiate sensors associated with I2C address of HIGH
LSM9DS1 imuLOW;                       // Instantiate sensors associated with I2C address of LOW

byte Sx_pin[3]  = {8, 9, 10};         // Select pins: {S0, S1, S2}

// Calibration (BASE) readings
static double imu_BASE[NSENS][NAXES] =  { {0, 0, 0},    //  {1x, 1y, 1z}
                                          {0, 0, 0},    //  {2x, 2y, 2z}
                                          {0, 0, 0},    //  {3x, 3y, 3z}
                                          {0, 0, 0},    //  {4x, 4y, 4z}
                                          {0, 0, 0},    //  {5x, 5y, 5z}
                                          {0, 0, 0} };  //  {6x, 6y, 6z}

// Enumerate sensor states ( 0==sensor1, 1==sensor2, ..., n==sensor(n+1) )
enum State { SEN_ERR, SEN_OK };
State sensorState[NSENS]  = { };      // Is the sensor detected and working?

void setup() {
  Serial.begin( BAUDRATE );           // Start serial monitor

  pinMode( 13, OUTPUT );              // Turn LED ON to know
  digitalWrite( 13, HIGH );           // Teensy ain't dead

  for ( byte i = 0; i < NPINS; i++ ) {
    pinMode( Sx_pin[i], OUTPUT );     // Set "Select Pins" as output
  }

  // Initialize sensors and load settings
  for (byte i = 0; i < NPAIR; i++) {
    sensorPairSelect(i);              // Switch between sensors
    setupIMU();                       // Setup IMUs
    calibrateIMU(HIGH, i);            // Calibrate Sensors
    calibrateIMU(LOW , i);            // Calibrate Sensors
  } Serial.println( F("Success.") );  // SUCCESS!
}

void loop() {

  // IMU readings (RAW)
  static double imu_RAW_X = 0;
  static double imu_RAW_Y = 0;
  static double imu_RAW_Z = 0;

  
  Serial.print("<");                                                // Start of data specifier

  // Obtain readings from ALL sensors
  for (byte i = 0; i < NPAIR; i++) {                                // Loop over the sensor pairs

    if(sensorState[2*i] == SEN_OK && sensorState[2*i+1] == SEN_OK) {// Set Sensor IFF it was INITIALIZED
      sensorPairSelect(i);                                          // Loop over sensors
      while ( !imuHIGH.magAvailable() && !imuLOW.magAvailable() );  // Check if sensor is ready

      // ------------------------------ SENSORS ON HIGH I2C ADDRESS ------------------------------
      
      imuHIGH.readMag();                                            // Do readings
      imu_RAW_X = double( imuHIGH.calcMag(imuHIGH.mx) );            //
      imu_RAW_Y = double( imuHIGH.calcMag(imuHIGH.my) );            // Store in temporary variable
      imu_RAW_Z = double( imuHIGH.calcMag(imuHIGH.mz) );            //

      // Subtract BASE readings from RAW readings to get CALIBRATED readings
      Serial.print(( imu_RAW_X - imu_BASE[2*i][0] ), 5);            // Print X readings to Serial
      Serial.print(", ");                                           // Comma delimit output
      Serial.print(( imu_RAW_Y - imu_BASE[2*i][1] ), 5);            // Print readings to Serial
      Serial.print(", ");                                           // Comma Y delimit output
      Serial.print(( imu_RAW_Z - imu_BASE[2*i][2] ), 5);            // Print Z readings to Serial
      Serial.print(", ");                                           // Comma Z delimit output

      // ------------------------------ SENSORS ON LOW I2C ADDRESS -------------------------------
      
      imuLOW.readMag();                                             // Do readings
      imu_RAW_X = double( imuLOW.calcMag(imuLOW.mx) );              //
      imu_RAW_Y = double( imuLOW.calcMag(imuLOW.my) );              // Store in temporary variable
      imu_RAW_Z = double( imuLOW.calcMag(imuLOW.mz) );              //

      // Subtract BASE readings from RAW readings to get CALIBRATED readings
      Serial.print(( imu_RAW_X - imu_BASE[2*i+1][0] ), 5);          // Print X readings to Serial
      Serial.print(", ");                                           // Comma delimit output
      Serial.print(( imu_RAW_Y - imu_BASE[2*i+1][1] ), 5);          // Print readings to Serial
      Serial.print(", ");                                           // Comma Y delimit output
      Serial.print(( imu_RAW_Z - imu_BASE[2*i+1][2] ), 5);          // Print Z readings to Serial
    }

    if(i != NPAIR - 1) Serial.print(", ");                              // Comma delimit output
  }
  Serial.print(">\n");                                              // End of data specifier
}

// =========================    Setup IMU       ========================
void setupIMU() {

  // ---------------------------------------- HIGH IMU Setup ---------------------------------------
  
  imuHIGH.settings.device.commInterface = IMU_MODE_I2C;   //
  imuHIGH.settings.device.mAddress      = LSM9DS1_M_HIGH; // Load IMU settings
  imuHIGH.settings.device.agAddress     = LSM9DS1_AG_HIGH;//

  imuHIGH.settings.gyro.enabled         = false;          // Disable gyro
  imuHIGH.settings.accel.enabled        = false;          // Disable accelerometer
  imuHIGH.settings.mag.enabled          = true;           // Enable magnetometer
  imuHIGH.settings.temp.enabled         = true;           // Enable temperature sensor

  imuHIGH.settings.mag.scale            = 16;             // Set mag scale to +/-12 Gs
  imuHIGH.settings.mag.sampleRate       = 7;              // Set OD rate to 80Hz
  imuHIGH.settings.mag.tempCompensationEnable = true;     // Enable temperature compensation (good stuff!)

  imuHIGH.settings.mag.XYPerformance    = 3;              // 0 = Low || 1 = Medium || 2 = High || 3 = Ultra-high
  imuHIGH.settings.mag.ZPerformance     = 3;              // Ultra-high performance

  imuHIGH.settings.mag.lowPowerEnable   = false;          // Disable low power mode
  imuHIGH.settings.mag.operatingMode    = 0;              // 0 = Continuous || 1 = Single || 2 = OFF

  // ---------------------------------------- LOW IMU Setup ----------------------------------------

  imuLOW.settings.device.commInterface = IMU_MODE_I2C;    //
  imuLOW.settings.device.mAddress      = LSM9DS1_M_LOW;   // Load IMU settings
  imuLOW.settings.device.agAddress     = LSM9DS1_AG_LOW;  //

  imuLOW.settings.gyro.enabled         = false;           // Disable gyro
  imuLOW.settings.accel.enabled        = false;           // Disable accelerometer
  imuLOW.settings.mag.enabled          = true;            // Enable magnetometer
  imuLOW.settings.temp.enabled         = true;            // Enable temperature sensor

  imuLOW.settings.mag.scale            = 16;              // Set mag scale to +/-12 Gs
  imuLOW.settings.mag.sampleRate       = 7;               // Set OD rate to 80Hz
  imuLOW.settings.mag.tempCompensationEnable = true;      // Enable temperature compensation (good stuff!)

  imuLOW.settings.mag.XYPerformance    = 3;               // 0 = Low || 1 = Medium || 2 = High || 3 = Ultra-high
  imuLOW.settings.mag.ZPerformance     = 3;               // Ultra-high performance

  imuLOW.settings.mag.lowPowerEnable   = false;           // Disable low power mode
  imuLOW.settings.mag.operatingMode    = 0;               // 0 = Continuous || 1 = Single || 2 = OFF

}

// =========================   Calibrate IMU    ========================
void calibrateIMU ( bool state, byte i ) {

  // Calibrate sensors that are on HIGH
  // LOW: INDEX[2*i]
  if ( state == HIGH ) {
    // Temporary value holders needed for calibration
    double imu_hold[NAXES] = {0, 0, 0};         // {x, y, z}
    if ( !imuHIGH.begin() ) {                   // Check if device is initialized
      sensorState[2*i] = SEN_ERR;               // Sensor ERROR

      Serial.print( F("Failed to communicate with LSM9DS1 ") );
      Serial.println( 2*i + 1 );

    } else {
      sensorState[2*i] = SEN_OK;                // Sensor is OK

      Serial.print( F("Calibrating sensor ") );
      Serial.println( 2*i + 1 );
      imuHIGH.calibrateMag();                   // Call built-in function to calculate bias

      // Perform our own calibration process to further clear noise
      for (int j = 0; j < CALIBRATION_INDEX ; j++) {
        delay( 25 );                            // Delay for stability
        while ( !imuHIGH.magAvailable() );      // Wait until readings are available

        imuHIGH.readMag();                      // Perform readings and store into temp holders
        imu_hold[0] += imuHIGH.calcMag( imuHIGH.mx );
        imu_hold[1] += imuHIGH.calcMag( imuHIGH.my );
        imu_hold[2] += imuHIGH.calcMag( imuHIGH.mz );

        // Get average
        if (j == CALIBRATION_INDEX - 1) {
          for ( byte k = 0; k < NAXES; k++) {
            imu_BASE[2*i][k] = imu_hold[k] / CALIBRATION_INDEX;
          }
        }
      }
    }
  }

  // Calibrate sensors that are on LOW
  // LOW: INDEX[2*i + 1]
  else if ( state == LOW ) {
    // Temporary value holders needed for calibration
    double imu_hold[NAXES] = {0, 0, 0};         // {x, y, z}
    if ( !imuLOW.begin() ) {                    // Check if device is initialized
      sensorState[2*i + 1] = SEN_ERR;           // Sensor ERROR

      Serial.print( F("Failed to communicate with LSM9DS1 ") );
      Serial.println( 2*i + 1 + 1);

    } else {
      sensorState[2*i + 1] = SEN_OK;            // Sensor is OK

      Serial.print( F("Calibrating sensor ") );
      Serial.println( 2*i + 1 + 1);
      imuLOW.calibrateMag();                    // Call built-in function to calculate bias

      // Perform our own calibration process to further clear noise
      for (int j = 0; j < CALIBRATION_INDEX ; j++) {
        delay( 25 );                            // Delay for stability
        while ( !imuLOW.magAvailable() );       // Wait until readings are available

        imuLOW.readMag();                       // Perform readings and store into temp holders
        imu_hold[0] += imuLOW.calcMag( imuLOW.mx );
        imu_hold[1] += imuLOW.calcMag( imuLOW.my );
        imu_hold[2] += imuLOW.calcMag( imuLOW.mz );

        // Get average
        if (j == CALIBRATION_INDEX - 1) {
          for ( byte k = 0; k < NAXES; k++) {
            imu_BASE[2*i+1][k] = imu_hold[k] / CALIBRATION_INDEX;
          }
        }
      }
    }
  }
}


// =========================    Set Sensor      ========================
void sensorPairSelect( byte sensorIndex ) {
  // The multiplexer is tied s.t. Teensy pin {8, 9, 10} -> {S0, S1, S2}
  // The output line Y0 ties to Sensors 1 and 2
  // The output line Y1 ties to Sensors 3 and 4
  // The output line Y2 ties to Sensors 5 and 6
  // More sensor pairs can be included

  // Sensor Pair 1, 000 ---> Y0
  if ( sensorIndex == 0 ) {
    for (byte i = 0; i < NPINS; i++) {
      digitalWrite(Sx_pin[i], LOW);
    }
  }

  // Sensor Pair 2, 001 ---> Y1
  else if ( sensorIndex == 1 ) {
    for (byte i = 0; i < NPINS; i++) {
      if (i == 0) {
        digitalWrite(Sx_pin[i], HIGH);
      } else digitalWrite(Sx_pin[i], LOW);
    }
  }

  // Sensor Pair 3, 010 ---> Y2
  else if ( sensorIndex == 2 ) {
    for (byte i = 0; i < NPINS; i++) {
      if (i == 1) {
        digitalWrite(Sx_pin[i], HIGH);
      } else digitalWrite(Sx_pin[i], LOW);
    }
  }

  // Else, something is wrong
  else Serial.println( F("Invalid Index") );
}

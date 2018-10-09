// Include required libraries
#include <Wire.h>
#include <SPI.h>
#include <SparkFunLSM9DS1.h>

// Define importatnt constants
#define LSM9DS1_M_HIGH                0x1E    // SDO_M on these IMU's are HIGH
#define LSM9DS1_AG_HIGH               0x6B    // SDO_AG on these IMU's are HIGH 
#define LSM9DS1_M_LOW                 0x1C    // SDO_M on these IMU's are LOW
#define LSM9DS1_AG_LOW                0x6B    // SDO_AG on these IMU's are HIGH [PINS NOT GROUNDED]***
#define CALIBRATION_INDEX             20      // Accounting for ambient magnetic fields
#define DECLINATION                   6.55    // Accounting for the Earth's magnetic field
#define BAUDRATE                      115200  // Serial communication baudrate
#define MUX_PIN                       10      // Multiplexer "Select pin"
#define DEBOUNCE                      5

// Timing variables. It occurs to me that we'd like to measure this output.
// Start time is the measurement taken at the beginning of the loop.
// End time is the measurement at the end of the loop.
// Loop time is the saved measurement of End time to carryover during the next loop.
double start_time = 0, loop_time = 0;

// The multiplexer will only transition across two output channels (Y0=000 and Y1=001).
// Since only one of the input pins is significant, this selecting variable will suffice with just two states.
// Of course, true= 1, false= 0.
bool state;

// Sensor calibration variables: To store the baseline values for the each sensor.
static double cal_imu0_x = 0,
              cal_imu0_y = 0,
              cal_imu0_z = 0,
              cal_imu1_x = 0,
              cal_imu1_y = 0,
              cal_imu1_z = 0,
              cal_imu2_x = 0,
              cal_imu2_y = 0,
              cal_imu2_z = 0,
              cal_imu3_x = 0,
              cal_imu3_y = 0,
              cal_imu3_z = 0;

// Declare sensor class
LSM9DS1 imuHigh;
LSM9DS1 imuLow;

void setup() {
  //Future self, before you go through this, I know there are much more efficient ways to write this code.
  //My purpose is to prove a concept and write the code quickly, which for me is easier by copy-pasting.
  //Sorry!
  //  -Past Self

  Serial.begin( BAUDRATE );           // Start serial monitor
  Serial.println( F("Confirming local sensor addresses...") );

  //Hence, since we have two addresses, each MUX state can support two sensors.
  //In order to set this up properly, we need to "setup" every sensor.
  //This means picking a pair of sensors, calibrating and setting them up individually.
  //Then, switching to the other pair of sensors, and doing the same.

  //Select Sensor Pair at LOW for the first two sensors.
  //Sensors: 1 (HIGH) and 2 (LOW)
  //We're going to call this state 0:
  pinMode(MUX_PIN, OUTPUT);
  digitalWrite(MUX_PIN, LOW);

  Serial.println( F("Setting up sensor at default address.") );
  setupIMU(false);
  if ( !imuLow.begin() ) {
    Serial.println( F("Failed to communicate with LSM9DS1.") );
    while (1);
  } else {
    Serial.println( F("Calibrating. Please Wait.") );

    //Initialize temp variables.
    double imux_hold = 0, imuy_hold = 0, imuz_hold = 0;

    //Call the built-in Calibration function. (Mildly effective.)
    imuLow.calibrateMag();

    //Baseline calibration function.
    for (int i = 0; i < CALIBRATION_INDEX ; i++) {
      delay( 25 );
      while ( !imuLow.magAvailable() );
      imuLow.readMag();
      //The sensor's defined C.S. does not coincide with the right hand rule.
      //The RHR is imposed by mapping the sensor's output to a predefined C.S.
      // Our C.S. +X -> Sensor +Z
      // Our C.S. +Y -> Sensor -X
      // Our C.S. +Z -> Sensor +Y
      imux_hold += double( imuLow.calcMag( imuLow.mz ) );
      imuy_hold += double( -1 * imuLow.calcMag( imuLow.mx ) );
      imuz_hold += double( imuLow.calcMag( imuLow.my ) );

      if (i == CALIBRATION_INDEX - 1) {
        cal_imu0_x = imux_hold / double(CALIBRATION_INDEX);
        cal_imu0_y = imuy_hold / double(CALIBRATION_INDEX);
        cal_imu0_z = imuz_hold / double(CALIBRATION_INDEX);
      };
    };
  };

  Serial.println( F("Setting up sensor at the secondary address.") );
  setupIMU(true);
  if ( !imuHigh.begin() ) {
    Serial.println( F("Failed to communicate with LSM9DS1.") );
    while (1);
  } else {
    Serial.println( F("Calibrating. Please Wait.") );

    //Clearing temp variables.
    double imux_hold = 0, imuy_hold = 0, imuz_hold = 0;

    //Call the built-in Calibration function. (Mildly effective.)
    imuHigh.calibrateMag();

    //Baseline calibration function.
    for (int i = 0; i < CALIBRATION_INDEX ; i++) {
      delay( 25 );
      while ( !imuHigh.magAvailable() );
      imuHigh.readMag();
      imux_hold += double( imuHigh.calcMag( imuHigh.mz ) );
      imuy_hold += double( -1 * imuHigh.calcMag( imuHigh.mx ) );
      imuz_hold += double( imuHigh.calcMag( imuHigh.my ) );

      if (i == CALIBRATION_INDEX - 1) {
        cal_imu1_x = imux_hold / double(CALIBRATION_INDEX);
        cal_imu1_y = imuy_hold / double(CALIBRATION_INDEX);
        cal_imu1_z = imuz_hold / double(CALIBRATION_INDEX);
      };
    };
  };

  /**************************************************************
    Iterate across MUX to the next two sensors.
   *************************************************************/

  //Select Sensor Pair at HIGH for the other two sensors
  //Sensors: 3 (HIGH) and 4 (LOW)
  //We're going to call this state 1:
  pinMode(MUX_PIN, OUTPUT);
  digitalWrite(MUX_PIN, HIGH);

  Serial.println( F("Setting up sensor at default address.") );
  setupIMU(false);
  if ( !imuLow.begin() ) {
    Serial.println( F("Failed to communicate with LSM9DS1.") );
    while (1);
  } else {
    Serial.println( F("Calibrating. Please Wait.") );

    //Initialize temp variables.
    double imux_hold = 0, imuy_hold = 0, imuz_hold = 0;

    //Call the built-in Calibration function. (Mildly effective.)
    imuLow.calibrateMag();

    //Baseline calibration function.
    for (int i = 0; i < CALIBRATION_INDEX ; i++) {
      delay( 25 );
      while ( !imuLow.magAvailable() );
      imuLow.readMag();

      imux_hold += double( imuLow.calcMag( imuLow.mz ) );
      imuy_hold += double( -1 * imuLow.calcMag( imuLow.mx ) );
      imuz_hold += double( imuLow.calcMag( imuLow.my ) );

      if (i == CALIBRATION_INDEX - 1) {
        cal_imu0_x = imux_hold / double(CALIBRATION_INDEX);
        cal_imu0_y = imuy_hold / double(CALIBRATION_INDEX);
        cal_imu0_z = imuz_hold / double(CALIBRATION_INDEX);
      };
    };
  };

  Serial.println( F("Setting up sensor at the secondary address.") );
  setupIMU(true);
  if ( !imuHigh.begin() ) {
    Serial.println( F("Failed to communicate with LSM9DS1.") );
    while (1);
  } else {
    Serial.println( F("Calibrating. Please Wait.") );

    //Clearing temp variables.
    double imux_hold = 0, imuy_hold = 0, imuz_hold = 0;

    //Call the built-in Calibration function. (Mildly effective.)
    imuHigh.calibrateMag();

    //Baseline calibration function.
    for (int i = 0; i < CALIBRATION_INDEX ; i++) {
      delay( 25 );
      while ( !imuHigh.magAvailable() );
      imuHigh.readMag();

      imux_hold += double( imuHigh.calcMag( imuHigh.mz ) );
      imuy_hold += double( -1 * imuHigh.calcMag( imuHigh.mx ) );
      imuz_hold += double( imuHigh.calcMag( imuHigh.my ) );

      if (i == CALIBRATION_INDEX - 1) {
        cal_imu1_x = imux_hold / double(CALIBRATION_INDEX);
        cal_imu1_y = imuy_hold / double(CALIBRATION_INDEX);
        cal_imu1_z = imuz_hold / double(CALIBRATION_INDEX);
      };
    };
  };

  //We did it! :)
  Serial.println( F("Success!") );
}

void loop() {
  // Start the timer. We're going to smoothen our output; 20Hz.
  start_time = micros();

  // Initialize IMU print variables.
  double  imux0 = 0,
          imuy0 = 0,
          imuz0 = 0,
          imux1 = 0,
          imuy1 = 0,
          imuz1 = 0;

  // Wait for sensors to become ready.
  while ( !imuHigh.magAvailable() && !imuLow.magAvailable() );

  if ( !state ) {
    //Select Sensor Pair at LOW for the first two sensors.
    //We're going to call this state 0:
    digitalWrite(MUX_PIN, LOW);
    delay (DEBOUNCE);

    //When the state is 0 or false, then the first two sensors are selected by the MUX.
    //We run the print commands w.r.t. them; making room for more output on one line later.

    // Do readings for HIGH and LOW addresses.
    imuLow.readMag();
    imuHigh.readMag();

    // To get our desired output, the built in function calculates the magnitude of the magnetic field,
    // from the voltage reading stored in the object's .mx/.my/.mx data.
    // The baseline reading is then subtracted from that result. Up to 3 decimal places are printed.

    //Sensor 1: HIGH aka default address.
    Serial.print( double(imuHigh.calcMag(imuHigh.mz)) - cal_imu0_x, 3 );
    Serial.print( ", ");
    Serial.print( -1 * double(imuHigh.calcMag(imuHigh.mx)) - cal_imu0_y, 3 );
    Serial.print( ", ");
    Serial.print( double(imuHigh.calcMag(imuHigh.my)) - cal_imu0_z, 3 );
    Serial.print( ", ");

    //Sensor 2: LOW aka secondary address, by grounding the SD0_M pin.
    Serial.print( double(imuLow.calcMag(imuLow.mz)) - cal_imu1_x, 3 );
    Serial.print( ", ");
    Serial.print( -1 * double(imuLow.calcMag(imuLow.mx)) - cal_imu1_y, 3 );
    Serial.print( ", ");
    Serial.print( double(imuLow.calcMag(imuLow.my)) - cal_imu1_z, 3 );
    Serial.print( ", ");

    //Prime the selecting variable to proceed to the next state on loop.
    state = true;

  };

  if ( state ) {
    //Select Sensor Pair at HIGH for the first two sensors.
    //We're going to call this state 1:
    digitalWrite(MUX_PIN, HIGH);
    delay (DEBOUNCE);

    //When the state is 1 or true, then the third and fourth sensors are selected by the MUX.
    //We run the print commands w.r.t. them (to apply the right baseline adjustment.)

    // Do readings for HIGH and LOW addresses.
    imuLow.readMag();
    imuHigh.readMag();

    // To get our desired output, the built in function calculates the magnitude of the magnetic field,
    // from the voltage reading stored in the object's .mx/.my/.mx data.
    // The baseline reading is then subtracted from that result. Up to 3 decimal places are printed.

    //Sensor 3: HIGH aka default address.
    Serial.print( double(imuHigh.calcMag(imuHigh.mz)) - cal_imu2_x, 3 );
    Serial.print( ", ");
    Serial.print( -1 * double(imuHigh.calcMag(imuHigh.mx)) - cal_imu2_y, 3 );
    Serial.print( ", ");
    Serial.print( double(imuHigh.calcMag(imuHigh.my)) - cal_imu2_z, 3 );
    Serial.print( ", ");

    //Sensor 4: LOW aka secondary address, by grounding the SD0_M pin.
    Serial.print( double(imuLow.calcMag(imuLow.mz)) - cal_imu3_x, 3 );
    Serial.print( ", ");
    Serial.print( -1 * double(imuLow.calcMag(imuLow.mx)) - cal_imu3_y, 3 );
    Serial.print( ", ");
    Serial.print( double(imuLow.calcMag(imuLow.my)) - cal_imu3_z, 3 );
    Serial.println();

    //Prime the selecting variable to proceed to the next state on loop.
    state = false;
  };

  //  //Time since this loop began.
  //  loop_time = (micros() - start_time) / 1000;
  //  Serial.print( loop_time, 3 );
  //  Serial.print( ", ");
  //
  //  //Time since the beginning of the program.
  //  Serial.println( millis(), DEC );
}

// =========================    Setup IMU       ========================
void setupIMU(bool address_select) {
  //There's almost certainly an easier/better way to do this.
  //Here we "setup" two instances of the IMU objects.
  //One for each address, since there are two.

  if (address_select) {
    imuHigh.settings.device.commInterface = IMU_MODE_I2C; //
    imuHigh.settings.device.mAddress      = LSM9DS1_M_HIGH;    // Load IMU settings
    imuHigh.settings.device.agAddress     = LSM9DS1_AG_HIGH;   //

    imuHigh.settings.gyro.enabled         = false;        // Disable gyro
    imuHigh.settings.accel.enabled        = false;        // Disable accelerometer
    imuHigh.settings.mag.enabled          = true;         // Enable magnetometer
    imuHigh.settings.temp.enabled         = true;         // Enable temperature sensor

    imuHigh.settings.mag.scale            = 16;           // Set mag scale to +/-12 Gs
    imuHigh.settings.mag.sampleRate       = 7;            // Set sampling rate to 80Hz
    imuHigh.settings.mag.tempCompensationEnable = true;   // Enable temperature compensation (good stuff!)

    imuHigh.settings.mag.XYPerformance    = 3;            // 0 = Low || 1 = Medium || 2 = High || 3 = Ultra-high
    imuHigh.settings.mag.ZPerformance     = 3;            // Ultra-high performance

    imuHigh.settings.mag.lowPowerEnable   = false;        // Disable low power mode
    imuHigh.settings.mag.operatingMode    = 0;            // 0 = Continuous || 1 = Single || 2 = OFF
  }
  else {
    imuLow.settings.device.commInterface = IMU_MODE_I2C; //
    imuLow.settings.device.mAddress      = LSM9DS1_M_LOW;    // Load IMU settings
    imuLow.settings.device.agAddress     = LSM9DS1_AG_LOW;   //

    imuLow.settings.gyro.enabled         = false;        // Disable gyro
    imuLow.settings.accel.enabled        = false;        // Disable accelerometer
    imuLow.settings.mag.enabled          = true;         // Enable magnetometer
    imuLow.settings.temp.enabled         = true;         // Enable temperature sensor

    imuLow.settings.mag.scale            = 16;           // Set mag scale to +/-12 Gs
    imuLow.settings.mag.sampleRate       = 7;            // Set sampling rate to 80Hz
    imuLow.settings.mag.tempCompensationEnable = true;   // Enable temperature compensation (good stuff!)

    imuLow.settings.mag.XYPerformance    = 3;            // 0 = Low || 1 = Medium || 2 = High || 3 = Ultra-high
    imuLow.settings.mag.ZPerformance     = 3;            // Ultra-high performance

    imuLow.settings.mag.lowPowerEnable   = false;        // Disable low power mode
    imuLow.settings.mag.operatingMode    = 0;            // 0 = Continuous || 1 = Single || 2 = OFF
  }
}

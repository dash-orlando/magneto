/*
 * Obtain magnetic field vector using multiplexed LSM9DS1 IMU sensors.
 * Obtained values take into account the magnetic field of the earth,
 * and the immediately surrounding area by taking a baseline average 
 * for each axis and then subtracting each them from the readings to 
 * give a calibrated reading independent of the ambient magnetic field.
 * 
 * AUTHOR                  : Edward Daniel Nichols
 * LAST CONTRIBUTION DATE  : Nov.  6th, 2017, Year of Our Lord
 * 
 * AUTHOR                  : Mohammad Odeh
 * LAST CONTRIBUTION DATE  : Jul. 19th, 2018 Year of Our Lord
 * 
 * CHANGELOG:-
 *  1- Moved over communications to MQTT
 *  2- Store calibration data in EEPROM
 *   (no need to recalibrate on each boot)
 *  3- No need to perform a hard-reset when failing to publish
 */

// Include required libraries
#include <Wire.h>
#include <SPI.h>
#include <SparkFunLSM9DS1.h>

// Useful defines.
#define BAUDRATE              115200                          // Serial communication baudrate

// System parameters
#define NSENS     4                                           // Number of sensors
#define NAXES     3                                           // Number of axes

// Array that will house the smoothed sensor orientation adjusted readings, for printing.
// See the 'sensorOrientation()' definition.
double sens[NSENS][NAXES] = {0};

// Initialize two instances of the LSM object; one for each M_address.
LSM9DS1 high;                                                 // Odd sensors 1 and 3
LSM9DS1 low;                                                  // Even sensors 2 and 4

// Call auxiliary functions library
#include "functions.h"

void setup() {

  Serial.begin( BAUDRATE );                                   // Start serial monitor

  /* MUST load EEPROM before you can write to it */
  EEPROM.begin( EEPROM_SIZE );
  EEPROM_readAnything( 0, calibration );                      // Use this if you don't want to print to serial
  //read_EEPROM(); delay( 1500 );                               // Load EEPROM and display on serial

  /*  Connect to Wi-Fi and setup MQTT communications */
  setup_WiFi();                                               // Connect to WiFi
  MQTT_connect( 250 );                                        // Connecto to MQTT broker

  /* Initialize the necessary MUX selection pins. */
  pinMode( S0, OUTPUT );
  pinMode( S1, OUTPUT );
  pinMode( S2, OUTPUT );
  digitalWrite( S2, LOW );

  for ( uint8_t whichPair = 1; whichPair <= NSENS / 2; whichPair++ )
  {
    pairSelect( whichPair );                                  // Switch between all sensor pairs
    setupIMU();                                               // Setup IMUS

    if ( !high.begin() || !low.begin() )                      // Initialize sensors, and print error code if failure.
    {
      Serial.print( F("Failed to communicate with LSM9DS1 in pair:") );
      Serial.println( whichPair );
      while ( 1 );
    }

    else if ( calibration.Calibrated )
    {
      Serial.print( F("Using calibration offsets from EEPROM\n") );

      for ( uint8_t i = 0; i < NSENS; i++ ) {                 // ...
        for ( uint8_t j = 0; j < NAXES; j++ ) {               // Pull calibration data from EEPROM
          cal[i][j] = calibration.sensors_offsets[i][j];      // ...
          delay( 5 );                                         // Ensure data has been properly stored
        }
      }
    }

    else
    {
      calibrateIMU( whichPair );                              // Run calibration routine to obtain offsets

      // After ALL sensors have been calibrated...
      if ( whichPair == NSENS / 2 )
      {
        for ( uint8_t i = 0; i < NSENS; i++ ) {               // ...
          for ( uint8_t j = 0; j < NAXES; j++) {              // Place calibration values in struct
            calibration.sensors_offsets[i][j] = cal[i][j];    // ...
          }
        }

        Serial.print( F("Writing to EEPROM...") );
        calibration.Calibrated  = true ;                      // Indicate that calibration was performed
        EEPROM.put( 0, calibration );                         // Save data to the EEPROM
        EEPROM.commit();                                      // ...
        Serial.print( F("DONE!\n") );

        delay( 500 );                                         // Ensure data has been saved
      }
    }
  }
}

void loop() {

  if ( !mqtt.connected() )                                    // Ensure we are connected
    MQTT_connect( 250 );                                      // to MQTT server

  for ( uint8_t whichPair = 1; whichPair <= NSENS / 2; whichPair++ )
  {
    pairSelect(whichPair);                                    // Switch between all sensor pairs

    while (!low.magAvailable() && !high.magAvailable() );     // Wait until the sensors are available.

    high.readMag();                                           // Take readings (High sensors)
    low.readMag();                                            // Take readings (Low sensors)

    orientRead( whichPair );                                  // Reorient readings and push to the array
  }

  /* When all of the values have been collected, print them */
  /* all at once, adjusting for the calibration baseline!   */
  char    buff[156] = {'\0'};                                 // String buffer
  strcat( buff, "<" );                                        // SOH indicator
  for (uint8_t i = 0; i < NSENS; i++) {
    for (uint8_t j = 0; j < NAXES; j++) {
      dtostrf( sens[i][j] - cal[i][j], 9, 6, &buff[strlen(buff)]);
      if (i == NSENS - 1 && j == NAXES - 1)
        continue;
      else
        strcat( buff, "," );
    }
  } strcat( buff, ">" );                                        // EOT indicator

  if ( devOutput.publish( buff ) )                              // Make sure it publishes
    Serial.println( buff );                                     // ...
  else                                                          // In case it fails, disconnect from MQTT Server
    mqtt.disconnect();                                          // ...

  delay( 25 );
}

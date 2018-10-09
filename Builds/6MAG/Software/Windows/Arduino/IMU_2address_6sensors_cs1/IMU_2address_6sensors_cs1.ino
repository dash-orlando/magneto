/*
   Obtain magnetic field vector using multiplexed LSM9DS1 IMU sensors.
   Obtained values take into account the magnetic field of the earth,
   and the immediately surrounding area by taking a baseline average for each axis
   and then subtracting each them from the readings to give a calibrated reading
   independent of the ambient magnetic field.

   AUTHOR                  : Edward Daniel Nichols
   LAST CONTRIBUTION DATE  : Nov. 6th, 2017, Year of Our Lord

   AUTHOR                  : Mohammad Odeh
   LAST CONTRIBUTION DATE  : Nov. 7th, 2017 Year of Our Lord

   CHANGELOG:-
    1- Both possible addresses for the IMUs are implemented.
    2- Calibration speed has significantly improved.
    3- All six sensors have been added.
    4- Implemented an EMA filter for smoothing data output.

    There is room to add more sensors.
*/

// Include required libraries
#include <Wire.h>
#include <SPI.h>
#include "SparkFunLSM9DS1.h"

// Define sensor address, for the setup.
#define LSM9DS1_M_HIGH                0x1E    // SDO_M on these IMU's are HIGH
#define LSM9DS1_AG_HIGH               0x6B    // SDO_AG on these IMU's are HIGH 
#define LSM9DS1_M_LOW                 0x1C    // SDO_M on these IMU's are LOW
#define LSM9DS1_AG_LOW                0x6B    // SDO_AG on these IMU's are HIGH [PINS NOT GROUNDED]***

// Useful defines.
#define CALIBRATION_INDEX             150     // Accounting for ambient magnetic fields
#define DECLINATION                   6.29    // Accounting for the Earth's magnetic field
#define BAUDRATE                      115200  // Serial communication baudrate
#define MUX_PIN                       10      // Multiplexer "Select pin"
#define DEBOUNCE                      1       // To ensure select pin voltage has enough time to settle.

// MUX lines are on these pins.
#define S0                            7
#define S1                            6
#define S2                            5
// S2 is grounded.
// MUX lines are selected in binary.
// For example, Y0 -> S0=LOW, S1=LOW, S2=LOW -> 000.

// Sensor Calibration variables: To store the averaged baseline values for each sensor.
double cal[6][3] = {0};

// Array that will house the smoothed sensor orientation adjusted readings, for printing.
// See the 'sensorOrientation()' definition.
double sens[6][3] = {0};

// Initialize two instances of the LSM object; one for each M_address.
LSM9DS1 high; //Odd sensors 1, 3, and 5
LSM9DS1 low;  //Even sensors 2, 4, and 6

// Call auxiliary functions library
#include "functions.h"

void setup() {
  // Start serial monitor.
  Serial.begin( BAUDRATE );

  // Initialize the necessary MUX selection pins.
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  digitalWrite(S2, LOW);

  for (int whichPair = 1; whichPair <= 3; whichPair++) {

    pairSelect(whichPair);    // Switch between all sensor pairs
    setupIMU();               // Setup IMUS

    //Initialize the sensors, and print error code if failure.
    if ( !high.begin() || !low.begin() ) {
      Serial.print( F("Failed to communicate with LSM9DS1 in pair:") );
      Serial.println(whichPair);
      while (1);
    } else {

      Serial.println( F("Calibrating, please wait.") );
      delay(25);
      //Calibration function:
      double hold[6] = {0};
      for (int i = 0; i < CALIBRATION_INDEX; i++) {

        //Declaring an index, to make it easier to assign values to/from the correct sensor.
        int n_hi = (whichPair - 1) * 2;
        int n_lo = (2 * whichPair) - 1;

        //Wait until sensors are available.
        delay(10);
        while ( !low.magAvailable() && !high.magAvailable() );

        high.readMag();                 // Take readings (High sensors)
        low.readMag();                  // Take readings (Low sensors)

        orientRead(whichPair);          //Reorient readings and push to the array

        hold[0] += sens[n_hi][0];       // Populate temporary hold array
        hold[1] += sens[n_hi][1];       // for the HIGH sensors.
        hold[2] += sens[n_hi][2];       // ...

        hold[3] += sens[n_lo][0];       // Populate temporary hold array
        hold[4] += sens[n_lo][1];       // for the LOW sensors.
        hold[5] += sens[n_lo][2];       // ...

        if ( i == CALIBRATION_INDEX - 1) {
          cal[n_hi][0] = hold[0] / CALIBRATION_INDEX;   // Compute the calibration (BASE)
          cal[n_hi][1] = hold[1] / CALIBRATION_INDEX;   // values for the High sensors
          cal[n_hi][2] = hold[2] / CALIBRATION_INDEX;   // ...

          //Computing, finally, the actual calibration value for the Low sensor.
          cal[n_lo][0] = hold[3] / CALIBRATION_INDEX;   // Compute the calibration (BASE)
          cal[n_lo][1] = hold[4] / CALIBRATION_INDEX;   // values for the Low sensors
          cal[n_lo][2] = hold[5] / CALIBRATION_INDEX;   // ...

        };
      };

      Serial.print( F("Calibration success for pair: ") );
      Serial.println(whichPair);
    };
  };
};

void loop() {
  Serial.print("<");          // Start of data specifier

  for (int whichPair = 1; whichPair <= 3; whichPair++) {
    pairSelect(whichPair);    // Switch between all sensor pairs

    //Wait until the sensors are available.
    while (!low.magAvailable() && !high.magAvailable() );

    high.readMag();           // Take readings (High sensors)
    low.readMag();            // Take readings (Low sensors)

    orientRead(whichPair);    //Reorient readings and push to the array
  }

  //When all of the values have been collected, print them all at once!
  //Adjusting for the calibration baseline!
  for (int i = 0; i < 6; i++) {
    for (int j = 0; j < 3; j++) {
      Serial.print(sens[i][j] - cal[i][j], 5);
      //delay(2);
      if (i == 5 && j == 2) {
        //Serial.println();
        continue;
      } else {
        Serial.print(", ");
      };
    };
  };

  Serial.println(">");
};

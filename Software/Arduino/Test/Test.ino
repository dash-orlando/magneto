#include <Wire.h>
#include <SPI.h>
#include <SparkFunLSM9DS1.h>

// Define sensor address, for the setup.
#define LSM9DS1_M_HIGH                0x1E              // SDO_M on these IMU's are HIGH
#define LSM9DS1_AG_HIGH               0x6B              // SDO_AG on these IMU's are HIGH 
#define LSM9DS1_M_LOW                 0x1C              // SDO_M on these IMU's are LOW
#define LSM9DS1_AG_LOW                0x6B              // SDO_AG on these IMU's are HIGH [PINS NOT GROUNDED]***

// Useful defines.
#define CALIBRATION_INDEX             150               // Accounting for ambient magnetic fields
#define DECLINATION                   6.29              // Accounting for the Earth's magnetic field
#define BAUDRATE                      115200            // Serial communication baudrate
#define MUX_PIN                       10                // Multiplexer "Select pin"
#define DEBOUNCE                      1                 // To ensure select pin voltage has enough time to settle.

// MUX lines are on these pins.
#define S0                            33
#define S1                            27
#define S2                            12

LSM9DS1 high;                                           //Odd sensors 1 and 3
LSM9DS1 low;                                            //Even sensors 2 and 4

void setup() {
  Serial.begin(115200);
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);

  digitalWrite(S0, LOW);
  digitalWrite(S1, LOW);
  digitalWrite(S2, LOW);

  if ( !high.begin() || !low.begin() )
  {
    Serial.print( F("Failed to communicate with LSM9DS1 in pair:") );
    while (1);
  }
}

void loop() {
  //Wait until sensors are available.
  delay(10);
  while ( !low.magAvailable() && !high.magAvailable() );

  high.readMag();                                 // Take readings (High sensors)
  low.readMag();                                  // Take readings (Low sensors)

  Serial.print( double( high.calcMag(high.mx) ) ); Serial.print(",");
  Serial.print( double( high.calcMag(high.my) ) ); Serial.print(",");
  Serial.print( double( high.calcMag(high.mz) ) ); Serial.print(",");

  Serial.print( double( high.calcMag(low.mx) ) ); Serial.print(",");
  Serial.print( double( high.calcMag(low.my) ) ); Serial.print(",");
  Serial.print( double( high.calcMag(low.mz) ) ); Serial.println();
}

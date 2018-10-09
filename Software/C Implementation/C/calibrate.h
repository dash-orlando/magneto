/*
 * Calibrate sensors to attenuate ambient magnetic field readings
 * 
 * Readings are done for CALIBRATION_INDEX number of times and
 * the averaged. The resultant offsets are then subtracted from
 * the RAW readings.
 */

#include <wiringPi.h>

#define CALIBRATION_INDEX             150                     // Accounting for ambient magnetic fields
#define DECLINATION                   6.29                    // Accounting for the Earth's magnetic field

// Sensor Calibration variables: To store the averaged baseline values for each sensor.
double cal[NSENS][NAXES] = {0};


// ========================  Calibrate  Sensors  =======================
void calibrateIMU( uint8_t whichPair )
{
  printf( "Calibrating, please wait.\n" );
  delay( 25 );

  //Calibration function:
  double hold[6] = {0};
  for ( uint8_t i = 0; i < CALIBRATION_INDEX; i++ )
  {
    //Declaring an index, to make it easier to assign values to/from the correct sensor.
    uint8_t n_hi = (whichPair - 1) * 2;
    uint8_t n_lo = (2 * whichPair) - 1;

    //Wait until sensors are available.
    delay( 10 );
    while ( !imuLO.magAvailable() && !imuHI.magAvailable() );

    imuHI.readMag();                                           // Take readings (High sensors)
    imuLO.readMag();                                            // Take readings (Low sensors)

    orientRead( whichPair );                                  // Reorient readings and push to the array

    hold[0] += sens[n_hi][0];                                 // Populate temporary hold array
    hold[1] += sens[n_hi][1];                                 // for the HIGH sensors.
    hold[2] += sens[n_hi][2];                                 // ...

    hold[3] += sens[n_lo][0];                                 // Populate temporary hold array
    hold[4] += sens[n_lo][1];                                 // for the LOW sensors.
    hold[5] += sens[n_lo][2];                                 // ...

    if ( i == CALIBRATION_INDEX - 1 )
    {
      cal[n_hi][0] = hold[0] / CALIBRATION_INDEX;             // Compute the calibration (BASE)
      cal[n_hi][1] = hold[1] / CALIBRATION_INDEX;             // values for the High sensors
      cal[n_hi][2] = hold[2] / CALIBRATION_INDEX;             // ...

      //Computing, finally, the actual calibration value for the Low sensor.
      cal[n_lo][0] = hold[3] / CALIBRATION_INDEX;             // Compute the calibration (BASE)
      cal[n_lo][1] = hold[4] / CALIBRATION_INDEX;             // values for the Low sensors
      cal[n_lo][2] = hold[5] / CALIBRATION_INDEX;             // ...
    }
  }

  printf( "Calibration success for pair: %i\n", whichPair );
}

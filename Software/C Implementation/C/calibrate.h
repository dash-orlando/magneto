/*
 * Calibrate sensors to attenuate ambient magnetic field readings
 * 
 * Readings are done for CALIBRATION_INDEX number of times and
 * the averaged. The resultant offsets are then subtracted from
 * the RAW readings.
 */

#include <wiringPi.h>

#define CALIBRATION_INDEX         	150                     					// Accounting for ambient magnetic fields
#define DECLINATION                	6.29                    					// Accounting for the Earth's magnetic field

// Sensor Calibration variables: To store the averaged baseline values for each sensor.
double cal[NSENS][NAXES] = {0};


// ========================  Calibrate  Sensors  =======================
void calibrateIMU( uint8_t whichPair )
{
  printf( "Calibrating, please wait.\n" );
  delay( 25 );

  double hold[6] = {0};
  for( uint8_t i = 0; i < CALIBRATION_INDEX; i++ )
  {
    //Declaring an index, to make it easier to assign values to/from the correct sensor.
    uint8_t n_HI = (whichPair - 1) * 2; 										// Define index for HI sensors
    uint8_t n_LO = (2 * whichPair) - 1; 										// Define index for LO sensors

    while( !imuLO.magAvailable() && !imuHI.magAvailable() );					// Wait until the sensors are available.
    imuHI.readMag(); imuLO.readMag(); 											// Take readings

    orientRead( whichPair );                                  					// Reorient readings and push to the array
	
    hold[0] += sens[n_HI][0];                                 					// Populate temporary hold array
    hold[1] += sens[n_HI][1];                                 					// for the HIGH sensors.
    hold[2] += sens[n_HI][2];                                 					// ...

    hold[3] += sens[n_LO][0];                                 					// Populate temporary hold array
    hold[4] += sens[n_LO][1];                                 					// for the LOW sensors.
    hold[5] += sens[n_LO][2];                                 					// ...

    if( i == CALIBRATION_INDEX - 1 ) 											// Average the readings
    {
      cal[n_HI][0] = hold[0] / CALIBRATION_INDEX;             					// Compute the calibration (BASE)
      cal[n_HI][1] = hold[1] / CALIBRATION_INDEX;             					// values for the High sensors
      cal[n_HI][2] = hold[2] / CALIBRATION_INDEX;             					// ...

      //Computing, finally, the actual calibration value for the Low sensor.
      cal[n_LO][0] = hold[3] / CALIBRATION_INDEX;             					// Compute the calibration (BASE)
      cal[n_LO][1] = hold[4] / CALIBRATION_INDEX;             					// values for the Low sensors
      cal[n_LO][2] = hold[5] / CALIBRATION_INDEX;             					// ...
    }
  }

  printf( "Calibration success for pair: %i\n", whichPair );
}

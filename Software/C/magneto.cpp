#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <sys/time.h>
#include <unistd.h>
#include "LSM9DS1_Types.h"
#include "LSM9DS1.h"
#include <wiringPi.h>

// System parameters
#define NSENS     2                                           // Number of sensors
#define NAXES     3                                           // Number of axes

#define LSM9DS1_M_HIGH                0x1E                    // SDO_M on these IMU's are HIGH
#define LSM9DS1_AG_HIGH               0x6B                    // SDO_AG on these IMU's are HIGH 
#define LSM9DS1_M_LOW                 0x1C                    // SDO_M on these IMU's are LOW
#define LSM9DS1_AG_LOW                0x6B                    // SDO_AG on these IMU's are HIGH [PINS NOT GROUNDED]***

// Array that will house the smoothed sensor orientation adjusted readings, for printing.
// See the 'sensorOrientation()' definition.
double sens[NSENS][NAXES] = {0};

// Initialize two instances of the LSM object; one for each M_address.
//~ LSM9DS1 imuHI( IMU_MODE_I2C, LSM9DS1_AG_HIGH, LSM9DS1_M_HIGH );	// Odd sensors 1 and 3
//~ LSM9DS1 imuLO( IMU_MODE_I2C, LSM9DS1_AG_LOW , LSM9DS1_M_LOW  );	// Even sensors 2 and 4
LSM9DS1 imuHI;	// Odd sensors 1 and 3
LSM9DS1 imuLO;

// Call auxiliary functions library
#include "functions.h"


int main(int argc, char *argv[])
{
	if( wiringPiSetupGpio() == -1 )
    {
		return 0;
	} 
	//~ LSM9DS1 imu( IMU_MODE_I2C, LSM9DS1_AG_HIGH, LSM9DS1_M_HIGH );
    
    for( uint8_t i = 1; i <= NSENS/2; i++ )
    {
		pairSelect( i );
		setupIMU();
		
		if ( !imuHI.begin() || !imuLO.begin() )
		{
			fprintf( stderr, "Failed to communicate with LSM9DS1 pair %i.\n", i );
			printf( "!imuHI.begin() %i\n", !imuHI.begin() );
			printf( "!imuLO.begin() %i\n", !imuLO.begin() );
			exit( EXIT_FAILURE );
		} calibrateIMU( i );
	}
    
	// Infinite loop after setup is complete
    for ( ;; )
    {
		// Collect data
		for( uint8_t i = 1; i <= NSENS/2; i++ )
		{
			pairSelect( i );
			
			while( !imuHI.magAvailable() && !imuLO.magAvailable() ) ; 	// Wait until the sensors are available.
			imuHI.readMag(); imuLO.readMag(); 							// Take readings
			
			orientRead( i );                                  			// Reorient readings and push to the array
		}
		
		// Print data
		char    buff[156] = {'\0'};                                 	// String buffer
		char 	temp[ 9 ] = {'\0'};
		strcat( buff, "<" );                                        	// SOH indicator
		for (uint8_t i = 0; i < NSENS; i++)
		{
			for (uint8_t j = 0; j < NAXES; j++)
			{
				if( sens[i][j] - cal[i][j] >= 0 )
				{
					snprintf( temp, 7+1, "%.5lf", sens[i][j] - cal[i][j] );
				}
				else
				{
					snprintf( temp, 8+1, "%.5lf", sens[i][j] - cal[i][j] );
				}
				strcat( buff, temp );
				
				if (i == NSENS - 1 && j == NAXES - 1)
					continue;
				else
					strcat( buff, "," );
			}
		}
		strcat( buff, ">" );
		printf( "%s\n", buff );
    } exit(EXIT_SUCCESS);
}

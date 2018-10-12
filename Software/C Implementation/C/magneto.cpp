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
#define NSENS     					4                                       	// Number of sensors
#define NAXES     					3                                       	// Number of axes

#define LSM9DS1_M_HIGH             	0x1E                    					// SDO_M on these IMU's are HIGH
#define LSM9DS1_AG_HIGH            	0x6B                    					// SDO_AG on these IMU's are HIGH 
#define LSM9DS1_M_LOW             	0x1C                    					// SDO_M on these IMU's are LOW
#define LSM9DS1_AG_LOW            	0x6B                    					// SDO_AG on these IMU's are HIGH [PINS NOT GROUNDED]***

// Create two instances of the LSM object; one for each M_address.
LSM9DS1 imuHI( IMU_MODE_I2C, LSM9DS1_AG_HIGH, LSM9DS1_M_HIGH );					// Odd  sensors
LSM9DS1 imuLO( IMU_MODE_I2C, LSM9DS1_AG_LOW , LSM9DS1_M_LOW  );					// Even sensors

// Call auxiliary functions library
#include "functions.h"


int main(int argc, char *argv[])
{
	if( wiringPiSetupGpio() == -1 ) 											// Start the wiringPi library
    {
		return 0;
	} 
    
    for( uint8_t i = 1; i <= NSENS/2; i++ )
    {
		pairSelect( i );
		setupIMU(); 															// Setup sampling rate, scale, etc...
		
		if ( !imuHI.begin() || !imuLO.begin() ) 								// Initialize sensors
		{
			fprintf( stderr, "Failed to communicate with LSM9DS1 pair %i.\n", i );
			printf( "!imuHI.begin() %i\n", !imuHI.begin() );
			printf( "!imuLO.begin() %i\n", !imuLO.begin() );
			exit( EXIT_FAILURE );
		} calibrateIMU( i ); 													// Perform user-defined calibration routine
	}
    
	// Infinite loop after setup is complete
    for ( ;; )
    {
		// Collect data
		for( uint8_t i = 1; i <= NSENS/2; i++ )
		{
			pairSelect( i ); 													// Switch between pairs
			
			while( !imuHI.magAvailable() && !imuLO.magAvailable() ) ; 			// Wait until the sensors are available.
			imuHI.readMag(); imuLO.readMag(); 									// Take readings
			
			orientRead( i );                                  					// Reorient readings and push to the array
		}
		
		// Print data
		char    buff[156] = {'\0'};                                 			// String buffer
		strcat( buff, "<" );                                        			// SOH indicator
		for (uint8_t i = 0; i < NSENS; i++) 									// Loop over sensors
		{																		// ...
			for (uint8_t j = 0; j < NAXES; j++) 								//	Loop over axes
			{																	// 	...
				char 	temp[ 9 ] = {'\0'};										// 	Array to hold calibrated readings
				if( sens[i][j] - cal[i][j] >= 0 ) 								// 	Formatting in case of positive reading
				{
					snprintf( temp, 7+1, "%.5lf", sens[i][j] - cal[i][j] );
				}
				else 															// 	Formatting in case of negative reading
				{
					snprintf( temp, 8+1, "%.5lf", sens[i][j] - cal[i][j] );
				}
				strcat( buff, temp ); 											// 	Append calibrated array to output buffer
				
				if (i == NSENS - 1 && j == NAXES - 1)
					continue;
				else
					strcat( buff, "," ); 										// 	Add delimiter
			}
		}
		strcat( buff, ">" );                                        			// SOH indicator
		printf( "%s\n", buff );                                        			// Print final OUTPUT string
    } exit(EXIT_SUCCESS);
}

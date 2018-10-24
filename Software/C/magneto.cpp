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

#include <math.h>
#include <float.h>

#include "levmar.h"

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

double CAL[NSENS][NAXES] 	= {0}; 												// CALIBRATED (RAW - BASE) readings
double norm[ NSENS ] 		= {0}; 												// L2-norm

// Call auxiliary functions library
#include "functions.h"


int main( int argc, char *argv[] )
{
	if( wiringPiSetupGpio() == -1 ) 											// Start the wiringPi library
    {
		return 0;
	} 
    
    pinMode( S0, OUTPUT ); 														// Set select pins as output
	pinMode( S1, OUTPUT ); 														// ...
	pinMode( S2, OUTPUT ); 														// ...
    
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
    
    // Setup solver
    opts[0]=LM_INIT_MU; opts[1]=1E-15; opts[2]=1E-15; opts[3]=1E-20;
	opts[4]= LM_DIFF_DELTA; // relevant only if the Jacobian is approximated using finite differences; specifies forward differencing
	//opts[4]=-LM_DIFF_DELTA; // specifies central differencing to approximate Jacobian; more accurate but more expensive to compute!
	
	// Infinite loop after setup is complete
    for( ;; )
    {
		// Collect data
		for( uint8_t i = 1; i <= NSENS/2; i++ )
		{
			pairSelect( i ); 													// Switch between pairs
			
			while( !imuHI.magAvailable() && !imuLO.magAvailable() ) ; 			// Wait until the sensors are available.
			imuHI.readMag(); imuLO.readMag(); 									// Take readings
			
			orientRead( i );                                  					// Reorient readings and push to the array
		}
		
		// Compute CALIBRATED readings + norm
		memset( norm, 0.0, NSENS*sizeof(norm) );								// Reset norms array
		for( uint8_t i = 0; i < NSENS; i++ ) 									// Loop over sensors
		{																		// ...
			for( uint8_t j = 0; j < NAXES; j++ ) 								//	Loop over axes
			{																	// 	...
				CAL[i][j] = RAW[i][j] - BASE[i][j]; 							// 	Store CALIBRATED readings
				norm[ i ] += CAL[i][j] * CAL[i][j]; 							// 	Compute norm (1/2)
				
				#ifdef DEBUG
					print_mag( CAL[i][j], i, j ); 								// Construct & print mag field array data
				#endif
			}
			norm[ i ] = sqrt( norm[i] ); 										// 	Compute norm (2/2)
		}
		
		// Run the LMA to estimate the position of the magnet
		ret=dlevmar_dif(system_of_eqns, init_guess, sensor_eqn, m, n, 1000, opts, info, NULL, NULL, NULL);  // no Jacobian
		
		#ifdef DEBUG
			print_lm_verbose();
		#else
			// Note to self: figure out why developers don't care for/use init_guess[0]
			// What is in init_guess[0]?
			for( uint8_t i = 0; i < m; ++i )
			{
				printf( "%.7g ", init_guess[i]*1000 );
			} 	printf( "\n" );
		#endif
		
    } exit(EXIT_SUCCESS);
}

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

// Lev-Mar required libraries
#include <math.h>
#include <float.h>
#include "levmar.h"

// Uncomment for debugging
#define DEBUG						0											// Verbose output
/*
 * DEBUG							0											NO DEBUG
 * "								1											Verbose Output ALL
 * "								2											--
 * "								3											--
 * "								4											--
 * "								5											Verbose Output for the END EFFECTOR Function
 */

// System parameters
#define NSENS     					6                                       	// Number of sensors
#define NAXES     					3                                       	// Number of axes
#define X_LIM 						500 										// Boundary limits
#define Y_LIM 						500 										// Boundary limits
#define Z_LIM 						500 										// Boundary limits

#define LSM9DS1_M_HIGH             	0x1E                    					// SDO_M on these IMU's are HIGH
#define LSM9DS1_AG_HIGH            	0x6B                    					// SDO_AG on these IMU's are HIGH 
#define LSM9DS1_M_LOW             	0x1C                    					// SDO_M on these IMU's are LOW
#define LSM9DS1_AG_LOW            	0x6B                    					// SDO_AG on these IMU's are HIGH [PINS NOT GROUNDED]***

// Create two instances of the LSM object; one for each M_address.
LSM9DS1 imuHI( IMU_MODE_I2C, LSM9DS1_AG_HIGH, LSM9DS1_M_HIGH );					// Odd  sensors
LSM9DS1 imuLO( IMU_MODE_I2C, LSM9DS1_AG_LOW , LSM9DS1_M_LOW  );					// Even sensors

double CAL[NSENS][NAXES] 	= {0}; 												// CALIBRATED (RAW - BASE) readings
double norm[ NSENS ] 		= {0}; 												// L2-norm
uint8_t ndx[ NAXES ] 		= {0};												// Store the index of the 3 sensors with the higest norms

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
	
	find_max_norm( norm, NSENS, ndx );											// Find sorted indices of sensors with maximum norms
	find_init_guess( init_guess, NAXES, XYZ, ndx ); 							// Find initial guess
	
	// Create logfile
	FILE *logfile = fopen( "output.txt", "w" ); 								// Open file for writing
	if( logfile == NULL )
	{
		printf( "ERROR! Could not open file\n" );
		exit( -1 );
	}
    
	// Setup solver
	opts[0]=LM_INIT_MU; opts[1]=1E-15; opts[2]=1E-15; opts[3]=1E-20;
	opts[4]= LM_DIFF_DELTA; // relevant only if the Jacobian is approximated using finite differences; specifies forward differencing
	//opts[4]=-LM_DIFF_DELTA; // specifies central differencing to approximate Jacobian; more accurate but more expensive to compute!

// ---------------------------------------------------------------------------------------------
// --------------------------------- INFINITE LOOP STARTS HERE ---------------------------------
// ---------------------------------------------------------------------------------------------

	// Infinite loop after setup is complete
	for( ;; )
	{
		unsigned int t = millis();
		// Collect data
		for( uint8_t i = 1; i <= NSENS/2; i++ )
		{
			pairSelect( i ); 													// Switch between pairs
			
			while( !imuHI.magAvailable() && !imuLO.magAvailable() ) ; 			// Wait until the sensors are available.
			imuHI.readMag(); imuLO.readMag(); 									// Take readings
			
			orientRead( i );                                  					// Reorient readings and push to the array
		}
		
		// Compute CALIBRATED readings + norm
		#ifdef DEBUG															// IF DEBUG
			char 	buff[39*NSENS] = {'\0'};									// 		String buffer
			strcat( buff, "<" );
		#endif
		
		for( uint8_t i = 0; i < NSENS; i++ ) norm[i] = 0;						// Reset norms array
		for( uint8_t i = 0; i < NSENS; i++ ) 									// Loop over sensors
		{																		// ...
			for( uint8_t j = 0; j < NAXES; j++ ) 								//	Loop over axes
			{																	// 	...
				CAL[i][j] = RAW[i][j] - BASE[i][j]; 							// 	Store CALIBRATED readings
				norm[ i ] += CAL[i][j] * CAL[i][j]; 							// 	Compute norm (1/2)
				
				if( DEBUG == 1 ) print_mag( buff, CAL[i][j], i, j ); 			//  Construct & print mag field array data
				
			}
			norm[ i ] = sqrt( norm[i] ); 										// Compute norm (2/2)
		} 	find_max_norm( norm, NSENS, ndx );									// Find sorted indices of sensors with maximum norms
		
		// Run the LMA to estimate the position of the magnet
		ret=dlevmar_dif(system_of_eqns, init_guess, sensor_eqn, m, n, 1000, opts, info, NULL, NULL, NULL);  // no Jacobian
		
		unsigned int end_time = millis() - t;
		
		// Bound solution to a predetermined volume and Printing Results
		if( fabs(init_guess[0]*1e3) > X_LIM || fabs(init_guess[0]*1e3) > X_LIM || fabs(init_guess[0]*1e3) > X_LIM )
		{
			find_max_norm( norm, NSENS, ndx );									// Find sorted indices of sensors with maximum norms
			find_init_guess( init_guess, NAXES, XYZ, ndx ); 					// Find initial guess
			printf( "Out of bounds. Finding initial guess.\n" );
		}
		else
		{
			if( DEBUG == 1 )
			{
				print_lm_verbose();
			}
			else if( DEBUG == 0 )
			{
				// Printing output
				//printf( " MAGNET POSITION ---------------------------- \n" );
				for( uint8_t i = 0; i < m; ++i )
				{
					printf( " pm[%i] = %.3lf ", i, init_guess[i]*1000 ); 				// Write magnet position to stdout
					fprintf( logfile, "pm[%i] = %.3lf ", i, init_guess[i]*1000 );		// Write to file
					
					init_guess[i] =+ dx;
				} 	printf( " t = %i\n", end_time ); fprintf( logfile, " t = %i\n", end_time );
			}
		}
		
		// End Effector Calculation ------------------------------------------- //
		// 		Approximation of the LOCAR end-effector
		end_effector(init_guess, end_effector_pos);
		
		
		
	} exit(EXIT_SUCCESS);
}

/*
 * Construct and eventually print the CALIBRATED magnetic field array
 * in case we want or need them.
 *
 * INPUTS:-
 * 		- double mag_field: CALIBRATED magnetic field readings
 * 		- uint8_t SENS_NDX: The 'i', or senseors', counter. 	\ Both of theses guys are used to determine the
 * 		- uint8_t AXES_NDX: The 'j', or axes', counter. 		/ end of the char array and when to print.
 *
 * OUTPUT:-
 * 		- NONE
 */
#include <stdio.h>

void print_mag( char* char_buff, double mag_field, uint8_t SENS_NDX, uint8_t AXES_NDX )
{	
	char temp[ 9 ] = {'\0'};													// Array to hold CALIBRATED readings
	if( mag_field >= 0 ) snprintf( temp, 7+1, "%.5lf", mag_field );				// Formatting in case of positive reading
	else 				 snprintf( temp, 8+1, "%.5lf", mag_field );				// Formatting in case of negative reading

	strcat( char_buff, temp ); 													// Append CALIBRATED array to output buffer
	
	if( SENS_NDX == NSENS - 1 && AXES_NDX == NAXES - 1 )
	{
		strcat( char_buff, ">" );                                        		// SOH indicator
		printf( "%s\n", char_buff );                                        	// Print final OUTPUT string
	}
	else
	{
		strcat( char_buff, "," ); 												// Add delimiter
	}
}

// -----------------------------------------------------------------------------

void print_lm_verbose( void )
{	
	printf( "Results:-\n" );
	
	printf( "Levenberg-Marquardt returned %d in %g iter, reason %g\nSolution: ", ret, info[5], info[6] );
	for( uint8_t i = 0; i < m; ++i )
	{
		printf( "%.7g ", init_guess[i]*1000 );
	}
	
	printf( "\n\nMinimization info:-\n" );
	for( uint8_t i = 0; i < LM_INFO_SZ; ++i )
	{
		printf( "%g ", info[i] );
	} 	printf( "\n" );
}

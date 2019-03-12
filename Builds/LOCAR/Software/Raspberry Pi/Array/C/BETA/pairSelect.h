/*
 * Switches between all the available sensors using the multiplexer
 */

#include <wiringPi.h>

#define DEBOUNCE                      1                       // To ensure select pin voltage has enough time to settle.

// MUX lines are on these pins.
#define S0                            22
#define S1                            23
#define S2                            24

// MUX lines are selected in binary.
// For example, Y0 -> S0=LOW, S1=LOW, S2=LOW -> 000.

// =======================    Select IMU pair       ====================
void pairSelect( uint8_t pair )
{
	if (pair == 1)
	{
		//s.t. the selection lines hit Y0, at 000
		digitalWrite( S0, LOW );
		digitalWrite( S1, LOW );
		digitalWrite( S2, LOW );
	} 
	
	else if ( pair == 2 )
	{
		//s.t. the selection lines hit Y1, at 001
		digitalWrite( S0, HIGH );
		digitalWrite( S1, LOW  );
		digitalWrite( S2, LOW );
	} 
	
	else if ( pair == 3 )
	{
		//s.t. the selection lines hit Y2, at 010
		digitalWrite( S0, LOW  );
		digitalWrite( S1, HIGH );
		digitalWrite( S2, LOW );
	} 
	
	else 
	{
		printf( "Error. This sensor pair doesn't exist!\n" );
		while (1);
	}
	delay( DEBOUNCE );
}

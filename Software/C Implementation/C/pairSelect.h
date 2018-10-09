/*
 * Switches between all the available sensors using the multiplexer
 */

#include <wiringPi.h>

#define DEBOUNCE                      1                       // To ensure select pin voltage has enough time to settle.

// MUX lines are on these pins.
#define S0                            17
#define S1                            27
#define S2                            22
// S2 is grounded.
// MUX lines are selected in binary.
// For example, Y0 -> S0=LOW, S1=LOW, S2=LOW -> 000.

// =======================    Select IMU pair       ====================
void pairSelect( int desiredPair )
{
  int pair = desiredPair;
  if (pair == 1) {
    //s.t. the selection lines hit Y0, at 000
    digitalWrite( S0, LOW );
    digitalWrite( S1, LOW );
    delay( DEBOUNCE );
  } else if ( pair == 2 ) {
    //s.t. the selection lines hit Y1, at 001
    digitalWrite( S0, HIGH );
    digitalWrite( S1, LOW  );
    delay( DEBOUNCE );
  } else if ( pair == 3 ) {
    //s.t. the selection lines hit Y1, at 010
    digitalWrite( S0, LOW  );
    digitalWrite( S1, HIGH );
    delay( DEBOUNCE );
  } else {
    printf( "Error. This sensor pair doesn't exist!\n" );
    while (1);
  }
};

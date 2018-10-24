/*
 * Construct LHS of equations for use with the LMA solver.
 * Recall, in order to solve a system numerically it
 * must have the form of,
 *
 *        if    >$\  LHS = f(x, y, z, ...) = g(x, y, z, ...) = RHS
 *        then  >$\  f(x, y, z, ...) - g(x, y, z, ...) = LHS - RHS = 0
 *
 * INPUTS:-
 * 		- double *init_guess	: Initial guess. On output contains estimated solution
 * 		- double *sensor_eqn	: Measurement vector. NULL implies a zero vector
 * 		- int m 				: Number of unkowns
 * 		- int n 				: Measurement vector dimension (number of equations?)
 * 		- void *data			: Pointer to possibly needed additional data, passed uninterpreted to func.
 * 									* Set to NULL if not needed
 *
 * OUTPUT:-
 * 		- NONE. Solution is stored in the init_guess array upon convergence.
 */
#include <math.h>
#include <float.h>
#include "levmar.h"

#define K 			1.09e-6 				// Big Ol' Magnet's constant (K) || Units { G^2.m^6}

int		ret; 								// LM return (return value is stored here for debugging)
int 	m = NAXES, n = NSENS; 				// Number of unknowns, number of equations
double 	init_guess[m] = {0}, 				// Initial guess. 5 is max(2, 3, 5)
		sensor_eqn[n] = {0}; 				// Equations array. 16 is max(2, 3, 5, 6, 16)
double 	opts[LM_OPTS_SZ],
		info[LM_INFO_SZ];

/*
# Define the position of the sensors on the grid
# relative to the origin, i.e:
#
#       +y  ^
#           |         o SEN3 <-(X3, Y3, Z3)
#           |
#           |                       ____ (X2, Y2, Z2)
#           |                      /
#           |                     V
#   ORIGIN, O----------------- o SEN2 --> +x
#  (0, 0, 0)|
#           |
#           |
#           |
#           |         o SEN1 <-(X1, Y1, Z1)
#           v
*/
double 	X1 =  00e-3, Y1 = -40e-3, Z1 =  00e-3; 											// Position of sensor 1
double 	X2 =  40e-3, Y2 =  00e-3, Z2 =  00e-3;                      					// Position of sensor 2
double 	X3 =  00e-3, Y3 =  40e-3, Z3 =  00e-3;                      					// Position of sensor 3
double 	X4 = -40e-3, Y4 =  00e-3, Z4 =  00e-3;                      					// Position of sensor 4 (ORIGIN)


void system_of_eqns( double *init_guess, double *sensor_eqn, int m, int n, void *data )
{	
	double 	x = init_guess[0], 															// ...
			y = init_guess[1], 															// Unpack initial guesses
			z = init_guess[2]; 															//
			
	double r1 = sqrt( (x - X1)*(x - X1) + (y - Y1)*(y - Y1) + (z - Z1)*(z - Z1) ); 		// Sensor 1
    double r2 = sqrt( (x - X2)*(x - X2) + (y - Y2)*(y - Y2) + (z - Z2)*(z - Z2) );		// Sensor 2
    double r3 = sqrt( (x - X3)*(x - X3) + (y - Y3)*(y - Y3) + (z - Z3)*(z - Z3) );		// Sensor 3
    double r4 = sqrt( (x - X4)*(x - X4) + (y - Y4)*(y - Y4) + (z - Z4)*(z - Z4) );		// Sensor 4 (ORIGIN)

    // Construct the equations
    sensor_eqn[0] = ( K*intpow( r1, -6 ) * ( 3.*( z/r1 )*( z/r1 ) + 1 ) ) - norm[0]*norm[0];    // Sensor 1
    sensor_eqn[1] = ( K*intpow( r2, -6 ) * ( 3.*( z/r2 )*( z/r2 ) + 1 ) ) - norm[1]*norm[1];    // Sensor 2
    sensor_eqn[2] = ( K*intpow( r3, -6 ) * ( 3.*( z/r3 )*( z/r3 ) + 1 ) ) - norm[2]*norm[2];    // Sensor 3
    sensor_eqn[3] = ( K*intpow( r4, -6 ) * ( 3.*( z/r4 )*( z/r4 ) + 1 ) ) - norm[3]*norm[3];    // Sensor 4
    
    
}

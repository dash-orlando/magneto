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
#define dx 			1e-7 					// Differential step needed for solver

int		ret; 								// LM return (return value is stored here for debugging)
int 	m = NAXES, n = NSENS; 				// Number of unknowns, number of equations
double 	init_guess[NAXES] = {0}, 			// Initial guess. 5 is max(2, 3, 5)
		sensor_eqn[NSENS] = {0}; 			// Equations array. 16 is max(2, 3, 5, 6, 16)
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
double 	X1 =  00e-3, Y1 = -40e-3, Z1 =  00e-3; 											
double 	X2 =  40e-3, Y2 =  00e-3, Z2 =  00e-3;                      					// Position of sensor 2
double 	X3 =  00e-3, Y3 =  40e-3, Z3 =  00e-3;                      					// Position of sensor 3
double 	X4 = -40e-3, Y4 =  00e-3, Z4 =  00e-3;                      					// Position of sensor 4 (ORIGIN)

double XYZ[NSENS][NAXES] = { { 00e-3, -40e-3,  00e-3},									// Position of sensor 1
							 { 40e-3,  00e-3,  00e-3},									// Position of sensor 2
							 { 00e-3,  40e-3,  00e-3},									// Position of sensor 3
							 {-40e-3,  00e-3,  00e-3},									// Position of sensor 4
							};

void system_of_eqns( double *init_guess, double *sensor_eqn, int m, int n, void *data )
{	
	double 	x = init_guess[0], 															// ...
			y = init_guess[1], 															// Unpack initial guesses
			z = init_guess[2]; 															//
	
	double r[n] = {0}; 																	// The 'r' term in the equation
	for( uint8_t i = 0; i < n; i++ )
	{
		uint8_t j = ndx[i]; 															// Get the index of the sensor we want to use
		double 	X = XYZ[j][0], Y = XYZ[j][1], Z = XYZ[j][2]; 							// Get the (X, Y, Z) co-ordinates of said sensor
		r[i] = sqrt( (x - X)*(x - X) + (y - Y)*(y - Y) + (z - Z)*(z - Z) ); 			// Construct the 'r' term
		sensor_eqn[i] = ( K*intpow( r[i], -6 ) * ( 3.*( z/r[i] )*( z/r[i] ) + 1 ) ) - norm[j]*norm[j];  
	}
}

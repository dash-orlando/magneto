/*
 * Construct LHS of equations
 */

#include <wiringPi.h>
#include <math.h>

#define K 			1.09e-6 		// Big Ol' Magnet's constant (K) || Units { G^2.m^6}

register int i, j; 					// Counters
int ret; 							// Number of iterations it takes to converge
double 	p[3], 						// Initial guess. 5 is max(2, 3, 5)
		eqn[3]; 					// Equations array. 16 is max(2, 3, 5, 6, 16)
int m = NAXES, n = NSENS; 			// Number of unknowns, number of equations
double 	opts[LM_OPTS_SZ],
		info[LM_INFO_SZ];

opts[0]=LM_INIT_MU; opts[1]=1E-15; opts[2]=1E-15; opts[3]=1E-20;
opts[4]= LM_DIFF_DELTA; // relevant only if the Jacobian is approximated using finite differences; specifies forward differencing
//opts[4]=-LM_DIFF_DELTA; // specifies central differencing to approximate Jacobian; more accurate but more expensive to compute!

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
double 	X1 =  00e-3, Y1 = -40e-3, Z1 =  00e-3; 									// Position of sensor 1
double 	X2 =  40e-3, Y2 =  00e-3, Z2 =  00e-3;                      			// Position of sensor 2
double 	X3 =  00e-3, Y3 =  40e-3, Z3 =  00e-3;                      			// Position of sensor 3
double 	X4 = -40e-3, Y4 =  00e-3, Z4 =  00e-3;                      			// Position of sensor 4 (ORIGIN)

// double *p 	: Initial guess. On output contains estimated solution
// double *eqn 	: Measurement vector. NULL implies a zero vector
// int m 		: Number of unkowns
// int n 		: Measurement vector dimension (number of equations?)
// void *data	: Pointer to possibly needed additional data, passed uninterpreted to func.
// 					* Set to NULL if not needed
void system_of_eqns( double *p, double *eqn, int m, int n, void *data )
{	
	double 	x = p[0], 															// ...
			y = p[1], 															// Unpack initial guesses
			z = p[2]; 															//
			
	double r1 = sqrt( (x - X1)**2. + (y - Y1)**2. + (z - Z1)**2. ); 			// Sensor 1
    double r2 = sqrt( (x - X2)**2. + (y - Y2)**2. + (z - Z2)**2. );				// Sensor 2
    double r3 = sqrt( (x - X3)**2. + (y - Y3)**2. + (z - Z3)**2. );				// Sensor 3
    double r4 = sqrt( (x - X4)**2. + (y - Y4)**2. + (z - Z4)**2. );				// Sensor 4 (ORIGIN)

    // Construct the equations
    eqn[0] = ( K*( r1 )**(-6.) * ( 3.*( z/r1 )**2. + 1 ) ) - norm[0]**2.     	// Sensor 1
    eqn[1] = ( K*( r2 )**(-6.) * ( 3.*( z/r2 )**2. + 1 ) ) - norm[1]**2.     	// Sensor 2
    eqn[2] = ( K*( r3 )**(-6.) * ( 3.*( z/r3 )**2. + 1 ) ) - norm[2]**2.     	// Sensor 3
    eqn[3] = ( K*( r4 )**(-6.) * ( 3.*( z/r4 )**2. + 1 ) ) - norm[3]**2.     	// Sensor 4
    
}

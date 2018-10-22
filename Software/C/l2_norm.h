/*
 * Compute the L2-norm of a vector
 */

#include <wiringPi.h>
#include <math>

// double const* u	: Vector that we want to compute the norm of
// int n 			: Size/length of vector
double l2_norm( double const* u, int n )
{
    double accum = 0.;
    for ( int i = 0; i < n; i++ )
    {
        accum += u[i] * u[i];
    }
    return sqrt(accum);
}

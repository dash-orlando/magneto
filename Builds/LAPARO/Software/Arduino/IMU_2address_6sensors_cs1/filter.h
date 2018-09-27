/*
 * A generalized approach for the exponential moving average
 * data smoothing based on the microsmooth library.
 *
 * Allows for multiple registers (smoothing for multiple
 * readings instead of one. Good stuff!!)
 * 
 * Recall that the exponential moving average has the form of:
 * 
 * s_n = ALPHA*x_n + ( 1-ALPHA )*s_{n-1}
 * where 0 < ALPHA < 1 is the smoothing factor
 * High ALPHA: NO smoothing.
 * Low ALPHA : YES smoothing.
 * VERY Low ALPHA: GREAT smoothing but less responsive to recent changes.
 */

#define ALPHA     0.25
#define NSENS     6
#define NAXES     3

static double exp_avg[NSENS][NAXES] =  { {0, 0, 0},    //  {1x, 1y, 1z}
                                         {0, 0, 0},    //  {2x, 2y, 2z}
                                         {0, 0, 0},    //  {3x, 3y, 3z}
                                         {0, 0, 0},    //  {4x, 4y, 4z}
                                         {0, 0, 0},    //  {5x, 5y, 5z}
                                         {0, 0, 0} };  //  {6x, 6y, 6z}
                                          
double ema_filter( double current_value, byte sens, byte axis ) {

  // Filter data
  exp_avg[sens][axis] = ALPHA*current_value + (1 - ALPHA)*exp_avg[sens][axis];

  // Return Filtered data
  return( exp_avg[sens][axis] );
}

/*
 * Compute the Position of the End-Effector
 * 
 * Functions associated with the position calculation of the
 * laparoscopic end-effector
 * Functions and variables may vary depending on the tool of use
 * 
 * Reference:-
 * 		2019 Boutelle Cost-Effective Laparoscopic Trainer Utilizing 
 *    Magnetic-Based Position Tracking
 */
 
//#define DEBUG                     5                                     // Debug only specific to the end effector function
#define PI                        3.14159265                            // Local definition of PI --Need to check correspondance across modules

bool    status                    = true;
int     error                     = 0;
double  end_effector_pos[NAXES]   = {0};                                // End Effector Position Array Initialization
double  tool_length               = 318;                                // Length (in mm) of the laparoscopic tool (scissors) --Note that length will change depending on tool
double  calc_tool_length          = 0;                                  // Calculated tool length (in mm) for error calculation
double  tool_length_error         = 0;
double  dist_ring_to_effector     = 0;                                  //
double  mag_pos_vector_len        = 0;                                  // Vector length (in mm) from the center of the magnetic tracking array (ring) and the center of the magnet
double  alphas[NAXES]             = {0};
double  test                      = 0;

/*
 *        |          |    -------------------> handle
 *        |          |    
 *        ---|    |---    -------------------> magnet
 *             ||             ==     == 
 *             ||              |      |
 *             ||              |      |
 *             ||               > mag_pos_vector_len
 *             ||              |      |
 *             ||              |      |
 *             ||              |      |
 *             ||             ==      |
 *   []=====[]====[]=====[] -----------------> mag. tracking ring
 *             ||                ==   |
 *             ||                 |   |
 *             ||                 |   |
 *             ||                 |    > tool length
 *             ||                 |   |
 *             ||                 |   |
 *             ||                 |   |
 *             ||                 |   |
 *             ||                  > dist_ring_to_effector
 *             ||                 |   |
 *             ||                 |   |
 *             ||                 |   |
 *             ||                 |   |
 *             VV                ==  ==
 * 
 * 
 */

double end_effector(double* init_guess, double* end_effector_pos, unsigned int t)
{
  // Calculate Magnet Position Vector Length
  mag_pos_vector_len = sqrt(( intpow(init_guess[0], 2) + intpow(init_guess[1], 2) + intpow(init_guess[2], 2) )) * 1000;
  //printf( "%.2lf \n", mag_pos_vector_len );
  
  // Calculate Distance from Sensor Ring to End-Effector
  dist_ring_to_effector = tool_length - mag_pos_vector_len;
  //printf( "%.2lf \n", dist_ring_to_effector );
  
  // Calculate the Cartesian Coordinates of the End Effector
  //    Determine Angle Projections
  for( uint8_t i = 0; i < NAXES; ++i )
  {
    alphas[i] = acos( (init_guess[i] * 1000) / mag_pos_vector_len ) * ( 180.0 / PI );
    //printf( " alpha[%i] = %.2lf \n", i, init_guess[i] * 1000, alphas[i] );
  } //printf( "\n" );
  //    Project Angles to Calculate Cartesian Coordinates
  for( uint8_t i = 0; i < NAXES; ++i )
  {
    end_effector_pos[i] = dist_ring_to_effector * cos( ( alphas[i] + 180.0 ) * ( PI / 180.0 ) );
    printf( " Pe[%i] = %.1lf", i, end_effector_pos[i] ); 
  } //printf( "\n" );
  // Validation
  //    The program re-calculates the measured length of the tool
  calc_tool_length = sqrt(( intpow( (init_guess[0] - end_effector_pos[0]), 2 ) + intpow( (init_guess[1] - end_effector_pos[1]), 2 ) + intpow( (init_guess[2] - end_effector_pos[2]), 2 )));
  
  // Diff. Error
  tool_length_error = tool_length - calc_tool_length;
  
  // Program Completion Timestamp
  unsigned int effector_pos_time = millis() - t;
  
  // Printing Statments ----------------------------------------------- //
  /*
  if( DEBUG == 0 )
  {
    for( uint8_t i = 0; i < NAXES; ++i )
    {
      //printf( " pe[%i] = %.3lf ", i, end_effector_pos[i] );              // Print end-effector position values
      //fprintf( logfile, "pe[%i] = %.3lf ", i, end_effector_pos[i] );    // Write end-effector position values to file 
    } printf( " t = %i\n", effector_pos_time ); fprintf( logfile, " t = %i\n", effector_pos_time );
  }
  else if( DEBUG == 1 || DEBUG == 5 )
  {
    printf(" END EFFECTOR DEBUG ============================= \n" );
    printf( " alphas = " );
    for( uint8_t i = 0; i < NAXES; ++i ) printf( "%.3lf, ", alphas[i] );
    printf( "\n epos = " );
    for( uint8_t i = 0; i < NAXES; ++i ) printf( "%.3lf ", end_effector_pos[i] );
    printf( "\n Meas. Tool Length = %.3lf | Calc. = %.3lf | Error = %.3lf \n", tool_length, calc_tool_length, tool_length_error);
  } printf( " Execution Time = %i\n\n", effector_pos_time );
  */
  
  printf( " t = %i \n", effector_pos_time );
  return tool_length;
}

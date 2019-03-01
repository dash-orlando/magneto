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

double end_effector_pos[NAXES]  = {0};                                  // End Effector Position Array Initialization
double tool_length              = 318;                                  // Length (in mm) of the laparoscopic tool (scissors) --Note that length will change depending on tool
double tool_shaft_length        = 0;                                    //
double mag_pos_vector_len       = 0;                                    // Vector length (in mm) from the center of the magnetic tracking array (ring) and the center of the magnet
double test                     = 0;

/*
 *        |          |    -------------------> handle
 *        |          |    
 *        ---|    |---    -------------------> magnet
 *             ||              |      | 
 *             ||              |      |
 *             ||              |      |
 *             ||               > mag_pos_vector_len
 *             ||              |      |
 *             ||              |      |
 *             ||              |      |
 *             ||              |      |
 *   []=====[]====[]=====[] -----------------> mag. tracking ring
 *             ||                     |
 *             ||                     |
 *             ||                     |
 *             ||                      > tool length
 *             ||                     |
 *             ||                     |
 *             ||                     |
 *             ||                     |
 *             ||                     |
 *             ||                     |
 *             ||                     |
 *             ||                     |
 *             ||                     |
 *             VV               -------
 * 
 * 
 */

double end_effector(double* init_guess, double* end_effector_pos)
{
  // Calculate Magnet Position Vector Length
  mag_pos_vector_len = sqrt(( intpow(init_guess[0], 2) + intpow(init_guess[1], 2) + intpow(init_guess[2], 2) ));
  /*
  double r = 1.0;
  if (b < 0)
  {
    a = 1.0 / a;
    b = -b;
  }
  while (b)
  {
    if (b & 1)
      r *= a;
    a *= a;
    b >>= 1;
  }
  return r;
  */
  return mag_pos_vector_len;
}

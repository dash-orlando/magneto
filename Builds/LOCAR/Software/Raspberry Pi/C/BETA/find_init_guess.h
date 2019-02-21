/*
 * Get an educated initial guess for use with LMA
 *
 * INPUTS:-
 *  	- double* guess				: initial guess array
 * 		- const double* sens_pos	: Sensors' positions on grid
 * 		- const uint8_t* sens_ndx	: Index of sensors with higest detected norm
 * 
 * OUTPUT:-
 *  	- NONE
 */

void find_init_guess( double* guess, uint8_t arr_size, double sens_pos[][NAXES], uint8_t* sens_ndx ) 
{ 
    for( uint8_t i = 0; i < arr_size; i++ )
    {
		for( uint8_t j = 0; j < arr_size; j++ )
		{
			guess[i] += sens_pos[sens_ndx[j]][i];
		} 	guess[i] /= 3;
		if( i == arr_size - 1 ) guess[i] -= 1e-3;
	}
}

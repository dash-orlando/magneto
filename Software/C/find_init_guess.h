/*
 * Get an educated initial guess for use with LMA
 *
 * INPUTS:-
 *  	- IN 1
 * 		- IN 2
 * 
 * OUTPUT:-
 *  	- NONE
 */

void find_init_guess( uint8_t* sensor_ndx, double* guess ) 
{ 
    double first, second, third; 					// Declare holding variables
	first = second = third = LONG_MIN;  			// Initialize to minus infinity
   
    /* There should be atleast two elements */
    if( arr_size < 3 ) 
    { 
        printf( "Invalid Input" ); 
        return; 
    } 
   
    for( uint8_t i = 0; i < arr_size ; i++ ) 
    { 
        /* If current element is smaller than first*/
        if(arr[i] > first) 
        { 
            third	= second; 
            second 	= first ; 
            first 	= arr[i]; 
			index[0]= i+1 	; 	// Place highest array index here
			
        } 
   
        /* If arr[i] is in between first and second then update second  */
        else if( arr[i] > second ) 
        { 
            third	= second; 
            second 	= arr[i];
			index[1]= i+1 	; 	// Place second highest array index here
        } 
   
        else if( arr[i] > third )
		{
            third 	= arr[i];
			index[2]= i+1	; 	// Place third highest array ndex here
		}
    } 
    printf( "Three largest elements are %.5f %.5lf %.5lf\n", first, second, third );
    printf( "Corresponds to sensors: %i, %i, %i\n", index[0], index[1], index[2] );
}

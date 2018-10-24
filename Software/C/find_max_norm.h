/*
 * Find the largest three elements in the norms array
 * and the corrseponding sensor index for each
 *
 * Reference:-
 * 		https://www.geeksforgeeks.org/find-the-largest-three-elements-in-an-array/
 */

#include <stdio.h> 
#include <limits.h> /* For LONG_MIN */ 

// double arr[]		: Vector that we want to compute the norm of
// int arr_size 	: Size/length of vector
// uint8_t* index	: Vector array containing the indices of the
// 						sensors from highest to lowest norm readings
void find_max_norm( double arr[], int arr_size, uint8_t* index ) 
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
            third	= second; 		// Make the old 2nd max the new 3rd max
            second 	= first ; 		// Make the old 1st max the new 2nd max
            first 	= arr[i]; 		// This is the new 1st max
            
            index[2]=index[1]; 		// Make index of the old 2nd max as the new 3rd max
            index[1]=index[0]; 		// Make index of the old 1st max as the new 2ndd max
			index[0]= i 	 ; 		// Place 1st highest array index here
			
        } 
   
        /* If arr[i] is in between first and second then update second  */
        else if( arr[i] > second ) 
        { 
            third	= second; 		// Make the old 2nd max the new 3rd max
            second 	= arr[i]; 		// This is the new 2nd max
            
            index[2]=index[1]; 		// Make index of the old 2nd max as the new 3rd max
			index[1]= i 	; 		// Place 2nd highest array index here
        } 
   
        else if( arr[i] > third )
		{
            third 	= arr[i]; 		// This is the new 3rd max
            
			index[2]= i		; 		// Place 3rd highest array ndex here
		}
    }
    
    #ifdef DEBUG
	    printf( "Three largest elements are %.5f %.5lf %.5lf\n", first, second, third );
	    printf( "Corresponds to sensors: %i, %i, %i\n", index[0]+1, index[1]+1, index[2]+1 );
	#endif
}

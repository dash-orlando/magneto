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
            third	= second; 
            second 	= first ; 
            first 	= arr[i]; 
			index[0]= i 	; 	// Place highest array index here
			
        } 
   
        /* If arr[i] is in between first and second then update second  */
        else if( arr[i] > second ) 
        { 
            third	= second; 
            second 	= arr[i];
			index[1]= i 	; 	// Place second highest array index here
        } 
   
        else if( arr[i] > third )
		{
            third 	= arr[i];
			index[2]= i 	; 	// Place third highest array ndex here
		}
    } 
    printf( "Three largest elements are %d %d %d\n", first, second, third );
}
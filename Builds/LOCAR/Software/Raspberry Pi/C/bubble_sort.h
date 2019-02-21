// A function to implement bubble sort 
void bubbleSort( uint8_t array[], uint8_t n ) 
{
	uint8_t temp, x, y; 			// Temporary, [j] element, [j+1] element 
	for (uint8_t i = 0; i < n-1; i++)
	// Last i elements are already in place
		for (uint8_t j = 0; j < n-i-1; j++)
			if (array[j] > array[j+1])
			{
				temp	= x; 
				x		= y; 
				y		= temp; 
			}
}

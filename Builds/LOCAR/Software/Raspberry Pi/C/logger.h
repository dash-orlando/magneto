/*
 * Output Data Logger
 * 
 * Functions associated with the storing, logging of data
 * 
 * Things to do:
 * - Generate several output/log files (magneto, debug, locar...)
 * 
 * Fluvio Lobo Fenoglietto 03/05/2019
 */
 
FILE *logfile = fopen( "output.txt", "w" ); 								            // Open file for writing

//if( logfile == NULL )
//{
//  printf( "ERROR! Could not open file\n" );
//  exit( -1 );
//}


'''
*
* Position tracking of magnet based on Finexus
* https://ubicomplab.cs.washington.edu/pdfs/finexus.pdf
*
* VERSION: 0.4.2
*   - MODIFIED: Create thread from .cpp implementation for data acquisition
*   - FIXED   : Position calculation lagged behind acquired data. Fixed that
*               by clearing queue prior to pulling data (that way we always
*               get the most up to data magnetic field readings)
*   - ADDED   : Determine direction and number of revolutions
*
*
* VERSION: 0.4.5
*   - MODIFIED: direction and revolution calculations are based on polar
*               co-ordinates
*
* KNOWN ISSUES:
*   - Can't determine whether we completed a FULL revolution
*     or just crossed the 180degree mark.
*       NOTE: arctan( y, x ) has a domain of [-pi, pi)
*
* AUTHOR                    :   Edward Nichols
* LAST CONTRIBUTION DATE    :   Sep. 29th, 2017 Year of Our Lord
* 
* AUTHOR                    :   Mohammad Odeh 
* LAST CONTRIBUTION DATE    :   Oct. 16th, 2018 Year of Our Lord
*
'''

# Import Modules
import  numpy                       as      np              # Import Numpy
from    time                        import  time, sleep, localtime     # Sleep for stability
from    scipy.optimize              import  root            # Solve System of Eqns for (x, y, z)
from    scipy.linalg                import  norm            # Calculate vector norms (magnitude)
from    usbProtocol                 import  createUSBPort   # Create USB port (serial comm. w\ Arduino)
import  argparse                                            # Feed in arguments to the program

# ************************************************************************
# =====================> CONSTRUCT ARGUMENT PARSER <=====================*
# ************************************************************************
ap = argparse.ArgumentParser()

ap.add_argument( "-d", "--debug", action = 'store_true',
                 help = "Debugging flag" )
ap.add_argument( "-v", "--verbose", action = 'store_true',
                 help = "Print EVERYTHING!!!")

args = vars( ap.parse_args() )

args["debug"]   = False
args["verbose"] = False

# ************************************************************************
# =====================> DEFINE NECESSARY FUNCTIONS <====================*
# ************************************************************************

def argsort( seq ):
    '''
    Sort a list's elements from smallest to largest and
    return the sorted INDICES NOT VALUES!
    
    INPUTS:
        - seq: A list whose elements are to be sorted 

    OUTPUT:
        - A list containing the indices of the given list's elements
          arranged from the index of the element with the smallest
          value to the index of the element with the largest value
    '''
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)

# --------------------------

def bubbleSort( arr, N ):
    '''
    Sort a list's elements from smallest to largest 
    
    INPUTS:
        - arr: List to be sorted
        - N  : Number of elements in said list that need to be sorted
                (i.e list has 5 elements, if N=3, sort the first 3)

    OUTPUT:
        - A sorted list of size N
    '''
    data = []
    for i in range(0, N):
        data.append( arr[i] )

    for i in range(0, len(data)):
        for j in range(0, len(data)-i-1):
            if (data[j] > data[j+1]):
                temp = data[j]
                data[j] = data[j+1]
                data[j+1] = temp
            else:
                continue
    return (data)

# --------------------------

def getData( ser, NSENS=6 ):
    '''
    Pool the data from the MCU (wheteher it be a Teensy or an Arduino or whatever)
    The data consists of the magnetic field components in the x-, y-, and z-direction
    of all the sensors. The array must begin with '<' as the SOH signal, the compononents
    must be comma delimited, and must end with '>' as the EOT signal.
    
            >$\     <B_{1x}, B_{1y}, B_{1z}, ..., B_{1x}, B_{1y}, B_{1z}> 
    
    INPUTS:
        - ser: a serial object. Note that the serial port MUST be open before
               passing it the to function

    OUTPUT:
        - Individual numpy arrays of all the magnetic field vectors
    '''
    global CALIBRATING

    # Flush buffer
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # Allow data to fill-in buffer
    # sleep(0.1)

    try:
        # Wait for the sensor to calibrate itself to ambient fields.
        while( True ):
            if(CALIBRATING == True):
                print( "Calibrating...\n" )
                CALIBRATING = False
            if ser.in_waiting > 0:  
                inData = (ser.read()).strip('\n')
                #print( inData )
                if( inData == b'<' ):
                    break  

        # Read the actual data value. Stop at End of Data specifier '>'. 
        line = ''
        while( True ):
            if ser.in_waiting > 0:
                inData = (ser.read()).strip('\n')
                if inData == '>':
                    break
                line = line + inData

        # Split line into the constituent components

        # Check if array is corrupted
        col     = (line.rstrip()).split(",")
        if (len(col) == NSENS*3):
            #
            # Construct magnetic field array
            #

            # Sensor 1
            Bx = float( col[0] )
            By = float( col[1] )
            Bz = float( col[2] )
            B1 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

            # Sensor 2
            Bx = float( col[3] )
            By = float( col[4] )
            Bz = float( col[5] )
            B2 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

            # Sensor 3
            Bx = float( col[6] )
            By = float( col[7] )
            Bz = float( col[8] )
            B3 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

            # Sensor 4
            Bx = float( col[9]  )
            By = float( col[10] )
            Bz = float( col[11] )
            B4 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

            # Sensor 5
            Bx = float( col[12] )
            By = float( col[13] )
            Bz = float( col[14] )
            B5 = np.array( ([Bx],[By],[Bz]), dtype='float64') # Units { G }

            # Sensor 6
            Bx = float( col[15] )
            By = float( col[16] )
            Bz = float( col[17] )
            B6 = np.array( ([Bx],[By],[Bz]), dtype='float64' )# Units { G }
            
            # Return vectors
            return ( B1, B2, B3, B4, B5, B6 )

        # In case array is corrupted, call the function again
        else:
            return( getData(ser) )

    except Exception as e:
        print( "Caught error in get_array()"        )
        print( "Error type {}".format(type(e))      )
        print( "Error Arguments {}".format(e.args)  )

# --------------------------

def LHS( root, K, norms ):
    '''
    Construct the left hand side (LHS) of the equations
    to numerically solve for.
    Recall that in order to solve a system numerically it
    must have the form of,
    
          if    >$\  LHS = f(x, y, z, ...) = g(x, y, z, ...) = RHS
          then  >$\  f(x, y, z, ...) - g(x, y, z, ...) = LHS - RHS = 0
    
    INPUTS:
        - root  : A numpy array contating the initial guesses of the roots
        - K     : K is a property of the magnet and has units of { G^2.m^6}
        - norms : An array/list of the vector norms of the magnetic field
                  vectors for all the sensors

    OUTPUT:
        - An array of equations that are sorted corresponding to which
          3 sensors' equations are going to be used with the LMA solver.
          The sorting is based on which 3 sensors are closest to the magnet.
    '''
    
    # Extract x, y, and z
    x, y, z = root
    
    # Construct the (r) terms for each sensor
    # NOTE: Relative distance terms are in meters
    #     : Standing on sensor(n), how many units in
    #       the x/y/z direction should I march to get
    #       back to sensor1 (origin)?
    r1 = float( ( (x - X1)**2. + (y - Y1)**2. + (z - Z1)**2. )**(1/2.) )    # Sensor 1 (ORIGIN)
    r2 = float( ( (x - X2)**2. + (y - Y2)**2. + (z - Z2)**2. )**(1/2.) )    # Sensor 2
    r3 = float( ( (x - X3)**2. + (y - Y3)**2. + (z - Z3)**2. )**(1/2.) )    # Sensor 3
    r4 = float( ( (x - X4)**2. + (y - Y4)**2. + (z - Z4)**2. )**(1/2.) )    # Sensor 4 
    r5 = float( ( (x - X5)**2. + (y - Y5)**2. + (z - Z5)**2. )**(1/2.) )    # Sensor 5
    r6 = float( ( (x - X6)**2. + (y - Y6)**2. + (z - Z6)**2. )**(1/2.) )    # Sensor 6
    
    # Construct the equations
    Eqn1 = ( K*( r1 )**(-6.) * ( 3.*( z/r1 )**2. + 1 ) ) - norms[0]**2.     # Sensor 1
    Eqn2 = ( K*( r2 )**(-6.) * ( 3.*( z/r2 )**2. + 1 ) ) - norms[1]**2.     # Sensor 2
    Eqn3 = ( K*( r3 )**(-6.) * ( 3.*( z/r3 )**2. + 1 ) ) - norms[2]**2.     # Sensor 3
    Eqn4 = ( K*( r4 )**(-6.) * ( 3.*( z/r4 )**2. + 1 ) ) - norms[3]**2.     # Sensor 4
    Eqn5 = ( K*( r5 )**(-6.) * ( 3.*( z/r5 )**2. + 1 ) ) - norms[4]**2.     # Sensor 5
    Eqn6 = ( K*( r6 )**(-6.) * ( 3.*( z/r6 )**2. + 1 ) ) - norms[5]**2.     # Sensor 6
    
    # Construct a vector of the equations
    Eqns = [Eqn1, Eqn2, Eqn3, Eqn4, Eqn5, Eqn6]

    # Determine which sensors to use based on magnetic field value (smallValue==noBueno!)
    sort = argsort( norms )                                                 # Auxiliary function sorts norms from smallest to largest
    sort.reverse()                                                          # Python built-in function reverses elements of list
    f=[]                                                                    # Declare vector to hold relevant functions

    for i in range(0, 3):                                                   # Fill functions' array with the equations that correspond to
        f.append( Eqns[sort[i]] )                                           # the sensors with the highest norm, thus closest to magnet

    # Return vector
    return ( f )

# --------------------------

def findIG( magFields ):
    '''
    Dynamic search of initial guess for the LMA solver based on magnitude
    of the magnetic field relative to all the sensors.
    A high magnitude reading indicates magnet is close to some 3
    sensors, the centroid of the traingle created by said sensors
    is fed as the initial guess
    
    INPUTS:
        - magfield: A numpy array containing all the magnetic field readings

    OUTPUT:
        - A numpy array containing <x, y, z> values for the initial guess
    '''
    
    # Define IMU positions on the grid
    #      / sensor 1: (x, y, z)
    #     /  sensor 2: (x, y, z)
    # Mat=      :          :
    #     \     :          :
    #      \ sensor 6: (x, y, z)
    IMU_pos = np.array(((X1, Y1, Z1) ,
                        (X2, Y2, Z2) ,
                        (X3, Y3, Z3) ,
                        (X4, Y4, Z4) ,
                        (X5, Y5, Z5) ,
                        (X6, Y6, Z6)), dtype='float64')

    # Read current magnetic field from MCU
    (H1, H2, H3, H4, H5, H6) = magFields

    # Compute L2 vector norms
    HNorm = [ float( norm(H1) ), float( norm(H2) ),
              float( norm(H3) ), float( norm(H4) ),
              float( norm(H5) ), float( norm(H6) )]
    
    # Determine which sensors to use based on magnetic field value (smallValue==noBueno!)
    sort = argsort( HNorm )                     # Auxiliary function sorts norms from smallest to largest
    sort.reverse()                              # Python built-in function reverses elements of list

    IMUS = bubbleSort( sort, 3 )

    # Return the initial guess as the centroid of the detected triangle
    return ( np.array(((IMU_pos[IMUS[0]][0]+IMU_pos[IMUS[1]][0]+IMU_pos[IMUS[2]][0])/3.,
                       (IMU_pos[IMUS[0]][1]+IMU_pos[IMUS[1]][1]+IMU_pos[IMUS[2]][1])/3.,
                       (IMU_pos[IMUS[0]][2]+IMU_pos[IMUS[1]][2]+IMU_pos[IMUS[2]][2])/3. -0.01), dtype='float64') )

# --------------------------

def find_end_effector( xm, ym, zm, Lt ):
    """
    Function to calculate the position of end effectors based on the position of the magnet
    """
    Li = np.sqrt( xm**2 + ym**2 + zm**2 )

    # calculate the length of the rod
    Lii = Lt - Li

    # calculate the coordinates of the end effector
    ## determine angle projections

    alpha_x = np.arccos( xm / Li )*( 180 / np.pi )
    alpha_y = np.arccos( ym / Li )*( 180 / np.pi )
    alpha_z = np.arccos( zm / Li )*( 180 / np.pi )

    # project
    xe = Lii*np.cos( ( alpha_x + 180 ) * (np.pi/180) )
    ye = Lii*np.cos( ( alpha_y + 180 ) * (np.pi/180) )
    ze = Lii*np.cos( ( alpha_z + 180 ) * (np.pi/180) )

    # validation
    length = np.sqrt( ( xm - xe )**2 + ( ym - ye )**2 + ( zm - ze )**2 )

    return xe, ye, ze, length
    


# ************************************************************************
# ===========================> SETUP PROGRAM <===========================
# ************************************************************************

# Useful variables
global CALIBRATING

CALIBRATING = True                              # Boolean to indicate that device is calibrating
READY       = False                             # Give time for user to place magnet

# Define the position of the sensors on the grid
# relative to the origin, i.e:
#
#       +y  ^
#           |         o SEN3 <-(X3, Y3, Z3)
#           |
#           |                       ____ (X2, Y2, Z2)
#           |                      /
#           |                     V
#   ORIGIN, O----------------- o SEN2 --> +x
#  (0, 0, 0)|
#           |
#           |
#           |
#           |         o SEN1 <-(X1, Y1, Z1)
#           v


#X0, Y0, Z0 = 00e-3,   00e-3,   00e-3                                         # ORGIN @ CENTER
X1, Y1, Z1 =  00e-3,   75e-3,   10e-3                                         # Position of sensor 1
X2, Y2, Z2 =  68e-3,   37e-3,   00e-3                                         # Position of sensor 2
X3, Y3, Z3 =  68e-3,  -37e-3,   10e-3                                         # Position of sensor 3
X4, Y4, Z4 =  00e-3,  -75e-3,   00e-3                                         # Position of sensor 4 
X5, Y5, Z5 = -68e-3,  -37e-3,   10e-3                                         # Position of sensor 5
X6, Y6, Z6 = -68e-3,   37e-3,   00e-3                                         # Position of sensor 6 

# Choose the magnet we want to track
##K           = 1.615e-7                                                      # Small magnet's constant   (K) || Units { G^2.m^6}
K           = 1.09e-6                                                       # Big magnet's constant     (K) || Units { G^2.m^6}
dx          = 1e-7                                                          # Differential step size (Needed for solver)

# Surgical tool dimensions
Lt          = 318                                                               # length of the surgical tool

# Establish connection with Arduino
DEVC        = "Arduino"                                                         # Device Name (not very important)
PORTPREFIX  = "COM"
PORTNUM     = 3                                                                 # Port number (VERY important)
BAUD        = 115200                                                            # Baudrate    (VERY VERY important)

# Error handling in case serial communcation fails (1/2)
try:
    IMU = createUSBPort( DEVC, PORTPREFIX, PORTNUM, BAUD )     # Create serial connection
    if IMU.is_open == False:                    # Make sure port is open
        IMU.open()
    print( "Serial Port OPEN" )

    initialGuess = findIG(getData(IMU))         # Determine initial guess based on magnet's location

# Error handling in case thread spawning fails (2/2)
except Exception as e:
    print( "Could NOT open serial port"         )
    print( "Error type {}".format(type(e))      )
    print( "Error Arguments {}".format(e.args)  )
    sleep( 2.5 )
    quit()                                                                  # Shutdown entire program

finally:
    # output file parameters
    date = localtime( time() )
    name = "output/%d-%d-%d_%d-%d-%d.txt" %(date[1],date[2],date[0]%100,date[3],date[4],date[5])         #FileName = Month_Day_Year
    f = open(name, 'w')
    
# ************************************************************************
# =========================> MAKE IT ALL HAPPEN <=========================
# ************************************************************************

print( "Ready in 3 " ), ; sleep( 1.0 )
print( "... 2 " ),      ; sleep( 1.0 )
print( "... 1 " )       ; sleep( 1.0 )
print( "GO!" )

# Start iteration
prog_start = time()
while( True ):

    loop_start = time()                                                     # Call clock() for accurate time readings

    # Data acquisition
    (H1, H2, H3, H4, H5, H6) = getData(IMU)                                 # Get data from MCU
    
    # Compute norms
    HNorm = [ float(norm(H1)), float(norm(H2)),                             #
              float(norm(H3)), float(norm(H4)),                             # Compute L2 vector norms
              float(norm(H5)), float(norm(H6)) ]                            #

    # Solve system of equations
    sol = root(LHS, initialGuess, args=(K, HNorm), method='lm',             # Invoke solver using the
               options={'ftol':1e-10, 'xtol':1e-10, 'maxiter':1000,         # Levenberg-Marquardt 
                        'eps':1e-8, 'factor':0.001})                        # Algorithm (aka LMA)

    # Store solution in array
    position = np.array( (sol.x[0]*1000,                                    # x-axis
                          sol.x[1]*1000,                                    # y-axis
                          sol.x[2]*1000,                                    # z-axis
                          time() - loop_start  ), dtype='float64' )         # time

    # Check value
##    if( position[2] < 0 ): position[2] = -1*position[2]                     # Make sure z-value
##    else: pass                                                              # ... is ALWAYS +ve


    # calculate position of end effector
    xm = position[0]
    ym = position[1]
    zm = position[2]
    xe, ye, ze, length = find_end_effector( xm, ym, zm, Lt )

    # Print solution (coordinates) to screen
    solution_str    = "(xm, ym, zm, xe, ye, ze, length, t): ({:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f})"          # ...
    output_str      = "{:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}"
    print( solution_str.format( position[0], position[1], position[2], xe, ye, ze, length, position[3], (time() - prog_start) ) )                          # ...
    # Write data to file
    f.write( output_str.format( position[0], position[1], position[2], xe, ye, ze, length, position[3], (time() - prog_start) ) )
    f.write( '\n' )

    sleep( 0.1 )                                                            # Sleep for stability

    # Check if solution makes sense
    if (abs(sol.x[0]*1000) > 500) or (abs(sol.x[1]*1000) > 500) or (abs(sol.x[2]*1000) > 500):
        initialGuess = findIG( getData(IMU) )                               # Determine initial guess based on magnet's location

    # Update initial guess with current position and feed back to solver
    else:    
        initialGuess = np.array( (sol.x[0]+dx, sol.x[1]+dx,                 # Update the initial guess as the
                                  sol.x[2]+dx), dtype='float64' )           # current position and feed back to LMA

# ************************************************************************
# =============================> DEPRECATED <=============================
# ************************************************************************
f.close()

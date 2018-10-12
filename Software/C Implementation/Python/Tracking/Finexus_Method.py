'''
*
* Position tracking of magnet based on Finexus
* https://ubicomplab.cs.washington.edu/pdfs/finexus.pdf
*
* VERSION: 0.4
*   - MODIFIED: Create thread from .cpp implementation for data acquisition
*
* KNOWN ISSUES:
*   - Nada atm
*
* AUTHOR                    :   Edward Nichols
* LAST CONTRIBUTION DATE    :   Sep. 29th, 2017 Year of Our Lord
* 
* AUTHOR                    :   Mohammad Odeh 
* LAST CONTRIBUTION DATE    :   Oct. 12th, 2018 Year of Our Lord
*
'''

# Import Modules
import  numpy               as      np              # Import Numpy
from    time                import  time, sleep     # Sleep for stability
from    scipy.optimize      import  root            # Solve System of Eqns for (x, y, z)
from    scipy.linalg        import  norm            # Calculate vector norms (magnitude)
from    usbProtocol         import  createUSBPort   # Create USB port (serial comm. w\ Arduino)
import  argparse                                    # Feed in arguments to the program
import  pexpect
from    threading                   import Thread, Event
from    Queue                       import Queue

# ************************************************************************
# =====================> CONSTRUCT ARGUMENT PARSER <=====================*
# ************************************************************************
ap = argparse.ArgumentParser()

ap.add_argument("-d", "--debug", action='store_true',
                help="invoke flag to enable debugging")

args = vars( ap.parse_args() )

args["debug"]   = False

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

q_output = Queue( maxsize=0 )                                                   # Define queue
def readMagneto( q_output, initialCall=True ):
    cmd = "/home/pi/Desktop/magneto/magneto"
    magneto = pexpect.spawn( cmd, timeout=None )

##    if( initialCall ):
##        q_output.put( magneto )                                              # Place variable in queue for retrival
##        initialCall = False
        
    for line in magneto:
        out = line.strip('\n\r')
        q_output.put( out )
        #print( out )

    #q_output.close()

# --------------------------

def getData( ser, NSENS=4 ):
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

    line = ser.get()
    line = line.strip( "<" )
    line = line.strip( ">" )
##    print( line )
    
    try:

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
            
            # Return vectors
            return ( B1, B2, B3, B4 )

        # In case array is corrupted, call the function again
        else:
            return( getData(ser) )

    except Exception as e:
        print( "Caught error in getData()"          )
        print( "Error type {}".format(type(e))      )
        print( "Error Arguments {}".format(e.args)  )

# --------------------------

def LHS( root, K, norms ):
    '''
    Construct the left hand side (LHS) of the equations
    to numerically solve for.
    Recall that in order to solve a system numerically it
    must have the form of,
    
                >$\  f(x, y, z, ...) = LHS = 0
    
    INPUTS:
        - root  : a numpy array contating the initial guesses of the roots
        - K     : K is a property of the magnet and has units of { G^2.m^6}
        - norms : An array/list of the vector norms of the magnetic field
                  vectors for all the sensors

    OUTPUT:
        - An array of equations that are sorted corresponding to which
          3 sensors' equations are going to be used with the LMA solver.
          The sorting is based on which 3 sensors are closest to the magnet.
    '''
    global PRINT
    
    # Extract x, y, and z
    x, y, z = root
    
    # Construct the (r) terms for each sensor
    # NOTE: Relative distance terms are in meters
    #     : Standing on sensor(n), how many units in
    #       the x/y/z direction should I march to get
    #       back to sensor1 (origin)?
    r1 = float( ( (x+0.000)**2. + (y+0.000)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 1 (ORIGIN)
    r2 = float( ( (x-0.040)**2. + (y+0.040)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 2
    r3 = float( ( (x-0.080)**2. + (y+0.000)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 3
    r4 = float( ( (x-0.040)**2. + (y-0.040)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 4

    # Construct the equations
    Eqn1 = ( K*( r1 )**(-6.) * ( 3.*( z/r1 )**2. + 1 ) ) - norms[0]**2.     # Sensor 1
    Eqn2 = ( K*( r2 )**(-6.) * ( 3.*( z/r2 )**2. + 1 ) ) - norms[1]**2.     # Sensor 2
    Eqn3 = ( K*( r3 )**(-6.) * ( 3.*( z/r3 )**2. + 1 ) ) - norms[2]**2.     # Sensor 3
    Eqn4 = ( K*( r4 )**(-6.) * ( 3.*( z/r4 )**2. + 1 ) ) - norms[3]**2.     # Sensor 4

    # Construct a vector of the equations
    Eqns = [Eqn1, Eqn2, Eqn3, Eqn4]

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
        - magfield: a numpy array containing all the magnetic field readings

    OUTPUT:
        - A numpy array containing <x, y, z> values for the initial guess
    '''
    
    # Define IMU positions on the grid
    #      / sensor 1: (x, y, z)
    #     /  sensor 2: (x, y, z)
    # Mat=      :          :
    #     \     :          :
    #      \ sensor 6: (x, y, z)
    IMU_pos = np.array(((0.0  , 0.0  ,   0.0) ,
                        (0.040,-0.040,   0.0) ,
                        (0.080, 0.000,   0.0) ,
                        (0.040, 0.040,   0.0)), dtype='float64')

    # Read current magnetic field from MCU
    (H1, H2, H3, H4) = magFields

    # Compute L2 vector norms
    HNorm = [ float( norm(H1) ), float( norm(H2) ),
              float( norm(H3) ), float( norm(H4) ) ]
    
    # Determine which sensors to use based on magnetic field value (smallValue==noBueno!)
    sort = argsort( HNorm )                     # Auxiliary function sorts norms from smallest to largest
    sort.reverse()                              # Python built-in function reverses elements of list

    IMUS = bubbleSort( sort, 3 )

    # Return the initial guess as the centroid of the detected triangle
    return ( np.array(((IMU_pos[IMUS[0]][0]+IMU_pos[IMUS[1]][0]+IMU_pos[IMUS[2]][0])/3.,
                       (IMU_pos[IMUS[0]][1]+IMU_pos[IMUS[1]][1]+IMU_pos[IMUS[2]][1])/3.,
                       (IMU_pos[IMUS[0]][2]+IMU_pos[IMUS[1]][2]+IMU_pos[IMUS[2]][2])/3. -0.01), dtype='float64') )

# ************************************************************************
# ===========================> SETUP PROGRAM <===========================
# ************************************************************************

# Useful variables
global CALIBRATING

CALIBRATING = True                                                      # Boolean to indicate that device is calibrating

##K           = 1.615e-7                                                  # Small magnet's constant   (K) || Units { G^2.m^6}
K           = 1.09e-6                                                   # Big magnet's constant     (K) || Units { G^2.m^6}
dx          = 1e-7                                                      # Differential step size (Needed for solver)


# Error handling in case serial communcation fails (1/2)
try:
    t_readMagneto = Thread( target=readMagneto, args=( q_output, ) )    # Define thread
    t_readMagneto.daemon = True                                         # Set to daemon
    t_readMagneto.start()                                               # Start thread

    initialGuess = findIG(getData(q_output))                            # Determine initial guess based on magnet's location

# Error handling in case serial communcation fails (2/2)
except Exception as e:
    print( "Could NOT create thread. Check .cpp")
    print( "Error type {}".format(type(e))      )
    print( "Error Arguments {}".format(e.args)  )
    sleep( 2.5 )
    quit()                                                              # Shutdown entire program


# ************************************************************************
# =========================> MAKE IT ALL HAPPEN <=========================
# ************************************************************************

print( "Ready in 3 " ), ; sleep( 1.0 )
print( "... 2 " ),      ; sleep( 1.0 )
print( "... 1 " )       ; sleep( 1.0 )
print( "GO!" )

# Start iteration
while( True ):

    start = time()                                                      # Call clock() for accurate time readings
    
    # Data acquisition
    (H1, H2, H3, H4) = getData(q_output)                                # Get data from MCU
    
    # Compute norms
    HNorm = [ float(norm(H1)), float(norm(H2)),                         # Compute norms
              float(norm(H3)), float(norm(H4)) ]                        # ...

    # Solve system of equations
    sol = root(LHS, initialGuess, args=(K, HNorm), method='lm',         # Invoke solver using the
               options={'ftol':1e-10, 'xtol':1e-10, 'maxiter':1000,     # Levenberg-Marquardt 
                        'eps':1e-8, 'factor':0.001})                    # Algorithm (aka LMA)

    # Store solution in array
    position = np.array( (sol.x[0]*1000,                                # x-axis
                          sol.x[1]*1000,                                # y-axis
                          sol.x[2]*1000,                                # z-axis
                          time()-start  ), dtype='float64' )            # time

    # Check value
    if( position[2] < 0 ): position[2] = -1*position[2]                 # Make sure z-value
    else: pass                                                          # ... is ALWAYS +ve

    # Print solution (coordinates) to screen
    print( "(x, y, z, t): (%.3f, %.3f, %.3f, %.3f)" %( position[0],
                                                       position[1],
                                                       position[2],
                                                       position[3] ) )

    sleep( 0.1 )                                                        # Sleep for stability

    # Check if solution makes sense
    if (abs(sol.x[0]*1000) > 500) or (abs(sol.x[1]*1000) > 500) or (abs(sol.x[2]*1000) > 500):
        initialGuess = findIG( getData(q_output) )                      # Determine initial guess based on magnet's location

    # Update initial guess with current position and feed back to solver
    else:    
        initialGuess = np.array( (sol.x[0]+dx, sol.x[1]+dx,             # Update the initial guess as the
                                  sol.x[2]+dx), dtype='float64' )       # current position and feed back to LMA

# ************************************************************************
# =============================> DEPRECATED <=============================
# ************************************************************************
#

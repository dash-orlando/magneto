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
from    time                        import  time, sleep     # Sleep for stability
from    scipy.optimize              import  root            # Solve System of Eqns for (x, y, z)
from    scipy.linalg                import  norm            # Calculate vector norms (magnitude)
from    threading                   import  Thread          # Create threads
from    Queue                       import  Queue           # Create queues
from    usbProtocol                 import  createUSBPort   # Create USB port (serial comm. w\ Arduino)
import  argparse                                            # Feed in arguments to the program
import  pexpect                                             # Spawn programs

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

def getData( queue ):
    '''
    Poll the data from the .cpp program and place in queue for retrieval
    The data consists of the magnetic field components in the x-, y-, and z-direction
    of all the sensors.
    
    INPUTS:
        - queue     : A queue object of size infinity

    OUTPUT:
        - Magnetic field readings placed in queue for later retrieval
    '''

    magneto = pexpect.spawn( cpp_prog, timeout=None )

    for line in magneto:
        out = line.strip('\n\r')
        if( args["verbose"] ): print( out )
        
        with queue.mutex:                                                   # Clear queue. This is done because we are placing items in the queue
            queue.queue.clear()                                             # faster than we are using, which causes our calculations to lag behind
            
        queue.put( out )                                                    # Place items in queue

    queue.close()                                                           # Close queue
    
# --------------------------

def get_array( array_queue, NSENS=4 ):
    '''
    Construct magnetic field readings into a numpy array. The input array must begin
    with '<' as the SOH signal, the compononents must be comma delimited, and must end
    with '>' as the EOT signal.
    
            >$\     <B_{1x}, B_{1y}, B_{1z}, ..., B_{1x}, B_{1y}, B_{1z}> 
    
    INPUTS:
        - array_queue : A queue object. This is where the magnetic field readings
                        from the .cpp program are stored.
        - NSENS       : Number of sensors in the array

    OUTPUT:
        - Individual numpy arrays of all the magnetic field vectors
    '''
    

    global CALIBRATING

    line = array_queue.get()                                                # Get whatever is in queue
    line = line.strip( "<" )                                                # Strip the SOH marker
    line = line.strip( ">" )                                                # Strip the EOT marker
    
    try:

        # Check if array is corrupted
        col     = (line.rstrip()).split(",")                                # Split elements using delimiter
        if (len(col) == NSENS*3):
            #
            # Construct magnetic field array
            #

            # Sensor 1
            Bx = float( col[0] )
            By = float( col[1] )
            Bz = float( col[2] )
            B1 = np.array( ([Bx],[By],[Bz]), dtype='float64')               # Units { G }

            # Sensor 2
            Bx = float( col[3] )
            By = float( col[4] )
            Bz = float( col[5] )
            B2 = np.array( ([Bx],[By],[Bz]), dtype='float64')               # Units { G }

            # Sensor 3
            Bx = float( col[6] )
            By = float( col[7] )
            Bz = float( col[8] )
            B3 = np.array( ([Bx],[By],[Bz]), dtype='float64')               # Units { G }

            # Sensor 4
            Bx = float( col[9]  )
            By = float( col[10] )
            Bz = float( col[11] )
            B4 = np.array( ([Bx],[By],[Bz]), dtype='float64')               # Units { G }
            
            # Return vectors
            return ( B1, B2, B3, B4 )

        # In case array is corrupted, call the function again
        else:
            return( get_array(array_queue) )

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
    r1 = float( ( (x - X1)**2. + (y - Y1)**2. + (z - Z1)**2. )**(1/2.) )    # Sensor 1
    r2 = float( ( (x - X2)**2. + (y - Y2)**2. + (z - Z2)**2. )**(1/2.) )    # Sensor 2
    r3 = float( ( (x - X3)**2. + (y - Y3)**2. + (z - Z3)**2. )**(1/2.) )    # Sensor 3
    r4 = float( ( (x - X4)**2. + (y - Y4)**2. + (z - Z4)**2. )**(1/2.) )    # Sensor 4 (ORIGIN)

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
                        (X4, Y4, Z4)), dtype='float64')

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

# --------------------------

def compute_rotation( position_crnt, TOL = 1e-6 ):
    '''
    Compute rotations and direction
    '''
    global position_prvs, revolutions

    r, theta = position_crnt                                                # Unpack data
    R, THETA = position_prvs                                                # ...

    if( theta >= -np.pi and THETA <= np.pi ):                               # Limit ourselves to atan2(y, x) domain
        if ( theta - THETA < -5 ):                                          #   In case we are going CCW
            revolutions -= 1                                                #       Decrement revolutions counter
            print( "We are moving CCW" )                                    #       ...
            print( " Number of revolutions: {}".format(revolutions) )       #       ...
            
        elif ( theta - THETA > 5 ):                                         #   In case we are going CW
            revolutions += 1                                                #       Increment revolutions counter
            print( "We are moving CW" )                                     #       ...
            print( " Number of revolutions: {}".format(revolutions) )       #       ..

    position_prvs = position_crnt                                           # Update PAST variable


# --------------------------

def convert_to_polar( cartesian_coordinates ):
    '''
    Convert cartesian to polar coordinates

    INPUTS:
        - cartesian_coordinates: Cartesian coordinates in the form (x, y, z, t)

    OUTPUT:
        - r     : The radius at which the magnet is found
        - theta : The angle  at which the magnet is found
    '''

    x, y, z, _  = cartesian_coordinates

    r           = np.sqrt( x**2 + y**2 )
    theta       = np.arctan2( y, x )

    if( args["debug"] or args["verbose"] ):
        print( "r = {}, theta = {}".format(r, theta) )

    return( r, theta )

# ************************************************************************
# ===========================> SETUP PROGRAM <===========================
# ************************************************************************

# Define useful variables/parameters
global position_prvs, revolutions                                           # Used to store previous position readings ...
position_prvs   = 0, 0                                                      # ... used for determining direction ...
revolutions     = 0                                                         # ... and number of revolutions

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

X1, Y1, Z1 =  00e-3, -40e-3,  00e-3                                         # Position of sensor 1
X2, Y2, Z2 =  40e-3,  00e-3,  00e-3                                         # Position of sensor 2
X3, Y3, Z3 =  00e-3,  40e-3,  00e-3                                         # Position of sensor 3
X4, Y4, Z4 = -40e-3,  00e-3,  00e-3                                         # Position of sensor 4 (ORIGIN)

# Choose the magnet we want to track
##K           = 1.615e-7                                                      # Small magnet's constant   (K) || Units { G^2.m^6}
K           = 1.09e-6                                                       # Big magnet's constant     (K) || Units { G^2.m^6}
dx          = 1e-7                                                          # Differential step size (Needed for solver)

# Full path to the compiled .cpp program
cpp_prog = "/home/pi/Desktop/magneto/magneto"                               # Define the program to use

# Error handling in case thread spawning fails (1/2)
try:
    q_cpp_output = Queue( maxsize=0 )                                       # Define queue (this will have the magnetic field readings)
    t_getData = Thread( target=getData, args=( q_cpp_output, ) )            # Define thread
    t_getData.daemon = True                                                 # Set to daemon
    t_getData.start()                                                       # Start thread

    initialGuess = findIG(get_array(q_cpp_output))                          # Determine initial guess based on magnet's location

# Error handling in case thread spawning fails (2/2)
except Exception as e:
    print( "Could NOT create thread, check .cpp")
    print( "Error type {}".format(type(e))      )
    print( "Error Arguments {}".format(e.args)  )
    sleep( 2.5 )
    quit()                                                                  # Shutdown entire program


# ************************************************************************
# =========================> MAKE IT ALL HAPPEN <=========================
# ************************************************************************

print( "Ready in 3 " ), ; sleep( 1.0 )
print( "... 2 " ),      ; sleep( 1.0 )
print( "... 1 " )       ; sleep( 1.0 )
print( "GO!" )

# Start iteration
while( True ):

    start = time()                                                          # Call clock() for accurate time readings

    # Data acquisition
    (H1, H2, H3, H4) = get_array(q_cpp_output)                              # Get data from .cpp program
    
    # Compute norms
    HNorm = [ float(norm(H1)), float(norm(H2)),                             # Compute norms
              float(norm(H3)), float(norm(H4)) ]                            # ...

    # Solve system of equations
    sol = root(LHS, initialGuess, args=(K, HNorm), method='lm',             # Invoke solver using the
               options={'ftol':1e-10, 'xtol':1e-10, 'maxiter':1000,         # Levenberg-Marquardt 
                        'eps':1e-8, 'factor':0.001})                        # Algorithm (aka LMA)

    # Store solution in array
    position = np.array( (sol.x[0]*1000,                                    # x-axis
                          sol.x[1]*1000,                                    # y-axis
                          sol.x[2]*1000,                                    # z-axis
                          time()-start  ), dtype='float64' )                # time

    # Check value
    if( position[2] < 0 ): position[2] = -1*position[2]                     # Make sure z-value
    else: pass                                                              # ... is ALWAYS +ve

    # Print solution (coordinates) to screen
    if( args["verbose"] ):
        solution_str = "(x, y, z, t): ({:.3f}, {:.3f}, {:.3f}, {:.3f})"     # ...
        print( solution_str.format( position[0], position[1],               # Print solution
                                    position[2], position[3] ) )            # ...

    sleep( 0.1 )                                                            # Sleep for stability

    # Check if solution makes sense
    if (abs(sol.x[0]*1000) > 500) or (abs(sol.x[1]*1000) > 500) or (abs(sol.x[2]*1000) > 500):
        initialGuess = findIG( get_array(q_cpp_output) )                    # Determine initial guess based on magnet's location

    # Update initial guess with current position and feed back to solver
    else:    
        initialGuess = np.array( (sol.x[0]+dx, sol.x[1]+dx,                 # Update the initial guess as the
                                  sol.x[2]+dx), dtype='float64' )           # current position and feed back to LMA
        
        compute_rotation( convert_to_polar( position ) )                    # Compute how many rotations we've done and direction

# ************************************************************************
# =============================> DEPRECATED <=============================
# ************************************************************************
#

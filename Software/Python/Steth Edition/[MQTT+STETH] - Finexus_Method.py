'''
*
* NOTE: REQUIRES A COMPLEMENTARY STETHOSCOPE TO FUNCTION
*
* Position tracking of magnet based on Finexus
* https://ubicomplab.cs.washington.edu/pdfs/finexus.pdf
*
*   - 1 Mode of operation
*       (a) Track position of stethosopce       ( NO PLOTTING )
*       (b) Trigger stethoscope at set regions  ( REQUIRES BT )
*
* VERSION: 1.1
*   - ADDED   : Move things over to MQTT
*
* KNOWN ISSUES:
*   - Non atm
*
* AUTHOR                    :   Edward Nichols
* LAST CONTRIBUTION DATE    :   Jan. 25th, 2017 Year of Our Lord
*
* AUTHOR                    :   Mohammad Odeh
* LAST CONTRIBUTION DATE    :   Jul. 17th, 2018 Year of Our Lord
*
'''

# Tracking + Solver Modules
import  paho.mqtt.client            as      mqtt            # MQTT Communications
import  numpy                       as      np              # Import Numpy
from    time                        import  sleep, clock    # Sleep for stability, clock for profiling
from    time                        import  time            # Time for timing (like duh!)
from    scipy.optimize              import  root            # Solve System of Eqns for (x, y, z)
from    scipy.linalg                import  norm            # Calculate vector norms (magnitude)
from    threading                   import  Thread          # Used to thread processes

try:
    import Queue as queue
except ImportError:
    import queue

from    bluetoothProtocol_teensy32  import  createBTPort, closeBTPort
from    stethoscopeProtocol         import  statusEnquiry   # Status Enquiry
import  os, platform                                        # Directory/file manipulation

# ************************************************************************
# =====================> DEFINE NECESSARY FUNCTIONS <====================*
# ************************************************************************

def on_connect(client, userdata, flags, rc):
    print( "Connected with result code {}".format(rc) )
    client.subscribe( "magfield", qos=1 )

# --------------------------
magField_data = []
def on_message(client, userdata, msg):

    if( msg.topic == "magfield" ):
        inData = msg.payload.decode("utf-8")
        inData = inData.strip("<")
        inData = inData.strip(">")

        # Split line into the constituent components
        col     = (inData.rstrip()).split(",")
        if (len(col) == 12):
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
            magField_data.append( [B1, B2, B3, B4] )
        else:
            print( "DATA CONSTRUCTION IMPROPER" )

    else: pass

# --------------------------

def argsort( seq ):
    '''
    Sort a list's elements from smallest to largest and
    return the sorted INDICES NOT VALUES!

    INPUTS:
        - seq: A list whose elements are to be sorted.

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
    Sort a list's elements from smallest to largest.

    INPUTS:
        - arr: List to be sorted.
        - N  : Number of elements in said list that need to be sorted.
                (i.e list has 5 elements, if N=3, sort the first 3)

    OUTPUT:
        - A sorted list of size N.
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
    return( data )

# --------------------------

def getData():
    '''
    Pool the data from the MCU (wheteher it be a Teensy or an Arduino or whatever)
    The data consists of the magnetic field components in the x-, y-, and z-direction
    of all the sensors. The array must begin with '<' as the SOH signal, the compononents
    must be comma delimited, and must end with '>' as the EOT signal.

            >$\     <B_{1x}, B_{1y}, B_{1z}, ..., B_{1x}, B_{1y}, B_{1z}>

    INPUTS:
        - ser: a serial object. Note that the serial port MUST be open before
               passing it the to function.

    OUTPUT:
        - Individual numpy arrays of all the magnetic field vectors.
    '''
    B1, B2, B3, B4 = magField_data[-1]

    # Return vectors
    return ( B1, B2, B3, B4 )


# --------------------------
x1, y1, z1 =  0.00e-3,  0.00e-3, 0.00e-3
x2, y2, z2 = 42.00e-3, 11.75e-3, 0.00e-3
x3, y3, z3 = 76.00e-3, 43.75e-3, 0.00e-3
x4, y4, z4 = 87.50e-3, 87.40e-3, 0.00e-3
def LHS( root, K, norms ):
    '''
    Construct the left hand side (LHS) of the equations
    to numerically solve for.
    Recall that in order to solve a system numerically it
    must have the form of,
    
                >$\  f(x, y, z, ...) = LHS = 0
    
    INPUTS:
        - root  : a numpy array contating the initial guesses of the roots.
        - K     : K is a property of the magnet and has units of { G^2.m^6 }.
        - norms : An array/list of the vector norms of the magnetic field
                  vectors for all the sensors.

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
    r1 = float( ( (x + x1)**2. + (y + y1)**2. + (z + z1)**2. )**(1/2.) )    # Sensor 1 (ORIGIN)
    r2 = float( ( (x - x2)**2. + (y - y2)**2. + (z + z2)**2. )**(1/2.) )    # Sensor 2
    r3 = float( ( (x - x3)**2. + (y - y3)**2. + (z + z3)**2. )**(1/2.) )    # Sensor 3
    r4 = float( ( (x - x4)**2. + (y - y4)**2. + (z + z4)**2. )**(1/2.) )    # Sensor 4

    # Construct the equations
    Eqn1 = ( K*( r1 )**(-6.) * ( 3.*( z/r1 )**2. + 1 ) ) - norms[0]**2.     # Sensor 1
    Eqn2 = ( K*( r2 )**(-6.) * ( 3.*( z/r2 )**2. + 1 ) ) - norms[1]**2.     # Sensor 2
    Eqn3 = ( K*( r3 )**(-6.) * ( 3.*( z/r3 )**2. + 1 ) ) - norms[2]**2.     # Sensor 3
    Eqn4 = ( K*( r4 )**(-6.) * ( 3.*( z/r4 )**2. + 1 ) ) - norms[3]**2.     # Sensor 4

    # Construct a vector of the equations
    Eqns = [Eqn1, Eqn2, Eqn3, Eqn4]

    # Determine which sensors to use based on magnetic field value (smallValue==noBueno!)
    sort = argsort( norms )                                         # Auxiliary function sorts norms from smallest to largest
    sort.reverse()                                                  # Python built-in function reverses elements of list
    f=[]                                                            # Declare vector to hold relevant functions

    for i in range(0, 3):                                           # Fill functions' array with the equations that correspond to
        f.append( Eqns[sort[i]] )                                   # the sensors with the highest norm, thus closest to magnet
        
    # Return vector
    return ( f )

# --------------------------

def findIG( magFields ):
    '''
    Dynamic search of initial guess for the LMA solver based on magnitude
    of the magnetic field relative to all the sensors.
    A high magnitude reading indicates magnet is close to some 3
    sensors, the centroid of the traingle created by said sensors
    is fed as the initial guess.
    
    INPUTS:
        - magfield: a numpy array containing all the magnetic field readings.

    OUTPUT:
        - A numpy array containing <x, y, z> values for the initial guess.
    '''
    
    # Define IMU positions on the grid
    #      / sensor 1: (x, y, z)
    #     /  sensor 2: (x, y, z)
    # Mat=      :          :
    #     \     :          :
    #      \ sensor 6: (x, y, z)
    IMU_pos = np.array(((x1, y1, z1) ,
                        (x2, y2, z2) ,
                        (x3, y3, z3) ,
                        (x4, y4, z4)), dtype='float64')

    # Read current magnetic field from MCU
    (H1, H2, H3, H4 ) = magFields

    # Compute L2 vector norms
    HNorm = [ float( norm(H1) ), float( norm(H2) ),
              float( norm(H3) ), float( norm(H4) ) ]
    
    # Determine which sensors to use based on magnetic field value (smallValue==noBueno!)
    sort = argsort( HNorm )                                         # Auxiliary function sorts norms from smallest to largest
    sort.reverse()                                                  # Python built-in function reverses elements of list

    IMUS = bubbleSort( sort, 3 )

    # Return the initial guess as the centroid of the detected triangle
    return ( np.array(((IMU_pos[IMUS[0]][0]+IMU_pos[IMUS[1]][0]+IMU_pos[IMUS[2]][0])/3.,
                       (IMU_pos[IMUS[0]][1]+IMU_pos[IMUS[1]][1]+IMU_pos[IMUS[2]][1])/3.,
                       (IMU_pos[IMUS[0]][2]+IMU_pos[IMUS[1]][2]+IMU_pos[IMUS[2]][2])/3. -0.01), dtype='float64') )

# --------------------------

def compute_coordinate():
    '''
    Compute the magnet's position in cartesian space.

    INPUTS:
        - No inputs.

    OUTPUT:
        - position: The most current and updated position
                    of the magnet in cartesian space.
    '''

    global initialGuess                                             # Modify from within function
    start = time()                                                  # Call clock() for accurate time readings

    # Data acquisition
    (H1, H2, H3, H4) = getData()                                    # Get data from MCU

    # Compute norms
    HNorm = [ float(norm(H1)), float(norm(H2)),                     # Compute L2 vector norms
              float(norm(H3)), float(norm(H4)) ]                    #

    # Solve system of equations
    sol = root(LHS, initialGuess, args=(K, HNorm), method='lm',     # Invoke solver using the
               options={'ftol':1e-10, 'xtol':1e-10, 'maxiter':1000, # Levenberg-Marquardt
                        'eps':1e-8, 'factor':0.001})                # Algorithm (aka LMA)

    # Store solution in array
    position = np.array( (sol.x[0]*1000,                            # x-axis
                          sol.x[1]*1000,                            # y-axis
                          sol.x[2]*1000,                            # z-axis
                          time()-start  ), dtype='float64' )        # time

    # Check value
    if( position[2] < 0 ): position[2] = -1*position[2]             # Make sure z-value
    else: pass                                                      # ... is ALWAYS +ve

    # Print solution (coordinates) to screen
    print( "(x, y, z, t): (%.3f, %.3f, %.3f, %.3f)" %( position[0],
                                                       position[1],
                                                       position[2],
                                                       position[3] ) )

    # Check if solution makes sense
    if (abs(sol.x[0]*1000) > 500) or (abs(sol.x[1]*1000) > 500) or (abs(sol.x[2]*1000) > 500):
        initialGuess = findIG( getData() )                          # Determine initial guess based on magnet's location
        return( compute_coordinate() )                              # Recursive call of function()

    # Update initial guess with current position and feed back to solver
    else:
        initialGuess = np.array( (sol.x[0]+dx, sol.x[1]+dx,         # Update the initial guess as the
                                  sol.x[2]+dx), dtype='float64' )   # current position and feed back to LMA
        trigSteth( position )
        return( position )                                          # Return position

# --------------------------

def storeData( data ):
    '''
    Store computed position co-ordinates into a .txt file

    INPUTS:
        - data: A list containing all the computed co-ordinate points
    '''

    print( "Storing data log under data.txt ..." ) ,

    # Unzip data into x, y, z
    x, y, z, t = data[0], data[1], data[2], data[3]

    # Setup paths!
    if platform.system()=='Windows':

        # Define useful paths
        homeDir = os.getcwd()
        dst     = homeDir + '\\output'
        dataFile= dst + '\\data.txt'

    elif platform.system()=='Linux':

        # Define useful paths
        homeDir = os.getcwd()
        dst = homeDir + '/output'
        dataFile= dst + '/data.txt'

    # Check if directory exists
    if ( os.path.exists(dst)==False ):
        # Create said directory
        os.makedirs(dst)

    # Write into file
    with open( dataFile, "a" ) as f:
        for i in range( 0, len(x) ):
                f.write(str(x[i]) + "," + str(y[i]) + "," + str(z[i]) + "," + str(t[i]) + "\n")

    print( "SUCCESS!" )

# --------------------------

def trigSteth( pos ):
    global stethON, lastROI
    x, y, z, _ = pos                                        # Unpack position

    # __START__: Get ROI
    # Region 1
    if(
        (100<=x  and x<=150) and
        ( 75<=y  and y<=125) and
        (z<100)
        ):
        crntROI = 1

    # Region 2
    elif( ( 50<=x and x<=100) and
          (-50<=y and y<=  0) and
          ( z<120 )
        ):
        crntROI = 2

    # Region 3
    elif(
          (125<=x and x<=175) and
          ( 25<=y and y<= 75) and
          ( z<120 )
        ):
        crntROI = 3
        
    # Region 4
    elif(
          (- 25<=x and x<= 25) and
          (-100<=y and y<=-50) and
          ( z<120 )
        ):
        crntROI = 4

    else: crntROI = 0
    # __END__: Get ROI

    # __START__: Send byte
    if( crntROI != lastROI ):                               # Check if we need to send a byte

        if( crntROI == 0):
            print( "NOT INSIDE ANY REGION" )
            sleep( 1.0 )
##            statusEnquiry( steth )
            
        elif( crntROI == 1):
            print( "We are in region #1" )
            sleep( 1.0 )
##            statusEnquiry( steth )

        elif( crntROI == 2):
            print( "We are in region #2" )
            sleep( 1.0 )
##            statusEnquiry( steth )

        elif( crntROI == 3):
            print( "We are in region #3" )
            sleep( 1.0 )
##            statusEnquiry( steth )

        elif( crntROI == 4):
            print( "We are in region #4" )
            sleep( 1.0 )
##            statusEnquiry( steth )


    else: pass
    # __END__: Send byte

    lastROI = crntROI                                       # Update lastROI with the current one

    return                                                  # Exit function
# --------------------------

# ************************************************************************
# ===========================> SETUP PROGRAM <===========================
# ************************************************************************

# Useful variables
global CALIBRATING
global initialGuess

CALIBRATING = True                                          # Boolean to indicate that device is calibrating

K           = 1.09e-6                                       # Big magnet's constant             (K) || Units { G^2.m^6}
##K           = 5.55e-6                                       # Cylindrical magnet's constant     (K) || Units { G^2.m^6}
##K           = 2.46e-7                                       # Spherical magnet's constant       (K) || Units { G^2.m^6}
##K           = 1.87e-7                                       # Small magnet's constant (w\hole)  (K) || Units { G^2.m^6}
##K           = 1.29e-7                                       # Small magnet's constant  (flat)   (K) || Units { G^2.m^6}
##K           = 1.29e-7                                       # Michael's magnet's constant       (K) || Units { G^2.m^6}
dx          = 1e-7                                          # Differential step size (Needed for solver)
calcPos     = []                                            # Empty array to hold calculated positions


# Error handling in case MQTT communcation setup fails (1/2)
try:
    # Setup MQTT
    addr = "192.168.42.1"
    client = mqtt.Client()
    client.max_inflight_messages_set( 60 )                  # Max number of messages that can be part of network flow at once
    client.max_queued_messages_set( 0 )                     # Size 0 == unlimited
    client.will_set( "general", "CONENCTION LOST",          # "Last Will" message. Sent when connection is
                     qos=1, retain=True )                   # ...lost (aka, disconnect was not called)
    client.reconnect_delay_set( min_delay=1, max_delay=2)   # Min/max wait time in case of reconnection

    client.on_connect = on_connect                          # Assign callback functions
    client.on_message = on_message                          # ...
    
    client.connect( addr, port=1883, keepalive=60 )         # Connect to MQTT network
    client.loop_start()                                     # Start loop
    sleep( 1.0 )                                            # Allow some time for data to be published

    initialGuess = findIG( getData() )                      # Determine initial guess based on magnet's location

# Error handling in case MQTT communcation setup fails (2/2)
except Exception as e:
    print( "Could NOT setup MQTT communications" )
    print( "Error Type      : {}".format(type(e)))
    print( "Error Arguments : {}".format(e.args) )
    sleep( 1.5 )
    quit()                                                  # Shutdown entire program

# Establish communication with stethoscope
addr = "00:06:66:D0:C9:60"
port = 1

# Error handling in case BTooth communcation fails (1/2)
try:
    steth = createBTPort( addr, port )

    if( steth != 0 ):
        statusEnquiry( steth )
        print( "Connection established" )
    else:
        raise Exception

# Error handling in case BTooth communcation fails (2/2)
except Exception as e:
    print( "Could NOT communicate with stethoscope" )
    print( "Error Type      : {}".format(type(e)))
    print( "Error Arguments : {}".format(e.args) )
    sleep( 1.5 )
    quit()                                                  # Shutdown entire program

lastROI = 0                                                 # Start an empty variable for the last recorded IMU

# ************************************************************************
# =========================> MAKE IT ALL HAPPEN <=========================
# ************************************************************************

x, y = np.array([]), np.array([])                           # Initialize empty numpy arrays
z, t = np.array([]), np.array([])                           # for x, y, z, and t

print( "System Ready." )                                    # Inform user to place magnet
sleep( 0.5 )                                                # Allow user time to react

while( True ):                                              # Loop until we get a valid user input
    var = raw_input( "Start? (Y/N): " )                     #   Prompt user if ready or nah!
    if  ( var=='Y' or var=='y' ): break                     #   ...
    elif( var=='N' or var=='n' ): pass                      #   ...
    else: print( "Invalid Choice" )                         #   ...
        
print( "\n******************************************" )
print( "*NOTE: Press Ctrl-C to save data and exit."   )
print( "******************************************\n" )
sleep( 1.0 )                                                # Allow user to read note

while( True ):                                              # Loop 43va
    try:
        pos = compute_coordinate()                          # Get updated magnet position

        x = np.append( x, pos[0] )                          # Append computed values
        y = np.append( y, pos[1] )                          # of x, y, z, and t
        z = np.append( z, pos[2] )                          # to their respective
        t = np.append( t, pos[3] )                          # arrays.


    except KeyboardInterrupt:
        print( '' )                                         # Start with a newline for aesthetics
##        storeData( (x, y, z, t) )                           # Store data points in text file
        break                                               # Break from loop!

# --------------------------------------------------------------------------------------

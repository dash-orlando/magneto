'''
*
* Position tracking of magnet based on Finexus ported to Raspberry Pi
* https://ubicomplab.cs.washington.edu/pdfs/finexus.pdf
*
* VERSION: 0.1.5
*   - ADDED   : Two addresses can be used.
*   - ADDED   : Multithreading.
*
* KNOWN ISSUES:
*   - Calculated position is not correct, NOT because
*     code doesn't work, but because I didn't input the
*     correct coordinates.
*
* AUTHOR                    :   Nicolas Maduro (aka Danny)
* LAST CONTRIBUTION DATE    :   Oct. 16th, 2017 Year of Our Lord
* 
* AUTHOR                    :   Mohammad Odeh 
* LAST CONTRIBUTION DATE    :   Nov. 11th, 2017 Year of Our Lord
*
'''

# Import Modules
import  numpy               as      np              # Import Numpy
import  RPi.GPIO            as      GPIO            # Use GPIO pins
from    time                import  sleep, time     # Sleep for stability / time execution
from    scipy.optimize      import  root            # Solve System of Eqns for (x, y, z)
from    scipy.linalg        import  norm            # Calculate vector norms (magnitude)
from    Queue               import  LifoQueue       # Last in First out queue
from    threading           import  Thread          # Multithread data
from    ctypes              import  *               # Import ctypes (VERY IMPORTANT)


# ************************************************************************
# =====================> DEFINE NECESSARY FUNCTIONS <====================*
# ************************************************************************

def loadLib():
    '''
    Load IMU library and prime with ctypes
    '''
    
    global imu
    path = "/home/pi/LSM9DS1_RaspberryPi_Library/lib/liblsm9ds1cwrapper.so"
    imu = cdll.LoadLibrary(path)

    imu.create.argtypes = [c_uint]
    imu.create.restype = c_void_p

    imu.begin.argtypes = [c_void_p]
    imu.begin.restype = None

    imu.calibrate.argtypes = [c_void_p]
    imu.calibrate.restype = None

    imu.magAvailable.argtypes = [c_void_p]
    imu.magAvailable.restype = c_int

    imu.readMag.argtypes = [c_void_p]
    imu.readMag.restype = c_int

    imu.getMagX.argtypes = [c_void_p]
    imu.getMagX.restype = c_float
    imu.getMagY.argtypes = [c_void_p]
    imu.getMagY.restype = c_float
    imu.getMagZ.argtypes = [c_void_p]
    imu.getMagZ.restype = c_float

    imu.calcMag.argtypes = [c_void_p, c_float]
    imu.calcMag.restype = c_float

# ------------------------------------------------------------------------

def setupMux():
    '''
    Setup multiplexer
    '''
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(23, GPIO.OUT)
    GPIO.setup(24, GPIO.OUT)
    GPIO.setup(25, GPIO.OUT)

# ------------------------------------------------------------------------

def setSensor( sensorIndex ):
    '''
    Switch between all the sensors

    INPUTS:
        - sensorIndex: index of the sensor pair

    OUTPUT:
        - NON
    '''
    
    # Sensor 1, 000
    if ( sensorIndex == 0 ):
        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)

    # Sensor 2, 001
    elif ( sensorIndex == 1 ):
        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)

    # Sensor 3, 010
    elif ( sensorIndex == 2 ):
        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.HIGH)
        GPIO.output(25, GPIO.LOW)

    # Sensor 4, 011
    elif ( sensorIndex == 3):
        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.HIGH)
        GPIO.output(25, GPIO.LOW)

    # Sensor 5, 100
    elif ( sensorIndex == 4):
        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)

    # Sensor 6, 101
    elif (sensorIndex == 5):
        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)

    else:
        print("Invalid Index")

# ------------------------------------------------------------------------

def setupIMU( N ):
    '''
    Setup IMUs (set scale, calibrate, etc...)

    INPUTS:
        - N: Number of sensors

    OUTPUT:
        - No output; sensor setup is global.
    '''
    
    global IMU_Base
    global IMU

    agAddrHigh, mAddrHigh = 0x6b, 0x1e                  # I2C addresses for Hi sensors
    agAddrLow, mAddrLow = 0x6b, 0x1c                    # I2C addresses for Lo sensors
    
    IMU_Base = np.empty((N,3), dtype='float64')         # Construct matrix of size  (Nx3)
    CALIBRATION_INDEX = 50                              # Average over this many readings
    
    IMU = [ imu.create(agAddrHigh, mAddrHigh),          # Create a list of all sensors. Note that ...
            imu.create(agAddrLow , mAddrLow ),          # ... each sensor pair consists of a Hi ...
            imu.create(agAddrHigh, mAddrHigh),          # ... & Lo sensor s.t their indices are:-
            imu.create(agAddrLow , mAddrLow ) ]         # Hi: [2*i] (EVENS) || Lo: [2*i+1] (ODDS)
    
    # Loop over all sensors
    for i in range( 0, (N/2) ):
        
        print( "Setting up sensor pair %i" %(i+1) )
        setSensor( i )

        if ( imu.begin(IMU[2*i]) or imu.begin(IMU[2*i+1]) )== 0:         # In case it fails
            print("Failed to communicate with LSM9DS1.")
            quit()

        else:
            imu.setMagScale( IMU[2 * i], 16 )           # Set scale to +/-16Gauss
            imu.setMagScale( IMU[2*i+1], 16 )           # Set scale to +/-16Gauss
            imu.calibrateMag( IMU[2 * i] )              # Call built-in calibration routine
            imu.calibrateMag( IMU[2*i+1] )              # Call built-in calibration routine

            cmxHi, cmyHi, cmzHi = 0, 0, 0               # Temporary calibration ...
            cmxLo, cmyLo, cmzLo = 0, 0, 0               # ... variables for Hi & Lo

            # Perform user-built calibration to further clear noise
            print( "Performing user-built calibration" )
            for j in range(0, CALIBRATION_INDEX):
                imu.readMag( IMU[2 * i] )
                imu.readMag( IMU[2*i+1] )

                cmxHi += imu.calcMag( IMU[2 * i], imu.getMagX(IMU[2 * i]) )
                cmyHi += imu.calcMag( IMU[2 * i], imu.getMagY(IMU[2 * i]) )
                cmzHi += imu.calcMag( IMU[2 * i], imu.getMagZ(IMU[2 * i]) )
                
                cmxLo += imu.calcMag( IMU[2*i+1], imu.getMagX(IMU[2*i+1]) )
                cmyLo += imu.calcMag( IMU[2*i+1], imu.getMagY(IMU[2*i+1]) )
                cmzLo += imu.calcMag( IMU[2*i+1], imu.getMagZ(IMU[2*i+1]) )

            # Average all the readings
            IMU_Base[2 * i][0] = cmxHi/CALIBRATION_INDEX
            IMU_Base[2 * i][1] = cmyHi/CALIBRATION_INDEX
            IMU_Base[2 * i][2] = cmzHi/CALIBRATION_INDEX

            IMU_Base[2*i+1][0] = cmxLo/CALIBRATION_INDEX
            IMU_Base[2*i+1][1] = cmyLo/CALIBRATION_INDEX
            IMU_Base[2*i+1][2] = cmzLo/CALIBRATION_INDEX
            
            print( "Correction constant for Hi sensor %i is:" %(i+1) )
            print( "x: %.5f, y: %.5f, z: %.5f\n" %(IMU_Base[2 * i][0], IMU_Base[2 * i][1], IMU_Base[2 * i][2]) )

            print( "Correction constant for Lo sensor %i is:" %(i+1) )
            print( "x: %.5f, y: %.5f, z: %.5f\n" %(IMU_Base[2*i+1][0], IMU_Base[2*i+1][1], IMU_Base[2*i+1][2]) )

# ------------------------------------------------------------------------        

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

# ------------------------------------------------------------------------

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

# ------------------------------------------------------------------------

def calcMag( N, Q ):
    '''
    Collect readings from IMU.
    INPUTS:
        - N: Number of sensors
        - Q: Queue used to pipe this thread to main program

    OUTPUT:
        - Places CALIBRATED magnetic field in queue
    '''

    B = np.zeros( (N,3), dtype='float64' )                              # Construct matrix of size  (Nx3)
    while( True ):
        for i in range(0, (N/2)):
            setSensor( i )                                                  # Select sensor pair (i)

            imu.readMag( IMU[2 * i] )                                       # Read magnetic field for Hi
            imu.readMag( IMU[2*i+1] )                                       # Read magnetic field for Lo
            
            mxHi = imu.calcMag( IMU[2 * i], imu.getMagX(IMU[2 * i]) )       # ...
            myHi = imu.calcMag( IMU[2 * i], imu.getMagY(IMU[2 * i]) )       # Calculate magnetic field for Hi
            mzHi = imu.calcMag( IMU[2 * i], imu.getMagZ(IMU[2 * i]) )       # ...

            mxLo = imu.calcMag( IMU[2*i+1], imu.getMagX(IMU[2*i+1]) )       # ...
            myLo = imu.calcMag( IMU[2*i+1], imu.getMagY(IMU[2*i+1]) )       # Calculate magnetic field for Lo
            mzLo = imu.calcMag( IMU[2*i+1], imu.getMagZ(IMU[2*i+1]) )       # ...

            B[2 * i] = np.array( (mxHi, myHi, mzHi), dtype='float64' )      # Units { G }
            B[2*i+1] = np.array( (mxLo, myLo, mzLo), dtype='float64' )      # Units { G }

    ##    print( B )                                                          # Print RAW data (for debugging)
    ##    return( B - IMU_Base )                                              # Return array
        Q.put_nowait( B - IMU_Base ) 

# ------------------------------------------------------------------------

def findIG( Q ):
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
    IMU_pos = np.array((( 0.000, 0.000, 0.000) ,
                        ( 0.000,-0.039, 0.000) ,
                        (-0.063, 0.000, 0.000) ,
                        (-0.063,-0.039, 0.000)), dtype='float64')

    # Read current magnetic field from MCU
    (H1, H2, H3, H4) = Q

    # Compute L2 vector norms
    HNorm = [ float( norm(H1) ), float( norm(H2) ),
              float( norm(H3) ), float( norm(H4) ) ]
    
    # Determine which sensors to use based on magnetic field value (smallValue==noBueno!)
    sort = argsort( HNorm )             # Auxiliary function sorts norms from smallest to largest
    sort.reverse()                      # Python built-in function reverses elements of list

    IMUS = bubbleSort( sort, 3 )

    # Return the initial guess as the centroid of the detected triangle
    return ( np.array(((IMU_pos[IMUS[0]][0]+IMU_pos[IMUS[1]][0]+IMU_pos[IMUS[2]][0])/3.,
                       (IMU_pos[IMUS[0]][1]+IMU_pos[IMUS[1]][1]+IMU_pos[IMUS[2]][1])/3.,
                       (IMU_pos[IMUS[0]][2]+IMU_pos[IMUS[1]][2]+IMU_pos[IMUS[2]][2])/3. -0.01), dtype='float64') )

# ------------------------------------------------------------------------

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
    r2 = float( ( (x+0.000)**2. + (y+0.039)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 2
    r3 = float( ( (x+0.063)**2. + (y+0.000)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 3
    r4 = float( ( (x+0.063)**2. + (y+0.039)**2. + (z+0.00)**2. )**(1/2.) )  # Sensor 4

    # Construct the equations
    Eqn1 = ( K*( r1 )**(-6.) * ( 3.*( z/r1 )**2. + 1 ) ) - norms[0]**2.     # Sensor 1
    Eqn2 = ( K*( r2 )**(-6.) * ( 3.*( z/r2 )**2. + 1 ) ) - norms[1]**2.     # Sensor 2
    Eqn3 = ( K*( r3 )**(-6.) * ( 3.*( z/r3 )**2. + 1 ) ) - norms[2]**2.     # Sensor 3
    Eqn4 = ( K*( r4 )**(-6.) * ( 3.*( z/r4 )**2. + 1 ) ) - norms[3]**2.     # Sensor 4

    # Construct a vector of the equations
    Eqns = [Eqn1, Eqn2, Eqn3, Eqn4]

    # Determine which sensors to use based on magnetic field value (smallValue==noBueno!)
    sort = argsort( norms )             # Auxiliary function sorts norms from smallest to largest
    sort.reverse()                      # Python built-in function reverses elements of list
    f=[]                                # Declare vector to hold relevant functions

    for i in range(0, 3):               # Fill functions' array with the equations that correspond to
        f.append( Eqns[sort[i]] )       # the sensors with the highest norm, thus closest to magnet
        
    # Return vector
    return ( f )

# ************************************************************************
# ===========================> SETUP PROGRAM <===========================
# ************************************************************************

# Useful variables
K           = 1.09e-6                               # Magnet's constant (K) || Units { G^2.m^6}
dx          = 1e-7                                  # Differential step size (Needed for solver)
NSENS       = 4                                     # Number of sensors used
H           = np.empty((NSENS,3), dtype='float64')  # Construct matrix of size  (Nx3)

# Start sensors
loadLib()                                           # Load LSM9DS1 Library
setupMux()                                          # Setup the RPi to use the multiplexer
setupIMU( NSENS )                                   # Setup IMUs (set scale, calibrate, etc...)

Q_calcMag = LifoQueue( maxsize=0 )                  # LIFO queue qith infinite size

# Start pooling data from serial port
t_calcMag = Thread( target=calcMag,                 # Create thread to read ...
                    args=(NSENS, Q_calcMag,) )      # ... data from sensors
t_calcMag.daemon = True
t_calcMag.start()                                   # Start thread

# ************************************************************************
# =========================> MAKE IT ALL HAPPEN <=========================
# ************************************************************************

print( "Place magnet on grid" )
print( "Ready in 3" )
sleep( 1.0 )
print( "Ready in 2" )
sleep( 1.0 )
print( "Ready in 1" )
sleep( 1.0 )
print( "GO!" )

initialGuess = findIG( Q_calcMag.get() )                            # Determine initial guess based on magnet's location

# Start iteration
while( True ):

    startTime = time()                                              # Start time
    
    # Data acquisition
    H = Q_calcMag.get_nowait()                                      # Pool data from thread
    
    # Compute norms
    HNorm = [ float(norm(H1)), float(norm(H2)),                     # Compute L2 vector norms
              float(norm(H3)), float(norm(H4)) ]                    # ...

    # Solve system of equations
    sol = root(LHS, initialGuess, args=(K, HNorm), method='lm',     # Invoke solver using the
               options={'ftol':1e-10, 'xtol':1e-10, 'maxiter':1000, # Levenberg-Marquardt 
                        'eps':1e-8, 'factor':0.001})                # Algorithm (aka LMA)

    # Print solution (coordinates) to screen
    print( "Current position (x , y , z):" )
    print( "(%.5f , %.5f , %.5f)mm" %(sol.x[0]*1000, sol.x[1]*1000, -1*sol.x[2]*1000) )

    # Check if solution makes sense
    if (abs(sol.x[0]*1000) > 500) or (abs(sol.x[1]*1000) > 500) or (abs(sol.x[2]*1000) > 500):
        initialGuess = findIG( Q_calcMag.get() )                    # Determine initial guess based on magnet's location
        
    # Update initial guess with current position and feed back to solver
    else:    
        initialGuess = np.array( (sol.x[0]+dx, sol.x[1]+dx,         # Update the initial guess as the
                                  sol.x[2]+dx), dtype='float64' )   # current position and feed back to LMA

    print( "t = %.5f" %(time()-startTime) )                         # End time
    sleep( 0.5 )                                                    # Sleep for stability
    

# ************************************************************************
# =============================> DEPRECATED <=============================
# ************************************************************************
#

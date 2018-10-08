'''
*
* Position tracking of magnet based on Finexus ported to Raspberry Pi
* https://ubicomplab.cs.washington.edu/pdfs/finexus.pdf
*
* VERSION: 0.1.1
*   - MODIFIED: Initial Release
*   - MODIFIED: Code is less horrible but still ugly af
*   - MODIFIED: Restructured code in order to streamline and
*               later on multithread code execution
*
* KNOWN ISSUES:
*   - Damn z-axis refuses to work!
*
* Author        :   Nicolas Maduro (aka Danny) 
* Last Modified :   Oct. 16th, 2017 Year of Our Lord
*
* Author        :   Mohammad Odeh 
* Last Modified :   Oct. 19th, 2017 Year of Our Lord
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
    Load library and prime with ctypes
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
        sleep( 0.1 )

    # Sensor 2, 001
    elif ( sensorIndex == 1 ):
        GPIO.output(23, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)
        sleep( 0.1 )

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

def calcMag( N ):
    '''
    Collect readings from IMU.
    INPUTS:
        - N: Number of sensors

    OUTPUT:
        - CALIBRATED magnetic field
    '''

    B = np.zeros( (N,3), dtype='float64' )                              # Construct matrix of size  (Nx3)

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

    return(B - IMU_Base)                                                # Return array


# ************************************************************************
# ===========================> SETUP PROGRAM <===========================
# ************************************************************************

# Useful variables
K           = 1.09e-6                               # Magnet's constant (K) || Units { G^2.m^6}
dx          = 1e-7                                  # Differential step size (Needed for solver)
NSENS       = 4                                     # Number of sensors used
H           = np.empty((NSENS,3), dtype='float64')  # Construct matrix of size  (NSENSx3)

# Start sensors
loadLib()                                           # Load LSM9DS1 Library
setupMux()                                          # Setup the RPi to use the multiplexer
setupIMU( NSENS )                                   # Setup IMUs (set scale, calibrate, etc...)


# ************************************************************************
# =========================> MAKE IT ALL HAPPEN <=========================
# ************************************************************************

print( "Ready in 2" )
sleep( 1.0 )
print( "Ready in 1" )
sleep( 1.0 )
print( "GO!" )



# Start iteration
while( True ):

    startTime = time()
    # Get magnetic field readings
    H = calcMag( NSENS )
    

    print ( "Sensor 1' (UpRight) : < %8.5f , %8.5f , %8.5f >" %(H[0][0], H[0][1], H[0][2]) )
    print ( "Sensor 1 (DownRight): < %8.5f , %8.5f , %8.5f >" %(H[1][0], H[1][1], H[1][2]) )
    print ( "Sensor 2' (UpLeft)  : < %8.5f , %8.5f , %8.5f >" %(H[2][0], H[2][1], H[2][2]) )
    print ( "Sensor 2 (DownLeft) : < %8.5f , %8.5f , %8.5f >" %(H[3][0], H[3][1], H[3][2]) )

    print( "t = %.5f" %(time()-startTime) )
    sleep( 0.25 )
    

# ************************************************************************
# =============================> DEPRECATED <=============================
# ************************************************************************
#
